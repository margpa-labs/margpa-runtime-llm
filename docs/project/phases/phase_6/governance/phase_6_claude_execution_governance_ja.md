# Phase 6 Claude長期実行Governance

    document_id: phase_6_claude_execution_governance
    status: accepted_frozen_not_activated
    phase: phase_6
    from: プロジェクト責任者兼設計統括者役
    to: Claude側設計統括者役
    recorded_at: 2026-08-22 21:13:08 JST
    automation_control_state: OFF
    implementation_authorized: false

## 1. Authority Model

Claude側設計統括者役は、Activation後にFrozen Scope内の設計具体化、実装、Test、Self-review、局所ReworkおよびRecoveryを自律実行する。最高責任者へRoutine判断を返さない。

ただし、Project Root外、Git／GitHub、Network、External Service、Secret、課金、User実Data、最上位規則、Stable正本および未許可Model Mutationを自己許可しない。唯一のRoot外例外候補は、Phase 6 Activation ReceiptでHumanがExact Physical Path、Subtree、Purposeおよび期間を明示したModel Symlink Targetであり、そのReceipt成立前または範囲外へ拡張しない。

## 2. Execution Range

Activation時に許可可能な範囲：

- Phase 6-0〜6-IのSource／Frontend／Test／Config／新規History／Handoff。
- Accepted Scope内の新規Module／Adapter／Schema／Fixture。
- Qwen Current Artifactを変更しないDeepSeek Derived Artifact領域。
- Project-local Test Temporary Root。
- Frozen Scope内の局所Bug修正と必要最小の既存Source変更。
- Project Root内Repositoryに対する`git status`、`git diff`、`git ls-files`、`git check-ignore`および`git rev-parse`相当のRead-only Inspection。Index／Ref／Worktreeを変更するGit Commandは含まない。

常に不許可：

- Phase 6-J Closure、Phase 7開始、Git Add／Commit／Push。
- Project Root外Read／Write／Execute。ただしCurrent Phase 6 Activation Receiptで明示されたModel Symlink TargetのExact Subtree／Operationだけを例外とする。
- Provider MemoryまたはClaude／Codex横断Memoryへの保存。
- User実runtime_dataのTest利用、削除、修復、Migrationまたは内容確認。
- Existing Stable Docs／Existing Historyの無断変更。
- Qwen Artifact、Official DeepSeek Canonical Snapshot、DeepSeek V4の変更／削除。
- Network Download、AWS、Lightning、一般公開、Secret／Credential操作。
- Dedicated Guard／Judge Model Download。

## 3. Dynamic Responsibility

固定Packageを機械的に量産しない。各Work Unit開始時にFrozen Contract、As-built、Current Diffおよび前Work Unit Resultから必要なSource／Test／Docsを動的に解決する。

Local Bug、Expected Test Failure、UI同期、Contract具体化、Naming衝突およびTest Fixture問題は権限範囲内で自己解消する。次の場合だけ停止する。

1. Root／Authority／Stable／Git／External／User Data Scope拡張が必要。
2. Frozen Requirementまたはユーザー決定を変更しなければ成立しない。
3. Model Conversion／Loadが未承認のDisk／Thermal／Memory Riskを要求する。
4. Irreversible Migration、Canonical Artifact破壊または重大Risk受容が必要。
5. 最上位規則とCurrent Instructionが衝突する。

UnresolvedであることだけをBlockerにしない。Controller-owned Next Workは自ら処理し、Deferred EvidenceはTrigger到来まで再活性化しない。

## 4. Stable／History

- Requirements／Architecture／ADR／Governance／Execution Plan／Acceptance Matrix／Execution Handoff／Phase IndexはActivation後のFrozen Inputとして扱う。
- Frozen内容に重大衝突を発見した場合は既存文書へ直書きせず、新規Correction／Deviation／HandoffをAppend-onlyで作成する。
- Subphase完了またはMaterial BoundaryごとにRecovery Entryを作る。
- Work Unitごとの機械的なDocument量産は禁止する。Recovery Fidelityに必要なまとまりで作る。
- From／To、Current State、Exact Mutation、Validation、Open Major FindingおよびNext Actionを各Handoffへ明記する。

## 5. Long-running／Compaction／Quota

- Auto-Compaction後はPhase Index、Claude Handoff、Long-running Companion、Hash Trackerおよび最新Recovery Entryから自己復旧する。
- 記憶、言語変化、直前会話またはProvider SummaryだけでRecovery完了を主張しない。
- 5時間制限等のProvider Quotaで停止した場合、自動再開後にCurrent Work Unit、Diff、Test、Hash／Recovery Entryを照合して継続する。
- Subphase報告、途中経過またはMaterial Boundary記録を理由に自走停止しない。
- Compaction／Quota後のRecovery成功、言語逸脱、誤停止、False CompletionおよびHuman InterventionをEvidence化する。
- Completion Handoffおよびユーザー向け主要報告は日本語とする。

## 6. Model Artifact Governance

- DeepSeek Q4作成はPhase 6 Activationで明示的に含まれた場合だけ行う。
- modelsがSymbolic Linkの場合、Activation Receiptに記録されたResolved Target、Qwen Read／Load専用Subtree、DeepSeek Canonical Read専用SubtreeおよびDeepSeek Derived Write専用Subtreeだけを例外Scopeとする。Logical Path名だけでRoot外Authorityを自己生成しない。
- 過去のDownload時に与えられた例外許可を再利用しない。
- Official SnapshotをRead-only Canonical Sourceとして扱う。
- Derived Artifactは専用gguf／manifest領域だけへ新規作成する。
- Conversion Intermediateが必要な場合はReceiptで許可されたDeepSeek専用Work Subtreeへ限定し、成功後も無断削除しない。
- Tool Revision、Recipe、Source Digest、Output Digest、Size、LicenseおよびRollbackを記録する。
- Disk Gateを毎Material Stepで確認し、設定された保全下限を下回る見込みなら開始／継続しない。
- V4 FlashをLocal Conversion／Load対象へ混入しない。
- Symlink Target内でもSibling Model、親Directory、Cache、Trashまたは未指定Subtreeへ拡張しない。
- ConversionやLoad失敗をSupportedへ捏造しない。Safe Unsupportedは正当な結果である。

## 7. Testing／Temporary Data

- Unit／Integration／Frontend TestはProject-local専用Temporary RootまたはFramework Fixtureを使う。
- Project Root外Temporary、dev/null、Home、Provider Cache、User実runtime_dataを使用しない。
- 大規模Full SuiteはSubphase／Material Boundaryで実行し、小修正ごとに繰り返さない。
- Model実Load TestとFake／Stub TestをEvidence Classで分離する。
- Test Environment、Manual Browser、Source Inspection、Reported Evidenceを混同しない。
- Testが生成したTemporary Artifactは、許可された専用Rootと既定Lifecycleの範囲でだけ処理する。無許可Cleanupを行わない。

## 8. Required Self-review

各Subphaseで最低限次を確認する。

1. Frozen Requirement／Acceptance IDとの対応。
2. OFF Call／Mutation 0。
3. OBSERVE non-intervention。
4. ENFORCE Authority／Budget／Registered Action。
5. Request／Turn／Attempt相関。
6. Secret／Path／Raw Content非露出。
7. v1／v2／Persistence／RAG／Citation／Stop／Branch回帰。
8. Public／Basic Call／Build／Write 0。
9. User実runtime_data 0。
10. 未許可Root外、Git Mutation、NetworkおよびProvider Memory 0。許可済みRead-only Git InspectionとReceipt記載のModel Symlink Target操作は、対象／Command／結果を別Evidenceとして記録する。

Self-review PASSはCodex Independent Reviewを代替しない。

## 9. Human Decision Burden

Claudeは次だけをUser／Codexへ返す。

- 新Authority、Scope拡張、Root外、External、Secret、課金。
- Model Artifact作成／削除等の明示Human Gate。
- 仕様目的を変える選択。
- 重大Risk受容。
- Final Acceptance／Backup／Phase移行。

Phase内のFile構成、Test追加、局所Refactor、Rework、Recovery Entry、Next WU選択および既知Deferred分類はClaude側設計統括者役の責務とする。

## 10. Completion Boundary

Phase 6-Iの全AcceptanceとSelf-reviewを完了し、Phase 6 COMPLETE_CANDIDATE Handoffを作成した時点で停止する。

停止時に次を行わない。

- Phase 6-J。
- User Acceptance代行。
- Phase 7設計／実装。
- Git／GitHub。
- AWS／Lightning／Desktop。
- Stable Roadmap／Currentの最終更新。
