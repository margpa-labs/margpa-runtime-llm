# Append-only／User Authority Governance Freeze

```yaml
document_id: append_only_and_user_authority_governance_freeze
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-26 20:39:48 JST
owner: 設計統括者役
authorization: user_explicit_instruction
git_operation_performed: false
```

## 1. 目的

本Recordは、Docs履歴保持、Git未決定状態および運用変更Authorityに関するユーザーの明示指示を、Project共通Governanceとして固定する。

本変更は、設計統括者役がStable Phase Indexを更新しながら対応するAppend-only Index Snapshotを作成しなかった事象を受けた再発防止である。ユーザーの許可なく既存運用を変更したことはGovernance Deviationであり、設計統括者役の役職またはWrite Scopeによって正当化されない。

## 2. 固定した規則

### 2.1 Git

- Git運用は未決定である。
- Git初期化、Commit、Branch、Tag、Remote、Push、公開Repository投入および履歴加工は、ユーザーがGit運用設計と実行操作を明示承認するまで行わない。
- 将来Gitを採用しても、Git HistoryはAppend-only Development Log、Timestamp Snapshot、Raw Phase History、Phase BackupおよびLossless Compilation Sourceの代替ではない。

### 2.2 Append-only Development Log

- 作成済みのAppend-only Development Logを全て保持する。
- Handoff、Status、Review、Evidence、Decision、Index SnapshotおよびRaw Sourceを、役目終了、重複、Stable反映済みまたはGit採用を理由に削除、上書き、統合、圧縮、置換または退役しない。
- Stable文書を更新する場合も、変更前原文と変更後原文をTimestamp付きHistoryとして保存する。
- Phase単位Lossless Compilationは、当該Phaseの全Append-only Development LogをSourceとする。
- Rollback、各時点の再現、Task再作成および後続再整理に必要な状態を失わせない。

### 2.3 User Authority

- User Explicit InstructionをProject内の最上位Authorityとする。
- 設計統括者役を含む全担当は、ユーザー承認済み運用を独断で変更できない。
- Docs構造、Append-only保持、命名、Role Authority、Git方針、正本境界、公開境界、削除・退役条件およびTask間伝達方式を、ユーザーの明示許可なく変更することを禁止する。
- 変更が必要な場合は、変更案、影響分析、保持・Rollback計画、ユーザー明示承認、実施、検証、Append-only変更Recordの順で行う。
- Authorityまたは指示が曖昧・競合する場合は、現行運用を維持して停止し、ユーザーへ確認する。
- 無許可変更はGovernance Deviationとして記録し、追加変更を停止して影響と復旧方法を報告する。

## 3. 変更前後の原文Snapshot

### 3.1 Documentation Rules

変更前：

- [Exact Before Snapshot](documentation_rules_before_user_authority_freeze_20260726203948.md)
- SHA-512：`f257a133ffbeb5878ba5540b3b6a4bab1d48c6d925008f9872ca8a6e3e6e4675c26248e68c6671d27a505d865b2dfc8171df0b35826bc4ab249224a1a9d64cb9`

変更後：

- [Exact After Snapshot](documentation_rules_after_user_authority_freeze_20260726203948.md)
- SHA-512：`ddd3639e72b895b090fde3b70eb0d637abb0734ef5eb6bc0ae769d16e53956f55850ea72b92a99d8976635281b9aeda89ba84093583cf6ded10b098274659b6c`
- Stable Target：[Documentation Rules](../../../../shared/conventions/documentation_rules_ja.md)

### 3.2 Documentation Structure／Task Operations

変更前：

- [Exact Before Snapshot](documentation_structure_and_task_operations_before_user_authority_freeze_20260726203948.md)
- SHA-512：`ddee72594385920ff57dd55bc111eaf83612651a8d022eb7e8e95b3524bbeac8d9aae28179558167e413652c9cd8dcd9027f8f934fec7653ba8b671d0cd8ba7c`

変更後：

- [Exact After Snapshot](documentation_structure_and_task_operations_after_user_authority_freeze_20260726203948.md)
- SHA-512：`863c0719c643de035fa43f281f74396df4e28305a15f142a02fd1f7da9f956d481b12298e90861f2043467d08c21001e61ef76b73b795d52cd12c663c196e740`
- Stable Target：[Documentation Structure／Task Operations](../../../../shared/operations/documentation_structure_and_task_operations_ja.md)

SnapshotはStable文書の原文をByte単位でCopyしたものであり、Snapshot配置に合わせたLink書換えは行っていない。Snapshot内の相対Linkは元Stable Pathを基準とする。

### 3.3 Phase 1-ex Index

変更前：

- [Before Snapshot](phase_index_before_user_authority_freeze_20260726203948.md)
- SHA-512：`ce7e442b0627f98d0f28015ad07b1aff58d31e8b82ab2780c597ab943c849e8184a005c0033cca7d7a4be0b8bc74f7454b6475d39b786976c892b7efaf534287`
- 復元方法：変更後原文へ、本作業で追加した既知Deltaだけを逆適用して変更直前状態を復元した。
- 復元忠実度：`exact_by_known_reverse_patch`

変更後：

- [Exact After Snapshot](phase_index_after_user_authority_freeze_20260726203948.md)
- SHA-512：`5b8de80ed60cf986c4b43fd848c757e875d2d467eb1261e10f26fe66dea53ad5b730cf9ae41e173109b24702989151697bd7d4dba1880b2d8007d0b35c9bc458`
- Stable Target：[Phase 1-ex Index](../../phase_index_ja.md)

Phase Indexの変更前Snapshotは作業着手時の直接Copyではない。この点を隠さず、復元方法を上記のとおり記録する。以後はStable文書編集前に必ず直接Copyを作成する。

### 3.4 Task Role／Write Authority Policy

変更前：

- [Exact Before Snapshot](task_role_write_authority_policy_before_user_authority_freeze_20260726203948.md)
- SHA-512：`affbf3727bf21ae9375c8fcd5db14a7834f42ecaa09bf7e3ce053913a92dd8e6c951fe98a122255a2092f9fda4144677287d5caf9a00992e2a0d4fd5a6fa2b8d`

変更後：

- [Exact After Snapshot](task_role_write_authority_policy_after_user_authority_freeze_20260726203948.md)
- SHA-512：`5a09854e7a32e41cb1684ffd514e780714ad3556d5c8540a2bd20231626e0e2537d781c8bb78dc941f3402c17cad15a528cbb9c3d43cdfe1d04ff54d74820158`
- Stable Target：[Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)

### 3.5 Requirements Specification

変更前：

- [Exact Before Snapshot](requirements_specification_before_user_authority_freeze_20260726203948.md)
- SHA-512：`c2678e3cb7b0926352217f154f38f9c4e6f3525c34a79e81aad112ffa9d270ff2b85bb15273edadd0f2c9d2bc07df813f03d413693b58f1e6edfa12f541aeae5`

変更後：

- [Exact After Snapshot](requirements_specification_after_user_authority_freeze_20260726203948.md)
- SHA-512：`a4b334618f089472c701a0fbb112ce03a52f49599be36df0aa55bae8db2a1f17e6313a8d985b9e7b9f3319435bac084bd0644bddf0b01a8e5a5cb29b1bbc975e`
- Stable Target：[Requirements Specification](../../../../current/requirements/requirements_specification_ja.md)

上記2文書は、検証で発見した「Stable／CurrentはGit Historyで更新する」という現行の矛盾文言だけを、ユーザーの明示指示へ整合させた。その他の要件またはRole Scopeは変更していない。

## 4. 実施境界

本作業で行ったこと：

- 共通ルールへの明文化
- 運用ルールへの明文化
- 現行Role PolicyおよびRequirements内の矛盾文言の整合
- 変更前後の原文Snapshot保存
- 本Governance Record作成
- Phase IndexとAppend-only Index Snapshotの更新

本作業で行っていないこと：

- Git初期化またはGit操作
- 既存Development Logの削除、上書き、統合または退役
- Docs Directory構造変更
- RoleのWrite Scope変更
- Public／Private境界変更
- Source Code、Test、ConfigまたはScript変更

## 5. 今後の完了条件

運用変更を含む作業は、次を全て満たすまで完了扱いにしない。

1. 既存運用と変更対象を明示する。
2. 影響とRollback方法を提示する。
3. ユーザーの明示承認を得る。
4. 変更前後の原文とEvidenceをAppend-onlyで残す。
5. Stable Indexと同一TimestampのIndex Snapshotを作る。
6. Link、Hashおよび保持件数を検証する。
