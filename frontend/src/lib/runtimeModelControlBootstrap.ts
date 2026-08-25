interface RuntimeModelControlBootstrapPayload {
  enabled?: unknown;
}

export function readRuntimeModelControlBootstrap(): boolean {
  const node = document.querySelector("#runtime-model-control-bootstrap");
  if (node === null) {
    return false;
  }
  try {
    const payload = JSON.parse(node.textContent) as RuntimeModelControlBootstrapPayload;
    return payload.enabled === true;
  } catch {
    return false;
  }
}
