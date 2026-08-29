# Phase 6 Post-Manual Production Wiring Delta 設計・実行Freeze（P6-RR-DELTA）

```yaml
document_id: phase_6_post_manual_production_wiring_delta_design_and_execution_freeze_20260827211749
status: controller_frozen_pending_user_activation
classification: differential_design_execution_acceptance_freeze
phase: phase_6
owner: プロジェクト責任者兼設計統括者役
target_provider: Claude
target_role: 設計者兼実装者役
created_at: 2026-08-27 21:17:49 JST
implementation_authority: false
closure_authority: false
phase_6_closure: blocked
phase_7: not_started
```

## 1. 結論

Phase 6 Remaining ReworkのPackage 0〜Iでは、Semantic Domain、Provider Registry、Lifecycle、Selene／Qwen3Guard Adapter候補、Budget、Failure表示、Recording相関およびAdvanced Mode UIの土台が実装された。しかし、Controller Independent ReviewとUser Mac Manual Acceptanceにより、Production Execution経路がその土台を正しく使用していないことを確認した。

本差分Reworkの目的は、成立済み土台を再実装することではない。次をProduction経路へ実配線し、表示とEvidenceを実行事実へ一致させることである。

```text
Configured Provider
  → Preflight / Load / Activation
  → Active Provider
  → Turn Frozen Snapshot
  → Executed Provider
  → Result / Action / Final
  → Recorded Provider / Correlated Evidence
```

```text
Definition / Descriptor
  → Criterion Selection
  → Batched Semantic Evaluation
  → Pass / Deviation / Unknown / Deferred with exact reason
  → Conflict / Action Resolution
  → Repair / Rejudge / Safe Fallback
  → Current and Historical Observability
```

## 2. 正本とLineage

本書は次をLosslessに継承する。

1. Phase 6 Requirements、Architecture、ADR、Execution Plan、Acceptance Matrix。
2. `P6-RR-DESIGN`とRemaining Rework Execution Plan。
3. Package 0〜IおよびPackage J Bounded Completion Candidateの成立済みEvidence。
4. P6-GOV-016 Controller Independent Review。
5. P6-GOV-017 User Mac M-1〜M-7 Manual Acceptance Evidence。
6. UserがManual Check後にPhase 6へ前倒し指定したBounded Advanced Mode／Sidebar UI Delta。

本書はHistorical Evidenceを削除・置換しないAppend-only Differential Freezeである。過去のPASSを再実行なしに無条件継承せず、変更によって無効化されないEvidenceだけを明示的にReuseする。

## 3. User Macで成立した事実

### 3.1 成立

- Startup時、MainはQwen Active、GuardはQwen3Guard Configured／Active none、JudgeはSelene Configured／Active noneだった。
- 全ModeはOFFだった。
- Built-in選択時、Configured／Activeの表示自体は`built_in.deterministic`へ変化した。
- Recording FULLではTurn RecordとJudge Evidence Recordの書込み成功を確認した。
- Main Model StatusとSidebarは、実際にLoad中のQwenを表示し続けた。

### 3.2 未成立

- Main DropdownはConfiguredだけをDeepSeekへ変更し、Runtime Switch Transactionを実行しなかった。
- Selene／Qwen3GuardのProduction FactoryまたはArtifact Resolutionが成立せず、Active noneのままMode Activationに失敗した。
- Activation Failureは汎用かつ一時表示で、Exact Reasonを保持しなかった。
- Built-in Deterministic選択時もAPIの`judge_role`は`main_self`で、LLM出力をParseして`malformed_output`になった。
- Semantic Criteriaは32件Selected、0件Evaluatedであり、Main Governance側の109件は全件Deferredのままだった。
- Provider Identity、Model Status、Sidebar、Judge Statusに異なるState Projectionが混在した。
- Judge StatusはTurn完了後の自動更新がなく、設定画面の再Openで初めて最新化する場合があった。
- OFF後も前回結果をCurrentまたは「現在実行中」と誤表示した。
- Recording Summaryは書込み成否を示したが、同一Requestとの相関を一画面で完全には示さなかった。

## 4. 不変Contract

### 4.1 Provider State分離

次を同一視しない。

```text
Available    : Registryに定義がある
Configured   : Userが次回Activation対象として選択した
Active       : Load／Preflight／Activation Transactionに成功した
Executed     : 当該TurnでFrozen Snapshotにより実際に呼ばれた
Recorded     : EvidenceへProvider Identityが永続化された
Displayed    : UIが上記のどのStateを表示しているか明記した
```

`Configured != Active != Executed != Recorded`をAPI、Domain、Test、UIの全境界で維持する。Configuredだけ変わったProviderをCurrent／Active／Executedと表示しない。

### 4.2 Built-in Deterministic

`built_in.deterministic`はModelではない。次を禁止する。

- Main Modelまたは別LLMを暗黙に呼ぶ。
- Modelの自由文JSONをParseする。
- `judge_role=main_self`を返す。
- Model Timeout／Malformed OutputをBuilt-in結果として返す。

Built-inは実装済みの決定論的Capabilityだけを評価し、未対応Criterionを`unknown`または`deferred`へExact Reason付きで分類する。対応していない意味論を評価済みと捏造しない。

### 4.3 Dedicated Provider

- Selene選択時はSeleneだけをJudgeとして実行する。
- Qwen／DeepSeekをJudgeに使う場合はUserの明示選択を必要とする。
- Qwen3Guard選択時はRule／Pattern Base経路に加算するDedicated Guardとして実行する。
- `none`はLoad、Inference、Budget消費、暗黙Fallbackを行わない。
- Provider Unavailable時はModeをOFFへRollbackし、Configuredは保持してよいが、Active／Executedをnoneとする。
- Failure ReasonはTyped Code、利用者向け説明、Provider、Stage、時刻を保持する。

### 4.4 Semantic Rule

ARGD／DAGDから選択されたSemantic Rule 109件を、黙って32件だけに縮小しない。Budget上Batchへ分割する場合も、Turn終了時に109件それぞれについて次のいずれかを確定する。

```text
pass
deviation
unknown
deferred(reason_code)
not_applicable(reason_code)
```

Remaining 77件のIdentityと理由をEvidenceから復旧できなければならない。Legacy Main Governance表示と新Semantic Resultは、同一Turn／同一Frozen Snapshotに相関させる。

### 4.5 Judge／Repair／Rejudge

- JudgeはSelected／Active Providerを実行する。
- ProviderごとのLoad、Prompt、Inference、Parse、Publish Budgetを用いる。
- 固定30秒を全Providerへ一律適用しない。
- Repair後のRejudgeもFrozen Contractで指定されたProviderを使う。
- Timeout、Malformed Output、Unavailable、Cancelled、Budget Exceededを区別する。
- Failure時にCandidateを通すかSafe Fallbackへ収束するかはModeとFailure ClassのContractに従う。
- Safe FallbackはTurnの回答言語とFailure Reasonに応じた文面とし、Userの責任を示唆しない。

### 4.6 Current／Historical／Recording

- Mode OFF時のCurrent Runは`disabled`または`none`であり、前回ResultをCurrent扱いしない。
- 実行中はCurrent Requestを表示し、前回ResultはHistoricalとして分離する。
- 完了／失敗／取消／Mode OFFをBackend EventまたはBounded Pollingで自動反映する。
- Turn RecordとJudge Evidence Recordは、Request ID、Turn ID、Started／Completed、Frozen Modes、Configured／Active／Executed Provider、Budget、Outcome／Failure、Repair／Rejudgeを相関表示する。
- Recording OFFでもJudge Result内にFrozen Recording Modeを表示してよいが、Recording成功を示してはならない。

## 5. Exact Differential Package

### P6-RR-K — Recovery／As-built Reconciliation

#### K-WU-001 Mandatory Reading／Digest

- Frozen文書と指定Digestを照合する。
- Package 0〜IをCOMPLETEのまま保持し、再実装しない。
- Package JのPASS／PARTIAL／FAIL／NOT RUNをそのまま継承する。

#### K-WU-002 Source-to-Production Map

- Registry、Lifecycle、Factory、Router、Feature Mode、Main Switch、Status API、FrontendのCall GraphをSource Evidenceで固定する。
- Test Fixtureだけが通りProduction Compositionが旧経路を使う箇所を列挙する。

#### K-WU-003 Recovery Index

- 変更前のExact Gap、再利用する実装、最初のMutation対象を記録する。

### P6-RR-L — Official Provenance／Artifact Authority／Factories

#### L-WU-001 Official Contract Provenance

- Selene Official Prompt TemplateとQwen3Guard Official Output Contractについて、Exact Upstream Revision／URL／DigestをProject内Manifestへ固定する。
- Network Authorityがなければ無断取得せず、Local Evidenceで可能な後続を継続し、ProvenanceをTyped PARTIALとする。

#### L-WU-002 Exact Artifact Preflight

- Selene／Qwen3Guard Artifactは、User発行の別Exact Model Authority Receiptで許可されたPath／OperationだけをRead／Loadする。
- 既存Qwen／DeepSeek ReceiptをSelene／Qwen3Guardへ拡張解釈しない。

#### L-WU-003 Production Factories

- SeleneとQwen3GuardのModel Definition、Artifact Resolver、Loader、Adapter FactoryをProduction Compositionへ登録する。
- Artifact missing、Digest mismatch、Hardware Gate、Load failureをTyped Failureにする。

#### L-WU-004 Focused Verification／Recovery

- Factory unavailable、成功、Rollback、Cancellation、Load failureを検証する。

### P6-RR-M — Provider Routing／Lifecycle／Main Switch

#### M-WU-001 Provider Execution Router

- Role Frozen SnapshotからSelected／Active Adapterを解決し、Executed IdentityをResultへ返す。
- Judge、Guard、Mainの暗黙Cross-role fallbackを除去する。

#### M-WU-002 Main Dropdown Transaction

- Main Provider選択をRuntimeModelControllerの実Switch Transactionへ接続する。
- Configuredだけの変更で成功表示しない。
- Success時はProvider Selection、Model Status、Sidebarを同一Revisionへ収束させる。
- Failure時は旧MainをActive維持し、Configured／Failureを正確に表示する。

#### M-WU-003 Role Lifecycle

- Mode Activation時にConfigured Dedicated ProviderをLoadし、成功時だけActive／ModeをCommitする。
- OFF、Provider変更、Shutdown、Busy、Cancellation、Load FailureのDrain／Rollback／Unloadを有界にする。

#### M-WU-004 Status Projection

- Model StatusのCurrent Main／Judge／Guardを、実Active Stateから投影する。
- Built-inはModel名ではなくProvider Typeとして表示する。
- Sidebarは実Current Mainと環境情報を保持する。

### P6-RR-N — Semantic／Built-in／109 Rule Integration

#### N-WU-001 Built-in Deterministic Repair

- Built-inがLLM Callを行わない実装とRegressionを追加する。
- APIの`judge_role`、configured／active／executedを`built_in.deterministic`へ一致させる。

#### N-WU-002 Criterion Capability Mapping

- Built-in、Selene、Main Model Judgeごとに評価可能Criterionを明示する。
- Capability不足をMalformed OutputではなくTyped Unknown／Deferredへ分類する。

#### N-WU-003 Batched Semantic Evaluation

- 109件をBudget内Batchへ分割し、全Criterion ResultをMergeする。
- exactly-once、Cancel、Timeout、Late Publish拒否、Duplicate ID拒否を維持する。

#### N-WU-004 Legacy Main Governance Projection

- `Selected 109 / Deferred 109`固定表示を、実Semantic Resultへ接続する。
- Structural ObservationとSemantic ObservationのIdentity／Source／ReasonをLosslessに統合する。

#### N-WU-005 Controlled Fixture

- Evidence矛盾、ユーザー訂正との矛盾、根拠なき断定、Premise逸脱のControlled Inputで全Criterion dispositionを検証する。

### P6-RR-O — Dedicated Guard／Judge／Repair／Budget

#### O-WU-001 Selene Judge Route

- Official Prompt、Strict Decoder、Typed Result、Provider BudgetをProduction Judge Hookへ接続する。
- Selene選択時にMain-selfを呼ばない。

#### O-WU-002 Qwen3Guard Additive Route

- Rule／Pattern Base ResultとQwen3Guard ResultをSource Identity付きでMergeする。
- Guard Model unavailable時のMode RollbackとFailure表示を保証する。

#### O-WU-003 Explicit Main Model Judge

- Qwen／DeepSeekはJudge Dropdownで明示選択した場合だけJudge Roleに使用する。
- MainとJudgeが同一Artifactでも、Role Lease、Budget、Executed Identityを分離する。

#### O-WU-004 Stage Budget／Repair Rejudge

- Provider／Hardware Profile別Budgetを用いる。
- Repair後はSelected Judgeで再評価し、initial／repair／rejudge Evidenceを同一Requestへ相関する。

#### O-WU-005 Failure Matrix

- unavailable、load_failed、deadline_exceeded、malformed_output、cancelled、shutdown、publisher_failedを個別に検証する。

### P6-RR-P — Observability／Recording／Bounded UI Delta

#### P-WU-001 Live Status Lifecycle

- 設定Open中もCurrent Run、Completion、Failure、Cancel、OFFを自動更新する。
- CurrentとHistoricalを明確に分離し、「別Turnの結果です—現在実行中」を実際の状態と一致させる。

#### P-WU-002 Recording Correlation

- Request ID、時刻、Frozen Modes、Configured／Active／Executed Provider、Outcome／Failure、Turn Record、Judge Evidence Recordを同一Summaryで表示する。

#### P-WU-003 Activation Failure

- Generic Toastだけでなく、設定画面内にExact Failure Code／Reason／Provider／時刻を再読可能な状態で保持する。

#### P-WU-004 Bounded Advanced Mode Layout

User指定によりPhase 6へ含めるのは次だけである。

1. Model Status内の重複Main Model切替欄だけを非表示にする。削除せずRollback可能とし、Context Size／Max New Tokensは維持する。
2. Advanced Mode順を`Judge／Repair／Recording → Model Status → Role Provider選択 → Runtime設定制御`へ変更する。
3. Research・Developer ModeのOFF／ON Controlを非表示にし、詳細を最初から表示する。Backend Toggle Contractは削除しない。
4. 詳細内の`research_developer_mode` Fieldを非表示にする。
5. 残る6 Fieldを左右3対3へ配置する。

```text
Left                         Right
conversation_storage_kind    acceleration_api
conversation_storage_version backend_kind
profile_key                  device_kind
```

6. Sidebarを、実Current Main Modelに加え、profile、device、accelerationを失わない表示へ戻す。`active · Context`だけで環境情報を上書きしない。
7. Judge Result詳細はOBSERVE／ENFORCE中も表示し、OFF時はCurrent disabledとHistoricalを分離する。

次は本差分へ含めず、Phase 9予約を維持する。

- Context 16384 Profile昇格とMax New Tokens上限再設計。
- Model別Context設定保持。
- Progressive／Strict ENFORCE Streaming。
- 区切り線、Margin、Button整列、回答言語Dropdown幅など一般UI磨き込み。
- 右側Governance Trace Panel。

#### P-WU-005 CLI／Help／API Contract

- Provider選択、Mode、Status、FailureのCLI Help／API Schema／Frontend型を一致させる。

### P6-RR-Q — Integrated Verification／Acceptance／Return

#### Q-WU-001 Focused／Static

- 変更箇所のFocused Test、Canonical Mypy、Ruff Format／Checkを実行する。

#### Q-WU-002 Full Regression

- Backend Full、Frontend Typecheck／Lint／Test／BuildをProject内Temp Contractで実行する。

#### Q-WU-003 Real Provider Matrix

Exact Artifact Authorityが成立した場合だけ、Selene／Qwen3GuardのLoad、Activate、Turn、Cancel、OFF、Reloadを検証する。AuthorityまたはHardware不足をPASSへ読み替えない。

#### Q-WU-004 Real Browser Matrix

- Main Switch、Dedicated Activation、Built-in、Semantic 109、Current／Historical、Recording、Bounded UIを実Browserで検証する。
- User Macにしか成立しない項目はUser Manual Gateとする。

#### Q-WU-005 Acceptance Re-derivation

- Original 40 Acceptance IDを全件再掲する。
- 変更に無関係な成立済みEvidenceはExact Path／Digest付きでReuseできる。
- 影響IDは再導出し、PARTIAL／NOT RUN／FAILをPASSにしない。

#### Q-WU-006 Completion Candidate

- Package Q RecoveryとClaude Return Handoffを作り、Controller Independent Reviewで停止する。
- Phase 6 Closure、Git、Backup、Roadmap、Phase 7へ進まない。

## 6. Delta Acceptance

| ID | Acceptance |
|---|---|
| P6-DELTA-001 | Main Dropdown成功時に実Mainが切り替わり、Configured／Active／Model Status／Sidebarが同一Revisionへ収束する。 |
| P6-DELTA-002 | Main Switch失敗時に旧Activeを維持し、ConfiguredとExact Failureを区別する。 |
| P6-DELTA-003 | Selene選択時、Selene Production FactoryとRouteを使用し、Main-selfへ暗黙Fallbackしない。 |
| P6-DELTA-004 | Qwen3Guard選択時、Dedicated GuardをRule／Pattern Baseへ加算し、実Provider Identityを記録する。 |
| P6-DELTA-005 | Built-in DeterministicはLLM Call 0で完了し、`malformed_output`をModel由来に発生させない。 |
| P6-DELTA-006 | `none`選択時はLoad／Inference／Budget消費／暗黙Fallbackが0である。 |
| P6-DELTA-007 | 109 Semantic Rule全件にDispositionとReasonがあり、32件以外の77件を消失させない。 |
| P6-DELTA-008 | Main GovernanceのSemantic表示が同一TurnのCriterion Resultを反映する。 |
| P6-DELTA-009 | Configured／Active／Executed／Recorded ProviderがAPI／UI／Evidenceで一致する。 |
| P6-DELTA-010 | Provider別Stage Budgetを用い、固定30秒一律Contractを使用しない。 |
| P6-DELTA-011 | Repair RejudgeはFrozen Selected Judgeを使用し、initial／repair／rejudgeを相関する。 |
| P6-DELTA-012 | Mode OFF時Currentはdisabled／none、前回ResultはHistoricalとして分離される。 |
| P6-DELTA-013 | Turn完了後、設定画面を閉じ直さずCurrent ResultとRecording Summaryが有界時間内に更新される。 |
| P6-DELTA-014 | Activation Failureが消えず、Typed Code／Reason／Provider／時刻を再読できる。 |
| P6-DELTA-015 | Recording SummaryがRequest ID、時刻、Frozen Modes、Provider、Outcome、Turn／Judge Evidenceを相関表示する。 |
| P6-DELTA-016 | User指定7件のBounded UI Deltaが成立し、Phase 9予約項目を混入しない。 |
| P6-DELTA-017 | Focused／Static／Backend Full／Frontend Canonicalで新Regression 0。 |
| P6-DELTA-018 | Real Provider未実行またはHardware／Authority不足をPASSへ捏造しない。 |
| P6-DELTA-019 | P6-RR-INC-001およびP6-RR-ACC-039をHistorical Nonconformanceとして保持する。 |
| P6-DELTA-020 | ClaudeはComplete Candidateまでで停止し、Closure／Git／Phase 7を主張しない。 |

## 7. Original Acceptance影響範囲

少なくとも次は差分修正後に再導出する。

```text
P6-RR-ACC-003〜009
P6-RR-ACC-014〜018
P6-RR-ACC-019〜035
P6-RR-ACC-037〜039
```

P6-RR-ACC-039はHistorical Root-outside Incidentが存在するため、Literal `0` Claimへ昇格できない。Requirementの目的を満たすCorrectionとIncident Accountingを示し、過去事実を消さない。

## 8. Authority依存

### 8.1 本書だけでは許可されない

- Selene／Qwen3GuardのProject Root外Symlink Target Read／Load。
- Network GET／Clone／Package Install／Model Download。
- Git Read／Write／Commit／Push。
- User `runtime_data`接触。
- Provider Memory接触。

### 8.2 実行前に別Receiptが必要

Dedicated Real Model Verificationには、Selene／Qwen3GuardのExact Root、Resolved Target、許可Operation、期間、Read-only／Load境界を定めたUser Authority Receiptが必要である。ReceiptがなければContract／Fixture／Failure Pathを実装・検証し、Real Model項目をPARTIAL／NOT RUNとする。

Official ProvenanceのNetwork取得にも、Exact Domain／URL／Methodを定めたUser Network Authorityが必要である。取得不能を理由に、無関係なPackageを停止しない。

## 9. Evidence／Recovery Contract

- Package K〜Qごとに`docs/project/phases/phase_6/history/index/`へRecovery Indexを作る。
- Indexは成立済みEvidence、変更File、Verification、Open Finding、Incident、`next_exact_work_unit`を記載する。
- Auto-Compaction／5時間制限後は最新Indexから差分再開し、完了Packageをやり直さない。
- Package Reportは停止点ではない。True Stop Condition以外は次へ進む。
- Package JのCanonical Evidenceは、影響を受けない範囲だけ再利用する。

## 10. Completion Boundary

Claudeが主張できる最大状態は次である。

```text
Phase 6 Production Wiring Delta Rework:
  COMPLETE_CANDIDATE_WITH_EXACT_PASS_PARTIAL_NOT_RUN_FAIL

Phase 6 Closure: NOT CLAIMED
Phase 7: NOT STARTED
```

Test PASSだけでProduction Wiring、Real Provider、Semantic 109件またはUser Manual AcceptanceをPASSにしない。Final判定はController Independent ReviewとUser Manual Acceptanceに残す。
