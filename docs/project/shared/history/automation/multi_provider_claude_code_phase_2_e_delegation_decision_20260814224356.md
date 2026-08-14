# Multi-provider Claude Code Phase 2-E Delegation Decision

```yaml
document_id: multi_provider_claude_code_phase_2_e_delegation_decision_20260814224356
status: accepted_pre_execution_decision
phase: phase_2
subphase: phase_2_e
language: ja
created_at: 2026-08-14 22:43:56 JST
from_role: User／Codexプロジェクト責任者兼設計統括者役
to_role: Claude設計統括者役
automation_scope: provider_delegated_subphase
execution_state: not_started
history_policy: append_only
```

## 1. Context

Phase 2-A～2-Dは実装、Automated ValidationおよびユーザーMac手動Acceptanceを完了した。ユーザーはPhase 2-D完了後Backupを取得済みと報告した。

Codex側の利用可能量がPhase 2-E完了後の最終Reviewに必要な余力を下回り始めたため、Routineな中間確認でCodexを消費せず、Phase 2-Eの設計・実装・再ReviewをClaude Code側へ有界委譲する方針を採用した。

この判断は、単に作業を別Modelへ移すものではない。既存のDocument-driven Role Authority、Append-only Evidence、Stable／History分離およびFinal Review Gateを、複数Provider間でも維持できるかを実運用で確認する最初のCross-provider Delegationである。

## 2. Accepted Role Topology

```text
最高責任者:
  Codexプロジェクト責任者兼設計統括者役

Claude側Controller:
  Claude設計統括者役

Claude側Delegated Roles:
  Claude Phase 2-E設計担当者役
  Claude Phase 2-E実装者役

Return Route:
  Claude COMPLETE_CANDIDATE
    → Codex最終Review
    → ユーザーMac手動Acceptance
```

Claude Codeが独立Taskを利用できる場合はRole単位で分離する。利用できない場合も、Role Transition、From／To、Write ScopeおよびReview ResponsibilityをEvidence上で分離する。

Codex側最高責任者は、Phase 2-E実行中のRoutine確認へ毎回介在しない。Claude側は自身のAuthority内でRecovery、Design、Review、Freeze、Implementation、Test、ReworkおよびFinal Reviewを連結し、`COMPLETE_CANDIDATE`または真のCurrent Transition Blockerの場合だけCodexへ返す。

## 3. Repository-native Provider Handoff

一時的な長文Prompt貼付を正本にせず、Repository内のProvider Bootstrap PackageをClaude Codeの入口とする。

- `docs/project/phases/phase_2/handoffs/claude_code/phase_2_e_claude_design_governance_index_ja.md`
- `docs/project/phases/phase_2/handoffs/claude_code/phase_2_e_claude_design_governance_handoff_ja.md`

Claude Codeへ渡す会話上の指示は、上記2文書を順番どおり全文読んで実行することだけで足りる。Recovery Source、Reading Order、Authority、Forbidden Scope、Completion ContractおよびReturn RouteはRepository内で管理する。

この方式により、Provider変更、Task再作成、Context消失または長期継続時も、過去の会話本文を再度手作業で編集・貼付せず、同じ正本入口から復元できる。

## 4. Claude Documentation Boundary

Claude側の設計、Handoff、Status、Review、CorrectionおよびCompletion Evidenceは、Timestamp付き新規FileとしてHistoryへAppend-onlyで作成する。

既存Stable文書はClaude側で絶対に変更しない。対象にはCurrent、Shared、Public、Phase 2 IndexおよびPhase 2 Stable Requirements／Architecture／Governance／ADR／Handoffs／Operationsを含む。

Claude完了後、Codex最高責任者がDiff、設計、TestおよびBoundaryをReviewし、Stable文書へ統合すべき内容だけを通常のSnapshot／History運用で反映する。

この分離により、Claude側の作業証跡をLosslessに保持しながら、複数Providerが同時にStable正本を書き換える競合を防ぐ。

## 5. Phase Routing Decision

```text
Phase 2-E:
  Claude Code側でDesignからCOMPLETE_CANDIDATEまで実行する。

Phase 2-F:
  Claude HandoffをCodexが最終Reviewし、ユーザーMac手動Acceptance後、Codex側で別途開始する。

Lightning:
  Phase 2では追加反映しない。
  Phase 3またはPhase 4完了後に、別の設計・権限・手動試験Gateで再開する。
```

Phase 2-E Handoffは、Phase 2-F、Git、GitHub、Lightning、External ServiceまたはStable Docs更新のAuthorityを生成しない。

## 6. Resource-aware Delegation Principle

複数Provider運用では、最高責任者Providerを全Routine工程へ細かく挟むことを安全性と同一視しない。最高責任者の利用可能量をFinal Review、重大Rework、Human Gateおよび次Phase判断へ残し、委譲Providerは与えられたSubphase Authority内を完遂する。

```text
Routine Design／Implementation／Rework:
  Delegated Provider内で解決する。

Final Conformance／Cross-phase Decision:
  Highest-responsibility Providerへ返す。

Authority Expansion／Root外／External／Secret／Irreversible:
  Delegated Provider内で許可しない。
```

これはProvider固有のHard-codeではない。将来Claude Code以外のProviderを追加する場合も、共通Canonical Ruleを複製せず、Provider別の短いRecovery Index／Handoff、Role ViewおよびAppend-only Return Evidenceによって接続する。

## 7. Current State／Next Action

```text
Codex Bootstrap Docs : CREATED
Claude Execution     : NOT STARTED
Phase 2-E            : WAITING FOR CLAUDE START
Phase 2-F            : NOT AUTHORIZED
Lightning            : DEFERRED UNTIL AFTER PHASE 3 OR 4
Git Mutation         : NOT AUTHORIZED BY THIS DECISION
```

ユーザーはClaude Codeでの実行を翌日以降に開始する予定である。開始時はBootstrap IndexとHandoffをClaude Codeへ指定し、Claude側は記載されたStartup Integrity Gateを通過後にPhase 2-Eを開始する。

## 8. Evidence Value

本Decisionから、今後のAutomation／Constitution設計へ次を蓄積する。

- Providerが異なってもRole AuthorityとStable／History境界を維持できるか。
- Repository-native Recoveryによって会話Contextへの依存を減らせるか。
- 最高責任者ProviderのHuman Decision Burdenと利用可能量を削減できるか。
- Delegated Provider内のDesigner／Implementer／Reviewer分離が成立するか。
- `COMPLETE_CANDIDATE` Return ContractだけでLossless Final Reviewが可能か。
- Provider固有AdapterとProvider-independent Governanceを分離できるか。

Phase 2-E完了後、成功、失敗、Near Miss、逸脱、Recovery Cost、Review差戻しおよび利用可能量への効果を追加のAppend-only Evidenceとして記録する。
