// Reads the server-injected capability marker. See
// src/margpa_runtime_llm/web/app.py DATA_CONTROLS_BOOTSTRAP_DISABLED /
// DATA_CONTROLS_BOOTSTRAP_ENABLED, which rewrites this exact tag's text
// content before the response is sent. The tag itself must always be
// present verbatim in the built index.html so that string replacement can
// find it.
export function readDataControlsBootstrap(): boolean {
  const node = document.querySelector("#data-controls-bootstrap");
  try {
    const value = JSON.parse(node?.textContent ?? "{}") as { enabled?: unknown };
    return value.enabled === true;
  } catch {
    return false;
  }
}
