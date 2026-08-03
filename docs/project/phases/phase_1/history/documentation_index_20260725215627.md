# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-25 21:56:27 JST`
- 更新日時: `2026-07-25 21:56:27 JST`
- Snapshot: `20260725215627`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260725214428.md`

## 1. Current Position

```text
Phase 1-I Web Presentation／UX Follow-up       : Complete／Accepted
Mac Web Manual Acceptance                      : Passed
Phase 1-F Pure CPU Repository Follow-up        : Complete／Accepted
Phase 1-F Pure CPU External Native Acceptance  : Pending
Lightning CPU Upload／Reconstruction Manual    : Current
Top-level Phase 1 Completion                   : Not Declared
Phase 1-ex                                     : Accepted Reservation／Not Started
```

## 2. Snapshot Resolution

本Indexは[documentation_index_20260725214428.md](documentation_index_20260725214428.md)を継承する。

前Snapshot以降の実装変更、外部操作または受入結果はない。本Snapshotでは、Lightning Pure CPU環境へ一括UploadするためのPath配置、Upload対象、除外対象、Preflight、Environment再構築、Native SmokeおよびWeb起動を統合したUser Manualを追加する。

## 3. Current Lightning Pure CPU Manual

[lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md](user_manual/lightning_cpu_upload_and_environment_reconstruction_manual_20260725215627.md)

このManualを、次のユーザー実行GateのCurrent手順とする。

```text
Clean Upload Staging
  → Lightning Project／Model分離配置
  → uv 0.11.29隔離配置
  → Pure CPU Read-only Preflight
  → Setup Plan
  → Environment Reconstruction
  → Environment Verification
  → Bounded Native Smoke
  → Web Preview Smoke
  → Result Status
  → External Native Review
```

## 4. Confirmed Script Paths

```text
Preflight:
  scripts/setup/preflight_lightning_ai_studio.sh

Pure CPU Setup:
  scripts/setup/setup_lightning_linux_x86_64_cpu.sh

Environment Verification:
  scripts/setup/verify_phase1_environment.py

Bounded Native Acceptance:
  scripts/models/phase1f_cross_environment_acceptance.py

Pure CPU Profile:
  config/profiles/lightning_linux_x86_64_cpu_native.toml
```

Pure CPU Preflightでは、既定Targetに依存せず次を明示する。

```text
--runtime-target cpu-native
```

## 5. Upload Boundary

```text
Required:
  src/
  config/
  scripts/
  pyproject.toml
  uv.lock

Recommended:
  tests/
  .gitignore

Excluded:
  .venv/
  models／GGUF
  docs/
  .python-version
  .git/
  macOS Metadata
  Python／Test／Lint／Type Cache
  Native Build Artifact
  Local Runtime Data
  Secret／Environment File
  Log／Backup Zip
```

開発元から直接削除せず、Clean Staging Copyを作成する。

## 6. Environment Contract

```text
OS            : Ubuntu
Architecture  : x86_64
Container     : Required
Python        : 3.12.11
uv            : 0.11.29／Isolated
Backend       : llama-cpp-python 0.3.34／Pure CPU
GPU           : Not Required
CUDA／nvcc    : Not Probed
Acceleration  : none
Fallback      : deny
```

## 7. Previous Accepted Review

[designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](handoffs/designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)

Repository側のPure CPU Detection、Model Root Contract、Setup、Acceptance CorrectionはAcceptedである。

## 8. External Gate

本Snapshotでは次を実施していない。

- Lightning Upload
- uv Install
- Dependency Install
- Environment変更
- Native Build
- Model配置
- Model Load
- Generation
- Port公開

External Native AcceptanceはPendingのまま保持する。

## 9. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

## 10. Scoped Authorization

本Manualはユーザー実行手順を定義する。外部Lightning操作、Git／GitHub、Phase 1完了宣言、Backup、Phase 1-ex開始またはRAG実装を自動許可しない。

## 11. Append-Only

旧Index、旧ManualおよびTimestamp付き文書は変更せず保持する。新Timestampの本Indexを最新とする。

