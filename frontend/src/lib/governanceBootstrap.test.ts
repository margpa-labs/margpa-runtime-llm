import { afterEach, describe, expect, test } from "vitest";
import { readGovernanceBootstrap } from "./governanceBootstrap";

function setBootstrapTag(textContent: string | null): void {
  document.body.innerHTML = "";
  if (textContent === null) {
    return;
  }
  const script = document.createElement("script");
  script.id = "governance-bootstrap";
  script.type = "application/json";
  script.textContent = textContent;
  document.body.appendChild(script);
}

describe("readGovernanceBootstrap", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  test("returns true only when the tag literally says enabled:true", () => {
    setBootstrapTag('{"enabled":true}');
    expect(readGovernanceBootstrap()).toBe(true);
  });

  test("returns false for the disabled marker", () => {
    setBootstrapTag('{"enabled":false}');
    expect(readGovernanceBootstrap()).toBe(false);
  });

  test("fails closed when the tag is missing entirely", () => {
    setBootstrapTag(null);
    expect(readGovernanceBootstrap()).toBe(false);
  });

  test("fails closed on malformed JSON", () => {
    setBootstrapTag("not json");
    expect(readGovernanceBootstrap()).toBe(false);
  });

  test("fails closed on a truthy-but-not-strictly-true enabled value", () => {
    setBootstrapTag('{"enabled":"true"}');
    expect(readGovernanceBootstrap()).toBe(false);
  });
});
