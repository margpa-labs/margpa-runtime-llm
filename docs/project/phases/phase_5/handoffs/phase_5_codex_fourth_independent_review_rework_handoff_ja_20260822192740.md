# Phase 5 Codex 第4回独立Review／最小Exact Rework Handoff

## 1. Routing

- From：プロジェクト責任者兼設計統括者役（Codex側）
- To：Claude側 設計統括者役
- Review入力：`docs/project/phases/phase_5/handoffs/phase_5_claude_third_rework_complete_candidate_handoff_ja.md`
- Automation：OFF
- Phase 5-H：本件修正後のCodex再確認まで開始禁止
- Git Mutation：禁止

## 2. 判定

```text
P5-CODEX-006 : CLOSED
P5-CODEX-007 : CLOSED
P5-CODEX-008 : PARTIAL／1件のみ最小Rework
P5-CODEX-009 : CLOSED（再Openしない）
P5-GOV-002   : CLOSED（再Openしない）
```

第3回Reworkにより、次は独立Probeでも成立した。

```text
Detector Registry mismatch : unavailable／Action 0
Action Registry mismatch   : unavailable／Action 0
Policy Decision mismatch   : unavailable／Action 0
Unknown Raw Label          : unknown／unknown_unresolved
```

RAG Sourceも`TOOL` Roleへ分離され、`SYSTEM`／`USER`と同一のNominal Authorityではなくなった。実GGUF Chat TemplateでのRAG動作確認はPhase 5-H User Mac Acceptance Gateへ正しく残す。ここでは再設計しない。

## 3. Remaining Major Finding — Malformed Provider ReturnがDecoder境界から例外漏洩する

### 3.1 独立Probe

`SafetyModelPort.classify()`の型注釈は`RawSafetyModelObservation`へ修正された。しかしPythonのProtocol／return annotationはRuntimeで返却型を強制しない。

Port実装が、壊れたProvider Responseとして`object()`を返すProbeを実行した。

```text
Provider return : object()
Expected        : typed ERROR／UNKNOWNへFail-closed
Actual          : AttributeError escaped
```

### 3.2 原因

`SafetyModelDetectorAdapter.detect()`の`try/except`は`self._safety_model.classify()`だけを囲んでいる。`decode_safety_model_observation(observation, ...)`は`try`の外にあるため、返却型不正、Field欠落、Decoder内部Validation Errorその他のMalformed ResponseがBridge外へ漏れる。

現在の`test_malformed_response_failure_never_converts_to_clear`は、正しく構築済みの`RawSafetyModelObservation`へProvider自身が`claimed_failure=MALFORMED_RESPONSE`を設定するTestであり、実際にMalformedな返却物をDecoder境界へ渡すTestではない。

これは既存のP5-CODEX-008／P5-RES-005に含まれる「Malformed ResponseをSafe Allowにせず、Typed FailureへFail-closedする」条件そのものであり、新規Scopeではない。

## 4. Required Minimal Rework

1. `SafetyModelDetectorAdapter.detect()`で、Provider CallだけでなくRaw Observationの型／Decoder処理全体をFail-closed境界内へ置く。
2. Malformed返却、Field欠落、旧`SafetyModelResponse`返却、Decoder例外を、例外漏洩ではなくTyped `DetectionOutcome.ERROR`または同等の安全側結果へ収束させる。
3. `SafetyModelUnavailable`は従来どおり`UNAVAILABLE`として区別する。
4. Unknown Raw Labelは従来どおり`UNKNOWN`、Known／Trustworthy Matchは従来どおり`MATCH`を維持する。
5. 次の実経路Testを追加する。
   - `classify()`が`object()`を返す
   - `classify()`が旧Decode済み`SafetyModelResponse`を返す
   - `classify()`自体が例外を送出する
   - Unknown Raw Labelが`UNKNOWN`になる正の回帰

## 5. Exact Scope

### Allowed

- `src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py`
- `tests/unit/guardrail_governance/test_safety_model_seam.py`
- 必要な場合のみ、上記境界の型を壊さず修正する最小のPhase 5 Safety Model Source／Test
- 新規Append-only Completion Handoff 1件

### Forbidden

- P5-CODEX-006／007／009、P5-GOV-002の再設計／再Open
- RAG Role／Snapshot設計の追加変更
- Phase 5-H Closure、Phase 6開始
- Project Root外接触、Provider Memory、User実`runtime_data/`
- 既存`.p5t/`／`.t/`／`.pytest_cache/`の削除・移動・Cleanup
- Git操作、Network、AWS、Lightning、Model Load／Download
- 既存Stable／History／Handoffの上書き

## 6. Validation／Return

Full Suiteの再実行は必須にしない。次で十分とする。

```text
1. 上記Malformed Return Matrix
2. tests/unit/guardrail_governance/test_safety_model_seam.py
3. Phase 5 Guardrail Focused Suite
4. 変更FileへのRuff／Mypy
```

完了時は新規Append-only HandoffへExact Mutation、Probe入出力、Focused Validation、作成Artifact Pathを記録して停止し、Codex再確認を待つこと。
