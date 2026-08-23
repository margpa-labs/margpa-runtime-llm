# Phase 6-I-WU-003 Real Browser Golden Path（実Hardware×実UI初統合）

```yaml
document_id: phase_6_i_wu003_real_browser_golden_path
status: current_recovery_entry
phase: phase_6
subphase: phase_6_i
work_unit: p6_i_wu003_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 02:55:00 JST
```

## 目的

これまでのReal Browser検証は全てFake Fixture（`bound_runtime()`相当のScratchpad
Server）で行い、実Model Loadは常にpytest単体（UIなし）で行ってきた。本WUで
初めて、実Qwen3-4B Model Loadと実Settings UIをMac Local上で統合して検証した。

## 発見された事前Gap（本WU着手前に解消）

```text
build_phase1_web_runtime()にはPhase 6-B（runtime_model_control_enabled）が
既に配線済みだったが、Phase 6-G-WU-004で追加したJudgeModeController／
RepairModeController／RecordingModeControllerは、WebRuntime Dataclassの
Fieldとしては存在するのに、本番Composition Root（build_phase1_web_runtime）
からは一度もInstance化されていなかった（Fake Fixtureでのみ構築されていた）。
CLI Entrypoint（entrypoints/web/main.py）にも対応する--phase-6-*Flagが
存在せず、実Serverでは/api/v5/feature-modes/*が常に404になる状態だった。

これはP6-I-WU-003自体の要件（実UIでJudge／Repairを確認する）を満たす前提
として埋める必要がある、本物のProduction Wiring Gapであり、Scope外の
先取り実装ではなく本WUの一部として対応した。
```

## Exact Mutation

```text
Modified:
  src/margpa_runtime_llm/bootstrap/web_application.py
    + import JudgeModeController／RepairModeController／RecordingModeController
    + build_phase1_web_runtime(..., feature_modes_enabled: bool = False)
    + feature_modes_enabled時に3 Controllerを構築しWebRuntimeへ渡す
  src/margpa_runtime_llm/entrypoints/web/main.py
    + --phase-6-runtime-model-control／--phase-6-feature-modes CLI Flag
    + _runtime_model_control_enabled()／_feature_modes_enabled()
      （既存の他Phase Flagと同型のLocal-loopback-only Gate）
    + runtime_factoryへruntime_model_control_enabled／feature_modes_enabled配線
```

## 実施方法

```text
実Server起動: .venv/bin/python -m margpa_runtime_llm.entrypoints.web.main
  --host 127.0.0.1 --port 8010
  --phase-6-runtime-model-control --phase-6-feature-modes
  --phase-5-guardrail-governance --phase-4-runtime-governance
  --phase-3-governance-definitions --configuration-control
  --conversation-persistence
  --conversation-runtime-data-root <Scratchpad専用Dir、User実Data外>
  --conversation-scope-id golden-path-p6i-wu003

実Model: main.qwen3-4b-q4-k-m（実Load、GGUF、Metal Backend）
Conversation Persistenceは既存のUser実Runtime Data（runtime_data/persistent/...）
とは完全に別のScratchpad Directoryへ隔離し、User実Dataを一切操作していない。
```

## 実施結果（Mac Local、実Browser、実Model）

| 項目 | 結果 |
|---|---|
| 実Generation | 「What is the capital of France?」→実Qwen「Paris」を実測確認 |
| Context／Token変更 | Context Size 8192→4096へApply、実Unload／Reload成功、Revision 0→1、State=active維持 |
| Mode再Open | Settings閉→開後もContext Size 4096、Judge=observe、Repair=observe、Recording=metadataが正しく保持 |
| Judge | UI ToggleをOFF→observeへApply、即時Revision増分・独立反映を実機で確認（Live Generation介入は未配線、既知のScope、捏造せず記録） |
| Repair | 同上、observeへApply成功、Judgeと独立して変化 |
| Status | Guardrail Enforce後の実Reject試行で`guardrail.input`が`State: evaluated, Severity: high, Detection数: 5, Match数: 1, 実行Action数: 1`という実測値へ変化することを確認（Not Invokedの—から実値への遷移を実機で確認） |
| Identity | Model StatusパネルがCurrent Main Model=main.qwen3-4b-q4-k-m、State=activeを実Backendから実測表示 |
| Safe Reject | Guardrail Mode ObserveプルErに設定後Enforceへ切替＋適用（Revision 2、Configuration Control経由のCAS Apply成功）。injection markerを含む入力（"ignore previous instructions"）を実送信し、実際に`Error: guardrail_reject_input`でBlockされ、Assistant回答は生成されなかったことを確認 |
| Conversation Recovery | 初回会話（fad6d1ca...）がServer再起動（Configuration Control追加のための再起動）を跨いでSidebarに残存することを実測確認（同一sqlite Storeへの実再接続） |
| Citation Recovery | 本Serverインスタンスでは--documentation-rag-profile未指定のためRAG機能自体がUnavailable。Citation Recovery自体は対象外（Scope外、既存のPhase 1-Gテストで別途担保） |
| Model Switch | 本Environmentには実Registered Model Definitionがmain.qwen3-4b-q4-k-mの1件のみ（config/models/配下）で、実Artifactを用いた別Model方向へのUI-level Switchは対象不可（DeepSeekはCURRENT_TOOLCHAIN_UNSUPPORTED継続）。Switch機構自体の実Hardware証跡はP6-B-WU-007（同一Model定義への実Context Resize Switch Cycle）で既に確立済み |

## 発見事項（正直な記録、捏造なし）

```text
Guardrail Mode Apply（OFF→Enforce）はConfiguration Controlの共有Preview／Apply
機構を経由する（P5-CODEX-002 Reworkの既存設計）。--configuration-control
Flagを付けずにServerを起動した状態でEnforceへApplyを試みたところ、Network
Requestが一切発行されずクライアント側で即座に「Mode適用に失敗しました。」
というFail-closed Guardが働くことを確認した（App.tsx:552-559の
`configurationState.capability !== "ready"`チェック）。これはBugではなく
既存のPhase 5 Architecture上の正しいFail-closed挙動だが、UIのGuardrail Mode
Panel自体にはConfiguration Control前提の説明が明示されておらず、
Configuration Control未接続構成での挙動が分かりにくい——将来のUX改善候補
として記録するに留め、本WUでは変更しない（Scope外）。
```

## Validation

```text
Full Suite : 1405 passed, 5 deselected in 61.55s（Bootstrap／CLI変更後も回帰0）
Ruff       : All checks passed!
Mypy       : Success: no issues found in 418 source files
Server後処理: 実Server 2回（Configuration Control追加のため1回再起動）とも
             正常終了・Process確認済み、Browser Tabも終了・破棄済み
```

## Next Exact Route

P6-I-WU-004（Self-review／COMPLETE_CANDIDATE）へ進む。Design Conformance、
Exact Mutation、Test、Model Artifact、Open Major Finding、Compaction／Quota、
False Completion、Human BurdenおよびRollbackを統合し、
Phase 6 Claude Complete Candidate Handoffの作成へ進む。
