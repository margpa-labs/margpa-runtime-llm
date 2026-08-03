# Phase 1 Operations Lossless Compilation
```yaml
document_id: phase_1_operations_lossless_compilation
phase: phase_1
status: frozen
language: ja
created_at: 2026-07-26 15:16:24 JST
frozen_at: 2026-07-26 15:16:24 JST
source_documents: 11
source_manifest: ../../phase_1_ex/operations/source_to_target_documentation_migration_manifest.json
source_hash_algorithm: sha512
supersedes: null
rag_default: true
```

## Compilation Policy

本書はPhase 1中に作成されたSource文書を、省略、要約、意味変更または再解釈せず、Source Path順に再配置したLossless Compilationである。

本文は原文を維持し、Directory Migration後も参照可能にするため、MarkdownのLocal Link Pathだけを機械的に正規化している。原文File、原文SHA-512および移動先はSource Manifestから一意に解決できる。

矛盾、旧判断、未解決事項および後継文書への置換前状態も削除していない。Currentな判断はCurrent Canonical文書とPhase Indexを参照する。

## Source Documents

<!-- SOURCE_BEGIN 1: docs/operations/known_issues_and_observations_20260719171836.md -->

### Source 1: `docs/operations/known_issues_and_observations_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/operations/known_issues_and_observations_20260719171836.md`
- Source SHA-512: `898e31bac9d7fc1ab07212f40f2311fcbbb7af14b8cd8f5522ac780c01f1a3266ee6eb20a2bd19001a7dc7a4a9606794cc77978d5ba49475941f83bab8eaa559`
- Source Size: `4106` bytes

# Known Issues／Observations Register

- 文書ID: `known_issues_and_observations`
- 状態: `current`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 作成担当: 設計者役担当Task
- 対象: Project横断の既知問題、非Blocking Observation、Technical Debt
- 正本言語: 日本語
- Phase 1-E Review: [designer_review_phase_1e_final_20260719164641.md](../history/handoffs/designer_review_phase_1e_final_20260719164641.md)
- supersedes: なし（新規Operations系列）

## 1. 目的

本書は、Phase受入を妨げないが、将来の設計、実装、UI、運用、診断品質で参照すべき既知事項を失わないためのCurrent Registerである。

各項目は、Severity、影響、再現条件、現在のDisposition、再評価条件を分離して記録する。

本書に記載されたことだけを理由に、実装者役へSource修正権限が発生するものではない。

## 2. 状態分類

```text
open_blocking       : 現在のPhaseまたはReleaseを止める
open_required       : 必須Follow-upが必要
accepted_deferred   : 影響を理解して後続Phaseへ延期
monitor             : 条件発生時に再評価
resolved            : 後継文書で解決Evidenceを記録
not_reproducible    : 再現不能。再発時に再開
```

## 3. Current Items

### MARGPA-OBS-0001: Mixed-source Presentation Config Error Attribution

```yaml
id: MARGPA-OBS-0001
state: accepted_deferred
severity: low
category: configuration_diagnostics
introduced_or_found_in: phase_1e_review
security_boundary_impact: none_observed
runtime_behavior_impact: none_for_valid_configuration
required_follow_up: false
```

#### Summary

Thinking Presentation Policyの複数Fieldへ異なるSourceから値が入った状態で、Environment由来のFieldが不正、別Fieldに正常なExplicit Overrideが存在すると、Error Codeが不正値のSourceではなく「いずれかのExplicit Overrideがあるか」に引っ張られる。

#### Reproduction

```text
MARGPA_THINKING_VISIBILITY = sometimes
explicit_display_label     = 明示推論
```

現在の結果：

```text
invalid_request
```

より精密な診断候補：

```text
invalid_configuration
offending_field  = visibility
offending_source = environment
```

#### Cause

`resolve_thinking_presentation_policy`は全Fieldの最終Validationを一括で行い、Error Code選択時に、実際に失敗したField／Sourceではなく、`explicit_visibility`または`explicit_display_label`が存在するかを確認している。

#### Impact

- 不正値は安全に拒否される
- Raw Config値、Absolute Path、SecretはSafe Errorへ露出しない
- 正常値のPrecedenceとSource Trackingには影響しない
- Thinking表示、Hidden No-flash、Persistence、Raw Model Portには影響しない
- UIやSupport時に、原因がCLI入力なのかEnvironment設定なのかを示す精度が低下する可能性がある

#### Disposition

Phase 1-EのAcceptance Criteriaには抵触せず、Source修正を必須としない。Phase 1-Eは`Complete／Accepted`のままとする。

次のいずれかで再評価する。

- Phase 2の設定UI／Config Validation設計時
- Field別Validation ErrorをUIへ表示する時
- Config Source Diff／Effective Config診断を強化する時
- External Release前にError Taxonomyを整理する時
- 同じ分類方式による実害または類似Findingが発生した時

改善候補は、FieldごとにValidationとSource Attributionを保持し、実際に失敗したFieldのSourceからError Codeを決定することである。

## 4. Phase／Backupへの影響

`MARGPA-OBS-0001`はAccepted Deferred Observationであり、Phase 1完了またはBackupを単独ではBlockしない。

Manifest／Phase Final Reviewでは、Known Observationとして本書を参照する。

## 5. 更新規則

新しいIssue／Observation、状態変更、Resolution Evidenceを追加する場合、既存Fileを編集せず、新Timestampの後継Registerを作成する。


<!-- SOURCE_END 1: docs/operations/known_issues_and_observations_20260719171836.md -->

---

<!-- SOURCE_BEGIN 2: docs/operations/known_issues_and_observations_20260719195134.md -->

### Source 2: `docs/operations/known_issues_and_observations_20260719195134.md`

- History Target: `docs/project/phases/phase_1/history/operations/known_issues_and_observations_20260719195134.md`
- Source SHA-512: `8f32d5f39852994b678bb646f4d0077591262efa0db8066c9ed022dc6c43f100ea2434d3689a8fd32c1d60645dea4c72d11d031f9edfb1b1376443e44bea0839`
- Source Size: `4692` bytes

# Known Issues／Observations Register

- 文書ID: `known_issues_and_observations`
- 状態: `current`
- 作成日時: `2026-07-19 19:51:34 JST`
- 更新日時: `2026-07-19 19:51:34 JST`
- Snapshot: `20260719195134`
- 作成担当: 設計者役担当Task
- 対象: Project横断の既知問題、非Blocking Observation、Technical Debt
- 正本言語: 日本語
- User Test補足: [phase_1_user_acceptance_findings_20260719195134.md](../history/user_manual/phase_1_user_acceptance_findings_20260719195134.md)
- supersedes: `known_issues_and_observations_20260719171836.md`

## 1. 状態分類

```text
open_blocking       : 現在のPhaseまたはReleaseを止める
open_required       : 必須Follow-upが必要
accepted_deferred   : 影響を理解して後続Phaseへ延期
monitor             : 条件発生時に再評価
resolved            : 後継文書で解決Evidenceを記録
not_reproducible    : 再現不能。再発時に再開
```

## 2. Current Items

### MARGPA-OBS-0001: Mixed-source Presentation Config Error Attribution

```yaml
state: accepted_deferred
severity: low
category: configuration_diagnostics
required_follow_up: false
```

Environment由来の不正なThinking Presentation値と、別Fieldの正常なCLI指定が同時に存在する場合、Error Codeの原因分類が少し不正確になる。不正値は安全に拒否され、正常動作、Security Boundary、Phase 1 Acceptanceを単独ではBlockしない。

Phase 2 Config UI、Field別Validation、External Release前のError Taxonomy整理時に再評価する。

### MARGPA-OBS-0002: Hidden Thinking Final Answer Exhaustion

```yaml
state: open_required
severity: low
category: cli_presentation_diagnostics
required_follow_up: true
```

Thinkingを有効、VisibilityをHiddenとし、Closing／Final Answerより前にToken上限へ到達すると、CLIの表示が空になる。Reasoning漏洩やParser故障ではないが、利用者が原因を判別できない。

Final Answer未生成を判定可能なEvidenceがある場合、Reasoning本文を露出せず、次の意味のSafe Warningを表示する。

```text
最終回答を生成する前にToken上限へ到達しました。
```

False Positiveを避け、正常な空回答、Model Error、User Cancelと混同しないことを実装条件とする。

### MARGPA-OBS-0003: Preserved Leading Whitespace in Final Answer

```yaml
state: accepted_deferred
severity: low
category: presentation_normalization
required_follow_up: false
```

Canonical Closing Tag後の改行をParserが保持するため、Final Answer先頭に空行が残る場合がある。Raw Output保持と無断Trim禁止の結果であり、Phase 1では修正しない。

UI／Presentation層で、Raw／Parsed Evidenceを変えず表示だけを正規化できる段階で再評価する。

### MARGPA-OBS-0004: Reasoning Language May Differ from Final Language

```yaml
state: accepted_deferred
severity: low
category: model_language_behavior
required_follow_up: false
```

`response_language = ja`でも、表示したQwen3 Reasoningが英語になる場合がある。Current Language PolicyはFinal AnswerへのBest-effort Instructionであり、Raw Reasoning Languageを強制しない。

Strict Language EnforcementはPhase 1-E Scope外である。Model固有Prompt、Reasoning Language設定、Model交換、表示用翻訳を後続で比較する。

### MARGPA-OBS-0005: Registered-platform Routing Is Not Full Hardware Auto-routing

```yaml
state: accepted_deferred
severity: low
category: deployment_portability
required_follow_up: false
```

OS／Architecture検出と登録済みDefault Profile選択は実装済みだが、Linux／Windows Profile、Platform別Native Build、実機検証は未完了である。また同一Linux x86_64内のCPU／CUDA／ROCm等をHardware Observationで自動選択する完成形は未実装である。

Application CoreはPlatform固有条件から分離済みであり、一般Cross-platform完成を延期しても後続Core PhaseをBlockしない。Lightning AI Studioのような明示環境は、当面Explicit Profileで追加・検証できる。

## 3. Phase／Backupへの影響

- `MARGPA-OBS-0001`、`0003`、`0004`、`0005`はAccepted Deferredであり、Phase 1を単独ではBlockしない。
- `MARGPA-OBS-0002`は実装対象候補であり、User Acceptance GateはFollow-upのDisposition確定までWaitingとする。
- Follow-upでSource／Config／Testsを変更した場合、影響範囲の再Review／再Testが必要である。

## 4. 更新規則

状態変更、Resolution Evidence、項目追加は既存Fileを編集せず、新Timestampの後継Registerで行う。

<!-- SOURCE_END 2: docs/operations/known_issues_and_observations_20260719195134.md -->

---

<!-- SOURCE_BEGIN 3: docs/operations/phase_1_backup_completion_record_20260726122144.md -->

### Source 3: `docs/operations/phase_1_backup_completion_record_20260726122144.md`

- History Target: `docs/project/phases/phase_1/history/operations/phase_1_backup_completion_record_20260726122144.md`
- Source SHA-512: `e294dd850c7ce293b082077fe98467323c5f5303691f58d5e795ef2a8be8eb5319cac4cb659040c235a96d34a6bccdd4115c7def5d937a047586bd552b689f00`
- Source Size: `5744` bytes

# Phase 1確定Backup 完了記録

- 文書ID: `phase_1_backup_completion_record`
- 状態: `completed_verified`
- 作成日時: `2026-07-26 12:21:44 JST`
- 更新日時: `2026-07-26 12:21:44 JST`
- Snapshot: `20260726122144`
- Backup Snapshot: `20260726121941`
- 作成担当: 設計者役担当Task
- Backup入力Index: [documentation_index_20260726121346.md](../history/documentation_index_20260726121346.md)
- Phase 1 Final Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- Pre-backup Scan: [pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md](../history/operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1確定Backupを作成し、Sanitation、SHA-512、Temporary Restoreおよび保存先Copy後の再検証を完了した。

```text
Backup Status             : COMPLETED／VERIFIED
Phase                     : Phase 1
Milestone                 : portable_runtime_mvp
Backup Snapshot           : 20260726121941
File Count                : 422
Uncompressed File Bytes   : 3,360,052
Archive Size Bytes        : 1,377,193
Restore Verification      : PASS
Privacy Scan              : PASS
Secret Scan               : PASS
```

## 2. Backup Location

Project Root外の次の論理配置へ保存した。

```text
MARGPA-RUNTIME-LLM/
├─ margpa-runtime-llm/
└─ phase_backups/
   └─ phase_1/
```

個人固有Absolute Pathは本書へ記録しない。

## 3. Backup Set

```text
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941.zip
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941_manifest.json
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941_receipt.json
margpa-runtime-llm_phase_1_portable_runtime_mvp_20260726121941_sha512.txt
```

## 4. SHA-512

Archive：

```text
9eaabdee62a36e072df5d990d68e9986ca34b2894f8d6212ac3db4c26c85b2947be6052e0b4bbace2575f774a28eb1694a8e6a846330d6b1c307b75d6931b483
```

Manifest：

```text
e7318bbbc03d24982567ea1f30dbf32ecce41e00885d196a91f8c0b4a82a63f7fb58d1f15b62a63e305988f950d45ed6e75de3f8f1939ba89827113736eebd8c
```

Receipt：

```text
a35e2374f76b436bf993f2011e638458ff03911842b8a5938e7a1180615db962b826d5fc2bc93c922724a204d2b7132e22939c5f383589e2ac67dd6d421ff45a
```

Sidecarの`shasum -a 512 -c`は保存先で3件すべてOKとなった。

## 5. Include Set

```text
.gitignore
.python-version
config/
docs/
pyproject.toml
scripts/
src/
tests/
uv.lock
```

Backup入力時点のCurrent Documentation Index：

```text
docs/documentation_index_20260726121346.md
```

## 6. Excluded Set

```text
.DS_Store
.venv/
Project Root models/
models Symbolic Link
GGUF Model Binary
.git/
.pytest_cache/
.mypy_cache/
.ruff_cache/
__pycache__/
*.pyc
*.pyo
.coverage
htmlcov/
.ipynb_checkpoints/
.env
.env.*
var/
*.log
Local Data
Credential
Secret
```

Model本体は含めず、ManifestへModel ID、File名、QuantizationおよびSHA-512だけを記録した。

## 7. Sanitation Verification

Candidateに対して次を確認した。

```text
Root Directory                    : margpa-runtime-llm/ only
Symbolic Link                     : 0
GGUF                              : 0
.DS_Store                         : 0
.venv                             : 0
Root models                       : 0
Cache／Bytecode                   : 0
Secret File                       : 0
Forbidden Identity Literal        : 0
Private Key／Token Pattern        : 0
```

`config/models/`はModel Registry定義を保持する正規Source Directoryであり、Project RootのModel Artifact置き場`models/`とは異なるためIncludeした。

## 8. Restore Verification

ArchiveをTemporary Directoryへ展開し、次を確認した。

1. Archive Rootが`margpa-runtime-llm/`の1件だけである。
2. Restored File Countが422である。
3. Source CandidateとRestored TreeのRelative Pathが一致する。
4. 全FileのSizeが一致する。
5. 全FileのSHA-512が一致する。
6. Forbidden Artifactが復元されない。
7. Manifest Inventoryと一致する。

結果：

```text
archive_root_valid        : true
inventory_matches_manifest: true
file_hashes_match         : true
restore_completed         : true
restored_file_count       : 422
symlink_absent            : true
forbidden_artifact_absent : true
privacy_scan_passed       : true
secret_scan_passed        : true
```

## 9. Candidate検証の安全停止

最初のTemporary Candidate検証では、禁止対象のProject Root `models/`と、必要な`config/models/`をDirectory名だけで同一視したため、安全側で停止した。

```text
Candidate contains forbidden directory: models
```

このCandidateはArchive確定またはBackup保存していない。

検査条件を次へ修正した。

```text
Forbidden:
  Project Root models/
  Root models Symbolic Link
  GGUF Artifact

Allowed:
  config/models/
```

新Timestamp `20260726121941`でCandidateを作り直し、全検証をPassしたSetだけを確定保存した。

## 10. VCS State

```text
vcs.type   : none
commit     : null
tag        : null
remote     : null
```

Phase 1 BackupはGit開始前Snapshotである。Git初期化またはGitHub公開は行っていない。

## 11. Phase Transition

```text
Phase 1 Backup : COMPLETE
Phase 1-ex     : READY TO START／NOT STARTED
```

初回GitHub公開はPhase 1-ex完了後まで延期する。

## 12. Authorization Boundary

Backup完了はPhase 1-exへ進める状態を示すが、Phase 1-exのSource／Config／Docs Migration、Git操作、Lightning変更またはRAG実装を自動開始しない。

<!-- SOURCE_END 3: docs/operations/phase_1_backup_completion_record_20260726122144.md -->

---

<!-- SOURCE_BEGIN 4: docs/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md -->

### Source 4: `docs/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md`

- History Target: `docs/project/phases/phase_1/history/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md`
- Source SHA-512: `5d795437a1ed8086e5e35d0075de0b58a960b06ec0eb3df1723cdf0e450b37ba906a54a68cd970fc8514c8a19dcb91b616ce67b580e77624b41ae28205cc59a3`
- Source Size: `13438` bytes

# Phase 1 Lightning最終化／Phase 1-ex開始前 統合記録

- 文書ID: `phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record`
- 状態: `current_pre_backup_record`
- 作成日時: `2026-07-26 12:02:29 JST`
- 更新日時: `2026-07-26 12:02:29 JST`
- Snapshot: `20260726120229`
- 作成担当: 設計者役担当Task
- 対象期間: Lightning Pure CPU実環境構築の再整理依頼からPhase 1確定Backup直前まで
- Phase 1 Final Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../history/handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- Current User Manual: [phase_1_web_and_lightning_user_manual_20260726111632.md](../history/user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)
- Phase 1-ex Pre-start Requirements: [phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](../history/requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)
- 正本言語: 日本語
- supersedes: なし

## 1. 文書の目的

本書は、Lightning AI Studio Pure CPU環境の実構築で発生した問題、途中の手順変更、Repository Test修正、外部Web公開、Manual Acceptance、Phase 1完了判定およびPhase 1-ex開始前の最新Decisionを、一つの時系列へ再統合する。

既存の詳細Manual、Review、HandoffおよびStatusを要約して置換するものではない。個別Evidenceは各原文書を正本として維持し、本書はPhase 1確定Backup前に全体経緯を追跡する入口とする。

## 2. Lightning Pure CPU環境構築で成立した最終Path

```text
/teamspace/studios/this_studio/
├─ margpa-runtime-llm/
│  ├─ .python-version
│  ├─ .venv/
│  ├─ config/
│  ├─ models -> ../models
│  ├─ pyproject.toml
│  ├─ scripts/
│  ├─ src/
│  ├─ tests/
│  └─ uv.lock
├─ models/
│  └─ main/
│     └─ qwen3-4b/
│        └─ gguf/
│           └─ Qwen3-4B-Q4_K_M.gguf
└─ .runtime-tools/
   └─ uv/
      └─ 0.11.29/
         └─ bin/
            ├─ uv
            └─ uvx
```

確定した環境変数：

```text
MARGPA_WORKSPACE_ROOT : /teamspace/studios/this_studio
MARGPA_PROJECT_ROOT   : /teamspace/studios/this_studio/margpa-runtime-llm
MARGPA_MODEL_ROOT     : /teamspace/studios/this_studio/models
MARGPA_UV_BIN         : /teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin
MARGPA_ENV_PREFIX     : /teamspace/studios/this_studio/margpa-runtime-llm/.venv
```

## 3. 構築中に発生した問題と最終解決

### 3.1 Model Symbolic Link循環

初回Upload後、Project内の`models/`が実Directoryで、その内部に自己参照する`models` Symbolic Linkが存在した。

```text
find: models/models: Too many levels of symbolic links
```

最終状態：

```text
margpa-runtime-llm/models -> ../models
```

Registryが要求するModel Root直下の`main/qwen3-4b/gguf/...`構造へ修正し、Model Checkが合格した。

### 3.2 Upload Artifact不足

RuntimeだけでなくFull Repository Suiteを実行するため、次が必要であった。

```text
tests/
.python-version
```

`.python-version`はLocal Macの既定Python Metadataであり、Lightning Runtime Pythonを決めない。ただしRepository Contract Testが参照するためTest Bundleへ含めた。

### 3.3 Shell Script Permission

Browser UploadまたはArchive展開により、Setup Scriptの実行権限が失われた。

```text
PermissionError: [Errno 13] Permission denied
```

Unit TestがScriptを直接実行するため、対象ScriptへUser Execute Permissionを付与した。

### 3.4 Lightning既設uvとのVersion差

Studio既設：

```text
uv 0.11.18
```

Project Required：

```text
uv 0.11.29
```

Studio既設uvを置換せず、Project専用Binaryを次へ隔離した。

```text
/teamspace/studios/this_studio/.runtime-tools/uv/0.11.29/bin
```

Binary SHA-512を検証し、TerminalごとにProject専用Pathを先頭へ設定した。

### 3.5 Active Conda EnvironmentとProject `.venv`

LightningのActive Conda Prefix：

```text
/home/zeus/miniconda3/envs/cloudspace
```

これをProject Virtual Environmentとして再利用しようとすると、`uv`が互換Environmentとして再作成できず失敗した。

最終Decision：

```text
MARGPA_ENV_PREFIX="$MARGPA_PROJECT_ROOT/.venv"
```

Macの`.venv/`はUploadせず、Lightning Linux x86_64／Python 3.12.11用にProject-local `.venv/`を再構築した。

### 3.6 Pure CPU `llama-cpp-python`

初回Verificationでは`llama_cpp`が存在しなかった。

```text
ModuleNotFoundError: No module named 'llama_cpp'
```

Pure CPU Native BuildをProject `.venv/`へ導入し、Environment Verificationを合格させた。

### 3.7 Test Isolation Failure

External Pure CPU RuntimeおよびBounded Native Acceptanceは合格した一方、Full Suiteでは実Lightning ContainerのEnvironment VariableおよびPlatform MarkerがUnit Testへ混入した。

最終的に次のTest-only修正を実装担当へ渡した。

- Platform Default Resolution Testを実Container Stateから分離する。
- Future Platform Alias Testを実Execution Environmentから分離する。
- Temporary Model Root TestをShellの`MARGPA_MODEL_ROOT`から分離する。
- Production Runtime挙動は変更しない。

修正後Evidence：

```text
Targeted Test : 41 passed
Full Suite    : 266 passed／1 skipped／3 deselected
Failure       : 0
```

Apple Silicon Metal Integration Testの1 SkipはLightning Linux x86_64で正常である。

## 4. Lightning Runtime最終判定

```text
Python                       : 3.12.11
Platform                     : Ubuntu Linux x86_64 Container
Runtime Target               : external.lightning-linux-x86_64.cpu-native
Backend                      : llama-cpp-python 0.3.34 Pure CPU
Model                        : Qwen3-4B-Q4_K_M.gguf
Environment Verification     : PASS
Static Verification          : PASS
Bounded Native Acceptance    : PASS
all_required_checks_passed   : true
Full Repository Suite        : GREEN
```

External Pure CPU Runtime自体と、Repository Portabilityの両方をAcceptedとした。

## 5. Lightning Web外部公開

Pure CPU ProfileでFastAPI Web Previewを起動し、Lightning Port ViewerからPublic Linkを公開した。

確認時Public Link：

```text
https://lightning-preview-url-redacted.invalid/not-published
```

Lightning Accountと無関係なBrowserおよびSafariからBasic認証を経由してアクセスできた。

次を確認した。

- Credentialなし／誤Credentialの拒否
- 正しいCredentialでWeb表示
- Studio Terminal／File Editorが外部から見えない
- `/healthz`が最小情報だけを返す
- Web Process停止後のPort Close

## 6. Lightning Web Manual Acceptance

必須項目：

```text
短い日本語生成                         : PASS
生成中の停止                           : PASS
停止後の再送信                         : PASS
新規Chat                               : PASS
UI日本語／English切替                  : PASS
回答言語ja／en切替                     : PASS
Browser Reload                         : PASS
別Tab同時生成時のModel Busy            : PASS
Server停止後のPort Close               : PASS
```

追加項目：

```text
User／Assistant Copy                   : PASS
Summary Mode                           : PASS
生成中のNew Chat                       : PASS
Summary中のStop                        : PASS
Thinking Generation／Visibility        : PASS
最大生成Token数による打切り            : PASS
```

Browser Reload後はConversationおよびUI Language以外のOptionがRuntime Defaultへ戻り、UI LanguageだけがBrowserへ保持された。

## 7. Model Busy

競合Tabで次の表示を確認した。

```text
The model is processing another request.
The request failed.

Modelは別のRequestを処理中です。
Requestに失敗しました。
```

具体的Messageと汎用Messageが重複する点はPhase 4 Presentation／UX Follow-upへ延期する。競合Requestを安全に拒否し、先行処理完了後に後続Requestが動作するため、Phase 1 Failureとはしない。

## 8. Pure CPU Performance

Lightning最小Pure CPUではQwen3 4B Q4_K_Mの生成が非常に遅い。

これは超軽量／低Cost環境を優先したExpected Limitationである。Summary Modeは通常回答後に同じModelを再度呼ぶため、さらに遅くなる。

```text
日常開発／高速確認     : Mac Metal
外部互換性／公開確認   : Lightning Pure CPU
Lightning GPU          : 必要な短時間検証時だけ明示選択
```

性能不足はCurrent Model Adapter、Runtime Governance構造またはCross-platform CorrectnessのFailureではない。

## 9. iPhone／Mobile

iPhone／iOS対応は不可能ではないが、Current Phase 1はMobile Responsive Acceptanceを持たない。

Phase 4または後続UI Phaseで次を扱う。

- Responsive Layout
- iOS Safari
- Touch Target
- Virtual Keyboard
- Safe Area
- Narrow Viewport
- Long Message／Code Block Overflow

Phase 1 CompletionをBlockしない。

## 10. Studio Sleepと公開Demo

実環境では、Studioを一定時間操作しないとSleepし、公開Demoも停止した。

したがって、Current Manual Start方式では、第三者へURLを送っただけで常時閲覧可能なDemoにはならない。

求める将来動作：

```text
Public URL Access
  → Traffic-aware Studio Wake
  → Web Server Auto-start
  → Model Load／Health Ready
  → Basic認証
  → Demo利用
  → Idle後にSleep
```

Studio起動後の`on_start.sh`だけでなく、URL AccessからStudio自体を起こすTraffic-aware Auto-startの利用可否をPhase 1-ex前半で確認する。

## 11. Basic認証のCurrent Decision

Current PreviewはBasic認証を維持する。

理由：

- Public Demo向けRate Limit、Request Budget、Cost Guardが未実装である。
- GitHubへURLを公開した場合、URLの推測困難性はAccess Controlにならない。
- Basic認証は将来の本格Account機能ではなく、少人数Preview用の暫定防壁である。

Current Repositoryへ個人情報または連絡先を掲載しないため、READMEへ「連絡してください」と記載しない。

README等の公開文書では、次の趣旨だけを記載する。

> 将来、Public Demo方式も検討しています。

Traffic-aware Auto-start、Public Demo向けCost Guardおよび本格的なAccount機能は分離する。

## 12. Access Modeの将来分類

将来候補：

```text
local
  → Loopback限定

preview_shared
  → 少人数検証
  → Basic認証

public_demo
  → 将来検討
  → 認証なし候補
  → Rate Limit／Token／Cost保護
  → Tool／RAG／外部操作なし

authenticated
  → 将来のAWS／高性能Model／大規模編成
  → Account／Quota／権限管理
```

`public_demo`の実装はCurrent Phase 1-ex必須Scopeにしない。

## 13. Phase 1完了

次がすべて成立した。

```text
Phase 1-A～1-I                 : COMPLETE／ACCEPTED
Mac Web Manual Acceptance     : PASS
Lightning Pure CPU Runtime    : ACCEPTED
Mac Full Repository Suite     : GREEN
Lightning Full Suite          : GREEN
Lightning External Web        : PASS
Top-level Phase 1             : COMPLETE／ACCEPTED
```

設計者役によるPhase完了／次Phase着手可能宣言と、ユーザーによる受入テスト合格宣言の両方が成立した。

Phase 1確定Backup TriggerはReadyである。

## 14. Phase 1-ex開始前Decision

Phase 1-exの実行順序を次とする。

```text
1. Phase 1確定Backup

2. Lightning Auto-start Read-only Preflight
   → Current Plan／Custom Port／Public URL／CPU固定／Basic認証
   → 簡単ならPhase 1-ex前半で実装
   → Deployment移行等が必要なら後続へ延期

3. Git運用設計
   → Branch／Tag／Commit／Author／Remote／Backup対応

4. Git公開準備
   → .gitignore／.gitattributes
   → Model／Secret／Cache除外
   → Privacy Scan
   → LICENSE方針
   → Commit直前まで準備

5. docs/構造再設計
   → Inventory／Target Tree／Ownership／Migration／Rollback

6. 新構造を全担当Taskへ通知

7. 既存DocsのLossless再整理

8. Canonical／公開Docs作成
   → README／overview_ja／concept_ja／roadmap_ja
   → Requirements／Architecture／Technology／Basic Design／Governance
   → LICENSE／NOTICE／CITATION等

9. Mac限定の簡易RAG

10. 全体Review／Test／Privacy Scan

11. 初回Commit／Tag／Phase 1-ex Backup／GitHub公開
```

Git準備はDocs再整理より前に進める。ただし既存の細分化Docs、移行前Path、不要Artifactまたは公開不適切情報を最初の公開Commit履歴へ残さないため、初回CommitはDocs再整理と最終Scan完了後まで作成しない。

## 15. Authorization Boundary

本書の作成によりPhase 1確定Backupの条件は確認できるが、Git初期化、Commit、Remote設定、Push、Lightning設定変更、Auto-start実装またはPhase 1-ex Source変更を自動許可しない。

Phase 1 Backupは、ユーザーの明示指示に基づき、本書とCurrent Documentation Indexを含む同一Snapshotから作成する。

<!-- SOURCE_END 4: docs/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md -->

---

<!-- SOURCE_BEGIN 5: docs/operations/phase_completion_backup_policy_20260719142558.md -->

### Source 5: `docs/operations/phase_completion_backup_policy_20260719142558.md`

- History Target: `docs/project/phases/phase_1/history/operations/phase_completion_backup_policy_20260719142558.md`
- Source SHA-512: `fe0ddcf2f4e3efc0ba1cb562e08b94f43a2c04343eb91b1372ea424a4d86ed67dc7f7045927d459227632b365b67ed1ce8e2d2f9a92839563c7d6105539c58e6`
- Source Size: `9789` bytes

# Phase完了Backup／Snapshot運用Policy

- 文書ID: `phase_completion_backup_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-19 14:25:58 JST`
- 更新日時: `2026-07-19 14:25:58 JST`
- Snapshot: `20260719142558`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 全上位Phaseの完了後Backup、Source Archive、Evidence Manifest、Restore
- 正本言語: 日本語
- 関連共通Rule: [documentation_rules_20260719142558.md](../history/requirements/documentation_rules_20260719142558.md)
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- supersedes: なし（新規Operations Policy系列）

## 1. 承認結論

Projectは、各上位Phaseの完了後にSource ArchiveとEvidenceを作成する。

Backupの正式Triggerは、設計者役がIndependent Reviewと必要文書を完了し、次の意味を明示的に出力した時点とする。

```text
Phase Nは完了。次はPhase N+1です。
```

文言の完全一致は必要ないが、次の両方が明示される必要がある。

1. 対象Phaseが完了・受入済みであること
2. 次Phaseへ移行すること

Implementer Statusが出ただけ、実装が終わったように見えるだけ、またはSubphaseのみが終わった時点ではBackup Triggerとしない。

## 2. Timing

正式な順序：

```text
Implementation Complete
  ↓
Implementer Status
  ↓
Designer Independent Review
  ↓
Required Follow-up Complete
  ↓
Phase Final Review／User Manual／Index確定
  ↓
Designer Phase Completion Declaration
  ↓
Phase Backup／Integrity Verification
  ↓
Next Phaseの実装変更
```

BackupはPhase完了宣言の後に取る。

原則として、次PhaseのSource／Config／Docsの実質的変更を始める前にBackupとIntegrity Verificationを完了させる。

## 3. Phase単位

定期Backupは上位Phase単位とする。

```text
Phase 1
Phase 2
Phase 3
...
```

`Phase 1-A`～`Phase 1-E`のようなSubphase完了だけで、自動的にPhase Backupを必須としない。

ただし、次の場合は臨時Snapshotを追加できる。

- 大規模Schema Migrationの直前
- 破壊的変更の直前
- Storage／Audit形式変更の直前
- Model／Backend交換の直前
- ユーザーが明示的にSnapshotを要求した場合

臨時SnapshotはPhase完了Backupと区別したName／Manifestを使用する。

## 4. Phase Completion Preconditions

設計者役は、次を確認した後にPhase完了を宣言する。

- Phase配下の必須SubphaseがComplete／Accepted
- Blockerがない
- 未解決事項が次PhaseまたはKnown Limitationとして明記済み
- Independent Review完了
- 必要なRegression／Native Verification完了
- Current User Manualが実装と整合
- Phase Final Reviewが存在
- 最新Documentation IndexがCurrent Setを正しく示す
- Backup対象と除外対象の範囲が確定

## 5. Backup Set

Phase Backupは次の4点Setを基本とする。

```text
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS.zip
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_manifest.json
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_receipt.json
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_sha512.txt
```

Phase 1候補：

```text
margpa-runtime-llm_phase_1_portable_runtime_mvp_YYYYMMDDHHMMSS.zip
```

Archive、Manifest、Receipt、SHA-512 Fileを同一Basename系列で紐付ける。

## 6. Archive Content

原則としてAllowlist方式を使用する。

Include候補：

```text
src/
tests/
config/
docs/
scripts/
notebooks/                 # 存在する場合

pyproject.toml
uv.lock
.python-version            # 存在する場合
.gitignore                 # 存在する場合
README*
LICENSE*
再構築に必要な明示済みRoot File
```

`config/`内でもSecret、Local OverrideまたはCredentialを含むFileは除外する。

## 7. Exclusion

```text
.venv/
models/
GGUF／Model Binary
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.ipynb_checkpoints/
.DS_Store
Cache
一時File
実行Log
Audit実データ
.env
Secret／Credential
Local Override
Backup Directory自体
```

Project Rootの`models/` Symbolic LinkはArchiveから原則除外する。Absolute Linkを別環境へ復元しないためである。Link Target／復元手順はManifestへ記録する。

## 8. Snapshot Manifest

Manifestは最低限次を含む。

### Identity

- Schema Version
- Snapshot ID
- Project Name
- Phase ID／Phase Name／Milestone
- Completion Declaration Timestamp
- Archive Creation Timestamp
- Current Documentation Index
- Phase Final Review
- Current Roadmap

### Source

- Included Path
- Excluded Path／Reason
- Included File Inventory
- Included File Size
- Included File SHA-512
- Manifest Canonicalization
- Manifest SHA-512

### VCS

CurrentはGit未使用のため、事実として次のように記録する。

```text
vcs.type        : none
vcs.commit_hash : null
vcs.tag         : null
```

Git導入後はCommit Hash／Tagを同じSchemaへ追加できる。Git未使用時はManifest SHA-512をSource Snapshot Identityとする。

### Environment

- OS／OS Version
- Architecture
- Hardware Profile
- Python Version
- Backend／Version／Build Variant
- Acceleration
- Dependency Lock SHA-512
- Verification Script／Result参照

### Model

- Model Key／Role
- Distribution Repository／Upstream Model
- File Name
- Relative Model Path
- External Model Root
- Size
- Format／Quantization
- Model Artifact SHA-512
- Model Definition SHA-512
- Symbolic Link復元方法

### Evidence

- Implementer Status
- Designer Final Review
- Test Command／Result Summary
- Static／Default／Native Gate
- Known Limitation
- User Manual

## 9. Manifest／Receiptの分離

ZIP本体のSHA-512をZIP内のManifestへ格納すると自己参照になる。

そのため次の分離を必須とする。

```text
Manifest:
  Archive内Content、File Hash、Environment、Model、Evidence

Receipt:
  完成後のZIP File Name、Size、SHA-512、Manifest SHA-512

SHA512 Sidecar:
  簡易整合性検証用
```

ManifestはArchive内に含め、必要に応じてArchiveの外にも同一Copyを保持する。ReceiptはArchive完成後に作るDetached Sidecarとする。

## 10. Docs Record

各Phaseの完了時に、設計者役は次の系列を`docs/operations/`へ作成する。

```text
phase_<n>_<milestone>_snapshot_record_YYYYMMDDHHMMSS.md
```

Phase 1候補：

```text
phase_1_portable_runtime_mvp_snapshot_record_YYYYMMDDHHMMSS.md
```

Snapshot Recordは次を人間向けに示す。

- Phase完了条件
- Final Review
- Current Index
- Current Roadmap
- Test Evidence
- Model／Environment Summary
- Backup SetのNaming Rule
- Manifest／Receiptの責務
- Exclusion
- Restore Entry Point

ZIP自体のHashはDetached Receiptを正本とし、Snapshot Record内へ自己参照となる形で書かない。

## 11. Backup Location

BackupはProject Root内へ保存しない。Archiveが次のArchiveへ再帰的に入ることと、Project自体が肥大化することを防ぐ。

推奨論理構造：

```text
MARGPA-RUNTIME-LLM/
├─ margpa-runtime-llm/
└─ backups/
   └─ margpa-runtime-llm/
      └─ phase_<n>/
```

実体PathはBackup実行前にユーザーが確定する。

同じMac／同じSSD上のCopyは誤操作対策にはなるが、Disk故障対策にはならない。重要なPhase Backupは外付けStorageまたはCloudへ第2Copyを保持することを推奨する。

## 12. Integrity Verification

Backup完了条件：

1. ZIPの構造検査がPass
2. ZIP SHA-512が計算済み
3. ReceiptとSHA512 Sidecarが一致
4. Manifest SHA-512が一致
5. Included File InventoryとArchive Contentが整合
6. Secret／Model Binary／`.venv`が含まれない
7. Temporary DirectoryへのTest Extractが成功
8. Restore Entry Point／Setup Recipeが特定できる

Modelを含まないため、Archive単体でNative Generationが完結すると主張しない。ManifestとSetup Recipeを使い、外部Modelを再配置して復元する。

## 13. Restore Test

最低限のRestore Test：

- ZIPをTemporary DirectoryへExtract
- Expected Root File／Directory確認
- Manifest File Inventory検証
- `uv.lock`／`pyproject.toml`の存在確認
- Modelが除外されていることの確認
- Model Root復元手順の確認
- DocsのLatest Index／Final Review参照確認

Dependency Install／Model Download／Native Testまで実行するFull Restore Drillは、ユーザーが別途許可した場合に行う。

## 14. Immutability／Retention

- Backup Setを上書きしない
- Timestampを持たせる
- 再作成時は新Timestampとする
- 古いPhase Backupを原則削除しない
- 再作成理由を新Manifest／Receiptへ記録する
- Backup SetのRenameを原則行わない

## 15. Git導入後

Gitは現時点で必須としない。

将来Gitを導入した場合は、Phase Backup Setに次を追加する。

```text
commit_hash
tag
dirty_state
repository_remote
```

Tag候補：

```text
phase-1-portable-runtime-mvp
```

Git TagはSource History上のIdentity、ZIPは独立復元用Archive、Manifest／ReceiptはEvidenceとして併存させる。

## 16. Authorization Boundary

本PolicyはBackupのTiming／Content／Evidence規則を承認する。

本Policyの作成だけでは、次を自動解禁しない。

- External Backup Directoryの作成
- ZIP／Manifest／Receiptの実生成
- Project外へのWrite
- Cloud Upload
- External DriveへのCopy
- Git初期化／Commit／Tag

実際のBackup作成はPhase完了Triggerの後、ユーザーの指示または事前に承認されたBackup Operator Scopeで行う。


<!-- SOURCE_END 5: docs/operations/phase_completion_backup_policy_20260719142558.md -->

---

<!-- SOURCE_BEGIN 6: docs/operations/phase_completion_backup_policy_20260719171836.md -->

### Source 6: `docs/operations/phase_completion_backup_policy_20260719171836.md`

- History Target: `docs/project/phases/phase_1/history/operations/phase_completion_backup_policy_20260719171836.md`
- Source SHA-512: `129eb786dea63dc1917052c7f328f17d83536d54af38a9e23e7c8082f64fdc63647055d82e844c3d011890d31d46b361f8e7c494be1a73e602ce83103b928050`
- Source Size: `10659` bytes

# Phase完了Backup／Snapshot運用Policy

- 文書ID: `phase_completion_backup_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-19 17:18:36 JST`
- 更新日時: `2026-07-19 17:18:36 JST`
- Snapshot: `20260719171836`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 全Top-Level Phaseの完了後Backup、Source Archive、Evidence Manifest、Restore
- 正本言語: 日本語
- 関連共通Rule: [documentation_rules_20260719171836.md](../history/requirements/documentation_rules_20260719171836.md)
- 役割権限: [task_role_write_authority_policy_20260719142558.md](../history/requirements/task_role_write_authority_policy_20260719142558.md)
- Known Observations: [known_issues_and_observations_20260719171836.md](../history/operations/known_issues_and_observations_20260719171836.md)
- supersedes: `phase_completion_backup_policy_20260719142558.md`

## 1. 承認結論

Projectは、各Top-Level Phaseについて次の2つが両方成立した後に、Phase Backupを取得する。

```text
Gate A: 設計者役によるPhase完了宣言と次Phase移行可能宣言
Gate B: ユーザーによる対象Manual／対象Snapshotの受入テスト合格宣言
```

いずれか片方だけではBackup Triggerは成立しない。

設計者宣言の意味：

```text
Phase Nは完了です。次はPhase N+1へ移行可能です。
```

ユーザー宣言の推奨形式：

```text
<対象User Manual File>のPhase Nユーザー受入テストは、全項目合格です。
```

文言の完全一致は必要ない。ただし、対象Phase、対象ManualまたはSnapshot、テスト合格が明確でなければならない。

## 2. Dual Approval Gate

Backup Triggerの状態は次で管理する。

| Designer Gate | User Test Gate | Backup |
|---|---|---|
| 未成立 | 未成立 | 不可 |
| 成立 | 未成立 | 不可 |
| 未成立 | 成立 | 不可 |
| 成立 | 成立 | 実行可能 |

推奨順序：

```text
Implementation Complete
  ↓
Implementer Status
  ↓
Designer Independent Review
  ↓
Required Follow-up Complete
  ↓
Current User Manual／Final Docs／Index
  ↓
Designer Final Readiness提示
  ↓
User Acceptance Test
  ↓
User Test Pass Declaration
  ↓
Designer Phase Completion／Next Phase Eligible Declaration
  ↓
Phase Backup／Integrity Verification
  ↓
Next Phaseの実質的変更
```

事情によりGate AとGate Bの順序が逆でも、両方が同じ対象状態を参照していればよい。

## 3. State Freeze

User TestとDesigner Declarationは、同じProject状態を対象にしなければならない。

いずれかのGate成立後、Backup作成前に次のMaterial Changeが入った場合、影響範囲に応じてReviewまたはUser Testを再実行する。

- `src/`、`tests/`、`config/`、`scripts/`の変更
- Dependency／Lock／Python Versionの変更
- Model Definition／Artifactの変更
- User Manualの操作結果に影響する変更
- Phase Acceptanceを変えるRequirements／Architecture／ADR変更

誤字だけのDocs追加など、実行状態へ影響しない変更でも、最新IndexとBackup Inventoryには反映する。

Backup Receipt／Snapshot Recordには、両Gateの対象文書とTimestampを記録する。

## 4. Triggerにならないもの

次だけではBackup Triggerとしない。

- Implementer Statusの作成
- 実装が終わったように見えること
- SubphaseのComplete／Accepted
- Designer Reviewだけの完了
- User Testだけの成功
- User Manual作成だけの完了
- 次PhaseのPlanning Docsが存在すること

`Phase 1-A`～`Phase 1-E`のようなSubphase完了だけで、Top-Level Phase Backupを必須としない。

## 5. Phase Completion Preconditions

設計者役は、次を確認した後にGate Aを成立させる。

- Phase配下の必須SubphaseがComplete／Accepted
- Blockerがない
- 未解決事項が次PhaseまたはKnown Limitationとして明記済み
- Independent Review完了
- 必要なRegression／Native Verification完了
- Current User Manualが実装と整合
- Phase Final Reviewが存在
- 最新Documentation IndexがCurrent Setを正しく示す
- User Acceptance Testの結果が確認可能
- Backup対象と除外対象の範囲が確定

UserはCurrent User Manualに従って受入テストを行い、Gate Bを明示する。

## 6. Phase単位と臨時Snapshot

定期BackupはTop-Level Phase単位とする。

```text
Phase 1
Phase 2
Phase 3
...
```

次の場合は、Dual Approval Gateとは別に臨時Snapshotを追加できる。

- 大規模Schema Migrationの直前
- 破壊的変更の直前
- Storage／Audit形式変更の直前
- Model／Backend交換の直前
- ユーザーが明示的にSnapshotを要求した場合

臨時SnapshotはPhase完了Backupと区別したName／Manifestを使用する。

## 7. Backup Set

Phase Backupは次の4点Setを基本とする。

```text
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS.zip
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_manifest.json
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_receipt.json
margpa-runtime-llm_phase_<n>_<milestone>_YYYYMMDDHHMMSS_sha512.txt
```

Phase 1候補：

```text
margpa-runtime-llm_phase_1_portable_runtime_mvp_YYYYMMDDHHMMSS.zip
```

Archive、Manifest、Receipt、SHA-512 Fileを同一Basename系列で紐付ける。

## 8. Archive Content

原則としてAllowlist方式を使用する。

Include候補：

```text
src/
tests/
config/
docs/
scripts/
notebooks/                 # 存在する場合

pyproject.toml
uv.lock
.python-version            # 存在する場合
.gitignore                 # 存在する場合
README*
LICENSE*
再構築に必要な明示済みRoot File
```

`config/`内でもSecret、Local OverrideまたはCredentialを含むFileは除外する。

## 9. Exclusion

```text
.venv/
models/
GGUF／Model Binary
__pycache__/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.ipynb_checkpoints/
.DS_Store
Cache
一時File
実行Log
Audit実データ
.env
Secret／Credential
Local Override
Backup Directory自体
```

Project Rootの`models/` Symbolic LinkはArchiveから原則除外する。Absolute Linkを別環境へ復元しないためである。Link Target／復元手順はManifestへ記録する。

## 10. Snapshot Manifest

Manifestは最低限次を含む。

### Identity

- Schema Version
- Snapshot ID
- Project Name
- Phase ID／Phase Name／Milestone
- Designer Completion／Next Phase Declaration
- User Acceptance Test Declaration
- 両DeclarationのTimestamp／対象Manual／対象Index
- Archive Creation Timestamp
- Current Documentation Index
- Phase Final Review
- Current Roadmap

### Source

- Included／Excluded PathとReason
- Included File Inventory／Size／SHA-512
- Manifest Canonicalization／SHA-512

### VCS

CurrentはGit未使用のため、事実として次を記録する。

```text
vcs.type        : none
vcs.commit_hash : null
vcs.tag         : null
```

Git未使用時はManifest SHA-512をSource Snapshot Identityとする。

### Environment／Model／Evidence

- OS／Architecture／Hardware
- Python／Backend／Acceleration
- Dependency Lock Hash
- Model Key／Role／Repository／File／Size／Format／Quantization
- Model Artifact／Definition SHA-512
- Symbolic Link復元方法
- Implementer Status
- Designer Final Review
- User Test Evidence
- Static／Default／Native Gate
- Known Issues／Observations
- User Manual

## 11. Manifest／Receiptの分離

ZIP本体のSHA-512をZIP内Manifestへ格納すると自己参照になるため、次を分離する。

```text
Manifest:
  Archive内Content、File Hash、Environment、Model、Evidence

Receipt:
  完成後のZIP File Name、Size、SHA-512、Manifest SHA-512

SHA512 Sidecar:
  簡易整合性検証用
```

ReceiptはArchive完成後に作るDetached Sidecarとする。

## 12. Docs Record

各Phaseの完了時に、設計者役は次の系列を`docs/operations/`へ作成する。

```text
phase_<n>_<milestone>_snapshot_record_YYYYMMDDHHMMSS.md
```

Snapshot Recordは次を人間向けに示す。

- Dual Approval Gate Evidence
- Phase完了条件
- Final Review／Current Index／Roadmap
- Test Evidence
- Model／Environment Summary
- Backup SetのNaming Rule
- Manifest／Receiptの責務
- Exclusion
- Restore Entry Point

## 13. Backup Location

BackupはProject Root内へ保存しない。

推奨論理構造：

```text
MARGPA-RUNTIME-LLM/
├─ margpa-runtime-llm/
└─ backups/
   └─ margpa-runtime-llm/
      └─ phase_<n>/
```

実体PathはBackup実行前にユーザーが確定する。同じMac／同じSSD上のCopyはDisk故障対策にはならないため、重要なBackupは第2Storageも検討する。

## 14. Integrity／Restore Verification

Backup完了条件：

1. ZIP構造検査がPass
2. ZIP SHA-512が計算済み
3. ReceiptとSHA512 Sidecarが一致
4. Manifest SHA-512が一致
5. InventoryとArchive Contentが整合
6. Secret／Model Binary／`.venv`が含まれない
7. Temporary DirectoryへのTest Extractが成功
8. Restore Entry Point／Setup Recipeが特定可能
9. Dual Approval Gate EvidenceがManifest／Snapshot Recordに存在

最低限のRestore Test：

- ZIPをTemporary DirectoryへExtract
- Expected Root File／Directory確認
- Manifest Inventory検証
- `uv.lock`／`pyproject.toml`確認
- Model除外確認
- Model Root復元手順確認
- Latest Index／Final Review／User Manual参照確認

Dependency Install、Model Download、Native Testまで行うFull Restore Drillは、別途ユーザー許可を必要とする。

## 15. Immutability／Retention

- Backup Setを上書きしない
- Timestampを持たせる
- 再作成時は新Timestampとする
- 古いPhase Backupを原則削除しない
- 再作成理由を新Manifest／Receiptへ記録する
- Backup Setを原則Renameしない

## 16. Git導入後

Gitは現時点で必須としない。将来導入した場合は、Commit Hash、Tag、Dirty State、RemoteをManifestへ追加する。

Git TagはSource History上のIdentity、ZIPは独立復元用Archive、Manifest／ReceiptはEvidenceとして併存させる。

## 17. Authorization Boundary

本PolicyはBackupのTiming／Content／Evidence規則を承認する。

本Policyの作成、Designer Gate、User Test Gateは、次を単独では自動解禁しない。

- External Backup Directoryの作成
- ZIP／Manifest／Receiptの実生成
- Project外へのWrite
- Cloud Upload
- External DriveへのCopy
- Git初期化／Commit／Tag

実際のBackup作成はDual Approval Gate成立後、ユーザーの指示または事前承認済みBackup Operator Scopeで行う。


<!-- SOURCE_END 6: docs/operations/phase_completion_backup_policy_20260719171836.md -->

---

<!-- SOURCE_BEGIN 7: docs/operations/phase_completion_backup_policy_20260720222402.md -->

### Source 7: `docs/operations/phase_completion_backup_policy_20260720222402.md`

- History Target: `docs/project/phases/phase_1/history/operations/phase_completion_backup_policy_20260720222402.md`
- Source SHA-512: `7b59bb0d28ff54cf5470d115ec7e4c3bf1a20c361bc8f3169e93b3768be555575d493c39601fcd2e38e553ceadb0f7abe47e14871ed022bc8bfbf662cc09792d`
- Source Size: `7043` bytes

# Phase完了Backup／GitHub公開運用Policy

- 文書ID: `phase_completion_backup_policy`
- 状態: `accepted_current`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 作成担当: 設計者役担当Task
- 承認者: ユーザー
- 対象: 全Top-Level Phase、Phase 1-ex、Backup、Source Archive、GitHub公開
- 正本言語: 日本語
- Privacy Policy: [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)
- supersedes: `phase_completion_backup_policy_20260719171836.md`

## 1. 基本決定

Projectは原則として、各Phaseの確定Snapshotごとに次の順序で運用する。

```text
Phase実装・検証
  → User Acceptance
  → Designer Phase完了／次Phase着手可能宣言
  → Backup Candidate作成
  → Archive Sanitation
  → Manifest／Hash／Restore検証
  → Backup確定
  → GitHub公開準備・公開
  → 次Phaseの実質的変更
```

各PhaseをGitHub上でも識別可能な履歴として残す。GitHub公開はBackupと同一の確定Source Snapshotを対象とし、別状態を黙って公開しない。

## 2. Backup Trigger

Backup Triggerは、同じProject状態について次の両Gateが成立した時点とする。

```text
Gate A: 設計者役がPhase完了と次Phase着手可能を宣言
Gate B: ユーザーが対象Manual／Snapshotの受入テスト合格を宣言
```

Implementer Status、Subphase完了、Designer Review、User Testのいずれか単独ではTriggerにならない。

一方のGate成立後にSource、Config、Dependency、Lock、Model Definition、User ManualへMaterial Changeが入った場合、必要なReviewまたはUser Testを再実行する。

## 3. PhaseごとのGitHub公開

通常運用では、各PhaseのBackup確定後に対応SnapshotをGitHubへ反映する。

最低限、次の対応関係を記録する。

- Phase ID／Milestone
- Backup Snapshot ID
- Archive SHA-512
- Documentation Index
- Git Commit Hash
- Git TagまたはRelease識別子
- 公開日時
- Known Issues

Branch、Tag、Release、Repository Visibility、GitHub Pages等の具体方式はPhase 1-exで再整備する。本文書だけではGit初期化、Remote作成、Push、公開範囲変更を許可しない。

## 4. 初回公開の例外

初回GitHub公開だけは、現在のPhase 1機能実装直後には行わない。

```text
Phase 1機能Snapshot確定
  → Phase 1-ex「運用再整備」
  → Phase 1-ex完了Gate
  → 公開候補Backup確定
  → 初回GitHub公開
```

初回公開SnapshotはPhase 1-ex完了後の状態とする。Phase 1-ex前のSnapshotはBackupとして保持できるが、初回GitHub公開対象にはしない。

## 5. Phase 1-ex

Phase 1-exをPhase 1と初回GitHub公開の間に追加する。

```text
Name   : Phase 1-ex
Purpose: 運用再整備
State  : Added／Requirements Pending
```

詳細要件、受入条件、実装範囲は後続会話で定義する。現時点ではPhaseの存在、目的、配置、初回公開Gateとの関係だけを確定し、Source変更や外部操作を許可しない。

## 6. Backup Set

Phase Backupは次を基本Setとする。

```text
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS.zip
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS_manifest.json
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS_receipt.json
margpa-runtime-llm_phase_<id>_<milestone>_YYYYMMDDHHMMSS_sha512.txt
```

Archive内のRoot Directoryは`margpa-runtime-llm/`とする。

## 7. Archive Include

原則Allowlist方式とし、再構築に必要な管理対象だけを入れる。

```text
src/
tests/
config/
docs/
scripts/
notebooks/       # 存在し、公開対象の場合
pyproject.toml
uv.lock
.python-version
.gitignore
README*
LICENSE*
明示承認されたRoot File
```

## 8. 毎回必須のArchive Sanitation

毎回、Backup Candidate作成後かつBackup確定前に、ZIP内の`margpa-runtime-llm/`を検査し、不要Fileをすべて除去する。

最低限の除外対象：

```text
.DS_Storeおよび大小文字違い
.venv/
models Symlink／models/
*.gguf／Model Binary
.git/
__pycache__/
*.pyc／*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage／htmlcov/
.ipynb_checkpoints/
.env／Credential／Secret
var/
実会話Log／Audit実Data
Temporary File／Editor Backup／OS Metadata
Local Override
Backup Directory自体
```

Allowlist外のFileは「必要そうだから」という推測で残さず、必要性を確認してから明示Includeする。

不要物を含むZIPを発見した場合、確定済みArchiveを直接上書きしない。未確定Candidateを破棄またはCleanな内容から再構築し、新Timestamp、Manifest、Receipt、SHA-512を生成する。

## 9. Sanitation完了条件

1. ZIPのRootが`margpa-runtime-llm/`だけである
2. InventoryがAllowlistと一致する
3. `.venv`、Model、Symlink、Cache、`.DS_Store`、Credentialがない
4. 個人固有Path、Hostname、Email、SecretのContent ScanがPassする
5. 第一者の公開Identityが`Nazuna Research`へ統一されている
6. Temporary DirectoryへのExtractが成功する
7. Manifest Inventoryと実Contentが一致する
8. Archive、Manifest、Receipt、SidecarのHashが一致する

## 10. Public Identity

第一者の公開Identityは常に次へ統一する。

```text
Nazuna Research
```

Git Author／Committer、GitHub Profile、README、License／Copyrightの扱いは、Privacy PolicyとPhase 1-exで確定する。第三者の正式なAttributionは維持する。

## 11. Manifest／Receipt

ManifestにはPhase、両Gate、Current Index、Include／Exclude Inventory、各File SHA-512、Environment、Model Metadata、Test Evidence、Known Issues、Git情報を記録する。

ZIP自身のHashは自己参照を避けるためDetached Receiptへ記録する。Git開始前は`vcs.type = none`、開始後はCommit Hash、Tag、Dirty State、Remoteを記録する。

## 12. Backup Location／Retention

- BackupはProject Root内へ保存しない
- Backup Setを上書きしない
- 再作成時は新Timestampを使う
- 古いPhase Backupを原則削除しない
- 同一Disk上だけでなく、第2Storageも検討する

## 13. Restore Verification

- Temporary DirectoryへExtract
- Expected Directory／Root File確認
- Manifest Inventory／SHA-512検証
- `pyproject.toml`／`uv.lock`確認
- Model／`.venv`／Local Artifact除外確認
- Model Root復元手順確認
- Latest Index／Final Review／User Manual確認

Dependency Install、Model Download、Native Testを伴うFull Restore Drillは別途許可を必要とする。

## 14. Authorization Boundary

本Policyは運用要件を確定するが、Backup実生成、Project外Write、Git操作、GitHub操作、Cloud Upload、公開を自動許可しない。それぞれ実行時のユーザー指示または事前承認Scopeを必要とする。

<!-- SOURCE_END 7: docs/operations/phase_completion_backup_policy_20260720222402.md -->

---

<!-- SOURCE_BEGIN 8: docs/operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md -->

### Source 8: `docs/operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md`

- History Target: `docs/project/phases/phase_1/history/operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md`
- Source SHA-512: `08a367057d00a35149a5d4ab3b7925af9de839d8e2226b09a40c3d7837fc4e8ad6d2f43b1305d1f1d58086314c7305f91cf0aac38e6c42ada153e33610808cce`
- Source Size: `3290` bytes

# Phase 1 Backup前 Privacy／Sanitation Scan

- 文書ID: `pre_phase_1_backup_privacy_and_sanitation_scan`
- 状態: `passed_with_documented_privacy_scrub`
- 作成日時: `2026-07-26 12:13:46 JST`
- 更新日時: `2026-07-26 12:13:46 JST`
- Snapshot: `20260726121346`
- 作成担当: 設計者役担当Task
- 対象: Phase 1確定Backup Candidate作成前の管理対象
- Pre-backup Index: [documentation_index_20260726121346.md](../history/documentation_index_20260726121346.md)
- 統合記録: [phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md](../history/operations/phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record_20260726120229.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Phase 1 Backup Candidate作成前のPrivacy／Sanitation ScanをPassとする。

```text
実個人名                         : 0
実個人Email                      : 0
実個人固有／Users Absolute Path  : 0
Credential実値                   : 0
Secret File                      : 0
旧Public Handle実値              : 0 after scrub
```

## 2. Privacy Exception Scrub

過去の実装担当Statusに、実行済み検索Patternを説明する目的で旧Public HandleのLiteralが1件残っていた。

対象：

```text
docs/handoffs/implementer_status_phase_1g_review_follow_up_20260721121817.md
```

Privacy／Public Identity例外として、旧HandleのLiteralを次へ匿名化した。

```text
<legacy-public-handle-pattern>
```

検索結果が0件であったこと、Exit Codeの意味および第三者Provenanceを機械置換しなかったというStatusの意味は変更していない。

Append-only原則の例外は、既存Policyで認められたPrivacy／Identity Scrubとして適用した。

## 3. Expected Fixtures

次は実個人情報ではなく、Privacy／Redaction／Markdown Security Test用の架空Fixtureであるため保持する。

```text
/Users/example/...
test@example.com
https://example.com
```

Docs内の`/Users/...`は、禁止対象Pathを説明する抽象表現であり、実Account Pathではない。

## 4. Archive Sanitation対象

Project Treeに次が存在するが、Backup Archiveから除外する。

```text
.DS_Store
.venv/
models Symbolic Link
.mypy_cache/
.pytest_cache/
.ruff_cache/
__pycache__/
*.pyc
*.pyo
.coverage
htmlcov/
.env
.env.*
var/
*.log
```

これらをProject Treeから削除することは本Scanの目的ではない。Sanitized Staging TreeへCopyする際にAllowlist＋Exclude Ruleで除外する。

## 5. Allowed Public Runtime References

次は個人連絡先ではなく、Projectまたは外部Runtimeの技術参照であるため保持できる。

- Lightning Public Preview URL
- Hugging Face Model Repository
- GitHub Organization／Repository候補
- Official Documentation URL
- Model ID／Revision／Hash
- Lightning内の中立的Runtime Path

公開URLの有効性または常時稼働は保証しない。

## 6. Backup Gate

本Scanにより、Sanitized Candidate作成へ進める。

Candidate作成後に改めて次を検証する。

- Inventory Allowlist
- Symlink不存在
- Model Binary不存在
- Cache／OS Metadata不存在
- Privacy Content Scan
- File SHA-512
- Archive SHA-512
- Temporary Restore
- Restored Inventory／Hash一致

<!-- SOURCE_END 8: docs/operations/pre_phase_1_backup_privacy_and_sanitation_scan_20260726121346.md -->

---

<!-- SOURCE_BEGIN 9: docs/operations/public_identity_docs_scrub_report_20260721112925.md -->

### Source 9: `docs/operations/public_identity_docs_scrub_report_20260721112925.md`

- History Target: `docs/project/phases/phase_1/history/operations/public_identity_docs_scrub_report_20260721112925.md`
- Source SHA-512: `f78a09a3aa2210a9def2cfc9fadc05eebd7a1e5846bd671751952598a65ffa8c58826d45fd2bbfa701adc7023abfb4d1fe78154de6fe40fb1a56e469bdd84984`
- Source Size: `4998` bytes

# Docs公開名義洗浄Report

- 文書ID: `public_identity_docs_scrub_report`
- 状態: `completed`
- 作成日時: `2026-07-21 11:29:25 JST`
- 更新日時: `2026-07-21 11:29:25 JST`
- Snapshot: `20260721112925`
- 実施担当: 設計者役担当Task
- 正本言語: 日本語
- 根拠: ユーザーの明示的な全Docs名義統一指示
- supersedes: なし

## 1. Objective

`docs/`内に残っていた廃止済み第一者名義を除去し、第一者の公開名義を`Nazuna Research`へ統一する。

削除対象の実値は、本Reportへ再掲しない。

## 2. Rule Applied

```text
Human-readable Name  : Nazuna Research
Project Internal Name: Nazuna Research Governance LLM
Machine-safe Slug    : nazuna-research
Repository Owner     : margpa-labs
```

個人GitHub AccountへのCommit帰属は一般表現へ変更し、Account HandleをDocsへ残さない。

## 3. Scope

```text
Target Root        : docs/
Matched Occurrence : 67
Affected Files     : 32
Edit Method        : apply_patch
```

対象Category：

- Requirements
- Architecture
- Governance
- Handoffs
- Documentation Index
- User Manual
- Operations Policy／Report

## 4. Affected File Manifest

```text
docs/architecture/governance_definition_platform_architecture_20260719112304.md
docs/architecture/public_documentation_and_phase_compilation_architecture_20260720231036.md
docs/documentation_index_20260720220216.md
docs/documentation_index_20260720222402.md
docs/documentation_index_20260721111659.md
docs/governance/governance_definition_catalog_20260719112304.md
docs/governance/runtime_governance_20260718174637.md
docs/handoffs/common_project_handoff_20260718174637.md
docs/handoffs/common_project_handoff_20260718193435.md
docs/handoffs/common_project_handoff_20260719142558.md
docs/handoffs/common_project_handoff_20260719164641.md
docs/handoffs/common_project_handoff_20260719171836.md
docs/handoffs/common_project_handoff_20260720220216.md
docs/handoffs/common_project_handoff_20260720222402.md
docs/handoffs/common_project_handoff_20260720231036.md
docs/handoffs/common_public_identity_and_naming_rule_20260721111659.md
docs/handoffs/public_documentation_handoff_20260718174637.md
docs/operations/phase_completion_backup_policy_20260720222402.md
docs/operations/publication_privacy_scrub_report_20260720220216.md
docs/requirements/documentation_rules_20260718193435.md
docs/requirements/documentation_rules_20260719142558.md
docs/requirements/documentation_rules_20260719171836.md
docs/requirements/documentation_rules_20260720220216.md
docs/requirements/documentation_rules_20260720222402.md
docs/requirements/generic_governance_definition_platform_requirements_20260719112304.md
docs/requirements/phase_1_ex_publication_identity_access_and_license_requirements_reservation_20260721111659.md
docs/requirements/project_requirements_20260718174637.md
docs/requirements/project_requirements_20260718193435.md
docs/requirements/public_identity_and_personal_information_policy_20260720220216.md
docs/requirements/public_identity_and_personal_information_policy_20260721111659.md
docs/user_manual/phase_1_macos_user_manual_20260719004209.md
docs/user_manual/phase_1_macos_user_manual_20260719171836.md
```

Manifestの記載数と事前Searchの対象File数は32で一致する。最終合格条件はFile数だけでなく、Target Root全体の残存0件で判定する。

## 5. Semantic Transformation

単純置換だけでなく、次を文脈別に修正した。

- Author／Maintainer／Public Identityを`Nazuna Research`へ統一
- Project通称を`Nazuna Research Governance LLM`へ統一
- Package／Namespace例をMachine-safe Slugへ変更
- 個人GitHub Accountへの帰属を、Handleなしの一般表現へ変更
- 旧名義を再掲する移行説明／禁止例を一般表現へ変更
- 名義例外の判断権限を設計者役Taskへ限定

## 6. Append-only Exception

今回の処理は、公開識別情報の除去を目的としてHistorical Docsを直接変更したため、Strict Append-onlyのPrivacy Exceptionに該当する。

結果として、対象Historical Fileは作成時点のBitwise内容と一致しない。過去に計算されたFile Size／Digestが存在する場合、それらを現在FileのDigestとして使用しない。

将来のPhase 1-exでは、公開候補Artifactから新しいManifest／Digestを再計算する。

## 7. Verification

2026-07-21 11:29:25 JSTに、`docs/`全体へCase-insensitive Searchを実行した。

```text
Deprecated First-party Name Match : 0
Result                            : PASS
```

Machine-safe SlugはGovernance Package／Namespace例にだけ残っている。

## 8. Non-scope

今回は次を走査・変更していない。

- `src/`
- `tests/`
- `scripts/`
- `config/`
- Root Metadata
- Git Metadata
- Model Artifact
- External Service
- GitHub Repository

これらはPhase 1-exのRead-only Preflight後に扱う。

## 9. Completion

`docs/`内の第一者名義統一は完了した。

<!-- SOURCE_END 9: docs/operations/public_identity_docs_scrub_report_20260721112925.md -->

---

<!-- SOURCE_BEGIN 10: docs/operations/publication_privacy_scrub_report_20260720220216.md -->

### Source 10: `docs/operations/publication_privacy_scrub_report_20260720220216.md`

- History Target: `docs/project/phases/phase_1/history/operations/publication_privacy_scrub_report_20260720220216.md`
- Source SHA-512: `90823e0490e380fac1513140cd008550b9c1864669eaeaa233112548735665728241d69346228d372021ec3150a42e5e4bf5be9832ddcc83d6b01057f5b1de89`
- Source Size: `3118` bytes

# 公開前プライバシーScrub実施記録

- 文書ID: `publication_privacy_scrub_report`
- 状態: `complete`
- 作成日時: `2026-07-20 22:02:16 JST`
- 更新日時: `2026-07-20 22:02:16 JST`
- Snapshot: `20260720220216`
- 実施担当: 設計者役担当Task
- 正本言語: 日本語
- Policy: [public_identity_and_personal_information_policy_20260720220216.md](../history/requirements/public_identity_and_personal_information_policy_20260720220216.md)
- supersedes: なし

## 1. 目的

Phase 1公開準備に先立ち、Project管理対象Fileから第一者の非公開IdentityとLocal環境情報を除去し、公開Identityを`Nazuna Research`へ統一する。

## 2. 対象

Project Root以下の管理候補Fileを再帰走査した。次は公開対象外または第三者管理物のため本文置換対象から除外した。

- `.venv/`
- `models` Symlinkの参照先とModel本体
- `.git/`
- Tool Cache、Bytecode、Coverage Data

Symlinkを辿る走査は行わず、外部Model Storageを変更していない。

## 3. 実施内容

- 第一者の旧Identity表記を`Nazuna Research`へ統一
- 内部通称を`Nazuna Research Governance LLM`へ統一
- 個人固有のProject Root、Definition Source、Model Rootを抽象Pathへ置換
- Local Temporary Pathを再現不能なPlaceholderへ置換
- 旧Handle表記揺れを`Nazuna Research`へ統一
- `.DS_Store`、Coverage Data、Project内Cache／Bytecodeを除去
- File名についても旧Identity表記を走査
- Email、連絡先、Private Key、SecretらしきPatternを走査

## 4. 最終結果

管理対象File内に、第一者の旧Identity、Local Account名、個人固有Project Path、個人Email、Private Keyの残存を認めなかった。

次は意図的に保持した。

- `example`を用いた架空のAbsolute Path: Privacy RedactionのUnit Test Data
- `/Users/...`という抽象表現: User固有Absolute Pathを禁止する設計例
- Model／Library／Repository／Licenseの第三者正式名称
- `Nazuna Research`

## 5. Local-only境界

`.venv/`と`models` SymlinkはLocal実行のため現存するが、`.gitignore`および公開方針で公開対象外である。公開Archive作成時は、これらが収録されていないことをManifestで再確認する。

Filesystem Owner等のOS MetadataはRepository本文ではない。Archive作成ToolがOwner Metadataを保存する場合は、公開用Archive生成時に正規化する。

## 6. 履歴への影響

Privacy／Security例外により、個人情報を含んでいた既存Docsは匿名化された。したがって、一部の過去Snapshotは作成当時のBit列と一致しない。

これは意図的な安全上の変更であり、削除した値を履歴復元のために再記録しない。文書上のDecision、Phase状態、設計内容は保持した。

## 7. 再実施条件

次の時点で再走査する。

- Git初期化前
- GitHub Push前
- Source Archive／Backup作成前
- README／Public Docs完成後
- Screenshot、Sample Log、Evidence追加後
- 外部環境で生成したLogの取り込み前

<!-- SOURCE_END 10: docs/operations/publication_privacy_scrub_report_20260720220216.md -->

---

<!-- SOURCE_BEGIN 11: docs/operations/runtime_and_absolute_path_verification_20260720222402.md -->

### Source 11: `docs/operations/runtime_and_absolute_path_verification_20260720222402.md`

- History Target: `docs/project/phases/phase_1/history/operations/runtime_and_absolute_path_verification_20260720222402.md`
- Source SHA-512: `04bfadd7258e33dbb7be140e0a342ff65c6ea5b2c3206e6e688560f6521dc0f82c6ab82ca8f8e13d37b3b479c03c41118974da2699c0175fb3c4a0ac954ab6bd`
- Source Size: `2663` bytes

# Runtime動作・絶対Path境界 確認記録

- 文書ID: `runtime_and_absolute_path_verification`
- 状態: `verified_with_external_environment_pending`
- 作成日時: `2026-07-20 22:24:02 JST`
- 更新日時: `2026-07-20 22:24:02 JST`
- Snapshot: `20260720222402`
- 実施担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: なし

## 1. 動作確認結果

Privacy Scrub後のMac環境で次を確認した。

```text
Default Test            : 181 passed／3 deselected
Ruff                    : Pass
Mypy                    : Pass／70 source files
Model Smoke on Mac Metal: 2 passed／1 skipped
```

Model Smokeの1 SkipはLightning用Profile Environment未指定による期待されたSkipである。

Sandbox内ではMetal Deviceが公開されず`llama_context`作成に失敗したが、Mac実機Execution Contextで再実行して2件Passした。Privacy ScrubによるMac Phase 1 Runtimeの機能破損は確認されなかった。

Lightning CUDA／CPUのNative Verificationは別Gateであり、未確認である。

## 2. Production Codeの絶対Path

次の管理対象を走査した結果、個人固有の`/Users/...` Pathは0件だった。

- `src/`
- `scripts/`
- `config/`
- Root Project Metadata／Lock／Ignore設定

Production Runtimeは個人固有Home PathをSourceへHard-codeしていない。

## 3. Test Fixture

`tests/`には`/Users/example/...`形式の架空Pathが存在する。これはNative ErrorからAbsolute PathをRedactするPrivacy Test Dataであり、実在するAccount情報ではない。

## 4. Local `.venv/`

`.venv/`にはPython仮想環境の仕様により、作成時環境の絶対Pathが自動生成される。

- `pyvenv.cfg`のBase Python Path
- Activate Scriptの`VIRTUAL_ENV`
- Console Entry PointのInterpreter Path
- Python ExecutableへのSymlink

`.venv/`は移植Artifactではなく、別環境でLockとSetup Recipeから再構築する。Git、ZIP、GitHub、公開物から除外する。

## 5. `models` Symlink

Project Rootの`models`はLocal Model Storageへの絶対Symlinkである。Production CodeのHard-codeではない。

SymlinkとTargetのModel本体はGit、ZIP、GitHub、公開物から除外し、Model配置規約と復元手順だけをManifestへ記録する。

## 6. 結論

```text
Managed Production Code : 個人固有絶対Pathなし
Tests                   : 架空Redaction Fixtureのみ
Local .venv             : 絶対Pathあり／正常／公開除外
Local models Symlink    : 絶対Pathあり／正常／公開除外
Mac Phase 1 Runtime     : Native Model Smoke Pass
Lightning Runtime       : Native Verification Pending
```


<!-- SOURCE_END 11: docs/operations/runtime_and_absolute_path_verification_20260720222402.md -->

---

