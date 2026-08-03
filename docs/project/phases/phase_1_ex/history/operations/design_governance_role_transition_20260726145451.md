# 設計Governance Role移行記録

- 文書ID: `design_governance_role_transition`
- 状態: `effective`
- 作成日時: `2026-07-26 14:54:51 JST`
- 更新日時: `2026-07-26 14:54:51 JST`
- Snapshot: `20260726145451`
- 作成担当: 設計統括者役
- 対象: 現在のCodex Task、Phase 1-ex、Phase 2以降の設計分業
- Previous Authority: [task_role_write_authority_policy_20260719142558.md](../requirements/task_role_write_authority_policy_20260719142558.md)
- ADR: [adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md](../adr/adr_0024_phase_first_project_documentation_and_lossless_history_20260726145451.md)
- 正本言語: 日本語
- supersedes: 現在のTaskを単独の`設計者役`とする部分

## 1. Effective Transition

Phase 1-ex開始に伴い、現在のTaskの役職を次へ変更する。

```text
Before:
  設計者役

After:
  設計統括者役
  兼 Phase 1-ex設計実務担当
```

Phase 1-ex専用設計者役Taskは作成しない。

## 2. Phase 1-ex Responsibilities

設計統括者役が直接担当する。

- Documentation Target Architecture
- Migration Manifest
- Lossless Compilation規則
- Git／Backup／Release設計
- Role／Authority再編
- Public／Project Boundary
- Canonical Docs構成
- RAG Documentation Scope
- Lightning Auto-start Preflight設計
- Phase 1-ex Review／Completion Gate

## 3. Phase 2 and Later

```text
設計統括者役
  ├─ Project全体要件
  ├─ Cross-Phase Architecture
  ├─ Shared Port／Policy／Governance
  ├─ Phase開始用上位設計
  ├─ Cross-Phase Conflict
  └─ Phase最終Review

Phase別設計者役
  ├─ Phase内Requirements
  ├─ Phase内Architecture
  ├─ Phase内ADR
  ├─ Implementer Handoff
  └─ Phase内再設計
```

Phase別設計者役はPhase 2から必要に応じて配置する。

## 4. Current Write Scope before Migration

Directory Migration完了までは、既存Authorityを暫定維持する。

```text
docs/requirements/
docs/architecture/
docs/governance/
docs/adr/
docs/operations/
docs/user_manual/
docs/handoffs/designer_*
docs/documentation_index_*
```

設計統括者役への名称変更だけを先に有効化し、未作成Target Directoryを既に存在するものとして扱わない。

## 5. Target Write Scope

Migration後の候補：

```text
docs/project/current/
docs/project/shared/
docs/project/phases/phase_1_ex/
docs/project/phases/<phase>/phase_index_ja.md
設計統括者Review／Cross-Phase ADR
```

Phase別設計者、実装者、対外Docs役の正確なWrite ScopeはMigration ManifestとTask Role Policy後継版で確定する。

## 6. Notification

Directory Migration完了後、次へ通知する。

- 実装者役
- 対外Docs役
- 将来のPhase別設計者役

通知内容：

- New Directory Tree
- Current Index
- Read-only Scope
- Write Scope
- Handoff／Status配置
- Stable Filename
- Timestamp Event規則
- RAG Default Scope
- Git運用開始時点

Migration前に新Pathへ書くよう依頼しない。

## 7. Decision Authority

設計統括者役は外部に存在しない権限を生成しない。

GitHub公開、Cloud変更、Secret登録、Model Download、Dependency変更、実装Scope拡大または破壊的Migrationは、ユーザー決定とAccepted Procedureを必要とする。

## 8. Current State

```text
Role Transition            : EFFECTIVE
Phase 1-ex Designer Task   : NOT CREATED／NOT REQUIRED
Directory Migration        : NOT STARTED
Phase 2 Designer Task      : FUTURE
```
