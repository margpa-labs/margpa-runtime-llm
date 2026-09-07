# Copilot 2026-10-01 Small Work Unit Cross-model Quota／Execution Efficiency Retest Reservation

```yaml
document_id: copilot_2026_10_01_small_work_unit_cross_model_quota_execution_efficiency_retest_reservation_20260902121740
document_type: append_only_planned_work_reservation
document_state: reserved_not_started
language: ja
created_at: 2026-09-02 12:17:40 JST
earliest_execution_date: 2026-10-01
owner: Nazuna Research
provider: GitHub_Copilot
execution_authority: false
network_authority: false
git_authority: false
```

## 1. User Decision

GitHub Copilotは少なくとも次の月間Quota Cycleまで継続利用し、2026-10-01以降にModel別のMatched Retestを行う。

対象Profileは次の4つとする。

- `GPT-5.6 Terra Max / 400K`（現行Reference）。
- `GPT-5.6 Terra High / 400K`。
- `GPT-5.3-Codex Medium`。
- `Sonnet 5`。

過去観測はWork Unit、Context、開始StateおよびFailure内容が一致しておらず、Model間のQuota効率を確定するには不足している。本予約は、工程を小さく揃えた比較によって追加Evidenceを取得するためのものである。

## 2. Experimental Design

各Profileへ、可能な限り同一の開始Commit／Working Tree、同一Exact Handoff、同程度の小Work Unit、同じTest Boundaryおよび同じReturn Schemaを与える。

一つのSessionへ複数Profileを混在させず、ProfileごとにFresh Sessionを使用する。Stale Task、Provider Memoryまたは前SessionのAuthorityを引き継がせない。

Work Unitは、20分前後でFocused TestとRecoveryまで到達できる規模を上限目安とする。月間Quota全量を一つのLong-runへ投入しない。

## 3. Measurement Axes

最低限、次をProfileごとに記録する。

| Axis | Record |
|---|---|
| Resource | 開始／終了Quota、AI Credits、経過時間、Compaction回数 |
| Progress | 完了WU、Accepted Diff、Focused／Canonical Test結果 |
| Quality | Controller Finding、Regression、Rework回数、Claim精度 |
| Autonomy | Unauthorized Action、False Stop、False Resume、User Interrupt |
| Recovery | Hard-stop Recovery、Partial State継承、Compaction後復旧 |
| Platform | Log Copy可否、Evidence回収Cost、操作上の制約 |
| Efficiency | Accepted WU／Quota、Rework-free Progress／Quota、Closure寄与／Quota |

単純な`Quota % / minute`だけで優劣を決めない。品質低下によりReworkとHuman Attentionが増えた場合、そのCostを総効率へ含める。

## 4. Claim Boundary

現在までの少数観測では、Terra High、Terra Max、GPT-5.3-Codex MediumのQuota減少速度に明確な差を確認できていない。一方、MediumではStale Task再開と追加介入が観測された。

したがって現時点では、低設定がQuota節約にならない状態が続くなら`GPT-5.6 Terra Max / 400K`を選ぶ方が相対的に妥当である可能性を維持する。ただし、これはMatched Retest前の条件付き仮説であり、Sonnet 5を含むModel順位、価格性能または一般的優劣を確定しない。

## 5. Execution Gate

本書は予約であり実行Authorityではない。2026-10-01以降、各Profileごとに個別Exact Handoff、Quota上限、対象Work UnitおよびStop BoundaryをUserが明示して開始する。

