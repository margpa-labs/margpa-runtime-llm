# Phase 9-2 Explicit Default-OFF Experiment Runtime Gate — Claude差分継続 Exact Handoff

```yaml
document_id: phase_9_controller_to_claude_explicit_default_off_experiment_runtime_gate_partial_continuation_exact_handoff_20260911160659
document_state: frozen_bounded_rework_handoff
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-11 16:06:59 JST
language: ja
decision_authority: user
controller_provider: codex
controller_task_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
controller_role: project_controller_design_governor
executor_provider: claude_code
executor_identity_type: session_id
executor_session_id: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
executor_role: designer_implementer
git_write_authorized: false
network_authorized: false
real_model_authorized: false
browser_authorized: false
closure_authorized: false
phase_9_3_authorized: false
```

## 1. Maximum Authorized Claim

```text
P9_2_EXPLICIT_DEFAULT_OFF_EXPERIMENT_RUNTIME_GATE_COMPLETE_CANDIDATE_FOR_CODEX_CONTROLLER_REVIEW
```

これは実装Taskが到達してよい最大Claimである。Phase 9-2 Complete、Phase 9 Closure、Phase 9-3 READY／開始またはRelease Readyを自己承認してはならない。

## 2. 起点と現在地

Codexの現行`設計者兼実装者役`Taskは、ユーザー割り込みに従ってCurrent Working TreeをPartial Returnとして固定した。実装方針と主要なGate配線は成立候補であり、Rollbackや再設計を必要とするConfirmed BlockerはControllerのRead-only Source Reviewでは確認していない。

一方、次が未完了であるためPartialのまま受理しない。

1. 最後に追加した`web/app.py`のdirect runtime factory向けnon-local lifespan fail-closed Guardと対応Testが未実行。
2. 最終Source状態に対するRelevant Regressionが未実行。
3. Required Sabotage-regressionが未実行。
4. Changed PathのRuff／Mypyが未実行。
5. Review AがPartial、Review Bが未完了。
6. Final Exact Return／Recoveryが未作成。

ClaudeはCurrent Working Treeをそのまま引き継ぎ、成立済み実装を作り直さず、上記残差だけを差分継続する。

## 3. Mandatory Reading

次を順番どおり読む。

1. `docs/project/phases/phase_9/history/operations/phase_9_2_minimal_closure_and_phase_9_3_ready_premature_claim_correction_addendum_ja_20260910121521.md`
2. `docs/project/phases/phase_9/handoffs/phase_9_codex_phase_9_2_explicit_default_off_experiment_runtime_gate_partial_exact_return_ja_20260911160254.md`
3. `docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_partial_recovery_ja_20260911160254.md`
4. Current Working TreeのChanged Source／Test 8 Path。
5. `docs/project/shared/task_roles/development_agent_hybrid_structured_instruction_handoff_operating_rule_ja.md`のTask Identity／Claude Session Adapter追記。

Partial Return SHA-512:

```text
9eb5fa3259bb6e1b71538e45917256c8145e030b8f52083f7e5c86b00391899031ff78fec824f16886369f2e52834f122c4ccd8a65ee8712028a78852bd0bf7c
```

Partial Recovery SHA-512:

```text
0feec7dfb9002efdc14351a43b2b6992a95616e0af4a7727c9a9611bd33ea937e2b14f51cd130fb1bb1b199e1a1d72d6c48c9f499b8d64816f02f5fc44eede6f
```

Premature Claim Correction SHA-512:

```text
7394b82824e867d8c38d165a333227541892b5c7f450b8744d05c75d655463dea0c89331668e9f6507e49789d4521d0ea27ab3d3c7c1d1a45d31399a1ee3d1b0
```

Digest不一致時は推測で続行せず、True Stopとして報告する。

## 4. 受理候補となる現行設計

次はCurrent Working Treeで確認された設計であり、成立済みTest Evidenceを理由なく破棄しない。

- CLI Opt-inは`--phase-9-experiment-runtime`。
- Composition引数は`experiment_runtime_enabled: bool = False`。
- Conversation PersistenceはStorage Prerequisiteであり、Experiment Authorityではない。
- Default OFF時はExperiment Service、Run Worker、Production Turn Adapter、Live Configuration ReaderおよびConfiguration Leaseを構築しない。
- Explicit ON時はLocal／Loopback、Authentication DisabledおよびConversation Persistenceを要求する。
- Disabled状態のPlan／Run MutationはHTTP 503、Code `experiment_disabled`。
- Settings MutationはDefault OFF時にExperiment Leaseを理由として409拒否されない。
- 通常UIのExperiment入口は非表示のまま。

現行Startup Commandには新Flagを追加しない限りDefault OFFとなる。この既定値を変更しない。

## 5. Claude Work Units

### CL-GATE-01 — Recovery／最終差分確認

- Partial Return／RecoveryのDigestを確認する。
- Current Working Treeの8 PathとPartial文書のChanged Pathsが一致するか確認する。
- 他の未コミット変更をUser／前工程の所有物として保持し、Clean、Rollback、Format対象にしない。
- `.task_tmp/`を含む既存Artifactを破壊的に削除しない。

### CL-GATE-02 — 未検証GuardのFocused Validation

`web/app.py`のlifespan Guardと対応Testを最初に実行する。最低限、次をHard Assertする。

- Experiment構成物が一つでもBoundされ、Access Policyがnon-local／authenticated／non-loopback許可なら、Request受付前にfail closedする。
- Fail-closed時にRuntime Closeが呼ばれる。
- Local／Auth Disabled／Loopback-onlyのExplicit Enabled構成を誤拒否しない。
- Default OFFの全Experiment構成物`None`は通常App起動を妨げない。

Guard自体にConfirmed Blocker／Majorがあれば局所修正する。Minorな表現・整理だけを理由にScopeを広げない。

### CL-GATE-03 — Disabled Surfaceの網羅確認

Routerを削除せずDisabled Contractを使う現行設計について、公開Endpointを分類し、Default OFF時に見えない実行が開始できないことを確認する。

- Preset DiscoveryをHTTP 200／`enabled=false`で残す設計は許容する。
- Plan、Run、Cancel、Comparison、Resultその他、Service／Workerを必要とする操作が、未構築Objectを迂回して実Workを開始しないことを確認する。
- Actor Call、Worker Task、Mutation、Evidence生成、Lease保持は0。
- Settings変更が`experiment_configuration_lease_held`にならない。

既存Testがこの境界を十分覆う場合は重複Testを増やさず、Coverage対応をReturnに記録する。不足する実行可能Endpointがある場合だけ最小Testを追加する。

### CL-GATE-04 — Enabled Regression／Shutdown

明示Enable時に既存Headless Coreが維持されることを、最小のTop-level Non-model経路で確認する。

```text
Plan -> Run -> Evidence -> Comparison -> Restart Read
```

Default OFF／Explicit ON双方で、構築されたWorkerだけをShutdownし、残留Background WorkやLeaseを残さないことを確認する。

Real Model、Browser、NetworkおよびUser `runtime_data`は使わない。

### CL-GATE-05 — Sabotage／Static Validation

- Gate Default、Object Construction条件またはDisabled Run境界のいずれか一つを一時的に壊し、新規／強化Testが確実にFailureを検出することを確認する。
- Sabotage前後で対象File Digestを保存し、完全復元後に元とByte一致することを確認する。
- 復元後に同じFocused TestをPASSさせる。
- Changed Source／TestへRuffを実行する。
- Repositoryの既存Mypy運用と整合するCommandを実行し、新規Error 0を確認する。既存Baselineを新規Failureとして修正Scopeへ入れない。
- Backend-only ReworkでFrontend Source／配信Bundleを変更しない場合、Frontend Build再実行を必須にしない。その判断理由をReturnに明記する。

### CL-GATE-06 — 二観点Review／Return

Review A:

```text
Default OFF、Authority、Bootstrap、API、Lease、Direct Factory、Access Policy、Shutdown
```

Review B:

```text
Explicit ON Regression、通常Chat／Settings等への非波及、Test Oracleの偽PASS、Disabled Surface、Configuration／CLI整合
```

Confirmed Blocker／Majorを発見した場合はScope内で修正し、影響範囲を再検証する。Minor／Non-blockerは無理に修正せずOpen Findingへ分離する。

新規Final Exact ReturnとFinal RecoveryをAppend-only Pathで作成し、Controller Independent Review待ちで停止する。

## 6. Acceptance Criteria

```text
AC-01  Gate省略時はExperiment Runtime全構成物がNone／非稼働
AC-02  Conversation Persistence単独ではExperiment Authorityが発生しない
AC-03  Default OFFでExperiment APIからWorkを開始できない
AC-04  Default OFFのActor／Worker／Mutation／Evidence／Leaseが0
AC-05  Default OFFでExperiment起因のSettings 409が発生しない
AC-06  Explicit ONはLocal／Loopback／Auth Disabled／Persistenceを要求
AC-07  Direct Factoryのnon-local Bound RuntimeはRequest前Fail-closed
AC-08  Explicit ONのHeadless Top-level経路が退行しない
AC-09  OFF／ON双方のShutdownが安全
AC-10  Sabotageが欠陥を検出し、復元後Byte一致＋PASS
AC-11  Ruff Clean、新規Mypy Error 0
AC-12  通常Chat／Judge／Guard／Repair／Recording／Data Controls等へ非波及
AC-13  UI入口は非表示のまま
AC-14  Review A／B完了、Confirmed Blocker／Major残件0
AC-15  Final Exact Return／Recoveryが新規Append-onlyで存在
```

## 7. Explicit Prohibitions

- Git add／commit／push／stash／resetその他のGit Write。
- Current Working TreeのClean／Rollback。
- Real Model Load、Browser Manual Test、Network、Project Root外Action、User `runtime_data`接触。
- Experiment UI再表示、ExperimentPanel修復またはPhase 11機能実装。
- Phase 9-3／Phase 10 Source作業。
- Headless Core削除、Gate Default ON、Conversation PersistenceからのAuthority再生成。
- Full Suiteの無目的な反復、成立済みReal Model Gateの再実行。
- Phase 9-2 Complete／Closure／Phase 9-3 READYの自己承認。

## 8. Resource／Stop Contract

Quotaまたは実行基盤で中断する場合、Current State、実行済みCommand／結果、未完了Acceptance、部分Mutation、Exact Next Actionを新規Recoveryへ保存し、Partialとして一度だけReturnする。未実施をPASSにせず、完成を演出しない。

途中報告は不要である。Userから割り込みが届いた場合は応答してよい。Final CandidateまたはTrue Stop時に一度だけ返す。

## 9. Return Identity Contract

Final Returnは本文先頭に次を含める。

```text
【Task Communication Identity】
From:
  Provider: Claude Code
  Identity Type: Session ID
  Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role: 設計者兼実装者役
To:
  Provider: Codex
  Identity Type: Task ID
  Task ID: 019f739b-8a21-7592-95cc-c83c9c08e5f6
  Role: プロジェクト責任者兼設計統括者役
Message Type: return
```

続けて次を返す。

- Maximum Claim。
- Work Unit別Disposition。
- Changed Paths。
- Test／Ruff／Mypy／Sabotage結果。
- Review A／B結果。
- Final Exact Return／Recovery Path。
- Open Finding。
- Git／Network／Model／Browser／Root外Actionの実施有無。

本Handoffは上記Bounded Reworkの実行Authorityだけを伝達する。Phase 9-2 Closure、Phase 9-3開始またはGit Authorityを生成しない。
