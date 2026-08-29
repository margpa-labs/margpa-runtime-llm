# MARGPA Runtime LLM 未解決課題Registry Snapshot — 2026-08-29 16:40:49 JST

```yaml
document_id: current_unresolved_findings_registry_snapshot_20260829164049
document_type: shared_history_unresolved_findings_snapshot
document_state: frozen
language: ja
created_at: 2026-08-29 16:40:49 JST
source: ../../未解決/current_unresolved_findings_registry_ja.md
trigger: phase_6_user_mac_core_manual_acceptance_fail
authority_owner: Nazuna Research
```

## Snapshot Decision

2026-08-29 User Mac実画面Acceptanceにより、Phase 6は`FAIL／ADJUST`へ再分類した。

| ID | Status | Priority | Closure |
|---|---|---:|---|
| UF-P6-001 | R26解決、Manual上の新規反証なし | resolved | 非Block |
| UF-P6-002 | Selene／Qwen3Guard Active none。False Authority固定を確認 | P0 | Block |
| UF-P6-003 | Semantic 109全件Deferred、evaluated 0 | P0 | Block |
| UF-P6-004 | Judge／Repair Golden Path 0、Safe Fallbackのみ | P0 | Block |
| UF-P6-005 | User Manual Gate FAIL | P0 | Block |
| UF-P6-006〜010 | 解決済みまたは延期可能 | P1〜P3 | 非Block |
| UF-UI-001 | Sidebar、Guard表示、Failure表示、Recording Label等 | P2、一部最終差分へ前倒し | 原則非Block |
| UF-UI-002 | Context／Token／Hardware Profile | P2 | 非Block |
| UF-UI-003 | ENFORCE Progressive Presentation | P2 | 非Block |
| UF-UI-004 | Raw HTML／Markdown Presentation | P2 | 非Block |

## Exact Manual Facts

```text
Dedicated Selene     : Configured / Active none / unavailable
Dedicated Qwen3Guard : Configured / Active none
Built-in Criteria    : selected 32 / evaluated 0 / not_applicable 32
Semantic Main        : selected 109 / deferred 109
Judge/Repair ENFORCE : unknown -> safe_fallback, Repair 0
Recording            : correlated and written
Stop                 : cancelled, no late records
Main Switch          : Qwen -> DeepSeek -> Qwen PASS
Conversation         : Reload / second tab / restart continuity PASS
```

## Source Diagnosis

- `src/margpa_runtime_llm/bootstrap/web_application.py`が`dedicated_model_authority_granted=False`を固定。
- `config/judge_templates/selene/manifest.json`は`verified_official_copy=false`。
- Built-in Deterministicは意味評価を実施せず、Budget内Criteriaを`not_applicable`へ分類する設計。
- Sidebarは`frontend/src/App.tsx`で`Context <loaded_context_size>`を意図的に追加しており、User指定と不一致。

## Active Decision

Phase 6はDedicated Model実起動、Semantic実評価、Judge／Repair Golden PathだけをP0 Reworkする。追加Hardening、Raw HTML、Context上限、Layout Polishは延期する。
