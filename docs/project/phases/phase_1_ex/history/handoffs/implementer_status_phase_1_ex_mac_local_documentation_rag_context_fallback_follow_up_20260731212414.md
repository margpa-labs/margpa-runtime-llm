# 実装担当 Phase 1-ex Mac Local Documentation RAG Context Fallback Follow-up Status

```yaml
document_id: implementer_status_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up
phase: phase_1_ex
status: implementation_complete_waiting_designer_re_review
language: ja
created_at: 2026-07-31 21:24:14 JST
owner: 実装者役担当Task
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_correctness_follow_up_20260731193204.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731193204.md
manual_acceptance_performed: false
```

## 1. Result

```text
Context Fallback Follow-up Implementation : COMPLETE
Required Automated Verification           : GREEN
Unit Mismatch Blocker F2                   : RESOLVED IN IMPLEMENTATION
Designer Re-review                         : WAITING
Local GGUF Manual Acceptance               : NOT PERFORMED
Browser Manual Acceptance                  : NOT PERFORMED
Manual Acceptance Gate                     : NO_GO UNTIL DESIGNER RE-REVIEW
```

本Follow-upでは、Token、Unicode CharacterおよびUTF-8 Byteの単位不整合だけを対象とした。Retriever Weight、BM25 Formula、Corpus Priority、Chunk Size Config、Context Size、`max_new_tokens`およびSafety Marginは変更していない。

## 2. Unit Mismatch Before／After

### Before

```text
maximum_tokens:
  Dynamic Token Budget

fallback_maximum_characters:
  Resolverで min(2,400, effective_tokens)へ縮小

Fallback計測:
  len(text.encode("utf-8"))

既定の実効Fallback:
  768 UTF-8 bytes
```

### After

```text
maximum_tokens:
  Main Model Contextに対するDynamic Token Budget

fallback_maximum_characters:
  Exact Counterを利用できない場合のUnicode Character Budget
  既定値 2,400 charactersをToken数と混同しない

Exact計測:
  Loaded Main Model Tokenizerが返すToken数

Fallback計測:
  len(text)

UTF-8 bytes:
  Corpus File Size用の別単位でありContext Character Budgetに使わない
```

`DocumentationEvidence.context_token_budget_used`と`token_counter_fallback_used`により、`context_used`がExact Token数かFallback Character数かを区別する。Counter失敗時はRaw TextやAbsolute Pathを出力せず、Safe Warning `documentation_token_counter_unavailable`を返す。

## 3. Exact Counter／Composition構造

```text
Local Mac Web Composition
  → LocalDocumentationRagComposition._DeferredTextTokenCounter
  → Web RuntimeがMain Model Load完了後にBind
  → InferenceService.count_text_tokens()
  → TextTokenCounterPort
  → LlamaCppModelAdapter.count_text_tokens()
  → 既にLoad済みのLlamaCppChatTemplate／Tokenizer
  → BoundedDocumentationContextAssembler
```

安全境界：

- `TextTokenCounterPort`はInference側の狭いOptional Protocolであり、Documentation Domainにllama.cpp固有型を持ち込まない。
- 既存Main ModelのTokenizerだけを使い、Modelの二重Load、追加常駐、RAGごとのModel File Reopenは行わない。
- Token Countは既存Generation LockをNon-blockingで使い、Generation中は`MODEL_BUSY`、Unload後は`MODEL_NOT_LOADED`とする。
- Counterが未Binding、Busyまたは計測失敗の場合はUnicode Character Fallbackへ明示的に切り替える。
- Basic Preview、Public DemoおよびLightningにDocumentation AdapterをBindingしていない。Mac用既存機能は維持した。

## 4. Dynamic Safety Evidence

次の既存式を変更していない。

```text
request_available_rag_tokens
  = max(
      0,
      effective_context_size
      - requested_max_new_tokens
      - system_history_current_prompt_tokens
      - safety_margin_tokens
    )

effective_rag_tokens
  = min(configured_maximum_rag_tokens, request_available_rag_tokens)
```

Testで次を固定した。

- History、GenerationまたはSafety Marginの増加でEffective Token Budgetが減少する。
- Minimum Useful未満でReference／Citationは0件、Safe Warningを返す。
- Exact Counter時は採用Reference Token数がEffective Token Budget以下である。
- Fallback時は2,400 Unicode Charactersの単位を維持し、768 Tokenと同数に縮小しない。
- Fallback Character Budget超過Chunkを採用せず、Overflowを黙認しない。
- 採用済みChunk本文をBudgetに合わせて途中切断しない。
- llama.cpp Adapterの最終Context Limit検査は変更していない。
- Contextから除外したChunkのFalse Citationは生成しない。

## 5. Required Functional Fixtures

条件：

```text
effective_context_size       : 4096
requested_max_new_tokens     : 2048
safety_margin_tokens         : 512
configured maximum RAG tokens: 768
prompt／history estimate      : 300
counter                      : deterministic exact Test Double
chunk config                 : Production Default 900／120／1600 characters
```

| 区分 | Reference | Citation | Context Used / Budget |
|---|---:|---:|---:|
| Project overview | 1 | 1 | 440 / 768 test-counter tokens |
| Roadmap progress | 1 | 1 | 398 / 768 test-counter tokens |
| System Architecture | 1 | 1 | 434 / 768 test-counter tokens |
| ARGD／DAGD | 1 | 1 | 404 / 768 test-counter tokens |
| EASA | 1 | 1 | 362 / 768 test-counter tokens |
| DLAGSA | 1 | 1 | 397 / 768 test-counter tokens |
| OCILNS | 1 | 1 | 377 / 768 test-counter tokens |

各FixtureはTemporary Project内の日本語Markdown、Reference Headerおよび非信頼参照資料Instructionを含む。実Project Docsは変更していない。

## 6. Changed Files and SHA-512

```text
src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: d64dc56f91c5646c19223eeeee111e5426b94d64a4f7405de2c1a9f035910d182f8ab722c4c03e8bf1cdaa4939acdd9b4b9db24c665a5a16df09bd08adf8b466
  after : d9e67d7913e7ae1d04be92193a26ad2c7aded1d9478b40214ff2dd2da2f80a71e97a52db01e498d31c00a25f75a60a131e590e8f2e12f2672e085fad8f2a1cd3

src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py
  before: 54065cad4b43ad59ef343f7849a89301d9a78be56aeec7e13ad48deb7fab21a032ac13fd7f407895c4e55497e5b4e2004aa434cd5e856c9168f8d69190432414
  after : 7bfd279c1ec79ac06fd02b65817f453ab83de3a732e7bfd83cd649c6b2eb8eaed2ccb8673d50a138e9d70847b6fdc36287001a8abad6407d4a0b8f1a9eff89cb

src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
  before: 132f51715949a1cd03f94b25d6b6c49ea08e5faf40ae9e03d6931ed5baa03683fe691d53ab72dee99664d368b4be79e7a32dc05a8e9934a41714f63d05fbec0b
  after : aba19a2d02c6f241619e6e243ce2a5eaf1b31c49dfa798ac73d8a6135b63f6442cef59263d320ae8fa37aed5c7062d387a2af7e847fc7d2a86305738e3fda0c4

src/margpa_runtime_llm/modules/inference/ports/model_port.py
  before: c7d84fd21367553acc8a1cdde118c32488650fc4929e43bca61ee9b08503bbcb3876c475c3f7519f72b9745f87d82a53f5c32cb7eeb90dc097a973480bfe438c
  after : 86019234320c3fdbf5b9a8698280954edc97a0dffc831ae666c9fb915248186605f851c7355df1d0701ae6e36978df7316a67f5281bd12bfdd9a4b3b577bd011

src/margpa_runtime_llm/modules/inference/application/inference_service.py
  before: e9a0c336e2a1646153436b244cf83cfe15ef0117beea87f6bf36531fb741100497349d60270b07c9de69eb3ea2a698d57b86130a700ae32d93acc4abf53d7850
  after : 111b49513da339426004fabe6a9996068b568551e53c60c0b2e1699d0761c1f63103ef9be5a8fbd894fc19b90c43f8248e47fde288b90f12d06bff9ace9c84f9

src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py
  before: ce647ce28e1e57c047b1f7f53919ec82ffcba75f101ac567fe794a472868cd05ebfdca58b18a9fdbead387f263f0d72068b626b264f32cb2019bcc8562e3f5ec
  after : 091bbcb210d97701a4c2074efc50dcfaaf5c7586896a542cc5b3bf0dfdeaf12994b7cb54471c78176652857af88c9862f9594347f4f493b6a98224a6c55a93e1

src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py
  before: 5cd7f0241f3faaa53ee608e218defc5fb4c7707d6500852e6775afceab868d6f29aadd1e972a3dbdad2e55f71815da86e1a15b3d6386f8e4d3b3633282e0f488
  after : 4c8af8d10104f7d955144cc5b7fee33e00bec24893304b847a2e1bb52e507dd1110f60440a0b0b1f1268129de10862e6a11ac45fd4f332f01c8958653a06ac2b

src/margpa_runtime_llm/bootstrap/documentation_rag.py
  before: 3946d6398befc74b9e647ecafdcac9b6ca4e8ed741efbeee61369bb04e9807aa6ebe0b73bf8de92e8c1fbcaaa57c10455e5d5d1f983cbff3796671d34bfa20d3
  after : a0b47d49ec7f386aaf4253f145b72d73d49f976da0d758f44c8f10b9e3834596b869e2aeade3eb7bf42b832c192dfdfb0be600fedb46224abb44c4d56598a49b

src/margpa_runtime_llm/bootstrap/web_application.py
  before: ce293d3d37d8f33ba560c1cf0584b52b134c48435cc2356d48b5c5d024b332a7264015c60276c41587ed2ba652db96e8427ef7b2bd04ae0a97138f716b7f33ed
  after : 264b94f5f5efe007efe397c603868209a3d4cb3cd6369f44ed114da68beedf151e300e3872b397f1db8132eab0fe2a3a92a7542fad929a77129c76c93f53559a

src/margpa_runtime_llm/entrypoints/web/main.py
  before: b4387460a70060130b58f8e7e95112f9fbd6b33bf63ebeba6bcfc839aaf1212405905c30802f73390e722fe52f3eec7db64c41e81d4fd2df32c47c271de5f562
  after : e6e176c234e452a963599a8610e6f2fdc16b6da101fa96c97833f59a867cf2e1961c0db6a4c1395c8a3531468d7803d434d8b1085603ba0b187f5c692577cbd2

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  before: 84526842d81bbd7f21e205597d20f1a74dc016b64bd23fae050f27771a55a4792a8326970120b9c169bd65a019f270ce10d5686252eae499a450fe435f629ac8
  after : 71d49dbc99d150d79126ce84ff7742aca6bea7cd31f131b4bde496a34679767db36a80a85298ec9d54a9505078a217fc1524eef2c5b4f1737b63b3ddd7a95e15

tests/unit/documentation_rag/test_bootstrap.py
  before: 7b5c4e4461af57de278a104b5a5046d53b4c9f34f073f6babb7116d8a4f0542f858879a415a7e7f3188ba7fa413dfff68ef52a1dbfaf232ea91f11b7d269b4ab
  after : 64cee34a4d9a514d37c911e38ff55cc6e4798b1be4be684f0b1785003b7336c0cd9d6b54a3aaa1db1ae75bff9b158b1cda98bf443061944b095f05f1baef18c4

tests/unit/inference/test_llama_cpp_boundary.py
  before: d2ab50d05e7af297aa08d548fcf720d32ec542bec200f874f141041a5080329d1fdb01bfae547259c1d1444d1de2f762aa73f9b29678f3a76ef5cb9e44416beb
  after : c1df9063187d5f498acdb66930fe533c570965b075938481d9bf1c9a412a6bdd960ea2c9efc21b48e7cbd840aac2db2b264f1c61dde0a9902b64ce762fa7ae42

tests/unit/web/test_web_cli.py
  before: d1c2ec58ff7f7790f9a4e149ad667fc81fb505b9a9ff6e6612ef973ab5018b27c623e0e3bbf63765cf9a42acd4870e3664fa55ee192849028a28e41ec108170b
  after : 59d6619b27a5fe4b29a31bb6c04b91d3b694ddefe7b1d0f2556b94fa8bd5c58da83b4ce54c4c73b40b9502a3d1fc92c5dad0f90524349a8dca2a9e56773bbddc
```

本StatusはAppend-onlyの新規Eventであり、既存Historyは編集していない。

## 7. Verification

```text
./.venv/bin/pytest -q tests/unit/documentation_rag
  39 passed in 0.81s

./.venv/bin/pytest -q tests/unit/inference
  142 passed in 2.90s

./.venv/bin/pytest -q tests/unit/conversation
  28 passed in 0.10s

./.venv/bin/pytest -q tests/unit/web/test_web_cli.py
  11 passed in 0.26s

./.venv/bin/pytest -q tests/unit/web/test_access_profiles.py
  8 passed in 0.06s

./.venv/bin/pytest -q tests/integration/web/test_web_app.py
  28 passed in 0.48s

./.venv/bin/pytest -q
  386 passed, 3 deselected in 49.07s

./.venv/bin/ruff check .
  PASS

./.venv/bin/ruff format --check .
  PASS / 119 files

./.venv/bin/mypy .
  PASS / 119 source files

node --check src/margpa_runtime_llm/web/static/app.js
  PASS / no output
```

## 8. Mutation Boundary／Remaining

実施していない操作：

- Dependency Install／Update。
- `pyproject.toml`、`uv.lock`、Application Config、Model Config、Deployment／Web Profileの変更。
- Model Download、Model Artifactの読取・Copy・Rename・SHA計算または実GGUF Smoke。
- Local Browser Manual Acceptance。
- Lightning、Network、GitまたはGitHub操作。
- Project Root外のSource／Docs操作。
- `models` Symbolic Linkの追跡。
- `docs/project/current/`、`docs/project/shared/`、Accepted Requirements／Architecture／Governance／ADR、Phase Index、Public Docsおよび既存Historyの変更。

未完了事項は設計統括者役の再Reviewと、その後に明示GOが出た場合のみ行うLocal GGUF／Browser Manual Acceptanceである。本StatusはManual AcceptanceまたはPhase完了を主張しない。
