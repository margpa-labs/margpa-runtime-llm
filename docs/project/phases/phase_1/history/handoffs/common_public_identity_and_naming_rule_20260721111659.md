# MARGPA Runtime LLM 共通公開名義・名称規則

```yaml
document_state: current
created_at: 2026-07-21 11:16:59 JST
supersedes: none
applies_to: all_tasks
public_author_name: Nazuna Research
repository_owner: margpa-labs
public_repository: margpa-labs/margpa-runtime-llm
```

## 1. Mandatory Common Rule

今後、設計者役、設計統括者役、Phase設計者役、実装者役、対外Docs役、その他の担当Taskは、第一者の作者名、研究名義、Maintainer表示名、研究主体名として、原則次を使用する。

```text
Nazuna Research
```

廃止済み第一者名義を一般的な表示名やProject通称へ新規使用しない。

## 2. Required Exceptions

第一者名義を`Nazuna Research`以外にする必要性は、設計者役Taskだけが判断できる。

- GitHub Account Handleを正確に示す必要がある。
- GitHub noreply Commit Email等の技術識別子へ含まれる。
- 既存Artifact／History／Provenanceを正確に参照する。
- 旧名義を検索・分類・移行する規則内で例示する。
- 変更不能な外部識別子である。

例外か不明な場合は自動置換せず、設計者役またはユーザーへ確認する。

## 3. Fixed Mapping

```text
Public Author／Research Name : Nazuna Research
Commit Author Name           : Nazuna Research
GitHub Organization          : margpa-labs
Public Repository            : https://github.com/margpa-labs/margpa-runtime-llm
```

Repository OwnerとAuthor Nameを混同しない。

## 4. Commit Attribution

Commitから個人GitHub Accountへ辿れることは許容されている。

ただし、次を守る。

- Commit Author Nameは`Nazuna Research`とする。
- 個人の実Emailを不要に公開しない。
- Commit Email／GitHub Account帰属は技術識別子として別管理する。
- Git設定変更はPhase 1-exの専用Handoff前に行わない。

## 5. Access Boundary

```text
GitHub Source／Docs
  → 閲覧・評価限定のSource-available公開
  → 追加利用はLicenseで制限

Lightning Public UI
  → 公開されたUI機能は自由に操作・評価可能
  → Source再利用権や管理権限は付与しない
```

## 6. Current Execution Boundary

本書は今後の表記規則を即時適用する。

既存Docs／Sourceの全件置換、Git設定、Public Export、LICENSE／NOTICE／CITATION生成、GitHub PushはPhase 1-exまで実行しない。

## 7. Canonical Detail

詳細は次を参照する。

- [公開識別子・個人情報取扱方針](../requirements/public_identity_and_personal_information_policy_20260721111659.md)
- [Phase 1-ex 公開名義・Access・License要件予約](../requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md)
