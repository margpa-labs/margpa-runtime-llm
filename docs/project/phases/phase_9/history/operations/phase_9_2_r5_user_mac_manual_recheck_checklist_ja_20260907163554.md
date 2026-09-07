# Phase 9-2 R5後 User Mac実画面Recheck Checklist

```yaml
document_id: phase_9_2_r5_user_mac_manual_recheck_checklist_20260907163554
document_type: user_manual_checklist
document_state: ready_not_run
phase: phase_9
program: phase_9_2
tester: nazuna_research
controller: codex
recorded_at: 2026-09-07 16:35:54 JST
language: ja
selene_in_scope: false
guard_retest_required: false
append_only: true
```

## 1. 今回の範囲

Phase 9-2で追加したExperiment UIの中心経路だけを確認する。

1. Fixtureで2 Variantを実行し、比較表とComponent別Evidenceを確認する。
2. 同一Production Plan内でMain-onlyとMain + Gemma Judge／Repair Variantを順次実行する。
3. Live ConfigurationがVariantと合わない場合のTyped Rejectを確認する。

Qwen3Guard、Selene、DeepSeek、RAG、Web、Dev Agent、Stop／Cancel、Browser Restart後の復元は今回再検証しない。GuardとJudge／Repair基盤自体はPhase 9-1とBackend実Model Gateで確認済みである。

## 2. 起動

Migrationは不要。既存Serverを停止し、Project Rootで次を実行する。Phase 9-2専用の追加CLI Flagはない。

```bash
./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main \
  --host 127.0.0.1 \
  --port 8000 \
  --conversation-persistence \
  --conversation-runtime-data-root "$PWD/runtime_data" \
  --conversation-scope-id "mac-local-primary" \
  --configuration-control \
  --phase-3-governance-definitions \
  --phase-3-governance-definitions-root "$PWD/definitions" \
  --phase-4-runtime-governance \
  --phase-4-runtime-governance-definitions-root "$PWD/definitions" \
  --phase-5-guardrail-governance \
  --phase-6-runtime-model-control \
  --phase-6-feature-modes \
  --phase-6-dedicated-model-authority \
  --phase-7-local-corpus \
  --local-corpus-runtime-data-root "$PWD/runtime_data" \
  --local-corpus-scope-id "mac-local-primary" \
  --phase-7-web-search \
  --phase-7-web-search-governance-mode off \
  --phase-7-data-controls \
  --data-controls-runtime-data-root "$PWD/runtime_data" \
  --data-controls-scope-id "mac-local-primary"
```

## 3. Fresh UI

1. Main Governance／Guard／Judge／Repair／RecordingをOFFにする。
2. 上部の「実験（Phase 9-2）」を開く。
3. 「実験 — Multi-Governance比較（Phase 9-2）」が開き、Experiment ID、Preset Case、Variant、実行Mode、Plan作成が表示される。
4. Production Variantの宣言ComponentにQwen／Gemma／Qwen3GuardのSelector IDが表示される。

## 4. Test A — Fixture比較

1. 実行Modeを「Fixture（安全・実Modelなし）」にする。
2. `Baseline (all components off)`と`Judge OBSERVE only`を選択する。
3. Planを作成し、両Variantを1回ずつ実行する。

PASS条件：

- 両Runが`completed`。
- 比較表に2 Row表示される。
- 実行Modeは両方`fixture`。
- Frozen Config DigestはFixtureのため`-`。
- Metric、評価、Raw Evidence参照が表示される。
- 詳細EvidenceはFixtureであることを明示する。
- BaselineとJudge OBSERVEでComponentのCall表示が同一にならず、Judgeの利用有無を区別できる。

## 5. Test B — 同一Production Planの2 Variant

ページを1回再読込し、全Mode OFFを確認してからExperiment画面を開く。

1. 実行Modeを「Production（実Turnを1回実行）」にする。
2. `Production: Main only`と`Production: Main + Judge/Repair ENFORCE`を選択する。
3. Planを作成する。
4. Desired Config DigestがVariantごとに表示され、2つが別の値であることを確認する。
5. まず全Mode OFFのまま`Production: Main only`を実行する。
6. Main-only Run完了後、Experiment画面を閉じる。
7. SettingsでJudge ProviderをGemma 4 E2Bにし、JudgeとRepairをENFORCEにする。Main Governance／Guard／RecordingはOFFのままにする。
8. Experiment画面を開き直し、同じPlanの`Production: Main + Judge/Repair ENFORCE`を実行する。

PASS条件：

- 閉じて開き直しても、そのページを再読込しない限り作成済みPlanが保持される。
- 2 Runとも`completed`。
- 比較表に同一Experiment IDの2 Rowが表示される。
- 実行Modeは両方`production`。
- Frozen Config Digestが両Rowに表示され、2つが別の値である。
- Main-onlyの詳細はMain `true`、Judge `false（確定Call 0）`、Repair `false（確定Call 0）`。
- Judge／Repair側の詳細はMain `true`、Judge `true`。RepairはJudge結果により非発火でもよく、表示された実測をそのまま記録する。
- Guardや現行Adapterで相関不能なComponentは「—（未観測）」と表示され、`false`と混同されない。
- 詳細EvidenceはProductionの実Turnであることを明示する。
- Failure理由がない。

## 6. Test C — Wrong Live ConfigurationのTyped Reject

Test B完了後、Judge／Repair ENFORCEのまま、同じPlanの`Production: Main only`をもう1回実行する。

PASS条件：

- Variantが宣言するJudge／Repair OFFとLive ENFORCEの不一致が拒否される。
- `live_config_mismatch`に相当する失敗理由が表示される。
- Runが`running`のまま残らない。
- 追加の成功Rowとして比較表へ混入しない。
- Main／Judge／Repairの新しい実行が始まったような表示にならない。

## 7. 終了と返却

最後にJudge／RepairをOFFに戻す。GuardやSeleneの追加確認は行わない。

```text
Fresh UI: PASS / FAIL
Test A Fixture比較: PASS / FAIL
Test B Production Main-only: PASS / FAIL
Test B Production Main+Gemma: PASS / FAIL
Test B 同一Planの比較表: PASS / FAIL
Test C Wrong Live Configuration Reject: PASS / FAIL

Experiment ID:
Case ID:
Variant ID / Run ID:
Desired Config Digest表示:
Frozen Config Digest表示:
比較表:
Component別詳細Evidence:
失敗理由／違和感／画面の固さ:
Server TerminalのError（Errorがある場合だけ）:
```

本Checklistは`USER MANUAL GATE / NOT RUN`。結果受領後、Controllerが別のResult記録にまとめ、Phase 9-2 CompleteとPhase 9-3開始可否を判定する。

