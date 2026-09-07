# Phase 9-1 — 実Gemma 32 Criterion Rejudge Evidence分離 Exact Handoff

```yaml
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-05 08:25:39 JST
language: ja
from: codex_controller
to: claude_designer_implementer
maximum_claim: P9_1_REAL_32_CRITERION_REJUDGE_EVIDENCE_REWORK_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. 受理済み事項

`LIVE_REPAIR_BUDGET.max_additional_tokens=2800`とFixture／Unitの32 Criterion成立は受理済み。2000へ戻さない。Repair 400、Rejudge 75／Criterion、32 Criterion、最大Call 2、Deadline／Context等も変更しない。

## 2. Rework

### A. 原因の分離

実機Testだけに最小Observabilityを追加し、実Generation Resultから次を失敗Assertより前に記録する。

- Rejudge Requestの`max_new_tokens`
- `finish_reason`、Prompt／Completion Token、Generation時間
- Raw Contentの文字数とSHA-512（全文をDocsへ複製しない）
- 同じRaw ContentをStrict Decoderへ1回通した`execution_state`、`failure_reason`、Recommendation
- Decode成功時のCriterion総数、pass／deviation／unknown数、期待32 IDのmissing／extra
- Strict Decoderが例外なら`JudgeDecodeError.reason`

Production Decoder／Contractは変更しない。Testが同一Raw Contentを診断目的で再Decodeするだけとする。

### B. 追加実機試験

Observability追加後、前回と同じMain Qwen Repair→Gemma Rejudge、実109 Corpusから通常選択した同一32 Criterion、Main context 16384／Gemma context 8192を**追加で正確に1回だけ**実行する。

- 成功時: Plan 2400、全32 ID、Decoder COMPLETED、Gemma Identity、改善採用をHard Assertする。
- 不成立時: Decoder FAILEDとCOMPLETED+UNKNOWNを区別し、実測値と理由を返す。同条件反復やその場のSource修復をしない。
- Artifact不足以外はSKIPしない。

### C. Unit境界補正

「2800を1 Token超過」のTestは、Candidate使用量400を維持し、局所`RepairBudget.max_additional_tokens=2799`で32×75=2400が1 Token不足になる形へ直す。Production Budgetは2800のまま。旧TestのCandidate 401条件をCurrent通常境界の証明として残さない。

### D. Claim訂正

旧Return／Recoveryは上書きせず、新規Correction／Returnで「`outcome=unknown`だけではDecoder FAILEDを断定できない」と訂正する。Source Commentの確定的な`Decode-scale limitation`表現も「原因未確定」へ最小訂正する。

## 3. 禁止事項

JSON Retry、Decoder緩和、Schema変更、Criterion削減、予算再変更、Batching、Selene、Frontend、Phase 9-2／9-3、Closure、Git変更は禁止。実機失敗を見て追加試行や即時修復へ進まない。

## 4. Verification／Return

該当Unit、対象Ruff、非Model Full Suite、Canonical Mypyを確認する。完全別観点のInternal Reviewを2回行う。ReturnとRecoveryは新規Pathで作り、Phase Index／Current Registryは編集せず、Controller Review待ちで停止する。

