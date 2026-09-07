# Phase 9-1 — 実32 Criterion完全Log取得 Execution-only Handoff

```yaml
document_type: exact_execution_handoff
document_state: ready
recorded_at: 2026-09-05 08:54:47 JST
language: ja
from: codex_controller
to: claude_designer_implementer
maximum_claim: P9_1_REAL_32_CRITERION_COMPLETE_LOG_CAPTURE_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. Current State

Budget 2800、Unit 38 passed、2799／Candidate 400境界、Test-only Observability実装はController受理済み。Claudeの前回Runは`tail -100`が診断行を捨てたためEvidence無効。Controller WitnessはMain Qwen Loadで停止し、Gemma／Rejudge未到達だった。

今回の目的はSource修復ではなく、既存Testの完全Logを確実に保存し、実Gemma 32 CriterionのFailure形状を一意に取得することだけである。

## 2. Preflight

- MARGPA Server、別pytest／Python／llama Process、MARGPA待受Portが残っていないことをRead-only確認する。
- 残存している場合は停止・Killせず、PID／Commandだけ報告してTrue Stopとする。
- Claude本体、Codex Desktopの`app-server`はMARGPA Serverと誤認しない。
- Preflightに問題がなければ次へ進む。追加のUser確認は不要。

## 3. 許可する唯一の実行

既存Testを同一条件で1回だけ実行する。出力は`tail`へ渡さず、Task専用の`/private/tmp/phase9_gemma32_claude_complete_capture_20260905085447.log`へ`tee`で完全保存する。Pipelineのpytest終了Codeを保持する。

対象:

```text
tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py::test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget
```

実行直後、Log Fileから次をRead-only抽出する。

- `[real-32-criterion-rejudge-evidence]` Marker行
- pytestのPASS／FAILと実行時間
- Main／Gemma Load Failureがある場合はそのTyped Code／Exception

Marker行が存在する場合、finish reason、Token、時間、Raw Digest、Strict Decode State／Reason、Recommendation、pass／deviation／unknown、missing／extra IDをReturnへ転記する。Raw Content全文は転記しない。

Markerが存在しない場合は、どのStage以前で停止したかをLogで確定し、再実行せず返す。

## 4. 禁止事項

- Source／Test／Configの編集
- 同一Testの反復
- `tail`によるLog切捨て
- Process Kill／Server操作
- JSON Retry、Decoder／Schema／Budget／Criterion変更
- Selene、Frontend、Phase 9-2／9-3、Closure、Git操作
- 変更がないのにFull Suite／Mypy／Ruffを再実行すること
- 広範なCanonical Docs再読込

## 5. Review／Return

Internal Reviewは、①Command／完全Log／Marker取得の手続き整合、②実測値とClaimの意味整合、の2観点だけを行う。Test再実行はしない。

新規PathのExact ReturnとRecoveryを作成し、完全Logの絶対PathとSHA-512を記録する。既存Docs／Phase Index／Registryは編集せず、Controller Review待ちで停止する。

