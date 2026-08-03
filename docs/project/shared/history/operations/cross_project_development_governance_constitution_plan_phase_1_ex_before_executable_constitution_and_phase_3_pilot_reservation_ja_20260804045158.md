# Cross-project Development Governance Constitution Plan

```yaml
document_id: cross_project_development_governance_constitution_plan
status: planned_preimplementation_gate
normative: false
language: ja
created_at: 2026-08-04 04:34:34 JST
updated_at: 2026-08-04 04:34:34 JST
owner: 設計統括者役
decision_authority: user
target_gate: before_agent_and_tool_implementation
rag_default: true
```

## 1. 位置付け

本書は、Project内に蓄積している絶対禁止事項、Documentation規則、Role／Authority、Mutation Control、Handoff、Review、Recovery、Backup、Git、Costおよび停止条件を、将来一つの章立てされた統合憲法書へLosslessに再編するための計画書である。

現時点では憲法書そのものではなく、作成時期、入力、構造、Portable Package要件およびAcceptanceを固定する予約である。本書だけを根拠に既存規則を置換、要約、廃止または移動しない。

## 2. 作成時期

統合憲法書は、RuntimeのAgent／Toolを本格実装する前の独立Gateで作成する。

それまでは、Phase 2 Document-driven Orchestration Pilotを含む実運用から次を継続収集する。

- Authority逸脱と未遂
- 誤解、暗黙推測およびScope拡張
- Task作成、命名、Handoff、Follow-upおよびReview
- 同一Working Treeでの競合
- Docs-only RecoveryとTask再作成
- Resource／Credit Limitによる安全なPause
- Backup、Git、External MutationおよびUser Gate
- Provider／Tool Capability差
- Ruleの重複、矛盾、欠落、例外および実効性

作成を早める場合も、入力Inventory、Source Hash、Conflict ListおよびUser Approvalを省略しない。

## 3. Canonical予定Path

```text
docs/project/shared/constitution/
├─ development_governance_constitution_ja.md
├─ constitution_manifest.yaml
├─ capability_contract_ja.md
├─ provider_adapters/
│  ├─ codex_ja.md
│  └─ claude_code_ja.md
└─ templates/
   ├─ authority_envelope_ja.md
   ├─ handoff_ja.md
   ├─ status_ja.md
   ├─ review_ja.md
   └─ recovery_ja.md

docs/project/shared/history/constitution/
└─ <stable_name>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

File構成は作成時のInventoryとReviewで調整できる。ただし、統合憲法書のStable本体、Package Manifest、Capability Contract、Provider Adapterおよび運用Templateを分離する原則は維持する。

## 4. Portable Package目標

`docs/project/shared/constitution/`を新規または他Projectへ配置し、Project固有のManifestとAuthorityを設定するだけで、同じ開発統治体制を即時展開できる状態を目標とする。

Portable PackageはMARGPA固有のAbsolute Path、Repository、Model、Phase番号、個人情報、Credentialまたは特定Task IDを前提にしない。Project固有値は別ManifestまたはAdapterへ分離する。

## 5. Provider-neutral要件

Normative CoreはCodex固有Tool名やClaude Code固有Commandを規則本文へ直結させない。共通Capabilityとして次を定義する。

```text
Task／Session Creation
Task Naming
Instruction／Handoff Delivery
Follow-up Messaging
Status Observation
Wait／Pause／Resume
Filesystem Read／Write
Shell／Test
Git／External Mutation
Human Approval
Recovery／Archive
```

Codex Desktop、Claude Codeその他の実行環境はProvider AdapterでCapabilityへ対応付ける。利用できないCapabilityは推測実行せず、`unsupported`、`manual_required`または`blocked`として扱う。

Provider互換性は「同じCommandが動くこと」ではなく、同じAuthority、Evidence、Stop、RecoveryおよびHuman Gateの意味が保持されることをAcceptance基準とする。

## 6. 統合対象

少なくとも次を章立てして取り込む。

1. User Authority／Project Decision Authority
2. 絶対禁止事項
3. Workspace／Project Root境界
4. Role／Task／Agent／Tool Authority
5. Mutation Authorization Envelope
6. Documentation Stable／History／Lossless／Index規則
7. Handoff／Acknowledgement／Status／Review
8. Concurrent Work／Write Collision Control
9. Git／Remote／External Service／Secret／Cost境界
10. Backup／Restore／Recovery／Task再作成
11. Resource Limit／Safe Pause／Resume
12. Incident／Deviation／Evidence Retention
13. Provider Capability Adapter
14. Cross-project Bootstrap／Validation
15. Constitution Change／Version／Migration

## 7. Lossless Compilation

統合憲法書は、既存規則の短い要約集として作らない。

```text
Source Inventory／Hash Freeze
  → Rule Classification
  → Duplicate／Conflict／Exception Matrix
  → Chapter Mapping
  → Lossless Draft
  → Source Traceability検証
  → Provider-neutral Core分離
  → Adapter／Template作成
  → Reconstruction Test
  → User Review／Acceptance
```

意味が重複する規則を統合する場合も、Source、原文、例外、適用範囲および変更理由をManifestから追跡可能にする。読みやすさを理由に禁止事項、失敗事例またはAuthority境界を弱めない。

## 8. Agent／Toolへの適用

統合憲法書は、開発担当Taskだけでなく、後続のAgent／Tool設計で使用するGovernance Source候補とする。

ただし、文書を配置しただけでRuntime権限、Tool Permissionまたは実行許可を生成しない。Agent／Toolへ適用する場合は、Machine-readable Policy、Deterministic Enforcement、Human Approval、EvidenceおよびFail-closed境界を別途設計する。

```text
Constitution Exists
  ≠ Loaded
  ≠ Active
  ≠ Authorized
  ≠ Enforced
  ≠ User Approved
```

## 9. Phase 2 Pilotからの入力

Phase 2 Pilotでは、当初はSubphaseまたは一つの有界なWork UnitごとにOrchestrationする。結果が安定した場合だけ、複数Work Unit、Phase完了単位、最終的にはProject完了単位へ対象粒度を拡大する。

粒度拡大はTask数または自律性の無条件拡大ではない。各段階でAuthority遵守、Cost、Recovery、Review品質、Conflict、User Gateおよび停止可能性を評価し、`GO／ADJUST／STOP`を決定する。

PilotのIncident、成功、停止、再開およびProvider Capability差は、憲法書作成時のEmpirical Inputとして保持する。

## 10. Acceptance Criteria

- 既存の全対象規則がSource／Hash付きで追跡できる。
- 絶対禁止、Authority、Docs、Mutation、RecoveryおよびUser Gateに情報ロスがない。
- MARGPA固有値を別Manifestへ分離できる。
- CodexとClaude Codeの双方についてCapability Mappingと不足時Fallbackを説明できる。
- Folder単体を他ProjectへCopyし、Bootstrap Checklistから同じRole／Docs／Handoff／Review体制を構築できる。
- Provider差がAuthorityの拡大または禁止事項の弱体化を生まない。
- Agent／Toolが文書の存在だけから権限を獲得しない。
- Constitution自体の変更、History、Version、ReviewおよびRollbackが定義される。
- 新しいTaskが旧会話へ依存せず、Packageから運用を再構築できる。
- ユーザーが内容と適用範囲を明示承認する。

## 11. 現在のDecision

```text
Constitution Folder       : reserved／not created yet
Constitution Compilation  : not started
Operational Rule Collection: active
Phase 2 Pilot Evidence    : required input
Agent／Tool Application   : future／separate design required
Codex Portability         : required
Claude Code Portability   : required
User Acceptance           : required
```

## 12. Related Documents

- [Experimental Document-driven Codex Task Orchestration](experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Documentation Rules](../conventions/documentation_rules_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Research Asset Mutation Control](research_asset_mutation_control_ja.md)
- [Phase Completion Review／Backup Gate](phase_completion_review_and_backup_gate_ja.md)
