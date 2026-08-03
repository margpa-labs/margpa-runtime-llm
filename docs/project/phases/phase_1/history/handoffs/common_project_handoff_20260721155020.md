# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-21 15:50:20 JST
supersedes: common_project_handoff_20260720231036.md
project_root: margpa-runtime-llm/
public_identity: Nazuna Research
current_design_role: 設計者役
future_design_role: 設計統括者役（Phase 1-exで変更予定）
```

## 1. Current State

```text
Phase 1-A～1-F Repository／Mac          : Accepted
Phase 1-F Lightning Native             : Deferred
Phase 1-G Cross-thread Follow-up        : Implementer Report Received／Review Pending
Phase 1-H                              : Waiting Phase 1-G Acceptance
Phase 1 Completion／Backup             : Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Current Role                           : 設計者役
Git                                    : Not Initialized
Current Docs Rule                      : Append-only／Timestamp
```

## 2. Phase 1-ex Complete Reservation

- 現設計者役を設計統括者役へ変更
- Phase別設計者役を配置可能にする
- 設計統括者、設計者、実装者、対外Docs役のAuthority再整理
- Git運用へ移行
- Docs DirectoryをInventory、Plan、Rollback付きでMigration
- Phase単位Lossless Compilation
- Public Identity、License、CITATION、NOTICE、Access境界
- Backup、Commit、Tag、GitHubを同一Snapshotへ対応
- 移行後に全担当Taskへ新構造とEntry Pointを通知

Phase 1-ex開始指示までは実行しない。

## 3. Stable Canonical Docs

Phase 1-exで次を作成する。

```text
docs/requirements_specification_ja.md
docs/system_architecture_ja.md
docs/technology_selection_ja.md
docs/basic_design_ja.md
docs/runtime_governance_specification_ja.md
```

- File名は英語
- 本文は日本語
- Git移行後のStable Filename
- 対外向け説明と技術正本を兼ねる
- 詳細設計書は必須にせず、将来必要箇所だけ追加

## 4. Project Continuity Master

```text
docs/project_continuity/project_continuity_master_ja.md
```

公開可能な継続正本とし、Project全体、Current State、Decision、Authority、Known Issue、Next Gate、Source Mapを、新Taskが即時再開できる粒度で統合する。

```text
public_export : true
github_public : include
```

Secret、個人Path、Credential、実会話Log等は含めない。

## 5. Public Files

```text
README.md
LICENSE
CITATION.cff
NOTICE.md
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
docs/public/phases/phase_<id>_summary_ja.md
```

READMEは日本語敬語＋末尾English Abstract。LICENSEは英語可。NOTICEは日本語／英語。その他Docs本文は日本語とする。

## 6. Phase 10 Original R&D

本体完成後、別Project／別Taskから次を疎結合統合するHookを予約する。

### 例外認識型安全統治機構

```text
研究領域：AI Safety Governance
```

内部安全傾向、周辺安全制御、入力文脈、生成過程等の相互作用と、例外を含む複合安全挙動を扱う。

### 分散証跡型例外認識エージェント統治安全機構

```text
研究領域：Multi-Agent Governance,
          Distributed Accountability,
          and Safety Assurance
```

複数主体間の責任、委譲、例外、改竄耐性付き証跡、全体整合、異常時の安全側制御を扱う。

公開Roadmapは名称、研究領域、1から2行概要だけとする。Project Continuity Masterには作業概念と統合Hookをもう少し詳しく記載する。Algorithm／核心は現在記載しない。

## 7. Generic Integration Rule

- External Governance Provider Port
- Capability Declaration
- Event／Evidence Reference
- Standard Governance Result
- `off／observe／enforce`
- Coreへ固有依存を入れない
- Providerなしで本体動作
- 存在しない権限を生成しない

## 8. Current Entry Points

- [最新Documentation Index](../documentation_index_20260721155020.md)
- [Phase 1-ex総合要件](../requirements/phase_1_ex_complete_operating_model_and_documentation_requirements_20260721155020.md)
- [Phase 1-ex Architecture](../architecture/phase_1_ex_documentation_continuity_and_publication_architecture_20260721155020.md)
- [ADR-0018](../adr/adr_0018_phase_1_ex_canonical_docs_continuity_and_future_r_and_d_20260721155020.md)
- [Phase 10 R&D Hook](../governance/phase_10_original_r_and_d_governance_extension_hooks_20260721155020.md)
- [Current Roadmap](../architecture/implementation_roadmap_20260721155020.md)

## 9. Immediate Next Gate

Phase 1-exとPhase 10へ移らず、Phase 1-G Cross-thread Follow-upの設計者Final Reviewを行う。

## 10. Authorization Boundary

本Handoffは、Role変更、Git操作、Docs Migration、Stable Docs生成、Backup、GitHub公開、Phase 10実装を許可しない。
