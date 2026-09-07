# Phase 9-1 IR-R4-02 — 「26件成立」Claimの訂正(短文) 未解決Snapshot

```yaml
document_id: phase_9_1_26_criterion_plan_acceptance_vs_execution_claim_correction_snapshot_20260905005446
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-05 00:54:46 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

Codex Controller独立Review(`../../../phases/phase_9/history/operations/phase_9_1_controller_ir_r3_return_review_and_delta_rework_ja_20260905003507.md`)IR-R4-02の指摘: 前回Return(`../../../phases/phase_9/handoffs/phase_9_claude_p9_1_controller_ir_r3_delta_rework_exact_return_ja_20260905002304.md`)の「26件成立を実証」という記述は、`_plan_rejudge()`直接呼出しで`max_new_tokens`のみ確認するTestに基づいており、実生成・Decode・改善採用・保存は一切実行していない。したがって成立しているのは**26件のToken Plan受理**のみであり、**26件のRepair→Rejudge実行成立**ではない。本Snapshotはこの区別を明示する短文訂正である。

## 2. 測定・Plan・実行の分離(訂正後の正確な記述)

```text
[測定] 実Qwen Tokenizerで、合成JSON(実ARGD/DAGD ID使用)を計数した結果:
       32件で55.3〜59.4 Token/Criterion。実生成のcompletion usageではない。
       Gemma／Seleneの実出力最悪値でもない。

[Plan] 上記測定に基づき`_REJUDGE_TOKENS_PER_CRITERION=75`を設定し、
       `_plan_rejudge()`が特定のCriterion数・候補Token消費量の組合せで
       Planを受理するかどうかをTestで確認した:
       - 候補消費5 Token(最小Fixture)の場合: 26件まで受理、27件で拒否。
       - 候補消費400 Token(Repair候補の実際の上限)の場合: 21件まで
         受理、22件で拒否。
       - 32件(Runtime既定選択上限)は候補消費0でも拒否(75×32=2400>2000)。

[実行] 実生成・Decode・改善回答採用・保存を伴う成立は、本Task全体を
       通じて1 Criterion(実機)および少数Criterion(Fixture、Judge/Main
       起点保存Test)でのみ確認済み。21〜26件規模での実行成立は
       未検証・未実証である。
```

## 3. 訂正箇所

- `tests/unit/bootstrap/test_repair_live_integration.py`: 該当Test関数名・Docstringを「Plan受理」の言明へ訂正(`test_a_26_criterion_token_plan_is_accepted_within_the_existing_budget_after_a_minimal_candidate_cost`等への改名)。候補が上限400 Tokenを使う場合の21件境界も新規Testとして追加。
- 前回Return(00:23)の「26件成立を実証」という記述は、本Snapshotにより「26件Token Plan受理を実証(実行成立ではない)」と読み替える。前回Return自体は上書きしない。

## 4. 75 Token/Criterionという見積りの位置づけ(再確認)

75は実測(32件合成JSON、Qwen Tokenizer)に基づく暫定見積りであり、次のいずれも証明していない:
- 実際の全出力に必須の情報量であること。
- Gemma／Seleneを含む全Providerの最悪値であること。
- 実生成時のToken消費が常にこの見積り以下に収まること。

3000 Token案(候補400＋暫定Rejudge2400を収める算式)も、Context／全体時間／実Model成立を保証するものではなく、実装許可への読み替えはしない(前回Snapshotの記載を維持)。Batching機構の導入だけでは総Token予算2000は自動的に増えず、Call上限との整合も別途必要であり、単純な代替解決として扱わない。

## 5. Status

```text
Current Point            : 「26件成立」Claimを「26件Token Plan受理」へ
                            訂正。21件(候補400 Token消費時)の境界も追加
                            確認。実行成立(生成・Decode・採用・保存)は
                            26件は言うまでもなく21件規模でも未実証の
                            まま。
Files Created／Modified  : 本File(新規作成)、
                            tests/unit/bootstrap/test_repair_live_integration.py
                            (Test関数名・Docstring訂正、21件境界Test追加)。
Validation                : Unit Test 38件PASS(21件境界Test含む)。
Open Current Blocker     : 32件Criterion Repair→Rejudgeの実行成立は
                            未達のまま(Plan受理も32件では不成立)。
Exact Next Route          : Codex Controller Independent Reviewを待つ。
```
