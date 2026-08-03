# Current／Shared／Public Stable Historyおよび設計統括者役完全復元 運用確定Record

```yaml
document_id: stable_document_history_and_design_governance_recovery_policy
phase: phase_1_ex
status: accepted_applied
language: ja
created_at: 2026-07-27 07:17:21 JST
owner: 設計統括者役
authority: user_explicit_instruction
supersedes: null
```

## 1. Decision

ユーザーの明示指示により、次の運用を共通ルールとして追加した。

1. `docs/project/current/history/`をCurrent Stable文書の変更前後原文Snapshot置場とする。
2. `docs/project/shared/history/`をShared Stable文書の変更前後原文Snapshot置場とする。
3. `docs/public/history/`をPublic Stable文書の変更前後原文Snapshot置場とする。
4. Roadmap Historyは`docs/public/history/roadmap/`へ置く。
5. Stable文書を変更する前に、現在の原文をTimestamp付きで完全コピーし、SHA-512一致を確認する。
6. Stable文書更新後も、更新後原文を別Timestampで完全コピーする。
7. 同じPhase内で同一文書を複数回更新しても、Timestampで全版を識別する。
8. 各Phase完了後、Phase Backup直前に設計統括者役の完全復元PackageとReconstruction Validationを作成する。

## 2. Filename

```text
<stable_document_stem>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

例：

```text
basic_design_phase_1_ex_ja_20260727071234.md
documentation_rules_phase_1_ex_ja_20260727071234.md
roadmap_phase_1_ex_ja_20260727071234.md
```

Public、Current、SharedのStable Filename自体にはTimestampを付けず、最新版入口として維持する。

## 3. Directory Mapping

```text
docs/project/current/requirements/
  → docs/project/current/history/requirements/

docs/project/current/architecture/
  → docs/project/current/history/architecture/

docs/project/current/governance/
  → docs/project/current/history/governance/

docs/project/current/project_continuity/
  → docs/project/current/history/project_continuity/

docs/project/shared/conventions/
  → docs/project/shared/history/conventions/

docs/project/shared/operations/
  → docs/project/shared/history/operations/

docs/project/shared/task_roles/
  → docs/project/shared/history/task_roles/

docs/public/roadmap_ja.md
  → docs/public/history/roadmap/
```

Current／Sharedで将来Categoryが増える場合も、原則としてHistory側へ同じ相対Categoryを作る。

## 4. Stable Update Sequence

```text
Owner／Active Phase／Language確定
  → 更新前Stable原文Snapshot
  → 更新前SHA-512一致確認
  → Snapshotと関連DocsからStableを再構築
  → Stable更新
  → 更新後Stable原文Snapshot
  → 更新後SHA-512一致確認
  → Active Phase変更Record
  → Phase Index更新
  → Append-only Documentation Index Snapshot
```

更新前Snapshotなしの丸ごと上書きを禁止する。History Snapshotは原文を要約、再解釈、整形またはLink修正せず保存する。

## 5. Existing Public Roadmap History

次はTimestamp規則導入前の既存History原本である。

```text
docs/public/history/roadmap/roadmap_phase_1_ja.md
```

本Fileは改名、上書き、置換または削除しない。以後のRoadmap Snapshotだけを次の形式にする。

```text
roadmap_<phase>_<language>_YYYYMMDDHHMMSS.md
```

## 6. Design Governance Complete Recovery

原則として各Phase完了後、Phase Backupを取得する直前に行う。

```text
Phase完了・次Phase移行可能宣言
  → Current／Shared／Project Continuity Refresh
  → Stable変更前後History Snapshot
  → Design Governance Recovery Manifest
  → Docs-only Reconstruction Validation
  → Phase Backup
```

Recovery Manifest：

```text
docs/project/phases/<phase>/history/operations/
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

新しい設計統括者役Taskは、旧Taskの会話記憶を使用せず、Docsだけから次を復元できなければならない。

- Project Identityと目的
- Current／Completed／Next Phase
- Accepted Requirements／Architecture／ADR／Governance
- 実装済み機能とTest
- Open Finding、未決事項、保留理由
- Role AuthorityとWrite Scope
- Docs運用とHistory規則
- External Service状態とユーザー担当操作
- Backup／Git／GitHub／Public Demo／License状態
- 主要Artifact Path、Version、SHA-512
- 次に行う安全な作業

設計統括者役を完全復元できれば、その設計統括者役からPhase別設計者役、実装者役および対外Docs役を再構成できる状態を完了条件とする。

## 7. First Applied Stable Documents

今回の運用追加では、次の4文書で更新前後Snapshotを作成した。

### 7.1 Documentation Rules

```text
Stable:
  docs/project/shared/conventions/documentation_rules_ja.md

Before:
  docs/project/shared/history/conventions/
  documentation_rules_phase_1_ex_ja_20260727071234.md

Before SHA-512:
  ddd3639e72b895b090fde3b70eb0d637abb0734ef5eb6bc0ae769d16e53956f55850ea72b92a99d8976635281b9aeda89ba84093583cf6ded10b098274659b6c

After:
  docs/project/shared/history/conventions/
  documentation_rules_phase_1_ex_ja_20260727071721.md

After SHA-512:
  7170c59e5296d62316ee0eaa10b70a6f38f6369d3047b7993527f3e44393fad87b097e92ef32452c866ee7ac766443d2436db57a49aa568cc9fcec1f2f0cb4fa
```

### 7.2 Documentation Structure／Task Operations

```text
Stable:
  docs/project/shared/operations/documentation_structure_and_task_operations_ja.md

Before:
  docs/project/shared/history/operations/
  documentation_structure_and_task_operations_phase_1_ex_ja_20260727071234.md

Before SHA-512:
  863c0719c643de035fa43f281f74396df4e28305a15f142a02fd1f7da9f956d481b12298e90861f2043467d08c21001e61ef76b73b795d52cd12c663c196e740

After:
  docs/project/shared/history/operations/
  documentation_structure_and_task_operations_phase_1_ex_ja_20260727071721.md

After SHA-512:
  464d5ff3ccab11743ade650b797f1e06476ac6db0e3991af0a9bb3cc6b72ee4c53c1cf27a8d6452c5415ed643f1158de1c94a9c4475ae005a6ed7ff63745810f
```

### 7.3 Task Role／Write Authority

```text
Stable:
  docs/project/shared/task_roles/task_role_write_authority_policy_ja.md

Before:
  docs/project/shared/history/task_roles/
  task_role_write_authority_policy_phase_1_ex_ja_20260727071234.md

Before SHA-512:
  5a09854e7a32e41cb1684ffd514e780714ad3556d5c8540a2bd20231626e0e2537d781c8bb78dc941f3402c17cad15a528cbb9c3d43cdfe1d04ff54d74820158

After:
  docs/project/shared/history/task_roles/
  task_role_write_authority_policy_phase_1_ex_ja_20260727071721.md

After SHA-512:
  2cc941383bf9dacc09958a53a25ef926c8a6757dccd09847d0807f3680ce866a7627daa60916b03bac642dfcc6fc08a1b909a12b7b8cbfbcd84198776827d0bc
```

### 7.4 Project Continuity Master

```text
Stable:
  docs/project/current/project_continuity/project_continuity_master_ja.md

Before:
  docs/project/current/history/project_continuity/
  project_continuity_master_phase_1_ex_ja_20260727071234.md

Before SHA-512:
  2e266ababfa3ae02644e6cefc4866ab4c5ae59bdf1341b78db20440e08c5609dbe715dc3ac00c0ff34b4f5a18b66243d82f3218fcd80b76221dce573c3b02e73

After:
  docs/project/current/history/project_continuity/
  project_continuity_master_phase_1_ex_ja_20260727071721.md

After SHA-512:
  62377162a4afc06ad2a16a4a02c0437b98834af7c4559427cf5384cc8da4b0f0005e3b95cf5f5c9e77b15d3074d15fd61980c5e96067db19544d8b4b91b4507d
```

## 8. Non-actions

- `docs/public/roadmap_ja.md`は今回変更していない。
- `docs/public/history/roadmap/roadmap_phase_1_ja.md`は変更していない。
- 既存Historyの改名、上書き、移動または削除は行っていない。
- Git操作は行っていない。
- Phase Backupは行っていない。
- Design Governance Recovery ManifestはPhase完了時に作成するため、今回は作成していない。
