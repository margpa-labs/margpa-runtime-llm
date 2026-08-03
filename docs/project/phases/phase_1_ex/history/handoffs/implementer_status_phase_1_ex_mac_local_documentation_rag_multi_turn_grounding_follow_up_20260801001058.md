# 実装担当 Phase 1-ex Mac Local Documentation RAG Multi-turn Grounding Follow-up Status

```yaml
document_id: implementer_status_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up
phase: phase_1_ex
status: implementation_complete_waiting_designer_re_review
language: ja
created_at: 2026-08-01 00:10:58 JST
owner: 実装者役担当Task
source_index: documentation_index_20260731231940.md
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_1_20260731231940.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260731231940.md
backup_confirmed_by_user: true
manual_acceptance_performed: false
```

## 1. Result

```text
F8 Exact Chat Prompt Token Counter       : RESOLVED IN IMPLEMENTATION
F9 Retrieval-hit / No-context Fail-close : RESOLVED IN IMPLEMENTATION
F10 Multi-identifier Coverage            : RESOLVED IN IMPLEMENTATION
F11 Grounding Instruction                : RESOLVED IN IMPLEMENTATION
F12 UI / Evidence State Separation       : RESOLVED IN IMPLEMENTATION
Required Automated Verification          : GREEN
Real Corpus Read-only Smoke               : GREEN
New-diff Local GGUF Manual Acceptance     : NOT PERFORMED
Designer Re-review                        : WAITING
```

本Follow-upはF8～F12だけを対象とした。Dependency、Config、Model Artifact、Public Demo／Lightning、Accepted DocsおよびCorpus Allowlistは変更していない。

## 2. F8～F12 Before／After

### F8 Exact Chat Prompt Token Counter

Before:

- Conversation LayerがSystem／History／Current PromptのUTF-8 Byte数をExact Token数として扱っていた。
- Loaded ModelのChat Templateと`thinking_mode`を含む同一Formatting PathをBudget計測に使っていなかった。

After:

- Optional Narrow `ChatPromptTokenCounterPort`を追加した。
- llama.cpp Adapterは既存`format_prompt(messages, thinking_mode).token_count`を使い、同じLoad済みModelとGeneration Lockで計測する。
- Inference ServiceからBootstrap経由でConversation Serviceへ注入する。二重Model Loadは行わない。
- Exact Counterが利用できない場合、UTF-8 Byte推定に戻さず`documentation_prompt_measurement_unavailable`でFail closedする。
- Evidenceは`base_prompt_used`、`base_prompt_unit=tokens`、`base_prompt_exact`を保持する。

### F9 Retrieval Hit／No Context

Before:

- Retriever Hit後にAssembled Blockが0件でも、参照なしの通常GenerationへFail openする可能性があった。

After:

```text
retrieved_chunk_count > 0
assembled_block_count == 0
grounding_state = context_insufficient
generation_allowed = false
should_generate = false
warning = documentation_context_budget_insufficient
model call = 0
```

True No Hitは`grounding_state=no_hit`とし、一般Chat継続を維持した。Pydantic不変条件でGrounding State、Retrieved Count、Assembled Count、Citation CountおよびGeneration Decisionの不整合を拒否する。

### F10 Multi-identifier Coverage

Before:

- Overall BM25 Rankingだけで最終Selectionし、複数Identifierの一部がTop Kから脱落し得た。

After:

- Query AnalyzerがDistinct Top-level Identifier Subjectを一般則で取得する。
- SubjectごとにHeading Exact、Path Component Exact、当該Subject単独のBody Matchの順でCoverage候補を確保し、残り枠を従来のGlobal Scoreで埋める。
- 複数名をBodyに列挙しただけのGeneral Document一件を、全Subject Coverageとはみなさない。
- BM25 Score、Corpus Priority、Document Diversity、Minimum ScoreおよびTie-breakを維持した。
- Production CodeにProject固有略称をHard-codeしていない。

```text
GenericNaturalLanguageQueryAnalyzer version : 1 -> 2
Bm25DocumentationRetriever version          : 3 -> 4
```

### F11 Grounding Instruction

System-owned Reference Instructionに次を追加した。

- Project固有の正式名称、略称展開、定義およびSystem間関係は現在のReferenceを根拠とする。
- Previous AssistantはProject Authorityではない。
- Referenceにない略称展開や関係を創作しない。
- 質問された定義がReferenceになければ根拠不足と明示する。

Docs内の命令、System Prompt、権限要求およびTool実行要求を非信頼とする従来境界は維持した。Judge／Repairは追加していない。

### F12 UI／Evidence

UIとEvent／Evidenceで次を区別する。

```text
no_hit                      : Docsに対応根拠なし、一般Generation可
context_insufficient        : 根拠は取得したが余力不足、Generation拒否
unavailable / docs missing  : 既定Safe Message、Generation拒否
denied                      : Access ProfileでControl非表示／Request拒否
prompt measurement failure  : Exact計測不可、Generation拒否
```

日本語／英語Messageを同時に定義し、Citation 0件だけで原因を隠さない。EvidenceはRaw Query、Raw Docs、Absolute Path、Model ObjectおよびSecretを保持しない。

## 3. Mandatory Fixture Results

### 3.1 Long Japanese Multi-turn

Deterministic Fixture Counterで、UTF-8 Byte数とToken数を別の単位として固定した。この数値は実Model Token数の代用主張ではなく、Byte数をExact Token数にしない回帰Fixtureである。

| Turn | Subject | Fixture Prompt Tokens | UTF-8 Bytes／Not Tokens | Documentation Budget | Citation |
|---:|---|---:|---:|---:|---|
| 1 | EASA | 40 | 180 | 768 tokens | continued |
| 2 | ARGD after long Japanese Assistant | 288 | 6,131 | 768 tokens | continued |
| 3 | DLAGSA after two long Japanese Assistants | 549 | 12,384 | 768 tokens | continued |

True Exhaustion Fixtureは`base_prompt=1600`、`context=4096`、`requested_max_new_tokens=2048`、`safety_margin=512`でDocumentation Budget 0となり、`documentation_context_budget_insufficient`、Inference Stream Call 0回を確認した。

### 3.2 Combined Subject Noisy Corpus

```text
query                 : EASA + DLAGSA + OCILNS natural Japanese question
canonical definitions : 3
general list document : 1
polite distractors     : 8
top_k                  : 4
subject coverage       : 3 / 3
uncovered              : 0
repeated result        : deterministic
result                 : PASS
```

### 3.3 Grounding Boundary

Previous AssistantがARGDとEASAの虚偽の関係を記述し、Current ReferenceはARGDの定義だけを持つFixtureを追加した。Prompt Composition上、Current ReferenceがSystem-owned Messageとして挿入され、Previous AssistantをAuthorityとしないInstructionおよび未根拠の略称／関係を創作しないInstructionが含まれることを確認した。Modelが必ず従うとは主張しない。

## 4. Real Corpus Read-only Smoke

実Project Allowlist CorpusをRead-onlyで検索した。Model Generationは行わず、Documentation Block計測には決定的Test Counter、Base Promptには明示したSimulation値を使用した。Docs、Config、Index FileおよびModel Artifactは変更していない。

| Case | Base Prompt | Documentation Budget | Subject Coverage | Assembled | Grounding | Generation |
|---|---:|---:|---:|---:|---|---|
| EASA | 420 | 768 | 1/1 | 4 | grounded_ready | allowed |
| ARGD | 420 | 768 | 1/1 | 3 | grounded_ready | allowed |
| DLAGSA | 420 | 768 | 1/1 | 4 | grounded_ready | allowed |
| EASA + DLAGSA + OCILNS | 420 | 768 | 3/3 | 4 | grounded_ready | allowed |
| ARGD long-history simulation | 1,040 | 496 | 1/1 | 2 | grounded_ready | allowed |
| DLAGSA long-history simulation | 1,280 | 256 | 1/1 | 1 | grounded_ready | allowed |

Combined QueryのSelected Headingは次の3 SubjectをTop K内でCoverageした。

- `Phase 10 Original R&D System Catalog > 2. EASA`
- `Phase 10 Original R&D System Catalog > 3. DLAGSA`
- `Phase 10 External Original R&D Integration Architecture > 7. OCILNS Boundary`

## 5. Existing Local Model Process

127.0.0.1:8000の既存Local Web Processを停止、KillまたはRestartせず、次のSafe Snapshotだけを参照した。

```text
healthz                 : HTTP 200
model_key               : main.qwen3-4b-q4-k-m
profile_key             : local.macos-arm64
device_kind             : gpu
acceleration_api        : metal
documentation_rag state : enabled
default RAG mode        : disabled
```

既存Processは本差分の適用前にLoadされた可能性があり、Handoffが二重Model Loadを禁止しているため、新差分の実GGUF Generation／Manual Acceptanceは実施していない。HealthとSafe Runtime Snapshotの確認は、新差分のModel Acceptanceとして扱わない。

## 6. Changed Files and SHA-512

```text
src/margpa_runtime_llm/modules/inference/ports/model_port.py
  before: 86019234320c3fdbf5b9a8698280954edc97a0dffc831ae666c9fb915248186605f851c7355df1d0701ae6e36978df7316a67f5281bd12bfdd9a4b3b577bd011
  after : 3da9c5e57a42bebe9ce1f9114843a7efa7be634611ba52d4d9067dbe310e1332a77370386f8aa922969e86866485a2026413c71ed05e4cc09eaed09fc22e210b

src/margpa_runtime_llm/modules/inference/application/inference_service.py
  before: 111b49513da339426004fabe6a9996068b568551e53c60c0b2e1699d0761c1f63103ef9be5a8fbd894fc19b90c43f8248e47fde288b90f12d06bff9ace9c84f9
  after : f9d7d3605f370b4068327fa6d4c8b8af698dce03fe9b1430ec4d58097fcb5eaaa8728f83559be54ae912cf93ae216a7c87dfc2a29ca805e826e72fa97fc50023

src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
  before: 4c8af8d10104f7d955144cc5b7fee33e00bec24893304b847a2e1bb52e507dd1110f60440a0b0b1f1268129de10862e6a11ac45fd4f332f01c8958653a06ac2b
  after : b29f6d975d2bbf9f9d3186cd51d3c9534f0aa14072be0d47878a80913bed4e19443e65edb5d4afa493e71bd31e4ac8f5ad3a684c8f76c110ba2afdfa31a8768f

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  before: f72fccbb44644571cbc355d7eac4566f08bd97d86e0e21ffe147aef62fec204aa00db7bb5dc112cd22384a97a7ce213a373aa95bf99c896987a336396500a279
  after : e9f6423f4797180de649d1c87639d0a5b3394d64e6b186de2a9a2bb06d4a71f4965a4e730a43547b00b9e34802a127b1834048766d733a3faf7640d28e8afec0

src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: 035f3027213c1d45ece2f0f1f155a45caa62533883e2a5c8111ca6d4e296b3fb413e788fc71c61f222edd6b6b633b5be43b807c853a955627dbbef63885bf634
  after : 7210b1e77a39e2c56fd4118dc1b253d5e6edc66e4ac5f387fcd0a9003077595defe30f8936225e13695f3301947808e843c845809e5f32e97b2d5516b6e9cc69

src/margpa_runtime_llm/modules/documentation_rag/public.py
  before: 1ba21cdfca2fa328a52fe5cd280102047f7954040f9ef8471805eaab2ba6b3a963175d571acad3f6da2b2c7eedf8762bb0ec6c3b696fe3aa554232a020d4fad5
  after : 7858f3d27a0d83f35ca07d7d43a164ba8aaeffc4a2d783411a3ebcb035985055a5091f96fb6c0d5b583d6899360137de122bb5f55be974cf99613e79f90c61c2

src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
  before: f7afead11876b2c2c480556f4db6ada74de5860c8b767d0614e1abfeeafd7b095e0f0a248fc91f8067e658155e1a44b1df6e9f65c19737755605c49932ce242a
  after : dcedffed036422722ac2722b693c76b58fa1055f939489d067dbfb199462726af5aec2f2e2d7aa52548569d75ca538c7ebaec2105c289dc900c50b2220d64d58

src/margpa_runtime_llm/adapters/documentation_rag/lexical_tokenizer.py
  before: 7eb817b184191ad5e3da7dff54c6e643822c80e97915fc9fc3c95341a1c28a0fad24584503920f27036e4b510b496ccc7804b350632686a76212dfbe49682019
  after : e5e4ee8a20443ef8641c723bb53d9dde183c8bf16952c2aaad9b34060e3d1e0ca39004a91768be7cc0fafd74a70e197f0d40370ab6a500425f6d63eccbbe28c7

src/margpa_runtime_llm/adapters/documentation_rag/query_analyzer.py
  before: fd6669f1b9cbb487f779371fc9c099821cbf94195959bd4f070725c2ed8099232df650f9681f11ce34fed449333018b32fa8e4dab1caf925c91e6e11e7abf8db
  after : 607eadc82b3a2fbef7b2f60b9c47233b91595fd1b0e5e3ad5d659f94dd666174c04a78409172d734f5fd3e7444dfe29466ea989ecf4bb10134b0ce389434f729

src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
  before: 53930b7275d3d2678e35b9c09fcbd641124d92b9eff2ca239d2cb9e4dad287ebb372e3cfbea1b8b8f2e951737fba70660f5e2ab35dc1eceabff46ece309e08b5
  after : fe36d508a846372777c623ac5a2d8021141fd86152320da289cc5db3f59566f095ab9640fbcdd88b30dd91610a18ea9c78577b128fce861815efc5d0a517eeb6

src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py
  before: 87eff32fa7385ce35454b5e65667761bdea6d2426452e7a260e9f9c7bc8f22d515fa3d4470d205289fa635f6b475b1651f99f20ebccdcbd10bbcfcdff18ceda0
  after : a76367e97396cab04ba63ebcc323d958da287f42d78fb797c2dfcccddf59a1c3e208fbb1e417d46b53095f430508127f50ca1075c475ff87e56268401dc0de9b

src/margpa_runtime_llm/bootstrap/web_application.py
  before: 264b94f5f5efe007efe397c603868209a3d4cb3cd6369f44ed114da68beedf151e300e3872b397f1db8132eab0fe2a3a92a7542fad929a77129c76c93f53559a
  after : 504a6c97ba9ba7485bfea959f2b3bc134943a8b6bb383591ce20dbe84f8fd451ad56e562ff5d3ea87aaf6be359de3f2148738ebb9a057638a2664dbb1d2b7c7d

src/margpa_runtime_llm/web/static/app.js
  before: 120ed5e45a25dd932c3422542eb24770d693c008ea2b968a86acc9dadc943166d63a5fe56d3be35336e90243f1fb875d98608308c78129705d1e358d8eb9a003
  after : fba58d02d16eae25b34a6af4795c9ac52218a9fcdcbb282f526fda59ea7a5a3e3e16c4f102276ec8598746e5e84bc254fabec51c73ab9469d730516aed269a82

tests/unit/inference/test_llama_cpp_boundary.py
  before: c1df9063187d5f498acdb66930fe533c570965b075938481d9bf1c9a412a6bdd960ea2c9efc21b48e7cbd840aac2db2b264f1c61dde0a9902b64ce762fa7ae42
  after : bb5d2897437db015d092842b5efb768e038e2aa3d7d20daffa0f0a4070802e400c96675e3ae056fc38974493fec9ff3ad150e6b37595081f100aab9ece8ad3e5

tests/unit/conversation/test_conversation_generation.py
  before: 45b98c134966556d5666cea83bb60a9aae9ba4a26f065cd79a6aed3ddfff100a2c767be0aad74661d6bdd2afa928e8f726769a3ed512bd674d7c39a74c689bef
  after : 744aa6ece537c752dd1b0d70ddc91f7c68110861dccc8c501552361f0b84ce66a15a7a8999b8a706d555c300a8579f4c2aff381bf8575ddd647ecf0c78a60b10

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  before: 24670ffbf1707532bdf09ea4172055a4b0c7798d45f5ee5ff9f75f70a2427439b47d199adebb2cd8852c5f86a7554d3bbfe6d5c70940cad59215213a8e66edc4
  after : 50a01de5600261a29af4e32e67f007185c7b97aef1c29b60183db4b74fffbac520cda47aa7d04302562135b27736c8766b38e947213949ec1cb8ef8c0f93a01f

tests/unit/documentation_rag/test_lexical_retrieval.py
  before: c80161436d2d515293af9a2c775e1efa76cece06557fab3558440307a47a5f8c2d4e57fe2d6e570dddf3fae34f88b0475fdc44547ae5f5ab0948cb9dec200b29
  after : 0530a70667ed27dd6a32174f38b01a46557f840804c4c40249c23659955596ad33f773d7aa8e315c3a0c9a3c835193f0bf6ecdf22bd29f55d9f8e0a5c6a5727e

tests/unit/documentation_rag/test_bootstrap.py
  before: 5d71ecdfc273e19367fe8864f65714f88cf29229b5f8364a761f7a893902df3117032a2f3016e4e5c735a9f053b5b8c0b503ce8fd2fa69dd9c6109233a7e54d3
  after : 75fca72d1631a0ac5105af0d89804a974d0851d5b5ab4b39b132155ae64bb38aaabefd138c0231b61f70e24bae2491868fa4d09f189435dd027d7d62dffa8602

tests/unit/web/test_web_cli.py
  before: 59d6619b27a5fe4b29a31bb6c04b91d3b694ddefe7b1d0f2556b94fa8bd5c58da83b4ce54c4c73b40b9502a3d1fc92c5dad0f90524349a8dca2a9e56773bbddc
  after : c63a3cb5d1f64b367c497b8c75a49dd8328800d582f1d4fb36bb836725573c5f8ea66609740f908cd76f801e826f5807ad1b71983302e0241f2dc5855c2480e3

tests/integration/documentation_rag/test_conversation_rag.py
  before: f1df159fc943c067ad93e4997432bbad689aabfae57f25e90daaa47c0824dce13a36c5816dc6f92fad7f513a4782af5204929e3a7a4f210cc8f534ee531b0b19
  after : 8f324d44b28bca91a275b8476d13c7081bac118590f8f59eeb93452d701e26e2cae6deff8fc42d26b1ea10236019bac6c5677e3222edabccb63436c930f3da3e

tests/integration/web/test_web_app.py
  before: 27c31a5b3f89aa040e36576d37da5fb0057e19c5f6fcb63fafe5fbcb822ea19fc1bc61be0361c208d4d6a759fc63ec0238b83b037e2f851ce537356d86a34c22
  after : 03a7ca1d83aa16f788c8b88fc4c738c571ddf4ccb594ac0f4e223f93fba3318af8603450abeeff744a6f5977d083647b04891641784af7a869a5c2753171b141
```

本StatusはAppend-onlyの新規Eventであり、既存Historyは編集していない。

## 7. Verification

```text
./.venv/bin/pytest -q tests/unit/documentation_rag
  50 passed

./.venv/bin/pytest -q tests/integration/documentation_rag
  7 passed

./.venv/bin/pytest -q tests/unit/inference
  142 passed

./.venv/bin/pytest -q tests/unit/conversation
  30 passed

./.venv/bin/pytest -q tests/unit/web
  29 passed

./.venv/bin/pytest -q tests/integration/web/test_web_app.py
  28 passed

./.venv/bin/pytest -q
  400 passed, 3 deselected in 48.66s

./.venv/bin/ruff check .
  PASS

./.venv/bin/ruff format --check .
  PASS / 120 files

./.venv/bin/mypy .
  PASS / 120 source files

node --check src/margpa_runtime_llm/web/static/app.js
  PASS / no output
```

## 8. Mutation Boundary／Remaining

実施していない操作：

- Dependency Install／Update。
- `pyproject.toml`、`uv.lock`、Application Config、Model Config、Deployment／Web／Feature Profileの変更。
- Corpus Allowlist、Context Size、Chunk Size、`top_k`、`max_new_tokens`またはSafety Marginの変更。
- Model Download、Model Artifactへの追従／Copy／Rename／SHA計算、二重Model Load。
- 既存Local Web ProcessのStop／Kill／Restart。
- Local Browser／GGUF Manual Acceptance。
- Public Demo／LightningでのRAG有効化またはLightning操作。
- Network経由のExternal Service、GitまたはGitHub操作。
- `models` Symbolic Linkの追跡。
- `docs/project/current/`、`docs/project/shared/`、Accepted Requirements／Architecture／Governance／ADR、Phase Index、Public Docsおよび既存Historyの変更。

残る限界：

- Grounding InstructionはPrompt Composition境界を強化するが、Judge／Repair未実装のためModelの最終回答正しさを保証しない。
- Real Corpus SmokeのPrompt／Documentation Block計測値は決定的Simulationであり、新差分の実GGUF Token計測Evidenceではない。
- 新差分をLoadした実Model／Browser Manual Acceptanceは、Designer Re-reviewのGOと別途の明示的な実行タイミングを必要とする。

本StatusはManual Acceptance、Designer AcceptanceまたはPhase完了を主張しない。
