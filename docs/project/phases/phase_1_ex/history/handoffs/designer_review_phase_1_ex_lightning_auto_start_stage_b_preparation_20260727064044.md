# 設計統括者Review：Phase 1-ex Lightning Auto-start Stage B Preparation

```yaml
document_id: designer_review_phase_1_ex_lightning_auto_start_stage_b_preparation
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-27 06:40:44 JST
owner: 設計統括者役
review_target: implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md
source_handoff: implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md
supersedes: null
```

## 1. Review Result

```text
Verdict:
  ACCEPTED

Blocking Findings:
  NONE

Non-blocking Findings:
  NONE

Repository Preparation:
  COMPLETE

Stage B Lightning Platform Execution:
  NOT_RUN

Platform Operator:
  USER_ONLY
```

Stage B Unattended External Wake TrialのRepository側Preparationは、Handoffの受入条件を満たしている。実装担当StatusをAcceptedとする。

このAccepted判定は、Lightning上でのTraffic-aware Wake-up成立を意味しない。API Builder Plugin、Platform Port、Managed Secrets継承、Public URL、Sleeping Studioの第三者Access Wake-up、二回目Wake、URL維持およびCredit条件は、ユーザーがStage Bを手動実施して確認する。

## 2. Reviewed Artifacts

- [実装担当向け Stage B Preparation Handoff](implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md)
- [実装担当 Stage B Preparation Status](implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md)
- `scripts/runtime/lightning/basic_preview_common.sh`
- `scripts/runtime/lightning/basic_preview_service.sh`
- `scripts/runtime/lightning/auto_start_preflight.sh`
- `tests/unit/runtime/test_lightning_basic_preview_service.py`

実装変更はTestへ限定されている。既存Lifecycle Script三件は内容変更されておらず、既存`run`契約を追加Testで検証する方式である。

## 3. Requirement Alignment

### 3.1 Foreground Entrypoint

API Builderの起動入口として次を採用した判断は妥当である。

```bash
bash scripts/runtime/lightning/basic_preview_service.sh run
```

`run`は事前検査後に`exec margpa-web`し、Foreground Process IdentityとSignal伝播を維持する。Platform側がProcess Lifecycleを所有する構成に適合する。

Manual Terminal向けBackground Lifecycleである次をAPI Builderに使用しない判断も正しい。

```bash
bash scripts/runtime/lightning/basic_preview_service.sh start
```

### 3.2 Thin Entrypoint

新しいThin Entrypointを追加しなかった判断をAcceptedとする。

既存`run`は次をEnvironmentで受け取れる。

- Workspace Root
- Project Root
- Model Root
- `.venv`
- Project-scoped `uv`
- Pure CPU Profile
- Host
- Port
- Basic Authentication

Platform固有の未確認変数を推測でProduction Scriptへ追加せず、重複するModel Load、認証またはWeb Server処理も作っていない。

### 3.3 External Working Directory／Port

Project外のWorking DirectoryからScriptを起動でき、`MARGPA_WEB_PORT`が`margpa-web --port`へ伝達されることを追加Testで確認している。

Lightning API Builder側のApplication Portと`MARGPA_WEB_PORT`を同じ確定値にする手順は妥当である。

`PORT`等のPlatform自動注入変数を未確認のままMappingせず、UI契約が異なる場合に停止する境界も正しい。

### 3.4 Runtime State／Lifecycle Ownership

Foreground `run`はPID、Log、LockまたはDefault Runtime State Directoryを作成しない。Background Lifecycle管理とPlatform Process管理を二重化していない。

既存のManual Basic Preview `start／stop／restart／status`は維持され、対象回帰Testにも合格している。

### 3.5 Credential／Exposure Boundary

CredentialはEnvironmentから継承し、Command Argument、Log、StatusまたはEvidenceへ実値を出さない。

空値、空白、Username禁止文字、改行をModel Load前に拒否する既存境界が維持されている。追加TestでもCredential値のStdout／Stderr非露出を確認している。

### 3.6 User-only Platform Operations

実装担当は次を実施していない。

- Lightning UI操作
- Plugin Install／Remove
- API Builder作成・設定
- Managed Secrets変更
- Public URL発行
- Studio Sleep／Wake
- Stage B実Trial
- Dependency Install／Build
- Model Download／変更
- Git操作

Platform操作をユーザー担当に限定するHandoff境界を守っている。

## 4. Independent Verification

設計統括者環境で再実行した。

```text
Shell Syntax:
  PASS

Target Runtime Test:
  32 passed in 31.83s

Repository Full Suite:
  299 passed
  3 deselected
  33.85s

Ruff Check:
  PASS

Ruff Format Check:
  PASS
  96 files already formatted

Mypy:
  PASS
  96 source files
```

実行Command：

```bash
bash -n \
  scripts/runtime/lightning/basic_preview_common.sh \
  scripts/runtime/lightning/basic_preview_service.sh \
  scripts/runtime/lightning/auto_start_preflight.sh

./.venv/bin/pytest -q \
  tests/unit/runtime/test_lightning_basic_preview_service.py

./.venv/bin/pytest -q

./.venv/bin/ruff check .
./.venv/bin/ruff format --check .
./.venv/bin/mypy .
```

## 5. SHA-512 Verification

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
2413cd6ca9a953d2829e676aac209e6b4781b0fe6ce3befaa0d7d934ca9cdff82cb8556ac8399c0a166c650084c9ff3443d4f64efbe76dbca080f3b6389eb88e

scripts/runtime/lightning/basic_preview_common.sh
1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58

scripts/runtime/lightning/basic_preview_service.sh
7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac

scripts/runtime/lightning/auto_start_preflight.sh
bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d

implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md
2c8e0ab5bb224da0d2ebd66dd7ca1d3dd21cde0464c95becec0e13f0817b2dadf41f4e6952a34d427c800d78888c6a2b3264599cfe18978d2e516e316b0ae254
```

Status記載のArtifact Hashと再計算値は一致する。

## 6. Platform Verification Boundary

次はRepository Reviewでは判定できないため、未確認のまま保持する。

- API Builder Install後の正確なUI
- Working Directory設定
- Startup Command設定
- Platform Port契約
- Managed SecretsのProcess Environment継承
- Health Check設定とTimeout
- Public URL発行
- Third-party URL AccessだけによるSleeping Studio Wake-up
- Owner Browser／Studio Tab／Terminal／SSH完全不在
- First／Second Cold Start
- 同一URL維持
- Credit消費
- Stop／Disable／Remove
- 外部ResponseのSecret／内部Path非露出

これらを偽Passにしていないため、StatusのEvidence分離は妥当である。

## 7. Next Gate

Repository側PreparationはAcceptedであり、実装上のBlockerはない。

次はユーザー判断で、Lightning上のStage Bを手動実施する。実装者役はLightning Platform操作を行わない。

Stage Bの合格条件は次のとおりである。

```text
Studio:
  SLEEPING

Owner Browser／Studio Tab／Terminal／SSH:
  CLOSED／NOT REQUIRED

Trigger:
  THIRD-PARTY VIEWER OPENS PUBLIC URL

Required Result:
  Studio wakes from URL Access
  Foreground run starts
  Model loads
  /healthz returns HTTP 200
  Basic Authentication remains active
  Viewer can generate
  Second Sleep／Wake succeeds
  Public URL remains usable
```

UI Label、Port、Secret継承、Process起動または課金条件が想定と異なる場合は、推測で進めず停止する。Platform MutationとRollbackはユーザーが行う。
