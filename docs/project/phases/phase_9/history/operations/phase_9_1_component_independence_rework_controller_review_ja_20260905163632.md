# Phase 9-1 — Component完全疎結合Rework Controller独立Review

```yaml
document_type: controller_independent_review
document_state: changes_required
recorded_at: 2026-09-05 16:36:32 JST
language: ja
reviewer_role: codex_controller
review_target: ../../handoffs/phase_9_claude_component_independence_gemma_guard_main_rework_exact_return_ja_20260905141500.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_REWORK_CHANGES_REQUIRED
phase_9_1_closure: false
real_model_action: none
git_mutation: none
append_only: true
```

## 1. 判定

`CHANGES REQUIRED / Phase 9-1 INCOMPLETE`。

Main OFF／Main Composition不在でもDedicated JudgeへSnapshotを渡せるようになった点、Gemma初回JudgeのBatch別Evidenceを取得した点は受理する。一方、WU-01／03／04／05の最大Claimは、実SourceとTest Oracleに対して過大であり受理しない。

## 2. 受理する差分

- Main不在時の`semantic_snapshot_unavailable`という直接Failureは解消方向へ進んだ。
- Gemma初回32 Criterionは、今回の1 TrialではBatch 1／2が完了し、Batch 3が`STOP`・500／1000 Tokenで不完全JSONになったというEvidenceを受理する。
- Evidence IdentityとCancellation起源を分離する必要性の認識、および追加Testの一部は有効。
- 非Model Full Suite 2346 passed、Ruff clean、Mypy既存Baseline維持という報告を保持する。

Controller Focused確認は33 passed／82 deselected。実Modelは再実行していない。

## 3. IR-CI-01 — WU-01は「起動独立」までで、OFF Call／Evidence 0ではない

`web_application.py`は、Main Compositionが存在する限り、Main ModeがOFFでもJudge Hookへ`runtime_governance_composition.record_semantic_response()`と`record_semantic_deferred()`を渡す。このためDedicated Judgeが完了すると、Main側`SemanticRuntimeCoordinator`へEvidenceとAction Decisionが生成される。

Controllerのメモリ内Probeでは次を確認した。

```text
frozen_main_mode       = off
evidence_created       = true
history_created        = true
executed_disposition   = observed
recommended_disposition = repair_requested
```

つまりAction介入が0でも、最上位不変条件の「Main OFFならMain Call／Mutation／Evidence／Authority 0」は未成立である。既存Testは`resolve_semantic_action()`の戻りが`OBSERVED`であることだけを確認し、Evidenceが作られないことを確認していない。

さらにMain OFF時のSnapshotはTurn開始時ではなく、生成後のJudge Hookから`JudgeSemanticTurnProvider`がLive Mode／Providerを再読して作る。Turn中にMode／Providerが変わると、`ConversationGenerationService.start()`で既にFreezeしたJudge Modeと異なるSnapshotを作り得る。

`JudgeSemanticTurnProvider`と共有Coordinatorの所有場所も`bootstrap/runtime_governance.py`および`modules/runtime_governance`のままである。Main CompositionからのObject依存は減ったが、中立Turn Contractの所有境界はまだ明瞭でない。

## 4. IR-CI-02 — WU-04 Evidence Identityが混成している

`_pending_evidence()`へ渡す`model_key`だけを`executed_provider`へ変更した一方、`model_runtime_info`は依然としてMain Candidateの`context.model_runtime_info`である。

Dedicated Gemma Judgeの場合、保存Evidenceは次の混成になり得る。

```text
model_identity          = Gemma
artifact_digest_sha512  = Main Qwen
backend_key/version     = Main Qwenを実行したBackend情報
```

これはConfigured／Active／Executed／Evaluatedを混同しないというWU-04契約に反する。追加Testは`model_identity`一項目しか確認しておらず、Artifact／Backendの誤帰属を検出しない。WU-04a resolvedは不受理とする。

## 5. IR-CI-03 — Cancellation起源のone-shot Setは競合する

`consume_preemption()`は破壊的なone-shot readであり、同じRunについてWorker側とENFORCE待機Loop側の二箇所が呼ぶ。Worker完了とOuter LoopのCancellation確認が競合すると、一方がTrueを消費し、もう一方が同じCancellationを`cancelled_by_request`へ誤分類し得る。

また、Preempt済みIDは必ず消費される保証がなく、例外経路や別Terminal経路ではSetへ残存し得る。現在のTestは各分岐を個別に通すだけで、同時Terminal Raceとcleanupを確認していない。Reason文字列も二種類のままである。

## 6. IR-CI-04 — WU-03「非問題」は証明されていない

実機TestはUserが報告した入力ではなく`What is the capital of France?`を使い、Guard OBSERVE／ENFORCEのProduction経路も通していない。直接Adapterを二回呼んだだけである。

Oracleも`first_clear == second_clear`なので、二回とも誤ってUnsafeでもPASSする。Category／Match Identity、OBSERVE Action 0、ENFORCE Action 1もAssertしていない。SourceがMode引数を受けないことは直接Mode注入を否定するだけで、未固定Samplingによる実運用上の分類不一致を解消しない。

したがって`WU03_CONFIRMED_NONISSUE`は不受理。元Handoffは必要時のQwen3Guard Role専用Generation Parameter固定を許可していた。

## 7. IR-CI-05 — WU-02のEvidenceは受理、根本原因Claimは不受理

今回のEvidenceは「当該TrialのBatch 3がToken上限到達ではなく不完全JSONで失敗」を示す。Gemma固有Quirk、Sampling、Prompt／Schema、Backend等のどれが原因かまでは一意に特定していない。別時点の複数JSON Object既知事象を、今回の未完JSON断片の根本原因へ直接転用できない。

また元Handoffは、Evidenceが示した場合のRole別Sampling固定を明示的に許可していた。「別途許可が必要だったため未実装」はHandoffの誤読である。Decoder緩和／JSON補修／盲目的Retryは引き続き禁止する。

## 8. IR-CI-06 — WU-05は未実施

元HandoffはProduction Web Composition、実32 Criterion、Recording FULL、実Persistence、同一Turn保存までを要求した。再実行されたTestはHook直結、1 Criterion、`persistent=None`、`recording_mode=off`であり、Test自身も永続化を検証しないと明記している。

これは有効な局所Golden PathだがWU-05の代替ではない。実装者が要求Scopeを事後にScope外化することはできない。WU-05は未実施のまま維持する。

## 9. 次の扱い

受理済みのSnapshot供給改善とBatch Observabilityは保持し、[R2差分Rework Exact Handoff](../../handoffs/phase_9_controller_component_independence_r2_delta_rework_exact_handoff_ja_20260905163632.md)だけを実行する。

Selene、Phase 9-2／9-3、Phase 10、Decoder緩和、JSON補修、無制限Retry、Git操作へ進まない。User Mac再確認前にPhase 9-1 Completeを主張しない。
