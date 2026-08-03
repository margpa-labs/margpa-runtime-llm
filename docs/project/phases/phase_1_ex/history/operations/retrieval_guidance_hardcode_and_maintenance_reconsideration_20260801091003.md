# Retrieval Guidance Hard-code／Maintenance再検討Record

```yaml
document_id: retrieval_guidance_hardcode_and_maintenance_reconsideration
phase: phase_1_ex
status: deferred_for_future_redesign
language: ja
created_at: 2026-08-01 09:10:03 JST
owner: 設計統括者役
source_evidence: mac_local_documentation_rag_manual_test_2_findings_20260801084952.md
```

## 1. Context

Mac限定簡易Documentation RAG第2回手動Testでは、正式名称、略称、文書責務およびSection関係の選択精度を改善する候補として、文書ごとの「ヒットキーワード列」またはRAG用の「Model参照用Index表」を挙げた。

その後、ユーザーから次の懸念が提示された。

```text
文書ごとのKeyword表や参照Index表も、結局はHard-codeになり得る。
文書追加、名称変更、Section移動および多言語化のたびに手動保守が必要になる。
保守性が悪化するため、現時点では採用したくない。
RAG精度を再調整する時点で、より良い方法を改めて検討する。
```

## 2. Decision

Hit Keyword列、Model参照用Index表または手作業のSubject→Document対応表を、現在の実装予定へ入れない。

前Recordで示した`RetrievalMetadataPort`は、採用済み設計ではなく、比較対象となり得る未確定候補としてだけ残す。

```text
Current status:
  not selected
  not authorized for implementation
  not a Phase 1-ex acceptance requirement

Future status:
  reconsider only when retrieval quality is redesigned
```

## 3. Why Manual Mapping Is Not Preferred

- 文書、Section、Aliasおよび翻訳版の増加に比例して保守量が増える。
- Canonical文書とKeyword表の更新時点がずれ、Stale Mappingを生み得る。
- 特定の現在Corpusへ過適合し、未知のGD、未知Schema、空Corpusを受け入れるProject原則と緊張する。
- 誤ったMappingがRetrieval Biasとなり、Citationがあるように見える誤回答を強化し得る。
- Main Model、RetrieverまたはCorpus交換時に手動表が隠れた依存となる。
- 「存在」「検索上の優先」「Authority」「真実性」を混同しやすい。

## 4. Future Reconsideration Questions

再調整時には、手動Keyword表を前提にせず、少なくとも次を比較する。

```text
Deterministic document-derived signals:
  headings
  glossary／definition syntax
  acronym expansion
  emphasized terms
  document role inferred from validated structure

Automatic build-time derivation:
  digest-bound generated retrieval metadata
  stale detection
  reproducible regeneration

Retrieval changes:
  query decomposition
  language-aware ranking
  sparse／dense hybrid
  semantic reranker
  authority-aware section selection

Evaluation／Governance:
  claim-to-citation entailment
  ARGD／DAGD
  Judge
  Repair／retrieve-more／refuse

Model／Corpus changes:
  upgraded main model
  rewritten public docs
  explicit glossary section inside canonical docs
```

いずれの方式も、Ablation、Maintenance Cost、Stale Risk、Unknown Document対応、LatencyおよびFailure Modeを比較してから採用する。

## 5. Non-negotiable Boundary

- Source CodeへProject固有略称を列挙しない。
- 特定のGD名、EASA、DLAGSA、OCILNS、ARGDまたはDAGDをRetrieverへHard-codeしない。
- Metadataの存在からAuthority、TruthまたはExecution Permissionを生成しない。
- 自動生成Metadataも根拠本文の代替にしない。
- 再設計前に「予約済みだから」という理由だけで実装しない。

## 6. Effect on Current Work

Mac RAGのScoped Acceptanceは変更しない。

Lightning Public Corpus RAGでは、既存のDeterministic Markdown Chunking、Lexical Retrieval、Bounded AssemblyおよびCitationを再利用する。Hit Keyword表／Model参照Index表は実装しない。

本件は、RAG精度改善を再開する将来時点のArchitecture Decisionとして改めて設計する。
