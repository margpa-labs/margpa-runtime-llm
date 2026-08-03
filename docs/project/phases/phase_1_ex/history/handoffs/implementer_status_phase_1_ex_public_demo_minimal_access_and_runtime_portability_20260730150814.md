# Phase 1-ex Public Demo Minimal Access／Runtime Portability 実装Status

```yaml
document_id: implementer_status_phase_1_ex_public_demo_minimal_access_and_runtime_portability
phase: phase_1_ex
status: implementation_complete_review_pending
language: ja
created_at: 2026-07-30 15:08:14 JST
completed_at: 2026-07-30 15:44:31 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730144921.md
mutation_id: public-demo-minimal-access-20260730150814
backup_confirmation: user_confirmed
supersedes: null
```

## 1. Result

Phase 1-ex Public Demo用の明示Access Profile、Foreground EntrypointおよびRuntime Portability Overrideを実装した。

Access Modeは次の三つを型として分離した。

```text
local         : Loopback限定／認証なし
basic_preview : Non-loopback許可／Basic認証必須
public_demo   : Non-loopback許可／認証なし／Documentation RAG拒否
```

`auth disabled`だけではNon-loopback公開へ移行できない。匿名Non-loopback Bindには、追跡対象の`public_demo` Access Profileを明示する必要がある。

Lightning UI、Port、URL、Studio、Plugin、Secret、Git、Dependency、ModelおよびCloud環境は変更していない。

## 2. Changed Files

新規：

```text
src/margpa_runtime_llm/web/access_profiles.py
config/web_profiles/basic_preview.toml
config/web_profiles/public_demo.toml
scripts/runtime/lightning/public_demo_service.sh
tests/unit/web/test_access_profiles.py
```

更新：

```text
src/margpa_runtime_llm/web/auth.py
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
tests/unit/web/test_auth.py
tests/unit/web/test_web_cli.py
tests/integration/web/test_web_app.py
tests/unit/runtime/test_lightning_basic_preview_service.py
```

変更なし：

```text
pyproject.toml
uv.lock
Model実体／Model Definition既存内容
Requirements／Architecture／Governance／ADR正本
docs/public/
```

## 3. Access／Authentication Contract

- Built-in `local`はLoopback Bindだけを許可する。
- `basic_preview`は従来どおりBasic Username／Passwordの両方を必須とする。
- `public_demo`はBasic Credential環境変数を読まず、引数にも子Processにも渡さない。
- `basic_preview`または`public_demo`以外のAccess ProfileでNon-loopbackへBindできない。
- Profile Key、Access Mode、Authentication ModeおよびNon-loopback許可の矛盾を起動前にFail Closedで拒否する。
- Public Demo ProfileがDocumentation RAGを許可する構成を起動前に拒否する。
- Optional Controlの未実装値をProfileへ指定した場合もFail Closedで拒否する。

## 4. Documentation RAG Separation

Documentation RAGは認証方式や公開Entrypointと同一機能として扱わない。

実装境界：

```text
Web Access Profile
  └─ Capability Ceilingだけを宣言

Documentation RAG Feature Profile
  └─ Access／Authとは独立して有効化意思を宣言

Documentation RAG Adapter Availability
  └─ 実Adapterが構築可能かを別条件として宣言
```

現在の実効状態：

```text
Public Demo:
  Access Capability = denied
  Feature Profile   = disabled
  Adapter           = not constructed
  Effective State  = disabled

Basic Preview／Local:
  Access Capability = eligible
  Feature Profile   = disabled
  Adapter           = not constructed
  Effective State  = disabled
```

将来のAWS／Azure等でも、認証ログインSurface、公開SurfaceおよびDocumentation RAGを別構成単位として扱う。Documentation RAGを使用する場合は、公開用Profileを変更せず、別のFeature ProfileとAdapterを明示注入する必要がある。公開用ProfileへDocumentation RAGを注入しようとした場合は拒否する。

Cloud Provider名、Vector Store、Embedding Model、認証方式またはRAG Dependencyは今回固定していない。

## 5. Optional Public Controls

将来Control用のPortだけを用意し、次は全て明示的に`off`とした。

```text
rate_limit
generation_budget
cooldown
public_max_new_tokens
request_quota
cost_guard
```

現在は副作用のないDisabled Policyだけを合成する。未実装ModeをProfileへ書いて見かけ上有効化することはできない。

## 6. Runtime Portability

Web Access ProfileからModel、Deployment、Platformを分離した。

次をAccess Profileとは独立してOverrideできる。

```text
MARGPA_WEB_PROFILE       / --profile
MARGPA_MODEL_DEFINITION  / --registry
MARGPA_MODEL_ROOT        / --model-root
MARGPA_MODEL_KEY         / --model-key
MARGPA_CONTEXT_SIZE      / --context-size
```

Access ProfileへQwen、GGUF、llama.cpp、Lightning、Metal、CUDA、AWSまたはAzure固有値を含めていない。

## 7. Public Demo Foreground Entrypoint

Repository側入口：

```bash
bash scripts/runtime/lightning/public_demo_service.sh preflight
bash scripts/runtime/lightning/public_demo_service.sh run
```

Contract：

- `preflight`はProject／Environment／Deployment／Model Definition／Public Access Profile／Disabled Controlを検査する。
- `run`は検査後に`exec margpa-web`し、Foreground Processを維持する。
- Basic Credential三項目を子Process Environmentから明示的に除外する。
- Background PID、Log、LockまたはRuntime Stateを作成しない。
- Platform Port、公開URL、Startup設定およびStudio操作は行わない。

Script Mode：

```text
755
```

## 8. UI

既存UIのBasic認証前提表現を、Access Modeに依存しないResearch Preview表現へ変更した。Public Demo ResponseへCredential、内部Path、Stack TraceまたはDocumentation RAG入口を追加していない。

## 9. Verification

Mutation Control条件：

```text
Backup                         : User confirmed
Approved temporary directory  : tests/.pytest-tmp-public-demo/
PYTHONDONTWRITEBYTECODE        : 1
Pytest cache provider          : disabled
Ruff cache                     : disabled
Mypy incremental/cache         : disabled, /dev/null
Temporary directory cleanup    : PASS
Project Root external access   : none
```

結果：

```text
Target Web／Runtime Tests : 80 passed
Repository Full Suite     : 319 passed／3 deselected
Ruff Check                : PASS
Ruff Format Check         : PASS／98 files
Mypy Strict               : PASS／93 source files
Shell Syntax              : PASS
```

主な回帰範囲：

- Local／Basic Preview／Public Demo Access Matrix
- Non-loopback Fail Closed
- Basic Credential必須および値の非露出
- Public DemoでCredentialを読まない／渡さない
- Public Demo Root／Streaming／Stop Route／Security Header
- Public DemoでDocumentation RAG Override拒否
- RAG Capability／Feature Profile／Adapter Availabilityの独立性
- Optional Control全項目`off`
- Foreground Process Identity／TERM Signal
- Public EntrypointがRuntime Stateを生成しない
- Deployment／Model Definition／Model Key／Context Size Override
- 既存Basic Preview Lifecycle回帰

## 10. SHA-512 Mutation Evidence

既存Fileの`before`はMutation直前再検証値。新規Fileは`absent`。

```text
src/margpa_runtime_llm/web/access_profiles.py
  before: absent
  after : b91d4420bb9b822607e7d23147b41f09b9c19239fa3bfe71ebcf21d8856f3b030067a682b0ebd6630d6f5f1a38b5fa7f635de9df890193926963785fa60b84ba

src/margpa_runtime_llm/web/auth.py
  before: 4d814da86aff61a0728fb89c9fe87095dd7f1692b6e569835fc9db81b28fbb8df3ecb3c4ba3f859b47b5c9e0262956adc40c90b6dc41b26f29b67229fb3631c8
  after : a994a6b6f1560739a9137bfb55cf95601c8354e079e155bce8713202b811d9b1a4d2cdbbb2e8ec8017fe7143119201124116a7f4c9a672a6e85b94405c794424

src/margpa_runtime_llm/entrypoints/web/main.py
  before: 65099830533778996a67809beb23fa0dbcc8cc39e389dd4f403d1d1a6896bd827f586a20c3fd8df8343067f26a1df259647221ed549fa2914f622b054d902c5b
  after : 2751e7409c3aa858d8e3c3d9712977284b4b3614e6952ea4f91fb309fea145295e3c7642d84113cb67bd6240aa1b2b0544225f52a88715c47c42fc6f9c8934e5

src/margpa_runtime_llm/web/static/app.js
  before: 7a6c950b842f700a021aa9c6be7acbaa592f1760bf86f39598c25933428f9468971f182969932f837ffa881ab410545d79d7941e852935f48aa4fa59b836bfba
  after : 440b414267786c38f6edc61b023b5a4004643681b3ee3ce5fb4995b2a1fa2ee7b3cb754deac4cc18b2066a60765c3122ebcb5e31b810d6fb1ea0053030aaaf11

src/margpa_runtime_llm/web/static/index.html
  before: 7d6cd586ca0647533bd3f2028ad7dbc45cd7b64549d2bd68c84e66684be2d8da14c1bcc9ffd2c1e9d5310800ac0c9f479bacc525b6414ae0acb13a2c0060b7bf
  after : ec13c8b2a98d5416a1a6f5949fc0c27127636781a5d9479523075d390c079b49ea428f5de9268f547f345d20cf822ceabb9f11baecb7cd589a34e888393c3e8b

config/web_profiles/basic_preview.toml
  before: absent
  after : 3b0c9ab2530322a2bd825b1afba139a8ccc8e80c7127d08fdf6b81e9e7732e13ea7344213491806002aeb9569609de02e30f623a4a548dc53c4c3453d9c21b21

config/web_profiles/public_demo.toml
  before: absent
  after : 09db3c8045d2912434358d7cb6d3be70f7d78ccc083a6fee099ee94876bdd47cb2e0d3bb448d3710f5dc254e2dca8b25d4a7b1441acab2629eaa239051726b0e

scripts/runtime/lightning/basic_preview_common.sh
  before: 1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58
  after : 9dd62759e8771908c3b2be3cbba1bfb82b1c40c4934a61d67e95000affc6f8e5f847efd310663315ab710783ad7598712b7aa70f184fffa0df8adc661152488c

scripts/runtime/lightning/basic_preview_service.sh
  before: 7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac
  after : eb24cc058be641ab09ace05340cb05377900474ff2cbfac6227308ee52a3926c4bec921c8f981885b973351406b2d05cb2fcf7c691015deb626e6d3639e0e102

scripts/runtime/lightning/auto_start_preflight.sh
  before: bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d
  after : 1c6cf2a3b66e004b172fa6255db7690a5d16417eaf35e586fdd3add0b7ea5d5a5798dfc3c94c70b22ea542f53040bb838048581e715557e4d615e7359dfda94a

scripts/runtime/lightning/public_demo_service.sh
  before: absent
  after : b2fa7dc6e1c75c866cc8da9f603389b888db25c4242d87a879e306e6d9dbff06d14fa18a1edb116747455d0725dd4f148ddaba0d6fc9e8c7c37cf264f0f97289

tests/unit/web/test_access_profiles.py
  before: absent
  after : aa83057f7c9b100ba49473a7b34306ec320be4b389df996876e6c56ef4904a98fc88ea66fe3e187e6a832e8a5b42912204aba7c13a8332fea1aba71d8870c5f1

tests/unit/web/test_auth.py
  before: cc4c927a88e0be62bb8d85cb6f6ab1152d4a2ef6404bb0cf4888cd604dccbd17580d924e37366383c99e9e70531f59ab513346f7d910d16eed8c745bee966543
  after : 1461646441f615e3a5c21291d61c180fc52c5663f3543d0d8874015a4e510cf55727c6e26499216690b5e5a433c9e0cf7d6d8d85d523ed76ff44a7f046135303

tests/unit/web/test_web_cli.py
  before: 11527f860d054ec0f2d23199f7c3a83ccd617e23a0360846881eb3ddf483e49ccf8f6904d93f661619b85c902755de5f84adf8643ffd78cbf22be79a94650629
  after : bf53af32f581a23eb8fc6845c500a83e225837f79aee9e7ee9165c28fec95b1e275f0007c16825ebad13c4838a148b62400961a4197ddcbfb86e1e52e6dc52ed

tests/integration/web/test_web_app.py
  before: ea59bfcb32ae4246be25eec09955ae8156e8246b5324190f616712d38f5793196cba4b6c7d93a80228c7b80dd0f61dba597fecd4375957d15c650a9177279ac9
  after : 561fe2fe9b068cd4043c6f267beef0d601c1ee1f45a46d4e9d56978eb6bf6cdc5de90e5a9ac3b914768e6e08302e90303b39649c0db8bf448c21899184f9e1c6

tests/unit/runtime/test_lightning_basic_preview_service.py
  before: 2413cd6ca9a953d2829e676aac209e6b4781b0fe6ce3befaa0d7d934ca9cdff82cb8556ac8399c0a166c650084c9ff3443d4f64efbe76dbca080f3b6389eb88e
  after : 8a6be929ee8228ad46a81675691c10503e31738115596079029b319d06f7259bd0e9f37dad5310a7e6079b3dce6778eed79a4fe414b0b5d977b8b04a4f6a096f
```

## 11. Manual Lightning Procedure

ユーザーがBackupおよび配置確認後にLightning上で手動実施する。

1. Correct Targetが`Nazuna-Research-Org`配下であることを確認する。
2. 更新済みRepositoryをLightning側へ反映する。
3. Project Rootで次を実行する。

   ```bash
   bash scripts/runtime/lightning/public_demo_service.sh preflight
   ```

4. `check.web_access_profile=pass mode=public_demo`、`check.access_boundary=pass mode=public_demo authentication=none`、`check.documentation_rag=pass capability=denied effective=disabled`および`check.public_controls=pass mode=off`を確認する。
5. Platform側Host／Portをユーザーが設定する。
6. Foreground起動する。

   ```bash
   bash scripts/runtime/lightning/public_demo_service.sh run
   ```

7. `/healthz`、Root UI、短いGeneration、Stop、Response Header、Credential非要求および内部情報非露出を確認する。
8. 同時に既存Basic Previewを起動せず、Port衝突を避ける。
9. Public URL、Credential、Account ID、個人PathまたはPrompt／Response本文をStatusへ記録しない。

Lightning上の実結果は本Statusでは未実施であり、合格扱いにしていない。

## 12. Rollback

### 12.1 Repository側

Repository側Rollback対象は、今回のPublic Demo Minimal Access／Runtime Portability実装である。Lightning構築そのものだけを戻す手順ではない。

ユーザーBackupを基準に、Section 2の更新Fileを復元し、新規File五件を除去する。Append-only Historyである本Statusは削除せず、Rollback結果を別の新規Status Eventとして記録する。

手動復元後は、Basic Preview対象Test、Repository Full Suite、Ruff、MypyおよびShell Syntaxを再確認する。

### 12.2 Lightning／Platform側

Lightning上でユーザーがPublic Demoを設定または起動した後のPlatform Rollbackは別操作とする。

1. Foreground Public Demo ProcessをTERMまたはPlatform Stopで停止する。
2. Public URL／Port公開を停止する。
3. Startup CommandまたはPlatform Configurationを元へ戻す。
4. Public Demo用Environment設定を外す。
5. 既存Basic Previewの設定およびCredentialを自動削除せず、ユーザーが保持判断する。
6. Basic Preview `preflight`と必要なLifecycle回帰を確認する。

Repository RollbackとPlatform Rollbackは独立して実行できる。

## 13. Remaining／Review Gate

- 設計統括者役Review Accepted待ち。
- Lightningでの配置、Preflight、公開、Generationおよび停止はユーザー手動。
- Documentation RAG Adapter、認証ログイン用Cloud Surface、RAG用Feature Profile実体およびCloud Deploymentは将来Phase。
- AWS／Azure等のProvider選定、RAG Dependency、Vector Store、Embedding Modelおよび認証方式は未決。
- Review Accepted前に後続Phase、RAG実装、Cloud構築またはGit操作へ進まない。
