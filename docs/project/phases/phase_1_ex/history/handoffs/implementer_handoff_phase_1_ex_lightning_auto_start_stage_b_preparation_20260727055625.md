# 実装担当向け Phase 1-ex Lightning Auto-start Stage B Preparation Handoff

```yaml
document_id: implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation
phase: phase_1_ex
status: accepted_ready_for_repository_preparation
language: ja
created_at: 2026-07-27 05:56:25 JST
owner: 設計統括者役
target_role: 実装者役
platform_operator: user
supersedes: null
```

## 1. Objective

Lightning API Builderを候補経路として、Stage B Unattended External Wake Trialをユーザーが安全に手動実施できるよう、Repository側の起動入口、Test、Command Template、Rollback、Evidence TemplateおよびUser Manual Actionを準備する。

本Handoffが許可するのはRepository側Preparationだけである。

Lightning上の次の操作はすべてユーザーが手動で行う。

```text
Plugin Install
API Builder設定
Startup Command入力
Port／Health設定
Public URL発行
Studio Sleep
Owner Session終了
Third-party相当Browser試験
Rollback操作
```

実装者役はLightning UI、Platform設定、Managed Secrets、Public URLまたはStudio状態を変更しない。

## 2. Authoritative References

- [ADR-0025](../../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [ADR-0026](../../adr/adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets_ja.md)
- [Public Demo／Auto-start要件](../../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Architecture](../../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Auto-start Requirement Alignment Correction](designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md)
- [Stage A Target Correction Status](implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md)
- [Stage A Accepted Review](designer_review_phase_1_ex_lightning_auto_start_stage_a_availability_and_target_correction_20260727054823.md)
- [Lightning Basic Preview Manual Lifecycle Review](designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Task Role／Write Authority](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Phase 1-ex Index](../../phase_index_ja.md)

Conflict時は日本語正本、ADR、Requirements、Architecture、訂正Review、本Handoffの順に確認する。ユーザーの明示した無人Wake-up条件を弱化しない。

## 3. Established State

```text
Correct Target:
  Nazuna-Research-Org／general／margpa-runtime-llm

Free CPU Studio:
  RUNNING

API Builder:
  VISIBLE／INSTALL CANDIDATE

Basic Preview Lifecycle:
  ACCEPTED_AS_PREREQUISITE

Stage A:
  ACCEPTED／PASS

Stage B:
  REQUIRED／REPOSITORY PREPARATION ONLY

Traffic-aware Auto-start:
  PENDING STAGE B

Anonymous Public Demo:
  DISABLED
```

## 4. Mandatory User Requirement

Stage Bの中核Acceptance Condition：

```text
Studio:
  SLEEPING

Owner Browser／Studio Tab／Terminal／SSH:
  CLOSED／NOT REQUIRED

Trigger:
  THIRD-PARTY VIEWER OPENS PUBLIC URL

Required Result:
  Lightning wakes the Studio
  Repository foreground entrypoint starts
  Model loads
  /healthz becomes HTTP 200
  Basic Authentication remains active
  Viewer can generate
```

OwnerがStudioを別操作で起動する、Terminalを開く、Browser Tabを維持する、または閲覧者のAccessに合わせて手動対応する構成は不合格とする。

## 5. Foreground Entrypoint Decision

API Builderの起動Commandは原則として次を使用する。

```bash
bash scripts/runtime/lightning/basic_preview_service.sh run
```

理由：

- `run`はForegroundで実行する。
- `run`は内部で`exec margpa-web`する。
- Platform側がProcessの生存、Signal、RestartおよびCold Startを監視できる。
- CredentialとRuntime前提を起動前に検査する。
- Background PID／Log／Lifecycle LockをPlatform Process管理と二重化しない。

次はAPI Builder起動Commandとして使用しない。

```bash
bash scripts/runtime/lightning/basic_preview_service.sh start
```

`start`はManual Terminal向けBackground Lifecycleであり、親Commandが終了する。API BuilderがServer Process終了と誤認する可能性がある。

## 6. Authorized Repository Work

### 6.1 Entrypoint Compatibility Assessment

既存`run`で次を満たすか確認する。

- API BuilderのWorking DirectoryからProjectを解決できる。
- `MARGPA_WORKSPACE_ROOT`を解決できる。
- `MARGPA_PROJECT_ROOT`を解決できる。
- `MARGPA_MODEL_ROOT`を解決できる。
- `MARGPA_UV_BIN`を解決できる。
- `MARGPA_ENV_PREFIX`を解決できる。
- `MARGPA_WEB_PROFILE`を解決できる。
- Hostを`0.0.0.0`へ設定できる。
- API Builderが指定するPortまたは`MARGPA_WEB_PORT`へBindingできる。
- Managed Secrets由来CredentialをEnvironmentから受け取れる。
- `MARGPA_RUNTIME_STATE_ROOT`を明示設定せずに動作できる。

API Builderが`PORT`等のPlatform Environment Variableを提供する場合は、既存`MARGPA_WEB_PORT`とのMappingを明示する。Platform Contractを確認できない段階でVariable名を推測してProduction Codeへ埋め込まない。

### 6.2 Thin Entrypoint

既存`run`だけではProject Root、Platform PortまたはEnvironment解決を安全に再現できない場合に限り、薄いEntrypointを追加できる。

候補：

```text
scripts/runtime/lightning/api_builder_basic_preview_entrypoint.sh
```

要件：

- Repository Lifecycleの`run`へ`exec`するだけの薄いAdapter。
- Model Load、Web Serverまたは認証処理を重複実装しない。
- Secret値をArgument、Log、FileまたはStatusへ出さない。
- Project固有の個人PathをHard-codeしない。
- 不足EnvironmentをFail Closedする。
- `MARGPA_RUNTIME_STATE_ROOT`を設定しない。
- Platform Signalを`margpa-web`へ伝播する。
- Background化しない。
- Install、Build、Network AccessまたはPlatform変更を行わない。

不要なら新Scriptを作らず、既存`run`を採用した理由をStatusへ記載する。

### 6.3 Command Template

ユーザーがAPI Builder UIへ入力するCommand Templateを作る。

Templateは次を含む。

- Working Directory前提
- Entrypoint
- Host
- Port
- Pure CPU Profile
- Model Root
- `.venv`
- Project-local `uv`
- Basic Auth Mode
- Managed SecretsのEnvironment Variable名
- Health Path

Credential実値、Private URL、Account IDまたは個人Pathは含めない。

Environment VariableをCommand Lineへ列挙するとSecret露出の危険がある場合は、Platform Environment／Managed Secrets継承を使用し、Commandには値を書かない。

### 6.4 Preflight／Test

最低限次を検証する。

- `run`またはThin EntrypointがForegroundのままServerへ`exec`する。
- Missing Environmentで非0終了する。
- Credentialの空白、Username禁止文字および不足値を拒否する。
- Credential値をStdout／Stderrへ出さない。
- `MARGPA_RUNTIME_STATE_ROOT`を明示Overrideしない。
- Background PID／Log／Lockを作らない。
- Platform Port Mappingを設定した場合に正しいPortへ渡す。
- Signalを子Processへ伝播できる。
- Project Root以外からの起動Contractが明示される。
- Existing Basic Preview `start／stop／restart`を破壊しない。
- API Builder Preparation CommandがPackage Install、BuildまたはNetwork Accessを行わない。

Model不要のTestを優先する。

## 7. User-operated Lightning Actions

実装担当Statusが設計統括者ReviewでAcceptedされた後、ユーザーが次を手動実施する。

### 7.1 Installation／Configuration

1. 正しいOrganization／Teamspace／Studioを確認する。
2. API Builder PluginをInstallする。
3. APIを新規作成する。
4. AcceptedされたForeground Commandを設定する。
5. Portを設定する。
6. Health Pathを`/healthz`へ設定できる場合は設定する。
7. Managed SecretsがProcess Environmentへ注入されることを確認する。
8. Basic Auth Modeを設定する。
9. Public URLを発行する。

UI Labelまたは設定項目が想定と異なる場合は、推測で進めずScreenshotまたは項目名だけを設計統括者へ戻す。

### 7.2 First Wake Trial

1. Manual Basic Previewを停止する。
2. Port `8000`または採用Portに既存Listenerがないことを確認する。
3. StudioをSleepさせる。
4. Owner Browser／Studio Tab／Terminal／SSHをすべて終了する。
5. 別Accountまたは第三者相当のPrivate BrowserからPublic URLを開く。
6. Public URL Access開始時刻を記録する。
7. Login PromptまたはApplication表示までの時間を記録する。
8. Basic認証なし／誤Credentialが拒否されることを確認する。
9. 正しいCredentialで画面を開く。
10. 短い生成を一回実行する。
11. `/healthz`が`200`であることを確認する。

### 7.3 Second Wake Trial

1. Application未使用状態にする。
2. Studioが再度Sleepしたことを確認する。
3. Owner Sessionを開かない。
4. 同じPublic URLを別Sessionから開く。
5. URL Accessだけで二回目のWake-upが成立することを確認する。
6. 同じURLが維持されるか確認する。
7. Basic認証と生成を再確認する。

## 8. Evidence Requirements

次をPrompt本文、Credential実値、Private URLまたは個人識別情報なしで記録する。

```text
checked_at_jst:
correct_target_confirmed:
api_builder_installed:
api_created:
foreground_entrypoint:
platform_port:
health_path:
studio_sleep_confirmed:
owner_sessions_closed:
third_party_url_trigger_only:
first_wake_pass:
first_cold_start_seconds:
healthz_200_after_first_wake:
basic_auth_after_first_wake:
model_generation_after_first_wake:
second_sleep_confirmed:
second_wake_pass:
second_cold_start_seconds:
same_url_preserved:
single_process_confirmed:
credit_before:
credit_after:
secret_exposure_found:
internal_path_exposure_found:
rollback_required:
notes_without_private_identifiers:
```

未実施項目をPassにしない。

## 9. Security／Privacy

- Basic認証を維持する。
- API Builder経路で匿名Public Demoへ切り替えない。
- Managed Secrets値をCommand、Docs、Log、ScreenshotまたはStatusへ記録しない。
- `/healthz`は最小情報だけを返す。
- Prompt／回答の永続保存を追加しない。
- Tool、RAG、Agent、External I/Oを追加しない。
- ErrorへCredential、Secret、Stack Traceまたは不要な内部Pathを出さない。
- Public URLそのものは内部Historyへ保存しない。

## 10. Rollback

Stage B開始前に、ユーザーが実行できるRollback手順をStatusへ明記する。

最低限：

1. API BuilderのAPIを停止または無効化する。
2. Public URLの公開を停止する。
3. Startup Commandを削除または無効化する。
4. 必要ならAPI Builder PluginをUser操作でRemoveする。
5. Foreground Processが停止したことを確認する。
6. Manual Basic Previewの既存Lifecycleが引き続き使えることを確認する。
7. Managed Secretsは削除せず、必要性をユーザーが判断する。

削除、RemoveまたはPublic設定変更はユーザーだけが実行する。

## 11. Stop Conditions

次の場合は推測で続行せず停止する。

- API Builder UIがDocs／Stage A Evidenceと大きく異なる。
- Foreground Commandを設定できない。
- Managed SecretsをProcessへ継承できない。
- Basic認証を維持できない。
- API Builderが独自Frameworkまたは別Artifact形式を必須とする。
- Public URL AccessではStudioがWake-upしない。
- Owner Sessionが必要になる。
- Secret、Credentialまたは内部Pathが露出する。
- 予期しない課金、Credit消費またはMachine変更が発生する。
- 同時起動で複数Processが残る。
- Rollback方法が不明。

停止時はPlatform状態をむやみに変更せず、観測結果をユーザーと設計統括者へ戻す。

## 12. Write Authority

実装者役が書き込める場所：

```text
scripts/runtime/lightning/                  # 必要最小限
tests/unit/runtime/                         # 必要最小限
docs/project/phases/phase_1_ex/history/handoffs/
```

Read-only：

```text
config/
src/
pyproject.toml
uv.lock
docs/project/current/
docs/public/
docs/project/shared/
docs/project/phases/phase_1_ex/adr/
docs/project/phases/phase_1_ex/architecture/
docs/project/phases/phase_1_ex/requirements/
```

`config/`、`src/`、DependencyまたはModel変更が必要な場合は、追加許可前に変更しない。

## 13. Explicitly Prohibited

- 実装者役によるLightning UI操作
- Plugin Install／Remove
- API Builder作成
- Startup Command設定
- Studio Sleep／Wake
- Public URL発行／変更／保存
- Managed Secrets変更
- Add Credits／Purchase
- Anonymous Public Demo
- RAG、Tool、Agent、Guardrail、Judge
- Dependency Install／Native Build
- Model Download／変更
- Git初期化、Commit、Push、GitHub操作
- 既存Docsの削除または上書き

## 14. Deliverables

実装担当は次を提出する。

1. Existing `run` Compatibility Assessment
2. 採用Entrypointと理由
3. 必要ならThin EntrypointとUnit Test
4. API Builder Command Template
5. User Manual Stage B手順
6. Rollback手順
7. Stop Conditions
8. 実行したRepository Test
9. 変更FileとSHA-512
10. 未確認Platform項目
11. 実装者Status

Status：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_YYYYMMDDHHMMSS.md
```

## 15. Acceptance Conditions

1. Foreground Entrypointが明確である。
2. API Builderに`start`ではなく`run`またはAccepted Thin Entrypointを使用する。
3. Secret値をCommand、Log、File、StatusまたはDocsへ出さない。
4. Platform Port／Health Contractが明確である。
5. User-operated手順が正しい対象を固定している。
6. Owner Session完全不在条件を弱化していない。
7. 二回のSleep／Wake Trialを要求している。
8. Basic認証、Model Load、Healthおよび生成を確認する。
9. Credit、Cold Start、URL維持、単一Processおよび情報非露出を記録する。
10. RollbackとStop Conditionsがある。
11. Platform変更を実装者が行っていない。
12. Git、RAG、Public DemoまたはDependency変更を行っていない。
13. Repository Testが合格している。
14. Append-only Statusを作成している。

## 16. Review／Execution Gate

実装者Status完成後、設計統括者役がRepository変更、Command、Test、User Manual、RollbackおよびScopeをReviewする。

Review Accepted後、ユーザーがLightning上のStage B手動作業を行う。

このHandoff自体はStage BのPlatform Mutationを許可しない。

## 17. Start Condition

実装担当は、本Handoffの範囲内でRepository Preparationへ着手できる。

Lightning上の操作は一切行わず、ユーザーが一括して手動実行できる状態を作る。
