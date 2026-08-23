# Phase 6〜9 Cumulative Full Closure Scope Correction

```yaml
document_id: phase_6_to_9_cumulative_full_closure_scope_correction_20260822214404
status: accepted_append_only_correction
recorded_at: 2026-08-22 21:44:04 JST
owner_role: プロジェクト責任者兼設計統括者役
scope: phase_3_to_phase_9_closure_route
phase_6_implementation_scope_changed: false
phase_6_automation_state: ARMED_NOT_ON
git_mutation: not_performed
```

## 1. User Decision

Codex利用可能量、Review Cost、Document量およびPhase 9での研究Platform統合を考慮し、Phase 6だけでFull Documentation Closureを行わない。Phase 3〜Phase 9の累積Full ClosureをPhase 9のFinal Closureへ集約する。

Phase 3〜5はTechnical Closure済みであり、再Openしない。未実施なのはPhase 3〜5を含む累積Docs統合／Lossless／全体整合であり、これをPhase 9へ接続する。

## 2. Corrected Closure Route

```text
Phase 3〜5:
  Technical Closure                  : COMPLETE／ACCEPTED／CLOSED
  Cumulative Documentation Closure   : PENDING PHASE 9

Phase 6:
  P6-0〜P6-I Claude Execution        : FROZEN SCOPE UNCHANGED
  P6-J                               : MINIMAL TECHNICAL CLOSURE
  Cumulative Documentation Closure   : DEFERRED TO PHASE 9

Phase 7／8:
  Phase-local Implementation／Review : REQUIRED
  Minimal Technical Closure          : REQUIRED
  Cumulative Documentation Closure   : DEFERRED TO PHASE 9

Phase 9:
  Phase-local Technical Closure      : REQUIRED FIRST
  Phase 3〜9 Cumulative Full Closure  : REQUIRED
  Phase 10 READY                     : AFTER CUMULATIVE FULL CLOSURE
```

このCorrectionはPhase 6の機能要件、Model Authority、Work Unit、Acceptance、Claudeの6-I停止線またはUser Manual Acceptanceを縮小しない。変更するのは6-J以降のDocumentation／Program Closure Routeだけである。

## 3. Minimal Technical Closure Contract

Phase 6〜8では、次を省略しない。

1. Controllerの独立Review。
2. Current Acceptanceへ影響する重大Findingの解消、Reworkおよび再Review。
3. Riskに応じたBackend／Frontend／Static／Integration／実Model Test。
4. 必要なUser Mac Manual Acceptance。
5. Authority、Root外、User Data、Git、NetworkおよびExternal Boundary確認。
6. Phase Index、Current Stop Point、Recoveryおよび次Phase READYの最小更新。
7. Deferred ItemのImpact／Owner／Target Phase／Re-entry Trigger／Verification記録。
8. Phase Backupの明示勧告とUser完了報告。

これらを省略して、Phase 9のFull Closureへ問題を隠して送ってはならない。Current Phase Acceptanceへ直接影響するFindingは当該Phase内で解決する。

## 4. Phase 9 Cumulative Full Closure Contract

Phase 9のTechnical Acceptance後、少なくとも次をPhase 3〜9の累積Sourceへ対して行う。

- Phase 3〜9のRequirements／Architecture／ADR／Governance／Implementation／Test／Review／Manual Acceptance／Incident／Recovery／Handoffの累積Docs統合。
- Current／Shared／Public／Roadmap／Project Continuity／Active Indexの相互整合。
- Source Set Freeze、Path、Size、SHA-512、Manifestおよび抽出／復元可能性を伴うLossless Compilation。
- PhaseをまたぐRuntime、Governance、Guardrail、Judge／Repair、RAG、Agent／Tool、ConstitutionおよびExperiment Platformの統合検査。
- Security／Privacy／Secret／Identity／License／不要物Scan。
- Known Limitation／Deferred Evidence／Phase 10入口の再分類。
- Final Recovery Manifest、User Backup、必要なHash／Restore Evidence。
- ユーザーが別途許可したGit Workflowに従うCommit／Push／Remote一致確認。
- Phase 10 READY判定。

Phase 9 Design時に、Current Source量と利用可能量に応じてExact Work UnitとOutput構成を動的に決める。固定数のDocument Packageを先にHard-codeしない。

## 5. Evidence Reuse／Cost Control

- Phase 3〜8のAccepted Test／Review／Manual Evidenceを再利用できる。
- RiskとAs-built変更がない項目を、形式だけのために全件再実行しない。
- Phase 9 Current RuntimeからPhase横断影響がある部分は統合再検証する。
- 各小修正でFull Suite、Losslessまたは大量Docsを反復しない。
- Minimal ClosureはEvidence欠落を意味せず、累積再編成をPhase 9へまとめるCost Controlである。

## 6. Frozen Contract Relationship

Phase 6 Accepted／Frozen Coreは変更しない。本書はAppend-only Correctionとして、次の表現だけを置換する。

```text
Before: Phase 6-J Codex／User Full Closure
After : Phase 6-J Codex／User Minimal Technical Closure

Before: Phase 4〜6 Runtime Governance MVP v1のFull ClosureをPhase 6で実施
After : Phase 4〜6 Runtime Governance MVP v1のTechnical AcceptanceをPhase 6で実施し、
        Phase 3〜9 Cumulative Full ClosureをPhase 9で実施
```

ClaudeのMaximum Endは引き続きP6-I-WU-004／COMPLETE_CANDIDATEであり、本Correctionを理由にPhase 6-J、Phase 7またはPhase 9へ進んではならない。

## 7. Operational Index Integrity

```text
96387175b19c267aaf862ca9ee7fb9c65e54fcc43beb388105aa3525becbe51817f8be169868a58fe48d7cd14010138685e07e9f44d0d7d9ad7476f066e31ba6  docs/project/phases/phase_6/phase_index_ja.md
```

Design FreezeおよびActivation Receiptに記録されたPhase Index Digestは各時点のEvidenceとして保持する。本Correction後のOperational State／Closure Routeは、上記Current DigestとCurrent Phase Indexを正とする。Frozen Core 7文書のDigestは変更していない。
