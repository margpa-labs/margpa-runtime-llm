# MARGPA Runtime LLM 共通公開名義・名称規則

```yaml
document_state: current_mandatory
created_at: 2026-07-21 11:29:25 JST
supersedes: common_public_identity_and_naming_rule_20260721111659.md
applies_to: all_tasks
public_author_name: Nazuna Research
machine_safe_slug: nazuna-research
repository_owner: margpa-labs
public_repository: margpa-labs/margpa-runtime-llm
exception_authority: 設計者役Taskのみ
```

## 1. Mandatory Rule

全担当Taskは、第一者の名義、名称、作者名、研究名義、Maintainer表示名、研究主体名に次を使用する。

```text
Nazuna Research
```

承認済み例外はない。

## 2. Exception Authority

別の第一者識別子を使用する必要性は、設計者役Taskだけが判断できる。

他の担当Taskは独自判断で例外を作らず、実値をDocsへ書く前にEscalateする。

## 3. Fixed Mapping

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
Project Internal Name        : Nazuna Research Governance LLM
GitHub Organization          : margpa-labs
Public Repository            : https://github.com/margpa-labs/margpa-runtime-llm
```

## 4. Machine-safe Form

Spaceを使えない技術識別子に限り、`Nazuna Research`のMachine-safe Slugとして次を使用できる。

```text
nazuna-research
```

## 5. Commit Attribution

Commitから個人GitHub Accountへ辿れることは許容する。ただし、Commit Author Nameは`Nazuna Research`とし、Account Handleや個人EmailをDocsへ追加しない。

## 6. Access Boundary

```text
GitHub Source／Docs
  → 閲覧・評価限定のSource-available公開

Lightning Public UI
  → 公開された通常機能を自由に操作・評価可能
```

## 7. Prohibition

- 廃止済み第一者名義をHistorical Docsへ再挿入しない。
- 移行説明、検索例、禁止例にも実値を記録しない。
- Root Metadata、CITATION、NOTICE、READMEで別名義を作らない。
- Git設定変更はPhase 1-ex専用Handoff前に行わない。

## 8. Canonical Detail

- [公開名義・名称の統一決定](../requirements/public_identity_and_naming_decision_20260721112925.md)
- [公開識別子・個人情報取扱方針](../requirements/public_identity_and_personal_information_policy_20260721111659.md)
- [Phase 1-ex 公開名義・Access・License要件予約](../requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md)

