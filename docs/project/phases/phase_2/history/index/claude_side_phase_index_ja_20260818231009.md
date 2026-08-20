# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260818231009
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-18 23:10:09 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260818223600.md](claude_side_phase_index_ja_20260818223600.md)
  （2026-08-18 22:36:00 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：5回目のManual Compaction Recovery完了後、
  ユーザー指示「今回の分の自動化／圧縮関連を、docsに書いて」
  「LLM自身への自動圧縮・自動復旧機能構想を、予約枠のとこにdocsとして
  書いておいて」に基づき、新規Evidence Doc・新規将来Scope提案Docを
  作成した結果を反映する。

  **前版からの構造変更**：なし。第2節「現在進行中のSub-phase」
  （2-E-I I-6）は前版のまま継続。第4節に新規予約Task 1件、第5節に
  新規完了項目1件を追加した。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260819002344.md](claude_side_phase_index_ja_20260819002344.md)（2026-08-19 00:23:44 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md](../handoffs/claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md)（2026-08-18 22:36:00 JST作成。本File作成時点で変更なし——実装作業の進展はなく、Docs記録のみの更新のため、新規Recovery Indexは作成していない）。

## 2. 現在進行中のSub-phase

### 2.1 Phase 2-E-I I-6：Context Usage Gauge Follow-up

**状態：要件確定済み。実装は未着手。**

設計・要件Doc：[claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md](../architecture/claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md)。

2-E-I（I-1〜I-5）完了後の実Browser確認で見つかった5件の指摘のうち、#2（Panel閉時のHover Message欠落）・#3（Panel外Clickで閉じない）・#5（「再開」Option表示不具合）の修正、および新規Toggle「コンテキスト表示」ON/OFF（既定OFF）の追加が確定Scope。#1（会話切替でGauge初期化）は保留、#4（Toggle OFF状態での謎の出力混入）は原因未特定のためScope外（別途調査）。

**次にやること**：ユーザーからの実装開始指示を待って、上記設計Docの第2節から着手する。

## 3. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I I-6 #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。原因調査自体もまだTrigger・担当が確定していない。
- **[新規]** Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘（「3Docs明示的再読込」と宣言しつつ、実際は1Fileのみ本Turn内Read Tool・残り2FileはSystem再挿入内容を利用）。File整合性自体はHash一致で担保済みだが、独立Failure Docとして記録するかはユーザー判断待ち。詳細は[claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md](../../../../shared/history/automation/claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md)第3.4節・第4節参照。

## 4. 予約Task（未着手、Trigger待ち）

### 4.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

構想は[future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md](../../../../shared/history/planned_work/future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)。**Trigger**：「Codex復活」。

### 4.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_context_observatory_ja_20260817234734.md](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)。第3.1節の縮小版は2-E-Iとして完了済み。残る部分は引き続きTrigger待ち。**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 4.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、修正未着手）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。**Trigger**：「RAG丸々改善Phase」。

### 4.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)。第2.1節は2-E-Iとして完了済み。第2.2節はAgent Runtime基盤が前提でTrigger待ち。**関連**：第4.6節（自動復旧側を補完する続編提案）。

### 4.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

構想は[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)。**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 4.6 [新規] LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md](../../../../shared/history/planned_work/future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md)。MARGPA Runtime自身が生成するLLMに、Claude Code等のAgent Harnessが既に備える「自動圧縮→自動復旧」Cycleに相当する機能を持たせる構想。第4.4節の続編（自動復旧側を補完）。**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。

## 5. 完了済み予約Task（記録として残す）

### 5.1〜5.8（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260818181920.md](claude_side_phase_index_ja_20260818181920.md)第4.1〜4.8節）を参照。「index作って」Trigger実行、Recovery Index前倒し再作成（2回）、運用メモ全面再編成、将来Scope提案2件のFolder整理、本File旧版の配置訂正、2-E-I設計書・工程分解の作成。

### 5.9 Phase 2-E-I：I-1〜I-5完了（2026-08-18発令 → 2026-08-18完了）

詳細は[claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md](../../../../shared/history/automation/claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md)。実装過程でllama-cpp-python Streaming Usage欠落を発見・修正。実Browser確認まで完了。

### 5.10 Compaction Recovery Hash記録手法の改善（2026-08-18発令 → 2026-08-18完了）

4回目のDrillで発生したHash自己参照問題を受け、運用メモ第3.13節を新設し、専用Stable File [claude_compaction_recovery_hash_manifest_ja.md](../../../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)（Hash Manifest）を新設した。今後のCompaction Recoveryでは、Before／After HashをこのFileへ記録する。

### 5.11 Failure記録2件の追加（2026-08-18発令 → 2026-08-18完了）

- [claude_output_anomaly_language_consistency_ja_20260818192108.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_language_consistency_ja_20260818192108.md)（言語一貫性逸脱、3回目）
- [claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md)（指示語の参照範囲取り違え）

### 5.12 実Browser確認によるI-6要件確定（2026-08-18発令 → 2026-08-18完了）

**完了**：[claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md](../architecture/claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md)。実装は第2節参照、未着手。

### 5.13 [新規] Compaction Recovery Cycle 5完了・Evidence記録・将来Scope提案追加（2026-08-18発令 → 2026-08-18完了）

5回目のManual Compaction Recoveryが成功（対象4File全件、Before／After Hash一致）。Hash Manifest・運用メモの成功回数カウンタを4→5に更新した。合わせて、Cross-provider（Codex）からの評価コメントを含むEvidence Doc（[claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md](../../../../shared/history/automation/claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md)）と、新規将来Scope提案（第4.6節）を作成した。

## 6. Status

```text
Current Point            : Phase 2-E-I I-6（要件確定・実装未着手）を
                            継続追跡中。5回目のCompaction Recovery完了
                            を受け、Evidence記録（Cross-provider評価
                            含む）と新規将来Scope提案（自動圧縮・自動
                            復旧Cycle）を追加した。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE（2-E-I I-6自体はユーザーの実装開始
                            指示待りだが、これはTracker文書としての
                            Blockerではない）。
Controller-owned Next Work: ユーザーからのI-6実装開始指示を待つ。
                            その他、第4節の各予約Task Trigger成立を
                            待つ。
Exact Next Route          : ユーザーの次の判断待ち。
```
