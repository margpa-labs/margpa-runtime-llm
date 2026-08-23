# Phase 4 Codex Second Independent Review — Exact Rework Handoff

```yaml
document_id: phase_4_codex_second_independent_review_rework_handoff_20260822071644
status: major_rework_required
phase: phase_4
subphase: phase_4_h
work_unit: p4_h_wu_002_codex_second_independent_major_review
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-22 07:16:44 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_4/handoffs/phase_4_claude_rework_complete_candidate_handoff_ja.md
completion_line: phase_4_claude_second_rework_complete_candidate
source_rework_authorized: true
test_rework_authorized: true
frontend_rework_authorized: true
new_append_only_evidence_authorized: true
stable_doc_mutation_authorized: false
runtime_data_access_authorized: false
definitions_mutation_authorized: false
git_mutation_authorized: false
phase_4_closure_authorized: false
phase_5_authorized: false
```

## 0. Controller Decision

`REJECT REWORK COMPLETE_CANDIDATE / SECOND MAJOR REWORK REQUIRED`。

前回`P4-CODEX-001..006`の中心的な修正は実Sourceへ反映されている。特にActual Entrypoint Wiring、Canonical Mode Mutation Path、Definition 0／Invalid Bundle、ENFORCE Failure Policyは改善を確認した。

ただし、Frozen Phase 4 ContractをClosureするには、次の重大残件がある。

```text
P4-CODEX-007 : Evidence／Standard ResultのTraceability不足
P4-CODEX-008 : Phase 3 Unbound Planを実Bindingしておらず、Binding Identityも不完全
P4-CODEX-009 : Configurationの複数External Applier Patchが部分適用し得る
P4-CODEX-010 : Authority StalenessとTerminal Conflict Resolutionが不完全
P4-GOV-002   : Project Root外Test Temp使用とCompletion Handoff内の矛盾

Phase 4 Technical Closure : BLOCKED
Phase 4 User Acceptance   : NOT READY
Phase 5                   : NOT AUTHORIZED
```

これはScope拡張ではなく、既存の`P4-RES-*`、`P4-BND-*`、`P4-ACT-*`、`P4-EVD-*`、`P4-ACC-*`および既承認Configuration Atomicity Contractを満たすためのReworkである。

## 1. Mandatory Repository Recovery

Provider Summary、Auto-compaction Summary、会話履歴または本Handoffだけを正本にしてはならない。次をRepositoryから再読してから再開する。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
3. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`
4. `docs/project/phases/phase_4/requirements/phase_4_requirements_ja.md`
5. `docs/project/phases/phase_4/architecture/phase_4_architecture_ja.md`
6. `docs/project/phases/phase_4/adr/phase_4_adr_ja.md`
7. `docs/project/phases/phase_4/operations/phase_4_execution_plan_ja.md`
8. `docs/project/phases/phase_4/operations/phase_4_acceptance_matrix_ja.md`
9. `docs/project/phases/phase_4/handoffs/phase_4_claude_execution_handoff_ja.md`
10. `docs/project/phases/phase_4/handoffs/phase_4_codex_independent_review_rework_handoff_ja_20260822015458.md`
11. `docs/project/phases/phase_4/handoffs/phase_4_claude_rework_complete_candidate_handoff_ja.md`
12. 本Handoff。

開始前に次を明記する。

```text
Repository Recovery       : PASS / FAIL
Active Phase              : Phase 4 Second Rework
Current Controller Handoff: 本Handoff
Git Mutation              : FORBIDDEN
Phase 5                   : FORBIDDEN
```

## 2. P4-CODEX-007 — Evidence／Standard ResultのTraceability不足

### Confirmed Finding

`GovernancePointTerminalPayload`は現在、次の集計値を中心に保持する。

```text
selected_descriptor_count
recommended_action_count
executed_action_count
severity／reason／latency／call_count
```

しかし、どのBinding／Plan／Rule／Evaluation／Recommendation／Actionが結果を構成したかを復元できない。

- `binding_digest_sha512`、Source Plan ID／Digest、Capability／Authority／Policy／Budget／Registry DigestがEvidenceにない。
- Selected Descriptor／Rule IdentityまたはDigestがEvidenceにない。
- Observation／DeviationのTyped Outcome／ReasonがEvidenceにない。
- Recommended ActionとExecuted／Not-executed Actionが別IdentityとしてEvidenceにない。
- Executed Actionの`executed`、`intervening`、`not_executed_reason_code`がEvidenceにない。

したがって、件数は一致してもRecommendationとExecutionの対応を追跡できず、`P4-RES-001／003／004`、`P4-EVD-001`、`P4-ACC-012`をCloseできない。

さらに次のFailureはSafe Statusへ残らない。

- Mode ProviderがUnreadableな場合、HookはFail-closedするが、Last Result／Evidenceへ`mode_unavailable`を記録しない。
- `GovernanceObserverPort.is_active()`または外部Observer呼出し自体がRaiseした場合、LogのみでProcess-local Degraded Statusへ反映しない。

### Required Correction

- `StandardGovernanceResult`からPhase 3 Evidence Portへ、Raw Contentを含まないBounded Typed Projectionを作る。
- 最低限、次をEvidenceから追跡可能にする。

```text
Invocation ID（既存Correlationで可）
Point／Stage／Mode／Execution State
Binding ID／Digest
Source Plan ID／Digest
Capability／Authority／Policy／Budget／Registry Digest
Selected Descriptor／Rule IDまたはSafe Digest
Observation／DeviationのTyped Outcome／Reason／Severity
Recommended Action ID／Reason Descriptor ID／Severity
Executed Action ID／executed／intervening／not_executed_reason_code
Latency／Call Count／Unavailable／Degraded Reason
```

- Recommended ActionとExecuted Actionを件数へ圧縮せず、別のBounded Typed Listまたは別Event Identityとして保存する。
- Raw Prompt／Output／Thinking／Secret／Absolute Path／Definition本文／Raw Exceptionは保存しない。
- Mode Unavailable、Observer Activity Check Failure、Observer Terminal FailureをModel I/Oから分離しながら、Process-local Last Result／Degraded Statusで可視化する。
- Default OBSERVEのEvidence Failureは非介入を維持する。ENFORCEのStop／Reject判定をEvidence再評価で作り直してはならない。
- Restart Readback Testは「Countが同じ」だけでなく、RecommendationとExecuted／Not-executedのIdentity／Reasonが保持されることを検証する。

## 3. P4-CODEX-008 — Phase 3 Unbound Planを実Bindingしていない

### Confirmed Finding

Frozen Phase 4は、Phase 3で生成したUnbound Compiled Planを上書きせず、新しいBound ArtifactへBindingする設計である。

しかしActual Compositionは次の状態である。

```text
RuntimeGovernanceComposition.bind_point()
  source_plan_id=None
  source_plan_digest_sha512=None
```

`load_reference_descriptors()`はFilesystem ProviderのVerified Sourceを独立に読み、Typed ARGD／DAGD Descriptorを作るが、同じVerified PackageからPhase 3 Normalized IR／Unbound Compiled PlanのIdentityを受け取らない。したがってPhase 4 Bindingは、実際にはPhase 3 Planへ結び付いていない。

加えてBinding Digest Payloadは`unavailable_reason_code`を含まない。同じPoint／Snapshot／Empty Descriptorでも、`no_provider`、`provider_failure`、`invalid_bundle`が同一Binding ID／Digestになり得る。これは「全Integrity Inputが変われば別Binding」という`P4-BND-002／003`、`P4-ACC-002／003`を満たさない。

### Required Correction

- Filesystem Providerの同一Verified Readから、Phase 3 Trusted Adapter／Normalized IR／Unbound Compiled Planを得る共通Pipelineを使用する。Verified Sourceを二度読みしない。
- ARGD／DAGD Typed Execution Descriptorは、同じVerified Source Resultへ接続したTrusted Extensionとして維持してよい。ただしSource Plan Identityを`None`のままにしない。
- `ReferenceDescriptorLoadResult`または同等のTyped Artifactに、最低限次を持たせる。

```text
provider／package／definition state
source_plan_id
source_plan_digest_sha512
descriptors
safe unavailable reason
```

- Non-empty DescriptorをExecutable Bindingへ使う場合、ValidなSource Plan ID／Digestを必須にする。Plan不在／Digest不整合はUnavailable、Action 0。
- Binding Digestへ、実際のSource Plan ID／Digest、Point／Stage相当Identity、選択Descriptor／Rule IdentityまたはDigest、Capability／Authority／Policy／Budget／Registry、およびBindingのSafe unavailable reasonを含める。
- Phase 3 Unbound Planそのものは変更／上書きしない。
- Actual Local Entrypoint Integration Testで、Valid Bundle時のBindingが`source_plan_id is not None`かつDigest一致、Bundle変更で旧Binding Cache Missになることを固定する。
- Empty／Invalid／Provider Failureは互いに異なるTyped Stateとして維持し、同一Digestへ不正に衝突しないことをTestする。

## 4. P4-CODEX-009 — Configuration Patchが部分適用し得る

### Confirmed Finding

`ConfigurationControlService.apply()`は、同一Patchに`governance_mode`と`main_governance_mode`の両方が含まれる場合、次の順で外部StateをMutateする。

```text
Phase 3 Governance Applier.apply()
→ Phase 4 Main Governance Applier.apply()
→ ConfigurationControlService内部Snapshot／RevisionをCommit
```

Phase 3 Applier成功後にPhase 4 Applierが失敗すると、ConfigurationControlService内部Snapshot／Revisionは旧状態のままだが、Phase 3 Runtime Modeだけ先に変更済みになる。Comment上の「one success boundary」は複数External Applier Patchでは成立しない。

現在のTestは各Applier単体の失敗、またはGovernance＋process-local fieldを確認するが、Phase 3＋Phase 4両Modeを同一Patchへ入れた第二Applier失敗を検証しない。

### Required Correction

次のいずれかを選ぶ。

1. External ApplierをPrepare／Commit／Rollback可能な二段階Contractへ変更し、全External StateをAtomicにCommitする。
2. Phase 4 MVPでは、複数External Applierを同一Patchで変更する要求を、Applier呼出し前にTyped Unsupportedとして拒否する。

Phase 4の最小安全解は`2`でよい。黙って順次適用しない。

必須Test：

- Phase 3 Mode＋Phase 4 Modeの混在Patchを、どのApplierも呼ばず拒否する、または完全Atomicに適用する。
- 第一Applier成功／第二Applier失敗を模擬し、両Runtime Controller、Configuration Snapshot、Revision、Digest、Operation Receiptがすべて旧状態である。
- 単独のPhase 3／Phase 4 Mode Apply、CAS、Concurrent Apply、Idempotencyは維持する。

## 5. P4-CODEX-010 — Authority Staleness／Terminal Conflictが不完全

### Confirmed Finding

`BoundGovernancePlan`は`authority_snapshot_digest_sha512`を保持するが、`action_resolver._binding_is_stale()`はCapability／Policy／Budget／Registryだけを比較し、Current Authority Digestを比較しない。

これはArchitecture §9の「Authority Revision変更でStale Bindingを再利用しない」と`P4-BND-003`に反する。Live AuthorityにAction IDが残っていれば、Revision／他Grant集合が変わった古いBindingでも実行へ進み得る。

またTerminal Conflictは、`dict`挿入順で最初に見つかった`stop_before_generation`または`reject_output`を選ぶ。Point／Stage適合性やSeverityを比較する前に他ActionをSupersedeするため、入力順によって「無効なTerminal Actionが有効なTerminal Actionを消し、その後Point不適合で自身も実行されない」結果になり得る。

### Required Correction

- `_binding_is_stale()`へCurrent Authority Snapshotを渡し、BindingのAuthority Digestと比較する。
- Authority RevisionまたはGrant集合の変更はBinding StaleとしてAction 0にする。Current Authority Check自体も維持する。
- Terminal Conflict Resolutionを入力順から分離する。
- Point／Stage／Registry／Authorityへ適合する候補をSafeに評価した上で、明示Criticality／Severity規則により一意に解決する。
- 解決不能なら全候補Action 0／`conflict_unresolved`。無効候補が有効候補を先にSupersedeしてはならない。
- Recommendation順序を反転したTest、Authority Revisionだけを変更したTest、Grant集合変更Test、両Terminal候補Testを追加する。

## 6. P4-GOV-002 — Test Temp BoundaryとHandoff内の矛盾

### Confirmed Finding

Claude Rework Handoff §11は、Final Validationがpytest既定のProject Root外System Temporary領域を実際に使用したと明記する。一方、§14はRoot-outside Actionを`NOT PERFORMED`と記録する。

この2つは同時に成立しない。

```text
Project Root外pytest Temporary Write : PERFORMED
Technical Test Result                 : 参考として有効
Root Boundary Compliance              : FAIL
Completion Handoff §14                : FACTUAL CORRECTION REQUIRED
```

Project Root内で自ら新規作成した`tmp/pytest-basetemp-p4-rework`の削除は、前HandoffでExact Cycle-owned Cleanupを許可していたため、それ自体を違反扱いしない。

### Required Correction

- Existing Handoffを編集しない。
- `docs/project/phases/phase_4/history/operations/phase_4_gov002_test_temp_boundary_and_completion_claim_correction_ja_<timestamp>.md`を新規Append-onlyで作る。
- Root外Temporary使用を`PERFORMED / GOVERNANCE VIOLATION`、§14を`FALSE CLAIM CORRECTED`として記録する。
- 次のValidationはProject Root直下の短い専用Pathだけを使用する。

```text
Exact Base Root: <PROJECT_ROOT>/.p4t
pytest basetemp: <PROJECT_ROOT>/.p4t/p
OS TMPDIR      : <PROJECT_ROOT>/.p4t/t
Tool Cache     : <PROJECT_ROOT>/.p4t/c
```

- `uv run`はProject Root外Cache／Temporaryへ接触し得るため使用しない。既存`./.venv/bin/python -m pytest`を使う。
- pytestには`--basetemp="$PWD/.p4t/p"`、Processには`TMPDIR="$PWD/.p4t/t"`を与える。
- Frontend Commandにも同じ`TMPDIR`を与える。Network／Dependency Installは禁止。
- `.p4t`はこのCycleが新規作成した専用Pathに限り、全Test／Evidence記録後にExact Cleanupしてよい。削除前後を記録する。
- 短いRoot-local Tempでも既存SQLite Testが失敗する場合、System TempへFallbackしない。Exact Failureを調査し、Root-local Fixture／Path Contractを修正するか、ControllerへTechnical Blockerとして返す。

## 7. Required Validation

### 7.1 Focused

- Standard Result／Evidence Typed Identity／Digest／Recommendation／Execution separation。
- Evidence Restart Readback／Write Failure／Observer Activity Failure／Redaction。
- Source Plan → Binding Identity／Digest／Cache Invalidation。
- Empty／Invalid／Provider Failure Typed State and Action 0。
- Mixed Phase 3＋Phase 4 Configuration Patch Atomicity。
- Current Authority Revision／Grant Change Stale Binding。
- Reverse-order Terminal Conflict／Unresolved Conflict。
- Actual Local Entrypoint、Public／Basic Call 0、v1／v2／Persistent／RAG／Terminal ordering。
- Frontend Typecheck／Lint／Test／Build。

### 7.2 Full／Static

Project Root-local `.p4t`だけを使用し、次を再実行する。

```text
./.venv/bin/python -m pytest ...focused... --basetemp="$PWD/.p4t/p"
./.venv/bin/python -m pytest -q --basetemp="$PWD/.p4t/p"
./.venv/bin/ruff check src tests
./.venv/bin/ruff format --check src tests
./.venv/bin/mypy src
TMPDIR="$PWD/.p4t/t" npm run typecheck
TMPDIR="$PWD/.p4t/t" npm run lint
TMPDIR="$PWD/.p4t/t" npm run test
TMPDIR="$PWD/.p4t/t" npm run build
```

pytest実行ごとに同じ非空`basetemp`を使い回さない。必要なら`.p4t/p-focused`、`.p4t/p-full`へ分ける。

## 8. Exact Allowed Scope

### Read

- Project Root内の本Reworkに必要なSource／Test／Frontend／Phase 3／Phase 4 Docs。
- `definitions/`はRead-only Verification Source。

### Write／Modify

必要な最小Pathだけを動的に選択する。使わないPathは変更しない。

```text
src/margpa_runtime_llm/modules/runtime_governance/**
src/margpa_runtime_llm/adapters/runtime_governance/**
src/margpa_runtime_llm/bootstrap/runtime_governance.py

src/margpa_runtime_llm/modules/audit_evidence/**
src/margpa_runtime_llm/adapters/audit_evidence/**
src/margpa_runtime_llm/bootstrap/audit_evidence.py

src/margpa_runtime_llm/modules/configuration_control/**
src/margpa_runtime_llm/modules/governance_definitions/**
src/margpa_runtime_llm/adapters/governance_definitions/**
src/margpa_runtime_llm/bootstrap/configuration_control.py
src/margpa_runtime_llm/bootstrap/governance_definitions.py
src/margpa_runtime_llm/bootstrap/web_application.py
src/margpa_runtime_llm/entrypoints/web/main.py

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/**
frontend/src/**
frontend/index.html
src/margpa_runtime_llm/web/static/**

tests/unit/runtime_governance/**
tests/unit/audit_evidence/**
tests/unit/configuration_control/**
tests/unit/governance_definitions/**
tests/unit/conversation/test_conversation_generation_governance_hooks.py
tests/unit/web/**
tests/integration/audit_evidence/**
tests/integration/governance_definitions/**
tests/integration/web/**

.p4t/**
```

Docs Writeは新規Append-onlyだけを許可する。

1. `docs/project/phases/phase_4/history/operations/phase_4_gov002_test_temp_boundary_and_completion_claim_correction_ja_<timestamp>.md`
2. 必要な新規Rework Evidence `docs/project/phases/phase_4/history/operations/phase_4_second_rework_..._<timestamp>.md`
3. `docs/project/phases/phase_4/handoffs/phase_4_claude_second_rework_complete_candidate_handoff_ja.md`

## 9. Forbidden

- Project Root外のRead／List／Stat／Write／Delete／Execute Target。
- `other/`、別Project、Provider Memory、Claude Memory、Codex Memory、External Service、Network、Secret／Credential。
- `runtime_data/`のRead／List／Stat／Write／Delete。
- `models/`のRead／List／Stat／Write／Delete／Load／Benchmark。
- `definitions/`のWrite／Rename／Delete／Format／Auto-fix。
- Stable Current／Shared／Roadmap／Phase Index／Requirements／Architecture／ADR／Execution Plan／Acceptance Matrixの編集。
- Existing History／Existing Handoffの編集／置換／削除。
- Git／GitHub Mutation、Commit／Push／Branch／Tag／Release。
- Phase 4 Closure／User Acceptanceの代行／Backup／Phase 5／6／DeepSeek／AWS。
- Frozen必須項目の任意Deferred化。
- System Temp、`/tmp`、`/private/tmp`、Provider CacheまたはUser Home CacheへのFallback。
- CountだけをRecommendation／Execution Evidenceと呼ぶこと。
- `source_plan_id=None`の実BindingをPhase 3 Plan Bindingと呼ぶこと。
- 複数External ApplierをRollbackなしで順次Mutateすること。

## 10. Completion Contract

Routineな実装判断、Test失敗、Type Error、Frontend整合、Evidence Schema、Root-local Tempの短Path調整はユーザーへ返さず、Claude側設計統括者役が自己Review／Reworkする。

停止が必要なのは次だけである。

- Project Root外Actionが必要。
- Stable／Frozen Contract変更が必要。
- User Data／`runtime_data/`が必要。
- Git／External／Network／Secret／Model Loadが必要。
- Phase 4 Acceptanceそのものを変えるHuman Decisionが必要。

完了時は新規`phase_4_claude_second_rework_complete_candidate_handoff_ja.md`に次を記録する。

```text
P4-CODEX-007..010                 : CLOSED / OPEN
P4-GOV-002                        : CORRECTED / OPEN
Source Plan Binding               : Exact Plan ID/Digest Evidence
Binding Integrity Input Matrix    : PASS / FAIL
Evidence Identity/Restart         : PASS / FAIL
Recommendation/Execution Split    : PASS / FAIL
Observer/Mode Degraded Visibility : PASS / FAIL
Mixed External Apply Atomicity    : PASS / FAIL
Authority Stale Matrix            : PASS / FAIL
Terminal Conflict Matrix          : PASS / FAIL
Actual Local Entrypoint           : PASS / FAIL
Public/Basic/v1/v2 Call 0         : PASS / FAIL
Backend Focused/Full              : Exact Tool Output
Frontend Checks                   : Exact Tool Output
Project-local Test Temp           : Exact Path / Created / Cleaned / Postflight
Existing Stable Edit              : Exact Count
Git Mutation                      : Evidence Class付き
Root-outside Action               : PERFORMED / NOT PERFORMED + Evidence Class
runtime_data Access               : Evidence Class付き
Remaining Technical Major         : Exact List
Remaining Governance Major        : Exact List
Recommendation                    : GO / ADJUST / STOP
```

新Completion Handoff作成後は停止する。Phase 4 Closure、Git、Phase 5へ進まない。
