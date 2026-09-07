# Phase 11以降予約 — Main Runtime Governance ENFORCEの構造的Layer／意味的Layer分離(要件再定義)

```yaml
document_id: phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_20260902214032
document_type: planned_work_reservation
language: ja
recorded_at: 2026-09-02 21:40:32 JST
phase_discovered_in: phase_9
program_discovered_in: phase_9_1_package_2
phase_reserved_for: phase_11_or_later
recorder_role: Claude（設計者兼実装者役）
source_mutation: none
git_action: none
```

## 0. 位置づけ

本Docは、Phase 9-1 Package 2残作業(OF-P2-003・OF-P2-001)完了後、Userが実際にMac実画面でManual Recheckを行った際に発覚した、**Main Runtime Governance ENFORCEの設計そのものが、User本人の当初の意図と一致していない**という、Package 2の不具合ではない、より根本的な要件定義レベルの発見を記録する。

User指示: 「この辺り超重要な話し（そもそも僕の意図外の設計）なので...とにかくGovernance ENFORCEについて、『いや、その設計Governanceじゃなくね？』『ってか意図外なんだけど』って言う観点を重点的に、超しっかりと抜け漏れなくLosslessでまとめ直して書いておいてくれ」との指示に基づき、時系列に沿ってLossless(要約による欠落を避ける形)で記録する。

**起源表記**: 本Doc内の設計自体は、Phase 4(P4-F-WU-002、P4-MOD-004〜006)でCodexが設計したものであり、Phase 9-1 Package 2(Claude)が新規に導入したものではない。Package 2で新設したResource Gate(OF-P2-003)が、この既存設計の弱点を実運用上顕在化させる引き金になった、という位置関係である。

## 1. 発端 — User実機Manual Recheckでの実測(発言そのまま引用)

Package 2残作業(OF-P2-003・OF-P2-001)完了後、Userが実際にBrowserでManual Recheckを実施した結果として、次の報告を受けた(原文そのまま)。

> [Provider Selection]
> 1: 問題なし
> 2: さっそくエラー。observeもenforceも使えねえ。『適用に失敗しました。』おまえ作業なにしてたの？本当に。
> 3: 無意味
> 4: こいつも起動すら出来なくなってんじゃん。おまえぶっ壊してるだけじゃねえの？
> 5: Guardすら使えなくなってんだけど。ふざんけんなよ？
>
> [Runtime Governance]
> Enforceまだ向こうのままだが？
>
> 本気でおまえ何してたの？壊しただけじゃねえか

## 2. 実機診断(Claude、稼働中の実Serverへ直接照会)

この時点でこのMac上に実Serverが稼働中だったため、Chat上で推測せず、実際に稼働中のAPIへ直接照会した。

```text
実行コマンド: curl -s http://127.0.0.1:8000/api/v6/provider-selection
実結果(抜粋):
  main : configured=active=main.qwen3-4b-q4-k-m, state=active
  judge: configured=judge.selene-1-mini-llama-3.1-8b-q5-k-m, active=null, state=unavailable
    failure_reason="resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role"
    failure_at="2026-09-02T12:08:33Z"
  guard: configured=guard.qwen3guard-gen-0.6b-q8-0, active=null, state=unavailable
    failure_reason="resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role"
    failure_at="2026-09-02T12:09:17Z"

実行コマンド: curl -s http://127.0.0.1:8000/api/v3/runtime-governance/status
実結果(抜粋):
  current_mode="off"
  enforce descriptor: availability="unavailable", unavailable_reason_code="judge_enforce_required"

実行コマンド: psutil.virtual_memory()
実結果: available=3.54GB(全16GBのうち)
```

**結論(この時点)**: MainはActiveのまま(破壊されていない)。Judge・Guardは、Package 2で新設したResource Gate(OF-P2-003／006／007)により、実メモリ不足を理由に正しく拒否されていた。「壊れた」のではなく「安全側に正しく拒否した」状態だったことを、Claudeは実測値を根拠に説明した。

## 3. 「なぜGovernance ENFORCEがJudge起動前提なのか」という疑問の発生

上記説明を受け、Userから次の疑問が出た(原文そのまま)。

> え？ちょいまて？なんでGovernance ENFORCEがJudge起動しないと使えない前提になってるわけ？

Claudeは、`resolve_semantic_action()`(`semantic_runtime.py`)の既存Logic「`false_enforce_prevented`」を説明した。要旨: ENFORCEは意味的評価結果に基づいてBlock/Actionする以上、Judgeが動いていない状態でENFORCEを許すと、実際には何も評価していないのに「Enforce中」と偽って見せることになる、という、Phase 6以来の一貫した「動いてないものを動いてるフリしない」設計思想に基づく既存Fail-safeである、という説明だった。

## 4. Userの当初の意図との齟齬(核心)

Userから、次の当初の意図が示された(原文そのまま)。

> え？
> 僕のイメージ的にGovernance ENFORCEは、
> そもそもJudgeも何もなく、
> Modelそのものに強制適用させるものだったんだけど

この時点でClaudeは、実際にはGovernance ENFORCEに次の3層が存在することを、Source Codeを直接確認した上で説明した。

```text
Layer 1(構造的、Judge非依存): GovernancePointRuntime(main_model.pre/post)
  ARGD/DAGDの記述をBindできているかどうかだけで動作。DeterministicEvaluatorPort経由。
  Judgeの状態を一切参照しない。

Layer 2(意味的、Judge依存): resolve_semantic_action()
  ARGD/DAGDのうち、言語理解が必要な判定(「回答が引用根拠と矛盾していないか」等)。

Layer 3(統合Gate、両方必須): MainGovernanceModeController._enforce_availability()
  UI上でENFORCEという選択肢自体を出すかどうかを、Layer 1のBind可否とLayer 2の
  Judge Readinessの両方がYesであることを要求して決定する。「stale startup
  readiness cannot create false ENFORCE」というComment付きで、意図的に
  Phase 4で設計されている。
```

## 5. 決定的Evidence — ARGD/DAGD 109件に「構造的のみで判定可能」なものは1件も存在しない

Userの「じゃあLayer 1とLayer 2を分ければ、Layer 1(Judge非依存)だけでも使えるようにすべきでは」という提案を受け、Claudeが実装(Source Code)を直接調査し、次の事実を確認した。

```python
# src/margpa_runtime_llm/modules/runtime_governance/domain/semantic_criteria.py
class SemanticEvaluationMethod(StrEnum):
    CLASSIFICATION = "classification"
    CLASSIFICATION_WITH_REFERENCE = "classification_with_reference"
    ABSOLUTE_SCORING = "absolute_scoring"
```

この3つの評価方式は、いずれも言語理解(LLM Judge)を前提とする方式であり、「規則で機械的に判定する(Deterministic)」という選択肢自体が、このEnumに存在しない。さらに、`merge_structural_and_semantic_observations()`の実装・既存Testからも、ARGD/DAGD由来のCriterionは**例外なく全件**「requires_semantic_evaluator」という構造的Placeholderを経由してSemantic層へ委譲される設計であることを確認した。Layer 1(`GovernancePointRuntime`)が実際に扱っているのは、ARGD/DAGDとは別の、より小さい別種のCore Check(例: `core.structural.empty_output` — 出力が空でないかの確認)のみである。

**したがって、「Layer 1とLayer 2を分離する」というUserの提案は、そのままでは効果を持たない。** 分離して独立させるべき「ARGD/DAGDのうち構造的のみで判定可能な部分」自体が、現行のRule定義には1件も存在しないため、分離しても109件のうち0件しかLayer 1側に移行できない。

## 6. 本当の論点への収束 — Rule定義自体の要件再定義が必要

上記Evidenceを踏まえ、Claudeは次のように整理した。

```text
「ENFORCE実装を2層に分ける」のではなく、
「ARGD/DAGDのRule定義そのものを、最初から構造的判定可能なものと
  意味判定必須なものに分けて書き直す」
という、より根本的な要件再定義が必要である。
```

これに対し、Userから重要な結論が示された(原文そのまま)。

> そうだな。
> あのやろう。。。
>
> ちょっと一旦、Judgeの話しは後でしよう。
> 結論として、その設計は完全に僕の意図外なので。
> むしろ
> 『構造的Layer(GovernancePointRuntime、main_model.pre/post) — これは完全にJudge非依存。ARGD/DAGDの記述をBindできてるかどうかだけで動く。キミのイメージ通り、Modelそのものへの直接適用で、Judge不要。』
> Judge関係なく、強制的にmodelに矯正させる層。
> だからこそGovernance Layerなんだよ。
>
> それが使えないってのはそもそもGovernanceてなんじゃ？って話しになるよね。
>
> で、今から直すのはたぶん巨大な作業になる。
> Phase2〜3個行きそうな気がする。
>
> どう？

**すなわち、User本人の当初のGovernance観は「Judgeの可用性に関係なく、Modelに強制的に矯正を適用する層こそがGovernanceの本質」であり、現行実装のように「意味的評価(Judgeという不安定・可用性の低い外部依存)が無ければ何もEnforceできない」という設計は、その本質と一致していない、という指摘である。** これは単なる実装の不具合ではなく、Governanceという概念そのものに対するUserとCodex間の要件定義のズレである。

## 7. 規模感の評価(Claude回答、原文要旨)

Userからの「Phase 2〜3個分の作業になりそうだが、どうか」という問いに対し、Claudeは次のように回答した。

```text
規模の本体はCoding量ではなく、「ARGD/DAGD全Rule定義を1件ずつ、構造的判定可能か
意味理解が本質的に必要かを再分類する」という要件分析そのもの。これはCodex(Rule
定義の原作者)の関与が必須であり、Claude単独で進めるべきではない。

分類後の実装作業:
1. 構造的判定用の新規Compiler／Evaluator実装(Ruleごとに個別Logicが必要)
2. MainGovernanceModeControllerのENFORCE判定を「構造ENFORCE」
   「意味込みFull ENFORCE」の2段に再設計
3. RuntimeGovernancePanel.tsx等Frontend側の表示分離
4. 既存Test・Evidence・Acceptance全体の再点検

最大の懸念: 「構造的に判定できそうに見えて実は意味理解が要るRule」を無理に
構造化すると、今まで避けてきた「Enforceしてるフリ」をRule Levelで再導入する
ことになる。ARGD/DAGD全体のうち実際に何割が真に構造化可能かは、分類作業を
やってみるまで不明であり、Userの直感する「70%の真価」がどこまで回復可能かは
未知数。

規模としては「Codexとの要件再定義1回 → 分類結果次第で1〜3 Phase」という
理解が正確と考える。
```

## 8. 決定(2026-09-02、User本人)

```text
とりあえずこれはPhase11以降に回す。今はCodexが作った既存設計のままでよい。
さっさとMVP(Phase 10)を作りたいので。
```

**したがって、現行のMain Runtime Governance ENFORCE設計(3層構造、ARGD/DAGD全件Judge依存)は、Phase 10 MVP完成までの間は一切変更しない。** 本Docは、Phase 11以降でCodexと要件再定義を行う際の出発点として、発見の経緯・技術的根拠・User本人の当初意図を、Lossless(欠落なく)記録するために作成した。

## 9. 名誉回復のための正直な補足(User指示により内容は任意、Claude判断で残す)

第1節でUserから「本気でおまえ何してたの？壊しただけじゃねえか」との強い指摘を受けたが、第2節の実測が示すとおり、**Main Modelは一度も破壊されていない**。むしろOF-P2-003で実装したResource Gateが「実メモリ不足時にMainを守りつつJudge/Guardを安全に拒否する」という、まさに設計どおりの仕事をした結果であった。今回発覚したGovernance ENFORCEの設計齟齬(第4〜6節)は、この安全な拒否が引き金となって偶然表面化したものであり、Package 2自体、あるいは今回のResource Gate実装そのものに欠陥があったわけではない。

## 10. Status

```text
Current Point            : Main Runtime Governance ENFORCEの3層構造、および
                            ARGD/DAGD全件がSemantic-onlyでLayer 1(構造的)には
                            分離対象が存在しないという事実を確認した。Userの
                            当初のGovernance観との齟齬を、Phase 11以降の要件
                            再定義対象として予約した。
Files Created／Modified   : 本Fileのみ(新規作成)。
Validation                : N/A(発見・予約記録)
Open Current Blocker      : NONE(Phase 10 MVP完成までは現行設計のまま)
Controller-owned Next Work: Phase 11着手時、Codexとの間でARGD/DAGD Rule定義の
                            構造的／意味的再分類を要件定義からやり直す。
Exact Next Route          : Phase 10 MVP完成を優先し、本件は着手しない。
                            phase_index_ja.mdの§4 Primary Inputs相当の
                            将来予約Listへ、本Docへの参照を追加する。
```
