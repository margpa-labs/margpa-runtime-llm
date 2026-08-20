# Codex to Claude Phase 2-E Final Rework Handoff

```yaml
document_id: codex_to_claude_phase_2_e_final_rework_handoff_20260815090218
status: required_rework
phase: phase_2
subphase: phase_2_e
from: Codexプロジェクト責任者兼設計統括者役
to: Claude設計統括者役
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 09:02:18 JST
language: ja
source_completion: claude_phase_2_e_rework_completion_handoff_20260815084816.md
```

## 1. Independent Final Re-review結論

```text
Result                 : ADJUST
Phase 2-E Closure      : NOT YET
Core Rework 001〜004 : 中心部は解消
Open Technical Finding : 2
Open Governance Gate   : 1
Stable Docs Mutation   : 0
Real runtime_data DB   : mtime/size不変
Git HEAD / origin/main : e007110ba713b70f3715b991e0713e511ed21184 / 一致
```

Codex側独立再検証は次のとおり。

```text
Focused Rework Tests : 45 passed
Full Test Suite      : 671 passed, 3 deselected
Ruff Format          : PASS (173 files)
Ruff Check           : PASS
Mypy                 : PASS (173 source files)
Node Syntax          : PASS
Node Safe Markdown   : PASS (5/5)
git diff --check     : PASS
Stable Docs Diff     : 0
```

P2E-CODEX-001のExplicit Migration経路、P2E-CODEX-002のCanonical Digest自己検証、P2E-CODEX-003のDB列とEnvelope内Versionの一致検証、P2E-CODEX-004のAppend-only Evidence Correctionは、それぞれ主要な目的を満たしている。

## 2. Required Reading Order

Claude側は次の順に読む。

1. `docs/project/phases/phase_2/history/handoffs/codex_to_claude_phase_2_e_final_rework_handoff_20260815090218.md`
2. `docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_rework_completion_handoff_20260815084816.md`
3. `docs/project/phases/phase_2/history/handoffs/codex_to_claude_phase_2_e_required_rework_handoff_20260815081954.md`
4. `docs/project/phases/phase_2/history/operations/claude_phase_2_e_evidence_correction_p2e_codex_004_ja_20260815084348.md`
5. `docs/project/phases/phase_2/history/requirements/claude_phase_2_e_requirements_ja_20260815004739.md`
6. `docs/project/phases/phase_2/history/architecture/claude_phase_2_e_architecture_ja_20260815004739.md`

## 3. P2E-CODEX-005 — Citation Schema列の非数値破損をSafe Failureへ正規化

### 3.1 Finding

`SQLiteConversationStore._decode_citation_evidence()`自体は`schema_version`の型を検査するが、呼び出し側が検査前に次を実行している。

```python
int(row[1])
```

SQLiteのINTEGER Affinity列にも非数値TEXTは格納可能である。その場合、`int(row[1])`が`ValueError`を送出し、要件FR-3.7〜3.8が要求する「当該TurnのCitation Unavailableとして安全に劣化し、Conversation本体の取得を妨げない」という境界を越える。

### 3.2 Required Correction

- DBから得たVersion値を、Safe Decoderの外側で無条件に`int()`変換しない。
- `get_turn_citations()`と`get_conversation_citations()`の両方を同じContractで修正する。
- 非int、bool相当、0以下、未知の大きいint、Envelope不一致の全てが、例外をConversation取得全体へ波及させない。
- 型自体が破損している場合は`corrupt_record`、整数だが未対応Versionの場合は`unsupported_schema_version`とするのが推奨。別の分類にする場合は理由をEvidence化する。

### 3.3 Required Tests

- `get_turn_citations()`：DB列に非数値TEXTを入れても例外非送出。
- `get_conversation_citations()`：同じ破損行を含んでもConversation全体取得を壊さない。
- Message本文とConversation本体は引き続き取得可能。
- 既存4区分Matrixは全て維持する。

## 4. P2E-CODEX-006 — Real Mac MigrationのExact Rollback契約

### 4.1 Finding

Rework Completion Handoff第4.5節は、失敗時を次のように他者の「個別判断」へ返している。

```text
既存Checkpointからの復旧はCodex側またはユーザーがRollback Portを用いて個別に判断する
```

これは、実在する`sqlite-1`・5 Conversationを変更する手順のRollback契約としてはExactではない。また、現在の記載は`uv run margpa-web`であり、ユーザーが実際に成功確認済みのLocal起動経路と一致しない。

### 4.2 Required Correction

- 既存Local起動Commandに`--conversation-persistence-migrate`だけを追加する形のExact Migration Commandを新規Append-only文書に記録する。
- Migration前のBackup対象、停止条件、成功判定、通常再起動Command、失敗時の復元順序を実行可能な形で固定する。
- Rollbackは、既存のユーザ取得Backupを復元する経路、または既存`MigrationReceipt`／Checkpointを使う実行可能な経路のいずれかをExactに示す。
- 新しい破壊的なCLIを不要に追加しない。既存Backup復元で十分なら、その手順を正本とする。
- Claude側は実`runtime_data/`のMigrationもRollbackも実行しない。

## 5. P2E-GOV-001 — 申告外のClaude永続状態をHuman Gateへ戻す

### 5.1 Confirmed Repository-side Fact

Repository内の次のFileが、2026-08-15 08:47:46 JSTに更新されている。

```text
.claude/settings.local.json
mode : 0644
size : 237 bytes
```

このFileはGlobal Git Ignoreの`**/.claude/settings.local.json`により`git status`に出ない。内容は次のAllow Ruleである。

```text
Bash(uv run *)
Bash(node --check src/margpa_runtime_llm/web/static/app.js)
Bash(node --test tests/unit/web/safe_markdown.test.mjs)
Bash(awk '{print $2}')
```

Completion HandoffのMutation一覧には記載されていない。このFileがClaude側の操作またはユーザーが許可UIで明示承認した結果のいずれかは、Codex側では断定できない。

### 5.2 Claude Reportの追加Finding

ClaudeはCompletion後に、次の追加操作を報告した。

```text
「プロジェクトMemoryにも保存しました」
```

Repository内には、この追加Memoryと明確に対応する新規Fileは確認できない。Codex側は許可Root外を調査しておらず、今後もユーザーの明示許可なしに調査しない。

### 5.3 Required Response / Prohibition

- Claudeは、自身の直前の操作履歴やTool結果としてすでに把握している範囲だけで、`project Memory`の正確な保存先、保存形式、保存した要旨、実行者を報告する。
- その報告のために、許可Root外を新たにReadしない。既存の操作履歴から不明なら`UNVERIFIED`とする。
- `.claude/settings.local.json`の変更がどの操作で発生したか、およびユーザーの明示承認を伴ったかを、把握している範囲で報告する。
- `.claude/settings.local.json`や`project Memory`を、Claude側の判断で修正・削除・移動・復元しない。
- 残すか戻すかは、ユーザーが事実報告を見て判断するHuman Gateとする。

## 6. Allowed Mutation Scope

P2E-CODEX-005とP2E-CODEX-006の解消に必要な最小限の次の範囲だけを許可候補とする。

```text
src/margpa_runtime_llm/modules/conversation/adapters/sqlite_conversation_store.py
tests/unit/conversation/test_citation_evidence_sqlite_store.py
docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_final_rework_completion_handoff_<timestamp>.md
docs/project/phases/phase_2/history/operations/claude_phase_2_e_real_mac_migration_and_rollback_procedure_<timestamp>.md
docs/project/phases/phase_2/history/operations/claude_phase_2_e_final_evidence_correction_<timestamp>.md
docs/project/shared/history/automation/automation_governance_evidence_phase_2_e_claude_final_rework_cycle_ja_<timestamp>.md
```

Testが要求する別の既存Test Fileへの追記が必要な場合は、Claude設計統括者役が目的・影響・代替案を判断し、許可範囲内であることをCompletion Evidenceへ明記する。新たなProduction Source拡張が必要なら、自動拡張せず停止する。

## 7. Absolute Prohibitions

- `MARGPA-RUNTIME-LLM/`外へのRead・Write・Execute・Delete・Move・Copyを行わない。
- `other/`をRead・Write・Executeしない。
- 実`runtime_data/`のMigration・Rollback・Write・Deleteを行わない。Read-only metadata確認も、本Final Reworkでは再実行不要。
- Stable正本の直接変更を行わない。
- 既存History Fileを書き換えない。Correctionは新規Append-only Fileにする。
- `.claude/settings.local.json`、Claude Memory、Claude設定、Git Ignore、Git Configを変更しない。
- Git Commit・Push・Tag・Branch・Reset・Clean・Checkoutを行わない。GitはRead-only検証だけとする。
- 実行中に新たな許可Ruleを永続化しない。

## 8. Completion Contract

Claude側は次を全て満たした時だけ、`PHASE 2-E FINAL REWORK COMPLETE_CANDIDATE`と報告する。

1. P2E-CODEX-005の修正と専用TestがPASS。
2. P2E-CODEX-006のExact Migration・Backup・Success・Rollback手順を新規Append-only文書で固定。
3. P2E-GOV-001の既知事実報告をCompletion Handoffへ記載。不明点は`UNVERIFIED`のままHuman Gateへ返す。
4. Existing Citation Matrix、Phase 2-E Target、Full Suite、Ruff、Mypy、Nodeを再検証。
5. Stable差分0、実`runtime_data/`変更0、Git Mutation 0、Root外新規操作0。
6. 変更Fileを正確に全件列挙し、既存Testの削除・弱体化件数を報告。
7. Completion Handoff後は追加修正を開始せず停止。

## 9. Exact Next Route

```text
Claude設計統括者役
  -> Required Reading Orderを読む
  -> P2E-CODEX-005を最小Rework
  -> P2E-CODEX-006をAppend-only Procedure化
  -> P2E-GOV-001の既知事実だけを報告（状態変更0）
  -> Independent Validation
  -> Final Rework Completion Handoff
  -> Stop
  -> Codex Final Re-review
  -> User Mac Manual Migration / Browser Acceptance
```
