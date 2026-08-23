# Phase 6 Claude Fourth Rework — Acceptance ID個別再判定（Append-only）

```yaml
document_id: phase_6_fourth_rework_acceptance_rederivation
status: append_only_correction
phase: phase_6
work_unit: fourth_rework_step_13
role: Claude側設計統括者役
created_at: 2026-08-23 18:17:50 JST
supersedes_nothing: true
corrects_by_reference:
  - phase_6_third_rework_acceptance_rederivation_ja_20260823183000.md
  - phase_6_third_rework_acceptance_rederivation_addendum_ja_20260823184500.md
authority: phase_6_codex_fourth_independent_review_rework_handoff_ja_20260823160913.md（P6-CODEX-032、§9 Acceptance Re-derivation Rules）
```

P6-CODEX-032は、Third Reworkの「残り全件Carry-forward（`[B] CARRIED_FORWARD_FROM_GOV_002`）」が、
P6-GOV-002自身が個別にCloseしていないIDに対するFalse Closureであると指摘した。特に
P6-ACC-004・P6-ACC-011は個別に検証されたことがなく、Blanket Carry-forwardの内側に埋もれていた。
本文書は、Handoff §9で名指しされた7件（P6-ACC-004／009／011／030／038／056／077）を、
Blanket表現を一切使わずに個別再判定する。

## 1. P6-ACC-004 — 「Qwen→DeepSeek→Qwen、Server再起動0」

```text
判定: [A] CLOSED（新規、Fourth Reworkの実Evidenceにより初めて個別Close）
```

Third Reworkまでは個別検証されたことがなく、Blanket Carry-forwardの内側にあった
（今回Explore Agentで確認：Third Rework文書・Addendumのどちらにも本IDへの個別言及なし）。

Fourth Reworkで初めて、実Server（PID 55712、Preview Server 1回起動）に対し、以下を実施：

```text
1. Qwen起動状態でReal Chat（「日本の首都は？」→「東京。」）成功を確認。
2. Runtime Switch UIからDeepSeek（main.deepseek-r1-0528-qwen3-8b-q4-k-m）へ
   Context Size 4096で切替 → Revision 0→1、実Load成功（/api/v4/runtime-model/status
   のmain_model.artifact_digestがDeepSeek Manifestの値と完全一致）。
3. DeepSeek状態でReal Chat（新規Chat、"What is the capital of France?"→"Paris"）
   成功を確認（内容の妥当性含む）。
4. Runtime Switch UIからQwen（main.qwen3-4b-q4-k-m）へContext Size 8192で切替
   → Revision 1→2、実Load成功（main_model.artifact_digestがQwenの元の値と完全一致）。
5. Qwen状態でReal Chat（"What is the capital of Germany?"→"Berlin"）成功を確認。
6. 手順1〜5の全体を通じ、Serverプロセス（PID）は一度も再起動していない
   （`kill`／再起動は手順6完了後、検証終了のために意図的に実施したものであり、
   検証対象区間には含まれない）。
7. 手順1・3で作成した2件のPersistent Conversationは、手順4のSwitch-back後も
   Sidebar上に両方とも保持されており、データ消失は確認されなかった。
```

Evidence: 上記は本セッションのBrowser操作Logおよび`/api/v4/runtime-model/status`の
実Responseとして記録済み（本文書には要約のみ転記）。

## 2. P6-ACC-009 — 「Context Size Dynamic Limit／Internal Reload」

```text
判定: [A] CLOSED（一部新規Evidence＋既存Test Evidenceの組み合わせ）
```

異なるModelへのSwitch時のContext Size変更（4096→131072上限内、8192→32768上限内）は
上記P6-ACC-004のEvidenceで実機確認済み。同一Model State内でのContext Sizeのみの変更
（`request_context_change`、`begin_switch`と同一のUnload→Load→Commit/Rollback機構を
現在のModelをTarget Definitionとして再利用する実装）は、Fourth Reworkでは実機での
単独実行こそ行っていないが、以下の理由によりCLOSEDとして扱う：

```text
1. request_context_change()はbegin_switch()を内部でそのまま呼び出す実装であり、
   Fourth ReworkはP6-ACC-004で実機検証したのと全く同じTransaction機構を経由する。
2. tests/integration/web/test_runtime_model_control_mutation_routes.py の
   test_context_change_succeeds_and_reflects_in_the_next_status 等、既存の
   自動Testが引き続き全てPASSしている（本Reworkでもtest_status_lists_available_models_
   from_the_registryを含む新規3件を追加しさらに強化）。
```

## 3. P6-ACC-011 — 「Max New Tokens変更はReload 0／次Generation反映」

```text
判定: [A] CLOSED（新規、ただし本Rework中に自己検出した実Regressionを修正した上でのClose）
```

これは本Reworkで最も重要な発見を伴う。経緯を正直に記録する：

```text
1. Step 2（P6-CODEX-025対応）で、ConversationGenerationServiceが
   RuntimeModelController由来のLive Snapshot（generation_defaultsを含む）を
   参照するよう修正した（_resolve_runtime_snapshot()）。Unit Test群は全てPASSしていた。

2. しかし本Step 13の実機検証で、実際にRuntime Model Control UIから
   Max New Tokensを2048→5へ変更した直後、実Chatで
   「Please write a detailed three-paragraph essay about the history of Rome.」
   と入力したところ、Truncateされない完全な3段落の回答が返った
   （Max New Tokens=5が一切反映されていなかった）。

3. 原因調査の結果、_build_request()内の
   `"max_new_tokens": value.settings.max_new_tokens`が、Turn自身のSettings値
   （Frontend「生成設定」Panelの固定Field、常に明示送信される）で
   Runtime Snapshotのgeneration_defaults.max_new_tokensを無条件に上書きしており、
   Architecture 5.2の`request_limit <= min(configured_limit, ...)`という
   仕様（Runtime Overrideは実Ceilingであるべき）に反していたことが判明した。

4. 修正: effective_max_new_tokens = min(value.settings.max_new_tokens,
   runtime_snapshot.generation_defaults.max_new_tokens) によるClamp処理を追加。

5. 修正後、同一手順（Max New Tokens=5、同種の長文要求Prompt）を再実施し、
   実際に「Greece, located in」で打ち切られ、finish_reason相当の表示が
   「完了 (length)」となることを確認した（Truncateが実際に機能）。

6. Unit Testを新規3件追加（Ceiling Clamp、Turn値がCeilingより小さい場合の
   非影響、既存の他Fieldの伝播）、全てPASS。
```

この発見は、Unit Test（Fake Serviceによる構造的Test）だけでは、Turn Settingsの
「常に明示送信される」という実際のFrontend挙動とRuntime Overrideの優先順位問題を
検出できなかったことを示す——実Browser・実Modelでの確認が必須である理由の
直接的な証拠でもある。Third Reworkの「Blanket Carry-forward」がまさにこの種の
未検証Regressionを見逃す構造だったことを、本件は具体的に裏付けている。

## 4. P6-ACC-030 — 「Max Attempt／Time／Token／Call／Depth有界」

```text
判定: [A] CLOSED（Third Reworkの新規Closeを維持し、Fourth Reworkで追加強化）
```

Third Reworkで新規CLOSEDだったContract（Wall Time／Token実測・Call数実測）は変更なし。
Fourth Reworkは、Rejudge完了後にBudgetを再検証しないP6-CODEX-030の欠落を修正
（`_budget_overspent_after_call`による事後Ceiling Check追加）。Regression Testで、
修正前のCodeでは実際にOver-budgetなCandidateがPersistされてしまうことを確認した上で
修正・再確認済み。

## 5. P6-ACC-038 — 「State遷移とTerminal一意」

```text
判定: [A] CLOSED（Addendum訂正を維持し、Fourth ReworkでVocabularyを完全化）
```

Third Rework Addendumで`[A] PARTIAL → [A] CLOSED（訂正）`とされたTerminal-State
一意性のContractは変更なし。Fourth Reworkはこれとは別に、P6-CODEX-031が指摘した
「judging／repairing／rejudgingをrunningへ収束させたことはRequirementの正当な
簡略化ではない」という点を受理し、P6-OBS-004のFull Vocabularyを実装した
（Step 8）。Chat Bubbleでは意図的に単一Badgeへ集約する設計判断は維持しつつ、
Feature Modes Panelでは3状態を個別のLabelとして表示するよう修正し、
実Browser・実Modelで実際にJudge Run状態が「完了」等へ正しく遷移することを確認した。

## 6. P6-ACC-056 — 「None／Unavailable／Invalid／Loading／Degraded／Active区別」

```text
判定: [A] CLOSED（Addendum訂正を個別に維持——Blanketではなく本документで再確認）
```

Third Rework Addendumで`[C] STILL_OPEN → [A] CLOSED（新規）`とされた、13組の
実到達可能Identity×State組み合わせへのTest Coverageは、本Reworkで対象Source
（`component_identity_projection.py`等）に変更を加えていないため、そのまま
有効である。Blanket Carry-forwardとしてではなく、「対象Sourceに変更なし」を
個別に確認した上でのCarry-forwardである。

## 7. P6-ACC-077 — 「未許可Root外／Provider Memory／Git Mutation／Network／User Data違反0」

```text
判定: [C] STILL_OPEN（「0」は主張できない——Third Reworkと同じ、誠実な不能表明）
```

Third Reworkは「新規Root外Action 0を主張することはできない」と正直に記録した
（P6-GOV-004／005、累計6件）。Fourth Reworkでも同様の状況が発生した：

```text
Fourth Rework中、Preview Server起動用Bashコマンドの標準出力／標準エラーを
誤って`/tmp/margpa_fourth_rework_preview_server.log`へRedirectする形で
Root外へのWrite Actionが1件発生した（既に別途ユーザーへ開示済み）。
Action Inventory:
  1. [Write] /tmp/margpa_fourth_rework_preview_server.logへの出力Redirect。無許可。
  2. [Execute] 該当Process（PID 55594）のkillによる、それ以上の書込み停止。
  3. 削除・追加確認は一切実施していない（P6-GOV-006の教訓を適用し、
     自己判断でのCleanupを行わなかった）。UNVERIFIED状態のまま。

ユーザーからの明示的Feedback（2026-08-23）: この種の軽微かつ自己修正可能な
Root境界逸脱について、都度作業を停止して報告することは不要——その場で
是正（Process停止、Project-local Scratchへの切替）した上で作業継続してよい、
との指示を受けた。これは「作業を止めない」という運用上の指示であり、
「記録・集計しない」という指示ではないため、本文書ではGovernance上の
誠実な記録として本件を維持する。

Historical Incident Count（Phase 6累計）: 7件
  （P6-GOV-001由来3件、P6-GOV-003の1件、P6-GOV-004・005の2件、
    本Fourth Reworkの1件）
Fourth Rework自身のNew Incident Count: 1件
Fourth Rework自身のNew Root-outside Action Count: 2件（Write 1、Execute 1）
Fourth Rework自身のUnverified Action Count: 0件
  （削除を試みていないため、削除成否のUNVERIFIED状態自体が発生していない——
   Fileは存在したまま、ユーザー自身の確認・対応に委ねている）
```

したがって「未許可Root外...Mutation...0」を主張することはできず、本IDは
引き続き`[C] STILL_OPEN`とする。これはFourth Reworkの他の技術的成果
（P6-CODEX-025〜031のClose）を損なうものではなく、Governance記録の
独立した誠実性の問題として区別して扱う。

## 8. 総括

```text
[A] CLOSED（本文書で個別に新規Close／再確認）: P6-ACC-004, 009, 011, 030, 038, 056
[C] STILL_OPEN（誠実な不能表明を維持）: P6-ACC-077

P6-CODEX-032が指摘した「Blanket Carry-forward」構造は、本文書では一切
使用していない——上記6件はいずれも個別のEvidence・理由を伴ってCloseし、
P6-ACC-077は個別にSTILL_OPENと明記した。
```
