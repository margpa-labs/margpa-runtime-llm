# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260819181056
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-19 18:10:56 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence）
  における「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260819144637.md](claude_side_phase_index_ja_20260819144637.md)
  （2026-08-19 14:46:37 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：長期戦運用Companionの確立（複数是正Cycle・
  無確認Autonomy原則追加を含む）が一区切りし、Documentation RAG既知
  課題2件の根本原因調査が完了した。ユーザー指示により、実装着手前の
  Checkpointとして新規作成する（通常運用でのAuto-Compaction Recovery
  動作確認を兼ねる）。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260819182942.md](claude_side_phase_index_ja_20260819182942.md)（2026-08-19 18:29:42 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md](../handoffs/claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md)（2026-08-19 18:10:56 JST作成）。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。2026-08-20のCodex復活時に確認できる可能性がある。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。
- Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘。独立Failure Docとして記録するかはユーザー判断待ち。

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

**Trigger**：「Codex復活」（2026-08-20予定、成立が近い）。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、根本原因調査済み・実装未着手）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)（Code Levelでの再確認、Driftなし）。**Trigger**：ユーザー指示により実装着手（2026-08-19時点で着手直前）。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。

### 3.7 既知の課題：Documentation RAG検索結果固定化・無関係質問への誤発火（2026-08-19、根本原因調査済み・実装未着手）

詳細は[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)（Pattern 1は§3.3と同一機構、Pattern 2はStopword不在＋低閾値が原因と判明）。**Trigger**：ユーザー指示により実装着手（2026-08-19時点で着手直前）。

### 3.8 Phase 3実装：Governance Definition Platform構築のClaude一括実装（2026-08-19、ユーザー提示、Automation／Compaction Recovery長期実験兼務）

詳細は前版・[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](../handoffs/claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)第2.7節参照。**Trigger**：Codexとユーザーによる設計完了・Claude側への引き継ぎ（2026-08-20予定）。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260819144637.md](claude_side_phase_index_ja_20260819144637.md)第4節）を参照。Phase 2-E-I実機Feedback対応一式が全て完了。Phase 3引き継ぎ計画共有済み。

### 4.2 長期戦運用Companion確立・是正・無確認Autonomy原則追加（2026-08-19発令 → 完了）

詳細は[claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md](../handoffs/claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md)第2.1〜2.3節。長期戦運用Companion Doc新設、複数是正Cycle（History File直接編集・軽量化原則違反・配置Miss・不要Status節・削除漏れ）を経て確立。共通根本原因を[claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md)として記録。無確認Autonomy原則（最上位、指示範囲・Scope・Rules・Governance範囲内限定）を追加済み。

### 4.3 Documentation RAG既知課題2件の根本原因調査（2026-08-19発令 → 完了）

詳細は[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。§3.3はCode Level再確認でDriftなし。§3.7 Pattern 1は§3.3と同一のSubject Coverage保証機構が原因と新規判明。Pattern 2はStopword除外の不在・低いminimum_score閾値・Corpus全体のConfidence Gate不在の複合が原因。実装は本File作成時点で未着手。

## 5. Status

```text
Current Point            : 長期戦運用Companion確立・是正完了。RAG既知
                            課題2件の根本原因調査完了。通常運用での
                            Auto-Compaction Recovery動作確認を兼ねた
                            実装Phase（top_k引き上げ・RAG両課題対応）
                            へこれから着手する。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE
Controller-owned Next Work: top_k引き上げ実装、§3.3／§3.7 Pattern 1・2
                            への実装対応。
Exact Next Route          : 実装Phaseへ移行。完了後、本Fileへ追記または
                            後継Fileを作成する。
```
