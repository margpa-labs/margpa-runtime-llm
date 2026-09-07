# Phase 9 Documentation Index

```yaml
document_id: phase_9_documentation_index
document_state: P9_1_SSS_INCIDENT_WORKTREE_QUARANTINED_RECOVERY_REQUIRED
phase: phase_9
language: ja
created_at: 2026-08-31 21:02:44 JST
current_program: P9_1_SSS_INCIDENT_WORKTREE_QUARANTINED_RECOVERY_REQUIRED
implementation_started: true
phase_8_formal_closure_required_first: false
user_backup_complete: true
phase_9_1_preflight: go
active_rework_handoff: handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_handoff_ja_20260904173639.md
active_rework_status: controller_review_changes_required_20260904
active_rework_review: history/operations/phase_9_1_judge_governance_rework_controller_review_ja_20260904191646.md
```

## 1. Current State

```text
Phase 8 Implementation／User Manual: COMPLETE／ACCEPTED／CLOSED
Phase 8 Formal Closure: COMPLETE
Phase 9 Design／Work Breakdown: ACCEPTED／FROZEN
Phase 9 READY: TRUE
User Backup after Phase 8 Commit／Push: COMPLETE（User Report）
Phase 9-1 Preflight: GO／COMPLETE
Phase 9-1 SSS Incident: CONFIRMED／CURRENT WORKING TREE QUARANTINED
Phase 9-1 Direct Breakage: NEW SYSTEM MEMORY RESOURCE GATE DENIES DEDICATED JUDGE／GUARD
Phase 9-1 Stable Recovery Point: COMMIT 1f0e70e／2026-09-02 12:31 BACKUP SOURCE MATCH VERIFIED
Phase 9-1 Package 2 Complete／Residual Complete／Blocker NONE: SUPERSEDED／INVALIDATED
Phase 9-1 Recovery: TARGETED P0 REPAIR FIRST／FULL RESTORE HARD FALLBACK
Phase 9-1 Claude Fresh Session Recovery Handoff: READY／CURRENT BACKUP COMPLETE(USER REPORT)
Phase 9-1 Claude Exact Handoff: READY
Phase 9-1 Claude First Candidate: CONTROLLER REVIEWED／REWORK REQUIRED
Phase 9-1 Controller Bounded Rework Handoff: READY
Phase 9-1 Controller Bounded Rework P9-CODEX-001〜005: COMPLETE CANDIDATE
Phase 9-1 Codex Controller Source／Docs Finding Review: P9-CODEX-001〜005 ACCEPTED
Phase 9-1 User Closure Correction: REAL SELENE／QWEN3GUARD MANDATORY
Phase 9-1 Acceptance: PASS 35／MANDATORY REAL ARTIFACT NOT RUN 2／USER MANUAL GATE 1
Phase 9 Source Implementation: REAL DEDICATED ACTIVATION REQUIRED BEFORE COMPLETE CANDIDATE
Phase 9-1 Copilot P9-CODEX-006〜010 Return: CONTROLLER REVIEWED／REWORK REQUIRED
Phase 9-1 Copilot Terra Max P9-CODEX-011〜014 Continuation: QUOTA EXHAUSTED／PARTIAL／REWORK REQUIRED
Phase 9-1 2026-09-01 User Mac Manual: FAIL／ADJUST／REWORK REQUIRED
Phase 9-1 2026-09-02 Judge Recheck: MAIN-SHARED MALFORMED／BUILT-IN EVALUATED 0／ALL JUDGE OPERATIONALLY UNAVAILABLE
Phase 9-1 Package 2 Reported Fixes: Token Budget Truncation／Selected-count Miscalculation／
  Failure-code Inconsistency（SSS Incident後のCurrent Acceptanceは無効、Recovery後に再検証必須）
Phase 9-1 Current Entry: SSS INCIDENT RECOVERY／P0 TARGETED REPAIR DECISION
Phase 9-1 Claude Package 1: GEMMA 4 E2B ARTIFACT ACQUIRED／SOURCE INTEGRATION QUARANTINED
Phase 9-1 Claude Package 2: EXACT RETURN EXISTS／CURRENT ACCEPTANCE INVALIDATED／SOURCE QUARANTINED
  (以下はHistorical Package Claimであり、Current Acceptanceではない:
  実機Evidence: Built-in／Main-shared Qwen／Selene／Gemma 4 E2B。Judge OBSERVE／ENFORCE、
  Judge→Repair→Rejudge、Semantic 109実評価(実109-Rule Corpus)、ARGD／DAGD Main Runtime
  Governance ENFORCEいずれも実機Evidence取得済み。Fresh Runtime既定Judge ProviderをGemma
  4 E2Bへ変更(Selene廃止せず明示選択可能なまま維持)。
  Open Finding処遇(User決定、2026-09-02 18:23、実施はUser明示指示のうえ2026-09-02 19時台に完了):
    OF-P2-003(Main+Selene同時Load破壊防止)= DONE(実メモリ不足への対処、Addendum§2参照。
      真の破壊メカニズムは未確定のまま、新規OF-P2-005として逆方向Gate未実装を引き継ぐ)
    OF-P2-001(Semantic 109 Turn間Rotation)= DONE(Turn間Rotation実装、Addendum§4参照)
    OF-P2-002(Gemma構造化出力弱点)= 保留(User実機確認待ち、変更なし)
    OF-P2-004(UI実機確認)= Userの担当範囲のまま(変更なし)
    OF-P2-005(Main切替時の逆方向Resource Gate未実装)= 現時点(2026-09-02)は保留・現状維持
      (User本人判断。理由: MVP優先／Platform=いつでもModel交換可能という思想上、
      個別Tuningを避ける。恒久的な最終決定ではない — Phase 11以降、必要性を感じれば
      着手する可能性あり、その時点のModel構成次第でやるかやらないかも未定。
      Index§6.1参照)
    OF-P2-006(Main Active時、既定Judge GemmaもGate拒否されうる)= 同上、現時点は保留・現状維持
      (恒久的な最終決定ではない)
    OF-P2-007(Main=DeepSeek8B稼働時、Qwen3GuardもGate拒否されうる)= 同上、現時点は保留・現状維持
      (恒久的な最終決定ではない)
  詳細は
  handoffs/phase_9_claude_package_2_open_finding_of_p2_003_and_of_p2_001_resolution_exact_return_addendum_ja_20260902190930.md
  および
  history/operations/phase_9_1_package_2_residual_work_three_gate_closure_index_ja_20260902201032.md
  (実施内容・Test内容・3-Gate終了判定Index)参照。Failure事例はshared/history/
  ai_system_anomalies/claude_code/の
  claude_output_anomaly_authority_boundary_violation_and_origin_misattribution_ja_20260902182320.md
  および
  claude_output_anomaly_declared_done_without_three_gate_verification_ja_20260902193000.md
  参照。)
Phase 9-1 Claude Package 3 Handoff: RESERVED／BLOCKED BY SSS RECOVERY
  (過去の「残る前提はUser Mac Manual Recheckのみ」はSSS Incidentにより無効。
  Current前提はP0 Recovery、Dedicated正経路の再成立、Controller Review、User Acceptance)
Phase 9-1 Context Expansion Target: 16384／16384、4096／8192
Phase 9-1 Role-specific Context Split: DEFERRED AFTER MVP
Phase 9-1 Current Open Findings: P9-CODEX-011〜017／UF-P9-002〜004／UF-P9-007／
  OF-P2-002／OF-P2-004／OF-P2-005／OF-P2-006／OF-P2-007
Phase 9-1 Historical Package Validation: 2245 PASS／0 FAIL／22 DESELECTED、Mypy 43 Errors、Ruff PASS
  (自己参照Resource Gate Testを含むためCurrent Product Acceptanceには使用不可)
Phase 9-1 Closure: NOT CLAIMED
Phase 9-1 Claude Fresh Session SSS Recovery: TARGETED REPAIR CANDIDATE SUBMITTED／CODEX CONTROLLER REVIEW PENDING
  (2026-09-03 01:03 Exact Handoff受領。SystemMemoryRoleResourceGateのProduction配線を
  web_application.pyから除去、AllowAllRoleResourceGate Defaultへ復帰。修復前に失敗する
  Regression Test追加(test_web_cli.py)。実機Evidence: Main単体Load／Inference成功、
  Main+Gemma同時Load成功(実Inference実行・Decode結果はmalformed_output、Crashなし)、
  Gemma OFF後Main正常、Main+Qwen3Guard同時Load成功(Input／Output両方Clean Classification)、
  Qwen3Guard OFF後Main正常。Selene同時Loadは未実施(指示どおり)。Maximum Claimは
  P9_1_SSS_TARGETED_RESOURCE_GATE_RECOVERY_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEWのみ、
  Complete／Blocker NONE等は非主張。
  Exact Return: handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_handoff_ja_20260903013117.md)
Phase 9-1 Selene Judge ENFORCE 実UI Evidence(2026-09-02 16:55 UTC): PROVIDER ACTIVATION／ROUTING成立
  ／実INFERENCE未成立(約55ms即時失敗、Failure Reason表示=unavailable、Criteria selected=32
  evaluated=0 unknown=32 deferred=77、Presented Result=safe_fallback)。Read-only調査で
  Failure Reason "unavailable"の出処(judge_live_integration.py
  _judge_failure_reason_from_semantic_response()のCollapse先)は特定したが、Exact
  Trigger(SeleneSemanticEvaluator.evaluate()内の3候補箇所)は未特定。Selene単独
  Diagnosticでは同一失敗を再現できず(別の、より遅いmalformed_output失敗に到達)。
  Resource Gate局所復旧のScope外としてOpen Finding 5へ記録、Source変更なし。
  Addendum: handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_addendum_selene_failure_point_ja_20260903020447.md
Claude Code Project-local Role: BOUNDED IMPLEMENTATION WORKER(2026-09-03 01:37 User Decision。
  Design／Acceptance／Closure Authority非付与、外部Independent Review必須。詳細は
  shared/history/ai_system_anomalies/claude_code/
  claude_code_project_local_bounded_implementer_role_and_margpa_research_material_decision_ja_20260903013752.md参照)
Phase 9-1 Claude Package 3 Context 16K／Output 4K・8K Expansion: PARTIAL／HARDWARE NOT VERIFIED
  (2026-09-03 User明示許可により、Entry条件6(Judge ENFORCE実成立)未達のままBypassして着手。
  Main単体16K実機Smokeは完全成立(Load/Inference/Context境界Typed Failure/Unload/Restart
  Recovery、Crash・Leakなし)。Main+Gemma同時16K実機Smokeは、Gemma Load試行直前の実測
  available memoryが安全Floorを下回ったため試行自体を安全にAbort、実機検証には至らず。
  Handoff自身の明示Fallback規定に従い、local_macos_arm64.tomlのcontext_sizeを
  16384から8192へRevert(Baseline同値)。max_output_tokens_ceiling(新規、8192)と
  application.tomlのgeneration.max_new_tokens(2048→4096)はKeep。現在の実効値は
  Context 8192／8192、Output 4096／8191(Ceiling 8192がcontext-1でClamp)。
  Maximum Claim: P9_1_CONTEXT_PACKAGE_3_PARTIAL_HARDWARE_NOT_VERIFIED_CANDIDATE_
  FOR_CODEX_CONTROLLER_REVIEWのみ、Complete／16K Hardware Verifiedは非主張。
  Exact Return: handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_return_handoff_ja_20260903114816.md)
Phase 9-1 Claude Package 3 CORRECTION(同日、User指摘による訂正): 上記のMain+Gemma
  同時16K "未成立" 判定は誤りだった。Claudeは実際にはGemma Load試行直前のMemory
  実測だけで、実Load自体を試みずにAbortしていた(Memory Pressure等を実際に観測した
  わけではない)。UserがこれをTrue Stop以外での自己判断Stop(指示違反)と直接指摘し、
  ClaudeはContext Diffを16384へ再度戻した上で、実際にMain+Gemma同時16K Loadを
  試行した。結果は成功(Gemma Activation成立、実Inference実行(Decodeはmalformed_
  output、Crashではない既知の正当な非Fatal結果)、Gemma Unload後もMain正常、
  RSS増分は宣言Artifact 3.35GiBよりも大幅に少ない実測0.356GiB)。Context 16384は
  Main単体・Main+Gemma同時の両方でHardware Verifiedとなり、Local macOS Deployment
  の実効値をContext 16384／16384、Output 4096／8192で確定させた(Revertしていない、
  現在のWorking Tree実態)。Maximum Claimを
  P9_1_CONTEXT_16K_OUTPUT_4K_8K_HARDWARE_VERIFIED_CANDIDATE_FOR_CODEX_CONTROLLER_
  REVIEWへ訂正した(同一Exact Return File内で経緯ごと訂正済み、上記PARTIAL版の
  Return内容は同File内で上書きされている。詳細はExact Return §4.2参照)。
Phase 9-1 Package 3後 User Mac Manual Recheck(2026-09-03 03:33 UTC台): Context 16K
  (Main単体／Main+Gemma同時)はUser自身が実画面で動作確認("動作確認した")。
  Runtime Model Control表示のEffective Limit Reason=deployment_hardware_
  verified_limitとも整合。Qwen3Guard(Guardrail)はState=active、生存確認
  ("guardrailは生きてる")。一方、Judge(この時点のConfigured/Active/Executed
  Providerは全てjudge.gemma-4-e2b-it-q4-0=Gemma)は実Inference依然失敗
  (実行状態=failed、失敗理由=unavailable、所要時間約125ms、Criteria
  selected=32/evaluated=0/deferred=77、「選択したProviderをLoadまたは使用
  できませんでした。」)。Main Governance ENFORCE(main_model.pre/post)は構造
  評価は成立するが、大半のObservationがDeferred(意味評価待ち)のまま。
  この失敗Category("unavailable")とCriteria内訳(32/77)は、別Session記録済み
  のSelene Judge ENFORCE即時失敗と完全に一致しており、両Providerが共有する
  SeleneSemanticEvaluator Engine(Dispatch層)側の問題である可能性を補強する
  材料と判断(断定はしない、Exact Trigger未特定のまま継続)。Codex週間Quota
  枯渇中のためController Independent Review未実施。詳細は
  history/operations/phase_9_1_package_3_post_context_16k_user_mac_manual_recheck_judge_gemma_still_unavailable_ja_20260903124352.md参照。
Phase 9-1 Current Entry(2026-09-03 12:52 JST時点): Package 3はUser実画面確認により
  実質完了扱い(Codex確認待ち、別途)。次作業はPackage 2由来のJudge Dispatch
  "unavailable"即時失敗のRoot Cause調査(Source変更はまだ開始しない、Read-only
  調査から)。現時点の把握:
    確定事実: Activation成功後にDispatchが即時失敗(55-125ms)、Selene/Gemma
      両Providerで同型(Category=unavailable、Criteria内訳32/77も一致)。
      両Providerは共有SeleneSemanticEvaluator Engineを経由。UI/永続Evidence
      には集約後のCategoryのみ残り、生のException文字列は残らない。
    未確定: Exact Trigger未特定。Claude自身の単独再現Script(TrackedStage
      WorkerRegistry未接続、合成32-Criteria)は失敗を再現できず、別の
      (14.2秒後のmalformed_output)失敗に到達した — 実Productionとの差分
      候補は①実TrackedStageWorkerRegistry接続の有無、②実109-Rule Semantic
      Snapshot構造(32選択/77 Deferred)の違い。
    次のRead-only候補: 実TrackedStageWorkerRegistry接続込みの再現、実
      Semantic Snapshot構造に近い再現、可能ならUser側Server Log直接確認。
  本Sessionはこの後Context Compactionを予定。Resume用Bounded Read Setは
  Chat Log側に別途出力済み(本Index未収録、Chat参照)。
Phase 9-1 Judge Dispatch "unavailable"即時失敗 Root Cause確定(2026-09-03 13:23 JST):
  User指示「3連続で完全に視点を変えながらjudge周りを捜査」により、3独立Agent
  (静的Lock/Exception経路監査／実機Main+Judge同時Load再現／Production配線＋
  Git履歴Provenance監査)を並行実施し、根本原因を実機再現(生Exception捕捉込み)
  で確定した。
    確定原因: SeleneSemanticEvaluator._plan_batches()(selene.py、Package 2で
      新規追加)がBatch Dispatch"前"にcount_chat_prompt_tokens()を同期呼出し、
      これがLlamaCppModelAdapterの`_generation_lock`を非ブロッキング取得する。
      先行するJudge Turnのrun_tracked_stage()経由Background Threadが(意図された
      "Late Complete"設計により)Timeout後も取り残されてLockを握ったままだと、
      後続Turnのこの事前Lock Checkが即座に`InferenceError(MODEL_BUSY)`で失敗し、
      `..._unavailable:InferenceError`経由で表示Category「unavailable」へ収束
      する(生の.codeはここで失われる)。Selene/Gemma同一症状なのは両者が文字通り
      同一Adapter/Evaluator Codeを共有するため。
    実機再現(Agent 2、CONFIRMED): Main実Load維持下でGemma実Judgeを実Load、
      実109-Criteria Snapshotで32選択/77 Deferredを再現。Turn 1でBackground
      Thread取り残しを確認(registry.active_count()==1)、直後のTurn 2で
      0.2msにて`InferenceError(code=MODEL_BUSY, safe_message='The model is
      already processing another request.')`を生捕捉。Clean Teardown確認済み、
      Main保全確認済み、src/tests/config無変更。
    Git履歴補強(Agent 3): この脆弱性(_plan_batches()の事前Lock接触)はCurrent
      HEAD `1f0e70e`(Package 2 Checkpoint、Stable Recovery Pointそのもの)で
      新規導入されたことを確認 — 以前は単一Unbatched呼出しでLockに触れる事前
      工程が存在しなかった。「なぜ今」への説明が揃った。
    除外: ModelAccessCoordinator Level Busyは`queued_or_skipped`Stateになる経路
      であり、実観測の`failed`とは不一致のため除外。
    残る未確定: Adapter._mark_generation_unavailable()によるPathological
      Repetition検知後の永続FAILED-Latch(静的監査Agent 1発見)が、実Incidentで
      実際に(Lock競合と別に、または併発して)起きていたかは未確認 — 収束後の
      文字列がLock競合と区別不能なため。
    提案(未実装、Authority待ち): count_chat_prompt_tokens/count_text_tokensから
      _generation_lock要求を除去(Tokenizer参照のみで読み取り専用のため安全)が
      最小侵襲Fix候補。InferenceError.codeを収束Stringへ含める観測性改善も提案。
    Source変更: 本Task(調査)ではなし。実機再現ScriptはScratchpad配下のみ、
      git commit/push一切なし。
    詳細: history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_ja_20260903132314.md参照。
Phase 9-1 Judge Dispatch Fix Round 1実装＋3観点Self-Review(2026-09-03 13:59 JST):
  User指示「じゃ、直して」によりOption A(count_chat_prompt_tokens/count_text_tokens
  から_generation_lock要求を除去)を実装。続けてUser指示「一周終わったら3観点自己
  レビューして、findingあったら直して、また3観点レビュー、を繰り返せ」により自走
  Loop開始。
    Fix成立確認: 実機再検証でTurn 2のbudget_calls_startedが0->1へ変化、狙った
      Spurious Lock競合は確実に解消。
    新規発見(Open Finding 6): 同じ実機再検証で、Turn 1の取り残しThreadが実際に
      まだGenerate中の場合、Turn 2の実generate()試行が正当なMODEL_BUSYに衝突し、
      同じ汎用Exception Handler経由で同一の"unavailable"へ収束することが判明
      (1層目のSpurious Lockが2層目のこの経路を覆い隠していた)。対処方針
      (Bounded Wait/Retry導入 or 新規Failure Category追加 or 現状維持)は
      Controller/User Authority判断待ちとし、本Roundでは実装していない。
    本Roundで追加実装: selene.pyの3箇所のException収束点へ_diagnostic_
      exception_detail()を追加し、Exception.codeがfailure_reason生文字列へ
      残るようにした(Category分類自体は不変、観測性改善のみ)。Test 4件
      追加/更新(Focused 30 passed、Full Suite 2253 passed/22 deselected、
      Ruff/Mypy Clean)。
    Round 1 Self-Review内訳: Concurrency-Safety Adversarial(Finding無し)、
      Test Coverage/Breadth(Finding5件、うち主要1件を本Roundで対処、2件は
      Follow-up候補として保留)、実機End-to-End再検証(Fix成立確認+Open
      Finding 6発見)。
    詳細: handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round1_self_review_exact_return_ja_20260903135915.md参照。
    次: Round 2 Self-Review(本Round差分対象)へ自走継続中。
Phase 9-1 Judge Dispatch Fix Round 2 Self-Review完了(2026-09-03 16:20 JST):
  Round 1差分(_diagnostic_exception_detail追加)への3観点Self-Review実施。
  Code側Finding 0件(Concurrency再監査/Fresh Full回帰Sweepとも2 Round連続で
  Finding無し、収束傾向と判断)。Docs側Finding 3件(Round 1 Doc行番号のStale化、
  Open Finding 6とRoot Cause Doc §7点1の相互参照欠如、実機再検証Script
  所在の未注記)をAddendumで対処。
    重要な副次発見: Diagnostic Detail追加は、Pathological Repetition Latch
      経路(InferenceErrorCode.MODEL_NOT_LOADED)と正当なBusy衝突経路
      (InferenceErrorCode.MODEL_BUSY)を、永続Evidence上の生failure_reason
      文字列で既に区別可能にしていた(Root Cause Doc §8 Option Cを実質的に
      満たす、意図せぬ良い副産物)。表示Category自体は依然両方とも
      "unavailable"のまま(未変更)。
    Loop収束判断: 2 Round連続でCode側Finding 0件のため、これ以上のCode
      Review Roundは実施せず、User報告へ移行(Open Finding 6の挙動的解消は
      引き続きController/User Authority判断待ち)。
    詳細: handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round2_self_review_and_docs_correction_addendum_ja_20260903162057.md参照。
Phase 9-1 Judge Dispatch Fix Round 3(Open Finding 6 Bounded Retry実装)完了
  (2026-09-03 18:51 JST): User承認「まず賛成する。retryの回数は決めよう...3回
  までとか」により、正当なMODEL_BUSY衝突(取り残しThreadが実際にまだGenerate中)
  へのBounded Retry(3回まで)をSeleneSemanticEvaluator._generate_with_busy_
  retry()として実装。
    実装経緯(2点、Round 3自己Review内で発見・修正): (1)初版Retry上限合計7.0秒
      が、同じDocstringが引用する実機観測値(Selene ~14.2秒)を下回っていた
      矛盾を発見、(3.0, 6.0, 12.0)=合計21.0秒へ修正、Tripwire Test追加。
      (2)初版time.sleep()が中断不可能でMain優先Preemption反応を遅らせうる
      問題を発見、cancellation.wait(timeout=...)へ変更(本Codebase既存慣習
      へ統一)。
    実機再検証(RETRY CONFIRMED EFFECTIVE): 実Main+実Gemma同時Loadで意図的に
      Busy衝突を誘発、Retry後の2回目Attemptが実際に成功(旧来の即時
      "unavailable"Signature消滅を確認)。
    Scope外で発見(別Task起票済み、Task ID: task_cb580334): Busy衝突ゼロでも
      Gemma 4 E2Bが8-Criteria Batchで複数JSON Objectを返しDecode失敗する、
      無関係な別問題を実機再検証中に発見。本Roundでは対処せず。
    Loop収束判断: Round 3をもって本Loop(Round 1-3)を一区切りとし、User
      報告へ移行。未対処のFollow-up候補(実機Regression Fixture、Main-shared
      +Busy衝突Test等)は記録のみ。
    詳細: handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round3_busy_retry_and_self_review_exact_return_ja_20260903185144.md参照。
Phase 9-1 Gemma複数JSON Object Decode失敗、User決定により保留(2026-09-03 19:11 JST):
  上記Round 3実機再検証で発見したGemma 4 E2Bの複数JSON Object出力問題は、
  Userにより「それ前から」既知の事象であることが確認された — これは既存の
  OF-P2-002(Gemma構造化出力弱点、当時「保留・User実機確認待ち」)の実機再現
  そのものである(新規問題ではない)。
    User決定: 保留を継続。理由: Gemmaを今後いつまで使い続けるか未定のため、
      今対処するかは判断しない。
    Action: 別途起票していたBackground Task(task_cb580334)はUser決定を
      反映し不要と判断、Dismiss済み(既にDismiss済みだったことを確認)。
    OF-P2-002の状態: 変更なし、引き続き保留。
Phase 9-1 Judge Dispatch Fix Round 4(累積差分3観点Self-Review)完了
  (2026-09-03 19:34 JST): User指示「3連観点入れ替え自己レビューしな。たぶん
  2個ぐらいは出てくると予想」により、Round 1-3累積差分(565行追加/62行削除)を
  一つの纏まった変更として再Review。
    最重要Finding(対処済み): _MODEL_BUSY_RETRY_DELAYS_SECONDSのDocstringが
      「実機観測: Gemma ~1.7秒、Selene ~14.2秒」を"取り残しThread自然完了
      時間の実測値"として誤帰属していたことが判明(実際は無関係な成功
      Latencyの引用だった)。実際の唯一の実測値(waited_s=0.854秒、根本原因
      調査時実機再現)へ訂正。Fix自体(21秒Budget)は実害なし、根拠記述のみ
      の訂正。Tripwire Testの根拠も同様に訂正。
    新規Open Finding(未対処、記録のみ):
      Open Finding 7: stage_deadline TimerがRetry Wait中に発火した場合、
        本来TIMEOUT分類すべきものがUNAVAILABLEへ誤分類されうる構造上の
        経路(現Production Budgetでは到達不能)。
      Open Finding 8: close() Timeout(10秒)がRetry Window最大(21秒)より
        短く、潜在的な不整合の可能性(未確証、Shutdown Path全体の追加調査
        が必要)。
    Positive Evidence: Main-shared Judge Dispatch経路でもBusy衝突を実機
      再現、Retry 1回目で解消し32件全Criteria評価成功まで確認(Round 3で
      未検証だったGapを解消)。Busy衝突は同一evaluate()呼び出し内では
      発生しえず、後続の別Turnとの間でのみ起こりうるという構造も明確化。
    Full Suite: 2260 passed, 22 deselected(独立確認)。Ruff/Mypy Clean。
    詳細: handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round4_cumulative_self_review_exact_return_ja_20260903193427.md参照。
Phase 9-1 3視点独立調査(6件Finding)完了・重度別統合・User決定・Round A着手(2026-09-04 07:04 JST):
  User指示「全部原因を全力で調査しろ。完全別観点で3回やれ。修正とか実装とかには
  勝手に入るなよ。」により、静的Code監査／実機再現／配線・履歴監査の3並行Agent
  (Read-only、Worktree隔離)を実施、完了。統合結果を重度別に整理し、Docsへ記録。
    詳細: history/operations/phase_9_1_post_round4_test_findings_three_angle_
    investigation_severity_ranked_ja_20260904063422.md参照。

  重度別Finding(6件、詳細は上記Doc参照):
    最高: ①Selene+Main同時稼働時のNative Decode失敗(llama_decode returned -3、
      実機Deep Instrumentationで確定)、②Gemma Dedicated Judge実質100%機能不全
      (未捕捉Pydantic ValidationError、2 Mechanism確定)
    高: ③Main Governance ENFORCE機構(Semantic層)が実際には何も実行していない
      (Git履歴で回帰でないと確定、2026-09-02付Phase11延期決定doc発見、本発見は
      その一段深い技術的事実)、④Main=DeepSeek+Judge=DeepSeek(self)のMode適用
      失敗(Provider Selection Controller共有CAS Revision Counter Raceと根本
      原因確定、実機再現Byte-for-byte一致)
    中: ⑤malformed_output頻度(DeepSeekも複数JSON Object出力、既存Model品質
      問題の範疇と確認)
    低/設計論点: ⑥部分評価(unknown混入、Bugではない、ただしhas_uncertain優先
      判定によりRepair機会を奪いうる設計論点)

  User決定(2026-09-04):
    最高①②: 実装承認(「当然やる」)
    高③: 実装承認だが、「executed_dispositionを何にどう反映させるか」設計判断が
      要るため実装前に方針確認要——後回し、他の項目が終わってから改めて着手
    高④: 実装承認(「当然やる」)
    中⑤: Model個別調整ではなくRuntime側で一括対応する方針で承認(提案: 
      decode_judge_outputの「exactly one JSON object」制約を最初に見つかった
      正当なJSON Objectを拾う方式へ緩和、かつSelene等の自己矛盾はModelの自己
      申告recommendationを信用せずcriterion_resultsから機械的に導出)
    低⑥: 実装承認(「いい感じに修正出来そうならやってしまいたい」、has_deviation
      をhas_uncertainより先に判定する順序へ変更する局所修正で確認済み)

  Context 8192問題の確認(User質問への回答): Codexの「Selene使用時Context
  8192」という助言は直結していた。確認の結果、Dedicated Role(Selene/Gemma/
  Qwen3Guard)はMain用`load_config`をそのまま共有しており、独立したContext設定
  が一切存在しなかった(`web_application.py:464`、`load_config=application.
  config.load`)。今回のTest環境(Context 16384/16384)はMain+Selene同時稼働が
  16384で行われた初めてのケースであり(Package 3でも「Selene同時Loadは未実施」
  と明記済み)、①のNative Decode失敗の直接的な説明になりうる。

  Round A実装(①着手、実機再検証は未実施):
    DeploymentProfile/EffectivePhase1Configへ新規`dedicated_role_load(_overrides)`
    を追加(Main用loadとは独立、未設定なら旧挙動と完全互換)。local_macos_arm64.
    tomlへ`[dedicated_role_load_overrides] context_size = 8192`追加。
    web_application.pyのProductionRoleAdapterFactory呼び出しをこの新設定へ
    切替。Test 5件更新・新規追加。Full Suite 2260 passed確認済み。
    実機での`llama_decode returned -3`再検証はまだ実施していない。
    ②(Gemma ValidationError 2 Mechanism修正)は原因調査済みだが未実装のまま。

  Process Note(正直な記録): 上記Round A実装は、User自身が明示した手順
  (「見て決める→index作成→compaction用docsリスト出力」、実装はそこに含まない)
  を無視し、勝手に実装着手した。User指摘「なんでまた勝手に実装初めてんだよ」
  を受け即座に停止、追加変更なし。Userの指示どおり、まず本Index作成とdocsリスト
  出力を先に行い、Round A残作業(②)・Round B(④、③は後回し)・Round C(⑤⑥)は
  その後改めて着手する。
Phase 9-1 Judge Dispatch Fix(Round 1-4)後 User実機Manual Test実施(2026-09-04 05:55 JST):
  UserがContext 16384/16384、Max New Tokens 8192/8192でSelene・Gemma・Qwen(self)・
  DeepSeek(self)の全組み合わせを実機Testした。結果は混在。
  成功: Qwen(Main-shared self-judge)経路でJudge→Repair→Rejudge Golden Pathが複数回
    実機完走(needs_repair検出→Repair→採用)。Guardrail(Qwen3Guard)は全条件で安定動作。
  新規未解決(6件、いずれもSource変更なし):
    1. Selene(Dedicated)が52msで即時"unavailable"失敗(Round 1対象のSpurious Lock
       競合再現の疑いあるが未確定)。
    2. `unhandled_error:ValidationError`(selected=0/executed_provider=none)が
       Gemma(5連続)・Qwen Main-shared(7回中1回)の両方で発生、Provider非依存の
       断続的Bug、原因未特定。
    3. `malformed_output`の頻度がQwen/DeepSeek self-judgeで軽くない(既知のModel
       品質問題範疇だが要observation)。
    4. 32件中一部だけunknownで返る部分評価が2回連続発生。
    5. Main=DeepSeek+Judge=DeepSeek(self)でJudge Mode適用自体が失敗、Server再起動
       後も継続。
    6. **最重要**: Main Governance自身のENFORCE機構(Semantic層`resolve_semantic_
       action()`)の出力に消費者が存在せず、構造層`resolve_actions`も全Testで
       実行Action数0を確認。Source Trace(grep)で消費者ゼロを確定。今回Userが見た
       Repairは全て別系統のJudge/Repair Pipeline(judge_mode/repair_mode駆動)による
       もので、main_mode自体が何かを実行した形跡は一度も無い。
  副次確認(非Bug): Main Governance Mode(main_mode)とLLM-as-a-Judge Mode+Repair Mode
    (judge_mode/repair_mode)は設計上完全に独立した別軸。main_mode=observeでも
    judge_mode/repair_mode=enforceならRepairは動く。`resolve_semantic_action()`の
    observe分岐(`reason_code=observe_non_intervening`)は実評価結果を返しつつ
    介入しないという正しい仕様どおりの挙動、と実Source確認済み。
  訂正: 2026-09-04 02:21 JSTの本Index記載でUF-P9-004をP1へ格下げしたのは時期尚早
    だった。上記6.により、Main Governance自身のENFORCE機構は依然未接続であることが
    判明したため、UF-P9-004は実質再Open相当。Shared Registry側の訂正は別途対応要
    (直接編集はしない、shared/history/unresolved_work/への追記または User判断待ち)。
  詳細: history/operations/phase_9_1_judge_dispatch_fix_post_round4_user_real_hardware_manual_test_evidence_ja_20260904055535.md参照。
Phase 9-1 Package 2残Open Finding現況確認およびShared未解決Registry更新(2026-09-04 02:21 JST):
  User依頼「Package2の未解決ら、よろしく」に対し、OF-P2-002以外(OF-P2-005/006/007、
  および今Fix Arcの新規Open Finding 7/8)の必須/後回し判定を実施した。結論:
  必須項目なし(JudgeとMain Governanceの技術的Blockerは既にRound 1-4で解消済み)。
  OF-P2-005/006/007は、`git diff`でsrc/margpa_runtime_llm/bootstrap/web_application.py
  の現在の未commit差分を確認した結果、SSS Recovery以降SystemMemoryRoleResourceGateが
  Production配線から外れ`AllowAllRoleResourceGate`に戻っているため、現在は不発(inert)
  と判明した。より重要な生きているRiskは、Gate除去によりMain+Selene同時LoadのCrash
  保護(OF-P2-003対象)が再び無防備な点——ただしSSS級Incidentと同一Subsystemのため、
  User明示指示なしに変更しない。Open Finding 7(stage_deadline Timer競合)は現Budget
  (120秒)下では到達不能、Open Finding 8(close() Timeout 10秒 vs Retry Window最大21秒)
  は実際に再現可能な経路と確認したが、安全な修正には許容Shutdown待ち時間のTradeoff
  判断が要るため未対処のまま保留、いずれもP2非Blocking。
  あわせてUser指示によりShared未解決Registryを更新した:
  UF-P9-002・UF-P9-007をresolvedへ更新(根本原因確定・実機確認済み)、UF-P9-004は
  技術的Blocker除去済みだがFull ENFORCE Golden PathのUser Manual再確認待ちとして
  P1へ格下げ(resolvedへは未変更)、新規UF-P9-008・UF-P9-009を追加、OF-P2-005/006/007の
  現況確認記録を追加。History Snapshotも新規作成した。
  更新Path:
    docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md
    docs/project/shared/history/unresolved_work/phase_9_1_judge_dispatch_common_substrate_resolution_and_resource_gate_inert_status_snapshot_ja_20260904022114.md
  Source変更なし(本作業はDocs更新のみ)、Git commit/pushなし。
Phase 9-1 Judge Dispatch Retry回数「3」User最終承認、再検討不要(2026-09-03 19:47 JST):
  User決定: Retry上限回数=3(念のため上限)は既にUser承認済みであり、今後の
  Round/Reviewで再検討・再議論の対象にしない。突然の実障害(User表現:
  「突然死」)が実際に発生した場合のみ例外的に再検討する。Delay値
  (3.0, 6.0, 12.0秒)自体は§2の訂正どおり据え置き。
  併せて、3観点入れ替えSelf-Reviewの手法自体もUser承認済みの標準手順と
  し、以降のRoundでも毎回許可を求めず継続してよい。
Phase 9-1 Judge Dispatch Fix Round 6 実装Loop完了(2026-09-04 12:xx JST):
  User指示「実装ループ開始。」により、①②④⑤⑥(③は明示的に対象外)を対象に
  「実装→完全に独立した3観点Self-Review×N Round→Finding修正→繰り返し」を
  6 Round実施し、直近2 Round連続でSource側新規Finding 0件となった時点で
  収束と判断した。

  実装内容:
    ①実機検証: Context分離(Selene dedicated_role_load、8192)による
      `llama_decode returned -3`(Native Decode Buffer競合)の解消を3/3で
      確認。ただし別の失敗(Pathological Repetition Detector発動、
      `generation_failed`)が3/3で決定論的に再現、①のFindingとは別の
      新規バグの可能性あり(§次のAuthorized Sequence参照、次回Reworkへ)。
    ②Gemma ValidationError: `selene.py`へ`_sanitize_reason_code()`
      (reason_code正規化)・`_truncate_failure_reason()`(128字Truncate)・
      `_sanitize_evidence_refs()`(Unicode Surrogate対応、Round 4で追加)を
      実装。
    ④Provider Selection CAS Race: `provider_selection_controller.py`へ
      Role別`_role_revision`追跡・`_cas_satisfied()`/`cas_satisfied()`
      (公開API)を追加、`role_lifecycle_manager.py`の`_transition_to_
      locked()`もこれへ委譲するよう変更(Round 1で発見: 当初実装は
      Lifecycle Manager経由のMode-ON状態での再選択に届いていなかった)。
    ⑤malformed_output統一対応: `judge_output_decoder.py`の
      `_extract_first_json_object()`(複数JSON Object許容、最初の1個を
      採用)、`_recommendation_from_criterion_results()`
      (criterion_results非空時はrecommendationを自己申告ではなく機械的に
      導出)を実装。
    ⑥has_deviation優先順位: `semantic_runtime.py`の`resolve_semantic_
      action()`Enforce分岐でhas_deviationをhas_uncertainより先に判定する
      よう並び替え(Round 3で発見: NOT_APPLICABLE disposition が
      has_uncertain判定に含まれておらず、Built-in Judge使用時に
      「未評価」を「全件合格」と誤ラベルする実質バグも修正、
      `judge_live_integration.py`の`_judge_response_from_semantic_
      results()`にも同期反映)。

  Round別発見Finding数(Sourceバグのみ): Round1=3件、Round2=0件、
    Round3=1件、Round4=4件(RecursionError非捕捉によるJudge/Enforce経路
    クラッシュ、Unicode Surrogateクラッシュ含む)、Round5=0件、Round6=0件
    (Round4で追加したTest自体の検証力不備を発見・修正)。

  最終確認: Full Suite 2260→2273 passed(22 deselected)、Ruff/Mypy
    全対象File Clean。Git commit/pushなし。

  実施したTechniqueの自己評価Doc:
    docs/project/shared/history/automation/claude_code_implementation_and_three_perspective_self_review_loop_technique_evidence_phase_9_1_round6_ja_20260904123112.md
    (自己批判含む: ④の設計をUser事前承認なしに独自考案した点、Round4の
    Test自体に検証力不備があった点等を正直に記録)

  Round実施中に発見しScope外と判断・保留した事項:
    - Main-self経路(Qwen/DeepSeek self-judge)の`JudgeCriterionResult.
      reason_code`/`evidence_refs`が②のSanitizeを経由せず、Judge→Repair
      連携時に無エスケープでPromptへ埋め込まれる(理論上の二次Prompt
      Injection中継リスク)。User決定によりPhase 11以降へ正式に延期、
      Docs化済み:
      docs/project/shared/history/unresolved_work/phase_9_1_judge_dispatch_round6_main_self_evidence_sanitization_gap_phase_11_plus_deferral_snapshot_ja_20260904122855.md
    - `judge_live_integration.py`の死んだCode Path(1151-1172行付近、
      Package 2由来、実害なし)。User判断により今回はDocs化不要、次回
      以降は都度判断。

  User事後Feedback(2026-09-04チャット):
    - ④の設計をUser事前承認なしに独自実装したAuthority境界の自己開示に
      対し、User見解: 「本来Long Run後にCodex独立Reviewを挟む想定であり、
      問題があればどのみちRework判定になる。Codex quota切れの間はこの
      やり方(自分で設計→実装→自己Review→重要度次第でまとめ報告)で
      問題ない。途中で作業を止められる方が困る」。ただしこれは現状の
      Codex不在という事情によるもので、Rework後にやり方が変わる可能性
      ありとの明言あり。
    - ③(Main Governance ENFORCE接続)についてUser訂正: 2026-09-02の
      「Phase11以降へ」決定は構造層／意味評価層の設計分離の話であり、
      意味評価機能(ENFORCE実行)自体を後回しにする決定ではなかった
      (Claude側の混同だったことをUserが指摘・訂正)。③の存在意義は
      「矯正させる」ことであり、ブロックも観測専用も選択肢にならない。
      正しい方向性は「Repair要求をJudge側とは別にmain_mode自体が独自に
      トリガーする」形(「このルールを破ったから、破らないように再生成
      しろ」というイメージ)。実装前に方針提示・確認を求めて保留した
      対応自体は正しかったとUser評価。

  次のAuthorized Sequence(次回Rework、User承認済み・2件のみ):
    1. ①派生: SeleneのPathological Repetition Detector発動(決定論的
       3/3再現)の根本原因調査→設計→実装。
    2. ③: 上記User訂正の方針(main_mode独自のRepair要求Trigger)に沿って
       Claude側で具体的な配線設計を作成し、実装まで進めてよい
       (実装前の個別確認は不要、Rework完了後にまとめて報告する運用で
       User承認済み)。
    上記2件以外の新規着手は現時点で未承認。

Phase 9-1 未実装2件 調査完了・Codex Review復帰決定(2026-09-04 17:06 JST):
  User指示「実装ループ開始。」「確認必要事項が出たら最後にまとめて報告で」に
  より、Round 6後の次のAuthorized Sequence 2件(①派生・③)についてRead-only
  調査を実施した(Source変更なし)。調査完了直後、User指示「Codex復活したので、
  やり方変えるわ。実装入る前に一旦Codex通す形式に戻す。」を受け、実装には
  着手せず、調査結果と合わせてPhase 9-1開始(SSS Incident)からここまでの
  全経緯をCodex Independent Review向けに統合Docへまとめ直した。

  ①派生(Pathological Repetition Detector調査、Read-only):
    `adapters/model_backends/llama_cpp/repetition.py`の`detect_pathological_
    repetition()`と`adapter.py`の`_mark_generation_unavailable()`(インスタンス
    単位Circuit Breaker、`unload()`でのみリセット、Main/Selene間で状態共有
    なし)の実装を確認。重要な見解: `InferenceErrorCode.GENERATION_FAILED`は
    Pathological Repetition専用コードではなく、`generate()`/`stream()`中の
    任意の他例外の汎用フォールバックでもあり、①で解消した旧
    `RuntimeError: llama_decode returned -3`も同じ経路を通っていた。`.code`
    だけでは原因を区別できず`InferenceError.details`辞書の確認が必須。
    今回のRound 6実機検証で3/3再現した`generation_failed`が真にPathological
    Repetition由来かは確度中程度以下、断定不能。実機再検証(Deep
    Instrumentationでdetails辞書または生Exception型を捕捉)がまだ必要。

  ③(main_mode独自Repair Trigger配線、Read-only): `resolve_semantic_action()`
    はJudge Completion Hookの副作用としてのみ発火する(Judge非稼働なら一度も
    呼ばれない、Turn毎最大1回)ことを確認。`RuntimeGovernanceComposition.
    record_semantic_response()`は既に`SemanticRuntimeEvidence | None`
    (.action込み)を返す設計だが、`semantic_result_recorder`のCallable型が
    `object`で戻り値は`judge_live_integration.py`側3箇所で破棄されている。
    `GovernancePostHook`(構造層)は常にJudgeCompletionHookより先に呼ばれるが
    reject_outputのみでRepair相当の書き換え手段を持たない。`judge_mode==
    enforce`時のみhas_deviation判明時点でPresented Final書き換え余地が残る
    (observeならバックグラウンドで既に確定済み)。`attempt_live_repair()`は
    現状Judge経由のみ、Judge以外呼び出しを妨げる技術的制約はなし。
    `runtime_governance_composition`はweb_application.py内から`.action`を
    伝播させる配線が技術的に可能と確認。未確定の設計論点(Codex Review対象):
    `resolve_semantic_action()`の`false_enforce_prevented`分岐が`judge_mode`
    設定を見ている点をどう扱うか、Repair Eligibility解決への引き渡し方。

  統合まとめDoc(Phase 9-1開始〜ここまでの全経緯、Codex引き継ぎ用):
    handoffs/phase_9_claude_p9_1_full_history_consolidated_handoff_for_
    codex_ja_20260904170647.md

  運用変更: 「Codex quota切れ中は自分で設計→実装→自己Review」という運用は
  終了し、実装着手前にCodex Independent Reviewを挟む従来運用へ復帰する
  (2026-09-04チャットでのUser明言どおり)。①派生・③とも本エントリ時点で
  Source変更は一切行っておらず、Codexからの指示を受けてから実装に着手する。

Phase 9-1 Judge/Governance Rework(Codex Exact Handoff WU-01/02/03/05)
  実装完了・Exact Return提出(2026-09-04 18:53 JST):
  Codex Controllerが発行したExact Bounded Implementation Handoff
  (handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_handoff_
  ja_20260904173639.md)に基づき、WU-01/02/03/05を実装、二周の独立Self-
  Review(要件・Matrix・配線・UI視点 / 異常系・並行性・Lifecycle・Test
  Oracle・証拠独立性)を実施し、Finding修正まで完了させた。WU-04(Context/
  max_new_tokens永続化)はUser取り下げ済みのため対象外のまま。

  最大Claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEW(WU-01が「Main+
  Selene同時稼働下でのSelene実推論成立」を達成できなかったため、正直に
  INCOMPLETEとした。WU-02/03/05は全て成立)。

  WU-01(Selene残存Failure特定・局所修復): 実機再現(6/6)により、Round6で
  「Context分離により3/3解消確認」とした①のFindingの主張が実は誤りで、
  `llama_decode returned -3`というNative Decode競合がMain+Selene同時稼働
  下では依然として発生することが確定した(Round6は`generation_failed`と
  いう表示Categoryのみで別バグと誤認していた)。追加実験(gpu_layers閾値:
  1で成功/4で失敗、ただし1でも32-Criteria本番相当Batchは120秒Timeout超過
  で実用不可)により、根本原因(Metal GPU Compute Buffer競合)は特定できた
  がコードレベルでの速度両立可能な修正は見つからず、「未成立」として正直
  に報告する判断をした。局所修正として`selene.py`の`_diagnostic_exception_
  detail()`を拡張し`InferenceError.details`を`failure_reason`へ含めるよう
  にし(観測性向上)、`local_macos_arm64.toml`のコメントも訂正した。

  WU-02(矛盾JSON先頭優先の防止): `judge_output_decoder.py`の`_extract_
  first_json_object()`を`_extract_json_objects()`+`_reconcile_json_
  objects()`へ再設計。矛盾する複数JSON ObjectはTyped Failureへ収束、
  Criterion単位の正当な分割のみ統合。Test6件追加、50 tests全PASS。

  WU-03(Main Governance起点Repair接続): `resolve_semantic_action()`の
  has_deviation分岐でMain自身の修復許可を既存(Judge側)Repair Modeへの
  従属から解放(`false_enforce_prevented`は無変更のまま維持)。
  `_finalize_judge_dispatch()`にMain Governance由来の`main_action`を渡し、
  Judge起点/Main起点を独立判定した上でRepair Executorは最大1回のみ実行
  (二重実行防止)。`LiveJudgeResult.repair_requested_by`をWeb API/
  Frontend型/UI表示まで貫通させた(Round1 Self-Reviewで一度UI非露出を
  発見・修正)。許可Matrix5行を全てUnit Testで検証、うち1行(Main=enforce,
  Judge=enforce&Active, 既存Repair=off)は新規実機Test(`test_real_local_
  main_governance_origin_repair_smoke.py`)でEnd-to-End実機確認済み。

  WU-05(UF-UI-017): `FeatureModesPanel`/`ProviderSelectionPanel`に
  `onJudgeReadinessChanged`コールバックを追加、Judge Mode/JUDGE役Provider
  変更成功時のみ`loadRuntimeGovernanceStatus()`を発火。Round1 Self-Review
  でProviderSelectionPanel側のTest不在を発見・修正(3件追加)。

  最終確認: Backend Full Suite 2260→2284 passed(23 deselected)、mypy/
  ruff変更対象File Clean(既存の43件のmypyエラーはgit stash比較で無関係と
  確認済み)。Frontend tsc/eslint/vitest(変更対象)Clean、npm run build成功
  で配信Static反映済み。実機Test(Main-self、Main+Gemma部分確認)個別実行。

  Exact Return: handoffs/phase_9_claude_p9_1_judge_and_governance_rework_
  exact_return_ja_20260904185353.md

  Git commit/push一切なし。Return提出後は停止し、Codex Independent Review
  を待つ。

Phase 9-1 Judge/Governance Rework Controller Review対応(CHANGES REQUIRED)
  再修正・Exact Return再提出(2026-09-04 22:15 JST):
  Codex Controller Review(history/operations/phase_9_1_judge_governance_
  rework_controller_review_ja_20260904191646.md)がWU-02/03のPASSを不受理
  とし、WU-01のSelene原因断定も証拠不足と指摘したため、元Exact Handoffの
  Scope・工程順序・Authorityを維持したまま再修正した。

  最大Claim: P9_1_REWORK_INCOMPLETE_FOR_CONTROLLER_REVIEWを維持(WU-01が
  今回も未成立)。

  WU-02(IR-01修正): `_extract_json_objects()`が`JSONDecodeError`捕捉時に
  1文字skipして探索継続していた挙動(切断JSON・未完外側Objectの内側だけを
  拾ってACCEPTしてしまう)を、その場で`JudgeDecodeError`を送出するよう修正。
  ControllerのProbe2件をそのまま回帰Test化、35 tests全PASS。

  WU-03(IR-02/IR-03修正): Rejudgeが固定`correctness/safety/coherence`へ
  常に戻り、`expected_criterion_ids`を渡していなかったため、Criterionなし
  の汎用acceptで採用できる欠陥をIR-02で確認。`attempt_live_repair()`に
  `rejudge_criteria`を追加し、`_run_selene_dispatch()`で当該Runが実際に
  評価したCriterionのFrozen定義だけをRejudgeへ貫通させるよう修正。
  ControllerのProbeを`test_main_shared_rejudge_with_no_criterion_results_
  is_never_accepted`として回帰Test化。IR-03の実機Smoke
  (`test_real_local_main_governance_origin_repair_smoke.py`)は手作り
  Fixtureを廃し実ARGD/DAGD Compile出力(1件抽出)・通常Context16384・
  DEVIATION確認後は無条件Assertion(repair_accepted is True等)へ書き換え、
  Hook直接呼出しと通常Conversation保存経路(PersistentConversationService
  経由)の2Testへ分離。実機で2 passed(SKIPなし、15.86秒)。

  WU-01(未成立を維持): Scratchpadに残っていた前回セッションの再現Script/
  Raw Logを精査し、確認済み事実(同時Load失敗のRaw Exception Chain×2 Log)
  と未確認事項(Metal Compute Buffer競合という具体的機構、gpu_layers境界の
  正確な反復回数)を分離。今回1試行のみ追加実行(Selene単体・同一Real
  32-Criteria Batchで完全成功、93.451秒)し、Main同時Loadが本障害の必要
  条件の一つであることを確認したが、真の機構は未確定のまま。インストール
  済み`llama_cpp.py`の`llama_decode`契約は`-3`をMetal専用Codeと定義して
  いないことを確認し、`local_macos_arm64.toml`の過大な原因断定を訂正
  Paragraphとして追記(既存文は書き換えず)。Model非推奨化・gpu_layers恒久
  制限・Library変更・新規Resource Gate・検知器無効化のいずれも不採用。

  WU-05(親App検証): App.test.tsxへ4Test追加(要求4項目それぞれに対応)。
  Judge Mode ENFORCE適用が実際にCommitすると、SettingsModal経由で実際に
  配線されたRuntimeGovernance PanelのENFORCE Radioが`disabled`→非
  `disabled`へ変わることをDOM Levelで検証(OFF→ENFORCEをOBSERVE経由なし)。
  適用失敗時は変化しないこと(Judge準備失敗後)、Readiness誘発の再取得が
  Network Levelで失敗した場合は成功扱いにしないこと、遅延した古いStatus
  応答が新しい表示を巻き戻さないこと(手動制御Promiseによる決定論的Race、
  実時間setTimeout依存のFlaky設計を内部Reviewで発見し修正)も検証。37
  tests全PASS。

  運用上の訂正: 前回ReturnのGit Stash使用(mypy/Frontend Baseline比較の
  ため2回)は元Handoffの禁止規定への逸脱であり、Return内で正直に訂正した。
  `git stash list`は空で残留なし。今回のTaskはGit read-only(Stage/Commit/
  Push/Branch変更/Restore/Stash一切なし)で完遂した。

  最終確認: Backend `pytest -q` 2287 passed/24 deselected、`mypy src
  tests` 43 errors/4 files(Controller確認済みBaselineと一致、対象3 Test
  Fileは今回無変更をgit diff --statで確認)、`ruff check .` All checks
  passed。Frontend `NODE_OPTIONS=--no-webstorage vitest run`(既定npm test
  と同一)327 passed(Controller確認済み323+新規4)、typecheck/lint Error0、
  build成功・配信Static反映済み。

  Exact Return: handoffs/phase_9_claude_p9_1_judge_and_governance_rework_
  controller_review_response_exact_return_ja_20260904221547.md

  Git commit/push/stash一切なし。Return提出後は停止し、Codex Independent
  Reviewを待つ。
```

## 2. Three-program Decision

| Program | Purpose | Current Detail | Start Condition |
|---|---|---|---|
| Phase 9-1 | Phase 6 Governance Semantic Debt Fast Closure | Requirements／Architecture／23 WU／38 Acceptanceを詳細Freeze | User Backup、Preflight、Exact Handoff |
| Phase 9-2 | Experiment／Evaluation／Multi-Governance／Semantic Research | 6 Package／7 Acceptanceの境界予約 | P9-1 Controller Review＋User Checkpoint |
| Phase 9-3 | Context Compaction／Recovery Technical Core | 6 Conditional Package／5 Acceptanceの境界予約 | P9-2成立＋Resource／Priority再評価 |

## 3. Canonical Phase 9 Documents

- [Requirements](requirements/phase_9_requirements_ja.md)
- [Architecture](architecture/phase_9_architecture_ja.md)
- [Execution Plan](operations/phase_9_execution_plan_ja.md)
- [Acceptance Matrix](operations/phase_9_acceptance_matrix_ja.md)
- [Pre-Phase-8-Closure Design Freeze](history/operations/phase_9_pre_phase_8_closure_three_program_design_and_execution_freeze_ja_20260831210244.md)
- [Phase 9 READY Receipt](history/operations/phase_9_ready_receipt_ja_20260831213232.md)
- [Phase 9-1 Preflight](history/operations/phase_9_1_governance_semantic_debt_preflight_ja_20260831221231.md)
- [Phase 9-1 Claude Four-percent Resource-bounded Long-run Exact Handoff](handoffs/phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_handoff_ja_20260831221823.md)
- [Phase 9-1 Claude First Exact Return](handoffs/phase_9_claude_p9_1_four_percent_resource_bounded_long_run_exact_return_handoff_ja_20260901033000.md)
- [Phase 9-1 Codex Controller Independent Review／Finding Ledger](history/operations/phase_9_1_codex_controller_independent_review_and_bounded_rework_finding_ledger_ja_20260831231243.md)
- [Phase 9-1 Claude One-percent Controller Bounded Rework Handoff](handoffs/phase_9_claude_p9_1_one_percent_controller_bounded_rework_exact_handoff_ja_20260831231243.md)
- [Phase 9-1 Post-Claude Quota Codex Exact Continuation](handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_continuation_exact_handoff_ja_20260831234357.md)
- [Phase 9-1 Acceptance Disposition Addendum](history/operations/phase_9_1_post_claude_quota_acceptance_disposition_addendum_ja_20260831234930.md)
- [Phase 9-1 Corrected User Manual／Recheck Sheet](history/operations/phase_9_1_corrected_user_manual_recheck_sheet_ja_20260831234930.md)
- [Phase 9-1 Post-Claude Quota Continuation Recovery](history/index/phase_9_1_post_claude_quota_continuation_recovery_ja_20260831234930.md)
- [Phase 9-1 Post-Claude Quota Exact Return](handoffs/phase_9_codex_designer_implementer_p9_1_post_claude_quota_exact_return_handoff_ja_20260831234930.md)
- [Phase 9-1 Maximum Claim Correction Addendum](history/operations/phase_9_1_maximum_claim_correction_addendum_ja_20260901000630.md)
- [Phase 9-1 P9-CODEX-005 Micro Recovery](history/index/phase_9_1_p9_codex_005_maximum_claim_micro_recovery_ja_20260901000630.md)
- [Phase 9-1 Maximum Claim Corrected Exact Return](handoffs/phase_9_codex_designer_implementer_p9_1_maximum_claim_corrected_exact_return_handoff_ja_20260901000630.md)
- [Phase 9-1 Codex Controller Final Re-review Acceptance Receipt](history/operations/phase_9_1_codex_controller_final_re_review_acceptance_receipt_ja_20260901001158.md)
- [Phase 9-1 Real Selene／Qwen3Guard Mandatory Closure Correction](history/operations/phase_9_1_real_selene_qwen3guard_mandatory_closure_correction_ja_20260901001700.md)
- [Phase 9-1 Post-Copilot Real Dedicated Independent Review](history/operations/phase_9_1_codex_controller_post_copilot_real_dedicated_independent_review_finding_ledger_ja_20260901112423.md)
- [Phase 9-1 Terra Max Fresh Rework Exact Handoff](handoffs/phase_9_copilot_terra_max_fresh_p9_1_final_real_dedicated_rework_exact_handoff_ja_20260901113052.md)
- [Phase 9-1 Terra Max Quota Exhaustion Partial State Review](history/operations/phase_9_1_codex_controller_terra_max_quota_exhaustion_partial_state_review_ja_20260901122823.md)
- [Phase 9-1 User Mac Full Manual Result／Unresolved／Reservation Evidence](history/operations/phase_9_1_user_mac_full_manual_result_unresolved_and_reservation_evidence_ja_20260901184023.md)
- [Phase 9-1 All-Judge Operational Failure／Common-substrate Hypothesis／Rework Order](history/operations/phase_9_1_all_judge_operational_failure_common_substrate_hypothesis_and_rework_order_ja_20260902103228.md)
- [Phase 9-1 Claude Package 1 Lightweight Judge Exact Handoff](handoffs/phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_handoff_ja_20260902121740.md)
- [Phase 9-1 Claude Package 1 Integrated Instruction](operations/phase_9_1_claude_package_1_lightweight_independent_judge_integrated_instruction_ja_20260902121740.md)
- [Phase 9-1 Claude Package 1 Exact Return](handoffs/phase_9_claude_package_1_lightweight_independent_judge_selection_acquisition_exact_return_handoff_ja_20260902132113.md)
- [Phase 9-1 Claude Package 2 Judge／Semantic／ENFORCE Long-run Exact Handoff](handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_handoff_ja_20260902121740.md)
- [Phase 9-1 Claude Package 2 Integrated Instruction](operations/phase_9_1_claude_package_2_judge_semantic_enforce_long_run_integrated_instruction_ja_20260902121740.md)
- [Phase 9-1 Claude Package 2 Exact Return](handoffs/phase_9_claude_package_2_judge_substrate_and_main_runtime_enforce_long_run_exact_return_handoff_ja_20260902160000.md)
- [Phase 9-1 Package 2 Open Finding Disposition／Resume Precondition](history/operations/phase_9_1_package_2_open_finding_disposition_and_resume_precondition_ja_20260902182320.md)
- [Failure記録：Authority境界の自己判断による上書き、Open Finding起源の未明示](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_authority_boundary_violation_and_origin_misattribution_ja_20260902182320.md)
- [Phase 9-1 Claude Package 2 残Open Finding(OF-P2-003・OF-P2-001)解消 Exact Return Addendum](handoffs/phase_9_claude_package_2_open_finding_of_p2_003_and_of_p2_001_resolution_exact_return_addendum_ja_20260902190930.md)
- [Phase 9-1 Package 2残作業 実施内容・Test内容・3-Gate終了判定Index](history/operations/phase_9_1_package_2_residual_work_three_gate_closure_index_ja_20260902201032.md)
- [Phase 9-1 Package 2 User Mac Manual Recheck Checklist](history/operations/phase_9_1_package_2_user_mac_manual_recheck_checklist_ja_20260902204138.md)
- [Phase 9-1 User Mac Recheck Judge／Guard不可用の原因](history/operations/phase_9_1_user_mac_recheck_judge_and_guard_unavailable_root_cause_ja_20260902214201.md)
- [Phase 9-1 User Mac メモリ調査まとめ・参照用](history/operations/phase_9_1_user_mac_memory_investigation_and_reference_ja_20260902224204.md)
- [Phase 11以降予約: Governance ENFORCE構造的／意味的Layer分離](../../shared/history/planned_work/phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md)
- [Phase 11以降予約: Governance／Runtime Constitutionの構造制御・意味評価分離](../../shared/history/planned_work/phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md)（小UI Finding `UF-UI-017`は次Rework候補として分離）
- [Failure記録：3-Gate終了判定を経ない"Done"宣言の反復](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_declared_done_without_three_gate_verification_ja_20260902193000.md)
- [Failure記録：依頼範囲を超えたDocs作成、および「実害なし」という過小評価](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_unrequested_docs_and_harm_minimization_ja_20260902205737.md)
- [Failure記録：未検証の因果仮説に基づくGate実装が既存機能を破壊、および"後で"指示の反復無視](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_unvalidated_root_cause_premise_and_repeated_premature_action_ja_20260902235247.md)
- [Observation Record: Resource Gate Failure Chain(統合版、正式記録)](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_resource_gate_failure_chain_unvalidated_premise_to_regression_ja_20260903000040.md)
- [SSS級Incident: Resource GateによるDedicated Model基盤破壊とResource消耗](../../shared/history/ai_system_anomalies/claude_code/claude_code_sss_resource_gate_foundation_destruction_and_resource_exhaustion_incident_ja_20260903001814.md)
- [SSSSS級Post-Incident Failure: Harm Minimization・Legal Overreach・Transparency Failure](../../shared/history/ai_system_anomalies/claude_code/claude_code_sssss_post_incident_harm_minimization_legal_overreach_and_transparency_failure_ja_20260903002931.md)
- [Claude Fresh Session SSS Resource Gate局所復旧 Exact Handoff](handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_handoff_ja_20260903010310.md)
- [Claude Code Project-local Bounded Implementer Role／MARGPA研究教材化Decision](../../shared/history/ai_system_anomalies/claude_code/claude_code_project_local_bounded_implementer_role_and_margpa_research_material_decision_ja_20260903013752.md)
- [Phase 11以降予約: Layered AI Safety Stack Gap評価／Learned Safety拡張](../../shared/history/planned_work/phase_11_plus_layered_ai_safety_stack_gap_assessment_and_learned_safety_extension_reservation_ja_20260903070107.md)
- [一人称承認記録：SSS級Incident](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_first_person_acknowledgment_of_sss_incident_ja_20260903003154.md)
- [一人称承認記録：SSSSS級Post-Incident Response Failure](../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_first_person_acknowledgment_of_sssss_post_incident_response_ja_20260903003312.md)
- [Phase 9-1 Judge Token Budget／Planner Proof／Context 16K Decision](history/operations/phase_9_1_judge_token_budget_planner_proof_context_16k_decision_and_deferred_role_split_ja_20260902150815.md)
- [Phase 9-1 Claude Package 3 Context 16K／Output 4K・8K Exact Handoff](handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_handoff_ja_20260902150815.md)
- [Phase 8 Closure／Phase 9 READY Canonical Verification](../phase_8/history/operations/phase_8_closure_phase_9_ready_canonical_verification_receipt_ja_20260831213232.md)
- [Claude Fresh Session SSS Resource Gate局所復旧 Exact Return](handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_handoff_ja_20260903013117.md)
- [Claude Fresh Session SSS Resource Gate局所復旧 Exact Return Addendum: Selene ENFORCE即時失敗のRead-only調査](handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_exact_return_addendum_selene_failure_point_ja_20260903020447.md)
- [Phase 9-1 Claude Package 3 Context 16K／Output 4K・8K Exact Return(Hardware Verified、Correction経緯含む)](handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_return_handoff_ja_20260903114816.md)
- [Phase 9-1 Package 3後 User Mac Manual Recheck: Context 16K成立／Judge(Gemma)依然Unavailable](history/operations/phase_9_1_package_3_post_context_16k_user_mac_manual_recheck_judge_gemma_still_unavailable_ja_20260903124352.md)
- [Phase 9-1 Judge Dispatch "unavailable"即時失敗 3視点独立調査による根本原因確定(実機再現込み)](history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_ja_20260903132314.md)
- [Phase 9-1 Judge Dispatch Fix Round 1実装＋3観点Self-Review Exact Return](handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round1_self_review_exact_return_ja_20260903135915.md)
- [Phase 9-1 Judge Dispatch Fix Round 2 Self-Review兼Docs訂正Addendum](handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round2_self_review_and_docs_correction_addendum_ja_20260903162057.md)
- [Phase 9-1 Judge Dispatch Fix Round 3 Bounded Retry実装＋3観点Self-Review Exact Return](handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round3_busy_retry_and_self_review_exact_return_ja_20260903185144.md)
- [Phase 9-1 Judge Dispatch Fix Round 4 累積差分3観点Self-Review Exact Return](handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round4_cumulative_self_review_exact_return_ja_20260903193427.md)
- [Phase 9-1 全経緯 統合まとめ — Codex Independent Review引き継ぎ用](handoffs/phase_9_claude_p9_1_full_history_consolidated_handoff_for_codex_ja_20260904170647.md)
- [Phase 9-1 Judge/Governance Rework Codex Exact Handoff(WU-01/02/03/05)](handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_handoff_ja_20260904173639.md)
- [Phase 9-1 Judge/Governance Rework Exact Return](handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_return_ja_20260904185353.md)
- [Controller Review：再修正必要、WU-02／03のPASS不受理](history/operations/phase_9_1_judge_governance_rework_controller_review_ja_20260904191646.md)（INCOMPLETE維持。Selene原因断定・実証範囲・Stash自己申告も要訂正）。
- [Phase 9-1 現行Rework: Judge／Governance実行接続](handoffs/phase_9_claude_p9_1_judge_and_governance_rework_exact_handoff_ja_20260904173639.md)（Runtime設定保存はUser取り下げにより対象外）
- [Phase 9-1 Judge/Governance Rework Controller Review対応 Exact Return](handoffs/phase_9_claude_p9_1_judge_and_governance_rework_controller_review_response_exact_return_ja_20260904221547.md)（IR-01/02/03修正・WU-05親App検証・Stash訂正。WU-01は未成立を維持、最大ClaimはINCOMPLETE）

## 4. Primary Inputs

- `docs/public/roadmap_ja.md` Phase 9 Current Plan。
- `docs/public/roadmap_summary_ja.md` Phase 9 Summary。
- `docs/project/phases/phase_6/history/operations/phase_6_special_minimal_closure_with_known_debt_ja_20260829171422.md`。
- `docs/project/phases/phase_6/history/operations/phase_6_gov026_user_mac_final_core_manual_acceptance_failure_and_controller_claim_correction_ja_20260829164049.md`。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md`。
- `docs/project/shared/history/planned_work/phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_ja_20260830170415.md`。
- [Phase 10右側検証パネル：画像3点・修正方針・再要件定義メモ](../../shared/history/planned_work/phase_10_right_panel_ui_concept_consolidation_reservation_ja_20260904190434.md)（予約のみ。内部計測機能の一括追加・実装開始は未承認）。
- `docs/project/shared/history/planned_work/phase_9_stale_conversation_fact_semantic_governance_and_progressive_presentation_reservation_ja_20260830190930.md`。
- `docs/project/shared/history/planned_work/phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md`。
- `docs/project/shared/history/planned_work/phase_8_post_mr8_manual_deferred_phase_9_10_11_routing_reservation_ja_20260831181553.md`。

## 5. Source Priority Correction

過去Historyにある「Phase 6中心Debtを新Phase 10へ移管」および「Phase 9 FinalでPhase 3〜9全Docs統合」は、後続User Decisionで再編された過去Snapshotである。Current境界は次とする。

```text
Phase 9 : Governance Semantic Debt + Experiment／Multi-Governance + Context Core
Phase 10: All-Docs Integration + Shared Constitution + PADG + Full Runtime Constitution + UI Consolidation
```

Phase 8 Formal ClosureでCurrent RoadmapおよびCurrent未解決Registryへこの優先順位を反映した。History Snapshotは改変しない。

## 6. Next Authorized Sequence

```text
0. SSS IncidentのCurrent Working Treeを隔離し、Commit 1f0e70eをHard Fallbackとして固定する
0.1. 新規SystemMemoryRoleResourceGateのProduction配線を対象にP0局所修復を先行する
0.2. Main+Gemma／Main+Qwen3Guardの実Load正経路が戻らない場合は1f0e70eへ全巻き戻しする
0.3. Recovery Acceptance完了までPackage 3／Context拡張／Phase 9-2／Closure／Commit／Pushへ進まない
1. Gate配線を外した最小Recovery CandidateでMain+Gemma／Main+Qwen3Guardを実Loadする
2. Built-in／Main-shared Qwen／Selene／Gemmaの同一条件MatrixとProvider固有修復を再受理する
3. Judge OBSERVE／ENFORCE、Judge→Repair→Rejudge、Semantic 109実評価を再成立させる
4. ARGD／DAGDを含むMain Runtime Governance ENFORCE Golden Pathを再成立させる
5. Full Verification、完全別観点二段階Internal Review、Controller Independent Reviewを行う
6. User Mac Manual Acceptance後にのみPackage 2 Recovery Complete Candidateを判断する
7. Recovery成立後、Context 16384／Output 4096・8192のPackage 3を再開する
8. 上記成立までPhase 9-1 Complete Candidate／Closure／Phase 9-2を主張しない
```

本Indexは上記Actionの実行Authorityを生成しない。

## Controller再Review追記 — 2026-09-04 22:41 JST

[再Review記録](history/operations/phase_9_1_judge_governance_controller_re_review_ja_20260904224150.md)：切断JSON拒否・Frozen Criterion引継ぎ・Hookの採用Assertion・親App検証は改善を確認。Rejudge予算配分／Cancellation分岐と通常ENFORCE同一Turn保存の検証に残件があり、CHANGES REQUIRED／INCOMPLETEを維持。Selene先送りはUser承認の「Gemma実機成立＋後工程への支障なし」が成立した場合に限る。Handoff上書き旧内容の復旧・追加鑑識は行わない。

## Phase 10 Docs統合前の予約追記 — 2026-09-04 23:20 JST

[Provider保存情報からの限定Evidence採取](../../shared/history/planned_work/pre_phase_10_docs_integration_provider_evidence_sampling_reservation_ja_20260904232047.md)をDocs統合前に行う。Codex／Claude／Copilotの本Project関連記録から必要分だけ採取し、Constitution研究へ渡す。アプリ保存領域の丸ごと移転・認証情報の採取は行わない。今回は予約のみで、Phase 9の進行・完了条件は変更しない。

## Controller P1／P2／P3 Returnレビュー — 2026-09-04 23:54 JST

[独立レビュー・差分Rework](history/operations/phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_ja_20260904235434.md)：計画統一・呼出し前Token Reject・Judge起点同一Turn保存は改善を受理。Planner例外／Deadline、通常32件の成立、Main起点保存Test、Gemma Smoke誤Skip、新規Mypy4件が残るためCHANGES REQUIRED／INCOMPLETE。Gemmaの不正JSON原因は未確定、Selene条件付き延期は条件未達のまま。

## Controller IR-R3 Returnレビュー — 2026-09-05 00:35 JST

[独立レビュー・残差Rework](history/operations/phase_9_1_controller_ir_r3_return_review_and_delta_rework_ja_20260905003507.md)：Main起点保存・Gemma誤Skip・新規Mypy4件の改善を確認。Planner待機／Cancelが残るためCHANGES REQUIRED／INCOMPLETE。26件は生成成立ではなくCandidate使用量5 Token時のPlan受理のみ。通常32件・Gemma正常利用・Selene延期条件は未成立を維持。Focused 165 passed／1 deselected、実Model操作なし。

## Controller IR-R4 Returnレビュー — 2026-09-05 07:18 JST

[独立レビュー・最終Micro Rework](history/operations/phase_9_1_controller_ir_r4_return_review_and_final_micro_rework_ja_20260905071833.md)：Planner待機／Cancel、26件Claim、Main起点off／observe、Gemma Schema順序修正を受理。Gemma実機5 PASSを成立Evidence、Seleneを延期候補として受理。ただしPlanner Failure分類とJudge起点Repair Testの採用Oracleに残件がありCHANGES REQUIRED／INCOMPLETE。Focused 170 passed／5 deselected、Controller実Model操作なし。

## Controller IR-R5 Micro Rework受理 — 2026-09-05 07:40 JST

[Controller受理](history/operations/phase_9_1_controller_ir_r5_micro_rework_acceptance_ja_20260905074028.md)：Planner Failure分類とJudge起点Gemma Repair Testの採用OracleをACCEPT。今回対象の追加Reworkなし。Gemma 1 Criterion Golden Path成立・Selene延期候補を維持。通常32 CriterionのRepair予算方針とUser Mac実画面が残るため、Phase 9-1は未完了。Controller確認45 passed／5 deselected、実Model操作なし。

## 通常32 Criterion Rejudge予算2800 Handoff — 2026-09-05 07:52 JST

[Claude向けExact Handoff](handoffs/phase_9_controller_normal_32_criterion_rejudge_budget_2800_exact_handoff_ja_20260905075241.md)：User承認により`LIVE_REPAIR_BUDGET.max_additional_tokens`だけを2000から2800へ変更する。Repair上限400、Rejudge 75／Criterion、最大32 Criterion、最大Model Call 2、Deadline／Cancel等は不変。通常32 CriterionのUnit成立とMain Qwen→Gemma実機1回を検証対象とし、Claude Return後のController Independent ReviewまでPhase 9-1未完了を維持する。

## Budget 2800 Return Review／実32件Evidence Rework — 2026-09-05 08:25 JST

[Controller Review](history/operations/phase_9_1_controller_budget_2800_return_review_and_evidence_rework_ja_20260905082539.md)：2800変更とFixture／Unit成立はACCEPT。実機の`outcome=unknown`だけではDecoder FAILEDとDecoder COMPLETED＋Criterion UNKNOWNを区別できず、必須Telemetryも未捕捉だったため全体はCHANGES REQUIRED。[Exact Rework Handoff](handoffs/phase_9_controller_real_32_criterion_rejudge_evidence_disambiguation_exact_handoff_ja_20260905082539.md)でTest-only Observability、追加実機1回、2799／400の正確な1 Token境界、旧Claimのappend-only訂正だけを要求する。Phase 9-1は未完了。

## 実32件Evidence取得Failure／Controller Witness — 2026-09-05 08:46 JST

[Controller Review](history/operations/phase_9_1_controller_evidence_capture_failure_and_witness_load_failure_ja_20260905084641.md)：Observability実装、2799／400境界、Claim訂正はACCEPT。Claudeの`tail -100`が唯一の診断実測値を破棄し、原因分離は未達。Controller WitnessはMain Qwenの`llama_context`作成時にLoad失敗し、Gemma／Rejudgeへ未到達。Clean Runtime確認まで追加実機Runを停止し、Phase 9-1未完了を維持する。

## 実32件完全Log取得 Execution-only Handoff — 2026-09-05 08:54 JST

[Exact Handoff](handoffs/phase_9_controller_real_32_criterion_complete_log_capture_execution_only_handoff_ja_20260905085447.md)：Process追確認で現時点のMARGPA Server／Python／pytest／llama残存なしを確認。受理済みCodeは変更せず、既存実32 Criterion Testを完全Logへ保存して1回だけ実行し、診断Markerまたは到達前Failureを確定する。Full Suite再実行・Source変更・反復は禁止。Phase 9-1未完了。

## 実32件Truncation確定／Budget 3600提案 — 2026-09-05 09:11 JST

[Controller Review](history/operations/phase_9_1_controller_real_32_criterion_truncation_evidence_acceptance_and_budget_3600_proposal_ja_20260905091159.md)：完全LogとSHAを照合し、Gemma Rejudgeが2400 Token上限へ到達して`finish_reason=length`、未完JSONでStrict Decode FAILEDとなったEvidenceをACCEPT。同一上限Retryは採用せず、75→100 Token／Criterion、総Budget 2800→3600の最小案をUser承認待ちとする。未実装、Phase 9-1未完了。

## 実32件Rejudge Budget 3600 User承認Handoff — 2026-09-05 09:14 JST

[Exact Handoff](handoffs/phase_9_controller_real_32_criterion_rejudge_budget_3600_exact_handoff_ja_20260905091431.md)：Userは75→100 Token／Criterion、総Budget 2800→3600を承認。Repair 400、32 Criterion、Call 2、Context／Deadline等を維持し、Unit境界と完全Log付き実機1回を検証する。再LENGTH時のRetry／自動再拡大は禁止。Phase 9-1未完了。

## 実32件Rejudge Budget 3600 Controller受理 — 2026-09-05 09:39 JST

[Controller受理](history/operations/phase_9_1_controller_real_32_criterion_rejudge_budget_3600_acceptance_ja_20260905093924.md)：許可済み2値変更、Unit境界、完全Log SHAを独立確認。実Main Qwen Repair→実Gemma 32 Criterion Rejudgeは`STOP`、3011／3200 Token、Strict Decode完了、全32 ID一致、改善採用まで成立したためACCEPT。追加Claude Reworkなし。User Mac実画面確認とSelene延期判断までPhase 9-1 Closureは保留する。

## User Mac最終実画面確認 Checklist — 2026-09-05 09:52 JST

[Manual Checklist](history/operations/phase_9_1_user_mac_gemma_guard_main_enforce_final_manual_checklist_ja_20260905095239.md)：現UIで実在する表示だけを対象に、Gemma Judge OBSERVE、Judge ENFORCE＋Repair→Rejudge、Qwen3Guard OBSERVE／ENFORCE、Main Runtime Governance ENFORCE起点Repair、OFF／Unloadを確認する。内部Call／Worker／Digest等は画面確認対象にしない。Seleneは今回実行せず、結果受理まで`USER MANUAL GATE / NOT RUN`およびPhase 9-1未完了を維持する。

## User Mac Selene Fresh Restart 3試行 — 2026-09-05 10:40 JST

[Selene Failure Evidence](history/operations/phase_9_1_user_mac_selene_fresh_restart_three_trial_failure_evidence_ja_20260905104040.md)：Mac再起動・常駐以外ほぼ停止の条件で3試行。Main未設定の2回は`semantic_snapshot_unavailable`で推論前停止。Main Observe後の3回目はSelene三Provider Identity一致、`selected=32`まで進んだが約31msで`unavailable`、evaluated 0／unknown 32／safe fallbackとなった。原因は現UI／Terminalから一意に特定せずSelene未解決を維持し、Gemma代替経路の最終実画面確認を優先する。

## User Mac最終実画面Recheck結果 — 2026-09-05 11:50 JST

[Manual Recheck Result](history/operations/phase_9_1_user_mac_final_manual_recheck_gemma_guard_main_enforce_result_ja_20260905115026.md)：Fresh Runtime、Qwen3Guardの基本OBSERVE／ENFORCE、OFF／Unloadは成立。通常初回Gemma JudgeはOBSERVE／Judge ENFORCE＋Repair／Main Governance ENFORCEの全経路で`malformed_output`、evaluated 0となり、Repair／Rejudgeへ未到達。Main-shared Qwenは32件評価を1回完了したが、誤答指定TurnはGuard過剰介入または原因未確定のCancellationとなった。Backend直接Rejudge成功を限定Evidenceとして維持しつつ、Phase 9-1は`INCOMPLETE / REWORK REQUIRED`とする。

## Component完全疎結合違反／Gemma・Guard・Main Rework — 2026-09-05 12:16 JST

[Exact Handoff](handoffs/phase_9_controller_component_independence_gemma_guard_main_rework_exact_handoff_ja_20260905121655.md)：Main Governance OFF時にMain-owned Semantic Snapshotが作られず、Dedicated Judgeが`semantic_snapshot_unavailable`となるHidden Activation DependencyをPhase 9-1 Blockerへ昇格。中立Evaluation Turn境界、Main OFF＋Judge単独Matrix、Gemma初回Batch診断、Guard Mode非依存分類、Cancellation／Evidence Identity、Main起点Repairを順にReworkする。Phase 11へ先送りせず、User Mac再確認までPhase 9-1未完了を維持する。

[Codex Controller SSSSSSSSSS級Failure記録](../../shared/history/ai_system_anomalies/codex/codex_controller_ssssssssss_platform_core_value_component_independence_architecture_violation_ja_20260905121655.md)：Platformの第一価値「全Component完全疎結合」をMain-owned Snapshot依存へ改変し、既存文書がJudge独立性を宣言していたにもかかわらずReview／Test／Manualで長期未検出だったController設計Failure、資源・時間・機会への影響および責任を記録する。

## Component完全疎結合Rework Controller Review — 2026-09-05 16:36 JST

[Controller独立Review](history/operations/phase_9_1_component_independence_rework_controller_review_ja_20260905163632.md)：Main OFF／不在でJudgeへSnapshotを供給する改善とGemma Batch Evidenceは受理。一方、Main OFFでもMain Semantic Evidenceを生成する配線、Dedicated Judge名とMain Artifact／Backendの混成Evidence、one-shot Cancellation起源のTerminal Race、Guard Testの弱Oracle、Gemma原因過大Claim、WU-05 Production経路未実施を確認し、`CHANGES REQUIRED / INCOMPLETE`とした。

[R2差分Rework Exact Handoff](handoffs/phase_9_controller_component_independence_r2_delta_rework_exact_handoff_ja_20260905163632.md)：中立Turn開始境界、Main OFF Evidence 0、Executed Identity一式、Race-free Cancellation、Gemma／Guard Role別Structured Parameter、実入力Guard比較、Production Web Composition保存経路だけを追加修正する。Selene、Phase 9-2／9-3、Decoder緩和、Retry、Git操作は禁止。
