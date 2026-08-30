# Phase 7 Non-Web Closure Alignment — Package P7-NW-0 Recovery（Entry／Current Baseline Freeze）

```yaml
document_id: phase_7_non_web_closure_p7_nw_0_recovery_20260829224815
document_type: package_recovery_index
document_state: final
language: ja
created_at: 2026-08-29 22:48:15 JST
active_contract: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md
package: P7-NW-0
task_identity: current_claude_phase_7_task
fresh_task_bootstrap: false
```

## 0. Recovery Index Pointer

前Package Chain（P7-0〜P7-I）は[P7-I Final Recovery](phase_7_current_claude_task_p7_i_final_recovery_ja_20260829190939.md)で終了済み。本Recovery Indexは同一Claude Task内の**差分Continuation**として、P7-NW-0（Entry／Current Baseline Freeze）を記録する。次Package: P7-NW-A Recovery。

## 1. Mandatory Differential Reading／Digest確認

Handoff §2記載の8文書全文を指定順で読了し、SHA-512を照合した。全件一致（不一致0件）。

```text
1. Claude Exact Return（27f68858...5dffc31）        一致
2. P7-I Final Recovery（2f5da0fe...2efd3190）        一致
3. Controller Bounded Independent Review（5717ecd0...9724d045） 一致
4. External Web Phase 11+延期Decision（e66f7021...e8cd5e44） 一致
5. Phase 7 Current Index（41773dd7...5919eee55f3f）   一致
6. Phase 7 Acceptance Matrix（65a33c7d...062b961bff）  一致
7. Current Unresolved Registry（923b84ec...a6f6749fd0） 一致
8. PoC／MVP Operating Policy（9b7dca30...b8fecb7d94990cd45835） 一致
```

Handoff本体自体のSHA-512（`b1fc2da6...48116de1c8`）も、開始直前に`shasum -a 512`で照合し一致を確認済み。

## 2. Current Decision Premiseの再取得

- ClaudeのP7-0〜P7-I `COMPLETE_CANDIDATE`は、Codex Controller Bounded Independent Reviewにより`ADJUST／BOUNDED WEB REWORK REQUIRED`と判定された（P7-CODEX-001〜005、いずれもWeb実利用経路に関するMajor Finding）。
- 2026-08-29 22:26、Userは実General Web Search、外部Network Search／Fetch、Web EvidenceのChat／Citation接続、Server Canonical Web OFF／ON、外部送信Consent／PII Enforcement、一般URL Fetch、Public／BYOP Endpoint UX、Hostile-site Sandbox、Provider CallとOutbound Network Callの観測分離を、**Phase 11以降へ明示的に延期**した。
- この結果、P7-CODEX-001〜005はPhase 7 Closure Blockerから、Phase 11以降で再開する既知DebtへReclassifyされた（未解決Registry `UF-P7-001`／`UF-P7-002`）。
- 本差分Taskの中心Scopeは、**Local Corpus／Citation／Data ControlsのPoC／MVP Closure品質、過大Claim訂正、Acceptance再導出およびUser Manual Candidate**のみである。Web実利用経路の実装・接続・修正は一切行わない。

## 3. Finding Ledger — P7-CODEX-001〜005を本Taskで修正しないことの明記

```yaml
finding_id: P7-NW-LEDGER-001
disposition: intentionally_not_reworked_this_task
scope_authority: phase_7_claude_non_web_closure_alignment_exact_differential_handoff_ja_20260829224014.md §1, §6
```

P7-CODEX-001（Production Web SearchがFixture固定）、P7-CODEX-002（Manual Web EvidenceがChat回答へ接続されない）、P7-CODEX-003（Web検索OFFがServer正本ではない）、P7-CODEX-004（外部送信Consent／PII GateがWeb実行経路へ未接続）、P7-CODEX-005（`network_calls_made`のObservability不正確）は、いずれも技術事実として保持し、Source修正を行わない。これらはUser Decisionにより既にPhase 11以降の`Governed External Web Knowledge Runtime`へ再分類済みであり（未解決Registry §6 `UF-P7-001`／`UF-P7-002`）、本Taskの中で新たに再確認・再テストする対象でもない（Handoff §6 Hard Scope Exclusionsに明記）。

## 4. 非Web Closure Blocker候補の列挙（Source変更前）

Source変更に着手する前に、Local Corpus／Citation／Data Controlsの範囲でCritical／Major／MVP Blocker候補がないかを、既存Source読解によって確認した（新規Testは追加していない）。

### 4.1 確認した観点と結果

```text
観点1: Local Corpus ContentがEnterprise guardrail.context_source経路を迂回しないか
  -> adapters/documentation_rag/composite_document_source.py を読解。
     CompositeDocumentSource は DocumentSourcePort レベルでのみ合成し、
     Local Corpus文書は既存 DocumentationRagApplicationService の
     単一Pipelineへ完全に合流する（別Injection経路を新設していない）。
     guardrail.context_source（CONTEXT_SOURCE_CLASS_DOCUMENTATION_RAG_CITATION）
     はDocumentationRagApplicationServiceの出力に対して既存のまま動作するため、
     Local Corpus由来のCitationも迂回なく同じScan対象になる。
     -> Blocker候補なし。

観点2: Data Controls UI／APIが未実装Capability（Export／Delete等）を
  実行可能であるかのように誤認させていないか
  -> DataControlsPanel.tsx、i18n/translations.ts（dataControls*キー全件）、
     data_controls_routes.py、data_controls_contracts.py を読解。
     APIは /policy(GET) /consent(PUT) /reset(POST) の3経路のみで、
     Export／Delete相当のRouteは存在しない。UIも「既定値へ戻す」
     （Consent Resetの正確な説明）のみで、Data Export／一括Delete、
     Feedback収集、Synthetic生成、Training実施等を示唆する文言は
     一件も存在しない。
     -> 虚偽Capability表示なし。UI／API文言修正の必要なし。

観点3: P7-ACC-023「Document Prompt InjectionをDetection Evidenceへ残す」の
  Local Context Source部分が独立して成立しているか
  -> Local Corpus文書は既存Phase 5 guardrail.context_source機構（観点1で
     確認済み）を通過するため、Web専用の新設 modules/web_knowledge/
     domain/prompt_injection_detector.py（Fetched Web Content限定の
     Heuristic、OFF/OBSERVE/ENFORCE Mode）とは独立に、Local Context
     Source部分のDetection Evidence経路は既存のまま維持されている。
     -> Blocker候補なし（Web部分とLocal部分は構造的に分離済み）。
```

### 4.2 結論

本Task開始時点でSource修正を要するCritical／Major／MVP Blockerは検出しなかった。P7-NW-B／P7-NW-Cでは、この結論を追加のTest増設なしに確認・記録するにとどめる（Handoff「既存Evidenceで成立する項目へ不要なTestやSource変更を追加しない」に従う）。単に実装が存在することを理由に、全Sourceを機械的に書き直す作業は行わない。

## 5. Action Inventory（本Package内）

```text
Git Action: 0（git status --short を1回、Working Tree差分確認目的でRead-onlyに実行。
  Handoff §7「偶発的なRead-only Git Callだけを理由に自己停止しない」に基づき、
  事実として記録し継続する。Mutationは一切行っていない）
Network Action: 0
Provider Memory Action: 0
Root外Read/Write: 0
Source／Test Mutation: 0
Destructive/Irreversible Mutation: 0
```

Exact next action: P7-NW-A（Scope／Acceptance Claim Correction）へ連結して進む。
