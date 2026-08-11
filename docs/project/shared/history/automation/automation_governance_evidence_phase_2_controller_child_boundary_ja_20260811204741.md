# Automation Governance Evidence — Controller／Child Boundary

```yaml
document_id: automation_governance_evidence_phase_2_controller_child_boundary_20260811204741
status: append_only_history_event
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 20:47:41 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - future_automation_governance_compiler
observation_id: OGE-P2PILOT-017
```

Final Alignment Reviewで、EnvelopeのController ActionとChild向けAbsolute ProhibitionのAuthority Subjectが曖昧であり、Pre-activation Freeze作業まで禁止して見える不整合を検出した。

Controllerの`PAUSED`中Preparation、Two-key Activation後のBounded ExecutionおよびChildのRead-only禁止を分離した。併せて、Design Review合格、User Acceptance、Digest Freeze、READY／ARMEDおよびONを別Stateとして保持した。

本修正はRole上限、Authorized Root、Existing Stable Write、Git、External、Secret、Destructive、Human-only AuthorityまたはChild Write Scopeを拡張しない。Automationは`PAUSED`、新Taskは未作成、Pilotは未再開である。

Stable Evidence Source：

- [Automation Governance Evidence Log](../../automation/automation_governance_evidence_log_ja.md#oge-p2pilot-017--controllerchild-authority-subjectとreviewacceptance-stateの明示)
- [Authorization Envelope draft-4](../../../phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md)
