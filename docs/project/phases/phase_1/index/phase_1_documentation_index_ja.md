# Phase 1 Documentation Index Lossless Compilation
```yaml
document_id: phase_1_index_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 76
source_manifest: ../../phase_1_ex/operations/source_to_target_documentation_migration_manifest.json
source_hash_algorithm: sha512
supersedes: null
rag_default: true
```

## Compilation Policy

本書はPhase 1中に作成されたSource文書を、省略、要約、意味変更または再解釈せず、Source Path順に再配置したLossless Compilationである。

本文は原文を維持し、Directory Migration後も参照可能にするため、MarkdownのLocal Link Pathだけを機械的に正規化している。原文File、原文SHA-512および移動先はSource Manifestから一意に解決できる。

矛盾、旧判断、未解決事項および後継文書への置換前状態も削除していない。Currentな判断はCurrent Canonical文書とPhase Indexを参照する。

## Source Documents

<!-- SOURCE_BEGIN 1: docs/documentation_index_20260718174637.md -->

### Source 1: `docs/documentation_index_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718174637.md`
- Source SHA-512: `d3048b1ae4e11dc721bb9e18a4df53414ccc6e61d5372586af0ebe44303188cdbb6d8b843d6e0f350648e5a3a0c29bc0f844a99047b3e1aa940fa333fc6a5a93`
- Source Size: `4659` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718174637`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoffを示す。

同じ主題のDocumentが複数存在する場合、この索引で`current`として掲載されたDocumentを正本として扱う。

## 2. 最初に読む文書

1. [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md)
2. [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md)
3. [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | File名、Timestamp、日本語、更新、正本の共通ルール |
| current | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | Project目的、Scope、優先順位、Hardware、制約 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |

## 7. Handoffs

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | 全担当Task |
| current | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | 設計者役 |
| waiting | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | 将来の実装者役 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. System Architecture
4. Model Strategy
5. Runtime Governance
6. Roadmap
7. ADR

### 実装者

1. Common Handoff
2. Implementer Handoff
3. Project Requirements
4. System Architecture
5. Model Strategy
6. Runtime Governance
7. Audit／Security
8. Roadmap
9. ADR

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Model Strategy
5. Runtime Governance
6. Audit／Security
7. ADR

## 9. 現在地点

```text
Phase 0
要件定義・技術選定・Architecture設計
```

Model選定とModel Storageは基本決定済み。

次の設計議題はProject全体のDirectory構成。

実装はまだ解禁されていない。

## 10. Snapshot構成

この初期Snapshotには次の17文書が含まれる。

```text
Requirements : 2
Architecture : 4
Governance   : 2
ADR          : 4
Handoffs     : 4
Index        : 1
Total        : 17
```

<!-- SOURCE_END 1: docs/documentation_index_20260718174637.md -->

---

<!-- SOURCE_BEGIN 2: docs/documentation_index_20260718193435.md -->

### Source 2: `docs/documentation_index_20260718193435.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718193435.md`
- Source SHA-512: `c3079d55856a427364235edc2c7d6e5431834f7a41e2844f5803c60c4d4d26a8934a4f89a8d534cd7e4ce13636eb255aa128d61c96b3bfcc6c1dd42ba591a8b2`
- Source Size: `7675` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718193435`
- supersedes: `documentation_index_20260718174637.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoffと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |

## 7. Handoffs

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 将来の実装者役 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. System Architecture
4. Model Strategy
5. Runtime Governance
6. Roadmap
7. ADR

### 実装者

1. Common Handoff
2. Implementer Handoff
3. Project Requirements
4. System Architecture
5. Model Strategy
6. Runtime Governance
7. Audit／Security
8. Roadmap
9. ADR

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Model Strategy
5. Runtime Governance
6. Audit／Security
7. ADR

## 9. 現在地点

```text
Phase 0
要件定義・技術選定・Architecture設計
```

Model選定とModel Storageは基本決定済み。

Project全体のDirectory構成も決定済みで、Phase 1最小Directoryだけ作成済み。

次の設計議題はLocal Backend、Python Version、Dependency管理、Config、Model Registry、Phase 1 Acceptance Criteria。

実装はまだ解禁されていない。

## 10. Snapshot構成

現在のDocument Setには次の18文書が含まれる。

```text
Requirements : 2
Architecture : 5
Governance   : 2
ADR          : 4
Handoffs     : 4
Index        : 1
Total        : 18
```

## 11. Historical Document Set

Append-Only移行前に更新されていた8文書について、`20260718174637`版を作成当初の内容へ復元し、現在内容を`20260718193435`版として保存した。

旧文書自体には後継情報を追記していない。

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |

## 12. Repository内の文書総数

```text
Current Document Set : 18
Historical Documents : 8
Total Stored Files    : 26
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

<!-- SOURCE_END 2: docs/documentation_index_20260718193435.md -->

---

<!-- SOURCE_BEGIN 3: docs/documentation_index_20260718201744.md -->

### Source 3: `docs/documentation_index_20260718201744.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718201744.md`
- Source SHA-512: `58bfa168aa67e6d6b45f26b310af8ac878b2d78f9aee5180de97022aa81c08429274c36f87fc491af16699eac4ec44377aac436b24168a1d5049f15ab43e6ea0`
- Source Size: `9053` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 20:17:44 JST`
- 更新日時: `2026-07-18 20:17:44 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718201744`
- supersedes: `documentation_index_20260718193435.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoffと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |

## 7. Handoffs

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 将来の実装者役 |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. System Architecture
4. Project Directory Structure
5. Python Environment and Dependency Strategy
6. Model Strategy
7. Runtime Governance
8. Roadmap
9. ADR

### 実装者

1. Common Handoff
2. Implementer Handoff
3. Designer Python Environment Handoff
4. Project Requirements
5. System Architecture
6. Project Directory Structure
7. Python Environment and Dependency Strategy
8. Model Strategy
9. Runtime Governance
10. Audit／Security
11. Roadmap
12. ADR

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Model Strategy
5. Runtime Governance
6. Audit／Security
7. ADR

## 9. 現在地点

```text
Phase 0
要件定義・技術選定・Architecture設計
```

決定済み：

- Initial ModelとQuantization
- External Model StorageとPOSIX Symbolic Link
- Modular Monolith＋機能別Module＋Port／Adapter
- Project Directory全体像
- Phase 1最小Directory
- Python 3.13.14 Primary
- Python 3.12.13 Fallback
- Project Rootの`.venv/`
- `uv 0.11.29`
- Phase単位Dependency Install
- Phase 1 Initial Dependency Version候補

未解禁：

- Python／uv／Package Install
- `.venv`作成
- `pyproject.toml`／`uv.lock`作成
- Source実装
- Model Load／Metal Build検証

次の設計候補は、Config方式、Model Registry、Phase 1 Acceptance Criteriaの詳細、Local Backend Interface、UI方式である。

## 10. Current Snapshot構成

現在の正本Document Setには次の21文書が含まれる。

```text
Requirements : 2
Architecture : 6
Governance   : 2
ADR          : 5
Handoffs     : 5
Index        : 1
Total        : 21
```

## 11. Historical Document Set

Append-Only移行前に更新されていた8文書について、`20260718174637`版を作成当初の内容へ復元し、現在内容を`20260718193435`版として保存した。

旧文書自体には後継情報を追記していない。

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |

## 12. Repository内の文書総数

```text
Current Document Set : 21
Historical Documents : 9
Total Stored Files    : 30
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 3: docs/documentation_index_20260718201744.md -->

---

<!-- SOURCE_BEGIN 4: docs/documentation_index_20260718212502.md -->

### Source 4: `docs/documentation_index_20260718212502.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718212502.md`
- Source SHA-512: `0a9808975c42124fc5bf0910a0824c0db9dcbf3f6226f6a9dfb67826b8cade1135a37b468b9237c4361300cd723c92047682d6403c55f403739e9e1315ae1664`
- Source Size: `9607` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 21:25:02 JST`
- 更新日時: `2026-07-18 21:25:02 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718212502`
- supersedes: `documentation_index_20260718201744.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Statusと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |

## 7. Handoffs／Status

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役 |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | Phase 1-A実装結果。主要技術成立性Pass、Follow-upあり |
| current | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | Phase 1-A設計Review、uv／Metal Build再現性Follow-up |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. System Architecture
4. Project Directory Structure
5. Python Environment and Dependency Strategy
6. Latest Implementer Status
7. Latest Designer Review
8. Runtime Governance
9. Roadmap
10. ADR

### 実装者

1. Common Handoff
2. Implementer Handoff
3. Python Environment Handoff
4. Latest Implementer Status
5. Latest Designer Review
6. Project Requirements
7. System Architecture
8. Project Directory Structure
9. Python Environment and Dependency Strategy
10. Model Strategy
11. Runtime Governance
12. Roadmap
13. ADR

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Model Strategy
5. Runtime Governance
6. Audit／Security
7. ADR

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smokeの主要技術成立性を確認済み
Environment再現性Follow-up待ち
```

Pass：

- Python 3.13.14／ARM64／通常GIL
- Project Root `.venv/`
- Direct Dependency Version
- `uv.lock` Hash
- `llama-cpp-python 0.3.34`
- Apple M2 Pro／Metal
- Qwen3-4B Load／Japanese Generation
- Streaming／Consumer-side Stop／Post-stop Generation
- Explicit Close／Unload
- Ruff／mypy／pytest／Jupyter

Required Follow-up：

- uv実行Fileの永続配置
- Metal Source Build RecipeのProject内永続化
- 別Task／Fresh条件での再現性確認

Recommended Follow-up：

- Opt-in `model_smoke` Test
- Backend Cold Init計測の分離

未着手：

- Phase 1-B Model Port／Contract／Production Adapter／Registry／Config／CLI
- Phase 2以降

## 10. Current Snapshot構成

現在の正本Document Setには次の23文書が含まれる。

```text
Requirements : 2
Architecture : 6
Governance   : 2
ADR          : 5
Handoffs     : 7
Index        : 1
Total        : 23
```

## 11. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |

## 12. Repository内の文書総数

```text
Current Document Set : 23
Historical Documents : 10
Total Stored Files    : 33
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 4: docs/documentation_index_20260718212502.md -->

---

<!-- SOURCE_BEGIN 5: docs/documentation_index_20260718221255.md -->

### Source 5: `docs/documentation_index_20260718221255.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718221255.md`
- Source SHA-512: `32735724f0032bdefb43c4e6931724796b079a7bfc6d349a49179d1482049c5888ace109851f2df980002bc6f4b58451cc8e2be871e4c128bdf10bf65d0397bc`
- Source Size: `11585` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 22:12:55 JST`
- 更新日時: `2026-07-18 22:12:55 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718221255`
- supersedes: `documentation_index_20260718212502.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役 |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Latest Designer Review
4. System Architecture
5. Project Directory Structure
6. Python Environment and Dependency Strategy
7. Latest Implementer Status
8. Runtime Governance
9. Roadmap
10. ADR

### 実装者

1. Common Handoff
2. Implementer Handoff
3. Latest Designer Review
4. Latest Implementer Status
5. Project Requirements
6. System Architecture
7. Project Directory Structure
8. Python Environment and Dependency Strategy
9. Model Strategy
10. Runtime Governance
11. Roadmap
12. ADR

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Latest Designer Review
5. Model Strategy
6. Runtime Governance
7. Audit／Security
8. ADR

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性を完了

Next Candidate
Phase 1-Bの詳細設計と、ユーザーによる実装許可
```

Pass：

- Python 3.13.14／ARM64／通常GIL
- Project Root `.venv/`
- User Scopeの永続`uv 0.11.29`
- Login Shellからの`uv lock --check`／`uv sync --frozen --offline`
- Direct Dependency Exact Version
- `uv.lock` Hash
- `llama-cpp-python 0.3.34`
- macOS／ARM64用Metal Source Build Recipe
- Fresh／Clean相当Build Evidence
- Apple M2 Pro／Metal／GPU Offload
- Qwen3-4B Load／Japanese Generation
- Streaming／Consumer-side Stop／Post-stop Generation
- Explicit Close／Unload
- Default pytest／Opt-in `model_smoke`
- Ruff／mypy

Required Follow-up：

```text
uv実行Fileの永続配置                   : Complete
Metal Source Build RecipeのProject永続化: Complete
別Task／Fresh条件での再現性確認         : Complete
```

Known Non-blocking Item：

- 通常Setupでも`--reinstall-package llama-cpp-python`により毎回Native再Buildする
- 再現性重視として現在は受理し、必要時にNormal Syncと明示Native Rebuildを分離する
- Qwen3のEmpty Thinking Tagに関するProduction Policyは未決定

未着手：

- Phase 1-B Model Port／Contract／Production Adapter／Registry／Config／CLI
- Phase 2以降

## 10. Review／Index作成運用

今後、正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の23文書が含まれる。

```text
Requirements : 2
Architecture : 6
Governance   : 2
ADR          : 5
Handoffs     : 7
Index        : 1
Total        : 23
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 23
Historical Documents : 13
Total Stored Files    : 36
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 5: docs/documentation_index_20260718221255.md -->

---

<!-- SOURCE_BEGIN 6: docs/documentation_index_20260718223203.md -->

### Source 6: `docs/documentation_index_20260718223203.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718223203.md`
- Source SHA-512: `d0416d748af17b2a1b30c31bd4e4fa4898b0c53c20831d385321d9ed10b9e13747001a6aba4f256fdc2d74b342fcf488a8ab0b106368d110df220d452498d87b`
- Source Size: `12419` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 22:32:03 JST`
- 更新日時: `2026-07-18 22:32:03 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718223203`
- supersedes: `documentation_index_20260718221255.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md)
5. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| current | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| proposed | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役 |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

Phase 1-B実装担当向けHandoffは、詳細設計のユーザー確認後に新Timestampで作成する。

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Latest Designer Review
4. Phase 1-B Model Runtime Contract
5. System Architecture
6. Project Directory Structure
7. Model Strategy
8. Python Environment Strategy
9. Runtime Governance
10. Roadmap
11. ADR

### 実装者

1. Common Handoff
2. Latest Designer Review
3. Phase 1-B Model Runtime Contract
4. ADR-0006
5. Implementer Handoff
6. Latest Implementer Status
7. Project Requirements
8. System Architecture
9. Project Directory Structure
10. Model Strategy
11. Python Environment Strategy
12. Roadmap

Phase 1-B専用Handoff作成後は、そのHandoffをImplementer Reading Orderの先頭側へ追加する。

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Latest Designer Review
5. Phase 1-B Model Runtime Contract
6. Model Strategy
7. Runtime Governance
8. Audit／Security
9. ADR

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性を完了

Phase 1-B
Model Runtime Contract詳細設計を作成
ユーザーReview／ADR Acceptance／実装担当Handoff待ち
```

Phase 1-B Design Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Multi-TurnはPhase 2
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Implementation未許可：

- Source／Config作成
- Model SHA-512計算とRegistry登録
- Production Adapter／CLI実装
- Dependency変更
- Phase 2以降

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- Qwen3 Soft Switchでは空Thinking Tagが残る場合がある
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の25文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 7
Index        : 1
Total        : 25
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 25
Historical Documents : 14
Total Stored Files    : 39
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

<!-- SOURCE_END 6: docs/documentation_index_20260718223203.md -->

---

<!-- SOURCE_BEGIN 7: docs/documentation_index_20260718224308.md -->

### Source 7: `docs/documentation_index_20260718224308.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718224308.md`
- Source SHA-512: `dfde2560188c8b22f93e151c905440fbd7792d3d0cc5dd8f8f5e7ec0dd706504e119301090803ef899735745bdca29e193ca71d89092e0c64dbcb340c729d222`
- Source Size: `13298` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 22:43:08 JST`
- 更新日時: `2026-07-18 22:43:08 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718224308`
- supersedes: `documentation_index_20260718223203.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
5. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
6. [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| approved | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| ready | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装担当。実装許可／Write Scope確認待ち |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Latest Designer Review
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Phase 1-B Implementer Handoff
7. System Architecture
8. Project Directory Structure
9. Model Strategy
10. Python Environment Strategy
11. Runtime Governance
12. Roadmap

### 実装者

1. Latest Documentation Index
2. Phase 1-B Implementer Handoff
3. Phase 1-B Model Runtime Contract
4. ADR-0006 Accepted
5. Common Handoff
6. Latest Designer Review
7. General Implementer Handoff
8. Latest Implementer Status
9. Python Environment Strategy
10. Project Directory Structure
11. Model Strategy
12. System Architecture

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Latest Designer Review
7. Model Strategy
8. Runtime Governance
9. Audit／Security

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性を完了

Phase 1-B
Model Runtime Contract詳細設計 : Approved
ADR-0006                       : Accepted
Implementer Handoff            : Ready
Source Implementation          : Not Started／Not Authorized
```

Phase 1-B Implementation Gate：

1. ユーザーによるPhase 1-B実装開始許可
2. `config/`作成・変更許可
3. 必要な場合の`pyproject.toml`変更許可
4. Model SHA-512計算許可
5. 実Model／Metal Integration Test実行許可

Locked Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Multi-TurnはPhase 2
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- Qwen3 Soft Switchでは空Thinking Tagが残る場合がある
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の26文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 8
Index        : 1
Total        : 26
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) |
| historical | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 26
Historical Documents : 16
Total Stored Files    : 42
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 7: docs/documentation_index_20260718224308.md -->

---

<!-- SOURCE_BEGIN 8: docs/documentation_index_20260718233938.md -->

### Source 8: `docs/documentation_index_20260718233938.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260718233938.md`
- Source SHA-512: `d79079cf915e6e087f6a1c43980c7a77eced714728a0369062aa81a6e8d695537bb981e7889a7972c4b0bccbd760ef27cfc65155fe99dc7168a8d6050ab621f0`
- Source Size: `14496` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-18 23:39:38 JST`
- 更新日時: `2026-07-18 23:39:38 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260718233938`
- supersedes: `documentation_index_20260718224308.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
5. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
6. [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md)
7. [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md)
8. [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| approved | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_follow_up_required | [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md) | Phase 1-B実装結果。主要経路Pass、2件Follow-up必要 |
| follow_up_required | [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md) | Ctrl+C Cooperative CancelとArtifact Digest事実性の修正依頼 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Latest Phase 1-B Designer Review
4. Latest Phase 1-B Implementer Status
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. Phase 1-B Implementer Handoff
8. System Architecture
9. Project Directory Structure
10. Model Strategy
11. Python Environment Strategy
12. Runtime Governance
13. Roadmap

### 実装者

1. Latest Documentation Index
2. Latest Phase 1-B Designer Review
3. Latest Phase 1-B Implementer Status
4. Phase 1-B Implementer Handoff
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. Common Handoff
8. General Implementer Handoff
9. Python Environment Strategy
10. Project Directory Structure
11. Model Strategy
12. System Architecture

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Latest Phase 1-B Designer Review
7. Model Strategy
8. Runtime Governance
9. Audit／Security

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性を完了

Phase 1-B
Model Runtime Contract詳細設計 : Approved
ADR-0006                       : Accepted
Source Implementation          : Implemented
Static／Default Test            : Pass
実Model／Metal Test             : Pass
Designer Review                : Follow-up Required
Final Acceptance               : Pending
```

Required Phase 1-B Follow-up：

1. 実Production StreamでCtrl+Cを`generation_failed`へ変換せず、CLI Cooperative Cancel／Exit 130を成立させる
2. Hash未検証時にRegistry期待値を実測Artifact Digestとして報告しない
3. Regression Testを追加する
4. 新しいImplementer Statusを作成する
5. 設計者が再レビューする

Locked Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Multi-TurnはPhase 2
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の28文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
Index        : 1
Total        : 28
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) |
| historical | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) |
| historical | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 28
Historical Documents : 17
Total Stored Files    : 45
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 8: docs/documentation_index_20260718233938.md -->

---

<!-- SOURCE_BEGIN 9: docs/documentation_index_20260719000348.md -->

### Source 9: `docs/documentation_index_20260719000348.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719000348.md`
- Source SHA-512: `eeb79d2b0f285ecd5097be2c631713372dcb03fd6b3f85ced7084ee3e72ab103e23564d8b6be112798caca2396203a65b7807b1ea0230faa604e07db2897e7eb`
- Source Size: `15478` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 00:03:48 JST`
- 更新日時: `2026-07-19 00:03:48 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719000348`
- supersedes: `documentation_index_20260718233938.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
5. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
6. [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md)
7. [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md)
8. [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| approved | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_test_follow_up_required | [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md) | Runtime修正2件Pass、false Config Test Fixtureのみ修正必要 |
| test_follow_up_required | [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md) | Phase 1-B Runtime本体Pass、Regression Test 1件の修正依頼 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Latest Phase 1-B Designer Review
4. Latest Phase 1-B Implementer Status
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. Phase 1-B Implementer Handoff
8. System Architecture
9. Project Directory Structure
10. Model Strategy
11. Python Environment Strategy
12. Runtime Governance
13. Roadmap

### 実装者

1. Latest Documentation Index
2. Latest Phase 1-B Designer Review
3. Latest Phase 1-B Implementer Status
4. Phase 1-B Implementer Handoff
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. Common Handoff
8. General Implementer Handoff
9. Python Environment Strategy
10. Project Directory Structure
11. Model Strategy
12. System Architecture

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Latest Phase 1-B Designer Review
7. Model Strategy
8. Runtime Governance
9. Audit／Security

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性を完了

Phase 1-B
Model Runtime Contract詳細設計 : Approved
ADR-0006                       : Accepted
Runtime Source Follow-up       : Pass
実CLI Ctrl+C／Exit 130         : Pass
Artifact SHA-512事実性         : Pass
Static／Default Test            : Pass
実Model／Metal Test             : Pass
Regression Test                : 1件Fixture修正待ち
Final Acceptance               : Pending／Test-only Follow-up
```

Required Phase 1-B Test-only Follow-up：

1. `verify_artifact_hash=false`Fixtureを有効な単一Key TOMLへ修正する
2. `Literal[True]`による`invalid_configuration`を実際に検査する
3. Default／Static Gateを再実行する
4. 新しいImplementer Statusを作成する
5. 設計者が最終レビューする

Locked Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Multi-TurnはPhase 2
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Artifact SHA-512はPhase 1-Bで常時検証する
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の28文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
Index        : 1
Total        : 28
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) |
| historical | [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md) | [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md) |
| historical | [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md) | [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) |
| historical | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) |
| historical | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) |
| historical | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) | [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 28
Historical Documents : 20
Total Stored Files    : 48
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 9: docs/documentation_index_20260719000348.md -->

---

<!-- SOURCE_BEGIN 10: docs/documentation_index_20260719001604.md -->

### Source 10: `docs/documentation_index_20260719001604.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719001604.md`
- Source SHA-512: `2b56d3d6c24500fa80255830bf3585911f0187cd16c3cde1fb896ab7c121b11275deaf853fed57d9b0094fdd57e10ffa7686d8c46f2e4d41d354c963048b224f`
- Source Size: `16165` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 00:16:04 JST`
- 更新日時: `2026-07-19 00:16:04 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719001604`
- supersedes: `documentation_index_20260719000348.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
5. [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Test-only Follow-up完了、Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入、Required Follow-up完了 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Phase 1-B Final Designer Review
4. Latest Phase 1-B Implementer Status
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. System Architecture
8. Project Directory Structure
9. Model Strategy
10. Python Environment Strategy
11. Runtime Governance
12. Roadmap

### 実装者

1. Latest Documentation Index
2. Phase 1-B Final Designer Review
3. Latest Phase 1-B Implementer Status
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Common Handoff
7. General Implementer Handoff
8. Python Environment Strategy
9. Project Directory Structure
10. Model Strategy
11. System Architecture

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Phase 1-B Final Designer Review
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. Model Strategy
8. Runtime Governance
9. Audit／Security

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性 : Complete

Phase 1-B
Model Runtime Contract詳細設計 : Implemented
ADR-0006                       : Accepted
Runtime Source                 : Accepted
実CLI Ctrl+C／Exit 130         : Accepted
Artifact SHA-512事実性         : Accepted
Regression Test                : Accepted
Static／Default Test            : Pass
実Model／Metal Test             : Pass
Final Designer Review          : Accepted
Phase 1-B                      : Complete
```

Phase 1-B完了は、Phase 2または他機能の実装を自動的に解禁しない。

Next Design Gate候補：

1. Phase 2のMVP境界
2. Multi-Turn／Session／Message Contract
3. History／Storage Adapter
4. FastAPI／Web UI選定
5. HTTP Streaming／Cancel
6. 実装担当HandoffとWrite Scope

Locked Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Artifact SHA-512はPhase 1-Bで常時検証する
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の28文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
Index        : 1
Total        : 28
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) |
| historical | [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md) | [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md) |
| historical | [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md) | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) |
| historical | [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md) | [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md) |
| historical | [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md) | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) |
| historical | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) |
| historical | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) |
| historical | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) | [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md) |
| historical | [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md) | [documentation_index_20260719001604.md](../history/documentation_index_20260719001604.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 28
Historical Documents : 23
Total Stored Files    : 51
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 10: docs/documentation_index_20260719001604.md -->

---

<!-- SOURCE_BEGIN 11: docs/documentation_index_20260719001844.md -->

### Source 11: `docs/documentation_index_20260719001844.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719001844.md`
- Source SHA-512: `b682eb4b5ff08d642e48eba59c691137a65fe3e7eb7186cf91ae7ec4adfa15dc22f41a62ec5a2ecb0e76acc7279a76b197578713a71384c3d32ed71d2e00aa8d`
- Source Size: `16470` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 00:18:44 JST`
- 更新日時: `2026-07-19 00:18:44 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719001844`
- supersedes: `documentation_index_20260719001604.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

直前IndexのHistorical表に旧Phase 1-A ReviewのLink Target取り違えがあったため、Append-Onlyで本Indexへ修正した。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
5. [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)
8. [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md)

## 3. Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入、Required項目完了、非ブロッカー記録 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Test-only Follow-up完了、Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入、Required Follow-up完了 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 担当別Reading Order

### 設計者

1. Common Handoff
2. Project Requirements
3. Phase 1-B Final Designer Review
4. Latest Phase 1-B Implementer Status
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. System Architecture
8. Project Directory Structure
9. Model Strategy
10. Python Environment Strategy
11. Runtime Governance
12. Roadmap

### 実装者

1. Latest Documentation Index
2. Phase 1-B Final Designer Review
3. Latest Phase 1-B Implementer Status
4. Phase 1-B Model Runtime Contract
5. ADR-0006 Accepted
6. Common Handoff
7. General Implementer Handoff
8. Python Environment Strategy
9. Project Directory Structure
10. Model Strategy
11. System Architecture

### 対外Docs作成者

1. Common Handoff
2. Public Documentation Handoff
3. Project Requirements
4. Phase 1-B Final Designer Review
5. Phase 1-B Model Runtime Contract
6. ADR-0006 Accepted
7. Model Strategy
8. Runtime Governance
9. Audit／Security

## 9. 現在地点

```text
Phase 1-A
Environment Setup／Qwen3-4B Metal Smoke／Environment再現性 : Complete

Phase 1-B
Model Runtime Contract詳細設計 : Implemented
ADR-0006                       : Accepted
Runtime Source                 : Accepted
実CLI Ctrl+C／Exit 130         : Accepted
Artifact SHA-512事実性         : Accepted
Regression Test                : Accepted
Static／Default Test            : Pass
実Model／Metal Test             : Pass
Final Designer Review          : Accepted
Phase 1-B                      : Complete
```

Phase 1-B完了は、Phase 2または他機能の実装を自動的に解禁しない。

Next Design Gate候補：

1. Phase 2のMVP境界
2. Multi-Turn／Session／Message Contract
3. History／Storage Adapter
4. FastAPI／Web UI選定
5. HTTP Streaming／Cancel
6. 実装担当HandoffとWrite Scope

Locked Decision：

- Thinking Default OFF、設定で切替可能
- Initial Context 4,096、上限固定ではない
- 一問一答＋Streaming＋Stop CLI
- Model Port Instanceは同時に1 Modelを所有
- Phase 1-Bの同時Generation数は1
- Capability不足は明示Error
- Streaming Stopは協調Cancel
- Artifact SHA-512はPhase 1-Bで常時検証する
- Registry／Deployment Profile／Generation Profileを分離
- TOML＋Pydantic v2
- llama.cpp固有処理はAdapterへ隔離
- Performance値はConfig／Profileで交換可能

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 10. Review／Index作成運用

正式Reviewを完了した場合は、原則として同じ作業単位で次を新規作成する。

1. 新TimestampのReview文書
2. Review対象、Review結果、旧文書との世代関係を反映した新Timestampの`documentation_index`

旧Review、旧Status、旧Indexは上書きしない。

## 11. Current Snapshot構成

現在の正本Document Setには次の28文書が含まれる。

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
Index        : 1
Total        : 28
```

## 12. Historical Document Set

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md) | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) |
| historical | [project_requirements_20260718174637.md](../history/requirements/project_requirements_20260718174637.md) | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) |
| historical | [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md) | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718193435.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [common_project_handoff_20260718174637.md](../history/handoffs/common_project_handoff_20260718174637.md) | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) |
| historical | [designer_handoff_20260718174637.md](../history/handoffs/designer_handoff_20260718174637.md) | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) |
| historical | [implementer_handoff_20260718174637.md](../history/handoffs/implementer_handoff_20260718174637.md) | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) |
| historical | [implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md](../history/handoffs/implementer_status_phase_1_environment_and_metal_smoke_20260718210342.md) | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) |
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [adr_0006_model_runtime_port_and_configuration_20260718223203.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718223203.md) | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) |
| historical | [implementer_status_phase_1b_model_runtime_20260718232354.md](../history/handoffs/implementer_status_phase_1b_model_runtime_20260718232354.md) | [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md) |
| historical | [implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md](../history/handoffs/implementer_status_phase_1b_model_runtime_follow_up_20260718235802.md) | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) |
| historical | [designer_review_phase_1b_model_runtime_20260718233938.md](../history/handoffs/designer_review_phase_1b_model_runtime_20260718233938.md) | [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md) |
| historical | [designer_review_phase_1b_model_runtime_follow_up_20260719000348.md](../history/handoffs/designer_review_phase_1b_model_runtime_follow_up_20260719000348.md) | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) |
| historical | [documentation_index_20260718174637.md](../history/documentation_index_20260718174637.md) | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) |
| historical | [documentation_index_20260718193435.md](../history/documentation_index_20260718193435.md) | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) |
| historical | [documentation_index_20260718201744.md](../history/documentation_index_20260718201744.md) | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) |
| historical | [documentation_index_20260718212502.md](../history/documentation_index_20260718212502.md) | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) |
| historical | [documentation_index_20260718221255.md](../history/documentation_index_20260718221255.md) | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) |
| historical | [documentation_index_20260718223203.md](../history/documentation_index_20260718223203.md) | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) |
| historical | [documentation_index_20260718224308.md](../history/documentation_index_20260718224308.md) | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) |
| historical | [documentation_index_20260718233938.md](../history/documentation_index_20260718233938.md) | [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md) |
| historical | [documentation_index_20260719000348.md](../history/documentation_index_20260719000348.md) | [documentation_index_20260719001604.md](../history/documentation_index_20260719001604.md) |
| historical | [documentation_index_20260719001604.md](../history/documentation_index_20260719001604.md) | [documentation_index_20260719001844.md](../history/documentation_index_20260719001844.md) |

## 13. Repository内の文書総数

```text
Current Document Set : 28
Historical Documents : 24
Total Stored Files    : 52
```

Current Document Setは現在の正本構成数であり、Historical Documentsを含まない。

## 14. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 11: docs/documentation_index_20260719001844.md -->

---

<!-- SOURCE_BEGIN 12: docs/documentation_index_20260719002104.md -->

### Source 12: `docs/documentation_index_20260719002104.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719002104.md`
- Source SHA-512: `826149e10282009ef98d98da54fbc16e0de0904a420b442cb1ce3377cbf1ad0a7599a2895c136b96203d1c1e983240e9cce888397ba2780113075ac0f94962e1`
- Source Size: `9987` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 00:21:04 JST`
- 更新日時: `2026-07-19 00:21:04 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719002104`
- supersedes: `documentation_index_20260719001844.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Reviewと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

直前2世代のIndexにHistorical Linkの表示名／Target取り違えが各1件あったため、既存Indexを編集せず、本Indexで正しいCurrent Setと修正済みLinkを再掲する。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
5. [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
6. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
7. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Test-only Follow-up完了、Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入、Required Follow-up完了 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. 現在地点

```text
Phase 1-A : Complete

Phase 1-B
Model Runtime Contract詳細設計 : Implemented
Runtime Source                 : Accepted
実CLI Ctrl+C／Exit 130         : Accepted
Artifact SHA-512事実性         : Accepted
Regression Test                : Accepted
Static／Default Test            : Pass
実Model／Metal Test             : Pass
Final Designer Review          : Accepted
Phase 1-B                      : Complete
```

Phase 1-B完了は、Phase 2または他機能の実装を自動的に解禁しない。

Next Design Gate候補：

1. Phase 2のMVP境界
2. Multi-Turn／Session／Message Contract
3. History／Storage Adapter
4. FastAPI／Web UI選定
5. HTTP Streaming／Cancel
6. 実装担当HandoffとWrite Scope

Known Non-blocking Item：

- 通常Setupでも`llama-cpp-python`を毎回Native再Buildする
- 同一ModelのIdempotent Load判定は現在Model Keyだけを比較する
- Distribution Revision／Commitを推測で埋めない
- Raw Output／Display Output分離は後続設計で確定する
- `.DS_Store`再生成は別のRepository Hygiene事項

## 9. Historical ChainとLink修正

完全なHistorical Chainは、直前Indexに保持されている。

- [documentation_index_20260719001844.md](../history/documentation_index_20260719001844.md)

本Indexでは、直前2世代で取り違えた次のLinkを正本として修正する。

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [designer_review_phase_1_environment_and_metal_smoke_20260718212502.md](../history/handoffs/designer_review_phase_1_environment_and_metal_smoke_20260718212502.md) | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) |
| historical | [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md) | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) |
| historical | [documentation_index_20260719001604.md](../history/documentation_index_20260719001604.md) | [documentation_index_20260719001844.md](../history/documentation_index_20260719001844.md) |
| historical | [documentation_index_20260719001844.md](../history/documentation_index_20260719001844.md) | [documentation_index_20260719002104.md](../history/documentation_index_20260719002104.md) |

## 10. Current Snapshot構成

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
Index        : 1
Current      : 28
Historical   : 25
Total        : 53
```

## 11. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 12: docs/documentation_index_20260719002104.md -->

---

<!-- SOURCE_BEGIN 13: docs/documentation_index_20260719004209.md -->

### Source 13: `docs/documentation_index_20260719004209.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719004209.md`
- Source SHA-512: `764cb6b6a1105573876def15ebdb1feb8bc5a223bcd4ece332be296e3c138c58a305224a0d1d607d4a529c7ea2928a4f4128aae28782eaa3fb7b37096c63e26c`
- Source Size: `8832` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 00:42:09 JST`
- 更新日時: `2026-07-19 00:42:09 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719004209`
- supersedes: `documentation_index_20260719002104.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)
5. [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
6. [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md)
7. [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md)
8. [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | Phase、現在地点、次の設計、未決事項 |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Test-only Follow-up完了、Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入、Required Follow-up完了 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A                      : Complete
Phase 1-B                      : Complete
Phase 1 Mac User Verification : Pass
Phase 1 macOS User Manual     : Current
Phase 1-C Cross-platform Hook : Next Design Task
```

Phase 1-C候補：

- Windows x86_64 Profile
- CPU／CUDA／Vulkan等のBackend Profile
- PowerShell Setup Hook
- Cross-platform Device識別
- GPU Offload RequirementのProfile化
- OS別Path／Test境界

Phase 1-Cの実装は、新しい設計、ADR、Handoffおよびユーザー許可後に行う。

## 10. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719002104.md](../history/documentation_index_20260719002104.md)

本Indexによる追加関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_index_20260719002104.md](../history/documentation_index_20260719002104.md) | [documentation_index_20260719004209.md](../history/documentation_index_20260719004209.md) |

## 11. Current Snapshot構成

```text
Requirements : 2
Architecture : 7
Governance   : 2
ADR          : 6
Handoffs     : 10
User Manual  : 1
Index        : 1
Current      : 29
Historical   : 26
Total        : 55
```

## 12. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 13: docs/documentation_index_20260719004209.md -->

---

<!-- SOURCE_BEGIN 14: docs/documentation_index_20260719013109.md -->

### Source 14: `docs/documentation_index_20260719013109.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719013109.md`
- Source SHA-512: `52a1abce081b525d91dbfb890d315a0bcfbacbaf80c9ead7109e02af57ac9fca7adfb24579ffacf95f272357b716ee962252ab41aa07d912c6376f249ff28f73`
- Source Size: `11177` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719013109`
- supersedes: `documentation_index_20260719004209.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
5. [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
6. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
7. [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
8. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
9. [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md)
10. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |
| current_approved | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C、全Platformを表現可能にするRequirement、Scope、Acceptance |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| current_approved_design | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Contract、Profile、Capability分離、Migration |
| proposed_deferred | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | 低スペック要因、Language Default、Thinking表示、Parser、Governance Sample |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260719013109.md](../history/architecture/implementation_roadmap_20260719013109.md) | Phase 1-A／1-B完了、Phase 1-C設計承認、Response Policy候補、後続Phase |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |
| accepted | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | 全Platformを表現するHook、Capability再分類、Profile Resolver、Verification State |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B Test-only Follow-up完了、最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| ready_for_implementation_authorization | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C実装担当Handoff、Response PolicyはScope外参照 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1 Mac User Verification                 : Pass
Phase 1-C Deployment／Platform／Acceleration  : Approved Design
Phase 1-C Implementation                      : Awaiting User Authorization
Response Language／Thinking Output            : Proposed／Deferred
```

Phase 1-CはWindows、Linux、CUDA等を今実装するPhaseではない。

全Platformを後から表現・接続できる境界を作り、Current Mac／Metal Regressionを通す。

## 10. Supersession Update

本Snapshotで追加・更新した関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md) | [implementation_roadmap_20260719013109.md](../history/architecture/implementation_roadmap_20260719013109.md) |
| historical | [documentation_index_20260719004209.md](../history/documentation_index_20260719004209.md) | [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md) |

新規系列：

- `phase_1c_deployment_platform_acceleration_requirements`
- `phase_1c_deployment_platform_acceleration_architecture`
- `response_language_and_thinking_output_policy`
- `adr_0007_deployment_platform_acceleration_abstraction`
- `designer_handoff_phase_1c_deployment_platform_acceleration`

## 11. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719004209.md](../history/documentation_index_20260719004209.md)

## 12. Current Snapshot構成

```text
Requirements : 3
Architecture : 9
Governance   : 2
ADR          : 7
Handoffs     : 11
User Manual  : 1
Index        : 1
Current      : 34
Historical   : 28
Total        : 62
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 14: docs/documentation_index_20260719013109.md -->

---

<!-- SOURCE_BEGIN 15: docs/documentation_index_20260719030341.md -->

### Source 15: `docs/documentation_index_20260719030341.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719030341.md`
- Source SHA-512: `77097e3a55b5511cb6c66a6d5b6dfbfaf5b27245f21acf7b49dc80b7f570a8afeebcfb3ad7ff4f0800717901fed65653a1e5a78ef133c11ee489e0ff5c8ab2b8`
- Source Size: `12126` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 03:03:41 JST`
- 更新日時: `2026-07-19 03:03:41 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719030341`
- supersedes: `documentation_index_20260719013109.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
5. [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
6. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
7. [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
8. [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md)
9. [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](../history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md)
10. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
11. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |
| current_approved | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C、全Platformを表現可能にするRequirement、Scope、Acceptance |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| implementation_follow_up | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Contract、Profile、Capability分離、Migration |
| proposed_deferred | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | 低スペック要因、Language Default、Thinking表示、Parser、Governance Sample |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260719013109.md](../history/architecture/implementation_roadmap_20260719013109.md) | Phase 1-A／1-B完了、Phase 1-C設計承認、Response Policy候補、後続Phase |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |
| accepted | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | 全Platformを表現するHook、Capability再分類、Profile Resolver、Verification State |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B Test-only Follow-up完了、最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implementation_follow_up | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C実装担当Handoff、Response PolicyはScope外参照 |
| reviewed_changes_requested | [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md) | Executed State修正は受理、Phase 1-C残修正あり |
| changes_requested | [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](../history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md) | Phase 1-C部分受入、OS拡張性とPre-load Validationを要求 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1 Mac User Verification                 : Pass
Phase 1-C Deployment Contract                 : Implemented
Phase 1-C Executed State Follow-up             : Accepted
Phase 1-C OS／Architecture Extensibility       : Changes Required
Phase 1-C Host Pre-load Validation             : Changes Required
Phase 1-C Final Acceptance                     : Pending
Response Language／Thinking Output             : Proposed／Deferred
```

Phase 1-CはWindows、Linux、CUDA等を現在のMachineで実装・検証するPhaseではない。

全Platformを後から表現・接続できる境界を成立させ、Current Mac／Metal Regressionを維持する。

## 10. Supersession Update

本Snapshotで追加・更新した関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_20260719021411.md) | [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md) |
| historical | [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md) | [documentation_index_20260719030341.md](../history/documentation_index_20260719030341.md) |

新規系列：

- `designer_review_phase_1c_deployment_platform_acceleration_follow_up`

## 11. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719013109.md](../history/documentation_index_20260719013109.md)

## 12. Current Snapshot構成

```text
Requirements : 3
Architecture : 9
Governance   : 2
ADR          : 7
Handoffs     : 13
User Manual  : 1
Index        : 1
Current      : 36
Historical   : 30
Total        : 66
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 15: docs/documentation_index_20260719030341.md -->

---

<!-- SOURCE_BEGIN 16: docs/documentation_index_20260719033038.md -->

### Source 16: `docs/documentation_index_20260719033038.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719033038.md`
- Source SHA-512: `e67a24535bab3cd46869710f78aac7730ce8a842431eec15f7be6a0b4bce5a651add46fd5a0a642ec323656dbd38bdd888241c169fdcda827e5f2f662473c2a6`
- Source Size: `12551` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 03:30:38 JST`
- 更新日時: `2026-07-19 03:30:38 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719033038`
- supersedes: `documentation_index_20260719030341.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md)
5. [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
6. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
7. [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
8. [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](../history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md)
9. [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](../history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md)
10. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
11. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |
| current_approved | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C、全Platformを表現可能にするRequirement、Scope、Acceptance |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| implementation_follow_up | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Contract、Profile、Capability分離、Migration |
| proposed_deferred | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | 低スペック要因、Language Default、Thinking表示、Parser、Governance Sample |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260719013109.md](../history/architecture/implementation_roadmap_20260719013109.md) | Phase 1-A／1-B完了、Phase 1-C設計承認、Response Policy候補、後続Phase |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |
| accepted | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | 全Platformを表現するHook、Capability再分類、Profile Resolver、Verification State |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B Test-only Follow-up完了、最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implementation_follow_up | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C実装担当Handoff、Response PolicyはScope外参照 |
| reviewed_changes_requested | [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](../history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md) | Registry／Pre-load修正は受理、参照整合Follow-upあり |
| changes_requested | [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](../history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md) | Phase 1-C主要修正受入、Registry参照整合を要求 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1 Mac User Verification                 : Pass
Phase 1-C Deployment Contract                 : Implemented
Phase 1-C Executed State Boundary             : Accepted
Phase 1-C OS／Architecture Registry            : Accepted
Phase 1-C Host Pre-load Validation             : Accepted
Phase 1-C Registry Reference Integrity         : Changes Required
Phase 1-C Final Acceptance                     : Pending
Response Language／Thinking Output             : Proposed／Deferred
```

Phase 1-Cの主要なCross-platform HookとCurrent Mac／Metal Regressionは成立している。

最終受入前に、Platform RegistryのCanonical Key参照整合を追加する。

## 10. Supersession Update

本Snapshotで追加・更新した関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md](../history/handoffs/implementer_status_phase_1c_deployment_platform_acceleration_follow_up_20260719025250.md) | [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](../history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md) |
| historical | [designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md](../history/handoffs/designer_review_phase_1c_deployment_platform_acceleration_follow_up_20260719030341.md) | [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](../history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md) |
| historical | [documentation_index_20260719030341.md](../history/documentation_index_20260719030341.md) | [documentation_index_20260719033038.md](../history/documentation_index_20260719033038.md) |

## 11. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719030341.md](../history/documentation_index_20260719030341.md)

## 12. Current Snapshot構成

```text
Requirements : 3
Architecture : 9
Governance   : 2
ADR          : 7
Handoffs     : 13
User Manual  : 1
Index        : 1
Current      : 36
Historical   : 33
Total        : 69
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 16: docs/documentation_index_20260719033038.md -->

---

<!-- SOURCE_BEGIN 17: docs/documentation_index_20260719035156.md -->

### Source 17: `docs/documentation_index_20260719035156.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719035156.md`
- Source SHA-512: `37bfb42174de4d753a9cd962931d276a5be9ebcab31f2685d4ab15f085a2785351626a804a3b462c8961b5928b2b1dc725309f27d86fc7e01924be71e2b7638f`
- Source Size: `11851` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 03:51:56 JST`
- 更新日時: `2026-07-19 03:51:56 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719035156`
- supersedes: `documentation_index_20260719033038.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md)
5. [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
6. [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
7. [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md)
8. [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
9. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
10. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、Scope、Acceptance、全Criteria Pass |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Contract、Registry、Resolver、Validation、Observation |
| proposed_deferred | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | 低スペック要因、Language Default、Thinking表示、Parser、Governance Sample |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| historical_roadmap_snapshot | [implementation_roadmap_20260719013109.md](../history/architecture/implementation_roadmap_20260719013109.md) | Phase 1-C実装開始前のRoadmap Snapshot。現在地点は本Indexを参照 |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | 全Platform Hook、Capability再分類、Platform Registry、Pre-load／Post-load Validation |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B Test-only Follow-up完了、最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C実装担当Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Follow-up Status、全Acceptance Pass |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Current Native Verification                  : macOS／Apple Silicon arm64／Metal
Response Language／Thinking Output            : Proposed／Deferred
Next Phase                                   : Not Selected／Not Authorized
```

Phase 1-Cの全Acceptance CriteriaはPassした。

次PhaseのRequirements、設計または実装は、ユーザーが議題と範囲を決定した後に開始する。

## 10. Supersession Update

本Snapshotで追加・更新した関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md](../history/handoffs/implementer_status_phase_1c_platform_registry_and_preload_validation_follow_up_20260719031938.md) | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) |
| historical | [designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md](../history/handoffs/designer_review_phase_1c_platform_registry_and_preload_validation_follow_up_20260719033038.md) | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) |
| historical | [documentation_index_20260719033038.md](../history/documentation_index_20260719033038.md) | [documentation_index_20260719035156.md](../history/documentation_index_20260719035156.md) |

## 11. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719033038.md](../history/documentation_index_20260719033038.md)

## 12. Current Snapshot構成

```text
Requirements : 3
Architecture : 9
Governance   : 2
ADR          : 7
Handoffs     : 13
User Manual  : 1
Index        : 1
Current      : 36
Historical   : 36
Total        : 72
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 17: docs/documentation_index_20260719035156.md -->

---

<!-- SOURCE_BEGIN 18: docs/documentation_index_20260719040237.md -->

### Source 18: `docs/documentation_index_20260719040237.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719040237.md`
- Source SHA-512: `2ce3ec876f37536c17cfea7a840899e75fe9930e557da7bef3fe5432a372f3a31eaa7f5ca283e0d23e3d9fa12dfed21935e0dd4e85d773e3e5dabc715fa44313`
- Source Size: `12601` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719040237`
- supersedes: `documentation_index_20260719035156.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書との世代関係を示す最新Indexである。

同じ主題のDocumentが複数存在する場合、File名末尾のTimestampが最も新しいDocumentを最新とする。

`documentation_index`もTimestampが最も新しいものを最新Indexとする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719040237.md](../history/architecture/implementation_roadmap_20260719040237.md)
5. [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
6. [phase_1d_response_language_requirements_20260719040237.md](../history/requirements/phase_1d_response_language_requirements_20260719040237.md)
7. [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md)
8. [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
9. [designer_handoff_phase_1d_response_language_20260719040237.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md)
10. [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
11. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | File名、Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約、現在の決定 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、Scope、Acceptance、全Criteria Pass |
| accepted_ready_for_implementation_authorization | [phase_1d_response_language_requirements_20260719040237.md](../history/requirements/phase_1d_response_language_requirements_20260719040237.md) | `ja／en／auto`、Default、優先順位、Composition、Acceptance |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | 機能別Module＋Port／Adapter、Phase別Directory、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry、GitHub方針 |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Package Version、Dependency Group、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Phase 1-B Contract、Port、Capability、Error、Registry、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Contract、Registry、Resolver、Validation、Observation |
| accepted_ready_for_implementation_authorization | [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md) | Response Contract、Resolver、Message Composer、Config／CLI Integration |
| partially_refined_phase_1e_source | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | Response Language部分はPhase 1-Dで具体化、Thinking部分はPhase 1-E設計元 |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260719040237.md](../history/architecture/implementation_roadmap_20260719040237.md) | Phase 1-A～1-E、Phase 1-D／1-E分割、現在地点、後続Phase |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、説明、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp File、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Initial ArchitectureとしてModular Monolithを採用 |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Phase単位Install、3.12 Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、TOML Registry／Profile、Phase 1-B CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | 全Platform Hook、Capability再分類、Platform Registry、Pre-load／Post-load Validation |
| accepted | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Default `ja`、Application Policy、Phase 1-D／1-E分離 |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境設計から実装者役への専用引き継ぎ |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up実装結果 |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A Follow-up受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B実装指示の基準文書 |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B Test-only Follow-up完了、最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C実装担当Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Follow-up Status、全Acceptance Pass |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| ready_for_implementation_authorization | [designer_handoff_phase_1d_response_language_20260719040237.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md) | Phase 1-D実装担当専用Handoff |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 将来の対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、動作確認、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Phase 1-D Response Language Policy            : Designed／Accepted／Implementation Not Authorized
Phase 1-E Thinking Presentation Policy        : Planned／Not Designed／Not Authorized
Current Native Verification                  : macOS／Apple Silicon arm64／Metal
```

Phase 1-DのRequirements、Architecture、ADRおよび実装担当Handoffは作成済みである。

Phase 1-DのSource／Config／Test実装は、ユーザーが明示的に実装開始を許可した後に行う。

Phase 1-EはPhase名と責務分離だけが決定しており、要件・設計はPhase 1-D完了後に確定する。

## 10. Supersession Update

本Snapshotで追加・更新した関係：

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementation_roadmap_20260719013109.md](../history/architecture/implementation_roadmap_20260719013109.md) | [implementation_roadmap_20260719040237.md](../history/architecture/implementation_roadmap_20260719040237.md) |
| historical | [documentation_index_20260719035156.md](../history/documentation_index_20260719035156.md) | [documentation_index_20260719040237.md](../history/documentation_index_20260719040237.md) |

`response_language_and_thinking_output_policy_20260719013109.md`は削除・置換しない。Response Language部分はPhase 1-D文書で具体化し、Thinking部分をPhase 1-E設計元として保持する。

## 11. Historical Chain

直前までの完全なHistorical Chainは、次のIndexに保持されている。

- [documentation_index_20260719035156.md](../history/documentation_index_20260719035156.md)

## 12. Current Snapshot構成

```text
Requirements : 4
Architecture : 10
Governance   : 2
ADR          : 8
Handoffs     : 14
User Manual  : 1
Index        : 1
Current      : 40
Historical   : 38
Total        : 78
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

<!-- SOURCE_END 18: docs/documentation_index_20260719040237.md -->

---

<!-- SOURCE_BEGIN 19: docs/documentation_index_20260719041847.md -->

### Source 19: `docs/documentation_index_20260719041847.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719041847.md`
- Source SHA-512: `81fbcc2f2d8beb0d836f2136fd3692f08bb7f963af6e5a7037f8d4b2ea41f3bc7e61b83b3d8dfd4a35c776ee30cce6327ade0583031c3484adca7613b522f4bf`
- Source Size: `13190` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719041847`
- supersedes: `documentation_index_20260719040237.md`

## 1. この索引の役割

この文書は現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと過去文書との世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719041847.md](../history/architecture/implementation_roadmap_20260719041847.md)
5. [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
6. [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
7. [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
8. [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md)
9. [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
10. [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
11. [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md)
12. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 3. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| accepted_ready_for_implementation_authorization | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| accepted_ready_for_implementation_authorization | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |

## 4. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| accepted_ready_for_implementation_authorization | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| accepted_ready_for_implementation_authorization | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| partially_refined_phase_1e_source | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | Thinking部分をPhase 1-E設計元として保持 |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| current | [implementation_roadmap_20260719041847.md](../history/architecture/implementation_roadmap_20260719041847.md) | Phase 1-D Config分離＋Language、Phase 1-E、後続Phase |

## 5. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |

## 6. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`維持、Config配置をADR-0009で修正 |
| accepted | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |

## 7. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| ready_for_implementation_authorization | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 8. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 9. 現在地点

```text
Phase 1-A Environment                         : Complete／Accepted
Phase 1-B Model Runtime                       : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration  : Complete／Accepted
Phase 1-D Configuration／Response Language    : Designed／Accepted／Implementation Not Authorized
Phase 1-E Thinking Presentation Policy        : Planned／Not Designed／Not Authorized
Current Native Verification                  : macOS／Apple Silicon arm64／Metal
```

Phase 1-DのSource／Config／Test実装は、ユーザーが明示的に実装開始を許可した後に行う。

## 10. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [phase_1d_response_language_requirements_20260719040237.md](../history/requirements/phase_1d_response_language_requirements_20260719040237.md) | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) |
| historical | [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md) | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) |
| historical | [designer_handoff_phase_1d_response_language_20260719040237.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719040237.md) | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) |
| historical | [implementation_roadmap_20260719040237.md](../history/architecture/implementation_roadmap_20260719040237.md) | [implementation_roadmap_20260719041847.md](../history/architecture/implementation_roadmap_20260719041847.md) |
| historical | [documentation_index_20260719040237.md](../history/documentation_index_20260719040237.md) | [documentation_index_20260719041847.md](../history/documentation_index_20260719041847.md) |

ADR-0008は削除しない。`ja／en／auto` Decisionを保持し、Config配置だけをADR-0009で修正する。

## 11. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719040237.md](../history/documentation_index_20260719040237.md)

## 12. Current Snapshot構成

```text
Requirements : 5
Architecture : 11
Governance   : 2
ADR          : 9
Handoffs     : 14
User Manual  : 1
Index        : 1
Current      : 43
Historical   : 43
Total        : 86
```

## 13. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

<!-- SOURCE_END 19: docs/documentation_index_20260719041847.md -->

---

<!-- SOURCE_BEGIN 20: docs/documentation_index_20260719112304.md -->

### Source 20: `docs/documentation_index_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719112304.md`
- Source SHA-512: `e73939273d2a3ce1bc23a38131712990739e2dd4de66904257ae06d6e73545e2e5c2fbbf3f576fc3945ee82e9e38596da55c7b3b691dde5c7fa1420c779857af`
- Source Size: `20838` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719112304`
- supersedes: `documentation_index_20260719041847.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。旧Fileの内容、Status、Linkは書き換えない。

## 2. 今回のSnapshotで確定したこと

- Phase 1-E後のProjectを、疎結合なAI実験・Runtime Governance Platformとして再編した。
- UIより前にComponent Registry、Experiment Runtime、Event／Status／Minimal Audit、Lightning AI Studioを置く。
- 共有Governance Control Plane + 分散Enforcement Point + Explicit Bindingを採用した。
- すべての任意ComponentとGovernanceに、個別Switchまたは`off／observe／enforce`を持たせる。
- ARGD／DAGD／CDOGDを含む全GDを任意とし、Definition 0件を正式Baselineにした。
- GD名、数、Path、SchemaをCoreにハードコードしない。
- Main GovernanceでGeneric Definition Platformを実証し、複数GDのDynamic RoutingはPhase 9へ延期した。
- 第一外部開発・検証環境はLightning AI Studio、ZeroGPUはPhase 10候補とした。
- Basic UIはModel、Response Language、Chat Action、Simple Statusに絞り、他を`開発・研究設定`に分離した。
- 旧Roadmapを後継Roadmapで置換した。
- 旧Index後に作成されたPhase 1-D実装Statusを索引に取り込んだ。Reviewは未実施のためAcceptedとしていない。

## 3. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md)
5. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
6. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
7. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
8. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
9. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
10. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
11. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
12. [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
13. [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
14. [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
15. [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)
16. [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md)
17. [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md)
18. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_review_requested | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_review_requested | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_review_requested | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_review_requested | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| partially_refined_phase_1e_source | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | Thinking部分をPhase 1-E設計元として保持 |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md) | Phase 0～10、Milestone、Current Position、Authorization Boundary |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`維持、Config配置をADR-0009で修正 |
| accepted_implemented_review_requested | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |

## 8. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implementation_complete_review_requested | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| implementation_complete_review_requested | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告、設計Review待ち |
| planning_handoff_implementation_not_authorized | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の実装担当への全体計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 9. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 10. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Implemented／Review Requested／Not Yet Accepted
Phase 1-E Thinking Presentation                    : Planned／Not Designed／Not Authorized
Phase 2+                                            : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                         : macOS／Apple Silicon arm64／Metal
Planned External Verification                       : Lightning AI Studio／Linux x86_64／CUDA
```

## 11. Phase 2以降のCurrent Roadmap

```text
Phase 2  Experimental Runtime Control Plane
  2-A Component Registry／Switchboard
  2-B Experiment Runtime
  2-C Event／Status／Minimal Audit
  2-D Lightning AI Studio

Phase 3  Generic Governance Definition Platform + Main Governance
Phase 4  Conversation Application／Web UI
Phase 5  Guardrail／Security／Policy
Phase 6  Judge／Evaluation／Repair
Phase 7  RAG／Data Governance
Phase 8  Agent／Tool／Memory
Phase 9  Multi-Governance Orchestration
Phase 10 Hardening／Public Release／Expansion
```

## 12. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementation_roadmap_20260719041847.md](../history/architecture/implementation_roadmap_20260719041847.md) | [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md) |
| historical | [documentation_index_20260719041847.md](../history/documentation_index_20260719041847.md) | [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md) |

その他の今回作成文書は新規系列であり、置換先を持たない。

## 13. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719041847.md](../history/documentation_index_20260719041847.md)

## 14. Current Snapshot構成

```text
Requirements : 7
Architecture : 15
Governance   : 3
ADR          : 13
Handoffs     : 16
User Manual  : 1
Index        : 1
Current      : 56
Historical   : 45
Total        : 101
```

## 15. 今回作成したSnapshot文書

### Requirements

- [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)

### Architecture

- [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
- [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
- [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
- [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
- [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md)

### Governance

- [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)

### ADR

- [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
- [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
- [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
- [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)

### Handoff

- [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md)

### Index

- [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)

## 16. Authorization Boundary

今回の許可はDocs作成に限られる。次は未解禁である。

- Phase 1-DのReview／Accepted判定
- Phase 1-Eの設計／実装
- Phase 2以降のSource／Config／Test／Directory変更
- Dependency Install
- Model Download
- ARGD／DAGD SourceのProject内Copy／Snapshot
- Lightning Studio作成／GPU／課金／Upload／Download
- ZeroGPU操作

## 17. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

<!-- SOURCE_END 20: docs/documentation_index_20260719112304.md -->

---

<!-- SOURCE_BEGIN 21: docs/documentation_index_20260719122035.md -->

### Source 21: `docs/documentation_index_20260719122035.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719122035.md`
- Source SHA-512: `62776398a038219fa696cb91bfd1f939d3d5b13b1ac0db214c38271a9b3023b86e4e1e931f2a26defc330f3af4a800cf3ddbe55e2614da7af0ea941ed7c6c663`
- Source Size: `18490` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 12:20:35 JST`
- 更新日時: `2026-07-19 12:20:35 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719122035`
- supersedes: `documentation_index_20260719112304.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- Phase 1-DのSource、Config、Test、Implementer Statusを設計Reviewした。
- Blocking／High／Medium Findingは0件であった。
- Acceptance Criteria 16／16をPassと判定した。
- Static、Default Test、Environment、Lock／Offline、Native Metal、Real CLI、Production Acceptanceを独立再実行した。
- Phase 1-Dを`Complete／Accepted`へ更新した。
- RoadmapのCurrent PositionとNext Actionを更新した。
- 次の設計対象はPhase 1-E Thinking Presentationである。

## 3. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719122035.md](../history/architecture/implementation_roadmap_20260719122035.md)
5. [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
6. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
7. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
8. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
9. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
10. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
11. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
12. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
13. [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md)
14. [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md)
15. [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md)
16. [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md)
17. [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md)
18. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| phase_1e_design_source | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | Thinking部分をPhase 1-E設計元として保持 |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719122035.md](../history/architecture/implementation_roadmap_20260719122035.md) | Phase 1-D Accepted、Phase 1-EがNext、Phase 0～10 |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |

## 8. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告／Review済み |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 9. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 10. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Planned／Not Designed／Not Authorized
Phase 2+                                            : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                         : macOS／Apple Silicon arm64／Metal
Planned External Verification                       : Lightning AI Studio／Linux x86_64／CUDA
```

## 11. Phase 1-D Independent Gate Summary

```text
Ruff Format        : Pass／54 files
Ruff Check         : Pass
Mypy Strict        : Pass／54 source files
Compileall         : Pass
Default Pytest     : 94 passed, 2 deselected
Model Smoke        : 2 passed, 94 deselected
Environment        : Pass／Python 3.13.14／Metal
uv Lock            : Pass／117 packages
uv Offline Dry Run : Pass／115 packages／No changes
Real CLI ja        : 成功。
Real CLI en        : success
Real CLI auto      : OK
Production Runtime : success
```

## 12. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementation_roadmap_20260719112304.md](../history/architecture/implementation_roadmap_20260719112304.md) | [implementation_roadmap_20260719122035.md](../history/architecture/implementation_roadmap_20260719122035.md) |
| historical | [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md) | [documentation_index_20260719122035.md](../history/documentation_index_20260719122035.md) |

Phase 1-D Reviewは新規系列であり、置換先を持たない。

## 13. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)

## 14. Current Snapshot構成

```text
Requirements : 7
Architecture : 15
Governance   : 3
ADR          : 13
Handoffs     : 17
User Manual  : 1
Index        : 1
Current      : 57
Historical   : 47
Total        : 104
```

## 15. 今回作成したSnapshot文書

- [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
- [implementation_roadmap_20260719122035.md](../history/architecture/implementation_roadmap_20260719122035.md)
- [documentation_index_20260719122035.md](../history/documentation_index_20260719122035.md)

## 16. Next Design Target

```text
Phase 1-E Thinking Presentation
  ├─ Thinking実行と表示の分離
  ├─ 表示／非表示
  ├─ Display Label
  ├─ Model Protocol Parser
  ├─ Streaming Filter
  ├─ Raw／Display Output
  └─ 保存Policy
```

## 17. Authorization Boundary

Phase 1-DはAcceptedである。Phase 1-Eの設計は次の対象として進められる。

ただし、次は未解禁である。

- Phase 1-EのSource／Config／Test実装
- Phase 2以降の実装
- Dependency Install
- Model Download
- Lightning Studio／ZeroGPU操作

## 18. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す

<!-- SOURCE_END 21: docs/documentation_index_20260719122035.md -->

---

<!-- SOURCE_BEGIN 22: docs/documentation_index_20260719123547.md -->

### Source 22: `docs/documentation_index_20260719123547.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719123547.md`
- Source SHA-512: `3b45b63aa592a87cc74f413f4cbe2ed5d3020bb581bc6a361061f9333d016e2491771bcc2a82e6e30134fe02c1af5ee79245377d9f7a96356ce9df73333946e7`
- Source Size: `20454` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719123547`
- supersedes: `documentation_index_20260719122035.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- Phase 1-E Thinking Presentationの詳細Requirementsを作成した。
- Model Port後段の独立Presentation Module Architectureを作成した。
- Thinking Execution／Parsing／Presentation／Persistenceを分離した。
- Default候補を`disabled／hidden／推論／disabled`とした。
- Application Config Schema `2`とModel Definition Schema `2`のMigrationを提案した。
- Model DefinitionのParser Keyによる非ハードコード構成を提案した。
- Stateful Streaming Parser、Hidden No-flash、Custom Display Labelを定義した。
- Raw Reasoning PersistenceをPhase 1-Eで`disabled`に制限した。
- Thinking FlagによるSamplingの暗黙自動切替を採用しない方針とした。
- ADR-0014を`proposed`、Implementer HandoffをDraftとして作成した。
- Phase 1-Eの現在地点を`Designed／Proposed Decision／Not Authorized`へ更新した。

## 3. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719123547.md](../history/architecture/implementation_roadmap_20260719123547.md)
5. [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
6. [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
7. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
8. [designer_handoff_phase_1e_thinking_presentation_20260719123547.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md)
9. [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
10. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
11. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
12. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
13. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
14. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
15. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
16. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
17. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| proposed_ready_for_user_review | [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md) | Execution／Parsing／Presentation／Persistence分離、22 Criteria |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| proposed_ready_for_user_review | [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md) | Presentation Module、Parser Registry、Stateful Streaming、CLI |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719123547.md](../history/architecture/implementation_roadmap_20260719123547.md) | Phase 1-E Designed／Proposed、Phase 0～10 |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |
| proposed | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md) | Thinking 4責務分離、Parser Key、Hidden No-flash、Raw保存OFF |

## 8. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告／Review済み |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| draft_waiting_for_adr_acceptance_and_implementation_authorization | [designer_handoff_phase_1e_thinking_presentation_20260719123547.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md) | Phase 1-E実装境界／実装未解禁 |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 9. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 10. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Designed／Proposed Decision／Not Authorized
Phase 2+                                           : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                        : macOS／Apple Silicon arm64／Metal
Planned External Verification                      : Lightning AI Studio／Linux x86_64／CUDA
```

## 11. Phase 1-E Proposed Decision Summary

```text
Execution Default      : disabled
Visibility Default     : hidden
Display Label Default  : 推論
Raw Persistence        : disabled only
Application Schema     : 2
Model Definition Schema: 2
Parser Selection       : Model Definition parser_key
Streaming              : Stateful／Delimiter Split Safe
Hidden                  : No-flash
Sampling                : No implicit switch
Raw Model Port Contract : Unchanged
```

## 12. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [implementation_roadmap_20260719122035.md](../history/architecture/implementation_roadmap_20260719122035.md) | [implementation_roadmap_20260719123547.md](../history/architecture/implementation_roadmap_20260719123547.md) |
| historical | [documentation_index_20260719122035.md](../history/documentation_index_20260719122035.md) | [documentation_index_20260719123547.md](../history/documentation_index_20260719123547.md) |
| historical_design_source | [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md) | [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md) |

Phase 1-E Requirements、ADRおよびHandoffは新規系列である。

## 13. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719122035.md](../history/documentation_index_20260719122035.md)

## 14. Current Snapshot構成

```text
Requirements : 8
Architecture : 15
Governance   : 3
ADR          : 14
Handoffs     : 18
User Manual  : 1
Index        : 1
Current      : 60
Historical   : 50
Total        : 110
```

## 15. 今回作成したSnapshot文書

- [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md)
- [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
- [designer_handoff_phase_1e_thinking_presentation_20260719123547.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md)
- [implementation_roadmap_20260719123547.md](../history/architecture/implementation_roadmap_20260719123547.md)
- [documentation_index_20260719123547.md](../history/documentation_index_20260719123547.md)

## 16. Next Decision Target

```text
User Review
  ├─ Default disabled／hidden／推論／disabled
  ├─ Application／Model Definition Schema 2
  ├─ Model-declared Parser Key
  ├─ Stateful Streaming Parser
  ├─ Malformed Fallback
  ├─ No Raw Persistence
  └─ No Automatic Sampling Switch
       ↓
Accepted ADR／Handoff後継版
       ↓
Explicit Implementation Authorization
```

## 17. Authorization Boundary

Phase 1-EのRequirements／Architectureは設計済みだが、DecisionはProposedである。

次は未解禁である。

- Phase 1-EのSource／Config／Test実装
- Application Config／Model Definitionの実更新
- Phase 2以降の実装
- Dependency Install／Update
- Model Download
- Lightning Studio／ZeroGPU操作

## 18. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 22: docs/documentation_index_20260719123547.md -->

---

<!-- SOURCE_BEGIN 23: docs/documentation_index_20260719130303.md -->

### Source 23: `docs/documentation_index_20260719130303.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719130303.md`
- Source SHA-512: `d9fc115abbfcdd3ac18e71a8dcf5d0e509dddca18f63f412b96ceaad62317f934c7ffda8c8deb8ea58b60070ff514cc9c428164d5b4b8ed8f0a3ffba1d092f93`
- Source Size: `20872` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719130303`
- supersedes: `documentation_index_20260719123547.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- Phase 1-Eの提案Decisionがユーザーにより承認された。
- Default Display Labelを`推論`から`高度推論`へ変更した。
- `高度推論`はDisplay Channelの識別Labelであり、Reasoning品質の保証ではないと定義した。
- Phase 1-E Requirements／ArchitectureのAccepted後継版を作成した。
- ADR-0014のAccepted後継版を作成した。
- 実装担当向けの正式Handoffを作成した。
- Phase 1-Eを`Design Accepted／Ready for Implementation Authorization`へ更新した。
- Source／Config／Test実装は引き続き未解禁である。

## 3. 最初に読む文書

1. [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)
2. [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md)
3. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
4. [implementation_roadmap_20260719130303.md](../history/architecture/implementation_roadmap_20260719130303.md)
5. [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
6. [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
7. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
8. [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
9. [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md)
10. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
11. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
12. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
13. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
14. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
15. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
16. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
17. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | Append-Only、Timestamp、最新判定、読み取り専用原則 |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| accepted_ready_for_implementation_authorization | [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md) | Default `高度推論`、4責務分離、22 Criteria |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| accepted_ready_for_implementation_authorization | [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md) | Presentation Module、Parser Registry、Stateful Streaming、CLI |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719130303.md](../history/architecture/implementation_roadmap_20260719130303.md) | Phase 1-E Design Accepted、Phase 0～10 |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |
| accepted | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md) | Default `高度推論`、Thinking 4責務分離、Parser Key、Raw保存OFF |

## 8. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | 全担当Task |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告／Review済み |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| accepted_ready_for_implementation_authorization | [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md) | Phase 1-E正式実装Handoff／実装開始許可待ち |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 9. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 10. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Design Accepted／Ready for Implementation Authorization
Phase 2+                                           : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                        : macOS／Apple Silicon arm64／Metal
Planned External Verification                      : Lightning AI Studio／Linux x86_64／CUDA
```

## 11. Phase 1-E Accepted Decision Summary

```text
Execution Default       : disabled
Visibility Default      : hidden
Display Label Default   : 高度推論
Raw Persistence         : disabled only
Application Schema      : 2
Model Definition Schema : 2
Parser Selection        : Model Definition parser_key
Streaming               : Stateful／Delimiter Split Safe
Hidden                   : No-flash
Sampling                 : No implicit switch
Raw Model Port Contract  : Unchanged
```

## 12. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [phase_1e_thinking_presentation_requirements_20260719123547.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md) | [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md) |
| historical | [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md) | [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md) |
| historical | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md) | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md) |
| historical | [designer_handoff_phase_1e_thinking_presentation_20260719123547.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719123547.md) | [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md) |
| historical | [implementation_roadmap_20260719123547.md](../history/architecture/implementation_roadmap_20260719123547.md) | [implementation_roadmap_20260719130303.md](../history/architecture/implementation_roadmap_20260719130303.md) |
| historical | [documentation_index_20260719123547.md](../history/documentation_index_20260719123547.md) | [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md) |

## 13. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719123547.md](../history/documentation_index_20260719123547.md)

## 14. Current Snapshot構成

```text
Requirements : 8
Architecture : 15
Governance   : 3
ADR          : 14
Handoffs     : 18
User Manual  : 1
Index        : 1
Current      : 60
Historical   : 56
Total        : 116
```

## 15. 今回作成したSnapshot文書

- [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
- [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
- [implementation_roadmap_20260719130303.md](../history/architecture/implementation_roadmap_20260719130303.md)
- [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md)

## 16. Next Gate

```text
Requirements     : Accepted
Architecture     : Accepted
ADR              : Accepted
Designer Handoff : Accepted
       ↓
User Implementation Authorization : Waiting
       ↓
Phase 1-E Implementation
```

## 17. Authorization Boundary

Phase 1-Eの設計と正式Handoffは完了した。

次は未解禁である。

- Phase 1-E Source／Config／Test実装
- Application Config／Model Definitionの実更新
- Phase 2以降の実装
- Dependency Install／Update
- Model Download
- Lightning Studio／ZeroGPU操作

## 18. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 23: docs/documentation_index_20260719130303.md -->

---

<!-- SOURCE_BEGIN 24: docs/documentation_index_20260719142558.md -->

### Source 24: `docs/documentation_index_20260719142558.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719142558.md`
- Source SHA-512: `5345df1570459a409d4dd79140f771f695c62a1f0c52012a6abbc1ebb7b50d34e7630cab166a82dc7b5d587a0ad37370df4619d840719e49542b599b00b5ba1f`
- Source Size: `22442` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719142558`
- supersedes: `documentation_index_20260719130303.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、Operations、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- 実装担当からPhase 1-Eの実装完了と、Acceptance Criteria `22／22 Pass`が報告された。
- Phase 1-Eは設計者役による独立レビュー前であるため、`Implementation Reported／Independent Review Pending`とした。
- Backup取得の発火条件を、Top-Level Phase全体の完了を設計者役が明示した直後に固定した。
- Subphase完了、実装担当の完了報告、Review途中ではBackupを取得しないことを明文化した。
- Phase完了BackupのArchive、Manifest、Receipt、SHA-512、除外対象、復元確認をOperations Policyとして新設した。
- 設計者役、実装者役、対外向けDocs作成者役の書込権限と読み取り専用境界を正式化した。
- `docs/operations/`の正本Ownershipを設計者役とした。
- 設計者役と実装者役の分離がPhase 1の実運用で機能していることを記録した。
- 対外向けDocs作成者役は、権限境界は正式化するが、実運用評価は今後とした。
- Documentation Rules、Common Handoff、Implementation Roadmapを後継化した。
- Source、Config、Test、Backup Archiveは今回変更・作成していない。

## 3. 最初に読む文書

1. [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md)
2. [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
3. [common_project_handoff_20260719142558.md](../history/handoffs/common_project_handoff_20260719142558.md)
4. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
5. [implementation_roadmap_20260719142558.md](../history/architecture/implementation_roadmap_20260719142558.md)
6. [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md)
7. [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
8. [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
9. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
10. [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md)
11. [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)
12. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
13. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
14. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
15. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
16. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
17. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
18. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
19. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md) | Project Root、Append-Only、Timestamp、Index、Review、Role、Backup Trigger |
| accepted_current | [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md) | Role別Write Authority、Read-only Boundary、Operations Ownership |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| implementation_reported_review_pending | [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md) | Default `高度推論`、4責務分離、22 Criteria |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| implementation_reported_review_pending | [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md) | Presentation Module、Parser Registry、Stateful Streaming、CLI |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719142558.md](../history/architecture/implementation_roadmap_20260719142558.md) | Phase 1-E Review待ち、Phase 0～10、Phase Completion／Backup Gate |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current Operations

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_current | [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md) | Phase完了直後のArchive、Manifest、Receipt、SHA-512、復元確認 |

## 8. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |
| accepted | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md) | Default `高度推論`、Thinking 4責務分離、Parser Key、Raw保存OFF |

## 9. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260719142558.md](../history/handoffs/common_project_handoff_20260719142558.md) | 全担当Task、Role、Review、Phase完了／Backup Trigger |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告／Review済み |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| implementation_reported | [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md) | Phase 1-E正式実装Handoff |
| implementation_complete_review_requested | [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md) | Phase 1-E実装報告、22／22 Pass、独立Review待ち |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 10. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Mac上でのPhase 1操作、Test、Troubleshooting |

## 11. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Implementation Reported／Independent Review Pending
Phase 1 Overall                                    : Final Review Pending／Completion Not Declared
Phase 1 Backup                                     : Not Triggered
Phase 2+                                           : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                        : macOS／Apple Silicon arm64／Metal
Planned External Verification                      : Lightning AI Studio／Linux x86_64／CUDA
```

## 12. Phase Completion／Backup Decision

```text
Implementer Completion Report
       ↓
Designer Independent Review
       ↓
Follow-up／Re-review if needed
       ↓
Phase Final Acceptance／User Manual／Docs／Index
       ↓
Designer Explicit Completion Declaration
  "Phase Nは完了です。次はPhase N+1です。"
       ↓
Phase Backup and Restore Verification
       ↓
Next Phase Substantive Changes
```

この条件はすべてのTop-Level Phaseに共通である。

## 13. Role Operation Status

```text
Designer Role     : Operationally Validated in Phase 1
Implementer Role  : Operationally Validated in Phase 1
Designer／Implementer Separation : Functioning as intended
External Docs Role: Authority Defined／Operational Validation Pending
Operations Owner  : Designer Role
```

## 14. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md) | [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md) |
| historical | [common_project_handoff_20260718193435.md](../history/handoffs/common_project_handoff_20260718193435.md) | [common_project_handoff_20260719142558.md](../history/handoffs/common_project_handoff_20260719142558.md) |
| historical | [implementation_roadmap_20260719130303.md](../history/architecture/implementation_roadmap_20260719130303.md) | [implementation_roadmap_20260719142558.md](../history/architecture/implementation_roadmap_20260719142558.md) |
| historical | [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md) | [documentation_index_20260719142558.md](../history/documentation_index_20260719142558.md) |

`task_role_write_authority_policy_20260719142558.md`と`phase_completion_backup_policy_20260719142558.md`は新規系列である。

## 15. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719130303.md](../history/documentation_index_20260719130303.md)

## 16. Current Snapshot構成

```text
Requirements : 9
Architecture : 15
Governance   : 3
Operations   : 1
ADR          : 14
Handoffs     : 19
User Manual  : 1
Index        : 1
Current      : 63
Historical   : 60
Total        : 123
```

## 17. 前回Index以降に追加した文書

- [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)
- [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md)
- [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md)
- [common_project_handoff_20260719142558.md](../history/handoffs/common_project_handoff_20260719142558.md)
- [implementation_roadmap_20260719142558.md](../history/architecture/implementation_roadmap_20260719142558.md)
- [documentation_index_20260719142558.md](../history/documentation_index_20260719142558.md)

## 18. Next Gate

```text
Phase 1-E Implementation Report : Received
       ↓
Designer Independent Review     : Next
       ↓
Phase 1 Final Acceptance
       ↓
Designer Completion Declaration
       ↓
Phase 1 Backup
       ↓
Phase 2
```

## 19. Authorization Boundary

今回許可されたのは、Backup Policy、Role Authority Policy、共通規則、Common Handoff、Roadmap、Indexの文書化である。

今回実施していないもの：

- Phase 1-E Source／Config／Testの修正
- Phase 1-Eの独立レビューとAccepted判定
- Phase 1完了宣言
- Backup Archive／Manifest／Receiptの生成
- Phase 2以降の実装
- Dependency Install／Update
- Model Download
- Lightning AI Studio／ZeroGPU操作

## 20. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 24: docs/documentation_index_20260719142558.md -->

---

<!-- SOURCE_BEGIN 25: docs/documentation_index_20260719164641.md -->

### Source 25: `docs/documentation_index_20260719164641.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719164641.md`
- Source SHA-512: `73659f8c4ec848a5ddbd64ea576c251ad2c5240ba5b9e434953981f4bc41c44e8485e52ddd8b149400aaffc439fdb91945d0191f16e7d1194e31bcc66c381040`
- Source Size: `21600` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 16:46:41 JST`
- 更新日時: `2026-07-19 16:46:41 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719164641`
- supersedes: `documentation_index_20260719142558.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、Operations、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- Phase 1-EのSource、Config、Tests、Implementer Statusを設計者役が独立レビューした。
- Blocking／High／Medium Findingは0件であった。
- Low Diagnostic Observationを1件記録したが、Required Follow-upは0件とした。
- Acceptance Criteria `22／22`をPassと判定した。
- Ruff、Mypy、Compileall、Bash、Default Pytest、Environment、Lock／Offline、Native Metalを独立再実行した。
- Phase 1-Eを`Complete／Accepted`へ更新した。
- Phase 1-A～1-Eの全実装Subphaseが`Complete／Accepted`となった。
- 現在のUser ManualがPhase 1-A／1-Bのみを対象とするため、Top-Level Phase 1は`Documentation／Cross-phase Finalization Pending`とした。
- Phase 1完了宣言とBackup取得はまだ行っていない。
- RoadmapとCommon Handoffを後継化した。
- Source、Config、TestsはReviewで変更していない。

## 3. 最初に読む文書

1. [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md)
2. [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
3. [common_project_handoff_20260719164641.md](../history/handoffs/common_project_handoff_20260719164641.md)
4. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
5. [implementation_roadmap_20260719164641.md](../history/architecture/implementation_roadmap_20260719164641.md)
6. [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md)
7. [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md)
8. [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md)
9. [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
10. [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
11. [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md)
12. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
13. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
14. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
15. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
16. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
17. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
18. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
19. [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md) | Project Root、Append-Only、Timestamp、Index、Review、Role、Backup Trigger |
| accepted_current | [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md) | Role別Write Authority、Read-only Boundary、Operations Ownership |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| implemented_accepted | [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md) | Default `高度推論`、4責務分離、22／22 Accepted |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| implemented_accepted | [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md) | Presentation Module、Parser Registry、Stateful Streaming、CLI |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719164641.md](../history/architecture/implementation_roadmap_20260719164641.md) | Phase 1-E Accepted、Phase 1 Documentation／Finalization待ち |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current Operations

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_current | [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md) | Phase完了直後のArchive、Manifest、Receipt、SHA-512、復元確認 |

## 8. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |
| accepted_implemented | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md) | Default `高度推論`、Thinking 4責務分離、Parser Key、Raw保存OFF |

## 9. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260719164641.md](../history/handoffs/common_project_handoff_20260719164641.md) | 全担当Task、Phase 1-E Accepted、Phase 1 Finalization |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Config／Language実装Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告／Review済み |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| implemented_accepted | [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md) | Phase 1-E正式実装Handoff |
| reviewed_accepted | [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md) | Phase 1-E実装報告、22／22 Pass |
| accepted_phase_1e_complete | [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md) | Phase 1-E最終受入 |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 1-E後の全体実装計画／境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 10. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current_update_required | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | Phase 1-A／1-Bのみ。Phase 1-C／1-D／1-Eの後継反映が必要 |

## 11. Current Position

```text
Phase 0                                             : Complete
Phase 1-A Environment                              : Complete／Accepted
Phase 1-B Model Runtime                            : Complete／Accepted
Phase 1-C Deployment／Platform／Acceleration     : Complete／Accepted
Phase 1-D Configuration／Response Language        : Complete／Accepted
Phase 1-E Thinking Presentation                    : Complete／Accepted
Phase 1 Implementation Subphases                   : Complete
Top-Level Phase 1                                  : Documentation／Cross-phase Finalization Pending
Phase 1 Backup                                     : Not Triggered
Phase 2+                                           : Requirements／Architecture Accepted／Implementation Not Authorized
Current Native Verification                        : macOS／Apple Silicon arm64／Metal
Planned External Verification                      : Lightning AI Studio／Linux x86_64／CUDA
```

## 12. Phase 1-E Independent Gate Summary

```text
Ruff Format        : Pass／68 files
Ruff Check         : Pass
Mypy Strict        : Pass／68 source files
Compileall         : Pass
Default Pytest     : 161 passed, 2 deselected
Model Smoke        : 2 passed, 161 deselected
Environment        : Pass／Python 3.13.14／Metal
uv Lock            : Pass／117 packages
uv Offline Dry Run : Pass／115 packages／No changes
Acceptance         : 22／22 Pass
Final Decision     : Accepted
```

## 13. Phase Completion／Backup Decision

```text
All Implementation Subphases Accepted
       ↓
User Manual Update
       ↓
Cross-phase Final Review／Docs／Index
       ↓
Designer Explicit Completion Declaration
  "Phase 1は完了です。次はPhase 2です。"
       ↓
Phase 1 Backup and Restore Verification
       ↓
Phase 2 Substantive Changes
```

## 14. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [common_project_handoff_20260719142558.md](../history/handoffs/common_project_handoff_20260719142558.md) | [common_project_handoff_20260719164641.md](../history/handoffs/common_project_handoff_20260719164641.md) |
| historical | [implementation_roadmap_20260719142558.md](../history/architecture/implementation_roadmap_20260719142558.md) | [implementation_roadmap_20260719164641.md](../history/architecture/implementation_roadmap_20260719164641.md) |
| historical | [documentation_index_20260719142558.md](../history/documentation_index_20260719142558.md) | [documentation_index_20260719164641.md](../history/documentation_index_20260719164641.md) |

`designer_review_phase_1e_final_20260719164641.md`は新規系列である。

## 15. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719142558.md](../history/documentation_index_20260719142558.md)

## 16. Current Snapshot構成

```text
Requirements : 9
Architecture : 15
Governance   : 3
Operations   : 1
ADR          : 14
Handoffs     : 20
User Manual  : 1
Index        : 1
Current      : 64
Historical   : 63
Total        : 127
```

## 17. 今回作成したSnapshot文書

- [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md)
- [implementation_roadmap_20260719164641.md](../history/architecture/implementation_roadmap_20260719164641.md)
- [common_project_handoff_20260719164641.md](../history/handoffs/common_project_handoff_20260719164641.md)
- [documentation_index_20260719164641.md](../history/documentation_index_20260719164641.md)

## 18. Next Gate

```text
Phase 1-E Accepted
       ↓
Phase 1 User Manual Update
       ↓
Phase 1 Cross-phase Final Review
       ↓
Top-Level Phase 1 Completion Declaration
       ↓
Phase 1 Backup
       ↓
Phase 2
```

## 19. Authorization Boundary

今回許可されたのはPhase 1-Eの独立Reviewと、Review結果に伴うDocs更新である。

今回実施していないもの：

- Source／Config／Testsの修正
- User Manualの更新
- Top-Level Phase 1完了宣言
- Backup Archive／Manifest／Receiptの生成
- Phase 2以降の実装
- Dependency Install／Update
- Model Download
- Lightning AI Studio／ZeroGPU操作

## 20. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 25: docs/documentation_index_20260719164641.md -->

---

<!-- SOURCE_BEGIN 26: docs/documentation_index_20260719171836.md -->

### Source 26: `docs/documentation_index_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719171836.md`
- Source SHA-512: `df82a848f4e7ccd5bedf91107921639228b5b8f71aa6f96d6d8f6cb873a6bbf6ffd08562dcdd4454b11f5b87759be4aed6914316ea7ce238a603b9cb8e73a8a6`
- Source Size: `22667` bytes

# MARGPA Runtime LLM 文書索引

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- 対象: `docs/`全体
- 正本言語: 日本語
- Snapshot: `20260719171836`
- supersedes: `documentation_index_20260719164641.md`

## 1. この索引の役割

この文書は、現在有効なRequirements、Architecture、Governance、Operations、ADR、Handoff、Status、Review、User Manualと、過去文書の世代関係を示す最新Indexである。

同一系列ではFile名末尾のTimestampが最も新しいDocumentを最新とする。

## 2. 今回のSnapshot Update

- Phase 1-E ReviewのLow Diagnostic ObservationをKnown Issues／Observations Registerへ正式登録した。
- `MARGPA-OBS-0001`をLow／Accepted Deferred／Required Follow-upなしとした。
- Backup TriggerをDesigner Declaration単独からDual Approval Gateへ変更した。
- Gate Aを「設計者のPhase完了・次Phase移行可能宣言」とした。
- Gate Bを「ユーザーの対象Manual／Snapshot受入テスト全項目合格宣言」とした。
- 両Gateが同じProject状態について成立するまでBackupしないことを明文化した。
- Phase 1 macOS User ManualをPhase 1-A～1-E対応へ後継化した。
- User Acceptance Test 13項目と合格宣言形式を定義した。
- Phase 1 Cross-phase最終Readiness Reviewを実施した。
- Phase 1を`Ready for User Acceptance Test`と判定した。
- Top-Level Phase 1完了宣言、Phase 2移行可能宣言、Backupはまだ行っていない。
- Documentation Rules、Roadmap、Common Handoff、Indexを後継化した。
- Source、Config、Tests、Dependency、Modelは変更していない。

## 3. 最初に読む文書

1. [documentation_rules_20260719171836.md](../history/requirements/documentation_rules_20260719171836.md)
2. [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
3. [common_project_handoff_20260719171836.md](../history/handoffs/common_project_handoff_20260719171836.md)
4. [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
5. [implementation_roadmap_20260719171836.md](../history/architecture/implementation_roadmap_20260719171836.md)
6. [designer_review_phase_1_final_readiness_20260719171836.md](../history/handoffs/designer_review_phase_1_final_readiness_20260719171836.md)
7. [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)
8. [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)
9. [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)
10. [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md)
11. [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
12. [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
13. [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md)
14. [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md)
15. [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md)
16. [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md)
17. [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)

## 4. Current Requirements

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [documentation_rules_20260719171836.md](../history/requirements/documentation_rules_20260719171836.md) | Append-Only、Role、Observation、Dual Backup Gate、User Acceptance Record |
| accepted_current | [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md) | Role別Write Authority、Read-only Boundary、Operations Ownership |
| current | [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md) | Project目的、Scope、優先順位、Hardware、制約 |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_requirements_20260719013109.md](../history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md) | Phase 1-C Requirement、全Criteria Pass |
| implemented_accepted | [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md) | Application／Model／Deployment／Platform Registry責務分離 |
| implemented_accepted | [phase_1d_response_language_requirements_20260719041847.md](../history/requirements/phase_1d_response_language_requirements_20260719041847.md) | Config分離、`ja／en／auto`、Composition、Acceptance |
| implemented_accepted | [phase_1e_thinking_presentation_requirements_20260719130303.md](../history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md) | Default `高度推論`、4責務分離、22／22 Accepted |
| accepted_planning_only | [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md) | Phase 2以降の疎結合AI実験・統治Platform要件 |
| accepted_planning_only | [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md) | 全GD任意、0件Baseline、汎用Provider／Adapter／IR／Compiler要件 |

## 5. Current Architecture

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md) | Modular Monolith、Port／Adapter、Deployment、UI、Storage |
| current | [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md) | Module、Port／Adapter、依存方向 |
| current | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | Model選定、Quantization、Storage、Registry |
| current | [python_environment_and_dependency_strategy_20260718201744.md](../history/architecture/python_environment_and_dependency_strategy_20260718201744.md) | Python、Venv、uv、Dependency、Fallback |
| implemented | [phase_1b_model_runtime_contract_20260718223203.md](../history/architecture/phase_1b_model_runtime_contract_20260718223203.md) | Model Runtime Contract、Config、CLI、Test |
| implemented_accepted | [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md) | Deployment／Platform／Acceleration Hook |
| implemented_accepted | [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md) | Application Config、Deployment Profile、Typed Composer |
| implemented_accepted | [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md) | Configuration Composition、Response Resolver、Message Composer |
| implemented_accepted | [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md) | Presentation Module、Parser Registry、Stateful Streaming、CLI |
| current | [future_extensions_20260718174637.md](../history/architecture/future_extensions_20260718174637.md) | RAG、Agent、Image、Cloud、複数Model／GD |
| accepted_planning_only | [governance_control_plane_architecture_20260719112304.md](../history/architecture/governance_control_plane_architecture_20260719112304.md) | 共有Control Plane、分散Point、Binding、State、Action／Budget |
| accepted_planning_only | [governance_definition_platform_architecture_20260719112304.md](../history/architecture/governance_definition_platform_architecture_20260719112304.md) | Empty／Filesystem Provider、Manifest、Adapter、IR、Compiler／Security |
| accepted_planning_only | [experimental_runtime_ui_status_architecture_20260719112304.md](../history/architecture/experimental_runtime_ui_status_architecture_20260719112304.md) | Switchboard、Experiment、Event／Status、Typed Config、UI |
| accepted_planning_only | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | Mac Metal／Lightning Linux CUDAのCross-environment設計 |
| current | [implementation_roadmap_20260719171836.md](../history/architecture/implementation_roadmap_20260719171836.md) | Phase 1 User Acceptance待ち、Dual Backup Gate、Phase 0～10 |

## 6. Current Governance

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md) | ARGD、DAGD、Compiler、Profile、将来GD |
| current | [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md) | Audit、SHA-512、Evaluation、Guard、Judge、Permission |
| current_reference_catalog | [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md) | ARGD／DAGDと16 Optional Extensionの意味、制約、推奨Binding |

## 7. Current Operations

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_current | [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md) | Designer＋User Dual Approval、Archive、Manifest、Receipt、Restore |
| current | [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md) | Low Observation、Technical Debt、再評価条件 |

## 8. Current ADR

| 状態 | 文書 | Decision |
|---|---|---|
| accepted | [adr_0001_initial_model_selection_20260718174637.md](../history/adr/adr_0001_initial_model_selection_20260718174637.md) | Main、Guard、JudgeとQuantization |
| accepted | [adr_0002_external_model_storage_20260718174637.md](../history/adr/adr_0002_external_model_storage_20260718174637.md) | External Model RootとPOSIX Symbolic Link |
| accepted | [adr_0003_japanese_documentation_and_handoffs_20260718174637.md](../history/adr/adr_0003_japanese_documentation_and_handoffs_20260718174637.md) | 日本語Docs、Timestamp、担当別Handoff |
| accepted | [adr_0004_modular_monolith_20260718174637.md](../history/adr/adr_0004_modular_monolith_20260718174637.md) | Modular Monolith |
| accepted | [adr_0005_python_environment_and_dependency_management_20260718201744.md](../history/adr/adr_0005_python_environment_and_dependency_management_20260718201744.md) | Python 3.13.14、`.venv`、uv、Fallback |
| accepted | [adr_0006_model_runtime_port_and_configuration_20260718224308.md](../history/adr/adr_0006_model_runtime_port_and_configuration_20260718224308.md) | Model Port、Lifecycle、Capability、Config、CLI |
| accepted_implemented | [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md) | Platform Hook、Capability分離、Validation |
| accepted_implemented_amended_by_0009 | [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md) | `ja／en／auto`、Config配置はADR-0009で修正 |
| accepted_implemented | [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md) | `application.toml`、Deployment責務分離、Typed Composition |
| accepted | [adr_0010_research_runtime_phase_reorganization_20260719112304.md](../history/adr/adr_0010_research_runtime_phase_reorganization_20260719112304.md) | Phase 2へExperimental Control Planeを置きPhase 0～10へ再編 |
| accepted | [adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md](../history/adr/adr_0011_shared_governance_control_plane_and_distributed_points_20260719112304.md) | 共有Control Plane + 分散Point + Explicit Binding |
| accepted | [adr_0012_optional_generic_governance_definition_platform_20260719112304.md](../history/adr/adr_0012_optional_generic_governance_definition_platform_20260719112304.md) | 全GD任意、0件Baseline、非ハードコード |
| accepted | [adr_0013_lightning_ai_studio_external_development_20260719112304.md](../history/adr/adr_0013_lightning_ai_studio_external_development_20260719112304.md) | 第一外部開発／検証環境にLightning AI Studioを採用 |
| accepted_implemented | [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md) | Default `高度推論`、Thinking 4責務分離、Parser Key、Raw保存OFF |

## 9. Current Handoffs／Status／Review

| 状態 | 文書 | 対象 |
|---|---|---|
| current | [common_project_handoff_20260719171836.md](../history/handoffs/common_project_handoff_20260719171836.md) | 全担当Task、Phase 1 User Test待ち、Dual Backup Gate |
| current | [designer_handoff_20260718193435.md](../history/handoffs/designer_handoff_20260718193435.md) | 設計者役 |
| waiting | [implementer_handoff_20260718193435.md](../history/handoffs/implementer_handoff_20260718193435.md) | 実装者役・General |
| waiting | [designer_python_environment_handoff_20260718201744.md](../history/handoffs/designer_python_environment_handoff_20260718201744.md) | Python環境専用Handoff |
| reviewed | [implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md](../history/handoffs/implementer_status_phase_1_environment_reproducibility_follow_up_20260718214958.md) | Phase 1-A再現性Follow-up |
| accepted | [designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md](../history/handoffs/designer_review_phase_1_environment_reproducibility_follow_up_20260718221255.md) | Phase 1-A受入 |
| implemented | [designer_handoff_phase_1b_model_runtime_20260718224308.md](../history/handoffs/designer_handoff_phase_1b_model_runtime_20260718224308.md) | Phase 1-B Handoff |
| reviewed_accepted | [implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md](../history/handoffs/implementer_status_phase_1b_model_runtime_test_follow_up_20260719001341.md) | Phase 1-B最終Status |
| accepted_phase_1b_complete | [designer_review_phase_1b_model_runtime_final_20260719001604.md](../history/handoffs/designer_review_phase_1b_model_runtime_final_20260719001604.md) | Phase 1-B最終受入 |
| implemented | [designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md](../history/handoffs/designer_handoff_phase_1c_deployment_platform_acceleration_20260719013109.md) | Phase 1-C Handoff |
| reviewed_accepted | [implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md](../history/handoffs/implementer_status_phase_1c_platform_registry_reference_integrity_follow_up_20260719034523.md) | Phase 1-C最終Status |
| accepted_phase_1c_complete | [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md) | Phase 1-C最終受入 |
| implemented_accepted | [designer_handoff_phase_1d_response_language_20260719041847.md](../history/handoffs/designer_handoff_phase_1d_response_language_20260719041847.md) | Phase 1-D Handoff |
| reviewed_accepted | [implementer_status_phase_1d_configuration_and_response_language_20260719095111.md](../history/handoffs/implementer_status_phase_1d_configuration_and_response_language_20260719095111.md) | Phase 1-D実装報告 |
| accepted_phase_1d_complete | [designer_review_phase_1d_final_20260719122035.md](../history/handoffs/designer_review_phase_1d_final_20260719122035.md) | Phase 1-D最終受入 |
| implemented_accepted | [designer_handoff_phase_1e_thinking_presentation_20260719130303.md](../history/handoffs/designer_handoff_phase_1e_thinking_presentation_20260719130303.md) | Phase 1-E Handoff |
| reviewed_accepted | [implementer_status_phase_1e_thinking_presentation_20260719134914.md](../history/handoffs/implementer_status_phase_1e_thinking_presentation_20260719134914.md) | Phase 1-E実装報告 |
| accepted_phase_1e_complete | [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md) | Phase 1-E最終受入 |
| ready_for_user_acceptance_test | [designer_review_phase_1_final_readiness_20260719171836.md](../history/handoffs/designer_review_phase_1_final_readiness_20260719171836.md) | Phase 1 Cross-phase Readiness |
| planning_handoff_current_scope | [designer_handoff_post_phase_1e_research_platform_20260719112304.md](../history/handoffs/designer_handoff_post_phase_1e_research_platform_20260719112304.md) | Phase 2以降のPlanning境界 |
| waiting | [public_documentation_handoff_20260718174637.md](../history/handoffs/public_documentation_handoff_20260718174637.md) | 対外Docs作成者役 |

## 10. Current User Manual

| 状態 | 文書 | 対象 |
|---|---|---|
| current_user_acceptance_candidate | [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md) | Phase 1-A～1-E、13項目User Acceptance Test |

## 11. Current Position

```text
Phase 0                                             : Complete
Phase 1-A～1-E                                      : Complete／Accepted
Phase 1 Cross-phase Readiness                       : Pass
Phase 1 User Manual                                 : Ready
Phase 1 User Acceptance Test                        : Waiting
Designer Completion／Phase 2 Eligible Declaration  : Waiting
Phase 1 Backup                                      : Not Triggered
Top-Level Phase 1                                   : Ready for User Acceptance Test
Phase 2+                                            : Planning Accepted／Implementation Not Authorized
Current Native Verification                        : macOS／Apple Silicon arm64／Metal
Planned External Verification                      : Lightning AI Studio／Linux x86_64／CUDA
```

## 12. Phase 1 Evidence Summary

```text
Individual Review  : Phase 1-A～1-E Accepted
Cross-phase Review : Pass
Ruff／Mypy         : Pass
Compileall／Bash   : Pass
Default Pytest     : 161 passed, 2 deselected
Native Metal Test  : 2 passed, 161 deselected
Environment        : Python 3.13.14／arm64／Metal／Pass
uv Lock            : 117 packages
uv Offline         : 115 packages／No changes
Known Blocker      : 0
```

## 13. Dual Approval Gate

```text
Gate A: Designer Phase Completion + Phase 2 Eligible Declaration
Gate B: User Acceptance Test Pass Declaration

Current Gate A : Waiting
Current Gate B : Waiting
Backup         : Not Triggered
```

## 14. Supersession Update

| 状態 | 旧文書 | 最新文書 |
|---|---|---|
| historical | [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md) | [documentation_rules_20260719171836.md](../history/requirements/documentation_rules_20260719171836.md) |
| historical | [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md) | [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md) |
| historical | [phase_1_macos_user_manual_20260719004209.md](../history/user_manual/phase_1_macos_user_manual_20260719004209.md) | [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md) |
| historical | [implementation_roadmap_20260719164641.md](../history/architecture/implementation_roadmap_20260719164641.md) | [implementation_roadmap_20260719171836.md](../history/architecture/implementation_roadmap_20260719171836.md) |
| historical | [common_project_handoff_20260719164641.md](../history/handoffs/common_project_handoff_20260719164641.md) | [common_project_handoff_20260719171836.md](../history/handoffs/common_project_handoff_20260719171836.md) |
| historical | [documentation_index_20260719164641.md](../history/documentation_index_20260719164641.md) | [documentation_index_20260719171836.md](../history/documentation_index_20260719171836.md) |

次は新規系列である。

- `known_issues_and_observations_20260719171836.md`
- `designer_review_phase_1_final_readiness_20260719171836.md`

## 15. Historical Chain

直前までの完全なHistorical Chain：

- [documentation_index_20260719164641.md](../history/documentation_index_20260719164641.md)

## 16. Current Snapshot構成

```text
Requirements : 9
Architecture : 15
Governance   : 3
Operations   : 2
ADR          : 14
Handoffs     : 21
User Manual  : 1
Index        : 1
Current      : 66
Historical   : 69
Total        : 135
```

## 17. 今回作成したSnapshot文書

- [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)
- [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)
- [documentation_rules_20260719171836.md](../history/requirements/documentation_rules_20260719171836.md)
- [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)
- [designer_review_phase_1_final_readiness_20260719171836.md](../history/handoffs/designer_review_phase_1_final_readiness_20260719171836.md)
- [implementation_roadmap_20260719171836.md](../history/architecture/implementation_roadmap_20260719171836.md)
- [common_project_handoff_20260719171836.md](../history/handoffs/common_project_handoff_20260719171836.md)
- [documentation_index_20260719171836.md](../history/documentation_index_20260719171836.md)

## 18. Next Gate

```text
Current User Manual
       ↓
User Acceptance Test 13項目
       ↓
User Test Pass Declaration
       ↓
Designer State Freeze Confirmation
       ↓
Phase 1 Completion／Phase 2 Eligible Declaration
       ↓
Phase 1 Backup
       ↓
Phase 2
```

## 19. Authorization Boundary

今回実施したもの：

- Low Observationの正本登録
- Backup Dual Approval GateのPolicy化
- Phase 1-A～1-E User Manual
- Phase 1 Cross-phase Readiness Review
- Common Rules／Roadmap／Handoff／Index更新

今回実施していないもの：

- Source／Config／Tests／Dependency変更
- User Acceptance Testの代行宣言
- Top-Level Phase 1完了宣言
- Phase 2移行可能宣言
- Backup Archive／Manifest／Receipt生成
- Phase 2実装

## 20. Append-Only判定規則

- 新しいTimestampのDocumentを最新とする
- 新しいTimestampのIndexを最新Indexとする
- 旧文書を上書きしない
- 旧文書を削除・改名・移動しない
- 後継文書の`supersedes`で旧文書を示す
- 旧文書の状態は最新Index側で示す


<!-- SOURCE_END 26: docs/documentation_index_20260719171836.md -->

---

<!-- SOURCE_BEGIN 27: docs/documentation_index_20260719195134.md -->

### Source 27: `docs/documentation_index_20260719195134.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719195134.md`
- Source SHA-512: `db5d9e0215b79c0c4194104aff809a31e77374f62ecee89a86ce81f4e8ec8ee2147700689d5630fdb206ad282e32e9f26d8d575ded3475bc808414ca198c738c`
- Source Size: `3675` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719171836.md`

## 1. Current Position

```text
Phase 1 User Acceptance Test  : In Progress
Acceptance Follow-up          : Proposed／Implementation authorization waiting
Phase 1 Completion            : Not declared
Phase 1 Backup                : Not triggered
Phase 2 Implementation        : Not authorized
```

## 2. Current Snapshot Resolution

本Indexは、変更のないCurrent Setを次の完全Indexから継承する。

- [documentation_index_20260719171836.md](../history/documentation_index_20260719171836.md)

次の系列だけを本Snapshotで置換または追加する。この継承元と下表を組み合わせることでCurrent Setを再現できる。

## 3. Replaced Current Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md) | [known_issues_and_observations_20260719195134.md](../history/operations/known_issues_and_observations_20260719195134.md) |
| historical | [common_project_handoff_20260719171836.md](../history/handoffs/common_project_handoff_20260719171836.md) | [common_project_handoff_20260719195134.md](../history/handoffs/common_project_handoff_20260719195134.md) |
| historical | [documentation_index_20260719171836.md](../history/documentation_index_20260719171836.md) | [documentation_index_20260719195134.md](../history/documentation_index_20260719195134.md) |

## 4. Added Current Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_supplement | [phase_1_user_acceptance_findings_20260719195134.md](../history/user_manual/phase_1_user_acceptance_findings_20260719195134.md) | CLI仮引数、Thinking、Cross-platformのUser Test補足 |
| proposed_waiting_implementation_authorization | [phase_1_acceptance_follow_up_requirements_20260719195134.md](../history/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md) | Help／Token上限Warning要件 |
| waiting_user_implementation_authorization | [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md) | 実装担当向けFollow-up |

## 5. Current User Manual Set

- 基本Manual: [phase_1_macos_user_manual_20260719171836.md](../history/user_manual/phase_1_macos_user_manual_20260719171836.md)
- Current補足: [phase_1_user_acceptance_findings_20260719195134.md](../history/user_manual/phase_1_user_acceptance_findings_20260719195134.md)

Follow-up後の再受入時に、必要に応じて両文書を統合した新Timestampの後継Manualを作成する。既存Manualは変更しない。

## 6. Known Issues State

```text
MARGPA-OBS-0001 : accepted_deferred
MARGPA-OBS-0002 : open_required
MARGPA-OBS-0003 : accepted_deferred
MARGPA-OBS-0004 : accepted_deferred
MARGPA-OBS-0005 : accepted_deferred
```

## 7. Next Gate

```text
Follow-up Disposition
  → 必要なら実装／Test／Review
  → User Acceptance再確認
  → Designer Completion Declaration
  → Phase 1 Backup
```

## 8. Authorization Boundary

本Indexと関連Docsは、Source／Config／Tests変更、外部Service操作、Phase 1完了、Backup、Phase 2実装を許可しない。

## 9. Append-Only

- 本Snapshotで既存Docsを編集、削除、改名、移動していない。
- 新しいTimestampのIndexをCurrent Entry Pointとする。
- 前Snapshotの完全Indexと本Indexの明示差分でCurrent Setを再現する。

<!-- SOURCE_END 27: docs/documentation_index_20260719195134.md -->

---

<!-- SOURCE_BEGIN 28: docs/documentation_index_20260719200711.md -->

### Source 28: `docs/documentation_index_20260719200711.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719200711.md`
- Source SHA-512: `e239ac981e9b12e32f4eb8f9ab737ba20a2162c61d1beb888792591475b4dadf85edf697e79d6a689d73487aa0805cb298c5d063710e5de255df9894f7b6bad9`
- Source Size: `3435` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719195134.md`

## 1. Current Position

```text
Phase 1 User Acceptance              : In Progress
Phase 1 Follow-up                    : Waiting Implementation Authorization
Phase 1 Completion／Backup           : Not Triggered
Lightning Dual Profile Design        : Accepted Planning Only
Lightning Implementation／Validation : Waiting Future Phase Authorization
```

## 2. Snapshot Resolution

変更のないCurrent Setは次のIndexから継承する。

- [documentation_index_20260719195134.md](../history/documentation_index_20260719195134.md)

本Snapshotでは下表の系列を置換または追加する。継承元と本差分によりCurrent Setを再現する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [lightning_ai_studio_cross_environment_architecture_20260719112304.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719112304.md) | [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md) |
| historical | [common_project_handoff_20260719195134.md](../history/handoffs/common_project_handoff_20260719195134.md) | [common_project_handoff_20260719200711.md](../history/handoffs/common_project_handoff_20260719200711.md) |
| historical | [documentation_index_20260719195134.md](../history/documentation_index_20260719195134.md) | [documentation_index_20260719200711.md](../history/documentation_index_20260719200711.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_planning_only | [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../history/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md) | CUDA／CPU Profile、Container／Detection要件 |
| waiting_future_phase_authorization | [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](../history/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md) | 実装担当向け将来Handoff |

## 5. Current Profile Plan

```text
Mac Current : config/profiles/local_macos_arm64.toml
Lightning   : config/profiles/lightning_linux_x86_64_cuda.toml  # planned
Lightning   : config/profiles/lightning_linux_x86_64_cpu.toml   # planned
```

Lightning Profile Fileはまだ作成していない。Container／CUDA DetectionとNative Buildが同時に必要であり、未検証TOMLだけをPhase 1 Snapshotへ混入させない。

## 6. Next Gates

```text
Phase 1:
  Acceptance Follow-up Disposition
    → 必要なら実装／Review／再Test
    → User Acceptance
    → Completion／Backup

Lightning:
  Future Phase Authorization
    → Container／CUDA Detection
    → CUDA／CPU Profile + Setup
    → Native Verification
    → Review／Index
```

## 7. Authorization Boundary

本Indexと設計Docsは、Source／Config／Tests変更、Lightning外部操作、Package Install、Model Download／Upload、GPU利用を許可しない。

## 8. Append-Only

- 既存Docsを編集、削除、改名、移動していない。
- 新しいTimestampの本IndexをCurrent Entry Pointとする。

<!-- SOURCE_END 28: docs/documentation_index_20260719200711.md -->

---

<!-- SOURCE_BEGIN 29: docs/documentation_index_20260719202333.md -->

### Source 29: `docs/documentation_index_20260719202333.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260719202333.md`
- Source SHA-512: `4085eeeb990bea821ce06e3162f18601aa50dce4b94f58db00788b29e1e6437ecac3080f54acf1902fed241594706a7a00ac5ada5e344636dd1d33ff1a38332b`
- Source Size: `3986` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719200711.md`

## 1. Current Position

```text
Top-level Phase 1     : Reopened for Follow-up and Phase 1-F
Phase 1-F             : Accepted／Implementation Pending
User Acceptance       : Waiting
Backup                : Not Triggered
Publication           : Planned／Not Authorized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260719200711.md](../history/documentation_index_20260719200711.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md](../history/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md) | [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md) |
| historical | [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md) | [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md) |
| historical | [implementation_roadmap_20260719171836.md](../history/architecture/implementation_roadmap_20260719171836.md) | [implementation_roadmap_20260719202333.md](../history/architecture/implementation_roadmap_20260719202333.md) |
| historical | [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](../history/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md) | [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md) |
| historical | [common_project_handoff_20260719200711.md](../history/handoffs/common_project_handoff_20260719200711.md) | [common_project_handoff_20260719202333.md](../history/handoffs/common_project_handoff_20260719202333.md) |
| historical | [documentation_index_20260719200711.md](../history/documentation_index_20260719200711.md) | [documentation_index_20260719202333.md](../history/documentation_index_20260719202333.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md) | Lightning前倒し、Python 3.12／3.13 Support |

## 5. Current Phase 1 Work

- [Acceptance Follow-up Handoff](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- [Phase 1-F Handoff](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)

## 6. Current Python／Platform Matrix

```text
macOS arm64 Native／Metal       : Python 3.13.14／Native Verified before new changes
Linux x86_64 Container／CUDA    : Python 3.12.11／Implementation Pending
Linux x86_64 Container／CPU     : Python 3.12.11／Preferred／Conditional
```

## 7. Next Gate

```text
Implementer Start
  → Shared Compatibility Changes
  → Mac Regression
  → Lightning CUDA Native Verification
  → CPU Disposition
  → Review／Manual／User Acceptance
  → Phase 1 Completion／Backup
  → Publication Preparation
```

## 8. Authorization Boundary

本Indexと設計Docsは、Source／Config／Lock変更、Lightning操作、Backup、Git／GitHub公開を許可しない。実装担当へのUser Start Instructionを待つ。

## 9. Append-Only

- 既存Docsを編集、削除、改名、移動していない。
- 新しいTimestampの本IndexをCurrent Entry Pointとする。

<!-- SOURCE_END 29: docs/documentation_index_20260719202333.md -->

---

<!-- SOURCE_BEGIN 30: docs/documentation_index_20260720220216.md -->

### Source 30: `docs/documentation_index_20260720220216.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260720220216.md`
- Source SHA-512: `5c7c7ca493484c6ca8a1e11a3aedf93437321cfc13a70739161e9d8e46e9b869d97bba817d3d2e540360a2942f1dd9ea8acaf6ce2f8679964ab446f32e8dd2c8`
- Source Size: `3523` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260719202333.md`

## 1. Current Position

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
User Acceptance                : Waiting
Backup                         : Not Triggered
Publication                    : Planned／Not Authorized
Privacy Scrub                  : Complete for managed files
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260719202333.md](../history/documentation_index_20260719202333.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_rules_20260719171836.md](../history/requirements/documentation_rules_20260719171836.md) | [documentation_rules_20260720220216.md](../history/requirements/documentation_rules_20260720220216.md) |
| historical | [common_project_handoff_20260719202333.md](../history/handoffs/common_project_handoff_20260719202333.md) | [common_project_handoff_20260720220216.md](../history/handoffs/common_project_handoff_20260720220216.md) |
| historical | [documentation_index_20260719202333.md](../history/documentation_index_20260719202333.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md) | 第一者公開Identityと個人情報の正本方針 |
| complete | [publication_privacy_scrub_report_20260720220216.md](../history/operations/publication_privacy_scrub_report_20260720220216.md) | 管理対象FileのPrivacy Scrub記録 |
| reported | [implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md](../history/handoffs/implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md) | Phase 1-F Repository実装報告／未Review |

## 5. Privacy Exception Record

ユーザーの明示指示に基づき、Privacy／Securityを優先して既存管理対象Docs内の第一者旧Identityと個人固有Pathを匿名化した。

このため一部のHistorical Snapshotは作成時のBit列と一致しない。削除情報は復元せず、設計内容とDecision履歴を保持する。

## 6. Public Identity

```text
Nazuna Research
```

第一者の作者、設計者、開発者、Maintainer等の公開固有名は上記へ統一する。第三者のModel、Library、Repository、License等の正式名称は保持する。

## 7. Next Gate

```text
Phase 1-F Independent Review
  → Lightning Upload Scope確定
  → CUDA Native Verification
  → CPU Verification／Disposition
  → Current User Manual
  → User Acceptance + Designer Completion Declaration
  → Backup
  → Publication Preparation
```

## 8. Authorization Boundary

本IndexはSource／Config変更、Lightning操作、Git／GitHub操作、Backup、公開、Phase 1-F Acceptance、Phase 1-G実装を許可しない。

## 9. Append-Only

新規方針文書は新Timestampで作成した。既存Docsの匿名化だけはPrivacy／Security例外として直接適用した。

<!-- SOURCE_END 30: docs/documentation_index_20260720220216.md -->

---

<!-- SOURCE_BEGIN 31: docs/documentation_index_20260720222402.md -->

### Source 31: `docs/documentation_index_20260720222402.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260720222402.md`
- Source SHA-512: `029f10b8948d6a4f3e9d8db0e9282c2533875f35582b8a4dd28d6e32f467c3366dfe78a30cbe9bbe895a6b7957e4feed0df7f0ac3fc807c638c1736a9ca6f026`
- Source Size: `3855` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720220216.md`

## 1. Current Position

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1-ex                     : Added／Requirements Pending
Initial GitHub Publication     : Deferred until Phase 1-ex completion
Privacy Scrub                  : Complete for managed files
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720220216.md](../history/documentation_index_20260720220216.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md) | [phase_completion_backup_policy_20260720222402.md](../history/operations/phase_completion_backup_policy_20260720222402.md) |
| historical | [documentation_rules_20260720220216.md](../history/requirements/documentation_rules_20260720220216.md) | [documentation_rules_20260720222402.md](../history/requirements/documentation_rules_20260720222402.md) |
| historical | [common_project_handoff_20260720220216.md](../history/handoffs/common_project_handoff_20260720220216.md) | [common_project_handoff_20260720222402.md](../history/handoffs/common_project_handoff_20260720222402.md) |
| historical | [documentation_index_20260720220216.md](../history/documentation_index_20260720220216.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| pending_definition | [phase_1_ex_operations_reorganization_requirements_20260720222402.md](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md) | Phase 1-exの存在、目的、初回公開Gate |
| verified | [runtime_and_absolute_path_verification_20260720222402.md](../history/operations/runtime_and_absolute_path_verification_20260720222402.md) | Mac動作、Production Path、`.venv`／Model境界 |

## 5. Accepted Operational Changes

- 各PhaseのBackup確定後、同一Snapshotを原則GitHubへ反映する。
- 初回GitHub公開だけはPhase 1-ex完了後まで延期する。
- Phase 1-ex「運用再整備」をPhase 1と初回公開の間へ追加する。
- 毎回、Backup Candidate内のProject RootをSanitizeし、不要物を除去する。
- 第一者の公開Identityは`Nazuna Research`へ統一する。

## 6. Archive Exclusion Summary

`.DS_Store`、`.venv`、`models` Symlink、Model Binary、`.git`、Cache、Bytecode、Coverage、Notebook Checkpoint、Credential、Secret、Local Runtime Data、Temporary Fileを公開Archiveへ含めない。

## 7. Verification Summary

```text
Default Test                 : 181 passed
Ruff／Mypy                   : Pass
Mac Metal Model Smoke       : 2 passed／1 expected skip
Managed Production /Users   : 0
Lightning Native            : Pending
```

## 8. Next Gate

```text
Phase 1-F Review
  → Lightning Verification
  → Phase 1 User Acceptance／Completion／Backup
  → Phase 1-ex Requirements／Implementation／Acceptance
  → Publication Candidate Backup／Sanitation
  → Initial GitHub Publication
```

Phase 1-Gとの順序は未確定である。

## 9. Authorization Boundary

本IndexはBackup作成、Phase 1-ex／1-G実装、Git初期化、GitHub操作、Lightning操作、外部公開を許可しない。

## 10. Append-Only

既存Docsを変更せず、新Timestampの後継文書を作成した。

<!-- SOURCE_END 31: docs/documentation_index_20260720222402.md -->

---

<!-- SOURCE_BEGIN 32: docs/documentation_index_20260720231036.md -->

### Source 32: `docs/documentation_index_20260720231036.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260720231036.md`
- Source SHA-512: `0c67105a78c80d41a6a7993211e8323cb97d5be51b6ea038b9c37b58305fe8c4ee485ac58f556329bd15ac9dae07be7612f689a4528ce6b18c412e9e432cddca`
- Source Size: `4560` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720222402.md`

## 1. Current Position

```text
Current Design Role           : 設計者役／Unchanged
Phase 1-F                     : Review／Lightning Native Verification Pending
Phase 1 Completion／Backup    : Waiting
Phase 1-ex                    : Accepted Reservation／Not Started
Git                           : Not Initialized
Docs Directory               : Current Structure／Unchanged
Initial GitHub Publication    : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720222402.md](../history/documentation_index_20260720222402.md)から継承する。本Snapshotの置換／追加を下表に示す。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md) | [model_strategy_20260720231036.md](../history/architecture/model_strategy_20260720231036.md) |
| historical | [phase_1_ex_operations_reorganization_requirements_20260720222402.md](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md) | [phase_1_ex_operations_reorganization_requirements_20260720231036.md](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md) |
| historical | [common_project_handoff_20260720222402.md](../history/handoffs/common_project_handoff_20260720222402.md) | [common_project_handoff_20260720231036.md](../history/handoffs/common_project_handoff_20260720231036.md) |
| historical | [documentation_index_20260720222402.md](../history/documentation_index_20260720222402.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [ADR-0016](../history/adr/adr_0016_canonical_model_and_deployment_artifact_separation_20260720231036.md) | Canonical ModelとDeployment Artifact分離 |
| accepted_reservation | [ADR-0017](../history/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md) | Phase 1-ex Role／Git／Docs Transition |
| accepted_reservation | [Lossless Compilation Requirements](../history/requirements/lossless_phase_document_compilation_requirements_20260720231036.md) | Source本文を変更しないPhase統合 |
| accepted_reservation | [Public Docs Architecture](../history/architecture/public_documentation_and_phase_compilation_architecture_20260720231036.md) | README／LICENSE／日本語Public Docs／Phase文書 |

## 5. Model Current Decision

```text
Guard Local／Mac   : DevQuasar Q8_0を維持
Guard Canonical    : Qwen公式通常Model
Judge Local／Mac   : bartowski Q5_K_Mを維持
Judge Canonical    : AtlaAI公式通常Model
Official Download  : Deferred
Selene Japanese    : Unverified／Experimental
```

## 6. Phase 1-ex Accepted Reservations

- 現在は設計者役を維持し、Phase 1-exで設計統括者役へ変更
- Phase別設計者役と設計統括者役の分離
- 4役のDocs／Git／Review Authority再整理
- Git導入とDocs運用再定義
- Docs Directory Migrationと完了後通知
- Phase単位Lossless Compilation
- Phase完了時のPublic Docs作成・更新
- 初回GitHub公開はPhase 1-ex完了後

## 7. Public File Reservation

```text
README.md
LICENSE
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

全Docsは日本語を基本とし、README末尾だけEnglish Abstractを追加する。LICENSEは公式英語原文を許容する。

## 8. Lossless Integrity

運用、共通ルール、Handoff等をPhase単位で統合する際、要約、意訳、再解釈、重複削除、矛盾解消を禁止する。Sourceと再抽出PayloadのSHA-512／Byte Size一致を完了条件とする。

## 9. Immediate Next Gate

```text
Phase 1-F Independent Review
  → Lightning CUDA／CPU Native Verification
  → Current User Manual／User Acceptance
  → Phase 1 Completion／Backup
  → Phase 1-ex Detailed Definition／Execution
  → Initial GitHub Publication
```

## 10. Authorization Boundary

本IndexはModel Download、Role変更、Git操作、Directory変更、Docs統合、Public Docs生成、Task通知、Lightning操作、Backup、GitHub公開を許可しない。

## 11. Append-Only

既存Docsを編集せず、新Timestampの後継文書として追加した。

<!-- SOURCE_END 32: docs/documentation_index_20260720231036.md -->

---

<!-- SOURCE_BEGIN 33: docs/documentation_index_20260720235113.md -->

### Source 33: `docs/documentation_index_20260720235113.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260720235113.md`
- Source SHA-512: `4f6fe89178f7fff8bf4164d8a4fd67e275117298f44807949aede8aaa09aa7893c2a7df21d21cecada0edd3e37f53fd0a57e9288eb08a6f5b57c3277f7855bea`
- Source Size: `3382` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-20 23:51:13 JST`
- 更新日時: `2026-07-20 23:51:13 JST`
- Snapshot: `20260720235113`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720231036.md`

## 1. Current Position

```text
Current Design Role           : 設計者役／Unchanged
Phase 1-F Repository Review   : Changes Requested
Phase 1-F Lightning Gate      : Not Started
Phase 1-G Concept             : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup    : Waiting
Phase 1-ex                    : Accepted Reservation／Not Started
Git                           : Not Initialized
Initial GitHub Publication    : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720231036.md](../history/documentation_index_20260720231036.md)から継承する。本SnapshotではPhase 1-F ReviewとIndexだけを追加／置換する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260720231036.md](../history/documentation_index_20260720231036.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| changes_requested | [Phase 1-F Lightning Cross-environment Runtime設計Review](../history/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md) | Repository実装の独立ReviewとLightning搬入前Follow-up |

## 5. Phase 1-F Review Summary

```text
Static／Default Gate       : Pass
Mac 3.13／Metal Gate      : Pass
Python 3.12 Native Gate   : Not Run
Lightning CUDA Gate       : Not Run
Lightning CPU Gate        : Not Run
High Finding              : 2
Medium Finding            : 2
Low Observation           : 1
Decision                  : Changes Requested
```

主な必須Follow-up：

- CUDA Capability／RequestとActual GPU Offload Observationの分離
- Acceptance ProbeのFail Closed化
- Response Language／Thinking PresentationのNative Check強化
- Target Lightning StudioでのVenv利用可否確認

## 6. Phase 1-G Position

ユーザーとの要件定義会話において、Phase 1-GをLightning公開用の最小Web Surfaceとして追加する方向は合意済みである。

```text
Backend       : FastAPI
Current UI    : Minimal Vanilla HTML／CSS／JavaScript
Future UI     : React等へ交換可能
Chat          : Single Ephemeral Multi-turn
Settings      : Language／Max New Tokens／Thinking
Access        : Minimal Preview Access Control
```

ただし、Phase 1-GのRequirements、Architecture、ADR、Handoffは本Snapshotでは作成しておらず、実装も許可されていない。

## 7. Immediate Next Gate

```text
Phase 1-F Implementer Follow-up
  → Phase 1-F Follow-up Review
  → Lightning Preflight／Single Upload
  → Lightning CUDA／CPU Native Verification
  → Phase 1-F Final Review
  → Phase 1-G Canonical Design／Implementation
```

Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未許可／未着手である。

## 8. Authorization Boundary

本IndexはSource修正、Lightning操作、Model Download、Phase 1-G実装、Backup、Git、GitHub公開を許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。

<!-- SOURCE_END 33: docs/documentation_index_20260720235113.md -->

---

<!-- SOURCE_BEGIN 34: docs/documentation_index_20260721003201.md -->

### Source 34: `docs/documentation_index_20260721003201.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721003201.md`
- Source SHA-512: `006341f919af540d07dcff8dad4fa58640c36a0f776a617a6d1e8268f611cf7c7043098f799fe6d5d21d9950b7f7e61630ab3c3723c1c7dcbdf79702c4eac201`
- Source Size: `4138` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 00:32:01 JST`
- 更新日時: `2026-07-21 00:32:01 JST`
- Snapshot: `20260721003201`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260720235113.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Changes Requested／Minor Static Gate
Previous Phase 1-F Findings            : Resolved／5 of 5
Phase 1-F Lightning Preflight          : Not Run
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260720235113.md](../history/documentation_index_20260720235113.md)から継承する。本Snapshotでは、Phase 1-F Implementer Follow-up Statusと設計Reviewを追加し、前回Phase 1-F Reviewの状態を後継Reviewへ置き換える。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260720235113.md](../history/documentation_index_20260720235113.md) | 本文書 |
| superseded | [Phase 1-F Lightning Cross-environment Runtime設計Review](../history/handoffs/designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md) | [Phase 1-F Repository Follow-up設計Review](../history/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| implementer_complete_waiting_review | [Phase 1-F Repository Review Follow-up Status](../history/handoffs/implementer_status_phase_1f_repository_review_follow_up_20260721001705.md) | 前回Findingへの実装対応と検証結果 |
| changes_requested_minor | [Phase 1-F Repository Follow-up設計Review](../history/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md) | 独立検証、残存Static Gate、Lightning搬入判定 |

## 5. Phase 1-F Follow-up Summary

```text
Previous High Findings       : Resolved／2 of 2
Previous Medium Findings     : Resolved／2 of 2
Previous Low Observation     : Resolved／1 of 1
Default Test                 : Pass／183 passed、3 deselected
Mac Model Smoke              : Pass
Mac Strict Acceptance        : Pass／22 of 22 required checks
Full Project Mypy            : Fail／1 test error
Lightning Preflight          : Not Run
Lightning CUDA／CPU Gate     : Not Run
Decision                     : Changes Requested／Minor Follow-up
Phase 1-F Completion         : Not Accepted Yet
```

新規必須Follow-upは、Testコード1箇所のMypy Export境界修正と、Full Project Gateの再実行である。

## 6. Accepted Pending Setting Change

ユーザー決定により、次の小規模変更時にDefaultを変更する。

```toml
[generation]
max_new_tokens = 2048
```

Current Repositoryは`512`である。Config既定値と関連Testを同時に更新し、後続のGuardrail／Context／UI実装で再調整可能な設定として維持する。

Thinking表示Label変更はPhase 1-GのUI／注記設計へ残す。

## 7. Immediate Next Gate

```text
Minor Repository Follow-up
  → Short Designer Review
  → Lightning Read-only Preflight
  → Single Source／Model Upload
  → Lightning Python 3.12.11／CUDA／CPU Verification
  → Phase 1-F Final Review
  → Phase 1-G Canonical Design／Implementation
```

Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未許可／未着手である。

## 8. Authorization Boundary

本IndexはSource／Config／Tests／Scriptsの修正、Lightning操作、Upload、Model Download、Phase 1-G実装、Backup、Git、GitHub公開を許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。

<!-- SOURCE_END 34: docs/documentation_index_20260721003201.md -->

---

<!-- SOURCE_BEGIN 35: docs/documentation_index_20260721010200.md -->

### Source 35: `docs/documentation_index_20260721010200.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721010200.md`
- Source SHA-512: `f6f246908c0b57aa596fd458d7ddb52170a60e09f2a23808099e9be3cf73e2e5bad73bbca20b89f05d726c4a57c8294668b5f65c6cd727cfec6e37a39bd6351c`
- Source Size: `3760` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 01:02:00 JST`
- 更新日時: `2026-07-21 01:02:00 JST`
- Snapshot: `20260721010200`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721003201.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Authorized／Not Run
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721003201.md](../history/documentation_index_20260721003201.md)から継承する。本Snapshotでは、Phase 1-F Minor Static Gate Follow-up StatusとAccepted Reviewを追加し、前回ReviewのChanges Requested状態を解消する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721003201.md](../history/documentation_index_20260721003201.md) | 本文書 |
| superseded | [Phase 1-F Repository Follow-up設計Review](../history/handoffs/designer_review_phase_1f_repository_follow_up_20260721003201.md) | [Phase 1-F Minor Static Gate Follow-up設計Review](../history/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| implementer_complete_waiting_review | [Phase 1-F Minor Static Gate Follow-up Status](../history/handoffs/implementer_status_phase_1f_minor_static_gate_follow_up_20260721005412.md) | Full Mypy修正、2048既定値反映、再検証 |
| accepted | [Phase 1-F Minor Static Gate Follow-up設計Review](../history/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md) | Repository受入とLightning Preflight進行判定 |

## 5. Phase 1-F Repository Summary

```text
Previous Static Finding     : Resolved
Full Project Mypy           : Pass／70 source files
Default Test                : Pass／183 passed、3 deselected
Ruff／Compile／Shell／Lock   : Pass
Mac Metal Model Smoke       : Pass
Application Default         : max_new_tokens = 2048
New Finding                 : 0
Repository Decision         : Accepted
Phase 1-F Completion        : Waiting Lightning Native Gate
```

## 6. Immediate Next Gate

```text
Lightning Read-only Preflight
  → Preflight Result Review
  → Single Source／Model Upload
  → Lightning Python 3.12.11／CUDA／CPU Verification
  → Phase 1-F Final Review
  → Phase 1-G Canonical Design／Implementation
```

最初はPreflight ScriptだけをTargetへ配置し、Environment Mode、Python、uv、Container、GPU Allocationを確認する。Full Upload、Dependency Sync、Native BuildはPreflight確認後に進める。

## 7. Deferred Items

- Thinking表示Labelの`高度推論`から`推論過程`等への変更はPhase 1-Gで扱う。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 8. Authorization Boundary

本IndexとReviewはLightning Read-only Preflightを許可する。Source／Config変更、Full Upload、Dependency Install、Native Build、Model Download、Phase 1-G実装、Backup、Git、GitHub公開は許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。

<!-- SOURCE_END 35: docs/documentation_index_20260721010200.md -->

---

<!-- SOURCE_BEGIN 36: docs/documentation_index_20260721010621.md -->

### Source 36: `docs/documentation_index_20260721010621.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721010621.md`
- Source SHA-512: `04b4d10955d746854d869e4d3040a4885d518509f48196db08ce357b854299734b9146454fc4141b1011207fe92e725e3823c51100030d77719023329e8aed75`
- Source Size: `3359` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 01:06:21 JST`
- 更新日時: `2026-07-21 01:06:21 JST`
- Snapshot: `20260721010621`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721010200.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Authorized／Ready for Execution
Phase 1-F Full Upload                  : Not Authorized
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721010200.md](../history/documentation_index_20260721010200.md)から継承する。本Snapshotでは、Phase 1-F Lightning Read-only Preflight専用Handoffを追加する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721010200.md](../history/documentation_index_20260721010200.md) | 本文書 |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_ready_for_execution | [実装担当向けPhase 1-F Lightning Read-only Preflight Handoff](../history/handoffs/implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md) | 小型Preflightの外部実行Scope、合否、Evidence、禁止事項 |

## 5. Preflight Scope

Lightning Targetへ先に配置するのは次の1ファイルだけである。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

```text
Allowed
  ├─ Script 1ファイル配置
  ├─ Help確認
  ├─ GPU Read-only Preflight
  ├─ CPU Candidate Read-only Preflight
  └─ Implementer Status作成

Not Allowed Yet
  ├─ Project Full Upload
  ├─ Model Upload
  ├─ Dependency Install／Sync
  ├─ Native Build
  ├─ Environment変更
  └─ CUDA／CPU Native Acceptance
```

## 6. Immediate Next Gate

```text
Lightning Read-only Preflight実行
  → implementer_status_phase_1f_lightning_read_only_preflight_*
  → Designer Preflight Review
  → Full Upload可否判定
```

Preflightが失敗した場合、その場でEnvironment修復を行わず、Evidenceを記録してReviewへ戻す。

## 7. Deferred Items

- Full Upload、Python Dependency Sync、CUDA Build／Reuse、Model配置はPreflight Review後に判断する。
- Thinking表示Label変更はPhase 1-Gで扱う。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 8. Authorization Boundary

本IndexとHandoffは、Lightning Read-only Preflight Script 1ファイルの配置と実行だけを許可する。Full Upload、Model Transfer、Dependency Install、Native Build、Source変更、Phase 1-G実装、Backup、Git、GitHub公開は許可しない。

## 9. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。

<!-- SOURCE_END 36: docs/documentation_index_20260721010621.md -->

---

<!-- SOURCE_BEGIN 37: docs/documentation_index_20260721090725.md -->

### Source 37: `docs/documentation_index_20260721090725.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721090725.md`
- Source SHA-512: `c683323050b9061c465ac780f69ee2ce2ba4c5d3187326cf28bba3f32cdd84b17f8915bc7401dc721e0a2c9cf59d54391e2b3b0452db303815a8ed99856e026b`
- Source Size: `4707` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 09:07:25 JST`
- 更新日時: `2026-07-21 09:07:25 JST`
- Snapshot: `20260721090725`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721010621.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Read-only Execution          : Accepted
Phase 1-F Lightning Preflight          : Blocked／uv Version Gate
Lightning Existing uv                  : 0.11.18／Unchanged
Project Expected uv                    : 0.11.29／Retained
Phase 1-F Full Upload                  : Not Authorized
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Post-generation Summary Mode           : Accepted／Deferred Phase 1-G Follow-up
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721010621.md](../history/documentation_index_20260721010621.md)から継承する。本Snapshotでは、Lightning Read-only Preflight Status／ReviewとPost-generation Summary Mode要件予約を追加する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721010621.md](../history/documentation_index_20260721010621.md) | 本文書 |
| superseded | [Phase 1-F Minor Static Gate Follow-up設計Review](../history/handoffs/designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md) | [Phase 1-F Lightning Read-only Preflight設計Review](../history/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| blocked_waiting_designer_decision | [Phase 1-F Lightning Read-only Preflight Status](../history/handoffs/implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md) | Lightning実行Evidenceとuv Version不一致 |
| execution_accepted_follow_up_required | [Phase 1-F Lightning Read-only Preflight設計Review](../history/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md) | 実行受入、uv方針、Full Upload停止判断 |
| accepted_deferred | [Post-generation Summary Mode要件予約](../history/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md) | 要約モードOFF／ONと初期Runtime値 |

## 5. Preflight Review Summary

```text
Script Placement／Integrity   : Pass
Implementer Scope Compliance  : Pass
Host／Container／Python       : Pass
GPU Evidence                  : Tesla T4／15360 MiB
nvcc                          : Available
GPU Preflight                 : Fail／uv 0.11.18
CPU Candidate Preflight       : Fail／uv 0.11.18
Expected uv                   : 0.11.29／Retained
Environment Mutation          : None
Full Upload                   : Not Authorized
```

次はLightning既設uvを変更せず、公式uv 0.11.29をProject専用隔離Pathへ導入する限定Follow-upを設計する。

## 6. Summary Mode Accepted Values

```text
User Option                  : 要約モード OFF／ON
Default                      : OFF
Normal max_new_tokens        : 2048
Summary max_new_tokens       : 1024
Summary Thinking             : disabled
Initial Backend              : Main Model再利用
Original Final Answer        : Preserve
Implementation Timing        : Phase 1-G Accepted後の小規模Follow-up
```

要約モードはPhase 1-Fへ混在させない。

## 7. Immediate Next Gate

```text
Project-local uv 0.11.29 Bootstrap Handoff
  → Limited Environment Follow-up
  → Preflight Re-run
  → Designer Review
  → Full Upload可否判定
```

## 8. Deferred Items

- Full Upload、Model Transfer、Dependency Sync、Native Buildはuv Follow-up後に判断する。
- Phase 1-GとSummary Modeの実装はPhase 1-F完了後に扱う。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 9. Authorization Boundary

本IndexとReviewは、Studio-global uv変更、Project-local uv導入、Full Upload、Model Transfer、Dependency Install、Native Build、Phase 1-G実装、Summary Mode実装、Backup、Git、GitHub公開を許可しない。

## 10. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。

<!-- SOURCE_END 37: docs/documentation_index_20260721090725.md -->

---

<!-- SOURCE_BEGIN 38: docs/documentation_index_20260721092818.md -->

### Source 38: `docs/documentation_index_20260721092818.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721092818.md`
- Source SHA-512: `320d1eae3ddbd55a9d1087dd52cc9c9ec8341e14450686559564fce9db66425d9e5d7d154597000d1e54d5bbea561c1efbf00bc48c3fc3646e325cb8ce24583b`
- Source Size: `4075` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 09:28:18 JST`
- 更新日時: `2026-07-21 09:28:18 JST`
- Snapshot: `20260721092818`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721090725.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Accepted
Lightning Project／Studio-local uv     : 0.11.29／Pass
Lightning Existing uv                  : 0.11.18／Unchanged
Lightning Python                       : 3.12.11／Retained
Phase 1-F Full Upload Handoff          : Ready to Create
Phase 1-F Full Upload                  : Not Run／Not Yet Authorized
Phase 1-F Lightning CUDA／CPU Gate     : Not Run
generation.max_new_tokens              : 2048／Applied
Post-generation Summary Mode           : Accepted／Deferred Phase 1-G Follow-up
Phase 1-G Concept                      : User Accepted／Canonical Docs Not Created
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721090725.md](../history/documentation_index_20260721090725.md)から継承する。本Snapshotでは、ユーザー実行によるProject／Studio-local uv導入とPreflight再実行のAccepted Reviewを追加し、前回のuv Version Blockを解消する。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721090725.md](../history/documentation_index_20260721090725.md) | 本文書 |
| superseded | [Phase 1-F Lightning Read-only Preflight設計Review](../history/handoffs/designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md) | [Phase 1-F Lightning Project-local uv Preflight設計Review](../history/handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [Phase 1-F Lightning Project-local uv Preflight設計Review](../history/handoffs/designer_review_phase_1f_lightning_project_local_uv_preflight_20260721092818.md) | uv隔離、Preflight再合格、Python維持、次Gate判定 |

## 5. Preflight Final Summary

```text
Project／Studio-local uv      : 0.11.29／Pass
Binary SHA-512                : Recorded
Lightning Existing uv         : 0.11.18／Unchanged
Permanent PATH Mutation       : None
Python                        : 3.12.11／Retained
GPU Preflight                 : Pass／Exit 0
CPU Candidate Preflight       : Pass／Exit 0
nvcc                          : Available
Preflight Decision            : Accepted
Full Upload                   : Waiting Dedicated Handoff
```

## 6. Python Decision

Lightning Pythonは3.12.11のまま維持する。Mac 3.13.14とLightning 3.12.11を正式Support Pairとして検証し、Cross-version交換性を示す。

Python 3.13をLightningへ追加する場合は、3.12.11を置換せず、将来の別Environment／Profileとして扱う。

## 7. Immediate Next Gate

```text
Full Upload／Native Verification Handoff作成
  → Single Upload
  → Dependency／CUDA／CPU Native Gate
  → Designer Final Review
```

## 8. Deferred Items

- Summary ModeはPhase 1-G Accepted後の小規模Follow-upで実装する。
- Phase 1 Completion、Backup、Phase 1-ex、Git、GitHub公開は未着手である。

## 9. Authorization Boundary

本IndexとReviewはFull Upload／Native Verification Handoffの作成を許可する。Full Upload、Model Transfer、Dependency Install、Native Build、Python Upgrade、Source変更、Phase 1-G実装、Backup、Git、GitHub公開は専用Handoff前には実行しない。

## 10. Append-Only

既存Docsを編集せず、新TimestampのIndexとして追加した。

<!-- SOURCE_END 38: docs/documentation_index_20260721092818.md -->

---

<!-- SOURCE_BEGIN 39: docs/documentation_index_20260721093952.md -->

### Source 39: `docs/documentation_index_20260721093952.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721093952.md`
- Source SHA-512: `d90461aab8aafde963dca3e875d4ae2ad75152f54d38976cd0a35d84f72b17137971d2b20b3687de724e5a68d1d09108fc50b22d014cbe24c35c552b7780dbbc`
- Source Size: `8203` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721092818.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Phase 1-A～1-E                         : Accepted
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Accepted
Lightning Project／Studio-local uv     : 0.11.29／Pass
Lightning Existing uv                  : 0.11.18／Unchanged
Lightning Python                       : 3.12.11／Retained
Lightning Full Upload                  : Deferred until Phase 1-H Mac Acceptance
Phase 1-F Lightning Native Gate        : Not Run／Not Complete
Phase 1-G Minimal Web Surface Design   : Accepted
Phase 1-G Implementation               : Authorized／Not Yet Reviewed
Phase 1-H Summary Mode                 : Accepted Reservation／Waiting Phase 1-G
generation.max_new_tokens              : 2048／Current Default
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721092818.md](../history/documentation_index_20260721092818.md)から継承する。

本Snapshotでは、ユーザー判断により次の実施順を正式化した。

```text
Phase 1-F Lightning Read-only Preflight Accepted
  ↓
Phase 1-G Minimal Web SurfaceをMacで実装／検証
  ↓
Phase 1-H Post-generation Summary ModeをMacで実装／検証
  ↓
Project／ModelをLightningへ一括Upload
  ↓
Lightning GPU／CPU Native Verification
```

大量Uploadの重複を避けるための順序変更であり、Phase 1-F Lightning Native Gateの省略または合格扱いではない。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721092818.md](../history/documentation_index_20260721092818.md) | 本文書 |
| superseded | [implementation_roadmap_20260719202333.md](../history/architecture/implementation_roadmap_20260719202333.md) | [implementation_roadmap_20260721093952.md](../history/architecture/implementation_roadmap_20260721093952.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [ADR-0016 Lightning一括Upload順序](../history/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md) | Phase 1-G／1-H先行とLightning搬入順序の決定 |
| current | [Implementation Roadmap](../history/architecture/implementation_roadmap_20260721093952.md) | Phase全体の現行実施順とGate |
| accepted | [Phase 1-G Requirements](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md) | Minimal Web Surfaceの正本要件 |
| accepted | [Phase 1-G Architecture](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md) | UI／API／Auth／Concurrencyの設計正本 |
| accepted_ready_for_implementation | [Phase 1-G Implementer Handoff](../history/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md) | 実装担当への正式指示 |

## 5. Phase 1-G Fixed Scope

```text
Web Framework             : FastAPI 0.139.2
ASGI Server               : Uvicorn 0.51.0
ASGI Test Client          : HTTPX 0.28.1
UI                        : Local Vanilla HTML／CSS／JavaScript
Future UI                 : React等へ交換可能なAPI Boundary
Conversation              : Browser-owned Ephemeral Multi-turn
Persistence               : None
Streaming                 : Required
Cancellation              : Required
Model Load                : One Process／One Instance
Concurrent Generation     : One／Second Request is 409
Public Bind               : Server-side Preview Auth Required
Health Check              : Minimal Unauthenticated `/healthz`
Static Asset              : Local only／No CDN
Model Output Rendering    : Plain Text／No direct HTML injection
```

## 6. Phase 1-G UI Setting Boundary

一般利用者がPhase 1-G UIで変更できる設定は次の3項目だけである。

```text
response.language
  ja／en／auto

generation.max_new_tokens
  integer
  default: 2048

presentation.thinking.visibility
  OFF／ON
  default: OFF／hidden
```

`generation.thinking_mode`はUIのVisibility Switchとは別である。Visibility変更だけでThinking Executionを変更しない。

Thinking表示Labelの初期値は`高度推論`から`推論過程`へ変更する。UIでは`推論過程（モデル生成）`等、モデルが生成した区間であることを明示する。

## 7. Phase 1-H Reservation

Phase 1-Hは[post_generation_summary_mode_requirements_reservation_20260721090725.md](../history/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)をCurrent Reservationとする。

```text
Summary Mode UI       : OFF／ON
Default               : OFF
Normal Generation Max : 2048
Summary Generation Max: 1024
Summary Thinking      : Disabled
Execution             : Same Model／Sequential Second Pass
Original Answer       : Preserved internally for Audit／Future Comparison
```

Phase 1-GのAccepted Review前にPhase 1-Hへ着手しない。Phase 1-G UIへ未実装Summary Switchを先行表示しない。

## 8. Lightning Decision

```text
Python                         : 3.12.11を維持
Project／Studio-local uv        : 0.11.29を維持
Studio既存uv                   : 0.11.18を変更しない
Full Project Upload            : Phase 1-G／1-H Mac受入後
Model Upload                   : 同一Batch候補
GPU Native Verification        : Full Upload後
CPU Native Verification        : Full Upload後
```

MacはPython 3.13.14、LightningはPython 3.12.11をSupport Pairとして扱う。

## 9. Immediate Next Gate

実装担当は次の文書を読み、Phase 1-Gだけを実装する。

1. [Phase 1-G Requirements](../history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md)
2. [Phase 1-G Architecture](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
3. [ADR-0016](../history/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
4. [Phase 1-G Implementer Handoff](../history/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md)

実装後は次を作成し、設計者Reviewへ戻す。

```text
docs/handoffs/implementer_status_phase_1g_minimal_web_surface_YYYYMMDDHHMMSS.md
```

Review時はRepository、Test、Manual Smoke、Statusを確認し、新TimestampのDesigner ReviewとDocumentation Indexを一緒に作成する。

## 10. Authorization Boundary

本IndexとPhase 1-G Handoffは、Phase 1-GのRepository実装とMac検証を許可する。

次はまだ許可しない。

- Phase 1-H実装
- Lightning Full Upload
- Lightning Dependency Install／Native Build／Model Transfer
- Phase 1完了宣言
- Backup
- Phase 1-ex開始
- Git初期化
- GitHub公開
- 本格UI／React化
- Chat永続化

## 11. Deferred Observations

過去Snapshotから次を継承する。

- Linux／Windowsの完全自動Profile Routingは後続の局所修正候補。
- Hidden Thinking時に最終回答前Token上限へ到達した場合の空表示は、Phase 1-Gで明示状態へ改善する。
- Thinking表示前後の余分な空行はPresentation正規化候補。
- Response LanguageがFinal Answerへ適用されても、Model生成Thinking区間の言語は一致しない場合がある。
- 不正Environment設定と別Field CLI Overrideが同時にある場合、Error原因分類が少し不正確になる低優先度観察事項がある。
- Setup Recipeの通常実行が`llama-cpp-python` Native Rebuildを毎回行う点は将来分離候補。

## 12. Append-Only

既存Docsを編集せず、新TimestampのRequirements、Architecture、ADR、Roadmap、Handoff、Indexとして追加した。新しいTimestampの文書を最新として扱い、旧Indexから変更のない正本文書は継承する。

<!-- SOURCE_END 39: docs/documentation_index_20260721093952.md -->

---

<!-- SOURCE_BEGIN 40: docs/documentation_index_20260721111659.md -->

### Source 40: `docs/documentation_index_20260721111659.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721111659.md`
- Source SHA-512: `2ff4756ca03f6548b57e0d4bd2c6f363a71453392aab5a0194e22e8b5c13fb88664ae0c0442bee2e19acfdb2c8782afef0f277589d6cb005752979047b757f2a`
- Source Size: `6447` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 11:16:59 JST`
- 更新日時: `2026-07-21 11:16:59 JST`
- Snapshot: `20260721111659`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721093952.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Public Author／Research Name           : Nazuna Research
Public Repository Owner               : margpa-labs
Public Repository                     : margpa-labs/margpa-runtime-llm
Commit Link to Personal GitHub Account : Allowed
GitHub Initial License Stage           : Evaluation-only Source-available／Reserved
Lightning Public UI Access             : Exposed Functions Freely Usable／Reserved
Phase 1-A～1-E                         : Accepted
Phase 1-F Repository Follow-up         : Accepted
Phase 1-F Lightning Preflight          : Accepted
Phase 1-F Lightning Native Gate        : Not Run／Not Complete
Phase 1-G Minimal Web Surface          : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                 : Accepted Reservation／Waiting Phase 1-G Review
Lightning Full Upload                  : Deferred until Phase 1-H Mac Acceptance
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
Initial GitHub Publication             : Deferred until Phase 1-ex completion
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721093952.md](../history/documentation_index_20260721093952.md)から継承する。

本Snapshotでは、旧第一者名義規則を`Nazuna Research`中心の新規則へ置き換え、Phase 1-exのGitHub／Lightning Access境界、License Staging、CITATION／NOTICE、Commit帰属許容を追加した。

Phase 1-Gについては[実装担当Status](../history/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md)の存在を確認したが、本Snapshotでは内容Reviewを行っていない。したがってAcceptedではなく`Review Pending`である。

## 3. Replaced Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical | [documentation_index_20260721093952.md](../history/documentation_index_20260721093952.md) | 本文書 |
| superseded | [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md) | [public_identity_and_personal_information_policy_20260721111659.md](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md) |

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current | [公開識別子・個人情報取扱方針](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md) | `Nazuna Research`中心の公開名義正本 |
| accepted_reservation | [Phase 1-ex 公開名義・Access・License要件予約](../history/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md) | GitHub／Lightning境界、License、CITATION、NOTICE、公開移行 |
| current_common_rule | [共通公開名義・名称規則](../history/handoffs/common_public_identity_and_naming_rule_20260721111659.md) | 全担当Taskが使用する短い共通規則 |

## 5. Current Identity Rule

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Repository Owner             : margpa-labs
Repository URL               : https://github.com/margpa-labs/margpa-runtime-llm
```

第一者の公開名義は例外なく`Nazuna Research`とする。GitHub Account Handleやnoreply Commit Email等の技術識別子を文書化する必要性は、設計者役Taskだけが判断する。

Commitから個人GitHub Accountへ辿れることは許容する。個人情報をSource／Docsへ追加掲載する許可ではない。

## 6. Public Access Boundary

### GitHub

初期公開は閲覧・評価限定のSource-available公開とし、OSSとは表示しない。GitHub利用規約上の閲覧／Forkを妨げず、それ以外の権利を独自Evaluation-only Licenseで定義する。

### Lightning

Lightning公開UIは、画面へ公開した通常機能を利用者が自由に操作・評価できるDemoとする。これはGitHub Sourceの再利用権、Model Weight取得権、管理権限を付与するものではない。

## 7. Phase 1-ex Public File Reservation

```text
README.md
LICENSE
CITATION.cff                  # English
NOTICE.md                     # Japanese／English
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

`CITATION.cff`はAuthor Entityを`Nazuna Research`とし、Custom Licenseを架空SPDX IDとして記載しない。必要時は`license-url`で`LICENSE`を参照する。

## 8. Immediate Next Gate

Phase 1-G実装担当Statusと関連RepositoryをReviewする。

Review後は、既存運用規則どおり新Timestampで次を一緒に作成する。

```text
docs/handoffs/designer_review_phase_1g_minimal_web_surface_YYYYMMDDHHMMSS.md
docs/documentation_index_YYYYMMDDHHMMSS.md
```

Phase 1-G Accepted前にPhase 1-Hへ着手しない。

## 9. Phase 1-ex Deferred Work

- 公開対象のRead-only Inventory
- 識別情報分類Manifest
- 洗浄済みPublic Export設計
- Evaluation-only License具体文面
- `CITATION.cff`／`NOTICE.md`作成
- Commit Author／Email設定
- PII／Secret／Path／Symlink／Binary検証
- 実装担当向けRead-only Preflight Handoff
- Public Repositoryへの初回Commit／Push

## 10. Authorization Boundary

本Snapshotで即時適用するのは、今後新規作成する内容における`Nazuna Research`の名義規則だけである。

次はまだ許可しない。

- Phase 1-ex開始
- 既存Repository全体の識別情報走査
- 既存Fileの一括置換／削除／Rename
- README／LICENSE／NOTICE／CITATION生成
- Git設定変更／Git初期化／Commit／Tag
- Git History書換え
- GitHub Push
- Lightning設定変更
- Phase 1-H実装
- Backup

## 11. Append-Only

既存Docsを編集せず、新TimestampのPolicy、Phase 1-ex Reservation、Common Rule、Indexとして追加した。新しいPolicyが旧第一者名義Policyを明示的にSupersedeする。

<!-- SOURCE_END 40: docs/documentation_index_20260721111659.md -->

---

<!-- SOURCE_BEGIN 41: docs/documentation_index_20260721112925.md -->

### Source 41: `docs/documentation_index_20260721112925.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721112925.md`
- Source SHA-512: `9f74c45d119a5d288b5f4e7254377ae22bf62047063be57a4c5faf70513451737ab47ff73424ca78289e2673397e671788920c9fe6a8309f2bd90c6e2a4d27eb`
- Source Size: `4856` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 11:29:25 JST`
- 更新日時: `2026-07-21 11:29:25 JST`
- Snapshot: `20260721112925`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721111659.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Public Author／Research Name           : Nazuna Research／Mandatory
Project Internal Name                 : Nazuna Research Governance LLM
Machine-safe Slug                     : nazuna-research
Naming Exception Authority            : 設計者役Task Only
Approved Naming Exceptions            : None
Deprecated Name Match in docs/        : 0／Pass
Public Repository Owner               : margpa-labs
Public Repository                     : margpa-labs/margpa-runtime-llm
Commit Link to Personal Account       : Allowed
Phase 1-G Minimal Web Surface          : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                 : Waiting Phase 1-G Review
Lightning Full Upload                  : Deferred
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721111659.md](../history/documentation_index_20260721111659.md)から継承する。

本Snapshotでは、`docs/`内の廃止済み第一者名義をPrivacy Exceptionにより直接洗浄し、表示名を`Nazuna Research`へ統一した。

## 3. Replaced／Superseded Documents

| 状態 | 旧文書 | Current文書 |
|---|---|---|
| historical_scrubbed | [documentation_index_20260721111659.md](../history/documentation_index_20260721111659.md) | 本文書 |
| superseded | [common_public_identity_and_naming_rule_20260721111659.md](../history/handoffs/common_public_identity_and_naming_rule_20260721111659.md) | [common_public_identity_and_naming_rule_20260721112925.md](../history/handoffs/common_public_identity_and_naming_rule_20260721112925.md) |

既存の[公開識別子・個人情報取扱方針](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md)は、Privacy Exceptionにより実値を除去した状態で継続する。名義例外なしの最新Decisionは本Snapshotの追加正本を優先する。

## 4. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_mandatory | [公開名義・名称の統一決定](../history/requirements/public_identity_and_naming_decision_20260721112925.md) | `Nazuna Research`への例外なし統一 |
| current_common_rule | [共通公開名義・名称規則](../history/handoffs/common_public_identity_and_naming_rule_20260721112925.md) | 全担当Task向け必須規則 |
| completed | [Docs公開名義洗浄Report](../history/operations/public_identity_docs_scrub_report_20260721112925.md) | 直接洗浄範囲・変換・ゼロ件検証 |

## 5. Naming Rule

```text
Human-readable First-party Name : Nazuna Research
Project Internal Name           : Nazuna Research Governance LLM
Machine-safe Slug               : nazuna-research
```

別の第一者識別子をDocsへ記録する必要性は、設計者役Taskだけが判断できる。現時点の承認済み例外はない。

他の担当Taskは、実値を再挿入せず設計者役TaskへEscalateする。

## 6. Privacy Scrub Result

```text
Target Root        : docs/
Initial Occurrence : 67
Initial Files      : 32
Final Occurrence   : 0
Result             : PASS
```

Historical Docsを直接変更したため、対象Fileの過去Size／Digestは現在内容のEvidenceとして使用しない。Phase 1-exで公開候補ArtifactのManifestとDigestを再生成する。

## 7. Commit Attribution

Commit Author Nameは`Nazuna Research`とする。Commitから個人GitHub Accountへ辿れることは許容するが、Account Handleや個人EmailをDocsへ記録しない。

## 8. Immediate Next Gate

[Phase 1-G実装担当Status](../history/handoffs/implementer_status_phase_1g_minimal_web_surface_20260721105005.md)と関連RepositoryをReviewする。

Review後は新TimestampのDesigner ReviewとDocumentation Indexを一緒に作成する。

## 9. Authorization Boundary

今回許可された変更は`docs/`内の名義洗浄と正本更新までである。

次はまだ行わない。

- `src/`、`tests/`、`scripts/`、`config/`、Root Metadataの識別情報洗浄
- Git設定変更／Git初期化／Commit／Push
- README／LICENSE／NOTICE／CITATION生成
- Phase 1-ex開始
- Phase 1-H実装
- Lightning Full Upload
- Backup

## 10. Append-only／Privacy Exception

新しいDecision、Common Rule、Scrub Report、IndexはAppend-onlyで追加した。既存32文書の該当箇所は、公開識別情報洗浄を優先するPrivacy Exceptionとして直接変更した。

<!-- SOURCE_END 41: docs/documentation_index_20260721112925.md -->

---

<!-- SOURCE_BEGIN 42: docs/documentation_index_20260721115330.md -->

### Source 42: `docs/documentation_index_20260721115330.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721115330.md`
- Source SHA-512: `74c9f652d368165992e3f4a48dbbfe64bd8cbba27e2b0f9247b0fb28fef3dd53da3907bf9034abb74a1aa5c3475b9f5c0ec063e0407845d66ff883a174c7ff41`
- Source Size: `4034` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 11:53:30 JST`
- 更新日時: `2026-07-21 11:53:30 JST`
- Snapshot: `20260721115330`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721112925.md`

## 1. Current Position

```text
Current Design Role                    : 設計者役／Unchanged
Public Author／Research Name           : Nazuna Research／Mandatory
Project Internal Name                 : Nazuna Research Governance LLM
Public Repository Owner               : margpa-labs
Phase 1-G Repository Implementation    : Completed Candidate
Phase 1-G Designer Review              : Changes Requested
Phase 1-G Blocking Work                : 3系統／Follow-up Waiting User Authorization
Phase 1-H Summary Mode                 : Waiting Phase 1-G Acceptance
Lightning Full Upload                  : Deferred
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721112925.md](../history/documentation_index_20260721112925.md)から継承する。

本Snapshotは、Phase 1-Gの設計Review結果と、実装担当向け限定Follow-upを追加する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_review_changes_requested | [Phase 1-G Minimal Web Surface設計Review](../history/handoffs/designer_review_phase_1g_minimal_web_surface_20260721115330.md) | 実装、Security、Streaming、UI、検証Evidenceの合否 |
| waiting_user_authorization | [実装担当向けPhase 1-G Review Follow-up](../history/handoffs/implementer_handoff_phase_1g_review_follow_up_20260721115330.md) | Mandatory Finding 3系統の限定修正 |

## 4. Phase 1-G Review Result

```text
High Finding                 : 1
Medium Finding               : 2
Low Observation              : 2
Static／Default Gate          : Pass／209 passed、3 deselected
Web Targeted Test            : Pass／26 passed
Mac Native Model Smoke       : Pass／2 passed、1 skipped
Final Decision               : Changes Requested
```

Mandatory Follow-up：

1. Backpressure中のClient DisconnectでもProducerとGeneration Gateを確実に解放する。
2. Final Answer前Token Exhaustion WarningをBrowserの`completed`処理で上書きしない。
3. Source内の第一者表示名2箇所を`Nazuna Research`へ統一する。

## 5. Accepted Areas

- FastAPI／UvicornのDelivery Adapter局所化
- Browser-owned Ephemeral Multi-turn
- Request単位の3設定とTracked TOML非変更
- Model Load 1回／Unload 1回
- Basic AuthとNon-loopback Fail Closed
- `/healthz`以外の共通認証境界
- Plain Text Rendering、Local Asset、Security Header
- Hidden ThinkingとCanonical Historyの分離
- Normal Stop／Post-cancel Generation
- Existing CLI／Config／Model Runtime Regressionなし

## 6. Unaccepted Areas

- Queue満杯時のDisconnect Cleanup
- Token Exhaustionの最終User-visible表示
- Source／Web UIのCurrent Public Naming

Browser `auto`の明示Manual EvidenceはFollow-up時に補完する。

## 7. Immediate Next Gate

```text
UserがPhase 1-G Follow-up開始を許可
  → 実装担当が限定修正とRegression Test
  → 後継Implementer Status
  → 設計者役Follow-up Review＋新Index
  → Phase 1-G Accepted判定
  → Phase 1-H Summary Mode
```

## 8. Authorization Boundary

本Snapshotで許可された変更はReview、Follow-up Handoff、IndexのAppend-only追加までである。

まだ行わない。

- Source／Config／Tests／Scriptsの修正
- Phase 1-H実装
- Lightning Full Upload／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex開始
- Git初期化／Commit／Push／GitHub公開

Follow-up実装は、ユーザーが実装担当Taskへ明示的に開始指示した後に行う。

## 9. Append-Only

既存文書を変更せず、新TimestampのReview、Handoff、Indexを追加した。

<!-- SOURCE_END 42: docs/documentation_index_20260721115330.md -->

---

<!-- SOURCE_BEGIN 43: docs/documentation_index_20260721122621.md -->

### Source 43: `docs/documentation_index_20260721122621.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721122621.md`
- Source SHA-512: `247a18ad8d4251d66c6f8920cc6081930f1304b0f48591e77f77557b6c7de11bc8b7258683a1feb561f7fd920d84e0cc804a0fe0af0804d735e7b49b9f0e6b4d`
- Source Size: `3675` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 12:26:21 JST`
- 更新日時: `2026-07-21 12:26:21 JST`
- Snapshot: `20260721122621`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721115330.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research／Mandatory
Project Internal Name                 : Nazuna Research Governance LLM
Phase 1-G Previous Findings            : Resolved／3 of 3
Phase 1-G New High Finding             : Cross-thread Native Generator Cancel
Phase 1-G Designer Review              : Changes Requested／One Local Follow-up
Phase 1-H Summary Mode                 : Waiting Phase 1-G Acceptance
Lightning Full Upload                  : Deferred
Phase 1-ex                             : Accepted Reservation／Not Started
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721115330.md](../history/documentation_index_20260721115330.md)から継承する。

本Snapshotは、Phase 1-G Review Follow-upの設計Review結果とCross-thread Cancel限定Handoffを追加する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_review_changes_requested | [Phase 1-G Review Follow-up設計Review](../history/handoffs/designer_review_phase_1g_review_follow_up_20260721122621.md) | 前回Finding解消確認と新規Cross-thread競合 |
| waiting_user_authorization | [実装担当向けCross-thread Cancel Follow-up](../history/handoffs/implementer_handoff_phase_1g_cross_thread_cancel_follow_up_20260721122621.md) | Phase 1-G残件1件の限定修正 |

## 4. Resolved Findings

- Queue Capacity超過時のProducer投入待ち解除
- Final Answer前Token Exhaustion Warningの画面保持
- Warning TextのCanonical History非追加
- Public Namingの`Nazuna Research`統一
- Browser `response_language=auto` Manual Evidence

## 5. Current Finding

```text
Severity : High
Area     : Disconnect／Cancellation Thread Boundary
Cause    : Event Loop Threadから実行中Native Generatorへclose()
Observed : ValueError: generator already executing
Impact   : Producer Await前にCleanupが例外離脱し得る
```

Web CleanupはCooperative Cancelを第一段とし、Native IteratorのCancel／CloseをProducer Thread上で行う必要がある。

## 6. Verification Result

```text
Static／Default Test       : Pass／211 passed、3 deselected
Web Targeted Test         : Pass／28 passed
Mac Native Model Smoke    : Pass／2 passed、1 skipped
uv Lock                   : Pass／122 packages
Public Naming Search      : Pass／0 match
Cross-thread Diagnostic   : Fail／ValueError再現
Final Decision            : Changes Requested
```

## 7. Immediate Next Gate

```text
UserがCross-thread Cancel Follow-upを許可
  → 実装担当がThread-affine CancelとRegression Test
  → 後継Implementer Status
  → 設計者役Phase 1-G Final Review＋新Index
  → Phase 1-G Accepted判定
  → Phase 1-H Summary Mode
```

## 8. Authorization Boundary

本Snapshotで許可された変更はReview、限定Handoff、IndexのAppend-only追加までである。

まだ行わない。

- Source／TestsのFollow-up修正
- Phase 1-H実装
- Lightning Full Upload／Model Transfer
- Phase 1完了宣言／Backup
- Phase 1-ex開始
- Git初期化／Commit／Push／GitHub公開

Follow-up実装は、ユーザーが実装担当Taskへ明示的に開始指示した後に行う。

## 9. Append-Only

既存文書を変更せず、新TimestampのReview、Handoff、Indexを追加した。

<!-- SOURCE_END 43: docs/documentation_index_20260721122621.md -->

---

<!-- SOURCE_BEGIN 44: docs/documentation_index_20260721155020.md -->

### Source 44: `docs/documentation_index_20260721155020.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721155020.md`
- Source SHA-512: `ea762ec3f4f130acdd6c7a4c60d16316a8686c529595a74b0b7e0deecfeec2f37e617af88754d93abd5f7f15dd605eaddcab0cfdac6098e08ec7850f8b32cec1`
- Source Size: `5483` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721122621.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Project Internal Name                 : Nazuna Research Governance LLM
Phase 1-G Cross-thread Follow-up       : Implementer Report Received／Review Pending
Phase 1-H Summary Mode                 : Waiting Phase 1-G Acceptance
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Complete Reservation Updated／Not Started
Phase 10 Original R&D Hooks            : Accepted Future Reservation
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                    : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721122621.md](../history/documentation_index_20260721122621.md)から継承する。

本SnapshotはPhase 1-ex全内容、Stable Canonical Docs 5件、Project Continuity Master、Phase 10 Original R&D Hookを再統合する。

Phase 1-G Cross-thread Follow-upは[実装担当Status](../history/handoffs/implementer_status_phase_1g_cross_thread_cancel_follow_up_20260721150603.md)を受領済みだが、設計者Final Review前であるためAcceptedへ変更しない。

## 3. Added／Updated Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| current_parent_reservation | [Phase 1-ex総合要件](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md) | Role、Git、Docs、公開、Backup、Continuityの親正本 |
| current_reservation_architecture | [Phase 1-ex Documentation／Continuity／Publication Architecture](../history/architecture/phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md) | Target Tree、正本層、Migration、Port構造 |
| accepted_reservation | [ADR-0018](../history/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md) | Stable Docs、Continuity、R&D公開Hookの決定 |
| accepted_future_reservation | [Phase 10 Original R&D Hook](../history/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md) | 2つの独立R&Dと疎結合統合方針 |
| current | [Implementation Roadmap](../history/architecture/implementation_roadmap_20260721155020.md) | Current Phase状態とPhase 10予約 |
| current | [Common Project Handoff](../history/handoffs/common_project_handoff_20260721155020.md) | 全Task向けCurrent Entry Point |

## 4. Phase 1-ex Stable Canonical Docs

Phase 1-exで次を作成する。現在は未生成である。

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
```

File名は英語、本文は日本語とする。詳細設計書はPhase 1-ex必須対象外である。

## 5. Project Continuity Master

Phase 1-exで次を作成する。

```text
docs/project_continuity/project_continuity_master_ja.md
```

公開可能な継続正本としてGitHubへ含め、新TaskがProject全体を高精度に再開できる粒度を持たせる。

## 6. Public Derived Files

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

Stable Canonical Docs、Project Continuity Master、Lossless Compilation、Derived Public Docsを別Artifactとして扱う。

## 7. Phase 10 Original R&D

### 例外認識型安全統治機構

```text
Research Area : AI Safety Governance
```

### 分散証跡型例外認識エージェント統治安全機構

```text
Research Area : Multi-Agent Governance,
                Distributed Accountability,
                and Safety Assurance
```

後者は公開概要にも`改竄耐性付き証跡`を予定要素として明記する。

両機構は本体完成後のPhase 10で、別Project／別TaskからGeneric External Governance Provider Portを通じて任意統合する。

## 8. Public Disclosure Decision

```text
Roadmap             : 名称、研究領域、1から2行概要
System Architecture : 接続位置、Optional、Core非依存
Continuity Master   : 作業概念と統合Hookをやや詳しく記載
Algorithm／Core Idea: 現時点では非掲載
```

構想の存在と方向性を先に公開し、研究の核心はまだ開示しない。

## 9. Immediate Next Gate

```text
Phase 1-G Cross-thread Follow-up Status
  → Designer Final Review＋新Index
  → Phase 1-G Acceptance
  → Phase 1-H
```

Phase 1-exまたはPhase 10へまだ着手しない。

## 10. Authorization Boundary

今回許可された変更は、Phase 1-exおよびPhase 10予約をCurrent DocsへAppend-onlyで記録することまでである。

まだ行わない。

- Phase 1-ex開始
- Role変更
- Git初期化／Commit／Push
- Docs Move／Rename／Delete
- Stable Canonical Docs 5件の実生成
- Project Continuity Masterの実生成
- README／LICENSE／CITATION／NOTICE生成
- Backup／GitHub公開
- Phase 10 R&D実装／統合

## 11. Append-Only

既存文書を変更せず、新TimestampのRequirements、Architecture、ADR、Governance、Roadmap、Handoff、Indexを追加した。

<!-- SOURCE_END 44: docs/documentation_index_20260721155020.md -->

---

<!-- SOURCE_BEGIN 45: docs/documentation_index_20260721162242.md -->

### Source 45: `docs/documentation_index_20260721162242.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721162242.md`
- Source SHA-512: `25dccdce3eaf287a27713a4275395474d123e69c6d15d556898aaadd2f9249754a18259f8a361aa164ccbf30aef81df8b06f41f1f2607cdbc2cf1735a34f4433`
- Source Size: `4955` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721155020.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G Cross-thread Follow-up       : Implementer Report Received／Review Pending
Phase 1-H                             : Waiting Phase 1-G Acceptance
Phase 1-ex                            : Accepted Reservation／Not Started
Phase 10 Original R&D Systems         : EASA／DLAGSA／OCILNS
Original R&D Public Names             : Accepted
Original R&D Config ON／OFF            : Accepted Future Requirement
Initial GitHub Publication            : Deferred until Phase 1-ex completion
Git                                   : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721155020.md](../history/documentation_index_20260721155020.md)から継承する。

本SnapshotはEASA／DLAGSAの正式名称公開、OCILNS追加、3 System個別ON／OFF、Phase 10統合Architectureを追加する。

Phase 1-ex総合要件は継続し、本SnapshotのExternal R&D Requirementsを追加要件として適用する。

## 3. Added／Updated Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted_reservation | [External R&D公開・統合要件](../history/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md) | 3 System名称、記載先、ON／OFF、公開境界 |
| current_future_catalog | [Phase 10 Original R&D Catalog](../history/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md) | EASA／DLAGSA／OCILNSの公開正本 |
| accepted_future_architecture | [Phase 10 Integration Architecture](../history/architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md) | Governance／Ledger PortとConfig境界 |
| accepted_future_reservation | [ADR-0019](../history/adr/adr_0019_phase_10_original_r_and_d_public_names_and_switches_20260721162242.md) | 正式名称、公開範囲、SwitchのDecision |
| current | [Implementation Roadmap](../history/architecture/implementation_roadmap_20260721162242.md) | Phase 10の3 Systemを同粒度で掲載 |
| current | [Common Project Handoff](../history/handoffs/common_project_handoff_20260721162242.md) | 全Task向けCurrent名称／位置づけ |

## 4. Official Names

```text
EASA
Exception Aware Safety Architecture
例外認識型安全統治機構

DLAGSA
Distributed LEA Agentic Governance & Safety Architecture
分散証跡型例外認識エージェント統治安全機構

OCILNS
Open Cognitive Interaction Ledger Network System
認知対話証跡台帳網
```

## 5. Research Areas

```text
EASA
  AI Safety Governance

DLAGSA
  Multi-Agent Governance,
  Distributed Accountability,
  and Safety Assurance

OCILNS
  Cognitive Interaction Provenance,
  Verifiable AI Systems,
  and Distributed Auditability
```

## 6. Config Requirement

```text
EASA   : OFF／ON
DLAGSA : OFF／ON
OCILNS : OFF／ON
Default: All OFF
```

各Systemを独立して切替可能にし、OFF時はLoad、Call、Write、Side Effectを発生させない。

## 7. Integration Boundary

- EASA／DLAGSA：Generic External Governance Provider Port
- OCILNS：Generic Evidence Ledger Port
- Core非依存
- 別Project／別Task
- Phase 10／本体完成後
- Providerなしで本体完全動作

## 8. Public Disclosure

```text
Roadmap             : 名称、研究領域、1から2行概要
System Architecture : 接続位置、Optional、ON／OFF
Continuity Master   : 作業概念をやや詳しく記録
Core Algorithm      : 現在非掲載
```

OCILNSは改竄耐性付き証跡を扱う。単一SHA-512 Digestだけに依存しない予定であるが、具体方式は現在記載しない。

## 9. Phase 1-ex Output Mapping

Phase 1-exで作成する次の文書へ3 Systemを反映する。

- `requirements_specification_ja.md`
- `system_architecture_ja.md`
- `basic_design_ja.md`
- `runtime_governance_specification_ja.md`
- `project_continuity_master_ja.md`
- `roadmap_ja.md`

`technology_selection_ja.md`へ各R&D System内部の使用技術を記載しない。本体Adapter側の技術判断だけを扱う。

## 10. Immediate Next Gate

Phase 1-exとPhase 10へまだ着手しない。Phase 1-G Cross-thread Follow-upの設計者Final Reviewが次である。

## 11. Authorization Boundary

今回許可された変更は3 Systemの名称、概要、研究領域、将来Integration／ON／OFF要件をDocsへAppend-onlyで記録することまでである。

Config、Source、External System、Git、GitHub、Phase 10実装は変更しない。

## 12. Append-Only

既存文書を変更せず、新TimestampのRequirements、Catalog、Architecture、ADR、Roadmap、Handoff、Indexを追加した。

<!-- SOURCE_END 45: docs/documentation_index_20260721162242.md -->

---

<!-- SOURCE_BEGIN 46: docs/documentation_index_20260721164248.md -->

### Source 46: `docs/documentation_index_20260721164248.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721164248.md`
- Source SHA-512: `44998414c1da83781e53b770f8a6834957082463746a7f5c7206dd4d89b19612de9d57517c832ca53234b09ee1a08da174da10b01fe35bc93b5bb09ce0eeaa26`
- Source Size: `4078` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 16:42:48 JST`
- 更新日時: `2026-07-21 16:42:48 JST`
- Snapshot: `20260721164248`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721162242.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G SSE Cross-thread Follow-up    : Resolved
Phase 1-G Shutdown Cancel               : Changes Requested／One Mandatory Follow-up
Phase 1-G Final Acceptance              : Pending
Phase 1-H                               : Waiting Phase 1-G Acceptance
Phase 1-ex                              : Accepted Reservation／Not Started
Phase 10 Original R&D Systems           : EASA／DLAGSA／OCILNS
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721162242.md](../history/documentation_index_20260721162242.md)から継承する。

本SnapshotはPhase 1-G Cross-thread Cancel Follow-upの設計Review、Shutdown Cancel追加Finding、実装担当Handoffを追加する。

EASA／DLAGSA／OCILNSの正式名称、公開範囲、Phase 10統合予約、個別ON／OFF要件は直前Indexから継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| changes_requested | [Phase 1-G Cross-thread Cancel Follow-up Review](../history/handoffs/designer_review_phase_1g_cross_thread_cancel_follow_up_20260721164248.md) | SSE解消確認、Shutdown Finding、最終受入判定 |
| waiting_user_authorization | [Phase 1-G Shutdown Cancel Follow-up Handoff](../history/handoffs/implementer_handoff_phase_1g_shutdown_cancel_follow_up_20260721164248.md) | 実装担当の限定修正範囲と受入条件 |

## 4. Review Result

### Resolved

- SSE Consumer Close時のEvent Loop ThreadからNative Generatorへの`force_cancel()`を除去した。
- Producer Thread上のCancel／Closeへ統一した。
- Cleanup TimeoutはThread-unsafe Escalationを行わず明示Failureとする。
- Thread-affine／Backpressure／Timeout Regressionが合格した。

### Remaining Mandatory Finding

```text
Path   : ConversationGenerationService.shutdown()
Trigger: Active Generation + Shutdown Timeout
Result : Cross-thread session.force_cancel()
Error  : ValueError: generator already executing
Impact : Model Close Callback未到達／Shutdown Failure無記録抑制
```

## 5. Independent Verification

```text
Static Format／Lint／Type／Compile : Pass
Default Regression                    : 213 passed、3 deselected
Conversation／Web Targeted            : 30 passed
uv Lock                               : Pass／122 packages
Setup Shell Syntax                    : Pass
Implementer Native Model Smoke        : 2 passed、1 skipped
Reviewer Native Model Smoke           : 2 failed、1 skipped／2 runs
Reviewer Native Failure               : Failed to create llama_context
```

Native FailureはModel Context作成時であり、Phase 1-G Web差分が実行される前に発生した。原因は未確定であり、Shutdown Follow-up後Reviewで再実行する。

## 6. Next Gate

```text
ユーザーによる追加Follow-up開始許可
  ↓
実装担当 Phase 1-G Shutdown Cancel Follow-up
  ↓
設計者役 Phase 1-G Final Review
  ↓
Phase 1-G Accepted判定
  ↓
Phase 1-H Summary Mode
```

## 7. Deferred State

- Phase 1-Hは未着手。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。
- Phase 10 Original R&D統合は将来予約のまま。

## 8. Authorization Boundary

本IndexはReview結果と次Gateを記録する。Source／Tests修正、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を許可しない。

## 9. Append-Only

既存Review、Handoff、Indexを変更せず、新TimestampのReview、Handoff、Indexを追加した。

<!-- SOURCE_END 46: docs/documentation_index_20260721164248.md -->

---

<!-- SOURCE_BEGIN 47: docs/documentation_index_20260721172916.md -->

### Source 47: `docs/documentation_index_20260721172916.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721172916.md`
- Source SHA-512: `8551c81f6e817b21140832b9e7579c49c5a89e8f50a55de8c3f969efbe01452497853bc1c432de6bcb7f7d45f167a1aab6730fa6cc2b1e2806e2f257d54a88fc`
- Source Size: `3995` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 17:29:16 JST`
- 更新日時: `2026-07-21 17:29:16 JST`
- Snapshot: `20260721172916`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721164248.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G Minimal Web Surface           : Accepted
Phase 1-G Cross-thread Cancel           : Resolved
Phase 1-G Shutdown Cancel               : Resolved
Phase 1-H Summary Mode                  : Ready for Requirements／Design
Phase 1-ex                              : Accepted Reservation／Not Started
Phase 10 Original R&D Systems           : EASA／DLAGSA／OCILNS
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721164248.md](../history/documentation_index_20260721164248.md)から継承する。

本SnapshotはPhase 1-G Shutdown Cancel Follow-upのAccepted Reviewを追加し、Phase 1-G全体をAcceptedへ更新する。

EASA／DLAGSA／OCILNSの正式名称、公開範囲、Phase 10統合予約、個別ON／OFF要件は継続する。

## 3. Added Document

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [Phase 1-G Shutdown Cancel Follow-up Review](../history/handoffs/designer_review_phase_1g_shutdown_cancel_follow_up_20260721172916.md) | Shutdown Finding解消とPhase 1-G最終受入 |

## 4. Phase 1-G Final Result

### Accepted Areas

- FastAPI／Vanilla UI／SSEのDelivery Adapter分離
- Browser-owned Ephemeral Conversation
- Response Language／Max New Tokens／Thinking Visibility
- Streaming／Stop／New Chat／Post-cancel Generation
- Bounded Queue／Backpressure Cleanup
- Producer Thread上のNative Cancel／Close
- Active Generation Shutdown／Restart
- Token Exhaustion WarningとCanonical History分離
- Preview Basic Authentication／Non-loopback Fail Closed
- Safe Error／Shutdown Failure Visibility
- Model Load once／Close once

## 5. Verification

```text
Static Format／Lint／Type／Compile : Pass
Default Regression                    : 215 passed、3 deselected
Conversation／Web Targeted            : 32 passed
uv Lock                               : Pass／122 packages
Setup Shell Syntax                    : Pass
Implementer Native Model Smoke        : 2 passed、1 skipped
Implementer Manual Native Gate        : Shutdown／Restart／Generation Pass
Reviewer Native Model Smoke           : Environment Failure／2 failed、1 skipped
```

Reviewer Native FailureはPhase 1-G Source実行前の`llama_context` creationである。Phase 1-G Source Findingとせず、Phase 1全体の最終User Gateで再実行する。

## 6. Non-blocking Observation

Public Session Surfaceに未使用の`force_cancel()`定義が残る。Current Source Callerは0件であり、現行LifecycleはCooperative Cancelだけを使う。将来の並行実行拡張前に削除／非公開化またはThread-safe Contract化する。

## 7. Next Gate

```text
Phase 1-G Accepted
  ↓
Phase 1-H Summary Mode Requirements／Design
  ↓
ユーザー承認
  ↓
Phase 1-H Implementation
  ↓
Lightning Batch Upload／Native Validation
  ↓
User Manual／Phase 1 Final Gate
```

## 8. Deferred State

- Phase 1-H実装は未着手。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。
- Phase 10 Original R&D統合は将来予約のまま。

## 9. Authorization Boundary

本IndexはPhase 1-GのAccepted判定と次Gateを記録する。Phase 1-H実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 10. Append-Only

既存Review／Indexを変更せず、新TimestampのAccepted ReviewとIndexを追加した。

<!-- SOURCE_END 47: docs/documentation_index_20260721172916.md -->

---

<!-- SOURCE_BEGIN 48: docs/documentation_index_20260721174346.md -->

### Source 48: `docs/documentation_index_20260721174346.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721174346.md`
- Source SHA-512: `78cc027e218b88a72f0b5440b00c668a874e535a1b5b189635a9c82c5c1c09f0dab47e539e06fac38e2bd89ab3d38f906bf619a39996e5e1b82dcc1e997b094e`
- Source Size: `4244` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721172916.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H Requirements／Architecture   : Accepted
Phase 1-H Implementation               : Waiting User Authorization
Phase 1-F Lightning Native             : Deferred／Not Run
Phase 1-ex                              : Accepted Reservation／Not Started
Phase 10 Original R&D Systems           : EASA／DLAGSA／OCILNS
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721172916.md](../history/documentation_index_20260721172916.md)から継承する。

本SnapshotはPhase 1-H Summary Mode／UI Languageの正本要件、Architecture、Accepted ADR、実装担当Handoff、Roadmapを追加する。

Phase 1-G Accepted結果、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| accepted | [Phase 1-H Requirements](../history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md) | Summary Mode／UI Language正本要件 |
| accepted | [Phase 1-H Architecture](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md) | Pipeline／SSE／Cancel／i18n設計 |
| accepted | [ADR-0020](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md) | SummaryとUI Language分離判断 |
| waiting | [Implementer Handoff](../history/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md) | ユーザー承認後の実装範囲 |
| current | [Implementation Roadmap](../history/architecture/implementation_roadmap_20260721174346.md) | Phase 1-H以後の順序 |

## 4. Phase 1-H Decisions

### Summary Mode

- OFF／ON、Default OFF
- ONは同じMain Modelによる逐次2段生成
- Normal max 2048、Summary max 1024
- Summary Thinking disabled
- Original Canonical Finalだけを要約対象にする
- Original／Summary／Presentedを分離する
- Error／Empty／Context／LengthはWarning付きOriginal Fallback
- CancelはFallbackせずCancelled
- Application Config Schemaを3へ更新する
- Deployment Profileは変更しない

### UI Language

- 右上の日本語／English Switch
- Default日本語
- Response Language `ja／en／auto`と完全分離
- Browser-only Translation Dictionary
- UI LanguageだけをNamespaced Local Storageへ保存
- Model Output／Thinkingを翻訳しない
- 新規Dependencyなし

## 5. Preserved Phase 1-G Boundaries

- Browser-owned Ephemeral Conversation
- One Process／One Worker／One Model Instance
- Process-wide Non-blocking Generation Gate
- Producer Thread上のNative Cancel／Close
- Disconnect／Backpressure／ShutdownのCooperative Cancel
- Model Load once／Close once
- Preview Basic Auth／Non-loopback Fail Closed
- Plain Text Rendering／No External CDN
- Terminal Event Exactly Once

## 6. Phase 1-H Acceptance Direction

```text
Design Complete
  → User authorizes implementation
  → Implementer Status
  → Designer Review + New Index
  → User Mac Test
  → Batch Lightning Upload／Validation
```

## 7. Deferred State

- Phase 1-H Source／Config／UIは未変更。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。
- Phase 10 Original R&D統合は将来予約のまま。

## 8. Authorization Boundary

本IndexはPhase 1-H設計完了を記録する。Phase 1-H実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 9. Append-Only

既存文書を変更せず、Phase 1-H設計文書と新Indexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 48: docs/documentation_index_20260721174346.md -->

---

<!-- SOURCE_BEGIN 49: docs/documentation_index_20260721182038.md -->

### Source 49: `docs/documentation_index_20260721182038.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721182038.md`
- Source SHA-512: `cc6dd2632a1f230740e96cb602f2005b5cf09cf1741f0236e3d7e7b16a97d71810ce0bd6789e1cef716ee732b6077f5d10571c3eb6d6d5f57b300ab825d2c5b0`
- Source Size: `3942` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:20:38 JST`
- 更新日時: `2026-07-21 18:20:38 JST`
- Snapshot: `20260721182038`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721174346.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H Implementation               : Changes Requested
Phase 1-H Automated Verification       : Pass
Phase 1-H Mac Metal Model Smoke        : Pass outside Sandbox
Phase 1-H Contract／Preview Boundary   : 4 Mandatory Findings
Phase 1-F Lightning Native             : Deferred／Not Run
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721174346.md](../history/documentation_index_20260721174346.md)から継承する。

本SnapshotはPhase 1-H実装報告と設計Review結果を追加し、Phase 1-Hを`changes_requested`へ更新する。

Phase 1-G Accepted、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| reported | [Phase 1-H Implementer Status](../history/handoffs/implementer_status_phase_1h_summary_mode_and_ui_language_20260721181202.md) | 実装・検証報告 |
| changes_requested | [Phase 1-H Designer Review](../history/handoffs/designer_review_phase_1h_summary_mode_and_ui_language_20260721182038.md) | 独立検証と受入判定 |

## 4. Review Result

### Pass

- Summary OFF 1回／ON 2回の逐次Inference
- Summary Thinking disabled／max 1024
- Canonical FinalだけのSummary Prompt Boundary
- Fallback Matrix
- Cancel／Disconnect／Shutdown Thread Boundary
- Schema 3／Deployment Profile非変更
- UI Language／Response Language分離
- Local Storage境界
- Static／Type／Unit／Integration／Mac Metal Smoke

### Changes Required

1. Summary成功SSEからOriginal全文を除く。
2. Hidden／Buffered Generation中のSSE Keepaliveを追加する。
3. Summary Noteへ情報欠落／変形可能性を日英で追加する。
4. Runtime API失敗表示をUI Language切替後に再描画する。

## 5. Verification Evidence

```text
Format／Lint／Type／Compile            : Pass
Node Syntax                            : Pass
Default Test                           : 242 passed、3 deselected
Conversation／Summary／Web Targeted    : 47 passed
uv Lock                                : Pass／122 packages
Setup Shell Syntax                     : Pass
Mac Metal Model Smoke outside Sandbox  : 2 passed、1 skipped
```

自動Testは合格しているが、Successful Summary ResponseにOriginalが存在しないことをCurrent TestがAssertしていない。Test PassだけではAcceptance条件を満たさない。

## 6. Required Follow-up

```text
Designer Follow-up Handoff
  → User Authorization
  → Implementer Correction
  → Implementer Status
  → Designer Re-review＋Index
```

Lightning Full UploadはFollow-up Accepted後までDeferredとする。

## 7. Deferred State

- Phase 1-Hは未Accepted。
- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 8. Authorization Boundary

本IndexはReview結果を記録する。Phase 1-H Follow-up実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 9. Append-Only

既存Status／Review／Indexを変更せず、新TimestampのReviewとIndexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 49: docs/documentation_index_20260721182038.md -->

---

<!-- SOURCE_BEGIN 50: docs/documentation_index_20260721182416.md -->

### Source 50: `docs/documentation_index_20260721182416.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721182416.md`
- Source SHA-512: `1cd57b1a977c5e60765fbb65cbb232ad11f72917ab58f7a979985506a01f7c3063a27e7882d90c228feb5794ba378c23e1270e6a7849fe6fe6ec68e972085c5e`
- Source Size: `3247` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:24:16 JST`
- 更新日時: `2026-07-21 18:24:16 JST`
- Snapshot: `20260721182416`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721182038.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H Implementation               : Changes Requested
Phase 1-H Follow-up Handoff            : Ready／Waiting User Authorization
Phase 1-H Automated／Mac Metal Base    : Pass
Phase 1-F Lightning Native             : Deferred／Not Run
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721182038.md](../history/documentation_index_20260721182038.md)から継承する。

本SnapshotはPhase 1-H Reviewの4 Mandatory Findingを解消する実装担当Follow-up Handoffを追加する。

Phase 1-G Accepted、Phase 1-H正本要件、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Document

| 状態 | 文書 | 役割 |
|---|---|---|
| waiting_user_authorization | [Phase 1-H Review Follow-up Handoff](../history/handoffs/implementer_handoff_phase_1h_review_follow_up_20260721182416.md) | 4 Findingの限定修正指示 |

## 4. Follow-up Scope

1. Summary成功SSEからOriginal全文と重複Summary全文を除く。
2. 非本文Transformation Metadataへ整理する。
3. 15秒IntervalのSSE Comment Keepaliveを追加する。
4. KeepaliveのDisconnect／Cancel／Cleanup Testを追加する。
5. Summary Risk Noticeへ情報欠落／変形可能性を日英で追加する。
6. Runtime Known ErrorをUI Language切替後に再描画する。

Config Schema、Summary Prompt、Model Adapter、CLI、Dependencyは変更しない。

## 5. Fixed Follow-up Values

```text
Keepalive Interval : 15.0 seconds
Keepalive Format   : : keepalive\n\n
Summary Success    : Presented Summary only
Summary Fallback   : Presented Original only
Client Metadata    : Non-content Transformation State
```

## 6. Next Gate

```text
User authorizes Follow-up
  → Implementer Correction
  → Implementer Status
  → Designer Re-review＋New Index
  → User Mac Acceptance
  → Batch Lightning Upload／Validation
```

## 7. Deferred State

- Follow-up Source修正は未着手。
- Phase 1-Hは未Accepted。
- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 8. Authorization Boundary

本IndexとHandoffは修正範囲を定義する。Follow-up実装、Lightning操作、Upload、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 9. Append-Only

既存Status／Review／Indexを変更せず、新TimestampのFollow-up HandoffとIndexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 50: docs/documentation_index_20260721182416.md -->

---

<!-- SOURCE_BEGIN 51: docs/documentation_index_20260721184140.md -->

### Source 51: `docs/documentation_index_20260721184140.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721184140.md`
- Source SHA-512: `7782fe136862725b6b76bc00cf9090bdac65669274c0836e0f8debc34f870f2b23bb81994a4c0ba5061833854a9e2cb14d6b855eeb27c8d1d4eaf2d0581da371`
- Source Size: `4575` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:41:40 JST`
- 更新日時: `2026-07-21 18:41:40 JST`
- Snapshot: `20260721184140`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721182416.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Phase 1-H Mandatory Findings           : 4／4 Resolved
Phase 1-H Default Regression           : 246 passed、3 deselected
Phase 1-H Mac Metal Model Smoke        : 2 passed、1 skipped
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

変更のないCurrent Setは[documentation_index_20260721182416.md](../history/documentation_index_20260721182416.md)から継承する。

本SnapshotはPhase 1-H Review Follow-up実装報告とAccepted Reviewを追加し、Phase 1-H全体をAcceptedへ更新する。

Phase 1-G Accepted、Phase 1-ex予約、EASA／DLAGSA／OCILNS予約、公開名義、Append-only規則は継続する。

## 3. Added Documents

| 状態 | 文書 | 役割 |
|---|---|---|
| reported | [Phase 1-H Follow-up Status](../history/handoffs/implementer_status_phase_1h_review_follow_up_20260721183457.md) | 4 Finding修正と検証報告 |
| accepted | [Phase 1-H Follow-up Review](../history/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md) | Follow-up受入とPhase 1-H最終判定 |

## 4. Resolved Findings

1. Summary成功SSEからOriginal全文と重複Summary全文を除去した。
2. Non-content Transformation Metadataへ整理した。
3. 15秒SSE Comment Keepaliveを追加した。
4. KeepaliveのDisconnect／Cancel／Cleanup Regressionを追加した。
5. Summary Risk Noticeへ情報欠落／変形可能性を日英で追加した。
6. Runtime Known ErrorをUI Language切替後に再描画できるようにした。

前回4 Findingのうち、1と2は同一Data Minimization Findingの修正項目、3と4はKeepalive Findingの修正項目である。Mandatory Finding単位では4／4解消である。

## 5. Verification Evidence

```text
Format／Lint／Type／Compile            : Pass
Node Syntax                            : Pass
Default Test                           : 246 passed、3 deselected
Conversation／Summary／Web Targeted    : 51 passed
uv Lock                                : Pass／122 packages
Setup Shell Syntax                     : Pass
Mac Metal Model Smoke                  : 2 passed、1 skipped
Successful Summary Original Presence  : False
```

## 6. Current Accepted Phase 1-H Contract

```text
Summary Mode        : off／post_generation
Default             : off
Normal max          : Request／Default 2048
Summary max         : 1024
Summary Thinking    : disabled
Execution           : Same Main Model Sequential
Success Presentation: Summary only
Fallback Presentation: Original only＋Warning
Cancel              : Cancelled／No Fallback
Keepalive           : 15-second SSE Comment
UI Language         : ja／en Browser-only
Response Language   : ja／en／auto Independent
```

## 7. Non-blocking Observations

- Summary Stage Broad ExceptionのSafe Operator Logは将来Observabilityで扱う。
- Legacy `force_cancel()`はRuntime Caller 0件のまま残る。
- Lightning Native／Reverse ProxyでのKeepaliveはBatch Gateで確認する。

## 8. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → User Manual Finalization
  → Phase 1 Completion Gate
```

## 9. Deferred State

- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1全体の完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 10. Authorization Boundary

本IndexとReviewはPhase 1-HをAcceptedとする。Lightning操作、Upload、Model Transfer、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 11. Append-Only

既存Status／Review／Indexを変更せず、新TimestampのAccepted ReviewとIndexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 51: docs/documentation_index_20260721184140.md -->

---

<!-- SOURCE_BEGIN 52: docs/documentation_index_20260721184329.md -->

### Source 52: `docs/documentation_index_20260721184329.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721184329.md`
- Source SHA-512: `adcc4bf91fe8fe1a2f778ec39c008344363dc91dd1a29e6be0301c768d8fe52478bc26f940827f400dfedac4c8e4fffa24ee9241a64cf7d99b136846c9ab8fa8`
- Source Size: `4560` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:43:29 JST`
- 更新日時: `2026-07-21 18:43:29 JST`
- Snapshot: `20260721184329`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721184140.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Phase 1-H Mandatory Findings           : 4／4 Resolved
Phase 1-H Default Regression           : 246 passed、3 deselected
Phase 1-H Mac Metal Model Smoke        : 2 passed、1 skipped
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

文書集合とAccepted Evidenceは[documentation_index_20260721184140.md](../history/documentation_index_20260721184140.md)から継承する。

本SnapshotはPhase 1-H Accepted状態を変更せず、解消項目と4 Mandatory Findingの対応を明確化する。

Accepted Review：

[designer_review_phase_1h_review_follow_up_20260721184140.md](../history/handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md)

## 3. Four Resolved Findings

### Finding 1：Successful Summary SSE Data Minimization

- Summary成功SSEからOriginal全文を除去した。
- 重複Summary全文Fieldを除去した。
- Non-content Transformation Metadataへ整理した。
- Original不在をRaw SSE Testで固定した。

### Finding 2：Long Silent SSE Keepalive

- 15秒IntervalのSSE Comment Keepaliveを追加した。
- Hidden Normal／Buffered Summaryの両方をTestした。
- Disconnect／Cancel／Cleanup／Terminal Countを回帰確認した。

### Finding 3：Summary Risk Notice

- 情報欠落／変形可能性を日本語とEnglishの両方へ追加した。
- Initial HTMLとTranslation Dictionaryを一致させた。

### Finding 4：Runtime Error Relocalization

- Runtime StatusをStable Stateへ変更した。
- Known ErrorをUI Language切替後に再描画できるようにした。
- Response Languageとの独立性を維持した。

## 4. Verification Evidence

```text
Format／Lint／Type／Compile            : Pass
Node Syntax                            : Pass
Default Test                           : 246 passed、3 deselected
Conversation／Summary／Web Targeted    : 51 passed
uv Lock                                : Pass／122 packages
Setup Shell Syntax                     : Pass
Mac Metal Model Smoke                  : 2 passed、1 skipped
Successful Summary Original Presence  : False
```

## 5. Current Accepted Phase 1-H Contract

```text
Summary Mode           : off／post_generation
Default                : off
Normal max             : Request／Default 2048
Summary max            : 1024
Summary Thinking       : disabled
Execution              : Same Main Model Sequential
Success Presentation   : Summary only
Fallback Presentation  : Original only＋Warning
Cancel                 : Cancelled／No Fallback
Keepalive              : 15-second SSE Comment
UI Language            : ja／en Browser-only
Response Language      : ja／en／auto Independent
```

## 6. Non-blocking Observations

- Summary Stage Broad ExceptionのSafe Operator Logは将来Observabilityで扱う。
- Legacy `force_cancel()`はRuntime Caller 0件のまま残る。
- Lightning Native／Reverse ProxyでのKeepaliveはBatch Gateで確認する。

## 7. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → User Manual Finalization
  → Phase 1 Completion Gate
```

## 8. Deferred State

- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1全体の完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 9. Authorization Boundary

本IndexはPhase 1-H Accepted状態を継承する。Lightning操作、Upload、Model Transfer、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 10. Append-Only

前Indexを変更せず、4 Findingとの対応を明確化した新TimestampのIndexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 52: docs/documentation_index_20260721184329.md -->

---

<!-- SOURCE_BEGIN 53: docs/documentation_index_20260721185031.md -->

### Source 53: `docs/documentation_index_20260721185031.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721185031.md`
- Source SHA-512: `be2894bc632f88b6fec5b6b893a7b8c3236c79a802f769149923004a1f896d1e1ac1c6703f55091601379bd802ec21fd84cf34f9b18b68e1008f98da050ff950`
- Source Size: `5178` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:50:31 JST`
- 更新日時: `2026-07-21 18:50:31 JST`
- Snapshot: `20260721185031`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721184329.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Phase 1-H Mandatory Findings           : 4／4 Resolved
Phase 1-H Default Regression           : 246 passed、3 deselected
Phase 1-H Mac Metal Model Smoke        : 2 passed、1 skipped
Web／Lightning User Manual             : Updated／Current Candidate
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Lightning Account外Access              : Procedure Defined／Validation Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidenceと文書集合は[documentation_index_20260721184329.md](../history/documentation_index_20260721184329.md)から継承する。

本SnapshotはSource、Config、TestまたはPhase Acceptanceを変更しない。Phase 1 Web PreviewのMac起動、Lightning CUDA／CPU設定、Basic認証、Port公開、Account外Access、Current UI機能を新しいUser Manualへ統合した。

## 3. Current User Manual

[phase_1_web_and_lightning_user_manual_20260721185031.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md)

対象：

- Local Mac Web起動
- Lightning Project用uv 0.11.29
- Model Root設定
- Preview Basic認証
- CUDA Profile起動
- CPU Profile起動
- Lightning Port 8000公開
- Account外Browser Access
- Current Web UI設定
- Security Boundary
- Troubleshooting
- Lightning公開前Checklist

前Manual`phase_1_macos_user_manual_20260719171836.md`は履歴として保持し、新Manualがこれをsupersedeする。

## 4. Current Accepted Phase 1-H Contract

```text
Summary Mode           : off／post_generation
Default                : off
Normal max             : Request／Default 2048
Summary max            : 1024
Summary Thinking       : disabled
Execution              : Same Main Model Sequential
Success Presentation   : Summary only
Fallback Presentation  : Original only＋Warning
Cancel                 : Cancelled／No Fallback
Keepalive              : 15-second SSE Comment
UI Language            : ja／en Browser-only
Response Language      : ja／en／auto Independent
```

## 5. Lightning Public Preview Contract

```text
Bind Host              : 0.0.0.0
Bind Port              : 8000
Authentication         : Environment-only Basic／Mandatory for non-loopback
CUDA Profile           : config/profiles/lightning_linux_x86_64_cuda.toml
CPU Profile            : config/profiles/lightning_linux_x86_64_cpu.toml
Public Surface         : Lightning Port 8000 Public HTTPS URL
Studio Editor Sharing  : Not Required／Must not be substituted for App URL
External Validation    : Incognito／Logged-out Browser
```

## 6. Security Boundary

- Basic認証はPreview限定であり、本番Account機能ではない。
- CredentialをTracked FileまたはDocsへ保存しない。
- Public Portを有効にする前にBasic認証を設定する。
- Studio編集用URLとWeb App公開URLを区別する。
- External AccessはLightning Native／Reverse Proxy Gateで実測する。

## 7. Verification State

```text
Manual／Implementation Contract Match : Checked
Official Lightning Port Guidance      : Checked
Mac Web Manual Execution              : Waiting User Acceptance
Lightning CUDA／CPU Setup             : Waiting Full Upload／Native Gate
Lightning Public URL                  : Waiting User Operation
Account外Access                        : Waiting Incognito Acceptance
```

## 8. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Environment Rebuild
  → Lightning CUDA／CPU Native Validation
  → Lightning Web／Public URL／Reverse Proxy Validation
  → Account外Browser Acceptance
  → Cross-environment Final Review
  → Phase 1 Completion Gate
```

## 9. Deferred State

- Lightning Project／ModelのUploadはユーザー実施予定である。
- Lightning `.venv`再構築とNative Buildは未実施である。
- Lightning Full Native Gateは未完了である。
- Phase 1全体の完了宣言／Backupは未実施である。
- Phase 1-exは未着手である。
- Git／GitHub公開は未実施である。

## 10. Authorization Boundary

本IndexとUser Manualの作成は、Lightning操作、Upload、Model Transfer、Dependency Install、GPU利用、Port公開、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 11. Append-Only

前Indexと既存Manualを変更せず、新しいUser Manualを参照する新TimestampのIndexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 53: docs/documentation_index_20260721185031.md -->

---

<!-- SOURCE_BEGIN 54: docs/documentation_index_20260721191915.md -->

### Source 54: `docs/documentation_index_20260721191915.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260721191915.md`
- Source SHA-512: `4007b881b4f1f81aee94239ee2fd34fe5929a9873a2f4e05e9f80087a354a662bcbab5a08558252529dd4e1a9e9ba5f5606fb1080671ffc655534a9f20085e91`
- Source Size: `5157` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 19:19:15 JST`
- 更新日時: `2026-07-21 19:19:15 JST`
- Snapshot: `20260721191915`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721185031.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Web／Lightning User Manual             : Updated／Current Candidate
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1-ex                             : Accepted Reservation／Not Started
Docs Writer until Phase 1-ex Complete  : Current Designer Task Only
Phase Compilation Owner                : Current Designer Task
README Roadmap Priority                : Accepted Requirement
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Lightning User Manual、Current Phase状態は[documentation_index_20260721185031.md](../history/documentation_index_20260721185031.md)から継承する。

本Snapshotは、Phase 1-ex完了までのDocumentation Writerを現在の設計者役担当Taskへ一時統一し、README内でRoadmapを最優先導線にする要件を追加する。

## 3. New Accepted Requirements

[phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md](../history/requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md)

主要決定：

- Phase 1-ex完了まで`docs/`の全Fileを現在の設計者役が作成する。
- Implementer Status、External Docs Statusを含め、他担当はDocsへ直接書き込まない。
- Phase単位Lossless Compilationも現在の設計者役が担当する。
- README、LICENSE、CITATION、NOTICE等のPhase 1-ex Documentation成果物も現在の設計者役が作成する。
- License条件はユーザーが決定する。
- README上部で`docs/public/roadmap_ja.md`を中核公開文書として強調する。
- Phase 1-ex完了後のWriter分担は、新しいRole／Authority Policyで決める。

## 4. Common Handoff

[common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md](../history/handoffs/common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md)

このHandoffを、Phase 1-ex完了までの設計者役、実装者役、対外Docs役、将来のPhase別設計者役へ共通適用する。

## 5. Temporary Ownership Matrix

| Artifact | Writer until Phase 1-ex Completion | Input Provider |
|---|---|---|
| Requirements／Architecture／ADR | 現在の設計者役 | ユーザー／各担当 |
| Implementer Handoff | 現在の設計者役 | 設計者役 |
| Implementer Status Document | 現在の設計者役 | 実装者役の報告Payload |
| Review／Index | 現在の設計者役 | 実装Evidence |
| README／Public Docs | 現在の設計者役 | ユーザー／対外Docs役の提案Payload |
| Lossless Phase Compilation | 現在の設計者役 | Frozen Source Set |
| Project Continuity Master | 現在の設計者役 | 全Canonical Source |
| LICENSE文面 | 現在の設計者役がFile化 | ユーザーが権利条件決定 |

## 6. README Roadmap Contract

```text
README Position     : Project概要直後または同等に目立つ上部
Roadmap Link        : docs/public/roadmap_ja.md
Roadmap Role        : Current Position／All Phases／Future Integrationの中核公開文書
README Tone         : 日本語敬語
README End          : English Abstract
Broken Roadmap Link : Publication Gate Fail
```

READMEへRoadmap全文を複製せず、Roadmapを最初に参照するよう強く案内する。

## 7. Unchanged Boundaries

- Phase 1全体の完了宣言は未実施である。
- Lightning Native／Public URL Gateは未完了である。
- Phase 1-exは未開始である。
- Docs Migration、Lossless Compilation実行、README生成はまだ許可されていない。
- Git／GitHub公開は未実施である。
- Public License条件はまだ最終確定していない。

## 8. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → Phase 1 Completion Gate
  → Backup
  → Phase 1-ex Start Authorization
  → Single WriterによるDocs／Git／Public再整備
  → Phase 1-ex Completion Gate
```

## 9. Authorization Boundary

本Indexと新Requirements／Handoffの作成は、Source変更、Phase 1-ex開始、Docs Migration、Lossless Compilation実行、README／LICENSE生成、Git初期化、Commit、Push、GitHub公開またはLightning操作を自動許可しない。

## 10. Append-Only

前Indexと既存Role Policyを変更せず、Documentation単一WriterとRoadmap最優先導線を記録した新TimestampのIndexを追加した。新しいTimestampの本Indexを最新とする。

<!-- SOURCE_END 54: docs/documentation_index_20260721191915.md -->

---

<!-- SOURCE_BEGIN 55: docs/documentation_index_20260722023908.md -->

### Source 55: `docs/documentation_index_20260722023908.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260722023908.md`
- Source SHA-512: `76ff0a929a9b5f7333c5bd29822b88179bc213a1fbf02db42de67f3a9bf6fcf58b2d8f9db88d0f8246ac33cb3db0adae430e139b4a63f4c0086b1479a80930d5`
- Source Size: `4776` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-22 02:39:08 JST`
- 更新日時: `2026-07-22 02:39:08 JST`
- Snapshot: `20260722023908`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721191915.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1 Overall Completion             : Not Declared
Phase 1-ex                             : Accepted Reservation／Not Started
Public Roadmap                         : Created／Current
Docs Writer until Phase 1-ex Complete  : Current Designer Task Only
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件は[documentation_index_20260721191915.md](../history/documentation_index_20260721191915.md)から継承する。

本Snapshotは、ユーザーの明示指示によりPublic Roadmapを前倒し作成したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

本Roadmapは、現在の最小Web Previewだけでは伝わらないProject全体像を、次の進展として公開する中核文書である。

```text
Portable Model Runtime
  → Cross-platform Runtime
  → Conversation Continuity／Component Switchboard
  → Audit／Evidence／Generic Definition Platform
  → MARGPA Main Governance
  → Guardrail／Policy／Authority Governance
  → Judge／Evaluation／Repair／Observability
  → RAG／Data Governance
  → Agent／Tool／Memory／Handoff Governance
  → Experiment／Multi-Governance Platform
  → Hardening／Cloud Scale／External Original R&D Integration
```

## 4. Roadmap Core Message

MARGPA Runtime LLMは単なるLocal LLM、Chat UI、Model Wrapperを最終目的としない。

Model、Guardrail、Policy、Judge、Repair、RAG、Agent、Tool、Memory、Audit、Governance Definitionを独立Componentとして扱い、共有Governance Control Planeと分散Governance Pointを通じて、構成差の効果とCostを再現可能に比較するRuntime Governance型AI研究基盤を目指す。

## 5. Phase State Accuracy

Roadmapは、次を明示的に分離している。

- Complete／Accepted
- Repository Accepted
- Validation Waiting
- Accepted Reservation
- Planned
- Future R&D

Phase 1-G／1-HはAcceptedとして記載する。一方、Lightning Native Gate、User Acceptance、Cross-environment Final Review、Phase 1 Completion Declarationは未完了として記載する。

## 6. Governance Architecture Represented

- Governance Definition 0件Baseline
- 未知GD／未知Schema／任意JSON
- 特定GD名のCore Hard-code禁止
- Immutable Definition Source＋Adjustment＋Binding
- 共有Governance Control Plane＋分散Governance Point
- Functional ComponentとGovernanceの独立切替
- `off／observe／enforce`
- Deterministic Rule First
- Semantic Evaluation Budget
- Evidence／Action／Authority Boundary
- CDOGD非必須／Custom Orchestrator交換性

## 7. Original R&D Public Boundary

RoadmapはPhase 10に、公開決定済みの次の名称、研究領域、概要、接続方向だけを記載する。

- EASA
- DLAGSA
- OCILNS

独自Algorithm、内部Protocol、改竄耐性の具体方式、非公開実装情報は記載しない。

## 8. Scoped Authorization

既存Phase 1-ex要件ではPublic Docs生成をPhase 1-ex開始後としていたが、ユーザーは本TurnでRoadmapだけの前倒し作成を明示的に許可した。

この許可は`docs/public/roadmap_ja.md`の作成と、そのIndex反映だけを対象とする。

次を自動許可しない。

- README、Overview、Concept、LICENSE、CITATION、NOTICEの作成
- Phase 1-ex開始
- Docs Directory Migration
- Lossless Compilation実行
- Git初期化、Commit、Tag、Push
- GitHub公開
- Lightning外部操作
- Future Phase実装

## 9. Next Gate

```text
Public Roadmap Created
  → User Review
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

前Indexと既存Roadmap正本を変更せず、安定File名のPublic Roadmapと新TimestampのIndexを追加した。Public RoadmapはPhase 1-exでGit履歴へ移行予定のStable Derived Documentとして扱う。

<!-- SOURCE_END 55: docs/documentation_index_20260722023908.md -->

---

<!-- SOURCE_BEGIN 56: docs/documentation_index_20260723131526.md -->

### Source 56: `docs/documentation_index_20260723131526.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260723131526.md`
- Source SHA-512: `97d0f463a2d333b2f5e5044ecf957e55a32bcec2041e7141c730ac3370a11914f8d37b653cba3ace4ef6e304d86ec0f72404c2950367c02a7eb52ebf5841686e`
- Source Size: `4722` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:15:26 JST`
- 更新日時: `2026-07-23 13:15:26 JST`
- Snapshot: `20260723131526`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260722023908.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1 Overall Completion             : Not Declared
Phase 1-ex                             : Accepted Reservation／Not Started
Public Roadmap                         : Updated／Current
Future ML Extension                    : Added／Future Reservation
Quantitative／Qualitative Evaluation   : Added／Future Reservation
Docs Writer until Phase 1-ex Complete  : Current Designer Task Only
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Public Roadmapの基本構成は[documentation_index_20260722023908.md](../history/documentation_index_20260722023908.md)から継承する。

本Snapshotは、ユーザーの明示指示によりPublic Roadmap後半へML追加と定量／定性評価設定の将来予約を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

Previous Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

Previous Snapshot SHA-512：

```text
5585a1e5f11633306f645fe16fcf6a1311349d4bd359c3242491d9be88ad184dce722b5f6a57b5ff7e58543fbc661ec4de9fb293f7e7c7be1a1c079af948e344
```

## 4. Future ML Extension

Phase 10のFuture Trackへ、Machine Learning／Training／Adaptation Extensionを追加した。

対象候補：

- Dataset Registry／Version／Digest／Provenance
- Traditional Machine Learning
- Fine-tuning／LoRA等のAdaptation
- Training Run／Experiment Identity
- Candidate Model Artifact
- Baseline Comparison
- Model Promotion／Rollback
- Drift／Regression Detection

Current Phase 1ではWeight更新を行わない。将来もUser Conversationから暗黙にWeightを更新するOnline LearningをDefaultにしない。

## 5. Quantitative／Qualitative Evaluation

次を独立して設定可能にする将来要件をRoadmapへ追加した。

```text
定量評価 : OFF／ON
定性評価 : OFF／ON

Mode:
  quantitative
  qualitative
  combined
  off
```

`combined`は定量＋定性を意味する。両者を単一Scoreへ無条件に圧縮せず、別Evidenceとして保持する。

## 6. Configuration Boundary

Conceptual Structure：

```toml
[components.machine_learning]
enabled = false

[components.evaluation]
enabled = true
mode = "combined"

[components.evaluation.quantitative]
enabled = true

[components.evaluation.qualitative]
enabled = true
```

最終Key／Schemaは対象Phaseで確定する。ML、Training、定量評価、定性評価を個別にON／OFF可能とする。

## 7. Validation Boundary

- `combined`と各Switchの矛盾を黙って自動修正しない。
- 両評価OFFを評価済みと記録しない。
- 定量評価はDataset、Metric、Threshold、Sample、Seed、Versionを記録する。
- 定性評価はRubric、Evaluator、Version、Scopeを記録する。
- Judge結果をGround Truthまたは最終Authorityと同一視しない。
- Candidate Modelは評価と採用Gate前にCurrent Modelを上書きしない。
- OFF時は対象処理、Training、Model Call、Artifact Write、Side Effectを行わない。

## 8. Scoped Authorization

本更新はPublic RoadmapへのFuture Reservation追加とIndex反映だけを対象とする。

次を自動許可しない。

- ML／Training／Fine-tuning／LoRA実装
- Dataset取得／登録
- Model Download／Weight更新
- Config実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作
- Future R&D System実装

## 9. Next Gate

```text
Roadmap Future ML／Evaluation Reservation Added
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

更新前のPublic Roadmapを`docs/public/history/`へ不変Snapshotとして保存したうえで、Stable Current RoadmapへFuture ML／Evaluation要件を追加した。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 56: docs/documentation_index_20260723131526.md -->

---

<!-- SOURCE_BEGIN 57: docs/documentation_index_20260723131846.md -->

### Source 57: `docs/documentation_index_20260723131846.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260723131846.md`
- Source SHA-512: `7a845da62e7dfb8e8c30111c764b1a8dd198ef7c2dcf7d8c66ff30cc002ad5c5db39e38ddce66ec249b336a6ce26fa9b0d3d1e2ba59b3c67165bdf7b766e452a`
- Source Size: `4028` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:18:46 JST`
- 更新日時: `2026-07-23 13:18:46 JST`
- Snapshot: `20260723131846`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723131526.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Evaluation Mode              : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件およびFuture ML Extensionは、[documentation_index_20260723131526.md](../history/documentation_index_20260723131526.md)から継承する。

本Snapshotは、ユーザーの訂正により、Future機能の直前Snapshotにおける旧称を「定量計算モード」として正規化したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

## 4. Future ML／Evaluation Modes

Phase 10のFuture Trackに、次を予約する。

```text
ML／Training／Adaptation
定量計算モード : OFF／ON
定性評価モード : OFF／ON

Mode:
  quantitative_calculation
  qualitative
  combined
  off
```

`combined`は、定量計算結果と定性評価結果を別Evidenceとして保持したうえで併用する。両者を無条件に単一Scoreへ圧縮しない。

## 5. Conceptual Configuration

```toml
[components.machine_learning]
enabled = false

[components.evaluation]
enabled = true
mode = "combined"

[components.evaluation.quantitative_calculation]
enabled = true

[components.evaluation.qualitative]
enabled = true
```

最終Key／Schemaは対象Phaseで確定する。上記名称をCoreへHard-codeする指示ではない。

## 6. Validation Boundary

- `combined`と各Switchの矛盾を黙って自動修正しない。
- 両方OFFの場合、計算・評価済みと記録しない。
- 定量計算モードはDataset、Metric、Threshold、Sample、Seed、Versionを記録する。
- 定性評価モードはRubric、Evaluator、Version、Scopeを記録する。
- Judge結果をGround Truthまたは最終Authorityと同一視しない。
- ML Component、Training Pipeline、定量計算モード、定性評価モードは個別にON／OFF可能とする。
- OFF時は対象処理、Training、Model Call、Artifact Write、Side Effectを行わない。

## 7. Scoped Authorization

本更新はPublic Roadmapの用語訂正と最新Index作成だけを対象とする。

次を自動許可しない。

- ML／Training／Fine-tuning／LoRA実装
- Dataset取得／登録
- Model Download／Weight更新
- Config実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作
- Future R&D System実装

## 8. Next Gate

```text
Future Mode Terminology Corrected
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 9. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 57: docs/documentation_index_20260723131846.md -->

---

<!-- SOURCE_BEGIN 58: docs/documentation_index_20260723133644.md -->

### Source 58: `docs/documentation_index_20260723133644.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260723133644.md`
- Source SHA-512: `12d2a5f096d0e37f53dc20839f49299b0829aa37e9536df2000759ade9e966c202e8f98074259502f05f80a5c1d9320f9fc32285c7cd086755e30a79b2f77079`
- Source Size: `4033` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:36:44 JST`
- 更新日時: `2026-07-23 13:36:44 JST`
- Snapshot: `20260723133644`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723131846.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件およびFuture ML Extensionは、[documentation_index_20260723131846.md](../history/documentation_index_20260723131846.md)から継承する。

本Snapshotは、ユーザーの訂正により、定量側と定性側の両方を「計算モード」として正規化したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

## 4. Future ML／Calculation Modes

Phase 10のFuture Trackに、次を予約する。

```text
ML／Training／Adaptation
定量計算モード : OFF／ON
定性計算モード : OFF／ON

Mode:
  quantitative_calculation
  qualitative_calculation
  combined
  off
```

`combined`は、定量計算結果と定性計算結果を別Evidenceとして保持したうえで併用する。両者を無条件に単一Scoreへ圧縮しない。

## 5. Conceptual Configuration

```toml
[components.machine_learning]
enabled = false

[components.evaluation]
enabled = true
mode = "combined"

[components.evaluation.quantitative_calculation]
enabled = true

[components.evaluation.qualitative_calculation]
enabled = true
```

最終Key／Schemaは対象Phaseで確定する。上記名称をCoreへHard-codeする指示ではない。

## 6. Validation Boundary

- `combined`と各Switchの矛盾を黙って自動修正しない。
- 両方OFFの場合、計算済みと記録しない。
- 定量計算モードはDataset、Metric、Threshold、Sample、Seed、Versionを記録する。
- 定性計算モードはRubric、Evaluator、Version、Scopeを記録する。
- Judge結果をGround Truthまたは最終Authorityと同一視しない。
- ML Component、Training Pipeline、定量計算モード、定性計算モードは個別にON／OFF可能とする。
- OFF時は対象処理、Training、Model Call、Artifact Write、Side Effectを行わない。

## 7. Scoped Authorization

本更新はPublic Roadmapの用語訂正と最新Index作成だけを対象とする。

次を自動許可しない。

- ML／Training／Fine-tuning／LoRA実装
- Dataset取得／登録
- Model Download／Weight更新
- Config実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作
- Future R&D System実装

## 8. Next Gate

```text
Future Calculation Mode Terminology Corrected
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 9. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 58: docs/documentation_index_20260723133644.md -->

---

<!-- SOURCE_BEGIN 59: docs/documentation_index_20260723134544.md -->

### Source 59: `docs/documentation_index_20260723134544.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260723134544.md`
- Source SHA-512: `7608536f8ff6eafd40ca858d8b81be1c705aa19f26865c164c694b62b6f3d822a790cb68e06cf7040293e7529b0cf72a56ce4e1b1ee8ba85c4363a60a798a75e`
- Source Size: `4637` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:45:44 JST`
- 更新日時: `2026-07-23 13:45:44 JST`
- Snapshot: `20260723134544`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723133644.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Research／Developer Mode                 : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Future ML Extensionおよび定量／定性計算モードは、[documentation_index_20260723133644.md](../history/documentation_index_20260723133644.md)から継承する。

本Snapshotは、将来の一般向けProduct化を考慮した「研究・開発者モード」の予約を記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

## 4. Research／Developer Mode

Phase 2のConfiguration Control Surfaceへ、次のGlobal UI Optionを追加した。

```text
研究・開発者モード : OFF／ON

OFF:
  一般利用者向けの基本設定だけを表示する

ON:
  研究・開発者向けの設定群を表示し、許可された範囲で編集可能にする
```

Conceptual Config：

```toml
[ui.research_developer_mode]
enabled = false
```

一般公開ProfileではDefaultを`OFF`とする。Local環境または許可された利用者は`ON`へ切替可能とし、Public Deploymentでは切替権限をAccess Control Policyで決定する。

## 5. Candidate Advanced Setting Groups

- Model／Backend／Artifact
- 詳細Generation Parameter
- Context／Token／Performance
- Component別ON／OFF
- Governance Point別`off／observe／enforce`
- Guard／Judge／Repair／RAG／Agent
- 定量計算モード／定性計算モード
- Experiment Profile／Seed／Baseline
- Audit／Evidence／Status
- ML／Training／Adaptation

## 6. Separation Boundary

研究・開発者モードは、高度設定群の表示と編集入口をまとめて切り替える。

次を意味しない。

- 権限の新規付与
- Policyの解除
- Guardrail／Governance／Auditの解除
- Tool実行許可
- Componentの一括有効化
- 不正な設定組合せの受理

個々のComponent、Governance Point、定量計算モード、定性計算モードのON／OFFは独立設定として保持する。

## 7. Validation／Security Boundary

- `ON`でもAccess Control、Tool Permission、Approval、Dependency、Conflict、Capability、Schema Validationを迂回できない。
- `OFF`でもServer側の検証、安全機構およびAuditを自動的に無効化しない。
- UIで非表示にするだけでSecurity Boundaryが成立したとみなさない。
- Clientから直接送信された未許可設定はServer側で拒否する。
- 設定変更前後のDiff、Source、Apply Resultを表示し、Audit Eventとして記録可能にする。

## 8. Scoped Authorization

本更新はPublic RoadmapへのFuture Reservation追加と最新Index作成だけを対象とする。

次を自動許可しない。

- UI／Config／Access Control実装
- ML／Training実装
- Model Download／Weight更新
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作

## 9. Next Gate

```text
Research／Developer Mode Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 59: docs/documentation_index_20260723134544.md -->

---

<!-- SOURCE_BEGIN 60: docs/documentation_index_20260725132748.md -->

### Source 60: `docs/documentation_index_20260725132748.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725132748.md`
- Source SHA-512: `ebd7420bd1eae477e89c785556b67b8eef32910a72ac2c1644dc56a38193620e69bb0befcc4b16637a11e947117c967e13aedc00e5ecae6728e1364958c54408`
- Source Size: `5025` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 13:27:48 JST`
- 更新日時: `2026-07-25 13:27:48 JST`
- Snapshot: `20260725132748`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723134544.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Public Warranty Disclaimer               : Reserved for Phase 1-ex
Phase 4 UI Interaction Requirements      : Added／Planned
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Research／Developer Mode                 : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Future ML Extension、定量／定性計算モードおよび研究・開発者モードは、[documentation_index_20260723134544.md](../history/documentation_index_20260723134544.md)から継承する。

本Snapshotは、Phase 1-exの公開免責要件とPhase 4のUI Interaction要件を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

## 4. Phase 1-ex Public Warranty Disclaimer

Phase 1-exで作成するREADMEと`LICENSE`の両方に、本Projectおよび配布物について一切の動作保証を行わない旨を明記する。

対象：

- 動作
- 可用性／継続性
- 互換性
- 正確性
- 安全性
- 特定目的への適合性
- Hardware／OS／Backend／Model／Dependency／外部Service／設定差

READMEには一般利用者向けの明確な日本語の注意書きを置く。`LICENSE`には採用利用条件と整合する正式な免責条項を置き、適用法令で認められる範囲の責任制限を明記する。

## 5. Phase 4 Local Folder Input

- 「ローカルフォルダを追加」ボタン
- Folderのドラッグ＆ドロップ（Drag and Drop）
- 対象、File数、Size、処理状態、Errorの表示
- 個別解除
- 未選択Pathの自動走査禁止
- 元Fileの変更、移動、削除禁止
- Hidden File、Secret、Symbolic Link、巨大Folder、未対応形式、重複FileのValidation
- 外部ServerへUploadする場合の事前表示
- Source Identity、Hash、採用範囲、処理結果のTraceability

Phase 4ではUI Entry Pointと安全な受渡し境界を設計し、本格的なIndex、Retrieval、Document更新はPhase 7のRAG責務と整合させる。

## 6. Phase 4 Generation Stop

- `Ctrl+C`を一般利用者向け停止方法にしない。
- 生成中に「停止」ボタンを表示する。
- Cooperative CancelをRuntimeへ伝播する。
- 受付、処理中、完了を区別する。
- 部分出力へ`cancelled`等の状態を関連づける。
- Cancel Eventと取得可能なEvidenceをAuditへ残す。

## 7. Phase 4 Send Interaction

長文や大きなContextではEnter単独送信による誤送信Riskが高まるため、Enter単独送信を固定仕様にしない。

検討候補：

- Enterで改行
- `Cmd+Enter`／`Ctrl+Enter`で送信
- 明示的な送信ボタン
- Enter送信の利用者設定
- IME変換確定中の誤送信防止
- Desktop／Mobile別操作
- 長文時の送信前状態の明確化

初期推奨候補は「Enterで改行、`Cmd+Enter`／`Ctrl+Enter`または送信ボタンで送信」とする。最終仕様はPhase 4で決定する。

## 8. Scoped Authorization

本更新はPublic Roadmapへの将来要件追加と最新Index作成だけを対象とする。

次を自動許可しない。

- README／LICENSEの現時点での作成または変更
- UI／Folder Input／RAG実装
- Phase 1-exまたはPhase 4の開始
- Git／GitHub操作
- Lightning外部操作

## 9. Next Gate

```text
Public Disclaimer／Phase 4 UI Requirements Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 60: docs/documentation_index_20260725132748.md -->

---

<!-- SOURCE_BEGIN 61: docs/documentation_index_20260725133218.md -->

### Source 61: `docs/documentation_index_20260725133218.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725133218.md`
- Source SHA-512: `b825c98828d6486bca6c781bdea175860dedcda9a2677d84c8919e70f066112f1922ffcf50ca7edb924e6ab5cfa767e17692fd30bb4e26f97164c54a949d64ec`
- Source Size: `4868` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 13:32:18 JST`
- 更新日時: `2026-07-25 13:32:18 JST`
- Snapshot: `20260725133218`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725132748.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Public Warranty Disclaimer               : Reserved for Phase 1-ex
Phase 4 UI Interaction Requirements      : Added／Planned
Responsive UI／Multi-device Experience   : Added／Future Phase
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Research／Developer Mode                 : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Phase 1-ex公開免責およびPhase 4 UI Interaction要件は、[documentation_index_20260725132748.md](../history/documentation_index_20260725132748.md)から継承する。

本Snapshotは、後半PhaseへResponsive UI／Multi-device Experienceを追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

## 4. Placement

Responsive UI／Multi-device Experienceは、Phase 10のFuture R&Dへ配置する。

Phase 2およびPhase 4では本格的な全端末最適化を完了条件にせず、後続対応を妨げないComponent構造とCSS／Layout Boundaryを維持する。本格対応と検証は基本UIおよび主要Runtime機能の安定後に行う。

## 5. Target Environments

- Smartphone
- Tablet
- Laptop
- Desktop
- Wide Display
- Portrait／Landscape
- 異なるViewport
- 異なるDevice Pixel Ratio
- Browser Zoom／OS Text Scaling
- Mouse／Trackpad／Keyboard／Touch
- Mobile Virtual Keyboard／Safe Area

## 6. Main Responsive Surfaces

- Chat Timeline
- Composer／Send／Stop
- New Chat／History／Navigation
- Basic Settings
- 研究・開発者モード／高度設定群
- Governance／Guard／Judge／Repair／Agent Status
- Audit／Evidence／Source
- Dialog／Notification／Error
- Local Folder／File入力のCapability別Fallback

## 7. Design Boundary

- Device名だけで分岐せず、ContentとLayoutが破綻する幅を基準にBreakpointを決める。
- 狭い画面ではSidebarや高度設定をDrawer、Sheetまたは段階表示へ切り替える。
- Send／StopはTouch TargetとThumb Reachを考慮する。
- Virtual Keyboard表示中もComposerと主要操作を失わない。
- Code、Table、Audit Detail等を除き、意図しない横Scrollを発生させない。
- Text Reflow、Contrast、Focus、Keyboard、Screen Reader Labelを考慮する。
- 日本語／英語のLabel長差で操作を欠落させない。
- 未対応CapabilityはFallbackまたはWarningを表示する。
- Responsive UIをAccess ControlまたはSecurity Boundaryの代替にしない。

## 8. Validation Candidates

- 代表ViewportとBreakpoint境界値
- Orientation変更
- Browser Zoom
- OS Text Size
- Desktop Keyboard／Touch
- Mobile Virtual Keyboard
- 日本語／英語UI
- 長文／Code Block／大きなAudit Detail
- Streaming／Stop／Error／Reconnect

Responsive Webと、将来のNative Mobile App／PWAは別Decisionとして扱う。

## 9. Scoped Authorization

本更新はPublic Roadmapへの将来要件追加と最新Index作成だけを対象とする。

次を自動許可しない。

- Responsive UI実装
- Native Mobile App／PWA実装
- Phase 1-exまたはFuture Phaseの開始
- Git／GitHub操作
- Lightning外部操作

## 10. Next Gate

```text
Responsive UI／Multi-device Experience Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 11. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 61: docs/documentation_index_20260725133218.md -->

---

<!-- SOURCE_BEGIN 62: docs/documentation_index_20260725162648.md -->

### Source 62: `docs/documentation_index_20260725162648.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725162648.md`
- Source SHA-512: `a148f248592fa51eab02144cfc77b807afbbac4530661a615d8a5e58a131f44a0bde3d18a9437f519e78cc746211e67e25b1b63a685f6823c8dd1bfca68c45ba`
- Source Size: `7009` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 16:26:48 JST`
- 更新日時: `2026-07-25 16:26:48 JST`
- Snapshot: `20260725162648`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725133218.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Phase Docs Language／Filename Policy     : Added／Phase 1-ex Reservation
Public Warranty／Switch Notice           : Added／Phase 1-ex Reservation
LLM Validation／Evaluation Design        : Added／Phase 9 Reservation
Responsive UI／Multi-device Experience   : Added／Future Phase
Future ML Extension                      : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、公開免責、Phase 4 UI InteractionおよびResponsive UI要件は、[documentation_index_20260725133218.md](../history/documentation_index_20260725133218.md)から継承する。

本Snapshotは、Phase 1-exのDocs言語／Filename Policy、既存規約文書の再利用候補、ON／OFF可能設計に伴う留意事項、およびJudge導入後のLLM動作検証／評価設計を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](../../../../public/history/roadmap_phase_1_ja.md)

## 4. Existing Fragmented Development Docs

Phase統合前のRequirements、Architecture、ADR、Review、Handoff、Status、Index等は、一括英訳または機械的Renameの対象にしない。

- 既存Path、Filename、Timestamp、State、本文、Hashを保持する。
- 原文を英訳目的で書き換えない。
- Phase単位Lossless CompilationのSourceとして扱う。
- 公開可否はGitHub AllowlistとPrivacy／Secret Scanで別途決定する。

## 5. Phase Compilation Documents

Phaseごとに一つの日本語統合文書を作成し、Filenameへ`_ja`を付ける。

```text
phase_1_compilation_ja.md
phase_2_compilation_ja.md
```

統合作業では、元資料を勝手に要約、意訳、再解釈または意味変更しない。Source Set、Path、State、Size、SHA-512および抽出可能性を記録する。

## 6. Public Document Filenames

人が直接読む公開文書は、原則として日本語正本を`_ja`で示す。

```text
overview_ja.md
concept_ja.md
roadmap_ja.md
requirements_specification_ja.md
system_architecture_ja.md
technology_selection_ja.md
basic_design_ja.md
runtime_governance_specification_ja.md
```

慣例的な固定名は例外とする。

- `README.md`
- `LICENSE`
- `CITATION.cff`
- `NOTICE.md`
- 必要に応じた`TERMS_OF_USE.md`

`README.md`は日本語を主とし、末尾に英語Abstractを置く。

## 7. Optional English Documents

余力がある場合に限り、Phase統合文書と公開文書の英語版を`_en`で作成できる。

- 英語版は必須Phase Gateにしない。
- 日本語正本をSource of Truthとする。
- 対応日本語File、Version、SnapshotまたはHashを示す。
- 要件、権限、免責、Status、未解決事項を追加、削除または弱化しない。
- 同期状態を明示する。

## 8. Prior TERMS_OF_USE／NOTICE Reuse

ユーザーが別Projectで作成した`TERMS_OF_USE.md`と`NOTICE.md`を後日提示した場合、再利用可能な条項を候補SourceとしてReviewする。

確認対象：

- Project名／対象範囲
- 利用許諾／禁止事項
- 免責／責任制限
- 第三者License／Model License
- Hosted Service条件
- README／LICENSE／NOTICE／TERMS_OF_USE間の矛盾

無検証のCopyは行わない。

## 9. ON／OFF Research Design Notice

本Projectは研究、比較および検証のため、各Componentと各Governance Pointを個別にON／OFF可能にする方向で設計する。

そのため、READMEの留意事項と、必要に応じて`LICENSE`、`TERMS_OF_USE.md`または`NOTICE.md`へ次を記載する。

- すべての設定組合せの動作、安全性または妥当性を保証しない。
- OFFにしたComponentの検査、制御、修復またはEvidenceが失われる可能性がある。
- Effective Config、無効Component、Warning、Degraded Stateを可能な範囲で表示・記録する。
- 研究自由度を理由にAccess Control、外部Authority、Tool Permissionまたは法令を迂回しない。
- 無意味、未対応または危険な組合せを黙って受理しない。

## 10. LLM動作検証／評価設計

Judge／Evaluation／Repairの基礎が成立するPhase 6より後のPhase 9に配置する。

主な対象：

- AI Research／AI Architecture／Software Engineering支援
- 要件／設計／実装支援
- 一般質問／雑談
- 日本語／英語
- Instruction／Premise／Context／Decision Preservation
- Governance／Guard／Judge／Repairの構成差
- RAG／Agent／Toolは各実装後に追加
- Streaming／Cancel／Context Limit
- Latency／Token／Memory／Failure Rate

評価には、Version付きEvaluation Set、定量計算モード、定性計算モード、Human Review、LLM-as-a-Judge、Baseline、Regression、Ablation、EvidenceおよびReproduction Procedureを含める。

Judgeを唯一のGround Truthまたは最終Authorityにしない。Judge Bias、Position Effect、Verbosity Bias、Language差およびModel依存性を検証する。評価結果が良好でも、READMEまたは`LICENSE`上の動作保証を意味しない。

## 11. Scoped Authorization

本更新はPublic Roadmapへの将来要件追加と最新Index作成だけを対象とする。

次を自動許可しない。

- 既存DocsのRename／Translation／統合
- README／LICENSE／NOTICE／TERMS_OF_USE作成
- LLM Validation／Evaluation実装
- Judge／ML／Future Phase実装
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作

## 12. Next Gate

```text
Phase 1-ex Docs／Notice and Future Evaluation Design Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 13. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 62: docs/documentation_index_20260725162648.md -->

---

<!-- SOURCE_BEGIN 63: docs/documentation_index_20260725164739.md -->

### Source 63: `docs/documentation_index_20260725164739.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725164739.md`
- Source SHA-512: `432224d5b82e480c12c67e42c62c80a0c9782d66ee328eedfc330d18fadecc1bd2aa098d66a6c8e64cffd07187f91b32685c518dd6416a2e346f972e91373f67`
- Source Size: `6376` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 16:47:39 JST`
- 更新日時: `2026-07-25 16:47:39 JST`
- Snapshot: `20260725164739`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725162648.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Public Documentation Corpus              : Added／Phase 1-ex Reservation
Project Documentation Explainer          : Added／Phase 2 Optional Reservation
Full RAG                                 : Phase 7 Planned
LLM Validation／Evaluation Design        : Phase 9 Reserved
Responsive UI／Multi-device Experience   : Future Phase Reserved
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、Phase 1-ex Docs言語／Filename Policy、公開免責、ON／OFF留意事項およびLLM動作検証／評価設計は、[documentation_index_20260725162648.md](../history/documentation_index_20260725162648.md)から継承する。

本Snapshotは、Public Documentation Corpus、軽量Project Documentation ExplainerおよびPhase 7 Full RAGへの拡張境界を追加したことを記録する。

## 3. Preliminary Repository Observation

2026-07-25時点のRead-only Preliminary Scan：

```text
docs/ File Count             : 264
docs/ Markdown Count         : 262
docs/ Approximate Size       : 2.7 MB
Private Key Pattern          : Not Detected
Common API Token Pattern     : Not Detected
Identifier／Local Path Files : 8
docs/public Markdown         : Relevant Pattern Not Detected
```

これは公開承認または完全なSecret Scanを意味しない。Phase 1-exで対象Snapshotを固定し、改めてPrivacy、Secret、PathおよびPublic Allowlistを検証する。

## 4. Corpus Boundary

`docs/`全体を無差別にCorpusへ投入しない。

Default Corpus候補：

- GitHub公開Allowlistに含まれる日本語正本`*_ja.md`
- 必要な慣例名Public Document
- Current Stateの文書

Default除外：

- Phase統合前のHandoff／Status／Review／Index
- Superseded Snapshot
- Local Path／旧識別情報／非公開URLを含む文書
- Markdown以外の不要File

Corpus ManifestへPath、Title、Language、State、Snapshot、Size、SHA-512を記録する。

## 5. Project Documentation Explainer

Phase 2のOptional Early Featureとして予約する。

```text
Project Documentation Explainer : OFF／ON
```

目的：

- Project Overviewの説明
- Architectureの説明
- Roadmap／Current Statusの説明
- Governance Conceptの説明
- 公開Docsに基づく一問一答
- Multi-turn成立後のSource付きFollow-up

## 6. Lightweight Preview Boundary

- Embedding Model／Vector Storeを必須にしない。
- 日本語対応の軽量Lexical／Character N-gram Retriever候補を使用する。
- Adapter経由で交換可能にする。
- 関連ChunkだけをContext Budget内で注入する。
- Source Document／Section／Linkを表示する。
- Snapshot／Chunk／Score／Digest／Token Budgetを記録可能にする。
- Retrieval失敗、Corpus不足、Context切捨てを表示する。
- Retrieved TextをInstructionではなくSource Dataとして扱う。
- Docs内の命令表現をRuntime Instructionとして実行しない。
- Docsに基づく説明とModel推測を区別する。
- OFF時はIndex Load、Retrieval、Context Injectionおよび追加Writeを行わない。

## 7. README Claim Gate

未実装時：

> 将来、このProjectの公開Docsを参照し、LLM自身にProjectを説明させる機能を予定しています。

実装とAcceptance完了後：

> このProjectについて、公開Docsを参照しながらLLM自身に説明させることができます。

実装前に現在利用可能な機能として記載しない。実装後もSourceと既知の限界を併記する。

## 8. Full RAG Boundary

軽量ExplainerはFull RAGを代替しない。

Phase 7で追加する候補：

- Arbitrary Local Document Registration
- Embedding
- Vector Store
- Multiple Corpus
- Document Update／Delete
- Index Lifecycle
- RAG Governance
- Data Leakage／Prompt Injection Control

早期Previewを実装した場合も、同一Retrieval／Evidence PortからPhase 7へ拡張する。

## 9. Early Implementation Gate

一問一答だけでもProject説明Demoとして有意義である。

ただし早期実装は、次をすべて満たす場合に限る。

- Phase 1-exの公開正本とCorpus Manifestが完成している。
- Privacy／Secret／Path Scanが完了している。
- 新規Embedding ModelまたはVector Storeを要求しない。
- Model Adapter／Conversation CoreへRAG固有依存を漏らさない。
- Source表示、Context Budget、Failure State、OFF動作をTestできる。
- Phase 1完了、公開移行または主要Gateを遅延させない。

満たさない場合はPhase 2またはPhase 7へ延期する。

## 10. Scoped Authorization

本更新はPublic Roadmapへの要件予約と最新Index作成だけを対象とする。

次を自動許可しない。

- RAG／Retriever／Index実装
- Docs全体のCorpus登録
- READMEへの実装済みClaim追加
- Embedding Model／Dependency Download
- Phase 1-ex／Phase 2／Phase 7開始
- Git／GitHub操作
- 外部環境操作

## 11. Next Gate

```text
Project Documentation Explainer Reserved
  → Phase 1 Current Gate継続
  → Cross-environment／Local Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex Public Corpus Preparation
  → Optional Early Explainer Decision
```

## 12. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 63: docs/documentation_index_20260725164739.md -->

---

<!-- SOURCE_BEGIN 64: docs/documentation_index_20260725192903.md -->

### Source 64: `docs/documentation_index_20260725192903.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725192903.md`
- Source SHA-512: `07d7c31551186632eedc3cb23561b8ea86025c09103cd10305800994be6e01bc29bb3ae051cd88ce0ead496e82281aad21bfb2394c5d0bf3b59fe6ca0bcfd52f`
- Source Size: `5958` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 19:29:03 JST`
- 更新日時: `2026-07-25 19:29:03 JST`
- Snapshot: `20260725192903`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725164739.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Complete／Accepted
Phase 1-H                                : Complete／Accepted
Mac Web User Test                        : Passed with Follow-up Findings
Top-level Phase 1 User Acceptance        : Not Yet Declared
Phase 1-F Lightning Native               : Pending
Lightning Pure CPU Runtime               : Follow-up Reserved
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Markdown Presentation                    : Phase 4 Candidate
Message Copy                             : Follow-up Candidate
Thinking UI State                        : Follow-up Required
Public Roadmap                           : Updated／Current
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-ex Docs Policy、Public Documentation Corpus、Project Documentation Explainer、Full RAG境界およびLLM動作検証／評価設計は、[documentation_index_20260725164739.md](../history/documentation_index_20260725164739.md)から継承する。

本Snapshotは、2026-07-25 Mac Web User Test、Thinking Visibility Root Cause、Markdown／Copy／Shortcut Follow-up、およびLightning Pure CPU Runtime要件を追加したことを記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 4. Detailed Review

[designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)

## 5. Mac Web User Test

```text
Visual Composition                    : PASS
Ephemeral Multi-turn                 : PASS
New Chat／Browser Memory Reset       : PASS
Model Reload Separation              : PASS
Send Button                          : PASS
Stop Button                          : PASS
Ctrl+Enter Send                      : PASS
Token Limit Behavior                 : PASS
UI Language Switch                   : PASS
Response Language Switch             : PASS
Summary Mode                         : PASS
Thinking Presentation               : UX FOLLOW-UP
Markdown Presentation                : NOT IMPLEMENTED
User／Assistant Copy                 : NOT IMPLEMENTED
```

Visual Evidenceとして、2026-07-25 19:12のMac Screenshot 2件を視認した。Screenshot自体はRepository Artifactではなく、Absolute Local Pathは記録しない。

## 6. Screen Composition Assessment

Phase 1 Previewとして想定どおりである。

- Branding／Runtime Identity
- UI Language
- New Chat
- Preview Notice
- Message Timeline
- Composer
- Stop／Send
- Response Language
- Max New Tokens
- Thinking Visibility
- Summary Mode

History、Account、Full Settings、Governance Status等は後続Phaseの責務であり、Phase 1不足とは扱わない。

## 7. Thinking Visibility Root Cause

Current Default：

```text
Thinking Generation : disabled
Presentation        : visible when Checkbox is ON
Generated Think     : none
Displayed Think     : none
```

Web UIは`thinking_visibility`だけを送信し、`thinking_mode`を変更しない。表示対象が生成されないため、CheckboxをONにしても何も出ない。

Core Failureとは断定しないが、UI上は誤解しやすいため、GenerationとVisibilityの分離状態を明示するFollow-upが必要である。

## 8. UI Follow-up

### Shortcut Hint

Current実装は`Cmd+Enter`／`Ctrl+Enter`送信へ対応している。Composer付近へ実際のShortcutを表示する。

### Markdown

Current Plain Text表示は`innerHTML`を禁止し、`textContent`を使うPhase 1の安全側実装である。

Markdown化にはSanitizer、危険URL拒否、Raw HTML無効化、Streaming中の不完全構文処理およびCanonical Content分離を必要とする。Default配置はPhase 4候補とする。

### Copy

User／Assistant MessageへCopy Buttonを追加する。Canonical ContentをCopyし、Hidden Thinking、Metadata、非表示Original Summaryを混入させない。

## 9. Lightning Pure CPU

既存CPU Profileは`compute_kind_key = "cpu"`かつ`gpu_layers = 0`だが、`build_variant_key = "cuda"`である。

Freshな最小CPU環境向けに、GPU、NVIDIA Driver、CUDA Toolkitおよび`nvcc`を要求しないPure CPU Profile／Build／Setup／Acceptanceを分離する。

候補：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

## 10. Priority

```text
P0 : Thinking Generation／Visibility UI整合
P1 : Shortcut Hint／Message Copy／Lightning Pure CPU
P2 : Sanitized Markdown Presentation
```

## 11. Scoped Authorization

本更新はReview、要件予約、Roadmap更新および最新Index作成だけを対象とする。

次を自動許可しない。

- UI／Thinking／Copy／Markdown実装
- Pure CPU Profile／Script実装
- Dependency Installation
- Model Download
- 外部環境操作
- Phase 1完了宣言
- Git／GitHub操作

## 12. Next Gate

```text
Mac Web Test Reviewed
  → Follow-up Scope Decision
  → Required Follow-up Implementation／Review
  → Mac Final User Acceptance
  → External CPU Native Validation when Available
  → Phase 1 Completion Decision
  → Backup
  → Phase 1-ex
```

## 13. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 64: docs/documentation_index_20260725192903.md -->

---

<!-- SOURCE_BEGIN 65: docs/documentation_index_20260725200001.md -->

### Source 65: `docs/documentation_index_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725200001.md`
- Source SHA-512: `d043bde195396c716d0bdd040e079e77d02c902aa3eec68ded372ec53245a7caa55675a4d4999f5d9e7cc877043fecfa67fde331e3f66f029061e22a05205097`
- Source Size: `7017` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725192903.md`

## 1. Current Position

```text
Public Author／Research Name                 : Nazuna Research
Phase 1-G                                    : Complete／Accepted
Phase 1-H                                    : Complete／Accepted
Mac Web User Acceptance                      : Passed with Follow-up Items
Phase 1-I Web Presentation／UX Follow-up      : Accepted／Ready for Implementation
Combined Manual Edge Tests                   : Deferred until Phase 1-I Review
Phase 1-F Lightning Repository／Preflight     : Accepted
Phase 1-F Lightning Pure CPU Repository Hook : Accepted／Ready for Implementation
Phase 1-F Lightning Native                   : Pending
Top-level Phase 1 Completion                 : Not Declared
Phase 1-ex                                   : Accepted Reservation／Not Started
Project Documentation Explainer／Simple RAG  : After Phase 1-ex
Mac Simple RAG                               : Optional Local Implementation
Lightning Simple RAG                         : Hook Only／Default OFF
Public Roadmap                               : Updated／Current
Docs Writer until Phase 1-ex Complete        : Current Designer Task Only
Initial GitHub Publication                   : Deferred until Phase 1-ex Completion
Git                                          : Not Initialized
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725192903.md](../history/documentation_index_20260725192903.md)を継承し、次を正式な設計状態として追加する。

- Phase 1-I Web Presentation and UX Follow-up
- Thinking GenerationとThinking VisibilityのWeb上の分離
- Reasoning／Final SSE Channel
- Shortcut HintとIME Guard
- Canonical Message Copy
- Completion後のSanitized Markdown
- Phase 1-I Review後のManual Edge Test一括実施
- Lightning Linux x86_64 Pure CPU Repository Hook
- Mac LocalとLightningで異なるSimple RAG Activation Policy

## 3. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 4. Source Review

[designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)

## 5. Phase 1-I Requirements／Architecture／ADR

- [phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md](../history/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md)
- [phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md](../history/architecture/phase_1i_web_presentation_and_ux_follow_up_architecture_20260725200001.md)
- [adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md](../history/adr/adr_0021_phase_1i_thinking_aware_safe_web_presentation_20260725200001.md)

## 6. Phase 1-I Implementer Handoff

[designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1i_web_presentation_and_ux_follow_up_20260725200001.md)

実装Scope：

```text
Thinking Generation／Visibility UI
Reasoning／Final SSE Channel
Localized Shortcut Hint
IME Composition Guard
User／Assistant Canonical Copy
Streaming Plain Text
Completion後Sanitized Markdown
Security／Regression Test
```

Manual Edge Testは実装担当の自動Testで代替しない。実装報告と設計Review後、ユーザーが次をまとめて確認する。

- 生成中New Chat
- Summary中Stop
- Browser Reload
- 別Tab Busy
- Token Boundary
- Thinking 4組合せ
- Markdown Sanitization／Fallback
- Copy対象
- Shortcut Hint

## 7. Lightning Pure CPU Requirements／Architecture／ADR

- [phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md](../history/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md)
- [phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md](../history/architecture/phase_1f_lightning_pure_cpu_runtime_follow_up_architecture_20260725200001.md)
- [adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md](../history/adr/adr_0022_lightning_pure_cpu_and_optional_component_hook_only_profile_20260725200001.md)

## 8. Lightning Pure CPU Implementer Handoff

[designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_runtime_follow_up_20260725200001.md)

Repository Scope：

```text
Pure CPU Deployment Profile
Pure CPU llama.cpp Build Contract
CPU Setup／Preflight Hook
Verification Target
Static／Unit／Integration Test
External Native Test Pending State
```

既存のCUDA BuildをCPUで実行するProfileは削除・改名せず、Pure CPU Build Profileと意味を分けて併存させる。

## 9. Simple RAG Placement

Simple RAG／Project Documentation ExplainerはPhase 1-IまたはPure CPU Handoffの実装対象ではない。

Phase 1-exで公開正本CorpusとManifestを整えた後、別Handoffで扱う。

```text
Mac Local:
  Optional implementation
  Explicit ON only
  Corpus／Retriever／Context Injectionを接続可能

Lightning:
  Hook only
  Default OFF
  Provider absent allowed
  No index load
  No retrieval
  No additional model call
```

この差はApplication Coreの分岐Hard-codeではなく、同じComponent Port、CapabilityおよびDeployment Profileで表現する。

## 10. Scoped Authorization

ユーザーの指示により、次のRepository実装へ着手可能である。

1. Phase 1-I Web Presentation and UX Follow-up
2. Phase 1-F Lightning Pure CPU Runtime Follow-up

両Scopeは別々に実装・報告・Reviewする。単一Statusへ混在させない。

次は自動許可しない。

- 外部Lightning Studio操作
- Upload／公開URL操作
- Dependencyの外部環境Install
- Model Download
- Simple RAG実装
- Phase 1-ex開始
- Phase 1完了宣言
- Backup
- Git／GitHub操作

## 11. Recommended Execution Order

```text
Phase 1-I Implementation
  → Implementer Status
  → Designer Review
  → Lightning Pure CPU Repository Follow-up
  → Implementer Status
  → Designer Review
  → Combined Mac Manual Edge Test
  → External Native Validation when available
  → Phase 1 Completion Decision
  → Backup
  → Phase 1-ex
  → Public Canonical Corpus
  → Mac Simple RAG／Lightning Hook-only Handoff
```

Phase 1-IとPure CPU Repository Follow-upの実装順を変更する場合も、変更範囲、TestおよびStatus Reportは分離する。

## 12. Next Required Reports

```text
docs/handoffs/implementer_status_phase_1i_*_YYYYMMDDHHMMSS.md
docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_YYYYMMDDHHMMSS.md
```

## 13. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 65: docs/documentation_index_20260725200001.md -->

---

<!-- SOURCE_BEGIN 66: docs/documentation_index_20260725201016.md -->

### Source 66: `docs/documentation_index_20260725201016.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725201016.md`
- Source SHA-512: `2b0094b59da351046317ac98a3f41bc3a33e1b0e09af011b6a8bffc4f5a70adda0613a3346591dfb4c80702b8929a98b2392d77e4645e6d29dd4c9c06039b38e`
- Source Size: `4387` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725200001.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up      : Accepted／Ready for Implementation
Combined Manual Edge Tests                   : Deferred until Phase 1-I Review
Phase 1-F Lightning Pure CPU Repository Hook : Accepted／Ready for Implementation
Lightning Pure CPU Preflight Addendum        : Accepted／Ready for Implementation
Lightning Environment Reconstruction         : User-run／External Gate
Simple RAG Implementation                    : After Phase 1-ex
Simple RAG Missing docs/ Contract             : Accepted Reservation
Mac Simple RAG                               : Optional Local Implementation
Lightning Simple RAG                         : Hook Only／Default OFF
Top-level Phase 1 Completion                 : Not Declared
Phase 1-ex                                   : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725200001.md](../history/documentation_index_20260725200001.md)を継承し、次を追加する。

- Mac／Lightning共通のSimple RAG `docs/` Availability Contract
- `docs/`不存在時の明示的Unavailable Result
- Lightning Pure CPU Preflightの既存Script拡張方針
- Lightning環境再構築をユーザー実行とする運用境界

## 3. Simple RAG Availability Requirements

[simple_rag_documentation_availability_requirements_20260725201016.md](../history/requirements/simple_rag_documentation_availability_requirements_20260725201016.md)

## 4. Accepted ADR

[adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md](../history/adr/adr_0023_simple_rag_missing_docs_explicit_unavailable_result_20260725201016.md)

## 5. Future Implementer Reservation

[designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md](../history/handoffs/designer_handoff_simple_rag_documentation_availability_reservation_20260725201016.md)

本HandoffはPhase 1-ex完了後用であり、現時点のRAG実装を許可しない。

共通Contract：

```text
Component OFF:
  docs/を探索しない。
  Startup Errorにしない。

Component ON／明示利用＋docs/ missing:
  state=unavailable
  reason_code=docs_directory_missing
  docs/が設置されていないため参照できません。
  index loadなし
  retrievalなし
  additional model callなし
```

## 6. Lightning Pure CPU Preflight Addendum

[designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md](../history/handoffs/designer_handoff_phase_1f_lightning_pure_cpu_preflight_addendum_20260725201016.md)

実装担当は既存の`preflight_lightning_ai_studio.sh`を優先的に拡張する。

```text
cuda-gpu  : CUDA Build／GPU Execution
cuda-cpu  : CUDA Build／CPU Execution
cpu-native: Pure CPU Build／CPU Execution
```

既存`--cpu-only`の意味をPure CPUへ変更しない。CPU-native経路では`nvidia-smi`、`nvcc`、CUDA CompilerまたはGPU Allocation Probeを呼び出さない。

## 7. User／Implementer Boundary

### 実装担当

- Preflight Repository実装
- Pure CPU Setup Script
- Profile
- Automated Test
- User-run Command Procedure
- Status Report

### ユーザー

- Lightning Environment Reconstruction
- Project／Model配置
- Setup Command実行
- Native Smoke
- Public Access確認

外部操作の結果をRepository TestだけでPassとみなさない。

## 8. Scoped Authorization

現在実装可能：

- Phase 1-I
- Lightning Pure CPU Repository Follow-up
- Lightning Pure CPU Preflight Addendum

現在実装不可：

- Simple RAG
- Project Documentation Explainer
- 外部Lightning操作
- Model Download
- Phase 1-ex開始
- Git／GitHub操作

## 9. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 10. Next Reports

```text
docs/handoffs/implementer_status_phase_1i_*_YYYYMMDDHHMMSS.md
docs/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_YYYYMMDDHHMMSS.md
```

Pure CPU StatusにはPreflight Addendumの結果も含める。

## 11. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 66: docs/documentation_index_20260725201016.md -->

---

<!-- SOURCE_BEGIN 67: docs/documentation_index_20260725212559.md -->

### Source 67: `docs/documentation_index_20260725212559.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725212559.md`
- Source SHA-512: `84e0e931aa327517d3ec2804e14aa61bf728b843d767c64a7bb8cea0fda320eb9a26941999627810d4cf7f0b19f4ec3e695ec19949fd01556d34e553a3f4c03b`
- Source Size: `5456` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 21:25:59 JST`
- 更新日時: `2026-07-25 21:25:59 JST`
- Snapshot: `20260725212559`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725201016.md`

## 1. Current Position

```text
Phase 1-G Minimal Web Surface                  : Complete／Accepted
Phase 1-H Summary Mode／UI Language            : Complete／Accepted
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Combined Manual Edge Tests                     : Passed
Phase 1-F Pure CPU Profile／Preflight／Setup    : Implemented
Phase 1-F Pure CPU Native Acceptance Contract  : Changes Requested
Phase 1-F Pure CPU External Native Validation  : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725201016.md](../history/documentation_index_20260725201016.md)を継承し、次を追加する。

- Phase 1-I Repository Review
- Mac Web Manual Acceptance結果
- Phase 1-I Accepted
- Phase 4 Markdown／Code Snippet／Busy UX予約
- Pure CPU Repository Review
- Pure CPU Native Acceptance Correction Handoff

## 3. Implementer Status

- [implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md](../history/handoffs/implementer_status_phase_1i_web_presentation_and_ux_follow_up_20260725203508.md)
- [implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md](../history/handoffs/implementer_status_phase_1f_pure_cpu_runtime_follow_up_20260725203508.md)

## 4. Phase 1-I Review

[designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md](../history/handoffs/designer_review_phase_1i_repository_and_mac_manual_acceptance_20260725212559.md)

判定：

```text
Repository Implementation : ACCEPTED
Mac Manual Acceptance     : ACCEPTED
Security Boundary         : ACCEPTED
Phase 1-I                 : COMPLETE／ACCEPTED
```

Manual PASS：

- User／Assistant Copy
- UI／Response Language
- Summary
- New Chat Context Reset
- New Chat during Generation
- Stop during Summary
- Reload
- Multi-tab Busy
- Thinking Dependency
- Thinking／Final Separation
- Completion Markdown

## 5. Phase 1-I Deferred Presentation

Phase 4へ延期する。

- Streaming中の段階的Markdown
- Markdown Table
- Code Snippet Language Label
- Assistant本文／Code Block分離
- Code Block個別Copy
- Syntax Highlight候補
- Busy具体Message／汎用Statusの二重表示整理

Current Streaming Plain Text／Completion Markdownは設計どおりであり、Phase 1-I Failureではない。

## 6. Pure CPU Review

[designer_review_phase_1f_pure_cpu_repository_20260725212559.md](../history/handoffs/designer_review_phase_1f_pure_cpu_repository_20260725212559.md)

判定：

```text
Profile／Preflight／Setup Direction : ACCEPTED
Native Acceptance Contract         : CHANGES REQUESTED
External Native Acceptance         : PENDING
Overall Pure CPU Follow-up          : NOT YET ACCEPTED
```

## 7. Pure CPU Blocking Finding

新Pure CPU ProfileとRuntimeは次を使う。

```text
acceleration_api = none
```

Native Acceptance ScriptのCPU Branchは次を固定している。

```text
acceleration_api = cpu_native
```

正しいPure CPU Runtimeでも`runtime_evidence_matches_profile`がFalseになるため、LightningへUpload／再構築する前に修正する。

また、Setupの`--model-path`は実際にはExpected Model Root Layoutを前提とするため、Option Contractを明確化する。

## 8. Correction Handoff

[designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md](../history/handoffs/designer_handoff_phase_1f_pure_cpu_acceptance_correction_20260725212559.md)

次の実装者Statusを要求する。

```text
docs/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_YYYYMMDDHHMMSS.md
```

## 9. Independent Verification

```text
pytest                         : 265 passed, 3 deselected
Phase 1-I／Pure CPU Targeted   : 30 passed, 1 deselected
Ruff Check                     : PASS
Ruff Format                    : PASS
Mypy                           : PASS
Node Safe Markdown             : 5 passed
Shell Syntax                   : PASS
uv lock --check                : PASS／122 packages
```

Mac Model Smokeを追加実行した時点では、既存Web Runtimeが同じQwen ModelをMemory Mapしており、二重Context作成が失敗した。ユーザーのWeb実生成は合格しているため回帰とは断定せず、Phase 1 Final GateでWeb Runtime停止後に再実行する。

## 10. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 11. Next Gate

```text
Pure CPU Acceptance Correction
  → Implementer Status
  → Designer Review
  → User-run Lightning Rebuild／Native Test
  → Cross-environment Final Review
  → Phase 1 Completion Decision
  → Backup
  → Phase 1-ex
```

## 12. Scoped Authorization

Correction Handoffに記載したRepository修正へ着手可能である。

次は自動許可しない。

- 外部Lightning操作
- Model Download
- Git／GitHub
- Phase 1 Completion宣言
- Backup
- Phase 1-ex開始
- Simple RAG実装

## 13. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 67: docs/documentation_index_20260725212559.md -->

---

<!-- SOURCE_BEGIN 68: docs/documentation_index_20260725214428.md -->

### Source 68: `docs/documentation_index_20260725214428.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725214428.md`
- Source SHA-512: `841fe3a8eee0a32b7514b0fee73408c8e0876b0c6108ea0ae2f1df748bb530a6353c7e26548234d837d6596c3f4951ae2f41ec7afaefbc0d7018691aae46157d`
- Source Size: `3255` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 21:44:28 JST`
- 更新日時: `2026-07-25 21:44:28 JST`
- Snapshot: `20260725214428`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725212559.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Pure CPU Repository Follow-up        : Complete／Accepted
Phase 1-F Pure CPU External Native Acceptance  : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725212559.md](../history/documentation_index_20260725212559.md)を継承する。

前SnapshotのPure CPU Changes RequestedはCorrection実装と独立再Reviewにより解消された。

## 3. Correction Status

[implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md](../history/handoffs/implementer_status_phase_1f_pure_cpu_acceptance_correction_20260725214037.md)

## 4. Accepted Re-review

[designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](../history/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)

判定：

```text
Pure CPU Profile／Runtime Detection : ACCEPTED
Pure CPU Preflight／Setup           : ACCEPTED
Acceptance Contract Correction      : ACCEPTED
Repository Follow-up                : COMPLETE／ACCEPTED
External Native Acceptance          : PENDING
```

## 5. Resolved Findings

### Acceleration

```text
CUDA GPU                 : cuda
CUDA Build CPU Execution : cpu_native
Pure CPU Build           : none
Mismatch                  : Fail Closed
```

Runtime値を選択Profileの`compute.acceleration_api_key`と照合する。

### Model Selection

```text
Canonical : --model-root
Artifact  : Registry Relative Path
Compat    : --model-path Validation
Download  : none
```

指定Artifactと実際にLoadするArtifactを一致させる。

## 6. Independent Verification

```text
pytest Full Suite : 267 passed, 3 deselected
Pure CPU Targeted : 9 passed, 1 deselected
Ruff              : PASS
Mypy              : PASS
Node Markdown     : 5 passed
Shell Syntax      : PASS
uv lock           : PASS／122 packages
Read-only Plan    : PASS
```

External Native Testは未実施であり、Passとは記録しない。

## 7. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 8. Next Gate

```text
User-run Lightning Read-only Preflight
  → Setup Plan
  → Environment Reconstruction
  → Environment Verification
  → Bounded Native Smoke
  → Result Review
  → Cross-environment Final Review
  → Phase 1 Completion Decision
```

## 9. Scoped Authorization

Repository Correctionは完了した。次の外部Lightning操作はユーザー実行Gateである。

本Indexは外部操作、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 10. Append-Only

旧IndexとTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 68: docs/documentation_index_20260725214428.md -->

---

<!-- SOURCE_BEGIN 69: docs/documentation_index_20260725215627.md -->

### Source 69: `docs/documentation_index_20260725215627.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260725215627.md`
- Source SHA-512: `08b2ce1e016d8a37df3a908fd8ac2dfd52960de2574563196a85da5e5ffbba0f79eae4ef6e33a87e181c56b18d00dca437a9c69824f50903d93d62ba9c7c475a`
- Source Size: `4157` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 21:56:27 JST`
- 更新日時: `2026-07-25 21:56:27 JST`
- Snapshot: `20260725215627`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725214428.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Pure CPU Repository Follow-up        : Complete／Accepted
Phase 1-F Pure CPU External Native Acceptance  : Pending
Lightning CPU Upload／Reconstruction Manual    : Current
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725214428.md](../history/documentation_index_20260725214428.md)を継承する。

前Snapshot以降の実装変更、外部操作または受入結果はない。本Snapshotでは、Lightning Pure CPU環境へ一括UploadするためのPath配置、Upload対象、除外対象、Preflight、Environment再構築、Native SmokeおよびWeb起動を統合したUser Manualを追加する。

## 3. Current Lightning Pure CPU Manual

[lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md](../history/user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md)

このManualを、次のユーザー実行GateのCurrent手順とする。

```text
Clean Upload Staging
  → Lightning Project／Model分離配置
  → uv 0.11.29隔離配置
  → Pure CPU Read-only Preflight
  → Setup Plan
  → Environment Reconstruction
  → Environment Verification
  → Bounded Native Smoke
  → Web Preview Smoke
  → Result Status
  → External Native Review
```

## 4. Confirmed Script Paths

```text
Preflight:
  scripts/setup/preflight_lightning_ai_studio.sh

Pure CPU Setup:
  scripts/setup/setup_lightning_linux_x86_64_cpu.sh

Environment Verification:
  scripts/setup/verify_phase1_environment.py

Bounded Native Acceptance:
  scripts/models/phase1f_cross_environment_acceptance.py

Pure CPU Profile:
  config/profiles/lightning_linux_x86_64_cpu_native.toml
```

Pure CPU Preflightでは、既定Targetに依存せず次を明示する。

```text
--runtime-target cpu-native
```

## 5. Upload Boundary

```text
Required:
  src/
  config/
  scripts/
  pyproject.toml
  uv.lock

Recommended:
  tests/
  .gitignore

Excluded:
  .venv/
  models／GGUF
  docs/
  .python-version
  .git/
  macOS Metadata
  Python／Test／Lint／Type Cache
  Native Build Artifact
  Local Runtime Data
  Secret／Environment File
  Log／Backup Zip
```

開発元から直接削除せず、Clean Staging Copyを作成する。

## 6. Environment Contract

```text
OS            : Ubuntu
Architecture  : x86_64
Container     : Required
Python        : 3.12.11
uv            : 0.11.29／Isolated
Backend       : llama-cpp-python 0.3.34／Pure CPU
GPU           : Not Required
CUDA／nvcc    : Not Probed
Acceleration  : none
Fallback      : deny
```

## 7. Previous Accepted Review

[designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](../history/handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)

Repository側のPure CPU Detection、Model Root Contract、Setup、Acceptance CorrectionはAcceptedである。

## 8. External Gate

本Snapshotでは次を実施していない。

- Lightning Upload
- uv Install
- Dependency Install
- Environment変更
- Native Build
- Model配置
- Model Load
- Generation
- Port公開

External Native AcceptanceはPendingのまま保持する。

## 9. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 10. Scoped Authorization

本Manualはユーザー実行手順を定義する。外部Lightning操作、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 11. Append-Only

旧Index、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。


<!-- SOURCE_END 69: docs/documentation_index_20260725215627.md -->

---

<!-- SOURCE_BEGIN 70: docs/documentation_index_20260726092413.md -->

### Source 70: `docs/documentation_index_20260726092413.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726092413.md`
- Source SHA-512: `f916ceb2818e5d94aeb964ac5d68674805dc25b07596da5751ca06088c9d65242cbfc63428dff4b5f9b243f98f92539a6d63745786bea4bc1d0d6a2b10a2a7db`
- Source Size: `4855` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725215627.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Pure CPU Repository Follow-up        : Complete／Accepted
Phase 1-F Lightning External Pure CPU Runtime  : Accepted
Cross-platform Full Repository Suite           : Test-only Follow-up Pending
Lightning Web Preview Acceptance               : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725215627.md](../history/documentation_index_20260725215627.md)を継承する。

前Snapshot以降、ユーザーがLightning AI Studio Pure CPU Environmentを実際に再構築し、Environment Verification、Static CheckおよびBounded Native Acceptanceを実行した。

事前想定から変更されたEnvironment経路、Model配置、Upload Artifact、File Mode、Native BuildおよびTest IsolationをCurrent Manualへ統合した。

## 3. Current Lightning Manual

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

主な確定事項：

```text
Project Root     : /teamspace/studios/this_studio/margpa-runtime-llm
Model Root       : /teamspace/studios/this_studio/models
Model Link       : margpa-runtime-llm/models -> ../models
Python           : 3.12.11
uv               : 0.11.29／Project-isolated
Environment Mode : project-venv
Environment      : margpa-runtime-llm/.venv
Backend          : llama-cpp-python 0.3.34／Pure CPU
```

## 4. External Runtime Review

[designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)

判定：

```text
Environment Verification   : PASS
External Pure CPU Runtime  : ACCEPTED
Native Acceptance          : PASS
Required Checks            : ALL TRUE
Static Verification        : PASS
Full Suite                 : 264 PASS／2 TEST ISOLATION FAIL
```

## 5. Test-only Follow-up

[designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](../history/handoffs/designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)

実装対象：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

目的：

- MockしたNative Platform Testを実Container Markerから分離する。
- Temporary Model Path Testを外部`MARGPA_MODEL_ROOT`から分離する。
- ユーザーによる手動Environment UnsetなしでFull SuiteをGreenにする。

## 6. Corrected Upload Boundary

Runtime必須：

```text
config/
scripts/
src/
pyproject.toml
uv.lock
```

Full Repository Testにも必要：

```text
tests/
.python-version
Shell Script Execute Bit
```

Model、Local `.venv`、Docs、Cacheおよび生成物はProject Upload Bundleから分離する。

## 7. Environment Route Correction

非採用：

```text
auto
  → studio-active
  → Lightning Active Conda Prefix
  → uv Project Environment Compatibility Error
```

Current：

```text
project-venv
  → Lightning Python 3.12.11
  → margpa-runtime-llm/.venv
  → Pure CPU Native Build
```

## 8. Verification Evidence

```text
Ruff Check  : PASS
Ruff Format : PASS／95 files
Mypy        : PASS／95 source files
pytest      : 264 passed／2 failed／1 skipped／3 deselected
Acceptance  : all_required_checks_passed=true
Profile     : external.lightning-linux-x86_64.cpu-native
```

2 FailureはProduction RuntimeではなくTest Isolationである。

## 9. Next Gate

```text
Test-only Follow-up Implementation
  → Mac Full Suite
  → Lightning Full Suite
  → Full Suite Green Review
  → Lightning Web Preview Acceptance
  → Top-level Phase 1 Completion Decision
```

Test-only修正後、Production Artifactを変更しない限りBounded Native Acceptanceを再実行しない。

## 10. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 11. Authorization Boundary

本SnapshotはTest-only Follow-up Handoffを許可する。

外部Lightning操作、Production Code変更、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 12. Append-Only

旧Index、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。


<!-- SOURCE_END 70: docs/documentation_index_20260726092413.md -->

---

<!-- SOURCE_BEGIN 71: docs/documentation_index_20260726093437.md -->

### Source 71: `docs/documentation_index_20260726093437.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726093437.md`
- Source SHA-512: `4f79fe4772a14a074ab37385c99405fafb314b495e8db2d5355eed0bf7996d8baca209706c46b45cb6114219f2a6d562acd65e54c60a39940db96fff26b31e79`
- Source Size: `4083` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 09:34:37 JST`
- 更新日時: `2026-07-26 09:34:37 JST`
- Snapshot: `20260726093437`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726092413.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Lightning External Pure CPU Runtime  : Accepted
Repository Test Isolation Follow-up            : Accepted
Mac Full Repository Suite                      : Green
Lightning Full Repository Suite                : Revalidation Pending
Lightning Web Preview Acceptance               : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726092413.md](../history/documentation_index_20260726092413.md)を継承する。

前SnapshotのTest-only Handoffに基づき、Platform Execution Environment IsolationとModel Root Subprocess Environment Isolationが実装された。

設計者役がMac Repositoryで独立ReviewおよびVerificationを行い、Repository変更をAcceptedとした。

## 3. Accepted Review

[designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md](../history/handoffs/designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md)

判定：

```text
Repository Test-only Change : ACCEPTED
Targeted Test               : 41 passed
Mac Full Suite              : 267 passed／3 deselected
Ruff                        : PASS
Ruff Format                 : PASS／95 files
Mypy                        : PASS／95 source files
Production Change           : NONE
```

## 4. Implemented Isolation

### Platform

Mock Native Platform Testへ次を明示した。

```text
raw_execution_environment=native
```

実Lightning Container MarkerからTestを分離する。

### Model Root

Temporary Model Root TestのSubprocessから次を除外した。

```text
MARGPA_MODEL_ROOT
MARGPA_PROFILE
```

ユーザーShellのApplication設定からTestを分離する。

## 5. Current Lightning Manual

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 6. External Runtime Review

[designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](../history/handoffs/designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)

External Pure CPU Runtime Accepted判定を維持する。

## 7. Lightning Revalidation

Lightningへ反映するFile：

```text
tests/unit/inference/test_deployment_platform.py
tests/unit/inference/test_lightning_cpu_native_setup.py
```

実行：

```text
Targeted Test
  → 41 passed expected

Full Suite
  → 266 passed
  → 1 skipped
  → 3 deselected
  → 0 failed
```

手動Environment UnsetなしでPassすることを確認する。

## 8. Native Acceptance

Production Artifact変更なし。

前回の：

```text
all_required_checks_passed=true
```

を有効なEvidenceとして維持し、Native Acceptance再実行を要求しない。

## 9. Next Gate

```text
Lightning Test 2File反映
  → Lightning Targeted Test
  → Lightning Full Suite
  → Full Suite Green Review
  → Lightning Web Preview Acceptance
  → Top-level Phase 1 Completion Decision
```

## 10. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 11. Authorization Boundary

本SnapshotはLightningへのTest 2File反映とRead-only Test実行手順を示す。

外部操作はユーザー実行Gateである。Production Code変更、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 12. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。


<!-- SOURCE_END 71: docs/documentation_index_20260726093437.md -->

---

<!-- SOURCE_BEGIN 72: docs/documentation_index_20260726094241.md -->

### Source 72: `docs/documentation_index_20260726094241.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726094241.md`
- Source SHA-512: `1cdda1b1cd7b4609a325898f5dcf701c0a2c1bdbfb1c617556ab6146af06fd0083152249ad80c2901bffabe5c9a8397674babd6a87e43e7a6b36519b10c99597`
- Source Size: `2795` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 09:42:41 JST`
- 更新日時: `2026-07-26 09:42:41 JST`
- Snapshot: `20260726094241`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726093437.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Lightning External Pure CPU Runtime  : Accepted
Repository Test Isolation Follow-up            : Accepted
Mac Full Repository Suite                      : Green
Lightning Full Repository Suite                : Green
Lightning Web Preview Acceptance               : Pending
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726093437.md](../history/documentation_index_20260726093437.md)を継承する。

ユーザーがLightningへTest-only変更を反映し、Targeted TestおよびFull Suiteを再実行した。Cross-platform Full Suite Greenを確認した。

## 3. Accepted Revalidation

[designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md](../history/handoffs/designer_review_phase_1f_lightning_full_suite_revalidation_20260726094241.md)

```text
Targeted Test : 41 passed
Full Suite    : 266 passed／1 skipped／3 deselected
Failure       : 0
```

## 4. Current Runtime State

```text
Environment Verification   : PASS
External Pure CPU Runtime  : ACCEPTED
Native Acceptance          : PASS
Required Checks            : ALL TRUE
Mac Full Suite             : GREEN
Lightning Full Suite       : GREEN
```

## 5. Current Manual

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 6. Next Gate

```text
Lightning Web Preview起動
  → Health Check
  → Basic認証境界
  → Port公開
  → Browser手動確認
  → Shutdown
  → Lightning Web Acceptance Review
```

## 7. Native Acceptance

Test-only変更のため再実行を要求しない。前回の`all_required_checks_passed=true`を有効なEvidenceとして維持する。

## 8. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 9. Authorization Boundary

次のユーザー実行GateはLightning Web Previewの起動・手動確認である。

Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 10. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。


<!-- SOURCE_END 72: docs/documentation_index_20260726094241.md -->

---

<!-- SOURCE_BEGIN 73: docs/documentation_index_20260726111632.md -->

### Source 73: `docs/documentation_index_20260726111632.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726111632.md`
- Source SHA-512: `ab9bfcc41db7590528912ade70513d16cdc38fd0ad042b29bf828ea4c3e90e63119a761ab2eb48008c5849d7b5ae6b5dd5ee7c7e70b0d84c1bd41644b48e00ec`
- Source Size: `4116` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726094241.md`

## 1. Current Position

```text
Phase 1-A～1-I                              : Complete／Accepted
Mac Web Manual Acceptance                  : Passed
Phase 1-F Lightning External Pure CPU      : Accepted
Mac Full Repository Suite                  : Green
Lightning Full Repository Suite            : Green
Lightning External Web Acceptance          : Passed
Top-level Phase 1                          : Complete／Accepted
Phase 1 Backup Trigger                     : Ready／Not Executed
Phase 1-ex                                 : Next／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726094241.md](../history/documentation_index_20260726094241.md)を継承する。

ユーザーがLightning Public Linkを、Lightning Accountと無関係なBrowserおよびSafariから確認した。Basic認証、Generation、Stop、New Chat、Language、Summary、Thinking、Copy、Model Busy、Browser Reload、Token打切りおよびServer停止を含むManual Acceptanceが合格した。

## 3. Phase 1 Final Review

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

```text
Blocking Finding            : None
Lightning Web Acceptance    : Passed
Top-level Phase 1           : Complete／Accepted
Next Phase                  : Phase 1-ex
```

## 4. Current User Manual

[phase_1_web_and_lightning_user_manual_20260726111632.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)

Lightning環境をゼロから再構築する場合：

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 5. Accepted Runtime Evidence

```text
Mac Full Suite             : 267 passed／3 deselected
Lightning Targeted Test    : 41 passed
Lightning Full Suite       : 266 passed／1 skipped／3 deselected
Lightning Native Acceptance: all_required_checks_passed=true
Mac Web                    : PASS
Lightning External Web     : PASS
```

## 6. Accepted Deferred Items

- Lightning Pure CPUの生成Latency
- iPhone／iOS／Mobile Responsive UI
- Streaming中のRaw Markdown
- Markdown Table
- Code Block個別Copy
- Model Busy表示の重複

これらは理解済みの非Blocking項目である。

## 7. Phase 1-ex Reservation

### 7.1 Complete Operating Model

[phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)

### 7.2 Lightning Auto-start／Cost Control

[phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md](../history/requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md)

Auto-startはPhase 1 CompletionをBlockしないOperations Follow-upである。

## 8. Backup Gate

Phase完了Policyの両Gateが成立したため、Phase 1 Backup TriggerはReadyである。

```text
Gate A: Designer Phase完了／次Phase着手可能宣言 : PASS
Gate B: User Manual Acceptance合格宣言           : PASS
```

Backupは未実行である。初回GitHub公開はPhase 1-ex完了後まで延期する。

## 9. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 10. Authorization Boundary

本Indexは次を自動許可しない。

- Backup生成
- Git初期化、Commit、Tag、Remote、Push
- GitHub公開
- Phase 1-exの実変更
- Lightning Auto-start設定
- Secret登録
- Machine Type変更

## 11. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

<!-- SOURCE_END 73: docs/documentation_index_20260726111632.md -->

---

<!-- SOURCE_BEGIN 74: docs/documentation_index_20260726120229.md -->

### Source 74: `docs/documentation_index_20260726120229.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726120229.md`
- Source SHA-512: `2f1ec17ad628b0a4e1d6883af74d60db08589ddc890d7fd5f73539e8d96f7664d3e900378e19c558417466c7f1df0fc15724dbbdce1f2b8c5fb1ff17966d8cd5`
- Source Size: `4529` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_pre_phase_1_backup`
- 作成日時: `2026-07-26 12:02:29 JST`
- 更新日時: `2026-07-26 12:02:29 JST`
- Snapshot: `20260726120229`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726111632.md`

## 1. Current Position

```text
Phase 1-A～1-I                              : Complete／Accepted
Mac Web Manual Acceptance                  : Passed
Lightning Pure CPU Runtime                 : Accepted
Mac Full Repository Suite                  : Green
Lightning Full Repository Suite            : Green
Lightning External Web Acceptance          : Passed
Top-level Phase 1                          : Complete／Accepted
Phase 1 Pre-backup Documentation           : Complete
Phase 1 Backup Trigger                     : Ready／Execution Authorized
Phase 1-ex                                 : Next／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726111632.md](../history/documentation_index_20260726111632.md)を継承する。

Lightning Pure CPU環境構築の実績、Test Isolation修正、外部Web Acceptance、CPU／Mobile制約、Studio Sleep、Basic認証継続、将来Public Demo表記、Auto-start早期判定、Git準備前倒しおよびPhase 1-exの最新順序を統合した。

## 3. Phase 1 Lightning Finalization Record

[phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](../history/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)

本書を、Lightning Pure CPU環境構築開始からPhase 1確定Backup直前までの統合入口とする。

## 4. Phase 1 Final Review

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

```text
Blocking Finding            : None
Top-level Phase 1           : Complete／Accepted
Backup Gate A               : Passed
Backup Gate B               : Passed
```

## 5. Current User Manual

[phase_1_web_and_lightning_user_manual_20260726111632.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)

詳細なLightning再構築：

[lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../history/user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)

## 6. Phase 1-ex Current Requirements

親要件：

[phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)

最新開始順序／Public Demo／Git準備：

[phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](../history/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)

## 7. Current Decisions

```text
Basic Authentication       : Keep for current Preview
Personal Contact in Repo   : Prohibited
README Demo Statement      : 「将来、Public Demo方式も検討しています。」
Public Demo Implementation : Deferred
Auto-start                 : Early read-only preflight in Phase 1-ex
Git Planning／Preparation  : Before docs Lossless Compilation
Initial Public Commit      : After docs reorganization and final sanitation
Simple RAG                 : Mac only after docs structure stabilization
```

## 8. Phase 1 Backup

ユーザーが、本Indexと統合記録を作成した後にPhase 1確定Backupを取得するよう指示した。

Backupは次を満たすこと。

- Project Root外へ保存
- Allowlist方式
- `.venv`、Model／Symlink、`.git`、Cache、`.DS_Store`、Secretを除外
- File InventoryとSHA-512
- Archive SHA-512
- Detached Receipt
- Temporary Restore
- Restored Inventory／Hash検証
- 個人固有情報／Absolute Local Path／Credential Scan

## 9. Current Public Roadmap

[roadmap_ja.md](../../../../public/roadmap_ja.md)

## 10. Authorization Boundary

本Indexの後続としてPhase 1確定Backupの作成はユーザーにより許可されている。

次はまだ許可されていない。

- Phase 1-exの実変更
- Git初期化、Commit、Tag、Remote、Push
- GitHub公開
- Lightning Auto-start設定
- Docs Directory Migration
- RAG実装

## 11. Append-Only

旧Index、旧Review、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本IndexをBackup前最新Indexとする。

<!-- SOURCE_END 74: docs/documentation_index_20260726120229.md -->

---

<!-- SOURCE_BEGIN 75: docs/documentation_index_20260726121346.md -->

### Source 75: `docs/documentation_index_20260726121346.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726121346.md`
- Source SHA-512: `050da280441e85cf1e4485a5cb811a90a5725a8a952a46b687ee892f465bf85dfa9e8653a41d2696c5a43d5987943c1f782959aa076fd688b074768244c19030`
- Source Size: `2924` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_pre_phase_1_backup_sanitized`
- 作成日時: `2026-07-26 12:13:46 JST`
- 更新日時: `2026-07-26 12:13:46 JST`
- Snapshot: `20260726121346`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726120229.md`

## 1. Current Position

```text
Top-level Phase 1                          : Complete／Accepted
Phase 1 Pre-backup Documentation           : Complete
Pre-backup Privacy／Sanitation Scan        : Passed
Phase 1 Backup Trigger                     : Ready／Execution Authorized
Phase 1 Backup                             : Not Yet Created
Phase 1-ex                                 : Next／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726120229.md](../history/documentation_index_20260726120229.md)を継承する。

Backup前Privacy Scanで、過去Statusに検索Pattern説明として残っていた旧Public Handle Literalを1件検出した。Public Identity PolicyのPrivacy例外に基づき匿名化し、意味を維持した。

## 3. Pre-backup Privacy／Sanitation Scan

[pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md](../history/operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md)

```text
実個人名／Email／Path   : 0
Credential実値          : 0
Secret File             : 0
旧Public Handle          : 0 after scrub
Expected Test Fixtures  : retained
```

## 4. Phase 1 Lightning Finalization

[phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](../history/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)

## 5. Phase 1 Final Review

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

## 6. Phase 1-ex Current Requirements

[phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](../history/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)

## 7. Backup Input Snapshot

Phase 1 Backupは、本IndexをCurrent Indexとする管理対象からSanitized Candidateを作成する。

Include候補：

```text
.gitignore
.python-version
config/
docs/
pyproject.toml
scripts/
src/
tests/
uv.lock
```

Exclude：

```text
.DS_Store
.venv/
models/
models Symbolic Link
.git/
Cache
Bytecode
Coverage
Secret
Local Data
```

## 8. Authorization Boundary

Phase 1確定Backupの作成、Sanitation、HashおよびRestore検証はユーザーにより許可されている。

Phase 1-ex変更、Git／GitHub操作、Lightning変更はまだ許可されていない。

## 9. Append-Only

旧Indexおよび旧文書は履歴として保持する。本IndexをPhase 1 Backup入力SnapshotのCurrent Indexとする。

<!-- SOURCE_END 75: docs/documentation_index_20260726121346.md -->

---

<!-- SOURCE_BEGIN 76: docs/documentation_index_20260726122144.md -->

### Source 76: `docs/documentation_index_20260726122144.md`

- History Target: `docs/project/phases/phase_1/history/documentation_index_20260726122144.md`
- Source SHA-512: `95f4d6ef2f5e4722b3961e454e3dd3b61e6cd71ef7f240332198746a8e10870b753319c0ee9fab9ff51e70d3c8d128da0f61ac417c0c6f88f680bcc5bb803258`
- Source Size: `3861` bytes

# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current_phase_1_backup_complete`
- 作成日時: `2026-07-26 12:21:44 JST`
- 更新日時: `2026-07-26 12:21:44 JST`
- Snapshot: `20260726122144`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260726121346.md`

## 1. Current Position

```text
Phase 1-A～1-I                              : Complete／Accepted
Mac Web Manual Acceptance                  : Passed
Lightning Pure CPU Runtime                 : Accepted
Mac／Lightning Full Repository Suite       : Green
Lightning External Web Acceptance          : Passed
Top-level Phase 1                          : Complete／Accepted
Phase 1 Backup                             : Complete／Verified
Git／GitHub                                : Not Started
Phase 1-ex                                 : Ready／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260726121346.md](../history/documentation_index_20260726121346.md)を継承する。

Phase 1確定Backup SetをProject Root外へ保存し、Archive、Manifest、ReceiptのSHA-512、Temporary Restore、Inventory、全File Hash、PrivacyおよびSecret Scanを検証した。

## 3. Phase 1 Backup Record

[phase_1_backup_completion_record_20260726122144.md](../history/operations/phase_1_backup_completion_record_20260726122144.md)

```text
Backup Snapshot : 20260726121941
File Count      : 422
Archive Size    : 1,377,193 bytes
Archive SHA-512 : 9eaabdee62a36e072df5d990d68e9986ca34b2894f8d6212ac3db4c26c85b2947be6052e0b4bbace2575f774a28eb1694a8e6a846330d6b1c307b75d6931b483
Restore         : PASS
```

## 4. Backup Input Index

[documentation_index_20260726121346.md](../history/documentation_index_20260726121346.md)

Backup Archiveには入力Indexまでが含まれる。本Backup完了記録と本IndexはDetached Post-backup Evidenceであり、次回BackupまたはGit Historyへ引き継ぐ。

## 5. Phase 1 Finalization

[phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](../history/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)

[designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)

## 6. Phase 1-ex Current Requirements

[phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](../history/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)

Current Sequence：

```text
1. Lightning Auto-start Read-only Preflight
2. Git運用設計
3. Git公開準備
4. docs/構造再設計
5. 全担当Taskへ通知
6. Lossless Docs再整理
7. Canonical／公開Docs
8. Mac限定簡易RAG
9. Review／Test／Privacy Scan
10. Initial Commit／Tag／Phase 1-ex Backup
11. GitHub公開
```

## 7. Current Public Demo Decision

```text
Current Preview            : Basic認証を維持
Personal Contact in Repo   : 掲載しない
README                     : 「将来、Public Demo方式も検討しています。」
Public Demo Guard          : Future
Traffic-aware Auto-start   : Phase 1-ex早期Preflight
```

## 8. Current User Manual

[phase_1_web_and_lightning_user_manual_20260726111632.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)

## 9. Authorization Boundary

Phase 1確定Backupは完了した。

次はまだ開始していない。

- Phase 1-ex変更
- Lightning Auto-start Preflight／設定変更
- Git初期化、Commit、Tag、Remote、Push
- Docs Directory Migration
- Canonical Docs生成
- Simple RAG実装
- GitHub公開

## 10. Append-Only

旧Index、Backup入力IndexおよびDetached Backup Evidenceを保持する。本IndexをPhase 1 Backup完了後の最新入口とする。

<!-- SOURCE_END 76: docs/documentation_index_20260726122144.md -->

---

