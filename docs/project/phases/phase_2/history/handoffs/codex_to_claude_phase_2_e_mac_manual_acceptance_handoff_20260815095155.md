# Codex to Claude Phase 2-E Mac Manual Acceptance Handoff

```yaml
document_id: codex_to_claude_phase_2_e_mac_manual_acceptance_handoff_20260815095155
status: authorized_manual_acceptance
phase: phase_2
subphase: phase_2_e
from: Codexプロジェクト責任者兼設計統括者役
to: Claude設計統括者役／Claude Mac手動Test実行者役
created_at: 2026-08-15 09:51:55 JST
language: ja
baseline: e007110ba713b70f3715b991e0713e511ed21184
execution_target: phase_2_e_manual_acceptance_result
git_mutation: prohibited
provider_memory_mutation: prohibited
lightning_work: prohibited
```

## 1. Mission

Phase 2-Eの技術ScopeはCodex独立ReviewでPASSした。Claude Code側は、実Mac・Local・Loopback環境でMigrationとBrowser／Operational Acceptanceを実行し、結果をRepository内の新規Append-only HandoffとChat報告の両方でCodex側へ返す。

本Handoffは実`runtime_data/`の`sqlite-1 -> sqlite-2`への明示Migrationを、本Acceptanceに必要な1回限り許可する。それ以外の実Data削除、初期化、強制修復またはRollbackは自動許可しない。

## 2. Required Reading Order

1. `docs/project/phases/phase_2/history/handoffs/codex_to_claude_phase_2_e_mac_manual_acceptance_handoff_20260815095155.md`
2. `docs/project/shared/automation/provider_memory_and_repository_canonical_authority_ja.md`
3. `docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_final_rework_completion_handoff_20260815092725.md`
4. `docs/project/phases/phase_2/history/operations/claude_phase_2_e_real_mac_migration_and_rollback_procedure_20260815092359.md`
5. `docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_completion_handoff_20260815075322.md` 第7節
6. `docs/project/phases/phase_2/history/operations/claude_phase_2_e_evidence_correction_p2e_codex_004_ja_20260815084348.md`
7. `docs/project/shared/automation/automation_governance_index_ja.md` 第5節
8. `docs/project/shared/operations/research_asset_mutation_control_ja.md`

Provider Memory、過去Sessionの暗黙記憶またはRepository外メモをRecovery Sourceにしない。

## 3. Top-level Rules・Absolute Prohibitions

次はRole、Provider、Tool Permission、Automation段階または成果の重要度に関係なく、絶対に越えない。

1. このHandoffが存在する`margpa-runtime-llm/`をAuthorized Project Rootとする。
2. Authorized Project Root外をRead、List、Search、Stat、Execute、Write、Create、Copy、Move、Rename、Delete、Permission変更、Cache作成、Temporary Artifact作成またはSymlink追跡の対象にしない。
3. `other/`、別Project、別Repository、Backup保管場所、Home配下Provider領域、Claude Memory、Codex Memory、Cloud、LightningまたはSecret Storeへ触れない。
4. Claude Memoryへの作成、追記、更新、読取依存および自動保存を行わない。
5. `.claude/settings.local.json`、`.codex/**`、Provider Permission設定、Git ConfigまたはGit Ignoreを更新しない。既存PermissionはProject Authorityの代替にならない。
6. Git Commit、Push、Pull、Fetch、Branch、Tag、Reset、Clean、Checkout、StashまたはGitHub操作を行わない。
7. Existing Stable DocsとExisting Historyを変更しない。Resultは新規Append-only Fileだけに書く。
8. 予定外の実Data Mutation、破壊的Action、External ActionまたはScope拡張が必要になった場合は、実行せず停止する。
9. 失敗を検出しても、勝手にRollback、Cleanup、DeleteまたはBackup復元しない。
10. Provider Permission UIが表示された場合、永続許可、`always allow`、Permission Rule追加またはProvider設定保存を選択しない。1回限りの実行許可で続行できない場合は停止する。

ユーザーは`margpa-runtime-llm_2-E_Claude投入前_20260814.zip`を取得済みと報告している。Claude側はその保管場所へ触れず、この報告をHuman-provided Backup Evidenceとして扱う。

## 4. Authorized Mutation Scope

```text
AUTHORIZED_REAL_DATA_MUTATION:
  runtime_data/
    - sqlite-1 -> sqlite-2 Explicit Migration 1回
    - Acceptance中の新規Conversation・Turn・Citation保存
    - Resume・Retry・Regenerate・Branch Selectによる通常Application Mutation

AUTHORIZED_APPEND_ONLY_RESULT:
  docs/project/phases/phase_2/history/handoffs/
    claude_phase_2_e_mac_manual_acceptance_result_<timestamp>.md

  docs/project/shared/history/automation/
    automation_governance_evidence_phase_2_e_claude_manual_acceptance_cycle_ja_<timestamp>.md
```

Source、Test、Config、Stable Docs、Existing Historyその他の実DataはRead-onlyとする。

実Browser Acceptanceのため、`http://127.0.0.1:8000/`とそのSame-origin APIに限り、本HandoffのTest中のBrowser操作を明示許可する。External Domain、別Local Port、File Upload／Download、Browser設定変更、History／Cache CleanupまたはLogin情報操作は許可しない。

## 5. Launch Contract

Project RootをCurrent Directoryにし、ユーザがこれまで成功確認した次のLocal Commandを基準とする。

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000 \
  --conversation-persistence \
  --conversation-runtime-data-root "$PWD/runtime_data" \
  --conversation-scope-id "mac-local-primary" \
  --configuration-control
```

Local MacではDocumentation RAGの既存Local Profileが自動解決される。新しいProfile、DependencyまたはEnvironment変数を追加しない。

## 6. Acceptance Sequence

### A. Pre-migration Fail-closed

1. 実DBのMode、Size、mtime、SHA-512をRead-onlyで記録する。内容、Message本文、絶対PathまたはSecretはResult Docsへ記録しない。
2. 第5節のCommandをMigration Flagなしで実行する。
3. `MIGRATION_REQUIRED`に相当するSafe Errorで停止することを確認する。
4. DBのSize、mtime、SHA-512が完全不変であることを確認する。

### B. Explicit Migration

第5節のCommandの最後に次のFlagだけを追加し、1回起動する。

```text
--conversation-persistence-migrate
```

1. Serverが通常起動すること。
2. Storage Schemaが`sqlite-2`であること。
3. CheckpointとCompleted Migration Markerが存在すること。
4. Migration前のConversation件数とMigration後のConversation件数が一致すること。
5. 既存ConversationがChat Listから開け、Messageが表示されること。

Migrationが失敗した場合、その時点で停止し、Rollbackを実行せず、Error、DBのAfter Metadata、Checkpoint／Markerの存在状態と次の推奨Actionだけを報告する。

### C. Normal Restart

1. Serverを`Ctrl+C`で正常停止する。
2. Migration Flagを外し、第5節の通常Commandで再起動する。
3. Migrationを再実行せず通常起動できること。
4. Existing ConversationとMessageが再び表示できること。

### D. Documentation RAG／Persistent Citation

1. Documentation RAGをONにし、Project Docsの記載を問う新規Questionを送信する。
2. Answer完了後にSafe Citationが表示されること。
3. 同じChatでFollow-up Questionを送信し、Multi-turn Contextが維持され、CitationがTurnごとに混線しないこと。
4. Browser Reload後も両TurnのCitationが再表示されること。
5. Chat Listから別Conversationを開き、再度対象Conversationを開いてCitationが再表示されること。
6. Resume後もCitationが再表示されること。
7. RetryまたはRegenerateを実行し、新Turnに新しいCitationが表示され、元TurnのCitationが変化しないこと。
8. Branch Selectを行い、各BranchのCitationが選択したTurnと一致し、別Branchと混線しないこと。
9. Serverを再度正常停止／通常再起動し、対象ConversationのCitationが復元されること。

Browser操作Capabilityがない場合、APIまたはAutomated Testの結果をBrowser Manual PASSと偎装しない。実行できた項目だけをPASSとし、実Browser専用項目は`UNVERIFIED_CAPABILITY_LIMIT`として返す。

### E. Runtime Composition Inspection

1. 現在のServerを停止する。
2. `--runtime-composition-inspection`を付けずに通常起動し、`GET /api/v2/runtime/components`がSafe 404であること。
3. Serverを停止し、通常Commandへ`--runtime-composition-inspection`を追加して起動する。
4. `GET /api/v2/runtime/components`が200を返し、3 ComponentのIdentity、State、Capability、Side-effect、Revisionおよび128文字Hexの`canonical_digest`を返すこと。
5. EndpointのGETの前後でConversation DBとConfig状態にMutationがないこと。

### F. Phase 2-A〜2-D Regression

実Browserで次を確認する。

- Chat List・Conversation Open・New Chat。
- Send・Streaming・Stop・Resume。
- Server Restart後のConversation復元。
- Configuration Controlの表示・Preview・安全なLive Apply。
- Existing v1 Ephemeral Chatが必要な場合にRegressionしていないこと。
- UIにSecret、Absolute Path、Raw Exception、Raw ThinkingまたはHidden Originalが表示されないこと。

### G. Final State

1. Test完了後にServerを`Ctrl+C`で正常停止する。
2. 実DBのModeが`0600`、Project内Runtime DirectoryがExisting Safety Contractを維持していること。
3. Stable Docs、Source、Test、Config、Git HEAD、`.claude/settings.local.json`およびProvider Memoryを変更していないこと。
4. 予定された実`runtime_data/`Mutationと新規Append-only Result Docs以外のMutationが0であること。

## 7. Result Handoff Contract

完了後、次を新規で作成する。

```text
docs/project/phases/phase_2/history/handoffs/
  claude_phase_2_e_mac_manual_acceptance_result_<timestamp>.md
```

必須記録：

- From / To / Role / Baseline / Timestamp。
- `PASS / PARTIAL / FAIL / STOPPED` 総合判定。
- A〜Gの各結果。
- Migration前後のSchema、Conversation件数、DB Size・mtime・SHA-512変化の一致性。Digest値自体はResult Docsへ必須としない。
- Existing Conversationの復元結果。Message本文は記録しない。
- RAG Multi-turnとCitation復元9項目の結果。
- Runtime Component 404／200／Digest検証。
- Phase 2-A〜D Regression。
- 実行できなかった項目と理由。
- Root外・Memory・Permission・Git・Stable・Source・Test・ConfigのMutation 0確認。
- Error、Warning、Unexpected Event、Rollback要否。
- Exact Current State、Open Technical Blocker、User Action Required、Codex Final Review Route。

その後、Agent自動化／Cross-provider Evidenceを次へ新規Append-onlyで追加する。

```text
docs/project/shared/history/automation/
  automation_governance_evidence_phase_2_e_claude_manual_acceptance_cycle_ja_<timestamp>.md
```

ただしProvider Memoryへは記録しない。

## 8. Stop Conditions

次のいずれかで新規Mutationを停止し、Result Handoffだけを作成してCodexへ戻す。

- Migration失敗、Integrity不一致、Conversation件数不一致またはExisting Conversation取得不能。
- DBまたはCheckpointのPermission不整合。
- Safe 404／200境界不成立。
- Citation消失、Branch混線、Message破損またはSensitive情報表示。
- Source、Test、Config、Stable、Existing History、Git、Provider MemoryまたはPermission Settingsの予定外変更。
- Root外Actionが必要、または実行済みと判明。
- 破壊的Rollbackまたは未許可Cleanupが必要。

## 9. Completion Report

Claude側は、Result HandoffとEvidenceを作成した後、Chatで次の形を返す。

```text
PHASE 2-E MAC MANUAL ACCEPTANCE: PASS / PARTIAL / FAIL / STOPPED

Result Handoff:
<project-relative path>

Automation / Cross-provider Evidence:
<project-relative path>

Summary:
- Migration
- Existing Conversation Recovery
- RAG Multi-turn / Citation Recovery
- Runtime Composition
- Phase 2-A〜D Regression
- Mutation Boundary

Open Blocker:
<NONE or exact finding>

Next Route:
Codex Final Review
```

報告後は追加修正、Cleanup、Git操作、Memory保存または次Subphase開始を行わず停止する。
