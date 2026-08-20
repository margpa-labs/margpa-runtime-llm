import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import AccountFooter from "./AccountFooter";

describe("AccountFooter", () => {
  test("clicking it opens settings", () => {
    const onOpenSettings = vi.fn();
    render(<AccountFooter language="en" onOpenSettings={onOpenSettings} />);
    fireEvent.click(screen.getByRole("button", { name: "Account" }));
    expect(onOpenSettings).toHaveBeenCalled();
  });
});
