# Claude Phase 2-E Exact Source／Test Mutation Manifest

```yaml
document_id: claude_phase_2_e_mutation_manifest_20260815004739
status: frozen
phase: phase_2
subphase: phase_2_e
from_role: Claude Phase 2-E設計担当者役
to_role: Claude Phase 2-E実装者役
role: phase_designer
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 00:47:39 JST
language: ja
source_architecture: claude_phase_2_e_architecture_20260815004739
source_adr: claude_phase_2_e_adr_20260815004739
```

本Manifestは、Handoff §5「Source／Test／Config Mutation Authority」の範囲内で実装者役が変更してよい対象の完全列挙である。ここに列挙されない`src/**`／`tests/**`／`config/**`Fileへの変更は許可されない。列挙外の変更が不可避と判明した場合は、実装者役は独断で拡張せず設計担当者役（本Controller Task内での同一Role Chain）へ差し戻す。

## 1. 新規Source File

```text
src/margpa_runtime_llm/modules/runtime_composition/__init__.py
src/margpa_runtime_llm/modules/runtime_composition/contracts.py
src/margpa_runtime_llm/modules/runtime_composition/ports.py
src/margpa_runtime_llm/modules/runtime_composition/application.py
src/margpa_runtime_llm/modules/runtime_composition/public.py
src/margpa_runtime_llm/web/runtime_composition_routes.py
```

## 2. 既存Source Fileの変更

```text
src/margpa_runtime_llm/modules/documentation_rag/contracts.py
  # PersistedTurnCitationEvidence, CitationUnavailable を追加（既存 DocumentationCitation を再利用、既存Class変更なし）

src/margpa_runtime_llm/modules/documentation_rag/ports.py
  # CitationEvidenceStorePort（get_turn_citations／get_conversation_citations）を追加

src/margpa_runtime_llm/modules/documentation_rag/public.py
  # 上記新規Contract／Portの再Export（既存Exportパターンに従う）

src/margpa_runtime_llm/modules/conversation/ports/conversation_store.py
  # CommitConversation へ Optional Field `citation_evidence: PersistedTurnCitationEvidence | None = None` を追加
  # ConversationRepositoryPort へ get_turn_citations／get_conversation_citations の委譲、または
  #   CitationEvidenceStorePort を同一Adapterに実装させる方式のどちらかを実装時に選択し、
  #   Implementer Statusへ選択理由を記録する（設計はAdapter内実装の自由度をここだけ残す）

src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
  # turn_citations テーブル作成（_initialise_schema 相当箇所）
  # commit() の既存 BEGIN IMMEDIATE Transaction内で turn_citations への INSERT を追加
  # get_turn_citations／get_conversation_citations の実装（SELECT、Fail-closed Parse）
  # STORAGE_SCHEMA_VERSION を "sqlite-1" → "sqlite-2" への migration対象に追加

src/margpa_runtime_llm/modules/conversation/adapters/sqlite_migration.py
  # source_version="sqlite-1", target_version="sqlite-2" の SQLiteMigrationStep を追加
  #   （turn_citations の CREATE TABLE IF NOT EXISTS のみ、既存データ変換なし）

src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
  # augment_with_context() の DocumentationAugmentation を、SSE用途に加えて
  #   Persistence用途（PersistedTurnCitationEvidence構築）へも渡す経路を追加
  #   既存のSSE `retrieval`／`completed`イベント生成ロジックは変更しない

src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
  # Turn完了（complete_generation相当）経路で、上記Persistence用途の
  #   PersistedTurnCitationEvidence を CommitConversation.citation_evidence に設定して commit() を呼ぶ
  # RAG state が ENABLED かつ citations 非空の場合のみ設定、それ以外は None（Citation Write 0）

src/margpa_runtime_llm/web/persistent_routes.py
  # GET /api/v2/conversations/{conversation_id} の turns[] Responseへ
  #   citations Field を追加（既存Fieldの変更・削除なし）
  # get_conversation_citations() の呼び出しを追加

src/margpa_runtime_llm/bootstrap/web_application.py
  # 既存3 Component（Documentation RAG／Conversation Persistence／Configuration Control）の
  #   構築・State解決の直後に ComponentRegistryService への register() 呼び出しを追加
  #   （既存if/elif分岐・既存Gate判定ロジック自体は変更しない）
  # LocalConversationPersistenceSettings 経路に Citation Store（SQLite Adapter拡張）の配線を追加

src/margpa_runtime_llm/entrypoints/web/main.py
  # --runtime-composition-inspection CLIフラグを追加
  # runtime_composition_routes のマウントを、既存 configuration_control と同型のGateで追加

src/margpa_runtime_llm/web/static/app.js
  # loadPersistentDetail()（app.js:1301付近）内、
  #   state.persistentDetail = await response.json(); の直後に、
  #   response.turns[].citations を state.persistentCitationEvidence へ書き込む処理を追加
  # renderCitations()／renderPersistentDetail()／handlePersistentEvent() は変更しない
```

## 3. 新規Test File

```text
tests/unit/runtime_composition/test_contracts.py
tests/unit/runtime_composition/test_application.py
tests/unit/web/test_runtime_composition_contracts.py
tests/integration/web/test_runtime_composition_web_app.py
tests/unit/documentation_rag/test_citation_persistence_contracts.py
tests/unit/conversation/test_citation_evidence_sqlite_store.py
tests/integration/conversation/test_persistent_citation_evidence.py
```

## 4. 既存Test Fileの変更（新規Testケース追加、既存Testの変更・削除は行わない）

```text
tests/unit/conversation/test_sqlite_conversation_store.py
  # turn_citations テーブルのCRUD、Atomicity、Idempotency、Fail-closed読み取りのTestを追加

tests/unit/conversation/test_sqlite_migration.py
  # sqlite-1 -> sqlite-2 MigrationのTestを追加

tests/unit/conversation/test_persistent_conversation_service.py
  # Turn完了時のCitation Commit配線のTestを追加

tests/unit/conversation/test_conversation_generation.py
  # Multi-turn／Branch下でCitationが混線しないことを検証するTestを追加

tests/unit/documentation_rag/test_context_citation_and_orchestrator.py
  # 既存Citation生成ロジックとPersistence用途への受け渡しの整合Testを追加

tests/integration/conversation/test_local_conversation_persistence.py
  # Reload／Restart／Resume／Retry／Regenerate／Branch SelectでのCitation復元Integration Testを追加

tests/integration/web/test_persistent_web_app.py
  # GET /api/v2/conversations/{id} のcitations Field往復Testを追加

tests/unit/web/test_persistent_web_contracts.py
  # citations Field のSchema Contract Testを追加

tests/unit/web/test_configuration_control_contracts.py
  # ComponentDescriptor と既存 FeatureHookDescriptor の非干渉（既存Contract不変）確認Testを追加（変更なし確認用）
```

## 5. Config変更

```text
なし（技術的に不可避なConfig変更は現時点で見込まれない。Implementer役が実装中に必要性を発見した場合、
      理由をStatusへ記録し、設計担当者役へ差し戻す）
```

## 6. 明示的に変更しないFile／Package

```text
src/margpa_runtime_llm/modules/conversation/domain/**       # Frozen（2-A以降）、本Phaseでは変更しない
src/margpa_runtime_llm/modules/conversation/domain/models.py # PersistedConversationMessage等へCitation Fieldを追加しない
src/margpa_runtime_llm/web/access_profiles.py                # 既存resolve_documentation_rag_state()等は変更しない
src/margpa_runtime_llm/modules/configuration_control/**      # 既存Contract／Applicationは変更しない
                                                               # （ComponentDescriptorはApplyDisposition／ConfigurationSourceを
                                                               #   Importして再利用するのみ）
既存 /api/v1/** Route定義                                     # 変更しない
```

## 7. Status

```text
Current Point            : Mutation Manifest Draft
Files Created／Modified   : 本Fileのみ（新規作成）
Validation                : N/A（設計段階）
Open Current Blocker      : NONE
Controller-owned Next Work: Acceptance Matrix／Implementer Handoff作成
Deferred Evidence         : §2 conversation_store.py の Port設計選択（委譲 vs 同一Adapter実装）は実装時確定
Exact Next Route          : Acceptance Matrix作成へ進む
```
