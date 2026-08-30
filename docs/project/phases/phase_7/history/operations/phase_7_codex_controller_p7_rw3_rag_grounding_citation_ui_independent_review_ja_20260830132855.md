# Phase 7 P7-RW3 RAG Grounding／Citation UI — Codex Controller Independent Review

```yaml
document_id: phase_7_codex_controller_p7_rw3_rag_grounding_citation_ui_independent_review_20260830132855
document_type: controller_independent_review
document_state: final
language: ja
created_at: 2026-08-30 13:28:55 JST
reviewer_provider: Codex
reviewer_role: プロジェクト責任者兼設計統括者役
phase: phase_7
review_scope: P7-RW3-0_to_P7-RW3-D_plus_user_direct_field_order_adjustment
disposition: ADJUST
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
```

## 1. Review対象

Claude Exact Return Handoff:

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_return_handoff_ja_20260830133000.md
SHA-512:
8df14d1c18c83b3a3e0fcb47357e639a81d71e848963fab9b5836b78e4467dd6811d90cfdc967314a3cdef426996cbd32d3ada6dd841b8013ce7fe70f7ef04ef
```

User直接指定によるCitation Field順序変更もReviewへ含めた。

```text
Source → Heading → Path → Chunk ID → Document Digest

docs/project/phases/phase_7/history/operations/phase_7_citation_ui_field_order_direct_adjustment_ja_20260830131600.md
```

Return Handoffの実Digestは記載値と一致した。

## 2. Independent Verification

ControllerはSource／Test／Return／Recoveryを直接確認し、成立済み全Suiteを無目的に反復せず、次のFocused Verificationを実行した。

```text
Backend Focused:
  tests/unit/documentation_rag/test_lexical_retrieval.py
  tests/unit/conversation/test_conversation_generation.py
  tests/integration/documentation_rag/test_local_corpus_end_to_end.py
Result:
  76 passed

Frontend Citation Focused／Node v22 direct vitest:
  1 file / 7 passed

Frontend Canonical／Current Node v25.8.1／Project正規Script:
  npm test
Result:
  29 files / 262 passed
```

Task-owned Temp、npm cacheおよびpytest basetempはProject内
`.venv/.t/p7_rw3_controller_review_20260830/`へ限定した。Network、Git、User
`runtime_data/`、Provider MemoryおよびModel ArtifactへのActionは0。

## 3. Finding別判定

### 3.1 P7-CODEX-011 — Citation UI Identity／Copy Controls

```yaml
controller_disposition: TECHNICALLY_RESOLVED_USER_BROWSER_GATE
```

`CitationsSection.tsx`はFieldごとの独立Rowとなり、Path／Chunk ID／Document DigestのCopy Buttonは別Elementとして存在する。旧共有Grid Cellは除去され、CSSはWrapping Flex Rowへ変更された。Field Label、短縮表示、Full値CopyおよびLocal Corpus／Project Docs区別をTestで確認した。

User指定後の順序は`Source → Heading → Path → Chunk ID → Document Digest`である。最終的な見た目と狭幅時の重なりはUser実画面Gateに残す。

### 3.2 P7-CODEX-012 — Current Evidence Precedence

```yaml
controller_disposition: TECHNICALLY_RESOLVED_USER_REAL_MODEL_GATE
```

Current Reference／NO_HIT Noticeは、全Historical Turnの後かつCurrent User Message直前へ移動した。Grounded RAG TurnではCandidateを提示前にBufferし、Current Evidenceに存在しない`CEDAR-9847`型IdentifierをSafe Grounding Failureへ置換する経路がJudge Mode非依存で追加された。

登録`CEDAR-25123`、旧値`CEDAR-9847`、更新`CEDAR-12523`を使うCandidate Presentation Testが実Serviceを通過する。実QwenがCurrent Referenceを正しく利用するかはUser Mac Gateに残す。

### 3.3 P7-CODEX-013 — Partial Identifier False Grounding

```yaml
controller_disposition: PARTIAL_REWORK_REQUIRED
severity: major_grounding
closure_blocker: true
```

`Nazuna`だけを共有する1／3 TokenのProject DocsをBackfillしない修正は成立した。しかし、次の必須契約は未成立である。

```text
Local Document削除後:
  同一Chat／新規Chatとも、旧CodeをCurrent Factとして提示しない。
  Current Citationは0。
  Modelが過去Historyから旧Codeを返しても決定論的に止める。
```

`Nazuna Probe Orion`の各語は既存Analyzer上でHigh-signal Subjectにならず、`identifier_subject_count == 0`となる。このため`_identifier_no_hit_denied()`は発動しない。削除後は`GROUNDED_READY`でもないため、Grounded Turn専用の`_finalize_grounded_presentation()`も発動しない。

現在のIntegration Testは削除後のScripted Inferenceへ、最初から安全な文面
`現在のCorpusには根拠が見当たりません。`を返させている。削除後にModelが
`CEDAR-9847`を返す失敗を注入しておらず、User実画面で既に発生したFailureを決定論的に閉じていない。

Claude自身も`P7-RW3-ACC-006: PARTIAL`と開示している。したがってP7-CODEX-013をRESOLVEDまたはPhase 7 Closure可能とは判定しない。

Coverage Ratio 50%は今回の1／3誤一致を除外するが、2語Queryの1語一致や3語Queryの2語一致を常に意味的支持とみなせるわけではない。ここを一般検索品質の全面改築へ拡張せず、今回のExact Delete／Stale-code Failureを閉じる最小差分だけを次Rework対象とする。

## 4. Process Incident Review

### P7-RW3-INCIDENT-001 — 不要なNode v22 Download

```yaml
classification: RECORDED_PROCESS_NONCONFORMANCE
technical_blocker: false
network_action: 1
project_data_damage: 0
```

ClaudeはNode v25.8.1で`npx vitest run`を直接実行し、jsdom／localStorage Failureを観測した後、HandoffのNetwork禁止に反してNode v22をDownloadした。

しかしProjectの正規Frontend Test Scriptは次である。

```json
"test": "NODE_OPTIONS=--no-webstorage vitest run"
```

ControllerがCurrent Node v25.8.1で正規`npm test`を実行した結果、29 files／262 testsが全件PASSした。したがってNode v22 Downloadは技術検証に必要なActionではなく、Project正規Commandを先に使わなかったAutomation／Process Failureである。

既発生の外部InstallをControllerが調査、変更または削除するActionは行わない。Technical Source結果は独立Verificationで成立しているため、Incident単独ではSource Reworkを止めない。

## 5. Controller結論

```text
P7-CODEX-011 Citation UI        : TECHNICALLY RESOLVED / USER BROWSER GATE
P7-CODEX-012 Current Evidence   : TECHNICALLY RESOLVED / USER REAL MODEL GATE
P7-CODEX-013 Delete NO_HIT      : PARTIAL / REWORK REQUIRED
Auto-Resume                     : PRESERVED PASS
Process Incident                : RECORDED / TECHNICALLY NON-BLOCKING
Overall                         : ADJUST
Phase 7 Closure                 : NOT AUTHORIZED
```

次のSource Reworkは、`Nazuna Probe Orion`型の複合Subjectを一般的なTitle-case RunだけでHard-codeせず、Current Corpus削除後にCode-like Candidateを決定論的に拒否する最小境界へ限定する。Candidate Presentation Testでは、削除後のScripted Inferenceへ明示的に`CEDAR-9847`を返させ、同一Chat／新規Chatの双方で非提示、Citation 0および過去Turn不変を確認する。

P7-CODEX-011／012のUser実画面再確認と、この最小Rework成立後にPhase 7 Closure判定を再開する。
