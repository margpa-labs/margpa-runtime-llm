# Phase 6 DeepSeek 8B Quantization — Codex設計者兼実装者役 Exact Handoff

```yaml
document_id: phase_6_deepseek_quantization_codex_designer_implementer_exact_handoff_20260823135123
status: accepted_active_on_receipt
phase: phase_6
workstream: deepseek_local_quantization_only
from: プロジェクト責任者兼設計統括者役
to: 設計者兼実装者役
created_at: 2026-08-23 13:51:23 JST
user_authority: explicit_quantization_delegation
automation: bounded_long_run
closure_target: quantization_complete_candidate
git_mutation: prohibited
source_mutation: prohibited
runtime_load: prohibited
```

## 1. Mission

Download済みの公式`deepseek-ai/DeepSeek-R1-0528-Qwen3-8B` Safetensors Snapshotから、Mac Local候補となるGGUF `Q4_K_M` Derived Artifactを作成し、Provenance、SHA-512、Size、RecipeおよびIntegrity Evidenceを固定する。

本Taskの完了点は**量子化Artifactの作成と構造的検証まで**である。Model Definition登録、Runtime Load、Qwen／DeepSeek切替、Benchmark、Source実装、Stable Docs更新、Roadmap更新、Git操作は行わない。

Claude側は別Taskで自己評価文書を作成中である。本TaskはModel専用Subtreeだけを扱い、Claude側のSource／Test／Phase 6 Reworkと競合させない。

## 2. Mandatory Reading Order

作業開始前に次を全文読む。

1. `docs/project/current/automation_cross_provider_compaction/automation_cross_provider_compaction_governance_integrated_ja.md`
2. `docs/project/shared/task_roles/role_authority_matrix_ja.md`
3. `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`
4. `docs/project/phases/phase_6/history/operations/phase_6_exact_model_authority_receipt_ja_20260822212732.md`
5. `docs/project/phases/phase_6/history/operations/phase_6_dependency_acquisition_authority_receipt_ja_20260822220804.md`
6. `docs/project/phases/phase_6/history/index/phase_6_a_wu002_recipe_freeze_and_dependency_evidence_ja_20260822222500.md`
7. `docs/project/phases/phase_6/history/index/phase_6_a_wu002_pretokenizer_blocker_ja_20260822223100.md`
8. 本Handoff

Role正本の構成が変化している場合は、`docs/project/shared/task_roles/`内のCurrent Role／Authority文書を動的に解決する。存在しない固定Pathを作って読了を捏造しない。

## 3. Known Starting State

```text
Canonical Repository : deepseek-ai/DeepSeek-R1-0528-Qwen3-8B
Exact Commit         : 6e8885a6ff5c1dc5201574c8fd700323f23c25fa
Canonical Payload    : 16,388,927,770 bytes／10 Model Files
Canonical Mutation   : PROHIBITED
Current Converter    : Homebrew llama.cpp build 7970
Previous Attempt     : HF → Q8_0 failed before output creation
Previous Error       : unknown BPE pre-tokenizer hash
Measured chkhsh      : 0d75215efe33c49084836cb245f2fa78de4b3858f5a3e54d5e1fd27f4ce33b05
Q8 Intermediate      : NOT CREATED
Q4_K_M Artifact      : NOT CREATED
Runtime Load         : NOT EXECUTED
```

以前の失敗を同じTool／同じRecipeで無目的に再試行しない。最初に対応済みConverterを確保する経路を設計し、Tool compatibilityを小さなPreflightで確認する。

## 4. Exact Filesystem Authority

### 4.1 Logical／Resolved Root

```text
Logical Model Root : margpa-runtime-llm/models
Resolved Target    : /Users/Nazuna Research/models/margpa-runtime-llm/models
```

Symbolic Linkであることを理由にResolved Target全体へ権限を拡張しない。次のExact Subtreeだけを扱う。

| Subtree | Authority |
|---|---|
| `models/main/deepseek-r1-0528-qwen3-8b/huggingface/` | Canonical root payload Read-only。`.cache/`／`figures/`除外 |
| `models/main/deepseek-r1-0528-qwen3-8b/conversion_work/` | 本Taskの新規Toolchain／Build／Q8 Intermediate／Log作成 |
| `models/main/deepseek-r1-0528-qwen3-8b/gguf/` | 新規Q4_K_M Artifact作成 |
| `models/main/deepseek-r1-0528-qwen3-8b/manifests/` | 新規Quantization Manifest／Digest Evidence作成 |

既存Fileは上書き、削除、移動、Rename、再利用しない。開始Preflightで同名Artifactまたは未知の既存内容を検出した場合は、内容を破壊せずInventoryを作成し、Collision対象だけ停止する。

### 4.2 Repository内Docs Authority

許可する書込みは次の新規Append-only Evidenceだけである。

- `docs/project/phases/phase_6/history/operations/phase_6_deepseek_quantization_*_ja_<timestamp>.md`
- `docs/project/phases/phase_6/handoffs/phase_6_deepseek_quantization_complete_candidate_handoff_ja_<timestamp>.md`

既存History、Stable Current Docs、Phase Index、Roadmap、Source、Config、Test、Lockfileを編集しない。

## 5. Toolchain Resolution Authority

### 5.1 Priority Order

1. 現在のProject `.venv`および既存Read／Execute Toolで互換性を解消できるか確認する。
2. 現在のHomebrew Converterが非対応であることを再確認した場合、公式`ggerganov/llama.cpp`の対応済みSource Snapshotを、Exact immutable Revisionで`conversion_work/toolchain/`へ新規取得する。
3. 取得した公式Source内ConverterとBundled `gguf-py`をProject-localに実行する。
4. 既存`llama-quantize`が出力GGUFと非互換の場合だけ、同じ公式Source SnapshotからProject-local `conversion_work/toolchain/build/`へ必要最小BinaryをBuildする。

Homebrew、System Python、Global Package、OS設定、Project `.venv`、`pyproject.toml`、`uv.lock`を変更しない。

### 5.2 Scoped Network Exception

Userの量子化実行指示を成立させるため、次のRead／Downloadだけを本Taskへ限定許可する。

- 公式`github.com/ggerganov/llama.cpp`のPublic Source／Archive／Commit Metadata。
- Exact Model `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`に関する公式Hugging Face Public Metadata。ただし新たなWeight Downloadは行わない。

条件：

- Credential、Login、Token、License同意、Private Mirror、任意Git Repositoryを使わない。
- ToolchainはExact immutable Revisionへ固定し、Mutable `main`だけをEvidenceにしない。
- Download先は`conversion_work/toolchain/`だけとする。
- Repository全体の`git clone`は使用しない。公式Source Archiveまたは必要最小Fileを取得し、Source RevisionとDigestを記録する。
- `convert_hf_to_gguf_update.py`等でHash Tableを更新する場合も、ToolchainのProject-local Copyだけを変更し、Official Canonical Snapshot、Homebrew Tool、Project Sourceを変更しない。
- Sourceに未Reviewの任意Patchを加えて変換成功を捏造しない。Model固有Hashを追加する場合、公式Metadataから再導出し、Patch、根拠、Before／After DigestをManifestへ記録する。

## 6. Disk／Resource Gate

各Material Stepの直前と直後に、Resolved Model Filesystemの空き容量を確認する。

```text
Minimum Preservation Floor : 64 GiB
Expected Intermediate       : Q8_0
Final Quantization          : Q4_K_M
Residency／Load             : NOT PERFORMED
```

- ProjectedまたはCurrent Free Spaceが64 GiB未満になるWriteを開始しない。
- 容量不足を理由にCanonical、V4、Qwen、Intermediate、Cache、User Dataその他既存Fileを削除しない。
- Conversion中に異常なMemory Pressure、Thermal状態、Disk急減またはUser停止指示を検出した場合は、Processを安全停止し、Partial Artifactを無断削除しない。
- Claude側が実Model／Full Testを開始したことを検出できた場合、File競合がなくてもResource競合を避けるため、現在のMaterial Stepを安全な境界まで完了して一時停止できる。

## 7. Exact Work Sequence

### DQ-001 — Read-only Preflight

- Mandatory Readingを完了する。
- Exact Task Authority、Logical／Resolved Path、Existing Destination State、Free Space、Tool Versionを確認する。
- Canonical SnapshotのExact Commit、File Count、Total Sizeおよび主要Manifest整合をRead-onlyで再確認する。
- Canonical Full Weight SHA-512の再計算は、変換が全Byteを読む工程と重複するため、必要性とCostを判断してManifestへEvidence Gradeを記録する。未計算を計算済みとしない。

### DQ-002 — Compatible Converter Freeze

- 前回Pre-tokenizer Failureを再現可能な最小条件で照合する。
- 対応済み公式Converter Revisionを動的に選定する。
- Converter、Bundled Python Module、QuantizerのRevision／SHA-512／Version／Commandを固定する。
- Canonical Sourceを変更しないRecipeをFreezeする。

### DQ-003 — HF Safetensors → Q8_0 Intermediate

- 出力は`conversion_work/`の新規Exact File名とする。
- Logも同Subtree内へ保存する。
- Process終了Code、Output Size、GGUF Metadataの構造検証、SHA-512、Disk Before／Afterを記録する。
- Partial／Unknown outputを成功扱いしない。

### DQ-004 — Q8_0 → Q4_K_M

- Q8_0 Intermediateを入力として、`gguf/`へ新規Q4_K_M Artifactを作成する。
- Q4_K_MのExact Scheme、Tool Revision、Command、Exit Code、Size、SHA-512およびGGUF構造検証を記録する。
- Intermediateは無断削除しない。

### DQ-005 — Provenance／Manifest

`manifests/`へ、少なくとも次を持つCanonical JSONまたはMarkdown Manifestを新規作成する。

- Official Repository／Exact Commit。
- Canonical Input Inventory／Evidence Grade。
- Converter／Quantizer Source、Revision、SHA-512。
- Dependency／Python／Platform情報。
- Full sanitized Recipe／Command。
- Q8_0／Q4_K_M File名、Size、SHA-512。
- Quantization Scheme。
- Start／End Timestamp。
- Disk Before／After／64 GiB Gate。
- Warning、Unsupported、Manual Patch、Retry、Resumeの有無。
- Canonical／Qwen／V4／Source／Git Mutation 0の範囲付き主張。

### DQ-006 — Completion Handoff

新規`phase_6_deepseek_quantization_complete_candidate_handoff_ja_<timestamp>.md`を作成し、プロジェクト責任者兼設計統括者役へ直接返す。

## 8. Explicit Prohibitions

- `models` Resolved Targetの親、Sibling Model、DeepSeek V4、Qwen、Guard、Judgeへの接触。
- DeepSeek Canonical SnapshotのWrite／Delete／Move／Rename／Repair。
- Existing Derived／Intermediate／Log／ToolchainのOverwrite／Delete。
- Model Definition登録、Runtime Load、Inference、Benchmark、Promotion、Default変更。
- Source、Frontend、Tests、Config、Stable Docs、Roadmap、Phase Index、GitのMutation。
- User実`runtime_data`、Provider Memory、`.claude`、`.codex`への接触。
- Homebrew／System／Global Package変更。
- Project外Temporary、Home Cache、OS Temporaryへの意図的Write。
- 容量確保のための自動Cleanup。
- Conversion成功前の`SUPPORTED`宣言。

## 9. Stop Conditions

次の場合だけ停止する。

1. Exact Subtree外Read／Write／Executeが不可避。
2. Credential、課金、License同意、Private Artifactが必要。
3. Canonical Snapshot変更または既存Artifact上書きが必要。
4. 64 GiB Disk Floorを維持できない。
5. 公式対応済みToolchainでもTokenizer／Architectureが安全に変換不能。
6. Output Integrityを検証できない。
7. User停止指示、異常Memory Pressure、Thermal／Disk異常。
8. Claude側作業との実Resource競合により、どちらかの検証精度を損なう。

通常のTool Version差、Converter選定、Project-local Build、Recipe調整、再開可能なCommand Failure、長時間処理はMicro-confirmation対象ではない。Authority内で自律解決し、Material BoundaryでRecoveryを残す。

## 10. Return Contract

Complete Candidateは次を全て満たす場合だけ返す。

```text
Q4_K_M Artifact              : CREATED
Q4_K_M Structural Validation : PASS
Q4_K_M SHA-512／Size         : RECORDED
Q8 Intermediate Status       : RECORDED／PRESERVED
Canonical Mutation           : 0
Qwen／V4／Sibling Mutation    : 0
Source／Test／Config Mutation : 0
Git Mutation                 : 0
User runtime_data Contact    : 0
Manifest                     : CREATED
Disk Floor                   : PASS
Runtime Load／Benchmark      : NOT PERFORMED
Open Critical Finding        : 0
```

失敗時は`BLOCKED`または`SAFE_UNSUPPORTED`を機械的に選ばず、Current Transitionへの影響、自力解消可能性、再現手順、Partial Artifact、必要Authorityおよび安全な再開入口を正確に記録する。
