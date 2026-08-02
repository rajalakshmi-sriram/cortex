# Building Cortex as a desktop app (Tauri)

This is the current, supported way to package Cortex as a double-clickable
desktop app for Mac and Windows. It wraps the same Flask backend + React
frontend used in normal development - nothing about the app's features
changes, it's just packaged so a user doesn't need Python or Node installed.

(An earlier pass used Electron for this - `electron/` has been removed.
Electron bundles a full Chromium browser, which has a hard floor of 4+
separate processes (main, GPU, network, renderer) and commonly totals
300-500MB+ of idle memory, regardless of what the app itself does. Tauri
uses the OS's own native WebView (WKWebView on macOS, WebView2 on Windows)
instead, so there's no bundled browser engine - idle memory for the whole
app is roughly 130MB versus Electron's ~525MB, measured on this machine.
The older `BUILD_MACOS_APP.md` / `build_macos_app.sh` / `macos-app/` /
`setup.py` files in this repo are from an even earlier PyQt6-only desktop
GUI that predates the web frontend entirely - unrelated to either build.)

## How it fits together

- `run_desktop.py` - production entrypoint for the Flask backend (binds to
  127.0.0.1 only, no dev reloader, and exits itself if its parent process
  disappears without a clean shutdown - see the "boot resiliency" comment
  at the top of that file).
- `cortex_backend.spec` - PyInstaller spec that bundles the backend and all
  its Python dependencies into a standalone binary, so end users don't need
  Python installed. Heavy scientific libraries (numpy/pandas/scipy/
  matplotlib/scikit-learn) are lazy-imported by the modules that use them
  (`app/stats_engine.py`, `app/chart_engine.py`, `app/nlp_engine.py`,
  `app/data_import.py`) rather than loaded at startup, so an idle session
  that never opens Data & Analysis or runs a literature search doesn't pay
  for them.
- `web/dist/` - the production React build (`npm run build` inside `web/`).
- `desktop-tauri/` - the Tauri wrapper:
  - `src-tauri/src/lib.rs` - spawns the bundled backend as a plain child
    process on a freshly-picked port every launch, waits for it to report
    healthy, then opens a window pointed at the bundled frontend with that
    port injected as `window.__CORTEX_API_BASE__` (see the matching change
    in `web/src/api/client.js`). Handles boot resiliency: single-instance
    lock, dynamic ports, and a real "couldn't start" retry screen if the
    backend fails to come up.
  - `src-tauri/tauri.conf.json` - points `frontendDist` at `../../web/dist`
    and bundles the whole `../../dist/cortex-backend` folder as a resource.
- Saved projects live in a normal per-user app-data folder, not inside the
  app bundle itself (`~/Library/Application Support/Cortex` on macOS,
  `%APPDATA%\Cortex` on Windows) - see `_user_data_dir()` in
  `config/config.py`.

## Building on macOS (what was just done)

```bash
# 0. One-time: install Rust if you don't already have it
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 1. Build the backend into a standalone binary
python3 -m venv venv-run  # if you don't already have one
venv-run/bin/pip install -r requirements.txt pyinstaller
venv-run/bin/pyinstaller cortex_backend.spec --noconfirm

# 2. Build the frontend
cd web && npm install && npm run build && cd ..

# 3. Install the Tauri CLI and build the installer
cd desktop-tauri && npm install
npm run tauri build
```

Output lands in `desktop-tauri/src-tauri/target/release/bundle/` (Cargo's
default, deeply-nested build directory):
- `dmg/Cortex_<version>_aarch64.dmg` (or `_x64.dmg` on an Intel Mac)
- `macos/Cortex.app` (the raw app bundle, if you just want to drag it to
  Applications directly instead of using the dmg)

For convenience, copy the finished files up to the top-level `release/`
folder after each build so they're easy to find without digging through
Cargo's target tree:

```bash
cp -R desktop-tauri/src-tauri/target/release/bundle/macos/Cortex.app release/Cortex.app
cp desktop-tauri/src-tauri/target/release/bundle/dmg/Cortex_*.dmg release/
```

`release/` is just a copy destination, not something Tauri writes to
directly - rerun those two lines after every `npm run tauri build` to keep
it up to date.

The app isn't code-signed or notarized (that requires a paid Apple Developer
account), so on first launch macOS Gatekeeper will show an "unidentified
developer" warning. The person installing it should right-click the app →
Open, or in System Settings → Privacy & Security click "Open Anyway". This
is normal for any app distributed outside the Mac App Store without a paid
developer certificate - it's not something wrong with the build.

## Building on Windows (not yet built - needs a Windows machine or CI)

PyInstaller does not cross-compile: a Windows `.exe` backend has to be built
by running PyInstaller *on Windows* (a real Windows machine, a VM, or a CI
runner like GitHub Actions - it cannot be produced from this Mac). The Tauri
shell itself also needs to be compiled on Windows for a Windows build.
Windows 10/11 ship WebView2 out of the box, so unlike Electron there's no
separate runtime to bundle for that part. Once you have a Windows
environment with Rust installed (`winget install Rustlang.Rustup`):

```powershell
# 1. Build the backend into a standalone binary
python -m venv venv-run
venv-run\Scripts\pip install -r requirements.txt pyinstaller
venv-run\Scripts\pyinstaller cortex_backend.spec --noconfirm

# 2. Build the frontend (same as macOS)
cd web
npm install
npm run build
cd ..

# 3. Install the Tauri CLI and build the installer
cd desktop-tauri
npm install
npm run tauri build
```

Output lands in `desktop-tauri\src-tauri\target\release\bundle\nsis\` (an
NSIS installer with a normal install wizard) and `\msi\` (an MSI installer,
if you'd rather distribute that format). Like the Mac build, it isn't
code-signed, so Windows SmartScreen will show an "unrecognized app" warning
on first run - the installer still works, the user just has to click "More
info" → "Run anyway".

The easiest way to actually get this build without owning a Windows machine
is a free GitHub Actions workflow using a `windows-latest` runner to run the
three steps above and upload `desktop-tauri/src-tauri/target/release/bundle/**`
as a build artifact.

## Rebuilding after future code changes

Any time you change the backend or frontend code, redo the matching step(s)
above and rerun `npm run tauri build` - there's no need to redo the icon or
Tauri project setup again, only the build/pack steps.
