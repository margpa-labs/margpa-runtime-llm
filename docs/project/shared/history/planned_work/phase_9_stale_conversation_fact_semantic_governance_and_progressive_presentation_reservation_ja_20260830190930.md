---
document_id: phase_9_stale_conversation_fact_semantic_governance_and_progressive_presentation_reservation_20260830190930
document_type: append_only_planned_work_design_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-08-30 19:09:30 JST
decision_authority: user
authority_owner: Nazuna Research
target:
  - phase_9_semantic_governance
  - phase_9_progressive_presentation
implementation_authorized: false
---

# Phase 9 — Stale Conversation Fact Governance／Progressive Presentation予約

## 1. 目的

Phase 7最終Manual Acceptanceで、削除済みLocal Corpusの旧FactがCurrent Retrievalからではなく、
過去Conversation Contextから再出力され得ることを確認した。これをPhase 9のSemantic Governance、
Judge、RepairおよびPresentation研究へ接続する。

## 2. Stale Fact Governance候補

### 2.1 Source Lifecycle

過去TurnのCitation、Source Class、Document ID、Revision、Chunk ID、Digestと、Current Source Registryの
Active／Updated／Deleted Stateを比較可能にする。

### 2.2 Context Authority

Historical Conversationは会話履歴であり、Current Fact Authorityではない。Current User Instruction、
Current Corpus／EvidenceおよびHistorical Assistant ClaimをAuthority／Freshnessの異なる入力として扱う。

### 2.3 Semantic Criterion

Generic Result Envelopeで少なくとも次を表現する。

```text
stale_evidence
source_deleted
source_revision_superseded
current_evidence_contradiction
historical_claim_without_current_support
freshness_unknown
```

### 2.4 Judge／Repair／Rejudge

Current Factを要求する質問でStale Factを検出した場合、再検索、Candidate修正、RejudgeおよびPresentationを
Request IDで相関する。修復不能なら原因別Safe Fallbackへ収束する。

## 3. Mode別境界

### RAG ON

Current Evidenceと直接比較し、削除済み／旧Revision Factを提示しない。NO_HITならStrict NO_HIT候補と
組み合わせられる。

### RAG OFF

すべての過去Factを遮断しない。Citation／Revision／Digestから削除・更新済みSource由来と追跡できるFactを
優先対象とする。通常の会話記憶を壊さず、Freshness-sensitive Questionだけを選択する。

## 4. Strict NO_HIT保留案

`RAG ON＋NO_HIT`でModelを呼ばず、設定言語の固定回答へ収束する方式は引き続き選択可能な保留案とする。
Phase 7 Closure Blockerにはしない。Phase 9で、Model Callあり＋Semantic Enforcementとの品質、Latency、
User ExperienceおよびResearch Valueを比較して採否を決める。

## 5. Progressive Presentation原則

ENFORCE、Judge／Repair、NO_HIT、Buffered Groundingその他、回答を即時確定できない経路でも、原則として
一括表示をDefaultにしない。

```text
開始／取得／生成／検証／修復／確定
```

をBlock単位またはState単位で段階表示する。Citationを先行表示する場合、NO_HIT Citationも消さずに
最終回答へ残す。未検証Candidateを確定回答に見せず、Progress StateとFinal Stateを区別する。

既に表示したTokenを回収できない制約があるため、次を比較する。

- Progressive State＋Final Answer。
- Verification-aware Block Streaming。
- Strict Buffered Presentation。
- Strict NO_HIT Deterministic Presentation。

既定値候補はProgressiveとし、一括表示は明示Modeまたは技術的必要性がある経路だけに限定する。

## 6. Acceptance Candidate

1. 削除済みSource由来のFactをCurrent Factとして断定しない。
2. 更新済みSourceではCurrent Revisionを優先する。
3. 過去Turn／Citation自体を書き換えない。
4. RAG OFFの通常Conversation Memoryを過剰遮断しない。
5. Stale判定、再検索、Repair、Rejudge、Presentationを相関できる。
6. Failure Reasonを回答言語で表示する。
7. 待機中も進行Stateが分かり、最終回答は段階的に提示される。
8. NO_HIT Citationが一瞬で消えない。
9. Strict／Progressiveを比較可能にする。
10. Model品質問題とRetrieval／Governance FailureをEvidence上で分離する。

## 7. Authority

本予約はPhase 9開始、Source Mutation、Model Load、Network、GitまたはPhase 7 Closure Authorityを与えない。

