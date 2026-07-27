# MARGPA Runtime LLM Documentation Rules

```yaml
document_id: documentation_rules
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 08:14:59 JST
owner: 設計統括者役
rag_default: true
```

## 1. Root

Project Rootは`margpa-runtime-llm/`である。ユーザーが`docs/`等の相対Pathだけを指定した場合、Project Root配下として解釈する。

Task間の情報伝達、進捗、Handoffおよび設計正本は原則`docs/`で行う。

Docsを読む担当は、明示的なWrite Authorityがない限りRead-onlyとして扱う。

Migration前の`docs/adr/`、`docs/architecture/`、`docs/governance/`、`docs/handoffs/`、`docs/operations/`、`docs/requirements/`、`docs/user_manual/`およびRoot Timestamp Indexは退役済みである。これらの旧Pathを再作成せず、Raw原文は`docs/project/phases/<phase>/history/`から参照する。

## 2. Language／Filename

- 本文は可能な限り日本語とする。
- File名は英語lower_snake_caseを基本とする。
- `docs/project/current/`と`docs/public/`の日本語文書は`_ja`を付け、日本語版を正本とする。
- `docs/project/current/`と`docs/public/`では、日本語正本作成・更新時に対応する`_en`派生版も作成する。
- 英語派生版は概要版、短縮版または抄訳にしない。日本語正本と同じ粒度、情報量および構造を保ち、見出し、要件、根拠、設計判断、制約、例外、留意事項、既知の制限、未決事項、参照先を省略せず対応させる。
- 自然な英語表現への翻訳、語順調整および用語説明は許容するが、意味の追加、削除、弱化、強化または再解釈を行わない。
- 英語版だけで新しい要件、判断または例外を追加しない。Conflict時は日本語版を正本とする。
- 日本語正本と英語派生版の同等性を確認できない場合、そのDocumentation Refreshは未完了として扱う。
- Phase、Shared、Raw History、Handoff、Status、Reviewおよび内部Operationsは日本語のみとする。
- `README.md`、`LICENSE`、`NOTICE.md`、`CITATION.cff`等の標準名は例外とする。
- 英語派生版は`_en`を使用する。

Phase 1-exのCanonical／Public生成Stageより前の暫定設計更新では`_en`が未作成でもよい。ただしInitial Commit前RefreshではCurrent／PublicのJA／EN Pairを必須とし、未作成のまま公開可能と判定しない。

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

Stable Current、Phase Compilation、Phase IndexおよびPublic CurrentにはTimestampを付けない。

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

- 本ProjectのGit運用は未決定である。
- Git初期化、Commit、Branch、Tag、Remote、Push、公開Repositoryへの投入、履歴加工およびGitを前提とするDocs運用は、ユーザーがGit運用設計を明示承認するまで実施しない。
- 将来Gitを採用した場合も、Gitは追加の差分管理・証跡手段であり、Append-only Development Log、Timestamp Snapshot、Phase HistoryおよびBackupの代替ではない。
- 「Gitに履歴が残る」ことを理由に、Docsの履歴保存を省略、削減または廃止しない。

### 5.2 運用変更の禁止

- ユーザーが承認済みのDocs構造、Append-only方針、保持方針、命名規則、Role Authority、Git方針、正本境界、公開境界、削除・退役条件およびTask間伝達方式を、ユーザーの明示許可なく変更してはならない。
- 設計統括者役であることは、ユーザー承認済み運用を単独で変更する権限を意味しない。
- 「改善」「整理」「重複除去」「Git移行」「Stable化」「役目終了」等を理由とする暗黙の運用変更を禁止する。
- 運用変更が必要と考える場合は、変更案、対象、影響、保持・Rollback方法および変更しない場合の影響を提示し、ユーザーの明示承認を得てから実施する。
- 指示が曖昧、競合またはAuthority不明である場合は、既存運用を維持して停止し、ユーザーへ確認する。都合のよい権限解釈を行わない。
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

Phase IndexまたはCurrent Indexを更新するたびに、同じ作業単位とTimestampで、更新後の論理状態を表す新しいAppend-only Index SnapshotをActive Phaseの`history/`へ必ず追加する。

```text
Stable Latest:
  docs/project/phases/<phase>/phase_index_ja.md
  docs/project/current/documentation_index_ja.md

Append-only Index Snapshot:
  docs/project/phases/<active_phase>/history/
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

`history/index/`への再配置は、Phase切替時に次を同時に満たせる場合だけ再検討する。

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

Initial Commit前には、実装後の状態に合わせてCurrent／Public／Setup／RAG／Public Demo／Git関連Docsを再編集し、JA／EN、Link、Identity、License、AllowlistおよびManifestを再検証する。

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

- `overview_ja.md`：Projectの概要を伝える文書とし、300〜500程度を基準にする。必要に応じて累積追加する。
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

この構造はPhase 2開始時から適用する予約である。Phase 1およびPhase 1-exのRaw Indexは、ユーザーの別途明示許可なしに遡及移動しない。
