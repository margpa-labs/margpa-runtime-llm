# Phase 5 Codex Independent Review — Exact Rework Handoff

```yaml
document_id: phase_5_codex_independent_review_rework_handoff_20260822153624
status: rework_required
phase: phase_5
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
recorded_at: 2026-08-22 15:36:24 JST
phase_5_h_closure: blocked
git_mutation: not_performed
```

## 1. Review Result

`phase_5_claude_complete_candidate_handoff_ja.md`の`GO／Open Major Finding 0`は受理しない。Phase 5の主要実装と回帰Testは広く成立しているが、Accepted／Frozen要件をClaude側だけで`DEFERRED／N/A`へ変更した3領域、Streaming契約の重大不整合、Static Gate失敗およびEvidence Class誤分類が残る。

```text
Codex Recommendation : ADJUST
Phase 5-H Closure     : DO NOT START
Source Repair         : NOT PERFORMED BY CODEX
User Mac Acceptance   : REWORK後
```

Minor／将来改善候補は本Handoffへ含めない。以下はPhase 5 Closureへ直接影響する重大Findingだけである。

## 2. Independent Validation

```text
Phase 5 Focused Backend : 97 passed
Backend Full            : 1156 passed／3 deselected
Frontend                : 175 passed／20 files
Ruff Full               : PASS
Bare Mypy               : FAIL — 99 errors／9 files
```

最初のBackend Fullは長いProject-local Basetemp名によりmacOS Path長制約へ到達し、SQLite Migration Test 9件が`unable to open database file`となった。短いProject-local Basetempで当該13 Testを再実行するとPASSし、Full再実行も`1156 passed／3 deselected`となった。この9件はSource Failure／Regressionとして扱わない。

## 3. Required Rework

### P5-CODEX-001 — `guardrail.context_source`を実RAG経路へ接続する

Frozen Contract：`P5-PNT-001/003`、`P5-DET-004`、`P5-ACC-007`、Execution Plan `P5-B-WU-003`、Completion Condition。

現状はIdentityだけが存在し、実RAG Pipelineへ接続されていない。Claude Handoff自身が`未接続（Deferred）`と記録している。RAGがSystem Roleへ昇格しない既存構造は互換防御であり、Phase 5専用Point、Source Trust分離、Indirect Injection DetectionおよびMode Matrixの代替ではない。

Required：

1. Retrieval後、Model Promptへ合成する前に、各RAG／External ContextをTyped Source Class付きで`guardrail.context_source`へ渡す。
2. User Input、System-owned Instruction、RAG Document、CitationおよびTool-like Textを同一Authorityとして扱わない。
3. OFFはCall 0、OBSERVEはDetection／Safe Evidenceのみ・RAG内容／Citation／Output Mutation 0、ENFORCEはApplicable Policy／Current Authority／Registryの明示Actionだけを実行する。
4. ENFORCE拒否時はModel Call、Ghost Completion、未承認Commit、Citation誤帰属を0にする。
5. RAG Source内Instruction、Benign Document、複数Citation、Persistent／Ephemeral、Retry／Regenerate／Branch／ResumeおよびPublic／Basic Call-0をTestする。

### P5-CODEX-002 — Stale Policy／Authority／Approval／Registryを実際にFail-closedする

Frozen Contract：`P5-AUT-003`、Architecture §3.3／§4／§10、`P5-ACC-014`、Execution Plan `P5-D-WU-001/002`。

現行`PolicySnapshot`／`AuthoritySnapshot`はRevisionと計算PropertyのDigestだけを持ち、Scope、Source Class、Expiryがない。ApprovalにSnapshot freshness契約がなく、ResolverはStale／Unknownを判定しない。固定Local値であることは、必須Negative Matrixを`N/A`にする理由にならない。

Required：

1. Policy／Authority／Approval／Detector Registry／Action Registryについて、Frozen設計が要求するRevision、Scope、Digest、Source Class、Expiry／Non-expiring表現をTyped Contractへ固定する。
2. Digest mismatch、Scope mismatch、Stale／Expired、Unknown Revision、Snapshot交換後の旧CacheをCurrentとして再利用しない。
3. OBSERVEはMutation 0でDegraded／UnavailableをEvidence化し、ENFORCEはSilent Observe／Safe Allowへ落とさずAction 0でFail-closedする。
4. Current固定Local Providerでも、Synthetic stale／unknown／mismatch Snapshotを使うRevision／Cache Matrixを作る。

### P5-CODEX-003 — Safety Model SeamとFake Adapter MatrixをFrozen Contractどおり完成させる

Frozen Contract：`P5-RES-005`、`P5-SFM-001..004`、Architecture §8、`P5-ACC-003/016/017`、Execution Plan `P5-E-WU-001..003`。

現行Portは`content -> GuardDetection`だけで、Model ID、Exact Revision、Artifact Digest、Label Schema、Calibration、Timeout、Latency、Token／Call数およびFailureを分離していない。Fake Adapter TestはMatch／Clearだけで、Unknown Label、Low Confidence、Timeout、MalformedおよびDeterministic DetectorとのConflictを検証していない。実Safety Model未LoadはProduction Non-scopeだが、Typed SeamとFake Negative MatrixはPhase 5 Scopeである。

Required：

1. Typed Request／Responseまたは等価Contractへ上記Identity／Calibration／Failure情報を分離する。
2. Production Default Unavailableを維持し、実Artifact Download／Loadは行わない。
3. Test-only FakeでUnknown Label、Low Confidence、Timeout、Malformed、Unavailable、Conflictを再現する。
4. いずれもPass／Allowへ変換せず、Mode／Policyに従うTyped unknown／degraded／unavailable、Action 0またはFail-closedへ収束させる。
5. Production Safety Model Call 0とDeterministic Baseline成立を再確認する。

### P5-CODEX-004 — Streaming OBSERVEとENFORCEのBounded／Zero-leak契約を修正する

Frozen Contract：Architecture §6.1／§6.2、`P5-PNT-005`、`P5-MOD-003`、`P5-ACC-005/009/022`、Execution Plan `P5-C-WU-002`。

現行`new_stream_guard()`はOBSERVEでも`NullStreamGuard`を返すため、Stream PointのDetection／Observation／Degraded Evidenceが0になる。これは「非介入」ではなく「未観測」であり、Architecture §6.1と不一致である。

また`IncrementalStreamGuard`は全Candidateを`_buffer`へ保持したまま毎Chunkで全再Scanするため、Memoryは非有界、処理量は長さに対して二次的に増え得る。固定64文字HoldbackはDetectorの最大Match長と契約されていない。実装済みPII Regexでは、長いlocal-partを持つEmailのPrefixがMatch確定前にClientへ放出される。

Codex実測：

```text
feed("a" * 100)       -> 36文字を先行放出
feed("@example.com") -> PII Match／Terminate
Result                -> Match対象Prefix 36文字が既にClient側へ放出済み
```

Required：

1. OFFは引き続きDetector Call 0／Byte-identicalとする。
2. OBSERVE専用ScannerはByte-identical Streamingを維持しながら、Bounded StateでDetection／Failureを記録し、絶対にTerminate／Suppressしない。
3. ENFORCEはDetectorごとの最大Candidate長または明示的な安全境界とHoldbackを契約し、Match対象文字列の一部も先行放出しない。
4. Released Prefixを無期限保持・全再Scanしない、明示上限を持つRequest-local Stateにする。Limit超過／Detector FailureはSilent Passしない。
5. Long Email、長いBenign Stream、Chunk 1文字分割、最大境界±1、Cancel／Disconnect、Concurrent Turnを含むRegressionを追加する。

### P5-CODEX-005 — Bare Mypy GateをPASSへ戻し、Baseline誤記録を訂正する

Frozen Contract：Execution Plan §4 Validation Ladder `Phase 5-G ... Ruff／Mypy`、Execution Handoff §4／§6。

Claude PreflightはBaselineを`mypy PASS`と記録したが、Completion時のBare Mypyは`99 errors／9 files`で失敗している。Codex再実行も同じ99件を確認した。さらにそのうち1件はPhase 5新規File`tests/integration/web/test_guardrail_governance_public_basic_call0.py`に存在するため、「Phase 5新規混入0」は事実と一致しない。

Required：

1. Project Rootで追加引数なしのBare MypyをExit 0にする。Frozen GateをClaude判断で「Phase 5関連Fileだけ0 Error」へ縮小しない。
2. Preflightの`PASS`とCompletionの`99 errors`が両立しない事実をAppend-only Correctionへ記録する。過去Evidenceを書き換えない。
3. `99 errors`を「既知債務」と呼ぶ場合は、Phase 5開始前に存在したことを再現可能なEvidenceで区別する。証明できないものは推測で分類しない。

### P5-GOV-001 — Zero ClaimとEvidence Gradeを正しく再分類する

Canonical Governance：`automation_cross_provider_compaction_governance_integrated_ja.md` §8.6、Phase 3 `P3-GOV-002/004/005` Correction lineage。

Claude Handoffは、Root外／Provider Memory／User `runtime_data/`／Network／External Action 0件と全数値を一括して`STRONG_VERIFIED`相当とした。しかし同一Session内の自己認識やRepository差分だけでは、過去Actionの不在証明にならない。Phase 3で既に同一表現を`SELF_REPORTED_UNVERIFIED`へ訂正済みである。

Required：

1. 既存Handoffを変更せず、Append-only Evidence Correctionを作る。
2. Codexが再実行したBackend／Frontend／Ruff／Mypyは`INDEPENDENTLY_REPRODUCED`として分離する。
3. Root外／Provider Memory／User Data／Network／External等の過去Action 0件は、完全なAction Logがない限り`SELF_REPORTED_UNVERIFIED`とする。
4. Current Repository State、現在のArtifact存在有無および過去Action Countを混同しない。
5. `.p5t/`やOS Temporary Artifactについて、事後推測、Root外調査または無許可Cleanupを行わない。

## 4. Allowed Rework Boundary

Frozen Phase 5 Scope内で、次の既存／新規Path Classだけを必要最小限変更できる。

```text
src/margpa_runtime_llm/modules/guardrail_governance/**
src/margpa_runtime_llm/adapters/guardrail_governance/**
src/margpa_runtime_llm/bootstrap/guardrail_governance.py
src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
Phase 5 GuardrailをRAG Context Sourceへ接続するために必要な既存Documentation RAG／Bootstrap境界
Phase 5 Configuration／Web Projectionの整合に必要な既存Path
tests/unit/guardrail_governance/**
tests/integration/conversation/** のPhase 5／RAG関連Test
tests/integration/documentation_rag/**
tests/integration/web/test_guardrail_*.py
Bare Mypy 99件をExit 0へ戻すためのExact Error Fileだけ
docs/project/phases/phase_5/history/** の新規Append-only Recovery／Correction
docs/project/phases/phase_5/handoffs/phase_5_claude_rework_complete_candidate_handoff_ja.md の新規作成
```

対象Fileは開始前に実Error／接続点から動的にExact化し、無関係なPackage、固定件数または既存Stable Docsを変更しない。

## 5. Forbidden

- Project Root外、Provider Memory、User実`runtime_data/`、`models/`、`definitions/`、Git／GitHub、Network、Model Load／Download、AWS／Lightning。
- Existing Stable Docs、既存History／Handoffの書換え。
- Phase 5-H Closure、User Acceptance、Phase 6、DeepSeek Gateの開始。
- Safety Model実Artifactを必要条件にすること。
- Frozen要件を`Deferred／N/A`へ再分類すること。
- Testを削除／Skip／緩和してPASSにすること。
- Root外Temporary Directoryの利用、事後探索または自己Cleanup。

## 6. Required Validation

```text
1. P5-CODEX-001..005 dedicated focused tests
2. Phase 5 Guardrail focused suite
3. Documentation RAG／Conversation／Persistence／Web adjacent regression
4. Public／Basic／v1／v2 Call-0 and compatibility spies
5. Backend Full Suite
6. Frontend test／typecheck／lint（UI変更時はbuild同期も含む）
7. ruff check .
8. ruff format --check .
9. Bare mypy — Exit 0
10. Project内の短い専用Basetempを明示使用
```

実Test数、失敗、Skip／Deselect、CommandおよびEvidence Classを正確に記録する。長いBasetempによる既知のmacOS Path長FailureをSource Regressionと誤分類しない。

## 7. Completion Contract

ClaudeはFrozen Scope内でSelf-repairし、全Required ReworkとValidationを完了してから、次の新規Fileを作る。

```text
docs/project/phases/phase_5/handoffs/
  phase_5_claude_rework_complete_candidate_handoff_ja.md
```

HandoffにはP5-CODEX-001..005／P5-GOV-001の各Closure Evidence、Exact Mutation、全Validation、Open Major Finding、自己申告と独立検証の分離を含める。完了後は追加作業を開始せず、Codex再Review待ちで停止する。
