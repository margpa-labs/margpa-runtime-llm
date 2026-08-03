# Current Canonical Reconstruction Record

```yaml
document_id: current_canonical_reconstruction
phase: phase_1_ex
state_at: 2026-07-27 10:11:32 JST
status: completed
owner: 設計統括者役
language: ja
operation_type: cumulative_stable_reconstruction
```

## 1. Purpose

`docs/project/current/`のCanonical文書を、Phase 1およびPhase 1-exの既存Source、Project Continuity第1周、Roadmap第1周およびSource Inventoryに基づき、累積・自己完結文書として再構築した。

既存本文を削除して短い要約へ置換せず、現時点のTaskを新規作成しても再説明なしで継続できる粒度を追加した。

## 2. Source Baseline

- Source Inventory:
  - Docs 493件
  - Demo Images 6件
  - Total 499件
  - Validation 499／499 PASS
- Project Continuity First Pass:
  - 921行
- Roadmap First Pass:
  - 1656行
- Phase 1 Lossless Source:
  - Existing 8 Compilation Categories
- Phase 1-ex Source:
  - Stable／History／Migration／Lightning／Documentation Operations

## 3. Requirements Specification

```text
Stable:
docs/project/current/requirements/requirements_specification_ja.md

Before:
docs/project/current/history/requirements/requirements_specification_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md

After:
docs/project/current/history/requirements/requirements_specification_phase_1_ex_canonical_reconstruction_ja_20260727101017.md
```

```text
Before SHA-512:
a4b334618f089472c701a0fbb112ce03a52f49599be36df0aa55bae8db2a1f17e6313a8d985b9e7b9f3319435bac084bd0644bddf0b01a8e5a5cb29b1bbc975e

After SHA-512:
71cd545dc1c0768dc0cbd27291c79175790d199698743b307a4aaaa11e8ce2124faa102d18c1588bf9e66334a4d5a543b44d5ffd8f152f99df00cc5ebbe373c1

After Lines:
766
```

主な追加：

- Hardware制約、優先順位、Prototype境界
- Model Runtime、Artifact、Generation、Thinking、Language
- Conversation、UI、Summary、Presentation
- Config／Switchboard／Invalid Combination
- Cross-platform、Lightning、Basic Preview、Public Demo
- Docs／Task Governance
- Audit／Evidence／Evaluation／Repair
- RAG／Agent／ML
- EASA／DLAGSA／OCILNS
- Publication／Legal／Acceptance Gate

## 4. System Architecture

```text
Stable:
docs/project/current/architecture/system_architecture_ja.md

Before:
docs/project/current/history/architecture/system_architecture_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md

After:
docs/project/current/history/architecture/system_architecture_phase_1_ex_canonical_reconstruction_ja_20260727101017.md
```

```text
Before SHA-512:
8d7c2851e8969e648f3b5ec0f4ca4b62c6ebeb0f5d0e91f55beb54fcb80de9c89229870b0faef950aa315de42d2a58f45276e47c44630bbb3ebed506683374cf

After SHA-512:
6f2e23c4c03ff0cbe69db7aa83ccf85f52edfa7b2d2ab0241eca7e28abfb0c15a555cc42f40a3bd637415fdd622dd9b6fc0dddba6628f15f06bf26746a502c4b

After Lines:
745
```

主な追加：

- Architectural Invariants／Dependency Direction
- Baseline／Optional Execution Pipeline
- Configuration Control Plane
- Model Runtime／Web／Access／Deployment
- Governance／Evidence／Observability
- Documentation／RAG
- External R&D Hook
- Current Implemented／In Progress／Not Implemented State

## 5. Technology Selection

```text
Stable:
docs/project/current/architecture/technology_selection_ja.md

Before:
docs/project/current/history/architecture/technology_selection_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md

After:
docs/project/current/history/architecture/technology_selection_phase_1_ex_canonical_reconstruction_ja_20260727101017.md
```

```text
Before SHA-512:
6756524b35a10eb26d5474508274b96e4e4b22579c9cf9ddc20fc37c04794838a8d820e412cf0e0bd2c2bb357184d79d6e1c3ab3ae66ee737a06c9052b812e29

After SHA-512:
5b310e37d395f34ac59fff36e91e8d2bcc2aaa3256cac465c7b9079702ac1aee92d62a38c34b4c2624ddaffc24e8eb143a596acfcc7fd9eb1731e7beb8858a75

After Lines:
471
```

主な追加：

- Python／uv／Environment
- Phase別Dependency導入
- Backend／Build Variant
- Main／Guard／Judge Model Strategy
- FastAPI／Streamlit／React比較
- Config／Storage／RAG
- macOS／Lightning／ZeroGPU／Cloud
- Test／Documentation／Distribution Boundary

## 6. Basic Design

```text
Stable:
docs/project/current/architecture/basic_design_ja.md

Before:
docs/project/current/history/architecture/basic_design_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md

After:
docs/project/current/history/architecture/basic_design_phase_1_ex_canonical_reconstruction_ja_20260727101017.md
```

```text
Before SHA-512:
10385f433a0899d6522f4e0566385c9b53dc9f2403e4a7926bc8b9618d8217067a83ca4554231fd920557d0981fbb533d1f8a7d2c2672e2580e7fa8ce7cea453

After SHA-512:
f5a91aa162860ccd0348d8ae4e73fa272e916578d1bd56cca9dae9b87738153c6f3dae8cea39917bd70eb2547b006cf68686690a69ee0fa919e5dd80affa7215

After Lines:
828
```

主な追加：

- Current Source Boundary／Bootstrap
- Config／Profile／Registry Contract
- Model Lifecycle／Conversation Event
- Web API／Client State
- Thinking／Markdown／Copy／Summary
- Lightning Path／Setup／Lifecycle／Runtime State
- Documentation Lifecycle
- Governance Component／External R&D Hook
- Deferred Design Items

## 7. Runtime Governance Specification

```text
Stable:
docs/project/current/governance/runtime_governance_specification_ja.md

Before:
docs/project/current/history/governance/runtime_governance_specification_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md

After:
docs/project/current/history/governance/runtime_governance_specification_phase_1_ex_canonical_reconstruction_ja_20260727101017.md
```

```text
Before SHA-512:
a26804cff4e4c70597d7ff534bf46bcf2df7a300a9a585334f3646522f90596099d7a1e264a8c707e13644fda91a7771f1211694d052338dd53eb035c8ff0ba5

After SHA-512:
39b33fd6ab35fa1f490e9aeb90967ba662bfe533c37d9409a448d20673048d3f77b71a8cb3c6b2aa28a3949e514ba47530d1cd7d961fa8abcf8d11983625c9f6

After Lines:
1141
```

主な追加：

- Scope／Non-scope
- Package／Definition／Empty／Unknown Contract
- Repository State／IR／Compiler／Profile
- Governance Point／Mode
- ARGD／DAGD詳細
- 16 GD Catalog
- Standard Result／Score／Evaluator
- Conflict／Action／State／Evidence
- Guardrail／Policy／Authority分離
- EASA／DLAGSA／OCILNS
- Security／Performance／Implementation Boundary／Order

## 8. Current Documentation Index

```text
Stable:
docs/project/current/documentation_index_ja.md

Before:
docs/project/current/history/index/documentation_index_phase_1_ex_before_canonical_reconstruction_ja_20260727100120.md

After:
docs/project/current/history/index/documentation_index_phase_1_ex_canonical_reconstruction_ja_20260727101132.md
```

```text
Before SHA-512:
8d23c1d76f6dfab76d79facb4198e42906ac7d35b0bf6af29e9c9010808ec4cf0df9b49e41e322f67ea6000a7b509eeaaa3c18d9cda7bc3603f3786cc25fbcf6

After SHA-512:
19d34ea4e08ed9109776120bb5e30d1b65aa6616d19e8c0396cf67c57af4b2f826bbf32861ad3703de79278f24a464e03c0cebb8579949f30200c4a4a077df7e

After Lines:
145
```

## 9. Verification

- Stable更新前Snapshot:
  - 6／6存在
- Stable更新後Snapshot:
  - 6／6存在
- Stable／After Snapshot Byte Comparison:
  - 6／6 PASS
- Current Markdown Relative Link Validation:
  - 7／7 PASS
- Existing Body Deletion:
  - なし
- History Overwrite:
  - なし
- Git Operation:
  - なし
- English Derived Documents:
  - 未作成
- Phase 1-ex Completion Declaration:
  - なし

## 10. Next

次はPhase 1とPhase 1-exのLossless Compilationを再構築する。

- Phase 1:
  - 完了済みPhaseとして、既存CompilationのSource Coverageを再検証し、全Categoryを横断するMaster Lossless文書を作成する。
- Phase 1-ex:
  - 進行中Phaseとして、Source Freeze時点までのInterim／Current-to-date Lossless文書を作成する。
- どちらもSource本文を改変せず、Path、Size、SHA-512および再抽出可能性を保持する。
