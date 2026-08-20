import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, test } from "vitest";
import { usePreference } from "./usePreference";

const KEY = "test.preference.v1";

describe("usePreference", () => {
  beforeEach(() => {
    window.localStorage.removeItem(KEY);
  });

  test("defaults to the provided value when nothing is stored", () => {
    const { result } = renderHook(() => usePreference<"a" | "b">(KEY, ["a", "b"], "a"));
    expect(result.current[0]).toBe("a");
  });

  test("reads an already-stored allowed value on init", () => {
    window.localStorage.setItem(KEY, "b");
    const { result } = renderHook(() => usePreference<"a" | "b">(KEY, ["a", "b"], "a"));
    expect(result.current[0]).toBe("b");
  });

  test("falls back to the default when the stored value is not in the allowed set", () => {
    window.localStorage.setItem(KEY, "unexpected");
    const { result } = renderHook(() => usePreference<"a" | "b">(KEY, ["a", "b"], "a"));
    expect(result.current[0]).toBe("a");
  });

  test("updating persists the new value to localStorage under the given key", () => {
    const { result } = renderHook(() => usePreference<"a" | "b">(KEY, ["a", "b"], "a"));
    act(() => {
      result.current[1]("b");
    });
    expect(result.current[0]).toBe("b");
    expect(window.localStorage.getItem(KEY)).toBe("b");
  });

  test("updating with a disallowed value resolves to the default instead", () => {
    const { result } = renderHook(() => usePreference<"a" | "b">(KEY, ["a", "b"], "a"));
    act(() => {
      // @ts-expect-error intentionally passing a runtime-invalid value
      result.current[1]("z");
    });
    expect(result.current[0]).toBe("a");
    expect(window.localStorage.getItem(KEY)).toBe("a");
  });
});
