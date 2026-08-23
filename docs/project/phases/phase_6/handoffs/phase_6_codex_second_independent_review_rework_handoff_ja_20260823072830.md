# Phase 6 Codex Second Independent Review Rework Handoff

```yaml
document_id: phase_6_codex_second_independent_review_rework_handoff_20260823072830
status: adjust_required
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役
created_at: 2026-08-23 07:28:30 JST
source_candidate: phase_6_claude_rework_complete_candidate_handoff_ja.md
closure_state: do_not_close
human_decision_required_before_rework: false
```

## 1. Decision

`phase_6_claude_rework_complete_candidate_handoff_ja.md`は受理しない。

同Candidate自身が次を申告している。

- P6-CODEX-002、006、007が`PARTIAL`。
- P6-ACC-022、028〜034が`NOT_EXECUTED`。
- P6-ACC-008、011、021、027、058、069、071等に未充足またはEvidence不足がある。
- Repair実Attempt、Calibration／Bias Matrix、Qwen Mode比較、複数UI Acceptanceが未実施。
- Open Major Findingが未解消のまま存在する。

前回HandoffのReturn Contractは、Open Major Finding 0かつ全必須Acceptanceが`PASS`または
契約上正当な`SAFE_UNSUPPORTED`になるまで`COMPLETE_CANDIDATE`を宣言しない、と定めた。
`Rework Complete Candidate`という別名へ変更しても、このGateは回避できない。

今回列挙する残作業はFrozen Phase 6 Scope内である。Controller側へ返す判断事項ではなく、
Claude側設計統括者役が設計、Task分解、実装、再Reviewまで自律的に完了させる対象である。
実装不能な真のBlockerが発生した場合だけ、`BLOCKED`として事実を返すこと。

DeepSeekの現行Toolchain Safe Unsupportedは引き続き許容する。本Reworkで新規Network、
Homebrew変更、Model Artifact操作は行わない。

## 2. Independent Validation

```text
Backend Full:
  TMPDIR="$PWD/.venv/.t" ./.venv/bin/python -m pytest \
    -p no:cacheprovider --basetemp=.venv/.t/r2
  1434 passed, 5 deselected in 64.65s

Ruff:
  PASS

Mypy:
  PASS — 430 source files

Frontend:
  typecheck PASS
  lint PASS
  23 files / 191 tests PASS
  build PASS
```

Regression TestはPASSしている。ただし、以下のMajor Findingは現行Testが対象にしていないか、
Candidate自身が未実装を明記しているため、Test PASSをClosure根拠にはできない。

## 3. Major Findings

### P6-CODEX-009 — Repair Coreが未実装

`resolve_repair_eligibility()`を呼ぶだけで、P6-E-WU-003／006および
P6-ACC-028〜034を満たしたことにはならない。

現状は次が存在しない。

- 新しいRepair Generation Attempt。
- OriginalとRepair Attemptの別Identity。
- Phase 4 Main Governance全Point再通過。
- Phase 5 Guardrail全Point再通過。
- Rejudge。
- Before／After同Criteria比較。
- Improvedの場合だけのPresented Answer選択。
- Attempt／Depth／Call／Token／Wall Time／Cancelの実行時Budget。
- Persistent Commit-before-completed、Terminal一意、Ghost Completion 0。
- Retry／Regenerate／Branch／Citationとの実統合。

判定：`CRITICAL／REQUIRED`。

### P6-CODEX-010 — Detached Judge ThreadがRuntimeを競合させる

現行`build_judge_completion_hook()`は、各Turn完了時に所有・追跡されないDaemon Threadを
生成し、Main Modelと同じ`InferenceService`を非同期利用する。

CandidateおよびSource自身が、Judge実行中の次Turnが`model_busy`になり得ることを認めている。
出力上限を200へ縮小しても競合は解消されない。また、次の問題が残る。

- Runtime shutdown時にJudge ThreadをCancel／Joinせず、Model closeと競合し得る。
- Judge呼出例外時にTyped Failure Resultを記録せず、過去`last_result`が残る。
- Hook開始時と完了時でModeをFreezeせず、実行中のMode変更が同じRunのRepair Eligibility／
  Recording動作を変え得る。
- BudgetのWall TimeはBlocking Model Callを中断できない。
- `last_result`がProcess-global latestだけで、Current Requestのpending／running／failedを表現しない。
- Internal JudgeがUser Main Generationを失敗させる可能性があるため、OBSERVEでCanonical Behavior
  不変というP6-ACC-017も成立しない。

判定：`CRITICAL／REQUIRED`。

### P6-CODEX-011 — RecordingがJudgeに結合し、Writer境界も不十分

Recordingは`_run_judge()`の末尾からしか呼ばれない。このためRecording FULL／METADATAでも
Judge OFFなら記録0となり、ADR-6-013のMode直交性に違反する。

Writerにも次の問題がある。

- `request_id`を無検証でFile名へ連結するため、`/`、`..`、Absolute Path等でBase Directory外へ
  解決可能。
- `base_dir`のSymlink／Non-regular／Containmentを検証しない。
- Judge CallごとにWriterを新規生成するため、LockがWriter Instance間で共有されず、Quota計算と
  Writeが競合可能。
- 各Writerが他Writerの生存中TemporaryをOrphanと誤認して削除し得る。
- 同一request_idの置換時、既存Target Sizeを差し引かずQuotaを二重計上する。
- File／Directory `fsync`を行わず、Atomic RenameだけをDurable Atomic Writeと扱う。
- Quota／Write Failureを`_record_evidence()`で無言に捨て、degraded／fail-closedを投影しない。
- Judge Run EvidenceにModel／Artifact／Backend、Prompt／Rubric／Config Digest、Token、Latency、
  Call／Cost等の必須Traceが不足する。

判定：`CRITICAL／REQUIRED`。

### P6-CODEX-012 — Runtime Status／Judge UIが未接続

Frozen P6-OBS-004は`idle→preparing→guarding→generating→judging→repairing→rejudging→...`
を要求する。現行Chat UIはJudge／Repair Stateへ遷移せず、JudgeはCompleted後の背景処理になる。

Backend `judge.last_result`もFrontend型`FeatureModeSnapshot`へ含まれず、
`FeatureModesPanel.tsx`はResultを表示しない。Current RequestのJudge／Repair／Recording状態、
Failure、Budget、Degradedを利用者が観測できない。

判定：`MAJOR／REQUIRED`。

### P6-CODEX-013 — Generation Attempt Provenance未保存

P6-MDL-005／P6-ACC-008は、各Generation AttemptへRole、Model、Artifact Digest、Backend、
Context Size、Generation Configを関連付けることを要求する。

現行`ConversationTurn`は`request_id`だけを持ち、Model／Artifact／Backend／Context／Configを
保持しない。Candidateの「request_id相関、PersistentTurnResponse投影でPASS」はEvidenceとして
成立しない。

Judge ResultについてもP6-LJG-002のModel／Artifact、Prompt／Rubric Digest、Criteria、Seed、
Config、Evidence Scope、Latency、Token、Call、CostをLive永続Evidenceへ結合していない。

判定：`MAJOR／REQUIRED`。

### P6-CODEX-014 — Component Identity Stateが実Bindingを完全には表さない

`Current Governance Layer`は`app.state.governance_definitions_runtime`からだけ導出される。
Phase 4 Runtime GovernanceがDefinitionsを実Bindingしていても、Phase 3 Runtime Flagが無効なら
`None`になり得る。Current Identityは実際にMain GovernanceへBindingされたManifest／Digest／
Planから導出すること。

また、`project_governance_layer_identity()`は`package_id`があればDigest欠落でも`ACTIVE`にする。
Frozen State MatrixのNone／Unavailable／Invalid／Loading／Degraded／Activeを実装・検証していない。
P6-ACC-024AをGuard／Governance NoneのEvidenceでPASS扱いした点も、同Acceptanceが
「Selene候補未Load時のJudge Current／Available捏造0」を対象とするため根拠が異なる。

判定：`MAJOR／REQUIRED`。

### P6-CODEX-015 — Safe RefusalのRaw CodeがStatus欄に残る

Chat Bubble本文は固定拒否文へ変換されたが、`App.tsx`のError処理は引き続き
`setStatusKey("errorStatus", {code: data.code})`を呼ぶため、通常UIのStatus欄に
`Error: guardrail_reject_input`を表示する。

さらに、`isSafetyRejectCode()`を定義した一方、`knownMessageText()`／
`translatedServerMessage()`は未知の`guardrail_*`／`governance_*` CodeへPrefix判定を使わない。
新しいReason Codeで固定Safe Refusalから外れ得る。

判定：`MAJOR／REQUIRED`。

### P6-CODEX-016 — Calibration／Comparison／Manual Acceptance未完了

次はFrozen Phase 6必須Scopeであり、Backlog化できない。

- Position／Verbosity／Language／Self-preference／Confidence／Deterministic Conflictの
  Calibration／Bias Matrix。
- QwenでGovernance／Guardrail／Judge／RepairのOFF／OBSERVE／ENFORCE比較。
- Accuracy Candidate、Unsupported Claim、Definition Confusion、Abstention、Over-refusal、
  Repair Improved／Worseの比較。
- Token、Latency、Model Call、Repair回数、Recording Byteの分離Metric。
- Max New Tokens実UI Apply、Model Reload 0、次Generation反映。
- Settings別Tab同期、Mobile-width、Keyboard／Focus。
- Judge OBSERVE＋Repair ENFORCEの完全な有界Golden Path。

判定：`MAJOR／REQUIRED`。

### P6-GOV-002 — Acceptance Auditの誤分類

次の少なくとも一部はPASS主張を訂正する必要がある。

- P6-ACC-008：Attempt Provenance未保存。
- P6-ACC-017：Internal Judgeにより後続Main Turnが`model_busy`となり得る。
- P6-ACC-021：Live Run Evidence永続化未接続。
- P6-ACC-026：Repair実行経路が存在しないことを「追加Generation 0」の肯定Evidenceにしない。
- P6-ACC-035〜039：Judge／Repairを含むCurrent Request Stateへ未統合。
- P6-ACC-041：Status欄にRaw Codeが残る。
- P6-ACC-049：WriterのPath／Concurrency／Durability／Degradedが未成立。
- P6-ACC-053〜056：実Bindingと全State Matrixが未成立。
- P6-ACC-073〜076：必須作業をControllerへ返してCandidate停止した事実を含めて再評価する。
- P6-ACC-077：Phase全体には既に訂正済みIncident 3件があり、「本Rework中」へ範囲を狭めて
  Phase AcceptanceをPASSにしない。

Candidate Handoffの`P6-CODEX-001 CLOSED`も、Cross-turn Race／Lifecycle未解消のため再Openする。
`P6-CODEX-003 CLOSED`もRaw Status Code未解消のため再Openする。
`P6-CODEX-004 CLOSED`もRecording非直交／Writer境界未解消のため再Openする。

## 4. Required Rework

### 4.1 Lifecycle-owned Judge Execution

Detached Daemon Threadを廃止し、Runtimeが所有するBounded Coordinatorへ置き換える。
設計は次を全て満たすこと。

- 同一Main ModelをJudgeへ使う場合も、Internal JudgeがUser Main Turnを`model_busy`へしない。
- Main Generation／Judge／Repairの優先順位と直列化を明示する。
- Request開始時のMode／Role／Artifact／Config／Budget SnapshotをFreezeする。
- Cancel、Timeout、Shutdown、Join、FailureをTyped terminal stateへ収束する。
- Judge開始／完了／失敗をCurrent Request Statusへ投影する。
- 失敗時に過去ResultをCurrentとして表示しない。
- Public／Basic／v1の追加Call 0を維持する。

同期実行、単一Worker Queue、Main-priority Scheduler等の具体方式は、Frozen不変条件を満たす範囲で
Claude側設計統括者役が決めてよい。

### 4.2 Complete Bounded Repair

P6-E-WU-001〜006をLive Pathで完了する。

- Eligibility後に新Attemptを生成する。
- Phase 4／5全Point再通過、Rejudge、同Criteria比較、Presented Answer選択を行う。
- OriginalとRepair Attemptを別Identity／別Evidenceにする。
- Improved以外を採用しない。
- Guardrail／Authority Denyを解除しない。
- 実BudgetとCancelを有界化する。
- Ephemeral／Persistent両方でTerminal／SSE／Store整合を保つ。
- Retry／Regenerate／Branch／Citationを回帰させない。
- Hidden Original、Partial、Raw Thinkingを通常保存しない。

### 4.3 Decoupled／Hardened Recording

RecordingをJudgeの有無から独立させ、Generation／Evaluation／RepairのTyped Eventから記録する。

- Judge OFF＋Recording METADATA／FULLでも契約どおり記録可能。
- Composition単位でWriter／Lock／Quota Stateを共有する。
- External IdentityをDigest Mappingまたは厳格Validationし、Absolute／Traversal／Separatorを拒否する。
- Base Root／Subdirectory／Existing ArtifactのContainment、Symlink、Hardlink、Non-regular、Ownership／Modeを
  Fail-closed検証する。
- Active Temporaryを別Writerが削除しないOwner／Recovery規則を実装する。
- Atomic Replaceに加えFile／Directory fsync、Short／Failed Write、Restart Recoveryを検証する。
- Same request id、Concurrent Writer、Quota Race、Replacement Accountingを検証する。
- Failure／QuotaをCurrent Statusのdegradedまたは契約上のfail-closedへ明示する。
- Live Judge EvidenceへP6-LJG-002必須Traceを保存する。
- `.gitignore`／Public／Basic／User実runtime_data境界を維持する。

### 4.4 Runtime Status／UI

- `preparing／guarding／generating／judging／repairing／rejudging／completed／rejected／
  cancelled／failed／degraded`をCurrent Request単位で投影する。
- BackendのJudge／Repair／Recording Result／Failure／Budget／DegradedをTyped Frontend Contractへ追加する。
- Feature Modes UIにCurrent RequestとHistorical Latestを混同せず表示する。
- Mode OFF復帰、再Open、Reload、別TabでStateを同期する。
- Internal Raw Codeを通常UIへ表示しない。

### 4.5 Attempt／Judge Provenance

各Generation Attemptへ、最低限次を永続・投影する。

- Runtime Role。
- Exact Model Identity。
- Artifact Digest。
- Backend Identity／Version。
- Context Size。
- Generation Config／Digest。
- Request／Turn／Attempt相関。

Judge RunへModel／Artifact、Prompt／Rubric／Criteria／Config Digest、Seed、Independence、Token、Latency、
Call、CostまたはCost-unavailable Stateを関連付ける。既存ConversationをMigrationなしで読む場合は、
Optional versioned extensionとUnknown-safe decodeを用い、古いRecordを捏造しない。

### 4.6 Component Identity Correctness

- Current Governance Layerを実Phase 4 Runtime Bindingから投影する。
- Phase 3 Control Surfaceの有無だけに依存しない。
- Manifest／Plan／Digest整合を検証する。
- Main／Guard／Judge／Governance全てでNone／Unavailable／Invalid／Loading／Degraded／Activeを
  実状態どおり投影する。
- Selene候補未Load時のCurrent／Available捏造0を専用Testで確認する。

### 4.7 Safe Refusal Completion

- Chat Bubble、Status Line、Warning、Reload／Resumeの全通常SurfaceでRaw Internal Codeを表示しない。
- 未知の将来`guardrail_*`／`governance_*`もPrefix分類で固定JA／EN Safe Refusalへ写像する。
- 通常ErrorとSafety Refusalを混同しない。
- RefusalをAssistant Authority／次Contextへ入れない。
- Live／Persistent／Reloadの実Browser Testを追加する。

### 4.8 Calibration／Experiment／UI Acceptance

P6-D-WU-004、P6-H-WU-001〜005、P6-I-WU-003をFrozen内容どおり完了する。
DeepSeekはSafe Unsupported／Call 0でよい。Qwenと実Local Judge／Repairを使って、比較Matrixと
分離Metricを生成する。

Max New Tokens、別Tab、Mobile、Keyboard／Focusを含むReal Browser Golden Pathを実行する。
Browser制約がある場合は、実ブラウザで可能な範囲とStatic／DOM Testを分離し、必須項目を
未検証のままCandidateへ戻さない。

### 4.9 Acceptance／Governance Correction

既存Candidateを上書きせず、新規Append-only Correctionで誤分類を訂正する。
全Acceptance IDを独立に再導出し、Grouped Rangeだけで一括PASSにしない。

Phase全体のGovernance Incidentは既存3件を保持する。本Rework新規Incidentを別欄に分ける。
`Git Mutation 0`と`Working Tree Dirty`を引き続き分離する。

## 5. Allowed Mutation Envelope

本ReworkはFrozen Phase 6 Scope内であり、追加Human判断は不要である。

許可対象：

- Phase 6責務に必要な`src/margpa_runtime_llm/`、`frontend/`、生成Static、`tests/`。
- Private Runtime Data除外に必要な`.gitignore`。
- Phase 6 History／Operations／Handoffsへの新規Append-only Evidence。
- 短いProject-local `.venv/.t` Test Root。

禁止対象：

- Project Root外Read／Write／Execute／Delete／Move／Repair。
- Provider Memory、`.claude`、`.codex`等への保存。
- User実`runtime_data`のRead／Write／Migration。
- Model Canonical／Derived Artifactの変更・削除・移動。
- Network／Homebrew／System／Global Package変更。
- Stable Current Docs、Roadmap、Phase Indexの直接更新。
- Git Mutation。
- Phase 7以降の実装。

既存Sourceを無理に一つの巨大Orchestratorへ集約せず、Port／Application Service／Adapterを分離する。
必要な新規Pathは最高責任者Roleの範囲内で動的に決め、不要なPackageは作らない。

## 6. Validation Contract

最低限、次を新規または拡張Testで検証する。

```text
Judge:
  OFF Call 0
  OBSERVE Canonical／次Turn不変
  Mode Snapshot Freeze
  Timeout／Failure／Cancel／Shutdown
  Cross-turn／Multi-tab／Rapid-send Model Busy 0
  Current Request Result／Stale Result 0

Repair:
  New Attempt Identity
  Phase 4／5 all-point re-entry
  Rejudge／Before-After／Improved-only
  Budget／Cancel／Failure
  Persistent Atomicity／Terminal exactly once
  Branch／Retry／Regenerate／Citation

Recording:
  Judge OFFとの直交性
  OFF／METADATA／FULL
  Traversal／Absolute／Symlink／Hardlink／Non-regular
  Multi-writer／Same-id／Quota Race
  Short Write／fsync／Atomic／Restart
  Degraded projection
  Protected Capture 0／Git ignore

Status／UI:
  judging／repairing／rejudging／degraded
  Raw Internal Code 0
  Four Identities全State
  Max Tokens次Generation反映
  Reopen／Reload／別Tab／Mobile／Keyboard／Focus

Compatibility:
  Public／Basic／v1追加Call・Write 0
  Existing Conversation migration／read compatibility
  User実runtime_data接触0
```

最終共通Command：

```text
TMPDIR="$PWD/.venv/.t" ./.venv/bin/python -m pytest \
  -p no:cacheprovider --basetemp=.venv/.t/f
./.venv/bin/ruff check src tests scripts
./.venv/bin/mypy
npm run typecheck --prefix frontend
npm run lint --prefix frontend
npm test --prefix frontend -- --run
npm run build --prefix frontend
```

## 7. Return Contract

次を全て満たした場合だけ、新しい`Phase 6 Claude Second Rework Complete Candidate Handoff`を
作成して停止する。

- P6-CODEX-009〜016／P6-GOV-002が全てCLOSED。
- 再OpenしたP6-CODEX-001／003／004がCLOSED。
- Repair実Attempt Golden Pathが実行可能。
- Calibration／Qwen Mode Comparisonが完了。
- Open Major Finding 0。
- 全必須AcceptanceがPASSまたは契約上正当なSAFE_UNSUPPORTED。
- `PARTIAL`／`NOT_EXECUTED`／`UNVERIFIED`を必須項目へ残さない。
- Full／Static／Frontend／Real Model／Real BrowserがPASS。
- Root外Action 0、User実Data接触0、Git Mutation 0。

一部だけを実装して`Controller-owned Followup`、`Backlog`、`要否判断`として返さない。
個別進捗報告では停止せず、真のStop Conditionがない限り全Reworkを連結実行する。

もしFrozen Phase 6内で技術的に成立しない項目があるなら、Candidateではなく`BLOCKED`として、
再現手順、Root Cause、代替案、影響範囲、必要Authorityを一つのHandoffにまとめて停止する。
