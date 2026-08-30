# Phase 7 Current Claude Task — Package P7-I Final Recovery（Implementation Freeze／Internal Review／Finding Ledger／Final Verification）

```yaml
document_id: phase_7_current_claude_task_p7_i_final_recovery_20260829190939
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 19:09:39 JST
active_contract: phase_7_claude_bounded_mvp_implementation_exact_handoff_ja_20260829172159.md
package: P7-I
internal_review_cycle: 2
```

## 0. Recovery Index Pointer

前Package: [P7-G/H Recovery](phase_7_current_claude_task_p7_gh_recovery_ja_20260829190219.md)。本Packageの成果物: [Exact Return Handoff](../../handoffs/phase_7_claude_bounded_mvp_implementation_exact_return_handoff_ja_20260829191047.md)。

## 1. Implementation Freeze

P7-0からP7-Hまでの全Package実装が完了した時点でのFreeze。以降、本Package（P7-I）ではRequirement-by-Requirement Internal Reviewとそれに伴うReworkのみを行い、新規機能Scopeは追加しない。

## 2. Internal Review Cycle 1 — Requirement-by-Requirement

`phase_7_acceptance_matrix_ja.md`記載の32 Acceptance全件を、実装Source・Test・Evidenceから個別に再導出した（実装当時の記憶ではなく、以下を再読して再確認：Requirements、Architecture、ADR、Acceptance Matrix、全Recovery Index）。

### 2.1 検出したFinding

#### Finding-001（Major、Rework済み）

```yaml
finding_id: P7-IR-001
severity: major
source_requirement: P7-REQ-015, P7-ACC-022
evidence: Architecture §4「Search Providerへ送るQueryとConversation Contextは明示Policyで
  最小化し、Secret／PII候補は送信前に検査する」との既存実装の乖離
affected_path: modules/web_knowledge/application/web_knowledge_service.py
failure_mode: Outbound Search Query（User入力そのまま）に対するSecret様Pattern検査が
  一切実装されておらず、Fetched Content側のPrompt Injection Detectionしか存在しなかった。
root_cause_candidate: P7-E実装時、Inbound（取得Content）側のGovernanceにのみ焦点を当て、
  Outbound（送信Query）側のGovernanceを見落とした。
required_rework: Secret様Pattern検出Moduleを新設し、Search Provider呼出し前にQueryを検査、
  検出時はFail-closedでSearch自体を拒否する。
verification_method: 新規Unit Test（Secret様Pattern11件Positive／4件Negative）＋
  Orchestrator Level Test（検出時にSearch Provider呼出しが0回であることを直接確認）。
disposition: fixed
```

**Rework内容**：`modules/web_knowledge/domain/secret_detector.py`新設（`detect_secret_candidates()`
— API Key／AWS Key／GitHub Token／Private Key Block／`key=value`形式Credential／Bearer
Tokenの高確度Pattern限定、一般PII（Email／電話番号）は誤検出過多になるため対象外と明示）。
`WebFetchFailureReason.SECRET_CANDIDATE_IN_QUERY`追加。`WebKnowledgeService.search_and_fetch()`
のAUTOMATIC Rejectの直後、Search Provider呼出し前に検査を追加。

```text
tests/unit/web_knowledge/test_secret_detector.py ... 11 passed
tests/unit/web_knowledge/test_web_knowledge_service.py::
  test_secret_shaped_query_is_rejected_before_any_provider_call ... passed
```

#### Finding-002（Major、Deferred・明示文書化）

```yaml
finding_id: P7-IR-002
severity: major
source_requirement: Architecture §1 Component Boundary（Web Search Port -> Context
  Injection Boundary -> Main Model）
evidence: 実装ではWeb Search／Fetch結果がConversation Generation（Main Model Context）へ
  一切注入されない。Manual Search Panelで検索・閲覧できるだけの独立Utilityである。
affected_path: modules/conversation/application/conversation_generation.py（変更なし）、
  modules/web_knowledge/（Chat非統合のまま）
failure_mode: Architecture図が示すEnd-to-endのWeb Grounding（Model回答へのWeb根拠自動反映）
  は成立していない。
root_cause_candidate: `conversation_generation.py`（2178行、極めて高いTest密度を持つ既存
  Core）へのN-source化改修は、このTask内で行うにはRegression Riskが大きいと判断し、
  Local Corpusと異なりWeb Searchでは意図的にChat非統合の設計を採った
  （P7-0 Recovery §3、P7-E/F Recovery §1参照）。
required_rework: 本Task内では実施しない（Regression Risk対Resource Costの比較により見送り）。
verification_method: N/A（既知の設計境界として文書化）。
disposition: deferred
```

**判断根拠（Rework不実施の理由）**：Requirements P7-REQ-008は`disabled／manual／automatic`を
明確に分離しており、Architecture全体の"自動Chat統合"はP7-REQ-013の`automatic` Trigger
Heuristicsの責務である。本TaskではAUTOMATICを`NotImplementedError`で明示的に未実装と
宣言しており（P7-E/F Recovery §1で既に開示済み）、`manual`活性化の責務は「Userが明示的に
検索しEvidenceを得られること」（P7-ACC-016で規定）であり、これは成立している。
Chat Context統合（自動的にModel回答へ反映されること）は`automatic`と不可分の機能であり、
本Findingは新規発見ではなく、既存の開示済みScope境界の再確認である。ただし、
Return Handoffで最も目立つ形で明記し、Codex Independent Reviewが「Chat回答がWeb Evidence
を自動的に反映する」という誤解をしないよう徹底する。

### 2.2 Observation（非Blocking、文書化のみ）

```yaml
finding_id: P7-IR-003
severity: observation
source_requirement: P7-ACC-008
note: Embedding Portは本Task全体を通じてHandoff指示通りReserved（未使用）のまま。
  BM25 Baselineのみ稼働しているため「Embedding Identity」Evidence Fieldは存在しない
  （Index／Retriever Identityは`DocumentationEvidence.retriever_key/version`で既存通り
  Evidence化されている）。Handoff「新しいVector Dependencyを必須化しない」という明示指示
  との整合を優先し、Embedding未使用自体はDefect扱いしない。
disposition: not_reproducible（設計通りの意図的Scope、Defectではない）
```

```yaml
finding_id: P7-IR-004
severity: observation
source_requirement: P7-ACC-013/014/015
note: Web CitationのReload／Restart／Branch永続化はN/A——Web Evidence自体がServer側に
  一切永続化されない設計（Data Controls Retention Fact `public_web: retained=False`で
  明示）ため、"永続化されたCitationの復元"という概念がWeb Sourceには存在しない。
  Local Corpus Citationは既存Phase 2機構をそのまま再利用しPASSする。
disposition: not_reproducible（Finding-002と同じScope境界に起因、Defectではない）
```

## 3. Rework Cycle 1

Finding-001のみ実施（上記2.1参照）。Finding-002はDeferred（Rework対象外、理由明記済み）。
Finding-003／004はObservationのためRework不要。

## 4. Internal Review Cycle 2 — 再確認

Rework（Finding-001）が他Governance Path（Prompt Injection Detection、OFF/OBSERVE/ENFORCE
各Mode、URL Security Boundary）を破壊していないことを、`tests/unit/web_knowledge`
全56 Testと、Backend Full Suite（1924 Test）を通じて確認した——新規Regressionなし。

Cross-component Wiring再確認：`WebKnowledgeService.search_and_fetch()`のSecret検査は
`AUTOMATIC` Rejectの直後・Search Provider呼出しの直前に位置し、`DISABLED`／`AUTOMATIC`
Branchより後、既存のSearch Provider呼出しBranchより前——順序を誤ると「Disabled時に
Secret検査が先に走りFailure Reasonが誤表示される」等のBugになり得るため、Source上で
直接確認した（`DISABLED`は最初期Returnのため到達しない、`AUTOMATIC`はRaiseのため到達しない、
の2点をコード上で確認済み）。

## 5. Final Verification

```text
Backend pytest（Full Suite、--basetemp Project内） : 1924 passed, 7 deselected
mypy（Project既定 files=[src,scripts,tests]）        : Success、526 source files
ruff check . / format --check .                       : All checks passed／All formatted
frontend: npm run typecheck                            : Clean
frontend: npm run lint                                 : Clean
frontend: npm test                                      : 256 passed（28 files）
frontend: npm run build                                  : Clean（87ms）
tests/integration/web（全Web App Integration一括）      : 195 passed
```

## 6. Requirement／32 Acceptance 最終Disposition

| ID | Disposition | 根拠 |
|---|---|---|
| P7-ACC-001 | PASS | conversation_generation.py等Core無変更、Full Regression Green |
| P7-ACC-002 | PASS | 既存Phase 2 Gate無変更（RAG OFF時Retrieval Call 0、既存Test） |
| P7-ACC-003 | PASS | Model Validator＋Route Testで機械的に保証 |
| P7-ACC-004 | PASS | Local Corpus登録、Test済み |
| P7-ACC-005 | PASS | Append-only Revision Chain |
| P7-ACC-006 | PASS | Soft-delete、Historical Evidence保持 |
| P7-ACC-007 | PASS | 既存Chunker機構の再利用 |
| P7-ACC-008 | PARTIAL | Index/Retriever Identityのみ（Embedding未使用は設計通り、Finding-003） |
| P7-ACC-009 | PASS | 既存RetrievedChunk構造を再利用 |
| P7-ACC-010 | PASS | 既存Grounding State機構／Web NO_RELEVANT_EVIDENCE |
| P7-ACC-011 | PASS（Local Corpus）／N/A（Web、Finding-002） | |
| P7-ACC-012 | PASS | Local/Web双方でCitation Identity完備 |
| P7-ACC-013 | PASS（Local Corpus）／N/A（Web、Finding-002/004） | |
| P7-ACC-014 | PASS（Local Corpus）／N/A（Web、Finding-002/004） | |
| P7-ACC-015 | PASS（Local Corpus）／N/A（Web、Finding-002/004） | |
| P7-ACC-016 | PASS | Manual Search Port経由実行、Golden Path Test済み |
| P7-ACC-017 | PASS | Snippet／Fetched Content構造的分離 |
| P7-ACC-018 | PASS | Canonical URL/Title/Provider/取得時刻/Digest Evidence化 |
| P7-ACC-019 | PASS | Source Authority Classification（Heuristic、明示） |
| P7-ACC-020 | PASS | 19 Test、実DNS Resolution含め検証 |
| P7-ACC-021 | PASS | httpx.MockTransportで実Semantics検証 |
| P7-ACC-022 | PASS（Rework後） | Finding-001 Fix、Secret Pattern検出 |
| P7-ACC-023 | PASS | Prompt Injection Detection、OFF/OBSERVE/ENFORCE全Mode Test済み |
| P7-ACC-024 | PASS | DOM順序・既存Toggle形式をTestで直接確認 |
| P7-ACC-025 | PASS | Retention Fact（読取専用）とConsent（変更可）を構造分離 |
| P7-ACC-026 | PASS | 既定OFF、Test確認済み |
| P7-ACC-027 | PASS | Test `test_saving_consent_never_claims_training_occurred` |
| P7-ACC-028 | PASS | Web Search request_id相関追加、Failure Reason全Path投影 |
| P7-ACC-029 | PASS | 277＋179件の隔離・全体Regression確認 |
| P7-ACC-030 | PASS | P7-A Recovery Indexに判定根拠記載済み |
| P7-ACC-031 | PASS | 全Canonical Verification Green |
| P7-ACC-032 | NOT RUN（USER GATE） | Real Browser Manual Acceptanceは本TaskのAuthority外 |

集計：PASS 27、PARTIAL 1（P7-ACC-008）、N/A相当（実質PASS範囲内でWeb部分のみ非該当）4件
（P7-ACC-011/013/014/015、いずれもLocal Corpus側はPASS）、NOT RUN 1（P7-ACC-032、User Gate）。

## 7. Open Critical／Major／Minor

```text
Open Critical: 0
Open Major   : 1（Finding-002、Web Search Chat Context非統合。Deferred・理由明記済み。
  Closure Blockerではない——PoC/MVP Operating Policy §5 P0判定基準
  「Phase目的の中心機能が未接続、実行不能または虚偽表示になる」に該当しない。Manual
  Search自体は完全に機能しており、虚偽表示も一切ない。Chat自動統合はRequirements自体が
  `automatic`活性化Tierの責務として明確に分離しており、本Task範囲外として一貫している）。
Open Minor   : Finding-003（Embedding未使用、設計通り）、Finding-004（Web Citation
  永続化N/A、設計通り）。いずれもDefectではなくScope境界の文書化。
```

## 8. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Exact Return Handoff作成後、Codex Controller Bounded Independent Review
待ちで停止する。
