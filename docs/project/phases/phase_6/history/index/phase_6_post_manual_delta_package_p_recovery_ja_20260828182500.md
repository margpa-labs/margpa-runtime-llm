# Phase 6 Post-Manual Delta — Package P Recovery（Observability／Recording／Bounded UI Delta）

```yaml
document_id: phase_6_post_manual_delta_package_p_recovery_20260828182500
package: P6-RR-P
completed_wu: P-WU-004 (Bounded Advanced Mode Layout, 全7項目), P-WU-005 (CLI Help Contract)
deferred_wu: P-WU-001 (Live Status Lifecycle自動更新 — Non-critical Open Findingとして記録), P-WU-002 (Recording Correlation単一Summary表示), P-WU-003 (Activation Failure詳細永続表示)
status: PACKAGE_COMPLETE_WITH_DEFERRAL
created_at: 2026-08-28 18:25:00 JST
next_exact_work_unit: P6-RR-Q-WU-001
task_owned_temp: .venv/.t/phase_6_claude_post_manual_delta_20260828161650/
git_action: NONE
root_outside_action: 0
provider_memory_action: 0
network_action: 0
runtime_data_action: 0
```

## 結論

P6-CODEX-058（User指定Bounded Advanced Mode／Sidebar UI Delta未実装）を解消した。全7項目（P-WU-004）を実装し、**実Backend（実Qwen Model Load済み）に対するReal Browser検証**で全項目を視覚的に確認した。P-WU-005（CLI Help）も修正した。P-WU-001〜003（Live自動更新、Recording単一Summary、Activation Failure永続表示）は、既存実装が部分的にこれらの要件を満たしていることを確認した上で、残る自動Poll機構の追加は本Packageでは見送り、Non-critical Open Findingとして記録する。

## P-WU-004 Bounded Advanced Mode Layout（全7項目実装）

### 1. Model Status内の重複Main Model切替Dropdown非表示

`RuntimeModelStatusPanel.tsx`：Legacy `/api/v4/runtime-model/switch`駆動のDropdownを`hidden`属性で非表示化（削除せず、Apply Contract・State共に保持——Rollback可能）。Context Size／Max New Tokens Controlは無変更で維持。

### 2. Advanced Mode順の変更

`SettingsModal.tsx`：`FeatureModesPanel`（Judge／Repair／Recording）を`RuntimeModelStatusPanel`（Model Status）より前へ移動。結果順：Judge／Repair／Recording → Model Status → Role Provider選択 → Runtime設定制御。Real Browserで確認済み。

### 3／4. Research・Developer Mode Control非表示、詳細を初期状態から表示

`ConfigurationControlPanel.tsx`：`developerDetailsVisible`Gate（`researchField?.value === "on"`）を削除し、Revision／Digest／Fieldsを常時表示に変更。OFF／ON Toggle自体は`hidden`属性で非表示化（Backend `onApply`Contractは無変更、削除なし）。`research_developer_mode` FieldをLEFT_COLUMN_FIELD_KEYSから除外。

### 5. 残る6 Fieldの左右3:3配置

`LEFT_COLUMN_FIELD_KEYS = [conversation_storage_kind, conversation_storage_version, profile_key]`、`RIGHT_COLUMN_FIELD_KEYS = [acceleration_api, backend_kind, device_kind]`へ変更。指定順と完全一致。

### 6. Sidebar Profile／Device／Acceleration情報の復元

`App.tsx`の`sidebarRuntimeStatus`計算ロジックを修正。従来はRuntime Model Control Status到達後、`[model_key, state, "Context N"]`のみで上書きし、Bootstrap Runtime SnapshotのProfile／Device／Acceleration情報（`runtimeStatus.text`の末尾Segment）を失っていた（P6-GOV-017 M-6の再現条件そのもの）。`bootstrapEnvironmentSuffix`として保持・再結合するよう修正。

### 7. Judge Result詳細のOBSERVE／ENFORCE中表示、OFF時Current／Historical分離

`FeatureModesPanel.tsx`の既存実装（`mergeCanonicalStatus`のRevision基準Merge、Backend `is_current`判定に基づく`last_result`／`historical_last_result`分離）が、この要件を既に構造的に満たしていることを確認した。本Package内での追加変更は不要と判断。

## Real Browser Verification（Evidence）

Model AuthorityがQwen／DeepSeekについては既存Historical Receiptで許可されている（Selene／Qwen3Guardとは別）ため、実Backend（`./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main --phase-6-runtime-model-control --phase-6-feature-modes`等、User Mac Manual Checkと同型のCLI、Task-owned `conversation-runtime-data-root`使用、実Qwen3-4B Load成功）を起動し、Browserで実際に操作した。

```text
確認1: Sidebar「main.qwen3-4b-q4-k-m / active · Context 8192 · local.macos-arm64 · gpu · metal」
       — Item 6の修正前は「active · Context 8192」のみで停止していたことをFix前に確認済み
       （フロントエンドBuild先を一時ディレクトリから正しいSTATIC_ROOTへ訂正した後に再現・解消を確認）。

確認2: Advanced Modeスクロール順 = Governance Definitions → Main/Guardrail Governance
       → Judge/Repair/Recording → Model Status → Role Provider選択 → Runtime設定制御
       （Item 2、視覚確認）。

確認3: Model Status内に重複Dropdown非表示、Context Size／Max New Tokens Controlは表示維持
       （Item 1、視覚確認）。

確認4: Runtime設定制御 — Research/Developer Mode Toggle非表示、Field 6件が
       左[conversation_storage_kind, conversation_storage_version, profile_key]／
       右[acceleration_api, backend_kind, device_kind]の3:3で表示
       （Item 3/4/5、視覚確認）。

確認5: Judge Provider=Selene（Default Configured）のままOBSERVE Activationを試行
       → 「適用に失敗しました。」表示、Mode=OFF維持。
       Network Response実測: {"code":"provider_selection_activation_failed",
       "message":"...could not be activated: dedicated_model_authority_unavailable"}
       — Package LのAuthority Gateが実Browser経路で正しく機能することを確認。
```

Real Model Loadは既存Qwen Authorityの範囲内でのみ実施した（Selene／Qwen3Guard Symlink Targetへの接触は本確認中も一切行っていない）。検証用Serverは確認後に正常終了（`kill`、Process残留なしを確認）。

## P-WU-005 CLI Help Contract

`entrypoints/web/main.py`の`--phase-6-feature-modes`Help文言「no live Generation-path effect」（P6-CODEX-053で指摘された、現実のJudge／Repair経路と矛盾する文言）を、実際の挙動（OBSERVE／ENFORCE時にJudge／RepairがLive Generation Pathを呼ぶ）と一致する記述へ修正した。

## Deferred Work Units（Non-critical Open Finding）

- **P-WU-001 Live Status Lifecycle自動更新**：`FeatureModesPanel.tsx`は現在、Panel可視化時に一度Fetchするのみで、Judge実行中／完了／Evidence Publication／Mode OFF遷移を自動Poll／Push更新しない（P6-CODEX-054）。ユーザーは手動Refreshまたは再Openで最新化する。自動Polling機構の追加は、Poll間隔設計・Resource消費・既存Revision-based Merge Logicとの整合が必要な独立した機能追加であり、本Bounded UI Delta Scope（既存要素の再配置・非表示化が中心）を超えるため、次Cycleへの候補として記録する。
- **P-WU-002／003**：Recording Summary自身の単一相関表示、Activation Failureの永続的Exact Reason表示は、`FeatureModesPanel.tsx`が個別のRecording Outcome行として部分的に表示しており（`renderRecordingOutcome`）、完全な単一Summary UIへの統合は本Packageでは実施しなかった。

## Focused／Regression Evidence

```text
Command: cd frontend && npx tsc --noEmit
Result : (no output / exit 0)

Command: cd frontend && npx eslint .
Result : (no output / exit 0)

Command: cd frontend && NODE_OPTIONS=--no-webstorage npx vitest run
Result : Test Files 25 passed (25) / Tests 227 passed (227)

Command: cd frontend && npx vite build
Result : 50 modules transformed, built to src/margpa_runtime_llm/web/static/ (Package J Baseline: 50 modules —一致)

Command: ./.venv/bin/ruff check src/ tests/ / mypy src/
Result : All checks passed! / Success: no issues found in 290 source files

Command: ./.venv/bin/pytest tests/unit/ tests/integration/
Result : 1674 passed, 7 deselected（Package O終了時と同数、Backend無変更のためRegression 0）

Real Browser: 実Qwen Model Load成功、Sidebar／Advanced Mode全7項目を視覚確認、
              Selene Authority Gate実HTTP Response確認。
```

## Claims Not Made

- Selene／Qwen3Guardの実Load成功を主張しない（本Real Browser確認でもAuthority境界を尊重し、Symlink Targetへ接触していない）。
- Live Status自動更新（Poll／Push）が実装されたと主張しない（P-WU-001、Deferred）。
- DeepSeekへの実Main Switchを本Packageで実行・確認したとは主張しない（既存Fixtureベース自動Testで経路自体は検証済みだが、Real Browser上でのDeepSeek実Loadは資源負荷の観点から見送った）。
