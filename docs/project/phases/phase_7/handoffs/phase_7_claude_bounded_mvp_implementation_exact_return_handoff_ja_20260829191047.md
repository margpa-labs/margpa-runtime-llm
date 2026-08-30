# Phase 7 Claude Bounded MVP Implementation — Exact Return Handoff

```yaml
document_id: phase_7_claude_bounded_mvp_implementation_exact_return_handoff_20260829191047
document_type: exact_return_handoff
document_state: final
language: ja
created_at: 2026-08-29 19:10:47 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_7
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
maximum_claim: COMPLETE_CANDIDATE
```

## 1. 冒頭要約（最重要：Scope境界の明示）

P7-0からP7-Iまで、Handoff指示通り連結実行した。Local Corpus（Document登録・検索・引用）、
Web Search／Fetch（Manual Search、Security Boundary、Evidence Governance）、Data Controls
（Retention事実の開示とPurpose別Consent）の3中心機能をBackend／Frontend双方向で実装し、
Internal Review 2 Cycleを経てComplete Candidateとして返却する。

**最も重要な一点**：Web Search／Fetch結果は、Manual Search Panelで検索・閲覧できる
**独立したUtility**として実装されており、**Chat（Main Model）のConversation Generation
Pipelineへは自動注入されない**。Model回答がWeb Evidenceを自動的に反映することはない
（P7-I Recovery Index Finding-002）。これはArchitecture図が示すEnd-to-end Web Grounding
の一部であり、Requirements自体が`disabled／manual／automatic`のうち`automatic`
Activation Tier（P7-REQ-013、自動Trigger Heuristics）の責務として明確に分離している
機能であり、本Taskでは`automatic`を`NotImplementedError`で明示的に未実装としている
（意図的Scope境界、隠蔽なし）。Local Corpus（Project Docs＋User登録Document）は対照的に
既存Chat Pipelineへ完全統合されている（既存Documentation RAG機構への合成方式）。

## 2. Completed Packages／Work Units

```text
P7-0 Entry／As-built Freeze                                          完了
P7-A Attachment Sizing                                                完了（Chat Composer統合はPhase 10延期）
P7-B Corpus／Document Lifecycle（Local Corpus）                        完了
P7-C Embedding／Index／Retriever（BM25 Baseline維持）                   完了
P7-D Context Injection／Citation Persistence（Local Corpus）            完了
P7-E Web Search／Fetch（Fixture Provider、実httpx Adapter）              完了
P7-F Web Security／Evidence Governance（SSRF対策、Prompt Injection）      完了
P7-G Data Controls                                                    完了
P7-H Integration／Observability／Regression                           完了
P7-I Internal Review（2 Cycle）／Final Verification／Return             完了
```

## 3. Changed Paths

### 3.1 Backend 新規（29 File）

```text
modules/documentation_rag/local_corpus_contracts.py
modules/documentation_rag/local_corpus_ports.py
adapters/documentation_rag/local_corpus_registry.py
adapters/documentation_rag/local_corpus_document_source.py
adapters/documentation_rag/composite_document_source.py
web/local_corpus_contracts.py
web/local_corpus_routes.py
modules/web_knowledge/__init__.py, contracts.py, ports.py
modules/web_knowledge/domain/__init__.py, url_security.py,
  prompt_injection_detector.py, secret_detector.py
modules/web_knowledge/application/__init__.py, web_knowledge_service.py
adapters/web_knowledge/__init__.py, fixture_providers.py, httpx_fetch_provider.py
bootstrap/web_knowledge.py
web/web_search_contracts.py, web_search_routes.py
modules/data_controls/__init__.py, contracts.py, ports.py
adapters/data_controls/__init__.py, json_file_consent_store.py
web/data_controls_contracts.py, data_controls_routes.py
```

### 3.2 Backend 変更（9 File）

```text
modules/documentation_rag/contracts.py（corpus_source_class Field追加、既存Default値保持）
adapters/documentation_rag/markdown_chunker.py, bounded_context_assembler.py, __init__.py
bootstrap/documentation_rag.py（local_corpus_registry合成引数追加）
web/contracts.py（WebRuntimeへ3 Feature分Field追加）
web/app.py（Router登録・Exception Handler・Bootstrap Marker・Loopback二重Gate×3）
bootstrap/web_application.py（3 Feature分引数追加）
entrypoints/web/main.py（CLI Flag×8追加：--phase-7-local-corpus,
  --local-corpus-runtime-data-root, --local-corpus-scope-id, --phase-7-web-search,
  --phase-7-web-search-governance-mode, --phase-7-data-controls,
  --data-controls-runtime-data-root, --data-controls-scope-id）
```

### 3.3 Backend Test 新規（14 File）／変更（2 File）

```text
新規: tests/unit/documentation_rag/{test_local_corpus_registry,
  test_local_corpus_document_source, test_composite_document_source}.py
  tests/integration/documentation_rag/test_local_corpus_end_to_end.py
  tests/integration/web/{test_local_corpus_web_app, test_web_search_web_app,
  test_data_controls_web_app}.py
  tests/unit/web_knowledge/{conftest, test_url_security, test_prompt_injection_detector,
  test_secret_detector, test_web_knowledge_service, test_httpx_fetch_provider}.py
  tests/unit/data_controls/test_json_file_consent_store.py
変更: tests/unit/documentation_rag/test_bootstrap.py（+2）、
  tests/unit/web/test_web_cli.py（既存Fake Builder Signature更新のみ、+0）
```

### 3.4 Frontend 新規（9 File）

```text
lib/{localCorpusBootstrap, webSearchBootstrap, dataControlsBootstrap}.ts
components/{LocalCorpusPanel, WebSearchPanel, DataControlsPanel}.tsx
components/{LocalCorpusPanel, WebSearchPanel, DataControlsPanel}.test.tsx
```

### 3.5 Frontend 変更（8 File＋Build出力）

```text
index.html（Bootstrap Marker×3追加）
types.ts, api/client.ts, App.tsx, components/SettingsPanel.tsx
components/SettingsModal/SettingsModal.tsx, SettingsModal.test.tsx
i18n/translations.ts（ja/en 各37 Key追加）
Build出力: web/static/{index.html, app.js, app.css}
```

### 3.6 Docs（Recovery Index／Handoff、8 File）

```text
history/index/phase_7_current_claude_task_{p7_0, p7_a, p7_bcd, p7_ef, p7_gh, p7_i_final}
  _recovery_ja_*.md
handoffs/phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md
  （本書）
```

## 4. Requirements／32 Acceptance Disposition

P7-I Recovery Index §6の表を正本とする。要約：**PASS 27／PARTIAL 1（P7-ACC-008、
Embedding未使用は設計通り）／Web部分のみN/A相当 4件（P7-ACC-011/013/014/015、
Local Corpus側は全てPASS、Finding-002のScope境界に起因）／NOT RUN 1（P7-ACC-032、
Real Browser User Manual Gate）**。捏造・過大Claimなし。

## 5. Focused／Canonical Verification

```text
Backend pytest（Full Suite） : 1924 passed, 7 deselected
mypy（Project既定）          : Success、526 source files
ruff check . / format --check .: All checks passed／All formatted
frontend: typecheck／lint    : Clean
frontend: npm test           : 256 passed（28 files）
frontend: npm run build      : Clean
tests/integration/web（全体）: 195 passed
```

新規Backend Test Node ID: Baseline（R28末）1811 → 1924、純増113件（Package別内訳は
  P7-B/C/D/E/F/G/Iの各Recovery Index参照、`pytest --collect-only`による機械算出で
  各時点ごとに一致確認済み）。
新規Frontend Test: Baseline（R28末）232 → 256、純増24件。

## 6. Internal Review／Rework結果

2 Cycle実施。Finding 4件検出（Major 2件、Observation 2件）。

```text
Finding-001（Major）: Web Search Outbound QueryへのSecret様Pattern検査欠落 → Rework実施・Fixed。
Finding-002（Major）: Web Search Chat Context非統合 → Deferred（Requirements自体が
  automatic Tierの責務と規定、本TaskではAutomatic未実装を既に開示済み、新規発見ではなく
  既存Scope境界の再確認。Closure Blockerに該当しないと判定——根拠は本書§1及びP7-I
  Recovery Index §7）。
Finding-003（Observation）: Embedding Identity Evidence欠如 → 設計通り（Not Reproducible）。
Finding-004（Observation）: Web Citation永続化N/A → 設計通り（Not Reproducible、Finding-002に起因）。
```

詳細はP7-I Recovery Index参照。

## 7. Attachment Sizing Decision

P7-A Recovery Index参照。Chat Composer統合（汎用File Attachment Button、Per-turn一時添付）は
Phase級と判定しPhase 10以降へ延期。局所化5項目（Transport／Metadata／Safe Storage／Text
Extraction／RAG Ingestion）はLocal Corpus（P7-B）のSettings経由登録として実現し、
Attachment Subsystem新設を回避した。

## 8. Real Network／Browser／User Data Action Inventory

```text
Real Network Action: 0（P7-E/F Recovery Index §1で明示——無Credential Search API不在のため
  Real Public Web Probe不実施、Fixture Provider Pairが本Taskの実Runtime Composition）。
Real Browser Action: 0（本Claude TaskはReal Browser Authorityを持たない）。
User Runtime Data（runtime_data/）Action: 0（全TestはPytest tmp_path Fixtureを使用、
  実運用時のみ`runtime_data/persistent/**`配下へ書く設計だが、本Task内では一切触れていない）。
Git Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

## 9. Known Findings／Deferrals

```text
P1〜P2:
- Finding-002: Web Search Chat Context非統合（本書§1参照、意図的Scope境界）。
- Web Search Automatic Activation（P7-REQ-013 Trigger Heuristics）未実装。
- DNS解決結果IPのSocket接続直接Pinning未実装（DNS Rebinding耐性、Phase 10 Hardening）。
- Local Corpus DocumentのTitle変更でChunk/Source ID再生成（旧Citation Path変更、実害小）。
- Data Controls「Export」はPolicy JSON取得のみ、「Delete」はConsent Resetのみ
  （Conversation／Local Corpus実データの横断的Export／一括消去は未実装）。
- Chat Composer汎用File Attachment（Phase 10延期、P7-A判定）。
```

上記は全て`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`への
反映をController判断に委ねる（本Claude TaskはStable未解決Registryへの直接書込み権限を
持たない）。

## 10. Active Process／Temporary Artifact

```text
Active Process: 0（本Task内でServer起動・Model Load等は一切行っていない）。
Temporary Artifact: 0（全Test Fixtureはpytest tmp_path／vitest内で自動Cleanup）。
```

## 11. Maximum Claim

**COMPLETE_CANDIDATE**

Active Scope（P7-0〜P7-H）の実装完了、Internal Review 2 Cycle以内、Open Critical 0、
Open Major 1件（Deferred・理由明記、Closure Blocker非該当）、Required Verification全成立。
Phase 7 Closure、Git、Backup、Roadmap、Phase 8のいずれも本Claudeからは着手していない。

## 12. Exact Next Action

**Codex Controller Bounded Independent Review待ちで停止する。**

Review範囲の推奨（Handoff §6／PoC-MVP Operating Policy §12に基づく）：

```text
中心主経路: Local Corpus登録→検索→引用→永続化（既存Chat Pipeline完全統合）が実際に動くか。
Web Search Manual Golden Path（Fixture Provider経由）が実際に動くか。
Data Integrity: 既存Conversation／Citation／Branch／Regenerate／Recording／Stopへの
  Regressionがないか（本Return §5・P7-I Recovery Index §5のEvidenceに基づく確認）。
Network副作用: RAG OFF／Web検索OFF双方でNetwork Call 0が真に保証されているか。
本書§1のScope境界（Web Search Chat非統合）が、Controller・User双方に正確に伝わっているか。
```

Phase 7 Closure、Git、Backup、Roadmap、Phase 8開始のいずれも行わず、本Returnをもって停止する。
