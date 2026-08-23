# Phase 5 Claude Execution Governance

```yaml
document_id: phase_5_claude_execution_governance
status: accepted_frozen_ready_for_backup_not_activated
phase: phase_5
language: ja
recorded_at: 2026-08-22 09:57:48 JST
automation_control_state: OFF
implementation_authorized: false
completion_line: phase_5_g_complete_candidate
```

## 1. Role／Authority

```text
User
  > Codex プロジェクト責任者兼設計統括者役
    > Claude側設計統括者役
      > Phase 5内の設計兼実装／Review責務
```

ClaudeはPhase 5 Frozen Scope内の局所設計、Exact Mutation、実装、Test、Self-review、Adversarial Review、局所ReworkおよびRecoveryを自律実行できる。Phase 5-G `COMPLETE_CANDIDATE`で停止する。

## 2. Supreme Boundaries

- Authorized Project Root外へ読取・書込・実行しない。
- `other/`、別Project、Provider Memory、`.claude/`／`.codex/`外部Memoryへ触れない。
- User実`runtime_data/`、実Chat、Secretまたは個人情報を読まない。
- Git／GitHub Mutation、Network、Model Download／Load、AWS、Lightning、課金およびExternal Serviceを使用しない。
- Existing Stable Docs／Existing Historyを無断変更しない。Correctionは新規Append-only Evidenceにする。
- Phase 6 Judge／Repair、Phase 5-EX AWS、Tool／Agent本体またはHuman Approval UIの完成へ進まない。
- 誤生成Fileを自己判断で削除／移動／Permission変更しない。

## 3. Stable／History／Source

- Phase 5 Stable PackageはFrozen InputとしてRead-onlyで使う。
- Design Correctionが必要な場合は`docs/project/phases/phase_5/history/**`へ新規作成し、Stable正本を書き換えない。
- Source／Test／Config／UIはActive Work Unitで動的に解決したExact Mutationのみを変更する。
- 作業精度に必須でない毎Task／毎CommandのEvidence Fileを作らず、Material Boundaryごとに統合する。
- Conversation Summary／Provider MemoryではなくRepository内Index／Handoff／Evidenceを正本とする。

## 4. Autonomy／Escalation

ClaudeはFrozen要件内のFile分割、Contract具体化、Detector実装、Test Fixture、Typed Error、局所Bug、Retryおよび局所Reworkを自己解決する。

Codex／Userへ返すのは次だけとする。

- Root／Authority／Stable／External／Git／User DataのScope拡張。
- Phase目的、Mode Semantics／Security PolicyまたはHuman Gateの変更。
- 実Model Download／Load、AWS／LightningまたはPhase 6前倒しが不可避。
- 重大Risk受容またはFrozen要件同士の両立不能。
- Phase 5-G `COMPLETE_CANDIDATE`とFinal Acceptance Gate。

`Unresolved ≠ Blocker`。次Work Unitで解決できることをHumanへMicro-escalateしない。Subphase報告で停止せず、5-Gまで継続する。

## 5. Compaction／Quota Recovery

Auto-compaction／Manual Compaction／5時間Quota停止の後は、次を再読してActive Work Unitから継続する。

1. Automation／Cross-provider／Compaction統合正本。
2. Claude Operating Notes／Long-running Companion／Tracker。
3. Phase 5 Index／Execution Plan／最新Recovery Index。
4. Active WUのAcceptance／Mutation／Open Finding。
5. 必要なSource／Test Diff。

復旧後の言語変化だけをFailureとはしないが、日本語Handoff／Status要件を忘れない。取得していないHash／Timestamp／Action 0を捛造しない。

## 6. Security Review Contract

- Positive Testだけでなく、Bypass、Encoding、Chunk Split、Race、Stale Snapshot、Partial Action、Evidence Leakage、Over-refusalをAdversarialにReviewする。
- Test PassだけでSecret／PII実値0、Root外0、Git Mutation 0またはFalse Completion 0を断言しない。Evidence Classを付ける。
- Existing Testの削除／弱体化、Fake Production Success、未検査`allow`、Unknown-to-safe変換でClosureしない。
- Claude Self-reviewはCodex Independent Reviewを代替しない。

## 7. Stop Boundary

```text
Claude Max Scope : Phase 5-G COMPLETE_CANDIDATE
Phase 5-H        : Codex／User only
Phase 5-EX／6   : separate design／authorization required
Git／External    : prohibited
```

本書はAccepted／Frozenだが、User Backup、Codex `ARMED`およびUser Startの二段Gateが成立するまでActivateしない。
