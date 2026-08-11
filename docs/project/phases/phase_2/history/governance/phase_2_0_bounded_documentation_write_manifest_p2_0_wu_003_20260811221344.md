# Phase 2-0 Bounded Documentation Write Manifest — P2-0-WU-003

```yaml
document_id: phase_2_0_bounded_documentation_write_manifest_p2_0_wu_003_20260811221344
manifest_id: p2-0-write-view-manifest-001
revision: exact-1
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-003
created_at: 2026-08-11 22:13:44 JST
language: ja
owner: プロジェクト責任者兼設計統括者役
decision_authority: user
authorized_root: runtime_resolved_project_root
entry_count: 7
```

## 1. Purpose

本Manifestは、`P2-0-WU-003`の初期Operational ViewをExact Path、Line CountおよびSHA-512で固定する。Full Corpusを通常起動時の既定値にせず、Phase 2-0の一件のBounded Documentation Writeに必要な範囲だけを与える。

本書の存在だけではRead、Write、Task作成、Automation開始またはDifferential Supplementを許可しない。

## 2. Exact Initial Operational View

| Order | Exact Relative Path | Lines | SHA-512 | Purpose |
|---:|---|---:|---|---|
| 1 | `docs/project/shared/operations/research_asset_mutation_control_ja.md` | 432 | `8830fd117b1214de3c4a495de23d75057676fa48724d01fadfa8c99b750ac22df6c34e255263904cfc9a7c53240b4bcd71b712ab5d83cd77569bb2414bc765de` | 最上位Folder／Mutation境界 |
| 2 | `docs/project/shared/task_roles/role_authority_matrix_ja.md` | 272 | `fb1440c5e344dfca4eb540c98d7a3fa6ff746e7a1b81d7a339aa8e8f65342853221dd86d88148b0a70101662bf13c3210055d062ac339e10b18ea27639fe8992` | Role／Docs Authority |
| 3 | `docs/project/shared/automation/automation_control_profile_ja.md` | 362 | `47e7928baf2a2506be7f11f7145a1e036885043156f5f59ba9127f749ae531fc3f8a1c81bf39c27a2c15be922d78289e0c14bbba2489e78a578edcdac48d895b` | Automation Level／State／Stop |
| 4 | `docs/project/phases/phase_2/phase_index_ja.md` | 259 | `95712d109f5e6dc3dfd3001a600d9aa787ff2908cff87ca5e105dd3b1fbb69f84f437539f5b5485335e489e6d01dfda11f58fa604e6788a1db1717746fb1bbce` | Phase 2 State／Subphase Plan |
| 5 | `docs/project/phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811210503.md` | 83 | `db4f1593b53779314031ec78a05cee1ad7e21d0983b7bcd58752a83d5c6d2e85dda015a34ade2b6c335c6700167c2fe88f46822df081d7f6ec10eed7313e4af1` | P2-0-WU-002 Controller Review |
| 6 | `docs/project/phases/phase_2/history/operations/phase_2_0_bounded_read_user_acceptance_p2_0_wu_002_20260811220630.md` | 51 | `3466c4e064dfe061824d0905e6f4c47dd28fae56bb701c7946f1824b7acf71d3ea536115f6898fea0bc5584ef0909418a49e3e3f4e915acd8f70f0b0b69089b5` | Accepted Result／Open Boundary |
| 7 | `docs/project/shared/history/automation/automation_governance_evidence_phase_2_task_identity_and_layered_recovery_ja_20260811220038.md` | 133 | `4727693c1b6e968632cd63624986547ac8a0df2adbb357ca5c63036b57404649bd1aac204550d7b9b1708925e5e9fbc3cb6c0b11fb81e802abd03d60431962fe` | Task Identity／Layered Recovery知見 |

## 3. Canonical Digests

```text
Entry Count                : 7
Total Lines                : 1,592
Ordered Path-set SHA-512   : d6e8facc41549604f8dd2634fe1b7c6398c8a3709d6d06410a9e679c3e3e3cb26fa9698d69a9435685715b26ac05052618324bcf2c2f29fa5af378e6fb7ffcb2
Initial Package SHA-512    : c6efe357d6cacab39948ed8fd3607e58c65ced42a9c8a8c9d124c76f0c273c5c5998597222e5916863e9adb6e1e947740a22cd0d98f04de2c9d500801e94adb0
```

Canonical Inputは`Order + TAB + Relative Path + TAB + Decimal Line Count + TAB + Lowercase SHA-512 + LF`をManifest順に連結する。Path-set Inputは`Relative Path + LF`をManifest順に連結する。

## 4. Read Boundary

```text
Exact File Read      : allowed only after activation
Directory Listing    : prohibited
Search／Glob         : prohibited
Git／History Lookup  : prohibited
Alternative Path     : prohibited
Symlink Traversal    : prohibited
Implicit Expansion   : prohibited
Mutation during Read : prohibited
```

Entry欠落、Unreadable、Line Count不一致、SHA-512不一致またはManifest Revision不一致ではCapabilityを進めず停止する。

## 5. Differential Supplement Boundary

Initial Viewが不足する場合、Childは不足内容を具体化して親Roleへ返し、独自探索しない。ユーザーが後続EnvelopeをAcceptedした場合に限り、親Roleは同一Authorized Root、同一Work Unit、Read-only、必要最小限かつ既知のExact Pathに限定してDifferential SupplementをConversation上で発行できる。

Supplementは少なくともExact Path、Line Count、SHA-512、Purposeおよび失効条件を持ち、Childの再ACK前にReadしない。Root、Role、Work Unit、Mutation、ExternalまたはHuman-only Gateの拡張は、親Roleだけでは許可できない。

## 6. Exact Write Target

```text
Exact Relative Path:
  docs/project/phases/phase_2/history/operations/phase_2_0_layered_recovery_operational_view_result_p2_0_wu_003_20260811220630.md

Required Initial State : absent
Allowed Action         : create one regular UTF-8 Markdown file
Existing File Mutation : none
Additional File Create : none
```

## 7. Invalidation

次のいずれかで本Manifestは失効する。

- Entry内容、Line CountまたはDigestの変化
- Task、Role、Work Unit、EnvelopeまたはWrite Targetの変化
- TargetがTask開始前に存在
- Authorized RootまたはProvider Capabilityの変化
- ユーザーによるRevocationまたは置換

## 8. Related Documents

- [Design Candidate](../operations/phase_2_0_bounded_documentation_write_candidate_p2_0_wu_003_20260811220630.md)
- [P2-0-WU-002 Acceptance](../operations/phase_2_0_bounded_read_user_acceptance_p2_0_wu_002_20260811220630.md)
- [Task Identity／Layered Recovery Evidence](../../../../shared/history/automation/automation_governance_evidence_phase_2_task_identity_and_layered_recovery_ja_20260811220038.md)
