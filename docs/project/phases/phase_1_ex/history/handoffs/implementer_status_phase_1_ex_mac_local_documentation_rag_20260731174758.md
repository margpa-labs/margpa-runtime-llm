# Phase 1-ex Mac限定簡易Documentation RAG 実装者Status

```yaml
document_id: implementer_status_phase_1_ex_mac_local_documentation_rag
phase: phase_1_ex
status: repository_implementation_completed_review_and_manual_acceptance_pending
language: ja
reserved_snapshot: 20260731174758
created_at: 2026-07-31 18:26:50 JST
owner: 実装者役担当Task
target_role: 設計統括者役
implementation_environment: local_macos_arm64
```

## 1. Result

Accepted Handoffの範囲で、Local Mac Web Runtimeへ追加Dependency、追加Modelまたは永続Indexを使わない簡易Documentation RAGを実装した。

```text
Local Mac:
  Access Capability = eligible
  Server Adapter = local lexical available
  UI Turn Default = OFF

Basic Preview:
  Access Capability = eligible
  Server Adapter = not bound
  Effective State = unavailable

Public Demo:
  Access Capability = denied
  Server Adapter = not constructed
  Request Override = rejected
  UI Control = hidden
```

Repository実装、自動TestおよびModel非Loadの実Corpus性能計測は完了した。実GGUFを使うRAG Model SmokeとBrowser Manual Acceptanceは未実施であり、完了扱いにしていない。

## 2. Read-only Authority Evidence

実装前および最終突合時に次をRead-only参照した。

```text
docs/project/phases/phase_1_ex/requirements/mac_local_documentation_rag_requirements_ja.md
  7ef26d2458ef481d47b0fa53dc5e8ec7e9da1d81c29bc35d0704245eb6cccb97b2ddfcc64e8a15b2071e3ea66a0eebe16fa081979d17f14eed791a4b1c6999be

docs/project/phases/phase_1_ex/architecture/mac_local_documentation_rag_technology_selection_ja.md
  56203c926ccf5cc99b04f3db210f1fb46aaedcccf30d55df70f5e3177f6b9970632ad1e87f8c7aa5a427561c43a5a34fbb88ef817a42ea91b2c68534ff347f53

docs/project/phases/phase_1_ex/architecture/mac_local_documentation_rag_architecture_ja.md
  0c7a27dd0cfa707a12654416576e357a49c52dc908b73a6d9dfc7ba1c85738c39ab46623a6e3fbaedd2a842b5486b5d6039272e1edb6a4f74aed43a317b49b0a

docs/project/phases/phase_1_ex/adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md
  d2bee3efabbf8a7a025ba2fa4d6da462bbcb85160a5fa2458a9ff7996df0bbcfbbbfdb74d9d7516b0311b7c54309686646f2b9e962a8fe4c59c234ecc8fa2f9b

docs/project/phases/phase_1_ex/adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md
  fe9c9103a0b8f646b782b0f15a54504fdc755a54a69dd0cb7e3baa390453cb77f3bbc9b4a8a0eab1b2435c35089120614a3d283d55c0b60d11a6c3c4c5d12dd6

docs/project/shared/conventions/documentation_rules_ja.md
  d4a786e195a3640f391830225828d5c38f7846b44fd8ba4db6ab6b13ff8399bf35cbdce89d40554596e800f81fdb5a40d9e9962164a8ecca9775b71b27b3e095

docs/project/shared/task_roles/task_role_write_authority_policy_ja.md
  c71841aaac0896d560d1f5d8e509737c7d50427c2fbeb452053dd9801092a14a70788eb82200d1a4ba781237103366990f7b9ae18b20628dc7f180656bab2e0a

docs/project/shared/operations/research_asset_mutation_control_ja.md
  eafebff8f2aa6c62e1626792d7bc6dfc5cb71e3295adce3098565717aa47a377271ff7fc067587b6ca2ee1c8d418fd5a56793cda1500be3713a16a1920eb1dd4

docs/project/phases/phase_1_ex/phase_index_ja.md
  67fff441677412c4e5e2aec2f951b597247ad5ee797497ba564d913eef58dec211237bbdb2a5d6adb5facfa829f662cd423a3a5023ea7c9d164458ba40c0478e

docs/project/phases/phase_1_ex/history/handoffs/implementer_handoff_phase_1_ex_mac_local_documentation_rag_20260731172259.md
  3e910e040948bccd6ed81f79050547265709851091c086bcf19b7d16e7bb728d151cb42a503eb220a03a7ed994782d82e155e47639fd4555cfc1e5619c80493a
```

Accepted Design Digest 4件はHandoff記載値と一致した。

## 3. Implemented Contracts

次をFramework非依存Portとして追加した。

```text
DocumentSourcePort
ChunkerPort
EmbeddingPort
IndexStorePort
RetrieverPort
ContextAssemblerPort
CitationPort
RagOrchestratorPort
```

初期Pipelineは`EmbeddingPort`を呼ばない。Dummy Embedding、Main Model流用、Hidden Downloadまたは外部APIは実装していない。

実装した主なContract：

- Immutable Pydantic DTOによるManifest、Document、Chunk、Retrieval、Context、Citation、Evidence、Augmentation。
- Project相対PathだけをDomain／SSEへ返すPath境界。
- SHA-512 Document／Corpus Manifest／Chunk／Query／Profile Evidence。
- System所有の非信頼Reference Message。
- Retriever Resultだけから生成するSystem Citation。
- Raw Query／Raw Document本文を含まないEvidence Metadata。
- Local／Basic／PublicのCapability、Adapter Availability、Request Selection、Corpus Availability分離。
- Future Embedding／Dense／Hybrid／Persistent／External Adapter用Port Hook。

## 4. Config Contract

新規：

```text
config/feature_profiles/documentation_rag_defaults.toml
  schema_version = "1"
  profile_key = "documentation-rag.defaults"
  default_mode = "disabled"

config/feature_profiles/local_documentation_rag.toml
  schema_version = "1"
  profile_key = "local.documentation-rag.lexical"
  provider_key = "local_lexical"
  active_phase = "phase_1_ex"
  completed_phases = ["phase_1"]
```

Default：

```text
max_documents = 512
max_file_bytes = 4 MiB
max_corpus_bytes = 32 MiB
max_chunks = 20000

target_characters = 900
overlap_characters = 120
maximum_characters = 1600

top_k = 4
max_chunks_per_document = 2
minimum_score = 0.1
bm25_k1 = 1.5
bm25_b = 0.75

maximum_tokens = 768
minimum_useful_tokens = 128
safety_margin_tokens = 512
fallback_maximum_characters = 2400
```

`config/application.toml`は変更していない。既存Schema Version 3とLightning Preflightの固定契約を変更せず、Portable Request Defaultを独立Configへ置き、Local CompositionからRuntime Snapshotへ注入した。

`pyproject.toml`および`uv.lock`も変更していない。

## 5. Corpus Contract

Default Include：

```text
docs/project/current/**/*.md
docs/public/**/*.md
docs/project/phases/phase_1_ex/phase_index_ja.md
docs/project/phases/phase_1/**/*_ja.md
```

Default Exclude：

```text
**/history/**
**/lossless/**
Hidden File
.DS_Store
Backup
Archive
Temporary File
Symbolic Link
Project Root外
Allowlist Root外
Non-Markdown
UTF-8 Decode失敗
Limit超過
```

CandidateはProject相対PathでSortし、既知除外対象はDocument上限へ算入しない。各Requestで相対Path、Sizeおよび実Content SHA-512からExact Manifest Digestを再確認する。

実Corpus Smoke時：

```text
eligible_documents = 20
warnings = []
```

## 6. Algorithm／Index Version

```text
Document Source Schema:
  1

Chunker:
  key = markdown_heading_chunker
  version = 1

Tokenizer:
  key = unicode_japanese_ngram
  version = 1

Retriever:
  key = field_weighted_bm25
  version = 1

Context Assembler:
  key = bounded_untrusted_reference
  version = 1

Citation Schema:
  1

Feature Profile Schema:
  1
```

Cache KeyはCorpus Manifest Digest、Feature Profile Digest、Source Schema、Chunker、Tokenizer、Retriever、Context AssemblerおよびCitation Versionを含む。

Index Snapshotは次をMemory内だけに保持する。

```text
index_id
cache_key
corpus_manifest_digest
chunker_key／version
tokenizer_key／version
retriever_key／version
document_count
chunk_count
built_at_monotonic
immutable lexical payload
```

Lazy Cold Build、single build lock、完成後Atomic Replace、Manifest／Algorithm変更時Rebuild、失敗時Incomplete Index非公開を実装した。Disk Indexは作成しない。

## 7. Retrieval／Context／Citation

- Unicode NFKCとLatin casefold。
- 日本語Character 2-gram／3-gram。
- Latin／digit／underscore／dot／slash／hyphen token。
- Body、Heading、Path、Exact Phrase、Corpus Priorityの独立Weight。
- Accepted Tie-break順を固定。
- `max_chunks_per_document`によるDocument Diversity。
- No Hit時は空Citation＋Safe Warningで通常Generation継続。
- Context上限はInstruction、Path、Heading、Markerおよび本文を含むReference Message全体へ適用。
- Budget超過時は低順位Chunkを除外し、採用Chunk本文を無秩序に切断しない。
- Docs内Reference MarkerをEscape。
- CitationはRetriever採用結果とContext採用BlockからSystemが生成。
- Model生成Citation文字列をSystem Citationへ昇格しない。

Main Model TokenizerはIndex／Model非Load境界ではBindingしていないため、初期Local Adapterは保守的な2,400文字Fallbackを使用する。

## 8. Conversation／SSE／UI

- 最新User MessageだけをRetrieval Queryにする。
- RAG本文をUser Messageへ連結せず、Conversation System Policy直後の`documentation_reference` System Messageへ分離。
- SSE Retrieval EventをModel Deltaから分離。
- Assistant TurnへState、Citation、Index RebuildおよびSafe Warningを関連付け。
- Summaryは一度だけRetrievalし、Original Citationを完了Eventまで維持。
- RetrievalをSSE Session内で開始し、先に`retrieving_documentation`とRequest IDを返す。
- Stop要求をRAG OrchestratorへCooperative Cancellationとして渡す。
- Retrieval中もModel Busy Gateを維持し、終了時に解放。
- Docs不在時は指定文言を返し、Model Callを開始しない。
- Assistant本文Copyは本文だけ。Citation Path Copyは別Button。
- Citation、ConversationまたはCorpus DataをLocal Storageへ保存しない。
- Browser Reload時はServer DefaultおよびHTML DefaultのOFFへ戻す。

## 9. Access Matrix

| Surface | Capability | Adapter | Request Default | Effective／Override |
|---|---|---|---|---|
| Local Mac | eligible | local lexical | OFF | available。Turn単位ON可 |
| Basic Preview | eligible | not bound | OFF | unavailable。ON拒否 |
| Public Demo | denied | not constructed | forced OFF | denied。ON拒否、Control非表示 |

Public／BasicへMac Filesystem Adapterを暗黙転用していない。

将来AWS／Azure等へ移行する場合も、認証Login、公開SurfaceおよびDocumentation RAGを独立Adapter／CompositionとしてBindingする。今回Cloud、Lightningまたは外部Adapterは実装していない。

## 10. New Files and SHA-512

新規FileのBeforeは`absent`。

```text
config/feature_profiles/documentation_rag_defaults.toml
  before: absent
  after : a373c8aa49992b1f616c99bfe3e590cbf4c469254b2e5cfd477438934ccdb220587ee5dcab61128b0135d229ca58600ef67f5cb2f7e8c29ddca376735ab149db

config/feature_profiles/local_documentation_rag.toml
  before: absent
  after : cb7e937ffcb00a6cd181727c322356d54f00bba14149d4db7bf41e5a20db33d82091dd7b90f4a6b30d49a1ed473930ed6dc43c61562e747054b4dcf8aca92f31

src/margpa_runtime_llm/modules/documentation_rag/__init__.py
  before: absent
  after : fa6fe2f616034905d4089b6bd0c658f7cd6c4a55ec658e7fc2c8b1cef1a7dc893c32cb29d6ac6a8fafd77c34bb187c871d42b3f3077289893e8bae08e388e384

src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: absent
  after : 5f9982ef5b00c75d7d3bd0c5ec7e8e95164ddb9175e025173d99cb2065a78da9fd56888e31f86bf3cd2b52faef4f2f1147d26cb95fe77065d4650ad088996fb6

src/margpa_runtime_llm/modules/documentation_rag/ports.py
  before: absent
  after : a9c0170cbf1408967089ade477545883eaff3df3854e18aab5e7b4c208777da464c2959c781685379271ac8e21c0a8295245ff002e919be6146f71e49eea14f1

src/margpa_runtime_llm/modules/documentation_rag/public.py
  before: absent
  after : 9457c44f7f3a68a94317eced66a1c2fda614377dc7d2c331914f3909da51f4458217696c492b5fc55ad201b77cee06f256bc45445911d86f60202aedce3e057e

src/margpa_runtime_llm/modules/documentation_rag/application/__init__.py
  before: absent
  after : a1a1955c74821d366018d0d4c672aba83fc4312cd8fdf9bfd7449fca38f640b575d5bff32d1568111b647bf936d101e7c5773e172847eec6dd914141a8593318

src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
  before: absent
  after : ed709f5e0913382bcb7bff1ee04f080a46b5f300786df68f7b08733b3baea97cd503b975ba3e26e5fa7f782ebe5adfb1165871473e44bc7647d1fd0721833955

src/margpa_runtime_llm/adapters/documentation_rag/__init__.py
  before: absent
  after : e4e64eac53f4b0dc84e43a33bf961b56f352885baee46d2fe127746d39acb10326d2490878ecea21b6067763b90f7fb4d662993f59e5a78f95a6b6c80db9eea1

src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
  before: absent
  after : 19dc86a0eb0dcc5aacc570d474d2fbf18fc730eb827f750b89c4769bb49e70e66941668c488aa72530dbc7207d69086f04df7822224262021965d2ca6e96dd09

src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py
  before: absent
  after : 3871902d5f217dfa2c3585495222a30b146b031b96ae3a17b0f6ef6b0431bef9de62e6210f60d733e5279af82c7d45899328dd189c5dc99f01b24bd851024741

src/margpa_runtime_llm/adapters/documentation_rag/in_memory_lexical_index.py
  before: absent
  after : 7c56eb2c247b30024fafbc7f7a6617404b4736579aece898f2d86f200b6776f6b442c7571935ac44e170456ac49f97f9ca7f540ef751a0f82cc1b65b00752f1f

src/margpa_runtime_llm/adapters/documentation_rag/lexical_tokenizer.py
  before: absent
  after : 12064b449c474c29f22462a5b8c4c629fd2ad86e6e218c3741d2c50214b195a005931fd012b2cb8c3b14c3199c74644b9263b50c80a6dec3e27ee2758bc3bb49

src/margpa_runtime_llm/adapters/documentation_rag/local_filesystem_source.py
  before: absent
  after : 899e6c65fff3888ebcb267f52a542275484bfb66305f98a84cccefda85ca12766da7957675a646fe3342f6e079c94d59ec9bcba72cc2c5c9f1cd1356d1346d4a

src/margpa_runtime_llm/adapters/documentation_rag/markdown_chunker.py
  before: absent
  after : 7968333e47dfced7ef1f0e4abb0a32ee25a51cf4643ef5964d1f2f27f7b81cf98b9da3ed52358385c35d7df8b8c50e4719675e045f2f3685d50478111b2e0a69

src/margpa_runtime_llm/adapters/documentation_rag/system_citation_adapter.py
  before: absent
  after : 74278a452956a1857f13ad454a320f96d15d7e636caa8b2d15def204ba1bb6a3c68edb5310ea83b6f87ffd84fa9386b3a6817de007ad9d8907b5ccd03213293d

src/margpa_runtime_llm/bootstrap/documentation_rag.py
  before: absent
  after : 3d510de2493c1cca84596c64ef0e399f03400db0976a4aca3c3358a2a751b2af017d70ad9e73103bc6aa48d6c34922d84953f4435a612e30686a0c220a5dc621

tests/unit/documentation_rag/test_bootstrap.py
  before: absent
  after : 7b5c4e4461af57de278a104b5a5046d53b4c9f34f073f6babb7116d8a4f0542f858879a415a7e7f3188ba7fa413dfff68ef52a1dbfaf232ea91f11b7d269b4ab

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  before: absent
  after : 37ef26f7e82d8bff769bbaa8ab8c02f4902d84d044909fe1f57b49b75e7fc34c3293f03c916ff0a7039295de035f3401acc9c1ad2a8a9b09a71672ed6a66a7f7

tests/unit/documentation_rag/test_lexical_retrieval.py
  before: absent
  after : b68abd7b39e0f4402089335e6e431a69ee337d47ee2ff96cea0dc04e68d50d55c2d872eb522e63d2d134ab281778c5e3d6f0293c2c8b8423216a90351869ed73

tests/unit/documentation_rag/test_local_filesystem_source.py
  before: absent
  after : b95b17c686c0912f568b4e5230319044b1b81cfaa3c3bad4e6e7c0ac695b07d4dd57f39d49b41c562826766006995386b7e83e537847e1bba61f2f6002b168e3

tests/unit/documentation_rag/test_markdown_chunker.py
  before: absent
  after : 729770fec285ec80d680b6b1eacd7afa6caf9e7635e80793aa72062df019d884454b53d8164fe0b4ba29c496f7d3feed4786b065d561e83df93e54ffdbcfc671

tests/integration/documentation_rag/test_conversation_rag.py
  before: absent
  after : 6b22b84c1c222fb9c277370c37cc7b315161671363ca14a11a3ce58770f90aecb46a639da5ef3daf5c148e56f1ea84235485724afd27bd7332d9c939fa26f1c3
```

New File SHA Listing Manifest Digest：

```text
dc9292d3ad72560c26ded7ccd93243bd51e782510802bb858c9956d1743a95650372993f70b9adb608e45dcfdf0a21dddbcb292456e5d7297e6da7103c05a279
```

## 11. Existing File Mutation Evidence

```text
src/margpa_runtime_llm/bootstrap/web_application.py
  before: 7dc562… (Phase A capture prefix)
  after : 2d16b936d516dbc6037d966abb12122a7964b15f358488b40168f373f8eba0fdc9b9de1cf7648cce95ae3d6fa3575f83e5fccc0a0b8c8867d6cebf4f0389abb8

src/margpa_runtime_llm/entrypoints/web/main.py
  before: ececf838ae27200ca662b2278c5ee30ad657e6b223bee7e22ff0cd65661a4186eaa1bbcd34713aeb41175aa1d7c69414d74d3207caa581fb17638d150f305972
  after : a1602df5ba7a0f68232164f382211666174d813cf953ddd0a93e4e75ae000c6649720606cfa8de12f3c64000ed04f9167e9fe9ff72c6aa5a15309f81a2e717fe

src/margpa_runtime_llm/modules/conversation/contracts.py
  before: 17050e… (Phase A capture prefix)
  after : ac005fa478be8dc791109089d33c8caa4220e92f0362d05828974c74fdaa1594af8643344769758b38d82de537f84551ee2ae9edab7a94919aee37d98df4bf89

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  before: c15a8c… (Phase A capture prefix)
  after : 1a7de791d49390fcaa4e4e7658c1f9dc7a5e9414c907c34069e524e22566e137b88bc0508431a390cb31ebfffdcd45a48baa93457cab68f916c9be912737a3dc

src/margpa_runtime_llm/modules/conversation/public.py
  before: 34d5ee… (Phase A capture prefix)
  after : 038369b61b4573d225e27c7ce006b334ece2156943865adb5e03095d7490074d89c6c2644fd3f195e904e3f7471f568343270290a4c42ba68708e422878180a3

src/margpa_runtime_llm/web/access_profiles.py
  before: b91d4420bb9b822607e7d23147b41f09b9c19239fa3bfe71ebcf21d8856f3b030067a682b0ebd6630d6f5f1a38b5fa7f635de9df890193926963785fa60b84ba
  after : 554eaf66f4243608063a7cd9eecd02dd4ee8e65d5f40d553322c7c33c1877a7eec4e892e89211fa3d00dff5f60093f178442953e848fe23c1bed252124e4805b

src/margpa_runtime_llm/web/contracts.py
  before: ddd964… (Phase A capture prefix)
  after : 16f7b2ce132ce4aaeffff8f0ec51787f5ea61440e76687a899e74c3f49e4b32972b1de31097463a534c4788e61917ef62f62a351bfe122b5f0283dac99483928

src/margpa_runtime_llm/web/static/index.html
  before: ec13c8b2a98d5416a1a6f5949fc0c27127636781a5d9479523075d390c079b49ea428f5de9268f547f345d20cf822ceabb9f11baecb7cd589a34e888393c3e8b
  after : 276f211d801d4dbae8992bbe7ed9888665f62ffc87dfeaf511da3cb66e9ee922ec85a6ee7e1bb1f70dd82f8f38c7a4dbaedb9dc545ce9b6e6a213cc9d3a7ed8f

src/margpa_runtime_llm/web/static/app.js
  before: 440b414267786c38f6edc61b023b5a4004643681b3ee3ce5fb4995b2a1fa2ee7b3cb754deac4cc18b2066a60765c3122ebcb5e31b810d6fb1ea0053030aaaf11
  after : 120ed5e45a25dd932c3422542eb24770d693c008ea2b968a86acc9dadc943166d63a5fe56d3be35336e90243f1fb875d98608308c78129705d1e358d8eb9a003

src/margpa_runtime_llm/web/static/app.css
  before: edb549… (Phase A capture prefix)
  after : 898259c0971ea448db9c0e4fb9d34447010bd4a54bfad2adceccab147618c60b5ba9a8ebe0d2bfce13f7161c957b79f930a423e3a35b87532e42f8f88b99883c

tests/unit/web/test_access_profiles.py
  before: aa83057f7c9b100ba49473a7b34306ec320be4b389df996876e6c56ef4904a98fc88ea66fe3e187e6a832e8a5b42912204aba7c13a8332fea1aba71d8870c5f1
  after : 66a589c2448101743cb199b506a9a4bd718790d4ea0136284746e3241b38a724109531918ef58648a95e5a77ec4543eded5e64f0b6b8c091038be8a28a009120

tests/unit/web/test_web_cli.py
  before: bf53af32f581a23eb8fc6845c500a83e225837f79aee9e7ee9165c28fec95b1e275f0007c16825ebad13c4838a148b62400961a4197ddcbfb86e1e52e6dc52ed
  after : 19a746c8b7b7a062c9c7af4bc5cf0afa520306643674d53bdee9fe55f664e262c0a154e1a87238938d2a77b6c46216dab377eb73b371805bee9249fae9c791ad

tests/integration/web/test_web_app.py
  before: 06d7a14cc6992474c09909b1a10fa5cebc1d51c9e04eefbf840e65efc2d82c01c1382163689d26c6ab7061a5d3b4f23dcd72c9d381c43d430362fbd036b6773d
  after : aa0cb4d7c8614f48e9d4bf8b3c57da1599fdc8a107283aa9521442a1ac55ec5698af02cc42f9a237d2a69e6da5a8cffea70a62bf64ab7029caebedcf1cd84369
```

Phase Aでは上記13変更Fileと、候補だが未変更だった次の1件を合わせた14 File Manifestを取得した。

```text
tests/unit/conversation/test_conversation_generation.py
  before／after:
  356ac1f806118b087b06d01464a9ed822e78c84a14fa0b86d60cc9e607aa56c18af7e76b1d24855ffb3c27e39840467b41f26fae19104373533ce9e546cc8f41
```

14 File Before Listing Manifest Digest：

```text
ac6bde627d4561e6bb6104a19f4fcb16bba4db0609dd5980de166d609cd2842f8e20a53e3f948003c904c453a87c513586756d7f128c2ecdc0428ffff40517c0
```

14 File After Listing Manifest Digest：

```text
839cf6ce9035688023a97d787e3ead21693667443435f28ec418f489b3ea754c938f1dcaed2c4ef97b466e108c98c63b08c3f0452e7c2d129eb3928d18e7a965
```

Preflight時に一度提示した`e9be…`は、未変更候補3件を混在させた17 File ListingのDigestであり、14 File Mutation Candidate Manifestではなかった。Mutation開始前に対象を再固定し、正しいBefore Listing Digestを`ac6bde…`へ訂正した。

なお、既存6 FileについてPhase Aで個別Full SHA-512を計算したが、Task Context自動圧縮後にFull値を再参照できず、上表では保持されたPrefixと14 File Aggregate Digestを記録した。これはEvidence保持上の既知不足であり、値を推測して補完していない。ユーザー取得済みBackupから個別Full値を再取得できる場合は、既存Statusを編集せずFollow-up Statusで補足する。

## 12. Verification

全CommandはProject Rootで既存`.venv`を使用し、`PYTHONDONTWRITEBYTECODE=1`、Pytest Cache Provider無効、Ruff `--no-cache`および承認済み一時Pathを使用した。

```text
Targeted Conversation／RAG／Web:
  61 passed

Full pytest:
  359 passed
  3 deselected
  duration = 49.81 seconds

Ruff format --check:
  119 files already formatted

Ruff check:
  All checks passed

Mypy:
  Success: no issues found in 114 source files

Metal Backend Integration:
  tests/integration/test_llama_cpp_metal.py passed
  llama.cpp GPU Offload／MTL support confirmed
```

主な自動確認：

- Project Root外／Allowlist外／Symbolic Link拒否。
- History／Lossless／Hidden／Backup／Archive／Temporary除外。
- UTF-8、File／Corpus／Document／Chunk上限。
- Absolute Path／Raw Content非露出。
- Heading、Breadcrumb、Code Fence、Overlap、Chunk再現性。
- NFKC、日本語2／3-gram、English／Identifier。
- BM25 Field Weight、Priority、Tie-break、Minimum Score、Diversity、No Hit。
- Cold／Warm、Manifest／Tokenizer Version Rebuild、Concurrent single build。
- Build Failure Atomicity、OFF時No Call／No Build／No Write。
- Message全体Context Budget、Marker Escape、System Citation。
- RAG ON System Reference、Latest User Query、Summary Retrieve Once。
- Docs Missing指定文言とNo Model Call。
- Retrieval中Cancel、Model Busy、Gate Release。
- Local UI、Default OFF、Reload Default、SSE Retrieval、Citation Block。
- Basic Eligible／Unavailable。
- Public Denied、Override拒否、起動時Adapter非生成。
- Existing Conversation／Thinking／Language／Summary／Stop／Web Regression。

承認済み一時Path：

```text
tests/.verification-tmp-mac-local-documentation-rag/
```

検証完了後に正規化済み実体Pathを再確認し、Directoryごと削除した。回収可能性を前提としないTest Artifactであり、現在は存在しない。

## 13. Performance Evidence

実Projectの許可CorpusをRead-only参照し、ModelをLoadせず、同一Process内で計測した。

```text
query:
  Nazuna Research Governance LLM Documentation RAG

documents:
  20

selected_chunks:
  4

cold:
  1.038241 seconds
  index_rebuilt = true

warm:
  0.081251 seconds
  index_rebuilt = false

additional_resident_memory:
  152.422 MiB

manifest_stable:
  true

warnings:
  none
```

Accepted目標との比較：

```text
Cold <= 10 seconds:
  pass

Warm <= 1 second:
  pass

Additional RSS <= 256 MiB:
  pass
```

Model生成時間は計測していないため、RAG処理時間と混在していない。

## 14. Model Smoke

実施：

```text
llama-cpp-python Metal Backend Integration
  pass
```

未実施：

```text
Existing GGUF Model Smoke
Documentation RAG GGUF Model Smoke
```

理由：

- `models`はProject Root外を指すSymbolic Linkである。
- Accepted Handoffは`models` Symbolic Linkを追跡しないよう明示している。
- Full pytest既定設定は`model_smoke` 3件をDeselectする。
- Model Artifactを読むための権限拡張、CopyまたはDownloadを行っていない。

## 15. Manual Acceptance Procedure

実操作はユーザーが行う。

1. Local Macで次を起動する。

   ```text
   .venv/bin/python -m margpa_runtime_llm.entrypoints.web.main --host 127.0.0.1 --port 8000
   ```

2. Browserで`http://127.0.0.1:8000/`を開く。
3. Runtime情報が表示され、`プロジェクトDocs参照／Project Docs` Controlが表示されることを確認する。
4. 初期値がOFFであることを確認し、通常Chatを1 Turn実行する。
5. ONへ切り替え、Project概要を質問する。
6. Roadmap、Architecture、`ARGD`等の英語略称を個別に質問する。
7. 各Assistant TurnでCitationのProject相対PathとHeadingを確認し、Path Copyを確認する。
8. No Hit用の無関係Queryを送り、空CitationとSafe Warningの後も通常Chatが継続することを確認する。
9. Summary Mode ONで、Citationが一度だけ検索され完了後も維持されることを確認する。
10. Cold Retrieval中およびModel生成中にStopし、停止後の次Turnが開始できることを確認する。
11. New Chatで画面内ConversationとCitationが消え、新しいTurnへ混入しないことを確認する。
12. RAGをONにした後Browser Reloadし、OFFへ戻ることを確認する。
13. 設計者許可済みDocs変更が別途行われた場合だけ、次のON Requestで`index_rebuilt=true`相当の再構築が起きることを確認する。Manual TestのためにCanonical Docsを変更しない。
14. Public Demo ProfileではControlが表示されず、形の正しい`documentation_rag_mode=enabled` Requestも拒否されることを確認する。

## 16. Known Limitations

- 初期RetrieverはSparse／Lexicalのみ。Embedding、Dense、Hybrid、Semantic Rerankは未実装。
- 日本語はCharacter 2／3-gramであり、形態素解析は行わない。
- IndexはProcess Memory内だけで、Process Restart後の最初のON RequestでCold Buildする。
- Exact Manifest要件により、Warm Requestでも許可DocumentのSHA-512を再計算する。
- Main Model TokenizerはRAG AdapterへBindingせず、Context Budgetは2,400文字Fallbackを使う。
- Provider／Corpus Policy変更はProcess Restartが必要。Turn単位OFF／ONだけRuntime変更可能。
- RetrievalはCooperative Cancel。Filesystem／Chunk境界で停止を確認するが、実行中の単一CPU処理を強制中断しない。
- CitationはSystem由来Metadataであり、回答内容の正しさ自体を保証しない。
- AWS／Azure／Home Server／Lightning用External Docs Adapter、認証Login連携、公開Surface連携は未実装。
- 既存File 6件の個別Before Full SHA-512は本Status内でPrefix＋Aggregate Evidenceとなっている。

## 17. Scope／Mutation Boundary

行っていないもの：

```text
Dependency Install
Model Download
Model Artifact Read
Persistent Index
External API
Network Access
Lightning操作
Cloud操作
Git操作
GitHub操作
config/application.toml変更
pyproject.toml変更
uv.lock変更
config/models変更
config/profiles変更
config/web_profiles変更
scripts/runtime/lightning変更
README変更
docs/public変更
docs/project/current変更
docs/project/shared変更
ADR／Requirements／Architecture／Phase Index変更
既存History変更
```

Project Root外を明示走査、作成、変更または削除していない。`models` Symbolic Linkを追跡していない。

新規Docs書込は本Status 1件だけであり、Accepted Handoffが許可した次の配置へ新規Eventとして作成した。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_mac_local_documentation_rag_20260731174758.md
```

## 18. Review Request

設計統括者役へ、次をReview依頼する。

1. Port／Config／Access Capability分離。
2. Corpus Allowlist／Exclusion／Path境界。
3. Sparse BM25、Versioned CacheおよびAtomic Index。
4. System-owned Reference／Citation／Evidence境界。
5. Retrieval SSE／Cancel／Summary Integration。
6. Local available＋Default OFF。
7. Basic eligible／unavailable。
8. Public denied＋Adapter非生成。
9. Test、PerformanceおよびModel Smoke未実施理由。
10. Before SHA-512個別Evidence 6件のFollow-up要否。

