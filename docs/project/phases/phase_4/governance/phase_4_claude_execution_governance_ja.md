# Phase 4 Claude Execution Governance

```yaml
document_id: phase_4_claude_execution_governance
status: accepted_frozen_ready_for_backup_not_activated
phase: phase_4
language: ja
recorded_at: 2026-08-21 22:04:22 JST
automation_control_state: OFF
implementation_authorized: false
completion_line: phase_4_g_complete_candidate
frozen_at: 2026-08-21 23:20:56 JST
```

## 1. Role／Authority

```text
User
  > Codex プロジェクト責任者兼設計統括者役
    > Claude側設計統括者役
      > Phase 4内のPhase設計／設計兼実装／Review責務
```

ClaudeはPhase 4のRoutineな局所設計、Exact Mutation、実装、Test、自己Review、局所ReworkおよびRecoveryを自律実行できる。Phase 4-G `COMPLETE_CANDIDATE`で停止し、Phase 4-H、Git、Phase 5またはExternal Actionへ進まない。

## 2. Supreme Boundaries

- Authorized Project Root外へ触れない。
- `other/`、別Project、Provider Memory、`.claude/`／`.codex/`外部Memoryへ触れない。
- User実`runtime_data/`へ触れない。
- Git／GitHub Mutationを行わない。
- Network、Model Download／Load、AWS、Secret、課金またはExternal Serviceを使用しない。
- Stable Existing Docs／Existing Historyを無断変更しない。
- DeepSeekをCurrentへPromotionしない。
- Phase 5／6の本実装へ進まない。
- 誤生成Fileを自己判断で削除／移動／Permission変更しない。

## 3. Stable／History

- Phase 4 Stable Candidate DocsはClaude実行開始時点のFrozen Inputとして扱い、直接変更しない。
- Correctionは`docs/project/phases/phase_4/history/**`へ新規Append-onlyで作る。
- Source／Test／Config／UIはActive Work UnitのExact Mutation内だけ変更する。
- Automation／Compaction Evidenceは意味あるCycle単位にまとめる。
- Provider MemoryとConversation Summaryを正本にしない。

## 4. Autonomy／Escalation

Claudeは、権限内の実装選択、File分割、Test Fixture、Typed Error、局所Bug、再送およびFrozen要件内の設計具体化を自分で解決する。

Human／Codexへ返すのは次だけとする。

- Root／Authority／Stable／External／Git／User DataのScope拡張。
- Phase目的またはMode Semanticsを変える必要。
- Phase 5／6責務の前倒しが不可避。
- 重大Risk受容または両立不能な設計。
- `COMPLETE_CANDIDATE`とFinal Acceptance Gate。

`Unresolved ≠ Blocker`。次Work UnitでClaudeが解決できる項目をMicro-escalationしない。Subphase完了報告を理由に停止しない。

## 5. Compaction Recovery

Compaction後は次を再読してから再開する。

1. Automation／Cross-provider／Compaction統合正本。
2. Claude Operating Notes／Long-running Companion／Flag。
3. Phase 4 Index。
4. Phase 4最新Recovery Index。
5. Active Work UnitのExact Scope／Open Finding。
6. 必要なSource／Test Diff。

各Material BoundaryでCurrent Stateを残し、毎Command／毎小修正でEvidence Fileを作らない。Compaction Hashは実際に取得したBefore／Afterだけを記録し、欠落値を捏造しない。

## 6. Review Contract

- Design／Implementation／Adversarial Security Review／Regression ReviewをPhase内で分ける。
- Self-reviewがPASSでもCodex Independent Reviewを代替しない。
- Test PassだけでPath、Authority、Cache、Crash、ConcurrencyまたはFalse ReceiptをCloseしない。
- Existing Testを削除／弱体化して件数を合わせない。
- 数値、Timestamp、Mutation 0はEvidence Classを明記し、推測断定しない。

## 7. Stop Boundary

```text
Claude Max Scope : Phase 4-G COMPLETE_CANDIDATE
Phase 4-H        : Codex／User only
Phase 5 Start    : separate design freeze／authorization required
Git／External    : prohibited
```

本書はAccepted／Frozenだが、ユーザーBackup報告、Codex `ARMED`および後続User Startが成立するまで実行契約としてActivateしない。
