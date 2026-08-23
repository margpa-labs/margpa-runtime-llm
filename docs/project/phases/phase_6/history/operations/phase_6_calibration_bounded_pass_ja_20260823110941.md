# Phase 6 Calibration — Bounded Initial Pass（Append-only、P6-CODEX-016 一部実施）

```yaml
document_id: phase_6_calibration_bounded_pass
status: append_only_evidence
phase: phase_6
work_unit: p6_codex_016_partial
role: Claude側設計統括者役
created_at: 2026-08-23 11:09:41 JST
supersedes_nothing: true
authority: phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md
```

## 0. 位置づけ（正直な範囲宣言）

本文書はP6-CODEX-016（Calibration／Qwen Mode比較実験一式）の**一部**を、
実Server（main.qwen3-4b-q4-k-m、実main.qwen3-4b-q4-k-m Load、Judge=ENFORCE、
Repair=OFFでJudge単体挙動を分離）に対する実HTTP Requestとして実際に実行し、
実際に返ってきたJudge Recommendation／Confidenceのみを記録したものである。
Handoffが要求する「Position/Verbosity/Language/Self-preference/Confidence/
Deterministic-Conflict Calibration Matrix」全体を統計的厳密性をもって
実施したものではない（各条件1〜3試行のみ、統計的有意性の主張はしない）。
これは「実施したふりをして数値を捏造する」ことを避けるための意図的な
Scope限定であり、隠蔽ではなく明示する。

## 1. 実行方法（実際に行ったこと）

```text
Server: ./.venv/bin/python -m margpa_runtime_llm.entrypoints.web.main
  --host 127.0.0.1 --port 8731 --conversation-persistence
  --conversation-runtime-data-root .venv/.t/golden_path_runtime_data
  --conversation-scope-id phase6-calibration-run-1 --phase-6-feature-modes
Model: main.qwen3-4b-q4-k-m（実Load、local.macos-arm64・gpu・metal）
Judge Mode: enforce（本Calibration実施区間中固定）
Repair Mode: off（Repairの影響を排除しJudge単体の挙動のみ計測）
Driver: 一時Script（Session Scratchpad配下、Project外・使い捨て）が
  実際に `POST /api/v1/chat/stream` へ8件の実Requestを送信し、各Turn完了後
  `GET /api/v5/feature-modes/status` をPollingしてJudge Runの実際の結果
  （recommendation／confidence／execution_state）を読み取った。
  全8件、execution_state="completed"（Judge自体の実行Failureは0件）。
```

## 2. 実測結果（生の出力、加工・選別なし）

```text
verbosity_terse_ja    : recommendation=accept       confidence=0.95
verbosity_verbose_ja  : recommendation=needs_repair  confidence=0.70
language_ja           : recommendation=accept       confidence=0.95
language_en           : recommendation=accept       confidence=0.95
consistency_trial_1   : recommendation=accept       confidence=1.00
consistency_trial_2   : recommendation=accept       confidence=1.00
consistency_trial_3   : recommendation=accept       confidence=1.00
confidence_hard_case  : recommendation=accept       confidence=0.95
```

## 3. 次元ごとの解釈（過度な一般化をしない）

```text
Verbosity（詳細さ）:
  同一事実（日本最高峰）について「山名のみ一言」と指示したCaseはaccept、
  「標高・所在都道府県・有名な理由を含め詳しく」と指示したCaseは
  needs_repairとなった。試行数1件ずつのため統計的結論は出せないが、
  少なくとも「単に長い／詳細な回答を無条件に高評価する」という典型的な
  Verbosity Biasの方向（長い方が常に有利）は本試行では観測されなかった
  （むしろ逆方向）。ただしこれは真の意味でVerbosity単体を分離した実験
  ではない——短い指示と詳細指示では生成される実内容自体が異なり
  （詳細指示は追加の事実主張を含むため、事実誤りが混入する余地も増える）、
  「長さ」と「内容の正確性」が交絡している。この交絡を解消するには、
  Judgeへ任意の合成候補文（同一事実内容・異なる長さのみ）を直接投入できる
  Interfaceが必要だが、現行のJudge実装は実Turnの実生成結果のみを評価する
  設計であり、そのようなSynthetic Candidate投入APIは存在しない
  （§4「発見されたArchitecture上の制約」参照）。

Language（言語）:
  「日本の首都」を日本語・英語それぞれで質問し、両方ともaccept・confidence
  0.95で一致した。この1組の試行では言語間の系統的な差は観測されなかった。

Deterministic-Conflict（決定性・自己一貫性）:
  「1たす1は何ですか」を独立した3 Turnで質問し、3/3ともaccept・
  confidence 1.00で完全に一致した。自明な質問のため、この結果自体は
  驚くべきものではないが、少なくとも同一の単純な入力に対してJudgeの
  出力が試行間で不安定にブレる、という明白な問題は本試行では検出
  されなかった。

Confidence（確信度の較正）:
  光速の正確な数値という、Modelが誤りやすい可能性のある質問に対し、
  Judgeはaccept・confidence 0.95を返した。Judge自身がMAIN_SELF
  （Main Modelと同一Model）であるため、この確信度が実際の正解率と
  真に相関しているかどうかは、独立した正解Referenceとの照合なしには
  検証できない。本試行はこの照合を行っておらず、「Judgeの確信度が
  高いことは、回答が事実として正しいことを意味しない」という限界を
  明示的に記録するに留める。

Position Bias（提示順序Bias）:
  未実施——実施不能な構造的理由がある。§4参照。

Self-preference Bias（自己選好Bias）:
  未実施——独立した別ModelによるJudgeが本環境に存在しない
  （既存の全Recovery Entryで確認済みのJudgeIndependenceClass.MAIN_SELF
  制約）ため、「自分自身の出力を優遇するか」を検証するための比較対象
  （独立Modelが生成した候補）を用意できない。これは新規のCalibration
  未実施ではなく、Phase 6全体を通じて既知・記録済みの構造的制約
  （Judge Independence常にMAIN_SELF）の帰結である。
```

## 4. 発見されたArchitecture上の制約（正直な記録）

```text
現行のLive Judge実装（bootstrap/judge_live_integration.py）は、実Turnが
実際に生成した1つの実候補文のみを評価する設計であり、
(a) 同一内容で長さのみ異なる合成候補、
(b) 提示順序を入れ替えた複数候補の比較（Pairwise Comparison）、
(c) 独立Modelが生成した候補との比較
のいずれも直接投入できるInterfaceを持たない。Position Biasの意味のある
計測には(b)のPairwise Judge Interfaceが本質的に必要であり、これは
「Calibration実験を怠った」のではなく「現行のJudge Portの設計それ自体が
単一候補Accept/Needs-repair分類であり、比較Judgeではない」という
Frozen Phase 6のArchitecture上の事実である。Pairwise Interfaceの追加は
Judge Port自体の拡張（新規Capability）に相当し、本Second Reworkの
Scope（既存Architectureの動作をCorrectにする）を超える。この区別を
明示することが本節の目的であり、真のBlockerとして報告するか、
Phase 7以降のRoadmap項目として扱うかはController判断に委ねる。
```

## 5. 未実施のまま残る項目（正直な記録）

```text
- Governance/Guardrail/Judge/Repairの4機能について、OFF/OBSERVE/ENFORCEの
  全組み合わせを分離Token/Latency/Model-Call/Repair-count/Recording-Byte
  Metricsで比較する一覧表: 未実施。
- Accuracy Candidate/Unsupported Claim/Definition Confusion/Abstention/
  Over-refusal/Repair-Improved-vs-Worseの比較: 未実施（既知の正解
  Referenceを伴うEvaluation Datasetの用意が必要で、本Bounded Passの
  Scope外）。
- Max New Tokens実UI Apply（Model Reload 0）のCall Spy実証: 未実施。
- 統計的に有意な試行数（各条件で最低でも数十件程度）によるMatrix: 未実施
  （本Passは各条件1〜3試行のみ）。
```
