# 実装担当 Phase 1-F Lightning Read-only Preflight Status

- 文書ID: `implementer_status_phase_1f_lightning_read_only_preflight`
- 状態: `preflight_blocked_waiting_designer_decision`
- 作成日時: `2026-07-21 01:39:00 JST`
- 更新日時: `2026-07-21 01:39:00 JST`
- Snapshot: `20260721013900`
- 作成担当: 実装担当Task
- 正本言語: 日本語
- Documentation Index: [documentation_index_20260721010621.md](../documentation_index_20260721010621.md)
- Preflight Handoff: [implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md](implementer_handoff_phase_1f_lightning_read_only_preflight_20260721010621.md)

## 1. Authorization／Scope

ユーザーの「最新IndexとPreflight Handoffを読んで開始」およびLightning Studio準備完了の指示に基づき、Phase 1-F Read-only Preflightだけを実行した。

Lightning Studioへ配置したProject Fileは`preflight_lightning_ai_studio.sh` 1点だけである。Full Project、Model Artifact、`.venv`は搬入していない。Package Install／Sync／Build、Environment／GPU設定変更、Source／Config／Test／Script変更、Git／GitHub操作、失敗後のRepairは行っていない。

Private URL、Session／Machine Identifier、Hostname、個人Path、Secretは本Statusへ記録していない。

## 2. Current State

```text
Target Studio                 : MARGPA-RUNTIME-LLM／1 x T4
Preflight Script Placement    : Complete／Hash Match
Help Gate                     : Pass
GPU Read-only Preflight       : Fail／uv Version Gate
CPU Candidate Preflight       : Fail／uv Version Gate
Full Project／Model Upload    : Not Performed
Environment Repair            : Not Performed／Not Authorized
Phase 1-F Native Runtime Gate : Not Started
Phase 1-F Completion          : Not Claimed
```

## 3. Script Placement／Integrity

配置先はStudio内の次のProject相対Pathである。

```text
scripts/setup/preflight_lightning_ai_studio.sh
```

Local正本とStudio配置物のSHA-512を照合した。

```text
SHA-512 : 1e78756d581de1895542bfc9a2f25438c4a2058b2d3873dd9208191f3d028cfff8cecb434a1d2ee02885727043b592ea90356df50774795e45ef91ebbe356eab
Result  : OK
Exit    : 0
```

## 4. Commands／Results

### 4.1 Help Gate

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --help
```

```text
Exit   : 0
Stdout : Usage、environment-mode、cpu-only、help、およびRead-only Probeの説明を表示
Stderr : None
```

### 4.2 GPU Read-only Preflight

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto
```

```text
Exit   : 1
Stdout : None
Stderr : Phase 1-F Lightning preflight failed: expected uv 0.11.29, got 0.11.18
```

### 4.3 CPU Candidate Read-only Preflight

```bash
bash scripts/setup/preflight_lightning_ai_studio.sh --environment-mode auto --cpu-only
```

```text
Exit   : 1
Stdout : None
Stderr : Phase 1-F Lightning preflight failed: expected uv 0.11.29, got 0.11.18
```

GPU／CPUの両経路は同一の`uv` Version Gateで停止した。失敗地点より後段の正式なGPU／`nvcc`判定には到達していない。

## 5. Read-only Environment Evidence

Preflight Scriptの判定順序上、`uv` Gate到達前に次が合格している。

```text
Platform            : Linux
Architecture        : x86_64
Distribution        : Ubuntu
Container Marker    : Supported
Environment Mode    : studio-active／autoで解決
Python              : 3.12.11／Exact Match
uv Expected         : 0.11.29
uv Observed         : 0.11.18
```

失敗後のRepairを行わず、後続判断に必要な事実だけを独立したRead-only Commandで確認した。

```text
Allocated GPU       : Tesla T4
GPU Memory Total    : 15360 MiB
nvidia-smi Exit     : 0
nvcc Availability   : Available
nvcc Probe Exit     : 0
```

これらの独立確認はGPU／CPU Preflightの失敗を合格へ変更するものではない。

## 6. Stop Reason／Designer Decision Request

Handoffが要求する`uv 0.11.29`とStudio Active Environmentの`uv 0.11.18`が一致しないため、Read-only PreflightはBlockされた。契約どおり、その場でのVersion変更や環境修復は行わず停止した。

設計者役には、次のいずれかを正本文書で決定するよう依頼する。

```text
1. PreflightのExpected uv Versionを見直す
2. 検証手順を伴うuv 0.11.29への明示的更新を別Scopeとして許可する
3. その他のEnvironment Mode／Runtime構築方針を指定する
```

決定と再実行許可が得られるまでは、Full Project／Model搬入、Lightning CUDA／CPU Native Gate、Phase 1-F完了判定へ進まない。
