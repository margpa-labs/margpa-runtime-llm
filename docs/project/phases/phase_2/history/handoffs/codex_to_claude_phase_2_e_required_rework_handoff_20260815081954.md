# Codex to Claude Phase 2-E Required Rework Handoff

```yaml
document_id: codex_to_claude_phase_2_e_required_rework_handoff_20260815081954
status: rework_required
phase: phase_2
subphase: phase_2_e
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude設計統括者役
baseline: e007110ba713b70f3715b991e0713e511ed21184
created_at: 2026-08-15 08:19:54 JST
language: ja
supersedes_none: true
```

## 1. Purpose

Claude側のPhase 2-E `COMPLETE_CANDIDATE`に対するCodex独立Final Reviewの結果を受け、現在の実装を`COMPLETE`へ昇格する前に必要なReworkを固定する。

Codexは本Reviewの検証過程でSource、Test、Git、実`runtime_data/`を変更していない。Docsの新規追加は本Rework Handoff 1件だけである。

## 2. Required Reading Order

Claude設計統括者役は、次の順序で読み、本Handoffを今回Reworkの直接入力とする。

1. `docs/project/phases/phase_2/history/handoffs/codex_to_claude_phase_2_e_required_rework_handoff_20260815081954.md`
2. `docs/project/phases/phase_2/history/handoffs/claude_phase_2_e_completion_handoff_20260815075322.md`
3. `docs/project/phases/phase_2/history/requirements/claude_phase_2_e_requirements_ja_20260815004739.md`
4. `docs/project/phases/phase_2/history/architecture/claude_phase_2_e_architecture_ja_20260815004739.md`
5. `docs/project/phases/phase_2/history/operations/claude_phase_2_e_acceptance_matrix_ja_20260815004739.md`
6. `docs/project/phases/phase_2/history/operations/claude_phase_2_e_conformance_review_ja_20260815075219.md`
7. 現在のWorking Tree差分と、本Handoffに列挙するSource／Test。

Stable正本は参照のみとし、明示されたHistory新規文書以外のDocsを変更しない。

## 3. Codex Independent Review Result

```text
Decision                  : ADJUST
Phase 2-E Complete        : NO
Stable Docs Diff          : 0
Tracked Modified Files    : 21
Untracked New Files       : 24
Independent Target Test   : 70 passed
Independent Full Test     : 660 passed / 3 deselected
Ruff / Mypy / Node        : PASS
Real runtime_data Mutation: 0
Git Mutation              : 0
```

広範なRegressionは検出していない。下記3件とEvidence補正だけをCurrent Rework Scopeとし、過去のDeferred事項を再活性化しない。

## 4. Required Finding P2E-CODEX-001 — Existing sqlite-1 Runtime Cannot Start

### Evidence

現在のユーザーMac実DBは次の状態である。

```text
storage_schema_version : sqlite-1
domain_schema_version  : 1
migration_state        : ready
conversation_count     : 5
turn_citations table   : absent
```

更新後の`SQLiteConversationStore.inspect_schema()`は正しく`MIGRATION_REQUIRED`を返す。しかし、`start_local_conversation_persistence()`は`EMPTY`と`READY`以外でも`open_ready_store()`を呼ぶため、既存Phase 2-D Chatを保持した通常起動はFail-closedで停止する。

### Required Outcome

- `sqlite-1 → sqlite-2`を、既存Checkpoint／Digest／Rollback契約を用いて実行できる。
- Migrationはユーザーの明示的な実行操作または明示Opt-inを必須とし、通常起動時に無断で実データをMigrationしない。
- Migration完了後は通常起動が成功し、既存Conversation／Message／Revisionが保持される。
- Migration失敗時は旧DBが不変で、中途状態をFail-closedで識別する。
- `sqlite-1`の会話データを持つFixtureから、「明示Migration → 通常Runtime Start → 会話読込」を通すIntegration Testを追加する。
- User Manual Acceptance用に、実行するExact Command、Backup／Checkpoint、成功判定、Rollback手順をCompletion Handoff Correctionへ記録する。

## 5. Required Finding P2E-CODEX-002 — Runtime Component Canonical Digest Is Empty

### Evidence

`_register_runtime_components()`が生成する3 Componentの`canonical_digest`は全て空文字である。`ComponentDescriptor.__post_init__()`も空文字を許可し、HTTP ResponseはDigest Field自体を投影していない。これはFR-1.1の「DescriptorはCanonical Digestを含む」と一致しない。

### Required Outcome

- 全ての登録済みDescriptorが、そのCanonical Payloadに対する正規SHA-512 Digestを必ず持つ。
- 空Digest、形式不正Digest、Payloadと不一致のDigestを黙って登録しない。
- Local Read-only EndpointからSafe Digestを投影する。
- Documentation RAG／Conversation Persistence／Configuration Controlの3件について、非空／128 hex／Payload変化時のDigest変化／HTTP投影をTestする。
- Registryが実行Authorityを生成しない既存契約は不変とする。

## 6. Required Finding P2E-CODEX-003 — Unknown Embedded Citation Schema Is Accepted

### Evidence

`SQLiteConversationStore._decode_citation_evidence()`はDB列の`citation_schema_version`だけを上限比較し、JSON Envelope内の`citation_evidence.citation_schema_version`との一致および対応Versionを検証していない。

Codexの独立再現で、次が正常な`PersistedTurnCitationEvidence`として返った。

```text
database column citation_schema_version : 1
embedded citation_schema_version        : 999
actual result                           : accepted
```

### Required Outcome

- Citation Schema Versionは現行の対応Versionだけを構築可能にするか、Decode時に明示的にSupported Version集合へ照合する。
- DB列VersionとEnvelope内Versionが不一致なRecordを正常Citationとして返さない。
- 未知の新Versionは`CitationUnavailable(reason="unsupported_schema_version")`とし、Conversation本体は読み込める契約を維持する。
- 列のみ未知、Envelopeのみ未知、両者不一致、正常VersionのTest Matrixを追加する。

## 7. Required Evidence Correction P2E-CODEX-004

Technical Reworkと並行し、次を新規Append-only Correction文書で補正する。既存History文書を上書きしない。

- Acceptance Matrixには、現在のRepositoryに存在しないExact Test名が複数記載されている。実在するTest IDへの写像に補正する。
- FR-1.1はDigestの必須性までTestできていなかったため、新規Testを正しく対応付ける。
- FR-3.7はDB列VersionだけでなくEnvelope内Versionと不一致も含むTestへ補正する。
- Completion／Conformanceの「既存Test変更0」は事実と異なる。実際は既存Test 5 Fileが変更されている。削除・弱体化は検出されず、Test Double対応と追加Testが中心であることを正確に記録する。
- Design Review後に新規History Draft 6文書のstatus Fieldを同一File上で`frozen`へ変更した件は、Stable正本変更ではないが、Append-only運用上のDeviationとして記録する。現時点で旧内容を復元せず、今後の訂正は新規Correction文書で行う。
- Frozen Mutation Manifest外の4 Source Pathを後続Conformance Reviewで追認した件も、事後EvidenceであったことをDeviationとして記録する。

## 8. Rework Authority and Boundaries

Claude設統括者役は、上記3件とEvidence Correctionを閉じるために必要な最小Source／Test／History新規文書のみを動的に解決する。

### Permitted

- 現在のPhase 2-E変更Source、および上記3件を閉じるために直接必要な既存Phase 2-E関連Sourceの最小変更。
- `tests/**`の最小新規／追加Test。既存Regression Testを削除・弱体化しない。
- `docs/project/phases/phase_2/history/**`および`docs/project/shared/history/automation/**`への新規Append-only Correction／Rework Status／Final Review／Completion Handoff。
- Claude設計統括者役が必要に応じてPhase 2-E設計担当者役／実装者役／Review役を分離し、上記範囲内で自律的に完遂すること。

### Prohibited

- 指定Project Root外の読取・作成・変更・削除。
- `other/`への全アクセス。
- 実`runtime_data/`のMigration／書込／補正。Migration TestはTemporary Fixtureだけを使用する。
- Stable正本（`docs/project/current/**`、`docs/public/**`、`docs/project/shared/**`のHistory外、Phase Index、Phase 2 Stable Requirements／Architecture／ADR／Governance／Handoff／Operations）の変更。
- 既存History文書の直接修正。
- Git Commit／Push／Branch／Merge／Tag／Release。
- Network／Lightning／Secret／External Service操作。
- 本Reworkに無関係なDeferred事項、Phase 2-F、Agent／Tool、Full Governance Engine、Full RAGの開始。
- 通常起動時の無断データMigration。

## 9. Required Validation

1. P2E-CODEX-001〜003のFocused Test。
2. Phase 2-E Target Test。
3. Conversation／Web／Documentation RAG／Configuration Control Regression。
4. Full Test Suite。
5. Ruff Format Check／Ruff Check／Mypy／Node Syntax／Safe Markdown Test。
6. Stable Docs Diff 0。
7. 実`runtime_data/`Mutation 0。
8. Project Root外Mutation 0。
9. Git Mutation 0。
10. 新規Correction文書内での実在Test ID照合。

## 10. Completion Contract

Claude側は、次を全て満たした場合だけ`PHASE 2-E REWORK COMPLETE_CANDIDATE`を返す。

- P2E-CODEX-001〜004が全てCLOSED。
- Open Technical Findingが`NONE`。
- Independent ReviewとFull ValidationがPASS。
- Stable正本、実`runtime_data/`、Project Root外、Gitへの禁止Mutationが0。
- 実Mac向けの明示Migration手順とManual Browser Acceptance Checklistが、新規Completion Handoffに揃っている。
- Codex側がその新規Completion Handoffを起点にFinal Re-reviewできる。

Claude側は完了報告後に追加修正を開始せず停止する。

## 11. Current Status

```text
Current Point             : Codex Final Review -> Required Rework Handoff Ready
Open Current Blocker      : P2E-CODEX-001 / 002 / 003 / 004
User Runtime Acceptance   : NOT STARTED
Phase 2-E Complete        : NO
Exact Next Route          : Claude設計統括者役が本Handoffを読み、Rework実行後に新規Completion Handoffを返す
```
