# Lightning Public Demo／Basic Preview Manual Acceptance

```yaml
document_id: lightning_public_demo_and_basic_preview_manual_acceptance
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-30 23:13:39 JST
owner: 設計統括者役
external_operation_owner: user
public_url_recorded: false
credential_recorded: false
rollback_executed: false
supersedes: null
```

## 1. Purpose

Phase 1-exで実装したPublic Demoの明示Access Profile、Credential分離、Stateless Preflight、Optional Control Hookおよび既存Basic Preview互換性について、ユーザーがLightning上で手動確認した一連の結果を記録する。

Public URL、Basic Credential、Account ID、Prompt本文、Response本文および個人識別情報は記録しない。

## 2. Repository Artifact Placement

Public Demo初回実装とFollow-upを合わせ、次の累積17 FileをLightning側の同一相対Pathへ反映した。

```text
src/margpa_runtime_llm/web/access_profiles.py
src/margpa_runtime_llm/web/auth.py
src/margpa_runtime_llm/web/app.py
src/margpa_runtime_llm/entrypoints/web/main.py
src/margpa_runtime_llm/web/static/app.js
src/margpa_runtime_llm/web/static/index.html

config/web_profiles/basic_preview.toml
config/web_profiles/public_demo.toml

scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/auto_start_preflight.sh
scripts/runtime/lightning/public_demo_service.sh

tests/unit/web/test_access_profiles.py
tests/unit/web/test_auth.py
tests/unit/web/test_web_cli.py
tests/integration/web/test_web_app.py
tests/unit/runtime/test_lightning_basic_preview_service.py
```

ユーザー報告：

```text
Placement:
  PASS

SHA-512:
  No mismatch reported

Script Permission:
  Applied
```

## 3. Initial Target Test Failure

最初のTarget Testは次の結果となった。

```text
72 passed
20 failed
```

20件はそれぞれ独立したProduction Failureではなく、全て次で停止していた。

```text
check.web_access_profile=fail reason=invalid_profile_contract
```

原因は、Manual ProcedureでTarget Testより前に次をPublic ProfileへExportしていたことである。

```text
MARGPA_WEB_ACCESS_PROFILE
```

Lightning Runtime Test Fixtureは安全な一時Projectを生成するが、親Process Environmentを継承する。親TerminalのPublic Profile PathがFixture内のBasic Preview Profile Pathより優先され、Basic Preview TestがPublic ProfileをBasic Contractとして検査したため、同一原因で連鎖失敗した。

これはSource、Config、転送、SHA-512またはLightning Runtimeの破損ではない。設計統括者役が提示したManual Procedureの実行順序不備である。

## 4. Test Procedure Correction

Project Fileは修正・再配置せず、Pytest ProcessだけからPublic Profile Overrideを除外する方式へ訂正した。

```bash
env -u MARGPA_WEB_ACCESS_PROFILE \
  "$MARGPA_ENV_PREFIX/bin/pytest" -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py \
  tests/unit/web/test_access_profiles.py \
  tests/unit/web/test_auth.py \
  tests/unit/web/test_web_cli.py \
  tests/integration/web/test_web_app.py
```

`env -u`は対象Pytest Processだけに作用し、親TerminalのPublic Demo設定を変更しない。

今後のManual Procedureでは次のいずれかを採用する。

```text
Option A:
  Target TestをPublic Profile Exportより先に実行する

Option B:
  Target Testをenv -u MARGPA_WEB_ACCESS_PROFILEで実行する
```

訂正後のAutomated Test件数そのものは、今回のユーザー報告に明記されていないため推測で補わない。

## 5. Public Demo／Basic Preview Manual Result

ユーザーがLightning上で確認した結果：

```text
Public Demo:
  PASS

Anonymous Access:
  PASS

Basic Preview:
  PASS

Basic Authentication:
  PASS

LLM Web Screen:
  PASS

LLM Generation:
  PASS

Public／Basic Separation:
  PASS
```

Public DemoとBasic Previewの両方でWeb画面およびLLM動作に問題がないことを確認した。

Public Demoは認証なし、Basic PreviewはBasic認証ありという別Access Contractを維持している。

## 6. Cold Start Observation

観測時刻：

```text
Start:
  23:01

Usable:
  23:03

Observed Cold Start:
  approximately 2 minutes
```

ユーザーはCache影響の可能性を指摘している。

本結果は当該時点の観測値であり、将来の起動時間を保証しない。Lightning側のCache、Studio状態、Machine割当、Model Artifact状態、NetworkおよびPlatform負荷により変動し得る。

## 7. Runtime Boundary

今回確認したPublic Demoの境界：

```text
Authentication:
  none

Documentation RAG:
  denied／disabled

Rate Limit:
  off

Generation Budget:
  off

Cooldown:
  off

Public Max New Tokens:
  off

Request Quota:
  off

Cost Guard:
  off

Tool／Agent／External Operation:
  not added
```

Basic Preview用CredentialはPublic Demoの子Processへ渡さない。Public DemoはBasic Preview用Runtime State、PID、Log、MarkerおよびLifecycle Lockへ依存しない。

## 8. Rollback

Rollback手順は定義済みだが、正常稼働中のPublic Demoを意図的に解除するManual Drillは実行していない。

```text
Rollback Procedure:
  DEFINED

Rollback Manual Drill:
  NOT_RUN

Phase Gate Impact:
  NON_BLOCKING
```

理由：

- Public DemoはForeground ProcessとしてPlatform Lifecycleに従う。
- Public API BuilderのStop／Disable、Auto-start OFFおよびPublic Link無効化で公開経路を停止できる。
- Basic Preview設定は削除せず保持している。
- Repository側のPublic／Basic Profileは同時に存在できる。
- Rollback未実施をPassと偽装せず、`NOT_RUN`として明示する。

将来、Platform構成変更、Release Gate強化、Cloud移行またはIncident Recovery Testが必要になった場合は、別のRollback Drillとして実施する。

## 9. Acceptance

```text
Public Demo Repository Implementation:
  ACCEPTED

Lightning Public Demo Manual Trial:
  ACCEPTED

Anonymous Access:
  ACCEPTED

Basic Preview Preservation:
  ACCEPTED

Public／Basic Access Separation:
  ACCEPTED

Cold Start:
  OBSERVED／approximately 2 minutes

Rollback:
  DEFINED／NOT_RUN／NON_BLOCKING
```

Phase 1-exのPublic Demo基盤は完了扱いとする。

次工程は、Public DemoではLoad／Callしない境界を維持したまま、Mac限定簡易Documentation RAGと将来External Environment Adapter Hookの要件・設計へ進む。
