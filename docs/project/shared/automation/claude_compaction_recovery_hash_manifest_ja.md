# Claude側設計統括者役 — Compaction Recovery Hash Manifest

```yaml
document_id: claude_compaction_recovery_hash_manifest
status: provisional_self_maintained
owner_role: Claude側設計統括者役
decision_authority: user
created_at: 2026-08-18 18:41:49 JST
last_updated_at: 2026-08-19 18:29:42 JST
language: ja
provisional: true
```

## 0. 本Fileの目的・位置づけ

本Fileは、[claude_side_design_governor_operating_notes_ja.md](../task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）第3.13節が定める、Compaction Recovery Hash記録の専用Stable Fileである。

運用メモと並ぶ、Claude側設計統括者役が自己判断で直接編集してよい第2のFile（運用メモ第0節・第2.1節参照）。作成の直接の契機：4回目のCompaction Recovery Drillにおいて、Recovery Index自身へその場でHash値を書き込んだ結果、Hash算出後の追記によってRecovery Index自身のHashが事後的に変化するという、恒久的な自己参照問題が発生したこと（詳細は[claude_manual_compaction_hash_verified_recovery_drill_4_ja_20260818173636.md](../history/automation/claude_manual_compaction_hash_verified_recovery_drill_4_ja_20260818173636.md)第3節参照）。ユーザー指摘：「Recovery Index自身のHashをRecovery Index自身へ書くと永久に自己参照問題になる」。

**本File自体は、Hash算出対象File群に含めない**（含めると同じ自己参照問題が再発するため）。

## 1. 運用Flow

```text
最終File群確定 → Hash取得（Before） → 本FileへBefore Hash記録
  → /compact → Hash取得（After） → 本FileへAfter Hash・判定結果を追記
```

- 第2節のCycle記録は**追記のみ**。既存Cycleの内容は書き換え・削除しない。
- 新しいCompaction Cycleごとに、第2節へ新しいSubsectionを追加する。
- 過去のCycle（1〜3回目）は、本File新設前に発生済みのため、Hash記録を持たない。本Fileには4回目以降のみを記録する。

## 2. Cycle別Hash記録

**現在のCompaction Recovery成功回数：7　失敗回数：0**（運用メモ第1節と同値。Cycleが増えるたびここを直接更新する——本File中で唯一、書き換えを行う箇所。以下のCycle記録自体は追記のみで、過去分は書き換えない）。

### Cycle 4（2026-08-18、Manual Compaction、成功）

```text
claude_side_design_governor_operating_notes_ja.md: f56df38…35dd → f56df38…35dd（一致）
claude_side_phase_index_ja_20260818171727.md: 67efecc…1da6 → 67efecc…1da6（一致）
claude_phase_2_e_i_process_breakdown_design_ja_20260818165116.md: 8cc9082…1619 → 8cc9082…1619（一致）
claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md: 87bed92…824c → 2b3add0…5028（不一致）
```

不一致1件について：Recovery Index自身に第6節（Hash記録）を追記したため、自身のBefore/After Hashが不一致になった。これが本File新設の契機。

### Cycle 5（2026-08-18、Manual Compaction、成功）

```text
claude_side_design_governor_operating_notes_ja.md: 108aada…c9e → 108aada…c9e（一致）
claude_side_phase_index_ja_20260818223600.md: 9a75fc4…7bc → 9a75fc4…7bc（一致）
claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md: cf8af31…20b6 → cf8af31…20b6（一致）
claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md: bae6c16…5022 → bae6c16…5022（一致）
```

4件全件一致。Compaction前後でFile内容が完全に保持されたことを確認した。

### Cycle 6（2026-08-19、Manual Compaction、成功）

```text
claude_side_design_governor_operating_notes_ja.md: 702b3e2…3e33 → 702b3e2…3e33（一致）
claude_side_phase_index_ja_20260819113202.md: b978432…f1fe2 → b978432…f1fe2（一致）
claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md: 842bea6…7830d → 842bea6…7830d（一致）
```

3件全件一致。Compaction前後でFile内容が完全に保持されたことを確認した。

### Cycle 7（2026-08-19、Auto Compaction、成功、Before Hash無し）

本Cycleは、運用メモ第3.6節が「例外的・自然発生側」と位置づけるAuto Compactionであり、発生を事前に検知できないため、Compaction直前のBefore Hash取得ができなかった（第3.10節が定める「片側Hashのみ」のケースに該当）。ユーザーからの明示指示「Manualじゃなくて、Autoだから、エビデンスは残すように」を受け、After Hash（Best-effort）と、第3.10節の補助的Evidence（後継File非存在確認・再読込内容と会話Summaryとの一致確認）を組み合わせて記録する。詳細は[claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md](../history/automation/claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md)。

```text
claude_side_design_governor_operating_notes_ja.md: (Before Hash無し) → e77a8c5…e056
claude_side_long_running_automation_companion_ja.md: (Before Hash無し) → d0c7177…101e8
claude_side_phase_index_ja_20260819181056.md: (Before Hash無し) → 5148934…125a5
claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md: (Before Hash無し) → f5efa1f…d689d
```

4件とも、Compaction後の再読込内容が、直前の会話Summaryに記録された内容（Task一覧、TOML設定値、Index本文の要旨）と完全に一致することを確認した。Before Hashが無いため単体では前後一致の直接証明にはならないが、内容一致という補助的Evidenceにより、実質的な情報欠落は無かったと判断する。
