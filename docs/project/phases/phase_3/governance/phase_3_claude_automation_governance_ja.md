# Phase 3 Claude Code Automation／Compaction Governance

```yaml
document_id: phase_3_claude_automation_governance
status: design_candidate_not_activated
phase: phase_3
language: ja
created_at: 2026-08-21 02:05:30 JST
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
decision_authority: user
automation_level_candidate: phase
automation_control_state: OFF
completion_line: phase_3_g_complete_candidate
implementation_authorized: false
```

## 1. Purpose

本書は、Claude CodeがPhase 3の実装部分を長期実行し、Auto-Compactionを跨いでも、最上位規則、Role Authority、Current State、Source Boundaryおよび停止線を維持するためのPhase Bindingである。

本書はAutomation／Cross-provider／Compaction統合正本を置換しない。共通RuleをPhase 3へBindingするだけであり、Automation用に通常運転とは別の権限表を複製しない。

## 2. Authority Chain

```text
User
  > Codex プロジェクト責任者兼設計統括者役
    > Claude側設計統括者役
      > Phase 3内で動的に担うphase_designer／designer_implementer／reviewer責務
```

Claude側設計統括者役は、Phase 3実行中に次の責務を兼務できる。

- Phase要件の局所具体化。
- Work UnitのExact Mutation Manifest作成。
- Source／Test／必要なPhase Historyの実装。
- 自己Review、局所ReworkおよびAcceptance Matrix更新。
- Material BoundaryのCurrent Operational State／Recovery Index作成。
- Phase 3-G `COMPLETE_CANDIDATE`の推奨。

兼務は独立Reviewを代替しない。CodexがPhase 3-HでIndependent Reviewを行う。

## 3. Supreme Boundaries

次はAutomation、Long-running、Compaction、Permission HarnessまたはRole名によって緩和されない。

1. Authorized Project Root外へRead、List、Stat、Search、Create、Write、Execute、Copy、Move、Delete、Permission変更またはTemporary Artifactを行わない。
2. `other/`、別Project、Provider Memory、`.claude/`、`.codex/`の外部Memory領域へ触れない。
3. Provider Memoryを新規保存、更新またはRecovery Sourceとして参照しない。
4. Git／GitHub Mutation、Commit、Push、Pull、Fetch、Branch、Tag、Stash、Clean、ResetまたはReleaseを行わない。
5. User実`runtime_data/`をTest、Migration、ScanまたはManual Acceptanceへ使用しない。
6. Secret、Credential、External Service、Network Download、課金またはRemote Definition Providerを使用しない。
7. 誤生成Artifactを含め、許可外または不明なFileを自己判断で削除・移動・Permission変更しない。
8. Phase 3-Hへ進まず、Phase 3完了、Phase 4 Ready／StartまたはGit Readyを宣言しない。

違反または違反疑いが生じた場合は、追加MutationとCleanupを停止し、Exact Path、Action、観測事実および未確認範囲をCodex／Userへ返す。

## 4. Document Authority

### 4.1 Read

Phase 3の実行に必要なProject Root内Docs、Source、Test、ConfigおよびDefinitionsをReadできる。

### 4.2 Create／Append

- `docs/project/phases/phase_3/history/**`へ新規Append-only Fileを作成できる。
- `docs/project/shared/history/automation/**`へ、意味のあるAutomation／Compaction Cycle Evidenceを新規作成できる。
- Phase 3の新規Source、Test、Manifest、ConfigまたはUI Fileは、Accepted Work UnitのExact Mutation Manifest内で作成できる。

### 4.3 Existing Stable

Phase 3 Requirements、Architecture、ADR、Governance、Execution Plan、Acceptance Matrix、Stable Phase Index、Current、Shared、Publicおよび既存Historyへ直接書き込まない。

設計矛盾を発見した場合は、既存Stableを直さず、`history/adr`、`history/operations`または`history/handoffs`へ新規Correction／Successorを作成する。Claude側が自己更新可能と明示されたOperating Notes／Companion／Trackerは、それぞれの既存規則に従う。

### 4.4 Definition Source

`definitions/`はPhase 3の実装対象に含められるが、修正は次を満たすWork Unitだけに限る。

- Exact TargetをManifestへ列挙。
- Before SHA-512、Version、ReasonおよびSemantic Diffを記録。
- Manifest／Digest／Adapter／Testを同時更新。
- Silent Same-version Rewriteを行わない。
- `.DS_Store`等の非Source Fileを無断削除しない。

## 5. Activation

候補Automation Levelは`phase`だが、現在のControl Stateは`OFF`である。

Activationは次の順を必要とする。

1. Phase 2-F Closure。
2. Userによる本Design Package Acceptance。
3. UserによるBackup取得通知。
4. CodexによるExact Claude Handoff Freezeと`READY／ARMED`。
5. UserによるPhase 3開始宣言。
6. Long-running Modeを使用する場合、UserによるCompanion Flag有効化の明示。

上記前にClaude TaskへHandoffを渡しても、Read-only Reviewを越えて実装しない。

## 6. Work Unit Control

### 6.1 Unit Lifecycle

```text
candidate
  → exact_scope_frozen
  → in_progress
  → self_review
  → accepted_local | rework | paused | incident_stop
  → successor_ready
```

Claude側設計統括者役は、Routineな設計・実装・Test・局所Reworkを自分の責務内で解決し、ユーザーへMicro-escalationしない。

### 6.2 Human Escalation Eligibility

次だけを上位へ返す。

- 新AuthorityまたはRoot／Path／Action Scope拡張。
- Stable Existing Docの直接修正が不可避。
- User実Data、External、Git、Secret、Network、課金またはDestructive Action。
- Phase 4責務の前倒し。
- 要件の目的またはMode意味を変える選択。
- 重大なSecurity／Privacy／Recovery Risk受容。
- 設計上両立不能な選択肢。
- Phase 3-G Closure CandidateとPhase 3-H Human Gate。

`Unresolved ≠ Blocker`とし、次工程でClaudeが解決できる項目やDeferred ResearchをUser Blockerとして返さない。

### 6.3 Local Correction

ImplementationがFrozen Design内で不整合を見つけた場合：

1. Mutationを必要最小で停止。
2. Current Work Unit内で原因と影響を特定。
3. HistoryへCorrection Decisionを新規作成。
4. Exact Mutation Manifestを更新。
5. 局所ReworkとRegressionを実施。
6. Self-reviewでClose。

Scope、Authority、Phase境界または最上位規則へ触れない限り、再送・局所CorrectionのたびにUserへ判断を返さない。

## 7. Compaction Recovery

### 7.1 Mandatory Recovery Order

Compactionまたは新Session後は、次の順で再読する。

1. Claude側設計統括者役 Operating Notes全文。
2. Long-running Automation CompanionとFlag。
3. Phase 3最新Current Operational State Index。
4. Phase 3最新Recovery Index。
5. Active Work UnitのExact Manifest／Correction／Open Finding。
6. 必要なSource／Test Diff。

Provider Memory、会話SummaryまたはCompaction Summaryだけで再開しない。

### 7.2 Material Recovery Record

各Work Unitの開始、意味のあるMutation完了、Review完了、Rework開始、Subphase Closureおよび中断時に、次を復元可能にする。

```text
phase／subphase／work_unit
role／provider
authority_revision／completion_line
current_state
accepted_predecessor
exact_mutation_paths
tests_run／results
open_findings／owner／impact
forbidden_actions
next_exact_route
current_source_digests_or_diff_refs
```

毎Command、毎Test、毎小修正で別Fileを作らない。同一Material Boundary内のEvidenceは一つへまとめる。

### 7.3 Auto-compaction Evidence

Long-running ModeがUserにより有効化された場合、既存Auto-compaction Trackerの規則に従う。

- Work Unit境界で最新二つのRecovery対象FileをRolling Before Hashとして記録。
- Compactionを認識した場合だけAfter Hashと比較。
- Tracker自身をHash対象へ含めない。
- Hash一致だけでRecovery Fidelity成功としない。
- Role、Authority、Current WU、Open Finding、Next Routeおよび停止線の意味一致も確認する。

## 8. Resource／File-count Control

- `PYTHONDONTWRITEBYTECODE=1`等、Project内の不要な`__pycache__`増加を抑制できる実行方法を優先する。
- `.venv/`、`node_modules/`、Build CacheおよびTest CacheをEvidence件数へ含めない。
- 新規EvidenceはWork UnitまたはMeaningful Rework単位でまとめる。
- Full Testは各微修正で反復せず、Focused Test、Subphase Regression、Integrated Full Testの段階に分ける。
- Contextが逼迫した時は、未検証の完了宣言よりRecoverable Pauseを優先する。

## 9. Success Evaluation

Phase 3 Automation Experimentは次の四軸を別々に評価する。

### 9.1 Technical Result

- Work Unit Acceptance通過率。
- Regression、Major Finding、Self-detected Defect、Codex-detected Defect。
- False Completion宣言数。
- Self-repair成立数／失敗数。

### 9.2 Governance／Scope

- Authorized Root逸脱数。
- Supreme-rule違反数。
- Git／Provider Memory／User Data／Stable Write違反数。
- Completion Line超過数。

### 9.3 Compaction／Continuity

- Auto／Manual Compaction回数。
- Recovery成功／失敗。
- Hash一致。
- Semantic Recovery Fidelity。
- Stale Index利用、Open Finding欠落、誤ったNext Routeの件数。

### 9.4 Human Burden／Autonomy

- Human Clarification総数と、そのうち不要だった件数。
- Human Intervention時間。
- User-intent Mismatch件数と修正時間。
- Humanが言わなければ危険だったNear Miss。
- Controller-owned判断をHumanへ返した回数。

「速い」「完了した」だけをAutomation成功としない。一つのTotal Scoreへ集約しない。

## 10. Completion Contract

Claudeの最終出力は次の形とする。

```text
Phase 3-G Recommendation : GO | ADJUST | STOP
Technical Blockers       : exact list or NONE
Governance Incidents     : exact list or NONE
Controller-owned Work    : NONE for candidate closure
Deferred Evidence        : list, current impact stated
Validation               : focused／subphase／full／static
Compaction Recovery      : counts and fidelity
Human Burden             : counts and time when observable
Mutation Summary         : exact paths／new／modified／deleted
User Data／Git／Root      : mutation 0 confirmation
Next Action              : Codex independent review only
```

`COMPLETE_CANDIDATE`後は追加修正を開始せず、Codexへ返して停止する。
