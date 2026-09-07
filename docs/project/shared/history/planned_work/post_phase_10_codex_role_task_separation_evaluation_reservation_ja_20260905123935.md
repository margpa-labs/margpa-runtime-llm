# Phase 10後 — Codex最高責任者／設計／実装Controller Role・Task分離検討予約

```yaml
document_id: post_phase_10_codex_role_task_separation_evaluation_reservation_20260905123935
document_type: planned_work_reservation
document_state: reserved_under_consideration_not_decided
language: ja
recorded_at: 2026-09-05 12:39:35 JST
decision_authority: user
authority_owner: Nazuna Research
earliest_reassessment: after_phase_10_completion
implementation_authorized_now: false
task_creation_authorized_now: false
automation_creation_authorized_now: false
git_action: none
append_only: true
```

## 1. 予約目的

Phase 10完了後、Codexの最高責任者役、設計統括者役、実装Controller役、独立Acceptance役、Closure／Docs統合役を、同一TaskのRole切替で扱い続けるか、複数Taskへ分離するかを再評価する。

発端、現状評価およびPhase 10までの暫定運用は[Automation Role評価](../automation/codex_controller_combined_authority_and_design_role_context_mixing_assessment_ja_20260905123935.md)に記録した。本予約は将来の検討枠であり、Role分離の採用決定ではない。

## 2. 検討対象

候補Roleは次である。

| Role候補 | 主責務 | 禁止境界候補 |
|---|---|---|
| 最高責任者／理念管理 | 理念、不変条件、Phase目的、重要変更承認 | Source実装、詳細設計の自己承認 |
| 設計統括 | 承認済み理念からArchitecture／Acceptanceを設計 | 理念・Scope・順序の無断変更 |
| 実装Controller | Handoff、Return Review、局所Rework | 全体設計の再解釈・拡張 |
| 独立Acceptance | User目的、理念、実画面、Failure境界の独立照合 | 実装修正との同一Turn混在 |
| Closure／Docs統合 | 成立済み事実の統合、公開境界整理 | Docs都合による要件変更 |

この5分割をそのまま採用するとは限らない。Quota効率が悪ければ、最高責任者と独立AcceptanceだけをFresh Taskへ分け、設計／実装Controller／Closureを統合する等の縮小案も比較する。

## 3. 評価観点

### 品質

- Platform最上位理念が局所設計により上書きされにくくなるか。
- User承認なしのScope／順序／Architecture変更を防げるか。
- 実装担当とAcceptance担当の前提共振を減らせるか。
- Context圧縮後もRole Authorityと禁止境界を復元できるか。

### Cost

- TaskごとのBootstrap、必読Docs、Handoff、同期、再説明に必要なQuota。
- UserがTask間の伝言役になる回数。
- Fresh Taskを増やすことで失われるCurrent Working Context。
- Review精度向上が、追加Quotaと時間に見合うか。

### Delivery

- MVP完成と就職用Portfolioの時期を不必要に遅らせないか。
- Role分離導入自体が新しい大規模Process Reworkにならないか。
- Phase 10統合Docsを短い共通前提として再利用できるか。

## 4. 最小案

全面分離の前に、次の省Quota案を優先候補とする。

1. Phase 10統合後の短いPlatform不変条件だけを全Task共通入力にする。
2. 通常実装は現行統合Controllerで続け、重大Architecture変更時だけ理念管理Taskへ戻す。
3. Phase／大規模PackageのClosure時だけFresh Independent Acceptanceを1回使う。
4. Routine Reworkごとに新Taskを作らない。
5. Role間Handoffは差分中心とし、全Docs再読を要求しない。

## 5. 再評価時の選択肢

```text
A. 現行の同一Task兼務を継続
B. 最高責任者／理念管理だけ分離
C. 最高責任者＋独立Acceptanceを分離
D. 設計／実装Controllerも含めて段階分離
E. 全5 Roleを分離
```

採用判断では、理念保全性だけでなく、1 Phaseまたは1 Work PackageあたりのQuota、User介入回数、再説明時間、Finding検出率、Rollback／Rework削減量を比較する。

## 6. 着手条件と非Authority

- 最短でもPhase 10完了後にNazuna Researchが再検討を指示する。
- Phase 10前に自動でTask、Automation、Role文書または新運用を作らない。
- 本予約を根拠に現行Phase 9／10の担当、順序、停止線を変更しない。
- Quota回復だけを自動着手条件にしない。
- 分離案を採用する場合も、試行範囲、期間、最大Task数、Quota停止線を先にUserが承認する。

## 7. Current Disposition

```text
Decision     : NOT DECIDED
Reservation  : RECORDED
Start        : NOT AUTHORIZED
Current Plan : COMBINED ROLE THROUGH AT LEAST PHASE 10
```

