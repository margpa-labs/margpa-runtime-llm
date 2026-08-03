# Phase 1-ex Lightning Auto-start Stage A Availability／Target Correction Review

```yaml
document_id: designer_review_phase_1_ex_lightning_auto_start_stage_a_availability_and_target_correction
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-27 05:48:23 JST
owner: 設計統括者役
reviewed_status:
  - implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md
  - implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md
```

## 1. Review結論

正しい対象に対するStage A Read-only Availability CheckをAcceptedとする。

```text
First Stage A Status:
  INVALID_FOR_TARGET／SUPERSEDED

Target Correction Status:
  ACCEPTED

Correct Target Stage A:
  PASS

API Builder Candidate:
  AVAILABLE FOR INSTALLATION

Stage B Unattended External Wake Trial:
  REQUIRED／AUTHORIZATION_PENDING

Traffic-aware Auto-start:
  NOT YET GO
```

初回Statusは別Organization Contextを対象としていたため、本Projectの判定根拠として使用しない。

最新のTarget Correction Statusは対象誤りをAppend-onlyで明示し、誤ったCredit Block判定を撤回したうえで、正しいOrganization／Teamspace／StudioのEvidenceへ置き換えている。

## 2. Correct Target

確認対象：

```text
Organization:
  Nazuna-Research-Org

Teamspace:
  general

Studio:
  margpa-runtime-llm

Machine:
  4 x CPU

Studio State:
  Free／on／running
```

Organization Credit表示が`0.00`であっても、対象Free CPU Studioは実際に稼働している。そのため、Credit表示だけを根拠にStage B不能と判断しない訂正は妥当である。

## 3. Stage A Evidence

正しい対象Studioで次が確認されている。

```text
API Builder visible:
  PASS

UI description:
  Create APIs for serverless use of your Studio

Install option:
  PRESENT

API Builder installed:
  NO／NOT_RUN

Current Free CPU Studio:
  RUNNING
```

上部Deploy Dialogの`Autoscale／Serverless`は`Coming soon`である一方、Serving Plugin CategoryにはAPI BuilderがInstall候補として存在する。

両Surfaceを同一機能と断定せず、公式Docsが案内するAPI Builder経路をStage B候補とした整理は正しい。

## 4. User Requirement Alignment

最新Statusは必須Acceptance Conditionを維持している。

```text
Owner Browser／Studio Tab／Terminal:
  CLOSED／NOT REQUIRED

Trigger:
  THIRD-PARTY VIEWER OPENS PUBLIC URL

Required Result:
  Studio wakes
  Repository Lifecycle starts
  Model loads
  /healthz = HTTP 200
  Basic Authentication remains active
  Viewer can generate
  Second sleep／wake succeeds
```

手動Basic PreviewをTraffic-aware Auto-startの代替にしていない。

## 5. Scope Review

Repository Code変更：

```text
NONE
```

追加文書：

```text
implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md
implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md
```

実施されていない操作：

- Add Credits／Purchase
- Studio Start／Stop
- Plugin Install／Remove
- Deploy
- API Builder作成
- Startup Command変更
- Port／Public URL変更
- Managed Secrets変更
- Basic認証変更
- 匿名Public Access
- Dependency／Model／RAG
- Git／GitHub

Stage AのRead-only Scopeを逸脱していない。

## 6. SHA-512 Review

Status：

```text
First Stage A Status:
  d36bc9909dbeb32e2c1ee5f105efa5c6adc0c17019c6128d46d58b42609c1662be4254c6156db41434f3e57809fbed6114d16caa131acc79d0f24ef663dd3fe8

Target Correction Status:
  39a40c5e58577e62c1a0e077b7055c1161db866d93dfd27f60de53d589783d028612d2c5fdf7b7cdd6068dea135fb2877f3ff303224454dbdbd4b1cb48dd8a8d
```

Accepted済みScript／Testは変化していない。

```text
auto_start_preflight.sh:
  bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d

basic_preview_common.sh:
  1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58

basic_preview_service.sh:
  7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac

test_lightning_basic_preview_service.py:
  df7998b9b7c2dbb537abc9a5c81bcb2c53f60df8afd949e6f46662efd13c161032dc1ff8bfce02568ac084029ec845c79a49400deb95f46000efbda7f5b9fbe5
```

Code変更がないため、前Accepted時の`30 passed`、Full Suite `297 passed／3 deselected`、Ruff、MypyおよびShell Syntax結果を継承できる。

## 7. Findings

### Blocking Finding

なし。

### Correctly Remaining Unknowns

- API Builder Pluginの実Install
- API作成
- Startup Command設定
- Public URL発行と再利用性
- 第三者URL AccessによるWake-up
- Cold Start
- 二回目のSleep／Wake
- URL維持
- Auto-start時のCredit条件
- Platform Log／ErrorのSecret・内部Path非露出

これらはStage Bで確認すべき項目であり、Stage Aで偽Passにしていない。

## 8. Decision

```text
Stage A:
  ACCEPTED／PASS

Proceed Direction:
  DESIGN STAGE B HANDOFF

Stage B Execution:
  USER EXPLICIT AUTHORIZATION REQUIRED

Traffic-aware Auto-start Final Decision:
  PENDING STAGE B
```

## 9. Next Gate

次はStage B専用Handoffを作成する。

Handoffでは最低限次を固定する。

- API Builder Install対象
- Startup Command
- Repository Lifecycle入口
- Managed Secrets継承
- Basic認証維持
- Public URL
- Sleep／Wake試験
- Owner Session完全不在条件
- 第三者相当Browser Session
- Health／Model Load／生成
- 二回目Wake-up
- Cold Start／Credit／URL維持
- Secret／Path非露出
- Rollback
- Stop Condition

Stage B Handoff作成だけではPlatform Mutationを許可しない。実行にはユーザーの明示許可を必要とする。
