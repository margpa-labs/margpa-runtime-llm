# 要改善事項 — Documentation RAGの検索結果固定化・無関係質問への誤発火（新規観測）

```yaml
document_id: documentation_rag_retrieval_relevance_and_static_results_known_issue_20260819113116
status: known_issue_open
phase: phase_2
subphase: documentation_rag
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 11:31:16 JST
language: ja
authorization: |
  ユーザー指示（2026-08-19）：実機確認で発見した2Patternについて、
  「2は今回やらない。予約枠のとこに、修正対象としてdocsにして」。
  修正・詳細な原因調査は一切未着手・未着手予定。本Docは発見内容の
  記録のみ。
created: Claude Code
```

## 0. 位置づけ

**本Docは既知の課題（Known Issue）の記録のみであり、修正・詳細な原因調査は一切未着手・未着手予定。** 既存の[documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md](documentation_rag_subject_coverage_self_citation_known_issue_ja_20260818002529.md)（以下「既存Known Issue」）とは別に、ユーザーが今回の実機確認で新たに発見した2つのPatternを記録する。既存Known Issueへの追記ではなく新規Docとした理由は、対象とする事象が異なるため（既存Known Issueは送信Error、本Docは検索結果の異常・誤発火）。

## 1. 事象

### Pattern 1：Query内容に関わらず検索結果が固定化する

Documentation RAGを`ON`にした状態で、内容の異なる複数のQuery（「MARGPA Runtime LLMとは？」→「LLMとは？」→「いや、MARGPA Runtime LLMとかじゃなくて、一般的なLLMとは？」）を連続して送信したところ、**3回とも全く同一の4件の参照文書**（`docs/public/roadmap_ja.md`、`docs/project/phases/phase_1/handoffs/phase_1_handoffs_ja.md`（2回重複）、`docs/project/phases/phase_1/architecture/phase_1_architecture_ja.md`）が返された。

続けて「NLPとは？」を送信したところ、送信Error（詳細未確認）が発生した。ユーザー自身の推測では、これは既存Known Issueが扱う`top_k`関連の既知Bugである可能性が高いとのことであり、Claude側でも、会話履歴に蓄積した過去のRAG回答由来のCitation欄（Path様Token）が、新しい短いQueryに対してもSubject Coverage判定へ引き続き影響し得るという点で、既存Known Issueと同一・関連の事象である可能性が高いと見ている（本Doc作成時点でCode Levelでの確認は行っていない）。

### Pattern 2：明らかに無関係な質問でもRAGが誤発火する

Documentation RAGを`ON`にした状態で、本Projectと全く無関係な質問（「リポビタンDの成分は？」）を送信したところ、RAGが起動し、本Projectの内部Docs（`docs/project/phases/phase_1/governance/phase_1_governance_ja.md`、`docs/project/phases/phase_1/requirements/phase_1_requirements_ja.md`）が「参照文書」として提示された。回答内容自体は、実際にはRAGから取得した情報を使わず、LLM自身の一般知識でリポビタンDについて回答しており、参照文書欄の内容と回答本文の関連性が無い。

## 2. 既存Known Issueとの関係

既存Known Issueは、「RAG回答の自己Copy送信によるSubject Coverage不足」という、特定の再現手順を持つ送信Error（`documentation_subject_coverage_insufficient`）を扱っている。本Docが記録するPattern 1・Pattern 2は、いずれもEmail送信自体は成功しており、**検索結果の内容・関連性そのものが不適切**という、既存Known Issueとは異なる症状である。「NLPとは？」のErrorのみ、既存Known Issueと同一機構による可能性が高い。

## 3. 原因調査について

本Doc作成時点では、ユーザー指示によりCode Levelでの原因調査は行っていない。将来の調査候補として、次の観点が考えられる（未検証の仮説）。

```text
- Pattern 1：BM25等の検索Scoreが、特定条件下でQuery内容に依存せず
  同一Rankingへ収束していないか（例：Query前処理・Tokenize段階での
  内容欠落、Cache層の意図しない再利用等）。
- Pattern 2：検索結果をRAG対象として採用するか否かのRelevance閾値
  判定が機能していない、または閾値自体が低すぎる可能性。
```

## 4. Status

```text
Current Point            : 実機確認で発見した2つの新規Pattern（検索結果
                            固定化・無関係質問への誤発火）を記録。修正・
                            詳細調査は一切未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。実装Fileは無変更。
Validation                : N/A（既知の課題記録）
Open Current Blocker      : NONE（Blockerではなく、将来の修正判断待ちの
                            記録）
Controller-owned Next Work: 既存Known Issueと合わせて、「RAG丸々改善
                            Phase」のTriggerが成立した際に、原因調査・
                            修正着手の要否を判断する。
Exact Next Route          : ユーザーからの修正着手指示待ち。
```
