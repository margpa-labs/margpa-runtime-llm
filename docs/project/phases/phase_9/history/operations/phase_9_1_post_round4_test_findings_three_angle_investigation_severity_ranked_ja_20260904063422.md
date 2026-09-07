# Phase 9-1 実機Test後6件Finding — 3視点独立調査・重度別統合報告

```yaml
document_id: phase_9_1_post_round4_test_findings_three_angle_investigation_severity_ranked_20260904063422
document_type: three_angle_investigation_result_severity_ranked
document_state: findings_confirmed_no_fix_authorized
language: ja
phase: phase_9
program: phase_9_1
recorded_at: 2026-09-04 06:34:22 JST
recorder_role: Claude(Bounded Implementation Worker)
trigger: User指示「とりあえず、全部原因を全力で調査しろ。完全別観点で3回やれ。修正とか実装とかには勝手に入るなよ。」
methodology: 3つの独立Agentによる並行調査(Worktree隔離、Read-only)
  agent_1: 静的Code/Exception-Path監査
  agent_2: Production配線監査＋Git履歴Provenance監査
  agent_3: 実機再現(実Model Load、生Exception捕捉、Deep Instrumentation)
in_response_to: history/operations/phase_9_1_judge_dispatch_fix_post_round4_user_real_hardware_manual_test_evidence_ja_20260904055535.md
git_action: none
source_mutation_this_task: none(3 Agentとも一切のSource/Test変更なし。実機再現Scriptは
  全てScratchpad配下、Project外、Git管理外)
implementation_authority: none(本Docは調査結果の統合記録であり、修正実装は一切行っていない)
```

## 0. 位置づけ

先の実機Manual Testで見つかった6件のFindingについて、3つの完全独立した観点(静的監査／実機再現／配線・履歴監査)で並行調査を実施した。以下、確定度に基づき重度別に整理する。**修正・実装は一切行っていない。すべて調査結果のみ。**

## 1. 重度: 最高(Critical) — 実際にCrashリスクまたは完全機能不全に達している

### 1-1. Selene+Main同時稼働時、Native Decode自体が失敗する(`llama_decode returned -3`)

```text
実機再現(Agent 3、CONFIRMED、3/3): Main+Selene同時Load・初回Dispatch(先行する
取り残しThreadが存在しない、純粋な最初のTurn)で、55ms前後の即時失敗を3回とも
再現した。Deep Instrumentationで、集約前の生Exceptionを捕捉:

  RuntimeError: llama_decode returned -3
  (adapter.py generate() -> chat_template.py create_chat_completion()
   -> llama_cpp内部decode() -> "raise RuntimeError(f'llama_decode returned
   {return_code}')")

対照実験(Agent 3、Selene単体・Main非稼働): 同じ即時失敗は一切発生せず、実際に
22-24秒かけた正常なGenerateが成立する(その後の失敗は別種の正当なmalformed_output
のみ)。

結論: これはRound 1-4が対象にした「取り残しThreadによるLock競合／正当なBusy
衝突」とは**別の、Native層の障害**である(初回Dispatchで発生しうる時点で
Lock競合系のメカニズムでは説明不能)。Main+Selene同時稼働時にNative層(Metal/GPU
Compute Graph)で実際に競合が起きていることを、初めて生Exceptionで実証した。
これは根本原因調査(9/3)のAgent 3が「静的監査だけでは確証できない」と留保した
"Native-level競合"仮説(§5-B)を、初めて実機で確定させたものである。
```

**関連する生きているRisk(重要)**: 現在Resource Gateは配線から外れており(SSS
Recovery後、`AllowAllRoleResourceGate`)、2026-09-01に実際にMainをCrashさせた
Main+Selene同時Load Incidentへの保護が無い状態のまま。今回確認したNative Decode
失敗(`llama_decode returned -3`)が、その元Incidentと同一・関連するMetal/GPU
Native層の不安定性である可能性が高い。Resource GateはSSS級Incidentを起こした
Subsystemであり、User明示の再着手判断なしに変更しない方針を維持するが、この
Native層の問題自体はGateの有無とは独立した、より根の深い技術的課題として認識
すべきである。

### 1-2. Gemma Dedicated Judgeが実質100%機能不全 — 未捕捉のPydantic ValidationErrorが2種類存在

```text
実機再現(Agent 3、CONFIRMED、readily reproducible): Qwen 5回中3回・DeepSeek 2回中
1回で`unhandled_error:ValidationError`を再現。原因は2つの独立したMechanism。

Mechanism A(reason_code Pattern違反): `SemanticCriterionResult.reason_code`
  (`modules/runtime_governance/domain/`)が厳格な正規表現
  `^[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$`を要求する一方、Judge Promptの実際の
  指示(`selene.py`の`response_schema`)は`"reason_code": "short code"`としか
  指定しておらず、Format制約を一切課していない。実測、136件の実Decode済み
  reason_codeのうち**12件(約8.8%)**が、Model自身が書いた自然文
  (例: `'insufficient evidence'`、`'no emotional input'`)であり、この
  Patternに違反していた。この`SemanticCriterionResult`構築箇所(`selene.py`
  `evaluate()`内、約L568)はtry/exceptで囲われておらず、生のPydantic
  ValidationErrorがそのまま外側まで抜ける。

Mechanism B(failure_reason自身のmax_length超過、新規発見): 
  `SemanticEvaluationResponse.failure_reason`には`max_length=128`制約がある。
  `JudgeDecodeError.reason`が長い場合(例: "missing criterion ids: [...]")、
  selene.py**自身の**except節が組み立てる`f"malformed_output:{exc.reason}"`
  という文字列自体が128字を超え、**その場で二重目のValidationError**が
  発生し、元々のmalformed_output診断そのものを握り潰す。Qwen・DeepSeek
  双方で同一に再現した。

両Mechanismとも、5連続すべて同一失敗だったGemma(Dedicated)の実際の原因である
可能性が高い(Agent 1の静的監査ではGemma固有の説明に到達できなかったが、
Provider非依存の共通メカニズムであることがAgent 3の実機再現で確定した)。
Gemma Dedicated Judgeは、この2つのMechanismのいずれかに繰り返し当たり続けた
結果、実質的に使用不能な状態になっている可能性が高い。
```

## 2. 重度: 高 — 実運用のGolden Pathを構造的に壊す

### 2-1. Main Governance自身のENFORCE機構(Semantic層)が実際には何も実行していない

```text
確定事実(Agent 1・Agent 2・Agent 3の3者一致):
  `resolve_semantic_action()`(semantic_runtime.py)の出力`executed_disposition`
  は、Codebase全体で消費者ゼロ。`SemanticRuntimeEvidence.action`という
  Evidence記録用フィールドに格納されるだけで、実際に何かを実行/ブロックする
  経路には一切繋がっていない。Judge/Repair側の実行判定は`judge_mode`/
  `repair_mode`のみを見ており、`main_mode`を一切参照しない。

Git履歴による確定(Agent 2、`git log -p -S executed_disposition`等):
  この機能は`fe03484`(Phase 6 Checkpoint)で新規導入されて以来、一度も
  外部消費者を持ったことがない。**過去に接続されていて後から切断された
  回帰ではない。** Docstring自体が導入当初から
  "Resolve recommendation separately from the authority-owned action."と
  明記しており、「推奨算出」と「権限を持つ主体による実行」の分離は
  設計当初からの意図と読み取れる。

重要な文脈(Agent 2の発見、最重要の補足情報):
  `docs/project/shared/history/planned_work/
  phase_11_plus_governance_enforce_structural_semantic_layer_split_
  reservation_ja_20260902214032.md`(2026-09-02 21:40 JST、今回の実機Test
  より1日半前)は、User自身がARGD/DAGD全109件が例外なくJudge(LLM)前提の
  評価方式であり、「Governance ENFORCEはそもそもJudgeも何もなく、Model
  そのものに強制適用させるものだったはず」という自身の期待との齟齬を
  実機Manual Recheckで発見し、議論した記録である。この設計はPhase 4
  (Codex原設計)由来であることも確認済み。**Userはこの議論の末尾で
  「とりあえずこれはPhase11以降に回す。今はCodexが作った既存設計の
  ままでよい。さっさとMVP(Phase 10)を作りたいので。」と明示決定している。**

  ただし、今回発見した内容はこの既存議論より一段深い: Sept-2の議論は
  「Judge依存であること自体」への異議に集中しており、「Judgeが実際に
  動いてENFORCEが有効な場合でも、その判定結果は誰にも使われない」という
  事実そのものには踏み込んでいなかった。Package 2の"WU-07 DONE"Claim
  (「実Judge Resultを受け取れるようになった」ことを以て完了とした)から
  はこの欠落は読み取りにくい。

  なお、実機確認(Agent 3)では副次的な非対称性も見つかっている:
  `resolve_semantic_action()`のEnforce分岐とObserve分岐で、has_uncertain/
  has_deviationの判定順序の扱いが異なり、同一の評価結果に対して
  `recommended_disposition`自体がEnforce/Observeで異なる値になるケースが
  ある(Turn 3の実例で確認)。

**訂正**: 本Recorderが直前(2026-09-04 02:21 JST)のPhase Indexで、この件を
「最重要」「UF-P9-004実質再Open」と単独で強調したのは、上記のSept-2既存
議論・User既存決定を踏まえずに書いたものであり、文脈が不足していた。
「回帰でも見落としでもなく、既に認識・Phase11延期決定済みの既知課題の、
一段深い技術的詳細」というのがより正確な位置づけである。優先度判断は
改めてUser自身に委ねる。
```

### 2-2. Main=DeepSeek + Judge=DeepSeek(self)のMode適用失敗 — Provider Selection Controllerの共有CAS Revision Counter競合

```text
実機再現(Agent 3、CONFIRMED、Byte-for-byte一致): 実際にRace条件を再現し、
Userが見たものと完全に同一のFailureを捕捉した。

  RACED_judge_reselect_with_stale_revision: ProviderSelectionError(
    code=revision_conflict,
    safe_message="The provider selection changed; reload and retry.")
  judge_configured_provider_after_raced_attempt:
    configured_provider="main.qwen3-4b-q4-k-m"（古いまま更新されない）
  activate_judge_after_raced_selection: state=unavailable,
    failure_reason="main_model_mismatch_requires_main_switch"

  対照(Race無し、Freshな状態でのJudge再選択): state=active（正常成立）

確定した根本原因: `ProviderSelectionController`はMAIN/GUARD/JUDGE
3つのRole全体で**単一のCAS(Compare-And-Swap) Revision Counter**を共有
している。Main切替1回につきこのCounterが**2回**Bumpされる。Main切替
"直後"にJudgeを再選択しようとするClientが、切替前の古いRevisionを
握ったままだと`REVISION_CONFLICT`で拒否され、Judgeの`configured_provider`
は静かに古い値のまま取り残される——結果として
`main_model_mismatch_requires_main_switch`という、あたかも「まだ選択して
いない」かのような誤解を招くFailure Reasonへ収束する。

「Server再起動しても直らない」という observation の説明: これは
Server再起動で回復するはずの一時的State不整合ではなく、**再選択操作
そのものが実行された瞬間に起きるCAS Protocol上の構造的Race**である
(Agent 1はServer再起動でJudge選択がGemma Defaultへ戻るはずと指摘し
"矛盾"と評価したが、Agent 3の実機再現により、そもそも問題の本質は
「再起動後もStaleな値が残る」ことではなく「Main切替直後のJudge再選択
操作自体が、タイミング次第で毎回Raceしうる」ことだと判明し、この点は
解消された)。
```

## 3. 重度: 中 — 既知カテゴリ範囲内、今回頻度を実測できた

### 3-1. `malformed_output`の頻度

```text
実機再現(Agent 3)による実測:
  Selene単体: 2/2(100%) — "repair recommendation has no deviated criterion"、
    "recommendation contradicts criterion results"（Selene自身のJSON内で
    推奨とCriterion結果が論理的に矛盾）。
  DeepSeek: 2回中1回は明示的malformed_output
    ("expected exactly one JSON object, found 5"、DeepSeekが5個の別々の
    JSON Objectを出力)、残り1回は§1-2 Mechanism Bにより別種のValidationError
    へ変質。
  Qwen: 5回中1回がMechanism Bにより変質、それ以外は正常。

これはRound 1-4の変更が原因ではなく(Retry機構はMODEL_BUSYのみ対象、Decode
失敗経路には一切関与しない、静的監査Agent 1でも確認済み)、既存の独立した
Model品質問題(既知のOF-P2-002/UF-P6-010系)の範疇。ただし、DeepSeekも
Gemmaと同様の「複数JSON Object出力」問題を起こすことが今回新たに確認され、
これはGemma固有ではなく、小型量子化Model全般に共通しうるJSON規律の問題で
ある可能性を示唆する。
```

## 4. 重度: 低／設計論点 — Bugではないが、検討価値のある挙動

### 4-1. 部分評価(evaluated<32、unknown混入) — Bugではないが、Repair機会を奪いうる設計

```text
確定(Agent 1・Agent 3一致、CONFIRMED NOT A BUG): `JudgeCriterionDisposition`
は`PASS`/`DEVIATION`/`UNKNOWN`の3値のみで、`UNKNOWN`はSchema上正当な値。
`decode_judge_output()`の完全性Checkは「全criterion_idが存在するか」のみを
見ており、"unknown"という正直な回答も正常にDecodeされる。今回のケースは
Modelが32件中2-3件について正直に「わからない」と回答した結果であり、
Batchの一部だけが不完全にDecodeされた、というBatch処理上の欠陥ではない。

ただし実機再現(Agent 3)で新たに判明した設計上の論点: `resolve_semantic_
action()`の判定順序は`has_uncertain`(unknown/deferred含む)を`has_deviation`
より先にCheckする。このため、32件中わずか1-2件が"unknown"であるだけで、
残り30件が明確なDeviationを示していても、Turn全体が`safe_fallback`へ
収束し、Repairの機会そのものが失われる。これはBugではなく設計判断の
結果だが、「一部不確実 → 全体棄却」という現在の優先順位が意図どおりか
どうかは、Controller/User Authorityが判断すべき論点として記録する。
```

## 5. 調査により解消・格下げされた仮説

```text
- Selene即時失敗の「Pathological Repetition Latch」説(Agent 1が候補として
  提示): Agent 3の実機再現(§1-1、Native Decode Error確定)により、
  少なくとも今回の失敗パターンについてはこちらの方が直接の説明として
  優先される。Pathological Repetition Latch自体が別の場面で起こりうる
  可能性は排除されない(既存Open扱いのまま)が、本件の主因ではないと判断。
- Resource Gate状況とValidationError(§1-2)の直接的因果関係(Agent 2が
  弱い仮説として提示): Agent 3により、ValidationErrorは純粋なPydantic
  Contract違反(reason_codeの正規表現、failure_reasonのmax_length)である
  ことが確定したため、Memory Pressureとの直接的因果関係は考えにくい。
  この仮説は棄却してよいと判断する。
- Resource Gate状況とSelene即時失敗(§1-1)の関連性(Agent 2が提示): これは
  むしろ強化された。Native Decode Error自体はMemory Pressureとは別の
  Native層競合だが、Main+Selene同時稼働という同一条件下で起きている点、
  および2026-09-01の元Incident(Main Crash)と条件が一致する点から、
  引き続き関連性の高い仮説として維持する。
```

## 6. Recovery / Source変更

```text
3 Agentとも一切のSource/Test変更なし。実機再現Scriptは全てScratchpad配下
(Project外、Git管理外)。Git commit/push一切なし。

実機再現Scriptの所在(Agent 3使用分、将来参照用):
  /private/tmp/claude-501/-Users-yukitakagi-Documents-pseudo-root-99-ps-
  Main-Creating-Objects---20260219-MARGPA-RUNTIME-LLM-margpa-runtime-llm/
  bccb7444-2530-4d4f-bbda-033f06c5df80/scratchpad/p9_judge_investigation/
  （Session-local、将来のSessionでは再実行不可。Project外のため本Doc記載の
  結果Summaryのみが再利用可能な記録）
```

## 7. Exact Next Action

```text
1. 本Docの内容をUserへ報告し、§1-4それぞれについて着手要否・優先順位の
   判断を仰ぐ(修正実装は一切行っていない、Authority待ち)。
2. §2-1(Main Governance ENFORCE機構未接続)は、既存のPhase 11延期決定
   (§2-1本文参照)を踏まえた上で、改めてUser自身に優先度判断を仰ぐ。
3. Shared未解決Registry(shared/unresolved_work/current_unresolved_findings_
   registry_ja.md)への反映は、本Docの内容が固まった後、直接編集はせず
   history/への追記または User判断待ちとする。
```
