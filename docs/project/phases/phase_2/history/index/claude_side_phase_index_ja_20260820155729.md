# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260820155729
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-20 15:57:29 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence）
  における「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260820114230.md](claude_side_phase_index_ja_20260820114230.md)
  （2026-08-20 11:42:30 JST作成、11:55:34 JST追記）の後継Fileである。前版の
  内容は重複して再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：Settings Modal内部構成の全面再設計・メイン画面
  挨拶文追加・完了Evidence作成が完了し、ユーザーよりUI変更作業の全完了が
  明示されたこと。あわせて、ユーザーの週間利用可能量が僅少となったため
  本日の実装作業を終了し、明日（利用可能量回復後）予定のPhase 3一括実装
  着手に備えた引き継ぎIndexとして、新しいRecovery Indexとあわせて作成した。
created: Claude Code
```

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_settings_modal_ui_restructure_and_phase3_handoff_recovery_index_ja_20260820155729.md](../handoffs/claude_settings_modal_ui_restructure_and_phase3_handoff_recovery_index_ja_20260820155729.md)（2026-08-20 15:57:29 JST作成）。

## 2. Open Questions（未解決、Trigger待ちではないもの）

- Codex側が「Claude側設計統括者役」という名称・Authority Hierarchyをどう認識しているか、Cross-provider間で正式合意された記録はまだない（2026-08-15時点から未確認のまま）。2026-08-20のCodex復活時に確認できる可能性がある。
- 運用メモ自体の最終的な設置場所・Status（`provisional_self_maintained`から`current`等への遷移条件）は、ユーザーの今後の判断による。
- 2-E-I #4（Context使用率Injection Toggle OFF状態での、思考過程・メタ会話のような出力混入）の原因は未特定。
- Cycle 5のCompaction Recovery報告における、Procedure Fidelityの精度に関する指摘。独立Failure Docとして記録するかはユーザー判断待ち。
- ユーザーのPort 8000 Serverが、Settings Modal Resize検証中（前々回Indexの時点）に接続不能を繰り返した根本原因は未特定のまま（前版から継続）。**本日判明した「見た目が変わらない」報告の真因（大画面上での相対的変化量の小ささ）とは別件であり、混同しないこと。**

## 3. 予約Task（未着手、Trigger待ち）

### 3.1 Temporal Authorityを持ったAgentic Runtime（2026-08-17、ユーザー提示、Codex宛予約）

**Trigger**：「Codex復活」（2026-08-20予定、成立が近い）。

### 3.2 Context Observatory（2026-08-17、ユーザー提示、Phase 3候補）

**Trigger**：「Phase 3の頭で作れそうなら作りたいが、後でもよい」。

### 3.3 既知の課題：Documentation RAG Subject Coverage Bug（2026-08-18、根本原因調査済み、`top_k`引き上げ以外は見送り）

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。Subject Coverage機構自体への変更は、`RAG丸々改善Phase`まで見送り確定。**Trigger**：`RAG丸々改善Phase`開始。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。設計参照材料：`claude_side_automation_cross_provider_compaction_governance_ja.md`第3.6節・第3.8節（「Turn到来時の自己特定は可能だが、Turn非依存の自発性は本Architecture上不成立」という実測制約）。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。3.4と同じ制約・参照材料を前提とする。

### 3.7 既知の課題：Documentation RAG検索結果固定化・無関係質問への誤発火（2026-08-19、Pattern 1は`top_k`引き上げ済み、Pattern 2は見送り確定）

詳細は[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)、および[documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md](../operations/documentation_rag_root_cause_investigation_pre_fix_ja_20260819181056.md)。**Trigger**：`RAG丸々改善Phase`開始。

### 3.8 Phase 3実装：Governance Definition Platform構築のClaude一括実装（2026-08-19提示 → 明日2026-08-21着手予定）

ユーザーより改めて明示指示：「明日、利用可能量が回復したら、Phase 3をまるごと一気にやる」。本日（2026-08-20）は週間利用可能量が僅少となったため、実装作業はここで終了し、明日へ引き継ぐ。この一括実装は、Automation／Compaction Recovery長期実験（長期戦Companion、`long_running_mode_active`切替）を兼務する予定。**Trigger**：Claude側の週間利用可能量回復（2026-08-21予定）。着手前の必読物は[Recovery Index](../handoffs/claude_settings_modal_ui_restructure_and_phase3_handoff_recovery_index_ja_20260820155729.md)第0.0節参照。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260820114230.md](claude_side_phase_index_ja_20260820114230.md)第4節）を参照。長期戦運用Companion確立、RAG既知課題2件の根本原因調査、`top_k`引き上げ、初のAuto-Compaction Recovery（Cycle 7）、RAG Pattern 2見送り決定、自己現在地特定能力の実測Evidence化、Settings Modal Resize実装・検証Failure記録、Automation／Cross-provider／Compaction統合Governance Doc新規作成・改名、Settings Modal Resize作業内容の完全記録Doc新規作成が完了。

### 4.2 Settings Modal内部構成の全面再設計・メイン画面挨拶文追加・完了Evidence作成（2026-08-20発令 → 完了）

ユーザー指示により、Settings ModalのSizeを870px→1450px→1550pxへ追加変更し、「設定」Tab・「アドバンスモード」Tab双方の内部構成（Nav Size、Button/OFF-ON Toggle Size統一、2 Column化、Field表示順序、説明文の書き換え）を全面再設計した。過程で、2 Column化に伴うCSS副作用Bug（`.switch-row{align-self:end}`による意図しない右端揃え）を発見・修正した。あわせて、メイン画面の空状態表示へ挨拶文（日英）を追加した。

「見た目が変わらない」という繰り返し報告については、Claude側Browser Paneでの実測とユーザー提供Screenshotの比例計算により、Code・Build・配信経路にはBugが無いことを確認した上で、最終的にユーザー自身により「大画面上での相対的な変化量の小ささが原因」と確認され、解消した。

ユーザーより、これら（Settings Modal Size変更・内部構成変更・メイン画面挨拶文追加）3項目をもって、UIをいじる作業は全部完了と明示された。詳細は[claude_settings_modal_ui_restructure_completion_evidence_ja_20260820154940.md](../../../../shared/history/automation/claude_settings_modal_ui_restructure_completion_evidence_ja_20260820154940.md)。Link解決・文字化けの自己Check済み。

## 5. Status

```text
Current Point            : Settings Modal内部構成の全面再設計・メイン画面
                            挨拶文追加・完了Evidence作成が完了。ユーザー
                            よりUI変更作業の全完了が明示された。週間利用
                            可能量僅少のため、本日の実装作業はここで終了。
Files Created／Modified   : frontend/src/styles/app.css、
                            frontend/src/components/SettingsPanel.tsx、
                            frontend/src/components/ConfigurationControlPanel.tsx、
                            frontend/src/components/MessageList.tsx、
                            frontend/src/i18n/translations.ts、本File、
                            対応するRecovery Index・完了Evidence（いずれも
                            新規作成）。
Validation                : Settings Modal変更はClaude側Browser Paneでの
                            実測により確認済み。本File・Recovery Indexは
                            Link解決・文字化けの自己Check済み。
Open Current Blocker      : NONE
Controller-owned Next Work: 明日（2026-08-21予定）、利用可能量回復を
                            確認した上でPhase 3一括実装に着手する。
Exact Next Route          : 明日の利用可能量回復通知待ち。着手前に運用
                            メモ・本File・対応するRecovery Indexを全文
                            読了すること。
```
