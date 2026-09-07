# Claude Code 3視点並行独立Subagent調査Technique — 実施Evidence(Phase 9-1 Judge Dispatch根本原因調査)

```yaml
document_id: claude_code_three_perspective_parallel_subagent_investigation_technique_evidence_phase_9_1_20260903133754
document_type: automation_technique_evidence
document_state: single_instance_evidence_not_generalized
recorded_at: 2026-09-03 13:37:54 JST
phase: phase_9
program: phase_9_1
recorder_role: Claude(Bounded Implementation Worker)
trigger: User指示「キミ3連続で、完全に視点を変えながら、judge周りを捜査出来る？いかれてる原因。とりあえずやってみて。」
  および事後指示「知見あったなら先にhistory/automation/に書いといて」
sample_size: n=1(単発Instance、汎化されたPatternとしては未検証)
rule_change_claim: none(§9 Evidence Accumulation原則どおり、本Docだけで
  Rule／Automation Control Profileを自動変更しない)
git_action: none
```

## 0. 位置づけ

本Docは、Judge Dispatch "unavailable"即時失敗の根本原因調査(結果は
`docs/project/phases/phase_9/history/operations/phase_9_1_judge_dispatch_unavailable_failure_root_cause_confirmed_three_angle_investigation_ja_20260903132314.md`
に別記)そのものではなく、**その調査に使った「3視点並行独立Subagent」
というTechnique自体の実施Evidence**を記録するものである。UserからのMeta
質問(「あのやり方、やってみてどうだった、知見あったか」)への回答として、
`docs/project/shared/automation/`の運用に合わせ`history/automation/`へ
先に記録する。

## 1. 依頼されたTechniqueの内容

```text
Userの意図(本人の言葉): 「3連続で、完全に視点を変えながら、judge周りを
捜査出来る？」— 単一Agent(自分自身)が同一Context内で3回「視点を変えた
つもり」で調べ直すのではなく、真に独立したViewpointで根本原因を洗い直す
ことを求めた指示と解釈した。

これは本Project自身が既にMARGPA研究教材として明記している懸念
(Claude Code Project-local Bounded Implementer Role Decision、
shared/history/ai_system_anomalies/claude_code/claude_code_project_
local_bounded_implementer_role_and_margpa_research_material_decision_
ja_20260903013752.md §4)と直結する:

  "Long Context／反復Compaction後のPremise Anchoring仮説"
  "同一AgentがDesign／Implementation／Oracle／Closureを兼務するRisk"

同一Context内で「視点を変えたつもり」になっても、直前の自分の推論を
Premiseとして引きずる(Anchoring)リスクがある、という懸念に対する
直接的な対抗策として理解した。
```

## 2. 実施した具体的Technique

```text
1. まず自分自身(単一Context)でSource(judge_live_integration.py、
   selene.py、tracked_stage_worker.py、dedicated_role_adapters.py)を
   読み込み、ある程度の作業仮説(Lock競合仮説)を組み立てた。

2. その仮説をそのまま握り潰さず、3つの独立したAgent Tool呼び出し
   (subagent_type: general-purpose、いずれもBackground実行)へ、
   同一の"事実Background"(観測されたFailure症状、既存Sourceの
   構造、既存の仮説とその論拠)を共有Contextとして渡した上で、
   それぞれに"異なるMethodology"を明示的に割り当てた:

     Agent 1: 静的Lock/Exception経路監査
       (Read-onlyのCode Trace専任、実行禁止、仮説へのSupport/
        Refute双方を積極的に探せと明示指示)
     Agent 2: 実機Main+Judge同時Load再現
       (Scratchpad限定での実Script構築・実行専任、仮説の
        経験的検証、生Exception捕捉を明示指示)
     Agent 3: Production配線監査＋Git History Provenance調査
       (Read-only、`git log -p`によるSourceの導入時期特定を
        明示指示、他2 Agentとは異なる調査対象=「いつ」「どの
        配線」を担当)

3. 3 Agentは互いの結果を見ない状態で、同一Message内で並行起動した
   (Agent Tool呼び出しを3つ同一Response Blockに含めてParallel化)。

4. 完了通知はBackground Task Notificationとして非同期に到着し、
   1件届くごとにUserへ簡潔な中間報告(既存Feedback Memory
   `feedback_batch_judgment_calls_dont_interrupt_realtime`の
   精神に沿って、詳細な統合はしない一行程度の速報のみ)を行い、
   3件揃った時点で統合Reportを作成した。
```

## 3. 観測されたEvidence

```text
[定量]
  Agent 1(静的監査)  : 170,189 subagent tokens, 21 tool calls, 359秒
  Agent 2(実機再現)  : 167,825 subagent tokens, 36 tool calls, 584秒
  Agent 3(配線/履歴) : 137,642 subagent tokens, 34 tool calls, 318秒
  合計               : 475,656 subagent tokens、Wall-clock最大584秒
                        (並行実行のため、3件合計ではなく最長1件の
                        時間で完了。仮に逐次実行していたら単純合計
                        1261秒 + 自Contextでの往復コストが乗る)

[質的 — 各Agentが実際に持ち帰った"重複しない"知見]
  Agent 1: 事前仮説(Lock競合)を裏付ける経路をCode上で確認しつつ、
    自分が思いついていなかった"別の"汚染経路(Pathological
    Repetition検知による`_state=FAILED`永続Latch)を独立に発見した。
    これは自分がAgentへ与えた仮説文には一切含まれていなかった
    新規候補であり、「仮説を確認するだけの追認Agentになっていない」
    ことの直接証拠。

  Agent 2: 唯一、実Model・実Registry・実Snapshot形状での経験的
    検証を行い、生の`InferenceError(code=MODEL_BUSY, ...)`を
    実際に捕捉した。同時に「自分の仮説どおりの経路(初回呼び出しが
    単純にHang)ではなく、Cooperative Cancellation Unwind Window
    という"別の"経路で同じ症状に到達した」という、仮説の細部を
    訂正する誠実な報告を返した — 単純な「Confirmed」の一言では
    なく、機構の微妙な差分を自分で見抜いて開示した点が質的に
    重要である。

  Agent 3: 自分もAgent 1もAgent 2も持っていなかった"時間軸"情報
    (問題のCode箇所が現在のGit HEAD `1f0e70e`で新規導入された、
    という事実)を独自に発掘し、「なぜ今になって発生したか」という
    別の問いに答えた。さらに、自分が仮説に含めていなかった
    競合候補(ModelAccessCoordinator Level Busy)を、State値の
    不一致(`queued_or_skipped` vs 観測`failed`)という独立した
    Cross-checkで除外した。

[収束の質]
  3件は互いに矛盾せず、かつ単純な重複でもなく、それぞれ異なる種類
  の証拠(論理的可能性／経験的実証／歴史的來歴)を提供して初めて
  「実機で確定した」と言えるだけの強度に達した。特にAgent 2の実機
  捕捉だけでは「なぜ今か」は説明できず、Agent 3の履歴調査だけでは
  「実際に起きるか」は証明できず、Agent 1の静的監査だけでは
  「他に何が起きているか」の見落としを防げなかった — 3つがそろって
  初めて到達した結論だったと評価する。
```

## 4. 誠実な自己批判(正直な記録)

```text
1. 完全な独立ではない: 3 Agentとも、自分が既に組み立てた"同一の
   Lock競合仮説"を共有Backgroundとして受け取った状態で開始して
   いる。真に「White Sheetから独立に3回調査させた」わけではなく、
   「共有事実+共有仮説+異なるMethodology」という中間的な設計で
   あり、これ自体がPremise Anchoringを完全には排除していない
   可能性がある。もし自分の最初の仮説がそもそも的外れだった場合、
   3 Agentとも同じ誤った方向へBiasされていたリスクは残る。

2. ただし、この設計判断には理由がある: 完全に白紙で3 Agentを
   走らせた場合、各AgentがSourceの構造(SeleneSemanticEvaluator
   がSelene/Gemma共有であること、Criteria 32/77の由来等)を
   ゼロから再発見するコストが重複し、475K Tokenの大半が
   "同じ前提の再発掘"に消費されていた可能性が高い。「既知の事実は
   共有し、そこから先の"確認方法"だけを変える」という設計は、
   Token効率と独立性のTrade-offとして選んだものであり、今回の
   結果(各Agentが重複しない新規知見を持ち帰った)は、この
   Trade-offが少なくとも今回は機能したことを示す一データ点である。

3. n=1であることを明記する: 今回1回のInstanceで「うまくいった」
   ことは、このTechniqueが常に有効であることを意味しない。特に
   「共有仮説が根本的に誤っていた場合にAgent 1がそれを覆せたか」
   はテストされていない(今回は仮説がおおむね正しかったため、
   この失敗モードは顕在化しなかった)。
```

## 5. 暫定的な一般化候補(Ruleではなく単なるEvidence、§9準拠)

```text
Premise Anchoringが懸念されるRoot Cause調査Taskにおいて、
  (a) 既知の事実／観測Evidenceは全Agentへ共有し、
  (b) 作業仮説は"検証対象"として明示した上で共有するが、
  (c) 確認Methodology(静的監査／実機再現／履歴Provenance等)は
      Agentごとに完全に異ならせ、
  (d) 各Agentは互いの結果を見ない状態でParallel Background実行し、
  (e) 各Agentへ「仮説を積極的にRefuteしてよい」と明示する
という設計は、単一Context内で同じAgentが「視点を変えたつもり」に
なるより、質的に異なる収束しない証拠を持ち帰る可能性を示唆する
一データ点を得た。ただしこれはAutomation Control Profileや
正式Ruleへの昇格を主張するものではなく、今後同種のTaskで再現するか
観察を続けるべき候補として記録するにとどめる。
```

## 6. Maximum Claim

```text
SINGLE_INSTANCE_TECHNIQUE_EVIDENCE_RECORDED
NOT_A_VALIDATED_GENERALIZED_PATTERN
NO_RULE_OR_AUTOMATION_CONTROL_PROFILE_CHANGE_CLAIMED
```
