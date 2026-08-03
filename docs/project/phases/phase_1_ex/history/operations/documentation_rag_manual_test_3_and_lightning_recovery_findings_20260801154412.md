# Documentation RAG 第3回手動Test／Lightning Recovery知見

```yaml
document_id: documentation_rag_manual_test_3_and_lightning_recovery_findings
phase: phase_1_ex
status: evidence_recorded
language: ja
created_at: 2026-08-01 15:44:12 JST
owner: 設計統括者役
evidence_source: user_manual_observation
```

## 1. Scope

次の実機Evidenceを記録する。

- Mac Local Documentation RAG
- Lightning Basic Preview Public Corpus RAG
- Lightning Public Demo Public Corpus RAG
- Lightning Runtime Snapshot混在からの復旧
- 第3回手動質問から得られた回答品質上の知見

## 2. Lightning Placement and Recovery

公開8文書は全件配置され、PreflightはBasic／Publicとも次を確認した。

```text
expected=8
present=8
missing=0
profile compatibility=pass
access boundary=pass
```

最初の起動では両Surfaceが共通Import Errorで停止した。

```text
ModuleNotFoundError:
  margpa_runtime_llm.adapters.documentation_rag.bm25_retriever
```

最新実装Statusの差分Fileだけを配置していたため、その差分が前提とするMac Documentation RAG基盤SourceがLightningに存在しなかった。Documentation RAG Directoryだけを追加した後、Test Collectionで旧Web Contractが残っていることも判明した。

```text
ImportError:
  DocumentationRagRuntimeSnapshot
```

さらに部分同期状態では、RAG Profile／ContractのVersion不一致によるInvalid Configurationと、Upload後のShell Script Permission Errorが発生した。

個別File交換を中止し、同一時点の次をLightningへ同期した。

```text
src/
config/
scripts/
tests/
pyproject.toml
uv.lock
.python-version
```

`__pycache__`、`.pyc`、`.venv`、Model、SecretおよびAllowlist外DocsはDeployment単位から除外した。Upload後に対象Shell ScriptだけのExecutable Permissionを復元した。

## 3. Recovery Verification

```text
SCRIPT_PERMISSION_EXIT:
  0

COHERENT_RUNTIME_IMPORT_OK:
  PASS

WEB_IMPORT_OK:
  PASS

RAG_INTEGRATION_IMPORT_OK:
  PASS

RAG_TEST_PLACEMENT_EXIT:
  0

Focused RAG／Web／Runtime:
  185 passed
  1 skipped
  29.49s

Web Integration isolated:
  28 passed
  0.75s

Skipped:
  Node.js unavailable for static web security contract
```

Node.js不在による1 Skipは、Lightning Python RuntimeまたはRAG起動失敗を意味しない。

復旧後、Public DemoとBasic PreviewはTraffic-aware Auto-start経路で起動し、両方でLLMおよびDocumentation RAGが動作した。Public DemoのManual Foreground起動も確認した。Basic Previewの今回のManual Foreground Command再確認は行っていないが、既存Lifecycle Acceptanceと今回のAuto-start実測は合格している。

## 4. Functional RAG Findings

### 4.1 Confirmed

- 一般質問ではRAG OFF時にCitationを出さない。
- Project質問ではRAG ON時に公開Docsを取得できる。
- Lightning Public CorpusではCitationが`docs/public/`の明示8文書に限定される。
- 日本語Queryと英語Queryの双方でReferenceを表示できる。
- Roadmap、Concept、OverviewおよびTechnology Selectionを検索対象にできる。
- Mac Local、Lightning Basic Preview、Lightning Public Demoの三SurfaceでAdapterが実際に動作する。

### 4.2 Known Quality Problems

取得とCitationが成立しても、生成回答の正確性は保証されない。

観測例：

- 根拠文書より過度に短く単純化する。
- 質問に対して部分的なSectionだけを選び、現在進捗を誤って説明する。
- 英語文書と日本語文書を混ぜ、指定言語または質問範囲からずれる。
- 一般的なLLM質問に対してProject Technology文書等の弱い関連ChunkをCitationする。
- Mac Localの広いCorpusでは、過去Phase文書をCurrent Factとして誤用する可能性がある。
- Citationが存在しても、Modelが根拠から逸脱した関係、状態または役割を生成する場合がある。

これは「検索していない」状態とは異なる。第3回Testでは検索、Context InjectionおよびCitationは成立しているが、Retriever Ranking、Chunk Selection、Current／Superseded識別、Answer Groundingおよび軽量Model能力に限界が残る。

## 5. Decision

```text
Mac Local RAG Adapter:
  FUNCTIONAL ACCEPTED

Lightning Basic Preview Public-doc RAG:
  FUNCTIONAL ACCEPTED

Lightning Public Demo Public-doc RAG:
  FUNCTIONAL ACCEPTED

Cross-environment RAG Hook:
  COMPLETE

Answer Quality／Semantic Grounding:
  KNOWN LIMITATION／FUTURE TUNING

Full RAG:
  NOT CLAIMED／PHASE 7
```

RAG機構成立と回答品質を分離する。今回のPhase 1-exでは、疎結合Adapter、Corpus境界、ON／OFF、Cross-environment接続、CitationおよびFail-closed基盤が成立したため完了とする。

精度調整は、固定Hit Keyword表またはProject固有Subject Mappingを直ちにハードコードせず、より高性能なModel、ARGD／DAGD等のGovernance、Judge、Retrieval評価、Current／Superseded MetadataおよびPhase 7本格RAGと合わせて再設計する。

## 6. Operational Lesson

対象Environmentが複数実装段階遅れている場合、実装担当Statusの最新差分だけをDeployment Setとして扱わない。

```text
Implementer changed-file list:
  delta against its documented baseline

Runtime deployment snapshot:
  coherent executable state for a target environment
```

Baseline一致が証明できない場合、`src／config／scripts／tests`を同一Snapshotとして同期する方が、連鎖Import／Contract／Config／Permission Errorを個別修復するより安全かつ低Costになり得る。この判断はケース依存だが、複数Phase差または横断Feature導入時は高優先度で検討する。
