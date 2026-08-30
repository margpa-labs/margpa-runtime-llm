# Phase 7 Claude RAG Grounding／Citation UI Final Bounded Rework — Exact Handoff

```yaml
document_id: phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_handoff_20260830121213
document_type: exact_differential_execution_handoff
document_state: frozen_ready
language: ja
created_at: 2026-08-30 12:12:13 JST
provider: Claude
role: 設計者兼実装者役
task_identity: current_claude_task
phase: phase_7
execution_scope: P7-RW3-0_to_P7-RW3-D
implementation_authority: requires_exact_user_start
maximum_claim: COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW
phase_7_closure_authority: false
phase_8_authority: false
git_authority: false
```

## 1. Authority／速度優先の停止線

現在のClaude Taskを継続使用する。Fresh Task初期化、Role Bootstrap、長いReceipt待ちを行わない。

本書はUser実画面で再現したRAG Failureを、次の3点だけで一回のBounded Reworkとして閉じる。

1. Citation UIのField Label／Copy Button配置が壊れている。
2. Identifier Backfill条件が弱く、`Nazuna`だけを共有する無関係Project Docsを採用する。
3. Current Reference／NO_HIT Noticeが過去Historyより前に置かれ、Qwenが旧回答を優先する。

P7-RW3-0からP7-RW3-Dまで連結実行する。進捗報告、軽微な操作ミス、既知Minorまたは追加Hardening候補だけを理由に停止しない。MaterialなData破損、過去Evidence改変、Scope内で解消不能な主経路RegressionだけをTrue Stopとする。

Phase 7 Closure、Phase 8、一般Web検索、Git、Backup、Roadmap、Real Network、Provider Memory、User `runtime_data/`接触は行わない。

## 2. Mandatory Reading

次の4文書だけを全文読む。追加の広域Docs探索は行わない。

1. Active Base Handoff

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_post_manual_citation_freshness_auto_resume_bounded_rework_exact_handoff_ja_20260830101851.md
SHA-512: f977711051cbe782eac06a8117603d6c0fcb510e77a43735bbe84c1311c1304201a704b8f5ed313051ffe455cfa63be5ce7c1499c90ca173c7dd39a6cc02f1a6
```

2. P7-RW2 Exact Return

```text
docs/project/phases/phase_7/handoffs/phase_7_claude_post_manual_bounded_rework_exact_return_handoff_ja_20260830113500.md
SHA-512: 3f7cfa96053bae65cfe4385c40d73a9c3934566089f5a2a818a15ed5440782ec9a9cb0456441fa205e16152fb4ca50ba16d4df218aee2ad20e0d2d8ced875166
```

3. Controller Review

```text
docs/project/phases/phase_7/history/operations/phase_7_codex_controller_post_manual_bounded_rework_review_ja_20260830113156.md
SHA-512: 9a6b6b1f4ffba13634bead5065d114052cb1b8313a4733f09e0c54851b7f974a55d67f5870eee73c6314bc9d96e877c9ebb1998addd8a259156c1a9c8364209f
```

4. User Recheck Sheet

```text
docs/project/phases/phase_7/history/operations/phase_7_post_manual_bounded_rework_user_recheck_sheet_ja_20260830113156.md
SHA-512: e5638236f8a49b8aa358c6ccffdb4c71824677ce810118c5cfd5eae075e1342c3b8d925871af75614f32f02d7a5cec397a1ad7bd139a3f55d8a3de7670adb1b5
```

## 3. User Mac Failure Evidence

### 3.1 Registered／Updated Local Document

```text
Deleted previous document:
  MARGPA Manual Probe 7

New document:
  MARGPA Manual Probe 8
  initial/current tested content: Nazuna Probe Orionの検証コードは CEDAR-25123 である。

updated tested content:
  Nazuna Probe Orionの検証コードは CEDAR-12523 である。
```

### 3.2 Grounded Answer Failure

新Local DocumentがCurrent Citationとして選択され、Document Digestも更新されたにもかかわらず、同一Chatの新Turnは繰り返し旧Documentの値を回答した。

```text
actual answer after new document:
  CEDAR-9847

actual answer after update:
  CEDAR-9847

expected:
  Current Local Documentの値（CEDAR-25123または更新後CEDAR-12523）
```

これはIndex更新Failureではない。Current Local Citation／Digestは変化している。Current Referenceが過去Assistant Historyより前へ挿入され、Qwenが後続の旧Historyを優先できるPrompt Order Failureである。

### 3.3 Delete Failure

削除後の同一ChatはCEDAR-9847をCurrent Factとして回答し、無関係なPhase 1 Project Docs Citationを表示した。

新規Chatは「直接的な記述はない」と述べながら、Phase 1のAcceptance Probeから架空のShell Codeを推測生成し、同じ無関係Citationを表示した。

Root causeは、P7-RW2のBackfill GuardがQuery Identifier Tokenとの**any overlap**だけを要求するため、`Nazuna`だけを含むPhase 1 Docsが`Probe`／`Orion`を含まなくても選択されることにある。

### 3.4 Citation UI Failure

Backend Identity自体は投影されたが、CSSが全Buttonへ同一Grid位置を指定し、3つのCopy Buttonを重ねて最後のButtonだけを表示している。

```css
.message-citation button {
  grid-column: 2;
  grid-row: 1 / span 2;
}
```

画面では2つの短縮HashがField Labelなしで表示され、`75dc...`と`c771...`のどちらがChunk ID／Document Digestか判別できなかった。表示された`75dc...`とDocument Digest Copyで得た`c771...`が異なるのはEvidence不一致ではなく、前者がChunk ID、後者がDocument DigestであることをUIが明示しなかったためである。

Project DocsにもChunk ID／Document Digestを表示すること自体は意図どおりであり、削除しない。同一Document由来の複数Chunkが同じDocument Digestを共有することも正しい。

### 3.5 Auto-Resume Result

次はUser MacでPASSしたため、再実装しない。

```text
Restart後の非Archive Chat: Resume Buttonなしで送信成功
Archive解除後のChat 2件: Resume Buttonなしで送信成功
再Archive／再解除後: Resume Buttonなしで送信成功
```

## 4. Finding

### P7-CODEX-011 — Citation UI Identity／Copy Controls Collapsed

```yaml
severity: major_user_observability
closure_blocker: true
```

### P7-CODEX-012 — Current Evidence Loses to Historical Assistant Context

```yaml
severity: major_grounding
closure_blocker: true
```

### P7-CODEX-013 — Partial Identifier Overlap Produces False Grounding

```yaml
severity: major_grounding
closure_blocker: true
```

P7-CODEX-007のBackend ProjectionとP7-CODEX-009 Auto-Resumeは保持する。P7-CODEX-008はP7-CODEX-012／013へ再分類して未解決とする。

## 5. P7-RW3-0 — Entry／Exact Reproduction

1. Mandatory Reading Digestを照合する。
2. `MARGPA Manual Probe 8`相当Fixtureを作る。
3. 次の3 Failureを修正前Testで再現する。
   - Current Local Referenceがあるのに旧History値が優先されるPrompt順序。
   - Local削除後、`Nazuna`だけを含むProject DocsがFalse Groundingされる。
   - Citation Copy Buttonが同一Grid Cellへ重なる。
4. Auto-Resume Source／Testへ変更を加えない。

Recovery:

```text
docs/project/phases/phase_7/history/index/phase_7_rag_final_bounded_rework_p7_rw3_0_recovery_ja_<timestamp>.md
```

## 6. P7-RW3-A — Citation UIを一回で修正

### 6.1 Required Markup

Citation 1件を、少なくとも次の独立Row／Labelへ分ける。

```text
Source: Local Corpus / Project Docs
Path: <project_relative_path>                  [Pathをコピー]
Heading: <heading_breadcrumb>
Chunk ID: <short chunk_id>                    [Chunk IDをコピー]
Document Digest: <short document_sha512>      [Document Digestをコピー]
```

### 6.2 Required Behavior

- 3つのCopy Buttonを重ねない。
- 各Buttonが対応する完全値だけをCopyする。
- 短縮値の隣にField Labelを必ず表示する。
- Full Hashは`title`またはCopyで確認できる。
- Mobile／狭いModal幅でもButtonを隠さず折り返す。
- Local Corpus／Project DocsのSource Labelを保持する。
- Project Docs Citation Identityも保持する。
- 過去Citation Recordの値は変更しない。Renderer変更だけで過去Turn表示が新Layoutになることは許容する。

### 6.3 Test

- 全Label可視。
- Copy Button 3個が可視かつ別Element。
- Path／Chunk／DigestそれぞれのCopy値が一致。
- 同一Documentの異なるChunkはChunk IDが異なりDocument Digestが同じでも正しく表示。
- Narrow Container Layoutで重なりなし。

Recovery:

```text
docs/project/phases/phase_7/history/index/phase_7_rag_final_bounded_rework_p7_rw3_a_recovery_ja_<timestamp>.md
```

## 7. P7-RW3-B — Identifier False Groundingを一回で修正

### 7.1 Required Retrieval Contract

Identifier-bearing Queryでは、1語だけの偶然一致を理由にTop-kを無関係Chunkで埋めない。

Exact Probe:

```text
Query: Nazuna Probe Orionの検証コードは？

Allowed grounded chunk:
  Nazuna + Probe + Orionを対象として支持するCurrent Local Document

Rejected false-grounding chunk:
  Nazunaだけを含むPhase 1 Public Mapping／Acceptance Probe文書
```

### 7.2 Implementation Constraint

- 単純な`any identifier overlap`を廃止する。
- Query内の複合固有SubjectまたはDistinctive Identifier Setを扱い、完全Phrase、全主要Token、または明示的なCoverage Ratioで判定する。
- `What is Runtime Governance?`等の通常Queryを壊さない。
- 以前撤回した無制限なTitle-Case Run Heuristicをそのまま復活させない。
- 2語／3語の正当な固有名、単一Identifier、Code／Path Queryを別Fixtureで保護する。
- Current Local EvidenceがSubjectを完全Coverageした場合、無関係Project DocsをTop-k Backfillしない。
- Current Evidenceが0の場合、回答根拠としてのCitationは0にする。

### 7.3 Deterministic Identifier NO_HIT

Current Corpusに複合固有SubjectのEvidenceがない場合、Main Modelの一般知識または過去Historyへ委ねて架空Codeを生成させない。

次のいずれかをRAG-owned Deterministic Contractとして実装する。

- Identifier-specific NO_HITをGeneration Deniedへ分離する。
- またはInference Call前に固定の「現在のCorpusに根拠がない」Presentationへ収束する。

通常の雑談／一般知識Queryに対する従来NO_HIT General Generationは維持する。固有Subject付きNO_HITだけをFail-closedにする。

Recovery:

```text
docs/project/phases/phase_7/history/index/phase_7_rag_final_bounded_rework_p7_rw3_b_recovery_ja_<timestamp>.md
```

## 8. P7-RW3-C — Current Evidence Precedence

### 8.1 Prompt Order

Grounded ReferenceとNO_HIT Noticeを、System直後／全History前ではなく、**最終User Messageの直前**へ挿入する。

```text
System
Historical User / Assistant Turns
Current Documentation Reference or Current NO_HIT Notice
Current User Message
```

`TOOL` Roleは維持する。LlamaCpp Chat Templateの最終User検出、Guardrail Context Source、Token Budget、Summary Modeを壊さない。

### 8.2 Current Authority Instruction

Current Reference Instructionへ次を明示する。

- Current ReferenceはこのTurnのCurrent Corpus Snapshotである。
- 過去Assistant回答と矛盾する場合、Current Referenceを優先する。
- Current Referenceにない旧Code／値を再利用しない。
- 回答中の固有Code／IdentifierはCurrent Referenceに存在するものだけを使用する。

### 8.3 Output Consistency Boundary

Current Grounded EvidenceがあるTurnで、CandidateがCurrent EvidenceにないCode形式Identifier（例:`CEDAR-9847`）を出した場合、そのCandidateを根拠付き回答としてそのまま提示しない。

既存Tokenizer／Identifier判定を再利用したBounded Consistency Check、1回だけのGrounded Retry、またはSafe Grounding Failureのいずれかで収束させる。Judge Modeへ依存させない。

Streaming済み誤答を後から撤回する方式は禁止する。Grounded RAG Turnだけ必要最小限Bufferするか、提示前に検査できる既存Stageを利用する。通常RAG OFF／一般Chat Streamingを変更しない。

### 8.4 Exact Regression

同一Conversation Historyへ旧Assistant回答`CEDAR-9847`を含め、Current Local Documentを次の順で実行する。

```text
1. Current = CEDAR-25123
   -> Final AnswerにCEDAR-9847を出さない。
   -> CEDAR-25123または正直なGrounding Failureへ収束。

2. Update Current = CEDAR-12523
   -> Final AnswerにCEDAR-9847／CEDAR-25123をCurrent Factとして出さない。
   -> CEDAR-12523または正直なGrounding Failureへ収束。

3. Delete Current Document
   -> 同一Chat／新規ChatともCodeを捏造しない。
   -> Current Evidenceなしの固定結果。
   -> Citation 0。

4. Historical Turns
   -> 過去Answer／Chunk ID／Document Digestは不変。
```

Prompt Message順序Testだけで完了扱いにしない。Candidate Presentationまで含むDeterministic Testを必須とする。

Recovery:

```text
docs/project/phases/phase_7/history/index/phase_7_rag_final_bounded_rework_p7_rw3_c_recovery_ja_<timestamp>.md
```

## 9. P7-RW3-D — Verification／1 Cycle Review／Return

### 9.1 Focused First

```text
Frontend Citation UI Test
Lexical Query／Retriever Test
Local Corpus End-to-End Update／Delete Test
Conversation Generation Prompt Order／Presentation Test
Persistent Citation Reload Test
```

### 9.2 Canonical Once

Focused成立後、最終差分でCanonical Backend／Mypy／Ruff／Frontend Typecheck／Lint／Test／Buildを各1回実行する。成立済みCommandを理由なく反復しない。

### 9.3 Internal Review

1 Cycleだけ実施する。P7-CODEX-011〜013、過去Evidence不変、Current Evidence Precedence、Identifier NO_HIT、Citation UIだけをReviewする。

Material Findingがあれば同Scope内で即Reworkし、該当Focused Testだけ再実行する。Minor／Polish／Phase 8以降候補は記録だけで停止・拡張しない。

### 9.4 Return

```text
docs/project/phases/phase_7/history/index/phase_7_rag_final_bounded_rework_p7_rw3_d_final_recovery_ja_<timestamp>.md
docs/project/phases/phase_7/handoffs/phase_7_claude_rag_grounding_and_citation_ui_final_bounded_rework_exact_return_handoff_ja_<timestamp>.md
```

最大Claimは`COMPLETE_CANDIDATE_FOR_CONTROLLER_REVIEW`。Phase 7 ClosureまたはUser Manual PASSを代行しない。

## 10. Acceptance

```text
P7-RW3-ACC-001: Citation Field Labelが明確で、Copy Button 3個が重ならない。
P7-RW3-ACC-002: 表示短縮値と対応するFull Copy値のFieldが一致する。
P7-RW3-ACC-003: Current Local Document完全Coverage時、無関係Project DocsをBackfillしない。
P7-RW3-ACC-004: 同一Chatの旧Assistant値よりCurrent Referenceを優先する。
P7-RW3-ACC-005: Update後は最新値または正直なGrounding Failureへ収束する。
P7-RW3-ACC-006: Identifier付き削除後NO_HITでCodeを捏造せずCitation 0。
P7-RW3-ACC-007: 過去Turn／Citation／Digest不変。
P7-RW3-ACC-008: RAG OFF／一般Chat Streaming不変。
P7-RW3-ACC-009: Auto-Resume既存PASSを維持。
P7-RW3-ACC-010: Canonical Regression 0。
```

## 11. Exact Next Action

Userの開始宣言受領後、P7-RW3-0からP7-RW3-Dまで停止せず連結実行する。
