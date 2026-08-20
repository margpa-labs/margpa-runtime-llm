# 将来Scope提案 — LLM自身によるContext Window認識・閾値ベースSelf-triggered Compaction

```yaml
document_id: future_scope_proposal_llm_self_context_awareness_and_self_triggered_compaction_20260818163021
status: reservation_not_started
phase: phase_3_candidate
subphase: null
from: ユーザー（原案）／Claude側設計統括者役（まとめ直し）
to: プロジェクト責任者兼設計統括者役（Codex）
role: design_governor
created_at: 2026-08-18 16:30:21 JST
language: ja
purpose: |
  ユーザーが2026-08-18に提示した将来Feature構想（LLM自身が現在の
  Context Window使用状況を把握・認識できる機能、およびLLM自身が
  定めた閾値に基づき自らCompactionを実行できる機能）を、Phase 3
  着手判断のInputとして記録する。ユーザー明示指示：「もし技術的に
  可能そうであればPhase3の頭に...っての書いといてくれる？」——本Doc
  は実装着手を意味しない。
authorization: |
  ユーザー指示（2026-08-18）。history/planned_work/以下への新規
  Append-only File作成であり、Claude側設計統括者役の無許可書込み
  範囲内（運用メモ第3.11節）。
related:
  - future_scope_proposal_context_observatory_ja_20260817234734
    （第3節「既存提案との関係」参照。第3.2節「LLM自身による段階的な
    自己申告」と部分的に重なるが、本Docはその申告を技術的に可能に
    する認識機構自体、および自己判断によるCompaction実行という、
    より踏み込んだAgentic Actionを対象とする）
created: Claude Code
```

## 0. 位置づけ（重要）

**本Docは提案・記録のみであり、実装は一切未着手・未着手予定。** ユーザー自身が「たぶん今は作れないよな。Agent実装とかその辺のPhaseにならないと」と明言しており、実現時期・技術的実現可能性の両方について、Phase 3着手時点で改めて判断する前提である。本Docの役割は、その判断時に参照できるInput資料を残すことに限定される。

## 1. 背景・要旨

本Session内で、ユーザーから次の2点を直接尋ねられた。

1. Manual Compaction（`/compact`）を、Claude側設計統括者役が自分で起動できるか。
2. 現在のContext Window使用率を、Claude側設計統括者役が自分で確認できるか。

いずれも、回答は「できない」だった。`/compact`はCLI側のSlash Commandであり、Claude側が呼び出せるTool（Function）としては提供されていない。Context Window使用率についても、それを読み取るTool／APIは無く、Claude側設計統括者役は正確な数値を把握する手段を持たない。

この回答を受け、ユーザーは「じゃ出来るとすれば、例えば作業の1塊でキミが最新index作る様にしておいて、可能な限りAuto-Compactionが発生する手前で用意出来る様にするぐらいしか出来ないね。なら仕方ない」と、現状の制約を踏まえた運用（運用メモ第3.12節「Manual Compaction前のIndex最新性確認」）を確認した上で、本Docが対象とする将来Feature構想を提示した。

## 2. 提案内容

### 2.1 LLM自身によるContext Window認識機能

LLM（Claude側設計統括者役に限らず、本Runtime上で動作するLLM一般）が、現在のContext Window使用状況（使用量・残量・閾値までの距離等）を、自ら把握・認識できる機能。現状は、この情報はHarness側（CLI等）にのみ存在し、LLM側からは不可視である。

この機能が実現すれば、[future_scope_proposal_context_observatory_ja_20260817234734.md](future_scope_proposal_context_observatory_ja_20260817234734.md)第3.2節が提案する「LLM自身による段階的な自己申告」（使用率85%で申告、90%で提案、95%で予告、等）が、技術的に初めて可能になる。Context Observatory側の提案は、あくまで「LLMが申告する」という振る舞いの提案であり、その振る舞いを支える認識機構自体は、本Docで扱う。

### 2.2 LLM自身による閾値ベースのSelf-triggered Compaction

LLM自身が、あらかじめ定められた閾値（Configuration可能な値であり、LLMが任意のTimingで判断するものではない）に達した時点で、自らCompactionを実行できる機能。ユーザーの明示的な留保：**「もちろん好きなタイミングで、ではなく、閾値は決める」**——LLM側の裁量は、あくまで「定められた閾値に達したかどうかの判定」に限定され、閾値そのものの決定・変更はLLM側の裁量に含まれない。

この機能は、運用メモ第2.4節（Git Mutation禁止）・第2.6節（Provider Memory禁止）等、既存のAuthority境界の考え方と同様、**LLMに新たな裁量を無制限に与えるものではなく、明確な条件下でのみ許可される、限定的なAgentic Actionとして設計する**必要がある。

## 3. 既存提案との関係

[future_scope_proposal_context_observatory_ja_20260817234734.md](future_scope_proposal_context_observatory_ja_20260817234734.md)は、Context Windowの可視化・Recovery Snapshot生成を、主に**対話者（ユーザー）向けの製品機能**として位置づけていた（同Doc第1節）。特に同Doc第3.2節は、LLMが自らの使用状況を会話中に申告する、という振る舞いを提案している。

本Docは、その前提となる**LLM自身の認識能力**（第2.1節）と、申告だけに留まらない**LLM自身による実行能力**（第2.2節、Self-triggered Compaction）を対象とする点で、Context Observatoryより一段深い、Agentic Actionの領域に踏み込む提案である。両者は競合しない別Scopeの提案であり、実装順序としては、第2.1節（認識）がContext Observatory第3.2節（申告）の前提になる、という依存関係がある。

## 4. 実現時期についての見通し

ユーザーは、本構想を「もし技術的に可能そうであればPhase 3の頭に」と、[Context Observatory提案](future_scope_proposal_context_observatory_ja_20260817234734.md)と同様の暫定的なTimingで位置づけた。ただし、同時に次の自己評価も示している。

> 「たぶん今は作れないよな。Agent実装とかその辺のPhaseにならないと。」

すなわち、本Docが対象とする2機能（特に第2.2節のSelf-triggered Compaction）は、LLMが自らTool実行等を通じて能動的にActionを起こす、Agent Runtime的な基盤を前提とする可能性が高く、**Phase 3の頭で技術的実現性がまだ整っていない場合は、Agent実装関連のPhase（Phase 3以降のいずれか）まで後ろ倒しになる**、という見通しをユーザー自身が示している。本Docは、この不確実性を残したまま記録する。

## 5. Status

```text
Current Point            : ユーザー構想を記録・まとめ直し。実装着手・
                            設計確定・技術的実現可能性の検証、いずれも
                            未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（提案記録）
Open Current Blocker      : NONE（Blockerではなく、Phase 3着手判断時の
                            検討候補という位置づけ。技術的実現可能性
                            自体が未検証である点に留意）
Controller-owned Next Work: Phase 3の内容・優先順位をCodex側・ユーザー
                            側で判断する際、本Docと
                            future_scope_proposal_context_observatory_ja_20260817234734.md
                            を合わせて候補として参照する。
Exact Next Route          : 本DocはRead-only参照材料として保持。
                            Claude側設計統括者役から能動的に着手・
                            提案することはない（Phase 3自体がまだ
                            開始していないため）。
```
