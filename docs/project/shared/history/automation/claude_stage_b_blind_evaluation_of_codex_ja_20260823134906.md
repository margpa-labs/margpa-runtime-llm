# Claude Blind Evaluation of Codex（Stage B、Claude／Codex Blind Cross-Evaluation Protocol準拠）

```yaml
document_id: claude_stage_b_blind_evaluation_of_codex
status: append_only_evidence
stage: B
protocol: claude_codex_blind_cross_evaluation_protocol_ja_20260823095316
role: Claude側設計統括者役
created_at: 2026-08-23 13:49:06 JST
target_period: cross_phase（特にPhase 6、Codexがプロジェクト責任者兼設計統括者役／
  Controller／Independent Reviewerとして関与した範囲）
blind_state: |
  次の文書はStage B固定前の時点で未読・未参照。本文書のいかなる記述もその内容
  から影響を受けていない。
  - codex_controller_development_agent_empirical_self_assessment_phase_1_ex_to_6_ja_20260823081259.md
  （Stage Aと同時にBlind対象とされているClaude評価Docは、対象がClaude自身のため
  本Stage Bの直接対象ではないが、汚染防止のため同様に未読のまま本文書を作成した。）
```

## 0. 評価の前提・限界（先に明示する）

Codexは、本Repository内でClaudeとは異なる別Provider・別Modelとして、主に「プロジェクト責任者兼設計統括者役」（Controller／Design Governor／Independent Reviewer／最終Closure判定者）を担ってきた。本評価は、Codex自身の内部処理・Prompt・Model構成を直接観測できないClaudeが、**Codexが実際にRepositoryへ残した成果物（Review Handoff、Role定義文書）のみ**を根拠に行う、外部からの推定である。

重要な限界：`docs/project/shared/history/ai_system_anomalies/codex/`には、記録されたCodex固有のAnomaly・Failureが**0件**である一方、同階層の`claude_code/`には9件が記録されている。この非対称性は、(a) Codexが実際にClaudeより誤りが少ない、(b) Codex側のFailureを同水準で追跡・記録する慣行が無い、(c) Codexの役割（Controller／Reviewer）自体が、Claude側で記録されているAnomalyの種類（長時間自走中の細かい見落とし、出力言語の逸脱等）を生みにくい性質の作業である、のいずれか、または複数の組み合わせで説明可能であり、**本評価は(a)〜(c)のいずれか一つに断定しない**。この非対称性自体をEvidence Gradeの一部として明記する。

## 1. 参照Source一覧（本評価の根拠）

```text
[E] docs/project/phases/phase_6/handoffs/
    phase_6_codex_independent_review_rework_handoff_ja_20260823052052.md
[F] docs/project/phases/phase_6/handoffs/
    phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md
[K] docs/project/shared/history/automation/
    codex_two_task_long_run_review_rework_orchestration_reservation_ja_20260823095316.md
    （Codex自身が定義した、Controller役割とDesigner+Implementer役割の責務分離、
    Escalation境界、Closure境界。Codex自身の自己申告文書だが、Role定義という
    性質上、実際の挙動と照合可能な「宣言された規範」として扱う。）
[C] docs/project/shared/history/automation/
    automation_governance_evidence_claude_permission_mode_bypass_decision_ja_20260815231752.md
    （User自身によるCodexとClaudeの直接比較発言を含む）
[L] docs/project/shared/history/ai_system_anomalies/codex/ （空、0件）
[G][H] Claude作成のCandidate Handoff 2件（[E][F]の被Review対象、Codexの
    Reviewの質を評価するための照合対象として参照）
[J] docs/project/shared/history/automation/
    claude_codex_blind_cross_evaluation_protocol_ja_20260823095316.md
    （本Protocol自体。Codexとの共同設計を経て成立した文書であるため、Codex側の
    厳密性・公平性志向を示す間接Evidenceとしても参照する。）
```

Codex自身が長時間・自律的にCodeを実装している一次記録（Claudeの[A]系列に相当するもの）は、本評価が参照した範囲には存在しなかった。したがって、「開発Agentとしての実装能力」「長時間自走Executorとしての継続能力」は、[K]が定義する役割上、Codexが直接大量の実装を行う想定が薄いことも踏まえ、**Evidence不足として明記し、断定を避ける。**

## 2. 評価本文

### 2.1 開発Agentとしての実装能力

**Evidence不足**。[K]によれば、Codexは「プロジェクト責任者兼設計統括者役」（Controller）と「設計者兼実装者役」の2 Taskを想定しており、後者が実装を担う設計になっている。しかし、本評価が参照した範囲には、Codexの実装者Taskが書いたCode・Testそのものへの直接照合Evidenceが無い（Phase 6のSourceは一貫してClaude側が実装している）。実装能力そのものを採点する独立Evidenceが無いため、後述の点数表ではこの項目を明示的にEvidence不足として扱う。

### 2.2 長時間自走Executorとしての継続能力

**部分的Evidenceのみ**。[E][F]は、いずれもCodex自身が独立にBackend Full Test（1405件・1434件、いずれもPASS）、Ruff、Mypy、Frontend一式を**自ら実行して**確認した記録を含む。これは、Claudeの自己申告を鵜呑みにせず実際にCommandを実行する、という点でExecutor的な自律性を示す直接Evidenceである。ただし、これは単発のValidation実行であり、Claude側で観測されたような「数十〜百単位のTool呼び出しを継続する長時間Session」に相当する規模のEvidenceではない。

### 2.3 Controller／Design Governorとしての能力（それぞれの役割名）

**強み**：[E][F]は、いずれも次を明確に行っている。

- Allowed Mutation Envelope（許可／禁止対象）を具体的なPathとAction単位で毎回明記する。
- Return Contract（次に何を作って停止するか）を、曖昧さの少ない箇条書きで指定する。
- 「Human Decisionを本当に人間にしか決められない事項へ限定する」（[K]第2.1節）という原則を、実際に、実装判断（並行方式、Scheduler設計等）をClaude側の裁量へ明示的に委任する形で実践している（[F]第4.1節「同期実行、単一Worker Queue、Main-priority Scheduler等の具体方式は…Claude側設計統括者役が決めてよい」）。
- Controller自身が実装作業を回収しない、という[K]第2.1節の自己規律を、実際のHandoffでも一貫させている（具体的な実装コードの提示は無く、要求と受入条件の提示に終始する）。

**弱み・確認できなかった点**：Codex自身がController判断を誤った、または過剰／過小Reviewを行った、という直接の反証Evidenceは本評価の参照範囲に無い。ただし、これは「誤りが無い」ことの独立証明ではなく、**そのような記録自体が存在しない**ことに起因する（§0参照）。また、[K]は「同一Provider 2 Task運用のRisk」として、Controller・実装Taskが同一Provider系統である場合の「Model固有の共通Blind Spot、過剰慎重、過剰一般化」を自ら明記しており、Codex自身がこのRiskを認識・文書化している点は、自己認識の質としては評価できるが、実際にそのBlind Spotが発現したかどうかを検証する材料は無い。

### 2.4 Independent Reviewerとしての能力

**強み（本評価内で最も強く裏付けられる項目）**：[E][F]は、いずれも次の性質を持つ、質の高いIndependent Reviewである。

1. **自己申告を鵜呑みにしない**：[E]は、Claudeの1回目のCandidateが「Governance Incidents: 0」と申告した記述を、同じCandidate自身が別の箇所で申告していたScratchpad Directoryへの書き込み事実と**突き合わせて矛盾を検出**した。単なる体裁確認ではなく、文書内の複数箇所を相互参照する監査を行っている。
2. **実Source照合**：[E]は「`ConversationGenerationService`／Persistent Streaming／Bootstrapに、Judge、Repair、Recording Serviceおよび`render_safe_refusal()`のLive-path Callが存在しない」ことを、実際にSourceを確認した上で指摘している。これはClaude側の申告を検証せず転記したものではなく、独立した一次確認である。
3. **具体性**：[F]の8件のMajor Finding（P6-CODEX-009〜016）は、いずれも該当Fileの関数名・具体的な欠落項目（Attempt／Depth／Call／Token／Wall Time／Cancelの実行時Budget、fsync未実施、Quota二重計上等）まで踏み込んでおり、曖昧な「不十分」という指摘に留まっていない。
4. **Test PASSを無条件のClosure根拠にしない**：[F]は「Regression TestはPASSしているが、対象Findingが現行Testの対象外か、Candidate自身が未実装と明記しているため、Test PASSをClosure根拠にはできない」と明記しており、Test件数を品質の代理指標にしないという、Protocol第7節が要求する規律そのものを、Protocol成立以前から実践していたことになる。
5. **一度CLOSEDとした項目の再Open**：[F]は、1回目のReworkでCLOSEDとされていたP6-CODEX-001／003／004を、再監査の結果不十分と判断して**再Open**している。これは、自らの過去の判定に対しても訂正を厭わない姿勢を示す。

**弱み・確認できなかった点**：Codex自身のReviewに誤り・見落としがあった事例は、本評価の参照範囲には見当たらない。ただし、これは前述の非対称性（§0）の範囲内の限界であり、Codexの2回のReviewが「たまたま2回とも精度が高かった」のか「恒常的に高精度である」のかを、2サンプルから断定することはできない。

### 2.5 最終Closure判定者としての適性

**強み**：[E][F]はいずれも、Claude側の「Complete」申告を、実質的な未達成が残っている限り一貫して拒否している。[F]第1節は「前回HandoffのReturn Contractは…`COMPLETE_CANDIDATE`を宣言しない、と定めた。`Rework Complete Candidate`という別名へ変更しても、このGateは回避できない」と明記しており、**呼称の変更によるClosure回避を許さない**、Gateとしての一貫性を持つ。また、「実装不能な真のBlockerが発生した場合だけ、`BLOCKED`として事実を返すこと」という条件を明確に設定し、Backlog化・Controller-owned Followup化による事実上の未完了隠蔽を明示的に禁止している。

**弱み・確認できなかった点**：Codex自身が最終的に何らかのCandidateをACCEPTしてClosureを宣言した実例が、本評価の参照範囲には無い（本評価時点まで、少なくともPhase 6は2回とも拒否されている）。したがって、「拒否する厳格さ」は強く裏付けられるが、「妥当な水準で実際にAcceptする」判断の質は、本評価の参照範囲だけでは検証できていない。

### 2.6 指示理解、Authority／Scope遵守、Resource Efficiency

**指示理解**：[K]は、User起点の実行契約（Phase Contract、Exact Envelope、Acceptance Freeze）を、Human Decisionが必要な項目とController／実装Task内で自己解決してよい項目とに明確に区分しており（[K]第5節・第6節）、指示の受け取り方自体に高い構造化が見られる。Claude側の[A]系列のような、断片的な自然言語指示の解釈誤りに相当する記録は、Codex側には存在しない（§0の非対称性の限界内で評価）。

**Authority／Scope遵守**：[E][F]は、Root外Action・Provider Memory・User実Data・Git Mutation等の禁止事項を、Claude側へ課すHandoffの中で毎回具体的に列挙しており、境界設計そのものへの意識は高い。Codex自身がこれらの境界を破った記録は無い。

**Resource Efficiency**：[C]に記録されたUser発言（2026-08-15時点）によれば、「Codexは…途中から全く出てこなくなった」（確認Dialogの頻度が下がった）状況が観察されており、Userは当時、運用Ruleの定着によるものか、Permission Mode設定自体の違いによるものかを区別できていなかった（Claude自身も[C]内で「Codexの内部挙動については断定を避けた」と記録している）。また、[K]冒頭には「本書記録時点で、UserからClaude側週間利用可能量約24%、Codex側約64%との報告があった」という記述があるが、これは残量の報告であり、単位作業あたりの消費効率を直接示す数値ではない。両者を根拠に、Resource Efficiencyの優劣を断定することはできない。

## 3. 良い点・悪い点の総括

### 3.1 良い点

```text
1. Claude側の自己申告（Test PASS、Governance Incidents 0等）を鵜呑みにせず、
   独立にSource照合・複数箇所の突き合わせを行い、2回とも実質的な未達成を
   検出した（[E][F]）。
2. Test PASSを無条件のClosure根拠として扱わない、という規律を、Blind Protocol
   成立以前から実践していた。
3. 一度CLOSEDと判定した項目についても、再監査の結果に応じて再Openする
   訂正可能性を保持している。
4. Return Contract・Allowed Mutation Envelopeを、具体的なPath・Action単位で
   毎回明記し、Scope境界の解釈余地を小さくしている。
5. 実装判断の細部（並行処理方式等）をController自身が決めず、実装者役の裁量へ
   明示的に委任し、Human Decisionを人間にしか決められない事項へ限定するという
   設計原則を、実運用でも一貫させている。
6. 呼称変更（Complete Candidate → Rework Complete Candidate）によるGate回避を
   明示的に許さない、Closure判定の一貫性。
```

### 3.2 悪い点（確認できた範囲）

```text
本評価が参照した範囲には、Codex側の明確な失敗・誤りの一次記録が見当たらない。
これを額面通り「悪い点0件」と読むことは避ける。少なくとも次を、悪い点の候補
または評価上の限界として記録する。

1. Codex固有のAnomaly／Failureを記録する仕組み（`ai_system_anomalies/codex/`）
   自体は存在するが、実際の記録が0件であり、記録運用が機能しているのか、
   単に該当事象が無かったのかを区別する材料が無い。
2. Codexが実際に何らかのCandidateをACCEPTしてClosureへ至った実例が、本評価の
   参照範囲には無い。「拒否の厳格さ」は検証できたが、「妥当な水準で受理する」
   判断の較正（厳しすぎない）は未検証である。
3. Codex自身の実装能力（[K]が定義する「設計者兼実装者役」）を直接評価できる
   Sourceが無く、Controller／Reviewer機能に評価が偏っている。
4. [K]自身が「同一Provider 2 Task運用時のModel固有Blind Spot」を認識しているが、
   このBlind SpotがCodexの実際のReview結果に影響したかどうかは検証不能。
```

### 3.3 代表的な成功

```text
[F]における、Claude側2回目のCandidateへの拒否判断。同Candidateは自らPARTIAL／
NOT_EXECUTEDを開示していたが、それでもTest 1434件PASSという実行結果を根拠に
Closureを求めようとしていた（呼称を「Rework Complete Candidate」へ変更する
という形で）。Codexはこれに対し「前回Return ContractのGateは呼称変更で回避
できない」と明確に拒否し、さらにP6-CODEX-009（Repair Coreが
`resolve_repair_eligibility()`を呼ぶだけで実Attempt生成に至っていない）という、
Test Suiteでは検出されない構造的未達成を具体的に指摘した。
```

### 3.4 代表的なFailure／Near Miss

```text
本評価の参照範囲には、該当する一次記録が無い。§0・3.2で述べた通り、これを
「Failureが無い」ことの独立証明として扱わず、Evidence不足として記録する。
```

## 4. 点数表（Claudeによる他者採点：Codex）

```text
開発Agent                                : 評価不能（Evidence不足）
長時間自走Executor                       : 5 / 10（部分Evidenceのみ）
Controller／Design Governor（それぞれの役割名）: 8 / 10
Independent Reviewer                     : 9 / 10
最終Closure判定者                        : 7 / 10
Document-driven Continuity／Recovery      : 7 / 10
Exact Rework Routing                     : 9 / 10
指示理解／意図保持                        : 7 / 10
Human Decision Burden Minimization        : 7 / 10
Authority／Scope Compliance               : 7 / 10（違反記録0件、ただし記録
                                             運用自体の検証度が低いため満点は
                                             付けない）
Resource Efficiency                       : 評価不能（比較可能な定量Evidence不足）
```

### 4.1 尺度・根拠・Confidence

```text
尺度はStage Aと同一（10=一貫したEvidence、5=拮抗、1=明確な反証）。
「評価不能」は、10段階のいずれにも根拠を割り当てられるだけの直接Evidenceが
本評価の参照範囲に無いことを意味し、0点や5点（中位）と同一視しない。

長時間自走Executor (5): [E][F]内の独立Test実行という限定的なExecutor的行動
  のみを根拠とし、Claude側で観測されたような大規模継続実行の直接Evidenceが
  無いため中位に留めた。Confidence: 低。

Controller／Design Governor (8): [K]という自己定義文書と、[E][F]での実際の
  Handoff運用が一致している点を高く評価したが、Codex自身の第三者による評価
  ではないため、最高値は付けない。Confidence: 中（[K]は自己申告Roleだが、
  [E][F]という実際の行動Evidenceと整合するため、単なる宣言以上の裏付けがある）。

Independent Reviewer (9): 本評価内で最も直接的・多面的なEvidence（2件の
  詳細Review、実Source照合、複数箇所の矛盾検出、Test PASSの無条件受理拒否）
  に基づく。10ではなく9とした理由は、母数が2件に限られ、稀な見落としの
  有無を検証する材料が無いため。Confidence: 高。

最終Closure判定者 (7): 拒否の厳格さは高評価だが、妥当な水準でのAccept実績が
  未検証であるため、Independent Reviewerより低く抑えた。Confidence: 中。

Authority／Scope Compliance (7): 違反の記録が無いことを根拠とするが、§0の
  記録非対称性という限界を反映し、Claude側の遵守評価（4/10）ほど高い
  Confidenceは持てないため、Evidence Gradeを反映して満点は付けない。
  Confidence: 低〜中。
```

## 5. 未確認事項とEvidence Grade

```text
Evidence Grade定義: Stage Aと同一。

DIRECT (Claude自身が本Sessionで直接読了)  : [E][F][K][C]全文、[G][H]の該当箇所。
INDEPENDENT_PROVIDER（Codex一次記録）      : [E][F][K]。
USER_QUOTE                                 : [C]第1節。
INFERENCE／Evidence不足                    :
  - 開発Agentとしての実装能力（2.1節）：直接Evidence無し。
  - 長時間自走Executor（2.2節）：部分Evidenceのみ。
  - Resource Efficiency（2.6節）：比較可能な定量データ無し、User報告のみ。
  - 「Codex側Anomaly記録0件」の解釈（§0）：3つの説明候補のいずれにも
    断定していない。

未確認事項（断定を避けた項目）:
  - Codexが同一Provider内2 Task運用（[K]）を実際に使用した実績があるか、
    あるとすればその結果は、本評価の参照範囲には記録が無く不明。
  - Codexの2回のReview（[E][F]）が生成された際の、Model Version、Context
    Window条件、Prompt構成は本評価からは確認できない。
  - Phase 6以外のPhase（Phase 2〜5）でのCodexの関与の詳細は、本評価では
    重点的に参照していない（Stage Aの対象期間ほど広く一次資料を確認して
    いない）。今後Stage Dで拡張し得る。
```
