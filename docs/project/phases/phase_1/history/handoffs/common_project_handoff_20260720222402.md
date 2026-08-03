# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-20 22:24:02 JST
supersedes: common_project_handoff_20260720220216.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
```

## 1. Current State

```text
Phase 1-A～1-E                 : Complete／Accepted
Acceptance Follow-up           : Implemented／Review Pending
Phase 1-F Repository Work      : Reported Complete／Review Pending
Lightning Native Verification : Waiting
Phase 1 User Acceptance        : Waiting
Phase 1 Completion／Backup     : Waiting
Phase 1-ex Operations          : Added／Requirements Pending
Initial GitHub Publication     : Deferred until Phase 1-ex completion
Privacy Scrub                  : Complete for managed files
```

## 2. New Operational Decisions

- 原則として各Phaseの完了・次Phase着手可能状態でBackupを取得する。
- Backup確定後、同一SnapshotをPhase単位でGitHubへ反映する。
- 初回GitHub公開だけはPhase 1-ex完了後に行う。
- Phase 1-exは運用再整備を扱い、詳細は後続で定義する。
- 毎回、Backup Candidate内の`margpa-runtime-llm/`をSanitizeし、不要Fileをすべて除去する。
- 第一者の公開Identityは常に`Nazuna Research`へ統一する。

## 3. Runtime／Path Verification

- Default Test: 181 passed
- Ruff／Mypy: Pass
- Mac Metal Model Smoke: 2 passed／1 expected skip
- Managed Production Codeの個人固有`/Users/...`: 0件
- Test内の`/Users/example/...`: 架空のPrivacy Fixture
- `.venv/`: 作成時Absolute Pathを含むLocal生成物／公開除外
- `models`: Local Model StorageへのAbsolute Symlink／公開除外
- Lightning CUDA／CPU: Native Verification Pending

詳細は[Runtime動作・絶対Path境界 確認記録](../operations/runtime_and_absolute_path_verification_20260720222402.md)を参照する。

## 4. Current Entry Points

- [Documentation Index](../documentation_index_20260720222402.md)
- [Documentation Rules](../requirements/documentation_rules_20260720222402.md)
- [Backup／GitHub公開Policy](../operations/phase_completion_backup_policy_20260720222402.md)
- [Phase 1-ex Requirements Placeholder](../requirements/phase_1_ex_operations_reorganization_requirements_20260720222402.md)
- [Privacy Policy](../requirements/public_identity_and_personal_information_policy_20260720220216.md)
- [Phase 1-F Status](implementer_status_phase_1f_lightning_cross_environment_runtime_20260719205819.md)

## 5. Next Gate

1. Phase 1-Fの独立Review
2. Lightning Upload Scopeの確定
3. Lightning CUDA／CPU検証
4. Current User Manual／User Acceptance
5. Phase 1完了宣言／Backup
6. Phase 1-exの詳細要件定義と実施
7. Phase 1-ex完了後の初回GitHub公開

Phase 1-G最小Web UI案との順序・関係は未確定であり、後続要件定義で整理する。

## 6. Authorization Boundary

本HandoffはPhase 1-F Acceptance、Phase 1-ex実装、Phase 1-G実装、Backup生成、Git初期化、Commit、Push、GitHub公開、Lightning操作を許可しない。
