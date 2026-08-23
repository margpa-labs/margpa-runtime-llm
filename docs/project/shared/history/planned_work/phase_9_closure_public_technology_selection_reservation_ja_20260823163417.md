# Phase 9 Closure直前 Public Technology Selection作成予約

```yaml
document_id: phase_9_closure_public_technology_selection_reservation_20260823163417
status: planned_work_priority_reservation
document_type: planned_work
language: ja
created_at: 2026-08-23 16:34:17 JST
requested_by: user
target_timing: immediately_before_phase_9_closure
target_candidate: docs/public/technology_selection_ja.md
source_reference_state: read_only_reference_only
```

## 1. Reservation

Phase 9の実装、Experiment／Multi-Governance Research Platform、Phase 3〜9累積Docs整理および最終Acceptanceが出揃った後、Phase 9 Closureを確定する直前に、Public向けのTechnology Selectionを新規作成する。

Target候補は次とする。

```text
docs/public/technology_selection_ja.md
```

Exact File名、Public IndexからのLink、英語派生版の要否およびCommit対象は、Phase 9 Closure時のAs-builtとPublic Docs構造を確認してFreezeする。

## 2. Read-only Reference

構成、章立て、Public向け情報粒度および記述方針の参考として、Userが明示した次の既存Public文書をRead-onlyで参照する。

```text
/Users/Nazuna Research/Documents/pseudo_root/
99_ps_Main_Creating_Objects専用_20260219/
MARGPA-RUNTIME-LLM-PUBLIC/margpa-runtime-llm/
docs/technology_selection_ja.md
```

このReferenceは2026-07-31時点の旧Public Technology Selectionであり、Phase 9 Closure時点の正本ではない。文章、採用技術、Version、Frontend構成、Model状態、RAG構成、Storage、Governance、Agent／Tool、実行環境および将来候補をそのままコピーしない。

`MARGPA-RUNTIME-LLM-PUBLIC/margpa-runtime-llm/`は現在のProject Rootとは別Repository／別用途である。本予約はReference File 1件のRead-only参照だけを記録するものであり、PUBLIC側RepositoryへのWrite、同期、削除、Git操作または自動反映を許可しない。

## 3. Phase 9 Closure時のSource of Truth

新しいPublic Technology Selectionは、次をPhase 9 Closure時点で再走査し、As-builtを正本として作成する。

- `pyproject.toml`および`uv.lock`。
- FrontendのPackage／Build／Test設定。
- `src/`の実Runtime Composition、Adapter、PortおよびEntry Point。
- `config/`のModel、Profile、RAG、AccessおよびRuntime設定。
- `definitions/`と、Phase 9時点のGovernance Definition実装状態。
- `constitution/`が実在する場合、その公開可能な位置付けとMode状態。
- Model Definition、実Artifact Evidenceおよび実Load／Acceptance結果。
- Conversation Persistence、SQLite、Recording、Evidence、AuditおよびExperiment Data境界。
- Phase 6 Judge／Repair／Observability、Phase 7 RAG／Data Governance、Phase 8 Constitution／Agent／Tool、Phase 9 Experiment PlatformのAccepted Evidence。
- `docs/public/roadmap_ja.md`、Phase Index、Closure ManifestおよびAccepted ADR。
- macOS、Linux、Metal、CPU、CUDAその他、実際に検証済みの実行環境。

Historyの旧計画、未Accepted Proposal、未実装候補または古いPublic文書をCurrent As-builtへ昇格させない。

## 4. Required Public Content

最低限、次をPublic向けに再構成する。

1. 文書の目的、対象時点および公開範囲。
2. 開発言語、Runtime Version範囲および選定理由。
3. Package、Dependency、BuildおよびLock管理。
4. Local LLM Runtime、Backend、Artifact形式およびModel構成。
5. Main、Guardrail、LLM-as-a-Judgeその他Role別ModelのCurrent／Available／Deferred状態。
6. CLI、Web API、Streaming、Frontend FrameworkおよびUI Build構成。
7. Configuration、Schema、Validation、Dynamic Runtime ControlおよびOFF／OBSERVE／ENFORCE Mode。
8. Conversation Persistence、SQLite、Runtime Data、Recordingおよび非Git管理Data境界。
9. RAG、Retrieval、Citation、Data GovernanceおよびCorpus Integrity。
10. Governance Definition、Compiler／Runtime Binding、Guardrail、Judge、RepairおよびObservability。
11. Constitution、Agent、ToolおよびAuthority Controlの実装済み範囲。ただし内部の機微なRule全文は公開しない。
12. Experiment／Evaluation／Audit／Evidence基盤。
13. Test、Static Check、Frontend Test、Real Model／Browser Acceptanceおよび品質管理。
14. 対応Hardware、OS、Local／Cloud／External Environmentの実証範囲。
15. Security、Privacy、Secret、Public DemoおよびExternal Publicationの境界。
16. 採用中、利用可能、検証中、延期、将来候補および不採用を区別したTechnology Matrix。
17. 今後変更され得る条件と、Roadmap正本への参照。

章立てはReference文書をBase候補にできるが、Phase 9 As-builtを正確に説明できるよう再編成してよい。

### 4.1 不採用／保留／置換Technology Decision Ledger

Public Technology Selectionには、採用技術だけでなく、Phase 1〜9で検討して採用しなかった技術、途中で置換した技術、後続へ延期した技術および比較候補の理由をPublic向けに記録する。

Phase 9 Closure時に、Phase 1〜6を遡及走査し、Phase 7〜9は以後の設計・実装・Review Evidenceから継続的に収集する。単にDependencyやSourceに存在しないことを「不採用」と推測せず、Roadmap、ADR、Technology Selection、Phase Requirements／Architecture、Planned Work、Review、Handoff、実機EvidenceおよびUser Decisionから確認できるものだけを記載する。

最低限、各Decisionへ次を持たせる。

| Field | Required Content |
|---|---|
| Technology／Candidate | Library、Framework、Model、Backend、Storage、Cloud、Toolまたは方式 |
| Category | Runtime、Frontend、RAG、Storage、Governance、Agent、Infrastructure等 |
| Decision State | `NOT_ADOPTED`／`DEFERRED`／`REPLACED`／`CANDIDATE`／`REJECTED_FOR_CURRENT_SCOPE` |
| Considered At | Phase、SubphaseまたはDecision時点 |
| Intended Benefit | 当初検討した目的と期待効果 |
| Reason | 不採用、延期または置換の具体的理由 |
| Evidence | ADR、Test、Benchmark、Resource実測、Compatibility、SecurityまたはUser Decision |
| Adopted Alternative | 実際に採用した技術または現行方式。存在しなければ`NONE` |
| Re-entry Trigger | 再検討する条件。恒久不採用ならその根拠 |
| Current Impact | Phase 9 Closure時点のRuntime／Public利用者への影響 |

不採用理由は、可能な限り次へ分類する。

- Hardware／Memory／Disk／Latency／Cost制約。
- Dependency Size、Build、Platform CompatibilityまたはMaintenance負担。
- Vendor／Framework Lock-inと、非依存Platform方針との不一致。
- 既存Port／Adapter／疎結合Architectureで代替可能。
- Security、Privacy、External Network、SecretまたはData Boundary上の問題。
- Evidence／Traceability／OFF・OBSERVE・ENFORCE統治境界との不整合。
- Current Phase Scopeに対して過剰、未成熟または時期尚早。
- Test／実機Benchmarkで不適合。
- より適切な代替Technologyへの置換。
- Userによる明示的な延期、不採用または優先順位変更。

次を混同しない。

```text
未検討                 ≠ 不採用
現在使っていない       ≠ 恒久不採用
Phase外へ延期          ≠ 技術的に不適合
候補として保持         ≠ 導入予定確定
Download済み           ≠ Runtime採用
比較で敗れた           ≠ 全環境で無価値
現時点のResource不足   ≠ 将来も実行不能
```

Phase 1〜6の遡及対象には、少なくともFrontend Framework、UI方式、LLM Runtime／Model、Model配布経路、RAG Framework／Embedding／Vector Store、Storage、Cloud／External Runtime、Security／Guardrail、Judge／Repairおよび採用を見送った追加Dependencyを含める。ただし、実際に検討したEvidenceがない固有Technologyを後付けでDecision Ledgerへ追加しない。

Phase 7以降に新しいTechnology比較を行う場合は、採用結果だけでなく、不採用候補、理由、Evidence GradeおよびRe-entry Triggerを各Phase History／ADRへ残し、Phase 9 Closure時のPublic Decision Ledgerへ集約できるようにする。

Public版では内部機密、個人事情、Credential、Exact Cost明細または攻撃可能なSecurity Detailを除きつつ、技術判断を第三者が再評価できる程度の理由を残す。「採用しなかった」の一文だけで終わらせない。

### 4.2 Phase 7 Web Retrieval／Web Search Technology Selection予約

Phase 7のFull RAG／Data Governanceでは、Local Document Retrievalに加え、Modelが必要に応じて外部Web情報を検索・取得・引用できるWeb Retrievalを実装候補へ含める。

これはModelへ無制限のNetwork権限やBrowser操作権限を直接付与する設計ではない。Modelは検索の必要性、QueryまたはRetrieval Intentを提案し、実際のExternal ActionはRuntime側のGoverned Port／AdapterがAuthority、Policy、BudgetおよびData Boundaryを検証して実行する。

Phase 7での候補構造は次とする。

```text
Model／Runtime
  ↓ Search Intent／Query Candidate
Web Search Planner
  ↓ Authority／Mode／Budget
WebSearchPort
  ↓ Provider Adapter
Search Result
  ↓ Selected URL only
WebFetchPort
  ↓ Content Type／Size／Redirect／SSRF Validation
Web Content Normalizer
  ↓ Prompt Injection／Source Quality／Data Governance
Existing RAG Chunk／Retriever／Context Assembler
  ↓
Answer＋Citation＋Source Snapshot／Digest
```

最低限の設計・実装候補は次である。

- `WebSearchPort`、`WebFetchPort`および`WebContentNormalizerPort`または同等の疎結合境界。
- Search Providerを交換可能にし、特定VendorへCoreを固定しないAdapter構造。
- Search Result Snippetと実取得本文を別Evidence Classとして扱う。
- URL、Canonical URL、Title、Provider、取得時刻、Content Type、Size、Content Digest、採用Chunk、ScoreおよびCitationを追跡する。
- Localhost、Private Network、Metadata Endpoint、危険Scheme、過剰Redirect、巨大Responseおよび未許可Content Typeを拒否するSSRF／Fetch Boundary。
- Web本文中のPrompt Injection、Instruction様Text、Secret要求、Data ExfiltrationおよびTool誘導をRuntime命令として扱わない。
- User Query、Conversation Context、Secret、PIIおよびInternal Pathを検索Providerへ無断送信しないQuery Privacy境界。
- Timeout、Search件数、Fetch件数、総Byte、Domain、Token、Latency、RetryおよびExternal Cost Budget。
- Dynamic Web ContentをCurrent Factとして永続固定しないSnapshot／Staleness／Re-fetch契約。
- Citation、取得失敗、Partial Fetch、Paywall、JavaScript必須Page、Unsupported FormatおよびSource ConflictのTyped Result。
- Default OFF。Explicit SearchとRuntime判断による自動Searchを区別する。
- OFF／OBSERVE／ENFORCEのExact意味はPhase 7設計時にFreezeし、OFFではNetwork Call 0を不変条件とする。
- Phase 8ではWeb検索機能を再実装せず、Phase 7の同じPortをAgent／Tool GovernanceへBindingできる構造にする。

Phase 7で固定すべきTechnology Decisionには、少なくとも次を含める。

- Search Provider／API方式。公式API、Self-hosted、Metasearch、Scraping等の候補比較と採用／不採用理由。
- Credential／API Key／Cost／Rate Limit／Terms／Availability境界。
- HTTP Client、HTML／Text Extraction、PDF等のDocument AdapterおよびJavaScript Renderingの要否。
- Cache／Snapshot／Revalidation方式。
- Local RAGとWeb RAGを統合するHybrid Ranking／Source Priority。
- Modelが自動Searchを要求できる条件と、User明示操作が必要な条件。
- Public、Local、Basic、Cloudその他Access ProfileごとのAvailability。

検索Provider、Crawler、Browser Automation、HTML Extractor、Cache、Vector StoreまたはAgent Frameworkのうち採用しなかった候補も、§4.1のTechnology Decision Ledgerへ理由とRe-entry Trigger付きで記録する。

Phase 9 Closure時のPublic Technology Selectionでは、Phase 7で実際にAcceptedとなったWeb Retrieval構成について、次をPublic向けに記載する。

- Web検索機能のCurrent State、Default Modeおよび利用可能Profile。
- Modelが直接Network Authorityを持たず、Runtime Port／Policy経由であること。
- 採用したSearch／Fetch／Extraction／Cache／Evidence技術。
- 不採用または延期したProvider／Framework／方式と、その理由。
- Query Privacy、SSRF、Prompt Injection、Citation、Snapshotおよび既知の限界。
- Phase 8 Agent／Tool Governanceとの接続境界。

本節はPhase 7の即時開始、Network Access、Provider契約、Credential作成、課金、Source Mutationまたは特定Technology採用を許可しない。Exact Requirements／Architecture／ADR／Provider選定／Authority／Acceptanceは、Phase 7 READY後に別途Freezeする。

## 5. State Vocabulary

Technology、Model、Backend、EnvironmentおよびComponentを曖昧な「導入予定」へ一括しない。少なくとも次を区別する。

```text
CURRENT
  Phase 9 Closure時点の標準経路で有効かつAccepted。

AVAILABLE
  実装・検証済みで、設定またはModeにより使用可能。

EXPERIMENTAL
  Research／Comparison用に実装済みだが、標準経路へ固定しない。

DEFERRED
  明示的に後続Phaseへ延期。Owner／Re-entry Triggerを正本へ持つ。

PLANNED
  Accepted Roadmapに存在するが未実装。

CANDIDATE
  比較候補であり、採用決定ではない。

NOT_ADOPTED
  比較済みまたは現時点では採用しない。

UNVERIFIED
  存在・実装・動作のEvidenceが不足している。
```

`Available`と`Default`、`Download済み`と`Runtime使用可能`、`Test済み`と`実機Accepted`、`候補`と`採用`を混同しない。

## 6. Public Sanitation

Public文書には次を含めない。

- 個人User名、Home Directory、Absolute Local Path。
- Secret、Credential、Token、Private Endpointまたは非公開Account情報。
- UserのChat履歴、Runtime Data、Raw Research Captureまたは個人Data。
- 内部専用のAuthorization Token、Recovery内容、Provider MemoryまたはPrivate Governance Rule全文。
- 公開を意図していないCost、Quota、個人環境の機微な運用情報。
- EvidenceのないSecurity、Compatibility、Performanceまたは品質保証。
- 実装されていない機能を完成済みに見せる表現。

必要なLocal Path例は、`/path/to/...`等の抽象表現へ変換する。Public文書の読者が内部構造を理解するために不要な実装Detailは、Current Architecture／ADR正本への内部参照へ逃がさず、公開可能な抽象表現で説明する。

## 7. Version／Evidence Rules

- Language、Runtime、Framework、Library、Backend、ModelおよびTool Versionは、Phase 9 Closure時点のLock／実行Evidenceから再取得する。
- 旧ReferenceのVersionを転記しない。
- Model名、Quantization、Artifact Format、Digest StateおよびRoleはModel Definition／Manifest／Runtime Acceptanceと照合する。
- `macOS対応`、`Linux対応`、`CUDA対応`、`Windows対応`等は、実証済み、設計対応、未検証を区別する。
- Test件数を記載する場合はPhase 9 Closure Manifestと一致させる。
- Updated Timestamp、Source Revision、対象CommitまたはClosure Manifestへの参照を持たせる。
- 必要に応じてTechnology Inventory／Pathset／SHA-512 ManifestをPhase 9 HistoryへAppend-onlyで作成する。

## 8. Closure Work Sequence

Phase 9 Closure直前に次を行う。

1. Userから追加要件、公開粒度および英語版要否を確認する。
2. 旧Public ReferenceをRead-onlyで再確認する。
3. Phase 9 Closure CandidateのSource、Config、Lockfile、Model Definition、FrontendおよびEvidenceをInventory化する。
4. Phase 1〜6の不採用／保留／置換Decisionを遡及収集し、Phase 7〜9のDecision Evidenceと結合したTechnology Decision Ledgerを作る。
5. 旧Referenceとの差分を、追加、変更、削除、延期、不採用理由および誤記訂正へ分類する。
6. `docs/public/technology_selection_ja.md`を新規作成する。既存する場合はHistory／Digestを残して更新する。
7. Public Sanitation、Privacy／Secret、Link、Markdown、VersionおよびAs-built整合を検証する。
8. Roadmap要約版、詳細Roadmap、Public IndexおよびPhase 9 Closure Manifestから入口を接続する。
9. User Review／Acceptanceを受ける。
10. Phase 9 Closure EvidenceへFinal Path、Size、SHA-512、Source RevisionおよびValidation結果を記録する。

## 9. Non-goals

- Phase 9以前にPublic Technology Selectionを完成扱いしない。
- 旧PUBLIC RepositoryをCurrent Projectへ自動同期しない。
- Internal Architecture、Constitution、Governance RuleまたはAgent Authorityを全量公開しない。
- Public文書をDependency Lock、Model Manifest、ArchitectureまたはRoadmapの新しい正本にしない。
- 英語版を自動的なClosure Blockerにしない。必要性はPhase 9 Closure時にUserが決定する。
- 本予約をPhase 6、7または8のClosure Blockerへ変更しない。

## 10. Current Status

本書は将来作業の予約である。現時点では次を行っていない。

```text
docs/public/technology_selection_ja.md 作成／更新 : NOT STARTED
Phase 9 Technology Inventory                    : NOT STARTED
Public Index／Roadmap Link更新                   : NOT STARTED
PUBLIC側Repository Mutation                     : 0
Git Mutation                                    : 0
```

Phase 9 Closure直前に、当時のAs-built、User要件、公開範囲およびClosure工程と統合してActivationする。
