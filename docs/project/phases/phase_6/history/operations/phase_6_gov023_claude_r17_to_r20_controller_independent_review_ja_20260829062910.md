# Phase 6 P6-GOV-023 — Claude R17〜R20 Controller Independent Review

```yaml
document_id: phase_6_gov023_claude_r17_to_r20_controller_independent_review_20260829062910
document_type: controller_independent_review
document_state: frozen
language: ja
created_at: 2026-08-29 06:29:10 JST
review_owner: Codex_プロジェクト責任者兼設計統括者役
review_target_provider: Claude
review_target_role: 設計者兼実装者役
review_target_return: phase_6_claude_current_task_r17_to_r20_exact_return_handoff_ja_20260829061552.md
verdict: ADJUST_REWORK_REQUIRED
phase_6_closure: prohibited
phase_7: prohibited
git_action: none
real_model_action: none
user_runtime_data_action: none
```

## 1. 結論

Claude R17〜R20の`Complete Candidate` Claimは、そのままでは受理しない。

```text
Focused Controller Verification: 155 passed
Canonical Evidence reported by Claude: Backend 1744 / Frontend 231 / Mypy 475 / Ruff PASS
Controller verdict: ADJUST / Rework Required
Open Technical Critical: 0 known
Open Technical Major: 3
Open Evidence / Claim Major: 1
Phase 6 Closure: NOT READY
```

R17〜R20には成立した改善がある。一方、Tracked Workerの実完了追跡、Dedicated Role実行LeaseのProduction配線、Qwen3Guard公式Contractの3点が未成立である。さらに66 Acceptance IDの集計と一部DispositionがCurrent Sourceと一致しない。

## 2. Review対象

- `docs/project/phases/phase_6/history/index/phase_6_current_claude_task_r20_final_recovery_ja_20260829061552.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r17_to_r20_exact_return_handoff_ja_20260829061552.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov022_claude_r13_to_r16_controller_independent_review_ja_20260829032604.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r17_to_r20_exact_rework_handoff_ja_20260829032604.md`
- R17〜R20 Current Source／Test／Recovery Index。
- Qwen公式一次資料：
  - `https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B`
  - `https://huggingface.co/Qwen/Qwen3Guard-Gen-0.6B/blob/main/tokenizer_config.json`
  - `https://github.com/QwenLM/Qwen3Guard`

## 3. Controller Verification

Project内Task Tempを用いて次を実行した。

```text
Lifecycle／Atomicity／Correlation／Feature Modes／Web Bootstrap: 85 passed
Judge／Dispatch／Response Language／Failure Presentation: 70 passed
Total Focused: 155 passed
```

Git、Real Model、User runtime_data、外部Model Artifact Mutationは行っていない。

## 4. 成立を確認した改善

1. Provider Selection GET、Feature Modes GETおよびMode／Provider Mutation Responseは、`RoleProviderLifecycleManager.composite_status()`またはMutation自身のComposite Resultを使う経路へ統一された。
2. ON／OFF Transaction中のStatus Readを同一Condition Lockで直列化し、Mode Commit失敗時のCandidate Rollbackも追加された。
3. `RequestCorrelationRegistry`はTurn開始時にbase Request IDを登録し、Turn／Judge／RecordingをServer-sideでJoinする。
4. `ResponseLanguage.AUTO`は最新User Inputの日本語Script有無からTurn内で一度だけ`ja`／`en`へ解決される。
5. Stage Deadline Failure Reasonは、汎用InconclusiveではなくTimeout文言へ分類される。
6. Claudeは自己ReviewでMode Commit Failure、Failure Reason分類漏れ、Correlation RegistryのBootstrap Test Gap等を発見・修正した。

これらは保持し、R0〜R20をRollbackまたは一括再実装しない。

## 5. Open Findings

### P6-CODEX-081 — Tracked Stage Workerの実完了追跡／Shutdown False-clean未解消

```yaml
severity: major
disposition: OPEN_REWORK_REQUIRED
contract_source: P6-RR-R18 item 3
```

`run_tracked_stage()`はCallerをBudget内へBoundし、Late ResultをCallerへ返さない点では改善している。しかし、Timeout時に返される`Future`はPrompt Build／Decodeの両Production Call Siteで参照を破棄される。

`tracked_stage_worker.py`自身にはActive Future Registry、Shutdown、JoinまたはCompletion CallbackによるOwner管理がない。`ModelAccessCoordinator`は外側のJudge Workerだけを追跡し、Prompt／Decodeの内側Workerを追跡しない。このため、Cancellationを無視して走り続けるPrompt／Decode Workerが存在しても、WebRuntime／CoordinatorはClean Shutdownを主張できる。

R18 Contractの「Cancellation無視Workerも実完了まで追跡し、Shutdown／JoinのFalse-cleanを作らない」は未成立であり、P6-CODEX-081はCLOSEDにできない。

### P6-CODEX-086 — Dedicated Judge／Guard実行LeaseのProduction配線が0件

```yaml
severity: major
disposition: OPEN_REWORK_REQUIRED
reopens_acceptance: [P6-RR-ACC-016, P6-RR-ACC-017]
```

`RoleProviderLifecycleManager`には`begin_turn()`／`end_turn()`とActive Turn Drainが実装されている。しかしCurrent Production Source全体で、この2 APIを呼ぶ箇所は0件であり、呼出しはTest内だけである。

Judgeは`active_adapter()`でRaw Adapterを取得した後、Leaseを持たずにBackground実行する。Qwen3GuardもDetectorごとに`active_adapter()`から得たGuard AdapterをLeaseなしで呼ぶ。したがって実Judge／Guard Call中でもLifecycle上の`_active_turns`は0のままであり、Provider切替、Mode OFF、Unload、Shutdownが実行中Adapterと競合できる。

Unit TestでLifecycle単体のActive Turn Drainが動くことは、ProductionでそのLeaseが取得されることのEvidenceではない。よってP6-RR-ACC-016／017のPASS Claimは不成立である。

### P6-CODEX-087 — Qwen3Guard公式Output Contract Manifest欠落に加えDecoder契約が公式正本と不一致

```yaml
severity: major
disposition: OPEN_REWORK_REQUIRED
reopens_acceptance: [P6-RR-ACC-022, P6-DELTA-004]
```

ClaudeはManifest未整備をOpen Majorとして正直に残したが、問題はProvenance欠落だけではない。

Qwen公式Model Cardおよび公式`tokenizer_config.json`のChat Templateは次を要求する。

```text
User Prompt moderation:
  Safety
  Categories

Assistant Response moderation:
  Safety
  Categories
  Refusal
```

Safeの場合も`Categories: None`が要求される。一方Current DecoderはInput／Contextで`Categories`を任意とし、Output Candidateでも`Categories`を任意としている。実際のUnit Testも`Safety: Safe`単独をValid Inputとして固定している。

これは公式ContractをManifest化していないだけでなく、現在のStrict Decoder／Test Fixtureが公式Chat Templateの必須Field契約と一致していない状態である。`verified_official_contract`をBooleanで注入する前に、Immutable Source Identity、Contract Digest、Target別Field順序、Category SetをManifestから検証する必要がある。

### P6-CODEX-084 — 66 ID Acceptance／Claim Auditは個別表が揃ったが最終Claimが不正確

```yaml
severity: evidence_major
disposition: OPEN_CORRECTION_REQUIRED
```

個別表は`P6-RR-ACC-001〜040`と`P6-DELTA-001〜026`の66 Unique IDを含む。しかし実内訳は次である。

```text
P6-RR-ACC: PASS 34 / PARTIAL 1 / N/A 3 / NOT RUN 2 = 40
P6-DELTA : PASS 23 / PARTIAL 3 = 26
Total    : PASS 57 / PARTIAL 4 / N/A 3 / NOT RUN 2 = 66
```

Return記載の`PASS 60`および`合計 66 ID／69行`は算術的に不成立である。また「新規49 tests」は記載内訳`9 + 10 + 14 + 12 = 45`と一致しない。

さらにP6-RR-ACC-016／017は前項のProduction Lease未配線によりPASSではない。P6-CODEX-084は個別行作成までは改善したが、CLOSEDにはできない。

## 6. Preserved Open Items／User Gates

次は本Reviewで新規Failへ昇格しないが、未完了のまま保持する。

- P6-DELTA-014：`failure_at`のBackend実値再読Test不足。
- P6-DELTA-016：Phase 9 Closure手前へ予約済みのFrontend Layout／Sidebar表示項目。
- Real Selene／Qwen3Guard Artifact：NOT RUN。
- Real Browser／User Mac Manual Acceptance：USER GATE。

## 7. Final Disposition

```text
P6-CODEX-080: CLOSED
P6-CODEX-081: OPEN / REWORK REQUIRED
P6-CODEX-082: CLOSED
P6-CODEX-083: CLOSED
P6-CODEX-084: OPEN / CLAIM CORRECTION REQUIRED
P6-CODEX-085: CLOSED
P6-CODEX-086: OPEN / REWORK REQUIRED
P6-CODEX-087: OPEN / REWORK REQUIRED

Controller Verdict: ADJUST
Phase 6 Closure: NOT READY
```
