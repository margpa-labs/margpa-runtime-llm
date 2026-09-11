# Phase 10予約 — PADG Package後／UI大改造前のGovernance・Constitution構造制御／意味評価レイヤー

```yaml
document_id: phase_10_post_padg_governance_constitution_structural_and_semantic_layers_before_ui_reservation_20260910083725
document_type: planned_work_architecture_and_sequence_reservation
document_state: accepted_user_direction_not_started
language: ja
recorded_at: 2026-09-10 08:37:25 JST
decision_authority: user
authority_owner: Nazuna Research
target_phase: phase_10
execution_boundary: after_padg_package_before_major_ui_rework
phase_10_plan_changed: true
implementation_authority: not_granted_by_this_reservation
git_authority: not_granted
append_only: true
supersedes_schedule_only:
  - phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_20260902214032
  - phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_20260904172003
retains_architecture_from:
  - runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_20260829114640
  - phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_20260902214032
  - phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_20260904172003
```

## 1. 今回のUser Decision

Phase 11以降へ予約していた次の構造制御レイヤーを、Phase 10へ前倒しする。

1. Main Runtime Governanceの構造制御レイヤー。
2. Runtime Constitutionの構造制御レイヤー。

両方とも、Judge、Repairその他の別Componentを必須前提にせず、Main Modelの入力構築、生成条件、出力制約または実行許可へ直接作用する独立経路として成立させる。

あわせて、Phase 10で予定するRuntime ConstitutionのJudge併用・意味評価レイヤーを同じBackend設計境界で整備する。ただし、三つを一つの密結合Componentへ統合するのではなく、次の独立経路として扱う。

```text
A. Main Runtime Governance Structural Control
B. Runtime Constitution Structural Control
C. Runtime Constitution Semantic Evaluation（JudgeはOptional Adapter）
```

実施時期は、Portable Autonomous Development Governance Package（PADG Package）完成後、Phase 10の大規模UI再設計へ着手する前とする。

## 2. 変更される実施順序

```text
Phase 9-2 User Manual／Phase 9 Closure境界
        ↓
Phase 10 Docs統合・Constitution材料整理
        ↓
Portable Autonomous Development Governance Package（PADG Package）
        ↓
Governance／Runtime ConstitutionのRule分類と実行Contract確定
        ↓
Main Runtime Governance Structural Control
        ↓
Runtime Constitution Structural Control
        ↓
Runtime Constitution Semantic Evaluation＋Optional Judge
        ↓
独立稼働／組合せ／Failure／Evidence Matrix
        ↓
Phase 10 Settings・右Panel・Main UI大改造
```

実装時には依存関係に応じて三経路の一部を並行設計してよいが、PADG Package完成前またはUI Contract確定後の後付け工事として無計画に開始しない。

## 3. 前倒しする理由

- Platformの主要価値は、Main、Main Governance、Constitution、Judge、Guard、Repairその他を独立して組み合わせ、実験・検証できる完全疎結合性にある。
- Backendの最終Component構成、Mode、状態、EvidenceおよびFailure表現を確定してからUIを作る方が、UIの二重改造を避けられる。
- UIを先に固定すると、構造制御と意味評価、現在設定と当該Turn実測、実行なしと未観測を後から無理に同じ表示へ押し込むRiskが高い。
- Main Governance／Runtime Constitutionの構造制御がJudgeなしで動く状態は、単なるUI上の差ではなくPlatform Architectureの中核である。
- MVP最短を維持しつつ、Phase 10成果を見た目だけでなく独自の統治・検証基盤として成立させるには、UI大改造前にBackend Contractを固定する方が全体工数を抑えやすい。

## 4. 三経路の責務

### 4.1 Main Runtime Governance Structural Control

- ARGD／DAGDその他のGovernance Definitionから、Runtimeで直接適用可能な構造制約を扱う。
- Main Modelの入力、Context構成、許可Action、生成条件、出力形式その他へ直接作用する。
- JudgeがOFF、不在、未Load、失敗またはUnsupportedでも単独で稼働できる。
- Ruleが登録・Bindされていることだけを「矯正成立」としない。実際に何を制約、変更、拒否または許可したかをEvidence化する。
- 意味理解が必要なRuleをPatternへ縮退させて構造制御済みと偽らない。

### 4.2 Runtime Constitution Structural Control

- Runtime Constitutionの各条文から、Main ModelまたはAgent／Tool実行へ直接適用可能な構造制約を扱う。
- Main Runtime Governanceとは別Component・別Authority・別Evidenceのまま維持する。
- Judge、Main Governance、Repairその他がOFFでも、Constitution Structural Control自身の成立範囲で単独稼働できる。
- PADG PackageやShared Development Constitutionを読んだだけで、製品Runtime ConstitutionへAuthorityまたはBindingを自動生成しない。

### 4.3 Runtime Constitution Semantic Evaluation

- 内容がConstitutionへ意味的に適合するかを、交換可能なEvaluator Adapterを介して評価する。
- Judgeを使用できるが、特定Model、ProviderまたはMain GovernanceへHard-codeしない。
- Judge OFF／不在／失敗時は、意味評価の`not_run`、`unavailable`またはTyped Failureを正直に示す。Structural Controlまで一括停止しない。
- 必要な場合だけRepair Requestを生成し、Repair結果を同じFrozen Rule／Criterionで再評価する。
- 正常Decodeされた評価内容が気に入らないことを理由にRetry、再評価または成功選別を行わない。

## 5. 完全疎結合Invariant

- Main Runtime GovernanceとRuntime Constitutionを親子関係にしない。
- Structural ControlとSemantic Evaluationを同じMode、同じ成功表示または同じFailureへ畳み込まない。
- JudgeはSemantic EvaluationのOptional Adapterであり、Structural Controlの起動条件にしない。
- Repairは明示的なRequestがある場合だけ起動する。Repair ModeがONという事実だけでRequesterを捏造しない。
- Guard、RAG、Recording、Presentation、Definition RoutingおよびDevelopment Agentを暗黙の必須依存にしない。
- ComponentがOFF、不在またはUnsupportedの場合、そのComponentのCall、Mutation、AuthorityおよびEvidenceを0にする。
- 一つのComponent Failureを他Componentの成功、失敗または未実行へ書き換えない。
- Provider／Model固有処理はAdapterへ置き、CoreへModel名やProvider名を固定しない。
- 通常Chatの全Component OFF経路を変更しない。

## 6. Rule分類

ARGD、DAGDおよびRuntime ConstitutionのRuleを、少なくとも次へ分類する。

```text
structural_applicable
semantic_required
hybrid_structural_and_semantic
unsupported_or_not_yet_classified
```

全Ruleを構造化できるという前提を置かない。同じRuleが構造的制約と意味評価の両方を必要とする場合、それぞれの適用結果、評価結果およびEvidenceを分離する。

現行ARGD／DAGD 109 Criterionが全てSemanticへ委譲されていたという旧実装Evidenceは、Userの本来意図に構造制御可能なRuleが存在しない証明ではない。Phase 10着手時に、現行定義と意図を再分類し、変換可能数、未対応数および理由を再導出する。

分類結果により総工数が変わっても、都合よく全件Structural対応済みと表示しない。Phase 10で成立させるCoverageと後続へ残すCoverageを、要件定義時に明示する。

## 7. EvidenceとMode表示

少なくとも次を別状態として保持する。

- Structural Rule selected／bound／applied／blocked／not applicable／failed。
- Semantic Criterion selected／evaluated／passed／deviated／unknown／not applicable／deferred。
- Configured、Active、Executed、Evaluated、Recorded Provider Identity。
- Structural Controlの実行結果。
- Semantic Evaluationの実行結果。
- Repair requester、Repair call、Repair outcome、Re-evaluationおよび採否。
- Candidate、Repaired Candidate、Final Presented Result。
- Frozen Mode、Rule Revision、Criterion Revision、Budget、Failure Reason。

Structural Controlだけが動作した状態を「全Constitution RuleのENFORCE成立」と表示しない。Semantic Evaluationが未実施でもStructural Controlの実績を消さず、逆にSemantic PASSからStructural Control適用を推定しない。

## 8. Phase 10 UI大改造との関係

UIは三経路のBackend Contractと保存Evidenceが固まった後に設計する。

最低限、次を独立表示できる構造にする。

- Main Runtime Governance Structural Mode／Result。
- Runtime Constitution Structural Mode／Result。
- Runtime Constitution Semantic Evaluation Mode／Result／Evaluator。
- Judge、Repair、Guardその他の独立状態。
- 当該TurnのFrozen実効値と現在のLive設定。
- `not_run`、Call 0、未観測、Unavailable、Failed、Completed、Pass／Deviationの差。

一つの`Governance ENFORCE`または`Constitution Mode`へ全状態をまとめず、どのレイヤーが実際に作用したかを確認できるようにする。

## 9. Acceptance候補

Phase 10着手時に詳細化するが、少なくとも次を実証対象にする。

1. Main Governance Structuralのみで、Judge Call 0のままMainへの直接制約が実際に作用する。
2. Runtime Constitution Structuralのみで、JudgeおよびMain Governance Call 0のまま直接制約が作用する。
3. Constitution SemanticのみをJudgeへ接続できる。
4. Structural＋Semanticを併用しても結果とAuthorityが混線しない。
5. Judge OFF／Unavailable／Failureでも両Structural経路が継続できる。
6. Main Governance OFFでもConstitutionが独立し、Constitution OFFでもMain Governanceが独立する。
7. Repairなし、Judge起点Repair、Main Governance起点Repair、Constitution起点Repairおよび複数Requesterを区別する。
8. 全Component OFFの通常Chatに無言のCall、MutationまたはEvidenceを追加しない。
9. Fixture、Integration、実Model、Browser／User Manual Evidenceを混同しない。
10. Settings／右Panelで、現在設定と当該Turnの実行状態を分離して確認できる。

## 10. MVP境界

本前倒しは、Phase 11以降の全研究項目をPhase 10へ移す決定ではない。次は別途判断する。

- 全Ruleを高度なDeterministic Compilerへ変換すること。
- Model Weight変更、Fine-tuningまたは再学習。
- 外部中立Evaluator、分散Node、複数Provider Arbitration。
- 完全なSelf-improving Constitution。
- 全業界向けPolicy Pack。
- Phase 10 MVPに不要な大規模性能最適化。

ただしMVPを理由に、三経路を再び密結合させたり、Structural Controlを単なる表示・Bind確認へ縮退させたりしない。

## 11. 既存予約との関係

今回更新するのは実施時期とPhase順序である。次の既存技術要件は維持する。

- `docs/project/shared/history/planned_work/phase_11_plus_governance_enforce_structural_semantic_layer_split_reservation_ja_20260902214032.md`
- `docs/project/shared/history/planned_work/phase_11_plus_governance_and_runtime_constitution_layer_split_reservation_ja_20260904172003.md`
- `docs/project/shared/history/planned_work/runtime_constitution_normal_chat_agent_tool_loose_coupling_and_hardcode_avoidance_reservation_ja_20260829114640.md`

次の旧Schedule表現は本DecisionでSupersedeする。

- 「構造／意味評価レイヤー分離はPhase 11以降」。
- 「Phase 10 UI再設計時も前倒ししない」。
- 「Phase 10 MVP完成までは現行設計を一切変更しない」。

PADG Packageの正式名称、二周編纂、Provider-neutral Core、Project固有要素のSanitizeおよびAuthority境界は維持する。

- `docs/project/shared/history/planned_work/phase_10_ready_portable_autonomous_development_governance_package_two_pass_compilation_reservation_ja_20260828091200.md`

Phase 10 UI予約の設計方針は維持するが、同文書の「構造／意味評価分離はPhase 11以降のまま」というScheduleだけを更新する。

- `docs/project/shared/history/planned_work/phase_10_right_panel_ui_concept_consolidation_reservation_ja_20260904190434.md`

## 12. 現在のAuthority境界

本書は予約とPhase順序の変更記録であり、次を許可しない。

- Phase 10開始。
- PADG Package作成。
- Rule再分類、Source実装、Schema変更またはUI変更。
- Phase 9-2 User Manualの省略。
- Phase 9 Closureの自己承認。
- Git Add／Commit／Push。
- 外部操作、Project外Writeまたは破壊的操作。

詳細設計、工程分解、Coverage、工数、Trial回数およびAcceptanceは、Phase 10でPADG Package完成後、実Sourceと統合Docsを確認して確定する。

## 13. Exact Next Route

```text
Current                    : RESERVED / NOT STARTED
Immediate Work             : Phase 9-2 User Manualを継続
Phase 10 Entry             : 別途User Decisionが必要
Structural/Semantic Entry  : PADG Package完成後
UI Major Rework Entry      : 三経路のBackend Contract・Evidence確定後
Implementation Authority   : NOT GRANTED BY THIS DOCUMENT
```
