# Phase 9-1 — Component完全疎結合 R2 Return Controller独立Review

```yaml
document_type: controller_independent_review
document_state: changes_required
recorded_at: 2026-09-05 18:17:01 JST
language: ja
reviewer_role: codex_controller
review_target: ../../handoffs/phase_9_claude_component_independence_r2_delta_rework_exact_return_ja_20260905175816.md
maximum_claim: P9_1_COMPONENT_INDEPENDENCE_R2_CHANGES_REQUIRED
phase_9_1_closure: false
real_model_action: none
git_mutation: none
append_only: true
```

## 1. 判定

`CHANGES REQUIRED / Phase 9-1 INCOMPLETE`。

R2は有効な進展を含むが、`WU-01／02／03／06 resolved`は過大Claimである。GemmaのMalformed JSONも未解決であり、Phase 9-1 ClosureやUser実画面再確認へは進まない。

## 2. 受理する進展

- Main OFF／Main不在でDedicated JudgeにSemantic Snapshotを供給できる方向の修正。
- Main OFF／absent時の`record_semantic_response()`／`record_semantic_deferred()` Call 0 Gate。
- Dedicated Gemma経路のEvaluated MainとExecuted Judge Artifact／Backend分離。
- GemmaとQwen3Guard限定のDeterministic Sampling。MainとSeleneへ波及させていない。
- Qwen3Guardの同一入力・同一Load SessionによるOBSERVE／ENFORCE比較は、当該一TrialのEvidenceとして受理する。
- Main Governance起点Repair、同一Turn保存、Recording FULLの局所配線は成立方向にある。

Controller Focused Verificationは168 passed。実Modelは再実行していない。

## 3. IR-R2-01 — Turn開始Freezeが一つのImmutable Snapshotになっていない

`ConversationGenerationService.start()`は`runtime_snapshot`と`judge_modes`を取得した後、`semantic_turn_begin_hook(request_id)`だけを呼ぶ。Hookに既得値を渡さないため、`web_application.py`の`_semantic_runtime_context()`がJudge／Repair Mode、Provider、LanguageをLiveで再読みする。

Controller Probeでは、Judge Mode Snapshot取得直後にLive Modeを変えると次を再現した。

```text
Conversation frozen Judge Mode = observe
Semantic begin live Judge Mode  = enforce
Mismatch                       = true
```

したがって「同じAttempt境界の開始値」は未成立である。さらにHook例外は握り潰され、同じ`JudgeSemanticTurnProvider`がJudge Completion時に再呼び出されるため、開始時Freeze失敗後に生成後のLive値で遅延Freezeできる。「開始時に一度だけ」とも矛盾する。

Dedicated AdapterもJudge Completion時に取得されるため、Turn開始時のActive Providerと実行Adapterの一致を検証する必要がある。

## 4. IR-R2-02 — Built-in Evidence Identityは今もMainと混成する

Built-in経路のLive Resultは`executed_provider=built_in.deterministic`だが、`_pending_evidence()`に`context.model_key`と`context.model_runtime_info`を渡している。Controller Probeの実ファイルは次だった。

```text
Live Executed Provider = built_in.deterministic
Evidence model_identity = main.test-model
Evidence artifact/backend/version = Mainの値
Evaluated model_identity = main.test-model
```

ExecutedとEvaluatedを再混同し、Model Call 0のBuilt-inにMain Artifactを帰属させている。R2のTestはDedicated Gemma一経路のみを強く検証し、Handoffが要求したGemma／Main-shared／Built-inの三経路を覆っていない。

## 5. IR-R2-03 — PreemptionのTerminal Raceは残っている

`was_preempted()`の非破壊peek化は有効だが、Background Workerの`finally`が`_preempted_task_ids`をdiscardした後にもENFORCE Terminal Ownerは起源を読む。Workerが先にResultを作って終了し、Terminal Ownerが後から走るScheduleをController Probeで固定すると次を再現した。

```text
Worker reader preempted   = true
Terminal reader preempted = false
Stored failure_reason     = cancelled_by_request
```

現在の16 Reader TestはWorkerをGateで停め、cleanup前の読取だけを検証するためこのRaceを検出しない。

## 6. IR-R2-04 — WU-06は通常32 Criterion Production Web Matrixではない

Fixture Testは`_CRITERION_COUNT = 4`、実機Testは`_bounded_real_criterion()`一件である。どちらもHandoffの「通常選択32／同一32 Rejudge」を検証しない。

また、実機TestはMalformed／`evaluated=0`／Deviation 0を`pytest.skip`へ逃がすが、HandoffはMissing Artifact以外のSKIPを禁止している。Fixture／実機ともProduction Composition Rootを通さず手組みし、R2の`semantic_turn_begin_hook`すら配線していない。このため`WU-06 resolved`は不受理とする。

## 7. IR-R2-05 — Gemma DefectとGuardのClaim境界

GemmaはDeterministic Samplingと一度のPrompt強化後も別BatchでMalformed JSONが再発しており、R2のPartial申告どおり未解決である。現在のSchema Exampleには`short reference`／`short code`が引き続き表示され、後置Ruleで「複写するな」と打ち消している。Provider局所Schemaそのものの非曖昧化が先であり、Decoder緩和／JSON補修／無条件Retryはまだ許可しない。

Qwen3Guardは当該Trialの一致を受理するが、一Trialだけで過去のDivergence原因をSampling非決定性に一意確定はできない。Root Cause Claimのみ訂正する。

## 8. Disposition

[R3残差Rework Exact Handoff](../../handoffs/phase_9_controller_component_independence_r3_residual_rework_exact_handoff_ja_20260905181701.md)のみを次に実行する。Selene、Phase 9-2／9-3、Phase 10、Git操作には進まない。
