# Phase 1-ex Public Demo Minimal Access／Runtime Portability Review

```yaml
document_id: designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability
phase: phase_1_ex
status: changes_required
language: ja
created_at: 2026-07-30 16:11:08 JST
owner: 設計統括者役
reviewed_status: implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md
source_handoff: implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730144921.md
supersedes: null
lightning_external_operation: not_performed
```

## 1. Result

判定を分離する。

```text
Explicit Web Access Profile:
  ACCEPTED

Basic Preview Compatibility:
  NO REGRESSION FINDING

Model／Deployment／Access Separation:
  ACCEPTED

Public Demo Repository Implementation:
  CHANGES_REQUIRED

Lightning Public Demo Trial:
  NO_GO
```

Public Demoを`local`および`basic_preview`と別の明示Access Profileとして扱い、認証なしNon-loopback Bindを偶発的なAuth無効化から分離した点はAcceptedとする。

Public Documentation RAGは`denied`、Public専用Optional Controlは全て`off`、Model／Deployment／Access／Feature／Lifecycleは別設定境界として保持されている。

一方、Public Demo Foreground EntrypointがBasic Preview用Runtime Stateへ間接依存し、Credential除外もPreflight後であるため、Lightningへ投入できる状態とは判定しない。

Optional Control PortもRequest Pipelineへ未接続であり、将来実装Hookとしては不十分である。

## 2. Reviewed Sources

```text
docs/project/phases/phase_1_ex/adr/
  adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md

docs/project/phases/phase_1_ex/requirements/
  public_demo_minimal_access_and_runtime_portability_requirements_ja.md

docs/project/phases/phase_1_ex/architecture/
  public_demo_access_profile_and_runtime_portability_architecture_ja.md

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730144921.md
  implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md

src/margpa_runtime_llm/web/
  access_profiles.py
  auth.py
  app.py

src/margpa_runtime_llm/entrypoints/web/
  main.py

config/web_profiles/
  basic_preview.toml
  public_demo.toml

scripts/runtime/lightning/
  basic_preview_common.sh
  basic_preview_service.sh
  auto_start_preflight.sh
  public_demo_service.sh

tests/
  unit/web/test_access_profiles.py
  unit/web/test_auth.py
  unit/web/test_web_cli.py
  integration/web/test_web_app.py
  unit/runtime/test_lightning_basic_preview_service.py
```

## 3. Accepted Points

- `local`、`basic_preview`および`public_demo`を型とConfigで分離している。
- Local Auth DisabledだけでNon-loopback Publicへ移行できない。
- `basic_preview`はBasic認証必須の既存契約を維持している。
- `public_demo`は明示Profile選択時だけ認証なしNon-loopbackを許可する。
- Profile Key、Exposure Mode、Authentication、Non-loopback許可およびRAG Capabilityの矛盾をFail Closedで拒否する。
- Public DemoでDocumentation RAGを`denied`としている。
- Basic Preview／Localでは将来RAGを接続可能な`eligible`状態を保持している。
- Public専用Rate Limit、Budget、Cooldown、Token Cap、QuotaおよびCost Guardを全て`off`としている。
- Access ProfileへModel、Backend、OS、GPUまたはCloud Provider固有値を混入していない。
- Deployment Profile、Model Definition、Model Root、Model KeyおよびContext SizeをAccess Profileと独立してOverrideできる。
- Public Demoの最終Web ProcessはForeground `exec`であり、Public Script自身はPID／Logを生成しない。
- 既存UIをBasic認証専用表現からAccess Mode非依存のResearch Preview表現へ変更している。
- Public ResponseへCredential、内部Path、Stack TraceまたはRAG入口を追加していない。

## 4. Required Findings

### F1. Public DemoがBasic Preview用Runtime Stateへ依存する

Severity: High

`public_demo_service.sh`の`validate_public_demo`は`margpa_project_preflight`を呼ぶ。

共通Configuration ResolutionとPreflightは、Public Demoが使用しない次のBasic Preview Lifecycle Artifactを解決・検査する。

```text
.runtime-state/margpa-runtime-llm/basic-preview
basic-preview.pid
basic-preview.log
.margpa-basic-preview-state
.margpa-runtime-llm-basic-preview.lifecycle.lock
```

Public Scriptはこれらを生成しないが、既存Directory、Marker、Lock、PermissionおよびWritable Ancestorへ依存する。

LightningではStudio Sleep／Restart後にRuntime State DirectoryのModeが変化する事象を既に観測している。このため、Basic Preview側の状態不整合だけで匿名Public Demoの`preflight／run`が起動前に失敗し得る。

これは次のContractと一致しない。

```text
Public Demo:
  Foreground
  Stateless Lifecycle
  Background PID／Log／Lock／Runtime Stateなし
  Basic Preview Lifecycleから分離
```

Required：

- Public Demo用Stateless Preflight経路を設ける。
- Project、Platform、Python、uv、Web Entrypoint、Deployment Profile、Model Definition、Model Artifact、Bind、Public Access Profile、RAG拒否およびOptional Control `off`の検査は維持する。
- Runtime State Root、PID、Log、Ownership MarkerおよびLifecycle Lockを解決・検査・作成・変更しない。
- `MARGPA_RUNTIME_STATE_ROOT`の値や既存Basic Preview StateのPermission不整合がPublic Demoへ影響しない。
- 共通処理を分離する場合も、Basic Preview Lifecycle側の安全検査を弱化しない。

### F2. Basic Credential除外がPreflight後である

Severity: High

`public_demo_service.sh`は最終的な`exec margpa-web`時だけ、次のEnvironment変数を除外する。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

その前の`margpa_project_preflight`はPython、uvその他の子Processを起動する。通常のProcess Environment継承により、Basic Preview用Managed SecretsがPublic Demo Preflightの子Processへ渡る。

最終Web Processでは除外されるため既存Testは合格するが、実装Statusに記載された「引数にも子Processにも渡さない」というContractは満たしていない。

Required：

- Public Scriptが最初の子Processを起動する前に、Credential三項目をEnvironmentから除外する。
- Common Script読込時に子Processが起動し得る構造なら、その前に除外する。
- 除外はPublic Script Process内だけで行い、親Terminal、Managed SecretsまたはBasic Preview側を変更しない。
- `preflight`と`run`の全子Processで三項目が不在であることをTestする。
- Credential値をArgument、Output、Log、Error、Test ArtifactまたはStatusへ出さない。

### F3. Optional Control PortがRequest Pipelineへ接続されていない

Severity: Moderate

`PublicControlPolicyPort`と`DisabledPublicControlPolicy`は存在するが、Composition Rootで生成したPolicyを`app.state`へ保存するだけである。

`create_web_app`と`/api/v1/chat/stream`はPolicyを受け取らず、次を呼び出さない。

```text
check_request
before_generation
observe_generation
after_generation
```

現在は全項目`off`のため生成結果への実害はない。しかし将来Rate Limit等を追加するときにWeb Routeを再設計する必要があり、「差し替え可能なHookを設置済み」とは扱えない。

Required：

- `PublicControlPolicyPort`をWeb ApplicationへInterface経由で注入する。
- Chat Request／Generation LifecycleからDisabled Policyも呼び出す。
- `after_generation`をCompleted、CancelledおよびErrorを含むTerminal Pathで一貫して扱う。
- Disabled PolicyではResponse、Streaming、Cancel、Summaryおよび既存UI挙動を変更しない。
- Spy／Recording PolicyによりPipeline呼出をTestする。
- 実際のRate Limit、Budget、Quota、PersistenceまたはCost計算は追加しない。

## 5. Verification

設計統括者役が実行したRead-only検証：

```text
SHA-512:
  Implementer Status記載の16 Fileと現在値が16／16一致

Ruff Check:
  PASS

Ruff Format Check:
  PASS／93 files

Mypy:
  PASS／93 source files

Shell Syntax:
  PASS
```

実装Statusに記録された検証Evidence：

```text
Targeted Test:
  80 passed

Repository Full Suite:
  319 passed
  3 deselected

Ruff／Mypy／Shell:
  PASS
```

本ReviewではProject外Temporary ArtifactまたはProject内Test Cacheを新規作成しないため、Pytestを再実行していない。Status記載時点と現在FileのSHA-512が一致するため、上記Test Evidenceの対象SourceにDriftはない。

Model Smoke、Lightning External Trial、API Builder変更、Port変更、Public URL発行および匿名公開は実行していない。

## 6. Gate

現時点のGate：

```text
Basic Preview:
  KEEP

Mac Local Runtime:
  KEEP

Public Demo Repository:
  CHANGES_REQUIRED

Lightning Public Demo Upload／Run:
  BLOCKED

Anonymous Public Access:
  BLOCKED
```

F1およびF2はLightning投入前のBlockerである。

F3は現時点の生成結果を壊す不具合ではないが、ユーザーが要求した将来制限Hookを成立させるため、同一Follow-upで解消する。

次は、[Public Demo Stateless Preflight／Credential Isolation／Policy Hook Follow-up Handoff](implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730161108.md)に限定して実装担当へ戻す。

実装担当Statusと再ReviewがAcceptedになるまで、ユーザーによるLightning Public Demo作業へ進まない。

## 7. Mutation／External Boundary

本Reviewでは次を行っていない。

- Source、Config、ScriptまたはTestの変更
- 既存Docsの上書き
- Project Root外の読取・変更
- Model Access
- Lightning操作
- Git／GitHub操作
- External Service変更

追加したのは、本Review、Follow-up HandoffおよびAppend-only Documentation Index Snapshotだけである。
