# Claude Fresh設計者兼実装者役Task Activation Sequence Reservation

```yaml
document_id: claude_fresh_designer_implementer_task_activation_sequence_reservation_20260826094454
status: reserved_not_activated
classification: planned_operating_work
created_at: 2026-08-26 09:44:54 JST
target_provider: claude
target_role: 設計者兼実装者役
task_creation_authority: not_granted_by_this_document
execution_authority: not_activated_by_this_document
git_authority: not_granted_by_this_document
```

## 1. 予約目的

Claudeの週間利用可能量および5時間制限が回復し、Phase 6以降の作業へ再投入できる時点で、長大化した旧Taskをそのまま再利用せず、Fresh Contextの新Taskを「設計者兼実装者役」として起動する手順を予約する。

この予約の目的は、Claudeの利用可能量を増加またはResetすることではない。旧Context、Auto Compaction後の曖昧な状態、撤回済みAuthority、旧仕様および過去の途中状態を新しいExecution Contractへ混入させず、Frozen DocsからCleanに開始することである。

本書はTask作成、Claude実行、Docs Mutation、Source Mutation、Network、GitまたはPhase Startを許可しない。

## 2. Role変更予約

Claude側TaskのRole名は、従来の`設計統括者役`から、実際の責務に一致する`設計者兼実装者役`へ変更する。

```text
Before : Claude／設計統括者役
After  : Claude／設計者兼実装者役
```

ClaudeはProject全体の最終設計統括者、最終Authority、Independent Closure判定者またはUser Authority代理ではない。Frozen Contractに基づき、詳細設計、工程分解、実装、Test、Recovery、自己ReviewおよびExact Reworkを担当する。

Project全体の設計統括、Authority Freeze、Independent Review、Rework判定およびClosure Recommendationは、Codexの`プロジェクト責任者兼設計統括者役`が担当する。

## 3. 旧Taskと新Task

Claude復帰時は、旧Taskを過去Evidence参照用として保持し、新Taskを作成する。

```text
旧Claude Task
  -> Historical TaskとしてRename
  -> 例: 元Claude設計者兼実装者役_1
  -> 原則として新規実装の送信先にしない

新Claude Task
  -> Role: 設計者兼実装者役
  -> Fresh Context
  -> 旧会話Context／Provider Memory／Authority／未完了状態を非継承
```

旧TaskのExact Renameは、Claude側UIで衝突しない名称をUserがActivation時に決める。旧Taskを削除することは本予約の要件ではない。

## 4. Activation前の必須順序

新Claude Taskには、実装用の大量Docsを最初から一括投入しない。次の順序を守る。

### Step 1 — Role／Task Identity固定

新Taskへ、少なくとも次を宣言する。

```text
Provider      : Claude
Role          : 設計者兼実装者役
Task Identity : Activation時に固定
Old Context   : NOT INHERITED
Execution     : NOT STARTED
```

### Step 2 — Authority通知

Codexの`プロジェクト責任者兼設計統括者役`から、最初に次だけを通知する。

1. 実行Authorityの成立条件。
2. Docs取扱Authority。
3. Authorized Root。
4. 許可対象Mutation Class。
5. 禁止対象とTrue Stop Condition。
6. Return Handoff経路。

この通知は`GRANTED_BUT_NOT_ACTIVATED`として扱い、通知だけで実装を開始させない。

### Step 3 — Claude側運用メモ2文書の全文読了

次の2文書を、実装Handoffより前に全文読ませる。

1. `docs/project/shared/task_roles/claude_side_design_governor_operating_notes_ja.md`
2. `docs/project/shared/task_roles/claude_side_long_running_automation_companion_ja.md`

1件目のFile名にはHistoricalな`design_governor`表現が残るが、Activation時のCurrent Role名は`設計者兼実装者役`である。File名だけを根拠に最終設計統括Authorityを再生成してはならない。

### Step 4 — Preflight Receipt

新Taskは、少なくとも次を返す。

- 2運用メモの全文読了。
- 旧Context／旧Authority非継承。
- Current Role理解。
- AuthorityとActivationの分離。
- Docs取扱境界理解。
- 実装未開始。

### Step 5 — Current差分Handoff作成

Claude復帰時点のCodex実装結果、Open Finding、Acceptance、Recovery、Resource残量およびUser方針から、Claude専用のCurrent差分HandoffをCodex Controllerが作成する。

Codex実装済み範囲をClaudeへ最初から重複実行させない。Claudeの初期投入先は、原則として次のいずれかとする。

- Independent Review。
- Open Findingに対するExact Rework。
- 未実装Packageの差分継続。
- Codex Resource停止後のRecovery Entryからの差分再開。

### Step 6 — 必要Docsだけを配送

Current差分Handoffが指定するMandatory Readingを、正本順序とExact Pathで渡す。旧Taskの会話要約やProvider Memoryを正本代替として使用しない。

### Step 7 — Exact Start

Userの開始宣言または事前にFreezeされたTwo-key Activationを満たした後、`GRANTED_BUT_NOT_ACTIVATED`から`ACTIVATED`へ遷移させ、Long Runを開始する。

## 5. Long Run規則

- Frozen Objective、Acceptance、ScopeおよびAuthorityを変更しない。
- 通常の設計判断、実装、Testおよび自己修正で逐一Userへ確認しない。
- Package／Material BoundaryごとにRecovery Indexを残す。
- Auto Compactionまたは5時間制限後は、完了済みPackageを再実行せず差分再開する。
- 単なる途中進捗報告を理由に停止しない。
- True Stop、Resource Safe Stop、Complete CandidateまたはUser明示Stopまで継続する。
- `Complete`、`違反0`、`全PASS`等の強い主張は、Exact ScopeとEvidence Gradeを伴わせる。
- Git、Closure、次Phase、Network、External Service、Provider MemoryおよびUser Dataは、別途Authorityがなければ扱わない。

## 6. Return経路

ClaudeからCodex Taskへの直接通信がActivation時に実測確認できない場合、Repository内HandoffとUser Relayを正規経路とする。直接送信できない状態で`Codexへ返送済み`と主張してはならない。

Return Handoffには、少なくとも次を含める。

- Provider、Role、Task Identity。
- Handoff Revision／Digest。
- Completed／Not Executed／Deferred。
- Changed Paths。
- ValidationとEvidence Grade。
- Open Finding。
- Compaction／5時間制限／Resource状態。
- Scope／Authority／Incident Accounting。
- Exact Next Action。

## 7. Activation Gate

```text
Claude Weekly／Five-hour Availability : USER CONFIRMATION REQUIRED
Fresh Claude Task                     : NOT CREATED BY THIS DOCUMENT
Current Task Identity                 : NOT ASSIGNED
Authority Notification               : RESERVED
Operating Notes Reading              : RESERVED
Current Delta Handoff                : NOT CREATED
Exact Start                          : NOT DECLARED
Long Run                             : NOT STARTED
```

## 8. 後続Evidence予約

本予約を実際に使用した場合は、成功、失敗、途中停止または未完了を問わず、結果を次へAppend-onlyで記録する。

`docs/project/shared/history/automation/`

少なくともTask再生成、旧Task Retention、Authority Receipt、運用メモ読了、Current差分Handoff、Long Run、Compaction／5時間制限、Review、ReworkおよびResource消費傾向を含める。
