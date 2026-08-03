# Executable Governance Constitution／Phase 2・3 Pilot Evidence設計記録

```yaml
document_id: executable_governance_constitution_and_phase_2_3_pilot_evidence_design
status: accepted_design_reservation
normative: false
phase: phase_1_ex
language: ja
created_at: 2026-08-04 04:51:58 JST
owner: 設計統括者役
decision_authority: user
rag_default: false
```

## 1. Decision

Phase 2以降の設計統括者役をProject責任者とする。ただしProject責任者も、絶対禁止事項、Docs規則、Authority規則その他の運用ルールの例外ではない。Project責任、Task編成Capability、長期運用上の信頼または承認待ち状態から、自己免除、自己Authority拡張または未列挙Actionの許可を生成しない。

承認、確認、Manual TestまたはUser Decisionを待つために安全に停止することは、運用ルール違反または責任放棄ではない。

## 2. Phase 2・3 Pilot

Phase 2の最初にDocument-driven Orchestration Pilotを実施する。最初は一つの有界なWork Unitを対象にし、Task作成、Task名設定、Authority設定、Handoff、Status、Follow-up、Review、停止およびRecoveryをAccepted Authorization Envelope内で連結する。

```text
Phase 2: Orchestration成立性の検証
Phase 3: 異なるPhaseでの再現性・移植性の検証
Later : EvidenceとUser Gateに基づく段階拡張
```

Phase 2の結果が`GO`または条件付き`ADJUST`としてAcceptedされた場合、Phase 3でもPilotを継続する。Phase 3では、異なるRequirements、担当Task、Context、Evidence Domainおよび実装対象でも同じControl Plane、Authority、Handoff、Review、StopおよびRecoveryが成立するかを確認する。

Pilot粒度は次の順序を候補とする。

```text
Bounded Work Unit
  → Connected Work Units
  → Subphase
  → Phase Completion
  → Project Completion
```

上位粒度への移行は自動ではなく、各段階のEvidenceとユーザー判断を必要とする。問題があれば粒度を縮小し、安全にPause／Stopする。

## 3. Agent／Tool前の統合憲法Gate

Agent／Toolを本格実装する前に、運用中に蓄積した次の規則とEvidenceを完全統合憲法へLossless Compilationする。

- 絶対禁止事項
- Authority／Delegation
- Docs正本／Stable／History／Lossless／Index
- Task Lifecycle／Handoff／交代／終了
- Mutation／Git／External Service／Secret／Cost
- Resource Limit／Context Limit
- Stop／Recovery／Backup
- Evidence／Audit／Review
- Incident／Deviation／Near Miss
- Exception／Emergency／改憲

Agentを高機能化する前に、Agentが存在、委譲、判断および実行してよい制度空間を先に定義する。

## 4. 単一巨大文書を避ける

統合された体系であっても、憲法を一枚の巨大Markdownにしない。長大Context、部分的な陳腐化、重複Rule ConflictおよびAgentごとの解釈差を避けるため、`constitution_index_ja.md`を正本入口とし、Scope、絶対禁止、Authority、Docs、Task、Mutation、Resource、Recovery、Evidence、Agent／Tool、Exceptionおよび改憲を章別に分離する。

Index、Revision、Digest、Rule IDおよびSource Traceabilityにより、分割文書を一つの正本体系として束ねる。

## 5. Rule ID／Priority／Exception

各Normative Ruleは一意なRule ID、分類、対象、規則、検知、違反時動作、復旧、EvidenceおよびSource Traceを持つ。

計画上の規範優先順位は次とする。

```text
絶対禁止／不可侵条件
  > 正式な例外／緊急承認
  > Phase Authorization Envelope
  > Role Authority
  > Phase Contract
  > Task Handoff
  > 通常の会話指示
  > 推測／慣例／善意
```

通常会話、Role名、Tool Permissionまたは効率を理由にAbsolute Ruleを上書きしない。例外可能なRuleの上書きは、理由、範囲、有効期限、承認者、復旧条件およびEvidenceを持つ正式なExceptionとして扱う。

## 6. Constitution View／Compiler候補

憲法全文を各Task、AgentまたはToolへ毎回手Copyしない。Canonical Constitutionを保持しつつ、Role、Phase、Task、ProviderおよびAuthorization Envelopeに応じて適用Ruleだけを抽出した`Constitution View`を派生させる。

ViewはRevision、Source Digest、Role、Read／Write Scope、適用Rule ID、禁止事項、Stop ConditionおよびEvidence義務を持つ。ViewはAuthorityを追加できず、Stale Revision、Digest不一致または未解決ConflictではFail-closedとする。将来、抽出と検証を行う`Constitution Compiler`へ拡張可能な構造を予約する。

## 7. Operational Evidence

Phase 2・3では成功だけでなく、次を記録する。

- 人間が介入しなければ危険だった地点
- Ruleが曖昧でも偶然成功した地点
- 停止すべきなのに進行しかけた地点
- Authority不足／過剰だった範囲
- Handoff不足、Context肥大化、Task交代閾値
- Resource／Credit消費
- Backupが必要だった変更規模
- 停止後の再開可能性
- 自動化可能な判断とHuman Gateが必要な判断

分類は次を予定する。

```text
RULE_EFFECTIVE
RULE_AMBIGUOUS
RULE_MISSING
RULE_OVERRESTRICTIVE
RULE_UNENFORCEABLE
HUMAN_GATE_REQUIRED
AUTOMATION_CANDIDATE
```

## 8. Constitution Research Preview

完全性を理由にAgent／Tool開始が永久延期されないよう、完成ではなく`Constitution Research Preview v0.x`の開始条件を定める。

- 重大な優先順位Conflictが解決済み
- 全Role Authorityが定義済み
- 全Absolute Ruleに違反時動作が存在
- Stop／Recovery／Backupが定義済み
- Evidence最低要件が定義済み
- Resource Limit処理が定義済み
- Task／Agent／Tool生成Authorityが定義済み
- 改憲／Version／Migration／Rollbackが定義済み
- Currentな人間＋AI Task運用で試験済み

開始後は曖昧Rule、Conflict、検知不能、過剰制限、Authority不足、Evidence CostおよびRecovery FailureをEvidence化して正式に改訂する。

## 9. Governance Test候補

- 許可Path外Mutationを拒否・停止できる。
- 古いConstitution Revision／ViewをStaleとして検出できる。
- Resource切れで未完了をCompleteにせず停止できる。
- Evidenceなしの完了報告をReviewが受理しない。
- Spawn AuthorityなしのTask生成を拒否できる。
- Project責任者の自己Authority拡張を検出できる。
- Absolute RuleとTask指示の衝突時に上位規範を選べる。
- 停止後にEvidenceから安全に復旧できる。

## 10. Current Boundary

本記録は設計予約である。Phase 2 Pilotの開始、Task作成、Agent／Tool実装、憲法Folder作成、Constitution Compiler実装、権限拡張、Git操作または外部操作を許可しない。

## 11. Related Documents

- [Cross-project Development Governance Constitution Plan](../../../../shared/operations/cross_project_development_governance_constitution_plan_ja.md)
- [Experimental Document-driven Codex Task Orchestration](../../../../shared/operations/experimental_document_driven_codex_task_orchestration_ja.md)
- [Phase 2 Subphase／Task Orchestration Preplan](../../../../shared/operations/phase_2_subphase_and_task_orchestration_preplan_ja.md)
- [Task Role／Write Authority Policy](../../../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Public Roadmap](../../../../../public/roadmap_ja.md)
