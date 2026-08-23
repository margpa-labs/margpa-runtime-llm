# Phase 6 Judge／Evaluation／Repair／Observability 統合Architecture

    document_id: phase_6_architecture
    status: accepted_frozen_not_activated
    phase: phase_6
    language: ja
    recorded_at: 2026-08-22 21:13:08 JST
    implementation_authorized: false

## 1. System Flow

    User Input
      → Phase 5 guardrail.input
      → Phase 5 guardrail.context_source
      → Phase 4 main_model.pre
      → Current Main Model Generation
      → Phase 5 guardrail.stream_candidate
      → Phase 4 main_model.post
      → Phase 5 guardrail.output_candidate
      → Canonical Candidate
      → Phase 6 Judge
      → Repair Eligibility／Authority／Budget
          ├─ no repair → Accepted Candidate
          └─ bounded repair
               → New Repair Attempt
               → Phase 4／5全Point再通過
               → Independent Re-evaluation
               → Accepted／Rejected／Failed
      → Durable Commit
      → completed／rejected／failed SSE

各段階はRuntime Eventを発行し、Observability ProjectionはEventを購読する。Status表示を推論経路の正本にしない。

## 2. Component Boundary

候補境界：

    modules/runtime_model_control/
      domain／application／ports／public

    adapters/runtime_model_control/
      llama_cpp／artifact_provenance

    modules/evaluation/
      domain／application／ports／public

    adapters/evaluation/
      deterministic／llm_judge／dataset

    modules/repair/
      domain／application／ports／public

    adapters/repair/
      registered_actions

    modules/runtime_observability/
      domain／projection／recording／ports

    bootstrap/
      runtime_model_control
      evaluation
      repair
      runtime_observability

    web/
      typed status／configuration／feedback／recording routes

実FileはPhase 6-0でAs-builtと既存Packageを確認して動的に解決する。本図を固定Directory量産命令にしない。

## 3. Runtime Model Manager

### 3.1 Canonical Snapshot

    RuntimeModelSnapshot
      revision
      selected_model_key
      role_bindings
      artifact_identity／digest
      backend_identity
      runtime_state
      loaded_context_size
      model_native_context_limit
      backend_context_limit
      deployment_verified_context_limit
      max_output_token_limit
      current_max_new_tokens
      last_transition_receipt

Browser、Sidebar、Advanced SettingsおよびJudge／Repairは同じServer Snapshotを参照する。

### 3.2 Switch Transaction

    Preview
      → Candidate Definition／Artifact／Backend検証
      → Runtime Revision／Digest CAS
      → Active Generation 0確認
      → Previous Runtime Receipt保持
      → Unload
      → Candidate Load
      → Capability実測照合
      → Atomic Current Commit
      → UI／Generation Binding更新

Load失敗時はPrevious ReceiptからRollbackする。Rollback失敗時はCurrentを不明な旧値へ戻さずUnavailableとしてGenerationを拒否する。

### 3.3 Main／Judge Role Binding

Model ArtifactとRuntime Roleを分離する。

    RoleBinding
      role: main | judge | guard
      model_identity
      artifact_digest
      backend_identity
      binding_state
      independence_class
      capability_digest

同一ArtifactをMain／JudgeへBindingできるが、Judge Independenceはshared_artifactとして低いことを表示する。独立Judge AdapterがUnavailableの場合もNoneまたはUnavailableを正確に表示する。

Roadmap上のSelene-1-Mini-Llama-3.1-8Bは独立Judge Adapter候補としてPort／Registry上の差替え余地を保持する。ただしExact Artifactが存在しない状態でCurrent、AvailableまたはLoadedを捏造しない。

## 4. DeepSeek Derived Artifact

Official SnapshotをCanonical、GGUF Q4_K_MをDerivedとする。

    models/main/deepseek-r1-0528-qwen3-8b/
      huggingface/     Canonical Snapshot
      gguf/            Derived Artifact
      manifests/       Provenance／Digest／Recipe

ManifestはUpstream Repository／Full Commit、Source Manifest Digest、Conversion Tool Revision、Recipe、Quantization、Tokenizer／Template、Output Size／SHA-512、License、Backend CompatibilityおよびMac Acceptanceを持つ。

CoreはこのPathやModel名を知らず、Model Definition／Registry／Manifestが解決する。Qwen Artifact、DeepSeek Canonical WeightおよびV4 Weightを上書きしない。

modelsがSymbolic Linkの場合はLogical PathとResolved Physical Pathを別Identityとして記録する。Containment CheckはLogical Prefixだけで通さず、Activation Receiptに記録されたExact Resolved Target／Subtreeと照合する。以前のDownload作業で認められた例外は別Execution CycleのAuthorityであり、自動再利用しない。

## 5. Dynamic Generation Control

### 5.1 Context Reload

    ContextChangePreview
      → effective max導出
      → CAS／Idle Gate
      → Same ModelをRequested ContextでReload
      → loaded_context_size実測
      → CommitまたはRollback

Server Process、Conversation ServiceおよびWeb Sessionは維持する。Reload中は新Generationを受け付けず、既存Conversationを削除しない。

### 5.2 Max New Tokens

    configured_limit
      <= min(model_output_limit, backend_output_limit)

    request_limit
      <= min(
           configured_limit,
           loaded_context_size
             - exact_prompt_tokens
             - governance_reserved_tokens
             - safety_reserved_tokens
         )

Max New Tokens変更はAtomic Runtime Overrideとして次Generationから使用する。Context Size変更時に再検証し、値が新上限を超える場合はSilent Clampせず明示的な再設定要求またはSafe Invalid Stateへする。

## 6. Evaluation Domain

### 6.1 Identity

    EvaluationDataset
      dataset_id／revision／digest／source_class

    EvaluationCase
      case_id／input／reference／criteria／language／tags

    EvaluationRun
      run_id／request／turn／attempt refs
      dataset／case／criteria refs
      evaluator_binding
      mode／config／seed／budget

    EvaluationResult
      dimension_results
      confidence／calibration
      unsupported_claims／contradictions
      recommendation
      evidence_refs
      token／latency／call／cost
      execution_state／failure

Reference本文をRuntime Evidenceへ無差別複製せず、必要範囲のDigest／Source Referenceを持つ。Tracked Evaluation FixtureとUser Runtime Resultを分離する。

### 6.2 Judge Pipeline

    Criteria Resolver
      → Deterministic Evaluators
      → optional LLM Judge
      → Calibration／Bias Metadata
      → Conflict Resolver
      → Judge Recommendation

DeterministicとLLM Resultを固定多数決で潰さない。Reference有無、Confidence、Evaluator Independence、Failure、Criteria適用範囲およびAuthorityを保持したままAction Resolverへ渡す。

### 6.3 Mode

Judge Mode：

- OFF：Judge Adapter／Dataset／Result Call 0。
- OBSERVE：評価するがCandidate、Stream、Persistenceを変更しない。
- ENFORCE：RecommendationをRepair Eligibilityへ渡せるが、Judge自身はRepairを実行しない。

## 7. Repair Domain

### 7.1 Repair Plan

    RepairPlan
      repair_plan_id
      trigger_result_refs
      strategy_id
      target_attempt_ref
      authority／policy refs
      budget
      success_criteria
      state

初期Strategy候補：

- regenerate_with_structured_feedback
- abstain_when_reference_insufficient
- request_clarification
- format_only_repair

実行可能StrategyはAdapter RegistryとAuthorityで決める。名称だけをCoreへ分岐Hard-codeしない。

### 7.2 State Machine

    planned
      → authorized
      → generating_repair
      → rejudging
      → accepted | rejected | exhausted | failed | cancelled

Original Attemptを書き換えない。Repair Candidateは新Attemptとして生成し、成功時だけPresented Answerへ採用する。

### 7.3 Budget

    RepairBudget
      max_attempts
      max_wall_time_ms
      max_additional_tokens
      max_total_model_calls
      max_depth
      deadline

各遷移で残Budgetを再計算する。Timeout／Cancel／Guardrail Reject／Authority Loss／Model Switch要求は安全なTerminalへ収束する。

## 8. Terminal／Persistence Ordering

    Candidate
      → Main Governance post
      → Guardrail output
      → Judge
      → optional Repair and Rejudge
      → Final Guardrail／Authority check
      → Canonical Presented Answer決定
      → Conversation Atomic Commit
      → completed SSE

Guardrail拒否はModel Call 0のrejected Terminalとする。UI向け定型文はPresentation Projectionであり、Assistant Model MessageとしてGeneration Contextへ保存しない。Reload時はTyped Reject Codeから再構築する。

Commit前にcompletedを送らない。Commit後の通信断は既存Detail再読へ収束する。

## 9. Request-correlated Observability

### 9.1 Event Envelope

    RuntimeEvent
      event_id
      request_id
      conversation_id／turn_id
      generation_attempt_id
      evaluation_run_id
      repair_attempt_id
      component_role／point_id
      state
      timestamp
      safe_payload
      config／artifact／definition refs

全IDが常に存在する必要はないが、存在しない理由をTyped Stateで表す。

### 9.2 Current Projection

Status APIはCurrent Request SnapshotとHistorical Latest-per-Pointを分離する。Current Requestで呼ばれていないoutput_candidate／stream_candidateを前回値で埋めない。

    Current Request
      input              evaluated
      context_source     not_invoked_current_request
      stream_candidate   not_invoked_current_request
      output_candidate   not_invoked_current_request

History表示を追加する場合もRequest IDとTimestampを明示する。

### 9.3 User-visible Status

    idle
      → preparing
      → guarding
      → generating
      → judging
      → repairing
      → rejudging
      → completed | rejected | cancelled | failed | degraded

内部StateとUI文言を同一Enumに固定せず、安全なProjection Mapperを使う。

## 10. Recording Architecture

既存runtime_data論理Rootを使用し、新たな大きな別Rootを作らない。

    runtime_data/persistent/<scope>/
      evaluations/
      experiments/
      evidence/
      feedback/

    runtime_data/derived/<scope>/
      evaluation_projections/

    runtime_data/recovery/
      checkpoints／migrations

Recording Mode：

- OFF：Recorder Build／Call／Write 0。
- METADATA：Safe EnvelopeとDigest／Metricのみ。
- FULL：許可されたCanonical Input／Presented Answer／Typed Resultを保存。

FULLでもProtected Capture対象を保存しない。Private Local ResultはGit対象外とし、公開可能Artifactは明示的なSanitize／Export／Manifest Gateを通す。

## 11. UI Architecture

### 11.1 Advanced Settings

AI Components：

    Current Main Model
    Current Guardrail Model
    Current LLM-as-a-Judge Model
    Current Governance Layer

Generation：

    Context Size Current／Limits／Reload State
    Max New Tokens Current／Limits／Request Availability

Governance：

    Main Runtime Governance
    Guardrail Governance
    Judge
    Repair
    Recording

利用者向けLabelへPhase番号を付けない。Phase情報はDocs／Roadmap／Evidenceに保持する。

### 11.2 Legacy Phase 3 Panel

Phase 3のDefinition／Manifest／Compiler／ProviderはPhase 4以降の内部基盤として保持する。Phase 3専用Mode Panelと利用者向けPhase番号表示は廃止／非表示とし、Current Governance LayerのIdentity表示へ統合する。既存CLI／APIの互換削除はPhase 6実装時に影響を確認し、必要ならDeprecated Internal Surfaceとして残す。

### 11.3 Safe Refusal

    Internal: guardrail_reject_input
      → Safe Presentation Mapper
      → JA: その依頼には対応できません。別の安全な内容であればお手伝いできます。
      → EN: I cannot help with that request. I can help with a safer alternative.

Raw CodeはDeveloper DetailにSafe Reasonとして表示可能だが、通常Chat本文へErrorとして露出しない。

## 12. Failure／Concurrency

- Model Switch、Context Reload、Generation、JudgeおよびRepairは互いのLease／Busy Stateを検証する。
- Cancel vs Complete vs Reject vs Repair AcceptはTerminal一件だけが勝つ。
- Multi-tab ApplyはRevision／Digest CASで競合を返す。
- Judge／Recorder／Status Subscriber FailureをMain Model成功へ混ぜない。
- Cache KeyへModel／Artifact／Backend／Context／Config／Definition／Judge／Rubric／Mode Digestを含める。
- Unknown Version、Digest mismatch、Malformed Result、Stale AuthorityまたはBudget不整合はFail-closedする。

## 13. Phase 7 Seam

Phase 6はEvaluation／Judge／Repair Portを成立させるが、現行Lexical RAGの最終品質判定をFreezeしない。Phase 7でEmbedding、Index、Retriever、Corpus LifecycleおよびRAG Governanceを更新した後、Source Relevance、Citation Faithfulness、Unsupported ClaimおよびPrompt Injectionを同じEvaluation Portへ接続する。
