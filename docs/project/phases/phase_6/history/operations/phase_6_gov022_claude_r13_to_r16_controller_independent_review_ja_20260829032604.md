# Phase 6 P6-GOV-022 — Claude R13〜R16 Controller Independent Review

```yaml
document_id: phase_6_gov022_claude_r13_to_r16_controller_independent_review_20260829032604
document_type: controller_independent_review
document_state: frozen
language: ja
created_at: 2026-08-29 03:26:04 JST
review_owner: Codex_プロジェクト責任者兼設計統括者役
review_target_provider: Claude
review_target_role: 設計者兼実装者役
review_target_return: phase_6_claude_current_task_r13_to_r16_exact_return_handoff_ja_20260828233354.md
verdict: ADJUST_REWORK_REQUIRED
phase_6_closure: prohibited
phase_7: prohibited
git_action: none
network_action: none
real_model_action: none
user_runtime_data_action: none
```

## 1. 結論

Claude R13〜R16の`Complete Candidate` Claimは、そのままでは受理しない。

```text
Technical regression baseline: PASS
Frozen Contract completion: FAIL
Controller verdict: ADJUST / Rework Required
Open Technical Critical: 0 known
Open Technical Major: 4
Open Evidence / QA Major: 2
Phase 6 Closure: NOT READY
```

R13〜R16には成立した改善がある。しかし、P6-CODEX-074〜078をすべてCLOSEDとするClaimはCurrent SourceとEvidenceに一致しない。P6-CODEX-080〜085として差分を再Openする。

## 2. Review対象

- `docs/project/phases/phase_6/history/index/phase_6_current_claude_task_r16_final_recovery_ja_20260828233354.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r13_to_r16_exact_return_handoff_ja_20260828233354.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov021_copilot_r9_to_r12_controller_independent_review_ja_20260828214107.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_post_copilot_r13_to_r16_corrected_continuation_handoff_ja_20260828221510.md`
- R13〜R16のCurrent Source／TestおよびRecovery Index。

## 3. 成立を確認した改善

1. Provider Selection変更とMode ApplyのMutation Callerは、`RoleProviderLifecycleManager`へ集約された。
2. Built-in Judgeは同期実行となり、Model Call 0／0ms Background Raceを除去した。
3. Judge Inference、Repair Generation、RejudgeにはTimer由来のCancellationが追加された。
4. 明示`ja`／`en`では、Turn側`response_language`がSemantic Snapshot非依存でJudge／Repairへ渡る。
5. Turn Recording HookはFrozen Recording Modeを受け取る経路へ修正された。
6. Backend Full 1701 passed、Mypy 471 files／0 issues、Ruff Check PASS、Frontend 231 tests／Typecheck／Lint／Build PASSという回帰Baselineは成立している。

これらは保持し、R0〜R16をRollbackまたは一括再実装しない。

## 4. Controller Focused Verification

Project内Task-owned Tempだけを使用した。

```text
Task Temp:
.venv/.t/codex_r13_r16_independent_review_20260829/

Focused Backend:
41 passed / Exit 0

Focused Ruff Check:
PASS / Exit 0

Focused Ruff Format Check:
FAIL / Exit 1
tests/integration/web/test_feature_modes_routes.py would be reformatted
```

対象Testは次の境界を含む。

- Role Lifecycle
- Provider／Mode Atomicity
- Feature Modes／Recording Correlation
- Stage Budget／Failure Presentation
- Recording Live Integration

さらに、Status ReaderがTransition Lockを共有していないことを診断コードで実際に再現した。

```text
Transition Thread:
  Provider Runtime StateをACTIVEへ更新
  -> Mode Commit直前で意図的に停止

Concurrent Reader Observed:
  provider_state = active
  active_provider = built_in.deterministic
  mode = off
```

したがって「Status Readerは旧Tupleまたは新Tupleだけを観測する」というR13 Claimは成立しない。

## 5. Open Findings

### P6-CODEX-080 — Status Readを含むAtomic Tuple未成立

```yaml
severity: major
reopens: [P6-CODEX-074, P6-CODEX-069, P6-CODEX-062]
```

`apply_mode_transition()`と`apply_provider_selection()`のMutation同士は同じ`self._condition`で直列化された。しかし次は同じLockを取得しない。

- `provider_selection_routes.get_provider_selection()` → `ProviderSelectionController.snapshot()`
- `feature_modes_routes.get_status()` → Mode Controller／Provider Controller／Judge Compositionを個別読取
- Mode Apply POST完了後の`_project_status(runtime)`

`_activate_locked()`はProviderをACTIVEへ更新した後にModeをCommitする。この間、独立Lockを使うStatus Readerは`Active Providerあり／Mode OFF`を観測できる。OFF方向もMode Commit後、Provider Deactivate前の中間Tupleを観測できる。

R13 Contractが要求したProvider Selection GET、Feature Modes GET、Mode Apply Response、Provider Apply Responseの完全Tuple Projectionは未成立である。

### P6-CODEX-081 — Prompt Build／DecodeのStage-owned Deadline未成立

```yaml
severity: major
reopens: [P6-CODEX-075, P6-CODEX-070, P6-CODEX-065]
```

`stage_deadline()`はJudge Inference、Repair Generation、RejudgeのModel CallへPreemptive Cancellationを追加した。一方、同ModuleのDocstringが明記する通り、Prompt BuildとDecodeは依然として完了後のElapsed Time比較だけである。

R14 ContractはPrompt Build、Judge Inference、Decode、Repair Generation、Rejudgeの各Stageが自身のDeadline／Cancel／Terminal Ownerを持つことを要求した。Prompt／Decodeを「同期CPU処理なので後検査だけ」として除外する変更は、ControllerによるContract変更を受けていない。

Prompt／DecodeをTracked Worker等へ分離し、Deadline後のLate Publish拒否と実Worker完了追跡を成立させる必要がある。

### P6-CODEX-082 — Request-ID Correlation Registry／Server-side Join未成立

```yaml
severity: major
reopens: [P6-CODEX-077, P6-CODEX-072, P6-CODEX-067]
```

R15実装はRecording Current IDをJudge Compositionから`recording_composition.last_outcome()`へ移した。これはJudge OFF Turnの「完了後」の誤Joinを一部改善するが、要求した共有Correlation Registryではない。

現行`RecordingCorrelationResponse`は次だけを持つ。

- Current Turn Recording Outcome
- Current Judge Evidence Recording Outcome
- Historical／Unmatched Recording

Judge Result、Final Disposition、Failure、Configured／Active／Executed Provider、Budget、Frozen Modes、開始／完了時刻は同じServer-side Correlation ObjectへJoinされていない。実行中TurnではTurn Recording Outcomeがまだ存在しないため、Current Requestを新Turnへ切り替えられず、過去TurnをCurrentに残し得る。

これはUser Macで確認済みの「送信後に設定を開くと一つ前、開き直すと最新」というObservability Lagを構造上残す。

### P6-CODEX-083 — Response Language `auto`が英語へ縮退

```yaml
severity: major
reopens: [P6-CODEX-076, P6-CODEX-071, P6-CODEX-066]
```

`ConversationGenerationSession._invoke_judge_completion_hook()`は次の二値化を行う。

```text
ResponseLanguage.JA -> ja
それ以外           -> en
```

したがって正式な第三値`ResponseLanguage.AUTO`は常に`en`へ変換される。日本語User Turn＋回答言語AUTOでも、Judge Timeout／Unavailable等のFailure Presentationが英語になる可能性が残る。

Turn開始時に`ja`／`en`／`auto`をそのまま凍結するだけでなく、AUTOの場合の実効Failure Languageを決定論的に解決し、Judge、Repair、Rejudge、Fallback全経路へ同じ値を渡す必要がある。

### P6-CODEX-084 — R16 Acceptance／Claim Audit Contract未充足

```yaml
severity: major_evidence
reopens: [P6-CODEX-078, P6-CODEX-073, P6-CODEX-068]
```

R16 ContractはRemaining Rework Acceptance 40＋Delta Acceptance 26を66 ID個別に再導出することを要求した。しかしReturnは次の状態である。

- Required 40の正本は`phase_6_remaining_rework_execution_plan_and_acceptance_ja_20260825130924.md`にある`P6-RR-ACC-001〜040`である。
- Returnは別のPhase-wide Matrixである`phase_6_acceptance_matrix_ja.md`の`P6-ACC-001〜040`を「Original Acceptance 40」として使用した。これはIDも要件も異なる別Setである。
- その誤った40件についてもSource文書への一括Pointerだけで、個別Dispositionなし。
- Delta 26: R13〜R16直接対象の10 IDだけ個別表示。
- その他16 ID: Full Suite PASSを理由に一括して「既存Coverage維持」とした。

Full Suite PASSは各Acceptance IDの要件充足を自動的に証明しない。正しい`P6-RR-ACC-001〜040`＋`P6-DELTA-001〜026`の66 IDすべてに`PASS／PARTIAL／NOT RUN／USER GATE／FAIL`とEvidence Pointerが必要である。Phase-wide `P6-ACC-001〜084`と混同しない。

またCanonical `ruff format --check src tests`はExit 1であり、変更対象の`tests/integration/web/test_feature_modes_routes.py`も非Canonicalである。「Canonical Static全PASS」とは主張できない。

### P6-CODEX-085 — S4／S9／S12／S13をPASSへ昇格できない

```yaml
severity: major_evidence
reopens: [P6-CODEX-078]
```

Claude自身がCaveatを記録しているため隠蔽ではないが、字義どおり未検証のScenarioを`PASS（Caveat付き）`とするのは不正確である。

- S4: Guard OBSERVEのScenarioに対しENFORCE Testだけ。
- S9: Frozen Selene Judge→Repair→同一Provider RejudgeのLive Hook連結なし。
- S12／S13: Timeout／UnavailableはPresentation関数単体だけで、JA／ENのLive Turn経路なし。

現時点の正確なDispositionは`PARTIAL`である。Fixture／Fake AdapterでAuthority不要のE2E Coverageを追加できるため、Real Model Authority待ちにはしない。

## 6. 最終Disposition

```text
P6-CODEX-080: OPEN / REWORK REQUIRED
P6-CODEX-081: OPEN / REWORK REQUIRED
P6-CODEX-082: OPEN / REWORK REQUIRED
P6-CODEX-083: OPEN / REWORK REQUIRED
P6-CODEX-084: OPEN / REWORK REQUIRED
P6-CODEX-085: OPEN / REWORK REQUIRED

R13〜R16 preserved improvements: ACCEPTED AS PARTIAL BASELINE
Claude Complete Candidate: REJECTED
User Mac Manual Acceptance: NOT READY
Phase 6 Closure: NOT READY
```

## 7. Exact Next Action

Current Claude Taskを維持し、R17〜R20の差分Reworkだけを実行する。Fresh Task化、Role Bootstrap、全Docs再読、R0〜R16の再実装は不要である。
