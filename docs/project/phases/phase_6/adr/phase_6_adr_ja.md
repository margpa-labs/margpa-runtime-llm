# Phase 6 ADR — Judge／Evaluation／Repair／Observability統合

    document_id: phase_6_adr
    status: accepted_frozen_not_activated
    phase: phase_6
    language: ja
    recorded_at: 2026-08-22 21:13:08 JST
    implementation_authorized: false

## ADR-6-001：Phase 6をRuntime Governance MVP v1統合境界とする

Phase 4 Main Governance、Phase 5 Guardrail／Authority、Phase 6 Judge／Repair／Observabilityを統合し、Phase 6完了時にPhase 4〜6 Programを本格Closureする。

## ADR-6-002：Judgeは独立ResultでありAuthorityではない

JudgeはEvaluation Result、Confidence、Bias／CalibrationおよびRecommendationを返す。Safety Deny、Authority Deny、Human Approval、Tool PermissionまたはCanonical Completionを単独決定しない。

## ADR-6-003：Deterministic Judgeを正式Baselineとする

LLM JudgeがUnavailableでもEvaluation Contractを成立させる。LLM Judgeは補助Evaluatorであり、Unknown／Malformed／Timeout／Low ConfidenceをPassへ変換しない。

## ADR-6-004：同一Modelの自己評価を独立Judgeと偽装しない

MainとJudgeが同一Artifactの場合もRole Identityを分離し、shared_artifact／self_preference_riskを記録する。独立Artifactがないことを隠さない。

## ADR-6-005：Repairは別Mode、別Authority、別Budgetとする

Judge ENFORCEはRepair候補をResolverへ渡せるだけとし、Repair Mode／Authority／Budgetが別途成立した場合だけRepairを実行する。

## ADR-6-006：Repairは新AttemptでありOriginalを書き換えない

Original Result、Repair Candidate、Re-evaluationおよびPresented Answerを別Identityにする。Repair失敗や悪化を成功として隠さない。

## ADR-6-007：初期Repairは有界一回をStandard候補とする

初期Profileは一回のRepairと一回の再評価を候補とする。ただし値はProfile／Capabilityで管理し、Coreへ永続的な固定上限として埋め込まない。

## ADR-6-008：DeepSeekは交換可能Candidate、QwenはStartup Default

DeepSeek-R1-0528-Qwen3-8B Q4_K_MをLocal Candidateとして統合するが、Startup DefaultはQwen3-4Bのままとする。DeepSeek失敗をPhase 6全体の失敗へ自動昇格せず、Safe UnsupportedでもModel-neutral Coreを継続する。

## ADR-6-009：Model SwitchはServer継続・Model Runtime Transaction

Web Serverを再起動せず、Idle Gate、Unload／Load、Capability照合、Atomic CommitおよびRollbackでModelを切り替える。同時常駐を初期必須にしない。

## ADR-6-010：Context SizeとMax New Tokensを分離する

Context SizeはModel内部Reloadを伴い得る。Max New TokensはReloadせず次Generationへ適用する。両者の上限はCurrent Capabilityから動的に導出しSilent Clampしない。

## ADR-6-011：StatusはRequest相関を正本とする

Pointごとの最終値をCurrent Requestの結果として表示しない。Request／Turn／Generation／Evaluation／Repair Identityで相関し、未実行Pointを明示する。

## ADR-6-012：Guardrail拒否は安全なPresentationへ変換する

内部Typed CodeとModel Call 0を維持しながら、通常UIでは言語別の安全な定型拒否を表示する。Model回答またはConversation Context上のAssistant Authorityとして偽装しない。

## ADR-6-013：Feature ModeとRecording Modeを直交させる

Judge／RepairのOFF／OBSERVE／ENFORCEと、RecordingのOFF／METADATA／FULLを独立させる。全てDefault OFFとし、FULLでもProtected Capture対象を保存しない。

## ADR-6-014：Runtime Dataは既存Rootへ分離保存し、Gitへ含めない

Evaluation／Experiment／Feedback／Evidenceは既存runtime_dataのScope別領域へ保存する。個人・研究Runを通常Stage対象にせず、公開は別Sanitize／Export Gateとする。

## ADR-6-015：利用者向け機能名へPhase番号を付けない

Main Runtime Governance（Phase 4）、Guardrail Governance（Phase 5）等のPhase番号Suffixを削除する。将来の利用者向け機能名にも原則付けず、開発履歴はRoadmap／Docs／Evidenceで管理する。

## ADR-6-016：Phase 3 UIを整理し内部基盤を保持する

Phase 3専用設定Panelは通常利用者向けSurfaceから廃止／非表示とする。一方、Definition Manifest／Provider／Compiler／IR等の内部基盤はPhase 4以降が利用するため削除しない。

## ADR-6-017：Advanced Identityは実Bindingから投影する

Current Main Model、Current Guardrail Model、Current LLM-as-a-Judge ModelおよびCurrent Governance LayerはServer Canonical Snapshotから表示する。Requested CandidateやDirectory存在をCurrentへ昇格しない。

## ADR-6-018：MARGPA ConstitutionはPhase 8へ分離する

Current Constitution Layer、constitution Root、Constitution OFF／OBSERVE／ENFORCEおよびAgent／Tool統治はPhase 8の責務とする。Governance DefinitionsとConstitutionを同一Componentにしない。

## ADR-6-019：RAG品質の最終定性評価はPhase 7後に行う

Phase 6では現行RAGの機能互換Smokeだけを維持する。Full RAGを変更するPhase 7完了後に、回答精度、Citation Faithfulness、Retrieval Relevance、HallucinationおよびGovernance介入を最終評価する。

## ADR-6-020：Public／Basic／Lightning／AWSは自動Bindingしない

Phase 6 Local機能の存在を外部Surfaceの安全性または提供完了とみなさない。DeploymentはPhase 10以降の独立Gateとする。

## ADR-6-021：ClaudeはPhase 6-I COMPLETE_CANDIDATEで停止する

Claude側設計統括者役はPhase 6-0〜6-Iを連結実行できるが、Phase 6-J、Git、Phase 7、AWS／Lightningへ自動進行しない。

## ADR-6-022：Phase 6 Closureは軽量化しない

Phase 6-JではPhase 4〜6 ProgramのFull Review、User Acceptance、Lossless Compilation／Manifest、Roadmap／Current更新、Backup、Phase 7 READYおよび許可済みGit反映を行う。Phase 4／5の最小Closureを統合回収する。
