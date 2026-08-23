# Phase 6 Exact Model Authority Receipt

```yaml
document_id: phase_6_exact_model_authority_receipt_20260822212732
status: accepted_armed_not_active
phase: phase_6
recorded_at: 2026-08-22 21:27:32 JST
owner_role: プロジェクト責任者兼設計統括者役
human_backup_gate: user_reported_complete
automation_control_state: ARMED_NOT_ON
implementation_authorized: false_until_user_start
git_mutation: not_authorized
network_external_action: not_authorized
```

## 1. Authority Decision

UserのPhase 6開始前Backup完了報告と、`Activation Preflight → Exact Model権限固定 → ARMED`の明示指示を受領した。この指示をPreflight Read AuthorityとしてResolved Target、Canonical Artifact、DiskおよびMemoryを確認し、Phase 6に限り、Project Root外へ解決される`models` Symbolic Linkについて、本書記載のExact Subtree／Operationだけを後続Executionの例外Authorityとして固定する。Preflight中のModel Target Write／Delete／Loadは0である。

本ReceiptはModel Conversion、Model Load、実装またはAutomation開始を単独では許可しない。後続User Startまで、Authorityは`ARMED_NOT_ACTIVE`である。

## 2. Resolved Model Root

```text
Logical Model Root : margpa-runtime-llm/models
Resolved Target    : /Users/Nazuna Research/models/margpa-runtime-llm/models
Purpose            : Phase 6 Local Model Feasibility／Qwen・DeepSeek切替
Active Period      : User Phase 6 Start後 ～ P6-I COMPLETE_CANDIDATE停止まで
Phase 6-J          : 本Authorityに含まない
```

Logical Pathだけを根拠にAuthorityを拡張しない。Resolved Targetの親、Sibling Model、DeepSeek V4、Trash、Home一般、Provider Cacheおよび未指定Subtreeは対象外である。

## 3. Exact Subtree／Operation Matrix

| Logical Subtree | Resolved Physical Subtree | 許可Operation | Activation時状態 |
|---|---|---|---|
| `models/main/qwen3-4b/gguf/` | `/Users/Nazuna Research/models/margpa-runtime-llm/models/main/qwen3-4b/gguf/` | Read／Load only | User Start後にActive |
| `models/main/deepseek-r1-0528-qwen3-8b/huggingface/` | `/Users/Nazuna Research/models/margpa-runtime-llm/models/main/deepseek-r1-0528-qwen3-8b/huggingface/` | Canonical root payload Read only。`.cache/`／`figures/`は除外 | User Start後にActive |
| `models/main/deepseek-r1-0528-qwen3-8b/gguf/` | `/Users/Nazuna Research/models/margpa-runtime-llm/models/main/deepseek-r1-0528-qwen3-8b/gguf/` | New create／write only | User Start後にActive |
| `models/main/deepseek-r1-0528-qwen3-8b/manifests/` | `/Users/Nazuna Research/models/margpa-runtime-llm/models/main/deepseek-r1-0528-qwen3-8b/manifests/` | New create／write only | User Start後にActive |
| `models/main/deepseek-r1-0528-qwen3-8b/conversion_work/` | `/Users/Nazuna Research/models/margpa-runtime-llm/models/main/deepseek-r1-0528-qwen3-8b/conversion_work/` | New create／write only | User Start後にActive |

DeepSeek派生3 SubtreeはPreflight時点で存在しない。P6-A開始時にいずれかが存在していた場合は、上書き、削除または自動再利用をせず、Current Stateを照合して停止する。Conversion Intermediateを成功後に無断削除してはならない。

## 4. Canonical Artifact Evidence

### 4.1 Current Qwen

```text
Model Key       : main.qwen3-4b-q4-k-m
Artifact        : models/main/qwen3-4b/gguf/Qwen3-4B-Q4_K_M.gguf
Size            : 2,497,280,256 bytes
Expected SHA-512: f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
Actual SHA-512  : f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
Result          : PASS
Write／Delete   : PROHIBITED
```

### 4.2 DeepSeek Canonical Snapshot

```text
Repository      : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Exact Commit    : 6e8885a6ff5c1dc5201574c8fd700323f23c25fa
Snapshot Root   : models/main/deepseek-r1-0528-qwen3-8b/huggingface/
Payload Size    : 16,388,927,770 bytes（Download Completion Evidence）
Model Files     : 10（Download Completion Evidence）
Current Shards  : model-00001-of-000002.safetensors／model-00002-of-000002.safetensors
Write／Delete   : PROHIBITED
```

PreflightはSnapshotの存在、主要FileおよびCurrent Sizeを確認した。Exact Source Manifest／Shard Digestの再検証はP6-AのCanonical Revalidationで行い、未実測事項をPASSと捏造しない。

## 5. Disk／Memory／Thermal Gate

```text
Model Filesystem             : /dev/disk3s5
Preflight Available Capacity : 88,108,548 KiB（約84.0 GiB）
Minimum Preservation Floor   : 64 GiB
System Physical Memory       : 17,179,869,184 bytes（16 GiB）
Initial Residency Policy     : Single Model only
```

- Conversion／Derived Artifact作成の各Material Step前に、Current Free SpaceとProjected Writeを確認する。
- Projected／Current Free Spaceが64 GiBを下回る場合、そのWriteを開始または継続しない。
- 空き容量確保を理由にCanonical、Derived、Intermediateまたは他Dataを自動削除しない。
- Model切替は旧ModelをUnloadしてから新ModelをLoadする。Qwen／DeepSeek同時常駐をAcceptance条件にしない。
- Load Failure、OOM／Process Kill、macOS Memory PressureのYellow／Red、制御不能なSwap増大、異常なThermal状態またはUser停止指示を検出した場合は、安全停止する。
- DeepSeekがSafe UnsupportedとなってもPhase 6契約上の正当な結果であり、Supportedを捏造しない。

## 6. Explicit Non-authority

次は本Receiptで許可しない。

- DeepSeek V4 Flash／ProのRead、Conversion、Load、BenchmarkまたはMutation。
- Qwen ArtifactまたはDeepSeek Canonical Snapshotの変更、移動、削除、上書き。
- Resolved Model Rootの親、Sibling Model、`.download_runtime/`、DeepSeek Snapshot内`.cache/`／`figures/`、未指定CacheまたはTrashへの拡張。
- Network Download、AWS、Lightning、外部Service、Secret／Credential操作。
- `runtime_data/`のTest利用、内容確認、Migration、修復または削除。
- Git Add／Commit／Push／Tag／Branch等のMutation。
- Project Root内の既存`.p5t/`／`.t/`の利用、修復、移動または削除。
- Conversion／LoadをUser Start前に開始すること。

## 7. Authority Result

```text
User Backup Gate          : PASS／USER REPORTED COMPLETE
Resolved Target           : CONFIRMED
Qwen Canonical Integrity  : PASS
DeepSeek Canonical Present: PASS／FULL DIGEST REVALIDATION DEFERRED TO P6-A
Disk Floor                : PASS AT PREFLIGHT
Memory／Thermal Contract  : FIXED
Exact Model Authority     : ACCEPTED／ARMED_NOT_ACTIVE
Filesystem Permission Bit: NOT CHANGED／AUTHORITY CONTRACT ONLY
Open Activation Blocker   : NONE
User Start                : PENDING
```
