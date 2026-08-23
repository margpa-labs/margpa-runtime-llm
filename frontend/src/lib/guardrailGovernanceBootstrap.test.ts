import { afterEach, describe, expect, test } from "vitest";
import { readGuardrailGovernanceBootstrap } from "./guardrailGovernanceBootstrap";

function setBootstrapTag(textContent: string | null): void {
  document.body.innerHTML = "";
  if (textContent === null) {
    return;
  }
  const script = document.createElement("script");
  script.id = "guardrail-bootstrap";
  script.type = "application/json";
  script.textContent = textContent;
  document.body.appendChild(script);
}

describe("readGuardrailGovernanceBootstrap", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  test("returns true only when the tag literally says enabled:true", () => {
    setBootstrapTag('{"enabled":true}');
    expect(readGuardrailGovernanceBootstrap()).toBe(true);
  });

  test("returns false for the disabled marker", () => {
    setBootstrapTag('{"enabled":false}');
    expect(readGuardrailGovernanceBootstrap()).toBe(false);
  });

  test("fails closed when the tag is missing entirely", () => {
    setBootstrapTag(null);
    expect(readGuardrailGovernanceBootstrap()).toBe(false);
  });

  test("fails closed on malformed JSON", () => {
    setBootstrapTag("not json");
    expect(readGuardrailGovernanceBootstrap()).toBe(false);
  });

  test("fails closed on a truthy-but-not-strictly-true enabled value", () => {
    setBootstrapTag('{"enabled":"true"}');
    expect(readGuardrailGovernanceBootstrap()).toBe(false);
  });
});
