# Phase 6 Second Rework — BLOCKED Handoff（一部項目のみ）

```yaml
document_id: phase_6_claude_second_rework_blocked_handoff
status: blocked_partial
phase: phase_6
work_unit: p6_second_rework
role: Claude側設計統括者役
created_at: 2026-08-23 11:12:42 JST
authority: phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md
references:
  - phase_6_governance_evidence_correction_ja_20260823105500.md（P6-GOV-002）
  - phase_6_calibration_bounded_pass_ja_20260823110941.md
  - phase_6_governance_evidence_correction_ja_20260823053000.md（P6-GOV-001）
```

## 0. 結論

本Second Reworkは、Second Independent Review Handoff
（`phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md`）
が要求したP6-CODEX-009〜016、再OpenされたP6-CODEX-001／003／004、
P6-GOV-002個別Acceptance ID再判定のうち、**大部分を技術的にClose**した。
ただしP6-CODEX-016（Calibration一式）のうち2項目（Position Bias、
Self-preference Bias）について、**Frozen Phase 6内で技術的に成立しない
真のBlocker**を特定した。これらはCandidateとして「未実施のまま黙って
Passにする」ことも、「無理に実装して機能を偽装する」こともできない
性質のものであるため、本文書はComplete Candidateではなく**この2項目に
限定したBLOCKED Handoff**として提出し停止する。

**それ以外の全項目**（P6-CODEX-001／003／004／009／010／011／012の大部分／
013／014／015、P6-GOV-002の個別Acceptance ID群、Calibrationの残り4次元
のBounded実施）は、下記§2のとおり実装・Test・実Hardware検証まで完了し、
Backend 1494件・Frontend 198件のTest全PASS、ruff／mypy／eslint／tsc／
vite build全通過を維持している。

## 1. Blocker詳細（再現手順・Root Cause・影響範囲・代替案・必要Authority）

### Blocker A: Position Bias Calibration

```text
再現手順:
  1. src/margpa_runtime_llm/bootstrap/judge_live_integration.py の
     `_run_judge()` を読む。
  2. Judgeへの入力は `build_judge_prompt(case=EvaluationCase, 
     candidate_answer=context.assistant_content, rubric_id=...)` の
     一本のみであり、候補は常に1件（そのTurnが実際に生成した1つの
     実回答）である。
  3. Position Biasを意味のある形で計測するには、同一の2つの候補
     （例: 候補A/候補Bを入れ替えて2回Judgeに提示し、判定が入れ替わるか
     を見る）をJudgeへ渡すPairwise Comparison Interfaceが必要だが、
     現行のLlmJudgeRequest／build_judge_prompt／decode_judge_output系は
     すべて「1候補→Accept/Needs-repairの二値＋確信度」という単一候補
     分類のSchemaで統一されている（judge_prompt_builder.py、
     judge_output_decoder.py、llm_judge.py のいずれにもPairwise用の
     Field／PromptTemplateが存在しない）。

Root Cause:
  Phase 6のLive Judge Architecture自体が、Evaluation Datasetに対する
  既存のDeterministic Evaluator（repair_orchestrator.py等が前提とする
  Batch評価の文脈）から流用された「1候補分類」Interfaceをそのまま
  Live Conversationへ転用したものであり、そもそもPairwise Comparison用に
  設計されていない。これはBugではなく、Frozen Phase 6のArchitecture文書
  （judge_prompt_builder.py・llm_judge.py等、既にPhase 6-D-WU-001〜003で
  Freeze済み）が定めたSchemaそのものの制約である。

影響範囲:
  P6-CODEX-016のPosition Bias計測項目のみ。Judge自体の実運用
  （Accept/Needs-repair判定、Repair Eligibility解決、Recording）には
  一切影響しない（本Reworkの実Hardware検証で実証済み、
  phase_6_governance_evidence_correction_ja_20260823105500.md §1参照）。

代替案:
  (a) Pairwise Comparison用の新規Judge Prompt/Response Schemaを追加し、
      既存の単一候補分類Schemaと並存させる（Judge Portの拡張、
      新規Capability追加に相当）。
  (b) Position Bias計測を諦め、Phase 7以降のRoadmap項目として
      切り出す。
  (c) 単一候補分類のまま、「同じ候補を独立した2回のTurnとして提示し
      判定が変わるかを見る」疑似的な代替指標を採用する（真のPosition
      Biasではなく、Deterministic-Conflict指標と実質的に同じものになる
      ため、Position Biasの代替としては不適切）。

必要Authority:
  (a)を選ぶ場合、Judge Port（Phase 6-D-WU-001の既存Frozen Schema）への
  変更はFrozen Phase 6のScope外であり、Controller側でのPhase 6
  Architecture変更承認、またはPhase 7以降への正式な繰り延べ決定が必要。
```

### Blocker B: Self-preference Bias Calibration

```text
再現手順:
  1. src/margpa_runtime_llm/modules/evaluation/application/
     judge_role_resolver.py の `resolve_judge_independence()` を読む。
  2. 本環境に構成されているJudge Roleは常に
     `JudgeIndependenceClass.MAIN_SELF`（Main ModelとJudge Modelが
     同一Instance）である。これは既存のRecovery Entry（Phase 6-D以降）
     で繰り返し確認・記録されてきた事実であり、本Second Reworkで
     新たに変化していない。

Root Cause:
  Self-preference Biasを意味のある形で計測するには、「Main Model自身が
  生成した候補」と「独立した別Model（または人間）が生成した候補」を
  同一Judgeに提示し、Judgeが前者を優遇するかを比較する必要があるが、
  本環境には独立したJudge Artifactが一切存在しない
  （すべてのRecovery EntryがJudgeIndependenceClass.MAIN_SELVESとして
  確認済み。config/models/配下にJudge専用の別Model Definitionは無い）。

影響範囲:
  P6-CODEX-016のSelf-preference Bias計測項目のみ。

代替案:
  (a) 独立したJudge Model（例: 別のGGUF Artifact）を新規にDownload／
      Load Configし、真に独立したJudge Roleを構成する
      （Model Artifact取得はAllowed Mutation Envelopeの「Model
      Canonical/Derived Artifact変更禁止」に抵触するため、本Rework
      Scope内では実行不可）。
  (b) Self-preference Biasの計測をPhase 7以降（独立Judge Artifactの
      正式な調達が決まった時点）へ繰り延べる。

必要Authority:
  (a)を選ぶ場合、新規Model Artifactの取得はAllowed Mutation Envelopeで
  明示的に禁止されている操作であり、Controller側での例外承認、または
  Phase 7以降でのAuthority付与が必要。
```

## 2. Closed項目の要約（詳細はP6-GOV-002 Correctionを参照）

```text
P6-CODEX-001（Cross-turn Race/Lifecycle）: CLOSED。
  ModelAccessCoordinator新規実装に加え、実Hardware Golden Path検証中に
  「Judgeがどのモードでも実際には一度も実行されていなかった」という
  重大Bug（Main Slot解放Timingの問題）を発見・修正・実Server再検証まで
  完了。全Unit/Integration Testでは検出できなかった種類の欠陥であり、
  実機検証を行ったことで初めて捕捉できた。

P6-CODEX-003（Raw Status Code）: CLOSED。
P6-CODEX-004（Recording非直交性／Writer境界）: CLOSED。
P6-CODEX-009（Repair Core）: CLOSED（実Hardware上でEligibility→候補生成→
  Rejudge→Outcome判定→Accept/Reject、およびAttempt Provenance付与まで
  End-to-end実証済み）。
P6-CODEX-010（Detached Judge Thread）: CLOSED。
P6-CODEX-011（Recording/Judge結合、Writer強化）: CLOSED。
P6-CODEX-012（Status/UI状態機械）: PARTIAL→大部分CLOSED。
  Chat UI自身のpreparing/guarding Live状態、Feature Modes Panelでの
  Judge Run状態／Repair結果／Recording Outcome表示は実Hardwareで実証。
  judging/repairing/rejudgingのChat Bubble自体でのLive視覚遷移は
  未実装（既存のJudge OFF/OBSERVE Canonical Behavior不変という
  Architecture上の制約と両立させる設計上の判断、Blocker扱いはしない）。
P6-CODEX-013（Attempt Provenance）: CLOSED。
P6-CODEX-014（Component Identity）: CLOSED。
P6-CODEX-015（Safe Refusal Raw Code）: CLOSED。
P6-CODEX-016（Calibration）: PARTIAL。Verbosity/Language/Deterministic-
  Conflict/Confidenceの4次元をBounded規模（各条件1〜3試行）で実Server・
  実Modelに対して実施しPASS（実行自体のFailure 0件）。Position Bias／
  Self-preference Biasは§1のBlockerにより未実施。統計的に有意な規模
  （各条件数十件以上）でのMatrix化も未実施。
P6-GOV-002: 個別Acceptance ID再判定完了（Correction文書参照）。
  再監査中にP6-ACC-026の実Bug（Repair OBSERVE下での意図しない追加
  Generation）を発見・修正。
```

## 3. 検証状態

```text
Full Test: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider
  --basetemp=.venv/.t/final → 1494 passed, 5 deselected。
Static: ruff check src tests scripts → All checks passed。
        mypy src → Success: no issues found in 273 source files。
Frontend: npm run typecheck / lint / test（198 passed）/ build → 全通過。
Real-Model: main.qwen3-4b-q4-k-mを実Load、実Browser経由でChat 2回、
  API直叩きでCalibration 8 Turn、Server Graceful Shutdown確認。
Root外操作: 0（Test Temporary RootはすべてProject-local `.venv/.t`配下）。
Provider Memory接触: 0。User実runtime_data接触: 0
  （すべて使い捨てのTest/Golden Path用Scope Idを使用）。
Git Mutation: 0（add/commit/push等は一切未実行）。
Network/Homebrew/Model Artifact変更: 0。
```

## 4. Controllerへの依頼事項

```text
1. §1のBlocker A／Bについて、代替案(a)〜(c)のいずれを採るか、または
   Phase 7以降への正式な繰り延べとするかの意思決定。
2. 上記が決まるまで、本Second Reworkの成果（§2のCLOSED項目群）を
   「Phase 6 Second Rework Complete Candidate」として正式に受理するか、
   Blocker解消を待つかの判断。
3. 本文書・P6-GOV-002 Correction・Calibration Bounded Passの3文書は
   いずれもAppend-onlyであり、既存Historyを書き換えていない。
```
