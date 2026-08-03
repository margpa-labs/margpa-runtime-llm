# MARGPA Runtime LLM Documentation Rules

```yaml
document_id: documentation_rules
status: current
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-26 20:29:35 JST
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

現在の正本。Stable Filenameを使用し、Git Historyで変更を追跡する。

### Phase

`docs/project/phases/<phase>/`

Phase Index、Lossless Compilation、Active Phase設計およびHistoryを置く。

### Shared

`docs/project/shared/`

Phase横断の規則、Role、SchemaおよびTemplateを置く。

### Public

`docs/public/`

人が最初に読む対外文書を置く。細かな履歴ではなくMilestone Historyを残す。

構造、読解順序、再構築境界、Phase運用およびTask間運用の詳細は[Documentation Structure／Task Operations](../operations/documentation_structure_and_task_operations_ja.md)を参照する。

## 4. Stable／Event Filename

Stable Current、Phase Compilation、Phase IndexおよびPublic CurrentにはTimestampを付けない。

Raw History、Handoff、Status、Review、実行Evidence等のEvent Fileは次の形式を使う。

```text
descriptive_name_YYYYMMDDHHMMSS.md
```

新しいTimestampほど新しいEventである。

## 5. History

- Historyは原則Immutableである。
- 内容変更時は新Timestampの新Fileを作る。
- 新Fileに`supersedes`を記載する。
- 古い文書へSuperseded表記を追記しない。
- Privacy／Credential Scrubだけは理由とRecordを伴う例外とする。
- Git開始後もRaw Phase Historyを通常のCurrent文書として上書きしない。

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

Backup後にPublic文書とGit／GitHub状態を更新する。Backup Artifactから`.DS_Store`、`.venv`、Model、Cache、Secret等を除外する。

Initial Commit前には、実装後の状態に合わせてCurrent／Public／Setup／RAG／Public Demo／Git関連Docsを再編集し、JA／EN、Link、Identity、License、AllowlistおよびManifestを再検証する。
