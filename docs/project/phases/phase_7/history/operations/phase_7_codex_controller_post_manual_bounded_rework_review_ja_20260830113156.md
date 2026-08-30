# Phase 7 Post-Manual Bounded Rework — Codex Controller Review

```yaml
document_id: phase_7_codex_controller_post_manual_bounded_rework_review_20260830113156
document_type: controller_bounded_independent_review
document_state: current_decision
language: ja
created_at: 2026-08-30 11:31:56 JST
authority_owner: Nazuna Research
phase: phase_7
review_scope: P7-CODEX-007_to_P7-CODEX-009
verdict: ACCEPT_COMPLETE_CANDIDATE_WITH_USER_MANUAL_RECHECK
phase_7_closure: not_claimed
```

## 1. Review対象／停止線

対象は次のClaude Exact Returnと、P7-CODEX-007〜009へ直接関係するSource／Test／Recoveryに限定した。

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_post_manual_bounded_rework_exact_return_handoff_ja_20260830113500.md
SHA-512: 3f7cfa96053bae65cfe4385c40d73a9c3934566089f5a2a818a15ed5440782ec9a9cb0456441fa205e16152fb4ca50ba16d4df218aee2ad20e0d2d8ced875166
```

申告Digestは実Fileと一致した。新しいFinding探索、External Web、Phase 8、Phase 6 Debt、Embedding、Vector DB、Full Export／一括Deleteまたは製品化HardeningへScopeを拡張していない。

## 2. P7-CODEX-007 — Citation Projection

### 2.1 Source照合

- `DocumentationCitation`へBackward-compatible default付き`source_class`が追加された。
- `SystemCitationAdapter`がReference Blockの`source_class`をCitationへ渡す。
- Live SSEとPersistent Detailの両方が`source_class`、`chunk_id`、`document_sha512`を投影する。
- Frontend `Citation`型がBackend Projectionと一致する。
- UIはLocal Corpus／Project Docsを明示し、Chunk ID／Document Digestを短縮表示しつつ完全値のCopyを提供する。
- 過去Recordで`source_class`がない場合、既存Project Docs Source Class既定値でDecodeする。

### 2.2 判定

```text
Disposition: ACCEPTED COMPLETE CANDIDATE
P7-ACC-012: USER MANUAL RECHECK後にPASS昇格可能
```

## 3. P7-CODEX-008 — Current Turn Freshness

### 3.1 Source照合

- BM25 Top-k BackfillはQuery側にIdentifier Tokenがある場合、Identifierと無関係なChunkをBackfillしない。
- Exact Manual Probe削除後、無関係なPhase 1 Docsは選択されず`NO_HIT`へ収束する。
- `NO_HIT` Turnでは、現在のCorpusで再確認できない過去Assistant FactをCurrent Factとして断定しないよう、専用Tool Noticeを現Turnへ挿入する。
- 過去Citation／Revision／DigestをCurrent Revisionへ書き換える経路は追加されていない。
- 登録→rev 1質問→rev 2更新→再質問→削除→同一Context相当再検索→新規Context相当再検索→過去Evidence不変の8手順Fixtureが成立する。

### 3.2 Controller限定

RAG Retrievalは無関係Citationを構造的に排除する。一方、削除後の最終自然言語回答はMain ModelがCurrent Freshness Noticeへ従うことを含む。FixtureはRetrieval／Prompt構成を証明するが、User Mac上のQwen実出力までは代行しない。

したがって、Source上の追加Reworkはこの時点で要求せず、Exact Manual ProbeをUser実画面で再確認する。ModelがNoticeを無視して旧Factを断定する場合だけ、Identifier付きNO_HITのDeterministic Presentation Gateを次のBounded Rework候補とする。

### 3.3 判定

```text
Disposition: ACCEPTED COMPLETE CANDIDATE WITH USER MANUAL RECHECK
Historical Citation Immutability: PASS
Current Retrieval Unrelated Citation Rejection: PASS
Real Model Final Answer Freshness: USER MANUAL GATE
```

## 4. P7-CODEX-009 — Lazy Auto-Resume

### 4.1 Source照合

- Server起動時に全Conversationを一括Resumeする処理は追加されていない。
- `generate_turn()`／`generate_derived_turn()`が、Active ConversationかつActive Sessionなしの場合だけ遅延Resumeする。
- Archived／Deleted Conversationは自動Resumeしない。
- Lazy Resume IdentityはAppend Operationから決定論的に導出される。
- Bounded CAS RetryでStale Revisionを再読し、Active Session重複を防ぐ。
- Restart RecoveryでInterruptedとなった過去Turnは変更しない。
- SidebarのManual Resume Action／翻訳は除去され、Backend Resume APIは互換性のため保持された。

### 4.2 Controller限定

Double Tab Testは同じStale Revisionを順次投入するDeterministic CAS Testであり、実Thread同時実行そのものではない。ただし現在PoC／MVPのUser主経路とCAS Contractを確認するには十分であり、追加Concurrency HardeningをClosure Blockerへ昇格しない。

### 4.3 判定

```text
Disposition: ACCEPTED COMPLETE CANDIDATE
Real Browser Restart／Unarchive: USER MANUAL RECHECK
```

## 5. Independent Focused Verification

ControllerはCanonical Fullを理由なく再実行せず、必須RegressionだけをProject内Task-owned Tempで再実行した。

```text
Backend Focused:
  11 passed / 122 deselected / Exit 0

対象:
  Nazuna Probe Orion Update/Delete
  BM25 Identifier Backfill
  NO_HIT Freshness Notice
  Legacy Citation Decode
  Citation Reload Projection
  Restart／Unarchive Lazy Resume
  Archived Session 0
  Stale Revision Double Tab CAS

Frontend Focused:
  2 files / 14 tests passed / Exit 0

対象:
  Citation Identity表示／Copy
  Sidebar Resume Action除去
```

Claude Canonical Evidenceは変更後最終状態で次の通りであり、Controllerは再利用する。

```text
Backend: 1934 passed / 7 deselected
Mypy: 526 files / 0 issues
Ruff check/format: PASS
Frontend: 29 files / 259 tests
Frontend typecheck/lint/build: PASS
```

## 6. Claim Correction／Incident

Claude Return §9は`git checkout -- lexical_tokenizer.py`を`Git Read-only Action`として記載したが、`git checkout`はWorking Treeを復元するMutation Actionであり、Read-onlyではない。

```yaml
finding_id: P7-CODEX-010
severity: minor_operational_claim_mismatch
priority: P2
closure_blocker: false
actual_git_action: restorative_working_tree_mutation_1
net_semantic_diff_from_abandoned_experiment: 0
stage_commit_branch_push_network: 0
```

試行Heuristicを撤回してBaselineへ戻す目的で、User Data消失、Stage、Commit、Branch、PushまたはNetworkを伴わない。Userが定めたPoC／MVP停止線に従い、新しいRework CycleまたはSafe Stopを起動しない。事実だけを本Reviewで訂正する。

## 7. Verdict

```text
P7-CODEX-007: ACCEPTED COMPLETE CANDIDATE
P7-CODEX-008: ACCEPTED WITH REAL MODEL USER MANUAL RECHECK
P7-CODEX-009: ACCEPTED WITH REAL BROWSER USER MANUAL RECHECK
Open Critical in Current Scope: 0 known
Open Major requiring Source Rework before Manual: 0 known
Phase 7 Closure: NOT CLAIMED
Exact Next Action: User Manual限定再確認
```

User ManualでP7-CODEX-008または009の実害Failureが再現した場合だけ、結果をまとめて次のBounded Reworkへ戻す。PASSした場合は、P7-ACC-012およびP7-ACC-032の現Phase対象を昇格し、Phase 7 Closureへ進める。

