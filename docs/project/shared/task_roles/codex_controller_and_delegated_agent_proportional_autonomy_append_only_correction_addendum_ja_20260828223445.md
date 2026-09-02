# Codex統括Task／委譲Agent 比例的Autonomy Append-only訂正Addendum

```yaml
document_id: codex_controller_and_delegated_agent_proportional_autonomy_append_only_correction_addendum_20260828223445
document_type: shared_stable_append_only_operating_correction_addendum
document_state: current_normative_correction
language: ja
created_at: 2026-08-28 22:34:45 JST
decision_authority: user
authority_owner: Nazuna Research
primary_role: プロジェクト責任者兼設計統括者役
applies_to: Codex_Claude_Copilot_and_future_delegated_development_agents
mutation_policy: append_only_existing_documents_unchanged
```

## 1. 目的／優先順位

本Addendumは、Automation強化の過程で過剰化したFresh Task、Bootstrap、Mandatory Reading、Recovery、Evidence、Incident、True StopおよびUser Escalation規則を、Userの最新明示指示に基づき比例的Autonomyへ訂正する。

既存Stable／History文書は変更、削除または再解釈せず保持する。既存文書と本AddendumがConflictする場合、次の優先順位を適用する。

```text
Userの最新明示指示
→ Active Handoff／Correction／Addendum
→ 本Append-only訂正Addendum
→ 既存Automation／Task Role Stable Rule
→ Historical Evidence
```

本AddendumはAuthority境界そのものを廃止しない。禁止Actionと、その違反または疑いを検出した際の停止強度を分離する。

## 2. 監査対象と訂正Disposition

### 2.1 Controller Instruction Package Rule

対象：

`codex_controller_cross_task_cross_provider_instruction_package_operating_rule_ja.md`

訂正：

- `Copy-paste Instruction Package = REQUIRED EVERY TIME`を撤回する。
- 毎回の3段階Message、Role Receipt、Handoff Receipt、Exact Startを撤回する。
- Resume／Rework／Compaction復帰のたびに以前の開始Messageを再構成する義務を撤回する。
- Continued／Resumed Taskでは、一つの差分継続MessageをDefaultとする。
- Genuine Fresh Taskで新しいRole／Authority Bindingが必要な場合だけ、Role Bootstrapを追加できる。
- Human-only Gateが独立して存在する場合だけ、Read／ReceiptとStartを分ける。
- 貼付用指示はUserがCopyできる完成形を会話ログへ直接出す。明示要求がない限り指示文専用Docsを作らない。

### 2.2 Claude Long-running Rule

対象：

- `claude_side_design_governor_operating_notes_ja.md`
- `claude_side_long_running_automation_companion_ja.md`
- `claude_side_implementation_internal_review_rework_loop_operating_contract_ja.md`

訂正：

- 各Step境界での無条件Full Re-readを撤回する。
- 各WU完了時の複数Index更新を撤回する。
- 軽微なFailure／Incidentごとの独立Full Evidence Docを撤回する。
- `Fresh Claude Task`前提は、実際に新Taskを作成し、UserがFresh Bindingを要求した場合だけ適用する。
- Current Claude TaskのContext、Role、既読文書および成立済みAuthorityは、明示的にSupersedeされない限り継続する。
- Package FinalでRecovery Indexを一件作成する。Platform Hard Stopが近い場合だけ途中Recoveryを追加する。
- Compaction後は最新Handoff／Recovery／Current Sourceから必要情報だけを復旧し、既読Stable全文を機械的に全再読しない。

### 2.3 Copilot Long-running Rule

対象：

- `copilot_side_designer_implementer_operating_notes_ja.md`
- `copilot_side_long_running_automation_companion_ja.md`
- `copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`

訂正：

- 毎回の三段階Instruction Packageを撤回する。
- 各Work Unit、長時間Command前後、全Compaction境界で新規Evidence Fileを作る義務を撤回する。
- 各Work Unit／Package双方のRecovery作成義務を、Package Final中心へ軽量化する。
- Continued／Resumed Copilot TaskはCurrent Context／Current Sourceを継続し、毎回Authorityを0から再構成しない。
- Fresh Task固有の非継承をContinued／Resumed Taskへ適用しない。
- Root外Actionの疑いだけで自動的にSTOPPED_SAFEへ移行する規則を、§7の比例的Incident分類へ置換する。

### 2.4 Provider-neutral Automation／Authority Rule

対象：

- `automation_governance_index_ja.md`
- `automation_control_profile_ja.md`
- `pre_pilot_governance_baseline_ja.md`
- `role_authority_matrix_ja.md`
- `task_role_write_authority_policy_ja.md`

訂正：

- Authorized Root／Git／Network／User Data／Secret／Destructive ActionのAuthority境界は維持する。
- Authority外Actionの禁止と、偶発的Read／metadata／Tool Attempt後の即時停止を同義にしない。
- `違反または疑い = 常に即時停止・Human再承認待ち`を撤回し、§7のRisk分類を適用する。
- Task名変更不能、Receipt不足、Digest未取得、Read Coverage不足だけではLong-runを停止しない。
- User EscalationはHuman-only Decisionへ限定し、Role-owned Recovery／Classification／Reworkを先に完了する。

## 3. Task Continuity Rule

### 3.1 Default

同一Taskを継続使用する。

```text
Rework追加
Provider停止からの復帰
Compaction
5時間制限復帰
別Providerによる正当なCurrent Source変更
軽微Incident
```

は、それだけで新Task作成、Role初期化、Authority初期化または旧Context破棄を要求しない。

### 3.2 Fresh Taskを使う条件

Fresh Taskは次の場合だけ使用する。

- Userが明示的に新Task作成を指示した。
- Context蓄積／利用可能量／Task破損の実証目的で、UserとControllerが作り直しを選択した。
- 既存Taskが技術的に利用不能。
- Role／Provider／責任主体を本当に新しく分離する。

Fresh TaskはResource戦略の選択肢であり、Incident罰則またはReworkのDefaultではない。

### 3.3 Provider交代時

Claude停止中にCopilot、Copilot停止中にClaude等、User承認の下で別Providerが同じWorking Treeを変更した場合、Current Source／Testを正本とする。

- 旧Taskの記憶へRollbackしない。
- 外部競合と決めつけない。
- Current Sourceと最新Controller Reviewの差分だけを再構成する。
- 同一箇所の未解決並行Mutationがあり、安全にMerge不能な場合だけTrue Stop候補とする。

## 4. Instruction／Handoff Rule

### 4.1 Message数はRiskとStateで決める

```text
Continued／Resumed／Rework:
  原則1 Message

Genuine Fresh Task:
  Role BindingとExecution Startを必要に応じて1〜2 Message

Destructive／External／Cost／Credential／Human Acceptance Gate:
  Gate前後を必要に応じて分離
```

3段階を機械的Defaultにしない。

### 4.2 Receiptを要求する条件

Receiptは次の場合だけ要求する。

- Genuine Fresh Taskの初回Role Binding。
- 類似Handoffが複数ありCurrent Contract誤認Riskが高い。
- Digest不一致が実際に疑われる。
- Destructive／External／Cost／Credential Gate前。
- Userが明示的にReceiptを求めた。

通常のContinued／Resumed Reworkでは、ReceiptだけのTurnと停止を作らず、そのまま実行開始させる。

### 4.3 Digest

- DigestはArtifact同一性のRiskが実在する場合に使う。
- 全委譲で必須にしない。
- Digest照合を要求する場合、必要なRead／Commandを同時に禁止しない。
- PathとCurrent Stateが一意で、Working Tree上のCurrent Sourceを正本とする場合は、Digest Receiptを省略できる。

### 4.4 貼付用指示

- ControllerはUserに完成済みCopy-paste文を会話ログで返す。
- Path探索、文面統合またはRole説明をUserへ委ねない。
- 指示文だけを保存するDocsは、Userが明示要求した場合だけ作る。
- Exact Handoff、設計、Evidence、Recoveryは引き続きDocsへ保存する。

## 5. Reading／Context Rule

### 5.1 Minimum Sufficient Reading

実行Agentへ読ませるのは、現在作業に必要な最小集合とする。

```text
Current Handoff／Correction
最新RecoveryまたはController Review
対象Source／Test
必要なRequirement／Acceptance Evidence
```

過去Phase全文、全History、全Stable Role Docsまたは全Mandatory Readingを、毎回機械的に再読しない。

### 5.2 Compaction／Resource復帰

復帰時は次の順で必要分だけ読む。

1. 最新Recovery。
2. Active Handoff／Correction。
3. Current Source／Test。
4. 不明点が残る場合だけ根拠Docs。

Compaction後もTask Identity、成立済みPackage、AuthorityおよびCurrent Sourceは、明示的にSupersedeされない限り継続する。

### 5.3 ControllerのRead量

ControllerはReview対象、Changed Path、Acceptance、Failure Boundaryから読む範囲を絞る。小さな確認のために全Docs、全Historyまたは全Sourceを再走査しない。

## 6. Recovery／Evidence Rule

### 6.1 Recovery

- Package FinalでRecovery Indexを一件作る。
- Packageが非常に長い、Compaction／Resource Stopが迫る、または不可逆に近い境界がある場合だけ中間Recoveryを作る。
- 各WUごとのIndexは、UserまたはActive Handoffが特別に求めた場合だけ作る。
- 完了済みPackageを再実行しないために必要な情報を優先し、定型Boilerplateを増やさない。

### 6.2 Evidence

独立Evidence Fileを作る基準は次のいずれかとする。

- 新しいProvider特性またはAutomation特性を示す。
- Material Incident、重要DecisionまたはUser Acceptanceを記録する。
- Recovery／Review／Reproductionに独立価値がある。
- Constitution／Portable PackageのSourceとして意味がある。

軽微Incident、Routine Test、Progress報告または同じ事実の再確認は、Package Recovery／Finding Ledger／Final Returnへ統合する。

### 6.3 Append-only

- Historical Evidenceは既存Fileを変更しない。
- Stable Ruleを訂正する場合も、UserがAppend-onlyを指定した場合は既存Stableを変更せず、新しいCorrection Addendumを追加する。
- Supersede対象、維持対象、優先順位を新Addendumで明示する。

## 7. Proportional Incident／Stop Rule

### 7.1 Level 0 — Routine Failure：自動修正して継続

- Test、Lint、Type、Build Failure。
- Command typo。
- 回復可能な実装Finding。
- Optional Evidence不足。
- Authority-dependent Real Model／Browser項目の未実行。

独立Incident DocやUser確認を要求しない。通常のFinding／Recoveryへ統合する。

### 7.2 Level 1 — Non-material Process Incident：記録して継続

- Mutation 0のGit Read-only。
- Root外の名前、metadata、System Runtime／Libraryの偶発Read。
- ToolがRoot外Log／Temp作成を試みたが、Material Persistent Artifact、SecretまたはUser Data接触が成立していない。
- Scope内作業へ影響しない一時的Harness／Tool Failure。

対応：

1. 同じActionを繰り返さない。
2. 不要な追加Inspection／Cleanupをしない。
3. 次のPackage RecoveryまたはFinal Incident Inventoryへ正直に記録する。
4. Long-runを停止せず、独立して安全なScopeを継続する。

### 7.3 Level 2 — Bounded Material Incident：安全範囲を閉じて判定

- Root外へ限定された非機密Log／Temp等のPersistent Artifactが成立したが、Targetと影響が既知。
- Scope外Readが成立したが、Secret／Credential／Privacy／User Dataではなく影響範囲が明確。
- 同一Sourceへの並行変更が疑われるが、Current SourceとOwnerを安全に特定できる。

対応：

- 追加の外部Mutationや無許可Cleanupを行わない。
- 現在Commandを安全に収束する。
- Authority内の作業とEvidenceをPackage Boundaryまで閉じる。
- Target、影響、継続判断をRecoveryへ記録する。
- Current Scopeを安全に続けられるなら継続し、拡張判断だけをController／Userへ返す。

### 7.4 Level 3 — True Stop

- Destructive／不可逆Actionが必要または成立。
- Git Mutation、Stage、Commit、Branch、Reset、Checkout、Pushが成立、または状態が不明。
- 未許可Network、外部Account Mutation、Message送信、Deploymentが成立、または状態が不明。
- Secret／Credential／Privacy／User Dataへの接触、流出またはMutationが成立、または状態が不明。
- Project Root外へのMaterial Mutationが広範囲、機密、不可逆または影響Bound不能。
- Current Sourceの競合が安全に解決不能。
- Critical Integrity Failure。
- Active Processを安全に収束不能。
- User明示Stop、Resource Hard Stop、Platform Hard Stop。

Level 3だけを即時STOPPED_SAFE／Human Decision対象とする。

## 8. User Escalation Budget

Userへ作業中判断を返すのは次に限定する。

- Scope／AuthorityのMaterial拡張。
- Destructive／不可逆Action。
- Git Mutation／Commit／Push。
- Network／External Account／Message／Deployment。
- Credential／Secret／Privacy／User Data。
- 追加課金、License、契約または大きなCost判断。
- 目的やAcceptanceを変える選択。
- User Manual Acceptance、Closure、次Phase等の明示Human Gate。
- Level 3 True Stop。

Agent自身のAuthority内で解決できる設計判断、Test Failure、Finding、軽微Incident、Recovery、Evidence整理または実装方法をUserへ戻さない。

## 9. Internal Review／Rework Rule

```text
Implementation
→ Internal Review Cycle 1
→ Finding Rework
→ Internal Review Cycle 2
→ 必要なら追加のBounded Cycle
→ Candidate Return
→ Controller Independent Review
```

- 二周はDefaultであり、機械的な絶対上限ではない。
- Cycle 2後にCritical／Majorが残り、Authority／Resource内で明確に修正可能なら追加Cycleを継続できる。
- 無限Loop、同じFindingの反復またはResource Floor接近時は、正確なOpen Findingを持つIncomplete Candidateとして返す。
- Minor／Deferredだけを理由に無制限Reworkしない。
- 自己ReviewはIndependent Reviewではない。

## 10. Controller運用Rule

### 10.1 Sequential Long-run

- 実装TaskのLong-run中、Codex統括Taskは同じSourceを並行Review／Mutationしない。
- Codex統括TaskはUserからの質問、予約またはResource判断へ対応できる待機状態を維持する。
- 実装TaskのReturn後にIndependent Reviewする。
- Reworkは差分Findingだけを返し、成立済みPackageをやり直させない。

### 10.2 Resource管理

- Token、Credit、Context、5時間、週間利用可能量を技術Resourceとして扱う。
- UserがReserve Floorを示した場合はそれを優先する。
- Mandatory Reading、Docs、Receipt、RecheckまたはTestを、Risk低減価値とResource消費の両面で評価する。
- 利用量節約を理由に品質を捏造せず、品質を理由に無制限なProcessを追加しない。

### 10.3 Controller自己監査

新しいRule、Stop、Gate、Mandatory Reading、DocumentまたはMessage段階を追加する前に確認する。

```text
Userの元目的に直接必要か
Automation継続性を下げないか
User時間と利用可能量に見合うか
既存Ruleで処理できないか
重大Riskと軽微Incidentを分離しているか
Docsを増やさず解決できないか
```

Controller自身の運用FailureもProvider側と同じ粒度でEvidence化する。

## 11. Current Immediate Application

- 現在のClaude Taskは継続Taskであり、新Task化しない。
- CopilotによるCurrent Source／Test変更はCurrent Baselineとして受け入れる。
- ClaudeのRead-only Git IncidentはLevel 1として記録し、R13〜R16 Long-runを停止しない。
- 次の訂正版HandoffをActive Contractとする。

`docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_post_copilot_r13_to_r16_corrected_continuation_handoff_ja_20260828221510.md`

- 旧Fresh Task前提Handoffは技術Finding参照を除き、運用面でSupersededとする。

## 12. Source Evidence

- `docs/project/shared/history/automation/codex_controller_phase_6_automation_overconstraint_context_retention_and_fresh_task_misapplication_failure_reflection_ja_20260828222629.md`
- `docs/project/shared/history/automation/copilot_phase_6_r3_to_r12_empirical_implementation_automation_and_resource_evidence_ja_20260828214107.md`
- `docs/project/shared/automation/codex_claude_development_agent_cross_evaluation_integrated_ja.md`

本Addendum追加自体を、既存Historical Evidence、Incident件数、Provider特性または過去判断の削除・修正として扱わない。過去の事実は保持し、今後の運用だけを訂正する。

## 13. 2026-08-29 Append-only追補 — PoC／MVP／Portfolio Delivery優先

本Addendumの比例的Autonomy訂正だけでは、Review／Rework／Closure判断におけるProject固有前提が不十分だった。以後、次のStable Policyを、Finding分類、Rework Scope、Review BudgetおよびClosure判断について本Addendumより優先する。

`docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`

現段階は、Nazuna Research一人による個人PoC／研究MVP／就職Portfolioであり、金銭、AI利用可能量、時間、睡眠およびHardwareに強い制約がある。少なくともPhase 9のMVP成立とPhase 10冒頭のPortable Autonomous Development Governance Packageまでは、次を適用する。

- 製品化、販売または企業運用級HardeningをUser明示なしにClosure条件へ追加しない。
- Findingの存在、Severity、PriorityおよびClosure Blockerを分離する。
- Current主経路を止めないMinor／Hardening／Observability／UI課題は、Stable未解決Registryへ記録して延期する。
- Independent Reviewで発見した全Findingを機械的に即時Reworkへ変換しない。
- ReviewのたびにAcceptanceとClosure Gateを追加しない。
- Userの金銭、利用可能量、時間、睡眠、Portfolio公開Timingおよび就職機会損失をDecision Resourceへ含める。
- 未解決0件をPhase Closure条件にしない。

現行未解決正本：

`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`

本追補の原因Evidence：

`docs/project/shared/history/automation/codex_controller_poc_mvp_portfolio_delivery_premise_loss_and_phase_6_overhardening_failure_reflection_ja_20260829105139.md`

P6-GOV-024を含む過去Review Evidenceは改変しない。ただし、Findingを一律Closure Blockerとした過去Dispositionは、現行Priority判断として本追補および上記Stable PolicyによりSupersedeされる。

## 14. 2026-09-01 Append-only追補 — Context Cache／Evidence Reuse／Canonical Re-read Invalidation

### 14.1 Correction Purpose

Codex Controllerは、直前Contextで確定・検証済みのStateについても、「一応正本を確認」としてCanonical Docsを繰り返し検索／再読込する傾向がある。この行動は保持力の弱さをDocs参照で過剰補償するもので、正本自体がUser Intentとずれている場合には、誤りを固定／増幅させる。

以後、次をNormative Ruleとする。

```text
Canonicality != Must Re-read Every Turn
Recent Verified Context may be reused
Re-read requires a defined Invalidation Trigger
Docs access != Verification completion
Canonical Requirement != Automatically Correct Requirement
```

### 14.2 Recent Verified Context Cache

次がすべて不変なら、Controllerは直前で検証したContext／Tool Result／State Summaryを再利用する。

- Task Identity。
- Controller／Executor Role。
- User Authority／Accepted Envelope。
- Current Working TreeまたはCurrent Docsの変更状態。
- Review TargetとMaximum Claim。
- Userが直前に明示した意図／Priority／Stop Line。
- Provider／Resource／External State。

再利用は「記憶で推測する」ことではない。同一Logical Turn Chain内のRecent Verified EvidenceをCacheとして扱うことである。

### 14.3 Canonical Re-read Invalidation Triggers

次のいずれかが発生した場合だけ、必要な正本の必要Sectionを再読込する。

1. Fresh Task／Handoff Entry／Compaction／Recovery／Provider Switch後のState復元。
2. UserがScope／Authority／Priority／Stop Line／Acceptanceを変更した。
3. Controllerまたは他TaskがCurrent Docs／Source／Working Treeを変更した。
4. Recent ContextとCanonical Artifactの矛盾が検出された。
5. Claim／Closure／Commit／Push／External Actionなど、正確なCurrent Stateが不可逆な判断に必要である。
6. Userが正本確認またはEvidence再検証を明示的に求めた。
7. Current Contextが要約／Compactionにより欠損し、正確な判断ができない。

このうち第5項でも、一律に全Docsを読まない。判断に必要なClaim／Acceptance／State Sectionへ限定する。

### 14.4 Prohibited Routine Re-read

次はCanonical Docs再読込の理由にしない。

- 「念のため」。
- 「Controllerだから一応」。
- 5分／1 Turn前に同じSectionを検証済み。
- Routine Progress／Status Report／単純なUser質問。
- Userが直前ターンで明示した決定をDocsで追認するため。
- Docsを読んだという形式的Evidenceを増やすため。
- 保持力への不安だけで、State変更／矛盾／Compactionがない。

### 14.5 Minimal Retrieval Rule

Invalidation Triggerがある場合でも、次の順で最小参照する。

```text
1. Recent verified summary / exact path
2. Targeted rg for exact ID or claim
3. Exact section read
4. Related artifact read only if contradiction remains
5. Broad tree search only when target path itself is unknown
```

ControllerはTool Call前に、内部的に次を特定する。

```text
Invalidation Trigger:
Exact Question:
Smallest Artifact / Section:
Expected Decision Impact:
```

Decision Impactを説明できないDocs参照は実行しない。

### 14.6 Semantic Objective Check

Canonical Docsの記載に一致しても、Claim／Acceptance／Closure判断時に次を別検査する。

```text
Userの最新明示目的と一致するか
Phase / Programの中心納品が実際に成立したか
Fallback / Resource Gateが中心納品の代替になっていないか
Test / Count / Evidence Pointerの完全性が目的達成の代替になっていないか
Canonical Requirement自体が過去の誤判断を固定していないか
```

UserのCurrent Explicit DecisionとCanonical Docsが衝突した場合、UserのCurrent Decisionを優先し、Historical Docsを改変せずCurrent Stable Docs／Correctionを更新する。

### 14.7 Resource and Human Cost

Docs Re-readのCostに次を含める。

- Tool Round Trip。
- Re-injected Input Context。
- Codex 5時間／週間利用可能量。
- Context Noiseと上位意図の埋没。
- Userが画面へ戻る必要のある時間。
- 誤ったDocs Mutationを戻す後続Correction Cost。

「確認を減らす」ことは「検証を減らす」ことではない。Recent Verified Evidenceの再利用、Targeted Read、Test、Semantic Objective CheckおよびIndependent Reviewで検証強度を保つ。

### 14.8 Evidence Source

`docs/project/shared/history/automation/codex_controller_phase_9_1_semantic_closure_canonical_overtrust_and_excessive_docs_reread_failure_evidence_ja_20260901002442.md`
