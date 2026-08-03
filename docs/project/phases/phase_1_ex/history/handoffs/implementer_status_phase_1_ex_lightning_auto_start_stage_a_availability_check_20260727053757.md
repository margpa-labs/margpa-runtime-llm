# Phase 1-ex Lightning Auto-start Stage A Availability Check 実装者Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check
phase: phase_1_ex
status: stage_a_complete_stage_b_blocked
language: ja
created_at: 2026-07-27 05:37:57 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md
source_correction_review: designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md
extends: implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727050852.md
decision_candidate: blocked_with_recheck_condition
decision_is_final: false
supersedes: null
```

## 1. Result

Stage A Read-only Availability Checkを、Lightning AI Studioの現Account／現Studio UIとLightning公式Docsに対して実施した。

```text
Stage A:
  COMPLETE

API Builder Feature:
  VISIBLE／AVAILABLE FOR INSTALLATION

Traffic-aware Serverless Direction:
  SUPPORTED BY OFFICIAL DOCUMENTATION

Current Studio Credit State:
  OUT_OF_CREDITS

Current Studio Runtime:
  SLEEPING／NO HARDWARE

Stage B:
  BLOCKED

Decision Candidate:
  BLOCKED_WITH_RECHECK_CONDITION
```

現時点の状態を`DEFER`または`NO_GO`として最終化しない。機能候補は現Account UIに存在するが、Credit不足により対象Studioを起動できず、Plugin Install、Public URL設定およびUnattended External Wake Trialへ進めないためである。

## 2. User Requirement Alignment

必須Acceptance Conditionは次である。

```text
Studio:
  SLEEPING

Owner Browser／Studio Tab／Terminal:
  CLOSED／NOT REQUIRED

Trigger:
  THIRD-PARTY VIEWER OPENS PUBLIC URL

Required Result:
  Studio wakes
  Repository Lifecycle entry starts
  Model loads
  /healthz returns HTTP 200
  Basic Authentication remains active
  Viewer can use MARGPA
```

手動Basic Previewは前提技術としてAcceptedを維持するが、Traffic-aware Auto-startの代替Acceptanceには使用しない。

## 3. Read-only UI Evidence

確認対象：

```text
Lightning Organization／Teamspace:
  Current signed-in context

Studio:
  MARGPA-RUNTIME-LLM

Machine indication:
  4 x CPU
```

### 3.1 Current Studio State

Studio UI表示：

```text
The Studio is sleeping because you're out of credits
```

別Panel表示：

```text
No hardware found
This app doesn’t have hardware at the moment
```

判定：

```text
Studio Sleeping:
  PASS／OBSERVED

Credits Available:
  FAIL／OUT_OF_CREDITS

Hardware Active:
  NO
```

`Add credits to turn on`は表示されたが、Click、購入、支払情報入力またはCredit変更は行っていない。

### 3.2 API Builder Availability

`Install Studio plugins`の`Serving` Categoryで次を確認した。

```text
API builder
Create APIs for serverless use of your Studio
Install
```

Install Controlには次の制約が表示された。

```text
Studio must be running to install plugin
```

判定：

```text
API Builder listed in current Account／Studio UI:
  PASS

Serverless purpose stated in UI:
  PASS

API Builder installed:
  NO／NOT_RUN

Installation currently possible:
  NO／STUDIO SLEEPING OUT OF CREDITS
```

InstallはPlatform Mutationであり、本Stage Aでは実行していない。

### 3.3 Deploy Surface

Studio上部の`Deploy` Dialogで次を確認した。

```text
Scheduled:
  Time-based

Autoscale:
  Coming soon
  Serverless / best for most

Docker:
  Coming soon

Reserved VM:
  Coming soon
```

Dialog内の`Deploy` ButtonはDisabledだった。

このDeploy Surfaceの`Autoscale／Serverless`は現UIでは利用不可である。一方、Serving Plugin Categoryには別経路として`API builder`がInstall候補として存在する。両者を同一機能として断定せず、Stage B候補は公式Docsが案内するAPI Builder Plugin経路とする。

### 3.4 Web App Plugins

`Web apps` Categoryでは次を確認した。

```text
Port viewer:
  INSTALLED

Gradio:
  INSTALL CANDIDATE

Streamlit:
  INSTALL CANDIDATE

React:
  INSTALL CANDIDATE
```

本Projectは既存Web ApplicationとLifecycle Scriptを使用するため、Gradio、StreamlitまたはReactの追加をStage A結果から自動許可しない。

## 4. Official Documentation Evidence

Lightning公式Docsの現行検索結果を確認した。

### 4.1 Expose Web Apps

[Lightning Expose web apps](https://lightning.ai/docs/overview/host-web-apps/expose-web-apps)は次を案内している。

- StudioへAPI Builder PluginをInstallする。
- APIを作成し、Server起動Commandを設定する。
- Public URLからWeb AppへAccessする。
- Serverlessでは未使用時にStudioがSleepする。
- User RequestでStudioがWake-upする。
- Auto startを有効化すると、Public URL訪問までStudioをSleep状態にできる。

### 4.2 On-start Actions

[Lightning On-start actions](https://lightning.ai/docs/overview/ai-studio/on-start-actions)は、Studio Home配下の`.lightning_studio/on_start.sh`がStudio起動ごとに自動実行され、Web Server等を開始できると説明している。

`on_start.sh`はStudio起動後のHookであり、Public URL AccessによるWake-up機能そのものとは区別する。

### 4.3 Auto Sleep

[Lightning Auto sleep](https://lightning.ai/docs/overview/ai-studio/auto-sleep)は、Idle Studioが自動Sleepし、EnvironmentとDataがSleep／Wake Cycle間で保持されると説明している。

Server Process稼働中にStudioがIdleと判定されるか、API Builder経路でSleepへ移行する条件はStage Bで確認する。

### 4.4 Host Demos

[Lightning Host demos](https://lightning.ai/docs/overview/host-web-apps/host-demos)は、CPU Demo、Auto-start、第三者のDemo URL AccessによるStudio Wake-upおよびCold Start Delayを説明している。

公式DocsはUser Requirementと方向上整合する。ただし、現Account／Studioでの実動作はStage B AcceptanceなしにPassとしない。

## 5. Stage A Evidence Matrix

|確認項目|結果|Evidence／残条件|
|---|---|---|
|API Builder／同等機能の表示|`pass`|Serving CategoryにAPI Builderを確認|
|現Account UI上のInstall候補|`pass`|Install Controlを確認。未実行|
|CPU Studioへの適用候補|`partial`|対象Studioは4 x CPU。Plugin Install／動作は未確認|
|Public URLとAuto-startの関係|`partial`|公式DocsでSupport。現Studioで未設定・未試験|
|Startup Command設定|`partial`|API Builder Commandと`on_start.sh`を公式Docsで確認。現Studioでは未設定|
|Free／Credit条件|`fail／blocked`|現UIがOut of Creditsを明示|
|URL Access Wake-upのPlatform提供|`partial`|公式DocsでSupport。現Accountの実動作は未試験|
|Deploy Autoscale／Serverless|`unavailable`|現Deploy DialogでComing soon|
|Current Public URLの再利用性|`unknown`|Stage B未実施|
|Owner不在の第三者Wake-up|`not_run`|Stage B必須|

`partial`は機能説明または入口の存在だけを示し、実環境Acceptanceを意味しない。

## 6. Correct Decision Flow

今回のStage A結果：

```text
Feature Candidate:
  AVAILABLE

Immediate Stage B Execution:
  BLOCKED_BY_CREDITS
```

したがって判定候補は次とする。

```text
BLOCKED_WITH_RECHECK_CONDITION
```

Recheck Condition：

1. 対象Studioを起動可能なCredit／Free Allowance状態へ戻す。
2. Stage AのAPI Builder表示とInstall可否を再確認する。
3. Stage B Platform Mutation、Plugin Install、Startup Command設定およびPublic URL試験について、設計統括者Reviewとユーザーの明示許可を得る。

Credit復旧後にAPI Builderを利用できない場合は、現Account／Studioに対する`NO_GO`または別Path設計を検討する。

Credit復旧後に利用可能なら、Stage Bを省略せずUnattended External Wake Trialへ進む。

## 7. Required Stage B Scope

Stage Bで最低限必要な作業：

1. API Builder PluginのInstallまたはAcceptedされた同等経路の設定。
2. Repository Lifecycle単一入口を呼ぶStartup Commandの設定。
3. Basic Previewを停止してStudioをSleepさせる。
4. Owner Browser、Studio TabおよびTerminalを閉じる。
5. 第三者相当SessionからPublic URLだけを開く。
6. Studio Wake-up、Model Load、`/healthz`、Basic認証および生成を確認する。
7. 再Sleep後に同じURLで2回目のWake-upを確認する。
8. URL維持、Cold Start、Credit、単一Processおよび情報非露出を記録する。

Stage BはPlugin Install、Command設定およびPublic URL操作を含むため、今回のStage A許可では実行しない。

## 8. Repository／Platform Change Confirmation

Repository Code変更：

```text
NONE
```

追加したRepository File：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md
```

実施していない操作：

```text
Add Credits／Purchase
Studio Start
Plugin Install／Remove
Deploy
API Builder作成
Startup Command変更
Port／Public URL変更
Managed Secrets変更
Basic認証変更
Anonymous Public Access
Dependency／Model／RAG
Git／GitHub
```

Credential、Secret、Private URL、Account ID、Organization ID、個人情報および支払情報は記録していない。

## 9. Next User Action

本Statusの設計統括者Review後、ユーザーがCredit状態の復旧方法を決定する。

```text
Option:
  Free Allowance／Monthly Resetを待つ
  または
  User自身の判断でCreditを追加する
```

Credit追加は購入を伴い得るため、実装者役は実行しない。

Studio起動可能状態へ戻った後、Stage B開始前に新しいHandoffとユーザーの明示許可を得る。

## 10. Review Gate

本StatusはStage A Evidenceと`BLOCKED_WITH_RECHECK_CONDITION`候補を記録するが、Traffic-aware Auto-startの最終判定を行わない。

設計統括者Reviewとユーザーの明示許可前に、Stage B、Plugin Install、Platform設定、Public URL変更またはAuto-start有効化へ進まない。
