import { afterEach, describe, expect, test } from "vitest";
import { readRuntimeModelControlBootstrap } from "./runtimeModelControlBootstrap";

function setBootstrapTag(textContent: string | null): void {
  document.body.innerHTML = "";
  if (textContent === null) {
    return;
  }
  const script = document.createElement("script");
  script.id = "runtime-model-control-bootstrap";
  script.type = "application/json";
  script.textContent = textContent;
  document.body.appendChild(script);
}

describe("readRuntimeModelControlBootstrap", () => {
  afterEach(() => {
    document.body.innerHTML = "";
  });

  test("returns true only for literal enabled true", () => {
    setBootstrapTag('{"enabled":true}');
    expect(readRuntimeModelControlBootstrap()).toBe(true);
  });

  test.each([null, '{"enabled":false}', "not json", '{"enabled":"true"}'])(
    "fails closed for %s",
    (payload) => {
      setBootstrapTag(payload);
      expect(readRuntimeModelControlBootstrap()).toBe(false);
    },
  );
});
