import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import CopyButton from "./CopyButton";

describe("CopyButton", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  test("shows the copied feedback after a successful clipboard write, then reverts", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });

    render(<CopyButton language="en" text="hello" />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button"));
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(writeText).toHaveBeenCalledWith("hello");
    expect(screen.getByRole("button")).toHaveTextContent("Copied");

    act(() => {
      vi.advanceTimersByTime(1600);
    });
    expect(screen.getByRole("button")).toHaveTextContent("Copy");
  });

  test("shows copy-failed feedback when the Clipboard API is unavailable", async () => {
    vi.stubGlobal("navigator", {});

    render(<CopyButton language="en" text="hello" />);
    await act(async () => {
      fireEvent.click(screen.getByRole("button"));
      await Promise.resolve();
      await Promise.resolve();
    });

    expect(screen.getByRole("button")).toHaveTextContent("Could not copy");
  });
});
