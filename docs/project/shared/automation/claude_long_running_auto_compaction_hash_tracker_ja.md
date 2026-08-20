# Claude側設計統括者役 — 長期戦Auto-Compaction Hash Tracker

```yaml
document_id: claude_long_running_auto_compaction_hash_tracker
status: provisional_self_maintained
owner_role: Claude側設計統括者役
decision_authority: user
created_at: 2026-08-19 16:53:50 JST
last_updated_at: 2026-08-19 17:08:09 JST
language: ja
provisional: true
```

## 0. 位置づけ

Hash Manifest（Manual Compaction専用）とは別の、Auto-Compaction用Tracker。設計根拠：[長期戦運用Companion第3.4節](../task_roles/claude_side_long_running_automation_companion_ja.md)、[Evidence](../history/automation/claude_long_running_automation_hash_tracker_and_timing_evidence_refinement_ja_20260819165350.md)。**本File自体はHash算出対象に含めない**（自己参照回避）。

## 1. 運用Flow

```text
Step境界でIndex更新 → 最新2FileのHashをBefore Hashとして記録（Rolling）
  → Compaction認識時のみ：After Hash取得・直近Beforeと比較・記録
  → 未認識ならそのCycleは記録せず終わる（Failure扱いしない）
```

記録はCycle成立分のみ（Rolling Baselineは次の更新で上書き）。粒度はHash Manifestと同一。

## 2. Cycle別Hash記録

**現在の長期戦Auto-Compaction Recovery成功回数：0　失敗回数：0**（Cycleが増えるたびここを直接更新する。以下は追記のみ。）

（Cycle記録はまだ無い。）
