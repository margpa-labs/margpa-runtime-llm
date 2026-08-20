import { useState } from "react";

// Generic same-shape port of the vanilla implementation's
// readStoredUiLanguage / readStoredUiTheme + setUiLanguage / setUiTheme
// pattern: a single localStorage key holding one of a small closed set of
// values, defaulting safely when storage is unavailable or the stored value
// is unrecognized.
export function usePreference<T extends string>(
  storageKey: string,
  allowedValues: readonly T[],
  defaultValue: T,
): [T, (value: T) => void] {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return stored !== null && (allowedValues as readonly string[]).includes(stored)
        ? (stored as T)
        : defaultValue;
    } catch {
      return defaultValue;
    }
  });

  const update = (next: T): void => {
    const resolved = (allowedValues as readonly string[]).includes(next) ? next : defaultValue;
    setValue(resolved);
    try {
      window.localStorage.setItem(storageKey, resolved);
    } catch {
      // Browser storage may be disabled; the in-memory value still works.
    }
  };

  return [value, update];
}
