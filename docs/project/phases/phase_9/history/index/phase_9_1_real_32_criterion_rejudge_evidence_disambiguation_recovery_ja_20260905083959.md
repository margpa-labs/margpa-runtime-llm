# Phase 9-1 実Gemma 32 Criterion Rejudge Evidence分離 Recovery

```yaml
document_id: phase_9_1_real_32_criterion_rejudge_evidence_disambiguation_recovery_20260905083959
document_state: complete_recovery
language: ja
created_at: 2026-09-05T08:39:59+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 08:25:39 JST Exact Handoff(実Gemma 32 Criterion Rejudge Evidence分離Rework)への対応として、§2 A/B/C/D全項目に着手した。Test-only Observability実装(A)・Unit境界補正(C)・Claim訂正(D)は完了。追加実機試験(B)は指示どおり正確に1回実行したが、Claude自身のLog取得手順(`tail -100`)のミスにより、新設Observabilityが実際に計算・出力した詳細診断値(execution_state/failure_reason/Criterion内訳/missing・extra ID等)を確認できず、「Decoder FAILED vs COMPLETED+UNKNOWN」の区別は今回も未確定のまま残った。反復禁止の指示に従い3回目の実機試験は実行していない。この制約を含めて正直に報告するExact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- Test-only Observability(`tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py`): 失敗Assertより前に、実`max_new_tokens`、`finish_reason`、Prompt/Completion Token、生成時間、Raw Content長とSHA-512、同一Raw Contentを実`decode_judge_output()`(Fail-closedでない生の版)へ1回通した診断結果(execution_state、JudgeDecodeError.reason、Recommendation、Criterion内訳、missing/extra ID)を記録・出力するBlockを追加。Production Decoder/Contractは無変更。
- Unit境界補正(`tests/unit/bootstrap/test_repair_live_integration.py`): 「2800を1 Token超過」Testを、Candidate 400維持・局所Budget 2799(Production 2800は無変更)の形へ書換。
- Claim訂正(`src/margpa_runtime_llm/bootstrap/repair_live_integration.py`のComment、および同Test Moduleの Docstring): 前回Returnの「Decode-scale limitationと整合的」という断定的表現を、「Decoder FAILEDとCOMPLETED+Criterion UNKNOWNは区別できておらず真因未確定」へ訂正。
- 追加実機試験を正確に1回実行、前回と同一形状の不成立(`outcome=unknown`, `accepted=False`)を確認(再現性は確認)、ただし詳細診断値はLog取得ミスにより未確認。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_real_32_criterion_rejudge_evidence_disambiguation_exact_return_ja_20260905083924.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_real_32_criterion_rejudge_evidence_disambiguation_exact_return_ja_20260905083924.md](../../handoffs/phase_9_claude_real_32_criterion_rejudge_evidence_disambiguation_exact_return_ja_20260905083924.md)

Maximum Claim: `P9_1_REAL_32_CRITERION_REJUDGE_EVIDENCE_REWORK_PARTIAL_SELF_LIMITED_CAPTURE`(Observability実装・Unit補正・Claim訂正は完了、実機Evidenceによる原因分離はClaude自身のLog取得ミスにより今回も未達成)

## 5. Open Items at This Point

- Decoder FAILED vs COMPLETED+Criterion UNKNOWNの区別: 未確定(原因分離用のObservabilityはCode上実装済み、次回実機試験で確実に取得できる状態)。
- 実機32 Criterion Rejudge: 2回連続で同一形状の不成立、再現性は確認、根本原因は未確定。
- Selene: 未解決のまま(今回変更なし)。
- Mypy 43 errors/4 files(既存Baseline、今回Scope外)。
- Frontend再検証未実施(今回変更なし)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手は行わない。
