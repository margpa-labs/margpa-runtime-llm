# Phase 8 Post-Manual Acceptance Bounded Rework Scope

```yaml
document_id: phase_8_post_manual_acceptance_bounded_rework_scope_20260831122257
document_type: controller_finding_and_execution_scope
document_state: frozen_for_handoff
language: ja
recorded_at: 2026-08-31 12:22:57 JST
decision_authority: user
controller: Codex_project_controller
implementation_authority: false_in_this_document
phase_8_closure: blocked_until_rework_and_user_recheck
```

## 1. Objective

2026-08-31 User Mac Manual Acceptanceで再現した、Phase 8中心MVPの次の差分だけを是正する。

```text
P8-MANUAL-001  Manual URL安定取得／Exact Failure／Fail-closed Grounding
P8-MANUAL-002  Web Citation必須Metadata／Actual Title／Redirect Truthfulness
P8-MANUAL-003  Archive Sidebar／Panel State Synchronization
P8-MANUAL-004  Constitution Preview Mode／Decision Layout
P8-MANUAL-005  Dev Agent informed Approval／Traceable Fixture Workspace
P8-MANUAL-006  Dev Agent Action Button Contrast
```

## 2. P8-MANUAL-001 — Manual URL MVP

正本：

`phase_8_manual_web_direct_url_reliability_grounding_and_context_budget_findings_ja_20260831112449.md`

必須の最小成立条件：

- 普通のPublic HTTP(S) URLに対し、Retry可能なDNS／Connect Failureを恒久Unsafe Rejectionと同一視しない。
- Retry／Backoff／Deadline／Cancelを有界化する。
- Public IPv4／IPv6 Candidateのみを安全に扱い、Private／Loopback／Link-local／Metadata／Dangerous Port拒否を維持する。
- Aggregate ReasonとSpecific ReasonをLive／Persistence／Reload／Restart／UIへ保存する。
- Userが当該URLだけをEvidenceと指定し、Fetch 0の場合は未取得Pageの要約／人物説明／Fact生成を行わず、Configured LanguageのTyped Safe Failureへ収束する。
- HTMLはRaw `script／style`等を無制限にMain Modelへ入れない。新規大規模Parserは作らず、最小Visible Text／Title抽出とEvidence Hard Cap、またはTyped `content_budget_exceeded`を選ぶ。

## 3. P8-MANUAL-002 — Web Evidence Traceability

Chat CitationとPersistenceに次を損失なく保持する。

```text
Source Class
Requested URL
Canonical URL
Fetched At
Content Type
Document Digest
Transformation
Source Authority（Current Contractにある場合）
Untrusted Label
Specific Failure Reason（Failure時）
```

- HTML Pageは取得可能な場合、URLの代わりに実`<title>`をTitleとして投影する。
- URL Copy Buttonを`Pathをコピー`と表示しない。
- RedirectでRequested URLとCanonical URLが異なる時だけ、両方を明示する。
- SuccessをTrustedと同一視しない。
- P8-ACC-010はRequired FieldのLive／Reload／Restart Evidenceで再導出する。

## 4. P8-MANUAL-003 — Archive State Synchronization

- SidebarはActive Chatだけを取得する。
- Archive後はSidebarから即時除外する。
- Archive済みChatはArchive Panelだけに表示する。
- Unarchive後はArchive Panelから除外し、Sidebarへ即時戻す。
- `Archive済みChatを表示／閉じる`を実装する。
- ShowまたはSettings Reopenで新しい一覧をFetchする。
- Settings Close後に古い`ready`状態をCurrentとして残さない。
- 解除後のManual Resume不要をRegressionさせない。

## 5. P8-MANUAL-004 — Constitution UI

Semantics／Contract／Production OFFは変更しない。Frontendだけで次へ整形する。

```text
MODE
  Decision
  評価区分
  Action許可範囲
  違反時の表示
```

OFF／OBSERVE／ENFORCEの名前とDecisionを同一行へ押し込まない。

## 6. P8-MANUAL-005／006 — Traceable Dev Agent Fixture

### 6.1 Fixed Workspace

Current In-memory Fake Writeは、次の追跡可能な実File Fixtureへ置き換える。

```text
<configured-runtime-data-root>/persistent/<scope-id>/dev_agent/
  fixture_workspace/
    notes/readme.md
    notes/todo.md
    notes/new.md
  runs/<run-id>.json
```

要求：

- RootはCurrent Runtime Configurationから導出する。
- Allowed Rootは`fixture_workspace`のみ。
- Absolute Path／`..`／Symlink／Root Escapeを拒否する。
- Owner-only Directory／File ModeとAtomic Writeを既存Run Storeと同程度に保つ。
- Project File／任意User File／Network／MCPに触れない。
- Fixture SeedはDeterministicにし、TestごとにTemp Runtime Rootを使える。
- Write完了後のPath／Digest／Timestamp／Run ID／Step ID／ResultをRun Evidenceと照合できる。
- Restart後にWorkspaceとRun Snapshotの追跡が可能。

### 6.2 Informed Approval UI

Run開始前／実行中／Approval Gateで少なくとも次を表示する。

```text
Tool Name／Tool ID
Step ID
Input
Target Path
Write Content
Overwrite有無
Resource Scope: fixture_workspace_only
Gate Reason
Execution Result／Output
```

Listは実Path一覧、Readは対象Pathと読み取りContent、Writeは保存PathとDigestをUIで追跡できる。

### 6.3 Button Contrast

Approval／Deny／Advance／Cancel／Completion ApprovalへPrimary／Secondary／Dangerの区別と読めるContrastを与える。
White／on／White相当を禁止し、Light／Dark両Themeで確認する。

## 7. Explicit Non-goals／Deferred

```text
General Keyword Search／Search Provider／Automatic Search
Browser Rendering／Login／Cookie／Anti-bot／Hostile-site Sandbox
Full Web Extraction／Ranking／Multi-source Contradiction
Normal ComposerにURLを直貼りする最終UX
Archive Dedicated Modalの本格Redesign
Archive完全削除／一括Delete／Export
Project Sourceに対するReal Dev Agent Tool
Real MCP／Dynamic Sub-agent／Level 1完成
Production Constitution Activation／GD Semantic接続
```

## 8. Stop Line

Phase 8で必要なのは、限定MVPの中心がUser実画面で追跡可能・安全・正直に動くことである。
Product品質、任意Site互換、未解決0件またはFormal Level 1を求めない。
