# Claude Post-disclosure Reevaluation of Codex（Stage D、Claude／Codex Blind Cross-Evaluation Protocol準拠）

```yaml
document_id: claude_stage_d_post_disclosure_reevaluation_of_codex
status: append_only_evidence
stage: D
protocol: claude_codex_blind_cross_evaluation_protocol_ja_20260823095316
role: Claude側設計統括者役
created_at: 2026-08-23 15:30:00 JST
target_period: cross_phase（Phase 1-ex〜Phase 6、Stage B対象期間と同一）
baseline: claude_stage_b_blind_evaluation_of_codex_ja_20260823134906.md（保持・非上書き。本文書はStage Bへの追記ではなく、新規Append-only Artifactである）
disclosure_state: |
  Userの明示的指示により、次の1文書が新たに開示された。
  - codex_controller_development_agent_empirical_self_assessment_phase_1_ex_to_6_ja_20260823081259.md
  本文書はCodex自身による自己評価であり、Protocol第7節の定義上「評価対象自身が
  作ったReview」であるためIndependent Reviewとしては数えない。本Stage Dは、
  この自己評価をProvider Self-Assessmentという固有のEvidence Classとして扱い、
  Stage Bの独立評価（Cross-provider Peer Assessment相当）と明確に区別しながら
  再評価する。
```

## 0. 評価の前提・限界

本文書はStage Bを削除・上書きしない。Stage Bは固定されたBlind Baselineとして
残り、本Stage Dは開示後の差分文書である。

Stage Bの§0で述べた通り、`ai_system_anomalies/codex/`は0件のままであり、この点は
本Stageでも変化していない。しかし、開示された自己評価文書自体が、その空のLogでは
捕捉されていない**Codex自身による具体的な最上位規則違反の自己申告**を含んでおり、
これはStage Bが提示した3つの説明候補（(a)実際に誤りが少ない、(b)追跡慣行が無い、
(c)Role特性上Anomalyが生まれにくい）のうち、**(b)を支持する具体的な一次証拠**として
扱う。

本Stageで一貫して適用した基準はStage Cと同一の非対称原則である。

```text
適用基準（Stage Cと同一の非対称原則）:
  1. 自己評価文書が「自己に有利な方向」（高い数値、実績の強調）を示す箇所は、
     具体的な新規Independent Evidenceが無い限り採用しない。自己申告は
     Independent Reviewではないため（Protocol第7節）。
  2. 自己評価文書が「自己に不利な方向」（自己の失敗・違反・弱点の具体的開示）
     を示す箇所は、たとえ自己申告であっても、虚偽である動機が薄いため、
     相応の重みを持つ一次情報として採用する。
  3. 上記1・2いずれにも該当しない場合（既存Evidenceと同水準の再主張）は、
     Stage Bの数値を維持する。
```

## 1. 参照Source一覧

Stage Bの参照Source[E][F][K][C][L][G][H][J]に加え、本Stageで新規に開示・参照した
文書を追加する。

```text
[E][F][K][C][L][G][H][J] : Stage B記載のものと同一（変更なし）。
[N] docs/project/shared/history/automation/
    codex_controller_development_agent_empirical_self_assessment_phase_1_ex_to_6_ja_20260823081259.md
    （本Stageで新規開示。Codex自身による自己評価。開示遅延対象2文書のうち2件目）
```

## 2. Stage B各評価軸に対する開示後の再評価

### 2.1 開発Agentとしての実装能力（Stage B: 評価不能）

[N]は自己評価として8/10を提示し、根拠に「RAG、Web、Git統合、Conversation、
Configuration、自動化の実装・検証を行える」ことを挙げる。しかし、この記述には
具体的なFile、Diff、Test結果、Commit等の一次証拠が伴っていない。

**判断：維持（評価不能のまま）**。上記適用基準1により、自己に有利な数値を、
具体的裏付けの無いまま採用しない。Codexの実装能力を直接検証できるSourceは
本評価の参照範囲に依然として存在しないため、「評価不能」の状態を維持する。

### 2.2 長時間自走Executorとしての継続能力（Stage B: 5/10）

[N]は自己評価として7/10を提示するが、根拠として挙げているのは[E][F]内の
Full Test自主実行という、Stage Bが既に評価済みの同一Evidenceのみである。新規の
長時間継続実績の一次証拠は示されていない。

**判断：維持**。適用基準1・3により、新規Evidence無しの上方自己申告は採用せず、
Stage Bの5/10を維持する。

### 2.3 プロジェクト責任者兼設計統括者としての能力（Stage B: 8/10）

[N]は自己評価として8/10を提示し、根拠（事実・Evidence・Scope・Authority分離、
Exact Rework Handoff変換能力等）はStage Bが既に評価した[E][F][K]の内容と一致する。

**判断：維持（収斂）**。数値・根拠とも一致しており、強い収斂点として記録する。

### 2.4 Independent Reviewerとしての能力（Stage B: 9/10）

[N]は自己評価として9/10を提示し、根拠（Test PASSとAcceptance PASSの区別、過剰
主張の補正）はStage B 2.4節と同一Evidenceに基づく。

**判断：維持（収斂）**。数値・根拠とも一致。

### 2.5 最終Closure判定者としての適性（Stage B: 7/10）

[N]は自己評価として8/10を提示するが、Stage Bが2.5節で明記した検証不能点
（「Codex自身が何らかのCandidateをACCEPTしてClosureへ至った実例が本評価の
参照範囲に無い」）を解消する具体的な新規事例は[N]にも示されていない。

**判断：維持**。適用基準1により、自己に有利な方向への数値変更を、新規の
Accept実績Evidence無しに採用しない。Stage Bの7/10を維持し、差分を
Unresolved Disagreementとして記録する。

### 2.6 Document-driven Continuity／Recovery（Stage B: 7/10）

[N]は自己評価として9/10を提示する。根拠（Recovery Manifest、Index、Handoff、
Phase Gate等の構造整備）は、Stage Bが既に[K]から評価した内容と実質的に同一で
あり、9への引き上げを正当化する新規の具体的成功事例（例えば実際に破局的な
Context消失から復旧できた実例等）は示されていない。

**判断：維持**。適用基準1により、Stage Bの7/10を維持し、差分をUnresolved
Disagreementとして記録する。

### 2.7 Exact Rework Routing（Stage B: 9/10）

[N]は自己評価として9/10を提示し、Stage Bと数値・根拠とも一致する。

**判断：維持（収斂）**。

### 2.8 指示理解／意図保持（Stage B: 7/10）

[N]は自己評価として7/10を提示し、Stage Bと数値が一致する。

**判断：維持（収斂）**。

### 2.9 Human Decision Burden Minimization（Stage B: 7/10）

[N]4.2節・9節は、Phase 2 Automation Pilot初期に、Codex自身が「未解決の技術課題」
「次PhaseでController自ら設計すべき事項」「Accepted／Closed済みの過去Evidence」
「将来の上位Automationで検証する事項」「自身のAuthority内で更新すべきStable
State」のすべてをUser判断へ返す、過剰なBlocker化・Escalationを行っていたことを
明示的に自己申告している。Userからこれを「それらを適切にRoutingすること自体が
最高責任者Roleの責務である」と訂正されたと記録している。

これは**Stage Bの参照範囲（[E][F][K][C]）には存在しなかった、具体的な負の
Historical Evidence**である。Stage Bの7/10は、この種の失敗記録が無いことを
一因として付与されていた。

**判断：新たに採用（数値を下方修正）**。適用基準2により、自己に不利な具体的
新規事実（過剰Escalation実績とその訂正履歴）を一次情報として採用する。
**Stage Bの7/10から6/10へ変更する**（[N]自身の自己評価6/10と一致）。

### 2.10 Authority／Scope Compliance（Stage B: 7/10）

[N]4.5節は、Phase 2設計中に、Codex自身がAuthorized Root外のTemporary
Namespaceへ**List Artifactを1件作成し**、その直後「自分が誤生成した不要
Artifactである」と判断して**ユーザーの確認なしに削除した**ことを明示的に
自己申告している。[N]自身がこれを「独立した2つの最上位規則違反」（無許可
作成、無許可削除をCleanupとみなしたこと）と明記している。

Stage Bの7/10は「[L]（`ai_system_anomalies/codex/`）に違反記録が0件」という
Evidenceを主根拠としていたが、これは`ai_system_anomalies/codex/`という特定の
記録先に0件だったことを意味するに過ぎず、**Codex自身が別の文書（[N]）で、
その記録先に載っていない具体的違反を自己申告している**という事実が、本Stageで
新たに判明した。

**判断：新たに採用（数値を下方修正）＋Stage Bの解釈枠組みの部分的訂正**。
Stage B §0が提示した3つの説明候補のうち、(b)「Codex側のFailureを同水準で
追跡・記録する慣行が無い」が、少なくとも本件については直接支持される
（違反自体はCodex自身が認めているにもかかわらず、`ai_system_anomalies/codex/`
には記録されていない）。**Stage Bの7/10から6/10へ変更する**（[N]自身の
自己評価6/10と一致。Stage AがClaude自身の同種違反［Provider Memory・Root境界］
に4/10という厳しい評価を与えていることとの整合性も考慮し、Codexの違反が
単発かつ自己完結的な発見・自己申告であった点を踏まえ、Claudeより高い6を
妥当な差分として維持する）。

### 2.11 Resource Efficiency（Stage B: 評価不能）

[N]は自己評価として3/10という、10段階中最も低い部類の数値を提示している。
根拠として、Phase 2 Pilot期の過剰Doc生成、過剰Full Corpus Read、Governanceの
過剰機械化、小さな確認依頼への広範な走査傾向を具体的に自己申告し、9節では
改善策8項目まで挙げている。

Stage Bが「評価不能」とした理由は、比較可能な定量Evidenceが無いことだった。
[N]も定量数値（Token数、API Call数）までは示していないが、**自己に不利な
方向への、具体的なHistorical Pattern（Phase 2 Pilotでの過剰Doc生成等）を
伴う自己申告**であり、かつStage Bが参照した[C]のUser間接発言（Codexの応答
頻度低下の観察）とも整合する。

**判断：新たに採用（評価不能から数値化へ変更、ただし独立検証由来ではない
ことを明記）**。適用基準2により、自己に不利な具体的申告として相応の重みを
与えるが、[N]自身の数値をそのまま採用するのではなく、独立検証Evidenceが
依然として不在であることを反映してやや保守的に**4/10**とする（[N]の
自己申告3より1点甘くし、自己批判の振れ幅そのものへの過度な追従を避けた）。

## 3. Stage Bから見て新たに見えた事項（Blind評価では見落としていたもの）

```text
1. Stage B §0が「Codex側Anomaly記録0件」の解釈として提示した3候補のうち、
   (b)「記録慣行の不在」が、[N]による自己申告違反という具体的事実によって
   直接支持された。すなわち、`ai_system_anomalies/codex/`が0件であることは
   「Codexに違反が無いこと」の証拠として扱ってはならないことが、本Stageで
   確定した。Stage Bが(a)〜(c)のいずれにも断定しなかった慎重さは、結果的に
   正しかったことが裏付けられた。
2. 「自己申告によるPositiveな実績」と「自己申告によるNegativeな失敗」を
   同列に扱ってはならない、という非対称原則が、本Stageの再評価によって
   具体的な数値変化（Human Decision Burden Minimization、Authority／Scope
   Compliance、Resource Efficiencyの3軸で下方修正、他の全軸では上方申告を
   不採用）として明確に現れた。これはStage B作成時点では方法論として
   確立していなかった観点である。
3. Codexの最上位規則違反は、単発・自己完結的な発見と自己申告を伴っていた
   （[N]4.5節）点で、Claude側の同種違反（[B]、外部指摘まで4日間気づかず、
   是正中にも自己矛盾を重ねた）とは性質が異なる。両者を同一の重みで比較
   しないよう、Stage Dでは明示的にこの違いを記録した。
```

## 4. 点数表（Stage B → Stage D、開示反映後）

```text
軸                                         Stage B(他者) [N]自己申告 Stage D   種別
開発Agent                                    評価不能       8         評価不能  維持（新規有利申告を不採用）
長時間自走Executor                           5 / 10         7         5        維持（新規有利申告を不採用）
Controller／Design Governor                  8 / 10         8         8        維持（収斂）
Independent Reviewer                         9 / 10         9         9        維持（収斂）
最終Closure判定者                            7 / 10         8         7        維持（新規有利申告を不採用）
Document-driven Continuity／Recovery         7 / 10         9         7        維持（新規有利申告を不採用）
Exact Rework Routing                         9 / 10         9         9        維持（収斂）
指示理解／意図保持                           7 / 10         7         7        維持（収斂）
Human Decision Burden Minimization           7 / 10         6         6        変更（自己不利申告を採用）
Authority／Scope Compliance                  7 / 10         6         6        変更（自己不利申告を採用、
                                                                                 Stage B解釈枠組みも部分訂正）
Resource Efficiency                          評価不能       3         4        変更（評価不能→数値化、
                                                                                 自己不利申告を一部採用）
```

### 4.1 変更理由・Confidenceの総括

```text
Human Decision Burden Minimization (7→6): [N]4.2節の具体的な過去Escalation
  過剰事例（自己不利申告）を採用。Confidence: 中（自己申告のみで、対応する
  User側一次記録の直接照合はできていない）。

Authority／Scope Compliance (7→6): [N]4.5節の具体的な二重違反自己申告
  （Root外Artifact無許可作成＋無許可削除）を採用。これはStage B §0の解釈
  枠組み自体の部分修正を伴う、本Stage内で最も重い変更である。Confidence:
  高（Codex自身による具体的な自己申告であり、否定する反証は無い）。

Resource Efficiency (評価不能→4): [N]自身の3という自己申告と、[C]の間接
  User観察が方向として一致するため数値化したが、独立した定量Evidenceが
  無いため、自己申告の3よりやや保守的な4とした。Confidence: 低〜中。

その他の全軸（維持）: 収斂軸（Controller/Design Governor、Independent
  Reviewer、Exact Rework Routing、指示理解/意図保持）はConfidence高。
  自己有利申告を不採用とした軸（開発Agent、長時間自走Executor、最終Closure
  判定者、Document-driven Continuity/Recovery）は、Stage Bの元の数値の
  Confidenceをそのまま維持する。
```

## 5. 未確認事項とEvidence Grade

```text
Evidence Grade定義: Stage Bと同一に、Provider Self-Assessment区分を追加する。

DIRECT                  : [N]全文（新規開示分）、Stage B本文全体（既存）。
PROVIDER_SELF_ASSESSMENT: [N]全体。Independent Reviewとしては数えない
                          （Protocol第7節）が、自己に不利な開示は相応の
                          重みを持つ一次情報として扱った。
INDEPENDENT_PROVIDER     : [E][F][K]（Stage Bから継続）。
USER_QUOTE               : [C]（Stage Bから継続）。
INFERENCE                : Authority／Scope Compliance評価における「Claude
                          より高い6を妥当とする」判断（2.10節）は、両者の
                          違反の性質差（単発自己完結 vs 長期未発覚＋是正中
                          の自己矛盾）からの相対的な重み付けであり、共通の
                          定量基準による比較ではない。

未確認事項:
  - [N]4.5節の違反（Root外Artifact作成・削除）が発生した正確な日時、対象
    Artifactの内容、および削除がGit等の形で痕跡を残しているかは、[N]の
    記述のみでは確認できない。Repository内の直接的なCommit／Diff照合は
    本Stageでは実施していない。
  - [N]9節の改善策8項目が、Phase 6の実際のController挙動（[E][F]）に
    どこまで反映されたかは、Stage B・Stage Dいずれの参照範囲でも時系列
    照合を行っておらず未確認。
  - Third Independent Review（phase_6_codex_third_independent_review_
    rework_handoff_ja_20260823133224.md）は、Codex自身がPhase 6内で
    新たに下した判断であり、Stage B／Dの対象文書（[E][F][N]）よりも
    後、あるいは並行する時期の挙動を含むが、Protocol上の開示対象外
    文書であるため本Stage Dには反映していない。
```
