# Phase 5 Codex 第3回独立Review／Exact Rework Handoff

## 1. Routing

- From：プロジェクト責任者兼設計統括者役（Codex側）
- To：Claude側 設計統括者役
- 対象：Phase 5 第2回Rework Candidate
- Review入力：
  - `docs/project/phases/phase_5/history/operations/phase_5_gov002_gov001_correction_reclassification_ja_20260822181202.md`
  - `docs/project/phases/phase_5/handoffs/phase_5_claude_second_rework_complete_candidate_handoff_ja.md`
- Review種別：独立Source／Contract／実経路Probe Review
- Automation：OFFのまま
- Phase 5-H：開始禁止
- Git Mutation：禁止

## 2. Controller判定

```text
Phase 5 Second Rework Result : REWORK REQUIRED
Phase 5-H Transition         : BLOCKED
Open Major Findings          : 3
Source Fix by Codex          : 0
Git Mutation                 : 0
```

P5-CODEX-009の「有効なPIIを含む大単一Deltaの欠落なき観測」と、P5-GOV-002の「無許可Cleanupを違反として再分類する訂正」は成立した。これらを再Openしない。

一方、P5-CODEX-006／007／008は、追加された型やTest自体は前進しているが、Frozen Requirementが要求する実効境界まで閉じていない。以下3件のみをRequired Reworkとする。

## 3. Major Finding 1 — P5-CODEX-006：RAG Retrieved DataがUser Inputと同じAuthorityになった

### 3.1 実装上の事実

`ConversationGenerationService._inject_documentation_reference()`は、RAG Referenceを次の形で実Promptへ入れている。

```text
role=user
name=documentation_reference
content=<retrieved document>
```

その後に、本物のUser Messageも`role=user`で続く。`LlamaCppChatTemplate._prepare()`は`ChatMessage`を辞書化してBackendのChat Templateへ渡すだけであり、`name=documentation_reference`をAuthority境界として検証・強制する処理を持たない。

したがって、前回の`role=system`問題は除去されたが、Retrieved／Untrusted Dataが今度はUser Inputと同じNominal Authorityになった。`ContextSourceUnit.source_class`はGuardrail Scan経路では保持されるものの、Modelへ渡るPrompt Composition境界では失われる。

これはFrozen Execution Planの次の要求を満たさない。

```text
User Input、System-owned Instruction、RAG Document、Citation、Tool-like TextのSource Classを保持する。
System-owned InstructionとRetrieved DataをDomain、Policy、Prompt Compositionの各境界で同一Authorityにしない。
name TagだけをAuthority分離と見なさない。
```

### 3.2 Required Rework

1. Retrieved／Untrusted Contextを、System InstructionともUser Inputとも同一AuthorityにならないPrompt Composition契約へ変更する。
2. `name`文字列、自然言語Prefix、単なるMessage順序だけをSecurity Boundaryにしない。
3. Domainの`source_class`／opaque source identityが、Guardrail判定後からBackend Prompt構築直前まで型として追跡可能であること。
4. 実Backendへ渡すNative Message／PromptをTestし、RAG SourceとUser Inputが同一Authorityへ潰れていないことを証明する。
5. Citation表示／永続復元、Retry／Regenerate／Branch／Resume、Public／Basic Call-0を維持する。

方式はClaude側で設計してよい。既存`MessageRole`のどれを使うか、専用Envelope／Prompt Builderを追加するかはHard-codeせず、Backend非依存性と将来のTool Contextを考慮して決定すること。

## 4. Major Finding 2 — P5-CODEX-007：Snapshot Identityが実体へBindingされていない

### 4.1 独立Probe

現実の`GuardrailGovernanceComposition`を用い、Revision 1でEntry／ResolutionのDigestも不変だが、SnapshotのScope／登録内容を実体と故意に不一致にした。

```text
Probe 007-A
Detector Registry Snapshot:
  scope=foreign_scope
  registered_detector_ids=(not.the.real.detector,)
Actual Runtime:
  real input detectors
Result:
  state=evaluated
  executed=[reject_input]

Probe 007-B
Action Registry Snapshot:
  scope=foreign_scope
  registered_action_ids=(warn,)
Actual Registry/Adapter:
  reject_inputを含む
Result:
  state=evaluated
  executed=[reject_input]

Probe 007-C
Entry Policy Snapshot:
  revision=1
Policy Decision Stamp:
  policy_revision=999
  policy_digest=別Identity
Result:
  state=evaluated
  executed=[reject_input]
```

### 4.2 原因

現在のRuntimeは、EntryとResolutionで取得したSnapshot同士のRevision／Expiry／Digest変化は検査する。しかし次を検査していない。

- Snapshot Set相互のScope整合
- `DetectorRegistrySnapshot.registered_detector_ids`と実Detector集合の一致
- `ActionRegistrySnapshot.registered_action_ids`と実Registry／Adapter集合の一致
- `PolicyDecision.policy_revision／policy_digest_sha512`とCaptured Policy Snapshotの一致

よって「同じ誤ったSnapshotを2回返す」Provider、または「Snapshotと実体が乖離した」Compositionでは、Current Binding Identityが成立していなくてもActionが実行される。

### 4.3 Required Rework

1. Entry時に一つのCurrent Snapshot Setを確立し、Scope互換性を検証する。
2. 実Detector ID集合をDetector Registry SnapshotへExact Bindingする。
3. 実Action Registry／Adapter集合をAction Registry SnapshotへExact Bindingする。少なくとも、実行候補ActionがCaptured Snapshotに登録されていない場合はAction 0へFail-closedする。
4. 全Policy DecisionのRevision／DigestをCaptured Policy Snapshotと照合する。
5. Approval-required経路では、Approval StateのScope／Revision／Digest／Expiryも、そのAction ResolutionのCurrent Bindingへ結合する。
6. OBSERVEはMutation 0のまま`degraded`、ENFORCEは`unavailable`／Action 0へ収束する。
7. 上記Probe A〜C相当をDirect Resolverではなく`GuardrailPointRuntime`／実Composition経路へ追加する。

## 5. Major Finding 3 — P5-CODEX-008：Raw Label Decoderを正式Portが迂回できる

### 5.1 独立Probe

現在の`SafetyModelPort.classify()`の返却型は依然`SafetyModelResponse`である。したがってPort適合Providerは`RawSafetyModelObservation`／`decode_safety_model_observation()`を通さず、完成済みResponseを直接返せる。

次のPort適合Providerを`SafetyModelDetectorAdapter`へ渡した。

```text
failure=none
confidence=1.0
confidence_threshold=0.0
category_id=novel_unknown_label
outcome=clear
```

独立実測結果：

```text
outcome=clear
category=novel_unknown_label
```

Fake Adapter内にDecoderを入れたことは成立しているが、実Provider Integration BoundaryはDecoderを強制していない。このため前回Findingの本質である「Provider自己申告をそのままTrustできる経路」が残っている。

### 5.2 Required Rework

1. 正式Provider PortはRaw Observationを返し、Trusted BridgeだけがSafe Decoder後の`SafetyModelResponse`を生成する構造にする、または同等にDecoder迂回不能な型境界へ変更する。
2. `SafetyModelDetectorAdapter`へ入る全実Provider Responseについて、Label Schema／Allowed Category／Failure／Timeout／Confidenceの検証済みであることを構造的に保証する。
3. Fake内部だけでなく、任意のPort実装が未知Raw Labelを返すProbeを追加する。
4. Unknown Label／Schema mismatch／矛盾Responseは`clear`／`allow`へ到達せず、`unknown`／`error`／`unavailable`へ収束する。
5. Production Default Unavailable、Safety Model Call 0、Deterministic Detector優先を維持する。

## 6. Accepted Evidence／再Open禁止

今回の独立Probeでは、次は成立した。

```text
ObservingStreamGuard:
  input length=40020
  valid embedded PII="victim@example.com "
  released=40020
  matches=1
  degraded=false
```

よってP5-CODEX-009は、本Reviewで新しい重大反証がない限りClosedのままとする。`victim@example.com`直後へ英字を連結した文字列は、一つの有効Email Tokenとしては別文字列になるため、今回のClosure Blockerにはしない。

P5-GOV-002についても、無許可`.p5t` Cleanupを`UNAUTHORIZED_CLEANUP_SELF_REPORTED`へ戻し、原因不明事項を`UNKNOWN`へ訂正した点はAcceptedとする。過去違反の事実は消さず、以後同種Cleanupを再実行しないこと。

## 7. Exact Scope

### 7.1 Allowed

- 上記3 Findingを閉じるために必要なPhase 5 Guardrail Domain／Port／Application／Adapter／Composition／Conversation Prompt Composition Source
- 対応するPhase 5 Unit／Integration Test
- 新規Append-only Rework Status／Completion Handoff／必要なCorrection Evidence

必要Fileは最小集合をClaude側 設計統括者役が動的に決定する。不要なPackage固定や関係ない既存Stable Docの変更は禁止する。

### 7.2 Forbidden

- Project Root外のRead／Write／Execute
- Provider Memory、`.claude/`、`.codex/`への保存
- User実`runtime_data/`の内容参照／変更
- `.p5t/`、`.t/`、`.pytest_cache/`その他既存Artifactの削除／移動／Cleanup
- Git add／commit／push／reset／checkout／clean
- Phase 5-H Closure、Phase 6開始、DeepSeek Load／Benchmark、Network／AWS／Lightning
- 既存Stable／History／Handoffの上書き

## 8. Validation／Return Contract

Claude側は、上記3件のExact Adversarial Probe、Phase 5 Guardrail Focused Test、RAG／Conversation／Web隣接回帰、Static Checkを実行する。Full Suiteを実行する場合も、既存Temporary Artifactを削除せず、新規の明示Pathを使い残置場所を申告する。

完了時は新規Append-only Handoffに次を記録する。

```text
P5-CODEX-006 : CLOSED / OPEN
P5-CODEX-007 : CLOSED / OPEN
P5-CODEX-008 : CLOSED / OPEN
P5-CODEX-009 : CLOSED（再Openしない）
P5-GOV-002   : CLOSED（違反履歴は保持）
Exact Mutation
Exact Probe Input/Output
Validation Result
Created Test Artifact Paths
Open Major Finding
Phase 5-H Recommendation
```

完了候補を返した時点で停止し、Codex Independent Re-reviewを待つこと。
