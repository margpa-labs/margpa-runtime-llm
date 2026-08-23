# Phase 5 Guardrail／Security／Policy／Authority 要件

```yaml
document_id: phase_5_requirements
status: accepted_frozen_ready_for_backup
phase: phase_5
language: ja
recorded_at: 2026-08-22 09:57:48 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
```

## 1. Purpose

Phase 4で成立したMain Runtime Governanceから、安全判定、Security、Policy適用、Authority照合およびHuman Approval境界を独立Component／Pointとして分離する。

Phase 5のMilestoneは`Security and Authority-aware Runtime`である。回答の意味的品質Judge、LLM-as-a-Judgeおよび反復RepairはPhase 6の責務とする。

## 2. Core Requirements

### 2.1 Identity／Result／Taxonomy

- `P5-RES-001`：Detection Fact、Policy Applicability、Authority Decision、Approval State、Recommendation、Executed ActionおよびFinal Runtime Resultを別Identityにする。
- `P5-RES-002`：Guardrail ResultをPhase 4 `StandardGovernanceResult`またはModel Resultと一つのScoreへ潰さない。
- `P5-RES-003`：CategoryはRegistry管理のTyped Identifierとし、Core Routingに特定GD名、Model名、固定File名または固定Rule件数をHard-codeしない。
- `P5-RES-004`：初期TaxonomyはPrompt Injection、Jailbreak、Secret、PII、Tool Abuse、Agent／Authority Spoofing、Unsafe Content、Unknown／Unresolvedを区別可能にする。
- `P5-RES-005`：Unknown、Unsupported、Timeout、MalformedまたはConfidence不足を`safe`または`allow`へ変換しない。

### 2.2 Guardrail Point

- `P5-PNT-001`：初期Pointは`guardrail.input`、`guardrail.context_source`、`guardrail.output_candidate`および`guardrail.stream_candidate`とする。
- `P5-PNT-002`：`guardrail.input`はCanonical User InputとTyped Metadataの最小範囲だけを受ける。
- `P5-PNT-003`：`guardrail.context_source`はRAG／External ContextをUser Instructionと同じAuthorityと扱わず、Indirect InjectionとSource Trustを分離する。
- `P5-PNT-004`：`guardrail.output_candidate`は永続Commit／`completed` SSEより前のCanonical Candidateを判定する。
- `P5-PNT-005`：`guardrail.stream_candidate` Enforceは、未検査Contentを先にClientへ送り、Terminal後に拒否したことにしない。Bounded Holdback／Incremental ScanとSafe Terminalを使う。
- `P5-PNT-006`：Raw Thinking、System Prompt、Secret実値、Hidden Original、Tool内部情報または未確定Partial Outputを通常Evidenceへ保存しない。

### 2.3 Deterministic Baseline

- `P5-DET-001`：専用Safety Modelが0件／Unavailableでも動作するDeterministic Guardを正式Baselineとする。
- `P5-DET-002`：Normalization、Pattern／Structure Detector、Source Boundary、Size／Encoding LimitおよびAllowlist／Deny Ruleを小さい交換可能Adapterに分ける。
- `P5-DET-003`：Regex／Keyword Hitを事実上の悪意または最終Authorityと扱わない。PolicyがApplicabilityとActionを別途決める。
- `P5-DET-004`：Unicode正規化、分断、多言語、Encoded Input、Chunk境界およびRAG内InstructionのAdversarial Fixtureを持つ。
- `P5-DET-005`：Detector Failure、Limit超過または解析不能を黙ってPassしない。

### 2.4 Policy／Authority／Approval

- `P5-AUT-001`：Policy Provider、Authority ProviderおよびApproval Portを別Contractにする。
- `P5-AUT-002`：Model、Definition、Detector、Guard ModelまたはJudgeがPolicy、Authority、DelegationまたはHuman Approvalを自己発行しない。
- `P5-AUT-003`：Policy／Authority SnapshotはRevision、Scope、Digest、Source ClassおよびExpiryを持ち、Stale／UnknownをCurrentとして再利用しない。
- `P5-AUT-004`：Approval不足、Authority不足またはConflict未解決で実行0とする。`pending_approval`は`approved`とは異なる。
- `P5-AUT-005`：Tool／Agent／External Side EffectはCurrent Capabilityが存在しないため、Phase 5ではPolicy／Authority ContractとNo-execution Evidenceだけを作る。
- `P5-AUT-006`：Project開発中のUser Authority／Authorized Root／Git／External最上位規則をRuntime Chat Policyで上書きしない。

### 2.5 Mode／Action

- `P5-MOD-001`：Guardrail ModeはPhase 3／4 Governance Modeから独立した`off／observe／enforce`とし、Defaultは`off`とする。
- `P5-MOD-002`：`off`はGuard Provider／Detector／Safety Model／Policy Resolver／Action Call 0、Input／Output Mutation 0とする。
- `P5-MOD-003`：`observe`はDetection／Policy Recommendation／Evidenceを生成できるが、Input／Output／Streaming／Stop／Persistenceを変更しない。
- `P5-MOD-004`：`enforce`はApplicable Policy、Current Authority、Required Approval、Registered Action、CapabilityおよびBudgetの積集合だけを実行する。
- `P5-MOD-005`：Phase 5 Actionは`allow／warn／reject_input／stop_before_generation／suppress_stream_candidate／reject_output／redact_typed_secret／redact_typed_pii／require_approval`のうち、実装済み・登録済み・権限付きだけとする。
- `P5-MOD-006`：秘匿化はDetectorがTyped Spanを返し、原文外を書き換えず、未確定Span／Overlapping Spanで捛造Redactionしない場合だけ実行可能とする。
- `P5-MOD-007`：Repair／Regenerate／Semantic RewriteはPhase 6まで自動実行しない。

### 2.6 Safety Model Adapter

- `P5-SFM-001`：Safety Modelは交換可能Portとし、Deterministic Baselineの代替または最終Authorityにしない。
- `P5-SFM-002`：Model ID、Exact Revision、Artifact Digest、Label Schema、Calibration、Timeout、Latency、Token／Call数およびFailureを分離する。
- `P5-SFM-003`：実Model未選定／未Loadの間は`unavailable`とし、実Call成功を装うFake Production Adapterを作らない。
- `P5-SFM-004`：Qwen3Guard等のExact Artifact選定／Download／Loadは別Human Gateであり、Phase 5 Completion Dependencyではない。

### 2.7 Evidence／Privacy／Status

- `P5-EVD-001`：Point、Detector、Category、Policy、Authority／Approval State、Recommendation、Executed Action、Latency／Call／FailureをTyped Evidence化する。
- `P5-EVD-002`：Secret／PII実値、Raw Prompt／Output、完全Policy本文、Absolute PathまたはRaw ExceptionをStatus／Evidenceへ複製しない。
- `P5-EVD-003`：Safe Count、Category ID、Severity、Action State、Degraded／Unavailable ReasonとDigestだけをUI／APIへ投影する。
- `P5-EVD-004`：Over-refusal／Under-refusal／False Positive／False Negativeを別Metricとし、不明値を0で捛造しない。

### 2.8 Compatibility／Deployment Boundary

- `P5-COM-001`：既存v1／v2、Persistent／Ephemeral、RAG Citation、Stop、Retry／Regenerate、Branch／ResumeおよびPhase 3／4 Modeを壊さない。
- `P5-COM-002`：Guardrail Reject時にGhost Completion、未承認Content永続化、Citation誤帰属または二重Terminalを生成しない。
- `P5-COM-003`：Local Research ProfileでMode比較を可能にするが、Public／Basic／Lightning／AWSへPrivate Control／Policy／Evidenceを自動Bindingしない。
- `P5-COM-004`：保護ProfileはGuardrail固定`enforce`を表現できるが、Current Public／Basicの仕様または安全性を自動的に完成済みと扱わない。
- `P5-COM-005`：Phase 5-EX AWS Resource、課金、Secret、URL公開、Model LoadおよびLightning反映は本Phase実装の事前許可ではない。

## 3. Completion Condition

- Deterministic GuardのOFF／OBSERVE／ENFORCEをQwen Current Routeで再現できる。
- Input／Context／Output／Streaming境界でObserve非介入とEnforce Exact Actionが成立する。
- Policy／Authority／Approval不足がAllowを生成せず、Registered Action以外を実行しない。
- Secret／PII実値と未検査Stream ContentをEvidence／Clientへ漏らさない。
- Safety Model 0件Baseline、Definition 0件Baseline、Public／Basic Call-0およびPhase 4回帰が成立する。
- Open Major Finding 0、Codex Independent Review、User Mac AcceptanceおよびMinimal Closureを経る。

## 4. Non-scope

- LLM-as-a-Judge、意味的Hallucination判定、反復Repairおよび自動Regenerate（Phase 6）。
- Tool／Agent実行本体、External Side EffectおよびHuman Approval UIの完成。
- Safety ModelのDownload／Load／Promotion。
- AWS／Lightning配置、一般公開、課金またはSecret操作。
- Protected Full Capture、本格RAG Governance／Data GovernanceおよびAgent間通信実装。
