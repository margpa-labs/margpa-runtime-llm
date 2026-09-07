# Claude Memory／Project `.claude/` 限定運用例外

```yaml
document_id: claude_memory_and_project_claude_directory_scoped_operational_exception_20260904024250
document_type: user_authorized_operational_rule_change_evidence
document_state: current_append_only_evidence
recorded_at: 2026-09-04 02:42:50 JST
language: ja_with_structured_english_terms
decision_authority: user
provider: Claude Code
scope: exact_two_target_exception
retroactive_reclassification: false
canonical_authority_granted: false
git_action: none
append_only: true
```

## 0. User Decision

Claude Codeが実効上利用する次の二対象について、作成・読取・更新・保持を許容し、Codexその他RoleはRoutine Cleanup、Commit準備またはGovernance確認のために削除・修正・監査しない。

```text
1. Claude Code Providerが本Projectへ対応付ける単一Memory File
   `MEMORY.md`／`Memory.md`

2. Project Root直下
   `margpa-runtime-llm/.claude/**`
```

Userは、この例外の目的を、同じMemory／Directory関連逸脱の反復によるHuman StressとCorrection Costを避け、Claude Code側で実効がある場合はそのProvider機能を利用可能にすること、とした。

## 1. Exact Meaning

```text
Claude Code:
  対象二か所をProvider-local補助状態として自由に利用できる。

Codex／Other Roles:
  原則として内容を読まない、評価しない、削除しない、修正しない、整理しない。

Git:
  Project `.claude/`は既存`.gitignore`対象のまま保持する。
  `git add -f`、Unignore、Stage、Commit、Push対象化を行わない。

Canonicality:
  非正本、非Authority、非Evidence、非Handoff、非Recovery Sourceのまま。

Conflict:
  User最新指示、Active Handoff、Repository Canonical Docsが常に優先する。
```

Routineな作成・更新・保持をViolationまたはAction Inventory対象としてUserへ逐次報告しない。内容をRepositoryの要件、実装、AcceptanceまたはClosureへ使用する場合は、必ずAuthorized Repository Sourceと実Evidenceで再検証する。

## 2. Boundary Preserved

例外は二対象だけである。次は引き続き禁止する。

```text
- 上記単一Memory File以外のProject Root外Read／Write／List／Mutation
- 他Provider Memory
- 他ProjectのClaude Memory
- `.claude/`以外の未許可Project-local Hidden State
- Git Mutation
- Network／External Account
- User Runtime Data
- Secret／Credential保存
- Model Artifact Mutation
- Stable Docs Authorityの拡張
- Scope／Requirement／Closure Authorityの生成
```

## 3. Historical Treatment

本決定以前のProvider Memory違反記録は、当時の規則とEvidenceとして有効である。今回の例外を遡及適用して、過去のViolation、Failure、CorrectionまたはResearch Evidenceを削除・弱体化しない。

過去Handoff／Historyにある`.claude/`およびClaude Memoryの全面禁止はHistorical Snapshotとして保持する。Current運用では、本決定と更新済みStable Ruleが、上記二対象に限って当該禁止をSupersedeする。

## 4. Codex Cleanup／Commit Rule

```text
- `.claude/`の存在をDirty Tree Cleanup対象にしない。
- Commit前に削除しない。
- 内容を確認するために列挙しない。
- `.gitignore`から外さない。
- MEMORY.md／Memory.mdを消さない、移動しない、修復しない。
- 対象が存在することをProject成果物またはCompliance証明に使わない。
```

Userが個別に確認・削除・更新を指示した場合だけ、当該指示の範囲で再評価する。

## 5. Maximum Claim

```text
CLAUDE_EXACT_TWO_TARGET_MEMORY_EXCEPTION_AUTHORIZED
PROVIDER_LOCAL_USE_ALLOWED
CANONICAL_AUTHORITY_NOT_GRANTED
ALL_OTHER_BOUNDARIES_PRESERVED
NO_RETROACTIVE_RECLASSIFICATION
```
