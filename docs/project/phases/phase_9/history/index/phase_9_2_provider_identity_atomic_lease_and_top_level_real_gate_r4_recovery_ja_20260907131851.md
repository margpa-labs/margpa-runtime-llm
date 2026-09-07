# Phase 9-2 Provider Identity / Atomic Lease / Top-level Real Gate R4 Recovery

```yaml
document_id: phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_recovery_20260907131851
document_state: full_recovery
language: ja
created_at: 2026-09-07T13:18:51+09:00
phase: phase_9
program: phase_9_2
```

## 1. Current Point

Codex Controller R3 Return Independent Review（`phase_9_2_controller_r3_return_independent_review_and_r4_rework_decision_ja_20260907104830.md`、判定`INCOMPLETE_FOR_USER_MANUAL`、Confirmed Findings IR-P9-2-R3-01〜06）を受け、同時に発行されたR4 Exact Handoff（`phase_9_controller_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_handoff_ja_20260907104830.md`）のR4-WU-01〜05を依存順に実施した。6件のConfirmed Finding（CRITICAL 2件、MAJOR 4件）を全件解消し、Top-level実Model Gateも最大3 Scenario全てを実際に実行して全て`completed`で終了した。Exact Returnを新規Fileとして提出、Codex Controller Independent Review待ち。

## 2. What Changed

- **Provider Identity Mismatch検出（R4-WU-01、IR-P9-2-R3-01 CRITICAL修正）**: `find_mismatched_slots()`にSelector比較を追加（Variantが`selector_id`を宣言した場合のみ、Modeと同時にProvider一致も要求）。`overlay_variant_onto_snapshot()`のバグ（Variant宣言時にLiveのSelectorを無条件で消していた）を修正。Production 3 Presetに`QWEN_MAIN`/`GEMMA_E2B_JUDGE`/`QWEN3_GUARD`を明示。
- **Full Snapshot Provider Identity（R4-WU-01、IR-P9-2-R3-03 MAJOR修正）**: 新規`ProviderIdentityEnvelope`（Configured/Active/ExpectedExecuted/ArtifactDigestを分離Field化、Main/Judge/Guardのみ）。Run Snapshot永続化時に`provider_identity`と、Case/Plan/Variant/Run Digestを相関させる`correlation`Blockを追加。
- **Live MatchとLeaseの原子化（R4-WU-02、IR-P9-2-R3-02 CRITICAL修正）**: 最終Live読取・照合・Frozen保存・実Actor呼出し・事後再確認の全シーケンスを、Worker側で既にLease取得済みのClosure内部へ完全移設。Route側の元の照合は同期409のためのAdvisory Pre-checkとしてのみ残し、Frozen保存はしない。Lease未配線時はTyped Call 0（`CONFIGURATION_LEASE_UNAVAILABLE`）へ収束、無保護Fallbackなし。
- **HTTP Lease実配線証明（R4-WU-02/05、IR-P9-2-R3-06 MAJOR修正）**: 実FastAPI Middleware経由で、実行中Production Runの間`POST /api/v5/feature-modes/judge`が`409`、完了後は復旧することを新規Testで確認。
- **Queue Future取消Cleanup（R4-WU-03、IR-P9-2-R3-04 MAJOR修正）**: `Future.cancel()`成功時に`_in_flight`とTimerを即座かつ冪等にCleanupする経路を新設、`_on_deadline()`/`request_cancel()`両方から共通利用。
- **Top-level実Model Gate（R4-WU-04、IR-P9-2-R3-05 MAJOR修正）**: 新規`build_phase1_web_runtime()`（Monkeypatchなし）経由の実HTTP Route Testを実装し、Resource Preflightを`memory_pressure`自身のSystem-wide指標（78-79% free、健全）で確認した上で実行。Main-only／Main+Gemma Judge/Repair ENFORCE／Main+Qwen3Guard ENFORCEの3 Scenario全てが`completed`。各SscenarioでRestart Read（独立した新規`LocalFilesystemExperimentStore`）を確認。
- **UI Provider Identity表示（R4-WU-01/05）**: `ExperimentPanel.tsx`のComponent表示にSelector（Provider識別子）を追加、Preset選択リストとComparison Tableの両方に反映。

## 3. Files Created This Round

- `src/margpa_runtime_llm/modules/experiment/domain/provider_identity.py`
- `tests/unit/experiment/test_provider_identity.py`
- `tests/unit/bootstrap/test_experiment_live_configuration.py`
- `tests/integration/test_real_top_level_experiment_production_gate_smoke.py`
- `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_ja_20260907131851.md`（本Roundの正本Return）
- 本File（Recovery Index）

## 4. Exact Return Handoff

[phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_ja_20260907131851.md](../../handoffs/phase_9_claude_phase_9_2_provider_identity_atomic_lease_and_top_level_real_gate_r4_exact_return_ja_20260907131851.md)

Maximum Claim: `P9_2_R4_USER_MANUAL_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW`

## 5. Verification Summary

- Provider/Snapshot Focused Unit: `test_config_snapshot_mismatch.py`（14件、新規5件）、`test_provider_identity.py`（新規4件）、`test_experiment_live_configuration.py`（新規4件）全Pass。
- Atomic Lease Race/Queue Cleanup: `test_run_worker.py`（14件、新規1件＋既存2件へAssert追加）全Pass。
- Production Web Middleware: `test_experiment_routes.py`（24件、新規6件）全Pass。
- Backend Non-model Full Suite: `2649 passed, 43 deselected`（83.71秒）。R3終了時点`2629 passed, 40 deselected`から純増20件。
- Ruff（Whole Repo）: `All checks passed!`。
- Canonical Mypy（Whole Repo）: `43 errors/4 files`（既存Baseline完全一致）。
- Frontend: `npm test`（331件全Pass）、`tsc --noEmit`/`eslint .`/`npm run build`いずれも成功。
- Sabotage-regression 3件（Selector比較除去、Lease内最終照合の外出し、Future Cancel時Cleanup除去）全て検出力確認・Byte-identical復元確認済み。
- 実Model Gate: **3/3 Scenario実行、全て`completed`**（Apple Silicon実機、逐次23.84秒、Exact Return第2.4節に詳細）。実行後Modelプロセス残存ゼロ確認済み。

## 6. Open Items at This Point

- Guard Evidence相関は引き続き`unavailable_correlation`（`called=None`）——真の相関機構自体はPhase 9-1側に存在せず今Round対象外。
- `main_called`曖昧Error Code問題はPhase 9-1側の改修待ち（Scope外）。
- Definition Set/RAG/Presentationの3 Slotは引き続きLive Controller不在（R2から継続、対象外）。
- 実Model Gateの3 Scenarioは各1 Trialのみ（Handoff自身の上限に従う逐次実行）——複数Trialでの再現性確認は未実施。
- Provider Identity/CorrelationはStore層のみに追加、Web API DTOへは未露出（Confirmed Blockerではないため今Round対象外）。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-2 Complete、Phase 9-3着手、Phase 9 Closure、追加の実Model実行のいずれも、本Returnの範囲では行わない。次の指示を待つ。
