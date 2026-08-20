# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260819002344
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-19 00:23:44 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260818231009.md](claude_side_phase_index_ja_20260818231009.md)
  （2026-08-18 23:10:09 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：Phase 2-E-I I-6（#2・#3・新規Toggle・#5）の
  実装完了。#5は実装着手後の調査でBackend Data Model欠落が真因と判明し、
  ユーザー確認を経てBackend拡張を伴う修正を実施した。

  **前版からの構造変更**：第2節「現在進行中のSub-phase」を再び廃止する
  （I-6完了により、2-E-I全体：I-1〜I-6が完了したため）。節番号は前版の
  第3節（Open Questions）以降を1つ繰り上げた。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260819113202.md](claude_side_phase_index_ja_20260819113202.md)（2026-08-19 11:32:02 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md](../handoffs/claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md)（2026-08-18 22:36:00 JST作成。本File作成時点で変更なし。次のManual Compaction前に、運用メモ第3.12節に従い最新性を確認し、必要なら新規Recovery Indexを作成する）。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。原因調査自体もまだTrigger・担当が確定していない。
- Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘（「3Docs明示的再読込」と宣言しつつ、実際は1Fileのみ本Turn内Read Tool・残り2FileはSystem再挿入内容を利用）。独立Failure Docとして記録するかはユーザー判断待ち（詳細は[claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md](../../../../shared/history/automation/claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md)第3.4節・第4節）。

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

構想は[future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md](../../../../shared/history/planned_work/future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)。**Trigger**：「Codex復活」。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_context_observatory_ja_20260817234734.md](../../../../shared/history/planned_work/future_scope_proposal_context_observatory_ja_20260817234734.md)。第3.1節の縮小版は2-E-Iとして完了済み。残る部分は引き続きTrigger待ち。**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、修正未着手）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。**Trigger**：「RAG丸々改善Phase」。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)。第2.1節は2-E-Iとして完了済み。第2.2節はAgent Runtime基盤が前提でTrigger待ち。**関連**：第3.6節（自動復旧側を補完する続編提案）。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

構想は[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)。**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md](../../../../shared/history/planned_work/future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md)。MARGPA Runtime自身が生成するLLMに、Claude Code等のAgent Harnessが既に備える「自動圧縮→自動復旧」Cycleに相当する機能を持たせる構想。第3.4節の続編（自動復旧側を補完）。**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260818231009.md](claude_side_phase_index_ja_20260818231009.md)第5節、5.1〜5.13）を参照。「index作って」Trigger実行、Recovery Index前倒し再作成、運用メモ全面再編成、2-E-I I-1〜I-5完了、Compaction Recovery Hash記録手法の改善、Failure記録2件の追加、Compaction Recovery Cycle 5完了・Evidence記録・将来Scope提案追加。

### 4.2 Phase 2-E-I I-6完了（2026-08-18発令 → 2026-08-19完了）

詳細は[claude_phase_2_e_i_i6_implementation_ja_20260819002250.md](../../../../shared/history/automation/claude_phase_2_e_i_i6_implementation_ja_20260819002250.md)。#2（Hover Tooltip復元）・#3（Panel外Click Close）・新規「コンテキスト表示」Toggle・#5（「再開」表示不具合）を実装。#5は当初想定（Frontend表示制御のみ）と異なり、Backend Data Model（Session Active状態のList露出）欠落が真因と判明し、Schema変更なしでBackend拡張（SQLite JSON1による`EXISTS`副問い合わせ）により修正した。Backend pytest 694件・Frontend Vitest 75件含む全Validation Clean、実Browser確認完了。#1（会話切替でGauge初期化）は引き続き保留、#4（Toggle OFF時の謎の出力混入）は引き続きScope外。

## 5. Status

```text
Current Point            : Phase 2-E-I（I-1〜I-6）が全て完了。現在進行中の
                            Sub-phaseは無し。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Tracker文書）
Open Current Blocker      : NONE
Controller-owned Next Work: 第3節の各予約Task Trigger成立を待つ。次の
                            まとまった作業指示、またはManual Compaction
                            実施の、いずれかのユーザー判断を待つ。
Exact Next Route          : ユーザーの次の判断待ち。
```
