# Phase 9 Closure時 `.claude/`確認・削除予約

```yaml
document_id: phase_9_closure_claude_local_artifact_cleanup_reservation_20260823154121
status: planned_destructive_action_not_authorized
document_type: append_only_planned_work
target_gate: phase_9_closure
recorded_at: 2026-08-23 15:41:21 JST
decision_authority: user
exact_candidate: <project-root>/.claude/
deletion_performed: false
```

## 1. Decision

Claude CodeがProject Root内へ再生成した`.claude/`について、Phase 9 Closure時にExact内容と必要性を確認し、Project運用に不要であれば削除する候補として予約する。

Userは、Repository外またはProvider固有MemoryをProjectの正本として依存させず、Repository内のIndex、Handoff、EvidenceおよびAccepted Stable DocsだけをCross-provider運用の正本とする方針を既に定めている。

## 2. Current Principle

```text
Provider-local Memory／Settings : Canonical Project Authorityではない
Repository Docs                 : Canonical Development Evidence／Handoff
Automatic Provider Memory Save  : Prohibited
Deletion Authority Now          : Not granted by this reservation
```

`.claude/`が存在すること自体を、ClaudeのAuthority、Recovery正本、Completion EvidenceまたはProject Stateとして扱わない。

## 3. Phase 9 Closure Gate

削除前に、次をExact Targetへ限定して確認する。

1. 対象が`<project-root>/.claude/`であり、別Project、Home Directory、Provider共通設定またはSymlink先ではない。
2. Directory内のFile一覧、Size、Tracked／Untracked状態およびSymlink有無。
3. Runtime、Test、Build、Claude Long-run RecoveryまたはAccepted運用が参照していないこと。
4. Repository内Docsへ未移記の唯一情報がないこと。
5. BackupまたはRecovery要否と、削除後にProviderが再生成する条件。
6. UserによるExact削除許可。

上記を満たし、不要と確定した場合だけ削除する。削除した対象、復元可能性および再生成条件をClosure Evidenceへ記録する。

## 4. Scope Boundary

- 本予約はProject Root内の`.claude/`だけを候補にする。
- Home Directory、他Project、`.codex/`、Claude全体設定またはProvider Memory領域を暗黙に含めない。
- `.gitignore`により非追跡であっても、無許可削除を正当化しない。
- Claudeが「不要」と報告した事実だけで削除せず、ControllerのAs-built確認とUserのExact許可を必要とする。
- Phase 9 Closure前に重大な干渉が判明した場合は、別の明示指示を受けるまで触らない。

## 5. Non-authorization

本書は破壊的操作の実行許可ではない。現時点の`.claude/`の読取、削除、移動、編集、Permission変更、Git操作またはProvider設定変更を開始しない。

