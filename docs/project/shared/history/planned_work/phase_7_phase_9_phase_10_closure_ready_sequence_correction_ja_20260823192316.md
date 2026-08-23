---
document_id: phase_7_phase_9_phase_10_closure_ready_sequence_correction_ja_20260823192316
status: planned_schedule_correction_not_started
document_type: append_only_planned_work_schedule_correction
language: ja
recorded_at: 2026-08-23 19:23:16 JST
decision_authority: user
applies_to:
  - phase_7_ready
  - phase_9_closure
  - phase_10_ready
schedule_correction_only: true
current_implementation_authorized: false
current_git_mutation_authorized: false
current_backup_operation_authorized: false
parent_directory_write_authorized: false
---

# Phase 7／Phase 9／Phase 10 Closure・READY順序変更予約

## 1. 決定

利用可能量の枯渇によってPhase 9 Closureが中途半端な状態で停止するRiskを避けるため、Phase 7 READY、Phase 9 Closure、Phase 10 READYの作業順序を変更する。

本書は既存予約の内容を削除せず、**実行時期と順序だけを訂正するAppend-only Scheduling Correction**である。既存予約に含まれる成果物要件は、明示的に廃止されたものを除いて維持する。

## 2. 新しい全体順序

```text
Phase 6 Special／Minimal Closure
  ↓
Phase 7 READY
  ↓
Commit／Push
  ↓
User Backup
  ↓
Phase 7 Preflight／Activation
  ↓
Phase 7〜9 Execution
  ↓
Phase 9 Special／Minimal Closure
  ↓
Phase 10 READY
  ↓
Phase 3〜9累積Docs統合
  ↓
Portable Development Governance Package作成
  ↓
Clean／Commit／Push
  ↓
User Backup
  ↓
次作業のPreflight／Activation
```

## 3. Phase 7 READYの共通Gate

Phase 7をREADY状態へ移した後は、次の順序を正本とする。

1. Phase 6のMinimal Technical ClosureとPhase 7 READY判定を完了する。
2. Current／Roadmap／Phase Index／Recovery Entry等、最小Closureに必要な状態文書を整合させる。
3. Working Tree、Stage対象、Privacy／Secret／不要物、Publication SanitationをCommit／Pushに必要な範囲で確認する。
4. Commitする。
5. Pushする。
6. Local HEAD、origin、GitHubの一致を確認する。
7. ユーザーがBackupを取得する。
8. 必要に応じてBackup名、Size、SHA-512、復元可能性をEvidence化する。
9. Phase 7のPreflight、Authority確認、READY／ARMED、開始宣言へ進む。

Commit／Pushが成立していない場合は、Backup後GateまたはPreflightへ進んだと偽ってはならない。Backup作成自体はユーザー操作を正本とし、AI側が無断でBackup置場へ接触してはならない。

## 4. Phase 9 ClosureはPhase 6型のSpecial／Minimal Closureへ変更

Phase 9 Closureでは、大規模な累積Docs統合を実施しない。Phase 6で採用したSpecial／Minimal Closureと同じ考え方を適用し、Phase 9を技術的・状態的に閉じてPhase 10 READYへ到達することを優先する。

最低限のClosure対象は次のとおり。

- Phase 9 Acceptance結果、重大Finding、Deferral、User Acceptanceを正確に記録する。
- Phase 9 Phase Index、Current Status、Recovery Entry、Handoff、通常版`roadmap_ja.md`の必要箇所を更新する。
- Phase 9時点の人向けRoadmap要約版を作成または最終更新する。
- Phase 9時点のPublic Technology Selectionを作成し、採用技術だけでなく不採用技術と不採用理由も記録する。
- Phase 3〜9のFull Closure／累積Docs統合がPhase 10 READYへ移されたことを明記する。
- Phase 9完了とPhase 10 READYを、未完了作業を隠さず区別して宣言する。
- `.claude`等の不要なProvider-local Artifactは、当該時点のユーザー指示とExact Mutation確認に従って処理する。予約だけを削除権限とみなさない。

以下はPhase 9 Closureでは実行しない。

- Phase 3〜9の累積Lossless Docs統合
- `docs/project/shared/constitution/`の完全再編成・Freeze
- Project固有成分を除いた移植用Packageの生成
- `MARGPA-RUNTIME-LLM/`直下への外部Package書込み

これにより、Docs統合途中で利用可能量が尽き、Phase 9自体のClosure判定まで未完了になるFailureを避ける。

## 5. Phase 10 READYへ移す作業

Phase 9 Closure後、Phase 10 READY状態で、次の順序により旧Phase 9 Closure予定の統合作業を行う。

1. Phase 3〜9のCurrent／Shared／Phase／History／Automation／Cross-provider／Compaction／Role／Authority／EvidenceをLosslessに再照合する。
2. 重複、旧正本、履歴、現行正本、Deferralを区別し、累積Docs統合を完了する。
3. Codex／Claude等のProviderに依存しない上位規範、制度、運用Ruleを`docs/project/shared/constitution/`へ再編成する。
4. Rule優先順位、Authority、最上位規則、禁止事項、Docs正本、Task Lifecycle、Handoff、Evidence、Resource、Stop／Recovery、Amendment等を完全Losslessな体系へまとめる。
5. Portable Development Governance Packageを、統合済み正本から派生生成する。
6. Packageから本Project固有成分を除去し、新規／途中の別Projectへ現開発体制を移植できるか検証する。
7. Phase 1-ex相当は移植用構造ではPhase 1へ統合し、Phase 1にも`history/index/`を持たせる。
8. Link、Path、Privacy、Secret、Project固有値、Provider-local Memory依存、外部参照、移植後のBootstrap手順を検証する。
9. Current／Roadmap／Index／Manifest／Handoffを統合後状態へ追随させる。
10. Working Treeを確認し、Commit／Push対象を確定する。
11. Commitする。
12. Pushする。
13. Local HEAD、origin、GitHubの一致を確認する。
14. ユーザーがBackupを取得する。
15. 必要なBackup Evidenceを確認する。
16. 次作業のPreflight、Authority確認、Activationへ進む。

## 6. Portable Packageの外部Write Gate

Portable Packageの予定配置先は、Project Rootである`margpa-runtime-llm/`の外側、`MARGPA-RUNTIME-LLM/`直下である。

したがって、本予約は外部Writeを許可しない。Phase 10 READYで作業するときは、以下を満たす必要がある。

- ユーザーがExact Parent RootとExact Destination Folderを明示する。
- Project Root外Writeについて、その時点で明示的Authorityを付与する。
- Source側の正本と移植用派生Packageを混同しない。
- Copy元、Copy先、除去対象、Sanitation結果、Manifest、DigestをEvidence化する。
- 外部PackageからSource側へ逆流する暗黙同期を作らない。

## 7. 利用可能量とRecovery境界

Phase 10 READYの統合作業は高Costであるため、意味のある大区切りごとにRecovery Entry／Current Position／差分Manifestを残す。Task単位の過剰な全文Snapshotは避けるが、Compaction、利用制限、Provider交代後に差分から再開できる粒度は維持する。

利用可能量が不足した場合は、以下を守る。

- 未完了をCompleteと宣言しない。
- 途中状態をStable正本へ昇格しない。
- 最後に完了したMaterial Boundaryと未完了範囲を明記する。
- Commit／Push／Backup／Preflightのどこまで成立したかを分離して記録する。
- 次回はRecovery Entryから差分再開する。

## 8. 既存予約との関係

次の既存予約は、成果物要件を維持する。

- `phase_9_closure_roadmap_summary_reservation_ja_20260823154121.md`
- `phase_9_closure_public_technology_selection_reservation_ja_20260823163417.md`
- `phase_9_closure_claude_local_artifact_cleanup_reservation_ja_20260823154121.md`
- `phase_10_ready_portable_development_governance_package_reservation_ja_20260823154121.md`
- `phase_6_interim_and_phase_9_final_roadmap_summary_reader_facing_requirements_ja_20260823185543.md`

ただし、**Phase 3〜9累積Docs統合とPortable Package作成の実行時期はPhase 10 READY**を正本とする。既存文書にPhase 9 Closureでの統合を示す記述がある場合、そのScheduling部分だけを本書が上書きする。

## 9. 非承認事項

本書を作成した時点では、次を開始しない。

- Phase 7、Phase 9、Phase 10の実装
- Docs統合
- Constitution編纂
- Portable Package作成
- Project Root外Write
- Git Stage／Commit／Push
- Backup作成またはBackup置場への接触
- 次PhaseのPreflight／Activation

各工程は、到達時点のAuthority、Exact Scope、User Gateに従って開始する。
