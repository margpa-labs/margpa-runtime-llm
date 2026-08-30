# Phase 7 Post-Manual Bounded Rework — Package P7-RW2-B Recovery（Current Turn Freshness／Grounding）

```yaml
document_id: phase_7_post_manual_bounded_rework_p7_rw2_b_recovery_20260830111500
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 11:15:00 JST
active_contract: phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md
package: P7-RW2-B
finding: P7-CODEX-008
```

## 0. Recovery Index Pointer

前Package: [P7-RW2-A Recovery](phase_7_post_manual_bounded_rework_p7_rw2_a_recovery_ja_20260830104500.md)。次Package: P7-RW2-C Recovery。

## 1. 自己修正の経緯（Handoff §11「Read-onlyの軽微な操作ミス…単独Stop理由にしない」に基づき事実を記録）

最初に試みた実装（`lexical_tokenizer.py`の`identifier_subject_tokens()`へ「2語以上連続するTitle-Case Latin語をSubjectとみなす」Heuristicを追加）は、`Nazuna Probe Orion`単体には正しく機能したが、Canonical Test実行で以下2件のMaterial Regressionを引き起こした。

```text
test_bootstrap.py::test_deferred_model_counter_falls_back_then_uses_bound_exact_counter
  Query "Nazuna Research Governance LLMの目的" の "Nazuna Research Governance"
  （3語）が誤ってSubjectと判定され、GROUNDED_READYがSUBJECT_COVERAGE_INSUFFICIENT
  へ変化した。
test_local_corpus_end_to_end.py::
  test_project_docs_citation_keeps_its_original_source_class_unchanged
  Query "MARGPAのRuntime Governance" の "Runtime Governance"（2語）が同様に
  誤判定された。
```

本Project自体のDocumentation語彙（"Runtime Governance"、"Documentation RAG"等）がTitle-Case複合英語Termで満ちているため、語数に依らずこのHeuristicは安全に境界線を引けないと判断した。既存主経路のMaterial Regressionは本Handoff §11 True Stop Condition相当の重大さがあるため、採用直前に`git checkout`で当該File（`lexical_tokenizer.py`）を破棄前の状態へ復元し、影響を受けた`bounded_context_assembler.py`（同時に試みた`REFERENCE_INSTRUCTION`文言拡張も、複数の既存Testが同定数の厳密な文字数境界に依存しており撤回）も個別に文字列単位で元へ戻した。両File復元後、`156 passed`（documentation_rag／conversation_generation関連Suite）でBaseline回復を確認した。

その後、より狭いScopeの代替実装（§2）へ切り替えた。

## 2. 採用した実装

### 2.1 BM25 Backfill Identifier-Overlap Guard（`bm25_retriever.py`）

`retrieve()`のTop-k Backfill Loop（既存の`for score, components, item in scored: ...`）が、Query側で既に計算済みの`analysis.identifier_tokens`（新設Heuristic不要、既存`GenericNaturalLanguageQueryAnalyzer`が返す既存Field）と一切共有Termを持たないChunkを、単にTop-k埋めのためだけに追加しないよう1条件を追加した。Queryが具体的なIdentifier様Termを一つも含まない場合（`identifier_tokens`が空）は無条件で従来通り動作し、通常の低特定性Topic検索（例: "MARGPAのRuntime Governance"）には一切影響しない。

結果として、`Nazuna Probe Orion`削除後の再質問は、無関係なProject Docsを機械的にBackfillせず`retrieval.selected == ()`（NO_HIT）へ収束する。

### 2.2 NO_HIT Freshness Notice（`conversation_generation.py`）

NO_HIT状態は契約上（`DocumentationEvidence`の`model_validator`）`should_generate=True`のまま一般会話を許可し続けるが、これまで`reference_message`が常に`None`のため`_inject_documentation_reference()`が何も注入しなかった。新たに、`augmentation.state is ENABLED`かつ`grounding_state is NO_HIT`の場合だけ、独立した非BudgetのTOOL Message（`NO_HIT_FRESHNESS_INSTRUCTION`）を注入する。既存のGROUNDED_READY経路（`REFERENCE_INSTRUCTION`、Token/Character Budget計算）には一切触れていないため、既存の厳密境界Testへの影響はない。

## 3. Regression（Handoff §7.3 Required Regression Scenario、8手順全件）

新規Integration Test`test_nazuna_probe_orion_freshness_update_delete_regression`（`tests/integration/documentation_rag/test_local_corpus_end_to_end.py`）で、Handoff §7.3の8手順を1つのDeterministic Fixtureとして再現した。

```text
1. rev1登録（CEDAR-7319）                                    -> PASS
2. 質問1: GROUNDED_READY、reference_messageにCEDAR-7319         -> PASS
3. rev2更新（CEDAR-8420）                                     -> PASS
4. 質問2: GROUNDED_READY、reference_messageにCEDAR-8420のみ、
   Citation document_sha512がrev1と異なる                       -> PASS
5. Soft-delete                                                -> PASS
6. 質問3: NO_HIT、reference_message=None、citations=()、
   reference_blocks=()（無関係Citationなし）                    -> PASS
7. 同一Queryを独立呼び出し（新規Conversation相当）: NO_HIT       -> PASS
8. 手順2／4で捕捉したAugmentationオブジェクトの内容が不変        -> PASS
```

その他Regression:

```text
tests/unit/documentation_rag/test_lexical_retrieval.py (新規3 Test):
  test_backfill_excludes_chunks_unrelated_to_named_identifiers_after_deletion
  test_backfill_still_finds_the_matching_document_when_it_exists
  test_backfill_is_unaffected_when_the_query_has_no_identifier_tokens

tests/unit/conversation/test_conversation_generation.py (新規1 Test):
  test_no_hit_splices_a_freshness_notice_and_still_generates
```

## 4. 全体検証

```text
uv run pytest -q                     -> 1930 passed, 7 deselected（P7-I基準1924から+6）
uv run mypy                          -> Success, no issues found in 526 source files
uv run ruff check .                  -> All checks passed
uv run ruff format --check .         -> 526 files already formatted
```

## 5. Scope境界の遵守

Embedding、Vector DB、一般的なTruth VerificationまたはPhase 6 Judge Reworkへは拡張していない。過去Turnの本文／Citation／Revision／Digestは一切書き換えていない（Lexical Retrieval側のみの修正、Historical Persistence Pathは無変更）。P7-ACC-008（Embedding未使用PARTIAL）は維持。

## 6. 既知の残存Limitation（Minor、延期）

Rev1→Rev2の直後、同一Chat内での**最初の**再質問1回だけ旧値を答え、次のTurnで自己修正するFlakiness（User Mac Manual Acceptance §2.6 `PASS_WITH_FRESHNESS_OBSERVATION`）は、本修正の直接対象ではない（GROUNDED_READY経路自体は既に正しくRev2のReference Messageを渡しており、Modelの応答傾向に依存する領域のため、実LLM Sampleを伴わないUnit Testでは決定的に保証できない）。`REFERENCE_INSTRUCTION`文言強化によるMitigationは、既存Budget境界Testとの衝突により本Task内では見送った。Minor、延期として記録する（新規Finding番号は付与しない。既存P7-CODEX-008 Findingの範囲内であり、Blockerには該当しない）。

## 7. Action Inventory

```text
Git Action: 1（git checkout -- lexical_tokenizer.py、Read-only破棄目的のRevert。
  Handoff §7の許容範囲内、Source Mutation 0への復元操作として実施、開示済み）
Network Action: 0
Source／Test Mutation: bm25_retriever.py, conversation_generation.py（Source 2File）、
  test_lexical_retrieval.py, test_conversation_generation.py,
  test_local_corpus_end_to_end.py（Test 3File）
Root外Read/Write: 0
```

Exact next action: P7-RW2-C（Lazy Auto-Resume）へ連結して進む。
