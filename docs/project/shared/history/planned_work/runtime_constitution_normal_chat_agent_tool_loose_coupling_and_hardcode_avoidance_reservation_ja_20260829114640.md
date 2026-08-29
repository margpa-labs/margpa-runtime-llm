# Runtime Constitution通常Chat適用／GD疎結合／Hard-code回避予約

```yaml
document_id: runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_20260829114640
document_type: planned_work_architecture_reservation
document_state: reserved_not_authorized
language: ja
created_at: 2026-08-29 11:46:40 JST
decision_authority: user
authority_owner: Nazuna Research
target_runtime_directory: <margpa-runtime-llm-project-root>/constitution/
phase_8_scope: provisional_runtime_constitution_foundation
phase_10_scope: full_runtime_constitution_after_shared_constitution_and_PADG
architecture_style: loose_coupling_replaceable_providers
hardcode_policy: avoid_to_maximum_practical_extent
roadmap_integration_gate: phase_6_closure_pre_gate
implementation_authority: not_granted
```

## 1. 対話起点と結論

本予約は、Userの次の問いから始まった議論をLosslessに設計予約へ固定する。

```text
通常スレでもconstitutionを使えるか。
既存ARGD／DAGD／AAGD等と競合しないか。
ConstitutionがGDを選択・統括する形は、MARGPA Runtime LLMの疎結合Conceptに反して密結合ではないか。
密結合とHard-codeを、可能な範囲で全力で回避する。
```

現行結論は次のとおりである。

1. Runtime ConstitutionはAgent専用に閉じず、通常Chatにも適用可能なRuntime-wide Packageとする。
2. 通常Chat、Agent、Toolへ同じ条文を無差別適用せず、Common CoreとCapability別Viewを分ける。
3. ConstitutionをARGD／DAGD／AAGD等の親Componentまたは直接Selectorにしない。
4. ConstitutionとGD群は独立Providerとして並列評価し、Generic Result Contractを通してResolverへ接続する。
5. Constitution Coreへ固有GD名、Model名、Provider名、Tool名またはProject内の固定実装をHard-codeしない。
6. Phase 8ではこの疎結合基盤を暫定実証し、本格編纂はPhase 10で行う。

## 2. 通常ChatへのConstitution適用

`margpa-runtime-llm/constitution/`は、最終的にAgentだけでなくRuntime全体へ適用可能な構造とする。

概念構造：

```text
constitution/
├─ common/
├─ views/
│  ├─ chat/
│  ├─ agent/
│  └─ tool/
├─ bindings/
├─ schemas/
└─ manifest/
```

Directory名はPhase 8／10の設計で変更可能だが、論理分離は維持する。

### 2.1 Common Constitution候補

- Authorityの存在確認。
- Evidence／Audit要件。
- Privacy／Secret／Data境界。
- Budget／Latency／Stop／Failure収束。
- Revision／Digest／View整合。
- User Sovereignty。
- Capability Scope外Actionの拒否。

### 2.2 Chat View候補

- Userの前提、制約および会話Context保持。
- 根拠なき断定、矛盾、CitationおよびEvidenceの扱い。
- Judge／Repair／Safe Fallback。
- 回答言語、出力形式、Branch、RecordingおよびConversation Persistence。
- ChatでToolを使う場合の提案、Permission、Approvalおよび実行の分離。

### 2.3 Agent View候補

- Planning、Step、Replanning、Completion。
- Tool選択、Handoff、Memory、Recovery。
- Approval／Autonomy Envelope。
- Long-running、Scheduler、Multi-Agent候補。

### 2.4 Tool View候補

- Tool Capability Metadata。
- Permission、Authority、Approval、Budget。
- Side Effect、Idempotency、Rollback、Evidence。
- Native Tool／MCP Adapter境界。

通常ChatへAgent専用のMulti-step Planning、Sub-Agent、Git、Deploy等の条文を自動適用しない。

## 3. Constitution Mode

Common／Chat／Agent／Toolは、必要に応じて独立したConstitution Modeを持てる構造とする。

```text
OFF
OBSERVE
ENFORCE
```

- Constitution OFFは、GD、Guardrail、Judge、Platform Security、Sandboxまたは既存AuthorityのOFFを意味しない。
- GD OFFはConstitution OFFを意味しない。
- Chat Constitution ONはAgent／Tool Authorityを生成しない。
- Agent Constitution ONはTool Constitution、Tool PermissionまたはHuman Approvalを自動的にONにしない。
- Mode間連動が必要な場合も、暗黙Hard-codeではなくVersioned Dependency／Activation Contractで表す。

## 4. 一度提示された階層案と訂正

議論途中で、次の階層案が提示された。

```text
Platform Security／Authority
→ Constitution
→ ARGD／DAGD／AAGD等を選択
→ GD Evaluation
→ Resolver
```

この表現ではConstitutionがGD群の親Selectorとなり、Constitution CoreがGD Identity、適用順または意味を知る必要がある。これはMARGPA Runtime LLMの次のConceptに反する。

- Generic Governance Definition。
- GD不在でもCoreが動く。
- 任意GDへ交換可能。
- Source JSON不変。
- Provider／Adapter／Compiler／Selectionの分離。
- Component間の疎結合。

したがって、この階層案は現行設計として却下し、本予約でSupersedeする。

## 5. 現行疎結合Architecture

ConstitutionとGD群は、同じRuntime Eventを受け取れる独立Provider群として扱う。

```text
                         ┌─ Constitution Provider／View ─┐
Runtime Event／Snapshot ─┤                               ├─ Generic Resolver ─ Action Resolver
                         └─ GD Orchestrator／Providers ──┘
                               ├─ 任意GD Adapter A
                               ├─ 任意GD Adapter B
                               └─ 任意GD Adapter N
```

### 5.1 Constitutionの責務

- GenericなAuthority／Approval／Scope／Budget／Evidence／Failure境界を評価する。
- Capability Viewへ適用可能なConstitution Clauseを解決する。
- Constitution固有Observation／Recommendation／ConstraintをGeneric Resultとして返す。
- 固有GDを選択、実行または内部Importしない。

### 5.2 GD側の責務

- Generic Definition Registry／Provider／Adapter／Compiler／Selectionを使う。
- 各GD固有の意味Ruleを評価する。
- Applicability、Observation、Deviation、Severity、RecommendationおよびEvidenceをGeneric Resultへ変換する。
- Constitutionの存在を前提にしない。

### 5.3 Resolverの責務

- Constitution ResultとGD Resultを同じGeneric Envelopeで受け取る。
- Source IdentityとNamespaceを失わず保持する。
- Priority、Authority、Scope、Specificity、Conflict StrategyおよびModeに基づいてAction候補を解決する。
- 解決不能Conflictを多数決、Provider順または固定if文で隠さない。
- 解決不能時はDeferred、Safe FallbackまたはHuman Gateへ正確に収束する。

## 6. Generic Result Contract候補

Constitution CoreおよびResolverは、ARGD／DAGD／AAGD等の固有結果型を直接参照せず、次のようなVersioned Generic Envelopeだけを扱う。

```text
GovernanceResultEnvelope
├─ result_id
├─ source_kind
├─ source_id
├─ namespace
├─ contract_version
├─ revision／digest
├─ capability_scope
├─ applicability
├─ outcome／severity
├─ observations
├─ recommendations
├─ required_authority
├─ required_approval
├─ budget_effect
├─ evidence_references
└─ failure／deferred_reason
```

Exact FieldはPhase 8設計時にFreezeする。この予約はField追加やSchema実装のAuthorityを与えない。

## 7. GD Bindingの外部化

Constitutionへ固有GD名を埋め込まず、GDの発見・選択・接続は次の外部Componentへ置く。

- Definition Registry。
- Capability／Applicability Metadata。
- Provider Manifest。
- Versioned Binding Manifest。
- Orchestrator／Selection Policy。
- Adapter Registry。
- Runtime Composition。

例：

```text
Agent Event
→ Generic GD Selection Port
→ Registryが適用候補を返す
→ Adapter経由で評価
→ Generic Envelope
```

Constitution Sourceを変更せずに、GD追加、削除、交換または複数同時稼働ができることをAcceptanceにする。

## 8. Hard-code回避Policy

可能な範囲で、次をCore SourceへHard-codeしない。

- `ARGD`、`DAGD`、`AAGD`等のDefinition ID。
- 個別GDのDirectory Path。
- Qwen、DeepSeek、Selene、Qwen3Guard等のModel／Provider ID。
- Codex、Claude、Copilot等の開発Provider名。
- Tool ID、MCP Server名、Command名。
- Role名、Capability表示名。
- Phase番号に依存するRuntime分岐。
- UI Labelを判定に使うLogic。
- Provider数、GD数、Tool数、View数。
- 優先順位を固定した巨大if／elif Chain。

### 8.1 Hard-codeを許容し得るもの

完全なHard-code 0を目的化しない。次は、理由、Version、MigrationおよびTestがある場合に限り固定可能とする。

- Protocolの最小Enum／State Machine。
- Security上変更不能なFail-closed Invariant。
- Schema VersionのBootstrap値。
- Canonical Generic Field名。
- 明示的にVersion Freezeされた外部Contractの検証定数。

固定値を置く場合も、Provider固有処理をCoreへ混入させず、Adapter／Manifest／Contract Moduleへ隔離する。

## 9. 疎結合Acceptance

Phase 8暫定版とPhase 10本格版で、少なくとも次を検証する。

1. Constitution PackageなしでもGD Runtimeが動く。
2. GD 0件でもConstitution Evaluatorが動く。
3. Constitution OFFでもGDを独立してOBSERVE／ENFORCEできる。
4. GD OFFでもConstitutionを独立してOBSERVE／ENFORCEできる。
5. ARGD等を別GDへ交換してもConstitution Source変更0。
6. 新GD追加時にConstitution Source変更0。
7. 通常Chat View追加時にAgent Core変更0。
8. Tool Provider交換時にConstitution Core変更0。
9. Binding Manifest変更がRevision／Digest／Evidenceへ反映される。
10. 未知Provider／未知GD／未知ViewはHard-coded Fallbackで誤実行せず、Typed FailureまたはDeferredになる。
11. Constitution ResultとGD ResultのSource IdentityがResolver後も消失しない。
12. Conflict解決不能時に多数決または登録順で黙って決定しない。

## 10. Phase配置

### Phase 8

- Runtime-wide Constitution PackageのSkeleton。
- Common／Chat／Agent／Tool Viewを追加可能なSchema。
- OFF／OBSERVE／ENFORCE基盤。
- Constitution ProviderとGD Providerの並列接続Port。
- Generic Result Envelope／Resolverの最小Prototype。
- Fake／Deterministic Constitution／GD／Toolによる疎結合Test。
- Agent Research Previewに必要な範囲だけのBounded Constitution。

通常Chatへの本格適用をPhase 8 Completion Claimへ必須化せず、後付け可能性と最小View実証を優先する。

### Phase 10

- Phase 3〜9 Docs統合。
- `docs/project/shared/constitution/`。
- PADG Package。
- 全Docs二周走査。
- Runtime-wide Constitutionの本格編纂。
- Chat／Agent／Tool各Viewの正式Acceptance。
- Full Conflict／Migration／Compatibility／Evidence検証。

## 11. Phase 6 Closure手前のRoadmap統合予約

Phase 6 Closure手前のRoadmap一括更新で、通常版と要約版へ次を統合する。

- Runtime Constitutionは通常Chatにも適用可能な構造とする。
- Common／Chat／Agent／Tool Viewを分離する。
- ConstitutionとGD群を親子関係にせず、独立ProviderとしてGeneric Resolverへ接続する。
- Constitution Coreへ固有GD名をHard-codeしない。
- Phase 8は疎結合Foundation、Phase 10はDocs統合後の本格版。

## 12. Reservation State

```text
Normal Chat Constitution View        : RESERVED
Agent Constitution View              : RESERVED
Tool Constitution View               : RESERVED
Constitution／GD Parallel Providers   : RESERVED
Generic Result／Resolver Prototype    : RESERVED FOR PHASE 8 DESIGN
Maximum Practical Hard-code Avoidance: REQUIRED DESIGN PRINCIPLE
Phase 10 Full Runtime Constitution    : RESERVED
Current Implementation               : NOT AUTHORIZED
Current Roadmap Mutation              : DEFERRED TO PHASE 6 CLOSURE PRE-GATE
```

## 13. Related Reservation

- `phase_8_provisional_and_phase_10_full_runtime_agent_constitution_staging_reservation_ja_20260829113647.md`
- `phase_8_margpa_development_agent_research_preview_and_phase_10_capability_levels_reservation_ja_20260828084745.md`
- `phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md`
