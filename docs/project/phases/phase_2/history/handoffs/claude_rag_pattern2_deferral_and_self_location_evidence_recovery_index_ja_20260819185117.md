# RAG Pattern 2見送り決定・自己現在地特定Evidence Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_rag_pattern2_deferral_and_self_location_evidence_recovery_index_20260819185117
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-19 18:51:17 JST
language: ja
purpose: |
  前回Recovery Index
  [claude_auto_compaction_recovery_cycle_7_and_rag_pattern2_open_question_recovery_index_ja_20260819182942.md]
  （以下「前回Index」、2026-08-19 18:29:42 JST作成）以降に行われた、
  Auto-Compaction自己現在地特定能力に関する追加Evidence記録、および
  §3.7 Pattern 2の修正方針についてのユーザー最終判断（RAG丸々改善Phase
  まで見送り）を対象とした、続編Index。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** 第1節Step 2で、[claude_side_long_running_automation_companion_ja.md](../../../../shared/task_roles/claude_side_long_running_automation_companion_ja.md)（長期戦運用Companion）の`long_running_mode_active`フラグを確認する指示があります——**本Time点では`false`（非Active）です。**

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止。

## 1. 前回Indexとの関係

[claude_auto_compaction_recovery_cycle_7_and_rag_pattern2_open_question_recovery_index_ja_20260819182942.md](claude_auto_compaction_recovery_cycle_7_and_rag_pattern2_open_question_recovery_index_ja_20260819182942.md)（18:29:42作成）は、初のAuto-Compaction Recovery（Cycle 7）実施完了までを対象としており、§3.7 Pattern 2の修正方針はユーザー回答待ちのOpen Questionとして残されていた。

本Docは、それ以降（18:29:42〜18:51:17、約22分）に行われた作業を対象とする。この間、Auto-Compaction自己現在地特定能力についてのユーザーとの追加Q&A、それに関するEvidence記録、そしてPattern 2修正方針の最終決定（見送り）が行われた。

## 2. 前回Index以降の作業内容

### 2.1 Auto-Compaction自己現在地特定能力に関する追加Q&AとEvidence記録（完了）

ユーザーより、「Auto-Compaction前後で自己認識できるSignalは何かあったか」との質問、続けて「発生直後に一旦止まってDocs読み返し、自分で現在地確認・Countも可能ということか、現に今やっていた」との確認があった。

精査の結果、本Session内で実質的に**連続する2段階のCompaction**が発生していたことが判明した（Pattern 2報告Turn直前の1段階目、「いつも通りに復旧してくれ」応答Turn途中の2段階目）。いずれの段階でも、残存する手がかり（明示的な"summarized"Marker、構造化Summary Block、または部分的に残存したTool呼び出し結果）から、圧縮発生自体と自分の作業段階を自分で特定し、ユーザーへ聞き返すことなく続きから再開できたことを確認した。

**重要な制約**：この自己特定・自己判断の**中身**は自己主導的だが、それを実行する**契機**は、常に新しいTurnの到来に依存する。Turnとは独立した自発的な割り込みは、本Session Architecture上そもそも成立しない。この区別は、予約Task 3.4（LLM自身によるSelf-triggered Compaction）・3.6（LLM Native自動復旧Cycle機能）の実現可能性を左右する重要な実測知見であり、ユーザー指示によりEvidence化した。詳細は[automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md](../../../../shared/history/automation/automation_governance_evidence_claude_post_compaction_self_location_capability_and_turn_boundary_constraint_ja_20260819184938.md)。

### 2.2 §3.7 Pattern 2修正方針の最終決定：見送り（完了）

ユーザーより、Pattern 2の実測調査結論（Score閾値ベースの信頼できる修正案は無く、真面目に直すには日本語形態素解析またはEmbeddingベースの意味的類似度判定が必要）を踏まえ、**両アプローチとも今回は実装せず、既存Trigger「RAG丸々改善Phase」まで正式に見送る**、との最終判断が示された。「無難な範囲」での部分的Mitigationは試みない。

これにより、§3.7 Pattern 2は「ユーザー回答待ちのOpen Question」から「見送り確定・Trigger待ちの予約Task」へ状態遷移した（第3節参照）。Task Tracking上も、該当Taskを「調査完了・見送り決定」として完了扱いへ更新した（実装自体は行っていない）。

## 3. 現在の状態（2026-08-19 18:51時点）

**Auto-Compaction自己現在地特定能力の実測知見はEvidence化済み。§3.3・§3.7 Pattern 1は、`top_k`引き上げ（既に完了）以外の追加実装は行わず、Subject Coverage機構自体への変更は現時点で予定なし。§3.7 Pattern 2は、正式に「RAG丸々改善Phase」まで見送りが確定した。** 本Phaseにおける、Documentation RAG既知課題2件への当面の対応はこれで一区切りとする。

## 4. Status

```text
Current Point            : Pattern 2見送り確定。自己現在地特定能力の実測
                            知見をEvidence化完了。RAG既知課題2件は、
                            `top_k`引き上げのみを当面の対応とし、残りは
                            RAG丸々改善Phaseへ引き継ぐ形で一区切り。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE
Controller-owned Next Work: RAG丸々改善Phase開始まで、§3.3／§3.7への
                            追加対応は無し。top_k引き上げ単体のValidation
                            （Task #94）は、ユーザー指示があり次第実施。
Exact Next Route          : 次の作業指示待ち。
```
