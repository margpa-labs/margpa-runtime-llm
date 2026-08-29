# Phase 6 Closure手前 — Phase 10 Constitution／Portability化・旧Phase 10のPhase 11移行予約

```yaml
document_id: phase_6_closure_pre_gate_phase_10_constitution_portability_and_phase_11_hardening_roadmap_restructure_reservation_20260829120117
document_type: planned_work_schedule_and_roadmap_update_reservation
document_state: reserved_not_executed
language: ja
created_at: 2026-08-29 12:01:17 JST
decision_authority: user
authority_owner: Nazuna Research
execution_gate: immediately_before_phase_6_closure
roadmap_targets:
  - docs/public/roadmap_ja.md
  - docs/public/roadmap_summary_ja.md
current_roadmap_mutation: prohibited_until_gate
```

## 1. 予約内容

Phase 6 Closure手前のRoadmap一括更新で、Constitution段階分離とPhase 10／11再編を同時に反映する。

現時点ではRoadmapを変更しない。過去History、旧Reservationおよび旧Phase番号のEvidenceも変更しない。新RoadmapとSchedule Correctionにより、今後の現行計画だけをSupersedeする。

## 2. 新Phase境界

```text
Phase 9
Experiment and Multi-Governance Research Platform
        ↓
Phase 10
Governance Consolidation, Constitution, and Portability
        ↓
Phase 11
Hardening, Cloud Scale, and External R&D Integration
```

Phase 10を、中途半端にDocs統合とHardeningが混在するPhaseにしない。Phase 10はGovernance、Constitution、移植性および正式編纂へ集中させる。

## 3. Phase 10へ置くもの

- Phase 3〜9 Docs Lossless Compilation。
- 全Docs第1周走査。
- `docs/project/shared/constitution/`のCanonical Candidate／正式編纂。
- Common／Codex／Claude／CopilotのProvider-neutral／Provider-specific分離。
- Portable Autonomous Development Governance Package（PADG Package）初版。
- 全Docs第2周走査、Gap／Coverage／Provenance／Sanitization Audit。
- PADG Package第2版または必要なCorrection。
- Phase 1-EXのPhase 1統合等、Portable Directory構造整理。
- Phase 8暫定`margpa-runtime-llm/constitution/`から、本格Runtime-wide ConstitutionへのMigration。
- Common／Chat／Agent／Tool Constitution View。
- ConstitutionとGD群の並列独立Provider化、Generic Result／Resolver、疎結合Acceptance。
- 最大限のHard-code回避とBinding／Registry／Manifest外部化。

## 4. Phase 11へ移すもの

旧Phase 10のうち、次をPhase 11へ一括移行する。

- Product／Enterprise Hardening。
- Cloud／AWS／GPU Server Scale。
- Multi-model Backend本格拡張。
- External R&D Integration。
- Context Observatory本格化。
- ML／Training拡張。
- Responsive UI本格対応。
- Long-term Audit、Hash Chain、WORM等。
- 高度Agent、Remote Tool、Generic MCP、Dynamic Sub-Agent、Multi-Agent Organization。
- Phase 10 Constitution／PADG完成後に行うべき外部Provider追加・移植実証。

従来`Phase 10以降`と記載した予約は、内容に応じて次のように再分類する。

```text
Docs／Shared Constitution／PADG／Runtime Constitution
→ Phase 10

Product Hardening／Cloud／高度Agent／外部統合／大規模運用
→ Phase 11以降
```

## 5. Constitution関連の同時反映

Phase 6 Closure手前のRoadmap更新では、次の既予約を一体として統合する。

- Phase 8は暫定・有界なRuntime Constitution Foundation。
- Phase 8のMode基盤はOFF／OBSERVE／ENFORCE。
- Runtime ConstitutionはAgent専用に閉じず、通常Chat／Agent／ToolへCapability Viewを追加可能にする。
- ConstitutionとARGD／DAGD／AAGD等のGD群を親子関係にしない。
- ConstitutionとGD群を並列独立ProviderとしてGeneric Resolverへ接続する。
- 固有GD、Model、Provider、Tool、RoleおよびPhase番号のHard-codeを最大限避ける。
- Phase 10でShared Constitution／PADG成立後、本格Runtime Constitutionを作成する。

## 6. Phase 6 Closure手前のExact Update Scope

次の2文書を同じ作業Cycleで更新する。

```text
docs/public/roadmap_ja.md
docs/public/roadmap_summary_ja.md
```

更新時に確認する。

1. Phase一覧表にPhase 11を追加する。
2. Phase 10の名称、目的、Entry／Exit、成果物をConstitution／Portability中心へ変更する。
3. 旧Phase 10のHardening項目をPhase 11へ移す。
4. `Phase 10以降`予約を内容別にPhase 10／Phase 11以降へ再分類する。
5. Phase 8暫定ConstitutionとPhase 10本格Constitutionの完成度差を明記する。
6. 通常Chat／Agent／Tool View、GD疎結合、Hard-code回避を簡潔に記載する。
7. Roadmap通常版と要約版のPhase番号、名称、順序および説明を一致させる。
8. 過去HistoryのPhase表記を遡及変更しない。

## 7. Related Reservations

- `phase_8_provisional_and_phase_10_full_runtime_agent_constitution_staging_reservation_ja_20260829113647.md`
- `runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_ja_20260829114640.md`
- `phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md`
- `phase_7_phase_9_phase_10_closure_ready_sequence_correction_ja_20260823192316.md`

## 8. Reservation State

```text
Phase 10 Constitution／Portability再編 : RESERVED
旧Phase 10 → Phase 11移行            : RESERVED
Roadmap通常版更新                     : DEFERRED TO PHASE 6 CLOSURE PRE-GATE
Roadmap要約版更新                     : DEFERRED TO PHASE 6 CLOSURE PRE-GATE
Past History Renumbering               : PROHIBITED
Current Implementation                 : NOT AUTHORIZED
```
