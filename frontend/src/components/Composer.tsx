import { useLayoutEffect, useRef } from "react";
import ContextUsageGauge from "./ContextUsageGauge";
import { translate } from "../i18n/translations";
import type { ContextUsage, UiLanguage } from "../types";

interface ComposerProps {
  language: UiLanguage;
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  onStop: () => void;
  sendDisabled: boolean;
  stopDisabled: boolean;
  statusText: string;
  contextUsage: ContextUsage | null;
  showContextUsage: boolean;
  // P8-A: Manual URL Evidence for the next Turn only (P8-REQ-002/
  // P8-ACC-009) - `webEvidenceEnabled` gates visibility on the Settings
  // Web Search toggle, mirroring `WebSearchPanel`'s own `toggleEnabled`.
  webEvidenceEnabled: boolean;
  webEvidenceUrl: string;
  onWebEvidenceUrlChange: (value: string) => void;
}

export default function Composer({
  language,
  value,
  onChange,
  onSend,
  onStop,
  sendDisabled,
  stopDisabled,
  statusText,
  contextUsage,
  showContextUsage,
  webEvidenceEnabled,
  webEvidenceUrl,
  onWebEvidenceUrlChange,
}: ComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  // Auto-grow height only (width stays fixed to the composer's own width).
  // Resetting to "auto" before reading scrollHeight is required — otherwise
  // scrollHeight would still reflect the previous, larger height on delete.
  useLayoutEffect(() => {
    const node = textareaRef.current;
    if (node === null) {
      return;
    }
    const resize = (): void => {
      node.style.height = "auto";
      node.style.height = `${node.scrollHeight.toString()}px`;
    };
    resize();
    // On first mount specifically, the stylesheet (font metrics, padding,
    // line-height) can still be settling when this first measurement runs,
    // producing a too-tall reading that then sticks as an inline style.
    // Re-measuring once more after the browser's next paint self-corrects it.
    const frame = requestAnimationFrame(resize);
    return () => {
      cancelAnimationFrame(frame);
    };
  }, [value]);

  return (
    <section id="composer" className="composer" aria-label={translate(language, "composerLabel")}>
      {webEvidenceEnabled ? (
        <div className="composer-web-evidence">
          <label htmlFor="composer-web-evidence-url">
            {translate(language, "composerWebEvidenceLabel")}
          </label>
          <input
            id="composer-web-evidence-url"
            type="url"
            placeholder={translate(language, "composerWebEvidencePlaceholder")}
            disabled={sendDisabled}
            value={webEvidenceUrl}
            onChange={(event) => {
              onWebEvidenceUrlChange(event.target.value);
            }}
          />
        </div>
      ) : null}
      <label htmlFor="prompt" id="prompt-label">
        {translate(language, "promptLabel")}
      </label>
      <textarea
        id="prompt"
        ref={textareaRef}
        rows={1}
        placeholder={translate(language, "promptPlaceholder")}
        disabled={sendDisabled}
        value={value}
        onChange={(event) => {
          onChange(event.target.value);
        }}
        onKeyDown={(event) => {
          if (!event.nativeEvent.isComposing && (event.metaKey || event.ctrlKey) && event.key === "Enter") {
            event.preventDefault();
            onSend();
          }
        }}
      />
      <div className="actions">
        <span id="generation-status">{statusText}</span>
        <span id="shortcut-hint" className="shortcut-hint">
          {translate(language, "shortcutHint")}
        </span>
        {showContextUsage && <ContextUsageGauge language={language} usage={contextUsage} />}
        <button id="stop" className="secondary" type="button" disabled={stopDisabled} onClick={onStop}>
          {translate(language, "stop")}
        </button>
        <button id="send" className="primary" type="button" disabled={sendDisabled} onClick={onSend}>
          {translate(language, "send")}
        </button>
      </div>
    </section>
  );
}
