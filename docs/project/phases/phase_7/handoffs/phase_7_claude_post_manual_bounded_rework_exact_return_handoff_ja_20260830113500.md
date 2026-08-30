# Phase 7 Claude Post-Manual Bounded Rework — Exact Return Handoff

```yaml
document_id: phase_7_claude_post_manual_bounded_rework_exact_return_handoff_20260830113500
document_type: exact_return_handoff
document_state: final
language: ja
created_at: 2026-08-30 11:35:00 JST
provider: Claude
role: 設計者兼実装者役
phase: phase_7
active_contract: phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
```

## 1. Status

P7-RW2-0からP7-RW2-Dまで、Handoff指示通り連結実行した。User Mac Manual Acceptance（ADJUST判定）が指摘したP7-CODEX-007（Citation Chunk／Digest Projection Gap）、P7-CODEX-008（Current Turn Freshness／Unsupported Historical Reuse）、P7-CODEX-009（Manual Resume Required）の3件を、指定Scope内で修正・検証した。P7-0〜P7-IおよびP7-NW-0〜Eの既存成立Baselineは再実装していない。実Web Rework（P7-CODEX-001〜005）には一切触れていない。

## 2. Completed Work Units

```text
P7-RW2-0 Entry／Regression Freeze                    完了（Digest照合、再現経路固定）
P7-RW2-A Citation Identity Projection                完了（P7-CODEX-007）
P7-RW2-B Current Turn Freshness／Grounding            完了（P7-CODEX-008）
P7-RW2-C Lazy Auto-Resume                             完了（P7-CODEX-009）
P7-RW2-D Verification／Internal Review（1 Cycle）／Return 完了
```

## 3. Changed Paths

### 3.1 P7-RW2-A（Citation Identity Projection）

```text
Backend Source:
  src/margpa_runtime_llm/modules/documentation_rag/contracts.py
    -> DocumentationCitationへsource_class Field追加（既定値付き）。
  src/margpa_runtime_llm/adapters/documentation_rag/system_citation_adapter.py
    -> source_classをCitationへ渡す1行追加。
  src/margpa_runtime_llm/web/persistent_contracts.py
    -> PersistentCitationResponseへsource_class／chunk_id／
       document_sha512の3 Field追加、_project_turn_citations()を対応。
  src/margpa_runtime_llm/web/persistent_streaming.py
    -> Live SSE RETRIEVAL投影へ同3 Field追加。

Backend Test:
  tests/integration/web/test_persistent_web_app.py
    -> Live SSE Projection Test／Persistent Detail Projection Test／
       Source Class区別Testを兼ねるAssertion拡張。
  tests/unit/conversation/test_citation_evidence_sqlite_store.py
    -> 旧Record（source_class欠落）のBackward Compatibility Test新規追加。

Frontend Source:
  frontend/src/types.ts
    -> Citation型へsource_class, chunk_id, document_sha512,
       retrieval_score, selected_order, truncatedを追加。
  frontend/src/components/CitationsSection.tsx
    -> Local Corpus／Project Docs明示Label、Chunk ID／Document Digest
       短縮表示＋完全値Copy Button追加。
  frontend/src/i18n/translations.ts
    -> citationSourceLocalCorpus, citationSourceProjectDocs,
       copyChunkId, copyDocumentDigest（ja/en）追加。

Frontend Test:
  frontend/src/components/CitationsSection.test.tsx（新規4 Test）
```

### 3.2 P7-RW2-B（Current Turn Freshness／Grounding）

```text
Backend Source:
  src/margpa_runtime_llm/adapters/documentation_rag/bm25_retriever.py
    -> Top-k Backfill Loopへ、Query側Identifier Tokenと無関係な
       Chunkを除外するGuardを追加。
  src/margpa_runtime_llm/modules/conversation/application/
  conversation_generation.py
    -> NO_HIT状態専用の独立した非Budget Freshness Notice Messageを
       新設し、_inject_documentation_reference()から注入。

Backend Test:
  tests/unit/documentation_rag/test_lexical_retrieval.py
    -> Backfill Guardの新規3 Test（削除後除外、実在時は正常検出、
       Identifier不在時は無影響）。
  tests/integration/documentation_rag/test_local_corpus_end_to_end.py
    -> Handoff §7.3 Required Regression Scenario 8手順を再現する
       test_nazuna_probe_orion_freshness_update_delete_regression
       を新規追加。
  tests/unit/conversation/test_conversation_generation.py
    -> NO_HIT Freshness Notice投影の新規Test追加。

試行して撤回したApproach（P7-RW2-B Recovery §1参照）:
  adapters/documentation_rag/lexical_tokenizer.pyへのTitle-Case-Run
  Subject検出Heuristicは、本Project自体の語彙（"Runtime Governance"等）
  でMaterial Regressionを起こしたため、git checkoutで完全に撤回した
  （現在HEADと同一、Diff 0）。
  bounded_context_assembler.pyのREFERENCE_INSTRUCTION文言拡張も、
  既存Tight Budget Testとの衝突により撤回した（現在は本Task開始前と
  同一内容）。
```

### 3.3 P7-RW2-C（Lazy Auto-Resume）

```text
Backend Source:
  src/margpa_runtime_llm/modules/conversation/application/
  persistent_conversation_service.py
    -> _lazy_resume_operation_id／_lazy_resume_session_id（新設）、
       _ensure_active_session（新設）、generate_turn／
       generate_derived_turnをBounded CAS Retry Loopへ書き換え。

Backend Test:
  tests/unit/conversation/test_persistent_conversation_service.py
    -> 新規4 Test（Restart後自動Resume、Unarchive後自動Resume、
       Archivedのまま拒否、Double Tab相当競合でSession exactly one）。

Frontend Source:
  frontend/src/components/Sidebar/ChatListItem.tsx
    -> ChatListAction型からresume除去、Resume Menu Item削除。
  frontend/src/i18n/translations.ts
    -> persistentResume（ja/en）除去。

Frontend Test:
  frontend/src/components/Sidebar/ChatListItem.test.tsx
    -> Resume特有Assertion除去、前提消滅Testを削除。
  frontend/src/App.test.tsx
    -> Resume依存Testをarchive Actionへ付け替え（同一Regression
       保護目的は保持）。

Build成果物（Frontend Sourceから再生成、手動編集なし）:
  src/margpa_runtime_llm/web/static/app.js
  src/margpa_runtime_llm/web/static/index.html
```

P7-0〜P7-IおよびP7-NW-0〜Eの既存Docs／Frozen Requirements／Frozen Acceptance Matrixはいずれも無改変。

## 4. P7-CODEX-007〜009 個別Disposition

```text
P7-CODEX-007: RESOLVED（本Task内でLive SSE／Persistent Detailの
  投影欠落を解消、Backward Compatible）。
P7-CODEX-008: RESOLVED_WITHIN_LEXICAL_SCOPE（Required Regression
  Scenario 8手順は全PASS。ただしUpdate直後・同一Chat内の1回限りの
  Freshness Flakinessは、LLM Sampling依存領域のためLexical Retrieval
  ScopeでのStructural Guaranteeの対象外——既存Observationとして
  Known／Deferred記録、新規Blockerではない）。
P7-CODEX-009: RESOLVED（Restart後／Unarchive後の最初の送信が手動
  Resumeなしで成功、Archivedは自動Resumeされず、Double Tab相当の
  競合でもActive Session exactly oneに収束、Sidebar Resume Button
  除去済み、Backend Resume APIは意図通り保持）。
```

## 5. Preserved Baseline Claim Correction

以前のP7-ACC-012（Citation Identity完備）PASS Claimは、User Mac Manual Acceptance（ADJUST）によりFAILへ訂正されていた。本Task完了により、P7-ACC-012はCOMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEWの範囲でPASSへ戻すCandidateとなるが、Claude自身はUser Manual Gate項目を自己PASS判定しない——Controller Independent ReviewおよびUser Mac再確認を経てから正式にPASSへ戻す。

P7-ACC-008（Embedding未使用PARTIAL）、P7-ACC-025（Full Export／一括Delete未実装PARTIAL）は無変更のまま維持する。External Web Runtime（P7-CODEX-001〜005）のPhase 11以降Deferredも無変更。

## 6. Verification

```text
uv run pytest -q                     -> 1934 passed, 7 deselected（Regression 0）
uv run mypy                          -> Success, no issues found in 526 source files
uv run ruff check .                  -> All checks passed
uv run ruff format --check .         -> 526 files already formatted

frontend: npx tsc --noEmit           -> エラーなし
frontend: npx eslint .               -> エラーなし
frontend: vitest run                 -> 29 files, 259 tests passed
frontend: npm run build              -> 成功（static/app.js／index.html再生成）
```

## 7. Internal Review／Rework

1 Cycle実施（P7-RW2-D）。観点はHandoff §9.2指定の6項目全て（P7-CODEX-007〜009 Requirement-by-Requirement、過去Evidence不変性、Current Turn Grounding、Resume Lifecycle／Race、API／SSE／Frontend Projection一致、Scope／Claim／Acceptance整合）。Critical 0、Major 0、MVP Blocker 0。

Minor Observation 1件（P7-RW2-IR-001：Update直後・同一Chat内の1回限りFreshness Flakiness、既存Observationの範囲内、非Blocking、Rework不要）。Rework Cycleは起動していない。

## 8. Known Partial／Deferred

```text
P7-RW2-IR-001（同一Chat内Update直後Freshness Flakiness、Minor、
  LLM Sampling依存のため本Bounded Scope外）
P7-ACC-008（Embedding未使用、設計通り、PARTIAL維持）
P7-ACC-025（Export／Delete非実装、意図的Scope縮小、PARTIAL維持）
P7-CODEX-001〜005（実Web Runtime、Phase 11以降既知Debt、無変更）
```

## 9. Incident／Boundary Inventory

```text
Real Network Action: 0
Real Browser Action: 0
User Runtime Data（runtime_data/）Action: 0
Git Mutation Action: 0
Git Read-only Action: 1（git checkout -- lexical_tokenizer.py、
  試行して撤回したHeuristicをHEADへ復元する目的、Source Mutation 0
  への復帰操作として実施、P7-RW2-B Recovery §1／7で開示済み）
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
Embedding／Vector DB／Full Export／一括Delete／Phase 6 Rework混入: 0
実Web Rework（P7-CODEX-001〜005）混入: 0
```

## 10. Active Process／Temporary Artifact

```text
Active Process: 0（本Task内でServer起動・Model Load等は一切行っていない。
  npm run buildはBuild Toolの実行であり、Runtime Server起動ではない）
Temporary Artifact: 0
```

## 11. Maximum Claim

**COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW**

P7-RW2-0〜P7-RW2-Cの作業完了、Internal Review 1 Cycle、Open Critical 0、Open Major 0（新規発生分）、Required Verification全成立、Handoff §7.3 Required Regression Scenario全PASS。Phase 7 Closure、Git Mutation、Backup、Roadmap、Phase 8のいずれも本Claudeからは着手していない。User Manual再確認をPASSへ代行していない。

## 12. Exact Next Action

**Codex Controller Bounded Independent Review待ちで停止する。**

Review範囲の推奨：

```text
P7-CODEX-007〜009それぞれについて、Handoffの要求Behaviorと本Task
  Evidenceが過不足なく対応しているか。
BM25 Backfill Identifier-Overlap Guardが、Handoffの必須Scenario
  以外の既存Query Pattern（一般的な低特定性Topic検索等）を意図せず
  過剰Filterしていないか（Canonical Suite Regression 0で裏付け済み）。
NO_HIT Freshness Noticeの挿入が、通常の一般会話（RAG無関係Query）を
  阻害していないか（should_generate=Trueが維持されていることを
  Contract Validatorで確認済み）。
Lazy Auto-Resumeの3方式比較（Frontend先行／Server-side lazy ensure／
  Bounded Combined Mutation）とServer-side lazy ensure選定の妥当性。
P7-RW2-IR-001（同一Chat内Update直後Freshness Flakiness）を、
  新たなBlockerとして扱うべきか、既存Observationの範囲内として
  Deferred継続するのが妥当か。
```

Phase 7 Closure、Git、Backup、Roadmap、Phase 8開始のいずれも行わず、本Returnをもって停止する。
