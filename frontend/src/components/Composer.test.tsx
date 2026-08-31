import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";
import Composer from "./Composer";

function baseProps() {
  return {
    language: "en" as const,
    value: "",
    onChange: vi.fn(),
    onSend: vi.fn(),
    onStop: vi.fn(),
    sendDisabled: false,
    stopDisabled: true,
    statusText: "",
    contextUsage: null,
    showContextUsage: false,
    webEvidenceEnabled: false,
    webEvidenceUrl: "",
    onWebEvidenceUrlChange: vi.fn(),
  };
}

describe("Composer", () => {
  test("does not render the Manual URL Evidence input when disabled", () => {
    render(<Composer {...baseProps()} />);
    expect(screen.queryByLabelText("Attach URL (this Turn only, optional)")).toBeNull();
  });

  test("renders and wires the Manual URL Evidence input when enabled", () => {
    const onWebEvidenceUrlChange = vi.fn();
    render(
      <Composer {...baseProps()} webEvidenceEnabled={true} onWebEvidenceUrlChange={onWebEvidenceUrlChange} />,
    );
    const input = screen.getByLabelText("Attach URL (this Turn only, optional)");
    fireEvent.change(input, { target: { value: "https://example.org/article" } });
    expect(onWebEvidenceUrlChange).toHaveBeenCalledWith("https://example.org/article");
  });

  test("the Manual URL Evidence input reflects the current value and disables with the composer", () => {
    render(
      <Composer
        {...baseProps()}
        webEvidenceEnabled={true}
        webEvidenceUrl="https://example.org/already-typed"
        sendDisabled={true}
      />,
    );
    const input = screen.getByLabelText("Attach URL (this Turn only, optional)");
    expect(input).toHaveValue("https://example.org/already-typed");
    expect(input).toBeDisabled();
  });
});
