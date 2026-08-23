most_recent_recovery_index: docs/project/phases/phase_6/history/index/phase_6_third_rework_steps_1_to_5_checkpoint_ja_20260823170000.md

# Phase 6 Third Rework — Step 6 完了（Current Request UI State + 実機検証）

```yaml
document_id: phase_6_third_rework_step_6_ui_state_and_real_hardware
status: current_recovery_entry
phase: phase_6
subphase: phase_6_third_rework
work_unit: required_rework_sequence_step_6
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 17:40:00 JST
authority: phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
```

## 実施結果（Step 6、P6-CODEX-024）

```text
Frontend実装:
  - DisplayMessage.requestId／PersistentTurn.request_id（新規）: 実は
    Backend（PersistentTurnResponse）に既に存在していたRequest ID Fieldを
    初めてFrontendで消費するよう配線。Ephemeral／Persistent両Streamの
    "start" Eventで設定、かつPersistent detail Reload後も
    turn.request_id経由で正しく復元される（実機検証で発見・修正した
    実Bug、後述）。
  - App.tsx: 1.5秒間隔の軽量Polling（/api/v5/feature-modes/status）を
    追加。Current-Request-correlatedなLiveJudgeBadgeをMessageList→
    MessageBubbleへ配線。
  - MessageBubble: judging(running)/improved(completed+repair_accepted)/
    degradedの3状態のみをChat Surfaceへ表示するcurated設計を採用
    （idle/queued_or_skipped/failed/cancelledはFeature Modes Panel側の
    詳細Viewに委ね、Chat Surfaceを煩雑にしない意図的Scope選択）。
  - FeatureModesPanel: JudgeModeSnapshot.stateのUnionをBackendの拡張後
    Vocabulary（queued_or_skipped/failed/cancelled/degraded）に合わせて
    拡張、last_resultのStale判定をstate比較からrequest_id比較へ是正。
  - i18n: chatLiveJudgeRunning/Improved/Degraded、
    featureModesJudgeState{Skipped,Failed,Cancelled,Degraded}をja/en
    両方に追加。
新規Test: MessageBubble 6件、MessageList 2件、App.tsx 2件。
Frontend Full: typecheck/lint/test(208件)/build 全PASS。
```

## 実機検証（実Server + 実Browser + 実main.qwen3-4b-q4-k-m Model）

```text
環境: MARGPA_MODEL_ROOT=/Users/Nazuna Research/models/margpa-runtime-llm/models
      （前回Session不在と誤認したが、正しいPathを再探索し発見。
      sha512／sizeともconfig/models/qwen3_4b_q4_k_m.tomlと一致確認済み）
Server: .venv/.t/server_logs/third_rework_golden_path.log
        （Project-local。P6-GOV-004参照——起動直後に誤って/tmp配下へ
        Log Redirectした事象を自己検知・即時是正した記録あり）

発見・修正した実Bug（実機検証でのみ露呈、Unit Testでは非検出）:
  Persistent Conversationでは、Streaming完了後にloadPersistentDetail()
  等がdetailToMessages()経由でmessagesを丸ごと再構築するため、
  Streaming中にupdateMessageByIdで設定したrequestIdが、
  emptyMessage()のdefault値（null）へ上書きされて消えていた。
  → 修正: PersistentTurnResponseに既存の`request_id` Fieldを
    Frontendの`PersistentTurn`型へ追加し、detailToMessages()内で
    turn.request_id経由でrequestIdを再構築するよう修正（Streaming中の
    値だけに依存しない、Reloadに強い実装へ是正）。

確認できた実結果:
  1. Judge ENFORCE + Repair ENFORCE + Recording FULLを実Feature Modes
     Panelから適用し、実Chat 2往復を実施。
  2. 両往復ともJudge実行: recommendation=accept, confidence=0.95、
     execution_state=completed、Repair Eligibility=
     not_eligible_no_repair_recommendation（accept時の正しい判定）。
  3. Recording FULLが実際にTurn Record・Judge Evidence Recordの両方を
     実File書き込み（ok:true）。
  4. Judge Evidence実File内容を確認: artifact_digest_sha512が
     config登録のsha512（f182f1d4...）と完全一致、backend_key=
     llama_cpp、backend_version=0.3.34——P6-CODEX-022のArtifact Digest
     修正が実際に機能していることを実Fileで直接確認。
  5. Page Reload後もrequestIdが正しく復元され、Judge Evidence
     Recordingとの相関が維持されることを確認（上記実Bug修正の効果）。
  6. Server SIGTERM Graceful Shutdown: "Application shutdown complete"
     まで正常完了、Zombie Processなし。
  7. Server Log全体を確認、Error/Exception/Traceback 0件。
  8. Judge Runの実際の`running`状態（Live Badge）は、実Modelの応答が
     速すぎて（Judge Latency約1.3秒）実Browser上での目視Timing捕捉には
     至らなかった——この特定のTransient状態自体はMessageBubble Unit
     Testで決定的に検証済みであり、実装自体の正しさはE2E Data Flow
     （Backend Judge→HTTP API→Frontend Polling→相関→Badge描画）の
     実機確認で裏付けられている。Repair実発火（needs_repair）も、
     短い実Prompt群では意図的に誘発できず、実機Unit観測はできて
     いない（Unit Testでのみ確認）——正直な未確認事項として記録する。
```

## Governance

```text
新規Incident: P6-GOV-004（本Entry作成前に別途Correction文書化済み、
  Claude自己検知・即時是正）。Phase 6累積Incident: 5件。
Git Mutation: 0。Provider Memory接触: 0。User実runtime_data接触: 0
  （すべて使い捨てのGolden Path用Scope Id使用）。
```

## Next Exact Route

```text
Step 7: Project-local Calibration Harnessと比較Matrixの完成（P6-CODEX-018）。
Step 8: Acceptance IDを1件ずつSource/Test/実機Evidenceから再判定。
Step 9: Full/Static/Frontend/Real Model/Real Browser再実行（最終）。
Step 10: 新しい"Phase 6 Claude Third Rework Complete Candidate Handoff"作成。
```
