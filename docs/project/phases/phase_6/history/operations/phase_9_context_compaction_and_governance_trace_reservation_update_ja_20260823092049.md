# Phase 9 Context Compaction／Recovery／Governance Trace予約更新記録

```yaml
document_id: phase_9_context_compaction_and_governance_trace_reservation_update_20260823092049
status: completed
phase: phase_6
change_type: future_phase_priority_reservation
created_at: 2026-08-23 09:20:49 JST
owner_role: プロジェクト責任者兼設計統括者役
git_mutation: not_performed
implementation_mutation: not_performed
```

## 1. User Decision

ユーザーは、Phase 9のExperiment／Multi-Governance Research Platform構築後、累積Full Closure前の
後半候補として、次の3機能群を実装したい意図を明示した。

1. Context Pressureに応じた自動Context圧縮・Snapshot・復旧。
2. Context UI上の重要Context Recovery／Handoff生成ButtonとManual Compaction Button。
3. Raw Model CandidateとGovernance／Judge／Repair適用後Finalを比較できる右側Observability Panel。

Context Threshold、Compaction形式、IconおよびPanel Designの具体化は、将来の設計統括者に
委ねられた。

## 2. Incorporated Decisions

- 固定95%ではなく、Effective Input BudgetとSafety ReserveからThresholdを設計する。
- 自動／手動Compactionの前に復元Snapshotを必須にする。
- 圧縮前のOriginal Chatを自動削除しない。
- 「復旧」を要約からの生成的復号とせず、Original参照とSelective Rehydrationで構成する。
- HandoffはStructured InstructionからLogへ出力し、Copyと任意の`.md` Downloadを予約する。
- Manual Compactionは正確なWarning Dialog、Cancel、Snapshot IDおよびRollbackを持つ。
- Full Raw Traceは研究価値を優先し、研究者の明示有効化下でRuntimeが実際に観測できた
  Rawを表示・保存可能にする。
- `Protected`は研究者からRawを隠すのではなく、Public／Basic／Git／Externalへの偶発露出防止を意味する。
- Visibility／Persistence／Redactionを分離し、`full_raw／persistent／none`を明示選択可能にする。
- OBSERVEはRawとAction 0、ENFORCEはRaw、実Action／RepairとFinalを比較できる。
- Providerが露出しないInternal Hidden Reasoningを捗造しない。
- 関連機能のDefaultは`off`とする。

## 3. Files

```text
NEW:
  docs/project/shared/history/planned_work/
    phase_9_late_context_compaction_recovery_and_governance_trace_observatory_ja_20260823092049.md

UPDATED:
  docs/public/roadmap_ja.md
  docs/project/phases/phase_6/phase_index_ja.md

HISTORY:
  docs/public/history/roadmap/
  docs/project/phases/phase_6/history/index/
```

## 4. Stable History

RoadmapとPhase 6 Indexには、更新前・更新後の完全Snapshotを保持する。

Before Snapshot作成時、内容HashはStableと完全一致したが、最初に作成した2 FileのFilenameに
実作成時刻より古い`20260823083830`を誤って使用した。History Immutable原則と無許可Cleanup禁止のため
削除またはRenameせず、正しい`20260823092049`のBefore Snapshotを追加した。

```text
Incorrectly timestamped but content-valid snapshots:
  roadmap_phase_6_before_phase_9_context_compaction_and_governance_trace_reservation_ja_20260823083830.md
  phase_index_phase_6_before_phase_9_context_compaction_and_governance_trace_reservation_ja_20260823083830.md

Canonical Before snapshots for this update:
  roadmap_phase_6_before_phase_9_context_compaction_and_governance_trace_reservation_ja_20260823092049.md
  phase_index_phase_6_before_phase_9_context_compaction_and_governance_trace_reservation_ja_20260823092049.md

Canonical After snapshots for this update:
  roadmap_phase_6_after_phase_9_context_compaction_and_governance_trace_reservation_ja_20260823092610.md
  phase_index_phase_6_after_phase_9_context_compaction_and_governance_trace_reservation_ja_20260823092610.md
```

```text
Roadmap Before SHA-512:
  60a9a96ba78fc37a2a46149e73521194e970698d94340ccfae00023d3b30e00d7b4246329326d1664c13dc6c71159be582316e1cb20c9efdca763104dd416a77

Roadmap After SHA-512:
  22c1ef7a69858d754dca0b94c62f606c69bd41bd72269fb6596fecda3ecacecccb56f35407551bf9cdae97f0516dbf4a3e026ff1f45f13bf316d8a1bffea48b8

Phase Index Before SHA-512:
  66f582fcd5bb9cbdf8aea624ba67e915c9a7161d51273837d4360026459e6cf663fd862d5d9eb7578010fbcfe7dcceca726981917d249cb2cd237179b3d36401

Phase Index After SHA-512:
  2df6b187ab2c3820e998774628524f42753d879e3fbb11f2e07186df2aecc7755a683425bd33f9805b25cae1502d48372ae673b75a7604b1902ebbf8db987350
```

誤Timestampは文書内容、Stable Source、Source実装、GitまたはRuntimeを変更していない。

## 5. Scope Boundary

本更新はPlanned WorkとRoadmap予約だけである。次は実行していない。

- Phase 9 Implementation／Design Freeze／Activation。
- Context Compaction／Capture／Raw StorageのSource実装。
- Public／Basic／CloudのRaw Trace有効化。
- User Chat／Runtime DataへのRead／Write。
- Git Mutation。
- Project Root外Action。

Phase 9設計時に、その時点のAs-built、利用可能量、Privacy／RetentionおよびPhase 3〜8 Evidenceを
再評価し、Exact ScopeをFreezeする。
