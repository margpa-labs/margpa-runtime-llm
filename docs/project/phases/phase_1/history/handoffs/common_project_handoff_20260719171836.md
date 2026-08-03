# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 17:18:36 JST
supersedes: common_project_handoff_20260719164641.md
project_root: margpa-runtime-llm/
```

## 1. 文書の目的

本書は、設計者役、実装者役、対外向けDocs作成者役など、複数タスク間で共有するプロジェクト共通情報の正本である。

タスク開始時は、最新の`documentation_index_YYYYMMDDHHMMSS.md`からCurrent Requirements、Architecture、Governance、ADR、Operations、Handoff、User Manualを確認する。

Docsは原則として読み取り専用で扱い、担当範囲外の文書を勝手に変更しない。

## 2. プロジェクト識別情報

- Project Name: `margpa-runtime-llm`
- Display Name: `MARGPA Runtime LLM`
- 通称: `Nazuna Research Governance LLM`
- Project Root: `margpa-runtime-llm/`
- Shared Documentation Root: `margpa-runtime-llm/docs/`
- 初期実行環境: Apple M2 Pro、16GB RAM、macOS、Apple Silicon
- Main Model: `Qwen3-4B-Q4_K_M.gguf`
- Guard Model候補: `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`
- Judge Model候補: `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`

ユーザーが`docs/`等の相対的なProject内Pathだけを示した場合、Project Root基準で解釈する。

## 3. Current Entry Points

- Documentation Rules: `docs/requirements/documentation_rules_20260719171836.md`
- Task Role Authority: `docs/requirements/task_role_write_authority_policy_20260719142558.md`
- Phase Backup Policy: `docs/operations/phase_completion_backup_policy_20260719171836.md`
- Known Issues／Observations: `docs/operations/known_issues_and_observations_20260719171836.md`
- Current Roadmap: `docs/architecture/implementation_roadmap_20260719171836.md`
- Phase 1 Readiness Review: `docs/handoffs/designer_review_phase_1_final_readiness_20260719171836.md`
- Current User Manual: `docs/user_manual/phase_1_macos_user_manual_20260719171836.md`
- Current Index: `docs/documentation_index_20260719171836.md`

文書はAppend-Onlyとし、内容変更時は新Timestampの後継文書を作る。

## 4. 役割別の権限

### 設計者役

Requirements、Architecture、Governance、ADR、Operations、User Manual、Index、Common／Designer Handoff、Reviewを管理する。

実装レビュー時、Source／Config／Testsは読み取り専用とし、修正許可なしにFixしない。

### 実装者役

Accepted Handoffとユーザー許可の範囲で`src/`、`tests/`、`scripts/`を変更し、`implementer_status_*`を作成する。Config／Root Fileは明示Scopeがある場合だけ変更する。

Canonical Docsは読み取り専用である。

### 対外向けDocs作成者役

README類、将来の`docs/public/`、`external_docs_status_*`を担当する。Canonical Docsは読み取り専用である。

### 運用評価

設計者役と実装者役の分離は、Phase 1-A～1-Eで有効に機能した。対外Docs役は権限定義済みだが、本格運用評価は今後行う。

## 5. Current Phase State

```text
Phase 0                                 : Complete
Phase 1-A                               : Complete／Accepted
Phase 1-B                               : Complete／Accepted
Phase 1-C                               : Complete／Accepted
Phase 1-D                               : Complete／Accepted
Phase 1-E                               : Complete／Accepted
Phase 1 Cross-phase Readiness           : Pass
Phase 1 User Manual                     : Ready
Phase 1 User Acceptance Test            : Waiting
Designer Completion／Phase 2 Eligible   : Waiting
Phase 1 Backup                          : Not Triggered
Phase 2 Implementation                  : Not Authorized
```

Top-Level Phase 1は`Ready for User Acceptance Test`であり、まだ完了宣言前である。

## 6. Phase 1 Evidence

```text
Default Test       : 161 passed, 2 deselected
Native Metal Test  : 2 passed, 161 deselected
Ruff／Mypy         : Pass
Compileall／Bash   : Pass
Environment        : Python 3.13.14／arm64／Metal／Pass
uv Lock            : 117 packages
uv Offline         : 115 packages／No changes
```

Current User ManualはPhase 1-A～1-E、Language、Thinking、Platform境界、User Acceptance Checklistを含む。

## 7. Known Observation

`MARGPA-OBS-0001`：Mixed-source Presentation Config Error Attribution。

- Severity: Low
- State: Accepted Deferred
- 不正値は安全に拒否される
- Phase 1 Acceptance／BackupをBlockしない
- Phase 2 Config UIまたはExternal Release前のError Taxonomy整理時に再評価

詳細はCurrent Known Issues Registerを参照する。

## 8. Backup Dual Approval Gate

Phase Backupは次の両方が同じProject状態について成立した後に実行可能となる。

```text
Gate A:
  設計者役がPhase完了と次Phase移行可能を明示

Gate B:
  ユーザーがCurrent User Manualの受入テスト全項目合格を明示
```

片方だけ、Implementer Statusだけ、Subphase完了だけではBackupしない。

Gate成立後にSource、Config、Tests、Dependency、Model Definition等のMaterial Changeがあれば、影響範囲に応じて再Review／再Testする。

## 9. User Acceptance Test

対象：

- [phase_1_macos_user_manual_20260719171836.md](../user_manual/phase_1_macos_user_manual_20260719171836.md)

UserはManual Section 22の13項目を確認する。

合格時の推奨宣言：

```text
phase_1_macos_user_manual_20260719171836.mdの
Phase 1ユーザー受入テストは、全項目合格です。
```

## 10. Current Next Action

1. ユーザーがCurrent ManualでPhase 1 User Acceptance Testを行う。
2. 全項目合格なら対象Manualを明示して合格宣言する。
3. 設計者役がMaterial Changeなしを確認する。
4. 設計者役がPhase 1完了・Phase 2移行可能を宣言する。
5. Dual Approval Gate成立後、Phase 1 Backupを作成・検証する。
6. Backup後にPhase 2へ進む。

本Handoffを読むこと自体は、Backup、Project外Write、Phase 2実装を許可しない。
