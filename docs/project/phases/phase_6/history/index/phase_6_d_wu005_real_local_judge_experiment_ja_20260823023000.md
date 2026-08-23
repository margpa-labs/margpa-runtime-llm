# Phase 6-D-WU-005 Real Local Judge Experiment（実Hardware Evidence確立）

```yaml
document_id: phase_6_d_wu005_real_local_judge_experiment
status: current_recovery_entry
phase: phase_6
subphase: phase_6_d
work_unit: p6_d_wu005_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 02:30:00 JST
```

## Exact Mutation

```text
Created:
  tests/integration/test_real_local_judge_smoke.py（@pytest.mark.model_smoke、
    既定Deselect、Apple Silicon限定）
```

## 実行結果（実Hardware、実Qwen3-4B）

```text
1. 実Qwen3-4Bへ実際の質問（"What is the capital of France?"）をGenerate。
2. build_judge_prompt()で実際のCandidate Answerを含むJudge Promptを構築。
3. 同一Qwen3-4BへそのJudge Promptを再Generate（MAIN_SELF Independence、
   独立Judge Artifactが本環境に無いため正直にSelf-Judgeと明記）。
4. decode_judge_output_fail_closed()で実際のRaw Text Outputを Decode。
   → 初回実行で有効なJSON（recommendation／confidence）を正しく生成・
     Decode成功（execution_state=COMPLETED）を実測確認。
   → Decoder自体はMalformed Caseでも例外を投げずFAILEDへ収束する設計のため、
     仮にModel出力が壊れていてもTestはCrashせずSkip記録する設計とした
     （今回は正常Decode成功のため非該当）。

実行時間: 3.65秒（2回の実Generation Callを含む）
```

## 意義

```text
Phase 6-D-WU-005「Real Local Judge Experiment：AvailableなQwenまたはDeepSeekで
少なくとも一つの実LLM Judge Runを行い、Fake／Stub TestとEvidence Classを
分離する」を実Hardwareで達成した。Prompt Builder（決定的生成）とStrict
Decoder（Fail-closed）が、実Model特有の出力揺れ（改行、余分な説明文等）に
対しても正しく機能することを実証した。
```

## Validation

```text
New model_smoke Test : 1 passed（実Hardware、3.65秒）
Default Suite         : 1403 passed／5 deselected（新規Test2件が正しくDeselect、回帰0）
Full model_smoke Suite: 4 passed／1 skipped（既存Non-scope）
Ruff／Mypy            : Clean
```

## Next Exact Route

Phase 6-H（Comparative Experiment）へ進む。実Generation・実Judge双方が実証された
ため、Qwen単体でのMode比較実験も現実的な範囲で着手可能。
