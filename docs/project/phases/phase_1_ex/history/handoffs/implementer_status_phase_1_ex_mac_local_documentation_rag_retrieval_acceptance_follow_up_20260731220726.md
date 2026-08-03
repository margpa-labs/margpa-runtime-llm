# 実装担当 Phase 1-ex Mac Local Documentation RAG Retrieval Acceptance Follow-up Status

```yaml
document_id: implementer_status_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up
phase: phase_1_ex
status: implementation_complete_waiting_designer_re_review
language: ja
created_at: 2026-07-31 22:07:26 JST
owner: 実装者役担当Task
source_review: designer_review_phase_1_ex_mac_local_documentation_rag_context_fallback_follow_up_20260731214639.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731214639.md
manual_acceptance_performed: false
```

## 1. Result

```text
Retrieval Acceptance Follow-up Implementation : COMPLETE
Required Automated Verification               : GREEN
F5 Natural-language Query Relevance            : RESOLVED IN IMPLEMENTATION
F6 Canonical Fixture Integrity                 : RESOLVED IN IMPLEMENTATION
F7 Measurement Unit Evidence                   : RESOLVED IN IMPLEMENTATION
Designer Re-review                             : WAITING
Local GGUF Manual Acceptance                   : NOT PERFORMED
Browser Manual Acceptance                      : NOT PERFORMED
Manual Acceptance Gate                         : NO_GO UNTIL DESIGNER RE-REVIEW
```

本Follow-upではF5～F7だけを対象とした。新Dependency、Embedding、Vector DB、Persistent Index、Corpus追加、Config変更、Public Demo／Lightning RAGおよびModel Backend変更は行っていない。

## 2. F5 Query Signal／Ranking Before／After

### Before

```text
Query:
  Tokenizer出力を一律のQuery FrequencyとしてBM25へ渡す

Natural polite query:
  Latin／Identifier Subjectと日本語の質問定型N-gramを区別しない

Result:
  多数の丁寧表現を含むNoise CorpusでSubjectが埋没し、
  roadmap、ARGD／DAGD等のCanonical ChunkがTop Kから脱落し得る
```

### After

```text
GenericNaturalLanguageQueryAnalyzer:
  Latin、Numeric、PathおよびCode形式のIdentifier Tokenを一般則で抽出
  Identifier Signal Weight : 4.0
  Auxiliary Context Weight : 0.2
  IdentifierがないQuery  : 従来のFrequencyを維持

Retriever:
  Query AnalyzerをRetrieverから分離して注入可能にした
  BM25 DF、Field Weight、Exact Phrase、Corpus Priority、Document Diversity、
  Minimum Score、No HitおよびDeterministic Tie-breakを維持
```

Versionは次のとおりである。

```text
JapaneseAwareLexicalTokenizer:
  key     : unicode_japanese_ngram
  version : 1 → 1
  理由    : Index側Tokenization結果は変更していない

GenericNaturalLanguageQueryAnalyzer:
  key     : generic_natural_language_subject_signal
  version : absent → 1

Bm25DocumentationRetriever:
  key     : field_weighted_bm25
  version : 2 → 3
  理由    : Query Weighting Algorithm変更を旧Index Cacheと分離する
```

Production CodeへのDomain固有語Hard-codeがないことは、Query AnalyzerおよびRetrieverのSourceをTest内でInspectionし、`roadmap`、`ARGD`、`DAGD`、`EASA`、`DLAGSA`、`OCILNS`が含まれないことを固定した。さらに対象Production Directoryへの同語検索は0件であった。

## 3. F6 Canonical Fixture Integrity

Fixture定義は次のCanonical箇所に合わせた。

- ARGD／DAGD: `docs/project/current/governance/runtime_governance_specification_ja.md` の `7. ARGD／DAGD`。
- EASA: `docs/project/current/project_continuity/project_continuity_master_ja.md` の `26.1 EASA`およびPhase 1 Governance Catalog。
- DLAGSA: 同文書の `26.2 DLAGSA`およびPhase 1 Governance Catalog。
- OCILNS: 同文書の `26.3 OCILNS`およびPhase 1 Governance Catalog。

Test Fixtureでは次を固定した。

```text
ARGD:
  Premise、Context、矛盾、情報不足、根拠、反証、代替仮説、表現、Drift、Repair

DAGD:
  Policy Goal、Constraint、Capability、Evaluation、Severity、Audit、Repair、
  Activation、Self Audit、Audit-to-Action、Status Reporting

EASA:
  内部安全傾向、周辺安全制御、入力文脈、生成過程およびComposite Safety Behavior
  単一物理Layerを断定しない

DLAGSA:
  複数の判断・実行・検証主体間の責任、委譲、例外、改竄耐性付き証跡、
  全体整合および異常時安全側制御

OCILNS:
  人、AI、Tool、外部System間の認知対話を、検証・参照・継承・監査可能な
  改竄耐性付き証跡単位として扱う台帳網
```

非公開Algorithm、未開示Protocolまたは略称から推測した意味は追加していない。

## 4. F7 Measurement Unit Contract

計測単位を`DocumentationMeasurementUnit`で明示した。

```text
TOKENS             : tokens
UNICODE_CHARACTERS : unicode_characters
```

Contract変更：

- `DocumentationReferenceBlock.estimated_tokens`を廃止し、`measured_size`と`measurement_unit`へ分離した。
- `AssembledDocumentationContext`へ`measurement_unit`と`measurement_limit`を追加した。
- `DocumentationEvidence`へ`context_budget_unit`、`context_measurement_unit`、`context_measurement_limit`を追加した。
- Exact Counter使用時はToken単位、Counter未設定・未Binding・失敗時はUnicode Character単位かつ`token_counter_fallback_used=true`とした。
- `context_used`、Block計測値および同単位Limitを一意に解決できる。
- Pydantic ValidatorでUnit／Flag不整合、Block／Context単位不一致、同単位Limit超過およびExact Token Limit不一致を拒否する。
- JSON Serializationで`unicode_characters`／`tokens`、Limitおよび`measured_size`を確認し、Character数が`estimated_tokens`へ格納されないことを固定した。

Context Assembler Versionは`3 → 4`とした。Exact loaded-model token counter、Dynamic Budget式、Safety Margin、Minimum Useful境界、任意Chunk途中切断禁止およびBackend最終Context検査は変更していない。

## 5. Noisy-corpus Fixture Result

各CaseでCanonical Chunk 1件と、Subjectへの参照および反復する日本語丁寧表現を含むDistractor 8件を同時にIndexし、Production Default `top_k=4`で2回同一結果になることを確認した。

| Natural Query | Top-ranked Path | Top-ranked Heading | Result |
|---|---|---|---|
| `roadmapの現在の進捗を教えてください` | `docs/public/roadmap_ja.md` | `Roadmap > 現在地と進捗` | PASS |
| `ARGDとDAGDについて説明してください` | `docs/project/current/governance/runtime_governance_specification_ja.md` | `ARGD/DAGD` | PASS |
| `EASAとは何ですか?` | `docs/public/concept_ja.md` | `External R&D Hook > EASA` | PASS |
| `DLAGSAとは何ですか?` | `docs/public/concept_ja.md` | `External R&D Hook > DLAGSA` | PASS |
| `OCILNSとは何ですか?` | `docs/public/concept_ja.md` | `External R&D Hook > OCILNS` | PASS |
| `システムArchitectureを説明してください` | `docs/project/current/architecture/system_architecture_ja.md` | `System Architecture` | PASS |
| `Nazuna Research Governance LLMとは何ですか?` | `docs/public/overview_ja.md` | `Project Overview` | PASS |

No Hit、Minimum Score、Document Diversity、Tie-breakおよび日本語だけのQueryの既存挙動も回帰Testで維持した。

## 6. Real Corpus Read-only Smoke

実ProjectのAllowlist CorpusをRead-onlyで検索した。Model Generationは行わず、RetrieverのTop K Citationを観測するためだけに決定的Test CounterをBindingした。Docs、Config、Index FileおよびModel Artifactは変更していない。

| Query | Selected Order | Path | Heading | Result |
|---|---:|---|---|---|
| `Nazuna Research Governance LLMとは何ですか?` | 1 | `docs/project/current/governance/runtime_governance_specification_ja.md` | `MARGPA Runtime Governance 仕様書` | relevant |
| `roadmapの現在の進捗を教えてください` | 1 | `docs/public/roadmap_ja.md` | `MARGPA Runtime LLM Roadmap` | PASS |
| `システムArchitectureを説明してください` | 3 | `docs/project/current/architecture/system_architecture_ja.md` | `MARGPA Runtime LLM 全体設計書 > 19. Deployment Architecture` | PASS |
| `ARGDとDAGDについて説明してください` | 1 | `docs/project/current/governance/runtime_governance_specification_ja.md` | `MARGPA Runtime Governance 仕様書 > 7. ARGD／DAGD` | PASS |
| `EASAとは何ですか?` | 1 | `docs/project/phases/phase_1/governance/phase_1_governance_ja.md` | `Phase 10 Original R&D System Catalog > 2. EASA` | PASS |
| `DLAGSAとは何ですか?` | 1 | `docs/project/phases/phase_1/governance/phase_1_governance_ja.md` | `Phase 10 Original R&D System Catalog > 3. DLAGSA` | PASS |
| `OCILNSとは何ですか?` | 2 | `docs/project/phases/phase_1/governance/phase_1_governance_ja.md` | `Phase 10 Original R&D System Catalog > 4. OCILNS` | PASS |

`OCILNS`のSelected Order 1も無関係資料ではなく、`docs/project/phases/phase_1/architecture/phase_1_architecture_ja.md`の`Phase 10 External Original R&D Integration Architecture > 7. OCILNS Boundary`であった。高Signal Identifier質問で無関係なUser ManualまたはLanguage SmokeがCanonical／Catalog定義より上位を占める結果はなかった。

## 7. Changed Files and SHA-512

```text
src/margpa_runtime_llm/adapters/documentation_rag/lexical_tokenizer.py
  before: 12064b449c474c29f22462a5b8c4c629fd2ad86e6e218c3741d2c50214b195a005931fd012b2cb8c3b14c3199c74644b9263b50c80a6dec3e27ee2758bc3bb49
  after : 7eb817b184191ad5e3da7dff54c6e643822c80e97915fc9fc3c95341a1c28a0fad24584503920f27036e4b510b496ccc7804b350632686a76212dfbe49682019

src/margpa_runtime_llm/adapters/documentation_rag/query_analyzer.py
  before: absent
  after : fd6669f1b9cbb487f779371fc9c099821cbf94195959bd4f070725c2ed8099232df650f9681f11ce34fed449333018b32fa8e4dab1caf925c91e6e11e7abf8db

src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
  before: daecec8829fced3ffb0ff85c0607ba8e2c3518c28dc93e7650b89bd62bc3af64be4b7b1ccde656ae45bd644a0e43e867ea28d149a304d3a8f690954884bdd8f7
  after : 53930b7275d3d2678e35b9c09fcbd641124d92b9eff2ca239d2cb9e4dad287ebb372e3cfbea1b8b8f2e951737fba70660f5e2ab35dc1eceabff46ece309e08b5

src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: d9e67d7913e7ae1d04be92193a26ad2c7aded1d9478b40214ff2dd2da2f80a71e97a52db01e498d31c00a25f75a60a131e590e8f2e12f2672e085fad8f2a1cd3
  after : 035f3027213c1d45ece2f0f1f155a45caa62533883e2a5c8111ca6d4e296b3fb413e788fc71c61f222edd6b6b633b5be43b807c853a955627dbbef63885bf634

src/margpa_runtime_llm/adapters/documentation_rag/bounded_context_assembler.py
  before: 7bfd279c1ec79ac06fd02b65817f453ab83de3a732e7bfd83cd649c6b2eb8eaed2ccb8673d50a138e9d70847b6fdc36287001a8abad6407d4a0b8f1a9eff89cb
  after : 87eff32fa7385ce35454b5e65667761bdea6d2426452e7a260e9f9c7bc8f22d515fa3d4470d205289fa635f6b475b1651f99f20ebccdcbd10bbcfcdff18ceda0

src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py
  before: aba19a2d02c6f241619e6e243ce2a5eaf1b31c49dfa798ac73d8a6135b63f6442cef59263d320ae8fa37aed5c7062d387a2af7e847fc7d2a86305738e3fda0c4
  after : f7afead11876b2c2c480556f4db6ada74de5860c8b767d0614e1abfeeafd7b095e0f0a248fc91f8067e658155e1a44b1df6e9f65c19737755605c49932ce242a

tests/unit/documentation_rag/test_bootstrap.py
  before: 64cee34a4d9a514d37c911e38ff55cc6e4798b1be4be684f0b1785003b7336c0cd9d6b54a3aaa1db1ae75bff9b158b1cda98bf443061944b095f05f1baef18c4
  after : 5d71ecdfc273e19367fe8864f65714f88cf29229b5f8364a761f7a893902df3117032a2f3016e4e5c735a9f053b5b8c0b503ce8fd2fa69dd9c6109233a7e54d3

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  before: 71d49dbc99d150d79126ce84ff7742aca6bea7cd31f131b4bde496a34679767db36a80a85298ec9d54a9505078a217fc1524eef2c5b4f1737b63b3ddd7a95e15
  after : 24670ffbf1707532bdf09ea4172055a4b0c7798d45f5ee5ff9f75f70a2427439b47d199adebb2cd8852c5f86a7554d3bbfe6d5c70940cad59215213a8e66edc4

tests/unit/documentation_rag/test_lexical_retrieval.py
  before: 1d1c440ffded822200d36b138bda2413c37d94d5cc74e63e1b9f7114547a48c8f0a94d352f7cc223313b6354e2bf35d04012bef1b138c9e360fa81b5e239c024
  after : c80161436d2d515293af9a2c775e1efa76cece06557fab3558440307a47a5f8c2d4e57fe2d6e570dddf3fae34f88b0475fdc44547ae5f5ab0948cb9dec200b29

tests/integration/documentation_rag/test_conversation_rag.py
  before: 6b22b84c1c222fb9c277370c37cc7b315161671363ca14a11a3ce58770f90aecb46a639da5ef3daf5c148e56f1ea84235485724afd27bd7332d9c939fa26f1c3
  after : f1df159fc943c067ad93e4997432bbad689aabfae57f25e90daaa47c0824dce13a36c5816dc6f92fad7f513a4782af5204929e3a7a4f210cc8f534ee531b0b19

tests/unit/conversation/test_conversation_generation.py
  before: 082a869e9e3d7d34dd8da7365299c47ec052e389038cfb1e6149e3080636ea482d6179903ef7afdbfcb689a6223dafc0fc7b251af0798a1bd9c966cd9938d293
  after : 45b98c134966556d5666cea83bb60a9aae9ba4a26f065cd79a6aed3ddfff100a2c767be0aad74661d6bdd2afa928e8f726769a3ed512bd674d7c39a74c689bef

tests/integration/web/test_web_app.py
  before: eb15d4d54ff8e079caef1836f7cbcdc217db6a1e5e1ae35c5d4637814f558dfca0e4748ba4c3ccfdd1e85731f4f22084c8c308b163a7cc0102c48b619f451aaa
  after : 27c31a5b3f89aa040e36576d37da5fb0057e19c5f6fcb63fafe5fbcb822ea19fc1bc61be0361c208d4d6a759fc63ec0238b83b037e2f851ce537356d86a34c22
```

本StatusはAppend-onlyの新規Eventであり、既存Historyは編集していない。

## 8. Verification

```text
./.venv/bin/pytest -q tests/unit/documentation_rag
  48 passed in 0.83s

./.venv/bin/pytest -q tests/integration/documentation_rag
  6 passed in 0.15s

./.venv/bin/pytest -q tests/unit/inference
  142 passed in 2.56s

./.venv/bin/pytest -q tests/unit/conversation
  28 passed in 0.16s

./.venv/bin/pytest -q tests/unit/web/test_web_cli.py
  11 passed in 0.36s

./.venv/bin/pytest -q tests/unit/web/test_access_profiles.py
  8 passed in 0.31s

./.venv/bin/pytest -q tests/integration/web/test_web_app.py
  28 passed in 0.54s

./.venv/bin/pytest -q
  395 passed, 3 deselected in 49.71s

./.venv/bin/ruff check .
  PASS

./.venv/bin/ruff format --check .
  PASS / 120 files

./.venv/bin/mypy .
  PASS / 120 source files

node --check src/margpa_runtime_llm/web/static/app.js
  PASS / no output
```

## 9. Mutation Boundary／Remaining

実施していない操作：

- Dependency Install／Update。
- `pyproject.toml`、`uv.lock`、Application Config、Model Config、Deployment／Web／Feature Profileの変更。
- Corpus Allowlist、Context Size、Chunk Size、`top_k`、`max_new_tokens`またはSafety Marginの変更。
- Model Download、Model Artifactの読取・Copy・Rename・SHA計算または実GGUF Generation。
- Local Browser Manual Acceptance。
- Public Demo／Basic Preview／LightningへのDocumentation Adapter Binding。
- Lightning、Network、GitまたはGitHub操作。
- Project Root外のSource／Docs操作。
- `models` Symbolic Linkの追跡。
- `docs/project/current/`、`docs/project/shared/`、Accepted Requirements／Architecture／Governance／ADR、Phase Index、Public Docsおよび既存Historyの変更。
- Scope外Refactor、File移動、RenameまたはCleanup。

未完了事項は設計統括者役の再Reviewと、その後に明示GOが出た場合のみ行うLocal GGUF／Browser Manual Acceptanceである。本StatusはManual AcceptanceまたはPhase完了を主張しない。
