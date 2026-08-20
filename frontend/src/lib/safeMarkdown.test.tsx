import { describe, expect, test } from "vitest";
import { render } from "@testing-library/react";
import { parseSafeMarkdown, renderSafeMarkdown, safeLinkTarget } from "./safeMarkdown";

describe("parseSafeMarkdown", () => {
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
      expect(serialized).toMatch(new RegExp(`"${type}"`));
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
      expect(safeLinkTarget(target)).toBeNull();
    }

    const serialized = JSON.stringify(parseSafeMarkdown("[run](javascript:alert(1))"));
    expect(serialized).not.toMatch(/"type":"link"/u);
    expect(serialized).not.toMatch(/javascript:/u);
    expect(serialized).toMatch(/run/u);
  });

  test("raw HTML and event handlers remain inert text", () => {
    const source = '<img src=x onerror="alert(1)"> <script>alert(1)</script>';
    const blocks = parseSafeMarkdown(source);

    expect(blocks[0]?.type).toBe("paragraph");
    const block = blocks[0];
    if (block?.type !== "paragraph") throw new Error("expected paragraph");
    expect(block.children[0]?.type).toBe("text");
    if (block.children[0]?.type !== "text") throw new Error("expected text node");
    expect(block.children[0].text).toBe(source);
  });

  test("a bare <br> becomes a break node, but <br> with attributes stays inert text", () => {
    for (const variant of ["<br>", "<br/>", "<br />", "<BR>"]) {
      const blocks = parseSafeMarkdown(`a${variant}b`);
      const block = blocks[0];
      if (block?.type !== "paragraph") throw new Error("expected paragraph");
      expect(block.children.map((node) => node.type)).toEqual(["text", "break", "text"]);
    }

    const withAttribute = parseSafeMarkdown('a<br onclick="evil()">b');
    const block = withAttribute[0];
    if (block?.type !== "paragraph") throw new Error("expected paragraph");
    expect(block.children).toHaveLength(1);
    expect(block.children[0]).toMatchObject({ type: "text", text: 'a<br onclick="evil()">b' });
  });

  test("<br> inside a table cell becomes a real line break, matching a common model authoring pattern", () => {
    const blocks = parseSafeMarkdown(
      "| A |\n|---|\n| line1<br>line2<br/>line3 |",
    );
    const table = blocks[0];
    if (table?.type !== "table") throw new Error("expected table");
    expect(table.rows[0]?.[0]?.map((node) => node.type)).toEqual([
      "text",
      "break",
      "text",
      "break",
      "text",
    ]);
  });

  test("a leading list marker (-, *, +) right after <br> becomes a bullet character, not a literal dash", () => {
    const blocks = parseSafeMarkdown(
      "| A |\n|---|\n| - 会話型LLM<br>* 語彙豊か<br>+ 自然な対話が得意 |",
    );
    const table = blocks[0];
    if (table?.type !== "table") throw new Error("expected table");
    const cell = table.rows[0]?.[0]?.filter((node) => node.type === "text");
    expect(cell?.map((node) => node.text)).toEqual([
      "• 会話型LLM",
      "• 語彙豊か",
      "• 自然な対話が得意",
    ]);
  });

  test("a mid-line hyphen (not at a line start) is left untouched", () => {
    const blocks = parseSafeMarkdown("value is -5, not a bullet");
    const block = blocks[0];
    if (block?.type !== "paragraph") throw new Error("expected paragraph");
    expect(block.children[0]).toMatchObject({ type: "text", text: "value is -5, not a bullet" });
  });

  test("external links carry the safe-link marker while relative links remain local", () => {
    const blocks = parseSafeMarkdown(
      "[external](https://example.com) [local](/docs) [mail](mailto:test@example.com)",
    );
    const block = blocks[0];
    if (block?.type !== "paragraph") throw new Error("expected paragraph");
    const links = block.children.filter((node) => node.type === "link");

    expect(links.map((link) => [link.target, link.external])).toEqual([
      ["https://example.com", true],
      ["/docs", false],
      ["mailto:test@example.com", false],
    ]);
  });

  test("malformed fenced Markdown fails closed for plain-text fallback", () => {
    expect(() => parseSafeMarkdown("```js\nunfinished")).toThrow(/Unclosed/u);
  });

  test("a GFM pipe table becomes a table block with header, alignment, and rows", () => {
    const blocks = parseSafeMarkdown(
      "| 能力 | 機能 | 説明 |\n"
        + "|------|------|------|\n"
        + "| ✅ 文章生成 | ✅ | 自然な文章をつくる |\n"
        + "| ✅ 質問への回答 | ✅ | ユーザーの質問に答える |",
    );
    expect(blocks).toHaveLength(1);
    const table = blocks[0];
    if (table?.type !== "table") throw new Error("expected table");
    expect(table.header.map((cell) => (cell[0]?.type === "text" ? cell[0].text : ""))).toEqual([
      "能力",
      "機能",
      "説明",
    ]);
    expect(table.align).toEqual([null, null, null]);
    expect(table.rows).toHaveLength(2);
    expect(table.rows[0]?.[0]?.[0]).toMatchObject({ type: "text", text: "✅ 文章生成" });
  });

  test("delimiter row alignment markers (:---, :---:, ---:) map to left/center/right", () => {
    const blocks = parseSafeMarkdown("| A | B | C |\n| :--- | :---: | ---: |\n| a | b | c |");
    const table = blocks[0];
    if (table?.type !== "table") throw new Error("expected table");
    expect(table.align).toEqual(["left", "center", "right"]);
  });

  test("an escaped pipe inside a cell does not split the cell", () => {
    const blocks = parseSafeMarkdown("| A | B |\n|---|---|\n| a\\|b | c |");
    const table = blocks[0];
    if (table?.type !== "table") throw new Error("expected table");
    expect(table.rows[0]?.[0]?.[0]).toMatchObject({ type: "text", text: "a|b" });
  });

  test("a delimiter row with a stray doubled trailing pipe (observed real model output) still parses as a table", () => {
    const blocks = parseSafeMarkdown(
      "| 能力 | 機能 | 説明 |\n"
        + "|------|------||\n"
        + "| 文章生成 | 文章作成 | 指示に従って生成する。 |",
    );
    expect(blocks).toHaveLength(1);
    expect(blocks[0]?.type).toBe("table");
  });

  test("a table header without a following delimiter row falls back to a paragraph (streaming-safe)", () => {
    const blocks = parseSafeMarkdown("| 能力 | 機能 | 説明 |");
    expect(blocks).toHaveLength(1);
    expect(blocks[0]?.type).toBe("paragraph");
  });

  test("a delimiter row still mid-stream (not yet arrived) does not throw", () => {
    expect(() => parseSafeMarkdown("| 能力 | 機能 |\n|--")).not.toThrow();
  });
});

describe("renderSafeMarkdown", () => {
  test("never renders raw HTML: dangerous markup shows as literal text, not real elements", () => {
    const source = '<img src=x onerror="alert(1)"> <script>alert(1)</script>';
    const { container } = render(<>{renderSafeMarkdown(source)}</>);

    expect(container.querySelector("img")).toBeNull();
    expect(container.querySelector("script")).toBeNull();
    expect(container.textContent).toBe(source);
  });

  test("external links get target=_blank and rel=noopener noreferrer; local links do not", () => {
    const { container } = render(
      <>{renderSafeMarkdown("[external](https://example.com) [local](/docs)")}</>,
    );
    const anchors = container.querySelectorAll("a");
    expect(anchors).toHaveLength(2);
    expect(anchors[0]?.getAttribute("href")).toBe("https://example.com");
    expect(anchors[0]?.getAttribute("target")).toBe("_blank");
    expect(anchors[0]?.getAttribute("rel")).toBe("noopener noreferrer");
    expect(anchors[1]?.getAttribute("href")).toBe("/docs");
    expect(anchors[1]?.hasAttribute("target")).toBe(false);
  });

  test("a rejected link target renders as plain text, not an anchor", () => {
    // The inline parser locates the link's closing ")" with a plain
    // indexOf, so a ")" inside the (rejected) URL itself — as in
    // "javascript:alert(1)" — ends the target early and leaves a stray
    // ")" as trailing text. That's pre-existing, faithfully-ported parser
    // behavior; the security property under test is just "no anchor,
    // no javascript: scheme anywhere in the output".
    const { container } = render(<>{renderSafeMarkdown("[run](javascript:alert(1))")}</>);
    expect(container.querySelector("a")).toBeNull();
    expect(container.textContent).toContain("run");
    expect(container.innerHTML).not.toContain("javascript:");
  });

  test("a Markdown table renders as a real <table> with <thead>/<tbody>, not a flattened paragraph", () => {
    const { container } = render(
      <>
        {renderSafeMarkdown(
          "| 能力 | 機能 | 説明 |\n"
            + "|------|------|------|\n"
            + "| ✅ 文章生成 | ✅ | 自然な文章をつくる |\n"
            + "| ✅ 質問への回答 | ✅ | ユーザーの質問に答える |",
        )}
      </>,
    );
    const table = container.querySelector("table");
    expect(table).not.toBeNull();
    expect(container.querySelectorAll("thead th")).toHaveLength(3);
    expect(container.querySelectorAll("tbody tr")).toHaveLength(2);
    expect(container.querySelectorAll("tbody td")).toHaveLength(6);
    expect(container.querySelector("p")).toBeNull();
  });

  test("alignment markers apply text-align to the corresponding column", () => {
    const { container } = render(
      <>{renderSafeMarkdown("| A | B | C |\n| :--- | :---: | ---: |\n| a | b | c |")}</>,
    );
    const headers = container.querySelectorAll("th");
    expect(headers[0]).toHaveStyle({ textAlign: "left" });
    expect(headers[1]).toHaveStyle({ textAlign: "center" });
    expect(headers[2]).toHaveStyle({ textAlign: "right" });
  });
});
