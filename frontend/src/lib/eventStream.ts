// Faithful port of the SSE framing logic from web/static/app.js
// (parseEventBlock / readEventStream). The transport parsing is identical;
// callers supply an onEvent handler instead of mutating shared DOM state.
import type { StreamEvent } from "../types";

export function parseEventBlock(block: string): StreamEvent | null {
  let eventType = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) {
      eventType = line.slice(6).trim();
    } else if (line.startsWith("data:")) {
      dataLines.push(line.slice(5).trimStart());
    }
  }
  if (dataLines.length === 0) {
    return null;
  }
  return {
    type: eventType as StreamEvent["type"],
    data: JSON.parse(dataLines.join("\n")) as StreamEvent["data"],
  };
}

export async function readEventStream(
  response: Response,
  onEvent: (event: StreamEvent) => void,
  unavailableMessage: string,
): Promise<void> {
  if (response.body === null) {
    throw new Error(unavailableMessage);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    buffer += decoder.decode(value, { stream: !done }).replaceAll("\r\n", "\n");
    let boundary = buffer.indexOf("\n\n");
    while (boundary >= 0) {
      const block = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const event = parseEventBlock(block);
      if (event !== null) {
        onEvent(event);
      }
      boundary = buffer.indexOf("\n\n");
    }
    if (done) {
      return;
    }
  }
}
