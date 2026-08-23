# Phase 6 Exact Design Freeze

```yaml
document_id: phase_6_exact_design_freeze_20260822211308
status: accepted_frozen
phase: phase_6
recorded_at: 2026-08-22 21:13:08 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
automation_control_state: OFF
git_mutation: not_performed
```

## 1. Freeze Decision

Phase 5 ClosureをPASSとし、Phase 6 Design Packageを`ACCEPTED／FROZEN`とする。Phase 6-0～6-IのClaude長期実行Packageは設計上成立しているが、User Backup、Exact Model／Disk／Memory／Resolved Scope Authority、Activation Preflight、Controller `ARMED`および後続User Startまで実行してはならない。

## 2. Frozen Package SHA-512

```text
b7697fe7fec6086468ed58654fea3849f50c94ea510f463fa745c3cdfa7fc46e92ff7c92152588889844213c6c5f820bc81c9376d139b36858a25ec5d6dd289a  docs/project/phases/phase_6/requirements/phase_6_requirements_ja.md
36ea1c3866f09a84b2214f7c6411883079243066fff62514c85cfd50f4f474fa9a4eb716637c96d049c8dd4a2e5c337162f60485210de2958c156ce104154a72  docs/project/phases/phase_6/architecture/phase_6_architecture_ja.md
8b9b8cb4ba2a83ccac8054081d951bd8aaca784768da2c3f507c2c7341262d1cc95d64db68808ac4db55d5f5fca972a1a0eea25b0ab35b61e25ead46b08ce7d9  docs/project/phases/phase_6/adr/phase_6_adr_ja.md
601c8b2a5148a55c88cfba5258560a8d987b3178a5a287a53051535e66c22a071e86466d07a186f946c26bd21f88cd4e08651ff343e1183ef257f29d7266b5e4  docs/project/phases/phase_6/governance/phase_6_claude_execution_governance_ja.md
17d41752e40517a5314e587eed74046511f4b344ba7b7898fc99c32f6ef87e390e5d9924a6982f492a702efd90dfae60b77e47268fb12191a5b6def57fa9961e  docs/project/phases/phase_6/operations/phase_6_execution_plan_ja.md
9f4619e111802138cc9be97a9cf57718a680f39b161b1078f1284b970d44a432c3db2757afb32d6372109c3ca94427c1706797d5802c679d9e9b22ec963d40c4  docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md
9eb8b3d7bb94441035eb6383a514779df6719fa8c66fbf31dfe424cfbe51287aadbd3f7b12bffd97e910461a6b5e47231666d9f50afb6f0a8a301861265339d8  docs/project/phases/phase_6/handoffs/phase_6_claude_execution_handoff_ja.md
dd84227d4683332b5e499bf7c746549a816985f0d4042b6b1d8f04b1b7ff02199d1792ddc542bb89d40dc0a88fc67cc68ef8470c6f0a22e389ab81f5778ed6d2  docs/project/phases/phase_6/phase_index_ja.md
```

DigestはFreeze時点のFile bytesに対する実測値である。Freeze後にStable Packageを変更する場合は、重大衝突、Before／After、影響、Controller Reviewおよび新しいFreeze Receiptを必要とする。局所実装上の具体化はAppend-only Correction／DeviationとSource／Testで扱い、Stable正本へ無断直書きしない。

## 3. Frozen Execution Boundary

```text
Claude Minimum Start : P6-0-WU-001
Claude Maximum End   : P6-I-WU-004／COMPLETE_CANDIDATE
Codex／User Boundary : Phase 6-J Full Closure
Phase 7／8／10       : NOT AUTHORIZED
Git Mutation         : NOT AUTHORIZED
Network／External    : NOT AUTHORIZED
Automation           : OFF until two-key activation
```

Exact Source／Test MutationはWork UnitごとにFrozen ContractとAs-builtからClaude側設計統括者役が動的に決定する。必要なものだけを作り、固定Packageを機械的に量産しない。

## 4. Model Symlink Exception Boundary

Design FreezeはModel Targetへの権限を生成しない。Phase 6 Activation Receiptは少なくとも次をHuman承認付きで別途固定する。

```text
Logical models Path
Resolved Physical Target
Qwen Read／Load-only Subtree
DeepSeek Canonical Read-only Subtree
DeepSeek Derived／Manifest Write Subtree
Optional DeepSeek Conversion Work Subtree
Purpose／Period／Disk Floor／Memory・Thermal Stop Conditions
```

過去Download Cycleの例外は再利用しない。Receipt成立前にResolved Target内容を読まない。許可Subtree外、Sibling Model、V4、親Directory、CacheまたはTrashへ拡張しない。

## 5. Git Boundary

Project Root内Repositoryの`status／diff／ls-files／check-ignore／rev-parse`相当はRead-only Evidenceとして利用できる。Index、RefまたはWorktreeを変更するGit Operation、GitHub、Network、Commit、Push、Tag、Branch操作は許可しない。

## 6. Recovery Boundary

Recoveryは各小修正ではなく、Phase 6-0、6-A、6-B、6-C、6-D、6-E、6-F、6-G、6-Hおよび6-IのMaterial Boundary単位で作る。Provider Compaction／Quota後はRepository内Index／Handoff／Recovery／Hash Evidenceから復旧し、Provider Memoryを正本にしない。

## 7. Activation Gate

```text
Phase 5 Closure          : PASS
Phase 6 Design Review    : PASS
Design Accepted／Frozen : PASS
User Backup              : PENDING
Exact Model Authority    : PENDING AFTER BACKUP
Codex Activation Preflight: PENDING
Codex ARMED              : PENDING
User Start               : PENDING AFTER ARMED
Implementation           : NOT AUTHORIZED
```
