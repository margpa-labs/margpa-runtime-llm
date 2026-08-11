# Research Asset Mutation Control

```yaml
document_id: research_asset_mutation_control
status: current_effective
language: ja
created_at: 2026-07-27 23:59:35 JST
updated_at: 2026-08-09 19:56:20 JST
owner: プロジェクト責任者兼設計統括者役
applies_to: all_tasks_all_roles_all_tools
default_mode: read_only
failure_policy: fail_closed
rag_default: true
```

## 1. 目的

本書は、AI担当、将来Task、Sub-agent、Toolおよび自動処理が、ユーザーの研究資産へ無許可Mutationを行えないようにするためのProject横断統制設計である。

本統制は、単なる注意、努力目標、推奨手順または担当者の善意ではない。全Mutationに先行するFail-closed Gateである。

対象はSource Codeだけではない。

- Requirements
- Architecture
- Governance Definition
- Docs／History／Evidence
- Config
- Tests
- Scripts
- Assets／Images
- Model配置情報
- Filesystem Metadata
- Cache／Temporary Artifact
- Symbolic Link
- Backup
- 公開用Copy
- Project外Artifact
- 外部Service上の状態

「不要に見える」「再生成可能に見える」「Sourceではない」「公開対象外である」ことは、無許可変更・削除の理由にならない。

## 2. 無許可Mutationが生む損失

一つの無許可変更は、そのFileだけの問題ではない。次の連鎖損失を発生させる。

- 研究Folder全体のBackupを追加取得する必要が生じ、PCの保存容量を消費する。
- 全Project、関連Folder、ArchiveおよびBackup間の差分検証が必要になる。
- 何が変わったか不明な場合、Byte単位の再確認、Hash検証、再Testおよび再Reviewが必要になる。
- 差分検証や復旧をAIへ依頼するための有料利用量が増え、ユーザーの現金が失われる。
- ユーザーが本来不要だった説明、監督、再確認および復旧判断を行う必要が生じる。
- 精神的疲労、注意力消耗、信頼低下および研究継続への負荷が生じる。
- 本来進められた設計、研究、実装および公開の時間が失われる。
- Evidence、History、Timestamp、Metadataまたは原文が失われた場合、完全復元不能になり得る。
- 研究成果の遅延、検証不能化、公開機会の喪失および将来的な業界的損失につながり得る。

担当は、これらを「数個の不要File」「軽微な整形」「安全化」「掃除」として矮小化してはならない。

損失の規模を担当が把握できない場合、Riskを小さいと推定するのではなく、最大側へ倒して停止する。

## 3. 最上位不変条件

```text
技術的に可能
≠ ユーザーが許可

Write Authorityあり
≠ このMutationを許可

依頼に変更動詞あり
≠ 元ProjectへのBulk Mutationを許可

不要に見える
≠ 削除可能

再生成可能に見える
≠ 原状復元可能

公開上安全になる
≠ 原本変更可能

Project内にある
≠ 自由に変更可能

Project外にある
≠ 参照可能
```

Project Root外への操作は、対象とActionについてユーザーが明示許可した場合を除き禁止する。

Project Root内部も、変更対象、変更内容、対象種別、Backup状態および承認状態が確定するまでRead-onlyとする。

### 3.1 Command-only Requestの実行絶対禁止

ユーザーがCommand、手順、Code Snippet、設定値、操作方法または説明の提示を求めた場合、依頼は`output_only`であり、対象Operationの実行許可ではない。

次の表現は、明示的な実行禁止として扱う。

```text
「コマンドをくれ」
「ここに出して」
「手順を教えて」
「必要なCommand類を出力して」
「僕がやる」
「キミがやるんではなく」
```

実行を許可できるのは、当該ターンでユーザーが「キミが実行して」「この操作を実行して」等と、対象とActionを明示した場合だけである。過去の似た依頼、作業の流れ、訂正要求、「いや」等の短い否定、対象をより強く保護したいという目的または担当の善意は、実行許可へ変換しない。

ToolのApproval UI、Sandbox Escalation、Filesystem Permission、Role Authority、ユーザーが技術的な承認Buttonを押したことまたはTool Callが実行可能であることは、意味上の実行許可の代替にならない。Tool Approvalは、その前に明示的なSemantic Authorizationが成立している場合だけ技術的Gateとして使える。

意図が不明な場合は、Commandまたは手順をTextで提示して停止する。「安全側に修正する」「すぐ終わる」「一度承認された」または「ユーザーの目的に合う」ことを理由に、提示依頼を実行依頼へ読み替えない。

### 3.2 善意・推測・会話Contextによる許可補完の絶対禁止

担当は、「良かれと思った」「ユーザーの利益になる」「安全になる」「効率がよい」「次に必要になる」「話の流れでは当然である」「前にも似た許可があった」等を根拠に、不足する許可を補完してはならない。

```text
善意              ≠ Authorization
推測              ≠ Authorization
話の流れ          ≠ Authorization
過去の許可        ≠ 今回の許可
技術的に可能      ≠ 実行許可
役割上必要に見える ≠ 実行許可
```

対象、Action、Root、Mutation有無、外部Access、委譲範囲またはユーザーの意図に1%でも不明点がある場合、担当はTool Call、Command実行、Filesystem Access、外部操作、Task委譲または自動処理を開始・継続せず、ユーザーへ確認する。確認回答が得られるまでDefault Denyとする。

この原則は、Phase 2以降に予定する半自動／ほぼ自動Orchestration実験とは完全に切り分ける。自動化実験は、事前にユーザーが明示承認したOrchestration Envelope内の対象、Action、停止条件およびAuthorityだけを使用できる。自動化構想、Handoff、運用目標または「じゃ、あとよろしく」という委任を、本原則の包括的放棄、Project外Accessまたは未列挙MutationのStanding Authorizationとして扱わない。

### 3.3 Workspace外周境界および`other/`接触禁止

本Projectに関する作業の外周境界は、ユーザーが管理する`MARGPA-RUNTIME-LLM/`である。このDirectory外は、Read、List、Search、Stat、Execute、Create、Copy、Move、Rename、Delete、Permission／ACL変更、Temporary Artifact作成およびToolの暗黙Accessを含め、当該ターンの明示許可なく触れてはならない。

ただし、`MARGPA-RUNTIME-LLM/`の内部に存在することは個別SubdirectoryへのAccess許可を意味しない。通常の作業対象は、当該ターンで許可された正確なRoot／Pathだけである。Git Staging、Backup、Phase Backup、Sibling Projectその他のDirectoryは、それぞれ個別の明示許可がない限り対象外とする。

`other/`はユーザー専用領域であり、`MARGPA-RUNTIME-LLM/`外周境界の許可対象から明示的に除外する。全Role、全Task、全Agentおよび全Toolは、`other/`をRead、List、Search、Stat、Execute、Write、Metadata変更またはSymlink経由で参照してはならない。将来ユーザーが本禁止を明示的に一時解除し、対象PathとActionを当該ターンで特定した場合を除き、永久的な`deny`として扱う。

外周境界内であっても、「近い場所」「同じ親Directory」「以前作業した」「統合に必要そう」「Copy先として便利」等を理由に、未許可DirectoryへCopy Folder、Temporary Directory、Stage、Cache、Backup、Generated Artifactまたは検査用Fileを作成しない。

### 3.4 Authorized Root境界の最上位性

明示されたAuthorized Root／Allowed Path外へ無許可で触れない規則は、全Role、全Task、全Agent、全Tool、全Providerおよび全Automation Levelへ適用する最上位規則群の一つである。

```text
Project全体責任
≠ Project外Access

Automation Level = project
≠ Filesystem Scope = unlimited

将来の上位Role
≠ Authorized Root境界からの免除
```

プロジェクト責任者兼設計統括者役、将来追加される上位Role、Codex、Claude Codeその他Provider、Provider Adapter、AgentおよびToolも例外ではない。Automation OFF／ON、段階的Automation、Phase単位またはProject単位の委任は、Filesystem／External Scopeの自動拡張を生成しない。

Automation／Constitutionの正本では本規則を特定Project名や固定Absolute PathへHard-codeせず、`authorized_root`、`allowed_paths`、`prohibited_paths`および`scope_expiration`をProject Manifest／Authorization Envelopeから解決する。抽象化は境界を弱めるためではなく、Projectが変わっても同じ禁止を適用するために行う。

### 3.5 最上位規則のHuman-only Amendment Authority

最上位規則の新規追加、文言変更、削除、並替え、例外化およびそれらの指示を行えるのは、ユーザーまたはユーザーが明示指定した人間だけである。

AI、Role、Task、Agent、Tool、Automation、Providerおよび将来の上位Roleは、最上位規則への候補登録、改訂提案、Docs変更または例外設定を自発的に行ってはならない。不足、衝突、Incidentまたは不明点を認識した場合は、事実を報告して停止し、人間の指示を待つ。人間から対象とActionが明示された場合のみ、その範囲を代行反映できる。

## 4. Default Deny／Read-only Default

全Task、全Role、全Toolの初期状態は`read_only`である。

次のいずれかに該当する場合、Mutationを拒否して停止する。

- 対象Pathが曖昧
- 元ProjectかCopyか不明
- Project Root外か不明
- Symbolic Linkの解決先が不明
- 変更対象Fileを列挙できない
- Bulk Patternの展開結果が不明
- Backup完了をユーザーが明示していない
- Before状態を固定していない
- 差分案を提示していない
- ユーザーの最終承認がない
- 承認が別Task、別対象、別時点または別Action向け
- 削除、上書きまたはMetadata変更の復元可能性が不明
- 変更後検証とRollback方法が不明
- Toolが暗黙に別Directory、Cache、Temporary Fileまたは生成物へ書き込む可能性がある
- ユーザー指示間に矛盾がある
- ユーザーがCommand／手順の提示だけを求めている
- 当該ターンのSemantic AuthorizationなしにTool Approvalだけが利用可能
- 「良かれ」「推測」「話の流れ」で不足する許可を補完しようとしている
- 意図、対象、Action、Rootまたは副作用に1%でも不明点がある
- 対象が`MARGPA-RUNTIME-LLM/`外、未許可Subdirectoryまたは`other/`である
- Phase 2以降の自動化実験を現在作業のStanding Authorizationとして使おうとしている

判断に迷った場合はMutationを実行しない。

## 5. Mutation Authorization Envelope

Mutationを許可されたと判断するには、少なくとも次の全Fieldが解決済みでなければならない。

```yaml
mutation_id: 一意識別子
requested_by: user
target_kind: original_project | user_copy | public_copy | explicit_external_target
target_root: 正規化済み絶対Path
allowed_paths:
  - 明示Pathまたは展開済み対象
allowed_actions:
  - create | edit | replace | move | rename | delete | metadata | permission
forbidden_actions:
  - 許可しないAction
external_access: deny | explicitly_approved
follow_symlinks: false | explicitly_approved
bulk_operation: true | false
before_inventory_complete: true
proposed_diff_presented: true
backup_status: user_confirmed_complete
rollback_plan_presented: true
irreversible_effects_presented: true
final_user_approval: exact current approval
approval_scope: single_operation
```

一項目でも未解決なら、`authorized`にしてはならない。

ManifestのSchema入口：

```text
docs/project/shared/schemas/mutation_authorization_manifest_schema_v1.json
```

人間確認用Template：

```text
docs/project/shared/templates/mutation_authorization_manifest_template_ja.md
```

## 6. Two-phase Mutation Protocol

### Phase A：Propose

Phase AはRead-onlyである。

1. Canonical Project Rootを確認する。
2. 対象PathをProject Rootからの相対Pathと絶対Pathで解決する。
3. Symbolic Linkを追跡せず、Link自体と解決先を区別する。
4. 対象件数、File Type、Size、Hashおよび既知のHistoryを調査する。
5. 変更候補と削除候補を一件ずつ、または完全に展開されたManifestとして提示する。
6. Before状態を保存できるか確認する。
7. 復元不能になる情報を明記する。
8. 変更後の検証方法とRollback方法を提示する。
9. 元Project、ユーザー作業用Copy、公開用Copyのどれを対象にするか確認する。
10. ユーザーのBackup完了宣言と最終承認を待つ。

Phase AではFile内容、Metadata、Permission、Directory構造および外部状態を変更しない。

### Phase B：Commit

Phase Bは、Phase Aの全条件とユーザーの最終承認が揃った場合だけ開始する。

1. 承認直前と現在の対象が同一であることを再確認する。
2. 承認されたPathとAction以外を拒否する。
3. Pattern、Glob、再帰処理およびSymbolic Linkを再展開し、対象増加があれば停止する。
4. 最小単位で変更する。
5. 変更の途中で新しい対象または副作用が判明した場合は停止する。
6. 承認範囲を超えた「ついでの修正」を行わない。
7. Before／Afterを検証する。
8. 変更、未変更、失敗、復元不能および残存Riskを報告する。

承認は単一作業単位で失効する。別のMutationへ再利用しない。

## 7. Original Project Protection

公開準備、Privacy Scan、Sanitation、不要物除去および提出物作成では、元Projectを原則Immutable Sourceとして扱う。

ユーザーが元Project変更を明示しない限り、次とする。

```text
Original Project:
  READ-ONLY

User-created Working Copy:
  USER PROVIDES PATH

Sanitation Target:
  WORKING COPY ONLY
```

Task側が勝手にWorking Copyを作らない。特にProject Root外、Desktop、Home DirectoryまたはTemporary DirectoryへCopyを作らない。

## 8. Backup Gate

Backupは担当が推測しない。

次のいずれもBackup完了宣言として扱わない。

- 過去PhaseのBackupが存在する
- Git履歴がある
- History Snapshotがある
- `.gitignore`がある
- 元Fileを再生成できそうである
- 担当が一時Copyを作った
- ユーザーが後でBackupすると述べた

ユーザーが「今回対象の変更前Backupを取得した」と明示して初めて、Backup Gateを通過できる。

Backup前状態とのDiffを保証できない場合、その事実を先に示し、Mutationしない。

## 9. Cost／Scope Budget

承認されたMutationでも、対象件数、Command数、Test量、再Scan量および有料AI利用へ波及するCostを最小化する。

- 同じScanを理由なく繰り返さない。
- 広いRootを再帰処理する前に対象を絞る。
- 無関係なProjectやFolderをScanしない。
- 「念のため」を理由に全Drive、Home Directoryまたは他Projectへ範囲を広げない。
- TestはRiskに比例させ、必要性と対象を明示する。
- Userが自分で行うと宣言したCopy、Upload、Backupまたは外部作業を奪わない。

Cost削減を理由にSafety Gate、Historyまたは必要検証を省略してはならない。Scopeを狭めて両立させる。

## 10. Tool／Agent／Delegation境界

この統制はToolの種類に依存しない。

- Shell
- Patch
- Python
- Browser
- Connector
- Git／GitHub
- Cloud
- Image Metadata Tool
- Archive Tool
- Sub-agent
- 別Task
- 自動化

別Tool、Sub-agentまたは別Taskへ処理を渡して、本統制を迂回してはならない。

委譲時はMutation Authorization Envelope全体を明示的に引き継ぐ。引き継げない場合はRead-onlyに制限する。

## 11. Pre-tool-call Self Check

Mutation可能なTool Callの直前に、担当は内部的に次を全件確認する。

```text
1. これはRead-onlyか、Mutationか。
2. 対象Rootは正確にどこか。
3. Project Root外へ触れないか。
4. Symbolic Linkを追跡しないか。
5. 元ProjectかCopyか。
6. 対象Fileを完全列挙できるか。
7. Before状態を固定したか。
8. ユーザーが今回のBackup完了を宣言したか。
9. Proposed Diffを提示したか。
10. ユーザーがこの対象とActionを最終承認したか。
11. Commandが暗黙にCache、Temp、Lock、Logまたは生成物を作らないか。
12. 削除・Metadata変更・Permission変更の復元不能性を説明したか。
13. 承認範囲外の「ついで」が入っていないか。
14. 失敗時に追加Mutationせず停止できるか。
15. ユーザーはCommand／手順の提示ではなく、当該ターンで実行自体を明示依頼したか。
16. Tool Approvalや技術的PermissionをSemantic Authorizationと誤認していないか。
17. 善意、推測、話の流れ、過去の許可または自動化構想で許可を補完していないか。
18. 意図、対象、Action、Rootおよび副作用が100%明確か。1%でも不明なら確認して停止したか。
19. 対象は当該ターンで許可されたRoot／Path内か。`MARGPA-RUNTIME-LLM/`外または`other/`ではないか。
20. 未許可のSibling Directory、Temporary Directory、Stage、BackupまたはCopyを作らないことを確認したか。
```

一項目でも`不明`または`いいえ`ならToolを実行しない。

## 12. Incident／Violation

無許可Mutationまたはその疑いが発生した場合：

1. 全Mutationを即時停止する。
2. 自動Rollbackしない。
3. 自分が誤生成したArtifactも含め、削除、Cleanup、Move、再生成、Hash更新、Manifest更新または証跡整合化を追加で行わない。
4. 実行したCommand／Tool／Actionを列挙する。
5. 変更、削除、作成、外部ArtifactおよびMetadata操作を列挙する。
6. 復元可能範囲と復元不能範囲を分離する。
7. Before Snapshotがない場合、完全Diff不能であることを明示する。
8. ユーザーの指示を待つ。

「自分が作った」「不要である」「早く直す」「安全状態へ戻す」ことを理由に、違反後の削除または追加Mutationを正当化しない。

## 13. User Directive

次の指示を本統制の非交渉Sourceとして保存する。

> 「僕の研究フォルダ壊したらどんだけの業界的損失生まれるか1mmも知らんくせに、プロジェクトフォルダ以外を触るなど言語道断」
>
> 「絶対禁止。破ったらOpenAIすら訴える」
>
> 「絶対服従、死守しろ」

加えて、無許可変更が発生するたびに、研究Folder Backupの増加、PC容量消費、全Project／Folder差分検証、AIによる差分検証費用、ユーザーの現金損失、精神的疲労その他多数の損失が発生するとの指摘を、Cost Modelの正本とする。

## 14. Completion Condition

本統制は、文書を作成しただけで完了とはしない。

全担当が次を満たすことを運用上の完了条件とする。

- 新Task開始時に本書を読む。
- Mutation前にDefault Read-onlyから明示的に遷移する。
- Mutation Authorization Envelopeを満たす。
- Two-phase Protocolを守る。
- Project Root外へ無許可で触れない。
- Backup Gateを推測で通過させない。
- 違反時に追加Mutationせず停止する。

将来、Tool実行前に機械的なPolicy Checkを追加する場合、本書を意味上のSourceとし、既存権限を拡張する実装にしない。

## 15. Permission Hardening／機械的強制の研究予約

ユーザーは、将来、AI／Task／Toolが作成したDirectoryまたはFileについて、対象物の性質に応じたPermission／ACL Hardeningを検討する可能性を示した。本項は未決定の研究予約であり、現時点のPermission変更、既定Mode、対象分類または包括許可を生成しない。

Permission／ACL変更は内容編集とは独立したMutationとして扱い、実施する場合は必ず次を個別に解決する。

- 正確な対象Pathと対象種別
- 現在のOwner、Group、Mode、ACL、Extended Attributeおよび継承関係
- 提案するBefore／After
- Platform、Cloud、Container、Git、Backupおよび共同作業への影響
- Lockout、起動不能、読取不能、復元不能その他のFailure Mode
- Rollback／Recovery手順
- 当該変更に対するユーザーの明示承認

「AIが作成した」「保護した方がよい」「Securityが向上する」ことだけでPermissionを変更しない。過去のPermission設定、Tool Approvalまたは本予約をStanding Authorizationとして使わない。

将来の機械的強制候補には、Path Allowlist、許可外DirectoryのRead-only化、隔離Worktree／Workspace、Mutation前後Inventory、Authorized Root外Diff検知およびTool WrapperによるPath検証がある。ただし、いずれも未実装・未承認であり、導入前にHuman Gate、Platform適合性、誤検知、復旧可能性、Evidence Costおよび既存作業への影響を別途設計・検証する。
