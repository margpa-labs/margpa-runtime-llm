# Phase 6 Dependency Acquisition Authority Receipt

```yaml
document_id: phase_6_dependency_acquisition_authority_receipt_20260822220804
status: accepted_active
phase: phase_6
recorded_at: 2026-08-22 22:08:04 JST
from: ユーザー／プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役
user_start: declared
automation_control_state: ON
implementation_authorized: true_within_frozen_phase_6_scope
dependency_network_authorized: true_scoped
git_mutation: not_authorized
model_download: not_authorized
```

## 1. Authority Decision

Userは、Accepted Phase 6 Work Unitに直接必要なPython依存を、Official PyPIからProject-local仮想環境へ取得・導入する限定Network Authorityを明示的に承認した。

既存のNetwork禁止は全面解除しない。本Receipt記載のDependency AcquisitionだけをExact Exceptionとし、Model Download、AWS、External Service、Credential、GitまたはPhase Scope拡張へ流用しない。

本Authority内の通常Dependency解決、Install、Validation、局所ReworkおよびEvidence作成について、ClaudeはUserへMicro-confirmationを返さず自律処理する。

## 2. Current Trigger／Reclassification

Claude ReportとCurrent Recovery Entryにより、P6-A-WU-001は完了し、P6-A-WU-002で次のPython Package不足が検出された。

```text
Initial Direct Packages : transformers／sentencepiece／gguf
Target Tool             : convert_hf_to_gguf.py
Current Classification : AUTHORITY WAIT RESOLVED BY THIS RECEIPT
Resolution Route        : ROLE_OWNED_CURRENT
```

`phase_6_a_wu001_toolchain_blocked_deferral_ja_20260822215600.md`のNetwork Authority待ちは本Receiptにより再活性化する。Phase 6-Aを未解決のままFinal Completionへ送らず、Current Diffを破壊しない形でP6-A-WU-002へ復帰する。

Phase 6-Bに既に着手済みのSource／Testがある場合、それを削除、Resetまたは捏造せずCurrent Stateとして照合する。安全な境界まで整合させた後、Phase 6-AのToolchain／Conversionを優先的に再開する。

## 3. Authorized Dependency Acquisition

### 3.1 Purpose

- DeepSeek Hugging Face Canonical SnapshotからGGUF Derived Artifactを作成するConversion Toolchain。
- Frozen Phase 6のJudge／Repair／Model-neutral Runtime／Validationに直接必要なPython依存。
- Accepted Work UnitのTest／Static／Buildを成立させる直接依存。

### 3.2 Install／Write Boundary

```text
Python Environment : margpa-runtime-llm/.venv/
Package Index      : Official PyPI
Initial Packages   : transformers／sentencepiece／gguf
Transitive Packages: Resolverが上記またはAccepted Phase 6 Direct Dependencyから導出したもの
Cache              : margpa-runtime-llm/.venv/.cache/**
Temporary          : margpa-runtime-llm/.venv/.tmp/**
Reproducibility    : pyproject.toml／uv.lockへ必要最小のDependency Group／Lock更新を許可
```

必要Packageは固定Listを機械的に増やさず、Current Converter、Python Version、PlatformおよびFrozen Work Unitから動的に選ぶ。新しい直接PackageがPhase 6 Acceptanceに必須なら、本Authority内で追加できる。ただしPackage名、必要理由、Version、取得元、Resolved Transitive Setおよび既存Dependencyへの影響をEvidence化する。

### 3.3 Network Boundary

- Official PyPIのMetadata／Wheel／Source Distribution／必要なBuild Dependency取得。
- 標準TLS検証を維持する。
- `--trusted-host`、TLS無効化、Credential埋込み、Private Index、Mirrorまたは任意URL Installを使用しない。
- PyPI以外のGit Repository、Release Asset、Model Hub、Cloud StorageまたはExternal APIへ拡張しない。

### 3.4 Execution Tool Boundary

既にAs-builtで特定された`/opt/homebrew/bin/convert_hf_to_gguf.py`は、Phase 6 DeepSeek Conversion目的のRead／Execute-only Toolとして利用できる。Homebrew Prefixの探索、Formula変更、`brew install／update／upgrade／uninstall`またはTool本体の変更は許可しない。実行前にToolのResolved Path、Version／Digest取得可能性およびRecipeをEvidence化する。

## 4. Required Procedure

Claude側設計統括者役は、Package単位のUser確認を行わず、最低限次を実施する。

1. Install前のPython Version、`.venv`、`pip／uv`、既存Package Setを記録する。
2. Project-local Cache／Temporary環境変数を設定し、意図的なHome／OS Temporary Writeを行わない。
3. Exact Direct Package、Resolved Version、Transitive Dependencyおよび取得元を記録する。
4. Blindな全Package Upgradeをせず、必要なDependencyだけを導入する。
5. `pyproject.toml／uv.lock`を変更する場合は、Conversion／Phase 6用Dependencyであることを分離し、Before／Afterを記録する。
6. Install後にImport、Converter Help／Recipe、Focused Testを確認する。
7. Existing Runtime Dependencyへの影響がある場合、Focused回帰とMaterial Boundary Full Validationを行う。
8. Package License、Yanked／Resolution Warning、Native Build、Install FailureおよびVersion ConflictをEvidence化する。
9. Dependency Cache／Temporary Artifactを無断削除しない。`.venv`全体を再作成しない。
10. P6-A-WU-002以降へ復帰し、Canonical Snapshotを変更せずDerived専用Subtreeへだけ書く。

## 5. Explicit Non-authority

次は本Receiptで許可しない。

- System Python、Global Site-packages、HomebrewまたはOS Package Managerの変更。
- `.venv`以外へのPython Package Install。
- Hugging Face／Model Repository／DeepSeek V4／Guard／Judge Model Download。
- `pip install`の任意URL、Git URL、Local Project外Path、Private RegistryまたはCredential利用。
- AWS、Lightning、一般公開、Secret、Login、課金操作。
- QwenまたはDeepSeek Canonical Snapshotの変更、削除、移動または上書き。
- Git Add／Commit／Push／Tag／Branch等のMutation。
- Phase 7以降、Stable正本、User実`runtime_data/`または未許可Rootへの権限拡張。
- Package導入失敗を理由とした既存`.venv`、Cache、Model、SourceまたはUser Dataの自動Cleanup。

## 6. Stop／Escalation Conditions

次の場合だけ停止する。

1. Official PyPI以外の取得元、Credential、課金またはLicense同意が必要。
2. System／Global／Homebrew Mutationが必要。
3. Accepted Phase 6 Scope外のPackage／機能追加でなければ成立しない。
4. Dependency ResolutionがCurrent Runtimeを破壊し、Frozen Acceptanceを維持できない。
5. Canonical Model Mutation、未許可Root WriteまたはIrreversible Data Migrationが必要。
6. Security／Integrity上の重大なPackage Findingがある。

通常のPackage不足、Resolver Conflict、Import Error、Version調整、Focused Test FailureまたはRecipe修正は、Frozen範囲内で自己解消する。`Unresolved`だけを理由にUserへ判断を返さない。

## 7. Six-document Recovery Set

Provider Quota／Auto-Compaction後は、次の6文書を全文再読する。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/phases/phase_6/phase_index_ja.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_claude_execution_handoff_ja.md`
4. `docs/project/phases/phase_6/history/operations/phase_6_exact_model_authority_receipt_ja_20260822212732.md`
5. `docs/project/phases/phase_6/history/operations/phase_6_activation_preflight_and_armed_receipt_ja_20260822212732.md`
6. `docs/project/phases/phase_6/history/operations/phase_6_dependency_acquisition_authority_receipt_ja_20260822220804.md`

その後、最新Phase 6 Recovery Entry、Current Diff、Test Evidence、Model／Disk StateおよびActive Work Unitを照合する。6文書再読だけでCurrent Source State確認を代替しない。

## 8. Current Authority Result

```text
User Start                    : PASS／DECLARED
Automation                    : ON
Phase 6 Implementation        : AUTHORIZED WITHIN FROZEN SCOPE
Dependency Network            : AUTHORIZED／SCOPED
Initial Direct Packages       : transformers／sentencepiece／gguf
Model Download                : PROHIBITED
System／Global／Homebrew Write : PROHIBITED
Git Mutation                  : PROHIBITED
P6-A Toolchain Authority Wait : RESOLVED
Next Route                    : RECOVER CURRENT DIFF → RETURN P6-A-WU-002
```

## 9. Operational Index Integrity

```text
66f582fcd5bb9cbdf8aea624ba67e915c9a7161d51273837d4360026459e6cf663fd862d5d9eb7578010fbcfe7dcceca726981917d249cb2cd237179b3d36401  docs/project/phases/phase_6/phase_index_ja.md
```

Frozen Core 7文書は変更していない。Phase IndexはUser Start、Automation `ON`、Current Work Unitおよび本Authorityを反映するOperational Stateとして更新し、Current Digestを本Receiptへ記録する。
