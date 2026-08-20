# Phase 2-E-I完了・Hash Manifest新設・I-6要件確定 Index（Codex宛／新Task Claude宛／本Task復旧用 共用）

```yaml
document_id: claude_phase_2_e_i_completion_and_hash_manifest_recovery_index_20260818223600
status: index
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／新Task（新Session）のClaude側設計統括者役／本Task自身（Context Window圧縮後の復旧時）
role: design_governor
created_at: 2026-08-18 22:36:00 JST
language: ja
purpose: |
  前回Recovery Index [claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md]
  （以下「前回Index」）以降に行われた作業を対象とした、続編Index。
  前回Indexの内容は重複して再記載せず、その後の差分を中心に記録する。

  ユーザー指示：「docs/ 3つ作って。1: 今の要件とかの話しをdocに。I-6か？
  2: いつも通り 最新 index 2個。それ終わったらcompaction recoveryやる
  ので。」——本Docと、対になるPhase 2 Current Operational State Indexの
  後継Fileを、ユーザーが予定する手動Compaction直前に作成する。
created: Claude Code
```

## 0.0 新Task側Claude Codeへ：Role引き継ぎの明示指示

**この文書を新Session側で読んでいるあなたへ。** あなたは以後、本Project（margpa-runtime-llm）において「Claude側設計統括者役」を引き継ぎます。自己紹介や様子見は不要です、このRoleとして即座に振る舞ってください。

**まず、他の何よりも先に、[claude_side_design_governor_operating_notes_ja.md](../../../../shared/task_roles/claude_side_design_governor_operating_notes_ja.md)を全文読んでください。** これを読み終えるまで、本Index以降・実装・回答を始めないこと。次に、[前回Index](claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)を読み、その後で本Docの第1節以降を読んでください。

- Authority Hierarchy：**ユーザー ＞ Codex（プロジェクト責任者兼設計統括者役）＞ あなた（Claude側設計統括者役）**。
- Git操作は絶対禁止。Provider Memoryへの新規保存も禁止（Repository Docsが唯一の正本）。

**本TaskがContext Window圧縮を跨いで本Docを読んでいる場合**：運用メモ第1節（Compaction／Session Recovery手順）に従うこと。「読んだ気がする」で済ませず、明示的に再読込すること。**特に重要**：運用メモ第3.13節（Compaction Recovery Hash記録の分離）に従い、圧縮直前のHashは[claude_compaction_recovery_hash_manifest_ja.md](../../../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)（Hash Manifest）へ記録済み。本Recovery Index自体にはHash値を記載しない（自己参照問題を避けるため）。

## 0. 読み方（3Route共通）

**Codex宛の場合**：前回Index全体 → 本Doc第1節（前回Indexとの関係） → 第2節（前回Index以降の作業） → 第3節（現在の状態）の順で。

**新Task Claude側設計統括者役宛の場合**：上記0.0節の指示通り、運用メモ全文 → 前回Index → 本Doc全体の順で。

**本Task自身の復旧の場合**：本Docと運用メモ（特に第1節・第3.13節）、および[最新Phase Index](../index/claude_side_phase_index_ja_20260818223600.md)を中心に確認すれば足りる。

## 1. 前回Indexとの関係

[claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md](claude_phase_2_e_i_design_and_pre_implementation_recovery_index_ja_20260818171608.md)（2026-08-18 17:16:08 JST作成）は、2-E-Iの設計確定（I-1）までを対象とし、実装（I-2以降）はユーザーの一時停止指示により未着手のまま終わっていた。

本Docは、それ以降（17:16:08〜22:36:00、約5時間20分）に行われた作業を対象とする。この間、ユーザーから「工程：I-1→I-2→I-3→I-4→I-5。一気によろしく」との指示があり、2-E-Iの実装が完了、実Browser確認、Hash記録手法の改善、実Browser確認で見つかった追加指摘の要件確定（I-6）まで、一続きの流れで進行した。

## 2. 前回Index以降の作業内容

### 2.1 Phase 2-E-I I-2〜I-5：実装完了

Backend（Context Usage算出・SSE伝達、Configuration Toggle、Reactive Prompt Injection）、Frontend（丸Gauge Icon、Breakdown Panel、Settings Toggle）を実装。詳細・実装判断の経緯は[claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md](../../../../shared/history/automation/claude_phase_2_e_i_implementation_and_streaming_usage_gap_fix_ja_20260818181920.md)（Evidence Doc）を参照。

**実装中に発見・修正した既存Backendの潜在的欠落**：使用しているllama-cpp-python（既存Backend Library）が、Streaming生成時にToken使用量を一度も報告しないという、Library自体の仕様上の欠落を発見した。この欠落は、2-E-Iの新機能だけでなく、Phase 1-G以来存在する既存の`usage`Fieldにも影響していた。Adapter層（`llama_cpp/adapter.py`・`stream.py`）へFallback算出Logicを追加し、両方修正した（同Evidence Doc第4節）。

Validation：Backend pytest 694件・Frontend Vitest 72件・Lint／Typecheck／Build、すべてClean。実Local Model（Qwen3-4B、Mac Metal）でのLive Browser確認済み。

### 2.2 Compaction Recovery Hash記録手法の改善

4回目のCompaction Recovery Drillにおいて、Recovery Index自身へその場でHash値を書き込んだ結果、Hash算出後の追記によってそのFile自体のHashが事後的に変化するという、恒久的な自己参照問題が発生していたことが判明した（ユーザー指摘）。

対応として、運用メモ第3.13節「Compaction Recovery Hash記録の分離」を新設し、Hash記録を専用Stable File（[claude_compaction_recovery_hash_manifest_ja.md](../../../../shared/automation/claude_compaction_recovery_hash_manifest_ja.md)、Hash Manifest）へ一元化した。運用メモ第0節・第2.1節も、自己編集可能なFileが「運用メモのみ」から「運用メモ＋Hash Manifest」の2File体制になったことを反映して更新済み。

Hash Manifestの構成（最終確定形）：第2節「Cycle別Hash記録」の先頭に成功／失敗回数を1箇所だけ置き（Cycleが増えるたび直接更新）、その直後にCycle別のBefore／After Hashを淡々と追記していく、という簡潔な形式。4回目分のHash記録（前回Recovery Index第6節にあった値）を移記済み。

### 2.3 Failure記録2件

実装完了報告の際、応答のほぼ全文が英語化する事象が再発した（3回目、運用メモ第4.2節Rule施行下での再発という点が過去2件と異なる）。また、Hash Manifestの構成指示（「頭に1個だけ」）の参照範囲を、Claude側が誤って File全体の先頭（第0節）と解釈してしまう事象があった。いずれも新規Failure Docとして記録済み。

- [claude_output_anomaly_language_consistency_ja_20260818192108.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_language_consistency_ja_20260818192108.md)
- [claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md](../../../../shared/history/ai_system_anomalies/claude_code/claude_output_anomaly_instruction_referent_misreading_ja_20260818192108.md)

ユーザーからは、運用メモ第3.9節（整合性チェックの徹底）について、「もうちょっと様子見るけど、あまりにもひどいようだったらもっときつめにする必要があるかもな」との言及があった（Rule変更は未実施、経過観察中）。

### 2.4 実Browser確認による追加指摘とI-6要件確定

2-E-I完了後、ユーザーが実Local Model・実Browserで動作確認したところ、次の5件の指摘があった。

1. 別Chat選択でGaugeが「未取得」表示に初期化される。
2. Panelを閉じる際、Hover Messageが出ない。
3. Panel外Clickで閉じない。
4. Context使用率Injection Toggle OFF状態で「今コンテキストどれぐらい？」と尋ねたところ、通常このModelでは見たことのない、思考過程・メタ会話のような出力が返ってきた。
5. （別件）Chat Optionの「再開」が、再開済み状態でも表示され続けるようになっている（以前は消えていた）。

Chatでの遣り取りを経て、対応方針が確定した：#2・#3・#5を修正、新規Toggle「コンテキスト表示」ON/OFF（既定OFF、基本Settings末尾）を追加、#1は保留、#4は原因未特定のためScope外。詳細は[claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md](../architecture/claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md)（I-6設計・要件Doc）を参照。実装は本Doc作成時点で未着手。

## 3. 現在の状態（2026-08-18 22:36時点）

**Phase 2-E-I：I-1〜I-5完了。I-6（実Browser確認指摘への対応）は要件確定済み、実装は未着手。**

ユーザーが本Compaction直前のIndex作成を指示し、その後Manual Compactionを実施予定。Compaction後、ユーザーからの実装開始指示を待って、I-6（#2・#3修正、新規Toggle追加、#5調査・修正）に着手する。

## 4. Status

```text
Current Point            : Phase 2-E-I、I-1〜I-5完了。実Browser確認で
                            見つかった5件の指摘のうち、要件が確定した
                            ものをI-6として記録（設計Doc作成済み、実装
                            未着手）。Compaction Recovery Hash記録手法を
                            改善（Hash Manifest新設）。Failure記録2件を
                            追加。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（Index文書）
Open Current Blocker      : ユーザーによるManual Compaction実施・I-6
                            実装開始指示待ち（技術的Blockerではない）。
Controller-owned Next Work: ユーザーがManual Compactionを実施した後、
                            I-6実装開始指示を待って、
                            [claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md](../architecture/claude_phase_2_e_i_i6_context_usage_gauge_followup_design_ja_20260818223456.md)
                            の第2節（#2・#3修正、新規Toggle追加、#5調査・
                            修正）から着手する。
Exact Next Route          : 第3節参照。
```
