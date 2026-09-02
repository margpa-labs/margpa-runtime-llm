# Phase 9-1 Copilot Terra Max Fresh Session Final Real Dedicated Rework Exact Handoff

```yaml
document_id: phase_9_copilot_terra_max_fresh_p9_1_final_real_dedicated_rework_exact_handoff_20260901113052
document_type: exact_fresh_session_designer_implementer_handoff
document_state: ready
language: ja
created_at: 2026-09-01T11:30:52+09:00
phase: phase_9
program: phase_9_1
provider: copilot
model: GPT-5.6 Terra
reasoning_effort: max
context_window: 400k
model_attribution_source: user_report
task_state: fresh
task_identity: p9_1_final_real_dedicated_rework_p9_codex_011_to_014
monthly_availability_at_entry: 57_percent_user_report
session_ai_credits_at_entry: 0_user_report
implementation_authority: true
real_local_artifact_authority: true
official_network_authority: false
real_browser_authority: false
git_authority: false
phase_9_1_closure_authority: false
phase_9_2_authority: false
maximum_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Task Identity

これは新規Copilot Sessionで行うPhase 9-1限定Reworkである。

Current Taskは次だけである。

```text
P9-CODEX-011
P9-CODEX-012
P9-CODEX-013
P9-CODEX-014
```

過去のPhase 8 Web Knowledge、CP8-01〜04、P8-A〜F、Phase 6 Rework、P9-CODEX-001〜010の完了済み部分をCurrent Taskとして自動再開しない。Provider Memory、旧TODO、旧会話要約、過去Taskの「続き」をCurrent Authorityとして使わない。

```text
Provider Memory != Current Task
Fresh Session != Permission to rediscover or restart old work
Acknowledgement != Execution Authority
```

## 2. Authorized Root／Canonical State

Authorized Project Root:

```text
/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm
```

Current Working TreeをCanonical Baselineとして受け入れる。Dirty Working Treeを理由にReset、Checkout、Rollback、作り直しを行わない。既存差分は複数Executor／Controllerの成立済み作業を含む。

次はAccepted Workとして保持し、理由なく再実装しない。

- P9-CODEX-001〜005。
- P9-CODEX-008／009。
- Candidate Load Cleanup／Rollback／DEGRADED。
- Lease Identity Registry／Exactly-once Release。
- Qwen3Guard内部Deadline／Tracked Worker／Late Publish 0。
- Selene Project-derived Template Digest／Project Contract Digest。
- numeric-string Confidence Strict Decode。
- P9-CODEX-006／007／010の有効な部分修正。

## 3. Mandatory Reading — 一度だけ

次をこの順で一度だけ読む。

1. Controller Finding Ledger:
   `docs/project/phases/phase_9/history/operations/phase_9_1_codex_controller_post_copilot_real_dedicated_independent_review_finding_ledger_ja_20260901112423.md`
   SHA-512:
   `f60be3b15e6d106f73692473370893a3c6b0e334c5a6e7fafad52d1dd3316547ddc89a107399f7b9f4f6a5d76c5042b72331330ab0ce188fb0c3f790285ada6d`
2. Binding Predecessor Handoffの§4〜14:
   `docs/project/phases/phase_9/handoffs/phase_9_copilot_p9_1_three_review_real_dedicated_completion_exact_handoff_ja_20260901034115.md`
   SHA-512:
   `82ee1b9d8330f6ade9b8650f3a3a43d52829dfa65e65066c7e1dc748966f5b3a74cfdd6e8059d52076116bbb21ec2d2b394ab6ca96a371bc1921e2d67254e757`
3. Current Phase Index:
   `docs/project/phases/phase_9/phase_index_ja.md`

全Docs Bootstrap、Phase 8 Docs再読、既知Handoffの反復読込をしない。Task Identity／Authority／Canonical Stateに変化がない限り、直前に確認した情報を再利用する。

## 4. Entry Receipt

最初のTool Callは、本Handoffと§3の二つのSHA-512確認に限定する。その後、一度だけ次を記録する。

```text
Task: Phase 9-1 Final Real Dedicated Rework
Model: GPT-5.6 Terra Max / 400k
Fresh Session: true
Current Findings: P9-CODEX-011〜014
Monthly Availability at Entry: 57% (User report)
Session AI Credits at Entry: 0 (User report)
Old Phase 8 Task Authority: expired
Git／Browser／Network／Phase 9-2 Authority: none
```

Entry Receiptを出した後、Routine Confirmationを求めずP9-CODEX-011から直ちに実装へ進む。

## 5. Authority

明示的に許可する。

- Project Root内Source／Test／Docs／ScriptのRead／Edit。
- Current Working Tree上のP9-CODEX-011〜014修正。
- Project内に既に登録済みのLocal Selene／Qwen3Guard ArtifactへのRead、Load、Inference、Drain、Unload。
- `--phase-6-dedicated-model-authority`相当の明示Authority ONを用いたLocal Smoke。
- localhostのProduction Application／API Compositionを使う非Browser検証。
- Focused／Integration／Full pytest、Mypy、Ruff、Format Check。
- Project Root内の再実行可能なReal Dedicated Acceptance Script作成。

次は許可しない。

- Network、Artifact Download、外部Search、第三者Mirror。
- Atla／Hugging Faceを含む外部Source Access。
- Real Browser／User画面操作の自己認定。
- Git Read／Write、Commit、Push、Branch操作。
- Backup、Phase 9-1 Closure、Phase 9-2／9-3開始。
- User runtime_dataの削除／Reset。
- Project Root外への新規File作成。
- Package Install／Runtime Upgrade。

Selene upstream Exact RevisionをNetworkなしで確定できない場合は、虚偽Revisionを埋めない。`unknown_network_prohibited`をExact Revision Fieldへ入れる現在形を、明示的なUnverified Basis Fieldへ分離して解消する。

## 6. Mandatory Continuation／No Useless Confirmation

次は停止理由ではない。

- Diffが大きい。
- Core Pipelineを触る。
- Testが失敗した。
- 修正可能なRegressionを検出した。
- Real Model Loadに時間がかかる。
- Independent Review前である。
- Minor Finding／非Blocking Incidentがある。
- Better Designを複数案から選ぶ必要がある。
- Contextに十分な情報があり、自分で安全に判断できる。
- Progress Reportを一度出した。

上記は、分析、修正、Test、Recoveryで処理し、自走を継続する。Userへ「進めてよいか」「この方式でよいか」「Testを実行してよいか」「Real Local ModelをLoadしてよいか」とRoutine Confirmationしない。本Handoffが必要Authorityを既に与えている。

```text
Risk Detection != Stop Authority
Large Diff != Stop
Pending Review != Stop
Uncertainty != User Interrupt
```

Userが「待て」「待機」「次の指示を待て」と明示した場合だけ、次のUser指示までRead／Search／Test／Edit／Model Loadを含むTool Callを0件にする。

## 7. P9-CODEX-011 — Reproducible Production Real Evidence

### 7.1 Project内Acceptance Script

`scripts/models/phase_9_1_real_dedicated_acceptance.py`を作成する。単なるComment付きHere-documentで済ませない。

Scriptは少なくとも次をCLI Optionで扱う。

- `--role selene|qwen3guard|all`
- Explicit Authority acknowledgement。
- Bounded timeout。
- Machine-readable JSON output。
- Exit 0／Non-zeroの正直な収束。

Script自身がProject Root外Artifact PathをLogへ平文露出する必要はないが、次をLosslessに出す。

- Provider ID。
- Model Definition Exact Revision。
- Artifact SHA-512。
- Manifest／Contract Digest。
- Preflight Stageと結果。
- Load result。
- Inference target／criterion count。
- Strict Decode result。
- Latency／Token Usage（取得可能な範囲を正直に表示）。
- Mode ON／Active State。
- Turn Evidence。
- OFF request。
- Active Turn Drain。
- Unload result。
- Final loaded process／worker state。

### 7.2 Production Composition

Direct Adapter Smokeだけで完了しない。既存Production Compositionを通し、少なくとも次を実証する。

```text
Explicit Authority ON
→ Provider Selection
→ Mode Activation
→ Production Role Lifecycle
→ Real Inference
→ Evidence Projection
→ Mode OFF
→ Drain
→ Real Unload
```

Production APIを直接呼ぶTest Client／Application Compositionは使用可。Real Browserは使わない。

### 7.3 Evidence Artifact

完全Command、Exit、JSON結果、実行日時をPhase 9 operations Evidenceへ保存する。Artifact／Manifest／Contract Identityを値付きで保持する。Returnの要約だけをEvidence正本にしない。

## 8. P9-CODEX-012 — External Cancellation／Preempt

Qwen3Guardの内部Deadlineは保持し、Turn-owned External Cancellationを追加する。

- Guardrail Hook ContractへCancellationを通す。
- Input／Context Source／Output Candidateの三経路で同じExternal Token Identityを使用する。
- Detector内部DeadlineとExternal Cancellationを合成し、どちらが先でも同じCallをCancelできるようにする。
- User Stopは実Guard CallをPreemptする。
- Mode OFFは新規Leaseを拒否し、Active Guard CallをCancel／Drainする。
- Server ShutdownはActive Guard CallをCancel／DrainしてからUnloadする。
- Timeout／Cancel後のLate ResultをEvidence／Actionへ採用しない。
- Lease ReleaseはExactly once。

必須Thread Regression:

1. User Stop mid-input-guard。
2. Mode OFF mid-context-source-guard。
3. Shutdown mid-output-candidate-guard。
4. External CancelとInternal DeadlineのRace。
5. Cancel後Late Complete。
6. Unload Exception時のTyped Degraded。

## 9. P9-CODEX-013 — Selene Bounded Semantic Contract

### 9.1 Actual Criterion Load

Real Evidenceを1 Criterionで終わらせない。Current Runtime既定の最大32 Selected Criterionを実Turn相当で処理し、Semantic-109の総和を証明する。

```text
Selected
= Evaluated／Pass／Deviation／Unknown

Applicable
= Selected + Deferred

Expected current baseline:
Selected up to 32
Remaining Deferred up to 77
Total up to 109
```

実Definitionsにより実数が変わる場合は、固定109を捏造せず、Compiler出力から導出したActual総和を記録する。

### 9.2 Budget Design

次のいずれかへ明示収束する。

- Bounded Batch。
- Criterion数／Prompt Token／Expected Output Tokenによる明示上限。
- Fitしない場合のTyped Fail-closed／Deferred。

一つのPromptへ無制限にCriterionを詰めず、固定`max_new_tokens=1000`で必ず足りると仮定しない。Prompt Token、Output Budget、Call Count、DeadlineをEvidence化する。

### 9.3 Selene Cancellation／Deadline

`SeleneSemanticEvaluator.evaluate()`から実`InferenceService.generate()`へTurn-owned Cancellationを渡す。Main-sharedだけでなくSelene分岐にもStage Deadlineを適用する。Timeout／User Stop／Mode OFF／Shutdown後のLate Resultを採用しない。

### 9.4 Provenance

Networkは使わない。Exact upstream revisionがProject内Evidenceから確定できない場合、次を分離する。

```text
official_copy_verified: false
official_upstream_revision: null
derived_contract_basis: official_family_reference_unverified
derived_from_upstream_revision: null
project_template_digest: exact
project_contract_digest: exact
```

`unknown_network_prohibited`をExact Revision値として受理しない。Project-derived Contractの実用性と公式Exact Copy Claimを分離する。

## 10. P9-CODEX-014 — Acceptance／Manual／Index Alignment

P9-CODEX-011〜013解消後に行う。

1. P9-ACC-001〜038をSource／Test／Real Evidenceから個別再導出。
2. 38行、Unique 38、Missing 0、Duplicate 0を機械検算。
3. P9-ACC-008／011を再現可能Real EvidenceからだけPASSへ昇格。
4. P9-ACC-037だけをReal Browser／User Manual Gateとして残す。
5. Corrected User Manualを、実起動Flag、Provider選択、Mode、Real Evidence、Semantic総和、Stop、OFF、Drain、Unloadの正順へ更新。
6. Phase Index、Recovery、Acceptance Addendum、Exact ReturnのCurrent Claimを一致させる。
7. Historical誤Claimは改変せずAppend-only CorrectionでSupersedeする。

## 11. Review規律

全実装後、観点変更二段階Internal Reviewを行う。

Cycle 1:

```text
Runtime／Negative Path／Cancellation／Concurrency／Resource Ownership
```

Cycle 2:

```text
Production Composition／Evidence Reproducibility／Acceptance Truthfulness／Operator Flow
```

同じTestを二度実行しただけで二段階ReviewとClaimしない。Cycleごとに検査質問と追加Findingを記録し、Critical／Major／MVP Blockerは同Session内で修正する。

## 12. Verification

最低限、次を実施する。

- P9-CODEX-011〜014 Focused Regression。
- Guard三経路のExternal Cancellation Thread Test。
- Selene 32 Criterion相当／Budget／Deadline Test。
- Runtime Model Lifecycle／Lease／Provider Selection Integration。
- Judge／Repair／Rejudge／Semantic Runtime Integration。
- Real Selene／Qwen3Guard Acceptance Script。
- Canonical Backend full pytest。
- `mypy src tests`。
- `ruff check`および`ruff format --check`。
- Frontend変更時だけFrontend test／typecheck／lint／build。

新Testは可能な範囲でRegression Guardを確認する。Test総数だけでCompleteをClaimしない。

## 13. Recovery／Resource Hard Stop

Package境界ごとにRecovery Indexを更新する。

Copilot Resource Hard Stopが近い場合、新しいWork Unitへ入らず、Current WUを安全に収束し、次を残す。

- COMPLETE／PARTIAL／INVALID。
- Exact Changed Paths。
- Exact Last Test／Result。
- Active Process／Loaded Model／Tracked Worker。
- Temporary Artifact。
- Exact Next Symbol／Test。
- Rollback禁止範囲。

Resource Hard Stopは正常なProvider Transitionであり、成立済みWorkをRollbackしない。Quota残量を確認するためだけにUserを呼ばない。UserがUIから終了後の残量／Creditsを報告する。

## 14. True Stop Conditions

次だけで停止する。

- Required Local Artifactが存在しない、またはRegistry Digest不一致。
- Project Root外の新Authorityが不可欠。
- Network／DownloadなしではCritical Blockerを解消できず、Honest Unverified設計にも収束できない。
- Canonical Working Treeが同一行で競合し、安全な統合が不可能。
- Provider Resource Hard Stop。
- User Manual／Real Browser Gate。
- Userの明示的な待機／停止命令。

Test失敗、実装難度、Blast Radius、Pending Review、修正可能なRegression、Minor Finding、通常の設計判断はTrue Stopではない。

## 15. Return Contract

Returnには次を含める。

- P9-CODEX-011〜014の個別Disposition。
- Accepted WorkをRollbackしていないこと。
- Source／Test／Script／DocsのExact Changed Paths。
- 再実行可能Real Selene Command／Evidence。
- 再実行可能Real Qwen3Guard Command／Evidence。
- Provider／Artifact／Manifest／Contract Digest。
- Semantic Criterion総和、Prompt／Output／Call Budget。
- User Stop／Mode OFF／Shutdown Thread Evidence。
- Acceptance 38件の最終内訳と機械検算。
- User Manual Gate残件。
- 二段階Internal Reviewの別観点と追加Finding。
- Full Validation結果。
- Active Process／Loaded Model／Temporary Artifact最終状態。
- Recovery IndexとExact Return Handoff。
- 経過時間。Quota／Session CreditsはUser報告待ちとし、推測しない。

最大Claimは次に限定する。

```text
P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

Return後はCodex Controller Independent Review待ちで停止する。Phase 9-1 Closure、Phase 9-2、Gitへ進まない。

## 16. First Action

本Handoff SHA-512と§3の二つのSHA-512を確認し、Entry Receiptを一度だけ残す。その後、P9-CODEX-011の再実行可能Acceptance ScriptとProduction Composition Boundaryの確定から実装を開始する。Routine Confirmationを挟まない。
