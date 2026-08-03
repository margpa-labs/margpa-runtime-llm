# 実装担当向け Phase 1-ex Lightning Public Corpus Documentation RAG Multi-access Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-08-01 09:10:03 JST
owner: 設計統括者役
target_role: 実装者役
external_operation_owner: user
requirements: ../../requirements/lightning_public_corpus_documentation_rag_multi_access_requirements_ja.md
architecture: ../../architecture/lightning_public_corpus_documentation_rag_multi_access_architecture_ja.md
decision: ../../adr/adr_0030_lightning_public_corpus_documentation_rag_multi_access_ja.md
supersedes: implementer_handoff_phase_1_ex_lightning_basic_preview_public_corpus_documentation_rag_adapter_hook_20260801090159.md
```

## 1. Effective Instruction

本HandoffがLightning Documentation RAG実装の最新指示である。

前Handoffの次は無効化される。

```text
Public Demo RAG denied
Public Demo adapter construction zero
Public Demo docs scan zero
Public DemoからRAG profile environmentをscrub
```

後継Decision：

```text
Basic Preview:
  Basic authentication preserved
  public 8-doc RAG eligible

Public Demo:
  authentication none preserved
  public 8-doc RAG eligible

Both:
  same explicit public corpus profile
  default OFF
  no internal docs
```

前Handoff、ADR-0029および旧要件はHistoryとして残し、編集・削除・上書きしない。実装は本Handoff、ADR-0030および後継設計に従う。

## 2. Required Reading

1. `../../requirements/lightning_public_corpus_documentation_rag_multi_access_requirements_ja.md`
2. `../../architecture/lightning_public_corpus_documentation_rag_multi_access_architecture_ja.md`
3. `../../adr/adr_0030_lightning_public_corpus_documentation_rag_multi_access_ja.md`
4. `../operations/retrieval_guidance_hardcode_and_maintenance_reconsideration_20260801091003.md`
5. `../operations/mac_local_documentation_rag_manual_test_2_findings_20260801084952.md`
6. `designer_review_phase_1_ex_mac_local_documentation_rag_manual_test_2_20260801084952.md`
7. `../../requirements/mac_local_documentation_rag_requirements_ja.md`
8. `../../architecture/mac_local_documentation_rag_architecture_ja.md`
9. `../../adr/adr_0028_mac_local_sparse_documentation_rag_and_external_adapter_hook_ja.md`
10. `../../../../shared/operations/research_asset_mutation_control_ja.md`
11. `../../../../shared/task_roles/task_role_write_authority_policy_ja.md`

## 3. Objective

既存Mac Sparse Documentation RAGを汎用Compositionへ整理し、Lightning Basic PreviewとPublic Demoの両方で、次の8文書だけを検索できるようにする。

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

実装者は8文書を作成、翻訳または編集しない。ユーザーがLightning上へ別途配置する。

## 4. Pre-mutation Gate／Baseline

開始前に次を確認する。

- Project Rootが`margpa-runtime-llm/`。
- Project Root外へ触れない。
- `models` Symbolic Linkを追跡しない。
- 変更予定Fileを列挙する。
- 主要Baseline SHA-512を照合する。
- 不一致時は勝手にMergeせず、現在値と必要差分を報告して停止する。
- Git、GitHub、Lightning、API Builder、Port、URL、Secrets、Private Bootstrapを操作しない。

```text
config/web_profiles/basic_preview.toml
3b0c9ab2530322a2bd825b1afba139a8ccc8e80c7127d08fdf6b81e9e7732e13ea7344213491806002aeb9569609de02e30f623a4a548dc53c4c3453d9c21b21

config/web_profiles/public_demo.toml
09db3c8045d2912434358d7cb6d3be70f7d78ccc083a6fee099ee94876bdd47cb2e0d3bb448d3710f5dc254e2dca8b25d4a7b1441acab2629eaa239051726b0e

src/margpa_runtime_llm/web/access_profiles.py
554eaf66f4243608063a7cd9eecd02dd4ee8e65d5f40d553322c7c33c1877a7eec4e892e89211fa3d00dff5f60093f178442953e848fe23c1bed252124e4805b

src/margpa_runtime_llm/bootstrap/documentation_rag.py
a0b47d49ec7f386aaf4253f145b72d73d49f976da0d758f44c8f10b9e3834596b869e2aeade3eb7bf42b832c192dfdfb0be600fedb46224abb44c4d56598a49b

src/margpa_runtime_llm/entrypoints/web/main.py
e6e176c234e452a963599a8610e6f2fdc16b6da101fa96c97833f59a867cf2e1961c0db6a4c1395c8a3531468d7803d434d8b1085603ba0b187f5c692577cbd2

scripts/runtime/lightning/basic_preview_common.sh
e86e1dd85eb48d68523bcc0e3fe859c66e413cff3688412a84c90ce8ec86cd9bab71e9ea9ec27bb52230159fd574a45b789c8b205a6cb37d6fe2bf2a2f843c14

scripts/runtime/lightning/basic_preview_service.sh
eb24cc058be641ab09ace05340cb05377900474ff2cbfac6227308ee52a3926c4bec921c8f981885b973351406b2d05cb2fcf7c691015deb626e6d3639e0e102

scripts/runtime/lightning/public_demo_service.sh
8f4cac68946ab3827e82446f2c04a58516ffffcb13fe27c81218086a112443e1ee4042b3a0084a785ebc00cf2251fd2c9e41e8bb1f015dbbf62a3139ff416aa8

tests/unit/runtime/test_lightning_basic_preview_service.py
502866c3cce07145ffd13b046b1b0e2fa4811c8731c288b2925f236f9b4acd5a74b589c16316da1cbb0f1f3f8c2035b54b27c64ba1d25ebb4979cbd6253ff46b
```

## 5. Authorized Mutation Scope

```text
config/web_profiles/public_demo.toml
config/feature_profiles/
  lightning_public_documentation_rag.toml

src/margpa_runtime_llm/web/access_profiles.py
src/margpa_runtime_llm/modules/documentation_rag/
src/margpa_runtime_llm/adapters/documentation_rag/
src/margpa_runtime_llm/bootstrap/documentation_rag.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/entrypoints/web/main.py

scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/public_demo_service.sh

tests/unit/documentation_rag/
tests/integration/documentation_rag/
tests/unit/web/
tests/integration/web/test_web_app.py
tests/unit/runtime/test_lightning_basic_preview_service.py

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_YYYYMMDDHHMMSS.md
```

Compatibility Exportのための関連`__init__.py`最小変更を許可する。

`config/web_profiles/basic_preview.toml`は既に`eligible`であり、意味変更は不要である。Test適合以外の変更をしない。

## 6. Forbidden Mutation

```text
docs/public/**
docs/project/current/**
docs/project/shared/**
Phase Index
Accepted Requirements／Architecture／ADR
既存History／Handoff／Status／Review／Index
README／Legal Docs
config/profiles/**
config/models/**
pyproject.toml
uv.lock
Model Artifact
Repository外Private Bootstrap
```

Authorized Scope外が必要なら実装せず、理由、対象、必要差分および影響をStatusへ記載して戻す。

## 7. Required Changes

### 7.1 Public Demo Capability

`config/web_profiles/public_demo.toml`を次へ変更する。

```toml
[features]
documentation_rag = "eligible"
```

`WebAccessProfile`の「Public Demoは必ずdenied」というInvariantを削除する。ただしAuthentication、Non-loopback、Profile Key整合性およびUnknown値拒否は維持する。

### 7.2 Feature Profile v2

Basic／Public共通のExplicit File Profileを追加する。

```text
profile path:
  config/feature_profiles/lightning_public_documentation_rag.toml

allowed access:
  basic_preview
  public_demo

allowed platform:
  linux x86_64 container

corpus:
  exact 8 files
```

既存Mac Profile v1を変更しない。

### 7.3 Explicit Source Selection

LightningではRecursive Tree Scanを使わず、検証済み8 PathだけをManifest候補にする。

Path Traversal、Absolute Path、Backslash、Line Break、Duplicate、Symlink、Root Escape、History、LosslessおよびAllowlist外を拒否する。

### 7.4 Generic Composition

Mac専用条件からRAG Coreを分離し、Feature Profile、Access ModeおよびPlatform ObservationでCompositionする。

既存`build_local_documentation_rag()`とMac Testを後方互換に保つ。Main Model二重Loadと追加Dependencyは禁止する。

### 7.5 Web CLI／Runtime Snapshot

明示Optionを追加する。

```text
--documentation-rag-profile DOCUMENTATION_RAG_PROFILE_PATH
```

Runtimeは次を区別する。

```text
capability
adapter availability
requested OFF／ON
effective state
provider display name
```

Profile Absolute Path、Corpus Absolute RootまたはPrivate情報をBrowserへ出さない。

### 7.6 Basic Preview Script

既定Public Corpus Profileを検証し、Foreground `run`へOptionを渡す。Credential、Stateful LifecycleおよびTraffic-aware Wakeを変更しない。

### 7.7 Public Demo Script

既定Public Corpus Profileを検証し、Foreground `run`へ同じOptionを渡す。

Basic Credential三項目の早期Scrubは維持する。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

`MARGPA_DOCUMENTATION_RAG_PROFILE`はCredentialではないためScrubしない。未検証値を直接渡さない。

### 7.8 RAG Default／Lifecycle

- Basic／PublicともDefault OFF。
- OFFならCorpus Scan／Index Build／Retrieval 0。
- 最初のONでLazy Build。
- Process終了でIndex破棄。
- Persistent Fileなし。

### 7.9 Retrieval Guidance

Hit Keyword列、Model参照用Index表、Subject MappingまたはProject固有略称のHard-codeを実装しない。

将来用の未使用Interfaceを形だけ追加する必要もない。本件は将来のRAG再設計で改めて判断する。

## 8. Required Tests

### 8.1 Access Matrix

- Basic Preview：Basic Auth＋RAG eligible。
- Public Demo：Auth None＋RAG eligible。
- Local：Loopback only＋既存RAG eligible。
- Access／Authentication矛盾は拒否。
- Publicでも内部Corpus ProfileはCompatibility拒否。

### 8.2 Corpus／Profile

- Profile v2が8 Pathだけを保持。
- Basic／Publicの両AccessでCompatibility Pass。
- Mac Profile v1回帰。
- Allowlist外Public、Current、Shared、Phase、History、Losslessを取得しない。
- Unsafe Path／Symlink／Root Escapeを拒否。
- Missing／Partial CorpusをCountで識別。
- Manifest DigestがContent変更で変化。

### 8.3 Runtime

- Basic／PublicでRAG OFF Zero Scan／Zero Build／Zero Retrieval。
- Basic／PublicでRAG ON Every-turn Retrieval。
- JA／EN QueryとCitation。
- Citationは8 Pathだけ。
- Context／Subject Coverage不足でModel Call 0。
- Summary Original Stage Retrieve Once。
- Stop／New Chat／Reload／Model Busy回帰。

### 8.4 Script／Isolation

- Basic `run`がProfile Optionを渡す。
- Public `run`もProfile Optionを渡す。
- Publicの子ProcessにBasic Credentialがない。
- Publicが`docs/project/**`を走査しない。
- Profile不正は両方Fail Closed。
- Existing Basic／Public Lifecycle TestがGreen。

## 9. Verification

```bash
./.venv/bin/pytest -q tests/unit/documentation_rag
./.venv/bin/pytest -q tests/integration/documentation_rag
./.venv/bin/pytest -q tests/unit/web
./.venv/bin/pytest -q tests/integration/web/test_web_app.py
./.venv/bin/pytest -q tests/unit/runtime/test_lightning_basic_preview_service.py
./.venv/bin/pytest -q
./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy .
node --check src/margpa_runtime_llm/web/static/app.js
bash -n scripts/runtime/lightning/basic_preview_common.sh
bash -n scripts/runtime/lightning/basic_preview_service.sh
bash -n scripts/runtime/lightning/public_demo_service.sh
```

Model Smoke、Lightning URL、API BuilderおよびSleep／Wakeは実装者Scope外である。

## 10. Completion Status

新Timestampで次を作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_YYYYMMDDHHMMSS.md
```

必須内容：

- Changed／Added File全件。
- Before／After SHA-512。
- 前Handoffからの変更点。
- Access Matrix。
- Profile v1／v2 Compatibility。
- Explicit Corpus Selection Call Graph。
- Basic／Public Script Argument Construction。
- Public Credential Scrub位置。
- RAG OFF Zero Scan Evidence。
- Internal Docs Scan 0 Evidence。
- Test Command、件数、結果、時間。
- 未実行項目とKnown Limitation。
- Project外、Lightning、Git、Model Artifact未変更。
- Scope外変更0件。

既存Artifactを上書きしない。

## 11. Acceptance Gate

Repository実装完了後、設計統括者役が全Changed File、Hash、Test、Access／Corpus境界およびMac回帰をReviewする。

Review Accepted後にだけ、ユーザー向けLightning差替・Test・Preflight・Basic／Public・Sleep／Wake手順を作成する。

Lightning上の全操作はユーザー担当である。
