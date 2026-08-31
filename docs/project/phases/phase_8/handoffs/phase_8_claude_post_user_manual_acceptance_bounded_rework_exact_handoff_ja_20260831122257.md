# Phase 8 Claude Post-User-Manual Acceptance Bounded Rework — Exact Handoff

```yaml
document_id: phase_8_claude_post_user_manual_acceptance_bounded_rework_exact_handoff_20260831122257
document_type: exact_differential_execution_handoff
document_state: frozen
language: ja
created_at: 2026-08-31 12:22:57 JST
provider: Claude
role: 設計者兼実装者役
task_identity: Current Claude Designer Implementer Task
task_state: continued_not_fresh
phase: phase_8
execution_scope: P8-MR0_through_P8-MR6
implementation_authority: true
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
phase_8_closure_authority: false
phase_9_authority: false
git_authority: false
network_authority: false
real_browser_authority: false
real_model_authority: false
real_mcp_authority: false
user_runtime_data_authority: false
backup_authority: false
```

## 1. Continuation Contract

これはFresh Task Bootstrapではない。Current Claude Task、Current Working Tree、P8-A〜F、P8-CR、P8-RW6／7の
成立済みSource／Test／Recoveryを維持し、User Mac Manual Acceptanceで再現した差分だけを直す。

次を行わない。

- Fresh Task化、Role／Authorityの初期化。
- 既存Mandatory Role Readingの全再読。
- P8-A〜F、P8-CR、P8-RW6／7の再実装／Rollback。
- Current Working Treeを無視した作り直し。
- Phase 8の全設計のやり直し。

## 2. Mandatory Differential Reading

次だけを指定順で全文読む。Digest不一致はPath／Expected／Observedを記録し、実質的Contract Conflictが無ければ
不要停止せずCurrent Working Treeを優先する。

1. 本Exact Handoff。
2. User Manual Segments 2〜5 Evidence。

```text
docs/project/phases/phase_8/history/operations/phase_8_user_mac_manual_acceptance_segments_2_to_5_evidence_ja_20260831122257.md
SHA-512: 58329b5067ed47c2b59ccf86139d45181bcc1b90fc1f311da59d1f6d9278543459d8dfdae3d99ff5b06ef1cf7e700f626bf2a61030df7851509def792f6a91c8
```

3. Post-Manual Bounded Rework Scope。

```text
docs/project/phases/phase_8/history/operations/phase_8_post_manual_acceptance_bounded_rework_scope_ja_20260831122257.md
SHA-512: a4cdb706be64da72e68ff45c736696868b0a3e47386c092c249f891a415820daaa61c6d1d55dc866274049a04bd56e9da14407b66afba7c430ca4fb2903e0beb
```

4. User Manual Web Segment 1 Evidence。

```text
docs/project/phases/phase_8/history/operations/phase_8_user_mac_manual_acceptance_web_segment_1_evidence_ja_20260831112449.md
SHA-512: 3623409cef549cf4dc57b04db9240f03c1eba403b1cc160cbaa724ea9358dd38bea2f8903be12fca18862fed7ded6327171026a85ca8a66f34b01282bcf2f6e6
```

5. Manual Web Finding。

```text
docs/project/phases/phase_8/history/operations/phase_8_manual_web_direct_url_reliability_grounding_and_context_budget_findings_ja_20260831112449.md
SHA-512: d9bd885b3bb2dbdfaa63f2866a2ff1313ee540aebcf6feb1a11002385edb3e492affb7dd3aa08919c43ddf6b807c95a2437ed276b612782a9e445542e47b6d03
```

6. Phase 8 Requirements。

```text
docs/project/phases/phase_8/requirements/phase_8_requirements_ja.md
SHA-512: e658a5f5fda55590e3875987f1622be3e91c415a8c881dc4f1c5266f53aee7017973669dd3b3a6e0305766238566b297d76c56adf444301e78334aadbea0a1ca
```

7. Phase 8 Architecture。

```text
docs/project/phases/phase_8/architecture/phase_8_architecture_ja.md
SHA-512: 1fdfdb8b7eb3bee3d884dc5d5867be6313a5fd01755d9534c7a0e19e9e70b71ffee7a6478ed34ce8f70d8cae4f3adfdae55361a5135c2dfc9cfce65828879a8c
```

8. Phase 8 Acceptance Matrix。

```text
docs/project/phases/phase_8/operations/phase_8_acceptance_matrix_ja.md
SHA-512: 40ebe8449d880fd00f98b3633825756a4e23d1edea8efbdac437be0ad718e6b6a0c04776f1907089cde23b057087ba3c3275ba68727d116bec2baee682bd1a34
```

9. Latest Claude Return。

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_constitution_preview_semantics_micro_rework_exact_return_handoff_ja_20260831071113.md
SHA-512: c4eeaddb9337e5249c4b84a4d36e695274a2ca575e92a1aa5d4f60c958411701e182a2bc8a11f5d963cda9fe0f673fb32c654a239bca630fcae773e717de871a
```

10. Latest Controller Review。

```text
docs/project/phases/phase_8/history/operations/phase_8_codex_controller_constitution_preview_semantics_single_targeted_re_review_ja_20260831072057.md
SHA-512: 2d63ba8bb01cce3538b438ec1615cb3836b4a3af4524d151f53fca672520a171107a0cf4b83590d9cb7cbb2d4cd8454933258d5f94c975bf2872b434b313cda9
```

11. Current Unresolved Registry。

```text
docs/project/shared/未解決/current_unresolved_findings_registry_ja.md
SHA-512: 3e345a13f88bcfcc25aef1e871f0fb268848db9d9618eacbc814405c12701c112a5a4085352450f5c7be9af783b99f50708675ee359578c376deec556ad76763
```

## 3. Preserved Baseline

次は再実装／Rollbackしない。

- Phase 7 Local Corpus／RAG／Citation／Data Controls／Conversation Persistence。
- Branch Data／API／Historical Record。Branch UI既定非表示。
- Archive Title／Timestamp／Open／Unarchive／Resume不要の成立済み経路。
- Direct URL OFF／SSRF／Redirect／Timeout／Size／Content-Typeの安全境界。
- `example.org`のFetch／Citation Digest／Untrusted／Reload／Restart。
- Loopback／Private／Link-local／Metadata／Dangerous Port拒否。
- Constitution Manifest／Revision／Digest／3-Mode Semantics／Production OFF／No Authority Expansion。
- Dev Agent Stable Capability ID／Run／Step／Concurrency／Budget／Envelope／Approval Evidence／Completion Gate／Cancel／Late Result拒否。
- General Keyword SearchがFixtureであり実Searchでないという正直なUI Claim。
- P8-ACC-038のGD相関PARTIAL。

## 4. Open Findings

```text
P8-MANUAL-001  Manual URL安定取得／Exact Failure／Fail-closed Grounding
P8-MANUAL-002  Web Citation Required Metadata／Actual Title／Copy Label
P8-MANUAL-003  Archive Sidebar／Panel State Synchronization
P8-MANUAL-004  Constitution Mode／Decision Layout
P8-MANUAL-005  Dev Agent informed Approval／Traceable Real-file Fixture
P8-MANUAL-006  Dev Agent Button Contrast
```

## 5. P8-MR0 — Entry／Recovery Freeze

- Mandatory Differential Readingを読む。
- Current Working TreeをCanonicalとする。
- Open Findingsを上記6件に固定する。
- Entry Recovery Indexを作る。
- 未完了のままProgress Reportのため停止しない。

## 6. P8-MR1 — Manual URL Reliability／Grounding

### Required

- DNS／Connect／TLS／Timeout／HTTP／Content Type／Response Sizeを可能な範囲でTyped Failureに分離する。
- Retry可能なFailureだけを固定回数／Deadline内でRetryする。Permanent Unsafe URLをRetryしない。
- Resolver／TransportをTestで注入可能にし、Network 0でTransient → Success、Permanent Failure、Public IPv4／IPv6 Candidateを再現する。
- Validation時とConnection時のAddressを完全にPinしたと虚偽主張しない。Production-grade DNS Rebinding HardeningはNon-goal。
- Fetch 0のManual Evidence-only TurnはMain Modelを呼ばない、またはPage Factを生成不可にしたConfigured-language Typed Safe Failureへ収束する。呼出しが0であることをCounting Fakeで証明する方式を優先する。
- HTMLは外部Dependency追加なしの最小Extractor／NormalizerまたはHard Capで扱う。`script／style／noscript`等のRaw Noiseを無制限にMain Modelへ入れない。
- 大きなHTMLは8192 ContextのOpaque Failureにせず、Budgeted EvidenceまたはTyped `content_budget_exceeded`にする。

### Required Regression

- Loopback／Private／Dangerous PortはRequest 0。
- Redirectごとの再検証。
- OFF時Network 0。
- Prompt Injection Detection／Untrusted Label。
- Direct URLとGeneral Keyword Search Fixtureを混同しない。

## 7. P8-MR2 — Web Citation Completeness

- `Requested URL／Canonical URL／Fetched At／Content Type／Digest／Source Class／Transformation／Untrusted`をLive SSE／Completed Event／Persistence／Reload／Restart／Frontendへ損失なく投影する。
- Existing ContractがSource Authorityを持つ場合はChat Citationにも表示する。新しいAuthority Claimは生成しない。
- HTML `<title>`を実Titleとして取得し、取得不能時だけCanonical URLへFallbackする。
- URL Buttonは`Canonical URLをコピー`、Requestedと異なる時は`Requested URLをコピー`と表示し、`Path`と呼ばない。
- FailureはAggregate／Specific Reasonを両方保存する。
- Existing RecordのBackward Compatibilityを保つ。
- P8-ACC-010／011／012をSource／Test／UI Evidenceから再導出する。

## 8. P8-MR3 — Archive Synchronization

- Sidebar FetchをActive-onlyにする。
- Archive後Sidebarから即時除外し、Archive一覧だけに残す。
- Unarchive後Archive一覧から即時除外し、Sidebarへ戻す。
- `Archive済みChatを表示／閉じる`を用意する。
- Show／Settings Reopen時にRefetchし、Close時にStale `ready`をCurrent扱いしない。
- Archived Chatを`開く`経路、Unarchive後Manual Resume不要を保つ。
- 完全削除／一括Delete／Export／Dedicated Modalは実装しない。

## 9. P8-MR4 — Constitution Presentation

- Backend Contract／Semantics／Production OFFを変更しない。
- Mode NameをHeaderとし、Decision／Evaluation／Action Permission／Violation Presentationをそれぞれ別行にする。
- chat／agent／tool、OFF／OBSERVE／ENFORCE、ja／enのFrontend Testを保つ。

## 10. P8-MR5 — Traceable Dev Agent Fixture／UI

### 10.1 Adapter／Composition

- Production CompositionのIn-memory Write Adapterを、Configured Runtime Data Root／Scope IDから導出する固定Local Fixture Workspace Adapterへ置き換える。
- Target Root：`<runtime-data-root>/persistent/<scope-id>/dev_agent/fixture_workspace/`。
- Seed：`notes/readme.md`、`notes/todo.md`。Write Target：`notes/new.md`。
- Seedは存在するCurrent FileをRestartごとに上書きしない。TestはTemp Rootを使う。
- Absolute Path／`..`／Symlink／Root Escapeを拒否する。RootとIntermediate PathのOwner／Directoryを検証する。
- Private Mode、Same-directory Temporary File、Atomic Replaceを使う。
- ListはRelative Path、ReadはPath／Content／Digest、WriteはPath／Digest／Written At／Overwrite有無をResultとして返す。
- Deny／Cancel／Authority FailureはWrite 0。
- Run SnapshotのPlan Input／Step Output／Approval Evidenceと実File DigestをReload／Restart後も照合できる。
- Unit Test用Pure Fake Adapterは必要なら保持してよいが、User実画面のProduction Compositionは追跡可能Workspaceを使う。

### 10.2 Contract／UI

- Userが承認するActual Server PlanのStep InputをREST Responseへ投影する。FrontendのHard-coded Plan表示だけを真実の正本にしない。
- Run／Step／Tool／Input／Output／Target Path／Write Content／Overwrite／Resource Scope／Gate ReasonをUIで表示する。
- Approval前にExact Actionが見える。Approval後にList／Read／Write ResultとDigestが見える。
- Existing Envelope／Approval Evidence／Budget／Completion GateのContractを弱めない。
- `fixture_workspace_only／実Project File・Networkに非接触`を明示する。
- Approval／Deny／Advance／Cancel／Completion ApprovalにPrimary／Secondary／Danger Styleを与え、Light／Dark両方で読める。

### 10.3 Required Tests

- ListがExact Seed Pathを返す。
- ReadがExact Content／Digestを返す。
- Approvalなし／Deny／Cancelで`notes/new.md`が生成されない。
- Approval後だけAtomic Writeされ、Result DigestとFile Digestが一致する。
- Root Escape／Symlink／Absolute Pathを拒否する。
- Restart後のRun／File／Evidence相関。
- Existing Concurrent Advance exactly-once／Budget／Envelope／Completion GateにRegression 0。
- FrontendでActual Input／Output／Resource Scope／Gate Reason／Button Contrastを確認する。

## 11. P8-MR6 — Verification／Internal Review／Return

1. Finding 6件を1件ずつ再導出する。
2. 変更範囲のFocused Backend／Frontend Testを行う。
3. Backend Full、Mypy、Ruff Check／Format Checkを行う。
4. Frontend Typecheck／Test／Lint／Buildを行う。Static Delivery Artifactを更新する。
5. Networkの必要なTestはFixture／Mock Transport／Injected Resolverで行い、実Networkを使わない。
6. User `runtime_data/`に触れず、Temp RootでReal-file Fixture Testを行う。
7. Requirement／Negative Path／Security Boundary／Persistence／UI Truthfulness／Acceptanceの6観点でInternal Reviewを1 Cycle行う。
8. Critical／Major／MVP BlockerがFinding Scope内にある場合だけReworkする。Minor／Hardening／Deferred Non-goalで追加Cycleを無限化しない。
9. Append-only Recovery Index、Acceptance Disposition Addendum、新User Manual Recheck Sheet、Exact Return Handoffを作る。

主に再導出するAcceptance：

```text
P8-ACC-002〜012
P8-ACC-015〜018
P8-ACC-021〜023
P8-ACC-026〜030
P8-ACC-033〜040
```

Frozen Acceptance Matrix自体を書き換えず、AddendumでCurrent Dispositionを示す。

## 12. Authority／Prohibitions

許可：

- Project Root内の必要なSource／Test／Frontend／Static／Phase 8 Docs Mutation。
- Project Root内のTest／Typecheck／Lint／Build。
- Testが作るProject Root内／System Temp内の限定Temporary Data。
- Recovery／Finding Ledger／Acceptance Addendum／User Manual Sheet／Exact Return作成。

禁止：

- Git Read／Write／Commit／Push。
- Network／Install／Download。
- Real Browser／Real Model／Real MCP。
- Userが現在使っている`runtime_data/`へのRead／Write。
- Project Root外への任意Read／Write／Redirect。
- General Search Provider／Automatic Search／SearXNG／Browser Rendering。
- Archive完全削除／一括Delete／Export／Dedicated Modalの本格実装。
- Project Sourceを操作するReal Dev Agent Tool、Real Network Tool、Real MCP。
- Production Constitution Activation／GD Semantic／Phase 6未完Debtの再実装。
- Roadmap／Phase 8 Closure／Backup／Phase 9開始。

実装難度、Core File変更、Diff量、Pending Controller Review、Minor Finding、実Network未許可またはUser Manual待ちだけで
停止しない。リスクはFocused Test／Canonical Regression／Recovery／Internal Reviewで管理し、P8-MR6まで連結実行する。

## 13. Return Condition

次を満たした時だけCodex Controller待ちで停止する。

```text
P8-MANUAL-001〜006 disposition
Preserved Baseline and Regression statement
Changed Paths
Focused／Canonical Verification
Network／User runtime_data／Real Browser／Real Model action count
Internal Review Finding Ledger
Acceptance Disposition Addendum
User Manual Recheck Sheet
Recovery Index Path
Exact Return Handoff Path
Maximum Claim
```

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK`。User Manual PASS、Phase 8 Closure、General Web Search、Formal Dev Agent Level 1または
Phase 9 ReadyをClaimしない。
