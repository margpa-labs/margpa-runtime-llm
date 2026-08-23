// Reads the server-injected capability marker. See
// src/margpa_runtime_llm/web/app.py RUNTIME_GOVERNANCE_BOOTSTRAP_DISABLED /
// RUNTIME_GOVERNANCE_BOOTSTRAP_ENABLED, which rewrites this exact tag's text
// content before the response is sent. The tag itself must always be
// present verbatim in the built index.html so that string replacement can
// find it.
export function readRuntimeGovernanceBootstrap(): boolean {
  const node = document.querySelector("#runtime-governance-bootstrap");
  try {
    const value = JSON.parse(node?.textContent ?? "{}") as { enabled?: unknown };
    return value.enabled === true;
  } catch {
    return false;
  }
}
