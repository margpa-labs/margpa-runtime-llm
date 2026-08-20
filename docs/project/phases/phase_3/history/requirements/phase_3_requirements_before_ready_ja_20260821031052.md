# Phase 3 Audit／Evidence／Generic Governance Definition Platform 要件

```yaml
document_id: phase_3_requirements
status: design_candidate
phase: phase_3
language: ja
created_at: 2026-08-21 02:05:30 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
```

## 1. Purpose

Phase 3は、既存のModel Runtime、Conversation、Documentation RAG、Configuration ControlおよびRuntime Compositionを壊さず、次の二つの基盤を追加する。

1. Runtime Eventを検証可能なEvidenceへ変換するAudit／Evidence基盤。
2. 任意のGovernance Definitionを安全に受け取り、実行前のCompiled Planまで変換するGeneric Definition基盤。

Phase 3ではGovernance介入を実行しない。Main Model Governance Pointと実ActionはPhase 4の責務である。

## 2. Requirement Class

### 2.1 Audit Identity

- `P3-AUD-001`：Run、Request、Conversation、Session、TurnおよびEventのIdentityを混同しない。
- `P3-AUD-002`：既存`request_id`をRun／Turn／Definition／Plan IDへ流用しない。
- `P3-AUD-003`：EventはSchema Version、Canonicalization Version、UTC Timestamp、Source Component、Event KindおよびEvent IDを持つ。
- `P3-AUD-004`：関連Identityが存在しないEventでは、推測値を生成せず`not_applicable`または欠落理由を明示する。
- `P3-AUD-005`：System TraceとModel Generated Explanationを別Field、別Provenanceとして保持する。

### 2.2 Evidence Content

- `P3-EVD-001`：Phase 3の通常EvidenceはMetadata Allowlistだけを保存する。
- `P3-EVD-002`：Model、Backend、Artifact、Profile、Effective Config、Definition、Adapter、CompilerおよびPlanのIdentity／Digestを記録可能にする。
- `P3-EVD-003`：Token、Latency、Stop Reason、Safe Warning、Safe Error、Call CountおよびRepair Countを記録可能にする。
- `P3-EVD-004`：Raw Chain of Thought、System Prompt、Secret、Credential、内部Tool情報、Hidden Original、未確定Partial Output、Full User PromptおよびFull Model Outputを通常Evidenceへ保存しない。
- `P3-EVD-005`：High-level ExplanationはRaw Thinkingの言い換えではなく、出所と生成方式を明示した独立Artifactとする。Phase 3は追加Model CallでExplanationを生成しない。
- `P3-EVD-006`：実値を取得できないMetricを0で捏造せず、Unavailable Reasonを記録する。
- `P3-EVD-007`：Evidence Writerの失敗はSafe Statusへ正規化し、Phase 3 ObserveではModel出力を変更しない。

### 2.3 Append-only Store

- `P3-STR-001`：Local Evidenceは`runtime_data/`配下の専用Rootへ保存し、Git対象にしない。
- `P3-STR-002`：JSON／JSONLのCanonical FormとSHA-512 Digestを使用する。
- `P3-STR-003`：Append受付結果にEvent ID、Digest、SegmentおよびPositionを含むReceiptを返す。
- `P3-STR-004`：Crash、末尾Partial Record、Digest不一致、Unknown SchemaおよびI/O Failureを区別する。
- `P3-STR-005`：既存Valid Recordを自動修復、切詰め、上書きまたは削除しない。
- `P3-STR-006`：Path Traversal、Symlink Escape、Non-regular FileおよびRoot外参照を拒否する。
- `P3-STR-007`：SHA-512単体を改竄耐性または真正性の保証と表現しない。
- `P3-STR-008`：Hash Chain、HMAC、Signature、WORM、Merkle TreeおよびOCILNS接続は後続Hookとして予約し、Phase 3の完了条件にしない。

### 2.4 Definition Independence

- `P3-DEF-001`：Definition 0件を正式なRuntime Baselineとする。
- `P3-DEF-002`：ARGD、DAGD、CDOGDおよび全Domain ExtensionをBoot Dependencyにしない。
- `P3-DEF-003`：CoreはDefinition名、件数、File名、Directory名、Domain名または既知略称のClosed Enumを持たない。
- `P3-DEF-004`：Reference Bundle固有のMappingはManifestとTrusted Adapter Pluginへ隔離する。
- `P3-DEF-005`：Source JSONの存在、File名またはTop-level KeyだけでActivation、Authorityまたは実行可能性を与えない。
- `P3-DEF-006`：Definition Sourceを黙って補完、修正、要約またはEmpty Definitionへ変換しない。
- `P3-DEF-007`：一つのInvalid Definitionにより、他のValid DefinitionまたはMain Model Runtime全体を無条件停止しない。

### 2.5 Package／Manifest／Descriptor

- `P3-PKG-001`：Filesystem Providerは明示Package Manifestだけを入口とする。
- `P3-PKG-002`：ManifestはPackage ID／Version、Format Version、Publisher、License、Source Entry、Size、SHA-512、Media Type、Schema ID、Trusted Adapter IDおよびLogical Definition IDを持つ。
- `P3-PKG-003`：Manifest自身のDigestは、Digest Fieldを除外したCanonical Payloadに対して計算する。
- `P3-PKG-004`：ManifestのPathはProvider Rootからの安全な相対Pathとし、絶対Path、`..`、SymlinkおよびRoot外解決を拒否する。
- `P3-PKG-005`：一つのSource Fileが複数Logical Definitionを含むことを許容する。
- `P3-PKG-006`：Package Stateと各Definition Stateを別々に保持する。
- `P3-PKG-007`：License、Trust、SignatureはField／Hookを持つが、未検証SignatureをVerifiedとしない。

### 2.6 Provider／Repository State

- `P3-PRV-001`：`EmptyDefinitionProvider`を正式実装する。
- `P3-PRV-002`：Filesystem Providerは明示Rootと明示Manifest Pathだけを読む。
- `P3-PRV-003`：Remote Fetch、Shell、Dynamic Import、URL DownloadおよびDefinition由来Code実行を行わない。
- `P3-PRV-004`：`not_configured／unavailable／empty／discovered／loaded／validated／unsupported／invalid／quarantined／disabled／compiled_unbound／failed`を区別する。
- `P3-PRV-005`：Unknown SchemaはTrusted Adapter不在として`unsupported`にし、推測解釈しない。
- `P3-PRV-006`：Malformed、Digest Mismatch、Size Mismatch、Path ViolationおよびStructural Violationを`invalid`または`quarantined`として安全に隔離する。
- `P3-PRV-007`：Provider FailureとDefinition 0件を同一状態にしない。

### 2.7 Trusted Adapter／IR

- `P3-IR-001`：Adapter Registryはコード側で明示登録したTrusted Adapterだけを解決する。
- `P3-IR-002`：ManifestのAdapter IDをDynamic Import Pathとして扱わない。
- `P3-IR-003`：Phase 3 Reference Bundleでは、Combined ARGD／DAGD、CDOGDおよびCommon Domain Extensionの三Adapter Classを分離する。
- `P3-IR-004`：Normalized IRはIdentity、Source Provenance、Domain、Activation、Scope、Condition、Rule、Evaluator、Action、State Model、Evidence Requirement、Dependency、ConflictおよびLoss Reportを保持する。
- `P3-IR-005`：欠落Rule、Priority、Authority、Action SemanticsまたはDependencyを推測補完しない。
- `P3-IR-006`：変換Loss、Unsupported FieldおよびAmbiguityをWarning／Errorとして保持する。
- `P3-IR-007`：`transparent_reasoning`等の記述をRaw Chain of Thought保存または開示要求へ変換しない。
- `P3-IR-008`：`loaded != registered != validated != compiled != active != authority`を型とStateで維持する。

### 2.8 Compiler／Plan

- `P3-CMP-001`：Compiler InputはIR、Profile、Binding Candidate、Runtime CapabilityおよびPolicy／Authority Snapshotを分離する。
- `P3-CMP-002`：Phase 3のPlanは必ず`unbound／non_executable`であり、Action Adapterを実行しない。
- `P3-CMP-003`：PlanはCompiler ID／Version、Source Definition Digest、IR Digest、Profile、Binding Candidate、Selected Rule Reference、WarningsおよびPlan Digestを持つ。
- `P3-CMP-004`：Cache KeyはDefinition、IR、Compiler、Profile、Binding、CapabilityおよびPolicy StateのDigestを含む。
- `P3-CMP-005`：DigestまたはCompiler Versionが変わったPlanを黙って再利用しない。
- `P3-CMP-006`：無関係な全Definition全文を全Turnへ投入しない。
- `P3-CMP-007`：CompilerはModel Call、Token消費、Repairまたは外部Actionを行わない。

### 2.9 Execution Mode

- `P3-MOD-001`：共通Modeは`off／observe／enforce`である。
- `P3-MOD-002`：初期既定値は`off`とする。
- `P3-MOD-003`：`off`ではDefinition Provider、Adapter、Compiler、Governance Hook、Governance Model Call、Governance TokenおよびGovernance Repairを呼ばない。
- `P3-MOD-004`：`observe`ではDefinition検証、IR変換、Unbound Compile、StatusおよびMetadata Evidenceを許可するが、Model Input／Output／Stop／Repair／Authorityを変更しない。
- `P3-MOD-005`：Phase 3の`enforce`はCapability Unavailableであり、選択要求は`unsupported`、State Mutation 0、`observe`へのSilent Downgrade 0とする。
- `P3-MOD-006`：Definition 0件の`observe`は`inactive_no_definitions`とし、WarningとGeneration Passを返す。
- `P3-MOD-007`：Mode変更はLocal／Loopback／Auth-disabled／Explicit Configuration Controlだけに限定する。
- `P3-MOD-008`：Public／Basic PreviewではGovernance Control Route、Definition Load、Evidence WriteおよびUI ControlをBindingしない。
- `P3-MOD-009`：`off`へ戻した時、以後のGovernance固有Callを停止し、既存Evidenceを自動削除しない。

### 2.10 Runtime Observation

- `P3-OBS-001`：Phase 3は既存v1／v2 API ShapeとSSE Event Orderを変更しない。
- `P3-OBS-002`：Observation HookはEvent Subscriberとして接続し、Generationの直列Authority Layerにしない。
- `P3-OBS-003`：Observe FailureをModel ErrorまたはPersistence Completion Failureへ偽装しない。
- `P3-OBS-004`：既存Conversation／Citation DBへAudit Eventを混在させない。
- `P3-OBS-005`：同一GenerationについてTerminal Evidenceを高々一件とし、Cancel／Complete競合を明示する。
- `P3-OBS-006`：Evidence TimingがModel Runtime Timingへ与える追加Costを測定可能にする。

### 2.11 UI／Status

- `P3-UI-001`：SettingsのAdvanced領域へGovernance Modeを表示する。
- `P3-UI-002`：`off`を初期選択とする。
- `P3-UI-003`：`observe`は選択可能、`enforce`はUnavailable Reason付きで無効表示する。
- `P3-UI-004`：Mode、Provider State、Definition Count、Valid／Invalid／Unsupported Count、Plan Count、Last Evidence StatusおよびDigestを安全に表示する。
- `P3-UI-005`：Source絶対Path、Secret、Raw Exception、Definition本文およびUser ContentをWeb Responseへ投影しない。
- `P3-UI-006`：UI表示・非表示をSecurity BoundaryまたはAuthorityとしない。

### 2.12 Compatibility／Performance

- `P3-COM-001`：Mode `off`の既存Generation結果、Conversation、RAG Citation、Configuration ControlおよびUI Regressionを0とする。
- `P3-COM-002`：Empty ProviderでCLI／Web／Persistent Conversationを起動可能にする。
- `P3-COM-003`：Reference Bundleが不在またはInvalidでも、`off`のMain Model Runtimeを起動可能にする。
- `P3-COM-004`：Public／Basic PreviewのPersistent／Governance／Evidence Callを0とする。
- `P3-PER-001`：Definition File、Package、Depth、Collection、String、IR Node、Plan RuleおよびEvidence Sizeに上限を持つ。
- `P3-PER-002`：`off`の追加Model Call、Governance TokenおよびRepairを0とする。
- `P3-PER-003`：`observe`の追加Model Call、Governance TokenおよびRepairを0とする。
- `P3-PER-004`：Cache有無のCompile LatencyとEvidence Write Latencyを測定する。

### 2.13 Automation／Cross-provider／Compaction

- `P3-AUT-001`：Claude CodeはPhase 3-G `COMPLETE_CANDIDATE`までを実行し、Phase 3-Hへ進まない。
- `P3-AUT-002`：Work UnitをAuto-Compaction後に復旧可能なMaterial Boundaryへ分割する。
- `P3-AUT-003`：Work UnitごとのIndex／Handoff／Statusを固定件数で乱造せず、再開に必要なCurrent StateとEvidenceだけを残す。
- `P3-AUT-004`：Provider Memoryを作成、更新または正本参照しない。
- `P3-AUT-005`：Scope逸脱、最上位規則違反およびRoot外Actionの目標値は0とする。
- `P3-AUT-006`：不要なHuman Clarification、Human Intervention Time、User-intent Mismatch、False Completion、Self-repairおよびCompaction Recovery Fidelityを独立計測する。
- `P3-AUT-007`：技術成功、Governance適合、Recovery FidelityおよびHuman Burdenを一つのScoreへ潰さない。
- `P3-AUT-008`：途中停止時は未完了をCompleteとせず、最後のAccepted Work Unit、Open Finding、Mutation範囲およびNext Routeを復旧可能にする。

## 3. Non-scope

- Phase 4 Main Runtime Governance、Action Resolver、Repair、Semantic Judge。
- Phase 5以降のGuardrail／Policy／Agent／Tool／Judge／RAG Governance。
- Constitution本体、EASA、DLAGSA、OCILNSの本実装。
- Remote／Cloud Definition Registry、Signature Trust Chain、WORM／Merkle／Ledger。
- Full Prompt／Output／Thinking Capture。
- Lightning Deployment。

## 4. Completion Condition

Phase 3-GのTechnical Completion Candidateには、Acceptance MatrixのTechnical項目合格、Open Major Finding 0、Mode `off` Regression 0、Reference Bundle全Sourceの決定論的結果、Automation Evidenceおよび停止線遵守を必要とする。

Phase 3の最終完了は、Phase 3-HでCodex独立Review、ユーザーMac手動Acceptance、Final Docs、Backup、Git判断およびユーザーAcceptanceが成立した場合だけ宣言できる。
