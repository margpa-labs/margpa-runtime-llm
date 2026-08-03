# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG Coverage Integrity Follow-up

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up
phase: phase_1_ex
status: implementation_accepted_manual_retest_go
language: ja
created_at: 2026-08-01 01:43:39 JST
owner: 設計統括者役
source_index: ../documentation_index_20260801003625.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up_20260801003625.md
reviewed_status: implementer_status_phase_1_ex_mac_local_documentation_rag_coverage_integrity_follow_up_20260801013611.md
manual_acceptance_gate: go
```

## 1. Decision

実装担当Status、変更Source、Contract、Test、SHA-512、Full SuiteおよびStatic Checkを独立に確認した。

```text
F13 RetrievalとAssembled Coverageの分離:
  ACCEPTED

F13 Partial／Missing Subject Fail-closed:
  ACCEPTED

F14 High-signal Identifier Classification:
  ACCEPTED

F8／F9／F11／F12 Regression:
  ACCEPTED

Implementation:
  ACCEPTED

Mac Local GGUF／Browser Manual Retest:
  GO

Mac限定簡易Documentation RAG全体の最終Acceptance:
  PENDING USER MANUAL EVIDENCE
```

本Reviewは、前ReviewのBlocker F13／F14がSource境界と自動Test上で解消されたことをAcceptedとする。実GGUFによる回答品質、実Token Budgetでの使用可否およびBrowser Lifecycleは未実施のため、機能全体の最終Acceptanceは宣言しない。

## 2. Accepted F13：Coverage Integrity

### 2.1 StageごとのCoverage分離

Coverageは次の2段階に分離された。

```text
Retrieval Stage:
  retrieval_covered_subject_count
  retrieval_uncovered_subject_count

Assembly Stage／Model実入力:
  covered_subject_count
  uncovered_subject_count
```

`SubjectCoverageTrace`はSubjectのSHA-512 DigestからSelected Chunk IDへのTransient Mappingを保持する。Raw Query、Raw Docs、Absolute PathまたはSubject文字列自体を新たな永続Evidenceとして追加していない。

### 2.2 AssemblyをAuthorityとする決定

次はすべて、実際にModel Promptへ入ったAssembled Chunk集合から導出される。

```text
assembled coverage
citation
assembled block count
grounding state
generation decision
```

Retrieverが3 Subjectを取得しても、Context Budgetにより1～2 SubjectしかAssemblyされない場合は次となる。

```text
grounding_state:
  subject_coverage_insufficient

should_generate:
  false

reference_message for model:
  none

inference call:
  zero
```

System Citationは実Assembly分だけを示すが、Denied状態ではModelへReference Messageを渡さない。これにより「Citationは1件だけだがEvidenceは3／3で、残りをModelが推測する」という不整合は閉じられた。

### 2.3 Missing Subject

3 Subject Queryに対しCorpus根拠が2 SubjectしかないFixtureで、Retrieval 2／3、Assembly 2／3、Generation DeniedおよびModel Call 0が検証されている。一部の根拠だけで全質問へGrounded Answerを作らない。

## 3. Accepted F14：High-signal Identifier Classification

Coverage SubjectはNFKC後、Case Fold前のSurface形状で判定される。

```text
Accepted generic signals:
  2文字以上のAll-uppercase Acronym
  数字を持つCode-like Token
  _ . / - を持つIdentifier／Path-like Token
  先頭以降に大文字を持つCamel／Mixed-case Token

Not a subject by initial capitalization alone:
  What
  Explain
  Briefly
```

`What`、`are`、`and`等はLexical Retrieval Signalに残るがCoverage Slotを消費しない。EASA／DLAGSA／OCILNS等のProject固有Allowlistまたはそれらを特別扱いするProduction Hard-codeはない。未知のZXQ／NVRTA／PLMKS Fixtureで同一の一般則が検証されている。

Tokenizer／Analyzer／Retrieverの意味変更に応じてVersionが更新され、Index Cache Keyも旧版から分離された。

## 4. Contract and Model-call Boundary

`DocumentationEvidence`は次をValidatorで拒否する。

- Retrieval Coverageの合計がSubject Countと一致しない。
- Assembly Coverageの合計がSubject Countと一致しない。
- Assembly CoverageがRetrieval Coverageを超える。
- `grounded_ready`でUncovered Subjectが残る。
- `context_insufficient`でAssembled BlockまたはCovered Subjectが存在する。
- `subject_coverage_insufficient`でGenerationが許可される。
- Citation Count、Assembled Block CountおよびEvidenceが一致しない。
- Denied AugmentationにModel用Reference Messageが含まれる。

Conversation Layerは`should_generate=false`の場合、Retrieval Eventの後にSafe Errorを返し、Inference Requestを作成しない。Integration TestでModel Call 0を確認した。

## 5. Independent Verification

### 5.1 Artifact Integrity

Implementer Statusに記載された変更Artifact 11件のAfter SHA-512を現在Fileと照合した。

```text
11／11:
  MATCH
```

### 5.2 Focused and Full Verification

```text
Focused Documentation RAG／Conversation／Web:
  152 passed

Repository Full Suite:
  408 passed
  3 deselected
  49.44s

Ruff Check:
  PASS

Ruff Format:
  PASS／120 files

Mypy:
  PASS／120 source files

JavaScript Syntax:
  PASS
```

### 5.3 Real Corpus Read-only Smoke

Implementerの実Corpus Read-only Smokeは、限定されたSimulation Budgetで次のSafe Boundaryを示した。

```text
Japanese combined:
  Retrieval 3／3
  Assembly 0／3
  context_insufficient
  denied

English combined:
  Retrieval 3／3
  Assembly 1／3
  subject_coverage_insufficient
  denied

Unknown uppercase identifiers:
  Retrieval 0／3
  Assembly 0／3
  subject_coverage_insufficient
  denied
```

これは、根拠不足またはAssembly不足のままModelを呼ばないというCorrectness確認である。実GGUF Token Counterと実Queryで必要なBlockを組み立てられるかはManual Retestで別に判定する。

## 6. Non-blocking Limitations

### 6.1 Surface Heuristic

High-signal ClassificationはSemantic Classifierではなく一般化したSurface Heuristicである。小文字だけの略称、未知Language、初期大文字の固有名詞または複合語の全意味を完全に分類するものではない。一方、本Follow-upの必須条件である通常英語と大文字／Code-like Identifierの分離は成立している。

### 6.2 Context Usability

Documentation Context上限は依然としてBoundedである。複数の大きなChunkを一度に質問した場合、正しくFail closedしても利用者が回答を得られない可能性がある。安全性を弱めて回答を強制せず、実GGUFのManual Evidence後にChunking／Budget／Retrieval調整の要否を判断する。

## 7. Mutation Boundary

ReviewではSource、Config、Model、Accepted Stable Docs、Current、Shared、Public、Phase Indexおよび旧Historyを変更していない。既存Local Web Processの停止、Kill、Restart、Model LoadまたはGenerationも行っていない。

Append-onlyの本Review、Manual Retest HandoffおよびDocumentation Index Snapshotだけを新規追加する。

## 8. Next Gate

ユーザーがMac Localの単一GGUF Model InstanceとBrowserでManual Retestを行う。

判定は次を分離する。

```text
全Subjectの根拠がAssemblyされ、正しいCitationと回答が出る:
  Functional PASS candidate

Context／Subject Coverage不足を明示し、Model回答を作らない:
  Safety PASS／Usability tuning pending

一部根拠だけで残りの正式名称、定義または関係を推測する:
  FAIL／Blocker
```
