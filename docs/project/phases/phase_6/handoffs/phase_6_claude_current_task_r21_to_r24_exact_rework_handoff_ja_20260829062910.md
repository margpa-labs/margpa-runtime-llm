# Phase 6 Claude Current Task R21〜R24 Exact Rework Handoff

```yaml
document_id: phase_6_claude_current_task_r21_to_r24_exact_rework_handoff_20260829062910
document_type: differential_exact_rework_handoff
document_state: ready_for_single_step_start
language: ja
created_at: 2026-08-29 06:29:10 JST
authority_owner: Codex_プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
target_task: current_existing_claude_task
preserved_baseline: current_working_tree_after_r0_to_r20
first_exact_work_unit: P6-RR-R21-WU-001
remaining_packages: P6-RR-R21_to_R24
maximum_claim: complete_candidate_with_real_provider_and_user_manual_gates
phase_6_closure: prohibited
phase_7: prohibited
git_action: prohibited
network: read_only_official_qwen_sources_only_authorized
```

## 1. Authority／Continuation

現在のClaudeタスクをそのまま継続する。Fresh Taskではない。Role Bootstrap、旧Context初期化、全Docs再読、Receipt専用段階は不要である。

R0〜R20の成立済み差分を保持し、Rollbackまたは一括再実装しない。Current Source／Testを正本として、P6-CODEX-081／084／086／087だけを差分修正する。

## 2. Required Reading

開始時に次の3文書だけを全文読む。

1. 本書。
2. `docs/project/phases/phase_6/history/operations/phase_6_gov023_claude_r17_to_r20_controller_independent_review_ja_20260829062910.md`
3. `docs/project/phases/phase_6/handoffs/phase_6_claude_current_task_r17_to_r20_exact_return_handoff_ja_20260829061552.md`

必要なSource／Testは各Package到達時に限定して読む。Workspace全走査、過去文書の全再読、Fresh Onboardingは行わない。

## 3. Exact Packages

### P6-RR-R21 — Production Dedicated Role Execution Lease

1. Judge／Guardの実Adapter解決とRole Turn Lease取得を、`RoleProviderLifecycleManager`の同一Condition Lock内でAtomicに行うAPIへ統合する。`active_adapter()`取得後に別Callで`begin_turn()`するTOCTOU設計は禁止する。
2. Dedicated Selene、Main-shared Judge、Qwen3Guard Model-backed Detector Callは、実行開始からTerminalまでLeaseを保持し、全成功／Failure／Timeout／Cancel／Exception Pathで`finally`相当からexactly-once Releaseする。
3. Built-in／noneはModel Leaseを作らず、暗黙Fallbackしない。
4. Provider切替、Mode OFF、Shutdownが実Call中に走った場合、Active Turn DrainまたはTyped Rejectionへ収束し、実行中AdapterをUnloadしない。
5. Judge Background／ENFORCE同期待ち、Guard Input／Output／Context Sourceの各Production経路を含める。
6. Threaded Regressionで、実CallをBlockした状態のProvider Change／OFF／Shutdown、Release後のUnload、Exception時のLease Leak 0を証明する。
7. P6-RR-ACC-016／017をProduction Wiring Evidenceで再導出し、P6-CODEX-086を閉じる。

### P6-RR-R22 — Tracked Stage Worker Registry／Shutdown

1. Prompt Build／Decode WorkerをLifecycle-owned Registryまたは同等のSingle Ownerへ登録する。Timeout時にCall Siteが`Future`を捨てる設計を廃止する。
2. Worker完了時にRegistryからexactly-once除去し、Exception、Timeout、Caller Cancel、Late Completeの全Pathを扱う。
3. Shutdownは新規Stage受付を止め、Active WorkerをBounded Joinする。Cancellation無視Workerが残る場合は`False`／Typed Failureを返し、Cleanを主張しない。
4. WebRuntime Close／Model Unloadより前にこのShutdown結果を確認し、False-clean時はUnloadを進めない。
5. Late Prompt／Decode ResultがJudge Result、Evidence、Presented Final、Last ResultへPublishされない既存性質を保持する。
6. Blocked Worker中Shutdown False、Release後Retry True、Worker Exception、複数Worker、Late Publish 0を実Thread Testで証明する。
7. P6-CODEX-081を閉じる。

### P6-RR-R23 — Qwen3Guard Official Contract Manifest／Strict Decoder

1. Qwen公式Model Card、公式`tokenizer_config.json` Chat Template、公式Qwen3Guard Repositoryを正本とし、Immutable Revision、Source URL、Source Digest、Target別Line Protocol、Category Set、Refusal FieldをProject-local Manifestへ固定する。
2. 本Packageに限り、Qwen公式Hugging Face RepositoryとQwenLM公式GitHub RepositoryへのRead-only取得を許可する。任意Domain、書込み、Login、Credential、Model Downloadは許可しない。Immutable Revision／Source Digestを取得し、推測値や`main` BranchをExact Revisionと偽らない。公式Source側の障害で取得不能な場合だけR23を`AUTHORITY_REQUIRED`へ分離し、R21／R22／R24は止めない。
3. Input／Context Sourceは`Safety`→`Categories`の2行、Output Candidateは`Safety`→`Categories`→`Refusal`の3行を必須とする。Safeも`Categories: None`を必須とする。
4. Target別公式Category Setを固定し、Inputだけの`Jailbreak`等をOutputで誤受理しない。未知LabelはSafeへ倒さない。
5. `verified_official_contract: bool`の外部注入だけでVerifiedにならず、Manifest Validation成功をActivation／Adapter Constructionの前提とする。
6. `model_id`／Exact Revision／Artifact SHA-512／Contract Manifest Digest／Schema IDをQwen3Guard ResultとEvidenceへ保持する。
7. Official Valid／Missing Categories／Wrong Order／Wrong Target Category／Malformed／Unknown／TimeoutのFixture Testを追加する。
8. P6-RR-ACC-022、P6-DELTA-004、P6-CODEX-087を、成立範囲とReal Model Gateを分けて再導出する。

### P6-RR-R24 — Acceptance Correction／Canonical Verification／Internal Review

1. 66 ID表の正本件数を再計算し、`PASS + PARTIAL + N/A + NOT RUN = 66`を機械的に検証する。
2. P6-RR-ACC-016／017はR21のProduction Evidence、P6-RR-ACC-022／P6-DELTA-004はR23のManifest／Identity Evidenceから再判定する。
3. `failure_at`のBackend Populated値をFailure Response後に再読できるFocused Testを追加し、P6-DELTA-014を再判定する。
4. Phase 9予約のP6-DELTA-016 Layout項目は勝手に実装せず、PARTIAL／DEFERREDを正確に保持する。
5. 新規Test数をClaimする場合はTest Node ID実数から算出する。概算やPackage内訳と不一致の合計を記載しない。
6. Focused、Canonical Mypy、Ruff Format Check、Ruff Check、Backend Full、Frontend Typecheck／Lint／Test／Buildを実行する。
7. Implementation Freeze後にRequirement-by-Requirement、Cross-component、Concurrency、Failure Injection、Negative Path、Claim AuditのInternal Reviewを実施する。Findingがあれば同じTaskでReworkし、もう一度Reviewする。
8. P6-CODEX-084を閉じる。

## 4. Recovery／Execution Control

- R21、R22、R23、R24の各Package Boundaryで簡潔なRecovery Indexを1件作る。Work Unitごとの文書乱造はしない。
- 通常のTest Failure、Finding、Read-only調査、既知の軽微なIncidentだけで停止しない。自己修正して継続し、最終Returnへ正直に記録する。
- True Stopは、破壊的／不可逆Mutation、Secret／個人情報露出、権限外NetworkまたはGit Mutation、続行不能な外部依存に限定する。
- Official Qwen Sourceへの限定Read-only取得は許可済みである。公式Source側の障害時だけR23をPARTIALへ分離し、R21／R22／R24を継続する。
- Progress報告後も自走する。Controllerへ確認を求めて停止しない。

## 5. Scope Boundary

禁止：

- Phase 6 Closure、Phase 7、Roadmap、Backup、Commit／Push。
- R0〜R20の一括再実装またはRollback。
- Phase 9へ予約済みのUI Layout／Streaming方式／Context上限再設計。
- User runtime_data、Provider Memory、未指定のProject外領域への接触。
- Git操作全般。

## 6. Return Contract

最大Claimは`Complete Candidate with Real Provider and User Manual Gates`である。

Returnには最低限、次を含める。

- P6-CODEX-081／084／086／087の個別Disposition。
- R21〜R24 Recovery Index。
- Production LeaseとTracked Worker Shutdownの実Thread Test名／結果。
- Qwen3Guard Manifest Identity、公式Source、Decoder Contract差分。
- 66 IDの正しい集計。
- Canonical Verification結果。
- Open Critical／Major／Minor／Real Model／User Gate。
- Exact Return Handoff。

完了後はCodex Controller Independent Review待ちで停止する。
