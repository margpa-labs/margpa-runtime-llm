# Phase 11以降予約 — 四段階Agent Capabilityと段階的成熟化

```yaml
document_id: phase_11_plus_four_level_agent_capability_and_incremental_maturity_reservation_20260905213338
document_type: lossless_capability_direction_reservation
document_state: agreed_direction_reserved_not_started
language: ja
recorded_at: 2026-09-05 21:33:38 JST
decision_authority: user
authority_owner: Nazuna Research
target_timing: phase_11_or_later_and_future_agent_program
previous_three_level_model_preserved_as_history: true
new_level_count: 4
all_levels_require_incremental_subdivision: true
phase_10_plan_changed: false
implementation_authorized_now: false
append_only: true
```

## 1. 予約の目的

本記録は、既存の三段階Agent Capabilityを四段階へ再整理し、各Levelを一括実装せず、細かな成熟段階へ分割して進めるというNazuna Researchの決定を固定する。

発端は、将来のMARGPA Development Agentへ18GD、Runtime Constitution、上級制御Actor、Domain Actor、Repair／Review、Evidence／State Ledger等を搭載する構想である。これらの導入にも相応の設計、実装、検証、UIおよび運用工数が必要になるため、通常のDevelopment AgentからFull-Cycle Autonomous Engineeringまでを粗い三段階だけで扱わない。

## 2. Controllerの誤読と訂正

Codex Controllerは一度、Levelを「GD／Governance機能の高度さ」だけで分類し、既存予約に明記されていたEnd-to-EndおよびFull-CycleのLifecycle軸を落とした。この解釈は誤りとして撤回する。

既存Levelの本来の軸は、Systemが自律して担当できるLifecycleの広さである。最終目的は単なる高度なDevelopment Agentではなく、Userが「これを作って回しておいて」と目的を渡した後、Consultingから設計、開発、Deployment、運用保守、監視、修復、改善、再設計、移行・廃止および次Cycleまで継続して自律運営するAIである。

GD、Constitution、Actor階層および分散Nodeは重要だが、それだけでAgentの最終Capabilityを定義しない。

## 3. 新しい四段階Capability

### Level 1 — Development Agent

通常のCodex、Claude、Copilot等に近い、Boundedな開発実行主体を成立させる。

```text
Design Support
→ Implementation
→ Test
→ Fix／Repair
```

Level 1は、Platformの基本的なAuthority、Approval、Budget、Stop、Evidence等を利用できるが、18GDによるMulti-GD Actor組織を完成条件にしない。

### Level 2 — Governed Development Agent

Level 1と同じくBoundedな開発を主対象としながら、ARGD／DAGD、Runtime Constitution、必要時起動のSupervisory ActorおよびDomain Actor等を使い、役割分業、戦略、権限、監査、Meta-review、RepairおよびEvidenceを統治されたWorkstreamとして扱う。

Level 2は今回新しく挿入する段階である。GDを搭載することと、全GDを毎回常駐・実行することは同義ではない。必要なComponentだけを選択して起動する。

### Level 3 — Governed End-to-End Autonomous Engineering Agent

従来のLevel 2に相当する。一つの案件・目的を入口からDeploymentまで自律遂行する。

```text
Consulting
→ Discovery
→ Problem Definition
→ Research
→ Requirements
→ Architecture
→ Implementation
→ Verification
→ Release
→ Deployment
```

Level 2のGoverned Developmentを土台に、Goal具体化、工程設計、複数Roleの調整および案件全体の完了責任を追加する。

### Level 4 — Governed Full-Cycle Autonomous Engineering Agent

従来のLevel 3に相当し、Nazuna Researchが目指す最終Capabilityである。完成やDeploymentを終端とせず、対象のLifecycleを継続的に自律運営する。

```text
Consulting
→ Research
→ Design
→ Build
→ Deploy
→ Operate
→ Monitor
→ Evaluate
→ Repair
→ Improve
→ Re-architect
→ Migrate／Retire
→ Next Cycle
```

User Experience上の要約は、**「これを作って回しておいて」と依頼すれば、Consultingから運用保守と継続改善まで長期的に回すAI**である。

## 4. 旧三段階との対応

| 旧区分 | 新区分 | 扱い |
|---|---|---|
| 旧Level 1 Development Agent | 新Level 1 | Capabilityを維持 |
| 該当なし | 新Level 2 | GD搭載のBounded Development段階として追加 |
| 旧Level 2 EEAE | 新Level 3 | End-to-End Capabilityを維持して番号を移動 |
| 旧Level 3 FCAE | 新Level 4 | Full-Cycle Capabilityを維持して番号を移動 |

過去文書のLevel番号を遡及改竄しない。将来の正本統合時に、旧番号、新番号、移行時点およびCapability Identityの対応を明示する。

## 5. Level 1〜4すべてを細分化する

各Levelを一つの巨大Work Packageとして実装・完成判定しない。Level 1にも通常AgentとしてのPlanning、Tool、Approval、State、Recovery、Evidence、UI等があり、Level 2以降はGD／Constitution／Actor分業が加わる。Level 3とLevel 4では、案件全体および長期Lifecycleの追加責任が発生する。

したがって、全Levelを少なくとも次の観点で段階化する。

1. Contract／Foundation：Identity、Authority、State、Port、Failure Boundaryを定義する。
2. Bounded Functionality：限定条件で中心機能を成立させる。
3. Integration：隣接Component、UI、Persistence、Evidence、Recoveryを接続する。
4. Operational Verification：実案件または実運用相当条件で検証する。
5. Acceptance：成立範囲、未成立範囲、Cost、Latency、Failure、Hardware条件を固定する。

これは現時点で全Levelを機械的に五つのSublevelへ固定する決定ではない。各Levelの規模と危険度に応じて、Work Package、Milestone、Acceptance Gateをさらに細かく分割するための原則である。大きな一括実装、長大Long Run、未検証の一括Completion Claimを避ける。

## 6. Capability、Governance、Topologyを混同しない

次の三軸を分離する。

```text
Capability Level:
  Development → Governed Development → End-to-End → Full-Cycle

Governance Composition:
  ARGD／DAGD／Constitution／Supervisory GD／Domain GD／Judge／Repair等

Execution Topology:
  Single Worker／Multi-Actor／Multi-Provider／Distributed Node等
```

Level 2以降ではGD系をCapabilityの重要要件とするが、Runtime実装を密結合にしない。個々のGD、Constitution、Judge、Repair、ProviderおよびNodeは、存在／不在、ON／OFF、交換、Failureおよび縮退を許容する。

Level 5を分散Nodeの別名として今すぐ追加しない。分散Nodeは現時点ではTopologyおよびAAGC／DLAGSA等との外部R&D連携事項である。将来、Level 4を超える固有Capabilityを定義した場合に限り、Level 5の必要性を別途判断する。

## 7. 導入順序

1. Phase 10 MVPを既定計画どおり優先する。
2. Phase 11以降、GD群とRuntime Constitutionの構造制御／意味評価を疎結合Componentとして成立させる。
3. Level 1を細分化し、通常Development Agentの安定した基礎を完成させる。
4. 新Level 2として、Governed Workstreamと必要時起動のMulti-GD Actor構成を段階導入する。
5. 新Level 3として、ConsultingからDeploymentまでのEnd-to-End Capabilityを段階導入する。
6. 新Level 4として、Operate以降を含む長期Full-Cycle Capabilityを段階導入する。
7. Dev Agentで安定後、必要なWorkstream Coreを通常Conversationへ応用する。

Exact Phase、Subphase、工数、名称、Sublevel数およびAcceptance Matrixは、各着手前の要件定義で決定する。

## 8. 不変条件

- 最終目的を「コードを書くAgent」または「GDを搭載したAgent」まで縮小しない。
- 新Level 4のConsultingから継続運用・次Cycleまでを無断で削らない。
- 新Level 2の追加を理由に、旧Level 2／3のCapability内容を削除しない。
- GD搭載を、全GD常駐、Judge必須または一つの共有Contextへの密結合へ変形しない。
- Levelの高さ、使用GD数、Model数、Actor数またはNode数を同一視しない。
- Level名称だけで完成をClaimせず、各段階の実測EvidenceとUser Acceptanceを要求する。
- Quota、時間、HardwareおよびMVP優先順位を無視して全Levelを同時着手しない。
- Codex ControllerはDocs、効率、一般論または局所実装を理由に、このLifecycle軸と最終目的を無断変更しない。

## 9. Current Disposition

```text
Four-Level Direction                 : AGREED AND RESERVED
Level 1 Development Agent            : FUTURE INCREMENTAL COMPLETION
Level 2 Governed Development Agent   : NEWLY INSERTED / FUTURE
Level 3 Governed End-to-End Agent    : FORMER LEVEL 2 / FUTURE
Level 4 Governed Full-Cycle Agent    : FORMER LEVEL 3 / FINAL TARGET
All-Level Fine-grained Decomposition : REQUIRED IN PRINCIPLE
Distributed Node as Level 5          : NOT DECIDED / SEPARATE TOPOLOGY
Phase 10 Scope Change                : NONE
Implementation Authority Now        : NOT GRANTED
Final Decision Authority            : NAZUNA RESEARCH
```

## 10. 関連予約

- `phase_8_margpa_development_agent_research_preview_and_phase_10_capability_levels_reservation_ja_20260828084745.md`
- `phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_ja_20260830170415.md`
- `phase_11_plus_governed_workstream_multi_gd_actor_dev_agent_first_and_distributed_node_future_reservation_ja_20260905180117.md`
- `phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md`

本記録は上記を削除・上書きせず、2026-09-05時点の最新User決定として四段階化と全Levelの段階的細分化を追加する。
