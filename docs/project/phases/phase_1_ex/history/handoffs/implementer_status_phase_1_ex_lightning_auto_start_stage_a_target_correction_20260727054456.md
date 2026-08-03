# Phase 1-ex Lightning Auto-start Stage A Target Correction 実装者Status

```yaml
document_id: implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction
phase: phase_1_ex
status: stage_a_complete_stage_b_authorization_pending
language: ja
created_at: 2026-07-27 05:44:56 JST
owner: 実装者役
source_handoff: implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md
source_correction_review: designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md
supersedes: implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md
corrected_reason: incorrect_organization_context
decision_candidate: proceed_to_stage_b_after_explicit_authorization
decision_is_final: false
```

## 1. Correction

[前Stage A Status](implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md)は、対象Projectとは別のOrganization Contextを確認していた。

したがって、前Statusに記録した次のEvidenceと判定は本Projectへ適用しない。

```text
Out-of-Credits Studio Evidence:
  INVALID_FOR_TARGET

Sleeping／No Hardware Evidence:
  INVALID_FOR_TARGET

BLOCKED_WITH_RECHECK_CONDITION:
  WITHDRAWN

Credit復旧待ち:
  NOT REQUIRED BY CURRENT TARGET EVIDENCE
```

Append-only規則により前Statusは削除・上書きせず、本訂正Statusで対象誤りと無効範囲を明示する。

## 2. Correct Target

ユーザー再確認に基づく正しい対象：

```text
Organization:
  Nazuna-Research-Org

Teamspace:
  general

Studio:
  margpa-runtime-llm
```

Credential、Secret、Private URL、Account ID、支払情報または個人情報は記録していない。

## 3. Correct Stage A UI Evidence

### 3.1 Organization／Studio State

Organization Homeで次を確認した。

```text
Studio:
  margpa-runtime-llm

Plan／Class:
  Free

State:
  on

Machine:
  4 x CPU

Teamspace:
  general
```

Organization Credit表示：

```text
Total Credits:
  0.00
```

同時に対象Studioは`Free／on／4 x CPU`として実際に稼働していた。

判定：

```text
Current Free CPU Studio Operation:
  PASS

Current Studio Start Blocked by Credit:
  NO

Paid／Concurrent／Auto-start Credit Behavior:
  UNKNOWN／STAGE B EVIDENCE REQUIRED
```

Credit残高`0.00`だけからFree CPU StudioまたはTraffic-aware Wake Trialが実行不能と推定しない。Stage B中のCredit条件、同時利用条件およびWake-up Costは別途記録する。

### 3.2 Correct Studio Runtime

対象Studio画面で次を確認した。

```text
Organization:
  Nazuna-Research-Org

Teamspace:
  general

Studio:
  margpa-runtime-llm

Environment:
  4 x CPU

Studio UI:
  RUNNING／INTERACTIVE

Project Directory:
  PRESENT

Models Directory:
  PRESENT

Lightning Runtime Directories:
  PRESENT
```

Repository内容、Model内容、SecretまたはTerminal出力は変更・取得していない。

### 3.3 API Builder

対象Studioの`Install Studio plugins` → `Serving` Categoryで次を確認した。

```text
API builder
Create APIs for serverless use of your Studio
Install
```

別Organizationで表示された`Studio must be running to install plugin`制約は、稼働中の正しい対象Studioでは表示されなかった。

判定：

```text
API Builder visible:
  PASS

Serverless purpose stated:
  PASS

Studio running:
  PASS

Install option presented:
  PASS

API Builder installed:
  NO／NOT_RUN
```

InstallはPlatform Mutationであり、今回のStage Aでは実行していない。

### 3.4 Deploy Surface

正しい対象Studioでも上部`Deploy` Dialogは次の表示だった。

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

上部Deploy Surfaceの`Autoscale／Serverless`は利用不可だが、Serving Plugin Categoryの`API builder`はInstall候補として存在する。

Stage B候補は、公式Docsが案内し、現UIにも存在するAPI Builder Plugin経路とする。両Surfaceを同一機能として扱わない。

## 4. Correct Stage A Evidence Matrix

|確認項目|訂正後結果|Evidence／残条件|
|---|---|---|
|正しいOrganization／Studio|`pass`|Nazuna-Research-Org／general／margpa-runtime-llm|
|Current Studio稼働|`pass`|Free／on／4 x CPU|
|API Builder表示|`pass`|Serving CategoryにInstall候補あり|
|API BuilderのServerless用途|`pass`|UIに`Create APIs for serverless use of your Studio`|
|API Builder Install|`not_run`|Platform Mutationのため未実行|
|Current CreditによるStudio Block|`no`|Credit表示0.00だがFree CPU Studioは稼働中|
|Auto-start Credit条件|`unknown`|Stage Bで要確認|
|Public URL発行／再利用|`not_run`|API Builder未Install|
|Startup Command設定|`not_run`|Stage B許可待ち|
|第三者URL Access Wake-up|`not_run`|Stage B必須|
|Cold Start／再Wake／URL維持|`not_run`|Stage B必須|
|Secret／内部Path非露出|`not_run_for_stage_b`|Repository／Manual Basic Preview EvidenceはAccepted済み|

## 5. Decision Flow

訂正後のStage A結果：

```text
Feature Candidate:
  AVAILABLE

Correct Studio:
  RUNNING

API Builder:
  INSTALL CANDIDATE AVAILABLE

Stage A:
  PASS

Stage B:
  REQUIRED／EXPLICIT AUTHORIZATION PENDING
```

Corrected Decision Candidate：

```text
PROCEED_TO_STAGE_B_AFTER_EXPLICIT_AUTHORIZATION
```

これはTraffic-aware Auto-startの`GO`判定ではない。Stage BでUser Requirementを実際に確認するまで最終判定しない。

## 6. Stage B Preconditions

Stage B開始前に必要：

1. 設計統括者役による本訂正StatusのReview。
2. API Builder Plugin Install、Startup Command設定、Public URL発行およびSleep／Wake試験を含むStage B Handoff。
3. ユーザーの明示許可。
4. 変更対象、Rollback、Managed Secrets、Basic認証、Evidence記録および停止条件の確定。

Stage B Acceptance：

```text
Owner Browser／Studio Tab／Terminal:
  CLOSED／NOT REQUIRED

Trigger:
  THIRD-PARTY VIEWER OPENS PUBLIC URL

Required:
  Studio wakes
  Repository Lifecycle starts
  Model loads
  /healthz = HTTP 200
  Basic Authentication remains effective
  Viewer can generate
  Second sleep／wake succeeds
  URL／Cold Start／Credit／Non-exposure recorded
```

## 7. Scope Confirmation

Repository Code変更：

```text
NONE
```

追加File：

```text
docs/project/phases/phase_1_ex/history/handoffs/
implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md
```

実施していない操作：

```text
Add Credits／Purchase
Studio Start／Stop
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

## 8. Review Gate

前Stage A Statusの対象誤りと`BLOCKED_WITH_RECHECK_CONDITION`を、本訂正Statusにより無効化する。

設計統括者Reviewとユーザーの明示許可前に、Stage B、API Builder Install、Startup Command設定、Public URL発行またはAuto-start有効化へ進まない。
