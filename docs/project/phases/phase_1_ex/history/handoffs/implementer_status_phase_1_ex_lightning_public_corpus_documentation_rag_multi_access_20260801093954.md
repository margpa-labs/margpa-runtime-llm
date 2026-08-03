# 実装担当 Phase 1-ex Lightning Public Corpus Documentation RAG Multi-access Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access
phase: phase_1_ex
status: implementation_complete_waiting_designer_review
language: ja
created_at: 2026-08-01 09:39:54 JST
owner: 実装者役担当Task
source_index: documentation_index_20260801091003.md
source_requirements: lightning_public_corpus_documentation_rag_multi_access_requirements_ja.md
source_architecture: lightning_public_corpus_documentation_rag_multi_access_architecture_ja.md
source_decision: adr_0030_lightning_public_corpus_documentation_rag_multi_access_ja.md
source_handoff: implementer_handoff_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_20260801091003.md
backup_confirmed_by_user: true
manual_acceptance_performed: false
```

## 1. Result

```text
Repository Implementation                  : COMPLETE
Basic Preview Basic Auth                   : PRESERVED
Basic Preview Public 8-doc RAG             : ELIGIBLE / DEFAULT OFF
Public Demo Authentication                 : NONE / PRESERVED
Public Demo Public 8-doc RAG               : ELIGIBLE / DEFAULT OFF
Mac Local Documentation RAG v1             : PRESERVED
Explicit Corpus / Internal Docs Exclusion  : GREEN
Automated Verification                     : GREEN
Lightning Manual Acceptance                : NOT PERFORMED / USER-ONLY
Designer Review                            : WAITING
```

前HandoffのBasic PreviewだけをRAG Eligibleとする旧設計を使用せず、最新のADR-0030に従い、Basic PreviewとPublic Demoの両方が同一の公開8文書Profileを利用できる構成へ更新した。`docs/public/**`の作成・翻訳・編集は行っていない。

## 2. Access Matrix

| Access | Authentication | Non-loopback | RAG Capability | Server Profile | Default |
|---|---|---:|---|---|---|
| Local | None | No | Eligible | Mac local v1 | Off |
| Basic Preview | Basic | Yes | Eligible | Lightning public v2 | Off |
| Public Demo | None | Yes | Eligible | Lightning public v2 | Off |

- LocalのLoopback-only、Basic PreviewのCredential必須、Public DemoのCredential不要を維持した。
- Public Demo固有の`documentation_rag = denied`不変条件だけを除去し、AccessとFeature Capabilityを独立して検証する。
- Browser RequestからFeature Profile、Corpus Path、Access CompatibilityまたはPlatformを選択する経路は追加していない。

## 3. Profile v1 / v2 Compatibility

```text
Mac Profile v1
  access   : local only
  platform : macos-arm64 only
  source   : existing aggregate LocalMarkdownDocumentSource

Lightning Profile v2
  access   : basic_preview / public_demo only
  platform : linux-x86_64-container only
  source   : ExplicitMarkdownDocumentSource
  corpus   : exact public 8 files
```

`build_documentation_rag()`がSchema、Access Mode、Platform ObservationおよびCorpus Selectionを検証する。既存`build_local_documentation_rag()`はLocal + macOS ARM64を渡すCompatibility Wrapperとして維持した。Public AccessにMac v1、LocalにLightning v2、またはLightning v2にmacOS Observationを渡すとSafeなInvalid Configurationで拒否する。

## 4. Explicit Corpus Selection and Lazy Call Graph

```text
margpa-web --documentation-rag-profile
  -> Web Access Profile capability
  -> build_documentation_rag
     -> Defaults + Feature Schema validation
     -> Access + Platform compatibility
     -> ExplicitMarkdownDocumentSource object construction
        (no manifest / no file read)
  -> Web runtime starts with default_mode=disabled

RAG OFF request
  -> Conversation bypass
  -> manifest 0 / file read 0 / chunk 0 / index 0 / retrieval 0

First RAG ON request
  -> fixed eight project-relative paths
  -> path / symlink / root / Markdown / UTF-8 / size validation
  -> manifest -> read -> chunk -> in-memory index -> retrieve -> assemble -> cite

Later unchanged RAG ON request
  -> same manifest digest -> in-memory index reuse
```

Lightning SourceのCandidate生成は、v2 Profileで検証済みの次の8 Pathを順に組み立てるだけであり、`rglob`や`docs/project/**`のRecursive Scanを行わない。

```text
docs/public/overview_ja.md
docs/public/overview_en.md
docs/public/concept_ja.md
docs/public/concept_en.md
docs/public/roadmap_ja.md
docs/public/roadmap_en.md
docs/public/technology_selection_ja.md
docs/public/technology_selection_en.md
```

Missing / Partial CorpusはProfile不正と分離し、Script Preflightで`expected=8 present=N missing=8-N`をReadinessとして表示する。RuntimeではPresent Document Countと`documentation_expected_file_missing` Warning Countを返し、全文書があるとのSilent Claimを行わない。

## 5. Lightning Script Construction and Isolation

```text
Basic Preview / Public Demo shared resolver
  MARGPA_DOCUMENTATION_RAG_PROFILE
    -> default tracked v2 profile when unset
    -> no line break / no dot segment / no backslash
    -> project-root bounded
    -> regular readable file / no symlink component
    -> schema / key / provider / access / platform / exact corpus validation
    -> canonical validated environment value
    -> --documentation-rag-profile <validated path>
```

Basic Previewは既存のCredential検証とStateful Lifecycleを維持し、Process IdentityにRAG Profile Pathも含める。Public DemoはScript先頭で、Directory解決やCommon HelperのSourceより前に次の3項目だけを`unset`する。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

`MARGPA_DOCUMENTATION_RAG_PROFILE`はCredentialではないためScrubせず、Contract検証後のCanonical Valueに置き換えて子Processへ引き継ぐ。PublicのPID、Log、Marker、LockまたはBasic Lifecycleの状態は新たに解決しない。

## 6. Automated Evidence

### 6.1 RAG OFF Zero Scan

- `DocumentationRagApplicationService`はSource Objectの構築時にManifestをLoadしない。
- Default Profileは`documentation-rag.defaults` v1の`default_mode = disabled`を維持する。
- Public Web IntegrationはDefault OFF RequestでRAG Query 0、明示ON Requestで初めて1 Queryとなることを確認した。
- Basic / Publicの両Accessでv2 Composition後もAdapter Objectのみで起動できる。

### 6.2 Internal Docs Scan 0

- Unit TestはAllowlist外Public、Current、Shared、Phase Historyを配置し、Manifestが8 Pathだけを含むことを確認した。
- Public Preflight FixtureはAllowlist外Publicと`docs/project/current/`を配置しても`present=1 missing=7`と判定し、それらをCountしない。
- Unsafe、Duplicate、Absolute、Traversal、Backslash、Line Break、SymlinkおよびRoot Escapeの拒否を自動Testで確認した。

### 6.3 Retrieval / Citation

- JA Queryは`docs/public/overview_ja.md`、EN Queryは`docs/public/overview_en.md`をSystem Citationとして取得した。
- Citation Pathは全て公開8 PathのSubsetかつProject-relativeである。
- Existing Every-turn Retrieval、Summary Original Stage Retrieve Once、Context / Subject Coverage Fail-closed、Stop、New Chat、ReloadおよびModel Busy回帰をFull Suiteで確認した。

## 7. Verification

```text
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m pytest -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py \
  tests/unit/documentation_rag \
  tests/integration/documentation_rag/test_public_corpus_rag.py \
  tests/unit/web \
  tests/integration/web/test_web_app.py
  178 passed in 54.73s

PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python -m pytest -q
  430 passed, 3 deselected in 57.20s

PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/ruff check .
  All checks passed

./.venv/bin/ruff format --check .
  122 files already formatted

PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/mypy .
  Success: no issues found in 122 source files

node --check src/margpa_runtime_llm/web/static/app.js
  exit 0

bash -n scripts/runtime/lightning/basic_preview_common.sh
bash -n scripts/runtime/lightning/basic_preview_service.sh
bash -n scripts/runtime/lightning/public_demo_service.sh
  all exit 0
```

## 8. Changed / Added Files and SHA-512

```text
config/web_profiles/public_demo.toml
  before: 09db3c8045d2912434358d7cb6d3be70f7d78ccc083a6fee099ee94876bdd47cb2e0d3bb448d3710f5dc254e2dca8b25d4a7b1441acab2629eaa239051726b0e
  after : 016eb67377abb39a79047f8462b284bdabdbebbaf8f38a399feb3ff2183fdeafe23b85cec969f5ffa8e75928aab36684b6c9f5f23e723a6cad8fb509ef460eae

config/feature_profiles/lightning_public_documentation_rag.toml
  before: absent
  after : 525e0ea6869e70e3dcc316ed176023bd7b6b069f0c51a469feb9c7e35f4af09b6d426844ba943dd523e850d6f24d8ec60ee114f80d708934250b1e497e744e70

src/margpa_runtime_llm/web/access_profiles.py
  before: 554eaf66f4243608063a7cd9eecd02dd4ee8e65d5f40d553322c7c33c1877a7eec4e892e89211fa3d00dff5f60093f178442953e848fe23c1bed252124e4805b
  after : 21fcea884e4ea9af226fcf3acc1ae03ff9beb713ff2710d02e49a517e26f79467fad9537fbece813c7d6fb19197dd613413cc7c4fb5a78c450e137325516dfac

src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  before: bf629a7cba55af826d91df72fd9eae86b8befbadf994d106de7f923afc106e5afb1ee8f11b3f7b5e58018aa6226673c62f24d877e763515dd479b66a4e99342f
  after : be0c4e8c7df1340203e74b98f0cbe40548fafc1db9019e731f78ff7700cf1522a26fbc496609cc3c09be736aa6017d56ecbcd864d68161c9b7fa508efb5e2a0e

src/margpa_runtime_llm/adapters/documentation_rag/local_filesystem_source.py
  before: 899e6c65fff3888ebcb267f52a542275484bfb66305f98a84cccefda85ca12766da7957675a646fe3342f6e079c94d59ec9bcba72cc2c5c9f1cd1356d1346d4a
  after : 6cbf483185780fe9b7f5e8302ee8949cf13cf7d1616c8a1b62fa54edb05254a1ec673223a631daaf81a18bf16296b84047f7ef69b3898591faeab49b5ca79769

src/margpa_runtime_llm/adapters/documentation_rag/__init__.py
  before: e4e64eac53f4b0dc84e43a33bf961b56f352885baee46d2fe127746d39acb10326d2490878ecea21b6067763b90f7fb4d662993f59e5a78f95a6b6c80db9eea1
  after : 9f2c6b0442fd9a1197eed4c585ea7f2efa97b63d562b14e349c234134e57a34a5b800ce5d12c901baafed054efaa1a10cd15383f38025772d28b1107842c63e5

src/margpa_runtime_llm/bootstrap/documentation_rag.py
  before: a0b47d49ec7f386aaf4253f145b72d73d49f976da0d758f44c8f10b9e3834596b869e2aeade3eb7bf42b832c192dfdfb0be600fedb46224abb44c4d56598a49b
  after : dc5897a9523789d57c08bc7bf9ad221e6b29174a47175401bf3806a6ff8a32f2215b85d740fac6332c3b3cf13900a8718f3f496fbfea593672dd30a80902a7b8

src/margpa_runtime_llm/entrypoints/web/main.py
  before: e6e176c234e452a963599a8610e6f2fdc16b6da101fa96c97833f59a867cf2e1961c0db6a4c1395c8a3531468d7803d434d8b1085603ba0b187f5c692577cbd2
  after : 08e8833a49622def9fefb8a44e10388a5b2abbbd06048bb979f71a7170ba381502320266e53584d97cf1430a5383924bad765bb94a88f6bf985cae78c1a5a4f8

scripts/runtime/lightning/basic_preview_common.sh
  before: e86e1dd85eb48d68523bcc0e3fe859c66e413cff3688412a84c90ce8ec86cd9bab71e9ea9ec27bb52230159fd574a45b789c8b205a6cb37d6fe2bf2a2f843c14
  after : dae7d3317fa9e1a7f3472d4d367c27f26fa2f86b79e97131c03f4db141f6058ff2c6b21b1c6f88ca10fa0c9665c02fe0bf77e7467d40b61e6707ecf8fc405b30

scripts/runtime/lightning/basic_preview_service.sh
  before: eb24cc058be641ab09ace05340cb05377900474ff2cbfac6227308ee52a3926c4bec921c8f981885b973351406b2d05cb2fcf7c691015deb626e6d3639e0e102
  after : 60c2b511d735c8c35b077e640ea3eda100f692d026e4d8b3fe088e5a57bcffebe691ab5c8675c2622cd41556c4af943a0167a0cd9c4087adf11b03f8c61fc597

scripts/runtime/lightning/public_demo_service.sh
  before: 8f4cac68946ab3827e82446f2c04a58516ffffcb13fe27c81218086a112443e1ee4042b3a0084a785ebc00cf2251fd2c9e41e8bb1f015dbbf62a3139ff416aa8
  after : 5668c1ce8b1a8a70a85192b4b744f96a984ef834367cc01ab24e2f05c040f7ba931fc5ac75aeff208d5674b0f423319179de561aa3d8968d822f4c348f031147

tests/unit/documentation_rag/test_bootstrap.py
  before: 75fca72d1631a0ac5105af0d89804a974d0851d5b5ab4b39b132155ae64bb38aaabefd138c0231b61f70e24bae2491868fa4d09f189435dd027d7d62dffa8602
  after : 05b173a7b98f10a6c30f88569c4c4a02a151484777a4db357d89f64ff4ee815d7ac9deda3dd1ffe4e8b33024dab475b94b3527cb9b8d08da907d4031efc4dfde

tests/unit/documentation_rag/test_explicit_filesystem_source.py
  before: absent
  after : ad085083f20cd0933a192dba8784f0be19fb8357fdca71f34ad7cc80617914e4775b5a9fea7ca93681f6cf456b31f19330f7d28ac924c01f0ed3f272cc73faed

tests/unit/web/test_access_profiles.py
  before: 66a589c2448101743cb199b506a9a4bd718790d4ea0136284746e3241b38a724109531918ef58648a95e5a77ec4543eded5e64f0b6b8c091038be8a28a009120
  after : 04a252e05ac03786cf34d3723fda19f6bc4f2cc44cf6f5e49cd464579d1cd54eae8dfc0b0ad32489b818bb63c1f2514872fcd268f420ace613adda1b5c6096f8

tests/unit/web/test_web_cli.py
  before: c63a3cb5d1f64b367c497b8c75a49dd8328800d582f1d4fb36bb836725573c5f8ea66609740f908cd76f801e826f5807ad1b71983302e0241f2dc5855c2480e3
  after : dcf1695f78a9c5a856dff4e7b7dcb9deb94f70a251492bc2beeda048faca748d92f79d97744e7a9553c0c71d223fff55bc4370bbf76468743de57faaac77699d

tests/integration/documentation_rag/test_public_corpus_rag.py
  before: absent
  after : 8f8cea9c09b5dc7ff3d1545d27bd518883121cfc4dce873d1898c7f75d657b3e53a2874679bff8369f0d1270120b852816f421308f6d536eed24d4640e26afef

tests/integration/web/test_web_app.py
  before: db246c8903d36a0f35b0cffb831fd6221e2c343d8e05e9bb394e01aa4726e79c3646e22ea77a6d997ad6ff1bb38a2385a5cbcbb964bdbc57b2dfe97f94c9f5eb
  after : 86814dd06764e2c0e440a852d23b96d104548c29d14a6bf1ec0f69aefa9f8c10dfaa85d8871f9df09c72cf80e9d705d8da7312b49096620a4f9193909188659c

tests/unit/runtime/test_lightning_basic_preview_service.py
  before: 502866c3cce07145ffd13b046b1b0e2fa4811c8731c288b2925f236f9b4acd5a74b589c16316da1cbb0f1f3f8c2035b54b27c64ba1d25ebb4979cbd6253ff46b
  after : 9037f98297ef36cd74c88de370206dd9cb9b7f5b55effd5920b70d6a4d416ed173788e554b30e902cb7fd3cb1ee7837e2ffaf3d179e4f4e863cdb936c5545ac1
```

Unchanged integrity evidence:

```text
config/web_profiles/basic_preview.toml
  before/after: 3b0c9ab2530322a2bd825b1afba139a8ccc8e80c7127d08fdf6b81e9e7732e13ea7344213491806002aeb9569609de02e30f623a4a548dc53c4c3453d9c21b21

config/feature_profiles/local_documentation_rag.toml
  before/after: cb7e937ffcb00a6cd181727c322356d54f00bba14149d4db7bf41e5a20db33d82091dd7b90f4a6b30d49a1ed473930ed6dc43c61562e747054b4dcf8aca92f31

config/feature_profiles/documentation_rag_defaults.toml
  before/after: a373c8aa49992b1f616c99bfe3e590cbf4c469254b2e5cfd477438934ccdb220587ee5dcab61128b0135d229ca58600ef67f5cb2f7e8c29ddca376735ab149db
```

## 9. Mutation and Operational Boundaries

- ユーザーからBackup済みの確認を受けた後に実装した。
- Authorized Mutation Scope外のProject File変更は0件である。
- Existing Current、Shared、Requirements、Architecture、Governance、ADR、Phase Index、Public DocsおよびExisting Historyを変更していない。本Statusだけを新規Eventとして作成した。
- `docs/public/**`、Project外の継続Artifact、Lightning、API Builder、URL、Port、Managed Secrets、Private Bootstrap、Git、GitHub、NetworkおよびModel Artifactを変更していない。
- `models` Symbolic Linkを追跡していない。
- Dependency Install、Version Update、Main ModelのLoadまたは二重Loadを行っていない。

## 10. Not Performed / Known Limitations

- Lightning上の8文書配置、Preflight、Basic / Public起動、API Builder、URL、Port、Sleep / Wake、Cold RebuildおよびCredential手動検証は、指示どおり実施していない。
- Real GGUF / Model Smokeは実施していない。Full Suiteの3 deselectedはReal-model系Markである。
- Lexical RetrievalはSemantic SufficiencyまたはCitationのClaim Entailmentを保証しない。Hit Keyword表、Project固有Subject Mappingまたは手動Indexは追加していない。
- LightningでPublic 8文書が全てMissingまたはEmptyの場合、通常Chatは起動可能だが、RAG ONはSafe WarningとModel Call 0でFail closedする。Partialの場合はPresent / Missing Countを明示し、存在するAllowlisted Documentだけを検索する。
- Basic PreviewとPublic Demoは別Processで起動する場合、それぞれ独立したIn-memory Indexを持つ。PersistentまたはCross-process Cacheは導入していない。

本StatusはDesigner Acceptance、Lightning Manual AcceptanceまたはPhase完了を主張しない。
