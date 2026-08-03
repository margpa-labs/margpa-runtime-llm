# Phase Index Append-only History Repair

```yaml
document_id: phase_index_append_only_history_repair
phase: phase_1_ex
status: completed_verified
language: ja
created_at: 2026-07-26 20:29:35 JST
owner: 設計統括者役
```

## 1. Incident

`docs/project/phases/phase_1_ex/phase_index_ja.md`をStable入口として更新した際、対応するTimestamp付きIndex Snapshotを毎回追加しなかった。

Stable Indexの最新版自体は維持されていたが、`history/documentation_index_20260726150349.md`以降のIndex開発ログが欠落した。

## 2. Cause

「Stable FilenameをGit Historyで更新する」という将来運用を、Git未開始時点にも先行適用し、「Git開始前は別Documentへ変更記録を残す」規則と、ProjectのAppend-only開発ログ方針をIndex更新へ厳密適用しなかった。

## 3. Repair Sources

```text
20260726154009:
  margpa-runtime-llm_重複docs削除前_20260726.zip

20260726170034:
  margpa-runtime-llm_docs構造_権限構造再整理後_20260726.zip

20260726175318以降:
  Stable Index内容
  Tool Patch記録
  作成済みADR／Requirements／Architecture／Handoff／Review
  Manifest生成時刻
```

## 4. Reconstructed Snapshots

次をAppend-onlyで追加した。

```text
documentation_index_20260726154009.md
documentation_index_20260726170034.md
documentation_index_20260726175318.md
documentation_index_20260726180711.md
documentation_index_20260726192912.md
documentation_index_20260726194949.md
documentation_index_20260726202036.md
documentation_index_20260726202935.md
```

最初の2件はBackup内の実物を基準とし、History配置に必要な相対LinkだけをRebaseした。

以降は記録済みPatch順序から各時点の論理状態を復元した。推測で新しい要件を加えていない。

## 5. Preventive Rule

- Stable Index更新とTimestamp Snapshot追加を必ず同じ作業単位で行う。
- Review／Handoff／Status追加時もIndex Snapshotを作る。
- Git開始後もIndex Snapshotを省略しない。
- 旧Snapshotは編集しない。
- IndexとReviewを同時作成する既存運用を維持する。

## 6. Scope

本Repairは欠落したIndex開発ログの復元と運用規則の明確化だけを行う。既存History、Handoff、Review、Requirements、Architectureまたは実装内容を変更しない。
