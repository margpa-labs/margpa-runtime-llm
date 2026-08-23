# Phase 5 Claude Third Rework Complete Candidate Handoff

```yaml
document_id: phase_5_claude_third_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_5
subphase: phase_5_h_rework_3
role: Claude側設計統括者役
provider: claude_code
predecessor: docs/project/phases/phase_5/handoffs/phase_5_codex_third_independent_review_rework_handoff_ja_20260822183801.md
superseded_completion: docs/project/phases/phase_5/handoffs/phase_5_claude_second_rework_complete_candidate_handoff_ja.md（Stable、変更なし）
gov001_correction: docs/project/phases/phase_5/history/operations/phase_5_gov001_evidence_grade_and_zero_claim_correction_ja_20260822163917.md（Stable、変更なし）
gov002_correction: docs/project/phases/phase_5/history/operations/phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md（Stable、変更なし、CLOSEDのまま）
recorded_at: 2026-08-22 19:02:33 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行）
long_running_mode_active: true
next_action: Codex Independent Re-review待ちのみ。Phase 5-H Closure／Phase 6／Git操作は一切行わない。
residual_test_artifacts_left_in_place: .p5t/（p3a/, p3b/, p3f/, pf2/, pfull2/, pv4/ の6件、合計約33MB、削除判断はUserへ返す）
```

本Documentは`phase_5_codex_third_independent_review_rework_handoff_ja_20260822183801.md`が要求したExact Rework（P5-CODEX-006／007／008）のClosure Evidenceである。User指示通り、**P5-CODEX-009とP5-GOV-002は再Openしていない**——Codex自身のAccepted Evidence（§6）記載通りCLOSEDのまま扱い、本Rework Cycleではこの2件について一切のSource変更を行っていない。既存のStable Handoff／既存History Fileも一切書き換えていない。

## Closure Summary

```text
P5-CODEX-006 : CLOSED
P5-CODEX-007 : CLOSED
P5-CODEX-008 : CLOSED
P5-CODEX-009 : CLOSED（再Openしない、User指示通り）
P5-GOV-002   : CLOSED（再Openしない、User指示通り。違反履歴は保持）
Open Major Finding: 0
Phase 5-H Recommendation: Codex Independent Re-review待ち（本Documentからは推奨しない）
```

## P5-CODEX-006（RAG Retrieved DataがUser Inputと同じAuthorityになった）— Closed

**問題**：第2回ReworkでRAG参照Messageを`role=system`から`role=user`へ変更したが、実User Messageも同じく`role=user`であるため、結局RetrievedデータがUser Inputと同一Nominal Authorityへ収束していた。

**修正**：
1. **RAG参照Messageを`role=tool`へ変更**（[conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py)の`_inject_documentation_reference()`）。System（Instruction）／User（人間の発話）のいずれとも異なる、第3の型レベルAuthorityを持つ。
2. **`LlamaCppChatTemplate`の`supported_message_roles`へ`MessageRole.TOOL`を追加**（[adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)）——追加しないと`InferenceService._validate_request()`がRAG有効な全生成を`UNSUPPORTED_CAPABILITY`で即座に拒否するため、機能的に必須の変更。`_prepare()`（`chat_template.py`）はRole固有の分岐を持たず、あらゆるRoleのMessageをそのままGGUF埋め込みJinja Chat Templateへ渡すのみであることを確認済み。
3. **Roleの選択自体をHard-codeしない**：新規`_PROMPT_ROLE_BY_SOURCE_CLASS`辞書（`source_class -> MessageRole`）を新設し、`DocumentationReferenceBlock.source_class`（[documentation_rag/contracts.py](../../../../../src/margpa_runtime_llm/modules/documentation_rag/contracts.py)へ新規追加、RAGモジュール自身が宣言する分類）から動的にRoleを決定する。今日の2種のSource ClassはいずれもTOOLへ写像されるが、将来の異なるSource Classは、この関数自体を変更せずMapping追加のみで異なる扱いが可能。
4. **型としての追跡可能性**：`_context_source_items()`をSession Methodからmodule-level関数へ昇格し、Guardrail判定（`_guardrail_context_source_check`）とPrompt Composition（`_inject_documentation_reference`）の両方が**同一の`augmentation`オブジェクトに対する同一関数呼び出し**から`tuple[_ContextSourceItem, ...]`を得る——Guardrail判定後に独立して別の生成ロジックへ切り替わることはない。
5. **実Native Messageの証明**：[test_conversation_generation.py](../../../../../tests/unit/conversation/test_conversation_generation.py)に`reference.model_dump(mode="json", exclude_none=True)["role"] == "tool"`と`request.messages[-1].model_dump(...)["role"] == "user"`を追加——`LlamaCppChatTemplate._prepare()`が実際に行う変換（`model_dump(mode="json", exclude_none=True)`）と同一の呼び出しであり、これが実Backendへ渡るNative Payloadそのものであることを確認した。

**実測（本Document作成時点で直接実行）**：
```
role=tool  name=documentation_reference content='[REFERENCE]retrieved...'
role=user  name=None                    content='what is x?'
```

**5. Citation表示／永続復元、Retry／Regenerate／Branch／Resume、Public／Basic Call-0の維持**：Citation永続化は`DocumentationCitation`（Message Content/Roleと無関係な別Contract）のみを介するため無影響。既存の[test_guardrail_governance_persistent_and_rag.py](../../../../../tests/integration/web/test_guardrail_governance_persistent_and_rag.py)（第2回Reworkで追加したRetry/Regenerate/Branch/Resume 4 Testを含む）を含む全Web/Conversation/Documentation RAG回帰Suiteが無修正のまま成功することを確認した（下記Validation参照）。

**既知の限定事項（正直に記録）**：本環境はModel Load/Downloadが禁止されているため、GGUF埋め込みJinja Chat Templateが実際に`role="tool"`のMessageをどう描画するかは実Model上で検証できていない——`_prepare()`自体がRole非依存であることはSource Read／Unit Testで確認済みだが、Chat Template自体の実際の解釈は本Reworkの範囲では未検証。これは第1回・第2回Reworkが`role=system`／`role=user`を選んだ際にも同一の制約があった。

## P5-CODEX-007（Snapshot Identityが実体へBindingされていない）— Closed

**問題**：Entry/Resolution二重取得によるRevision/Expiry/Digest自己一致検査は成立していたが、(a) Snapshot相互のScope整合、(b) `DetectorRegistrySnapshot.registered_detector_ids`と実Detector集合の一致、(c) `ActionRegistrySnapshot.registered_action_ids`と実`registry`/`adapters`集合の一致、(d) `PolicyDecision.policy_revision`/`policy_digest_sha512`とCaptured Policy Snapshotの一致、のいずれも検査していなかった。

**修正**（[point_runtime.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py)）：
1. `_scope_consistent()` — Policy/Authority/DetectorRegistry/ActionRegistryの4 Snapshotの`scope`が全て一致することを検証。
2. `actual_detector_ids = frozenset(detector.detector_id for detector in self._detectors)` を `detector_registry.registered_detector_ids` と突合。
3. `actual_action_ids = frozenset(registry.keys())` を `action_registry.registered_action_ids` と突合。
4. `_policy_decisions_bound_to_snapshot()` — 全`PolicyDecision`の`policy_revision`/`policy_digest_sha512`をEntry Binding の`policy_snapshot`と突合。
5. 上記4つのいずれかが不一致なら`entry_binding_mismatch=True`とし、OBSERVEは`degraded`、ENFORCEは既存の`binding_stale`ORチェーンへ合流させて`unavailable`／Action 0へ収束。
6. **Approval Scope Binding**（[action_resolver.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/action_resolver.py)）：`resolve()`へ新規`expected_scope`引数を追加し、Approval-required経路で`approval.scope != expected_scope`なら`APPROVAL_MISSING`としてFail-closed。

**Codex Third Independent Review Probe A／B／C の再現・修正確認（本Document作成時点で実`GuardrailGovernanceComposition`に対して直接実行）**：
```
Probe 007-A（Detector Registry scope=foreign_scope, registered_detector_ids=(not.the.real.detector,)、実Detectorは本物のInput Detector群）
  → state=unavailable executed=[]（修正前: state=evaluated executed=[reject_input]）

Probe 007-B（Action Registry scope=foreign_scope, registered_action_ids=(warn,)、実registry/adaptersはreject_inputを含む）
  → state=unavailable executed=[]（修正前: state=evaluated executed=[reject_input]）

Probe 007-C（Entry Policy Snapshot revision=1、Policy Decision Stampがpolicy_revision=999/別Digestを自称）
  → state=unavailable executed=[]（修正前: state=evaluated executed=[reject_input]）
```

**Test**: [test_point_runtime.py](../../../../../tests/unit/guardrail_governance/test_point_runtime.py) — Direct Resolverではなく`GuardrailPointRuntime`経由でProbe A/B/C相当を再現する3 Test（`test_enforce_fails_closed_when_snapshot_scope_disagrees_with_the_rest`／`test_enforce_fails_closed_when_detector_registry_ids_disagree_with_real_detectors`／`test_enforce_fails_closed_when_action_registry_ids_disagree_with_real_registry`／`test_enforce_fails_closed_when_a_policy_decision_stamp_disagrees_with_the_snapshot`の4件）に加え、新しい検査自体が誤検知しないことを確認する正の対照Test（`test_enforce_succeeds_when_every_binding_component_genuinely_agrees`）を追加。

## P5-CODEX-008（Raw Label Decoderを正式Portが迂回できる）— Closed

**問題**：`SafetyModelPort.classify()`の返却型が依然`SafetyModelResponse`（Decode済み）だったため、Port適合Providerは`decode_safety_model_observation()`を一切通さず、完成済みの「信頼できる」Responseを直接返せた——Fake自身がDecoderへ回すよう自制していただけで、境界として強制されていなかった。

**修正**：
1. **`SafetyModelPort.classify()`の返却型を`RawSafetyModelObservation`（未検証の生Observation）へ変更**（[ports.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/ports.py)）——Port Contract自体がもはや`is_trustworthy`を持つ型を返せない。
2. **`SafetyModelDetectorAdapter`のみが`decode_safety_model_observation()`を呼ぶ唯一の場所**になるよう[safety_model_adapters.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py)を再設計。`DeterministicFakeSafetyModelAdapter`はもはやDecoderを自ら呼ばず、生Observationを返すだけ——実Providerと構造的に同じ形。
3. **任意のPort実装での迂回不能性を証明するTest追加**：`DeterministicFakeSafetyModelAdapter`を一切importしない、Protocolを構造的に満たすだけの独立クラス（`_HostileConformantProvider`）でCodexのProbeを再現。

**Codex Third Independent Review Probe の再現・修正確認（本Document作成時点で、Fakeを一切介さない独立Port実装に対して直接実行）**：
```
Input : failure=none, confidence=1.0, confidence_threshold=0.0,
        category_id=novel_unknown_label, outcome=clear
        （Fake Helper Classを一切importしない、Protocol構造適合のみの独立クラス）
Result: outcome=unknown, category=unknown_unresolved
```
修正前は`outcome=clear, category=novel_unknown_label`だったもの（Codex Third Review記載値）が、Port Contract自体の型変更によりDecoderを構造的に迂回不能となり、`unknown`へ収束している。

**5. Production Default Unavailable、Safety Model Call 0、Deterministic Detector優先の維持**：`UnavailableSafetyModelAdapter`は変更なく`SafetyModelUnavailable`を送出し続ける（返却型シグネチャのみ更新、挙動は不変）。Production Composition（`build_input_detectors()`/`build_output_detectors()`）が`SafetyModelDetectorAdapter`を含まないことを再確認するTestも維持。

**Test**: [test_safety_model_seam.py](../../../../../tests/unit/guardrail_governance/test_safety_model_seam.py)（全面改稿——全TestがBridge経由の`SafetyModelDetectorAdapter.detect()`結果を検証、直接`.classify()`のDecode済みFieldを検査する旧パターンを廃止；新規`test_an_arbitrary_port_conformant_provider_cannot_bypass_the_decoder`）、[test_policy_authority_approval_adapters.py](../../../../../tests/unit/guardrail_governance/test_policy_authority_approval_adapters.py)（Fakeの生Observation自体の決定性検査へ更新）。

## Exact Mutation（本Third Rework Cycleで変更・新規作成した全File）

**Source**:
- [src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py](../../../../../src/margpa_runtime_llm/adapters/model_backends/llama_cpp/adapter.py)（`supported_message_roles`へ`TOOL`追加）
- [src/margpa_runtime_llm/modules/documentation_rag/contracts.py](../../../../../src/margpa_runtime_llm/modules/documentation_rag/contracts.py)（`DocumentationReferenceBlock.source_class`追加）
- [src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py](../../../../../src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py)（`_context_source_items`をmodule-level化、`_PROMPT_ROLE_BY_SOURCE_CLASS`新設、`_inject_documentation_reference`をTOOL Role・Source Class駆動へ再設計）
- [src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/point_runtime.py)（Scope整合／実Detector-Action id集合Binding／Policy Decision Stamp Binding追加）
- [src/margpa_runtime_llm/modules/guardrail_governance/application/action_resolver.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/application/action_resolver.py)（`expected_scope`引数＋Approval Scope Fail-closed追加）
- [src/margpa_runtime_llm/modules/guardrail_governance/ports.py](../../../../../src/margpa_runtime_llm/modules/guardrail_governance/ports.py)（`SafetyModelPort.classify()`の返却型を`RawSafetyModelObservation`へ変更）
- [src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py)（Fakeが生Observationを返すのみへ変更、Bridgeのみが唯一のDecoder呼び出し元）

**Test**:
- [tests/unit/conversation/test_conversation_generation.py](../../../../../tests/unit/conversation/test_conversation_generation.py)（Role assertion更新＋実Native Dict確認Test追加）
- [tests/unit/guardrail_governance/test_point_runtime.py](../../../../../tests/unit/guardrail_governance/test_point_runtime.py)（既存Fixtureの内部整合性修正＋Probe A/B/C相当4 Test＋正の対照Test追加）
- [tests/unit/guardrail_governance/test_safety_model_seam.py](../../../../../tests/unit/guardrail_governance/test_safety_model_seam.py)（全面改稿、Bridge経由検証へ統一、任意Port実装Probe追加）
- [tests/unit/guardrail_governance/test_policy_authority_approval_adapters.py](../../../../../tests/unit/guardrail_governance/test_policy_authority_approval_adapters.py)（Fake検証を生Observation形へ更新）

**Documentation（新規）**:
- 本File自体（新規）

既存のStable Doc／既存History／既存Handoff（GOV-001・GOV-002訂正を含む）は1件も編集していない。P5-CODEX-009関連File（Stream Guard、Reasoning Channel等）は本Cycle中一切変更していない。

## Required Validation

| # | 項目 | Command | 結果 |
|---|------|---------|------|
| 1 | P5-CODEX-006/007/008 Exact Adversarial Probe | 上記3項の実測（本Document内） | 全て修正確認済み |
| 2 | Phase 5 Guardrail Focused Suite | `pytest tests/unit/guardrail_governance/` | 126 passed |
| 3 | RAG／Conversation／Web隣接回帰 | `pytest tests/integration/web/ tests/unit/conversation/ tests/integration/conversation/ tests/unit/documentation_rag/ tests/integration/documentation_rag/ tests/unit/inference/ tests/contract/` | 575 passed |
| 4 | Backend Full Suite（新規明示Path、既存Artifact削除なし） | `pytest --basetemp=.p5t/pfull2` | **1234 passed, 3 deselected**（61.77s） |
| 5 | Frontend test／typecheck／lint | `npm run test -- --run` / `npm run typecheck` / `npm run lint` | 175 passed（20 File）／Error 0／Error 0（UI非変更のためBuild再確認は必須外） |
| 6 | `ruff check .`／`ruff format --check .`（`.p5t/`除外） | `ruff check --extend-exclude .p5t .` / `ruff format --check --extend-exclude .p5t .` | All checks passed! ／ 320 files already formatted |
| 7 | Bare mypy | `mypy` | Success: no issues found in 320 source files |

`.p5t/`除外Flagの理由はP5-GOV-002方針（Test Artifact無許可削除禁止）により`.p5t/`配下に複数Basetempが残置されているため——第2回Reworkの`phase_5_claude_second_rework_complete_candidate_handoff_ja.md`item 10と同一の事情。

## 残置Test Artifact

`.p5t/`配下、本Document作成時点で以下が残置されている（いずれも削除していない）：
```
.p5t/p3a/      (第1次 conversation/documentation_rag/web/inference 回帰実行分)
.p5t/p3b/      (同上、Role修正後の再実行分)
.p5t/p3f/      (P5-CODEX-006/007統合後の回帰実行分)
.p5t/pf2/      (第2回Rework由来、既存残置分)
.p5t/pfull2/   (本Document用Backend Full Suite実行分)
.p5t/pv4/      (第2回Rework由来、既存残置分)
合計: 約33MB
```
削除するかどうかの判断はUserへ返す。

## 自己申告と独立検証の分離

- 本Document中のBackend Full Suite（1234 passed）／Frontend（175 passed）／ruff／mypy／各Adversarial Probe実測値：**REPOSITORY_STATE_VERIFIED**（Claude自身が本Session内で直接Command実行し観測。独立した第三者による再実行はまだ得ていない）。
- Codex Third Independent Review自身が記載したProbe結果（修正前の`state=evaluated executed=[reject_input]`等）：一次証拠はCodex自身のHandoffであり、本Documentはそれを引用・対比するのみ。
- Project Root外接触・Provider Memory・User実`runtime_data/`・Network・AWS/Lightning・Authority捏造：引き続き**SELF_REPORTED_UNVERIFIED**（独立したAction Log裏付けなし、P5-GOV-001/002訂正済み分類を継承）。
- `.p5t/`のCleanupは本Cycle中一切実行していない（P5-GOV-002確立の方針を遵守）。

## Next Action

Codex Independent Re-review待ちで停止する。Phase 5-H Closure、Phase 6開始、User Acceptance、DeepSeek Gate、いかなるGit操作も本Document作成後は一切行わない。`.p5t/`は削除せず残置し、削除するかどうかの判断はUserへ返す。
