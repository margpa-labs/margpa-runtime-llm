# Phase 7 RAG Grounding／Citation UI Final Bounded Rework — Package P7-RW3-C Recovery（Current Evidence Precedence）

```yaml
document_id: phase_7_rag_final_bounded_rework_p7_rw3_c_recovery_20260830130500
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 13:05:00 JST
active_contract: phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_ja_20260830121213.md
package: P7-RW3-C
finding: P7-CODEX-012
```

## 0. Recovery Index Pointer

前Package: [P7-RW3-B Recovery](phase_7_rag_final_bounded_rework_p7_rw3_b_recovery_ja_20260830125500.md)。次Package: [P7-RW3-D Recovery](phase_7_rag_final_bounded_rework_p7_rw3_d_final_recovery_ja_20260830132500.md)。

## 1. Prompt Order（Handoff §8.1）

`_inject_documentation_reference()`は従来、`messages[0]`がSYSTEMなら`(messages[0], reference, *messages[1:])`——SYSTEM直後・全History前へ挿入していた。`ConversationGenerationInput`のValidatorが「最終Messageは必ずUSER Role」を保証することを利用し、新しい`_splice_before_final_user_message()`で「最終Messageの直前」へ挿入するよう変更した。

```text
System
Historical User / Assistant Turns
Current Documentation Reference or Current NO_HIT Notice
Current User Message
```

`TOOL` Roleはそのまま維持した。既存Test 2件（`test_no_hit_splices_a_freshness_notice_and_still_generates`、`test_current_reference_instruction_outweighs_false_prior_assistant_authority`）は旧順序（`messages[1]`）をAssertしていたため、`messages[-2]`／`messages[-1]`基準へ更新した。`tests/integration/documentation_rag/test_conversation_rag.py`の1件も同様に更新した。History 0件（単発Turn）のTestは位置が偶然一致するため変更不要だった。

## 2. Current Authority Instruction（Handoff §8.2）

`bounded_context_assembler.py`の`REFERENCE_INSTRUCTION`（複数の既存Testが厳密なToken／Character Budgetを較正している共有定数）へは一切触れず、`conversation_generation.py`内だけで完結する新しい独立Instruction `CURRENT_EVIDENCE_AUTHORITY_INSTRUCTION` を、Splice時に`reference_message`の前へ付加する形で実装した（P7-RW2-Bの`NO_HIT_FRESHNESS_INSTRUCTION`と同じ、既に確立済みのPattern）。

```text
このReferenceは今回TurnのCurrent Corpus Snapshotである。
過去のAssistant回答と矛盾する場合、このReferenceを優先する。
このReferenceにない過去のCode・値を再利用しない。
回答内の固有Code／IdentifierはこのReferenceに実在するものだけを使う。
```

`test_context_usage_breakdown_separates_rag_reference_from_system_prompt`が、この追加によりReference Messageの文字数が増えたことでFake `TokenUsage`の桁が不足し破綻したため、Test内のArbitrary Fake値（実Message長と無関係な固定値）を500→2000へ引き上げた——実Token Budgetを較正するTestではないため、Handoff §7.2の「Tight Budget Test」保護対象には該当しない。

## 3. Output Consistency Boundary（Handoff §8.3）

Judge Modeに依存しない、既存Buffering基盤（ENFORCE Modeが既に使っている`emit_deltas=False`＋`_terminal_events`の一括Delivery）を再利用したBounded Consistency Checkを実装した。

```text
_grounded_rag_turn(): augmentation.reference_message is not None
  （Schema Validatorにより、これは厳密にGROUNDED_READYと等価）。

_unsupported_candidate_identifiers(candidate_text):
  Code形状Identifier（`[A-Za-z][A-Za-z0-9]*[-_][A-Za-z0-9]*[0-9]...`、
  `CEDAR-9847`型の汎用Pattern、Project固有Allowlistではない）をCandidate
  から抽出し、Current Evidence Text（_context_source_itemsの生Content、
  REFERENCE_INSTRUCTION等のBoilerplateを含まない）に存在しないものを
  返す。

_finalize_grounded_presentation(result):
  1件でも見つかれば、finish_reason等は保持したままfinal_content／
  display_contentだけをSafe Grounding Failure文言へ置換する。
```

Grounded RAG Turnは`_events_without_summary()`で`emit_deltas`を強制的に`False`とし（Judge Mode Enforceと同じBuffering）、Streaming済み誤答の後から撤回は発生しない。`_terminal_events()`へ`force_bulk_emit`引数を追加し、Grounded RAG Turnでは（Enforce Modeと独立に）置換後のContentを一括Deliverする。Summary Mode側の2箇所（`_events_with_summary`／`_summary_fallback_events`）にも同じ`_finalize_grounded_presentation()`を適用した（Summary Modeは元々両Stageとも`emit_deltas=False`固定のため、追加のBuffering変更は不要）。

RAG OFF・通常NO_HIT・通常General Chat Streamingはいずれも`_grounded_rag_turn()`がFalseのため、`emit_deltas`計算は従来と Byte-identicalのままである。

## 4. Regression

```text
tests/unit/conversation/test_conversation_generation.py:
  test_grounded_candidate_naming_an_unsupported_code_identifier_is_withheld
    -> 不整合Candidate（CEDAR-9847）がLive Deltaへ一切流れず、
       置換後の1件だけがBulk Deliverされることを確認。
  test_grounded_candidate_using_only_evidence_identifiers_is_presented_unchanged
    -> Evidence内のCode（CEDAR-25123）だけを使う正当な回答は
       無変更のまま提示されることを確認（False Positive防止）。

tests/integration/documentation_rag/test_local_corpus_end_to_end.py:
  test_nazuna_probe_orion_candidate_presentation_regression
    -> Handoff §8.4の4手順を、実際のConversationGenerationServiceを
       通した最終Candidate Presentationとして検証（詳細はP7-RW3-D
       Recovery参照）。
```

## 5. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation:
  Backend: conversation_generation.py（Source）、
    test_conversation_generation.py（Test、1新規Fixture＋2新規Test）
  Test: test_conversation_rag.py（既存Assertion更新のみ）
Root外Read/Write: 0
```

Exact next action: P7-RW3-D（Verification／Internal Review／Return）へ連結して進む。
