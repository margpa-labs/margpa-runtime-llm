# Phase 8 Post-User-Manual Rework — Codex Controller Independent Review

```yaml
document_type: controller_independent_review
document_state: final
phase: phase_8
review_target: P8-MR0_through_P8-MR6
review_result: ADJUST
reviewed_at: 2026-08-31 13:48:26 JST
reviewer_role: project_controller_and_design_governor
product_quality_target: poc_mvp
review_cycle: single_bounded_cycle
```

## 1. 結論

Claudeは今回、指定されたP8-MR0〜P8-MR6を不要停止なしで連結実行した。実装の大半は実際に前進しており、少なくとも次は有効な改善である。

- Manual URL Fetch失敗時のMain Model Call 0へのFail-closed化。
- Typed Failure、有界Retry、HTML Noise除去、Citation Metadata追加。
- ArchiveとSidebarの同期、Archive PanelのClose。
- Constitution Previewの列崩れ解消。
- Dev Agentの追跡可能なLocal Fixture WorkspaceとApproval前Input表示。
- Dev Agent Action ButtonのContrast改善。

ただし、現状のReturnをUser実画面再確認へそのまま渡すことはできない。以下6件はEnterprise Hardeningや趣味的完全性ではなく、今回のExact Contract、Persistence、旧履歴互換、実画面再確認に直接影響するClosure Blockerである。そのため判定は`ADJUST`とする。

## 2. Review範囲と停止線

今回は「製品化品質」や「未解決0件」を目指していない。PoC・MVPとして、次をReview対象とした。

```text
Phase 8の主機能が実行可能
Failure時に虚偽の根拠表示をしない
LiveとReload／Restart後でEvidenceが食い違わない
Existing Recordを破壊しない
8192 Contextの既知実害を再発させない
Userが実際に起動／再確認できる
Acceptance Claimが数学的／事実的に正しい
```

Charset全般、Readability品質、DNS Rebinding完全耐性、実Search Provider、任意サイトへの完全対応は今回のBlockerに含めない。

## 3. Review Evidence

### 3.1 Focused Backend Test

実行Command：

```bash
./.venv/bin/pytest -q --tb=short \
  tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_is_injected_as_an_untrusted_tool_message \
  tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_html_noise_is_stripped_and_budgeted_before_injection \
  tests/unit/conversation/test_conversation_generation.py::test_manual_web_evidence_and_documentation_rag_are_both_injected_in_the_same_turn \
  tests/unit/conversation/test_conversation_generation.py::test_guardrail_context_source_hook_also_governs_manual_web_evidence
```

実測：

```text
4 failed in 0.25s

expected COMPLETED -> actual web_evidence_fetch_failed: 3
expected guardrail_context_source_rejected -> actual web_evidence_fetch_failed: 1
```

### 3.2 Focused Frontend Test

以下6 File／90 TestはPASSした。

```text
WebCitationsSection.test.tsx
DataControlsPanel.test.tsx
SettingsModal.test.tsx
ConstitutionPanel.test.tsx
DevAgentPanel.test.tsx
App.test.tsx

6 files / 90 tests passed
```

したがって、P8-MANUAL-003〜006の対応を破棄しない。次ReworkはWeb Evidence・Persistence・Compatibility・Verification Docsの差分に限定する。

## 4. Open Findings

### P8-CODEX-013 — Resolver Injection／Test Hermeticity未成立

```yaml
severity: major_mvp_blocker
impact: canonical_verification, network_zero_contract, guardrail_web_evidence_path
disposition: rework_required
```

Input Exact Handoffは、Resolver／TransportをTestから注入し、実Network 0で検証することを明示していた。しかし現行実装は、`WebKnowledgeService.fetch_direct_url()`と`HttpxWebFetchProvider._attempt_one_hop()`がどちらもProduction Validatorを直接呼び、`validate_url_before_connect()`が`socket.getaddrinfo()`を実行する。

Reference：

```text
src/.../web_knowledge/application/web_knowledge_service.py:275
src/.../adapters/web_knowledge/httpx_fetch_provider.py:142
src/.../web_knowledge/domain/url_security.py:110-121
tests/unit/conversation/test_conversation_generation.py:1791-1797
```

Conversation TestのStub Fetch ProviderはSocketを開かないが、Stubに到達する前のService Validatorが実DNSを要求する。その結果、Controller環境でFocused Test 4件が実失敗した。Returnの「既知3 Test」も現行実測と一致しない。

### P8-CODEX-014 — Fail-closed ERROR経路でFailure Web Evidenceが永続化されない

```yaml
severity: major_mvp_blocker
impact: reload_restart_truthfulness, P8-ACC-011, P8-MANUAL-002
disposition: rework_required
```

`ConversationGenerationSession`はManual URL Fetchで有効Citation 0の場合、`web_evidence_fetch_failed`のERROR Eventを返す。しかしPersistent Serviceは、COMPLETED経路でのみ`session.web_search_result`を`complete_generation()`へ渡し、ERROR経路の`fail_generation()`には渡していない。

Reference：

```text
src/.../conversation_generation.py:859-870
src/.../persistent_conversation_service.py:982-1005
src/.../persistent_conversation_service.py:1018-1032
src/.../persistent_conversation_service.py:514-530
```

このため、Live SSE上のAggregate／Specific Failureは表示できても、Reload／Restart後のCurrent TurnにWeb Failure Evidenceが残らない。現行のPersistence TestはFake GeneratorがFailure Result付きCOMPLETEDを返す経路であり、今回追加した実ERROR Terminalを証明していない。

### P8-CODEX-015 — Web Citation Schema 1／2のBackward Compatibilityが破れている

```yaml
severity: major_data_compatibility_blocker
impact: historical_citation_recovery, P8-ACC-011
disposition: rework_required
```

`WebCitation.transformation`は現在Requiredである。ReaderはSchema Version 1〜3を受理範囲とする一方、旧Payloadを現行Modelへそのまま`model_validate()`する。Schema 2には`transformation`が無いためValidationErrorとなり、`corrupt_record`へ落ちる。

Reference：

```text
src/.../web_knowledge/contracts.py:257-275
src/.../web_knowledge/contracts.py:319-335
src/.../sqlite_conversation_store.py:963-998
```

`corrupt_record`への安全なDegradeはCrash回避であり、旧履歴のBackward Compatibilityではない。Input HandoffはExisting RecordのBackward Compatibility維持を明示していたため、Closure前にReader Compatibilityを成立させる必要がある。

### P8-CODEX-016 — Large HTMLのContext Budget保証とRaw Content Contractが未成立

```yaml
severity: major_mvp_blocker
impact: user_reproduced_context_failure, typed_failure_contract
disposition: rework_required
```

現行Normalizerは12,000「文字」の固定Capであり、実際のEffective Context、Conversation History、RAG、System Prompt、Max New Tokensの残量を参照しない。CJKは英文よりToken／Character比が高くなり得るため、「8192 ContextのOpaque Failureを起こさない」というClaimは固定Character Capだけでは成立しない。

さらに、Fetch Configは既定1,500,000 bytes／最大10,000,000 bytesを許容する一方、`WebEvidence.fetched_content`は200,000 characters上限である。Fetch Boundary内で正常に取得できたContentが、`WebEvidence`構築時の未分類Pydantic ValidationErrorになり得る。

Reference：

```text
src/.../html_normalizer.py:38-43
src/.../conversation_generation.py:2508-2577
src/.../conversation_generation.py:2705-2741
src/.../web_knowledge/contracts.py:182
src/.../web_knowledge/contracts.py:410-418
```

### P8-CODEX-017 — User Manual Recheck Sheetの起動／Pathが実構成と一致しない

```yaml
severity: major_closure_process_blocker
impact: user_manual_recheck_reproducibility
disposition: docs_rework_required
```

現行Sheetは`uv run margpa-web`だけを起動Commandとしている。これではConversation Persistence、Phase 7 Web Search、Data Controls等の必要Flagが成立しない。また、Dev Agent Fixtureの任意Terminal確認Pathが`runtime_data/persistent/default/...`であるが、Userの実構成Scopeは`mac-local-primary`である。

さらにSheetは「Loopback外へ一切出ない」と記載しながら、Public URLへのManual Fetchを手順に含めている。実Network使用を正直に明示し、Migration必要時の初回起動と、以後のMigration無し起動を分離する必要がある。

Reference：

```text
.../phase_8_claude_post_user_manual_acceptance_recheck_sheet...md:13-25
.../phase_8_claude_post_user_manual_acceptance_recheck_sheet...md:95-99
.../phase_8_user_mac_manual_acceptance_test_sheet...md:32-69
```

### P8-CODEX-018 — Acceptance Dispositionの数学的集計が誤っている

```yaml
severity: major_closure_claim_blocker
impact: acceptance_truthfulness, phase_8_closure
disposition: docs_rework_required
```

Handoffで指定した主な再導出対象は次の31件である。

```text
P8-ACC-002〜012 = 11
P8-ACC-015〜018 = 4
P8-ACC-021〜023 = 3
P8-ACC-026〜030 = 5
P8-ACC-033〜040 = 8
TOTAL = 31
```

Current AddendumのTableは参考としてP8-ACC-013／014も含むため、Table行は33件である。しかし集計は`PASS 34 + PARTIAL 1 + USER MANUAL GATE 1 = TOTAL 36`としており、実Tableと一致しない。また「未再導出 4」の後に8 IDを列挙している。

P8-ACC-039も、Controller Focused Test 4件が実失敗している現状で「条件付きPASS」に計上できない。Frozen Matrixは編集せず、Current Addendumを正確に再導出する必要がある。

またControllerで`./.venv/bin/ruff format --check`を実行した結果、次のPhase 8関連5 Fileが実際にFormat Check失敗であった。

```text
src/margpa_runtime_llm/modules/dev_agent/application/run_service.py
tests/integration/web/test_constitution_web_app.py
tests/unit/constitution/test_constitution_contracts.py
tests/unit/dev_agent/test_dev_agent_contracts.py
tests/unit/dev_agent/test_run_service.py

5 files would be reformatted, 557 files already formatted
```

したがって「Ruff Format全件Clean」というReturn Claimも現行Working Treeの実測と一致しない。この5 Fileは今回確認したPhase 8 Source／Testであり、次Reworkで限定的にMechanical FormatしてCanonical CheckをCleanにする。

## 5. Preserved／Deferred

### Preserved

```text
P8-MANUAL-003 Archive Sidebar／Panel同期実装
P8-MANUAL-004 Constitution Layout実装
P8-MANUAL-005 Traceable Fixture Workspace／Approval Input／Output実装
P8-MANUAL-006 Button Contrast実装
P8-CR系のConcurrency／Envelope／Approval Evidence／Budget／Completion Gate
P8-RW6／RW7のRedirect Authority／Constitution Preview Semantics
```

### 今回のClosure Blockerにしないもの

```text
General Keyword SearchのReal Provider
SearXNG／Automatic Search
Charset全般／JavaScript Rendering／Login／Cookie／Form
Production-grade DNS Rebinding Pinning
Readability品質の完成
Real MCP／正式Development Agent Level 1
Phase 6 Semantic／Selene／Qwen3Guard残件
Dev Agent Fixture WorkspaceのEnterprise-grade TOCTOU Hardening
```

`network_calls_made`がRetryの実Attempt数ではなくProvider呼出数に近い現行語義は、既存Observability Debtとして保留する。今回のReworkで必要なContractを無限拡張しない。

## 6. Controller Disposition

```yaml
current_claim: ADJUST_REQUIRED
ready_for_user_manual_recheck: false
phase_8_closure_ready: false
next_exact_work_unit: P8-MR7-0
maximum_next_return_claim: COMPLETE_CANDIDATE_FOR_USER_MANUAL_RECHECK
required_review_cycles_in_next_task: 1
```

次ReworkはP8-CODEX-013〜018に限定し、成立済みのUI／Archive／Dev Agent Foundationを再実装しない。
