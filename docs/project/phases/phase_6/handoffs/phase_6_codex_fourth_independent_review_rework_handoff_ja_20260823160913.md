# Phase 6 Codex Fourth Independent Review／DeepSeek Runtime Integration Exact Rework Handoff

```yaml
document_id: phase_6_codex_fourth_independent_review_rework_handoff_20260823160913
status: adjust_required_active_on_receipt
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役
created_at: 2026-08-23 16:09:13 JST
source_handoff: phase_6_claude_third_rework_complete_candidate_handoff_ja_20260823190000.md
independent_review_result: adjust_required
closure_state: do_not_close
human_decision_required_before_rework: false
automation: bounded_long_run
closure_target: fourth_rework_complete_candidate
```

## 1. Decision

`phase_6_claude_third_rework_complete_candidate_handoff_ja_20260823190000.md`は、Phase 6 Complete Candidateとして受理しない。

Focused Test 99件はPASSした。しかしSource、Frozen Requirements、Acceptance Matrix、過去のPARTIAL判定および実Runtime Compositionを独立照合した結果、既存Testが通過していても成立しないCritical／Major Findingを確認した。

最重要Findingは、Runtime Model Controlが独立したController Snapshotを更新するだけで、実Chat／Judge／RepairのGeneration経路が起動時に捕捉したModel Key、Generation Defaults、Context SizeおよびRuntime Infoを使い続ける点である。現在のUI／APIは適用成功を表示できても、次の実Generationへ変更が反映されたことを意味しない。

また、別WorkstreamでDeepSeek Q4_K_M Artifactの作成と構造検証は完了した。したがって、本ReworkではDeepSeekを未取得／未量子化として扱わず、Model Definition登録、実Load、起動中のQwen↔DeepSeek切替、実Chat反映およびRollbackまでをPhase 6 Acceptanceへ含める。

本Handoffは追加作業開始のためのExact Contractである。通常の進捗報告、Subphase境界、未解決事項の発見または過去Evidenceの存在だけを理由に停止しない。真のStop Condition以外は、担当Roleの権限内で設計、実装、Test、自己修正、再Testを連結する。

## 2. Mandatory Reading Order

開始前に、次を全文で再読する。存在しないPathを読了済みと主張せず、同名の新しいAppend-only Correctionがある場合はCurrent Stateとして併読する。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
3. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
4. `docs/project/phases/phase_6/requirements/phase_6_requirements_ja.md`
5. `docs/project/phases/phase_6/architecture/phase_6_architecture_ja.md`
6. `docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md`
7. `docs/project/phases/phase_6/operations/phase_6_execution_plan_ja.md`
8. `docs/project/phases/phase_6/handoffs/phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md`
9. `docs/project/phases/phase_6/handoffs/phase_6_claude_third_rework_complete_candidate_handoff_ja_20260823190000.md`
10. `docs/project/phases/phase_6/history/operations/phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md`
11. `docs/project/phases/phase_6/history/operations/phase_6_third_rework_acceptance_rederivation_addendum_ja_20260823184500.md`
12. `docs/project/phases/phase_6/handoffs/phase_6_deepseek_quantization_complete_candidate_handoff_ja_20260823141827.md`
13. `docs/project/phases/phase_6/history/operations/phase_6_deepseek_quantization_completion_evidence_ja_20260823141827.md`
14. `models/main/deepseek-r1-0528-qwen3-8b/manifests/deepseek-r1-0528-qwen3-8b-Q4_K_M-quantization-manifest-20260823141827.json`
15. 本Handoff。

再読後、Source As-builtを正本として照合する。Recovery文書の完了主張をSource／Testより優先しない。

## 3. Independent Review Evidence

```text
Focused Pytest:
  tests/unit/inference/test_model_access_coordinator.py
  tests/unit/bootstrap/test_judge_live_integration.py
  tests/unit/bootstrap/test_repair_live_integration.py
  tests/unit/bootstrap/test_recording_live_integration.py
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
  tests/unit/runtime_model_control/test_dynamic_context_and_tokens.py
  tests/integration/web/test_runtime_model_control_mutation_routes.py
Result:
  99 passed in 1.53s

Review Method:
  Source-based independent inspection
  Frozen Requirements／Acceptance／Prior PARTIAL Evidence照合
  User runtime_data Read／Write: 0
  Git Mutation: 0
  Network／External Action: 0
```

99件のPASSはRegression Evidenceとして有効である。一方、以下の競合、実Composition、Path AttackおよびMode変更条件を該当Testが実行していないため、Findingの反証にはならない。

## 4. Required Findings

### P6-CODEX-025 — Runtime Model Controlが実Generationの正本になっていない

`build_runtime_model_controller()`は独立Snapshotを保持するが、`web_application.py`はChat、Judge、RepairおよびRecordingを起動時の`application.config.selected_model`、`application.config.generation`および`runtime_info`で構築する。

`ConversationGenerationService`も、それらをインスタンスFieldへ固定し、各RequestでControllerのCurrent Snapshotを読まない。結果として次が起こる。

1. Advanced SettingsのMax New Tokens変更はController表示だけ更新し、次Chatは別のChat Settings値を使い得る。
2. Context Size Reload後も、Conversation Projection／Provenance／Validationは起動時Contextを使い得る。
3. Model Switchが成功しても、Chat／Judge／Repairは旧Model KeyでRequestを作り、実AdapterのLoaded Modelと不一致になる。
4. Recording／Judge EvidenceのModel Identity、ArtifactおよびBackend Traceが実Loaded Stateとずれ得る。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Runtime Model Controller／CoordinatorのCurrent Stateを、実Generationの唯一のProcess-local Runtime Source of Truthにする。
- Main Turn開始時に、Model Key、Artifact、Backend、Context Size、Max New Tokens、Generation ParametersおよびDigestを1 Attempt SnapshotとしてFreezeする。
- Chat、RAG、Summary、Judge、Repair、RejudgeおよびRecordingへ、役割ごとの実Snapshotを渡す。起動時定数をCurrent値として使い回さない。
- Mode／Model／Context変更はIdle Gate、CAS、Atomic CommitおよびRollbackを維持する。実行中Attemptの途中で値を変えない。
- Chat SettingsとAdvanced Runtime Settingsを二重正本にしない。表示値、Apply値、次Generation適用値およびEvidence値を一致させる。
- Max New Tokens変更はModel Reload 0で次Generationへ反映する。
- Context Size変更は同一Modelを安全にReloadし、成功後だけCurrent Stateと次Generationへ反映する。
- Model Switch成功後だけ全Current Projectionを更新し、失敗時は旧ModelでChat可能な状態へ戻す。

### P6-CODEX-026 — DeepSeek Q4_K_MがRuntimeへ未登録・未検証

量子化Workstreamにより、次のArtifactは作成・構造検証済みである。

```text
Model:
  deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Exact Upstream Commit:
  6e8885a6ff5c1dc5201574c8fd700323f23c25fa
Logical Artifact Path:
  models/main/deepseek-r1-0528-qwen3-8b/gguf/
  DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf
Size:
  5,027,782,720 bytes
SHA-512:
  b32af428f1e44c8f4f19b4069b5bc56042ecdb58b18cfb604ee17f3389786398
  6987e731ec4cd28929b72af4b845ac99d7b5f405d97c56bbec40db437518e786
Format:
  GGUF v3／qwen3／Q4_K_M mixed
Native Context Metadata:
  131072
```

Artifact完成は、Runtimeで使用可能であることのEvidenceではない。現行`config/models/`にはQwen Definitionしかなく、DeepSeek実Load、実Inference、起動中SwitchおよびQwenへのRollback／Switch-backは未実施である。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Existing Qwen Definitionを変更せず、DeepSeek用Model Definitionを新規追加する。
- Model Key、Logical Role、Artifact Relative Path、Size、SHA-512、Backend、Architecture、Native Context Limit、Chat Template、Thinking ControlおよびCapabilityは、GGUF／Manifest／実Backendから導出する。Qwen Definitionの値を無条件コピーしない。
- 起動初期値は引き続きQwenとする。
- Runtime起動後、Server RestartなしでQwen→DeepSeek→Qwenを切替可能にする。
- Advanced Settingsへ利用可能Model選択、Current Main Model、Context SizeおよびMax New Tokensを表示する。
- SidebarのCurrent Model表示も実Current Stateへ追随する。
- DeepSeekは初回に保守的なContext SizeでLoadし、MacのMemory／Latencyを実測する。Native Maximumを初回から割り当てない。
- DeepSeekの実Chatを最低1 Turn実行し、Model Key、Artifact Digest、Backend、Context、Max New TokensおよびAttempt Config DigestがDeepSeek実値になることを確認する。
- Qwenへ切り戻した後に実Chatを最低1 Turn実行し、Server Restart 0、既存Persistent Conversation破壊0、Runtime State不一致0を確認する。
- Load／Inference失敗時はTyped Failureと旧QwenへのRollbackを実証する。失敗をSupportedへ変換しない。
- Q8_0 Intermediate、Canonical Hugging Face Snapshot、Partial Artifact、Qwen、V4およびSibling Modelを削除・変更しない。

DeepSeekが現Mac／既存Backendで真にLoad不能であることを、Exact Model Definition、実Load Attempt、Typed ErrorおよびRollback Evidenceで初めて確認した場合だけ、`RUNTIME_UNSUPPORTED`を報告できる。その場合もPhase 6 Complete Candidateとはせず、実測Evidence付きの真のStop Conditionとして返す。

### P6-CODEX-027 — Background Thread開始とShutdownが競合する

`ModelAccessCoordinator.start_background()`はBackground Slotを取得後にCondition Lockを解放し、Threadを開始し、その後で`_background_thread`へ登録する。

この間に`shutdown()`が実行されると、`_background_thread is None`を見て安全停止済みとしてReturnし、その後Background Threadが開始してAdapter Unload後のModelへアクセスし得る。

判定：`CRITICAL／REQUIRED`。P6-CODEX-019のClosure主張を再Openする。

必要対応：

- ThreadのStarting／Registered／Running／TerminalをShutdownとAtomicに直列化する。
- Shutdownが未登録Starting Threadを見逃さない。
- Start failure時にSlot、Thread参照、Cancel参照およびStateを完全Rollbackする。
- Shutdown完了Return後にTargetが開始しないことをDeterministic Race Testで実証する。
- Shutdown／Start／Cancel／Main-priority／Unloadの全Interleavingで、二重Terminal、Slot Leak、Use-after-unloadおよびFalse Clean Shutdownを0にする。

### P6-CODEX-028 — Recording Path Nofollow契約が未完成

中間Path検証は`base_dir.resolve()`後のPathからComponentを再構築するため、Containment Root内の別Directoryを指すSymlink Componentを原Path上で検出できない。

さらに`.write.lock`は`os.open(O_CREAT | O_RDWR)`でFollowされ、Symlink、Hardlink、Non-regularおよび既存Ownerを検査しない。Exact Target File自身もQuota Scanの`exclude`対象となるため、既存Hardlinkを拒否できない経路がある。

判定：`CRITICAL／REQUIRED`。P6-CODEX-022のClosure主張を再Openする。

必要対応：

- Lexical ComponentをRootから順番にnofollow検査し、最後にResolved Containmentを別途検証する。
- Containment Root内を指すSymlinkも拒否する。
- Lock Fileをnofollowで開き、Regular、Single-link、Expected Owner／Modeを検証する。Platform上の安全な`openat`／`O_NOFOLLOW`等を使用し、未対応時にSilent Followしない。
- Exact Target、他JSON、Lock、TemporaryおよびDirectory EntryのSymlink／Hardlink／Non-regularをFail-closedにする。
- Internal Symlink、External Symlink、Lock Symlink、Lock Hardlink、Exact Target Hardlink、Multi-process RaceのFault Injectionを追加する。

### P6-CODEX-029 — Recording ModeがJudge Run開始時にFreezeされていない

Judge／Repair ModeはHook開始時にSnapshotされるが、Judge Evidence Recorderは書込時にRecording Modeを再取得する。

そのため、Run開始時OFF→完了前FULLでは予定外Write、FULL→OFFでは必要Evidence欠落が起こり得る。

判定：`MAJOR／REQUIRED`。P6-CODEX-020のClosure主張を一部再Openする。

必要対応：

- Judge、Repair、Recording Modeを同一Run開始時に1 Immutable Run SnapshotへFreezeする。
- RecorderはRun Snapshotを受け、途中でController Modeを再読しない。
- OFF→FULL、FULL→OFF、OBSERVE／ENFORCE変更をRun途中に行うDeterministic Testを追加する。
- 次Runには新Modeを反映し、Current Runには影響させない。

### P6-CODEX-030 — Repair Budgetを2回目Call後に強制していない

Repair Candidate生成後はBudgetを確認するが、Rejudge完了後にUsageを更新した後、Budgetを再判定せずDecode／Acceptance／Persistenceへ進む。

判定：`MAJOR／REQUIRED`。P6-CODEX-021のClosure主張を一部再Openする。

必要対応：

- 各Model Callの前後、およびCanonical Mutation前にAttempt、Call、Token、Wall Time、Depth、Cancel Budgetを評価する。
- Rejudge後にBudget超過したCandidateを採用・永続化しない。
- Slow Rejudge、Token超過、Cancellation境界、Clock境界のTestを追加する。
- Budget超過時にCanonical Head、Derived TurnおよびEvidenceの整合を維持する。

### P6-CODEX-031 — P6-OBS-004を実装裁量へ格下げしている

Frozen RequirementsのP6-OBS-004は、Runtime Stateとして次を明示する。

```text
idle, preparing, guarding, generating, judging, repairing, rejudging,
completed, rejected, cancelled, failed, degraded
```

Third Rework Addendumは、Acceptance Matrixの短い表現だけを使い、`judging／repairing／rejudging`の表示をChat Bubble上の任意実装案へ再分類した。しかし現行Feature Modes Panelも`running`等の粗いVocabularyであり、Frozen P6-OBS-004のStateを完全表現していない。

判定：`MAJOR／REQUIRED`。P6-ACC-038のClosed訂正を受理しない。

必要対応：

- Frozen RequirementsをAddendumの解釈で縮小しない。
- Current Request Identityと相関したRuntime Stateとして、上記全Vocabularyを表現する。
- 非同期Judge／Repair Architectureは維持できる。SSEを不必要に保持する必要はないが、Polling／Event／Projectionのいずれかで同じRequestの`judging→repairing→rejudging→terminal`を観測可能にする。
- Chat SurfaceとAdvanced Detailの表示粒度は分けられるが、どこかの利用者向けSurfaceで全Current Stateを明示する。
- Historical LatestをCurrent Request Stateへ混在させない。
- State Transition、Cancel、Failure、Degraded、Repairなし、Repair採用／不採用をTestする。

### P6-CODEX-032 — Acceptanceを根拠なく一括Carry-forwardしている

以前のClaude Handoffは、少なくとも次をPARTIALとして記録していた。

- P6-ACC-004：Qwen→DeepSeek→Qwen実Switch。
- P6-ACC-011：Max New Tokens実Apply、Reload 0、次Generation反映。

Third Rework Acceptance Rederivationは、P6-GOV-002で個別にClosedしていないAcceptanceまで「残り全件Carry-forward」とした。これはSource／Test Evidenceを持たないFalse Closureである。

判定：`CRITICAL EVIDENCE／REQUIRED`。

必要対応：

- 全Acceptance IDを個別に、Source、Test、実Model、実Browser、StaticまたはDeferredのEvidence Class付きで再導出する。
- `残り全件Carry-forward`を禁止する。
- P6-ACC-004、009、011、022、030、038、056、077および本Reworkの影響を受けるIDは必ず再実行する。
- PASS、PARTIAL、NOT_EXECUTED、UNVERIFIED、DEFERREDを事実どおり記録する。必須IDが未達ならComplete Candidateを返さない。

### P6-CODEX-033 — Root外IncidentのAction Inventoryが不足し、無許可Repairを正当化している

P6-GOV-004／005は、Project Root外への作成だけでなく、存在確認、削除および削除確認まで含む。誤作成後にAI側判断で削除することは許可されておらず、「自己検知・短時間・実質影響0」はAuthorizationの代替にならない。

判定：`CRITICAL GOVERNANCE／REQUIRED`。

必要対応：

- 新規Append-only Correctionを作り、Incident数とAction数を分離する。
- 各Incidentについて、Write、Read／Existence Check、Execute、Delete、Post-delete Checkを実際のCommand／Action単位で列挙する。
- 未観測を0と書かず、確認できないものはUNVERIFIEDとする。
- 「自己検知・即時是正」を改善Evidenceとして記録することはできるが、許可済み／無違反／実質0へ再分類しない。
- 本Rework中にRoot外誤作成が起きた場合、追加の確認、削除、移動またはRepairを行わず、Exact Pathと実施済みActionだけ報告して停止する。

既存6 Incidentは消せないHistorical Evidenceである。本Reworkの目的は過去を0へ戻すことではなく、虚偽のないAction Inventoryと、以後の新規Incident 0を成立させることである。

## 5. Required Rework Sequence

次の順序で連結する。通常の状況報告でTurnを終了しない。

1. `P6-GOV-006`相当の新規Append-only Correctionを作り、P6-GOV-004／005のAction InventoryとReturn Contract違反を訂正する。
2. Runtime Model Current Stateと実Generation Compositionを単一正本へ統合する。
3. DeepSeek Model Definition、Runtime Switch API／UI、Sidebar／Advanced Projectionを実装する。
4. ModelAccessCoordinatorのStart／Shutdown Raceを修正する。
5. Recording Path／Lock／Target Nofollowを修正する。
6. Judge Run SnapshotへRecording Modeを統合する。
7. Repair Budgetの全Call後／Mutation前強制を実装する。
8. P6-OBS-004の全State Projectionを完成する。
9. Unit／Integration／Concurrency／Fault Injectionを実行し、失敗を自力修正する。
10. 実QwenでBaseline Chatを確認する。
11. 実DeepSeekを保守的ContextでLoadし、DeepSeek Chat、QwenへのSwitch-back ChatおよびFailure Rollbackを確認する。
12. Advanced Settings、Sidebar、Context Size、Max New Tokens、Judge／Repair／RecordingおよびRuntime Stateを実Browserで確認する。
13. Acceptance IDを個別再導出し、過去のFalse ClosureをAppend-onlyで訂正する。
14. Full Backend、Static、Frontend、Real Model、Real Browserを再実行する。
15. 新規`Phase 6 Claude Fourth Rework Complete Candidate Handoff`を作成し、Controllerへ返して停止する。

## 6. Allowed Mutation Envelope

### 6.1 Repository Source／Test

本Finding解消に必要な、次の疎結合範囲を変更できる。

- `src/margpa_runtime_llm/modules/runtime_model_control/`
- `src/margpa_runtime_llm/adapters/runtime_model_control/`
- `src/margpa_runtime_llm/modules/conversation/`
- `src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py`
- `src/margpa_runtime_llm/bootstrap/runtime_model_control.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
- `src/margpa_runtime_llm/bootstrap/repair_live_integration.py`
- `src/margpa_runtime_llm/bootstrap/recording_live_integration.py`
- `src/margpa_runtime_llm/adapters/runtime_observability/local_filesystem_recording_writer.py`
- Runtime Model、Feature Mode、Conversation、SidebarおよびAdvanced Settingsに直接必要なWeb Route／Contract／Frontend Source。
- 上記に対応する`tests/`、`frontend/src/**/*.test.*`および既存Test Fixture。
- 新規`config/models/deepseek_r1_0528_qwen3_8b_q4_k_m.toml`またはRepositoryの既存命名規約に従う同等の1 Model Definition。

Dynamic Source Resolutionを使い、必要なものだけ変更する。上記を全て変更する義務はなく、無関係なModuleへ変更範囲を広げない。

### 6.2 Append-only Docs

新規作成だけを許可する。

- `docs/project/phases/phase_6/history/operations/phase_6_gov006_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/history/index/phase_6_fourth_rework_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/history/operations/phase_6_fourth_rework_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_fourth_rework_complete_candidate_handoff_ja_<timestamp>.md`

既存Stable Docs、Roadmap、Phase Index、Requirements、Architecture、ADR、Acceptance Matrixおよび既存Historyを直編集しない。CorrectionはAppend-onlyで参照関係を明示する。

### 6.3 Exact Model Read／Load Exception

`models/`はSymbolic Linkであり、Resolved TargetはProject Root外にある。本Handoffは、Userが今回明示した「DeepSeekを使えるようにする」目的に限り、次のLogical Artifactと必要最小MetadataをRead／Memory Loadする権限を固定する。

```text
models/main/deepseek-r1-0528-qwen3-8b/gguf/
  DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf
models/main/deepseek-r1-0528-qwen3-8b/manifests/
  deepseek-r1-0528-qwen3-8b-Q4_K_M-quantization-manifest-20260823141827.json
```

必要な比較Baselineとして、既存Qwen Definitionが指すExact Qwen ArtifactのRead／Loadを許可する。

許可内容：Read、Metadata取得、Digest照合、Runtime Memory Load、Inference。

禁止内容：Write、Delete、Move、Rename、Permission変更、Timestamp変更、Conversion、再Quantization、Download、Sibling探索、V4接触、Cache Cleanup。

Model Test Log、Runtime Data、TemporaryおよびScreenshotはProject Root内のTask専用Scratchへ置く。Userの実`runtime_data/`を使わない。

### 6.4 Project-local Scratch

Task専用Scratchとして、`.venv/.t/phase_6_fourth_rework_<timestamp>/`配下の新規内容だけを作成・使用・Task内削除できる。既存の未知Artifactを削除しない。

`/tmp`、`/private/tmp`、`$TMPDIR`、`/dev/null`、Home Directory、`.claude`、`.codex`、Provider Memoryその他Project Root外を、Log／Redirect／Temp／Probe／Existence Check／Cleanupに使わない。

## 7. Forbidden Actions

- Git Stage／Commit／Push／Branch／Tag／Release。
- Network、PyPI、Hugging Face、GitHub、Homebrew、AWSその他External Action。
- User実`runtime_data/`のRead／Write／Migration／Delete。
- Existing Model Artifactの削除、上書き、移動または再量子化。
- Stable Current Docs、Roadmap、Phase IndexまたはFrozen Requirementsの直編集。
- Provider Memory、`.claude`、`.codex`、Project外Scratchpadへの接触。
- Root外誤作成後のAI判断による確認、削除、移動または修復。
- RequirementsをAcceptance Matrixの短い要約で縮小すること。
- `Test PASS`だけを根拠に実Model／実Browser AcceptanceをPASSへ変更すること。
- PARTIAL／NOT_EXECUTED／UNVERIFIEDを一括Carry-forwardでClosedへ変更すること。
- 通常の進捗報告、Subphase完了、Deferred EvidenceまたはController-owned Workを理由に停止すること。

## 8. Validation Contract

### 8.1 Runtime Model Single Source of Truth

```text
Initial current model:
  Qwen

Qwen baseline generation:
  PASS
  Applied Model Key／Artifact／Backend／Context／Max Tokens／Digest一致

Dynamic Max New Tokens:
  Apply success
  Model reload 0
  Next generationへ反映
  Chat UI／Advanced UI／Attempt Evidence一致

Dynamic Context Size:
  Idle-only reload
  Current Modelだけreload
  Next generation／Status／Evidence一致
  Failure時旧ContextへRollback

Dynamic Model Switch:
  Qwen → DeepSeek → Qwen
  Server restart 0
  Each switch Atomic CAS
  Each modelで実Chat 1 Turn以上
  Failure時旧ModelへRollback
  Persistent Conversation破壊0
  Sidebar／Advanced Current Model追随

Judge／Repair／Recording:
  Current Role Snapshotと実Loaded Model一致
  Stale startup Model Key 0
  Artifact／Backend／Config Digest一致
```

### 8.2 Concurrency／Lifecycle

```text
Background start vs shutdown deterministic race
Shutdown return後Target start 0
Shutdown timeout後Adapter unload 0
Thread start failure slot leak 0
Target exception stale running 0
Main-priority cancellation terminal 1
Shutdown後new Main／Background 0
```

### 8.3 Recording

```text
Internal-root symlink reject
External-root symlink reject
Lock symlink reject
Lock hardlink reject
Exact target hardlink reject
Non-regular reject
Cross-process lock／quota race
Short write／replace／fsync failure
Task-owned orphan recovery only
```

### 8.4 Run Snapshot／Repair Budget

```text
Judge／Repair／Recording Mode mid-run change:
  Current Run snapshot不変
  Next Run新Mode反映

Repair:
  Budget check before／after every model call
  Budget check before canonical mutation
  Post-rejudge wall-time exceed reject
  Post-rejudge token exceed reject
  Canonical head mutation 0 on reject
```

### 8.5 Runtime State／UI

次をCurrent Request Identity付きでBackendおよび利用者向けSurfaceから確認する。

```text
idle
preparing
guarding
generating
judging
repairing
rejudging
completed
rejected
cancelled
failed
degraded
```

Historical LatestとCurrent Requestを分離し、Reload／Resume／Retry／Regenerate／Branch Selectでも誤相関しない。

### 8.6 Full Validation

- Focused Unit／Integration／Concurrency／Fault Injection。
- Backend Full Test。
- Ruff Format／Check。
- Mypy。
- Frontend Typecheck／Lint／Test／Build。
- 実Qwen Model。
- 実DeepSeek Model。
- 実BrowserでQwen→DeepSeek→Qwen、Context、Max New Tokens、Sidebar、Advanced Settings、Judge／Repair／Recording、Current Runtime State。
- Test Countだけでなく、Command、Exit Code、Evidence Class、対象Model、未実施項目を記録する。

## 9. Acceptance Re-derivation Rules

Acceptance再導出は次に従う。

1. 各IDを1行以上で個別に列挙する。
2. 判定は`PASS／PARTIAL／NOT_EXECUTED／UNVERIFIED／DEFERRED／NOT_APPLICABLE`から選ぶ。
3. Evidence Source、Evidence Grade、Current Runtime Impactを付ける。
4. Prior PASSは今回のSource変更で影響を受けるか再評価する。
5. 実Model必須IDをMock／StaticだけでPASSにしない。
6. 実Browser必須IDをDOM Unit TestだけでPASSにしない。
7. RequirementsとAcceptance Matrixが衝突または粒度差を持つ場合、上位かつ詳細なFrozen Requirementsを優先する。
8. 担当Roleが自力で解決できる次作業をHuman Decisionへ返さない。

## 10. Governance Return Rule

Phase 6累積Incidentは少なくとも6件であり、0へ戻さない。P6-GOV-004／005のAction Inventory訂正後、次を分けて報告する。

```text
Historical Incident Count
Historical Exact Action Count
Current Fourth Rework New Incident Count
Current Fourth Rework Root-outside Action Count
Unverified Action Count
```

本ReworkでRoot外Incidentが発生した場合は、その時点で真のStop Conditionである。追加確認・削除・Repairをせず、実施済みActionだけを報告する。

## 11. Return Contract

次を全て満たした場合だけ`COMPLETE_CANDIDATE`を返す。

- P6-CODEX-025〜033が全件CLOSED。
- 再OpenしたP6-CODEX-019／020／021／022／024を新EvidenceでCLOSEDにできる。
- DeepSeek Model Definition、実Load、実Chat、QwenへのSwitch-backがPASS。
- Qwen／DeepSeek／Qwenの全Attemptで実Model IdentityとEvidenceが一致。
- P6-ACC-004、009、011、030、038、056、077および影響Acceptanceが個別再検証済み。
- 必須AcceptanceへPARTIAL／NOT_EXECUTED／UNVERIFIEDがない。
- Open Critical／Major Finding 0。
- Backend Full、Static、Frontend、実Qwen、実DeepSeek、実BrowserがPASS。
- Current Fourth Reworkの新規Root外Incident／Action、Git Mutation、Network、User実Data接触、Provider Memory接触が0。
- Historical Incident／Action Inventoryを過小申告していない。

Return Handoffには、少なくとも次を含める。

- Exact changed files。
- Exact new files。
- DeepSeek DefinitionとArtifact Provenance。
- Qwen→DeepSeek→Qwenの実測結果、Load時間、Generation時間、Memory／Resource観測およびRollback結果。
- Runtime Model、Context、Max New Tokensの実Generation反映Evidence。
- Concurrency／Path／Mode Snapshot／BudgetのFault Injection結果。
- P6-OBS-004全StateのProjection Evidence。
- Acceptance ID個別再導出へのEntry Point。
- Governance CorrectionへのEntry Point。
- Full／Static／Frontend／Real Model／Real Browser結果。
- Open Finding 0、または真のStop ConditionのExact Evidence。

真のStop Conditionが発生した場合だけ、`BLOCKED`ではなく次を返す。

```text
STOPPED_SAFE
Current Transitionへの直接影響
自力解消を試した範囲
不足Authorityまたは物理的制約
Mutation／Process／Artifactの安全状態
Exact Resume Entry
```

DeepSeekが実測上Runtime Unsupportedの場合はComplete Candidateを宣言せず、この形式で返す。他のController-owned Workを未実施のまま一緒に止めない。安全な独立Workは完了させてから、DeepSeekのExact Stop Evidenceを返す。

