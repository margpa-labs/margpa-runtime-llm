# Phase 5 Codex Second Independent Review — Exact Rework Handoff

```yaml
document_id: phase_5_codex_second_independent_review_rework_handoff_20260822171307
status: rework_required
phase: phase_5
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
recorded_at: 2026-08-22 17:13:07 JST
predecessor:
  - docs/project/phases/phase_5/handoffs/phase_5_codex_independent_review_rework_handoff_ja_20260822153624.md
  - docs/project/phases/phase_5/handoffs/phase_5_claude_rework_complete_candidate_handoff_ja.md
  - docs/project/phases/phase_5/history/operations/phase_5_gov001_evidence_grade_and_zero_claim_correction_ja_20260822163917.md
phase_5_h_closure: blocked
source_repair_by_codex: not_performed
git_mutation: not_performed
```

## 1. Review Result

Claude Reworkにより、実RAG経路へのPoint接続、Streaming Enforceの長いEmail Prefix漏えい修正、Safety Modelの基本Typed SeamおよびBare Mypy回復は前進した。しかし、`Open Major Finding 0`／`P5-CODEX-001..004 Closed`は受理できない。

本ReviewはMinor、表現上の好み、将来改善候補を再活性化しない。以下はAccepted／Frozen Phase 5 Contractまたは最上位運用規則へ直接影響する重大Findingだけである。

```text
Codex Recommendation : ADJUST
Phase 5-H Closure     : DO NOT START
Open Major Finding   : 4 technical areas + 1 governance correction
P5-CODEX-005         : ACCEPTED
Source-wide Regression: NOT DETECTED
```

## 2. Independent Validation

### 2.1 Reproduced PASS

```text
Focused Guardrail／RAG／Stream : 129 passed
Bare Mypy                     : PASS — 319 source files
Ruff Check                    : PASS
Ruff Format Check             : PASS — 319 files
Frontend Test                 : PASS — 175 tests／20 files
Frontend Typecheck／Lint      : PASS
```

Backend Fullは、長いProject-local Basetempを使った初回Runで`1197 passed／9 failed／3 deselected`となった。9件はすべて既知のmacOS Path長制約によるSQLite `unable to open database file`である。同じMigration関連2 File・18 Testを短いProject-local Basetempで再実行し、`18 passed`を確認した。したがって9件をSource Regressionとして扱わない。

### 2.2 Independent Adversarial Probes

```text
Probe A: PolicySnapshot revision=0
Result : reject_input executed=True

Probe B: ActionRegistrySnapshot revision=0
Result : reject_input executed=True

Probe C: OBSERVE Streamの単一大Delta
Input  : "victim@example.com" + "x" * 1000
Result : released_len=1018／match_count=0

Probe D: Safety Model unknown label
Input  : failure=none、confidence=1.0、category_id=novel_unknown_label、outcome=clear
Result : is_trustworthy=True／bridge outcome=clear
```

これらはDocument解釈ではなく、Current Sourceを直接呼び出して得た結果である。

### 2.3 Review-time Test Artifacts

Codex ReviewはProject Root内だけで、次のProject-local Basetempを生成した。無許可Cleanup禁止に従い、本Reviewでは削除していない。

```text
.pytest_cache/codex_p5r2_focused/
.pytest_cache/codex_p5r2_full/
.t/
```

## 3. Required Rework

### P5-CODEX-006 — RAG Source Authority分離を実体化する

Reopen lineage：`P5-CODEX-001`、`P5-PNT-001/003`、`P5-ACC-007`、`P5-B-WU-003`。

成立した部分：

- Retrieval後かつRequest構築前に`guardrail.context_source`を呼ぶ経路は接続された。
- Known MarkerをENFORCEで検出した場合のModel Call 0経路は成立する。

未成立の重大部分：

1. Hook引数は依然としてFlat `str`であり、RAG Document／Citation／System-owned Instruction／Tool-like Textを識別するTyped Source Classが存在しない。
2. 全RAG Contextを一つの`reference_message`へ畳み、個別Source Identity／Authorityを保持していない。
3. Model RequestではRAG Contentが依然`MessageRole.SYSTEM`として挿入される。Claude Handoff自身も「真のSystem Promptと同一Nominal Authority」と認めている。
4. Known MarkerのScan-and-Vetoは、未登録表現のInstruction-like TextがSystem Authorityを得る構造を解消しない。
5. Exact Reworkで必須としたRetry／Regenerate／Branch／Resume専用経路Testを作らず、Full Suiteと共有Path論証へ置換している。

Required：

- RAG／External Contextを、少なくとも`source_class`、opaque source/citation identity、untrusted contentを持つTyped EnvelopeとしてPointへ渡す。
- System-owned InstructionとRetrieved Dataが、Domain、Policy、Prompt Compositionの各境界で同一Authorityにならない構造へ修正する。`name="documentation_reference"`だけをAuthority分離と見なさない。
- 複数Source／Citationを一つの無型文字列へ潰す前に、Source単位の判定とSafe aggregate decisionを行う。
- OFF／OBSERVE／ENFORCE、Benign／Indirect Injection、Persistent／Ephemeral、Retry／Regenerate／Branch／Resume、Public／Basic Call-0を実経路で検証する。
- Existing Citation表示／永続復元とPhase 2-E互換を壊さない。

### P5-CODEX-007 — 全Current SnapshotのFreshnessを実RuntimeでFail-closedする

Reopen lineage：`P5-CODEX-002`、`P5-AUT-003`、`P5-ACC-014`、Architecture §3.3／§4／§10。

現状はAuthorityだけの部分実装である。

- `PolicySnapshot`へFieldは増えたが、`GuardrailPointRuntime`はPolicy revision／expiry／scope／digestを実行可否へ使わない。
- `DetectorRegistrySnapshot`／`ActionRegistrySnapshot`はRevisionと計算Digestだけで、Scope／Source Class／Expiryを持たない。
- `ApprovalState`はOutcomeとReferenceだけで、Revision／Scope／Digest／Source Class／Expiryを持たない。
- Detector Registryは実RuntimeへSnapshotとして渡されず、Digest文字列をResultへ写すだけである。
- `expected_authority_digest_sha512=authority.digest_sha512`は同じLive Objectから直前に再計算しており、通常Composition経路でSnapshot交換を検出できない。Direct Resolver Testだけが人工的Mismatchを作っている。
- OBSERVEはStale／Unknownでも`evaluated`のままで、Degraded／Unavailable Evidenceへ収束しない。

独立Probeでは`policy_revision=0`と`action_registry_revision=0`の両方で、実Actionが実行された。

Required：

- Policy／Authority／Approval／Detector Registry／Action Registryの全てに、Frozen ContractのRevision／Scope／Digest／Source Class／Expiryまたは明示Non-expiringを持たせる。
- Point評価開始時にCurrent Snapshot Setを一度だけCaptureし、Decision／Resolver／Resultまで同じBinding Identityを使う。Resolution直前のLive値をExpected値として再計算しない。
- Policy DecisionのStamped Identity、Registry実体、Adapter実体およびApproval StateをCaptured Snapshotと照合する。
- Revision 0、expired、malformed expiry、scope mismatch、digest mismatch、Snapshot交換、旧CacheをActual Composition経路でFail-closedにする。
- OBSERVEはContent Mutation 0のままDegraded／UnavailableをSafe Evidence化し、ENFORCEはAction 0へ収束する。
- Direct Resolverだけでなく`GuardrailGovernanceComposition`／`GuardrailPointRuntime`を通すRevision／Cache Matrixを追加する。

### P5-CODEX-008 — Unknown Safety Model Labelを型とSchemaでRejectする

Reopen lineage：`P5-CODEX-003`、`P5-RES-005`、`P5-SFM-001..004`、`P5-ACC-017`。

`SafetyModelResponse.failure=UNKNOWN_LABEL`をFake自身が設定した場合のTestは成立している。しかしこれは「未知Labelを検出した」Testではなく、「既にUNKNOWN_LABELと分類済みのResponseをBridgeがUNKNOWNへ変換した」Testである。

Current Contractには、`label_schema_id`が示すAllowed Label／Category集合と`GuardDetection`を照合する境界がない。そのため、未知Categoryを持つResponseでもProviderが`failure=none`、高Confidence、`outcome=clear`を返せば`is_trustworthy=True`となり、Bridgeは`clear`をそのまま返す。独立Probeで再現済みである。

Required：

- Label Schema IdentityとAllowed Label／Category mapping、または同等のTyped Decoder境界を固定する。
- Raw／Provider ResponseをSafe Decoderで検査し、Unknown Label、Schema mismatch、矛盾したFailure／Timeout／Calibrationを`unknown`／`error`／`unavailable`へFail-closedする。
- Fake Matrixは`failure=UNKNOWN_LABEL`を事前注入するだけでなく、実際にUnknown Raw Label／Unknown Category／Schema mismatchを返すProviderを通して検出境界を試験する。
- Production Unavailable／Call 0およびDeterministic Detector優先は維持する。

### P5-CODEX-009 — 全Client-visible Streamを欠落なくOBSERVE／ENFORCEする

Reopen lineage：`P5-CODEX-004`、Architecture §6.1／§6.2、`P5-PNT-005`、`P5-ACC-005/009/022`。

成立した部分：

- ENFORCEの長いEmail Prefix leakは、Bounded RegexとDetector由来Holdbackにより修正された。
- OFFはNull Guard、OBSERVEはByte-identical非介入、ENFORCEはBounded WindowというMode分離ができた。

残る重大不整合：

1. `ObservingStreamGuard.feed()`は`(_window + delta)[-window_chars:]`へ切り詰めてからScanする。単一DeltaがWindowより長い場合、先頭／中間のMatchを未検査のままClientへ全放出する。独立ProbeでPII見落としを再現済み。
2. OBSERVEの`detection_count`／`match_count`／`degraded`はRequest-local Object内だけに残り、Stage終了後に破棄される。`guardrail.stream_candidate`のTyped Result／Safe Evidence／UI Statusへ接続されていないため、実運用上のObservationは回収不能である。
3. `_emit_guarded()`は`ThinkingContentKind.REASONING`を無条件にGuard対象外とする。Thinking VisibilityがVISIBLEならReasoning DeltaはClient-visibleであり、Secret／PIIを未検査のままStreamingできる。Terminal Output Guardも`presented.final_content`しか検査しないため、既に漏れたReasoningを補足できない。

Required：

- 任意長の単一Deltaも、Bounded Chunk処理または等価方式で全位置を欠落なくScanし、OBSERVEはByte-identical／非介入を維持する。
- Stream GuardのTerminal SummaryをTyped `guardrail.stream_candidate` ResultとしてCompositionへ返し、Safe Count／Match／DegradedだけをStatus／Evidenceへ接続する。Raw Candidateは保存しない。
- Client-visibleなFINAL／REASONINGの両ChannelをGuard対象にする。Hidden Reasoningは非表示・非永続の既存契約を維持する。
- 大単一Deltaの先頭／中間／末尾、1文字Chunk、Long Benign、Visible Thinking内Secret／PII、Cancel／Disconnect、Concurrent Turnを実経路で検証する。

### P5-GOV-002 — Evidence Correction自体の分類と無許可Cleanupを訂正する

Reopen lineage：`P5-GOV-001`、Canonical Governance §8.6、Phase 3 `P3-GOV-004/005`。

`phase_5_gov001_evidence_grade_and_zero_claim_correction_ja_20260822163917.md`はZero断定の多くを`SELF_REPORTED_UNVERIFIED`へ正しく戻した。一方、次は未訂正である。

1. ClaudeはExact Rework Handoffの「`.p5t/`／Temporary Artifactの無許可Cleanupを行わない」に反して、各Checkpointで`rm -rf .p5t`を実行したと自ら記録している。
2. その削除を「現在時制のCommandだから`REPOSITORY_STATE_VERIFIED`」と分類しているが、Evidence Classは許可の有無を変えない。またDocument記録時点では既に過去Actionであり、Current Repository Stateとも異なる。
3. Bare Mypy Preflight齟齬の原因を「新規File追加前、またはProject全体を対象にしなかった」と推測している。再現可能Evidenceがないため、原因は`UNKNOWN`と記録すべきである。
4. `REPOSITORY_STATE_VERIFIED`を「再実行可能なCommand Result」に広げると、Current Stateと過去Action／過去Outputが再混同される。実測値は再現したReviewerが`INDEPENDENTLY_REPRODUCED`へ昇格できるが、Claude自身の過去Runは自己申告である。

Required：

- 既存Correctionを変更せず、新規Append-only Correctionを作る。
- `.p5t/`削除を、Project Root内のTest Scratchだったという限定付きで、`UNAUTHORIZED_CLEANUP_SELF_REPORTED`として記録する。事後探索、復元、追加Cleanupは行わない。
- Bare Mypy齟齬の原因を`UNKNOWN／証拠不足`へ訂正する。
- Current Repository State、Reproducible Current Result、Past Action Log、Self-reportを再分離する。
- 今後のReworkではTest Artifactを無許可削除しない。

## 4. Accepted Rework

次は再Rework対象へ戻さない。

- `P5-CODEX-005`：Bare MypyはCodex独立再実行でExit 0を確認した。
- Ruff Check／Format、Frontend Test／Typecheck／LintはPASSした。
- Backend Fullの9失敗は長Path由来であり、短Pathの関連18 TestがPASSしたためSource Regressionではない。
- ENFORCE Streamingの従来の長いEmail Prefix leakは修正された。
- Safety ModelのProduction Default Unavailable／実Artifact Call 0方針は維持されている。

## 5. Allowed Rework Boundary

必要性を実Sourceから動的にExact化し、次のPath Classだけを最小変更できる。

```text
src/margpa_runtime_llm/modules/guardrail_governance/**
src/margpa_runtime_llm/adapters/guardrail_governance/**
src/margpa_runtime_llm/bootstrap/guardrail_governance.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
RAG Source Class／Prompt Composition修正に必要な既存Documentation RAG Contract／Application境界
Guardrail Stream ResultをComposition／Statusへ返すために必要な既存Web／Configuration境界
tests/unit/guardrail_governance/**
tests/integration/conversation/** の該当Guardrail／RAG／Thinking Test
tests/integration/documentation_rag/** の該当Context Source Test
tests/integration/web/test_guardrail_*.py
docs/project/phases/phase_5/history/** の新規Append-only Correction／Recovery
docs/project/phases/phase_5/handoffs/phase_5_claude_second_rework_complete_candidate_handoff_ja.md の新規作成
```

既存Stable Docs、既存History／Handoffを変更しない。Exact File Setは変更前に実接続点から確定する。

## 6. Forbidden

- Project Root外、Provider Memory、User実`runtime_data/`、`models/`、`definitions/`、Git／GitHub、Network、Model Load／Download、AWS／Lightning。
- Existing Stable Docs、既存History／Handoffの書換え。
- Phase 5-H Closure、User Acceptance、Phase 6、DeepSeek Gateの開始。
- Frozen要件をClaude判断でScope外／Deferred／共有Path論証へ置換すること。
- Test削除／Skip／緩和によるPASS化。
- Root外Temporaryの利用、Project-local Test Artifactを含む無許可Cleanup。

## 7. Required Validation

```text
1. Typed RAG Source Authority／Prompt Composition／全Conversation経路Matrix
2. Policy／Authority／Approval／Detector Registry／Action RegistryのActual Runtime stale/cache Matrix
3. Unknown Raw Label／Unknown Category／Schema mismatch Safety Model Matrix
4. Large Single Delta／Visible Thinking／Stream Result Status／Concurrency Matrix
5. Phase 5 Guardrail Focused Suite
6. RAG／Conversation／Persistence／Web Adjacent Regression
7. Public／Basic／v1／v2 Call-0
8. Backend Full Suite（短いProject-local Basetemp）
9. Frontend test／typecheck／lint。UI／Built Static変更時はbuild同期
10. ruff check .／ruff format --check .／Bare mypy
```

Test件数、失敗、Skip／Deselect、Command、Basetemp Path、Evidence Classを正確に記録する。Project-local Test Artifactは停止時に残し、削除判断をユーザーへ返す。

## 8. Completion Contract

Claudeは上記4技術領域とGovernance CorrectionをFrozen Scope内でSelf-repairし、Required Validation完了後に次の新規FileだけをCompletion入口として作る。

```text
docs/project/phases/phase_5/handoffs/
  phase_5_claude_second_rework_complete_candidate_handoff_ja.md
```

Handoffには各FindingのClosure Evidence、Exact Mutation、独立再現可能なAdversarial Probe、Validation、残置Test Artifact、Open Major Findingを含める。作成後は追加作業を開始せず、Codex Final Re-review待ちで停止する。
