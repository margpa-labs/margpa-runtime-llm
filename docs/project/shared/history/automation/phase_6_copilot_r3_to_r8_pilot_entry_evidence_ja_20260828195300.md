# Phase 6 Copilot R3〜R8 Pilot Entry Evidence

```yaml
document_id: phase_6_copilot_r3_to_r8_pilot_entry_evidence_20260828195300
document_type: provider_pilot_entry_evidence
document_state: append_only
language: ja
created_at: 2026-08-28 19:53:00 JST
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
active_contract: docs/project/phases/phase_6/handoffs/phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_ja_20260828193037.md
active_contract_sha512: a71d747d4715c550ebc51de5c543bcd76be520329c500bfe57ac15a1bf079d67f14e249134e079d9f49a7c374de0ae7072fa63d1f0da0bb8d93d77baafba2bab
entry_work_unit: P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED
temporary_root: .venv/.t/phase_6_copilot_continuation_20260828193037/
```

## Entry Boundary

UserのExact Startを受領した。User Backup Gateは完了済みであり、CopilotはBackupを取得、検査または変更しない。

R3 Current Partial七Fileは保全し、Phase 6 Package 0〜I、Claude K〜Q accepted scope、Rework R0〜R2を再実装しない。R3-WU-001〜008をCurrent Source、Current TestおよびFocused／Static Evidenceから再導出し、不成立または中断箇所だけを差分実装する。

## Authority and Action Inventory at Entry

```text
Authorized Root: <PROJECT_ROOT>
Git: prohibited, including read-only
Network / MCP / external account: prohibited
Provider Memory: prohibited
User runtime_data: prohibited
Project Root outside action: prohibited
Real Model load / inference / artifact access: prohibited
Backup / Phase 6 Closure / Phase 7: prohibited
Stable Shared Docs / Roadmap / Public Docs / Constitution mutation: prohibited

This Copilot execution before this entry artifact:
  Source / Test / Config / Frontend mutation: 0
  Command: 0
  Git action: 0
  Network action: 0
  Provider Memory action: 0
  User runtime_data action: 0
  Root-outside action: 0
  Real Model action: 0
```

## Mandatory Reading and Digest

Mandatory Reading 29件を指定順で全文読了した。Active Handoff、Controller R3 ReconstructionおよびCopilot Stable 3文書のSHA-512はすべてMATCHである。

## Initial State

```text
R0〜R2: PACKAGE_COMPLETE / PRESERVED
R3: PARTIAL / UNVERIFIED / Current Source preserved
R4〜R8: NOT STARTED
P6-CODEX-064: OPEN / R3 target
P6-CODEX-065: OPEN / R4 target
P6-CODEX-066: OPEN / R5 target
P6-CODEX-067: OPEN / R6 target
P6-CODEX-068: ACKNOWLEDGED / R8 final correction target
Historical Unauthorized Git Read: 1 / preserved
```

## Exact Next Action

`P6-RR-R3-WU-001_REDERIVATION_WITH_CURRENT_PARTIAL_PRESERVED`
