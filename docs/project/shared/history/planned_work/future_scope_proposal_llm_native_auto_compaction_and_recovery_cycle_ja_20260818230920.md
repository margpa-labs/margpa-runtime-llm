# 将来Scope提案 — LLM Native自動Context圧縮・自動復旧Cycle機能

```yaml
document_id: future_scope_proposal_llm_native_auto_compaction_and_recovery_cycle_20260818230920
status: reservation_not_started
phase: phase_3_candidate
subphase: null
from: ユーザー（原案）／Claude側設計統括者役（まとめ直し）
to: プロジェクト責任者兼設計統括者役（Codex）
role: design_governor
created_at: 2026-08-18 23:09:20 JST
language: ja
purpose: |
  ユーザーが提示した将来Feature構想（本Runtime＝MARGPA自身が生成する
  LLMに、Claude Code・GPT系Agent Harness等が既に備えている「Context
  Window圧縮→復旧」の自動Cycleに相当する機能を持たせる）を、Phase 3
  着手判断のInputとして記録する。ユーザー明示指示：「別件で、それ
  終わったらでいいけど、このLLMに自動コンテキスト圧縮と自動解凍
  （要するにclaudeやgptとかみたいなやつ）の機能をつけたいって話しを
  覚えてる？出せる範囲でいいので、予約枠のとこにdocsとして書いておいて」。
  本Docは実装着手を意味しない。
authorization: |
  ユーザー指示（2026-08-18）。history/planned_work/以下への新規
  Append-only File作成であり、Claude側設計統括者役の無許可書込み
  範囲内（運用メモ第3.11節）。
related:
  - future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021
    （第3節「既存提案との関係」参照。本Docは、同Docが対象とする
    「認識」「圧縮実行判断」の先に位置する、圧縮後の「復旧（解凍）」
    側を主対象とする）
  - future_scope_proposal_context_observatory_ja_20260817234734
created: Claude Code
```

## 0. 位置づけ（重要）

**本Docは提案・記録のみであり、実装は一切未着手・未着手予定。** 技術的実現可能性の検証、実現時期の判断は、いずれもPhase 3着手判断時にあらためて行う前提である。

## 1. 背景・要旨

本Session（Claude側設計統括者役によるCross-provider PoC）自体が、Context Window圧縮（Compaction）と、それに続く復旧（Recovery）を、Session内で繰り返し手動運用してきた。具体的には、Compaction直前に最新のCurrent Operational State Index・Recovery Indexを作成し、対象Fileの内容Hashを記録した上でCompactionを実行し、直後にOperating Rules・Current State・Recovery Indexを明示的に再読込し、Hash比較によって内容保持を検証する、という一連の手順である（[claude_side_design_governor_operating_notes_ja.md](../../task_roles/claude_side_design_governor_operating_notes_ja.md)第1節・第3.13節、および本Folder配下のCompaction Recovery関連Evidence群を参照）。

ユーザーは、この運用（Claude CodeというHarnessが本Session自体に対して提供している、圧縮と復旧のCycle）に相当する機能を、本Project（MARGPA）が開発しているRuntime自体が生成するLLM対話にも持たせたい、という将来構想を提示した。すなわち、「LLM側のContext Windowが閾値に達したら自動的に要約・圧縮し、その後の対話継続時には自動的に必要な情報を復元する」という、Claude・GPT系AgentがHarness側で既に備えている振る舞いを、MARGPA Runtime自身の機能として組み込みたい、という趣旨である。

## 2. 提案内容

### 2.1 自動Context圧縮（既存提案との重複部分）

LLMが自らのContext Window使用状況を認識し、あらかじめ定められた閾値に達した時点で、対話履歴を要約・圧縮する機能。この部分は、[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)第2.1節（認識）・第2.2節（閾値ベースSelf-triggered Compaction）が既に対象としている範囲であり、本Docはそれを重複して再提案するものではない。

### 2.2 自動復旧（解凍）——本Docが追加する範囲

圧縮後の対話継続時に、LLM自身（またはRuntime側の補助機構）が、圧縮前の対話で確立していた文脈・状態を、人手の介在なしに自動的に復元する機能。既存提案（第2.1節・第2.2節）は「認識」と「圧縮実行の判断」を主眼としており、圧縮後にどのように文脈を復元するかという「復旧（解凍）」側の設計には踏み込んでいない。本Docは、この復旧側を明示的な提案範囲として追加する。

本Session自体の手動運用（第1節参照）は、この「復旧」が具体的に何を必要とするかを示す、実地の参考事例となる。要約された状態から会話を再開する際、少なくとも次の要素が必要であることが、本Session内の反復運用から経験的に確認されている。

```text
- 直前までの作業状態を要約した最新Snapshot（本Session：Current
  Operational State Index相当）
- 継続に必要な最小限の背景・規則情報（本Session：Operating Rules相当）
- 圧縮前後で内容が保持されたことの検証手段（本Session：Hash比較相当）
```

MARGPA Runtime自身にこの機能を持たせる場合、これらに相当する仕組み（要約Snapshotの自動生成・保存、対話再開時の自動読込、圧縮前後の一貫性検証等）を、Runtime側でどう実現するかが、技術的な検討課題になると見込まれる。

## 3. 既存提案との関係

[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)は、「認識」（第2.1節）と「閾値ベースの圧縮実行判断」（第2.2節）を対象とし、圧縮後の復旧側は対象外としていた。本Docは、その続きに位置する「復旧（解凍）」側を主対象とする、補完的な提案である。両Docを合わせることで、「認識→圧縮判断→圧縮実行→復旧」という一連のCycle全体が、将来Scope提案として揃う。

[future_scope_proposal_context_observatory_ja_20260817234734.md](future_scope_proposal_context_observatory_ja_20260817234734.md)は、主に対話者（ユーザー）向けの可視化・申告機能を対象としており、本Docが扱う自動復旧Mechanism自体とは別Scopeである。

## 4. 実現時期についての見通し

ユーザーは本構想を「それ（Phase 2-E-I I-6関連のDocs作成）が終わったらでいい」という、緊急性のないTimingで提示した。関連提案（第2.1節・第2.2節相当、[future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md](future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md)第4節）に対するユーザー自身の既存の見立て——「たぶん今は作れないよな。Agent実装とかその辺のPhaseにならないと」——は、本Docが追加する「自動復旧」側についても同様に当てはまると考えられる。特に、対話再開時に人手を介さず自動的に文脈を復元する仕組みは、Agent Runtime的な基盤（自動Trigger、自動Snapshot読込等）を前提とする可能性が高い。

## 5. Status

```text
Current Point            : ユーザー構想（自動圧縮＋自動復旧）のうち、
                            自動圧縮側は既存提案（2026-08-18 16:30:21
                            JST作成）で記録済み。本Docで、未記録だった
                            自動復旧側を補完し、提案を記録・まとめ直した。
Files Created／Modified   : 本Fileのみ（新規作成）。既存提案Docは
                            変更していない（History上書き禁止原則）。
Validation                : N/A（提案記録）
Open Current Blocker      : NONE（Blockerではなく、Phase 3着手判断時の
                            検討候補という位置づけ）
Controller-owned Next Work: Phase 3の内容・優先順位をCodex側・ユーザー
                            側で判断する際、本Docと
                            future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_ja_20260818163021.md
                            を合わせて候補として参照する。
Exact Next Route          : 本DocはRead-only参照材料として保持。
                            Claude側設計統括者役から能動的に着手・
                            提案することはない（Phase 3自体がまだ
                            開始していないため）。
```
