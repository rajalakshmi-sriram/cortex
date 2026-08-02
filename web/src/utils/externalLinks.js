import { openUrl } from '@tauri-apps/plugin-opener';

/**
 * Makes every external link in the app (journal homepages, DOI links, tool
 * recommendation chips, etc.) actually open somewhere, on both the plain
 * web app and the packaged desktop app.
 *
 * In a normal browser, <a target="_blank"> already just works - nothing to
 * do there. Inside the Tauri desktop app's WebView, though, clicking a
 * target="_blank" link does nothing on its own: Tauri doesn't
 * automatically forward "open a new window" requests to the OS's default
 * browser unless told to. Without this, every external link in the app was
 * a dead click in the desktop build.
 *
 * This installs one document-wide click listener (mounted once from
 * App.jsx) rather than touching every individual <a> tag across the app -
 * it only takes over when running inside Tauri, and only for links that
 * actually leave the app (an absolute http/https href).
 */
export function initExternalLinkHandler() {
  if (!window.__TAURI__) return; // plain web app - browser already handles this natively

  document.addEventListener('click', (e) => {
    const anchor = e.target.closest('a[href]');
    if (!anchor) return;

    const href = anchor.getAttribute('href') || '';
    if (!/^https?:\/\//i.test(href)) return; // in-app/relative links - leave to the router

    e.preventDefault();
    openUrl(href).catch((err) => {
      console.error('Failed to open external link:', err);
    });
  });
}
