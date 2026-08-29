---
document_id: phase_6_gov024_claude_r21_to_r24_controller_independent_review_20260829101215
document_type: controller_independent_review
document_state: frozen
language: ja
created_at: 2026-08-29 10:12:15 JST
review_owner: Codex_プロジェクト責任者兼設計統括者役
review_target_provider: Claude
review_target_role: 設計者兼実装者役
review_target_return: phase_6_claude_current_task_r21_to_r24_exact_return_handoff_ja_20260829091444.md
verdict: ADJUST_REWORK_REQUIRED
phase_6_closure: prohibited
phase_7: prohibited
git_action: none
real_model_action: none
user_runtime_data_action: none
---

# Phase 6 P6-GOV-024 — Claude R21〜R24 Controller Independent Review

## 1. 結論

Claude R21〜R24は、Production Lease配線、Tracked Worker Registry、Qwen3Guard公式Source取得およびAcceptance集計を前進させた。しかし`Complete Candidate with Real Provider and User Manual Gates`は受理しない。

```text
Controller Focused Tests: 77 passed
Controller Negative Probes: 3 reproduced failures
Verdict: ADJUST / Rework Required
Open Technical Major: 3
Open Evidence / Governance Major: 1
Phase 6 Closure: NOT READY
```

R0〜R24の成立済み差分は保持し、Rollbackまたは一括再実装しない。R25以降は本Reviewで再現した競合と未完了Evidenceだけを差分修正する。

## 2. Review対象

- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r21_to_r24_exact_return_handoff_ja_20260829091444.md`
- `docs/project/phases/phase_6/history/index/phase_6_current_claude_task_r21_recovery_ja_20260829084104.md`
- `docs/project/phases/phase_6/history/index/phase_6_current_claude_task_r22_recovery_ja_20260829084917.md`
- `docs/project/phases/phase_6/history/index/phase_6_current_claude_task_r23_recovery_ja_20260829090242.md`
- `docs/project/phases/phase_6/history/index/phase_6_current_claude_task_r24_final_recovery_ja_20260829091318.md`
- R21〜R24 Current Source／Test。
- Qwen公式Hugging Face Exact Revision：`Qwen/Qwen3Guard-Gen-0.6B@fada3b2f655b89601929198343c94cd2f64d93cc/tokenizer_config.json`。

## 3. 成立を確認した改善

1. Judge／Guard Production Call SiteへRole Turn Lease取得／解放が実配線された。
2. Prompt Build／Decode Workerを共有Registryへ登録し、WebRuntime Close前にShutdown結果を確認する経路が追加された。
3. Checked-in Qwen3Guard Manifestの現在内容は、Qwen公式Exact RevisionのChat TemplateにあるInput 2行、Output 3行、Inputのみ`Jailbreak`を含むCategory Setと整合する。
4. DecoderはSafeでも`Categories: None`を要求し、Wrong Order／Wrong Target Categoryを拒否する。
5. 66 IDの算術は`59 + 2 + 3 + 2 = 66`として正しく再計算された。
6. ClaudeはImplementation Freeze後にInternal Reviewを行い、`_unload_locked()`のException時非対称性を自ら発見して記録した。

これらは保持する。ただし「Sourceから導出した現在のManifest内容が正しい」ことと、「Runtime Manifest Validatorが偽Contractを拒否できる」ことは別である。

## 4. Controller Verification

Project内Task Tempを用いたFocused Testは次のとおり。

```text
test_tracked_stage_worker.py
test_role_lifecycle_manager.py
test_judge_live_integration_dispatch_router.py
test_qwen3guard_detector_adapter.py
test_qwen3guard_manifest.py
test_qwen3guard_adapter.py

Result: 77 passed
```

既存Testは全てPASSした。一方、次の未収録Negative Probe 3件はCurrent Sourceで再現した。

```text
Probe A:
  shutdown_clean=True
  worker_started_after_shutdown=True
  registry_active_after_clean=1

Probe B:
  state_after_off=degraded
  failure_reason=active_turn_drain_pending
  new_lease_after_off=True

Probe C:
  provider_id=wrong.provider
  required_fields=(Wrong,)
  categories=(FakeInput,)
  is_complete_and_verified=True
```

Git、Real Model、User runtime_data、Model Artifact Mutationは行っていない。

## 5. Open Findings

### P6-CODEX-088 — Tracked Worker AdmissionとShutdownのTOCTOU

```yaml
severity: major
disposition: OPEN_REWORK_REQUIRED
reopens_acceptance: [P6-RR-ACC-017]
```

`run_tracked_stage()`は、`registry.accepting_new_work()`、`executor.submit(work)`、`registry.track(future)`を別々に実行する。Shutdownはその間に`_accepting=False`と現在の`_active` Snapshotを取得できる。

Controller Probeでは、受付確認後かつSubmit前にShutdownを通すことで、Shutdownが`True`を返した後にWorkerが開始し、Registryへ1件残る状態を再現した。これはR22の「Shutdown開始後の新規受付0」「Cancellation無視Workerが残る場合False」「False Clean 0」を満たさない。

既存の「先にShutdownを完了してからSubmitする」直列Testは、このCheck-to-Submit Raceを検証していない。P6-CODEX-081は完全には閉じておらず、P6-CODEX-088として差分再Openする。

### P6-CODEX-089 — Mode OFF／Drain待ち後も新規Role Leaseを発行する

```yaml
severity: major
disposition: OPEN_REWORK_REQUIRED
reopens_acceptance: [P6-RR-ACC-016, P6-RR-ACC-017]
```

`begin_role_turn()`はAdapter存在と`_shutting_down`だけを確認し、Selectionが`ACTIVE`か、`active_provider`がAdapterと一致するか、Roleが`_pending_unload`かを確認しない。

既存Leaseを保持したままMode OFFへ遷移すると、Selectionは`DEGRADED / active_turn_drain_pending`となる。しかしその状態でもController Probeは新しいLease取得に成功した。これにより、OFF後の新規Model Call拒否が成立せず、Drain／Unloadを延長できる。

さらにClaude自身が`IR-R24-001`として記録した通り、`_unload_locked()`はUnload Exception時にAdapterをMapへ残す。そのAdapterへも`begin_role_turn()`は新しいLeaseを発行し得る。これは単なるObservationではなく、Unavailable／Degraded Adapterの再実行を許すProduction Lifecycle Failureである。

### P6-CODEX-090 — Qwen3Guard Manifestが偽ContractをVerified扱いする

```yaml
severity: major
disposition: OPEN_REWORK_REQUIRED
reopens_acceptance: [P6-RR-ACC-022]
```

現在の`is_complete_and_verified`は、BooleanがTrueで、Revision／Digest／Category／Mappingが空でないことだけを確認する。次を検証しない。

- Official Repository Identity。
- Exact Revision形式。
- Provider ID／Label Schema ID。
- `Safety`／`Categories`／`Refusal`のExact Field順序。
- Safety／Refusal Label Set。
- Input 9／Output 8 CategoryのExact Set。
- Category MappingがCategory Unionを過不足なく覆うこと。
- Adapterへ渡された`model_id`とManifest `provider_id`の一致。

Controller Probeでは、Provider、Schema、Source、Required Fields、Category Setを全て偽物へ置換しても`is_complete_and_verified=True`となった。現在Checked-in Manifestの内容自体は公式Sourceと整合するが、Runtime GateはManifest破損／誤BindingをFail-closedにできない。

### P6-CODEX-091 — Qwen3Guard実Provider IdentityがGuard Evidenceで消失する

```yaml
severity: evidence_major
disposition: OPEN_REWORK_REQUIRED
reopens_acceptance: [P6-DELTA-004]
```

`Qwen3GuardClassification`は`model_id`、Exact Revision、Artifact SHA-512、Contract Manifest Digest、Schema IDを保持する。しかし`Qwen3GuardDetectorAdapter.detect()`はGeneric `GuardDetection`へ変換する際にCategory／Outcome／Confidence／Severityだけを残し、実Provider Identityを破棄する。

R21〜R24 HandoffはR23 item 6としてResultとEvidenceへのIdentity保持を明示要求していた。Claude ReturnもP6-DELTA-004をPARTIALのまま残しており、「未実装項目0」「Real Provider／Browser以外完了」とするClaimとは両立しない。Guard Evidenceの正本または型付きProvenanceへIdentityを保持し、Round-trip Testが必要である。

## 6. Acceptance再導出

R24集計をBaselineとし、次をPASSからPARTIALへ戻す。

- P6-RR-ACC-016：OFF後の新規Leaseを拒否できない。
- P6-RR-ACC-017：Worker Shutdown False-cleanとRole Drain競合が残る。
- P6-RR-ACC-022：Checked-in値は取得済みだがManifest Validationが偽Contractを拒否しない。

P6-DELTA-004およびP6-DELTA-016はPARTIALを維持する。

```text
PASS    : 56
PARTIAL : 5
N/A     : 3
NOT RUN : 2
Total   : 66
```

## 7. Final Disposition

```text
P6-CODEX-081: PARTIALLY RESOLVED / superseded by P6-CODEX-088
P6-CODEX-084: CLOSED (arithmetic correction retained)
P6-CODEX-086: PARTIALLY RESOLVED / superseded by P6-CODEX-089
P6-CODEX-087: PARTIALLY RESOLVED / superseded by P6-CODEX-090 and 091
P6-CODEX-088: OPEN
P6-CODEX-089: OPEN
P6-CODEX-090: OPEN
P6-CODEX-091: OPEN

Controller Verdict: ADJUST
Phase 6 Closure: NOT READY
```

Real Selene／Qwen3Guard ArtifactおよびReal Browser Gateは未実施のまま保持する。
