# Runtime Deployment Snapshot運用方針

```yaml
document_id: runtime_deployment_snapshot_policy
document_state: current
language: ja
created_at: 2026-08-01 15:44:12 JST
updated_at: 2026-08-01 15:44:12 JST
owner: 設計統括者役
scope: cross_environment_runtime_deployment
```

## 1. Purpose

Local、Home Server、Lightning、Cloudその他の外部RuntimeへProjectを反映する際、異なる開発時点のSource、Config、ScriptおよびTestが混在することを防ぐ。

実装担当Statusの変更File一覧は、記録されたBaselineに対する差分である。対象環境がそのBaselineと一致することを証明できない場合、変更File一覧をそのままDeployment Manifestとして扱ってはならない。

## 2. Core Rule

次のいずれかに該当する場合、個別差分よりも同一時点のRuntime Deployment Snapshot同期を優先する。優先度は高い。

- 対象環境が複数Subphaseまたは複数Follow-up分遅れている。
- 新機能が既存の複数Layerへ接続され、Transitive Dependencyが変更File一覧だけでは閉じない。
- Git Commit、Release Artifactまたは完全Deployment ManifestによるBaseline一致証明がない。
- Import Error、Contract Import不一致、Config Schema不一致またはTest Collection Errorが連鎖する。
- 一つずつFileを交換する調査Costが、同一Snapshotの再配備Costを上回る。
- 対象環境が一時的・再構築可能で、完全同期の影響範囲が明確である。

```text
Verified identical baseline:
  bounded delta deployment may be used

Baseline unknown／multiple phases behind／dependency chain changed:
  coherent runtime snapshot deployment preferred
```

「常に全Directoryを入れ替える」ことを固定規則にはしない。Model、巨大Artifact、`.venv`、Secret、Private Bootstrapまたは利用者Dataまで無条件に再配備する意味ではない。対象、Baseline、Cost、RollbackおよびEnvironment特性を確認してDeployment単位を選ぶ。

## 3. Coherent Runtime Deployment Unit

現行Python Runtimeの標準Deployment単位は次とする。

```text
src/
config/
scripts/
tests/
pyproject.toml
uv.lock
.python-version
```

Featureが公開Docsを必要とする場合は、許可済みCorpusだけを別の明示Manifestとして追加する。

標準除外：

```text
.venv/
models/
cache／temporary／log
__pycache__/
*.pyc
secret／credential
repository外private bootstrap source
allowlist外docs
local override
```

Model Artifact、`.venv`、Managed Secrets、API Builder、Port、URLおよびRepository外Private Bootstrapは、Runtime Source Snapshotと別のLifecycle／Authorityで扱う。

## 4. Deployment Sequence

1. Source Snapshotと対象EnvironmentのBaselineを識別する。
2. Deployment対象と除外対象を固定する。
3. 同一Snapshotの`src／config／scripts／tests`とMetadataを同期する。
4. Uploadで失われたExecutable Permissionを、対象Scriptに限定して復元する。
5. Application Entry Pointと新Feature ContractのImport Smokeを行う。
6. Config／Profile／Corpus Preflightを行う。
7. Focused Testを行う。
8. 必要に応じてFull Suiteを行う。
9. Manual ForegroundまたはPlatform-owned Foregroundで起動する。
10. Access、Lifecycle、Feature ON／OFFおよびRollback境界を確認する。

Import SmokeはPreflightの代替ではなく、PreflightもImport Smokeの代替ではない。

## 5. Permission Boundary

Web UploadまたはStudio Sleep／WakeによってExecutable Modeが変化する可能性がある。Permission修復は、Owner、Symlink、Pathおよび対象Fileを確認した後、明示されたScriptだけへ限定する。

Project Root外、Workspace全体、Home、Model Root、Environment Rootまたは広い親Directoryへ再帰的なPermission変更を行わない。

## 6. Verification Evidence

最低限、次を記録する。

- Deployment Snapshot識別子または作成時刻
- Source／Config／Script／Testの同期範囲
- 除外範囲
- Import Smoke結果
- Profile／Corpus Preflight結果
- Focused／Full Test結果
- Script Permission確認
- Manual Runtime結果
- Access Surface別のAcceptance
- Known Limitation
- Rollbackまたは再同期条件

## 7. Phase 1-ex Evidence

LightningへDocumentation RAG Multi-accessを反映した際、最新変更Fileだけを同期したため、Mac Documentation RAG導入時の既存依存Sourceが不足した。

観測例：

```text
ModuleNotFoundError:
  bm25_retriever

ImportError:
  DocumentationRagRuntimeSnapshot

Configuration Error:
  mixed RAG profile／contract versions

Permission Error:
  uploaded shell scripts not executable
```

同一時点の`src／config／scripts／tests`とMetadataへ同期し、Script Permissionを限定復元した後、Import Smoke、Focused Test、Basic Preview、Public DemoおよびDocumentation RAGが復旧した。

この事例により、Baseline不一致時のCoherent Runtime Deployment Snapshot優先を正式運用とする。

## 8. Non-authority

本方針は、Project Root外操作、外部Platform操作、Secret変更、Model変更、Git操作、広範な削除または既存研究Assetの上書きを自動承認しない。

Deploymentを実施する担当、対象Platform、対象PathおよびMutation Scopeは、各Handoffまたはユーザー指示で別途確定する。
