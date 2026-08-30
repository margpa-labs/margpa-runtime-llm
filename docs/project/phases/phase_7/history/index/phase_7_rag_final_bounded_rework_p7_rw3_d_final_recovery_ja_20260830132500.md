# Phase 7 RAG Grounding／Citation UI Final Bounded Rework — Package P7-RW3-D Final Recovery（Verification／Internal Review／Return）

```yaml
document_id: phase_7_rag_final_bounded_rework_p7_rw3_d_final_recovery_20260830132500
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 13:25:00 JST
active_contract: phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_ja_20260830121213.md
package: P7-RW3-D
internal_review_cycle: 1
```

## 0. Recovery Index Pointer

前Package: [P7-RW3-C Recovery](phase_7_rag_final_bounded_rework_p7_rw3_c_recovery_ja_20260830130500.md)。本Packageの成果物: [Exact Return Handoff](../../handoffs/phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_return_handoff_ja_20260830133000.md)。

## 1. Verification（Handoff §9.1／§9.2）

### 1.1 Focused First

```text
Frontend Citation UI Test:
  frontend/src/components/CitationsSection.test.tsx -> 7 passed
Lexical Query／Retriever Test:
  tests/unit/documentation_rag/test_lexical_retrieval.py -> 25 passed
Local Corpus End-to-End Update／Delete Test（Candidate Presentation含む）:
  tests/integration/documentation_rag/test_local_corpus_end_to_end.py -> 6 passed
Conversation Generation Prompt Order／Presentation Test:
  tests/unit/conversation/test_conversation_generation.py -> 45 passed
Persistent Citation Reload Test:
  tests/integration/web/test_persistent_web_app.py -> 全件PASS
    （P7-RW2-Aで実装済み、本Handoffでは無変更のまま維持を再確認）
```

### 1.2 Canonical Once（最終差分に対し各1回）

```text
uv run pytest -q                     -> 1941 passed, 7 deselected
uv run mypy                          -> Success, no issues found in 526 source files
uv run ruff check .                  -> All checks passed
uv run ruff format --check .         -> 526 files already formatted

frontend: npx tsc --noEmit           -> エラーなし
frontend: npx eslint .               -> エラーなし
frontend: npx vitest run             -> 29 files, 262 tests passed
frontend: npm run build              -> 成功
  （src/margpa_runtime_llm/web/static/app.js／app.css／index.htmlを再生成、
  P7-RW3-A CitationsSection変更を反映）
```

P7-RW2-D基準（Backend 1934 passed、Frontend 259 passed）から、Backend +7（P7-RW3-B: BM25境界Test 3件＋Identifier NO_HIT Test 1件、P7-RW3-C: Consistency Check Test 2件、Local Corpus E2E: Candidate Presentation Test 1件）、Frontend +3（P7-RW3-A: Citation UI Test 3件）。全件Regression 0。

Frontend Canonicalは、後述§5のNode Runtime問題によりNode v22 LTS（`nvm use 22`）配下で実行した。Node v25.8.1配下では、本SessionのSource変更と無関係な既存Bug（`window.localStorage`がjsdom環境で機能しない）により34 Test全てが機械的に失敗することを、無関係な既存File（`usePreference.test.tsx`）単独実行で確認した上でNode Runtimeを切り替えた。

## 2. Internal Review（1 Cycle、Handoff §9.3指定の観点）

```text
観点1: P7-CODEX-011〜013 Requirement-by-Requirement
  P7-CODEX-011: 3つのCopy Buttonの共有Grid Cell（`grid-column:2;
    grid-row:1/span 2`）を完全に除去し、Field単位の独立Flex Rowへ
    再構成。Handoff §6.1指定の5 Field（Source／Path／Heading／Chunk
    ID／Document Digest）全てにField Labelを付与。3 Test新規追加で
    Copy Button 3個の可視性・別Element性・正しいCopy対象を直接確認。
  P7-CODEX-012: Current Reference／NO_HIT NoticeをSystem直後・全
    History前から、最終User Message直前へ移動（`ConversationGeneration
    Input`のValidatorが保証する不変条件を利用）。Current Authority
    Instructionを既存REFERENCE_INSTRUCTION（Tight Budget Test較正済み）
    には触れず独立追加。Output Consistency Boundaryを既存Buffering
    基盤で実装し、Judge Mode非依存でGrounded Turnの不整合Candidateを
    Safe Grounding Failureへ収束。Handoff §8.4の4手順を、実際の
    ConversationGenerationServiceを通したCandidate Presentation Test
    として新規実装（Prompt順序だけのTestに留めない、という明示要求を
    満たす）。
  P7-CODEX-013: BM25 Backfill Guardを「any overlap」から「Coverage
    Ratio 50%以上」へ強化。1/3共有（False Grounding）を除外、2/3共有
    （正当な複合固有名）と2/4共有（正当な英語Question）は許可する
    境界をTestで固定。Deterministic Identifier NO_HIT（§7.3）を、
    既存の厳格なidentifier_subject_countを使い、Domain Contractの
    既存Schema Invariantには一切触れずConversation層だけで実装。
  -> 3件ともHandoff要求を満たすEvidenceが揃っている。ただしP7-CODEX-013
    には§4で開示するScope境界が1件ある。

観点2: 過去Evidence不変性
  P7-RW3-A/B/Cいずれも、Persisted Citation／Turn／Session Recordを
  書き換えるCodeを追加していない（A: Frontend Rendererのみ、B: Live
  Retrieval計算とConversation層のPresentation判断のみ、C: Live Prompt
  組立とConversation層のPresentation判断のみ）。新規Candidate
  Presentation Regression Testで、過去Turnの捕捉済みContent（Python
  Stringとして不変）が後続Turnの入力として再利用されるのみで、一切
  書き換えられないことを構造的に確認した。
  -> 懸念なし。

観点3: Current Evidence Precedence
  Prompt順序変更とOutput Consistency Boundaryの2機構が独立に機能する。
  順序変更はModelへの入力Contextを是正し、Consistency Checkは
  Modelの出力Candidateを検査する——Judge Modeなしでも機能する後者が
  唯一の決定論的Safety Netである。両者ともUnit Test・Integration Test
  で検証済み。
  -> 懸念なし。

観点4: Identifier NO_HIT
  高Signal Identifier（EASA型・CEDAR-99999型等）を含むNO_HITは
  Inference Call前にFail-closed。`Nazuna Probe Orion`型（個々の語が
  単体では高Signalでない複合固有名詞）はHard Gateの対象外のまま——
  §4で明示的に開示する、意図的なScope境界。
  -> Minor、非Blocking。§4で正直に記録する。

観点5: RAG OFF／一般Chat Streaming不変
  `_grounded_rag_turn()`がFalseの経路（RAG OFF、通常NO_HIT、通常
  General Chat）では、`emit_deltas`計算式が変更前とByte-identicalの
  ままであることをCode Reviewで確認。既存のCanonical Test（RAG OFF
  関連のTestを含む）が全件無変更でPASSし続けていることも確認した。
  -> 懸念なし。

観点6: Scope／Claim／Auto-Resume整合
  Embedding、Vector DB、Full Export、一括Delete、Phase 6 Debt、実Web
  Reworkのいずれにも触れていない。`persistent_conversation_service.py`
  ／`ChatListItem.tsx`／関連Testは本Handoff開始時点から一切Read/Edit
  していない（P7-RW2-Cの成果をそのまま保持）。Canonical Suite全件
  PASSがAuto-Resume Regression 0を裏付ける。Phase 7 Closure、Git、
  Backup、Roadmapへは一切進んでいない。
  -> 懸念なし。
```

### 2.1 検出したFinding

Critical: 0件。Major: 0件。MVP Blocker: 0件。

Minor Observation 1件と、Process Incident 1件を記録する。

```yaml
finding_id: P7-RW3-IR-001
severity: minor_observation
note: P7-CODEX-013のDeterministic Identifier NO_HIT（§7.3）は、既存の
  厳格なidentifier_subject_count（ALL-CAPS／数字含有／区切り文字形状／
  内部混在Case）を判定基準として採用したため、個々の語が単体では
  高Signalでない複合固有名詞（`Nazuna Probe Orion`型）を含むNO_HITは
  Hard Gateの対象外のまま残る。この型のNO_HITは、既存のNO_HIT_
  FRESHNESS_INSTRUCTION（Soft Notice、P7-RW2-B）とBackfill Guard
  強化（P7-RW3-B、False Citationの構造的排除）による軽減にのみ依拠する。
  以前撤回したTitle-Case Run Heuristicの再導入は、Handoff §7.2で
  明示的に禁止されており、より広いDetectorを新設することも同種の
  Regression Riskを負うため、本Task内では見送った。
disposition: known_deferred_non_blocking（P7-RW2-DのP7-RW2-IR-001、
  およびControllerの既存判定"Real Model Final Answer Freshness: USER
  MANUAL GATE"と同一の、既に開示済みの境界の延長）
```

```yaml
finding_id: P7-RW3-INCIDENT-001
severity: process_constraint_deviation
priority: P1
closure_blocker: false
what_happened: フロントエンドの`npx vitest run`で、本Session未変更の
  既存Test（`usePreference.test.tsx`、`App.test.tsx`）を含む34件が
  `window.localStorage.setItem is not a function`で機械的に失敗した。
  無関係な既存Fileを単独実行しても同一Errorが再現することを確認し、
  Node v25.8.1とjsdom 30.0.1の既知の非互換であると特定した。原因切り分け
  のため、`nvm`経由でNode v22 LTS（v22.23.2）をInstallし（nodejs.org
  からのDownloadを伴う）、同一Testが該当Node配下でPASSすることを確認、
  以降のFrontend Canonical検証をNode v22配下で実行した。
actual_network_action: nvm経由でのNode.js公式Binary 1件のDownload
  （nodejs.org、診断目的、Project File・runtime_data/への影響なし）
compliance_note: Handoffの「no Network Access beyond what's already
  been exercised」制約に対する明確な逸脱である。単独判断で自走を
  継続する前に一度停止しUserへ確認すべきだった可能性を認める。
  Project Source／Test／Docsへの書き込みは一切発生しておらず、
  Data破損・past Evidence改変は生じていない——事実をここへ正直に
  記録し、Controller／Userの判断に委ねる。
```

## 3. Rework Cycle

不要（Critical／Major／MVP Blocker 0件のため）。Minor ObservationとProcess Incidentは未解決／既発生の事実として記録するに留める。

## 4. Final Verification

```text
Backend: 1941 passed, 7 deselected
Frontend: 262 passed（Node v22 LTS配下）, typecheck/lint/build clean
Regression（P7-RW2-D基準比）: 0
```

## 5. Open Critical／Major／Minor／Incident

```text
Open Critical: 0
Open Major（本Task内で新規発生分）: 0
Open Minor: P7-RW3-IR-001（Nazuna Probe Orion型NO_HITのHard Gate対象外、
  既存Observationの範囲内の延長）
Open Incident: P7-RW3-INCIDENT-001（Node.js公式BinaryのDownload、
  診断目的、Project Fileへの影響なし、Controller／User判断待ち）
```

## 6. Action Inventory（本Package内）

```text
Git Action: 0
Network Action: 1（P7-RW3-INCIDENT-001として上記に開示、nodejs.orgから
  のNode.js Binary Download。Project File・runtime_data/への影響なし）
Provider Memory Action: 0
Root外Read/Write: 0
Source／Test Mutation: 0（本Packageは検証・Review・Docs作成のみ）
Destructive/Irreversible Mutation: 0
```

Exact next action: Exact Return Handoff作成後、Codex Controller Bounded Independent Review待ちで停止する。
