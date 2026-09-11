# Phase 9-2 User Mac実画面テスト—当初項目・途中結果・方針変更前Input

```yaml
document_id: phase_9_2_user_mac_original_manual_checklist_partial_result_and_strategy_change_input_20260910093525
document_type: append_only_user_manual_evidence_and_interrupted_checklist
document_state: manual_run_interrupted_by_accepted_strategy_change
phase: phase_9
program: phase_9_2
language: ja
recorded_at: 2026-09-10 09:35:25 JST
decision_authority: user
controller: codex
browser_manual_performed_by: user
real_model_run_in_this_recording_action: false
source_or_test_mutation_in_this_recording_action: false
git_authority: not_granted
append_only: true
```

## 1. 本書の目的

Phase 9-2のUser Mac実画面テストについて、予定変更前の確認項目、ユーザーが実施した範囲、画面上の実測、ControllerがSource照合で確認した仕様と欠落、および未実施のまま中止した項目を、後から混同しない形で保存する。

本書は、Phase 9-2 Complete、User Acceptance、UI修復完了またはPhase 9-3開始をClaimしない。

## 2. 予定変更前の正本入口

以前の実画面ChecklistのAppend-only正本Inputは次である。

- `docs/project/phases/phase_9/history/operations/phase_9_2_r5_user_mac_manual_recheck_checklist_ja_20260907163554.md`

同書は、次の三系統を確認対象としていた。

1. Fixtureで2 Variantを実行し、比較表とComponent別Evidenceを確認する。
2. 同一Production Plan内でMain-onlyとMain + Gemma Judge／Repair ENFORCEを順次実行する。
3. Live ConfigurationがVariant宣言と一致しないとき、Typed RejectとCall 0を確認する。

2026-09-09のWhole Scope Review 3／R4受入後は、次のBackend成立範囲がその前提となった。

- Plan／Run／Variant／Request Identityの分離。
- Frozen Configuration／Provider Identity／Raw Evidence／Comparison／Restart Read。
- FreshnessのFalse PASS防止。
- Hidden Variant Factorの排除。
- Repair requesterとRepair Call／Adoptionの一致。
- Fixture EvidenceをProduction Evidenceへ昇格しない境界。

関連受入記録：

- `docs/project/phases/phase_9/handoffs/phase_9_controller_phase_9_2_whole_scope_independent_review_3_r4_acceptance_result_ja_20260909130912.md`
- `docs/project/phases/phase_9/handoffs/phase_9_codex_phase_9_2_whole_scope_r4_evidence_truth_rework_exact_return_ja_20260909125404.md`

## 3. 予定していた実画面テスト全体

### 3.1 Fresh Runtime／Button表示

開始前に次を設定する予定だった。

```text
Main Governance : OFF
Guard            : OFF
Judge            : OFF
Repair           : OFF
Recording        : OFF
Main Provider    : Qwen3 4B / Active
Judge Provider   : Gemma Configured / Active none
Guard Provider   : Qwen3Guard Configured / Active none
```

右上の「実験（Phase 9-2）」を開き、次を確認する予定だった。

- 「実験 — Multi-Governance比較（Phase 9-2）」が開く。
- Experiment ID、Preset Case、Variant、実行Mode、Plan作成が表示される。
- 右上の実験Button、Plan作成、実行Buttonが青系で読みやすい。
- 詳細／閉じるButtonの文字と背景を明確に判別できる。
- 実行中に中止Buttonが表示される場合は赤系である。
- 灰色背景と白文字の組合せで読みにくい状態がない。
- 開いただけで赤いErrorが出ない。

### 3.2 Fixture比較

- `Fixture（安全・実Modelなし）`を選ぶ。
- 少なくともBaselineとJudge OBSERVEの2 Variantを同一Planで選ぶ。
- 両Variantを各1回実行する。
- 両Runの`completed`、2 Rowの比較表、Fixture表示、Metric／評価／Raw Evidence参照、Component Call差を確認する。

Whole Scope確認では、実装済みのRevision付きSemantic Case／Fixture Variantが、Plan→Run→Raw Evidence→Comparison→Restart Readの経路で假のPASSを作らないことも後続確認候補だった。ただし、全Presetを同時実行すること自体を必須とはしていない。

### 3.3 Freshness／Semantic Case

- Current Valueを実回答で採用した場合だけPASS相当になる。
- Current Valueの単な文字列出現、引用、否定、無関係な回答はPASSにならない。
- Productionで観測していないSemantic EvidenceをFixtureで補わない。

### 3.4 同一Production Planの2 Variant

- `Production（実Turnを1回実行）`を選ぶ。
- `Production: Main only`と`Production: Main + Judge/Repair ENFORCE`を同一Planへ入れる。
- Main-onlyを全Mode OFFで実行する。
- 完了後、Judge ProviderをGemmaにし、Judge／RepairをENFORCEへ変更する。
- 同一PlanのJudge／Repair Variantを実行する。
- 2 Runが`completed`、同一Experiment IDの2 Row、異なるDesired／Frozen Config Digest、Main／Judge／Repairの実測Call、未観測と確定Call 0の区別を確認する。

### 3.5 Wrong Live ConfigurationのTyped Reject

- Judge／Repair ENFORCEのまま、Judge／Repair OFFを宣言するMain-only Variantを再実行する。
- `live_config_mismatch`相当で拒否される。
- Runが`running`のまま残らず、成功Rowへ混入せず、新しいModel Callを実行しない。

### 3.6 当初の終了処理

- Judge／RepairをOFFに戻す。
- 追加のSelene、DeepSeek、Guard、RAG、Web、Dev Agent試験は行わない。
- Experiment ID、Case ID、Variant／Run ID、Digest、比較表、Component別Evidence、Failure／違和感、Server Errorがあれば返却する。

## 4. 2026-09-10 User Mac実施範囲と実測

ユーザーはFresh UIから確認を開始し、次を実測した。

1. 「比較するVariant」で複数のCheckboxを選択できた。それがFixture以外の実Model Runでも意図されたものか、実モデルを複数同時にLoad／実行するRiskがないか、疑問が生じた。
2. 中止Buttonを画面上で発見できなかった。
3. 中止できず、Experiment画面を閉じて開き直しても、ModeやPlan条件を切り替えられなかった。
4. 詳細Evidenceをクリックしても無反応に見える場合があった。
5. 「詳細Evidence（Component別）」が表示されても、実行中か完了済みかが明確ではなく、その後も別Modeを試せないロック状態が続いた。
6. Component別詳細が、比較表系の操作を2回行わないと出ないように見える場合、または出ない場合があった。
7. 次の実験条件へ戻すために、Browser Reloadが必要だった。

ボタン配色の最終PASS／FAIL、赤Errorの有無、Experiment／Run ID、実行回数、個別RunのTerminal StateおよびServer TerminalのErrorは、当該報告文で明示されていない。本書はこれらを推測で補完しない。

## 5. Controller Source照合

### 5.1 複数Variantの意味

複数Variant選択は、同一Plan／Caseで条件差を比較する意図である。各Variantは個別の実行Buttonで順次実行され、複数の実ModelをCheckbox選択だけで同時実行する設計ではない。

ただし、現UIはこの意味、順次実行、Live Configuration変更、Resource消費および実行中排他を十分に説明していない。

### 5.2 Cancel導線

中止Buttonは、比較表のRun Rowが非Terminalのときだけ表示される。Run Rowの更新前、表が見えない場合、または既にTerminalの場合は表示されない。これはBackend Cancel機能の不在ではないが、利用可能な実画面Cancel導線として不十分である。

### 5.3 Plan LockとBrowser Reload

Plan作成後は`planReady=true`により、Experiment ID、Case、VariantおよびExecution Modeが無効化される。Plan Immutable自体は比較の一貫性を守る意図であるが、「新しいPlan」、「現Planを破棄」または安全なResetが存在しない。

Experiment PanelはApp上にMountされたまま`open=false`で非表示になるため、閉じて開き直してもStateが保持される。そのため、Browser Reloadが事実上のResetになっていた。

### 5.4 詳細Evidenceの無反応

詳細取得中のLoading表示、取得失敗のError表示、Retry導線がない。Fetch失敗時は詳細Dataを`null`にしたままにするため、画面上では無反応に見える。

「2回操作しないと出ない／出ない場合がある」の個々のEvent Sequenceは、Browser Network LogとRun IDが保存されていないため一意の根本原因まで断定しない。ただし、失敗を無反応に見せるUI欠落はSource上で確認できる。

## 6. 当初ChecklistのDisposition

| 項目 | 状態 | 根拠 |
|---|---|---|
| Fresh UIのPanel Open | `OBSERVED` | Panel内操作と問題がユーザーから報告された |
| Button配色・赤Errorの最終確認 | `NOT RECORDED` | 報告に明示なし |
| Fixture比較 | `INTERRUPTED / NOT ACCEPTED` | Cancel／Reset／詳細導線の問題で継続せず |
| Freshness／Semantic Case | `NOT RUN IN THIS MANUAL` | 予定変更 |
| Production Main-only | `NOT RUN IN THIS MANUAL` | 予定変更 |
| Production Main + Gemma | `NOT RUN IN THIS MANUAL` | 予定変更 |
| Wrong Live Configuration Reject | `NOT RUN IN THIS MANUAL` | 予定変更 |
| Phase 9-2 User Manual全体 | `FAIL AS CURRENT VISIBLE UI / STOPPED` | 現モーダルは通常UIとして受入できない |

## 7. この時点の判断境界

- 今回の報告は、Experiment Backend CoreのPlan／Run／Trace／Evidence／Comparison／Restart Readが失敗した証拠ではない。
- 今回の報告は、現在のMinimal Experiment UIのPlan Lifecycle、Cancel導線、Details StateおよびReset経路が通常利用に十分でない証拠である。
- 本書作成時点で、ユーザーは当初の実画面テスト継続を中止し、Experiment UIのMVP優先度と後続依存を再評価する方針へ変更した。
- 方針変更の正本は、同Timestampの`phase_11_plus_experiment_workspace_ui_deferment_and_headless_core_preservation_reservation_ja_20260910093525.md`とする。

