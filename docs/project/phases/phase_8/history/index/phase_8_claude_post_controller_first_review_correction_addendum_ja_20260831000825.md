# Phase 8 Claude Post-Controller First Review — Correction Addendum (Append-only)

```yaml
document_type: correction_addendum
phase: phase_8
package: P8-CR (P8-CR0-CR4)
provider: Claude
created_at: 2026-08-31 00:08 JST
addendum_kind: append_only_historical_correction
```

## 目的

Codex Controller第1回Independent Review（`phase_8_codex_controller_p8_a_through_p8_f_first_independent_review_ja_20260830234754.md`）が指摘したHistorical false claim／Traceability不整合を、既存のP8-D／P8-E Recovery文書を一切改変せずに訂正する。本文書はAppend-onlyであり、対象文書のいずれも書き換えていない。

## 訂正1 — AuthorizationEnvelope実配線に関するFalse Claim（P8-CODEX-002）

### 訂正対象の記述

`src/margpa_runtime_llm/modules/dev_agent/application/run_service.py`の`submit_approval()`内に存在した、次のComment（P8-D／P8-E時点のSource自身のコメント。Recovery文書ではなくSource内コメントだが、実装の実態と乖離した記述だったため、Controller Reviewが「Historical P8-D Recoveryのclaim」として問題視した内容と同一の主張である）：

> 「constructing this Envelope is the one place an `AuthorizationEnvelope` would be issued; it is scoped to exactly this `(run_id, step_id)` pair...」

### 実態との乖離

- `AuthorizationEnvelope`型は`contracts.py`に定義され単体Testも存在したが、`submit_approval()`は実際には`AuthorizationEnvelope`を一度も構築していなかった（`StepRecord.approved: bool`を立てるのみ）。
- Source Search上、実行Path内に存在したのは上記commentだけであり、「would be issued」という将来形の記述が、恰も実装済みであるかのように読めるProse表現になっていた。

### 訂正内容

P8-CR2にて、`AuthorizationEnvelope`を`start_run()`内で実際に構築しRun Snapshotへ永続化するよう実装した。上記commentは`run_service.py`から削除され、正しい実装（`_issue_envelope()`、`advance()`内の`_envelope_violation()`照合）へ置き換わっている。詳細は本Package（P8-CR）自身の`phase_8_claude_post_controller_first_review_traceability_addendum_ja_20260831000825.md`を参照。

### 対象文書への処置

- `phase_8_claude_p8_d_complete_package_recovery_ja_20260830225641.md`：**改変しない**（Historical Immutability）。同文書がこの実態と異なる記述を含んでいた場合、それはP8-D時点の誠実な設計意図の記録として保持し、本Addendumが「その後Controller Reviewで実配線不備と判定され、P8-CR2で是正された」という事実を追記する形で補う。
- 今後この事実を参照する場合は、P8-D Recovery単体ではなく本Addendumおよび`phase_8_claude_p8_a_through_p8_f_exact_return_handoff_ja_20260830233316.md`§6（開示済みIncident）と併せて読むこと。

## 訂正2 — Acceptance集計の不整合（P8-CODEX-003）

### 訂正対象の記述

- `phase_8_claude_p8_f_complete_package_recovery_ja_20260830233316.md`：「40件中38件PASS、2件PARTIAL」という要約文と、本文中の「PARTIAL 2件の内容」節が、実際に列挙されたPARTIAL項目がP8-ACC-038の1件のみであるにもかかわらず「2件」という数字を用いていた。
- `phase_8_claude_p8_f_requirement_acceptance_source_test_traceability_ja_20260830233316.md`：一部箇所で「39 PASS / 1 PARTIAL」という異なる集計が併記されていた。
- いずれの箇所でも、Real MCP／Real ModelをAcceptance項目の1件として数える記述と、Scope外／NOT RUN Boundaryとして扱う記述が混在していた。

### 訂正内容

Rework後（P8-CR2完了後）のCandidate集計を次に統一する。

```text
PASS             38
PARTIAL           1  # P8-ACC-038（GD相関、Real LLM/Tool Execution段階まで正直にPARTIAL据え置き）
USER MANUAL GATE  1  # P8-ACC-040（User実画面確認が必須。Claude Browser実演はCandidate Evidenceであり代替不可）
TOTAL             40
```

Real MCP／Real Modelは、Acceptance Matrix 40項目のいずれの1件としても数えない。両者は「Authority不足によりNOT RUN」というScope外Boundaryであり、Fixture PASSでも実接続PASSでもない、実接続自体が試みられていない状態として別記する。

### 対象文書への処置

- `phase_8_claude_p8_f_complete_package_recovery_ja_20260830233316.md`・`phase_8_claude_p8_f_requirement_acceptance_source_test_traceability_ja_20260830233316.md`：**改変しない**（Historical Immutability）。
- 正本の最新集計は本Package（P8-CR）の`phase_8_claude_post_controller_first_review_traceability_addendum_ja_20260831000825.md`および`phase_8_claude_post_controller_first_review_bounded_rework_exact_return_handoff_ja_*.md`（本Package完了時作成）を参照すること。両文書が今後この集計についての正本となる。

## 訂正3 — Claude localhost Browser EvidenceのClaim範囲（Controller Review §4に基づく明確化）

### 訂正対象の記述

P8-F完了時点のExact Return Handoffおよび関連Recovery文書は、Claude Browserによる`localhost:8000`実演を「P8-ACC-040 PASS」の根拠として扱う書き方をしていた。

### 訂正内容

Claude Browserによるlocalhost確認は、**Automated Candidate Evidence**として有用であり、UIが実際に動作することの強い状況証拠にはなるが、**User Manual Acceptance（P8-ACC-040）そのものを代行しない**。P8-ACC-040は`phase_8_claude_p8_f_user_manual_test_sheet_ja_20260830233316.md`に従いUser（Human Reviewer）が実際に手を動かして確認するまでUSER MANUAL GATEのまま据え置く。上記「訂正2」の統一集計はこの区別を反映している。

なお、Real Browser使用自体の是非（明示的禁止下での使用というProcess Nonconformance）は、Controller Reviewが既に「Disposition: RECORDED / NON-BLOCKING」として記録済みであり、本Rework（P8-CR）はこれを再調査しない。`/tmp`一時ファイル使用の件も同様にController Review記録済み・Non-blockingとして参照するのみとする。

## 訂正4 — Constitution Rule ProseのStale記述

`constitution/rules/external-write-requires-human-gate.md`の「Existing Enforcement」節が「Harnessはまだ存在しない」というP8-D以前の時点記述のまま残っていた。P8-CR3にて、Fake／Deterministic Harnessが現に存在し`write_note`のExternal Write GateをApproval Profile経由で構造的に満たしていること、Real Toolは依然未接続であること、Constitution Resolver自身によるRule実行（`unsupported_action`）は変わらず未実装であることを正直に反映するよう本文を更新した（Digestは`ConstitutionRule`のMetadataから計算されるため、この本文更新はManifestのDigest不一致を発生させない — `test_json_file_provider.py`等の既存Testで確認済み）。

## 本Addendumが変更していないもの

- P8-A〜P8-Fの実装成果物（Behavior面）そのもの。本Addendumは記述の訂正のみを扱う。
- `phase_8_claude_p8_a_through_p8_d_e_f_*`系の既存Recovery／Handoff文書のいずれの本文も未改変。
