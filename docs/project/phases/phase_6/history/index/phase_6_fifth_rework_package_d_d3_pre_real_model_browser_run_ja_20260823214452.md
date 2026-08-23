# Phase 6 Fifth Rework — Package D D-3実Model／Browser Pre-run Entry

```yaml
document_id: phase_6_fifth_rework_package_d_d3_pre_real_model_browser_run_20260823214452
status: recovery_entry_pre_run
phase: phase_6
package: package_d
material_boundary: d_3_pre_real_model_browser_run
owner_role: 設計者兼実装者役
created_at: 2026-08-23 21:44:52 JST
authority: phase_6_codex_controller_package_d_d2_resume_authority_ja_20260823213619.md
previous_entry: phase_6_fifth_rework_package_d_d2_acceptance_rederivation_ja_20260823214248.md
phase_closure_state: do_not_close
```

## 1. Pre-run State

```text
D-2 Acceptance再導出      : COMPLETE（84 ID、79 PASS／5 PARTIAL）
Active Process by this Task: 0
Active Model Load           : 0
Source／Test Mutation       : 0
User runtime_data Contact   : 0
Provider Memory Contact     : 0
Git Action                  : 0
Network External Action     : 0
New Cycle Root-outside Action: 0
```

## 2. Exact Authorized Runtime Targets

```text
Qwen:
  model_key = main.qwen3-4b-q4-k-m
  logical model root = <Project Root>/models

DeepSeek:
  model_key = main.deepseek-r1-0528-qwen3-8b-q4-k-m
  exact derived Q4_K_M artifact authorized by existing Phase 6 Model Authority

V4 Flash Local Call: 0
Model Artifact Mutation: 0
```

## 3. Task-owned Project-local State

次のPathだけを新規D-3 Temporary／Cache／Log／Conversation Storeとして使用する。

```text
.venv/.t/phase_6_fifth_rework_d3_20260823214452/
  server.log
  conversation_data/
  browser_evidence/
  pytest/
  cache/
```

本Entry作成後にDirectoryを作成する。Final Returnまで自己判断で削除しない。User `runtime_data/`、`other/`、Project Root外Temporary、`/dev/null`は使用しない。

## 4. Planned Matrix

1. Current Qwen Snapshot／Identity／Binding／Revisionを取得。
2. 同一Qwen Context Size変更でUnload→Reload→Commit、次Attempt／Context Usage／Evidence一致を確認。
3. Qwen→DeepSeek→QwenをServer再起動0で実行し、Identity／Artifact／Backend／MAIN Binding／Governance Capabilityを各Commit後に確認。
4. DeepSeek Multi-turnはPackage Bの変更後Evidenceを再利用しつつ、Browser上でConversation継続とSpecial Token Leakage 0を再確認。
5. Judge／Repair／Recording ModeとCurrent Request／Runtime Stateを確認。
6. Conversation／Citation／Branch／Reload／別Tab同期を確認。
7. Busy／Conflict／Load Failure RollbackはCurrent Focused Testで決定的に再確認し、実Modelを破壊的Failureへ誘導しない。
8. Serverを正常終了し、Task-owned Process／Model Load 0へ戻す。

## 5. Browser Execution Boundary

Browser SkillのInstruction FileはProject Root外にあるため本Authorityでは読まない。Repository内Server、Current Frontend Buildおよび利用可能なLocal Browser Controlだけを用い、外部Site／Networkへ移動しない。Browser EvidenceはLocal loopback `127.0.0.1`だけを対象とする。

## 6. Resume Procedure

中断時は本Entryから再開し、Task-owned Temporaryの残存、Server Sessionの有無、最後に成功したMatrix StepとExact Next Actionを新規Recoveryへ記録する。Package A〜C／D-1／D-2は再実行しない。

