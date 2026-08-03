# 実装担当 Phase 1-ex Mac Local Documentation RAG Coverage Integrity Follow-up Status

```yaml
document_id: implementer_status_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up
phase: phase_1_ex
status: implementation_complete_waiting_designer_re_review
language: ja
created_at: 2026-08-01 01:36:11 JST
owner: 実装者役担当Task
source_index: documentation_index_20260801003625.md
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260801003625.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up_20260801003625.md
backup_confirmed_by_user: true
manual_acceptance_performed: false
```

## 1. Result

```text
F13 Retrieval / Assembled Coverage Integrity : RESOLVED IN IMPLEMENTATION
F14 High-signal Identifier Classification     : RESOLVED IN IMPLEMENTATION
F8 / F9 / F11 / F12 Regression                : GREEN
Required Automated Verification               : GREEN
Real Corpus Read-only Smoke                    : GREEN / SAFE FAIL-CLOSED
Local GGUF / Browser Manual Acceptance         : NOT PERFORMED
Designer Re-review                             : WAITING
```

本Follow-upはF13／F14のみを対象とした。Config、Dependency、Model Artifact、Conversation本体、Inference／llama.cpp Adapter、Public Demo／Lightning、Accepted DocsおよびCorpus Allowlistは変更していない。

## 2. F13／F14 Before／After

### 2.1 F13 Coverage Integrity

Before:

```text
retrieval coverage : 3 / 3
assembled coverage : 1 / 3でもEvidenceは3 / 3
generation          : assembled blockが1件以上ならallowed
```

After:

- `SubjectCoverageTrace`が、Subject SHA-512 Digestから実際のSelected Chunk IDへのTransient Mappingを保持する。Raw Query、Raw Docs、Absolute PathまたはSubject文字列をEvidenceへ追加していない。
- Retrieval Stageは`retrieval_covered_subject_count`／`retrieval_uncovered_subject_count`として分離した。
- 既存`covered_subject_count`／`uncovered_subject_count`は、Model Promptへ実際に入ったAssembled Blockから再計算する。
- Citation、Assembled Block Count、Grounding StateおよびGeneration Decisionは同じAssembled Chunk集合から導出する。
- 一部SubjectのみAssemblyされた場合は`subject_coverage_insufficient`とし、`should_generate=false`、Model用Referenceなし、Inference Call 0でFail closedする。UIに日本語／英語のSafe Messageを追加した。
- System Citationは実Assembly分だけを示すが、Denied時はModel PromptへReference Messageを渡さない。

Deterministic Partial Assembly Fixture:

```text
requested subjects            : 3
retrieval coverage            : 3 / 3
retrieved chunks              : 3
assembled coverage            : 2 / 3
assembled blocks / citations  : 2 / 2
grounding state               : subject_coverage_insufficient
generation                    : denied
inference stream call         : 0
```

Missing Subject Fixture:

```text
requested subjects            : 3
retrieval coverage            : 2 / 3
assembled coverage            : 2 / 3
grounding state               : subject_coverage_insufficient
generation                    : denied
missing coverage              : explicit in evidence
```

### 2.2 F14 High-signal Classification

High-signal SubjectはNFKC後、Case Fold前のOriginal Surface形状で決定する。一般則は次のとおり。

- 2文字以上の英字がすべて大文字のAcronym。
- 英字と数字を含むCode-like Token。
- 英数字の間に`_`、`.`、`/`または`-`を持つIdentifier／Path-like Token。
- Initial-capだけではなく、先頭以降に大文字を持つCamel／Mixed-case Token。
- 文末PeriodはSubject本体から除外する。

`What`、`are`、`and`、`Explain`、`briefly`等はLexical Retrieval Signalとして維持するが、Coverage Slotは消費しない。Project固有語AllowlistやStopword ListをProduction Codeへ追加していない。

```text
Japanese EASA / DLAGSA / OCILNS : high-signal 3, retrieval 3/3, assembly 3/3,
                                  citations 3, generation allowed
English prose-noise query       : high-signal 3, retrieval 3/3,
                                  ordinary prose coverage slots 0
Unknown ZXQ / NVRTA / PLMKS     : high-signal 3, retrieval 3/3
```

Semantic Versionは次のとおり更新し、Index Cache Keyを分離した。

```text
JapaneseAwareLexicalTokenizer         : 1 -> 2
GenericNaturalLanguageQueryAnalyzer   : 2 -> 3
Bm25DocumentationRetriever            : 4 -> 5
```

## 3. Real Corpus Read-only Smoke

実Project Allowlist CorpusをRead-onlyで検索した。Model Generationは行わず、Documentation Block計測には決定的`len`、Base Promptには300 tokensのSimulation値を使用した。Docs、Config、Index FileおよびModel Artifactは変更していない。

| Case | Subject | Retrieval | Assembly | Citation | Grounding | Generation |
|---|---:|---:|---:|---:|---|---|
| Japanese combined | 3 | 3/3 | 0/3 | 0 | `context_insufficient` | denied |
| English prose-noise combined | 3 | 3/3 | 1/3 | 1 | `subject_coverage_insufficient` | denied |
| Unknown uppercase identifiers | 3 | 0/3 | 0/3 | 1 | `subject_coverage_insufficient` | denied |

Real Corpusの引用Blockは768-token Simulation Budgetに対して大きく、日本語CombinedはZero-blockの既存F9境界、英語Combinedは1/3 Partial Assemblyの新F13境界でそれぞれ安全側に停止した。Unknown Queryは通常英文のLexical Hitがある一方でSubject Definition Coverageが0/3のため、根拠のないGrounded Generationを行っていない。

Production Documentation RAG Sourceに対するProject固有語Scanは次の語でMatch 0件だった。

```text
EASA / DLAGSA / OCILNS / ARGD / DAGD
```

## 4. Verification

```text
./.venv/bin/pytest -q tests/unit/documentation_rag
  57 passed

./.venv/bin/pytest -q tests/integration/documentation_rag
  8 passed

./.venv/bin/pytest -q tests/unit/conversation
  30 passed

./.venv/bin/pytest -q tests/unit/web
  29 passed

./.venv/bin/pytest -q tests/integration/web/test_web_app.py
  28 passed

./.venv/bin/pytest -q
  408 passed, 3 deselected

./.venv/bin/ruff check .
  All checks passed

./.venv/bin/ruff format --check .
  120 files already formatted

./.venv/bin/mypy .
  Success: no issues found in 120 source files

node --check src/margpa_runtime_llm/web/static/app.js
  exit 0
```

## 5. Changed Files and SHA-512

```text
src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: 7210b1e77a39e2c56fd4118dc1b253d5e6edc66e4ac5f387fcd0a9003077595defe30f8936225e13695f3301947808e843c845809e5f32e97b2d5516b6e9cc69
  after : bf629a7cba55af826d91df72fd9eae86b8befbadf994d106de7f923afc106e5afb1ee8f11b3f7b5e58018aa6226673c62f24d877e763515dd479b66a4e99342f

src/margpa_runtime_llm/adapters/documentation_rag/lexical_tokenizer.py
  before: e5e4ee8a20443ef8641c723bb53d9dde183c8bf16952c2aaad9b34060e3d1e0ca39004a91768be7cc0fafd74a70e197f0d40370ab6a500425f6d63eccbbe28c7
  after : 60fadfbe801e9bfca2298273250bad76d9d23da17a791a97362d4a614def786ca3618c4c3de26376b63a2d2e5909081695f0a8c76d0d79fb557a9e1d1ab51d7a

src/margpa_runtime_llm/adapters/documentation_rag/query_analyzer.py
  before: 607eadc82b3a2fbef7b2f60b9c47233b91595fd1b0e5e3ad5d659f94dd666174c04a78409172d734f5fd3e7444dfe29466ea989ecf4bb10134b0ce389434f729
  after : cd17e2abbf7827f6c788cc09a73ce95b84269797d17a4d27a3c2da4bd9fb1cc0027670720431edbfa7764b8b40a57b517ea0ba8886d1038dc107d92325e83c42

src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
  before: fe36d508a846372777c623ac5a2d8021141fd86152320da289cc5db3f59566f095ab9640fbcdd88b30dd91610a18ea9c78577b128fce861815efc5d0a517eeb6
  after : 8a993d2108d82b57d24026d4df3c79021a99d14fbb5233f526e489815642b1f3ae2bc67cefd250b343d4a83831e926e52d7143e6de9eb856311a4dfe6e037cb7

src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
  before: dcedffed036422722ac2722b693c76b58fa1055f939489d067dbfb199462726af5aec2f2e2d7aa52548569d75ca538c7ebaec2105c289dc900c50b2220d64d58
  after : e00a15f3f34ef4982de6d59a266b81a695387954ef930ba030acbe050f4f05dfd43ba20ae5d67cf7b470007c634b229460508f267e262212407eb5c47cda0731

src/margpa_runtime_llm/web/static/app.js
  before: fba58d02d16eae25b34a6af4795c9ac52218a9fcdcbb282f526fda59ea7a5a3e3e16c4f102276ec8598746e5e84bc254fabec51c73ab9469d730516aed269a82
  after : c961ca5466a23895ca293bac8b5c07cafab53450a76fa11577469fbf542c88eea6e2dbcd9670daf6e4d62bf714845aec86f64481e1e9b2467c9a411c5cc3924e

tests/unit/documentation_rag/test_lexical_retrieval.py
  before: 0530a70667ed27dd6a32174f38b01a46557f840804c4c40249c23659955596ad33f773d7aa8e315c3a0c9a3c835193f0bf6ecdf22bd29f55d9f8e0a5c6a5727e
  after : ed45b955eab6f15f02954d25f1a7335abd502fa142fac0265d8a5e6c90892ff236e0d933fbf7032519de341fe336f2774f5c3939cccfcfee3c77da470a1f9893

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  before: 50a01de5600261a29af4e32e67f007185c7b97aef1c29b60183db4b74fffbac520cda47aa7d04302562135b27736c8766b38e947213949ec1cb8ef8c0f93a01f
  after : 662b672010fab852edb49c97d4e5bf8a6dc6841ad9dc258396b49978132c312e37cfa97dc3b26b26d32452d55a545d4c5681fc8c5ba578ecbae9702b91b019c2

tests/unit/conversation/test_conversation_generation.py
  before: 744aa6ece537c752dd1b0d70ddc91f7c68110861dccc8c501552361f0b84ce66a15a7a8999b8a706d555c300a8579f4c2aff381bf8575ddd647ecf0c78a60b10
  after : c175d0b65cdb6b65f23a4b41f71d11f2d661226ed1b31f613d7dd2a0354b73a8b1a77050ef5592a5f92a732d9ba4dd20f62de27f2a9224aa4ea23438841f424a

tests/integration/documentation_rag/test_conversation_rag.py
  before: 8f324d44b28bca91a275b8476d13c7081bac118590f8f59eeb93452d701e26e2cae6deff8fc42d26b1ea10236019bac6c5677e3222edabccb63436c930f3da3e
  after : d4c0c6f8679368bd58df5ba0296d3607d592edee4f08a6501e0e9660948eb68f7f90429fd181d2ae425d81c0d66be0221afc40b9cf71d4b6583f0079855cc47e

tests/integration/web/test_web_app.py
  before: 03a7ca1d83aa16f788c8b88fc4c738c571ddf4ccb594ac0f4e223f93fba3318af8603450abeeff744a6f5977d083647b04891641784af7a869a5c2753171b141
  after : db246c8903d36a0f35b0cffb831fd6221e2c343d8e05e9bb394e01aa4726e79c3646e22ea77a6d997ad6ff1bb38a2385a5cbcbb964bdbc57b2dfe97f94c9f5eb
```

## 6. Mutation and Operational Boundaries

- Backup済みのユーザー確認後に実装した。
- Existing Local Web Processの停止、KillまたはRestartは行っていない。
- ModelのLoad／Generation、Manual Acceptanceは行っていない。
- Git、GitHub、Network、LightningおよびExternal Serviceを操作していない。
- `models` Symlinkを追跡していない。
- Existing History、Current、Shared、Public、Phase IndexおよびAccepted Stable Docsは変更していない。

## 7. Remaining Limitations and Next Gate

- High-signal Classificationは一般化したSurface Heuristicであり、全Language／DomainのIdentifier分類を完全に保証するものではない。
- Real Corpus SmokeのToken計測は決定的Simulationであり、実GGUF Token CounterまたはModel回答のAcceptanceではない。
- Subject Coverage不足ではModel Generationを拒否する。Partial Subject Answerを許可する新Contractは導入していない。
- Designer Re-reviewがGOとするまで、ユーザーManual Acceptanceは再開しない。

本StatusはManual Acceptance、Designer AcceptanceまたはPhase完了を主張しない。
