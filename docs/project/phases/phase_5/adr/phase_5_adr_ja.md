# Phase 5 ADR — Guardrail／Security／Policy／Authority

```yaml
document_id: phase_5_adr
status: accepted_frozen_ready_for_backup
phase: phase_5
language: ja
recorded_at: 2026-08-22 09:57:48 JST
implementation_authorized: false
```

## ADR-5-001：Safetyと推論品質Governanceを別Resultにする

Phase 4のMain Governance ResultとPhase 5 Guardrail Resultを統合Scoreへ潰さない。Safety／Authority Denyを品質Scoreで相殺しない。

## ADR-5-002：Deterministic First、Safety Model Optional

Rule-based／Structural Guardを正式Baselineとする。Safety Modelは交換可能な補助Evaluatorであり、UnavailableでもPhase 5 Coreは成立する。

## ADR-5-003：Guardrail ModeはPhase 3／4 Modeから独立する

Guardrailに独立した`off／observe／enforce`を持たせ、Defaultは`off`とする。一つのModeが他ComponentのAuthorityを自動生成しない。

## ADR-5-004：DetectionとPolicy／Authorityを分離する

Detector HitはActionではない。Policy Applicability、Current Authority、Approval、CapabilityおよびBudgetを通過したRegistered Actionだけを実行する。

## ADR-5-005：AIはApproval／Authorityを自己発行しない

Model、Guard Model、GD、DetectorまたはJudgeのOutputをHuman Approval／Delegation／Tool Permissionの正本にしない。

## ADR-5-006：Enforce Streamingは「後でReject」にしない

Enforce時に未検査のStream ContentをClientへ先に公開しない。Deterministic Stream GuardはBounded Holdback／Incremental Scanを使う。完全Semantic Safety Evaluationが必要な場合はDelayed Releaseとして別Capability化する。

## ADR-5-007：Secret／PII Evidenceは実値を持たない

Detection EvidenceはCategory／Detector／Policy／ActionとSafe Countに限る。検出したSecret／PIIのHashであっても通常Evidenceに保存しない。

## ADR-5-008：Typed Redactionだけを実行候補にする

Redactionは明示的なTyped Span、Policy、Authority、Overlap検証および原文完全性が成立する場合に限る。不明な場合は捛造修正せずReject／Approval Requirementへ収束する。

## ADR-5-009：Public／Basicは自動的に保護済みにならない

Phase 5実装の存在だけでPublic／Basic／Lightning／AWSをSafeまたはProtectedと表記しない。Profile BindingとDeployment Acceptanceは別Gateとする。

## ADR-5-010：Phase 6 Judge／Repairを前倒ししない

Phase 5はHallucination／意味的品質の判定や自動再生成を実装しない。Phase 6が返すJudge／Repair ResultもPhase 5 Safety／Authority Denyを上書きできない。

## ADR-5-011：Claudeは5-G COMPLETE_CANDIDATEで停止する

ClaudeはPhase 5-0～5-Gを連結実行できるが、5-H、Git、Phase 5-EX AWSおよびPhase 6へ自動進行しない。

## ADR-5-012：Phase 5 Closureは軽量、Phase 6後にProgram統合Review

Phase 5ではRecovery、実測Test、Open Major Finding、User Gateを残しながら最小Closureとし、Phase 4～6の全体整理はPhase 6完了時に行う。
