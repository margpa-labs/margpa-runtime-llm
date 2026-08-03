# Phase 1-ex Mac Local Documentation RAG Correctness Follow-up Implementer Status

```text
status: IMPLEMENTATION_COMPLETE_PENDING_DESIGNER_REVIEW
phase: phase_1_ex
role: implementer
subject: mac_local_documentation_rag_correctness_follow_up
recorded_at: 2026-07-31 19:15:21 JST
manual_acceptance: NOT_STARTED_NO_GO
```

## 1. Result

Accepted Follow-up Handoffで指定されたF1～F4を実装し、対象Test、Repository全Suite、Ruff、MypyおよびJavaScript構文確認を完了した。

```text
F1 BM25 Document Frequency Correctness : completed
F2 Dynamic Request Context Budget      : completed with conservative fallback
F3 Empty Valid Corpus Boundary         : completed
F4 Local Mac Host Eligibility          : completed
```

未完了境界は次である。

- Main Model TokenizerのExact Token Counterは、Inference Adapter全体へ広いInterface変更を加えず、未接続とした。
- 保守的FallbackだけでContext上限を成立させた。将来のExact CounterはRequest Context Port境界から追加可能である。
- 実GGUF、BrowserおよびユーザーManual Acceptanceは実施していない。
- 本StatusだけではManual Acceptanceへ進まない。設計統括者役の再Reviewと明示的なGOを待つ。

ユーザーは本Follow-up変更前Backupについて、直前Backupをそのまま使用して作業続行可能と確認した。

## 2. Authority and Inputs

```text
designer_review_phase_1_ex_mac_local_documentation_rag_20260731184134.md
  638c76c4e2127578413d5f8ea9babbad67ee66a9b306be157efd5e54de0a7324e8112886c0175737e72b2cb36fc40c1b7f912ca19a235de9a1ceff39513dfb27

implementer_handoff_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731184134.md
  5053f6ae1ab1c673df44b93ee9ad1df9e6b102c898b6ab860feb020505cc7d6b58acaa6999846ba56c40704174c07d68aa385e4bf72f6fb0637a89eb483e6323

implementer_status_phase_1_ex_mac_local_documentation_rag_20260731174758.md
  a160c916e251e48a2db4a804819d988d8ca401997884c7b6ee16ad520bf1318a3b102d761c32c689a7d3a68d478d139fea182abe328600b7a735519653d0a98d
```

Project Root内だけを対象とし、`models` Symbolic Linkは追跡していない。

## 3. F1: BM25 Document Frequency

### Before

Body、HeadingおよびPathのTerm Frequency `Counter`をDocument Frequency `Counter`へ直接加算していた。同一Chunk内でTokenが反復すると`df > population`となり、IDFが負になって一致Chunkが検索結果から消える境界があった。

### Change

- DFへは各ChunkのTerm Keyだけを1回ずつ加算する。
- Body、HeadingおよびPathの全Fieldへ同じ不変条件を適用した。
- Retriever Algorithm Versionを`1`から`2`へ更新し、旧Index Cacheとの混在を防止した。
- 英語反復Tokenと日本語2-gram／3-gram反復Fixtureを追加した。

### After Evidence

```text
Repeated English Token:
  df(test) = 1 per matching chunk
  matching chunk retrieved

Repeated Japanese N-gram:
  all field df <= population
  matching chunk retrieved

Existing ranking, tie-break, diversity and no-hit tests:
  PASS
```

## 4. F2: Dynamic Request Context Budget

### Before

RAG OrchestratorへQueryとCancellationしか渡らず、固定`maximum_tokens = 768`／`fallback_maximum_characters = 2400`を使用していた。履歴、Requestの`max_new_tokens`、実Runtime Context SizeおよびSafety MarginはBudgetへ反映されていなかった。

### Change

Immutable `DocumentationRagRequestContext`を追加した。

```text
effective_context_size
requested_max_new_tokens
system_history_current_prompt_tokens
prompt_token_count_exact
```

Production Web Compositionは、Model Load後の`runtime_info.loaded_context_size`をConversationへ渡す。ConversationはResponse Language System Message、全History、Current User MessageおよびDocumentation Reference Message Framing ReserveをRequest単位で見積もり、Contextual RAG Portへ渡す。

Budget計算式は次である。

```text
request_available_rag_tokens
  = max(
      0,
      effective_context_size
      - requested_max_new_tokens
      - estimated_or_exact_system_history_current_prompt_tokens
      - safety_margin_tokens
    )

effective_rag_tokens
  = min(configured_maximum_rag_tokens, request_available_rag_tokens)
```

Tokenizerを安全に公開する既存Portがないため、今回は次の保守的Fallbackを採用した。

```text
Prompt estimate:
  64 token base reserve
  + each Message UTF-8 byte length
  + each role/name UTF-8 byte length
  + 64 token framing reserve per Message
  + 64 token Documentation Reference Message framing reserve

Reference assembly:
  rendered Reference MessageのUTF-8 byte数を1 byte = 1 tokenとして保守的に計測
  fallback limit = min(configured fallback characters, effective_rag_tokens)
```

UTF-8 byte単位は通常Text Token数に対する保守的上界として使用する。Chunk本文の途中切断は行わない。Available Budgetが`minimum_useful_tokens`未満ならReferenceとCitationを生成せず、`documentation_context_budget_insufficient` Warningを返す。

Production Local Compositionは`ContextualRagOrchestratorPort`を使用する。既存Test Double向けのPre-request-context互換Portは残したが、Production CompositionへはBindingしていない。

Main Backendの`prompt.token_count + max_new_tokens <= loaded_context_size`最終検査は変更していない。

### After Evidence

```text
same query / same corpus:
  larger history        -> context budget decreased
  larger max_new_tokens -> context budget decreased
  larger safety margin  -> context budget decreased

insufficient budget:
  reference_message = none
  citations = empty
  selected_chunk_count = 0
  safe warning emitted

normal budget:
  rendered UTF-8 byte usage <= effective RAG token budget
  prompt estimate + reference usage + max_new_tokens + safety <= context size

summary:
  existing retrieve-once contract remains green
```

## 5. F3: Empty Valid Corpus

### Before

Manifestが非空でも二回目Readで全Documentが除外された場合、空IndexをStoreし、No Hitとして`enabled／should_generate = true`を返していた。`document_count`もManifest Entry数を使用していた。

### Change

- `load_documents`後の有効Document 0件を明示的にUnavailableとした。
- Chunk生成後の0件もUnavailableとした。
- Empty IndexをAtomic StoreへReplaceしない。
- Partial Failureで有効Documentが残る場合だけDegraded継続する。
- Normal／No-hit／Unavailable／Build Failureの`document_count`へ、判明している実有効Document数またはIndex Document数を使用する。
- Absolute PathおよびDocument本文をWarning／Evidenceへ含めない。

### After Evidence

```text
all files changed after manifest:
  state = unavailable
  should_generate = false
  document_count = 0
  index replace calls = 0

one valid document remains:
  state = enabled
  document_count = 1
  partial failure warning retained

zero chunks:
  state = unavailable
  index replace calls = 0
```

## 6. F4: Local Mac Host Eligibility

### Before

`WebExposureMode.LOCAL`だけでMac Local Documentation AdapterをBindingしていた。Linux／Windows Local Web RuntimeでもMac用Adapterが構築される可能性があった。

### Change

Composition RootでWeb ExposureとHost Eligibilityを分離した。

```text
Local adapter eligible
  = WebExposureMode.LOCAL
  and platform.system() == "Darwin"
  and platform.machine().casefold() == "arm64"
```

OS固有判定はDocumentation Domainへ入れていない。

### After Evidence

```text
Darwin / arm64 / Local : adapter available
Linux / x86_64 / Local : adapter not built, unavailable
Windows / AMD64        : host eligibility false
Basic Preview          : eligible profile, adapter unavailable
Public Demo            : denied, adapter factory not called
```

Mac用既存機能は維持されている。

## 7. Changed Files and SHA-512

```text
src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
  before: 19dc86a0eb0dcc5aacc570d474d2fbf18fc730eb827f750b89c4769bb49e70e66941668c488aa72530dbc7207d69086f04df7822224262021965d2ca6e96dd09
  after : daecec8829fced3ffb0ff85c0607ba8e2c3518c28dc93e7650b89bd62bc3af64be4b7b1ccde656ae45bd644a0e43e867ea28d149a304d3a8f690954884bdd8f7

src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py
  before: 3871902d5f217dfa2c3585495222a30b146b031b96ae3a17b0f6ef6b0431bef9de62e6210f60d733e5279af82c7d45899328dd189c5dc99f01b24bd851024741
  after : 54065cad4b43ad59ef343f7849a89301d9a78be56aeec7e13ad48deb7fab21a032ac13fd7f407895c4e55497e5b4e2004aa434cd5e856c9168f8d69190432414

src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: 5f9982ef5b00c75d7d3bd0c5ec7e8e95164ddb9175e025173d99cb2065a78da9fd56888e31f86bf3cd2b52faef4f2f1147d26cb95fe77065d4650ad088996fb6
  after : d64dc56f91c5646c19223eeeee111e5426b94d64a4f7405de2c1a9f035910d182f8ab722c4c03e8bf1cdaa4939acdd9b4b9db24c665a5a16df09bd08adf8b466

src/margpa_runtime_llm/modules/documentation_rag/ports.py
  before: a9c0170cbf1408967089ade477545883eaff3df3854e18aab5e7b4c208777da464c2959c781685379271ac8e21c0a8295245ff002e919be6146f71e49eea14f1
  after : 5066ff4249e67fa98d8d9e1c7c732a58063187b7ef8fc235452ccc83af42429f7b1914918e62085c460d282b1324ef7a738a66af122de88764cb3751acd0d999

src/margpa_runtime_llm/modules/documentation_rag/public.py
  before: 9457c44f7f3a68a94317eced66a1c2fda614377dc7d2c331914f3909da51f4458217696c492b5fc55ad201b77cee06f256bc45445911d86f60202aedce3e057e
  after : 1ba21cdfca2fa328a52fe5cd280102047f7954040f9ef8471805eaab2ba6b3a963175d571acad3f6da2b2c7eedf8762bb0ec6c3b696fe3aa554232a020d4fad5

src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
  before: ed709f5e0913382bcb7bff1ee04f080a46b5f300786df68f7b08733b3baea97cd503b975ba3e26e5fa7f782ebe5adfb1165871473e44bc7647d1fd0721833955
  after : 132f51715949a1cd03f94b25d6b6c49ea08e5faf40ae9e03d6931ed5baa03683fe691d53ab72dee99664d368b4be79e7a32dc05a8e9934a41714f63d05fbec0b

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  before: 1a7de791d49390fcaa4e4e7658c1f9dc7a5e9414c907c34069e524e22566e137b88bc0508431a390cb31ebfffdcd45a48baa93457cab68f916c9be912737a3dc
  after : f72fccbb44644571cbc355d7eac4566f08bd97d86e0e21ffe147aef62fec204aa00db7bb5dc112cd22384a97a7ce213a373aa95bf99c896987a336396500a279

src/margpa_runtime_llm/bootstrap/documentation_rag.py
  before: 3d510de2493c1cca84596c64ef0e399f03400db0976a4aca3c3358a2a751b2af017d70ad9e73103bc6aa48d6c34922d84953f4435a612e30686a0c220a5dc621
  after : 3946d6398befc74b9e647ecafdcac9b6ca4e8ed741efbeee61369bb04e9807aa6ebe0b73bf8de92e8c1fbcaaa57c10455e5d5d1f983cbff3796671d34bfa20d3

src/margpa_runtime_llm/bootstrap/web_application.py
  before: 2d16b936d516dbc6037d966abb12122a7964b15f358488b40168f373f8eba0fdc9b9de1cf7648cce95ae3d6fa3575f83e5fccc0a0b8c8867d6cebf4f0389abb8
  after : ce293d3d37d8f33ba560c1cf0584b52b134c48435cc2356d48b5c5d024b332a7264015c60276c41587ed2ba652db96e8427ef7b2bd04ae0a97138f716b7f33ed

src/margpa_runtime_llm/entrypoints/web/main.py
  before: a1602df5ba7a0f68232164f382211666174d813cf953ddd0a93e4e75ae000c6649720606cfa8de12f3c64000ed04f9167e9fe9ff72c6aa5a15309f81a2e717fe
  after : b4387460a70060130b58f8e7e95112f9fbd6b33bf63ebeba6bcfc839aaf1212405905c30802f73390e722fe52f3eec7db64c41e81d4fd2df32c47c271de5f562

tests/unit/documentation_rag/test_lexical_retrieval.py
  before: b68abd7b39e0f4402089335e6e431a69ee337d47ee2ff96cea0dc04e68d50d55c2d872eb522e63d2d134ab281778c5e3d6f0293c2c8b8423216a90351869ed73
  after : 1d1c440ffded822200d36b138bda2413c37d94d5cc74e63e1b9f7114547a48c8f0a94d352f7cc223313b6354e2bf35d04012bef1b138c9e360fa81b5e239c024

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  before: 37ef26f7e82d8bff769bbaa8ab8c02f4902d84d044909fe1f57b49b75e7fc34c3293f03c916ff0a7039295de035f3401acc9c1ad2a8a9b09a71672ed6a66a7f7
  after : 84526842d81bbd7f21e205597d20f1a74dc016b64bd23fae050f27771a55a4792a8326970120b9c169bd65a019f270ce10d5686252eae499a450fe435f629ac8

tests/unit/conversation/test_conversation_generation.py
  before: 356ac1f806118b087b06d01464a9ed822e78c84a14fa0b86d60cc9e607aa56c18af7e76b1d24855ffb3c27e39840467b41f26fae19104373533ce9e546cc8f41
  after : 082a869e9e3d7d34dd8da7365299c47ec052e389038cfb1e6149e3080636ea482d6179903ef7afdbfcb689a6223dafc0fc7b251af0798a1bd9c966cd9938d293

tests/unit/web/test_web_cli.py
  before: 19a746c8b7b7a062c9c7af4bc5cf0afa520306643674d53bdee9fe55f664e262c0a154e1a87238938d2a77b6c46216dab377eb73b371805bee9249fae9c791ad
  after : d1c2ec58ff7f7790f9a4e149ad667fc81fb505b9a9ff6e6612ef973ab5018b27c623e0e3bbf63765cf9a42acd4870e3664fa55ee192849028a28e41ec108170b

tests/integration/web/test_web_app.py
  before: aa0cb4d7c8614f48e9d4bf8b3c57da1599fdc8a107283aa9521442a1ac55ec5698af02cc42f9a237d2a69e6da5a8cffea70a62bf64ab7029caebedcf1cd84369
  after : eb15d4d54ff8e079caef1836f7cbcdc217db6a1e5e1ae35c5d4637814f558dfca0e4748ba4c3ccfdd1e85731f4f22084c8c308b163a7cc0102c48b619f451aaa
```

本Status FileはAppend-only新規Eventであり、既存Historyは変更していない。

## 8. Verification

```text
Target:
  tests/unit/documentation_rag                 28 passed
  tests/unit/conversation                      28 passed
  tests/unit/web/test_web_cli.py                10 passed
  tests/unit/web/test_access_profiles.py         8 passed
  tests/integration/web/test_web_app.py          28 passed
  combined specified target                    102 passed in 1.20s

Repository Full Suite:
  371 passed
  3 deselected
  48.35s

Ruff Check:
  PASS

Ruff Format Check:
  PASS / 119 files

Mypy:
  PASS / 119 source files

node --check src/margpa_runtime_llm/web/static/app.js:
  PASS / no output
```

## 9. Mutation Boundary

実施していない操作：

- Dependency Install／Update。
- `pyproject.toml`、`uv.lock`、Application Config、Deployment／Web Profileの変更。
- Model Download、Model File Read、Model SHA計算または実GGUF Smoke。
- Network、Git、GitHubまたはLightning操作。
- Project Root外のSource／Docs操作。
- `docs/project/current/`、`docs/project/shared/`、Accepted Requirements／Architecture／Governance／ADR、Phase Index、Public Docsおよび既存Historyの変更。
- `models` Symbolic Linkの追跡。

Testは`PYTHONDONTWRITEBYTECODE=1`およびPytest Cache Provider無効で実行した。最終Mypy Cacheは`/private/tmp/margpa-runtime-llm-mypy-cache`を使用した。

## 10. Scope Observations

- Exact Main Model Token Counterは未接続であり、本Statusは保守的UTF-8 byte fallbackを正本Evidenceとする。
- Initial implementation以前から存在した`__pycache__`は観察したが、削除・編集していない。
- Manual AcceptanceはNo-Goのままであり、次の行為は設計統括者役の再Review後に限る。

