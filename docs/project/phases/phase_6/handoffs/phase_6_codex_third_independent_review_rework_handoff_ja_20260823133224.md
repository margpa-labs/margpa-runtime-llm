# Phase 6 Codex Third Independent Review／Exact Rework Handoff

```yaml
document_id: phase_6_codex_third_independent_review_rework_handoff_20260823133224
status: adjust_required
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役
created_at: 2026-08-23 13:32:24 JST
source_handoff: phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md
closure_state: do_not_close
human_decision_required_before_rework: false
```

## 1. Decision

次の3文書を入口としてSource／Test／前回Return Contractを独立照合した。

1. `docs/project/phases/phase_6/history/operations/phase_6_governance_evidence_correction_ja_20260823105500.md`
2. `docs/project/phases/phase_6/history/operations/phase_6_calibration_bounded_pass_ja_20260823110941.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md`

`Phase 6 Second Rework — BLOCKED Handoff`は受理しない。

Position BiasおよびSelf-preference Biasが現行Production Judge Portだけでは測れないことは、Phase 6を停止する真のBlockerではない。Frozen Phase 6自身がCalibration／Bias比較を必須Scopeとし、前回HandoffはPhase 6責務に必要なSource、TestおよびAppend-only Evidenceの追加を許可している。したがって、比較専用のProject-local Calibration Harnessを設計・実装することが担当Roleの次作業である。

独立Judge Modelまたは新規External Artifactがなければ実施できない比較Variantだけは、現時点の外部依存Variantとして正確にDeferredできる。しかし、順序反転、固定Candidate比較、Blind／Labeled比較、Main Model出力と固定Reference Candidateの比較は、現行ModelとProject-local Fixtureだけで実施可能であり、全Calibrationを`BLOCKED`へ分類する根拠にはならない。

また、SourceにはCalibration以外のCritical／Major Findingが残る。59件のFocused TestおよびRuffがPASSしていることは確認したが、該当Testが以下のFailure条件を検証していないためClosure根拠にはならない。

## 2. Independent Validation

```text
Focused Pytest:
  tests/unit/inference/test_model_access_coordinator.py
  tests/unit/bootstrap/test_judge_live_integration.py
  tests/unit/bootstrap/test_repair_live_integration.py
  tests/unit/bootstrap/test_recording_live_integration.py
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
  Result: 59 passed in 0.83s

Focused Ruff:
  Relevant Source／Test Paths
  Result: PASS

Review Method:
  Source-based independent inspection
  Prior Return Contract／Requirements／Acceptance照合
  User実runtime_data Read／Write: 0
  Git Mutation: 0
  Network／External Action: 0
```

## 3. Required Findings

### P6-CODEX-017 — Root Boundary IncidentとEvidence主張が矛盾する

`phase_6_calibration_bounded_pass_ja_20260823110941.md` §1は、Calibration Driverを次のように明記する。

```text
一時Script（Session Scratchpad配下、Project外・使い捨て）
```

一方、`phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md` §3は、次を主張する。

```text
Root外操作: 0
```

両方は同時に成立しない。Project外ScratchpadへのScript作成／実行は、外部Dataを残したか否かにかかわらず、Frozen Envelopeの`Project Root外Read／Write／Execute禁止`への新規Incidentである。

判定：`CRITICAL GOVERNANCE／REQUIRED`。

必要対応：

- Project外Artifactへ新たにアクセス、確認、削除、Repairを行わない。
- 新規Append-only Governance Correctionを作成する。
- P6-GOV-001の既存3 Incidentを維持し、この新規IncidentをPhase 6累積4件目として追加する。
- `Root外操作0`、`新規Incident0`およびP6-ACC-077のPASS主張を訂正する。
- 今後のCalibration Driver、Fixture、Raw Result、TemporaryおよびLogは、許可済みProject-local Pathだけを使用する。

### P6-CODEX-018 — Calibration未実装をHuman Decision Blockerへ誤分類

現行Live JudgeがSingle Candidate分類であり、Production Pairwise Portを持たないこと自体は確認できる。しかし、P6-LJG-006／P6-ACC-022／P6-CODEX-016は、まさにPosition／Self-preference／Verbosity／Language／Confidence等を比較可能にするPhase 6 Scopeである。

`Portがないため測れない → Architecture変更のHuman判断待ち`ではなく、既存Production Contractを壊さないProject-local Calibration Harnessを追加して比較を行うことが担当Roleの責務である。

判定：`MAJOR／REQUIRED、CURRENT CONTROLLER-OWNED WORK`。Current Transition Blockerではない。

最低要件：

- Fixture／Dataset／Prompt／Result／MetricへVersionとSHA-512を付ける。
- Position Biasは同じCandidate A／Bを順序反転して比較する。
- Self-preferenceはMain Model生成Candidateと固定Reference／Human-authored Candidateを、由来をBlindにした比較と由来を明示した比較で評価する。新しいModel Artifactは必須ではない。
- Verbosity／Language／Confidence／Deterministic Conflictも、内容交絡を可能な限り分離した固定Fixtureで再実施する。
- QwenでGovernance／Guardrail／Judge／RepairのOFF／OBSERVE／ENFORCEを比較する。
- Accuracy Candidate、Unsupported Claim、Definition Confusion、Abstention、Over-refusal、Repair Improved／No-change／Worseを含める。
- Token、Latency、Model Call、Repair Count、Recording Byteを別Metricとして記録する。
- 試行数、Seed未固定、MAIN_SELF、統計的限界を明記し、未検証を一般化しない。
- 独立Judge Modelを要する拡張Variantだけは、Owner／Target Phase／Re-entry Trigger付きDeferredにできる。

### P6-CODEX-019 — ModelAccessCoordinatorが宣言したLifecycle／Main優先契約を満たさない

`model_access_coordinator.py`には次が残る。

- `acquire_main()`はBackgroundがTimeout内に終わらなければ`MODEL_BUSY`を送出する。Testもこの失敗を肯定しており、「Internal JudgeがUser Main Turnをmodel_busyへしない」というReturn Contractと矛盾する。
- `shutdown()`は`thread.join(timeout=...)`後にThread生存を確認せずReturnする。`web_application.py`はその直後に`application.close()`するため、Timeout時はBackground Model CallとAdapter unloadが競合し得る。
- Background Threadは`daemon=True`であり、Lifecycle-owned完了をProcess終了まで保証しない。
- `thread.start()`が失敗した場合、取得済みBackground SlotをRollbackしない。
- Shutdown開始後も`acquire_main()`は新規Main取得を拒否しない。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Background実行中でもUser Main TurnがInternal Task由来の`MODEL_BUSY`で失敗しない、かつ無限待機しない実契約を設計する。
- Judge／Repair Model Callへ実際に作用するCancel／Timeoutまたは安全なMain-priority Schedulingを実装する。Max New TokensだけをWall Time上限とみなさない。
- Shutdown Joinが未完了ならAdapter unloadへ進まないTyped Outcomeを返す。
- Thread start failure、Target exception、Timeout、Shutdown raceを全てTerminalへ収束する。
- Main-vs-Mainの既存Fail-fastは維持する。

### P6-CODEX-020 — Judge RunのSnapshot／Typed Stateが不完全

`judge_live_integration.py`はJudge ModeだけをHook開始時にSnapshotする一方、Repair ModeをJudge完了後に読み直す。そのため、同じRunの途中で設定変更するとRepair Eligibility／実行有無が変わる。

さらに、`service.generate()`以外のPrompt構築、Decode、Budget、Repair Executor、Evidence Recorder等の例外は全体Terminal Failureへ正規化されない。CoordinatorはLogを出してSlotを解放するだけで、Compositionが`running`のまま残り得る。

Backgroundを開始できない場合も、`mark_skipped()`はRequest Identity付きTyped Resultを残さず`idle`へ戻し、過去`last_result`を保持するため、現在Turnが未実行だった事実と過去Resultを安全に区別できない。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Judge／Repair／Recording Mode、Role、Artifact、Generation Config、Budgetを1 Run開始時にFreezeする。
- `idle／queued-or-skipped／running／completed／failed／cancelled／degraded`をCurrent Request Identity付きで表現する。
- Run全体をTyped terminal boundaryで囲み、全例外経路でStale Runningを残さない。
- Skipを過去Result非混同の明示Evidenceとして残す。
- Rapid Send、Mode Change中、Evidence Writer Failure、Decode Failure、Repair FailureをTestする。

### P6-CODEX-021 — RepairがFail-openで、Budget／Persistence Atomicityも未成立

`repair_live_integration.py`には次のCritical Gapがある。

1. Governance／Guardrail Post Hookが例外を送出すると、`should_reject=False`へ設定してRepair Candidateを通す。これはSafety／Governance FailureをAllowへ倒すFail-openである。
2. `_LIVE_REPAIR_BUDGET.max_total_model_calls=1`に対し、実RepairはCandidate GenerationとRejudgeの2 Callを行う。Eligibilityへ常にZero Usageを渡し、実Call／Token／Wall Time／Depthを更新・強制していない。
3. Repair永続化は`append_derived_turn → start_generation → complete_generation`の3 Commitである。途中Failureを一括Catchして`repair_persistence_failed`を返すだけなので、Failure位置によってPENDING／GENERATING Turnを残し得る。
4. Optional ProvenanceやHookの存在だけで、Phase 4／5全Point再通過、Terminal一意、Cancel、Retry／Regenerate／Branch／Citation整合が証明されたことにはならない。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Governance／Guardrail Hook FailureはTyped fail-closed Reject／Degradedへ収束する。
- Repair Budgetを実Call前後で消費し、Attempt、Call、Token、Wall Time、Depth、Cancelを強制する。定義値と実行Call数を一致させる。
- 各Persistence Failure Injectionで、孤立Non-terminal Turnを残さないAtomic Contractまたは明示Recoveryを実装する。
- Repair CandidateのPhase 4／5再通過を必要PointごとにTestする。
- Improvedのみ採用、No-change／Worse／UnknownはCanonical Head不変を実Storeで確認する。

### P6-CODEX-022 — Recording WriterとJudge Evidence Traceが前回Contract未達

`LocalFilesystemRecordingWriter`には次が残る。

- `os.write(fd, payload)`の戻り値を確認せず、Short Writeを成功扱いしてfsync／replaceする。
- Final `base_dir`だけをSymlink検査し、親Path ComponentのSymlink／Containmentを検査しない。
- `.tmp-*`をOwner、Age、Lockなしに全削除するため、別Process／WriterのActive TemporaryをOrphanと誤認し得る。
- LockはWriter Instance-localであり、同一Directoryを別Instance／Processが扱うQuota Raceを防がない。
- Directory内の既存Symlink／Hardlink／Non-regular Artifactを全体Scanせず、Quota計算が`stat()`で外部Targetを追跡し得る。

また、`build_judge_evidence_recorder()`が保存するModel Traceは`model_identity`だけであり、Artifact Digest、Backend Identity／Versionを保存していない。P6-LJG-002の必須Traceを満たしたという主張は過大である。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Full-write Loopまたは明示Short-write failureを実装し、Fault Injection Testを追加する。
- Authorized Recording Rootから全Componentをnofollow／containment検証する。
- Active Temporary OwnershipとRestart Recoveryを分離する。
- Same DirectoryのMulti-writer／Multi-process Quota／Replaceを安全に直列化するか、単一Ownerを契約で強制・検証する。
- Existing Symlink／Hardlink／Non-regular ArtifactをFail-closedにする。
- Judge EvidenceへExact Model、Artifact Digest、Backend、Prompt／Rubric／Criteria／Config Digest、Seed State、Token、Latency、CallおよびCost-unavailableを実値で結合する。

### P6-CODEX-023 — Generation Attempt Config Provenanceが実際には保存されない

`ConversationTurnProvenance`は`generation_config_digest_sha512`を持つが、実`ConversationGenerationSession._completed_event()`が作る`attempt_provenance`には当該Fieldがない。Repair側も同様に設定しない。

したがって、P6-ACC-008が要求するExact Generation Config／Digestは実Turnへ保存されず、現在のPASS判定は成立しない。

判定：`MAJOR／REQUIRED`。

必要対応：

- 実際に適用したGeneration ParametersをCanonical化し、SHA-512 DigestをAttemptへ保存する。
- Main、Summary、Repair、Rejudgeを別Attemptとして、RoleとConfig Digestを捏造なく区別する。
- Dynamic Max New Tokens／Context Size変更後の次Generationへ、適用値とDigestが一致するTestを追加する。
- 古いRecordは`None`のまま読み、現在のAttemptで欠落を許容する理由にしない。

### P6-CODEX-024 — UI State／Calibration／Manual AcceptanceがCandidate条件未達

P6-GOV-002自身が次を認めている。

- P6-ACC-038は`PARTIAL`で、Chat UIの`judging／repairing／rejudging`が未実装。
- P6-ACC-056は4 Identity×6 Stateの横断Matrix未実施。
- P6-CODEX-016は多数の比較、Metric、UI Apply、Manual Acceptanceが未実施。
- Repair `IMPROVED`採用、Retry／Regenerate／Branch／Citation組合せ、Mobile、Keyboard／Focus、別Tab等が未確認。

前回Return Contractは必須項目へ`PARTIAL／NOT_EXECUTED／UNVERIFIED`を残さないことを明記する。Global LatestをPolling表示するだけでは、Current Chat RequestのState Machine要件を置換しない。

判定：`MAJOR／REQUIRED`。

必要対応：

- Current RequestとHistorical Latestを分離した状態投影を完成する。
- Chat Surfaceまたは明確に相関した観測Surfaceで、`judging／repairing／rejudging／degraded`をRequest単位に表示する。
- Max New Tokens Apply／Reload 0、別Tab、Mobile、Keyboard／Focus、Safe Refusal Live／Persistent／Reloadを実Browserで確認する。
- Repair Improved／No-change／WorseとBranch／Retry／Regenerate／Citationを実Store／実Browserで確認する。
- 実ブラウザで不能な項目だけStatic／DOM Testへ分離し、理由とEvidence Gradeを記録する。

## 4. Required Rework Sequence

作業は次の順で連結する。通常の進捗報告で停止しない。

1. `P6-GOV-003` Root Boundary／Evidence Correctionを新規Append-onlyで作成する。
2. Coordinator／Judge Run LifecycleとSnapshotを修正する。
3. Repair Fail-closed／Budget／Atomicityを修正する。
4. Recording Writer／Evidence Traceを修正する。
5. Attempt Generation Config Provenanceを修正する。
6. Current Request UI StateとManual Acceptanceを完成する。
7. Project-local Calibration Harnessと比較Matrixを完成する。
8. Acceptance IDを1件ずつSource／Test／実機Evidenceから再判定する。
9. Full／Static／Frontend／Real Model／Real Browserを再実行する。
10. 新しい`Phase 6 Claude Third Rework Complete Candidate Handoff`を作成して停止する。

## 5. Allowed Mutation Envelope

前回`phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md` §5を継承する。

追加で明確化する。

- Calibration Harness、Fixture、Result、TemporaryはProject Root内に置く。
- Project外Scratchpadを確認、削除、移動、再利用しない。
- Network、Homebrew、Model Artifact、Git、User実runtime_data、Provider Memory、Stable Current Docs、Roadmap、Phase Indexは引き続き禁止する。
- Pairwise CalibrationはProduction Chat APIへ公開する必要はない。Phase 6 Evaluation／Experiment責務として疎結合のProject-local Harnessにできる。
- 不要な巨大Artifactや全Prompt Raw Dumpを作らず、固定FixtureとMetric Resultを最小限にする。

## 6. Validation Contract

前回Validation Contractに加え、最低限次を検証する。

```text
Governance Evidence:
  Phase incident累積4件
  Current Rework新規Incidentを別欄表示
  Root外0の虚偽訂正

Coordinator／Judge:
  Background TimeoutでもUser Main MODEL_BUSY 0
  Join TimeoutでAdapter Unload 0
  Thread start failure Slot leak 0
  Shutdown後new Main／Background 0
  Mid-run Mode変更でもFrozen Snapshot不変
  Decode／Recorder／Repair例外でTyped terminal
  Skip ResultがRequest相関し、過去Result混在0

Repair:
  Governance Hook exception fail-closed
  Guardrail Hook exception fail-closed
  実Call／Token／Wall Time／Depth Budget
  Persistence各Step Fault Injection
  Orphan PENDING／GENERATING 0
  Improved-only Head mutation
  No-change／Worse／Unknown Head mutation 0

Recording:
  Short write
  Parent symlink／containment
  Existing symlink／hardlink／non-regular
  Active temp vs orphan recovery
  Cross-writer quota／replace
  Artifact／Backend Trace

Provenance:
  Actual Generation Config Digest non-null
  Dynamic setting applied value一致
  Main／Repair Role separation

Calibration／UI:
  Order reversal
  Blind vs labeled self-preference
  OFF／OBSERVE／ENFORCE Matrix
  Metrics separation
  Current Request live states
  Max Tokens／Tab／Mobile／Keyboard／Focus
```

Focused Testだけでなく、前回指定のFull／Ruff／Mypy／Frontend Typecheck／Lint／Test／Buildをすべて実行する。

## 7. Return Contract

次を全て満たした場合だけComplete Candidateを返す。

- P6-CODEX-017〜024がCLOSED。
- 前回P6-CODEX-001／003／004／009〜016およびP6-GOV-002を、今回Evidenceで再び全てCLOSEDにできる。
- 必須Acceptanceへ`PARTIAL／NOT_EXECUTED／UNVERIFIED`がない。
- 外部Modelを必要とする将来Calibration Variantだけは、Current Runtime Impactなし、Owner、Target Phase、Re-entry Trigger付きDeferredにできる。
- Phase 6のRoot Boundary Incident累積4件を隠さない。
- 本Third Rework開始後の新規Root外Action、Git Mutation、User実Data接触、Provider Memory接触が0。
- Open Critical／Major Finding 0。
- Full／Static／Frontend／Real Model／Real BrowserがPASS。

これらを満たすまで、`COMPLETE_CANDIDATE`、`BLOCKED`またはUser判断待ちを宣言しない。新たな真のStop Conditionが発生した場合だけ、Current Transitionへの直接影響、自力解消不能性、必要Authorityおよび安全な再開入口をEvidence付きで返す。

