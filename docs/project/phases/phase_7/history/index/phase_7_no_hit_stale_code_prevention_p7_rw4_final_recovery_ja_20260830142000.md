# Phase 7 削除後NO_HIT Stale Code防止・最小Rework — Package P7-RW4 Final Recovery

```yaml
document_id: phase_7_no_hit_stale_code_prevention_p7_rw4_final_recovery_20260830142000
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 14:20:00 JST
active_contract: docs/project/phases/phase_7/history/operations/phase_7_codex_controller_p7_rw3_rag_grounding_citation_ui_independent_review_ja_20260830132855.md
active_contract_sha512: b479ed17ac3e6d05d75ebd689c1422d811001fe1d90384aed5fcade2a732e40e115210e51d89427befe1d1d4b2da3ebf7880e28c8a5805c28dff09e38fd27d73
package: P7-RW4
finding: P7-CODEX-013（残り1経路、Controller Review §3.3 PARTIAL_REWORK_REQUIRED）
internal_review_cycle: 1
```

## 0. Recovery Index Pointer

前Package: [P7-RW3-D Recovery](phase_7_rag_final_bounded_rework_p7_rw3_d_final_recovery_ja_20260830132500.md)。本Packageの成果物: [Exact Return Handoff](../../handoffs/phase_7_claude_no_hit_stale_code_prevention_bounded_rework_exact_return_handoff_ja_20260830143000.md)。

## 1. Digest照合

Controller Review（正本）の実File SHA-512を`shasum -a 512`で照合し、上記`active_contract_sha512`と一致を確認した。

## 2. Controller指摘の再確認

Controller Review §3.3が特定した未成立契約:

```text
Local Document削除後:
  同一Chat／新規Chatとも、旧CodeをCurrent Factとして提示しない。
  Current Citationは0。
  Modelが過去Historyから旧Codeを返しても決定論的に止める。
```

既存Integration Testが削除後のScripted Inferenceへ最初から安全な文面`現在のCorpusには根拠が見当たりません。`を返させており、`CEDAR-9847`型の失敗値を注入していなかったため、防御を実際には証明していなかった（Controller §3.3の指摘通り）。

## 3. Root Cause

P7-RW3-Cの Output Consistency Boundary（`_finalize_grounded_presentation()`）は`_grounded_rag_turn()`（`GROUNDED_READY`、すなわち`reference_message is not None`）の場合にのみ適用されていた。P7-RW3-BのDeterministic Identifier NO_HIT Denial（`_identifier_no_hit_denied()`）は`identifier_subject_count > 0`の場合にのみInference Call前に発動する。

`Nazuna Probe Orion`のような複合固有名詞は、既存Analyzer上で個々の語が高Signalにならないため`identifier_subject_count == 0`となり、Document削除後のNO_HIT Turnは上記どちらの既存Gateにも該当しないまま実Inference Callへ進んでいた。この経路にだけ、Consistency Boundaryが及んでいなかった。

## 4. Fix（最小差分）

`src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py`のみを変更した。

```text
1. 新規メソッド `_no_hit_rag_turn()` を追加。
   augmentation.evidence.grounding_state is DocumentationGroundingState.NO_HIT
   のみを判定する（新しいSubject／Identifier検出Heuristicは一切追加しない）。

2. `_finalize_grounded_presentation()` の適用条件を
   `not self._grounded_rag_turn()` から
   `not (self._grounded_rag_turn() or self._no_hit_rag_turn())`
   へ拡張した。判定本体（`_unsupported_candidate_identifiers()`、
   `_CODE_IDENTIFIER_PATTERN`、Safe Grounding Failureへの置換）は
   一切変更していない。

3. `_events_without_summary()` の Buffering 判定変数を
   `grounded_rag_turn` から `buffered_rag_turn =
   self._grounded_rag_turn() or self._no_hit_rag_turn()` へ拡張し、
   `emit_deltas` と `_terminal_events(force_bulk_emit=...)` の両方へ
   適用した。Summary Mode側（`_events_with_summary`／
   `_summary_fallback_events`）は元々常時Bufferedのため無変更。
```

### なぜ安全に機能するか

NO_HIT状態では`augmentation.reference_blocks`と`augmentation.reference_message`がいずれも空（Contracts側の既存Schema Invariantが保証）であるため、`_grounded_evidence_text()`は空文字列を返す。既存の`_unsupported_candidate_identifiers()`はCandidate内のCode形状Identifierのうち「Evidence Textに含まれないもの」を返すので、NO_HIT時はCandidate内のCode形状Identifierが1件でもあれば必ず検出される——新しい判定式を1件も追加せず、既存の仕組みがNO_HIT状態でも正しく機能する。

### Scope遵守の確認

```text
Title-Case Run Heuristic: 再導入していない（Subject／Identifier検出には
  一切触れていない。判定はCandidate内のCode形状Identifierのみ）。
固有名Allowlist: 追加していない。
`Nazuna Probe Orion`のHard-code: 行っていない（Fixtureのテスト文言のみ）。
一般的な意味解析基盤: 新設していない。
P7-CODEX-011（Citation UI／Field順）: frontend/への変更は本Package内で0件。
P7-CODEX-012（Current Reference）: `_splice_before_final_user_message()`・
  `CURRENT_EVIDENCE_AUTHORITY_INSTRUCTION`は無変更。
Auto-Resume: `persistent_conversation_service.py`／`ChatListItem.tsx`は
  本Package開始時点から一切Read/Editしていない。
```

## 5. 必須Regression Test

`tests/integration/documentation_rag/test_local_corpus_end_to_end.py`へ新規追加した
`test_deleted_local_corpus_document_denies_a_stale_code_from_conversation_history_regression`が、
Handoffが要求した10項目を1Testとして検証する。

```text
1. Local DocumentへCEDAR-25123を登録                        -> 実施
2. 同じChatの過去Assistant回答へCEDAR-9847を保持              -> 実施
3. Local Documentを削除                                      -> 実施
4. Scripted Inferenceが明示的にCEDAR-9847を返す               -> 実施
   （Controllerが指摘した「最初から安全な文面を返す」旧パターンを
   採用していない——ここが本Testの核心）
5. 最終表示へCEDAR-9847が一切出ない                           -> assert確認
6. Citationが0件                                              -> assert確認
7. 固定の「現在のCorpusに根拠なし」へ収束                      -> Warning
   Code `grounding_consistency_safe_fallback`で確認
8. 新規ChatでもScripted InferenceにCEDAR-9847を返させ、
   同じ結果になる                                              -> assert確認
9. 過去Turn／Citation／Digest不変                              -> History
   Tupleの内容が書き換わっていないことを確認
10. RAG OFFでは既存挙動とStreamingを維持                       -> DELTA
   件数>=1・内容にCEDAR-9847がそのまま含まれることを確認
```

Unit Test（`tests/unit/conversation/test_conversation_generation.py`）を2件追加し、`ConversationGenerationService`単体でも同じ機構を検証した。

```text
test_no_hit_candidate_naming_a_code_shaped_identifier_is_withheld:
  実Inference Callが発生した（NO_HIT Denial Pre-Inference Gateとは別経路
  であることを明示）上で、Candidateが一切Streamingされず（Delta 1件、
  置換後の固定文言のみ）、Citation 0件であることを確認。
test_no_hit_candidate_without_a_code_shaped_identifier_is_presented_unchanged:
  Code形状Identifierを含まない通常のNO_HIT雑談回答がFalse Positiveなく
  無変更のまま提示されることを確認。
```

## 6. 検証順（Handoff指定）

```text
1. Exact Regression Test（上記5.）:
   uv run pytest -q tests/integration/documentation_rag/test_local_corpus_end_to_end.py -k denies_a_stale_code
   -> 1 passed
2. 関連Conversation／Local Corpus Focused Test:
   uv run pytest -q tests/unit/conversation/test_conversation_generation.py
     tests/integration/documentation_rag/test_local_corpus_end_to_end.py
     tests/integration/documentation_rag/test_conversation_rag.py
     tests/unit/documentation_rag/test_lexical_retrieval.py
   -> 87 passed
3. Backend Canonical（1回）:
   uv run pytest -q                     -> 1944 passed, 7 deselected
   uv run mypy                          -> Success, no issues found in 526 source files
   uv run ruff check .                  -> All checks passed
   uv run ruff format --check .         -> 526 files already formatted
4. Frontend Source変更: 0件のため、Frontend再検証は実施していない
   （`git status`でfrontend/への本Package由来の変更が0件であることを
   確認済み）。
5. 該当なし（4.によりFrontend確認自体が不要）。
```

P7-RW3-D基準（Backend 1941 passed）から、Backend +3（Integration Test 1件＋Unit Test 2件）。全件Regression 0。

## 7. Internal Review（1 Cycle）

```text
観点1: Controller指摘の実際の解消
  新規Regression TestはController §3.3が明示した「Scripted Inferenceへ
  最初から安全な文面を返させていた」問題を直接是正し、CEDAR-9847という
  失敗値を明示的に注入した上でCitation 0・非表示・固定Presentationへの
  収束を実証した。
  -> 懸念なし。

観点2: 既存Gateとの重複／競合
  `_identifier_no_hit_denied()`（Pre-Inference、identifier_subject_
  count>0のみ）と`_no_hit_rag_turn()`経由の新しいPost-Candidate Check
  （NO_HIT全般）は排他ではなく補完関係——前者が発動した場合は`events()`
  内で早期returnするため`_events_without_summary()`自体に到達せず、
  後者はそれ以外のNO_HIT（identifier_subject_count==0、複合固有名詞
  含む）だけをCandidate生成後に検査する。二重発動や競合はない。
  -> 懸念なし。

観点3: GROUNDED_READYとの排他性
  `grounding_state`はDocumentationEvidenceの単一Enum値であり、
  `reference_message`はGROUNDED_READYのみで非Noneになる既存Schema
  Invariant（P7-RW3-C Recoveryで確認済み）。`_grounded_rag_turn()`と
  `_no_hit_rag_turn()`が同時にTrueになることはない。
  -> 懸念なし。

観点4: 過去Evidence不変性
  本Fixは`ConversationGenerationSession`内のephemeralな判定のみを追加
  しており、Persisted Citation／Turn／Session Recordを書き換える経路を
  一切追加していない（P7-RW3-Cと同一クラスの変更）。新規Regression
  Testは`same_chat_history`（Python Tuple）の内容が最後まで不変で
  あることを直接assertする。
  -> 懸念なし。

観点5: RAG OFF／一般Chat Streaming不変
  `_no_hit_rag_turn()`は`self._documentation_augmentation`がNoneの
  Turn（RAG OFF）では常にFalseを返す。新規Regression Testの手順10で
  RAG OFF TurnがDelta 1件以上・無変更のCandidateで即時提示される
  ことを直接確認した。
  -> 懸念なし。

観点6: Scope／Claim／Auto-Resume整合
  §4「Scope遵守の確認」に記載の通り、Citation UI・Current Reference・
  Auto-Resumeのいずれのファイルにも触れていない。Node追加Install・
  Network・Git・Backup・Roadmap・Phase 7 Closure・Phase 8・User
  runtime_data/のいずれのActionも発生していない。
  -> 懸念なし。
```

### 7.1 検出したFinding

Critical: 0件。Major: 0件。MVP Blocker: 0件。Minor: 1件（新規発生ではなく、既存の開示済み境界の延長）。

```yaml
finding_id: P7-RW4-IR-001
severity: minor_observation
note: 本Rework が閉じるのは「Candidate内のCode形状Identifier
  （`CEDAR-9847`型、digit＋separator形状）」に限る。Model が Code形状
  ではない平易な事実文（例:「検証は合格でした」のような、数字・区切り
  文字を含まない stale な言明）をConversation Historyから再利用した
  場合、本Gateは対象外のまま残る。Handoff自体が要求した契約は
  「CEDAR-9847型のCode-shaped Identifier」に明示的に限定されており、
  この境界はP7-RW3-IR-001／P7-RW2-IR-001と同一系統の、既に開示済みの
  Scope境界の延長である。
disposition: known_deferred_non_blocking（Handoff §Required Behaviorの
  明示スコープ内であり、本Rework内でのRework対象ではない）
```

## 8. Rework Cycle

不要（Critical／Major／MVP Blocker 0件のため）。Minor Observationは既存の開示済み境界の延長として記録するに留める。

## 9. Action Inventory

```text
Git Action: 0
Network Action: 0（Node追加Install・再Downloadは行っていない、既存の
  `uv run`ツールチェーンのみ使用）
Provider Memory Action: 0
Root外Read/Write: 0
Source Mutation:
  src/margpa_runtime_llm/modules/conversation/application/
    conversation_generation.py（`_no_hit_rag_turn()`追加、
    `_finalize_grounded_presentation()`適用条件拡張、
    `_events_without_summary()`のBuffering条件拡張の3箇所のみ）
Test Mutation:
  tests/unit/conversation/test_conversation_generation.py
    （新規Test 2件追加）
  tests/integration/documentation_rag/test_local_corpus_end_to_end.py
    （新規Test 1件追加）
Frontend Mutation: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: Exact Return Handoff作成後、Codex Controller Bounded Independent Review待ちで停止する。
