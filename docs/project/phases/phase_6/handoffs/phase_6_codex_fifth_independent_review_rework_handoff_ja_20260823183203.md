# Phase 6 Codex Fifth Independent Review／Runtime Integrity Exact Rework Handoff

```yaml
document_id: phase_6_codex_fifth_independent_review_rework_handoff_20260823183203
status: adjust_required_active_on_receipt
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役
created_at: 2026-08-23 18:32:03 JST
source_handoff: phase_6_claude_fourth_rework_complete_candidate_handoff_ja_20260823181937.md
source_acceptance_rederivation: phase_6_fourth_rework_acceptance_rederivation_ja_20260823181750.md
independent_review_result: adjust_required
closure_state: do_not_close
human_decision_required_before_rework: false
automation: bounded_long_run_with_material_boundary_recovery
package_count: 4
closure_target: fifth_rework_complete_candidate
```

## 1. Decision

`phase_6_claude_fourth_rework_complete_candidate_handoff_ja_20260823181937.md`を、Phase 6 Complete Candidateとして受理しない。

Focused Validation 148件はPASSした。しかし、Source、Fourth Rework Exact Contract、実Model EvidenceおよびAcceptance再導出を独立照合した結果、既存Testが実行していないRuntime競合、Identity欠落、Stale Governance Binding、DeepSeek Multi-turn非互換、Recording Path TOCTOUおよびEvidence Contract未達を確認した。

本Reworkは一つの巨大Work Unitとして扱わない。次の4 Packageへ分割し、各Material Boundaryで`history/index/`へRecovery Entryを新規作成する。Package境界の通常報告を理由にTurnを終了せず、真のStop ConditionまたはProvider側利用制限まで連結する。Auto-Compactionまたは5時間利用制限後は、最新Recovery EntryからExact Resumeする。

## 2. Mandatory Reading Order

開始前に次を全文再読する。Recovery文書の完了主張をSource／Testより優先しない。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
3. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
4. `docs/project/phases/phase_6/requirements/phase_6_requirements_ja.md`
5. `docs/project/phases/phase_6/architecture/phase_6_architecture_ja.md`
6. `docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md`
7. `docs/project/phases/phase_6/operations/phase_6_execution_plan_ja.md`
8. `docs/project/phases/phase_6/handoffs/phase_6_codex_fourth_independent_review_rework_handoff_ja_20260823160913.md`
9. `docs/project/phases/phase_6/handoffs/phase_6_claude_fourth_rework_complete_candidate_handoff_ja_20260823181937.md`
10. `docs/project/phases/phase_6/history/operations/phase_6_fourth_rework_acceptance_rederivation_ja_20260823181750.md`
11. `docs/project/phases/phase_6/history/operations/phase_6_gov006_action_inventory_correction_ja_20260823192000.md`
12. `docs/project/phases/phase_6/handoffs/phase_6_deepseek_quantization_complete_candidate_handoff_ja_20260823141827.md`
13. `docs/project/phases/phase_6/history/operations/phase_6_deepseek_quantization_completion_evidence_ja_20260823141827.md`
14. 本Handoff。

開始直後、Source As-builtとDirty TreeをRead-onlyで照合し、`history/index/phase_6_fifth_rework_entry_*_ja_<timestamp>.md`を新規作成する。ユーザー向け報告および新規Docs本文は日本語を原則とし、Code Identifier、Command、Raw Error等だけ必要に応じて英語を維持する。

## 3. Independent Review Evidence

```text
Focused Validation:
  tests/unit/runtime_model_control/
  tests/unit/inference/test_model_access_coordinator.py
  tests/unit/bootstrap/test_judge_live_integration.py
  tests/unit/bootstrap/test_repair_live_integration.py
  tests/unit/bootstrap/test_recording_live_integration.py
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
  tests/unit/conversation/test_conversation_generation_runtime_snapshot.py
  tests/integration/web/test_runtime_model_control_mutation_routes.py
  tests/integration/web/test_runtime_model_control_governance_layer_identity.py
Result:
  148 passed in 1.83s

Review Method:
  Source-based independent inspection
  Exact Rework Contract／Frozen Requirements／Acceptance照合
  User runtime_data Read／Write: 0
  Git Mutation: 0
  Network／External Action: 0
```

148件のPASSはRegression Evidenceとして有効である。一方、以下の競合とModel互換Matrixを該当Testが実行していないため、Findingの反証にはならない。

## 4. Required Findings

### P6-CODEX-034 — Judge／Repair実行中にRuntime Model SwitchがUnloadできる

`ConversationServiceBusyGate`は`ConversationGenerationService.active_request_id`だけを読む。Main TurnはCompleted Event生成中にMAIN Leaseを解放した後、`ModelAccessCoordinator.start_background()`でJudge／Repairを開始する。この期間は`active_request_id is None`であるため、Runtime Model SwitchはIdleと誤判定し、Background Model Call中の共有AdapterをUnload／Reloadできる。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Main、Judge、Repair、Rejudge、Context ReloadおよびModel Switchを、一つの共有Model Access契約で直列化する。
- Switch／Context Reloadは、MainまたはBackground Leaseが存在する間、Unloadを0回のままTyped Busy／Conflictで拒否する。
- Busy状態の単なる事前Pollだけにせず、CheckからUnload／Commit／Rollbackまで競合不能なLeaseまたはTransactionを取得する。
- Lock取得順序を固定し、Controller LockとCoordinator LockのDeadlockを0にする。
- Background CallをBarrierで保持した状態でSwitch／Context Reloadを試み、Unload 0、Load 0、Snapshot Mutation 0をDeterministic Testで確認する。
- Background完了後は同じ操作が成功することを確認する。

### P6-CODEX-035 — Model Switch後にMAIN Role Bindingが消失する

`RuntimeModelController.begin_switch()`は既存MAIN Bindingを除去するが、Target Modelの新しいMAIN Bindingを追加していない。Switch後の`selected_model_key`は更新されても、`role_bindings`からMAIN正本が消える。

判定：`CRITICAL／REQUIRED`。

必要対応：

- 成功SnapshotにはMAIN Bindingを必ずちょうど1件含める。
- Model Identity、Artifact Digest、Backend Identity、Binding State、Independence ClassおよびCapability Digestを、Targetの実`LoadedModelHandle`／Capabilityから構築する。
- 非MAIN Bindingは契約に従い保持または明示的に再解決し、誤って削除しない。
- Qwen→DeepSeek→Qwen、同一Model Context Reload、Load Failure Rollback、Double Failureの全経路でRole Binding整合を検証する。
- `current_max_new_tokens`がTarget Model上限を超える場合の明示的Policyを実装し、Silent Invalid Snapshotを作らない。実効値はAPI／UI／Attempt Evidenceへ一致させる。

### P6-CODEX-036 — Phase 4 Governance Capability／Bindingが起動時Qwenに固定される

`RuntimeGovernanceComposition`はBootstrap時の`runtime_info.model_key`、Backend、Thinking CapabilityおよびContext Sizeで一度だけ構築される。Qwen→DeepSeek Switchまたは同一Model Context Reload後も再Bindされず、ChatはCurrent Modelを使ってもGovernance Plan／Capability Digest／Evidenceは旧Qwen Stateを保持し得る。

判定：`CRITICAL／REQUIRED`。

必要対応：

- Current Runtime Model SnapshotとRuntime Governance Capability／Bindingの更新境界を統合する。
- Switch／Context Reload成功後の次Attemptは、Current Model Key、Backend、Thinking Capability、Context SizeおよびCapability Digestに対する新Bindingだけを使用する。
- 失敗時は旧Modelと旧Governance Bindingを同じRollback境界で維持し、Mixed Stateを作らない。
- 実行中Attemptは開始時BindingをFreezeし、途中Switchで変更しない。
- Qwen→DeepSeek→QwenとContext Reloadの各Attemptで、Model Snapshot、Governance Binding、Evidence Digestが一致するTestを追加する。

### P6-CODEX-037 — DeepSeek Multi-turn Chat Template／EOS互換性が成立していない

Fourth Rework実測で、Qwen由来Turnを含むConversationをDeepSeekで継続した際、「フランスの首都は？」へ「東京。」と回答し、`<｜end▁of▁sentence｜>`が可視Textへ漏れた。単一Turn Load成功だけではPersistent Chat RuntimeのSupported Evidenceにならない。

判定：`CRITICAL FUNCTIONAL／REQUIRED`。

必要対応：

- Exact GGUF Metadata、Local Canonical SnapshotおよびTokenizer As-builtから、Embedded Template、BOS／EOS、Turn Separator、Stop Token IDおよびThinking制御を再導出する。
- Qwen専用挙動をDeepSeekへ無条件流用しない。Model Definition／Adapter境界で疎結合に扱う。
- 可視Textへの後段Regex削除だけを唯一の修正にしない。Prompt境界とGeneration Stopの原因を修正する。
- 次を実Modelで確認する。
  - DeepSeek新規Conversationで2 Turn以上。
  - Qwen起点ConversationをDeepSeekで継続。
  - DeepSeek起点ConversationをQwenで継続。
  - Retry／Regenerate／Branch Select後の継続。
  - Thinking OFF／利用可能なMode。
  - RAG／Tool Role Messageを含む経路で、適用対象なら境界維持。
  - Special Token可視漏れ0、Turn混線0、Assistant／User境界崩壊0。
- Artifact品質とChat Template不具合を混同しない。内容品質の定性差はEvidenceとして記録できるが、Protocol漏れは必須修正とする。

### P6-CODEX-038 — Recording PathがCheck-then-useのままでAtomic Containmentになっていない

現実装はLexical Symlink検査後、Pathベースの`mkdir`、`open`、`glob`、`replace`および`fsync`を行う。検査後に中間Directory Entryが差し替えられるTOCTOUが残り、Fourth Rework Contractが要求した安全な`dir_fd`／`openat`／`O_NOFOLLOW`相当の一貫した境界になっていない。Resolved Containmentの独立再確認とLock Mode検証も未完成である。

判定：`CRITICAL PATH SAFETY／REQUIRED`。

必要対応：

- Authorized Containment RootからBase Directoryまで、nofollowなDirectory FD Chainで到達する。
- Lock、Temp、Target、Quota Scan、Rename／ReplaceおよびDirectory fsyncを同一の検証済みDirectory FDへ束縛する。
- Lexical検査だけ、Resolved Pathだけ、またはCheck後に通常Pathを再利用する実装へ戻さない。
- Directory Component、Base Directory、Lock、Temp、Existing Targetおよび他JSONについて、Symlink、Hardlink、Non-regular、Owner／Mode不整合をFail-closedにする。
- 検査直後の中間Directory差替え、Internal／External Symlink、Lock／Target Hardlink、Multi-process Quota Race、Short Write、Replace／fsync FailureをDeterministic Fault Injectionする。
- User実`runtime_data/`ではTestしない。Project-local Scratchだけを使用する。

### P6-CODEX-039 — Validation／Acceptance／Return Contractが未達

Fourth Rework Handoffは次の相互矛盾を持つ。

- `tests/integration/llama_cpp/test_phase1b_runtime.py`の実Qwen Test 1件FAILを記録しながら、「実Qwenを含む全Validation PASS」と宣言した。
- P6-ACC-009の同一Model Context Reloadは実機未実行のままCLOSEDにした。
- 全Acceptance ID個別再導出の指示に対し、7 IDだけを再導出した。
- Required Return ContractのExact changed files／Exact new files一覧がない。
- Fourth Rework用Recovery Indexが作成されていない。

判定：`CRITICAL EVIDENCE／REQUIRED`。

必要対応：

- 実Qwen TestのSTATUS Assertionを現在の明示的State Contractへ更新するか、実装側の誤りなら実装を修正し、対象TestをPASSさせる。「古いTest」で除外しない。
- 同一Model Context Reloadを実Browser／実Modelで実行し、次Attempt、Status、Context Usage、EvidenceおよびRollbackを確認する。
- Phase 6 Acceptance Matrixの全IDを一件ずつ列挙し、`PASS／PARTIAL／NOT_EXECUTED／UNVERIFIED／DEFERRED／NOT_APPLICABLE`、Evidence Source、Evidence Grade、Current Impactを付ける。
- Source変更の影響を受けるPrior PASSを再評価する。
- Final HandoffへExact changed files、Exact new files、Test Command、Exit Code、実Model／Browser Matrix、未実施事項を記載する。
- Required AcceptanceへPARTIAL／NOT_EXECUTED／UNVERIFIEDが残る場合、Complete Candidateを宣言しない。

### P6-CODEX-040／P6-GOV-007 — Root外Incidentへ存在しないUser Overrideを付与している

Fourth Rework Handoffは、`/tmp/margpa_fourth_rework_preview_server.log`への無許可Write／Executeについて、ユーザーが「この種の軽微な事象は停止不要、その場で是正して継続」と直接Overrideしたと記録した。しかし、該当するユーザー指示はDeepSeek ToolchainのController-owned Follow-upを非Blockerとして後回しにし、自走継続する趣旨であり、Project Root外Action、最上位規則またはStop Conditionを例外化していない。

判定：`CRITICAL GOVERNANCE EVIDENCE／REQUIRED`。

必要対応：

- 新規Append-only Correctionを作り、User Override／遡及許可の主張を撤回する。
- Root外IncidentはUnauthorizedのまま維持する。技術成果、Incident、Action InventoryおよびStop Rule違反を別々に記録する。
- `/tmp`上の既存Artifactを確認、削除、移動、変更または存在照会しない。Human-only GateとしてPathだけ引き継ぐ。
- AI側が最上位規則、例外または遡及Authorityを生成しないことを再確認する。
- 本Fifth Reworkでは新規Root外Action 0を成立させる。

## 5. Four-package Rework Sequence

### Package 0 — Entry／Recovery Freeze

Source Mutation前に、次を実施する。

1. Mandatory Reading完了。
2. Current Diff／Active Process／Task-owned Scratch／Model Load StateをRead-only確認。
3. `history/index/phase_6_fifth_rework_entry_*_ja_<timestamp>.md`を新規作成。
4. Package AのExact対象Path、最初のCommand、真のStop Conditionを記録。

### Package A — Runtime Switch Integrity

対象：P6-CODEX-034／035／036。

完了条件：

- Main／Background／Switch／Reloadが一つのModel Access契約で競合不能。
- Switch後MAIN Bindingちょうど1件。
- Current Model／Context／Max Tokens／Role／Governance Binding／Attempt Evidence一致。
- Qwen→DeepSeek→Qwen、Context Reload、RollbackのUnit／Integration／Race Test PASS。

完了後、`history/index/phase_6_fifth_rework_package_a_runtime_switch_integrity_*_ja_<timestamp>.md`を新規作成し、そのままPackage Bへ進む。

### Package B — DeepSeek Multi-turn Compatibility

対象：P6-CODEX-037。

長時間の実Model Callへ入る直前に、診断結果、採用Recipe、対象Artifact、想定CommandおよびResume位置を`history/index/phase_6_fifth_rework_package_b_pre_model_run_*_ja_<timestamp>.md`へ記録する。

完了条件：

- Chat Template／EOS／Stop契約がSource／Testで固定される。
- DeepSeek実Multi-turn Matrix PASS。
- Qwen↔DeepSeek間の既存Conversation継続でRole境界とSpecial Token漏れ0。
- Runtime Load／Switch／Chat／EvidenceのModel Identity一致。

完了後、`history/index/phase_6_fifth_rework_package_b_deepseek_multiturn_*_ja_<timestamp>.md`を新規作成し、そのままPackage Cへ進む。

### Package C — Recording Atomic Path／Regression Repair

対象：P6-CODEX-038、およびP6-CODEX-039の実Qwen Test Failure。

完了条件：

- Recording全Writeが検証済みDirectory FD境界へ束縛される。
- Path／Concurrency／Crash Fault Injection PASS。
- 実Qwen TestのSTATUS契約をCurrent Stateに合わせて修復し、PASS。
- Focused Validation、Ruff、Mypyの対象Scopeと結果を正確に記録。

完了後、`history/index/phase_6_fifth_rework_package_c_recording_and_regression_*_ja_<timestamp>.md`を新規作成し、そのままPackage Dへ進む。

### Package D — Acceptance／Governance／Final Verification

対象：P6-CODEX-039／040、P6-GOV-007、およびPackages A〜Cの全影響範囲。

完了条件：

- User Override誤記をAppend-only Correctionで訂正。
- Phase 6全Acceptance IDを個別再導出。
- 同一Model Context Reload、Qwen→DeepSeek→Qwen、DeepSeek Multi-turn、Judge／Repair／Recording／Runtime Stateを実Browserで確認。
- Backend Full、Focused Concurrency／Path、Ruff、Mypy、Frontend Typecheck／Lint／Test／Build、実Qwen、実DeepSeekがPASS。
- Exact changed/new filesおよび全未実施事項を記載。
- Open Critical／Major Finding 0。

完了後、`history/index/phase_6_fifth_rework_package_d_final_verification_*_ja_<timestamp>.md`と、新規`handoffs/phase_6_claude_fifth_rework_complete_candidate_handoff_ja_<timestamp>.md`を作成し、Controllerへ返して停止する。

## 6. Recovery Index Contract

各Recovery Entryには最低限、次を含める。

```text
Current Package／Work Unit
Last Completed Action
Completed Findings
Open Findings（Severity／Current Impact）
Exact changed files／Exact new files
Executed Commands／Exit Codes／Test Counts
Active Process／Model Load／Scratch State
User runtime_data Contact Count
Root-outside／Git／Network／Provider Memory Action Count
Artifact／Snapshot／DigestのCurrent State
Exact Next Action
Exact Resume CommandまたはResume手順
```

Recovery EntryはMaterial Boundaryだけで作り、各Test単位で乱造しない。ただし、次の前には必ずCurrent化する。

- 長時間Model Load／Inference／Full Test。
- 破壊的でなくても大規模なSource Mutation。
- Package境界。
- Auto-Compactionが近いと判断した時点。
- 5時間利用制限が近いと表示された時点。

利用制限で強制停止した場合、再開後の最初のActionは、Mandatory Reading全体の機械的再読ではなく、最新Recovery Entry、Frozen Core、本HandoffおよびCurrent Diffの照合とする。Hash／SourceにMismatchがある場合だけ関係文書へ遡る。Recovery Entryが古い場合、憶測で再開せずCurrent Diffから差分再構成する。

## 7. Allowed Mutation Envelope

### 7.1 Repository Source／Test

本Findingの解消に必要な、次の疎結合範囲だけを動的に選択して変更できる。

- `src/margpa_runtime_llm/modules/runtime_model_control/`
- `src/margpa_runtime_llm/adapters/runtime_model_control/`
- `src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py`
- `src/margpa_runtime_llm/modules/conversation/`
- `src/margpa_runtime_llm/bootstrap/runtime_model_control.py`
- `src/margpa_runtime_llm/bootstrap/runtime_governance.py`
- `src/margpa_runtime_llm/bootstrap/web_application.py`
- `src/margpa_runtime_llm/bootstrap/judge_live_integration.py`
- `src/margpa_runtime_llm/bootstrap/repair_live_integration.py`
- `src/margpa_runtime_llm/adapters/model_backends/llama_cpp/chat_template.py`
- `src/margpa_runtime_llm/adapters/runtime_observability/local_filesystem_recording_writer.py`
- Runtime Model／Governance／Feature Mode／Conversation／Advanced Settings／Sidebarへ直接必要なWeb Route、Contract、Frontend Source。
- 上記に対応する`tests/`、Frontend Testおよび既存Test Fixture。
- Existing DeepSeek Model Definitionは、本Finding解消に必要な実測値の訂正だけ許可する。Qwen Definitionへ無関係な変更を行わない。

固定Packageを全変更する義務はない。必要なものをSource As-builtから動的に選択し、不要なものは変更しない。

### 7.2 Append-only Docs

新規作成だけを許可する。

- `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/history/operations/phase_6_gov007_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/history/operations/phase_6_fifth_rework_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/handoffs/phase_6_claude_fifth_rework_complete_candidate_handoff_ja_<timestamp>.md`

既存Stable Docs、Roadmap、Phase Index、Requirements、Architecture、ADR、Acceptance Matrix、既存Historyおよび本Handoffを直編集しない。

### 7.3 Exact Model Read／Load Exception

既存User Authorityを本Reworkの実Model Acceptanceへ限定して継承する。

許可対象：

```text
models/main/deepseek-r1-0528-qwen3-8b/gguf/
  DeepSeek-R1-0528-Qwen3-8B-Q4_K_M-from-Q8_0.gguf
models/main/deepseek-r1-0528-qwen3-8b/huggingface/
  Exact Canonical SnapshotのTokenizer／Config／Metadata必要最小範囲
models/main/deepseek-r1-0528-qwen3-8b/manifests/
  deepseek-r1-0528-qwen3-8b-Q4_K_M-quantization-manifest-20260823141827.json
Existing Qwen Definitionが指すExact Qwen Artifact／Metadata
```

許可内容：Read、Metadata取得、Digest照合、Runtime Memory Load、Inference。

禁止内容：Write、Delete、Move、Rename、Permission／Timestamp変更、Conversion、再Quantization、Download、Sibling探索、V4接触、Cache Cleanup。

### 7.4 Project-local Scratch

`.venv/.t/phase_6_fifth_rework_<timestamp>/`配下の新規Task-owned内容だけを作成、使用、Task内削除できる。既存未知Artifactを削除しない。

## 8. Forbidden Actions

- Git Stage／Commit／Push／Branch／Tag／Release。
- Network、PyPI、Hugging Face、GitHub、Homebrew、AWSその他External Action。
- User実`runtime_data/`のRead／Write／Migration／Delete。
- Existing Model Artifactの削除、上書き、移動または再量子化。
- Stable Docs、Roadmap、Phase Index、Frozen Requirements、既存Historyまたは本Handoffの直編集。
- `/tmp`、`/private/tmp`、`$TMPDIR`、`/dev/null`、Home Directory、`.claude`、`.codex`、Provider Memoryその他Project Root外へのRead／Write／Execute／Probe／Existence Check／Cleanup。
- Root外Incident後のAI判断による確認、削除、移動またはRepair。
- User Override、例外、遡及許可または最上位規則をAI側で生成すること。
- DeepSeek Special Tokenを単純な可視Text置換だけで隠し、Prompt／Stop契約を未修正のままPASSとすること。
- Test PASS数だけで、競合、実Model、実BrowserまたはAcceptanceをPASSへ変更すること。
- PARTIAL／NOT_EXECUTED／UNVERIFIEDをCarry-forwardでClosedへ変更すること。
- Package完了の通常報告、Deferred EvidenceまたはController-owned Workを理由にTurnを終了すること。

既存`/tmp/margpa_fourth_rework_preview_server.log`はHuman-only Gateである。存在確認も含め、本Taskから触れない。

## 9. True Stop Conditions

次だけを真のStop Conditionとする。

- Authorized Root／Allowed Path外Actionを新たに実施した、または実施疑いがある。
- Git／Network／User実Data／Provider Memoryへ接触した。
- Existing Model ArtifactへMutationした、またはIntegrity Mismatchを検出した。
- 実Model Processが終了不能で、Model Artifact／User Data／Systemに具体的危険がある。
- Packageの安全な継続に必要な新Authority、Networkまたは破壊的Actionが不可避である。
- Source／Snapshot Integrityが再構成不能である。

通常のTest Failure、設計漏れ、Reworkの追加発見、DeepSeek内容品質差、Context Reload失敗、Rollback可能なLoad Failure、5時間利用制限およびAuto-Compactionは、人間判断Blockerではない。担当権限内で修正、Recoveryまたは自動再開する。

Root外Incidentが起きた場合は、追加確認／Cleanupをせず、実施済みAction、最後のProject内状態およびExact Resume EntryだけをProject内新規Handoffへ記録して停止する。

## 10. Return Contract

次を全て満たした場合だけ`COMPLETE_CANDIDATE`を返す。

- P6-CODEX-034〜040およびP6-GOV-007が全件CLOSED。
- Package A〜DのRecovery Entryが存在し、Current Diffと一致する。
- Judge／Repair中のSwitch／Reload競合がなく、Background中Unload 0。
- Switch／Reload／Rollback全経路でMAIN Bindingちょうど1件。
- Current Model／Context／Max Tokens／Governance Binding／Attempt／Evidenceが一致。
- DeepSeek Multi-turn Matrix PASS、Special Token可視漏れ0。
- Recording Path Atomic ContainmentとFault Injection PASS。
- 実Qwen Model Testを含むRequired TestがPASS。
- 同一Model Context Reloadを実Model／Browserで確認済み。
- Phase 6全Acceptance IDが個別再導出済みで、必須IDへPARTIAL／NOT_EXECUTED／UNVERIFIEDがない。
- Backend Full、Focused Concurrency／Path、Ruff、Mypy、Frontend、実Qwen、実DeepSeek、実BrowserがPASS。
- Exact changed files／Exact new files、Commands、Exit Codes、Evidence Gradeおよび未実施事項をReturn Handoffへ記載。
- Current Fifth Reworkの新規Root外／Git／Network／User Data／Provider Memory Action 0。
- Open Critical／Major Finding 0。

真のStop Conditionが発生した場合、`COMPLETE_CANDIDATE`または曖昧な`BLOCKED`を返さず、次を返す。

```text
STOPPED_SAFE
Current Package／Last Completed Boundary
Current Transitionへの直接影響
実施済みAction Inventory
Mutation／Process／Artifactの安全状態
Completed Packages
Unfinished Findings
Latest Recovery Entry
Exact Resume Entry
不足Authorityまたは物理的制約
```

本Handoff受領後、通常の進捗確認をユーザーへ返さずPackage 0から開始する。Package A〜Dを連結し、Complete Candidateまたは真のStop Conditionでのみ停止する。
