# Phase 7 Non-Web Scope／Acceptance Addendum（Append-only）

```yaml
document_id: phase_7_non_web_scope_and_acceptance_addendum_20260829225200
document_type: append_only_scope_and_acceptance_reclassification_addendum
document_state: current_decision
language: ja
created_at: 2026-08-29 22:52:00 JST
supersedes: none_append_only
amends_by_reference:
  - operations/phase_7_acceptance_matrix_ja.md（Frozen、削除・改竄しない）
  - handoffs/phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md
  - history/operations/phase_7_codex_controller_bounded_independent_review_adjust_ja_20260829215534.md
  - history/operations/phase_7_external_web_runtime_phase_11_plus_deferral_decision_ja_20260829222647.md
source_task: current_claude_phase_7_task
package: P7-NW-A
```

## 1. 本書の位置付け

本書はAppend-onlyであり、`phase_7_acceptance_matrix_ja.md`（Frozen）の32項目を削除・上書きしない。2026-08-29のUser Decision（実Web機能をPhase 11以降へ延期）を踏まえ、各Acceptance IDを`CURRENT_PHASE_APPLICABLE`／`DEFERRED_TO_PHASE_11_PLUS`／`CURRENT_KNOWN_PARTIAL_NON_BLOCKING`へ個別再導出し、Evidence Pointerを付す。一括`Regression 0`のみでの代替は行わない。

分類は`phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md` §4 P7-NW-Aで指定された最低限の割当を正本とし、そこに含まれないID（005〜007, 009, 010, 012〜015, 026, 027, 029〜031等）は、既存Evidence（P7-I Final Recovery §6、Controller Review §7）から本書が個別に再導出する。

## 2. 32 Acceptance 個別Disposition

| ID | Class | Disposition | Evidence Pointer |
|---|---|---|---|
| P7-ACC-001 | CURRENT_PHASE_APPLICABLE | PASS | Phase 2 Citation／Conversation Contract無変更。Backend Full `1924 passed, 7 deselected`（P7-I Recovery §5）。本Taskでも当該Sourceに変更なし。 |
| P7-ACC-002 | CURRENT_PHASE_APPLICABLE | PASS | RAG OFFでRetrieval／Injection Call 0。既存Phase 2 Gate無変更（P7-I Recovery §6）。 |
| P7-ACC-003 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | Web検索OFFはFrontend Local State（`webSearchMode`）のみでServer Canonical未成立（P7-CODEX-003）。Server Canonical `disabled／manual` Snapshotの新設はHard Scope Exclusion（Handoff §6）。未解決Registry `UF-P7-001`。 |
| P7-ACC-004 | CURRENT_PHASE_APPLICABLE | PASS | Local Document登録。`adapters/documentation_rag/local_corpus_registry.py`、`tests/unit/documentation_rag/test_local_corpus_registry.py`（12 tests）。 |
| P7-ACC-005 | CURRENT_PHASE_APPLICABLE | PASS | Append-only Revision Chain。同上Test群、Controller Focused Review「Local Corpus: ACCEPTED BASELINE」（Controller Review §1／§3.1）。 |
| P7-ACC-006 | CURRENT_PHASE_APPLICABLE | PASS | Soft-delete、Current／Historical分離。`test_local_corpus_registry.py`、`test_composite_document_source.py`（4 tests）。 |
| P7-ACC-007 | CURRENT_PHASE_APPLICABLE | PASS | 既存`markdown_chunker.py`の再利用、`corpus_source_class` Fieldで Local Corpus由来Chunkを識別（Chunk ID／DigestはDocument Revisionへ結び付く、既存機構）。 |
| P7-ACC-008 | CURRENT_KNOWN_PARTIAL_NON_BLOCKING | PARTIAL | BM25 Retriever／Index Identity（`retriever_key/version`）のみEvidence化。Embedding実体は本Task・本Addendumのいずれでも追加しない（Handoff §4／§6でEmbedding Model／Vector DB追加を明示的に禁止）。PASSへ捏造しない。 |
| P7-ACC-009 | CURRENT_PHASE_APPLICABLE | PASS | 既存`RetrievedChunk`構造（Candidate／Selected区別、Score）をLocal Corpusでも再利用（変更なし）。 |
| P7-ACC-010 | CURRENT_PHASE_APPLICABLE | PASS | No Relevant Evidenceを回答根拠ありへ変換しない既存Grounding State機構。Local Corpus検索0件時も同一機構が適用される（`test_local_corpus_end_to_end.py`）。 |
| P7-ACC-011 | CURRENT_PHASE_APPLICABLE（Local Corpus部分）／DEFERRED_TO_PHASE_11_PLUS（Web部分） | PASS（Local）／DEFERRED（Web） | Context Injectionへ選択Evidenceのみを渡す経路はLocal Corpus側で既存機構どおり成立（P7-I Recovery §6 `P7-ACC-011 PASS（Local Corpus）`）。Web側はManual Search Panelが独立UtilityでMain Model Context Injectionへ到達しないため対象外（Finding-002／P7-CODEX-002）。 |
| P7-ACC-012 | CURRENT_PHASE_APPLICABLE | PASS | Document／Chunk／Digest／Source IdentityはLocal Corpus Citationで完備（既存Phase 2 Citation機構＋`corpus_source_class`）。Web Citation側はP7-ACC-011と同じ理由でPhase 11以降Scope。 |
| P7-ACC-013 | CURRENT_PHASE_APPLICABLE（Local Corpus部分）／DEFERRED_TO_PHASE_11_PLUS（Web部分） | PASS（Local）／N/A→DEFERRED（Web） | Reload後のCitation復元はLocal CorpusがPhase 2既存永続化機構をそのまま利用（PASS）。Web EvidenceはServer側に一切永続化されない設計（Data Controls Retention Fact `public_web: retained=False`）ため、復元対象自体が存在しない（Finding-004、not_reproducible ではなく本Addendumでは`DEFERRED_TO_PHASE_11_PLUS`へ整理——Phase 11でWeb Citation永続化を設計する際に再定義）。 |
| P7-ACC-014 | 同上 | PASS（Local）／DEFERRED（Web） | Server Restart後のCitation復元。理由はP7-ACC-013と同一。 |
| P7-ACC-015 | 同上 | PASS（Local）／DEFERRED（Web） | Branch／Regenerate／Resume後の正しいCitation分岐。理由はP7-ACC-013と同一。既存Conversation Branch機構は無変更。 |
| P7-ACC-016 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED（Controller: PARTIAL — Provider Port Golden Pathのみ） | `bootstrap/web_knowledge.py`は`FixtureWebSearchProvider`固定。Real Web Searchは未接続（P7-CODEX-001）。 |
| P7-ACC-017 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | Snippet／Fetched Content構造分離はPort契約として存在するが、Fixtureスコープのみ。 |
| P7-ACC-018 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | Canonical URL等のEvidence化はFixtureスコープのみ。 |
| P7-ACC-019 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | Source Authority Classification（Heuristic）はFixtureスコープのみ。 |
| P7-ACC-020 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | Private／Loopback／Metadata Endpoint拒否は`url_security.py`として実装・19 Testで検証済みだが、保護対象のReal Web Fetch自体が未接続のためAcceptance対象機能はPhase 11以降（Security Scaffoldとして保持、Handoff §3.2）。 |
| P7-ACC-021 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | 危険Scheme／Redirect／巨大Response／Timeout有界化は`httpx_fetch_provider.py`として実装済みだが、同様の理由でPhase 11以降。 |
| P7-ACC-022 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED | Secret様Pattern検査（`secret_detector.py`）は実装・Test済みだが、PII候補検査と外部送信Consent Enforcementの実行経路接続が未成立（P7-CODEX-004）。Scaffoldとして保持。 |
| P7-ACC-023 | CURRENT_PHASE_APPLICABLE（Local Context Source部分）／DEFERRED_TO_PHASE_11_PLUS（Web Fetched Content部分） | PASS（Local）／DEFERRED（Web） | Local Corpus文書は既存Phase 5 `guardrail.context_source`機構（`CONTEXT_SOURCE_CLASS_DOCUMENTATION_RAG_CITATION`）をP7-NW-0 §4観点1で確認済みのとおり迂回なく通過し、Detection Evidence経路は無変更。Web Fetched Content専用の`modules/web_knowledge/domain/prompt_injection_detector.py`（OFF/OBSERVE/ENFORCE）はPort実装・Test済みだが、Chat非接続のためPhase 11以降Scope。 |
| P7-ACC-024 | DEFERRED_TO_PHASE_11_PLUS | DEFERRED（Handoff §4 明示指定） | Web Search Toggleの表示位置・既存Toggle形式自体は`SettingsModal.test.tsx`でDOM順序を直接確認済み（技術的にはPASS相当）だが、本Acceptance項目はWeb Search Activationを対象とするため、Web機能全体の延期に合わせてAcceptance credit自体をDeferredへ整理する（Handoff §4の最低限指定に従う）。実装・Testそのものは削除しない。 |
| P7-ACC-025 | CURRENT_PHASE_APPLICABLE | PARTIAL | Source／Retention／External Transmission Consent／Purpose別Consentの4軸は`DataControlConsent`／`RetentionFact`で構造的に分離済み（PASS）。「Export」「Delete」は独立したData Lifecycle操作として実装しておらず（APIは`/policy` `/consent` `/reset`の3経路のみ、Export／一括Delete Routeは存在しない）、UI／API側もこれを実行可能であるかのように表示していない（本Addendム作成時に`DataControlsPanel.tsx`／`data_controls_routes.py`／全`dataControls*`翻訳キーを確認、虚偽Capability表示なし）。この欠落は元Return Handoff §9で既に開示済みの意図的Scope縮小であり、Hard Scope Exclusion（Handoff §6「全Data Export／Delete」）により本Task・本Addendムでも追加しない。 |
| P7-ACC-026 | CURRENT_PHASE_APPLICABLE | PASS | Feedback／Synthetic／Future Training利用Default OFF。`test_json_file_consent_store.py`。 |
| P7-ACC-027 | CURRENT_PHASE_APPLICABLE | PASS | `test_saving_consent_never_claims_training_occurred`。Consent保存＝Training実施ではないことをTestで直接確認。 |
| P7-ACC-028 | CURRENT_PHASE_APPLICABLE（非Web部分）／DEFERRED_TO_PHASE_11_PLUS（Web Provider／Network投影部分） | PASS（非Web）／DEFERRED（Web） | Local Corpus・Data Controls経路のFailure Reason／Stage／Request ID表示は既存機構どおり正直（Local Corpus Request IDはConversation既存相関を利用）。Web側`network_calls_made`がFixture Port Callを実Networkのように数える不正確さ（P7-CODEX-005）はPhase 11以降で`provider_calls_attempted`／`outbound_network_calls_attempted`分離として再開（未解決Registry `UF-P7-002`）。本Taskでは単独Rework Loopを作らない（Handoff・Registry双方の既存指示どおり）。 |
| P7-ACC-029 | CURRENT_PHASE_APPLICABLE | PASS | Conversation／Branch／Recording／Stopに重大Regressionなし。Backend Full `1924 passed`（本Taskで未変更のため再利用、Verification Contract §5.1）。 |
| P7-ACC-030 | CURRENT_PHASE_APPLICABLE | PASS | Attachment Sizing採用／延期（Phase 10延期）の判定根拠はP7-A Recovery Indexに既存。 |
| P7-ACC-031 | CURRENT_PHASE_APPLICABLE | PASS | 本Taskは変更範囲がDocs（Addendum、Recovery Index、Manual Test Sheet、Return Handoff）のみであり、Source／Test変更0件。Canonical Full Suiteの無意味な再実行はせず、P7-I成立Evidence（Backend `1924 passed`／Mypy `526 files clean`／Ruff clean／Frontend `256 passed`／typecheck／lint／build clean）を再利用する（Verification Contract §5.1、Controller Focused Evidence Backend `111 passed`／Frontend `4 files／39 tests`も併せて再利用）。 |
| P7-ACC-032 | CURRENT_PHASE_APPLICABLE（Local Corpus／Citation／Data Controls User Gate部分）／DEFERRED_TO_PHASE_11_PLUS（Web Source部分） | USER MANUAL GATE／NOT RUN | 本Task（P7-NW-D）で[Manual Test Sheet](phase_7_local_corpus_data_controls_user_manual_test_sheet_ja_20260829225900.md)を作成した。Real Browser実行はClaudeのAuthority外であり、User自身が実施する。Web Source確認項目はManual Test Sheetに含めない（Phase 11以降）。 |

## 3. 集計

```text
CURRENT_PHASE_APPLICABLE（純PASS）        : 001,002,004,005,006,007,009,010,026,027,029,030,031（13件）
CURRENT_PHASE_APPLICABLE（PASS、Local側） : 011,012,013,014,015,023,028（Local／非Web部分、7件。Web側は個別にDEFERRED）
CURRENT_PHASE_APPLICABLE（PARTIAL）       : 025（1件、Export／Delete非実装は意図的Scope縮小・既開示）
CURRENT_KNOWN_PARTIAL_NON_BLOCKING        : 008（1件、Embedding未使用は設計通り）
DEFERRED_TO_PHASE_11_PLUS（純Deferred）   : 003,016,017,018,019,020,021,022,024（9件）
USER MANUAL GATE／NOT RUN                 : 032（1件、Local部分のみ現Phase対象。Web部分はDeferred）
```

Open Critical: 0。Open Major（Non-Web Scope内）: 0。Web Scope内のMajor 5件（P7-CODEX-001〜005）はPhase 11以降へ既に再分類済み（本書§1参照、本書では新規Findingとして扱わない）。

## 4. 訂正されるClaim

```text
訂正前（旧Return Handoffの含意しうる誤読）:
  「Phase 7でWeb Search／FetchのPort、Security、Governance機構を実装した」
  という記述だけを読むと、実Web検索が使えるかのように誤解され得る。

訂正後（本Addendumで明示するClaim）:
  Phase 7で完成したのは、Local Corpus／Citation／Data ControlsのMVP主経路と、
  将来のExternal Web Runtimeへ接続可能なProvider Port／Fixture／Security
  Scaffoldである。実External Provider、Network Call、Web-grounded Chatは
  未実装であり、Phase 11以降へ延期した（External Web Runtime Phase 11+
  延期Decision §9と同一文言）。
```

本書はこのClaim訂正を、Frozen Requirements／Architecture／Acceptance Matrixを書き換えることなく、Append-onlyで固定する。

## 5. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation: 0（本書はDocs追加のみ）
```

Exact next action: P7-NW-B／P7-NW-C（Local Corpus／Data Controls Closure Readiness確認）へ連結して進む。
