# Docs公開名義洗浄Report

- 文書ID: `public_identity_docs_scrub_report`
- 状態: `completed`
- 作成日時: `2026-07-21 11:29:25 JST`
- 更新日時: `2026-07-21 11:29:25 JST`
- Snapshot: `20260721112925`
- 実施担当: 設計者役担当Task
- 正本言語: 日本語
- 根拠: ユーザーの明示的な全Docs名義統一指示
- supersedes: なし

## 1. Objective

`docs/`内に残っていた廃止済み第一者名義を除去し、第一者の公開名義を`Nazuna Research`へ統一する。

削除対象の実値は、本Reportへ再掲しない。

## 2. Rule Applied

```text
Human-readable Name  : Nazuna Research
Project Internal Name: Nazuna Research Governance LLM
Machine-safe Slug    : nazuna-research
Repository Owner     : margpa-labs
```

個人GitHub AccountへのCommit帰属は一般表現へ変更し、Account HandleをDocsへ残さない。

## 3. Scope

```text
Target Root        : docs/
Matched Occurrence : 67
Affected Files     : 32
Edit Method        : apply_patch
```

対象Category：

- Requirements
- Architecture
- Governance
- Handoffs
- Documentation Index
- User Manual
- Operations Policy／Report

## 4. Affected File Manifest

```text
docs/architecture/governance_definition_platform_architecture_20260719112304.md
docs/architecture/public_documentation_and_phase_compilation_architecture_20260720231036.md
docs/documentation_index_20260720220216.md
docs/documentation_index_20260720222402.md
docs/documentation_index_20260721111659.md
docs/governance/governance_definition_catalog_20260719112304.md
docs/governance/runtime_governance_20260718174637.md
docs/handoffs/common_project_handoff_20260718174637.md
docs/handoffs/common_project_handoff_20260718193435.md
docs/handoffs/common_project_handoff_20260719142558.md
docs/handoffs/common_project_handoff_20260719164641.md
docs/handoffs/common_project_handoff_20260719171836.md
docs/handoffs/common_project_handoff_20260720220216.md
docs/handoffs/common_project_handoff_20260720222402.md
docs/handoffs/common_project_handoff_20260720231036.md
docs/handoffs/common_public_identity_and_naming_rule_20260721111659.md
docs/handoffs/public_documentation_handoff_20260718174637.md
docs/operations/phase_completion_backup_policy_20260720222402.md
docs/operations/publication_privacy_scrub_report_20260720220216.md
docs/requirements/documentation_rules_20260718193435.md
docs/requirements/documentation_rules_20260719142558.md
docs/requirements/documentation_rules_20260719171836.md
docs/requirements/documentation_rules_20260720220216.md
docs/requirements/documentation_rules_20260720222402.md
docs/requirements/generic_governance_definition_platform_requirements_20260719112304.md
docs/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md
docs/requirements/project_requirements_20260718174637.md
docs/requirements/project_requirements_20260718193435.md
docs/requirements/public_identity_and_personal_information_policy_20260720220216.md
docs/requirements/public_identity_and_personal_information_policy_20260721111659.md
docs/user_manual/phase_1_macos_user_manual_20260719004209.md
docs/user_manual/phase_1_macos_user_manual_20260719171836.md
```

Manifestの記載数と事前Searchの対象File数は32で一致する。最終合格条件はFile数だけでなく、Target Root全体の残存0件で判定する。

## 5. Semantic Transformation

単純置換だけでなく、次を文脈別に修正した。

- Author／Maintainer／Public Identityを`Nazuna Research`へ統一
- Project通称を`Nazuna Research Governance LLM`へ統一
- Package／Namespace例をMachine-safe Slugへ変更
- 個人GitHub Accountへの帰属を、Handleなしの一般表現へ変更
- 旧名義を再掲する移行説明／禁止例を一般表現へ変更
- 名義例外の判断権限を設計者役Taskへ限定

## 6. Append-only Exception

今回の処理は、公開識別情報の除去を目的としてHistorical Docsを直接変更したため、Strict Append-onlyのPrivacy Exceptionに該当する。

結果として、対象Historical Fileは作成時点のBitwise内容と一致しない。過去に計算されたFile Size／Digestが存在する場合、それらを現在FileのDigestとして使用しない。

将来のPhase 1-exでは、公開候補Artifactから新しいManifest／Digestを再計算する。

## 7. Verification

2026-07-21 11:29:25 JSTに、`docs/`全体へCase-insensitive Searchを実行した。

```text
Deprecated First-party Name Match : 0
Result                            : PASS
```

Machine-safe SlugはGovernance Package／Namespace例にだけ残っている。

## 8. Non-scope

今回は次を走査・変更していない。

- `src/`
- `tests/`
- `scripts/`
- `config/`
- Root Metadata
- Git Metadata
- Model Artifact
- External Service
- GitHub Repository

これらはPhase 1-exのRead-only Preflight後に扱う。

## 9. Completion

`docs/`内の第一者名義統一は完了した。
