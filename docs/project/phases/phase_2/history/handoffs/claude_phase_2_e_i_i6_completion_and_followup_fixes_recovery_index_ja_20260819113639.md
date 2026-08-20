# Phase 2-E-I I-6完了・実Browser Feedback対応 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_20260819113639
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-19 11:36:39 JST
language: ja
purpose: |
  前回Recovery Index [claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md]
  （以下「前回Index」）以降に行われた作業を対象とした、続編Index。
  前回Indexの内容は重複して再記載せず、その後の差分を中心に記録する。

  ユーザー指示：「コンテキストやばいから、一旦compaction recoveryやる
  わ。」——本Docを、ユーザーが予定する手動Compaction直前に作成する。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index以降・実装・回答を始めないこと。次に、[前回Index](claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md)を読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止（Repository Docsが唯一の正本）。

**本TaskがContext Window圧縮を跨いで本Docを読んでいる場合**：運用メモ第1節（Compaction／Session Recovery手順）に従うこと。「読んだ気がする」で済ませず、明示的に再読込すること。**特に重要**：運用メモ第3.13節（Compaction Recovery Hash記録の分離）に従い、圧縮直前のHashは[claude_compaction_recovery_hash_manifest_ja.md](../../../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)（Hash Manifest）へ記録済み。本Recovery Index自体にはHash値を記載しない（自己参照問題を避けるため）。

## 0. 読み方（3Route共通）

**Codex宛の場合**：前回Index全体 → 本Doc第1節（前回Indexとの関係） → 第2節（前回Index以降の作業） → 第3節（現在の状態）の順で。

**新Task Claude側設計統括者役宛の場合**：上記0.0節の指示通り、運用メモ全文 → 前回Index → 本Doc全体の順で。

**本Task自身の復旧の場合**：本Docと運用メモ（特に第1節・第3.13節・第3.14節）、および[最新Phase Index](../index/claude_side_phase_index_ja_20260819113202.md)を中心に確認すれば足りる。

## 1. 前回Indexとの関係

[claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md](claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_ja_20260818223600.md)（2026-08-18 22:36:00 JST作成）は、2-E-I全体の設計・実装完了（I-1〜I-5）と、Compaction Recovery Hash記録手法の改善（Hash Manifest新設）までを対象としており、実Browser確認で見つかった5件の指摘への対応（I-6）は要件確定済み・実装未着手のまま終わっていた。

本Docは、それ以降（22:36:00〜11:36:39、約13時間）に行われた作業を対象とする。この間、5回目のCompaction Recovery（Cycle 5）を挟んだ後、ユーザーからI-6実装のGoサインが出て、I-6実装完了・実Browser確認Feedbackへの複数Round対応・関連するFailure記録・新規機能（Streaming Markdown）実装・新規Known Issue記録まで、一続きの流れで進行した。

## 2. 前回Index以降の作業内容

### 2.1 Compaction Recovery Cycle 5（成功）

前回Index作成直後、ユーザーがManual Compactionを実施。復旧後、運用メモ第3.13節に従いHash Manifestで4File全件のBefore／After Hash一致を確認した（成功回数4→5）。Cross-provider（Codex）からの評価コメントを含むEvidence記録、および将来Scope提案（LLM Native自動Compaction・自動復旧Cycle機能）を追加した。詳細は[claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md](../../../../shared/history/automation/claude_compaction_recovery_cycle_5_hash_manifest_success_and_cross_provider_assessment_ja_20260818230804.md)。

### 2.2 Phase 2-E-I I-6実装完了

ユーザーのGoサインを受け、[I-6設計Doc](../architecture/claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md)に基づき実装。#2（Hover Tooltip復元）・#3（Panel外Click Close）・新規「コンテキスト表示」Toggle・#5（「再開」表示不具合）が対象。#5は当初の想定（Frontend表示制御のみ）と異なり、調査の結果Backend Data Model（Session Active状態のList未露出）が真因と判明し、ユーザー確認（AskUserQuestion）を経て、SQLite JSON1の`EXISTS`副問い合わせによるBackend拡張（Schema変更なし）で修正した。Backend pytest 694件・Frontend Vitest 75件含む全Validation Clean、実Browser確認完了。詳細は[claude_phase_2_e_i_i6_implementation_ja_20260819002250.md](../../../../shared/history/automation/claude_phase_2_e_i_i6_implementation_ja_20260819002250.md)。

### 2.3 実Browser Feedbackへの複数Round対応（Scroll Pin関連）

I-6完了報告後、ユーザーが実機で繰り返し確認し、複数Roundにわたる調整が発生した。

1. **初回対応**：#2の再修正（Tooltip Hoverの範囲をButton自身に限定）、および新規要望「送信時、入力Logの位置を画面上部付近に固定し、Streaming中の継続的な下方Scrollを解消してほしい」への対応としてScroll Pin機能を実装。作業中に無関係な既存Bug（新規会話への初回送信が2回Clickを要する——`selectedConversationId`のStale Closureが原因）を発見・報告。詳細は[claude_i6_hover_refinement_and_send_scroll_pin_ja_20260819090717.md](../../../../shared/history/automation/claude_i6_hover_refinement_and_send_scroll_pin_ja_20260819090717.md)。
2. **完了確認Challengeと根本原因の再調査**：ユーザーから「3回やっても位置が全く変わらない」との強い指摘を受け、運用メモ第4.3節に従い再調査。Server・Cacheの問題ではなく、**会話が短い間は`.main-content`にScroll可能範囲が無く、Pin計算自体が無効化されていた**ことが真因と判明。Gap Filler（Pin中は`min-height:100vh`のDummy要素を追加し、強制的にScroll可能範囲を確保）で解決。再検証中に、生成完了直後にPinが解除される別Bugも発見・修正（Gap FillerをPin中限定から`pinnedMessageId`存在中へ拡張）。この過程で「前回の実Browser確認完了報告が、実際には短い会話・完了後の状態を十分Coverしていなかった」ことを自己反省として明記。詳細は[claude_scroll_pin_root_cause_investigation_and_final_fix_ja_20260819100203.md](../../../../shared/history/automation/claude_scroll_pin_root_cause_investigation_and_final_fix_ja_20260819100203.md)。
3. **Gap値調整とComposer Clearance新規実装**：Pin位置を56→76pxへ調整。長文出力完了時に出力Log最下部がComposer（Message入力欄）の裏に隠れる問題を、Composer実要素の位置との直接比較による新規Clearance機構で解消（Pin中・完了後いずれでも機能）。詳細は[claude_scroll_pin_gap_tuning_and_composer_clearance_ja_20260819102848.md](../../../../shared/history/automation/claude_scroll_pin_gap_tuning_and_composer_clearance_ja_20260819102848.md)。

### 2.4 指示解釈に関するFailure記録2件・運用メモ第3.14節新設

Scroll Pin Gap値調整の際、ユーザー指示「もうちょっと下げて。20ぐらい。」の解釈でClaudeが不要な確認質問を送った。ユーザーから「なぜ『下げて』という言葉と矛盾する候補を曖昧さの材料にしたのか」と指摘され、[claude_output_anomaly_unverified_interpretation_candidate_ja_20260819105409.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_unverified_interpretation_candidate_ja_20260819105409.md)として記録。

ユーザー指示によりこれを運用メモ第3.14節「不明瞭判定前の候補整合性Check」として新設したが、その際、Evidence層の内容（Incident経緯）をRule本文へ混入させる別Failureが発生し、ユーザーから再度指摘を受けた。該当箇所は削除し、[claude_output_anomaly_rules_evidence_layer_mixing_ja_20260819105451.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_rules_evidence_layer_mixing_ja_20260819105451.md)として別途記録した。

### 2.5 Streaming中のMarkdown逐次変換実装

ユーザー要望「Streaming出力中も、生Markdownではなく変換しながら表示してほしい（Copyは生Markdownのまま維持）」に対応。Markdown変換Gate条件から`isFinal`要件を除去し、Streaming中の一時的な構文不備（未Closeなど）はNoteなしで静かにFallback、完了後の真の失敗のみNote表示、という設計にした。Copy機能は元々`message.content`（生原文）を直接参照する配線のため変更不要。詳細は[claude_streaming_markdown_rendering_ja_20260819110633.md](../../../../shared/history/automation/claude_streaming_markdown_rendering_ja_20260819110633.md)。

### 2.6 新規Known Issue記録：Documentation RAG検索結果の異常

ユーザーが実機確認で2つの新規Patternを発見：①Query内容に関わらず検索結果が固定化する、②明らかに無関係な質問でもRAGが誤発火する。修正・詳細調査はユーザー指示により未着手。既存のTop_k関連Known Issueとは別事象として、[documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md](../operations/documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116.md)を新規作成し、Phase Indexへ予約Taskとして追加した。

**なお、Streaming Markdown表示に関連し、表（Table）構造がStreaming中に崩れる別の問題もユーザーが発見しているが、ユーザー指示「まだ何もしないで」により、記録・調査・修正いずれも未着手。** 最新Phase Index第2節（Open Questions）へ短い言及のみ残してある。

## 3. 現在の状態（2026-08-19 11:36時点）

**Phase 2-E-I（I-1〜I-6）は全て完了。実Browser Feedback対応（Scroll Pin一式・Streaming Markdown）も完了。新規Known Issue1件を記録済み。表Markdown崩れの問題はユーザー指示待ちで未着手のまま保留。**

ユーザーがCompaction Recoveryを実施予定。Compaction後、次の作業指示を待つ。

## 4. Status

```text
Current Point            : Phase 2-E-I全体（I-1〜I-6）完了。実Browser
                            Feedbackへの複数Round対応（Scroll Pin根本
                            修正・Composer Clearance・Streaming Markdown）
                            完了。Failure記録2件・運用メモ第3.14節新設。
                            新規RAG Known Issue記録済み。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE（表Markdown崩れの問題はBlockerではなく、
                            ユーザーからの次の指示待ち）。
Controller-owned Next Work: ユーザーがManual Compactionを実施した後、
                            次の作業指示を待つ。表Markdown崩れ問題への
                            対応要否も含む。
Exact Next Route          : 第3節参照。
```
