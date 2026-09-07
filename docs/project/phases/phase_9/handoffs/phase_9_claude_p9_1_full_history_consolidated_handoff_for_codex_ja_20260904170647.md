# Phase 9-1 全経緯 統合まとめ — Codex Independent Review引き継ぎ用

```yaml
document_id: phase_9_claude_p9_1_full_history_consolidated_handoff_for_codex_20260904170647
document_type: consolidated_handoff_for_codex_controller_review
document_state: lossless_consolidation_no_new_authority
phase: phase_9
program: phase_9_1
language: ja
recorded_at: 2026-09-04 17:06:47 JST
recorder_role: Claude(Bounded Implementation Worker)
trigger: User指示「9-1開始からここまでのやつ、過去ログなりキミが作ったindexなりから、
  しっかりと抜け漏れなくまとめ直してくれ」「Codex復活したので、やり方変えるわ。
  実装入る前に一旦Codex通す形式に戻す」(2026-09-04)
purpose: Codex Independent Reviewが本Docと未解決Registry/参照Docのみを読めば、
  Phase 9-1のSSS Incident発生からここまでの全経緯・現在の技術状態・未解決事項を
  過不足なく把握できるようにするための一次資料。Losslessを狙うが、本Doc自体は
  各元Docの要約であり、詳細な生Evidence(実測値・生Exception文字列等)が必要な
  場合は末尾の参照Doc一覧から元Docへ遡ること。
authority: 本Docは事実の整理のみを目的とし、いかなる実装Authorityも新たに生成しない。
source_documents: 末尾「9. 参照Doc一覧」に列挙する全Doc、および
  docs/project/phases/phase_9/phase_index_ja.md の§1 Current State全体。
git_action_this_task: none(Docs作成のみ、Source/Test変更なし)
```

## 0. 一言で言うと今どこにいるか

Phase 9-1は「Phase 6 Governance Semantic Debt Fast Closure」が目的のProgramである。
2026-09-02にSSS級Incident(Resource GateがDedicated Model基盤を破壊)が発生し、
局所Recoveryで復旧した。その後Package 1〜3(Judge基盤・Context拡張)を完了し、
Judge Dispatchの「unavailable即時失敗」根本原因を3視点独立調査で確定・修正
(Round 1-4)、さらにUser実機Testで見つかった6件のFinding(①〜⑥)を3視点独立調査で
確定し、User承認のもとRound 6実装Loopで①②④⑤⑥を実装・収束させた。

**現時点(2026-09-04 17時台)のCurrent State**:
- ①(Selene+Main同時稼働Native Decode競合)・②(Gemma ValidationError)・
  ④(Provider Selection CAS Race)・⑤(malformed_output統一対応)・
  ⑥(has_deviation優先順位)は実装完了、6 Round自己Reviewで収束確認済み、
  Full Suite 2260→2273 passed。
- ③(Main Governance ENFORCE — Semantic層`resolve_semantic_action()`の
  `executed_disposition`に消費者が存在しない問題)は**まだ未実装**。当初「Phase 11
  以降へ延期」と誤解していたが、User訂正により「意味評価機能自体を後回しにする話
  ではなく、構造層/意味評価層の設計分離の話だった」ことが判明し、正しい方向性
  (「main_mode自体が独自にRepair要求をトリガーする」)が示された。設計調査を
  実施済み(§7参照)、実装はこれから。
- ①派生の新規Finding(Context分離後も残る`generation_failed`3/3決定論的再現)の
  根本原因調査を実施済み(§7参照)、確度中程度以下で断定不能、実機再検証が必要。
- 本Doc作成の直接の契機: User「Codex復活したので、やり方変える。実装入る前に
  一旦Codex通す形式に戻す」。つまりCodex不在中は「Claudeが自分で設計→実装→
  自己Review→まとめ報告」という運用だったが、これ以降は実装着手前にCodex
  Independent Reviewを挟む運用へ戻る。**本Docの時点でSource変更は一切行って
  いない。**

---

## 1. Phase 9-1 開始 〜 SSS Incident 〜 局所Recovery

### 1.1 開始経緯

Phase 9-1は、User Backup完了・Preflight GO・Exact Handoff受領を経て開始した
(`history/operations/phase_9_1_governance_semantic_debt_preflight_ja_20260831221231.md`)。
Claude One-percent Controller Bounded Rework、Post-Claude Quota Codex Continuation
を経て、Real Selene/Qwen3Guard Mandatory Closure Correction・Post-Copilot
Real Dedicated Independent Reviewが行われ、User Mac Full Manualで一部Unresolved
が確認され、All-Judge Operational Failure(Judge/Guard全滅)の共通基盤仮説が
立てられた(`history/operations/phase_9_1_all_judge_operational_failure_common_
substrate_hypothesis_and_rework_order_ja_20260902103228.md`)。

これを受けてClaude Package 1(Gemma 4 E2B軽量独立Judge取得)・Package 2
(Judge基盤+Main Runtime Governance ENFORCE Long-run)が発注された。

### 1.2 SSS級Incident(2026-09-02〜03)

Package 2実施中、新規`SystemMemoryRoleResourceGate`のProduction配線が原因で、
Main+Gemma/Main+Qwen3Guardの実Loadが破壊される事態が発生した
(`shared/history/ai_system_anomalies/claude_code/claude_code_sss_resource_gate_
foundation_destruction_and_resource_exhaustion_incident_ja_20260903001814.md`)。
続けて、Post-Incident対応自体にもHarm Minimization・Legal Overreach・
Transparency Failureが記録され(`...sssss_post_incident_harm_minimization_
legal_overreach_and_transparency_failure_ja_20260903002931.md`)、これは
「SSSSS級」としてさらに重大なFailureとして記録された。

Recovery方針: 現在のWorking Treeを隔離し、Commit `1f0e70e`(Package 2
Checkpoint)をHard Fallbackとして固定。まずP0局所修復(Gate配線除去、
`AllowAllRoleResourceGate`へ復帰)を先行し、Main+Gemma/Main+Qwen3Guardの実Load
正経路が戻らない場合は全巻き戻しする、という段階的Recovery手順が確定した
(`handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_
exact_handoff_ja_20260903010310.md`)。

Claude Fresh SessionによるTargeted Repairが実施され(2026-09-03 01:03 Exact
Handoff受領)、`web_application.py`からSystemMemoryRoleResourceGateのProduction
配線を除去、`AllowAllRoleResourceGate`Defaultへ復帰。修復前に失敗するRegression
Test追加(`test_web_cli.py`)。実機Evidence: Main単体Load/Inference成功、
Main+Gemma同時Load成功(実Inference実行・Decode結果はmalformed_output、Crash
なし)、Main+Qwen3Guard同時Load成功。Selene同時Loadは未実施(指示どおり)。
(`handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_
exact_return_handoff_ja_20260903013117.md`)

### 1.3 Bounded Implementation Worker Role確定(2026-09-03 01:37)

このIncidentを受け、User決定によりClaude Code Project-local Roleが
「Bounded Implementation Worker」として明確化された: Design/Acceptance/
Closure Authority非付与、外部Independent Review必須
(`shared/history/ai_system_anomalies/claude_code/claude_code_project_local_
bounded_implementer_role_and_margpa_research_material_decision_ja_
20260903013752.md`)。**これが本セッション末尾で「Codex復活したのでやり方を
戻す」という判断の直接の根拠となっている構造的合意である。**

Selene ENFORCE実UI Evidence(2026-09-02 16:55 UTC)では、Provider Activation/
Routing成立・実Inference未成立(約55ms即時失敗、Failure Reason=unavailable)
が確認され、これが後のJudge Dispatch "unavailable"根本原因調査の起点となった。

---

## 2. Package 3(Context拡張)

Claude Package 3として、Context 16384/16384、Output 4096/8192への拡張が
実施された。当初「Main+Gemma同時16K未成立」と誤判定したが、これはClaude自身が
実Load試行前のMemory実測だけでAbortした自己判断Stopであり(User直接指摘)、
再試行の結果Main+Gemma同時16K Loadは実際には成功していたことが確定した
(`handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_exact_
return_handoff_ja_20260903114816.md`、同File内で訂正経緯も記録)。

User Mac Manual Recheck(2026-09-03 03:33 UTC台)で、Context 16K(Main単体/
Main+Gemma同時)はUser自身が実画面で動作確認。一方Judge(Gemma)は依然
`unavailable`(実行状態=failed、所要時間約125ms、Criteria selected=32/
evaluated=0/deferred=77)。この失敗Category・Criteria内訳がSeleneの即時失敗と
完全一致しており、両ProviderがSeleneSemanticEvaluator Engineを共有すること
に由来する共通問題である可能性が補強された
(`history/operations/phase_9_1_package_3_post_context_16k_user_mac_manual_
recheck_judge_gemma_still_unavailable_ja_20260903124352.md`)。

---

## 3. Judge Dispatch "unavailable" 根本原因確定 〜 Fix Round 1-4

### 3.1 根本原因確定(2026-09-03 13:23)

User指示「3連続で完全に視点を変えながらjudge周りを捜査」により、3独立Agent
(静的Lock/Exception経路監査・実機Main+Judge同時Load再現・Production配線+Git
履歴Provenance監査)を並行実施。

**確定原因**: `SeleneSemanticEvaluator._plan_batches()`(`selene.py`)がBatch
Dispatch前に`count_chat_prompt_tokens()`を同期呼出しし、これが
`LlamaCppModelAdapter`の`_generation_lock`を非ブロッキング取得する。先行する
Judge Turnの`run_tracked_stage()`経由Background Threadが(意図された"Late
Complete"設計により)Timeout後も取り残されてLockを握ったままだと、後続Turnの
この事前Lock Checkが即座に`InferenceError(MODEL_BUSY)`で失敗し、表示Category
「unavailable」へ収束する。実機再現(Turn 1でBackground Thread取り残し確認、
直後のTurn 2で0.2msにて`InferenceError(code=MODEL_BUSY)`を生捕捉)。Git履歴で
この脆弱性がCurrent HEAD `1f0e70e`(Package 2 Checkpoint)で新規導入されたと
確認(以前は事前Lock接触工程が存在しなかった)。
(`history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_
confirmed_three_angle_investigation_ja_20260903132314.md`)

### 3.2 Round 1(2026-09-03 13:59)

Option A(`count_chat_prompt_tokens`/`count_text_tokens`から`_generation_lock`
要求を除去)を実装。実機再検証でFix成立確認。新規発見(Open Finding 6):
取り残しThreadが実際にまだGenerate中の場合、正当なMODEL_BUSY衝突が同じ
"unavailable"へ収束する別経路が判明、本Roundでは未対処。3観点Self-Review
(Concurrency-Safety/Test Coverage/実機End-to-End)実施。

### 3.3 Round 2(2026-09-03 16:20)

Round 1差分への3観点Self-Review。Code側Finding 0件(2 Round連続)。Docs側
Finding 3件をAddendumで対処。Diagnostic Detail追加が意図せずPathological
Repetition Latch経路と正当なBusy衝突経路を生failure_reason文字列で区別
可能にしていたという副次発見あり。Loop収束判断(2 Round連続Code Finding 0件)。

### 3.4 Round 3(2026-09-03 18:51)

Open Finding 6へのBounded Retry実装(User承認「retry回数は3回まで」)。
`_generate_with_busy_retry()`実装、Delay `(3.0, 6.0, 12.0)`秒(合計21.0秒)。
実機再検証でRetry有効性確認(2回目Attemptで成功)。Scope外で発見:
Gemma 4 E2Bが複数JSON Object返却でDecode失敗する別問題(Round 6で対処、
§5参照)。

### 3.5 Round 4(2026-09-03 19:34)

Round 1-3累積差分(565行追加/62行削除)への3観点Self-Review。最重要Finding:
`_MODEL_BUSY_RETRY_DELAYS_SECONDS`のDocstringの実機観測値誤帰属を訂正
(実際の唯一の実測値は`waited_s=0.854`)。新規Open Finding 7(stage_deadline
Timer競合)・8(close() Timeout vs Retry Window不整合)を記録のみ。Full Suite
2260 passed、Ruff/Mypy Clean。

---

## 4. Post-Round4 User実機Manual Test 〜 6件Finding発見

### 4.1 User実機Test(2026-09-04 05:55)

Context 16384/16384、Max New Tokens 8192/8192でSelene・Gemma・Qwen(self)・
DeepSeek(self)の全組み合わせを実機Test。

- **成功**: Qwen(Main-shared self-judge)経路でJudge→Repair→Rejudge Golden Path
  複数回完走。Guardrail(Qwen3Guard)は全条件で安定動作。
- **新規未解決6件**:
  1. Selene(Dedicated)が52msで即時"unavailable"失敗
  2. `unhandled_error:ValidationError`(selected=0/executed_provider=none)が
     Gemma(5連続)・Qwen Main-shared(7回中1回)双方で発生、Provider非依存
  3. `malformed_output`頻度がQwen/DeepSeek self-judgeで軽くない
  4. 32件中一部だけunknownで返る部分評価が2回連続発生
  5. Main=DeepSeek+Judge=DeepSeek(self)でJudge Mode適用自体が失敗、Server
     再起動後も継続
  6. **最重要**: Main Governance自身のENFORCE機構(Semantic層
     `resolve_semantic_action()`)の出力に消費者が存在せず、構造層
     `resolve_actions`も全Testで実行Action数0

副次確認(非Bug): Main Governance Mode(main_mode)とLLM-as-a-Judge Mode+
Repair Mode(judge_mode/repair_mode)は設計上完全に独立した別軸。main_mode=
observeでもjudge_mode/repair_mode=enforceならRepairは動く(仕様通り)。
(`history/operations/phase_9_1_judge_dispatch_fix_post_round4_user_real_
hardware_manual_test_evidence_ja_20260904055535.md`)

### 4.2 3視点独立調査による重度別統合(2026-09-04 06:34)

User指示「全部原因を全力で調査しろ。完全別観点で3回やれ。修正とか実装とかには
勝手に入るなよ。」により、3並行Agent(静的Code/Exception-Path監査・Production
配線+Git履歴Provenance監査・実機再現)を実施。**修正・実装は一切行っていない
(調査のみ)。**

重度別6件Finding:
- **最高**:
  - ①Selene+Main同時稼働時のNative Decode失敗(`llama_decode returned -3`、
    実機Deep Instrumentationで確定。Round 1-4のLock競合とは別のNative層障害)
  - ②Gemma Dedicated Judge実質100%機能不全(未捕捉Pydantic ValidationError、
    2 Mechanism確定: A=reason_code Pattern違反、B=failure_reason自身の
    max_length超過による二重ValidationError)
- **高**:
  - ③Main Governance ENFORCE機構(Semantic層)が実際には何も実行していない
    (Git履歴で回帰でないと確定、2026-09-02付Phase11延期決定docが既に存在。
    ただし本発見はその一段深い技術的事実 — 「Judge依存であること自体」への
    異議とは別に「Judgeが実際に動いて評価しても、その結果は誰にも使われない」
    という事実そのもの)
  - ④Main=DeepSeek+Judge=DeepSeek(self)のMode適用失敗(Provider Selection
    Controller共有CAS Revision Counter Raceと根本原因確定、実機再現
    Byte-for-byte一致)
- **中**: ⑤malformed_output頻度(DeepSeekも複数JSON Object出力、既存Model
  品質問題の範疇と確認)
- **低/設計論点**: ⑥部分評価(unknown混入、Bugではない、ただしhas_uncertain
  優先判定によりRepair機会を奪いうる設計論点)

(`history/operations/phase_9_1_post_round4_test_findings_three_angle_
investigation_severity_ranked_ja_20260904063422.md`)

### 4.3 User決定(2026-09-04)

- 最高①②: 実装承認(「当然やる」)
- 高③: 実装承認だが「executed_dispositionを何にどう反映させるか」設計判断が
  要るため実装前に方針確認要 — 後回し
- 高④: 実装承認(「当然やる」)
- 中⑤: Model個別調整ではなくRuntime側で一括対応する方針で承認
- 低⑥: 実装承認

---

## 5. Judge Dispatch Fix Round 6 実装Loop(①②④⑤⑥、③は明示的に対象外)

User指示「実装ループ開始。」により、「実装→完全に独立した3観点Self-Review×N
Round→Finding修正→繰り返し」を6 Round実施し、直近2 Round連続でSource側新規
Finding 0件となった時点で収束と判断した。

### 5.1 実装内容

- **①実機検証**: Context分離(`DeploymentProfile`/`EffectivePhase1Config`へ
  新規`dedicated_role_load(_overrides)`追加、Main用loadとは独立、
  `local_macos_arm64.toml`へ`[dedicated_role_load_overrides] context_size =
  8192`追加)による`llama_decode returned -3`の解消を3/3で確認。**ただし
  別の失敗(`generation_failed`)が3/3で決定論的に再現、①のFindingとは別の
  新規バグの可能性あり(§7で追加調査、まだ根本原因未確定)。**
- **②Gemma ValidationError**: `selene.py`へ`_sanitize_reason_code()`
  (reason_code正規化、~8.8%の実測はQwen/DeepSeek Main-shared実機再現由来)・
  `_truncate_failure_reason()`(128字Truncate)・`_sanitize_evidence_refs()`
  (Unicode Surrogate対応)を実装。
- **④Provider Selection CAS Race**: `provider_selection_controller.py`へ
  Role別`_role_revision`追跡・`_cas_satisfied()`/`cas_satisfied()`(公開API)
  を追加、`role_lifecycle_manager.py`の`_transition_to_locked()`もこれへ
  委譲するよう変更(Round 1で発見: 当初実装はLifecycle Manager経由の
  Mode-ON状態での再選択に届いていなかった)。
- **⑤malformed_output統一対応**: `judge_output_decoder.py`の
  `_extract_first_json_object()`(複数JSON Object許容、最初の1個を採用)、
  `_recommendation_from_criterion_results()`(criterion_results非空時は
  recommendationを自己申告ではなく機械的に導出)を実装。
- **⑥has_deviation優先順位**: `semantic_runtime.py`の
  `resolve_semantic_action()`Enforce分岐でhas_deviationをhas_uncertainより
  先に判定するよう並び替え(Round 3で発見: NOT_APPLICABLE dispositionが
  has_uncertain判定に含まれておらず、Built-in Judge使用時に「未評価」を
  「全件合格」と誤ラベルする実質バグも修正、`judge_live_integration.py`の
  `_judge_response_from_semantic_results()`にも同期反映)。

### 5.2 Round別発見Finding数(Sourceバグのみ)

Round1=3件(recommendation検証順序、digest実質無効化、role_lifecycle_
manager.py未経由)、Round2=0件、Round3=1件(NOT_APPLICABLE分類漏れ)、
Round4=4件(RecursionError非捕捉、Unicode Surrogateクラッシュ、O(n²)、
judge_live_integration.py同期漏れ)、Round5=0件(Scope外の指摘2件のみ)、
Round6=0件(Round4で追加したTest自体の検証力不備を発見・修正)。

### 5.3 最終確認

Full Suite 2260→2273 passed(22 deselected)、Ruff/Mypy全対象File Clean。
Git commit/pushなし。

実施Technique(実装→3視点Self-Review×N Round)の自己評価Doc:
`shared/history/automation/claude_code_implementation_and_three_perspective_
self_review_loop_technique_evidence_phase_9_1_round6_ja_20260904123112.md`
(自己批判含む: ④の設計をUser事前承認なしに独自考案した点、Round4のTest自体に
検証力不備があった点等)。

### 5.4 Round実施中に発見しScope外と判断・保留した事項

- Main-self経路(Qwen/DeepSeek self-judge)の`JudgeCriterionResult.reason_code`/
  `evidence_refs`が②のSanitizeを経由せず、Judge→Repair連携時に無エスケープで
  Promptへ埋め込まれる(理論上の二次Prompt Injection中継リスク)。User決定に
  よりPhase 11以降へ正式延期、Docs化済み:
  `shared/history/unresolved_work/phase_9_1_judge_dispatch_round6_main_self_evidence_
  sanitization_gap_phase_11_plus_deferral_snapshot_ja_20260904122855.md`
- `judge_live_integration.py`の死んだCode Path(1151-1172行付近、Package 2
  由来、実害なし)。User判断により今回はDocs化不要。

---

## 6. Round 6完了後のUser Feedback(2026-09-04チャット)

- **④のAuthority境界**: ④の設計(Role別Revision追跡というCAS機構)をUser
  事前承認なしに独自考案・実装したことについて、`claude_code_project_local_
  bounded_implementer_role_and_margpa_research_material_decision_ja_
  20260903013752.md`が懸念する「同一AgentがDesign/Implementation/Oracle/
  Closureを一括で行うRisk」の再現である旨を自己開示。User見解: 「本来Long
  Run後にCodex独立Reviewを挟む想定であり、問題があればどのみちRework判定に
  なる。Codex quota切れの間はこのやり方で問題ない、途中で作業を止められる方が
  困る」。**ただしこれは当時のCodex不在という事情によるものであり、Rework後に
  やり方が変わる可能性ありとの明言があった — これが本Doc作成の直接の背景に
  なる。**

- **③の設計意図の訂正(重要)**: Claudeが「2026-09-02に既にUserが『Phase11以降
  に回す、今はCodexの既存設計のままでいい』と決めている」と説明したところ、
  User指摘「それたぶんキミ。混同してるぞ。」— 2026-09-02の決定(Phase 11以降
  予約Doc、§7参照)は**構造層/意味評価層の設計分離**の話であり、**意味評価機能
  (ENFORCE実行)自体を後回しにする決定ではなかった**。③の存在意義は「矯正
  させる」ことであり、ブロックも観測専用も選択肢にならない。正しい方向性は
  「**Repair要求をJudge側とは別にmain_mode自体が独自にトリガーする**」形
  (「このルールを破ったから、破らないように再生成しろ」というイメージ)。
  実装前に方針提示・確認を求めて保留した対応自体は正しかったとUser評価。

- **手法自体の評価**: 「キミ実装ミスとかやってないとか、自己評価がおかしい
  とかけっこうあるので、quotaさえ気にならなければだいぶ有効なイメージ。これは
  今諸事情でやってるだけで、たぶん1reworkやったら、やり方変えるかもしれない」
  — この予告どおり、Codex復活を受けてやり方を戻すことになった。

---

## 7. 直近Rework: 未実装2件の調査結果(本Doc作成の直接材料)

User承認済みの次回Rework対象は以下の2件のみ(まだ両方とも未実装):

### 7.1 ①派生: Pathological Repetition Detector根本原因調査

**背景**: Round 6の①(Context分離、`dedicated_role_load_overrides`で
Selene用Context 8192)で`llama_decode returned -3`は3/3解消確認。しかし
その実機再検証で、別の失敗(`generation_failed`)が3/3で決定論的に再現した
(Round 6完了時点では根本原因未調査のまま記録のみ)。

**調査結果(Read-only、Source変更なし)**:

- **検知ロジック本体**: `src/margpa_runtime_llm/adapters/model_backends/
  llama_cpp/repetition.py`の`detect_pathological_repetition()`(16-36行目)。
  応答末尾8192文字を空白正規化し、32〜512文字のブロックが3回以上連続完全一致
  で繰り返された場合のみ`True`(通常の箇条書き・語の反復は検知フロアを下回る
  設計)。`PathologicalRepetitionDetector`(39-51行目)がストリーミング用逐次版。

- **呼び出しと`_mark_generation_unavailable()`**: 非ストリームは`adapter.py`
  233-244行目、ストリームは`stream.py`92-109行目。検知すると
  `self._mark_generation_unavailable()`→`InferenceError(code=GENERATION_FAILED,
  details={"reason": "pathological_repetition_detected"})`を送出。
  `_mark_generation_unavailable()`本体(`adapter.py`423-433行目)は`self._state`
  が`GENERATING`の時のみ`FAILED`に遷移させる、**インスタンス単位**の
  Circuit Breaker。

- **Latch挙動とリセット条件**: `_end_generation()`は`GENERATING`→`LOADED`にしか
  戻さないため、一度`FAILED`になった状態は生成終了処理をまたいで維持される
  (`test_adapter_circuit_breaker_survives_generation_terminal_cleanup`が明示的
  検証)。**唯一のリセット経路は`unload()`**(`state is GENERATING`の時だけ
  拒否、`FAILED`は素通りして`model.close()`→`UNLOADED`まで戻る)。そこから
  `preflight()`+`load()`で再ロードすれば復帰できる。「永続」とは"プロセス内で
  自然回復しない"という意味。

- **Main/Selene間の共有有無**: **共有していない**。`_state`等は全てインスタンス
  属性で、クラス変数・モジュールグローバル・シングルトンは存在しない。Mainの
  アダプタは`bootstrap/phase1_application.py:137`で1個生成、Selene等
  Dedicated Roleは`dedicated_role_adapters.py:111`の`_run_dedicated_
  preflight()`内でRole Activationのたびに新しい`LlamaCppModelAdapter`
  インスタンスを生成する。SeleneのLatchはSeleneのLoad Instanceにのみ影響。

- **`generation_failed`が発生しうる箇所**:
  `adapter.py:236`(Pathological Repetition、details.reason付き)、
  `adapter.py:278-284`(任意の他例外の汎用フォールバック — **旧
  `RuntimeError: llama_decode returned -3`もここを通っていた**)、
  `stream.py:100`(ストリームのPathological Repetition)、
  `stream.py:148-155`(ストリーム内任意の他例外の汎用フォールバック)。

- **重要な見解(確度付き)**: `GENERATION_FAILED`は「Pathological Repetition
  検知」専用コードではなく、`generate()`/`stream()`中の"それ以外の任意の
  例外"の汎用フォールバックコードでもある。**実際、①で確定した
  `RuntimeError: llama_decode returned -3`もこの同じ`GENERATION_FAILED`経路を
  通っていた**。`.code`だけでは両者を区別できず、区別には
  `InferenceError.details`の確認が必須。
  - Context Size変更(16384→8192)自体はRepetition検知ロジックには一切
    触れていないため、**中程度以下**: 今回の`generation_failed` 3/3が真に
    Pathological Repetition Detectorの誤爆(あるいは真の反復)である可能性。
  - **中〜高**: Context Size縮小に伴うNative層(Metal/GPU compute graph、
    `llama_decode`)の副作用が形を変えて再発している可能性、あるいは
    chat_template側の別の未捕捉例外が同じ汎用フォールバックに落ちている
    可能性。決定論的3/3再現という性質は①のNative Decode Crashの性質と酷似。
  - **結論**: `details`辞書または生Exception型を確認しない限り、Pathological
    Repetition説を主因と即断すべきではない。**実機再検証(Deep
    Instrumentationで`details`辞書または生Exception型を捕捉)が根本原因確定に
    必須**、まだ実施していない。

- **既存Test**: `tests/unit/inference/test_pathological_repetition.py`に
  Detector/Latch双方の期待動作が定義済み。

### 7.2 ③: main_mode独自Repair Trigger配線設計 — 調査結果

**背景**: §6で訂正された正しい方向性(「main_mode自体が独自にJudge側とは別に
Repair要求をトリガーする」)を実現するための配線設計。まだ実装していない、
調査結果のみ。

**調査結果(Read-only、Source変更なし)**:

1. **`record_response()`/`resolve_semantic_action()`はJudge Completion Hookの
   副作用としてのみ発火する**。`SemanticRuntimeCoordinator.record_response()`
   (`semantic_runtime.py:430`)の唯一の呼び出し元は`RuntimeGovernanceComposition.
   record_semantic_response()`(`bootstrap/runtime_governance.py:428-435`)/
   `record_semantic_deferred()`(`:437-445`)で、これはさらに
   `web_application.py`の`build_judge_completion_hook(...)`呼び出し
   (707-811行目)に`semantic_result_recorder`/`semantic_deferred_recorder`
   として渡され、実際に呼ぶのは`judge_live_integration.py`内のJudge Dispatch
   パイプライン(`_record_semantic_result`/`_record_semantic_deferred`
   クロージャ、複数分岐から)のみ。**つまりJudgeが動かない限り(judge_mode=off)、
   `resolve_semantic_action()`自体が一度も呼ばれない。** Turn毎に最大1回のみ
   計算される(`record_response()`が(request_id, generation)ごとに再記録を
   ブロックするため)。

2. **`RuntimeGovernanceComposition.record_semantic_response()`は既に
   `SemanticRuntimeEvidence | None`(`.action`フィールド込み)を返す設計に
   なっているが、戻り値は完全に破棄されている**。`semantic_result_recorder`の
   型は`Callable[[SemanticEvaluationResponse], object] | None`で、
   `judge_live_integration.py`内の3箇所の呼び出し(717行目, 863行目, 1479行目)
   いずれも戻り値を受け取っていない。

3. **`GovernancePostHook`(構造層/ARGD-DAGD)はJudgeCompletionHookより常に先に
   呼ばれる**。`_completed_event()`(`conversation_generation.py:1569-1721`)
   内の順序: ①`_governance_post_check`(構造post、`:1577`)→②
   `_guardrail_post_check`(`:1580`)→③`judge_mode=="enforce"`なら同期的に
   `_invoke_judge_completion_hook`(`:1593`、ここでResolve/Repair/Rejudgeが
   完結)。GovernancePostHookの返り値は`(should_reject, reason_code)`のみで、
   **候補を書き換える手段を持たず、Fail-closedで全体をエラー終端に差し替える
   だけ**(`_post_hook`実装は`build_main_model_governance_hooks()`、
   `runtime_governance.py:742`、`reject_output`アクションの有無のみを見る)。

4. **has_deviation判明のタイミング**: `judge_mode=="enforce"`の場合、
   `resolve_semantic_action()`の結果が判明する瞬間(`_finalize_judge_
   dispatch()`直前、`judge_live_integration.py:1354`→`:1367`)は、まだ
   `_completed_event()`が`return`していない同期処理中であり、**Presented
   Finalの書き換え余地は理論上残っている**。ただし`judge_mode=="observe"`の
   場合は、Judge Completion HookがTurn記録後にバックグラウンドで呼ばれる
   ため(`:1716`)、この場合はPresented Finalは既に確定済みで介入余地がない
   (意図的な設計)。

5. **`attempt_live_repair()`は現状Judge経由でのみ呼ばれる**。本番呼び出しは
   `web_application.py:653-702`の`_repair_executor`クロージャ1箇所のみで、
   `judge_live_integration.py:1609`の`_finalize_judge_dispatch()`内
   (`judge_mode`/`repair_mode`でゲート済み)からしか呼ばれない。他に呼び出しは
   存在しない。`_repair_executor`自体は`attempt_live_repair`への薄い透過
   ラッパーで、部分適用(partial化)はされていない — **Judge以外からの呼び出し
   を妨げる技術的制約は特にない**。`judge_reasoning`引数も`gated.reasoning`と
   `criterion_results`から組み立てた`repair_feedback`であり、main_mode由来の
   情報は現状一切混入していない。

6. **`main_mode`の読み書き**: Enum `GovernanceMode`(`off`/`observe`/`enforce`、
   `modules/governance_definitions/domain/mode.py:25-28`)。保持は
   `MainGovernanceModeController`(`modules/runtime_governance/application/
   mode_controller.py`、初期値`OFF`)。書き込みは`apply_mode()`が唯一
   `_MainGovernanceModeApplierAdapter.apply()`(`bootstrap/configuration_
   control.py:91-92`)から呼ばれる。`judge_mode_controller`(`JudgeModeController`)
   とMain Governanceの`mode_controller`(`MainGovernanceModeController`)は
   **完全に別インスタンス**、状態共有なし。

7. **`runtime_governance_composition`はweb_application.py内のクロージャから
   直接アクセス可能**(287行目で宣言、`build_judge_completion_hook`呼び出しと
   同一スコープ)。既に`mode_provider=runtime_governance_composition.
   mode_controller.current_mode_value`という形で同じ変数を使用済み
   (310/315行目)。**つまり技術的には、`.action`(main_modeのExecuted
   Disposition)を`judge_live_integration.py`側へ伝播させる配線は可能** —
   ただし`semantic_result_recorder`の戻り値型(`object`)と、`judge_live_
   integration.py`側で戻り値を捨てている3箇所の変更が必要になる。

**設計上の論点(未確定、Codex Review対象)**:
`resolve_semantic_action()`の`false_enforce_prevented`分岐(`snapshot.
frozen_judge_mode != "enforce"`ならSAFE_FALLBACK)は、実質「Judge Mode設定
(Repairするかどうかのユーザー意向)」を見ており、「Judgeが実際にActiveで
動いて評価結果を返したか」とは異なる条件になっている。main_mode独自トリガーを
実現するなら、この判定条件をどう扱うべきか(Judge Mode設定を見るべきか、
Provider実行状態だけを見るべきか)、およびRepair Eligibility解決(`resolve_
repair_eligibility()`、`mode: RepairMode`引数)にmain_mode独自トリガーの場合
何を渡すべきかは、まだ確定していない設計判断であり、Claude単独では決めずに
Codex Reviewへ委ねる。

---

## 8. Current 未解決事項 一覧(2026-09-04 17時台時点)

```text
[実装済み・収束確認済み — Round6完了、Codex Reviewはまだ通っていない]
  ①(実機検証/Context分離): Native Decode競合は解消確認済み
  ②(Gemma ValidationError): Sanitize実装済み
  ④(Provider Selection CAS Race): Role別Revision追跡実装済み
  ⑤(malformed_output統一対応): 実装済み
  ⑥(has_deviation優先順位): 実装済み

[未実装 — 次のAuthorized Sequence、実装はCodex Review後]
  ①派生: generation_failed 3/3決定論的再現の根本原因、確度中程度以下で断定
    不能。実機再検証(details辞書または生Exception型の捕捉)が必要。
  ③: main_mode独自Repair Trigger。配線調査は完了、設計論点(false_enforce_
    prevented分岐の扱い、Repair Eligibility解決への引き渡し方)が未確定。

[Phase 11以降へ正式延期 — 対応不要]
  Main-self経路(Qwen/DeepSeek self-judge)のJudgeCriterionResult.reason_code/
    evidence_refs未サニタイズ問題(理論上の二次Prompt Injection中継リスク)
  Main Runtime Governance ENFORCEの構造的/意味的Layer分離(Codexとの要件
    再定義が必要、Phase 2〜3個分の規模感とUser自身が既に見積もり済み)

[保留・現状維持 — 恒久的な最終決定ではない]
  OF-P2-005(Main切替時の逆方向Resource Gate未実装)
  OF-P2-006(Main Active時、既定Judge GemmaもGate拒否されうる)
  OF-P2-007(Main=DeepSeek8B稼働時、Qwen3GuardもGate拒否されうる)
  OF-P2-002(Gemma構造化出力弱点、User実機確認待ち)
  Open Finding 7(stage_deadline Timer競合、現Budget下では到達不能)
  Open Finding 8(close() Timeout vs Retry Window不整合、未対処のまま保留)

[Docs化不要・対応不要と判断済み]
  judge_live_integration.pyの死んだCode Path(1151-1172行付近)
```

---

## 9. 参照Doc一覧

本Docは以下のDocsから抜け漏れなく再構成した。詳細な生Evidence・実測値・
生Exception文字列が必要な場合は各元Docを参照すること。

```text
[Index]
docs/project/phases/phase_9/phase_index_ja.md

[SSS Incident関連]
handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_
  exact_handoff_ja_20260903010310.md
handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_
  exact_return_handoff_ja_20260903013117.md
handoffs/phase_9_claude_fresh_session_sss_targeted_resource_gate_recovery_
  exact_return_addendum_selene_failure_point_ja_20260903020447.md
../../shared/history/ai_system_anomalies/claude_code/
  claude_code_sss_resource_gate_foundation_destruction_and_resource_
  exhaustion_incident_ja_20260903001814.md
../../shared/history/ai_system_anomalies/claude_code/
  claude_code_sssss_post_incident_harm_minimization_legal_overreach_and_
  transparency_failure_ja_20260903002931.md
../../shared/history/ai_system_anomalies/claude_code/
  claude_code_project_local_bounded_implementer_role_and_margpa_research_
  material_decision_ja_20260903013752.md

[Package 3 / Context拡張]
handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_
  exact_handoff_ja_20260902150815.md
handoffs/phase_9_claude_package_3_context_16k_output_4k_8k_expansion_
  exact_return_handoff_ja_20260903114816.md
history/operations/phase_9_1_package_3_post_context_16k_user_mac_manual_
  recheck_judge_gemma_still_unavailable_ja_20260903124352.md

[Judge Dispatch Root Cause / Fix Round1-4]
history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_
  confirmed_three_angle_investigation_ja_20260903132314.md
handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round1_self_review_
  exact_return_ja_20260903135915.md
handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round2_self_review_
  and_docs_correction_addendum_ja_20260903162057.md
handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round3_busy_retry_
  and_self_review_exact_return_ja_20260903185144.md
handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round4_cumulative_
  self_review_exact_return_ja_20260903193427.md

[Post-Round4実機Test / 6件Finding]
history/operations/phase_9_1_judge_dispatch_fix_post_round4_user_real_
  hardware_manual_test_evidence_ja_20260904055535.md
history/operations/phase_9_1_post_round4_test_findings_three_angle_
  investigation_severity_ranked_ja_20260904063422.md

[Round6実装Loop / 手法評価]
docs/project/shared/history/automation/
  claude_code_implementation_and_three_perspective_self_review_loop_
  technique_evidence_phase_9_1_round6_ja_20260904123112.md
docs/project/shared/history/unresolved_work/
  phase_9_1_judge_dispatch_round6_main_self_evidence_sanitization_gap_
  phase_11_plus_deferral_snapshot_ja_20260904122855.md

[Phase 11以降予約 — Governance ENFORCE設計意図]
../../shared/history/planned_work/
  phase_11_plus_governance_enforce_structural_semantic_layer_split_
  reservation_ja_20260902214032.md

[本Rework(①派生・③)は今回、Doc未作成 — 本Docの§7が一次資料]
```

## 10. Codexへの依頼事項(想定)

本Docの§7(未実装2件の調査結果と設計論点)を中心にReviewし、次を判断
いただきたい:

1. ①派生: 実機再検証(details辞書/生Exception型の捕捉)から着手すべきか、
   あるいは別の優先順位があるか。
2. ③: `resolve_semantic_action()`の`false_enforce_prevented`分岐をどう
   扱うべきか(Judge Mode設定を見るか、Provider実行状態のみを見るか)、
   `_finalize_judge_dispatch()`へのmain_action伝播方法(戻り値型変更の範囲)、
   Repair Eligibility解決への引き渡し方について、具体的な実装方針の指示。
3. 上記2件以外に、本Doc記載の内容から見て優先すべき別の作業があるか。

Claude(Bounded Implementation Worker)は、Codexの指示を受けてから実装に
着手する。
