# MARGPA Runtime LLM Documentation Rules

```yaml
document_id: documentation_rules
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-08-11 13:09:30 JST
owner: 設計統括者役
rag_default: true
```

## 1. Root

Project Rootは`margpa-runtime-llm/`である。ユーザーが`docs/`等の相対Pathだけを指定した場合、Project Root配下として解釈する。

Task間の情報伝達、進捗、Handoffおよび設計正本は原則`docs/`で行う。

Docsを読む担当は、明示的なWrite Authorityがない限りRead-onlyとして扱う。

Migration前の`docs/adr/`、`docs/architecture/`、`docs/governance/`、`docs/handoffs/`、`docs/operations/`、`docs/requirements/`、`docs/user_manual/`およびRoot Timestamp Indexは退役済みである。これらの旧Pathを再作成せず、Raw原文は`docs/project/phases/<phase>/history/`から参照する。

### 1.1 Project Root境界の絶対遵守

Projectに関する通常の読取・作成・変更・削除・Copy・Move・Rename・Archive・展開・Metadata操作・Permission操作・Hash取得・一時Artifact作成およびCommand実行の対象境界は、Project Rootである`margpa-runtime-llm/`内部に限定する。

次を非交渉規則とする。

- ユーザーが、対象Pathと実施Actionをその作業について明示的に許可しない限り、Project Root外のFile、Directory、Temporary Directory、Desktop、Home Directory、Model置場、Cloud Storage、外部Repositoryまたは外部Serviceへ一切触れない。
- Tool、Sandbox、Filesystem、OS、Connector、RoleまたはTask上の技術的Permissionは、ユーザーの許可を意味しない。
- 過去の別作業に対する許可、包括的に見える権限、Write Scopeまたは「作業上便利である」という事情を、Project Root外へ触れる許可へ拡張解釈しない。
- Project内のSymbolic LinkがProject Root外を指す場合、ユーザーがLink先とActionを明示許可しない限り、Linkを追跡して読取、走査、変更、削除またはCopyしない。
- `/private/tmp`等のTemporary Directoryを含め、Project Root外へ検査用Copy、公開用Stage、Manifest、Cache、Backupまたは中間生成物を勝手に作らない。
- Project Root外を参照する必要があると判断した場合は、対象、目的、Action、Risk、作成・変更・削除の有無および後処理を事前提示し、ユーザーの明示許可を待つ。

### 1.2 原本変更前の必須停止Gate

個人情報検査、公開Sanitation、不要File削除、名称置換、機械的一括変更、Directory再編、Metadata除去、Permission変更、Archive作成その他の広範な処理では、元Projectを直接変更してはならない。

必ず次の順序を守る。

1. 元ProjectをRead-onlyで調査する。
2. 検出対象、変更候補、削除候補、対象件数、対象Path、影響およびRollback可否を提示する。
3. 操作対象が元Projectか、ユーザー作成の作業用Copyか、公開用Copyかを明示的に確認する。
4. ユーザーによるBackup取得完了の明示を待つ。
5. 変更対象と変更内容について、改めてユーザーの明示承認を得る。
6. 承認された対象だけを変更し、元Projectと作業用Copyを混同しない。
7. Before／After差分、削除物、復元不能物および検証結果を報告する。

ユーザーの依頼文に「置換」「削除」「修正」等が含まれていても、広範なSanitation、公開準備または一括処理で、元Project／Copyの区別またはBackup完了が明示されていない場合は、Read-only調査と候補提示で停止する。都合よく元Projectへの即時変更許可と解釈しない。

### 1.3 ユーザー明示の非交渉指示

次のユーザー指示を、表現を弱化、要約または再解釈せず保存する。

> 「僕の研究フォルダ壊したらどんだけの業界的損失生まれるか1mmも知らんくせに、プロジェクトフォルダ以外を触るなど言語道断」
>
> 「絶対禁止。破ったらOpenAIすら訴える」
>
> 「絶対服従、死守しろ」

本Projectの操作境界、原本保全、Backup Gateおよびユーザー承認に関しては、設計統括者役を含む全担当がこの指示を死守する。違反または違反の疑いを認識した場合、修復を名目とする追加変更も勝手に行わず、直ちに作業を停止し、実施済みAction、対象、影響、復元可能範囲、復元不能範囲および残存Artifactをユーザーへ報告して指示を待つ。

### 1.4 Research Asset Mutation Control

全担当、全Tool、将来TaskおよびSub-agentへ適用するMutation統制正本は、[Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)とする。

同書は次を強制する。

- Default Read-only／Default Deny
- 無許可Mutationの連鎖損失を矮小化しないCost Model
- Mutation Authorization Envelope
- Propose／Commitの二段階Protocol
- 元Project原則Immutable
- ユーザーによるBackup完了宣言
- Pre-tool-call Self Check
- Tool／Agent／Delegationによる迂回禁止
- 違反時の即時停止と無許可修復禁止

無許可Mutationが発生するたび、研究Folder Backupの増加、PC容量消費、全Project／Folder差分検証、AI差分検証費用による現金損失、精神的疲労、研究時間喪失、復元不能および将来的な研究・業界上の機会損失が発生し得る。この損失を「軽微なFile変更」として扱わない。

Mutation Manifestは次を使用する。

```text
Schema:
  docs/project/shared/schemas/mutation_authorization_manifest_schema_v1.json

Template:
  docs/project/shared/templates/mutation_authorization_manifest_template_ja.md
```

## 2. Language／Filename

- 本文は可能な限り日本語とする。
- File名は英語lower_snake_caseを基本とする。
- `docs/project/current/`、`docs/project/shared/`および`docs/public/`の日本語Stable文書は`_ja`を付け、日本語版を正本とする。
- `docs/project/current/`、`docs/project/shared/`および`docs/public/`以下にある全`*_ja` Stable文書を、任意英語派生版の対象とする。
- 上記三Root内であっても、Path中に`history/`を含む全文書・全Artifactは英語派生版の対象外とする。History Snapshot、Append-only Index、Event、Before／After原文、旧版を翻訳、Rename、複製または`_en`化しない。
- 英語派生版は概要版、短縮版または抄訳にしない。日本語正本と同じ粒度、情報量および構造を保ち、見出し、要件、根拠、設計判断、制約、例外、留意事項、既知の制限、未決事項、参照先を省略せず対応させる。
- 自然な英語表現への翻訳、語順調整および用語説明は許容するが、意味の追加、削除、弱化、強化または再解釈を行わない。
- 英語版だけで新しい要件、判断または例外を追加しない。Conflict時は日本語版を正本とする。
- 英語派生版を作成対象に含めたDocumentation Refreshでは、日本語正本との同等性を確認できない場合、そのRefreshを未完了として扱う。
- Phase、Raw History、Handoff、StatusおよびReviewは日本語のみとする。Shared Stable文書は英語派生版の対象に含む。
- `README.md`、`LICENSE`、`NOTICE.md`、`CITATION.cff`等の標準名は例外とする。
- 英語派生版は`_en`を使用する。

Phase 1-ex Stage 6のDocumentation Refreshで作業余力がある場合は、Current／Shared／Publicの全対象Stable文書について`_en`派生版を作成する。余力がない場合は、後日またはPhase 2前半へ明示的に延期する。英語版作成をPhase 1-ex、初回Commit、BackupまたはPhase 2移行の自動必須Gateへ変更してはならない。作成すると決定した場合は、対象文書すべてを日本語正本と同じ粒度で作り、部分的な抄訳を正式版として扱わない。

## 3. Documentation Classes

### Current

`docs/project/current/`

現在の正本。Stable Filenameは最新版への入口として使用する。変更前後の原文は、相対Categoryを維持して`docs/project/current/history/`へTimestamp付きで保持する。Git Historyを前提にせず、将来Gitを採用してもAppend-only Logの代替にしない。

### Phase

`docs/project/phases/<phase>/`

Phase Index、Lossless Compilation、Active Phase設計およびHistoryを置く。

### Shared

`docs/project/shared/`

Phase横断の規則、Role、SchemaおよびTemplateを置く。変更前後の原文は、相対Categoryを維持して`docs/project/shared/history/`へTimestamp付きで保持する。

### Public

`docs/public/`

人が最初に読む対外文書を置く。変更前後の原文は`docs/public/history/`へ保持する。Roadmapの履歴は`docs/public/history/roadmap/`へ分離し、同一Phase内の複数更新もTimestampで識別する。

構造、読解順序、再構築境界、Phase運用およびTask間運用の詳細は[Documentation Structure／Task Operations](../operations/documentation_structure_and_task_operations_ja.md)を参照する。

## 4. Stable／Event Filename

Current、Shared、Public、Phase Stable、Phase Compilation、Phase IndexおよびLossless再整理後の最新版正本にはTimestampを付けない。

この規則はRoadmapだけの例外規則ではなく、全Stable文書に共通して適用する。

例：

```text
Current:
  requirements_specification_ja.md
  system_architecture_ja.md
  project_continuity_master_ja.md

Shared:
  documentation_rules_ja.md
  documentation_structure_and_task_operations_ja.md
  task_role_write_authority_policy_ja.md
  design_governance_handoff_ja.md

Public:
  overview_ja.md
  concept_ja.md
  roadmap_ja.md

Phase Stable:
  phase_index_ja.md
  phase_<phase>_requirements_ja.md
  phase_<phase>_architecture_ja.md
  Phase Lossless CompilationのStable文書
```

Timestampを付けるのは、History Snapshot、Handoff、Status、Review、実行Evidence、変更RecordおよびAppend-only Index Snapshot等の履歴・Event Artifactだけである。

Raw History、Handoff、Status、Review、実行Evidence等のEvent Fileは次の形式を使う。

```text
descriptive_name_YYYYMMDDHHMMSS.md
```

新しいTimestampほど新しいEventである。

Current、SharedおよびPublicのStable文書を退避するHistory Snapshotは次の形式を使う。

```text
<stable_document_stem>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

例：

```text
basic_design_phase_1_ex_ja_20260727071234.md
documentation_rules_phase_1_ex_ja_20260727071234.md
roadmap_phase_1_ex_ja_20260727071234.md
```

同一Phaseで同じ文書を複数回更新しても、Timestampが異なるため衝突しない。変更前／変更後の区別はSnapshot本文の`updated_at`、SHA-512、対応する変更Recordおよび作成順序から解決する。

## 5. History

- Historyは原則Immutableである。
- 内容変更時は新Timestampの新Fileを作る。
- 新Fileに`supersedes`を記載する。
- 古い文書へSuperseded表記を追記しない。
- Privacy／Credential Scrubだけは理由とRecordを伴う例外とする。
- Git開始後もRaw Phase Historyを通常のCurrent文書として上書きしない。
- 作成済みのAppend-only Development Log、Handoff、Status、Review、Evidence、Decision、Index SnapshotおよびRaw Sourceは、役目を終えたこと、重複して見えること、Stable版へ反映済みであること、または将来Gitを使用することを理由に削除、上書き、統合、圧縮、置換または退役しない。
- Stable Filenameの文書を更新する場合も、更新前の原文と更新後の原文をTimestamp付きHistoryへ保存し、各時点の内容を復元可能にする。
- Phase単位のLossless Compilationを作る際は、当該PhaseのAppend-only Development Log全体をSourceとし、一部の最新版だけから再構成しない。
- Rollback、監査、Task再作成およびPhase単位再整理に必要な情報を失わせない。

### 5.1 Gitの現在状態

- 本ProjectはExisting RepositoryのHistoryを継承し、Git運用を開始している。Branch、Commit、Pull Request、Merge、Tag、Remote、Identity、Backup対応およびLocal Working Rootの正本は[Git Workflow Policy](../operations/git_workflow_policy_ja.md)とする。
- Git操作はユーザーの明示承認Gateを維持する。Git運用開始を、Commit、Push、Merge、Branch／Tag削除、Remote変更、History RewriteまたはRepository設定変更のStanding Authorizationとして扱わない。
- Gitは追加の差分管理・証跡手段であり、Append-only Development Log、Timestamp Snapshot、Phase HistoryおよびBackupの代替ではない。
- 「Gitに履歴が残る」ことを理由に、Docsの履歴保存を省略、削減または廃止しない。

### 5.2 運用変更の禁止

- ユーザーが承認済みのDocs構造、Append-only方針、保持方針、命名規則、Role Authority、Git方針、正本境界、公開境界、削除・退役条件およびTask間伝達方式を、ユーザーの明示許可なく変更してはならない。
- 設計統括者役であることは、ユーザー承認済み運用を単独で変更する権限を意味しない。
- 「改善」「整理」「重複除去」「Git移行」「Stable化」「役目終了」等を理由とする暗黙の運用変更を禁止する。
- 運用変更が必要と考える場合は、変更案、対象、影響、保持・Rollback方法および変更しない場合の影響を提示し、ユーザーの明示承認を得てから実施する。
- 指示が曖昧、競合またはAuthority不明である場合は、既存運用を維持して対象Actionを停止し、都合のよい権限解釈を行わない。担当内の技術・設計・実装・Docs解釈は直属上位Role、Cross-Role／Cross-Phase／委譲境界は最高責任者役、ユーザー意図・最上位規則・Root／Authority拡張・External／Secret／Destructive・Human-only GateはユーザーへEscalateする。
- 無許可の運用変更はGovernance Deviationとして記録し、発見時は作業を停止して、原状・影響・復旧方法を報告する。

### 5.3 Current／Shared／Public Stable History

次のHistory RootをStable文書の変更前後Snapshot置場として使用する。

```text
docs/project/current/history/
docs/project/shared/history/
docs/public/history/
```

配置規則：

```text
Current:
  docs/project/current/<category>/<stable_document>
    → docs/project/current/history/<category>/

Shared:
  docs/project/shared/<category>/<stable_document>
    → docs/project/shared/history/<category>/

Public:
  docs/public/<stable_document>
    → docs/public/history/<category>/

Public Roadmap:
  docs/public/roadmap_ja.md
    → docs/public/history/roadmap/

Current Index:
  docs/project/current/documentation_index_ja.md
    → docs/project/current/history/index/

Public Overview:
  docs/public/overview_ja.md
    → docs/public/history/overview/

Public Concept:
  docs/public/concept_ja.md
    → docs/public/history/concept/
```

Stable文書を変更する作業は、次の順序を必須とする。

1. 対象Stable文書とOwner、Active Phase、Languageを確定する。
2. 更新前原文を`<stem>_<phase>_<language>_YYYYMMDDHHMMSS.md`として対応Historyへ完全コピーする。
3. 更新前Stable文書とHistory SnapshotのSHA-512一致を確認する。
4. 更新前Snapshot、Current／Phase／Shared／Publicの関連正本、Raw Historyおよびユーザー指示をSourceとして新しいStable文書を構築する。
5. Stable文書を更新し、Link、Language Pair、意味の保持およびWrite Authorityを検証する。
6. 更新後原文も別Timestampの同形式Filenameで対応Historyへ完全コピーし、SHA-512一致を確認する。
7. Active Phaseの変更Record、Phase IndexおよびAppend-only Documentation Index Snapshotへ対応を記録する。

更新前Snapshotを作らずStable文書を丸ごと上書きすることを禁止する。更新後Stableだけを残し、更新前原文をGit Historyから復元する運用にも変更しない。

`docs/public/history/roadmap/roadmap_phase_1_ja.md`はTimestamp規則導入前の既存History原本としてImmutableに保持する。改名、上書きまたは置換せず、以後に作るRoadmap Snapshotだけを`roadmap_<phase>_<language>_YYYYMMDDHHMMSS.md`形式にする。

## 6. Lossless Compilation

- 「まとめる」は要約を意味しない。
- Source InventoryとSHA-512を先に固定する。
- 決定、条件、例外、矛盾、未解決事項を削らない。
- Sourceの意味を変えない。
- Link Path等の配置依存情報だけ機械的に正規化できる。
- 各Source Path、HashおよびRaw Historyへの対応を維持する。
- 重複や矛盾を勝手に一つの新判断へ統合しない。

## 7. Index

```text
Current Index:
  docs/project/current/documentation_index_ja.md

Phase Index:
  docs/project/phases/<phase>/phase_index_ja.md
```

IndexもStable文書として更新する。ただし、Stable Indexは最新版への入口であり、開発ログを置き換えない。

Phase IndexまたはCurrent Indexを更新するたびに、同じ作業単位とTimestampで、更新後の論理状態を表す新しいAppend-only Index SnapshotをActive Phaseの所定Historyへ必ず追加する。

```text
Stable Latest:
  docs/project/phases/<phase>/phase_index_ja.md
  docs/project/current/documentation_index_ja.md

Append-only Index Snapshot:
  Phase 1／Phase 1-ex:
    docs/project/phases/<active_phase>/history/

  Phase 2以降:
    docs/project/phases/<active_phase>/history/index/

  documentation_index_YYYYMMDDHHMMSS.md
```

- Stable Indexだけを上書きして作業を完了しない。
- Snapshotへ`supersedes`、対象Stable Index、作成時刻および当該時点の状態を記録する。
- Snapshot作成後は上書きしない。
- History配置による相対Link変更は機械的にRebaseし、その旨を記録する。
- Review、Handoff、Statusまたは重要DecisionをIndexへ追加した場合も、同時にSnapshotを作る。
- Git Historyは補助証跡であり、Append-only Index Snapshotの代替にしない。
- 過去Snapshotを事後復元する場合は、`reconstructed`、復元元および復元忠実度を明示する。

Git開始前に作成されたRaw `documentation_index_YYYYMMDDHHMMSS.md`は、原文の相対Link基準を維持するため、現在は各Phaseの`history/`直下へ保持する。

Phase 1／Phase 1-exのRaw Indexを`history/index/`へ再配置する場合は、次を同時に満たせる場合だけ再検討する。

- Raw本文とSHA-512の保全
- Index内部の相対Link維持
- Source／Retirement／Target Manifest更新
- Current／Phase／Compilation Link検証
- 担当TaskへのPath変更通知

これらを満たさない単純Moveは行わない。

## 8. Write Authority

- 設計統括者役：Current、Shared、Cross-Phase、Phase Final Review
- Phase別設計者役：担当PhaseのRequirements／Architecture／ADR
- 実装者役：`src／tests／scripts`と許可されたConfig、Status Event
- 対外Docs役：README、LICENSE、NOTICE、CITATION、`docs/public/`

Canonical技術正本、Frozen Compilationおよび他担当領域はRead-onlyとする。

上記Write Scopeは、記載範囲の文書をユーザー承認済み運用に従って作成・更新できる範囲を示すだけであり、運用規則そのものを独断で変更するAuthorityではない。ユーザーの明示指示が最上位であり、設計統括者役を含む全担当はこれを上書きできない。

詳細は[Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)を参照する。

## 9. Links

- CurrentはStable TargetへLinkする。
- Phase IndexはCompilation、Final Review、Backup EvidenceへLinkする。
- CompilationはSource ManifestからRaw HistoryとSHA-512を解決可能にする。
- History原本へCurrent Backlinkを追記しない。
- File移動時はLocal Linkを検証し、Known Exceptionを分離する。

## 10. RAG

Default Source：

- Current Canonical
- Active Phase Index
- Completed Phase Compilation
- Public Current

Raw Historyは通常検索対象外とし、監査、矛盾調査またはSource指定時だけ使用する。

## 11. Identity／Security

- 公開名義は`Nazuna Research`を使用する。
- 個人連絡先、個人Profile、実Absolute Path、Credential、Secretを記載しない。
- Model本体、実会話Log、RAG私有資料を公開対象へ含めない。
- Test Fixtureは架空値であることを明示する。

## 12. Phase Completion

Phase完了は、実装／Review、ユーザーAcceptance、設計統括者の完了・次Phase移行可能宣言後に確定する。

Phase完了宣言後、Phase Backupを取得する直前に、設計統括者役の完全復元用Continuity RefreshとReconstruction Validationを必ず実施する。これが未完了の場合、Phase Backupへ進まない。

Continuity Refreshでは、Current Canonical、Shared Rules、Role Authority、Project Continuity Master、Active／Completed Phase Index、Accepted Review、Open Finding、未決事項、External State、次Phase入口およびSource／SHA-512対応を更新する。新しい設計統括者役Taskが旧Taskの会話記憶を前提にせず、Docsだけから現設計統括者役の責務、判断、状態および次作業を復元できることを完了条件とする。

Backup後にPublic文書とGit／GitHub状態を更新する。Backup Artifactから`.DS_Store`、`.venv`、Model、Cache、Secret等を除外する。

Initial Commit前には、実装後の状態に合わせてCurrent／Shared／Public／Setup／RAG／Public Demo／Git関連Docsを再編集し、Language Scope、Link、Identity、License、AllowlistおよびManifestを再検証する。`_en`派生版は作業余力がある場合にCurrent／Shared／Publicの非History Stable文書を対象として作成する。作成しない場合は後日またはPhase 2前半へ延期し、その状態をInitial Commit対象Manifestへ明記する。

ただし、Git／GitHub状態の更新は、Git運用設計と当該更新操作についてユーザーの明示許可を得た場合に限る。

## 13. Shared Category／Stable History対応

SharedのPhase横断文書は、次のCategoryを正式な配置先として使用する。

```text
docs/project/shared/
├─ conventions/
├─ operations/
├─ task_roles/
├─ schemas/
├─ templates/
├─ user_manual/
└─ design_governance_handoff/
```

各Stable文書の変更前後Snapshotは、同じCategory名を維持して次へ保存する。

```text
docs/project/shared/history/
├─ conventions/
├─ operations/
├─ task_roles/
├─ schemas/
├─ templates/
├─ user_manual/
└─ design_governance_handoff/
```

`schemas/`と`templates/`は将来Artifactが作成された時点から同じStable History規則を適用する。空Directoryの存在だけを理由にDummy Fileを作らない。

設計統括者役専用のStable入口は次とする。

```text
docs/project/shared/design_governance_handoff/
design_governance_handoff_ja.md
```

更新前後Snapshot、Phase完了時のRecovery Manifestおよび復元検証Evidenceは、次へAppend-onlyで保持する。

```text
docs/project/shared/history/design_governance_handoff/
```

Recovery ManifestのFilenameは次とする。

```text
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

## 14. 情報保存最優先／累積完全版

本ProjectのDocs運用は、情報ロスによる再説明必要化、復元不能、判断根拠の断絶および機会損失を避けることを最優先とする。

特に次の文書群は、情報ロスを一切許さない水準で構築・更新する。

- 既存DocsのLossless再整理
- `docs/project/current/`のCurrent Canonical
- `docs/project/current/project_continuity/`
- `docs/project/shared/`
- Phase単位Lossless Compilation
- 設計統括者役の完全復元文書

これらの最新版は差分だけを記載する文書にしない。各Stable文書は、その一つだけを読んでも現在有効な内容を解決できる累積・自己完結の完全版とする。

- 新しい決定、要件、例外、制約、既知の制限、未決事項、根拠および参照先を既存内容へ追加する。
- 既にAcceptedとなった情報を、短文化、重複除去、読みやすさ、File SizeまたはGit差分を理由に黙って削らない。
- 訂正が必要な場合は、更新前原文をHistoryへ保持し、最新版では旧記述との関係、訂正理由および現在有効な内容を明示する。
- 後続版は原則として、Projectの進展に応じて粒度と情報量が増える。
- 複数文書から再構築する場合は、最新版だけでなく対象範囲のRaw History、Accepted Review、Handoff、Status、DecisionおよびEvidenceをSource Inventoryへ含める。
- 「同じ内容が別文書にある」ことを、正本に必要な自己完結情報を落とす理由にしない。詳細参照Linkを使う場合も、当該文書の目的に必要な前提と結論を残す。

`Project Continuity Master`はProject継続性の生命線として扱う。現在位置、決定、未決事項、復元手順、外部状態および次の安全な一手を差分参照なしで解決できる状態を維持する。

## 15. Public文書の累積運用

Public文書も基本的に追加式とし、Milestone更新時に変更前後の完全Snapshotを対応Historyへ保存する。

```text
docs/public/overview_ja.md
  → docs/public/history/overview/

docs/public/concept_ja.md
  → docs/public/history/concept/

docs/public/roadmap_ja.md
  → docs/public/history/roadmap/
```

内容の目安：

- `overview_ja.md`：Projectの目的、対象問題、位置付け、全体構造、設計原則、研究方法、Evidence思想および現在地を、単独で概要を理解できる粒度で説明する。他文書が存在することを理由に極端に短縮せず、固定の行数・文字数だけを達成基準にしない。必要に応じて累積追加する。
- `concept_ja.md`：OverviewとRoadmapを踏まえ、Projectのコンセプトが伝わる粒度とする。必要に応じて累積追加する。
- `roadmap_ja.md`：現在の`roadmap_ja.md`と同等以上の粒度で、実装済み、進行中、未着手、将来構想、Phase Gateおよび研究上の方向性をしっかり記録する。必要に応じて累積追加する。

対外向けに読みやすく整えることは許容するが、Projectの特徴、研究価値、重要な将来構想、制約または留意事項を、単純化のために消さない。

## 16. Current Index History

`docs/project/current/documentation_index_ja.md`の変更前後Snapshotは次へ保存する。

```text
docs/project/current/history/index/
documentation_index_<phase>_<language>_YYYYMMDDHHMMSS.md
```

このCurrent Index Historyは、Active Phase直下のAppend-only `documentation_index_YYYYMMDDHHMMSS.md`とは役割が異なる。

- Current Index History：Current Stable Index本文そのものの変更前後原文
- Phase Documentation Index Snapshot：当該作業時点のDocs構成、変更Record、Source、HashおよびPhase状態

両方を保持し、一方で他方を代替しない。

## 17. Shared Optional Category／専用Category

次のShared Categoryは、必要なArtifactがある場合だけ使用する任意Categoryである。

```text
docs/project/shared/schemas/
docs/project/shared/templates/
docs/project/shared/user_manual/
```

- 使用が必要になった時点でArtifactを置く。
- 現在または特定Phaseで不要なら使用しなくてよい。
- Directoryが存在することを、文書作成の必須要件と解釈しない。
- 空Directoryを維持するためだけのDummy Fileを作らない。
- Artifactを作成・更新した場合は、対応する`docs/project/shared/history/<category>/`へ変更前後Snapshotを保存する。

Docs運用の専用Categoryは既存の次を使用する。

```text
docs/project/shared/operations/
docs/project/shared/history/operations/
```

今後のPhase横断Docs運用手順、構造運用、Migration、Compilation、Index、Backup前Docs処理およびTask間Docs運用は、原則`shared/operations/`をStable入口とする。純粋な命名、言語、Immutable性等の規約正本は`shared/conventions/`へ置き、Operationsから参照する。Docs運用のために意味が重複する新しい同格Directoryを追加しない。

権限管理の専用Categoryは既存の次を使用する。

```text
docs/project/shared/task_roles/
docs/project/shared/history/task_roles/
```

Role、Write Authority、Read-only Boundary、EscalationおよびTask間責務は`shared/task_roles/`へ集約する。意味が重複する`authority/`、`permissions/`等の新しい同格Directoryは作らない。

## 18. Public Stable Filename／Roadmap更新

Public文書の最新版はTimestampなしのStable Filenameを維持する。

ここでRoadmapを示すのは具体例であり、TimestampなしStable名の規則自体はCurrent、Shared、Public、Phase StableおよびLossless再整理後正本の全てに適用する。

```text
docs/public/overview_ja.md
docs/public/concept_ja.md
docs/public/roadmap_ja.md
```

`<phase>_<language>_YYYYMMDDHHMMSS`を付けるのは、`history/`へ保存する変更前後Snapshotだけである。

```text
docs/public/history/overview/
overview_<phase>_<language>_YYYYMMDDHHMMSS.md

docs/public/history/concept/
concept_<phase>_<language>_YYYYMMDDHHMMSS.md

docs/public/history/roadmap/
roadmap_<phase>_<language>_YYYYMMDDHHMMSS.md
```

Roadmap更新では、少なくとも次を毎回確認・反映する。

- 現在の進捗
- 完了済み、進行中、未着手、保留および再評価待ちの区別
- Active Phaseと次Phase
- Phase Gate／公開状態／Backup状態
- 新しく追加された要件
- 既存要件の変更、優先順位変更および再配置
- 将来構想、研究機能、外部R&D Hook
- Known Limitation、依存条件および重要な留意事項

新要件が増えた場合、Roadmapへ漏れなく反映する。後続Phaseへ移した要件も消さず、移動先と状態を明示する。

## 19. Phase 2以降のPhase History Index

Phase 2以降は、各Phaseに次を設ける。

```text
docs/project/phases/<phase>/
├─ phase_index_ja.md
└─ history/
   └─ index/
      └─ documentation_index_YYYYMMDDHHMMSS.md
```

- `phase_index_ja.md`はTimestampなしの最新Stable入口である。
- `history/index/`は、Stable Phase Indexとは別のAppend-only Documentation Index Snapshot置場である。
- Stable Phase Indexを更新するたびに、新TimestampのSnapshotを`history/index/`へ追加する。
- Snapshotを上書きせず、新しいTimestampほど新しい状態とする。
- Phaseの`index/`に置くLossless Compilation等とは役割を分離する。

この構造はPhase 2開始時から必須適用する。Phase 2最初のDocumentation Index Snapshotから`history/index/`へ保存し、`history/`直下へ新規作成しない。Phase 1およびPhase 1-exのRaw Indexは、ユーザーの別途明示許可なしに遡及移動しない。

## 20. 大規模再構築の二周規則

情報ロスの影響がProject全体へ波及する大規模Documentation Reconstructionでは、Project Continuity MasterとRoadmapを一度だけ作って完了してはならない。

必須順序：

```text
Source Inventory／Freeze
  → Project Continuity Master 第1周
  → Roadmap 第1周
  → Current Canonical再構築
  → Phase単位Lossless再整理
  → Shared再構築
  → Project Continuity Master 第2周
  → Roadmap 第2周
  → Public／README／Legal Artifact
  → Corpus全体検証
```

第1周は後続文書を構築するための復元基盤、第2周は作業中に確定したSource、Hash、文書構成、進捗、例外、未決事項および公開状態を取り込む最終照合である。第2周で第1周の内容を短縮せず、追加・訂正方式で累積させる。

`concept_ja.md`等のPublic文書はProject Continuity、RoadmapおよびCurrent CanonicalをSourceとして作る。Conceptを独立した想像で補完せず、疎結合、研究性、Runtime Governance、交換可能性および将来R&D Hookを正本と同じ意味で表現する。

## 21. Phase Lossless Compilationの直接収録方式

Phase単位Lossless Compilationは、読みやすい要約だけで原文保存を代替しない。現在採用している直接収録方式では、各Sourceを次の情報とともにCompilationへByte単位で埋め込む。

- 連番
- Source Path
- Source Size
- Source SHA-512
- Begin／End Marker
- Source Set Digest
- Machine-readable Manifest

検証ではMarker後から宣言Byte数を再抽出し、各Source SHA-512とManifestを照合する。

自己参照と無限増殖を避けるため、Compilation生成前にSource Freezeを行い、生成対象の`lossless/`、当該作業で後から作るRecord／Index／Snapshotおよび`.DS_Store`を除外する。除外は情報削除ではなく、Source集合を有限・再現可能にする境界である。Freeze後に増えたArtifactは次回CompilationまたはFinal Phase Compilationで取り込む。

Phase 1-exのPhase途中Compilationは必ず`interim`または`current-to-date`と明示し、Phase完了版を装わない。Phase完了時には、その後追加されたPhase 1-ex文書を含む新しいFinal Lossless Compilationを別途作成する。

## 22. 2026-07-27再構築時点の検証済み基準

今回の再構築で確認した基準は次である。

```text
Initial Source Inventory:
  Docs Files       : 493
  Demo Images      : 6
  Total Entries    : 499
  Entry-list SHA-512:
    1d1dd20dafc6184339bb6ce709269d6c8e058ec97aba982a1ab0554c4754a7148b1b5fc9cfd362891480eafd723f909792393e3ebd094d04fdd349cbfe46e22c

Phase 1 Lossless:
  Sources          : 316
  Verification     : 316 / 316 pass
  Source-set SHA-512:
    52958a309007df372e0d31f91f576ecdb3f81bb44c632fb53561068cfe9e3a4a5073bb4d8a229b20a5dbfc87212950b2a55e45740dce350ba3a88789f7cc5165

Phase 1-ex Interim Lossless:
  Sources          : 145
  Verification     : 145 / 145 pass
  Source-set SHA-512:
    0220358633c705e4c936455c613804bff6fff6ab90d9294318f0853278ae4154c6d088252650fe460ac44a0064f2c995a825c8649f642b9e206d1d29ebaef89b
```

Source Inventoryは再構築開始時のFreeze、Phase Lossless件数は各Compilation Freeze時点であり、同じ時刻の集合ではない。作業後に追加されたSnapshot、Record、IndexおよびPublic Artifactにより現在のFile数が増えることは正常である。件数差を欠落と誤認せず、各ManifestのFreeze時刻とScopeで照合する。

関連Stable入口：

- `docs/project/phases/phase_1/lossless/phase_1_lossless_ja.md`
- `docs/project/phases/phase_1/lossless/phase_1_lossless_manifest.json`
- `docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_ja.md`
- `docs/project/phases/phase_1_ex/lossless/phase_1_ex_interim_lossless_manifest.json`

この基準は今後のFinal Compilationで置換せず、比較元として保持する。

## 23. 文書ごとの責務分離

文書を作成・更新する前に、対象読者、文書の役割、正本範囲、記載すべき要素、記載してはならない詳細および参照先を確定する。

「別文書に書かれている」ことだけを理由に、当該文書を理解するために必要な最低限の説明、現在地、利用境界、免責または正本導線を削除しない。一方、自己完結を理由に、下位文書の詳細を上位入口へ丸ごと複製しない。

### 23.1 README

READMEはRepositoryを初めて開いた読者のための最小Project入口である。

記載する。

- Project名と公開名義
- Projectを識別できる短い説明
- 現在Phase
- Roadmapへの強い導線
- Overview、Concept、Roadmapおよび主要Canonicalへの導線
- 代表的な現在画面
- Research Preview／Open Source状態
- Model Weight非同梱等の重要な配布境界
- 利用条件と第三者Artifactへの短い注意
- LLM出力に関する基本的な注意
- 一切の保証を行わないこと
- 文書が必要に応じて変更される可能性
- LICENSE、TERMS_OF_USE、NOTICEおよびCITATIONへの導線
- 短いEnglish Abstract

READMEへ記載しない。

- 個別Hardware、Memory、OS Architecture、Acceleration、PythonまたはBackend Version
- 個別Model Artifact、Directory Treeまたは配置手順
- Setup Command、CLI Command、Server起動・停止または環境再構築手順
- 外部Serviceの操作手順、Credential設定またはPort公開手順
- Phase別の未搭載機能、将来Componentまたは研究機構の詳細列挙
- Architecture、Governance、OperationsまたはUser Manual本文の再掲

READMEに必要な免責と利用境界は、LICENSE等へのLinkだけに置き換えない。初見で誤解や危険な依存を避けるための短い要点をREADMEにも残し、法的・運用上の正本へLinkする。

READMEには次の文を明記する。

> 各文書は修正する必要性があるため、都度内容が変更される可能性があります。

### 23.2 Public Overview

OverviewはProject全体を俯瞰する概要文書であり、READMEより詳しく、Concept、RoadmapおよびCurrent Canonicalより抽象度を高く保つ。

記載する。

- Projectの目的
- 背景と対象問題
- Projectの位置付け
- 全体の論理構造
- 中核となる設計原則
- AuthorityとEvidenceに関する不変条件
- 比較・検証方法の概要
- Project Continuityの考え方
- 現在Phaseの短い位置付け
- 詳細文書の読解順序
- 研究・保証上の境界

Overviewへ記載しない。

- 個別Hardware、Memory、OS Architecture、AccelerationまたはVersion
- 個別Model Artifact、Backend VersionまたはFile配置
- Setup、CLI、Server操作または外部Service操作
- Phaseごとの詳細な実装済み／未実装一覧
- User Manual、Technology SelectionまたはOperations Evidenceの再掲

他文書が存在することを理由に、Overviewを数行の実行環境説明へ縮小しない。Project全体像を単独で理解できる粒度を確保する。

### 23.3 Public Concept

ConceptはProjectの思想、中核概念、不変条件、研究上の意味および長期的な位置付けを説明する。

- 実装手順、環境仕様およびPhase別Status一覧を主内容にしない。
- 比喩を使う場合は字義的な製品・実装主張と区別する。
- 将来構想を現在の実装済み能力として表現しない。
- 会話口調、感情的評価、採用文脈、個人・企業・無関係な役職等の識別情報を混入させない。

### 23.4 Public Roadmap

Roadmapは、Phase別の実装済み、進行中、未着手、保留、依存順序、Phase Gate、将来構想および進捗の正本である。

- READMEやOverviewから削除した将来機能を消失させず、Roadmapで管理する。
- 現在の進捗をMilestone更新時に反映する。
- 実装済みと計画を明確に分ける。
- 新要件、優先順位変更および後続Phaseへの移動を追跡可能にする。

### 23.5 Current Canonical

```text
Requirements Specification:
  機能要件、非機能要件、制約、受入条件、未決事項

System Architecture:
  System Boundary、Component配置、接続、情報Flow、Trust／Authority Boundary

Technology Selection:
  実行環境、Model、Backend、Language、Library、Version、採否理由、互換性

Basic Design:
  Component責務、Port、Contract、Schema、主要Flow、Error、State

Runtime Governance Specification:
  Governance Definition、Compile、Binding、State、Evaluation、Action、Repair、Evidence

Project Continuity Master:
  Project全体の累積状態、決定、未決事項、復元入口、次の安全な一手
```

### 23.6 Phase／Operations／User Manual

```text
Phase Index:
  当該PhaseのGoal、正本、Evidence、Review、Status、残作業、Index Chain

Phase Requirements／Architecture／ADR:
  当該Phaseに限定した要件、設計、Decision

Operations／Evidence:
  実行手順、Migration、Validation、Receipt、Failure、Rollback

User Manual:
  利用者が行うSetup、起動、停止、操作、確認、Troubleshooting

Handoff／Status／Review:
  担当境界、作業指示、実施結果、Finding、Acceptance
```

環境詳細と操作手順はREADME／Overviewではなく、Technology Selection、OperationsおよびUser Manualへ置く。

### 23.7 重複の判断

必要な重複と不要な重複を区別する。

必要な重複：

- READMEの短い免責とLICENSEへの導線
- README／Overviewの現在PhaseとRoadmapへの導線
- Overviewの中核原則とConcept／Architectureへの導線
- 各正本が単独で成立するための前提と結論

不要な重複：

- READMEへの環境MatrixやCommand一式
- Overviewへの個別Acceptance Log
- ConceptへのPhaseごとの実装Checklist
- Roadmapへの操作手順全文
- 複数正本への同一Schema全文コピー

文書責務を理由に必要情報を削りすぎず、自己完結を理由に詳細を複製しすぎない。上位文書は要点と正本導線を保持し、詳細は責務を持つ下位文書へ委ねる。

### 23.8 作成・Review Checklist

文書作成・更新時に次を確認する。

1. 対象読者は誰か。
2. この文書が回答する質問は何か。
3. この文書の正本範囲は何か。
4. 最低限重複して残すべき要点は何か。
5. 他文書へ委ねる詳細は何か。
6. 個別環境、操作、将来計画またはEvidenceが責務外へ流入していないか。
7. 他文書があることを理由に必要情報を削りすぎていないか。
8. 実装済み、進行中、未実装、保留を混同していないか。
9. 免責、利用条件、Securityおよび変更可能性の必要な短い注意が残っているか。
10. 正本へのLinkが存在し、切れていないか。
11. 変更前後Snapshot、Record、IndexおよびSHA-512を残したか。
