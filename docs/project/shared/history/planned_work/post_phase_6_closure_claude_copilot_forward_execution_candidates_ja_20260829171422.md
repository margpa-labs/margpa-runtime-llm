# Phase 6 Closure後 Claude／Copilot前倒し可能作業一覧

```yaml
document_id: post_phase_6_closure_claude_copilot_forward_execution_candidates_20260829171422
document_state: accepted_catalog_not_execution_authority
language: ja
created_at: 2026-08-29 17:14:22 JST
current_phase: phase_7_ready
providers:
  - claude
  - copilot
authority_owner: Nazuna Research
```

## 1. 基本方針

本書は、Provider利用可能量、5時間制限およびContext残量に応じて、Phase 7以降の作業を安全に前倒しする候補一覧である。実行Authorityは別のExact Handoffで与える。

Provider共通Roleは`設計者兼実装者役`とし、Returnでは必ずProvider、Task Identity、Completed Boundary、Open Finding、Next Actionを示す。

## 2. Phase 7 Current Critical Path

### Priority A — Claude第一候補

Claudeへ連結実行を委任できる。

1. P7-0 As-built Freeze。
2. P7-A Generic Attachment Sizing。
3. P7-B Corpus／Document Lifecycle。
4. P7-C Embedding／Index／Retriever。
5. P7-D Context Injection／Citation Persistence。
6. P7-E Web Search／Fetch／Settings Toggle。
7. P7-F Web Security／Evidence Governance。
8. P7-G Data Controls。
9. P7-H Integration／Observability／Regression。
10. P7-I Complete Candidate／User Manual Handoff。

Claudeは各PackageでRecoveryを残し、Routine進捗報告で停止しない。内部Reviewを1回行い、P0／P1があれば同一Task内でBounded Reworkし、再Reviewして返す。

### Priority B — Copilot代替／差分候補

Claudeが利用制限、Provider障害またはContext限界へ到達した場合、Copilotは最後に完了したRecoveryから差分継続できる。

- Port／Domain Model／Schemaの局所実装。
- Focused Unit／Integration Test。
- Settings Toggle／Data Controls UI。
- Citation／Evidence Projection。
- Failure Path／Security Fixture。
- Claude Return後の明確なP0／P1差分Rework。

Copilotへ全Projectの再設計、既完了Packageの再実装、無制限なInternal Reviewを与えない。

## 3. 競合なしに前倒し可能なRead-only／Design

- Search Provider候補のInterface比較。Network実行なし。
- Embedding／Vector Store候補の比較とLocal Resource見積り。
- Corpus Migration／Index Version Test Matrix。
- SSRF／Prompt Injection／Secret／PII Fixture設計。
- Data Controls Field／Consent／Purpose Matrix。
- Attachment File Type／Size／Parser／Sandbox Matrix。
- User Manual Scenario、Failure Copy、Citation表示案。
- Phase 8 Agent／Tool Port Inventory。ただしPhase 8 Source変更なし。

## 4. Human／Controller Gate必須

- Network Search Providerの実Call、Credential、課金、契約。
- Package Install／Dependency変更。
- User実File、`runtime_data`、Conversation、Citationへの接触。
- Model Download／Artifact変更。
- Git Stage／Commit／Push。
- Backup、Project Root外Write。
- Phase Closure／次Phase READY。
- External Messaging、Cloud、AWS、Lightning、Public URL。

## 5. 前倒し禁止

- Phase 6既知DebtをPhase 7のついでに無断修正する。
- Phase 8／9／10のSourceを先行実装する。
- Provider Memoryを正本化する。
- Stable／Public DocsのCompletion ClaimをExecutorが変更する。
- P2／P3 FindingをClosure Blockerへ自動昇格する。
- Current Phase Sourceと別Taskで競合する並行Mutation。

## 6. Provider交代

```text
Claude -> Recovery／Return -> Controller判定 -> Copilot差分Handoff
Copilot -> Recovery／Return -> Controller判定 -> Claude差分Handoff
```

交代時は旧Task ContextやAuthorityを自動継承しない。ただし毎回Fresh Taskを強制せず、同一Taskが健全なら継続利用する。読むDocsはExact Handoffに必要な最小集合とする。

## 7. Completion Boundary

Executorの最大Claimは`COMPLETE_CANDIDATE`。Controller Independent ReviewとUser Manual前にPhase 7を`COMPLETE／ACCEPTED`としない。
