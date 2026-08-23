# Phase 6 Codex Independent Review Rework Handoff

```yaml
document_id: phase_6_codex_independent_review_rework_handoff_20260823052052
status: adjust_required
phase: phase_6
from: プロジェクト責任者兼設計統括者役
to: Claude側設計統括者役
created_at: 2026-08-23 05:20:52 JST
source_candidate: phase_6_claude_complete_candidate_handoff_ja.md
closure_state: do_not_close
human_decision_required_before_rework: false
```

## 1. Controller Decision

`phase_6_claude_complete_candidate_handoff_ja.md`は、Phase 6の
`COMPLETE_CANDIDATE`として受理しない。判定は`ADJUST_REQUIRED`である。

理由は、同Handoffが未実装／未検証と申告した項目のうち、次がFrozen Phase 6
Execution PlanおよびAcceptance Matrixの必須Work Unitだからである。

- Judgeの実Conversation Generation Path配線。
- Bounded RepairのNew Attempt、Phase 4／5再通過、Rejudge、Presented Answer選択。
- Safe Refusalの実Presentation／Persistence／Context分離。
- RecordingのLocal Writer、Atomic Write、Quota、Failure／Degraded、Git除外。
- Current Guardrail Model／Current Governance Layerを含む4種Identityの実API／UI投影。
- Calibration／Bias Matrix、Qwen Mode比較、Judge／Repair効果、分離Metric。
- Acceptance Matrix全数Auditおよび実行可能なReal Browser Golden Path。

これらを`Controller-owned Followup`、`Backlog`またはPhase 7以降へ移す権限は、
今回のClaude Execution Contractにはない。Phase 6-Jは不足実装を肩代わりする工程ではなく、
Independent Review／局所Rework／User Acceptance／Closureの工程である。

DeepSeekの`CURRENT_TOOLCHAIN_UNSUPPORTED／NOT EXECUTED`は、現行Tool Revisionに
対するSafe Unsupportedとして許容できる。新たなHomebrew変更、HF Hub照会、Network拡張を
本Reworkの成立条件にはしない。恒久Unsupportedとは断定しない。

## 2. Independent Evidence

### 2.1 Source／UI実体

以下を独立照合した。

- `ConversationGenerationService`／Persistent Streaming／Bootstrapに、Judge、Repair、
  Recording Serviceおよび`render_safe_refusal()`のLive-path Callが存在しない。
- `JudgeModeController`、`RepairModeController`、`RecordingModeController`は、現時点では
  Mode status／toggleへだけ配線されている。
- `runtime_model_control_routes.py`はMain／JudgeだけをResponseへ投影し、Guard／Governance
  Layerを公開しない。
- `RuntimeModelStatusPanel.tsx`もMain／Judgeの2 Rowだけを表示する。
- `featureModesNote`自身が「Modeを切り替えるだけでConversationへの実際の介入は別途接続が必要」
  と明記している。
- 通常ChatはGuardrail Reject時にRaw Code `guardrail_reject_input`を既存Error表示へ渡し、
  `safe_refusal.py`の固定JA／EN文言を使わない。

### 2.2 Validation

Project-localかつ短いTemporary Rootを使い、次を独立実行した。

```text
Backend Full:
  TMPDIR="$PWD/.venv/.t" ./.venv/bin/python -m pytest \
    -p no:cacheprovider --basetemp=.venv/.t/f
  1405 passed, 5 deselected in 61.77s

Ruff:
  All checks passed

Mypy:
  Success: no issues found in 423 source files

Frontend:
  typecheck PASS
  lint PASS
  22 files / 187 tests PASS
  build PASS
```

より深いProject-local Root
`.venv/.tmp/codex_phase6_review/pytest_full`では、SQLite staging pathが長くなり、
Migration系9件が`sqlite3.OperationalError: unable to open database file`で失敗した。
`.venv/.t/f`へ短縮すると全件PASSしたため、Product Regressionとは分類しない。
今後のCanonical Full Testは短いProject-local Temporary Rootを明示し、OS Temporaryへ
逃がさないこと。

### 2.3 Evidence／Boundaryの不整合

Candidate Handoffには次の事実不整合がある。

1. `Governance Incidents: 0`としながら、同文書自身が
   `/private/tmp/claude-501/.../scratchpad/golden_path_runtime_data`へのWriteを申告する。
   Phase 6 GovernanceはProject-local Test Temporary Rootを要求しており、これは
   `SELF_REPORTED_ROOT_BOUNDARY_VIOLATION`である。
2. Dependency Authority Receipt成立前のRecovery Entryが、
   `/opt/homebrew/bin/convert_hf_to_gguf.py`および関連Toolの確認を申告する。
   後発Receiptは過去Accessを遡及承認しない。少なくとも
   `SELF_REPORTED_PRE_AUTHORITY_ROOT_OUTSIDE_READ_OR_EXECUTE`として記録する。
3. Session前半の不要なUser確認は、`Governance Incident 0`と両立しない。
   `AUTOMATION_UNNECESSARY_ESCALATION`として記録する。
4. `Git Mutation 0`は成立し得るが、Working Treeは多数のTracked変更／Untracked追加を含み、
   `Working Tree Clean維持`は事実と異なる。両者を分離して訂正する。
5. `models/main/deepseek-r1-0528-qwen3-8b/`には、空の`gguf/`、
   `conversion_work/`、`manifests/` Directoryが実在する。
   「Derived未作成」「Write-only-new-create領域への書き込み実績0」は不正確である。
   `EMPTY_DIRECTORY_CREATED／DERIVED_FILE_0`へ訂正する。削除・移動は行わない。

Root外Artifactは本Reworkのために再確認、削除、移動または修復してはならない。
Repository内の自己申告Evidenceだけを根拠にAppend-only Correctionを作成する。

## 3. Required Rework

### P6-CODEX-001 — Live Evaluation／Judge Integration

Frozen ArchitectureのMode契約を通常ChatとPersistent Chatの実Generation Flowへ配線する。

- Judge OFF：Judge Adapter build／call／mutation 0。
- Judge OBSERVE：実評価を行うがCanonical Answer、SSE、Conversation Persistenceを変更しない。
- Judge ENFORCE：Typed RecommendationをRepair Eligibilityへ渡せるが、Judge単独で
  Safety／Authority／Canonical Completionを決定しない。
- 実行ごとにRequest／Turn／Generation／Evaluation Runを相関し、過去Requestを混在させない。
- Main-self JudgeはIndependentと表示しない。
- Unavailable／Malformed／Timeout／Budget超過をFail-closedのTyped Stateへ正規化する。
- Public／Basic／既存v1の新規Call／Writeを0のまま維持する。

Unitだけでなく、実Conversation Generationを通るCall Spy／SSE／Store／Web Integration Testを
追加する。

### P6-CODEX-002 — Bounded Repair Live Orchestration

`execute_repair_plan()`を実Conversationへ接続する。

- Repair OFF／OBSERVEでは追加Generation 0。
- ENFORCEはJudge Recommendation、Repair Mode、Authority、Capability、Budgetが全て成立した場合だけ。
- Originalを上書きせず、新しいGeneration／Attempt Identityを作る。
- CandidateはPhase 4 Main GovernanceおよびPhase 5 Guardrailの全対象Pointを再通過する。
- Rejudge後、同CriteriaによるBefore／After比較でImprovedだけを採用候補にする。
- Worse／Unknown／FailureをSuccessへ昇格しない。
- Attempt／Depth／Call／Token／Wall Time／Cancelを有界化する。
- Commit-before-completed、Terminal一意、Ghost Completion 0、Hidden Original通常保存0を守る。
- Persistent Retry／Regenerate／Branch／Citationを破壊しない。

### P6-CODEX-003 — Safe Refusal Live Presentation

`render_safe_refusal()`または同等の単一Safe Presentation Mapperを、実Guardrail Reject経路へ配線する。

- 通常UIへ`Error: guardrail_reject_input`その他Raw Internal Codeを表示しない。
- User Languageに応じた固定JA／EN安全拒否を表示する。
- Model Call 0を維持する。
- Safe RefusalをAssistant Message／Assistant Authority／次Generation Contextへ混入させない。
- Persistent ConversationではReload／Resume後にもTyped拒否表示を再構築する。
- Internal codeはDeveloper Detailと通常Presentationを分離する。

### P6-CODEX-004 — Local Recording Adapter／Git Boundary

Frozen Recording Architectureどおり、既存`runtime_data`論理RootへLocal-only Writerを実装し、
Live Generation／Evaluation／Repairから使用可能にする。

- `runtime_data/persistent/<scope>/{evaluations,experiments,evidence,feedback}/`
  および必要なDerived／Recovery境界を用いる。
- OFFはWriter build／call／write 0。
- METADATAはAllowlist Metadata／Digest／Metricだけ。
- FULLもCanonical Input、Presented Answer、Typed Resultだけを許可する。
- Raw Thinking、System Prompt、Secret、RAG Internal Context、Tool内部、Hidden Original、
  未確定Partial Outputを保存しない。
- Atomic Write、Quota、Write Failure、Degraded／Fail-closed、Restart Recoveryを検証する。
- Private Evaluation／Experiment／Feedback／EvidenceがGit Stage対象外であることを、
  `.gitignore`、`git check-ignore`、`git ls-files`で確認する。
- User実`runtime_data`をTest／Migration／読取対象にしない。Testは短いProject-local Fixtureだけを使う。

### P6-CODEX-005 — Four Component Identities

Server Canonical Snapshotから次の4 Rowを別々に投影し、Advanced UIへ表示する。

1. Current Main Model
2. Current Guardrail Model
3. Current LLM-as-a-Judge Model
4. Current Governance Layer

Guard Model `None`とGuardrail Mode OFFを混同しない。Governance LayerはDirectory名ではなく、
Manifest／Digest／Runtime Bindingから導出する。None／Unavailable／Invalid／Loading／Degraded／Activeを
捏造せず区別する。Requested CandidateをCurrentへ昇格しない。

### P6-CODEX-006 — Calibration／Mode Comparison／Metrics

Frozen P6-D-WU-004およびP6-H-WU-001〜005を完了する。

- Position、Verbosity、Language、Self-preference、Confidence、Deterministic Conflictの
  Calibration／Bias Matrix。
- QwenでGovernance／Guardrail／Judge／RepairのOFF／OBSERVE／ENFORCE比較。
- Judge／RepairによるAccuracy Candidate、Unsupported Claim、Definition Confusion、Abstention、
  Over-refusal、Repair Improved／Worseの比較。
- Token、Latency、Model Call、Repair回数、Recording Byteを分離計測する。
- Dataset、Model、Role、Mode、Definition、Rubric、Budget、Run DigestをFreezeし再現可能にする。
- DeepSeekは現行Safe UnsupportedならCall 0＋Reasonでよく、Supportedを捏造しない。

### P6-CODEX-007 — Production Controls／Golden Path

- Max New Tokensを実Production UIから変更し、Model Reload 0かつ次Generationへの反映を
  Call Spyと実Browserで確認する。
- Settings再Open、Reload、別Tab、CAS Conflict、ja／en、Keyboard、Focus、Mobile-width、
  No-secret Projectionを確認する。
- Manual Acceptance項目9「Judge OBSERVEとRepair ENFORCEの有界Golden Path」を
  実行可能な状態へする。
- Main／Guard／Judge／Governance Identity、Safe Refusal、Request Status、Mode OFF復帰、
  Conversation／Citation Recoveryを同じ実Server Golden Pathで確認する。

### P6-GOV-001 — Append-only Governance／Evidence Correction

既存HistoryとCandidate Handoffを上書きせず、Phase 6 Historyへ新規Correctionを作成する。

最低限、次を事実どおり分類する。

- Root-outside `/private/tmp` Write：`SELF_REPORTED_ROOT_BOUNDARY_VIOLATION`。
- Receipt前の`/opt/homebrew`確認：`SELF_REPORTED_PRE_AUTHORITY_ACCESS`。
- 不要なUser確認：`AUTOMATION_UNNECESSARY_ESCALATION`。
- Git Mutation 0とWorking Tree Dirtyを分離。
- DeepSeek empty derived directories created、derived file 0。
- Nested Project-local Test Rootでの9 failureと、短いProject-local Rootでの1405 PASS。

これらを0件へ再分類したり、過去Receiptで遡及承認したりしない。Root外を再検査しない。

### P6-CODEX-008 — Acceptance Matrix全数Audit／Candidate再発行

全Acceptance IDを1件ずつ、`PASS／SAFE_UNSUPPORTED／NOT_APPLICABLE／FAIL`へ分類し、
Evidence Pathと実行Class（Unit／Integration／Static／Real Model／Real Browser）を添える。

- `UNVERIFIED`、`NOT EXECUTED`、既知の必須`PARTIAL`を残したまま
  `COMPLETE_CANDIDATE`を再発行しない。
- Deferredが許されるのは、Frozen Contract自身が条件付きDeferralを定義した項目だけ。
- 新CandidateではOpen Major Finding 0、Technical ScopeのController-owned unfinished work 0、
  Manual Acceptanceが実行可能であることを確認する。
- Working Tree状態、Mutation境界、DeepSeek Artifact状態、Governance Incident数を
  実測／自己申告Classに沿って正確に記載する。

## 4. Allowed Mutation Envelope

本Reworkは既に承認されたFrozen Phase 6 Scope内であり、新しいHuman仕様判断は不要である。
Claude側設計統括者役は必要なTask分解、設計者兼実装者相当の実行、再Reviewを自律的に行う。

許可対象：

- Phase 6対象の`src/margpa_runtime_llm/`内Source／Adapter／Bootstrap／Web。
- Phase 6対象の`frontend/`および生成済み`src/margpa_runtime_llm/web/static/`。
- Phase 6対象の`tests/`。
- Private Runtime Data除外に必要な`.gitignore`。
- Phase 6 `history/index/`、`history/operations/`、`handoffs/`への新規Append-only Evidence。
- 既存Project-local `.venv`と短いProject-local Test Temporary Rootの利用。

禁止対象：

- Authorized Project Root外のRead／Write／Execute／Delete／Move／Repair。
- Provider Memory、`.claude`、`.codex`その他Repository外Memoryへの保存。
- User実`runtime_data`のRead／Write／Migration。
- DeepSeek／Qwen Canonical Artifactの変更・削除・移動。
- DeepSeek empty derived directoryの削除・再作成・内容追加。
- 新規Network、Homebrew、Global／System Package変更。
- Stable Current Docs、Roadmap、Phase Indexの直接更新。
- Git add／commit／push／tag／branch／stash／reset／checkout等のGit Mutation。
- Phase 7以降の実装。

必要な新Source／Test PathはFrozen責務内で動的に決めてよい。既存Docsへの上書きではなく、
From／Toを持つ新規Index／Handoff／Statusを作る通常のDocs運用を守る。

## 5. Validation Contract

Rework完了時に最低限、次を実行する。

```text
Backend focused integration:
  Live Judge／Repair／Recording／Safe Refusal／Identity／Persistent／Public-Basic Call-0

Backend full:
  TMPDIR="$PWD/.venv/.t" ./.venv/bin/python -m pytest \
    -p no:cacheprovider --basetemp=.venv/.t/f

Static:
  ./.venv/bin/ruff check src tests scripts
  ./.venv/bin/mypy

Frontend:
  npm run typecheck --prefix frontend
  npm run lint --prefix frontend
  npm test --prefix frontend -- --run
  npm run build --prefix frontend

Boundary:
  Public／Basic／v1の追加Judge／Repair／Recorder Call 0
  User実runtime_data Read／Write 0
  Root外Action 0（本Rework開始後）
  Git Mutation 0
  Protected Capture 0
  DeepSeek Canonical／Derived Mutation 0
```

Full Test用Temporary Rootは短いProject-local Pathへ固定し、`/tmp`、`/private/tmp`、
Claude Scratchpadその他Root外を使わない。Test Temporary Artifactは`.venv`配下へ隔離する。

## 6. Return Contract

Rework後、次の2文書を新規作成して停止する。

1. Phase 6 Governance／Evidence Correction。
2. Phase 6 Claude Rework Complete Candidate Handoff。

Rework Candidate Handoffには次を含める。

- P6-CODEX-001〜008／P6-GOV-001のClose Matrix。
- 全Acceptance ID Audit。
- Exact Mutation一覧。
- Live-path Integration図または明確な呼出順序。
- Full／Static／Frontend／Real Model／Real Browser Evidence。
- Recording Path／Git Ignore／Quota／Failure Evidence。
- Manual Acceptance可能項目。
- Open Major Finding。
- False Completion Self-check。
- Governance Incidentの正確な分類。

`Open Major Finding: NONE`かつ全必須Acceptanceが
`PASS`またはContract上正当な`SAFE_UNSUPPORTED`にならない限り、
`COMPLETE_CANDIDATE`を宣言しない。

本Handoff受領後、個別Reworkごとの進捗報告では停止しない。真のStop Conditionがなければ、
全Rework、全Validation、Self-review、Candidate Handoffまで自走し、そこで停止する。
