# Phase 1 Requirements Lossless Compilation
```yaml
document_id: phase_1_requirements_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 38
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

<!-- SOURCE_BEGIN 1: docs/requirements/configuration_layer_requirements_20260719041847.md -->

### Source 1: `docs/requirements/configuration_layer_requirements_20260719041847.md`

- History Target: `docs/project/phases/phase_1/history/requirements/configuration_layer_requirements_20260719041847.md`
- Source SHA-512: `3cbb1e4111b9023d80827561e7b08da782cd99a4a9cbb19c56b22b68f83004385387ee5557a84248c6d05cabe23c7ef6c9a94b6057210ea78fc746a3a3c04a5a`
- Source Size: `12333` bytes

# Configuration Layer 分離要件

- 文書ID: `configuration_layer_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Application Config、Model Definition、Deployment Profile、Platform Registry、Effective Config
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
- Architecture: [configuration_layer_architecture_20260719041847.md](../history/architecture/configuration_layer_architecture_20260719041847.md)
- Accepted ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: なし（新規Configuration Layer専用Requirements系列）

## 1. 結論

Current `config/profiles/local_macos_arm64.toml`は、Application共通設定、Model選択、Storage、Generation、DeploymentおよびHardware Tuningを一つのFileへ混在させている。

Linux、Windows、Home ServerまたはCloud Profileを追加した場合、Platformと無関係な`max_new_tokens`、Language、Model Root等まで複製され、設定Driftが発生する。

Phase 1-D実装前に、Configを責務単位へ分離する。

```text
Application Config
Model Definition
Deployment Profile
Platform Registry
Environment／Explicit Override
        ↓
Typed Configuration Composer
        ↓
Effective Phase 1 Config
```

## 2. Required Directory Structure

```text
config/
├─ application.toml
├─ models/
│    └─ qwen3_4b_q4_k_m.toml
├─ profiles/
│    └─ local_macos_arm64.toml
└─ platforms/
     └─ platform_registry.toml
```

Phase 1-Dでは、Generation／Responseごとの小Fileを量産しない。

将来複数Presetが必要になった場合は、次を追加可能とする。

```text
config/presets/
├─ generation/
└─ response/
```

## 3. Configuration Ownership

### 3.1 Application Config

`config/application.toml`はPlatformをまたいで共有するApplication Defaultを所有する。

- Application Key／Schema Version
- Selected Model
- Model Root
- Common Load Default
- Generation Default
- Response Policy Default

### 3.2 Model Definition

`config/models/*.toml`はModel ArtifactとModel固有事実を所有する。

- Model Key／Role
- Source／Revision
- Artifact Path／Hash／Format／Quantization
- Backend Compatibility
- Architecture
- Native Context Limit
- Chat Template Source
- Required／Optional Model Capability
- Provenance／Verification

Model DefinitionはCurrent Platform、Default Languageまたは利用者のGeneration Preferenceを所有しない。

### 3.3 Deployment Profile

`config/profiles/*.toml`はDeployment固有事実とHardware Tuningだけを所有する。

- Profile Key／Schema Version／Verification State
- Host OS／Architecture／Execution Environment
- Compute／Vendor／Acceleration／Memory Topology
- Backend Runtime／Build Variant／Execution Mode
- Runtime Requirements／Fallback Policy
- Hardware-dependent Load Override

Deployment ProfileはSelected Model、Model Root、Generation DefaultまたはResponse Languageを所有しない。

### 3.4 Platform Registry

`config/platforms/platform_registry.toml`は次だけを所有する。

- OS Alias
- Architecture Alias
- Platform Default Profile Path
- Registry Schema／Reference Integrity

Application Defaultを所有しない。

## 4. Field Placement

| Field | Owner | 備考 |
|---|---|---|
| `selected_model` | Application Config | Environment／CLIでOverride可能 |
| `model_root` | Application Config | Storage設定、Platformではない |
| `context_size` | Application Common Load Default | 必要時だけDeployment／CLI Override |
| `verify_artifact_hash` | Application Common Load Default | Integrity Policy |
| `verbose_backend` | Application Common Load Default | Diagnostic Default |
| `max_new_tokens` | Application Generation | Request Override可能 |
| Sampling値 | Application Generation | 将来Preset化可能 |
| `thinking_mode` | Application Generation | 表示Policyとは別 |
| `response.language` | Application Response | Phase 1-Dで`ja` Default |
| `host` | Deployment Profile | OS／Architecture等 |
| `compute` | Deployment Profile | GPU／CPU／Acceleration等 |
| `backend_runtime` | Deployment Profile | Build Variant等 |
| `runtime_requirements` | Deployment Profile | Current Deployment要求 |
| `batch_size` | Deployment Load Override | Hardware Tuning |
| `micro_batch_size` | Deployment Load Override | Hardware Tuning |
| `threads` | Deployment Load Override | Hardware Tuning |
| `threads_batch` | Deployment Load Override | Hardware Tuning |
| `gpu_layers` | Deployment Load Override | Hardware／Backend Tuning |
| `use_mmap` | Deployment Load Override | Host／Backend Tuning |
| `use_mlock` | Deployment Load Override | Host／Memory Tuning |
| Artifact SHA-512 | Model Definition | Artifact Identity |
| Native Context Limit | Model Definition | Model固有上限 |

## 5. Application Config Contract

初期概念形：

```toml
schema_version = "1"
application_key = "default"
selected_model = "main.qwen3-4b-q4-k-m"

[model_root]
default = "./models"
environment_variable = "MARGPA_MODEL_ROOT"

[load_defaults]
context_size = 4096
verbose_backend = false
verify_artifact_hash = true

[generation]
max_new_tokens = 512
temperature = 0.7
top_p = 0.8
top_k = 20
min_p = 0.0
presence_penalty = 1.5
frequency_penalty = 0.0
repeat_penalty = 1.0
stop_sequences = []
thinking_mode = "disabled"

[response]
language = "ja"
```

Tracked Fileでは再現性のため値を明示する。

## 6. Deployment Profile Contract

Migration後の概念形：

```toml
schema_version = "3"
profile_key = "local.macos-arm64"
verification_state = "native_verified"

[host]
...

[compute]
...

[backend_runtime]
...

[runtime_requirements]
...

[load_overrides]
batch_size = 256
micro_batch_size = 256
threads = 6
threads_batch = 6
gpu_layers = -1
use_mmap = true
use_mlock = false
```

`context_size`はApplication Defaultを使用する。特定Deploymentで異なる値が必要になった場合だけ`load_overrides.context_size`を許可する。

## 7. Schema Version

```text
Application Config Schema : 1
Deployment Profile Schema : 2 → 3
Model Definition Schema   : 1のまま
Platform Registry Schema  : 1のまま
```

Deployment Profile Version更新の理由は、Response追加ではなく、Application共通Fieldの除去と`load`から`load_overrides`への責務変更である。

## 8. Typed Composition

汎用的なDictionary Deep Mergeを禁止する。

理由：

- Typoが新しいFieldとして混入する
- Field Ownerが不明になる
- PlatformがApplication Policyを上書きできる
- List置換／結合規則が曖昧になる
- AuditでSourceを説明しにくい

Typed ContractとField Allowlistによって合成する。

```text
ModelLoadConfig
  = Built-in ModelLoad Default
  + Application load_defaults
  + Deployment load_overrides Allowlist
  + Environment Load Override
  + Explicit／CLI Load Override
```

GenerationとResponseにはDeployment Overrideを適用しない。

## 9. Resolution Precedence

### Model Selection／Model Root

```text
Explicit／CLI
  > Environment
  > Application Config
  > Built-in Default
```

### Load

```text
Explicit／CLI
  > Environment
  > Deployment Load Override
  > Application Common Load Default
  > Built-in Default
```

### Generation

```text
Per-request／CLI
  > Environment
  > Application Generation Default
  > Built-in Default
```

### Response Language

```text
Per-request／CLI
  > Environment
  > Application Response Default
  > Built-in Default
```

### Deployment Profile Selection

```text
Explicit Profile
  > Environment Profile
  > Platform Default Resolver
```

## 10. Source Tracking

Effective Configは、値だけでなくSourceを追跡可能にする。

最低限：

- `applied_sources`
- `profile_resolution_source`
- `response_language_source`

将来AuditではField単位のSource Mapへ拡張可能とする。

Phase 1-Dで全Fieldの詳細Provenance Engineは実装しない。

## 11. Functional Requirements

### CR-1 Application Config Loader

`config/application.toml`をStrict Validationで読み込む。

- Unknown Field拒否
- Unknown Schema拒否
- Unsafe Model Root拒否
- Unknown Language拒否
- Generation／Load値Validation

### CR-2 Deployment Profile Loader

Migration後のSchema `3`を読み込む。

- Application FieldをProfileへ書いた場合はUnknown Fieldとして拒否
- `load_overrides`以外の任意Deep Mergeを許可しない
- Hardware Override FieldをAllowlistで制限する

### CR-3 Effective Config Composer

Application Config、Model Definition、Deployment Profile、EnvironmentおよびExplicit Overrideから既存`EffectivePhase1Config`相当を生成する。

### CR-4 Compatibility Validation

- Selected Model BackendとDeployment Backendの整合を確認する
- Context SizeがModel Native Limitを超えないことを確認可能にする
- Deployment Runtime RequirementをPre-load／Post-loadで維持する
- Unknown／Incompatibleを黙ってFallbackしない

### CR-5 CLI Compatibility

既存CLI操作を維持する。

- `--model-root`
- `--model-key`
- `--context-size`
- `--profile`
- Generation Override
- `model-info`

### CR-6 Observability

`model-info`でApplication ConfigとDeployment Profileが別Sourceであることを確認できるようにする。

最低限：

```text
application_key
selected_model
profile_key
profile_resolution_source
load
generation
response
applied_sources
```

## 12. Non-functional Requirements

- 新規外部Dependencyを追加しない
- Application CoreへmacOS固有処理を追加しない
- Model AdapterへConfig合成を追加しない
- Config Loader／Composerを実ModelなしでUnit Test可能にする
- Existing Native Metal RuntimeをRegressionさせない
- Config File Hashを実装担当Statusへ記録する
- Tracked ConfigへUser固有Absolute Pathを記載しない

## 13. Scope外

- Multiple Application Config Selector UI
- Remote Config Service
- Dynamic Config Reload
- Secret Manager
- User／Session Preference Storage
- Generic Plugin Config
- Arbitrary Deep Merge
- 全FieldのField-level Provenance Log
- Windows／Linux実Profile
- Generation Preset Directory実装
- Response Preset Directory実装
- Phase 1-E Thinking Presentation

## 14. Required Tests

### Loader

- Application Config Schema `1`
- Deployment Profile Schema `3`
- Unknown Field拒否
- Old Mixed ProfileをCurrentとして受理しない
- Unsafe Path拒否

### Ownership

- Application ConfigがSelected Model／Model Root／Generation／Responseを持つ
- Deployment Profileがこれらを持たない
- Deployment ProfileがHardware Load Overrideを持つ
- Model DefinitionがArtifact／Capabilityを維持する

### Composition

- 共通Default継承
- Deployment Hardware Override
- Environment Override
- CLI Override
- Field別Precedence
- Invalid Override Safe Error
- Unknown PlatformのNo Fallback

### Regression

- Static Gate
- Default pytest
- Environment／Lock／Offline Gate
- `model-info`
- Load／Generate／Stream／Cancel／Unload
- Metal Smoke
- Artifact Hash Verification

## 15. Acceptance Criteria

1. `config/application.toml`が追加される
2. Application Config Schema `1`がStrict Validationされる
3. Deployment Profile Schemaが`3`になる
4. Platform ProfileからApplication共通Fieldが除かれる
5. `load_overrides`がHardware Fieldだけを受理する
6. GenerationとResponseがPlatform Profileへ複製されない
7. Typed ComposerがEffective Configを生成する
8. Field別PrecedenceがTestされる
9. Model／Deployment Backend整合Validationが維持される
10. Existing CLIがRegressionしない
11. Current Mac／Metal RuntimeがRegressionしない
12. 新規外部Dependencyがない

## 16. Authorization Boundary

本Requirementsはユーザー承認済みのConfiguration Layer分離を記録する。

Source、Config、TestまたはScriptの変更は、ユーザーからPhase 1-D実装開始の明示許可を得た後に行う。

<!-- SOURCE_END 1: docs/requirements/configuration_layer_requirements_20260719041847.md -->

---

<!-- SOURCE_BEGIN 2: docs/requirements/documentation_rules_20260718174637.md -->

### Source 2: `docs/requirements/documentation_rules_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/requirements/documentation_rules_20260718174637.md`
- Source SHA-512: `3c88d3d6d96820db420955f905b2bec125ada84ed452ccef7d685960bfcd3d953298640d7e8bf0adc2c7c1d9ede7c8e34b165ea9b9fb76802ee05d235b5c54f3`
- Source Size: `5102` bytes

# 文書作成・命名・更新共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書
- 正本言語: 日本語

## 1. 目的

この文書は、`docs/`以下に作成する文書のファイル名、時刻、言語、更新、正本、引き継ぎ方法を統一する共通ルールである。

設計者、実装者、対外向けDocs作成者、その他の担当タスクは、文書を新規作成する前にこのルールを参照する。

## 2. 必須ファイル名形式

Markdown文書のファイル名は、次の形式を必須とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

例：

```text
system_architecture_20260718174023.md
runtime_governance_20260718174023.md
common_project_handoff_20260718174023.md
adr_0001_initial_model_selection_20260718174023.md
```

正規表現の概念形：

```text
^[a-z0-9]+(?:_[a-z0-9]+)*_[0-9]{14}\.md$
```

## 3. ファイル名の規則

- 説明部分は英語の小文字を使用する
- 単語の区切りには`_`を使用する
- 空白を使用しない
- ハイフンを使用しない
- 日本語をファイル名に使用しない
- 最後に14桁の作成時刻を必ず付ける
- 拡張子は原則`.md`とする
- ADRは`adr_0001_...`の形式で連番を持たせる
- Model ID、Class名、設定キー等の原表記は本文中に記載し、ファイル名へ無理に再現しない

## 4. 時刻の規則

14桁の時刻形式：

```text
YYYYMMDDHHMMSS
```

内訳：

```text
YYYY : 年
MM   : 月
DD   : 日
HH   : 時（24時間）
MM   : 分
SS   : 秒
```

Timezoneは`Asia/Tokyo / JST`を正本とする。

複数文書を一つの設計Snapshotとして一括作成する場合は、文書セットの作成開始時刻を全ファイルで共有してよい。この場合、全ファイルのFront Matter相当のメタデータに同じ作成日時を記載し、同一Snapshotであることを明示する。

## 5. 文書本文の言語

本文は可能な限り日本語で作成する。

英語を保持するもの：

- Model ID
- Repository ID
- Class名
- 関数名
- 設定キー
- Protocol名
- Licenseの正式名称
- 外部資料の正式名称
- コード上必要な識別子
- ARGD／DAGD等の定義上の正式語

英語資料を参照する場合は、日本語で内容を説明し、原文名称と参照先を併記する。

## 6. 文書の必須メタデータ

各文書の先頭には、可能な限り次を記載する。

```text
文書ID
状態
作成日時
更新日時
担当または対象
正本言語
上位文書
置換対象
```

状態候補：

```text
draft
current
experimental
deprecated
superseded
archived
```

## 7. 更新と版管理

### 7.1 軽微な修正

誤字、リンク修正、意味を変えない表現修正は既存ファイルを更新してよい。その場合は本文の`更新日時`を更新する。

### 7.2 実質的な改訂

要件、設計判断、Module Boundary、公開方針等を実質的に変更する場合は、新しい作成時刻を持つ新規ファイルを作成する。

新しい文書には次を記載する。

```text
置換対象: 旧ファイル名
```

旧文書には、可能な場合は次を追記する。

```text
状態: superseded
後継文書: 新ファイル名
```

## 8. 正本の決定

同じ主題の文書が複数ある場合、単純に時刻が新しいものを自動的な正本とはしない。

`docs/documentation_index_*.md`で`current`として指定された文書を現在の正本とする。

## 9. Directoryの役割

```text
docs/
├─ requirements/  要件、制約、MVP、未決事項
├─ architecture/  システム構成、Model、Storage、Roadmap
├─ governance/    ARGD、DAGD、監査、評価、安全性
├─ adr/           設計判断と理由
└─ handoffs/      共通・担当別の引き継ぎ
```

必要になった場合は、同じ命名規則に従って追加Directoryを設ける。

## 10. 引き継ぎ時の利用方法

新しい担当タスクは、原則として次の順に読む。

1. 最新の`documentation_index_*.md`
2. 最新の`common_project_handoff_*.md`
3. 担当領域のRequirements／Architecture／Governance
4. 関連ADR
5. 未決事項と次の作業

引き継ぎ文書は正本の内容を勝手に変更せず、正本への参照と現在地点を示す。

## 11. 禁止事項

- Timestampを持たないMarkdown文書を新規作成しない
- 同名ファイルを上書きして重大な設計変更を隠さない
- 日本語正本と英語文書の内容を無管理で分岐させない
- 古い引き継ぎ文書だけを根拠に実装しない
- 確定、暫定、未決、将来、対象外を混同しない
- ユーザー固有のSecretやCredentialをDocsへ記載しない

## 12. このSnapshotについて

この文書を含む初期文書セットは、`20260718174637`を共通Snapshot時刻として作成した。

<!-- SOURCE_END 2: docs/requirements/documentation_rules_20260718174637.md -->

---

<!-- SOURCE_BEGIN 3: docs/requirements/documentation_rules_20260718193435.md -->

### Source 3: `docs/requirements/documentation_rules_20260718193435.md`

- History Target: `docs/project/phases/phase_1/history/requirements/documentation_rules_20260718193435.md`
- Source SHA-512: `bb6414983994b8038290e91a3415d96d0564387392ae5fcc77ba00ed0ab08c2c7410a7cbdaa3dcb987e18ebba23166573ef7a1d324db3cd0ae56348821192042`
- Source Size: `11102` bytes

# 文書作成・命名・更新共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書
- 正本言語: 日本語
- supersedes: `documentation_rules_20260718174637.md`

## 1. 目的

この文書は、`docs/`以下に作成する文書のファイル名、時刻、言語、更新、正本、引き継ぎ方法を統一する共通ルールである。

設計者、実装者、対外向けDocs作成者、その他の担当タスクは、文書を新規作成する前にこのルールを参照する。

## 1.1 プロジェクトルートと相対Pathの解決

このProjectにおけるProject Rootの論理表記は、次とする。

```text
margpa-runtime-llm/
```

現在のLocal環境における実体Path：

```text
/path/to/margpa-runtime-llm/
```

ユーザーが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合は、明示的に別の基準Pathが指定されていない限り、Project Rootを基準として解釈する。

例：

```text
User指定 : docs/
解釈      : margpa-runtime-llm/docs/

User指定 : docs/architecture/
解釈      : margpa-runtime-llm/docs/architecture/
```

相対PathをHome Directory、現在のTask固有Directory、外部Model Root等へ勝手に読み替えない。

## 1.2 タスク間の情報伝達

設計者、実装者、対外向けDocs作成者、その他の担当タスク間における情報伝達、決定事項、進捗通達、未決事項、引き継ぎは、原則として次を共通基盤とする。

```text
margpa-runtime-llm/docs/
```

担当タスクは、会話内だけで重要な決定や進捗を閉じず、ユーザーから記録を許可・依頼された場合は、適切なRequirements、Architecture、Governance、ADR、Handoffへ反映する。

ただし、Docsへの記録は明示的な作成・更新権限がある場合に限る。単にDocsを読むよう依頼されたことを、編集許可として扱わない。

## 1.3 Docs参照時の読み取り専用原則

`margpa-runtime-llm/docs/`を読み込む、確認する、参照する、引き継ぐよう指示された場合、原則として必ず読み取り専用で扱う。

次の操作は、ユーザーから明示的な変更指示または作成・更新許可がない限り行わない。

- File作成
- File編集
- File削除
- File名変更
- Directory作成・削除
- Status変更
- 正本の差し替え
- 内容の自動修正

矛盾、誤記、古い情報、Link切れ等を発見した場合も、読み取り依頼だけで勝手に修正しない。発見内容を報告し、変更権限を確認する。

「Docsを参照する権限」と「Docsを変更する権限」は別の権限として扱う。

## 2. 必須ファイル名形式

Markdown文書のファイル名は、次の形式を必須とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

例：

```text
system_architecture_20260718174023.md
runtime_governance_20260718174023.md
common_project_handoff_20260718174023.md
adr_0001_initial_model_selection_20260718174023.md
```

正規表現の概念形：

```text
^[a-z0-9]+(?:_[a-z0-9]+)*_[0-9]{14}\.md$
```

## 3. ファイル名の規則

- 説明部分は英語の小文字を使用する
- 単語の区切りには`_`を使用する
- 空白を使用しない
- ハイフンを使用しない
- 日本語をファイル名に使用しない
- 最後に14桁の作成時刻を必ず付ける
- 拡張子は原則`.md`とする
- ADRは`adr_0001_...`の形式で連番を持たせる
- Model ID、Class名、設定キー等の原表記は本文中に記載し、ファイル名へ無理に再現しない

## 4. 時刻の規則

14桁の時刻形式：

```text
YYYYMMDDHHMMSS
```

内訳：

```text
YYYY : 年
MM   : 月
DD   : 日
HH   : 時（24時間）
MM   : 分
SS   : 秒
```

Timezoneは`Asia/Tokyo / JST`を正本とする。

複数文書を一つの設計Snapshotとして一括作成する場合は、文書セットの作成開始時刻を全ファイルで共有してよい。この場合、全ファイルのFront Matter相当のメタデータに同じ作成日時を記載し、同一Snapshotであることを明示する。

## 5. 文書本文の言語

本文は可能な限り日本語で作成する。

英語を保持するもの：

- Model ID
- Repository ID
- Class名
- 関数名
- 設定キー
- Protocol名
- Licenseの正式名称
- 外部資料の正式名称
- コード上必要な識別子
- ARGD／DAGD等の定義上の正式語

英語資料を参照する場合は、日本語で内容を説明し、原文名称と参照先を併記する。

## 5.1 プロジェクト通称の共通表記

Projectの通称は、次を正本とする。

```text
Nazuna Research Governance LLM
```

Project名と表示名を併記する場合は、次の表記を使用する。

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

新規Docs、Handoff、README、Architecture説明では、通称を勝手に短縮・翻訳・変更せず、`Nazuna Research Governance LLM`へ統一する。

## 6. 文書の必須メタデータ

各文書の先頭には、可能な限り次を記載する。

```text
文書ID
状態
作成日時
更新日時
担当または対象
正本言語
上位文書
置換対象
```

状態候補：

```text
draft
current
experimental
deprecated
superseded
archived
```

## 7. 更新と版管理

`docs/`以下の文書は、厳格なAppend-Only方式で管理する。

### 7.1 作成済み文書の不変性

作成済みDocsは原則として変更しない。

変更しない対象：

- 本文
- Metadata
- Status
- Link
- File名
- Timestamp
- 誤字
- 表現

誤字、Link切れ、意味を変えない修正であっても、既存Fileを直接編集せず、新しいTimestampを持つ後継Fileを作成する。

### 7.2 変更時は新規Fileを作成する

要件追加、設計変更、進捗更新、Status更新、誤記修正を行う場合は、新しい作成時刻を持つ新規Fileを作成する。

例：

```text
project_requirements_20260718174637.md
project_requirements_20260718193435.md
```

同じFile名への上書きは禁止する。

### 7.3 `supersedes`の記録

後継文書には、置換する旧文書をMetadataとして明記する。

```text
supersedes: project_requirements_20260718174637.md
```

必要に応じて複数の旧文書を参照できる。

旧文書へ`superseded`、`後継文書`等を追記しない。それ自体が旧Snapshotの改変になるためである。

旧文書の状態と後継関係は、新しい`documentation_index`側で管理する。

### 7.4 Documentation IndexもAppend-Onlyとする

`documentation_index`も上書きしない。

文書構成、最新文書、Status、後継関係が変わるたびに、新TimestampのIndexを作成する。

```text
documentation_index_20260718174637.md
documentation_index_20260718193435.md
```

古いIndexを残すことで、その時点で何が正本だったかを再現可能にする。

### 7.5 HandoffとStatusもAppend-Onlyとする

Handoff、進捗通達、担当別Statusも毎回新規Fileとして作成する。

例：

```text
common_project_handoff_YYYYMMDDHHMMSS.md
designer_status_<topic>_YYYYMMDDHHMMSS.md
implementer_status_<topic>_YYYYMMDDHHMMSS.md
external_docs_status_<topic>_YYYYMMDDHHMMSS.md
```

過去のHandoffやStatusを上書きしない。

### 7.6 新しいものを最新とする

同じ文書ID、同じ主題、同じFile Prefixに属する文書では、File名末尾のTimestampが最も新しいFileを最新とする。

```text
project_requirements_20260718174637.md
project_requirements_20260718193435.md  ← 最新
```

`documentation_index`についても、Timestampが最も新しいものを最新Indexとする。

新しい文書が古い内容へ戻すRollbackであっても、新Timestampの文書を作成する。そのため、常に「新しいものが最新」という判定を維持する。

### 7.7 古い文書を削除しない

古い文書はDevelopment ProcessとDecision Historyの一部として保持する。

原則として次を行わない。

- Delete
- Rename
- Move
- Content Rewrite
- Metadata Rewrite

例外的なHistory修復が必要な場合は、ユーザーから明示的な許可を得て、修復内容と理由を新しいIndexまたは専用History文書へ記録する。

## 8. 正本と最新の決定

最新の`documentation_index_*.md`を最初に確認する。

最新Indexは、次を管理する。

- 現在の最新文書
- 過去文書
- supersedes関係
- Current Document Set
- Historical Document Set

同じ文書系列では、Timestampが最も新しい文書を最新とする。

新規Taskは、古いIndexや古いHandoffだけを根拠に作業を開始しない。

## 8.1 Append-Onlyの必須7原則

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes`として旧Fileを明記する
4. `documentation_index`も上書きせず、新Timestampで作る
5. 古いIndexを残し、各時点の正本文書構成を再現可能にする
6. HandoffやStatusも毎回新規作成する
7. 古い文書へ`superseded`表記を追記せず、新Index側で状態を示す

## 9. Directoryの役割

```text
docs/
├─ requirements/  要件、制約、MVP、未決事項
├─ architecture/  システム構成、Model、Storage、Roadmap
├─ governance/    ARGD、DAGD、監査、評価、安全性
├─ adr/           設計判断と理由
└─ handoffs/      共通・担当別の引き継ぎ
```

必要になった場合は、同じ命名規則に従って追加Directoryを設ける。

## 10. 引き継ぎ時の利用方法

新しい担当タスクは、原則として次の順に読む。

1. 最新の`documentation_index_*.md`
2. 最新の`common_project_handoff_*.md`
3. 担当領域のRequirements／Architecture／Governance
4. 関連ADR
5. 未決事項と次の作業

引き継ぎ文書は正本の内容を勝手に変更せず、正本への参照と現在地点を示す。

## 11. 禁止事項

- Timestampを持たないMarkdown文書を新規作成しない
- 既存Fileを上書きしない
- 古い文書を削除・改名・移動しない
- 古い文書へStatusや後継情報を追記しない
- 最新Indexを確認せずに作業を開始しない
- 日本語正本と英語文書の内容を無管理で分岐させない
- 古い引き継ぎ文書だけを根拠に実装しない
- 確定、暫定、未決、将来、対象外を混同しない
- ユーザー固有のSecretやCredentialをDocsへ記載しない

## 12. このSnapshotについて

この文書は、`documentation_rules_20260718174637.md`を置換し、Append-Only方式を正式な共通ルールとして追加した後継文書である。

<!-- SOURCE_END 3: docs/requirements/documentation_rules_20260718193435.md -->

---

<!-- SOURCE_BEGIN 4: docs/requirements/documentation_rules_20260719142558.md -->

### Source 4: `docs/requirements/documentation_rules_20260719142558.md`

- History Target: `docs/project/phases/phase_1/history/requirements/documentation_rules_20260719142558.md`
- Source SHA-512: `59057857b1eb1cd160e02150a605beecf76f1fca0d2889382858e217b75e9799662f692fa1f145c2bf6c0ddd81b566b6c6345f892fd3be6f92c9ce233ce9d60a`
- Source Size: `7802` bytes

# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- Snapshot: `20260719142558`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- Backup Policy: [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md)
- supersedes: `documentation_rules_20260718193435.md`

## 1. 目的

本書は、`docs/`のFile名、時刻、言語、Append-Only更新、正本、担当TaskのWrite Authority、Review／Index、Phase完了Backupの共通ルールを定義する。

新しいTaskは、最新Documentation Indexと本書を最初に参照する。

## 2. Project Root

Logical Root：

```text
margpa-runtime-llm/
```

Current Local Root：

```text
/path/to/margpa-runtime-llm/
```

Userが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合は、明示的な別基準がない限りProject Root基準とする。

## 3. Project表記

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

新規Docsでは通称を`Nazuna Research Governance LLM`へ統一する。

## 4. Task間Communication

要件、Decision、Progress、Finding、Review、Handoff、未解決事項、Phase Statusは原則として次を共通基盤とする。

```text
margpa-runtime-llm/docs/
```

会話内だけで重要Decisionを閉じない。ただしDocsへの記録はUserの指示とTask Role Authorityの範囲内で行う。

## 5. Docs Read-only Principle

Docsを読み込む、参照する、引き継ぐ、確認する依頼は、原則としてRead-onlyである。

次は明示的なWrite指示またはRole Authorityがない限り行わない。

- File作成／編集／削除
- Rename／Move
- Status変更
- 正本差し替え
- Link修正
- 誤字修正

問題を発見しても読み取り依頼だけで勝手に修正せず、Findingを報告する。

## 6. Filename

Markdown文書は次の形式とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

概念正規表現：

```text
^[a-z0-9]+(?:_[a-z0-9]+)*_[0-9]{14}\.md$
```

規則：

- 説明部分は英小文字／数字
- `_`区切り
- 空白／Hyphen／日本語をFile名に使用しない
- 末尾に14桁Timestamp
- ADRは`adr_0001_...`形式
- Model ID／Class名／原表記は本文で保持

## 7. Timestamp

```text
YYYYMMDDHHMMSS
```

Timezone：

```text
Asia/Tokyo／JST
```

同一設計Snapshotで複数文書を作る場合は、作成開始時刻を共有できる。全Fileに同じSnapshot／作成日時を記載する。

## 8. Language

本文は可能な限り日本語とする。

原表記を保持する主なもの：

- Model／Repository ID
- Class／Function／Config Key
- Protocol／Licenseの正式名
- ARGD／DAGD等のDefinition上の識別子
- Code上の識別子

## 9. Required Metadata

各文書の先頭に可能な限り次を記載する。

```text
文書ID
状態
作成日時
更新日時
Snapshot
担当／対象
正本言語
上位／関連文書
supersedes
```

## 10. Append-Only

`docs/`はStrict Append-Onlyとする。

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes: old_file_YYYYMMDDHHMMSS.md`を記載する
4. Documentation Indexも上書きせず新Timestampで作る
5. 古いIndexを残し、各時点のCurrent Setを再現可能にする
6. Handoff／Status／Reviewも毎回新規作成する
7. 古い文書へSuperseded表記を追記せず、新Index側で状態を示す

誤字、Link切れ、意味を変えない修正でも既存Fileを直接編集しない。

## 11. Latest／Current

- 同一系列でTimestampが最も新しいFileを最新とする
- 最新`documentation_index_*`をCurrent Set判定の入口とする
- Rollback内容でも新Timestampを使う
- 古いDocs／Indexを削除／Rename／Moveしない
- 古いHandoffだけを根拠に作業を開始しない

## 12. Directory

```text
docs/
├─ requirements/  要件、制約、共通Rule、Role Authority
├─ architecture/  System構成、Model、Storage、Roadmap
├─ governance/    ARGD／DAGD、Audit、Evaluation、Security
├─ adr/           Decision、理由、代替案
├─ operations/    Phase Backup、Snapshot、Restore、Release Operations
├─ user_manual/   内部User Manual
├─ public/        将来の対外Public Docs
└─ handoffs/      Common／Designer／Implementer／External Handoff／Status／Review
```

`docs/public/`は必要になった時点で作成する。

## 13. Role Authority

詳細正本：

- [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)

要約：

```text
設計者:
  Requirements／Architecture／Governance／ADR／Operations
  User Manual／Index／Common／Designer Handoff／Review
  各担当の開始用Handoff

実装者:
  src／tests／scripts
  implementer_status_*
  config／Root FileはAccepted Handoff + User許可で条件付き

対外Docs作成者:
  README／docs/public/
  external_docs_status_*
  Canonical DocsはRead-only
```

## 14. Review／Index Pairing

実装者Statusを設計者がReviewした場合、原則として次を同一Snapshotで作成する。

```text
designer_review_<topic>_YYYYMMDDHHMMSS.md
documentation_index_YYYYMMDDHHMMSS.md
```

ReviewとIndexは設計者役のOwnershipとする。

Findingがある場合でも、Review依頼だけでSource Fixを行わない。

## 15. Handoff／Status

- `common_project_handoff_*`: 設計者
- `designer_handoff_*`: 設計者
- `designer_review_*`: 設計者
- `implementer_handoff_*`: 設計者が開始指示として作成
- `implementer_status_*`: 実装者
- `public_documentation_handoff_*`: 設計者が開始指示として作成
- `external_docs_status_*`: 対外Docs作成者

すべてAppend-Onlyとする。

## 16. Operational Status

設計者役と実装者役の分業は、Phase 1-A／1-B／1-C／1-DおよびPhase 1-EのDesign／Handoff／Implementation Cycleで実運用され、現時点で有効に機能している。

対外Docs作成者役はTask作成済みだが、本格的な実作業検証は未完了である。

## 17. Phase Completion Backup

詳細正本：

- [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md)

Backup Trigger：

```text
設計者がIndependent Review／Final Docs／Indexを完了し、
「Phase Nは完了。次はPhase N+1です」
と明示した直後。
```

Backupは完了宣言後、次Phaseの実質的変更前に行う。Implementer StatusだけではTriggerとしない。

## 18. New Task Reading Order

1. 最新`documentation_index_*`
2. 最新`common_project_handoff_*`
3. 本Documentation Rules
4. Task Role Authority Policy
5. 担当領域のRequirements／Architecture／Governance
6. 関連ADR
7. 最新Designer Handoff／Status／Review

## 19. Prohibited

- TimestampなしMarkdownの新規作成
- Existing Docsの上書き／削除／Rename／Move
- 古いDocsへ後継Status追記
- Latest Index未確認での作業開始
- Role Scope外Write
- Read依頼からのWrite Authority推定
- Review依頼からのFix Authority推定
- Secret／Credential／Personal DataのDocs記載
- 確定／暂定／未決／Future／Scope外の混同

## 20. Policy Update

本書を変更する場合は既存Fileを編集せず、新Timestampの後継文書とDocumentation Indexを作成する。

<!-- SOURCE_END 4: docs/requirements/documentation_rules_20260719142558.md -->

---

<!-- SOURCE_BEGIN 5: docs/requirements/documentation_rules_20260719171836.md -->

### Source 5: `docs/requirements/documentation_rules_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/requirements/documentation_rules_20260719171836.md`
- Source SHA-512: `e2f0d2d418fb27ce58133781e34e158d923141b456ab2848b3ef7e31cba79fcdaff27351c452aa5e0088043a87a64d081ac9e561dcdb6f6d23f26ee63f864098`
- Source Size: `9117` bytes

# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)
- Known Issues／Observations: [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)
- supersedes: `documentation_rules_20260719142558.md`

## 1. 目的

本書は、`docs/`のFile名、時刻、言語、Append-Only更新、正本、担当TaskのWrite Authority、Review／Index、Phase完了Backupの共通ルールを定義する。

新しいTaskは、最新Documentation Indexと本書を最初に参照する。

## 2. Project Root

Logical Root：

```text
margpa-runtime-llm/
```

Current Local Root：

```text
/path/to/margpa-runtime-llm/
```

Userが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合は、明示的な別基準がない限りProject Root基準とする。

## 3. Project表記

```text
Project Name  : margpa-runtime-llm
Display Name  : MARGPA Runtime LLM
Internal Name : Nazuna Research Governance LLM
```

新規Docsでは通称を`Nazuna Research Governance LLM`へ統一する。

## 4. Task間Communication

要件、Decision、Progress、Finding、Review、Handoff、未解決事項、Phase Statusは原則として次を共通基盤とする。

```text
margpa-runtime-llm/docs/
```

会話内だけで重要Decisionを閉じない。ただしDocsへの記録はUserの指示とTask Role Authorityの範囲内で行う。

## 5. Docs Read-only Principle

Docsを読み込む、参照する、引き継ぐ、確認する依頼は、原則としてRead-onlyである。

次は明示的なWrite指示またはRole Authorityがない限り行わない。

- File作成／編集／削除
- Rename／Move
- Status変更
- 正本差し替え
- Link修正
- 誤字修正

問題を発見しても読み取り依頼だけで勝手に修正せず、Findingを報告する。

## 6. Filename

Markdown文書は次の形式とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

概念正規表現：

```text
^[a-z0-9]+(?:_[a-z0-9]+)*_[0-9]{14}\.md$
```

規則：

- 説明部分は英小文字／数字
- `_`区切り
- 空白／Hyphen／日本語をFile名に使用しない
- 末尾に14桁Timestamp
- ADRは`adr_0001_...`形式
- Model ID／Class名／原表記は本文で保持

## 7. Timestamp

```text
YYYYMMDDHHMMSS
```

Timezone：

```text
Asia/Tokyo／JST
```

同一設計Snapshotで複数文書を作る場合は、作成開始時刻を共有できる。全Fileに同じSnapshot／作成日時を記載する。

## 8. Language

本文は可能な限り日本語とする。

原表記を保持する主なもの：

- Model／Repository ID
- Class／Function／Config Key
- Protocol／Licenseの正式名
- ARGD／DAGD等のDefinition上の識別子
- Code上の識別子

## 9. Required Metadata

各文書の先頭に可能な限り次を記載する。

```text
文書ID
状態
作成日時
更新日時
Snapshot
担当／対象
正本言語
上位／関連文書
supersedes
```

## 10. Append-Only

`docs/`はStrict Append-Onlyとする。

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes: old_file_YYYYMMDDHHMMSS.md`を記載する
4. Documentation Indexも上書きせず新Timestampで作る
5. 古いIndexを残し、各時点のCurrent Setを再現可能にする
6. Handoff／Status／Reviewも毎回新規作成する
7. 古い文書へSuperseded表記を追記せず、新Index側で状態を示す

誤字、Link切れ、意味を変えない修正でも既存Fileを直接編集しない。

## 11. Latest／Current

- 同一系列でTimestampが最も新しいFileを最新とする
- 最新`documentation_index_*`をCurrent Set判定の入口とする
- Rollback内容でも新Timestampを使う
- 古いDocs／Indexを削除／Rename／Moveしない
- 古いHandoffだけを根拠に作業を開始しない

## 12. Directory

```text
docs/
├─ requirements/  要件、制約、共通Rule、Role Authority
├─ architecture/  System構成、Model、Storage、Roadmap
├─ governance/    ARGD／DAGD、Audit、Evaluation、Security
├─ adr/           Decision、理由、代替案
├─ operations/    Backup、Snapshot、Restore、Release、Known Issues
├─ user_manual/   内部User Manual／User Acceptance Test
├─ public/        将来の対外Public Docs
└─ handoffs/      Common／Designer／Implementer／External Handoff／Status／Review
```

`docs/public/`は必要になった時点で作成する。

## 13. Role Authority

詳細正本：

- [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)

要約：

```text
設計者:
  Requirements／Architecture／Governance／ADR／Operations
  User Manual／Index／Common／Designer Handoff／Review
  各担当の開始用Handoff

実装者:
  src／tests／scripts
  implementer_status_*
  config／Root FileはAccepted Handoff + User許可で条件付き

対外Docs作成者:
  README／docs/public/
  external_docs_status_*
  Canonical DocsはRead-only
```

## 14. Review／Index Pairing

実装者Statusを設計者がReviewした場合、原則として次を同一Snapshotで作成する。

```text
designer_review_<topic>_YYYYMMDDHHMMSS.md
documentation_index_YYYYMMDDHHMMSS.md
```

ReviewとIndexは設計者役のOwnershipとする。

Findingがある場合でも、Review依頼だけでSource Fixを行わない。

## 15. Known Issues／Observations

PhaseをBlockしないが将来参照すべきFindingは、Review内だけでなく最新`known_issues_and_observations_*`へ登録する。

項目ごとに次を記録する。

- Stable ID
- State／Severity／Category
- Reproduction
- Cause／Impact
- Required Follow-upの有無
- Disposition
- 再評価条件

Observation登録だけでは実装修正を解禁しない。

## 16. Handoff／Status

- `common_project_handoff_*`: 設計者
- `designer_handoff_*`: 設計者
- `designer_review_*`: 設計者
- `implementer_handoff_*`: 設計者が開始指示として作成
- `implementer_status_*`: 実装者
- `public_documentation_handoff_*`: 設計者が開始指示として作成
- `external_docs_status_*`: 対外Docs作成者

すべてAppend-Onlyとする。

## 17. Operational Status

設計者役と実装者役の分業は、Phase 1-A～1-EのDesign、Handoff、Implementation、Independent Reviewで実運用され、有効に機能した。

対外Docs作成者役はTask作成済みだが、本格的な実作業検証は未完了である。

## 18. Phase Completion Backup

詳細正本：

- [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)

Backup Triggerは次の二重条件とする。

```text
Gate A:
  設計者役がPhase完了と次Phase移行可能を明示

Gate B:
  ユーザーが対象User Manual／Snapshotの受入テスト全項目合格を明示
```

両Gateが同じProject状態を対象として成立した後、次Phaseの実質的変更前にBackupを行う。

Implementer Status、Subphase完了、Designer Review、User Testのいずれか単独ではTriggerとしない。

Gate成立後にMaterial Changeが入った場合は、影響範囲に応じてReviewまたはUser Testを再実行する。

## 19. User Acceptance Test Record

Current User Manualは、対象PhaseのUser Acceptance Test手順と合格条件を持つ。

ユーザー宣言の推奨形式：

```text
<user_manual_file>のPhase Nユーザー受入テストは、全項目合格です。
```

Snapshot Record／Manifestは、この宣言と設計者宣言の両方をEvidenceとして参照する。

## 20. New Task Reading Order

1. 最新`documentation_index_*`
2. 最新`common_project_handoff_*`
3. 本Documentation Rules
4. Task Role Authority Policy
5. 担当領域のRequirements／Architecture／Governance
6. 関連ADR
7. 最新Designer Handoff／Status／Review
8. Latest Known Issues／Operations Policy

## 21. Prohibited

- TimestampなしMarkdownの新規作成
- Existing Docsの上書き／削除／Rename／Move
- 古いDocsへ後継Status追記
- Latest Index未確認での作業開始
- Role Scope外Write
- Read依頼からのWrite Authority推定
- Review依頼からのFix Authority推定
- Secret／Credential／Personal DataのDocs記載
- 確定／暫定／未決／Future／Scope外の混同
- Dual Approval Gate片方だけでのPhase Backup

## 22. Policy Update

本書を変更する場合は既存Fileを編集せず、新Timestampの後継文書とDocumentation Indexを作成する。

<!-- SOURCE_END 5: docs/requirements/documentation_rules_20260719171836.md -->

---

<!-- SOURCE_BEGIN 6: docs/requirements/documentation_rules_20260720220216.md -->

### Source 6: `docs/requirements/documentation_rules_20260720220216.md`

- History Target: `docs/project/phases/phase_1/history/requirements/documentation_rules_20260720220216.md`
- Source SHA-512: `65b6f55024c294061146643a3fb1932581ad873dd210090a4ee89c6328ee44b356ed31c05f8c242f8b43a332897619044a558e55701d7bbfe383f4a1be9d27d0`
- Source Size: `7169` bytes

# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)
- Backup Policy: [phase_completion_backup_policy_20260719171836.md](../history/operations/phase_completion_backup_policy_20260719171836.md)
- Known Issues／Observations: [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)
- supersedes: `documentation_rules_20260719171836.md`

## 1. 目的

本書は、Docsの基準Path、公開識別子、File名、時刻、言語、Append-Only、正本、担当TaskのWrite Authority、Review／Index、Phase完了Backupを定義する。

新しいTaskは、最新Documentation Index、本書、Privacy Policyを最初に参照する。

## 2. Project Root

Logical Rootは`margpa-runtime-llm/`である。ユーザーが`docs/`、`src/`、`models/`等の相対Pathだけを指定した場合、明示的な別基準がない限りProject Root基準とする。

文書やSampleへ個人固有のCurrent Local Rootを記録せず、必要な場合は`/path/to/margpa-runtime-llm`等の抽象Pathを使う。

## 3. Project表記と公開識別子

```text
Project Name   : margpa-runtime-llm
Display Name   : MARGPA Runtime LLM
Internal Name  : Nazuna Research Governance LLM
Public Identity: Nazuna Research
```

第一者の作者、設計者、開発者、Maintainer等の固有名表記は`Nazuna Research`へ統一する。役割名である「ユーザー」「設計者役担当Task」「実装担当Task」等は固有名ではないため使用できる。

## 4. Task間Communication

要件、Decision、Progress、Finding、Review、Handoff、未解決事項、Phase Statusは原則`margpa-runtime-llm/docs/`を共通基盤とする。

会話内だけで重要Decisionを閉じない。ただしDocsへの記録はユーザー指示とTask Role Authorityの範囲内で行う。

## 5. Docs Read-only Principle

Docsを読み込む、参照する、引き継ぐ、確認する依頼は原則Read-onlyである。明示的なWrite指示またはRole Authorityがない限り、作成、編集、削除、Rename、Move、Status変更、正本差し替え、Link修正を行わない。

## 6. Filename／Timestamp／Language

Markdown文書は次の形式とする。

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

- 説明部分は英小文字／数字と`_`
- 末尾はAsia/Tokyoの作成時刻`YYYYMMDDHHMMSS`
- ADRは`adr_0001_...`形式
- 同一設計Snapshotの複数文書は同じTimestampを共有できる
- 本文は可能な限り日本語とする
- Model ID、Class名、Protocol、License、Definition識別子は正式表記を保持する

## 7. Required Metadata

各文書の先頭に可能な限り、文書ID、状態、作成日時、更新日時、Snapshot、担当、正本言語、関連文書、`supersedes`を記載する。

## 8. Append-Only

`docs/`は原則Strict Append-Onlyとする。

1. 作成済みDocsは原則変更しない
2. 内容変更時は新Timestampの新Fileを作る
3. 新Fileに`supersedes`を記載する
4. Documentation Indexも上書きせず新Timestampで作る
5. 古いIndexを残し、各時点のCurrent Setを再現可能にする
6. Handoff／Status／Reviewも毎回新規作成する
7. 古い文書へSuperseded表記を追記しない
8. 同一系列ではTimestampが最も新しいFileを最新とする
9. 最新`documentation_index_*`をCurrent Setの入口とする

## 9. Privacy／Security Exception

個人情報、Credential、Secret、公開不適切なLocal PathはAppend-Onlyより優先する。発見時は既存Fileを直接削除または匿名化できる。

例外適用時は、実値を再掲しない新規Scrub ReportとIndexを作り、歴史SnapshotがBitwise同一でなくなった事実を記録する。削除情報を復元・再掲しない。

詳細は[公開識別子・個人情報取扱方針](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)を正本とする。

## 10. Directory

```text
docs/
├─ requirements/  要件、制約、共通Rule、Role Authority
├─ architecture/  System構成、Model、Storage、Roadmap
├─ governance/    Governance、Audit、Evaluation、Security
├─ adr/           Decision、理由、代替案
├─ operations/    Backup、Snapshot、Restore、Release、Known Issues、Scrub Report
├─ user_manual/   内部User Manual／User Acceptance Test
├─ public/        将来の対外Public Docs
└─ handoffs/      Common／Designer／Implementer／External Handoff／Status／Review
```

## 11. Role Authority

```text
設計者:
  Requirements／Architecture／Governance／ADR／Operations
  User Manual／Index／Common／Designer Handoff／Review
  各担当の開始用Handoff

実装者:
  src／tests／scripts
  implementer_status_*
  config／Root FileはAccepted Handoff + ユーザー許可で条件付き

対外Docs作成者:
  README／docs/public/
  external_docs_status_*
  Canonical DocsはRead-only
```

設計者役と実装者役の分業はPhase 1の実運用で有効に機能した。対外Docs作成者役は本格的な実作業検証前である。

## 12. Review／Index Pairing

実装者Statusを設計者がReviewした場合、原則として同一Snapshotの`designer_review_<topic>_*`と`documentation_index_*`を作る。FindingがあってもReview依頼だけでSourceを修正しない。

非BlockerのFindingは最新`known_issues_and_observations_*`へStable ID、State、Severity、再現、影響、Disposition、再評価条件を記録する。

## 13. Handoff／Status Ownership

- `common_project_handoff_*`: 設計者
- `designer_handoff_*`: 設計者
- `designer_review_*`: 設計者
- `implementer_handoff_*`: 設計者が開始指示として作成
- `implementer_status_*`: 実装者
- `public_documentation_handoff_*`: 設計者が開始指示として作成
- `external_docs_status_*`: 対外Docs作成者

## 14. Phase Completion Backup

Backup Triggerは次の二重条件である。

```text
Gate A: 設計者役がPhase完了と次Phase移行可能を明示
Gate B: ユーザーが対象User Manual／Snapshotの受入テスト全項目合格を明示
```

両Gateが同一Project状態について成立した後、次Phaseの実質的変更前にBackupする。Material Changeが入った場合は影響範囲に応じReviewまたはUser Testを再実行する。

## 15. 公開前確認

Public Docs作成、Source Archive、Git／GitHub公開の直前にPrivacy Policyの公開前Gateを実行する。Git Author／Committer、外部Account、Repository設定は、ユーザーの別途許可なく変更しない。

<!-- SOURCE_END 6: docs/requirements/documentation_rules_20260720220216.md -->

---

<!-- SOURCE_BEGIN 7: docs/requirements/documentation_rules_20260720222402.md -->

### Source 7: `docs/requirements/documentation_rules_20260720222402.md`

- History Target: `docs/project/phases/phase_1/history/requirements/documentation_rules_20260720222402.md`
- Source SHA-512: `2f2410846e0d050374d2f74e47308ece4f59ae47e0f7fab49df92612e1627174840ddc622246af9d1e562ac7dc48a07a59f6c0db0e13a61fb39cace43fff98b6`
- Source Size: `4769` bytes

# 文書作成・命名・更新・権限共通ルール

- 文書ID: `documentation_rules`
- 状態: `current`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 適用範囲: `margpa-runtime-llm/docs/`以下の全文書と担当Task間運用
- 正本言語: 日本語
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)
- Backup／Publication Policy: [phase_completion_backup_policy_20260720222402.md](../history/operations/phase_completion_backup_policy_20260720222402.md)
- Known Issues／Observations: [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)
- supersedes: `documentation_rules_20260720220216.md`

## 1. Project／Identity

```text
Project Root   : margpa-runtime-llm/
Project Name   : margpa-runtime-llm
Display Name   : MARGPA Runtime LLM
Internal Name  : Nazuna Research Governance LLM
Public Identity: Nazuna Research
```

相対PathはProject Root基準とする。第一者の作者、設計者、開発者、Maintainer等の固有名は`Nazuna Research`へ統一する。個人固有絶対PathをDocsやSourceへ記録しない。

## 2. Task間Communication／Read-only

要件、Decision、Progress、Review、Handoff、未解決事項、Phase Statusは原則`docs/`を共通基盤とする。

Docsの読込、参照、確認依頼は原則Read-onlyであり、明示的Write指示またはRole Authorityなしに編集、削除、Rename、Move、正本差し替えを行わない。

## 3. Filename／Timestamp／Language

```text
lower_snake_case_YYYYMMDDHHMMSS.md
```

- TimestampはAsia/Tokyoの`YYYYMMDDHHMMSS`
- 同一Snapshotの複数文書は同じTimestampを共有できる
- 本文は可能な限り日本語
- 正式なModel ID、Class、Protocol、License、Definition識別子は原表記を保持
- 先頭Metadataに文書ID、状態、時刻、Snapshot、担当、関連文書、`supersedes`を記載

## 4. Append-Only

1. 作成済みDocsは原則変更しない
2. 変更時は新Timestampの後継Fileを作る
3. 後継Fileに`supersedes`を記載する
4. Index、Handoff、Status、Reviewも毎回新規作成する
5. 古い文書へSuperseded表記を追記しない
6. 最新Timestampを最新とする
7. 最新`documentation_index_*`をCurrent Setの入口とする

個人情報、Credential、Secret、公開不適切Pathの削除はPrivacy／Security例外として既存Fileへ直接適用できる。実値を再掲しないScrub ReportとIndexを残す。

## 5. Directory／Ownership

```text
requirements : 設計者
architecture : 設計者
governance   : 設計者
adr          : 設計者
operations   : 設計者
user_manual  : 設計者
handoffs     : File系列ごとの担当
public       : 対外Docs作成者
```

- 設計者はRequirements、Architecture、Governance、ADR、Operations、Manual、Index、Handoff、Reviewを担当する
- 実装者は`src/`、`tests/`、`scripts/`、`implementer_status_*`を担当する
- `config/`とRoot FileはAccepted Handoffとユーザー許可で実装者が変更できる
- 対外Docs作成者はREADME、`docs/public/`、`external_docs_status_*`を担当し、Canonical DocsはRead-onlyとする
- Implementer Statusを設計者がReviewした場合、ReviewとIndexを同一Snapshotで作る

## 6. Phase Backup／GitHub公開

Phase Backupは次の両Gate後に行う。

```text
Gate A: 設計者のPhase完了／次Phase着手可能宣言
Gate B: ユーザーの受入テスト合格宣言
```

原則、各PhaseのBackup確定後に同一SnapshotをGitHubへ反映する。初回だけはPhase 1-ex「運用再整備」完了後までGitHub公開を延期する。

毎回、Backup Candidate内の`margpa-runtime-llm/`から`.DS_Store`、`.venv`、Model、Symlink、Cache、Bytecode、Coverage、Secret、Local Data等の不要物を除去し、Inventory、Privacy、SHA-512、Restoreを検証してからBackupを確定する。

詳細は[Phase完了Backup／GitHub公開運用Policy](../history/operations/phase_completion_backup_policy_20260720222402.md)を正本とする。

## 7. Phase 1-ex

Phase 1と初回GitHub公開の間にPhase 1-ex「運用再整備」を追加する。詳細は未定義であり、[要件プレースホルダー](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md)から後続定義する。

## 8. Authorization Boundary

Docsへの要件記録だけではSource変更、Backup生成、Git操作、GitHub操作、外部環境操作、公開を許可しない。

<!-- SOURCE_END 7: docs/requirements/documentation_rules_20260720222402.md -->

---

<!-- SOURCE_BEGIN 8: docs/requirements/generic_governance_definition_platform_requirements_20260719112304.md -->

### Source 8: `docs/requirements/generic_governance_definition_platform_requirements_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/requirements/generic_governance_definition_platform_requirements_20260719112304.md`
- Source SHA-512: `acceaef92cd0b689429ce4f2b8ca0c16a0bbd61687dc13fac3a3d2a33e8ce8eb6419b696a85797cae3cbb4f20156f5abbec40d4effd80499a0fe79756306a5c3`
- Source Size: `12216` bytes

# 汎用Governance Definition Platform要件

- 文書ID: `generic_governance_definition_platform_requirements`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 3 Generic Governance Definition Platform
- 正本言語: 日本語
- 上位要件: [post_phase_1e_research_platform_requirements_20260719112304.md](../history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md)
- 関連Catalog: [governance_definition_catalog_20260719112304.md](../history/governance/governance_definition_catalog_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- supersedes: なし（新規要件系列）

## 1. 最重要原則

Governance DefinitionはRuntimeの任意Pluginであり、Boot Dependencyではない。

Runtime Coreは、次のいずれも前提にしない。

- GDの名前
- GDの数
- ARGD／DAGD／CDOGDの存在
- File名やDirectory構造
- JSON Schemaの単一性
- Domain、Category、Point IDの固定一覧
- Definition Repositoryの存在

ARGDとDAGDも例外にしない。JSONが1個もない状態を正式なBaselineとし、Main Model Runtimeが正常に動作することを必須とする。

## 2. 必須の入力状態

少なくとも次の全状態を考慮する。

1. Definition Sourceが未設定
2. Definition Directoryが存在しない
3. Definition Directoryはあるが空
4. ManifestはあるがEntryが0件
5. 0 byte Fileがある
6. `{}`だけのJSONがある
7. 無関係なJSONがある
8. 日本語名または任意名のJSONがある
9. 未知SchemaのJSONがある
10. Manifestが指すAdapterがない
11. 複数Versionの同一Definition IDがある
12. Duplicate Identityがある
13. Dependency不足、Conflict、Hash不一致がある
14. ARGD／DAGDの複合Source JSONがある
15. 標準Envelopeを持つCustom Definitionがある
16. Custom SchemaとTrusted Adapterの組み合わせがある

どの状態も、理由のないProcess Crash、暗黙のEnforcement、名前からの自動解釈を起こさない。

## 3. Empty Baseline

### 3.1 Default

```toml
[governance]
enabled = false
definition_sources = []

[components.main_model.governance]
mode = "off"
```

### 3.2 動作

Definition 0件、Governance OFFで次が正常に動作する。

- Model Load／Unload
- Generate
- Streaming
- Cancel
- Response Language
- Generation Config
- CLI／将来のAPI

この場合、Governance由来の負荷は次とする。

```text
Definition Load        : 0
Governance Model Call  : 0
Governance Prompt      : 0
Governance Token       : 0
Governance Repair      : 0
```

Statusは次の意味を明示できる。

```text
governance_state : governance_disabled
definitions      : 0
```

## 4. Repository State

Repository全体の状態は、少なくとも次を区別する。

| State | 意味 |
|---|---|
| `unconfigured` | Sourceが設定されていない |
| `empty` | 有効なDefinition Entryが0件 |
| `ready` | 1件以上の利用可能Definitionがある |
| `degraded` | 一部にInvalid／Unsupported／Conflictがあるが、利用可能な部分がある |
| `error` | Source自体が読めない、またはRequired条件を満たせない |

判定原則：

- 任意Directoryがない場合は`unconfigured`または`empty`であり、それだけでFatal Errorとしない。
- 空Directoryは`empty`とする。
- Malformed JSONは`empty`ではなく`degraded／invalid_json`とする。
- Permission等で設定済みSourceにAccessできない場合は`error`とする。

## 5. ModeとDefinition 0件の組み合わせ

| Mode | Definition 0件時の必須動作 |
|---|---|
| `off` | Pass-throughで正常動作する |
| `observe` | `inactive_no_definitions`とWarningを記録する。BindingがRequiredならError |
| `enforce` | Required Governance Missingとして安全側に拒否／Error。Enforce成功と記録しない |

Modeが`enforce`であるだけで、Definitionの存在、Compile成功、Rule適用、Action実行を假定しない。

## 6. 汎用Contract要件

特定GDごとのLoader／ClassをCoreに追加する方式を禁止する。次の汎用Conceptを用いる。

- `GovernanceDefinitionProvider` Port
- `EmptyDefinitionProvider`
- `FilesystemDefinitionProvider`
- `GovernanceDefinitionRegistry`
- `GovernancePackageManifest`
- `GovernanceDefinitionDescriptor`
- `GovernanceDefinitionAdapterRegistry`
- `GovernanceDefinitionCompiler` Port
- `NormalizedGovernanceIR`
- `CompiledGovernancePlan`
- `GovernanceBinding`
- `GovernancePoint`
- `GovernanceRepositoryState`
- `GovernanceExecutionResult`

`EmptyDefinitionProvider`はTest Dummyではなく、0件Baselineを表現する正式なProduction Implementationとする。

## 7. SchemaとAdapter

任意JSONは、存在するだけでGovernanceとして解釈できない。次のPipelineを必須とする。

```text
Raw JSON
  ↓ Definition Adapter
Standard Descriptor
  ↓ Normalization
Normalized Governance IR
  ↓ Compiler
Compiled Governance Plan
```

初期Adapter候補：

1. Legacy ARGD／DAGD Adapter
2. Standard GD Adapter
3. Generic Declarative Rule Adapter
4. 将来のTrusted Custom Adapter

Custom Adapterは実行Codeであり、JSONとは別のTrusted Pluginとして登録する。JSONがCode、Module Import、Shell Command、Network Fetchを指示することは認めない。

## 8. Discovery要件

### 8.1 Manifest First

Package Manifestによる明示登録を推奨する。

Manifestは最低限、次を持つ。

- Package ID／Version
- Definition ID／Version
- Relative Path
- Expected Digest
- Schema ID
- Adapter ID
- Required／Optional Dependency

### 8.2 Content Discovery

標準Envelopeを持つJSONに限り、Content-based Discoveryを将来許容できる。

### 8.3 禁止事項

- File名の`aisgd`を見てSecurityと決めない。
- File名の`cdogd`を見てOrchestratorと決めない。
- Directory名の`ordinary`、`orchestration`をRuntime Semanticsにしない。
- 名前や作者推奨PathをCapabilityの根拠にしない。

明示Binding、Descriptor、Capabilityが正本である。

## 9. Package Layout

次は推奨例であり、Runtime Contractではない。

```text
definitions/
  packages/
    margpa_foundational/
      manifest.toml
      argd_v0.3.1_en_dagd_v0.4.4_en.json
    nazuna-research_domain_extensions/
      manifest.toml
      definitions/...
    custom/
      manifest.toml
      definitions/...
```

`definitions/`全体が空、`packages/`がない、Custom ProviderがFilesystemを使わない、という構成も有効とする。

## 10. Standard Descriptor

Descriptorは次の情報を表現できる。

- Provider ID
- Package ID／Version
- Namespace
- Definition ID／Version／Digest
- Schema ID／Adapter ID
- Display Name
- Domain Tag
- Capability
- Dependency／Conflict
- Recommended Point
- License／Author
- Validation State
- Activation Metadata

Domain Tag、Capability、Point IDは拡張可能なStringとし、Core内のClosed Enumで全世界を固定しない。

## 11. Definition State

個別Definitionに少なくとも次の状態を持てること。

```text
available
active
inactive
disabled
missing
empty
invalid_json
invalid_schema
unsupported_schema
adapter_missing
hash_mismatch
duplicate_identity
dependency_missing
conflict
incompatible
quarantined
```

- Manifestに記載されない無関係JSON、または標準EnvelopeのないJSONは無視できる。
- Manifestで明示登録されたがSchemaまたはAdapterを理解できない場合は、黙って読み替えず`quarantined／unsupported_schema／adapter_missing`とする。
- Invalidな1件が任意Package全体やMain Model Runtimeを無条件にCrashさせない。

## 12. Security制約

- JSONをDataとしてのみ扱う。
- Code Execution、Shell、Dynamic Import、自動URL Downloadを禁止する。
- Configured Root外へのPath Traversalを禁止する。
- File Size、Nesting Depth、Rule Count、Prompt Size、Compiled Plan Sizeに上限を設ける。
- Digestを検証し、Duplicate Identityは明示的に拒否する。
- Unknown Actionは実行しない。
- Adapter PluginはJSON Packageより高いTrustと明示的なInstall／Registrationを必要とする。

## 13. CDOGDとOrchestration

- CDOGDは任意Definitionの1つであり、Coreの必須Dependencyではない。
- CDOGDがなくてもManual Binding、Static Routing、User-selected Profileは動作する。
- Dynamic Routingは、Orchestration Capabilityを持つActive Definitionが存在する場合にのみ有効化できる。
- CDOGD以外のCustom Definitionが同等のCapabilityを申告する場合、交換可能である。
- CDOGDという名前だけでDynamic Routing Capabilityを付与しない。
- Dynamic Routing自体はPhase 9まで延期する。

## 14. ARGD／DAGDの扱い

- 現在の参照SourceはARGD v0.3.1とDAGD v0.4.4をTop Levelの`argd`と`dagd`に持つ複合JSONである。
- SourceはByte-for-byteで保存し、SHA系DigestとLicense／Author／Versionを記録する。
- Runtime上ではLegacy Adapterが2つのStandard Descriptorへ展開できる。
- 正式に分離されたSourceがない限り、利便性のために原本JSONを独自分割しない。
- `margpa_foundational`等のPackageはDefault提供候補ではあるが、Coreに必須ではない。
- ARGD／DAGDの名前をCore Class、Required Profile、Fixed Pointにハードコードしない。

## 15. Source不変・Adjustment要件

Definition Source JSONをRuntime調整のために書き換えない。

```text
Immutable Definition Source
  + Package Manifest
  + Runtime Adjustment Profile
  + Binding
  + Compiler Version
  ↓
Compiled Governance Plan
```

Adjustment Profileは次を持てる。

- Activation
- Include／Exclude Rule
- Priority
- Soft Weight
- Threshold／Severity
- Mode
- Semantic Evaluator Selection
- Model Call／Token／Latency／Repair Budget
- Action Mapping
- Status Verbosity

Ruleは少なくとも次に分類する。

| Rule Class | Adjustmentの扱い |
|---|---|
| Hard Constraint | Runtime Profileで無効化・弱化しない |
| Structural Rule | 依存と整合する範囲で選択可 |
| Soft Rule | Weight／Threshold調整可 |
| Advisory Rule | 記録・推奨中心 |

Adjustmentは、存在しないPolicy、Authority、Approval、Capabilityを生成しない。

## 16. Identity／Audit要件

次を個別にIdentityとDigestで記録する。

- Raw Definition Source
- Package Manifest
- Standard Descriptor
- Adapter ID／Version
- Normalized IR
- Adjustment Profile
- Compiler ID／Version
- Compiled Plan
- Governance Point
- Binding
- Evaluation Result
- Recommended Action
- Executed Action

## 17. Test Matrix

### 17.1 Discovery／Validation

- Missing Directory
- Empty Directory
- Empty Manifest
- 0 byte File
- `{}`
- Unrelated JSON
- Arbitrary／Japanese Filename
- Unknown Schema
- Adapter Missing
- Duplicate Identity
- Same ID with Multiple Versions
- Hash Mismatch
- Dependency Missing
- Conflict

### 17.2 Compatibility

- Combined ARGD／DAGD Source
- Standard Custom Definition
- Custom Schema + Trusted Adapter
- Custom Point ID
- CDOGD Absent
- Custom Orchestrator Capability

### 17.3 Runtime Mode

- Zero Definition + OFF
- Zero Definition + OBSERVE
- Zero Definition + ENFORCE
- Optional Binding + Missing
- Required Binding + Missing
- Unknown Action
- Invalid DefinitionとValid Definitionの混在

## 18. 第一拡張受入シナリオ

1. Definition 0件でMain Model RuntimeとExperiment Baselineが動作する。
2. 任意名のJSON 1個、Manifestまたは標準Envelope、Adapter、Profile、Bindingを追加する。
3. Runtime Coreの改修なしで、そのDefinitionがDiscovery、Validation、Compile、Point実行に参加する。
4. Definitionを外すと、0件Baselineに戻る。
5. それぞれのRun Recordから、構成差と負荷差を再現できる。

## 19. Authorization Boundary

本文書はPhase 3の要件をAcceptedとするが、実装は未解禁である。今回行うのはDocs作成のみである。

<!-- SOURCE_END 8: docs/requirements/generic_governance_definition_platform_requirements_20260719112304.md -->

---

<!-- SOURCE_BEGIN 9: docs/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md -->

### Source 9: `docs/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md`

- History Target: `docs/project/phases/phase_1/history/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md`
- Source SHA-512: `f855561dc6a66db207450b3d89e8955f8a70d2e51b7bddad16fbc83da0760e6d9b622710d50264583e3dab4b62e9df700d4fbcad8368526eea66223747c7d62b`
- Source Size: `6833` bytes

# Lightning AI Studio Dual Runtime Profile要件

- 文書ID: `lightning_ai_studio_dual_runtime_profile_requirements`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 20:07:11 JST`
- 更新日時: `2026-07-19 20:07:11 JST`
- Snapshot: `20260719200711`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Lightning AI Studio Linux x86_64 Container、CUDA／CPU Profile
- 正本言語: 日本語
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719200711.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719200711.md)
- Handoff: [implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md](../history/handoffs/implementer_handoff_lightning_ai_studio_dual_runtime_profiles_20260719200711.md)
- supersedes: なし（新規Dual Profile要件系列）

## 1. Decision

Lightning AI Studioでは、GPU利用可能時とGPU利用上限到達／未割当時の両方を扱うため、次の2つのDeployment Profileを用意する。

```text
config/profiles/lightning_linux_x86_64_cuda.toml
config/profiles/lightning_linux_x86_64_cpu.toml
```

Profile Key候補：

```text
external.lightning-linux-x86_64.cuda
external.lightning-linux-x86_64.cpu
```

Tesla T4、Xeon 8488C等のHardware SKUはProfile名へ固定せず、Runtime Observation／Environment Reportへ記録する。

## 2. Confirmed Environment

```text
Service               : Lightning AI Studio
Operating System      : Ubuntu 24.04.4 LTS
Kernel                : Linux 6.8.0-1058-aws
Architecture          : x86_64
Execution Environment : Docker Container
Python                : 3.12.11
Logical CPU           : 4
Host RAM              : 15 GiB
Swap                  : 9 GiB
GPU                   : NVIDIA Tesla T4
GPU VRAM              : 15,360 MiB
Driver                : 580.159.03
CUDA Runtime          : 13.0
CUDA Toolkit／nvcc    : 13.0／V13.0.88
```

Python 3.12.11は、ProjectのPython 3.13.14 Primaryに対するNative Build互換性Fallback方針と整合する。環境差を隠さずEnvironment Reportへ記録する。

## 3. CUDA Profile Requirements

```text
host.os                    = linux
host.architecture          = x86_64
host.execution_environment = container
host.distribution          = ubuntu
compute.kind               = gpu
compute.vendor             = nvidia
compute.acceleration       = cuda
compute.memory_topology    = discrete
backend                    = llama_cpp
backend.build_variant      = cuda
load.gpu_layers            = -1
runtime.required_device    = gpu
runtime.required_api       = cuda
runtime.required_capability= gpu_offload
fallback                   = deny
```

Profile作成時の`verification_state`は`defined`とし、CUDA Build、Model Load、GPU Offload、Generation、Cancel、Unloadを実機で確認後にだけ`native_verified`の新しいProfileへ進める。

## 4. CPU Profile Requirements

```text
host.os                    = linux
host.architecture          = x86_64
host.execution_environment = container
host.distribution          = ubuntu
compute.kind               = cpu
compute.acceleration       = cpu_native
compute.memory_topology    = cpu_ram
backend                    = llama_cpp
load.gpu_layers            = 0
runtime.required_device    = cpu
runtime.required_api       = cpu_native
runtime.required_capability= none
fallback                   = deny
```

CPU Vendor／SKUはStudio割当により変化し得るため、ProfileへIntel Xeon 8488Cを固定しない。

CPU ProfileのBackend Build Variantは実機確認で次から決める。

1. CUDA-enabled Buildを`gpu_layers = 0`でGPU未割当時にもCPU実行できる場合、同一Environmentを再利用する。
2. CUDA Library／Device不在によりImportまたはLoadが失敗する場合、CPU Build用Environment／Setup Recipeを分離する。

未確認の段階で、同一CUDA BuildによるCPU Fallbackを保証しない。

## 5. Profile Selection

初期版は暗黙Fallbackを行わず、利用者が明示Profileを選択する。

```bash
./.venv/bin/margpa-llm model-info \
  --profile config/profiles/lightning_linux_x86_64_cuda.toml
```

```bash
./.venv/bin/margpa-llm model-info \
  --profile config/profiles/lightning_linux_x86_64_cpu.toml
```

理由：

- Current Platform Registryは同じHost Keyへ複数Defaultを登録できない。
- GPU Quota、GPU未割当、Driver異常、VRAM不足を同一の「CPUへFallback可能」と黙って解釈しない。
- Experiment再現性のため、使用ProfileとCompute Targetを明示する。

将来、Hardware ObservationとExplicit Fallback Chainが成立した後に`auto`選択を追加できる。

## 6. Required Runtime Follow-up

TOML追加だけでは不十分であり、次を同じ実装Scopeに含める。

1. Docker／Container Execution Environment検出
2. Linux x86_64 Container ProfileとのPre-load整合
3. llama.cpp CUDA BuildのRuntime Detection
4. CUDA実行とCPU実行の分離
5. CUDA／CPU Setup Recipe
6. Linux Environment Verification
7. CUDA／CPU Native Smoke Test
8. Profile、Registry、Reference Integrity Test

Current Device DetectorはMetal以外をCPUとして扱うため、CUDA判定を追加しない限りCUDA ProfileはPost-load Validationで拒否される。

## 7. Load Defaults

初期候補：

```text
threads       : 4
threads_batch : 4
context_size  : Application Default 4096
use_mmap      : true
use_mlock     : false
```

Batch／Micro BatchはMac値を無条件に固定せず、CUDA／CPU Smoke時のMemory、Latency、安定性を見て決める。Qwen3-4Bだけでなく将来Model交換を考慮し、GPU SKU固有最適値をProfileの永続的事実と混同しない。

## 8. Acceptance Criteria

- Containerを`native`と偽って記録しない。
- CUDA Profileは実際に`device_kind = gpu`、`acceleration_api = cuda`、`gpu_offload = true`を申告する。
- CPU Profileは`device_kind = cpu`、`acceleration_api = cpu_native`、`gpu_offload = false`を申告する。
- GPU未割当時にCUDA ProfileがCPUへ黙ってFallbackしない。
- CPU ProfileでQwen3-4BをLoad／Generate／Stream／Cancel／Unloadできる。
- Model Artifact SHA-512をMacと一致確認できる。
- Python、Driver、CUDA、Build Variant、Device、VRAM、RAMをEnvironment Evidenceへ記録する。
- Mac Metal Profileと既存Testを壊さない。

## 9. Phase Boundary

本設計は後続Core PhaseをBlockしない。Phase 1 Backup前に未検証Linux Profileを混入させず、Lightning対応Phaseで実装・Native検証する。

## 10. Authorization Boundary

本要件は設計Decisionを記録する。Config／Source／Tests／Setup Recipe変更、Lightning上のInstall、Build、Model Upload／Download、GPU利用は、ユーザーによる実装開始許可後に行う。

<!-- SOURCE_END 9: docs/requirements/lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md -->

---

<!-- SOURCE_BEGIN 10: docs/requirements/lossless_phase_document_compilation_requirements_20260720231036.md -->

### Source 10: `docs/requirements/lossless_phase_document_compilation_requirements_20260720231036.md`

- History Target: `docs/project/phases/phase_1/history/requirements/lossless_phase_document_compilation_requirements_20260720231036.md`
- Source SHA-512: `c1ee5cdd6e02c4b888d5706f6030f419198066b94c7738e5c50299a41ecc8b774c5150e694bde9a342d125b308d8f5fea39a26b444568d77bcbe2afd3e48227d`
- Source Size: `4733` bytes

# Phase単位Lossless Documentation Compilation要件

- 文書ID: `lossless_phase_document_compilation_requirements`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 実施予定担当: 対外Docs役
- 正本言語: 日本語
- supersedes: なし

## 1. 目的

Phase完了ごとに、当該Phaseで新規作成または更新してきたDocsをPhase単位の1Fileへ再整理する。

統合文書は次の両方を満たす。

- GitHubで人に見せても問題がない
- Codex Taskを作り直しても即時引き継ぎ可能な粒度を持つ

ただし、運用、共通ルール、権限、Task間情報伝達、要件、Accepted Decision等を勝手に要約、意訳、再解釈してはならない。

## 2. Lossless Principle

Phase統合はSummary Rewriteではなく、Lossless Compilationとする。

```text
Source Documents
  ↓ exact copy + external metadata
Phase Compilation Document
  ↓ extraction verification
Original Bytes Reproducible
```

元本文の内容、用語、口調、順序、Decision、Boundaryを変更しない。

## 3. `verbatim_required`対象

- 運用規則
- 共通ルール
- Task間Handoff
- Role Authority／Write Authority
- Requirements／Acceptance Criteria
- Accepted ADR／Decision
- Architecture Boundary
- Authorization Boundary
- Backup／Git／公開Policy
- Privacy／Security Rule
- Model／Environment／Path情報
- Known Issues／未解決事項
- Review Finding／Test Evidence

## 4. 禁止事項

- 要約
- 意訳
- 再解釈
- 読みやすさを理由とした書き換え
- 用語、口調、表記の無断統一
- 重複の勝手な削除
- 矛盾の勝手な解消
- 新旧記述の無断選別
- 複数文書を混ぜた新しい結論の生成
- Authorization Scopeの拡大または縮小
- 数値、Version、Hash、Path、Stateの変更

## 5. 許可される追加

元本文の外側に限り、次を追加できる。

```text
Source File
Source Document ID
Source State
Source Timestamp
Source Size
Source SHA-512
BEGIN SOURCE
<元内容そのまま>
END SOURCE
```

新旧文書や矛盾文書は双方の本文を保持し、`current`、`historical`、`superseded`、`conflicting`等の状態を外側のManifestで示す。

## 6. Deterministic Compilation

1. Phase対象Source SetをFreeze
2. Path、Size、SHA-512、Document ID、StateをInventory化
3. 決定論的な順序を定義
4. Source本文を変更せず統合
5. 統合Fileから各Source Payloadを再抽出
6. 再抽出PayloadのByte Size／SHA-512を元Sourceと比較
7. 全件一致時だけCompilation Pass
8. 統合File自身のSHA-512とSource Manifestを記録

1件でも不一致ならFail Closedとし、対外Docs役が修正を推測せず設計者役へ返す。

## 7. Public Safetyとの両立

公開不可情報を統合中に書き換えてはならない。次のいずれかを選ぶ。

1. Sourceを正式なPrivacy Scrub工程で先にSanitizeする
2. 公開不可SourceをFile単位で除外し、Path、Hash、除外理由をManifestへ記録する
3. 内部用Lossless Compilationと公開用Derived Documentを分離する

Credential、個人情報、Private Pathを保持するためにLossless原則を利用してはならない。Privacy／Security削除は既存Policyどおり優先するが、削除は統合工程の外で明示的に行う。

## 8. Derived Public Docsとの分離

次は説明用Derived Docsであり、要約・編集可能である。

- `README.md`
- `overview_ja.md`
- `concept_ja.md`
- `roadmap_ja.md`

一方、Phase Compilation、共通ルールCompilation、Handoff CompilationはLosslessを必須とする。Derived DocsをCanonical RequirementsやLossless Handoffの代替にしない。

## 9. Review Gate

- 対外Docs役: Compilation実施、Manifest、Public Safety Scan
- Phase設計者役: Phase内Source Setと内容整合を確認
- 将来の設計統括者役: Cross-Phase RuleとCurrent Setを確認
- ユーザー: 必要に応じて公開前受入

現在のPhase 1-ex前は、設計者役がReview責務を持つ。

## 10. Timing

```text
Phase Test完了
  → Phase Review
  → Lossless Compilation
  → Derived Public Docs更新
  → Privacy／Integrity Review
  → Phase Final Gate
  → Backup
  → GitHub反映
```

統合文書がBackup対象である場合、Backup確定後に内容を変更しない。

## 11. Authorization Boundary

本書はPhase 1-ex以後の要件予約である。現在のDocs統合、既存Docs削除、Git操作、Public Docs生成、Script実装、Directory変更を許可しない。


<!-- SOURCE_END 10: docs/requirements/lossless_phase_document_compilation_requirements_20260720231036.md -->

---

<!-- SOURCE_BEGIN 11: docs/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md -->

### Source 11: `docs/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md`
- Source SHA-512: `a82b26a44d0bb8002634c0a164155790f8197111f143ad853d92c1a824a6595b9926537aa18a82ac3aae9061f2a25671eef80d11e80eb8296046c3703de1a72a`
- Source Size: `3154` bytes

# Phase 1 ユーザー受入Follow-up要件

- 文書ID: `phase_1_acceptance_follow_up_requirements`
- 状態: `proposed_waiting_implementation_authorization`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象: CLI HelpとHidden Thinking Token上限診断
- 正本言語: 日本語
- User Test補足: [phase_1_user_acceptance_findings_20260719195134.md](../history/user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- Handoff: [implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md](../history/handoffs/implementer_handoff_phase_1_acceptance_follow_up_20260719195134.md)
- supersedes: なし（新規Follow-up系列）

## 1. Scope

実装候補は次の2件に限定する。

1. CLI Helpで大文字表記が仮引数名であることを説明する。
2. Hidden ThinkingがToken上限へ到達しFinal Answerを生成できなかった場合、Safe Warningを表示する。

Final先頭空行の正規化、Reasoning Language強制、一般Cross-platform完成は本Follow-upに含めない。

## 2. CLI Help要件

- Top-level、`generate`、`model-info`のHelpで、Usage中の大文字が実際の値へ置き換える仮引数名であると理解できること。
- `--profile`はSubcommand後へ置くことが分かること。
- `--profile PROFILE_PATH`のように意味のあるMetavarへ変更してよい。
- Optionの機能、値の例、Default／Sourceを過不足なく説明する。
- Help表示だけでModelをLoadしない。
- Helpの終了Codeは0を維持する。

## 3. Token上限Warning要件

- Thinking Executionが有効であること。
- Reasoningが非表示であること。
- Final Answerが生成されていないこと。
- Token上限到達を示す信頼できるStop Evidenceがあること。

上記を満たす場合だけ、Reasoning本文を含まないSafe Warningを表示する。

日本語の意味：

```text
最終回答を生成する前にToken上限へ到達しました。
```

要件：

- Raw Reasoningを表示しない。
- User Cancel、Model Error、正常な空回答をToken上限として誤分類しない。
- Streaming／Non-streamingの両方で意味が一致する。
- Warning出力先とExit CodeをTestで固定する。
- Model PortのCanonical OutputをPresentation都合で書き換えない。
- `--max-new-tokens`増加等の利用者向け対処をManualへ記載する。

## 4. Acceptance Criteria

- CLI Help Testが追加される。
- Correct／Incorrect `--profile`順序のBehaviorが維持される。
- Hidden Thinking＋Token上限でSafe Warningが出る。
- Hidden Thinking＋Final到達時はWarningが出ない。
- Visible Thinking、Thinking Disabled、Cancel、Errorで誤Warningが出ない。
- Default Test、Model Smoke、Ruff、MypyがPassする。
- 実装者Statusと設計者Reviewを新Timestampで作成する。

## 5. Authorization Boundary

本書とHandoffの作成だけでは実装開始を許可しない。ユーザーが実装担当へFollow-up開始を指示した後にSource／Testsを変更する。

<!-- SOURCE_END 11: docs/requirements/phase_1_acceptance_follow_up_requirements_20260719195134.md -->

---

<!-- SOURCE_BEGIN 12: docs/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md -->

### Source 12: `docs/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md`
- Source SHA-512: `d5309f6c1d3eaba6782a8e6e3f2138782261069aaa80a78a657a199034730f5c92177e7da55939bc880965ea0685493f5bce35c3370da5180439c9ffdd3011ec`
- Source Size: `19144` bytes

# Phase 1-ex 運用・Documentation・公開再整備 総合要件

- 文書ID: `phase_1_ex_complete_operating_model_and_documentation_requirements`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 15:50:20 JST`
- 更新日時: `2026-07-21 15:50:20 JST`
- Snapshot: `20260721155020`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- Architecture: [phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md](../history/architecture/phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md)
- ADR: [adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md](../history/adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md)
- Lossless Compilation: [lossless_phase_document_compilation_requirements_20260720231036.md](../history/requirements/lossless_phase_document_compilation_requirements_20260720231036.md)
- 公開名義・Access・License: [phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md](../history/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md)
- Phase 10 R&D Hook: [phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md](../history/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)
- supersedes: `phase_1_ex_operations_reorganization_requirements_20260720231036.md`

## 1. 文書の目的

本書は、これまで複数文書と会話で予約されたPhase 1-exの実施内容を、実行前の総合要件として再統合する。

Phase 1-exは機能追加Phaseではなく、MARGPA Runtime LLMを継続開発、Task分業、Backup、Git、GitHub公開、将来の長期研究開発へ耐えられる運用状態へ移行するPhaseである。

既存の詳細Policy、ADR、Lossless Compilation要件、公開名義・License要件は引き続き有効である。本書はそれらの内容を縮小せず、Phase 1-ex全体の親入口を提供する。

## 2. Phase Identity

```text
Phase ID      : Phase 1-ex
Name          : 運用再整備
Position      : Top-level Phase 1完了後／初回GitHub公開前
Type          : Operations／Documentation／Repository Transition
State         : Accepted Reservation／Not Started
Primary Goal  : 継続開発可能で公開可能な確定運用へ移行する
```

## 3. 現在の非実行境界

ユーザーがPhase 1-ex開始を明示するまでは、次を実行しない。

- 設計者役から設計統括者役への変更
- Phase別設計者Taskの新設
- 役割権限の実変更
- Git初期化、Commit、Tag、Remote設定、Push
- DocsのMove、Rename、削除、Directory Migration
- Stable Canonical Docs、README、LICENSE等の実生成
- Lossless Compilationの実行
- 公開用Staging Treeの生成
- GitHub公開
- Phase 10 R&D機構の実装または統合

現在のAppend-only、Timestamp、Role Authority、Directory構造を維持する。

## 4. Phase 1-ex開始前提

Phase 1-exは、Top-level Phase 1の完了条件と順序を満たした後に開始する。

最低限の前提：

- Phase 1-AからPhase 1-Hまでの対象ScopeがAcceptedである。
- Mac User Acceptanceが合格している。
- Lightning Mandatory Gateと公開UI GateのDispositionが確定している。
- Current User ManualがPhase 1機能を反映している。
- 設計者役がPhase 1完了と次Phase着手可能を宣言している。
- ユーザーがPhase 1最終Test合格を宣言している。
- Phase 1確定SnapshotのBackup要否と実行順が確定している。

Phase 1-ex実行中にPhase 1機能へMaterial Changeが入った場合、必要なReviewとUser Acceptanceを再実行する。

## 5. 役割・Authority再整備

Phase 1-exで次の役割を正式に再整理する。

```text
設計統括者役
Phase別 設計者役
実装者役
対外Docs役
```

### 5.1 設計統括者役

現在の設計者役を、Phase 1-ex内で設計統括者役へ変更する。

責務：

- Project全体要件、Architecture、Phase構成
- Cross-Phase整合
- 共通Port、Governance Core、Security／Privacy Boundary
- Accepted ADR／Policy管理
- Phase開始用上位設計とHandoff
- Phase最終Review、移行判定、Escalation判断
- Stable Canonical Docsの内容責任
- Project Continuity Masterの正本責任

### 5.2 Phase別設計者役

Phaseごとに専用設計者役Taskを配置可能にする。

- 設計統括者役から上位要件、制約、受入境界を受け取る。
- Phase内要件、Architecture、ADR、実装Handoffを具体化する。
- ユーザー要求またはEvidenceにより、上位設計から大きく外れない範囲で再設計できる。
- Cross-Phase影響、共通Policy変更、権限拡大は設計統括者役へEscalateする。

### 5.3 実装者役

- `src／tests／scripts`をStanding Scopeとする。
- `config／pyproject.toml／uv.lock／Root Metadata`はAccepted Handoffとユーザー許可を必要とする。
- Requirements、Architecture、Governance、ADR正本はRead-onlyとする。
- 実装またはFollow-upごとにStatusを作成する。

### 5.4 対外Docs役

- README、公開説明Docs、Phase Summary、CITATION、NOTICEを担当する。
- Lossless Phase Compilationを、決定論的なProcedureに従って実施する。
- Canonicalな技術内容をPublic向けに黙って変更しない。
- Stable Canonical Docsの編集作業を担当する場合も、内容Ownerの設計統括者役によるReviewを必要とする。
- LICENSEの権利条件はユーザー決定を必須とする。

### 5.5 Authority再定義対象

- DirectoryごとのStanding／Conditional Write Scope
- Read-only Scope
- Handoff、Status、Review、Index Ownership
- Git、Backup、Release、Public Export権限
- Phase開始／完了Gate
- Cross-Phase Escalation
- Canonical DocsとDerived Public DocsのOwner
- Project Continuity Masterの更新責任

## 6. Git移行

Phase 1-exからGit運用へ移行する。

Phase 1-exで次を要件定義し、検証してから実行する。

- Repository初期化Point
- Initial Commit Allowlist
- Branch Strategy
- Commit単位、Message規則
- Phase Tag／Release規則
- Backup Snapshot、Manifest、Commit、Tagの対応
- Dirty State Gate
- Remoteと公開Repositoryの対応
- Commit Author／Email／Account帰属
- `.gitignore`、Secret Scan、Binary／Model除外
- Rollback／Restore
- Public Staging TreeとDevelopment Treeの関係
- Git HistoryとDocs Historyの役割分担

公開Repository：

```text
Owner       : margpa-labs
Repository  : margpa-labs/margpa-runtime-llm
Author Name : Nazuna Research
```

Commit Author Nameは`Nazuna Research`とする。Commitから個人GitHub Accountへ辿れることは許容するが、個人EmailやAccount HandleをDocsへ不要に記録しない。

## 7. Documentation運用移行

### 7.1 Filename／Language

Phase 1-ex後に新設または移行するDocsのFile名とDirectory名は英語を使用する。

```text
File／Directory Naming : English／lower_snake_caseを基本
Japanese Body          : Required by default
Language Suffix        : _ja
```

Model ID、Protocol、Class、License、Definition ID等の正式識別子は原表記を保持する。

### 7.2 Git移行前後の履歴モデル

```text
Before Git
  → Timestamp付きAppend-only Docs

After Git
  → Stable Canonical Filenameを更新
  → Git Historyが差分履歴を保持
  → Immutable Phase Compilationは別Artifactとして保持
```

既存Timestamp DocsはHistorical Evidenceとして削除しない。Stable Docsへ再整理したことを理由に、元文書を破壊、上書き、無断要約しない。

### 7.3 Directory Migration

移行前に次を作成する。

- Current File Inventory
- Target Directory Tree
- Current／Historical／Superseded／Conflicting分類
- Move／Keep／Compile／Exclude Manifest
- Relative Link更新計画
- Write Authority Mapping
- Validation Procedure
- Rollback Plan

Directoryを先に変更し、その後に正本関係を考えることを禁止する。

## 8. Stable Canonical Public Documents

Phase 1-exで、対外向け説明と技術正本を兼ねる次の5文書を作成する。

```text
docs/
├─ requirements_specification_ja.md
├─ system_architecture_ja.md
├─ technology_selection_ja.md
├─ basic_design_ja.md
└─ runtime_governance_specification_ja.md
```

### 8.1 `requirements_specification_ja.md`

- Project目的、利用対象、Scope
- 機能要件
- 非機能要件
- Platform／Resource制約
- Security／Privacy／Audit要件
- Model／Governance交換性
- Phase境界、Out of Scope、受入条件
- 未実装機能と将来要件の明示

### 8.2 `system_architecture_ja.md`

- System全体構造
- Layer／Module責務
- Dependency方向
- Application Core、Adapter、Port
- Local／Lightning／Cloud／Hybrid配置
- Data／Control／Event Flow
- Trust／Authority Boundary
- Future External R&D Extension Hookの配置

### 8.3 `technology_selection_ja.md`

日本語文書名は「技術選定書」とする。

- 採用技術、Version、Support Range
- 採用理由
- 不採用／保留候補と理由
- Platform／Backend互換性
- Canonical ModelとDeployment Artifact
- 将来の交換条件
- 関連ADRとの対応
- 既知のRiskと再評価条件

### 8.4 `basic_design_ja.md`

- API、UI、Config、Model、Storage、Governanceの基本構造
- 外部／内部Interface
- Module接続
- State、Error、Cancellation、Securityの基本方針
- Directory／Config／Schemaの基本設計
- 詳細実装へ渡すBoundary

詳細設計書はPhase 1-exの必須成果物にしない。既存Granular DocsとSourceを維持し、将来必要になったSubsystemだけ任意に作成する。

### 8.5 `runtime_governance_specification_ja.md`

- Runtime Governanceの目的と思想
- ARGD／DAGDの位置づけ
- GD 0件でも成立する構造
- 未知のGD、任意JSON、将来GDの汎用受入
- Registry、Loader、Validator、Compiler、Instance
- Shared Control Plane＋Distributed Governance Point
- `off／observe／enforce`
- Layer ON／OFF、依存、競合、Capability
- State、Score、Deviation、Severity、Action
- Audit、Evidence、Repair、Rebind、Enforce、Reinitialize
- 権限やPolicyを新しく生成しないBoundary
- Phase 10 External R&D Hook

### 8.6 作成原則

- 既存正本をSource Inventory化してから作る。
- 決定事項、未決事項、例外、Known Issueを混同しない。
- 未実装事項を実装済みと書かない。
- 読みやすさを理由にAccepted Boundaryを変更しない。
- Stable Docs間の重複は参照で抑制し、正本Ownerを明示する。

## 9. Derived Public Documents／Root Files

対外Docs役が次を作成または更新する。

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

- README本文は日本語の敬語とし、末尾にEnglish Abstractを置く。
- READMEへ実在するLightning公開URLを記載する。架空URLを置かない。
- LICENSEは英語正本を許容する。
- NOTICEは日本語と英語を使用する。
- CITATION.cffは英語でCFF 1.2.0へ準拠する。
- Overview、Concept、Roadmap、Phase Summaryは日本語とする。
- 将来`*_en`を追加可能とするが、現在は必須にしない。

Stable Canonical DocsとDerived Public Docsを混同しない。READMEやOverviewは説明用であり、Canonical Requirementsを置換しない。

## 10. Project Continuity Master

Taskを丸ごと新規作成しても即時再開できるよう、次を作成する。

```text
docs/project_continuity/
└─ project_continuity_master_ja.md
```

本Fileは公開可能なProject Continuity正本とする。

```text
classification : public_project_continuity
public_export   : true
github_public   : include
language        : Japanese
filename        : English
```

最低限、次を統合する。

- Project目的、思想、優先順位
- Current Phase、完了、未完了、保留
- 全ArchitectureとModule責務
- Model、Backend、Artifact、配置
- Platform、Python、Dependency、Deployment Profile
- Config構造、優先順位、Layer ON／OFF
- Runtime Governance全体
- Guardrail、Judge、Repair、Agent、RAG等の将来要件
- 役割、Write Authority、Handoff、Review、Index規則
- Docs、Git、Backup、Release、公開運用
- Public Identity、Repository、License Stage
- Accepted ADR／Decision
- Known Issues、未解決事項、再評価条件
- 次の作業、開始条件、禁止事項
- Task再開時の読込順序
- Source Document Map
- Phase 10 Original R&D Hook

単なる短い要約にせず、Decision、Boundary、例外、未決事項を分離する。運用規則等の意味を勝手に再解釈しない。

公開Fileであるため、個人Path、Credential、Secret、実会話Log、Private Artifactを含めない。公開可能性と継続性を両立する。

## 11. Lossless Phase Compilation

Phase完了ごとに、そのPhaseで作成されたDocsをPhase単位で再整理する。

これはSummary RewriteではなくLossless Compilationである。

- Source SetをFreezeする。
- Path、Document ID、State、Size、SHA-512をInventory化する。
- 元本文を変更せず格納する。
- 統合Fileから元Payloadを再抽出する。
- Byte SizeとSHA-512を比較する。
- 1件でも不一致ならFail Closedとする。
- 矛盾文書も勝手に解消せず、外部Metadataで状態を示す。

Privacy ScrubはCompilation外で明示的に行う。公開用Derived Docsと内部／公開Lossless Compilationの関係をPhase 1-exで確定する。

## 12. 公開名義・Privacy

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Project Internal Name        : Nazuna Research Governance LLM
Repository Owner             : margpa-labs
Public Repository            : margpa-labs/margpa-runtime-llm
```

公開候補から次を除外する。

- 法的氏名、個人連絡先、個人Profile
- 個人固有Absolute Path、Hostname、OS Account名
- Credential、Secret、Token、Private Key
- `.venv`、Model Weight、`models` Symlink
- Cache、Bytecode、Coverage、`.DS_Store`
- Local Log、実会話、RAG資料、Local Override

第三者の正式名称、Model ID、Repository、License、Citation、Hashは勝手に置換しない。

## 13. GitHub SourceとLightning UIのAccess境界

### GitHub

- 初期公開はEvaluation-onlyのSource-availableとする。
- Open Sourceとは主張しない。
- 閲覧、評価、Clone、Fork等の範囲をLICENSEで定義する。
- 商用、Production、再配布、派生物、AI Training等の扱いを明示する。

### Lightning Public UI

- 公開UIの通常機能は自由に操作、評価可能とする。
- Prompt、New Chat、公開設定、生成、停止、再試行を許可する。
- UI利用はSource再利用、Model取得、管理Access、妨害行為の権利を付与しない。

## 14. License Staging

初期Stage：

```text
Classification : Source-available／Proprietary Evaluation-only
Open Source     : No
Primary File    : LICENSE
```

一定の完成後、ユーザー判断でOSS化できる。OSS化対象Version、過去Release、Contributor権利、Third-party License、変更日を記録する。

Top-level LicenseをModel、ARGD／DAGD、第三者GD、Dependency等へ一括適用しない。

## 15. Backup／Phase-end／GitHub Sequence

```text
Implementation／Test完了
  → Designer Review
  → User Acceptance
  → Phase完了／次Phase着手可能宣言
  → Lossless Compilation
  → Stable／Derived Public Docs更新
  → Privacy／License／Integrity Review
  → Backup Candidate
  → Archive Sanitation
  → Manifest／SHA-512／Restore検証
  → Backup確定
  → Git Commit／Tag／GitHub反映
```

最終順序は既存Dual Gate Policyとの整合をPhase 1-exで確定する。BackupとGitHubは同一Source Snapshotを指す。

## 16. Public Archive／Repository Exclusion

公開TreeとBackup CandidateをAllowlist方式で作る。

除外対象：

```text
.venv/
models／models Symlink
*.gguf
.git/              # ZIPから除外。Git Repository自体では別管理
Cache／Bytecode／Coverage
.DS_Store
Credential／Secret
var／Local Runtime Data
Temporary／Editor File
Local Override
```

Modelは名称、Canonical Source、Artifact、Revision、Format、Quantization、SHA-512、配置手順だけをManifestへ残す。

## 17. Phase 10 Original R&D Hook

本体の一通りの完成後、別Project／別Taskで開発される次の独立R&D機構を疎結合統合できるHookを残す。

1. 例外認識型安全統治機構
2. 分散証跡型例外認識エージェント統治安全機構

Coreへ固有実装を依存させず、汎用External Governance Provider Port、Capability、Event、Evidence、Standard Resultで接続する。両機構が存在しなくてもMARGPA Runtime LLM本体は完全に動作する。

公開情報量と詳細は[Phase 10 R&D Hook正本](../history/governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)に従う。

## 18. Migration Validation

Phase 1-exでは最低限、次を検証する。

- InventoryとTarget Tree一致
- Relative Link Check
- Current／Historical正本解決
- Stable Docs相互参照
- Lossless再抽出とSHA-512一致
- Filename English／Body Japanese
- Public Identity／PII／Secret Scan
- Model／Binary／Symlink／Venv除外
- LICENSE／NOTICE／CITATION整合
- CFF Schema Validation
- Reproducible Setup
- Static／Unit／Integration／Native Test
- Archive Manifest／Restore
- Git Clean State／Commit／Tag対応
- Task Handoffからの再開試験
- 各担当TaskへのMigration通知

## 19. Phase 1-ex Completion Gate

次がすべて成立するまでPhase 1-ex完了を宣言しない。

- Role／Authority再編Accepted
- Git Workflow Accepted／実動作確認済み
- Docs Directory Migration完了
- Stable Canonical Docs 5件完成・Review済み
- Project Continuity Master完成・再開試験済み
- Public Root／Derived Docs完成
- Lossless Compilation Procedure合格
- Privacy、License、Attribution、Integrity合格
- Backup／Restore合格
- 全担当Taskへの新構造通知完了
- Rollback手順確認
- ユーザー最終受入
- 初回GitHub公開対象Commit／Tree確定

## 20. Out of Scope

- 詳細設計書の網羅的作成
- Phase 10 R&D機構そのものの実装
- 未公開のR&D Algorithm／核心部分の記述
- OSS化の即時実行
- Model WeightのRepository収録
- Phase 2以降の機能実装

## 21. Authorization Boundary

本書はPhase 1-exの総合要件予約を更新する。

本書作成だけでは、Phase 1-ex開始、Role変更、Git操作、Docs Migration、Stable Docs実生成、README／LICENSE等の生成、Backup、GitHub公開、Phase 10実装を許可しない。

<!-- SOURCE_END 12: docs/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md -->

---

<!-- SOURCE_BEGIN 13: docs/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md -->

### Source 13: `docs/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md`
- Source SHA-512: `87dd312c1b1669a1c1191de157e1d7b59b96c5b7bbe8cbaab6c51d6a96bcfe69900ab63af47be205a9f9e328a8805b363eacd12c7fa2488c6a4eef5d1d05cdf8`
- Source Size: `8104` bytes

# Phase 1-ex External Original R&D 公開・統合予約要件

- 文書ID: `phase_1_ex_external_r_and_d_publication_and_integration_requirements`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 16:22:42 JST`
- 更新日時: `2026-07-21 16:22:42 JST`
- Snapshot: `20260721162242`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Parent Requirements: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- System Catalog: [phase_10_original_r_and_d_system_catalog_20260721162242.md](../history/governance/phase_10_original_r_and_d_system_catalog_20260721162242.md)
- Integration Architecture: [phase_10_external_r_and_d_integration_architecture_20260721162242.md](../history/architecture/phase_10_external_r_and_d_integration_architecture_20260721162242.md)
- supersedes: なし（Phase 1-ex外部R&D公開・統合系列の初回）

## 1. 目的

Phase 1-exで作成する公開DocsとProject Continuity Masterへ、MARGPA Runtime LLM本体完成後に統合予定の3つのオリジナルR&D Systemを、正式名称付きで記録する。

3 Systemは別Project／別Taskで独立開発し、Phase 10でMARGPA Runtime LLMへ疎結合統合する。構想の存在と方向性は公開し、Algorithm、実装方式、研究の核心は現在開示しない。

## 2. Official Public Names

### 2.1 EASA

```text
Abbreviation  : EASA
English Name  : Exception Aware Safety Architecture
Japanese Name : 例外認識型安全統治機構
Research Area : AI Safety Governance
```

### 2.2 DLAGSA

```text
Abbreviation  : DLAGSA
English Name  : Distributed LEA Agentic Governance & Safety Architecture
Japanese Name : 分散証跡型例外認識エージェント統治安全機構
Research Area : Multi-Agent Governance,
                Distributed Accountability,
                and Safety Assurance
```

`LEA`の正式な意味を本Project側で推測、展開、再定義しない。正式表記をそのまま保持する。

### 2.3 OCILNS

```text
Abbreviation  : OCILNS
English Name  : Open Cognitive Interaction Ledger Network System
Japanese Name : 認知対話証跡台帳網
Research Area : Cognitive Interaction Provenance,
                Verifiable AI Systems,
                and Distributed Auditability
```

## 3. Public Summary

### EASA

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用を対象とし、例外を含む複合的な安全挙動を統治する独立R&D Architecture。

### DLAGSA

複数の判断・実行・検証主体間における責任、委譲、例外、改竄耐性付き証跡、全体整合および異常時の安全側制御を扱う独立R&D Architecture。

### OCILNS

人、AI、Tool、外部System間の認知的対話出来事を、後から検証、参照、継承、監査できる改竄耐性付き証跡単位として扱い、長期、分岐、多Model、多Thread環境でも再接続可能性を維持する独立R&D System。

## 4. Phase 1-ex Documentation Placement

### `docs/public/roadmap_ja.md`

各Systemについて次だけを記載する。

- 略称
- 正式英名
- 日本語名
- 研究領域
- 1から2行のPublic Summary
- Phase 10／別Project／疎結合統合予定

### `docs/system_architecture_ja.md`

- 3 Systemの外部配置
- EASA／DLAGSA用Generic Governance Provider Port
- OCILNS用Generic Evidence Ledger Port
- Optional／Core非依存
- Configによる個別ON／OFF

内部Algorithmや使用技術は記載しない。

### `docs/runtime_governance_specification_ja.md`

- EASA／DLAGSAをExternal Governance Providerとして扱う将来Hook
- OCILNSをEvidence／Ledger Providerとして接続できる将来Hook
- Standard Result、Event、Evidence Reference、Mode、Failure Boundary
- 固有Systemなしでも本体が成立する原則

### `docs/project_continuity/project_continuity_master_ja.md`

Public Summaryより少し詳しく、次を記録する。

- EASAのSafety Stack作業概念
- DLAGSAの複数主体、責任、委譲、検証、例外、改竄耐性付き証跡
- OCILNSの認知対話、長期／分岐／多Model／多Thread、継承、検証、改変検知、Provider非依存
- 3 Systemの独立開発、Phase 10、疎結合、ON／OFF
- 未公開の核心を推測または補完しない境界

### その他のCanonical Docs

- `requirements_specification_ja.md`：将来拡張要件として名称と任意統合を記載
- `basic_design_ja.md`：Generic PortとConfig境界だけを記載
- `technology_selection_ja.md`：本体側Adapter要件だけ。各R&D Systemの内部使用技術は記載しない

## 5. Config ON／OFF Requirement

EASA、DLAGSA、OCILNSを個別にON／OFFできるConfigをPhase 10統合時に持つ。

概念例：

```toml
[extensions.providers.easa]
enabled = false

[extensions.providers.dlagsa]
enabled = false

[extensions.providers.ocilns]
enabled = false
```

最終SchemaはPhase 10で決定する。上記KeyをCore Codeへ固定する指示ではない。Registry／Provider Definitionから設定を解決できる構造を優先する。

Mandatory Behavior：

- Defaultは3 SystemともOFFとする。
- 3 Systemを独立してON／OFFできる。
- OFF時はLoad、Network Call、External Write、評価、Side Effectを行わない。
- ProviderまたはRequired Capabilityがない状態でONにした場合、黙って無視せずSafe Error／Degraded／Refusalを返す。
- Effective Config、Provider ID、Version、Hash、Enabled StateをAudit可能にする。
- 将来UIへ出す場合は一般設定ではなく研究開発者向け設定に置く。
- System本体とSystem用Governance Pointの有効状態を必要に応じて分離する。

EASA／DLAGSAは、ON時に`observe／enforce`等のGovernance Modeを別設定として持てる。ON／OFFと介入Modeを同一視しない。

OCILNSは証跡記録／検証Systemであり、Governance介入Modeを無理に適用しない。OCILNS固有のOperation ModeはPhase 10側要件で定義する。

## 6. OCILNS Scope Boundary

OCILNSの目的はLLM応答精度の直接向上ではない。

対象は、認知的作業に関わる対話出来事を、後から再参照、再検証、再接続、継承、監査可能な状態で維持することである。

候補Evidence：

- Input／Output
- Event順序／時刻
- Model／Provider情報
- 人の意図
- AI応答
- Tool実行
- 判断根拠の高水準記録
- 制約／前提／補助情報
- 未解決事項
- 継承対象
- 改変検知情報

OCILNSは特定LLM Provider、保存先、UI、Cloud環境へ依存しない。単一SHA-512 Digestだけに依存しない改竄耐性構成を予定するが、具体方式は本書へ記載しない。

## 7. Integration Boundary

```text
EASA／DLAGSA
  → External Governance Adapter
  → Generic External Governance Provider Port

OCILNS
  → Evidence Ledger Adapter
  → Generic Evidence Ledger Port

MARGPA Core
  → Generic Ports only
```

- 固有PackageなしでMARGPA Coreが動作する。
- 外部System FailureがCoreを無条件に停止させない。Fail PolicyをConfigで明示する。
- 存在しない権限やPolicyを生成しない。
- ProviderなしのBaseline比較が可能である。
- 外部SystemのVersion、Definition、Evidence ReferenceをAuditへ残せる。

## 8. Public／Non-public Boundary

公開する：

- 名称、略称、正式英名、日本語名
- 研究領域
- Public Summary
- Phase 10、別Project、疎結合統合
- Config個別ON／OFF予定
- Generic Port上の位置

現在記載しない：

- 独自Algorithm
- 内部Data Structure／Protocol
- 改竄耐性の具体方式
- 評価方式の核心
- 非公開Repository、Path、実装情報

## 9. Authorization Boundary

本書はPhase 1-exの記載予約とPhase 10の統合要件予約である。3 Systemの実装、Config変更、Adapter追加、外部接続、Algorithm公開を現在許可しない。

<!-- SOURCE_END 13: docs/requirements/phase_1_ex_external_r_and_d_publication_and_integration_requirements_20260721162242.md -->

---

<!-- SOURCE_BEGIN 14: docs/requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md -->

### Source 14: `docs/requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md`
- Source SHA-512: `684f110667cae64404b331a71c4ed4175e5497804fa1dddb65c0329b83fff108f4d4423b872edf3bf1a501ae8648d4ad1e13ee4a223e9446c4052d396703cd88`
- Source Size: `11043` bytes

# Phase 1-ex完了までのDocumentation単一Writer／Roadmap最優先導線 要件

- 文書ID: `phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements`
- 状態: `accepted`
- 作成日時: `2026-07-21 19:19:15 JST`
- 更新日時: `2026-07-21 19:19:15 JST`
- Snapshot: `20260721191915`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- 適用開始: 本要件Accepted時点
- 適用終了: Phase 1-ex完了宣言時点
- 関連総合要件: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- 関連Lossless要件: [lossless_phase_document_compilation_requirements_20260720231036.md](../history/requirements/lossless_phase_document_compilation_requirements_20260720231036.md)
- 既存Role Policy: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- supersedes: なし（Phase 1-ex完了までの期間限定Override）

## 1. 決定

Phase 1-ex完了宣言までは、`docs/`配下に作成する全Documentationを、現在の設計者役担当Taskが単一Writerとして作成する。

これは、既存の役割別Write Scopeに対する期間限定Overrideである。

```text
適用期間:
  本要件Accepted
  ～ Phase 1-ex完了宣言

docs/ Writer:
  現在の設計者役担当Taskのみ

対象:
  docs/配下の全File
  Phase単位Lossless Compilation
  Root Public Docsの設計・作成
  README.md等のPhase 1-ex公開成果物
```

Phase 1-ex完了後のDocumentation Ownershipは、Phase 1-exで確定する新しいRole／Authority Policyに従う。現時点でPhase 2以後の永続的な単一Writer運用を確定しない。

## 2. 単一Writerの対象範囲

現在の設計者役担当Taskは、Phase 1-ex完了まで次をすべて作成する。

- Requirements
- Architecture
- Governance
- ADR
- Operations Policy
- User Manual
- Review
- Documentation Index
- Common Handoff
- Designer Handoff
- Implementer Handoff
- Implementer Statusの文書化
- External Docs Statusの文書化
- Public Docs
- Phase Summary
- Project Continuity Master
- Phase単位Lossless Compilation
- Documentation Migration Record
- Documentation Inventory／Manifest
- Phase 1-ex Completion Evidence
- README、LICENSE、CITATION、NOTICEに関するDocumentation

Rootに配置する次の公開成果物も、Phase 1-ex完了までは現在の設計者役担当Taskが作成する。

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
```

LICENSEの権利条件はユーザー決定を必須とし、設計者役担当Taskが独自にLicense条件を決めない。

## 3. 他担当Taskの扱い

### 3.1 実装者役

実装者役は、Source、Test、Script、許可されたConfig等の実装結果を、会話または明示された報告Payloadとして設計者役へ渡す。

Phase 1-ex完了までは、実装者役自身が`docs/handoffs/implementer_status_*`を含む`docs/`配下へFileを書き込まない。設計者役が、実装者役の報告を根拠としてStatus Documentを作成する。

実装者役の発言を文書化する場合、次を区別する。

- 実装者役が報告した事実
- 設計者役が独立確認した事実
- 設計者役の評価／Review
- ユーザーが確認した事実
- 未確認事項

設計者役は、実装者役の報告内容を勝手に成功扱いへ変更しない。

### 3.2 対外Docs役

対外Docs役は、Phase 1-ex完了までは`README.md`、`docs/public/`、`external_docs_status_*`を含め、Documentation Fileを直接作成しない。

必要な提案、構成案、校正案、公開観点の指摘は、会話または設計者役への入力として提出できる。最終的なFile作成、内容固定、Index反映は現在の設計者役担当Taskが行う。

### 3.3 将来の設計統括者役／Phase別設計者役

現在の設計者役を設計統括者役へ変更する処理は、既存決定どおりPhase 1-ex内で行う。

Phase 1-ex完了までのDocumentation単一Writerは、Role変更後も同一の現在Taskが継続する。Phase別設計者役を作成した場合でも、Phase 1-ex完了前はDocsへ直接書き込ませず、Documentation Payloadを設計統括者役へ返す。

## 4. 既存Policyとの優先関係

適用期間中、Documentation Write Ownershipについて矛盾がある場合は、本要件を優先する。

期間限定でOverrideする例：

- 実装者役による`implementer_status_*`直接作成
- 対外Docs役によるREADME／Public Docs直接作成
- 対外Docs役によるLossless Phase Compilation実施
- Phase別設計者役によるDocs直接作成

Overrideしない事項：

- Source／Test／Script等の実装Ownership
- ユーザーだけが決めるLicense条件
- ユーザーの外部操作権限
- Git／GitHub／Lightning操作のAuthorization Boundary
- Canonical Docsの意味内容
- Append-Only、Timestamp、Public Identity、Privacy Rule

## 5. Append-Only運用

Phase 1-exでDocumentation運用が正式移行されるまで、既存のAppend-Only規則を維持する。

- 作成済みDocsを原則変更しない。
- 内容変更時は新Timestampの新Fileを作る。
- 新Fileから旧Fileまたは影響対象を明示する。
- Documentation Indexも新Timestampで作る。
- 古いDocsと古いIndexを履歴として保持する。
- 新しいTimestampを最新とする。
- File名は英語と`_YYYYMMDDHHMMSS`を使用する。
- 本文は原則日本語とする。

Phase 1-exのMigrationでFile移動、再編、Git管理への変更が必要な場合は、Inventory、Hash、Link検証、Rollbackを先に定義してから実施する。

## 6. Phase単位1File統合の担当

Phase完了ごとの1File統合は、現在の設計者役担当Taskが実施する。

これは要約ではなくLossless Compilationである。

```text
Source Set Freeze
  → Inventory
  → Path／Document ID／State／Size／SHA-512記録
  → 元本文を変更せず格納
  → 再抽出
  → Byte Size／SHA-512照合
  → 全件一致時のみPass
```

次を禁止する。

- 勝手な要約
- 意訳
- 再解釈
- 用語や口調の無断変更
- 重複の勝手な削除
- 矛盾の勝手な解消
- 新旧文書の無断選別
- Authorization Boundaryの変更
- 数値、Version、Hash、Path、Stateの変更

公開不可情報の除外または匿名化は、Lossless Compilation中の書換えとして行わず、独立したPrivacy Scrub工程として記録する。

## 7. READMEのRoadmap最優先要件

ユーザーが公開成果物の中で最も見せたい文書はRoadmapである。

Phase 1-exで作成する`README.md`は、Roadmapを補助リンクまたは末尾の参考資料として扱わず、最優先の閲覧導線として強調する。

対象Roadmap：

```text
docs/public/roadmap_ja.md
```

最終Directory設計でPathが変更された場合も、READMEから実在するCurrent Roadmapへ直接到達できるLinkを維持する。

## 8. README内のRoadmap表示要件

READMEの上部、Project概要の直後または同等に目立つ位置へ、Roadmap専用SectionまたはCalloutを置く。

最低限、次を満たす。

- `Roadmap`を独立見出しまたは視認性の高い導線として置く。
- 「このProjectの現在地、今後のPhase、完成予定像を確認する場合はRoadmapを最初に参照してください」という趣旨を敬語で明示する。
- Roadmapへの直接Linkを置く。
- RoadmapがProjectの中核公開文書であることを伝える。
- Current Phase、実装済み、未完成、将来計画の詳細をREADME内で不完全に再構築せず、Roadmapへ誘導する。
- Roadmap Link切れを公開前TestでFailとする。
- Mobile／GitHub表示でも導線が埋もれない位置に置く。

表示例の趣旨：

```markdown
## Roadmap — 最初にご覧ください

本Projectの現在地、Phaseごとの実装状況、今後追加するRuntime Governance、
Guardrail、Judge、RAG、Agent、および将来R&D統合計画は、Roadmapにまとめています。

→ [Roadmapを確認する](../../../../public/roadmap_ja.md)
```

これは文言の固定Templateではない。README本文は敬語を維持しつつ、同等以上に明確なRoadmap導線を作る。

## 9. READMEとRoadmapの責務分離

READMEは次を簡潔に説明する。

- 何を作っているか
- 現在動く範囲
- 最初の起動／公開Demoへの導線
- Roadmapへの最優先導線
- Setup、License、Docsへの入口
- 末尾のEnglish Abstract

Roadmapは次を詳しく扱う。

- 全Phase一覧
- 各Phaseの目的と主要機能
- 実装済み／検証中／未着手／将来予約
- Phase Gateと依存関係
- Runtime Governance Platformへの発展
- EASA、DLAGSA、OCILNS等の将来統合Hook
- 現時点の制約と再評価条件

READMEへRoadmap全文を複製しない。READMEからRoadmapを強調して案内し、Phase情報のCurrent SourceをRoadmapへ集約する。

## 10. 検証条件

Phase 1-ex完了前に次を検証する。

```text
[ ] docs/配下のPhase 1-ex期間中Writerが現在の設計者役へ統一されている
[ ] 他担当Task向けHandoffに直接Docsを書かない境界が通知されている
[ ] Phase単位Lossless Compilationを現在の設計者役が実施している
[ ] Compilationの全Sourceが再抽出可能である
[ ] Byte Size／SHA-512が全件一致する
[ ] README上部にRoadmap専用導線がある
[ ] Roadmap Linkが実在し、GitHub上で解決する
[ ] READMEとRoadmapの実装状態表示が矛盾しない
[ ] README末尾にEnglish Abstractがある
[ ] Public IdentityがNazuna Researchに統一されている
[ ] Credential、個人Path、Private Artifactが公開Docsに含まれない
```

## 11. Completion Boundary

本要件の単一Writer運用は、Phase 1-exの全Completion Gateが合格し、現在の設計者役または移行後の設計統括者役がPhase 1-ex完了を明示的に宣言した時点まで継続する。

単にREADME、Roadmapまたは統合Fileを作っただけでは終了しない。

Phase 1-ex完了後のWriter分担は、その時点のAccepted Role／Authority Policyを正本とする。

## 12. Authorization Boundary

本要件のAccepted化は、Phase 1完了、Phase 1-ex開始、Docs Migration、Lossless Compilation実行、README／LICENSE生成、Git初期化、Commit、Push、GitHub公開またはLightning外部操作を自動許可しない。

現在許可されるのは、Phase 1-ex完了までのDocumentation Writerと、将来READMEのRoadmap最優先導線を要件として固定することだけである。

## 13. Append-Only

既存Role Policy、Phase 1-ex総合要件、Lossless Compilation要件を変更せず、期間限定の単一WriterとRoadmap最優先導線を追加する新Timestamp文書として作成した。

<!-- SOURCE_END 14: docs/requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md -->

---

<!-- SOURCE_BEGIN 15: docs/requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md -->

### Source 15: `docs/requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md`
- Source SHA-512: `622ae9cefc02deb90ddd7b563e09facaa5d9f38de85877f8a0dc027bfd2ca16bf277247112b450bf05a543e07d86955d2c1e9438d0332a979db8ac6d7cb85d08`
- Source Size: `8380` bytes

# Phase 1-ex Lightning Web Auto-start／Cost Control 要件予約

- 文書ID: `phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation`
- 状態: `accepted_reservation_not_implemented`
- 作成日時: `2026-07-26 11:16:32 JST`
- 更新日時: `2026-07-26 11:16:32 JST`
- Snapshot: `20260726111632`
- 作成担当: 設計者役担当Task
- 対象Phase: Phase 1-ex「運用再整備」
- Acceptance Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- 正本言語: 日本語
- supersedes: なし

## 1. 背景

Lightning Web Previewは、Pure CPU Profile、Basic認証、外部Browserおよび主要Web機能についてAcceptanceを通過した。

一方、StudioのSleep／Restartごとに次をTerminalへ手入力する運用は負担が大きい。

- Workspace／Project／Model／uv／`.venv` Path
- `PATH`
- Basic認証Mode、Username、Password
- Profile
- Host／Port
- `margpa-web`起動
- Health Check

Phase 1実装のCorrectness問題ではなく、公開Previewを継続運用するためのOperations問題としてPhase 1-exへ予約する。

## 2. Goal

利用者がPublic LinkへAccessしたとき、必要に応じてLightning環境とMARGPA Webが起動し、Idle時には安全にSleepできる構成を目指す。

```text
Traffic／Studio Wake
  → Runtime Start
  → Model Load
  → Health Ready
  → Basic Authentication
  → Web Available

Idle
  → Web／Studio Sleep
  → Compute Cost停止
  → Persistent Artifact維持
```

## 3. Two-stage Automation

### 3.1 Studio起動後の自動Web起動

LightningのStudio Launch ActionからProject-owned Launcherを呼ぶ。

候補：

```text
~/.lightning_studio/on_start.sh
  → margpa-runtime-llm/scripts/run/start_lightning_pure_cpu_web.sh
```

`on_start.sh`へ長いApplication起動手順を直接埋め込まず、Repository管理可能なLauncherへ責務を寄せる。

### 3.2 URL AccessによるTraffic-aware Auto-start

StudioがSleep中でもPublic URLへのAccessを契機に起動できるLightningのAuto-start／Hosted App機能を利用可能か確認する。

Current Port Viewerによる手動Port公開だけで、URLからStudio Wakeまで成立すると仮定しない。

実装前に次をRead-only Preflightする。

- Current Lightning PlanでAuto-startを利用できるか
- Custom Port Appで利用できるか
- Public LinkがSleep／Wake後も維持されるか
- CPU StudioをTargetに固定できるか
- Cold Start中の表示
- Health CheckとReady判定
- Auto-startとBasic認証の順序
- Credit／無料CPU枠への影響

## 4. Project-owned Launcher

候補File：

```text
scripts/run/start_lightning_pure_cpu_web.sh
```

最低責務：

- Workspace Root、Project Root、Model Root、Project-local uv、Project `.venv`を決定する。
- Pure CPU Profileを明示する。
- GPUへ黙って切り替えない。
- Model ArtifactとExecutableを確認する。
- Basic認証が有効であることを確認する。
- Secret不足時にFail Closedする。
- 同一Port／同一Processの重複起動を防止する。
- `margpa-web`を起動する。
- `/healthz`がReadyになるまでBounded Waitする。
- Startup FailureをCredentialなしのLogへ記録する。
- Stop／Restart／Stale PIDを安全に扱う。

Launcherの実装方式は、Lightning On-start Process Lifecycleを確認してから決定する。`nohup`、Background Job、PID FileまたはProcess Supervisorを根拠なく固定しない。

## 5. Persistent Configuration

### 5.1 Non-secret

次はLightning Studio EnvironmentまたはProject-owned Launcherの既定値候補とする。

```text
MARGPA_WORKSPACE_ROOT
MARGPA_PROJECT_ROOT
MARGPA_MODEL_ROOT
MARGPA_UV_BIN
MARGPA_ENV_PREFIX
MARGPA_WEB_AUTH_MODE
```

PathはCurrent Lightning Environmentに固有であるため、Application Coreへハードコードしない。

### 5.2 Secret

次はLightning Managed Secretsまたは同等のSecret Storeで管理する。

```text
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

PasswordをRepository、Config、Docs、Command Example、Screenshot、Process Argument、公開Logへ保存しない。

外部Preview利用者へ毎回Credentialを再通知しないため、Auto-start時にRandom Passwordを毎回再生成しない。安定したPreview CredentialをSecret Storeへ登録し、必要時に明示Rotateする。

## 6. Cost／Performance Policy

```text
Default Lightning Runtime : Pure CPU
GPU Runtime               : Explicit opt-in only
Silent GPU Selection      : Forbidden
Summary Mode              : User opt-in
Thinking Generation       : User opt-in
Max New Tokens            : User configurable
```

Pure CPUの遅さは利用者へ明示する。Summary Modeは通常回答後に同じModelを再度呼ぶため、Pure CPUでは特にLatencyが増える。

GPUは短時間のBenchmark、Compatibility Testまたは明示Demo時だけ選択し、終了後にCPUへ戻す。

## 7. Sleep Semantics

Lightningの通常Auto-sleepと、Traffic-aware Hosted App Auto-startを区別する。

- 通常のStudio Auto-sleepでは、実行中のAPI ServerがActive WorkとしてSleepを妨げる場合がある。
- Traffic-aware Auto-startは、User Trafficを監視し、未使用時にApp／Studioを停止する別のHosting動作である。
- Browserを閉じただけで直ちにProcess停止またはCost停止したと推測しない。
- Lightning DashboardのMachine StateとCredit Consumptionを実測する。

Manual Sleepは、Auto-start Acceptance完了までの安全なCost Control手段として維持する。

## 8. Cold Start

URL Accessから利用可能になるまで、Model LoadおよびSHA-512検証を含むCold Startが発生する。

要件：

- Cold StartはFailure表示と区別する。
- 起動中Statusを可能な範囲で表示する。
- 無期限に待たない。
- Ready前にModel Requestを受け付けない。
- Cold Start時間を計測する。
- Public Preview利用者へ数分待つ可能性を案内する。

## 9. Acceptance Conditions

### 9.1 Functional

1. StudioまたはHosted AppをSleepさせる。
2. Public Linkへ外部BrowserからAccessする。
3. Manual Terminal入力なしに起動が開始される。
4. Cold Start後にBasic認証画面が表示される。
5. 正しいCredentialでMARGPA Webを開ける。
6. `/healthz`がReadyを返す。
7. 短い日本語生成が成立する。
8. 二重Processが起動しない。
9. Idle後にPlatform定義どおりSleepする。
10. 次回Accessで再度起動できる。

### 9.2 Security

1. Credential未設定時はPublic Bindを拒否する。
2. SecretがLog、Docs、Git、Process Argumentへ出ない。
3. `/healthz`は最小情報だけを返す。
4. Public RootはBasic認証を維持する。
5. Auto-start ScriptはModel／Project以外を変更しない。

### 9.3 Cost

1. Default MachineはCPUである。
2. Auto-startがGPUへ切り替えない。
3. Sleep中のCompute StateをDashboardで確認する。
4. User Trafficがない状態で無期限実行しない。

## 10. Fallback

Current Lightning Plan、Custom Port AppまたはPublic LinkでTraffic-aware Auto-startが利用できない場合：

```text
Fallback A:
  Studioを手動Wake
  → on_start.shでWebを自動起動

Fallback B:
  Current Manual手順
  → Pure CPU Webを手動起動
  → 使用後にManual Sleep
```

Platform制約を回避するためにCredentialを外す、GPUを常時起動する、非公開APIへ依存する等の変更を行わない。

## 11. iOS／Responsive UI

iPhone／iOSは本Auto-start要件の対象外とする。

Mobile Browser対応はPhase 4または後続UI PhaseのResponsive Designとして扱う。Public Linkへ到達できることと、Mobile UX Acceptanceを同一視しない。

## 12. Authorization Boundary

本書はPhase 1-exの要件予約であり、次を自動許可しない。

- `on_start.sh`の変更
- Lightning Environment Variable／Secretの追加
- Source／Script変更
- Auto-start有効化
- Machine Type変更
- Public Link変更
- Git／GitHub操作

実装前にCurrent Lightning UI／PlanのRead-only Preflightと、実装担当向けAccepted Handoffを作成する。

<!-- SOURCE_END 15: docs/requirements/phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md -->

---

<!-- SOURCE_BEGIN 16: docs/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md -->

### Source 16: `docs/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md`
- Source SHA-512: `e19ecdbbd95747821f2ec9514b993d67e8d60f31dc3cecd8f7ca00a9f5c512e6b67860caa981ab3fa67773bd266b5e272b6bd6724cf928cca8a39015f39e0b24`
- Source Size: `1927` bytes

# Phase 1-ex 運用再整備 要件プレースホルダー

- 文書ID: `phase_1_ex_operations_reorganization_requirements`
- 状態: `requirements_pending`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- supersedes: なし

## 1. 確定事項

Phase 1と初回GitHub公開の間に、次を追加する。

```text
Phase ID : Phase 1-ex
Name     : 運用再整備
State    : Added／Requirements Pending
```

Phase 1-ex完了後に初回GitHub公開を行う。Phase 1-ex前の状態は初回公開しない。

## 2. 現時点の目的

- Phase単位BackupとGitHub履歴の対応を整える
- 公開前Sanitationを再現可能にする
- 公開Identity、Path、Secret、Archive境界を固定する
- Git／GitHub運用、Release単位、証跡を整える
- 今後の各Phaseで同じ運用を反復可能にする

## 3. 未定義事項

次は後続の要件定義で決める。

- Git初期化、Branch、Commit、Tag、Release方式
- Repository Visibilityと公開範囲
- Backup生成／Sanitation Scriptの要否
- Manifest／Receipt Schema
- GitHubへ含めるDocs／Public Docs境界
- README、License、Copyright
- CI、Release Check、Secret Scanの範囲
- Phase 1-exのUser Manualと受入条件
- 担当Task間の実行順序

## 4. 完了条件

現時点では未定義である。詳細要件確定前にPhase 1-ex完了を宣言しない。

少なくとも、運用文書、公開対象Inventory、Privacy Gate、Backup／GitHub対応、復元・検証手順がAcceptedであることを将来の候補条件とする。

## 5. Authorization Boundary

本書はPhase 1-exの存在と配置を確定するだけであり、実装、File変更、Backup生成、Git初期化、Commit、Remote作成、Push、GitHub公開を許可しない。


<!-- SOURCE_END 16: docs/requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md -->

---

<!-- SOURCE_BEGIN 17: docs/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md -->

### Source 17: `docs/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md`
- Source SHA-512: `040ab639b364251d25fde8570beb6635e4646b2b2c5b1e5e075cae12229c3fff808ebbb590fb32a000b88e971889b6e9089d97c7f2f4c55bdaa0ac0cbaab3d1a`
- Source Size: `5652` bytes

# Phase 1-ex 運用再整備 要件

- 文書ID: `phase_1_ex_operations_reorganization_requirements`
- 状態: `accepted_reservation_requirements_incomplete`
- 作成日時: `2026-07-20 23:10:36 JST`
- 更新日時: `2026-07-20 23:10:36 JST`
- Snapshot: `20260720231036`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- ADR: [ADR-0017](../history/adr/adr_0017_phase_1_ex_operating_model_and_documentation_transition_20260720231036.md)
- supersedes: `phase_1_ex_operations_reorganization_requirements_20260720222402.md`

## 1. Phase Identity

```text
Phase ID : Phase 1-ex
Name     : 運用再整備
Position : Phase 1機能確定後／初回GitHub公開前
State    : Added／Accepted Reservation／Not Started
```

## 2. Current Non-execution Rule

Phase 1-ex開始指示までは、現在の設計者役、Docs Authority、Append-Only Rule、Directory Structure、Git未導入状態を維持する。

現時点で次を行わない。

- 設計統括者役への変更
- 新しいPhase設計者Taskの作成
- Git初期化／Commit／Remote／Push
- Docs Directory変更／File移動／Rename
- Write Authority変更
- 各担当Taskへの構造変更通知
- Lossless Compilation実行
- README／LICENSE／Public Docs生成

## 3. Role／Authority Reorganization

Phase 1-exで次の役割を再整理する。

- 設計統括者役
- 設計者役
- 実装者役
- 対外Docs役

対象：

- DirectoryごとのWrite Authority
- Read-only範囲
- Handoff／Status／Review／Index Ownership
- Phase開始／完了Gate
- Cross-Phase Escalation
- Public Docs／Lossless Compilation Ownership
- Git操作権限
- Backup／Release操作権限

現設計者役を設計統括者役へ変更するのはPhase 1-exの実行項目であり、現在はまだ設計者役とする。

## 4. Phase Design Delegation

Phase 1-ex完了後、必要に応じてPhaseごとに専用設計者役を配置する。

設計統括者役がPhase単位の上位設計、制約、受入境界、Handoffを渡す。Phase設計者役は、ユーザー要求またはEvidenceによる仕様変更を含め、上位設計から大きく外れない範囲で詳細を再設計できる。

Cross-Phase影響、共通Architecture、Accepted Policy変更はEscalation対象とする。

## 5. Git Transition

Phase 1-exからGit運用へ変更する。

要件定義対象：

- Repository初期化Point
- Initial Commit Scope
- Branch Strategy
- Commit Granularity／Message
- Phase Tag／Release
- Backup Snapshotとの対応
- Dirty State Gate
- Remote／Visibility
- Git Author／Committer Privacy
- Secret Scan／Ignore
- Rollback／Restore
- Docs HistoryとGit Historyの役割分担

初回GitHub公開はPhase 1-ex完了後とする。以後は原則、各Phaseのテスト、Docs、Final Gate、Backup確定後に同一SnapshotをGitHubへ反映する。

## 6. Docs Operating Model

Git運用次第で、これまで新Timestampで作成してきたDocsをPhase単位で1Fileへ再整理する。

必要条件：

- 公開して問題ない
- 新Taskが即引き継げる
- 原文の意味、Decision、Boundaryを変えない
- 運用／共通ルール／Handoff等はLossless
- Source InventoryとHashを持つ
- Current／Historical／Conflictingを外部Metadataで示す
- Public Derived DocsとCanonical Compilationを分離する

詳細は[Lossless Compilation要件](../history/requirements/lossless_phase_document_compilation_requirements_20260720231036.md)を正本とする。

## 7. Docs Directory Migration

Phase 1-exで`docs/`の新Directory構造を設計し、Migration Plan、対象Inventory、Link更新、Validation、Rollbackを定義してから変更する。

変更完了後、各担当Taskへ新構造と権限を通知する。移行途中に新旧Pathを暗黙併用しない。

## 8. Public Docs

対外Docs役がPhase完了単位、テスト完了後、Backup前に作成または更新する。

```text
README.md
LICENSE
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

- Docsはすべて日本語
- README本文は敬語
- README末尾にEnglish Abstract
- READMEへ実在するLightning公開サイトURL
- LICENSEは英語公式原文を許容
- その他は研究文書風の日本語
- 将来`*_en.md`を追加可能だが現在は要求しない

## 9. Phase-end Sequence

```text
Implementation／Test完了
  → Phase Review
  → Lossless Phase Compilation
  → Public Derived Docs作成・更新
  → Privacy／License／Integrity Review
  → User Acceptance／Designer Final Gate
  → Backup Candidate／Sanitation／確定
  → Git Commit／Tag／GitHub反映
```

詳細なGate順序は既存Backup Policyと整合させ、Phase 1-exで最終確定する。

## 10. Remaining Definition Items

- Git Strategyの詳細
- Final Docs Directory Tree
- Current／Historical正本関係
- Lossless Compilation File Format／Script
- Public／Internal Source Set境界
- Project Code License
- README Template
- Phase Summary Template
- CI／Secret Scan／Link Check
- Migration Test／Rollback
- Phase 1-ex User Manual／Acceptance Criteria
- Phase 1-Gとの順序

## 11. Completion Gate

未定義項目がAcceptedになり、Role、Git、Docs、Migration、Compilation、Public Docs、Backup、Notification、Rollbackの検証が完了するまでPhase 1-ex完了を宣言しない。

## 12. Authorization Boundary

本書は要件予約を記録する。Phase 1-exの実行、Role変更、Task作成、Git操作、Directory変更、Docs統合、Public Docs生成、各担当通知、GitHub公開をまだ許可しない。


<!-- SOURCE_END 17: docs/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md -->

---

<!-- SOURCE_BEGIN 18: docs/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md -->

### Source 18: `docs/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md`
- Source SHA-512: `8e6ba320f6a0f2ad8dff3a9574818128e8f7883dc211388fbc1a559b53c2789624f9531440b4409dafbab8eb654c14997f90702c73b28c0edd6aa584760de31b`
- Source Size: `6732` bytes

# Phase 1-ex 開始順序／Public Demo／Git準備 要件予約

- 文書ID: `phase_1_ex_pre_start_execution_order_and_public_demo_requirements`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-26 12:02:29 JST`
- 更新日時: `2026-07-26 12:02:29 JST`
- Snapshot: `20260726120229`
- 作成担当: 設計者役担当Task
- 親要件: [phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md](../history/requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- 統合記録: [phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](../history/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)
- 正本言語: 日本語
- supersedes: `phase_1_ex_lightning_web_autostart_and_cost_control_requirements_reservation_20260726111632.md`

## 1. Current Decision

Phase 1はComplete／Acceptedであり、Phase 1確定Backup後にPhase 1-exを開始する。

Phase 1-exの主要対象：

- Lightning Auto-start実現可能性の早期判定
- Git運用設計および公開準備
- `docs/` Directory構造再編
- 担当Taskへの新構造通知
- 既存DocsのLossless再整理
- Canonical／公開Docs作成
- Mac限定簡易RAG
- 初回GitHub公開

## 2. READMEのPublic Demo表記

公開Repositoryへ個人情報、個人連絡先または個人Profileへの導線を掲載しない。

したがって、READMEへ次の趣旨を記載しない。

```text
デモの閲覧を希望する場合は連絡してください。
連絡後にCredentialを案内します。
```

Current Phase 1 PreviewはBasic認証付きの少人数検証用である。

公開READMEでは次の趣旨だけを使用する。

> 将来、Public Demo方式も検討しています。

Public URLをREADMEへ掲載するかは、Traffic-aware Auto-start、Access Control、Cost Guardおよび公開時の稼働状態を確認してから決定する。

## 3. Basic認証

Current Lightning PreviewではBasic認証を維持する。

```text
Current Mode : preview_shared
Authentication: Basic
Account System: Not Implemented
```

Basic認証は、将来AWS上で導入する本格Account／Quota／Permission機能とは別物である。

`public_demo`のためのRate Limit、Token Budget、Cost Guard、Bot対策等はキリなくScopeが広がるため、Phase 1-ex必須機能にしない。

## 4. Lightning Auto-start Early Preflight

Phase 1-exの機能変更前半で、まずRead-only Preflightを行う。

確認対象：

- Current Lightning PlanでTraffic-aware Auto-startを利用できるか
- FastAPI＋Custom Port Viewerへ適用できるか
- Public URLからSleep中StudioをWakeできるか
- CPU MachineをDefaultに維持できるか
- Basic認証を維持できるか
- Public URLがSleep／Wake後に維持されるか
- Cold Start中の表示または待機動作
- Credit／無料枠への影響

Decision Rule：

```text
Simple Path:
  Native Auto-start／小規模Launcherで成立
  → Phase 1-ex前半で実装

Complex Path:
  Deployment移行、大規模Adapter、Plan変更または課金前提
  → Current Phase 1-exから延期可能
```

短時間のRead-only Preflightによって難易度を判定し、Platform制約が判明した後も無制限に実装Scopeを拡張しない。

## 5. Git準備の前倒し

Git運用設計および公開準備を、既存DocsのLossless再整理より前へ移動する。

前倒し対象：

- Branch Strategy
- Commit Message
- Phase Tag／Release
- Backup／Manifest／Commit対応
- Author Name／Commit Email
- Remote／Public Repository
- `.gitignore`
- `.gitattributes`
- Model／Binary／Secret／Cache除外
- Privacy Scan
- License／Terms／Notice方針
- Initial Commit Allowlist

## 6. Initial Commit Boundary

Git準備を先に行っても、次が完了するまで初回公開Commitを作成しない。

- `docs/` Directory再編
- 担当Taskへの新構造通知
- Lossless Phase Compilation
- Canonical Docs作成
- README／LICENSE等の公開文書
- Public Identity Scan
- Personal Information Scan
- Secret Scan
- Model／`.venv`／Cache除外
- Link Validation
- Test／Review

既存の細分化Docsまたは移行前Artifactを一度Commitし、後から削除する方式は採用しない。削除後もGit Historyへ残るためである。

`git init`自体を早期に行うか、初回Commit直前に行うかはGit運用設計で決める。いずれの場合も、初回Public Historyへ含める内容はSanitized Allowlistから決定する。

## 7. docs再編

Git準備後に次を実行する。

1. Current File Inventory
2. Target Directory Tree
3. Current／Historical／Superseded／Conflicting分類
4. Move／Keep／Compile／Exclude Manifest
5. Relative Link更新計画
6. Ownership／Write Authority再定義
7. Rollback Plan
8. Directory Migration
9. 全担当Taskへの通知
10. Lossless Compilation

既存文書を勝手に要約、意味変更または再解釈しない。

## 8. Canonical／Public Docs

少なくとも次を整備する。

```text
README.md
LICENSE
NOTICE.md
CITATION.cff
docs/overview_ja.md
docs/concept_ja.md
docs/roadmap_ja.md
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
docs/project_continuity_master_ja.md
```

実際の配置先はTarget Directory Tree確定時に決める。

## 9. Mac限定簡易RAG

Docs構造とCanonical Setが確定した後に実装する。

- Mac実機ではDocumentation Explainerとして利用する。
- Lightning初期公開ではHookのみを許容する。
- `docs/`がない場合は明示的Unavailable Resultを返す。
- RAG対象のPublic／Private分類を行う。
- Modelへ渡したDocument／Chunk／Hashを将来Audit可能にする。

Docs再編前にIndexを作り、移行後に作り直すことを避ける。

## 10. Final Phase 1-ex Order

```text
1. Phase 1確定Backup
2. Lightning Auto-start Read-only Preflight
3. Git運用設計
4. Git公開準備
5. docs/構造再設計
6. 全担当Taskへ通知
7. 既存Docs Lossless再整理
8. Canonical／公開Docs作成
9. Mac限定簡易RAG
10. Review／Test／Privacy Scan
11. Initial Commit／Tag／Phase 1-ex Backup
12. GitHub公開
```

## 11. Authorization Boundary

本要件予約はPhase 1-exの順序と境界を確定するが、次を自動許可しない。

- Lightning設定変更
- Auto-start有効化
- Git初期化
- Commit／Tag／Remote／Push
- Docs Move／Rename／Delete
- Source／Config変更
- RAG実装
- GitHub公開

Phase 1確定Backup完了後、ユーザーのPhase 1-ex開始指示に従う。

<!-- SOURCE_END 18: docs/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md -->

---

<!-- SOURCE_BEGIN 19: docs/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md -->

### Source 19: `docs/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md`
- Source SHA-512: `1d912280bf6caf0f4d4446902595ab72812c46cd0100d137f21bcb80ec65a61adab3cee2e2494f0e8f1a41f9e4d9b0761c0fe12f1df462910c5761ec4b3f6678`
- Source Size: `11602` bytes

# Phase 1-ex 公開名義・Access・License要件予約

- 文書ID: `phase_1_ex_publication_identity_access_and_license_requirements_reservation`
- 状態: `accepted_reservation_not_started`
- 作成日時: `2026-07-21 11:16:59 JST`
- 更新日時: `2026-07-21 11:16:59 JST`
- Snapshot: `20260721111659`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- 親要件: [phase_1_ex_operations_reorganization_requirements_20260720231036.md](../history/requirements/phase_1_ex_operations_reorganization_requirements_20260720231036.md)
- 公開識別情報正本: [public_identity_and_personal_information_policy_20260721111659.md](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md)
- supersedes: なし（Phase 1-ex公開移行詳細の追加予約）

## 1. Position

本書はPhase 1-exで実施する公開Repository移行、公開名義整理、License Staging、Citation／Notice作成、公開前検証の追加要件を予約する。

現在は予約段階であり、調査Command、Repository変更、Git操作、公開Artifact生成、Pushをまだ開始しない。

## 2. Public Identity

```text
Organization／Repository Owner : margpa-labs
Public Author／Research Name    : Nazuna Research
Public Repository              : https://github.com/margpa-labs/margpa-runtime-llm
Commit Author Name             : Nazuna Research
Commit Account Traceability    : 個人GitHub Accountへ辿れることを許容
```

Commit Emailは個人の実Emailを公開しない候補を優先する。GitHub提供noreply Email等により個人GitHub Accountへ帰属・リンクされることは許容する。

## 3. Two Public Access Boundaries

GitHub RepositoryとLightning AI Studio上の公開UIは、別の公開境界として扱う。

### 3.1 GitHub Repository

GitHub上のProject Source／Docsは、初期公開段階では次の方針とする。

```text
閲覧                : 許可
評価                : 許可範囲をLicenseで定義
GitHub機能上のFork  : GitHub利用規約上の権利を妨げない
その他の利用        : 明示許諾がない限り禁止
OSS                 : まだ該当しない
```

初期公開はOpen Sourceではなく、Evaluation-onlyのSource-available公開である。

「評価」の具体的範囲はPhase 1-exでLicense文面として確定する。最低限、次を明示する。

- Source閲覧
- Clone／Download／GitHub Forkの扱い
- Local実行評価の可否
- 評価に必要な一時的変更の可否
- Benchmarkと結果公開の可否
- Commercial／Production／Service利用禁止
- 再配布／再公開／Sublicense禁止
- 派生物作成／配布禁止
- AI Training／Dataset化の扱い
- Evaluation終了後の保管／削除
- Warranty／Liability Disclaimer
- 違反時の権利終了

GitHub Public RepositoryのPlatform上、利用者には閲覧とForkに関するGitHub利用規約上の権利が生じる。Project独自Licenseは、GitHub利用規約を上書きするものではなく、それ以外の追加利用権を定義・制限する。

### 3.2 Lightning Public UI

Lightning公開UIは、利用者が画面に公開された機能を自由に操作・評価できるInteractive Demoとする。

許可範囲：

- 公開UIへのAccess
- Prompt入力
- 新規Chat
- 公開された設定値の変更
- 生成／停止／再試行
- 画面へ返された結果の閲覧
- 通常利用範囲での機能評価

Lightning UIの自由利用は、次の権利を自動的に付与しない。

- GitHub Sourceの再利用／再配布
- Model Weightの取得
- 管理画面／CredentialへのAccess
- 未公開API／InfrastructureへのAccess
- Service妨害、過剰負荷、不正Access
- Projectの商用再提供

公開UIの利用条件、生成結果の扱い、Rate／Resource制約、Model由来の制約は、公開前にREADME／UI Notice／利用条件へ整理する。

## 4. License Staging

### 4.1 Initial Stage

ある程度以上完成するまで、Project Codeは独自のEvaluation-only License候補とする。

```text
Classification : Source-available／Proprietary Evaluation-only
Open Source     : No
Primary File    : LICENSE
Language        : English authoritative text候補
```

独自License文面は法的効果を持つため、公開前に専門家確認を推奨する旨を記録する。

### 4.2 Future OSS Stage

一定の完成条件を満たした後、ユーザー判断によりOSS Licenseへ変更可能とする。

OSS移行時は次を記録する。

- OSS化対象Version／Tag／Commit
- 採用License
- 過去Evaluation-only Releaseの扱い
- Contributor権利とRelicense可否
- Third-party Licenseとの整合
- License変更日
- README／NOTICE／CITATION／Package Metadata更新

OSS化を将来予定していることは、現在のEvaluation-only版へOSS権利を先行付与するものではない。

## 5. Root Public Files

Phase 1-exでは、既存予約に加えて次を公開候補として作成する。

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

### 5.1 `CITATION.cff`

```text
Language        : English
CFF Version     : 1.2.0
Author Entity   : Nazuna Research
Repository Code : https://github.com/margpa-labs/margpa-runtime-llm
License         : Custom Licenseのため架空SPDX IDを使用しない
License URL     : Public Repository内のLICENSE URL候補
```

Version／Release Date／DOIは、実在値が確定した場合だけ記載する。架空値や予定値をCitation Metadataへ入れない。

### 5.2 `NOTICE.md`

```text
Language : Japanese and English
```

最低限、次を含める。

- Project名と公開名義
- Repository Owner
- 現在のLicense Stage
- `LICENSE`が権利許諾の正本であること
- ARGD／DAGD等の個別LicenseとAttribution
- Third-party Library／Model／Artifactの権利分離
- Model WeightをRepositoryへ含めないこと
- Trademark／No Endorsement候補
- 日本語と英語の対応関係

`NOTICE.md`へLicense本文を重複させず、権利許諾の正本を`LICENSE`へ一本化する。

## 6. Component License Separation

Top-level Project Licenseを全Artifactへ一括適用しない。

最低限、次を分離する。

```text
Project-owned Source Code
Project-owned Documentation
ARGD／DAGD Definition
Third-party Governance Definition
Model Weight／Tokenizer／Config
Python Dependency
Web／UI Asset
Sample／Generated Output
```

ARGD／DAGDのCC-BY-SA-4.0、Model License、第三者Dependency License、個別AttributionをTop-level Evaluation-only Licenseで上書きしない。

## 7. Identifier Classification Rule

公開対象内の廃止済み第一者名義等を、文脈を無視して単純一括置換しない。次のClassへ分類する。

```text
repository_identity
  → margpa-labs／新Repository URL

public_author_identity
  → Nazuna Research

personal_information
  → 削除または中立化

local_environment_identifier
  → 匿名化または公開対象外

technical_account_identifier
  → 必要時のみ保持

immutable_provenance
  → 変更禁止／理由記録

third_party_identity
  → 正式表記を維持

manual_review
  → 自動変更禁止／ユーザー判断待ち
```

## 8. Phase 1-ex Required Work

Phase 1-exでは、実変更前に次を行う。

1. 公開面へ現れ得るFile／Metadata／HistoryのRead-only Inventory
2. 識別情報分類Manifest作成
3. 変更対象、変更方法、非変更理由の一覧化
4. Public AllowlistとPrivate Exclusionの確定
5. 洗浄済みPublic Exportの設計
6. License／CITATION／NOTICEのDraft設計
7. Commit Author／Email／Account帰属確認
8. PII／Secret／Path／Symlink／Binary／Model検査設計
9. Verification／Completion Gate定義
10. 実装担当向けRead-only Preflight Handoff

Read-only Preflight ReviewがAcceptedになるまで、置換、File削除、History変更、Public Export、Pushを行わない。

## 9. Migration Strategy

既存開発Treeや履歴を直接洗浄しない。原則として次の構成を優先する。

```text
Development Source／Internal Evidence
  ↓ Read-only Inventory
Classification Manifest
  ↓ Allowlist Export
Sanitized Public Staging Tree
  ↓ Validation
User／Designer Approval
  ↓ Clean Public Commit
margpa-labs/margpa-runtime-llm
```

履歴を移行する必要がある場合も、原本ではなく専用Clone／Copyを対象とする。

## 10. Verification／Completion Conditions

公開前に最低限、次をすべて満たす。

- Repository URL／Badge／Clone URLが新Repositoryを指す。
- Public Author／Maintainer名が`Nazuna Research`である。
- 廃止済み第一者名義の残存箇所が全件分類済みである。
- 本名、LinkedIn、職務経歴、個人連絡先、個人Pathがない。
- Secret／Credential／Tokenがない。
- `.venv`、Model Weight、Symlink、Cache、Local Logがない。
- LICENSE、README、NOTICE、CITATIONの表示が矛盾しない。
- `CITATION.cff`がCFF 1.2.0 Schema Validationへ合格する。
- Third-party Attribution／Licenseを保持している。
- Public Exportから環境を再構築できる。
- Test、Link Check、Archive Manifest、Hash検証が合格する。
- Commit Author Nameが`Nazuna Research`である。
- Commitから個人GitHub Accountへ辿れる可能性が許容済みDecisionと一致する。
- GitHub権利境界とLightning UI利用境界が明記されている。
- Push対象Commit／Treeをユーザーが最終確認している。

## 11. Documentation Ownership

- 設計者役／将来の設計統括者役が本要件、分類規則、Architecture、ADR、Preflight Handoffを管理する。
- 実装担当はRead-only Preflight結果とPublic Export実装Statusを新規Handoffとして記録する。
- 対外Docs役がREADME、NOTICE、CITATION、公開Docsを作成する。
- LICENSEの最終権利条件はユーザー決定を必須とする。
- Pushは専用Authorizationとユーザー最終承認を必須とする。

## 12. Authorization Boundary

本書はPhase 1-exのAccepted Reservationである。

現時点では次を行わない。

- Phase 1-ex開始
- Repository全体の識別情報走査
- 既存Fileの置換／削除／Rename
- README／LICENSE／NOTICE／CITATION生成
- Git初期化／Commit／Tag／Remote設定
- Git History書換え
- 公開RepositoryへのPush
- Lightning設定変更

これらはPhase 1-G Review、Phase 1-H、Lightning検証、Phase 1完了Gateとの順序を確認したうえで、Phase 1-ex開始指示後に実施する。

## 13. References

- GitHub Docs: [Licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- GitHub Docs: [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service)
- GitHub Docs: [About CITATION files](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files)
- Citation File Format: [CFF 1.2.0 Schema Guide](https://github.com/citation-file-format/citation-file-format/blob/main/schema-guide.md)
- GitHub Docs: [Setting your commit email address](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address)
- Open Source Initiative: [The Open Source Definition](https://opensource.org/osd)

<!-- SOURCE_END 19: docs/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md -->

---

<!-- SOURCE_BEGIN 20: docs/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md -->

### Source 20: `docs/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md`
- Source SHA-512: `dd9d07d5c852345659c4003aef3579a6103ec9071335204fcbe0136dfe6d8e104ee601f54afe179a2315ef6fb41eb2e0b1d799646bfce896b37919c2c40f4305`
- Source Size: `11854` bytes

# Phase 1-C Deployment／Platform／Acceleration Abstraction要件

- 文書ID: `phase_1c_deployment_platform_acceleration_requirements`
- 状態: `current_approved`
- 作成日時: `2026-07-19 01:31:09 JST`
- 更新日時: `2026-07-19 01:31:09 JST`
- Snapshot: `20260719013109`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-C、Deployment Profile、Platform、Acceleration、Runtime Capability
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
- 関連Architecture: [phase_1c_deployment_platform_acceleration_architecture_20260719013109.md](../history/architecture/phase_1c_deployment_platform_acceleration_architecture_20260719013109.md)
- 関連ADR: [adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md](../history/adr/adr_0007_deployment_platform_acceleration_abstraction_20260719013109.md)
- supersedes: なし（新規Phase 1-C要件系列）

## 1. 結論

Phase 1-Cは、Windows専用実装を追加するPhaseではない。

macOS、Windows、Linux、CPU、GPU、NPU、Local、Home Server、Cloud、Native、ContainerおよびRemote Runtimeを、Application Coreへ固有条件を埋め込まず、同一の構造で後から追加できるDeployment／Platform／Acceleration境界を作る。

```text
Phase 1-Cで行うこと
  全環境を表現・検証・選択できる最小ContractとHookを作る

Phase 1-Cで行わないこと
  全OS、全GPU、全Backendを実装・Build・検証する
```

## 2. 背景

Phase 1-Bでは、次が実装・検証済みである。

```text
Host              : macOS／Apple Silicon arm64
Hardware          : Apple M2 Pro／16GB Unified Memory
Backend           : llama-cpp-python 0.3.34
Acceleration      : Metal
Model             : Qwen3-4B Q4_K_M／GGUF
Application       : Model Port経由
Deployment Config : TOML Profile
```

Model PortとAdapterの分離は成立しているが、現在の実装には次のmacOS／Metal固定点が残る。

- CLIのDefault Profileが`local_macos_arm64.toml`へ固定されている
- `gpu_offload`がModel固有のRequired Capabilityとして扱われている
- CPU Deploymentでは同じModelを使用できてもCapability不足として拒否される
- Runtime Device判定が実質`metal`または`cpu`である
- Environment VerificationとModel SmokeがDarwin／arm64／Metalを前提とする
- Native SetupがBash、POSIX Pathおよび`.venv/bin/`を前提とする

これらを放置したままUI、Audit、GovernanceおよびRemote Runtimeを積み上げると、Deployment固有条件が上位層へ伝播する可能性がある。

一方、Windows、CUDA、ROCm、Vulkan等をHardware未確定の段階ですべて実装すると、未検証ProfileとBuild Scriptが増え、将来の実機に合わず作り直す可能性が高い。

したがって、今は汎用境界だけを確定する。

## 3. macOSとCUDAの整理

CUDAは過去のIntel MacとNVIDIA GPUの組合せでは存在した。

NVIDIA CUDA 10.2はmacOSをSupportした最後のCUDA Toolkitであり、CUDA 11以降はmacOS上の開発・実行をSupportしない。

現在のApple Silicon MacではCUDAを使用できない。

現在のMac候補は次である。

- CPU
- Apple Accelerate
- Metal
- Metal Performance Shaders／PyTorch MPS
- MLX／MLX-LM
- Core ML／Apple Neural Engine
- VulkanからMetalへのTranslation Layer

現在のM2 Pro ProfileはMetalをPrimaryとする。

## 4. 表現対象となる独立軸

全組合せをFile名やClass名へ埋め込まない。次の軸を分離して表現する。

### 4.1 Host

- Operating System
- OS Version／Distribution
- CPU Architecture
- Native／WSL／VM／Container
- Host Identifier
- Headless／Desktop

### 4.2 Compute Device

- CPU
- Integrated GPU
- Discrete GPU
- Unified GPU
- NPU
- TPU
- HPU
- FPGA／ASIC
- Remote Accelerator

### 4.3 Vendor

- Apple
- NVIDIA
- AMD
- Intel
- Qualcomm
- Huawei
- Google
- AWS
- Moore Threads
- その他のVendor

Vendor値は閉じた列挙へ永久固定しない。

### 4.4 Acceleration API／Runtime

- CPU Native
- BLAS／OpenBLAS
- Apple Accelerate
- Metal／MPS
- CUDA
- HIP／ROCm
- Vulkan
- SYCL／oneAPI／XPU
- OpenVINO
- DirectML／WinML
- Core ML
- OpenCL
- CANN
- MUSA
- WebGPU
- RPC／Remote API
- Vendor Plugin

### 4.5 Memory Topology

- CPU RAM
- Unified Memory
- Shared Memory
- Discrete VRAM
- NUMA
- Multi-GPU
- Partial Offload
- Remote Memory

### 4.6 Backend Adapter

- llama.cpp／llama-cpp-python
- MLX／MLX-LM
- Transformers／PyTorch
- vLLM
- ONNX Runtime
- OpenVINO
- TensorRT／TensorRT-LLM
- Core ML
- Remote OpenAI-compatible API
- 将来Adapter

### 4.7 Model Artifact Variant

- GGUF
- Safetensors
- MLX形式
- ONNX
- OpenVINO IR
- TensorRT Engine
- Core ML Package
- Vendor Compile済みArtifact

同じLogical Modelに複数Artifact Variantを関連づけられること。

### 4.8 Execution Topology

- Same Process
- Same Host Service
- Localhost API
- LAN Home Server
- Remote GPU Server
- Cloud API
- Single Device
- Multi-GPU
- Multi-Node
- Hybrid

## 5. Required／Detected／Executedの分離

最低限、次の3種類を分離する。

```text
Required Capability
  Deploymentが成立するために必要な条件

Detected Capability
  Runtimeが実際に検出・申告した能力

Executed State
  当該Requestで実際に使用したDevice／Backend／Offload
```

例：

```text
Qwen3-4B Model Definition
  GPU Offloadを必須にしない

macOS Metal Deployment Profile
  gpu_offloadをRequiredとする

Windows CPU Deployment Profile
  gpu_offloadをRequiredとしない
```

Required Capability不足を黙って無視しない。

- 明示Error
- 許可されたFallback
- Degrade Warning
- Execution Refusal
- Audit Log記録

のいずれかへ解決する。

Phase 1-Cでは、許可されていない暗黙Fallbackを実装しない。

## 6. Functional Requirements

### P1C-REQ-001 Deployment固有要件の分離

Model Definition、Model Adapter、Deployment Requirementを分離する。

ModelがCPUで実行可能であるにもかかわらず、特定DeploymentのGPU要件によってModel全体が使用不能にならないこと。

### P1C-REQ-002 ProfileによるHost表現

Deployment Profileは少なくとも次を表現できること。

- OS
- Architecture
- Execution Environment
- Compute Device種別
- Vendor
- Acceleration API
- Backend Adapter
- Backend Build Variant
- Required Runtime Capability

### P1C-REQ-003 Identifierの拡張性

未知の将来Vendor、Acceleration API、BackendまたはDeviceを追加するとき、Application Coreの条件分岐を増殖させない。

安定した共通概念には型を使用してよいが、Vendor名やBackend名を全世界分の閉じたEnumとして固定しない。

識別子はRegistry追加可能なString Keyとして扱う。

### P1C-REQ-004 Profile Resolution

Profile選択Sourceを次の優先順位で解決できるHookを設ける。

```text
Explicit CLI／Application指定
  > Environment指定
  > Platform Default Resolver
```

未対応PlatformをmacOS Profileへ黙ってFallbackしない。

### P1C-REQ-005 Runtime Observation

Runtimeは可能な範囲で次を申告する。

- 実OS
- 実Architecture
- Backend Key／Version
- Build Variant
- Detected Device
- Acceleration API
- GPU Offload有無
- Device ID／Name（取得可能な場合）
- Memory Topology（取得可能な場合）

観測できない情報を推測で補完しない。

### P1C-REQ-006 Model Artifact分離

Logical ModelとArtifact Variantを分離できるHookを維持する。

初期版では現在のGGUFだけを使用するが、将来Safetensors、MLX、ONNX等を同じLogical Modelへ関連づけられる構造を妨げない。

### P1C-REQ-007 Pathの移植性

- Coreで`/`または`\\`へ依存しない
- Python内部は`pathlib`を使用する
- Tracked Configへユーザー固有絶対Pathを保存しない
- Model RootはEnvironmentまたは明示設定で差し替え可能とする
- Windows Symbolic Linkを必須にしない

### P1C-REQ-008 Verification State

設計済み、実装済み、実機検証済みを混同しない。

候補状態：

```text
defined
implemented
statically_verified
native_verified
unsupported
experimental
```

現在の正しい状態：

```text
macOS／Apple Silicon／Metal : native_verified
その他Platform             : definedまたはfuture
```

### P1C-REQ-009 Mac Regression

Phase 1-C実装後も次を維持する。

- Qwen3-4B Metal Load／Unload
- SHA-512常時検証
- Streaming
- Cooperative Cancel
- Thinking Control
- Context Overflow Policy
- Default Test
- Metal Model Smoke

### P1C-REQ-010 追加Dependency抑制

Phase 1-C Hookだけを理由にCUDA、ROCm、Vulkan、PyTorch、MLX、ONNX RuntimeまたはCloud SDKをInstallしない。

## 7. Phase 1-C Implementation Scope

### 実装対象

- Deployment／Platform／Computeを表す最小Contract
- Deployment RequirementとModel Capabilityの分離
- `gpu_offload`要件のmacOS Profile側への移動
- Profile Resolverの差し替え境界
- Runtime Observationの正規化Hook
- Mac Profile Migration
- Unit／Contract Test
- 既存macOS／Metal Regression

### 実装対象外

- Windows実Profile
- PowerShell Setup
- Windows Native Build
- Linux実Profile
- Docker
- CUDA Build
- ROCm／HIP Build
- Vulkan Build
- SYCL／OpenVINO Build
- MLX Adapter
- Transformers Adapter
- vLLM Adapter
- Remote API Adapter
- Multi-GPU実装
- Model Artifact変換
- 追加Model Download

## 8. 将来Profile候補

次は将来追加候補であり、Phase 1-Cの実装対象ではない。

```text
local.macos-arm64.metal
local.macos-arm64.cpu
local.windows-x86_64.cpu
local.windows-x86_64.cuda
local.windows-x86_64.vulkan
local.windows-x86_64.hip
local.linux-x86_64.cpu
local.linux-x86_64.cuda
local.linux-x86_64.rocm
local.linux-x86_64.vulkan
local.linux-x86_64.sycl
local.linux-arm64.cpu
home-server.linux.cuda
home-server.linux.rocm
remote.openai-compatible
cloud.vllm.cuda
cloud.vllm.rocm
cloud.aws-neuron
cloud.google-tpu
```

Hardware、OS、DriverおよびBackendを決定した時点で、必要なものだけを作成・検証する。

## 9. Acceptance Criteria

Phase 1-C HookのAcceptanceは次とする。

1. Model DefinitionからDeployment固有の`gpu_offload必須`が分離されている
2. macOS Metal Profileが`gpu_offload`を明示的に要求する
3. Required CapabilityとDetected Capabilityが比較される
4. 未対応Platformを暗黙にmacOS扱いしない
5. Profile ResolverがTest可能である
6. 将来のOS／Vendor／Acceleration Key追加にCore変更を必須としない
7. Tracked Configへユーザー固有絶対Pathを入れない
8. 既存Default Test、Static CheckおよびMetal Model SmokeがPassする
9. macOS以外を`native_verified`と誤記しない
10. Phase 2以降の機能へ越境しない

## 10. Authorization Boundary

本要件は設計判断の承認を記録する。

Source、Config、Test、Script、DependencyまたはRoot Fileの変更を自動的に許可しない。

実装担当は、専用Handoffを読み、ユーザーからPhase 1-C実装開始と必要なWrite Scopeを明示的に許可された後に作業する。

## 11. 外部参照

- NVIDIA CUDA 10.2 Release Notes: https://docs.nvidia.com/cuda/archive/10.2/pdf/CUDA_Toolkit_Release_Notes.pdf
- llama.cpp Build Documentation: https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- llama-cpp-python README: https://github.com/abetlen/llama-cpp-python/blob/main/README.md
- PyTorch MPS Backend: https://docs.pytorch.org/docs/stable/notes/mps
- vLLM Installation: https://docs.vllm.ai/en/latest/getting_started/installation/index.html
- ONNX Runtime Execution Providers: https://onnxruntime.ai/docs/execution-providers/


<!-- SOURCE_END 20: docs/requirements/phase_1c_deployment_platform_acceleration_requirements_20260719013109.md -->

---

<!-- SOURCE_BEGIN 21: docs/requirements/phase_1d_response_language_requirements_20260719040237.md -->

### Source 21: `docs/requirements/phase_1d_response_language_requirements_20260719040237.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1d_response_language_requirements_20260719040237.md`
- Source SHA-512: `969bf29989da17aec265f9d660bc93ec6de57adb219f9eccd405e4c67bdcda6a10a60e69b0a391171bd9e48415cb00d8576557099051f5a2c7e314abc99c9a74`
- Source Size: `13504` bytes

# Phase 1-D Response Language Policy 要件定義

- 文書ID: `phase_1d_response_language_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:02:37 JST`
- 更新日時: `2026-07-19 04:02:37 JST`
- Snapshot: `20260719040237`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D、Response Language、Config、Prompt Composition、CLI
- 正本言語: 日本語
- 上位要件: [project_requirements_20260718193435.md](../history/requirements/project_requirements_20260718193435.md)
- 前Phase最終Review: [designer_review_phase_1c_final_20260719035156.md](../history/handoffs/designer_review_phase_1c_final_20260719035156.md)
- Architecture: [phase_1d_response_language_architecture_20260719040237.md](../history/architecture/phase_1d_response_language_architecture_20260719040237.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- supersedes: なし（新規Phase 1-D専用Requirements系列）

## 1. 結論

Phase 1-Dでは、回答言語の既定値をModel、Backend Adapterまたは個別Promptへハードコードせず、交換可能なResponse Language PolicyとしてApplication側に追加する。

初期Contractは次とする。

```text
Allowed Response Language : ja／en／auto
Built-in Default          : ja
Tracked Profile Default   : ja
Phase 1 CLI Override      : --response-language
Environment Override      : MARGPA_RESPONSE_LANGUAGE
Policy Owner              : Application／Orchestration
Model Adapter Modification: 原則不要
```

Phase 1-Dは「既定の回答言語を指定する機能」である。Modelが実際に出力した自然言語を完全に識別・強制・保証する機能ではない。

## 2. 背景

Phase 1-BのQwen3-4B実機確認では、同じ日本語Promptでも、回答言語を明示しない場合に英語で出力し、`日本語で`を加えた場合に日本語で出力する事象を確認した。

この事象は小型Modelだけを原因とするものではない。

- Project ContextがModelへ渡されていない
- 回答言語の既定値が存在しない
- Promptが複数解釈可能である
- Thinkingが誤った前提を深掘りする場合がある
- ThinkingとFinal Answerが同じToken Budgetを消費する

ユーザーは英語を常用しないため、初期Deploymentでは日本語を既定値とする必要がある。一方、将来の英語利用、Model交換、Cloud移行およびAPI利用に備え、言語指定をModel固有実装へ閉じ込めてはならない。

## 3. Phase分割

Phase 1の残りを次のように分割する。

```text
Phase 1-D : Response Language Policy
Phase 1-E : Thinking Presentation Policy
```

Phase 1-Dに含めるもの：

- `ja／en／auto` Contract
- Default Language
- Profile／Environment／CLI Override
- Effective Policy解決
- System Message Composition
- Config／CLI／Audit向け表示
- Unit／Integration／Native Smoke

Phase 1-Eへ送るもの：

- Thinking実行と表示の分離
- `<think>`表示／非表示
- Thinking Label変更
- Streaming Thinking Filter
- Malformed Thinking Tag Policy
- Raw Output／Display Output分離
- Raw Thinking保存方針
- Thinking用Sampling Profile

## 4. 用語

### 4.1 Response Language Policy

回答時にModelへ与える既定の言語方針。

### 4.2 Effective Response Language

Profile、Environmentおよび明示Overrideを解決した結果、当該Requestへ適用するPolicy値。

### 4.3 Observed Output Language

Modelが実際に生成した文章の言語。

Phase 1-Dでは、Effective Response LanguageとObserved Output Languageを同一視しない。

### 4.4 `auto`

Applicationが特定言語のSystem Instructionを追加せず、明示System Message、User Prompt、Conversation ContextおよびModel挙動へ委ねるMode。

`auto`は自動言語判定Classifierの実装を意味しない。

## 5. Functional Requirements

### FR-1 Response Language Contract

初期値は次の3値だけを受理する。

```text
ja
en
auto
```

- 大文字小文字や未知Aliasを黙って正規化しない
- 未知値は`invalid_configuration`またはCLI Parse Errorとして拒否する
- 将来BCP 47相当へ拡張可能な境界を維持する
- Phase 1-Dで全言語一覧を実装しない

### FR-2 Default

Built-in DefaultとCurrent Tracked Profile Defaultは`ja`とする。

既定値は利用者の明示的な別言語指定を禁止する強制Policyではない。

### FR-3 Tracked Profile

Current Deployment Profileへ次を追加する。

```toml
[response]
language = "ja"
```

Profile Schemaは、構造変更を明示するため`2`から`3`へ更新する。

Model Registry Schemaは変更しない。

### FR-4 Environment Override

次を受理する。

```text
MARGPA_RESPONSE_LANGUAGE=ja
MARGPA_RESPONSE_LANGUAGE=en
MARGPA_RESPONSE_LANGUAGE=auto
```

未知値は安全な設定Errorとする。

### FR-5 CLI Override

`generate` Commandへ次を追加する。

```text
--response-language ja
--response-language en
--response-language auto
```

CLIは許可値以外をParse段階で拒否する。

`model-info`はProfile／Environmentから解決したPolicyを表示する。Request専用CLI Overrideは`generate`にだけ適用する。

### FR-6 Precedence

Phase 1-Dの構造化設定は、次の優先順位で解決する。

```text
Per-request Explicit Override
  > Environment Override
  > Deployment Profile
  > Built-in Default
```

Phase 2以降の追加候補：

```text
API Request Override
  > Session Preference
  > User Preference
  > Deployment Profile
  > Built-in Default
```

Phase 1-DでSession／User Preference Storageを実装しない。

### FR-7 Natural-language Instruction

User PromptまたはUser指定System Messageに「英語で」「日本語で」等が書かれている場合、Modelがその明示指示を優先できる内容のDefault Policy Instructionとする。

ただしPhase 1-Dでは、自然文から言語指定を抽出するClassifier、正規表現判定またはLLM判定を実装しない。

そのため、構造化されたEffective Policyと、Modelが自然文を解釈した結果が異なる可能性を認める。これを黙って「Language Policy適用成功」と断定しない。

### FR-8 System Message Composition

Language PolicyはApplication／Orchestration層でSystem InstructionへCompileする。

要件：

- `ja`では日本語Default Instructionを追加する
- `en`では英語Default Instructionを追加する
- `auto`ではLanguage Instructionを追加しない
- User Prompt本文を変更しない
- User指定`--system`を破棄・置換しない
- Project PolicyとUser指定System Instructionを決定論的に合成する
- Model Adapterへ日本語／英語Instructionをハードコードしない
- CLIと将来APIで同じComposerを再利用できる

初期Instructionの意味：

```text
ja   : 原則として日本語で回答する。Userが別言語を明示した場合はその指定に従う。
en   : 原則として英語で回答する。Userが別言語を明示した場合はその指定に従う。
auto : Applicationによる言語指定を加えない。
```

### FR-9 Prompt Ownership

合成後のSystem Messageでは、Projectが追加したLanguage PolicyとUserが指定したSystem Instructionの境界を一定形式で保持する。

User指定文字列は内容を改変せず、合成後Message内に保持する。

生のUser指定System Messageと合成後System Messageを将来Auditで区別できる設計とする。ただしPhase 1-DでAudit永続化は実装しない。

### FR-10 Config Observability

Effective Configおよび`model-info`で最低限次を確認できるようにする。

```text
response_language
response_language_source
```

Source候補：

```text
built_in_default
profile
environment
explicit
```

Applied PolicyをModelのObserved Output Languageとして記録しない。

### FR-11 Streaming／Non-streaming Parity

StreamingとNon-streamingで同じMessage ComposerとEffective Policyを使用する。

CLI描画後に言語を変換しない。

### FR-12 Existing System Flag Compatibility

次の既存形式を維持する。

```text
margpa-llm generate --prompt "..."
margpa-llm generate --prompt "..." --system "..."
```

Language Policy追加によって`--system`が無視されてはならない。

### FR-13 Error Handling

Config／Environmentの不正Languageは既存の安全な`InferenceError`境界へ変換する。

Errorへ次を含めない。

- User Prompt全文
- System Message全文
- Secret
- Absolute Model Path

### FR-14 Model Independence

Phase 1-DのContract、ResolverおよびComposerはQwen3、GGUF、llama.cpp、MetalまたはmacOSへ依存しない。

Current Native VerificationはQwen3-4B／llama.cpp／Metalで実施してよいが、Core Policyは将来Adapterでも利用可能にする。

### FR-15 Existing Behavior Preservation

次をRegressionさせない。

- Model Load／Unload
- One-shot Generation
- Streaming
- Cancel
- Thinking実行On／Off
- Generation Override
- Profile Resolution
- Deployment Validation
- `model-info`
- Model Artifact SHA-512検証

## 6. Non-functional Requirements

### NFR-1 疎結合

- Model PortへLanguage固有Fieldを要求しない
- llama.cpp AdapterへLanguage Policyを持たせない
- EntrypointだけにBusiness Ruleを閉じ込めない
- Pure Functionまたは小さなServiceとしてTest可能にする

### NFR-2 依存性

Phase 1-Dのために新しい外部Libraryを追加しない。

### NFR-3 Immutability／Validation

既存のImmutable Pydantic Contractと`extra="forbid"`方針を維持する。

### NFR-4 Reproducibility

Tracked ProfileへDefaultを明示し、Profile Hash変更を実装担当Statusへ記録する。

### NFR-5 Audit Readiness

将来のAudit Logで次を区別できるField境界を維持する。

- Requested／Effective Response Language
- Policy Source
- Applied Language Instruction
- User System Message
- Model Output
- Observed Output Language（将来Evaluation）

## 7. Scope外

- Output Language Classifier
- 翻訳
- 言語ごとのModeration Model
- 言語ごとのRAG Index
- BCP 47全対応
- Session／User Preference永続化
- Web UI Language Selector
- API実装
- Thinking表示／非表示
- Thinking Label
- `<think>` Parser
- Streaming Thinking Filter
- Raw Thinking保存
- High-Level Explanation
- Governance Score
- Guard Model／Judge Model呼び出し
- Model Download／変更
- Dependency追加

## 8. Required Test

### Contract／Config

- `ja／en／auto`を受理する
- 未知値を拒否する
- Profile Defaultが`ja`
- Schema Version `3`を受理する
- 旧／未知Schemaを黙って受理しない
- Environment Overrideを解決する
- Explicit OverrideがEnvironmentより優先される
- EnvironmentがProfileより優先される
- Sourceが正しく記録される

### Message Composition

- `ja` Instructionを追加する
- `en` Instructionを追加する
- `auto`でLanguage Instructionを追加しない
- User Promptを変更しない
- User System Messageを保持する
- User Systemなし／ありの両方
- Streaming／Non-streamingが同じMessage列を使う
- Model Adapter固有機能を呼ばずにUnit Testできる

### CLI

- `--response-language ja／en／auto`
- 未知値のParse拒否
- Flag省略時はProfile／Environmentを使用
- `model-info`にEffective LanguageとSourceを表示
- 既存Generation Flagとの併用

### Regression

- Ruff Format Check
- Ruff Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Model Smoke
- Qwen3 Default Japanese Smoke
- Qwen3 Explicit English Smoke

Native Outputは確率的であるため、Unit Testの決定論的Message Compositionを正本Gateとし、Native Smokeは実Modelへの伝達確認として扱う。

## 9. Acceptance Criteria

1. `ja／en／auto`が型付きContractとして存在する
2. Defaultが`ja`である
3. Profile Schemaが`3`へ更新される
4. `MARGPA_RESPONSE_LANGUAGE`が機能する
5. `--response-language`が機能する
6. Explicit > Environment > Profile > Built-inの順で解決される
7. Effective LanguageとSourceを確認できる
8. `auto`が特定言語Instructionを注入しない
9. User PromptとUser System Messageが保持される
10. ComposerがModel Adapterから独立している
11. Streaming／Non-streamingが同じPolicyを使う
12. Thinking表示機能が混入していない
13. 新規外部Dependencyがない
14. Static／Default Testが全件Passする
15. Current Mac／Metal RuntimeがRegressionしない

## 10. Authorization Boundary

本Requirements、Architecture、ADR、HandoffおよびIndexの作成はユーザーが許可した要件・設計作業である。

Source、Config、Test、Script、DependencyまたはRoot Fileの変更は、Phase 1-D実装開始についてユーザーから明示的な許可を得た後に行う。

## 11. Phase 1-D完了境界

Phase 1-D完了とは、Current ProfileのDefault日本語、`ja／en／auto`切替、解決優先順位、Message Composition、CLI、Config表示およびRegressionが成立した状態を意味する。

Phase 1-D完了は、Modelが常に指定言語だけを出力する保証、Thinking非表示、Raw Thinking非保存またはPhase 1-E完了を意味しない。

<!-- SOURCE_END 21: docs/requirements/phase_1d_response_language_requirements_20260719040237.md -->

---

<!-- SOURCE_BEGIN 22: docs/requirements/phase_1d_response_language_requirements_20260719041847.md -->

### Source 22: `docs/requirements/phase_1d_response_language_requirements_20260719041847.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1d_response_language_requirements_20260719041847.md`
- Source SHA-512: `c366f0d05145ce7d9df84dabf5eb3cea14b7109ab0d31bd970a231d305cfbcf15b508efdb9725db298c1f704abbc6efb508029f66f654dbfce939224df134321`
- Source Size: `8809` bytes

# Phase 1-D Response Language Policy 要件定義

- 文書ID: `phase_1d_response_language_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 04:18:47 JST`
- 更新日時: `2026-07-19 04:18:47 JST`
- Snapshot: `20260719041847`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-D、Configuration Layer分離、Response Language、Prompt Composition、CLI
- 正本言語: 日本語
- Configuration Requirements: [configuration_layer_requirements_20260719041847.md](../history/requirements/configuration_layer_requirements_20260719041847.md)
- Architecture: [phase_1d_response_language_architecture_20260719041847.md](../history/architecture/phase_1d_response_language_architecture_20260719041847.md)
- Accepted ADR: [adr_0008_response_language_policy_20260719040237.md](../history/adr/adr_0008_response_language_policy_20260719040237.md)
- Amendment ADR: [adr_0009_application_deployment_configuration_separation_20260719041847.md](../history/adr/adr_0009_application_deployment_configuration_separation_20260719041847.md)
- supersedes: `phase_1d_response_language_requirements_20260719040237.md`

## 1. 結論

Phase 1-Dは次の二つを同じMigration単位で実施する。

1. Application共通設定とDeployment Profileの責務分離
2. `ja／en／auto` Response Language Policy

Response LanguageはPlatform固有設定ではないため、`local_macos_arm64.toml`へ追加しない。

```text
config/application.toml
  └─ [response]
       language = "ja"
```

## 2. 前版からの変更

前版の次を修正する。

```text
Old:
  local_macos_arm64.tomlへ[response]を追加
  Response追加を理由にProfile Schema 3へ更新

New:
  config/application.tomlへ[response]を追加
  Application Config Schemaを1で新設
  Deployment Profileは共通Field分離を理由にSchema 3へ更新
```

次は維持する。

- Allowed `ja／en／auto`
- Default `ja`
- Application／Orchestration Ownership
- Explicit > Environment > Application > Built-in
- System Message Composition
- Natural-language Classifierを実装しない
- Phase 1-E Thinking Presentationとの分離

## 3. Phase 1-D Scope

### Configuration Layer

- `config/application.toml`
- `ApplicationConfig` Contract／Loader
- `DeploymentProfile` Schema `3`
- Application共通FieldのProfileからの除去
- Typed Effective Config Composer
- Field別Precedence
- Config Source表示

### Response Language

- `ResponseLanguage`: `ja／en／auto`
- Built-in／Application Default `ja`
- `MARGPA_RESPONSE_LANGUAGE`
- `--response-language`
- Effective Policy／Source
- System Message Composer
- Streaming／Non-streaming Parity

## 4. Configuration Ownership

### `config/application.toml`

- `selected_model`
- `model_root`
- Common `load_defaults`
- `generation`
- `response`

### `config/profiles/local_macos_arm64.toml`

- Host
- Compute
- Backend Runtime
- Runtime Requirements
- Hardware `load_overrides`
- Verification State

### `config/models/qwen3_4b_q4_k_m.toml`

- Artifact／Hash／Quantization
- Model Architecture／Native Limit
- Model Capability／Provenance

## 5. Application Config

Phase 1-DのTracked Default：

```toml
schema_version = "1"
application_key = "default"
selected_model = "main.qwen3-4b-q4-k-m"

[model_root]
default = "./models"
environment_variable = "MARGPA_MODEL_ROOT"

[load_defaults]
context_size = 4096
verbose_backend = false
verify_artifact_hash = true

[generation]
max_new_tokens = 512
temperature = 0.7
top_p = 0.8
top_k = 20
min_p = 0.0
presence_penalty = 1.5
frequency_penalty = 0.0
repeat_penalty = 1.0
stop_sequences = []
thinking_mode = "disabled"

[response]
language = "ja"
```

## 6. Response Language Contract

```text
ja   : 日本語を既定とする
en   : 英語を既定とする
auto : ApplicationからLanguage Instructionを追加しない
```

- 未知値を拒否する
- `jp`等を`ja`へ黙ってAlias変換しない
- Phase 1-DでBCP 47全対応を実装しない
- `auto`はLanguage Classifierではない

## 7. DefaultとOverride

```text
Per-request／CLI Explicit
  > MARGPA_RESPONSE_LANGUAGE
  > Application Config [response]
  > Built-in Default ja
```

Deployment ProfileはResponse LanguageをOverrideできない。

Phase 2以降にSession／User Preferenceを追加可能とする。

## 8. System Message Composition

Language PolicyはApplication／Orchestration層でSystem InstructionへCompileする。

### `ja`

```text
回答は原則として日本語で行ってください。
ユーザーが回答言語を明示的に指定した場合は、その指定を優先してください。
```

### `en`

```text
Respond in English by default.
If the user explicitly requests a different response language, follow that request.
```

### `auto`

Language Instructionを追加しない。

要件：

- User Promptを変更しない
- User指定System Messageを破棄しない
- Project PolicyとUser Systemを決定論的に合成する
- CLIと将来APIで同じComposerを使う
- Model AdapterへLanguage文言を置かない

## 9. Structured PolicyとNatural Language

Phase 1-DはDefault Languageを指定する機能であり、Strict Output Enforcementではない。

User Prompt内の「英語で」「日本語で」等をApplicationで解析しない。Default Instructionを通じてModelがUserの明示指定へ従えるようにする。

Applied PolicyとObserved Output Languageを同一視しない。

## 10. Deployment Profile Migration

Current ProfileをSchema `3`へMigrationする。

削除：

```text
selected_model
model_root
generation
loadの共通Field
```

維持：

```text
profile_key
verification_state
host
compute
backend_runtime
runtime_requirements
```

追加／変更：

```text
[load] → [load_overrides]
Hardware Tuning Fieldだけ
```

## 11. Typed Composition

Generic Deep Mergeは禁止する。

```text
Load:
  Explicit > Environment > Deployment Override
           > Application Default > Built-in

Generation:
  Request > Environment > Application > Built-in

Response:
  Request > Environment > Application > Built-in
```

DeploymentはGenerationとResponseを変更できない。

## 12. Observability

`model-info`で最低限次を確認可能にする。

```text
application_key
profile_key
selected_model
load
generation
response.language
response.source
profile_resolution_source
applied_sources
```

## 13. Existing Behavior Preservation

- Model Load／Unload
- Generate／Streaming／Cancel
- Thinking実行On／Off
- Generation Override
- Profile Resolution
- Deployment Validation
- Artifact SHA-512
- `model-info`
- Current Mac／Metal Runtime

## 14. Phase 1-E Scope外

- `<think>`表示／非表示
- Thinking Label
- Model Protocol Parser
- Streaming Thinking Filter
- Raw／Display Output分離
- Raw Thinking保存
- Thinking Sampling Profile
- High-Level Explanation

## 15. その他Scope外

- Language Detection Classifier
- Translation
- Session／User Preference Storage
- Web UI／API
- Multiple Application Config Selector
- Generation／Response Preset Directory
- Dynamic Reload
- Remote Config
- New External Dependency
- Windows／Linux実Profile

## 16. Required Tests

### Configuration

- Application Schema `1`
- Deployment Schema `3`
- Ownership違反Field拒否
- Typed Load Composition
- Field別Precedence
- Selected Model／Deployment Backend整合
- Migration前後のEffective値一致

### Language

- `ja／en／auto`
- Unknown拒否
- Application Default `ja`
- Environment／CLI Override
- Source Tracking
- 6つのMessage Composition Case
- User Prompt／System保持
- Streaming／Non-streaming Parity

### Regression

- Ruff Format／Check
- Mypy Strict
- Default pytest
- Environment Verification
- Bash Syntax
- `uv lock --check`
- Exact Offline Dry Run
- Metal Smoke
- Default `ja`／Explicit `en`／`auto` Native Smoke

## 17. Acceptance Criteria

1. `config/application.toml`が共通正本になる
2. Application Config Schema `1`がStrict Validationされる
3. Deployment Profile Schema `3`がStrict Validationされる
4. Platform Profileから共通Fieldが除かれる
5. Typed ComposerがEffective Configを生成する
6. PlatformがGeneration／Responseを上書きできない
7. `ja／en／auto`が機能する
8. Defaultが`ja`である
9. Environment／CLI Overrideが機能する
10. Effective Language Sourceを確認できる
11. ComposerがAdapter非依存である
12. User Prompt／System Messageが保持される
13. Phase 1-E機能が混入しない
14. 新規外部Dependencyがない
15. Static／Default TestがPassする
16. Current Mac／Metal RuntimeがRegressionしない

## 18. Authorization Boundary

本RequirementsはAcceptedである。

Source、Config、Test、ScriptまたはDependencyの変更は、ユーザーがPhase 1-D実装開始を明示した後に行う。

<!-- SOURCE_END 22: docs/requirements/phase_1d_response_language_requirements_20260719041847.md -->

---

<!-- SOURCE_BEGIN 23: docs/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md -->

### Source 23: `docs/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md`
- Source SHA-512: `e33fb2f3b6fd4f572c8ff64f2b19c6f3c8022954fbf18d3f3384907b5745ab7e94920a0ee2509f91e2fdae001fb7ee3e9fd18d324ddd50157f06f7ceacaf4de4`
- Source Size: `15461` bytes

# Phase 1-E Thinking Presentation 要件定義

- 文書ID: `phase_1e_thinking_presentation_requirements`
- 状態: `proposed_ready_for_user_review`
- 作成日時: `2026-07-19 12:35:47 JST`
- 更新日時: `2026-07-19 12:35:47 JST`
- Snapshot: `20260719123547`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E、Thinking実行、Output Protocol正規化、表示、Streaming、保存境界
- 正本言語: 日本語
- 設計元: [response_language_and_thinking_output_policy_20260719013109.md](../history/architecture/response_language_and_thinking_output_policy_20260719013109.md)
- Architecture: [phase_1e_thinking_presentation_architecture_20260719123547.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719123547.md)
- Proposed ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719123547.md)
- supersedes: なし（Phase 1-E Requirements新規系列）

## 1. 結論

Phase 1-Eでは、次の4責務を独立したContractとして実装する。

```text
Thinking Execution   : ModelにThinkingを実行させるか
Protocol Parsing     : Model固有OutputをReasoningとFinalへ正規化する
Presentation         : Reasoningを利用者へ表示するか
Persistence          : Raw Reasoningを永続化するか
```

これらを一つのBooleanへ統合しない。

Phase 1-Eの初期値は次とする。

```text
Thinking Execution   : disabled
Thinking Visibility  : hidden
Display Label        : 推論
Raw Persistence      : disabled
```

## 2. 背景

Current Runtimeには`ThinkingMode`があり、CLIの`--thinking`でQwen3のThinking実行を切り替えられる。

しかし、Current CLIはModelが生成した`<think>...</think>`をRaw Textのまま表示する。次は未分離である。

- Thinkingを実行するか
- Thinkingを見せるか
- Canonical Protocol Tagと表示Tag
- Reasoning ContentとFinal Content
- Non-streamingとStreamingの表示動作
- 表示とAudit保存

利用者は、Application Configで日本語または英語を切り替えるのと同様に、Thinkingの表示／非表示と表示ラベルを変更できる必要がある。

## 3. 用語

### 3.1 Raw Model Output

Model Portが返した未変換のText。Current `GenerationResult.content`と`GenerationChunk.text_delta`が該当する。

### 3.2 Canonical Thinking Protocol

ModelまたはChat Templateが使用する機械的Delimiter。Current Qwen3では次である。

```text
<think>
</think>
```

### 3.3 Normalized Output

Raw Model Outputを次へ分離した内部表現。

```text
reasoning_content
final_content
parse_status
parse_warnings
```

### 3.4 Display Output

VisibilityとDisplay Labelを適用し、CLI／将来API／Web UIへ渡す表示用Output。

## 4. Phase 1-E Scope

- Application Config Schema `2`へのMigration
- `[presentation.thinking]`追加
- Thinking Presentation用のImmutable Contract
- Field別PrecedenceとSource Tracking
- Model DefinitionのOutput Protocol宣言
- Parser KeyによるParser選択
- Tagged Thinking Output Parser
- Non-streaming正規化と表示
- Stateful Streaming Parser
- Hidden ModeでのReasoning非表示
- Visible ModeでのUser-defined Display Label
- Parse Status／Warning
- CLI Override
- `model-info`のEffective Presentation表示
- Current Mac／Metal RuntimeのRegression確認

## 5. Scope外

- Thinkingが正しいことの保証
- Thinking内容の品質評価
- High-level Explanation生成
- Raw Chain of ThoughtのAudit Log保存
- Thinkingの自動要約
- Thinking用Sampling Presetの自動適用
- ThinkingのToken Budget分離
- Strict Language Enforcement
- Web UI／API
- Multi-turn Session
- Governance／Judge／Repair
- 新規外部Dependency

## 6. Configuration Migration

`config/application.toml`をSchema `1`から`2`へMigrationする。

Deployment Profile Schema `3`は変更しない。PresentationはOS／GPU／Backend固有ではないため、Deployment Profileには置かない。

```toml
schema_version = "2"

[presentation.thinking]
visibility = "hidden"
display_label = "推論"
persistence = "disabled"
```

Current `[generation].thinking_mode`は保持する。

```toml
[generation]
thinking_mode = "disabled"
```

## 7. Thinking Execution Contract

Existing Contractを維持する。

```text
disabled      : Thinking実行を無効化
enabled       : Thinking実行を有効化
model_default : Model／Templateの既定動作に委ねる
```

Presentation設定はThinking Executionを暗黙変更しない。

## 8. Thinking Presentation Contract

### Visibility

```text
hidden  : CanonicalなReasoning SectionをDisplay Outputへ出さない
visible : Canonical TagをDisplay Labelへ変換して表示する
```

Unknown Valueを拒否する。`on／off`等を黙ってAlias変換しない。

### Display Label

Defaultは`推論`とする。

CLI Visible Outputは次の形である。

```text
<推論>
Reasoning Content
</推論>
Final Content
```

`display_label = "思考過程"`であれば次のようになる。

```text
<思考過程>...</思考過程>
```

Display Labelは次を満たす。

- 1～64文字
- 空白だけでない
- 先頭／末尾空白を許可しない
- `<`、`>`、`/`を含まない
- CR／LF／制御文字を含まない
- 日本語、英語等のUnicode文字は許可する

Display LabelはModelへ送信しない。

## 9. Persistence Contract

Phase 1-Eでは次のみを許可する。

```text
persistence = "disabled"
```

- Raw ReasoningをFile／JSON／JSONL／Databaseへ保存しない
- Visibleであっても保存を意味しない
- Parserが一時的にMemory上で扱うことは永続化ではない
- 将来Persistenceを追加する場合は、別Requirements／ADR／Audit Policyを必要とする

`enabled`等の未対応値は拒否する。

## 10. PrecedenceとSource Tracking

### Visibility

```text
CLI Explicit
  > MARGPA_THINKING_VISIBILITY
  > Application Config
  > Built-in hidden
```

### Display Label

```text
CLI Explicit
  > MARGPA_THINKING_LABEL
  > Application Config
  > Built-in 推論
```

### Persistence

```text
Application Config
  > Built-in disabled
```

Phase 1-EでPersistenceのEnvironment／CLI Overrideは許可しない。

FieldごとにSourceを保持する。

```text
visibility_source
display_label_source
persistence_source
```

## 11. CLI Contract

ExistingのExecution Flagを維持する。

```text
--thinking
--no-thinking
```

Presentation Flagを追加する。

```text
--show-thinking
--hide-thinking
--thinking-label "推論"
```

`--show-thinking`と`--hide-thinking`はMutually Exclusiveとする。

Example：

```bash
margpa-llm generate \
  --prompt "設計案を考えて" \
  --thinking \
  --show-thinking \
  --thinking-label "推論"
```

`--show-thinking`だけを指定してもThinking Executionを自動で`enabled`にしない。

## 12. Execution／Presentation Matrix

| Execution | Visibility | 期待動作 |
|---|---|---|
| `disabled` | `hidden` | Finalだけ表示 |
| `disabled` | `visible` | Reasoningが存在しなければFinalだけ表示 |
| `enabled` | `hidden` | Thinkingは実行し得るがFinalだけ表示 |
| `enabled` | `visible` | ReasoningをDisplay Label付きで表示し、続けてFinalを表示 |
| `model_default` | `hidden` | Model既定動作、Canonical Reasoningは非表示 |
| `model_default` | `visible` | Model既定動作、Reasoning検出時のみ表示 |

## 13. Model Output Protocol Definition

Parser選択をModel Key／Architecture／Backend名のハードコードで行わない。

Model Definitionが次を宣言する。

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Display LabelはModel Definitionへ置かない。

Unknown Parser Keyは黙ってPlain TextへFallbackせず、Application Build時に明示Errorとする。

将来のModelは`plain_text_v1`、`tagged_thinking_v1`または追加Parser KeyをDefinitionで選べる構造とする。

## 14. Parser Semantics

Phase 1-EのTagged Parserは、先頭の単1個のCanonical Thinking SectionだけをProtocolとして解釈する。

```text
[optional leading whitespace]
<think>
reasoning
</think>
final
```

規則：

1. 先頭にOpening Delimiterがなければ、全TextをFinalとする
2. Opening／Closingが完成していればReasoningとFinalへ分離する
3. Opening後にClosingがなければ`unclosed_reasoning`とする
4. Final内のTagらしきTextはユーザーContentの可能性があるため黙って削除しない
5. Parseで判断した結果とWarningを返す

Parse Status：

```text
plain_text
complete
unclosed_reasoning
malformed_protocol
```

ParserはReasoningの真実性、正しさまたは内部推論との一致を主張しない。

## 15. Non-streaming要件

- Raw `GenerationResult`は改変しない
- Presentation ServiceがRaw Contentを受け取る
- ParserでNormalized Outputを作る
- RendererでDisplay Outputを作る
- Hiddenでは`final_content`だけを表示する
- VisibleではCanonical TagだけをDisplay Tagへ変換する
- Final Contentの文字を無断でTrim／要約／翻訳しない

## 16. Streaming要件

Streaming ParserはStatefulとする。Chunk単位のRegex置換だけで実装しない。

```text
detecting_prefix
inside_reasoning
after_reasoning
plain_text
terminal
```

必須動作：

- `<think>`または`</think>`が複数Chunkへ分割されても検出できる
- Prefix判定中は最小限のSuffix Bufferを保持する
- HiddenでReasoning Chunkを一瞬表示して後から消す動作を禁止する
- VisibleでCanonical Delimiterをそのまま表示しない
- Final Chunk、Finish Reason、Usage、Cancel／CloseのSemanticsを壊さない
- StreamingとNon-streamingで同じRaw Outputから同じDisplay Outputを得る

## 17. Malformed時の方針

### Openingなし

全TextをFinalとし、原則Warningなしとする。Thinkingが生成されない正常系を許容するためである。

### Openingあり／Closingなし

- Status: `unclosed_reasoning`
- Warningを付与する
- Hidden: Reasoningと判定した部分を表示しない
- Visible: Display Opening TagとReasoningを表示し、TerminalでDisplay Closing Tagを補う
- Final Contentは空とする

### Extra／Unexpected Delimiter

- User Contentの可能性があるため黙って削除しない
- `malformed_protocol`またはWarningとして観測可能にする
- Phase 1-EのHiddenは安全性Guardrailではなく、Canonical Leading SectionのPresentation Policyである

## 18. Privacy／Audit境界

- Raw Reasoningを生のChain of Thoughtの真の内部記録と主張しない
- VisibilityとPersistenceを同一視しない
- HiddenをSecurity／Secret Redactionの代替としない
- Current CLIに新しいRaw Output保存機能を追加しない
- 将来Audit LogではHigh-level Process SummaryとSystem Traceを優先する
- Parser Warning／Parse StatusはRaw Reasoning本文なしで監査可能にする

## 19. Thinking Sampling Policy

Phase 1-EではThinking Modeに応じたSampling Parameterの自動変更を行わない。

理由：

- `--thinking`がTemperature等を暗黙変更すると再現性が下がる
- Thinking ExecutionとGeneration Tuningは別責務である
- Modelごとの推奨値は今後変わり得る
- Phase 2以降のExplicit Experiment Presetで比較する方が適する

Current Generation Overrideをそのまま使用できる状態を維持する。

## 20. Observability

`model-info`に最低限次を含める。

```text
effective_config.generation.thinking_mode
effective_config.presentation.thinking.visibility
effective_config.presentation.thinking.display_label
effective_config.presentation.thinking.persistence
effective_config.presentation.thinking.visibility_source
effective_config.presentation.thinking.display_label_source
effective_config.presentation.thinking.persistence_source
model.output_protocol.thinking.parser_key
```

Runtime生成ごとのParse Status／WarningはPresentation Resultから参照できるようにする。

## 21. Existing Behavior Preservation

- Model Load／Unload
- Non-streaming Generation
- Streaming／Cancel／Close
- Token Usage／Timing／Finish Reason
- Artifact SHA-512
- `ja／en／auto`
- User System Message合成
- Generation Override
- Deployment／Platform Validation
- Current Mac／Metal Runtime
- `GenerationResult`／`GenerationChunk`／Model PortのRaw Contract

## 22. Required Tests

### Config

- Application Schema `2`
- Schema `1`を黙って受理しない
- Default `hidden／推論／disabled`
- Environment／CLI Precedence
- Field別Source
- Invalid Visibility／Label／Persistence拒否
- Deployment ProfileがPresentationを所有できない

### Model Protocol

- Model Definition Schema `2`
- Parser Key／Delimiter検証
- Unknown Parser Key拒否
- Parser選択にModel Key／Architectureの分岐がない

### Non-streaming

- Plain Text
- Complete Thinking Section
- Hidden／Visible
- Custom Label
- Unclosed Reasoning
- Extra Delimiter
- Final Content保持
- Raw Result不変

### Streaming

- Opening Delimiterの全Chunk分割パターン
- Closing Delimiterの全Chunk分割パターン
- 1文字Chunk
- Empty Delta
- Hidden No-flash
- Visible Label
- Malformed Terminal
- Non-streaming Parity
- Finish／Usage／Cancel／Close保持

### CLI／Regression

- `--thinking`と`--show-thinking`の独立
- `--show-thinking／--hide-thinking`の排他
- `--thinking-label`
- `model-info`
- Ruff Format／Check
- Mypy Strict
- Default Pytest
- Environment／Lock／Offline Gate
- Native Metal Thinking Hidden／Visible Smoke
- Phase 1-D Language Smoke

## 23. Acceptance Criteria

1. Thinking ExecutionとVisibilityが独立している
2. PersistenceがVisibilityから独立し、`disabled`に固定される
3. Application Config Schema `2`がStrict Validationされる
4. Deployment Profile Schema `3`が変更されない
5. Defaultが`disabled／hidden／推論／disabled`である
6. Visibility／LabelのEnvironment／CLI Overrideが機能する
7. Field別Sourceを確認できる
8. Canonical DelimiterとDisplay Labelが分離される
9. ParserがModel DefinitionのParser Keyから選択される
10. Model Key／Architecture／Backend名を用いたParserハードコードがない
11. Non-streamingでReasoning／Finalが正規化される
12. StreamingでDelimiterがChunk分割されても正しく動作する
13. Hidden StreamingでReasoningが一瞬表示されない
14. VisibleでCustom Display Labelが使用される
15. Malformed Protocolが決定論的に処理され、Warningが得られる
16. Raw `GenerationResult`／`GenerationChunk`が改変されない
17. StreamingのFinish／Usage／Cancel／Closeが保持される
18. Raw Reasoningが新しく永続保存されない
19. Sampling ParameterがThinking Flagで暗黙変更されない
20. 新規外部Dependencyがない
21. Static／Default TestがPassする
22. Current Mac／Metal RuntimeがRegressionしない

## 24. Authorization Boundary

本書はPhase 1-Eの提案Requirementsである。

ユーザーによるDecision承認前は、次を解禁しない。

- Source／Config／Test実装
- Existing Fileの変更
- Dependency追加
- Model Download
- Phase 2以降の実装


<!-- SOURCE_END 23: docs/requirements/phase_1e_thinking_presentation_requirements_20260719123547.md -->

---

<!-- SOURCE_BEGIN 24: docs/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md -->

### Source 24: `docs/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md`
- Source SHA-512: `3068ec66bdb07e28b5c1d7081dc3146e53eea734138319ca97084609d9018835d5237cba0790b895aba9e8b2504701bc92bec4f088f247929794cd8b1afcf068`
- Source Size: `12610` bytes

# Phase 1-E Thinking Presentation 要件定義

- 文書ID: `phase_1e_thinking_presentation_requirements`
- 状態: `accepted_ready_for_implementation_authorization`
- 作成日時: `2026-07-19 13:03:03 JST`
- 更新日時: `2026-07-19 13:03:03 JST`
- 承認日時: `2026-07-19 13:03:03 JST`
- Snapshot: `20260719130303`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: Phase 1-E、Thinking実行、Output Protocol正規化、表示、Streaming、保存境界
- 正本言語: 日本語
- Architecture: [phase_1e_thinking_presentation_architecture_20260719130303.md](../history/architecture/phase_1e_thinking_presentation_architecture_20260719130303.md)
- Accepted ADR: [adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md](../history/adr/adr_0014_thinking_execution_presentation_and_persistence_separation_20260719130303.md)
- supersedes: `phase_1e_thinking_presentation_requirements_20260719123547.md`

## 1. 承認結論

Phase 1-Eは、次の4責務を独立したContractとして実装する。

```text
Thinking Execution   : ModelにThinkingを実行させるか
Protocol Parsing     : Model固有OutputをReasoningとFinalへ正規化する
Presentation         : Reasoningを利用者へ表示するか
Persistence          : Raw Reasoningを永続化するか
```

承認された初期値：

```text
Thinking Execution   : disabled
Thinking Visibility  : hidden
Display Label        : 高度推論
Raw Persistence      : disabled
```

## 2. 提案版からの変更

ユーザー承認により、Default Display Labelを次のように変更した。

```text
Old : 推論
New : 高度推論
```

理由：

- LLMの通常回答も広い意味では推論である
- Thinking Onで表示される専用Sectionと通常回答を区別したい
- Display Labelは後からApplication Config／Environment／CLIで変更できる

`高度推論`はUI上の識別Labelであり、Reasoningが必ず高品質、正しい、真の内部推論であると主張するものではない。

その他の提案Decisionは承認され、本書に取り込む。

## 3. 背景

Current Runtimeは`ThinkingMode`とCLIの`--thinking／--no-thinking`を持つが、Modelが生成した`<think>...</think>`をRaw Textのまま表示する。

次を分離する必要がある。

- Thinkingを実行するか
- Thinkingを見せるか
- Model Protocol TagとDisplay Tag
- Reasoning ContentとFinal Content
- Non-streamingとStreaming
- UI表示とAudit保存

## 4. Scope

- Application Config Schema `2`
- `[presentation.thinking]`
- Thinking Presentation用Immutable Contract
- Field別Precedence／Source Tracking
- Model Definition Schema `2`
- Output Protocol宣言
- Parser KeyによるParser選択
- Plain Text／Tagged Thinking Parser
- Non-streaming正規化／表示
- Stateful Streaming Parser
- Hidden No-flash
- Visible Custom Display Label
- Parse Status／Warning
- CLI Override
- `model-info`
- Current Mac／Metal Regression確認

## 5. Scope外

- Thinkingの正しさ保証
- Thinkingの品質評価
- High-level Explanation生成
- Raw Chain of ThoughtのAudit Log保存
- Thinkingの自動要約
- Thinking用Sampling Presetの自動適用
- ThinkingのToken Budget分離
- Strict Language Enforcement
- Web UI／API／Multi-turn
- Governance／Judge／Repair
- 新規外部Dependency

## 6. Configuration

`config/application.toml`をSchema `1`から`2`へMigrationする。

```toml
schema_version = "2"

[generation]
thinking_mode = "disabled"

[presentation.thinking]
visibility = "hidden"
display_label = "高度推論"
persistence = "disabled"
```

Deployment Profile Schema `3`は変更しない。PresentationはPlatform固有設定ではない。

## 7. Thinking Execution

Existing Contractを維持する。

```text
disabled      : Thinking実行を無効化
enabled       : Thinking実行を有効化
model_default : Model／Templateの既定動作に委ねる
```

VisibilityはExecutionを暗黙変更しない。

## 8. Presentation

### Visibility

```text
hidden  : CanonicalなReasoning SectionをDisplay Outputへ出さない
visible : Canonical TagをDisplay Labelへ変換して表示する
```

### Display Label

Default：

```text
高度推論
```

CLI Visible Output：

```text
<高度推論>
Reasoning Content
</高度推論>
Final Content
```

User Override例：

```text
display_label = "思考過程"
<思考過程>...</思考過程>
```

Label Validation：

- 1～64文字
- Blank禁止
- 先頭／末尾空白禁止
- `<`、`>`、`/`禁止
- CR／LF／制御文字禁止
- Unicode許可

Display LabelはModelへ送信しない。

## 9. Persistence

Phase 1-Eで許可する値：

```text
persistence = "disabled"
```

- Raw ReasoningをFile／JSON／JSONL／Databaseへ保存しない
- VisibleでもPersistedを意味しない
- ParserのMemory上の一時保持は永続化ではない
- 将来の保存機能は別Requirements／ADR／Audit Policyを必要とする

## 10. Precedence／Source

### Visibility

```text
CLI Explicit
  > MARGPA_THINKING_VISIBILITY
  > Application Config
  > Built-in hidden
```

### Display Label

```text
CLI Explicit
  > MARGPA_THINKING_LABEL
  > Application Config
  > Built-in 高度推論
```

### Persistence

```text
Application Config
  > Built-in disabled
```

Phase 1-EでPersistenceのEnvironment／CLI Overrideを許可しない。

Field別Source：

```text
visibility_source
display_label_source
persistence_source
```

## 11. CLI

Execution：

```text
--thinking
--no-thinking
```

Presentation：

```text
--show-thinking
--hide-thinking
--thinking-label "高度推論"
```

`--show-thinking`と`--hide-thinking`はMutually Exclusiveとする。

`--show-thinking`はExecutionをONにせず、`--thinking`はVisibilityをVisibleにしない。

## 12. Execution／Presentation Matrix

| Execution | Visibility | 期待動作 |
|---|---|---|
| `disabled` | `hidden` | Finalだけ表示 |
| `disabled` | `visible` | ReasoningがなければFinalだけ表示 |
| `enabled` | `hidden` | Thinkingを実行し得るがFinalだけ表示 |
| `enabled` | `visible` | ReasoningをDisplay Label付きで表示後、Finalを表示 |
| `model_default` | `hidden` | Model既定動作、Canonical Reasoningは非表示 |
| `model_default` | `visible` | Model既定動作、Reasoning検出時のみ表示 |

## 13. Model Output Protocol

Parser選択をModel Key／Architecture／Backend名のハードコードで行わない。

Model Definition Schema `2`：

```toml
schema_version = "2"

[output_protocol.thinking]
parser_key = "tagged_thinking_v1"
opening_delimiter = "<think>"
closing_delimiter = "</think>"
```

Canonical DelimiterはModel Definitionが所有し、Display LabelはApplicationが所有する。

Unknown Parser KeyはSilent Fallbackせず明示Errorとする。

## 14. Normalized Output

```text
reasoning_content
final_content
parse_status
parse_warnings
```

Parse Status：

```text
plain_text
complete
unclosed_reasoning
malformed_protocol
```

ParserはReasoningの真実性、正しさまたは真の内部推論との一致を主張しない。

## 15. Parser Semantics

Leading Canonical Thinking Sectionを1個だけProtocolとして解釈する。

```text
[optional leading whitespace]
<think>
reasoning
</think>
final
```

1. Openingなし: 全TextをFinal
2. Opening／Closingあり: Reasoning／Finalへ分離
3. Openingあり／Closingなし: `unclosed_reasoning`
4. Final内のTagらしきTextを無断削除しない
5. Parse Status／Warningを返す

## 16. Non-streaming

- Raw `GenerationResult`を改変しない
- Presentation ServiceでNormalize／Renderする
- HiddenはFinalだけ
- VisibleはCanonical TagをDisplay Tagへ変換
- Final ContentをTrim／要約／翻訳しない

## 17. Streaming

Stateful Parserを使用し、Chunk単位Regex置換にしない。

```text
detecting_prefix
inside_reasoning
after_reasoning
plain_text
terminal
```

必須：

- Opening／Closing DelimiterのChunk分割対応
- Minimum Suffix Buffer
- Hidden No-flash
- VisibleでCanonical Tagをそのまま表示しない
- Finish／Usage／Cancel／Close保持
- Non-streamingとのDisplay Parity

## 18. Malformed Policy

### Openingなし

全TextをFinal。原則Warningなし。

### Openingあり／Closingなし

- Status: `unclosed_reasoning`
- Warning付与
- Hidden: 検出済みReasoningを表示しない
- Visible: Display Closing TagをTerminalで補完
- Final Contentは空

### Extra Delimiter

- User Contentの可能性があるため無断削除しない
- `malformed_protocol`またはWarningとして観測
- HiddenはSecurity Guardrailではない

## 19. Privacy／Audit

- Raw Reasoningを真のChain of Thoughtと主張しない
- VisibilityとPersistenceを同一視しない
- HiddenをSecret Redactionの代替にしない
- Raw Reasoning保存を追加しない
- Parse Status／WarningはRaw本文なしで観測できる

## 20. Sampling

Thinking ModeによるTemperature／Top-p／Presence Penalty等の自動変更を行わない。

Thinking用PresetはPhase 2以降のExplicit Experiment Profile候補とする。

## 21. Observability

`model-info`に次を含める。

```text
effective_config.generation.thinking_mode
effective_config.presentation.thinking.visibility
effective_config.presentation.thinking.display_label
effective_config.presentation.thinking.persistence
effective_config.presentation.thinking.visibility_source
effective_config.presentation.thinking.display_label_source
effective_config.presentation.thinking.persistence_source
model.output_protocol.thinking.parser_key
```

## 22. Existing Behavior Preservation

- Model Load／Unload
- Non-streaming／Streaming／Cancel／Close
- Token Usage／Timing／Finish Reason
- Artifact SHA-512
- `ja／en／auto`
- User System Message合成
- Generation Override
- Deployment／Platform Validation
- Current Mac／Metal
- Raw `GenerationResult`／`GenerationChunk`／Model Port

## 23. Required Tests

### Config

- Application Schema `2`
- Old SchemaのSilent Acceptance禁止
- Default `hidden／高度推論／disabled`
- Environment／CLI Precedence
- Field別Source
- Invalid Value／Label拒否
- DeploymentがPresentationを所有できない

### Model Protocol

- Model Definition Schema `2`
- Parser Key／Delimiter Validation
- Unknown Parser Key拒否
- Model Key／Architecture非依存

### Parser／Renderer

- Plain Text
- Complete Thinking
- Hidden／Visible
- Default／Custom Label
- Unclosed／Extra Delimiter
- Final Content保持
- Raw Result不変

### Streaming

- Opening／Closingの全Chunk Split
- 1文字Chunk
- Empty Delta
- Hidden No-flash
- Visible Label
- Malformed Terminal
- Non-streaming Parity
- Finish／Usage／Cancel／Close保持

### CLI／Regression

- Execution／Visibility独立
- Flag Exclusivity
- `--thinking-label`
- `model-info`
- Ruff／Mypy／Pytest／Compileall
- Environment／Lock／Offline
- Native Metal Hidden／Visible
- Phase 1-D Language Smoke

## 24. Acceptance Criteria

1. Thinking ExecutionとVisibilityが独立している
2. PersistenceがVisibilityから独立し、`disabled`に固定される
3. Application Config Schema `2`がStrict Validationされる
4. Deployment Profile Schema `3`が変更されない
5. Defaultが`disabled／hidden／高度推論／disabled`である
6. Visibility／LabelのEnvironment／CLI Overrideが機能する
7. Field別Sourceを確認できる
8. Canonical DelimiterとDisplay Labelが分離される
9. ParserがModel DefinitionのParser Keyから選択される
10. Model Key／Architecture／Backend名のParserハードコードがない
11. Non-streamingでReasoning／Finalが正規化される
12. StreamingでDelimiterがChunk分割されても正しく動作する
13. Hidden StreamingでReasoningが一瞬表示されない
14. VisibleでDefault／Custom Display Labelが使用される
15. Malformed Protocolが決定論的に処理され、Warningが得られる
16. Raw `GenerationResult`／`GenerationChunk`が改変されない
17. StreamingのFinish／Usage／Cancel／Closeが保持される
18. Raw Reasoningが新しく永続保存されない
19. Sampling ParameterがThinking Flagで暗黙変更されない
20. 新規外部Dependencyがない
21. Static／Default TestがPassする
22. Current Mac／Metal RuntimeがRegressionしない

## 25. Authorization Boundary

本RequirementsとDecisionはAcceptedである。

ただし、本Accepted化はSource／Config／Test実装を自動解禁しない。Phase 1-E実装開始には、ユーザーの明示的な実装許可を必要とする。


<!-- SOURCE_END 24: docs/requirements/phase_1e_thinking_presentation_requirements_20260719130303.md -->

---

<!-- SOURCE_BEGIN 25: docs/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md -->

### Source 25: `docs/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md`
- Source SHA-512: `6459e2395f30c84706af5f5760ae279ad501dd5583af7727383ba647b8068d5b03c12752da056bd6565cb2ee3271bb6032afe0eb9ff1733ceb65e717e4d7b9eb`
- Source Size: `6033` bytes

# Phase 1-F Lightning Cross-environment Runtime要件

- 文書ID: `phase_1f_lightning_cross_environment_runtime_requirements`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-19 20:23:33 JST`
- 更新日時: `2026-07-19 20:23:33 JST`
- Snapshot: `20260719202333`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Python 3.12／3.13、Lightning Linux Container、CUDA必須、CPU候補
- 正本言語: 日本語
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../history/adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- Architecture: [lightning_ai_studio_cross_environment_architecture_20260719202333.md](../history/architecture/lightning_ai_studio_cross_environment_architecture_20260719202333.md)
- Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](../history/handoffs/implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- supersedes: `lightning_ai_studio_dual_runtime_profile_requirements_20260719200711.md`

## 1. Objective

Phase 1公開前に、同一Repository、Application Core、Model Definition、Qwen3-4B GGUFを用いて次を成立させる。

```text
Mac       : CPython 3.13.14／macOS arm64／Metal
Lightning : CPython 3.12.11／Ubuntu 24.04 Container／Linux x86_64／CUDA
Lightning : CPython 3.12.11／Ubuntu 24.04 Container／Linux x86_64／CPU候補
```

## 2. Python Support

Project Metadata候補：

```toml
requires-python = ">=3.12,<3.14"
```

要件：

- Macの`.python-version = 3.13.14`をPrimary Defaultとして維持してよい。
- Lightning SetupはPython 3.12.11を明示選択する。
- `uv.lock`はPython 3.12／3.13の両方を解決可能とする。
- Pinned Direct Dependency Versionは、両Versionで解決できる限り維持する。
- Ruff TargetとMypy Python Versionは、最小Supportである3.12のSyntax／Typingを検査する。
- Mac 3.13とLightning 3.12でDefault Testを実行する。
- Platform固有Environment Verificationが他PlatformのPython Patchを誤拒否しない構造にする。
- Python 3.11以下はSupport対象外とする。

## 3. Lightning Profiles

必須：

```text
config/profiles/lightning_linux_x86_64_cuda.toml
```

Best Effort／期限管理対象：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

Profile意味は、前身Dual Profile要件を継承する。

- CUDA: `gpu／nvidia／cuda／gpu_layers=-1／fallback=deny`
- CPU: `cpu／cpu_native／gpu_layers=0／fallback=deny`
- Host: `linux／x86_64／container／ubuntu`
- Hardware SKUはProfile名へ固定しない。
- 初期版はExplicit `--profile`で選択する。

## 4. Required Code／Configuration Changes

1. Python Support RangeとLockを3.12／3.13へ拡張する。
2. Ruff／Mypy／Setup／Verificationを最小Python 3.12とPlatform差へ整合させる。
3. Container Execution Environmentを検出する。
4. Mac Native Detectionを維持する。
5. llama.cpp CUDA Build／Executionを検出する。
6. CPU実行をCUDA実行と分離して申告する。
7. CUDA ProfileとCPU Profileを追加する。
8. Linux CUDA Build Recipeを追加する。
9. 可能ならLinux CPU Recipeまたは同一CUDA BuildのCPU Modeを成立させる。
10. Model RootをLightningのPersistent StorageからEnvironmentで指定できるよう維持する。
11. Metal固有Test Marker／Help／VerifierをCross-environment構造へ整理する。

## 5. Phase 1-F Mandatory Gate

必須合格条件：

- Mac Python 3.13.14の既存Default／Metal TestがPassする。
- Lightning Python 3.12.11でProject Install／Syncが成立する。
- Lightning Default TestがPassする。
- Lightning CUDA Buildが成立する。
- CUDA ProfileでQwen3-4BをLoadできる。
- `device_kind=gpu`、`acceleration_api=cuda`、`gpu_offload=true`を観測する。
- SHA-512がMacの同一Model Artifactと一致する。
- Generate、Streaming、Non-streaming、Cancel、Unloadが成立する。
- Response Language／Thinking Presentationの主要Contractが成立する。
- GPU未割当時にCUDA ProfileがCPUへ黙ってFallbackしない。
- Environment、Profile、Backend、Model、Test EvidenceをStatusへ記録する。

## 6. CPU Gate

CPU Profileは実装対象とするが、次の2段階で扱う。

### Preferred

- CUDA-enabled Buildのまま`gpu_layers=0`でCPU実行できる。
- GPU未割当状態でもImport／Load／Generateできる。
- CPU Observationが正しい。

### Deadline-safe Alternative

同一Environmentで成立せず、別Native Build／Environmentが公開期限を大きく圧迫する場合：

- CPU Profile候補、失敗Evidence、必要なFollow-upを記録する。
- CUDA RuntimeをPhase 1-F必須Gateとして先に完了できる。
- CPU対応を未実装のまま「対応済み」と主張しない。
- 延期判断は実装担当が独断で行わず、設計者Reviewとユーザー承認で確定する。

## 7. Publication Gate

Phase 1-F完了後に次を行う。

1. Mac／Lightning User Manual更新
2. Phase 1 Cross-environment Final Review
3. ユーザー受入テスト
4. 設計者のPhase 1完了・次Phase移行可能宣言
5. Phase 1 Backup
6. Public README、Setup、License、Model取得手順、Known Limitations
7. Secret、実Log、Model Binary、Local Path、Credentialの除外確認
8. ユーザーの明示許可後にGit／GitHub公開操作

## 8. Out of Scope

- Web UI／Live Demo URL
- Multi-turn Conversation
- Runtime Governance本実装
- Guard／Judge／Agent
- Arbitrary Linux Hardware Auto-router
- Windows Native Runtime
- ROCm／Vulkan
- GPU Quotaを検知したRuntime自動Fallback

## 9. Authorization Boundary

本要件は実装開始可能な設計正本である。実装担当TaskがSource／Config／Lock／Tests／Scriptsを変更するには、ユーザーから当該Handoffへの開始指示を受ける。Lightning上のInstall、Build、Model配置、GPU利用はLightning側で別途実行する。

<!-- SOURCE_END 25: docs/requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md -->

---

<!-- SOURCE_BEGIN 26: docs/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md -->

### Source 26: `docs/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md`
- Source SHA-512: `32b989eae570febd034cb20ca40b07529092499060685e6f27b30f5fcd4bef4eb04857f0cf4b5af4356a0ff1308ee53ac2a688d360ebd4beed7a79c7e16657ca`
- Source Size: `5811` bytes

# Phase 1-F Lightning Pure CPU Runtime Follow-up 要件定義

- 文書ID: `phase_1f_lightning_pure_cpu_runtime_follow_up_requirements`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Purpose

GPU、NVIDIA Driver、CUDA Toolkitまたは`nvcc`を利用できないFreshなLinux x86_64 CPU環境で、MARGPA Runtime LLMをPure CPU Buildとして再構築できるRepository Hookを用意する。

## 2. Current Gap

Current Profile：

```text
config/profiles/lightning_linux_x86_64_cpu.toml
```

Current Effective Intent：

```text
compute_kind_key  : cpu
gpu_layers        : 0
build_variant_key : cuda
```

これはCUDA BuildをCPU実行するProfileであり、Pure CPU Buildではない。Fresh CPU環境でCUDA Buildが存在しない場合、SetupがCUDA Toolkit／`nvcc`を要求する可能性がある。

## 3. Scope

- Pure CPU Deployment Profile
- Pure CPU Backend Build Variant
- CPU専用Setup Script
- CPU専用Preflight
- CPU専用Environment Verification
- Static／Unit／Integration Test
- Bounded Native Acceptance Hook
- User Manual／Status用情報

## 4. Non-goals

- Lightning外部環境での実行
- GPU／CUDA Profile変更
- Model Download
- Model File Upload
- Public URL
- RAG実装
- Project Documentation Corpus Upload
- Performance Guarantee
- Cloud Provider固有SDK

## 5. Required Profile

候補：

```text
config/profiles/lightning_linux_x86_64_cpu_native.toml
```

最低条件：

```text
host.operating_system_key       : linux
host.architecture_key           : x86_64
host.execution_environment_key  : container
compute.compute_kind_key        : cpu
compute.vendor_key              : generic
compute.acceleration_api_key    : none
backend_runtime.backend_key     : llama_cpp
backend_runtime.build_variant   : cpu
load.gpu_layers                 : 0
runtime.required_device_kind    : cpu
runtime.required_acceleration   : none
```

実際のSchema Field名はCurrent Contractに合わせる。意味をCUDAへ偽装しない。

## 6. Setup Requirements

候補：

```text
scripts/setup/setup_lightning_linux_x86_64_cpu.sh
```

- Python `>=3.12,<3.14`
- Target候補はPython 3.12.11
- Project-local Environmentまたは明示されたStudio Environment
- `llama-cpp-python==0.3.34`
- CPU Build
- CUDA／Metal／ROCmを要求しない。
- NVIDIA Driver／`nvidia-smi`／`nvcc`を要求しない。
- Existing CUDA BuildをPure CPU合格Evidenceにしない。
- Normal SyncとNative Rebuildを分離する。
- Repeated Runを可能にする。
- Failure時に不足条件を明示する。

## 7. Preflight

Preflightで確認する。

- Linux
- x86_64
- Container／Studio Environment
- Python Version
- `uv` Version／Path
- CPU Count
- Memory
- Writable Project／Environment Path
- Model PathはOptional Check

Preflightで要求しない。

- GPU
- NVIDIA Driver
- CUDA
- `nvcc`

## 8. Runtime Observation

Runtimeは次を区別する。

```text
backend build variant : cpu
device kind           : cpu
acceleration api      : none
gpu offload           : false
gpu layers            : 0
```

CPU Buildを`cuda`または`gpu`として表示しない。

## 9. Model／Resource Boundary

Model RootはRepository外を正本とし、`MARGPA_MODEL_ROOT`またはEnvironment-local Symlinkで解決できる。

Model Artifactと`.venv`をRepository／Upload Bundleへ含めない。

CPU SmokeはResourceを抑える。

- Main Model 1個だけをLoad
- Guard／Judge／RAG／SummaryはDefault OFF
- Thinking Default OFF
- 短いPrompt
- Bounded Max New Tokens
- 1 Concurrent Generation

## 10. Project Documentation Explainer Boundary

Phase 1-ex後にMac実機でProject Documentation Explainerを実装する場合も、Lightning CPU DeploymentではHook-onlyをDefaultとする。

```text
Component Contract : present
Provider／Index     : absent allowed
enabled             : false
Index Load          : none
Retrieval           : none
Additional Model Call: none
```

OFF時にProvider不存在をStartup Failureとしない。利用不能機能を実行済みと表示しない。

この要件はRAG実装開始を許可しない。

## 11. Automated Test

- Pure CPU Profile Schema
- Host／Architecture／Container Match
- `build_variant=cpu`
- `device=cpu`
- `acceleration=none`
- `gpu_layers=0`
- `gpu_offload=false`
- CUDA Capabilityを要求しない。
- Explicit Profile Resolution
- Mac／CUDA Profile非Regression
- Setup Script Syntax
- Preflight without GPU Commands
- Verification Fail Closed

## 12. Deferred Native Test

外部CPU環境利用可能時に実施する。

- Fresh Setup
- Backend Import
- CPU System Info
- Model Load
- SHA-512
- Short Generation
- Streaming
- Cancel
- Token Limit
- Japanese Response
- Memory／Latency
- Shutdown

Native未実行をPassとして記録しない。

## 13. Acceptance

Repository Acceptance：

1. Pure CPU ProfileとCUDA CPU Execution Profileが区別される。
2. Setup／PreflightがGPU／CUDA／`nvcc`を必須にしない。
3. Static／Unit／IntegrationがPassする。
4. Mac／CUDA Regressionがない。
5. Native TestがPendingとして明示される。

Final Native Acceptance：

1. Fresh CPU EnvironmentでSetupできる。
2. Pure CPU Buildとして観測される。
3. Qwen3-4B Q4_K_MのBounded Smokeが完了する。

## 14. Authorization

Repository側Profile／Script／Testの実装へ着手可能である。外部環境操作は別Gateとする。


<!-- SOURCE_END 26: docs/requirements/phase_1f_lightning_pure_cpu_runtime_follow_up_requirements_20260725200001.md -->

---

<!-- SOURCE_BEGIN 27: docs/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md -->

### Source 27: `docs/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md`
- Source SHA-512: `5350dcd2a32da485d8e60b80199fa32301ba9c423ab6dd47fc5db44f07e08d737a8b19d47bf5f94810e7b49609293ea57fe3421e2f445bef0983d35fdd588431`
- Source Size: `13199` bytes

# Phase 1-G Minimal Web Surface 要件定義

- 文書ID: `phase_1g_minimal_web_surface_requirements`
- 状態: `accepted_ready_for_implementation`
- 作成日時: `2026-07-21 09:39:52 JST`
- 更新日時: `2026-07-21 09:39:52 JST`
- Snapshot: `20260721093952`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: FastAPI、最小Web UI、Ephemeral Multi-turn、Preview Access Control
- 正本言語: 日本語
- Architecture: [phase_1g_minimal_web_surface_architecture_20260721093952.md](../history/architecture/phase_1g_minimal_web_surface_architecture_20260721093952.md)
- ADR: [adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md](../history/adr/adr_0016_batch_lightning_upload_after_phase_1h_20260721093952.md)
- Handoff: [implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md](../history/handoffs/implementer_handoff_phase_1g_minimal_web_surface_20260721093952.md)
- supersedes: なし（Phase 1-G正本要件の初回）

## 1. Objective

Current Model-independent Runtimeへ、Macと将来Lightningで利用可能な最小Web Surfaceを追加する。

```text
Browser
  → Server-side Preview Access Control
  → FastAPI Application Boundary
  → Conversation／Generation Application Service
  → Existing Inference／Presentation Contracts
  → Model Port
```

Phase 1-Gは本格的なGPT風製品UIではなく、Phase 1公開候補を少人数で操作・検証できる最小構成である。

## 2. Technology Decision

```text
API Framework : FastAPI 0.139.2
ASGI Server   : Uvicorn 0.51.0／base package
API Test      : HTTPX 0.28.1
Frontend      : Vanilla HTML／CSS／JavaScript
Transport     : HTTP + Server-Sent Events
Python        : >=3.12,<3.14
```

Dependency方針：

- `fastapi[standard]`は採用しない。
- FastAPI本体とUvicorn baseを明示Pinする。
- `uvicorn[standard]`のPlatform固有Optional Dependencyを初期必須にしない。
- Jinja2、React、Node、npm、WebSocket専用Library、SSE追加Libraryを初期導入しない。
- HTTPXはASGI Test用Dev Dependencyとする。

正本確認先：

- [FastAPI PyPI](https://pypi.org/project/fastapi/)
- [Uvicorn PyPI](https://pypi.org/project/uvicorn/)
- [HTTPX PyPI](https://pypi.org/project/httpx/)

## 3. User-visible Scope

### 3.1 Chat

- 1 Browser Tabにつき1つのCurrent Chatを持つ。
- 複数Turnの`user／assistant`会話を行える。
- Streaming表示する。
- 生成をStopできる。
- New ChatでCurrent Chatを初期化できる。
- Input送信中の二重送信を防止する。
- Model／Profile／Device等の最小Runtime Statusを表示する。
- Safe Error／Warningを画面上へ表示する。

### 3.2 Settings

一般UIへ次の3項目だけを表示する。

```text
Response Language
  └─ ja／en／autoのPull-down

Max New Tokens
  └─ Integer
  └─ Initial／Default 2048

推論過程を表示
  └─ OFF／ON Switch
  └─ presentation.thinking.visibilityだけを変更
```

Settings変更はBrowser Current Chat／Request単位であり、`config/application.toml`を書き換えない。

要約モードOFF／ONはPhase 1-Hで追加する。Phase 1-Gで動かないSwitchを先に表示しない。

### 3.3 Thinking注記

UI上の表示名を次へ変更する。

```text
Config Display Label : 推論過程
UI説明名             : 推論過程（モデル生成）
```

`高度推論`は、品質が高度であると誤認させる可能性があるためDefaultから変更する。

UIに次の趣旨を明示する。

- これはModelが生成した推論形式のTextであり、真の内部思考や正しさを保証しない。
- VisibilityはThinking実行のON／OFFとは別である。
- Thinkingが無効な場合、VisibilityをONにしても推論過程は表示されない。
- Token上限によって最終回答前に生成が終了する場合がある。
- Raw Thinkingは永続保存しない。

内部Model Protocolの`<think>...</think>`は変更しない。

## 4. Conversation State

Phase 1-GではConversation HistoryをServerへ永続保存しない。

```text
Browser Memory
  └─ user／assistant Canonical Final Messages
       ↓ every request
FastAPI
  └─ validate／compose／generate
```

- BrowserはCurrent ChatのMessage列をMemory上で保持する。
- RequestごとにCurrent Message列全体をServerへ送る。
- ServerはBrowser間でConversation Stateを共有しない。
- Page ReloadでHistoryが失われてもよい。
- New ChatはBrowser MemoryをClearする。
- Server Restartで復元しない。
- 複数Saved Chatを作らないためDelete Buttonは不要である。
- History／Resume／Delete／Title／Searchは後続Phaseで扱う。

複数利用者が同じPreview Credentialを使っても、BrowserごとのMessage列が混ざらないことを必須とする。

## 5. Message Contract

Browserから受理するRoleは次だけとする。

```text
user
assistant
```

- Client指定の`system`／`tool` Roleを受理しない。
- 空Messageを拒否する。
- 最終Messageは`user`でなければならない。
- Role順序を検証し、不正列はSafe Errorとする。
- ServerがResponse Language用System Instructionを先頭へ構成する。
- Client Historyへ戻すAssistant MessageはCanonical Final Answerだけとする。
- Visible Thinkingを次TurnのAssistant Historyへ混入させない。
- Context超過時にHistoryを黙って削除・要約・切り詰めない。
- Context不足は明示Error／Warningとして返す。

## 6. API Scope

最低限の候補Endpoint：

```text
GET  /healthz
GET  /api/v1/runtime
POST /api/v1/chat/stream
GET  /
GET  /assets/*
```

### `/healthz`

- 認証不要としてよい。
- `status`以外のModel、Path、Version、Credentialを返さない。
- Readinessの詳細主張はしない。

### `/api/v1/runtime`

- 認証必須。
- Model Key、Profile Key、Device Kind、Acceleration API、Default UI Settingを返してよい。
- Absolute Path、Secret、Raw System Promptを返さない。

### `/api/v1/chat/stream`

- 認証必須。
- Validated Message列と3 Settingを受け取る。
- Server-Sent EventsでStatus、Display Delta、Warning、Completion、Safe Errorを識別可能に返す。
- CompletionにはFinish ReasonとCanonical Final Assistant Messageを含める。
- Hidden ThinkingをClientへ送信しない。

## 7. Streaming／Cancellation

- Browserは`AbortController`等でStreaming RequestをCancelする。
- ServerはDisconnectを検出し、Native Generation StreamへCooperative Cancelを伝播する。
- Cancel後もModel Runtimeを再利用可能である。
- Cancelled ResponseをAssistant HistoryへCompleted Messageとして追加しない。
- Terminal Eventは1回だけ発生する。
- StreamingとNon-streaming内部Contractを重複実装しない。
- UI Status表示の遅延でModel GenerationをBlockしない。

Phase 1-Gは1 Process／1 Worker／1 Model Instanceとする。

- 同時Generationは1件だけ許可する。
- Busy時は無制限Queueに積まず、SafeなBusy Responseを返す。
- ModelをRequestごとにLoadしない。
- Startup／Lifespanで1回Loadし、Shutdownで1回Unloadする。

## 8. Preview Access Control

Phase 1-GのAccess Controlは、公開製品認証ではなく少人数Preview用Server-side Basic Authenticationとする。

Environment候補：

```text
MARGPA_WEB_AUTH_MODE=disabled|basic
MARGPA_WEB_AUTH_USERNAME=...
MARGPA_WEB_AUTH_PASSWORD=...
```

要件：

- Default Bindは`127.0.0.1`とする。
- Loopback BindではAuth Disabledを許可する。
- `0.0.0.0`等Non-loopback BindではBasic Authを必須とし、Credential不足ならStartupをFail Closedする。
- CredentialはEnvironmentからだけ受け取る。
- CredentialをTOML、Source、Log、Error、HTML、API Responseへ出さない。
- 比較はTiming Attackを避ける標準のConstant-time Compareを使用する。
- `/healthz`以外のUI、Assets、APIを同じAccess Controlで保護する。
- Interactive API Docs／ReDocは初期版で公開しない。
- Query Parameter／URLへTokenを入れない。
- Client-side JavaScriptだけのPassword判定を行わない。
- TLS終端はLightning等の信頼できるReverse Proxyへ委ねる。直接InternetへPlain HTTP公開しない。

## 9. Web Security／Privacy

- Model Outputを`innerHTML`で描画しない。
- Plain Textとして安全に表示する。
- 初期版でMarkdown HTML Renderingを行わない。
- External CDN／External JavaScript／External Fontを使わない。
- Static AssetはRepository内へ保持する。
- Broad CORSを有効にしない。
- Same-origin前提とする。
- `Cache-Control: no-store`等の適切なResponse Headerを検討する。
- Credential、Message、Model OutputをAccess Logへ本文として残さない。
- Traceback、Absolute Path、Environment VariableをClientへ返さない。
- Error Responseは既存`InferenceError.safe_message`思想を継承する。

Phase 1-GはGuardrail、Prompt Injection Defense、Content Safetyを実装したとは主張しない。

## 10. Config／Runtime Behavior

- UIはTracked TOMLを直接編集しない。
- UI DefaultはEffective Configから取得する。
- Response Languageは`ja／en／auto`だけを許可する。
- Max New Tokensは正のInteger、Phase 1-G上限2048とする。
- Thinking Visibilityは`hidden／visible`へMappingする。
- Thinking ExecutionはUI Visibilityから暗黙変更しない。
- Model Root、Profile、Model Key、Context Size等はServer Startup Configとし、一般UIから変更しない。
- Config SourceとRequest OverrideをAudit可能な境界として分離する。

## 11. CLI／Entrypoint

候補Command：

```text
margpa-web
```

要件：

- Current CLI `margpa-llm`を壊さない。
- Web EntrypointはCLIのPrivate FunctionをImportしない。
- Host、Port、Profile、Registry、Model Root等のStartup Optionを提供できる。
- Worker数は1に固定する。
- Development Auto Reloadを公開候補で使用しない。
- Non-loopback BindとAuthの整合をStartup前に検証する。

## 12. Dependency／Setup

候補`pyproject.toml`構造：

```toml
[project.optional-dependencies]
web = [
  "fastapi==0.139.2",
  "uvicorn==0.51.0",
]

[dependency-groups]
dev = [
  "httpx==0.28.1",
]
```

実際のTOML構造は既存GroupとMergeし、重複Tableを作らない。

- `uv.lock`を更新する。
- Mac Setup Recipeへ`--extra web`を追加する。
- Lightning Setup Recipeも最終搬入前に`--extra web`対応へ更新する。
- Native `llama-cpp-python` Build手順とWeb Dependency Syncを混同しない。
- Requirements.txtはPhase 1-G必須正本にせず、Public Packaging時に必要性を再評価する。

## 13. Test Requirements

### Unit／Contract

- API Request Schema
- Role／Order Validation
- Language／Token／Visibility Validation
- Context Errorの非破壊動作
- Safe Error Mapping
- Basic Auth Success／Failure／Missing Credential
- Non-loopback Fail Closed
- Secret Redaction
- Busy Response
- Thinking Hidden／Visible
- Canonical FinalとDisplay Contentの分離

### ASGI

- HTTPXによるIn-process ASGI Test
- Fake Model Port／Fake StreamをDependency Injectionする。
- `/healthz`
- Runtime Metadata Redaction
- SSE Event Order
- Completion 1回
- Client Disconnect／Cancel
- Static Asset配信
- AuthでUI／Assets／APIが同じく保護される。

### Native／Manual

- Mac 3.13.14／MetalでServer Startup
- Browserから日本語／英語／auto
- Multi-turn
- Streaming
- Stop後の再生成
- New Chat
- Max New Tokens 2048
- Thinking Visibility注記
- ModelをRequestごとに再Loadしない。
- Existing CLI／Model Smoke Regression

## 14. Acceptance Criteria

- FastAPI／UvicornをEntrypointへ局所化できている。
- Browser間でConversationが混ざらない。
- New ChatがCurrent BrowserだけをResetする。
- Settings 3項目がRequest Overrideとして動く。
- Tracked TOMLを書き換えない。
- Streaming／Stop／Post-cancel Generationが成立する。
- Hidden ThinkingがClientへ漏れない。
- Public BindがCredentialなしで起動しない。
- Model OutputをHTMLとして実行しない。
- Modelを1回Load／1回Unloadする。
- Full Static／Default／Mac Native TestがPassする。
- Phase 1-HとLightning Full Uploadを実行していない。

## 15. Out of Scope

- Conversation永続化
- Chat History／Resume／Delete／Title／Search
- Regenerate
- Multiple Model選択
- TOML Editor／Save／Diff
- Developer／Research Setting UI本体
- Post-generation Summary Mode実装
- Runtime Governance／ARGD／DAGD
- Guardrail／Judge／Repair／Agent／RAG
- Rate Limiting本格実装
- OAuth／OIDC／User Account
- Markdown／Code Highlighting
- React／Next.js／Node Build
- Lightning Full Upload／Live URL公開

## 16. Authorization Boundary

本要件とHandoffにより、実装担当はPhase 1-GのRepository変更とMac検証を開始できる。

Phase 1-H、Lightning Full Upload、Model Transfer、Lightning Dependency Sync／Native Build、Backup、Git、GitHub公開は許可しない。

<!-- SOURCE_END 27: docs/requirements/phase_1g_minimal_web_surface_requirements_20260721093952.md -->

---

<!-- SOURCE_BEGIN 28: docs/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md -->

### Source 28: `docs/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md`
- Source SHA-512: `b40a902b6455717389bd5d63d285f88a163c070986eafe8aa6859b80ac297941468d1dd4e9420dd3beea7f4b42087a6e103196f232660d2c41f67da76dd330eb`
- Source Size: `13956` bytes

# Phase 1-H Summary Mode／UI Language 要件定義

- 文書ID: `phase_1h_summary_mode_and_ui_language_requirements`
- 状態: `accepted_design_complete_waiting_implementation_authorization`
- 作成日時: `2026-07-21 17:43:46 JST`
- 更新日時: `2026-07-21 17:43:46 JST`
- Snapshot: `20260721174346`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Post-generation Summary Mode、画面表示言語切替
- 正本言語: 日本語
- Architecture: [phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md](../history/architecture/phase_1h_summary_mode_and_ui_language_architecture_20260721174346.md)
- ADR: [adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md](../history/adr/adr_0020_phase_1h_summary_pipeline_and_ui_language_separation_20260721174346.md)
- Handoff: [implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md](../history/handoffs/implementer_handoff_phase_1h_summary_mode_and_ui_language_20260721174346.md)
- supersedes: `post_generation_summary_mode_requirements_reservation_20260721090725.md`

## 1. Objective

Phase 1-Gで成立したMinimal Web Surfaceへ、次の2機能を追加する。

```text
1. 要約モード OFF／ON
   └─ 通常回答を同じMain Modelでもう一度要約してから表示

2. 画面表示言語 日本語／English
   └─ UI Textだけを切替
   └─ Modelの出力言語とは独立
```

Phase 1-Hは、Phase 4の本格UI、会話永続化、専用要約Model、LLM-as-a-Judgeを先取りしない。現在の疎結合性、Model交換性、Single-worker、Cooperative Cancelを維持したまま、小規模なResponse TransformationとUI Localization Boundaryを成立させる。

## 2. User-visible Scope

### 2.1 要約モード

一般設定へ次を追加する。

```text
要約モード  [ OFF | ON ]
Default      : OFF
```

- OFF時はCurrent Phase 1-Gと同じ1回生成とする。
- ON時は通常回答を生成した後、同じMain Modelへ要約を1回だけ依頼する。
- 通常回答をStreaming表示してから置換しない。
- 通常回答生成中はStatusだけを表示し、要約生成の出力だけを回答欄へStreaming表示できる。
- 要約失敗時は、警告とともに通常回答へFallbackする。
- Switchは内部の`off／post_generation` ModeへMappingする。

### 2.2 画面表示言語

画面右上へ次の切替を追加する。

```text
日本語 | English
Default: 日本語
```

画面表示言語は、設定内の`Response Language`と完全に分離する。

有効な組合せ：

| UI Language | Response Language | 結果 |
|---|---|---|
| ja | ja | 日本語UI／日本語回答 |
| ja | en | 日本語UI／英語回答 |
| en | ja | 英語UI／日本語回答 |
| en | en | 英語UI／英語回答 |
| ja／en | auto | 選択UI言語／Model側自動回答 |

UI Language変更は、Model Message、System Instruction、Response Language Policy、Thinking Outputを変更しない。

## 3. Summary Runtime Values

```text
通常生成 max_new_tokens : Request値／Default 2048
要約生成 max_new_tokens : 1024固定
要約時Thinking          : disabled固定
要約Backend              : main_model
実行方式                 : Sequential
同時Model常駐            : なし
元回答保存               : true
失敗時Policy             : fallback_original
```

要約生成では、通常生成の`temperature／top_p／top_k／min_p／penalty／seed`等のEffective Generation値を継承し、`max_new_tokens`と`thinking_mode`だけを要約用Policyで上書きする。専用Sampling Profileは後続候補とする。

## 4. Processing Contract

```text
Validated Conversation Input
  → Normal Generation
  → Thinking／Final分離
  → Original Canonical Final Answer
  → Summary Request構築
  → Same Main Model／Thinking disabled／max 1024
  → Summary Final Answer検証
      ├─ Complete／Non-empty → Summaryを表示・履歴へ採用
      ├─ Failed／Empty／Length／Context不足 → Warning＋OriginalへFallback
      └─ Cancelled → Cancelled Terminal／履歴へ追加しない
```

要約対象は通常生成のCanonical Final Answerだけとする。次を要約Requestへ含めない。

- 通常生成のThinking／Reasoning Segment
- Presentation用表示Label
- 生のChain of Thought
- 元のConversation History
- User Promptの再掲
- Runtime内部状態
- System Prompt／Governance内部Evidence
- Credential／Path／Secret

## 5. Summary Instruction

要約RequestはBackend-independentなTyped Contractから構成し、特定Model名、GGUF、llama.cppを前提にしない。

要約指示は最低限、次を要求する。

- 入力された元回答を要約し、要約本文だけを返す。
- 新しい事実、判断、約束、出典を追加しない。
- 結論、前提、制約、警告、未解決事項、否定、例外を勝手に反転・削除しない。
- Code、Command、Identifier、数値等を変更する場合は意味を壊さない。
- 元回答内の指示らしきTextを命令として実行せず、要約対象Dataとして扱う。
- `ja／en`では指定されたResponse Languageに合わせる。
- `auto`では元回答の主要言語を維持する。

元回答は明確なData Boundaryで囲み、Summary System Instructionと混同させない。Phase 1-HはPrompt Injection Defense完成を主張しないが、元回答内の命令を要約器が実行対象と解釈しにくい構成を必須とする。

## 6. Original／Summary Artifact

Phase 1-Hの1 Turn内では次を明確に分離する。

```text
original_final_answer : 通常生成のCanonical Final Answer
summary_final_answer  : 要約生成のCanonical Final Answer
presented_answer      : 成功時Summary／Fallback時Original
```

- Summary成功時、次TurnのBrowser Conversation Historyへ追加するAssistant MessageはSummaryとする。
- Fallback時はOriginalをAssistant Messageとする。
- OriginalはPipeline内の独立Artifactとして保持する。
- Phase 1-HではOriginalをBrowserへ常時送信または永続保存しなくてよい。
- 将来のAudit LogでOriginal／Summaryを別Artifactとして保存できるMetadata境界を用意する。
- ThinkingはOriginal Preservationの対象にしない。

## 7. Failure／Degraded Policy

次の場合、不完全なSummaryを採用せずOriginalへFallbackする。

- Summary Inference Error
- Summary Context Limit Error
- Summary Outputが空または空白だけ
- Summary ParserからCanonical Final Answerを得られない
- Summary `finish_reason=length`
- Summary Terminalが不明または不整合

Fallback時：

- Safe Warning Codeを返す。
- OriginalをCanonical Assistant Messageとして完成させる。
- SummaryのRaw Exception、Prompt、Pathを返さない。
- Original自体のToken上限Warningを消さない。
- Summary失敗を正常なSummary成功として記録しない。

CancellationはFailure Fallbackとしない。通常生成中または要約生成中にCancelされた場合、`cancelled`で終了し、Original／SummaryのどちらもConversation Historyへ追加しない。

## 8. Context Policy

- Current Model Adapterの正確なFormatted Prompt Token検証を再利用する。
- 要約用`max_new_tokens=1024`を黙って超えない。
- Phase 1-Hでは元回答を無断切捨てしない。
- Phase 1-HではSummary Token Budgetを黙って動的縮小しない。
- Summary RequestがLoaded Contextへ収まらない場合、Warning付きOriginal Fallbackとする。
- Context Sizeの自動拡大、History圧縮、Pre-generation Summaryは後続設計とする。

## 9. Streaming／Status／Terminal

OFF時は既存のPhase 1-G SSE Contractを維持する。

ON時の論理Event順序：

```text
start(state="generating_answer")
  → Normal Generation／BrowserへDeltaを出さない
status(state="summarizing_answer")
  → Summary Delta
  → Warning 0..n
completed
```

Fallback時はSummary Deltaを採用せず、`completed.assistant_message`のOriginalを表示する。Terminal Eventは`completed／cancelled／error`のいずれか1回だけとする。

UI Statusは最低限、次を言語別に表示する。

```text
回答を生成しています / Generating an answer
回答を要約しています / Summarizing the answer
完了 / Completed
```

## 10. UI Localization Scope

切替対象：

- Document Title
- `html lang`
- Button、Label、Heading、Placeholder
- Preview Note
- Settings名とOption表示名
- Status、Warning、Known Errorの安全な表示
- Empty State／New Chat後の説明
- Accessibility用`aria-label`等
- 要約モードの説明

切替対象外：

- Modelが生成した回答
- Model Generated Thinking
- Model Key、Profile Key、Device Key等のIdentifier
- Serverから来た未知の自由Textを機械翻訳すること
- Requestの`response_language`値

Known Error／WarningはCodeをKeyとしてUI Dictionaryから表示できる。未知Codeは固定された安全なGeneric Message、またはServerのSafe Messageをそのまま表示し、Client側で恣意的に翻訳しない。

## 11. UI Language Persistence

- Browserの`localStorage`へUI Languageだけを保存してよい。
- KeyはProject Namespaceを持つ。例：`margpa.ui_language.v1`。
- 保存値は`ja／en`だけとし、不正値は`ja`へFallbackする。
- New ChatでUI Languageを初期化しない。
- Page Reload後に復元する。
- Chat Message、Credential、Response Language、Prompt、Model Outputは`localStorage`へ保存しない。
- Storage利用不可でも日本語Defaultで動作する。

## 12. Configuration

Application Configへ次のLayer Configを追加する。

```toml
[layers.summarization]
mode = "off" # off | post_generation
backend = "main_model"
max_new_tokens = 1024
thinking_mode = "disabled"
preserve_original = true
failure_policy = "fallback_original"
```

- Application Config Schemaは`2`から`3`へ更新する。
- Deployment Profile Schemaは変更しない。
- UI LanguageはTOML／Server Runtime Configへ追加しない。
- `/api/v1/runtime`はSummary Defaultを安全に返す。
- Browser RequestのSwitchは`settings.summary_mode`へMappingする。
- Phase 1-HではSummary Backendとして`main_model`だけを受理する。

## 13. Security／Privacy

- Summary OutputもPlain Textで描画し、`innerHTML`を使わない。
- Original／Summary／PromptをServer Access Logへ出さない。
- Summary ErrorにRaw Exception、Absolute Path、Promptを含めない。
- UI DictionaryはRepository内へ保持し、外部CDN／翻訳APIを使わない。
- UI Language切替でBasic Auth／Access Control境界を変えない。
- Summary LayerはToolを呼ばない。
- Phase 1-HはGuardrail／Content Safety／Prompt Injection対策完成を主張しない。

## 14. Non-functional Requirements

- OFF時の追加Inference回数は0である。
- ON時は同じMain Modelを逐次利用し、同時Generationを行わない。
- Modelを要約ごとにReloadしない。
- Normal＋Summaryを1つのActive Conversation SessionとしてGeneration Gateで保護する。
- Summary開始前にNormal Native Streamを確実にCloseする。
- SSE Consumer Disconnect、Stop API、Runtime ShutdownのCooperative Cancelを両段階で維持する。
- CLIの既存One-shot動作を変更しない。
- 新規Runtime Dependency／JavaScript Libraryを追加しない。
- Mac Python 3.13.14とLightning Python 3.12.11のSupport Pairを維持する。

## 15. Out of Scope

- Dedicated Summary Model
- 要約Model選択UI
- Pre-generation Prompt／History要約
- RAG Context要約
- Chat履歴永続化
- 元回答の表示切替UI
- 要約品質のJudge評価
- ARGD／DAGDによる要約判定
- Prompt Injection／Content Safetyの完成
- React／Next.js／Node Build
- Machine Translation API
- UI言語のTOML永続化
- Phase 4の本格設定UI
- Lightning Full Upload／Native Validation
- Phase 1完了宣言／Backup／Git／GitHub公開

## 16. Acceptance Criteria

### 16.1 Summary Mode

- OFF時、Model Callが正確に1回であり、Phase 1-G Streaming互換である。
- ON時、NormalとSummaryが正確に各1回、重複せず逐次実行される。
- Summary RequestへOriginal Canonical Finalだけが渡る。
- Summary Thinkingは常にdisabled、maxは1024である。
- Summary成功時はSummaryだけが表示・履歴採用される。
- Summary失敗、空、Context不足、Length時はWarning付きOriginalへFallbackする。
- CancelがNormal／Summaryの両段階で成立する。
- Cancel後に次Generationが成立する。
- Shutdown Timeout／Close契約をPhase 1-Gから後退させない。

### 16.2 UI Language

- 右上Switchで日本語／Englishを即時切替できる。
- UI言語とResponse Languageの全組合せが独立して動作する。
- New Chat後もUI Languageが維持される。
- Reload後にUI Languageだけが復元される。
- Message／Credential／Model OutputをBrowser Storageへ保存しない。
- Title、`html lang`、主要ARIA、Status、Setting、Known Errorが切り替わる。
- Model Output／ThinkingをUI切替で翻訳しない。

### 16.3 Regression

- Existing Static／Unit／Integration／Model Smokeが合格する。
- Basic Auth／Non-loopback Fail Closedが後退しない。
- SSE Terminalは正確に1回である。
- Hidden ThinkingがClientへ漏れない。
- Model Load once／Close onceを維持する。

## 17. Authorization Boundary

本書はPhase 1-Hの正本要件を確定するが、実装開始を自動許可しない。実装担当は、ユーザーからPhase 1-H実装開始の明示指示を受けた後、対応Handoffの範囲だけを変更できる。

## 18. Append-Only

要件予約文書を変更せず、本書をPhase 1-Hの後継正本として追加した。

<!-- SOURCE_END 28: docs/requirements/phase_1h_summary_mode_and_ui_language_requirements_20260721174346.md -->

---

<!-- SOURCE_BEGIN 29: docs/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md -->

### Source 29: `docs/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md`

- History Target: `docs/project/phases/phase_1/history/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md`
- Source SHA-512: `5daf76c1bd32a49f36023db29e6eec381d88e5718f70dd95d0af722466886240dd68df5693e84be60bca0d65f5beeb4217ffad2ef1ebb429c24836e150e44b9b`
- Source Size: `8571` bytes

# Phase 1-I Web Presentation and UX Follow-up 要件定義

- 文書ID: `phase_1i_web_presentation_and_ux_follow_up_requirements`
- 状態: `accepted`
- 作成日時: `2026-07-25 20:00:01 JST`
- 更新日時: `2026-07-25 20:00:01 JST`
- Snapshot: `20260725200001`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- Source Review: [designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md](../history/handoffs/designer_review_phase_1_mac_web_ui_user_acceptance_and_follow_up_20260725192903.md)
- supersedes: なし

## 1. Purpose

Mac Web User Testで確認されたPhase 1-G／1-Hの基本動作を維持しながら、主要LLM Productに近い可読性と操作性へ仕上げる。

対象：

- Thinking Generation／Visibility UI整合
- Shortcut Hint
- User／Assistant Message Copy
- Sanitized Markdown Presentation
- 実装後のまとめAcceptance Test

## 2. Scope

### 2.1 Thinking

- Thinking Generation `disabled／enabled`をWeb Requestで明示できる。
- Thinking Visibility `hidden／visible`と独立させる。
- Generation OFF時にVisibilityだけONという状態を、UIで誤解なく扱う。
- ThinkingはFinal Answerと別のPresentation Regionへ表示する。
- Raw ThinkingをConversation Historyへ保存しない。
- Summary GenerationのThinkingは引き続きDisabledとする。

### 2.2 Shortcut Hint

- Current実装の`Cmd+Enter`／`Ctrl+Enter`送信を画面上で発見可能にする。
- 日本語／英語UIへ対応する。
- 表示内容と実際のKeyboard Handlerを一致させる。
- IME変換確定中のEnterを送信として扱わない。

### 2.3 Message Copy

- User MessageとAssistant MessageにCopy Buttonを付ける。
- Canonical TextをCopyする。
- Hidden Thinking、Metadata、非表示Original Summary、Rendered HTMLを混入させない。
- 成功／失敗を利用者へ通知する。

### 2.4 Markdown

- Assistant Final AnswerをMarkdownとして表示する。
- User InputはDefault Plain Textとする。
- Streaming中の不完全Markdownを安全に扱う。
- Completion後のCanonical Final AnswerをRender Sourceとする。
- XSS、危険URL、Raw HTMLをFail Closedで扱う。

## 3. Non-goals

- Persistent Conversation
- Account System
- Full Responsive UI
- Project Documentation Explainer／RAG
- Local Folder Upload
- Governance／Guard／Judge／Repair UI
- Raw Thinking Persistence
- Thinking品質保証
- Clipboard Read
- External CDN依存

## 4. Required User-facing Behavior

### 4.1 Thinking Controls

概念表示：

```text
推論生成       : OFF／ON
推論過程を表示 : OFF／ON
```

許可状態：

| Generation | Visibility | Behavior |
|---|---|---|
| OFF | OFF | Final Answerだけを生成・表示 |
| OFF | ON | UIで無効化するか、表示対象なしを明示 |
| ON | OFF | Thinkingを生成し得るが画面へ表示しない |
| ON | ON | ThinkingとFinalを別領域に表示 |

一般利用者向けDefault：

```text
Generation : OFF
Visibility : OFF
```

### 4.2 Thinking Notice

- Thinking表示は真の内部思考、正解、根拠の完全性を保証しない。
- Thinking ONはLatency／Token Usageを増やす可能性がある。
- Token上限へ達するとFinal Answerが生成されない可能性がある。
- Raw Thinkingは永続保存しない。

### 4.3 Shortcut

Composer付近へ、次に相当する表示を置く。

```text
Cmd+Enter／Ctrl+Enterで送信
```

英語表示：

```text
Send with Cmd+Enter / Ctrl+Enter
```

### 4.4 Copy

- 各User MessageにCopy Buttonを表示する。
- 完了したAssistant Final AnswerにCopy Buttonを表示する。
- Copy成功後は短時間`コピーしました／Copied`を表示する。
- Failure時は`コピーできませんでした／Could not copy`を表示する。
- Copy ButtonはKeyboard Focus可能にする。

### 4.5 Markdown

初期対応候補：

- Heading
- Paragraph
- Unordered／Ordered List
- Emphasis／Strong
- Inline Code
- Fenced Code Block
- Block Quote
- Link
- Horizontal Rule
- TableはParser選定と安全性に応じた候補

Raw HTMLは表示しない。危険なURL SchemeはLink化しない。

## 5. Message／Presentation Separation

最低限、次を区別する。

```text
User Canonical Text
Assistant Canonical Final Text
Ephemeral Thinking Text
Rendered Assistant DOM
Status／Warning／Error
```

- Browser Conversation Historyへ保存するAssistant ContentはCanonical Final Textだけとする。
- Rendered DOMからHistoryや次Requestを再構築しない。
- Thinkingを次TurnのAssistant Messageへ混入させない。
- Summary ON時はPresented SummaryだけをCanonical Assistant Contentとする。
- 非表示Original SummaryをCopyまたはDOMへ露出しない。

## 6. Streaming Requirements

- Reasoning DeltaとFinal DeltaをClientが意味的に区別できる。
- Visibility Hidden時にReasoning DeltaをClientへ送らない。
- Final DeltaはStreaming中にPlain Text表示してよい。
- Completion時にCanonical Final Contentを安全なMarkdownへ変換する。
- ReasoningはMarkdown Rendererへ渡さず、専用のPlain Text Regionへ表示する。
- Cancelled／Error／Length Warning時に不完全回答をCompleted Answerと誤認させない。

## 7. Markdown Security Requirements

- Runtime時に外部CDNへ接続しない。
- Parser／Sanitizerを追加する場合、Versionを固定する。
- Third-party License、Source、Version、Artifact Digestを記録する。
- Raw HTMLをDefault Disabledとする。
- `script`、`style`、`iframe`、Form、Event Handler属性等を拒否する。
- `javascript:`等の危険URLを拒否する。
- External Linkは安全な属性を持つ。
- Sanitized Result以外を`innerHTML`へ渡さない。
- Parser Failure時はPlain TextへFallbackする。
- Security TestなしでMarkdown Renderingを有効化しない。

## 8. Copy Security Requirements

- `navigator.clipboard.writeText`等のWriteだけを使用する。
- Clipboard内容をReadしない。
- Canonical Text以外をCopy Sourceにしない。
- Thinking Hidden時にReasoningをCopyしない。
- Clipboard API利用不能時に無言で成功扱いしない。

## 9. Configuration／Contract

Web Runtime DefaultsへThinking Modeを追加する。

Conversation Settings候補：

```text
response_language
max_new_tokens
thinking_mode
thinking_visibility
summary_mode
```

- Unknown ValueはValidation Errorとする。
- Model CapabilityにThinking Controlがなければ、Thinking Generation ControlをDisabled／Unavailableにする。
- Application DefaultとExplicit Web SettingのSourceを区別可能にする。

## 10. Automated Test Requirements

### Thinking

- Generation／Visibility 4組合せ
- Plain Text Model
- Tagged Thinking Complete／Unclosed／Malformed
- Hidden Reasoning非送信
- Visible ReasoningとFinalのRegion分離
- Summary Thinking Disabled
- Final Token Limit Warning

### Markdown

- Heading／List／Emphasis／Code／Link
- Streaming Chunk分割
- Completion後Render
- Raw HTML
- Script／Event Handler
- Dangerous URL
- Malformed Markdown
- Parser Failure Plain Text Fallback
- Japanese／English

### Copy

- User Canonical Text
- Assistant Canonical Final Text
- Markdown Source
- Thinking非混入
- Hidden Original Summary非混入
- Success／Failure Feedback

### UI

- Shortcut Hint
- `Cmd+Enter`／`Ctrl+Enter`
- IME Composition
- New Chat
- Stop
- UI Language
- Response Language

## 11. Deferred Combined Manual Test

Phase 1-I実装後に、次をまとめてUser Testする。

- 生成中New Chat
- Summary中Stop
- Browser Reload
- 別Tab同時生成／Model Busy
- Max New Tokens `0／1／2048／2049`
- Thinking 4組合せ
- Markdown表示
- User／Assistant Copy
- Shortcut Hint

## 12. Acceptance

次をすべて満たす。

1. Existing Phase 1-G／1-H Regressionがない。
2. Thinking GenerationとVisibilityが別契約として動作する。
3. ThinkingとFinalがDOM／History／Copyで混在しない。
4. Assistant Final Answerが安全にMarkdown表示される。
5. XSS TestがFail Closedである。
6. User／Assistant CopyがCanonical Contentを使用する。
7. Shortcut Hintと実動作が一致する。
8. Ruff／Mypy／Pytest／Web IntegrationがPassする。
9. User Manual更新後にCombined Manual Testを実施できる。

## 13. Authorization

ユーザーは2026-07-25、Phase 1完了前に本Follow-upを先行実施する方針と、実装担当Handoff作成を指示した。


<!-- SOURCE_END 29: docs/requirements/phase_1i_web_presentation_and_ux_follow_up_requirements_20260725200001.md -->

---

<!-- SOURCE_BEGIN 30: docs/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md -->

### Source 30: `docs/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md`

- History Target: `docs/project/phases/phase_1/history/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md`
- Source SHA-512: `cce84e7dafc471e48b2124ffeb0003a80927e3ec0d0d7498e0a8d1cd3160403ea9625f1668bcc95572b7e5c6dcad653369b4d654fed25ce6f9255baeab7acda2`
- Source Size: `6371` bytes

# Post-generation Summary Mode 要件予約

- 文書ID: `post_generation_summary_mode_requirements_reservation`
- 状態: `accepted_deferred_to_phase_1g_follow_up`
- 作成日時: `2026-07-21 09:07:25 JST`
- 更新日時: `2026-07-21 09:07:25 JST`
- Snapshot: `20260721090725`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 対象: Phase 1-G最小UI成立後の小規模Follow-up
- 正本言語: 日本語
- 最新Index: [documentation_index_20260721090725.md](../history/documentation_index_20260721090725.md)
- supersedes: なし（Post-generation Summary Mode要件系列の初回）

## 1. Decision

ユーザー向けOptionへ次を追加する。

```text
要約モード  OFF／ON
```

初期値はOFFとする。ONの場合、Main Modelが生成した最終回答をそのまま表示せず、同じMain Modelによる2回目の要約生成を通してから表示する。

本機能はPhase 1-Fへ混在させない。Phase 1-Gの最小UIを先に成立させ、その直後の小規模Follow-upで実装する。

## 2. Initial Runtime Values

```text
通常生成 max_new_tokens : 2048
要約生成 max_new_tokens : 1024
要約時Thinking          : disabled
要約Backend              : Main Model
実行方式                 : Sequential／同時常駐なし
```

要約生成を2048にしない主な理由は、Current `context_size = 4096`の中に元回答、System／要約指示、要約出力を収める必要があるためである。

要約時はThinkingを無効化し、Reasoning Token消費によって最終要約が出ない危険を抑える。

## 3. Processing Flow

```text
User Request
  → Normal Generation／max 2048
  → Canonical Final Answer抽出
  → Summary Request構築
  → Same Main Model／Thinking disabled／max 1024
  → Summary Result Validation
  → User Presentation
```

要約対象は、通常生成のCanonical Final Answerだけとする。

次は要約対象にしない。

- Model Generated Thinking／Reasoning Segment
- 生のChain of Thought
- Runtime内部状態
- System Prompt
- Governance内部Evidence

## 4. UI Requirement

一般UIへ、通常設定として次を追加する。

```text
要約モード  [ OFF | ON ]
```

- 一般利用者には単純な横スライド型ON／OFF Switchとして表示する。
- OFFがDefaultである。
- ONは内部の`post_generation` Modeへ変換する。
- 要約生成中は、通常生成と区別できるStatusを表示する。

表示例：

```text
回答を生成しています
  → 回答を要約しています
  → 完了
```

将来の研究開発者向け設定では、Backend、Token上限、失敗時Policy等を表示可能にする。

## 5. Configuration Candidate

初期候補：

```toml
[layers.summarization]
mode = "off" # off | post_generation
backend = "main_model"
max_new_tokens = 1024
thinking_mode = "disabled"
preserve_original = true
```

一般UIのBooleanはConfigへ直接Booleanとして固定せず、内部Modeへ変換する。将来、別の要約方式や専用Modelを追加可能にするためである。

## 6. Architecture Boundary

SummarizationはPresentation上の文字列短縮ではなく、追加Inferenceを伴うResponse Transformation Layerとして扱う。

```text
Application／Generation Pipeline
  → Summarization Port
      └─ Initial Adapter: Main Model再利用
      └─ Future Adapter : Dedicated Summary Model
  → Presentation
```

- Main Model固有処理をApplication Coreへ入れない。
- 要約Modelを将来交換可能にする。
- Main Modelと別Modelを同時常駐させることを初期要件にしない。
- ConfigでLayer単位にOFF／ON相当を切り替え可能にする。

## 7. Original Answer Preservation

要約前のCanonical Final Answerは破棄しない。

- 将来のAudit Logへ元回答と要約回答を別Artifact／Eventとして記録できる。
- UIでは将来「元の回答を表示」を追加可能にする。
- 要約による欠落、歪み、過剰短縮を比較可能にする。
- 元回答をユーザーへ常時表示することは初期必須ではない。
- Model Generated ThinkingはOriginal Answer Preservationの対象外とする。

## 8. Failure／Token Handling

- Summary Callが失敗した場合、元回答を警告付きで表示する。
- Summary Outputが空の場合、元回答へFallbackする。
- `finish_reason=length`を検出し、要約が上限へ到達した事実を隠さない。
- 元回答自体がToken上限へ到達している場合、そのWarningを要約後も維持する。
- Context残量が不足する場合、設定値を黙って超過させない。
- Effective Summary Token上限は、将来Prompt TokenとSafety Marginから動的に縮小可能にする。
- Cancellationは通常生成中と要約生成中の両方で成立させる。

## 9. Streaming

初期版では、要約モードON時に元回答をStreaming表示しない。

```text
通常生成中 : Statusのみ表示
要約生成中 : 要約結果をStreaming表示可能
```

元回答を先に表示してから要約回答へ置換すると、表示内容が突然変化し、保存対象も曖昧になるため初期版では採用しない。

## 10. Out of Scope

次は本機能と分離する。

- ユーザー入力の生成前要約
- 会話履歴の自動圧縮
- RAG Contextの要約
- ARGD／DAGDによる要約許可判定
- Dedicated Summary Modelの初期同時常駐
- 要約品質のLLM-as-a-Judge評価

入力や会話履歴の生成前要約は、前提・決定事項・入力構造を失う危険があるため、将来のContext Managementとして別途設計する。

## 11. Acceptance Direction

将来実装時は最低限次を確認する。

- OFF時は追加Inferenceが発生しない。
- ON時は通常生成と要約生成が各1回だけ発生する。
- 要約時Thinkingが無効である。
- 要約上限が1024である。
- 元回答と要約回答が混同されない。
- 要約失敗時に元回答へ安全にFallbackする。
- Cancelが両段階で成立する。
- Model Adapter交換性を壊さない。

## 12. Authorization Boundary

本書は要件予約であり、Phase 1-F Source／Config／UIの変更を許可しない。実装はPhase 1-G最小UI Accepted後の別Handoffにより開始する。

<!-- SOURCE_END 30: docs/requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md -->

---

<!-- SOURCE_BEGIN 31: docs/requirements/post_phase_1e_research_platform_requirements_20260719112304.md -->

### Source 31: `docs/requirements/post_phase_1e_research_platform_requirements_20260719112304.md`

- History Target: `docs/project/phases/phase_1/history/requirements/post_phase_1e_research_platform_requirements_20260719112304.md`
- Source SHA-512: `2538c34823a01e8f2daf61ebdf90125c6ca993d7b3cde7fa3877ae1cb1db55f075bbff1cbeca5e97aa6a04ca99f3729c66b646e088152badf3c89a28c1bfebea`
- Source Size: `14374` bytes

# Phase 1-E後 AI実験・統治Platform拡張要件

- 文書ID: `post_phase_1e_research_platform_requirements`
- 状態: `accepted_planning_only`
- 作成日時: `2026-07-19 11:23:04 JST`
- 更新日時: `2026-07-19 11:23:04 JST`
- Snapshot: `20260719112304`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-E完了後のProject全体要件
- 正本言語: 日本語
- 関連: [generic_governance_definition_platform_requirements_20260719112304.md](../history/requirements/generic_governance_definition_platform_requirements_20260719112304.md)
- 最新Index: [documentation_index_20260719112304.md](../history/documentation_index_20260719112304.md)
- supersedes: なし（新規要件系列）

## 1. 文書の位置づけ

本文書は、Phase 1-E完了後に優先度を上げる機能群と、それに伴うProject全体の要件変更を正本化する。

今回の変更は、単なる機能追加ではない。`margpa-runtime-llm`を、単一のLocal LLM推論Runtimeから、次の性格を持つプラットフォームへ拡張する。

> 機能層、統治層、評価、修復、実験、配置環境をそれぞれ交換・観測・有効化・無効化できる、疎結合なAI実験・Runtime Governance Platform。

## 2. 変更後の最上位目標

### 2.1 骨格の優先

- 小型Modelの性能を限界まで追求するより、全機能を差し替え可能にする骨格を先に成立させる。
- 将来、高性能機材、Home Server、Lightning AI Studio、Cloud GPU、別Backendを使う際に、Application Coreを作り直さない。
- Model、Guard、Judge、RAG、Agent、Tool、Repair、Governance Definitionの交換はPortとAdapterを通じて行う。

### 2.2 研究装置としての目標

すべての任意ComponentとそのGovernanceを個別に制御し、次を比較できることを重視する。

- Governanceなし
- Governanceの観測のみ
- Governanceによる介入あり
- Guard、Judge、Repair、Agent等の個別ON／OFF
- 同一Input、Model、Seed、Configでの再現実行
- 品質、Latency、Token、追加Model Call、Repair回数の比較

目標は「疎結合です」という構造上の主張に留まらず、構成差による効果とコストを再現可能に比較できる状態である。

## 3. Scopeの基本単位

### 3.1 Functional Component

Functional Componentは実際の処理を行う。

- Main Model
- Input Processing
- RAG
- Guardrail
- Policy
- Judge
- Repair
- Agent
- Tool
- Memory
- Output Processing
- Audit Storage
- Status Projection

### 3.2 Governance Point

Governance PointはFunctional Componentの前後または必要な境界に置く軽量な実行点である。そのPointに必要なRuleだけを適用する。

### 3.3 Governance Control Plane

定義、Compile、状態、Evidence、Action解決、Auditを共通化する。各Pointに完全なMARGPA一式を複製しない。

### 3.4 Governance Binding

PointとDefinitionをBindingする設定単位とする。Bindingは少なくとも次を持つ。

- 対象Point
- Definition ReferenceまたはCapability Requirement
- Profile
- Mode
- Activation Condition
- Budget
- Priority
- Required／Optional

DefinitionはRuleのSource、Pointは処理経路上の場所、Bindingは接続設定である。JSON 1個を1つの実行層と同一視しない。

## 4. 疎結合と依存性要件

### 4.1 Component制御

- Main Model以外の任意Functional Componentは`enabled`を持つ。
- 各Governance Bindingは`mode = off | observe | enforce`を持つ。
- `off`: 実行せず、Governance由来のToken、Call、Repairを発生させない。
- `observe`: 判定と記録は行うが、出力や処理経路に介入しない。
- `enforce`: 停止、拒否、修復、再生成、制約適用等の登録済みActionを実行できる。
- Main ModelはChat実行時の必須Componentとするが、Main Model Governanceは無効化できる。

### 4.2 階層構造

平坦で曖昧なBoolean群ではなく、少なくとも次の責務分離を持つ。

```toml
[components.guard]
enabled = false

[components.guard.governance]
mode = "off"
```

### 4.3 構成Validation

すべてのComponentとBindingについて、次を表現・検証できること。

- Required Dependency
- Optional Dependency
- Conflict
- Capability Requirement
- Degraded Mode
- Invalid Combination
- Hot Reload可否
- Model Reload必要性
- Application Restart必要性
- Side Effect Level

例：

- `Agent OFF + Agent Governance ON`は通常はInvalidとする。
- `Judge OFF + Repair ON`は、RepairのTrigger SourceがJudge以外にあるかで有効性が変わる。
- 依存不足を黙って無視せず、Error、Warning、Degradedのいずれかとして表示・記録する。

### 4.4 無効化できない外部制約

Application ConfigのON／OFFは、Host OS、System Policy、Developer Policy、外部Service、実在する権限・法令・承認条件を無効化しない。

Tool PermissionをOFFにすることを`allow all`と解釈しない。Permission判定が無い場合は、Toolを無効化するか、安全側に拒否する。

## 5. Governance実行要件

### 5.1 共有Control Planeと分散Point

採用構成は次とする。

```text
Governance Control Plane
  ├─ Definition Registry／Provider
  ├─ Validator／Adapter／Compiler
  ├─ Rule Selection
  ├─ Namespaced Governance State
  ├─ Evidence／Audit
  ├─ Conflict Resolution
  └─ Action Resolver

Execution Pipeline
  ├─ Input Governance Point
  ├─ RAG Governance Point
  ├─ Guardrail Governance Point
  ├─ Agent Governance Point
  ├─ Tool Governance Point
  ├─ Judge Governance Point
  ├─ Main Model Governance Point
  └─ Output／Repair Governance Point
```

### 5.2 実行負荷

- Startup時はMetadataを中心に読み、Definition本体は必要時にLazy Loadする。
- ターンに必要なDefinitionとRuleのみをCompileする。
- 決定論的に判定できる項目はPython側で処理する。
- 意味的判定が必要なときだけSemantic Evaluatorを呼ぶ。
- Definition Hash、Adjustment Hash、Compiler Version、PointをKeyにCompiled PlanをCacheする。
- Model Call、Token、Latency、Repair、RetryにBudgetを設ける。
- Functional Componentが呼ばれない場合、対応Pointも呼ばない。

各層にPointを分散させるだけで軽量になるわけではない。上記のActivation、Selection、Cache、Budgetを必須とする。

### 5.3 StateとAction

- Turn／Session単位のShared Context、PointごとのLocal State Namespace、Append-Only Evidence／Eventを分離する。
- 単一のMutableな巨大Stateに集約しない。
- 複数PointからActionが発火した場合は、中央のAction Resolverで最終解決する。
- 未知ActionはRecommendationとEvidenceに残すだけとし、登録済みAction Adapter、Capability、Authorityがなければ実行しない。
- GovernanceがGovernanceを無限に呼ぶ再帰構造を禁止する。Meta-governanceは将来機能とし、原則OFFまたは非同期、最大Depth 1とする。

## 6. Experiment Runtime要件

### 6.1 Profile

少なくとも次の比較Profileを作成可能にする。

```text
baseline_no_governance
baseline_empty_governance
main_governance_observe
main_governance_enforce
guard_judge_repair
all_implemented_layers
```

### 6.2 Run Record

一回の実験実行に次を関連づけて保存する。

- `experiment_id`
- `run_id`
- Model ID／Artifact Digest／Quantization／Backend
- Definition／Package／Adjustment／Compiled Plan Digest
- Effective Config Snapshot／Hash／Source
- Enabled Component／Governance Mode
- Seed
- Input／Output
- Token Count／Latency／Stop Reason
- Audit Result／Score／Deviation／Severity
- Repair Count／Retry Count
- Runtime Status／Warning／Error

## 7. Runtime Status／Observability要件

Status ReportingはGuardrail等の前に直列で挿入する層ではなく、Eventを購読する横断的なProjectionとする。

- 各Componentは共通Runtime Event Contractに従う。
- CLI、Web UI、Audit Log、Experiment Recordが同じEventを利用できる。
- Reporting／Projectionの障害でInference本体を失敗させない。
- 必須Lifecycle Stateと、表示／永続化するReportingを分離する。
- DAGD内部のGovernance Status Reporterと、全RuntimeのStatus Projectionを区別する。

表示候補：

```text
idle
preparing
governance_precheck
guarding
generating
judging
repairing
agent_running
completed
cancelled
failed
```

加えて、Current Component、Governance State、Attempt、Warning、Elapsed Timeを表示可能にする。

## 8. UI／Configuration要件

### 8.1 一般向けの基本UI

一般利用者が触る可能性を考慮し、表側は次を中心にする。

- New Chat
- Chat History／Resume
- Main Model
- Response Language
- Generate／Stop／Regenerate
- 簡易なCurrent Status

`New Chat`はTOML設定ではなくApplication Actionである。

### 8.2 開発・研究設定

上記以外は、UI上の`開発・研究設定`に集約し、次の見出しで分離する。

- Generation
- Model Runtime
- Component Structure
- Governance
- Evaluation／Repair
- Agent／Tool
- Experiment
- Status／Audit
- Deployment

### 8.3 Typed Config Service

UIからVersion Control対象の`config/application.toml`を直接書き換えない。

```text
UI Input
  ↓
Typed Schema Validation
  ↓
Effective Config Preview
  ↓
Diff／Source／Apply Mode表示
  ↓
Atomic Save
```

- `config/application.toml`はRepository内のDefault正本とする。
- UIはGit対象外のLocal Runtime Override TOMLへ保存する。具体PathはPhase 4で決める。
- 変更前後のDiff、各値のSource、Effective Configを表示する。
- 適用時期をImmediate／Next Request／Model Reload／Application Restartで表示する。
- 将来のReset／Export／Import／Presetに対応できる。
- Governance調整UIは原始Definition JSONを変更せず、Adjustment Overlay／Profileを編集する。

## 9. 外部開発／検証環境要件

### 9.1 採用環境

Phase 2の主要外部開発／検証環境は`Lightning AI Studio`とする。

- 現行Repositoryを通常のLinux開発環境として動かす。
- Linux x86_64／CUDA／llama.cpp用Deployment Profileを追加する。
- SSH、VS Code、永続Storage、GPU、Port公開を使用する。
- 同一Model Port、GGUF、Config Composition、Test Contractを共有する。
- Model ArtifactはGitに含めず、環境ごとに配置しHashを検証する。
- Mac MetalとLightning CUDAの実効Config、Capability、Latency、Token Speed、Outputを比較できる。

### 9.2 ZeroGPU

Hugging Face ZeroGPUは直近のMVP実行基盤には採用しない。Phase 10の次の用途に延期する。

- 公開Demo
- PyTorch／Transformers Backend交換性の実証
- Gradio Adapterの追加
- GGUF／llama.cppとは別系統のDeployment Adapter検証

## 10. 将来のFunctional LayerとGovernance Hook

次のFunctional Layerは段階的に追加する。各Layerの実装時に、Governance PointとBinding Hookも用意する。ただし、実装前のLayerの完全なGovernance処理を先行実装しない。

| Functional Layer | Governance例 | 主な関心事 |
|---|---|---|
| Main Model | Main Governance | Premise、Context、Scope、Generation Constraint |
| Guardrail | Guard Governance | Injection、Jailbreak、Secret、Policy |
| Judge | Judge Governance | Evaluation Criteria、Independence、Confidence、Conflict |
| Repair | Repair Governance | Trigger、Budget、Success Criteria、Loop Prevention |
| Agent | Agent Governance | Plan、Step、State、Handoff、Completion |
| Tool | Tool Governance | Permission、Scope、Side Effect、Approval |
| RAG | RAG／Data Governance | Source、Chunk、Evidence、Injection、Leakage |
| Policy | Policy Governance | Applicable Policy、Priority、Exception、Record |

## 11. Non-functional Requirements

### 11.1 交換性

- Definition名、Model名、OS名、GPU種別をDomain Coreにハードコードしない。
- Adapter、Provider、Registry、CapabilityとTyped Contractで解決する。

### 11.2 再現性

- Artifact、Definition、Config、Compiler、Profile、Seed、EnvironmentのIdentityとHashを記録する。
- 実効値とSourceを記録する。

### 11.3 障害分離

- Status Projection、Audit Sink、非必須Governance Providerの障害でMain Inferenceを必ず失敗させない。
- Fail Open／Fail ClosedはComponent、Mode、Required Flag、Side Effectで明示的に決める。

### 11.4 セキュリティ

- Definition JSONを実行Codeとして扱わない。
- Tool／Agent／外部I/Oの実行は、Modelの推奨だけで行わない。
- 既存の権限、Policy、承認条件に対する解釈と、権限の生成を区別する。

## 12. Scope外・延期

- Phase 1-E完了前の大規模なGovernance Platform実装
- Phase 3での16 GD全実装・全同時実行
- CDOGDを必須とする自動Routing
- ZeroGPUの即時対応
- 生のChain of Thoughtの保存・公開
- JSONからの任意Code実行
- Application ConfigからのSystem／Host／外部Policy無効化

## 13. Acceptance Criteria

### Phase 2受入基準

- Component RegistryがON／OFF、Dependency、Conflict、Capabilityを表現できる。
- Governance Modeの`off／observe／enforce`を型として表現できる。
- Experiment ProfileとRun RecordによりBaselineと構成差を比較できる。
- Event ContractとStatus ProjectionがInferenceと疎結合である。
- Mac MetalとLightning Linux／CUDAで共通Contract Testを実行できる。

### Phase 3受入基準

- Governance Definitionが0個でもMain Model Runtimeが完全に動作する。
- 任意のDefinition PackageをCore改修なしで登録・Bindingできる。
- Source JSONを変更せず、Adapter／IR／Compiler／Adjustmentで実行Planを生成できる。
- Main Governanceで`off／observe／enforce`を比較できる。
- Definitionなしの`enforce`を成功扱いしない。

## 14. Authorization Boundary

本文書は要件のAccepted Snapshotである。今回のユーザー指示はDocs作成の許可であり、Phase 2以降のSource、Config、Test、Dependency、外部環境を実装・変更する許可ではない。

<!-- SOURCE_END 31: docs/requirements/post_phase_1e_research_platform_requirements_20260719112304.md -->

---

<!-- SOURCE_BEGIN 32: docs/requirements/project_requirements_20260718174637.md -->

### Source 32: `docs/requirements/project_requirements_20260718174637.md`

- History Target: `docs/project/phases/phase_1/history/requirements/project_requirements_20260718174637.md`
- Source SHA-512: `a5d7c055caf477b192d17f1c1e46d638077df98ec86062a3a45aad299e78df9b69217c33a3b347e89f9df6ec0f7b7b36651d721eb39a5b398b23f38e3b59dee3`
- Source Size: `7659` bytes

# MARGPA Runtime LLM プロジェクト要件

- 文書ID: `project_requirements`
- 状態: `current`
- 作成日時: `2026-07-18 17:46:37 JST`
- 更新日時: `2026-07-18 17:46:37 JST`
- 対象: プロジェクト全体
- 正本言語: 日本語
- 文書ルール: [documentation_rules_20260718174637.md](../history/requirements/documentation_rules_20260718174637.md)

## 1. プロジェクト識別情報

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

プロジェクトルート：

```text
/path/to/margpa-runtime-llm
```

## 2. プロダクト定義

Hugging Face由来の事前学習済みオープンモデルを利用し、ローカルおよび将来のクラウド環境で動作できるGPT風対話型LLMシステムを構築する。

単なるChat UIではなく、モデル外部のRuntimeが推論、統治、監査、評価、修復、安全性、権限を管理するシステムとする。

成果物の位置づけ：

> Hugging Face由来の事前学習済みオープンモデルを用い、ローカル推論、対話管理、監査、評価、修復、外部統治を一体化した、モデル非依存のRuntime Governance型LLMプロトタイプ。

基盤モデル自体を独自に事前学習したとは主張しない。

## 3. MVPの対応範囲

少なくとも次の対話を対象とする。

- AI研究
- AI設計
- AI実装
- 開発相談
- 要件整理
- Architecture設計
- コード関連
- 技術調査
- 一般的な質問
- 普通の雑談

## 4. 機能Scope

段階的に次を統合する。

- ローカル推論
- 会話管理
- GPT風Web UI
- Streaming
- 会話履歴
- 履歴再開
- 生成停止
- 回答再生成
- Generation Config
- Model交換
- Runtime Governance
- ARGD／DAGD統合
- Guardrail
- Prompt Injection対策
- Tool Permission
- Audit Log
- SHA-512整合性検証
- 回答評価
- Deviation検出
- Repair／Regeneration
- 高水準の説明概要
- RAG
- AI Agent
- LLM-as-a-Judge
- Governance Definition交換
- Local／Cloud／Hybrid展開

## 5. 優先順位

1. 要求機能が一通り実際に動くこと
2. システム全体の骨格を成立させること
3. Moduleが分離・交換可能であること
4. Runtime Governance、監査、説明、修復が成立すること
5. 現在のMacBook Proで継続的に動作すること
6. GitHubへ成果物として提示できること
7. 推論速度
8. Context長
9. 回答品質

小型モデルの回答性能が十分高くなくても、システム全体の機能が成立すれば初期MVPとして許容する。

将来、機材更新やCloud移行を行ったときに、Modelだけを交換して高性能化できる状態を優先する。

## 6. 設計思想

ユーザーの基本思想：

> 基本、可能な限り全部分離する。依存性は敵。オブジェクト指向、疎結合、交換可能性を基本とする。

採用原則：

- 単一責任
- 疎結合
- 依存性逆転
- Interface／Port経由の接続
- 依存性注入
- Model Adapter
- Storage Adapter
- Governance Adapter
- 外部I/Oと内部Logicの分離
- Framework固有コードの局所化
- 循環依存の禁止
- Module単位で交換・無効化・Test可能
- すべてを無理にClass化しない
- Framework自体をDomain Logicにしない
- PathをCoreへハードコードしない
- Secretを分離する

初期構成はMicroservicesではなく、内部が明確に分離されたModular Monolithとする。

## 7. 実行環境

```text
PC              : MacBook Pro
Hardware Model  : Mac14,9
SoC             : Apple M2 Pro
CPU             : 10コア（高性能6 + 高効率4）
GPU             : Apple M2 Pro 内蔵GPU
RAM             : 16GB LPDDR5ユニファイドメモリ
Architecture    : Apple Silicon / ARM64
GPU API         : Metal / MPS
CUDA            : 使用不可
内蔵Display      : 3024 × 1964 Retina
外部Display      : BenQ XL2420T / 1920 × 1080
```

制約：

- 16GBをOS、Model、KV Cache、RAG、UI、監査等で共有する
- 小～中規模の量子化Modelを中心とする
- 複数の大型Modelを常時同時ロードしない
- Judgeは原則On-Demandとする
- Full Governanceでは推論回数が増える可能性がある
- 速度、発熱、消費電力、Memoryを後で実測する
- CUDA専用処理をInitial Coreへ持ち込まない

## 8. Context保持方針

- 初期段階では長大なContextを最優先しない
- まず要求機能を一つずつ完成させる
- 会話履歴、要約、検索、長期記憶のHookは設ける
- 機材更新またはCloud利用後に強化する
- ARGDの無断要約禁止と物理的Context上限の整合は今後設計する

## 9. Local／Cloud両対応

Application Coreを共通化し、Deployment Profileで切り替える。

```text
Local Profile
  Metal / MPS / MLX / llama.cpp
  Local Model
  JSON / JSONL

Cloud Profile
  CUDA / vLLM等
  GPU Server
  PostgreSQL / Object Storage等

Hybrid Profile
  UIとApplicationはLocal
  推論だけCloud
```

初期から守ること：

- macOS固有処理をApplication Coreへ入れない
- Device選択を設定化する
- Model BackendをAdapter化する
- StorageをAdapter化する
- Cloud SDKをCoreへ入れない
- Secretを外部設定へ分離する

## 10. 初期Model構成

詳細は[model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)を正本とする。

```text
Main Model:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf
  Q4_K_M

Guard Model:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
  Q8_0
  Phase 4

LLM-as-a-Judge:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
  Q5_K_M
  将来On-Demand
```

必要性が出た場合の通常版候補：

```text
Qwen/Qwen3Guard-Gen-0.6B
AtlaAI/Selene-1-Mini-Llama-3.1-8B
```

## 11. 初期対象外

- Fine-tuning
- LoRA
- DPO
- RLHF
- 継続事前学習
- 独自Weight更新
- Image入力
- Docker
- Microservices化
- SQL必須化
- 16個の将来GD実装
- CDOGDによる自動Routing
- Judgeの常時稼働
- 複数大型Modelの同時常駐

## 12. 現在の禁止事項

明示的な実装解禁があるまで、原則として次を行わない。

- 実装
- Source File作成・変更
- Config File作成・変更
- Dependency Install
- 追加Model Download
- Git初期化
- 外部Serviceへの変更操作
- 勝手な技術選定確定

個別に許可され完了した操作：

- Project構造の読み取り確認
- 専用範囲の`.DS_Store`削除
- Finder Aliasの削除
- POSIX Symbolic Linkの作成
- 3つのGGUF参照確認
- このDocs一式の作成

これらは一般的な実装解禁を意味しない。

## 13. 現在の主要未決事項

- Project全体のDirectory構成
- Python Package構成
- Domain／Application／Port／Adapter境界
- Local Inference Backend
- Config方式
- Model Registry形式
- Dependency管理方式
- UI技術
- API境界
- Test構成
- Log／Data Directory
- Governance Compiler仕様
- Audit JSON Canonicalization
- GuardのFail Open／Fail Closed
- Repository License

## 14. 関連文書

- [system_architecture_20260718174637.md](../history/architecture/system_architecture_20260718174637.md)
- [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md)
- [implementation_roadmap_20260718174637.md](../history/architecture/implementation_roadmap_20260718174637.md)

<!-- SOURCE_END 32: docs/requirements/project_requirements_20260718174637.md -->

---

<!-- SOURCE_BEGIN 33: docs/requirements/project_requirements_20260718193435.md -->

### Source 33: `docs/requirements/project_requirements_20260718193435.md`

- History Target: `docs/project/phases/phase_1/history/requirements/project_requirements_20260718193435.md`
- Source SHA-512: `e9ecc2eee77441b91a4d945486047e86e61ae0ca0da67c79ec7d84c49963dd8ff4cd9b290ed5088e966e4750d85efcfed2c4273daa42d2578ddab032ecb4656b`
- Source Size: `7762` bytes

# MARGPA Runtime LLM プロジェクト要件

- 文書ID: `project_requirements`
- 状態: `current`
- 作成日時: `2026-07-18 19:34:35 JST`
- 更新日時: `2026-07-18 19:34:35 JST`
- 対象: プロジェクト全体
- 正本言語: 日本語
- supersedes: `project_requirements_20260718174637.md`
- 文書ルール: [documentation_rules_20260718193435.md](../history/requirements/documentation_rules_20260718193435.md)

## 1. プロジェクト識別情報

```text
Project Name : margpa-runtime-llm
Display Name : MARGPA Runtime LLM
Internal Name: Nazuna Research Governance LLM
```

プロジェクトルート：

```text
/path/to/margpa-runtime-llm
```

## 2. プロダクト定義

Hugging Face由来の事前学習済みオープンモデルを利用し、ローカルおよび将来のクラウド環境で動作できるGPT風対話型LLMシステムを構築する。

単なるChat UIではなく、モデル外部のRuntimeが推論、統治、監査、評価、修復、安全性、権限を管理するシステムとする。

成果物の位置づけ：

> Hugging Face由来の事前学習済みオープンモデルを用い、ローカル推論、対話管理、監査、評価、修復、外部統治を一体化した、モデル非依存のRuntime Governance型LLMプロトタイプ。

基盤モデル自体を独自に事前学習したとは主張しない。

## 3. MVPの対応範囲

少なくとも次の対話を対象とする。

- AI研究
- AI設計
- AI実装
- 開発相談
- 要件整理
- Architecture設計
- コード関連
- 技術調査
- 一般的な質問
- 普通の雑談

## 4. 機能Scope

段階的に次を統合する。

- ローカル推論
- 会話管理
- GPT風Web UI
- Streaming
- 会話履歴
- 履歴再開
- 生成停止
- 回答再生成
- Generation Config
- Model交換
- Runtime Governance
- ARGD／DAGD統合
- Guardrail
- Prompt Injection対策
- Tool Permission
- Audit Log
- SHA-512整合性検証
- 回答評価
- Deviation検出
- Repair／Regeneration
- 高水準の説明概要
- RAG
- AI Agent
- LLM-as-a-Judge
- Governance Definition交換
- Local／Cloud／Hybrid展開

## 5. 優先順位

1. 要求機能が一通り実際に動くこと
2. システム全体の骨格を成立させること
3. Moduleが分離・交換可能であること
4. Runtime Governance、監査、説明、修復が成立すること
5. 現在のMacBook Proで継続的に動作すること
6. GitHubへ成果物として提示できること
7. 推論速度
8. Context長
9. 回答品質

小型モデルの回答性能が十分高くなくても、システム全体の機能が成立すれば初期MVPとして許容する。

将来、機材更新やCloud移行を行ったときに、Modelだけを交換して高性能化できる状態を優先する。

## 6. 設計思想

ユーザーの基本思想：

> 基本、可能な限り全部分離する。依存性は敵。オブジェクト指向、疎結合、交換可能性を基本とする。

採用原則：

- 単一責任
- 疎結合
- 依存性逆転
- Interface／Port経由の接続
- 依存性注入
- Model Adapter
- Storage Adapter
- Governance Adapter
- 外部I/Oと内部Logicの分離
- Framework固有コードの局所化
- 循環依存の禁止
- Module単位で交換・無効化・Test可能
- すべてを無理にClass化しない
- Framework自体をDomain Logicにしない
- PathをCoreへハードコードしない
- Secretを分離する

初期構成はMicroservicesではなく、内部が明確に分離されたModular Monolithとする。

## 7. 実行環境

```text
PC              : MacBook Pro
Hardware Model  : Mac14,9
SoC             : Apple M2 Pro
CPU             : 10コア（高性能6 + 高効率4）
GPU             : Apple M2 Pro 内蔵GPU
RAM             : 16GB LPDDR5ユニファイドメモリ
Architecture    : Apple Silicon / ARM64
GPU API         : Metal / MPS
CUDA            : 使用不可
内蔵Display      : 3024 × 1964 Retina
外部Display      : BenQ XL2420T / 1920 × 1080
```

制約：

- 16GBをOS、Model、KV Cache、RAG、UI、監査等で共有する
- 小～中規模の量子化Modelを中心とする
- 複数の大型Modelを常時同時ロードしない
- Judgeは原則On-Demandとする
- Full Governanceでは推論回数が増える可能性がある
- 速度、発熱、消費電力、Memoryを後で実測する
- CUDA専用処理をInitial Coreへ持ち込まない

## 8. Context保持方針

- 初期段階では長大なContextを最優先しない
- まず要求機能を一つずつ完成させる
- 会話履歴、要約、検索、長期記憶のHookは設ける
- 機材更新またはCloud利用後に強化する
- ARGDの無断要約禁止と物理的Context上限の整合は今後設計する

## 9. Local／Cloud両対応

Application Coreを共通化し、Deployment Profileで切り替える。

```text
Local Profile
  Metal / MPS / MLX / llama.cpp
  Local Model
  JSON / JSONL

Cloud Profile
  CUDA / vLLM等
  GPU Server
  PostgreSQL / Object Storage等

Hybrid Profile
  UIとApplicationはLocal
  推論だけCloud
```

初期から守ること：

- macOS固有処理をApplication Coreへ入れない
- Device選択を設定化する
- Model BackendをAdapter化する
- StorageをAdapter化する
- Cloud SDKをCoreへ入れない
- Secretを外部設定へ分離する

## 10. 初期Model構成

詳細は[model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)を正本とする。

```text
Main Model:
  Qwen/Qwen3-4B-GGUF
  Qwen3-4B-Q4_K_M.gguf
  Q4_K_M

Guard Model:
  DevQuasar/Qwen.Qwen3Guard-Gen-0.6B-GGUF
  Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf
  Q8_0
  Phase 4

LLM-as-a-Judge:
  bartowski/Selene-1-Mini-Llama-3.1-8B-GGUF
  Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf
  Q5_K_M
  将来On-Demand
```

必要性が出た場合の通常版候補：

```text
Qwen/Qwen3Guard-Gen-0.6B
AtlaAI/Selene-1-Mini-Llama-3.1-8B
```

## 11. 初期対象外

- Fine-tuning
- LoRA
- DPO
- RLHF
- 継続事前学習
- 独自Weight更新
- Image入力
- Docker
- Microservices化
- SQL必須化
- 16個の将来GD実装
- CDOGDによる自動Routing
- Judgeの常時稼働
- 複数大型Modelの同時常駐

## 12. 現在の禁止事項

明示的な実装解禁があるまで、原則として次を行わない。

- 実装
- Source File作成・変更
- Config File作成・変更
- Dependency Install
- 追加Model Download
- Git初期化
- 外部Serviceへの変更操作
- 勝手な技術選定確定

個別に許可され完了した操作：

- Project構造の読み取り確認
- 専用範囲の`.DS_Store`削除
- Finder Aliasの削除
- POSIX Symbolic Linkの作成
- 3つのGGUF参照確認
- このDocs一式の作成
- Project全体のDirectory構成決定
- Phase 1最小Directoryの作成

これらは一般的な実装解禁を意味しない。

## 13. 現在の主要未決事項

- Local Inference Backend
- Config方式
- Model Registry形式
- Dependency管理方式
- UI技術
- API境界
- Governance Compiler仕様
- Audit JSON Canonicalization
- GuardのFail Open／Fail Closed
- Repository License

## 14. 関連文書

- [system_architecture_20260718193435.md](../history/architecture/system_architecture_20260718193435.md)
- [project_directory_structure_20260718192110.md](../history/architecture/project_directory_structure_20260718192110.md)
- [model_strategy_20260718174637.md](../history/architecture/model_strategy_20260718174637.md)
- [runtime_governance_20260718174637.md](../history/governance/runtime_governance_20260718174637.md)
- [audit_evaluation_security_20260718174637.md](../history/governance/audit_evaluation_security_20260718174637.md)
- [implementation_roadmap_20260718193435.md](../history/architecture/implementation_roadmap_20260718193435.md)

<!-- SOURCE_END 33: docs/requirements/project_requirements_20260718193435.md -->

---

<!-- SOURCE_BEGIN 34: docs/requirements/public_identity_and_naming_decision_20260721112925.md -->

### Source 34: `docs/requirements/public_identity_and_naming_decision_20260721112925.md`

- History Target: `docs/project/phases/phase_1/history/requirements/public_identity_and_naming_decision_20260721112925.md`
- Source SHA-512: `8cc9425ef0050b7525cd0404d3151f51585d4018f558b3b136d7d8003a03d1b4523db25f3c63546e301f4bdbd533b0ffb928badd239cfa0b47e84a4db8fe8fc1`
- Source Size: `3357` bytes

# 公開名義・名称の統一決定

- 文書ID: `public_identity_and_naming_decision`
- 状態: `current_mandatory`
- 作成日時: `2026-07-21 11:29:25 JST`
- 更新日時: `2026-07-21 11:29:25 JST`
- Snapshot: `20260721112925`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- 関連方針: [public_identity_and_personal_information_policy_20260721111659.md](../history/requirements/public_identity_and_personal_information_policy_20260721111659.md)
- supersedes: なし（公開名義の例外なし統一を確定する追加正本）

## 1. Mandatory Decision

今後使用する第一者の名義、名称、作者名、研究名義、Maintainer表示名、研究主体名は、すべて次へ統一する。

```text
Nazuna Research
```

現在、別の第一者名義をDocsへ残す承認済み例外はない。

## 2. Decision Authority

`Nazuna Research`以外の第一者識別子を使用する技術的必要性は、本Projectの設計者役Taskだけが判断できる。

他の担当Taskは、次を行わない。

- 独自判断による旧名義の復元
- 外部Account HandleのDocsへの追加
- 作者名の短縮、翻訳、別名化
- 歴史説明を理由とした廃止済み名義の再掲
- Source／Docs／Metadataへの例外追加

必要性が疑われる場合は、実値を書かずに設計者役TaskへEscalateする。

## 3. Fixed Public Mapping

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Project Internal Name        : Nazuna Research Governance LLM
Repository Organization      : margpa-labs
Public Repository            : https://github.com/margpa-labs/margpa-runtime-llm
```

## 4. Machine-safe Slug

Spaceを使用できないPackage ID、Namespace、Directory例等では、次のMachine-safe Slugを使用できる。

```text
nazuna-research
```

これは別名義ではなく、`Nazuna Research`を機械識別子へ正規化した表現である。

例：

```text
nazuna-research.margpa
nazuna-research_domain_extensions
```

## 5. Commit Traceability

Commit Author Nameは`Nazuna Research`とする。

Commit Metadataから個人GitHub Accountへ辿れることは許容する。ただし、Account Handleや個人EmailをDocsへ記載する必要性は別問題であり、現時点では記載しない。

## 6. Documentation Requirement

- 新規Docsでは`Nazuna Research`を使用する。
- Historical Docsを公開候補へ含める場合も、第一者名義を`Nazuna Research`へ統一する。
- 廃止済み名義を移行説明や検索結果としてDocsへ再掲しない。
- Scrub Reportは削除対象の実値を記録しない。
- 全担当向けCommon RuleとDocumentation Indexは本Decisionを参照する。

## 7. Current Verification State

2026-07-21 11:29:25 JST時点で、`docs/`全体の廃止済み第一者名義に対するCase-insensitive Search結果は0件である。

Machine-safe Slugは、必要なGovernance Package／Namespace例にだけ存在する。

## 8. Authorization Boundary

本書は名義規則を即時適用する。

本書だけではSource、Config、Git Metadata、Remote Repository、GitHub Account設定の変更を許可しない。`docs/`以外の公開識別情報洗浄は、Phase 1-exのPreflight、Review、専用Handoff後に実施する。


<!-- SOURCE_END 34: docs/requirements/public_identity_and_naming_decision_20260721112925.md -->

---

<!-- SOURCE_BEGIN 35: docs/requirements/public_identity_and_personal_information_policy_20260720220216.md -->

### Source 35: `docs/requirements/public_identity_and_personal_information_policy_20260720220216.md`

- History Target: `docs/project/phases/phase_1/history/requirements/public_identity_and_personal_information_policy_20260720220216.md`
- Source SHA-512: `685888834d6cd6f2f7530961754afe5ea0d987f22a6ca939cc8cfc8233ac71e70a4c07620d7f49ce220ce8ea346140cc472817439fdbff4b4c6b1f4e94a3c7dc`
- Source Size: `3818` bytes

# 公開識別子・個人情報取扱方針

- 文書ID: `public_identity_and_personal_information_policy`
- 状態: `current`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. 決定

本Projectにおける第一者の公開識別子は、次の表記だけに統一する。

```text
Nazuna Research
```

Projectの作者、設計者、開発者、Maintainer、連絡主体、Copyright主体等を公開文書やMetadataへ記載する場合も、この表記を使用する。

## 2. 禁止する第一者情報

公開候補Artifactへ次を記録しない。

- 法的氏名、実名、旧名、別表記、音訳表記
- Local OSのAccount名
- Home Directoryを含む個人固有の絶対Path
- Local Hostname、端末名、Machine固有識別子
- 個人Email、電話番号、住所、生年月日
- Credential、API Key、Secret、Private Key、Cookie、Token
- Private Repository、非公開資料、Local Attachmentへの到達Path
- 実会話Log、RAG投入資料その他の個人Data

## 3. 適用対象

本方針は次へ適用する。

- `src/`、`tests/`、`scripts/`、`config/`
- Root Metadata、License、README、Release Artifact
- `docs/`以下の内部文書と公開文書
- Sample、Log、Evidence、Screenshot、Terminal出力
- Archive、Manifest、Git Commit Metadata、GitHub表示情報

公開前には、本文だけでなくFile名、Symlink、Archive内Path、画像Metadata、生成物も検査する。

## 4. 第三者情報

Model、Library、Protocol、Paper、Repository、License等に必要な第三者の正式な名称と帰属は削除しない。

`Nazuna Research`への統一は第一者の公開Identityに対する規則であり、第三者をProject作者として誤表示する規則ではない。

## 5. 架空値と禁止例

Privacy FilterやPath RedactionのTestに必要な架空値、または設計文書内の抽象化された禁止例は、実在人物・実環境へ結び付かない場合に限り保持できる。

架空値は`example`、`<MODEL_ROOT>`、`/path/to/...`等、架空であることが明確な表現を使う。

## 6. Local-only Artifact

次は公開Artifactへ含めない。

- `.venv/`
- `models` SymlinkとModel本体
- `*.gguf`
- Cache、Coverage Data、Bytecode
- `.DS_Store`
- `var/`以下のLocal Runtime Data

これらはLocal実行に必要でも、公開Source ArchiveやGit管理対象ではない。公開Archive作成時はIgnore設定だけに依存せず、収録Manifestを検査する。

## 7. Append-Onlyの例外

個人情報、Credential、Secret、公開不適切なLocal Pathを既存Docsで発見した場合、Privacy／Securityを優先し、既存Fileを直接削除または匿名化できる。

この処理はStrict Append-Onlyの例外である。次を残す。

- 実値を再掲しないScrub Report
- 対象範囲と検査方法
- 検査結果
- 歴史SnapshotがBitwise同一ではなくなった事実

削除した個人情報を履歴復元目的で新Docsへ再記録してはならない。

## 8. 公開前Gate

公開前に最低限、次を確認する。

1. 第一者表記が`Nazuna Research`へ統一されている
2. 個人固有Path、Hostname、連絡先、Credentialがない
3. `.venv`、Model、Cache、Local LogがArchiveへ入っていない
4. Sample LogとScreenshotが匿名化されている
5. Git Author／CommitterとGitHub Profileの公開範囲をユーザーが確認している
6. 第三者LicenseとAttributionが保持されている

Gitを将来開始する際は、公開前にGitのAuthor名とEmailを別途確認する。現在の本方針だけで外部Service設定を変更しない。

<!-- SOURCE_END 35: docs/requirements/public_identity_and_personal_information_policy_20260720220216.md -->

---

<!-- SOURCE_BEGIN 36: docs/requirements/public_identity_and_personal_information_policy_20260721111659.md -->

### Source 36: `docs/requirements/public_identity_and_personal_information_policy_20260721111659.md`

- History Target: `docs/project/phases/phase_1/history/requirements/public_identity_and_personal_information_policy_20260721111659.md`
- Source SHA-512: `aea826fffce1afb300b748026e4c87816c01ece699b30a10d0ad5f4b7c2482fa7b941bf479cf317056ecf9b4cc943061d00136df3f5d7b4fa2a0338307cf4b1e`
- Source Size: `8707` bytes

# 公開識別子・個人情報取扱方針

- 文書ID: `public_identity_and_personal_information_policy`
- 状態: `current`
- 作成日時: `2026-07-21 11:16:59 JST`
- 更新日時: `2026-07-21 11:16:59 JST`
- Snapshot: `20260721111659`
- 作成担当: 設計者役担当Task
- 決定者: ユーザー
- 正本言語: 日本語
- supersedes: `public_identity_and_personal_information_policy_20260720220216.md`

## 1. 決定

本Projectにおける第一者の公開上の作者名、研究名義、Maintainer表示名、研究主体名、Copyright表示名には、原則として次を使用する。

```text
Nazuna Research
```

今後新規作成するSource、Docs、Metadata、公開Artifact、UI表示、Release情報では、特段の技術的・歴史的理由により別名義を使う必要がある場合を除き、`Nazuna Research`へ統一する。

廃止済み第一者名義は、一般的な作者表示名として使用しない。

## 2. Public Repository Identity

```text
Organization／Repository Owner : margpa-labs
Public Author／Research Name    : Nazuna Research
Public Repository              : margpa-labs/margpa-runtime-llm
Repository URL                 : https://github.com/margpa-labs/margpa-runtime-llm
```

GitHub Owner、Repository URL、Clone URL、Badge、Workflow参照、Package Metadata等では、役割に応じて`margpa-labs`または上記Repository URLを使用する。

`margpa-labs`はRepository Namespaceであり、作者表示名`Nazuna Research`とは役割を分ける。

## 3. 名義例外の判断権限

第一者名義はすべて`Nazuna Research`へ統一する。別の第一者名義または識別子をDocsへ記録する必要性は、設計者役Taskだけが判断できる。現時点で承認済み例外はない。

- 実在するGitHub Account Handleを正確に示す必要がある。
- GitHub提供のnoreply Commit Email等、Account Handleを含む技術識別子を使用する。
- Commit、Tag、Release、Audit Evidenceの出所を正確に示す必要がある。
- 既存ArtifactのAuthor Metadata、Hash対象、過去VersionのProvenanceを改変できない。
- 第三者Service上の既存識別子として変更不能である。
- 移行規則内で旧名義を検索・分類するため、文字列そのものを例示する必要がある。

例外を使用する場合は、単なる慣習や置換漏れではなく、保持理由を説明可能にする。

意味上必要か不明な箇所は自動置換せず、`manual_review`として判断待ちにする。

## 4. 表示名と技術識別子の分離

次を同一視しない。

```text
Display Author Name : Nazuna Research
Repository Owner    : margpa-labs
GitHub Account      : 必要時のみ実在Account Handle
Commit Name         : Nazuna Research
Commit Email        : 別途選択する技術識別子
```

Commitから個人GitHub Accountへ辿れることは、ユーザー判断により許容する。

ただし、Commit Nameは`Nazuna Research`を使用し、個人の実Emailを公開する必要はない。GitHub noreply Email等を使用する場合、そのAccount Handleが技術識別子として表示されることを許容する。

GitHubはCommit Emailを用いてCommitをAccountへ関連付けるため、表示名変更だけではAccount帰属は変わらない。この挙動は本Projectでは既知かつ許容されたものとして扱う。

## 5. Naming Application Matrix

| 対象 | 使用する値 | 備考 |
|---|---|---|
| 作者／研究主体／Maintainer表示 | `Nazuna Research` | 原則固定 |
| Copyright主体表示 | `Nazuna Research` | 法的確認が必要な場合は別途Review |
| Citation Author | `Nazuna Research` | CFF Entity Nameとして記録 |
| Git Commit Author Name | `Nazuna Research` | Emailとは分離 |
| GitHub Organization／Owner | `margpa-labs` | Repository Namespace |
| Repository URL | `https://github.com/margpa-labs/margpa-runtime-llm` | 公開正本 |
| GitHub Account Handle | 実在値 | 技術上必要な場合だけ |
| Project通称 | `Nazuna Research Governance LLM` | 固定 |
| 第三者Author／Organization | 第三者の正式名 | 変更禁止 |

## 6. 禁止する第一者情報

公開候補Artifactへ次を記録しない。

- 法的氏名、実名、旧名、別表記、音訳表記
- Local OSのAccount名
- Home Directoryを含む個人固有の絶対Path
- Local Hostname、端末名、Machine固有識別子
- 個人Email、電話番号、住所、生年月日
- LinkedIn、職務経歴書、個人用Profile、個人連絡先への不要な参照
- Credential、API Key、Secret、Private Key、Cookie、Token
- Private Repository、非公開資料、Local Attachmentへの到達Path
- 実会話Log、RAG投入資料その他の個人Data

CommitからGitHub Accountへ辿れることを許容する決定は、上記の個人情報をSourceやDocsへ積極的に掲載する許可ではない。

## 7. 適用対象

本方針は次へ適用する。

- `src/`、`tests/`、`scripts/`、`config/`
- Root Metadata、License、README、Release Artifact
- `docs/`以下の内部文書と公開文書
- Sample、Log、Evidence、Screenshot、Terminal出力
- Archive、Manifest、Git Commit／Tag Metadata、GitHub表示情報
- `CITATION.cff`、`NOTICE.md`、`CODEOWNERS`
- Workflow、Badge、Package Metadata、生成物

公開前には本文だけでなく、File名、Symlink、Archive内Path、画像Metadata、Binary、生成物も検査する。

## 8. 第三者情報と不変Evidence

Model、Library、Protocol、Paper、Repository、License等に必要な第三者の正式な名称と帰属は削除または変更しない。

次へ一括置換を行わない。

- 第三者Author／Maintainer
- Upstream Repository ID
- Model ID／Revision
- License本文
- Citation
- Hash／Digest
- 署名対象
- 過去Logの真正性を示すEvidence

洗浄によりArtifact内容が変化した場合は、旧Digest内の文字列を置換せず、公開用Artifactから新しいDigestを再計算する。

## 9. Historical Docs／Artifact

本書以前のDocsに旧名義が含まれることは、直ちに当該Docsを破壊的に書き換える許可にならない。

Phase 1-exで次を分類する。

```text
Current Public-facing Source : Nazuna Researchへ変更
Historical Internal Record   : 原本保持または非公開
Public Historical Evidence   : 匿名化版／再生成版を別Artifact化
Immutable Provenance         : 変更せず理由を記録
Manual Review                : 判断待ち
```

公開用Repositoryは洗浄済みExportを優先し、内部の原本や既存開発履歴を直接破壊しない。

## 10. Local-only Artifact

次は公開Artifactへ含めない。

- `.venv/`
- `models` SymlinkとModel本体
- `*.gguf`
- Cache、Coverage Data、Bytecode
- `.DS_Store`
- `var/`以下のLocal Runtime Data

公開ArchiveやGit TreeはIgnore設定だけに依存せず、収録Manifestと実体を検査する。

## 11. Append-Onlyの例外

個人情報、Credential、Secret、公開不適切なLocal Pathを既存Docsで発見した場合、Privacy／Securityを優先し、既存Fileを直接削除または匿名化できる。

この処理はStrict Append-Onlyの例外である。次を残す。

- 実値を再掲しないScrub Report
- 対象範囲と検査方法
- 検査結果
- 歴史SnapshotがBitwise同一ではなくなった事実

削除した個人情報を履歴復元目的で新Docsへ再記録してはならない。

## 12. 公開前Gate

公開前に最低限、次を確認する。

1. 第一者の表示名が`Nazuna Research`へ統一されている。
2. Repository NamespaceとURLが`margpa-labs/margpa-runtime-llm`を指す。
3. 廃止済み第一者名義が公開候補Artifactに残っていない。
4. 個人固有Path、Hostname、連絡先、Credentialがない。
5. `.venv`、Model、Cache、Local Logが公開Treeへ入っていない。
6. Sample LogとScreenshotが匿名化されている。
7. Git Author Nameが`Nazuna Research`である。
8. Commit Account帰属をユーザーが許容した現在決定と整合する。
9. 第三者LicenseとAttributionが保持されている。
10. 洗浄後ArtifactのDigestが再計算されている。

## 13. Authorization Boundary

本書は今後使用する名義と公開識別情報の正本規則である。

本書だけでは既存Fileの一括置換、既存Docsの削除、Git設定変更、Git初期化、履歴書換え、公開RepositoryへのPushを許可しない。これらはPhase 1-exのPreflight、Review、個別Handoff、ユーザー承認後に実施する。

<!-- SOURCE_END 36: docs/requirements/public_identity_and_personal_information_policy_20260721111659.md -->

---

<!-- SOURCE_BEGIN 37: docs/requirements/simple_rag_documentation_availability_requirements_20260725201016.md -->

### Source 37: `docs/requirements/simple_rag_documentation_availability_requirements_20260725201016.md`

- History Target: `docs/project/phases/phase_1/history/requirements/simple_rag_documentation_availability_requirements_20260725201016.md`
- Source SHA-512: `41a560541c8f51b2613a1e5f87655ac7e520f67684d5c3da54b9ea303af3c670df50f84350969bfc5dada0da8791a093f333898933716b14cc0208815f938e1e`
- Source Size: `3581` bytes

# Simple RAG Documentation Availability 要件定義

- 文書ID: `simple_rag_documentation_availability_requirements`
- 状態: `accepted_reservation`
- 作成日時: `2026-07-25 20:10:16 JST`
- 更新日時: `2026-07-25 20:10:16 JST`
- Snapshot: `20260725201016`
- 作成担当: 設計者役担当Task
- Decision Owner: ユーザー
- 正本言語: 日本語
- supersedes: なし

## 1. Purpose

Phase 1-ex後に追加するSimple RAG／Project Documentation Explainerについて、Mac実機とLightningのどちらでも、参照対象の`docs/`が設置されていない状態を明示的かつ安全に処理する。

## 2. Common Contract

Deployment先にかかわらず、次を共通Contractとする。

```text
Component OFF:
  docs/を探索しない。
  CorpusをLoadしない。
  Errorを発生させない。

Component ON／明示利用:
  docs/存在確認を行う。
  docs/が存在しない場合はUnavailable Resultを返す。
  ModelへProject説明を推測させない。
  Application全体をCrashさせない。
```

## 3. Missing Docs Result

最低限、次の構造化情報を返せること。

```text
component   : project_documentation_explainer
state       : unavailable
reason_code : docs_directory_missing
retryable   : true
```

日本語表示：

```text
docs/が設置されていないため参照できません。
```

英語表示：

```text
The docs/ directory is not installed, so it cannot be referenced.
```

表示文言だけに依存せず、UI／CLI／APIが同じ`reason_code`を解釈できること。

## 4. Behavioral Requirements

- `docs/`不存在を空の検索結果、回答不能、Model Failureまたは内部Server Errorへ偽装しない。
- `docs/`不存在時に、Modelの一般知識だけでProject説明を生成しない。
- Corpus未構築、Manifest不存在、読取権限不足、破損、空Corpusは、必要に応じて別Reason Codeとして区別する。
- Error MessageへAbsolute Local Path、利用者名またはSecretを露出しない。
- Audit／StatusへLogical Component名、Reason Code、発生段階を記録可能にする。
- `docs/`を自動Downloadまたは外部から自動取得しない。
- Missing状態から`docs/`を配置した後、明示的Reloadまたは再試行で回復可能にする。

## 5. Mac Local

Mac LocalではPhase 1-ex後にSimple RAG本体を接続できる。

```text
enabled = false  # default candidate
```

利用者がONにした時だけ`docs/`、Corpus ManifestおよびRetrieverを確認する。`docs/`がなければ共通Unavailable Resultを返す。

## 6. Lightning

Lightningでは当面Hook-only／Default OFFとする。

```text
enabled             : false
provider             : absent allowed
docs probe           : none
index load           : none
retrieval            : none
additional model call: none
```

OFF時に`docs/`が存在しなくてもStartup Failureとしない。将来ONにした状態で`docs/`またはProviderが不足する場合は、共通Unavailable Contractに従う。

## 7. Test Requirements

- OFF＋`docs/`不存在：正常起動、探索なし
- ON＋`docs/`不存在：`docs_directory_missing`
- ON＋`docs/`存在：Availability Gate通過
- Missing時：Model Callなし
- Missing時：Index Loadなし
- Missing時：Absolute Path非露出
- 日本語／英語Message
- Missingから配置後の明示的Retry
- Mac／LightningでReason Code一致

## 8. Scope and Authorization

本要件はAccepted Reservationである。Phase 1-ex完了前のRAG実装を許可しない。


<!-- SOURCE_END 37: docs/requirements/simple_rag_documentation_availability_requirements_20260725201016.md -->

---

<!-- SOURCE_BEGIN 38: docs/requirements/task_role_write_authority_policy_20260719142558.md -->

### Source 38: `docs/requirements/task_role_write_authority_policy_20260719142558.md`

- History Target: `docs/project/phases/phase_1/history/requirements/task_role_write_authority_policy_20260719142558.md`
- Source SHA-512: `0f29b1437ea871004b3617b2ae54d243bab5d42f693e2cadcf053d5022258b0296b4ff13b89388f2c7730539ae84d66a3c1cf5bc513811d5277f5828b78da7af`
- Source Size: `9548` bytes

# 担当Task別Write／Read Authority Policy

- 文書ID: `task_role_write_authority_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- Snapshot: `20260719142558`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 設計者役、実装者役、対外Docs作成者役、将来担当Task
- 正本言語: 日本語
- Documentation Rules: [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md)
- Backup Policy: [phase_completion_backup_policy_20260719142558.md](../history/operations/phase_completion_backup_policy_20260719142558.md)
- supersedes: なし（新規Authority Policy系列）

## 1. 目的

本Policyは、担当TaskごとのStanding Write Scope、Read-only Scope、Phase固有のConditional ScopeおよびHandoffのOwnershipを定義する。

目的：

- 設計と実装の分離
- 正本Docsの保護
- 実装担当の明確な作業範囲
- Review時の独立性
- 対外Docsと内部正本の分離
- 不要な権限拡大の防止
- Task間Handoffの再現性

## 2. Authorityの性質

本PolicyはProject運用上のWrite Authorityであり、OS／Filesystem上の技術的Permissionと同一ではない。

- Userが最終Authorityを持つ
- Userの明示的な個別指示は本PolicyのStanding Scopeを限定的に拡張・縮小できる
- 引き継ぎやRead依頼はWrite Authorityを意味しない
- 技術的にWrite可能でも、Policy上のAuthorityがなければ書き込まない
- Userの個別許可は対象、期間、Phase、File Scopeを越えて一般化しない

## 3. Scopeの3分類

### Standing Write Scope

役割に通常付与されるWrite範囲。

### Conditional Write Scope

Accepted HandoffとUserの実装／作業許可で、Phaseごとに一時的に追加されるWrite範囲。

### Read-only Scope

参照／Review／Testはできるが、既存Contentの修正・上書き・削除はできない範囲。

## 4. 設計者役担当Task

### 4.1 Standing Write Scope

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/                     # 内部User Manualの現行Owner
docs/documentation_index_*
docs/handoffs/common_*
docs/handoffs/designer_*
```

次のHandoffはFile Prefixが異なっても、開始指示として設計者役が作成できる。

```text
docs/handoffs/implementer_handoff_*
docs/handoffs/public_documentation_handoff_*
将来の担当開始用Handoff
```

### 4.2 Owned Document Types

- Requirements
- Architecture
- Governance正本
- ADR
- Roadmap
- Documentation Rules
- Role Authority Policy
- Operations Policy
- Phase Completion／Snapshot Record
- Documentation Index
- Designer Review／Final Review
- Common Handoff
- Designer Handoff
- 各担当の開始用Handoff
- 内部User Manual

### 4.3 Review Authority

設計者役は、実装者役のStatusとSource／Config／TestをRead-onlyでIndependent Reviewする。

可能な操作：

- Source／Config／Test参照
- Static Test／Unit Test／Integration Test実行
- Native Runtime検証
- Hash／Manifest／Link検証
- Finding／Acceptance判定
- `designer_review_*`作成
- Reviewと同時の新Documentation Index作成

Review依頼はSource／Config／TestのFix実装を意味しない。Findingがある場合はReviewへ記録し、実装担当へFollow-upを返す。

### 4.4 Read-only Scope

```text
src/
tests/
scripts/
config/
pyproject.toml
uv.lock
README等の対外Docs担当Owner領域
docs/handoffs/implementer_status_*
docs/handoffs/external_docs_status_*
```

設計者役が実装を兼務する場合は、UserがそのTaskに対して実装範囲を明示的に許可する。

## 5. 実装者役担当Task

### 5.1 Standing Write Scope

```text
src/
tests/
scripts/
docs/handoffs/implementer_status_*
```

### 5.2 Conditional Write Scope

次はStanding Scopeではない。Accepted Designer Handoffが対象Pathを明記し、Userが当該Phaseの実装開始を許可した場合だけWriteできる。

```text
config/
pyproject.toml
uv.lock
ルートのBuild／Runtime設定
Migration File
Phase固有Asset
新規Directory
```

Handoffに書かれていないFileへのWriteが必要になった場合は、独断でScopeを広げず設計者／Userへ返す。

### 5.3 Status Ownership

実装者役は、実装またはFollow-upごとに新TimestampのStatusを作成する。

```text
docs/handoffs/implementer_status_<topic>_YYYYMMDDHHMMSS.md
```

Statusには次を含める。

- Authorization／Scope
- Changed／Added File
- Implementation Summary
- Test Command／Result
- Native Verification
- Hash／Dependency／Schema変更
- Known Limitation
- Acceptance Criteria対応
- Review依頼

実装者役は`designer_review_*`または`documentation_index_*`を作成しない。

### 5.4 Read-only Scope

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/
docs/documentation_index_*
docs/handoffs/common_*
docs/handoffs/designer_*
その他のCanonical Docs
```

要件・Architecture・Governance／ADR正本に問題を発見しても直接修正しない。Statusへ記録し、設計者役へ返す。

## 6. 対外Docs作成者役担当Task

### 6.1 Standing Write Scope

```text
README*
docs/public/                         # 将来のPublic Docs候補
docs/handoffs/external_docs_status_*
```

License、Security Policy、Contribution Policyまたは法的表記の変更は、Userの明示的な個別許可を必要とする。

### 6.2 Read-only Scope

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/
docs/documentation_index_*
src/
tests/
config/
```

対外DocsはCanonical Docsを参照して作成する。Canonicalな要件・Architecture・Governanceの内容を直接変更しない。

### 6.3 Status Ownership

```text
docs/handoffs/external_docs_status_<topic>_YYYYMMDDHHMMSS.md
```

対外Docs作成者役は、正本とPublic Docsの矛盾をStatusへ記録し、設計者／Userへ返す。

## 7. `docs/operations/` Ownership

Standing Owner：

```text
設計者役担当Task
```

対象：

- Phase Completion Backup Policy
- Snapshot Record
- Restore Policy／Restore Result
- Release／Milestone Operations
- Backup Naming／Retention
- Operationsの人間向け記録

External Archive、Manifest／Receiptの実ファイル生成は`docs/operations/`のWrite Authorityに自動的に含まれない。Project外WriteまたはBackup Operatorの許可を別途必要とする。

## 8. Documentation Index Ownership

`documentation_index_*`のStanding Ownerは設計者役とする。

新Indexを作成する主なTiming：

- Requirements／Architecture／Governance／ADR更新
- Designer Handoff更新
- Designer Review完了
- Phase／Milestone Status更新
- Common Rule／Operations Policy更新
- Current／Historical Setの変更

実装者Statusの作成時は、実装者がIndexを作らず、設計者Review時にReviewとIndexをセットで作成する。

## 9. Handoff／Review Naming Ownership

| Prefix／Type | Standing Owner |
|---|---|
| `common_project_handoff_*` | 設計者 |
| `designer_handoff_*` | 設計者 |
| `designer_review_*` | 設計者 |
| `implementer_handoff_*` | 設計者（開始指示） |
| `implementer_status_*` | 実装者 |
| `public_documentation_handoff_*` | 設計者（開始指示） |
| `external_docs_status_*` | 対外Docs作成者 |

Follow-upでも過去Fileを上書きせず、新Timestampを使用する。

## 10. Operational Validation Status

### 設計者役／実装者役

現在の設計者役と実装者役の分業は、Phase 1-A／1-B／1-C／1-Dの実装、Status、Review、Follow-up、Final Acceptanceで実運用された。

また、Phase 1-EでRequirements／Architecture／ADR／Formal Handoffを設計者が作成し、実装者が実装を担当する流れが継続している。

現時点の評価：

```text
設計者役／実装者役の分業は、実運用上有効に機能している。
```

今後も当面の間、本Authority構造をCurrent Policyとする。

### 対外Docs作成者役

対外Docs作成者役はTask作成済みだが、現時点で実作業による十分な運用検証は完了していない。

そのため、対外Docs役のAuthorityは暂定的に正式化するが、実運用後に必要に応じて後継Policyで調整できる。

## 11. Conflict／Escalation

次の場合は作業を独断で続けず、User／Ownerへ返す。

- 複数役割が同じFileを同時変更する
- Standing Scope外のWriteが必要
- Canonical Docsと実装が矛盾
- HandoffとUser Instructionが矛盾
- Current Indexが不明
- 既存File上書きが必要に見える
- Secret／Personal Data／External Credentialが関係
- 破壊的操作が必要

## 12. Prohibited Actions

- 担当外のCanonical Fileを勝手に変更しない
- Read依頼をWrite許可と解釈しない
- Review依頼をFix許可と解釈しない
- 古いDocs／Handoff／Status／Reviewを上書きしない
- Userの一回限りの許可をStanding Authorityに変換しない
- 実装者が設計Decisionを黙って変更しない
- 設計者がIndependent Review中に黙ってSource Fixしない
- 対外Docs役がCanonical要件をPublic向けに黙って改変しない

## 13. Policy Change

本Policyを変更する場合は既存Fileを編集せず、新Timestampの後継Policyと最新Documentation Indexを作成する。


<!-- SOURCE_END 38: docs/requirements/task_role_write_authority_policy_20260719142558.md -->

---

