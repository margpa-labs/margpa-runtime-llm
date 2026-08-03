# Simple RAG Documentation Availability 要件定義

- 文書ID: `simple_rag_documentation_availability_requirements`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- supersedes: なし

## 1. Purpose

Phase 1-ex後に追加するSimple RAG／Project Documentation Explainerについて、Mac実機とLightningのどちらでも、参照対象の`docs/`が設置されていない状態を明示的かつ安全に処理する。

## 2. Common Contract

Deployment先にかかわらず、次を共通Contractとする。

```text
Component OFF:
  docs/を探索しない。
  CorpusをLoadしない。
  Errorを発生させない。

Component ON／明示利用:
  docs/存在確認を行う。
  docs/が存在しない場合はUnavailable Resultを返す。
  ModelへProject説明を推測させない。
  Application全体をCrashさせない。
```

## 3. Missing Docs Result

最低限、次の構造化情報を返せること。

```text
component   : project_documentation_explainer
state       : unavailable
reason_code : docs_directory_missing
retryable   : true
```

日本語表示：

```text
docs/が設置されていないため参照できません。
```

英語表示：

```text
The docs/ directory is not installed, so it cannot be referenced.
```

表示文言だけに依存せず、UI／CLI／APIが同じ`reason_code`を解釈できること。

## 4. Behavioral Requirements

- `docs/`不存在を空の検索結果、回答不能、Model Failureまたは内部Server Errorへ偽装しない。
- `docs/`不存在時に、Modelの一般知識だけでProject説明を生成しない。
- Corpus未構築、Manifest不存在、読取権限不足、破損、空Corpusは、必要に応じて別Reason Codeとして区別する。
- Error MessageへAbsolute Local Path、利用者名またはSecretを露出しない。
- Audit／StatusへLogical Component名、Reason Code、発生段階を記録可能にする。
- `docs/`を自動Downloadまたは外部から自動取得しない。
- Missing状態から`docs/`を配置した後、明示的Reloadまたは再試行で回復可能にする。

## 5. Mac Local

Mac LocalではPhase 1-ex後にSimple RAG本体を接続できる。

```text
enabled = false  # default candidate
```

利用者がONにした時だけ`docs/`、Corpus ManifestおよびRetrieverを確認する。`docs/`がなければ共通Unavailable Resultを返す。

## 6. Lightning

Lightningでは当面Hook-only／Default OFFとする。

```text
enabled             : false
provider             : absent allowed
docs probe           : none
index load           : none
retrieval            : none
additional model call: none
```

OFF時に`docs/`が存在しなくてもStartup Failureとしない。将来ONにした状態で`docs/`またはProviderが不足する場合は、共通Unavailable Contractに従う。

## 7. Test Requirements

- OFF＋`docs/`不存在：正常起動、探索なし
- ON＋`docs/`不存在：`docs_directory_missing`
- ON＋`docs/`存在：Availability Gate通過
- Missing時：Model Callなし
- Missing時：Index Loadなし
- Missing時：Absolute Path非露出
- 日本語／英語Message
- Missingから配置後の明示的Retry
- Mac／LightningでReason Code一致

## 8. Scope and Authorization

本要件はAccepted Reservationである。Phase 1-ex完了前のRAG実装を許可しない。

