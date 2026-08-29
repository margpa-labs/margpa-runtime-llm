# Phase 6 Remaining Rework後 User Mac限定Manual Check

```yaml
document_id: phase_6_user_mac_bounded_manual_check_after_remaining_rework_20260826202919
status: READY_FOR_USER_MANUAL_CHECK
authority: USER_INTERACTIVE_CHECK_ONLY
predecessor: phase_6_gov016_remaining_rework_controller_independent_review_ja_20260826202919.md
created_at: 2026-08-26 20:29:19 JST
acceptance_promotion: PROHIBITED_UNTIL_REWORK
```

## 1. 目的

本Checkは、現状のUI／APIがSource Reviewどおりに振る舞うかをUser Macで確認するための限定Gateである。
Selene／Qwen3GuardまたはPhase 6をPASSへ昇格する試験ではない。

## 2. 起動

Project Rootから次で起動する。

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
  --phase-6-feature-modes
```

## 3. Check項目

### M-1 初期Provider State

Advanced ModeのProvider Selectionで次を確認する。

```text
Main: configured=Qwen / active=Qwen
Guard: configured=Qwen3Guard / active=none / state=configured
Judge: configured=Selene / active=none / state=configured
全Mode: OFF
```

### M-2 Main Dropdownの実Switch不成立確認

Provider SelectionのMainをDeepSeekへ変更する。直後にSidebarとModel StatusのCurrent Main Modelを確認する。

```text
予測される現状:
Provider Selection: configured=DeepSeek
実Main／Sidebar／Model Status: Qwenのまま
```

この差が出ればP6-CODEX-049を再現したことになる。ここで実Main Model切替PASSとはしない。

### M-3 Dedicated Judge ActivationのUnavailable確認

JudgeをSelene ConfiguredのままOBSERVEへ変更する。

```text
予測される現状:
Activation Error
Judge ModeはOFF維持
Judge active=none
failure_reason=dedicated_provider_artifact_unavailable 相当
```

Errorの文言と、Modeが偽ってOBSERVEにならないことを記録する。

### M-4 Dedicated Guard ActivationのUnavailable確認

GuardをQwen3Guard ConfiguredのままOBSERVEへ変更する。

```text
予測される現状:
Activation Error
Guard ModeはOFF維持
Guard active=none
failure_reason=dedicated_provider_artifact_unavailable 相当
```

### M-5 Built-in JudgeのFalse Identity確認

Judge Providerを`Built-in Deterministic`へ変更し、Judge ModeをOBSERVEにする。Main GovernanceはOBSERVE、
他は任意でOFFのまま、短い質問を1回送る。Advanced Modeと
`GET /api/v5/feature-modes/status`を確認する。

確認対象：

```text
Provider SelectionはBuilt-in Deterministicをactiveと表示するか
Judge Resultのjudge_roleはmain_selfになっていないか
configured_provider / active_providerと実Judge Roleが矛盾していないか
Semantic criteria_selected / evaluated / pass / deviation / unknownが更新されるか
Main GovernanceのDeferred数が一律109のままか、Semantic Resultへ置換されたか
```

矛盾があればP6-CODEX-047／050の再現であり、Judge Acceptance PASSではない。

### M-6 OFF／Historical State分離

M-5後にJudgeをOFFへ戻してAdvanced Modeを閉じ、再度開く。

```text
Current Mode: OFF
Current Result: なし
Historical Last Result: M-5のResultとして明示的に分離
```

前回結果がCurrentとして表示された場合はUI／Observability Reworkへ追加する。

### M-7 Recording相関

Recordingをmetadataまたはfullへ変更し、短いTurnを1回実行する。画面に表示される次の値を記録する。

```text
Request ID
Started / Completed time
Frozen Modes
Configured / Active Provider
Outcome / Reason
Turn Recording outcome
Judge Evidence Recording outcome
```

Judge Result側だけに値があり、Recording Summary自身が成否だけならP6-CODEX-053の未完了を確認したことになる。

## 4. 今回行わないこと

- Selene／Qwen3Guardの実用品質PASS主張。
- DeepSeek品質、長時間Judge／Repair Matrix、全Model Real Acceptance。
- Phase 6 Closure、Phase 7、Git、Model Artifact変更。
- Source Reviewで既に未接続と確定した経路を、UI表示だけでPASSへ昇格すること。

## 5. Return形式

M-1〜M-7を、`PASS／再現／未実施`と画面文言で返す。Controllerはその結果をP6-GOV-016へ
Append-onlyで連結し、Claude用差分Exact Handoffを作成する。
