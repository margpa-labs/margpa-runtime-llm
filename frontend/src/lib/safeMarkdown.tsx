// Faithful TypeScript/React port of web/static/safe_markdown.js. The parser
// (parseSafeMarkdown, parseInline, safeLinkTarget) is unchanged in behavior;
// only the rendering step changes, from manual DOM node construction to
// returning React elements. This still never uses dangerouslySetInnerHTML,
// preserving the original "no innerHTML" safety property.
import { Fragment, type ReactNode } from "react";

const BLOCK_TAGS = new Set([
  "blockquote",
  "code_block",
  "heading",
  "horizontal_rule",
  "ordered_list",
  "paragraph",
  "table",
  "unordered_list",
]);

function containsControlCharacter(value: string): boolean {
  for (const character of value) {
    const code = character.codePointAt(0) ?? 0;
    if (code <= 0x1f || code === 0x7f) {
      return true;
    }
  }
  return false;
}

export function safeLinkTarget(rawTarget: string): string | null {
  const target = rawTarget.trim();
  if (!target || containsControlCharacter(target) || target.startsWith("//")) {
    return null;
  }
  const scheme = /^([a-z][a-z0-9+.-]*):/iu.exec(target);
  if (scheme !== null && !["http", "https", "mailto"].includes(scheme[1]!.toLowerCase())) {
    return null;
  }
  return target;
}

type InlineNode =
  | { type: "text"; text: string }
  | { type: "code"; text: string }
  | { type: "strong"; children: InlineNode[] }
  | { type: "emphasis"; children: InlineNode[] }
  | { type: "link"; target: string; external: boolean; children: InlineNode[] }
  | { type: "break" };

type TableAlignment = "left" | "center" | "right" | null;

type BlockNode =
  | { type: "horizontal_rule" }
  | { type: "code_block"; language: string | null; text: string }
  | { type: "heading"; level: number; children: InlineNode[] }
  | { type: "blockquote"; children: InlineNode[] }
  | { type: "ordered_list"; start: number; items: InlineNode[][] }
  | { type: "unordered_list"; items: InlineNode[][] }
  | { type: "paragraph"; children: InlineNode[] }
  | { type: "table"; align: TableAlignment[]; header: InlineNode[][]; rows: InlineNode[][][] };

function splitTableRow(line: string): string[] {
  let trimmed = line.trim();
  if (trimmed.startsWith("|")) {
    trimmed = trimmed.slice(1);
  }
  if (trimmed.endsWith("|") && !trimmed.endsWith("\\|")) {
    trimmed = trimmed.slice(0, -1);
  }
  const cells: string[] = [];
  let current = "";
  for (let index = 0; index < trimmed.length; index += 1) {
    const character = trimmed[index]!;
    if (character === "\\" && trimmed[index + 1] === "|") {
      current += "|";
      index += 1;
      continue;
    }
    if (character === "|") {
      cells.push(current.trim());
      current = "";
      continue;
    }
    current += character;
  }
  cells.push(current.trim());
  return cells;
}

function isTableDelimiterRow(line: string): boolean {
  const trimmed = line.trim();
  if (!trimmed.includes("|")) {
    return false;
  }
  // A delimiter cell always requires at least one hyphen, so an empty cell
  // here is never legitimate content — only ever a stray/doubled pipe
  // artifact (observed from real streamed model output) — and is dropped.
  const cells = splitTableRow(trimmed).filter((cell) => cell !== "");
  return cells.length > 0 && cells.every((cell) => /^:?-+:?$/u.test(cell));
}

function parseTableAlignment(cell: string): TableAlignment {
  const left = cell.startsWith(":");
  const right = cell.endsWith(":");
  if (left && right) {
    return "center";
  }
  if (right) {
    return "right";
  }
  if (left) {
    return "left";
  }
  return null;
}

export function parseSafeMarkdown(source: string): BlockNode[] {
  if (typeof source !== "string") {
    throw new TypeError("Markdown source must be a string.");
  }
  const normalized = source.replaceAll("\r\n", "\n").replaceAll("\r", "\n");
  const lines = normalized.split("\n");
  const blocks: BlockNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index]!;
    if (!line.trim()) {
      index += 1;
      continue;
    }

    const fence = /^ {0,3}```([a-z0-9_+-]*)\s*$/iu.exec(line);
    if (fence !== null) {
      const content: string[] = [];
      index += 1;
      while (index < lines.length && !/^ {0,3}```\s*$/u.test(lines[index]!)) {
        content.push(lines[index]!);
        index += 1;
      }
      if (index >= lines.length) {
        throw new Error("Unclosed fenced code block.");
      }
      index += 1;
      blocks.push({
        type: "code_block",
        language: fence[1] || null,
        text: content.join("\n"),
      });
      continue;
    }

    const heading = /^(#{1,6})\s+(.+)$/u.exec(line);
    if (heading !== null) {
      blocks.push({
        type: "heading",
        level: heading[1]!.length,
        children: parseInline(heading[2]!),
      });
      index += 1;
      continue;
    }

    if (/^ {0,3}((\*|-|_)\s*){3,}$/u.test(line)) {
      blocks.push({ type: "horizontal_rule" });
      index += 1;
      continue;
    }

    if (line.includes("|") && index + 1 < lines.length && isTableDelimiterRow(lines[index + 1]!)) {
      const header = splitTableRow(line).map((cell) => parseInline(cell));
      const align = splitTableRow(lines[index + 1]!)
        .filter((cell) => cell !== "")
        .map(parseTableAlignment);
      index += 2;
      const rows: InlineNode[][][] = [];
      while (index < lines.length && lines[index]!.trim() && lines[index]!.includes("|")) {
        rows.push(splitTableRow(lines[index]!).map((cell) => parseInline(cell)));
        index += 1;
      }
      blocks.push({ type: "table", align, header, rows });
      continue;
    }

    if (/^ {0,3}>\s?/u.test(line)) {
      const quote: string[] = [];
      while (index < lines.length && /^ {0,3}>\s?/u.test(lines[index]!)) {
        quote.push(lines[index]!.replace(/^ {0,3}>\s?/u, ""));
        index += 1;
      }
      blocks.push({ type: "blockquote", children: parseInline(quote.join("\n")) });
      continue;
    }

    const unordered = /^ {0,3}[-*+]\s+(.+)$/u.exec(line);
    if (unordered !== null) {
      const items: InlineNode[][] = [];
      while (index < lines.length) {
        const item = /^ {0,3}[-*+]\s+(.+)$/u.exec(lines[index]!);
        if (item === null) {
          break;
        }
        items.push(parseInline(item[1]!));
        index += 1;
      }
      blocks.push({ type: "unordered_list", items });
      continue;
    }

    const ordered = /^ {0,3}(\d+)[.)]\s+(.+)$/u.exec(line);
    if (ordered !== null) {
      const items: InlineNode[][] = [];
      const start = Number(ordered[1]);
      while (index < lines.length) {
        const item = /^ {0,3}(\d+)[.)]\s+(.+)$/u.exec(lines[index]!);
        if (item === null) {
          break;
        }
        items.push(parseInline(item[2]!));
        index += 1;
      }
      blocks.push({ type: "ordered_list", start, items });
      continue;
    }

    const paragraph = [line];
    index += 1;
    while (index < lines.length && lines[index]!.trim() && !startsBlock(lines[index]!)) {
      paragraph.push(lines[index]!);
      index += 1;
    }
    blocks.push({ type: "paragraph", children: parseInline(paragraph.join("\n")) });
  }

  if (blocks.some((block) => !BLOCK_TAGS.has(block.type))) {
    throw new Error("Unsupported Markdown block.");
  }
  return blocks;
}

function startsBlock(line: string): boolean {
  return (
    /^ {0,3}```/u.test(line) ||
    /^(#{1,6})\s+/u.test(line) ||
    /^ {0,3}>\s?/u.test(line) ||
    /^ {0,3}[-*+]\s+/u.test(line) ||
    /^ {0,3}\d+[.)]\s+/u.test(line) ||
    /^ {0,3}((\*|-|_)\s*){3,}$/u.test(line) ||
    (line.trim() !== "" && line.includes("|"))
  );
}

function parseInline(source: string): InlineNode[] {
  const nodes: InlineNode[] = [];
  let plain = "";
  let index = 0;
  // True at index 0 and right after a <br> break — the only positions a
  // block-level list marker could appear within inline content, since a
  // <br>-joined table cell is the one place list-like "- " text survives
  // down to this level at all (a real multi-line paragraph starting with
  // "- " is already caught by the block-level list parser beforehand).
  let atLineStart = true;

  const flush = (): void => {
    if (plain) {
      nodes.push({ type: "text", text: plain });
      plain = "";
    }
  };

  while (index < source.length) {
    if (atLineStart) {
      const bulletMatch = /^ {0,3}[-*+]\s+/u.exec(source.slice(index));
      atLineStart = false;
      if (bulletMatch !== null) {
        flush();
        plain += "• ";
        index += bulletMatch[0].length;
        continue;
      }
    }

    if (source[index] === "`") {
      const end = source.indexOf("`", index + 1);
      if (end > index + 1) {
        flush();
        nodes.push({ type: "code", text: source.slice(index + 1, end) });
        index = end + 1;
        continue;
      }
    }

    if (source[index] === "<") {
      // A narrow, safe exception to "never render raw HTML": only the
      // attribute-less <br> tag (no payload is structurally possible) is
      // recognized, since models commonly use it for intra-cell line breaks
      // in table cells, which can't otherwise contain a real newline. Any
      // other tag, or <br> with attributes, still falls through as inert text.
      const breakMatch = /^<br\s*\/?>/iu.exec(source.slice(index));
      if (breakMatch !== null) {
        flush();
        nodes.push({ type: "break" });
        index += breakMatch[0].length;
        atLineStart = true;
        continue;
      }
    }

    if (source[index] === "[") {
      const labelEnd = source.indexOf("](", index + 1);
      const targetEnd = labelEnd < 0 ? -1 : source.indexOf(")", labelEnd + 2);
      if (labelEnd > index + 1 && targetEnd > labelEnd + 2) {
        const label = source.slice(index + 1, labelEnd);
        const rawTarget = source.slice(labelEnd + 2, targetEnd);
        const target = safeLinkTarget(rawTarget);
        flush();
        if (target === null) {
          nodes.push({ type: "text", text: label });
        } else {
          nodes.push({
            type: "link",
            target,
            external: /^https?:/iu.test(target),
            children: parseInline(label),
          });
        }
        index = targetEnd + 1;
        continue;
      }
    }

    const marker = source.startsWith("**", index) ? "**" : source.startsWith("__", index) ? "__" : null;
    if (marker !== null) {
      const end = source.indexOf(marker, index + 2);
      if (end > index + 2) {
        flush();
        nodes.push({
          type: "strong",
          children: parseInline(source.slice(index + 2, end)),
        });
        index = end + 2;
        continue;
      }
    }

    if (source[index] === "*" || source[index] === "_") {
      const end = source.indexOf(source[index]!, index + 1);
      if (end > index + 1) {
        flush();
        nodes.push({
          type: "emphasis",
          children: parseInline(source.slice(index + 1, end)),
        });
        index = end + 1;
        continue;
      }
    }

    plain += source[index]!;
    index += 1;
  }
  flush();
  return nodes;
}

export function renderSafeMarkdownBlocks(blocks: BlockNode[]): ReactNode {
  return (
    <>
      {blocks.map((block, index) => (
        <Fragment key={index}>{renderBlock(block)}</Fragment>
      ))}
    </>
  );
}

export function renderSafeMarkdown(source: string): ReactNode {
  return renderSafeMarkdownBlocks(parseSafeMarkdown(source));
}

export function containsTable(blocks: BlockNode[]): boolean {
  return blocks.some((block) => block.type === "table");
}

function renderBlock(block: BlockNode): ReactNode {
  if (block.type === "horizontal_rule") {
    return <hr />;
  }
  if (block.type === "code_block") {
    return (
      <pre>
        <code data-language={block.language ?? undefined}>{block.text}</code>
      </pre>
    );
  }
  if (block.type === "heading") {
    const Heading = `h${block.level.toString()}` as "h1" | "h2" | "h3" | "h4" | "h5" | "h6";
    return <Heading>{renderInline(block.children)}</Heading>;
  }
  if (block.type === "blockquote") {
    return <blockquote>{renderInline(block.children)}</blockquote>;
  }
  if (block.type === "ordered_list") {
    return (
      <ol start={block.start !== 1 ? block.start : undefined}>
        {block.items.map((item, index) => (
          <li key={index}>{renderInline(item)}</li>
        ))}
      </ol>
    );
  }
  if (block.type === "unordered_list") {
    return (
      <ul>
        {block.items.map((item, index) => (
          <li key={index}>{renderInline(item)}</li>
        ))}
      </ul>
    );
  }
  if (block.type === "table") {
    return (
      <table>
        <thead>
          <tr>
            {block.header.map((cell, index) => (
              <th key={index} style={block.align[index] ? { textAlign: block.align[index] } : undefined}>
                {renderInline(cell)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {block.rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} style={block.align[cellIndex] ? { textAlign: block.align[cellIndex] } : undefined}>
                  {renderInline(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    );
  }
  return <p>{renderInline(block.children)}</p>;
}

function renderInline(nodes: InlineNode[]): ReactNode {
  return nodes.map((node, index) => {
    if (node.type === "text") {
      return <Fragment key={index}>{node.text}</Fragment>;
    }
    if (node.type === "code") {
      return <code key={index}>{node.text}</code>;
    }
    if (node.type === "strong") {
      return <strong key={index}>{renderInline(node.children)}</strong>;
    }
    if (node.type === "emphasis") {
      return <em key={index}>{renderInline(node.children)}</em>;
    }
    if (node.type === "break") {
      return <br key={index} />;
    }
    return (
      <a
        key={index}
        href={node.target}
        target={node.external ? "_blank" : undefined}
        rel={node.external ? "noopener noreferrer" : undefined}
      >
        {renderInline(node.children)}
      </a>
    );
  });
}
