# Phase 1-ex Lightning Auto-start Go／No-Go Assessment 実装者Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment
phase: phase_1_ex
status: assessment_complete_review_pending
language: ja
created_at: 2026-07-27 05:08:52 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md
source_review: designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md
source_evidence: lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence_20260727003044.md
recommendation: defer
recommendation_is_final_decision: false
supersedes: null
```

## 1. Assessment Result

```text
Repository Auto-start Read-only Readiness:
  PASS

Lightning Basic Preview Manual Lifecycle:
  ACCEPTED

Traffic-aware Auto-start Platform Evidence:
  INCOMPLETE

Recommended Decision:
  DEFER

Final Decision Authority:
  USER／DESIGN GOVERNANCE
```

現時点では`DEFER`を提案する。

これはAuto-startが不成立という`NO_GO`判定ではない。Repository側の起動入口、Environment-only Secret境界、Health Contract、二重起動防止、CPU Basic PreviewおよびModel生成は成立している。

一方、Traffic-aware Auto-startの成立に必須な、現Accountでの機能可用性、Sleeping StudioのPublic URL AccessによるWake-up、Cold Start、Idle後の再Wake-up、URL維持およびCredit条件が未確認である。未確認項目をPassにできないため、`GO`または`CONDITIONAL_GO`を提案するEvidenceがまだ不足している。

## 2. Repository Read-only Assessment

確認対象：

```text
scripts/runtime/lightning/auto_start_preflight.sh
scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
tests/unit/runtime/test_lightning_basic_preview_service.py
```

確認結果：

|確認項目|結果|根拠|
|---|---|---|
|Traffic-aware Auto-start実装との誤認防止|PASS|PreflightはPlatform項目を`manual_required／not_run`として出力し、Platform変更を行わない|
|Project起動Command|PASS|`basic_preview_service.sh start`を単一入口として再利用可能|
|Environment／Profile／Model Path|PASS|Read-only Preflightで設定解決とPure CPU Profileを検査|
|Health Contract|PASS|`/healthz`のHTTP 200／`{"status":"ok"}`契約を検査|
|Secret境界|PASS|CredentialはEnvironmentからのみ継承し、Argument、PID、Log、Statusへ明示出力しない|
|二重起動防止|PASS|Atomic Lifecycle Lock、既存PID／Process Identity／Start Token確認を実装済み|
|Studio起動HookとTraffic-aware Wake-upの分離|PASS|Read-only Preflightは両者を別のManual項目として扱う|
|Basic Preview／Public Demo分離|PASS|`mode=basic_preview public_demo=false`を明示し、匿名Accessを有効化しない|
|Fail Closed|PASS|必須Path、Profile、Artifact、VersionまたはCredential不整合時は非0終了|

Production Auto-start HookまたはPlatform Adapterは現時点で追加していない。

## 3. Current Evidence Matrix

Status Vocabulary：

```text
pass
partial
fail
not_run
manual_required
unknown
```

|No.|必須項目|現在値|Evidence／不足|
|---:|---|---|---|
|1|API Builder／Public App／同等機能の利用可否|`unknown／manual_required`|現Account／OrganizationのUIまたは権限確認が未実施|
|2|Studio、Machine、Credit条件|`partial`|Linux x86_64 Pure CPUのBasic PreviewはAccepted。Auto-start機能の利用条件とWake-up時Creditは未確認|
|3|固定または再利用可能なPublic URL|`partial`|起動中Basic Previewの外部URLとBasic認証は確認済み。Sleep／Wake後の固定性・再利用性は未確認|
|4|Public URL AccessによるSleeping Studio Wake-up|`not_run／manual_required`|Traffic-aware Wake-up実験なし|
|5|Wake-up後のLifecycle Startup Command実行|`partial`|Repository入口はAccepted。Platform Hookからの実行は未確認|
|6|Model Load、SHA-512、`/healthz`正常化|`partial`|手動StartでModel生成とHealthはPASS。Wake-up経路でのArtifact Hash／Load／Healthは未確認|
|7|Cold Start時間|`not_run／manual_required`|計測値なし|
|8|Idle Sleep後の再Wake-up|`not_run／manual_required`|再Wake-up実験なし|
|9|Restart／Sleep／Wake後のURL維持|`not_run／manual_required`|Manual Lifecycle RestartはPASSだがPlatform URL維持試験ではない|
|10|Secret、Credential、内部Path非露出|`partial`|Repository出力、Basic認証境界、Evidence redactionはPASS。Platform Hook／Wake-up Log／Public Errorは未確認|
|11|CPU運用／GPU・Credit過剰消費回避|`partial`|Pure CPU Basic PreviewはPASS。Auto-start時のMachine選択とCredit消費条件は未確認|
|12|Studioへ張り付かず閲覧者が起動可能|`not_run／manual_required`|第三者Accessを契機とする無人Wake-up試験なし|

Repositoryだけで確定できる項目と、Lightning Platformでしか確定できない項目を分離した。`partial`は当該項目の一部Evidenceだけがあり、Auto-start Acceptanceを意味しない。

## 4. Platform Manual Checklist

### 4.1 Stage A：Read-only Availability Check

Platform設定を変更せず、Lightning UIまたはAccount表示で次を確認する。

1. API Builder、Public AppまたはTraffic-aware起動機能の表示有無。
2. 現Account／Organizationで利用可能か、Upgradeまたは追加権限が必要か。
3. 現StudioとLinux x86_64 Pure CPU Machineを対象にできるか。
4. Wake-up、起動時間、Machine時間またはPublic Appに関するCredit条件。
5. Public URLが固定、再利用可能またはSession単位のどれか。
6. Startup CommandまたはOn-start Actionを設定可能か。
7. Auto-sleep後のURL Access Wake-upをPlatformが明示的にSupportするか。

Evidenceへ記録するのは機能名、`available／unavailable／unknown`、制約の要約だけとする。Account ID、Organization ID、個人名、Private URL、CredentialまたはSecretを記録しない。

### 4.2 Stage B：Controlled Traffic-aware Trial

Stage Aで機能利用可能と確認し、設計統括者Reviewとユーザーの明示許可を得た後だけ実施する。

1. Basic Previewが停止状態であることを確認する。
2. Platform Hook候補からRepository Lifecycleの単一入口を呼ぶ。
3. StudioをSleep状態へ移す。
4. Studio Terminalへ接続しない別Browser／SessionからPublic URLへAccessする。
5. Access開始からStudio Wake-up、Process開始、`/healthz` 200までの時間を計測する。
6. Credentialなしで`401`、正しいManaged Secrets経由のCredentialで画面表示となることを確認する。
7. Model生成を1回行い、起動後のModel Loadを確認する。
8. Lifecycle Log、Platform Log、Browser ErrorおよびResponseにSecret、Credential、内部Pathがないことを確認する。
9. Idle Sleep後、同じURLで2回目のWake-upを行う。
10. Restart、SleepおよびWake後にURLが維持されるか確認する。
11. 二重AccessまたはStartup再実行でWeb Processが1件だけであることを確認する。
12. Machine種別とCredit消費がPreview用途の許容範囲か、ユーザーが判定する。

Stage BはPlatform Mutationを含み得るため、本Assessment Statusだけでは実施を許可しない。

## 5. Evidence Record Template

Private URLとSecret値を含めず、次の形式で記録する。

```text
checked_at_jst:
account_feature_available: pass|fail|unknown
feature_label:
machine_supported: pass|fail|unknown
machine_class: cpu|gpu|unknown
credit_condition_acceptable: pass|fail|unknown
public_url_issued: pass|fail|not_run
public_url_reusable: pass|fail|unknown
startup_command_supported: pass|fail|unknown
startup_command_executed: pass|fail|not_run
sleeping_studio_wake_up: pass|fail|not_run
cold_start_seconds:
healthz_200_after_wake: pass|fail|not_run
model_load_after_wake: pass|fail|not_run
artifact_hash_verified_after_wake: pass|fail|not_run
basic_auth_boundary_after_wake: pass|fail|not_run
idle_sleep_completed: pass|fail|not_run
second_wake_up: pass|fail|not_run
url_preserved_after_restart_sleep_wake: pass|fail|unknown
single_process_after_retries: pass|fail|not_run
secret_exposure_found: yes|no|not_run
internal_path_exposure_found: yes|no|not_run
viewer_can_trigger_without_studio_session: pass|fail|not_run
notes_without_private_identifiers:
```

未実施欄は空欄やPassにせず`not_run`または`unknown`とする。

## 6. Effort／Change Scope／Risk

### 6.1 Stage A

```text
Estimated Effort:
  15–30 minutes

Repository Change:
  NONE

Platform Mutation:
  NONE
```

### 6.2 Stage B

機能が既存Lifecycle入口を直接呼べる場合：

```text
Estimated Hands-on Effort:
  1–2 hours
  plus Platform idle／sleep waiting time

Repository Change:
  NONEまたはThin Hook／Testの必要最小限

Platform Change:
  USER-MANAGED／EXPLICIT AUTHORIZATION REQUIRED
```

Thin Hookが必要な場合の候補変更範囲：

```text
scripts/runtime/lightning/
tests/unit/runtime/test_lightning_basic_preview_service.py
```

実装前に、Hookの責務、File、Platform設定、RollbackおよびTestを定めた追加Handoffとユーザー許可を必要とする。

Platform専用Adapterまたは別Frameworkが必要な場合：

```text
Estimated Engineering Effort:
  1–3 days or more after design

Recommendation:
  Keep DEFER and reassess cost／benefit
```

主なRisk：

- Platform機能、権限またはUIがAccountごとに異なる。
- Public URL AccessだけでStudioをWake-upできない可能性がある。
- CPU Model LoadによりCold Startが長くなる。
- URLがSleep／Restart後に変わる可能性がある。
- Wake-up自体のRateをApplication側で制限できず、Credit消費を誘発し得る。
- Platform LogまたはErrorへ内部Pathが出る可能性がある。
- Hook再実行とManual Startが競合する可能性がある。RepositoryのAtomic Lockは二重Processを防止するが、Platform側Retry契約の確認は必要である。

## 7. Recommendation

推奨：

```text
DEFER
```

根拠：

1. Basic Previewを手動起動すれば現時点のPreview目的を満たせる。
2. Repository側に大きな欠陥や追加Dependency要求はない。
3. GO判定の核心であるTraffic-aware Wake-up、Cold Start、URL維持およびCredit条件が未確認である。
4. 未確認のPlatform機能を前提にHookやAdapterを先行実装すると、不要な工事になる可能性がある。
5. Stage Aは短時間・Read-onlyで実施でき、再評価条件を低Costで明確化できる。

### Reassessment Conditions

次が揃った時点で再評価する。

- Stage Aで現Account／StudioのTraffic-aware機能利用可能性が確認される。
- ユーザーがStage BのPlatform設定とControlled Trialを明示許可する。
- Sleep／Wake、Cold Start、URL維持、Creditおよび非露出Evidenceが記録される。

全条件が合格すれば`GO`、機能は成立するが時間・URL・Machine・Credit制約が残る場合は`CONDITIONAL_GO`を再検討する。

## 8. Repository Verification

```text
Assessment-focused Tests : 3 passed
Lifecycle Test           : 30 passed
Repository Full Suite    : 297 passed／3 deselected
Shell Syntax             : PASS
Ruff Check               : PASS
Ruff Format Check        : PASS／96 files
Mypy Strict              : PASS／91 source files
```

対象File SHA-512：

```text
bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d  scripts/runtime/lightning/auto_start_preflight.sh
1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58  scripts/runtime/lightning/basic_preview_common.sh
7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac  scripts/runtime/lightning/basic_preview_service.sh
df7998b9b7c2dbb537abc9a5c81bcb2c53f60df8afd949e6f46662efd13c161032dc1ff8bfce02568ac084029ec845c79a49400deb95f46000efbda7f5b9fbe5  tests/unit/runtime/test_lightning_basic_preview_service.py
```

HashはAccepted済みRepository／Lightning配置値と一致する。

通常SuiteではModel Smokeを実行していない。`3 deselected`をPassとして扱わない。

## 9. Scope Confirmation

変更File：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727050852.md
```

変更していないもの：

```text
scripts/
tests/
src/
config/
pyproject.toml
uv.lock
Current／Shared／Requirements／Architecture／ADR／Public Docs
```

Lightning Platform設定、API Builder、Public App、Port、Public URL、Managed Secrets、匿名Access、Dependency、Model、RAGおよびGitは変更していない。

## 10. Next User Manual Action

設計統括者Review後、ユーザーはまずSection 4.1のStage AだけをRead-onlyで実施する。

Stage Aの結果をEvidence Templateへ`pass／fail／unknown`で記録し、設計統括者役へ戻す。Stage BまたはAuto-start有効化は、Stage A結果に基づく別の明示許可まで行わない。

## 11. Review Gate

本Statusは判定根拠と`DEFER`提案を記録するが、Go／No-Goを最終確定しない。

設計統括者Reviewとユーザー決定前に、Auto-start Hook、Platform設定、Public URL変更、匿名Public Demoまたは後続実装へ進まない。
