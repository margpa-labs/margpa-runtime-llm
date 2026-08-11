# Phase 2-0 Documentation Capability Manifest — P2-0-WU-004 exact-1

```yaml
document_id: phase_2_0_documentation_capability_manifest_p2_0_wu_004_exact_1_20260811233209
manifest_id: p2-0-documentation-capability-manifest-001
revision: exact-1
status: exact_candidate_user_acceptance_pending
phase: phase_2
subphase: phase_2_0
work_unit: P2-0-WU-004
created_at: 2026-08-11 23:32:09 JST
language: ja
owner_role: プロジェクト責任者兼設計統括者役
target_role: Phase 2設計担当者役
entry_count: 6
total_lines: 1324
ordered_package_sha512: 033b7d11d771beb477099984ebd4a023a9db9c8e12678e4b3f369adcf417d6a5dd3734727d266b6ae207cd23bb7053edb57fbc33f0b9e4a2db0a6a2e10496826
```

## 1. Purpose

P2-0-WU-003で発生した`Content／Mutation Safety PASS`と`Literal Provider Grammar FAIL`を受け、Raw Command名ではなくCapability Semanticsを中心に、一件のBounded Documentation Createを再試験する。

本Manifestは、Child Taskが読むInitial Operational Viewの唯一のPath Set正本である。Control PackageとExact Result Pathを除き、本Manifest外を探索、推測または追加Readしない。

## 2. Deterministic Package Digest

Ordered Package SHA-512は、各Entryを次のUTF-8形式で一行ずつ並べ、末尾改行を含めて計算した。

```text
<order>\t<exact_relative_path>\t<line_count>\t<sha512>\n
```

```text
Entry Count             : 6
Total Lines             : 1,324
Ordered Package SHA-512 : 033b7d11d771beb477099984ebd4a023a9db9c8e12678e4b3f369adcf417d6a5dd3734727d266b6ae207cd23bb7053edb57fbc33f0b9e4a2db0a6a2e10496826
```

## 3. Exact Entries

| Order | Exact Relative Path | Lines | SHA-512 | Purpose |
|---:|---|---:|---|---|
| 1 | `docs/project/shared/operations/research_asset_mutation_control_ja.md` | 432 | `8830fd117b1214de3c4a495de23d75057676fa48724d01fadfa8c99b750ac22df6c34e255263904cfc9a7c53240b4bcd71b712ab5d83cd77569bb2414bc765de` | Authorized Root、No-cleanup、Human-only Amendment境界 |
| 2 | `docs/project/shared/task_roles/role_authority_matrix_ja.md` | 272 | `fb1440c5e344dfca4eb540c98d7a3fa6ff746e7a1b81d7a339aa8e8f65342853221dd86d88148b0a70101662bf13c3210055d062ac339e10b18ea27639fe8992` | Phase DesignerのExecution／Docs Authority |
| 3 | `docs/project/shared/automation/documentation_capability_contract_ja.md` | 204 | `0a5cbd22e6c671e855659e02b947c464506d4bb6c741adfa436ee9a3a782b3e84699a081923ae4dbd1518767d3865d482d7fc33b60a4eb66f0ad81bf4c2a951e` | Provider-neutral Capability Semantics正本 |
| 4 | `docs/project/shared/automation/provider_adapters/codex_desktop_documentation_io_adapter_ja.md` | 141 | `9907ea7c0f703d4e6e65620f45e9608ce7ec6fa036c1b23aec7a08e552b57fc69fd93b26c345d519a8922a38541374e5c83f3f490df53d2ed5bb63630e973051` | Codex Desktop semantic mappingとBatch Deny |
| 5 | `docs/project/phases/phase_2/history/operations/phase_2_0_bounded_write_controller_review_p2_0_wu_003_20260811225656.md` | 159 | `e443c4e0371f084f5329cf681d83b6fdd94f623f85607bc6a7adc35fbd60a36bcbdc6d366b9dfa53db145e5e047a37a7e2a8e304a7038028d94a1fd034ca2c31` | 直前Work Unitの独立ReviewとDeviation境界 |
| 6 | `docs/project/phases/phase_2/history/operations/phase_2_0_capability_contract_redesign_after_p2_0_wu_003_20260811231332.md` | 116 | `1a40e0f32e50e474ade8ed4928b08b1bdec3b2bf39a8166314b889a083114cbf4d13041ba2a8d74a42f469cb28664a88a6930a6f41b1ec32dc037e8637e71b24` | 再設計DecisionとP2-0-WU-004候補境界 |

## 4. Read Capability Contract

```text
Capability             : bounded_documentation_read／exact_single_target_read
Target Source          : this Manifest exact entries only
Target Cardinality     : one exact target per invocation
Required Identity      : existing regular file／non-symlink
Required Coverage      : complete content
Required Integrity     : exact line count + SHA-512
Directory Discovery    : deny
Search／Glob／Recursion : deny
Batch Capability       : unavailable／deny
Artifact／Cache／Log    : deny
External／Git／Secret   : deny
```

Providerは`whole_text_read／ranged_text_read／provider_native_text_read`から、Exact Target、Coverage、Truncationおよび現在Capabilityに適合するInvocation Classを選択する。Raw Command名は本Manifestで固定しない。

各Entryについて、実際のInvocation Class、Exact Target、Observed Line Count／Digest、Coverage、Provider Traceの有無およびDeviationをResultへ記録する。

## 5. Exact Result Contract

```text
Exact Result Path:
docs/project/phases/phase_2/history/operations/phase_2_0_documentation_capability_conformance_result_p2_0_wu_004_20260811233209.md

Capability             : bounded_documentation_create
Allowed Action         : create one regular UTF-8 Markdown file
Creation Cardinality   : exactly one
Existing File Mutation : zero
Additional Artifact    : zero
Permission／ACL        : zero
Git／External／Secret   : zero
```

Resultへ次を含める。

1. Control Package Identity。
2. Consumed Manifest 6件とCoverage。
3. Capability SemanticsとProvider Mapping Mode。
4. EntryごとのInvocation Class／Provider Trace Availability／Deviation。
5. Authority、Scope、Capability Semantics、Provider Mapping、Result、EvidenceおよびStop／Recoveryの自己評価候補。
6. P2-0-WU-003を遡及変更していないこと。
7. Mutation Report。
8. Missing Information／Contradiction。
9. First Safe Next Action。

Result自身の最終Line Count／SHA-512は本文へ自己埋込みせず、作成後の会話ReportとController Reviewに保持する。

## 6. Stop Conditions

- Control Package、Manifest Entry、Line CountまたはSHA-512不一致。
- Exact Targetが不存在、Directory、SymlinkまたはUnreadable。
- 一つのProvider Invocationが複数Targetを処理した、またはTarget分離を証明できない。
- Output Truncation、Coverage Gap／OverlapまたはProvider Trace不明を解消できない。
- Exact Result Pathが既に存在する、または一回のCreateで完了できない。
- Directory探索、Search、Glob、Recursive Traversal、追加ArtifactまたはScope拡張が必要。
- Authority、最上位規則、Human Gate、Provider ResourceまたはContextにConflictがある。

Stop後はCleanup、Delete、Rollback、二回目のPatch、代替Scopeまたは自動Retryを行わない。

## 7. Non-elevation

本Manifestの存在は、Envelope Acceptance、Task作成、READY、Start、WriteまたはPhase 2-A Authorityを生成しない。Exact Package全体のユーザーAcceptanceとTwo-key Startを別途必要とする。
