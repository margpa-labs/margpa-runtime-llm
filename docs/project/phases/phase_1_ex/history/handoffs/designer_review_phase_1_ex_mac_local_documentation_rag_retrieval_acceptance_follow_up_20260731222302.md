# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG Retrieval Acceptance Follow-up

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up
phase: phase_1_ex
status: accepted_ready_for_user_manual_acceptance
language: ja
created_at: 2026-07-31 22:23:02 JST
owner: 設計統括者役
review_target: implementer_status_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731220726.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_retrieval_acceptance_follow_up_20260731214639.md
manual_acceptance_performed: false
manual_acceptance_gate: go
supersedes: null
```

## 1. Result

```text
Retrieval Acceptance Follow-up:
  ACCEPTED

F5 Natural-language Query Relevance:
  RESOLVED

F6 Canonical Fixture Integrity:
  RESOLVED

F7 Measurement Unit Evidence:
  RESOLVED

Required Automated Regression:
  GREEN

Local GGUF／Browser Manual Acceptance:
  GO／NOT_YET_PERFORMED
```

実装担当Status、変更Source、Test、SHA-512および実Project Corpusを独立に再確認した。

前ReviewでManual Acceptanceを妨げていたF5～F7は解消しており、新たなBlocking Findingはない。ユーザーによるLocal Mac Web・実GGUF・Browser Manual Acceptanceへ進んでよい。

## 2. Reviewed Scope

変更対象は次の範囲に限定されている。

```text
Production:
  lexical tokenizer
  generic query analyzer
  BM25 retriever
  documentation RAG contracts
  bounded context assembler
  documentation RAG application service

Tests:
  documentation RAG unit／integration
  conversation contract propagation
  web contract propagation

Documentation:
  implementer append-only status only
```

次のScope拡大はない。

```text
New Dependency
Embedding／Vector DB／Persistent Index
Corpus Allowlist変更
Config変更
Model Backend変更
Lightning／Public Demo RAG
Git／Network／External Service操作
```

## 3. Integrity Verification

実装担当Statusが記載した変更後SHA-512と現在FileのSHA-512を全件照合した。

```text
Checked Files:
  12

SHA-512 Match:
  12／12

Mismatch:
  0
```

Production対象Directoryに対し、次のProject固有語Hard-codeを検索した。

```text
roadmap
ARGD
DAGD
EASA
DLAGSA
OCILNS
```

Result：Production Code内0件。

## 4. F5 Review：Natural-language Query Relevance

### 4.1 Architecture

`GenericNaturalLanguageQueryAnalyzer`がRetrieverから分離され、次の一般則を保持する。

```text
Latin／Numeric／Path／Code Identifier:
  high signal

Other natural-language context:
  auxiliary signal

No identifier query:
  existing Japanese n-gram frequency behavior
```

Index側TokenizerはVersion 1を維持し、Query AnalyzerはVersion 1として新設された。RetrieverはRanking Algorithm変更に合わせVersion 2から3へ更新され、旧Cache Keyと分離されている。

BM25 DF、Body／Heading／Path Weight、Exact Phrase、Corpus Priority、Document Diversity、Minimum Score、No HitおよびDeterministic Tie-breakは維持されている。

### 4.2 Noisy Corpus

正本1件と、丁寧表現およびSubject参照を含むDistractor 8件で、Production Default `top_k=4`の順位を固定するTestを確認した。

```text
Roadmap:
  canonical top-ranked

ARGD／DAGD:
  canonical top-ranked

EASA:
  canonical top-ranked

DLAGSA:
  canonical top-ranked

OCILNS:
  canonical top-ranked

System Architecture:
  canonical top-ranked

Project Overview:
  canonical top-ranked
```

同一Inputの反復取得結果も同一である。

### 4.3 Real Project Corpus

Model生成を行わず、現在のAllowlist CorpusからCitationを再取得した。

| Query | Selected Order | Verified Source |
|---|---:|---|
| `Nazuna Research Governance LLMとは何ですか?` | 1 | Current Runtime Governance |
| `roadmapの現在の進捗を教えてください` | 1 | `docs/public/roadmap_ja.md` |
| `システムArchitectureを説明してください` | 1 | Current System Architecture |
| `ARGDとDAGDについて説明してください` | 1 | Current Governance ARGD／DAGD |
| `EASAとは何ですか?` | 1 | Phase 1 Governance Catalog EASA |
| `DLAGSAとは何ですか?` | 1 | Phase 1 Governance Catalog DLAGSA |
| `OCILNSとは何ですか?` | 1 | Phase 1 Architecture OCILNS Boundary |

Roadmap、ARGD／DAGD、EASAおよびDLAGSAは前Reviewで確認した無関係なLanguage Smoke／User Manual断片を上位に選択しない。OCILNSも定義に直接関連するArchitecture Boundaryが最上位である。

## 5. F6 Review：Canonical Fixture Integrity

Fixtureの意味をCurrent CanonicalおよびPhase 1 Governance Catalogと照合した。

```text
ARGD:
  Premise／Context／矛盾／情報不足／根拠／反証／代替仮説／表現／Drift／Repair

DAGD:
  Policy Goal／Constraint／Capability／Evaluation／Severity／Audit／Repair／
  Activation／Self Audit／Audit-to-Action／Status Reporting

EASA:
  内部安全傾向／周辺安全制御／入力文脈／生成過程／Composite Safety Behavior
  単一物理Layerを断定しない

DLAGSA:
  複数の判断／実行／検証主体間の責任／委譲／例外／改竄耐性付き証跡／
  全体整合／異常時安全側制御

OCILNS:
  人／AI／Tool／外部System間の認知対話を検証／参照／継承／監査可能な
  改竄耐性付き証跡単位として扱う台帳網
```

旧Fixtureの誤った定義は残っていない。略称から非公開Algorithmまたは未開示Protocolを推測した追加もない。

## 6. F7 Review：Measurement Unit Evidence

次の単位をContractで明示する。

```text
tokens
unicode_characters
```

`estimated_tokens`は廃止され、Blockは`measured_size`と`measurement_unit`を保持する。ContextおよびEvidenceもBudget Unit、Measurement Unit、Same-unit LimitおよびFallback Stateを分離する。

Pydantic不変条件は次を拒否する。

- Token FlagとMeasurement Unitの不一致。
- Fallback FlagとMeasurement Unitの不一致。
- BlockとContextのMeasurement Unit不一致。
- 同一単位Limit超過。
- Exact Token Measurement LimitとDynamic Token Budgetの不一致。

Counter未Bindingまたは失敗時は`unicode_characters`および`token_counter_fallback_used=true`となり、Unicode Character数をToken数として記録しない。

## 7. Automated Verification

設計統括者役が独立実行した。Test CacheへのWriteを避け、Python Bytecodeの新規生成を抑止した。

```text
Combined Required Target Suite:
  271 passed
  3.61s

Repository Full Suite:
  395 passed
  3 deselected
  48.30s

Ruff Check:
  PASS

Ruff Format Check:
  PASS／120 files

Mypy:
  PASS／120 source files

JavaScript Syntax:
  PASS
```

## 8. Additional Model Smoke Observation

Review範囲を超えた追加確認として`model_smoke`を起動したが、2件が`Failed to create llama_context`で停止した。

同時にLocal Port 8000でPython Web ProcessがListen中であることをRead-only確認した。16GB Unified Memory環境で既存Web RuntimeとSmoke TestがModel／Contextを二重に保持しようとした状態であり、RAG差分の回帰Failureとは判定しない。

```text
Model Smoke Result:
  NOT_EVALUABLE_DURING_EXISTING_LOCAL_WEB_RUNTIME

Existing Process Stop:
  NOT_PERFORMED

Manual Acceptance:
  existing Web Runtimeを適切にRestartし、単一Model Instanceで確認する
```

設計統括者役は既存Processを停止、変更またはKillしていない。

## 9. Non-blocking Known Limitation

初期RetrieverはSparse／Lexicalであり、Semantic Retrievalではない。追加の境界確認で、ASCIIの`/`または`-`だけのSequenceも現行TokenizerでIdentifierとして解釈され、日本語だけの主題Signalを弱める場合があることを確認した。

次の理由でManual AcceptanceのBlockerとはしない。

- Accepted受入Queryと実Corpusの全必須区分は正本を取得する。
- 初期実装がLexical RetrievalであることはAccepted済みの制約である。
- 該当記号を含まない通常の日本語Queryは従来の2-gram／3-gram検索を維持する。
- 後続のRetrieval Evaluation／Hybrid Retrievalで精度を比較・改善できる。

Manual Acceptanceで実用上の問題が出た場合は、問題Query、Citation Path／Headingおよび期待SourceをEvidenceとして別Follow-upに戻す。

## 10. Acceptance Decision

```text
Initial Implementation:
  ACCEPTED AFTER FOLLOW-UPS

Correctness Follow-up:
  ACCEPTED

Context Fallback Follow-up:
  ACCEPTED

Retrieval Acceptance Follow-up:
  ACCEPTED

User Local GGUF／Browser Manual Acceptance:
  AUTHORIZED

Public Demo／Lightning Documentation RAG:
  DENIED／OUT_OF_SCOPE
```

実装担当への追加修正Handoffは作成しない。次はユーザー所有のLocal Mac Manual Acceptanceである。

