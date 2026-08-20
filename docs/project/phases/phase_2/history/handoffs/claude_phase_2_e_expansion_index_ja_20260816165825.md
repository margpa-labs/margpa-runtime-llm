# Phase 2-E拡張作業 統合Index（Codex宛／新Task Claude宛 共用）

```yaml
document_id: claude_phase_2_e_expansion_index_20260816165825
status: index
phase: phase_2
subphase: phase_2_e_all
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役
role: design_governor
created_at: 2026-08-16 16:58:25 JST
language: ja
purpose: |
  当初Scope「Phase 2-E | Runtime Component切替基盤とDocumentation RAG
  Follow-up」から、ユーザー指示により大きく拡張したPhase 2-E一連作業
  （2-E-B〜2-E-G＋UI微調整5Round）の全Docsへの道しるべ。
  Context Windowが逼迫した状況でのユーザー指示により、
  「Codex復帰時の状況伝達」と「新TaskのClaude側設計統括者役が同じ
  状態から再開できること」の両目的を1つのFileで兼ねる。
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index第1節以降・実装・回答を始めないこと。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- 唯一の自己編集可Stable文書は[claude_side_design_governor_operating_notes_ja.md](../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)。**全文を読んでから作業を始めること。** Role Identity・Docs Write境界・Escalation境界・Git操作絶対禁止（最上位規則相当）・Permission Mode運用実績・ユーザーの作業Style（Docs化Preference）が記載されている。
- Git操作（Commit／Push／Branch操作等、Read-only以外の一切）は、Permission Modeに関わらず絶対禁止。
- Provider Memoryへの新規保存は禁止（Repository Docsが唯一の正本）。

## 0. 読み方（2Route共通）

各節、Path付きでFile一覧を挙げる。**まずこのIndex自体と、[claude_side_design_governor_operating_notes_ja.md](../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（運用メモ、Claude側の唯一の自己編集可Stable文書）を先に読むこと。** 個別Docsを読む前提知識（Role、Authority Hierarchy、Git操作絶対禁止、Bypass Permission実験の経緯、ユーザーの作業Style）がここに集約されている。

**Codex宛の場合**：第1節（当初Scope完了報告）→第2節（拡張作業の経緯・全体像）→第4節（現在Open／未着手）の順で。Git操作は一切していないので、`git status`で本Fileおよび関連Docsの新規性を確認すれば足りる。

**新Task Claude側設計統括者役宛の場合**：第0節→運用メモ全体→第2節（技術的な現在地の把握が主目的）→第3節（Frontend Architecture詳細）→第4節（次にやること）の順で。

## 1. 当初Scopeの完了報告（拡張前）

```text
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_completion_handoff_20260815075322.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_claude_completion_ja_20260815075428.md
```

「Runtime Component切替基盤とDocumentation RAG Follow-up」自体は上記で完了済み。以降は全てそこからの拡張。

## 2. 拡張作業の経緯・全体像（時系列）

### 2.1 Mac Manual Acceptance〜運用メモ確立（2026-08-15）

```text
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_mac_manual_acceptance_result_20260815112801.md（STOPPED、後に第9.1節等を例外的に追記）
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_claude_manual_acceptance_cycle_ja_20260815112801.md
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_mac_manual_acceptance_result_20260815202128.md（PASS、新規File）
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_claude_manual_acceptance_execution_cycle_ja_20260815202128.md
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_manual_acceptance_configuration_control_ux_finding_ja_20260815200020.md（「Apply完了」文言等のUX Finding）
docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md（新規作成、以降ずっと自己更新）
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_claude_role_authority_calibration_cycle_ja_20260815210742.md
```

### 2.2 Permission Mode（Bypass Permissions）実験の開始

```text
docs/project/shared/history/automation/automation_governance_evidence_claude_permission_mode_bypass_decision_ja_20260815231752.md
```

以降、2-E-D〜2-E-Gの各Cycleで「Bypass実験その2」のEvidenceを継続記録（次節に統合）。

### 2.3 2-E-B／2-E-C／2-E-D（Config Control DB表示、Mac専用context_size、Theme切替）

```text
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_b_e_c_completion_handoff_ja_20260815221756.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_b_e_c_claude_autonomous_cycle_ja_20260815221756.md
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_b_storage_version_field_addendum_ja_20260815223912.md
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_d_completion_handoff_ja_20260816004711.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_d_bypass_nonstop_cycle_ja_20260816004711.md
```

### 2.4 React/Vite移行〜Sidebar化〜Settings Modal化（2-E-E／F／G本体）

**設計（承認済み）**：
```text
docs/project/phases/phase_2/history/architecture/claude_phase_2_e_e_to_h_react_migration_design_ja_20260816102654.md
```

**実装Completion Handoff（各Sub-phase）**：
```text
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_e_completion_handoff_ja_20260816113534.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_e_bypass_nonstop_cycle_ja_20260816113534.md
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_f_completion_handoff_ja_20260816115426.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_f_bypass_nonstop_cycle_ja_20260816115426.md
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_g_completion_handoff_ja_20260816120251.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_g_bypass_nonstop_cycle_ja_20260816120251.md（E→F→G通算評価も含む）
```

Frontendは完全新規`frontend/`（React 19 + Vite 8 + TS strict）。Build成果物は`src/margpa_runtime_llm/web/static/`へ出力し既存FastAPI配信を無改修で維持。詳細ArchitectureはDesign Doc（上記）参照。

### 2.5 UI微調整5Round（実画面確認ベース、CSS専用）

```text
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_f_g_css_refinement_completion_handoff_ja_20260816132247.md（第1弾：Icon Toggle・透過・Auto-grow）
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_f_g_css_refinement_round2_completion_handoff_ja_20260816142248.md（第2弾：Header/Composer Fixed化、Turn Action統合）
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_f_g_css_refinement_round3_completion_handoff_ja_20260816144539.md（第3弾：背景を透過→Solidへ差し戻し、Bubble幅Content-driven化）
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_f_g_css_refinement_round4_completion_handoff_ja_20260816150655.md（第4弾：Composer枠追加（初版・Blue、後に訂正）、幅50%・Padding20%）
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_f_g_css_refinement_round5_completion_handoff_ja_20260816151713.md（第5弾：枠色訂正（Neutral）、Topbarにも枠、幅57%・Padding10%）
docs/project/shared/history/automation/automation_governance_evidence_claude_frontend_design_capability_self_assessment_ja_20260816161000.md（Claude自身のFrontend/Web Design能力の自己評価）
```

**現在のCSS最終状態（新Task側で実装を触る場合の前提）**：`.topbar`／`.composer`はPosition Fixed（`--sidebar-offset` Custom Property経由でSidebar幅に自動追従、`.app-shell`へ`transform`は使わない——理由は上記round2 Handoff第3節）。両者とも枠線`var(--message-assistant-bg)`・背景`var(--bg-page)`。`.message`は`width:fit-content; min-width:15%; max-width:57%`（`.main-content`基準）。`.messages`は`padding:18px 10%`。

## 3. 現Frontend Architecture要点（新Task Claude側設計統括者役 向け）

```text
frontend/                          Node.js/React/Vite。Python Packageから完全独立
  src/App.tsx                      中心Orchestration（旧app.jsの状態機械を忠実移植）
  src/components/Sidebar/          Sidebar・SidebarHeader・ChatList・ChatListItem・AccountFooter
  src/components/SettingsModal/    SettingsModal（左Nav＋右Content、設定／アドバンスモード）
  src/components/SidebarToggleButton.tsx  Fixed Icon Button（Sidebar内外で位置固定）
  src/styles/app.css               CSS Custom Property Token化（:root＝White既定、
                                    :root[data-theme="dark"]＝Dark）
  npm run {lint,typecheck,test,build}  全てClean状態を維持（本Index作成時点）
```

Backend側は無改修（Frontend専用作業のため）。`pytest -q`＝664 passed, 3 deselected（本Index作成時点）。

## 4. 現在Open・未着手（次にやること）

```text
- 2-E-H（余力枠）：会話「名前変更」「削除」の新規Backend実装
  （Domain→Port→Adapter→API→Test一式）＋Frontend配線。**実装完了**
  （2026-08-16、Dialog 0件Non-stop完走）。設計Doc
  （claude_phase_2_e_h_process_breakdown_design_ja_20260816173714.md）、
  Completion Handoff
  （claude_phase_2_e_h_completion_handoff_ja_20260816193010.md）、
  Automation Governance Evidence
  （automation_governance_evidence_phase_2_e_h_bypass_nonstop_cycle_ja_
  20260816193010.md）参照。Backend（title・ConversationState.DELETED
  ・sqlite-3 Migration・Rename/Delete Route）・Frontend（ChatListItem
  Inline編集・Delete確認Dialog）ともValidation Clean、実Browser確認
  （Light/Dark）済み。第5.2節の「User Self-service Restore UI」は
  引き続き未定事項のまま（H Scope外）。
- UIの細部の残り：ユーザー判断で「Phase 4以降に回す」と明言済み
  （2026-08-16）。今回のUI微調整はここで一旦Close。
- claude_side_design_governor_operating_notes_ja.md 第6節に
  「index作って」Trigger予約Taskの記載あり（本File作成をもって
  実行済みと見なしてよい）。
```

## 5. Status

```text
Current Point            : Context Window逼迫（残り約8%）のため、ユーザー
                            指示によりCodex宛／新Task Claude宛の統合Index
                            として作成。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザーの次の判断（新Task化 or 本Session継続）。
Exact Next Route          : 第4節参照。
```
