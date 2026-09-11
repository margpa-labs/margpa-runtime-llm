# Phase 9-2 全範囲 Independent Review 3 — Acceptance Truth Rework Handoff

- 作成: 2026-09-09 02:21:25 JST
- 判定: `CHANGES_REQUIRED`
- Review観点: 要件から実装・実行・Comparisonまでの主張可能範囲
- 対象: Phase 9-2全範囲
- 修正対象: Blocker 1件、Major 2件

## 1. Review成立条件

Independent Review 1の4件およびIndependent Review 2の3件は、各Rework後のSource確認とController Focused TestでPASSした。本Reviewは両Reviewと観点を重ねず、P9-REQ-201〜209／P9-ACC-039〜045を「型や単体Classifierが存在する」ではなく「Versioned CaseをPlan→Run→Evidence→Comparisonへ通し、その結果を正直に比較できる」の意味で再監査した。

## 2. Confirmed Findings

### IR-P9-2-WHOLE-R3-01 — BLOCKER

`classify_freshness_answer()`は`SourceRevisionState.CURRENT`でHistorical Citation Digestが不変なら、回答本文がCurrent Source Valueを含まなくても無条件に`CURRENT_FACT_USED`を返す。さらにWebの選択可能Freshness Caseはこの`CURRENT` Caseを使うため、`"I am not sure."`のような回答でもComparisonが`PASS`になることを既存Test自身が正例として固定している。

要求:

- `CURRENT`でも回答がCurrent Source Valueを実際に使った場合だけ`CURRENT_FACT_USED`とする。
- Current Value不使用、無関係回答、空／Evidence不足をPASSにしない。
- Updated／Deletedの既存判定およびHistorical Citation改変の最悪判定を維持する。
- 実`evaluate_case_outcome()`とTop-level Fixture Comparison経路でFalse PASSが消えることをSabotage付きで証明する。

### IR-P9-2-WHOLE-R3-02 — MAJOR

P9-REQ-205〜207／P9-ACC-042〜043で必要なSource Updated／Deleted、Relevant／Irrelevant Hit、NO_HIT差、Source Authority／Correction／Belief RevisionのDomain Objectは存在するが、多くがRevision付き`EvaluationCaseManifest`としてCase Packへ入らず、Preset Case→Plan→Run→Comparisonの実行経路へ接続されていない。Acceptance Testは孤立したClassifierを直接呼ぶだけで、Comparisonの`false_positive`／`false_grounding`／`correction_acceptance`は実Runで常に未観測のままになり得る。

要求:

- 必須Semantic CaseをRevision付きCase Manifestとして識別可能にし、Case固有Evidence／Evaluatorへ明示的にRoutingする。
- 少なくともFreshness Updated、Source Deleted、Relevant Hit、Irrelevant Hit、NO_HIT with call、Strict NO_HIT Call 0、Belief Revision／Correction、False Improvementを、要件どおり比較可能なTop-level Deterministic Fixture経路へ接続する。
- False-positive／False-grounding／Correction Acceptance等は実Evidenceから導出できる時だけ値を持ち、未観測を`False`へ潰さない。
- 同一Case Revision、Run／Case／Rubric Identity、再起動後Comparison Readを維持する。

### IR-P9-2-WHOLE-R3-03 — MAJOR

P9-REQ-202〜204／208〜209、P9-ACC-040〜041／044〜045の一部が、孤立したDomain Unit Testに留まる。現`ComparisonReport`はBaseline／Regression／Ablation Declarationを持たず、Multiple Definition／Routing差、Strict Buffer／Progressive、Manual URL Fail-closed Call 0はPlan→Run→Comparisonへ接続されていない。特にAcceptance MappingのCall 0 Testは`ExecutionTraceProjection`を手で構築しており、実Adapter CounterまたはRun Evidenceを裏付けていない。

要求:

- P9-2の公開済み最小Experiment経路で、代表的なMain／Judge／Guard／Main Governance／Definition・GD／RAG／Repair／Mode差を同一CaseのVariantとして実行・比較できるようにする。Productionで未対応のComponentを偽装せず、FixtureとProductionの境界は維持する。
- Baseline／Regression／Ablationの関係と実際の単一要因差を、Comparisonの永続Artifactから読めるようにする。複数要因差を単一要因効果として表示しない。
- Multiple DefinitionのMatch／Conflict／Suppression、Manual／Static／Dynamic RoutingおよびRepair要求元を、比較対象RunのEvidenceへ接続する。
- Strict Buffer／Progressiveの状態列と、Manual URL Fail-closed／Strict NO_HIT／Guard short-circuitのCall 0を、手作りProjectionだけでなくTop-level Fixture Actor／Execution EvidenceからComparisonへ通す。
- P9-REQ-201〜209／P9-ACC-039〜045のFixture MatrixをTop-level実行でHard Assertし、単体型生成だけをAcceptance PASSに数えない。

## 3. Scope／設計境界

- 上記3件を満たす最小の汎用結線と回帰Testだけを実装する。Phase 10 UI大改造は行わない。
- Model／Provider／Case固有条件をExperiment CoreへHard-codeせず、Case／Actor／Evaluator Adapter側へ置く。
- Fixture結果をReal Model結果と表示しない。未観測を0／False／PASSへ変換しない。
- 通常Chat、Phase 9-1基盤、Data Controlsへ影響を波及させない。
- 実Model、Browser実画面、User Manual、Phase 9-3、Phase 10、Git write、Commit、Push、Cleanは禁止。
- Phase 9-2 Complete／Closureを自己承認しない。

## 4. Verification／Return

1. 各Findingの修正前再現と修正後Hard Assert。
2. Top-level Fixture Plan→Run→Evidence→ComparisonのAcceptance Matrix。
3. Restart Read、Identity、False-success、Call 0、Fixture／Production分離の回帰。
4. Phase 9-2 Backend／Frontend範囲Test、Ruff、Mypy、Frontend test／typecheck／lint／build。
5. 新規主要Oracleを修正前相当へ戻すSabotageで検出力を確認し、完全復元する。
6. 新規PathのExact ReturnとRecoveryをAppend-onlyで作る。既存文書を上書きしない。
7. 中間報告は禁止。完了時はController Taskへ必ず最終報告し、その後停止する。

