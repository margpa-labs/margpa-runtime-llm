import { describe, expect, test } from "vitest";
import { parseEventBlock, readEventStream } from "./eventStream";

describe("parseEventBlock", () => {
  test("parses an event: + data: block into a typed StreamEvent", () => {
    const event = parseEventBlock('event: start\ndata: {"request_id":"abc"}');
    expect(event).toEqual({ type: "start", data: { request_id: "abc" } });
  });

  test("defaults to type message when no event: line is present", () => {
    const event = parseEventBlock('data: {"text":"hi"}');
    expect(event?.type).toBe("message");
  });

  test("joins multiple data: lines before parsing JSON", () => {
    const event = parseEventBlock('event: delta\ndata: {"text":\ndata: "hi"}');
    expect(event).toEqual({ type: "delta", data: { text: "hi" } });
  });

  test("returns null when the block has no data: lines", () => {
    expect(parseEventBlock("event: start")).toBeNull();
  });
});

function sseResponse(chunks: string[]): Response {
  const encoder = new TextEncoder();
  const stream = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) {
        controller.enqueue(encoder.encode(chunk));
      }
      controller.close();
    },
  });
  return new Response(stream);
}

describe("readEventStream", () => {
  test("emits one event per blank-line-delimited block, even split across chunks", async () => {
    const events: unknown[] = [];
    const response = sseResponse([
      'event: start\ndata: {"request_id":"1"}\n\n',
      'event: delta\ndata: {"text":"a',
      'b"}\n\nevent: completed\ndata: {"finish_reason":"stop"}\n\n',
    ]);
    await readEventStream(response, (event) => events.push(event), "unavailable");
    expect(events).toEqual([
      { type: "start", data: { request_id: "1" } },
      { type: "delta", data: { text: "ab" } },
      { type: "completed", data: { finish_reason: "stop" } },
    ]);
  });

  test("throws the given message when the response has no body", async () => {
    const response = new Response(null);
    await expect(readEventStream(response, () => undefined, "stream unavailable")).rejects.toThrow(
      "stream unavailable",
    );
  });
});
