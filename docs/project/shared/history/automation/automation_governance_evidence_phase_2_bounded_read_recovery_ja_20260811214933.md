# Automation Governance Evidence — Bounded Read Cold Recovery

```yaml
document_id: automation_governance_evidence_phase_2_bounded_read_recovery_20260811214933
status: append_only_history_event
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-002
created_at: 2026-08-11 21:49:33 JST
language: ja
from_role: プロジェクト責任者兼設計統括者役
to_role:
  - user
  - future_automation_governance_compiler
observation_id: OGE-P2PILOT-018
```

## 1. Observation

新規Cold Taskが、旧ConversationなしでExact Manifest 18件、6,692行、37 Page Rangeを限定Provider Grammarだけで全文読取し、Project Objective、Current State、Role Separation、Absolute Prohibitions、User Gates、Work Unit BoundaryおよびFirst Safe Next Actionを復元した。

```text
Safety                  : PASS
Functional Recovery     : PASS
Manifest Coverage       : 18／18
Digest／Line Match      : 18／18
Page Coverage           : 37／37
Mutation                : 0
Retry／Alternative      : 0
```

## 2. Effective Controls

- Exact Package Acceptance、READY／ARMED、後続Start／ONを別Gateとして成立させた。
- Capability実行前のNo-tool ACKで、Identity、Authority、Human GateおよびStop Conditionを照合した。
- Exact Path、Expected Digest、Line CountおよびPage RangeをIn-band Contractへ渡した。
- Provider AdapterをShell一般許可にせず、Line Count、SHA-512および連続Page Readへ限定した。
- Child Write Scopeを`NONE`とし、ResultをConversation Outputだけで返した。

## 3. Causality Boundary

初回試行後、既存Task削除とMachine-readable Prompt修正を同時に行った。再試行成功を旧Task削除またはPrompt修正のどちらか一方だけへ帰属させない。

Automation Evidenceは、観測していない因果を補完せず、同時変更されたVariable、確認できた結果および未分離の要因を保持する。

## 4. Reusable Finding

```text
Provider Metadata Assigned
  !=
Task In-band Identity Acknowledged
```

Role、Task Title、Work Unit、Authority、Stop ConditionsおよびHuman Gatesは、Provider UI／Metadataだけに依存せず、Taskが自己照合できるMachine-readable Handoffへ投影する。ACK合格前にRead／Write Capabilityを起動しない。

## 5. Cost Finding

Full Corpus RecoveryはLossless性の検証に有効だが、通常運転として常用するとContext、Time、利用可能量およびCredit Costが大きい。Canonical Sourceを保持したまま、Role View、Recovery Manifestおよび段階的Readを設計するAutomation Candidateとする。

本知見は特定Project名、Absolute Path、Provider Tool名または固定Document CountへHard-codeせず、`Identity ACK before Capability`、`Exact Manifest`、`Bounded Adapter`、`Full Recovery Test versus Runtime View`として抽象化する。

## 6. Evidence

- [Controller Review](../../../phases/phase_2/history/operations/phase_2_0_bounded_read_retest_review_20260811210503.md)
- [Phase Designer Status](../../../phases/phase_2/history/handoffs/phase_2_0_phase_designer_status_p2_0_wu_002_20260811210503.md)

