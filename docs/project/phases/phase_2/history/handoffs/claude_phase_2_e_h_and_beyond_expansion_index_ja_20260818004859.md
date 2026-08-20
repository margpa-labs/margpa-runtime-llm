# Phase 2-E-H以降 拡張作業Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_phase_2_e_h_and_beyond_expansion_index_20260818004859
status: index
phase: phase_2
subphase: phase_2_e_h_and_beyond
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-18 00:48:59 JST
language: ja
purpose: |
  前回作成した [claude_phase_2_e_expansion_index_ja_20260816165825.md]
  （以下「前回Index」）以降に行われた作業を対象とした、続編Index。
  前回Indexの内容は重複して再記載せず、前回Indexの内容を前提として、
  その後の差分を中心に記録する。3つの宛先（Codex復帰時、新Task
  Claude起動時、本Task自身がContext Window圧縮を跨いだ場合の復旧時）
  で共用する。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index以降・実装・回答を始めないこと。次に、[前回Index](claude_phase_2_e_expansion_index_ja_20260816165825.md)を読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止（Repository Docsが唯一の正本）。

**本TaskがContext Window圧縮を跨いで本Docを読んでいる場合**：上記と同様の手順（運用メモ全文の再読込→前回Index→本Doc）に従うこと。圧縮直後は、直前に読んでいたFileの一部しか自動的に再挿入されない場合がある（運用メモ第1節参照。2026-08-18に運用メモは複数回構造再編成されており、本Doc作成時点の「第9節」は、その後「第8節」を経て、現在「第1節」）。「読んだ気がする」で済ませず、明示的に再読込すること。

> **[2026-08-18追記]** 運用メモは同日、Rule専用への構造再編成を受けた（詳細：[automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md](../../../../shared/history/automation/automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md)）。本Doc内の節番号参照は、以後この追記により補正する。予約Task・Open Questionsは、運用メモから[claude_side_phase_index_ja_20260818121842.md](../index/claude_side_phase_index_ja_20260818121842.md)（Phase 2 Current Operational State Index、最新版）へ分離済みのため、本Doc第7節「現在Open・未着手」と合わせてそちらも確認すること。

## 0. 読み方（3Route共通）

**Codex宛の場合**：前回Index第1節（当初Scope完了）→前回Index第4節（旧Open項目）→本Doc第1節（前回Indexとの関係）→第2節（2-E-H完了報告）→第7節（現在Open）の順で。

**新Task Claude側設計統括者役宛の場合**：上記0.0節の指示通り、運用メモ全文→前回Index→本Doc全体の順で。

**本Task自身の復旧の場合**：本Docと運用メモ（特に第1節）、および[Phase 2 Current Operational State Index](../index/claude_side_phase_index_ja_20260818121842.md)（最新版）を中心に確認すれば足りる（前回Indexの内容は、既に会話履歴の中に残っている可能性が高いため、必要に応じて参照）。

## 1. 前回Indexとの関係

[claude_phase_2_e_expansion_index_ja_20260816165825.md](claude_phase_2_e_expansion_index_ja_20260816165825.md)は、当初Scope完了から2-E-B〜G（React/Vite移行・Sidebar化・Settings Modal化・CSS微調整5Round・Frontend設計能力自己評価）までを対象とした、統合Index兼Recovery文書である。本Docはその**続編**であり、前回Index作成（2026-08-16 16:58頃）以降の作業を対象とする。前回Indexの内容は、本Docでは再記載しない。

## 2. 2-E-H：完了報告

会話の「名前変更」「削除」機能。設計から実装・実機確認まで**完了済み**。

```text
設計Doc（Open Question全4問＋追加確認事項2件、いずれも確定済み）：
  docs/project/phases/phase_2/history/architecture/
    claude_phase_2_e_h_process_breakdown_design_ja_20260816173714.md

Completion Handoff：
  docs/project/phases/phase_2/history/handoffs/
    claude_phase_2_e_h_completion_handoff_ja_20260816193010.md

Automation Governance Evidence（Dialog 0件でのNon-stop完走、
2-E-D・E・F・G・Hの5 Sub-phase連続実績）：
  docs/project/shared/history/automation/
    automation_governance_evidence_phase_2_e_h_bypass_nonstop_cycle_ja_20260816193010.md
```

**実装内容の要点**：`ConversationState.DELETED`新設、`title`Fieldを`state`/`head_turn_id`と同じ「Domain Snapshot＋冗長SQL列」Patternで追加、SQLite Schema Migration（sqlite-2→sqlite-3、純追加）、Rename/Delete API・Route、List Default除外（`?state=deleted`で参照可）。Frontend：Sidebar Option MenuへRename（List内Inline編集）・Delete（確認Dialog付き）を追加。

**実機確認（ユーザー本人、2026-08-17〜18）**：Migration適用、名前変更・削除の実機動作、**再起動を跨いだ状態維持（Migration前から存在した既存会話の履歴保全を含む）**、Delete確認Dialogの実機表示——**すべて確認済み、問題なし**。

## 3. Context Window圧縮実験と、そこから確立した運用規則

2026-08-16、意図的にContext使用率を限界まで使い切り、実際にAuto-compactionが発動するかを検証する実験を実施した（96%→9%）。結果と、そこから発見した「圧縮直後は一部Fileしか自動再挿入されない」という非対称性は、[運用メモ第1節](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)に記録済み。関連Evidence：

```text
docs/project/shared/history/automation/
  automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md
```

この実験結果を受け、2-E-Hは新Task化せず、本Session内で引き続き完走した（実際に完走済み、第2節参照）。

**あわせて、[運用メモ](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)へ以下の新規則を確立した（第3.1・3.2節）**：

- 全てのDocsは研究・技術文書として書く（口語・絵文字・Slang・Nazuna Research以外の固有名詞をDocsへ持ち込まない）。
- Stable文書作成時は、重要な統治判断・状態遷移・Failure/Success・設計根拠について、意味を落とさないLossless水準で書く。

**新Task・Codexが今後Docsを作成する際は、この2つの規則を前提とすること。**

## 4. 将来Scope提案（Phase 3以降検討候補、実装未着手）

いずれもユーザー提示の構想を記録したのみで、実装は一切未着手。

```text
Temporal Authorityを持ったAgentic Runtime
（Time Provider／Scheduler／Tool／Agent Runtime／Evidence）：
  docs/project/shared/history/planned_work/
    future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md
  Triggerは「Codex復活」。

Context Observatory
（Context Window可視化Panel＋LLM自己申告＋Recovery Snapshot機構）：
  docs/project/shared/history/planned_work/
    future_scope_proposal_context_observatory_ja_20260817234734.md
  Phase 3候補、時期未確定。
```

## 5. 既知の課題（修正未着手）

```text
Documentation RAG「Subject Coverage不足」による自己引用Loop Bug：
  docs/project/phases/phase_2/history/operations/
    documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md
  RAG回答自体をCopyして送り返すと、送信Message内のFile Path風Token
  が過剰にSubject判定され、既定top_k（4）を必ず超えて機械的に失敗する。
  ユーザーの意向：「RAG丸々改善Phase」で対応予定、それまでは現状維持。
  修正着手前にBackup取得予定。
```

## 6. 現Frontend／Backend Architecture要点（前回Indexからの差分）

```text
Backend: STORAGE_SCHEMA_VERSION = sqlite-3（title列追加、Migration
         Step 2件登録済み）。ConversationState = ACTIVE／ARCHIVED／
         DELETEDの3値。
Frontend: ChatListItem.tsx に Rename（Inline編集）・Delete
         （confirm付き）を追加、ChatListAction = "resume"|"archive"|
         "unarchive"|"delete"。
Test: pytest 682 passed／3 deselected（前回Index時点664から増加）。
      npm test 69 passed（前回Index時点64から増加）。
```

他の構造（React/Vite基盤、CSS Custom Property Token化等）は前回Indexから無変更。

## 7. 現在Open・未着手（次にやること）

```text
- Documentation RAG改善：ユーザーの意向により、専用の改善Phaseで
  まとめて対応予定。個別修正は現時点で行わない。
- 第4節の将来Scope提案2件：いずれもTrigger未成立、着手判断待ち。
- 本Docの作成をもって、[Phase 2 Current Operational State Index第4.2節](../index/claude_side_phase_index_ja_20260818121842.md)の「Recovery Index再作成」
  予約Taskは実行済みとみなしてよい。
```

## 8. Status

```text
Current Point            : 2-E-H完了、実機確認完了。Context圧縮実験
                            完了・Docs化完了。将来Scope提案2件・既知の
                            課題1件を記録済み。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザーの次の判断（RAG改善Phaseの着手
                            時期、将来Scope提案の優先順位付け等）。
Exact Next Route          : 第7節参照。
```
