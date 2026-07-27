import assert from "node:assert/strict";
import test from "node:test";

import {
  parseSafeMarkdown,
  safeLinkTarget,
} from "../../../src/margpa_runtime_llm/web/static/safe_markdown.js";

test("supported Japanese and English Markdown becomes an allowlisted syntax tree", () => {
  const blocks = parseSafeMarkdown(
    "# 見出し\n\n- **強調**\n- *emphasis* and `code`\n\n"
      + "1. first\n2. second\n\n> quote\n\n"
      + "[OpenAI](https://openai.com)\n\n```js\nconst safe = true;\n```\n\n---",
  );
  const serialized = JSON.stringify(blocks);

  for (const type of [
    "heading",
    "unordered_list",
    "ordered_list",
    "blockquote",
    "paragraph",
    "code_block",
    "horizontal_rule",
    "strong",
    "emphasis",
    "code",
    "link",
  ]) {
    assert.match(serialized, new RegExp(`"${type}"`));
  }
});

test("dangerous URL schemes are rejected instead of becoming links", () => {
  for (const target of [
    "javascript:alert(1)",
    "data:text/html,<script>alert(1)</script>",
    "vbscript:msgbox(1)",
    "//evil.example/path",
    "java\nscript:alert(1)",
  ]) {
    assert.equal(safeLinkTarget(target), null);
  }

  const serialized = JSON.stringify(
    parseSafeMarkdown("[run](javascript:alert(1))"),
  );
  assert.doesNotMatch(serialized, /"type":"link"/u);
  assert.doesNotMatch(serialized, /javascript:/u);
  assert.match(serialized, /run/u);
});

test("raw HTML and event handlers remain inert text", () => {
  const source = '<img src=x onerror="alert(1)"> <script>alert(1)</script>';
  const blocks = parseSafeMarkdown(source);

  assert.equal(blocks[0].type, "paragraph");
  assert.equal(blocks[0].children[0].type, "text");
  assert.equal(blocks[0].children[0].text, source);
});

test("external links carry the safe-link marker while relative links remain local", () => {
  const blocks = parseSafeMarkdown(
    "[external](https://example.com) [local](/docs) [mail](mailto:test@example.com)",
  );
  const links = blocks[0].children.filter((node) => node.type === "link");

  assert.deepEqual(
    links.map((link) => [link.target, link.external]),
    [
      ["https://example.com", true],
      ["/docs", false],
      ["mailto:test@example.com", false],
    ],
  );
});

test("malformed fenced Markdown fails closed for plain-text fallback", () => {
  assert.throws(() => parseSafeMarkdown("```js\nunfinished"), /Unclosed/u);
});
