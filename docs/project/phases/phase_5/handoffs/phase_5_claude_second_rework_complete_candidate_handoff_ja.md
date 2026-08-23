# Phase 5 Claude Second Rework Complete Candidate Handoff

```yaml
document_id: phase_5_claude_second_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_5
subphase: phase_5_h_rework_2
role: Claude側設計統括者役
provider: claude_code
predecessor: docs/project/phases/phase_5/handoffs/phase_5_codex_second_independent_review_rework_handoff_ja_20260822171307.md
superseded_completion: docs/project/phases/phase_5/handoffs/phase_5_claude_rework_complete_candidate_handoff_ja.md（Stable、変更なし）
gov001_correction: docs/project/phases/phase_5/history/operations/phase_5_gov001_evidence_grade_and_zero_claim_correction_ja_20260822163917.md（Stable、変更なし）
gov002_correction: docs/project/phases/phase_5/history/operations/phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md
recorded_at: 2026-08-22 18:15:20 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行）
long_running_mode_active: true
next_action: Codex Final Re-review待ちのみ。Phase 5-H Closure／Phase 6／Git操作は一切行わない。
residual_test_artifacts_left_in_place: .p5t/（pf2/, pv4/ の2件、合計約9.3MB、削除判断はUserへ返す。詳細は§Required Validation item 10）
```

本Documentは`phase_5_codex_second_independent_review_rework_handoff_ja_20260822171307.md`が要求したExact Rework（P5-CODEX-006〜009、P5-GOV-002）の全件Closure Evidenceである。既存のStable Handoff／既存History Fileは一切書き換えていない。訂正はすべてAppend-only（`phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md`）として別Fileに記録した。

## Open Major Finding

**Required Rework 5項目（P5-CODEX-006〜009、P5-GOV-002）はすべてClose**。ただし、P5-CODEX-009のProbe C検証中に、**Required Rework項目とは別の、新規・隣接する軽微な検出Gapを自己発見した**（§P5-CODEX-009内「新規発見事項」に詳述）。これはCodexが本Rework Handoffで要求した項目ではなく、本Rework自身が意図的にScope外へ追いやったものでもない——検証中に偶然見つけたものを隠さず記録する。

## P5-CODEX-006（RAG Source Authority分離の実体化）— Closed

**未成立だった5点への対応**：

1. **Typed Source Class Envelope**：[domain/context_source.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/context_source.py)（新規）に`ContextSourceUnit`（`source_id`／`source_class`／`content`）を新設。`guardrail.context_source` Hookは Flat `str`ではなく`tuple[ContextSourceItemLike, ...]`を受け取るよう変更（[conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py)の`ContextSourceItemLike` Protocol、`GuardrailContextSourceHook`型）。

2. **個別Source Identity／Authority保持**：[documentation_rag/contracts.py](../../../../../src/margpa_runtime_llm/modules/documentation_rag/contracts.py)の`DocumentationAugmentation`へ`reference_blocks: tuple[DocumentationReferenceBlock, ...]`を追加（[documentation_rag.py](../../../../../src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py)の`augment_with_context()`が`context.blocks`をそのまま渡す）。既存の`reference_message`（Flat string）は互換のため維持しつつ、Guardrailは`reference_blocks`（1 Citation = 1 Source、`chunk_id`を`source_id`に）を優先して使う。`reference_blocks`が空の場合（Legacy非Contextual `RagOrchestratorPort`——本番Adapterなし）のみ、旧来のFlat 1-Source Fallbackへ後退する。

3. **System-owned InstructionとRetrieved Dataの Authority分離**：`ConversationGenerationService._inject_documentation_reference()`が組み立てるRAG参照Messageの`role`を`MessageRole.SYSTEM`から`MessageRole.USER`へ変更した（Frozen `inference.contracts.messages`のEnumは変更していない——`USER`は既存の値）。`name="documentation_reference"`というTagだけに依存しない、Prompt Composition境界そのものでの構造的降格である。実際の確認：
   ```
   role=user name='documentation_reference' content='...'   # RAG Reference（旧: role=system）
   role=user name=None       content='question'             # 実User発話
   ```
   Token集計（`_context_usage`）も`message.role is SYSTEM`一致ではなく`message.name`一致で`rag_context_tokens`を分離するよう修正——Role変更後も既存の内訳UIが壊れない。

4. **Per-Source判定→Safe Aggregate Decision**：[point_runtime.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py)の`invoke()`が`content_sources`受領時、各Source毎に各Detectorを個別実行してから集約する（1つの結合文字列を作らない）。

5. **OFF／OBSERVE／ENFORCE、Benign／Indirect Injection、Persistent／Ephemeral、Retry／Regenerate／Branch／Resume、Public/Basic Call-0**：[test_guardrail_governance_persistent_and_rag.py](../../../../../tests/integration/web/test_guardrail_governance_persistent_and_rag.py)へ実HTTP経路のTestを4件新規追加——`SequencedContextualRag`（呼び出し毎に異なるReference文字列を返すFake）を使い、**同一の生きたComposition/Serviceインスタンス**がRetry／Regenerate／Branch-select／Resume-then-new-turnという4種の後続操作それぞれの後でも一貫してGuardrailを効かせ続けることを実HTTP経路で証明した（前回Rework時の「Shared Code Path論証」という評価を避けるため）：
   - Retry：Malicious Referenceで一度Failした Turnを再度Retryしても、2回ともModel Call 0でFail。
   - Regenerate：1回目Benignで完了した Turnに対しRegenerateした際、Rag Fixtureが2回目にMaliciousへ切り替わると、Regenerate側だけがFail（元Turnは完了のまま）。
   - Branch-select：Branch Head選択という純粋なMetadata Mutationの直後に投稿した新規Turnも、引き続きGuardrailに遮断される。
   - Resume：Archive→Unarchive→Resumeというセッションライフサイクル操作の直後に投稿した新規Turnも、引き続きGuardrailに遮断される。

**未解消のまま明記する既知の残存事項**：メッセージ全体のAuthority Model再設計（例えば`ChatMessage`に真の`AuthorityClass`型フィールドを持たせる等）はPhase 3/4のFrozen `inference.contracts.messages`を変更する必要があり、本Rework Boundaryの範囲外——今回の`USER` Role降格は、その完全な再設計を待たずに実際のPrompt上でSystem Authorityを剥奪する、現実的で最小Diffな中間解である。

## P5-CODEX-007（Policy／Authority／Approval／Detector Registry／Action Registryの実Runtime Fail-closed化）— Closed

- **全4種SnapshotへScope／Source Class／Expiry追加**：[domain/snapshots.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/snapshots.py)の`DetectorRegistrySnapshot`／`ActionRegistrySnapshot`へ`scope`／`source_class`／`expires_at`／`has_established_revision`／`is_expired`を追加（`PolicySnapshot`／`AuthoritySnapshot`と同型）。`ApprovalState`（[domain/results.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/results.py)）へも同型の`approval_revision`／`scope`／`source_class`／`expires_at`／`digest_sha512`を追加。
- **Entry Binding／Resolution Binding の分離**：[point_runtime.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py)を全面改稿。`invoke()`はPolicy／Authority／DetectorRegistry／ActionRegistryの4 Provider Portを直接受け取り、Point評価の**開始時**（Entry Binding）と、`enforce`実行**直前**（Resolution Binding）の**2回、独立して`.snapshot()`を呼ぶ**。両者の内容が一致しない、またはどちらかがStale/Unknownなら`binding_stale=True`として`resolve_actions()`へ渡し、無条件にAction 0とする。
- **`GuardrailGovernanceComposition`のAuthority非更新問題を解消**：`self.authority`（一度だけ計算されたSnapshot値）を廃し、`self.authority_provider`（Provider本体）を保持——Policyが元々そうしていたのと同じ「毎回生きたProviderへ問い合わせる」設計に揃えた。Detector/Action Registryも`_FixedDetectorRegistryProvider`／`_FixedActionRegistryProvider`という薄いPort Wrapperを新設し、Composition内から独立再取得可能にした。
- **OBSERVE Degraded化／ENFORCE Unavailable化**：Stale/Unknownな Binding は、OBSERVEでは`ExecutionState.DEGRADED`（`degraded_reason_code="binding_stale"`）、ENFORCEでは`ExecutionState.UNAVAILABLE`（`unavailable_reason_code="binding_stale"`）へ収束するよう修正——従来は両Modeとも単なる`evaluated`のままだった。
- **Approval StateのStale/Unknown Fail-closed**：[action_resolver.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/action_resolver.py)へ、`approved`だが`has_established_revision`が偽または`is_expired`なApprovalを`APPROVAL_MISSING`としてFail-closedする分岐を追加（本MVPでは`approval_required=True`を出すPolicyが存在しないため、現時点では到達路が実運用上は未行使だが、専用Testで到達性を証明済み）。

**Codex Second Review Probe A／B の再現・修正確認（本Document作成時点で直接実行、Composition経由）**：
```
Probe A: PolicySnapshot revision=0 → execution_state=unavailable executed=[] unavailable_reason_code=binding_stale
Probe B: ActionRegistrySnapshot revision=0 → execution_state=unavailable executed=[] unavailable_reason_code=binding_stale
```
いずれも修正前は`executed=True`だったもの（Codex Second Review記載値）が、修正後は`execution_state=unavailable`／`executed=[]`へFail-closedしている。加えて、Revision自体は正常（`=1`）だがDigestだけが変化するケース（Entry-Resolution間でAction Registryが差し替わる、より狭いケース）も新規Test（`test_enforce_fails_closed_when_action_registry_digest_changes_before_resolution`）で到達性を証明した。

**Test**: [test_point_runtime.py](../../../../../tests/unit/guardrail_governance/test_point_runtime.py)（Provider Port経由の`GuardrailPointRuntime`／`GuardrailGovernanceComposition`を通す Revision／Cache Matrix、Direct Resolver Test [test_action_resolver.py](../../../../../tests/unit/guardrail_governance/test_action_resolver.py)は既存のまま維持）。

## P5-CODEX-008（Unknown Safety Model Labelの型・Schema境界での棄却）— Closed

- **`RawSafetyModelObservation`＋Decoder境界の新設**：[domain/safety_model.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/safety_model.py)へ、Providerが返す未検証の生Observation（`raw_category_label`／`raw_signal`／`raw_confidence`等）を表す新規Contractと、`decode_safety_model_observation()`関数を追加。この関数だけが`raw_category_label`を`CategoryRegistry.is_known()`（`taxonomy.py`の既存だが従来Dead Codeだった機構）へ照合する唯一の場所であり、`claimed_failure=NONE`／高Confidenceを自称していても未登録Categoryなら独立に`UNKNOWN_LABEL`へ強制する。
- **Fake MatrixがDecoder境界を実際に試験するよう再設計**：[safety_model_adapters.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py)の`DeterministicFakeSafetyModelAdapter`は、もはや`failure=UNKNOWN_LABEL`等を直接設定できない——`raw_category_label`／`confidence`／`timed_out`のみを受け取り、内部で`decode_safety_model_observation()`を呼ぶ。`UNKNOWN_LABEL`と`LOW_CONFIDENCE`はDecoderが独立に導出する結果としてのみ現れる（`claimed_failure`引数からは`UNKNOWN_LABEL`／`LOW_CONFIDENCE`を渡すこと自体をValidatorで拒否）。

**Codex Second Review Probe D の再現・修正確認（本Document作成時点で直接実行）**：
```
Input : failure=none相当（claimed_failure未指定）、confidence=1.0、confidence_threshold=0.0、
        raw_category_label="novel_unknown_label"、raw_signal=CLEAR相当（Marker不一致）
Result: failure=unknown_label, is_trustworthy=False, detection.outcome=unknown
```
修正前は`is_trustworthy=True`／`outcome=clear`だったもの（Codex Second Review記載値）が、Providerの自己申告に関わらずDecoderが独立して`UNKNOWN_LABEL`へ収束している。

**Test**: [test_safety_model_seam.py](../../../../../tests/unit/guardrail_governance/test_safety_model_seam.py) — `test_unknown_raw_category_label_is_independently_rejected_by_the_decoder`（Probe D同等）、`test_a_known_registered_category_is_not_flagged_as_unknown_label`（過剰Failでないことの確認）、`test_low_confidence_failure_never_converts_to_clear_even_on_a_real_match`（LOW_CONFIDENCEもDecoder導出のみに変更）。

## P5-CODEX-009（全Client-visible Streamの欠落なきOBSERVE／ENFORCE）— Closed

1. **`ObservingStreamGuard`の大Delta欠落バグ修正**：[stream_guard.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/stream_guard.py)の`feed()`が`(self._window + delta)[-window_chars:]`で**Scan前に**切り詰めていたのを、**Scan後に**切り詰める（＝毎回の`combined`全体をDetectorへ渡した後で、次回持ち越し用の末尾だけを保持）よう修正。副作用として発生する「持ち越しWindow内のMatch再カウント」問題は、直前の持ち越しWindow単体を再チェックすることで二重カウントを防止した。
2. **Terminal Stream Result Routing**：`GuardrailStreamGuardLike` Protocolへ`summary() -> GuardrailStreamSummaryLike`を追加し、`IncrementalStreamGuard`／`ObservingStreamGuard`／`NullStreamGuard`全てに実装。`ConversationGenerationSession._run_stage()`は Stage終了時（Cancel／Reject／正常完了いずれの経路でも）に必ず一度、新規`guardrail_stream_result_hook`を呼ぶ。Composition側の新規`record_stream_guard_summary()`がこれを`GuardrailResult`へ変換し`guardrail.stream_candidate`として`record_result()`する——[guardrail_governance_routes.py](../../../../../src/margpa_runtime_llm/web/guardrail_governance_routes.py)のStatus Route`points`タプルへ4番目のPointとして追加。
3. **REASONING Channelの無条件除外を撤廃**：`_emit_guarded()`が`kind is ThinkingContentKind.REASONING`を理由にStream Guardを無条件Skipしていたのを撤廃。REASONING用に**独立した**第二のStream Guard Instance（`reasoning_stream_guard`）を新設し、FINAL Channelとは別のScan/Holdback状態を保つ（Channel跨ぎでのHoldback Flush誤タグ付けを防ぐため）。実際にはHidden Reasoning（既定）はPresentation層（`ThinkingPresentationSession._visible_semantic_deltas()`）が`semantic_deltas`へ含める前に除去するため、この修正が意味を持つのはThinking Visibility=VISIBLEの場合のみ——ちょうどReasoningが実クライアントへ到達する場合と一致する。

**新規発見事項（Required Rework項目外、Probe C検証中に自己発見）**：Codexの元Probe C（`"victim@example.com" + "x" * 1000`）をそのまま再現したところ、`match_count=0`のままだった。原因を追跡した結果、これは`ObservingStreamGuard`のWindowing問題ではなく、`_EMAIL_PATTERN`正規表現自体の`\b`（Word Boundary）終端要件に起因することを確認した——TLD直後に非単語文字（空白・句読点等）が一切現れないまま英字が続くと、正規表現が有効な終端境界を見つけられずMatch自体が成立しない（`"victim@example.com "`のように空白を1つ挟むだけで`match_count=1`に戻ることを確認済み）。これはStream Guardの欠陥ではなく`PiiPatternDetector`の正規表現境界条件そのものの限界であり、**本Second Rework HandoffのRequired Rework 4項目のいずれにも該当しない、新規・独立した軽微な検出Gap**として、隠さずここに記録する。修正はしていない——Scope外の項目を勝手にScope内へ広げず、かといって黙って見なかったことにもしない、という原則に基づく。

**Test**: [test_stream_guard.py](../../../../../tests/unit/guardrail_governance/test_stream_guard.py)（オーバーサイズ単一Delta中央でのMatch捕捉、二重カウント防止、`summary()` 3種）、[test_conversation_generation_guardrail_stream_integration.py](../../../../../tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py)（Visible Reasoning漏洩捕捉／Hidden Reasoning非到達の確認／Result Hook呼び出し2種）、[test_bootstrap_hooks.py](../../../../../tests/unit/guardrail_governance/test_bootstrap_hooks.py)（`record_stream_guard_summary`のOFF/ENFORCE/OBSERVE別Status反映）、[test_guardrail_governance_web_app.py](../../../../../tests/integration/web/test_guardrail_governance_web_app.py)（Status Routeの4 Point確認）。

## P5-GOV-002（GOV-001訂正自体の再訂正）— Closed

Append-only Correction File [phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md](../history/operations/phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md)を新規作成した。既存の`phase_5_gov001_evidence_grade_and_zero_claim_correction_ja_20260822163917.md`は一切書き換えていない。

- `.p5t/`削除（`rm -rf .p5t`）を、`REPOSITORY_STATE_VERIFIED`という誤った分類から、新設した`UNAUTHORIZED_CLEANUP_SELF_REPORTED`へ訂正した——検証可能性の強さと許可の有無を混同しないよう明示。
- Bare Mypy Preflight齟齬の原因を、根拠のない推測（「新規File追加前」等）から`UNKNOWN`（証拠不足）へ訂正した。
- Current Repository State／Reproducible Current Result／Past Action Log／Self-reportの4種を明確に再分離した。
- 事後探索・復元・追加Cleanupは一切行っていない。
- **本Rework Cycle自身についての追加自己申告**：本Correction執筆前の時点で、本Second Rework Cycle自身の中でも複数回`rm -rf .p5t`を実行していたことを認める（Codex Second Reviewを読み切る前の実行分を含む）。本Correction作成以降、本Rework Cycleの残り作業では`.p5t/`を削除せず残置した——実際に、この後に実行したBackend Full Suite（1228 passed）はすべて`.p5t/pf2`という**削除しない**新規Basetempで実行し、Session終了時点でそのまま残している（下記 Required Validation item 10参照）。

## Exact Mutation（本Second Rework Cycleで変更・新規作成した全File）

**Source**:
- [src/margpa_runtime_llm/modules/guardrail_governance/domain/snapshots.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/snapshots.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/domain/results.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/results.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/domain/context_source.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/context_source.py)（新規）
- [src/margpa_runtime_llm/modules/guardrail_governance/domain/safety_model.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/safety_model.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/domain/__init__.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/domain/__init__.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/application/action_resolver.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/action_resolver.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/application/stream_guard.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/stream_guard.py)
- [src/margpa_runtime_llm/modules/guardrail_governance/application/__init__.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/__init__.py)
- [src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py)
- [src/margpa_runtime_llm/bootstrap/guardrail_governance.py](../../../../../src/margpa_runtime_llm/bootstrap/guardrail_governance.py)
- [src/margpa_runtime_llm/bootstrap/web_application.py](../../../../../src/margpa_runtime_llm/bootstrap/web_application.py)
- [src/margpa_runtime_llm/web/guardrail_governance_routes.py](../../../../../src/margpa_runtime_llm/web/guardrail_governance_routes.py)
- [src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py)
- [src/margpa_runtime_llm/modules/documentation_rag/contracts.py](../../../../../src/margpa_runtime_llm/modules/documentation_rag/contracts.py)
- [src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py](../../../../../src/margpa_runtime_llm/modules/documentation_rag/application/documentation_rag.py)

**Test**:
- [tests/unit/guardrail_governance/test_point_runtime.py](../../../../../tests/unit/guardrail_governance/test_point_runtime.py)（Provider Port経由の再設計、6 Test）
- [tests/unit/guardrail_governance/test_bootstrap_hooks.py](../../../../../tests/unit/guardrail_governance/test_bootstrap_hooks.py)（Context Source tuple化、Stream Result Routing 3 Test追加）
- [tests/unit/guardrail_governance/test_safety_model_seam.py](../../../../../tests/unit/guardrail_governance/test_safety_model_seam.py)（Decoder境界試験へ再設計）
- [tests/unit/guardrail_governance/test_stream_guard.py](../../../../../tests/unit/guardrail_governance/test_stream_guard.py)（大Delta捕捉／二重カウント防止／summary() 6 Test追加）
- [tests/unit/conversation/test_conversation_generation.py](../../../../../tests/unit/conversation/test_conversation_generation.py)（Role assertion修正のみ）
- [tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py](../../../../../tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py)（Visible/Hidden Reasoning、Result Hook 4 Test追加）
- [tests/integration/web/test_guardrail_governance_persistent_and_rag.py](../../../../../tests/integration/web/test_guardrail_governance_persistent_and_rag.py)（Retry/Regenerate/Branch/Resume 4 Test追加）
- [tests/integration/web/test_guardrail_governance_web_app.py](../../../../../tests/integration/web/test_guardrail_governance_web_app.py)（Status 4 Point確認を追加）

**Documentation（新規、Append-only）**:
- [docs/project/phases/phase_5/history/operations/phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md](../history/operations/phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md)（新規）
- 本File自体（新規）

既存のStable Doc／既存History／既存Handoff（GOV-001訂正を含む）は1件も編集していない。

## Required Validation（10項目、全実測）

| # | 項目 | Command | 結果 |
|---|------|---------|------|
| 1 | Typed RAG Source Authority／Prompt Composition／全Conversation経路 | `pytest tests/integration/web/test_guardrail_governance_persistent_and_rag.py` | 9 passed |
| 2 | Policy／Authority／Approval／Detector Registry／Action Registry Runtime stale/cache Matrix | `pytest tests/unit/guardrail_governance/test_point_runtime.py tests/unit/guardrail_governance/test_action_resolver.py` | 23 passed |
| 3 | Unknown Raw Label／Unknown Category／Schema mismatch Safety Model Matrix | `pytest tests/unit/guardrail_governance/test_safety_model_seam.py` | 11 passed |
| 4 | Large Single Delta／Visible Thinking／Stream Result Status／Concurrency | `pytest tests/unit/guardrail_governance/test_stream_guard.py tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py` | 36 passed |
| 5 | Phase 5 Guardrail Focused Suite | `pytest tests/unit/guardrail_governance/` | 120 passed |
| 6 | RAG／Conversation／Persistence／Web Adjacent Regression | 上記＋`tests/integration/web/` `tests/unit/conversation/` `tests/unit/documentation_rag/`（Full Suiteに包含） | 全件Full Suiteへ包含、個別実行でも失敗なしを確認済み |
| 7 | Public／Basic／v1／v2 Call-0 | `pytest tests/integration/web/test_guardrail_governance_public_basic_call0.py tests/integration/web/test_runtime_governance_public_basic_call0.py` | 全passed（Full Suiteに包含） |
| 8 | Backend Full Suite（短いProject-local Basetemp） | `pytest --basetemp=.p5t/pf2`（Project Root全体） | **1228 passed, 3 deselected**（60.82s） |
| 9 | Frontend test／typecheck／lint | `npm run test -- --run` / `npm run typecheck` / `npm run lint` | **175 passed（20 File）** ／ Error 0 ／ Error 0（UI非変更のためBuild再確認は必須外） |
| 10 | `ruff check .`／`ruff format --check .`／Bare mypy | 下記詳細参照 | 全PASS（下記の限定付き） |

### item 10 詳細（ruffとTest Artifact残置の相互作用）

Required Validationの意図的な方針転換（P5-GOV-002）に伴い、`.p5t/`配下（`pf2/`＝Backend Full Suite本体、`pv4/`＝Required Validation item 1個別再実行分、計約9.3MB）は本Document作成後も**削除せず残置する**。この残置Directory内には、Symlink/Root-escape関連のTestが意図的に作る「Lightning workspace with spaces」という名のFixture Project（`app.py`という名の断片的なPythonファイルを含む）が実在する。`ruff`のConfigは元々`.p5t/`をExcludeしていないため、これを含めたまま`ruff check .`を素朴に実行すると、このFixture内の断片Python（`@app.get(...)`のみが単独で存在し`app`が未定義）に対して`F821`が47件検出される——**これはSource Regressionではなく、残置したTest ArtifactにRuffが誤って踏み込んだ結果である**（Codexが以前指摘した「macOS長Basetemp Path起因の偽陽性」と同じ性質の、別種の偽陽性）。

正しいCommand（Test ArtifactをCLI Flagで明示的に除外、Config File自体は変更しない）：
```
ruff check --extend-exclude .p5t .        → All checks passed!
ruff format --check --extend-exclude .p5t . → 320 files already formatted
```
Bare `mypy`（引数無し、`pyproject.toml`の`[tool.mypy]`が元々`files=["src","scripts","tests"]`のみを対象にしており`.p5t/`を最初からScanしないため、Flag不要）：
```
mypy → Success: no issues found in 320 source files
```

## 自己申告と独立検証の分離（P5-GOV-002訂正後分類を適用）

- 本Document中のBackend Full Suite（1228 passed）／Frontend（175 passed）／ruff／mypyの各実測値：**REPOSITORY_STATE_VERIFIED**（Claude自身が本Session内で直接Command実行し観測。独立した第三者による再実行はまだ得ていない）。
- Probe A／B／D（Codex Second Review記載の入力をそのまま用いて本Document作成時点で再実行した結果）：**REPOSITORY_STATE_VERIFIED**（Claude自身の再実行であり、Codex自身の再実行ではない——`INDEPENDENTLY_REPRODUCED`を名乗るのはCodex自身がこのHandoff以降に再実行した場合のみ）。
- Probe Cで新規発見した`_EMAIL_PATTERN`の`\b`境界限界：**REPOSITORY_STATE_VERIFIED**（本Document作成時点で直接実行し観測した事実）。
- `.p5t/`削除（本Rework Cycle中の複数回、Correction執筆前）：**UNAUTHORIZED_CLEANUP_SELF_REPORTED**（P5-GOV-002訂正後の分類。Project Root内のTest Scratchのみを対象にしたという限定付きの自己申告）。
- Project Root外接触・Provider Memory・User実`runtime_data/`・Network・AWS/Lightning・Authority捏造：引き続き**SELF_REPORTED_UNVERIFIED**（独立したAction Log裏付けなし）。

## Next Action

Codex Independent Review（Second Rework再Review）待ちで停止する。Phase 5-H Closure、Phase 6開始、User Acceptance、DeepSeek Gate、いかなるGit操作も本Document作成後は一切行わない。`.p5t/`（`pf2/`／`pv4/`）は削除せず残置し、削除するかどうかの判断はUserへ返す。
