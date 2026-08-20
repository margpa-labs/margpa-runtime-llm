# Auto-Compaction Recovery Cycle 7・RAG Pattern 2未決着 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_auto_compaction_recovery_cycle_7_and_rag_pattern2_open_question_recovery_index_20260819182942
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-19 18:29:42 JST
language: ja
purpose: |
  前回Recovery Index
  [claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md]
  （以下「前回Index」、2026-08-19 18:10:56 JST作成）以降に発生した、
  通常運用でのAuto-Compaction（Context使用率84%到達を契機とする自動発動）
  への復旧、およびRAG Pattern 2の設計方針が未決着のまま継続している状態を
  対象とした、続編Index。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** 第1節Step 2で、[claude_side_long_running_automation_companion_ja.md](../../../../shared/task_roles/claude_side_long_running_automation_companion_ja.md)（長期戦運用Companion）の`long_running_mode_active`フラグを確認する指示があります——**本Time点では`false`（非Active）です。**

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止。

## 1. 前回Indexとの関係

[claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md](claude_long_running_companion_established_and_rag_fix_pre_work_recovery_index_ja_20260819181056.md)（18:10:56作成）は、長期戦運用Companion確立と、Documentation RAG既知課題2件の根本原因調査完了までを対象としていた。同Index作成直後、ユーザーより次の実装指示が示されていた：「top_k=4を無難な範囲で引き上げる。§3.3・§3.7 Pattern 1・Pattern 2の両方（実質的に3事象）へ対応する。」

本Docは、それ以降（18:10:56〜18:29:42、約19分）に行われた作業を対象とする。この間、`top_k`引き上げ実装、Pattern 2修正設計に向けた実測調査、そして本題であるAuto-Compaction発生・通常運用でのRecoveryを行った。

## 2. 前回Index以降の作業内容

### 2.1 `top_k`引き上げ実装（完了）

`config/feature_profiles/local_documentation_rag.toml`・`lightning_public_documentation_rag.toml`の両方で、`top_k = 4` → `top_k = 8`へ変更した。既存Testが実Config値へ依存していないことをGrepで確認済み（`tests/unit/runtime/test_lightning_basic_preview_service.py`・`tests/unit/documentation_rag/test_lexical_retrieval.py`の`top_k`関連記述は、埋め込みFixtureまたは明示引数であり、実Config File読み取りに依存しない）。

### 2.2 RAG Pattern 2修正設計に向けた実測調査（完了、ただし方針は未決着）

実際のDocumentation RAG Compositionを用いた3本のScratchpad Probe Scriptにより、複数のQueryに対するBM25 Score・Score内訳・`identifier_subject_count`を実測した。

**主要な知見**：Score絶対値・Heading／Body／Exact-phrase内訳・`identifier_subject_count`のいずれの信号も、単独では「本来RAGが答えるべき正当な質問」と「無関係な質問」を確実に分離できない。特に、正当な広範質問「このProjectの目的は何ですか？」（Score 50.2）と、無関係な質問「リポビタンDの成分は？」（Score 48.5）がほぼ同点だった一方、他の無関係質問（天気・カレーレシピ）はScore 6〜19と明確に低かった——単純なScore閾値では、一方を通せば他方も通り、一方を弾けば他方も弾かれる状態にある。

この知見はユーザーへ報告済み。原因は、日本語Tokenizerが形態素解析ではなく文字N-gramを用いているため、文法的に自然な文であれば話題に関係なくCorpus内Headingとの偶然のN-gram一致が一定量発生することにあると推定される。**「無難な範囲のTuning」では確実な解決に至らないという結論に至り、ユーザーへ、(a) 部分的Mitigationを試みるか、(b) `RAG丸々改善Phase`（§3.3・§3.7双方の既存Trigger）まで見送るか、の判断を仰いだ。本Doc作成時点で、ユーザーからの回答はまだ無い。**

### 2.3 Auto-Compaction発生・通常運用でのRecovery（完了）

Context使用率84%到達时点で、ユーザーより「もうすぐAuto-Compactionくる、いつも通りに復旧してくれ、Manualじゃなくて Autoだからエビデンスは残すように」との指示があった。運用メモ第1節の復旧手順（本文再読込→長期戦Companion Flag確認→Phase Index／Recovery Index確認→必要Evidence個別参照）を実施し、成功した。詳細は[claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md](../../../../shared/history/automation/claude_auto_compaction_recovery_drill_cycle_7_ja_20260819182942.md)。Hash Manifest・運用メモのCompaction Recovery成功回数を6→7へ更新済み（[claude_compaction_recovery_hash_manifest_ja.md](../../../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)）。

本Cycleは、過去6回全てがManual Compaction（`/compact`）を対象としていたのに対し、**初めてAuto Compactionを対象としたRecovery Drillである**。Before Hashを事前取得できなかったため、After Hash（Best-effort）＋後継File非存在確認＋再読込内容と会話Summaryとの一致確認、という補助的Evidenceの組み合わせで検証した（詳細は上記Evidence Doc第4節）。

## 3. 現在の状態（2026-08-19 18:29時点）

**Auto-Compaction Recoveryは成功。長期戦運用Companion体制は非Active（`long_running_mode_active: false`）のまま。`top_k`引き上げは完了。§3.3・§3.7 Pattern 1は、Subject Coverage保証機構という共通原因の理解までは完了しているが、実装（コード変更）自体はまだ着手していない。§3.7 Pattern 2は、単純なScore閾値では確実な解決に至らないことが実測で判明し、方針判断をユーザーへ委ねた状態で応答待ちである。**

## 4. Status

```text
Current Point            : Auto-Compaction Recovery（Cycle 7）成功。top_k
                            引き上げ完了。§3.3／§3.7 Pattern 1の実装（コード
                            変更）は未着手。§3.7 Pattern 2は方針判断待ち
                            （ユーザー回答待ち、本Doc作成時点で未回答）。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : §3.7 Pattern 2の修正方針（部分的Mitigationか
                            RAG丸々改善Phaseへの見送りか）——ユーザー判断待ち。
Controller-owned Next Work: ユーザーからのPattern 2方針回答を待ち、回答に
                            応じて§3.3／§3.7 Pattern 1・Pattern 2の実装へ
                            着手する。
Exact Next Route          : ユーザー応答待ち。応答後、実装Phaseへ移行。
```
