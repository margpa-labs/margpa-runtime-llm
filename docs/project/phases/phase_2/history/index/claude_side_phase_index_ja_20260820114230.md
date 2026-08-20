# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260820114230
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-20 11:42:30 JST
updated_at: 2026-08-20 11:55:34 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence）
  における「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260820035431.md](claude_side_phase_index_ja_20260820035431.md)
  （2026-08-20 03:54:31 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：docs/配下全File精査に基づく統合Governance Doc
  [claude_side_automation_cross_provider_compaction_governance_ja.md]の新規作成完了、
  および明日（利用可能量回復後）のPhase 3一括実装着手予告。ユーザー指示
  により、今回は作業用（Current Operational State）Indexのみを作成する
  （Recovery Indexは前版のものを維持、新規作成なし）。

  2026-08-20 11:55:34 JST追記：ユーザーより明示の例外指示により、通常は
  新しい後継Fileを作る運用（第0節参照）を今回だけ省略し、本Fileへ直接
  追記した。対象は、Governance Docの改名、およびSettings Modal Resize
  作業内容の完全記録Docの新規作成。
created: Claude Code
```

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_settings_modal_resize_verification_failure_recovery_index_ja_20260820035431.md](../handoffs/claude_settings_modal_resize_verification_failure_recovery_index_ja_20260820035431.md)（2026-08-20 03:54:31 JST作成）。本Fileは今回、作業用Indexのみの更新であり、Recovery Indexは前版のものを継続して指す（新規作成なし）。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。今回作成した[claude_side_automation_cross_provider_compaction_governance_ja.md](../../../../shared/automation/claude_side_automation_cross_provider_compaction_governance_ja.md)第2.2節にも、この未解決状態を明記した。2026-08-20のCodex復活時に確認できる可能性がある。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。
- Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘。独立Failure Docとして記録するかはユーザー判断待ち。
- ユーザーのPort 8000 Serverが、Settings Modal Resize検証中に接続不能を繰り返した根本原因は未特定（前版から継続）。

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

**Trigger**：「Codex復活」（2026-08-20予定、成立が近い）。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、根本原因調査済み、`top_k`引き上げ以外は見送り）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。Subject Coverage機構自体への変更は、`RAG丸々改善Phase`まで見送り確定。**Trigger**：`RAG丸々改善Phase`開始。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。設計参照材料：[claude_side_automation_cross_provider_compaction_governance_ja.md](../../../../shared/automation/claude_side_automation_cross_provider_compaction_governance_ja.md)第3.6節・第3.8節（「Turn到来時の自己特定は可能だが、Turn非依存の自発性は本Architecture上不成立」という実測制約）。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。3.4と同じ制約・参照材料を前提とする。

### 3.7 既知の課題：Documentation RAG検索結果固定化・無関係質問への誤発火（2026-08-19、Pattern 1は`top_k`引き上げ済み、Pattern 2は見送り確定）

詳細は[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。**Trigger**：`RAG丸々改善Phase`開始。

### 3.8 Phase 3実装：Governance Definition Platform構築のClaude一括実装（2026-08-19提示 → 2026-08-19夜、明日実施が確定）

ユーザーより明示指示：「明日キミの利用可能量が回復したら、Phase 3を一気にやってもらうから。」——これにより、従来「Codexとユーザーによる設計完了・Claude側への引き継ぎ待ち」としていたTriggerが、**日付付きの確定予定**へ具体化した。詳細は前版・[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](../handoffs/claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)第2.7節参照。この一括実装は、Automation／Compaction Recovery長期実験（長期戦Companion、`long_running_mode_active`切替）を兼務する予定。**Trigger**：Claude側の利用可能量回復（2026-08-21、日付未確定だが「明日」と明示）。

### 3.9 Settings Modal Resizeのユーザー実画面での最終確認（2026-08-19、ユーザーにより対応打ち切り）

CSS・Build成果物は完了・自己検証済みだが、ユーザーの実Browserでの最終確認は未完了。詳細は[claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328.md)。**Trigger**：ユーザーからの再開指示。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260820035431.md](claude_side_phase_index_ja_20260820035431.md)第4節）を参照。長期戦運用Companion確立、RAG既知課題2件の根本原因調査、`top_k`引き上げ、初のAuto-Compaction Recovery（Cycle 7）、RAG Pattern 2見送り決定、自己現在地特定能力の実測Evidence化、Settings Modal Resize実装・検証Failure記録が完了。

### 4.2 Automation／Cross-provider／Compaction統合Governance Docの新規作成（2026-08-20発令 → 完了）

ユーザー指示により、`docs/`配下全File（1,864件規模）をRead-onlyで精査し（4件のExplore Agentを並行起動、自身も[Automation Governance Index](../../../../shared/automation/automation_governance_index_ja.md)・[Automation Control Profile](../../../../shared/automation/automation_control_profile_ja.md)・[Automation／Governance Evidence Log](../../../../shared/automation/automation_governance_evidence_log_ja.md)（1,288行）・[Role Authority Matrix](../../../../shared/task_roles/role_authority_matrix_ja.md)・[Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)・主要Cross-provider／Compaction Evidence群を直接精読）、Automation・Cross-provider・Compaction（Manual・Auto）の3テーマを統合したStable Governance Doc、[claude_side_automation_cross_provider_compaction_governance_ja.md](../../../../shared/automation/claude_side_automation_cross_provider_compaction_governance_ja.md)を`docs/project/shared/automation/`へ新規作成した。

4件のAgent全ての完了報告を受け、それぞれの発見を本Docへ反映済みである。Phase 2内の2件の新規Cross-provider Incident（Mac Manual Acceptance文言Near-miss、P2E-GOV-001のSelf-report不一致）、Mode-invariant Authority Correction（2026-08-11、通常運転／Automation権限表の一本化という本Corpus最大級の是正）、`docs/project/shared/history/planned_work/`配下のCompaction関連未着手構想3件（Context Observatory、LLM Self Context Awareness、LLM Native自動復旧Cycle）、Fallibility Controlの無例外適用原則、PAUSED_RESOURCE_LIMIT、Phase 2＝Feasibility／Phase 3＝Reproducibility区分、長期戦Companionの前史（Phase 2 Subphase Preplan第10.2節）を新たに反映した。既存正本を置き換えず、統合Viewとして位置づけている。反映後、Link解決・文字化けの自己Checkを再実施し、全て通過を確認した。

### 4.3 統合Governance Docの改名（2026-08-20発令 → 完了）

ユーザー指示により、`claude_side_automation_cross_provider_governance_ja.md`を`claude_side_automation_cross_provider_compaction_governance_ja.md`へ改名した（Docが扱う3テーマのうちCompactionがFilename上抜けていたための訂正）。File本体（`document_id`・自己参照箇所2件・Update Policy節のSnapshot命名規則）、および本Fileを含む参照元1件のLinkを、いずれも新Filenameへ更新済み。

なお、改名作業の過程で、`git mv`を一度誤って実行した（Git状態変更は運用メモ第2.4節により絶対禁止）。対象FileがGit管理下に無かったため`git`側は"not under version control"で即座に失敗し、Repository状態への実害は無かったが、Process上の逸脱として本Fileに記録する。以後は素の`mv`のみを使用した。

### 4.4 Settings Modal Resize作業内容の完全記録Docの新規作成（2026-08-20発令 → 完了）

ユーザー指示「昨日やってた、『設定画面のサイズを変える』の件について、やった事をdocsに全部書く」を受け、[claude_settings_modal_resize_complete_work_record_ja_20260820115319.md](../../../../shared/history/automation/claude_settings_modal_resize_complete_work_record_ja_20260820115319.md)を新規作成した。既存の[claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_frontend_verification_loop_and_unwarned_system_permission_prompt_ja_20260820035328.md)（Failure分析・教訓）とは役割を分離し、新規Docは「何を、どの順で、どう試したか」という作業内容そのものをLossless水準で時系列記録した（Viewport測定の試行錯誤、CSS変更2回の詳細、Node EPERM障害、自己Dev Serverでの初回視覚確認、Production Build、`screencapture`無警告Dialog事象、一意Marker技術によるBuild Pipeline健全性実証、最終Deliverable状態）。Link解決・文字化けの自己Check済み。

## 5. Status

```text
Current Point            : Automation／Cross-provider／Compaction統合
                            Governance Doc新規作成・改名完了。Settings
                            Modal Resize作業内容の完全記録Doc新規作成
                            完了。明日、利用可能量回復後にPhase 3一括
                            実装へ着手予定（長期戦Automation実験を兼務）。
Files Created／Modified   : 本File（直接追記、ユーザー例外指示による）、
                            claude_side_automation_cross_provider_
                            compaction_governance_ja.md（改名後Filename）、
                            claude_settings_modal_resize_complete_work_
                            record_ja_20260820115319.md（新規作成）。
Validation                : 上記いずれもLink解決・文字化けの自己Check済み。
Open Current Blocker      : NONE
Controller-owned Next Work: 明日（2026-08-21予定）、利用可能量回復を
                            確認した上でPhase 3一括実装に着手する。
Exact Next Route          : ユーザーからの次の指示待ち、または明日の
                            利用可能量回復通知待ち。
```
