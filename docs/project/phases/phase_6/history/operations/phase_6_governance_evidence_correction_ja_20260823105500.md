# Phase 6 Governance／Evidence Correction（Append-only、P6-GOV-002）

```yaml
document_id: phase_6_governance_evidence_correction_p6_gov_002
status: append_only_correction
phase: phase_6
work_unit: p6_gov_002_second_rework_in_progress
role: Claude側設計統括者役
created_at: 2026-08-23 10:55:00 JST
supersedes_nothing: true
corrects_by_reference:
  - phase_6_claude_rework_complete_candidate_handoff_ja.md
  - phase_6_governance_evidence_correction_ja_20260823053000.md
authority: phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md
```

本文書は`phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md`
（Second Independent Review）の指示に基づき、P6-GOV-002として個別Acceptance ID
（グループ化せず一件ずつ）を、本Rework Session内で実際に実装・実行し
Passした自己申告Evidence（ソースPath／Test名／実行結果）のみを根拠に再判定する。
既存History／Candidate Handoffを書き換えず、Append-only Correctionとして記録する。
P6-GOV-001が記録した3件のGovernance Incident（Root Boundary Violation 1、
Pre-authority Access 1、Unnecessary Escalation 1）は、本Reworkでも新規Incidentが
0件であることをもって、引き続きPhase全体で3件のまま維持する（P6-ACC-077参照、
「本Rework期間中のみ」へScopeを狭めない）。

**本文書作成時点で、本Second Reworkは未完了である。** P6-CODEX-016（Calibration／
Qwen Mode比較実験）およびP6-CODEX-012の一部（Judge/Repair/RecordingがChat UI自身の
Bubble上でLive遷移する、真にTurn内リアルタイムのUI State Machine）は、本文書作成時点で
未実施／未実装である。該当するAcceptance IDは正直にNOT_EXECUTED／PARTIALのまま記録し、
達成したふりをしない。

---

## 1. 再Openされた P6-CODEX-001／003／004

### P6-CODEX-001（Cross-turn Race/Lifecycle）

```text
事実: `ModelAccessCoordinator`
  （src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py）
  を新規実装し、Main Turn／Background Task（Judge／Repair）間のModel Access調停を
  Main-vs-Main即時Fail-fast（既存契約維持）とMain-vs-Background有界Wait
  （デフォルト30秒）に分離した。`ConversationGenerationService`
  （conversation_generation.py）はこのCoordinatorを共有Instanceとして受け取り、
  `bootstrap/web_application.py`で一つのCoordinatorを構築しConversation側と
  Judge/Repair側の両方へ同一Instanceを注入している。
  独立Test: tests/unit/inference/test_model_access_coordinator.py（10件、全Pass）。
  Judge Hook結合Test: tests/unit/bootstrap/test_judge_live_integration.py内の
  test_hook_skips_and_marks_skipped_when_coordinator_is_busy（Main稼働中は
  Background Taskが即座にSkipされ、Queueされないことを実証）。
  Runtime Shutdown連携: `web_application.py`の`_close()`が
  `model_access_coordinator.shutdown()`を`application.close()`より先に呼び、
  稼働中のBackground Model Callを必ずJoinしてからAdapter Unloadへ進む
  （Judgeスレッドとの競合を構造的に排除）。

  【実Hardware Golden Path中に発見・修正した重大Bug】実Server
  （main.qwen3-4b-q4-k-m、実Browser経由）でJudge Mode=observe／enforceを
  適用し実際にChat発話したところ、`/api/v5/feature-modes/status`が
  `judge.state: "idle"`／`judge.last_result: null`のまま変化しないという
  事実が判明した。原因調査の結果、`_invoke_judge_completion_hook()`は
  `ConversationGenerationSession._completed_event()`内から同期的に
  呼ばれるが、そのTurn自身がModelAccessCoordinatorへ確保した"main" Slotは
  `events()`の`finally: self._release()`でのみ解放され、これは
  Generatorが完全にExhaustされた後（＝COMPLETED Eventがこのメソッドから
  Returnされ、呼び出し元が次のIterationを試みてGeneratorが終了する時点）
  にしか実行されない。つまりJudge Hookが
  `model_access_coordinator.start_background()`を呼ぶ瞬間、そのTurn自身の
  "main" Slotはまだ解放されておらず、`start_background()`は常に
  `self._current_kind is not None`によりFalseを返し、Judgeは
  「Busyのため今回はSkip」という扱いで静かに一度も実行されていなかった
  （Modeに関わらず、あらゆる実Turnで再現する）。
  この不具合は、既存の全Unit Testが`hook()`をこの正確な解放Timing関係を
  経由せず直接呼び出していたため検出されなかった（実Fake Callによる
  Unit Testの限界であり、実Browser＋実Model Serverでの確認によって
  初めて捕捉できた）。
  修正: `_completed_event()`内でRecording／Judge両Hookを呼ぶ直前に
  `self._release()`を明示的に呼び、Main Slotを先に解放してから
  Background Slot取得を試みるようにした（`events()`側の`finally`は
  同じrequest_idに対し二重に呼ばれても安全なGuard済みなので、
  そのまま残置）。
  Regression Test: tests/unit/conversation/等の既存1494件は全てPass
  （挙動を変えずに解放Timingのみ前倒し）。実Hardware再検証:
  修正後にServerを再起動し、同一手順で再実行した結果、
  `judge.state: "completed"`、`judge.last_result.recommendation`
  （"accept"／"needs_repair"）、Judge Evidence File実書き込み
  （`<request_id>-judge-evidence.json`、`config_digest_sha512`等の
  実Field含む）を実際に確認した。さらにJudge=enforce／Repair=enforce
  で「円周率を小数点以下20桁まで」という実際にModelが誤答しやすい
  質問を送ったところ、`recommendation: "needs_repair"` →
  `repair_eligibility: "eligible"` → Repair候補生成＋Rejudgeが実際に
  実行され → 今回は`repair_outcome: "no_change"`（Rejudge後も
  needs_repairのまま）→ `repair_accepted: false`、新規Turn非作成、
  という一連の実Pipelineが実際にEnd-to-endで動作することを実Server上で
  確認した（Improved以外は新規Turnを作らないという設計どおりの挙動）。
判定: CLOSED（上記の重大Bugを実Hardware検証で発見・修正・再検証まで
  完了した。これは本Second Reworkが実施した中で最も重大な発見であり、
  「Grouped PASS判定では検出不能で、個別の実機検証によってのみ
  発覚した」実例である。）
```

### P6-CODEX-003（Raw Status Code）

```text
事実: `frontend/src/App.tsx`の2箇所（旧`setStatusKey("errorStatus", {code:...})`、
  Status行に生Codeを`"Error: {code}"`Templateで埋め込んでいた）を
  `setWarningStatus(code, message)`（既存の`translatedServerMessage()`経由Path）
  へ置換した。`frontend/src/i18n/translations.ts`から未使用となった
  `errorStatus: "Error: {code}"`（ja/en）を削除した。
  さらに`frontend/src/lib/persistentDetailProjection.ts`の
  `knownMessageText()`／`translatedServerMessage()`を、`isSafetyRejectCode()`
  （既存の`guardrail_*`/`governance_*` Prefix判定）による未列挙Code用の
  Fallbackを実際に使うよう修正した（従来はDefineされているのみで未使用だった）。
  Test: frontend/src/lib/persistentDetailProjection.test.ts（新規3件）、
  frontend/src/App.test.tsx（既存分含め全Pass）。
判定: CLOSED（Status行・Chat Bubble本文の両方でRaw Codeが露出する経路は
  発見時点で存在した2箇所とも修正済み。ただし全経路の悉皆的網羅は
  静的Grep＋既存＋新規Testに基づくものであり、実Browser Live/Persistent/
  Reload全経路の目視確認は本文書作成時点で未実施。）
```

### P6-CODEX-004（Recording非直交性／Writer境界）

```text
事実: `LocalFilesystemRecordingWriter`
  （src/margpa_runtime_llm/adapters/runtime_observability/local_filesystem_recording_writer.py）
  を以下の点で強化した。
  (a) request_idを`^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$`で検証し、`/`／`..`／
      絶対Path様の値を`RecordingPathRejected`で拒否。
  (b) base_dirがSymlinkである場合、またmkdir後にSymlink／非Directoryへ
      化けていた場合を`RecordingPathRejected`で拒否。
  (c) 既存同名Fileへの上書き時、Quota計算から旧Fileのサイズを正しく除外
      （二重計上の是正）。
  (d) 書き込みFile自体とDirectory Entryの両方に`os.fsync`を適用
      （Atomic Renameのみでは実Durabilityとして不十分という指摘への対応）。
  (e) 置換先が既にSymlink／非通常Fileである場合を`RecordingPathRejected`で拒否。
  Test: tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
      （19件、Traversal／Symlink／Quota置換／fsync呼び出しSpy／非通常File拒否を含め全Pass）。
  さらにRecordingをJudgeから完全に分離した新規`bootstrap/recording_live_integration.py`
  を実装し、`ConversationGenerationSession._completed_event()`から独立した
  `RecordingCompletionHook`として直接呼び出す構成へ変更（詳細はP6-CODEX-011節）。
判定: CLOSED（指摘された5点の脆弱性はいずれも実装・Test済み。）
```

---

## 2. 個別Acceptance ID 再判定（一件ずつ、Grouping不可）

```text
P6-ACC-008（TurnへExact Model／Artifact／Backend／Config）
  判定: PASS
  根拠: `ConversationTurnProvenance`（conversation/domain/models.py）を新規追加し
    `ConversationTurn.provenance`（Optional、無Migration）へ格納。
    `ConversationGenerationSession._completed_event()`が
    `data["attempt_provenance"]`（model_identity/backend_key/backend_version/
    artifact_digest_sha512/context_size）を実際のModelRuntimeInfoから構築し、
    `PersistentConversationService._generate_pending_turn()`が
    `_decode_attempt_provenance()`経由でTurnへ永続化する。
    Repair生成のAttemptにも同じProvenanceを付与（repair_live_integration.py）。
    Test: tests/unit/conversation/test_conversation_generation_attempt_provenance.py（3件）、
    tests/unit/conversation/test_persistent_attempt_provenance.py（4件、実SQLite
    Round-trip含む）、tests/unit/bootstrap/test_repair_live_integration.py内
    test_accepted_repair_turn_also_carries_real_attempt_provenance。

P6-ACC-017（Judge OBSERVEでCanonical Answer不変／後続TurnへのModel Busy波及なし）
  判定: PASS
  根拠: 前Reworkで解決済みの同一Turn自己衝突Fixに加え、本Reworkで
    ModelAccessCoordinatorがMain-vs-Background競合の実質的な発生窓を縮小
    （§1 P6-CODEX-001参照）。JudgeがOFF時はHook冒頭で即Returnし
    EvaluationCase／Prompt／Model Callを一切構築しない
    （test_judge_off_never_calls_the_model）。
    実Hardware検証: §1 P6-CODEX-001に記載のとおり、実Server／実Browser／
    実main.qwen3-4b-q4-k-mでJudge=observeを実際に適用し実Chatを送信、
    Canonical Answer（Chat Bubble表示内容）がJudge実行の有無に関わらず
    Byte-identicalであることを目視確認した（Judge実行中もChat応答自体は
    即座に完了しUserを待たせない）。後続Requestへの`model_busy`波及は
    確認した2 Turn（observe/enforce各1回）では発生しなかった。

P6-ACC-021（Prompt／Rubric／Model／Seed／Config Digest追跡）
  判定: PASS
  根拠: `build_judge_evidence_recorder()`（recording_live_integration.py）が
    Judge Run完了ごとに独立Evidence File
    （`<request_id>-judge-evidence.json`、Turn本体のRecordingとは別Writer/
    別Directory）へ、model_identity／judge_role／rubric_id／
    prompt_digest_sha512（生Promptは非保存、Digestのみ）／recommendation／
    confidence／token_usage／latency_ms／execution_state／
    seed_pinned・seed（未Pin時は正直に"unpinned"）／config_digest_sha512
    （Rubric/Criteria/MaxNewTokensのCanonical JSON SHA-512）／
    cost_estimate_available:false（金銭Costは本環境で算出不能なため
    明示的Unavailable、捏造しない）を記録する。Repair実行時は
    repair_outcome／repair_accepted／repair_new_turn_idも同封する。
    Test: tests/unit/bootstrap/test_recording_live_integration.py（7件）、
    tests/unit/bootstrap/test_judge_live_integration.py内
    test_judge_evidence_recorder_is_actually_invoked_with_real_provenance
    （実際にHookから呼ばれ、実Fileが書かれることをEnd-to-endで実証）。

P6-ACC-026（Repair OBSERVEで追加Generation 0）
  判定: PASS（本Rework中に発見・修正した実Bug）
  根拠: `resolve_repair_eligibility()`はOBSERVEをENFORCEと同一に分類する
    （OFFのみ除外する）純粋なClassification関数であり、これ自体は仕様として
    妥当だが、`judge_live_integration.py`の呼び出し側がEligibility判定のみで
    Repair Executorを実行しており、Repair Mode=OBSERVEでも実際に
    Repair候補生成＋Rejudgeの2回の追加Model Callが発生し得る状態だった
    （既存Testはいずれも repair_executor 未指定か Mode=ENFORCEの組み合わせのみで、
    この経路は未Testだった）。本Reworkで呼び出し側に
    `repair_mode is RepairMode.ENFORCE`の明示Gateを追加し、Eligibility自体は
    引き続き計算・Status表示用に保持（OBSERVE下でも"eligible"という正直な
    分類は維持、"not eligible"への捏造はしない）。
    Test: tests/unit/bootstrap/test_judge_live_integration.py内
    test_repair_observe_never_invokes_the_executor_zero_additional_generation
    （Fix前提でCall回数0とEligibility="eligible"の両方を検証）。

P6-ACC-035（Request／Turn／Generation／Judge／Repair相関）
  判定: PASS
  根拠: `PersistentConversationService.locate_request()`（process-local、
    best-effort、Source of Truthではないと明記）がrequest_idから
    (conversation_id, turn_id)を解決し、Repair実行がこれを用いて
    正しいTurnへAttemptを追加する。Judge Evidence Fileのrequest_idは
    Turn自体のrequest_idと共有Prefixを持つため、Turn record・Turn-level
    Recording File・Judge Evidence Fileの3者はrequest_id経由で相関可能。
    Test: tests/unit/bootstrap/test_recording_live_integration.py内
    test_judge_evidence_never_collides_with_the_turn_level_recording_file。

P6-ACC-036（Current Requestへ過去Point結果混在0）
  判定: PASS（Judge/Recordingの範囲。Turn自体のUI Stateは別途P6-ACC-038参照）
  根拠: `JudgeGovernanceComposition.current_state()`が
    idle/running/completedを保持し、running中はlast_result()が別Turnの
    ものである可能性をAPI Response自体が`state`Fieldで明示する
    （feature_modes_routes.pyの`JudgeModeSnapshotResponse.state`）。
    Frontend（FeatureModesPanel.tsx）はstate==="running"時、last_resultに
    "(from a previous Turn — a Run is currently in flight)"を明示表示する。
    Test: tests/integration/web/test_feature_modes_routes.py内
    test_status_projects_a_real_judge_result_including_repair_fields、
    frontend/src/components/FeatureModesPanel.test.tsx内
    "a stale last result while a Run is in flight is labeled as such"。

P6-ACC-037（未実行PointをTyped not-invoked表示）
  判定: PASS
  根拠: JudgeがOFFならHookは即Returnし`composition`へ何も記録しない
    （current_state()は"idle"のまま、last_result()はNone）。
    Background Task Slotが埋まっている場合は`start_background()`がFalseを
    返し、`composition.mark_skipped()`で明示的にidleへ戻す
    （黙って何もしない、ではなく"Skipされた"という状態遷移として記録）。

P6-ACC-038（State遷移とTerminal一意）
  判定: PARTIAL（Judge/Repair Composition側はPASS、Chat UI自体のTurn内
    Live State MachineはP6-OBS-004の全State
    idle→preparing→guarding→generating→judging→repairing→rejudging→...
    のうちpreparing/guardingのみ実装済み、judging/repairing/rejudgingは
    未実装のまま）
  根拠（達成分）: `ConversationGenerationSession.events()`が新規に
    STATUS(state="preparing")をTurn開始直後、STATUS(state="guarding")を
    Guardrail/Governance Pre-check直前に発行する（既存のSTART/STATUS
    Eventの意味は一切変更せず、純粋加算）。Frontend（App.tsx）は
    これらを翻訳済みStatus文言として表示する。
    Test（Backend）: tests/unit/conversation/、tests/integration/conversation/、
    tests/integration/documentation_rag/、tests/integration/web/test_web_app.py
    内の関連Testを本Reworkで全て新Sequenceへ更新し全Pass（1494件）。
    Test（Frontend）: frontend/src/App.test.tsx内
    "preparing/guarding STATUS events before start are handled..."。
  未達成分（正直な残課題）: JudgeがChatの同一SSE接続内で"judging"/
    "repairing"/"rejudging"へ遷移する仕組みは実装していない。これは
    Judge/RepairがTurn完了後の非同期Background Taskであるという
    既存Architecture（Judge OFF/OBSERVEはCanonical Behaviorに一切影響
    しないという既存不変条件、ADR-6-013）と両立させるため、同一SSE
    接続を保持したままJudge/Repairの完了を待つ設計variant（Turn応答を
    遅延させる）は採用していない。代わりに`/api/v5/feature-modes/status`
    （Polling可能な別APIとして今回新規に`judge.state`/`judge.last_result`/
    `recording.last_outcome`/`recording.judge_evidence_last_outcome`を
    実装、FeatureModesPanel.tsxで実際に表示）でJudge/Repair/Recordingの
    Current Stateを観測可能にした。これはP6-OBS-004の「Observability」
    という意図には実質的に応えるが、「同一Chat Bubble上でのLive視覚遷移」
    という文字通りの要求までは満たしていない。

P6-ACC-039（Subscriber Failureで成功捏造0）
  判定: PASS（Recording／Judge Evidence Writer失敗の範囲）
  根拠: `RecordingCompositionState`が`record_ok()`/`record_degraded()`を
    分離し、Writer失敗（RecordingWriteFailure/RecordingQuotaExceeded/
    RecordingPathRejected）を`ok=False`＋具体的`degraded_reason`として
    記録する（黙って握り潰さない、成功と誤表示しない）。
    Test: test_a_write_failure_degrades_the_composition_state_instead_of_raising。

P6-ACC-041（Raw Error CodeでなくJA／EN Safe Refusal）
  判定: PASS（§1 P6-CODEX-003参照）

P6-ACC-049（Atomic Write／Quota／Failure／Degraded）
  判定: PASS（§1 P6-CODEX-004参照）

P6-ACC-053（Main／Guard／Judge／Governance Layerを別Row表示）
  判定: PASS（変更なし、既存実装を再確認。4種のIdentityは
    `component_identity_projection.py`の別々の関数・別々のPydantic型で
    Projectionされ、Route側（runtime_model_control_routes.py）でも
    別々のFieldとしてResponseへ格納されている。）

P6-ACC-054（Guard Model NoneとGuardrail Modeを混同0）
  判定: PASS（変更なし、既存実装を再確認。`project_guard_model_identity()`は
    Guardrail Modeを一切引数に取らず、model_id/exact_revision/
    artifact_digest_sha512のみから独立にState導出する。）

P6-ACC-055（Governance LayerはManifest／Digest／Bindingから導出）
  判定: PASS（本Reworkで是正）
  根拠: 従来`runtime_model_control_routes.py`の`_project_status()`は
    Governance Layer Identityを`request.app.state.governance_definitions_runtime`
    （Phase 3の独立したPackage閲覧用Control Surface）から導出しており、
    Phase 4 Runtime Governanceが実際にDefinitionsをBindしていても、
    Phase 3側Flagが無効ならNoneを表示するという事実と異なる隠蔽が
    起きていた。本Reworkで、実際にBind済みのPhase 4
    `WebRuntime.runtime_governance_composition.source_plan_id`/
    `.source_plan_digest_sha512`（`load_reference_descriptors()`が
    検証済みPackage Readから確立した実Plan Identity）から導出するよう
    修正した。
    Test: tests/integration/web/test_runtime_model_control_governance_layer_identity.py
    （2件、Phase 3 State完全不在下でPhase 4実BindingがACTIVE表示される
    Regression Testと、Phase 4未Enable時にNone表示されるTestの両方）。

P6-ACC-056（None／Unavailable／Invalid／Loading／Degraded／Active区別）
  判定: PARTIAL→大部分PASSへ是正
  根拠: `project_governance_layer_identity()`／`project_guard_model_identity()`
    に、package_id/model_idが存在してもDigestが欠落する場合を`INVALID`
    として明示するBranchを追加した（従来はDigest欠落でも無条件でACTIVEに
    分類していた）。
    Test: tests/unit/runtime_observability/test_component_identity_projection.py内
    test_governance_layer_identity_is_invalid_when_package_id_present_without_a_digest、
    test_guard_model_identity_is_invalid_when_model_id_present_without_a_digest。
  残課題: Main Model Identityの`LOADING`/`DEGRADED`/`UNAVAILABLE`は
    既存の`RuntimeState`由来Mappingで従来通りCoverされているが、
    6状態すべてを一つのMatrixとして4 Identity×6 Stateの全24組み合わせを
    横断的に検証するTestは本Reworkでは新設していない（個別Identityごとの
    部分的Coverageに留まる）。

P6-ACC-073〜076（Compaction Recovery／5時間Quota再開／Subphase報告／
  False Completion分類）
  判定: 再評価スコープ外（本文書はCode/Test Evidenceに基づく技術的
    Acceptance再判定であり、これら4件はSession運用そのものの記録に
    関するものである。本Second Rework Session自体が、Second Independent
    Review Handoffで指示された全Work Unitを連結実行中であり、Compaction
    後もこのGovernance文書作成まで一貫して継続している。個別のQuota
    再開／Subphase報告Timelineに関する具体的Evidence追記は、本文書の
    主目的であるP6-CODEX-009〜016の技術的Closureとは別軸のため、
    最終Handoff側で扱う。）

P6-ACC-077（未許可Root外／Provider Memory／Git Mutation／Network／
  User Data違反0）
  判定: PASS（本Rework期間中の新規Incident0件）。P6-GOV-001記録の
    既存3件はPhase全体のIncidentとして引き続き有効（Scopeを「本Rework
    期間中のみ」へ縮小しない、Second Reviewの明示的指摘どおり）。
    本Rework中のGit Mutation: 0（git add/commit/push等は一切未実行）。
    Root外Read/Write/Execute: 0（全編集はProject Root配下、Test Temporary
    RootもすべてTMPDIR="$PWD/.venv/.t"配下）。User実runtime_data接触: 0
    （全Testは`tmp_path`Fixture配下の使い捨てSQLite/Recording Directory
    のみを使用）。
```

---

## 3. 未完了・NOT_EXECUTEDのまま記録する項目（隠蔽しない）

```text
P6-CODEX-016（Calibration／Qwen Governance/Guardrail/Judge/Repair
  OFF/OBSERVE/ENFORCE比較実験一式）:
  NOT_EXECUTED。実LLM（Qwen3-4B）に対する多数回の実推論を要する
  Position/Verbosity/Language/Self-preference/Confidence/
  Deterministic-Conflict Calibration Matrix、Accuracy Candidate/
  Unsupported Claim/Definition Confusion/Abstention/Over-refusal/
  Repair-Improved-vs-Worse比較、分離Token/Latency/Model-Call/
  Repair-count/Recording-Byte Metricsは、本文書作成時点で一切実施
  していない。Max New Tokens実UI Apply（Model Reload 0）のCall Spy
  実証も未実施。

P6-CODEX-012の一部（Chat UI自身のTurn内Live State Machine）:
  上記P6-ACC-038参照。preparing/guardingはLive実装済み、
  judging/repairing/rejudgingは別APIのPolling経由観測に留まる。

Real Browser Golden Path（Judge-OBSERVE＋Repair-ENFORCE、実Qwen3-4B
  Server相手）:
  中核部分は本文書作成時点までに実施・PASS済みへ更新する
  （§1 P6-CODEX-001の実Hardware発見・修正・再検証を参照）。
  実施済み: 実Server起動（main.qwen3-4b-q4-k-m実Load）、実Browser経由の
  実Chat発話2回（Judge=observe 1回、Judge=enforce＋Repair=enforce 1回）、
  Judge実行・Judge Evidence実File書き込み・Recording実File書き込みの
  実確認、Repair Eligibility→候補生成→Rejudge→Outcome判定→
  Accept/Reject（今回はno_change/未採用）という実Pipeline全体の
  End-to-end動作確認。
  未実施のまま残るもの: Repairが実際にIMPROVED（採用・新規Turn作成）
  となるCaseの実確認（今回試行した1件はno_changeで終わった）、
  Retry/Regenerate/Branch/Citationとの実組み合わせ確認、Mobile幅／
  Keyboard・Focus操作、Settings Cross-tab同期の実Browser確認、
  Max New Tokens実UI Apply＋Model Reload 0のCall Spy実証。
```

## 総括

```text
本Rework（Second Rework）で技術的にClosedと判定できたのは:
  P6-CODEX-001／003／004（再Open分）、P6-CODEX-009／010／011／013／014／015
  （新規指摘8件のうち6件）、およびP6-GOV-002個別Acceptance ID群のうち
  P6-ACC-008/017/021/026/035/036/037/039/041/049/053/054/055（大部分）/077。
  このうちP6-ACC-026は、本Rework中の再監査によって初めて発見された
  実際のBug（Repair OBSERVE下での意図しない追加Generation）であり、
  「Grouping/一括PASSでは見逃されていたはずの欠陥」を個別再判定によって
  実際に捕捉・修正できたことを示す。

  さらに重要な追加事実として、§1 P6-CODEX-001に記載のとおり、実Server
  （main.qwen3-4b-q4-k-m）＋実Browserによる実Hardware Golden Path検証中に、
  「JudgeがModeに関わらずあらゆる実Turnで一度も実行されていなかった」
  という、全1494件のFake Inference Unit/Integration Testでは検出不能
  だった重大Bugを発見・特定・修正し、修正後に同一実Server／実Browser／
  実Modelで再検証してJudge実行・Judge Evidence実File書き込み・
  Recording実File書き込み・Repair実Pipeline（Eligibility→候補生成→
  Rejudge→Outcome判定→Accept/Reject）のEnd-to-end動作を実際に確認した。
  これは「実装したはずのものが実際には一度も動いていなかった」という、
  Test Coverageの見た目の充実だけでは検出できない種類の欠陥であり、
  実Hardware検証を省略しなかったことで初めて捕捉できたことを明記する。

技術的に未Closedのまま残るのはP6-CODEX-012の一部（Chat UI Live
  judging/repairing/rejudging）、およびP6-CODEX-016（Calibration一式）
  である。実Browser Golden Pathの中核（Judge-OBSERVE実行確認、
  Repair-ENFORCE実Pipeline確認）は上記のとおり実施・PASS済みへ更新した。
  残る2項目は「実装不可能な真のBlocker」ではなく、「実LLM推論を伴う
  長時間の追加作業」および「既存Architecture不変条件（Judge OFF/OBSERVEは
  Canonical Behavior不変）との両立を優先した設計選択の帰結」である。
  この区別を偽らないため、本Second ReworkはこのGovernance Correction
  作成の時点ではComplete Candidateを宣言せず、継続作業中である。
```
