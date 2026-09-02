# Phase 9-1 Codex Controller Post-Copilot Real Dedicated Independent Review Finding Ledger

```yaml
document_id: phase_9_1_codex_controller_post_copilot_real_dedicated_independent_review_finding_ledger_20260901112423
document_type: append_only_controller_independent_review_finding_ledger
document_state: rework_required
language: ja
created_at: 2026-09-01T11:24:23+09:00
phase: phase_9
program: phase_9_1
review_target: phase_9_copilot_p9_1_real_dedicated_completion_exact_return_handoff_20260901111141
reviewed_claim: P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
controller_disposition: rejected_rework_required
phase_9_1_closure: not_claimed
```

## 1. 結論

Copilot Returnの`P9_1_COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`は受理しない。

P9-CODEX-008／009のLifecycle／Lease修正とRegressionは成立候補として維持する。P9-CODEX-006のProject-derived Contract分離、Digest検証、numeric-string Confidence Decodeも有効な前進である。しかし、Phase 9-1の最低条件であるReal Selene／Qwen3GuardのProduction経路成立、停止・解放、Acceptance再導出を証明するEvidenceが不足し、P9-CODEX-006／007／010は完了していない。

```text
P9-CODEX-006: PARTIAL — 有効修正あり、実運用上限／Deadline／Provenance未成立
P9-CODEX-007: PARTIAL — Static Capability Preflightへの縮小は有効、Stage別実Evidence未成立
P9-CODEX-008: ACCEPTED CANDIDATE
P9-CODEX-009: ACCEPTED CANDIDATE
P9-CODEX-010: PARTIAL — 内部Deadlineは追加、User Stop／Mode OFF／Shutdown Preempt未配線

New Findings:
P9-CODEX-011: CRITICAL / MVP BLOCKER
P9-CODEX-012: MAJOR / MVP LIVENESS BLOCKER
P9-CODEX-013: MAJOR / SEMANTIC COMPLETION BLOCKER
P9-CODEX-014: MAJOR / ACCEPTANCE AND RETURN BLOCKER
```

## 2. Review対象

- Exact Return: `docs/project/phases/phase_9/handoffs/phase_9_copilot_p9_1_real_dedicated_completion_exact_return_handoff_ja_20260901111141.md`
- Recovery: `docs/project/phases/phase_9/history/index/phase_9_1_p9_codex_006_010_real_dedicated_completion_recovery_ja_20260901111141.md`
- Real Evidence: `docs/project/phases/phase_9/history/operations/phase_9_1_copilot_automation_evidence_real_dedicated_ja_20260901111141.md`
- Binding Handoff: `docs/project/phases/phase_9/handoffs/phase_9_copilot_p9_1_three_review_real_dedicated_completion_exact_handoff_ja_20260901034115.md`
- Current Working Tree Source／Test／Phase Index。

Focused Controller Regression:

```text
122 passed in 2.66s

対象:
- Selene Prompt／Decoder
- Dedicated Role Production Wiring Fixture
- Role Lifecycle／Lease
- Qwen3Guard Detector／Adapter
- Provider Selection Role Atomicity
```

Focused Testが通ることはSource修正の回帰防止Evidenceであるが、Real Production CompositionとUser Stop配線の代替ではない。

## 3. P9-CODEX-011 — Real Dedicated Evidenceが再現不能でProduction Compositionを証明しない

Severity: `CRITICAL / MVP BLOCKER`

Real Evidence文書に記録されたCommandは次だけである。

```text
./.venv/bin/python - <<'PY'
# dedicated role adapter preflight/load/inference/unload smoke
PY
```

および、Timeout Probeも同様にCommentだけでScript本体がない。この記録からは、次を再実行・独立検証できない。

- 使用したArtifact Path／Artifact SHA-512。
- Registry Definition／Manifest／Contract Identity。
- Production Web Compositionを経由したProvider Selection／Mode Activation。
- SeleneのSemantic Snapshot、Selected／Evaluated／Deferred総和。
- Judge observe／enforce、Repair→Rejudge、Frozen Provider Identity。
- Qwen3GuardのStrict Safety／Category／Refusal Decode詳細。
- Mode OFF、Active Turn Drain、Real UnloadのState遷移。
- Process Exit、Latency、Token Usage、Loaded Model解放確認。

JSON要約の`result_count=1`と三つの`failure=none`は、Adapterを直接構築したSmoke結果としては有用である。しかしBinding Handoffが必須とした次のProduction経路を証明しない。

```text
Explicit Authority ON
→ Provider Selection
→ Mode ON
→ Production Composition
→ Real Load
→ Real Turn Evidence
→ Mode OFF／Stop
→ Drain
→ Real Unload
```

Return本文では`Mode OFF / unload: success`、`Artifact/manifest identity付きでevidence保持: success`をClaimしているが、Real Evidence JSONにその値・状態遷移・検査Commandが存在しない。したがってReal Selene／Real Qwen3Guard PASSへの昇格を拒否する。

Required Rework:

1. Real Smokeを再実行可能なProject内Scriptまたは完全Commandとして保存する。
2. 実行日時、Exit、Provider、Artifact／Manifest／Contract Digest、Latency／Token、Selected／Evaluated／DeferredをLosslessに記録する。
3. Production API／Compositionを通したMode ON→Turn→OFF→Drain→Unloadを実証する。
4. Direct Adapter Smokeは補助Evidenceとして区別し、Production PASSと同一視しない。
5. Active Process／Loaded Model 0をRead-only State Evidenceで確認する。

## 4. P9-CODEX-012 — Qwen3GuardのCancellationがCaller／User Stop／Mode OFFへ接続されていない

Severity: `MAJOR / MVP LIVENESS BLOCKER`

`Qwen3GuardDetectorAdapter.detect()`は呼出しごとに内部`CancellationToken()`を新規生成し、内部Stage DeadlineでのみCancelする。`detect()`のPortには外部Cancellation引数がなく、Guardrail Hook三種にもTurn Cancellationを渡す契約がない。

```text
Conversation User Stop
→ Conversation Sessionの_cancel_requested／Judge Cancellationだけを更新
→ Guardrail HookへTokenを渡さない
→ Qwen Detectorの内部Tokenとは無関係
```

そのため今回の実装で成立したのは次である。

- 内部Inference BudgetによるBounded Return。
- Timeout後のLate Result不採用。
- Worker完了後のLease Release。
- Registry Drain後のShutdown。

一方、Binding Handoffの必須条件だった次は未成立である。

- User Stopが実Guard Callを即時Preemptする。
- Mode OFFが実Guard CallのTokenをCancelしてDrainへ進める。
- Server Shutdownが既存Deadline待ちではなく実CallをPreemptする。
- 三経路共通のExternal Cancellation IdentityをThread Race Testで確認する。

`Mode OFF`が新規Callを止め、既存Leaseの終了を待つことと、既存CallをPreemptできることは別である。Returnの`P9-CODEX-010: COMPLETE`を`PARTIAL`へ戻す。

Required Rework:

1. Guardrail Hook／Detector PortへTurn-owned Cancellationを配線する。
2. Internal Deadline TokenとExternal User／Mode／Shutdown Cancellationの所有関係を明示する。
3. User Stop、Mode OFF、Shutdownそれぞれを実Threadで強制し、Model Call Cancel、Late Publish 0、Lease exactly-once、Unload後Cleanを独立Testする。

## 5. P9-CODEX-013 — Seleneは1 Criterion Smokeだけで実Semantic負荷／Deadline／Provenanceが未成立

Severity: `MAJOR / SEMANTIC COMPLETION BLOCKER`

有効な修正:

- Official CopyとProject-derived ContractのField分離。
- Derived Template Digest／Project Contract Digestの検証。
- Strict Decoderで有限範囲内numeric-string Confidenceを受理。
- Real GGUFが少なくとも1 CriterionのJSONを返しStrict Decodeできたという観測。

未成立点:

### 5.1 実Criterion数

Current Semantic Runtimeの既定`max_criteria`は32である。Real Evidenceは`result_count=1`だけで、実Turn相当の32 Selected、残Deferred、総和109を証明しない。Project-derived Templateは全Criterionを一つのPrompt／一つのJSONへ入れ、`max_new_tokens=1000`固定である。入力Token Budget、出力Fit、Batch、Call Budgetを事前検証しない。

したがって「1 Criterionは動いた」から「Phase 9-1のSemantic-109経路が実用上成立した」へClaimを上げられない。

### 5.2 Deadline／Cancellation

`SeleneSemanticEvaluator.evaluate()`は`InferenceService.generate()`へCancellation Tokenを渡さず、Selene専用のStage Deadlineも持たない。Main-shared Judge側にはDeadline付きGenerateがあるが、Selene分岐はEvaluatorを直接呼ぶため同じ保護を受けない。

### 5.3 Provenance

Manifestの`derived_from_upstream_revision`は`unknown_network_prohibited`である。これは未確定状態の正直な表示としては評価できるが、Exact Revisionではない。さらにBinding Handoffは、Project内Source不足時にAtla公式SourceへのRead-only取得を許可していた。よってReturnの「derived-from revisionを明示」は、値がExact Revisionであるかのように読めるためClaimを縮小する必要がある。

Required Rework:

1. 実Turn相当Criterion数でPrompt／Output Budgetを測定し、Bounded Batch、明示上限またはTyped Fail-closedへ収束する。
2. Selected＋Evaluated／Unknown＋Deferred＝Applicable総数を実Evidence化する。
3. Selene GenerateへTurn CancellationとStage Deadlineを配線する。
4. Exact Official Revisionを公式Sourceから取得・記録するか、`derived_from_upstream_revision_unverified`等の別Fieldへ分離し、Exact Revision Claimをしない。

## 6. P9-CODEX-014 — Acceptance／Manual／Index／Return Contractが更新されていない

Severity: `MAJOR / ACCEPTANCE AND RETURN BLOCKER`

Binding HandoffはP9-CODEX-006〜010後に次を要求した。

- Phase 9-1 Acceptance全38件をSource／Test／Real Evidenceから個別再導出。
- P9-ACC-008／011をReal Artifact EvidenceでDisposition。
- Corrected User Manualを現在のSelene／Qwen3Guard手順へ更新。
- Phase Index／Current Stateを新しいDispositionへ更新。
- Acceptance全件の最終内訳をReturnへ含める。

Copilotが新規作成したのはRecovery、Real Evidence、Exact Returnの3文書だけである。Current Phase Indexは依然として次を示す。

```text
PASS 35
MANDATORY REAL ARTIFACT NOT RUN 2
USER MANUAL GATE 1
REAL DEDICATED ACTIVATION REQUIRED BEFORE COMPLETE CANDIDATE
```

既存Manualも`RESOURCE_GATED / NOT RUN`前提のままである。Returnには38件の最終内訳がない。この状態でComplete Candidateを返すと、Source／Real Evidence／Acceptance／Current Indexが互いに矛盾する。

Required Rework:

1. P9-CODEX-011〜013解消後、38件を個別再導出する。
2. P9-ACC-008／011を再現可能Real EvidenceからのみPASSへ上げる。
3. P9-ACC-037のUser Manualを実際の起動Flag／順序／表示／Stop／OFF／Unloadへ同期する。
4. Current Phase Index、Recovery、ReturnのClaimと内訳を一致させる。

## 7. Accepted Work

次は理由なくRollbackしない。

- Candidate Load失敗後のBest-effort Cleanup／Rollback／DEGRADED収束。
- Active Lease Identity Registry、Duplicate／Stale／Forged Release拒否、Exactly-once Release。
- Qwen3Guard AdapterへのCancellation Token伝播自体。
- Qwen3Guard内部Deadline、Tracked Worker、Timeout後Late Publish 0。
- Selene Project-derived Templateの独立DigestとProject Contract Digest。
- numeric-string Confidenceの有限／範囲内Strict Decode。
- Controller Focused 122 PASS。

これらの有効性と、Phase 9-1 Complete Candidate不成立は両立する。

## 8. Current Stop Line

```text
Maximum Claim:
P9_1_REWORK_REQUIRED_AFTER_COPILOT_REAL_DEDICATED_REVIEW

Real Selene PASS:
NOT ACCEPTED

Real Qwen3Guard PASS:
NOT ACCEPTED

Phase 9-1 Complete Candidate:
false

Phase 9-1 Closure:
false

Phase 9-2:
not started
```
