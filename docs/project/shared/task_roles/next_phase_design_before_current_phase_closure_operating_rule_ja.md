# Current Phase Closure前の次Phase設計・工程分解運用Rule

```yaml
document_id: next_phase_design_before_current_phase_closure_operating_rule
document_type: shared_stable_normative_operating_rule
document_state: current_stable_authority
language: ja
created_at: 2026-08-30 19:09:30 JST
decision_authority: user
authority_owner: Nazuna Research
applies_to:
  - project_responsible_design_controller
  - codex_claude_copilot_designer_implementer
  - future_provider_agents
priority: user_current_operating_rule
```

## 1. Rule

原則として、Current Phaseの中心機能、Controller ReviewおよびUser Manual AcceptanceがClosure可能な
状態へ到達した後、Formal Closureへ入る前に、現時点で可能な範囲の次Phase設計と工程分解を行う。

```text
Current Phase実装・Review・Manual Acceptance
→ Closure Candidate判定
→ 未解決／延期／Evidence固定
→ 次Phaseの現時点設計・工程分解
→ Current Phase Formal Closure
→ Roadmap／Current／Continuity更新
→ Clean／Commit／Push／Backup等のClosure Gate
→ 次Phase READY／Preflight／開始
```

## 2. 目的

- Current PhaseのContext、実装知識、Manual Evidenceおよび未解決境界が鮮明な間に、次Phaseへ引き継ぐ。
- Closure／Compaction／Task切替後の情報損失と再読Costを下げる。
- 次Phase開始後に、設計不足で実装を止める回数を減らす。
- Providerへ渡すExact Handoff、Package、Work UnitおよびAcceptanceの準備を先に成立させる。
- 次Phase設計でCurrent PhaseのBlockerが発見された場合、Closure前に正しく分類できるようにする。

## 3. Closure前に作る最小成果物

次Phaseについて、現時点のEvidenceで確定できる範囲だけを対象に、少なくとも次を作る。

1. 目的、Non-goalおよびPoC／MVP Stop Line。
2. As-built BaselineとReuse対象。
3. Requirement／Architecture候補。
4. Package／Work Unitへの工程分解。
5. Dependency、順序、並列可能範囲。
6. Acceptance CandidateとUser Manual Gate。
7. Risk、Authority、Network、Git、Model、Hardware、Resource境界。
8. Recovery Index／Handoff／Compaction Strategy。
9. Claude／Codex／Copilot等のRole分担候補。
10. 未確定事項、設計時点AssumptionおよびPreflightで再確認する項目。

次Phaseの全情報が揃うまでCurrent Phase Closureを無期限に止めない。確定できない項目は
`TBD_AT_PREFLIGHT`、`AUTHORITY_REQUIRED`または`USER_DECISION_GATE`として正直に残す。

## 4. Authority境界

Closure前の次Phase設計は、次Phase実装開始ではない。

```text
Design／Decomposition作成 : 許可Scope
Next Phase Source Mutation : 不許可
Next Phase Tool実行        : 不許可
Next Phase External Action : 不許可
READY／開始Claim           : Formal Gate前は不許可
```

設計、Handoff、Preflightおよび実装開始Authorityを分離する。設計書が存在することを、実行許可、
Resource確保、Network許可または外部Provider Authorityの成立と同一視しない。

## 5. Current Phaseへの逆流Control

次Phase設計中に新しい改善候補を発見しても、Current Phaseへ無制限に戻さない。

- Current Phase P0 Closure Blockerなら、Evidence付きで最小Reworkを判断する。
- P1以下、将来機能、UI PolishまたはHardeningなら、未解決Registry／Planned Workへ送る。
- 次Phase設計の完全性を理由にCurrent Phase Closureを無期限延長しない。
- Userが次Phase設計後にClosureを指示した場合、勝手に追加実装へ進まない。

## 6. 例外

次の場合、完全な設計工程をSafe Boundaryで中断し、最小Recoveryを残してFormal Closureを先行できる。

- Userが明示的にClosure優先を指示した。
- 利用可能量、5時間制限、金銭、睡眠またはHardware Reserveが危険域へ入った。
- 次Phaseの前提が外部Authority、契約、HardwareまたはUser Decision待ちで設計不能。
- Current Phaseを閉じないこと自体がData、Git、BackupまたはContinuity Riskになる。

例外適用時は、未作成設計項目とExact Next ActionをRecovery／Planned Workへ残す。

## 7. Phase 7からの適用

本RuleはPhase 7 Closureから適用する。Phase 7のFormal Closure前にPhase 8の現時点設計・工程分解を
行い、その後にRoadmap 2種を含むClosure作業へ進む。Phase 8設計の実作業はUserの次Turn指示を待つ。

