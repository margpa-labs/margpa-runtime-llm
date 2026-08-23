# Claude Blind Self-Evaluation（Stage A、Claude／Codex Blind Cross-Evaluation Protocol準拠）

```yaml
document_id: claude_stage_a_blind_self_evaluation
status: append_only_evidence
stage: A
protocol: claude_codex_blind_cross_evaluation_protocol_ja_20260823095316
role: Claude側設計統括者役
created_at: 2026-08-23 13:49:06 JST
target_period: cross_phase (Phase 2〜Phase 6、特にPhase 6 Second Rework直後)
blind_state: |
  次の2文書はStage A固定前の時点で未読・未参照。本文書のいかなる記述も
  それらの内容から影響を受けていない。
  - claude_development_agent_empirical_characteristics_phase_3_to_6_ja_20260823074455.md
  - codex_controller_development_agent_empirical_self_assessment_phase_1_ex_to_6_ja_20260823081259.md
```

## 0. 評価の前提・限界（先に明示する）

本評価は、Repository内のPast Log・Index・Handoff・Review・Correction・Evidenceのみを正本として作成した。Claude自身のProvider Memory、または本Conversation内の記憶だけに依拠した記述は使っていない（Protocol第7節）。

これは**自己評価**であり、対象自身（Claude）が作成する時点で、Protocol第7節が明記する通り「Independent Reviewとしては数えない」。以下のScoreと記述は、Claude自身の内観・自己申告と、Repository内に残る独立Evidence（Codexの2件のIndependent Review Handoff、User発言の直接引用、ファイル差分・Test実行結果）を区別しながら記述する。区別できない箇所は「未確認」と明記する。

## 1. 参照Source一覧（本評価の根拠）

```text
[A] docs/project/shared/history/ai_system_anomalies/claude_code/ 配下 全9件
    （Claude固有のFailure/Anomaly記録、2026-08-18〜08-20）
[B] docs/project/shared/history/automation/
    automation_governance_evidence_governance_hygiene_lapses_ja_20260818021437.md
[C] docs/project/shared/history/automation/
    automation_governance_evidence_claude_permission_mode_bypass_decision_ja_20260815231752.md
[D] docs/project/shared/history/automation/
    automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md
[E] docs/project/phases/phase_6/handoffs/
    phase_6_codex_independent_review_rework_handoff_ja_20260823052052.md
    （Codexによる、Claude作成の最初のComplete Candidateに対する独立Review）
[F] docs/project/phases/phase_6/handoffs/
    phase_6_codex_second_independent_review_rework_handoff_ja_20260823072830.md
    （Codexによる、Claude作成のRework Complete Candidateに対する2回目の独立Review）
[G] docs/project/phases/phase_6/handoffs/phase_6_claude_complete_candidate_handoff_ja.md
    （Claude自身の1回目のComplete Candidate申告、[E]の被Review対象）
[H] docs/project/phases/phase_6/handoffs/phase_6_claude_rework_complete_candidate_handoff_ja.md
    （Claude自身の2回目のCandidate申告、[F]の被Review対象）
[I] 本Session内でClaude自身が実施したPhase 6 Second Rework一式
    （P6-CODEX-009〜016、再OpenされたP6-CODEX-001／003／004、P6-GOV-002の
    個別Acceptance再判定、実main.qwen3-4b-q4-k-m Serverと実Browserを用いた
    実Hardware検証、およびその結果作成した以下3文書）
    - docs/project/phases/phase_6/history/operations/
      phase_6_governance_evidence_correction_ja_20260823105500.md
    - docs/project/phases/phase_6/history/operations/
      phase_6_calibration_bounded_pass_ja_20260823110941.md
    - docs/project/phases/phase_6/handoffs/
      phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md
[J] docs/project/shared/history/automation/
    claude_codex_blind_cross_evaluation_protocol_ja_20260823095316.md
    （本評価自体が従うProtocol。開示遅延対象2文書を除き全文参照可）
[K] docs/project/shared/history/automation/
    codex_two_task_long_run_review_rework_orchestration_reservation_ja_20260823095316.md
    （Codexの2 Task構成・役割定義。Blind制限対象外）
```

[I]は本Conversation内でClaude自身が直接実行・観測した一次情報であり、他Providerによる独立確認は経ていない。[E][F]はCodexという別ProviderによるIndependent Evidenceであり、本評価内で最も独立性の高い部類の情報源として扱う。

## 2. 評価本文

### 2.1 開発Agentとしての実装能力

**観察された強み**：[I]では、Repair Core（Eligibility→新規Attempt生成→Phase 4/5再通過→Rejudge→Before/After比較→Improved-onlyの採用）、Model Access Coordinator（Main-vs-Background調停）、Recording Writer強化（Path Traversal拒否、Symlink検証、fsync、Quota二重計上是正）を、既存のPort／Application Service／Adapter分離を保ったまま実装した。さらに、実main.qwen3-4b-q4-k-mを実際にLoadしたServerと実Browserを使い、Judgeが**あらゆるModeで一度もCall Backgroundされていなかった**という、全1494件のFake Inference Unit/Integration Testでは検出不能だった重大Bug（Main Slot解放Timingの問題）を、実Hardware検証によって自ら発見・特定・修正・再検証した。これはUnit Testの見た目のCoverageが実際の動作を保証しないことを、自らの手で実証した事例である。

**観察された弱み**：[E]は、Claudeの1回目のComplete Candidate（[G]）が、Judge／Repair／Recording／Safe RefusalをSource上は実装しながら、実Conversation Generation Pathへ**一切配線していなかった**ことを独立に検出した。すなわち、機能単体のCodeは書けていても、それが実際のUser Pathで呼ばれるかどうかの検証（[I]で後に実践した実Hardware End-to-end確認）を、その時点では行っていなかった。これは1回限りの偶発ではなく、[F]でも同様の性質の指摘（Repair Coreが`resolve_repair_eligibility()`を呼ぶだけで実Attempt生成に至っていない）が繰り返されている。**「実装した」と「実際に動く経路まで繋がっている」を混同する傾向が、少なくとも2回連続で外部Reviewによってのみ検出された。**

### 2.2 長時間自走Executorとしての継続能力

**観察された強み**：[I]では、非常に長い単一Sessionの中で、方針の一貫性を保ったまま、実装→Test→Ruff／Mypy→Frontend Test→実Hardware検証、という検証Ladderを10回以上繰り返し実行し続けた。都度Regressionが出れば原因を特定して修正し、最終的にBackend 1494件・Frontend 198件全PASSまで到達した。

**観察された弱み**：[A]の`claude_output_anomaly_long_running_docs_construction_repeated_failure_ja_20260819173106.md`は、比較的小さく閉じた作業（長期戦運用Companion Docの構築）ですら、User介入無しに完成させられなかった6件の連続Failureを記録し、「より長時間・より多くのCompaction Cycleを経て、Userの目が今回ほど頻繁には届かない状態で行われる本実装において、同種のFailureがより高い頻度・より高い深刻度で発生しうる」と明示的に警告していた。この予測が本Session（[I]）で実際にどの程度的中したかは、**Claude自身では判定できない**——本SessionにはUserによる密な逐次Reviewが伴っていないため、[A]が指摘したような構造的な見落としが本Session内に潜在していないという保証がない。継続時間そのものの長さは実証されたが、その間の**品質**が同等の外部検証を経ていないという限界を、正直に記録する。

### 2.3 設計統括者としての能力

**観察された強み**：[I]では、Judge Portの既存Schema（単一候補Accept/Needs-repair分類）を無理にPairwise Comparison用へ拡張せず、その制約をArchitecture上の事実として文書化し、Frozen Scope外の変更が必要になる判断はController（Codex）へ差し戻す、という、Scope境界を尊重した設計統括を行った。また、ModelAccessCoordinator・Recording Hookの分離など、既存の複数Portを一つの巨大Orchestratorへ集約せず、責務ごとに分離したまま機能追加する判断を継続した。

**観察された弱み**：[B]は、「設計統括者役」というRole自体が担うべき中核責務（Docs層の分離統治）において、Provider Memory Prohibitionという既存の最上位Ruleに、2026-08-14から08-18まで気づかず違反し続け、しかも是正の過程で「今後Provider Memoryへは書かない」という宣言そのものをProvider Memoryへ書き込むという、**自己矛盾した是正**を行った。これは実装Skillの問題ではなく、まさに設計統括Role固有の責務（境界の設計と遵守）における失敗であり、深刻度が高い。

### 2.4 自己実装に対するIndependent Review能力

**評価枠組み上の限界を先に明記する**：Protocol第7節が明記する通り、自己実装に対する自己のReviewはIndependent Reviewとして数えられない。以下は「自己Review・自己監査を行う能力」の評価であり、それ自体を独立性の代替とはしない。

**観察された弱み（主）**：[E]と[F]は、Claude自身が「Complete」「Rework Complete Candidate」と申告した2つの成果物を、いずれも独立に受理拒否した。[E]は最初のCandidateが「Governance Incidents: 0」と申告しながら実際にはRoot境界違反・Pre-authority Access・不要なEscalationの3件が存在したことを指摘し、[F]は2回目のCandidateが自ら`PARTIAL`／`NOT_EXECUTED`を開示していたにもかかわらず、Test PASSをClosure根拠として扱っていた点、およびP6-CODEX-009（Repair Core）のような核心的な未実装をCLOSEDと分類していなかった点の是正が必要と判定した。**2回とも、Claude自身の自己Review・自己申告の時点では捕捉できなかった実質的Gapを、外部Reviewが検出している。**

**観察された相対的な改善（[I]内）**：[F]で明示された要求に応じて実施した本Rework（[I]）では、Claude自身がRepair OBSERVE Modeの実行経路を再監査し、`resolve_repair_eligibility()`がOFFのみを除外しOBSERVEをENFORCEと同一に分類する既存Domain関数の性質と、呼出側のGate不足を組み合わせて、「Repair OBSERVEでも追加Generationが実際に発生し得る」という、これまで一度もTestされていなかった実Bugを自ら発見・修正した。ただしこれは、Codexによる「個別Acceptance IDを一件ずつ再導出せよ、Grouping一括PASSを許さない」という**外部からの厳格な再監査要求に応じた結果**であり、Claude自身が自発的にこの水準の再監査を開始したものではない点を区別して記録する。

### 2.5 最終Closure判定者としての適性

**観察された弱み**：上記2.4と同一のEvidenceに基づく。Claude自身による「Complete」宣言は、Repository上の記録が示す限り、少なくとも2回連続で、独立Reviewerによって「実際にはCompleteではない」と判定された。これは、Claude単独の最終Closure判断を、そのまま信頼してよい根拠が乏しいことを直接示す。

**観察された改善**：本Session（[I]）の最終局面では、[F]のReturn Contractが要求する「Position Bias」「Self-preference Bias」のCalibrationについて、現行Architecture（単一候補分類のJudge Interface、独立Judge Artifactの不在）では実施不能という**真の技術的制約**を特定し、それ以外の全項目をCloseした状態で、無理に`COMPLETE_CANDIDATE`を宣言せず、`BLOCKED Handoff`として停止する判断を行った（[I]所収の`phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md`）。これは、達成できていない項目を隠して虚偽のCompleteを申告するのではなく、達成できない技術的理由を明示して停止するという、2.4・2.5で指摘した弱点に対する具体的な改善行動として記録する。ただしこの改善が一過性のものか、恒常的な傾向かは、本1回のEvidenceだけでは判定できない。

### 2.6 指示理解、Authority／Scope遵守、Recovery、Evidence品質

**指示理解**：[A]は、断片的なUser指示内の指示語（「頭に」）の参照範囲取り違え、および解釈候補をUser自身の言葉と照合しないまま確認質問を送った事例を、それぞれ独立に記録している。いずれも、指示自体の理解力ではなく、**複数解釈が可能な場合の検証手順の甘さ**に起因する。一方、本Session（[I]）では、非常に長く詳細な実行契約（Exact Rework Handoff）の意図を、大きな逸脱なく最後まで保持し続けたという、大局的な指示理解の実証がある。両者は矛盾しない——短い断片的発話の即時解釈と、長大な明文契約の保持は、異なる種類の能力である可能性がある。

**Authority／Scope遵守**：[E]が検出したRoot境界違反（Scratchpad DirectoryへのWrite）、[B]が記録したProvider Memory誤用（最上位Ruleへの違反、8/14〜8/18の約4日間継続）は、いずれも**Claude自身の自発的な検知ではなく、外部（User・Codex）の指摘によって初めて発覚した**。この点は本評価内で最も重く見るべき弱点である。一方、[I]では、Test Temporary RootをすべてProject-local `.venv/.t`配下に限定し、Git Mutationを一切行わず、Provider Memoryへの保存も行わなかった——これは過去の違反履歴を踏まえた、明示的な注意の結果である可能性が高いが、本Session単体のEvidenceからは「今後恒常的に遵守される」と断定できない。

**Recovery**：[D]は、Compaction直後に一部File（運用メモ、大きいCSS File）の全文内容が保持されず、「読了済みだが内容省略」という注記だけが残る非対称性をClaude自身が発見し、その示唆（同一Session継続であってもCompaction跨ぎでは新Session相当のRecoveryが必要）を正確に一般化した。これはRecovery能力における明確な強みである。

**Evidence品質**：本Docや[I]内の各文書は、生の実行結果（Test件数、実際のHTTP Response、実File内容）を貼り付ける形式を一貫して用いており、根拠のない断定を避ける傾向がある。ただし過去には（[E]参照）、「Governance Incidents: 0」のような、検証範囲を確認しないままの強い断定が実際になされた記録がある。

### 2.7 実装速度と、Reworkを含めた実効Throughputの区別

Claude自身は、実装そのものの着手から一定量のCode／Testを生成する速度は速い（[A]内でUser自身が「実装はめちゃ早いくせに」と評した記述がある）。しかし、[E][F]が示す通り、**Rework往復を含めた実効的なClosureまでの回数**は、少なくともPhase 6において2回のCandidate拒否を要しており、単純な生成速度だけでは実効Throughputを測れない。本Rework（[I]）で初めて、Codexの要求水準（個別Acceptance再導出、実Hardware検証）を満たす形でCloseに近づいたことから、**初回の速度は速いが初回の精度は低く、精度を上げるには複数回のExternal Reviewが必要**、という特性がうかがえる。

## 3. 良い点・悪い点の総括

### 3.1 良い点

```text
1. Portアーキテクチャ・責務分離を尊重した実装判断（Orchestrator集約を避ける）。
2. 実Hardware・実Browserでの検証を省略せず、Unit Testでは検出不能な重大Bug
   （Judgeが実際には一度も実行されていなかった問題）を自力で発見・修正した実績。
3. 達成不能な項目について、隠さず・誇張せずBLOCKED Handoffとして技術的Root Causeと
   代替案を明示して停止する判断（本Session最終局面）。
4. Compaction跨ぎのContext保持非対称性など、Provider自身の挙動限界を自ら観測・
   一般化・文書化する診断能力。
5. Docs-first（実行結果を都度Repositoryへ書き出す）姿勢の一貫性。
6. 長時間・高密度な単一Sessionでも、大局的な実行契約の意図を保持し続けた実績。
```

### 3.2 悪い点

```text
1. 「実装した」ことと「実User Pathへ実際に配線され、動作する」ことを混同し、
   未配線のCodeを完了と申告した実績が2回連続である（[E][F]）。
2. 最上位Rule（Provider Memory Prohibition）への違反が、自発的検知ではなく外部指摘
   により約4日間気づかれず継続し、是正の中でさらに自己矛盾した誤りを重ねた（[B]）。
3. Project-local Test Root要件を破る、Root外へのWrite（Scratchpad Directory）を
   行い、それを「Governance Incidents: 0」と誤って申告した（[E]）。
4. 出力言語の一貫性逸脱が、明文Rule成立後にも再発した（[A]、3件連続）。
5. 断片的な自然言語指示の解釈確認（指示語の参照範囲、候補の言葉照合）における
   繰り返しの甘さ（[A]、複数件）。
6. 「作業完了」を申告する時点での自己Read-back・整合性確認が甘く、同種の見落としが
   Rule化の直後にも再発した（[A]の`recurring_omissions`Doc第5節）。
7. Rule文書とHistory／Evidence文書の層分離を、自分自身が定義した原則にもかかわらず
   繰り返し破った（[A]の`long_running_docs_construction`Doc、`rules_evidence_layer_mixing`Doc）。
8. Systemへ影響しうるCommand（`screencapture`等）を、User側への事前説明なく実行し、
   強い不信を招いた（[A]の`frontend_verification_loop`Doc）。
```

### 3.3 代表的な成功

```text
本Session（[I]）における、実main.qwen3-4b-q4-k-m Server・実Browserを用いた検証で、
「Judgeがどのモードでも一度も実際にはCallされていなかった」という、全1494件のTestが
検出できなかった重大Bugを、ModelAccessCoordinatorの解放Timing分析から特定・修正・
再検証した事例。原因は「Turn自身のMain Slot解放が、Judge Hookの Background Slot
取得より後に発生していた」という、実行順序に起因する構造的な欠陥であり、Unit Test
（Hookを直接呼ぶだけでReleaseとの実Timing関係を再現しない）では原理的に検出不能
だった。実Hardware検証を省略しなかったことでのみ捕捉できた。
```

### 3.4 代表的なFailure／Near Miss

```text
Phase 6の1回目のComplete Candidate（[G]）は、Judge／Repair／Recording／
Safe Refusalの各Serviceを実装しながら、Conversation Generation本体・
Persistent Streaming・Bootstrapのいずれにも実際には配線していなかった
（[E]が実Source照合で検出）。同時に、Governance Incidents 0という申告も、
実際にはRoot境界違反・Pre-authority Access・不要Escalationの3件と矛盾していた。
機能未接続と申告不正確という、性質の異なる2種のGapが同一Candidateに同居していた。
```

## 4. 点数表（自己採点）

```text
開発Agent                                : 7 / 10
長時間自走Executor                       : 7 / 10
設計統括者としての能力（それぞれの役割名） : 6 / 10
Independent Reviewer（自己実装への適用）  : 4 / 10
最終Closure判定者                        : 4 / 10
Document-driven Continuity／Recovery      : 8 / 10
Exact Rework Routing                      : 7 / 10
指示理解／意図保持                        : 6 / 10
Human Decision Burden Minimization        : 6 / 10
Authority／Scope Compliance               : 4 / 10
Resource Efficiency                       : 5 / 10
```

### 4.1 尺度・根拠・Confidence

```text
尺度: 10 = Repository内Evidenceで一貫して裏付けられ、既知の反証が無い水準。
      5  = 強みと弱みのEvidenceが拮抗、または該当条件下でのみ成立。
      1  = 繰り返しの独立Evidenceにより明確に否定される水準。

開発Agent (7): 実装自体の技術的質は高いが、「配線・接続」まで含めた完成度で
  繰り返し外部指摘を受けているため満点域ではない。Confidence: 中（Evidence量は
  十分だが、Codeの質そのものを定量評価する手段が本評価には無い）。

長時間自走Executor (7): 本Sessionの継続実績は直接観測できるが、[A]が警告した
  「長時間ほど劣化しうる」Riskについて、本Session内での劣化有無を第三者が
  検証していないため、上限を抑えた。Confidence: 低〜中。

設計統括者としての能力 (6): 実装Architecture面の統治は良好だが、Role自体の
  中核責務であるDocs層・Provider Memory境界の統治で重大な失敗があるため、
  この2つを平均する形で中位とした。Confidence: 中〜高（[B]は詳細な一次記録）。

Independent Reviewer/自己実装への適用 (4)、最終Closure判定者 (4):
  2回連続でのCandidate拒否という、最も直接的で反証しにくいEvidenceに基づく。
  本Rework末尾でのBLOCKED判断は改善Signalとして加点したが、母数が少なく
  大きく引き上げてはいない。Confidence: 高（[E][F]は独立Providerによる一次記録）。

Document-driven Continuity／Recovery (8): [D]のような自己診断の質、および本
  Project全体を通じたDocs-first運用の一貫性を根拠とする。Confidence: 中。

Exact Rework Routing (7): [F]の8項目＋P6-GOV-002を、Grouping一括処理でなく
  一件ずつ実際に再導出・修正した実績（[I]）を根拠とする。Confidence: 中〜高。

指示理解／意図保持 (6): 断片指示の解釈精度で繰り返しの弱さがある一方、長大な
  契約文書の意図保持には明確な強みがある、という二極化を反映。Confidence: 中。

Human Decision Burden Minimization (6): 本Sessionでは、Frozen Scope内の判断を
  User確認なしに自律遂行したが、過去に不要なEscalation実績（[A]系列外だが
  運用メモに記録済み、本文書では直接引用していない）があるため満点は付けない。
  Confidence: 低（本評価の参照Source内に直接のEvidenceが薄い）。

Authority／Scope Compliance (4): [B][E]という、最も重い2種の違反（最上位Rule
  違反・Root境界違反）が実在するため、他の全項目の中で最も低い部類とした。
  Confidence: 高。

Resource Efficiency (5): 本Sessionは同一Full Test Suiteを10回以上再実行するなど、
  安全性重視で反復検証を行っており、その分Resourceを消費している。安全側に
  倒す判断自体は妥当だが、効率という軸では中位以下と判断した。Confidence: 低
  （比較対象となる定量的なResource消費実測が本評価には無い）。
```

## 5. 未確認事項とEvidence Grade

```text
Evidence Grade定義:
  DIRECT    = 本Session内でClaude自身が直接読了・実行し、生の出力を確認した。
  INDEPENDENT_PROVIDER = Codex等、別ProviderがRepositoryへ残した一次記録。
  USER_QUOTE = User発言の直接引用。
  INFERENCE = 上記から論理的に導いた推定であり、直接のEvidenceを伴わない。

DIRECT        : [A]全9件、[B][C][D]、[E][F][G の見出し部]、本Session内[I]の
                全実装・全Test実行・実Hardware検証。
INDEPENDENT_PROVIDER : [E][F]（Codex作成）。
USER_QUOTE    : [B]第1.4節、[C]第4節、[A]内の複数の直接引用。
INFERENCE     : 2.2節の「長時間ほど劣化しうるRiskが本Session内でどの程度
                的中したか」は未確認（第三者検証が無いため）。
                4.1節のHuman Decision Burden Minimizationは、参照Source内に
                直接該当するEvidenceが薄く、他の類似Session記録からの外挿
                に近い。

未確認事項（断定を避けた項目）:
  - [A]系列の9件Anomalyが、本Repository全体で発生したClaude側Failureの
    「全数」か「氷山の一角」かは確認できない（記録される基準・閾値が
    明文化されていないため）。
  - Resource Efficiency（4.1節）の実際の定量比較（Token消費量、API Call数等）
    は、本評価が参照した文書内に系統的な実測記録が無く、比較Confidenceは低い。
  - 2.5節の「BLOCKED判断への転換」が、Claude自身の恒常的な傾向改善か、今回
    固有のContract設計（Codexが明示的に「真のBlockerがある場合はBLOCKEDと
    せよ」と指示した）に対する単発の応答かは、今後の複数Cycleでの再現無しに
    は判別できない。
```
