# Phase 8 Post-User-Manual Rework Controller Findings — Claude Bounded Exact Handoff

```yaml
document_type: exact_handoff
document_state: final
provider: Claude
role: designer_and_implementer
task_identity: current_continued_claude_task
task_state: continued_not_fresh
phase: phase_8
package: P8-MR7-0_through_P8-MR7-6
implementation_authority: true
independent_review_authority: false
phase_8_closure_authority: false
maximum_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
created_at: 2026-08-31 13:48:26 JST
```

## 1. Objective

Codex Controller Independent Reviewで検出したP8-CODEX-013〜018だけを差分是正し、Phase 8をUser Mac Manual Recheckへ渡せるCandidateへ収束させる。

今回はFresh Taskではない。現在のClaude Task／Context／Current Working Treeを継続し、Bootstrap、Role Reading、Mandatory Reading全件の再実行、新規Task初期化を行わない。

## 2. Active Contract／Differential Reading

次の差分文書を読み、Current Working TreeをCanonical Baselineとする。

1. Controller Review

```text
docs/project/phases/phase_8/history/operations/phase_8_post_user_manual_rework_controller_independent_review_adjust_ja_20260831134826.md
```

2. 本Exact Handoff

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_post_user_manual_rework_controller_findings_bounded_exact_handoff_ja_20260831134826.md
```

3. 直前Return／Recovery

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_post_user_manual_acceptance_bounded_rework_exact_return_handoff_ja_20260831132631.md
docs/project/phases/phase_8/history/index/phase_8_claude_post_user_manual_acceptance_bounded_rework_recovery_ja_20260831132631.md
```

4. 元のBounded Rework Contract

```text
docs/project/phases/phase_8/handoffs/phase_8_claude_post_user_manual_acceptance_bounded_rework_exact_handoff_ja_20260831122257.md
```

既読のPhase 8 Requirements／Architecture／Acceptance Matrix／共通Role Docsを最初から全文再読しない。差分の意味確認に必要な範囲だけ参照する。

## 3. Preserved Baseline

次は成立済みとして保持する。Rollback／再実装しない。

```text
P8-MANUAL-003 Archive Sidebar／Panel Synchronization
P8-MANUAL-004 Constitution Mode／Decision Layout
P8-MANUAL-005 Traceable Dev Agent Fixture／Approval Input／Output
P8-MANUAL-006 Dev Agent Button Contrast
P8-CR系Concurrency／Authorization Envelope／Approval Evidence／Budget／Completion Gate
P8-RW6 Redirect Evidence Truthfulness
P8-RW7 Constitution Preview 3-axis Semantics
```

## 4. Open Findings

```text
P8-CODEX-013 Resolver Injection／Test Hermeticity
P8-CODEX-014 ERROR-terminal Failure Web Evidence Persistence
P8-CODEX-015 Web Citation Schema 1／2 Backward Compatibility
P8-CODEX-016 Context-aware Web Evidence Budget／Raw Content Contract
P8-CODEX-017 User Manual Recheck Sheet Reproducibility
P8-CODEX-018 Acceptance Disposition Count／Claim Correction
```

## 5. P8-MR7-0 — Entry／Recovery Freeze

- Differential Readingを行う。
- Current Working TreeをCanonical Baselineとする。
- P8-CODEX-013〜018をOpen Findingとして固定する。
- Entry Recovery Indexを作る。
- 進捗報告や実装難度だけで停止しない。

## 6. P8-MR7-1 — Resolver Injection／Hermetic Regression

### Required

- URL Security ValidationのResolver／Validator DependencyをTestから注入可能にする。Production Defaultは現行のFail-closed Validatorのままとする。
- `WebKnowledgeService` Boundaryと`HttpxWebFetchProvider`のHopごとのValidation Boundaryの両方を扱う。いずれか一方だけをFakeにして、もう一方が実DNSを呼ぶ状態を残さない。
- Redirect Hopごとの再検証、Loopback／Private／Dangerous Port Request 0、OFF時Network 0を保つ。
- Injected Resolver／Validator／Mock TransportでPublic IPv4／IPv6、Transient Failure→Success、Permanent RejectionをDeterministicに証明する。
- Controllerで実失敗した次の4 TestをNetwork 0でPASSさせる。TestをSkip／xfailへ変更しない。

```text
test_manual_web_evidence_is_injected_as_an_untrusted_tool_message
test_manual_web_evidence_html_noise_is_stripped_and_budgeted_before_injection
test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn
test_guardrail_context_source_hook_also_governs_manual_web_evidence
```

## 7. P8-MR7-2 — ERROR-terminal Web Evidence Persistence

- `ConversationGenerationSession`が`web_evidence_fetch_failed`のERRORで終了する場合も、`session.web_search_result`からAggregate／Specific Failure Evidenceを永続化する。
- Failed TurnにAssistant Messageを偽造しない。Turn State／Failure ReasonとWeb Citation Evidenceを同じTerminal Commit Boundaryで収束させる。
- COMPLETED専用経路だけにWeb Evidenceを結びつけない。`fail_generation()`または同等のTerminal Commit APIを最小差分で拡張する。
- Fake GeneratorがFailure Result付きCOMPLETEDを返すTestだけで代用しない。実際のERROR Event経路を通し、Store再Open／Reload／Restart相当でAggregate／Specific Reasonが復元されるTestを追加する。

## 8. P8-MR7-3 — Schema 1／2 Reader Compatibility

- Frozen Historical Recordを書き換えず、Reader側でSchema 1／2を現行In-memory Contractへ昇格する。
- Schema 2で欠ける`transformation`は、保存済み`content_type`から現行のPure Classificationで導出する。
- Schema 1で`requested_url`が無い場合は、当時唯一のURLである`canonical_url`をCompatibility Projectionに使う。これを「当時Redirect前URLを保存していた」と虚偽主張しない。
- Unknown Future Schema／Digest不一致／構造破損は従来どおりFail-closedにする。
- Schema 1／2の実Encoded SQLite Recordを読み、Citation Metadataが復元されるRegression Testを追加する。

## 9. P8-MR7-4 — Context-aware Evidence Budget／Content Contract

### Raw Fetch Contract

- `max_response_bytes`内のUTF-8 Contentが`WebEvidence`構築時の未分類ValidationErrorにならないよう、Byte CapとCharacter Contractを整合させる。
- Security BoundaryのResponse Size上限は弱めない。現行Configが許容する最大Byte数より小さいPydantic Character Capで偶発的にCrashさせない。
- 200,000 characters超え、かつConfigured Byte Cap内のContentでTyped Resultが成立するTestを追加する。

### Model Injection Budget

- 12,000 Character固定Capだけを「8192 Context保証」としない。
- 既存の`chat_prompt_token_counter`、`effective_context_size`、`max_new_tokens`、Conversation／System／RAG等の残量を使い、Web Evidenceの現行Turnに実際に入るBudgetを決定する。
- 実装方式は、Full PromptのToken Countに基づく有界Truncation／Binary Search等の最小差分でよい。別の大規模Chunking基盤を作らない。
- Web Evidenceが1 Tokenも安全に入らない場合は、Main Model Call 0のTyped `content_budget_exceeded`へ収束させる。Base Conversation自体が上限超過の場合と、Web Evidence追加だけが原因の場合を混同しない。
- CJK Long Content／8192 Effective Context／長いHistory／RAG併用／Max New Tokens予約を含むTestで、Opaque `context_limit_exceeded`にならないことを実証する。

## 10. P8-MR7-5 — Recheck Sheet／Acceptance Correction

### User Manual Recheck Sheet

- `uv run margpa-web`だけの起動手順を撤回する。
- 前回正本のFull Flag Commandを使い、次の2種類を明示する。
  1. Schema Migrationが必要な初回の`--conversation-persistence-migrate`付き起動。
  2. Migration完了後の、同Flag無しの通常起動。
- Conversation／Local Corpus／Data ControlsのRuntime RootとScope IDはUserのCurrent構成`$PWD/runtime_data`／`mac-local-primary`で統一する。
- Dev Agent任意確認Pathは実Scopeへ合わせる。または`<configured-scope-id>`から導出すると明記する。
- `example.org`等のPublic URL FetchはLoopback内で完結せず、User Macから実NetworkへOutboundすることを正直に明記する。

### Acceptance Correction

- Frozen`phase_8_acceptance_matrix_ja.md`は編集しない。
- Current Acceptance Disposition AddendumをAppend-only Correction AddendumでSupersedeする。
- 集計の混同を避けるため、P8-ACC-001〜040の全40件を個別に再導出し、PASS／PARTIAL／FAIL／USER MANUAL GATE／NOT RUNの合計が必ず40になるよう機械検証する。
- P8-ACC-038のGD相関PARTIALとP8-ACC-040のUSER MANUAL GATEを根拠なくPASSへ上げない。
- P8-ACC-039はFocused／Canonical Verificationが実際にCleanになった後だけPASSとする。
- Controllerで`ruff format --check`が指摘した次のPhase 8関連5 Fileは、その5 Fileだけに限定してCanonical Formatterを適用する。無関係のFileへFormat Scopeを広げない。

```text
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py
tests/integration/web/test_constitution_web_app.py
tests/unit/constitution/test_constitution_contracts.py
tests/unit/dev_agent/test_dev_agent_contracts.py
tests/unit/dev_agent/test_run_service.py
```

## 11. P8-MR7-6 — Verification／Internal Review／Return

1. P8-CODEX-013〜018を1件ずつ再導出する。
2. Controllerの4 Failureを含むFocused Backend Testを実行する。
3. Web Knowledge／Persistence／SQLite Compatibility／Conversation Generation／Dev Agent Regressionを実行する。
4. 上記5 Fileの限定Mechanical Format後、Backend Full、Mypy、Ruff Check／Format Checkを実行する。
5. Frontend Source変更が0でも、今回はPhase 8 User Recheck直前の最終CandidateであるためFrontend Typecheck／Test／Lint／Buildを1回実行する。
6. Networkが必要なTestはInjected Resolver／Validator／Mock Transportで行い、実Network Action 0にする。
7. User `runtime_data/`に触れず、Temp Root／Temp SQLiteでPersistenceとFixtureを検証する。
8. Requirement／Negative Path／Persistence／Backward Compatibility／Context Budget／Acceptance Claimの6観点でInternal Reviewを1 Cycleだけ行う。
9. Critical／Major／MVP Blockerだけを同Package内でReworkする。Minor／Hardening／Phase 11+項目でReviewを無限化しない。
10. Recovery Index、Acceptance Correction Addendum、Corrected User Manual Recheck Sheet、Exact Return Handoffを作る。

## 12. Authority／Prohibitions

### 許可

- Project Root内の必要なSource／Test／Frontend／Static／Phase 8 Docs Mutation。
- Project Root内のTest／Typecheck／Lint／Build。
- Testが使うProject Root内／System Temp内の限定Temporary Data。
- Recovery／Acceptance Correction／User Manual Recheck Sheet／Exact Return作成。

### 禁止

- Git Read／Write／Commit／Push。
- Network／Install／Download。
- Real Browser／Real Model／Real MCP。
- Userが使用している`runtime_data/`へのRead／Write。
- Project Root外への任意Read／Write／Redirect。
- General Search Provider／Automatic Search／SearXNG／Browser Rendering。
- Archive完全削除／一括Delete／Export／Dedicated Modalの実装。
- Production-grade DNS Rebinding Pinning／任意Charset／Readability基盤へのScope拡張。
- Project Sourceを操作するReal Dev Agent Tool、Real Network Tool、Real MCP。
- Production Constitution Activation／GD Semantic／Phase 6未完Debtの再実装。
- Roadmap／Phase 8 Closure／Backup／Phase 9開始。

実装難度、Core File変更、Diff量、Pending Controller Review、既存UIが成立済みであること、Minor Findingだけで停止しない。指定True Stop Conditionがない限りP8-MR7-6まで連結実行する。

## 13. Return Condition

次を満たした場合だけCodex Controller再Review待ちで停止する。

```text
P8-CODEX-013〜018 Individual Disposition
Preserved Baseline／Regression Statement
Changed Paths
Focused／Canonical Verification
Controller 4 Failure = PASS
Schema 1／2 Compatibility Evidence
ERROR-terminal Reload／Restart Evidence
CJK／8192／RAG／History Context Budget Evidence
Acceptance 40-ID Machine-verified Tally
Network／User runtime_data／Real Browser／Real Model Action Count
Internal Review Result
Exact Return Handoff
```

最大Claimは`COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK`。Phase 8 Closure／P8-ACC-040 PASS／Phase 9 READYは主張しない。
