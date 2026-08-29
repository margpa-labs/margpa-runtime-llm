import type { ProviderSelectionStatus } from "../types";

export function mergeProviderSelectionStatus(
  current: ProviderSelectionStatus | null,
  incoming: ProviderSelectionStatus,
): ProviderSelectionStatus {
  if (current === null) {
    return incoming;
  }
  return (incoming.revision ?? -1) >= (current.revision ?? -1) ? incoming : current;
}
