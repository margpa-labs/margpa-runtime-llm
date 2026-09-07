# Phase 9-1 — User Mac Selene Fresh Restart 3試行 Failure Evidence

```yaml
document_id: phase_9_1_user_mac_selene_fresh_restart_three_trial_failure_evidence_20260905104040
document_type: user_manual_test_evidence
document_state: unresolved_failure_confirmed
phase: phase_9
program: phase_9_1
tester: user_nazuna_research
environment: apple_m2_pro_16gb
language: ja
recorded_at: 2026-09-05 10:40:40 JST
```

## 1. 実施条件

UserはMacを再起動し、常駐Process以外をほぼ停止した状態でSeleneを3回確認した。各試行間でもMacを再起動した。ServerはDedicated Model Authority付きのPhase 9-1 Manual Commandで起動した。

## 2. Trial 1／2 — Semantic Snapshot前停止

Trial 1はServer起動直後にSeleneへ切り替え、Judge／Repair／RecordingをENFORCE。Trial 2は再起動後、Selene JudgeだけをENFORCEした。

両方ともMain Runtime Governanceが未設定で、次の同型結果となった。

- Selene ProviderはConfigured／Active表示。
- Frozen Main Modeは`unknown`。
- Criteriaは`selected=0`／`evaluated=0`。
- Failureは`semantic_snapshot_unavailable`。
- Presented Resultは`safe_fallback`。

この2試行はSelene推論前に停止しており、Selene実Inferenceの成否Evidenceにはしない。

Request ID:

- Trial 1: `d8338a4b-2402-4840-8d42-a64b14f57a1e`
- Trial 2: `15a3d2c4-feb8-4781-b101-a5f17e6b4228`

## 3. Trial 3 — Semantic Snapshot成立後の実行Failure

再起動後、Main Runtime Governanceを先にObserveへ設定し、通常Turnで`main_model.pre／post` Evidenceが生成されることを確認した。その後、Selene JudgeをENFORCE、Repair／Recording／GuardをOFFとして新Turnを送信した。

```text
Request ID: b3af1497-802c-4f7f-b284-8e40dbb3367a
Started:   2026-09-05T01:35:30.253900+00:00
Completed: 2026-09-05T01:35:30.285430+00:00
Configured Provider: judge.selene-1-mini-llama-3.1-8b-q5-k-m
Active Provider:     judge.selene-1-mini-llama-3.1-8b-q5-k-m
Executed Provider:   judge.selene-1-mini-llama-3.1-8b-q5-k-m
Frozen Modes: main=observe, guard=off, judge=enforce, repair=off, recording=off
Criteria: selected=32, evaluated=0, unknown=32, deferred=77
Failure: unavailable
Presented Result: safe_fallback
```

画面表示は「選択したProviderをLoadまたは使用できませんでした」。Main Governance Evidence自体は正常で、`main_model.post`はDeferred 77まで進んだ。Server Terminalで確認できた関連行は次のみだった。

```text
decode: removing memory module entries for seq_id = 0, pos = [256, +inf)
```

## 4. 判定

Trial 3により、Snapshot不足を解消してもSeleneが32 Criterion実評価を完了できないFailureを確認した。Provider表示はActiveかつ三Identity一致だが、評価は0件のまま約31msで`unavailable`へ収束している。

したがって、Seleneは`UNRESOLVED`を維持する。ただし、UI／Terminal EvidenceだけではLoad、Dispatch、Native Decode、Resourceのどこで失敗したか一意に特定できない。PCメモリ不足、Selene Artifact不良、Native競合のいずれも本Evidenceだけで断定しない。

Gemma代替経路の確認を優先し、Selene修復は延期候補として扱う。Phase 9-1 Closureは別途Gemma／Guard／Main Governance実画面結果の受理後に判断する。
