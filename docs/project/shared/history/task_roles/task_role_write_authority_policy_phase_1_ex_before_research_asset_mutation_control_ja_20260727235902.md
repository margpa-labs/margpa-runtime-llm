# Task Role／Write Authority Policy

- 文書ID: `task_role_write_authority_policy`
- 状態: `current_effective`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-07-27 23:52:14 JST`
- Snapshot: `20260726150349`
- 作成担当: 設計統括者役
- Role Transition: [design_governance_role_transition_20260726145451.md](../../phases/phase_1_ex/history/operations/design_governance_role_transition_20260726145451.md)
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../../phases/phase_1_ex/architecture/target_documentation_structure_ja.md)
- Notification Plan: [documentation_migration_task_notification_plan_20260726150349.md](../../phases/phase_1_ex/handoffs/documentation_migration_task_notification_plan_ja.md)
- Shared Operations: [documentation_structure_and_task_operations_ja.md](../operations/documentation_structure_and_task_operations_ja.md)
- 正本言語: 日本語
- supersedes: `task_role_write_authority_policy_20260719142558.md`

## 1. Current Transition

```text
Current Task:
  設計統括者役
  兼 Phase 1-ex設計実務担当

Phase 1-ex専用設計者役:
  作成しない

Phase 2以降:
  Phase別設計者役を配置可能
```

Directory Migrationと旧Root重複配置の退役は完了した。Target Path AuthorityはCutover通知時点から有効である。旧Pathは存在を前提にせず、参照・書込とも禁止する。旧原文はPhase HistoryまたはPublic Historyから参照する。

## 2. 設計統括者役

### Standing Responsibilities

- Project全体Requirements
- Cross-Phase Architecture
- Shared Governance／Policy／Port
- Phase構成
- Current Canonical Docs
- Project Continuity Master
- Shared Convention／Schema／Template
- Role Authority
- Phase開始用上位Handoff
- Phase最終Review
- Cross-Phase Conflict
- Backup／Git／Release設計
- Current／Shared Stable History管理
- Phase完了時の設計統括者役完全復元Package
- Design Governance Reconstruction Validation

### Target Write Scope

```text
docs/project/current/
docs/project/current/history/
docs/project/shared/
docs/project/shared/history/
docs/project/shared/design_governance_handoff/
docs/project/shared/history/design_governance_handoff/
docs/project/phases/<active_phase>/phase_index_ja.md
docs/project/phases/<active_phase>/adr/ Cross-Phase ADR
docs/project/phases/<active_phase>/operations/ Designer Review／Migration
docs/project/phases/<active_phase>/history/handoffs/designer_*
```

Phase 1-exではPhase別設計者役を兼ねるため、Phase 1-ex配下のRequirements／Architecture／ADR／Operations／Handoffsへ書込可能とする。

### Phase Completion Recovery Responsibility

設計統括者役は、各Phase完了宣言後かつPhase Backup直前に、自身を新しいTaskへ完全移行できる状態をDocsで固定する責任を持つ。

最低限次を行う。

- Current Canonical／Current Index更新
- Project Continuity Master更新
- Shared Rules／Role Authorityの有効版確認
- 変更対象Stable文書の更新前後History Snapshot
- Completed Phase Compilation／Final Review／Acceptance固定
- Open Finding／未決事項／次Phase入口固定
- `design_governance_recovery_manifest_YYYYMMDDHHMMSS.md`作成
- Docsだけを用いたReconstruction Validation

Recovery Manifestは次へ追加する。

```text
docs/project/shared/history/design_governance_handoff/
```

設計統括者役さえ完全復元できれば、設計統括者役がCurrent／Shared／Phase HandoffからPhase別設計者役、実装者役および対外Docs役を再構成できる状態を完了条件とする。

会話Taskの記憶、旧Task固有Contextまたは暗黙知を必須Dependencyとして残さない。完全復元を確認できない場合、Phase Backupへ進めない。

## 3. Phase別設計者役

Phase 2以降に配置する。

### Write Scope

```text
docs/project/phases/<assigned_phase>/requirements/
docs/project/phases/<assigned_phase>/architecture/
docs/project/phases/<assigned_phase>/adr/
docs/project/phases/<assigned_phase>/operations/ Phase-local Design
docs/project/phases/<assigned_phase>/history/handoffs/designer_*
```

### Read-only

- `docs/project/current/`
- `docs/project/shared/`
- 他PhaseのFrozen Compilation
- `docs/public/`

Cross-Phase変更、Shared Port、Role Authority、Public IdentityまたはGlobal Governanceは設計統括者役へEscalateする。

## 4. 実装者役

### Source Write Scope

```text
src/
tests/
scripts/
```

Accepted Handoffとユーザー許可がある場合：

```text
config/
pyproject.toml
uv.lock
Root Metadata
```

### Docs Write Scope

```text
docs/project/phases/<active_phase>/history/handoffs/implementer_status_*
```

### Read-only

- Current Canonical Docs
- Shared Policy
- Requirements／Architecture／Governance／ADR
- Frozen Phase Compilation
- Public Docs

実装者役はCanonical RequirementsまたはArchitectureを直接変更しない。

## 5. 対外Docs役

### Write Scope

```text
README.md
LICENSE
NOTICE.md
CITATION.cff
docs/public/
docs/public/history/
docs/project/phases/<active_phase>/history/handoffs/external_docs_status_*
```

### Conditional Write

Lossless CompilationまたはCanonical Docsを作業として生成する場合、Source Meaning Ownerである設計統括者役のReviewを必要とする。

### Read-only

- Requirements
- Architecture
- Governance
- ADR
- Project Continuity Masterの技術内容

Public向けに読みやすくしても、正本の意味を変更しない。

## 6. History

Historyは原則Immutableである。

書込可能なのは新しいEvent Fileの追加だけとし、既存History Fileを編集しない。

Privacy／Credential／Secret Scrubは例外として、変更理由とScrub Recordを必要とする。

## 7. Current／Stable Docs

Stable Filenameは最新版への入口であり、Git Historyを前提にしない。Git運用は未決定であり、将来Gitを採用してもTimestamp付きAppend-only Development Logを全て保持する。

- Update前にOwnerを確認する。
- Material ChangeはReviewを必要とする。
- Phase Freeze済みCompilationを通常のCurrent文書として上書きしない。
- Stable文書の変更前原文と変更後原文をTimestamp付きHistoryへ保存する。
- Current／Shared／PublicのHistory Snapshotは`<stem>_<phase>_<language>_YYYYMMDDHHMMSS.md`形式で対応Categoryへ保存する。
- 更新前SnapshotとStable原文のSHA-512一致を確認してからStable文書を変更する。
- Stable更新後も別Timestampで更新後原文を保存し、Active Phaseの変更RecordとIndex Snapshotへ記録する。
- Git開始前後を問わず、変更記録、Index Snapshot、Raw HistoryおよびEvidenceを削除、上書き、統合、圧縮、置換または退役しない。

Write Authorityは、承認済み運用に従って担当範囲へ書き込める権限であり、ユーザー承認済み運用を変更する権限ではない。設計統括者役を含む全担当は、ユーザーの明示許可なくDocs構造、Append-only保持、命名、Role Authority、Git方針、正本境界、公開境界、削除・退役条件またはTask間伝達方式を変更してはならない。

## 8. Index Authority

```text
Project Current Index:
  設計統括者役

Phase Index:
  Phase別設計者役
  ＋設計統括者役のFinal Review

Public Index／README:
  対外Docs役
  ＋設計統括者役のTechnical Review
```

## 9. Migration Authority

Directory Migrationの実行は、Accepted Manifest、Rollback Planおよびユーザー許可を必要とする。

各担当TaskはMigration完了通知前に新Pathへ書き込まない。

## 10. External Action Boundary

GitHub Push、Cloud変更、Secret登録、Model Download、Dependency変更、Public Access変更または削除操作は、Directory Write Authorityから自動的に許可されない。

Project Root外に対する読取、走査、作成、Copy、変更、削除、Move、Rename、Archive、展開、Metadata操作、Permission操作、一時Artifact作成およびCommand実行も、Role Authority、Tool PermissionまたはFilesystem Permissionから自動的に許可されない。

全担当に対して次を強制する。

- 通常の作業対象を`margpa-runtime-llm/`内部に限定する。
- Project Root外へ触れる場合は、ユーザーが対象PathとActionを当該作業について明示許可していることを必須とする。
- Project外を指すSymbolic Linkを、ユーザーの明示許可なしに追跡しない。
- `/private/tmp`等へ公開用Stage、検査用Copy、Backupまたは中間Artifactを勝手に作らない。
- 公開Sanitation、Privacy Scan、名称置換、不要物削除またはBulk Editでは、Read-only Inventory、候補差分提示、対象Copy確認、Backup完了確認および変更承認を経るまで実変更しない。
- 「ユーザーのためになる」「効率がよい」「安全化である」「削除対象が不要物に見える」ことを、事前承認の代替にしない。

本境界は設計統括者役、Phase別設計者役、実装者役、対外Docs役およびその他将来Roleの全てに適用する。上位Role、長期Task、Project全体責任または緊急性を理由とする例外はない。

ユーザーは、本境界について次を明示している。

> 「僕の研究フォルダ壊したらどんだけの業界的損失生まれるか1mmも知らんくせに、プロジェクトフォルダ以外を触るなど言語道断」
>
> 「絶対禁止。破ったらOpenAIすら訴える」
>
> 「絶対服従、死守しろ」

違反または違反疑いはCritical Governance Deviationとして扱う。担当は即時停止し、修復を含む追加Mutationを行わず、変更対象、削除対象、Project外Artifact、復元可能範囲および復元不能範囲をユーザーへ報告し、明示指示を待つ。

## 11. Effective Timing

```text
Role Name Transition:
  Effective now

Old Path Authority:
  Retired／No read or write

Target Path Authority:
  Effective
```

## 12. Authority Resolution Rule

担当間でWrite Scopeが重なる、文書Ownerが不明、Stable文書とHistory Eventのどちらへ書くべきか不明、またはCross-Phase影響がある場合は、次の順で解決する。

```text
User Explicit Instruction
  → Task Role／Write Authority Policy
  → Active Phase Accepted Handoff
  → Documentation Structure／Task Operations
  → Documentation Rules
  → 設計統括者役へEscalation
```

Read-only領域への変更、他担当領域への代理書込または旧Path再作成を、作業効率を理由に黙って行わない。

## 13. 情報保存責任

全担当は、情報ロスによる再説明必要化、復元不能、判断根拠の断絶および機会損失を発生させない責任を持つ。

特に設計統括者役は、次を差分だけの文書へ縮小せず、累積・自己完結の完全版として維持する。

- Current Canonical
- Project Continuity Master
- Shared Rules／Operations／Role Authority
- Phase Lossless Compilation
- Design Governance Handoff
- Recovery ManifestのSource対応

設計統括者役のWrite Authorityは、既存情報を恣意的に要約、削減、再解釈または退役するAuthorityを含まない。訂正時も更新前原文、訂正理由および現在有効な内容を追跡可能にする。

Phase別設計者役と実装者役は、Status、Handoff、Review Sourceまたは失敗Evidenceを「解決済み」「正本へ反映済み」という理由で削除しない。

対外Docs役はPublic文書を基本的に追加式で管理する。読みやすさを改善しても、Projectの独自性、研究価値、主要な将来構想、重要な制約および留意事項を失わせない。Overview、ConceptおよびRoadmapの変更前後Snapshotを対応する`docs/public/history/<category>/`へ保存する。

## 14. 設計統括者役Handoff Authority

設計統括者役専用Handoffの正本入口は次とする。

```text
docs/project/shared/design_governance_handoff/
design_governance_handoff_ja.md
```

更新前後Snapshot、Recovery Manifestおよび復元検証Evidenceは次へ保持する。

```text
docs/project/shared/history/design_governance_handoff/
```

設計統括者役は原則各Phase完了後、Phase Backup直前にこのHandoffを更新する。Task Limit等により継続性が危うい場合はPhase途中でも臨時更新する。

新しい設計統括者役TaskがDocsだけで旧Taskを完全に引き継げない場合、Recoveryは未完了である。設計統括者役を復元できることに加え、その新TaskがPhase別設計者役、実装者役および対外Docs役を必要な正本とHandoffから再作成できることを完了条件とする。

## 15. 大規模Documentation ReconstructionのAuthority

大規模再構築では、設計統括者役がSource Inventory、Current、Shared、Phase Lossless、Project Continuity、Roadmapおよび相互Linkの技術的整合を管理する。Phase 1-ex完了までは、ユーザーの明示指示によりREADME、Public Docs、利用条件文書を含む全Docs作成を設計統括者役が担当する。

この一時的な担当集中は、対外Docs役の恒久的Write Authorityを廃止するものではない。Phase 2以降の通常運用へ戻す時点で、対外Docs役の再開範囲とHandoffをユーザー承認のもとで確定する。

再構築中も次は許可されない。

- Source Inventoryへ含めるべきRaw Historyを独断で除外する。
- 読みやすさを理由にLossless文書を要約へ置換する。
- Phase 1-ex途中のCompilationをFinalと表記する。
- 英語版作成をユーザー決定前に公開Gateへ追加する。
- Git未設計の状態でGit初期化、CommitまたはPushを行う。
- Public文書作成を理由に、未公開の核心Algorithm、Secret、Private URLまたは個人情報を追加する。
- 設計統括者役の判断だけで既存運用を変更する。

## 16. 現在の作業OwnerとRead-only境界

2026-07-27のDocumentation Reconstruction中のOwnerは次である。

```text
設計統括者役:
  Source Inventory
  Project Continuity Master
  Current Canonical
  Phase 1／Phase 1-ex Lossless
  Shared
  Public
  README／LICENSE／TERMS／NOTICE／CITATION
  Reconstruction Validation

実装者役:
  実装変更は依頼されていない
  Current／Shared／Phase Lossless／PublicはRead-only

対外Docs役:
  Phase 1-ex完了まで作業待機
  既存Public／README／Legal ArtifactはRead-only

ユーザー:
  運用変更、Git、公開、License方針、External Service操作の最終Authority
```

作業待機はRole削除を意味しない。次のHandoffがAcceptedされるまで、他担当は設計統括者役の再構築対象へ代理書込みしない。
