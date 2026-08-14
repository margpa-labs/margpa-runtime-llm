# Phase 2 Subphase／Task Orchestration Preplan

```yaml
document_id: phase_2_subphase_and_task_orchestration_preplan
status: active_phase_2_preplan
normative: false
language: ja
created_at: 2026-08-02 22:17:49 JST
updated_at: 2026-08-04 11:17:44 JST
owner: 設計統括者役
target_phase: phase_2
selected_pilot: document_driven_codex_task_orchestration
rag_default: true
```

## 1. 位置付け

本書は、Phase 2 `Conversation Continuity and Experimental Control Surface`を、細かすぎず大きすぎないSubphaseへ分割し、設計統括者役、Phase 2設計担当者役およびPhase 2実装者役がDocument-drivenで連携するためのPreplanである。

Phase 2はユーザー確認により開始済みであり、現在はPhase 2-0 Automation Pilotの設計Review待ちである。Phase 2開始は、Phase 2設計担当者役Taskの作成、Pilot実行、Source変更または元来のPhase 2-A機能実装を自動許可しない。Phase 2設計担当者役は、Accepted Authorization Envelopeと明示的Task作成指示が成立した後に限り、本PreplanをSourceとして、Phase目標、Cross-Phase不変条件およびUser Requirementを変えない範囲で局所設計を再調整できる。

## 2. Phase 2の完了目標

```text
Phase 1の一時的Web Preview
  → 永続Conversation
  → 明示的なConfiguration Control Surface
  → 一般利用者と研究／開発者向け設定の分離
  → Component Registry／Switchboardの基礎
  → Sourceを保持したDocumentation RAG Follow-up
```

Phase 2 Milestoneは`Persistent Chat and Explicit Runtime Composition`とする。

## 3. Subphase構成

### Phase 2-0 — Orchestration Pilot Design／Bootstrap

目的：

- 元来のPhase 2機能設計・実装へ入る前に、Document-driven Orchestration PilotのRequirements、Capability Contract、Authorization Envelope、Cost／Stop、RecoveryおよびAcceptanceを確定する。
- 現設計統括者役をProject責任者とし、Project全体、Cross-Phase不変条件、Task編成、最終ReviewおよびRecoveryの責任境界を明記する。
- Envelopeで許可された範囲に限り、必要なTask作成、Task名設定、Authority設定、Handoff、Status、Follow-upおよびReviewを実際に一往復以上行う。
- 最初の一つの有界なWork Unitを対象に`GO／ADJUST／STOP`を判定する。

主な完了条件：

- User Authorityを維持したAuthorization EnvelopeがAcceptedである。
- 新TaskがDocsだけからRole、Scope、Current State、禁止事項および停止条件を復元できる。
- Task間の往復、Review、PauseおよびRecovery Evidenceを追跡できる。
- 権限外Mutation、同時Write、未承認External Actionまたは未完了状態のComplete表記がない。
- 元来のPhase 2-Aへ進めるか、Pilot設計を調整／停止するかをEvidence付きで判断できる。

初回候補Work Unitは`P2-0-WU-001 Docs-only Recovery and Authority Acknowledgement`である。独立したPhase 2設計担当者役Taskを最大1件だけ作成し、File／Git／External／Secret／Sub-agent Authorityを与えず、正本DocsだけからProject StateとAuthorityを復元できるかを評価する案である。現時点ではDraftであり、Taskは作成していない。

設計Package：

- [Phase 2-0 Pilot Requirements](../../phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md)
- [Phase 2-0 Pilot Architecture](../../phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md)
- [Phase 2-0 Authorization Envelope Draft](../../phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md)
- [Phase 2-0 Execution Plan](../../phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md)
- [Phase 2-0 Phase Designer Bootstrap Handoff Draft](../../phases/phase_2/handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md)

### Phase 2-A — Phase Contract／Conversation Domain Foundation

目的：

- Phase 2のRequirements、Architecture、ADR、Acceptance、Migration／Rollback境界を確定する。
- Session／Turn／Message IdentityとConversation StateのDomain Contractを確定する。
- Storage Adapter境界、Schema Version、不変条件、Failure ContractおよびPhase 1 Compatibilityを確定する。
- Phase 2 Index、Subphase Handoff、History IndexおよびTask Authorityを成立させる。

主な完了条件：

- IdentityおよびPersistence ContractがTest可能である。
- Browser MemoryだけのPhase 1動作からの移行境界が明示される。
- 2-B以降が未確定の暗黙仕様に依存しない。

### Phase 2-B — Conversation Persistence／Lifecycle Services

目的：

- Conversation、Session、TurnおよびMessageの保存／取得／一覧／再開Contractを実装する。
- New Chat、Resume、History、RegenerateおよびBranch候補のApplication Service境界を作る。
- Generation Stop、Error Recovery、中途StateおよびModel ReloadとChat Actionの分離を成立させる。
- Corruption、Version不一致、存在しないConversationおよび部分FailureをFail-closedで扱う。

主な完了条件：

- Process／Browser Reload後もAccepted Contractに従いConversationを再開できる。
- Storage実装をWeb UIへハードコードしない。
- Raw Thinking非保存等のPhase 1不変条件を保持する。

### Phase 2-C — Conversation Application UX

目的：

- Chat List、History、New Chat、Resume、削除候補、RegenerateおよびBranch候補をUI／API境界へ接続する。
- Streaming、Stop、Error、ReconnectおよびModel Busyの状態表示を永続Conversationと整合させる。
- Model Reloadを必要とするActionとChat内で完結するActionを分離する。
- Phase 4以降の本格UIおよび後続Responsive対応を妨げないComponent／CSS／API Boundaryを保持する。

主な完了条件：

- 永続・再開・停止・再送信の一連のUser Flowが破綻しない。
- UIがStorage、Model Backendまたは将来Governance実装に直接依存しない。
- BrowserとServerの責任境界が明示される。

### Phase 2-D — Configuration Control Surface／Research Developer Mode

目的：

- 一般利用者向け設定と研究／開発者向け高度設定を分離する。
- `研究・開発者モード OFF／ON`で設定入口の表示を切り替える。
- Config Schema Validation、Effective Config、Source、Diff、Apply Resultを扱う。
- Runtime中に変更できる設定とRestartが必要な設定を分離する。
- SecretをUI、Tracked Config、LogまたはAudit Detailへ書かない。

主な完了条件：

- 研究／開発者モードが権限昇格、Policy解除または安全機構の一括無効化にならない。
- Clientが送る未許可設定をServer側で拒否できる。
- 表示の有無とSecurity Boundaryを混同しない。

### Phase 2-E — Runtime Composition Switchboard／RAG Follow-up

目的：

- Functional Component Descriptor、`enabled`、Dependency、Conflict、Capability、Degraded Mode、Side Effect LevelおよびApply Timingの基礎を作る。
- 将来Governance Bindingの`off／observe／enforce`を収容できるが、Phase 2でFull Governance Runtimeを先行実装しない。
- `Agent OFF + Agent Governance ON`等の無意味または危険な組み合わせを黙って受理しない。
- Phase 1-ex Documentation RAGを、Sourceを保持したMulti-turn Follow-upへ拡張する。
- RAG Adapter成立と回答精度保証を引き続き分離する。

主な完了条件：

- Componentの存在、登録、有効化、権限、承認および実行を混同しない。
- RAG Follow-upがSource／Citation／Unavailable境界を維持する。
- 後続Phase 3以降のGovernance／EvidenceとPhase 7のFull RAGへ差替え可能である。

### Phase 2-F — Cross-environment Acceptance／Phase Closure

目的：

- Mac Localを主要開発環境、Lightningを外部互換／公開Surfaceとして有界に再検証する。
- Unit／Integration／Static／Manual／Lifecycle／Security／Privacy Testを閉じる。
- Conversation Migration、Config復元、Stop／Restart、Runtime SnapshotおよびRollbackを検証する。
- [Phase Completion Review／Backup Gate](phase_completion_review_and_backup_gate_ja.md)に従い、Phase 2全体のFinal Check、Finding解決、必要なFollow-up／再Reviewを閉じる。
- Phase 2 Lossless Compilation、Current／Shared／Public更新、Recovery Manifest、Final Review、User Acceptance、明示的なBackup通知およびBackup検証を完了する。
- Document-driven Orchestration Pilotの成否を評価する。

主な完了条件：

- Phase 2 Milestoneと受入条件がEvidence付きでAcceptedできる。
- Phase 3以降に同じSubphase／Task運用を拡張できるかGo／Adjust／Stopを判定できる。
- 原則としてPhase 2のFindingを全て解決し、例外延期は共通Gateの条件とユーザーの明示承認を必須とする。
- User AcceptanceとBackupなしにPhase 2完了宣言またはPhase 3移行を行わない。

## 4. Subphase依存順

```text
2-0 Orchestration Pilot Design／Bootstrap
  → 2-A Phase Contract／Domain Foundation
  → 2-B Persistence／Lifecycle Services
  → 2-C Conversation Application UX
  → 2-D Configuration Control Surface
  → 2-E Runtime Composition／RAG Follow-up
  → 2-F Cross-environment Acceptance／Closure
```

2-Cと2-Dの一部は設計上並行検討できるが、同一Working TreeへのWrite-heavy実装は原則直列とする。2-Eは2-AのComponent境界と2-DのConfig Contractに依存する。2-Fは未Accepted Subphaseを隠して閉じない。

## 5. Subphase共通Gate

各Subphaseは原則次の順序で進める。

```text
設計統括者役:
  Project責任者としてCross-Phase Scope／Authority／不変条件を固定
  必要Task、Task名、Authority、Handoff、Follow-up、ReviewおよびRecoveryを管理

Phase 2設計担当者役:
  Subphase Requirements／Architecture／ADR／Acceptance／Handoffを作成

設計統括者役:
  実装開始前Review／Accepted Handoff

Phase 2実装者役:
  Accepted Scope内のSource／Tests／Scripts／許可Configを実装
  Implementer Status／Test Evidence／Mutation Inventoryを返却

Phase 2設計担当者役:
  Phase-local適合Review／Follow-up案

設計統括者役:
  Cross-Phase／Authority／Final Subphase Review
  Accepted／Follow-up／Rejected／Pausedを確定
```

External UI、User-visible Behavior、Backup、Git／GitHub、公開、Secret、課金環境およびPhase移行はユーザーGateを維持する。

設計統括者役のProject責任はUser Authorityを代替しない。Envelope外のTask作成、Task名変更、Write Scope拡張、External Mutation、Git操作またはPhase移行は、Project責任者の独断で実行しない。

## 6. Phase Orchestration Authorization Envelope

Phase 2開始時に、ユーザーは一度の明示承認で、事前に列挙されたTaskとRoutine Handoffを含む`Phase Orchestration Authorization Envelope`をAcceptedできる。

必須項目：

```text
Phase
Allowed Task Role／Task Name
Maximum Active Task Count
Maximum Replacement Task Count
Working Tree／Worktree Boundary
Read／Write Authority
Subphase Scope
Creation Timing
Cost／Usage Stop Condition
Human Authority Gate
External／Git／Secret／Destructive Boundary
Status／Review／Recovery Path
Envelope Expiration
```

Envelopeの明示承認後は、その内部の通常Handoff、Status取得、Review、Follow-upおよび事前承認済みTask作成を設計統括者役が連結できる。ただし、Envelopeは無制限のTask作成、自動の外部操作、権限拡張またはUser Gate省略を許可しない。未列挙Task、代替Role、上限超過またはScope拡張は改めてユーザー承認を必要とする。

## 7. Task構成と実装者更新

Phase 2の初期構成は次を推奨する。

```text
設計統括者役          : 現Taskを継続。Project／Cross-Phase／Final Review。
Phase 2設計担当者役     : Phase 2専用の新規独立Task。
Phase 2実装者役         : Phase 2専用の新規独立Taskを基本案とする。
```

Phase 1の実装者Taskを自動継続するのではなく、Phase 2開始時のContext、未解決状態、Write Scope、Git／Worktree状態および復元性を評価する。Phase 2専用の新実装者Taskは、旧Contextの汚染を持ち越さず、Phase 2 Index／Handoff／Current／Sharedから復元できることを確かめるPilotの一部とする。

同一Phase 2実装者Taskは、次の条件を満たす間は2-A～2-Fで継続利用できる。

- Current Scope、Accepted Handoff、Working TreeおよびOpen Findingを正確に解決できる。
- Context LimitまたはService利用可能量が安全な完了を妨げていない。
- Authority逸脱、重複実装、古いHandoffの混同または繰り返した誤修復がない。
- StatusとMutation Inventoryが完全で、新Taskに置き換えてもDocsから復元できる。

次のいずれかで実装者Task更新を検討する。

- Context Limit／Task不安定化／Service制限が近い。
- Accepted ScopeまたはArchitectureが大きく切り替わる。
- 権限逸脱または無許可Mutationの疑いがある。
- Status／Evidence不足によりCurrent Stateを安全に復元できない。
- 同じ原因のFollow-up失敗またはHandoff誤読が繰り返される。
- Phaseが完了し、次PhaseでContext分離の便益が高い。

更新時は旧TaskのWriteを停止し、最終Status、Files Changed、Test、Open Finding、Git／External StateおよびRecovery Pathを固定してから新Taskを開始する。旧新Taskを同一Working Treeへ同時Writeさせない。

## 8. 利用可能量／Credit中断前提

Codexの利用可能量、Model利用限度、Cloud Creditまたは外部Serviceの残量により、任意のSubphase途中で作業が停止する可能性を正常な運用前提とする。

- 利用可能量を取得できない場合、十分な残量があると推測しない。
- 大きなSubphaseまたは新規Taskを開始する前に、取得可能な範囲でUsage／Credit／Timeを確認する。
- Limit、Quota、CreditまたはService拒否を検出したら、自動で代替Model、追加課金、別Account、別Serviceまたは大量の代替Taskへ切り替えない。
- 完了していない作業を、残量不足を理由にAcceptedまたはCompleteと表記しない。
- 状態を`PAUSED_RESOURCE_LIMIT`相当とし、最後に確認済みのDocs、Source、Test、Working Tree、Open Finding、次の最小Actionおよび必要Authorityを記録する。
- Task側がStatusを書けない状態で停止した場合、設計統括者役は既存Evidenceから確認できる範囲だけをRecovery Recordに固定し、未確認状態を作り話で埋めない。

Resource LimitによるPauseはProject Failureとは限らないが、Recovery Evidenceがなければ次Taskへの安全な引継ぎを行わない。

## 9. 全Role／全Taskの権限逸脱前提

設計統括者役を含むすべてのRole、Task、AgentおよびToolは、誤解、Context欠落、自己判断の拡張またはToolの暗黙副作用により、権限外または運用ルール外のActionを取る可能性があるものとして設計する。Role名、上位責任、長期の成功実績またはTool Permissionを、権限遵守の保証とみなさない。Project責任者も絶対禁止事項、Docs規則、Authority規則その他の運用ルールの例外ではなく、自己判断で規則またはAuthorityを上書きできない。承認・確認待ちによる停止はこの制約と矛盾しない。

全TaskはMutation前に、少なくとも次を解決する。

```text
Current Role／Phase／Subphase
Accepted Handoff
Read／Write Scope
Exact Target
Project Root／Worktree
Prohibited Actions
Before State
User Gate
Expected Diff／Test／Evidence
Stop／Rollback／Escalation
```

構造的な対策：

- Task開始時にAuthority Acknowledgementを必須にする。
- HandoffはAllowedとProhibitedの両方を明記する。
- 実装StatusはCreated／Modified／Deletedを完全列挙する。
- Reviewでは成果の機能だけでなく、変更Path、Git／External StateおよびAuthority適合を検査する。
- 設計統括者役も自身のAuthorityを自己拡張せず、User Explicit InstructionとShared Ruleに従う。
- 委譲先の権限を委譲元の権限から自動導出しない。
- 権限逸脱またはその疑いを検出したら即時停止し、追加Mutation、無許可Rollback、自動修復または証跡削除を行わない。
- 逸脱後は対象、Action、Before／After、復元可能性、未確認範囲および必要User Decisionを報告する。

本前提は「信頼しないから分業しない」ことを意味しない。各Roleの専門性を使いつつ、存在、役割、権限、承認、実行および責任を混同しないためのDefense-in-depthである。

## 10. Phase 3以降への展開Gate

Phase 3～Phase 9を同様に`Phase <N>-A`等へ分割するのは、Phase 2-FでPilot結果を評価した後とする。Phase 2を成立性検証とし、結果が`GO`または条件付き`ADJUST`としてAcceptedされた場合は、Phase 3でもPilotを継続して再現性・移植性を検証する。次Phaseごとに、粒度、Task数、実装者更新条件、Cost、権限逸脱、RecoveryおよびReview工数を再評価し、黙って横展開しない。

Phase 10以降はExternal Original R&D Integration等の特殊性が高いため、現時点の横展開対象から除外し、後続設計で別途分解する。

### 10.1 Orchestration粒度の拡張

Phase 2-0では一つの有界なWork Unitから開始する。安定性を確認できた場合だけ、複数Unit、Subphase、Phase完了単位へ拡張する。複数PhaseをまたぐProject完了単位は長期目標とし、Phase 2 Pilotだけで自動承認しない。

```text
Bounded Work Unit
  → Connected Work Units
  → Subphase
  → Phase Completion
  → Project Completion
```

粒度変更ごとにAuthority、Cost、Conflict、Recovery、Review Quality、Task ReplacementおよびUser Gateを再評価する。

Phase 3では、Phase 2と異なるRequirements、Task Context、Evidence Domainおよび実装対象でも、同じDocument-driven Control Plane、Authority Envelope、Handoff、Review、StopおよびRecoveryが成立するかを確認する。Phase 2成功はPhase 3の無条件自動実行Authorityを生成せず、Phase 3開始GateとEnvelopeを別途Acceptedする。

### 10.2 Long-running Orchestration Target

ユーザーがAccepted Orchestration Envelopeの範囲内で「じゃ、あとよろしく」と委任した場合、次のユーザー確認時までに、1 Subphase、1 Follow-up、1 Review Packageまたは同等の有界なWork Unitを、完了、Review待ちまたはEvidence付きの安全なPauseへ到達させることを目標とする。夜間委任から翌朝までに一つの仕事が明確に進んでいる状態を目指すが、時間保証、User Gateの代行、未検証の完了表記またはAuthority越境を許可しない。

Codex利用可能量、Credit、Service Limit、User Decision、Manual Test、External Service、BackupまたはAuthorityにより完了できない場合は、最後の確認済み状態、Test、Open Finding、停止理由、次の最小Actionおよび必要Authorityを残す。

## 11. Phase 2 Pilot Acceptance

Subphase分割とTask OrchestrationのPilotは、次を満たした場合に限りPhase 3以降への展開候補とする。

- Subphase間の責任と依存が明確で、過度な細分化または巨大Handoffを発生させなかった。
- 設計統括者役、Phase 2設計担当者役および実装者役がDocsだけからCurrent Stateを復元できた。
- Routine Handoff／Reviewの自動連結がUser Authorityを弱化しなかった。
- 権限外Mutation、同時Write、証跡欠落または未承認のExternal／Git Actionがなかった。
- Resource Limitで停止しても、完了状態を偽装せず再開できた。
- Task分離が再説明Cost／Context Pollutionを減らし、利用可能量に対して合理的な便益を持った。
- Phase 2 Final ReviewとUser Acceptanceで`GO／ADJUST／STOP`を判定できた。
- 成功、Incident、Near MissおよびHuman Interventionが、`RULE_EFFECTIVE`、`RULE_AMBIGUOUS`、`RULE_MISSING`、`RULE_OVERRESTRICTIVE`、`RULE_UNENFORCEABLE`、`HUMAN_GATE_REQUIRED`または`AUTOMATION_CANDIDATE`へ分類された。
- Phase 3で再現性・移植性を検証する場合の対象、粒度、Authority、StopおよびAcceptanceを説明できた。

## 12. Related Documents

- [Experimental Document-driven Codex Task Orchestration](experimental_document_driven_codex_task_orchestration_ja.md)
- [Task Execution Routing／Cost Control](task_execution_routing_and_cost_control_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
- [Phase Completion Review／Backup Gate](phase_completion_review_and_backup_gate_ja.md)
- [Research Asset Mutation Control](research_asset_mutation_control_ja.md)
- [Cross-project Development Governance Constitution Plan](cross_project_development_governance_constitution_plan_ja.md)
- [Public Roadmap](../../../public/roadmap_ja.md)
