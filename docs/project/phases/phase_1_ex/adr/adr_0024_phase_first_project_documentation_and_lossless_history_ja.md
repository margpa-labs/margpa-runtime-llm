# ADR-0024 Phase-first Project Documentation／Lossless History

- 文書ID: `adr_0024_phase_first_project_documentation_and_lossless_history`
- 状態: `accepted`
- 作成日時: `2026-07-26 14:54:51 JST`
- 更新日時: `2026-07-26 14:54:51 JST`
- Snapshot: `20260726145451`
- 作成担当: 設計統括者役
- 対象Phase: Phase 1-ex
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../architecture/target_documentation_structure_ja.md)
- Migration Requirements: [phase_1_ex_documentation_migration_and_canonical_content_requirements_20260726145451.md](../requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- Role Transition: [design_governance_role_transition_20260726145451.md](../history/operations/design_governance_role_transition_20260726145451.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Context

Phase 1完了時点の`docs/`は次の状態である。

```text
Total Docs                  : 309
Timestamped Docs            : 308
ADR                         : 26
Architecture                : 45
Governance                  : 5
Handoffs                    : 99
Operations                  : 11
Requirements                : 38
User Manual                 : 7
Documentation Index         : 76
Public                      : 3
```

Timestamp付きAppend-only方式はGit開始前の追跡性を確保した。一方、Current文書、人が読むPhase成果、Task引継ぎ、簡易RAGおよびGit履歴を考えると、Current／Compiled／History／Publicの境界を明確にする必要がある。

## 2. Decision

`docs/`を次の最上位境界へ再編する。

```text
docs/
├─ project/
│  ├─ current/
│  ├─ phases/
│  └─ shared/
└─ public/
```

`project/`は公開Repository内のProject技術正本、Phase成果、Task Evidenceおよび運用規則を格納する。

`public/`は対外説明用に編集された文書を格納する。

`internal/`という名称は、非公開情報を含むと誤解されるため使用しない。`project/`内も公開Repositoryへ含められることを前提とする。

## 3. Phase-first

Phase成果はCategory-firstではなくPhase-firstとする。

```text
採用:
docs/project/phases/phase_1/adr/

不採用:
docs/project/adr/phase_1/
```

理由：

- Phase単位のBackup、Review、HandoffおよびFreezeと一致する。
- Phase別設計者役が対象Phaseだけを読みやすい。
- 簡易RAGの対象をPhase単位で限定できる。
- Phase単位のLossless Compilationを一か所から解決できる。
- Cross-categoryのPhase Statusを`phase_index_ja.md`から辿れる。
- 将来のPhaseごとのGit Tag／Releaseと対応しやすい。

## 4. Lossless History

旧Granular Docsの`history/`はCategory内部へ分散せず、Phase直下に旧Treeを保持する。

```text
docs/project/phases/phase_1/
├─ adr/
│  └─ phase_1_adr_ja.md
├─ architecture/
│  └─ phase_1_architecture_ja.md
└─ history/
   ├─ adr/
   ├─ architecture/
   ├─ governance/
   ├─ handoffs/
   ├─ operations/
   ├─ requirements/
   ├─ user_manual/
   └─ documentation_index_*.md
```

旧TreeをPhase `history/`配下へまとめて移すことで、既存の相対Linkを可能な限り保持する。

例：

```text
Before:
docs/adr/example.md
  → ../requirements/requirement.md

After:
docs/project/phases/phase_1/history/adr/example.md
  → ../requirements/requirement.md
```

`history/adr/../requirements/`として同じ関係が維持される。

Category内部へ個別`history/`を置く案は、旧相対Linkを破壊しやすいため採用しない。

## 5. Filename Policy after Git

### 5.1 Timestampなし

- `docs/project/current/`のCurrent Canonical Docs
- Phase単位Lossless Compilation
- `docs/public/`のCurrent Public Docs
- Phase Index

例：

```text
requirements_specification_ja.md
system_architecture_ja.md
phase_1_adr_ja.md
phase_index_ja.md
roadmap_ja.md
```

変更履歴はGitで保持する。

### 5.2 Timestamp維持

- Git開始前に作成されたGranular Docs
- Immutable Handoff／Status／Review／Audit Event
- 旧Documentation Index

これらは元File名を変えずPhase `history/`へ移す。

### 5.3 Public History

PublicのMilestone SnapshotはTimestampではなくPhase／Release識別子を使用する。

```text
docs/public/history/roadmap_phase_1_ja.md
docs/public/history/overview_phase_1_ja.md
```

`docs/public/history/phase_1/`までは作らない。

## 6. Current／Phase／Public

```text
project/current
  → Project横断の最新技術正本

project/phases/phase_<id>
  → Phase単位のFreeze可能な成果とEvidence

project/shared
  → Phase非依存のConvention、Role、Schema、Template

public
  → 対外向けに編集された概要、Concept、Roadmap
```

Current Canonical DocsとPublic Docsは同一ではない。両方とも公開Repositoryへ含められるが、読者と詳細度が異なる。

## 7. RAG Default Scope

Default：

```text
docs/public/
docs/project/current/
docs/project/phases/<selected_phase>/*/*_ja.md
```

Default除外：

```text
**/history/**
```

Historyは研究、監査または明示的Historical Retrieval Modeでだけ検索対象にする。

PathだけでなくDocument Metadataに`phase`、`status`、`audience`、`canonical`、`rag_default`および`source_documents`を持たせる。

## 8. Phase Freeze

Phase Compilationは対象Phase Acceptance後にFreezeする。

Freeze後に誤りが判明した場合、黙って書き換えず次のいずれかを使用する。

- Amendment
- Correction Record
- 次PhaseのCurrent Canonical更新
- Git Commit上の明示的Correction

具体規則はGit運用設計で確定する。

## 9. Role Decision

Phase 1-ex開始時点で、現在のTaskを「設計者役」から「設計統括者役」へ変更する。

Phase 1-ex専用設計者役は作らない。設計統括者役がPhase 1-exの設計実務を直接担当する。

Phase 2以降は、設計統括者役の下にPhase別設計者役を配置可能にする。

## 10. Consequences

- Currentを探すために最新Timestampを比較する必要がなくなる。
- Phase単位のTask再開、RAG、ReviewおよびBackupが容易になる。
- 旧Evidenceは削除せず保持される。
- PublicとProject技術正本が混在しない。
- Migration前に全File ClassificationとLink検証が必要になる。
- CurrentからHistoryへの重複RetrievalをRAG側で防ぐ必要がある。

## 11. Authorization Boundary

本ADRはTarget構造をAcceptedとするが、Directory作成、Move、Rename、Delete、Link変更またはGit操作を単独では許可しない。

Migration Manifest、Rollback Planおよびユーザー確認後に実移行する。
