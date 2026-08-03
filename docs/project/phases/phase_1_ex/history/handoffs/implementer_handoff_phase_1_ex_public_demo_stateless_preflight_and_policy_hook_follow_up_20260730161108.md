# 実装担当向け Phase 1-ex Public Demo Stateless Preflight／Credential Isolation／Policy Hook Follow-up Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up
phase: phase_1_ex
status: accepted_ready_for_implementation
language: ja
created_at: 2026-07-30 16:11:08 JST
owner: 設計統括者役
target_role: 実装者役
source_review: designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730161108.md
source_status: implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md
supersedes: null
external_operation_owner: user
```

## 1. Objective

Accepted済みの明示Web Access Profile、Basic Preview互換性、Public Documentation RAG拒否およびRuntime交換性を維持したまま、Public Demoに残る三つのFindingだけを解消する。

```text
F1:
  Public DemoをBasic Preview Runtime Stateから完全分離

F2:
  Public Demoの全子ProcessからBasic Credentialを早期除外

F3:
  Disabled Optional Control Policyを実際のRequest Pipelineへ接続
```

実際のRate Limit、Cost Guard、Documentation RAG本体、Public Login、Agent、Toolまたは外部操作は追加しない。

## 2. Required Reading

次の順序でRead-only参照する。

1. `designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730161108.md`
2. `implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md`
3. `implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730144921.md`
4. `../../requirements/public_demo_minimal_access_and_runtime_portability_requirements_ja.md`
5. `../../architecture/public_demo_access_profile_and_runtime_portability_architecture_ja.md`
6. `../../adr/adr_0027_public_demo_minimal_access_and_deferred_control_hooks_ja.md`
7. `../../../../shared/operations/research_asset_mutation_control_ja.md`
8. `../../../../shared/task_roles/task_role_write_authority_policy_ja.md`

## 3. Authorized Mutation Scope

必要な最小差分に限り、次を変更できる。

```text
scripts/runtime/lightning/public_demo_service.sh
scripts/runtime/lightning/basic_preview_common.sh

src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/web/app.py
src/margpa_runtime_llm/web/access_profiles.py

tests/unit/runtime/test_lightning_basic_preview_service.py
tests/unit/web/test_access_profiles.py
tests/unit/web/test_web_cli.py
tests/integration/web/test_web_app.py

docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_YYYYMMDDHHMMSS.md
```

`basic_preview_service.sh`または`auto_start_preflight.sh`への追随変更が必要な場合は、共通Helper分離による既存Call Site適合の最小差分だけ許可する。

次は変更しない。

```text
config/web_profiles/
config/profiles/
config/models/
pyproject.toml
uv.lock
README.md
docs/public/
docs/project/current/
docs/project/shared/
ADR／Requirements／Architecture正本
Phase Index
既存History
Model Artifact
```

Authorized Scope外の変更が必要と判断した場合は実装せず、理由、対象、必要差分および影響をStatusへ記載して設計統括者役へ戻す。

## 4. Pre-mutation Gate

実装開始前に次を確認する。

- Project Rootが`margpa-runtime-llm/`である。
- Project Root外へ触れない。
- `models` Symbolic Linkを追跡しない。
- User Backup GateとMutation AuthorizationをSource Status／ユーザー指示から確認する。
- 対象FileのBefore SHA-512を取得する。
- 本Handoff作成後に対象Sourceが変更されていない。
- 変更予定Fileを列挙する。
- 未承認のGit、Lightning、Upload、DependencyまたはEnvironment変更を行わない。

本HandoffはScope内実装の設計指示であり、Project Root外操作、Lightning操作または広範なCleanupの許可ではない。

Review時点の主要Baseline：

```text
scripts/runtime/lightning/public_demo_service.sh
b2fa7dc6e1c75c866cc8da9f603389b888db25c4242d87a879e306e6d9dbff06d14fa18a1edb116747455d0725dd4f148ddaba0d6fc9e8c7c37cf264f0f97289

scripts/runtime/lightning/basic_preview_common.sh
9dd62759e8771908c3b2be3cbba1bfb82b1c40c4934a61d67e95000affc6f8e5f847efd310663315ab710783ad7598712b7aa70f184fffa0df8adc661152488c

src/margpa_runtime_llm/entrypoints/web/main.py
2751e7409c3aa858d8e3c3d9712977284b4b3614e6952ea4f91fb309fea145295e3c7642d84113cb67bd6240aa1b2b0544225f52a88715c47c42fc6f9c8934e5

src/margpa_runtime_llm/web/app.py
e5ee8a99e886b6f26660c1fe4d68464e85101478c7056a8cb92bf7527934ae3abb8a6e5863c420dfe01b1e41544082ca97774866c3abc4aab9fdd58ffe70c658

src/margpa_runtime_llm/web/access_profiles.py
b91d4420bb9b822607e7d23147b41f09b9c19239fa3bfe71ebcf21d8856f3b030067a682b0ebd6630d6f5f1a38b5fa7f635de9df890193926963785fa60b84ba
```

不一致がある場合は勝手にMergeせず、現在値と差分対象を報告して停止する。

## 5. Required Changes

### 5.1 Stateless Public Preflight

Public Demo用Preflightを、Basic Preview Lifecycle Stateへ依存しない経路へ分離する。

Public Demoで維持する検査：

```text
Host／Architecture／Container
Distribution
Project Root
Model Root
Environment Prefix
Python Version
uv Version
margpa-web
Deployment Profile Schema
Model Definition／Registry
Model Artifact Layout／Existence
Health Contract Source
Web Host／Port
Explicit public_demo Access Profile
Authentication = none
Documentation RAG = denied
Optional Control = off
```

Public Demoで行わない処理：

```text
Runtime State Root Resolution
Runtime State Permission Validation
Ownership Marker Validation
PID File Validation
Log File Validation
Lifecycle Lock Validation
Runtime State／PID／Log／Lockの作成・変更・削除
```

推奨構造：

```text
Shared Core Preflight
  → Project／Runtime／Model／Access共通検査

Basic Preview Lifecycle Preflight
  → Shared Core
  → Runtime State／Lock／Credential検査

Public Demo Stateless Preflight
  → Shared Core
  → Public Profile／RAG Deny／Control Off検査
```

Function名は実装者が既存構造へ合わせてよい。巨大なCode Copyを作らず、Lifecycle固有検査の適用先を明示的に分ける。

`MARGPA_RUNTIME_STATE_ROOT`が設定されていても、Public Demoはその値を解決・検証・表示・変更しない。

既存Basic Previewでは、Dedicated State Root、Permission、Marker、PID、LogおよびLockの安全検査を全て維持する。

### 5.2 Credential Isolation Before Any Child Process

Public Demo Entrypointでは、次の三項目を最初の子Process生成前に除外する。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

要件：

- Public Script Process内だけで除外する。
- 親Shell、Lightning Managed SecretsまたはBasic Preview Processを変更しない。
- Common Script読込が子Processを起動する場合は、その前に除外する。
- `preflight`と`run`の両方へ適用する。
- 最終`exec`時の防御的な`env -u`は維持してよい。
- Credential値を比較、表示、Hash化、保存またはStatus記録しない。
- Argument、Process Command Line、Output、Log、ErrorおよびTest Artifactへ含めない。

### 5.3 Effective Optional Control Hook

`PublicControlPolicyPort`をWeb Application Compositionへ注入し、Chat Request Pipelineから呼び出す。

最低Contract：

```text
Request Validation後／Generation開始前:
  check_request

Conversation Generation開始直前:
  before_generation

Generation Observation Point:
  observe_generation

Completed／Cancelled／Errorを含むTerminal Path:
  after_generation
```

実装上の注意：

- Disabled Policyは副作用なし、拒否なし、保存なしを維持する。
- Streamingの終了、Client Disconnect、CancelおよびExceptionで`after_generation`の二重呼出または呼出漏れを起こさない。
- 既存Conversation RuntimeのSingle-active-generation Contractを壊さない。
- Summary Mode、Thinking、Copy、Language、StopおよびNew Chatを変更しない。
- Control PolicyをAccess Profile、Model AdapterまたはConversation DomainへHardcodeしない。
- 実Control Adapterは追加しない。

### 5.4 Documentation RAG Boundary

今回RAG本体を追加しない。

次を維持する。

```text
public_demo:
  capability = denied
  feature = disabled
  adapter = not constructed

basic_preview／local:
  capability = eligible
  feature = disabled
  adapter = not constructed
```

Public DemoへRAG用Route、Option、Document Path、Index、EmbeddingまたはDependencyを追加しない。

## 6. Required Tests

### 6.1 Stateless Public Preflight

- Basic Preview Stateが存在しなくてもPublic `preflight／run`が合格する。
- Basic Preview Stateが不正ModeでもPublicへ影響しない。
- Basic Preview Marker／PID／Log／Lockが不正でもPublicへ影響しない。
- `MARGPA_RUNTIME_STATE_ROOT`が危険・不正・Read-onlyな値でもPublicは参照しない。
- Public実行後にRuntime State、PID、LogまたはLockを生成しない。
- Basic Preview側では同じ不正状態を従来どおりFail Closedで拒否する。

Test用DirectoryはProject内の承認済みPytest Temporary Rootだけを使用し、Project Root外へ新規Artifactを作らない。

### 6.2 Credential Isolation

- Public `preflight`のPython／uvを含む全子ProcessにCredential三項目が存在しない。
- Public `run`の全子Processと最終Web Processに三項目が存在しない。
- Basic PreviewではCredentialを従来どおりApplicationへ渡す。
- Secret実値がstdout、stderr、Process Record、Test ArtifactまたはFailure Messageへ出ない。

固定CredentialをRepositoryへ書かず、Test内で動的生成する。

### 6.3 Control Hook

Recording／Spy Policyで次を確認する。

- 正常Generation
- Streaming完了
- Cancellation
- Client Disconnect
- Generation Error
- Summary Mode

Disabled Policy使用時に既存HTTP Status、SSE Event、生成結果およびCancel挙動が変わらないことを確認する。

### 6.4 Regression

最低限次を実行する。

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
tests/unit/web/test_access_profiles.py
tests/unit/web/test_auth.py
tests/unit/web/test_web_cli.py
tests/integration/web/test_web_app.py
```

その後：

```text
Repository Full Pytest
Ruff Check
Ruff Format Check
Mypy
Shell Syntax
uv lock --check
```

Model SmokeとLightning External Trialは実装担当Scope外である。未実行項目をPassと記載しない。

## 7. Prohibited

- Lightning Studio／API Builder／Port／Public URL／Managed Secretsの変更
- Upload、DownloadまたはCloud操作
- 匿名Public Accessの有効化
- Basic認証Previewの削除
- Rate Limit、Budget、Cooldown、QuotaまたはCost Guard本体の実装
- Documentation RAG本体またはDependencyの追加
- Agent／Tool／External APIの追加
- Model Artifactの読取・変更・Hash再計算
- Dependency Version変更
- Git／GitHub操作
- `.DS_Store`、Cache、既存Artifactまたは無関係FileのCleanup
- Authorized Scope外の変更

## 8. Completion Status

完了後、新Timestampで次を作成する。

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_YYYYMMDDHHMMSS.md
```

Statusへ必ず記載する。

- Before／After File一覧
- Before／After SHA-512
- F1～F3の対応箇所
- Stateless Public PreflightのCall Graph
- Credential除外が最初に成立する位置
- Public／BasicのEnvironment継承差
- Control HookのInvocation Order
- Test件数と結果
- 未実行項目
- Known Limitation
- Project外／Lightning／Gitを変更していないこと
- Scope外変更が0件であること

既存Status、Review、HandoffまたはIndexを上書きしない。

## 9. Acceptance

次を全て満たすこと。

1. Public DemoがBasic Preview Runtime State、PID、Log、MarkerおよびLockへ依存しない。
2. Public DemoがLifecycle Artifactを作成・変更・削除しない。
3. Public Demoの最初の子ProcessからCredential三項目が不在である。
4. Basic Previewは従来のCredential／Lifecycle安全契約を維持する。
5. Public Documentation RAGは引き続き強制無効である。
6. Optional Controlは全て`off`のままである。
7. Disabled PolicyがRequest／Generation Pipelineを実際に通る。
8. Model／Deployment／Access／Feature／Lifecycleの分離を維持する。
9. 対象Test、Full Suite、Static CheckおよびShell Checkが合格する。
10. Lightning、Model、Git、DependencyおよびProject Root外を変更していない。

実装担当Status作成後、設計統括者役へ再Reviewを依頼する。
