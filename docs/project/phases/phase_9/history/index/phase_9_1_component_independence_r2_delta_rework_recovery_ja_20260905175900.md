# Phase 9-1 Component完全疎結合 R2差分Rework Recovery

```yaml
document_id: phase_9_1_component_independence_r2_delta_rework_recovery_20260905175900
document_state: complete_recovery
language: ja
created_at: 2026-09-05T17:59:00+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 16:36:32 JST Controller Review(`CHANGES REQUIRED / Phase 9-1 INCOMPLETE`、IR-CI-01〜06)を受け、同時刻発行のR2差分Rework Exact Handoffに従い、R2-WU-01からR2-WU-06までを順に実施した。R2-WU-01(中立Turn境界の真の分離)、R2-WU-02(Executed/Evaluated/Artifact Identity分離)、R2-WU-03(Cancellation起源のRace-free化)、R2-WU-05(Guard同一条件検証)、R2-WU-06(Production Web Composition)の5件は解決を確認した。R2-WU-04(Structured Role Generation局所固定)はSampling固定の実装・検証は完了したが、認可された2回の実機Trial(1回のPrompt局所強化を挟む)を経てもGemma初回32 Criterion JudgeのMalformed JSON Fragment Defectは間欠的に残存し、部分解決として正直に報告した。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `runtime_governance.py`: `begin_semantic_turn()`をpeer read-or-begin化。`record_semantic_response()`/`record_semantic_deferred()`にMain OFF/absent Call-0 Gateを追加。
- `conversation_generation.py`/`web_application.py`: `semantic_turn_begin_hook`を新設し、Evaluation Turn ContextをConversation Turn開始時に一度だけFreezeするよう変更。
- `judge_live_integration.py`/`recording_live_integration.py`: Judge Evidenceへ`evaluated_model_identity`/`configured_judge_provider`/`active_judge_provider`を追加、Dedicated Judge経路の`model_runtime_info`を実行Adapter自身のものへ正しく分離。
- `model_access_coordinator.py`/`judge_live_integration.py`: `consume_preemption()`(一発消費)を`was_preempted()`(非破壊peek)へ置換、Terminal(`start_background`の`_run()`finally)で一度だけcleanup。Reason文字列を統一。
- `selene.py`/`dedicated_role_adapters.py`/`qwen3guard_adapter.py`: Gemma JudgeとQwen3Guard専用の決定的Generation Sampling Contract(temperature=0/top_k=1/seed=0等)を局所注入。Selene/Main-shared/Main会話Defaultは無変更。
- `config/judge_templates/gemma_4_e2b/*`: 認可された1回のみのPrompt局所強化(Rule 6)とManifest Digest再計算。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_r2_delta_rework_exact_return_ja_20260905175816.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_component_independence_r2_delta_rework_exact_return_ja_20260905175816.md](../../handoffs/phase_9_claude_component_independence_r2_delta_rework_exact_return_ja_20260905175816.md)

Maximum Claim: `P9_1_R2_WU01_WU02_WU03_WU05_WU06_RESOLVED_WU04_SAMPLING_FIX_VERIFIED_JSON_DEFECT_NARROWED_NOT_ELIMINATED`

## 5. Open Items at This Point

- R2-WU-04: Gemma初回32 Criterion JudgeのMalformed JSON Fragment Defectが間欠的に残存——次の一手はCodex Controllerの明示的判断待ち。
- R2-WU-06実機Trialは初回Candidateを決定的Fixed文字列としており、Main自身の実Generation誤答ケースは未確認(意図的なScope選択)。
- Qwen3Guard決定的Sampling下での長期的非決定性排除は1実機Trialでの確認に留まる。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手、追加の実機Trialのいずれも行わない。
