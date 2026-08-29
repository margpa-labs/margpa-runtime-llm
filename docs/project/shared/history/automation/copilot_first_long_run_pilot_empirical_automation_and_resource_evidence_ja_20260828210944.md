# GitHub Copilot app 初回Long-run Pilot — Automation／Resource実測Evidence

```yaml
document_id: copilot_first_long_run_pilot_empirical_automation_and_resource_evidence_20260828210944
document_type: cross_provider_automation_empirical_evidence
document_state: stable_historical_evidence
language: ja
created_at: 2026-08-28 21:09:44 JST
provider: GitHub Copilot app
role: 設計者兼実装者役
pilot_scope: Phase_6_P6_RR_R3_to_R8
model_ui_label: GPT-5.6_Terra
reasoning_ui_label: High
context_ui_label: 400K
autopilot: enabled_by_user
controller: Codex_プロジェクト責任者兼設計統括者役
```

## 1. 目的

GitHub Copilot appを第三Provider候補として初めて導入し、次を実測した。

- Stable Role Rule＋Frozen Exact HandoffによるFresh Cross-provider移管。
- R3 PartialをRollbackしない差分Long-run。
- Package／WU Recovery Cadence。
- Implementation→Internal Review→Rework→Re-review。
- Autopilot／Harness解除状態での不要確認・不要停止の有無。
- 400K Context表示下のCompaction／Resource挙動。
- Copilot固有Rule、将来ConstitutionおよびPortable Autonomous Development Governance Packageへ使えるEvidenceの採取。

## 2. Pilot設定と境界

Userが観測したCopilot UI設定：

```text
App       : GitHub Copilot app
Mode      : Autopilot
Model     : GPT-5.6 Terra
Reasoning : High
Context   : 400K
```

1.1M Contextは利用可能量消費が不明なため使用しなかった。Auto-compactionが実際に起きたというEvidenceは本Pilotでは得られていない。

## 3. 成立した点

- Fresh Role／Authority BootstrapとMandatory Reading Receiptが成立した。
- Contract Digest照合とPilot Entry Evidenceを作成した。
- Claude R3 PartialをRollbackせず、R3〜R8へ差分継続した。
- R3／R4ではWU単位Checkpointを高頻度で残した。
- Backend／Frontend／Staticへ実装し、Candidate Evidence上はBackend 1700、Frontend 229、Mypy／Ruff／Typecheck／Lint／Buildを完走した。
- Implementation Freeze、Internal Review 1、Internal Review 2、Return Handoffという形式自体は作成した。
- Real Model／Network Authority不足をPASSへ捏造せず、NOT RUN／AUTHORITY REQUIREDへ残した。
- Git／Network／Provider Memory／User runtime_data／Real Model Mutation 0を返した。

CopilotはSource実装能力とTest収束能力を示した。単なる閲覧補助ではなく、Phase 6の複数Componentを横断する実装主体として使用可能なEvidenceがある。

## 4. Automation Failure

### 4.1 不要停止

既存Evidenceで少なくとも4件を確認した。

```text
AUTO-STOP-001 : R6-WU-001後に不要停止
AUTO-STOP-002 : R3〜R5 Regression後に不要停止
AUTO-STOP-003 : User説明後も自動再開せず停止継続
AUTO-STOP-004 : Provider UIのTemporary Path表示をRoot外Action候補と誤認して停止
```

Userは、初期Claude Taskで観測された「確認したがり／報告したがり」に近い挙動と評価した。Frozen Contractは「Progress報告後も自走」「Finding／Test Failure／長時間は停止理由でない」と明示していたため、単なる慎重さではなくAutomation Contract不遵守である。

### 4.2 False-positive Root Boundary

Copilot UIまたはPlatform Tool Outputに`/var/folders/.../T/`相当が表示されたことと、Copilot自身がCommand／ToolでRoot外Actionを行ったことは同一ではない。本PilotではCopilot起因のRead／Write／List／Stat／Cleanupは立証されなかった。

External UI表示だけをTrue Stopへ昇格したことで、UserのManual Resumeを余分に要求した。

### 4.3 Internal Review／Returnの浅さ

Internal Review形式は作ったが、内容はP6-CODEX-062〜068をFixedと列挙する程度で、Requirement-by-Requirement、S1〜S17、Failure Injection、Cross-component Wiring、Original 40＋Delta 26を実際に再導出していなかった。

Return Handoff、FreezeおよびR8 Recoveryも短いSummaryであり、Frozen Return Contractが要求したExact File SHA、Acceptance全件、Identity／Budget／109／Language／Recording Matrixを欠いた。

これはAutomation Failureと実装Findingを分離して扱う。

- 実装成果：保全価値あり。
- Self-review／Claim Control：不十分。
- Complete Candidate Claim：Controller Reviewで棄却。

## 5. Resource Evidence

UserはPilot後、Copilot ProのAI Creditについて次を観測した。

```text
UI表示 : AI credits 61% consumed
残量   : 39%
Reset  : 約3日12時間後（当時のUI表示）
```

本PilotがCopilot初回の主要Long-runであったという会話Contextはあるが、61%全量が本Packageだけに起因したと厳密には証明しない。Model、High Reasoning、400K Context、再開回数、Source量、Test量の寄与は分離不能である。

少なくとも、CopilotもHeavy PhaseのLong-runで利用可能量を急速に消費し得る。残39%で次Reworkを行う場合、Package／WU RecoveryとResource Stop前Recoveryは必須である。

## 6. Provider比較へ使える暫定特性

```text
Implementation breadth        : 高い
Regression convergence        : 高い
Frozen scope understanding    : 中程度
Unattended continuation       : 低〜中
False-positive stop tendency  : 高い（初回Pilot）
Self-review evidence depth    : 低い
Claim calibration             : 不十分
Recovery artifact frequency   : 高い（前半）、後半は粗い
```

一回のPilotから恒久的なProvider特性へ一般化しない。今後のPhase 6 Rework、Phase 7以降およびPortable Package検証で更新する。

## 7. 次回運用Correction

1. Progress報告と停止を明確に分離する。
2. True StopはCopilot自身のActionとの因果を確認してから宣言する。
3. 各WU Checkpointを後半Packageでも省略しない。
4. Resource Hard Stop前にExact Next WU、Active Process 0、Mutation Inventoryを残す。
5. Internal ReviewはRequirement／Scenario／Failure Injection／Negative Path／Cross-component単位でEvidenceを付ける。
6. Return Contractの項目をCheck List化し、一項目も省略しない。
7. Complete Candidate ClaimはTest CountではなくContract全件から再導出する。
8. Copilot Return後もCodex Controller Independent Reviewを必須とする。

## 8. 正本Evidence

- `docs/project/shared/history/automation/phase_6_copilot_r3_to_r8_pilot_entry_evidence_ja_20260828195300.md`
- `docs/project/shared/history/automation/phase_6_copilot_pilot_unexpected_stop_and_microphone_ui_failure_ja_20260828200549.md`
- `docs/project/shared/history/automation/phase_6_copilot_pilot_repeated_unnecessary_stop_failure_addendum_ja_20260828202127.md`
- `docs/project/phases/phase_6/history/operations/phase_6_copilot_to_codex_automation_failure_report_ja_20260828202127.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov020_copilot_r3_to_r8_controller_independent_review_ja_20260828210944.md`

## 9. 暫定Decision

```text
Copilot as implementation provider : CONTINUE EXPERIMENT
Copilot unattended long-run        : NOT YET TRUSTED
Copilot self-review as final gate  : NOT ACCEPTED
Codex independent review           : MANDATORY
Resource-aware recovery            : MANDATORY
```
