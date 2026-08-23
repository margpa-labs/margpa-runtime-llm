# Phase 6 Third Rework — Acceptance ID個別再判定（Append-only、Required Rework Sequence Step 8）

```yaml
document_id: phase_6_third_rework_acceptance_rederivation
status: append_only_evidence
phase: phase_6
work_unit: required_rework_sequence_step_8
role: Claude側設計統括者役
created_at: 2026-08-23 18:30:00 JST
authority: phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
baseline: docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md
prior_individual_rederivation: docs/project/phases/phase_6/history/operations/phase_6_governance_evidence_correction_ja_20260823105500.md（P6-GOV-002）
```

## 0. 本文書の方法論（正直な範囲宣言）

Third Reviewは「Acceptance IDを1件ずつ再判定する」ことを要求している。
本文書は全79件＋補助ID（012A/012B/024A/044A/077A）を、以下3種類に分類して
個別に扱う。**「全件を今回改めて実機再実行した」という主張はしない**——
それは事実に反する。

```text
[A] THIRD_REWORK_NEW_EVIDENCE:
    本Third Rework（P6-CODEX-017〜024の実装）で直接変更されたSource／
    Testに対応するIDであり、本Reworkの中で新規に取得したSource／Test／
    実機Evidenceに基づき再判定する。
[B] CARRIED_FORWARD_FROM_GOV_002:
    本Third Reworkで変更していないSource／Testに対応するIDであり、
    P6-GOV-002（Second Rework、2026-08-23 10:55:00 JST）が既に個別ID
    ごとに実施したCLOSED判定を、変更なしとして引き継ぐ。P6-GOV-002本文へ
    参照する（本文書内に再転記しない）。
[C] STILL_OPEN:
    本Third Reworkでも未解決、またはP6-GOV-002時点でPARTIAL／
    NOT_EXECUTEDのまま残っているID。
```

## 1. Model／Runtime Control（P6-ACC-001〜012B）

```text
分類: [B] CARRIED_FORWARD_FROM_GOV_002（全件）
理由: 本Third ReworkはModel Switch／Context Size／Max New Tokens関連の
  Sourceを変更していない。P6-GOV-002が個別に確認済みの判定をそのまま
  維持する。
```

## 2. Evaluation／Judge（P6-ACC-013〜024A）

```text
[A] P6-ACC-008（TurnへExact Model／Artifact／Backend／Config）:
  CLOSED（新規）。P6-CODEX-023修正により、conversation_generation.py
  _generation_config_digest_sha512()が実際にGeneration Config Digestを
  計算しattempt_provenanceへ格納、persistent_conversation_service.py経由
  でConversationTurnProvenance.generation_config_digest_sha512へ実際に
  永続化されることを、tests/unit/conversation/
  test_conversation_generation_attempt_provenance.py（Digest変化Test含む）
  およびtest_persistent_attempt_provenance.pyで確認。Repair側も独立
  Digest（role=repair）で同様に修正（repair_live_integration.py
  _repair_generation_config_digest()）。以前のP6-CODEX-023指摘
  （「実際には保存されない」）は解消。

[A] P6-ACC-016（Judge OFFで追加Call／Mutation 0）:
  CLOSED（新規）。judge_live_integration.pyのhook()が、Judge OFF時
  mark_skipped(reason="judge_off")のみを呼び、Model Callを一切発生させ
  ないことを、test_judge_off_never_calls_the_model他で確認。加えて
  Calibration Harness実行（Mode Matrix、judge=off）でも実Model環境で
  Call発生0、composition.current_state()="queued_or_skipped"を確認。

[A] P6-ACC-019（LLM Judge Typed Decode／Unknown Fail-closed）:
  CLOSED（新規、範囲拡張）。judge_live_integration.py _run_judge_and_
  repair()を全体Try/Exceptで囲み、Prompt構築／Budget／Repair Executor／
  Evidence Recorder等、Model Call以外の例外もTyped Failure（execution_
  state="failed"）へ収束することを、
  test_unhandled_exception_anywhere_in_the_run_still_reaches_a_terminal_state
  で確認。

[A] P6-ACC-020（Same Artifact JudgeをIndependentと表示0）:
  CLOSED（維持、新規確認）。LiveJudgeResult.judge_role・Judge Evidence
  Fileのjudge_role Fieldとも一貫して"main_self"（JudgeIndependenceClass.
  MAIN_SELF）を記録することを、実機Judge Evidence File
  （3cca3893-...-judge-evidence.json、judge_role: "main_self"）で
  直接確認。

[A] P6-ACC-021（Prompt／Rubric／Model／Seed／Config Digest追跡）:
  PARTIAL→ほぼCLOSED（新規）。実Judge Evidence Fileで
  prompt_digest_sha512・rubric_id・config_digest_sha512・seed_pinned
  （+ artifact_digest_sha512／backend_key／backend_version、P6-CODEX-022
  修正分）を実値で確認。Seedは意図的に未固定（seed_pinned: false）で
  あることを正直に記録——これはBugではなくGap（決定論的Decodingを現状
  要求していないため）として明示する。

[A] P6-ACC-022（Position／Verbosity／Language／Self Bias比較）:
  PARTIAL（新規、前進あり）。scripts/models/phase_6_calibration_
  harness.pyにより、Position Bias（2 Fixture、順序反転）・Self-preference
  Bias（1 Fixture、Blind／Labeled）を新規に実施（phase_6_calibration_
  harness_results_ja_20260823180000.md参照）。ただし独立Judge Model
  との突合・真の第三者著作Corpusとの比較はDeferred（Model Artifact
  調達がAllowed Mutation Envelope外のため）。PARTIALのまま正直に維持
  するが、Second Rework時点（この2次元が完全に未実施）からは前進した。

[B] その他（013〜015, 017, 018, 023, 024, 024A）: CARRIED_FORWARD_FROM_
  GOV_002。
```

## 3. Repair（P6-ACC-025〜034）

```text
[A] P6-ACC-026（Repair OBSERVEで追加Generation 0）:
  CLOSED（維持、Second Reworkからの既存修正）。judge_live_integration.py
  の呼出側Gate（repair_mode is RepairMode.ENFORCE明示Check）は本Third
  Reworkでも変更なく維持。テストで再確認。

[A] P6-ACC-027（Repair ENFORCEはRegistry／Authority／Budget内だけ）:
  CLOSED（新規、強化）。repair_live_integration.pyのBudget実施行使
  （LIVE_REPAIR_BUDGET.max_total_model_calls=2、実Call数と一致）、
  test_budget_exhausted_before_rejudge_blocks_the_second_model_call
  および test_default_live_budget_allows_exactly_the_two_real_calls_
  repair_makes で、宣言Budgetと実Enforcementが一致することを確認
  （Second Rework時点のP6-CODEX-021指摘=不一致、は解消）。

[A] P6-ACC-029（Repair CandidateがPhase 4／5全Point再通過）:
  CLOSED（維持、新規確認強化）。Governance/Guardrail Post Hookの
  Fail-closed化（例外時should_reject=True）を
  test_governance_post_hook_exception_is_fail_closed_and_marked_degraded
  他で確認。以前のFail-open Bug（例外時should_reject=False）は解消。

[A] P6-ACC-030（Max Attempt／Time／Token／Call／Depth有界）:
  CLOSED（新規）。P6-ACC-027と同一Evidence。Wall Time／Token実測・
  Call数実測をtest群で確認。

[A] P6-ACC-033（Ghost Completion／Double Terminal／Uncommitted
  Completed 0）:
  CLOSED（新規）。3-step永続化Chain（append_derived_turn→
  start_generation→complete_generation）の各失敗Pointで、
  fail_generation()によるBest-effort補償を
  test_persistence_failure_at_start_generation_marks_the_orphan_turn_failed
  および...at_complete_generation...で確認——孤立PENDING/GENERATING
  Turnが実Storeで解消されFAILEDへ遷移することを直接確認。

[B] その他（025, 028, 031, 032, 034）: CARRIED_FORWARD_FROM_GOV_002。
```

## 4. Observability／Presentation（P6-ACC-035〜043）

```text
[A] P6-ACC-035（Request／Turn／Generation／Judge／Repair相関）:
  CLOSED（新規、強化）。JudgeGovernanceCompositionのcurrent_request_id()
  が、Judge OFF・Model Busy・実行中・完了のいずれの状態でも一貫して
  現在Turnと相関することを、mark_skipped()のRequest Identity相関化
  （P6-CODEX-020）およびFrontend側MessageList/MessageBubbleの
  requestId相関Test（8件）で確認。実Browserでも、Page Reload後も
  request_id相関が維持されることを確認済み（Persistent Turn Response
  のrequest_id Fieldを新規消費する形で修正）。

[A] P6-ACC-036（Current Requestへ過去Point結果混在0）:
  CLOSED（新規）。mark_skipped()がOFF Mode／Busy Skipいずれでも
  current_request_idを更新するようになったため、
  test_hook_marks_skipped_and_correlated_when_judge_mode_is_off で、
  過去Turnの完了結果が後続のOFF Turnで「現在の結果」と誤認されないこと
  （current_request_id不一致で判別可能）を確認。Second Rework時点の
  Gap（OFF時にcomposition更新自体が起きない）は解消。

[A] P6-ACC-037（未実行PointをTyped not-invoked表示）:
  CLOSED（新規、拡張）。JudgeRunStateへqueued_or_skipped／cancelled／
  degradedを追加、FeatureModesPanelのUnion型・Label表示も追従。

[A] P6-ACC-038（State遷移とTerminal一意）:
  PARTIAL→大部分CLOSED。Chat Surface自体でのjudging/repairing/
  rejudishingの個別粒度可視化はScope限定（judging実行中は単一の
  "running"表示、Repair内部の細分状態はChat Surfaceでは意図的に非表示、
  Feature Modes Panelでのみ全State表示）——これは意図的な、開示済みの
  Scope選択であり、隠蔽ではない（MessageBubble.tsx judgeBadgeLabelKey()
  のCommentで明示）。Terminal State自体の一意性（Run全体のTyped
  Terminal Boundary化）はCLOSED（P6-CODEX-020修正、Test多数で確認）。

[A] P6-ACC-039（Subscriber Failureで成功捏造0）:
  CLOSED（維持、新規確認）。Recording HookはRecordingWriteFailure等を
  RecordingCompositionStateのDegraded projectionへ変換し、Canonical
  Turnには一切影響しないことを既存Test群およびP6-CODEX-022の新規Test
  （fcntl Lock取得失敗のRecordingWriteFailure化等）で確認。

[B] その他（040〜043）: CARRIED_FORWARD_FROM_GOV_002。
```

## 5. Feedback／Recording（P6-ACC-044〜051）

```text
[A] P6-ACC-049（Atomic Write／Quota／Failure／Degraded）:
  CLOSED（新規、大幅強化）。P6-CODEX-022の5項目修正
  （Short Write完全書込みLoop化、containment_root経由の中間Path
  Symlink検査、Age-gated Orphan Temp Pruning、fcntl.flock経由の
  Cross-process直列化、既存Entry Hardlink/Symlink Fail-closed化）を
  全て新規Test（28件、うち9件新規）で確認、かつ実Server・実Browser・
  実Model環境でも実際にRecording FULL成功（ok:true）、Judge Evidence
  File内へArtifact Digest／Backend Identity実値記録を確認。

[B] その他（044, 044A, 045〜048, 050, 051）: CARRIED_FORWARD_FROM_
  GOV_002。
```

## 6. UI／Identity（P6-ACC-052〜063）

```text
[A] P6-ACC-053（Main／Guard／Judge／Governance Layerを別Row表示）:
  CARRIED_FORWARD_FROM_GOV_002（Source変更なし）。

[A] P6-ACC-056（None／Unavailable／Invalid／Loading／Degraded／Active
  区別）:
  PARTIAL（維持）。Judge Run Stateの区別自体は本Third Reworkで拡張
  （idle/queued_or_skipped/running/completed/failed/cancelled/degraded）
  したが、Third Reviewが指摘した「4 Identity×6 State横断Matrix」の
  網羅的実機確認は、Time制約により本Reworkでも未実施のまま正直に
  PARTIALとする。

[追加・新規] Chat Surface Live Judge/Repair Badge（P6-CODEX-024固有、
  既存IDに対応なし、新規Acceptance相当）:
  CLOSED（新規）。requestId相関・running/improved/degraded Badge表示・
  Persistent Reload後の相関維持を、Unit Test（MessageBubble 6件、
  MessageList 2件、App.tsx 2件）および実Server・実Browser・実Model
  環境で確認。

[B] その他（052, 054, 055, 057〜063）: CARRIED_FORWARD_FROM_GOV_002。
```

## 7. Compatibility／Experiment（P6-ACC-064〜072）

```text
分類: [B] CARRIED_FORWARD_FROM_GOV_002（全件）
理由: 本Third ReworkはRAG／DeepSeek Compatibility関連のSourceを変更
  していない。
```

## 8. Automation／Governance（P6-ACC-073〜079）

```text
[A] P6-ACC-077（未許可Root外／Provider Memory／Git Mutation／Network／
  User Data違反0）:
  STILL_OPEN、ただし正確な数値へ訂正済み。本Third Rework開始後、
  Claude自身が2件のRoot Boundary事象を自己検知・即時是正した
  （P6-GOV-004: Log Redirect先誤り、P6-GOV-005: cp宛先誤り）。
  Phase 6累積Governance Incidentは6件（P6-GOV-001由来3件＋P6-GOV-003
  1件＋P6-GOV-004／005の2件）。「新規Root外Action 0」を主張することは
  できない——正確には「新規Root外Actionが2件発生したが、いずれもClaude
  自身が同一操作内で自己検知・即時是正し、実質的影響（機微情報漏洩・
  外部Read/Write残存）は0」である。この不一致自体を、隠さず本Acceptance
  ID自体のEvidenceとして記録する。

[A] P6-ACC-078（Stable直書き0、Correction Append-only）:
  CLOSED（維持、新規確認）。本Third Reworkで作成した全Correction
  文書（P6-GOV-003／004／005）はいずれもAppend-only、既存History
  非改変。

[B] その他（073〜076, 079）: CARRIED_FORWARD_FROM_GOV_002。
```

## 9. Manual Acceptance（10項目）

```text
本Third Reworkの範囲では、Claude単独によるManual Acceptance実施は
Third Review §7 Return Contractの対象外（User Real-environment
Acceptanceは別途User自身が行う）。Claude側は実Server・実Browserでの
Golden Path確認（Step 6・Step 7参照）までを担当範囲とする。
```

## 10. 総括

```text
[A] THIRD_REWORK_NEW_EVIDENCE  : 18件（008, 016, 019, 020, 021, 022,
  026, 027, 029, 030, 033, 035, 036, 037, 038(部分), 039, 049, 056(部分),
  077, 078 — 重複含む実数）
[C] STILL_OPEN                 : P6-ACC-022（PARTIAL）、P6-ACC-038
  （Chat Surface細分State非表示、意図的Scope限定として開示）、
  P6-ACC-056（4×6 Matrix網羅未実施）、P6-ACC-077（累積Incident6件、
  0ではない）
[B] CARRIED_FORWARD_FROM_GOV_002: 残り全件
```

Third Review Return Contract §7「必須Acceptanceへ`PARTIAL／NOT_EXECUTED／
UNVERIFIED`がない」という条件は、**本文書時点ではまだ満たされていない**
——P6-ACC-022・038・056がPARTIALのまま残る。これらは実装不能なBlockerでは
なく、追加のCalibration拡張（独立Judge Model等、Deferred済み）または
追加のUI／実機確認Timeの不足によるものであり、Third Reviewの枠組みでは
「Controller-owned Followup」として、既存Frozen Architecture内で追加
実施可能なWorkである。次Stepでの対応方針は、Complete Candidate Handoff
自体に明記する。
