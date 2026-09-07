# Phase 9-1 Component完全疎結合／Gemma／Guard／Main Rework Recovery

```yaml
document_id: phase_9_1_component_independence_gemma_guard_main_rework_recovery_20260905141600
document_state: complete_recovery
language: ja
created_at: 2026-09-05T14:16:00+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 12:16:55 JST Exact Handoff(Component完全疎結合／Gemma／Guard／Main Rework)への対応として、WU-01からWU-05までを順に実施した。WU-01(独立Turn Context境界)とWU-04(Cancellation起源分類・Evidence Identity契約)は、いずれもSource修正・新規Test・Sabotage-regressionによる検出力証明まで含めて確定的に解決した。WU-02(Gemma通常初回Judge)は実機Batch別Observabilityで実Evidenceを取得し、当初仮説(最初のBatchで停止)を明示的に反証したが、根拠なき修正は避け、未解決のまま正直に報告した。WU-03(Qwen3Guard Mode非依存)はSource構造上Mode非依存であることを確認し、実機1回の同一条件2回呼び出しでも非決定性は再現せず、修正は不要と判断した。WU-05(Main起点Repair)は既存Golden Path実機Testの再PASSに留め、Full「Production Web Composition」Matrixの新規構築はScope外として明示的に見送った。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `runtime_governance.py`/`web_application.py`: Main非依存の`build_neutral_semantic_runtime()`/`JudgeSemanticTurnProvider`を新設し、Main OFF/不在でもDedicated Judgeが独立してSnapshotを得られるよう配線変更。
- `judge_live_integration.py`: `judge_run_evidence`の`model_identity`を実行Providerベースへ修正(3箇所)。Cancellation分類を`ModelAccessCoordinator.consume_preemption()`ベースへ修正(2箇所)。
- `model_access_coordinator.py`: `consume_preemption()`機構を新設(Main優先Preemptionを外部から検出可能に)。
- 新規Test File 2本(`test_runtime_governance_component_independence.py`、`test_real_local_qwen3guard_mode_independence_smoke.py`)、既存Test File複数への追加・修正。
- Source修正は上記4Fileのみ。Decoder/Prompt/Schema/Batching/Frontend/Seleneは無変更。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_gemma_guard_main_rework_exact_return_ja_20260905141500.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_component_independence_gemma_guard_main_rework_exact_return_ja_20260905141500.md](../../handoffs/phase_9_claude_component_independence_gemma_guard_main_rework_exact_return_ja_20260905141500.md)

Maximum Claim: `P9_1_COMPONENT_INDEPENDENCE_WU01_AND_WU04_RESOLVED_WU02_REAL_EVIDENCE_ONLY_WU03_CONFIRMED_NONISSUE_WU05_CORE_RECONFIRMED`

## 5. Open Items at This Point

- WU-02(Gemma通常初回Judge)は未解決——次の一手はCodex Controllerの明示的指示待ち。
- WU-03は1回のTrialでの非再現に留まる——恒久的な非決定性排除の証明ではない。
- WU-05のFull「Production Web Composition」Matrixは今回未構築——WU-02解決後の実施が望ましいと考える。
- Cancellation Reason文字列(`preempted_by_main_priority`/`cancelled_by_main_priority_preemption`)の命名不統一が残存。
- 拒否文二重表示(既存の弱Finding)は今回も未着手のまま維持。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手、追加の実機Trialのいずれも行わない。
