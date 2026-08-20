import { useRef, useState } from "react";
import { translate, type TranslationKey } from "../i18n/translations";
import type { UiLanguage } from "../types";

interface CopyButtonProps {
  language: UiLanguage;
  text: string;
  translationKey?: TranslationKey;
  className?: string;
}

export default function CopyButton({
  language,
  text,
  translationKey = "copy",
  className = "message-copy secondary",
}: CopyButtonProps) {
  const [feedback, setFeedback] = useState<TranslationKey | null>(null);
  const timeoutRef = useRef<number | null>(null);

  const handleClick = async (): Promise<void> => {
    let next: TranslationKey;
    try {
      if (!("clipboard" in navigator)) {
        throw new Error("clipboard_unavailable");
      }
      await navigator.clipboard.writeText(text);
      next = "copied";
    } catch {
      next = "copyFailed";
    }
    setFeedback(next);
    if (timeoutRef.current !== null) {
      window.clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = window.setTimeout(() => {
      setFeedback(null);
    }, 1600);
  };

  const activeKey = feedback ?? translationKey;
  return (
    <button
      type="button"
      className={className}
      data-i18n-message={activeKey}
      onClick={() => void handleClick()}
    >
      {translate(language, activeKey)}
    </button>
  );
}
