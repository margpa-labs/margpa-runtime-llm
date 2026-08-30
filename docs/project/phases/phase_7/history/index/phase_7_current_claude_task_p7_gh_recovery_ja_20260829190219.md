# Phase 7 Current Claude Task — Package P7-G/H Recovery（Data Controls／Integration・Observability・Regression）

```yaml
document_id: phase_7_current_claude_task_p7_gh_recovery_20260829190219
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 19:02:19 JST
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
package: P7-G, P7-H
```

## 0. Recovery Index Pointer

前Package: [P7-E/F Recovery](phase_7_current_claude_task_p7_ef_recovery_ja_20260829184625.md)。次Package: P7-I（User Manual Candidate／Complete Candidate、Exact Return Handoff）。

## 1. P7-G 実装（Data Controls、`modules/data_controls/`）

### 1.1 設計判断：Retention Fact（読取専用）とConsent（変更可能）の分離

本Codebaseには元々TTL／自動削除機構、Feedback収集機構、Synthetic Data生成機構、Training Pipelineのいずれも存在しない。これを踏まえ、Data Controlsを以下2種へ厳密分離した。

```text
Retention Fact（読取専用、Static）：Chat／Local RAG Evidence／Web Evidence／Human Feedback／
  Synthetic Generatedの各Source Classについて、現在の実挙動（保存有無・理由）を機械的に正直に
  記述する。存在しない機構について「設定可能」を装わない。
Consent（変更可能、永続化）：External Query Transmission／Feedback Research Use／
  Synthetic Data Use／Future Training Exportの4項目。全てDefault OFF（P7-REQ-019）。
  保存はConsent Preferenceの記録に過ぎず、Training実施を意味しない（P7-REQ-021、
  Test `test_saving_consent_never_claims_training_occurred`で直接検証）。
```

### 1.2 実装

`JsonFileDataControlConsentStore`：`JsonFileLocalCorpusRegistry`と同水準のSymlink拒否・
Owner-only Permission・Atomic Write・Fail-closed Corrupt検出。`/api/v2/data-controls/policy`
(GET)、`/consent`(PUT、部分更新)、`/reset`(POST、既定値へ復元)。`--phase-7-data-controls`
CLI Flag（Loopback-only Gate、既存Patternと同一）。

Frontend：`SettingsModal.tsx`のCategoryを`"basic" | "advanced" | "data_controls"`の3種へ拡張し、
「データコントロール」を独立Top-level Tabとして追加（Architecture §5の「設定／データ
コントロール」という2領域構造に対応、Advanced Mode配下への従属ではない）。全Consent Toggle
既定OFF、Retention Factは編集不可の説明Listとして表示。

## 2. P7-H 実装（Integration／Observability／Regression）

### 2.1 Request ID相関

Web Search Orchestrator（`WebKnowledgeService.search_and_fetch()`）の`WebSearchAndFetchResult`へ
`request_id`を必須Fieldとして追加し、`SEARCH_DISABLED`等の早期Failure Pathを含む全Return文で
Stamp する（従来は`search_run`（`None`になり得る）内にのみ存在し、Search自体が実行されない
Failure Caseでは相関Keyが失われていた）。`/api/v2/web-search/search`のResponseへ
`request_id`を投影し、Client側はEvidence／Failureの両方を同一Request IDで参照できる。

Local Corpus Citationは既存Phase 2 Citation機構（`DocumentationEvidence.query_digest`等）を
無変更で再利用しているため、独自のRequest ID相関追加は不要（既存機構がそのまま適用される）。

### 2.2 Regression確認（Conversation／Citation／Branch／Regenerate／Recording／Stop）

`conversation_generation.py`、`persistent_contracts.py`、`sqlite_conversation_store.py`は
本Phase全体を通じて一切変更していない（P7-0 Recovery §3の設計方針通り、Local Corpusは
既存Pipelineへの合成、Web Search／Data Controlsは完全に独立した新規機能として実装したため）。

```text
tests/unit/conversation + tests/integration/conversation +
  tests/integration/web/test_persistent_web_app.py ... 277 passed（隔離実行で確認）
Citation／Branch／Regenerate／Recording／Stop関連Test（Keyword一致） ... 179件、
  Full Suite内で全件PASS
```

### 2.3 Failure Language／Reason正直性

Web Search：`failure_reason`（`search_disabled`／`search_provider_unavailable`／
`no_relevant_evidence`等）、Evidence単位の`rejected`／`rejection_reason`を常時投影。
Local Corpus：既存`documentation_*`Warning Code機構をそのまま利用。虚偽成功への変換は
行っていない（Architecture §3 Invariant 10、既存Test群で保証）。

## 3. Focused Evidence

```text
tests/unit/data_controls/test_json_file_consent_store.py ... 7 passed
tests/integration/web/test_data_controls_web_app.py ... 7 passed
frontend: DataControlsPanel.test.tsx ... 5 passed
frontend: SettingsModal.test.tsx ... +2 passed（Data Controls Tab Gating）
```

新規Backend Test Node ID: 7+7 = 14。新規Frontend Test: 5+2 = 7（249→256）。

## 4. Canonical Evidence

```text
Backend pytest（Full Suite） : 1912 passed, 7 deselected（Baseline 1898 + 14新規 = 1912、一致確認済み）
mypy（Project既定）          : Success、524 source files
ruff check . / format --check .: All checks passed／All formatted
frontend: typecheck／lint    : Clean
frontend: npm test           : 256 passed（28 files）
frontend: npm run build      : Clean（90ms）。data-controls-bootstrap Marker、Build出力へ反映確認済み。
tests/integration/web（全体） : 195 passed（Local Corpus／Web Search／Data Controls／既存Feature
  全Web App Integration Testを一括実行、相互干渉なし）
```

## 5. Requirement／Acceptance対応（暫定、最終集計はP7-I）

```text
P7-REQ-016〜021: 実装・Test済み。
P7-ACC-025（Source／Retention／Export／Delete／External Transmission／Purpose Consent分離）:
  PASS（Retention Fact読取専用APIとConsent変更可能APIを構造的に分離）。
P7-ACC-026（Feedback／Synthetic／Future Training既定OFF）: PASS（機械Test確認済み）。
P7-ACC-027（保存をTraining完了と表示しない）: PASS（Test `test_saving_consent_never_...`）。
P7-ACC-028（Failure Reason／Stage／Provider／Request ID正直表示）: PASS（Web Search
  request_id相関追加により強化）。
P7-ACC-029（Conversation／Branch／Recording／Stopに重大Regressionがない）: PASS
  （277＋179件の隔離・全体Test確認）。
```

## 6. Known Findings／Deferrals

```text
P2: 「Export」はData Controls自体のPolicy JSON取得（GET /policy）に留まり、Conversation全体や
  Local Corpus全体を含む横断的な「全データExport」機能は未実装（Scope外、Phase 9/10候補）。
P2: 「Delete」はConsent RecordのReset（既定値復帰）のみ。Conversation／Local Corpus実データの
  一括消去Actionは未実装（実装するとDestructive Actionの検証コストが大きく、本Task Resource
  内では見送った）。
```

## 7. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Package P7-I（User Manual Candidate／Complete Candidate、Internal Review、
Exact Return Handoff作成）へ継続。
