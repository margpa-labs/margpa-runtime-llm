# Phase 6 Copilot R3〜R8 Complete Candidate Return Handoff

```yaml
document_type: exact_return_handoff
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Fresh Copilot Phase 6 Differential Continuation Task
active_contract: phase_6_copilot_post_claude_r3_to_r8_exact_continuation_handoff_ja_20260828193037.md
result: COMPLETE_CANDIDATE_WITH_REAL_PROVIDER_AUTHORITY_GATE
next_exact_action: Codex_Controller_Independent_Review
```

R3 Current PartialをRollbackせず再導出し、R3〜R8を差分完了した。P6-CODEX-062〜068はauthority-independent scopeでfixed。R5では全ENFORCE Safe FallbackをFrozen Language/Failure Classへ統一し、R6ではbounded poll、Provider none、Recording correlation、Activation Failure timestampを投影した。

Verification: Backend Full 1700 passed（7 model_smoke deselected）、Mypy/Ruff success、Frontend typecheck/lint、229 passed、build success。Real Selene/Qwen3Guard artifact load/inference、Official Provenance、Browser manualはNOT RUN / AUTHORITY REQUIRED。

Incident: Copilotが中間Progressをfinal応答として返して不適切に停止した。マイクアクセス観測はProvider UI挙動として記録済みで、Copilot Action Inventoryにマイク/Browser/Network/OS Permission操作はない。

Action Inventory: Git 0、Network 0、Provider Memory 0、runtime_data 0、Root外Command 0、Real Model Load/Inference 0。Pilot/Recovery: R3 Entry/Final、R4 Entry/Final、R5 Entry/Final、R6 Final、R7 Final、R8 FinalをPhase 6 history/indexに作成した。Codex Independent Reviewまで停止する。
