# GitHub Copilot app試運転前Configuration／Authority／Evidence Capture Baseline

```yaml
document_id: copilot_app_pre_pilot_configuration_authority_and_evidence_capture_baseline
document_type: shared_history_automation_evidence
document_state: append_only
language: ja
created_at: 2026-08-28 19:19:37 JST
provider: GitHub Copilot app
pilot_state: not_started
authority_state: rules_created_handoff_not_created
decision_authority: user
```

## 1. 目的

GitHub Copilot appを第3の開発Provider候補として初めて本Projectへ導入する前に、User-observed Configuration、未検証能力、Authority境界、Evidence取得方針およびPilot開始前Gateを固定する。

本EvidenceはCopilotの実装品質または能力評価ではない。試運転前のBaselineである。

## 2. User-observed Configuration

2026-08-28、UserはGitHub Copilot appへ本Repositoryを追加した。UI上で次を観測している。

```text
Application: GitHub Copilot app
Mode Label: Autopilot
Model Label: GPT-5.6 Terra
Reasoning Label: High
Context Label: 400K
Project Label: MARGPA-RUNTIME-LLM
Harness: User設定により承認要求を緩和した状態
Alternative Context Label: 1.1Mを選択可能とのUser観測
```

Userは、利用可能量消費が不明なため`1.1M`を選ばず、`400K`と`High`で開始準備している。

これらはすべて`USER_OBSERVED_UI_CONFIGURATION`である。Modelの内部Revision、実Context、Auto-compaction閾値、Cost、Tool権限、Session継続、Background実行または自動再開を証明しない。

## 3. 導入目的

Copilotを単なる予備実装Providerとしてだけでなく、次の研究Evidenceを得る対象とする。

- Automation／Long-running。
- Cross-provider Handoff／Review／Rework。
- Manual／Auto CompactionとRecovery。
- Agent間Role分離。
- Codex側Task間情報共有との比較。
- Provider非依存RuleとProvider固有Ruleの分離。
- `margpa-runtime-llm/constitution/`への将来材料。
- `docs/project/shared/constitution/`への将来材料。
- Portable Autonomous Development Governance Packageへの将来移植材料。

## 4. Pilot前Authority State

```text
Copilot Role Rules: CREATED
Copilot Long-run Rules: CREATED
Copilot Internal Review Rules: CREATED
Copilot Exact Handoff: NOT CREATED
Copilot Exact User Start: NOT ISSUED
Copilot Implementation Authority: FALSE
Copilot Source／Test／Config Mutation: 0 known
Copilot Command／Git／Network／Model Action: 0 known
Backup before Handoff: PENDING USER ACTION
Claude stopped-state progress rederivation: PENDING DISCUSSION
```

Userは、Copilot用Exact Handoffを作る前にBackupを取得する方針を明示した。したがってBackup確認前にHandoffを発行せず、実装を開始させない。

Claudeが停止した時点の成立済み範囲、Open Finding、未完了Work Unit、Incidentおよび利用制限状態は、本Evidenceでは推測しない。後続会話でExactに再導出してからCopilotへ差分Scopeを渡す。

## 5. 作成したStable Rule

1. `docs/project/shared/task_roles/copilot_side_designer_implementer_operating_notes_ja.md`
2. `docs/project/shared/task_roles/copilot_side_long_running_automation_companion_ja.md`
3. `docs/project/shared/task_roles/copilot_side_implementation_internal_review_rework_loop_operating_contract_ja.md`

これらはPre-pilot時点からStable Currentとして扱う一方、Copilot固有能力の記述は`pre_pilot_unverified`である。Pilot Evidenceにより修正が必要になった場合、既存Historyを改変せず、新Evidence、Controller ReviewおよびUser Decisionを経てStable Ruleを改訂する。

## 6. 未検証項目

初回Pilotでは、少なくとも次を個別にEvidence化する。

1. Fresh TaskのRole／Authority Bootstrap理解。
2. Absolute Path、Mandatory Reading、Digest Receiptの精度。
3. Source／Test／Docs WriteおよびCommand実行能力。
4. Authorized RootとProject内Temporaryの遵守。
5. Git／Network／Provider Memory／User Dataへの暗黙接触有無。
6. Autopilot中のRoutine Confirmation頻度。
7. Long-running継続、Progress Report後の自走。
8. Work Unit／Package Recovery Indexの作成能力。
9. Internal Review／Finding／Rework／Re-reviewの成立。
10. Context圧縮の発動、認識、保持／欠落、復旧。
11. 5時間／週間／Credit等の利用制限と停止挙動。
12. 利用制限後の自動／手動再開能力。
13. Stopped-safe、Exact Return HandoffおよびControllerへの返却精度。
14. UI Labelと実Execution Identityの一致。
15. `400K`とResource消費の実測関係。

## 7. Evidence Capture Plan

初回Pilotでは、次の順にAppend-only Evidenceを残す。

```text
Pre-pilot Baseline（本書）
→ Fresh Role／Authority Receipt
→ Exact Handoff／Digest Receipt
→ Pilot Entry Boundary
→ Work Unit Recovery
→ Package Recovery
→ Compaction／Resource／Incident Evidence
→ Implementation Freeze
→ Internal Review／Rework Evidence
→ Complete／Incomplete／Stopped-safe Return
→ Codex Independent Review
→ User Manual Acceptance
→ Cross-provider Empirical Assessment
```

同じ内容を細切れに複製せず、Provider特性、RecoveryまたはAcceptanceを再現できる意味あるBoundaryで記録する。ただし初回Pilotは、後続Pilotより高い頻度を維持する。

## 8. Pilot Entry Sequence

Pilot開始前のExact順序は次とする。

1. UserがBackupを取得し、その完了を明示する。
2. Claude停止時点のEvidence／Recovery／HandoffからCurrent Stateを再導出する。
3. Copilotへ渡す差分Scope、成立済み範囲、再実行禁止範囲およびOpen FindingをFreezeする。
4. ControllerがCopilot用Copy-paste Instruction Packageを作る。
5. Fresh Copilot TaskへRole／Authority Bootstrapを送り、Receipt後に停止させる。
6. 三つのCopilot Stable RuleとExact Handoff／Mandatory Readingを読ませ、Digest Receipt後に停止させる。
7. UserがExact User Startを送る。
8. CopilotがPackage／Work Unit単位で実装、Recovery、内部Review、Rework、Returnを行う。
9. Codex ControllerがIndependent Reviewする。

## 9. Handoff未作成の理由

本時点では、次の二Gateが未成立である。

- UserによるBackup完了。
- Claude停止時点のCurrent State／残Scope確定。

したがって、本作業ではCopilot Stable RuleとPre-pilot Evidenceだけを作成し、Copilot用Exact Handoff、Execution Instruction、Source／Test／Config Mutation、Copilot実行またはPhase 6 Claimを行わない。

## 10. Current Decision

```text
Decision: PREPARE RULES AND EVIDENCE ONLY
Copilot Pilot: NOT STARTED
Backup Gate: REQUIRED BEFORE HANDOFF
Claude Progress Review: REQUIRED BEFORE HANDOFF
Next Action: User Backup → Claude State Discussion → Exact Copilot Handoff Creation
```
