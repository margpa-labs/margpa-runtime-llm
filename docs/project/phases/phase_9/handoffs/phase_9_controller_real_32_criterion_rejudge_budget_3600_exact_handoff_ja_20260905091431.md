# Phase 9-1 — 実32 Criterion Rejudge Budget 3600 Exact Handoff

```yaml
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-05 09:14:31 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
maximum_claim: P9_1_REAL_32_CRITERION_REJUDGE_BUDGET_3600_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. User決定

Userは、実Gemma 32 Criterionが`finish_reason=length`／Completion 2400で切断され未完JSONとなったEvidenceを踏まえ、次の最小変更を承認した。

- `_REJUDGE_TOKENS_PER_CRITERION`: 75→100
- `LIVE_REPAIR_BUDGET.max_additional_tokens`: 2800→3600

Repair Candidate上限400、通常32 Criterion、最大Model Call 2、Gemma Context 8192、Main Context 16384、Rejudge Deadline 120秒は変更しない。

## 2. 実装

- 上記2値だけを変更する。
- 75／2800をCurrent値として扱うSource Comment／Testを、過去事実と新Current値が混ざらないよう最小訂正する。
- 前回追加済みのTest-only Observabilityを維持し、Raw内の`criterion_id`文字列出現数を追加する。Raw全文はDocsへ記録しない。
- Production Decoder、Schema、Prompt、Criterion集合、Batching、Retryには触れない。

## 3. Fixture／Unit

1. Candidate 400＋32×100=3600がPlan受理され、Rejudge Requestの`max_new_tokens=3200`となる。
2. 同一32 Criterionを落とさずRepair→Rejudge→改善採用、Model Call 2、合計3600以下を確認する。
3. Candidate 400＋局所Budget 3599では1 Token不足として拒否する。
4. Candidate 400＋33 Criterionは3700となり、Production Budget 3600では拒否する。
5. Context不足、Counter失敗、Deadline、Cancel、Registry shutdownのTyped分類とCall抑止を維持する。
6. 旧75／2800への一時Sabotageで新境界Testが失敗することを確認し、直後に復元・無差分確認する。

## 4. 実機 — 1回だけ

PreflightでMARGPA Server、別pytest／Python／llama Process、MARGPA Port残存をRead-only確認する。残存時はKillせずTrue Stopとする。

問題がなければ、既存のMain Qwen Repair→Gemma Rejudge実32 Criterion Testを同一条件で1回だけ実行する。出力は`tail`へ渡さず、新規Task専用Logへ`tee`で完全保存し、pytest終了Codeを保持する。

必須Evidence:

- Plan／Request `max_new_tokens=3200`
- `finish_reason`、Prompt／Completion Token、生成時間
- Raw文字数／SHA-512／`criterion_id`出現数
- Strict Decode State／Reason／Recommendation
- pass／deviation／unknown、missing／extra ID
- Gemma Identity、改善採用、Presented Content
- 完全Logの絶対Path／SHA-512／行数

成功時は全32 ID、Decoder COMPLETED、改善採用をHard Assertする。不成立時は観測結果を返し、同条件Retry、追加Budget拡大、Criterion削減、Prompt／Schema修正へ進まない。

## 5. 禁止事項

Selene、JSON Retry、Decoder緩和、Schema／Prompt変更、Batching、Context／Deadline／Call上限変更、Frontend、Phase 9-2／9-3、Closure、Git add／commit／push／stashは禁止。Current Registry／Phase Indexは編集しない。

## 6. Verification／Return

対象Unit、非Model Full Suite、対象Ruff、Canonical Mypyを実行する。Internal Reviewは①予算・Token・Failure境界、②実機Evidence・Claim・手続きの完全別2観点で行う。Return／Recoveryは新規Pathで作成し、Controller Review待ちで停止する。

