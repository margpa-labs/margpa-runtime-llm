# Phase 3 Execution Plan／Work Unit Breakdown

```yaml
document_id: phase_3_execution_plan
status: design_candidate_not_started
phase: phase_3
language: ja
created_at: 2026-08-21 02:05:30 JST
owner_role: プロジェクト責任者兼設計統括者役
execution_provider_candidate: claude_code
implementation_authorized: false
work_unit_count_total: 33
claude_work_unit_count: 30
codex_user_closure_work_unit_count: 3
claude_completion_line: phase_3_g_wu_004_complete_candidate
```

## 1. Execution Policy

- Work UnitはAuto-Compaction後に一意に再開できるMaterial Boundaryとする。
- 一Unitに設計、実装、Focused Test、Self-reviewおよびRecovery State更新を含める。
- 同一Unit内の微修正ごとに別Handoff／Status／Evidenceを作らない。
- Unit開始時に、候補Path ClassからExact Mutation ManifestをFreezeする。
- Unit外Pathが必要なら、Claude側設計統括者役がPhase 3範囲内かを判断し、History Correctionを作る。Root／Stable／Git／External等へ触れる場合だけ停止する。
- Focused TestをUnitごと、Subphase RegressionをSubphaseごと、Full TestをPhase 3-Gで行う。
- 完了済みUnitを、新Evidence、Integrity MismatchまたはDependency Changeなしに再Openしない。

## 2. Phase 3-0 — Entry／Baseline／Recovery Bootstrap

### P3-0-WU-001：Authority／Source Preflight

**目的**：開始時点のAuthority、Root、Completion Line、Dirty Tree、Provider Memory禁止、Phase 2-F ClosureおよびDesign Successorを確認する。

**Action**：Read-only。

**Acceptance**：

- User Start、Backup通知、Codex READY／ARMED、Phase 2-F Closureを確認。
- Authorized Rootと禁止対象を絶対Pathで再確認。
- Phase 3 Design Packageの全Linkが解決。
- Git Mutation 0、Root外Action 0。

### P3-0-WU-002：Implementation Baseline

**目的**：開始時点のSource、Test、Definition Corpus、Frontend、Runtime Data非接触境界を固定する。

**Action**：Read-only Test／Inventory。

**Acceptance**：

- Focused／Full Testの開始Baselineを記録。
- Definition 17 Source／18 Logical Definitionを再Hash。
- User実`runtime_data/`を読まず、存在確認も不要とする。
- Current Mutation Inventoryと既存Dirty Stateを、Phase 3 Mutationと分離。

### P3-0-WU-003：Exact Execution Freeze

**目的**：Phase 3-A～GのPath Class、Test Command、Recovery Index、Long-running Flagおよび停止条件を、開始時点の現行Sourceへ合わせる。

**Output**：Phase 3 History配下のExecution Freeze／Current Operational State／Recovery Index。

**Acceptance**：

- Stable Designを直接変更しない。
- Long-running ModeはUserが明示有効化した場合だけActive。
- 次Unit P3-A-WU-001を一意に特定可能。

## 3. Phase 3-A — Audit Identity／Canonical Evidence Contracts

### P3-A-WU-001：Audit Identity／Event Contract

**実装**：AuditRun、AuditEvent、Correlation Reference、Event Kind、Safe PayloadのTyped Contract。

**Acceptance**：ID型混同拒否、Invalid Timestamp／Enum／Payload拒否、Raw Arbitrary Object拒否。

### P3-A-WU-002：Canonicalization／Digest

**実装**：Versioned Canonical JSON、SHA-512、Digest Field除外、NaN／Infinity拒否。

**Acceptance**：Key順に非依存な同一Digest、Payload差分でDigest差分、Unicode決定論、Self-digestなし。

### P3-A-WU-003：Evidence Port／In-memory Reference

**実装**：Append、Read／Verify、Status、ReceiptのPortとIn-memory Contract Adapter。

**Acceptance**：Append-only、Duplicate Event拒否、Receipt整合、Typed Failure、Phase 3-A Focused／Static Test合格。

## 4. Phase 3-B — Local Append-only Evidence Store

### P3-B-WU-001：Store Root／Scope／Path Safety

**実装**：明示Root、Server-owned Scope、Directory Mode、Symlink／Traversal／Non-regular拒否。

**Acceptance**：Root外Write 0、User入力Path 0、tmp FixtureだけでTest、既存`runtime_data/`非接触。

### P3-B-WU-002：JSONL Append／Receipt／Recovery

**実装**：Segment Metadata、Exclusive Append、Flush、Receipt、Valid Prefix Read、Partial Tail／Digest Mismatch検出。

**Acceptance**：Fault Injection、Concurrent Append、Partial Tail非受理、既存Byte非変更、自動切詰め0。

### P3-B-WU-003：Evidence Store Contract／Regression

**実装**：In-memoryとJSONLへ共通Contract Test、Safe Error Projection、Status。

**Acceptance**：Adapter同値、Absolute Path／Raw Exception非露出、Subphase Test合格、Open Major 0。

## 5. Phase 3-C — Definition Package／Provider／Repository State

### P3-C-WU-001：Reference Bundle Manifest／README

**実装**：`definitions/`配下にVersioned Manifestと説明を追加し、17 Source／18 Definitionを明示Mappingする。

**Acceptance**：Path／Size／SHA-512／Schema／Adapter／Object Pointer一致、Coreへの既知名Hard-code 0、`.DS_Store`非参照・非削除。

### P3-C-WU-002：Package／Descriptor／Provider ContractとEmpty Provider

**実装**：Generic Contract、State、Typed Failure、Empty Provider。

**Acceptance**：Definition 0件を正常結果として返し、Unavailable／Failedと区別、Generation Boot Pass。

### P3-C-WU-003：Filesystem Provider／Manifest Loader

**実装**：明示Root／Manifest、Byte Size、Digest、Media Type、Safe Relative Path検証。

**Acceptance**：Directory Scan 0、Filename Inference 0、Symlink Escape 0、Remote／Dynamic Import 0。

### P3-C-WU-004：Repository State／Quarantine

**実装**：Package／Source／DefinitionごとのStateとPartial Acceptance Policy。

**Acceptance**：Unknown Schema=`unsupported`、Digest Mismatch=`invalid／quarantined`、Valid Sibling保持、EmptyへのSilent変換0。

## 6. Phase 3-D — Trusted Adapter Registry／Normalized IR

### P3-D-WU-001：Trusted Adapter Registry

**実装**：明示登録、Schema／Media Type／Adapter Version照合、Duplicate／Conflict拒否。

**Acceptance**：Manifest StringからImport 0、Unknown Adapter safe unsupported、登録とAuthority分離。

### P3-D-WU-002：Combined ARGD／DAGD Adapter

**実装**：一Sourceから二DefinitionをObject Pointerで分離し、IR／Loss Reportへ変換。

**Acceptance**：Version／Identity／Source Digest保持、State／Action不整合をWarningまたはError化、Source Rewrite 0。

### P3-D-WU-003：CDOGD／Domain Extension Adapter

**実装**：CDOGDとCommon Extension Adapter。Decision Pipeline／Conditional WatchdogをIR Referenceへ保持。

**Acceptance**：15 Extensionの共通Contract合格、SPPGD→DAAGD→SDAGDとConditional SDMRGD保持、Routing／Activation実行0。

### P3-D-WU-004：Full Corpus IR Conformance

**実装**：17 Source／18 DefinitionをManifest駆動でNormalizeするContract Test。

**Acceptance**：期待集合一致、Definition名をCore Testへ閉じ込めずBundle Contractへ限定、Raw CoT要求生成0、IR Digest決定論。

## 7. Phase 3-E — Compiler／Unbound Plan

### P3-E-WU-001：Compiler Contract／Unbound Plan

**実装**：Deterministic Compiler、Plan Contract、Rule／Evaluator／Action Reference、Dependency／Conflict Report。

**Acceptance**：全Plan`binding_state=unbound`、`executable=false`、Action Call 0、Model Call 0。

### P3-E-WU-002：Plan Digest／Cache

**実装**：Compiler／IR／Profile／Binding Candidate／Capability／Authority Snapshotを含むDigestとProcess-local Cache。

**Acceptance**：Stale Plan再利用0、Cache Hit／Miss決定論、Digest Mismatch拒否。

### P3-E-WU-003：Empty／Unknown／Invalid Matrix

**実装**：0件、Unknown Adapter、Unknown Schema、Malformed、Invalid sibling、Reference BundleのCompile Matrix。

**Acceptance**：0件正常、Unknown非実行、Invalid隔離、Main Runtime非停止、Phase 3-C～E Regression合格。

## 8. Phase 3-F — Mode／Configuration／Status／UI／Observation

### P3-F-WU-001：Governance Mode Contract

**実装**：`off／observe／enforce`、Availability、Apply Disposition、Mode Snapshot、Revision／Digest。

**Acceptance**：Default off、Observe available、Enforce unavailable、Unsupported Mutation 0、Silent Downgrade 0。

### P3-F-WU-002：Configuration／Bootstrap／CLI Binding

**実装**：既存Configuration Control、Local Bootstrap、Explicit Profile／CLI SeamへModeとProviderを接続。

**Acceptance**：Local／Loopback／Auth-disabledのみ、Tracked ConfigへのUI Write 0、Public／Basic Service Build 0、off時Provider Call 0。

### P3-F-WU-003：Governance Status API

**実装**：Runtime、Definition Catalog、Plan、Evidence StatusのRead-only API。

**Acceptance**：Safe Allowlist、Absolute Path／Body／Secret／Raw Exception 0、Public／Basic Route Call 0。

### P3-F-WU-004：React Settings UI

**実装**：Advanced SettingsのThree-state Mode、Status Summary、Preview／Apply、i18n、Test、Built Static同期。

**Acceptance**：OFF初期、OBSERVE選択、ENFORCE disabled reason、Keyboard／ARIA、Apply Failure時State保持、Frontend Test／Build／Lint合格。

### P3-F-WU-005：Non-intervening Runtime Observation Hook

**実装**：既存Generation LifecycleへOptional Observerを接続し、Start／Terminal MetadataをEvidence化。

**Acceptance**：v1／v2 SSE Shape／Order不変、Model I/O不変、Terminal高々1、Writer Failure非介入、off時Hook Call 0。

### P3-F-WU-006：Mode／Access／Compatibility Matrix

**実装**：off、observe、enforce rejected、empty、reference、invalid、Public、Basic、Persistent、Ephemeralを横断Test。

**Acceptance**：off Regression 0、Observe Model Output Mutation 0、Public／Basic Definition／Evidence Call 0、Subphase Full合格。

## 9. Phase 3-G — Integrated Verification／Completion Candidate

### P3-G-WU-001：Integrated Technical Validation

**実行**：Focused Test全群、Conversation／Web Regression、Frontend Test／Build／Lint、Ruff Format／Check、Mypy、Full Test。

**Acceptance**：Open Technical Major 0、既存Test削除／弱体化0、Expected Skip明記、User実Data非接触。

### P3-G-WU-002：Automated Local UX／Recovery Verification

**実行**：tmp Runtime RootでServer起動、OFF Boot、OBSERVE Apply、Catalog／Plan／Evidence、OFF復帰、Restart Recoveryを自動検証。

**Acceptance**：実User Conversation DB非使用、Enforce不可視でなくUnavailable表示、Evidence再読、Server clean shutdown。

### P3-G-WU-003：Automation／Compaction Final Evidence

**実行**：Technical、Governance、Recovery、Human Burdenの四軸を集計し、Auto-Compaction CycleとSelf-repairを記録。

**Acceptance**：Scope逸脱0をEvidenceで確認、False Completion／Intervention／Mismatchを隠さない、Total Scoreへ集約0。

### P3-G-WU-004：Claude COMPLETE_CANDIDATE Handoff

**実行**：Exact Mutation、Validation、Finding、Deferred、Manual Checklist、Rollback、Codex Review入口を一つのCompletion Handoffへまとめる。

**Acceptance**：RecommendationをClaudeが`GO／ADJUST／STOP`で提示し、Phase 3-Hへ進まず停止する。

## 10. Phase 3-H — Codex／User Final Closure（Claude実行禁止）

### P3-H-WU-001：Codex Independent Review

設計適合、Source、Test、Security、Mode、Definition Corpus、Evidence Store、Automation Evidenceを独立Reviewする。FindingはExact Rework Handoffへ変換する。

### P3-H-WU-002：User Mac Manual Acceptance

ユーザーが実環境でOFF／OBSERVE／OFF、UI、Conversation、RAG、RestartおよびEvidence表示を確認する。実Data Migrationや破壊操作が必要なら別Gateとする。

Phase 2で延期されたLightning横断Acceptanceも独立Checklistとして解決する。これはPhase 3機能のLightning Deploymentを自動許可せず、実施困難な場合は影響、理由および次のTriggerを伴う正式再延期として扱う。

### P3-H-WU-003：Final Docs／Backup／Git／Closure

Codexが必要なCurrent／Phase Index／Roadmap／Recoveryを更新し、ユーザーへBackup取得を依頼する。Git操作はその時点の明示許可後だけ行う。Local／origin／GitHub一致確認後、ユーザーAcceptanceによりPhase 3完了とPhase 4 Start Gateを判定する。

## 11. Test Strategy

### 11.1 Unit

- Identity、Canonicalization、Digest、State、Manifest、Path、Adapter、IR、Compiler、Mode。

### 11.2 Contract

- In-memory／JSONL Evidence Store。
- Empty／Filesystem Provider。
- Reference Bundle Adapter三種。

### 11.3 Integration

- Definition Pipeline。
- Evidence Restart／Partial Tail。
- Configuration／Web／React。
- v1／v2 Observation。

### 11.4 Regression／Static

```text
PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/pytest -q
./.venv/bin/ruff format --check src tests
./.venv/bin/ruff check src tests
./.venv/bin/mypy
npm --prefix frontend test
npm --prefix frontend run build
npm --prefix frontend run lint
```

開始時点のProject構成によりCommandが異なる場合、同じ検証意味を維持したProvider MappingをP3-0-WU-003で記録する。

## 12. Pause／Resume

利用可能量、Context、Provider Errorまたは時間切れで停止する場合：

1. 実行中Commandを安全に終了または状態確認。
2. Partial Mutationを隠さない。
3. Current WUを`paused`とし、Acceptedにしない。
4. Exact Changed Paths、Last Passing Test、Open Finding、Next CommandではなくNext Semantic Actionを記録。
5. Recovery Indexと必要なHashを作成。
6. Git、Cleanup、Scope拡張またはPhase Closureを行わず停止。
