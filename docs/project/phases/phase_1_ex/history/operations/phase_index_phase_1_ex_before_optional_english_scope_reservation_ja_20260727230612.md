# Phase 1-ex Documentation Index

```yaml
document_id: phase_1_ex_documentation_index
phase: phase_1_ex
status: active
language: ja
created_at: 2026-07-26 15:16:24 JST
updated_at: 2026-07-27 22:57:35 JST
owner: 設計統括者役
rag_default: true
```

## 1. Phase Goal

Phase 1成果を公開可能・継続可能・Git管理可能な構造へ移し、GitHub初回公開と後続Phaseの基盤を整える。

## 2. Documentation Migration

- [ADR-0024](adr/adr_0024_phase_first_project_documentation_and_lossless_history_ja.md)
- [Target Documentation Structure](architecture/target_documentation_structure_ja.md)
- [Migration Requirements](requirements/documentation_migration_and_canonical_content_requirements_ja.md)
- [Source Inventory](operations/documentation_source_inventory_and_classification_ja.md)
- [Source→Target Manifest](operations/source_to_target_documentation_migration_manifest.json)
- [Link／Rollback Plan](operations/documentation_link_update_and_rollback_plan_ja.md)
- [Migration Preflight](operations/documentation_migration_preflight_ja.md)
- [Candidate Report](operations/documentation_migration_candidate_report.json)
- [Migration Receipt](operations/documentation_directory_migration_receipt_ja.md)
- [Migration Validation](operations/documentation_directory_migration_validation_ja.md)
- [Legacy Root Retirement Manifest](operations/documentation_legacy_root_retirement_manifest.json)
- [Legacy Root Retirement Validation](operations/documentation_legacy_root_retirement_validation_ja.md)
- [Target Manifest](operations/documentation_directory_migration_target_manifest.json)

## 2.1 Phase 1-ex追加設計

- [ADR-0025 Public Demo／Auto-start／Pre-release Gate](adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [ADR-0026 Lightning Basic Preview Lifecycle／Managed Secrets](adr/adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets_ja.md)
- [Public Demo／Auto-start／Pre-release Requirements](requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start／RAG Extension Architecture](architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [Pre-initial Commit Documentation Refresh Plan](operations/pre_initial_commit_documentation_refresh_plan_ja.md)

## 2.2 Active Implementation Handoff

- [実装担当向け Lightning Auto-start Read-only Preflight Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_read_only_preflight_20260726192912.md)
- [実装担当向け Lightning Basic Preview Lifecycle Scripts Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_basic_preview_lifecycle_scripts_20260726194949.md)
- [設計統括者Review：Auto-start／Lifecycle Scripts](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_and_lifecycle_scripts_20260726202036.md)
- [実装担当向け Lifecycle Safety Follow-up Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726202036.md)
- [実装担当 Lifecycle Safety Follow-up最終Status](history/handoffs/implementer_status_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726212010.md)
- [設計統括者Review：Lifecycle Safety Follow-up Accepted](history/handoffs/designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726213429.md)
- [Lightning手動Environment／Preflight Evidence](history/operations/lightning_manual_environment_and_preflight_evidence_20260726233910.md)
- [実装担当向け Linux `/proc` Test Fixture Follow-up Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md)
- [実装担当 Linux `/proc` Test Fixture Follow-up Status](history/handoffs/implementer_status_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235039.md)
- [設計統括者Review：Linux `/proc` Test Fixture Accepted](history/handoffs/designer_review_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235422.md)
- [設計統括者Review：Lightning Basic Preview Manual Lifecycle Accepted](history/handoffs/designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Lightning Environment Recovery／Lifecycle Acceptance Evidence](history/operations/lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence_20260727003044.md)
- [実装担当向け Lightning Auto-start Go／No-Go Assessment Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md)
- [実装担当 Lightning Auto-start Go／No-Go Assessment Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727050852.md)
- [設計統括者Review：Lightning Auto-start Go／No-Go Assessment Accepted](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727051659.md)
- [設計統括者訂正Review：Lightning Auto-start Requirement Alignment](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md)
- [実装担当 Stage A Availability Check Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md)
- [実装担当 Stage A Target Correction Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md)
- [設計統括者Review：Stage A Availability／Target Correction Accepted](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_a_availability_and_target_correction_20260727054823.md)
- [実装担当向け Stage B Preparation Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md)
- [実装担当 Stage B Preparation Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md)
- [設計統括者Review：Stage B Preparation Accepted](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727064044.md)
- [Lightning Stage B Manual Trial Preparation／Port 7860](history/operations/lightning_stage_b_manual_trial_preparation_and_port_7860_20260727171551.md)
- [Lightning Stage B Unattended Wake Failure／Private Bootstrap Preparation](history/operations/lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation_20260727182736.md)
- [Lightning Stage B Traffic-aware Auto-start Acceptance](history/operations/lightning_stage_b_traffic_aware_auto_start_acceptance_20260727224609.md)

Auto-start Project-side Read-only Preflight、Lightning Basic Preview Lifecycle、正しい対象に対するStage A Read-only Availability CheckおよびStage B Repository PreparationはAcceptedである。Lightning UI／Platform上のStage B作業はユーザーが手動実施し、実装担当は行わない。その後の実機試験により、Sleeping Studioに対する外部URL AccessだけでのTraffic-aware Wake-up、認証、Model Startup、LLM利用およびIdle Sleepへの再移行を複数回確認し、現在のBasic Preview用途について`GO`とした。

## 2.3 Shared Documentation Operations

- [Current／Shared／Public Stable Historyおよび設計統括者役完全復元 運用確定Record](history/operations/stable_document_history_and_design_governance_recovery_policy_20260727071721.md)
- [Current Index Public Roadmap History Link Correction](history/operations/current_index_public_roadmap_history_link_correction_20260727072019.md)
- [情報保存最優先／累積完全版／設計統括者役専用Handoff 運用確定Record](history/operations/documentation_information_preservation_and_design_governance_handoff_policy_20260727080023.md)
- [Shared任意Category／Roadmap Lifecycle／Phase 2 History Index予約 運用確定Record](history/operations/shared_documentation_category_and_phase_index_history_policy_20260727081459.md)
- [全Stable文書Filename適用範囲 明確化Record](history/operations/stable_filename_scope_clarification_20260727083901.md)

Current、SharedおよびPublicのStable文書は、変更前後の原文を対応する`history/`へ`<stem>_<phase>_<language>_YYYYMMDDHHMMSS.md`形式で完全保存する。原則として各Phase完了後、Phase Backup直前に設計統括者役の完全復元PackageとDocs-only Reconstruction Validationを作成する。

Current Indexは`docs/project/current/history/index/`へ変更前後原文を保存する。Sharedでは`schemas/`、`templates/`、`user_manual/`および`design_governance_handoff/`と対応Historyを正式配置とする。PublicではOverview、Concept、RoadmapごとのHistory Directoryを使用する。

Lossless再整理、Current、Project Continuity、Sharedおよび設計統括者役Handoffは、差分だけでなく累積・自己完結の完全版として更新する。Publicも原則追加式とする。

`shared/schemas/`、`shared/templates/`および`shared/user_manual/`は必要な場合だけ使用する。Docs運用は既存`shared/operations/`、権限管理は既存`shared/task_roles/`へ集約する。Roadmap Stable名は`roadmap_ja.md`のまま維持し、Timestamp付き完全SnapshotはHistoryだけへ保存する。Phase 2以降は各Phaseの`history/index/`をAppend-only Index Snapshot置場として使用する。

TimestampなしStable名の規則はRoadmapだけでなく、Current、Shared、Public、Phase Stable、Phase Compilation、Project Continuity、Design Governance Handoffおよび既存DocsのLossless再整理後正本へ共通適用する。Timestampを付けるのはHistory SnapshotとEvent Artifactだけである。

## 2.4 Documentation Reconstruction

- [Documentation Reconstruction Human-readable Inventory](history/operations/documentation_reconstruction_inventory_20260727093727.md)
- [Documentation Reconstruction Machine-readable Source Manifest](history/operations/documentation_reconstruction_source_inventory_20260727093727.json)
- [Project Continuity／Roadmap First-pass Record](history/operations/documentation_reconstruction_continuity_and_roadmap_first_pass_20260727094639.md)
- [Current Canonical Reconstruction Record](history/operations/current_canonical_reconstruction_20260727101132.md)
- [Phase 1／Phase 1-ex Lossless Reconstruction Record](history/operations/phase_1_and_phase_1_ex_lossless_reconstruction_20260727102850.md)
- [Phase 1-ex Interim Lossless Compilation](lossless/phase_1_ex_interim_lossless_ja.md)
- [Phase 1-ex Interim Lossless Manifest](lossless/phase_1_ex_interim_lossless_manifest.json)
- [Phase 1 Complete Lossless Compilation](../phase_1/lossless/phase_1_lossless_ja.md)
- [Phase 1 Complete Lossless Manifest](../phase_1/lossless/phase_1_lossless_manifest.json)

Documentation再構築のSource Setとして、Docs 493件とDemo画像6件、合計499件をFreezeした。Machine-readable ManifestはPath、File Type、SizeおよびSHA-512を保持し、499／499件の一致を確認済みである。

`project_continuity_master_ja.md`と`roadmap_ja.md`は第1周を完了した。Current Canonical、Phase 1／Phase 1-ex Lossless、Shared、Publicおよび公開Metadata完成後に第2周を行う。

Phase 1-ex Losslessは、Phase完了版ではなく作成時点までのInterim／Current-to-date Compilationとして識別する。Phase 1-ex完了時には、その後の全資料を含めた正式な完了版を再生成する。

Current Canonical 5文書とCurrent Documentation Indexは、更新前後の完全SnapshotをHistoryへ保存したうえで累積再構築した。Current Markdown 7件のRelative Linkは全件存在確認済みである。

Phase 1は316件、Phase 1-exはSource Freeze時点の145件をPhase単位の単一Lossless Compilationへ直接収録した。Compilationから全Sourceを再抽出し、SizeとSHA-512がPhase 1で316／316件、Phase 1-exで145／145件一致した。

Phase 1-ex版は進行中PhaseのInterim／Current-to-date版であり、Phase完了版ではない。Phase 1-ex完了時に後続Sourceを含めて正式完了版を再生成する。

Shared 4正本は更新前後の完全Snapshotを保持したうえで累積再構築した。Docs運用、Role Authority、設計統括者役Recovery、二周方式、英語版再判断、Phase Lossless検証値および公開準備境界を最新状態へ統一した。

Project Continuity MasterとRoadmapの第2周、Overview、Concept、README、Research Preview LICENSE、TERMS_OF_USE、NOTICEおよびCITATION初版を作成した。Stable Corpusの相対Linkは262件中欠落0、旧名義・個人Pathは0件、`.DS_Store`は18件削除後0件、Phase Lossless再抽出およびTest／Static Checkは全て合格した。

最終対象へIndex／Recordを追加した後の再検証では、21 Files・286 Relative Links中欠落0、Demo画像6／6、旧名義・個人Path0、`.DS_Store` 0、CITATION Parse合格を確認した。Documentation Reconstruction初版は`pass`である。

## 2.5 Post-documentation Design Governance Recovery

- [Design Governance Stable Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
- [Interim Current-state Recovery Manifest](../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260727121343.md)
- [README Before Phase Position Refresh](history/operations/readme_before_phase_status_and_recovery_refresh_20260727121225.md)
- [README After Phase Position Refresh](history/operations/readme_after_phase_status_and_recovery_refresh_20260727121343.md)
- [Phase Index Before Recovery Refresh](history/operations/phase_index_before_post_documentation_recovery_refresh_20260727121343.md)

README上部へ現在地`Phase 1-ex / 最終予定 Phase 10`とRoadmap導線を追加した。設計統括者役Stable Handoffは、Documentation Corpus完成・検証後の現在状態、残作業、Lightning URL更新境界および臨時Recovery Manifest規則を累積反映した。

Recovery Manifestは、ユーザーの明示要求に基づくPhase途中の`interim_current_state`である。新しい設計統括者役Taskは旧Task会話へ依存せず、Current Index、Project Continuity Master、Stable Handoff、本Manifest、Phase 1-ex IndexおよびRoadmapから即時復旧できる。Phase 1-ex完了版Recovery Manifest、Final Lossless、ReviewおよびBackupは別途必要である。

## 2.6 Public Concept Governance Kernel Reintegration

- [Public Concept Stable](../../../public/concept_ja.md)
- [Public Concept Before Reintegration](../../../public/history/concept/concept_phase_1_ex_before_governance_kernel_reintegration_ja_20260727123044.md)
- [Public Concept After Reintegration](../../../public/history/concept/concept_phase_1_ex_governance_kernel_reintegration_ja_20260727123238.md)
- [Reintegration Record](history/operations/public_concept_governance_kernel_reintegration_20260727123238.md)
- [Phase Index Before Reintegration](history/operations/phase_index_before_public_concept_reintegration_20260727123238.md)

Public Conceptへ、Governance Definitionの実行可能Component化、共有Control Planeと分散Governance Point、反証可能な実験、存在とAuthorityの分離、AI Lifecycle、External R&D Port、Project運用への先行適用およびPhase 1のCross-environment Runtime契約としての位置付けを累積再統合した。

元Sourceの会話口調、感情的評価、人物・採用文脈、個人・企業・役職等の識別情報および過大な実装済み主張は採用していない。「Kernel」「Hypervisor」「実験OS」は概念的比喩であり、実装済みOperating SystemまたはHardware Hypervisorを意味しない。

## 2.7 README／Overview Document Responsibility Correction

- [README Stable](../../../../README.md)
- [Public Overview Stable](../../../public/overview_ja.md)
- [README Before Correction](history/operations/readme_before_document_responsibility_correction_20260727125332.md)
- [README After Correction](history/operations/readme_after_document_responsibility_correction_20260727125332.md)
- [Overview Before Correction](../../../public/history/overview/overview_phase_1_ex_before_document_responsibility_correction_ja_20260727125332.md)
- [Overview After Correction](../../../public/history/overview/overview_phase_1_ex_document_responsibility_correction_ja_20260727125332.md)
- [Correction Record](history/operations/readme_overview_document_responsibility_correction_20260727125553.md)
- [Phase Index Before Correction](history/operations/phase_index_before_readme_overview_responsibility_correction_20260727125332.md)

READMEへEnvironment、Model配置、Setup、CLI、Server操作、Public Demo運用および未搭載機能の詳細を収録していた文書責務違反を修正した。READMEは59行の最小Project入口とし、Roadmapを現在状態・将来構想の正本として強調する。

Public Overviewは、個別Hardware、Memory、Architecture、Python、Backend、Model Artifactおよび外部環境検証を削除し、23行から237行へ再構築した。Projectの目的、対象問題、位置付け、全体構造、Governance Definition Platform、設計原則、Authority不変条件、比較可能な研究方法、Evidenceおよび現在地を説明する。

## 2.8 README Required Elements／Document Responsibility Rules

- [README Stable](../../../../README.md)
- [Documentation Rules Stable](../../shared/conventions/documentation_rules_ja.md)
- [README Before Restoration](history/operations/readme_before_required_elements_restoration_20260727131258.md)
- [README After Restoration](history/operations/readme_after_required_elements_restoration_20260727131419.md)
- [Documentation Rules Before](../../shared/history/conventions/documentation_rules_phase_1_ex_before_document_responsibility_rules_ja_20260727131258.md)
- [Documentation Rules After](../../shared/history/conventions/documentation_rules_phase_1_ex_after_document_responsibility_rules_ja_20260727131419.md)
- [Change Record](history/operations/readme_required_elements_and_document_responsibility_rules_20260727131445.md)
- [Phase Index Before Change](history/operations/phase_index_before_readme_required_elements_and_responsibility_rules_20260727131434.md)

READMEへ、Projectの中核的特徴、Research Preview／Open Source状態、Model Weight非同梱、第三者Artifact、LLM出力上の注意、無保証、文書変更可能性およびLegal正本への導線を簡潔に戻した。個別環境、操作手順および未搭載機能の詳細は戻していない。

Shared Documentation Rulesへ、README、Overview、Concept、Roadmap、Current Canonical、Phase、OperationsおよびUser Manualの責務、記載必須要素、記載しない詳細、必要な重複、不要な重複およびReview Checklistを正式追加した。

## 2.9 Lightning Stage B Manual Trial Preparation

- [Manual Trial Preparation／Port 7860 Record](history/operations/lightning_stage_b_manual_trial_preparation_and_port_7860_20260727171551.md)
- [Current Index Before Change](../../current/history/index/documentation_index_phase_1_ex_before_lightning_stage_b_manual_trial_preparation_ja_20260727171551.md)
- [Phase Index Before Change](history/operations/phase_index_before_lightning_stage_b_manual_trial_preparation_20260727171551.md)

Lightning上でStage B対象Artifact四件のSHA-512、Permission、Managed Secrets Availability、Stage B追加Test `32 passed`およびPreflightを確認した。

最初のPreflightでは、前回Manual Lifecycleが残した既定Runtime State DirectoryのMode不一致をFail Closedで検出した。対象が正規DirectoryでありSymbolic Linkではないことを確認後、Directoryを`700`、Marker／Logを`600`へ限定修復し、再Preflightで`runtime_state_root`とCredentialを含む必須Checkが合格した。Foreground `run`ではPID Fileを作らないため、`basic-preview.pid`が存在しない状態は正常である。

既存Manual Previewは停止済みで、Listenerなしを確認した。API Builderの確定Application／Listen Portは`7860`とし、`MARGPA_WEB_PORT`も同じ値へ統一した。API Builder発行のPublic URLを別Browserから開き、Studio稼働中のMARGPA利用に合格した。

これはPre-wake Smokeの合格であり、Traffic-aware Auto-startの合格ではない。First／Second Unattended Wake Trialは未実施であり、次はSleeping Studio、Owner Session完全不在、第三者相当Public URL AccessだけによるWakeを確認する。

## 2.10 Lightning Stage B Unattended Wake Failure／Private Bootstrap

- [Failure／Private Bootstrap Preparation Record](history/operations/lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation_20260727182736.md)
- [Current Index Before Change](../../current/history/index/documentation_index_phase_1_ex_before_lightning_stage_b_unattended_wake_failure_and_private_bootstrap_ja_20260727182736.md)
- [Phase Index Before Change](history/operations/phase_index_before_lightning_stage_b_unattended_wake_failure_and_private_bootstrap_20260727182736.md)

First Unattended Wakeでは、Sleeping Studioに対する別BrowserからのAPI Builder URL AccessだけではApplicationが開かなかった。Studio再起動後の観測により、Project／Model等のArtifactと、Terminal Export、Process StateおよびRuntime State Permissionは別のPersistence境界であることを確認した。Managed Secretsは新しいProcessから利用可能だったが、手動設定したPath、Port等のShell Environmentは保持されなかった。

既存Foreground `run`の選択は維持する。追加した方針は、その前段にRepository外Private Bootstrapを置き、固定Environment、Port `7860`、Managed Secrets存在確認、限定Permission修復、安全検査およびForeground Service委譲を一括して行うことである。

Private Bootstrap Source、正確な起動Command、Public URLおよびCredential値は公開Repository／Docsへ保存しない。内部ReviewではRuff、Mypy strict、構文検査、疑似Bootstrap試験3件および既存Lifecycle Unit Test `32 passed`を確認した。Lightning実機への配置、Preflight、Test、Manual RunおよびFirst Wake再試験はユーザー作業待ちであり、Traffic-aware Auto-startは未確認のままである。

## 2.11 Lightning Stage B Traffic-aware Auto-start Acceptance

- [Traffic-aware Auto-start Acceptance Record](history/operations/lightning_stage_b_traffic_aware_auto_start_acceptance_20260727224609.md)
- [Current Index Before Change](../../current/history/index/documentation_index_phase_1_ex_before_lightning_stage_b_traffic_aware_auto_start_acceptance_ja_20260727224609.md)
- [Phase Index Before Change](history/operations/phase_index_before_lightning_stage_b_traffic_aware_auto_start_acceptance_20260727224609.md)
- [Roadmap Before Change](../../../public/history/roadmap/roadmap_phase_1_ex_before_lightning_traffic_aware_auto_start_acceptance_ja_20260727224609.md)

Studio Sleep／RestartによりPrivate BootstrapのModeが`600`から`744`へ変化することを確認した。Permission永続を前提にせず、Private Bootstrap自身がOwner、Symlink、危険なWritable Modeを検査し、安全に限定修復できるModeだけをPrivate Modeへ戻す設計を実機運用へ適用した。

Private Bootstrap経由のPreflight、限定Unit Test `32 passed`、Manual Foreground Startup／Shutdownは合格した。その後、Sleeping Studioに対するPublic URL Accessだけで、Authentication、Model StartupおよびLLM利用まで複数回成立した。

同一URLでManaged Secretsを変更し、旧Credential拒否、新Credential認証およびLLM利用を確認した。Wake／Sleep Cycleを複数回再現し、継続的に起動画面を監視しなくても起動することを確認した。

観測Cold Startは約3～10分、Idle-to-sleepは約10～12分である。一度だけJSONらしき一時応答が表示されたが、再Accessで正常復帰し、再現未確認の低優先度観察事項とする。

現在のLightning Basic Preview用途について、Read-only Preflightは`ACCEPTED`、Auto-start Go／No-Goは`GO`、Traffic-aware External Wakeは`PASS`とする。これはProduction SLA、匿名Public Demoまたは無制限公開の承認ではない。

## 2.12 Phase 1-ex Revised Execution Order

- [実行順変更／Git未使用掲載境界 Record](history/operations/phase_1_ex_revised_execution_order_and_pre_git_publication_boundary_20260727225735.md)

Phase 1-exの残工程順を変更した。ユーザー原文では番号`4`が二度使われていたため、内容と前後関係を変えず10段階へ正規化した。

次工程は、Gitを使用しないGitHub掲載準備と一時掲載である。詳細指示は今後ユーザーから与えられるため、本変更時点ではGit操作、GitHub掲載、Public Demo匿名公開その他の外部変更を行わない。

Git未使用の一時掲載、後段のGit初期化／GitHub公開との対応および初回Commitの関係は、Git運用設計で明示的に確定する。設計統括者役が独自判断で統合、前後入替または省略しない。

## 3. Role／Notification

- [Task Role／Write Authority](../../shared/task_roles/task_role_write_authority_policy_ja.md)
- [Documentation Structure／Task Operations](../../shared/operations/documentation_structure_and_task_operations_ja.md)
- [Design Governance Handoff](../../shared/design_governance_handoff/design_governance_handoff_ja.md)
- [Task Notification Plan](handoffs/documentation_migration_task_notification_plan_ja.md)

## 4. Current Canonical

- [Current Documentation Index](../../current/documentation_index_ja.md)
- [Requirements](../../current/requirements/requirements_specification_ja.md)
- [System Architecture](../../current/architecture/system_architecture_ja.md)
- [Technology Selection](../../current/architecture/technology_selection_ja.md)
- [Basic Design](../../current/architecture/basic_design_ja.md)
- [Runtime Governance](../../current/governance/runtime_governance_specification_ja.md)
- [Project Continuity Master](../../current/project_continuity/project_continuity_master_ja.md)

## 5. Phase 1

- [Phase 1 Index](../phase_1/phase_index_ja.md)

## 6. Remaining Phase 1-ex Scope

1. Git未使用のGitHub掲載準備／一時掲載。詳細はユーザーの後続指示待ち。
2. Basic認証Previewと分離したPublic Demo基盤実装、匿名公開前最終確認、合格後の匿名公開有効化。
3. Local Mac簡易Documentation RAG＋External Hook。
4. Git運用設計。Branch／Tag／Commit、Author／Email、Remote／公開Repository、Backup対応を確定する。
5. Git初期化／公開Sanitation。`.gitignore`、`.gitattributes`、除外、Privacy Scan、LICENSE方針、初回Commit直前準備およびユーザー原文上のGitHub公開を含む。初回Commitはまだ作らない。
6. 必要なDocsだけを再整理・新規作成し、Phase 1-ex Final LosslessとDesign Governance Recovery情報を更新する。
7. 全体Review／Test／Privacy Scanを行う。
8. ユーザーの明示許可後に初回Commitを作成する。
9. Phase 1-ex完了条件とUser Acceptance後にPhase 1-ex Backupを取得する。
10. Phase 1-ex完了・Phase 2着手可能宣言後にPhase 2へ進む。

英語版は今回の日本語正本再構築には含めない。Phase 1-ex後半で、日本語正本と同粒度の派生版を作成するか再判断する。

匿名Public Accessは、Public Demo基盤、Rate Limit、Token上限、Cost／Resource保護、Tool／RAG／外部操作遮断、Basic認証Previewとの分離および最終確認に合格した後、ユーザーの明示判断で有効化する。

Stage 1のGit未使用掲載、Stage 5のGitHub公開との対応およびStage 8の初回Commitの正確な関係は、Stage 4で未解決事項として確定する。順序上の曖昧さを設計統括者役の推測で解消しない。

## 7. History

Phase 1-ex開始時の旧Index、Role Transition、Migration Control EventおよびMigration前Stable Source 8件の原文は`history/`へ保持する。旧Root重複配置は全原文のSHA-512一致確認後に退役済みである。

- [Current／Public JA／EN同等粒度決定](history/requirements/current_public_ja_en_equivalent_granularity_decision_20260726180711.md)
- [Phase Index Append-only History Repair](history/operations/phase_index_append_only_history_repair_20260726202935.md)
- [Append-only／User Authority Governance Freeze](history/operations/append_only_and_user_authority_governance_freeze_20260726203948.md)
- [Lifecycle Safety Follow-up Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_lifecycle_safety_follow_up_20260726213429.md)
- [Lightning Manual Environment／Preflight Evidence](history/operations/lightning_manual_environment_and_preflight_evidence_20260726233910.md)
- [Linux `/proc` Test Fixture Follow-up Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726233910.md)
- [Linux `/proc` Test Fixture Follow-up Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_linux_proc_test_fixture_follow_up_20260726235422.md)
- [Lightning Basic Preview Manual Lifecycle Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance_20260727002440.md)
- [Lightning Environment Recovery／Lifecycle Acceptance Evidence](history/operations/lightning_basic_preview_environment_recovery_and_lifecycle_acceptance_evidence_20260727003044.md)
- [Lightning Auto-start Go／No-Go Assessment Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727003044.md)
- [Lightning Auto-start Go／No-Go Assessment Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727050852.md)
- [Lightning Auto-start Go／No-Go Assessment Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727051659.md)
- [Lightning Auto-start Requirement Alignment Correction Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction_20260727052747.md)
- [Stage A Availability Check Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_availability_check_20260727053757.md)
- [Stage A Target Correction Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_a_target_correction_20260727054456.md)
- [Stage A Availability／Target Correction Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_a_availability_and_target_correction_20260727054823.md)
- [Stage B Preparation Handoff](history/handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md)
- [Stage B Preparation Status](history/handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md)
- [Stage B Preparation Accepted Review](history/handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727064044.md)
- [Stable History／Design Governance Recovery Policy](history/operations/stable_document_history_and_design_governance_recovery_policy_20260727071721.md)
- [Current Index Public Roadmap History Link Correction](history/operations/current_index_public_roadmap_history_link_correction_20260727072019.md)
- [Information Preservation／Design Governance Handoff Policy](history/operations/documentation_information_preservation_and_design_governance_handoff_policy_20260727080023.md)
- [Shared Documentation Category／Phase Index History Policy](history/operations/shared_documentation_category_and_phase_index_history_policy_20260727081459.md)
- [Stable Filename Scope Clarification](history/operations/stable_filename_scope_clarification_20260727083901.md)
- [Documentation Reconstruction Inventory](history/operations/documentation_reconstruction_inventory_20260727093727.md)
- [Documentation Reconstruction Source Manifest](history/operations/documentation_reconstruction_source_inventory_20260727093727.json)
- [Project Continuity／Roadmap First Pass](history/operations/documentation_reconstruction_continuity_and_roadmap_first_pass_20260727094639.md)
- [Current Canonical Reconstruction](history/operations/current_canonical_reconstruction_20260727101132.md)
- [Phase 1／Phase 1-ex Lossless Reconstruction](history/operations/phase_1_and_phase_1_ex_lossless_reconstruction_20260727102850.md)
- [Shared Documentation Reconstruction](history/operations/shared_documentation_reconstruction_20260727104505.md)
- [Public／Canonical／Legal Documentation Reconstruction](history/operations/public_canonical_and_legal_documentation_reconstruction_20260727110347.md)
- [Documentation Reconstruction Final Validation](history/operations/documentation_reconstruction_final_validation_20260727110834.md)
- [Post-documentation Interim Design Governance Recovery Manifest](../../shared/history/design_governance_handoff/design_governance_recovery_manifest_20260727121343.md)
- [Post-documentation Design Governance Recovery Refresh](history/operations/post_documentation_design_governance_recovery_refresh_20260727121814.md)
- [Public Concept Governance Kernel Reintegration](history/operations/public_concept_governance_kernel_reintegration_20260727123238.md)
- [README／Overview Document Responsibility Correction](history/operations/readme_overview_document_responsibility_correction_20260727125553.md)
- [README Required Elements／Document Responsibility Rules](history/operations/readme_required_elements_and_document_responsibility_rules_20260727131445.md)
- [Lightning Stage B Unattended Wake Failure／Private Bootstrap Preparation](history/operations/lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation_20260727182736.md)
- [Lightning Stage B Traffic-aware Auto-start Acceptance](history/operations/lightning_stage_b_traffic_aware_auto_start_acceptance_20260727224609.md)
- [Phase 1-ex Revised Execution Order／Pre-Git Publication Boundary](history/operations/phase_1_ex_revised_execution_order_and_pre_git_publication_boundary_20260727225735.md)

### 7.1 Index Snapshot Chain

- [2026-07-26 15:40:09](history/documentation_index_20260726154009.md)
- [2026-07-26 17:00:34](history/documentation_index_20260726170034.md)
- [2026-07-26 17:53:18](history/documentation_index_20260726175318.md)
- [2026-07-26 18:07:11](history/documentation_index_20260726180711.md)
- [2026-07-26 19:29:12](history/documentation_index_20260726192912.md)
- [2026-07-26 19:49:49](history/documentation_index_20260726194949.md)
- [2026-07-26 20:20:36](history/documentation_index_20260726202036.md)
- [2026-07-26 20:29:35](history/documentation_index_20260726202935.md)
- [2026-07-26 20:39:48](history/documentation_index_20260726203948.md)
- [2026-07-26 21:34:29](history/documentation_index_20260726213429.md)
- [2026-07-26 23:39:10](history/documentation_index_20260726233910.md)
- [2026-07-26 23:54:22](history/documentation_index_20260726235422.md)
- [2026-07-27 00:24:40](history/documentation_index_20260727002440.md)
- [2026-07-27 00:30:44](history/documentation_index_20260727003044.md)
- [2026-07-27 05:16:59](history/documentation_index_20260727051659.md)
- [2026-07-27 05:27:47](history/documentation_index_20260727052747.md)
- [2026-07-27 05:48:23](history/documentation_index_20260727054823.md)
- [2026-07-27 05:56:25](history/documentation_index_20260727055625.md)
- [2026-07-27 06:40:44](history/documentation_index_20260727064044.md)
- [2026-07-27 07:17:21](history/documentation_index_20260727071721.md)
- [2026-07-27 07:20:19](history/documentation_index_20260727072019.md)
- [2026-07-27 08:00:23](history/documentation_index_20260727080023.md)
- [2026-07-27 08:14:59](history/documentation_index_20260727081459.md)
- [2026-07-27 08:39:01](history/documentation_index_20260727083901.md)
- [2026-07-27 09:46:39](history/documentation_index_20260727094639.md)
- [2026-07-27 10:11:32](history/documentation_index_20260727101132.md)
- [2026-07-27 10:30:27](history/documentation_index_20260727103027.md)
- [2026-07-27 10:47:19](history/documentation_index_20260727104719.md)
- [2026-07-27 11:07:15](history/documentation_index_20260727110715.md)
- [2026-07-27 11:09:50](history/documentation_index_20260727110950.md)
- [2026-07-27 12:19:47](history/documentation_index_20260727121947.md)
- [2026-07-27 12:35:53](history/documentation_index_20260727123553.md)
- [2026-07-27 12:58:34](history/documentation_index_20260727125834.md)
- [2026-07-27 13:18:30](history/documentation_index_20260727131830.md)
- [2026-07-27 17:18:45](history/documentation_index_20260727171845.md)
- [2026-07-27 18:27:36](history/documentation_index_20260727182736.md)
- [2026-07-27 22:46:09](history/documentation_index_20260727224609.md)
- [2026-07-27 22:57:35](history/documentation_index_20260727225735.md)
