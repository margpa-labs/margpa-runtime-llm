# Phase 7 RAG Grounding／Citation UI Final Bounded Rework — Package P7-RW3-B Recovery（Identifier False Grounding一回修正）

```yaml
document_id: phase_7_rag_final_bounded_rework_p7_rw3_b_recovery_20260830125500
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-30 12:55:00 JST
active_contract: phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_ja_20260830121213.md
package: P7-RW3-B
finding: P7-CODEX-013
```

## 0. Recovery Index Pointer

前Package: [P7-RW3-A Recovery](phase_7_rag_final_bounded_rework_p7_rw3_a_recovery_ja_20260830123500.md)。次Package: [P7-RW3-C Recovery](phase_7_rag_final_bounded_rework_p7_rw3_c_recovery_ja_20260830130500.md)。

## 1. 実装方式の選定（Handoff §7.2「以前撤回したTitle-Case Run Heuristicをそのまま復活させない」）

### 1.1 Backfill Guard（`bm25_retriever.py`）

P7-RW2-Bの既存Guardは「`identifier_tokens`との重なりが1件以上（any overlap）」だけを要求していた。`Nazuna Probe Orion`（3語）に対し`Nazuna`だけを共有するPhase 1 Docsが、この弱いGuardを通過していた。

「全主要Token」「明示的なCoverage Ratio」のいずれかで判定するというHandoff §7.2の指示に対し、次の理由で**Coverage Ratio（50%以上）**を採用した。

```text
全Token一致（100%必須）を検討したが却下:
  identifier_tokensはQuery中の全Latin/数字TokenをそのままExposeする
  既存の広い定義であり（`what`/`is`等の一般語も含む）、"What is Runtime
  Governance?"のような正当な4-Token Englishの質問で、実在するDocの
  HeadingがCoverするのは"runtime"/"governance"の2/4だけ（"what"/"is"
  はDocの地の文に現れない）。100%必須はこの正当なQueryを壊す。

Coverage Ratio 50%以上（採用）:
  Nazuna Probe Orion（3 Token）で1/3のみ共有するChunkは
  2*1=2 < 3で除外、2/3を共有するChunkは2*2=4>=3で許可。
  ARGD DAGD等の2-Token Compoundでは1/2共有＝旧"any overlap"と同値
  （既存Fixtureへの影響なし）。
  "What is Runtime Governance?"の2/4共有は2*2=4>=4で許可
  （正当なQueryを壊さない）。
```

以前撤回した`identifier_subject_tokens()`（Title-Case Run Heuristic）へは一切触れていない。`subject_identifiers`が担うSUBJECT_COVERAGE_INSUFFICIENT判定（Handoffが直接指定しない、より上位の別の判定Path）には無関係であり、P7-RW2-Bで発生したMaterial Regression（"Runtime Governance"等の正当な複数語Domain語彙が誤ってStrict Subjectとして扱われる）とは異なる、より狭いScopeの修正である。

### 1.2 Deterministic Identifier NO_HIT（Handoff §7.3）

Handoffは2方式を提示していた。

```text
(a) Identifier-specific NO_HITをGeneration Deniedへ分離する。
(b) Inference Call前に固定のPresentationへ収束する。
```

当初(a)を`documentation_rag.py`の`_enabled()`（`should_generate`計算Path）へ実装したが、`DocumentationEvidence`の既存Pydantic Validatorが「NO_HIT状態は`generation_allowed=True`のみを許可する」ことを既にHard-Enforceしている事実に到達した（`contracts.py`: `"no-hit state must allow only ungrounded general generation"`）。これはPhase 6以前から確立された、Persistence／Frontend／SSE Contract全体が依拠する既存Domain Invariantであり、変更すればBlast Radiusが本Bounded Reworkの3件Scopeを大きく超える。

即座に撤回し、(b)「Inference Call前に固定のPresentationへ収束する」を`conversation_generation.py`だけへ実装する方式へ切り替えた（Domain Contract・Persistence Schema・Frontend Typeへは一切触れない）。

```text
_identifier_no_hit_denied(augmentation):
  grounding_state is NO_HIT かつ evidence.identifier_subject_count > 0
  （既存の厳格なSubject Detector、新規Heuristicではない）。

_identifier_no_hit_denied_event(augmentation):
  self._inference.stream()を一度も呼ばず、固定文言を
  そのままCOMPLETED Eventのassistant_message.contentへ収束する。
```

`identifier_subject_count`は「ALL-CAPS Run／数字含有／区切り文字形状／内部混在Case」という既存の厳格なSignal（`subject_identifiers`と同一）を使う。`Nazuna`/`Probe`/`Orion`はいずれも単体では該当しないため、`Nazuna Probe Orion`クエリ自体はこのHard Gateの対象外のまま残る——既存のNO_HIT_FRESHNESS_INSTRUCTION（Soft Notice、P7-RW2-B）による軽減のみを維持する、意図的なScope境界である（§5で詳述）。

## 2. Regression（新規Test）

```text
tests/unit/documentation_rag/test_lexical_retrieval.py:
  test_backfill_excludes_a_chunk_sharing_only_a_minority_of_named_identifiers
    -> Nazuna単独共有（1/3）のPhase 1類似Chunkを正しく除外。
  test_backfill_admits_a_chunk_sharing_a_majority_of_named_identifiers
    -> Nazuna+Probe共有（2/3）のChunkは正しく許可（Ratio境界の両側を固定）。
  test_backfill_admits_a_chunk_matching_half_the_query_identifier_tokens
    -> "What is Runtime Governance?"（2/4）が壊れないことを確認。

tests/unit/conversation/test_conversation_generation.py:
  test_identifier_no_hit_denies_generation_with_a_fixed_presentation
    -> identifier_subject_count>0のNO_HITでModel Callが0回、
       固定PresentationがCOMPLETEDへ収束することを確認。
```

## 3. 全体検証

```text
uv run pytest -q                     -> 1939 passed, 7 deselected（本Package内の一時点）
uv run mypy                          -> Success
uv run ruff check .                  -> All checks passed
```

## 4. False Startの開示（Handoff §7.2「Read-onlyの軽微な操作ミス...は単独Stop理由にしない」に該当）

`documentation_rag.py`の`_enabled()`へ`generation_allowed=False`を書き込む版を一度実装し、Test実行で`DocumentationEvidence`のPydantic Validation Errorに遭遇して初めてSchema Invariantの存在に気づいた。該当箇所を`Edit`で元のTextへ手動復元し（`git diff --stat`で差分ゼロを確認、Git Actionは使用していない）、Test Fileから対応する2 Testも削除した。Source／Testの正味Diffはゼロで、Data破損・past Evidence改変は発生していない。

## 5. Scope境界の開示

`Nazuna Probe Orion`のような、個々の語が単体では高Signalでない複合固有名詞のNO_HITは、本Packageの新Hard Gateでは捕捉されない。同一Chatでの削除後Freshness（`test_nazuna_probe_orion_freshness_update_delete_regression`が既に証明する、BackfillによるFalse Citation排除）と、Real Model向けのSoft Notice（P7-RW2-B）による軽減のみに依拠する——これはP7-RW2-DのMinor Observation（P7-RW2-IR-001）およびControllerの既存判定（"Real Model Final Answer Freshness: USER MANUAL GATE"）と同一の、既に開示済みの境界である。新規Regressionではない。

## 6. Action Inventory

```text
Git Action: 0
Network Action: 0
Source／Test Mutation:
  Backend: bm25_retriever.py, conversation_generation.py（Source）、
    test_lexical_retrieval.py, test_conversation_generation.py（Test）
  一時的にdocumentation_rag.py（False Start、Edit手動復元済み、正味Diff 0）
Root外Read/Write: 0
```

Exact next action: P7-RW3-C（Current Evidence Precedence一回修正）へ連結して進む。
