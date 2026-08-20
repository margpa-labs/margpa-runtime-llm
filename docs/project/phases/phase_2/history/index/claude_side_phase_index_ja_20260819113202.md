# Claude側設計統括者役 — Phase 2 Current Operational State Index

```yaml
document_id: claude_side_phase_2_operational_state_index_20260819113202
status: tracker
phase: phase_2
subphase: claude_side_design_governor_operating_notes_companion
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task Claude側設計統括者役／本Task自身（復旧時）
role: design_governor
created_at: 2026-08-19 11:32:02 JST
language: ja
purpose: |
  3層モデル（Operating Rules／Current Operational State／History-Evidence、
  [claude_side_design_governor_operating_notes_ja.md]第3.3節参照）における
  「Current Operational State」層を担う、Phase 2固有のIndexである。

  本Fileは、前版
  [claude_side_phase_index_ja_20260819002344.md](claude_side_phase_index_ja_20260819002344.md)
  （2026-08-19 00:23:44 JST作成）の後継Fileである。前版の内容は重複して
  再記載せず、前版作成以降の差分を中心に更新した。

  本File作成の直接の契機：前版作成以降、実Browser確認Feedbackへの対応
  （Scroll Pin位置修正・Composer Clearance・初回送信2回Click Bug修正・
  Streaming中Markdown逐次変換）とFailure記録2件・運用メモRule追加が
  未反映のまま蓄積していたため、まとめて反映する。合わせて、実機確認
  で新たに発見したDocumentation RAGの既知課題を予約Taskへ追加する。
created: Claude Code
```

> **後継Fileあり**：本Fileは[claude_side_phase_index_ja_20260819144637.md](claude_side_phase_index_ja_20260819144637.md)（2026-08-19 14:46:37 JST作成）に引き継がれた。最新状態はそちらを参照。

## 0. 本Fileの位置づけ

本Fileは、Claude側設計統括者役が現在保持している「進行中のSub-phase」「未解決のOpen Question」「未着手の予約Task（Trigger待ち）」「完了済みだが記録として残す予約Task」を一元管理する、Phase 2固有のCurrent Operational State Indexである。

**運用Rule（恒久的な行動規範）はここには書かない**——それは[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)（以下「運用メモ」）側の役割である。**Incident・Failure・Success・実験結果等の詳細な経緯もここには書かない**——それは`docs/project/shared/history/`配下の役割である。

本Fileは、内容が大きく更新されるたびに、既存Fileを上書きせず、新しい日付を持つ後継Fileとして作り直す運用とする。

## 1. 最新の引き継ぎ用／自己復旧用Index（Recovery Index）へのPointer

**現時点の最新Recovery Index**：[claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md](../handoffs/claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md)（2026-08-19 11:36:39 JST作成。ユーザーが予定するManual Compaction直前に作成）。

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

詳細は[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](../operations/documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)。**Trigger**：「RAG丸々改善Phase」。**関連**：第3.7節（同一Triggerで扱う新規観測分）。

### 3.4 LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](../../../../shared/history/planned_work/future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)。第2.1節は2-E-Iとして完了済み。第2.2節はAgent Runtime基盤が前提でTrigger待ち。**関連**：第3.6節（自動復旧側を補完する続編提案）。

### 3.5 margpa-runtime-llmのAWS配置（2026-08-18、ユーザー指示、予約）

構想は[future_scope_proposal_aws_deployment_ja_20260818171240.md](../../../../shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md)。**Trigger**：「なるべく早めに」、具体的Timing未確定。

### 3.6 LLM Native自動Context圧縮・自動復旧Cycle機能（2026-08-18、ユーザー提示、Phase 3候補）

構想は[future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md](../../../../shared/history/planned_work/future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_ja_20260818230920.md)。MARGPA Runtime自身が生成するLLMに、Claude Code等のAgent Harnessが既に備える「自動圧縮→自動復旧」Cycleに相当する機能を持たせる構想。第3.4節の続編（自動復旧側を補完）。**Trigger**：Phase 3、Agent Runtime基盤の整備状況次第。

### 3.7 [新規] 既知の課題：Documentation RAG検索結果固定化・無関係質問への誤発火（2026-08-19、修正未着手）

詳細は[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)。Query内容に関わらず検索結果が固定化するPattern、および明らかに無関係な質問でもRAGが誤発火するPatternの2件。第3.3節の既存Known Issueとは別事象（送信Errorではなく検索結果自体の不適切さ）。**Trigger**：第3.3節と同一、「RAG丸々改善Phase」。ユーザー指示により優先度は低（週間利用可能量の制約、Docs記録済みで現状は十分）。

## 4. 完了済み予約Task（記録として残す）

### 4.1（前版までの完了項目）

前版（[claude_side_phase_index_ja_20260819002344.md](claude_side_phase_index_ja_20260819002344.md)第4節、4.1〜4.2）を参照。2-E-I I-1〜I-6完了（含むBackend Session Active状態拡張）。

### 4.2 I-6実機Feedback対応：Hover範囲修正・送信時Scroll Pin（2026-08-19発令 → 完了）

詳細は[claude_i6_hover_refinement_and_send_scroll_pin_ja_20260819090717.md](../../../../shared/history/automation/claude_i6_hover_refinement_and_send_scroll_pin_ja_20260819090717.md)。#2 Hover TooltipをButton自身のHoverのみへ限定。送信時、入力Logを画面上部付近へPinし、Streaming中の継続的な下方Scrollを解消。作業中に無関係な既存Bug（新規会話への初回送信が2回Clickを要する）を発見・報告。

### 4.3 Scroll Pin根本原因調査・Gap Filler方式による最終修正（2026-08-19発令 → 完了）

詳細は[claude_scroll_pin_root_cause_investigation_and_final_fix_ja_20260819100203.md](../../../../shared/history/automation/claude_scroll_pin_root_cause_investigation_and_final_fix_ja_20260819100203.md)。ユーザーからの完了確認Challenge（「3回やっても変わらない」）を受けて再調査し、会話が短い間は`.main-content`にScroll可能範囲が無くPin計算が無効化されていたことを特定。Gap Filler（Pin中は`min-height:100vh`のDummy要素を追加）で解決。副次的に、生成完了直後にPinが解除される別Bugも発見・修正。前回の「実Browser確認完了」報告が実際には短い会話・完了後の状態を十分Coverしていなかった点を反省記録。

### 4.4 Scroll Pin Gap値調整・Composer Clearance新規実装（2026-08-19発令 → 完了）

詳細は[claude_scroll_pin_gap_tuning_and_composer_clearance_ja_20260819102848.md](../../../../shared/history/automation/claude_scroll_pin_gap_tuning_and_composer_clearance_ja_20260819102848.md)。Pin位置を56→76pxへ調整。長文出力完了時に出力Log最下部がComposer（Message入力欄）の裏に隠れる問題を、Composer実要素との直接比較による新規Clearance機構で解消。

### 4.5 指示解釈Failure記録2件・運用メモ第3.14節新設（2026-08-19発令 → 完了）

ユーザーから「なぜ『下げて』という言葉と矛盾する候補を曖昧さの材料にしたのか」との指摘を受け、[claude_output_anomaly_unverified_interpretation_candidate_ja_20260819105409.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_unverified_interpretation_candidate_ja_20260819105409.md)を作成。運用メモへ第3.14節「不明瞭判定前の候補整合性Check」を新設する過程で、Evidence層の内容をRule本文へ混入させる別Failureも発生し、[claude_output_anomaly_rules_evidence_layer_mixing_ja_20260819105451.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_rules_evidence_layer_mixing_ja_20260819105451.md)として別途記録。該当箇所は運用メモから削除済み。

### 4.6 Streaming中のMarkdown逐次変換実装（2026-08-19発令 → 完了）

詳細は[claude_streaming_markdown_rendering_ja_20260819110633.md](../../../../shared/history/automation/claude_streaming_markdown_rendering_ja_20260819110633.md)。Markdown変換Gate条件から`isFinal`要件を除去し、Streaming中も見出し・箇条書き・Code Block等を逐次整形表示。Copy機能は元々表示ではなく生Markdown原文を直接参照する配線のため変更不要。実Browser確認完了。

### 4.7 Markdown表（Table）のStreaming中崩れ修正（2026-08-19発令 → 完了）

詳細は[claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md](../../../../shared/history/automation/claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md)。独自Markdown Parser（`safeMarkdown.tsx`）にGFM Pipe Table対応（Header／Delimiter行検出、Escaped Pipe、Alignment、Streaming途中の非例外Fallback）を新規実装。根本原因は、Table行が既存の`paragraph`Fallbackへ落ち、連結された生改行がBrowserの空白折り畳みで失われていたこと。実LLM出力での検証中に、Delimiter行の二重Pipe（実際に観測されたModel出力Artifact）に対する追加耐性修正も実施。Vitest 16/16・ESLint・tsc・Build全てClean、実Browser確認（Dark／White、Streaming中・完了後）完了。検証中、本修正と無関係な既存Test基盤問題（`App.test.tsx`・`usePreference.test.tsx`の`localStorage` Error）を発見・報告のみ実施（詳細Doc第7節参照、対応はScope外）。

### 4.8 表を含むMessageの横幅拡張（message-wide、2026-08-19発令 → 完了）

詳細は[claude_message_wide_bubble_for_table_content_ja_20260819123330.md](../../../../shared/history/automation/claude_message_wide_bubble_for_table_content_ja_20260819123330.md)。通常Messageの横幅上限（`max-width: 57%`）は変更せず、Markdown表を含むMessageのみ`.message-wide`（`max-width: 85%`、約1.5倍）を付与する仕組みを実装。`safeMarkdown.tsx`を`parseSafeMarkdown`＋新規`renderSafeMarkdownBlocks`／`containsTable`へ分離し、二重Parseを避けた。Vitest 25/25・ESLint／tsc／Build Clean、実Browser確認（通常57%／表85%の実測値差分）完了。**ユーザー自身の実機確認済み**（2026-08-19）：表を含むMessageのみ横幅が拡張され、直後に通常の質問へ切り替えると元の最大幅へ正しく戻ることを確認。

### 4.9 表現重視モード（Style限定Prompt Injection、2026-08-19発令 → 完了）

詳細は[claude_expressive_mode_style_only_prompt_injection_ja_20260819124942.md](../../../../shared/history/automation/claude_expressive_mode_style_only_prompt_injection_ja_20260819124942.md)。推論・結論・事実内容は変えず、口調（ノリ・テンション）・「www」等の砕けた表現・顔文字・絵文字・記号装飾のみを変化させるOpt-in Toggleを実装。既存の「Context使用率Prompt Injection」と同じ設計Pattern（専用Enum＋条件付きSYSTEM Message Injection）を踏襲。既定Disabledとし、素のModel挙動と区別できるよう「設定」の「基本」Categoryへ開示Note付きで配置（ユーザー要求「元のQwenなのか改造Qwenなのかわかりずらくならない」ため）。Backend pytest 688 passed・Frontend Vitest Pass（既知の無関係localStorage問題を除く）・ESLint／tsc／Build Clean、実Browser確認（OFF＝平板な回答／ON＝事実内容は同一のまま絵文字・顔文字・www付きの回答）完了。**ユーザー自身の実機確認済み**（2026-08-19）：「OpenAIって何年から存在するんだっけ？」という同一質問に対し、OFF／ON双方で「2015年設立」という結論・年表の実質的内容は保持されたまま、ON時のみ絵文字・「www」・Casualな口調が付加されることを確認。

### 4.10 表Cell内`<br>`混入の修正（2026-08-19発令 → 完了）

詳細は[claude_table_cell_br_line_break_fix_ja_20260819132416.md](../../../../shared/history/automation/claude_table_cell_br_line_break_fix_ja_20260819132416.md)。ユーザーが多列比較表（ChatGPT／Claude／Gemini／Qwen比較、Screenshot添付）で発見。「生HTMLを一切Renderしない」というSecurity方針上、`<br>`もText扱いされていたことが原因（GFM表Cellの改行にはこれが標準的手法）。属性を一切持ち得ない`<br>`・`<br/>`・`<br />`（大小文字問わず）のみを認識する狭いExceptionを追加し、属性付きTag等は従来通りInert Textのまま——Security Invariantは保持。Vitest 18/18・ESLint／tsc／Build Clean、実Browser確認（`hasLiteralBrText: false`・`realBrElements: 34`の直接測定）完了。

### 4.11 表Cell内箇条書きMarker（`-`）残留の修正（2026-08-19発令 → 完了）

詳細は[claude_table_cell_bullet_marker_fix_ja_20260819133331.md](../../../../shared/history/automation/claude_table_cell_bullet_marker_fix_ja_20260819133331.md)。第4.10節の`<br>`修正直後、ユーザーが同一箇所で発見した続報：`<br>`は消えたが、箇条書きMarkerの`-`（例：「- 会話型LLM」）はそのまま残留していた。Block Level Listの検出が、表Cell（`<br>`区切りの一枚岩文字列としてInline Parserへ渡る）には及ばないことが原因。`parseInline`へ「現在行の先頭にいるか」を追跡する状態（文字列先頭・`<br>`直後にのみ真）を追加し、その位置での`-`/`*`/`+`MarkerをBullet文字「• 」へ置換。文中のMid-line Hyphen（`-5`等）や通常のBlock Level Listには無影響。Vitest 20/20・ESLint／tsc／Build Clean、実Browser確認（ユーザー報告と同一Cell内容を実際に生成させ`hasLiteralDash: false`・`hasBullet: true`を直接測定）完了。

## 5. Status

```text
Current Point            : Phase 2-E-I I-6完了後の実Browser確認Feedback
                            対応（Scroll Pin・Composer Clearance・初回
                            送信Bug・Streaming Markdown・Markdown表崩れ
                            修正・表Message横幅拡張・表現重視モード・表
                            Cell内`<br>`混入修正・表Cell内箇条書きMarker
                            残留修正）が全て完了。表幅拡張・表現重視
                            モードは、ユーザー自身の実機確認も完了。
                            Documentation RAG検索結果の異常は、ユーザー
                            指示によりTrigger待ちのまま優先度低で保留
                            （第3.7節）。
Files Created／Modified   : frontend/src/lib/safeMarkdown.tsx、
                            frontend/src/lib/safeMarkdown.test.tsx、
                            frontend/src/components/MessageBubble.tsx、
                            frontend/src/components/MessageBubble.test.tsx、
                            frontend/src/styles/app.css（第4.7・4.8節）、
                            src/margpa_runtime_llm/modules/conversation/
                            contracts.py・public.py・application/
                            conversation_generation.py、
                            tests/unit/conversation/
                            test_conversation_generation.py、
                            frontend/src/types.ts、frontend/src/App.tsx、
                            frontend/src/components/SettingsPanel.tsx、
                            frontend/src/components/SettingsModal/
                            SettingsModal.test.tsx、
                            frontend/src/i18n/translations.ts（第4.9節）、
                            frontend/src/lib/safeMarkdown.tsx・
                            safeMarkdown.test.tsx（第4.10節、再修正）。
                            本File自体は直接編集（同一Session内の連続
                            作業のため、新規後継Fileは作成せず）。
Validation                : N/A（Tracker文書自体）。第4.7〜4.10節記載の
                            作業そのものはBackend pytest／Frontend
                            Vitest／ESLint／tsc／Build／実Browser確認済み。
Open Current Blocker      : NONE
Controller-owned Next Work: 第3節の各予約Task Trigger成立を待つ。
Exact Next Route          : ユーザーの次の判断待ち。
```
