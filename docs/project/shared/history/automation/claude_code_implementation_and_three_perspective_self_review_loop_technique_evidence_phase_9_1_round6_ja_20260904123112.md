# Claude Code「実装→3視点自己Review×N Round」Loop Technique — 実施Evidenceと自己評価(Phase 9-1 Judge Dispatch Fix Round 6)

```yaml
document_id: claude_code_implementation_and_three_perspective_self_review_loop_technique_evidence_phase_9_1_round6_20260904123112
document_type: automation_technique_evidence
document_state: single_instance_evidence_not_generalized
recorded_at: 2026-09-04 12:31:12 JST
phase: phase_9
program: phase_9_1
recorder_role: Claude(Bounded Implementation Worker)
trigger: User指示「実装ループ開始。」(2026-09-04)。事前に与えられた仕様:
  「一通り実装→完全に観点を変えた自己レビューを3回→Findingや作業やり残しが
  あればまた一通り実装→…を、バグが完全に潰れて、やるべき作業が完全に
  なくなるまで繰り返す」
  事後指示「あと今回のやり方について、shared/history/automation/にこの
  やり方に関してのキミの評価をしっかり目に書いておいてくれ」
related_prior_evidence: claude_code_three_perspective_parallel_subagent_investigation_technique_evidence_phase_9_1_ja_20260903133754.md
  (前日実施の「3視点並行独立Subagent"調査"Technique」の直接の発展形。
  前回は"原因調査"のみにこのTechniqueを使ったが、今回は"実装＋修正"を
  含む、より広いScopeの反復Loopへ拡張した初回Instance)
sample_size: n=1(単発Instance、6 Round分は同一Loop内の反復であり
  独立したSample数としては数えない)
rule_change_claim: none
git_action: none
```

## 0. 位置づけ

本Docは、Judge Dispatch Fix Round 6(Finding ①②④⑤⑥への対応、③は明示的に
対象外)そのものの内容(実装Diff・修正Findingの詳細)ではなく、そこで
使った「実装→完全に独立した3視点Self-Review×N Round、収束するまで反復」
というLoop Technique自体の実施Evidenceと、それに対する自己評価を記録する。

## 1. 実施した具体的Technique

```text
1. User指示「実装ループ開始。」を受け、対象5項目(①実機検証、②Gemma
   ValidationError修正、④Provider Selection CAS Race修正、⑤malformed_
   output Runtime統一対応、⑥has_deviation優先順位)についてSourceを
   実装。

2. 実装完了後、3つの独立したAgent Tool呼び出し(subagent_type:
   general-purpose)を同一Message内でParallel起動し、それぞれに
   完全に異なる観点(切り口)を明示的に割り当てた。他Agentの結果は
   一切見せず、各Agentは独立にSourceとTestを読んで調査した。

3. 3 Agentの結果が揃った時点で統合し、実質的なバグ(Finding)があれば
   Source側で修正、対応するRegression Testを追加、Full Suite/Ruff/Mypy
   で確認。

4. 「Findingが直近2 Round連続でゼロ」になるまで、2の観点を毎回変えながら
   1-3を反復した。

5. 各Roundで実際に使った観点(計18種、重複なし):
   Round 1: 静的Correctness監査 / Test Coverage監査 / 実機・統合監査
   Round 2: 並行性(Thread-Safety)監査 / Docs・コメント正確性監査 /
            実証的シナリオ検証(実際にPythonで動かす)
   Round 3: 境界値/Edge Case網羅性監査 / 既存Docs・Requirements整合性
            監査 / Web API・HTTP層統合検証
   Round 4: 型/入力検証Adversarial監査 / 既存Role・後方互換性監査 /
            全体俯瞰Integration監査
   Round 5: セキュリティ/権限昇格監査 / 既存Busy Retry機構との相互作用
            監査 / Fresh Eyes全体再読(切り口を指定しない自由監査)
   Round 6: 静的Correctness最終監査 / Test Coverage最終監査 /
            実機・統合最終監査(Round1と同じ「型」の観点だが、6 Round
            分の蓄積された最終状態を対象にした通し確認という別の役割)
```

## 2. 観測されたEvidence(定量)

```text
[Round別 Subagent Token消費・Tool呼び出し数・所要時間(並列実行の最長値)]
  Round 1: 469,597 tokens / 76 tool calls / 最長370.5秒
    (静的145,940・Coverage148,865・統合174,792)
  Round 2: 417,556 tokens / 61 tool calls / 最長299.6秒
    (並行性121,280・Docs165,410・実証130,866)
  Round 3: 449,251 tokens / 78 tool calls / 最長326.4秒
    (境界値163,693・整合性153,379・Web API132,179)
  Round 4: 531,858 tokens(うち75,947 tokensはAPI Rate Limitで完全に
    無駄になった1回分の再実行前失敗コスト) / 139 tool calls /
    最長454.2秒(再実行分のみ)
    (型/入力153,660・互換性143,923・俯瞰158,328)
  Round 5: 475,940 tokens / 64 tool calls / 最長485.1秒
    (セキュリティ156,852・Busy Retry120,389・Fresh Eyes198,699)
  Round 6: 544,344 tokens / 118 tool calls / 最長500.7秒
    (静的最終215,663・Coverage最終194,255・統合最終134,426)

  Subagent合計: 約288.9万tokens(6 Round×3 Agent=18回、うち3回は
    Round 4でAPI Rate Limitにより完全失敗し再実行、実質発火回数21回)
  この集計にはメインSession自身(実装Edit、Bash実行、Read、Full Suite
  複数回実行等)のToken消費は含まない — 別途相当量が発生している。

[発見されたFinding数の推移(Sourceコード自体の実質的バグのみ)]
  Round 1: 3件(recommendation検証順序、digest実質無効化、
    role_lifecycle_manager.pyがCAS修正を未経由)
  Round 2: 0件(Docstring精度の誤り4件のみ、Source挙動への実害なし)
  Round 3: 1件(resolve_semantic_action()のhas_uncertain判定に
    NOT_APPLICABLE漏れ — Built-in Judge使用時に「未評価」を
    「全件合格」と誤ラベルする実質バグ)
  Round 4: 4件(RecursionError非捕捉によるJudge/Enforce経路クラッシュ、
    Unicode Surrogate文字によるUnicodeEncodeErrorクラッシュ、
    O(n^2)計算量、judge_live_integration.py側の同種箇所への同期漏れ)
  Round 5: 0件(Scope外の指摘2件のみ — Main-self経路Evidence未サニタイズ
    のセキュリティ論点、既存の既知Open Finding 7の再発見)
  Round 6: 0件(ただし自分がRound 4で追加したTest自体の検証力不備を
    発見・修正 — "{"の単純な繰り返しはJSON構文エラーで即座に停止し、
    RecursionErrorを一切誘発しないという誤りに気づかず書いていた)

  実質的なSourceバグ修正合計: 8件(Round 1〜4のみ)
  収束判定: Round 5・Round 6の2 Round連続でSource側の新規バグ0件と
    なったことをもって収束と判断した。
```

## 3. 誠実な自己批判・質的評価(正直な記録)

```text
1. 「重大なバグを実際に発見できた」ことは事実であり、価値は大きい。
   特にRound 4で見つかった2件(RecursionError非捕捉、Unicode Surrogate
   によるUnicodeEncodeErrorクラッシュ)は、実装時の自分には全く
   想定できていなかった種類の入力(病的に深いネストJSON、対になって
   いないUnicode Surrogate文字)であり、これらは実運用のLocal量子化
   Modelが劣化出力として現実に生成しうる形である。もし今回のLoopを
   1 Roundだけ、あるいは自分一人の目視レビューだけで終えていたら、
   この2件は本番Judge/Enforce経路の未捕捉クラッシュとして残っていた
   可能性が高い。

2. 収穫は単調減少しなかった: Round 2で一度Source Finding 0件になった
   後、Round 3・Round 4で再び本物のバグが見つかった。これは「1回
   Findingがゼロになったら収束」という基準では不十分であることを
   示す実例であり、「2 Round連続でゼロ」という基準(前回のJudge
   Dispatch Fix Round 1-4で確立した基準を踏襲)には根拠があったと
   言える。逆に言えば、"n Round連続ゼロ"の n をいくつに設定すべきかは、
   今回もn=2を機械的に踏襲しただけで、それ自体の妥当性は検証して
   いない。

3. Loop自体が「実装Authority」の境界を越えるRiskを露呈させた: ④
   (Provider Selection CAS Race修正)は、User承認が「当然やる」の
   一言のみで、⑤⑥のような具体的修正方式の事前提示は無かった。
   実装段階で、Role別Revision追跡という新しいCAS機構を自分で設計・
   実装し、Round 3の独立Review(Docs整合性観点)がこれを事後的に
   指摘するまで、この点を自覚していなかった。さらに、その自作の
   CAS設計に対する自分自身のSelf-Review中に見つけた不備(exact-
   revision一致時にdigestを検証せず素通りさせていた)自体が、
   `claude_code_project_local_bounded_implementer_role_and_margpa_
   research_material_decision_ja_20260903013752.md`が既に名指しで
   懸念していた「同一AgentがDesign／Implementation／Oracle／Closure
   を兼務するRisk」をそのまま再現していた。3観点Self-Review Loopは
   Code Correctnessの検出には有効だったが、「そもそもこの設計判断を
   自分が下してよかったのか」というAuthority境界の逸脱は、Loopの
   構造そのものからは自動的に検出されない(たまたまRound 3の一つの
   観点がこれを拾っただけで、意図して設計したCheckではない)。

4. Self-Review自身が新しいミスを持ち込むリスクが実際に顕在化した:
   Round 4で追加したRegression Test(深いネストJSONでRecursionErrorが
   正しく処理されることを検証する意図)は、実際にはRecursionErrorを
   一切誘発しない誤った入力("{"の単純な繰り返しは2文字目で構文
   エラーになり、再帰が積み上がらない)を使っていた。この不備は
   Round 6のTest Coverage監査Agentが「このTestは`except RecursionError`
   分岐を削除してもPASSし続ける」という具体的な実験で発見した。
   これはLoopの価値を裏付ける実例であると同時に、「自分が書いた
   Testが検証したいものを本当に検証しているか」は、実装者自身の
   直感だけでは見抜けなかったという事実でもある。しかも、その場で
   単純に修正した1回目の対処(深さを増やすだけ)も的外れで、実際に
   pytest経由で実行して初めて誤りに気づき、2回目の修正(有効な
   ネスト構造への変更)でようやく解決した — Self-Review後の修正
   自体にも、さらなる検証(実行して確認)が必要だったということ。

5. Resource Costは軽くない: Subagentだけで約289万Token、6 Round×3
   Agentの並列実行でもWall-clockは各Round5〜8分、6 Round合計で
   おおよそ35〜40分程度(並列化の恩恵込みでこの値、逐次実行だったら
   数倍かかっていたはず)。さらにRound 4の最初の3並列AgentはAPI
   Rate Limitで全滅し、再実行が必要だった(Userに一度中断され、
   制限解除後に再開する形になった)。「バグが完全に潰れるまで」を
   文字通り実行すると、この規模のResource消費が前提になる、という
   ことを正直に記録する。

6. 「Scope外」判定の一部は自分の判断であり、事後にUserへ確認する
   運びとなった: Round 5で見つかったMain-self経路のEvidence未
   サニタイズ問題(セキュリティ論点)を、②のScope(Gemma固有の
   ValidationError対策)外と自分で判断して保留したが、これが妥当な
   線引きだったかはUser自身の目線では別の結論もあり得た(実際、
   Userはこれを"直ちに対処"ではなく"Phase 11以降へ正式に延期"という
   形で、改めて意思決定している)。Loop実行中の「これはScope外」
   という自己判断そのものは、Loopの収束条件には数えず、最終報告で
   一括してUserに開示する運用にしたことで、少なくとも隠蔽にはなら
   なかった。
```

## 4. 暫定的な一般化候補(Ruleではなく単なるEvidence)

```text
「実装→独立した3視点Self-Review×N Round、直近2 Round連続Finding 0で
収束」という設計は、少なくとも今回のn=1 Instanceにおいて:
  (a) 単独実装では見逃していた複数の実クラッシュ級バグを実際に検出した
  (b) 収穫は単調減少せず、1 Roundの"ゼロ"だけでは収束と判断できない
      ことを示した(2 Round連続基準には経験的な裏付けが得られた)
  (c) Self-Review Loop自体が新たなミス(検証力のないTest)を持ち込む
      ことがあり、"Self-Reviewが指摘した修正"にもさらなる実行確認が
      要ることを示した
  (d) Code Correctness監査としては機能したが、Authority境界(この
      設計判断を自分が下してよいか)を専任で見張る観点は含まれておらず、
      これは狙って設計されたChecksではなく偶然拾われたものだった

(d)は次に同種のLoopを回す際、観点の一つとして「今回実装した設計判断は
事前にUser/Controllerへ承認を得るべき粒度だったか」を明示的に含める
価値があることを示唆する、という以上の一般化はしない。Rule化・Automation
Control Profileへの反映は主張しない。
```

## 5. Maximum Claim

```text
SINGLE_INSTANCE_TECHNIQUE_EVIDENCE_RECORDED
NOT_A_VALIDATED_GENERALIZED_PATTERN
NO_RULE_OR_AUTOMATION_CONTROL_PROFILE_CHANGE_CLAIMED
AUTHORITY_BOUNDARY_GAP_IN_THIS_LOOP_DESIGN_DISCLOSED_NOT_RESOLVED
```
