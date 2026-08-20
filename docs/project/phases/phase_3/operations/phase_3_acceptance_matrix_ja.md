# Phase 3 Acceptance／Regression Matrix

```yaml
document_id: phase_3_acceptance_matrix
status: design_candidate
phase: phase_3
language: ja
created_at: 2026-08-21 02:05:30 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
```

## 1. Technical Acceptance

| ID | Acceptance | Required Evidence |
|---|---|---|
| `P3-ACC-001` | `off`が初期値 | Config／API／UI／Boot Test |
| `P3-ACC-002` | `off`でProvider／Adapter／Compiler／Hook Call 0 | Spy／Counter Test |
| `P3-ACC-003` | `off`でModel Generation、Conversation、RAG、CitationがRegressionなし | v1／v2 Integration |
| `P3-ACC-004` | `observe`でModel Input／Output／SSE／Commitを変更しない | Golden／Spy／Integration |
| `P3-ACC-005` | Phase 3の`enforce`要求はUnsupported、Mutation 0 | Service／API／UI Test |
| `P3-ACC-006` | Empty ProviderでDefinition 0件Baseline成立 | CLI／Web／Persistent Boot |
| `P3-ACC-007` | Reference Bundle 17 Source／18 DefinitionをManifest駆動で処理 | Corpus Contract Test |
| `P3-ACC-008` | File名／Directory／Top Keyによる意味推測0 | Negative Test／Code Review |
| `P3-ACC-009` | Unknown Adapter／SchemaをUnsupportedとして非実行 | Matrix Test |
| `P3-ACC-010` | Invalid Sourceを隔離し、Valid SiblingとMain Runtimeを保持 | Fault Injection |
| `P3-ACC-011` | Combined ARGD／DAGD、CDOGD、Extension三Adapterが決定論的IRを生成 | Adapter Contract |
| `P3-ACC-012` | 全Compiled PlanがUnbound／Non-executable | Compiler Test |
| `P3-ACC-013` | Plan Digest／CacheがStale Entryを拒否 | Cache Matrix |
| `P3-ACC-014` | Evidence Event Canonicalization／SHA-512決定論 | Unit Test |
| `P3-ACC-015` | JSONL Append、Concurrent Write、Receipt、Restart Recovery成立 | Store Contract／Integration |
| `P3-ACC-016` | Partial Tail／Digest Mismatch／Unknown Schemaを自動修復せず検出 | Fault Injection |
| `P3-ACC-017` | Raw CoT、Secret、System Prompt、Hidden Original、Full Content保存0 | Payload Spy／Fixture Scan |
| `P3-ACC-018` | Evidence Writer FailureがObserve Generationを壊さない | Failure Injection |
| `P3-ACC-019` | Public／BasicでGovernance Service／Route／Definition／Evidence Call 0 | Access Profile Spy |
| `P3-ACC-020` | UIがOFF／OBSERVE／Unavailable ENFORCEを正確に表示 | React／Browser Test |
| `P3-ACC-021` | APIが絶対Path、Definition本文、Raw Exceptionを露出しない | Response Contract |
| `P3-ACC-022` | Existing Testを削除・弱体化せずFull Regression合格 | Test Diff／Full Result |

## 2. Security Acceptance

| ID | Scenario | Expected |
|---|---|---|
| `P3-SEC-001` | Absolute／`..` Manifest Path | Reject／Root外Read 0 |
| `P3-SEC-002` | Symlink Source | Reject |
| `P3-SEC-003` | Oversized Source／Deep JSON／Large Collection | Typed Reject／Runtime存続 |
| `P3-SEC-004` | Manifest Adapter IDにModule Path | Unsupported／Import 0 |
| `P3-SEC-005` | Definition内Shell／URL／Template表現 | Data扱い／実行0 |
| `P3-SEC-006` | Digest／Size Mismatch | Invalid／Quarantine |
| `P3-SEC-007` | Evidence PayloadへSecret-like Fixture | Allowlistで拒否またはRedact |
| `P3-SEC-008` | Public／Basicからv3 Governance Route | Not bound／safe unavailable |
| `P3-SEC-009` | Enforce API直接要求 | Unsupported／Mode不変 |
| `P3-SEC-010` | User実`runtime_data/` | Test／Scan／Migration 0 |

## 3. Mode Matrix

| Provider | Definition | Mode | Expected Repository | Model | Governance Call | Evidence | Intervention |
|---|---|---|---|---|---:|---|---:|
| none／empty | 0 | off | not loaded／empty descriptor only | pass | 0 | governance-specific 0 | 0 |
| filesystem configured | 18 | off | source unread | pass | 0 | governance-specific 0 | 0 |
| empty | 0 | observe | `inactive_no_definitions` | pass | deterministic only | warning metadata | 0 |
| filesystem | valid 18 | observe | validated／compiled_unbound | pass unchanged | deterministic only | metadata | 0 |
| filesystem | partial invalid | observe | valid + isolated invalid | pass unchanged | deterministic only | degraded metadata | 0 |
| any | any | enforce | request rejected | unchanged | 0 new execution | safe error metadata when applicable | 0 |

## 4. Definition Corpus Acceptance

- Source Path、Byte Length、SHA-512、Schema ID、Adapter ID、Definition ID、VersionおよびObject PointerがManifestと一致する。
- 17 Sourceから18 Logical Definitionが一意に得られる。
- ARGDとDAGDを一Sourceに含む構造を保持する。
- CDOGDを必須Boot Dependencyまたは自動Routerにしない。
- 15 Extensionの共通構造と個別Non-target／Role／Activationを保持する。
- SPPGD→DAAGD→SDAGDとConditional SDMRGDを保持し、相互再帰実行しない。
- `transparent_reasoning`をRaw Chain of Thought保存へ変換しない。
- Source修正があればVersion／Correction／Digest／Manifestの一貫性を確認する。

## 5. Evidence Acceptance

- Event Digest再計算一致。
- ReceiptがEvent ID／Digest／Segment／Positionと一致。
- Event順序は記録するが、Timestampだけを因果関係の唯一根拠にしない。
- System TraceとModel ExplanationがField／Provenanceで分離。
- Missing Metricは0でなくUnavailableとして表現。
- SHA-512をTamper-proofと表記しない。
- Conversation DBとEvidence Storeが物理／論理的に分離。

## 6. Automation／Cross-provider Acceptance

| Axis | Metric | Target／Interpretation |
|---|---|---|
| Technical | Work Unit pass | 全33中、Claude対象30 UnitがAcceptedまたは明示Rework後Accepted |
| Technical | False completion | 0 |
| Technical | Self-repair | 発生数と成功数を両方記録。多いこと自体を成功にしない |
| Governance | Root／Scope逸脱 | 0 |
| Governance | Provider Memory／Git／User Data／Stable違反 | 0 |
| Governance | Completion Line超過 | 0 |
| Recovery | Auto／Manual Compaction | 回数、成功、失敗、未認識を分離 |
| Recovery | Hash Fidelity | Before／After一致またはMismatch説明 |
| Recovery | Semantic Fidelity | Role／Authority／WU／Finding／Next Routeの一致 |
| Human Burden | Clarification | 総数と不要数を分離。不要0を目標 |
| Human Burden | Intervention Time | 観測可能な範囲で記録 |
| Human Burden | User-intent Mismatch | 件数と修正時間。0を目標 |
| Human Burden | Human-only Gate | 正しいGateはAutomation Failureに数えない |

## 7. Required Test Layers

### 7.1 Focused

- `tests/unit/audit_evidence/`
- `tests/unit/governance_definitions/`
- `tests/integration/audit_evidence/`
- `tests/integration/governance_definitions/`
- 対応Configuration／Web／Frontend Test。

### 7.2 Regression

- Conversation Domain／Persistence／Streaming。
- Documentation RAG／Citation Persistence。
- Configuration Control／Runtime Composition。
- v1／v2 Web API。
- Model Adapter／CLI。

### 7.3 Static／Full

- Ruff Format／Check。
- Mypy Strict。
- Frontend Test／Typecheck／Build／Lint。
- Python Full Suite。
- Link／JSON Parse／Manifest Digest／Non-ASCII corruption check。

## 8. Manual Acceptance Reservation

Phase 3-Hでユーザーが確認する候補：

1. Default OFFで通常Chat／Persistent Chat／RAG Citationが従来どおり動く。
2. SettingsにOFF／OBSERVE／ENFORCEが表示される。
3. ENFORCEが理由付きで無効。
4. OBSERVEへ切替後も回答本文が変わらず、Definition／Plan／Evidence Statusが更新される。
5. Server Restart後にEvidenceを安全に再読できる。
6. OFFへ戻すと新規Governance Evidenceが増えず、通常Chatは動く。
7. Unknown／Invalid FixtureでRuntime全体が停止しない。
8. Public／Basic ProfileにGovernance ControlやPrivate Evidenceが露出しない。
9. Phase 2から延期されたLightning横断Acceptanceを独立実施し、または影響と再開Triggerを伴う正式再延期として閉じる。

User実Data、Migrationまたは破壊操作を伴う場合は、このChecklistから分離して個別手順を作る。

## 9. Closure Decision

Claudeは本MatrixのTechnical／Automation Scopeを自己評価し、Phase 3-Gで`GO／ADJUST／STOP`を出す。CodexはPhase 3-Hで独立再検証する。ユーザーだけがFinal Acceptanceを行う。
