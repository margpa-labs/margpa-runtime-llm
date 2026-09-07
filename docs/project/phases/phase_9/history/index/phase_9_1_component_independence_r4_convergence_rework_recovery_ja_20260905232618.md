# Phase 9-1 Component完全疎結合 R4収束Rework Recovery

```yaml
document_id: phase_9_1_component_independence_r4_convergence_rework_recovery_20260905232618
document_state: complete_recovery
language: ja
created_at: 2026-09-05T23:26:18+09:00
phase: phase_9
program: phase_9_1
```

## 1. Current Point

Codex Controllerの2026-09-05 19:50:51 JST Controller Review(R3 Returnに対する`CHANGES REQUIRED`、IR-R3-01〜05)を受け、同時刻発行のR4収束Rework Exact Handoffに従い、R4-WU-01からR4-WU-06までを順に実施した。R4-WU-01(Semantic Turn Snapshot/Freeze Failure/EvidenceのRequest-local化)、R4-WU-02(Judge Identity 3経路Matrixの完結)、R4-WU-03(Cancellation Terminal Arbitrationの限定)の3件は解決を確認した。R4-WU-04(Gemma専用Compact Criterion Schema)は、共有Decoderの既存の省略可能性を利用して`reason_code`/`evidence_refs`をSchemaから完全に除去し、実機2 Trial(Deviation含む32 Criterion、完全決定的)でR3から持ち越されていたMalformed JSON Defectの根絶を確認した。R4-WU-05は、Fixture水準(`context_size`を実配置と同じ`8192`へ修正)・実機水準(1 Trial、Handoff上限どおり)の両方でGolden Pathが完全に成立することを確認した——R3-WU-05が実機水準で正直にFailしたまま停止していた残存Findingは本Roundで解消された。Exact Returnを新規Fileとして提出済み、Codex Controller Independent Review待ちで停止している。

## 2. What Changed

- `semantic_runtime.py`(application): `SemanticRuntimeCoordinator`の単一`_current`Slotを`request_id`単位のRequest-local Ledger(`_turns: OrderedDict`)へ置換。`begin()`はLock下で既存Entryの有無を確認し、既存の場合は新Generationを作らず返す(2 Thread同時Begin対応)。UI向け"Latest Current"Pointer(`_latest_request_id`)を分離。`_MAX_TRACKED_TURNS=128`のFIFO Evictionを追加。
- `runtime_governance.py`: `JudgeSemanticTurnProvider`の単一Freeze-failure Slotを`request_id`単位の`OrderedDict`(`_failed_request_ids`、`_MAX_TRACKED_FREEZE_FAILURES=128`)へ置換。
- `judge_live_integration.py`: ENFORCE Wait Loopが再利用してよいWorker Terminalを`execution_state == "cancelled"`のみへ限定(旧`in ("cancelled", "failed")`から変更)——通常のFailureがCancellationを上書きしなくなった。
- `selene.py`: `GemmaPromptAdapter._criterion_result_example()`を`reason_code`/`evidence_refs`を含む5-Field例からCompact 3-Field例(`criterion_id`/`disposition`/`confidence`)へ変更。
- `config/judge_templates/gemma_4_e2b/*`: Gemma専用Templateへ「Do not include reason_code or evidence_refs」を明示する新規Rule 6を追加、Manifest Digestを再計算。

## 3. Files Created This Round

- `docs/project/phases/phase_9/handoffs/phase_9_claude_component_independence_r4_convergence_rework_exact_return_ja_20260905232353.md`(本Roundの正本Return)
- 本File(Recovery Index)

## 4. Exact Return Handoff

[phase_9_claude_component_independence_r4_convergence_rework_exact_return_ja_20260905232353.md](../../handoffs/phase_9_claude_component_independence_r4_convergence_rework_exact_return_ja_20260905232353.md)

Maximum Claim: `P9_1_R4_WU01_WU02_WU03_WU04_WU05_RESOLVED_GEMMA_DEVIATION_MALFORMED_DEFECT_ELIMINATED_REAL_GOLDEN_PATH_PASSED`

## 5. Open Items at This Point

- R4-WU-05実機Golden Path Trialは1回のみ(Handoffの上限どおり)——再現性(同一条件での複数回一致)は未検証。R4-WU-04自身の2 Trialが完全に決定的だったことから、同一結果になる可能性が高いと推定されるのみ。
- R4-WU-04のDeviation Trialで`result_criteria_evaluated=31`(全32 CriterionはDecode/報告済みだが、この集計値のみ31)——本RoundのScope外として深掘りしていない。
- R2で報告済みのGuard(R2-WU-05)は本Roundで再確認していない(Scope外)。

## 6. Next Step

Codex Controller Independent Reviewを待つ。Phase Closure、次Phase着手、追加の実機Trial、Decoder緩和/JSON補修/Retry追加のいずれも行わない。
