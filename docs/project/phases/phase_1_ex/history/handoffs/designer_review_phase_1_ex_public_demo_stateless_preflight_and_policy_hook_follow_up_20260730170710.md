# Phase 1-ex Public Demo Stateless Preflight／Credential Isolation／Policy Hook Follow-up Review

```yaml
document_id: designer_review_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up
phase: phase_1_ex
status: implementation_accepted_with_publication_hygiene_follow_up
language: ja
created_at: 2026-07-30 17:07:10 JST
owner: 設計統括者役
reviewed_status: implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170041.md
source_review: designer_review_phase_1_ex_public_demo_minimal_access_and_runtime_portability_20260730161108.md
source_handoff: implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730161108.md
supersedes: null
lightning_external_operation: not_performed
```

## 1. Result

判定を実装、Lightning手動試験および公開文書衛生に分離する。

```text
F1 Stateless Public Preflight:
  RESOLVED／ACCEPTED

F2 Credential Isolation:
  RESOLVED／ACCEPTED

F3 Effective Optional Control Hook:
  RESOLVED／ACCEPTED

Basic Preview Compatibility:
  NO REGRESSION FINDING

Public Demo Repository Implementation:
  ACCEPTED

Lightning Public Demo Manual Trial:
  GO

Anonymous Public Activation:
  USER DECISION AFTER MANUAL TRIAL

Next GitHub／Public Documentation Sync:
  PUBLICATION HYGIENE CORRECTION REQUIRED
```

Repository実装はAcceptedとする。

前Reviewで指摘したF1からF3は、要求された境界を維持したまま解消されている。Basic Preview、Local Runtime、Model、Deployment Profile、RAGおよび実制限機能のScopeを拡張する変更は確認されなかった。

ユーザー担当によるLightning上の配置、起動、URL、Sleep／Wakeおよび匿名Accessの手動試験へ進める。

ただし、最新実装Statusに公開対象として不適切な実ユーザー由来の絶対Pathが1件あり、Project内に`.DS_Store`が2件存在する。実装合格とは分離し、次回GitHub／公開物同期前に明示承認を伴うPublication Hygiene処理が必要である。

## 2. Reviewed Sources

```text
docs/project/phases/phase_1_ex/history/handoffs/
  implementer_handoff_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730161108.md
  implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170041.md

scripts/runtime/lightning/
  public_demo_service.sh
  basic_preview_common.sh

src/margpa_runtime_llm/entrypoints/web/
  main.py

src/margpa_runtime_llm/web/
  app.py

tests/unit/runtime/
  test_lightning_basic_preview_service.py

tests/integration/web/
  test_web_app.py
```

## 3. F1 Review：Stateless Public Preflight

判定：Resolved／Accepted

`basic_preview_common.sh`は次の責務へ分離された。

```text
Core Configuration Resolution
Common Runtime／Artifact／Bind Checks
Lifecycle Configuration Resolution
Lifecycle State Safety Checks
```

Public Demoは`margpa_stateless_project_preflight`を使用し、Project、Platform、Python、uv、Web Entrypoint、Deployment Profile、Model Definition、Model Artifact、BindおよびPublic Access Profileの検査を維持する。

一方、Basic Preview専用の次のArtifactを解決・検査しない。

```text
Runtime State Root
PID
Log
Ownership Marker
Lifecycle Lock
```

既存の不正な`MARGPA_RUNTIME_STATE_ROOT`またはBasic Preview StateのPermission不整合がPublic Demoを阻害しないTestが追加されている。

Basic Previewは従来どおりLifecycle ConfigurationとState Safety Checkを通り、Fail Closed境界を維持している。

## 4. F2 Review：Credential Isolation

判定：Resolved／Accepted

`public_demo_service.sh`は、Common Script読込、`dirname`、Python、uvおよびWeb Entrypointを含む最初の子Processより前に、次のBasic Preview用Credential変数をPublic Script Process内から除外する。

```text
MARGPA_WEB_AUTH_MODE
MARGPA_WEB_AUTH_USERNAME
MARGPA_WEB_AUTH_PASSWORD
```

最終`exec env -u`もDefense in Depthとして維持されている。

Testでは、Public Demoの`dirname`、Python、uvおよび`margpa-web`子ProcessにCredential三項目が存在しないことを確認する。Basic PreviewではCredentialが必要な範囲で保持されるため、Public化のために既存Basic認証境界を弱化していない。

Credential値そのものをArgument、標準出力、ErrorまたはTest Evidenceへ出す変更は確認されなかった。

## 5. F3 Review：Effective Optional Control Hook

判定：Resolved／Accepted

Composition Rootで生成した`PublicControlPolicyPort`は`create_web_app`へInterface経由で注入され、Chat Request／Generation Lifecycleから次を呼び出す。

```text
check_request
before_generation
observe_generation
after_generation
```

`after_generation`は通常完了、Summary、Cancel、Error、Client DisconnectおよびGeneration開始失敗を含むTerminal Pathで1回だけ呼ばれるTestを持つ。

Request Validation失敗ではGeneration Hookへ到達しない。

現行`DisabledPublicControlPolicy`ではStreaming、Summary、Thinking、CancelおよびResponse内容を変更しない。

今回追加されたものは将来Control実装を差し込むためのPortとLifecycle Hookであり、Rate Limit、Budget、Quota、Cooldown、Token Cap、Cost GuardまたはPersistenceそのものではない。この境界は当初要求どおりである。

## 6. Verification

設計統括者役が実行した検証：

```text
Changed File SHA-512:
  Implementer Status記載値と6／6一致

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
  92 passed

Repository Full Suite:
  331 passed
  3 deselected

Ruff／Mypy／Shell／uv Lock:
  PASS
```

本ReviewではProject内外へTest CacheまたはTemporary Artifactを新規作成しないため、Pytestを再実行していない。Status作成時と現在Source／TestのSHA-512が一致し、Test Evidence対象にDriftがないことを確認した。

Model Smoke、Lightning External Trial、API Builder、Port、Public URL、Sleep／Wake、GitおよびGitHubは変更していない。

## 7. Publication Hygiene Findings

### P1. 最新実装Statusに実ユーザー由来の絶対Pathが1件ある

Severity: Publication Blocker

対象：

```text
implementer_status_phase_1_ex_public_demo_stateless_preflight_and_policy_hook_follow_up_20260730170041.md
line 358
```

外部`uv`の検証Pathとして、実ユーザーHomeを含む絶対Pathが記録されている。Secretではないが、公開名義分離および個人識別情報除外のProject方針と一致しない。

本Reviewでは、Append-only History、既存文書不変および無断変更禁止のため修正していない。また、本Review内へ対象値を複製していない。

次回GitHub／公開物同期前に、ユーザーの明示承認を得た上で、Privacy Scrub例外として匿名化し、変更理由、変更前Hashおよび変更後Hashを記録する必要がある。

### P2. `.DS_Store`が2件存在する

Severity: Publication Hygiene

検出位置：

```text
Project Root
docs/
```

本Reviewでは削除していない。

次回Backup／公開Copy／GitHub同期前のSanitation対象とする。削除対象の確定と実行は、ユーザーの明示承認後に行う。

## 8. Gate

```text
Basic Preview:
  KEEP

Mac Local Runtime:
  KEEP

Public Demo Repository:
  ACCEPTED

Lightning Public Demo Manual Trial:
  GO

Anonymous Public Activation:
  NOT YET DECLARED

GitHub／Public Documentation Sync:
  BLOCKED UNTIL P1／P2 ARE RESOLVED OR EXPLICITLY EXCLUDED
```

次はユーザー担当によるLightning Public Demo手動試験である。

手動試験でRepository実装とLightning環境の契約を確認した後、匿名公開を有効化するかをユーザーが判断する。

P1およびP2はLightning手動試験を妨げないが、次回GitHub／公開物同期前には解消または公開対象外化が必要である。勝手な修正、削除、移動、置換またはProject外操作は行わない。
