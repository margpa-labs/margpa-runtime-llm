import { describe, expect, test } from "vitest";
import { DEFAULT_UI_LANGUAGE, knownServerMessages, translate, translations } from "./translations";

describe("translate", () => {
  test("resolves a plain key for both languages", () => {
    expect(translate("ja", "send")).toBe(translations.ja.send);
    expect(translate("en", "send")).toBe(translations.en.send);
    expect(translations.ja.send).not.toBe(translations.en.send);
  });

  test("interpolates a single {placeholder}", () => {
    expect(translate("ja", "completed", { reason: "length" })).toBe("完了 (length)");
    expect(translate("en", "completed", { reason: "length" })).toBe("Completed (length)");
  });

  test("interpolates a value embedded mid-string", () => {
    expect(translate("en", "warning", { message: "disk full" })).toBe("Warning: disk full");
  });

  test(`defaults to "${DEFAULT_UI_LANGUAGE}" as the language every TranslationKey is defined against`, () => {
    const jaKeys = Object.keys(translations[DEFAULT_UI_LANGUAGE]).sort();
    const enKeys = Object.keys(translations.en).sort();
    expect(enKeys).toEqual(jaKeys);
  });
});

describe("knownServerMessages", () => {
  test("every mapped code resolves to a real translation key", () => {
    for (const key of Object.values(knownServerMessages)) {
      expect(translations.ja[key]).toBeTypeOf("string");
      expect(translations.en[key]).toBeTypeOf("string");
    }
  });
});
