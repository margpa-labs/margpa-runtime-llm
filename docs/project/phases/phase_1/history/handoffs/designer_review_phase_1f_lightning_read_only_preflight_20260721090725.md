# Phase 1-F Lightning Read-only Preflight 設計Review

- 文書ID: `designer_review_phase_1f_lightning_read_only_preflight`
- 状態: `execution_accepted_environment_follow_up_required`
- 作成日時: `2026-07-21 09:07:25 JST`
- 更新日時: `2026-07-21 09:07:25 JST`
- Snapshot: `20260721090725`
- 作成担当: 設計者役担当Task
- 対象: Lightning Read-only Preflight実行結果とFull Upload可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md](implementer_status_phase_1f_lightning_read_only_preflight_20260721013900.md)
- Handoff: [implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md](implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md)
- Repository Accepted Review: [designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md](designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- 最新Index: [documentation_index_20260721090725.md](../documentation_index_20260721090725.md)
- supersedes: `designer_review_phase_1f_minor_static_gate_follow_up_20260721010200.md`

## 1. Review結論

実装担当によるRead-only Preflight実行はAcceptedとする。

Script 1ファイルだけを配置し、Help、GPU、CPU Candidateを指示どおり実行した。Preflight失敗後もPackage、Environment、Source、GPU設定を変更せず、Full Project／Modelを搬入せず停止している。Privacy／Secret除外も成立している。

Preflight自体は、Lightning既設`uv 0.11.18`とProject期待値`uv 0.11.29`の不一致により不合格である。これはMARGPA RuntimeやPython／CUDAのFailureではなく、Native Gateへ進む前のToolchain Reproducibility Gateである。

設計判断として、期待値を0.11.18へ緩和しない。Lightning既設uvをGlobal／Studio共通環境で上書きもしない。後続の限定Scopeで、公式uv 0.11.29をProject専用の隔離Pathへ導入し、そのBinaryを明示してPreflightを再実行する。

したがって、現時点ではFull Uploadを許可しない。

```text
Implementer Scope Compliance : Pass
Script Integrity             : Pass／SHA-512 Match
Help Gate                    : Pass
Host／Python Precondition    : Pass
GPU Allocation Evidence      : Pass／Tesla T4 15360 MiB
nvcc Availability            : Available
GPU Preflight                : Fail／uv 0.11.18 != 0.11.29
CPU Candidate Preflight      : Fail／same uv Gate
Environment Mutation         : None
New Product Finding          : 0
Environment Follow-up        : Required
Full Upload                  : Not Authorized
Phase 1-F Completion         : Not Accepted Yet
```

## 2. Scope Compliance

次はHandoffどおり成立した。

- Lightningへ配置したProject FileはPreflight Script 1点だけである。
- Local正本とLightning配置物のSHA-512が一致した。
- Mac `.venv`、Model Artifact、Project本体を搬入していない。
- `uv sync`、`pip install`、Native Build、Config／Source変更を行っていない。
- 失敗後の即席Repairを行っていない。
- Credential、Private URL、Session／Machine Identifier、個人PathをStatusへ残していない。
- GPU／CPUの未合格結果をPass扱いしていない。

独立したLocal照合でも、Preflight ScriptのSHA-512はStatus記載値と一致した。

```text
1e78756d581de1895542bfc9a2f25438c4a2058b2d3873dd9208191f3d028cfff8cecb434a1d2ee02885727043b592ea90356df50774795e45ef91ebbe356eab
```

## 3. Environment Evidence

Preflightがuv Gateへ到達したこと、および追加のRead-only Evidenceから次を確認できる。

```text
Operating System      : Linux
Architecture          : x86_64
Distribution          : Ubuntu
Execution Environment : Container
Environment Mode      : studio-active
Python                : 3.12.11／Exact Match
uv                    : 0.11.18／Expected 0.11.29
GPU                    : Tesla T4／15360 MiB
nvidia-smi             : Available
nvcc                   : Available
```

GPU／`nvcc`の独立確認はPreflight自体を合格へ変更しないが、次の限定Follow-upを実行可能なTargetであることは示している。

## 4. uv Version Decision

### 4.1 Retain 0.11.29

Projectは、既存ADR、Mac Setup、Lightning Setup、Preflightでuv 0.11.29を再現性Toolchainとして固定している。ここでLightning既設値へ期待値を緩めると、環境ごとに異なるuvでLock／Sync／Buildを行うことになり、Phase 1-FのCross-environment Reproducibility目的を弱める。

`pyproject.toml`のBuild Backendも`uv_build>=0.11.29,<0.12`である。これはuv CLI Versionと同一概念ではないが、Projectが0.11.29世代を基準としている補助Evidenceである。

uv 0.11.18が本Projectで実際に動かないと判定したわけではない。互換性を未検証のまま受理せず、Accepted Toolchainへ揃える判断である。

### 4.2 Do Not Mutate Studio-global uv

LightningのPersistent Active Environmentには他のPackage／Toolが存在し得る。既設`uv`を直接Upgrade／Overwriteすると、Studio共通環境へ不要な副作用を与える。

次の構造を採用する。

```text
Lightning Existing uv 0.11.18
  └─ Unchanged

MARGPA Project-local Toolchain
  └─ uv 0.11.29／Exact Version／Explicit Path
```

Project専用uvはPython Environment内Packageではなく、公式Standalone Binaryとして隔離する方向を第一候補とする。

### 4.3 Primary Sources

- [uv 0.11.18 Official Release](https://github.com/astral-sh/uv/releases/tag/0.11.18)
- [uv 0.11.29 Official Release](https://github.com/astral-sh/uv/releases/tag/0.11.29)
- [uv Official CLI Reference](https://docs.astral.sh/uv/reference/cli/)

公式ReleaseではLinux x86_64用0.11.29 ArtifactとVersion固定Installerが提供されている。後続設計では、公式配布物、Checksum／Digest検証、隔離配置、明示Path、Version再確認を必須にする。

## 5. Required Follow-up

次の小規模Follow-upを、Read-only Preflightとは分離した明示的なEnvironment Mutation Scopeとして設計する。

```text
1. uv 0.11.29 Project-local Bootstrap Script
2. Official Source／Exact Version固定
3. Downloaded ArtifactまたはInstallerのIntegrity Evidence
4. Studio-global uv 0.11.18が未変更であることの確認
5. Project-local uv 0.11.29の明示Path確認
6. 同じPreflightをProject-local uvで再実行
7. GPU／CPU Candidate Resultを後継Statusへ記録
```

Preflight Scriptへ自動Install処理を混在させない。Read-only ProbeとMutationを別Script／別Stepに維持する。

## 6. Independent Verification

Local Repositoryで次を確認した。

```text
Preflight Script SHA-512                      : Statusと一致
bash -n Preflight／Lightning Full Setup       : Pass
pytest Config／Deployment Platform対象        : Pass／65 tests
Local Source／Config変更                      : None required by this Review
```

Lightning側のCommandは外部Target実行であるため、設計者役はImplementer StatusのEvidenceをReviewした。外部Targetで未実行のNative Gateを合格扱いしていない。

## 7. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| Implementer Read-only Execution | Accepted | Scope／停止条件を遵守 |
| Script Integrity | Pass | SHA-512 Match |
| Host／Container／Python | Pass | Linux x86_64／Ubuntu／Container／3.12.11 |
| GPU Allocation Evidence | Pass | Tesla T4／15360 MiB |
| uv Toolchain Gate | Fail | Observed 0.11.18／Expected 0.11.29 |
| GPU Preflight | Blocked | uv Gateで停止 |
| CPU Candidate Preflight | Blocked | uv Gateで停止 |
| Product Runtime | Not Run | Full Upload前 |
| Full Upload | Not Authorized | uv Follow-up待ち |

## 8. Next Gate

```text
Project-local uv 0.11.29 Bootstrap設計／Handoff
  → Implementer限定Follow-up
  → Project-local uv Version／Integrity確認
  → Read-only Preflight再実行
  → Designer Review
  → Full Upload可否判定
```

Source一式、Model、Dependency Sync、Native Build、CUDA／CPU Acceptanceはまだ開始しない。

## 9. Summary Mode Decision Separation

本Turnで確定した要約モードは、[Post-generation Summary Mode要件予約](../requirements/post_generation_summary_mode_requirements_reservation_20260721090725.md)へ分離した。Phase 1-FのPreflight／Toolchain判断へ混在させない。

## 10. Authorization Boundary

本Reviewは実装担当のRead-only実行をAcceptedとするが、Full Upload、Model Transfer、Dependency Install、Studio-global uv変更、Project-local uv導入、Native Buildをまだ許可しない。

次はProject-local uv 0.11.29 Bootstrap専用Handoffを作成し、ユーザーが実装担当へ開始を指示した後に進める。

## 11. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
