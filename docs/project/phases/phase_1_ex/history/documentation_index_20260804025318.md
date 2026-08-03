# Phase 1-ex Documentation Index Snapshot

```yaml
document_id: phase_1_ex_documentation_index_snapshot
snapshot: 20260804025318
state_at: 2026-08-04 02:53:18 JST
status: current_snapshot
snapshot_of:
  - ../phase_index_ja.md
  - operations/git_workflow_acceptance_merge_and_branch_retirement_20260804025318.md
  - ../../../current/documentation_index_ja.md
  - ../../../shared/conventions/documentation_rules_ja.md
  - ../../../shared/operations/git_workflow_policy_ja.md
  - ../../../shared/operations/git_publication_sanitation_policy_ja.md
supersedes: documentation_index_20260803210658.md
source: user_directed_git_workflow_completion_and_merged_branch_retirement
```

本Snapshotは[2026-08-03 21:06:58版](documentation_index_20260803210658.md)までの全状態を継承し、Git運用正本、PR #1 Merge、`main` Postflight、作業Branch退役およびLocal Working Root方針をAppend-onlyで記録する。

## 1. Accepted State

```text
Existing Repository History : preserved
Pull Request                 : #1 merged
Merge Method                 : merge commit
Merge Commit                 : 9fff303175a3224963254eacddd66f9cf5112a5a
Default Branch               : main
Local／origin/main           : aligned
Working Tree                 : clean at postflight
Git fsck                     : pass
Publication Files            : 1,053／1,053
Path／Content Mismatch       : 0／0
Merged Working Branch        : retired locally and remotely
Tag／Release                  : none
Phase 1-ex                   : in progress
```

## 2. Git Workflow Decisions

- `main`を公開・統合済みGit正本とする。
- 作業は最新`main`から有界Branchを作り、原則Draft PR＋Merge Commitで統合する。
- Commit Messageは`type(optional-scope): summary`形式とする。
- 公開Identityは`Nazuna Research`とGitHub-linked private noreply Emailを使用し、具体値をDocsへ記録しない。
- TagはPhase Final Gate後のAnnotated Tag `phase-<phase>-complete`を候補とし、自動作成しない。
- Force Push、History Rewrite、Repository再作成、Tag移動および無承認Remote変更を禁止する。
- GitはDocs History、Lossless Compilation、SHA-512 EvidenceおよびBackupを代替しない。
- Branch Protectionは未設定であり、別判断とする。

## 3. Local Working Root

Phase 1-exの残作業中は、Original Projectを開発内容正本、Git Staging CloneをGit History／Remote操作正本とする二重Rootを維持する。

Git Staging Cloneは永久必須ではない。Phase 1-ex Final Backup後、Phase 2開始前を第一候補として、Git Clone全体を単一Git Working Rootへ移行できる。`.git`だけのCopy、Original／Cloneの無承認削除・Rename・入替は行わない。

## 4. Normative Sources／Evidence

- [Git Workflow Policy](../../../shared/operations/git_workflow_policy_ja.md)
- [GitHub Publication Sanitation Policy](../../../shared/operations/git_publication_sanitation_policy_ja.md)
- [Documentation Rules](../../../shared/conventions/documentation_rules_ja.md)
- [Current Documentation Index](../../../current/documentation_index_ja.md)
- [Phase 1-ex Index](../phase_index_ja.md)
- [Git Workflow Acceptance／PR Merge／Branch Retirement](operations/git_workflow_acceptance_merge_and_branch_retirement_20260804025318.md)

## 5. Before／After Snapshot

- [Documentation Rules Before](../../../shared/history/conventions/documentation_rules_phase_1_ex_before_git_workflow_acceptance_ja_20260804025318.md)
- [Documentation Rules After](../../../shared/history/conventions/documentation_rules_phase_1_ex_after_git_workflow_acceptance_ja_20260804025319.md)
- [GitHub Publication Sanitation Policy Before](../../../shared/history/operations/git_publication_sanitation_policy_phase_1_ex_before_git_workflow_acceptance_ja_20260804025318.md)
- [GitHub Publication Sanitation Policy After](../../../shared/history/operations/git_publication_sanitation_policy_phase_1_ex_after_git_workflow_acceptance_ja_20260804025319.md)
- [Git Workflow Policy Initial Accepted Snapshot](../../../shared/history/operations/git_workflow_policy_phase_1_ex_after_initial_acceptance_ja_20260804025319.md)
- [Current Index Before](../../../current/history/index/documentation_index_phase_1_ex_before_git_workflow_acceptance_ja_20260804025318.md)
- [Current Index After](../../../current/history/index/documentation_index_phase_1_ex_after_git_workflow_acceptance_ja_20260804025319.md)
- [Phase Index Before](operations/phase_index_phase_1_ex_before_git_workflow_acceptance_ja_20260804025318.md)
- [Phase Index After](operations/phase_index_phase_1_ex_after_git_workflow_acceptance_ja_20260804025319.md)

## 6. SHA-512

```text
Previous Documentation Index:
9d3650c2ecbb6b1e9a1c5846337cd0f9a36585a8d2e12b53b0345031f303b194deced9566342212b806f2f1e387db815e7a39964882948f29a3ce27bcb096865

Documentation Rules Before:
d4a786e195a3640f391830225828d5c38f7846b44fd8ba4db6ab6b13ff8399bf35cbdce89d40554596e800f81fdb5a40d9e9962164a8ecca9775b71b27b3e095

Documentation Rules After／Stable:
014c8ed93d6b70139ff184a42760acb8b406bcf8c3c0e2fd4a43761f4d9cc2aa61857c81bfebabf3bdaa0d9c48f2a732e84d989a49a7205c33d8eaf73415c818

GitHub Publication Sanitation Policy Before:
889cbbacefefa37cfa98f6a26d0738ebe6018532d04d8bef1015fddb9584867004e590e27a4e4d93dbb6f0e58c8accec784c2d9900a7f669517d62ce3de26655

GitHub Publication Sanitation Policy After／Stable:
3c4f8d559469df32a0f8044978b9e3be83ce3540ee5671e8c1ead43332486347f704b472af2cad9b9f6f213a7d763b601efed4911fe8945cedbf4678ef5292c8

Git Workflow Policy Initial／Stable:
0051c05dfa30d91b7d41fa17efe2952a25896bea0290912ea4b462df992ab840603fb10dfba64aab93aed6a77e4306f1a5d8f19cfc274a61cbd159d67dcca509

Current Index Before:
b3c114d2bd986dc2cb36095570918bad23ae40f2f21d1dd879c8d94706fd6873e6d4feb1fecd95d116dec81ac98d6b05ab6b9c5cfaaf1b184fa00d32307e7746

Current Index After／Stable:
8c7eacf6fbb8ce559bc3e31df89f6211b61cbc0a567aaa0561a3413f60fc033872024a5cac55a2bb85defaabee85bebc2085d2d99ec97922449095237e71e813

Phase Index Before:
4a78c3f3f5f6e8b58ab00d4e7ac0f2e68725ac4fd91554eabb1ea0f2f5ab5178af854ef7501fc0951d67bec9fd9f459ae42c0f351a508a3ac15611ea8435d06c

Phase Index After／Stable:
b321c87f376965de2914c2df6b12e9abb49fd6d104cc000e91f8d7b9e331e19fae280553b77fc28a41acd6ab761fe8c992c836849b0aaad39d81b7b47f74f916

Git Workflow Acceptance Record:
30be123968e8e73c0ffcc3368c79aaa0b00f1fb0568980faeb64db06af7b08ae31cf46186fc4a33a74f5ec65066456c2ff034841367c2d53431acd02d079c007
```

## 7. Mutation Boundary

```text
Original Project Docs      : updated／added within authorized Git design scope
Original Runtime Code      : unchanged
Original Config／Tests     : unchanged
Git Staging main           : unchanged after postflight
Remote main                : unchanged after accepted merge
Merged Local Branch        : deleted with explicit user authorization
Merged Remote Branch       : deleted with explicit user authorization
Tag／Release               : none
Visibility／Metadata       : unchanged
Branch Protection          : unchanged
other/                     : not accessed
Task／Sub-agent Creation   : none
```

## 8. Next Gate

Phase 1-exの次工程は、必要Docsの最終再整理、Phase 1-ex Final Lossless／Design Governance Recovery更新、全体Review／Test／Privacy Scan、User AcceptanceおよびPhase Final Backupである。

Tag、Release、Branch Protectionまたは単一Git Root Cutoverは、それぞれ対象・手順・Rollbackを提示し、ユーザーが明示承認するまで実行しない。
