# Phase 8 Claude Post-Controller First Review Bounded Rework — Exact Handoff

```yaml
document_id: phase_8_claude_post_controller_first_review_bounded_rework_exact_handoff_20260830234754
document_type: exact_differential_execution_handoff
document_state: frozen
language: ja
created_at: 2026-08-30 23:47:54 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-CR0_through_P8-CR4
implementation_authority: true
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL
phase_8_closure_authority: false
phase_9_authority: false
git_authority: false
network_authority: false
real_browser_authority: false
real_model_authority: false
real_mcp_authority: false
backup_authority: false
```

## 1. 継続前提

これはFresh Task Bootstrapではない。現在のClaude Task、Current Working Tree、P8-A〜P8-Fの成立済みSource／Test／Recoveryをそのまま継続する。

次を行わない。

- Role文書やP8-A〜F Mandatory Readingの全再読。
- P8-A〜P8-Fの再実装、Rollbackまたは成立済みTestの理由なき再実行。
- 新Task化、旧Context／Authority初期化。
- Phase 8全体の設計やり直し。

## 2. 必読差分

次の4文書だけを指定順で全文読む。

1. Controller Independent Review

```text
/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_8/history/operations/phase_8_codex_controller_p8_a_through_p8_f_first_independent_review_ja_20260830234754.md
SHA-512: 0f6922f2ee8df95db265f59aa3430fd070ca08599e3fe1afd1f5918f45178acecdf27e1c7d8e4647dc93644d0f52d3998d4f51e36e1bb8f63929b376ef6cdbf5
```

2. Phase 8 Requirements

```text
/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md
SHA-512: e658a5f5fda55590e3875987f1622be3e91c415a8c881dc4f1c5266f53aee7017973669dd3b3a6e0305766238566b297d76c56adf444301e78334aadbea0a1ca
```

3. Phase 8 Architecture

```text
/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md
SHA-512: 1fdfdb8b7eb3bee3d884dc5d5867be6313a5fd01755d9534c7a0e19e9e70b71ffee7a6478ed34ce8f70d8cae4f3adfdae55361a5135c2dfc9cfce65828879a8c
```

4. Phase 8 Acceptance Matrix

```text
/Users/yukitakagi/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/MARGPA-RUNTIME-LLM/margpa-runtime-llm/docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md
SHA-512: 40ebe8449d880fd00f98b3633825756a4e23d1edea8efbdac437be0ad718e6b6a0c04776f1907089cde23b057087ba3c3275ba68727d116bec2baee682bd1a34
```

Digest不一致だけでは直ちに全体停止せず、対象Path、Expected、Observedを記録し、実質的Contract Conflictかを判定する。

## 3. Preserved COMPLETE

次を再実装しない。

- P8-A Manual URL Evidence／Security／Citation／Persistence。
- P8-B Branch UI既定非表示／Archive Lazy一覧・開く・解除。
- P8-C Provisional Runtime ConstitutionのManifest／Provider／Resolver／UI Foundation。
- P8-D Run／Step／Tool Port／Registry／Fake Adapter／MCP Fixtureのうち、Finding対象外。
- P8-E JSON Run Store／Restart Recovery／Constitution相関のうち、Finding対象外。
- P8-F Approval Profile 4種、Important Gate Reason 8種、Demo Run UI。
- P8-ACC-038のGD相関PARTIALという正直な分類。

## 4. P8-CR0 — Entry／Finding Freeze

Controller Findingを次で固定する。

```text
P8-CODEX-001 Concurrent advance duplicate Tool execution
P8-CODEX-002 AuthorizationEnvelope unwired / false PASS claim
P8-CODEX-003 Acceptance count and User Manual Gate correction
```

Source、Test、Current Docsを読んでExact Changed Pathを決め、Recovery Indexを作成する。ここで途中Returnしない。

## 5. P8-CR1 — Concurrent Transition Atomicity

### Required

- 単一Local Process内で、同一RunのState TransitionをAtomic化する。
- `advance`、`submit_approval`、`cancel_run`、`record_late_result`の競合を決定的に扱う。
- 同一StepへのConcurrent `advance`でTool Portの`execute()`がexactly onceになる。
- Stored State、attempt count、output、completionが実実行回数と矛盾しない。
- 別Runは不要にGlobal Serial化しない設計を優先するが、MVPで安全性を確保する最小実装が明瞭ならService-level Lockも許容する。
- Cross-process／Distributed Lockは実装しない。

### Required Tests

- 実Thread＋Blocking／Counting Fake Toolで同時`advance`を再現し、実行1回をAssert。
- `advance`対`cancel`、Approval対Cancelの少なくとも代表RaceをTestし、二重実行、Late publishまたは虚偽Stateが無いことをAssert。
- REST／`asyncio.to_thread`経路でもSource上同じAtomic Boundaryを通ることをFocused Testまたは明示的Composition Assertionで示す。

## 6. P8-CR2 — Actual Frozen Authorization Envelope／Approval Evidence

### Required

既存の未使用`AuthorizationEnvelope`を装飾型のまま残さない。Architecture正本のBounded MVPに合わせ、実行Stateへ接続する。

最低限、新規RunのFrozen Envelopeで次を表現する。

```text
Run Identity
Allowed Step IDs
Allowed Tool IDs／Action Set
Resource Scope（本Phaseではfixture_only等の正直な限定値）
Max Step／Attempt Boundary
Expiry／Deadline
Gate Conditions／Important Gate Reasons
```

- `start_run()`でServer側がEnvelopeを生成し、Run SnapshotとともにPersistする。
- CallerがEnvelopeそのものを自由入力してAuthorityを拡張できない。
- `advance()`はStep実行直前にRun／Step／Tool／Resource／ExpiryがEnvelope内か検証する。
- 不一致はTyped Failureへ収束し、Tool Execution 0をTestする。
- Approval Evidenceは少なくともRun／Step／Tool／Decision／Actor Class／Timestamp／Gate Reasonを相関し、Restart後も保持する。
- 別Run、別Step、別ToolへのApproval／Envelope再利用を拒否する。
- 既存Run Store FileをCorrupt扱いにしないBackward Compatibilityを維持する。
- 既存`approved: bool`をCompatibility Fieldとして残すかMigrationするかは実装判断に任せるが、真の正本はTyped Evidenceとする。

### Non-goals

- Real Filesystem Tool。
- Real Network Tool。
- Real MCP。
- Dynamic Authority／Sub-agent。
- Enterprise Policy Language。

## 7. P8-CR3 — Evidence／Current Prose Correction

- Historical P8-D／E Recoveryを改変しない。
- Historical false claimを訂正するAppend-only Correction Addendumを作る。
- 新Traceability AddendumとExact ReturnでP8-CODEX-001〜003のDispositionを示す。
- Rework成立後のAcceptance集計を次へ統一する。

```text
PASS             38
PARTIAL           1  # P8-ACC-038
USER MANUAL GATE  1  # P8-ACC-040
TOTAL             40
```

- Real MCP／Real ModelはAcceptance PARTIALへ混入させず、Scope外／NOT RUN Boundaryとして別記する。
- Claude localhost Browser EvidenceはAutomated Candidate EvidenceでありUser Manual PASSではない。
- `constitution/rules/external-write-requires-human-gate.md`の「Harnessはまだ存在しない」という古い時点文言を、現状のFake／Deterministic Harness成立とReal Tool非接続を正直に示す文言へ更新する。
- Controller Reviewで記録済みのBrowser／`/tmp` Incidentは再調査せず、Non-blocking Process Nonconformanceとして参照する。

## 8. P8-CR4 — Verification／Internal Review／Return

1. P8-CODEX-001〜003をFinding単位で再判定する。
2. Dev Agent Focused Test、Persistence／Restart、REST、Constitution相関を実行する。
3. Backend Canonical Test／Mypy／Ruffを実行する。
4. Frontend Sourceに変更が無ければFrontend再実行は不要。変更した場合だけTypecheck／Test／Lint／Buildを実行する。
5. Internal Reviewを1 Cycle行う。
6. Recovery IndexとExact Return Handoffを作る。

## 9. Authority／禁止事項

許可：

- Project Root内の対象Source／Test／Current Constitution prose／Phase 8 DocsのRead／Mutation。
- 既存`.venv`、既存Dependency、既存Node Modulesを使ったTest／Static／Build。
- Project Root内Test Temporary Directory。

禁止：

- Git Read／Mutation、Commit、Push。
- Network／Install／Download。
- Real Browser。
- Real Model／Real MCP／Provider Memory。
- User `runtime_data/`のRead／Mutation。
- Project Root外File／Directoryの作成、更新または削除。
- Backup、Roadmap、Phase 8 Closure、Phase 9。
- P8-A〜P8-Fの全面再実装。

## 10. Execution Control

- Current TaskのままP8-CR0→CR1→CR2→CR3→CR4を連結実行する。
- 実装難度、Diff量、Blast Radius、Controller Review前、Minor Finding、Progress ReportはTrue Stopではない。
- RiskはFocused Test、Canonical Regression、Recovery IndexおよびInternal Reviewで管理する。
- Routine Progress報告後も自走する。
- Long-run前のManual Compactionは既にUserが行う運用であり、本Taskから再要求しない。
- True StopまたはResource Hard Stop接近時だけ、Current WUのExact Recoveryを残してSafe Returnする。

## 11. Return Contract

Exact Returnには次を含める。

```text
P8-CODEX-001〜003 Disposition
Changed Paths
Concurrency Probe Results
Authorization Envelope実配線Evidence
Approval Evidence Persistence／Restart Evidence
Backward Compatibility Evidence
Focused／Canonical Validation
Internal Review Finding／Rework
Acceptance 38 PASS / 1 PARTIAL / 1 USER MANUAL GATE
Process Action Inventory
Exact Next Action: Codex Controller Re-review
```

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL`。Return後は停止する。
