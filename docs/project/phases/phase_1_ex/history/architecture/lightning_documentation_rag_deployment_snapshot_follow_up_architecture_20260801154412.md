# Lightning Documentation RAG Deployment Snapshot Follow-up Architecture

```yaml
document_id: lightning_documentation_rag_deployment_snapshot_follow_up_architecture
phase: phase_1_ex
status: accepted_from_manual_recovery
language: ja
created_at: 2026-08-01 15:44:12 JST
owner: 設計統括者役
```

## 1. Context

Lightning Public Corpus Documentation RAG Multi-access実装後、公開8文書、最新差分SourceおよびProfileを配置し、Basic／Public Preflightは合格したが、両SurfaceのForeground起動が失敗した。

原因はRAG機能自体、Model、Corpus、CredentialまたはPortではなく、Lightning Runtime Treeが複数時点のArtifactを混在させていたことである。

## 2. Failure Chain

```text
Preflight:
  pass

Application import:
  missing pre-existing Mac RAG adapter module

Partial source repair:
  web／conversation contract version mismatch

Test collection:
  old web contracts cannot export current RAG snapshot

Profile tests:
  old／incomplete config set causes invalid configuration

Lifecycle tests:
  uploaded shell executable mode lost
```

PreflightはHost、Path、Profile、Corpus、CredentialおよびAccess Contractを確認したが、Application Module Graph全体のImport可能性を検証していなかった。したがってPreflight合格とApplication起動可能性は同一ではない。

## 3. Corrected Deployment Topology

```text
Local accepted runtime snapshot
  ├─ src
  ├─ config
  ├─ scripts
  ├─ tests
  ├─ pyproject.toml
  ├─ uv.lock
  └─ .python-version
       ↓ coherent synchronization
Lightning project runtime
       ↓ permission restoration
Import smoke
       ↓
Profile／corpus preflight
       ↓
Focused tests
       ↓
Basic Preview／Public Demo startup
       ↓
RAG OFF／ON manual acceptance
```

公開DocsはRuntime Snapshotと混在させず、公開8文書Allowlistとして独立して配置する。Model、`.venv`、Managed Secrets、Private Bootstrap、API BuilderおよびURLは別Lifecycleのまま維持する。

## 4. Accepted Runtime Boundary

```text
Mac Local:
  local documentation profile
  accepted

Lightning Basic Preview:
  basic authentication
  explicit public 8-doc profile
  accepted through traffic-aware auto-start

Lightning Public Demo:
  authentication none
  explicit public 8-doc profile
  accepted through manual foreground and auto-start
```

Basic PreviewとPublic Demoは同じ公開Corpus Contractを利用するが、Access Profile、AuthenticationおよびProcess Lifecycleを共有しない。Public DemoはBasic Credentialを読み取らない。

## 5. Future Preflight Improvement

次の追加を後続候補とする。

- Application Entry Point Import Smoke
- Feature Contract Import Smoke
- Runtime Deployment ManifestとBaseline Digest
- Source／Config／Script／Test Snapshot Version整合性
- Script Executable Mode検証
- Optional Static Asset Syntax検証

これらは今回の機能Acceptanceを妨げない。実装する場合も、Model Load、Network、外部Platform操作またはPersistent IndexをPreflightへ混入させない。

## 6. Deployment Strategy Decision

Verified同一Baselineに対する小さな修正は差分Deploymentを許容する。一方、複数Subphaseの差、横断Layer追加またはBaseline不明がある場合は、個別File追跡よりCoherent Runtime Deployment Snapshotを高優先度とする。

これは再構築Costと調査Costの比較に基づく運用選択であり、無差別な全Artifact上書き規則ではない。
