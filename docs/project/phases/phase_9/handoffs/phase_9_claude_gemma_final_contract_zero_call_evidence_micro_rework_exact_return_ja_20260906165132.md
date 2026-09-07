# Phase 9-1 — Gemma Final Contract: Model Call 0 Evidence Micro Rework Exact Return

```yaml
document_id: phase_9_claude_gemma_final_contract_zero_call_evidence_micro_rework_exact_return_20260906165132
document_type: exact_return_handoff
document_state: ready
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-06 16:51:32 JST
language: ja
from: claude_code
to: codex_controller
decision_authority: user
authority_owner: Nazuna Research
in_response_to: phase_9_controller_gemma_final_contract_zero_call_evidence_micro_rework_exact_handoff_ja_20260906133525.md
phase_9_1_closure_authorized: false
git_write: none
append_only: true
```

## 1. 最大Claim

`P9_1_GEMMA_FINAL_CONTRACT_ZERO_CALL_EVIDENCE_MICRO_REWORK_READY_FOR_INDEPENDENT_REVIEW`

Codex Controller Independent Reviewが指摘した最後の1件(IR-FC-04: Model Call 0時のPrompt Digest誤記録)を修正した。修正はDedicated batched経路のModel-Call-0分岐のみに閉じており、通常batched経路(Batch>=1)・非batched既存Caller・Model Call・Judge判定・Repair・Constrained Decoding・Provider Lifecycleへの影響はゼロであることを機械的に確認した。Phase 9-1 ClosureはCodex Controller/User側の判断であり、本Returnは主張しない。

## 2. 対象範囲(Scope Boundary遵守の確認)

- 変更はIR-FC-04(Model Call 0時の`prompt_digest_sha512`誤記録)のみ。Retry・Seed変更・Decoder・Schema・Prompt・Sampling・Budget・Contextへの変更なし。
- Gemma/Selene/Qwen/Guardの実機試験は一切行っていない。実機Golden Path・Server起動も行っていない(Handoffが明示的に禁止)。
- UI・Phase 9-2/9-3・Phase 10への拡張なし。
- Git write操作(`add`/`commit`/`push`/`stash`/`reset`)は一切実行していない。実行したGit操作は`git status --porcelain`(読み取り専用の状態確認)のみ。
- 既存Docsは無編集。本Returnと対になるRecovery Indexは、いずれも新規Pathで作成する。
- 非Model Full Suiteの再実行は行っていない(Handoffが「このEvidence 1点のためには不要」と明記)。

## 3. IR-FC-04 — Model Call 0時のPrompt Digest誤記録(Before/After)

### Finding(再掲)

Dedicated batched経路(`_run_selene_dispatch()`)でBatchが0件の場合、`_batch_dispatch_prompt_digest_sha512(())`は`None`を返していた。`None`はRecording層(`recording_live_integration.py`の`record_judge_evidence()`)で「Overrideなし」と解釈され、実際のModel Promptではない固定説明文`(dedicated Selene evaluator: prompt built internally by SelenePromptAdapter)`のSHA-512が`prompt_digest_sha512`として保存されていた。`call_count=0`でModel Callも実Promptも存在しないEvidenceに、正規のPrompt Digestらしい128桁値が残る、という問題。

### Before

[judge_live_integration.py](../../../../../src/margpa_runtime_llm/bootstrap/judge_live_integration.py)の`_batch_dispatch_prompt_digest_sha512()`:

```python
def _batch_dispatch_prompt_digest_sha512(
    batch_evidence: tuple[BatchDispatchEvidence, ...],
) -> str | None:
    if not batch_evidence:
        return None
    joined = "".join(item.prompt_digest_sha512 for item in batch_evidence)
    return hashlib.sha512(joined.encode("utf-8")).hexdigest()
```

`batch_evidence`が空Tupleの場合の`None`が、呼び出し元(`_finalize_judge_dispatch()`→`_pending_evidence()`→`record_judge_evidence()`)を通じて「Override未指定、`prompt`引数(固定説明文)をhashせよ」という既存Fallbackを誤って起動させていた。

### After

同関数の空Tuple分岐のみを変更し、`None`ではなく既存Metadata契約(`config_digest_sha512 or "unavailable"`等、同じ`record_judge_evidence()`内で既に使われている「真に不明な値には固定文字列`"unavailable"`」規約)に揃えた文字列`"unavailable"`を返すよう修正した。戻り値型も実態に合わせ`str | None`から`str`へ変更(空Tupleでも常に文字列を返すため)。

```python
def _batch_dispatch_prompt_digest_sha512(
    batch_evidence: tuple[BatchDispatchEvidence, ...],
) -> str:
    if not batch_evidence:
        return "unavailable"
    joined = "".join(item.prompt_digest_sha512 for item in batch_evidence)
    return hashlib.sha512(joined.encode("utf-8")).hexdigest()
```

`"unavailable"`は`None`ではないため、`record_judge_evidence()`のOverride判定(`prompt_digest_sha512_override if ... is not None else hashlib.sha512(prompt...)`)を経て、Fallbackのhash計算を経由せずそのまま`prompt_digest_sha512`へ記録される。呼び出し元(`_run_selene_dispatch()`)・`_finalize_judge_dispatch()`・`_pending_evidence()`・`record_judge_evidence()`のシグネチャ/呼び出し規約は一切変更していない。

実Batchが1件以上ある場合(通常batched経路)は、既存の集約Hash計算(`joined`のSHA-512)がそのまま維持される。非batched既存Caller(Main-selfの汎用品質Dispatch)はこの関数を一切呼んでおらず、`prompt_digest_sha512_override`引数自体を渡さない(Default`None`)ため、「渡された実Promptをhashする」既存挙動は無変更。

## 4. Required Test(Handoff §2)との対応

Handoffが列挙した5点は、いずれも今Roundで直接確認した(下記5節)。

- `call_count == 0`: 既存Test(`test_selene_shaped_dispatch_with_zero_batch_calls_records_evidence_call_count_zero`、IR-FC-03で追加済み)がすでに確認済み、無変更で継続Pass。
- `prompt_digest_sha512 == "unavailable"`: 新規Test 2件で確認(5節)。
- `seed_pinned is False` / `seed == "unpinned"`: 既存Test(上記と同じ)がすでに確認済み(`seed`引数`None`→Recorder内で`seed_pinned=False`/`seed="unpinned"`に変換)、無変更で継続Pass。
- `batch_evidence_json`なし: 既存Test(上記と同じ)がすでに確認済み、無変更で継続Pass。

## 5. 証明

- **`test_judge_evidence_records_prompt_digest_unavailable_on_model_call_zero`(新規、[test_recording_live_integration.py](../../../../../tests/unit/bootstrap/test_recording_live_integration.py))**: Handoffが明示的に要求した「実`build_judge_evidence_recorder()`まで通す確定的Test」。`build_judge_evidence_recorder()`が返す実`record_judge_evidence`を、Model-Call-0の形(`call_count=0`, `seed=None`, `prompt_digest_sha512_override="unavailable"`, `batch_evidence_json=None`, `prompt=`固定説明文)で直接呼び出し、実際にDiskへ書き出されたJSON Fileの`metadata_fields`を読み取って`call_count==0`/`seed_pinned is False`/`seed=="unpinned"`/`prompt_digest_sha512=="unavailable"`/`"batch_evidence_json" not in fields`を確認。
- **`test_selene_shaped_dispatch_with_zero_batch_calls_records_evidence_call_count_zero`への追加Assert([test_judge_live_integration_dispatch_router.py](../../../../../tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py))**: IR-FC-03で追加済みの全Deferred(Model Call 0)Fixtureに`assert evidence_calls[0]["prompt_digest_sha512_override"] == "unavailable"`を追加し、`_run_selene_dispatch()`自体が実際に`"unavailable"`をRecorderへ渡していることを確認(Judge dispatch router層でのFocused Test)。
- **通常batched経路(Batch=4)が無変更であることの確認([test_production_composition_root_32_criterion_gemma_enforce_golden_path.py](../../../../../tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py))**: 実`build_judge_evidence_recorder()`経由の既存Fixture Golden Path(`call_count==4`)に`assert judge_evidence["prompt_digest_sha512"] != "unavailable"`と`assert len(str(judge_evidence["prompt_digest_sha512"])) == 128`を追加し、実Batch>=1経路のPrompt Digestが今回の修正で変化していないことを確認。
- **非batched既存Callerの無変更確認**: `test_judge_evidence_records_default_call_count_and_unpinned_seed_when_caller_omits_them`(既存、無変更)が`record_judge_evidence()`をOverride未指定(`prompt_digest_sha512_override`省略)で呼び、実Prompt文字列のhashが`prompt_digest_sha512`へ記録されること(Fallback経路自体は無変更)を引き続き確認しており、継続Pass。
- **Sabotage-regression**: `_batch_dispatch_prompt_digest_sha512()`の空Tuple分岐を`return None`(元のBug)へ戻す→`test_selene_shaped_dispatch_with_zero_batch_calls_records_evidence_call_count_zero`が`assert None == "unavailable"`で失敗することを確認(新規Assert箇所が検出力を持つことを確認)。復元後、`diff`でBackupとByte一致を確認。

### Test実行結果

```
tests/unit/bootstrap/test_recording_live_integration.py
tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py
tests/unit/bootstrap/test_judge_live_integration.py
tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py
-> 88 passed in 7.75s(修正後、Sabotage復元後の最終実行)
```

### Ruff / Mypy(変更File)

```
ruff check src/margpa_runtime_llm/bootstrap/judge_live_integration.py \
  tests/unit/bootstrap/test_recording_live_integration.py \
  tests/unit/bootstrap/test_judge_live_integration_dispatch_router.py \
  tests/unit/bootstrap/test_production_composition_root_32_criterion_gemma_enforce_golden_path.py
-> All checks passed!

mypy src tests
-> Found 43 errors in 4 files
```

Canonical Mypy Baseline(既存4File、`tests/unit/guardrail_governance/test_point_runtime.py`、`tests/integration/conversation/test_conversation_generation_guardrail_stream_integration.py`、`tests/unit/guardrail_governance/test_stream_guard.py`、`src/margpa_runtime_llm/bootstrap/judge_live_integration.py:631`)と完全一致。新規Error 0件。

## 6. 実モデル/実機/Server(不実施の確認)

Handoff §3「実モデル、実機Golden Path、Server起動は不要かつ禁止」に従い、本Roundでは一切実行していない。前Round(2つ前のRound)で確認済みの実機Golden Path 2回分(`repair_rejudge_provider='judge.gemma-4-e2b-it-q4-0'`成立、Rejudge Sampling直接確認済み)は、いずれもIR-FC-04のScope外(Prompt Digest Metadataは実機Evidenceの他Fieldに影響しない、`call_count`/`seed`等の実機挙動は本Roundで変更していない)であり、再確認は行っていない。

## 7. 未解決事項(Open Findings、変更なし)

前Return(`phase_9_claude_gemma_constrained_decoding_final_contract_micro_rework_exact_return_ja_20260906131256.md`)およびAddendum(`..._addendum_real_hardware_rejudge_sampling_confirmation_ja_20260906132919.md`)からの引き継ぎ。本Roundで変更していない。

1. Rejudge Samplingの実機独立計装: 前AddendumでUser許可の下、実機直接確認済み(解消済み)。
2. `criteria_evaluated`のUnknown 1件判定理由: 引き続き今Round未調査(Handoffの明示指示どおり、Scope外)。
3. Memory(Process RSS)定量計測: 引き続き今Round未実施(Handoffの明示指示どおり、Scope外)。
4. 他5箇所の既存実機Test(Trial A/B以外): 本Roundも未更新・未実行。
5. R2-WU-05のGuard: 本Roundも再確認していない。

## 8. Git

`git add`/`commit`/`push`/`stash`/`reset`は一切実行していない。実行したGit操作は`git status --porcelain`(状態確認のみ、書き込みなし)。

## 9. Next Step

Codex Controller Independent Reviewを待つ。Phase 9-1 Closure、User Acceptance、次Phase着手、追加の実機Trial、Selene実機実行、Guard修正・実機再試行、JSON Retry/Seed変更/Decoder緩和/JSON補修/部分採用、Main Context/Repair Budget/Criterion上限の変更のいずれも行わない。本Returnで停止する。
