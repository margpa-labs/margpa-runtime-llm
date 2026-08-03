# 設計統括者Review：Phase 1-ex Mac限定簡易Documentation RAG Multi-turn Grounding Follow-up

```yaml
document_id: designer_review_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up
phase: phase_1_ex
status: changes_required_re_review_no_go
language: ja
created_at: 2026-08-01 00:36:25 JST
owner: 設計統括者役
source_index: ../documentation_index_20260731231940.md
source_handoff: implementer_handoff_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260731231940.md
reviewed_status: implementer_status_phase_1_ex_mac_local_documentation_rag_multi_turn_grounding_follow_up_20260801001058.md
manual_acceptance_gate: no_go
```

## 1. Decision

実装担当Status、変更Source、Test、SHA-512、Full SuiteおよびStatic Checkを独立に確認した。

```text
F8 Exact Chat Prompt Token Counter:
  ACCEPTED

F9 Retrieval Hit／No Block Fail-closed:
  ACCEPTED FOR ZERO-BLOCK CASE

F10 Multi-identifier Coverage:
  PARTIAL／REJECTED

F11 Grounding Instruction:
  ACCEPTED AS PROMPT COMPOSITION BOUNDARY

F12 UI／Evidence State Separation:
  ACCEPTED FOR EXISTING STATES

Overall Follow-up:
  CHANGES_REQUIRED

Manual GGUF／Browser Retest:
  NO_GO
```

Automated SuiteがGreenであることは確認したが、1回目手動Testで発見した複数Subject混同を防ぐには、Coverageの意味と実際のPrompt内容が一致していない。現在の差分を最終Acceptedとはしない。

## 2. Accepted Portions

### 2.1 F8 Exact Base Prompt Measurement

- `ChatPromptTokenCounterPort`は狭いOptional Capabilityとして追加されている。
- llama.cpp AdapterはLoad済みModelの`format_prompt(messages, thinking_mode).token_count`を使用する。
- Inference ServiceおよびComposition Rootを経由し、二重Model Loadを行わない。
- ConversationはUTF-8 Byte数をExact Token数として扱わない。
- Exact Counterが利用できない場合は`documentation_prompt_measurement_unavailable`で停止する。

### 2.2 F9 Zero-block Fail-closed

```text
retrieval.selected > 0
assembled blocks == 0
```

では`should_generate=false`となり、Conversation LayerはModelを呼び出さずSafe Errorを返す。True No Hitとの状態分離も成立している。

### 2.3 F11 Grounding Instruction

現在のReferenceをProject固有事実の根拠とし、過去Assistant回答をAuthorityとせず、未記載の略称展開またはSystem間関係を創作しないInstructionがSystem-owned Referenceへ追加されている。

これはPrompt Composition境界のAcceptedであり、4B Modelが必ず従うことまたは回答内容の正しさを保証するAcceptanceではない。

### 2.4 F12 Existing State Separation

No Hit、Context不足、Docs Missing／Unavailable、Prompt Measurement FailureおよびAccess Profile Denialの既存境界は分離されている。Context不足では通常回答を表示しない。

## 3. Blocking Finding F13：Retrieval CoverageとAssembled Coverageの混同

```text
severity: blocking
affected: F10, F11, Evidence Integrity, Manual Acceptance
```

### 3.1 Cause

RetrieverはSubjectごとの候補を選び、`covered_subject_count`を返す。

Context AssemblerはBudgetに入らないChunkを除外できるが、どのSubjectが実際のReference Blockへ入ったかを返さない。

Application Serviceは次を別々のSourceから組み立てている。

```text
assembled_block_count:
  actual Context Blocks

covered_subject_count／uncovered_subject_count:
  pre-assembly Retrieval Result

generation_allowed:
  true when at least one Block exists
```

したがって、RetrieverがEASA、DLAGSA、OCILNSを3／3 Coverageしても、BudgetによりEASAだけがPromptへ入った状態を`covered=3／uncovered=0／grounded_ready／generation_allowed=true`として扱える。

### 3.2 Independent Reproduction

Project固有語をProductionへ追加せず、既存Test Helperと3件のCanonical Definition Fixtureを使って再現した。

```text
Query:
  EASAとは何ですか？ DLAGSAとは何ですか？ OCILNSとは何ですか？

Retriever:
  identifier subjects = 3
  covered = 3
  uncovered = 0
  selected = EASA, DLAGSA, OCILNS

Bounded Assembly:
  limit = 768
  assembled blocks = 1
  actual heading = EASA only
```

Current Application LogicではBlockが1件あるためGeneration Allowedとなり得る。一方、EvidenceはPre-assemblyの3／3 Coverageを保持する。

### 3.3 Impact

ModelへDLAGSA／OCILNSの根拠が渡っていないのに、System側は全SubjectをCoverageしたように扱う。これは1回目手動Testで観測した「一部の根拠だけを使い、残りの正式名称・定義・関係を推測する」Failureを再発させる。

Citationが実Blockだけに限定されていても、Coverage EvidenceとGrounding Decisionが不正確であるためBlockerとする。

## 4. Blocking Finding F14：通常の英語文章をHigh-signal Identifierとして扱う

```text
severity: blocking
affected: F10, English Input, Coverage Capacity, Evidence Integrity
```

### 4.1 Cause

`identifier_subject_tokens()`はNFKC／Case Fold後の全Latin TokenをSubjectとして返す。

このため次の英語Queryでは、略称3件だけでなく通常語もSubjectになる。

```text
Query:
  What are EASA, DLAGSA, and OCILNS?

Current Subjects:
  what, are, easa, dlagsa, and, ocilns

identifier_subject_count:
  6
```

これは「Distinct High-signal Identifier」のContractではない。

### 4.2 Independent Reproduction

`What`、`Are`および`And`という一般見出しをNoise Corpusへ加え、`top_k=4`で再現した。

```text
Selected:
  What
  Are
  EASA
  DLAGSA

Missing:
  OCILNS

Coverage Metadata:
  subjects = 6
  covered = 4
  uncovered = 2
```

一般英単語がCoverage Slotを消費し、実際のProject Identifierが脱落する。

### 4.3 Impact

Web UIは英語入力および英語回答を許可しており、Accepted ArchitectureもEnglish／Identifier Tokenを対象とする。日本語FixtureだけがGreenでもGeneric High-signal Identifier要件は満たさない。

Project固有略称Allowlistを追加するのではなく、Original Surface、Token形状、Exact Heading／Path Evidenceその他の一般則で通常文章とIdentifier Subjectを分離する必要がある。

## 5. Verification

### 5.1 Implementer Artifact Integrity

Statusに記載された変更Source／Test 21件のAfter SHA-512を現在Fileと照合した。

```text
21／21:
  MATCH

Implementer Status SHA-512:
  a3baed6f64a4e74bbcffd11af43dc4d11f954ccb25f2a176ed6f8313b940188f99a82c6d7bb5848e6aace04c10bae6477975f7720539031ac9aad5539e97fe85
```

### 5.2 Independent Automated Verification

```text
Repository Full Suite:
  400 passed
  3 deselected
  51.84s

Ruff Check:
  PASS

Ruff Format:
  PASS／120 files

Mypy:
  PASS／120 source files

JavaScript Syntax:
  PASS
```

### 5.3 Mutation Boundary

ReviewではSource、Config、Model、Accepted Stable Docs、Current、Shared、Public、Phase Index、Lightningおよび既存Historyを変更していない。既存Local Web Processの停止、Kill、Restartまたは二重Model Loadも行っていない。

## 6. Required Follow-up

1. High-signal Identifier Subjectを通常のLatin文章から一般則で分離する。
2. Subject CoverageをRetriever Selectionだけでなく、実際にPromptへ入ったReference Block単位で再計算する。
3. 必須Subjectを一部しか組み立てられない場合、全Coverage済みとせずFail closedまたは明示的なPartial Coverage Contractにする。
4. Grounding Decision、CitationおよびCoverage Evidenceを同じAssembled Reference Setから導出する。
5. 日本語と英語のMulti-subject Noise Fixture、Partial Assembly FixtureおよびModel Call 0回を追加する。

## 7. Next Gate

実装担当役がCoverage Integrity Follow-upを実装し、新しいAppend-only Statusを提出する。

設計統括者役が再ReviewしてGOとするまで、ユーザーによる実GGUF／Browser Manual Acceptanceは再開しない。
