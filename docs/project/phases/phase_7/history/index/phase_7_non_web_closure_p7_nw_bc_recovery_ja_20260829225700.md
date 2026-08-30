# Phase 7 Non-Web Closure Alignment — Package P7-NW-B／P7-NW-C Recovery（Local Corpus／Citation Closure Readiness、Data Controls Closure Readiness）

```yaml
document_id: phase_7_non_web_closure_p7_nw_bc_recovery_20260829225700
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 22:57:00 JST
active_contract: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md
package: P7-NW-B_and_P7-NW-C
```

## 0. Recovery Index Pointer

前Package: [P7-NW-A Recovery](phase_7_non_web_closure_p7_nw_a_recovery_ja_20260829225200.md)。次Package: P7-NW-D Recovery。P7-NW-BとP7-NW-Cはいずれも「既存実装をSourceとTestから確認するだけで、修正を要するCritical／Major／MVP Blockerが見つからなかった」という同一性質の結果になったため、1件のRecovery Indexへ統合する（PoC／MVP Operating Policy §10 Docs最小化に従う）。

## 1. P7-NW-B — Local Corpus／Citation Closure Readiness

Handoff §4 P7-NW-Bが列挙する確認対象を、既存Source・既存Test・既存Recovery Evidenceから個別に確認した。

```text
確認対象                                    | 確認結果 | 根拠
--------------------------------------------|---------|------------------------------------------
Local Document Register -> Revision／Digest | PASS    | local_corpus_registry.py、
Identity -> Composite Document Source ->    |         | test_local_corpus_registry.py(12)、
BM25 Retrieval -> Selected Evidenceだけを    |         | test_composite_document_source.py(4)、
Context Injection -> Assistant Response と  |         | test_local_corpus_end_to_end.py(4)、
Citationを分離 -> Conversation Persistence   |         | test_local_corpus_web_app.py(7)
-> Reload／Restart／Branch／Regenerate/Resume|         | （いずれもP7-B/D Recoveryで既存Green、
                                              |         |  Controller Focused Review Backend 111
                                              |         |  passedに包含、Controller Review §3.1
                                              |         |  「Local Corpus: ACCEPTED BASELINE」）
RAG OFFでRetrieval／Injection Call 0          | PASS    | 既存Phase 2 Gate無変更（P7-ACC-002、
                                              |         | P7-I Recovery §6）
登録／更新／Soft DeleteとCurrent／Historical   | PASS    | test_local_corpus_registry.pyの
分離                                          |         | Soft-delete系Test、Composite Sourceは
                                              |         | corpus_source_class単位でCurrent
                                              |         | Manifestのみ再構成
No Relevant EvidenceをCitationありへ変換しない | PASS    | 既存Grounding State機構（変更なし）、
                                              |         | test_local_corpus_end_to_end.pyで
                                              |         | 0件検索時の挙動を確認済み
Selected Chunk、Score、Document／Chunk Digest、| PASS    | 既存RetrievedChunk構造の再利用、
Retriever Identity                           |         | retriever_key/versionのEvidence化
                                              |         | （P7-ACC-008/009関連）
Local Corpus Contentが既存                   | PASS    | 本Task P7-NW-0 §4観点1で新規確認：
guardrail.context_source経路を迂回しない      |         | composite_document_source.pyを読解し、
                                              |         | 別Injection経路を新設していないことを
                                              |         | Source上で直接確認（Handoff指定の
                                              |         | 確認対象、本Task内で新たに実施した
                                              |         | 唯一の直接Source Read）
Failureを成功表示へ変換しない                 | PASS    | JsonFileLocalCorpusRegistryは
                                              |         | SqliteConversationStoreと同じFail-closed
                                              |         | 破損File検出規律を持つ（P7-B Recovery、
                                              |         | 本Task内でSource再読は行わず、既存
                                              |         | Recovery Evidenceを再利用）
```

### 1.1 本Packageで直さないと確認した項目（Handoff §4 P7-NW-B明示）

Title変更時のSource／Chunk ID再生成、Semantic Embedding／Vector Store、Retrieval Ranking品質研究、汎用File Attachment、Phase 6 Judge／Guard／Semantic Debt——いずれも本Packageでは触れていない（Source Diff 0）。

### 1.2 結論

Critical／Major／MVP Blockerに該当するProduction Composition直接Evidenceの欠落は検出しなかった。新規Testは追加していない（既存Evidenceで成立する項目へ不要なTestを追加しない、というHandoff指示に従う）。

## 2. P7-NW-C — Data Controls Closure Readiness

Handoff §4 P7-NW-Cが列挙する確認対象を、`DataControlsPanel.tsx`、`data_controls/contracts.py`、`data_controls_routes.py`、`data_controls_contracts.py`、`i18n/translations.ts`（`dataControls*`全14キー）を本Task内で直接読解して確認した。

```text
確認対象                                    | 確認結果 | 根拠
--------------------------------------------|---------|------------------------------------------
Retention Factは読取専用の実装事実であり、    | PASS    | RetentionFact(ImmutableContract)。
変更可能設定と表示しない                     |         | UI上もConsent Toggleとは別Sectionで
                                              |         | 表示専用（DataControlsPanel.tsx、
                                              |         | data-controls-retention-facts）
Purpose別Consentは互いに独立し、             | PASS    | DataControlConsent 4 Field独立、
全Default OFF                                |         | test_json_file_consent_store.py、
                                              |         | P7-ACC-026 PASS
Consent StoreのRevision／Schema、Atomic       | PASS    | JsonFileDataControlConsentStore、
Replace、Private Mode、Symlink／Corrupt       |         | SqliteConversationStore同等の規律
Failure                                      |         | （P7-G Recovery、本Taskで無変更）
保存されたConsentをTraining／Weight Update    | PASS    | test_saving_consent_never_claims_
完了と表示しない                             |         | training_occurred（P7-ACC-027）
未実装のFeedback収集、Synthetic生成、         | PASS    | 本Task内で新規確認：UI／API双方に
Training Export、全Data Export／Deleteを     |         | Export／Delete相当のButton・Routeが
利用可能と表示しない                         |         | 存在しないことを直接確認
                                              |         | （data_controls_routes.pyは
                                              |         | /policy /consent /reset の3経路のみ）
external_query_transmission_consentは        | PASS    | Docstring「Independent of whether
将来予約であり、外部送信Enforcement成立と    |         | Web Search itself is toggled ON —
Claimしない                                  |         | this documents *consent*」で
                                              |         | Enforcement未成立を明示。UIも
                                              |         | Consent Toggle文言のみでEnforcement
                                              |         | 成立を示唆しない
```

### 2.1 修正要否の判断

Handoff §4 P7-NW-Cは「UI／APIが未実装Capabilityを実行可能と誤認させる場合だけ、最小の文言／Capability Projectionを修正する」としている。本Task内での直接確認の結果、そのような誤認させる文言・Capability Projectionは検出しなかった。したがって**UI／API／文言のいずれも変更していない**。Conversation／Corpus全Export、一括Delete、TTL、Training PipelineまたはDataset Governanceの新設も行っていない（Handoff §6 Hard Scope Exclusion）。

## 3. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation: 0（P7-NW-B／P7-NW-Cとも確認のみで、修正を要する事項は検出されなかった）
Root外Read/Write: 0
```

Exact next action: P7-NW-D（User Manual Candidate／Observability）へ連結して進む。
