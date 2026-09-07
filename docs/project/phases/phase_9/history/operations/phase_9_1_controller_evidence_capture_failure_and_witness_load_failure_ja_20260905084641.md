# Phase 9-1 — 実32 Criterion Evidence取得Failure Controller Review

```yaml
document_type: controller_independent_review
document_state: blocked_on_clean_runtime_recheck
recorded_at: 2026-09-05 08:46:41 JST
language: ja
reviewer: codex_controller
phase_9_1_closure: false
```

## 1. 判定

`PARTIAL ACCEPT / REAL EVIDENCE STILL INCOMPLETE`。

次は受理する。

- Test-only Observability実装
- Candidate 400／局所Budget 2799による正確な1 Token不足Test
- Production Budget 2800維持
- `outcome=unknown`からDecoder Failureを断定しないSource／Claim訂正

Controller再確認はUnit 38 passed、対象Ruff clean。Production Source／Testへの追加変更は行っていない。

## 2. Claude検証手続きFailure

Claudeは原因分離用の診断出力を実装した後、唯一許可された実機Runを`2>&1 | tail -100`で実行した。失敗Traceback後半だけが残り、診断Markerの実測行が捨てられた。

Claude Session JSONLの該当Tool Resultまで確認したが、残っていたMarkerはTraceback内に表示されたSource行だけであり、Raw Digest／Finish Reason／Token／Strict Decode結果の実測値は復元できなかった。

これはModelのFailureではなく、Evidenceを取得する作業自身がEvidenceを破棄した手続きFailureである。2回目Runは`outcome=unknown`再現の参考にはなるが、目的だったDecoder FAILEDとCOMPLETED＋Criterion UNKNOWNの分離には使用できない。

## 3. Controller Witness

Claudeへ直ちに再委任せず、Controller Witnessとして同一Testを一時Logへ切り詰めず保存する形で1回実行した。

結果はInference以前のMain Qwen Loadで失敗した。

```text
ValueError: Failed to create llama_context
InferenceErrorCode: model_load_failed
model_key: main.qwen3-4b-q4-k-m
elapsed: 3.94s
```

Gemma Load、Repair、Rejudge、診断Decodeには到達していないため、Gemma 32 Criterionの成功／失敗回数には数えない。一時Logは`/private/tmp/phase9_gemma32_controller_witness_202609050845.log`。Source変更なし。

実行後の`memory_pressure -Q`はSystem-wide memory free 81%だったが、この値だけでMetal／既存Process／Native Context状態の原因は断定しない。Process一覧確認はSandboxに拒否された。勝手なProcess停止や再試行は行っていない。

## 4. Current Disposition

- Budget／Unit／Observability Code: ACCEPT。
- 実Gemma 32 Criterion成立: INCOMPLETE。
- 原因分離Evidence: INCOMPLETE。
- 次の実機Runは、MARGPA Server等のModel保持Processが停止し、Clean RuntimeであることをUserと確認してから行う。
- 次回は`tee`で完全Logを保存し、終了後にMarker行の存在を確認してから報告する。`tail`単独使用は禁止。
- JSON Retry、Decoder緩和、Criterion削減、予算追加、Selene着手は行わない。

## 5. Process追確認

Userから「ClaudeがServerを止め忘れた可能性」が示されたため、権限付きRead-only確認を追加した。

- `uvicorn`／`margpa_runtime_llm`／Python／pytest／llama Process: 該当なし
- MARGPAらしいTCP LISTEN: 該当なし
- Claude本体Process: 稼働中。ただしRSS約254 MBで、別Python／llama Childは確認されない
- Codexの`app-server` Process: 稼働中。これはCodex Desktop自身のBackendであり、MARGPA Serverではない

よって、確認時点で「ClaudeがMARGPA Serverを残した」とは立証されない。Controller Witness時点だけ一時的に存在して終了した可能性までは否定できないが、現在Evidenceはない。Mainの`llama_context`作成失敗は、忘れられたServerを原因と断定せず、Native／Metal Context作成の一時的Failureとして未確定を維持する。
