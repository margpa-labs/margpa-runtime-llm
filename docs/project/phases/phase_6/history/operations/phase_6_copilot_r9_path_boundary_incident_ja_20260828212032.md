# Phase 6 Copilot R9 Path Boundary Incident

```yaml
document_type: automation_incident
created_at: 2026-08-28 21:20:32 JST
provider: GitHub Copilot app
package: P6-RR-R9
severity: contained
incident: initial_test_command_resolved_from_workspace_parent
external_contact: none
network: false
git: false
model_load: false
user_runtime_data: false
source_test_config_mutation: false
```

最初のFocused Test commandはcanonical rootの親directoryから`.venv/bin/pytest`を解決しようとし、exit 127となった。Source/Test/Config/Stable Docsには変更を加えていない。task-owned temporary directoryが親workspace側に一度作成されたため、以後のcommandは明示的にcanonical rootへ`cd`し、task temporary rootもcanonical root内だけを使用する。

これは停止理由にはせず、Active Contract §6.6に従いTool実行因果が確認されたBounded incidentとして記録する。
