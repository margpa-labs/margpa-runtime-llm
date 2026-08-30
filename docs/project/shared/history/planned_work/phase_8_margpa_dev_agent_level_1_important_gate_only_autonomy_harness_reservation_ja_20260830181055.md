---
document_id: phase_8_margpa_dev_agent_level_1_important_gate_only_autonomy_harness_reservation_20260830181055
document_type: append_only_planned_work_design_refinement
document_state: reserved_not_started
language: ja
recorded_at: 2026-08-30 18:10:55 JST
decision_authority: user
authority_owner: Nazuna Research
target:
  - phase_8_research_preview_foundation
  - level_1_formal_completion
implementation_authorized: false
---

# MARGPA Dev Agent Level 1 — 重要Gate限定Autonomy Harness予約

## 1. 決定

`MARGPA Development Agent`／`MARGPA Dev Agent`は、Level 1段階から可能な限り、
現在のUserとCodex Controller Taskに近い操作感を目標にする。

```text
安全で事前Scope内の通常作業
→ 逐次確認せず自走

重要Gate
→ Userへ確認

Platform／OS／Access Control上の最終Safety Gate
→ Harness設定にかかわらず維持
```

Phase 8では完成級Level 1を主張しないが、このUXを後付けにせず、Research Previewの
Approval／Autonomy Harness、Authorization Envelope、Run StateおよびEvidence Schemaへ組み込む。

## 2. 目標User Experience

UserはAgentへ目的、Scope、予算、禁止事項および重要Gateを最初に渡す。その後、Agentは
Accepted Envelope内で設計補助、実装、Test、修正およびRecoveryを連結実行し、各Fileや各Commandで
Userを拘束しない。Userは別作業を行い、重要Gate到達時だけ判断する。

```text
User Input
→ Goal／Scope／Authority／Budget／Stop Conditions／Important GatesをFreeze
→ AgentがEnvelope内を自走
→ EvidenceとProgressを非Blockingに記録
→ Important GateでだけUserを呼ぶ
→ 承認／修正／拒否後に再開
```

これは「何でも自動承認」ではない。安全性と権限境界を先に構造化し、その内側では
Approval Fatigueを発生させない設計である。

## 3. Phase 8 Harness Profile候補

### 3.1 Manual Approval

各Side Effect前に確認する比較Baseline。Public Demoまたは初回学習用Profile候補。

### 3.2 Risk-based Approval

Read-only、Workspace内、可逆的、BoundedなActionは自走し、Risk Classが閾値を超えた場合だけ確認する。

### 3.3 Envelope Autonomous／Important-Gate Only

Userが事前承認したExact Envelope内では、定義済み重要Gateまで確認しない。Owner Research Profileでは、
現在のUser／Codex運用に近い本Profileを主要候補とする。

### 3.4 Plan Only

計画、差分候補および必要Authorityだけを作成し、Mutationを実行しない。

Public DemoのDefaultとOwner Local ProfileのDefaultは分離可能にする。Public利用者へ危険Profileを
暗黙適用せず、Owner自身のResearch Environmentでは明示Opt-in後にGate-only運用を利用できるようにする。

## 4. 確認しないAction Candidate

Accepted Envelope、Tool Capability、ConstitutionおよびPlatform Boundaryをすべて満たす場合、
次を逐次確認なしで実行可能な候補とする。

- 許可Workspace内のRead／Search。
- Userが依頼したScope内のSource／Test／Docs編集。
- Project内の可逆的File作成。
- 事前定義した非破壊Test／Typecheck／Lint／Build。
- Project-owned Temp／Cacheの作成と、Exact Ownershipが証明された範囲のCleanup。
- Recovery Index、Progress EvidenceおよびHandoff作成。
- 失敗後のBounded Retry。
- Accepted Findingに対するScope内Rework。

Action名だけで許可せず、Target Root、Side Effect、Budget、Retry、TimeoutおよびRecoveryを含む
Capability Contractで判定する。

## 5. Important Gate Candidate

少なくとも次はUser確認候補とする。

- Accepted ScopeまたはWorkspace Root外へのWrite。
- 削除、上書き、Rollback等の不可逆または復旧困難なAction。
- Network送信、外部Service変更、Message送信または第三者への影響。ただし事前承認Envelope内の限定Actionは別Tierで扱える。
- Secret、Credential、個人情報または機密Dataを扱うAction。
- Git Commit／Push／PR／Release／Deploy等の公開・共有State変更。
- 購入、課金、Quota消費または高Cost Action。
- Authority拡張、Provider／Role変更または新しいAgent／Tool生成。
- Requirements、ArchitectureまたはUser意図を実質的に変えるScope拡大。
- Data Loss、Security、Legal、Privacyまたは重大Incidentの疑い。
- Budget、Step、Time、RetryまたはContext Limit到達。
- Completion／Closure／Production昇格等のHuman Acceptance Gate。

Gate表示は「許可しますか」だけでなく、理由、対象、予想Side Effect、Recovery可能性、Cost、
許可範囲および選択肢を短く提示する。

## 6. HarnessとPlatform Safetyの分離

MARGPA HarnessがActionを許可しても、OS Sandbox、Filesystem Permission、Provider Platform Gate、
Access Control、法令または外部Service Policyを解除しない。

```text
MARGPA Harness Allow
≠ OS／Platform Bypass
≠ Secret／Privacy Bypass
≠ 存在しないAuthorityの生成
```

Provider側の強制確認が発動した場合は、Harnessが勝手に承認せず、Runを`WAITING_FOR_PLATFORM_GATE`等の
明示Stateにする。Gate解決後、同一Run／Step／Evidence Identityから再開可能にする。

## 7. State／Evidence Candidate

最低限、次を区別する。

```text
PLANNED
AUTHORIZED_WITHIN_ENVELOPE
RUNNING_WITHOUT_INTERACTION
WAITING_FOR_IMPORTANT_GATE
WAITING_FOR_PLATFORM_GATE
REJECTED
CANCELLED
FAILED
COMPLETED_CANDIDATE
```

各Actionには、Run ID、Step ID、Capability ID、Target、Frozen Envelope Revision／Digest、
Approval Profile、Risk Class、Gate Reason、Actor、開始／完了、OutcomeおよびRecovery Pointerを保持する。

## 8. Anti-pattern

- 安全なWorkspace内Actionまで毎回確認し、UserをAgent監視へ拘束する。
- 「自己責任Mode」を理由に全Safety境界を解除する。
- Allow／DenyをTool名だけで判定し、TargetやArgumentを見ない。
- 軽微なNear Missごとに全Runを停止する。
- Gateを避けるためにActionを分割、言い換えまたは別Toolへ迂回する。
- 一度の許可を無関係な将来Taskへ無期限継承する。
- UI上のMode表示だけで実Authority成立を主張する。

## 9. Acceptance Candidate

1. SafeなWorkspace内Taskを複数Step連結しても、不要な確認Dialogが発生しない。
2. UserはLong Run中に別作業を行え、重要Gateだけで呼ばれる。
3. Envelope外Actionは実行前に停止する。
4. Platform強制GateをBypassしない。
5. 一時許可と永続Policyを混同しない。
6. Risk／Target／Costの違いに応じてGateが変わる。
7. Gateには対象と影響が理解可能な日本語で表示される。
8. Reject／Cancel後に遅延Side Effectが発生しない。
9. Gate解決後、同一Runから重複実行なしで再開できる。
10. Public DemoとOwner Research ProfileのDefaultを分離できる。

## 10. Source Evidence

本設計予約は、次の実測を主Sourceとする。

- `docs/project/shared/history/automation/codex_workspace_scoped_autonomy_and_important_gate_only_approval_empirical_evidence_ja_20260830181055.md`
- `docs/project/shared/history/automation/claude_phase_7_build_artifact_omission_and_platform_safety_gate_observation_ja_20260830175855.md`

CodexとClaudeの現行挙動をそのままHard-codeせず、Provider非依存のCapability、Envelope、Risk、Gate、
StateおよびEvidence Contractへ抽象化する。

## 11. Authority

本書は設計予約であり、Phase 8開始、Agent実行、Tool Authority、Network、Git、外部Actionまたは
Harness Bypassを許可しない。Phase 8 Design／Preflightで、PoC／MVPに必要な最小Surfaceへ工程分解する。

