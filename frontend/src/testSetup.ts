import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// `test.globals` is deliberately off (imports are explicit throughout this
// suite), so @testing-library/react's own auto-cleanup — which only
// self-registers when it finds afterEach already on globalThis — never
// fires on its own; without this, DOM nodes from one test leak into the next.
afterEach(cleanup);

// jsdom doesn't implement scrollIntoView (real browsers do); components that
// call it for "scroll latest message into view" would otherwise throw here.
if (typeof Element.prototype.scrollIntoView !== "function") {
  Element.prototype.scrollIntoView = () => undefined;
}
