# MARGPA Runtime LLM 共通プロジェクト引き継ぎ

```yaml
document_state: current
created_at: 2026-07-19 14:25:58 JST
supersedes: common_project_handoff_20260718193435.md
project_root: margpa-runtime-llm/
```

## 1. 文書の目的

本書は、設計者役、実装者役、対外向けDocs作成者役など、複数タスク間で共有するプロジェクト共通情報の正本である。

タスク開始時は、まず最新の`documentation_index_YYYYMMDDHHMMSS.md`を読み、そこから現在有効な要件、Architecture、Governance、ADR、Operations、Handoff、User Manualを確認する。

Docsは原則として読み取り専用で扱い、担当範囲外の文書を勝手に変更しない。

## 2. プロジェクト識別情報

- Project Name: `margpa-runtime-llm`
- Display Name: `MARGPA Runtime LLM`
- 通称: `Nazuna Research Governance LLM`
- Project Root: `margpa-runtime-llm/`
- Shared Documentation Root: `margpa-runtime-llm/docs/`
- 初期実行環境: Apple M2 Pro、16GB RAM、macOS、Apple Silicon
- 初期Main Model: `Qwen3-4B-Q4_K_M.gguf`
- 初期Guard Model候補: `Qwen.Qwen3Guard-Gen-0.6B.Q8_0.gguf`
- 初期Judge Model候補: `Selene-1-Mini-Llama-3.1-8B-Q5_K_M.gguf`

ユーザーが`docs/`などの相対的なProject内パスだけを示した場合、Project Rootを基準として解釈する。

## 3. 現在有効な共通規則

- Documentation Rules: `docs/requirements/documentation_rules_20260719142558.md`
- Task Role Write Authority Policy: `docs/requirements/task_role_write_authority_policy_20260719142558.md`
- Phase Completion Backup Policy: `docs/operations/phase_completion_backup_policy_20260719142558.md`
- Current Roadmap: `docs/architecture/implementation_roadmap_20260719142558.md`
- Current Documentation Index: `docs/documentation_index_20260719142558.md`

文書名は英小文字と`_`を基本とし、末尾に作成時刻を秒まで含む`_YYYYMMDDHHMMSS`を付ける。既存文書は原則変更せず、変更時は新Timestampの後継文書を作る。新しいTimestampの文書を、その系列の最新候補として扱う。

## 4. タスク間の情報伝達

タスク間の情報伝達、進捗報告、レビュー結果、開始指示は、原則として`docs/`以下のTimestamp付き文書を介して行う。

主要な文書種別は次のとおりである。

- 要件・共通規則: `docs/requirements/`
- Architecture・Roadmap: `docs/architecture/`
- Governance設計: `docs/governance/`
- 意思決定記録: `docs/adr/`
- 運用・Backup・Release記録: `docs/operations/`
- タスク間Handoff・Status・Review: `docs/handoffs/`
- User Manual: `docs/user_manual/`
- 公開向け文書候補: Repository直下のREADME類、将来の`docs/public/`

## 5. 役割別の権限

詳細な正本は`task_role_write_authority_policy_20260719142558.md`とする。

### 5.1 設計者役

設計者役は、要件、Architecture、Governance、ADR、Operations、User Manual、Documentation Index、共通Handoff、設計者Handoff、各担当の開始用Handoffを管理する。

実装レビュー時は`src/`、`tests/`、`config/`、`scripts/`などを読み取り専用で確認し、ユーザーから修正を明示されていない限り、実装を勝手に修正しない。

### 5.2 実装者役

実装者役は、受理済みHandoffとユーザーの実装許可の範囲内で、`src/`、`tests/`、`scripts/`を変更し、`docs/handoffs/implementer_status_*`へ実装報告を新規作成する。

`config/`、Root直下のBuild・Dependency・Environment関連ファイルは、受理済みの設計またはHandoffで明示された場合に限り変更対象となる。

要件、Architecture、Governance、ADR、Operationsなどの正本文書は読み取り専用である。

### 5.3 対外向けDocs作成者役

対外向けDocs作成者役は、README類、将来の`docs/public/`、`docs/handoffs/external_docs_status_*`を担当する。

要件、Architecture、Governance、ADR、Operationsの正本は読み取り専用であり、公開文書へ変換する際も内容を勝手に変更しない。

### 5.4 現在の運用評価

設計者役と実装者役の分離は、Phase 1-AからPhase 1-Dまでの設計、Handoff、実装報告、独立レビューで実際に機能しており、Phase 1-Eでも同じ流れを継続している。

対外向けDocs作成者役は、現時点では十分な実運用実績がないため、権限境界は正式化するが、運用上の妥当性は今後検証する。

## 6. 現在のPhase状態

### 6.1 Phase 1

- Phase 1-A: Accepted／Complete
- Phase 1-B: Accepted／Complete
- Phase 1-C: Accepted／Complete
- Phase 1-D: Accepted／Complete
- Phase 1-E: Design Accepted／Implementation Reported／Independent Review Pending

Phase 1-Eについて、ユーザーから実装完了らしいとの共有はあるが、設計者役による最新Status、関連Source、Config、Testsの独立レビューはまだ完了していない。

したがって、Phase 1全体はまだ完了宣言前であり、Phase 1 Backupの発火条件にも達していない。

### 6.2 Phase 2以降

Phase 2以降の再構成済みRoadmapと主要Architecture方針は存在するが、Phase 2の実装はまだ開始しない。

## 7. Reviewの標準手順

1. 実装者役がTimestamp付きStatusを新規作成する。
2. 設計者役が最新Statusと関連実装を読み取り専用で確認する。
3. 受入条件、Test、回帰、文書整合性を確認する。
4. 問題があれば、Reviewと新しい実装者向けHandoffを作る。
5. 問題がなければ、Accepted Reviewを作る。
6. Reviewと同じ時点の新しいDocumentation Indexを作る。

Review後は、原則としてReview文書とDocumentation Indexを一緒に新規作成する。

## 8. Phase完了とBackupの発火条件

Backupは、実装者役が完了を報告した時点や、Phase内のSubphaseが完了した時点では取得しない。

各Top-Level Phaseについて、受入条件、独立レビュー、必要なFollow-up、User Manual、Indexなどを完了させ、設計者役がユーザーへ明示的に次の趣旨を宣言した直後をBackup取得タイミングとする。

> Phase Nは完了です。次はPhase N+1です。

全Phaseで同じ条件を用いる。Backup取得は次Phaseの実質的な変更開始より前に行う。

具体的なArchive、Manifest、SHA-512、除外対象、保管先、復元確認は`phase_completion_backup_policy_20260719142558.md`に従う。

この共通Handoffを読むこと自体は、Project外へのBackup作成や外部書き込みを許可しない。

## 9. 現在の次作業

1. 最新のPhase 1-E実装者Statusを特定して読む。
2. Phase 1-E関連のSource、Config、Testsを独立レビューする。
3. 必要ならFollow-up Handoffを作成し、実装修正後に再レビューする。
4. Phase 1全体の受入条件、User Manual、Docs、Indexを最終確認する。
5. 設計者役がPhase 1完了を明示する。
6. その直後にPhase 1 Backupを取得する。
7. Backup検証後、Phase 2へ移行する。

現時点では、Phase 1-Eの独立レビュー、Phase 1完了宣言、Phase 1 Backup、Phase 2実装のいずれも未完了である。
