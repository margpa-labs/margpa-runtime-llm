# Phase 9-1 — 通常32 Criterion Rejudge予算2800 Exact Handoff

```yaml
document_id: phase_9_controller_normal_32_criterion_rejudge_budget_2800_exact_handoff_20260905075241
document_type: exact_implementation_handoff
document_state: ready
recorded_at: 2026-09-05 07:52:41 JST
language: ja
from: codex_controller
to: claude_designer_implementer
decision_authority: user
authority_owner: Nazuna Research
maximum_claim: P9_1_NORMAL_32_CRITERION_REJUDGE_BUDGET_2800_READY
phase_9_1_closure: false
git_action: prohibited
append_only: true
```

## 1. User決定と目的

Userは2026-09-05、`LIVE_REPAIR_BUDGET.max_additional_tokens`を**2000から2800へ変更する最小案**を承認した。

現行の上限はRepair Candidate 400、Rejudgeは通常32 Criterion×暫定75=2400。総上限2800により、Criterion削減や出力係数の再縮小をせず、通常32件を同じFrozen集合のRepair→Rejudgeへ渡せるようにする。

## 2. 実装境界

- `LIVE_REPAIR_BUDGET.max_additional_tokens`だけを2000→2800へ変更する。`max_total_model_calls=2`、時間上限、`_REPAIR_MAX_NEW_TOKENS=400`、`_REJUDGE_TOKENS_PER_CRITERION=75`、Criterion選択上限32は変更しない。
- 2000固定を前提にしたSourceコメントとTestを、過去事実と新しいCurrent値が混ざらないよう最小限更新する。
- 32 Criterion、Repair使用量400のPlanが`max_new_tokens=2400`で受理され、22／26等の以前の「2000時点の境界」をCurrent仕様として残さない。
- Token／Context不足、Counter失敗、Deadline、Cancel、Registry shutdownのTyped分類とRejudge Call 0を維持する。

## 3. 必須検証

### A. Fixture／Unit

1. Candidateが最大400 Tokenを使用後も、実ARGD／DAGD相当の32 Criterion全件を保持したPlanが2400 Tokenで成立する。
2. 32件を1件も落とさず、Repair→同一集合Rejudge→改善採用までEnd-to-Endで成立する。合計使用量は2800以下、Model CallはRepair＋Rejudgeの2回。
3. 2800を1 Tokenでも超える条件、Context不足、Deadline、Cancel、Counter失敗、Registry shutdownは、従来どおり呼出し前または該当境界でTypedに拒否される。
4. 新規／書換Testは、旧2000上限へ戻す等のSabotageで意図どおり失敗することを確認し、復元後の差分が残らないようにする。

### B. 実モデル — 1回だけ

Main QwenをRepair Candidate生成、GemmaをRejudgeに使い、**実109 Corpusから通常どおり選ばれた32 Criterion**を同一Frozen集合のまま渡す有界Smokeを1回だけ行う。Main context=16384、Gemma dedicated context=8192の既存設定を使う。

確認対象は、Plan=2400、全32 ID保持、実Gemma Decode成功、同一Gemma Identity、改善回答採用、実Token／時間／Failure Reason。Artifact不足以外を安易にSkipしない。失敗時は同条件反復・追加予算拡大・Criterion削減をせず、実測結果をそのまま返す。

この実機試験は32件Rejudgeの成立確認であり、User Mac実画面確認の代替ではない。

## 4. 禁止事項

Selene試行、不正JSONリトライ、Decoder緩和、Context／`max_new_tokens`全体設定変更、Call上限変更、Batching新設、Native更新、Download、新Resource Gate、Frontend変更、Phase 9-2／9-3、Closure、Git add／commit／pushは禁止。

Gemma Schema順序、Planner Failure分類、Judge／Main Governance Golden Path等の受理済み実装を再設計しない。Current RegistryとPhase IndexはController判断前に直接更新しない。

## 5. Return

対象Focused Test、非実機Full Suite、Ruff、Canonical Mypyを実行する。完全に異なる観点でInternal Reviewを2回行い、新規PathのExact ReturnとRecoveryを作成して停止する。

最大Claimは実結果に合わせる。実32件が不成立ならComplete Candidateへ引き上げない。Phase 9-1 ClosureやSelene解決をClaimしない。
