# Phase 9-1 Gemma Constrained Decoding Final Contract Micro Rework Recovery

```yaml
document_id: phase_9_1_gemma_constrained_decoding_final_contract_micro_rework_recovery_20260906131451
document_state: complete_recovery
language: ja
created_at: 2026-09-06T13:14:51+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controller Independent Review(`phase_9_controller_gemma_constrained_decoding_final_contract_micro_rework_exact_handoff_ja_20260906124425.md`)が指摘した3件の極小Finding——(IR-FC-01)Gemma RejudgeがSampling契約を初回Judgeと共有していない、(IR-FC-02)StructuredOutputConstraintのSchema/Digestが構築後に不一致になり得る、(IR-FC-03)Model Call 0時にEvidence `call_count`が`1`へ捏造される——をすべて修正した。修正はGemma固有経路のみに閉じており、Main通常回答・Repair Candidate・Qwen3Guard・RAG/Web/Dev Agentへの影響はゼロであることを機械的に再確認した。実機Golden Path 1回(Handoff上限どおり)を実行し、成立を確認した。前Returnの2箇所(Memory定量成立の主張、`criteria_evaluated`のAnomaly表現)を訂正した。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `generation.py`: `StructuredOutputConstraint.from_schema()`が非JSON直列化可能な入力でTyped Validation Failureへ収束するよう修正。
- `chat_template.py`: `_build_grammar()`がGrammar構築直前にSchema Digestを再照合し、不一致ならTyped Fail-closed。
- `selene.py`: `SeleneSemanticEvaluator`へ読み取り専用`sampling_overrides`Property追加。
- `repair_live_integration.py`: `attempt_live_repair()`へ`rejudge_sampling_overrides`引数追加、Rejudge Parameters構築を修正(`max_new_tokens`は常にRejudge Plan値)。
- `judge_live_integration.py`: `_run_selene_dispatch()`が`evaluator.sampling_overrides`をRejudgeへ伝播、`call_count`の`or 1`Fallbackを削除。
- `web_application.py`: `_repair_executor`ローカルClosureへ`rejudge_sampling_overrides`引数を透過。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_ja_20260906131256.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_ja_20260906131256.md](../../handoffs/phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_ja_20260906131256.md)

Maximum Claim: `P9_1_GEMMA_CONSTRAINED_DECODING_FINAL_CONTRACT_MICRO_REWORK_READY_FOR_USER_RECHECK`

## 5. Verification Summary

- 新規Focused Test 6件All Pass。Sabotage-regression3件(IR-FC-01/02/03それぞれ)で検出力を確認。
- 非Model Full Suite: `2402 passed, 37 deselected`。Ruff Clean。Canonical Mypy `43 errors/4 files`(既存Baseline一致、新規Error 0)。
- 実機Golden Path 1回: `1 passed in 158.29s`。Count保存則(`31+1+0=32`、`32+77=109`)成立。Process/Port確認Clean(前後とも残存なし)。

## 6. Open Items at This Point

- Rejudge Samplingは実機での独立計装がなく、Fixture Golden Path(実配線・Fake Model Port)による機械的証明と実機Trial成功の状況証拠にとどまる。
- `criteria_evaluated`のUnknown 1件判定理由は今Round未調査(Handoffの明示指示どおり)。
- Memory(Process RSS)定量計測は今Round未実施(Handoffの明示指示どおり)。
- 他5箇所の既存実機Test(Trial A/B以外)は本Round未更新・未実行。
- R2-WU-05のGuardは本Roundでも再確認していない。

## 7. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-1 Closure、User Acceptance、次Phase着手、追加の実機Trial、Selene実機実行、Guard修正・実機再試行、JSON Retry/Seed変更/Decoder緩和/JSON補修/部分採用、Main Context/Repair Budget/Criterion上限の変更のいずれも行わない。
