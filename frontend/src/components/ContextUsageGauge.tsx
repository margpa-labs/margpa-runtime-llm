import { useEffect, useRef, useState } from "react";
import { translate } from "../i18n/translations";
import type { ContextUsage, UiLanguage } from "../types";

interface ContextUsageGaugeProps {
  language: UiLanguage;
  usage: ContextUsage | null;
}

const RING_RADIUS = 8;
const RING_CIRCUMFERENCE = 2 * Math.PI * RING_RADIUS;

// Round gauge icon + click-toggle breakdown panel, positioned near the
// composer. Interaction mirrors SidebarToggleButton exactly (click toggles
// state, hover only reveals a one-line tooltip naming the action) — the
// same established pattern, applied to a second button.
export default function ContextUsageGauge({ language, usage }: ContextUsageGaugeProps) {
  const [panelOpen, setPanelOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);
  const available = usage !== null;
  const ratio = usage === null ? 0 : Math.min(1, Math.max(0, usage.usage_ratio));
  const percentLabel = usage === null ? "—" : `${Math.round(ratio * 100).toString()}%`;
  const tooltipLabel = translate(
    language,
    !available ? "contextUsageUnavailable" : panelOpen ? "contextUsageToggleHide" : "contextUsageToggleShow",
  );
  const dashOffset = RING_CIRCUMFERENCE * (1 - ratio);
  const fillLevel = ratio >= 0.95 ? "danger" : ratio >= 0.85 ? "warn" : "normal";

  // Outside-click closes the panel, mirroring ChatListItem's own options-menu
  // pattern (a small anchored popover, not a full-screen modal — the
  // SettingsModal backdrop pattern doesn't fit here since there is no
  // full-screen overlay dimming the rest of the app for this gauge).
  useEffect(() => {
    if (!panelOpen) {
      return;
    }
    const handleOutsideClick = (event: MouseEvent): void => {
      if (wrapRef.current !== null && !wrapRef.current.contains(event.target as Node)) {
        setPanelOpen(false);
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick);
    };
  }, [panelOpen]);

  return (
    <div className="context-usage-wrap" ref={wrapRef}>
      <button
        id="context-usage-toggle"
        type="button"
        className="context-usage-button"
        aria-pressed={panelOpen}
        aria-label={tooltipLabel}
        disabled={!available}
        onClick={() => {
          setPanelOpen((previous) => !previous);
        }}
      >
        <svg viewBox="0 0 20 20" width="20" height="20" aria-hidden="true">
          <circle cx="10" cy="10" r={RING_RADIUS} className="context-usage-track" strokeWidth="2.4" fill="none" />
          {available && (
            <circle
              cx="10"
              cy="10"
              r={RING_RADIUS}
              className={`context-usage-fill context-usage-fill--${fillLevel}`}
              strokeWidth="2.4"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={RING_CIRCUMFERENCE}
              strokeDashoffset={dashOffset}
              transform="rotate(-90 10 10)"
            />
          )}
        </svg>
      </button>
      <div className="context-usage-popouts">
        <span className="context-usage-tooltip" role="tooltip">
          {tooltipLabel}
        </span>
        {panelOpen && usage !== null && (
          <div
            id="context-usage-panel"
            className="context-usage-panel"
            role="dialog"
            aria-label={translate(language, "contextUsagePanelLabel")}
          >
            <div className="context-usage-panel-headline">
              <span>{translate(language, "contextUsagePanelLabel")}</span>
              <span className="context-usage-panel-percent">{percentLabel}</span>
            </div>
            <dl className="context-usage-breakdown">
              <div>
                <dt>{translate(language, "contextUsageHistoryLabel")}</dt>
                <dd>{usage.breakdown.conversation_history_tokens.toLocaleString()}</dd>
              </div>
              <div>
                <dt>{translate(language, "contextUsageSystemPromptLabel")}</dt>
                <dd>{usage.breakdown.system_prompt_tokens.toLocaleString()}</dd>
              </div>
              <div>
                <dt>{translate(language, "contextUsageRagLabel")}</dt>
                <dd>{usage.breakdown.rag_context_tokens.toLocaleString()}</dd>
              </div>
              <div>
                <dt>{translate(language, "contextUsageFreeLabel")}</dt>
                <dd>{usage.breakdown.free_tokens.toLocaleString()}</dd>
              </div>
            </dl>
            <p className="context-usage-panel-total">
              {usage.total_tokens.toLocaleString()} / {usage.loaded_context_size.toLocaleString()} tokens
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
