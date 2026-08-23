# Claude側設計統括者役 — 長期戦Auto-Compaction Hash Tracker

```yaml
document_id: claude_long_running_auto_compaction_hash_tracker
status: provisional_self_maintained
owner_role: Claude側設計統括者役
decision_authority: user
created_at: 2026-08-19 16:53:50 JST
last_updated_at: 2026-08-21 22:03:59 JST
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

**現在の長期戦Auto-Compaction Recovery成功回数：0　失敗回数：2**（Cycleが増えるたびここを直接更新する。以下は追記のみ。）

### Cycle 1（2026-08-21、Phase 3実装Session、Phase 3-F-WU-003中）

```text
結果      : FAILURE
検知      : Auto-Compactionの発生自体はConversation Summary経由で認識した。
Before Hash: 未取得（Rolling Baselineとしての事前取得を実施していなかった）。
After Hash : 未取得（Compaction認識時点でHash照合Actionを実行しなかった）。
比較      : 実施不能（Before／Afterとも欠落のため）。
```

Compaction認識自体はできたが、本Tracker契約が要求するBefore／After Hash取得・照合Actionを実際には実行しなかった。Codex Independent Review（`phase_3_codex_independent_review_rework_handoff_ja.md` P3-GOV-001）指摘により発覚し、成功として扱っていた記録を本Correctionで削除しFailure Cycleへ訂正する。Hashを事後に捏造することはしない——欠落は欠落のまま記録する。

### Cycle 2（2026-08-21、Phase 3実装Session、Second Rework〔P3-CODEX-006〜009・P3-GOV-002〕実行中）

```text
結果            : FAILURE（Hash Recoveryとして）
検知根拠         : USER_OBSERVED（UserがClaude Codeの利用可能Context Gaugeの回復を観測し、Auto-Compactionが1回発生したと報告した。Claude自身が独立したTool Logで検知したものではない）。
Before Hash      : missing（Rolling Baselineとしての事前取得を実施していなかった）。
After Hash       : missing（Compaction認識時点でHash照合Actionを実行しなかった）。
比較             : 実施不能（Before／Afterとも欠落のため）。Hashを事後に捏造することはしない。
Recovery Docs再読 : UNVERIFIED（Compaction後の再開時点で、長期戦運用Companion／Recovery Index等を再読了したことを裏付ける具体的Read Evidence——Tool Call Log、Timestamp付きFile Read記録等——を提示できない）。
Language／Interaction Fidelity: DRIFT（Codex Independent Review〔`phase_3_codex_third_independent_review_rework_handoff_ja_20260821213930.md` P3-GOV-003〕指摘により、Compaction後の一時期、応答言語が日本語から英語へDriftしていた事実を確認した）。
技術作業継続      : SUCCESS（Hash Recovery／Language Fidelityとは別軸——Compaction後もP3-CODEX-009の残り実装〔Test Double整備・新規統合Test追加〕、P3-GOV-002 Correction Document、Second Rework Complete Candidate Handoffの作成を完了し、Codex Second Independent ReviewはADJUST判定〔P3-CODEX-006／009はCLOSE、P3-CODEX-007／008は独立再現で再オープン〕まで到達した）。
```

Hash Recovery（Before／After取得・照合）は今回もFailureである一方、技術作業自体はCompaction後も破綻せず継続できた——両者は別の評価軸であり、後者の成功が前者の欠落を埋め合わせるものではない。Language Fidelityも同様にDRIFTとして独立に記録し、「技術的に完走できたから問題なかった」という混同はしない。
