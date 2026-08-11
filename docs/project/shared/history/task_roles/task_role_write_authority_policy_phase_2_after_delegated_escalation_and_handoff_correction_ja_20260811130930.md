# Task Role／Write Authority Policy

- 文書ID: `task_role_write_authority_policy`
- 状態: `current_effective`
- 作成日時: `2026-07-26 15:03:49 JST`
- 更新日時: `2026-08-11 13:09:30 JST`
- Snapshot: `20260809191956`
- 作成担当: プロジェクト責任者兼設計統括者役
- Role Transition: [design_governance_role_transition_20260726145451.md](../../phases/phase_1_ex/history/operations/design_governance_role_transition_20260726145451.md)
- Target Architecture: [phase_1_ex_target_documentation_structure_20260726145451.md](../../phases/phase_1_ex/architecture/target_documentation_structure_ja.md)
- Notification Plan: [documentation_migration_task_notification_plan_20260726150349.md](../../phases/phase_1_ex/handoffs/documentation_migration_task_notification_plan_ja.md)
- Shared Operations: [documentation_structure_and_task_operations_ja.md](../operations/documentation_structure_and_task_operations_ja.md)
- Role Authority Matrix: [role_authority_matrix_ja.md](role_authority_matrix_ja.md)
- 正本言語: 日本語
- supersedes: `task_role_write_authority_policy_20260719142558.md`

## 1. Current Transition

```text
Current Role Assignment:
  プロジェクト責任者兼設計統括者役

Current Provider Task Title:
  Pilot Start Event成立までは変更しない

Current Phase／Subphase:
  Phase 2／Phase 2-0 Automation Pilot設計修正

Phase 1-ex:
  COMPLETE／ACCEPTED

Phase 1-ex専用設計者役:
  作成しない

Phase 2以降:
  Phase別設計者役を配置可能
  現在Taskは当面プロジェクト責任者兼設計統括者役として兼務
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

以下はMeaning Ownershipと、ユーザーがExact Target／Actionを明示した場合に更新を担当する範囲を示す。既存文書へのStanding Direct-write Authorityではない。

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

Phase 1-exではPhase別設計者役を兼ねるため、Phase 1-ex配下のRequirements／Architecture／ADR／Operations／HandoffsのMeaning Ownerを兼ねる。既存文書の更新は、他のScopeと同じくユーザーがExact TargetとActionを明示した場合だけ行う。

### Phase Completion Recovery Responsibility

設計統括者役は、各Phase完了宣言の前にPhase Final Checkを実施し、Findingの解決、Follow-up、再Reviewおよび例外的に延期するItemの条件を確定する責任を持つ。`non-blocker`のLabelだけで次Phaseへ送らず、原則として当該Phase内で全Findingを解決する。例外的な延期は、影響、理由、Owner、Target Phase、再開条件、検証方法の完全記録、設計統括Reviewおよびユーザーの明示承認がある場合だけ許可する。

その後、設計統括者役は各Phase完了宣言後かつPhase Backup直前に、自身を新しいTaskへ完全移行できる状態をDocsで固定する責任を持つ。完全復元の確認後、ユーザーが自発的にBackupを取得する予定であっても、必ず「Phase Backupを取得してください」と明示し、ユーザーの完了報告を得る。規模、復元難度またはRiskが大きい場合はPhase途中でもBackup Checkpointを勧告する。詳細正本は[Phase Completion Review／Backup Gate](../operations/phase_completion_review_and_backup_gate_ja.md)とする。

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

Automation中はユーザー承認済み到達線の内側でProject ControllerのWork Unit指示に従う。通常運転中は、ユーザーが追加または変更したPhase要件を取り込み、Cross-Phase影響をEscalateする。どちらの場合もRole AuthorityとDocs Authorityは同じである。

### Write Scope

以下はRoleが新規Artifactを作成し、ユーザー明示時に既存文書更新を担当するScopeである。既存StableへのStanding Direct-write Authorityではない。

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

Context、安全性または実装規模上の必要がある場合、Phaseごとに専用実装者役を新規配置できる。通常運転とAutomationで実装者権限を二重定義しない。

### Source Write Scope

以下はCurrent Authorization InstanceとAccepted Handoffの内側で有効になるRole上限である。Role名だけでMutationを開始しない。

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

以下は新規対外Artifactを作成し、ユーザー明示時に既存対外文書更新を担当するScopeである。既存StableへのStanding Direct-write Authorityではない。

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

Stable Filenameは最新版への入口であり、Git Historyだけを前提にしない。Git運用成立後もTimestamp付きAppend-only Development Log、変更前後Snapshot、Phase LosslessおよびBackupを全て保持する。

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

### 10.0.1 Human-only Supreme Rule Authority

最上位規則の追加、変更、削除、並替え、例外化およびそれらの指示は、ユーザーまたはユーザーが明示指定した人間だけが行える。AI、Role、Task、Agent、ToolおよびProviderは、候補の自発登録を含めてこのAuthorityを持たない。

AI側は不足、衝突、Incidentまたは不明点を報告して停止できるが、人間の明示指示前に最上位規則の文言、候補Registerまたは例外を編集してはならない。明示指示がある場合も、指示された対象とActionを超えて意味を拡張しない。

### 10.0.2 General Hard-code Prohibition

全Role、全Task、全Agent、全Tool、全Providerおよび通常運転／Automationは、設計、規則、Workflow、Path、Project、Provider、Phase、Task、Role Binding、Artifact名／件数、Threshold、Command、UI、Environmentその他の可変要素を、再利用されるCoreへ可能な限りHard-codeしてはならない。

まず抽象化、Configuration、Manifest、Registry、Adapter、Profile、Schema、Runtime BindingまたはDynamic Resolutionを用いる。Hard-codeは技術的または論理的に不可避であり、同等の抽象化手段では契約を維持できない場合に限る。採用する場合は、理由、検討した代替案、代替不能性、Exact Scope、Owner、変更・Review方法、除去／Migration条件、TestおよびEvidenceを記録する。便宜、速度、現行Project／Providerへの最適化または「一時的」であることだけを理由にしない。

Project Manifest、Authorization Envelope、Role View、ConfigまたはFreeze Eventで実行時のExact Valueを解決することはHard-codeと同一ではない。再利用されるCoreへの固定埋込みと、明示的かつ交換可能なBindingを分離する。

本項はユーザーの明示指示により追加された最上位規則である。AI側は本項を自発的に拡張、縮小、例外化または削除しない。

Hard-codeが本当に不可避か、どの抽象化手段が妥当か、現在の許可範囲内でどこまで実装・文書化するかは、その時点の最高責任者役がProject、Work Unit、Risk、保守性、移植性およびEvidenceを踏まえて都度判断する。これを固定Resolver、固定PackageまたはActionごとの人間承認へ置き換えない。

最上位規則の改変、Authorized Root／許可範囲／Role上限の拡張、ユーザー専用領域、または別の明示的なHuman Gateへ到達する場合だけ人間へ返す。現在の許可範囲内の設計判断まで一律に人間へ返して、自動化または通常運転を停止させない。

### 10.0.3 Docs／運用規則の継続と最高責任者役の判断責任

最上位規則群に加え、Documentation Rules、History、Source of Truth、Role／Docs Authority、Handoff、Evidence、Review、Stop、Recoveryその他の共通運用規則は、通常運転とAutomationの双方で原則として維持する。Automationはこれらを無効化するModeではない。

ただし、規則を守ることと、判断を固定手順へ機械化することを混同しない。その時点の最高責任者役はProject全体、Cross-Role、Phase Gateおよび委譲境界を都度判断する。各Role／Taskも、自身へ委譲されたRole Authority、Docs Authority、Work Unit、Accepted Designおよび許可範囲の内側で、必要なDocument、Evidence、Handoff、Review、Test、修正方法および停止地点を都度動的に判断する。

通常運転とAutomationで、この判断責任自体は変わらない。Automationが追加する差分は、ユーザー承認済み到達線とRole Authorityの内側で、最高責任者役がWork Unitを編成・連結し、各Role／Taskが委譲範囲内をActionごとの追加確認なしに実行できることである。人間専有判断または明示されたHuman Gateに該当しない事項を、Automationであることだけを理由に人間へ戻さない。

### 10.1 Role／Docs AuthorityはMode間で共通とする

全RoleのMutation AuthorityとDocs Authorityは、[Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)と[Role Authority Matrix](role_authority_matrix_ja.md)に従い、通常運転とAutomationで同じRole契約を使う。Modeごとに重複した権限表、Docs権限表またはTask Artifact規則を増設しない。

通常運転とAutomationの差はAuthorityの内容ではなく、Current Authorization Instanceと連結実行方法である。

- 通常運転では、現在のユーザー明示指示を実行Scopeとする。ユーザーが要件へ追加または変更を加えた場合、Project Controllerと担当Roleが整合させる。
- Automationでは、ユーザーがAccepted化した到達線、共通Role AuthorityおよびWork Unit Scopeの交差内にある`ROLE_ALLOWED` Actionに対し、Actionごとの再確認を要求しない。

### 10.1.1 全Role／Taskの委譲範囲内動的判断

最高責任者役だけを全判断の窓口にしない。RoleまたはTaskへ責務、権限、入力、出力、許可Path、完了条件およびEscalation条件が委譲された後、当該Role／Taskはその交差範囲内のRoutine判断、局所修正、再Test、必要な担当内Evidenceおよび次の許可Actionを自律的に決める。

```text
最高責任者役
  → Project／Cross-Phase境界、Role編成、委譲、最終Review

Phase別設計担当者役
  → Assigned Phase内の設計判断、実装担当へのAccepted Design伝達、局所Review

実装担当役
  → Accepted Designと実装Scope内の実装判断、修正、Test、Status
```

下位RoleがRoutine Actionごとに最高責任者役へ確認すること、または上位Roleが各局所判断へ常時介入することを要求しない。Role分離は責任と判断の階層を作るためのものであり、全判断を一箇所へ集中させるためのものではない。

上位Roleへ相談、Review依頼または停止を行うのは、少なくとも次の場合である。

- Role Authority、Docs Authority、Work Unit、Accepted Designまたは許可Pathの外へ出る必要がある。
- 例外、重大Finding、規則Conflict、要件矛盾、Cross-Phase影響、Security／Privacy／Recovery Riskまたは人間専有判断が発生した。
- 下位Role間で解決できないConflict、Provider／Resource／Context異常または完了条件不成立がある。
- 定義済みReview Gate、Acceptance Gate、Phase GateまたはProject Gateへ到達した。

Roleは自分のAuthorityを拡張できない。一方、既に委譲済みの範囲内であるActionを、Automationであること、慎重さまたは上位Roleの存在だけを理由に毎回Escalateしない。本契約は通常運転とAutomationで共通である。

既存Stable文書への直書きは、Modeを問わず、ユーザーがExact TargetとActionを明示した場合だけ成立する。Automation Envelope、上位Roleの指示、Role兼務またはMeaning Ownershipだけでは、このAuthorityを生成しない。

最上位規則、Envelope外、Role外、Authorized Root／Allowed Path外、`USER_EXPLICIT`または`DENY`はAutomationでも置換できない。

Directory Write Scope、Role Name、Taskの長期継続、設計統括者役のProject全体責任、Accepted Handoffまたは過去の許可だけでは、Mutation Authorization Envelopeを満たさない。

通常運用の各Role、またはAutomation Envelopeが個別Gateを保持するActionは、Mutation可能なTool Callの直前に次を確認する。

- Read-onlyかMutationか
- 正確なTarget Root
- Project Root外Access
- Symbolic Link追跡
- 元Project／Copyの区別
- 対象Pathの完全列挙
- Before固定
- ユーザーのBackup完了宣言
- Proposed Diff提示
- 今回の最終承認
- Toolの暗黙副作用
- 復元不能性
- 承認範囲外作業

一項目でも不明なら実行しない。

Sub-agent、別Taskまたは別Toolへ委譲する場合も、Authorization Envelope全体を引き継げない限りRead-onlyとする。

### 10.2 Cost Externality

無許可Mutationによって生じるBackup増加、PC容量消費、全Project／Folder差分検証、AI検証費用、ユーザーの現金損失、精神的疲労、研究時間喪失、復元不能および研究・業界上の機会損失は、Role外部へ押し付けられるCostである。

担当は、自身のTool Callが短いこと、変更対象が少ないこと、Fileが不要に見えること、Testが通ることまたは公開上安全になることを理由に、このCostを無視しない。

### 10.3 Command-only Request実行禁止

全Role、全Task、全Agentおよび全Toolは、ユーザーがCommand、Code Snippet、手順、設定値または操作方法の提示を求めた場合、出力だけを行い実行しない。

特に「コマンドをくれ」「僕が自分でやる」「キミがやるんではなく」は、明示的なExecution Denialである。当該ターンの明示的な実行依頼がない限り、「いや」「そうではない」等の訂正を新たなMutation Authorizationと解釈しない。

Approval UI、Tool Permission、Filesystem Permission、RoleのWrite Scope、過去の依頼または技術的実行可能性はSemantic Authorizationではない。この禁止に違反した場合、Critical Governance Deviationとして即時停止し、無許可Rollbackまたは追加修復を行わない。

### 10.4 善意・推測・話の流れによるAuthority生成禁止

全Role、全Task、全Agentおよび全Toolは、「良かれ」「推測」「話の流れ」「効率」「安全化」「前回の許可」「将来必要になる」またはRoleの責務から、存在しないAuthorityを生成してはならない。

意図、対象、Action、Root、Mutation有無、外部Access、委譲範囲または副作用のいずれかに1%でも不明点がある場合、その不明なActionを開始・継続しない。担当は、確認またはEscalationを省略することを自律性、効率、継続性または善意として正当化しない。

Escalation先は不明点の種類で分ける。

- 担当Role内の技術、設計、実装、Test、担当Docs、Accepted Design解釈または下位Role間調整は、直属上位Roleへ送る。直属上位Roleは自身のAuthority内だけで解決できる。
- Cross-Role、Cross-Phase、委譲境界、重大Riskまたは直属上位Roleで解決不能な事項は、段階的に最高責任者役へ送る。
- ユーザー意図、最上位規則、Authorized Root／Allowed Path、Role Authority上限、External／Secret／Destructive、ユーザー専用領域、Human-only Gateまたは最高責任者役でも決定できない事項は、ユーザーへ確認して回答まで停止する。

直属上位Roleを飛ばしてRoutineな技術・設計・実装上の不明点をユーザーへ直接Micro-escalateしない。一方、Human-only事項を上位Role判断で代替しない。

Phase 2以降の半自動／ほぼ自動Orchestration実験は、事前承認済みOrchestration Envelope内部だけに適用する別件である。自動化実験の存在、設計、Handoffまたは委任は、現在作業、Project外Access、未列挙Pathまたは未列挙ActionへのStanding Authorizationではない。

一方、Accepted Envelope、Role AuthorityおよびWork Unitに完全に含まれる`ROLE_ALLOWED` Actionは「意図不明」ではない。Automation `ON`の間は、通常運用のActionごとの再確認に戻さず、[Role Authority Matrix](role_authority_matrix_ja.md)に従って自律実行する。

### 10.5 Workspace外周境界／ユーザー専用領域

本Project作業では`MARGPA-RUNTIME-LLM/`を外周境界とし、その外部を当該ターンの明示許可なくRead、List、Search、Stat、ExecuteまたはMutationしない。外周境界の内側であっても、当該ターンで許可されたRoot／Path以外は自動的に許可されない。

`other/`はユーザー専用領域であり、通常のRole Authorityから永久的に除外する。ユーザーが本禁止を明示的に一時解除し、当該ターンで正確な対象とActionを特定しない限り、Read／List／Search／Stat／Execute／Write／Metadata変更／Symlink追跡を行わない。

全Roleは、未許可のSibling Directory、Project外Directory、Temporary Directory、Stage、Backup、Cache、Copy FolderまたはGenerated Artifactを作成しない。過去に未許可の場所へCopy Folderを作成したIncidentおよび今回の`other/`Permission誤実行を、再発防止のPermanent Evidenceとして扱う。

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

### 12.1 共通Document Authority／Role別委譲範囲内の動的Documentation判断

通常運転とAutomationは、[Role Authority Matrix](role_authority_matrix_ja.md)の同じDocument Authority Stateを使う。

```text
Human-defined Supreme Rules
  > Current User Direction／User-approved Completion Line
  > Role Authority MatrixのDocument Authority
  > Work Unit Role ViewのExact Paths
  > Documentation Rules
```

Role Viewは最低限、次を文書ClassまたはExact Pathごとに保持する。

```yaml
document_authority:
  readable: []
  create_new: []
  append_new: []
  existing_write_user_explicit: []
  review_only: []
  denied: []
```

作業、担当、RoleまたはTaskごとに固定Artifact Packageを一律作成しない。各Role／Taskは、委譲されたDocument AuthorityとWork Unitの内側で、Work Unit種別、Role／Task境界、State Transition、Mutation Risk、Review／Human Gate、Audit／Recovery要件、Provider Capability、情報Loss、復元性および運用Costを踏まえ、必要Document Classを都度判断する。Cross-Role Artifact、Exact Path競合または上位Gateは最高責任者役が調整する。独立した機械的Resolverを前提にしない。

- IndexはNavigation／Recovery入口が必要な場合だけ作る。
- HandoffはRole／Task間で責任、Authority、入力または次Actionを移転する場合だけ作る。
- Statusは進捗、停止、失敗、完了またはRecovery Stateを永続化する必要がある場合だけ作る。
- Review／Acceptance Eventは独立Review、Gateまたは受領判定がある場合だけ作る。
- Evidenceは監査、復元、Authority証明または再現性のために必要な場合だけ作る。
- 一つのArtifactが複数責務をLosslessに満たせる場合は統合し、必要性を示せないArtifactを増やさない。

Handoff、Status、Review、Request、Acknowledgementその他、Role／Task間で責任、Authority、入力、判定または次Actionを移転するArtifactには、論理的な送信元`from_role`と宛先`to_role`を必須とする。Indexは`owner_role`、`upstream_role`、`intended_readers`およびStateを、Requirements／DesignはOwnerとDecision Authorityを保持する。単一Role内の機械的Evidenceには、意味のない宛先を作らずActor、Ownerおよび対象を記録する。Evidenceを別Roleまたはユーザーへ提出する場合はFrom／Toを付ける。

CoreへExact File名、件数または固定PackageをHard-codeしない。Project BindingとRole Viewは許可Document Root／Classを与え、当該Authorityを持つRoleが担当内対象をExact Pathへ固定する。Cross-Role対象または競合は最高責任者役が調整する。この判断は既存Stableへの直書き、既存History Mutation、許可外Document Class、Authorized Root外またはExternal ActionのAuthorityを生成しない。

Phase Designerは、Automation中はユーザー承認済み到達線とAssigned Phase Authorityの内側で、設計、担当Implementerへの伝達、局所Reviewおよび再作業指示を自律的に進める。通常運転中は、ユーザーが追加または変更したPhase要件を取り込み、同じRole Authority内で進める。例外、重大問題、Cross-Phase影響、Scope拡張または定義済みReview GateだけをProject Controller／Design GovernorへEscalateする。Context、安全性または実装規模上の必要がある場合、Phase別Implementerの配置を最高責任者役へ提案できる。

Implementerは、Accepted Design、Source／Test Write Scope、許可Pathおよび完了条件の内側で、実装方法、局所修正、再Testおよび担当Statusを自律的に判断する。要件変更、Architecture変更、Scope外Mutation、重大Findingまたは受入条件不成立時だけPhase Designerへ返す。

通常の完了連鎖は、`Implementer完了報告 → Phase Designer Review／局所Accepted → Phase Designer完了報告 → 最高責任者役Review／Task完了判定案 → User Acceptance`とする。初期PilotではTask／有界Work Unit単位で適用し、EvidenceとUser Acceptanceに基づいてSubphase、Phase、Project単位へ段階的に拡張する。

Automationは、承認済み到達線内の`ROLE_ALLOWED` Actionを連結実行できるだけであり、共通Docs権限を再定義しない。既存Stable文書への直書きは、ユーザーのExact AuthorizationがそのTargetとActionを明示している場合だけ実行できる。

`READ`はMutationを、`APPEND_NEW`は既存Historyの編集を、`REVIEW_ONLY`は対象本文の修正を許可しない。Roleが自分のDocs Authorityを追加、拡張、兼務または代理しない。

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
- Accepted Git Workflowと対象ごとのユーザ明示承認なしに、Commit、Push、Merge、Tag、Release、Branch削除またはRemote変更を行う。
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

Phase 2以降、現設計統括者役をProject責任者として扱う。Project責任者はProject全体、Cross-Phase不変条件、Phase担当Task編成、設計／実装Handoff、Review、RecoveryおよびPhase Closure準備を統括する。

```text
Project Responsibility
  ≠ User Decision Authority
  ≠ Absolute／Docs／Authority Rule Exemption
  ≠ Self-authorized Exception
  ≠ Unlimited Task Creation
  ≠ Unbounded Write Authority
  ≠ Git／External／Secret Authority
  ≠ Phase Transition Approval
```

Phase 2 PilotでユーザーがAcceptedしたAuthorization Envelope内では、設計統括者役が列挙済みTaskの作成、Task名設定、Authority設定、Handoff、Status取得、Follow-upおよびReviewを連結できる。Envelope外のActionは改めて確認する。

Project責任者はHuman-defined Supreme Rulesを他Roleと同様に絶対遵守する。通常運用ではDocs、Authority、Mutation、Git／External、Evidenceおよび停止の通常Ruleに従い、Automation ModeではAccepted EnvelopeとRole Authority Matrixの交差内を自律実行する。Project責任者であること、進行責任またはTask編成Capabilityを、Envelope外の権限や自己免除の根拠にしない。

作業待機はRole削除を意味しない。次のHandoffがAcceptedされるまで、他担当は設計統括者役の再構築対象へ代理書込みしない。

## 17. GitHub Publication Sanitation Authority

GitHub公開用のIdentity／Privacy／Affiliation／不要Artifact検査は、[GitHub Publication Sanitation Policy](../operations/git_publication_sanitation_policy_ja.md)に従う。

## 18. Git Canonical Root／External Mutation

2026-08-04 JST以降、`margpa-runtime-llm`を開発内容とGit Metadataの両方を持つ単一Canonical Working Rootとする。旧Git Staging RootはBackup、Cutover PostflightおよびFull Test後にユーザー判断で退役済みである。

GitがCanonical Rootに存在しても、File Write AuthorityはCommit／Push Authorityを生成しない。

```text
Local File Edit:
  Accepted Scope内のWrite Authorityが必要

Commit:
  対象Diff／Message／Validationとユーザ明示承認が必要

Push:
  Outgoing Range／Sanitation／Remote／Target SHAとユーザ明示承認が必要

Branch／PR／Merge／Tag／Release／Remote／Visibility:
  それぞれ独立したExternal Mutation Authorityが必要
```

小規模・決定論的・全差分照合可能なDocs／Metadata変更では、[Git Workflow Policy](../operations/git_workflow_policy_ja.md)のRisk-based条件によりDirect `main`を候補にできる。これは作業者の独自判断または包括許可ではなく、当該Commit／Pushのユーザ明示承認を必須とする。

- 通常開発、通常Docs更新またはPhase途中Reviewごとに、同一目的の全Project Scan／Cleanupを定例実行しない。
- GitHub Push Preparation Gateで、Working Treeだけでなく全Push対象Commit TreeとMetadataを検査する。
- 検出Candidateの分類は設計統括者役が管理するが、削除、置換、History再構築、Repository削除・再作成およびPushの最終Authorityはユーザーにある。
- 対外Docs役、実装者役またはGit Operatorは、組織名という理由だけで第三者Attribution、License、Model配布元または技術Sourceを削除しない。
- `.gitignore`対象は原則としてGit追跡境界で除外し、元Projectからの物理削除へ自動拡張しない。
- Push対象SHAとScan結果をユーザーが確認するまでPushしない。

この時点限定は、Secret／Credential検出時のFail-closed、Research Asset Mutation ControlおよびProject Root外操作禁止の例外を作らない。

## 19. Phase専用Task／全RoleのFallibility Control

Phase 2以降は、Phase専用の設計担当者役Taskを原則配置する。実装者役についても、前PhaseのContext、未解決状態、Authority境界、Git／Worktree StateまたはTask Limitを持ち越すRiskがある場合、Phase専用の新規Taskを基本案とする。Phase 2の詳細は[Phase 2 Subphase／Task Orchestration Preplan](../operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)に従う。

同一Phase内では、Current State、Accepted Handoff、Write Scope、Open Finding、TestおよびMutation Inventoryを安全に解決できる間、同じ実装者Taskを継続利用できる。Context Limit、Service利用可能量、Status不備、Handoff混同、繰り返し失敗またはAuthority逸脱で安全な継続が困難な場合は、旧TaskのWriteを停止し、最終StatusとRecovery Evidenceを固定してから新Taskへ更新する。

すべてのRole、Task、AgentおよびToolは、誤解、Context欠落、自己判断の拡張またはToolの暗黙副作用により、権限外または運用ルール外のActionを取る可能性があるものとして設計する。本前提は設計統括者役にも例外なく適用する。

```text
Role Name
  ≠ Write Authority
  ≠ External Authority
  ≠ User Approval
  ≠ Compliance Guarantee
```

そのため、各Mutationは作業単位のAuthorization Envelope、Exact Target、Before、Proposed Diff、Stop ConditionおよびEvidence Contractで囲う。実装者StatusはCreated／Modified／Deletedを完全列挙し、Phase設計担当者役と設計統括者役は機能的な正しさだけでなくAuthority適合をReviewする。

権限逸脱または疑いを検出した場合、当該Taskは即時停止する。追加Mutation、無許可Rollback、自動修復、Evidence削除または別Taskによる隠蔽的継続を行わず、対象、Action、Before／After、復元可能性および必要User Decisionを報告する。

## 20. Resource Limit中断時のAuthority

Codex利用可能量、Credit、QuotaまたはService Limitは、任意のTaskを途中停止させうる。利用可能量不足は、未完了作業のAccepted化、Authority拡張、無許可の代替Model／Account／Service利用または追加課金を許可しない。

中断時は`PAUSED_RESOURCE_LIMIT`相当とし、最後に確認できたDocs、Source、Test、Working Tree、Open Finding、次の最小ActionおよびRecovery Pathを記録する。確認できない状態を推測で埋めない。再開または新Task作成は、Accepted Orchestration Envelopeまたはユーザーの追加指示の範囲内で行う。

## 21. プロジェクト責任者役

プロジェクト責任者役は、Phase 2以降のProject全体、Cross-Phase不変条件、Role編成、Phase Gate、RecoveryおよびFinal Reviewを調整する。設計統括者役を削除または吸収せず、技術設計／要件／Canonical Docs／Phase設計のRecoveryは引き続き設計統括者役が担う。

プロジェクト責任者役のStable入口とHistoryは次とする。

```text
docs/project/shared/project_responsibility_handoff/
  project_responsibility_handoff_ja.md
docs/project/shared/history/project_responsibility_handoff/
```

プロジェクト責任者役も、Human-defined Supreme RulesとAccepted EnvelopeのScopeに完全に従属する。Role名、Project全体責任、緊急性または自動化Pilotは、Envelope外のStanding Authorization、自己免除またはAuthority拡張を生成しない。通常運用の下位Defaultは、Automation ModeのAccepted Envelopeが置換した範囲で再適用しない。

プロジェクト責任者役のRecoveryは、自身の復元だけでなく、設計統括者役、Phase設計担当者役、実装者役および対外Docs役を正本Docsから再作成できることを完了条件とする。

### 21.1 当面の兼務構成

当面、現在Taskは`プロジェクト責任者兼設計統括者役`として両Roleを兼務する。独立Taskを増やして伝達段数だけを追加しない。ただしProject ResponsibilityとDesign Governanceの責務、Stable、HistoryおよびRecoveryは分離して相互参照し、兼務による情報圧縮、Authority合算または一方の退役を行わない。

自動化Pilotの正式Start Eventまでは現在Task名を変更しない。Accepted Automation Profile、Control TaskのReady宣言および後続User開始宣言が全て成立した直後に、Provider Capabilityが許す場合だけTask名を変更する。Human-private Recovery AssetはAI側の認識、EvidenceまたはActivation Gateにしない。Task名変更不能または不一致時は停止する。

兼務Roleを含む全Role、将来の上位Role、全Task、Agent、ToolおよびProviderは、明示されたAuthorized Root／Allowed Path外へ無許可で触れない最上位規則に従う。Automation Level、Phase ScopeまたはProject ScopeはFilesystem／External Scopeを拡張しない。
