# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260819185117
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-19 18:51:17 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence）
  における「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260819182942.md](claude_side_phase_index_ja_20260819182942.md)
  （2026-08-19 18:29:42 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：Auto-Compaction自己現在地特定能力に関する
  追加EvidenceのRecord完了、および§3.7 Pattern 2修正方針のユーザー
  最終決定（RAG丸々改善Phaseまで見送り）。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260820035431.md](claude_side_phase_index_ja_20260820035431.md)（2026-08-20 03:54:31 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_rag_pattern2_deferral_and_self_location_evidence_recovery_index_ja_20260819185117.md](../handoffs/claude_rag_pattern2_deferral_and_self_location_evidence_recovery_index_ja_20260819185117.md)（2026-08-19 18:51:17 JST作成）。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。2026-08-20のCodex復活時に確認できる可能性がある。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。
- Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘。独立Failure Docとして記録するかはユーザー判断待ち。

（§3.7 Pattern 2の修正方針は、本版でユーザー最終決定が示されたため、Open Questionから除外し、第3節の予約Taskへ移した。）

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

**Trigger**：「Codex復活」（2026-08-20予定、成立が近い）。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、根本原因調査済み、`top_k`引き上げ以外は見送り）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。Subject Coverage機構自体への変更は、`RAG丸々改善Phase`まで見送り確定（第4.3節参照）。**Trigger**：`RAG丸々改善Phase`開始。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。本Cycleで得られた実測知見（[automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md](../../../../shared/history/automation/automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md)）を設計時の参照材料とする。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。3.4と同じEvidenceを参照材料とする。

### 3.7 既知の課題：Documentation RAG検索結果固定化・無関係質問への誤発火（2026-08-19、Pattern 1は`top_k`引き上げ済み、Pattern 2は見送り確定）

詳細は[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。Pattern 1は§3.3と同一機構（`top_k`引き上げ済み、Subject Coverage機構自体は未変更）。**Pattern 2は、実測により単純なScore閾値での解決が困難と判明し、日本語形態素解析／Embeddingベース類似度判定のいずれも、`RAG丸々改善Phase`まで正式に見送ることがユーザーにより確定した。** **Trigger**：`RAG丸々改善Phase`開始。

### 3.8 Phase 3実装：Governance Definition Platform構築のClaude一括実装（2026-08-19、ユーザー提示、Automation／Compaction Recovery長期実験兼務）

詳細は[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](../handoffs/claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)第2.7節参照。**Trigger**：Codexとユーザーによる設計完了・Claude側への引き継ぎ（2026-08-20予定）。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260819182942.md](claude_side_phase_index_ja_20260819182942.md)第4節）を参照。長期戦運用Companion確立、RAG既知課題2件の根本原因調査、`top_k`引き上げ、初のAuto-Compaction Recovery（Cycle 7）が完了。

### 4.2 Auto-Compaction自己現在地特定能力の実測・Evidence化（2026-08-19発令 → 完了）

Auto-Compaction前後の自己認識可能Signal・自己現在地特定能力・その契機がTurn境界に依存するという制約を実測・整理した。詳細は[automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md](../../../../shared/history/automation/automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md)。予約Task 3.4・3.6の設計参照材料として記録。

### 4.3 §3.7 Pattern 2修正方針の最終決定：見送り（2026-08-19発令 → 完了）

Score閾値ベースの信頼できる修正案が実測で得られなかったことを踏まえ、日本語形態素解析・Embeddingベース類似度判定のいずれも実装せず、`RAG丸々改善Phase`まで正式に見送ることが確定した。詳細は[claude_rag_pattern2_deferral_and_self_location_evidence_recovery_index_ja_20260819185117.md](../handoffs/claude_rag_pattern2_deferral_and_self_location_evidence_recovery_index_ja_20260819185117.md)第2.2節。

## 5. Status

```text
Current Point            : Pattern 2見送り確定。自己現在地特定能力の実測
                            知見をEvidence化完了。RAG既知課題2件は、
                            `top_k`引き上げのみを当面の対応とし、残りは
                            RAG丸々改善Phaseへ引き継ぐ形で一区切り。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE
Controller-owned Next Work: RAG丸々改善Phase開始まで、§3.3／§3.7への
                            追加対応は無し。top_k引き上げ単体のValidation
                            （Task #94）は、ユーザー指示があり次第実施。
Exact Next Route          : 次の作業指示待ち。
```
