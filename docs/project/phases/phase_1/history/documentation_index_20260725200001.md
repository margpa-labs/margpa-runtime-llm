# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725192903.md`

## 1. Current Position

```text
Public Author／Research Name                 : Nazuna Research
Phase 1-G                                    : Complete／Accepted
Phase 1-H                                    : Complete／Accepted
Mac Web User Acceptance                      : Passed with Follow-up Items
Phase 1-I Web Presentation／UX Follow-up      : Accepted／Ready for Implementation
Combined Manual Edge Tests                   : Deferred until Phase 1-I Review
Phase 1-F Lightning Repository／Preflight     : Accepted
Phase 1-F Lightning Pure CPU Repository Hook : Accepted／Ready for Implementation
Phase 1-F Lightning Native                   : Pending
Top-level Phase 1 Completion                 : Not Declared
Phase 1-ex                                   : Accepted Reservation／Not Started
Project Documentation Explainer／Simple RAG  : After Phase 1-ex
Mac Simple RAG                               : Optional Local Implementation
Lightning Simple RAG                         : Hook Only／Default OFF
Public Roadmap                               : Updated／Current
Docs Writer until Phase 1-ex Complete        : Current Designer Task Only
Initial GitHub Publication                   : Deferred until Phase 1-ex Completion
Git                                          : Not Initialized
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725192903.md](documentation_index_20260725192903.md)を継承し、次を正式な設計状態として追加する。

- Phase 1-I Web Presentation and UX Follow-up
- Thinking GenerationとThinking VisibilityのWeb上の分離
- Reasoning／Final SSE Channel
- Shortcut HintとIME Guard
- Canonical Message Copy
- Completion後のSanitized Markdown
- Phase 1-I Review後のManual Edge Test一括実施
- Lightning Linux x86_64 Pure CPU Repository Hook
- Mac LocalとLightningで異なるSimple RAG Activation Policy

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 4. Source Review

[designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)

## 5. Phase 1-I Requirements／Architecture／ADR

- [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- [phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md](architecture/phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md)
- [adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md](adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md)

## 6. Phase 1-I Implementer Handoff

[designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md](handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md)

実装Scope：

```text
Thinking Generation／Visibility UI
Reasoning／Final SSE Channel
Localized Shortcut Hint
IME Composition Guard
User／Assistant Canonical Copy
Streaming Plain Text
Completion後Sanitized Markdown
Security／Regression Test
```

Manual Edge Testは実装担当の自動Testで代替しない。実装報告と設計Review後、ユーザーが次をまとめて確認する。

- 生成中New Chat
- Summary中Stop
- Browser Reload
- 別Tab Busy
- Token Boundary
- Thinking 4組合せ
- Markdown Sanitization／Fallback
- Copy対象
- Shortcut Hint

## 7. Lightning Pure CPU Requirements／Architecture／ADR

- [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- [phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md](architecture/phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md)
- [adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md](adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md)

## 8. Lightning Pure CPU Implementer Handoff

[designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)

Repository Scope：

```text
Pure CPU Deployment Profile
Pure CPU llama.cpp Build Contract
CPU Setup／Preflight Hook
Verification Target
Static／Unit／Integration Test
External Native Test Pending State
```

既存のCUDA BuildをCPUで実行するProfileは削除・改名せず、Pure CPU Build Profileと意味を分けて併存させる。

## 9. Simple RAG Placement

Simple RAG／Project Documentation ExplainerはPhase 1-IまたはPure CPU Handoffの実装対象ではない。

Phase 1-exで公開正本CorpusとManifestを整えた後、別Handoffで扱う。

```text
Mac Local:
  Optional implementation
  Explicit ON only
  Corpus／Retriever／Context Injectionを接続可能

Lightning:
  Hook only
  Default OFF
  Provider absent allowed
  No index load
  No retrieval
  No additional model call
```

この差はApplication Coreの分岐Hard-codeではなく、同じComponent Port、CapabilityおよびDeployment Profileで表現する。

## 10. Scoped Authorization

ユーザーの指示により、次のRepository実装へ着手可能である。

1. Phase 1-I Web Presentation and UX Follow-up
2. Phase 1-F Lightning Pure CPU Runtime Follow-up

両Scopeは別々に実装・報告・Reviewする。単一Statusへ混在させない。

次は自動許可しない。

- 外部Lightning Studio操作
- Upload／公開URL操作
- Dependencyの外部環境Install
- Model Download
- Simple RAG実装
- Phase 1-ex開始
- Phase 1完了宣言
- Backup
- Git／GitHub操作

## 11. Recommended Execution Order

```text
Phase 1-I Implementation
  → Implementer Status
  → Designer Review
  → Lightning Pure CPU Repository Follow-up
  → Implementer Status
  → Designer Review
  → Combined Mac Manual Edge Test
  → External Native Validation when available
  → Phase 1 Completion Decision
  → Backup
  → Phase 1-ex
  → Public Canonical Corpus
  → Mac Simple RAG／Lightning Hook-only Handoff
```

Phase 1-IとPure CPU Repository Follow-upの実装順を変更する場合も、変更範囲、TestおよびStatus Reportは分離する。

## 12. Next Required Reports

```text
docs/handoffs/implementer_status_phase_1i_*_YYYYMMDDHHMMSS.md
docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_YYYYMMDDHHMMSS.md
```

## 13. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。
