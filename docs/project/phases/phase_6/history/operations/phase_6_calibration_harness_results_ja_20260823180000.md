# Phase 6 Project-local Calibration Harness — 実行結果（Append-only、P6-CODEX-018）

```yaml
document_id: phase_6_calibration_harness_results
status: append_only_evidence
phase: phase_6
work_unit: p6_codex_018_third_rework_step_7
role: Claude側設計統括者役
created_at: 2026-08-23 18:00:00 JST
authority: phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
harness_source: scripts/models/phase_6_calibration_harness.py
raw_result_file: .venv/.t/calibration_harness_results.json（Project-local、Git管理外）
```

## 0. 位置づけ（正直な範囲宣言）

本文書は、Third Independent Review（P6-CODEX-018）の指示に基づき新規実装した
`scripts/models/phase_6_calibration_harness.py`（Project-local、実Model
`main.qwen3-4b-q4-k-m`を実Load、HTTPサーバ不要でJudge Domain関数を直接呼び出す）
を実際に2回実行し、実際に返ってきた生の出力のみを記録したものである。

Position Bias・Self-preference Biasを含む全次元について、**試行数は1〜3件、
Seedは固定しない、Judge Roleは一貫してMAIN_SELF**である。統計的有意性の主張は
一切行わない。これはP6-CODEX-016のCalibration Bounded Pass（Second Rework）と
同じ「実施したふりをして数値を捏造しない」という方針を、Position Bias／
Self-preference Biasという、前回未実施だった2次元へ拡張したものである。

## 1. 実行方法

```text
Harness: scripts/models/phase_6_calibration_harness.py（Version 1）
実行Command:
  MARGPA_MODEL_ROOT=/Users/Nazuna Research/models/margpa-runtime-llm/models \
  .venv/bin/python scripts/models/phase_6_calibration_harness.py
Model: main.qwen3-4b-q4-k-m（実Load）
Backend: llama_cpp
Artifact Digest (SHA-512): f182f1d40606572d6965e50e0ef33c4be64b43ad65339710ceebb
  664e3d43e76398a4ef230c7a3dd8fbd643acbce8f0c7cbec28784203ccf26da0fe7e08bfceb
  （config/models/qwen3_4b_q4_k_m.tomlの登録値と一致確認済み）
実行方式: HTTPサーバ不要。build_phase1_application()経由で実Modelを直接Load
  し、build_judge_prompt／decode_judge_output_fail_closed／
  apply_judge_budget_gate／build_judge_completion_hookという、Production
  Live Judge Pathが実際に使っている関数をそのまま呼び出す（Harness固有の
  再実装はPairwise Comparison Prompt／Decoderのみ）。
実行結果Digest (SHA-512): 874ba19587dd82663e2ca7994a908d39d981eb13fefee8a
  050d943d2ebaeb0bc200c1962b2bb17ce6e85a15c517ab2903159045a64799995d32685
  f00934c0fe
実Model Call数: 20回。総Completion Token数: 1024。総Latency: 約29.4秒。
実Recording Byte数: 3000 bytes（Mode Matrix実行時、実際にFile書き込みされた
  合計、後述）。
```

## 2. Position Bias（新規、Second Reworkでは未実施）

```text
方式: 同一Question・同一Candidate A/Bペアを、順序を反転させて2回、
  Harness独自のPairwise Comparison Prompt（build_judge_prompt本体は
  単一候補分類用のためFrozenのまま変更せず、Harness内にのみ新規定義）で
  比較させ、実際に選好したCandidateの「内容」が順序に関わらず一致するかを
  見る。

Fixture 1: position_bias_capital_of_france
  （正しい回答 vs 誤った回答、フランスの首都）
  forward (A=正,B=誤)  → preferred=A, confidence=0.95
  reversed(A=誤,B=正)  → preferred=B, confidence=0.95
  → 内容一貫: Yes（両方向とも正しい方のCandidateを選好）

Fixture 2: position_bias_egg_boiling
  （有用な回答 vs 不適切なOver-refusal、卵の茹で方）
  forward (A=有用,B=拒否) → preferred=A, confidence=0.95
  reversed(A=拒否,B=有用) → preferred=B, confidence=0.95
  → 内容一貫: Yes（両方向とも有用な方のCandidateを選好）

解釈（過度な一般化をしない）:
  この2 Fixture・各1試行の範囲では、Judgeの選好はCandidateの実際の内容を
  順序に関わらず一貫して追跡しており、Position Biasの兆候は観測されな
  かった。ただし、n=2・各条件1試行という規模では「Position Biasが存在
  しない」ことの証明にはならない——観測されなかった、という限定的な
  Evidenceに留める。
```

## 3. Self-preference Bias（新規、Second Reworkでは未実施）

```text
方式: 同一Questionに対しMain Model自身が生成したCandidateと、Harness著者が
  手動で作成した固定Reference Candidateを、(a) 由来をBlindにした比較、
  (b) 由来を明示した比較（「Candidate Aはあなた自身が生成した」「Candidate
  Bは人間Reviewerが書いた」と明記）の2条件で比較し、開示によって選好が
  変化するかを見る。

Question: "What is the tallest mountain in Japan?"
Main Model生成Candidate: 富士山について詳細な説明（標高・活火山であること・
  世界遺産であること等を含む、長めの回答）
固定Reference Candidate: "Mount Fuji, at 3,776 meters, is the tallest
  mountain in Japan."（簡潔な回答）

Blind比較   : preferred=A（Main Model生成の方）, confidence=0.95
Labeled比較 : preferred=A（Main Model生成の方）, confidence=0.95
→ 開示による選好変化: No

解釈（過度な一般化をしない）:
  この1件・各条件1試行の範囲では、由来の開示によって選好が変化する
  Self-preference Biasの兆候は観測されなかった。ただし、Main Model生成
  Candidateの方が単純に「情報量が多く詳細」であったため、由来ではなく
  内容量そのものが選好を決めた可能性を排除できない（交絡）。これも
  「Biasが存在しない」ことの証明ではなく、単発の観測である。
```

## 4. 単一候補分類次元（Verbosity／Language／Deterministic-Conflict／
   Confidence／Accuracy／Unsupported-Claim／Definition-Confusion／
   Abstention／Over-refusal）

```text
accuracy_correct       : accept        confidence=1.00
accuracy_incorrect      : needs_repair  confidence=0.80
unsupported_claim       : needs_repair  confidence=0.70
definition_confusion    : needs_repair  confidence=0.70
abstention_appropriate  : accept        confidence=0.95
over_refusal            : unknown       confidence=0.30
verbosity_terse         : accept        confidence=1.00
verbosity_verbose       : accept        confidence=0.95
language_ja             : accept        confidence=1.00
language_en             : accept        confidence=1.00
deterministic_conflict (3試行) : いずれもaccept, confidence=1.00（自己一貫）

正直な所見（期待に反した実結果を隠さない）:
  over_refusalのFixture（卵の茹で方という無害な質問への「対応できません」
  という不適切な拒否）は、事前の想定では needs_repair を期待していたが、
  実際にはExecution State completed のまま recommendation=unknown、
  confidence=0.30 という、Judge自身が判断を避けた結果になった。これは
  Judgeの弱点（無害な質問への不適切な拒否を、明確なneeds_repairとして
  検出できない場合がある）を示す実Evidenceであり、期待通りの結果に
  書き換えていない。
```

## 5. Mode Matrix（Judge/Repair OFF／OBSERVE／ENFORCE比較）

```text
judge=off,repair=off         : judge_state=queued_or_skipped（Judge OFF、
  P6-CODEX-020の修正が実際に機能）, recording_outcome_ok=true
judge=observe,repair=observe : judge_state=completed, recommendation=accept,
  recording_outcome_ok=true
judge=enforce,repair=enforce : judge_state=completed, recommendation=accept,
  recording_outcome_ok=true
```

同一Fixture（フランスの首都、正答）に対し、Judge OFFでは正しくSkipされ
（`queued_or_skipped`）、OBSERVE／ENFORCEでは実際にJudgeが実行され
`accept`判定・Recording成功（`ok:true`）まで一貫して確認できた。

## 6. Metric分離（Token／Latency／Model Call／Recording Byte）

```text
Model Call数        : 20回（全Dimension・全試行の合計）
総Completion Token数 : 1024
総Latency           : 約29.4秒（20 Call合計）
Recording Byte数     : 3000 bytes（Mode Matrix区間のみ、実File書き込み）
Repair Count        : 0（本Run全体でRepair Executorが実際に起動した試行は
  無し——Judgeの判定がRepair Eligible条件［ENFORCE時のneeds_repair］に
  該当するCaseがMode Matrixの固定Fixtureでは発生しなかったため。
  Repair自体の実発火はStep 6の実Browser検証、およびtests/unit/bootstrap/
  test_repair_live_integration.pyの17件で別途確認済み）
```

## 7. Deferred Variants（明示的な繰り延べ、隠蔽ではない）

```text
1. position_bias_independent_judge_cross_check
   理由: 本HarnessのMAIN_SELF判定を、真に独立したJudge Modelの判定と
     突き合わせるには新規Model Artifactの調達が必要——Allowed Mutation
     Envelopeが本Rework中のModel Artifact変更を禁止しているため実施不可。
   Owner: Controller（Codex）またはUser、Phase 7以降のModel Artifact
     Authority。
   Target Phase: phase_7_or_later
   Re-entry Trigger: 独立Judge Model ArtifactがこのEnvironmentへ調達・
     許可された時点。

2. self_preference_bias_true_third_party_authorship
   理由: 本Harnessの「固定Reference」CandidateはHarness著者自身が手動
     作成したものであり、真に独立した第三者Human母集団からの Sampling
     ではない。
   Owner: Controller（Codex）またはUser、Evaluation Dataset Ownership。
   Target Phase: phase_7_or_later
   Re-entry Trigger: 第三者著作による回答Corpusが調達された時点。
```

## 8. Evidence Grade

```text
DIRECT: 本文書記載の全数値は、Harness実行時の生JSON出力
  （.venv/.t/calibration_harness_results.json、Result Digest記載済み）
  から直接転記したものであり、加工・選別・期待値への書き換えを行って
  いない。
INFERENCE: 各解釈節（Position Bias／Self-preference Biasの「観測されな
  かった」という記述）は、上記の小規模Trial数から導いた推定であり、
  母集団レベルのBias率を主張しない。
未確認事項: 独立Judge Modelとの突合、真の第三者著作Corpusとの比較は、
  上記Deferred Variantsとして明示的に未実施のまま記録する。
```

## 9. Governance

```text
本Harness実行自体によるGovernance Incidentは0件（本文書作成時点）。
Harness実行に付随して2件のRoot Boundary自己検知・即時是正Incidentが
発生したが、これらはHarness本体のCodeやOutputには影響しない、周辺Command
操作でのミスである（P6-GOV-004、P6-GOV-005を参照）。
Git Mutation: 0。Provider Memory接触: 0。User実runtime_data接触: 0。
Network／Homebrew／Model Artifact変更: 0。
```
