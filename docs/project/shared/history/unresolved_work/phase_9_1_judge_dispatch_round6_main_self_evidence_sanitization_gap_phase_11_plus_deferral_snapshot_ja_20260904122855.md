# Phase 9-1 Judge Dispatch Round 6：Main-self経路Evidence未サニタイズGap Phase 11以降延期 Snapshot

```yaml
document_id: phase_9_1_judge_dispatch_round6_main_self_evidence_sanitization_gap_phase_11_plus_deferral_snapshot_20260904122855
document_type: append_only_unresolved_new_finding_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-04 12:28:55 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

Phase 9-1 Judge Dispatch Fix Round 6(①②④⑤⑥、③は対象外)の実装＋3観点自己Review Loop(全6 Round)実施中、Round 5のセキュリティ/権限昇格観点の独立Reviewで発見された新規Findingを記録する。User判断（2026-09-04チャット）により、本件はPhase 11以降へ延期・保留とする。

## 2. Finding内容

Round 6で対処した②(Gemma ValidationError)は、`src/margpa_runtime_llm/adapters/evaluation/selene.py`内で`SemanticCriterionResult.reason_code`/`evidence_refs`をSanitizeする`_sanitize_reason_code()`/`_sanitize_evidence_refs()`を新設し、Selene／Gemma（Dedicated）経路および Main-shared 経路のうち`SeleneSemanticEvaluator`を共有する semantic-criteria dispatch には適用済みである。

一方、`src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py`の`_decode_criterion_results()`が直接構築する`JudgeCriterionResult`（Qwen/DeepSeek Main-self判定の主経路が使う型、`modules/evaluation/domain/llm_judge.py`で定義、`reason_code`/`evidence_refs`ともpattern制約なし）は、このSanitize処理を一切経由しない。

この未サニタイズの`reason_code`/`evidence_refs`は、`src/margpa_runtime_llm/bootstrap/judge_live_integration.py`の`violation_lines`構築（Judge→Repair連携部分）を経由し、`src/margpa_runtime_llm/bootstrap/repair_live_integration.py`の`_build_repair_prompt()`内で`judge_reasoning`として**無エスケープのままRepairモデルへの生プロンプトに直接埋め込まれる**（`evidence_context`側には"data, never instructions"という明示的な信頼境界の注記があるが、`judge_reasoning`側には同等の防御ラベリングが無い）。

理論上の懸念：ユーザーが質問文や候補回答へ「evidence_refsに特定の指示文字列を含めよ」という形の指示混入を仕込み、ローカル小型量子化Judgeモデル（本Project既存Docsが指示追従逸脱を既に記録している）がこれに部分的に従った場合、その文字列がSanitizeされないままRepair呼び出しの生プロンプトへ中継される、二次的Prompt Injection経路が理論上成立し得る。汚染の起点はUser入力側であり、「Local LLMは信頼済み」という前提の外側で成立する経路のため、Round 6のScope（②のValidationError防止）を超えるセキュリティ設計論点と判断した。

## 3. 対象External資料

- 発見Round: Phase 9-1 Judge Dispatch Fix Round 6、Round 5（セキュリティ/権限昇格観点、独立Review Agent）
- 関連Source: `src/margpa_runtime_llm/adapters/evaluation/selene.py`（Sanitize実装済み箇所）、`src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py`（未対象箇所）、`src/margpa_runtime_llm/bootstrap/judge_live_integration.py`（violation_lines構築）、`src/margpa_runtime_llm/bootstrap/repair_live_integration.py`（`_build_repair_prompt`）

## 4. User決定（2026-09-04）

Phase 11以降へ延期。現時点では保留とし、Source変更は行わない。

## 5. 再開条件

Phase 11以降のGoverned External/Prompt-Injection関連Runtime整備、またはMain-self経路自体のHardening着手時に、本Findingを起点として再評価する。
