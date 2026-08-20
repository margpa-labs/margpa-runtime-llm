# Phase 2-E-I実機Feedback一式完了・Phase 3引き継ぎ準備 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_20260819144637
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-19 14:46:37 JST
language: ja
purpose: |
  前回Recovery Index
  [claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md]
  （以下「前回Index」、2026-08-19 11:36:39 JST作成）以降に行われた作業を
  対象とした、続編Index。前回Indexの内容は重複して再記載せず、その後の
  差分を中心に記録する。

  ユーザー指示：「Phase 3の実装部分はまるごと通してClaudeに一気に作って
  もらう予定。Automation／Auto-Compaction Recovery（長期戦）の実験も
  兼ねて。って事で、最新のindex 2個作っといて。」——Codex復活（2026-08-20
  予定）を翌日に控えた時点での、区切りとして作成する。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index以降・実装・回答を始めないこと。次に、[前回Index](claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md)を読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止（Repository Docsが唯一の正本）。

**本TaskがContext Window圧縮を跨いで本Docを読んでいる場合**：運用メモ第1節（Compaction／Session Recovery手順）に従うこと。「読んだ気がする」で済ませず、明示的に再読込すること。

## 0. 読み方（3Route共通）

**Codex宛の場合**：前回Index全体 → 本Doc第1節（前回Indexとの関係） → 第2節（前回Index以降の作業） → 第3節（現在の状態）の順で。特に第2.7節（Phase 3引き継ぎ計画）を重点的に確認されたい。

**新Task Claude側設計統括者役宛の場合**：上記0.0節の指示通り、運用メモ全文 → 前回Index → 本Doc全体の順で。

**本Task自身の復旧の場合**：本Docと運用メモ（特に第1節・第3.13節・第3.14節）、および[最新Phase Index](../index/claude_side_phase_index_ja_20260819144637.md)を中心に確認すれば足りる。

## 1. 前回Indexとの関係

[claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md](claude_phase_2_e_i_i6_completion_and_followup_fixes_recovery_index_ja_20260819113639.md)（2026-08-19 11:36:39 JST作成）は、Phase 2-E-I I-6完了・実Browser Feedback対応（Scroll Pin一式・Streaming Markdown・新規RAG Known Issue記録）までを対象としていた。

本Docは、それ以降（11:36:39〜14:46:37、約3時間10分）に行われた作業を対象とする。この間、6回目のCompaction Recovery（Cycle 6）を挟んだ後、ユーザーから4件の追加実機Feedback（Markdown表崩れ・表Message横幅拡張・表現重視モード・表Cell内`<br>`および箇条書きMarker残留）への対応を完了し、続けてPhase 3（次期Sub-phase）実装計画の共有を受けた。

## 2. 前回Index以降の作業内容

### 2.1 Compaction Recovery Cycle 6（成功）

前回Index作成直後、ユーザーがManual Compactionを実施。復旧後、運用メモ第1節に従い3Docs（運用メモ・最新Phase Index・前回Index）を明示的に再読込し、Hash Manifest（[claude_compaction_recovery_hash_manifest_ja.md](../../../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)）で3File全件のBefore／After Hash一致を確認した（成功回数5→6）。

### 2.2 Markdown表（Table）のStreaming中崩れ修正

前回Indexで「ユーザー指示待ちで未着手」としていた課題に、ユーザーからの明示的なGoサイン（「表Markdown崩れの方に着手してくれ」）を受けて着手。独自Markdown Parser（`safeMarkdown.tsx`）にGFM Pipe Table対応（Header／Delimiter行検出、Escaped Pipe、Alignment、Streaming途中の非例外Fallback）を新規実装した。根本原因は、Table行が既存の`paragraph`Fallbackへ落ち、連結された生改行がBrowserの空白折り畳みで失われていたこと。実LLM出力での検証中に、Delimiter行の二重Pipe（実際に観測されたModel出力Artifact）に対する追加耐性修正も実施した。詳細は[claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md](../../../../shared/history/automation/claude_streaming_markdown_table_rendering_fix_ja_20260819120800.md)。

### 2.3 表を含むMessageの横幅拡張（message-wide）

ユーザー要望「通常時の横幅の最大は変えず、表を使う時だけ最大1.5倍ぐらいに広げたい」に対応。通常Messageの`max-width: 57%`は変更せず、Markdown表を含むMessageのみ`.message-wide`（`max-width: 85%`）を付与する仕組みを実装。`safeMarkdown.tsx`を`parseSafeMarkdown`＋新規`renderSafeMarkdownBlocks`／`containsTable`へ分離し、二重Parseを回避した。詳細は[claude_message_wide_bubble_for_table_content_ja_20260819123330.md](../../../../shared/history/automation/claude_message_wide_bubble_for_table_content_ja_20260819123330.md)。

### 2.4 表現重視モード（Style限定Prompt Injection）

ユーザー要望「Qwenの出力、推論そのものは変えずに、ノリ・テンション・草生やし（www）・顔文字・絵文字・アイコン等の表現だけ変えたい。ただし素のQwenと見分けが付かなくなると困るので、表現重視モードとして設定の基本Categoryへ」に対応。既存の「Context使用率Prompt Injection」と同じ設計Pattern（専用Enum＋条件付きSYSTEM Message Injection）を踏襲し、推論・結論・事実内容は変えず表現のみを変化させるOpt-in Toggle（既定Disabled）を実装した。詳細は[claude_expressive_mode_style_only_prompt_injection_ja_20260819124942.md](../../../../shared/history/automation/claude_expressive_mode_style_only_prompt_injection_ja_20260819124942.md)。

### 2.5 表Cell内`<br>`混入・箇条書きMarker残留の修正（2件連続）

第2.3節の機能確認後、ユーザーが多列比較表で発見した2件の続報に対応。

1. **`<br>`混入**：「生HTMLを一切Renderしない」というSecurity方針上、GFM表Cellの改行に標準的に使われる`<br>`もText扱いされていたことが原因。属性を一切持ち得ない`<br>`・`<br/>`・`<br />`のみを認識する狭いExceptionを追加し、Security Invariantを保持したまま解消した。詳細は[claude_table_cell_br_line_break_fix_ja_20260819132416.md](../../../../shared/history/automation/claude_table_cell_br_line_break_fix_ja_20260819132416.md)。
2. **箇条書きMarker（`-`）残留**：`<br>`は消えたが、Marker文字`-`（例：「- 会話型LLM」）が残留していた続報。Block Level Listの検出が表Cell（`<br>`区切りの一枚岩文字列）には及ばないことが原因。`parseInline`へ「行頭にいるか」を追跡する状態を追加し、その位置の`-`／`*`／`+`をBullet文字「• 」へ置換した。詳細は[claude_table_cell_bullet_marker_fix_ja_20260819133331.md](../../../../shared/history/automation/claude_table_cell_bullet_marker_fix_ja_20260819133331.md)。

いずれも実LLM出力を用いた実Browser確認で、報告内容と同一の症状を再現させたうえで修正を確認している。

### 2.6 ユーザー自身の実機確認（第2.3節・第2.4節）

第2.3節（表Message横幅拡張）・第2.4節（表現重視モード）について、ユーザー自身の実機確認が完了した。表Message横幅拡張は「表だけ広がってる。直後簡単な質問に切り替えたら、ちゃんと元の最大幅に戻ってる」、表現重視モードは「OpenAIって何年から存在するんだっけ？」への回答をOFF／ON両方で提示され、事実内容（2015年設立という結論・年表）が同一のまま、ON時のみ絵文字・「www」・Casualな口調が付加されることを確認された。両件とも、対応する[最新Phase Index](../index/claude_side_phase_index_ja_20260819144637.md)第4.8節・第4.9節（前版）へユーザー確認済みとして追記済み。

第2.5節完了後、ユーザーから「一旦つけたいUI系は一通り完了でいいかな」との確認があり、今回のI-6実機Feedback対応Round全体（第2.2〜2.5節、および前回Index記載のScroll Pin一式・Streaming Markdown）が完了したことを相互確認した。

### 2.7 Phase 3引き継ぎ計画の共有

ユーザーより、`docs/public/roadmap_ja.md`（Codex管理、Claude側Read-only）第9節「Phase 3 — Audit, Evidence, and Generic Definition Infrastructure」の内容確認を依頼され、Read-onlyのまま全文を提示した。State`Planned`。Audit／Evidence基盤（Turn／Request／Run／Event Identity、JSONL Append-Only Log、SHA-512等）と、Generic Governance Definition Platform（`EmptyDefinitionProvider`、Definition Provider、Adapter Registry、Compiler Port等）を構築するPhaseであり、Governance Definition 0件でもRuntimeが正常動作するBaselineを維持しながら、任意のGovernance Definitionを安全に受け入れる拡張境界を作ることが主旨。

続けてユーザーより、次の計画が共有された。

- Codexプロジェクト責任者兼設計統括者役は2026-08-20（木）に復活予定。Phase 3の設計自体はCodexとユーザーが行う。
- 設計完了後、Phase 3の実装部分はまるごとClaude側設計統括者役が一気通貫で実装する予定。これは同時に、本Session中に確立してきたAutomation／Auto-Compaction Recovery機構（3Docs明示的再読込、Hash Manifest、Phase Index／Recovery Index succession等）の、長期戦（Long-running）実地検証を兼ねる。
- ユーザーより、Phase 3で使用予定のGovernance Definition群（`other/margpa-runtime-llm用_definitions_20260819.zip`、Project Root外・ユーザー管理領域）が提示され、Read-onlyで内容を確認した（Repositoryへは格納していない）。構成：
  - Core（1File内2件）：ARGD (Axiomatic Reasoning Governance Definition) v0.3.1、DAGD (Declarative AI Governance Definition) v0.4.4
  - Orchestration（1件）：CDOGD (Cross-Domain Orchestration Governance Definition) v0.1.0
  - Domain Extensions（14件、いずれもv0.1.0）：
    - Ordinary（10件）：AAGD、ACRGD、AIAGD、AIRGD、AISGD、DCAGD、DSGD、MPGD、OMRGD、PMOGD、SEGD
    - Decision Pipelines（3件）：SPPGD、DAAGD、SDAGD
    - Conditional Watchdogs（1件）：SDMRGD
- ユーザーより、今日2026-08-19（水）時点でClaude側Weekly Usage残量が約21%、2026-08-21（金）に復活する旨の共有があった。

この過程で、Claude側が習慣的にProvider Memory（`~/.claude/projects/.../memory/`）の`MEMORY.md`をReadしようとし（存在しなかったため即座に失敗、実際の書込みは発生していない）、ユーザーからその場で指摘を受けた。ユーザーの指摘通り、Provider MemoryではなくRepository側Index（本Docのような仕組み）を使うべき場面であったと確認し、以降このTurn内では書込みを行っていない。実害・実際のRule違反は発生していないが、運用メモ第2.6節の趣旨に照らした継続的な注意点として記録する。

Phase 3の詳細設計自体は未着手であり、本Docは設計着手前の状態を引き継ぐためのCheckpointである。

## 3. 現在の状態（2026-08-19 14:46時点）

**Phase 2-E-I（I-1〜I-6）、および実機Feedback対応一式（Scroll Pin・Composer Clearance・初回送信Bug・Streaming Markdown・Markdown表崩れ修正・表Message横幅拡張・表現重視モード・表Cell内`<br>`／箇条書きMarker修正）は、ユーザー確認込みで全て完了。**

Phase 3は、2026-08-20（木）のCodex復活を待って、Codexとユーザーによる設計から始まる。Claude側は、設計完了・引き継ぎを受けてから実装Phaseへ入る予定であり、現時点で先行着手すべき事項はない。

## 4. Status

```text
Current Point            : Phase 2-E-I実機Feedback対応一式が、ユーザー確認
                            込みで完了。Phase 3（Governance Definition
                            Platform）の実装をClaudeが一括担当する計画が
                            共有され、Automation／Auto-Compaction Recovery
                            長期実験も兼ねる予定であることを確認した。
                            設計はCodex復活（2026-08-20予定）後にCodexと
                            ユーザーが行う。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : NONE（Phase 3設計未着手はBlockerではなく、
                            Codex復活待ちの正常な順序待ち）。
Controller-owned Next Work: Codex復活・Phase 3設計完了・Claude側への
                            引き継ぎを待つ。
Exact Next Route          : 第3節参照。
```
