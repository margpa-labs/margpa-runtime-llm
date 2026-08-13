# Phase 2-B Conversation Persistence／Lifecycle Implementation Handoff

```yaml
handoff_id: phase_2_b_conversation_persistence_implementation
status: accepted_and_frozen_for_implementer
phase: phase_2
subphase: phase_2_b
created_at: 2026-08-14 JST
from_role: Phase 2設計担当者役
to_role: Phase 2実装者役
review_return_to: Phase 2設計担当者役
final_review: プロジェクト責任者兼設計統括者役
```

## 1. Objective

Phase 2-A Domain／Portを変更せず、Local Private向けSQLite Repository、明示Migration／Checkpoint、Lifecycle Application Service、Generation Context Mapper、Persistent OrchestratorおよびCrash Recoveryを実装する。Existing v1、Public Demo、Shared Basic Previewは未Binding／Storage Write 0のまま維持する。

## 2. Mandatory Inputs

- [Phase 2-B Requirements](../requirements/phase_2_b_conversation_persistence_requirements_ja.md)
- [Phase 2-B Architecture](../architecture/phase_2_b_conversation_persistence_architecture_ja.md)
- [Phase 2-B ADR](../adr/phase_2_b_conversation_persistence_adr_ja.md)
- [Phase 2-B Acceptance Matrix](../operations/phase_2_b_acceptance_matrix_ja.md)
- Phase 2-A `conversation/domain/`、`conversation/ports/`およびUnit Tests
- Existing `conversation/contracts.py`、`conversation/public.py`、`application/conversation_generation.py`

Conflict時はRequirements、Architecture、ADR、Handoff、Acceptance Matrixの順ではなく、上位規則／Controller指示を最優先し、局所文書間の矛盾は実装前にPhase 2設計担当者役へ返す。

## 3. Write Lease／Allowed Paths

実装者のWrite Leaseは一Task・一Writerとし、次だけを許可する。

```text
src/margpa_runtime_llm/modules/conversation/adapters/__init__.py                 NEW
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py NEW
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_migration.py        NEW
src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py     NEW
src/margpa_runtime_llm/modules/conversation/application/persistence_models.py   NEW
src/margpa_runtime_llm/modules/conversation/application/recording.py            NEW
src/margpa_runtime_llm/modules/conversation/application/generation_context_mapper.py NEW
src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py NEW
src/margpa_runtime_llm/modules/conversation/application/__init__.py             MODIFY if export required

tests/unit/conversation/test_sqlite_conversation_store.py                       NEW
tests/unit/conversation/test_sqlite_migration.py                                NEW
tests/unit/conversation/test_generation_context_mapper.py                       NEW
tests/unit/conversation/test_conversation_recording_contract.py                 NEW
tests/unit/conversation/test_persistent_conversation_service.py                 NEW
tests/integration/conversation/test_local_conversation_persistence.py           NEW

docs/project/phases/phase_2/history/handoffs/
  implementer_status_phase_2_b_<timestamp>.md                                   NEW exactly one
```

追加Fileが必要なら勝手に拡張せず、Phase 2設計担当者役へ理由とExact Pathを返す。既存`application/__init__.py`変更は新Public Contract Exportに必要な場合だけとする。

## 4. Forbidden Paths／Actions

次を変更しない。

- `src/margpa_runtime_llm/modules/conversation/domain/**`
- `src/margpa_runtime_llm/modules/conversation/ports/**`
- `src/margpa_runtime_llm/modules/conversation/contracts.py`
- `src/margpa_runtime_llm/modules/conversation/public.py`
- `src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`
- `src/margpa_runtime_llm/web/**`、`src/**/entrypoints/**`
- `config/**`、`scripts/**`、`pyproject.toml`、Lockfile、`.gitignore`
- Existing Phase 2 Docs／History、Public Docs、Current／Shared Docs
- Project Rootの`runtime_data/**`またはRepository外Path

Git Mutation、Network、Package Install、External Service、Permission変更、既存File削除、Production Runtime起動を行わない。

## 5. Implementation Sequence

### B1. Store Core

1. Explicit Root／Bound ScopeのPath ResolverとSafety Check。
2. Read-only `inspect_schema()`。
3. Explicit `initialize_new_store()`。
4. Canonical Snapshot Serialization／Digest／Exact Validation。
5. Repository `get／list／get_commit_receipt／commit`。
6. CAS、Operation Idempotency、Unknown Outcome Normalization。

### B2. Migration／Recovery Storage

1. Explicit Migration Registry／Plan。
2. Checkpoint／Marker／Staging／全件Validation／Atomic Cutover。
3. Receipt Target Digest一致時だけRollback。
4. Test-only Legacy Fixture Step。Production Legacy Stepは0。

### B3. Application

1. Lifecycle Command／Safe Failure Model。
2. Create／Resume／Pending／Generating／Complete／Cancel／Fail／Interrupt／Archive。
3. Completed Branch＋Pending User Mapperと既存上限の明示Error。
4. Persistent Generation Orchestrator。
5. Startup Crash Recovery Gate。

### B4. Opt-in Factory

Disabled／Explicit Local SettingsとBuilderを追加する。Metadata-only Recording Portの型境界は追加できるがConcrete Recorderは作らない。Builder／ImportはWrite 0、RecorderはDefault `None`、Recording Modeは`off`以外を拒否する。Web／CLI／TOMLへ接続しない。

## 6. Required Technical Rules

- Standard Library `sqlite3`以外のStorage Dependencyを追加しない。
- SQL ValueはParameter Bindingし、Snapshot／IDをSQL Identifierへ使わない。
- Model生成中にConnection、Transaction、MutexまたはFile Lockを保持しない。
- Terminal Persistence成功前にTerminal Eventを渡さない。
- Unknown Outcomeは同一Operation Receipt照合以外でRetryしない。
- MigrationはActive StoreのIn-place変換を行わない。
- Test以外のRuntime Dataを作らない。Test Rootは`tmp_path`だけを使う。
- Canonical Message以外のThinking、Prompt、RAG Context、Partial、Hidden Original、Secretを表現／保存しない。
- Recording Hookは未Binding／OFF／Call 0。Filesystem Recorderを実装しない。
- ErrorにPath、SQL、Raw Driver Message、Message ContentまたはCredentialを出さない。

## 7. Required Tests

最低限、Acceptance Matrixの全IDをTest名またはDocstringから追跡可能にする。

- Init／InspectのWrite BoundaryとPermission拒否。
- Snapshot Round-trip、Digest／Metadata／Unknown Field／Schema不一致。
- Create／Update CAS、二Instance Lost Update、Same Operation Idempotency、異Payload拒否。
- Commit Response喪失相当のReceipt収束、Unknown時Blind Retry 0。
- Stable List／Cursor／Scope分離／本文非露出。
- Locked、Read-only、Permission、Capacity、CorruptionのSafe Error。
- Migration Success、変換失敗、Marker残存、旧原本不変、Rollback、Post-write拒否。
- Lifecycle全遷移、Terminal Reopen拒否、Cancel／Complete競合。
- Mapper順序、Branch、除外Role、上限超過Generation Call 0。
- Generation中Storage Lock 0、Terminal Commit後Event、Disconnect Interrupted。
- Startup Crash Recovery、CAS競合、Unknown Outcome。
- Recorder Call 0、Project Root Runtime Data 0、Sensitive Artifact 0。
- Existing v1／Web／Public／Basic Regression。

## 8. Validation Commands

Repository Rootで順に実行する。

```bash
.venv/bin/pytest -q \
  tests/unit/conversation/test_sqlite_conversation_store.py \
  tests/unit/conversation/test_sqlite_migration.py \
  tests/unit/conversation/test_generation_context_mapper.py \
  tests/unit/conversation/test_conversation_recording_contract.py \
  tests/unit/conversation/test_persistent_conversation_service.py \
  tests/integration/conversation/test_local_conversation_persistence.py

.venv/bin/pytest -q tests/unit/conversation tests/integration/web

.venv/bin/ruff format --check src tests
.venv/bin/ruff check src tests
.venv/bin/mypy

.venv/bin/pytest -q
```

`tests/integration/conversation/`が存在しない場合は、許可されたTest File作成時に親Directoryだけを作成してよい。Validation中のProject Root Runtime Data作成有無を前後Inventoryで確認する。

## 9. Evidence／Return Route

実装者は新規Status File一件へ次を記録し、Phase 2設計担当者役へ返す。

```text
From: Phase 2実装者役
To: Phase 2設計担当者役
Result: PASS | PARTIAL | BLOCKED
Changed paths: exact list
Acceptance IDs: PASS/FAIL list
Commands and exact results
Project runtime_data writes: 0 / exact finding
Existing v1 mutations: 0 / exact finding
Public／Basic binding: 0 / exact finding
Sensitive persistence: 0 / exact finding
Known limitations／remaining findings
Rollback unit
```

設計担当者役はSource／Test／StatusをReviewし、局所Findingを実装者へ返して閉じる。設計Acceptance後にだけControllerへClosure Recommendationを提出する。実装者はUserへ直接完了判定を返さない。

## 10. Rollback

Phase 2-BのRollback UnitはAllowed Source／Testの新規Fileと、必要時の`application/__init__.py`追加Exportだけである。既存Domain／Port／v1をRollback対象へ含めない。実Data Migrationを実行しないため、Repository Source RollbackにRuntime Data復旧を混在させない。

## 11. Completion Condition

- Acceptance MatrixのRequired項目が全てPASS。
- Target／Regression／Static／Full SuiteがPASS。
- Existing v1 Mutation 0、Project Root Runtime Data 0、Public／Basic Binding 0。
- Phase 2設計担当者役が設計適合をAccepted。
- ControllerがCross-Phase ClosureをReview可能なEvidenceが揃う。
