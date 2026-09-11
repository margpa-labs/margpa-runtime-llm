---
document_type: codex_model_fallback_ui_observation_and_hypothesis_evidence
language: ja
title: Codex Sol→Luna再試行UIの実測と実効Model／Reasoning非可視性に関する仮説整理
created_at: 2026-09-08T21:12:08+09:00
author_role: Codex Controller
project: MARGPA-RUNTIME-LLM
authority_owner: Nazuna Research
recording_policy: append_only
status: observed_and_hypothesized_not_failure_determined
causality_status: unconfirmed
---

# Codex Sol→Luna再試行UIの実測と実効Model／Reasoning非可視性に関する仮説整理

## 0. 本書の目的

2026-09-08、長時間実行中のCodex Taskに、選択中の`GPT-5.6 Sol 極高`から`GPT-5.6 Luna`での再試行を提案するUIが表示された。

本書は、このUIから確認できる事実、公式情報、利用者から共有された前例、そこから導く推論、未検証の仮説を分離して保存する。

これは現時点でFailure断定を行う文書ではない。特に、次を事実として断定しない。

- 実行中に自動でSolからLunaへ切り替わったこと。
- UI表示と実際のBackend実行Modelが異なっていたこと。
- Reasoning Effortが表示値から密かに引き下げられたこと。
- 2026-09-08に観測された別のTask／Event Orchestration異常と、本件が同一原因であること。
- 特定の料金Planへ誘導する目的で本仕様が導入されたこと。

## 1. Evidence Source

### 1.1 Screenshot 1

```text
/Users/yukitakagi/Desktop/スクリーンショット 2026-09-08 20.56.15.png
```

画面上で確認できた主な表示は次のとおりである。

- Taskは`14m 46s 作業中`だった。
- Composer上の選択表示は`GPT-5.6 Sol 極高`だった。
- 次の案内が表示された。

> このリクエストについてもう少し慎重に検討しています
>
> お急ぎの場合は、より高速なモデルで再試行してください。ただし、複雑なリクエストへの対応能力は低くなる可能性があります。

- `再試行`操作が提示された。

### 1.2 Screenshot 2

```text
/Users/yukitakagi/Desktop/スクリーンショット 2026-09-08 20.56.28.png
```

`再試行`確認画面で、次が表示された。

> 現在の作業を破棄して再試行しますか？

> This will replace the current attempt in the conversation. Any file changes or other actions already taken will remain.

> メッセージは GPT-5.6 Luna を使って再送信されます。複雑なタスクでは性能が劣る場合があります

選択肢は次の2つだった。

- `待機を続ける`
- `破棄して再試行`

## 2. 観測事実

本節はScreenshotまたはUI文言から直接確認できる範囲だけを記録する。

1. 長時間作業中のTaskに、高速Modelでの再試行経路が提示された。
2. 再試行先として`GPT-5.6 Luna`が明記された。
3. 再試行前のComposer表示は`GPT-5.6 Sol 極高`だった。
4. UIは、Lunaでは複雑なTaskへの対応能力が低くなる可能性を明示した。
5. `破棄して再試行`を選ぶと、現在のAttemptは置換される。
6. 現在までのFile変更その他のActionは残ると表示された。
7. 利用者には、現在のAttemptを継続するか、破棄してLunaへ再送するかの選択肢が提示された。
8. Screenshotだけでは、`待機を続ける`選択中のBackend Model、実効Reasoning Effort、Compute BudgetまたはFallback履歴を確認できない。

## 3. 公式情報として確認した事項

2026-09-08時点のOpenAI Docs／ChatGPT Learnでは、次の役割分けが示されている。

- `GPT-5.6 Sol`は、複雑なCoding、Computer Use、Research等に対応するGPT-5.6系列の高性能Modelとして説明されている。
- `GPT-5.6 Luna`は、高速かつ低Costで、明確、反復的または大量のTask向けとして説明されている。
- 高いReasoning Effortは、複雑なTaskの結果改善につながり得る一方、処理時間とToken使用量が増えると説明されている。
- Codex App Serverの公開Contractでは、Turn開始時に`model`と`effort`を指定できる。

参照先：

- https://learn.chatgpt.com/docs/models?surface=app
- https://learn.chatgpt.com/docs/app-server

これらの公式情報はModel間の用途、Cost、速度、Reasoning Effortの差を裏付ける。一方、選択中のSolからBackendが自動かつ非表示でLunaへ切り替わる仕様は、今回確認した公式情報では確認できなかった。

## 4. 利用者から共有された関連前例

利用者は、継続的に使用してきた通常ChatGPTのModel側から、公式情報を根拠として次の説明を受けていたと報告した。

> 一定量を超えると、Fallbackして一時的に下位Modelへ落とすことがある。

これは本書では`user_reported_contextual_evidence`として扱う。

- 通常ChatGPT側に下位Model Fallbackの前例がある、という判断材料にはなる。
- その仕様がCodex Desktopの今回のTaskへ同じ形で適用されたことの直接証明ではない。
- 当該通常ChatGPT仕様の原文、対象Plan、閾値、表示条件、適用期間は本書作成時には独立確認していない。

## 5. 推論

本節は、観測事実と公式情報を組み合わせた推論であり、直接の実測ではない。

### 5.1 Capability／Cost Tiering

SolとLunaには、能力、速度、用途およびCostのTier差がある。今回のUIは、高性能だが時間を要する処理を待つか、より高速だが複雑なTaskでは性能が落ち得るModelへ切り替えるかを選ばせる設計と整合する。

したがって、次の理解は方向として妥当である。

```text
高度・複雑な処理
  -> 高Capability／高Cost側

速度・大量処理・Resource節約
  -> 低Cost／低Capability側
```

ただし、これだけから「より高度な作業をさせたければ必ず追加料金を払う」という個別Planの課金条件までは確定できない。どのCostをProvider、Subscription、Creditまたは利用者が負担するかは別の契約問題である。

### 5.2 Silent Fallback仮説が合理的である理由

通常ChatGPT側のFallback前例に関する利用者報告と、Codex側に今回明示されたSol→Luna再試行経路を合わせると、Codexにも自動または半自動の縮退経路が存在する可能性を検討することは合理的である。

さらに、実行後の実効Model／Reasoningを利用者が検証できないため、UI上の選択値とBackend上の実効値が一致することを外部から証明できない。

これにより、Silent Fallbackは「根拠のない空想」ではなく、検証対象とすべき実装仮説になる。

一方、今回のUI自身は明示的な利用者確認を要求している。したがって通常Contractとして最も強く支持される解釈は、利用者が`破棄して再試行`を選んだ後にLunaへ変更される、というものである。

## 6. 未検証仮説

### H1：明示的な再試行時だけLunaへ切り替わる

```yaml
status: most_directly_supported
```

Screenshot上のContractどおり、`待機を続ける`場合はSolの現在Attemptを維持し、`破棄して再試行`を選んだ場合だけLunaで新しいAttemptを開始する。

### H2：UI表示を維持したままBackendでLunaへ自動Fallbackする

```yaml
status: plausible_but_unverified
```

UI上は`GPT-5.6 Sol 極高`のままでも、一定の利用量、待機時間、負荷、Quotaまたは内部Policyを境に、BackendではLunaへ切り替わる可能性がある。

現在、これを裏付けるExecuted Model Identityは取得できていない。

### H3：ModelはSolのままだが、実効Reasoning／Compute Budgetが縮退する

```yaml
status: plausible_but_unverified
```

Backend ModelはSolのままでも、Reasoning Effort、Reasoning Token Budget、Tool回数、Deadline、Context処理量またはLong-run Budgetが表示値より低くなる可能性がある。

外部から見た品質低下や指示保持低下は、H2とH3のどちらでも起こり得る。

### H4：2026-09-08のTask／Event異常と同一Rolloutに由来する

```yaml
status: timing_correlation_only
```

同日、Model Picker、再試行UI、Task OrchestrationまたはPlatform側の変更を示唆する複数の変化が観測された。しかし、旧指示再送、不要Task生成、Task状態不一致、Task間通信の承認待ち化と本件を結ぶ直接Evidenceはない。

これらは同じRolloutに由来する可能性も、独立した問題である可能性も残る。

関連Evidence：

```text
docs/project/shared/history/ai_system_anomalies/codex/codex_phase_9_2_task_orchestration_instruction_replay_and_resource_loss_consolidated_evidence_ja_20260908205225.md
```

## 7. 現時点で不明な事項

- 現在Attemptで実際に実行されたModel ID。
- 実際に適用されたReasoning Effort。
- Requested値とEffective値が一致していたか。
- 自動Fallbackの有無、発生時刻、理由および閾値。
- FallbackがQuota、Rate Limit、Latency、System LoadまたはSafety Policyのどれに起因するか。
- Long-running Taskの途中でModelまたはBudgetが変更されるか。
- App／Task Harness／Server側のVersionと今回のUI導入時期。
- 今回の変更が全利用者、特定Plan、段階的Rolloutまたは実験群のどれに適用されたか。

不明事項は`unknown`として保持し、推測値で埋めない。

## 8. FailureではなくTransparency課題としての評価

明示的な同意を得て、高速な下位Modelへ再試行できる機能自体はFailureとは限らない。長時間Taskから利用者を救済する正当なUXになり得る。

問題になり得るのは、次の場合である。

- 利用者の同意なしにModelまたはReasoningが縮退する。
- UIのRequested値とBackendのEffective値が異なる。
- Fallback後も元のModel表示が残る。
- 実行結果からExecuted ModelとEffective Reasoningを監査できない。
- Fallbackが指示保持、検証深度またはTask Authorityへ影響しても、Evidenceが残らない。

したがって本件の現時点の分類は、`confirmed_failure`ではなく、`observed_fallback_ui_with_unresolved_execution_transparency`とする。

## 9. MARGPA-RUNTIME-LLMへの設計教訓

同種の不透明性を避けるため、各Turn、Stage、RetryおよびSubtaskのEvidenceへ最低限次を分離記録する。

```yaml
requested_model_identity: required
configured_model_identity: required
active_model_identity: required
executed_model_identity: required
requested_reasoning_effort: required
effective_reasoning_effort: required_or_explicitly_unavailable
requested_budget: required
effective_budget: required_or_explicitly_unavailable
fallback_occurred: required
fallback_from: required_when_fallback
fallback_to: required_when_fallback
fallback_reason: required_when_fallback
fallback_authority: user | runtime | provider | unknown
user_consent: required_when_user_choice_exists
retry_attempt_id: required
superseded_attempt_id: required_when_retry
runtime_revision: required_or_explicitly_unavailable
```

設計原則は次のとおりである。

1. Requested、Configured、Active、Executedを同一Fieldへ混ぜない。
2. Reasoning EffortもRequestedとEffectiveを分離する。
3. Modelが同じでもBudget縮退を別Eventとして記録する。
4. Fallbackを暗黙の内部処理にせず、Reason、Authority、Consent、時刻をEvidence化する。
5. Retryは旧Attemptを上書きせず、Attempt Ledger上でSupersessionとして関連付ける。
6. File Mutationが残りModel Reasoningだけ破棄される場合、その境界を明示する。
7. 表示上のModel名ではなく、実行Adapterが確定したIdentityを記録する。
8. 実効値を取得できない場合、推定値を記録せず`unavailable`または`unknown`とする。

## 10. 現時点の結論

実測されたのは、長時間実行中の`GPT-5.6 Sol 極高`Taskに対し、現在Attemptを破棄して`GPT-5.6 Luna`へ再送する選択肢が提示されたことである。

利用者が再試行を承認していない状態で、自動的にLunaへ切り替わった事実は確認されていない。一方、通常ChatGPT側のFallback前例に関する利用者報告、Codex上の明示的なSol→Luna経路、実効Model／Reasoningを監査できない現状を踏まえると、Silent FallbackまたはEffective Budget縮退は十分に検証価値のある仮説である。

本件は現時点でFailureと断定せず、観測済みUI、公式確認事項、推論、仮説、Unknownを分離したEvidenceとして保持する。
