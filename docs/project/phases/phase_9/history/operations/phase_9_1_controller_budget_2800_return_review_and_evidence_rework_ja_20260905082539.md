# Phase 9-1 — Budget 2800 Return Controller Review

```yaml
document_type: controller_independent_review
document_state: changes_required
recorded_at: 2026-09-05 08:25:39 JST
language: ja
reviewer: codex_controller
phase_9_1_closure: false
```

## 1. 判定

`CHANGES REQUIRED`。

`LIVE_REPAIR_BUDGET.max_additional_tokens=2800`、32 CriterionのPlan=2400、Fixture上のRepair→Rejudge→採用、既存Typed Failure維持は受理する。実Gemma 32 Criterion Rejudgeは未成立であり、Failure Evidenceが原因を一意に区別できないためPhase 9-1 Complete Candidateにはしない。

Controller確認はUnit 38 passed、対象Ruff clean、Budget実値2800／Call上限2／Repair 400／Rejudge 75×32=2400。他の実Model試験は再実行していない。

## 2. Findings

### IR-R6-01 — `unknown`からDecoder失敗を断定できない

重大度: Major。

`repair_live_integration.py`はDecoderがFAILEDの場合だけでなく、DecoderがCOMPLETEDでもRecommendationがUNKNOWNなら最終`outcome=unknown`を返す。DecoderはCriterion Resultに`unknown`が1件でも含まれるとRecommendationをUNKNOWNへ導出できる。

したがって、今回の`accepted=False`／`outcome=unknown`／`rejected_reason=None`だけから「実Gemma DecodeがCOMPLETEDに至らなかった」とは断定できない。少なくとも次を区別する必要がある。

- JSON不正、欠落ID等によるDecoder FAILED／`malformed_output`
- 全32 IDをDecodeしたが1件以上が`unknown`でDecoder COMPLETED／Recommendation UNKNOWN
- その他のRecommendation／Criterion構成

旧Returnの断定はappend-only Correctionで訂正し、Source Commentの「Decode-scale limitation」も未確定表現へ直す。

### IR-R6-02 — 必須Telemetry／Failure Reason未捕捉

重大度: Major。

元Handoffは実Token、時間、Failure Reasonの取得を要求したが、実行時はPrintが失敗Assertより後にあり、取得できなかった。事後にPrint位置は直されたが、現Testが出すのはUsageと総Outcomeだけで、Raw Generationの`finish_reason`、Strict Decoderの`execution_state`／`failure_reason`／Recommendation／Criterion内訳をまだ記録しない。

実Modelを再度動かす前にTest-only Observabilityを完成させ、Controllerが許可する追加1回だけで原因を区別する。

### IR-R6-03 — 1 Token超過Testの境界が通常条件と異なる

重大度: Minor。

現TestはCandidate使用量401として残量2399を作るが、通常Repair Candidate上限は400。Planner防御Testとしては有効でも、「承認値2800より1 Token低ければ通常32件が入らない」という境界証明にはなっていない。

Candidate 400を維持し、局所Fixture Budgetを2799にした条件で拒否を証明する。Production Budget 2800は変更しない。

## 3. Disposition

- Budget 2000→2800: ACCEPT。戻さない。
- Fixture／Unit: ACCEPT。ただしIR-R6-03のみOracleを補正する。
- 実Gemma 32件: INCOMPLETE。追加1回の診断付き実行を許可する。
- JSON Retry／Decoder緩和／Criterion削減／予算追加: 引き続き禁止。
- Selene／Phase 9-2／9-3／Closure: 対象外。

