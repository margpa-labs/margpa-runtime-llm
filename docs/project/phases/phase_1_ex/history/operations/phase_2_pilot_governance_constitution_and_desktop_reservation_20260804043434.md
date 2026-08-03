# Phase 2 Pilot／Governance Constitution／Desktop Reservation

```yaml
document_id: phase_2_pilot_governance_constitution_and_desktop_reservation
phase: phase_1_ex
status: accepted_reservation
created_at: 2026-08-04 04:34:34 JST
owner: 設計統括者役
decision_authority: user
scope:
  - future_desktop_application
  - phase_2_history_index_path
  - phase_2_orchestration_pilot_first_gate
  - project_responsibility
  - progressive_orchestration_granularity
  - cross_project_governance_constitution
  - codex_and_claude_code_portability
privacy: sanitized
```

## 1. Decision Summary

次を将来要件・運用予約としてAcceptedした。

1. 後続のいずれかのPhaseでDesktop Application化する。
2. Phase 2以降のAppend-only Documentation Index Snapshotを各Phaseの`history/index/`へ保存する。
3. Phase 2の最初にDocument-driven Orchestration Pilotの設計と最小実行を行う。
4. 現設計統括者役をProject責任者とする。
5. Pilotは小さな有界単位から始め、Phase完了単位、最終的にはProject完了単位を長期目標とする。
6. Agent／Tool本格実装前に、運用規則を完全な統合憲法書へLossless再編する。
7. 憲法書Packageは他Projectへ移植でき、Codex DesktopとClaude Codeの双方へAdapter可能にする。

## 2. Desktop Application

Desktop Application化のPhase、Framework、配布方式および対応OSは未決定である。現時点ではWeb／CLI／Runtime CoreをPresentationへHard-codeせず、後続でLocal Model、File Access、Offline利用、Sandbox、Secret Storage、Update、Code SigningおよびGPU Backendを評価できる境界を維持する。

本予約は即時実装、Phase 4／10への固定、特定Framework採用、Web版廃止または公開配布を意味しない。

## 3. Phase 2 Index Operation

Phase 2の最初のSnapshotから次を必須とする。

```text
docs/project/phases/phase_2/
├─ phase_index_ja.md
└─ history/
   └─ index/
      └─ documentation_index_YYYYMMDDHHMMSS.md
```

`phase_index_ja.md`はStable入口、`history/index/`はAppend-only状態履歴である。Phase 1／Phase 1-exのRaw Indexは相対Linkと原文保持のため遡及移動しない。

## 4. Phase 2 Pilot First Gate

元来のPhase 2-A～2-Fへ入る前に、`Phase 2-0 — Orchestration Pilot Design／Bootstrap`を行う。

```text
Pilot Design
  → Capability／Authority／Cost／Stop／Recovery
  → User-approved Authorization Envelope
  → Task Creation／Naming／Authority Setup
  → Handoff／Status／Follow-up／Review
  → Bounded Work Unit Acceptance
  → Original Phase 2 Work
```

Task作成、Task名変更、Authority設定およびTask間通信は、ユーザーがAcceptedしたEnvelope内部だけで連結する。Envelope外の新Task、権限拡張、Git／External／Secret／Destructive ActionまたはPhase移行は追加承認を必要とする。

## 5. Project Responsibility

現設計統括者役をProject責任者とする。

責任範囲：

- Project全体の整合
- Cross-Phase不変条件
- Phase／Role Task編成
- Index／Handoff／Reading Order／Authority準備
- 設計Review／実装Handoff／Follow-up
- Recovery／Phase Closure準備

Project責任者はUser Authorityを代替しない。ユーザーが要件、Backup、External Mutation、Git／公開、Secret、課金、Destructive Action、User AcceptanceおよびPhase移行の最終Authorityを保持する。

## 6. Progressive Granularity

```text
Stage 1: one bounded work unit
Stage 2: multiple connected work units
Stage 3: one subphase
Stage 4: one phase completion
Stage 5: one project completion
```

各StageでAuthority、Cost、Context、Conflict、Recovery、Review QualityおよびUser Gateを評価する。成功実績だけで次Stageへ自動移行せず、必要なら粒度を戻すかPause／Stopする。

## 7. Integrated Constitution

Agent／Tool本格実装前に、運用規則を`docs/project/shared/constitution/`へ統合する。

対象には少なくとも次を含む。

- 絶対禁止事項
- Documentation Stable／History／Lossless／Index
- Role／Task／Agent／Tool Authority
- Mutation Authorization
- Handoff／Status／Review
- Concurrency／Write Collision
- Git／External／Secret／Cost
- Backup／Restore／Recovery
- Resource Limit／Safe Pause
- Incident／Deviation／Evidence
- Constitution Version／Migration

統合は要約置換ではなく、Source Inventory、Hash、Conflict Matrix、章MappingおよびReconstruction Testを伴うLossless Compilationとする。

## 8. Cross-project／Provider Portability

憲法書Folderを新規／他Projectへ配置し、Project固有Manifestを設定するだけで同等の開発体制を即時展開できる状態を目標とする。

Normative CoreへCodex固有Tool名をHard-codeしない。Task作成、Task命名、Handoff、Follow-up、Status、Wait、Filesystem、Shell、Git、Human ApprovalおよびRecoveryをCapabilityとして定義し、Codex DesktopとClaude CodeのProvider Adapterへ対応付ける。

Capabilityが存在しない場合は推測実行せず、`unsupported`、`manual_required`または`blocked`とする。Provider差によりAuthorityや禁止事項を弱めない。

## 9. Agent／Tool Boundary

憲法書は後続Agent／ToolのGovernance Source候補だが、文書を配置または読込しただけで実行権限を付与しない。

```text
Existence ≠ Activation ≠ Authority ≠ Approval ≠ Execution
```

Runtime適用にはMachine-readable Policy、Deterministic Enforcement、Human Approval、EvidenceおよびFail-closed設計を別途必要とする。

## 10. Current Boundary

```text
Phase 2 Pilot          : reserved／not started
Phase 2-0 Design       : not started
Constitution Folder    : reserved／not created
Desktop Application   : reserved／phase undecided
Task Creation          : not authorized by this record
Agent／Tool Authority  : not granted
Git／External Mutation : not authorized
Phase 1-ex             : in progress
```

## 11. References

- [Experimental Document-driven Codex Task Orchestration](../../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Cross-project Development Governance Constitution Plan](../../../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)
- [Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Project Continuity Master](../../../../current/project_continuity/project_continuity_master_ja.md)
- [Public Roadmap](../../../../../public/roadmap_ja.md)
