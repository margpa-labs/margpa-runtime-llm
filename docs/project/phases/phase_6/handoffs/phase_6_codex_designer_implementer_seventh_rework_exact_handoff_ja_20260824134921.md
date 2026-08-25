# Phase 6 Seventh Rework — Codex設計者兼実装者役 Exact Handoff

```yaml
document_id: phase_6_codex_designer_implementer_seventh_rework_exact_handoff
status: exact_execution_authority_active
phase: phase_6
rework: seventh_rework_user_ui_runtime_model_semantic_enforcement
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-24 13:49:21 JST
implementation_authority: true_within_this_handoff
phase_closure_authority: false
git_mutation_authority: false
network_authority: false
automation_mode: long_run_until_complete_candidate
```

## 1. Objective

P6-GOV-010／011のUser Mac Manual EvidenceとUser確定要件を正本として、Phase 6のUI、Runtime Model
Control、Judge／Repair／ENFORCE、Current Local Qwen／DeepSeek経路を修正し、独立Review可能な
`COMPLETE_CANDIDATE`まで連結実行する。

Package境界の進捗報告は停止理由ではない。Recovery Entryを作った後、そのまま次Packageへ進む。
真のStop Condition以外でUser／Controllerへ確認を返さない。

## 2. Mandatory Reading Order

次を省略せず全文読む。

1. `docs/project/phases/phase_6/history/operations/phase_6_gov010_user_mac_manual_acceptance_and_codex_implementation_failure_ja_20260823232403.md`
2. `docs/project/phases/phase_6/history/operations/phase_6_gov011_user_ui_runtime_model_and_semantic_enforcement_rework_scope_ja_20260824134921.md`
3. 本Handoff。
4. `docs/project/phases/phase_6/phase_index_ja.md`
5. `docs/project/phases/phase_6/requirements/phase_6_requirements_ja.md`
6. `docs/project/phases/phase_6/architecture/phase_6_architecture_ja.md`
7. `docs/project/phases/phase_6/adr/phase_6_adr_ja.md`
8. `docs/project/phases/phase_6/operations/phase_6_execution_plan_ja.md`
9. `docs/project/phases/phase_6/operations/phase_6_acceptance_matrix_ja.md`
10. `docs/project/phases/phase_6/handoffs/phase_6_codex_designer_implementer_sixth_rework_complete_candidate_handoff_ja_20260823223405.md`
11. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_b_deepseek_multiturn_ja_20260823205724.md`
12. `docs/project/phases/phase_6/history/index/phase_6_fifth_rework_package_d_final_verification_ja_20260823222047.md`

その後、Current Source／Test／Model Definitionを憶測ではなく直接照合する。

## 3. Authority／Boundary

### 3.1 Authorized Root

```text
/Users/Nazuna Research/Documents/pseudo_root/99_ps_Main_Creating_Objects専用_20260219/
  MARGPA-RUNTIME-LLM/margpa-runtime-llm/
```

### 3.2 Allowed Mutation

- Phase 6修正に直接必要な`src/`、`frontend/src/`、`tests/`、`frontend` Test、Tracked Model Definition／
  Local Profileの最小変更。
- Phase 6の新規Append-only Recovery／Evidence／Handoff。
- Project内Task-owned Temporary。`.venv/.t/phase_6_seventh_rework_<timestamp>/`等へ隔離する。

### 3.3 Read／Load-only Model Exception

既にUserが例外承認した`models/` SymlinkのResolved Target内に限り、現Qwen／DeepSeek Artifactを
Read／Load／Inference Testしてよい。Weight、GGUF、Tokenizer、Manifest、Conversion Artifactを変更、移動、
削除、再Download、再量子化してはならない。

### 3.4 Forbidden

- Authorized Root外Read／Write／Enumeration。`/dev/null`を含む。
- `.claude`、`.codex`、Provider MemoryのRead／Write／Semantic利用。
- User `runtime_data/`のRead／Write。Test DataはTask-owned Temporaryだけを使う。
- Git add／commit／push／branch／reset／cleanその他Git Mutation。
- Network、Dependency Install、Homebrew、AWS、Lightning、外部Service。
- `definitions/` CorpusのSemantic Mutation。
- Phase 7、Roadmap、Phase 6 Closure、Backup。
- Controllerが作成した既存Untracked
  `docs/project/shared/history/planned_work/phase_7_web_retrieval_data_controls_and_data_source_scope_reservation_ja_20260824130432.md`
  の変更／削除／Stage。

Root親Directoryの一覧化は不要である。作業開始時は`pwd`とExact Root比較、以後はExact Pathを使う。

## 4. Working Rules

1. `Unresolved != Blocker`。Current Transitionに直接必要で、自権限で解決不能、安全性・完全性・
   可逆性・Authorityを破壊するものだけ停止する。
2. 自権限内の不具合は自ら修正し、Evidenceを付ける。Userへ設計者の職務を返さない。
3. Historical Failureを、新EvidenceなしにCurrent Blockerへ再活性化しない。
4. `0`、`PASS`、`Regression 0`は観測範囲とMethodを併記する。未観測を0へしない。
5. Test大量PASSをUser Acceptanceの代替にしない。
6. Compaction／Provider Limitへ備え、各Package完了時に`history/index/`へRecovery Entryを作る。
7. Recovery Entry作成後に停止せず次Packageへ進む。
8. Existing User Changesを保持する。自Task外のDirtyを修正、削除、Stageしない。

## 5. Work Packages

### Package A — Authority／As-built／Reproduction

- Mandatory Readingを完了し、Current Diff、Running Process、Task-owned Temporary、対象Source／Testを照合。
- P6-GOV-010／011の各Failureを自動Testまたは実Runtimeで再現し、再現不能ならEvidence Gradeを記録。
- UI FieldのSource of Truth、Runtime Snapshot、Model Definition Capability、Judge／Repair Data Flowを図示可能な
  一覧にする。
- Recovery Entryを作り、Package Bへ継続。

### Package B — UI Consolidation／Immediate Mode Apply

- P6-GOV-011 §2〜4を実装する。
- ModeはClick即時Mutation。成功／Conflict／Failure／連打／別Tab／ReloadでCanonical Stateへ収束。
- Advanced旧Model／Context、Basic旧Max New Tokens、Model Switch横の重複Context入力を整理。
- Research ModeをAdvanced最下部へ移動。
- 利用者向けFeature名からPhase Suffixを付けない。Layoutを崩さない。
- Frontend Component／API／Interaction Testを追加。
- Recovery Entryを作り、Package Cへ継続。

### Package C — Current Runtime Identity Projection

- Sidebar、Advanced、Environment／Current ComponentのCurrent Model表示を同一Runtime Snapshotへ統一。
- Configured Startup DefaultとCurrent Loaded Modelを型・Label・APIで分離。
- Model Switch、Switch Failure Rollback、Reload、二Tab更新をTest。
- `main_self` Judgeの実Model KeyとIndependence Classを表示し、専用Judge Artifact未設定と区別。
- Recovery Entryを作り、Package Dへ継続。

### Package D — Context／Max New Tokens Capability Contract

- Qwen 32768／DeepSeek 131072表示と実適用失敗の原因を直接特定。
- Native／Backend／Hardware／Effective Maximumを分離。入力上限はEffective Maximumへ固定。
- 実際に表示最大値を適用できるか、適用不能なら安全なEffective上限とTyped Reasonを表示する。
- Max New Tokens Default 2048維持、Model別Upper Limit、残Contextとの制約、Switch時の収束を実装。
- 最大、最大-1、最小、範囲外、Busy、CAS Conflict、Load Failure、Rollback、再起動をTest。
- Recovery Entryを作り、Package Eへ継続。

### Package E — Judge／Repair／Semantic ENFORCE

- Judge Prompt／Output Decoder／Evaluation Orchestrator／Repair Router／Presented Final境界を再設計・修正。
- ReferenceなしのUser Correction矛盾、Premise逸脱、Unsupported Assertionを評価する。
- RAG／Citation Evidenceがある時はEvidence contradictionを入力へ含める。
- Local Qwen／DeepSeekのJSON出力差を安全に扱う。ParserはSchemaを緩めて意味を捏造してはならない。
- Judge FailureをPASSへせず、ENFORCEではKnown Failed CandidateをPresented Finalへ通さない。
- Repair Budget、Rejudge、Terminal State、Safe User-facing FallbackをTest。
- OFF／OBSERVE／ENFORCEの差を実証する。
- 既に接続済み機能を将来形で説明する古いUI Copyを修正する。Semantic Rule Deferredとの差は正確に残す。
- Recovery Entryを作り、Package Fへ継続。

### Package F — Qwen／DeepSeek Real Runtime

- QwenのEvidence無視／訂正無視をJudge→Repair／Safe Finalで止めるGolden Pathを実Modelで検証。
- DeepSeekの病的反復をChat Template、EOS、Stop、Sampling、Raw Token単位で切り分ける。
- Fix可能ならProject Source／Tracked Definitionだけで修正する。Model Artifact自体は変更しない。
- Fix不能なら反復を有界検出して停止し、Safe Unavailable／Rollbackへ収束させる。
- Qwen Default、Qwen→DeepSeek→Qwen、会話／Citation／Branch、二Tab、Restartを回帰確認。
- CPU／Metalは実測したものだけを主張し、普通Terminal Metal未確認をPASSへしない。
- Recovery Entryを作り、Package Gへ継続。

### Package G — Integrated Verification／Return

- Acceptance §6を全件、ID別に再導出。
- Backend Full、Canonical Mypy、Ruff Format／Check、Frontend Typecheck／Lint／Test／Buildを実行。
- Relevant Real Model／Browser Matrixを実行。User Mac固有の目視項目はUser GateとしてExact List化。
- Open Critical／Majorが0の場合だけCOMPLETE_CANDIDATEとする。
- Completion RecoveryとDirect Return Handoffを作成し、Phase Closureへ進まずControllerへ返す。

## 6. Exact Acceptance Contract

### UI／State

- `P6-RW7-UI-001`: 全Mode Selectorで独立Apply Buttonが存在せず、選択Clickが一回のMutationを発行する。
- `P6-RW7-UI-002`: Failure／Conflict／Response順序逆転でも表示とServer Canonical Stateが乖離しない。
- `P6-RW7-UI-003`: Advanced旧Model／Context、Basic旧Max New Tokens、Switch横の重複Context入力が消え、
  LayoutとKeyboard操作が維持される。
- `P6-RW7-UI-004`: Research ModeがAdvanced最下部にあり、Click即時適用される。
- `P6-RW7-UI-005`: Current ModelがSidebar／Advanced／Environmentで一致し、Switch／Reload／二Tabで追随する。
- `P6-RW7-UI-006`: 利用者向けFeature名に`（Phase N）`を付けず、説明はCurrent Capabilityを示す。

### Runtime Model／Capability

- `P6-RW7-MDL-001`: Startup Qwen DefaultとCurrent Runtime Modelが分離され、再起動後Qwenへ戻る。
- `P6-RW7-MDL-002`: Qwen／DeepSeekのNative MaxとEffective Maxが分離され、入力上限表示は実適用可能。
- `P6-RW7-MDL-003`: Context最大／境界／範囲外／Busy／RollbackがModel別に決定的。
- `P6-RW7-MDL-004`: Max New Tokens Default 2048、Model別Upper Limit、残Context制約が成立する。
- `P6-RW7-MDL-005`: DeepSeek病的反復が正常化、または有界停止＋Safe Unavailableへ収束する。

### Judge／Repair／Enforcement

- `P6-RW7-JDG-001`: main_self Judge IdentityがCurrent Model KeyとIndependence Class付きで表示される。
- `P6-RW7-JDG-002`: Qwen／DeepSeekの許容可能なStructured OutputをDecoderが読め、MalformedをPASSへしない。
- `P6-RW7-JDG-003`: ReferenceなしでUser Correction矛盾／Premise逸脱／根拠なき断定を評価できる。
- `P6-RW7-JDG-004`: Citation Evidence contradictionがJudgeへ到達する。
- `P6-RW7-JDG-005`: Judge Failureは画面へ正確に出て、Repair Successを捏造しない。
- `P6-RW7-JDG-006`: ENFORCEではKnown Failed CandidateをFinalへ通さず、Bounded RepairまたはSafe Finalへ収束。
- `P6-RW7-JDG-007`: OBSERVEはCandidateを変更せずEvidenceを表示、OFFは追加Action 0。
- `P6-RW7-JDG-008`: Repair LoopにBudgetとTerminal保証があり、無限反復しない。

### Regression／Evidence

- `P6-RW7-REG-001`: Conversation／Citation／Branch／Regenerate／二Tab／Reloadが維持される。
- `P6-RW7-REG-002`: RecordingのTurn／Judge EvidenceがMode契約どおり記録される。
- `P6-RW7-REG-003`: Backend／Frontend Canonical ValidationがPASSし、既存Testの削除／弱体化0。
- `P6-RW7-REG-004`: Project Root外、Provider Memory、User Runtime Data、Git、NetworkのForbidden Action 0を
  実行Logに基づき報告する。推測による0主張は禁止。

## 7. True Stop Conditions

次の場合だけ停止する。

1. Authorized Root外Action／Provider Memory／User runtime_data接触が発生した。
2. Weight／Artifact Mutation、Network、Git等の新AuthorityがCurrent Transitionに不可欠になった。
3. Existing User Workを破壊せず分離できない重大Conflict。
4. 安全性、完全性、可逆性、Authorityを破壊せず進行できないCritical Finding。

Model品質が不十分、あるTestが失敗、設計修正が必要、処理時間が長い、Compactionが発生した、Packageが
完了した、という事実だけでは停止しない。Recovery Entryから差分再開し、COMPLETE_CANDIDATEまで進む。

## 8. Direct Return Contract

Return Handoffには最低限次を含める。

```text
From: 設計者兼実装者役
To: プロジェクト責任者兼設計統括者役
Status: COMPLETE_CANDIDATE | STOPPED_SAFE
Completed Packages:
Changed Files:
Acceptance ID Disposition:
Backend／Frontend Verification:
Real Qwen／DeepSeek Evidence:
Open Critical／Major／Non-critical:
Root／Memory／runtime_data／Git／Network Action Inventory:
User Manual Acceptance Remaining:
Exact Next Action: Controller Independent Review
```

Phase 6 Closure、Phase 7、Roadmap、Commit／Pushへ進まない。
