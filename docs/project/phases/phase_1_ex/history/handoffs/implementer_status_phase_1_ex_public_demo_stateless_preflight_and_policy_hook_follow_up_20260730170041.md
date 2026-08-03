# Phase 1-ex Public Demo Stateless Preflight／Credential Isolation／Policy Hook Follow-up 実装Status

```yaml
document_id: implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up
phase: phase_1_ex
status: implementation_complete_review_pending
language: ja
created_at: 2026-07-30 17:00:41 JST
owner: 実装者役
source_review: designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730161108.md
source_handoff: implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730161108.md
source_status: implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730150814.md
mutation_id: public-demo-stateless-preflight-policy-hook-follow-up-20260730161108
backup_confirmation: user_confirmed_for_this_mutation
supersedes: null
```

## 1. Result

設計統括者ReviewのF1～F3だけを修正した。

```text
F1 Stateless Public Preflight:
  RESOLVED

F2 Credential Isolation Before Any Child Process:
  RESOLVED

F3 Effective Optional Control Hook:
  RESOLVED
```

既存Explicit Access Profile、Basic Preview、Public RAG拒否、全Optional Control `off`およびRuntime交換性を維持した。

Lightning、Model、Git、DependencyおよびMac用Runtime／Configは変更していない。

## 2. Changed Files

更新：

```text
scripts/runtime/lightning/public_demo_service.sh
scripts/runtime/lightning/basic_preview_common.sh
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/web/app.py
tests/unit/runtime/test_lightning_basic_preview_service.py
tests/integration/web/test_web_app.py
```

新規：

```text
docs/project/phases/phase_1_ex/history/handoffs/
  implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170041.md
```

Scope外変更：

```text
0
```

## 3. F1 Stateless Public Preflight

共通Scriptを次の境界へ分割した。

```text
margpa_resolve_core_configuration
  └─ Project／Workspace／Model／Environment／uv／Bind
     Deployment／Access／Registry／Model Override

margpa_common_preflight_checks
  └─ Host／Architecture／Container／Distribution
     Project／Model／Python／uv／Web Entrypoint
     Deployment Schema／Model Artifact／Health Contract／Bind

margpa_resolve_lifecycle_configuration
  └─ Basic Preview Runtime State／PID／Log／Marker／Lock
     Health／Stop Timeout

margpa_validate_lifecycle_preflight
  └─ Runtime State Writable Ancestor／curl
```

Public Call Graph：

```text
public_demo_service.sh
  → Credential unset
  → Common Helper source
  → select_public_access_profile
  → margpa_stateless_project_preflight
       → margpa_resolve_core_configuration
       → margpa_common_preflight_checks
  → margpa_validate_public_demo_contract
       → public_demo Profile
       → authentication none
       → Documentation RAG denied
       → Optional Control off
  → margpa_build_web_arguments
  → Foreground exec margpa-web
```

Basic Preview Call Graph：

```text
basic_preview_service.sh
  → Common Helper source
  → margpa_project_preflight
       → margpa_resolve_configuration
            → margpa_resolve_core_configuration
            → margpa_resolve_lifecycle_configuration
       → margpa_common_preflight_checks
       → margpa_validate_lifecycle_preflight
  → margpa_validate_basic_preview_contract
       → Pure CPU Contract
       → basic_preview Profile
       → Credential Validation
```

Public Preflightは次を参照、解決、表示、作成、変更または削除しない。

```text
MARGPA_RUNTIME_STATE_ROOT
basic-preview.pid
basic-preview.log
.margpa-basic-preview-state
.margpa-runtime-llm-basic-preview.lifecycle.lock
```

Basic Preview側の既存Lifecycle安全検査は維持した。

## 4. F2 Credential Isolation

Public Script内の最初の外部Command、Command SubstitutionおよびCommon Helper Sourceより前に次を`unset`する。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

最終`exec`時の`env -u`も防御的に維持した。

Environment継承：

```text
Public Demo Script Process:
  Parentから起動後、Script自身だけで三項目をunset

Public dirname／Python／uv／margpa-web:
  三項目すべてabsent

Parent Terminal／Managed Secrets:
  変更なし

Basic Preview Python／uv／margpa-web:
  既存どおりEnvironment継承

Credential Value:
  Argument／Output／Log／Test Artifact／Statusへ保存なし
```

TestではCredential値を実行時に動的生成し、存在有無だけを記録した。固定SecretをRepositoryへ追加していない。

## 5. F3 Effective Optional Control Hook

`PublicControlPolicyPort`を`create_web_app`へInterfaceとして注入し、Composition Rootから実Policyを渡すよう変更した。

Invocation Order：

```text
FastAPI Request Schema Validation
  → control_policy.check_request
  → control_policy.before_generation
  → ConversationGenerationService.start
  → SSE semantic eventごとにcontrol_policy.observe_generation
  → completed／cancelled／error／client disconnectのfinally
       → control_policy.after_generation exactly once
```

Generation開始失敗では、`ConversationGenerationService.start`のException Pathから`after_generation`を一回呼ぶ。

Keepalive CommentはGeneration Eventではないため、`observe_generation`対象にしない。

`DisabledPublicControlPolicy`は引き続き副作用、拒否、Persistenceおよび出力変更を持たない。

実Rate Limit、Budget、Cooldown、Quota、Cost Guard、Counter、TimerまたはExternal Storeは追加していない。

## 6. Documentation RAG Boundary

変更なし。

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

RAG Route、Option、Document Path、Index、Embedding、RetrievalまたはDependencyは追加していない。

## 7. Mac／Basic Preview Preservation

次は変更していない。

```text
Mac Deployment Profile
Mac Metal Runtime
Model Definition
Web Access Profile Config
src/margpa_runtime_llm/web/access_profiles.py
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
pyproject.toml
uv.lock
```

Mac／Metal Integration対象を含むRepository Full Suiteに合格した。

Mac用`uv`はVersion確認とLock整合のRead-only Checkだけに使用し、Install、Update、Lock更新またはMac環境変更を行っていない。

## 8. Required Test Evidence

Target Test：

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
tests/unit/web/test_access_profiles.py
tests/unit/web/test_auth.py
tests/unit/web/test_web_cli.py
tests/integration/web/test_web_app.py

Result:
  92 passed
```

Repository Full Suite：

```text
331 passed
3 deselected
```

Full Suiteには次を含む。

```text
tests/integration/test_llama_cpp_metal.py
  PASS

Lightning Basic Preview Lifecycle:
  42 passed

Web Integration:
  27 passed
```

Static／Lock：

```text
Ruff Check:
  PASS

Ruff Format Check:
  PASS／98 files

Mypy:
  PASS／93 source files

Shell Syntax:
  PASS

uv:
  0.11.29／aarch64-apple-darwin

uv lock --check --offline --no-cache:
  PASS／122 packages resolved
```

対象Test初回では、新規AssertionがBasic Fail Closedの`pid_file`／`log_file` Check名を許容していなかった二件と、Broad Root `/`を通常のAbsolute Path表示と区別できていなかった一件が失敗した。Production実装Failureではない。Assertionを契約へ限定修正後、Runtime対象42件、全対象92件およびFull Suite 331件が合格した。

全Ruff初回では、承認済みPytest Temporary Root内に作成された疑似Project FixtureをRepository Sourceとして走査した。Temporary Root削除後にRepository本体へ再実行し合格した。

## 9. New Regression Coverage

### Stateless Public

- Basic Runtime State不在でもPublic `preflight／run`が合格。
- Basic State Directory不正ModeでもPublicへ影響しない。
- Marker、PID、LogおよびLock不正でもPublicへ影響しない。
- Publicは不正Artifactを変更しない。
- Broad／Dot Segment Runtime State OverrideをPublicが解決しない。
- 同じ不正状態をBasic Previewは従来どおりFail Closedで拒否。
- Public Foreground ProcessがPID／Log／State／Lockを作成しない。

### Credential Isolation

- Publicの最初の`dirname`子Processで三項目不在。
- Public Python／uv／margpa-webで三項目不在。
- Public `preflight`と`run`の両方で不在。
- Basic Previewでは既存どおりApplicationへCredentialを継承。
- Credential実値のOutput／Record非露出。

### Control Hook

- Normal Completion。
- Streaming Completion。
- Summary Mode。
- Cancellation。
- Client Disconnect。
- Generation Error。
- Generation Start Failure／Model Busy。
- Request Validation失敗時にPolicyへ未到達。
- `after_generation`一回のみ。
- Disabled Policy使用時の既存HTTP／SSE／Cancel挙動維持。

## 10. Verification Artifact Control

承認済みTemporary Root：

```text
tests/.verification-tmp-public-demo-follow-up/
```

用途：

```text
Pytest --basetemp
Mypy cache
```

完了後状態：

```text
removed
```

`PYTHONDONTWRITEBYTECODE=1`、Pytest Cache Provider無効、Ruff `--no-cache`を使用した。

## 11. External Access

ユーザーはMac用`uv`を使用不能にしない条件でRead-only Lock Checkを許可した。

当初提示された次の候補Pathは存在せず、実行も変更も成立しなかった。

```text
<workspace>/.runtime-tools/uv/0.11.29/bin/uv
```

Shellが解決した実体：

```text
$HOME/.local/bin/uv
```

実施Action：

```text
read／execute:
  uv --version
  uv lock --check --offline --no-cache
```

外部File、Cache、PackageまたはEnvironmentの作成・変更・削除は行っていない。

これ以外のProject Root外Pathを走査、変更または作成していない。

## 12. SHA-512

```text
scripts/runtime/lightning/public_demo_service.sh
  before: b2fa7dc6e1c75c866cc8da9f603389b888db25c4242d87a879e306e6d9dbff06d14fa18a1edb116747455d0725dd4f148ddaba0d6fc9e8c7c37cf264f0f97289
  after : 8f4cac68946ab3827e82446f2c04a58516ffffcb13fe27c81218086a112443e1ee4042b3a0084a785ebc00cf2251fd2c9e41e8bb1f015dbbf62a3139ff416aa8

scripts/runtime/lightning/basic_preview_common.sh
  before: 9dd62759e8771908c3b2be3cbba1bfb82b1c40c4934a61d67e95000affc6f8e5f847efd310663315ab710783ad7598712b7aa70f184fffa0df8adc661152488c
  after : e86e1dd85eb48d68523bcc0e3fe859c66e413cff3688412a84c90ce8ec86cd9bab71e9ea9ec27bb52230159fd574a45b789c8b205a6cb37d6fe2bf2a2f843c14

src/margpa_runtime_llm/entrypoints/web/main.py
  before: 2751e7409c3aa858d8e3c3d9712977284b4b3614e6952ea4f91fb309fea145295e3c7642d84113cb67bd6240aa1b2b0544225f52a88715c47c42fc6f9c8934e5
  after : ececf838ae27200ca662b2278c5ee30ad657e6b223bee7e22ff0cd65661a4186eaa1bbcd34713aeb41175aa1d7c69414d74d3207caa581fb17638d150f305972

src/margpa_runtime_llm/web/app.py
  before: e5ee8a99e886b6f26660c1fe4d68464e85101478c7056a8cb92bf7527934ae3abb8a6e5863c420dfe01b1e41544082ca97774866c3abc4aab9fdd58ffe70c658
  after : 627695ba9cf878c96749a03349c02381dae65a420d83e33a6a5f9415e4785e7c353e485c463fad35a4f1d0d635613d514c1100962916cc3e5eeee3cd0ea4c90e

tests/unit/runtime/test_lightning_basic_preview_service.py
  before: 8a6be929ee8228ad46a81675691c10503e31738115596079029b319d06f7259bd0e9f37dad5310a7e6079b3dce6778eed79a4fe414b0b5d977b8b04a4f6a096f
  after : 502866c3cce07145ffd13b046b1b0e2fa4811c8731c288b2925f236f9b4acd5a74b589c16316da1cbb0f1f3f8c2035b54b27c64ba1d25ebb4979cbd6253ff46b

tests/integration/web/test_web_app.py
  before: 561fe2fe9b068cd4043c6f267beef0d601c1ee1f45a46d4e9d56978eb6bf6cdc5de90e5a9ac3b914768e6e08302e90303b39649c0db8bf448c21899184f9e1c6
  after : 06d7a14cc6992474c09909b1a10fa5cebc1d51c9e04eefbf840e65efc2d82c01c1382163689d26c6ab7061a5d3b4f23dcd72c9d381c43d430362fbd036b6773d
```

Unchanged Evidence：

```text
src/margpa_runtime_llm/web/access_profiles.py
  b91d4420bb9b822607e7d23147b41f09b9c19239fa3bfe71ebcf21d8856f3b030067a682b0ebd6630d6f5f1a38b5fa7f635de9df890193926963785fa60b84ba

config/web_profiles/basic_preview.toml
  3b0c9ab2530322a2bd825b1afba139a8ccc8e80c7127d08fdf6b81e9e7732e13ea7344213491806002aeb9569609de02e30f623a4a548dc53c4c3453d9c21b21

config/web_profiles/public_demo.toml
  09db3c8045d2912434358d7cb6d3be70f7d78ccc083a6fee099ee94876bdd47cb2e0d3bb448d3710f5dc254e2dca8b25d4a7b1441acab2629eaa239051726b0e

scripts/runtime/lightning/basic_preview_service.sh
  eb24cc058be641ab09ace05340cb05377900474ff2cbfac6227308ee52a3926c4bec921c8f981885b973351406b2d05cb2fcf7c691015deb626e6d3639e0e102

scripts/runtime/lightning/auto_start_preflight.sh
  1c6cf2a3b66e004b172fa6255db7690a5d16417eaf35e586fdd3add0b7ea5d5a5798dfc3c94c70b22ea542f53040bb838048581e715557e4d615e7359dfda94a

pyproject.toml
  518c8cbe95777e6481da94e28d90ec62cbb5679130a0b490b9437bd0d8e15f87436b9b2d3ee7b4de40a3f164800f4173ae763452088b2163c08360648f2a2a10

uv.lock
  46d946f33b374e2f32adc25e7bba313cf7722a5fd22f55e8c627481331cabd0f910f6c263423b06a120c80ad3b5d433c974dc44f51cfd4092ce853e21822871a
```

## 13. Not Executed

次は未実行であり、Pass扱いにしない。

```text
実Model Load／Generation Smoke
Lightning External Trial
Lightning Upload
API Builder変更
Port／Public URL変更
Sleep／Wake
Anonymous Public Access
Git／GitHub
Dependency Install／Update
```

## 14. Known Limitations

- Optional Control Interfaceは現在引数なしのLifecycle Hookである。将来の実AdapterがRequest Identity、UsageまたはCost情報を必要とする場合、Interface Contextを別設計で追加する必要がある。
- Public PreflightはStatelessだが、Project、Environment、Deployment、Model DefinitionおよびModel Artifactが利用可能であることは引き続き要求する。
- Public専用Rate、Budget、QuotaおよびCost保護は設計どおり`off`である。
- Repository検証はPlatform Public URL、External ReachabilityまたはTraffic-aware Public Wakeを保証しない。

## 15. Rollback

Repository側：

1. ユーザーが今回取得した変更直前BackupからSection 2の既存六Fileを復元する。
2. 本StatusはAppend-only Historyのため削除しない。
3. Rollback結果を新規Implementer Status Eventとして追加する。
4. Basic Preview対象Test、Web対象Test、Full Suite、Ruff、Mypy、Shell Syntaxおよび`uv lock --check`を再実行する。

Platform側：

```text
今回変更なし
Rollback対象なし
```

## 16. Review Gate

設計統括者役のAccepted再Review待ち。

Accepted前にLightning Public Demo Upload／Run、Public URL、Port、Anonymous Access、RAG、Gitまたは後続Phaseへ進まない。
