# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 19:29:03 JST`
- 更新日時: `2026-07-25 19:29:03 JST`
- Snapshot: `20260725192903`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725164739.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Complete／Accepted
Phase 1-H                                : Complete／Accepted
Mac Web User Test                        : Passed with Follow-up Findings
Top-level Phase 1 User Acceptance        : Not Yet Declared
Phase 1-F Lightning Native               : Pending
Lightning Pure CPU Runtime               : Follow-up Reserved
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Markdown Presentation                    : Phase 4 Candidate
Message Copy                             : Follow-up Candidate
Thinking UI State                        : Follow-up Required
Public Roadmap                           : Updated／Current
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-ex Docs Policy、Public Documentation Corpus、Project Documentation Explainer、Full RAG境界およびLLM動作検証／評価設計は、[documentation_index_20260725164739.md](documentation_index_20260725164739.md)から継承する。

本Snapshotは、2026-07-25 Mac Web User Test、Thinking Visibility Root Cause、Markdown／Copy／Shortcut Follow-up、およびLightning Pure CPU Runtime要件を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 4. Detailed Review

[designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)

## 5. Mac Web User Test

```text
Visual Composition                    : PASS
Ephemeral Multi-turn                 : PASS
New Chat／Browser Memory Reset       : PASS
Model Reload Separation              : PASS
Send Button                          : PASS
Stop Button                          : PASS
Ctrl+Enter Send                      : PASS
Token Limit Behavior                 : PASS
UI Language Switch                   : PASS
Response Language Switch             : PASS
Summary Mode                         : PASS
Thinking Presentation               : UX FOLLOW-UP
Markdown Presentation                : NOT IMPLEMENTED
User／Assistant Copy                 : NOT IMPLEMENTED
```

Visual Evidenceとして、2026-07-25 19:12のMac Screenshot 2件を視認した。Screenshot自体はRepository Artifactではなく、Absolute Local Pathは記録しない。

## 6. Screen Composition Assessment

Phase 1 Previewとして想定どおりである。

- Branding／Runtime Identity
- UI Language
- New Chat
- Preview Notice
- Message Timeline
- Composer
- Stop／Send
- Response Language
- Max New Tokens
- Thinking Visibility
- Summary Mode

History、Account、Full Settings、Governance Status等は後続Phaseの責務であり、Phase 1不足とは扱わない。

## 7. Thinking Visibility Root Cause

Current Default：

```text
Thinking Generation : disabled
Presentation        : visible when Checkbox is ON
Generated Think     : none
Displayed Think     : none
```

Web UIは`thinking_visibility`だけを送信し、`thinking_mode`を変更しない。表示対象が生成されないため、CheckboxをONにしても何も出ない。

Core Failureとは断定しないが、UI上は誤解しやすいため、GenerationとVisibilityの分離状態を明示するFollow-upが必要である。

## 8. UI Follow-up

### Shortcut Hint

Current実装は`Cmd+Enter`／`Ctrl+Enter`送信へ対応している。Composer付近へ実際のShortcutを表示する。

### Markdown

Current Plain Text表示は`innerHTML`を禁止し、`textContent`を使うPhase 1の安全側実装である。

Markdown化にはSanitizer、危険URL拒否、Raw HTML無効化、Streaming中の不完全構文処理およびCanonical Content分離を必要とする。Default配置はPhase 4候補とする。

### Copy

User／Assistant MessageへCopy Buttonを追加する。Canonical ContentをCopyし、Hidden Thinking、Metadata、非表示Original Summaryを混入させない。

## 9. Lightning Pure CPU

既存CPU Profileは`compute_kind_key = "cpu"`かつ`gpu_layers = 0`だが、`build_variant_key = "cuda"`である。

Freshな最小CPU環境向けに、GPU、NVIDIA Driver、CUDA Toolkitおよび`nvcc`を要求しないPure CPU Profile／Build／Setup／Acceptanceを分離する。

候補：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

## 10. Priority

```text
P0 : Thinking Generation／Visibility UI整合
P1 : Shortcut Hint／Message Copy／Lightning Pure CPU
P2 : Sanitized Markdown Presentation
```

## 11. Scoped Authorization

本更新はReview、要件予約、Roadmap更新および最新Index作成だけを対象とする。

次を自動許可しない。

- UI／Thinking／Copy／Markdown実装
- Pure CPU Profile／Script実装
- Dependency Installation
- Model Download
- 外部環境操作
- Phase 1完了宣言
- Git／GitHub操作

## 12. Next Gate

```text
Mac Web Test Reviewed
  → Follow-up Scope Decision
  → Required Follow-up Implementation／Review
  → Mac Final User Acceptance
  → External CPU Native Validation when Available
  → Phase 1 Completion Decision
  → Backup
  → Phase 1-ex
```

## 13. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
