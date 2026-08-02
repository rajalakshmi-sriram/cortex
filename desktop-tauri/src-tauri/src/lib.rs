//! Cortex desktop shell (Tauri).
//!
//! Uses the OS's native WebView instead of bundling Chromium, which is the
//! whole reason this exists instead of the earlier Electron build: Electron
//! has a hard floor of 4+ separate Chromium processes (main, GPU, network,
//! renderer) that commonly totals 300-500MB+ idle, regardless of what the
//! app itself does. Tauri's shell process is a few MB.
//!
//! The Flask backend (built by PyInstaller from ../../run_desktop.py, see
//! ../../cortex_backend.spec) is bundled as a resource folder (not a Tauri
//! "sidecar", since PyInstaller produces a directory of files rather than a
//! single binary) and spawned as a plain child process. Boot resiliency
//! mirrors the earlier Electron implementation:
//!   - tauri-plugin-single-instance: a second launch focuses the existing
//!     window instead of spawning a competing backend.
//!   - A fresh, dynamically-picked port every launch, so a leftover process
//!     from a previous crash can never block a new one from starting.
//!   - The backend's own parent-PID watchdog (see run_desktop.py) means it
//!     exits itself if this process ever disappears without a clean
//!     shutdown, so nothing is left running between launches.
//!   - If the backend doesn't come up, the window shows a real error screen
//!     with a Retry button instead of staying blank.

use base64::Engine;
use std::net::TcpListener;
use std::path::PathBuf;
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::{Duration, Instant};
use tauri::{AppHandle, Manager, State, WebviewUrl, WebviewWindowBuilder};

struct BackendState {
    child: Mutex<Option<Child>>,
    // Resolved once on the main thread during setup() and reused from
    // there on - path-resolving Cocoa/bundle APIs on macOS can behave
    // oddly when called from a background thread, so this is computed
    // eagerly rather than re-derived inside the boot thread each time.
    binary_path: PathBuf,
}

fn find_free_port() -> u16 {
    TcpListener::bind("127.0.0.1:0")
        .and_then(|l| l.local_addr())
        .map(|addr| addr.port())
        .unwrap_or(5050)
}

fn resolve_backend_binary_path(app: &AppHandle) -> PathBuf {
    let exe_name = if cfg!(windows) { "cortex-backend.exe" } else { "cortex-backend" };
    if cfg!(debug_assertions) {
        // Dev fallback: the PyInstaller build already produced at the repo
        // root (`pyinstaller cortex_backend.spec` run from the project root).
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../dist/cortex-backend")
            .join(exe_name)
    } else {
        app.path()
            .resource_dir()
            .expect("resource_dir should exist in a bundled app")
            .join("cortex-backend")
            .join(exe_name)
    }
}

fn kill_backend(state: &BackendState) {
    if let Some(mut child) = state.child.lock().unwrap().take() {
        let _ = child.kill();
        let _ = child.wait();
    }
}

/// Spawns the backend, replacing any previous instance. Returns the port
/// it's listening on.
fn spawn_backend(state: &BackendState) -> Result<u16, String> {
    kill_backend(state);

    let port = find_free_port();

    let child = Command::new(&state.binary_path)
        .env("PORT", port.to_string())
        .env("CORTEX_PARENT_PID", std::process::id().to_string())
        .spawn()
        .map_err(|e| format!("Couldn't start the backend at {}: {}", state.binary_path.display(), e))?;

    *state.child.lock().unwrap() = Some(child);
    Ok(port)
}

fn wait_for_backend(port: u16, timeout: Duration) -> bool {
    let deadline = Instant::now() + timeout;
    let url = format!("http://127.0.0.1:{port}/health");
    while Instant::now() < deadline {
        if let Ok(resp) = ureq::get(&url).timeout(Duration::from_secs(2)).call() {
            if resp.status() == 200 {
                return true;
            }
        }
        std::thread::sleep(Duration::from_millis(300));
    }
    false
}

fn data_url_html(html: &str) -> tauri::Url {
    let encoded = base64::engine::general_purpose::STANDARD.encode(html);
    tauri::Url::parse(&format!("data:text/html;base64,{encoded}")).unwrap()
}

fn loading_html() -> String {
    r#"<html><body style="margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:#faf6ee;font-family:-apple-system,system-ui,sans-serif;color:#5a5346;">
<div style="text-align:center;">
<div style="font-size:20px;font-weight:700;margin-bottom:8px;">Starting Cortex&hellip;</div>
<div style="font-size:13px;opacity:0.7;">This only takes a moment.</div>
</div></body></html>"#
        .to_string()
}

fn error_html(message: &str) -> String {
    let safe = message.replace('&', "&amp;").replace('<', "&lt;").replace('>', "&gt;");
    format!(
        r#"<html><body style="margin:0;height:100vh;display:flex;align-items:center;justify-content:center;
background:#faf6ee;font-family:-apple-system,system-ui,sans-serif;color:#5a5346;">
<div style="text-align:center;max-width:420px;padding:24px;">
<div style="font-size:20px;font-weight:700;margin-bottom:10px;">Cortex couldn't start</div>
<div style="font-size:13px;opacity:0.8;margin-bottom:18px;">{safe}</div>
<button onclick="window.__TAURI__.core.invoke('retry_backend')"
style="background:#6f93b3;color:white;border:none;border-radius:8px;padding:10px 20px;
font-size:13px;font-weight:700;cursor:pointer;">Retry</button>
</div></body></html>"#
    )
}

fn close_main_window(app: &AppHandle) {
    if let Some(w) = app.get_webview_window("main") {
        let _ = w.close();
    }
}

fn show_window(app: &AppHandle, url: WebviewUrl, init_script: Option<String>) {
    close_main_window(app);
    let mut builder = WebviewWindowBuilder::new(app, "main", url)
        .title("Cortex")
        .inner_size(1440.0, 900.0)
        .min_inner_size(960.0, 640.0)
        .background_color(tauri::window::Color(0xfa, 0xf6, 0xee, 0xff));
    if let Some(script) = init_script {
        builder = builder.initialization_script(&script);
    }
    let _ = builder.build();
}

fn boot(app: &AppHandle) {
    show_window(app, WebviewUrl::External(data_url_html(&loading_html())), None);

    let state: State<BackendState> = app.state();
    match spawn_backend(&state) {
        Ok(port) => {
            if wait_for_backend(port, Duration::from_secs(15)) {
                let init = format!("window.__CORTEX_API_BASE__ = 'http://127.0.0.1:{port}';");
                show_window(app, WebviewUrl::App("index.html".into()), Some(init));
            } else {
                show_window(
                    app,
                    WebviewUrl::External(data_url_html(&error_html(
                        "The backend didn't respond in time. Your Mac's security software, \
                         a strict firewall, or a port conflict could be the cause.",
                    ))),
                    None,
                );
            }
        }
        Err(e) => {
            show_window(app, WebviewUrl::External(data_url_html(&error_html(&e))), None);
        }
    }
}

#[tauri::command]
fn retry_backend(app: AppHandle) {
    std::thread::spawn(move || boot(&app));
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.unminimize();
                let _ = w.set_focus();
            }
        }))
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![retry_backend])
        .setup(|app| {
            // Resolved here, on the main thread, before anything else touches
            // it - see the comment on BackendState::binary_path.
            let binary_path = resolve_backend_binary_path(&app.handle());
            app.manage(BackendState {
                child: Mutex::new(None),
                binary_path,
            });

            let handle = app.handle().clone();
            std::thread::spawn(move || boot(&handle));
            Ok(())
        })
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app_handle, event| {
            if let tauri::RunEvent::ExitRequested { .. } = event {
                let state: State<BackendState> = app_handle.state();
                kill_backend(&state);
            }
        });
}
