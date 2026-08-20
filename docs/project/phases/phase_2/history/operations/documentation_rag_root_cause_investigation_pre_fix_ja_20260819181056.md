# Documentation RAG既知課題2件 — 実装前根本原因調査

```yaml
document_id: documentation_rag_root_cause_investigation_pre_fix_20260819181056
status: investigation_record
phase: phase_2
subphase: documentation_rag
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 18:10:56 JST
language: ja
related:
  - documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529
  - documentation_rag_retrieval_relevance_and_static_results_known_issue_ja_20260819113116
```

## 0. 位置づけ

ユーザー指示「その2点について、実装／修正はまだ入らず、調査だけしてくれ。今。」を受けた、実装着手**前**の根本原因調査記録。本Docの時点では実装Fileへの変更は一切無い。

## 1. §3.3（既存Known Issue）：Codeとの整合性再確認

[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)の分析（`_is_high_signal_identifier`によるSubject抽出→`top_k`超過でFail-closed停止）が、現在のCodeと一致するかを検証した。

- `lexical_tokenizer.py`の`_is_high_signal_identifier()`：記載通りの判定条件（全Upper2文字以上／数字含有／Path区切り文字／混在Case）が現存。
- `contracts.py:545`の`top_k: int = Field(default=4, ...)`：既定値4は変わらず。
- `documentation_rag.py`の`assembled_uncovered_subject_count`判定（326〜340行）：1件でも未Coverage Subjectがあれば`grounding_state = SUBJECT_COVERAGE_INSUFFICIENT`となり`generation_allowed = False`——記載通り。

**結論：既存分析にDriftは無く、そのまま有効。**

## 2. §3.7 Pattern 1（検索結果固定化）：新たな根本原因

`bm25_retriever.py`の`retrieve()`（109〜261行）を精査した結果、**§3.3と同一のSubject Coverage保証機構が、Pattern 1の直接の原因である**ことが判明した。

### 2.1 選定Logicの構造

```text
1. 通常のBM25 Relevance Scoreで全ChunkをScoring・Sort（187〜196行）。
2. Sort結果を使う前に、Query内の各Subject（"LLM"等の高Signal識別子）
   ごとに `_coverage_candidate()` を呼び、Subjectを最もよくCoverする
   Chunkを1件、`selected_rows` へ強制的に先埋めする（200〜218行）。
3. `top_k` 枠が余った分だけ、通常のRelevance順で埋める（220〜230行）。
```

`_coverage_candidate()`（264〜287行）は、`(tier, global_rank)`でSortして先頭を返す、**完全に決定論的な選択**（Tie-break・乱数要素は無い）。

### 2.2 Pattern 1との対応

ユーザーが実際に試した3Query（「MARGPA Runtime LLMとは？」「LLMとは？」「一般的なLLMとは？」）は、いずれも"LLM"（全Upper2文字以上）という同一Subjectを含み、2件中2件は"MARGPA"も含んでいた。

`top_k=4`という少ない枠のうち、Subject Coverage保証Loopが"LLM"・"MARGPA"それぞれについて**常に同一のAnchor Chunk**を強制的に確保するため、残りのRelevance順で埋まる枠が非常に少なく（多くの場合ゼロに近く）なり、Query本来の違いが結果へほとんど反映されなくなる。

**すなわち§3.3と§3.7 Pattern 1は、同一の設計判断（Subject Coverage保証）が生む、2つの異なる症状である。**

## 3. §3.7 Pattern 2（無関係質問への誤発火）：新たな根本原因

2つの要因の複合。

### 3.1 Stopword除外の不在

`src/margpa_runtime_llm/adapters/documentation_rag/`・`src/margpa_runtime_llm/modules/documentation_rag/`配下を検索したが、Stopword（助詞等の機能語）除外の実装は存在しない。日本語の助詞（「の」「は」等）も、そのままQuery Termとして採用される。

### 3.2 低いminimum_score閾値と、Corpus全体のConfidence Gate不在

```text
minimum_score = 0.1（local_documentation_rag.toml・lightning_public_documentation_rag.toml
                     双方で同一）
```

`bm25_retriever.py`184行の`if score >= query.minimum_score`は、この低い閾値を超えた個別Chunkだけを候補に残すが、「Corpus全体で見て、そもそも十分Confidentな一致が存在するか」を判定する仕組みは無い。Subject Coverageに基づくFail-closed判定（§1参照）は、Query全体のTopic的な関連性とは無関係な、別の判定軸である。

### 3.3 Pattern 2との対応

「リポビタンDの成分は？」のような、Corpusと無関係なQueryでも、共通の助詞等から偶然0を超えるScoreが立ち、`minimum_score=0.1`を超えてしまうため、「一応それらしい」Chunkが提示される。

## 4. Status

```text
Current Point            : §3.3・§3.7（Pattern 1・Pattern 2）全ての根本
                            原因をCode Level（行番号付き）で特定した。
                            実装・修正は一切未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。実装Fileは無変更。
Validation                : N/A（調査記録）
Open Current Blocker      : NONE
Controller-owned Next Work: ユーザー指示により、top_k引き上げ（緩和策）
                            および両Pattern双方への対応実装へ進む。
Exact Next Route          : 実装Phaseへ移行。
```
