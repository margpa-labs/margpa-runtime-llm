# Phase 8暫定版／Phase 10本格版 Runtime Agent Constitution段階分離予約

```yaml
document_id: phase_8_provisional_and_phase_10_full_runtime_agent_constitution_staging_reservation_20260829113647
document_type: planned_work_reservation
document_state: reserved_not_authorized
language: ja
created_at: 2026-08-29 11:36:47 JST
decision_authority: user
authority_owner: Nazuna Research
target_runtime_directory: <margpa-runtime-llm-project-root>/constitution/
phase_8_target: provisional_bounded_runtime_agent_constitution
phase_10_target: full_runtime_agent_constitution_after_shared_constitution_and_PADG
roadmap_update_gate: immediately_before_phase_6_closure
implementation_authority: not_granted
```

## 1. 予約の目的

製品Runtime内のAgent／Toolへ適用する`margpa-runtime-llm/constitution/`は、Phase 8とPhase 10以降で完成度を明確に分ける。

Phase 8時点ではPhase 3〜9の全Docs統合、`docs/project/shared/constitution/`の完全編纂およびPortable Autonomous Development Governance Package（PADG Package）が未成立である。その状態でRuntime Agent Constitutionを完全版としてFreezeすると、未収録Rule、旧Ruleの誤昇格、Provider固有運用と製品Runtime規則の混同、後続Docs統合との矛盾が発生し得る。

したがって、Phase 8ではAgent Research Previewを動かすための暫定・有界なConstitution基盤だけを作り、本格版はPhase 10のShared Constitution／PADG Package成立後に作る。

## 2. 二つのConstitution境界

次を混同しない。

### A. 開発体制／移植用Constitution

```text
docs/project/shared/constitution/
```

対象：

- Automation。
- Cross-provider。
- Manual／Auto Compaction Recovery。
- Agent間Role分離。
- Codex Task間情報共有／伝達。
- Authority、Handoff、Review、Rework、Evidence、Docs運用。
- `common／Codex／Claude／Copilot`のProvider-neutral／Provider-specific分離。
- PADG PackageのCanonical Source。

### B. 製品Runtime Agent／Tool用Constitution

```text
<margpa-runtime-llm-project-root>/constitution/
```

対象：

- MARGPA Runtime上のAgent／Tool／Memory／Handoff。
- Capability、Role、Action、Tool Permission、Approval、Budget。
- Agent／Tool Governance Point。
- Agent実行時のConstitution Mode、Evaluation、EvidenceおよびEnforcement。

Shared ConstitutionまたはPADG Packageの存在だけで、Runtime AgentへAuthorityを自動付与しない。

## 3. Phase 8 — 暫定Runtime Agent Constitution

Phase 8では`margpa-runtime-llm/constitution/`を作成できる。ただし最大Claimは次とする。

```text
Provisional Runtime Agent Constitution
Constitution Research Preview v0.x
Bounded Constitution View
Foundation／Hook／Schema／Mode実証
```

`Full`、`Complete`、`Lossless`、`Production Constitution`または全Project Rule統合済みとは表記しない。

### 3.1 Phase 8対象

- Directory／Package Skeleton。
- Constitution Manifest、Schema Version、Revision、Digest。
- Runtime Agent／Tool向けの最小Constitution View。
- 対象Capability／Role／Provider／Tool Binding。
- Constitution Modeの基盤。
- Mode別Evaluation／Evidence／Action境界。
- Stale Revision、Digest不一致、View不足時の正確なFailure。
- Fake／Deterministic／限定Local Toolでの最小実証。
- Phase 8時点でAccepted済みのRuleだけをBounded Sourceとして採用。

### 3.2 Mode

Phase 8では比較研究と段階導入のため、少なくとも次のModeを扱える基盤を作る。

```text
OFF
OBSERVE
ENFORCE
```

- `OFF`：Constitution固有Evaluation／Actionを行わない比較Baseline。ただしOS Sandbox、Platform Security、Access Control、既存Authority、法令および開発環境の禁止事項を解除しない。
- `OBSERVE`：適用Rule、Deviation、推奨ActionおよびEvidenceを記録するが、Constitution固有Actionを強制しない。
- `ENFORCE`：有効なRevision／Digest／View／Authority／Approvalが成立した範囲だけで、定義済みActionを実行する。不足時に黙ってOBSERVEまたはOFFへFallbackしない。

Mode Buttonまたは表示の有無だけで実行Authorityを発生させない。

### 3.3 Phase 8で含めないもの

- Phase 3〜9全Docsの完全Lossless統合。
- `docs/project/shared/constitution/`の正式完成。
- PADG Packageの正式完成。
- 全Provider／全Task／全Incident／全Automation Evidenceの完全反映。
- Level 1 MARGPA Development Agentの正式完成。
- Level 2／3 Agent Capability。
- Production／Enterprise-grade Constitution。
- 広範なRemote Tool、Git、Network、Deployまたは外部Account Authority。

## 4. Phase 10 — 本格Runtime Agent Constitution

本格的な`margpa-runtime-llm/constitution/`は、Phase 10で次の順序を経た後に作る。

```text
Phase 3〜9 Docs Lossless Compilation
→ 全Docs第1周走査
→ docs/project/shared/constitution/ Canonical Candidate
→ PADG Package初版
→ 全Docs第2周走査／Gap Audit
→ Shared Constitution／PADGの必要訂正・Freeze
→ Runtime Agent／Tool向けRule抽出・変換
→ 本格 margpa-runtime-llm/constitution/ 作成
→ Phase 8暫定版からのMigration／Compatibility検証
```

### 4.1 Phase 10本格版の要件

- Phase 8暫定版との差分とMigrationを記録する。
- Shared Constitution／PADGからRuntimeへ採用したRuleのSource Pointerを保持する。
- Provider固有開発運用Ruleを製品Runtimeへ無差別に移植しない。
- Product固有Capability、Tool、Memory、Handoff、ApprovalおよびEvidenceへ再構成する。
- Rule ID、Revision、Digest、Manifest、View、Schemaおよび改憲手続きをFreezeする。
- Runtime Agent向けに必要なRuleだけを抽出し、Shared／Portable PackageからAuthorityを自動継承しない。
- OFF／OBSERVE／ENFORCEの意味とFailure Contractを本格Acceptanceする。
- Level 1以降のAgent Capability Contractと結び付ける。

## 5. Phase 8暫定版の扱い

Phase 8暫定版は使い捨てにしない。Phase 10本格版のPrototype／Migration Sourceとして保持する。

ただし、次を禁止する。

- 暫定Ruleを根拠なく恒久Ruleへ昇格する。
- Phase 8の不足を隠して完全版とClaimする。
- Phase 10でDirectoryを無言Overwriteし、旧Revision／Evidenceを失う。
- Shared Constitution／PADGの全内容をRuntime Constitutionへ丸ごとCopyする。

## 6. Phase 6 Closure手前のRoadmap更新予約

Phase 6 Closure手前で行うRoadmap一括更新時に、次の二段階を`docs/public/roadmap_ja.md`および`docs/public/roadmap_summary_ja.md`へ明記する。

### Phase 8記載

- `margpa-runtime-llm/constitution/`はAgent Research Preview用の暫定・有界基盤。
- OFF／OBSERVE／ENFORCE、Manifest／Revision／Digest／View／Hookの最小実証。
- Phase 3〜9全Docs統合前であり、完全Constitutionとは主張しない。

### Phase 10記載

- Phase 3〜9 Docs統合、全Docs二周走査、`docs/project/shared/constitution/`およびPADG Package成立後に、本格Runtime Agent Constitutionを作る。
- Phase 8暫定版からのMigration、Rule Source、Compatibilityおよび正式Acceptanceを行う。

既存Roadmapに近い記載が存在しても、Phase 6 Closure手前の更新でこの順序と完成度差を曖昧さなく統合する。

## 7. Reservation State

```text
Phase 8 Provisional Runtime Constitution : RESERVED
Phase 10 Full Runtime Constitution        : RESERVED
Phase 6 Closure Roadmap Update            : RESERVED
Current Directory Creation                : NOT AUTHORIZED
Current Implementation                    : NOT AUTHORIZED
Current Roadmap Mutation                  : DEFERRED UNTIL PHASE 6 CLOSURE PRE-GATE
```

本予約だけでPhase 8／10作業、Directory作成、Roadmap更新、Agent／Tool Authority付与または外部Actionを開始しない。

## 8. Related Reservations

- `phase_8_margpa_development_agent_research_preview_and_phase_10_capability_levels_reservation_ja_20260828084745.md`
- `phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md`
- `pre_phase_8_portable_margpa_constitution_package_and_runtime_identity_ja_20260822150342.md`
