# Claude Phase 2-E Acceptance Matrix

```yaml
document_id: claude_phase_2_e_acceptance_matrix_20260815004739
status: frozen
phase: phase_2
subphase: phase_2_e
from_role: Claude Phase 2-E設計担当者役
to_role: Claude Phase 2-E実装者役 ／ Claude設計統括者役
role: phase_designer
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 00:47:39 JST
language: ja
```

## 1. Requirements Traceability

| ID | 要件要約 | 検証Test（新規／既存拡張） |
|---|---|---|
| FR-1.1 | ComponentDescriptor解決（3 Component） | `tests/unit/runtime_composition/test_application.py` |
| FR-1.2 | 矛盾Component登録のFail-closed拒否 | `tests/unit/runtime_composition/test_application.py::test_conflicting_registration_rejected` |
| FR-1.3 | Registryは実行許可を生成しない | `tests/unit/runtime_composition/test_application.py::test_registry_grants_no_execution_authority`（Registry操作だけでは既存Gate判定に影響しないことを確認） |
| FR-1.4 | 実State写像（既存Gate変更なし） | `tests/integration/web/test_runtime_composition_web_app.py` |
| FR-1.5 | governance_seam_mode="off"固定 | `tests/unit/runtime_composition/test_contracts.py::test_seam_mode_rejects_non_off` |
| FR-1.6 | Local限定Endpoint／Public Zero-binding | `tests/integration/web/test_runtime_composition_web_app.py::test_public_preview_returns_404` |
| FR-2.1〜2.5 | 既存RAG State契約の維持 | `tests/unit/documentation_rag/test_context_citation_and_orchestrator.py`（既存Test、Regressionとして確認） |
| FR-2.6 | Multi-turn／Branch下のCitation非混線 | `tests/unit/conversation/test_conversation_generation.py::test_branch_citations_do_not_cross`, `tests/integration/conversation/test_local_conversation_persistence.py` |
| FR-2.7 | Phase 7 Port境界維持 | 既存Port Protocol Signature不変（Static Check＋既存Contract Test） |
| FR-3.1 | 本文非埋め込み | `tests/unit/documentation_rag/test_citation_persistence_contracts.py::test_no_free_text_content_field` |
| FR-3.2 | Typed関連付け | `tests/unit/documentation_rag/test_citation_persistence_contracts.py` |
| FR-3.3 | 禁止Field構築不能 | `tests/unit/documentation_rag/test_citation_persistence_contracts.py::test_model_has_no_forbidden_fields`（Pydantic Model Fields Introspectionで禁止Field名不在を機械的に確認） |
| FR-3.4 | 6経路でのCitation復元 | §2 Matrix参照 |
| FR-3.5 | Atomicity | `tests/unit/conversation/test_sqlite_conversation_store.py::test_turn_commit_and_citation_are_atomic` |
| FR-3.6 | Crash Recovery統合 | `tests/integration/conversation/test_persistent_citation_evidence.py::test_crash_recovery_includes_citation` |
| FR-3.7 | 未知Schema VersionのFail-closed | `tests/unit/conversation/test_citation_evidence_sqlite_store.py::test_unsupported_schema_version_returns_unavailable` |
| FR-3.8 | Corrupt RecordのFail-closed | `tests/unit/conversation/test_citation_evidence_sqlite_store.py::test_corrupt_record_returns_unavailable_not_raise` |
| FR-3.9 | RAG OFF時Citation Write 0 | `tests/unit/conversation/test_persistent_conversation_service.py::test_rag_off_writes_zero_citation_rows` |
| FR-3.10 | Public／Basic非Binding | `tests/integration/web/test_persistent_web_app.py`（既存Regression、Citation Store非構築を確認） |
| FR-3.11 | Derived Turn非上書き | `tests/integration/conversation/test_persistent_citation_evidence.py::test_retry_regenerate_preserve_source_citations` |
| FR-3.12 | Branch SelectはCitation非変更 | `tests/integration/conversation/test_persistent_citation_evidence.py::test_branch_select_does_not_mutate_citations` |
| NFR-1〜10 | 既存Contract非破壊 | §3 Regression Matrix参照 |

## 2. Citation復元 6経路 Matrix（Handoff §9必須）

| # | 経路 | Test |
|---|---|---|
| 1 | Browser Reload | `tests/integration/web/test_persistent_web_app.py::test_citations_survive_reload_fetch` |
| 2 | Server Restart | `tests/integration/conversation/test_persistent_citation_evidence.py::test_citations_survive_server_restart` |
| 3 | Chat Listから再Open | `tests/integration/conversation/test_persistent_citation_evidence.py::test_citations_survive_reopen_from_list` |
| 4 | Resume | `tests/integration/conversation/test_persistent_citation_evidence.py::test_citations_survive_resume` |
| 5 | Retry／Regenerate | `tests/integration/conversation/test_persistent_citation_evidence.py::test_retry_regenerate_preserve_source_citations` |
| 6 | Branch Select | `tests/integration/conversation/test_persistent_citation_evidence.py::test_branch_select_does_not_mutate_citations` |

## 3. Compatibility Regression Matrix

| Invariant | Regression Test |
|---|---|
| `/api/v1/chat/**` 無変更 | 既存 `tests/integration/web/test_web_app.py` Full Pass |
| `/api/v2/conversations/**` 既存Contract無変更 | 既存 `tests/integration/web/test_persistent_web_app.py` Full Pass |
| `/api/v2/configuration/**` 既存Contract無変更 | 既存 `tests/integration/web/test_configuration_control_web_app.py` Full Pass |
| Public／Basic Zero-binding（Conversation／Config／Citation／Component全て） | 既存 Public／Basic関連Test Full Pass ＋ 新規Citation／Component分のZero-binding Test |
| Phase 2-A〜2-D Domain Invariant無変更 | `tests/unit/conversation/test_conversation_domain.py` Full Pass（無変更） |
| SQLite Adapter内部実装がDomain／Portへ非漏洩 | Static Import Check（`modules/conversation/domain/**`が`sqlite_conversation_store`をImportしないことをGrep／Lintで確認） |
| Model生成中DB Lock非保持 | 既存Test（Streaming中Citation書込を行わないことをコード経路で確認、§5.9設計） |
| Browser Static／Security Contract（Markdown Safety、LocalStorage非会話化、Client History非送信等） | 既存 `tests/unit/web/test_persistent_static_contract.py`・`tests/unit/web/test_safe_markdown.py` Full Pass（既存Substring Assertion群を維持したまま`loadPersistentDetail()`へ追記するため、既存Testは無改変で通る設計。§Design Reviewで実Fileを確認済み） |

## 4. Static／Full Suite

```text
- Ruff Format Check
- Ruff Check
- Mypy
- Full Test Suite（現Baseline 615 passed／3 deselected からの差分を記録し、新規Test分の純増を確認）
- runtime_data/ 非Mutation確認（Test Fixtureは既存Test Contractに従いTemporary Directory使用、実runtime_data/へ触れない）
- Stable Docs非Mutation確認（git diff で docs/project/current/**, docs/project/shared/**, docs/public/**,
  phase_index_ja.md, phase_2/{requirements,architecture,adr,governance,handoffs,operations}/** に変更が
  ないことを確認）
- Project Root外Mutation 0確認（git status --porcelain の対象が margpa-runtime-llm/ 内のみであることを確認）
```

## 5. Status

```text
Current Point            : Acceptance Matrix Draft
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（設計段階）
Open Current Blocker      : NONE
Controller-owned Next Work: Implementer Handoff作成、Independent Design Review
Deferred Evidence         : NONE
Exact Next Route          : Implementer Handoff作成へ進む
```
