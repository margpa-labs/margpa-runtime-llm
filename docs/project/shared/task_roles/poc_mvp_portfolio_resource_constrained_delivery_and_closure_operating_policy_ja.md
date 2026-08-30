# 個人PoC／MVP／就職Portfolio／Resource制約下のDelivery・Review・Closure運用Policy

```yaml
document_id: poc_mvp_portfolio_resource_constrained_delivery_and_closure_operating_policy
document_type: shared_stable_normative_operating_policy
document_state: current_stable_authority
language: ja
created_at: 2026-08-29 10:51:39 JST
decision_authority: user
authority_owner: Nazuna Research
applies_to:
  - Codex_プロジェクト責任者兼設計統括者役
  - Codex_Claude_Copilot設計者兼実装者役
  - future_provider_agents
  - Phase_review_rework_closure_planning
priority: user_current_project_premise
mutation_policy: stable_current_source
```

## 1. Authorityと目的

本Policyは、MARGPA Runtime LLMの現段階におけるDelivery、Independent Review、Rework、未解決管理およびPhase Closure判断の現行正本である。

既存文書に、より厳しい一般的Hardening、完全性、Evidence、ReviewまたはClosure条件が存在しても、本Projectの現在段階に対する適用は本Policyで比例化する。Historical Evidenceは削除しないが、今後のBlocker分類は本Policyを優先する。

優先順位は次のとおりとする。

```text
Userの最新明示指示
→ 本Policy
→ Active Phase Handoff／Acceptance（本Policyに反しない範囲）
→ 比例的Autonomy Addendum
→ その他Stable Rule
→ Historical Evidence
```

## 2. Current Project Premise

現段階のProjectは次の条件下にある。

```text
開発主体: Nazuna Research一人
段階: PoC／研究MVP／就職Portfolio
組織Resource: なし
金銭・AI利用可能量・時間・Hardware: 強い制約あり
短期目標: Phase 9までのMVP成立
次の重要目標: Phase 10冒頭のPortable Autonomous Development Governance Package
Product／Enterprise Hardening: 原則としてその後
```

速度、公開Timing、Portfolioとしての説明可能性および次Phaseへの到達は、品質の対立概念ではなく、品質Decisionの一部である。

## 3. 禁止する前提切替

Userの明示決定なしに、次の前提切替を行わない。

- PoCから販売製品品質へ切り替える。
- 個人利用から企業Multi-user運用へ切り替える。
- MVPから完全Hardeningへ切り替える。
- Current HardwareからCloud／Server級可用性へ切り替える。
- Portfolioの納期より、全Technical Debt 0件を優先する。
- 未解決を記録して延期する選択肢を消す。

## 4. Severity、Priority、Blockerの分離

全Findingは次の3軸を別々に評価する。

```text
Severity: 問題が発生した場合の技術的影響
Priority: 現在の目的とResourceに対して、いつ直すべきか
Closure Blocker: 現Phaseを閉じることを実際に禁止するか
```

`Severity=Major`は自動的に`Priority=P0`または`Closure Blocker=YES`を意味しない。

## 5. Priority定義

### P0 — Current Phase Closure Blocker

次のいずれかをEvidence付きで満たす場合だけP0とする。

- Phase目的の中心機能が未接続、実行不能または虚偽表示になる。
- Userが使う主経路で再現し、回避不能。
- Configured／Active／Executed ProviderまたはModeが不一致で研究結果を誤認させる。
- 現在利用するDataのLoss、破損、Privacy、SecretまたはDestructive Riskがある。
- 次Phaseが誤った土台へ依存する。
- Frozen User Manual Acceptanceの必須項目がFAIL。

### P1 — 近接Phaseで直す

- 主経路に影響し得るが回避策がある。
- 小さく安全に直せ、次Phaseで触るとCostが大きくなる。
- Observability不足により調査が著しく困難だが、実行自体は成立する。

P1だけではPhase Closureを禁止しない。

### P2 — Phase 9／10へ延期

- UI Polish、Layout、文言、余白、表示順。
- 現在の主経路で発生しないRace／Rare Edge Case。
- 現在正しいContract／Manifestを、将来の破損から守る追加検証。
- Evidence／Provenance／Identityの完全性向上。
- Enterprise Hardening、Scale、HA、Multi-user、長期運用耐性。

### P3 — Backlog／条件待ち

- Product化、販売、企業採用時に初めて必要。
- Cloud／Server／新Hardware／外部契約が前提。
- 現段階では費用対効果が成立しない研究候補。

## 6. Closure Blocker判定Contract

Controllerが新しいClosure Blockerを宣言する場合、必ず同じ記録内で次を示す。

```text
再現経路
現在Userに見える影響
Data／Safety／Research Integrityへの影響
回避策の有無
次Phaseへ送れない理由
最小修正Scope
概算Resource Cost
```

一項目でも説明できない場合、Defaultは未解決Registryへの登録であり、即時Reworkではない。

## 7. Review Budget

### 7.1 Default Cycle

```text
Implementation Candidate
→ Controller Independent Review 1回
→ P0だけをBounded Rework
→ Targeted Re-review 1回
→ User Manual Acceptance
→ Closureまたは明示された最小残件
```

### 7.2 新Finding

Re-review中に新Findingを発見しても、P0条件を満たさない限り追加Rework Cycleを開始しない。Stable未解決Registryへ送る。

### 7.3 Moving Goalpost禁止

- Frozen AcceptanceをReview後に無断追加しない。
- Product／Enterprise観点をPoC Acceptanceへ後付けしない。
- Minor／Deferred 0件をClosure条件にしない。
- 全ProviderのInternal Review Finding 0件をClosure条件にしない。

## 8. Resource Gate

次を技術Resourceとして扱う。

- Userの金銭。
- Claude／Codex／Copilot等の週間利用可能量。
- 5時間制限。
- Context／Compaction Cost。
- Local PCのMemory、Disk、CPU／GPU。
- Userの作業時間、睡眠、Manual Test負担。
- Portfolio公開、応募、就職Timing。

P1以下の修正が、Phase到達、Reserve FloorまたはUser生活を圧迫する場合、延期する。

## 9. 未解決はFailure隠蔽ではない

今直さないFindingは、次の現行正本へ記録する。

`docs/project/shared/未解決/current_unresolved_findings_registry_ja.md`

History Snapshotは次へAppend-onlyで置く。

`docs/project/shared/history/未解決/`

各Findingへ、Status、Severity、Priority、Impact、Deferral Target、Reopen Condition、Closure Blockerを記録する。

## 10. Docs最小化

- 同じ事実をHandoff、Recovery、Review、Reflectionへ無制限に複製しない。
- Stable Current Sourceは現在判断を示す。
- History Snapshotは時点判断を固定する。
- Reflectionは重大な判断Failureだけに使う。
- Routine Findingは未解決Registryへ統合する。

## 11. Phase 6 Immediate Ruling

### Current P0候補

- Mode OFF／Provider切替後に新しい実行Leaseを許すLifecycle不整合。
- Selene／Qwen3GuardのConfigured／Active／Executedが一致せず、実Providerが動かないまたは虚偽表示になる状態。
- Semantic 109件がLive Turnで実評価されず、旧`Deferred 109`のままになる状態。
- Judge／Repairの実画面Golden Pathが成立しない状態。
- Real Browser／User Macの必須Manual Acceptance Failure。

### P1以下へ再分類する候補

- Current Production Shutdown順で主経路影響が証明されていないWorker Admission Race。
- Current Manifestが公式Sourceと一致している状態での偽Manifest防御強化。
- Guard Evidence Provider Identityの完全Round-trip。
- Phase 9予約済みUI Polish。

P6-GOV-024のEvidence自体は保持するが、全4 Findingを一律Closure Blockerとした判断は本PolicyでSupersedeする。

## 12. 既に開始済み作業

既に開始済みのR25〜R28は、中断・RollbackによりさらにResourceを失わないため完了まで進めてよい。ただし、そのReturn後に新しいEnterprise Hardening Cycleを自動追加しない。

次のController Reviewは、Current主経路、Data Integrity、安全、Provider実行Identity、Semantic評価、Judge／Repair、User Manual Acceptanceへ限定する。

## 13. Controller自己確認

新しいReworkを発行する前に、必ず次を確認する。

```text
これは本当に現在のPoC主経路を止めるか。
Userが実画面で困るか。
次Phaseへ送ると何が壊れるか。
未解決Registryで管理できないか。
修正Costは残Resourceに見合うか。
Portfolio公開を遅らせる価値があるか。
製品化前提へ勝手に切り替えていないか。
```

一つでも曖昧なら、即時Reworkではなく分類・延期をDefaultとする。

## 14. Source Evidence

- `docs/project/shared/history/automation/codex_controller_poc_mvp_portfolio_delivery_premise_loss_and_phase_6_overhardening_failure_reflection_ja_20260829105139.md`
- `docs/project/shared/history/automation/codex_controller_phase_6_automation_overconstraint_context_retention_and_fresh_task_misapplication_failure_reflection_ja_20260828222629.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov024_claude_r21_to_r24_controller_independent_review_ja_20260829101215.md`

## 15. 2026-08-29直接追記 — 実画面テスト前の完成度上限と追加改善の決定権

本節はUserの最新明示指示により、今回に限り本Stable Policyへ直接追記する。

### 15.1 一発合格を目的にしない

Controllerおよび実装Agentは、Userによる実画面テスト前に理論上の完全性を追い続け、全Findingを先回りして除去することで「一発合格」を目指してはならない。

実画面テストでは、Source Review、Unit／Integration TestおよびAgent内部Reviewでは検出できない問題が発見され得る。その内容と影響Levelによっては、どれだけ事前Hardeningを行っても追加修正が必要になる。

したがって、実画面テスト前の過剰な一発合格狙いは、次のCostを増やす一方で、再作業を確実には防がない。

- Codex／Claude／Copilot等の利用可能量。
- Userの金銭、時間、待機および睡眠。
- Context、Review、TestおよびDocs Cost。
- Phase 7以降の開始遅延。
- MVP／Portfolio公開と就職活動の機会損失。

これは品質向上ではなく、費用対効果を失った非効率として扱う。

### 15.2 実画面テストへ渡す停止線

実装、ReviewおよびReworkは、次の4条件を満たした時点でUser実画面テストへ渡す。

```text
Phase目的の主機能が動く。
Data破損、虚偽表示、誤Provider実行等の実害ある問題がない。
次Phaseの土台として使用できる。
User実画面テストを安全に開始できる。
```

この停止線を満たした後、理論Race、Rare Edge Case、完全Provenance、UI Polishまたは将来Hardeningを理由に、Manual Gateへの移行を遅らせない。

### 15.3 実画面テスト後の追加修正

Userは、実画面テスト時に必要に応じて「ここをもっとこうしてほしい」と追加改善を指示できる。

その場合、Controllerは実画面Evidenceを受けて、次の順に判断する。

1. 機能的Blockerなら現在PhaseのBounded Reworkへ入れる。
2. 小さく、明確で、現在直す費用対効果が高ければ対応する。
3. 表示改善、好み、低頻度Edge CaseまたはHardeningなら未解決Registryへ記録し、Phase 9／10等へ延期する。
4. Userが明示的に現在対応を求めた場合は、その指示を優先する。

AgentはUserの追加指示を先読みし、想像上の要望を無制限に実装してはならない。

### 15.4 Phase 7へのResource優先

Phase 6の実画面テスト可能状態へ到達した後は、残Resourceを理論上のPhase 6完全化へ使い切らず、Phase 7のMVP完了へ優先配分する。

Phase 6に未解決課題が残っていても、P0 Closure BlockerでなければStable未解決Registryへ保持したまま先へ進める。Phase 7でも同じ原則を適用し、RAG／Web検索／Data Governanceの中心経路を先に成立させる。

## 16. 2026-08-29補正 — 既知Debt受容は雑な実装の許可ではない

UserがPhase 6の既知影響を受容してPhase 7へ進む決定は、Phase 7の設計、実装、検証、ReviewまたはDocsを適当に行う許可ではない。

次を明確に分離する。

```text
既知Debtを記録して延期する
≠ 新しいPhaseを雑に作る
≠ Test／Reviewを省略する
≠ 虚偽Claimを許す
≠ Data／Citation／Security／Authorityを軽視する
```

Phase 7では、RAG、Web検索、Citation永続化およびData Governanceの中心経路を、PoC／MVPに比例した設計と検証で確実に成立させる。不要なEnterprise Hardeningは追加しないが、Frozen Scope内の実装品質、既存機能Regression、Userに見える状態および次Phaseの土台は丁寧に確認する。

### 16.1 Controllerの役割境界

プロジェクト責任者兼設計統括者役Taskは、Defaultで次を担う。

- Scope、Priority、Resource、AuthorityおよびAcceptanceの決定。
- 設計者兼実装者役へのExact Handoff。
- 実装中の待機。
- Return後のBounded Independent Review。
- User Manual結果の分類と次判断。

実装は設計者兼実装者役Taskへ委任する。Userが統括者Taskによる直接実装を明示した場合を除き、「小さく見える」「すぐ直せそう」というController判断だけでSource／Test／Buildを開始しない。利用可能量のReserve、Userが途中で相談できる余地および役割分離を、実装速度より先に守る。

### 16.2 Quality Stop Line

Phase 7の標準停止線は次とする。

```text
Frozen Scopeの中心機能が実経路で動く。
主なFailureが正直に表示される。
既存会話／Citation／Branch／Persistenceを壊さない。
Focused Testと比例した統合検証が通る。
User Manualへ渡せる。
```

この線を超えた後の追加Hardeningは未解決Registryへ送る。この線より前で「MVPだから」と雑に切り上げることも、この線を超えて理論完全性を無限追求することも禁止する。

## 17. Closure前の次Phase設計・工程分解

2026-08-30のUser決定により、原則としてCurrent PhaseのFormal Closure前に、現時点で可能な範囲の
次Phase設計、工程分解、Acceptance Candidate、Authority／Resource境界およびProvider Handoff候補を作る。

これにより、Current PhaseのContextとManual Evidenceが鮮明な間に次Phaseへ接続し、Closure後の再読、
Compactionおよび設計停止Costを下げる。ただし、設計書の作成は次Phaseの実装開始Authorityを生成しない。

Stable詳細Rule：

`docs/project/shared/task_roles/next_phase_design_before_current_phase_closure_operating_rule_ja.md`

Phase 7からこの順序を適用し、Phase 8設計・工程分解後にPhase 7 Formal Closureへ進む。
