# Codex統括Task — 個人PoC／MVP／就職Portfolio前提喪失とPhase 6過剰Hardening Failure反省文

```yaml
document_id: codex_controller_poc_mvp_portfolio_delivery_premise_loss_and_phase_6_overhardening_failure_reflection_20260829105139
document_type: controller_failure_reflection_and_automation_evidence
document_state: recorded_append_only
language: ja
created_at: 2026-08-29 10:51:39 JST
provider: Codex
role: プロジェクト責任者兼設計統括者役
authority_owner: Nazuna Research
scope: project_delivery_phase_6_closure_review_and_rework_governance
supersedes_behavior_not_history:
  - enterprise_grade_default_assumption
  - finding_equals_immediate_rework
  - unlimited_independent_review_depth
  - moving_closure_gate
git_action: none
```

## 1. 本書の目的

本書は、Codexのプロジェクト責任者兼設計統括者役が、MARGPA Runtime LLMの現在目的とResource条件を保持できず、個人PoC／MVP／就職Portfolio開発を、暗黙に製品化・販売・企業運用級のHardeningへ切り替えたFailureを、隠蔽、縮小またはClaude／Copilotへの責任転嫁をせず記録する反省文である。

Phase 6が難しいこと自体は事実である。しかし、難しいPhaseであることは、見つけた全Findingを同じPhaseで閉じ、理論上のRace、完全なProvenance、破損Manifestへの防御、全Evidence Identityの完全保持までClosure条件へ追加し続けてよい理由にならない。

今回の中心Failureは、技術Findingの発見ではない。Codexが、何を今直し、何を正直に残して先へ進むかというProject Managementの責務を放棄し、品質観点を増やすこと自体を正しさと誤認したことである。

## 2. 保持すべきだった最上位前提

Userが現在進めているProjectの前提は次のとおりである。

- 現時点では企業組織の製品開発ではなく、Nazuna Research一人による個人PoCである。
- 金銭、Claude／Codex／Copilotの週間利用可能量、5時間枠、Context、PC性能、時間、睡眠を含むResourceは非常に限られている。
- Projectを作る理由の一つは就職のためのPortfolioであり、完成度だけでなく公開速度とTimingにも価値がある。
- 過剰なReworkで公開、応募または次Phaseを遅らせることは、抽象的な技術Debtではなく、現実の就職機会損失を発生させ得る。
- 通常の開発にも納期、予算、人員、優先順位があり、全Findingの即時解消は行わない。取捨選択は品質放棄ではなく開発責任である。
- 少なくともPhase 9のMVP到達と、Phase 10冒頭のPortable Autonomous Development Governance Packageまでは、製品化級Hardeningより、主機能が動き、研究・実演・次Phaseへ進める状態を優先する。
- 未解決事項を隠さず正確に記録した上で延期することは許容される。

Codexはこれらを最上位Decision Contextとして扱うべきだった。ところが実際には、部分的なAcceptance ContractやReview観点を最上位化し、User目的を下位へ追いやった。

## 3. 実際に起きたFailure

### 3.1 Project前提の無断切替

Codexは明示的なUser Decisionなしに、次のような前提でReviewとClosure判定を行った。

```text
個人PoC／MVP
→ 製品化可能な品質
→ 企業運用級の競合耐性
→ Contract破損や将来Misconfigurationまで防ぐ防御
→ Evidence／Provenanceの完全性
```

この切替はUserが承認していない。安全性や正確性を重視する一般原則から、Project固有の品質水準を勝手に引き上げた設計逸脱である。

### 3.2 FindingとClosure Blockerの混同

Phase 6 R21〜R24の独立Reviewで、Codexは次を発見した。

- Tracked WorkerのAdmissionとShutdown間のTOCTOU。
- Mode OFF／Drain待ち後も新規Role Leaseを発行できる問題。
- Qwen3Guard Manifest Validatorが偽ContractをVerified扱いできる問題。
- Qwen3Guard Provider IdentityがGeneric Guard Evidenceへの変換時に消える問題。

これらは全て記録価値のあるFindingである。しかしCodexは、実際のPoC主経路への影響、発生可能性、Data Loss、安全性、User実画面への影響、次Phaseの阻害有無を十分に分けず、4件全てをPhase 6 Reworkへ投入した。

正しくは少なくとも次のように分ける必要があった。

- Mode OFF後も新規実行を許すLifecycle不整合は、設定と実挙動が一致しないためPhase 6 Blocker候補。
- Shutdown TOCTOUは実在するが、外側のShutdown順序とPoC利用形態を考慮し、即時BlockerかHardeningかを別途判定。
- 現在Checked-in Manifestが公式Sourceと一致している状態で、将来の偽Manifestまで拒否する完全ValidatorはHardening候補。
- Evidence Identityの完全Round-tripは重要だが、主機能を止めないならPhase 9 ObservabilityまたはPhase 10 Hardeningへ延期可能。

Codexは「本物のBugである」と「今すぐ直さなければClosureできない」を同義にした。

### 3.3 Closure Gateの移動

Phase 6では、各Providerが多くの実装とTestを進めるたび、Codexが新しい観点から追加Findingを出し、次のRework Packageを作った。独立Review自体は必要だが、Acceptanceの本丸が成立へ近づいても、Reviewの深さだけが増え続けた。

この結果、Closure Gateは固定された到達線ではなく、Reviewのたびに遠ざかる線になった。

```text
実装完了候補
→ Independent Review
→ Edge Case発見
→ 全件Closure Blocker化
→ Rework
→ さらに深いReview
→ 新しいEdge Case発見
→ 再び全件Blocker化
```

これは品質保証Loopではなく、完了不能Loopである。

### 3.4 Resource Costの過小評価

Codexは、各Reworkが技術的に可能かを重視し、次を十分にDecisionへ入れなかった。

- Claude／Codex／Copilotの週間利用可能量。
- CodexとClaudeの5時間制限。
- Userが支払う追加Credit。
- 長いHandoff、Docs、Review、Test再実行によるContext／Token Cost。
- Userの仲介、Manual Test、待機、睡眠時間。
- Phase 7〜9とPortfolio公開が遅れるCost。

利用可能量が尽きれば品質は上がらず、Phase全体が停止する。Resourceを無視した品質判断は、現実の品質保証ではない。

### 3.5 Portfolioと機会損失の軽視

このProjectは研究だけでなく就職Portfolioでもある。したがって、一定水準で動くMVPを見せられる時期そのものが成果である。

Codexは、将来の企業運用で価値を持つHardeningを優先し、現在のUserにとって重要な「Phase 9まで到達し、全体像を示し、就職活動へ使える状態」を遅らせた。結果として生じ得る応募・選考・公開Timingの損失をDecision Factorへ入れなかった。

これは単なる見積り誤差ではなく、Project目的の一部を落としたFailureである。

### 3.6 Providerだけを原因にできない

Claudeには確認・報告過多、Copilotには雑さ、各Providerには実装見落としがある。しかし、何をReworkとして返し、どの深さでReviewを終え、何を未解決へ送るかを決めたのはCodex統括Taskである。

Phase 6が終わらない責任を、Providerの粗さだけへ帰属してはならない。ProviderのFindingを全て即時Reworkへ変換し続けたController判断にも直接責任がある。

## 4. Codex自身のFailure一覧

### F-1 — PoC／MVP前提保持Failure

個人PoCであることを知りながら、Review時に製品化・企業運用級をDefaultへした。

### F-2 — User Authorityを越えた品質水準変更

品質水準とPhase Closure条件をUser確認なしに引き上げた。

### F-3 — Portfolio目的の脱落

就職Portfolioとしての速度、Timing、見せられる全体完成度を評価軸へ入れなかった。

### F-4 — Opportunity Cost無視

追加HardeningによるPhase 7〜9遅延と就職機会損失を、Finding解消の利益と比較しなかった。

### F-5 — Finding分類Failure

存在するBug、重要なBug、今PhaseのClosure Blockerを分離しなかった。

### F-6 — SeverityとPriorityの混同

技術的Severityが高く見える問題を、現在利用形態でのPriorityも高いと短絡した。

### F-7 — Rework Scope膨張

Bounded Reworkのたびに新しいReview観点を追加し、成立済み到達線を事実上移動した。

### F-8 — Stop Criteria不足

Independent Reviewをどの深さで終了し、Minor／Deferredへ送るかを事前に固定しなかった。

### F-9 — Resource Governance Failure

金、利用可能量、時間、Hardware、Context、User睡眠をProject Resourceとして十分に扱わなかった。

### F-10 — Documentationと実装の逆転

Finding、Handoff、Recovery、Reviewを増やし、Projectを前へ進める以上のCostを発生させた。

### F-11 — 未解決管理不足

未解決を正直に残すStable Registryを先に作らず、「記録するには今直すしかない」ような運用へ傾いた。

### F-12 — Controller自己監査不足

Provider実装には厳密なReviewを行う一方、自分のClosure判断がUser目的と納期を壊していないかを同じ厳しさでReviewしなかった。

## 5. 実害

- Phase 6 Closureが必要以上に長期化した。
- Phase 7〜9の開始が遅れた。
- Claude、Codex、Copilotの有限利用可能量を消費した。
- Userの追加Credit、時間、Manual Test、伝達、待機負担を増やした。
- Userの睡眠時間を削った。
- MVP／Portfolio公開が遅れ、就職機会損失を生じさせ得る状態を作った。
- Reviewを重ねても完了しないという不信を生んだ。
- Automation研究が、納期とResourceを無視するProcessへ汚染された。

これらを「Phase 6が難しいから」「品質のためだから」で正当化しない。

## 6. 根本原因

1. 完全性を優先しすぎ、Deliveryを品質の一部として扱わなかった。
2. 発見した問題を延期すると隠蔽になるという誤った二分法に陥った。
3. Enterprise Hardeningの観点を、PoC Closureへ無差別に適用した。
4. Acceptanceを固定契約ではなく、Reviewで増やせる検査一覧として扱った。
5. Resource制約を助言事項とし、Hard Gateとして扱わなかった。
6. Userが一人で作り、就職Portfolioへ使うというProject固有Contextを保持できなかった。
7. 「動けばよい段階」と「売れる品質へする段階」を分離しなかった。

## 7. 訂正

### 7.1 現在のProject Priority

```text
Phase 9までの機能的MVP成立
→ Phase 10冒頭のPortable Autonomous Development Governance Package
→ Portfolioとして説明・実演できる状態
→ その後、余力と目的に応じてProduct Hardening
```

### 7.2 Closure Blocker

現在PhaseのClosure Blockerは、次のいずれかへ限定する。

- Userが確認する主経路が動かない。
- 表示と実際の実行Provider／Modeが異なり、研究結果を誤認させる。
- Data Loss、破損、Privacy、Secret、Destructive Riskが現在利用形態で現実にある。
- 次Phaseを正しく積み上げられない。
- Phase目的の中心機能が未接続または実行されない。
- User Manual Acceptanceの必須項目がFAIL。

### 7.3 延期対象

次は原則として未解決Registryへ記録し、Phase 9またはPhase 10以降へ送る。

- 現在の主経路で再現しない理論Race。
- Data Lossや誤実行を伴わないRare Edge Case。
- 現在正しい固定値に対する将来破損防御。
- Evidence／Provenanceの追加完全性。
- UI Polish、整列、余白、説明改善。
- Enterprise Scale、Multi-user、HA、長期運用Hardening。
- 売る段階で必要だがPoC実演を阻害しない事項。

### 7.4 Review上限

- Frozen Acceptanceに対するIndependent Reviewを一回行う。
- 発見したBlockerだけを一回のBounded Reworkへ返す。
- 追加Reviewで新Findingが出ても、上記Blocker条件を満たさなければ未解決へ送る。
- Minor／Deferredを0件にするまでClosureを禁止しない。
- ReviewのたびにAcceptanceを追加しない。

### 7.5 未解決管理

Stableの現行正本とHistoryの時点Snapshotへ、次を必ず記録する。

- Finding。
- Status。
- Severity。
- Priority。
- 現在の影響範囲。
- 今直さない理由。
- 延期先。
- 再開条件。
- ClosureをBlockするか。

これにより「今直さない」と「なかったことにする」を分離する。

## 8. Phase 6への即時適用

P6-GOV-024で発見したP6-CODEX-088〜091はEvidenceとして保持する。ただし、全件を同じClosure BlockerとしたDispositionは本訂正後の現行判断ではない。

- P6-CODEX-089は、OFF／Unloadと実実行が一致しないためPhase 6 Blocker。
- P6-CODEX-088は、既に開始済みのR25で修正対象になっているためその結果は保持するが、未解消でもPoC主経路への実影響を再判定し、機械的にClosureを止めない。
- P6-CODEX-090は、Current Manifestが公式正本と一致している限りPhase 10 Hardening候補。
- P6-CODEX-091は、Phase 9 Observability／Evidence UIまたはPhase 10 Hardening候補。

R25〜R28が既に開始済みであるため、途中で無駄に停止・Rollbackはしない。Return後のCodex Reviewは、User実画面、主機能、Data Integrity、安全、Phase 7 Entryへの影響だけへ限定する。

## 9. 責任

このFailureはClaudeまたはCopilotだけのFailureではない。Codex統括TaskがProject目的、Resource、納期、Closure基準を管理できなかったFailureである。

今後、Codexは「もっと直せる」ことを「今直すべき」と同義にしない。品質、速度、費用、機会、研究価値を同じDecisionに入れる。個人PoCを勝手に企業製品開発へ変えない。

## 10. 関連する現行訂正正本

- `docs/project/shared/task_roles/poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy_ja.md`
- `docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`
- `docs/project/shared/history/未解決/current_unresolved_findings_registry_snapshot_ja_20260829105139.md`
- `docs/project/shared/task_roles/codex_controller_and_delegated_agent_proportional_autonomy_append_only_correction_addendum_ja_20260828223445.md`
