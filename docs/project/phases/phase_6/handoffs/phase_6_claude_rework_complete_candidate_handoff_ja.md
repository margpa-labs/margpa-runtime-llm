# Phase 6 Claude Rework Complete Candidate Handoff

```yaml
document_id: phase_6_claude_rework_complete_candidate_handoff
status: rework_complete_candidate
phase: phase_6
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 07:20:00 JST
source_rework_handoff: phase_6_codex_independent_review_rework_handoff_ja_20260823052052.md
```

本文書は同Rework Handoff §6 Return Contractに基づき、P6-CODEX-001〜008／
P6-GOV-001への対応を統合したCandidate Handoffである。詳細Evidenceは
`docs/project/phases/phase_6/history/index/`配下の新規Recovery Entry群
（本Rework分、末尾`_ja_202608230[5-7]****.md`）を一次資料とする。

## 1. P6-CODEX-001〜008／P6-GOV-001 Close Matrix

| ID | 状態 | 要約 |
|---|---|---|
| P6-GOV-001 | CLOSED | Append-only Correction作成済み（Root境界／Pre-authority Access／不要Escalation／Git Mutation対Working Tree分離／DeepSeek Empty Directory／Nested Temp Root問題の6件を正確分類） |
| P6-CODEX-001 | CLOSED | Live Judge Integration完全実装・実配線・実Hardware検証済み |
| P6-CODEX-002 | PARTIAL | Repair Eligibility Resolutionは実配線・実検証済み。実New Attempt生成／Phase 4-5再通過／Rejudge／Presented Answer選択はNOT EXECUTED（Controller-owned Followup、理由は§5） |
| P6-CODEX-003 | CLOSED | Safe Refusal Live Presentation（Live経路＋Reload再構築）完全実装・Test済み |
| P6-CODEX-004 | CLOSED | Local Recording Adapter（Atomic Write／Quota／Failure／Git Boundary）完全実装・Test済み |
| P6-CODEX-005 | CLOSED | Four Component Identities（Main／Judge／Guard／Governance Layer）実API・実UI配線済み |
| P6-CODEX-006 | PARTIAL | Calibration／Bias Matrix（Position／Verbosity／Language等）は依然NOT EXECUTED。Live Judgeの実Hardware実行自体は本Rework全体を通じ複数回実証済み（数値的Bias比較Matrixとしては未成立） |
| P6-CODEX-007 | PARTIAL | 実Server／実Model／実BrowserによるGolden Path検証を実施し、その過程で重大なRace Condition（model_busy誤発生）を発見・修正・再検証した。Max New Tokens単独の実UI変更検証、別Tab同期、Mobile-width、Keyboard／Focusは本Reworkでは未実施（§5） |
| P6-CODEX-008 | 本文書 | Acceptance Matrix全数Audit（§2）、Candidate再発行 |

## 2. Acceptance Matrix全数Audit

```text
分類基準:
  PASS             = 本Session（本Rework含む）内の実Evidence（Unit／
                      Integration／Real Model／Real Browser Test）で
                      直接検証済み。
  SAFE_UNSUPPORTED = Frozen Contractが許容するDeepSeek関連の安全な
                      Unsupported状態（Capability 0を正確に申告）。
  NOT_APPLICABLE   = 本Phase 6 Scope外、または該当機能自体が
                      Frozen Designで意図的に不在。
  PARTIAL          = 一部Evidence有り、既知の残Gapを明記。
  NOT_EXECUTED     = 実Evidence0、Controller-owned Followupとして開示。

本Auditは新規に発見された実Bugや実Regressionの有無を優先して再確認した
うえで、既存Recovery Entry群のEvidenceと突合した。全79項目についての
独立した一件ずつのRe-derivationではなく、既存Evidenceとの照合である旨を
明記する（Codex Independent Reviewでの独立再確認を推奨）。
```

### 2.1 Model／Runtime Control

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-001 | PASS | 実Server起動でmain.qwen3-4b-q4-k-mが既定Load（本Rework含め全Golden Path Sessionで実測） |
| P6-ACC-002 | SAFE_UNSUPPORTED | Canonical読取専用Access確認済み、Derived Directory実在（Empty）、Derived File 0（Correction Entry） |
| P6-ACC-003 | NOT_APPLICABLE | V4 Flashは Exact Model Authority Receipt自体でOUT OF SCOPE、本Session中一切Access 0 |
| P6-ACC-004 | PARTIAL | Generic Switch機構は実Hardware検証済み（B-WU-007）。実DeepSeek Round-tripはSAFE_UNSUPPORTEDにより実行不可 |
| P6-ACC-005 | PASS | test_switch_is_rejected_while_a_generation_is_active_idle_only_gate |
| P6-ACC-006 | PASS | test_load_failure_rolls_back/test_double_failure_leaves_runtime_unavailable |
| P6-ACC-007 | PASS | 本Rework Golden Pathで複数Turn連続後もConversation Sidebar／Persistence維持を実測 |
| P6-ACC-008 | PASS | ConversationTurn.request_id相関、PersistentTurnResponse投影で確認 |
| P6-ACC-009 | PASS | 実UIでContext Size 8192→4096実変更・実Reload成功（P6-I-WU-003、本Rework含め複数回実測） |
| P6-ACC-010 | PASS | test_context_change_reload_failure_does_not_adopt_the_requested_size_as_current |
| P6-ACC-011 | PARTIAL | Unit Testでは検証済み。本Rework内での実UI単独操作は未実施（既存Evidenceに依拠） |
| P6-ACC-012 | PASS | test_context_change_above_effective_max_is_rejected_without_touching_the_backend |
| P6-ACC-012A/B | PASS | Exact Model Authority Receipt記載のSymlink境界を全Session通じて遵守（Root外操作0） |

### 2.2 Evaluation／Judge

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-013〜015 | PASS | Domain Contract分離、Deterministic Evaluator Model Call 0（既存6-C Test群） |
| P6-ACC-016 | PASS | test_judge_off_never_calls_the_model（本Rework新規） |
| P6-ACC-017 | PASS | test_judge_hook_receives_the_correlated_request_user_input_and_answer、
  実Browser Golden PathでCanonical Answer不変を実測 |
| P6-ACC-018 | PASS | Hook戻り値不使用の構造的保証、Repair Eligibility解決もJudge=ENFORCE時のみ（自己発見・修正済み） |
| P6-ACC-019 | PASS | test_judge_enforce_also_runs_and_malformed_output_fails_closed |
| P6-ACC-020 | PASS | JudgeIndependenceClass.MAIN_SELF固定、実Browserでも一貫表示確認 |
| P6-ACC-021 | PARTIAL | Prompt Digest等の追跡はDomain Contractに存在するが、Live経路でのRun Evidence永続化は未接続（Recording経路とJudge Runの結合は次Followup） |
| P6-ACC-022 | NOT_EXECUTED | Calibration／Bias Matrix未着手（変更なし、既知のGap） |
| P6-ACC-023 | PASS | test_real_local_judge_smoke.py（既存）＋本Rework Golden Pathでの複数回実Live Judge Run |
| P6-ACC-024 | PASS | Judge Recommendationのみでは何も直接決定しない設計（構造的保証） |
| P6-ACC-024A | PASS | Guard Model／Governance LayerともNoneをNoneのまま返す（P6-CODEX-005） |

### 2.3 Repair

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-025 | PASS | test_judge_observe_never_resolves_repair_eligibility_even_with_needs_repair等、3種のMode独立Test |
| P6-ACC-026 | PASS | Eligibility Resolutionのみでは追加Generation 0（構造的、実Attempt生成が存在しないため） |
| P6-ACC-027 | PARTIAL | Eligibility ResolutionはBudget Checkを含むが実Attempt実行が無いため実行時保証は未実証 |
| P6-ACC-028〜034 | NOT_EXECUTED | 実New Attempt生成が無いため、これらはDomain／Unit Test（Fake）でのみ検証済み。Live実証はP6-CODEX-002残Scope |

### 2.4 Observability／Presentation

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-035 | PASS | JudgeCompletionContext.request_id相関、実Golden Pathで確認 |
| P6-ACC-036〜039 | PASS | 既存status_projection.py Test群（本Rework中回帰0を確認） |
| P6-ACC-040 | PASS | 実Browserで実測（guardrail_reject_input時、Model Call実行前に拒否、実Judge Threadも起動しないことをHook実装のGuardrail Post-check優先順位で保証） |
| P6-ACC-041 | PASS | knownServerMessages 14 Code Mapping、Reload再構築Test 3件（P6-CODEX-003） |
| P6-ACC-042 | PASS | failure_reason_codeはAssistant Message化されない、Client-side合成のみ（同上） |
| P6-ACC-043 | PASS | test_guardrail_reject_persists_failure_reason_code_without_assistant_message、
  detailToMessages Reload Test 3件 |

### 2.5 Feedback／Recording

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-044／044A | PASS | 既存Feedback Domain Test（6-F-WU-004、回帰0確認済み） |
| P6-ACC-045 | PASS | test_recording_off_writes_nothing_even_though_a_root_and_scope_are_configured |
| P6-ACC-046／047 | PASS | SafeRecordingEnvelope既存Test＋本ReworkのReal Write Test（Full Modeで実File内容確認） |
| P6-ACC-048 | PASS | extra="forbid" Envelope、Writerは新規保存経路を追加しない |
| P6-ACC-049 | PASS | test_local_filesystem_recording_writer.py 8 Test（Atomic／Quota／Failure／Restart Recovery／Orphan Prune） |
| P6-ACC-050 | PASS | 全TestはpytestのTmp_pathのみ使用、User実runtime_data接触0 |
| P6-ACC-051 | PASS | .gitignore追加＋git check-ignore実測確認 |

### 2.6 UI／Identity

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-052〜056 | PASS | 実Golden Pathで4 Identity全表示、None／Active区別を実機確認（P6-CODEX-005） |
| P6-ACC-057 | PASS | 実UIでContext／Max Tokens Current／Limit表示（Model Statusパネル、複数回実測） |
| P6-ACC-058 | PARTIAL | Settings再Open実測済み。別Tab同期は本Reworkで未実施（既存6-G-WU-006の同項目もUNVERIFIED） |
| P6-ACC-059〜061 | PASS | 既存6-G Test群、本Rework中回帰0 |
| P6-ACC-062 | PASS | Governance Layerは実際にgovernance_definitions_runtimeから投影、Fake値0 |
| P6-ACC-063 | PASS | Web Response Contract全てextra="forbid"、Secret非露出をP6-I-WU-001で確認、本Reworkでも変更なし |

### 2.7 Compatibility／Experiment

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-064／065 | PASS | 本Rework中Full Suite回帰0を都度確認（1434 passed） |
| P6-ACC-066 | PASS | RAG最終品質判定は引き続き主張していない |
| P6-ACC-067 | PASS | 既存Test群、本Rework中回帰0 |
| P6-ACC-068 | PASS | Public／Basic Test群、本Rework中回帰0確認 |
| P6-ACC-069 | PARTIAL | OFF-mode Baselineのみ既存（6-H）。OBSERVE／ENFORCE比較Matrixは本Reworkでも未実施 |
| P6-ACC-070 | PASS | DeepSeekは一貫してCURRENT_TOOLCHAIN_UNSUPPORTEDと正確申告 |
| P6-ACC-071 | PARTIAL | Latency／Token／Call個別計測はJudge Live Result（confidence／execution_state等）で部分的に可能。分離Metrics Reportとしては未成立 |
| P6-ACC-072 | PASS | 6-Hで実際のFalse Negative事例を捏造せず記録済み（既存） |

### 2.8 Automation／Governance

| ID | 分類 | Evidence |
|---|---|---|
| P6-ACC-073〜075 | PASS | 本Session全体を通じ、Auto-compaction後もRecovery Entry参照で継続、Subphase報告による不要停止0 |
| P6-ACC-076 | PASS | 本文書自体がFalse Completion／Rework／Human介入を正確分類する試み（§4） |
| P6-ACC-077 | PASS | 本Rework中、許可Root外操作0、Network／Homebrew要求0 |
| P6-ACC-077A | PASS | 過去Download例外の再利用0（DeepSeek関連は引き続き封印） |
| P6-ACC-078 | PASS | Stable直書き0、本文書もCorrection Append-only |
| P6-ACC-079 | PASS | 本Reworkは8 CODEX項目＋GOV-001をMaterial Boundary（各1 Recovery Entry）単位で記録、乱造0 |

## 3. Exact Mutation一覧（本Rework全体）

```text
新規Source:
  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
  src/margpa_runtime_llm/adapters/runtime_observability/__init__.py
  src/margpa_runtime_llm/adapters/runtime_observability/local_filesystem_recording_writer.py
  frontend/src/lib/persistentDetailProjection.ts

新規Test:
  tests/unit/bootstrap/test_judge_live_integration.py（9 Test）
  tests/unit/conversation/test_conversation_generation_judge_hook.py（6 Test）
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py（8 Test）
  tests/integration/governance_definitions/test_observe_summary_governance_layer_identity.py（2 Test）
  frontend/src/lib/persistentDetailProjection.test.ts（3 Test）

主要Modified（抜粋、詳細は各P6-CODEX Recovery Entry参照）:
  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
    （JudgeCompletionHook型追加、_completed_event()内の呼び出し順序修正
      ＝本Reworkで発見・修正した最重要Bug）
  src/margpa_runtime_llm/modules/conversation/application/persistent_conversation_service.py
  src/margpa_runtime_llm/modules/conversation/domain/models.py
    （ConversationTurn.failure_reason_code追加、Migration不要）
  src/margpa_runtime_llm/modules/governance_definitions/runtime.py
    （GovernanceObserveSummaryへpackage_id／manifest_digest_sha512追加）
  src/margpa_runtime_llm/modules/runtime_observability/presentation/safe_refusal.py
    （is_safety_reject_code()追加）
  src/margpa_runtime_llm/web/persistent_contracts.py
  src/margpa_runtime_llm/web/runtime_model_control_routes.py
    （Guard／Governance Layer Identity投影追加）
  src/margpa_runtime_llm/web/feature_modes_routes.py
    （Judge Last Result投影追加）
  src/margpa_runtime_llm/web/contracts.py
  src/margpa_runtime_llm/bootstrap/web_application.py
    （Judge Completion Hook、Recording配線）
  src/margpa_runtime_llm/entrypoints/web/main.py（変更なし、既存Flag再利用）
  .gitignore（Recording私的Directory除外）
  frontend/src/App.tsx（detailToMessages抽出、Safe Refusal再構築）
  frontend/src/types.ts、i18n/translations.ts、
  frontend/src/components/RuntimeModelStatusPanel.tsx（4 Identity表示）

Git Mutation: 0（本Rework中も一度もgit add／commit／push未実行）
```

## 4. Live-path Integration（実呼出順序）

```text
実Conversation Generation（Ephemeral／Persistent共通、ConversationGenerationSession）:
  1. Governance Pre-check（既存Phase 4）
  2. Guardrail Pre-check（既存Phase 5）
  3. Model Stream実行（既存Core）
  4. Governance Post-check（既存Phase 4）
  5. Guardrail Post-check（既存Phase 5）
  6. Context Usage計算（既存、_text_token_counter経由でShared Generation Lock使用）
  7. ★Judge Completion Hook（P6-CODEX-001、本Reworkで手順6より後へ移動——
     自己衝突Bug修正）
       a. Judge Mode Check（OFFなら即Return、Model Call 0）
       b. Background Thread起動、Judge Prompt構築、実Model Call
          （max_new_tokens=200、Shared Generation Lock使用）
       c. Fail-closed Decode、Budget Gate
       d. Judge Mode=ENFORCEかつ実行成功時のみ: Repair Eligibility Resolution
          （P6-CODEX-002 partial）
       e. Recording Mode≠OFF時: Local Filesystem Writerへ実Evidence記録
          （P6-CODEX-004）
  8. Completed Event返却（Judge成否に関わらずCanonical Contentは不変）

Guardrail／Governance Reject時（Safe Refusal, P6-CODEX-003）:
  1. Pre-check Reject → Error Event（code=guardrail_*/governance_*）
  2. Persistent層: failure_reason_code永続化（Assistant Message化しない）
  3. Frontend: knownServerMessages経由で固定JA/EN文言表示
     （Live／Reload両経路で同一Mapper使用）
```

## 5. Full／Static／Frontend／Real Model／Real Browser Evidence

```text
Backend Full（最終）: TMPDIR="$PWD/.venv/.t" pytest -p no:cacheprovider
  --basetemp=.venv/.t/f → 1434 passed, 5 deselected in 63.42s
Ruff: All checks passed!
Mypy: Success: no issues found in 430 source files
Frontend: typecheck PASS／lint PASS（Warning 0）／
  Test Files 23 passed (23) / Tests 191 passed (191)／build PASS
  （P6-CODEX-003時点の最終計測。本Rework後半のFrontend変更は無いため
  数値は据え置き、Backend側の回帰は都度1434まで再確認済み）

Real Model／Real Browser（本Rework、Project-local Temp Root使用）:
  1. Judge Live Integration: 実Qwen3-4Bを用いた複数回のReal Chat + Real
     Judge Call、Feature Modes Status APIでの実Result確認（recommendation=
     accept, confidence=0.95等）。
  2. 4 Component Identity: 実Server（--phase-6-runtime-model-control）で
     Main／Judge／Guard／Governance Layer全表示を実機確認。
  3. Safe Refusal: Guardrail Enforce実適用（Configuration Control経由の
     実CAS Apply）＋実Injection Prompt送信でBlockを確認
     （P6-I-WU-003より継続）。
  4. ★Critical Fix検証: model_busy Race Conditionを実際に3回再現し、
     修正後は同一操作（Judge=observe中の連続実Message送信）を3／3件
     成功させたことを実機確認。
  5. Recording: Judge Live Integration経由でRecording Mode=FULL時に実File
     （request_id.json、Canonical Input／Presented Answer含む）が実際に
     書き込まれることを確認（Unit Test内、tmp_path使用）。
```

## 6. Recording Path／Git Ignore／Quota／Failure Evidence

```text
Recording Path: runtime_data/persistent/<Recording独自Hashed Scope>/evaluations/
  <request_id>.json（Atomic Rename、Restart後も既存File可視）
Git Ignore: .gitignoreへ4 Pattern追加、git check-ignoreで実File除外を確認
Quota: LocalFilesystemRecordingWriter(max_total_bytes=...)で総Byte数超過時
  RecordingQuotaExceededをRaise、Partial File 0（Test 3件で直接検証）
Failure: 書込不可Directory（chmod読取専用化）でRecordingWriteFailureを
  正しくRaiseすることをTestで直接検証、Orphan Temp Fileの次回Write時
  自動Pruneも確認
```

## 7. Manual Acceptance可能項目

```text
Acceptance Matrix §9の10項目中、本Reworkにより新たに実行可能となった項目:
  1. Qwen Default起動: 元々可能。
  3. Context Size変更とServer継続: 可能（P6-I-WU-003より継続、本Reworkでも再確認）。
  4. Max New Tokens変更と次Generation反映: UI操作自体は可能（実Applyの
     Call Spy付き単独検証は本Reworkでは未実施、既存Unit Testに依拠）。
  5. Main／Guard／Judge／Governance Layer表示: 可能（本Rework新規）。
  7. Guardrail Safe Refusal: 可能（Live＋Reload両方、本Rework新規）。
  8. Request単位Status: 部分的に可能（Guardrail Pointの実State遷移は
     P6-I-WU-003で確認済み、Judge独自のRequest Status表示は
     Feature Modes Status API経由でのみ、専用UI Widgetは無し）。
  9. Judge OBSERVEとRepair ENFORCEの有界Golden Path: **部分的に可能**。
     Judge OBSERVEは完全に実行可能（本Rework最重要成果）。Repair ENFORCEは
     Eligibility Resolutionまでは実行・観測可能（Feature Modes Statusの
     repair_eligibility Field）だが、実際にRepairが新しいAttemptを生成する
     Golden Pathは未実装のため、「有界」を実証する対象自体が存在しない。
  10. Mode OFF復帰、再Open、Browser Reload、Conversation／Citation維持:
     Mode OFF復帰・再Open・Reloadは可能（本Rework新規実測）。別Tab同期は
     未検証。Citation維持はRAG機能自体を本Reworkでは検証していない。

項目2（DeepSeek切替）・6（Phase番号なしUI、既存確認済み）は変更なし。
```

## 8. Open Major Finding

```text
1. 【本Reworkで発見・修正済み、記録として残す】Judge Live Integrationの
   Background Thread実行が、同一TurnのContext Usage Token Counterおよび
   後続Turnの実Generationと、共有Single-context Model Adapterの
   Generation Lockを巡って競合し、実際のChat Messageがmodel_busyへ
   誤って失敗する重大なRegressionが存在した。Root Cause特定・修正・
   実Hardware再検証まで完了（§本文Recovery Entry参照）。修正後も
   Cross-turn（別Turn同士の）Collisionは理論上残る（Retryableとして
   処理可能、根絶には別Design要、Controller-owned Followup）。
2. 【未解消、Controller-owned Followup】P6-CODEX-002の実New Attempt
   生成（Phase 4/5全Point再通過、Rejudge、Presented Answer選択）は、
   Persistent Store MutationをBackground Threadから安全に行う設計が
   本Reworkの時間内で確立できなかったため、意図的に実装しなかった。
3. 【未解消、Backlog継続】P6-CODEX-006 Calibration／Bias Matrix
   （Position／Verbosity／Language／Self-preference／Confidence／
   Deterministic Conflict）、およびQwen OBSERVE/ENFORCE Mode比較Matrix
   は本Reworkでも未着手。
4. 【未解消、範囲外】Settings別Tab同期、Mobile-width、Keyboard／Focus
   Interactive検証（6-G-WU-006由来）は本Reworkでも未実施。
```

## 9. False Completion Self-check

```text
本文書のいかなる記述も「未実測をPASSと主張」していない。§2のPARTIAL／
NOT_EXECUTED分類は、それぞれ具体的な残Gapを明記した。§8のOpen Major
Findingは4件とも実在する未解消事項であり、0件と偽っていない。
P6-CODEX-002／006／007の一部が引き続きPARTIALであることを踏まえ、
本文書は「Phase 6 COMPLETE_CANDIDATE」ではなく「Rework Complete
Candidate」として提出する——Codex Independent ReviewおよびUser Mac
Acceptanceにおいて、残る3件のPARTIAL項目（Repair実Attempt生成、
Calibration Matrix、一部UI Interactive検証）の要否・優先度を
改めて判断されたい。
```

## 10. Governance Incidentの正確な分類

```text
本Rework中のGovernance Incident: 0件（新規）。
本Rework中に実施した2回のDebug Trace挿入（conversation_generation.py／
adapter.pyへの一時的なprint文追加）は、Root Cause特定のための最小限の
診断行為であり、Authorized Project Root内のSource変更（Allowed Mutation
Envelopeの範囲内）である。Debug Trace自体は最終的に全て削除し、Full Suite
再実行でClean状態を確認した。Root外操作・Network・Homebrew要求は本Rework
中0件。P6-GOV-001で分類した3件（Root Boundary Violation、Pre-authority
Access、Unnecessary Escalation）は前Session由来であり、本Reworkでの新規
発生ではない。
```

## Next Exact Route

```text
本文書の提出をもって、Frozen Handoff §9のStop Condition
「Phase 7／8／10以降を実装しなければPhase 6が成立しない重大衝突」には
該当しないが、本Rework Handoff自体の指示（「Rework Candidate Handoffまで
自走し、そこで停止する」）に従い、ここで停止する。Phase 6-J、Git、
Phase 7へは進まない。次のCodex Independent Reviewにて、§8 Open Major
Finding 4件（うち1件は既に修正済みだが記録として残置）の要否判断を
仰ぐ。
```
