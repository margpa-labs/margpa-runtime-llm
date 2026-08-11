# Phase 2-0 Bounded Documentation Write Freeze Receipt — P2-0-WU-003 exact-1

```yaml
document_id: phase_2_0_bounded_documentation_write_freeze_receipt_p2_0_wu_003_exact_1_20260811223702
receipt_id: p2-0-freeze-receipt-005
revision: exact-1
status: corrected_exact_package_accepted_ack_retry_authorized
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:37:02 JST
language: ja
from_role: user
to_role:
  - プロジェクト責任者兼設計統括者役
  - Phase 2設計担当者役
task_title: Phase 2設計担当者役 P2-0-WU-003
task_limit: 1
capability_start_authorized: false
supersedes: p2-0-freeze-receipt-005/unrevisioned
```

## 1. Correction Authority

ユーザーは、Initial ACK Review後に次を明示した。

> P2-0-WU-003 Freeze Receipt Correctionの新規作成と、同じTaskへのNo-tool ACK再要求を許可する。

本Correctionは、Original Receiptに欠けていた`revision` Fieldを追加する。Exact Control Package、Initial Operational View、Task、Write Path、Allowed Capability、ProhibitionおよびHuman Gateは変更しない。

## 2. Frozen Exact Control Package

| Order | Artifact／Revision | Lines | SHA-512 |
|---:|---|---:|---|
| 1 | `docs/project/phases/phase_2/history/governance/phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_exact_2_20260811221832.md`／`p2-0-envelope-002 exact-2` | 148 | `ab893d07f22dfc8a165eca912a29a2ab78fb5a318810db297f5ca69e7a84e54cba65932dcb8a61fdbbcf09b20cf8beae45119d232652900d0b481c7df724e738` |
| 2 | `docs/project/phases/phase_2/history/governance/phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md`／`p2-0-write-view-manifest-001 exact-1` | 95 | `616332df3343c4c73466736d875240afc7f77f2ffc68d4cd46ff7b93973dd2b4742d4fa39ffe4550f1dce4ee11dfac362fc1c4795a0dd86906565ef06e38c5f4` |
| 3 | `docs/project/phases/phase_2/history/handoffs/phase_2_0_phase_designer_bounded_write_handoff_p2_0_wu_003_exact_2_20260811221832.md`／`p2-0-handoff-phase-designer-002 exact-2` | 193 | `0b3c242fa309a3be2507251a17bb60d4a770e1fc9c6a0e131e90dadb34ae920519d37527a47ad5f0b265efb08bd02f1266327ecc2c40b7bdadb6970c95ece569` |

```text
Control Package Path-set SHA-512 : fb152eea15ca53c5ff0e65fd191c30cf32dbb703432060075473ba8d402d7e611ea628c020cb5cf7548effaf9eed979632b2a115d38b7913a1ab1bf08c7b3ed9
Control Package SHA-512          : f84a0cea264588503604ccb3e331e5f5d09837881891655f2861794024d1ca80d856caa3841fd83d9037b2fa4c110e4e4e5669f487e3f2c509abd35c5474439b
```

## 3. Frozen Initial Operational View

```text
Entry Count              : 7
Total Lines              : 1,592
Ordered Path-set SHA-512 : d6e8facc41549604f8dd2634fe1b7c6398c8a3709d6d06410a9e679c3e3e3cb26fa9698d69a9435685715b26ac05052618324bcf2c2f29fa5af378e6fb7ffcb2
Initial Package SHA-512  : c6efe357d6cacab39948ed8fd3607e58c65ced42a9c8a8c9d124c76f0c273c5c5998597222e5916863e9adb6e1e947740a22cd0d98f04de2c9d500801e94adb0
```

## 4. Exact Task／Write Boundary

```text
Task Title : Phase 2設計担当者役 P2-0-WU-003
Task ID    : 019ff101-b853-7852-a904-bd20df158a66
Task Count : one／already created／no replacement

Exact Write Path:
docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md

Write Target State       : absent
Current Child Mutation   : 0
Capability Start         : not authorized
```

## 5. ACK Retry Boundary

同じTaskへ、Correction Receipt `p2-0-freeze-receipt-005／exact-1`のPath、Line CountおよびSHA-512を含むNo-tool ACK再要求を一回だけ送信できる。

TaskはRequired Field全件をExactに返し、欠落、不明、`N/A`または不一致がある場合は`ACK_STATUS: REJECTED`としなければならない。ACK合格後もRead／Writeを開始せず、Controller READYとユーザーStartを待つ。

## 6. State／Invalidation

```text
Original ACK     : CONTROLLER REJECTED
Correction       : CREATED
No-tool Re-ACK   : AUTHORIZED／PENDING
Capability Start : NOT AUTHORIZED
Automation       : PAUSED_ACK_CORRECTION
```

Correction Receipt、Control Package、Task IdentityまたはWrite Target Stateが変化した場合は失効する。

## 7. Related Documents

- [Original Receipt](phase_2_0_bounded_documentation_write_freeze_receipt_p2_0_wu_003_20260811222544.md)
- [Initial ACK Review](phase_2_0_bounded_write_initial_ack_review_p2_0_wu_003_20260811223702.md)
- [Exact Envelope exact-2](../governance/phase_2_0_bounded_documentation_write_envelope_p2_0_wu_003_exact_2_20260811221832.md)
- [Exact Manifest exact-1](../governance/phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344.md)
- [Exact Handoff exact-2](../handoffs/phase_2_0_phase_designer_bounded_write_handoff_p2_0_wu_003_exact_2_20260811221832.md)
