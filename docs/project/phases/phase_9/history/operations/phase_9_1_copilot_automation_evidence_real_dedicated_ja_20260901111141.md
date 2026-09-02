# Phase 9-1 Copilot Automation Evidence — Real Dedicated

```yaml
document_id: phase_9_1_copilot_automation_evidence_real_dedicated_20260901111141
document_state: evidence_recorded
language: ja
created_at: 2026-09-01T11:11:41+09:00
phase: phase_9
program: phase_9_1
scope: p9_codex_006_to_010
```

## 1. Real Selene / Qwen3Guard Smoke (Authority ON)

実行コマンド:

```text
./.venv/bin/python - <<'PY'
# dedicated role adapter preflight/load/inference/unload smoke
PY
```

主要結果:

```json
{
  "selene": {
    "preflight_ready": true,
    "provider_id": "judge.selene-1-mini-llama-3.1-8b-q5-k-m",
    "provider_state": "active",
    "result_count": 1,
    "failure_reason": null,
    "dispositions": ["deviation"]
  },
  "qwen3guard": {
    "preflight_ready": true,
    "classifications": [
      {"target": "guardrail.input", "failure": "none"},
      {"target": "guardrail.context_source", "failure": "none"},
      {"target": "guardrail.output_candidate", "failure": "none"}
    ]
  }
}
```

## 2. Bounded Timeout/Cancel Negative Path with Drain

実行コマンド:

```text
./.venv/bin/python - <<'PY'
# Qwen3GuardDetectorAdapter with 1ms budget + tracked worker registry
PY
```

主要結果:

```json
{
  "outcome": "unknown",
  "category_id": "unknown_unresolved",
  "elapsed_ms": 2,
  "leases": 1,
  "releases_after_shutdown": 1,
  "registry_clean_shutdown": true
}
```

`timeout`後のlate resultを採用せず、worker完了をdrainしてからunloadできることを確認。

## 3. Full Validation

```text
./.venv/bin/pytest -q
=> 2216 passed, 7 deselected

./.venv/bin/ruff check
=> All checks passed

./.venv/bin/mypy src tests
=> Success: no issues found in 558 source files
```
