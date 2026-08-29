# Phase 6 Remaining Rework — Root-outside stderr Redirect Incident

```yaml
document_id: phase_6_remaining_rework_root_outside_stderr_redirect_incident_20260826094511
status: append_only_incident_stopped_safe
phase: phase_6
incident_id: P6-RR-INC-001
severity: critical_governance_stop
detected_at: 2026-08-26 09:45:11 JST
actor: current_designer_implementer_task
automation_state: stopped_safe
```

## 1. Exact Incident

P6-RR-C-WU-001のAs-built Read中、複数Fileを読むShell Commandの末尾へ、存在しないFileのstderr抑制を目的として次のRedirectを誤って含めた。

```text
2>/tmp/not_allowed
```

Target `/tmp/not_allowed` はAuthorized Project Root外である。Shell RedirectによりFile Createまたは既存File Truncateが起きた可能性があるため、Frozen Exact Handoff §6.2／§10のProject Root外Action禁止に抵触した。

## 2. Known／Unknown

```text
known actor       : current designer-implementer task
known action      : stderr shell redirection
known target      : /tmp/not_allowed
known occurrence  : 1 command
known cleanup     : 0
before state      : unknown
after existence   : unverified
after size/content: unverified
external impact   : unknown beyond the exact target
```

Project Root外への追加Stat／Read／Writeは違反を拡大するため実施していない。自動削除、移動、修復またはPermission変更も行っていない。

## 3. Functional／Governance Separation

- 事故前にP6-RR-0／A／Bを完了し、Focused Test 8 passed、Focused Mypy 25 files PASS、Focused Ruff PASSへ到達した。
- その技術成果は本Incidentを治癒しない。
- Incident検出後はSource／Test／Config実装を停止し、許可済みAppend-only Recovery／Incident／Returnだけを作成する。

## 4. Current Accounting

```text
Current task unauthorized Root-outside action : 1
Current task Git／Network／Install             : 0 / 0 / 0
Current task Provider Memory／runtime_data      : 0 / 0
Current task Model Artifact Mutation            : 0
Historical Phase 6 Process Incidents            : 3
Historical Phase 6 Root-outside Incidents       : 2
Historical Unauthorized Git Read                : 1
Current cumulative Process Incidents            : 4
Current cumulative Root-outside Incidents       : 3
```

## 5. Resume Condition

Controller／Userが本Incidentと`/tmp/not_allowed`の取扱いを判断し、P6-RR-C-WU-001からの新しいExact Resume Authorityを発行するまで、本Taskは`STOPPED_SAFE`を維持する。
