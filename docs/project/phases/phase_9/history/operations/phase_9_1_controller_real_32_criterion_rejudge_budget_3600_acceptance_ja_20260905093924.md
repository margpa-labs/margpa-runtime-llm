# Phase 9-1 — 実32 Criterion Rejudge Budget 3600 Controller受理

```yaml
document_type: controller_acceptance
document_state: accepted
from: codex_controller
to: user
review_target: ../../../handoffs/phase_9_claude_real_32_criterion_rejudge_budget_3600_exact_return_ja_20260905093032.md
closure_authority: none
language: ja
recorded_at: 2026-09-05 09:39:24 JST
```

## 1. 判定

`P9_1_REAL_32_CRITERION_REJUDGE_BUDGET_3600_ACCEPTED`

今回対象の追加Reworkは不要。Phase 9-1 Closure自体はまだ行わない。

## 2. 受理した内容

- `_REJUDGE_TOKENS_PER_CRITERION`: `75 -> 100`
- `LIVE_REPAIR_BUDGET.max_additional_tokens`: `2800 -> 3600`
- Repair Candidate上限400、最大Model Call 2、Deadline、Main／Gemma Contextは維持。
- 32 CriterionではRejudge上限3200、Candidateが400を全消費しても合計3600で境界内。
- 33 Criterionおよび局所Budget 3599では呼出し前拒否を維持。

## 3. Controller独立確認

- 対象Unit: `38 passed`
- 対象Ruff: `All checks passed`
- 実Modelの再実行は行わず、Claude保存済み完全Logを照合した。
- Log SHA-512はReturn記載の
  `91ba197af7087f35a74801d284bc45fbc2ddaf2abe02a87e02df95bfb4d9b43d86657e755eae6bacc23a61107602bdd3a9935bb9c43d94ae77963043520377f9`
  と一致した。
- Log Markerは`finish_reason=STOP`、`completion_tokens=3011 / max_new_tokens=3200`、Strict Decode `completed`、32件全PASS、missing／extraなし、Recommendation `accept`、`accepted=True`、`outcome=improved`を示す。
- 実機TestのHard AssertはGemma Identity、独立Artifact Role、改善採用、非空かつ元誤答と異なるPresented Contentまで確認している。

## 4. Claim境界

今回の1回で、実Main Qwen Repairから実Gemma 32 Criterion Rejudge、Strict Decode、改善採用までの成立を確認した。ただし、非決定的な実Modelの恒常的成功率までは主張しない。

Selene自体は未解決のまま。Gemmaによる代替経路はBackend実機水準で大きく成立したが、User Mac実画面での最終確認前にPhase 9-1 Complete／Closureへは進まない。

## 5. 次Action

追加Claude Reworkではなく、User Mac上でGemma JudgeのOBSERVE／ENFORCE、Repair→Rejudge、Main Runtime Governance ENFORCEの実画面成立を確認する。その結果を受けてSelene延期の最終扱いとPhase 9-1 Complete Candidateを判断する。
