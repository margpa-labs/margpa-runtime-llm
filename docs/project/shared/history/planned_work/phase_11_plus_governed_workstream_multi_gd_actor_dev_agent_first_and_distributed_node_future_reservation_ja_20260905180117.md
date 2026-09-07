# Phase 11以降予約 — Governed Workstream／Multi-GD Actor／Dev Agent先行／将来分散Node

```yaml
document_id: phase_11_plus_governed_workstream_multi_gd_actor_dev_agent_first_and_distributed_node_future_reservation_20260905180117
document_type: lossless_architecture_and_product_direction_reservation
document_state: agreed_direction_reserved_not_started
language: ja
recorded_at: 2026-09-05 18:01:17 JST
decision_authority: user
authority_owner: Nazuna Research
earliest_architecture_timing: phase_11_or_later
initial_product_surface: future_full_development_agent
later_product_surface: normal_conversation
phase_10_plan_changed: false
implementation_authorized_now: false
external_r_and_d_implementation_authorized_now: false
distributed_node_system_owned_by_this_project: false
append_only: true
```

## 1. 本記録の目的と会議範囲

本記録は、2026-09-05にNazuna ResearchとCodex Controllerの間で行った、将来のMARGPA Development Agent、18 Governance Definitions、Runtime Constitution、役割分業、可視化、Context Compaction、Multi-Model／Distributed AIおよび外部R&D分担に関する重要な設計会議を、後続Taskで再解釈・改変されないようLosslessに固定する。

発端となったUserの問いは次である。

> Phase 11以降で二つの構造レイヤーを作った後、開発エージェントを作る時、Codex、Claude、Copilotその他を役割ごとに分けた方が効率的ではないか。18GDを役割ごとに別Taskへ分けるのは面倒なので、ARGD、DAGD、Constitutionを共通TOP制御層とし、その下にCDOGD、戦略、承認／権限、監査、監査を監査するMeta-GDを上級制御層として必要時だけ起動し、残るDomain特化GDをCDOGDで回せないか。一つのCodex Taskに相当する単位の中で分業し、全GDとConstitutionが今何をしているかをいつでも見たい。

その後、次も合意・留保した。

- `Task`は作業単位とUI上の会話単位が混同される。
- `Session`はProvider接続やCompactionにより分断されるため、長期Identity名として不正確になり得る。
- `Thread`は会話系列としては近いが、通常Threadとの区別や内部Actor階層を表しにくい。
- 最上位のUser可視単位として`Governed Workstream`を採用候補とする。
- まず将来のFull Dev Agentで成立させ、完成後に通常Conversationへ応用する。
- 将来の理想はModel自体の分散・Node化だが、現時点の資金・Hardware・MVP Scopeでは実施しない。
- 同一Model Familyを複数Nodeへ使う場合、Nodeごとの個体特性を変える必要がある。その生成・分散統治はDLAGSA等の別R&D群の担当だったとのUser認識を記録する。

## 2. 今回の確定方向

将来の役割分業を、Provider製品側の「Task」「Session」「Subagent」を正本として設計しない。MARGPA側に一つの永続的な`Governed Workstream`を置き、その内部に役割ごとの論理Actor、Actor Run、Evidence、Artifact、Authority、BudgetおよびStateを持たせる。

```text
Persistent:
  Workstream Identity
  Actor Identity
  Event／Evidence Ledger
  Artifact Graph
  Frozen Authority／Budget／Requirement
  Checkpoint／Next Action

Ephemeral:
  Codex／Claude／Copilot／Local Model等の推論Worker
  Provider Session
  Model Context Projection
  Tool Process
```

**Actorの役割・状態は永続させるが、推論Workerは必要時だけ起動する。** SubagentやModel Processが一時的であること自体は問題ではない。一時Workerを役割Stateの唯一の保存場所にすることが問題である。

## 3. 実装時期と導入順序

本構想を現在のPhase 9-1またはPhase 10へ追加しない。導入順序は次を基本とする。

1. Phase 10 MVPを既定計画どおり優先する。
2. Phase 11以降、GD系の構造制御レイヤーを設計・実装する。
3. Phase 11以降、Runtime Constitutionの構造制御レイヤーを設計・実装する。
4. 二つの構造制御と、それぞれの意味評価レイヤーを独立Componentとして成立させる。
5. Future Full MARGPA Development Agentを最初の`Governed Workstream` Surfaceとして実装・検証する。
6. Dev AgentでActor分業、Authority、Audit、Repair、Evidence、Compaction耐性およびUI可視化を安定させる。
7. 同じEngineを汎用化し、通常Conversationへ`Conversation Workstream`として応用する。

現在存在するDev Agent Research Preview／Level 1 Harnessと、ここでいう将来のFull Multi-GD Development Agentを混同しない。前者の知見を利用するが、本記録だけで後者が成立済みとはしない。

## 4. Governed Workstreamの階層案

```text
Governed Workstream
│
├─ Core Governance Plane
│  ├─ ARGD／DAGD Governance Source
│  │   ├─ GD Structural Control
│  │   └─ GD Semantic Evaluation
│  └─ Runtime Constitution Source
│      ├─ Constitution Structural Control
│      └─ Constitution Semantic Evaluation
│
├─ Supervisory Control Plane
│  ├─ CDOGD   : 必要な役割を選択・起動・停止・接続
│  ├─ SPPGD   : 戦略・優先順位の構造を作成
│  ├─ DAAGD   : 決定権限・責任・承認要否・委譲境界を評価
│  ├─ SDAGD   : 戦略構造と権限評価を最終判断前に監査
│  └─ SDMRGD  : SDAGD自身の監査状態を必要時だけMeta-review
│
├─ Domain Actor Plane
│  ├─ AAGD／ACRGD／AIAGD／AIRGD／AISGD
│  ├─ DCAGD／DSGD／MPGD／OMRGD／PMOGD／SEGD
│  └─ CDOGDがManifest、Capability、Evidence、Scopeから必要なものだけ選択
│
├─ Repair／Review Plane
│  ├─ neutral Repair Request Port
│  ├─ Repair Actor／Provider
│  └─ Re-evaluation／Adoption／Rejection
│
└─ Evidence／State Ledger
   ├─ Workstream／Run／Actor／Step Event
   ├─ Authority／Approval／Budget／Deadline
   ├─ Input／Output／Artifact／Digest
   └─ Audit／Meta-audit／Repair／Presentation Outcome
```

ARGD、DAGD、Runtime Constitutionは共通TOP制御Sourceである。ここでいう「二つの構造レイヤー」は、GD Source側の構造制御とRuntime Constitution側の構造制御を指す。ただし、三者を一つの巨大Componentへ統合しない。各Sourceの存在／不在、ON／OFF、構造制御／意味評価を独立させ、Conflictは明示的な調停契約へ渡す。

## 5. 既存18GD分類との関係

Reference Bundleには、ARGD、DAGD、CDOGDおよび15 Domain Extensionの計18 Logical Definitionがある。現在のManifest上では、SPPGD、DAAGD、SDAGD、SDMRGDも`decision_pipelines`系Domain Extensionである。

今回の`Supervisory Control Plane`案は、Source Package上のAdapter ClassやDefinition分類を即時変更する決定ではない。**Dev AgentのWorkstream内で、これらを上級の論理Actorとして必要時にActivationするRuntime配置案**である。

正式名称と責任境界は次のとおり。

| ID | 正式名称 | Workstream内の役割 | 越えてはならない境界 |
|---|---|---|---|
| CDOGD | Cross-Domain Orchestration Governance Definition | Routing、Activation、Role Assignment、Handoff、Suppression、Repair伝播 | 最終判断、承認、説明内容、Domain固有判断を所有しない |
| SPPGD | Strategic Planning and Prioritization Governance Definition | 戦略、選択肢、優先順位、継続／停止等の構造化 | 権限を自己付与せず、監査や実装を代行しない |
| DAAGD | Decision Authority and Accountability Governance Definition | 誰が決めるか、責任主体、Human承認要否、AI委譲範囲を評価 | 判断内容や戦略を作らず、自己承認せず、最終判断を代替しない |
| SDAGD | Strategic Decision Audit Governance Definition | SPPGDの戦略構造とDAAGDの権限評価を監査 | 戦略を作り直さず、権限を再決定せず、SDMRGDを監査しない |
| SDMRGD | Strategic Decision Meta-Review Governance Definition | SDAGDの監査状態・逸脱・不安定性を必要時だけMeta-review | 全Systemの最高権限や最終判断者にならない |

PMOGDは名称にOrchestrationを含むが、Project Management and OrchestrationというDomain責任を持つ。全Domain横断Activationを所有するCDOGDと同一視しない。

## 6. 常駐させず、必要時だけ起動する

18GDすべてへ毎Turn Model Callを行う構造は採用しない。Quota、Latency、Memory、Failure Surfaceが不必要に増大し、役割分離の利益を失う。

構造制御可能な規則は可能な限りCompileしてRuntimeへ適用し、常駐LLMを要求しない。Semantic ActorはTrigger条件を満たす時だけ起動する。

```text
単純な実装:
  CDOGD routing + SEGD等の必要Domain Actor

戦略判断を含む:
  + SPPGD

権限／承認／委譲判断を含む:
  + DAAGD

高Impactな最終判断前:
  + SDAGD

SDAGDの監査品質が不安定／異議あり:
  + SDMRGD
```

CDOGD自身も常時推論し続けるModelではなく、Workstream開始、Scope変更、Conflict、Handoff、Failure、Repair伝播等のRouting Pointで起動できるActorとする。登録されているだけで各GDへAuthorityやActive状態を与えない。

複数Domain Actorの並列実行は、入力依存・Authority・Side Effectが分離できる場合だけ許可する。依存関係があるActorを見かけ上並列化し、古いEvidenceで判断させない。

## 7. ProviderとRoleを固定しない

Codex、Claude、Copilot、Local LLMその他は、GDそのものでも恒久的な役職でもなく、Actor Runを実行する交換可能なWorker Providerとして扱う。

```text
SPPGD Actor Run  ─> 今回はCodex
SEGD Actor Run   ─> 今回はClaude
SDAGD Actor Run  ─> 別ContextのCodex、Local Judgeまたは将来Node
```

後日Providerが変わっても、SPPGD／SEGD／SDAGDとしてのActor Identity、Input、Authority、EvidenceおよびOutcomeは継続する。同じModelを複数Roleへ使う場合も、RoleごとにFrozen Context、Tool Authority、Output ContractおよびEvidenceを分離する。

現在観測されたProviderの得手不得手をRoutingへ利用してよいが、「Claudeは永遠に実装兵」「Codexは常に最高責任者」のように製品名をArchitectureへHard-codeしない。

## 8. 「一つのCodex Taskだけで分業」の正確な意味

Userが望む「一つのTask」は、利用者が複数Task間の伝言役にならず、一つの画面から全体を追えるというUser Experienceを指す。全Actorが同じ会話Context、同じMutable Memory、同じAuthorityを共有することではない。

現在のCodex／Claude／Copilot標準UIだけに依存し、一つのProvider Task内部で役割を演じ分ける方式には限界がある。

- Subagentの内部進捗が常に完全表示されるとは限らない。
- Provider固有Compactionで前提が変形する。
- Role間の独立ContextとBlind Reviewを保証しにくい。
- Provider Session終了と役割State消失を混同しやすい。
- 全ActorのAuthority／Budget／Evidenceを共通形式で追いにくい。

したがって、MARGPA上では一つの`Governed Workstream`として見せつつ、裏側ではActorごとに独立したModel Call、Worker、ProcessまたはContext Projectionを利用できる構造にする。

## 9. 用語候補とIdentity境界

最上位の正式候補は`Governed Workstream`、UI短縮表示は`Workstream`とする。

| 用語 | 意味 | Compaction／Provider交代との関係 |
|---|---|---|
| Workstream | 一つの継続的な目的、Authority、ArtifactおよびEvidence系列 | 継続する |
| Thread | Userへ見える会話系列／Transcript | 分岐・追加され得る |
| Run | 一回の有界な計画・実行・停止／完了単位 | Workstream内に複数存在 |
| Actor Run | 一つのGD／RoleがFrozen Inputで行う実行 | Providerから独立したIdentityを持つ |
| Session | Provider、ModelまたはRuntimeとの一時接続期間 | 切断・再生成され得る |
| Step | Tool Call、評価、変更、Test等の最小Action | Run／Actor Runへ相関する |

`Task`はUser-facing名称として避ける候補とする。ただし外部Provider APIがTask／Threadと呼ぶIdentityはAdapterで保持し、MARGPAのWorkstream Identityと同一視しない。

## 10. Compactionを正本にしない

Conversation本文、Model Memory、Provider Session、Compaction Summaryは、Workstreamの正本ではない。次回Model Callへ渡すための一時的なContext Projectionである。

正本は次とする。

- Append-only Event／Evidence Ledger。
- Actor StateとState Transition。
- Frozen Requirement、Scope、Authority、Budget、Stop Condition。
- ArtifactとDigest、Before／After、採用／不採用。
- 未解決Finding、異議、Minority Opinion、次Action。
- User Decisionと、その時点で参照したEvidence。

Compaction後は正本から必要範囲を再投影し、Summaryの言い回しだけで理念、要件、順序、完了条件またはAuthorityを変えない。

## 11. 全GD／Constitution可視化

将来のDev Agent UIでは、SubagentのChatを個別に開かなくても、全Definition／Actorの状態を一つのWorkstream Panelから確認できるようにする。

まず`Definition`と`Actor Instance`を区別する。Definitionが登録されているだけなら「何かを実行中」と表示しない。実際にActivationされたInstanceだけがCurrent Actionを持つ。

表示State候補：

```text
UNREGISTERED / REGISTERED / DORMANT / ELIGIBLE
QUEUED / RUNNING / WAITING_FOR_INPUT
WAITING_FOR_APPROVAL / WAITING_FOR_PLATFORM_GATE
COMPLETED / FAILED / CANCELLED / SUPPRESSED / DEGRADED
```

各Actorについて最低限表示する候補：

- Definition／Actor／Actor Run Identity。
- 現在StateとCurrent Action。
- なぜ起動・抑制・停止されたか。
- Trigger元、Parent Run、入力Evidence。
- Executed Provider／Model／Runtime。
- Frozen Context／Definition／Constitution RevisionまたはDigest。
- Authority、Tool Permission、Approval Requirement。
- Token／Time／Call／Repair BudgetとDeadline。
- Input／Output Artifact、Finding、Recommendation。
- Handoff先、Repair返却先、次Action。
- Started／Updated／Completed、Failure Code／Reason。

Panel候補はActor Tree、Timeline、Evidence、Outputs、Authority／BudgetをProgressive Disclosureで分ける。情報を既存Settingsへ無制限に直書きしない。

## 12. Dev Agent先行と通常Conversationへの展開

最初の対象をDev Agentとする理由は、Plan、File、Tool Call、Side Effect、Approval、Test、Review、Handoff等を構造化しやすく、Actorの責務と正否を通常会話より検証しやすいためである。

```text
Development Workstream
  ├─ Plan／Strategy
  ├─ Authority／Approval
  ├─ Domain Design／Implementation
  ├─ Test／Audit／Meta-audit
  ├─ Repair／Rework
  └─ Evidence／Artifact／Closure Candidate
```

Workstream CoreをDev Agent専用Schemaへ固定しない。Dev Agent固有のFile、Tool、Test、Git、Approval等はSurface／Capability Adapterへ置く。

Dev Agent完成後、同じCoreへConversation Adapterを接続し、通常ThreadにもActor階層、構造Governance、Semantic Evaluation、Repair、Evidenceおよび可視化を応用する。通常Conversation対応をDev Agent初期完成条件へ混入させない。

## 13. 将来の分散AI／Node化

理想的には、一つの大規模Modelまたは一つのProviderへ全Roleを依存させず、複数Nodeへ判断・実行・検証を分散する。異なるModel Family／Provider／Runtimeで実用的な候補があれば、相関Failureを減らせる可能性がある。

しかし、費用、Hardware、Availability、能力、License、Context、Structured Output等を同時に満たす「ちょうどよい異種Model」が存在するとは限らない。現実にはDeepSeek Flash等の同一Base ModelをN Nodeへ配置する可能性もある。

同一Base Modelの複製は、可用性・Throughput・多数決には寄与しても、そのままでは同じ学習由来のBiasやFailureが相関する。その場合、User方針として**Nodeごとに個体特性そのものを変える**方向を採る。

個体特性を何で構成・生成・固定・評価するかは本記録で決定しない。異なるContext、Memory、Policy、Role、Sampling、Adapter、学習差分等は候補になり得るが、根拠なく実装方式を固定しない。「N個ある」という数だけで中立性をClaimしない。

目標となる性質は次である。

- Nodeごとの判断がBlind／独立に形成される。
- 同一Failureが全Nodeへ伝播しにくい。
- 少数意見を多数決で消さずEvidenceへ保持する。
- Arbitration自身も別Authorityと監査対象を持つ。
- Node停止・悪性出力・Byzantine的挙動を全体Failureへ直結させない。
- Provider、Model、Node、Role、Evidence Identityを区別する。

これは長期方向であり、現在のMac、資金、MVPで複数Model常駐や完全中立分散を要求しない。

## 14. AAGC／DLAGSA等の外部R&Dとの責任分界

User認識では、Nodeごとの個体特性、分散AI、Node Governanceおよびそれを成立させるSystemは、AAGC、DLAGSA等の別R&D群の担当である。特にDLAGSAは既存公開Concept上、Multi-Agent Governance、Distributed Accountability、Safety Assuranceを研究領域とする。

このリポジトリ内ではAAGCの正式名称・現行責務を確認できなかったため、AAGCの展開名やExact Ownershipを本記録で創作しない。将来接続時に、AAGC／DLAGSA各正本から再確認する。

MARGPA Runtime LLMは、それらの分散基盤そのものをCoreへ再実装しない。将来はNode Pool、External Governance Provider、Evidence Ledger等をPort／Adapter経由で受け入れる側とする。

```text
AAGC／DLAGSA等
  └─ Node生成／個体差／分散実行／分散統治／責任・安全保証

MARGPA Runtime LLM
  └─ Workstream、Actor Routing、Authority、Component接続、UI、Evidence投影
      + External Node／Governance／Ledger Port
```

外部R&Dが未接続、OFF、UnavailableまたはFailureでも、単一Node／単一ProviderによるMARGPA Core Runtimeを破壊しない。

## 15. 中立性に関するClaim境界

「完全に中立」は将来目標であり、現時点の成立Claimではない。異種Modelであっても共通Dataset、Provider Policy、Prompt、EvaluatorまたはArbitratorによる相関が残り得る。同一Base Modelの個体差も、独立性が実測されなければ見かけ上の多様性に留まる。

将来は少なくとも次を分けて評価する。

- Infrastructure分散。
- Provider／Runtime分散。
- Model Family分散。
- Context／Memory／Policy分散。
- Epistemic Independence。
- Failure Domain分離。
- Decision Authority分散。
- Evidence／Ledger分散または改竄耐性。

いずれか一つの成立をもって「完全中立」「完全分散」と表現しない。

## 16. 理念・全体設計の無断変更禁止

過去にCodex Controllerが、局所Reuse、短期効率、既存Docs、Testの通しやすさ等を優先し、Userが最初に定義したComponent完全疎結合というPlatform価値を、明示承認なしに密結合方向へ変形させたFailureがある。同様の変更を本構想で繰り返してはならない。

次は最上位不変条件として扱う。

1. Nazuna Researchが最終Decision Authorityである。
2. 全Component、GD、Constitution、Actor、Provider、Nodeは、存在／不在、ON／OFF、交換、Failureを許容する。
3. 特定Provider、Model、GD名または現在のUI都合をCoreへHard-codeしない。
4. User-visibleな一つのWorkstreamと、内部の一つの共有Context／Authorityを同一視しない。
5. CDOGDはRouting Authorityであり、最終判断・承認・Domain判断を吸収しない。
6. Supervisory Actorは必要時Activationとし、登録だけで常時実行しない。
7. Compaction Summary、Memory、Handoff、DocsはUser合意を変更するAuthorityを持たない。
8. Unit Test、既存実装、正本Docの記述を理由に、後の明示User決定を黙って上書きしない。
9. 「効率化」「Reuse」「安全側」「一般的設計」を理由に、理念、Scope、順序、AcceptanceをControllerが自己変更しない。
10. Dev Agent先行、通常Conversation後続、分散Nodeは外部R&D連携という今回の順序を無断変更しない。

## 17. 全体設計変更の必須手続き

将来、本記録と異なる方がよいと判断したController／Designer／Actorは、勝手に実装へ反映してはならない。変更前に次をUserへ提示する。

```text
1. 変更対象となる既存理念／不変条件／合意文
2. 提案するExact Delta
3. 変更が必要と考えるSource Evidence
4. 利点、欠点、Quota／時間／Migration Cost
5. Component独立性、Authority、UI、Evidenceへの影響
6. 既存実装・Roadmap・Acceptance・外部R&D境界への影響
7. 変更しない案を含む選択肢
8. Rollback／Recovery方法
9. Nazuna Researchの明示承認
```

矛盾するDocsを発見した場合、Controller判断で「正本に書いてあるから」と一方を採用しない。新旧日時、User発言、実装状態および矛盾を報告し、決定を求める。ログで十分な場合に大量Docs再読を強制せず、Docsも無視せず、Authorityと鮮度を区別する。

Combined Controller Roleが継続している間、設計者として提案した変更を、最高責任者役として自動承認しない。理念へ触れる変更は必ずUser Gateへ戻す。

## 18. Anti-pattern

- 18GDすべてを毎Turn常時推論させる。
- 一つのModel Callへ全Role Promptを詰め、役割分業成立とClaimする。
- Subagentの会話履歴を唯一のActor Stateにする。
- WorkstreamとProvider Thread／Sessionを一対一固定する。
- CDOGDが戦略、承認、監査、実装を吸収する。
- DAAGDを自動承認者として扱う。
- SDAGDが監査対象を書き換えてからPASSする。
- SDMRGDを無条件常駐の最高AI権限へ昇格する。
- Provider名をGD Roleへ恒久固定する。
- Compaction SummaryからRequirementを再生成し、User合意を欠落・変形させる。
- 多数決でMinority Findingを削除する。
- 同一ModelをN個起動しただけで中立・独立とClaimする。
- AAGC／DLAGSAの未確認仕様をMARGPA側で創作する。
- 将来の分散構想を理由にMVPを遅らせる。
- Dev Agentと通常Conversationを最初から同時実装し、検証Surfaceを拡散させる。

## 19. 将来Acceptance候補

1. 一つのWorkstream UIから全DefinitionとActor Instanceの状態を区別して確認できる。
2. DORMANTなGDはModel Call、Action、Evidenceを生成しない。
3. CDOGDはManifest／Capability／Evidenceから必要ActorだけをActivationする。
4. 同じProviderを複数Roleに使ってもContext、Authority、Output、Evidenceが混ざらない。
5. Provider交代・Session終了・Compaction後もWorkstream／Actor Identityが継続する。
6. Actorの現在作業、起動理由、Budget、Authority、Artifact、次Actionが表示される。
7. SPPGD、DAAGD、SDAGD、SDMRGDが互いの責務を代替しない。
8. Human Approvalが必要な判断をDAAGDまたは別Actorが自己承認しない。
9. Dev AgentのFile／Tool／Git固有機能を外してもWorkstream Coreが成立する。
10. Dev Agent成立後、Conversation Adapterを追加してもCore Schemaを全面改造しない。
11. 外部Node Pool未接続でも単一Providerで動作する。
12. 外部NodeのFailureがWorkstream全体を無条件に破壊しない。
13. 同一Model Nodeの個体差と実際の独立Failure率を別に評価する。
14. Arbitration結果だけでなくMinority Findingと根拠を保存する。
15. User承認なしの理念・全体Architecture変更をTestで検出またはReview Gateで停止できる。

## 20. 今回決めていないこと

- Phase 11以降の正確なSubphase、開始日、工数、Quota。
- Workstream、Run、Actor Runの最終Schema／Class／Database。
- Actorごとに使用するModel、Provider、Context Size、Sampling。
- 全Actorを別Process、別Machine、別Modelのどれで隔離するか。
- 18GDのSource Package分類そのものを変更するか。
- CDOGDの選択Algorithm、Priority Score、並列度。
- Nodeごとの個体特性を生成するAlgorithm。
- AAGCの正式名称・責務・接続Contract。
- DLAGSA側の具体実装、Consensus、Byzantine耐性、Node Ledger方式。
- 「完全中立」を満たす定量条件。
- Dev Agent Panelの最終Visual Design。
- 通常Conversationへの適用時期。
- 現在のCodex／Claude／Copilot Taskを即時再編すること。

## 21. 関連する既存記録との関係

- `governance_component_independence_repair_trigger_and_selene_deferral_reservation_ja_20260905171547.md`: Component独立性、構造／意味評価分離および中立Repair Portを前提として維持する。
- `phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md`: GD群とRuntime Constitutionの構造／意味評価レイヤー分離を維持する。
- `phase_8_margpa_dev_agent_level_1_important_gate_only_autonomy_harness_reservation_ja_20260830181055.md`: Dev AgentのEnvelope、Important Gate、State、Evidence設計を将来Workstreamへ接続する。
- `post_phase_10_codex_role_task_separation_evaluation_reservation_ja_20260905123935.md`: 現在のProject運用Task分離検討と、製品内Actor Architectureを混同しない。
- `docs/public/concept_ja.md`のExternal R&D Hook: DLAGSA等はMARGPA Coreへ密結合せず、Port／Event／Evidence Contractで接続する原則を維持する。

本記録は既存文書を上書きせず、今回の最新User決定を追加する。実装着手時は、古い局所設計を理由に本記録の理念・順序・境界を暗黙変更しない。

## 22. Current Disposition

```text
Architecture Direction       : AGREED AND RESERVED
Current Implementation       : NOT STARTED BY THIS RECORD
Phase 9-1 / Phase 10 Change  : NONE
First Full Surface           : FUTURE MARGPA DEVELOPMENT AGENT
Normal Conversation          : APPLY AFTER DEV AGENT STABILIZATION
Distributed Nodes            : FUTURE / EXTERNAL R&D COORDINATION
Final Decision Authority     : NAZUNA RESEARCH
Unauthorized Design Drift    : PROHIBITED
```
