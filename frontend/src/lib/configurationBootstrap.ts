// Reads the server-injected capability marker. See
// src/margpa_runtime_llm/web/app.py CONFIGURATION_BOOTSTRAP_DISABLED /
// CONFIGURATION_BOOTSTRAP_ENABLED, which rewrites this exact tag's text
// content before the response is sent. The tag itself must always be
// present verbatim in the built index.html so that string replacement can
// find it.
export function readConfigurationBootstrap(): boolean {
  const node = document.querySelector("#configuration-bootstrap");
  try {
    const value = JSON.parse(node?.textContent ?? "{}") as { enabled?: unknown };
    return value.enabled === true;
  } catch {
    return false;
  }
}
