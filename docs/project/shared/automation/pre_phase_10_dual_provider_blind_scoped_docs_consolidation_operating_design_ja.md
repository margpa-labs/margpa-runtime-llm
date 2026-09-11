# Phase 10直前 Claude／Codex 独立Docs統合 Blind運用設計

```yaml
document_id: pre_phase_10_dual_provider_blind_scoped_docs_consolidation_operating_design
document_type: stable_operating_design
document_state: current_reserved_for_pre_phase_10_execution
recorded_at: 2026-09-11 17:46:29 JST
language: ja
authority_owner: Nazuna Research
decision_authority: user
scope: pre_phase_10_scoped_dual_provider_docs_consolidation
providers:
  - claude_code
  - codex
execution_order:
  - claude_code
  - codex
blindness_target: codex_must_not_read_claude_consolidation_before_codex_side_freeze
append_only: true
git_write_authorized: false
```

## 1. 目的

Phase 10の全範囲Docs統合へ進む前に、Claude CodeとCodexが同一のFreeze済みSource Setを別々に読み、互いの統合成果へ引きずられない二つのStable候補を作る。

この工程の目的は、どちらか一方を正解と決めることではない。異なるProvider／Model／Harness／Roleが同じ一次資料から抽出する構造、優先順位、欠落、矛盾および設計観点の差を、後続の全範囲統合に利用できる独立材料として保存することである。

特に、Claudeを先に実行しても、CodexがClaude側Stable本文、要約、見出し、Finding、ReturnまたはUserによる内容説明を事前に読まない状態を維持する。

## 2. User Decisionと適用範囲

### 2.1 Stable作成対象

独立Stableを新規作成する範囲は次に限定する。

1. `docs/project/current/automation_cross_provider_compaction/`
2. `docs/project/current/history/automation_cross_provider_compaction/`
3. `docs/project/shared/`配下にある、Constitution関連で有効な資料の対象Folder

Stable作成対象外のFolderへ、今回の独立統合を理由とするStableを作らない。

### 2.2 探索・読み取り対象

統合品質を上げるため、Source Discoveryの母集団は`docs/`配下の全Fileとする。ただし、両Providerへ渡す実際のSource Setは、工程開始時に作成するFreeze Manifestへ列挙したFileだけとする。

次はSource Setへ含めない。

- 今回のBlind Run開始後に生成されたClaude側／Codex側成果物。
- Blind Staging Directory全体。
- Current RunのHandoff、Return、Recovery、Reviewまたは会話要約のうち、先行Providerの結論を含むもの。
- Backup、一時File、Generated Cacheその他、Source Authorityを持たないArtifact。

### 2.3 2 Pass原則

各Providerは同じFreeze済みSource Setを使い、二段階で作業する。

1. Pass 1: Source Setを全件読み、対象範囲ごとのStable候補を新規作成する。
2. Pass 2: 同じSource Setを再び全件照合し、Lossless性、矛盾保持、Authority、時系列、Evidence Pointerおよび初見可読性を監査する。

Pass 2で補正が必要な場合、Pass 1成果物を黙って上書きしない。Append-only Addendumまたは新Revisionを作り、置換関係を明記する。

## 3. Blindnessの最上位Invariant

1. Claude側成果物がFreezeされる前にCodex側作業を開始しない。
2. Codex側成果物がFreezeされるまで、Claude側成果物の本文、要約、見出し構造、Findingおよび結論をCodexへ開示しない。
3. 両Providerは同じSource Manifest Revisionを使用する。
4. `docs/`全探索という説明だけで済ませず、実際に読取可能なSource FileをManifestで固定する。
5. Claude側成果物を通常のSource Folderへ先に公開しない。Codex側の通常探索へ混入させない。
6. File名は人とAgentの双方へ読取禁止を伝えるが、File名だけを隔離機構とはみなさない。
7. Codex側HandoffへClaude側のFile名以外の意味情報を載せない。可能ならFile名自体も汎用Output Slotだけを示し、見出しや結論を漏らさない。
8. User Relay時もClaude側Return本文をCodexへ貼らない。必要な連絡は`claude_stage_complete_and_sealed`という状態通知に限定する。
9. Codexが禁止Artifactを一部でも読んだ場合、Blind成立を主張しない。
10. 意図せぬ閲覧が起きても成果物を削除・改変せず、Contamination Incidentとして保存する。
11. Blindnessは評価条件であり、Claude側文書の正本性やCodex側文書の優先権を自動生成しない。
12. 独立成果物は後続比較前にそれぞれDigest付きでFreezeする。

## 4. Directory／命名設計

実行時に、次の一時的なAppend-only Stagingを作る。

```text
docs/project/shared/blind_preintegration/<run_id>/
├─ control/
│  ├─ blind_scope_manifest.json
│  ├─ blind_scope_manifest.sha512
│  ├─ source_read_contract_ja.md
│  └─ stage_state.json
├─ claude_side_sealed_until_codex_complete/
│  ├─ claude_side__codex_do_not_read_until_blind_complete__<target_key>__<timestamp>.md
│  ├─ ...
│  ├─ exact_return/
│  └─ recovery/
├─ codex_side/
│  ├─ codex_side__independent__<target_key>__<timestamp>.md
│  ├─ ...
│  ├─ exact_return/
│  └─ recovery/
└─ evidence/
   ├─ claude_completion_manifest.json
   ├─ codex_completion_manifest.json
   ├─ blindness_audit.json
   └─ unseal_record_ja.md
```

`run_id`は日時だけに依存せず、一意なUUID等を含める。`target_key`は対象Folderを識別する中立Keyとし、先行成果物の結論をFile名へ書かない。

Staging成果物は独立作業完了後も原位置へAppend-onlyで残す。公開先へCopyしても、原ArtifactをMove／Deleteしない。

## 5. Freeze Manifest Contract

`blind_scope_manifest.json`は最低限、次を持つ。

```json
{
  "schema_version": "dual_provider_blind_docs_consolidation_v1",
  "run_id": "<uuid>",
  "created_at": "<timestamp>",
  "decision_authority": "user",
  "source_root": "docs/",
  "source_freeze_revision": "<git-head-or-working-tree-snapshot-id>",
  "source_set_digest_sha512": "<digest>",
  "source_files": [
    {
      "path": "<path>",
      "digest_sha512": "<digest>",
      "size_bytes": 0,
      "authority_class": "<class>"
    }
  ],
  "stable_target_scopes": ["<target>"],
  "forbidden_read_prefixes_for_codex": ["<claude-sealed-prefix>"],
  "excluded_paths": ["<path>"],
  "provider_order": ["claude_code", "codex"],
  "required_passes_per_provider": 2,
  "blind_stage": "prepared",
  "unseal_authorized": false
}
```

`source_freeze_revision`はGit Commitだけで代用しない。Working Treeに未Commit変更がある場合、対象PathとDigestのManifest自体をSource Revisionとする。

Manifest作成後にSource Fileが変わった場合、黙って新内容を読むことを禁止する。Runを`source_changed_after_freeze`として止め、新Manifestで再開するか、Userが差分を受理したAppend-only Addendumを作る。

## 6. 実行State Machine

```text
PREPARE
  -> CLAUDE_BLIND_BUILD
  -> CLAUDE_SEALED
  -> CODEX_BLIND_BUILD
  -> DUAL_FROZEN
  -> UNSEALED_COMPARE
  -> PUBLISHED
  -> FINAL_INTEGRATION

Failure／Stop:
  SOURCE_CHANGED
  BLIND_CONTAMINATED
  PARTIAL_RECOVERY_AVAILABLE
  USER_DECISION_REQUIRED
```

各遷移は`stage_state.json`へProvider Identity、Task／Session ID、時刻、入力Manifest Digest、出力DigestおよびAuthorityを記録する。会話中の自己申告だけでStateを進めない。

## 7. Stage別手順

### 7.1 PREPARE

Controllerは、Stable Target Scopeを確定し、`docs/`全体を探索してSource候補を列挙する。History、Current、Stable、Correction、Addendum、HandoffおよびEvidenceのAuthorityを区別したManifestを作る。

この時点でClaudeとCodexの両Handoffを同一Source Manifestから作る。Provider固有Tool差だけをAdapterとして変え、Objective、Scope、AcceptanceおよびSource Setは変えない。

### 7.2 CLAUDE_BLIND_BUILD

ClaudeはManifestへ列挙されたSourceだけを読み、Pass 1とPass 2を実行する。Output、ReturnおよびRecoveryは全て`claude_side_sealed_until_codex_complete/`へ作る。

完了時は、内容をCodexへRelayせず、次だけを通知する。

```text
run_id
provider identity
stage: claude_sealed
completion manifest path
completion manifest digest
output count
partial／complete
```

### 7.3 CODEX_BLIND_BUILD

Codexは新規Taskまたは独立作業Contextで開始する。Mandatory ReadingはManifest、共通運用RuleおよびManifest内Sourceだけとする。

Codex側は禁止Prefixを、次の全操作から除外する。

- `rg --files`、`find`、検索、全文Grep。
- File Open／Read／Summarize。
- Recovery Set／Mandatory Reading。
- Handoff添付、会話要約、Tool Output。
- 自動Index、IDE Search、Embedding／RAG Input。

検索時は、例えば次のような除外を付ける。

```text
rg --files docs -g '!**/blind_preintegration/**'
rg '<pattern>' docs -g '!**/blind_preintegration/**'
```

ただし最も強い方式は、Directory全体検索ではなく、Manifestに列挙されたPathを正のAllowlistとして順に読む方式である。CodexはRead Logへ実際に読んだPathとDigestを記録し、Claude側Sealed Prefixが0件であることを返す。

### 7.4 DUAL_FROZEN／UNSEALED_COMPARE

Codex側Pass 2とCompletion ManifestがFreezeされた後、UserまたはControllerが`unseal_authorized=true`へ遷移させる。この時点で初めて両側Artifactを同じ比較Contextへ入力できる。

比較は次を分離する。

- 共通して保存した事実／設計／判断。
- 片側だけが保存した有効観点。
- Authorityまたは時系列の解釈差。
- 片側だけの過大Claim／欠落／誤読。
- 表現、構造、初見可読性の差。
- 解消できないConflictと必要なUser Decision。

比較によって独立Artifactを上書きしない。比較結果は別Artifactとして保存する。

### 7.5 PUBLISHED／FINAL_INTEGRATION

比較後、各独立Stableを指定された`docs/project/shared/`直下の対応Folderへ新規Fileとして公開する。

```text
claude_side_<target>_stable_ja_<timestamp>.md
codex_side_<target>_stable_ja_<timestamp>.md
```

どちらが作成したかをFile名とMetadataの両方で明示する。公開後、Phase 10全範囲Docs統合は両Provider成果物、比較Artifactおよび元Sourceをまとめて読む。この最終工程で初めて相互成果を統合材料として扱う。

## 8. Handoff設計

両ProviderのHandoffは、Projectで定めるTask Communication IdentityとHybrid Handoff方式を使う。

```text
Identity／Routing Header
+ Natural-language Intent／Rationale
+ XMLまたはMarkdown Section Boundary
+ JSON Execution Contract
+ Exact Artifact Path／Digest
```

Claude側Handoffには通常のInputを渡す。Codex側Handoffには次を明記する。

- `blind_input_only: true`
- `claude_output_read_allowed: false`
- `source_manifest_is_allowlist: true`
- `forbidden_path_prefixes`
- `user_relay_must_not_include_claude_content: true`
- `accidental_read_disposition: blind_contaminated`
- `unseal_authority: user_or_controller_after_dual_freeze`

Codexへ「Claudeはこうまとめた」「ClaudeはこのFindingを出した」等の誘導情報を与えない。単なる中立状態通知だけを許可する。

## 9. Acceptance／Audit

Blind独立統合の成立には最低限、次が必要である。

1. 両ProviderのInput Manifest Digestが一致する。
2. 両Providerが同じStable Target Scopeを扱う。
3. 各ProviderがPass 1／Pass 2を区別して完了する。
4. Claude側成果物がCodex Freeze前に通常Sourceへ公開されていない。
5. Codex Read LogにClaude Sealed Pathが存在しない。
6. Codex Handoff／Conversation ContextにClaudeの結論または要約が存在しない。
7. 両Outputが別Identity／DigestでFreezeされる。
8. Partial、Unknown、ConflictおよびSource ChangeがPASSへ変換されていない。
9. Unsealが両Freeze後である。
10. 公開先が予約された指定範囲に限られる。
11. 元Artifactと比較ArtifactがAppend-onlyで保持される。
12. Git Write、Phase 10開始または本番統合のAuthorityが本書だけから生成されていない。

Blindness Auditには、少なくとも次を記録する。

```text
manifest identity／digest
provider task／session identity
read log
forbidden-path read count
output identity／digest
stage transition times
user relay payload class
accidental disclosure／tool injection
unseal authority／time
audit disposition
```

## 10. 汚染・Failure時の処理

CodexがClaude側Artifactまたはその実質的要約を読んだ場合、次を行う。

1. 読んだ対象、時刻、経路、範囲をEvidence化する。
2. 現Codex Outputを`BLIND_CONTAMINATED`として保持する。
3. Blind Outputとしての採用を禁止する。
4. Blind性が必要なら、未汚染の新規Codex Taskと同一Freeze Manifestで再実行する。
5. 再実行不能なら、Blind比較ではなく`informed_review`として分類する。

ToolやHarnessが禁止Pathを自動注入した可能性がある場合も、読んでいないと推測してPASSにしない。観測できない場合は`blindness_unknown`とする。

## 11. 限界と保証範囲

本設計はRepository上の隔離、Allowlist、Handoff制約、Read Logおよび段階Freezeによる運用上のBlindnessを定義する。Filesystem ACL、暗号化または別MachineによるCryptographic Isolationではない。

したがって、`絶対に1 bitも見ていない`という保証をProvider自己申告だけで主張しない。より強いIsolationが必要な場合は、Claude側成果物を別Workspace／別Repository／暗号化Archiveへ隔離し、Codex TaskのFilesystemから物理的に読めない構成を使う。

Current運用では、同一Workspace上でも次の組合せにより実用的な独立性を高める。

```text
same frozen source allowlist
+ sealed output prefix
+ fresh Codex task/context
+ content-free user relay
+ explicit read deny
+ read-log audit
+ dual digest freeze before unseal
```

## 12. Current Provider Profile

初回想定は次である。

```text
Claude Code:
  Identity Type: Session ID
  Role: designer_implementer
  Order: first

Codex:
  Identity Type: Task ID
  Role: project_controller_design_governor or bounded independent consolidator
  Order: second

Routing:
  user_relay
```

Task名はRoleを管理しやすくするLabelであり、通信Identityの代わりではない。Task／Session ID、Provider、Role、Message Typeを毎回明記する。

## 13. 現在地

```text
Operating Design: COMPLETE／RESERVED
Source Freeze Manifest: NOT CREATED
Claude Blind Consolidation: NOT STARTED
Claude Output Seal: NOT STARTED
Codex Blind Consolidation: NOT STARTED
Dual Freeze: NOT STARTED
Unseal／Comparison: NOT STARTED
Publication: NOT STARTED
Phase 10 Full Docs Integration: NOT STARTED
```

本書は将来工程の運用設計であり、実行Authorityを単独で生成しない。具体的なTarget Folder選定、Freeze Manifest作成、Provider HandoffおよびUnsealは、Phase 10直前のUser Decisionに従う。

## 14. 関連文書

- [Phase 10直前 Claude／Codex 独立Docs統合 予約](../planned_work/pre_phase_10_dual_provider_scoped_docs_consolidation_reservation_ja_20260907092855.md)
- [Claude／Codex Blind Cross-Evaluation Protocol](../history/automation/claude_codex_blind_cross_evaluation_protocol_ja_20260823095316.md)
- [Development Agent Hybrid Structured Instruction Handoff Operating Rule](../task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md)
- [Task ID／Role二重Identity通信 Decision Evidence](../history/automation/development_agent_task_id_role_dual_identity_communication_decision_evidence_ja_20260910150333.md)

