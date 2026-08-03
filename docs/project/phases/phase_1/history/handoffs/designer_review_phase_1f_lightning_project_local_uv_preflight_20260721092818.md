# Phase 1-F Lightning Project-local uv Preflight 設計Review

- 文書ID: `designer_review_phase_1f_lightning_project_local_uv_preflight`
- 状態: `accepted_ready_for_full_upload_handoff`
- 作成日時: `2026-07-21 09:28:18 JST`
- 更新日時: `2026-07-21 09:28:18 JST`
- Snapshot: `20260721092818`
- 作成担当: 設計者役担当Task
- 外部実行担当: ユーザー
- 対象: Project専用uv 0.11.29導入とLightning Preflight再実行
- 正本言語: 日本語
- 前回Review: [designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md](designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 最新Index: [documentation_index_20260721092818.md](../documentation_index_20260721092818.md)
- supersedes: `designer_review_phase_1f_lightning_read_only_preflight_20260721090725.md`

## 1. Review結論

ユーザーがLightning AI Studioで実行したProject専用uv 0.11.29の隔離導入とPreflight再実行をAcceptedとする。

Project／Studio専用Tool Pathのuvは0.11.29であり、Lightning既設`/usr/local/bin/uv`は0.11.18のまま維持された。Shell全体のPATHを恒久変更せず、Preflight Processだけで専用uvを優先している。

Help、GPU Mandatory Preflight、CPU Candidate PreflightはすべてExit Code 0で合格した。したがって、Phase 1-FのRead-only Preflight GateをAcceptedとし、Full Project／Modelを一度だけ搬入する次Handoffを作成可能と判定する。

ただし、Dependency Sync、CUDA Native Build／Reuse、Model Load、Generate、CPU Runtimeはまだ未実行である。Phase 1-F全体の完了宣言ではない。

```text
Project／Studio-local uv       : 0.11.29／Pass
Lightning Existing uv          : 0.11.18／Unchanged
Permanent PATH Mutation        : None
Help Gate                      : Pass／Exit 0
GPU Preflight                  : Pass／Exit 0
CPU Candidate Preflight        : Pass／Exit 0
Python                         : 3.12.11／Retained
Environment Mode               : studio-active
nvcc                           : Available
Preflight Decision             : Accepted
Full Upload Handoff            : Ready to Create
Phase 1-F Completion           : Not Accepted Yet
```

## 2. User-supplied External Evidence

### 2.1 Project／Studio-local uv

```text
Version      : uv 0.11.29／x86_64-unknown-linux-gnu
Placement    : Studio-local .runtime-tools/uv/0.11.29/bin/uv
Binary Size  : 65,688,664 bytes
uvx          : Present
SHA-512      : 957e3ee915fef24101de24a8414c4a9f60e3bd25f0e127eb89a12a78e6bbb6f79621dcb5e10dc41e31834f77a6d7180bebcdfc7ccb08901eba059cde627e8d48
```

個人情報や公開に不要な絶対Pathは正本文書へ保存せず、Studio-local相対概念として記録する。

### 2.2 Lightning Existing uv

```text
Command Source : /usr/local/bin/uv
Version        : uv 0.11.18／x86_64-unknown-linux-gnu
Mutation       : None
```

既設uvとMARGPA専用uvの分離が成立している。

## 3. GPU Preflight Evidence

実行方式：Process単位でMARGPA専用uv DirectoryをPATH先頭へ置き、Preflightを`auto` Modeで実行した。

```text
Result           : Phase 1-F Lightning preflight passed.
Exit Code        : 0
Environment Mode : studio-active
Python           : 3.12.11
uv               : 0.11.29／MARGPA専用Path
GPU Required     : 1
nvcc Available   : yes／informational
```

前回EvidenceからAllocated GPUはTesla T4／15360 MiBであり、今回のGPU Required Gateも合格した。

## 4. CPU Candidate Preflight Evidence

```text
Result           : Phase 1-F Lightning preflight passed.
Exit Code        : 0
Environment Mode : studio-active
Python           : 3.12.11
uv               : 0.11.29／MARGPA専用Path
GPU Required     : 0
nvcc Available   : yes／informational
```

この結果は、GPU Requirementを外したEnvironment Candidateの合格である。GPU未使用のModel Load／Generateや、GPUなしInstance上のCPU Runtimeを証明するものではない。CPU Native GateはFull Upload後に別途実行する。

## 5. Python Version Decision

Lightning Pythonは3.12.11のまま維持する。

根拠：

- ADR-0015でLightning既設CPython 3.12.11を正式な検証対象としてAccepted済みである。
- Project Metadataは`>=3.12,<3.14`であり、3.12.11は正式Support範囲内である。
- Mac 3.13.14とLightning 3.12.11の両方を通すことで、Application CoreのCross-version Portable Runtimeを実証できる。
- Studio Active EnvironmentのPython Upgradeは、既設Package、CUDA Native Build、Persistent Environmentへ新しい変数と副作用を追加する。
- 3.12.11でPreflightが成立しており、現時点でUpgradeを必要とするFailureが存在しない。

将来Lightning Python 3.13を追加する場合は、3.12.11を置換せず、別Environment／別Profile／別Native Gateとして追加する。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| uv Isolation | Pass | 0.11.29専用Path／0.11.18既設維持 |
| Installer Result | Pass | Exact Version Binary利用可能 |
| Permanent PATH Mutation | Pass | なし |
| Python 3.12.11 | Pass | Accepted Target維持 |
| GPU Preflight | Pass | Exit 0 |
| CPU Candidate Preflight | Pass | Exit 0／Native Runtime未証明 |
| Full Project／Model Upload | Not Run | 次Handoff待ち |
| Dependency Sync | Not Run | 次Gate |
| CUDA Native Runtime | Not Run | Mandatory Gate |
| CPU Native Runtime | Not Run | Candidate Gate |

## 7. Next Gate

```text
Full Upload／Native Verification Handoff
  → Project Sourceを一度だけ搬入
  → Mac固有物／Secret／Cache除外確認
  → GGUF ModelをPersistent Model Pathへ配置
  → MARGPA専用uv 0.11.29でLock／Sync
  → Existing CUDA Build確認または限定Rebuild
  → Python 3.12.11 Default Test
  → CUDA Mandatory Acceptance
  → CPU Candidate Acceptance
  → Implementer／External Status
  → Designer Final Review
```

ユーザーが懸念しているUpload回数を増やさないため、次Handoffで搬入対象、除外対象、Model配置、実行順を一括して固定する。

## 8. Authorization Boundary

本ReviewはRead-only PreflightをAcceptedし、Full Upload／Native Verification専用Handoffの作成を許可する。

本Review単独では、Full Upload、Model Transfer、Dependency Sync、Native Build、Source変更、Python Upgrade、Phase 1-G実装、Backup、Git、GitHub公開をまだ許可しない。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
