const BLOCK_TAGS = new Set([
  "blockquote",
  "code_block",
  "heading",
  "horizontal_rule",
  "ordered_list",
  "paragraph",
  "unordered_list",
]);

export function safeLinkTarget(rawTarget) {
  const target = rawTarget.trim();
  if (!target || /[\u0000-\u001f\u007f]/u.test(target) || target.startsWith("//")) {
    return null;
  }
  const scheme = target.match(/^([a-z][a-z0-9+.-]*):/iu);
  if (scheme !== null && !["http", "https", "mailto"].includes(scheme[1].toLowerCase())) {
    return null;
  }
  return target;
}

export function parseSafeMarkdown(source) {
  if (typeof source !== "string") {
    throw new TypeError("Markdown source must be a string.");
  }
  const normalized = source.replaceAll("\r\n", "\n").replaceAll("\r", "\n");
  const lines = normalized.split("\n");
  const blocks = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim()) {
      index += 1;
      continue;
    }

    const fence = line.match(/^ {0,3}```([a-z0-9_+-]*)\s*$/iu);
    if (fence !== null) {
      const content = [];
      index += 1;
      while (index < lines.length && !/^ {0,3}```\s*$/u.test(lines[index])) {
        content.push(lines[index]);
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

    const heading = line.match(/^(#{1,6})\s+(.+)$/u);
    if (heading !== null) {
      blocks.push({
        type: "heading",
        level: heading[1].length,
        children: parseInline(heading[2]),
      });
      index += 1;
      continue;
    }

    if (/^ {0,3}((\*|-|_)\s*){3,}$/u.test(line)) {
      blocks.push({ type: "horizontal_rule" });
      index += 1;
      continue;
    }

    if (/^ {0,3}>\s?/u.test(line)) {
      const quote = [];
      while (index < lines.length && /^ {0,3}>\s?/u.test(lines[index])) {
        quote.push(lines[index].replace(/^ {0,3}>\s?/u, ""));
        index += 1;
      }
      blocks.push({ type: "blockquote", children: parseInline(quote.join("\n")) });
      continue;
    }

    const unordered = line.match(/^ {0,3}[-*+]\s+(.+)$/u);
    if (unordered !== null) {
      const items = [];
      while (index < lines.length) {
        const item = lines[index].match(/^ {0,3}[-*+]\s+(.+)$/u);
        if (item === null) {
          break;
        }
        items.push(parseInline(item[1]));
        index += 1;
      }
      blocks.push({ type: "unordered_list", items });
      continue;
    }

    const ordered = line.match(/^ {0,3}(\d+)[.)]\s+(.+)$/u);
    if (ordered !== null) {
      const items = [];
      const start = Number(ordered[1]);
      while (index < lines.length) {
        const item = lines[index].match(/^ {0,3}(\d+)[.)]\s+(.+)$/u);
        if (item === null) {
          break;
        }
        items.push(parseInline(item[2]));
        index += 1;
      }
      blocks.push({ type: "ordered_list", start, items });
      continue;
    }

    const paragraph = [line];
    index += 1;
    while (
      index < lines.length
      && lines[index].trim()
      && !startsBlock(lines[index])
    ) {
      paragraph.push(lines[index]);
      index += 1;
    }
    blocks.push({ type: "paragraph", children: parseInline(paragraph.join("\n")) });
  }

  if (blocks.some((block) => !BLOCK_TAGS.has(block.type))) {
    throw new Error("Unsupported Markdown block.");
  }
  return blocks;
}

function startsBlock(line) {
  return (
    /^ {0,3}```/u.test(line)
    || /^(#{1,6})\s+/u.test(line)
    || /^ {0,3}>\s?/u.test(line)
    || /^ {0,3}[-*+]\s+/u.test(line)
    || /^ {0,3}\d+[.)]\s+/u.test(line)
    || /^ {0,3}((\*|-|_)\s*){3,}$/u.test(line)
  );
}

function parseInline(source) {
  const nodes = [];
  let plain = "";
  let index = 0;

  const flush = () => {
    if (plain) {
      nodes.push({ type: "text", text: plain });
      plain = "";
    }
  };

  while (index < source.length) {
    if (source[index] === "`") {
      const end = source.indexOf("`", index + 1);
      if (end > index + 1) {
        flush();
        nodes.push({ type: "code", text: source.slice(index + 1, end) });
        index = end + 1;
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

    const marker = source.startsWith("**", index)
      ? "**"
      : source.startsWith("__", index)
        ? "__"
        : null;
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
      const end = source.indexOf(source[index], index + 1);
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

    plain += source[index];
    index += 1;
  }
  flush();
  return nodes;
}

export function renderSafeMarkdown(source, documentRef = document) {
  const fragment = documentRef.createDocumentFragment();
  for (const block of parseSafeMarkdown(source)) {
    fragment.append(renderBlock(block, documentRef));
  }
  return fragment;
}

function renderBlock(block, documentRef) {
  if (block.type === "horizontal_rule") {
    return documentRef.createElement("hr");
  }
  if (block.type === "code_block") {
    const pre = documentRef.createElement("pre");
    const code = documentRef.createElement("code");
    code.textContent = block.text;
    if (block.language !== null) {
      code.dataset.language = block.language;
    }
    pre.append(code);
    return pre;
  }
  if (block.type === "heading") {
    const heading = documentRef.createElement(`h${block.level}`);
    appendInline(heading, block.children, documentRef);
    return heading;
  }
  if (block.type === "blockquote") {
    const quote = documentRef.createElement("blockquote");
    appendInline(quote, block.children, documentRef);
    return quote;
  }
  if (block.type === "ordered_list" || block.type === "unordered_list") {
    const list = documentRef.createElement(block.type === "ordered_list" ? "ol" : "ul");
    if (block.type === "ordered_list" && block.start !== 1) {
      list.start = block.start;
    }
    for (const item of block.items) {
      const listItem = documentRef.createElement("li");
      appendInline(listItem, item, documentRef);
      list.append(listItem);
    }
    return list;
  }
  const paragraph = documentRef.createElement("p");
  appendInline(paragraph, block.children, documentRef);
  return paragraph;
}

function appendInline(parent, nodes, documentRef) {
  for (const node of nodes) {
    if (node.type === "text") {
      parent.append(documentRef.createTextNode(node.text));
      continue;
    }
    if (node.type === "code") {
      const code = documentRef.createElement("code");
      code.textContent = node.text;
      parent.append(code);
      continue;
    }
    if (node.type === "emphasis" || node.type === "strong") {
      const emphasis = documentRef.createElement(node.type === "strong" ? "strong" : "em");
      appendInline(emphasis, node.children, documentRef);
      parent.append(emphasis);
      continue;
    }
    if (node.type === "link") {
      const link = documentRef.createElement("a");
      link.href = node.target;
      if (node.external) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
      }
      appendInline(link, node.children, documentRef);
      parent.append(link);
      continue;
    }
    throw new Error("Unsupported Markdown inline node.");
  }
}
