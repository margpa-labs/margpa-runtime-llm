# P6-CODEX-004 Local Recording Adapter／Git Boundary — Rework Complete

```yaml
document_id: phase_6_codex_p6_codex_004_local_recording_adapter
status: current_recovery_entry
phase: phase_6
work_unit: p6_codex_004_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 06:35:00 JST
```

## 発見

```text
.gitignoreは既存で/runtime_data/persistent/**/conversations/等を除外して
いたが、本Handoffが明示するevaluations／experiments／evidence／feedback
Directoryは1件も除外されていなかった——Recording機構自体が未実装だった
ため実害は無かったが、実装前に対応しないとP6-ACC-051を最初から破ることに
なる、実際のGap。
```

## Exact Mutation

```text
Created:
  src/margpa_runtime_llm/adapters/runtime_observability/__init__.py
  src/margpa_runtime_llm/adapters/runtime_observability/local_filesystem_recording_writer.py
    （LocalFilesystemRecordingWriter、RecordingWriteFailure、
      RecordingQuotaExceeded）
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
    （8 Test：Atomic Write、Quota超過、Write Failure、Restart Recovery、
      Orphan Temp File Prune、不正max_total_bytes）
Modified:
  .gitignore
    + /runtime_data/persistent/**/{evaluations,experiments,evidence,feedback}/
  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
    + _recording_scope_directory_key()（独自Domain Separator、
      sqlite_conversation_store.pyの private _SCOPE_DOMAIN を再利用しない）
    + build_judge_completion_hook()へrecording_mode_controller／
      recording_runtime_data_root／recording_scope_id引数追加
    + Judge実行成功時、RecordingMode≠OFFならLocalFilesystemRecordingWriter
      ＋RecordingServiceを都度構築しRecord（Quota／Write Failureは
      Degraded、Judge Threadを止めない）
  src/margpa_runtime_llm/bootstrap/web_application.py
    + conversation_persistence_settingsからrecording_runtime_data_root／
      recording_scope_idを解決してbuild_judge_completion_hook()へ渡す
Modified（Test）:
  tests/unit/bootstrap/test_judge_live_integration.py
    + 2 Test（Recording OFF→書き込み0、Recording FULL→実File書き込み
      確認、tmp_path使用）
```

## 設計判断

```text
書き込み先: runtime_data/persistent/<Recording独自Hashed Scope>/evaluations/
  ——Conversation Persistenceの<Scope>Hashとは別のDomain Separator
  （margpa-recording-scope-v1）を用いた独立Hashとし、sqlite_conversation_
  store.pyの private _SCOPE_DOMAIN定数を跨Module参照しない設計とした。
Recording Serviceは都度新規構築: RecordingModeController自身のDocstringが
  「Live Mode変更は次にRecordingServiceを構築するCallerにだけ反映される」
  と明記している設計に従い、Judge Thread内で都度Mode Snapshotを読み直して
  新規RecordingServiceを構築する（Modeの取り違え・古いMode固定化を防ぐ）。
Fail-closed Degraded: RecordingQuotaExceeded／RecordingWriteFailureは
  Judge Background Thread内でCatchしDropする——Recordingはあくまで
  Evidence生成であり、失敗してもJudge本体やConversation Generationを
  巻き込まない（既存のGuardrail／Governance Hookと同じ「Coreを壊さない」
  哲学を踏襲）。
Conversation Persistence未Enabledの場合: recording_runtime_data_root／
  recording_scope_idがNoneのままとなり、Recording自体は静かに無効化
  される（誤ったPathへの書き込みや例外は発生しない）。
```

## Validation

```text
Backend Full: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider --basetemp=.venv/.t/f
  1430 passed, 5 deselected in 61.78s（新規10 Test含む、回帰0）
Ruff: All checks passed!
Mypy: Success: no issues found in 430 source files
Git Ignore実測: git check-ignoreでevaluations/配下の実Fileが正しく
  Ignore対象と判定されることを手動確認済み（Commit前に再確認予定）。
```

## Acceptance Cross-check

```text
P6-ACC-045（Recording OFFでBuild／Call／Write 0）: PASS（既存
  build_recording_envelope()のOFF Guardに加え、新規Testで実Write 0を
  End-to-endで確認）
P6-ACC-046（METADATAがAllowlist Fieldだけを保存）: PASS（既存Domain Test
  継続有効、Writer自体はSafeRecordingEnvelopeの中身をそのまま直列化する
  だけで新たなField混入経路を持たない）
P6-ACC-047（FULLがCanonical Input／Presented Answerだけを許可）: PASS
  （同上、SafeRecordingEnvelopeのextra="forbid"が引き続き唯一の関門）
P6-ACC-048（Thinking／System／Secret等保存0）: PASS（envelope自体の
  Field制約を継承、Writerは新たな保存経路を追加しない）
P6-ACC-049（Atomic Write／Quota／Failure／Degraded）: PASS（本Entry新規
  実装、8 Testで直接検証）
P6-ACC-050（TestがUser実runtime_dataへRead／Write 0）: PASS（全TestはPython
  pytest tmp_pathのみ使用、User実runtime_dataへの接触0）
P6-ACC-051（Private Evaluation等がGit Stage対象外）: PASS（.gitignore追加
  ＋git check-ignoreで実測確認）
```

## Next Exact Route

P6-CODEX-006（Calibration／Mode Comparison／Metrics）または
P6-CODEX-005/007へ進む。実Model実行を伴う項目のため、Time Budgetを
考慮し優先順位を再評価する。
