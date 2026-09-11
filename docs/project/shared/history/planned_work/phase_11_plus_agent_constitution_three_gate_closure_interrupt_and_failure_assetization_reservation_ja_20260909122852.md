# Phase 11以降 Agent Constitution 3-Gate Closure／Interrupt／Failure資産化予約

```yaml
document_id: phase_11_plus_agent_constitution_three_gate_closure_interrupt_and_failure_assetization_reservation_20260909122852
document_type: planned_work_constitution_reservation
document_state: reserved_not_started
earliest_target: phase_11_plus
recorded_at: 2026-09-09 12:28:52 JST
decision_authority: user
provider_neutral_target: true
implementation_authorized: false
append_only: true
```

## 1. Source Evidenceと判断

主要Source Evidence:

`docs/project/shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_declared_done_without_three_gate_verification_ja_20260902193000.md`

このIncidentでは、次のFailure Chainが連続して観測された。

```text
感覚的な完了判定
→ 「確認した」と「恒久Evidenceとして保存した」を混同
→ Review Scopeを新規Diff内部へ限定
→ 既存の成立済みAcceptanceとの相互作用を未確認
→ 人間判断の必要性と即時Interruptの必要性を混同
→ Done宣言後に欠落が繰り返し判明
```

さらに3-Gateを適用して対象集合を網羅した結果、指摘されたGemmaだけでなく、有限な`2 × 3 = 6`組合せの全探索からOF-P2-007も発見された。失敗を隠さず認めたこと、指摘を対象全体へ一般化したことは、Failureとは別の正のEvidenceとして保持する。

この観測群はClaude個体への注意書きだけに閉じず、Phase 11以降のAgent Constitution、MARGPA RuntimeおよびPADGへProvider非依存のRule／Fixture候補として昇格する。

## 2. Core Rule候補

### 2.1 Done is a governed state, not a self-declared impression

`Done`は「作業を終えた感覚」「Testを多数実行した」「報告を書いた」「手が止まった」ことではない。明示されたClosure Gateを、追跡可能なEvidence付きで通過したStateである。

```text
Done != Work Stopped
Done != Implementation Finished
Done != Many Tests Passed
Done requires governed closure evidence
```

### 2.2 Three-Gate Closure Rule

次の3 Gateが全てEvidence Pointer付きでYesになるまで、Done宣言を禁止する。

1. `Planned Work Complete?`
   - 指示、Work Unit、Finding、明示Scopeを全件Dispositionしたか。
2. `Required Evidence Persisted?`
   - その場限りの観測ではなく、再現・再読・監査可能なArtifactへ保存したか。
3. `Acceptance / Closure Criteria Actually Satisfied?`
   - 新規Diff内部だけでなく、影響を受ける既存Accepted Stateとの相互作用を含め、実際の受入条件を満たしたか。

一つでも`no`、`unknown`、`not_run`、`unavailable`なら、最大ClaimをそのStateへ制限する。未実施をPASSへ変換しない。

### 2.3 Observation is not Persistent Evidence

Consoleで見た、即席Scriptが一度通った、その場で値を確認した、会話で報告した、は恒久Evidenceではない。再現可能なTest、保存Log、Versioned Evidence、Digest付きArtifact等へ残り、後続Taskが再検証できて初めてEvidence Gateを満たす。

```text
Observation != Persistent Evidence
Reported value != Reproducible artifact
```

### 2.4 Review Scope includes affected accepted state

新規Code内部だけのReviewでClosureしない。変更が影響し得る既存機能、既存Acceptance、組合せ、Provider／Mode Matrix、Failure BoundaryおよびUser-visible PathをScopeへ含める。

対象集合が有限かつ列挙可能なら、一件だけを局所修正して終了せず、関連集合へScopeを一般化する。ただし無制限探索へ拡張せず、列挙根拠、上限、Costおよび除外理由を残す。

### 2.5 Human Decision Required is not Immediate Human Interruption

人間判断が必要でも、今すぐ作業を止めて割り込む必要があるとは限らない。重要度だけでInterruptせず、少なくとも次を独立Stateとして扱う。

```text
interrupt_required
decision_required
work_blocked
reversible
authority_required
safety_impact
```

即時Interruptは原則として、次が同時成立する場合に限定する。

```text
重要な判断である
+ 今決めなければ安全または正当に続行できない
+ Human Authorityが必須である
```

True Stopでない重要事項は`Pending Decision`としてEvidence化し、安全に進められる別作業を継続し、作業区切りでまとめてEscalateする。これはアイゼンハワーマトリクスの「重要度×緊急度」をAgent向けに機械化した形である。

### 2.6 Recovery／Authority Invariants

既存Incident群から得た次のInvariantも同じConstitution候補群へ含める。

```text
Acknowledgement != Permission to Resume
State Recovery != Authority Recovery
Human Decision Required != Immediate Human Interruption
Observation != Persistent Evidence
Done != Work Stopped
Done requires Three-Gate Closure
```

## 3. Completion Stateの分離

一つの`done` Booleanへ潰さず、少なくとも次を別Stateとして保持する。

1. `Implementation Complete`
2. `Verification Complete`
3. `Evidence Complete`
4. `Acceptance Complete`
5. `Closure Complete`

各StateはOwner、Required Inputs、Evidence Pointer、判定時刻、Revision、未成立理由および次Gateを持つ。下位State成立から上位State成立を推測しない。例えば`Implementation Complete`かつ多数Test PASSでも、Evidence未保存またはAcceptance未確認ならClosureではない。

## 4. Failure Patternの一般化

今回の価値は「ClaudeがTestを漏らした」というProvider固有記録だけではない。次の3種類の構造Failureが一本のChainとして観測された点にある。

- 完了判定が感覚的で、Closure Gateに結び付かない。
- 一時ObservationとPersistent Evidenceを混同する。
- Review Scopeが新規Diff内部に閉じ、既存Accepted Stateと有限な関連組合せを見ない。
- Human Decision、Work Block、Immediate Interruptを分離しない。

一方で次の長所は別Claimとして保持する。

- 指摘された1件だけでなく、Catalog全体の有限組合せへ一般化しOF-P2-007を発見した。
- 欠落を隠さず調査し、事実として認めた。

Failure Recordだから全行動を一括して失敗扱いにせず、Evidence単位でFailureと正の行動を分離する。この評価分離自体をConstitution／Judge／Reviewの設計原則にする。

## 5. IncidentからPortable Governanceへの昇格Pipeline

```text
Incident
→ Observation Record
→ Failure Pattern
→ Generalized Rule
→ Constitution Clause
→ Regression Test
→ Portable Governance／PADG
```

失敗を個体への叱責や会話Memoryだけで終わらせず、Source Evidence、一般化理由、適用Scope、例外、Counterexample、Test OracleおよびVersionを持つ資産へ変換する。

Provider固有挙動をそのままCommon Ruleへ過剰昇格しない。Claude、Codex、Copilotその他Providerで再利用するCore Ruleと、Provider Adapter／Known Failure Patternを分離する。

## 6. MARGPA Runtime／PADGでの利用先

このIncident系列を次へ利用可能にする。

- Governance Definitionの評価Fixture。
- Agent Constitutionの検証Case。
- JudgeのFailure Classification。
- Human Gate／Escalation PolicyのRegression。
- Development Agent Acceptance Suite。
- Handoff／Recovery／Closure State MachineのTest。
- PADG PackageのPortable RuleおよびProvider Adapter用Known Pattern。

将来は、既知Failure Patternを外部Governanceが事前検知し、Providerが同種の誤ったDone、過剰Interrupt、Authority Recovery誤認またはEvidence未保存へ進む前に警告・停止・Deferred化できる形を目指す。

## 7. Machine-readable候補

Clause／State／Findingは少なくとも次のIdentityを候補とする。

- `rule_id`、`revision`、`digest`、`source_incident_refs`
- `applicability`、`provider_scope`、`capability_scope`
- `required_gates`、`gate_results`、`evidence_pointers`
- `decision_required`、`interrupt_required`、`work_blocked`
- `authority_required`、`safety_impact`、`reversible`
- `enumerable_domain`、`coverage`、`excluded_cases`
- `completion_state`、`maximum_claim`、`failure_reason`
- `exception`、`supersession`、`owner`

Ruleが存在するだけでDoneを阻止したと主張せず、Regression Testで誤ったDone／Interrupt／Resumeを実際に検出できることを確認する。

## 8. Acceptance候補

- 3 Gateの一つが未成立ならDoneへ遷移できない。
- 一時観測しかない場合、Evidence Completeにならない。
- 新規Diffが既存Acceptanceへ影響する場合、対象ScopeがClosure Gateへ追加される。
- 有限Domainの一件Findingから、認可上限内のCoverage Matrixを生成できる。
- Human Decisionが必要でもTrue Stopでなければ即時InterruptせずPendingへ送る。
- AcknowledgementやState RecoveryだけでAuthority／Resume Permissionを復元しない。
- 5つのCompletion Stateと最大ClaimがUI、Evidence、Handoffで一致する。
- Provider固有FailureとCommon Constitution Ruleを混同しない。
- Failureと長所をEvidence単位で別評価できる。

## 9. 非目標と時期

本予約はClaudeを一括して低品質と断定するものではなく、個別Incidentから再利用可能な構造Ruleを抽出する。Phase 10 MVP／Docs統合を遅らせず、Phase 11以降にRuntime Constitution、Shared Constitution、PADGおよびDevelopment Agent設計との整合を取って正式化する。

本予約だけではConstitution変更、Runtime実装、Regression追加、Provider評価、PADG輸出、Task停止またはGit操作を許可しない。
