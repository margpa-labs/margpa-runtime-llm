# Phase 8 User Mac Final Four PASS／Restart State Follow-up — Unresolved Snapshot

```yaml
document_type: append_only_unresolved_snapshot
document_state: frozen_history
language: ja
recorded_at: 2026-08-31 20:39:48 JST
decision_authority: user
stable_registry: ../../未解決/current_unresolved_findings_registry_ja.md
```

## 1. Final Four

| Stable ID | User Decision |
|---|---|
| UF-P8-003 | PASS — Completion Gate=`completion` |
| UF-UI-011 | PASS — Chat切替後に過去Warningなし |
| UF-UI-012 | PASS — White／Darkの注意色をUser採用 |
| UF-UI-013 | PASS — New Demo Run Primary Button |

## 2. New Deferred Findings

| Stable ID | 内容 | Target | Closure |
|---|---|---|---|
| UF-P8-013 | Dev Agent CapabilityがRestart後もON | Phase 9／10 | Non-blocking |
| UF-P8-014 | Per-purpose ConsentがRestart後もON／Default Policy曖昧 | Phase 10 | Non-blocking |
| UF-UI-016 | English Retention Fact本文が日本語 | Phase 10 | Non-blocking |

## 3. Controller Correction

Untrusted Labelを`--citation-text`へ変えるController追加Handoffは、Userの実画面AcceptanceによりSuperseded／Not Authorized。
P8-MR9の`--gauge-warn`表示をCurrent Accepted Baselineとする。
