# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag
phase: phase_1_ex
status: changes_required_before_manual_acceptance
language: ja
created_at: 2026-07-31 18:41:34 JST
owner: 設計統括者役
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_20260731172259.md
reviewed_status: implementer_status_phase_1_ex_mac_local_documentation_rag_20260731174758.md
follow_up_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731184134.md
manual_acceptance_gate: no_go
supersedes_review: null
```

## 1. Review結論

```text
Repository Implementation:
  CHANGES_REQUIRED

Manual Model／Browser Acceptance:
  NO_GO

Existing Regression Suite:
  GREEN

Blocking Findings:
  2 High

Required Follow-up Findings:
  2 Moderate
```

主要なPort分離、Corpus Allowlist、Project Root境界、System所有Reference、System由来Citation、Memory内Index、Public DemoでのRAG拒否および既存Conversation統合は、Accepted設計に沿っている。

一方、BM25のDocument Frequency計算に実検索結果を失わせる不具合がある。また、Accepted要件で定義したMain Model Contextからの動的RAG Budget算出が接続されておらず、`safety_margin_tokens`が実効しない。これらは手動試験結果を不安定または誤解を招くものにするため、ユーザーの手動Acceptanceより先に修正する。

Partial Read Failure後の有効Document 0件境界と、Local Mac限定Composition境界も、同じFollow-upで設計どおりに閉じる。

## 2. Reviewed Scope

主に次を確認した。

```text
config/feature_profiles/
  documentation_rag_defaults.toml
  local_documentation_rag.toml

src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/documentation_rag.py
src/margpa_runtime_llm/modules/conversation/
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/web/

tests/unit/documentation_rag/
tests/unit/conversation/
tests/unit/web/
tests/integration/web/

Accepted Requirements／Technology Selection／Architecture／ADR-0028
Implementer Handoff／Implementer Status
```

## 3. Accepted Points

- 新しいRuntime Dependency、Model、Network AccessまたはPersistent Indexを追加していない。
- `DocumentSourcePort`、`ChunkerPort`、`EmbeddingPort`、`IndexStorePort`、`RetrieverPort`、`ContextAssemblerPort`、`CitationPort`および`RagOrchestratorPort`を分離している。
- 初期Lexical Pipelineは`EmbeddingPort`を呼ばない。
- CorpusはCanonical／Stable Markdownへ限定し、`history`、`lossless`、Hidden、Backup、Temporary、Symbolic LinkおよびProject Root外を除外する。
- Document、Corpus Manifest、Chunk、QueryおよびProfileへSHA-512 Evidenceを持つ。
- IndexはMemory内Immutable Snapshotで、Lazy Build、Build LockおよびAtomic Replaceを持つ。
- 取得本文はUser Messageへ連結せず、System所有の非信頼Reference Messageとして分離する。
- CitationはModelの自己申告ではなくRetriever／Contextの採用結果から生成する。
- RAG OFF、Basic Preview unavailableおよびPublic Demo deniedをUI／Request／Adapter Availabilityで分離する。
- Public DemoではLocal Documentation Adapterを構築しない。
- Summary時にRetrievalを再実行せず、元回答のCitationを維持する。
- Cancellation、New Chat、Model Busyおよび既存Presentation契約を維持する。
- ErrorへAbsolute Path、Credential、Raw QueryまたはDocument本文を返さない。

## 4. Required Findings

### F1. BM25 Document FrequencyがTerm Frequencyとして集計される

Severity: High／Blocking

対象：

```text
src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py:62-67
src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py:119-132
```

`body_terms`、`heading_terms`および`path_terms`はChunk内のToken出現回数を持つ`Counter`である。その`Counter`をDocument Frequency用`Counter`へ`update`しているため、同じTokenが1 Chunk内に20回あればDFが20増える。

BM25のDFは、そのTokenを含む検索母集団内Chunk数でなければならず、常に`0 <= df <= population`である必要がある。

設計統括者役の独立再現：

```text
population = 2
df(test) = 20
query = test
selected = 0
```

該当TokenのDFがPopulationを超えることでIDFが負となり、実際に一致するDocumentが検索結果から消える。

Required：

- DFへは各ChunkにつきToken Keyを1回だけ加算する。
- Body、Heading、Pathの全Fieldで同じ不変条件を守る。
- `df <= population`をTestで固定する。
- 英語Tokenの多数反復Fixtureを追加する。
- 日本語2-gram／3-gramの多数反復Fixtureを追加する。
- 一致DocumentがScore条件を満たして選択されることを確認する。
- Tie-break、Field Weightおよび既存Ranking Contractを変更しない。

### F2. 動的Context BudgetとSafety MarginがRequest Pipelineへ接続されていない

Severity: High／Blocking

対象：

```text
src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py:30-51
src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py:218-239
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:147-168
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py:657-681
```

Accepted要件は次を定義している。

```text
effective_context_size
  - requested_max_new_tokens
  - system_and_history_tokens
  - safety_margin
  = available_rag_budget
```

現在は、RAG OrchestratorへQueryとCancellationだけが渡される。会話履歴、Requestの`max_new_tokens`、有効Context SizeおよびSafety Marginを使ったRequest単位のBudget解決がない。

Context Assemblerには常に固定`maximum_tokens = 768`または`fallback_maximum_characters = 2400`が渡される。`safety_margin_tokens`は値を保持するだけで計算に使われない。

また、`minimum_useful_tokens`の判定はToken Counterがある場合の`maximum_tokens < minimum_useful_tokens`だけだが、Contract Validatorがその値の組合せを生成前に拒否するため、現在の分岐は実質到達不能である。

独立再現では、同一RetrievalへSafety Marginを`0`と`700`で切り替えても、両方とも`context_used = 254／blocks = 1`となった。

Required：

- Request単位のRAG Budget入力またはResolver Contractを追加する。
- Effective Context Size、Requested Max New Tokens、System／History／Current Prompt使用量およびSafety MarginをBudgetへ反映する。
- Configの`maximum_tokens`は動的Available Budgetに対する上限として扱う。
- Main Model Tokenizerを安全に利用可能ならToken数を使う。
- 利用できない場合は、履歴と生成上限を無視せず保守的Fallbackで上限を算出する。
- 実Available Budgetが`minimum_useful_tokens`未満ならReferenceを注入せず、安全なState／Warningとする。
- Main Backendの最終Context Limit検査はDefense in Depthとして維持する。
- History増加、`max_new_tokens`増加およびSafety Margin増加でRAG Budgetが減少するTestを追加する。
- Reference Messageを含む最終RequestがContext Limitを超えないことをTestする。

広いInference Adapter再設計が必要になる場合は推測で実装せず、必要Contractと影響をStatusへ記載して設計統括者役へ戻す。

### F3. Partial Read Failureで有効Documentが0件でもNo Hitとして通常生成する

Severity: Moderate／Required Follow-up

対象：

```text
src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py:138-181
src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py:195-216
src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py:251-252
```

Manifest作成後、Documentが変更、削除または読取不能になった場合、`load_documents`はDocument単位で除外する。すべて除外されても空Chunk Indexを生成し、Retrieval No Hitとして`state = enabled／should_generate = true`を返す。

Accepted要件では、Partial Read Failure後に有効Documentが0件なら`docs_unavailable`としてRAG Model Callを開始しない。

`document_count`もManifest Entry数を返すため、実際に読み込めた有効Document数と異なる可能性がある。

Required：

- `load_documents`後に有効Document 0件を明示判定する。
- Chunk生成後に有効Chunk 0件を明示判定する。
- 該当時は`documentation_corpus_empty`等のSafe Warning、`unavailable`および`should_generate = false`を返す。
- Empty IndexをAtomic Storeへ公開しない。
- Partial FailureでDocumentが残る場合だけDegraded継続する。
- Status／EvidenceのDocument Countは実際に有効なDocument数と一致させる。
- Manifestは非空だが二回目Readで全件除外されるFixtureを追加する。

### F4. Local Adapter BindingがMacではなくWeb Exposure Modeだけで決まる

Severity: Moderate／Required Follow-up

対象：

```text
src/margpa_runtime_llm/entrypoints/web/main.py:111-145
```

現在は`WebExposureMode.LOCAL`だけでLocal Filesystem Adapterを構築する。Deployment／Host Platformを確認していないため、LinuxまたはWindowsでLocal Web Profileを選んだ場合にもMac Local AdapterがBindingされる。

Accepted要件は初期RuntimeをLocal Mac、External RuntimeをHook Onlyとしている。Basic PreviewとPublic Demoは現在安全に分離されているが、Platform追加時の暗黙転用を防ぐ必要がある。

Required：

- Composition RootでWeb Access CapabilityとDeployment／Host Eligibilityを別々に解決する。
- 初期Local AdapterはMac対象RuntimeでのみAvailableとする。
- Linux／Windows／External Runtimeでは、明示External Adapterがない限りUnavailableとする。
- OS判定をDocumentation Domain内部へ埋め込まない。
- Public Demo denied／Adapter非構築、Basic Preview eligible／Adapter未Bindingを維持する。
- Linux x86_64 Local Exposure FixtureでもMac AdapterをBindingしないTestを追加する。

## 5. Independent Verification

設計統括者役が再実行した。

```text
Target Documentation RAG／Conversation／Web Test:
  69 passed in 0.94s

Repository Full Suite:
  359 passed
  3 deselected
  49.99s

Ruff Check:
  PASS

Ruff Format Check:
  PASS／114 files

Mypy:
  PASS／119 source files

JavaScript Syntax:
  PASS／node --check
```

実GGUFを使うRAG Model SmokeとBrowser Manual Acceptanceは未実施である。未実施項目をPass扱いしない。

実CorpusのModel非Load Retrieval Smokeでは、MARGPA Runtime LLM、ARGD／DAGD、EASA、DLAGSA、OCILNS、Mac Documentation RAGおよびPublic Demo RAGのQueryでCitation候補を取得できた。ただしF1により、反復語を含む別Corpusでは検索結果が欠落し得るため、手動Acceptanceの代替Evidenceにはしない。

## 6. Integrity／Scope

```text
Accepted Requirements:
  7ef26d2458ef481d47b0fa53dc5e8ec7e9da1d81c29bc35d0704245eb6cccb97b2ddfcc64e8a15b2071e3ea66a0eebe16fa081979d17f14eed791a4b1c6999be

Accepted Technology Selection:
  56203c926ccf5cc99b04f3db210f1fb46aaedcccf30d55df70f5e3177f6b9970632ad1e87f8c7aa5a427561c43a5a34fbb88ef817a42ea91b2c68534ff347f53

Accepted Architecture:
  0c7a27dd0cfa707a12654416576e357a49c52dc908b73a6d9dfc7ba1c85738c39ab46623a6e3fbaedd2a842b5486b5d6039272e1edb6a4f74aed43a317b49b0a

Accepted ADR-0028:
  d2bee3efabbf8a7a025ba2fa4d6da462bbcb85160a5fa2458a9ff7996df0bbcfbbbfdb74d9d7516b0311b7c54309686646f2b9e962a8fe4c59c234ecc8fa2f9b

Implementer Status:
  a160c916e251e48a2db4a804819d988d8ca401997884c7b6ee16ad520bf1318a3b102d761c32c689a7d3a68d478d139fea182abe328600b7a735519653d0a98d
```

Review中にSource、Config、Test、Model、Dependency、Lightning、GitまたはProject Root外を変更していない。

## 7. Next Gate

[Mac限定簡易Documentation RAG Correctness Follow-up Handoff](implementer_handoff_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731184134.md)の範囲だけを実装担当へ戻す。

Follow-up Status提出後、設計統括者役がSource、Contract、Regression Testおよび全Suiteを再Reviewする。F1～F4が解消されてから、ユーザーによるLocal GGUF／Browser Manual Acceptanceへ進む。
