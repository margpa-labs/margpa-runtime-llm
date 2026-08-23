# Phase 5 Execution Plan

```yaml
document_id: phase_5_execution_plan
status: accepted_frozen_ready_for_backup
phase: phase_5
language: ja
recorded_at: 2026-08-22 09:57:48 JST
implementation_authorized: false
claude_completion_line: phase_5_g_complete_candidate
work_unit_count: 32
```

## 1. Execution Principle

Phase 5-0～5-GをClaudeが一つのLong-running Executionとして連結する。Work UnitはCompaction／Quota Recoveryの安全な現在地であり、毎WUの報告で停止する理由ではない。

## 2. Subphase

```text
Phase 5-0 : Entry／Phase 4 As-built Reconciliation／Threat Model／Execution Freeze
Phase 5-A : Guardrail Identity／Result／Taxonomy／Port
Phase 5-B : Deterministic Input／Context Guard
Phase 5-C : Output／Streaming Guard／Terminal Atomicity
Phase 5-D : Policy／Authority／Approval／Conflict Resolution
Phase 5-E : Optional Safety Model Seam／Calibration Contract
Phase 5-F : Runtime／Evidence／Configuration／Web／UI Integration
Phase 5-G : Integrated Adversarial Verification／COMPLETE_CANDIDATE
Phase 5-H : Codex Independent Review／User Acceptance／Minimal Closure
```

## 3. Work Units

### Phase 5-0 — Entry／Freeze

#### P5-0-WU-001：Entry Preflight

Phase 4 Closure、Frozen Package、User Backup、Authorized Root、Current Qwen Route、Working Tree、Git Non-mutation、User `runtime_data/`禁止およびClaude Recovery正本をRead-only確認する。

#### P5-0-WU-002：Phase 4 As-built Compatibility Matrix

Runtime Governance Result／Point／Binder／Action／Evidence／Configuration／Web／UI、v1／v2／Persistent／RAG／Public／Basicの実Source／Testを照合する。Existingの内部変更でなくAdditive Composition境界を固定する。

#### P5-0-WU-003：Threat Model／Trust Boundary

Direct／Indirect Injection、Secret／PII、Encoded／Multilingual／Fragmented Input、Streaming Leak、Authority Spoofing、Stale Policy、Approval Forgery、Evidence Leak、Over／Under-refusalをThreat／Asset／Actor／Boundary／Failureで整理する。

#### P5-0-WU-004：Exact Execution Freeze／Baseline

Allowed／Forbidden Path Class、Baseline Test、Material Recovery境界、Completion LineおよびCurrent Dirty TreeをAppend-only Receiptへ固定する。

### Phase 5-A — Contracts

#### P5-A-WU-001：Identity／Taxonomy／Limits

Invocation／Detection／Policy／Authority／Approval／Action／ResultのTyped Identity、Registry-based Category、Bounded Collection／String／Spanを実装する。

#### P5-A-WU-002：Guardrail Result／Canonicalization

Detection Fact、Decision、Recommendation、Executed Action、Unavailable／Degraded、Metricを分離したImmutable ResultとCanonical SHA-512を実装する。

#### P5-A-WU-003：Provider／Registry／Port

Detector、Policy、Authority、Approval、Safety Model、Action、EvidenceのPortを実装する。ドメインへWeb／Model／File I/Oを漏らさない。

#### P5-A-WU-004：Contract Adversarial Test

Unknown Enum／Category、NaN／Infinity、Unbounded Span／Collection、Cross-ID、Digest不整合、Overlap／Out-of-range SpanおよびRaw Content混入をFail-closed Testする。

### Phase 5-B — Input／Context Guard

#### P5-B-WU-001：Canonical Normalization Pipeline

Unicode／Invisible／Whitespace／Encoding Candidate／Sizeを有界に処理し、原文とNormalized ViewのIdentityを混ぜない。

#### P5-B-WU-002：Deterministic Input Detectors

Injection／Jailbreak Marker、Secret／PII Candidate、Authority／Tool Spoofing、Disallowed Structureの分離Detectorを実装する。HitをFinal Intentとしない。

#### P5-B-WU-003：Context Source Authority Guard

User Input、System-owned Instruction、RAG Document、Citation、Tool-like TextのSource Classを保持し、RAG内InstructionがAuthorityを獲得しない経路を実装する。

#### P5-B-WU-004：Input Mode／Attack Matrix

OFF Call 0、OBSERVE Mutation 0、ENFORCE Exact Reject／Warning、Multilingual／Encoded／Fragmented／Long Input、False Positive Fixtureを検証する。

### Phase 5-C — Output／Streaming

#### P5-C-WU-001：Deterministic Output Detector

Secret／PII Candidate、Policy-forbidden Structure、Authority SpoofingおよびOutput LimitをCanonical Candidateで検査する。

#### P5-C-WU-002：Incremental Stream Guard

Bounded Suffix／Chunk State、Cross-chunk Match、Safe Prefix Release、Cancel／Disconnect／Scanner FailureのContractを実装する。

#### P5-C-WU-003：Typed Redaction／Reject Action

Verified SpanだけのRedaction、Overlap／Ambiguous時Reject、原文外書替え0、Secret／PII実値Evidence 0を実装する。

#### P5-C-WU-004：Terminal／Persistence Atomicity

Phase 4 post→Phase 5 output guard→Commit→completedの順序、Reject／Cancel／Failure／Unknown Commit、Retry／Regenerate／Branch／CitationをFault Injectionで検証する。

### Phase 5-D — Policy／Authority／Approval

#### P5-D-WU-001：Policy Provider／Snapshot

Scope／Revision／Digest／Applicability／Required Authority／Approval／Action Mappingを持つRead-only Policy Providerを実装する。

#### P5-D-WU-002：Authority Provider／Approval Port

Current AuthorityとExternal Human Approval Stateを分離する。Currentに実Approval Providerがない場合はUnavailable／Pendingを正確に返す。

#### P5-D-WU-003：Guardrail Decision／Action Resolver

Detection→Policy→Conflict→Authority→Approval→Capability→Budget→Registryの順で実行／Not-executedを決定する。

#### P5-D-WU-004：Main Governance Conflict Matrix

Phase 4 Pass／Reject／Stop、Guardrail Allow／Warn／Redact／Reject、Approval Pending／Deniedの全重要組合せを単一Terminalへ収束する。

### Phase 5-E — Safety Model Seam

#### P5-E-WU-001：Safety Model Typed Port

Artifact／Revision／Label Schema／Calibration／Confidence／Timeout／Cost／FailureのContractを実装する。

#### P5-E-WU-002：Unavailable／Fake Test Adapter

Production DefaultはUnavailable。TestのみDeterministic Fake Adapterを用い、Unknown Label／Timeout／Malformed／ConflictをSafe Allowにしない。

#### P5-E-WU-003：Calibration／Model-free Completion Matrix

Safety Model 0件、Unavailable、Low Confidence、ConflictおよびAdditional Call 0を検証する。実Artifact Loadは行わない。

### Phase 5-F — Integration／Surface

#### P5-F-WU-001：Bootstrap／Generation Composition

Guardrail PointをExisting Ephemeral／Persistent／RAG／Summary／Retry／Regenerateの正しいTerminal順序へ合成する。

#### P5-F-WU-002：Mode／Configuration Control

Guardrail Mode／Profile／AvailabilityをLocal Configuration Preview→Apply CASへ独立Fieldとして追加する。Default OFF、Phase 3／4 Mode非連動、Unavailable Silent Downgrade 0。

#### P5-F-WU-003：Evidence／Status API

Safe Count／Category／Severity／Policy／Authority／Approval／Action／Degradedを投影し、Raw Content／Secret／PII／Path／Exceptionを投影0とする。

#### P5-F-WU-004：Settings UI／Observability

OFF／OBSERVE／ENFORCE、Current Mode再Open同期、Point／Detection／Action Count、Safety Model Unavailable／Phase 6 Semantic Boundaryを日本語／英語で表示する。

#### P5-F-WU-005：Public／Basic／Compatibility Call-0

Existing Public／BasicへPrivate Control／Policy／Evidenceが出ないこと、Explicit Protected Profileなしで自動Bindingしないこと、v1／v2／Phase 4回帰をSpyで固定する。

### Phase 5-G — Verification／Complete Candidate

#### P5-G-WU-001：Golden Mode／Adversarial Matrix

Definition 0件／Guard Model 0件／Valid／Invalid／Stale、OFF／OBSERVE／ENFORCE、Input／Context／Stream／Output、False Positive／Negativeを統合検証する。

#### P5-G-WU-002：Security／Privacy／Concurrency／Recovery

Path／Digest／Size／Symlink／Race／Cache／Multi-tab／Cancel／Restart／Evidence Failure／Secret／PII非露出をAdversarialに検証する。

#### P5-G-WU-003：Full Regression／Performance

Backend Full、Frontend Test／Typecheck／Lint／Build、Ruff／Mypy、OFF Call 0、Observe非介入、Enforce Latency／Memory／Evidence Sizeを実測する。

#### P5-G-WU-004：Self-review／COMPLETE_CANDIDATE

Design Conformance、Security Review、Exact Mutation、Open Major Finding、Compaction／Quota Recovery、Human Burdenを日本語Handoffに統合して停止する。

## 4. Validation Ladder

```text
Per WU       : focused tests
Per Subphase : focused + adjacent regression + static
Phase 5-G    : backend full + frontend full/typecheck/lint/build
               + adversarial/security/privacy/diff review
Phase 5-H    : Codex independent major review + User Mac acceptance
```

Full Suiteは大きな境界ごとに実行し、小修正ごとに数千FileのContext／Evidenceを量産しない。

## 5. Stop Conditions

- Root／Authority／Stable／User Data／Git／ExternalのScope拡張が必要。
- Phase 6 Judge／RepairなしにはPhase 5要件を満たせない重大衝突。
- Existing API／Persistenceの不可逆Migrationが必要。
- Enforce Streamが未検査Contentを漏らす以外に成立しない。
- 実Safety Model／Network／Model Load／AWSが必須になる。
- 重大Risk受容がUser判断を必要とする。

これ以外のFrozen Scope内の局所Bug／Test Failure／設計具体化はClaudeが自己解決する。
