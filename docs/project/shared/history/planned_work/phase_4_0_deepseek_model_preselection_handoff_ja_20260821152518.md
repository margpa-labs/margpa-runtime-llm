# Phase 4-0 DeepSeek Model事前選定 — 設計者兼実装者役Handoff

```yaml
document_id: phase_4_0_deepseek_model_preselection_handoff_20260821152518
status: ready_for_user_activation_not_started
phase: phase_4_pre_entry
subphase: phase_4_0_preselection
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-21 15:25:18 JST
language: ja
document_class: append_only_planned_work_handoff
authorization: ユーザーによる2026-08-21の設計・Handoff作成指示
execution_authority: not_granted_by_this_document
```

## 1. Mission

Phase 3とは独立して、Phase 4 Entryで採用候補となるDeepSeek公式Open WeightをRead-only調査し、Main Primary Candidate、Fallback Candidate、Qwen比較BaselineおよびPhase 4 Final Freeze Gateを確定候補として提示する。

本TaskではDownload、Model Load、Benchmark実行、AWS構築、Source実装、Stable Docs更新、Roadmap更新またはGit操作を行わない。

## 2. Activation Gate

本Handoffは実行可能な設計Packageであるが、作成だけではTask開始を意味しない。

次が揃った場合だけ開始する。

1. ユーザーが設計者兼実装者役へ本Handoffを指定する。
2. ユーザーが事前選定調査の開始を明示する。
3. 設計者兼実装者役がFrom／To、Project Root、Read Scope、Write Scope、禁止事項および停止条件をNo-toolでACKする。

ACK前にToolを使わない。

## 3. Mandatory First Read

次の順に読む。

1. `docs/project/shared/history/planned_work/phase_4_0_deepseek_model_preselection_design_ja_20260821152518.md`
2. `docs/project/shared/conventions/documentation_rules_ja.md`
3. `docs/project/shared/operations/research_asset_mutation_control_ja.md`
4. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
5. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
6. `docs/public/roadmap_ja.md`のPhase 3境界、Phase 4 Entry CandidateおよびCurrent Model Strategy。
7. `docs/project/shared/history/planned_work/future_scope_proposal_aws_deployment_ja_20260818171240.md`
8. 設計書第8節のCurrent Model／Model Port／Backend Read Scope。

Conflict時は、ユーザー指示、最上位規則、Current Shared Policy、本Handoff、本設計の順に解決する。Authority拡張はしない。

## 4. No-tool ACK Format

開始前に次だけを返す。

```text
ACK: P4-0 DeepSeek Preselection
Role: 設計者兼実装者役
From: プロジェクト責任者兼設計統括者役
To: 設計者兼実装者役
Project Root: <current project root>
Mode: Read-only research plus three new append-only result files
Phase 3 Mutation: PROHIBITED
Stable Docs Mutation: PROHIBITED
Source/Test/Config Mutation: PROHIBITED
Model Download/Load: PROHIBITED
AWS/External Account Mutation: PROHIBITED
Git Mutation: PROHIBITED
Root-outside Filesystem Access: PROHIBITED
Ready: YES
```

## 5. Execution Sequence

```text
P4-0-SEL-001 Current Contract Recovery
  -> P4-0-SEL-002 Official Candidate Inventory
  -> P4-0-SEL-003 Artifact／Backend Feasibility
  -> P4-0-SEL-004 Hardware／AWS Feasibility
  -> P4-0-SEL-005 Vector Evaluation
  -> P4-0-SEL-006 Recommendation／Freeze Gate
  -> Self-review
  -> Status／Handoff Return
```

途中のRoutineなUnknownはEvidence付き`unknown`として保持し、候補比較を続ける。Project Root外Filesystem、権限拡張、Credential、課金、Download、License Risk受容、Phase 4開始またはCurrent Promotionが必要になった場合だけ停止する。

## 6. Exact Write Lease

ユーザーが実行開始を明示した後、次の新規Fileだけを作成できる。

```text
docs/project/shared/history/planned_work/
  phase_4_0_deepseek_model_candidate_inventory_ja_<timestamp>.md
  phase_4_0_deepseek_model_selection_recommendation_ja_<timestamp>.md
  phase_4_0_deepseek_model_selection_status_ja_<timestamp>.md
```

- `<timestamp>`は作成時JST `YYYYMMDDHHMMSS`とする。
- 既存Fileを変更しない。
- 同じ内容を複数Fileへ重複させない。
- InventoryはSource Evidenceと候補Matrixを持つ。
- RecommendationはVector比較、Primary／Fallback、Freeze Gateを持つ。
- StatusはExact Files、検証、禁止事項遵守、Next Routeだけを持つ。
- 追加Fileが必要と感じても作らず、上記3件へ統合する。

## 7. Source Discipline

優先順位は次とする。

```text
Official DeepSeek Hugging Face／GitHub
  > Official inference-engine documentation
  > Official AWS／Hugging Face documentation
  > Research paper／technical report
  > Third-party benchmark／community evidence
```

- 全重要FactにURLと`accessed_at`を付ける。
- Web Search結果Snippetだけを最終根拠にしない。
- Model CardとFile Tree、Commit History、Licenseを直接確認する。
- Third-party Quantizationを公式Artifactと呼ばない。
- 実測していないLatency、Token/s、VRAM、QualityまたはCostを実測値と呼ばない。
- Source間Conflictは両方を記録し、無断で都合のよい方を採用しない。

## 8. Decision Requirement

単一総合Scoreで潰さず、設計書第6.5節のVectorを使う。

最低限、次を決定する。

1. Main `PRIMARY_CANDIDATE` 1件。
2. `FALLBACK_CANDIDATE` 1件以上。
3. Qwen3-4B `COMPARISON_BASELINE／RETAINED`。
4. Pro級DeepSeekをPhase 4初期へ採用するか、Research-onlyへ置くか。
5. Canonical Weight Routeと、必要ならDerived Artifact Route。
6. 最有力Backend Routeと代替Backend Route。
7. AWSでのFeasible Scenarioと、成立しない／未確認Scenario。
8. Phase 4 EntryでStale CheckするFact。
9. Download、Cost、License、AWSおよびPromotionのHuman Gate。

「情報不足なのでユーザーが全部選んでください」で終えない。技術的Recommendationを出し、人間にしか決められないGateだけを返す。

## 9. Stop Conditions

次のいずれかで即停止し、無許可修復を行わない。

- Project Root外Filesystem Accessが必要または発生した。許可済み公開Web Primary SourceのRead-only参照は除く。
- Existing File Mutationが必要または発生した。
- Phase 3、Stable Docs、Source、Test、ConfigまたはGitへ差分が生じた。
- Model Download、Package Install、Model LoadまたはBenchmark実行が必要になった。
- Login、Token、Credential、Billing、AWS MutationまたはLicense同意操作が必要になった。
- 個人情報、Secret、Local User PathまたはAccount IdentifierをOutputへ含める必要が生じた。
- 公式SourceのIdentityまたはLicenseが解決不能でPrimary CandidateのGateを満たせない。

Routineな候補不採用、Engine非対応、巨大Artifact、Quota不明またはCost高は停止条件ではない。Evidenceとして分類し、Fallbackを評価する。

## 10. Self-review

Completion前に次を確認する。

```text
[ ] Candidate list was refreshed at execution time.
[ ] Official source and third-party evidence are separated.
[ ] Every material fact has URL and accessed_at.
[ ] Unknown and estimate are not presented as measured fact.
[ ] Activated params are not treated as total memory.
[ ] Canonical and derived artifacts are separate.
[ ] HF is acquisition source, not runtime dependency.
[ ] Main model, backend, artifact, cloud, and promotion are separate.
[ ] Primary, fallback, Qwen baseline, and rejection reasons exist.
[ ] Phase 4 Final Freeze is still pending.
[ ] Exactly three result/status files or fewer were created.
[ ] Existing files, Phase 3, source, stable docs, Git, and AWS were unchanged.
[ ] Root-outside filesystem access and provider memory writes are zero; authorized public Web reading is the only external read.
```

## 11. Return Route

完了後は、設計者兼実装者役からプロジェクト責任者兼設計統括者役へ次を返す。

```text
Status: COMPLETE_CANDIDATE／ADJUST／STOPPED
Primary Candidate: <candidate>
Fallback Candidate: <candidate(s)>
Qwen Baseline: RETAINED
Created Files: <exact paths>
Model Download: NOT PERFORMED
AWS Mutation: NOT PERFORMED
Source/Stable/Phase 3/Git Mutation: 0
Root-outside Filesystem Access: 0
Major Unknowns: <list>
Final Freeze Gates: <list>
Next Action: Codex Controller Review
```

Return後は、Phase 4開始、Download、実装、AWS構築、Roadmap更新、CommitまたはPushを開始せず停止する。
