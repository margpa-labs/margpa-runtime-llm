# Phase 9-1 Package 2 — User Mac Manual Recheck Checklist(実画面確認項目)

```yaml
document_id: phase_9_1_package_2_user_mac_manual_recheck_checklist_20260902204138
document_type: user_manual_checklist
language: ja
recorded_at: 2026-09-02 20:41:38 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
recorder_role: Claude（設計者兼実装者役）
source_mutation: none
git_action: none
```

## 0. 位置づけ

本Docは、Phase Index Next Authorized Sequence #8「User Mac Manual Recheck」のためのChecklistである。Userから「僕が確認するべき項目を全部ログに出して」との指示を受けて作成する。

各項目は、実際のFrontend Source(`frontend/src/components/ProviderSelectionPanel.tsx`／`FeatureModesPanel.tsx`／`RuntimeGovernancePanel.tsx`)を本Doc作成時に直接確認し、**実在するField・表示のみ**を列挙している(Package 2 Handoff §5「Manual／Observability Truthfulness」— UIに存在しない内部項目を「画面で確認」と指示しない、に従う)。Backend専用でUIに出ない項目は「(画面には出ない、Backend Evidenceのみ)」と明記する。

前提: Package 2本体・OF-P2-003・OF-P2-001の実装はClaude側でCompleteだが、**このChecklistの実施自体は未実施**。以下は全てUser自身が実際のBrowserで行う。

## 1. Provider Selection画面(Judge/Guard/Main、3 Role共通)

Provider Selection画面はMain／Guard／Judgeの3 Roleごとに区画があり、各区画に`Configured Provider`・`Active Provider`・`State`・(存在する場合)`Failure Reason`が表示される。

```text
[ ] 1-1. Fresh Runtime(Server起動直後)で、Judge区画のConfigured Providerが
        「judge.gemma-4-e2b-it-q4-0」(Gemma 4 E2B)になっていること。
[ ] 1-2. 同じくFresh Runtimeで、Judge区画のActive Providerが「none」、
        Stateが「configured」であること(未Load)。
[ ] 1-3. Judge Modeを OBSERVE または ENFORCE へ切り替えた直後、Judge区画の
        Active ProviderがGemmaになり、State が「loading」を経て「active」に
        遷移すること(実際にLoadされる)。
[ ] 1-4. Judge ModeをOFFへ戻した後、Judge区画のActive Providerが「none」、
        Stateが「configured」へ戻ること(Unloadへ収束)。
[ ] 1-5. Judge区画でProviderを明示的に「Selene」へ切り替え、同様にLoad/
        Unloadが正しく機能すること(Gemma既定化後もSeleneが従来どおり使えること)。
[ ] 1-6. Guard区画も同様に、Configured/Active/Stateが正確に表示されること。
```

## 2. Resource Gate(OF-P2-003／006／007)による拒否の実画面確認 — 新規、今回追加

Main稼働中に、実メモリ条件次第でJudge/Guardの起動がGateによって拒否されることがある(Backendでは既に実機Evidence確認済み、実画面での見え方は今回のUser Manual Recheckが初)。

```text
[ ] 2-1. Main Model稼働中に、Judge ModeをGemma選択のままON(OBSERVE/ENFORCE)にする。
        もしこのMacの実メモリ条件下でGateが拒否した場合、Judge区画のStateが
        「unavailable」になり、Failure Reasonに
        「resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role」
        という文字列がそのまま表示されること(不透明な失敗ではなく、原因が
        画面上に明記されること)。
[ ] 2-2. 同様にSeleneを明示選択した場合も同じ形式のFailure Reasonが表示されること
        (Selene(8B)の方が大きいため、より拒否されやすい想定)。
[ ] 2-3. Guard区画でQwen3Guardを有効化した場合も同様(特にMain Model側を
        DeepSeek 8Bへ切り替えている場合に拒否されやすい想定)。
[ ] 2-4. 拒否された場合、画面上でMain自体が壊れていない(引き続き通常どおり
        会話できる)ことを確認する — これが本Gateの本来の目的(破壊防止)。
```

## 3. Judge OBSERVE／ENFORCE と Semantic Criteria表示(Feature Modes画面)

Feature Modes画面のJudge Status欄に、Turn実行後、次のFieldが表示される: `Request ID`、`Recommendation`、`Confidence`、`Execution State`、`Configured/Active/Executed Provider`、`Budget`、`Frozen Modes(main/guard/judge/repair/recording)`、`Criteria: selected/evaluated/passed/deviated/unknown/not_applicable/deferred`、`Failure Reason`、`Repair Eligibility/Outcome/Accepted`。

```text
[ ] 3-1. Judge ModeをOBSERVEにして通常のTurnを送信し、Judge Statusが
        「judging」→「completed」等へ遷移すること。
[ ] 3-2. Criteria行に selected(選択件数)・evaluated(評価件数)が表示され、
        **evaluated が 0 でないこと**(旧症状「malformed_output／evaluated 0」
        からの脱却— Codexが挙げていた確認項目そのもの)。
[ ] 3-3. Failure Reason欄に「malformed_output」等の文字列が**出ないこと**
        (Token Planner修正の実画面上の帰結)。
[ ] 3-4. 同じ会話で新しいTurnを複数回(目安3回程度)連続送信し、そのたびに
        selected/evaluated が安定して出続けること(1回だけ偶然成功、では
        ないことの確認)。
[ ] 3-5. 複数Turn(4回程度)にわたり、Criteria: selected= の中身(裏側で
        どのCriterionが選ばれているか)が毎回同じでないことを、可能であれば
        Request ID等と突き合わせて確認する(OF-P2-001のTurn間Rotation — ただし
        個々のCriterion IDそのものは画面に出ないため、これは目安の確認であり、
        必須ではない。確実な確認はBackend Test側で完了済み)。
[ ] 3-6. Judge ModeをENFORCEに切り替えて同様に送信し、Execution Stateや
        Recommendationが実際の回答内容に対応した形で変化すること。
```

## 4. Judge→Repair→Rejudge、Frozen Provider Identity(8項目契約の項目5)

```text
[ ] 4-1. Repair ModeをENFORCEにし、意図的に事実と矛盾する回答が生成される
        状況を作るか、既存のRepair誘発シナリオを使い、Repair Eligibility／
        Repair Outcome／Repair Accepted／Repair New Turn が画面に表示される
        ことを確認する。
[ ] 4-2. その際、Frozen Modes行の judge= と、Configured/Active/Executed
        Providerが、Repair〜Rejudgeの一連の流れで同じProvider(Gemmaなら
        Gemmaのまま)を指し続けること(別のProviderへ無言ですり替わらない)。
```

## 5. Main Runtime Governance ENFORCE(ARGD／DAGD、Runtime Governance画面)

Runtime Governance画面の各Point行に、`Execution State`・`Selected Count`・`Severity`・`Executed Count`・`Observation Count`・括弧内に`Pass Count`・`Deviation Count`・`Deferred Count`、および該当時は`Unavailable Reason`／`Degraded Reason`が表示される。

```text
[ ] 5-1. Main ModeをENFORCEにし、実際のTurnを送信した後、該当Pointの
        Selected Count・Observation Count・Pass/Deviation/Deferred Countが
        0以外の意味のある値で表示されること。
[ ] 5-2. Judge非Active、あるいはJudge Modeが正しく組み合わさっていない状態で
        ENFORCEにした場合は、Unavailable Reasonに「false_enforce_prevented」
        等、安全側Fallbackであることが分かる文字列が出ること(実際に許可されて
        いないENFORCEが、許可されているかのように見えないこと)。
```

## 6. 参考: 画面には出ない、Backendでのみ保証されている項目(誤って画面確認を試みないこと)

```text
- Semantic 109の正確な合計(53 ARGD + 56 DAGD = 109)そのもの — 画面には
  1 Turn分のselected/evaluated/deferredしか出ない。109という総数の整合性は
  Backend Test(tests/integration/test_real_local_semantic_109_batched_judge_smoke.py
  等)で既に実機確認済み。
- Token Planner内部のBatch分割(32件を8件ずつ4 Model Callへ分割する等) —
  画面には最終結果しか出ない。tests/unit/evaluation/test_judge_batch_token_planner_regression.py
  で機械的に確認済み(§7参照、再実行可能)。
- Resource Gateの正確なByte数計算 — 画面にはFailure Reasonの文字列としてのみ
  現れる(§2参照)。数値自体はtests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py
  で実測済み。
```

## 7. 参考: Backend側で既に再現可能なFocused Command(Userが望めば自分でも再実行可能)

```bash
# Token Planner(Codexが言及していたもの、Package 2本体分、今回のOF-P2-003/001とは別件)
.venv/bin/python -m pytest tests/unit/evaluation/test_judge_batch_token_planner_regression.py -q -v

# OF-P2-003/006/007 Resource Gate実機Evidence(Main×Dedicated Role全6組み合わせ)
.venv/bin/python -m pytest tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py -m model_smoke -q -s

# OF-P2-001 Turn間Rotation(Fixtureおよび実Corpus)
.venv/bin/python -m pytest tests/unit/runtime_governance/test_semantic_runtime.py tests/integration/test_real_local_semantic_109_batched_judge_smoke.py -q

# Full Canonical(Regression確認)
.venv/bin/python -m pytest -q -m "not model_smoke"
```

## 8. Status

```text
Current Point            : User Mac Manual Recheckのための実画面確認Checklistを、
                            実Frontend Sourceを直接確認した上で作成した。
Files Created／Modified   : 本Fileのみ(新規作成)。
Validation                : N/A(Checklist自体はUser未実施)。
Open Current Blocker      : User自身によるBrowser上での実施待ち。
Controller-owned Next Work: なし。
Exact Next Route          : 本Checklistに基づきUserが実画面確認を行い、結果を
                            Claude／Codexへ共有する。
```
