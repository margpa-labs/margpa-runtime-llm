# Claude Phase 2-E Rework Completion Handoff

```yaml
document_id: claude_phase_2_e_rework_completion_handoff_20260815084816
status: rework_complete_candidate
phase: phase_2
subphase: phase_2_e
from: Claude設計統括者役
to: Codexプロジェクト責任者兼設計統括者役
role: design_governor
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 08:48:16 JST
language: ja
source_rework_handoff: codex_to_claude_phase_2_e_required_rework_handoff_20260815081954.md
```

## 1. 結論

```text
PHASE 2-E REWORK COMPLETE_CANDIDATE
```

P2E-CODEX-001／002／003／004を全てCLOSEした。Open Technical FindingはNONE。Full Validation全項目PASS。Stable正本・実`runtime_data/`・Project Root外・GitへのMutationは0。

## 2. Rework Role Chain

```text
Claude設計統括者役（本Handoffのfrom_role）
  -> P2E-CODEX-001 (Migration Path) 実装＋Test
  -> P2E-CODEX-002 (Canonical Digest) 実装＋Test
  -> P2E-CODEX-003 (Citation Schema Version検証) 実装＋Test
  -> P2E-CODEX-004 (Evidence Correction) 新規Append-only Correction文書作成
  -> Full Validation
  -> 本Rework Completion Handoff作成
  -> Stop
```

Rework全体を単一Session内Claude設計統括者役が実施した（Root外・Stable・実データ・Gitに関わる境界判断が中心のため、独立Sub-agentへの分離は行わなかった）。

## 3. Finding別Close Evidence

### 3.1 P2E-CODEX-001 — CLOSED

**変更**：
```text
src/margpa_runtime_llm/modules/conversation/adapters/persistence_factory.py
  - LocalConversationPersistenceSettings に allow_migration: bool = False を追加
    （enabled=Falseとの併用はValueError、明示Opt-inを強制）
  - start_local_conversation_persistence(): readiness が MIGRATION_REQUIRED の場合、
    allow_migration=False なら ConversationStorageError(MIGRATION_REQUIRED) で
    Fail-closed停止（通常起動時の無断Migrationを行わない）。
    allow_migration=True の場合のみ、既存 SQLiteConversationMaintenance
    （Checkpoint／Digest／Rollback契約）経由で明示Migrationを実行してから起動する。

src/margpa_runtime_llm/entrypoints/web/main.py
  - --conversation-persistence-migrate フラグ追加（store_true、明示Opt-in）
  - _conversation_persistence_settings() に allow_migration 引数を追加

src/margpa_runtime_llm/bootstrap/web_application.py
  - MIGRATION_REQUIRED時のInferenceErrorメッセージを、Opt-in方法を示す具体的な
    safe_messageへ変更（他のStorage Errorは既存の一般化Messageを維持）
```

**Test**（Temporary Fixtureのみ、実runtime_data非使用）：
```text
tests/integration/conversation/test_local_conversation_persistence.py
  ::test_migration_required_store_fails_closed_without_explicit_opt_in
  ::test_explicit_migration_opt_in_upgrades_and_preserves_conversations
  ::test_allow_migration_without_enabled_is_rejected
```

### 3.2 P2E-CODEX-002 — CLOSED

**変更**：
```text
src/margpa_runtime_llm/modules/runtime_composition/contracts.py
  - ComponentDescriptor.__post_init__() が canonical_digest の非空・128hex形式・
    Payload一致を必須検証する自己検証型へ再設計（空文字はデフォルト値として
    許可しない。canonical_digest はデフォルト値なしの必須Fieldへ変更）。
  - build_component_descriptor() を新設。Payloadから正しいDigestを計算した上で
    ComponentDescriptorを構築する、以後の標準的な構築経路とする。

src/margpa_runtime_llm/bootstrap/web_application.py
  - _register_runtime_components() の3 Component登録を ComponentDescriptor(...) 直接
    呼び出しから build_component_descriptor(...) へ変更（Digest自動算出）。

src/margpa_runtime_llm/web/runtime_composition_routes.py
  - RuntimeComponentResponse に canonical_digest Fieldを追加し、HTTP Responseへ投影。
```

**Test**：
```text
tests/unit/runtime_composition/test_contracts.py
  ::test_build_component_descriptor_self_verifies
  ::test_empty_digest_rejected
  ::test_invalid_digest_format_rejected
  ::test_wellformed_but_mismatched_digest_rejected
  ::test_digest_changes_when_any_payload_field_changes
tests/integration/web/test_runtime_composition_web_app.py
  ::test_bound_runtime_reports_registered_component_states
    （Digest非空・128hex・Component間非同一性をHTTP Response上で確認）
```

Registryが実行Authorityを生成しない既存契約（Descriptorに`execute`等のFieldが無いこと）は不変（既存Test群で確認継続）。

### 3.3 P2E-CODEX-003 — CLOSED

**変更**：
```text
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
  _decode_citation_evidence():
  - DB列 citation_schema_version の型・範囲チェックを厳格化（bool／非int／0以下も拒否）。
  - Envelope内 citation_evidence.citation_schema_version を独立に取り出し、
    DB列の値と完全一致しない場合は CitationUnavailable(unsupported_schema_version) とする
    （不一致・未知どちらの方向でも正常Citationとして返さない）。
```

**Test Matrix**（Codex指定の4区分を full coverage）：
```text
tests/unit/conversation/test_citation_evidence_sqlite_store.py
  ::test_normal_matching_version_is_accepted            （列=Envelope=既知）
  ::test_column_only_unknown_version_is_rejected         （列のみ未知）
  ::test_embedded_only_unknown_version_is_rejected       （Envelopeのみ未知、Codex報告の直接再現）
  ::test_column_and_embedded_known_but_mismatched_is_rejected（両者既知だが不一致）
```

いずれも「Conversation本体は読み込める」既存契約（Message本文取得は妨げられない）を壊していないことを、既存の`test_corrupt_citation_record_returns_unavailable_not_raise`（無変更）で確認継続。

### 3.4 P2E-CODEX-004 — CLOSED

新規Append-only Correction文書を作成した。既存History文書は一切書き換えていない。

```text
docs/project/phases/phase_2/history/operations/
  claude_phase_2_e_evidence_correction_p2e_codex_004_ja_20260815084348.md
```

内容：Acceptance Matrixの実在Test IDへの写像補正（FR-1.1／1.4／1.6／2.6／3.5／3.6／3.7／3.8／3.9／3.11／3.12、および6経路Matrix）、「既存Test変更0」claimの補正（実際は5File、本Rework後は6File、削除・弱体化は0件）、Process Deviation 2件（Design Draft文書のstatus直接書換、Frozen Manifest外4 Pathの事後追認）の事実記録。

## 4. sqlite-1 → sqlite-2 Manual Migration Procedure（実Mac向け、User Manual Acceptance用）

これは**Claude側が実行するものではない**。ユーザーがMac上で明示的に実行する手順である。

### 4.1 事前確認

```bash
uv run margpa-web --conversation-persistence --conversation-runtime-data-root <既存のruntime_data_root> --conversation-scope-id <既存のscope_id>
```
上記フラグ（Migrate Opt-inなし）で通常起動し、次のメッセージが出ることを確認する。これが「Migration必要」の合図である。

```text
error [invalid_configuration]: The conversation store uses an older schema and requires an
explicit, opted-in migration before it can start. Re-run with the migration opt-in enabled
to upgrade it in place.
```

### 4.2 Backup（ユーザー自身が実施）

Migration実行前に、`<runtime_data_root>/persistent/<scope_key>/conversations/conversations.sqlite3`を含む`runtime_data/`全体を、ユーザー自身の手でBackupする。Claude側はBackup取得を代行しない。

### 4.3 Exact Migration Command

```bash
uv run margpa-web --conversation-persistence --conversation-runtime-data-root <既存のruntime_data_root> --conversation-scope-id <既存のscope_id> --conversation-persistence-migrate
```

`--conversation-persistence-migrate`を追加した状態で1回起動する。内部で次が自動実行される（追加のユーザー操作は不要）。

1. 既存DBの`0600`ChecksumつきCheckpoint（`<runtime_data_root>/recovery/checkpoints/<scope_key>/conversations/`）を作成。
2. Staging DBへ`turn_citations`Table追加＋`storage_schema_version`を`sqlite-2`へ更新。
3. 検証後、`fsync`＋`os.replace`による原子的Cutover。
4. Migration Marker（`completed`）記録。

### 4.4 成功判定

- サーバーが通常どおり起動し、既存のChat List・各Conversationの内容が全て表示される。
- 2回目以降の起動では`--conversation-persistence-migrate`は不要（`storage_schema_version`が既に`sqlite-2`のため）。

### 4.5 失敗時／Rollback

- Migration完了前にプロセスが異常終了した場合、次回起動時に`MIGRATION_INCOMPLETE`として検出され、Fail-closedで停止する（既存Checkpointからの復旧はCodex側またはユーザーが`docs/project/phases/phase_2/architecture/phase_2_b_conversation_persistence_architecture_ja.md`記載のRollback Portを用いて個別に判断する。本Rework範囲では実DBへのRollback操作自体は実行していない）。
- 旧DBはCheckpointとして`recovery/checkpoints/`配下に保持される（Migration機構の既存契約、Phase 2-B以来変更なし）。

## 5. Manual Browser Acceptance Checklist（追加分、既存Completion Handoff第7節に追記）

10. 既存の`sqlite-1`会話データがある環境で、Migrate Opt-inなしに起動し、明示的なエラーで停止すること（データが壊れていないこと）を確認する。
11. 上記4.3の手順でMigrationを実行し、既存Conversationが全て復元されることを確認する。
12. Migration後、Documentation RAG Citationを含む新しいTurnを生成し、`GET /api/v2/runtime/components`のResponseで各Componentに128文字Hexの`canonical_digest`が入っていることを確認する（開発者向け確認、必須ではない）。

## 6. Full Validation結果

```text
Focused P2E-CODEX-001〜003 Test : 78 passed
Full Test Suite                 : 671 passed／3 deselected
  （前回Completion Handoff時 660 passed から +11、Regression 0）
Ruff Format Check                : 173 files already formatted
Ruff Check                       : All checks passed
Mypy（strict, src+tests）         : Success, no issues found in 173 source files
Node Syntax（app.js）             : OK
Node Test（safe_markdown）        : 5/5 passed
Stable Docs Diff                  : 0
実runtime_data/ Mutation          : 0（mtime Session開始前のまま。全Migration TestはtMP_pathのみ使用、
                                     実DBのMigrationは一度も実行していない）
Project Root外Mutation            : 0
Git Mutation                      : 0（実行したGit CommandはRead-only（status/diff）のみ）
新規Correction文書内Test ID       : 全件Grepで実在確認済み（第1節参照）
```

## 7. Current Blocker

```text
NONE
```

## 8. Codex Final Re-review Entry Point

```text
1. 本Rework Completion Handoff（本文書）
2. codex_to_claude_phase_2_e_required_rework_handoff_20260815081954.md（本Reworkの入力）
3. claude_phase_2_e_evidence_correction_p2e_codex_004_ja_20260815084348.md
4. git diff（e007110ba713b70f3715b991e0713e511ed21184..現在Working Tree）
   - P2E-CODEX-001: persistence_factory.py, entrypoints/web/main.py, bootstrap/web_application.py
   - P2E-CODEX-002: runtime_composition/contracts.py, bootstrap/web_application.py,
     web/runtime_composition_routes.py
   - P2E-CODEX-003: modules/conversation/adapters/sqlite_conversation_store.py
5. 第6節Full Validation結果
```

Claude側は本報告後に追加修正を開始せず停止する。
