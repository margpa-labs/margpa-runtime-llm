# Phase 8 Copilot残7% Resource-bounded Entry Baseline

```yaml
document_id: phase_8_copilot_seven_percent_resource_bounded_entry_baseline_20260830195125
document_type: cross_provider_automation_evidence
document_state: final
language: ja
created_at: 2026-08-30 19:51:25 JST
provider: GitHub Copilot app
phase: phase_8
evidence_state: pre_execution_baseline
```

## 1. User Resource Signal

2026-08-30、Userから次が報告された。

```text
Codex Weekly Remaining   : 64%
Claude Weekly Remaining  : 42%
Copilot Weekly Remaining : 7%
```

UserはClaude分を節約し、Phase 8先頭をCopilotで実行して残量を使い、その後をClaudeへ渡す方針を決定した。CopilotはSession制限を理由に新しい`設計者兼実装者役`Taskが作られている。

## 2. Controller Disposition

CopilotへPhase 8全体を渡さず、過去のUser決定どおりManual URL Evidenceに対応する`P8-0／P8-A`へ限定する。

残7%では途中停止可能性が高いため、通常のPackage Finalだけでなく各Work Unit境界RecoveryをUserが特別指定した。これは恒常的なDocs増加Ruleではなく、今回のResource条件に比例した例外である。

## 3. Prior Copilot Evidence Kept

- 最初期Pilotでは不要停止／確認傾向が観測された。
- 後続の直近Copilot Reworkでは、User報告上、変な停止は1回もなかった。
- 実装速度は速い一方、Controller Reviewで作業漏れ／粗さが見つかる傾向があり、自己ReviewだけをIndependent Reviewへ昇格しない。
- CopilotがProject Rootの親側へ`.venv/.t`を作った過去Root境界FailureはHistorical Evidenceとして保持する。

上記事実から今回の挙動を事前決定しない。現在Taskの確認回数、停止理由、Recovery品質、Compaction／Session、Resource消費、Review Findingを新しいEvidenceとして取得する。

## 4. Pre-execution Observation

```text
Task Identity                 : Fresh Copilot Phase 8 Head Task
User-observed Model／Mode     : 今回のEntry時点では未再確認
Compaction／Auto-resume       : UNKNOWN
Exact Scope                   : P8-0／P8-A
Real Network／Git             : NOT AUTHORIZED
Focused Backend Baseline      : 64 passed
Focused Frontend Baseline     : 1 file／6 passed
Phase 8 Source Mutation       : 0
```

## 5. Evidence to Capture on Return

- CopilotがRoutine Confirmation／Progress報告で停止した回数。
- Resource／Session停止の時点と、直前Recoveryの有無。
- 各WU Recoveryから実際に差分再開できるか。
- Project Root外、Git、Network、Provider Memory、User DataへのAction。
- Internal Reviewで検出したFindingとController Reviewとの差。
- 実装速度、Test品質、Production Wiring、UI／Persistence漏れ。
- 最終的に消費したCopilot Resourceは、Userから値が得られた範囲だけ記録する。
