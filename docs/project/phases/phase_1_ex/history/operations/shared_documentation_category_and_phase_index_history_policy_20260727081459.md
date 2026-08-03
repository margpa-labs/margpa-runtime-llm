# Shared Documentation Category／Phase Index History Policy Record

```yaml
document_id: shared_documentation_category_and_phase_index_history_policy
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-27 08:14:59 JST
owner: 設計統括者役
user_authorized: true
git_operation: none
deletion: none
```

## 1. 確定内容

### Shared任意Category

次は必要な場合だけ使用する。

```text
docs/project/shared/schemas/
docs/project/shared/templates/
docs/project/shared/user_manual/
```

不要な場合は使わなくてよい。Directoryの存在だけを理由にArtifact作成を強制しない。使用した場合は対応する`shared/history/<category>/`へ変更前後Snapshotを保存する。

### Docs運用専用Category

既存の次を使用する。

```text
docs/project/shared/operations/
docs/project/shared/history/operations/
```

新しい重複Directoryは作らない。純粋な命名、言語、Immutable性等は既存`shared/conventions/`を正本とし、Operationsから参照する。

### 権限管理専用Category

既存の次を使用する。

```text
docs/project/shared/task_roles/
docs/project/shared/history/task_roles/
```

Role、Write Authority、Read-only Boundary、EscalationおよびTask間責務を集約する。意味が重複するAuthority用Directoryは追加しない。

## 2. Public Stable／History Filename

最新版はTimestampなしのStable Filenameを維持する。

```text
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
```

`<phase>_<language>_YYYYMMDDHHMMSS`を付けるのはHistoryへ移す変更前後完全Snapshotだけである。

```text
overview_<phase>_<language>_YYYYMMDDHHMMSS.md
concept_<phase>_<language>_YYYYMMDDHHMMSS.md
roadmap_<phase>_<language>_YYYYMMDDHHMMSS.md
```

## 3. Roadmap更新

Roadmapは固定計画表ではなく、Projectの現在状態と増加した要件を累積反映する。

毎回更新する対象：

- 現在の進捗
- 完了済み／進行中／未着手／保留／再評価待ち
- Active Phase／Next Phase
- Phase Gate／Backup／公開／Git状態
- 新規要件
- 既存要件の変更、優先順位、移動先
- 将来研究機能／External R&D Hook
- Known Limitation／Dependency／留意事項

新規要件を漏らさない。後続Phaseへ移した要件は削除せず、状態と移動先を示す。

## 4. Phase 2以降のHistory Index予約

Phase 2開始時から次を使用する。

```text
docs/project/phases/<phase>/
├─ phase_index_ja.md
├─ index/
│  └─ Phase Lossless Compilation等
└─ history/
   └─ index/
      └─ documentation_index_YYYYMMDDHHMMSS.md
```

- `phase_index_ja.md`：Timestampなしの最新Stable入口
- `index/`：Phase Lossless Compilation等
- `history/index/`：Append-only Documentation Index Snapshot

本予約を理由にPhase 1／Phase 1-exのRaw Indexを遡及移動しない。既存配置変更には別途ユーザー承認、Migration Plan、Link検証およびRollback Planを必要とする。

## 5. Snapshot／SHA-512

### Documentation Rules

```text
Before:
docs/project/shared/history/conventions/
documentation_rules_phase_1_ex_ja_20260727081459.md

SHA-512:
a4ae20e9e7b225c4e0df8ce34cadc34b668e5c18c0620d10738f9c55edffa59e31f980a4e0e4a6bc9716ab7460a4194ab721e88b89846a6953df3cda54f87337

After:
docs/project/shared/history/conventions/
documentation_rules_phase_1_ex_ja_20260727082448.md

SHA-512:
6eb978db4035b0f27cafe64fab5a1f43426d63988a844e58988f34eea48fabefd56b33f1c19faa5e09371e1454a99ecdfe3182d5f6f7d0384125f560044420de
```

### Documentation Structure／Task Operations

```text
Before:
docs/project/shared/history/operations/
documentation_structure_and_task_operations_phase_1_ex_ja_20260727081459.md

SHA-512:
303c077a97ae671a1b08a4b51944b633e46cdb99f448811ae32a1c9e115a668d2e47752ea53fc349c8ab9a82e0822962e68947b854fc63d149a72a2d6c4fd10d

After:
docs/project/shared/history/operations/
documentation_structure_and_task_operations_phase_1_ex_ja_20260727082448.md

SHA-512:
1d6ccc365ed398aabc3ab17ec5a10337f4f7964a3b16389e09b10a238b408d98034c358069c71bbf415ce8f81cea01f92ae19e6e4b4c33bee6e1c326b09cd506
```

### Phase Index

```text
Before:
docs/project/phases/phase_1_ex/history/operations/
phase_index_before_shared_documentation_category_and_phase_index_history_policy_20260727081459.md

SHA-512:
ac115a250bdd534f792c544d90eb33d26606077047320ad120fe5fd3518a193a149fb37e8d1b48fe4ea671ac92aa7a2cf18f0e35f936aa12537955cd336b70a5

After:
docs/project/phases/phase_1_ex/history/operations/
phase_index_after_shared_documentation_category_and_phase_index_history_policy_20260727081459.md

SHA-512:
80d1ffc951d12b72234d6fc6f8650c4696998663588feffb2522702bf0b726a2eec62af9d6278c19a4a882f605d17c39767827c6144544a658e48ba1207d01dd
```

各Snapshotは対応Stable原文と完全一致を確認した。

## 6. 非実施事項

- 新しい重複Categoryの作成
- `schemas/`、`templates/`、`user_manual/`へのDummy Artifact作成
- Phase 1／Phase 1-ex Raw Indexの移動
- Public Stable Filenameの変更
- Git操作
- History削除または上書き

