// Reads the server-injected capability marker. See
// src/margpa_runtime_llm/web/app.py GUARDRAIL_BOOTSTRAP_DISABLED /
// GUARDRAIL_BOOTSTRAP_ENABLED, which rewrites this exact tag's text
// content before the response is sent. The tag itself must always be
// present verbatim in the built index.html so that string replacement can
// find it.
export function readGuardrailGovernanceBootstrap(): boolean {
  const node = document.querySelector("#guardrail-bootstrap");
  try {
    const value = JSON.parse(node?.textContent ?? "{}") as { enabled?: unknown };
    return value.enabled === true;
  } catch {
    return false;
  }
}
