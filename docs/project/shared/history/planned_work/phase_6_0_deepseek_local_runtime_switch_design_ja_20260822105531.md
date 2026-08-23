# Phase 6-0 DeepSeek Local Runtime Switch／Dynamic Token Control 設計予約

```yaml
document_id: phase_6_0_deepseek_local_runtime_switch_design_20260822105531
status: planned_not_started_not_authorized
document_type: append_only_planned_work
target_phase: phase_6_0_before_judge_repair_freeze
recorded_at: 2026-08-22 10:55:31 JST
owner_role: プロジェクト責任者兼設計統括者役
implementation_authorized: false
model_load_authorized: false
git_mutation_authorized: false
```

## 1. Purpose

Phase 6のJudge／Repair実装へ入る前に、Mac Local RuntimeでCurrent QwenとDeepSeek Practical FallbackをServer Process再起動なしで切り替えられる境界を成立させる。

本Gateは、Phase 4で別Model Gateへ延期されたDeepSeek Local Feasibility／Integrationを回収する。Phase 4～10のCoreをDeepSeek固有化するためではなく、同じModel Port、Governance、Guardrail、Judge、Repair、RAGおよびConversation Contractが複数Modelで成立することを早期に実証する。

```text
Target Model Gate
  Current Baseline : Qwen3-4B GGUF Q4_K_M
  Local Candidate  : DeepSeek-R1-0528-Qwen3-8B Derived Q4
  Server Candidate : DeepSeek-V4-Flash-0731（Local対象外、後続Server Gate）
```

## 2. User Decisions Preserved

1. 起動時Default ModelはCurrent Qwen3-4Bのままとする。
2. DeepSeek-R1-0528-Qwen3-8Bは、公式SafetensorsからProvenanceを追跡できるDerived Q4 ArtifactをLocal候補とする。
3. QwenとDeepSeekはWeb Serverを再起動せず、Runtime中に切り替え可能にする。
4. Current ModelはSidebarとAdvanced Settingsの双方へ表示し、Server側Canonical Stateへ追随させる。
5. `context_size`と`max_new_tokens`はAdvanced Settingsで現在値と上限を確認できるようにする。
6. 両設定は固定値へHard-codeせず、Current Model、Artifact、Backend、Deployment Profileおよび実Runtime Capabilityから上限を解決する。
7. `context_size`はWeb Serverを再起動せず変更可能にする。ただしBackend上必要なModel内部Reloadは許容する。
8. `max_new_tokens`はModel ReloadなしでRuntime中に変更し、次Generationから反映する。
9. Phase 6以降はDeepSeek前提へ固定せず、Qwen／DeepSeekの同一Contract比較を維持する。

## 3. Current As-built／Evidence Class

### 3.1 Repository-verified

- `models/main/qwen3-4b/gguf/`がCurrent Qwen Artifact経路として存在する。
- `models/main/deepseek-r1-0528-qwen3-8b/huggingface/`が存在する。
- `models/main/deepseek-v4-flash-0731/huggingface/`が存在する。
- `config/application.toml`のCurrent Selectionは`main.qwen3-4b-q4-k-m`である。
- `config/models/`にDeepSeek Runtime Model Definitionはまだ存在しない。
- Current BackendはQwen用llama.cpp／GGUF経路であり、DeepSeek Safetensorsをそのまま選択する経路は未実装である。
- Mac Deployment ProfileのCurrent `context_size`は`8192`である。
- Application Generation DefaultのCurrent `max_new_tokens`は`2048`である。
- Current Configuration Controlでは`selected_model`と`context_size`がRestart-required、`max_new_tokens`がRead-onlyとして投影される。

### 3.2 Prior cross-task report／independent revalidation required

先行Download Taskは次を報告したが、本書作成Cycleでは全Weight Digestを独立再計算していない。Phase 6-0 EntryでManifest、Exact RevisionおよびArtifact Integrityを再検証する。

```text
DeepSeek-R1-0528-Qwen3-8B
  Official Commit : 6e8885a6ff5c1dc5201574c8fd700323f23c25fa
  Reported Size   : 16,388,927,770 bytes
  Reported State  : official snapshot downloaded／remote manifest pass

DeepSeek-V4-Flash-0731
  Official Commit : 7872f01b1d1fe23eabc4c98b48bffcef5a386062
  Reported Size   : 166,898,661,074 bytes
  Reported State  : official snapshot downloaded／remote manifest pass
```

Download済みという報告は、Load、Mac Compatibility、Quantization、Quality、Runtime RegistrationまたはCurrent Promotionを意味しない。

## 4. Runtime Model Selection Contract

### 4.1 Canonical State

Runtime Model Manager／Switch CoordinatorをModel PortとWeb／Configuration Controlの間に設け、次をCanonical Stateとして管理する。

```text
selected_model_key
artifact_identity／artifact_digest
backend_key／backend_runtime_identity
loaded_context_size
model_native_context_limit
backend_context_limit
deployment_verified_context_limit
model_max_output_tokens
runtime_state
last_transition_receipt
```

Browser Local State、DOM選択値またはTracked TOMLの書換えをCurrent Runtimeの正本にしない。Settings再Open、Browser ReloadおよびSidebar再描画では、Server側Current Snapshotを再取得する。

### 4.2 Startup Default

- Server Process起動時Defaultは`main.qwen3-4b-q4-k-m`とする。
- Runtime中のModel切替はProcess-localとする。
- Server再起動後も前回選択を自動復元する永続化は、本Gateでは行わない。
- 将来Persistent Selectionを導入する場合は、Secret、Config Source、RollbackおよびCorrupt Stateを別Gateで定義する。

### 4.3 Switch Transaction

```text
Preview／Capability Check
  → Generation Idle確認
  → Previous Runtime Receipt保持
  → Current Modelを安全にUnload
  → Candidate Modelを指定ContextでLoad
  → Artifact／Backend／Capabilityを実測照合
  → Atomic Current Selection Commit
  → Sidebar／Advanced SettingsへCanonical Snapshot反映
```

- Active Generation中のModel／Context切替は拒否する。Silent Cancel、途中から別Modelへ継続またはPartial Outputの混在は禁止する。
- 初期版ではQwenとDeepSeekを同時常駐させることを必須にしない。
- Candidate Load失敗時はPrevious Model／ContextへRollbackを試行する。
- Rollback成功時はPrevious StateをCurrentとして復元し、失敗理由をSafe Typed Statusへ出す。
- Rollbackも失敗した場合は`model_unavailable`へFail-closedし、成功表示、旧Model表示またはGeneration受付を行わない。
- UIはLoad開始時ではなく、成功Receipt確定後にCurrent Modelを更新する。

### 4.4 Conversation／Evidence

- Model切替でConversation、Turn、Message、RAG Citation、Selected BranchおよびGovernance Stateを削除しない。
- 新しいGenerationだけが新Current Modelを使用する。
- 各Generation Attempt／Turnへ実際に使用したModel Key、Artifact Digest、Backend Identity、Context SizeおよびGeneration Configを記録する。
- 過去TurnをCurrent Model名へ書き換えない。
- Same Conversation内でModelが変わっても、Context ProjectionはCanonical Messageを使い、過去Assistant OutputをAuthorityへ昇格しない。

## 5. DeepSeek Local Q4 Artifact Contract

### 5.1 Canonical／Derived Separation

公式SafetensorsをCanonical Source、Q4 GGUF等をDerived Artifactとして分離する。

Derived Manifestには最低限次を含める。

```text
upstream_repository
upstream_full_commit_sha
upstream_manifest_digest
conversion_tool／exact revision
conversion recipe／parameters
quantization scheme
source／output format
output file size／SHA-512
tokenizer／chat template provenance
license review
Mac architecture／Backend version
quality delta／correctness smoke
```

### 5.2 Initial Candidate

- Initial Local CandidateはQ4 classとする。
- Exact schemeはllama.cpp Compatibility、Model Quality、Disk、Unified MemoryおよびConversion Evidenceを確認してFreezeする。現時点で文字列だけをHard-codeしない。
- Community Artifactを自動採用せず、公式WeightからのSelf-conversionと第三者Derived Artifactを別Decisionとして扱う。
- Q4生成／取得前にCurrent llama.cpp Versionが対象Architecture、Tokenizer、Chat TemplateおよびFunction Callingを正しく扱えるか確認する。

### 5.3 Local Feasibility

- V4 Flashは本Mac Local Gateの対象外とする。
- R1-0528-Qwen3-8B Q4について、Load、First Token、Streaming、Cancel、Unload、Reload、Context、Memory Pressure、Thermal、LatencyおよびQuality Smokeを実測する。
- Mac Unified Memory容量を推測で記録せず、実行時にユーザー承認された方法で確認する。
- Load成功だけで実用可能と判定せず、Conversation／RAG／Governance／Guardrail非Regressionを通す。

## 6. Dynamic Context Size

### 6.1 Meaning

`context_size`はModel Load時のContext Windowであり、Current Mac Defaultは`8192`である。llama.cppではLoaded Contextを安全にインプレース変更できないため、Web Serverを維持しつつModel RuntimeだけをUnload／Reloadする。

```text
Advanced Settings Preview
  → Model／Backend／Deployment上限照合
  → Idle Gate
  → Same Modelを新context_sizeで内部Reload
  → Runtimeが返すloaded_context_sizeを照合
  → 成功Receipt後にCurrent Snapshot更新
```

### 6.2 Limits

選択可能上限は少なくとも次の最小値から動的に解決する。

```text
min(
  model_native_context_limit,
  backend_supported_context_limit,
  deployment_verified_context_limit
)
```

- Model Card値だけを、このMacで安全に使用可能な上限と同一視しない。
- 未検証範囲は`verified`と表示しない。
- Hardware不足、Backend拒否またはLoad失敗をSilent Clampしない。
- 値を固定一覧へHard-codeせず、Model Definition／Capability Snapshot／Deployment Profileから構築する。

### 6.3 UI

Advanced Settingsに次を表示する。

- Current／Requested Context Size。
- Model Native Limit。
- Backend Limit。
- Deployment Verified Limit。
- Effective Selectable Maximum。
- Model内部Reloadが必要であること。
- Current State：idle／reloading／rollback／ready／failed。

Sidebarには少なくともCurrent Modelを表示し、必要に応じCurrent Context Sizeを併記できる。ただしSidebar表示をRuntime Authorityにしない。

## 7. Dynamic Max New Tokens

### 7.1 Meaning

`max_new_tokens`は一回のGenerationで許可する最大新規Token数であり、Current UI／Validationには固定`2048`上限がある。本GateではCurrent Model／Contextに追随するRuntime設定へ変更する。

- Model Reloadを行わない。
- 次のGenerationから反映する。
- Advanced Settings再Open時にServer側Current値を表示する。
- Model／Context切替後は上限を再計算する。

### 7.2 Limits

Global設定の上限と、個別Generationで実際に利用可能な上限を分離する。

```text
configured_max_new_tokens
  <= min(model_max_output_tokens, backend_max_output_tokens)

request_effective_max_new_tokens
  <= min(
       configured_max_new_tokens,
       loaded_context_size - exact_prompt_and_reserved_tokens
     )
```

- System、History、Current User、RAGおよび必要なGovernance／Guardrail予約分を無視しない。
- Current PromptでContextへ収まらない値をSilent Clampしない。送信前PreviewまたはSafe Validation Errorを返す。
- Browser固定`1..2048`だけで検証せず、Serverも同じCapability Snapshotから検証する。
- UIとServer Validationの上限不一致を禁止する。

### 7.3 UI

Advanced Settingsに次を表示する。

- Current Max New Tokens。
- Model／Backend上の最大値。
- Current Contextでの利用可能値。
- Prompt／History／RAGにより個別Request上限が下がり得ること。
- 適用結果またはValidation Error。

Context Usage表示と可能な範囲で連携するが、推定値をExactと表示しない。

## 8. UI Synchronization Contract

### Sidebar

- Current Modelの安全な表示名。
- Loading／Switching／Rollback／Unavailableの状態。
- Model切替成功後の即時追随。
- Browser Reload後のServer Snapshot再取得。

### Advanced Settings

- Model Selector。
- Current Model／Candidate Model。
- Context Size Current／Maximum／Source。
- Max New Tokens Current／Maximum／Source。
- Preview／Apply／Failure／Rollback Receipt。

### Consistency

- Sidebar、Advanced Settings、Runtime Status APIおよび実Generation Model Identityを一致させる。
- Apply要求値を、成功前にCurrent値として表示しない。
- Settingsを閉じて開き直したときDefault表示へ戻さない。
- 別Browser／TabでもServer側Canonical Stateを取得する。

## 9. Phase 6 Dependency

本GateをPhase 6-0のAs-built Reconciliation後、Judge／Repair Exact Freeze前に実行する。

```text
Phase 5 Accepted／Closed
  → Phase 6-0 As-built Reconciliation
  → DeepSeek Local Feasibility／Integration
  → Runtime Model／Context／Output Token Switch Acceptance
  → Phase 6 Judge Model／Evaluation／Repair Exact Freeze
```

これによりPhase 6は、Qwenだけへ固定した評価ではなく、少なくともQwen／DeepSeekのModel Identityを明示した比較を設計できる。ただしDeepSeek成功をPhase 6全機能の必須条件に自動昇格しない。Mac Feasibilityが不成立の場合も、Model-neutral Contractと明示Unsupported Evidenceを残し、QwenでPhase 6を継続できる。

## 10. Acceptance Matrix Candidate

### Artifact／Load

- Canonical／Derived Provenanceが追跡可能。
- Exact Q4 Artifact Digestが検証される。
- DeepSeek Load／Unload／Reloadが成功する、またはSafe Unsupportedが確定する。
- V4 FlashをMac対象として誤表示しない。

### Runtime Switch

- Startup DefaultはQwen。
- Qwen→DeepSeek→QwenをServer再起動なしでRound-tripできる。
- Active Generation中の切替を安全に拒否する。
- Candidate Load失敗時にPrevious QwenへRollbackできる。
- Rollback失敗時はGeneration受付をFail-closedする。

### Conversation／Feature Compatibility

- Persistent／Ephemeral Conversationが失われない。
- RAG Citation、Retry／Regenerate、Branch、Stop、Resumeが壊れない。
- Main Governance／Guardrail OFF／OBSERVE／ENFORCEが両Modelで同じContractを通る。
- Turn／EvidenceへExact Model／Artifact／Backend／Config Identityが残る。

### Context／Tokens

- Modelごとの上限がUIとAPIで一致する。
- Context Size変更でServerは生存し、Modelだけ安全にReloadされる。
- Settings再Open／Browser Reload後もCurrent Contextを表示する。
- Max New Tokens変更はReloadなしで次Generationへ反映される。
- Prompt込みでContextを超える要求をSilent Clampしない。

### UI

- SidebarとAdvanced SettingsのCurrent Modelが実Runtimeと一致する。
- Switch／Reload／Rollback中の状態が確認できる。
- Apply失敗時に要求値をCurrent値として残さない。

### Regression

- Current Qwen Mac routeを維持する。
- Public／Basic／LightningへDeepSeekやLocal Controlを自動Bindingしない。
- User実`runtime_data/`へTestが接触しない。
- Phase 4／5 Governance／Security／Authority境界を弱めない。

## 11. Stop／Human Gates

次は人間判断または上位Gateへ返す。

- Derived Artifact作成／取得方法とExact Q4 scheme。
- 大規模Disk Mutation、Canonical Weight削除またはModel Artifact置換。
- Project Root外、Network、External Serviceまたは追加Download。
- Native Mac Hardware情報取得方法。
- Model Loadによる高Memory／Thermal／Disk Risk受容。
- DeepSeekをStartup DefaultまたはCurrent Promoted Modelへ変更する判断。
- Runtime Selectionの永続化。
- V4 Flash Server／AWS／Cloud Backend開始。

## 12. Non-Authorization Statement

本書の作成は次を許可しない。

- Phase 6開始。
- DeepSeek Quantization、Conversion、Load、BenchmarkまたはPromotion。
- Source／Config／Test／Frontendの変更。
- User実`runtime_data/`への接触。
- Git／GitHub、Network、AWS、Lightning、Secret、課金または外部公開。
- Phase 5実行中Scopeへの混入。

Phase 5 Closure後、Phase 6設計時にAs-built、Mac Resource、Backend Compatibility、Disk余力およびHuman Gateを再確認し、Exact PackageへFreezeする。

