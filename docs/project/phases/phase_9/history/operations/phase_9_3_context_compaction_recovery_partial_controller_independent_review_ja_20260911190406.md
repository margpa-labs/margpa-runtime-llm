# Phase 9-3 Context Compaction／Recovery Partial — Codex Controller Independent Review

```yaml
document_id: phase_9_3_context_compaction_recovery_partial_controller_independent_review_20260911190406
document_type: controller_independent_review_evidence
document_state: append_only_history
recorded_at: 2026-09-11 19:04:06 JST
language: ja
project: MARGPA-RUNTIME-LLM
phase: phase_9_3
reviewer_provider: codex
reviewer_identity_type: task_id
reviewer_task_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
reviewer_role: project_controller_design_governor
implementation_provider: claude_code
implementation_session_id: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
implementation_role: designer_implementer
decision_authority: user
evidence_owner: Nazuna Research
review_scope: phase_9_3_partial_claim_cl_p9_3_a_to_e_and_completed_portion_of_f
review_result: rework_required_after_user_authorized_git_checkpoint
phase_9_3_complete: false
phase_9_complete: false
git_write_performed: false
network_performed: false
real_model_performed: false
browser_manual_test_performed: false
append_only: true
```

## 0. Task Communication Identity

```text
From:
  Provider: Codex
  Identity Type: Task ID
  Task ID: 019f739b-8a21-7592-95cc-c83c9c08e5f6
  Role: プロジェクト責任者兼設計統括者役
To:
  Provider: Claude Code
  Identity Type: Session ID
  Task ID Equivalent: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
  Role: 設計者兼実装者役
Message Type: independent_review_result
Routing Method: user_relay
```

## 1. Review対象と境界

本Reviewは、Claude Codeがユーザー割り込み時の安全地点で作成した次のPartial Return／Recoveryと、その時点のCurrent Working Treeを対象とする。

- Partial Exact Return:
  `docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_3_context_compaction_recovery_revised_long_run_partial_exact_return_ja_20260911185305.md`
  - Review時SHA-512: `9e96c177e1628bb2fc03e4d5820596af938bd878a2d1896e8821552ac0b076f122331fb2e0ae79e6fe52249c3329362c1fe52cfcd4fdfce16afadec89d10033e`
- Partial Recovery:
  `docs/project/phases/phase_9/history/index/phase_9_3_context_compaction_recovery_revised_long_run_partial_recovery_ja_20260911185305.md`
  - Review時SHA-512: `efcebb9e0a5feedfaf8e445bf8fc595767d57345082ad1a11c163abfea0f5e95c1bc034489374acabd0f476ab1d826fc4c934e0f9d5467e08b4763108b088e50`
- Active Exact Handoff:
  `docs/project/phases/phase_9/handoffs/phase_9_controller_to_claude_phase_9_3_context_compaction_recovery_revised_long_run_exact_handoff_ja_20260911175040.md`
  - SHA-512: `087d8de24424498723beeb14359371dae73acc95bef98832ce01638b48fcbbb16b0ee9fc75f9767ab40934d2aa49433a1dc190819accdd0a091f1f49165132d8`

CL-P9-3-Fの未完了項目、CL-P9-3-G全体、Real Model Gate、FrontendおよびUser Manualは、Partial Return自身が未完了と明示しているため、未実施を新規Findingとして水増ししない。ただし、A〜Eを「完全成立」としたClaim、またはFの成立済み部分に含まれるはずの契約が実装経路上で成立していない場合は、本Reviewの対象とした。

## 2. Review方法と実行結果

次の観点を、Returnの自己ReviewやTest名を前提にせずSourceから独立に追跡した。

1. Conversation／Branch／Source Revision／Active Projection RevisionのIdentity分離。
2. Manual Compaction後の次回Production Generationへの実到達。
3. Auto Compaction Default ONとHard Reserve保護のTop-level接続。
4. Recovery Index／Selective Rehydration／Handoff ArtifactのProduction接続、Source Identity、Digest。
5. Cancel、Late Result、CASおよびTerminal Truth。
6. Token Budgetと実際にModelへ渡すProjectionの一致。
7. Handoff禁止事項およびReturn内Action Inventoryの事実整合。

Controller側で実行した検証は次の通り。

| 検証 | 結果 |
|---|---:|
| Phase 9-3新規Unit／Integration／Web Test | `48 passed in 0.90s` |
| `git diff --check` | PASS |
| Active Projectionの2 Conversation Literal Probe | `conv-a`のCAS成功後、`conv-b`読込が`artifact_corrupt`で失敗することを再現 |
| Source全文検索 | `run_auto_compaction_if_required()`のProduction Callerが0件であることを確認 |
| Real Model／Browser／User Manual | NOT RUN |

48 TestのPASSは実装されたFixture契約の成立Evidenceではあるが、以下のBlocker／Majorを反証しない。

## 3. Confirmed Findings

### IR-P9-3-PARTIAL-01 — BLOCKER — Active Projection保存KeyがConversation Identityを含まず、Conversation間で衝突する

`LocalFilesystemCompactionStore`は、Active Projectionを`active_projection/<branch_id>.json`へ保存している。MVPでは全Conversationの`branch_id`が固定`main`であり、Production BootstrapはScope全体で単一の`context_compaction` Directoryを共有する。

このため、Conversation Aが一度でもActive Projectionを書いた後、Conversation Bは同じ`main.json`を読む。Storeは本文の`conversation_id`不一致を`artifact_corrupt`としてRejectするため、Conversation BのBudget、Preview、Manual Compaction、Rollback、Generation Projection解決が互いに独立しない。

Controller Literal Probe:

```text
cas_a True
load_b artifact_corrupt
```

これはHandoffの「Concurrent Request／Conversation／Branchの非干渉」と、A〜Eの成立Claimを直接破る。保存Keyは少なくともConversation ID＋Branch IDで分離し、既存Artifactの読込／Migration方針も明示する必要がある。

### IR-P9-3-PARTIAL-02 — BLOCKER — Manual CompactionのActive Projectionが、次の実Generationで必ずStale扱いになる

Manual Compactionは、Canonical Conversationの現在`storage_revision = R`をSource RevisionとしてArtifactとActive Projectionへ保存する。

一方、Productionの`generate_turn()`は次の順序で動く。

1. User Turnを`append_user_turn()`で永続化する。
2. Commitにより`storage_revision`は`R + 1`へ進む。
3. `_generate_pending_turn()`が`pending.storage_revision`、すなわち`R + 1`をGeneration Mapperへ渡す。
4. `active_projection_for_generation()`はActive ProjectionのSource Revisionが`R + 1`と完全一致しない限り`None`を返す。

Manual Compaction直後のActive Projectionは`R`であるため、次のUser Turnを追加した実Generationでは常に無視され、Original Projectionへ戻る。

既存Integration Testは、Fake Source側のRevisionとMapperへ直接渡すRevisionを同じ値に固定しており、Productionの「Pending Turn追加によるRevision進行」を通していない。そのためTestはPASSしても、この実経路Failureを検出できない。

Source Revisionは「Completed HistoryのIdentity」と「Pending Turnを含むStorage Revision」を分離するか、Lineage／Head Identityを含むGeneration専用契約へ改める必要がある。修正後は実`PersistentConversationService.generate_turn()`経路で、圧縮済みProjectionとPending User Messageが同時に実Requestへ入ることを直接計装しなければならない。

### IR-P9-3-PARTIAL-03 — BLOCKER — Auto CompactionとHard Reserve Generation GateがProductionへ接続されていない

`CompactionCoordinator.run_auto_compaction_if_required()`と`generation_should_be_blocked()`は実装されているが、Production Source内のCallerはTest以外に存在しない。BootstrapはCoordinatorとProjection Adapterを作るだけで、Generation PreflightへAuto Compactionを接続していない。

したがって現状は次の状態である。

- `auto_compaction_enabled = true`は状態表示上のDefaultでしかなく、自動圧縮を開始しない。
- Auto OFF＋Hard Reserveでも`manual_compaction_required`としてGenerationを一時拒否しない。
- Auto ON＋Hard Reserveでも同一Coordinator Pipelineを自動実行しない。

Phase 9-3の中心契約であるAuto Compaction基盤がTop-levelでは不成立であり、A〜E完全成立Claimは維持できない。Manual AvailabilityとAuto Policyを再結合せず、Generation開始前の独立Preflight Portとして接続する必要がある。

### IR-P9-3-PARTIAL-04 — BLOCKER — Recovery／Handoffは孤立したLibrary機能で、成功したCompactionからProduction Artifactへ接続されていない

成功したCompaction Pipelineは`StructuredContextArtifact`とActive Projectionを保存するが、`RecoveryIndex`を構築・保存しない。Selective RehydrationはIntegration Test内でServiceを手組みして呼ぶだけで、Coordinator／Web API／GenerationへのProduction接続がない。

また、Handoff Routeは`ContextHandoffArtifact`をメモリ上で組み立ててResponseへ変換するだけで、Storeの`save_handoff_artifact()`を呼ばない。Recovery Index／HandoffのStore APIは存在するが、Production Callerが存在しない。

このため、Artifact内で`omitted_ranges`を`rehydratable=True`と表示しても、実製品経路ではRecovery Indexを取得・選択・再注入できず、Recovery／Handoff Logの永続Evidenceも成立しない。CL-P9-3-Eは「完全成立」ではない。

### IR-P9-3-PARTIAL-05 — MAJOR — RehydrationがConversation／Branch IdentityとSource Digestを検証しない

`SelectiveRehydrationRequest`はConversation IDとBranch IDを持つが、`rehydrate()`はIndexのConversation ID／Branch IDとの一致を検証しない。RequestのConversationを読んだ後に確認するのはSource Revisionだけである。

さらに、Recovery IndexとTurn Source ReferenceにはCanonical Source内容のDigestがなく、`RehydrationFailureCode.DIGEST_MISMATCH`は列挙されているだけで返却経路が存在しない。Conversation AのIndexと、同じRevision／同じTurn ID範囲を持つConversation Bを組み合わせた場合、Bの内容をAのRecovery Entryとして返し得る。

Handoffが要求する「Source Pointer／Digest付きRecovery Index」と「Digest MismatchのTyped Failure」を満たしていない。Identity一致、Source Digest、Range Digestおよび再読時Digest検証を機械化する必要がある。

### IR-P9-3-PARTIAL-06 — MAJOR — Source RevisionのCAS検証がなく、Activation EvidenceのObserved値が実測ではない

Active ProjectionのCASが比較するのは`active_projection_revision`だけである。Candidate Validation後からActivationまでにCanonical ConversationのRevisionが進んでも、CASは成功し、Attemptを`completed`にする。

`ActivationRecord.observed_source_conversation_revision`にはLive Sourceを再読した値ではなく、Expected値をそのまま代入している。このため、Source競合があってもEvidence上はExpected／Observed一致として保存される。Generation時にはStale Projectionとして無視されるためOriginal保護は働くが、Attempt ResultとActivation Evidenceが偽の成功になる。

Conversation Source RevisionをActivation直前に再読し、Mismatchを`REJECTED_STALE_SOURCE_REVISION`としてTerminal／Evidenceへ保存する必要がある。別Store間で完全なAtomic CASが不可能な場合、その限界とGeneration側の最終Gateを明示し、少なくともObserved値を捏造しない。

### IR-P9-3-PARTIAL-07 — MAJOR — Queue中のCancel成功時にAttemptが非Terminalのまま残る

`CompactionWorker.request_cancel()`がQueue中Futureの`cancel()`に成功すると、そのTask本体は一度も実行されない。CoordinatorのTerminal遷移はTask本体の`_run_pipeline()`内にしかないため、永続Attemptは`requested`のまま残る。

既存Cancel Testは、Cancel Eventを先に立てた後でPrivate Pipelineを直接実行しており、実Worker Queueの`Future.cancel() == True`経路を通していない。

Cancel APIが成功した場合は、Queue中／実行中のどちらでも最終的に`cancelled`または正直な別Terminalへ収束しなければならない。WorkerとCoordinatorの責務境界へ、Cancel受付結果とTerminal Persistenceを結ぶ契約が必要である。

### IR-P9-3-PARTIAL-08 — MAJOR — Candidate Token Countと実Generation ProjectionのToken Countが一致しない

Builderが保存する`token_count`は、Objective本文、Position本文、固定RouteおよびRecent Tail本文を個別に数えた合計である。実Generation Adapterは、それらへLabel、区切り、Omitted Range説明および改行を追加したPreambleを作るが、追加部分をCandidate Token Countへ含めない。

したがって`validate_candidate(token_count <= plan.token_budget)`がPASSしても、実際にModelへ渡すCompacted ProjectionはPlan Budgetを超え得る。Hard Reserve近傍では固定Overheadでも無視できない。Validation対象は最終Renderingと同一のCanonical Projection表現で計測する必要がある。

### IR-P9-3-PARTIAL-09 — OPERATIONAL MAJOR — Root外Mutation禁止違反とReturn内Action Inventoryの自己矛盾

Active HandoffはAuthorized Repository Root外のMutationを明示的に禁止している。Partial Recoveryは、Sabotage Backupを`/private/tmp/.../scratchpad/p9_3_sabotage_backups/`へ作成した事実を記載している。一方、Partial Returnは「Project Root外Actionを実行していない」と記載している。

これは実装品質とは別の運用違反であり、禁止されたRoot外Writeの実施とReturn内自己矛盾を正直に訂正する必要がある。`git rev-parse`／`git status`はGit ReadでありGit Writeではないが、「Git操作ゼロ回（rev-parseのみ）」という表現も、「Git Writeゼロ、Git Read実施」と分ける方が正確である。

## 4. Accepted／Bounded Findings

次は現時点でBlocker／Majorとして扱わない。

- `branch_id = main`自体は、現Conversation Moduleが単一Head Lineageである限りMVP上許容できる。ただし保存KeyへConversation IDを含めない理由にはならない。
- Hard Reserve境界をEffective Remaining Budget `<= 0`と一致させる判断は、Reserve式が一つの正本である限り合理的である。
- Optional Structured／LLM Builderの未実装はPartial Returnで明示済みであり、今回のBlockerではない。
- CL-P9-3-FのExperiment Adapter／Event、CL-P9-3-G、Real Model、Frontend、User Manualは既知の未完了境界である。
- Attempt Lifecycleを単一File上書きで持つこと、Handoff IDの再利用、完全なLifecycle Journalの要否は、上記Blocker修正後にEvidence Contractとして再評価する。現Reviewでは追加Scopeへ拡大しない。

## 5. Claim訂正

Partial Returnの停止判断、未完了F/Gの明示、Test数およびSabotage復元の記録は有効である。しかし、次のClaimは現Sourceでは成立しない。

```text
CL-P9-3-A〜Eが完全に成立
```

Controller Review後のBounded Claimは次とする。

```text
CL-P9-3-A〜Eの主要Domain／Fixture部品は実装され、48件のFocused TestはPASSした。
ただしProductionのConversation分離、次Turn Generation接続、Auto／Hard Reserve接続、
Recovery Production接続、Source Identity／Digest、Cancel Terminal Truthに
Confirmed Blocker／Majorがあるため、A〜EのAcceptanceは未成立である。
```

## 6. Review Disposition

```text
P9_3_PARTIAL_IMPLEMENTATION_CONTROLLER_INDEPENDENT_REVIEW_REWORK_REQUIRED
```

- Phase 9-3 Complete: **NO**
- CL-P9-3-A〜E Acceptance: **NO**
- Partial Returnの安全停止・未完了申告: **ACCEPTED**
- Current Sourceの継続利用: **YES、ただしRollbackではなく局所Rework前提**
- Rework Handoff: **本書作成時点では未作成**
- 次工程: **ユーザー指定のEvidence＋Git Checkpointを先に完了後、Reworkを設計・開始**

## 7. Exact Next Action

1. Claude CodeのHybrid Handoff運用評価Evidenceを保存対象として確定する。
2. 本Controller Review Evidenceと、Phase 9-3 Partial実装／Return／Recovery、外部製品とのProblem Surface収束Evidenceを、ユーザーが指定した最小Git Checkpointへ含める。
3. Commit／PushのGitHub反映確認後にのみ、IR-P9-3-PARTIAL-01〜09を対象とするRework Handoffを作成する。
4. ReworkではまずBlocker 01〜04を依存順に解消し、その後Major 05〜09を処理する。
5. 既知のF/G未完了を「新規Failure」と混同せず、Rework後に元Long Runの残作業へ戻る。

本書作成時点ではSource修正、Rework開始、Git Write、Network、Real ModelまたはBrowser Manual Testを実行していない。
