# Phase 2-A Implementation Authorization Envelope

```yaml
envelope_id: p2_a_envelope_001
revision: exact_1
status: active
phase: phase_2
subphase: phase_2_a
created_at: 2026-08-12 01:51:52 JST
authority_source: user_phase_2_a_full_automation_start
controller: プロジェクト責任者兼設計統括者役
```

## 1. Authorized Root

```text
<AUTHORIZED_PROJECT_ROOT>
```

Root外、Sibling Project、`other/`、Public別Repository、Human-private Backup領域およびSymbolic Link先はRead／Write／Executeの対象外である。

## 2. Authorized Transition Line

```text
P2-A-WU-001 Design Freeze
-> P2-A-WU-002 Domain／Port／Unit Test Implementation
-> P2-A-WU-003 Compatibility／Acceptance／Closure Recommendation
-> User Final Acceptance待ちで停止
```

Phase 2-Bを開始しない。

## 3. Authorized Mutation

### New Source

```text
src/margpa_runtime_llm/modules/conversation/domain/__init__.py
src/margpa_runtime_llm/modules/conversation/domain/errors.py
src/margpa_runtime_llm/modules/conversation/domain/identity.py
src/margpa_runtime_llm/modules/conversation/domain/models.py
src/margpa_runtime_llm/modules/conversation/ports/__init__.py
src/margpa_runtime_llm/modules/conversation/ports/conversation_store.py
```

### New／Phase-local Tests

```text
tests/unit/conversation/test_conversation_domain.py
tests/unit/conversation/test_conversation_store_contract.py
```

### Phase 2-A Documentation

```text
docs/project/phases/phase_2/{requirements,architecture,adr,governance,operations,handoffs}/phase_2_a_*
docs/project/phases/phase_2/history/{index,operations,handoffs}/phase_2_a_*
docs/project/phases/phase_2/phase_index_ja.md
docs/public/roadmap_ja.md
docs/public/history/roadmap/roadmap_phase_2_ja_<timestamp>.md
```

Existing Stable更新は、Before／After History Snapshotを伴う。History既存Fileは変更しない。

## 4. Read-only Existing Source

```text
src/margpa_runtime_llm/modules/conversation/contracts.py
src/margpa_runtime_llm/modules/conversation/public.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
src/margpa_runtime_llm/web/
src/margpa_runtime_llm/bootstrap/
```

Phase 2-Aでは変更しない。

## 5. Authorized Verification

- Target Unit Tests
- Existing Conversation／Web Regression Tests
- Full `pytest`（既存Deselection条件を維持）
- Ruff Format Check／Ruff Check／Mypy
- Shell／TOML／Internal LinkのRead-only Check
- Git Diff／StatusのRead-only Check

TestがProject Root内へ通常Cacheを作る場合、既存Ignore Contract内だけを許可する。Root外Temporary Artifactを作らない。

## 6. Not Authorized

- Git Stage／Commit／Push／Branch／Tag／Release
- Network、GitHub、Cloud、Lightning、Secret、Credential、課金操作
- Dependency／Lockfile／Deployment Profile変更
- Concrete Storage File／Database作成
- Existing v1 API／UI／Runtime変更
- File削除、Cleanup、Rename、Move、Permission変更
- Phase 2-B以降のMutation
- Authorized Root外の操作

## 7. Stop Conditions

- Root／Mutation Scope逸脱またはその疑い
- Existing v1 Wire Contractの変更が必要
- Concrete Storage／Dependency変更が必要
- Secret／Privacy／External／Destructive Actionが必要
- Requirements／Architectureで解消不能な重大Conflict
- Test Failureが本Scopeで安全に解消できない
- 利用可能量等で安全なCheckpointを残せない

Routineな設計補正、Source実装、Test修正、Docs同期および再ReviewはController／実装責任内で解消し、人間判断へ返さない。

## 8. Completion Boundary

Technical Blocker 0、Target／Regression／Static Check合格、Scope外Mutation 0、Phase 2-A Docs／Index／Roadmap整合およびClosure Recommendation作成までを自律完了する。最終Acceptance、Phase 2-B開始、Gitおよび新しいExternal ActionはHuman Gateである。
