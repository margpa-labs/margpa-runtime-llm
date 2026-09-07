# Phase 9-1 — 実32 Criterion完全Log取得 Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../handoffs/phase_9_controller_real_32_criterion_complete_log_capture_execution_only_handoff_ja_20260905085447.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 08:59:35 JST
```

## 1. Maximum Claim

`P9_1_REAL_32_CRITERION_DECODER_FAILURE_ROOT_CAUSE_DISAMBIGUATED_NO_FIX_APPLIED`

**主張すること**:
- Preflight(§2)をRead-onlyで実施し、MARGPA Server・別pytest/Python/llama Process・MARGPA待受Port(8000)のいずれも残存していないことを確認した。Killは発生していない(対象が存在しなかったため)。
- 許可された唯一の実行(§3)を実施した: 指定Testを正確に1回、`tail`を経由せず`tee`で指定Logへ完全保存し、pytestの終了Codeを保持した。
- Log Fileから`[real-32-criterion-rejudge-evidence]` Markerを確認し、その実測値を本Returnへ転記した(Raw Content全文は転記していない)。
- **今回のMarkerにより、「Decoder FAILEDかDecoder COMPLETED+Criterion UNKNOWNか」を初めて実機Evidenceで一意に確定できた: 今回はDecoder FAILED(Strict Decode `execution_state='failed'`)であり、原因は`finish_reason=LENGTH`かつ`completion_tokens`がRejudge Planの上限(2400)ちょうどに達していること——実Gemma応答がToken上限で途中終端(Truncate)され、不完全なJSONとしてDecodeに失敗したことに一致する。**

**主張しないこと(明示的除外)**:
- Source修復は行っていない。本Handoffの目的どおり、原因分離のEvidence取得のみを行った。
- この1回の結果を「Gemmaが32 Criterionを構造的に処理できない」という一般化された結論として主張しない——`finish_reason=LENGTH`という具体的な観測事実と、それに一致するDecode失敗理由のみを報告する。
- 今回の結果は同一条件下での1回の実機観測であり、反復・追加試行は行っていない(禁止事項どおり)。
- Selene解決、Phase 9-1 Closure、Decoder/Budget/Criterion変更は主張・実施していない。

## 2. 対象

[Codex Controller Execution-only Handoff(2026-09-05 08:54:47 JST)](../handoffs/phase_9_controller_real_32_criterion_complete_log_capture_execution_only_handoff_ja_20260905085447.md)、§2(Preflight)・§3(許可された唯一の実行)全項目。

## 3. Files Changed

**なし。** 本Handoffの指示どおり、Source／Test／Configは一切編集していない。

## 4. Preflight結果(§2、Read-only)

```text
[FACT] `ps aux | grep -iE "python|pytest|llama|uvicorn|margpa"` → 該当なし
       (出力ゼロ行)。
[FACT] `lsof -nP -iTCP:8000` → 該当なし(MARGPA Serverの既定Port
       8000にListenしているProcessなし)。
[FACT] `lsof -nP -iTCP -sTCP:LISTEN` の全体スキャンでも、rapportd・
       ControlCenter・GarageBandといったmacOS標準/User Applicationの
       Port(49152、7000、5000、50893)のみで、MARGPA関連・Python関連の
       LISTENは皆無だった。
[FACT] `ps -eo pid,ppid,command | grep -iE "gguf|qwen|gemma|margpa_runtime"`
       → 該当なし(Model Load済みの残存Processなし)。
```

Claude本体・Codex Desktopの`app-server`をMARGPA Serverと誤認する事態も発生しなかった(そもそも該当するCommand文字列を持つProcessが一件も存在しなかった)。残存が一件もなかったため、Kill操作は発生せず、そのままStep 3へ進んだ。

## 5. 実行(§3)

```text
[FACT] 実行Command:
       cd <project_root>
       set -o pipefail
       ./.venv/bin/python -m pytest \
         "tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py::\
test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget" \
         -q -m model_smoke -s 2>&1 \
         | tee /private/tmp/phase9_gemma32_claude_complete_capture_20260905085447.log
       echo "PYTEST_EXIT_CODE=$?"
[FACT] pytest終了Code: 1(pipefail経由で保持、tee自体の終了Codeではない)。
[FACT] pytest結果行: "1 failed in 75.14s (0:01:15)"。
[FACT] 完全Log絶対Path: /private/tmp/phase9_gemma32_claude_complete_capture_20260905085447.log
[FACT] 完全Log SHA-512:
       1c8bba6f8fd9bfc0721f4991b5fbe494574adae5fc30040156e08e40b140efd
       13b1aa7ab3feec82e792788797099aca9fbb7c032c4e1d9d3e28c2d8f3352f277
[FACT] 完全Logサイズ: 12677 bytes、187行。
[FACT] `[real-32-criterion-rejudge-evidence]` Marker: Log内に実出力として
       1件確認(4行目)。もう1件(140行目)はpytestが失敗Traceback内で
       表示したTest自身のSource Code文字列であり、実行結果の重複出力
       ではない(Grep結果とLog原文で確認済み)。
[FACT] Main/Gemma Load Failureの兆候(InferenceError、MODEL_NOT_LOADED、
       Model Load関連のTraceback等)はLog内に一件もなかった——両Model
       とも正常にLoadされ、実Generateまで到達している。
```

### 5.1 Marker実測値の転記(Raw Content全文は転記しない)

| 項目 | 値 |
|---|---|
| `result_outcome` | `'unknown'` |
| `result_accepted` | `False` |
| `result_rejected_reason` | `None`(事前Typed拒否ではなく、事後Rejudge評価Decode後の未Accept経路) |
| Rejudge Requestの`max_new_tokens` | `2400` |
| `finish_reason` | `<FinishReason.LENGTH: 'length'>` — Token上限到達による打ち切り |
| Prompt Token | `3612` |
| Completion Token | `2400`(Plan上限2400ちょうど——実応答がToken上限まで生成され続けたことを示す) |
| 生成時間 | `64.05919679200451`秒(elapsed_ms=64608) |
| Raw Content文字数 | `7763`文字 |
| Raw Content SHA-512 | `1e9c02d65cf89c012e382a23c0cb4b8be0d90d7d4477339abb624ab0f3b1e9906d4cc3c4fcd34289ae5fb3ed86f454e23c0c918f5b461f47f7a803a9483621bf` |
| Strict Decode State(診断用、生Decodeを1回のみ実行) | `'failed'`(`JudgeDecodeError`が送出された) |
| Strict Decode Reason | `'found `{` that does not decode as one complete, well-formed JSON object -- a truncated or malformed judgment fragment, not a harmless wrapper'` |
| Recommendation | `None`(Decode失敗のため未算出) |
| Criterion内訳(pass/deviation/unknown) | `None`/`None`/`None`(Decode失敗のため未算出) |
| missing ID | `None`(未算出) |
| extra ID | `None`(未算出) |

### 5.2 判定(観測事実のみ、解釈の飛躍なし)

`finish_reason=LENGTH`かつ`completion_tokens`がRejudge Planの`max_new_tokens`(2400)と完全一致していることから、実Gemma応答はToken上限に達して生成が打ち切られたことが確認できる。診断用Strict Decoderは、この打ち切られたRaw Contentに対して`execution_state='failed'`、理由「JSON Objectとして不完全な`{`」を返した——これは、Criterion単位で`unknown`という正常なDispositionが返ってきた場合(`_recommendation_from_criterion_results()`がCOMPLETED状態から`EvaluationRecommendation.UNKNOWN`を導出する経路)とは異なる、**構造的に不完全な(Truncateされた)JSONによるDecoder自体の失敗**である。

Recommendation・Criterion内訳・missing/extra IDが全て`None`であること自体も、Decodeが「Criterion単位の判定に到達する前」に失敗したことと整合する(`_decode_criterion_results()`より前、JSON Object抽出の段階で例外が送出されたため)。

## 6. Focused／Static Verification

本Handoffの指示どおり、Source/Test/Configを一切変更していないため、Full Suite・Mypy・Ruffは実行していない(§4禁止事項「変更がないのにFull Suite／Mypy／Ruffを再実行すること」)。広範なCanonical Docs再読込も行っていない。

## 7. Internal Review(2観点のみ)

### Review ① — Command／完全Log／Marker取得の手続き整合

- [OK] Preflightを、対象を誤認せずRead-onlyで実施し、残存なしを確認した(§4)。残存があった場合の停止手順(Kill禁止・PID/Command報告のみ)は、対象が存在しなかったため発動しなかった。
- [OK] 実行Commandは指示された対象Test・Marker・Model条件と完全一致している(前回・前々回のReturnと同一のTest ID、同一のMain/Gemma Context設定)。
- [OK] 出力は`tail`を一切経由せず、`tee`で指定Path(`/private/tmp/phase9_gemma32_claude_complete_capture_20260905085447.log`)へ完全保存した。`set -o pipefail`により、`tee`自体の終了Codeではなく、pytest自身の終了Code(1)を確実に保持した。
- [OK] Log全文をRead-onlyでGrep・確認し、Marker行(実出力1件、Source表示1件を正しく区別)・PASS/FAIL行・Load Failure兆候の有無を確認した。Log FileのAbsolute Path・SHA-512・サイズ・行数を記録した。
- [OK] Test自体の再実行は行っていない(1回のみ)。

### Review ② — 実測値とClaimの意味整合

- [OK] Maximum Claimは「原因分離が今回達成された」ことと「修復は行っていない」ことの両方を明示しており、実測値(Decoder FAILED、finish_reason=LENGTH、completion_tokens=Plan上限と一致)と整合している。
- [OK] 「Gemmaが32 Criterionを扱えない」という一般化や、Decoder/Budget/Criterionへの言及を伴う結論の飛躍はしていない——観測された具体的Factのみを記載した(§5.2)。
- [OK] Raw Content全文はDocsへ一切記載していない(文字数とSHA-512のみ)。
- [OK] 本Returnは、指示どおりSource修復・追加試行・JSON Retry・Decoder/Budget/Criterion変更のいずれも提案・実施していない——次のStep判断はController/Userに委ねている。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **実Gemma 32 Criterion Rejudgeの真因**: 今回、Decoder FAILED(Truncateされた不完全JSON、`finish_reason=LENGTH`、`completion_tokens`がPlan上限2400と一致)であることが実機Evidenceで確定した。ただし、これが「常に」再現するか、それとも今回このTrialに限った現象かは、追加試行を行っていないため未確認(禁止事項により今回は確認していない)。
2. **対処方針**: Rejudge Token上限(現在2400、Candidate 400込みで2800ちょうど)を、実Gemmaが32件のCriterion結果を打ち切りなく生成しきるには不足している可能性がある、という仮説がEvidenceとして得られた。ただし、Budget再拡大は本Handoffで明示的に禁止されており、対処の要否・方法はController/User判断に委ねる。
3. **Selene**: 未解決のまま(前回Returnと同じ、今回変更なし)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外(今回はMypy自体実行していない)。

## 9. Action Inventory

**実行した**: Preflight(Read-only、残存確認)、指定Testの正確に1回の実行(`tee`による完全Log保存、pytest終了Code保持)、Log FileからのMarker/PASS-FAIL/Load Failure兆候のRead-only抽出、実測値の本Returnへの転記(Raw Content全文除く)、本Return・Recovery新規File作成。

**実行しなかった**: Source/Test/Config編集。同一Testの反復・追加試行。Process Kill/Server操作。JSON Retry、Decoder/Schema/Budget/Criterion変更。Selene、Frontend、Phase 9-2/9-3、Closure、Git操作。変更がないFull Suite/Mypy/Ruffの実行。広範なCanonical Docs再読込。

**Temporary Artifact／Active Process／Model Load**: 実行後のPost-run Read-only確認で、残存Process・Port Listenともになし(両ModelがTest自身の`finally`Blockで正常にUnloadされたことを確認)。完全Log File(`/private/tmp/phase9_gemma32_claude_complete_capture_20260905085447.log`)はTask専用の一時Fileとして保持している(削除していない)。

## 10. Exact Next Action for Codex Controller

1. Preflight結果(§4)を確認する——残存なし、Kill不要だったことを確認する。
2. 実行手続き(§5、tee経由の完全Log保存、pytest終了Code保持)を確認する。
3. Marker実測値(§5.1)とその判定(§5.2)——今回はDecoder FAILED(Truncate起因の不完全JSON)であり、Decoder COMPLETED+Criterion UNKNOWNではなかったこと——を確認する。
4. 上記を踏まえ、Rejudge Token予算(現在2800)が実Gemmaの32 Criterion応答完了に対して不足している可能性というEvidenceをどう扱うか(追加のBudget再拡大提案を検討するか、Fixture/Unit水準の成立と実機Evidence取得の完了をもって本項目を一旦区切りとするか、他の対応を取るか)を、Userとともに判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作、Source修復は行わない。Codex Controller Independent Reviewを待つ。
