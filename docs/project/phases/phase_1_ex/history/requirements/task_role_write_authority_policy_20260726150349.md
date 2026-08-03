# Task Role／Write Authority Policy

- 文書ID: `task_role_write_authority_policy`
- 状態: `accepted_target_policy_not_migrated`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-26 15:03:49 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- Role Transition: [design_governance_role_transition_20260726145451.md](../operations/design_governance_role_transition_20260726145451.md)
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../architecture/phase_1_ex_target_documentation_structure_20260726145451.md)
- Notification Plan: [documentation_migration_task_notification_plan_20260726150349.md](../handoffs/documentation_migration_task_notification_plan_20260726150349.md)
- 正本言語: 日本語
- supersedes: `task_role_write_authority_policy_20260719142558.md`

## 1. Current Transition

```text
Current Task:
  設計統括者役
  兼 Phase 1-ex設計実務担当

Phase 1-ex専用設計者役:
  作成しない

Phase 2以降:
  Phase別設計者役を配置可能
```

Directory Migration完了までは既存Path Authorityを暫定維持する。Target Path AuthorityはCutover通知後に有効化する。

## 2. 設計統括者役

### Standing Responsibilities

- Project全体Requirements
- Cross-Phase Architecture
- Shared Governance／Policy／Port
- Phase構成
- Current Canonical Docs
- Project Continuity Master
- Shared Convention／Schema／Template
- Role Authority
- Phase開始用上位Handoff
- Phase最終Review
- Cross-Phase Conflict
- Backup／Git／Release設計

### Target Write Scope

```text
docs/project/current/
docs/project/shared/
docs/project/phases/<active_phase>/phase_index_ja.md
docs/project/phases/<active_phase>/adr/ Cross-Phase ADR
docs/project/phases/<active_phase>/operations/ Designer Review／Migration
docs/project/phases/<active_phase>/history/handoffs/designer_*
```

Phase 1-exではPhase別設計者役を兼ねるため、Phase 1-ex配下のRequirements／Architecture／ADR／Operations／Handoffsへ書込可能とする。

## 3. Phase別設計者役

Phase 2以降に配置する。

### Write Scope

```text
docs/project/phases/<assigned_phase>/requirements/
docs/project/phases/<assigned_phase>/architecture/
docs/project/phases/<assigned_phase>/adr/
docs/project/phases/<assigned_phase>/operations/ Phase-local Design
docs/project/phases/<assigned_phase>/history/handoffs/designer_*
```

### Read-only

- `docs/project/current/`
- `docs/project/shared/`
- 他PhaseのFrozen Compilation
- `docs/public/`

Cross-Phase変更、Shared Port、Role Authority、Public IdentityまたはGlobal Governanceは設計統括者役へEscalateする。

## 4. 実装者役

### Source Write Scope

```text
src/
tests/
scripts/
```

Accepted Handoffとユーザー許可がある場合：

```text
config/
pyproject.toml
uv.lock
Root Metadata
```

### Docs Write Scope

```text
docs/project/phases/<active_phase>/history/handoffs/implementer_status_*
```

### Read-only

- Current Canonical Docs
- Shared Policy
- Requirements／Architecture／Governance／ADR
- Frozen Phase Compilation
- Public Docs

実装者役はCanonical RequirementsまたはArchitectureを直接変更しない。

## 5. 対外Docs役

### Write Scope

```text
README.md
LICENSE
NOTICE.md
CITATION.cff
docs/public/
docs/project/phases/<active_phase>/history/handoffs/external_docs_status_*
```

### Conditional Write

Lossless CompilationまたはCanonical Docsを作業として生成する場合、Source Meaning Ownerである設計統括者役のReviewを必要とする。

### Read-only

- Requirements
- Architecture
- Governance
- ADR
- Project Continuity Masterの技術内容

Public向けに読みやすくしても、正本の意味を変更しない。

## 6. History

Historyは原則Immutableである。

書込可能なのは新しいEvent Fileの追加だけとし、既存History Fileを編集しない。

Privacy／Credential／Secret Scrubは例外として、変更理由とScrub Recordを必要とする。

## 7. Current／Stable Docs

Stable FilenameはGit Historyを前提に更新する。

- Update前にOwnerを確認する。
- Material ChangeはReviewを必要とする。
- Phase Freeze済みCompilationを通常のCurrent文書として上書きしない。
- Git開始前は変更記録を別DocumentまたはMigration Receiptへ残す。

## 8. Index Authority

```text
Project Current Index:
  設計統括者役

Phase Index:
  Phase別設計者役
  ＋設計統括者役のFinal Review

Public Index／README:
  対外Docs役
  ＋設計統括者役のTechnical Review
```

## 9. Migration Authority

Directory Migrationの実行は、Accepted Manifest、Rollback Planおよびユーザー許可を必要とする。

各担当TaskはMigration完了通知前に新Pathへ書き込まない。

## 10. External Action Boundary

GitHub Push、Cloud変更、Secret登録、Model Download、Dependency変更、Public Access変更または削除操作は、Directory Write Authorityから自動的に許可されない。

## 11. Effective Timing

```text
Role Name Transition:
  Effective now

Old Path Authority:
  Effective until Migration Cutover

Target Path Authority:
  Effective after Migration Completion Notification
```
