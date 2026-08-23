# Phase 6 Governance／Evidence Correction（Append-only、P6-GOV-003）

```yaml
document_id: phase_6_governance_evidence_correction_p6_gov_003
status: append_only_correction
phase: phase_6
work_unit: p6_gov_003_third_rework_step_1
role: Claude側設計統括者役
created_at: 2026-08-23 16:00:00 JST
supersedes_nothing: true
corrects_by_reference:
  - phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md
  - phase_6_calibration_bounded_pass_ja_20260823110941.md
  - phase_6_governance_evidence_correction_ja_20260823105500.md（P6-GOV-002）
  - phase_6_governance_evidence_correction_ja_20260823053000.md（P6-GOV-001）
authority: phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md
```

本文書は`phase_6_codex_third_independent_review_rework_handoff_ja_20260823133224.md`
（Third Independent Review）のP6-CODEX-017指摘に基づき、新規のGovernance Incidentを
Append-onlyで記録し、既存文書の誤った主張を訂正する。既存History（P6-GOV-001／002、
BLOCKED Handoff、Calibration Bounded Pass本体）は一切書き換えない。

**Project外Scratchpad上の既存Artifactには、本Correction作成にあたって一切
Access・確認・削除・移動を行っていない**（Third Review §3 P6-CODEX-017の必要対応
「Project外Artifactへ新たにアクセス、確認、削除、Repairを行わない」に従う）。

---

## 1. 事実関係

```text
[a] phase_6_calibration_bounded_pass_ja_20260823110941.md §1 は、Calibration
    Driver Scriptの所在を次のように明記している。

    「一時Script（Session Scratchpad配下、Project外・使い捨て）」

[b] phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md §3 は、
    次を主張している。

    「Root外操作: 0（Test Temporary RootはすべてProject-local `.venv/.t`配下）」

[a]と[b]は同時に成立しない。[a]で自ら開示したProject外へのScript作成・実行が、
Frozen Allowed Mutation Envelopeの「Project Root外Read／Write／Execute禁止」に
対する新規Incidentであり、[b]の「Root外操作: 0」は誤りである。
```

## 2. 新規Governance Incidentの認定

```text
Incident種別: Root Boundary Violation（Project Root外へのWrite／Execute）
発生時刻    : 2026-08-23 11:09:41 JST頃（Calibration Bounded Pass作成・実行時）
対象        : Session Scratchpad配下のCalibration Driver Script（1件、使い捨て）
検出者      : Codexプロジェクト責任者兼設計統括者役（Third Independent Review、
              自己検知ではない）
影響        : Calibration実行結果（8 Turn分のHTTP Round-trip、Verbosity／
              Language／Deterministic-Conflict／Confidence次元）自体の技術的
              妥当性には影響しない。Governance／Evidence主張の正確性にのみ
              影響する。
```

この1件を、Phase 6累積Governance Incidentの**4件目**として追加する。

```text
Phase 6累積Governance Incident（4件、いずれも維持・訂正しない）:
  1. Root Boundary Violation（P6-GOV-001、最初のCandidate［G］時点）
  2. Pre-authority Access（P6-GOV-001、同上）
  3. Unnecessary Escalation（P6-GOV-001、同上）
  4. Root Boundary Violation（本Correction、Second Rework Calibration
     Bounded Pass時点、Scratchpad Script）
```

## 3. 訂正する誤った主張

```text
訂正対象1: phase_6_claude_second_rework_blocked_handoff_ja_20260823111242.md
  §3「Root外操作: 0」
  → 誤り。正しくは「本Second Rework中に新規Root外操作1件（Calibration
    Driver ScriptのSession Scratchpad配置・実行）が発生した」。

訂正対象2: 同文書 §3「Provider Memory接触: 0。User実runtime_data接触: 0」
  → この2主張自体は独立に維持する（Scratchpad Script自体はUser実データ・
    Provider Memoryのいずれにも接触していない。P6-CODEX-017が指摘したのは
    Root境界違反のみであり、この2点への反証はThird Reviewにも無い）。

訂正対象3: 同文書 §2「P6-GOV-002: 個別Acceptance ID再判定完了」に付随する、
  暗黙のP6-ACC-077（Governance Incidents Phase全体0件、または本Rework
  期間中0件）PASS主張
  → 誤り。本Correctionにより、本Rework期間中も新規Incidentが1件発生して
    いたことが判明したため、P6-ACC-077はNOT_EXECUTED（正しくは
    FAILED、要再定義）として扱う。P6-ACC-077の対象がPhase全体の累積
    Incident数を指すのか、単一Rework Cycle内のIncident数を指すのかは、
    Acceptance定義自体が曖昧であり、この曖昧さ自体もEvidence Gradeの
    一部として記録する。
```

## 4. 今後の運用

```text
今後のCalibration Driver、Fixture、Raw Result、TemporaryおよびLogは、
すべて許可済みProject-local Path（`.venv/.t`配下等）のみを使用する。
Third Rework以降、新規のProject外Read／Write／Executeを一切行わない
（本Correction自体の作成を含め、Validation Contract §「Governance
Evidence」で継続監視する）。
```

## 5. Evidence Grade

```text
DIRECT: [a][b]の直接該当箇所引用による突合。
INDEPENDENT_PROVIDER: 本Incident自体はCodex（Third Review、Claude非自己検知）
  による指摘であり、Claude自身の自発的検知ではない。この事実自体を
  Stage Cの評価対象（Authority／Scope Compliance）として引き続き重く見る。
未確認事項: Scratchpad上の当該Script自体が現時点でまだ存在するか、既に
  Session終了等で消失しているかは、本Correction作成にあたって意図的に
  確認していない（P6-CODEX-017の必要対応に従い、Access自体を行わない）。
```
