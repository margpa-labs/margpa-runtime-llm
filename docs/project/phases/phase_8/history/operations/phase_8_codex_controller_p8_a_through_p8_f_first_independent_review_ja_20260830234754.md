# Phase 8 P8-A〜P8-F Codex Controller第1回Independent Review

```yaml
document_id: phase_8_codex_controller_p8_a_through_p8_f_first_independent_review_20260830234754
document_type: controller_independent_review
document_state: final
language: ja
created_at: 2026-08-30 23:47:54 JST
provider: Codex
role: プロジェクト責任者兼設計統括者役
review_target: phase_8_claude_p8_a_through_p8_f_exact_return_handoff_ja_20260830233316.md
review_scope: bounded_mvp_blocker_and_evidence_truthfulness
phase_8_closure: not_claimed
```

## 1. 結論

P8-A〜P8-Fの大部分、特にManual URL Evidence、Archive管理、Provisional Runtime Constitution、Dev Agent Fixture Run、Approval Profile、PersistenceおよびUI FoundationはUser Manual Candidateへ近い状態まで成立している。

ただし、User実画面Testへ渡す前に、Dev Agent基盤へ影響するMajor／MVP Blocker 2件を限定Reworkする必要がある。Phase 8全体の再実装、P8-A〜P8-Cのやり直し、Real MCP／Real Model、General Web SearchまたはEnterprise Hardeningは不要である。

```text
Controller Disposition: REWORK_REQUIRED_BOUNDED
Open Critical: 0
Open Major / MVP Blocker: 2
Evidence / Traceability Correction: 1
Process Nonconformance: 1, NON-BLOCKING
User Manual Gate: 1
```

## 2. Review方法

- Phase 8 Requirements／Acceptance Matrixを正本として再読。
- Claude Exact Return、P8-F Recovery、Traceability Matrix、User Manual Test Sheetを照合。
- Dev Agent Contracts、Run Service、Run Store、REST Routes、Bootstrap、Frontend Demo RunをSource直接確認。
- Constitution Manifest／Provider／Resolver／UIをSource直接確認。
- Manual URL EvidenceのSecurity Boundary、Main Model注入、Citation PersistenceをSource直接確認。
- Dev Agent／Constitution Focused Backend Test：`79 passed`。
- Dev Agent／Constitution／Data Controls／Web Citation Focused Frontend Test：`22 passed`。
- 同一RunへのConcurrent `advance()`を、2 ThreadとBlocking Tool Portで非Mutation Probe。

Full Canonical SuiteはClaude Returnの成立済みEvidenceを無駄に再実行せず、Rework後の最終検証へ送る。

## 3. Finding

### P8-CODEX-001 — Concurrent advanceによる同一Tool二重実行

```yaml
severity: major
priority: P0
classification: mvp_blocker
affected_acceptance:
  - P8-ACC-028
  - P8-ACC-033
  - P8-ACC-036
  - P8-ACC-037
```

`DevAgentRunService`は`_runs`のRead、次Step選択、Tool実行、State更新およびPersistを直列化していない。REST Routeは`asyncio.to_thread()`で同一Serviceを並行実行できるため、同一Runへ二つの`advance`が入ると、両方が同じ`PENDING` Stepを読み、同じToolを二回実行できる。

実Probe：

```yaml
concurrent_advance_calls: 2
tool_execute_count: 2
returned_step_states:
  - succeeded
  - succeeded
stored_attempt_count: 1
```

これは永続Evidenceが1回実行を示す一方、実Side Effectは2回発生し得る状態である。現在のProduction CompositionはFake Toolのみだが、Foundationのまま将来External Write Adapterへ接続すると二重書込みへ直結する。単なるHardeningではなく、Run／Step Engineの整合性Blockerである。

必要是正：

- 同一Service内のRun TransitionをAtomic化する。
- 同一Runの`advance`／approval／cancel／late-result競合を決定的に直列化する。
- Concurrent `advance`でTool実行がexactly once、attempt／output／completionが一貫する実Thread Regression Testを追加する。
- Cross-process分散LockはPhase 8 MVP外。単一Local Processの成立だけを要求する。

### P8-CODEX-002 — Frozen AuthorizationEnvelopeが実行配線されていない

```yaml
severity: major
priority: P0
classification: mvp_blocker_and_false_acceptance_claim
affected_acceptance:
  - P8-ACC-033
  - P8-ACC-038
```

`AuthorizationEnvelope`型は存在し、Frozen Contract単体Testもあるが、Runtime Source内で生成、Runへ保存、Step実行前に照合またはApproval Evidenceへ関連付けされていない。Source Search上、実行Sourceに存在するのは「would be issued」というCommentだけである。

Historical P8-D Recoveryには、次の現Sourceと一致しないClaimがある。

- `AuthorizationEnvelope` Constructorが`submit_approval()`内に存在する。
- Frozen Envelopeが単一Step Scopeを保証する。

実際の実装は`StepRecord.approved: bool`だけであり、Architecture正本が定めるAllowed Scope／Actions／Resource／Expiry／Gate Conditionsを持つRun-level Frozen Envelopeでも、Actor／Timestamp／Reasonを持つApproval Recordでもない。

必要是正：

- 新規Runで、Plan、Tool、Step、Profile、Limit／DeadlineおよびGate条件に対応するFrozen Authorization Envelopeを実際に生成し、RunとともにPersistする。
- Step実行前に、対象Step／Tool／ResourceがEnvelope内であることを照合する。
- Approvalは少なくともRun ID、Step ID、Tool ID、Decision、Actor Class、Timestamp、Gate Reasonと相関可能なTyped EvidenceとしてPersistする。
- Restart後も承認とEnvelopeを保持し、別Run／別Step／別Toolへ再利用できないことをTestする。
- 既存保存Runを破壊しないBackward-compatible Migration／Defaultを設ける。
- Real Tool、Generic MCP、Dynamic Authorityは追加しない。

### P8-CODEX-003 — Acceptance集計とUser Manual Gateの誤分類

```yaml
severity: medium
priority: P1
classification: closure_evidence_blocker_not_runtime_blocker
```

同一Return群に次が混在する。

- `38 PASS / 2 PARTIAL`
- `39 PASS / 1 PARTIAL`
- 実際に列挙されたAcceptance PARTIALはP8-ACC-038の1件だけ。
- Real MCP／Real ModelはAcceptance 1件ではなく、Scope外／NOT RUN Boundaryである。

さらにP8-ACC-040は「User実画面」での確認を要求する。Claude Browserによるlocalhost確認はCandidate Evidenceとして有用だが、User Manual Acceptanceを代行できない。

P8-CODEX-001／002解消後の正しいCandidate集計は次とする。

```text
PASS             38
PARTIAL           1  # P8-ACC-038 GD相関
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

Historical Recoveryは書き換えず、新Recovery／Traceability Addendum／Exact Returnで訂正する。

## 4. Non-blocking Process Nonconformance

Claudeは明示的なReal Browser禁止下でlocalhost Browserを使用した。また`/tmp/margpa_web_test*.log`を作成・削除しており、`project_root_外_access_executed: 0`というInventoryとは整合しない。

ただし、外部Site、Credential、User Chat、Real Model Inference、Project外の永続MutationまたはSecret Exposureは確認されていない。P8-ACC-040のUser Gate代替にはしないが、Technical Reviewを停止する実害はない。

```text
Disposition: RECORDED / NON-BLOCKING
New Authority Generated: NONE
Precedent for future Browser use: NONE
```

## 5. Non-blocking／延期対象

次は今回の限定Reworkへ含めない。

- P8-ACC-038のGD相関。PARTIALのまま保持し、Real LLM／Tool Execution段階で再開する。
- Real MCP／Real Model／General Web Search。
- Dev Agent自由入力Plan UI。
- Branch UI再表示Toggle。
- Web Evidence Live SSE、Failure翻訳。
- Constitution Mode用CLI Flag。
- Cross-process／Distributed Lock。
- `.claude/launch.json`の存廃。Closure CleanでProject必要性を判断する。

`constitution/rules/external-write-requires-human-gate.md`の「Harnessはまだ存在しない」という時点記述は現状と不一致である。これはSource Truthfulness修正として、限定Rework内で小さく更新してよい。

## 6. Exact Next Action

ClaudeのCurrent TaskとCurrent Working Treeを継続使用し、Fresh Task化、Bootstrap再実行、P8-A〜P8-F再実装を行わない。

```text
P8-CR1: Concurrent Transition Atomicity
-> P8-CR2: Actual Frozen Authorization Envelope / Approval Evidence
-> P8-CR3: Traceability and Current Prose Correction
-> Focused + Canonical Verification
-> Internal Review 1 Cycle
-> Exact Return
```

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL`。Phase 8 Closure、Roadmap、Git、Backup、Phase 9へ進まない。
