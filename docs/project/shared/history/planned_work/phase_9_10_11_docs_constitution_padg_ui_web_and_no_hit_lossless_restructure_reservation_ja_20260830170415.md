# Phase 9／10／11 Docs・Constitution・PADG・UI・Web・NO_HIT Lossless再編予約

```yaml
document_id: phase_9_10_11_docs_constitution_padg_ui_web_and_no_hit_lossless_restructure_reservation_20260830170415
document_type: append_only_planned_work_lossless_restructure_reservation
document_state: reserved_not_started
language: ja
created_at: 2026-08-30 17:04:15 JST
decision_authority: user
authority_owner: Nazuna Research
current_phase: phase_7_closure_preparation
implementation_authority: false
phase_transition_authority: false
network_authority: false
git_authority: false
```

## 1. 目的

本書は、Phase 7実画面確認中に確定した次の判断を、一部だけ切り取らずLosslessに統合する。

- Phase 9へ残す技術Coreと、Phase 10後半へ移すUI再編を分離する。
- Phase 6特殊最小Closureで残した中心Debtを、Phase 9の有界Rework候補へ移す。
- Phase 10を、Project全Docs統合、Shared Constitution、PADG、Full Runtime ConstitutionおよびUI Consolidationの一貫したPhaseへ再構成する。
- 旧Phase 10のHardening、Cloud、External R&D、正式Agent Capability等をPhase 11以降へ送る。
- Phase 8のConstitutionは暫定版、Phase 10のConstitutionは全Docsを根拠にした本格版と分ける。
- General Web SearchとFormal Agent Level 1はPhase 11以降へ送り、Phase 8はManual URL EvidenceとResearch Foundationに限定する。
- RAG ON＋NO_HIT時のStrict Deterministic Responseを、現在実装しない保留案として残す。

過去Historyは変更しない。既存予約とConflictする場合、本書のUser Decisionを現在の再編正本とする。

## 2. Phase 7現在地とNO_HIT保留案

Phase 7ではLocal Corpus、Citation、Data Controls、Auto ResumeおよびRAG Current／Historical分離をBounded MVPとして実装した。実画面確認で、Local Corpus登録・更新後のCurrent値反映、過去Turn不変および削除後の旧Code非提示を確認した。

P7-RW5では次だけをCurrent Rework対象とする。

- NO_HIT CitationをRetrieval直後から先行表示し、Final回答がStreamingされても消さず、回答後／Reload後も保持する。回答とCitationの一括表示へ変更しない。
- Local Corpus Citationは空Headingではなく`Title` Fieldとして登録Titleを表示する。
- Synthetic `local-corpus/<slug>.md`をUser-facing Pathへ出さず、Active Runtimeの実保存Registryである`runtime_data/persistent/<scope-id>/local_corpus/documents.json`を表示する。Current User Mac例は`runtime_data/persistent/mac-local-primary/local_corpus/documents.json`であり、Scope IDをHard-codeせずActive Runtime設定から導出する。

次はCurrent Closure Blockerにしない。

```text
Optional Strict NO_HIT Mode:
  RAG ON＋NO_HITではMain Modelを呼ばず、Turn開始時に固定した回答言語で
  決定論的な「現在の根拠なし」回答へ収束する。

Current Decision:
  Qwenの回答言語・表現はGovernance未接続状態のModel品質として現状許容する。
  Strict Modeは将来必要になった場合に追加できる保留案とし、Phase 7 Closureを止めない。

Reopen Condition:
  Userが明示的にStrict NO_HITを要求する、またはModel出力が再びMaterialな
  False Grounding／言語逸脱を生み、Current Governanceだけでは閉じられない場合。
```

過去Turn、過去Citation、当時のRevision／DigestをCurrent Corpusへ追随させて書き換えない。

## 3. Phase 8 — Bounded Research Foundation

### 3.1 Manual URL Evidence

Phase 8冒頭では、Phase 7のWeb Search／Fetch PortとSecurity Scaffoldを再利用し、次の限定機能だけを候補とする。

1. Userが明示的に貼ったPublic `http／https` URLを取得して画面表示する。
2. 同ContentをUntrusted External EvidenceとしてMain Modelへ渡す。
3. URL、取得時刻、DigestおよびSourceをCitation／Evidenceとして保持する。
4. Default OFF、User明示操作、Local Loopbackを基本境界とする。

General Search Provider、検索候補の自動発見、LLM-triggered Automatic Search、Account、Credential、Cost、Quota、Public Demo運用、Hostile-site Sandboxおよび高度Data QualityはPhase 11以降とする。

### 3.2 Provisional Runtime Constitution

Phase 8ではProject Root直下の`constitution/`へ、通常Chat／Agent／Toolで利用可能な暫定・有界基盤を作る候補を維持する。

```text
Maximum Claim:
  Provisional Runtime Constitution
  Constitution Research Preview v0.x
  Foundation／Hook／Schema／Mode実証

Mode Foundation:
  OFF
  OBSERVE
  ENFORCE
```

Phase 8時点では全Docs統合前であり、完全版、Lossless版、Production版または全Rule統合済みと主張しない。

### 3.3 通常Chat／Agent／ToolとGD群

- Runtime ConstitutionをAgent専用に閉じない。
- Common CoreとChat／Agent／Tool Capability Viewを分ける。
- Constitutionと17 JSON Source／18 Logical GDを親子関係にしない。
- Constitution ProviderとGD Provider群を並列独立に評価し、Versioned Generic Result EnvelopeをGeneric Resolverへ渡す。
- ConstitutionがARGD、DAGD、AAGD等を直接選択、Importまたは実行しない。
- GD追加・削除・交換でConstitution Sourceの変更を必須にしない。
- 固有GD、Model、Provider、Tool、Role、UI LabelおよびPhase番号のHard-codeを可能な範囲で全力回避する。
- 固定が必要なFail-closed InvariantやSchema Bootstrap値は、理由、Version、MigrationおよびTestを持つContractへ隔離する。

### 3.4 Dev Agent Foundation

Phase 8ではUIを含む`MARGPA Development Agent` Research Preview／Foundationを候補とするが、Formal Level 1完成は主張しない。

- 通常Chat／Dev Agent切替。
- 安定Capability IDと変更可能な表示名の分離。
- Run／Step／State、Tool Port／Registry、MCP Client Adapter Port。
- Manual／Risk-based／Envelope Autonomous／Gate-only／Plan-only Approval Profile。
- Constitution／GD Hook、Stop／Cancel／Budget／Audit。
- Fake／Deterministic／限定Local Toolによる実証。

Generic MCP、広範な実Tool、Dynamic Sub-Agent、長時間完全自律、Git／Network／Deployおよび正式Level 1はPhase 11以降とする。

## 4. Phase 9 — Technical Core／Multi-Governance／Bounded Phase 6 Debt Rework

Phase 9は「細かなUIを全て仕上げるPhase」ではなく、Runtime技術Coreと構成比較を閉じるPhaseとする。

### 4.1 Phase 6中心Debtの有界Rework

Phase 6で成立したProvider Registry、Role Lifecycle、Budget、Deadline、Cancel、Recording、Failure Presentation、Rule／Pattern Base Guardrail、Built-in Judge PortおよびGD Compiler入口をAs-built Baselineとして再利用する。

次をPhase 9の有界Rework候補へ移す。

1. Selene Dedicated Judgeの実Artifact Load／Inference／Prompt／Strict Output Contract。
2. Qwen3Guard Dedicated Guardの実Artifact Load／Inference／Target別Output Contract。
3. ARGD／DAGDその他GD Semantic RuleのLive Criterion評価。
4. Built-in Evaluatorの適用可能Criterionと`not_applicable／deferred／unknown`境界。
5. Independent JudgeによるJudge／Repair／Rejudge Golden Path。
6. Main Governance Semantic ENFORCE、Conflict／Priority／Budget。
7. Configured／Active／Executed／Evidence Identityの一致。

ただし個人PoC／MVPの停止線を適用する。Phase目的の中心経路が動き、Data破損や虚偽成功表示がなく、User実画面Testへ渡せ、次Phaseの土台になる状態で止める。企業Product級HardeningをPhase 9 Closure Blockerへ勝手に昇格しない。

### 4.2 Experiment／Multi-Governance

- Model／Judge／Guard／GD／RAG／Repair／Modeの組合せをRun Identity付きで比較する。
- Self JudgeとIndependent JudgeをEvidence上で区別する。
- Multiple Definition、Conflict、Suppression、Repair Propagation、Manual／Static／Dynamic Routingを比較する。
- Dedicated ProviderがResource上成立しない場合も、Built-in／Rule-based／Noneの正直なBaselineで技術Coreを閉じる。

### 4.3 Phase 9で行わないもの

- Project全Docs統合／Full Closure。
- `docs/project/shared/constitution/`完全版。
- PADG Package完成。
- Full Runtime Constitution。
- Settings／Sidebar／右側Panelを含む大規模なVisual UI再編。
- 旧Phase 10のCloud／Hardening／External R&D。

Phase 9はTechnical Closureを優先し、中途半端なDocs統合またはUI改修を抱えたまま閉じない。

## 5. Phase 10 — 一貫したProject Integration Program

Phase 10は次の順序を崩さない。各作業を一つの曖昧な「Docs統合」に混ぜない。

```text
1. Project-wide All-Docs Integration Pass 1
2. Project-wide All-Docs Integration Pass 2
3. Shared Constitution Compilation Pass 1（全Docs走査）
4. Shared Constitution Compilation Pass 2（全Docs再走査）
5. PADG Package初版／Portability Validation／第2版
6. Full Runtime Constitution
7. Phase 10後半 UI／Right-side Observatory Consolidation
```

### 5.1 Project-wide All-Docs Integration — Pass 1

`Phase 3〜9だけ`ではなく、Repository内の**全Docs**をSource Corpusとする。

対象例：

- `docs/project/current/`。
- 各PhaseのStable `phase_*_ja.md`、Requirements、Architecture、Index、Lossless Compilation。
- `docs/project/shared/` Stable／History。
- `docs/public/`。
- Phase History、Handoff、Review、Recovery、Operations、Planned Work、Unresolved、Automation、Constitution Research。
- Root公開Docsとの整合に必要なDoc Pointer。

Pass 1ではSource Inventoryを作り、各Stableが現在も最新版・正本として妥当かを確認する。古い`project/current/`、Phase Stable、Public StatusおよびCross-referenceを必要に応じて更新する。HistoryをStableへ無差別統合せず、Current Decision、Superseded Decision、Raw EvidenceおよびHistorical Incidentを分類する。

### 5.2 Project-wide All-Docs Integration — Pass 2

Pass 1の成果物だけを読むのではなく、再び全Source Docsを走査する。

- Source Inventory漏れ。
- Stable更新漏れ。
- Phase間Conflict。
- Current／Historical混同。
- Old Phase番号／延期先の矛盾。
- Public／Current／Phase Stable不一致。
- Pointer、Digest、Provenance、Coverage。

必要な訂正はPass 1成果物を無言Overwriteせず、History／Gap Audit／新Revisionを伴って反映する。Pass 2完了後にProject-wide Docs CorpusをFreezeする。

### 5.3 Shared Constitution — Pass 1

All-Docs Integration完了後、Constitution編纂のために**全Docsを改めて走査する**。Docs統合の副産物だけでConstitutionを作らない。

`docs/project/shared/`はAutomation、Cross-provider、Compaction、Role、Authority、Incident、Evidence、Git、BackupおよびClosure知識が集中するため重点Sourceとするが、唯一のSourceにはしない。

全Phase、Current、Public、History、Handoff、Review、Failure、Near Miss、User DecisionおよびProvider Evidenceから、Rule SourceとProvenanceを抽出し、`docs/project/shared/constitution/`のCanonical Candidateを作る。

### 5.4 Shared Constitution — Pass 2

Pass 1 CandidateだけをReviewせず、再び全Docsを走査する。

- Rule抽出漏れ。
- Historical FailureをNormative Ruleへ誤昇格していないか。
- User最新Decisionと旧Automation RuleのConflict。
- Provider固有挙動とCommon Ruleの混同。
- Authorityの過剰生成、過剰停止、過剰Receipt、過剰Fresh Task化。
- Provenance、Rule ID、Revision、Digest、Exception、Amendment Procedure。

Gapを第2版へ反映し、Shared ConstitutionをFreezeする。

### 5.5 PADG Package

正式名称は`Portable Autonomous Development Governance Package`、短縮名は`PADG Package`とする。

- Automation／Cross-provider／Agent Orchestration。
- Manual／Auto Compaction Recovery。
- Agent／Task間Role分離。
- Codex Task間情報共有、Claude／Copilot Long-run。
- Authority／Approval／Evidence／Incident／Resource／Docs Lifecycle。
- Development Constitution。

`common/`、`providers/codex/`、`providers/claude/`、`providers/copilot/`を分離する。CommonをProvider最小公倍数へ縮退させず、未対応CapabilityはManifestで明示する。

初版を作った後、他Projectへ移植可能かを第2周で再検証し、Path、Provider Tool、Project固有名、Role、PhaseおよびUIへの隠れた依存をGap Auditする。初版を消さず第2版へ反映する。

### 5.6 Full Runtime Constitution

Shared ConstitutionとPADGが成立した後、Phase 8暫定`constitution/`から本格Runtime Constitutionへ移行する。

- 通常Chat／Agent／Tool向けCommon／Capability View。
- Rule Source Pointer、Rule ID、Revision、Digest、Manifest、Schema。
- OFF／OBSERVE／ENFORCEの正式契約。
- Constitution Providerと18 Logical GD Provider群の疎結合並列評価。
- Generic Resolver／Conflict／Priority／Authority／Evidence。
- 暫定版からのMigration／Compatibility。

Shared／Portable Packageの全Ruleを製品Runtimeへ丸ごとCopyせず、Runtime Capabilityに必要なRuleだけをSource Pointer付きで再構成する。

### 5.7 Phase 10後半 UI／Right-side Observatory Consolidation

Technical Core、Docs Corpus、ConstitutionおよびPADGが固まった後に、累積UIをまとめて再編する。

- Advanced Settingsの順序、区切り、余白、Mode Button整列。
- Research／Developer内部設定の非表示化。
- Sidebar環境情報、回答言語幅、Model／Context／Token表示。
- Context WindowのNative／Backend／Hardware Verified／Effective／Working区別。
- Context右側のHandoff／Manual Compaction Action。
- Main Chat右側のGovernance Trace／Observability Panel。
- User Input、RAG、PRE、Candidate、POST、Guard、Judge、Resolver、Repair、Final、AuditのIdentity Chain。
- Strict／Progressive ENFORCEの表示・操作。
- Responsive／Multi-device Layout。

UI変更前にTechnical ContractをFreezeし、UI都合でRuntime Identity、EvidenceまたはAuthorityを再定義しない。

### 5.8 Citation／Source Presentation Consolidation

Current UIのように、一つのAssistant出力の下へ複数Citationを複数列で全展開する方式は、Source数が増えるほど回答本文を圧迫するため、Phase 10後半のRight-side Panel再編時に変更する。

対象はWebだけに限定しない。

- Project Documentation RAG。
- Local Corpus。
- Public／External Web Evidence。
- User提供Markdown／JSON／Text／Document。
- 将来の画像、音声、動画、Archiveおよび一般File Attachment。
- Tool／Agentが取得したExternal／Generated Artifact。
- その他、回答生成に使用された全Source Class。

表示は次の三層へ分離する。

```text
Assistant Answer:
  短いInline Citation／Source Chipだけを本文付近へ表示

Popover／Preview:
  Source Title、Source Class、短い概要、DomainまたはDocument名を表示

Right-side Source Panel:
  全Source、本文との対応、Title、Path／URL、Heading、Chunk ID、
  Document Digest、Revision、取得時刻、Provider、採用理由、Score、
  Evidence／Trust State等の詳細を表示
```

Source PanelはRAGとWebで別々の場当たり的UIを作らず、共通のVersioned Source／Citation Projectionを購読する。Source Class固有項目はExtension Fieldとして追加し、Main Chat、Citation、Persistent ConversationおよびAuditのIdentityを失わない。

Web SourceのInline CitationまたはPreviewを選択した場合は、安全なExternal Link属性を付けて対象Siteを新規Tabで開く。Project Docs／Local Corpus／添付File等は、実在するDocument／Artifact Locationまたは専用Previewを開く。Synthetic Pathや存在しないFileをUser-facing Linkとして表示しない。

回答Copyは画面上のChipやRight Panelの見た目をコピーせず、Portable Markdownへ変換する。本文中にはSource参照を置き、末尾にReference Definitionを付ける。

```markdown
適当に1個：最新RoadmapではPhase 8に`MARGPA Development Agent`のResearch Preview/Foundationが明記されてる。
Webも確認。ホロライブ公式では天音かなたは現在「卒業生」表記。([[ホロライブ公式サイト](https://hololive.hololivepro.com/talents/amane-kanata/?utm_source=chatgpt.com)][1])

[1]: https://hololive.hololivepro.com/talents/amane-kanata/?utm_source=chatgpt.com "〖卒業生〗 天音かなた | 所属タレント一覧 | hololive（ホロライブ）公式サイト"
```

Local／Project／File Sourceでは、外部URLを捏造せず、PortableなRepository Path、Artifact ID、Document IDまたは利用可能なLink TargetをSource種別に応じて出力する。Reference番号は一つの回答内で安定させ、同一Sourceの不要な重複定義を避ける。

過去TurnのCitation／Reference Definitionは当時のSource Revision／Digestへ固定する。Current Sourceの更新や削除によって過去回答を遡及書換えしない。右Panelへの移動はPresentation変更であり、Citation、Provenance、Digest、Persistent EvidenceまたはAudit情報を削除・縮退する許可ではない。

## 6. Phase 11以降

旧Phase 10の次を、Phase 11以降の独立Programへ移す。

- Audit／Evidence Hardening、Hash Chain、Signature、WORM等。
- Home Server、Cloud、AWS、Windows／Linux、Backend Expansion、Lightning Refresh。
- Model／Modality／Training／Data Governance拡張。
- External Original R&D Integration。
- Governed External Web Knowledge Runtime。
- Formal MARGPA Development Agent Level 1。
- MARGPA EEAE Agent Level 2、MARGPA FCAE Agent Level 3。
- Generic MCP、Remote Tool、長時間自律、Dynamic Sub-Agent、Deploy／Operate。
- 外部Gmail／LINE等の重要Gate通知、詳細確認、指示／承認。
- Phase 10完成後、`<project-root>/constitution/`、`docs/project/shared/constitution/`および`<parent-root>/portable-autonomous-development-governance-package/`の三系統すべてを、新規中立Codex Task／Claude／GPT通常Thread等でCross-provider妥当性評価し、User判断で必要な系統だけ任意再編纂する候補。単体評価と三系統間の相互整合を扱い、Phase 10 Scope／Gateへは追加しない。詳細は`phase_11_plus_cross_provider_constitution_validity_review_and_optional_recompilation_reservation_ja_20260901185439.md`。

### 6.1 Governed External Web Knowledge Runtime

Phase 8 Manual URL Evidenceを土台に、Search Provider、Account、Credential、Cost、Quota、Privacy、Terms、Consent、Secret／PII Gate、Search／Fetch／Normalize／Selection／Chat Injection／Citation、Hostile-site／Parser IsolationおよびPublic Demo Operator Contractを扱う。

Provider既定値は`none`、Activationは`disabled`、ConsentはOFF、External Network Callは0とする。Manual Search／Groundingを先に成立させ、Automatic Search Triggerは別Gateとする。

### 6.2 Autonomous Engineering Agent Capability Levels

- Level 1：Development AgentとしてDesign Support、Implementation、Test、Fix／Repairを安定運用する。
- Level 2：ConsultingからDeploymentまで一案件をEnd-to-Endで完遂する。
- Level 3：Operate、Monitor、Repair、Improve、Re-architect、Migrate／Retire、Next Cycleまで継続運営する。

Capability名と内部Agent Topologyを分離し、正式完成は実案件EvidenceとUser Acceptanceで判定する。

## 7. Claim／Authority境界

- 本予約はPhase 7 ClosureまたはP7-RW5 PASSを先取りしない。
- Phase 9／10／11のImplementation Authorityを生成しない。
- 旧HistoryのPhase番号を遡及変更しない。
- Roadmap更新はCurrent Planの再分類であり、実装済みClaimではない。
- 未解決項目を解決済みへ変更しない。
- PoC／MVP停止線を維持し、Product／Enterprise完全性を黙ってClosure Gateへ昇格しない。

## 8. Supersession／Related Sources

本書は次を削除せず、現在のPhase割当と走査順を訂正・統合する。

- `phase_8_provisional_and_phase_10_full_runtime_agent_constitution_staging_reservation_ja_20260829113647.md`
- `runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_ja_20260829114640.md`
- `phase_6_closure_pre_gate_phase_10_constitution_portability_and_phase_11_hardening_roadmap_restructure_reservation_ja_20260829120117.md`
- `phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md`
- `phase_8_margpa_development_agent_research_preview_and_phase_10_capability_levels_reservation_ja_20260828084745.md`
- `phase_8_manual_url_evidence_and_phase_11_general_web_search_lossless_scope_refinement_ja_20260830083225.md`
- `phase_11_plus_governed_external_web_knowledge_runtime_reservation_ja_20260829222647.md`
- `phase_6_governance_semantic_runtime_difficulty_retrospective_and_phase_10_transfer_ja_20260829175551.md`

Current corrections:

```text
Phase 3〜9だけのDocs統合       -> 全Project Docsを2周統合
Docs統合とConstitution同時作成 -> 別Programとして各2周
SharedだけからConstitution     -> 全Docs走査、Sharedは重点Source
Phase 6中心DebtをPhase 10      -> Phase 9有界Rework候補
Phase 9大規模UI                -> Phase 10後半
旧Phase 10 Hardening           -> Phase 11以降
Formal Agent Level 1           -> Phase 11以降
General Web Search             -> Phase 11以降
```
