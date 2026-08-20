# 要改善事項 — Documentation RAG「Subject Coverage不足」による自己引用Loop Bug

```yaml
document_id: documentation_rag_subject_coverage_self_citation_known_issue_20260818002529
status: known_issue_open
phase: phase_2
subphase: documentation_rag
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-18 00:25:29 JST
language: ja
authorization: |
  ユーザー指示（2026-08-17）：実機確認で発見したBugについて、「今は
  このままでいい。ただ、要改善事項として書いておいて」。修正は一切
  未着手・未着手予定。本Docは発見内容の記録のみ。
created: Claude Code
```

## 0. 位置づけ

**本Docは既知の課題（Known Issue）の記録のみであり、修正は一切未着手・未着手予定。** ユーザーは実機確認でこのBugを発見した後、「今はこのままでいい」と明言しており、修正着手前にはBackup取得を予定している。本Docの役割は、原因を含めて正確に記録し、将来の修正判断・優先順位付けのInputとすることに限定される。

## 1. 事象

Documentation RAGを`ON`にした状態で、**LLM自身が直前に出力した回答（引用文書欄付き）をそのままCopyして次のMessageとして送信すると、`Error: documentation_subject_coverage_insufficient`という送信Errorが発生する。** 発生後は、会話Optionから「再開」を選ばないと復帰しない。

一方、RAGが関与しない通常の質問（例：「Qwenってどこの会社のModel？」）は、同じ会話内・同じ状態でも問題なく成功する。

## 2. 根本原因

### 2.1 Subject（必須Coverage対象）の抽出条件

`src/margpa_runtime_llm/adapters/documentation_rag/lexical_tokenizer.py`の`_is_high_signal_identifier()`（59〜73行）は、送信Message内の英数字混じりTokenのうち、次のいずれかに該当するものを「必ず根拠Chunkを確保すべきSubject」として扱う。

```text
- 英字2文字以上が全てUppercase（例："LLM"）
- 数字を含む（例："phase_1"）
- 英数字の間にPath区切り文字（"." "_" "/" "-"）がある
  （例："docs/public/roadmap_ja.md"、"margpa-runtime-llm"）
- 先頭以外にUppercaseを含む混在Case
```

### 2.2 top_kによる機械的な失敗

`src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py`の`retrieve()`（200〜218行）は、検出された各Subjectへ優先的に1件以上のChunkを割り当てようとするが、`RetrievalQuery.top_k`（既定値4、`src/margpa_runtime_llm/modules/documentation_rag/contracts.py:545`）に達した時点で打ち切る。

`src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py`（305〜340行）は、1件でもCoverageされなかったSubjectがあれば、`documentation_subject_coverage_insufficient`という警告を発し、**回答生成そのものを止める**（`generation_allowed = False`）。これはFail-closed（不明な場合は安全側に倒す）という、Documentation RAG全体の設計方針に沿った、意図的な挙動である。

### 2.3 自己引用Loopとしての成立条件

RAG回答は、本文中に引用元のFile Pathを含む「参照文書」欄を出力する。この回答をそのままCopyして送り返すと、その引用欄自体が、次のQueryのSubjectとして再解釈されてしまう。

実際にユーザーが再現したMessage（前回回答の全文Copy）には、少なくとも次の5件の独立したSubjectが含まれていた。

```text
LLM（全Upper）
margpa-runtime-llm（Hyphen区切り）
docs/public/roadmap_ja.md（Path）
docs/project/phases/phase_1/handoffs/phase_1_handoffs_ja.md（Path、数字入り）
docs/project/phases/phase_1/architecture/phase_1_architecture_ja.md（Path、数字入り）
```

`top_k=4`に対してSubjectが5件以上のため、**確率的にではなく、必ず**いずれか1件がCoverage対象から漏れる。一方、「Qwenってどこの会社？」のようなMessageには、上記条件に該当するTokenが実質0件のため、Subject Coverageの制約自体が発生しない。

**すなわちこれは、「RAG回答が自らの引用欄を出力する」という仕様と、「送信Message内のPath様Tokenを無条件にSubjectとして扱う」という仕様の組み合わせにより、RAG回答をCopyして送り返すという、ごく自然な操作が、決定論的に自滅する自己参照的な構造になっている。**

## 3. 設定値についての補足調査

ユーザーからは、「PCの性能上、あまり攻めた設定にできなかったのではないか（Codex側の判断として）」という推測が示された。この推測を検証するため、`top_k`の設定箇所を確認した。

- `config/feature_profiles/local_documentation_rag.toml`（Mac Local向けProfile）：`top_k = 4`
- `config/feature_profiles/lightning_public_documentation_rag.toml`（Lightning／Public Demo向けProfile）：`top_k = 4`

**両者は同一の値であり、環境（Local Mac／Cloud）による差別化は現時点でされていない。** これは、Phase 2-C（`docs/project/phases/phase_2/`該当Handoff参照）でMac専用に`context_size`が個別Tuningされた前例とは対照的である。したがって、「Local Macの性能を踏まえて意図的に控えめにした」という明確な設計根拠を裏付けるDocsは、少なくとも`docs/project/phases/phase_2/`配下のRequirements／Architecture文書には見当たらなかった（本Docの調査範囲内）。ユーザーの推測は妥当性のある仮説として残しつつ、**現状は「意図的なHardware Tuningの結果」というより、「Corpus規模・Context Budget（768 Tokens）とのBalanceで一律に選ばれた値」である可能性の方が高い**、という調査結果を付記しておく。

## 4. 改善方向（将来検討、未着手）

以下は、いずれも実装しておらず、将来の改善候補として列挙するに留める。

```text
- 送信Message内の「引用文書欄」形式（本Product自身が出力するCitation
  Blockの形式）を検出し、その部分をSubject抽出の対象から除外する。
  RAG回答が生成するCitation欄には、本Product固有のFormatがある可能性が
  高く、これを識別できれば、自己引用Loopの根を断てる。
- Subject数がtop_kを上回る場合に、即座にFail-closedで停止するのでは
  なく、「一部Subjectのみ根拠不足」という段階的な警告（部分的な回答＋
  未Cover Subjectの明示）へ緩和する設計も検討に値する。ただし、これは
  Fail-closedという既存の設計思想そのものに関わる判断であり、安易に
  変更すべきではない。
- top_k・Context Budget等のRAG関連設定を、Local Mac／Cloud等の実行
  環境ごとに、意図を明記した上で個別Tuningする（Phase 2-Cのcontext_size
  Tuningと同様のPattern）。仮に現状の値が「一律の暫定値」であるなら、
  環境ごとの意図的な調整に置き換える余地がある。
- 送信Message長・抽出Subject数に対する事前チェックを設け、機械的な
  失敗が確定している場合には、送信前（Client側）で利用者へ警告する。
```

## 5. Status

```text
Current Point            : Bugの原因を特定し、記録のみ完了。修正は
                            一切未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。実装Fileは無変更。
Validation                : N/A（既知の課題記録）
Open Current Blocker      : NONE（Blockerではなく、将来の修正判断
                            待ちの記録）
Controller-owned Next Work: ユーザーがBackup取得完了後、修正着手の
                            要否・優先順位を判断する。
Exact Next Route          : ユーザーからの修正着手指示待ち。
```
