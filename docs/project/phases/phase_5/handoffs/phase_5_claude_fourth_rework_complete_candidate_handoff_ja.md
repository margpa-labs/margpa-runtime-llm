# Phase 5 Claude Fourth Rework Complete Candidate Handoff

```yaml
document_id: phase_5_claude_fourth_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_5
subphase: phase_5_h_rework_4
role: Claude側設計統括者役
provider: claude_code
predecessor: docs/project/phases/phase_5/handoffs/phase_5_codex_fourth_independent_review_rework_handoff_ja_20260822192740.md
superseded_completion: docs/project/phases/phase_5/handoffs/phase_5_claude_third_rework_complete_candidate_handoff_ja.md（Stable、変更なし）
recorded_at: 2026-08-22 19:34:14 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行）
long_running_mode_active: true
next_action: Codex再確認待ちのみ。Phase 5-H Closure／Phase 6／Git操作は一切行わない。
residual_test_artifacts_left_in_place: .p5t/（p3a/, p3b/, p3f/, pf2/, pfull2/, pv4/ の6件、合計約33MB。本Rework Cycleの単体Test実行はいずれも新規Artifactを生成していない。削除判断はUserへ返す）
```

本Documentは`phase_5_codex_fourth_independent_review_rework_handoff_ja_20260822192740.md`が要求した最小Exact Rework（P5-CODEX-008の1件、Malformed Provider Return）のClosure Evidenceである。User指示通り、**P5-CODEX-006／007／009およびP5-GOV-002は再Openしていない**——本Rework Cycleでは`safety_model_adapters.py`とその対応Testのみを変更し、RAG Role設計・Snapshot Binding設計には一切触れていない。既存のStable Handoff／既存History Fileも一切書き換えていない。

## Closure Summary

```text
P5-CODEX-006 : CLOSED（再Openしない、User指示通り）
P5-CODEX-007 : CLOSED（再Openしない、User指示通り）
P5-CODEX-008 : CLOSED（本Reworkにより完全Close）
P5-CODEX-009 : CLOSED（再Openしない、User指示通り）
P5-GOV-002   : CLOSED（再Openしない、User指示通り）
Open Major Finding: 0
```

## P5-CODEX-008 残存事項（Malformed Provider ReturnがDecoder境界から例外漏洩する）— Closed

**問題**：`SafetyModelPort.classify()`の戻り値型注釈は第3回Reworkで`RawSafetyModelObservation`へ修正済みだったが、Pythonの`Protocol`／型注釈はRuntimeで戻り値の実際の型を強制しない。`SafetyModelDetectorAdapter.detect()`の`try/except`は`self._safety_model.classify()`の呼び出しだけを囲んでおり、続く`decode_safety_model_observation(observation, ...)`の呼び出しは`try`ブロックの外にあった。そのため、`classify()`が壊れたReturn（例：`object()`、または誤って旧`SafetyModelResponse`をそのまま返す）をした場合、Decoder内部で`observation.timed_out`／`observation.claimed_failure`等へアクセスした瞬間に`AttributeError`がBridge外へ漏洩していた。

**修正**（[safety_model_adapters.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py)）：`SafetyModelDetectorAdapter.detect()`の`try`ブロックを、`self._safety_model.classify(...)`の呼び出しと`decode_safety_model_observation(...)`の呼び出しの両方を囲むよう拡張した。`SafetyModelUnavailable`は従来どおり最初に捕捉して`UNAVAILABLE`へ、それ以外の例外（Decoder内部で発生するものを含む）は`ERROR`へ収束する——例外の発生源が`classify()`自体かDecoder処理かを区別する必要がなくなり、Bridge全体が単一のFail-closed境界になった。

**Codex Fourth Independent Review Probe の再現・修正確認（本Document作成時点で直接実行）**：
```
Provider return : object()
修正前          : AttributeError escaped（Bridge外へ例外が漏洩）
修正後          : outcome=error, category=unknown_unresolved
```

**Required Minimal Rework 5項目への対応**：
1. ✅ `detect()`のFail-closed境界を、Provider CallとDecoder処理全体を覆うよう拡張。
2. ✅ Malformed返却（`object()`）、旧`SafetyModelResponse`返却、Decoder例外を、いずれも例外漏洩ではなくTyped `DetectionOutcome.ERROR`へ収束させることを確認。
3. ✅ `SafetyModelUnavailable`は従来どおり`UNAVAILABLE`として区別されることを維持（`except SafetyModelUnavailable`を`except Exception`より先に配置）。
4. ✅ Unknown Raw Labelは従来どおり`UNKNOWN`、Known／Trustworthy Matchは従来どおり`MATCH`を維持することを既存Test（`test_unknown_raw_category_label_is_independently_rejected_by_the_decoder`／`test_a_known_registered_category_is_not_flagged_as_unknown_label`）で再確認。
5. ✅ 実経路Test追加（下記）。

## Exact Mutation

**Source**:
- [src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py](../../../../../src/margpa_runtime_llm/adapters/guardrail_governance/safety_model_adapters.py) — `SafetyModelDetectorAdapter.detect()`の`try`ブロックを`decode_safety_model_observation(...)`呼び出しまで拡張。Class Docstringを更新。

**Test**:
- [tests/unit/guardrail_governance/test_safety_model_seam.py](../../../../../tests/unit/guardrail_governance/test_safety_model_seam.py) — 新規2 Test追加：
  - `test_a_malformed_return_of_a_bare_object_fails_closed_through_the_decoder`（Codex Probe完全再現：`classify()`が`object()`を返す）
  - `test_a_malformed_return_of_a_stale_decoded_response_fails_closed_through_the_decoder`（`classify()`が旧Decode済み`SafetyModelResponse`を返す）
  - 既存の`test_a_raising_safety_model_fails_closed_through_the_bridge_not_silently`（`classify()`自体が例外を送出）、`test_unknown_raw_category_label_is_independently_rejected_by_the_decoder`／`test_a_known_registered_category_is_not_flagged_as_unknown_label`（Unknown Raw Label→UNKNOWN、Known Category→MATCHの正の回帰）は変更なく維持——Required Rework item 5の残り2条件は既存Testが既にCoverしていることを確認した。

他File（RAG Role、Snapshot Binding、Stream Guard、GOV-002関連）は本Rework Cycle中一切変更していない。

## Focused Validation

| # | 項目 | Command | 結果 |
|---|------|---------|------|
| 1 | Malformed Return Matrix（Probe再現） | 本Document内の直接実行 | `object()` Return → `outcome=error`（修正前: AttributeError escaped） |
| 2 | `test_safety_model_seam.py` | `pytest tests/unit/guardrail_governance/test_safety_model_seam.py` | 14 passed |
| 3 | Phase 5 Guardrail Focused Suite | `pytest tests/unit/guardrail_governance/` | 128 passed |
| 4 | 変更FileへのRuff／Mypy | `ruff format`／`ruff check`（両File指定）／`mypy`（Project全体） | 全てPASS（`mypy`: Success, no issues found in 320 source files） |

Handoff指示通り、Full Suiteの再実行は行っていない（Codex側が「必須にしない」と明示したため）。本Rework Cycleの全Test実行はいずれも`tmp_path`を要するTestを含まなかったため、`.p5t/`へ新規Artifactは生成していない——既存の残置分（`p3a/, p3b/, p3f/, pf2/, pfull2/, pv4/`、計約33MB、第2回・第3回Rework由来）のみが引き続き残置されている。Cleanupは一切実行していない。

## Next Action

Codex Independent Re-confirmation待ちで停止する。Phase 5-H Closure、Phase 6開始、User Acceptance、DeepSeek Gate、いかなるGit操作も本Document作成後は一切行わない。
