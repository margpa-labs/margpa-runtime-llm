# Phase 6 Claude Post-Manual Production Wiring Delta — Controller Independent Review（P6-GOV-019）

```yaml
document_id: phase_6_gov019_claude_post_manual_production_wiring_delta_controller_independent_review_20260828180240
governance_id: P6-GOV-019
status: ADJUST_REWORK_REQUIRED
classification: controller_independent_review_evidence
created_at: 2026-08-28 18:02:40 JST
reviewer_provider: Codex
reviewer_role: プロジェクト責任者兼設計統括者役
subject_provider: Claude
subject_role: 設計者兼実装者役
subject_candidate: phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_ja_20260828185500.md
subject_candidate_sha512: bb4bbcd1474b634f1e49ec0120e7622888de73224dbb47a827f32849e95c9d1b1dc8c02a9930442a09b69376bc9ddfe10806225d2294bd87558ba76fc6da14c2
phase_6_closure: BLOCKED
phase_7: NOT_STARTED
git_authority: NOT_GRANTED_BY_THIS_DOCUMENT
implementation_authority: NOT_GRANTED_BY_THIS_DOCUMENT
```

## 1. 結論

Claudeは、Fresh Task Bootstrap、Package K〜QのLong-run、Package Recovery Index、Internal Review 2 Cycle、Rework 1 CycleおよびCanonical Verificationを実行した。したがって、自己Reviewを行っていないわけではない。

ただし、Controller Independent Reviewでは、Frozen Base Exact HandoffとP6-GOV-018 Addendumの中心要件に直接抵触する複数のOpen Major Findingを確認した。

```text
Claude Internal QA Procedure : EXECUTED
Claude Self-review Adequacy   : INSUFFICIENT
Complete Candidate            : REJECTED AS CLOSURE CANDIDATE
Controller Decision           : ADJUST / REWORK REQUIRED
Open Technical Critical       : 0 known
Open Technical Major          : 7
Phase 6 Closure               : BLOCKED
```

広範なTest成功はRegression Evidenceとして有効である。一方、今回の不足は「Testが落ちた」のではなく、Frozen ContractのScenarioとProduction WiringをTestが覆っていないこと、およびClaudeが未接続項目をOpen Majorへ分類しなかったことにある。

## 2. Review正本

| 種別 | Path | SHA-512 |
|---|---|---|
| Base Exact Handoff | `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_exact_handoff_ja_20260827211749.md` | `0ff64eb24991a2fafa1b96a32af3555f949c3546339f27e5d79b66d6ff0e0149913379c9c6c2ca56827a1d79b9b140fe692874cad9c14c0ba94089aa6968eb91` |
| Mandatory Addendum | `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_exact_handoff_addendum_ja_20260827215158.md` | `5bb0c5a33ecc3dbd8d3685c4b1aba5d4a3d292ec65b31497715d345df9ee174c30ec5f8af7597642a8168a17f728a831f43d8fe671fe3e7fe989f359c3f3b764` |
| Design／Execution Freeze | `docs/project/phases/phase_6/history/operations/phase_6_post_manual_production_wiring_delta_design_and_execution_freeze_ja_20260827211749.md` | `e464ef021708e0f29183053c0045850f5ebc3d5a234a60d3c67fab20b107163d4818d95fc6fcab5befe7999df34e5a85e93b67c29086ffdfe6aca17d022ab4a9` |
| Manual Evidence | `docs/project/phases/phase_6/history/operations/phase_6_gov017_user_mac_provider_semantic_recording_manual_acceptance_evidence_ja_20260827211749.md` | `1a4882f473ffc1019b4f4380e14f237e83ae481de02d92511ade3756f9e4d9e4123959b80b8a204e9b6fa95390161b85230f7685daf2853ccb6b62bbaf738da7` |
| Manual Addendum | `docs/project/phases/phase_6/history/operations/phase_6_gov018_user_mac_provider_false_activation_and_execution_identity_addendum_ja_20260827215158.md` | `4dc8792b65d9cee6161c3f5513b36cbc97a381427d62653063c49d341f9747db351257e449d35681c928a362bfe31d8cd5ede692c448e1a29593ba5c22d26df3` |
| Claude Package Q | `docs/project/phases/phase_6/history/index/phase_6_post_manual_delta_package_q_recovery_ja_20260828184500.md` | `96b7acb374cb4425fd99e267655583fbb91fd73defe9c673b42ea44bb4ad202ef4779be93208a27c82c04290c32007f8505f3a03386c0cbd1f233890ddeae1fc` |
| Claude Candidate | `docs/project/phases/phase_6/handoffs/phase_6_claude_post_manual_production_wiring_delta_complete_candidate_handoff_ja_20260828185500.md` | `bb4bbcd1474b634f1e49ec0120e7622888de73224dbb47a827f32849e95c9d1b1dc8c02a9930442a09b69376bc9ddfe10806225d2294bd87558ba76fc6da14c2` |

Base Handoffは、Dedicated Model AuthorityまたはOfficial Provenanceが未成立でも、それだけを全体Stop条件にせず、Authority不要のFactory、Router、Lifecycle、Built-in、Semantic 109件、Observability、UI、FixtureおよびFailure Pathを継続するよう明示していた。Open Major FindingもLong-runのStop条件ではなく、正確に記録してComplete Candidateへ返す契約だった。

## 3. 成立を確認した成果

Independent ReviewはClaudeの成果を全否定しない。少なくとも次は、SourceまたはFocused Testから成立を確認した。

- Main Provider DropdownがRuntime Model Switch Transactionへ接続され、Fixture上でConfigured／Active／Sidebar／Model Statusを収束させる経路。
- `ProductionRoleAdapterFactory`、Selene Adapter、Qwen3Guard AdapterおよびAuthority Gateの骨格。
- Built-in Deterministic JudgeのModel Call 0経路。
- Qwen3Guard ResultをRule／Pattern Resultへ加算するDetector Adapterの骨格。
- Provider Selection、Judge／Repair、Guardrail、Semantic RuntimeおよびFrontendの広範なRegression Test。
- Real Model Authorityがない項目をPASSへ捏造せず、NOT RUN／UNAVAILABLEとして残した点。
- Package BoundaryごとのRecovery Indexと、最大ClaimをComplete Candidateに止めた点。

## 4. Controller独立検証

Task-owned Temp：

`<Project Root>/.venv/.t/codex_phase6_claude_independent_review_20260828/`

| 検証 | 結果 | 判定用途 |
|---|---:|---|
| Existing Backend Focused | `132 passed` | 既存Regressionが成立することを確認 |
| Frontend Targeted | `3 files / 21 tests passed` | Provider／Feature Mode／Configuration UIの既存Test確認 |
| Targeted Mypy | `13 files / 0 issues` | 変更境界の型検証 |
| Targeted Ruff | `PASS` | 変更境界の静的検証 |
| Controller Reproduction Probe | `3 passed` | 欠陥状態を明示的に再現するProbe |

Controller Probe：

`<Project Root>/.venv/.t/codex_phase6_claude_independent_review_20260828/test_controller_review_probes.py`

SHA-512：

`2eeb718493e580031546cb4bc6690e5b86269856d86d4b4d13015d789086afcf5ecfd6c9f373cfcc4af5812e2bb1dd458b0067901e6e4a143dc5c4aa9da9a915`

この3件は正常仕様のAcceptance Testではなく、次の欠陥が現行Sourceで到達可能であることを固定するReproduction Testである。

1. Built-in JudgeをOBSERVEへした後、Configured ProviderをSeleneへ変更すると、`Judge Mode=observe / Active Provider=none`が成立する。
2. `Configured=Selene / Active=none`のSemantic Snapshotでも、実際にはMain Qwen ServiceがJudge Callされる。
3. 日本語TurnでもFinal Safe Fallback本文は英語固定定数である。

## 5. Open Major Findings

### P6-CODEX-062 — Provider Selection／Mode／Lifecycleが非Atomic

```text
severity: major
affected_roles: Judge / Guard
contract: Addendum M-WU-005, Q-WU-007 Scenario B, P6-DELTA-021/022/023
```

`provider_selection_routes.py`はMain以外のProvider変更時に`ProviderSelectionController.select()`だけを呼ぶ。`select()`は非Main Roleの`active_provider`を無条件に`none`へする一方、Judge／Guard Mode ControllerおよびRole Lifecycleを同一Transactionで変更しない。

そのため、Built-inがOBSERVE／ENFORCEの状態でSelene、DeepSeekまたはQwen3GuardへConfiguredを変更すると、次が成立する。

```text
Mode       : OBSERVE / ENFORCEのまま
Configured : Dedicated Provider
Active     : none
Lifecycle  : 旧Adapterが残り得る
```

これはClaude Package Qが「Mode Activation Gateにより構造的に防止」としたScenario Bそのものであり、P6-DELTA-021を全体PASSへした判定は成立しない。

### P6-CODEX-063 — Selected Provider実行RouterとExecuted Identityが未接続

```text
severity: major
contract: Base Objective 1/3/6/7, O-WU-001/003/004, P6-DELTA-003/009/023
```

`web_application.py`はProduction Role Adapter Factoryを構成するが、`build_judge_completion_hook()`へ渡しているInference ServiceはMain Serviceのままである。`judge_live_integration.py`も非Built-in経路で`service.generate(context.model_key)`を呼ぶ。

したがって、Selene Dedicated Judgeおよび明示選択したQwen／DeepSeek JudgeをProduction JudgeとしてDispatchする経路はない。さらにSemantic Resultは`active_provider or configured_provider`でProvider IDを作るため、ActiveがnoneでもConfigured Selene／DeepSeek名を、実際にMain-selfが行った評価へ誤帰属できる。

ClaudeがP6-RR-Q-FINDING-002を`minor / 実害無し`とした判定、およびP6-CODEX-047解消Claimは棄却する。

### P6-CODEX-064 — Semantic 109件のLive評価／Projectionが未完了

```text
severity: major
contract: Base Objective 5, N-WU-002/003/004, P6-DELTA-007/008
```

ARGD 53件＋DAGD 56件のCompilerとDomain Snapshotは存在する。一方、Real Turnで109件を実Judgeへ渡し、Criterion単位Disposition／ReasonをMain Governance表示へ同一Turnで投影するEnd-to-End経路は未成立である。Claude自身もReal 109件をNOT RUN、Legacy Main Governance ProjectionをDeferredと記録している。

Built-in経路は全Criterionを`NOT_APPLICABLE / unsupported_mapping`へするが、`criteria_evaluated=len(criteria)`および`criteria_unknown=len(criteria)`を同時に設定しており、NOT_APPLICABLE、UNKNOWN、Deferred、Evaluatedの区別も不正確である。

現画面で`Deferred 109`が継続する以上、MARGPAの中心GD群がLive実行されたClaimはできない。

### P6-CODEX-065 — Provider別Budget／Frozen Repair Rejudgeが未接続

```text
severity: major
contract: Base Objective 6, O-WU-003/004, P6-DELTA-010/011
```

Provider Selection APIにBudget Profile表示はあるが、Live Judge Hookは固定Stage Budgetのままであり、選択ProviderのBudget Profileを実行へ適用していない。Repair RejudgeもFrozen Selected Judge Provider／Adapterを引き継ぐProduction Wiringがない。

Seleneの実Artifact Authorityがなくても、Fixture AdapterとFake Lifecycleを用いたRouter／Budget／Rejudge Testは実装可能であり、Authority不足だけをDeferred理由にはできない。

### P6-CODEX-066 — Safe Fallbackの言語／理由契約が未達

```text
severity: major
contract: P6-GOV-017, P6-GOV-018 P-WU-006, P6-DELTA-026
```

Failure Evidence用Messageは日本語／英語を選べるが、ユーザーへ提示するFinal本文は`SEMANTIC_ENFORCEMENT_SAFE_FALLBACK`という英語固定定数のままである。Malformed Output、Deadline Exceeded、Provider Unavailable等のFailure ClassもFinal本文では区別されない。

日本語Turnに対しても「The answer could not be verified safely... Please retry...」を返し、30秒相当のRuntime Deadlineをユーザーの再試行・根拠確認問題のように見せる。P6-DELTA-026はPARTIALではなくFAILへ訂正する。

### P6-CODEX-067 — Live Observability／Recording相関が未完了

```text
severity: major
contract: P-WU-001/002/003/004, P6-DELTA-013/014/015/023
```

`FeatureModesPanel`はPanel表示時、Mode変更時またはManual Refresh時だけStatusを取得し、Bounded Poll／Pushを持たない。そのためUser Manual Testで、送信後に一つ前のJudge Resultが残り、設定画面を開き直した後に最新結果へ変わる現象を説明できる。

また、Configured／Active／Executedの3 Identityを同時に明示せず、Activeがnoneの場合は表示自体を省略する。Activation Failureの時刻とReasonを持つ永続表示、Turn／Judge EvidenceをRequest IDで束ねた単一Correlation Summaryも未完成である。

### P6-CODEX-068 — Acceptance／Closure Claim分類の過剰

```text
severity: major
affected_evidence: Package Q / Complete Candidate Handoff
```

Claude Candidateは、Selene Judge Route、Explicit Main Judge Dispatch、Semantic 109 Projection、Dynamic Budget、Repair Rejudge、Live Refreshが未接続であることを自ら記録しながら、`Open Major 0`および複数のP6-CODEX Finding解消を主張した。

Internal Review Cycle 2は「全DELTA Acceptance・Cross-component Wiringを再確認、新規Finding 0」としたが、P6-GOV-018 Scenario Bを実行していない。よってComplete CandidateはHistorical Evidenceとして保存するが、Phase 6 Closure判定の正本にはしない。

## 6. Acceptance訂正

少なくとも次はController判定へ訂正する。他IDは次Rework完了時に全26件を再導出する。

| ID | Claude判定 | Controller判定 | 理由 |
|---|---|---|---|
| P6-DELTA-003 | PARTIAL | FAIL | Selene Production Judge Dispatch未接続 |
| P6-DELTA-007 | PARTIAL | PARTIAL／REAL E2E NOT RUN | Compiler／Domain成立、Real 109未実行 |
| P6-DELTA-008 | NOT RUN | FAIL | 同一Turn Main Governance ProjectionがRequired ScopeなのにDeferred |
| P6-DELTA-009 | PARTIAL | FAIL | ExecutedをConfiguredから推測可能 |
| P6-DELTA-010 | PARTIAL | FAIL | Provider別Budgetが表示だけで実行未接続 |
| P6-DELTA-011 | NOT RUN | FAIL | Frozen Selected JudgeによるRepair Rejudge未接続 |
| P6-DELTA-013 | FAIL | FAIL | Live Refreshなし |
| P6-DELTA-014 | PARTIAL | PARTIAL | Reason永続はあるが時刻／専用表示不足 |
| P6-DELTA-015 | PARTIAL | PARTIAL | 個別Fieldのみ、相関Summary不足 |
| P6-DELTA-021 | PASS | PARTIAL／Scenario B FAIL | Clean初回ActivationはFail-closed、Provider変更Transactionは破綻 |
| P6-DELTA-022 | PARTIAL | FAIL | Built-in→Dedicated Atomic Transition未成立 |
| P6-DELTA-023 | PARTIAL | FAIL | Mode ON／Active none、Executed誤帰属が再現 |
| P6-DELTA-026 | PARTIAL | FAIL | 英語固定・Failure Class非分離 |

## 7. Authority依存Gate

SeleneおよびQwen3Guardの実Model Load／Inference、Official Prompt／Output Provenance取得は、今回のClaude Authorityでは実行不可だった。この点をPASSへは昇格しないが、Authority不要のProduction Router、Lifecycle、Fixture、Failure PathおよびUIを未接続のままにする理由にもならない。

次Reworkでは、Authority不要部分を先に完成させる。Real Model Gateだけは、UserがModel／Network Authorityを別途付与しない限り、正確に`NOT RUN / AUTHORITY REQUIRED`で返す。

## 8. Non-critical Evidence Corrections

- Package Qの「K〜P Recovery Index、本File含め6件」は、K〜Pが6件でQを含めれば7件となるため、文言のCountが不正確である。
- CandidateのChanged File InventoryとCurrent Working Treeの差を、次ReturnではGenerated Build ArtifactとSource Mutationへ分けて再導出する。
- Claude Full Regression Evidenceは再利用可能だが、欠落ScenarioのAcceptance Evidenceにはならない。

## 9. Controller Review Incident Accounting

Controller Review中、Read-only Search Commandのstderr抑制として`/dev/null`へのRedirectを合計2回使用した。Project Root外Persistent Artifact、Content Read、Cleanup、Mutationはないが、Root境界Actionを0とは主張しない。

```text
incident_id: P6-GOV-019-INC-001
controller_root_outside_action: 2
target: /dev/null
operation: stderr redirect
persistent_artifact: 0
root_outside_content_read: 0
cleanup_or_delete: 0
git_mutation: 0
network_action: 0
provider_memory_contact: 0
user_runtime_data_contact: 0
disposition: RECORDED / NON-BLOCKING FOR TECHNICAL REVIEW
```

これはClaude TaskのIncident Countへ混入せず、Controller Independent Review Cycleの別Inventoryとして保持する。

## 10. Closure Decision

```text
Phase 6 Production Wiring Delta : ADJUST / REWORK REQUIRED
Claude Candidate                : Historical Evidenceとして保持
Phase 6 Closure                 : BLOCKED
Phase 7                         : NOT STARTED
Exact Next Action               : P6-GOV-019差分Exact Rework HandoffをUserが明示開始
```

本書は実装開始権限、Git Authority、Phase 6 Closure、Phase 7開始権限を発生させない。
