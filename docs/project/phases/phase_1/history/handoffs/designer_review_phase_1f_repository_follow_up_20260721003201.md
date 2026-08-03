# Phase 1-F Repository Follow-up 設計Review

- 文書ID: `designer_review_phase_1f_repository_follow_up`
- 状態: `changes_requested_minor_static_gate_before_lightning`
- 作成日時: `2026-07-21 00:32:01 JST`
- 更新日時: `2026-07-21 00:32:01 JST`
- Snapshot: `20260721003201`
- 作成担当: 設計者役担当Task
- 対象: Phase 1-F Repository Review Follow-upとLightning搬入可否
- 正本言語: 日本語
- 実装報告: [implementer_status_phase_1f_repository_review_follow_up_20260721001705.md](implementer_status_phase_1f_repository_review_follow_up_20260721001705.md)
- 前回Review: [designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md](designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md)
- 要件: [phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md](../requirements/phase_1f_lightning_cross_environment_runtime_requirements_20260719202333.md)
- ADR: [adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md](../adr/adr_0015_phase_1f_lightning_and_python_312_support_20260719202333.md)
- 実装Handoff: [implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md](implementer_handoff_phase_1f_lightning_cross_environment_runtime_20260719202333.md)
- 最新Index: [documentation_index_20260721003201.md](../documentation_index_20260721003201.md)
- supersedes: `designer_review_phase_1f_lightning_cross_environment_runtime_20260720235113.md`

## 1. Review結論

前回Reviewで指摘したHigh 2件、Medium 2件、Low 1件は、Repository実装上すべて適切にFollow-upされている。

Mac実機ではDefault Test、Model Smoke、Strict Acceptanceが通り、Strict Acceptanceの必須Checkは22件すべて合格した。GPU Offloadについても、Capability／Request／Observationが分離され、Metal Model LoadをObservation SourceとするEvidenceが記録されている。

ただし、実装報告が実行した限定範囲の`mypy`は通っている一方、Project全体の正式な`mypy`を独立実行するとTestコード1箇所で失敗する。Lightningへ一度だけまとめて搬入する前に直せる局所的な残件であるため、本Follow-upはMinor Changes Requestedとする。

また、Lightning Target上のPreflight、Python 3.12.11 Dependency Sync、CUDA／CPU Native Gateは未実行であり、Phase 1-F全体の完了はまだ宣言しない。

```text
前回High Finding解消       : 2／2
前回Medium Finding解消     : 2／2
前回Low Observation解消    : 1／1
新規Medium Finding         : 1
Default Test               : Pass／183 passed、3 deselected
Mac Model Smoke            : Pass／2 passed、1 skipped、1 deselected
Mac Strict Acceptance      : Pass／22 of 22 required checks
Full Project Mypy          : Fail／1 error
Lightning Preflight        : Not Run
Lightning CUDA Native Gate : Not Run
Lightning CPU Candidate    : Not Run
Final Decision             : Changes Requested／Minor Follow-up
Phase 1-F Completion       : Not Accepted Yet
```

## 2. 前回Findingの解消確認

### 2.1 Actual GPU Offload Evidence

`GpuOffloadEvidence`により、次が分離された。

```text
supported
requested
observed
observation_source
process_gpu_memory_bytes
```

- CUDAでは、Current Processの`nvidia-smi` GPU Memoryが正値の場合だけ`observed=true`となる。
- GPU使用を確認できない場合は、CUDA Buildや`gpu_layers=-1`だけを根拠にGPU Runtimeを主張せずFail Closedとなる。
- CPU Profileでは、Backend CapabilityとRuntime Request／Observationが分離される。
- Pre-load Environment Verifierは、未実行のActual Observationを成功扱いしない。
- Mac Metalでは、Model／Context Load成功後の`metal_model_load`がObservation Sourceとして記録される。

前回High Findingは解消した。

### 2.2 Acceptance ProbeのFail Closed

Acceptance Scriptは22件の必須条件を`required_checks`へ集約し、全件合格時だけ`all_required_checks_passed=true`とする。1件でも不合格、または予期しない例外があれば非0で終了する。

Setup Scriptも`set -euo pipefail`によりProbe失敗を成功扱いしない。前回High Findingは解消した。

### 2.3 Language／Thinking Evidence

- 日本語、英語、Streaming、Post-cancelで識別可能なMarkerを使用する。
- Resolved Language Policyと、Modelへ渡すSystem Messageの両方を検証する。
- Thinkingは正常なReasoning／Final分離、Complete Parse、`finish_reason != length`を必須とする。
- Hidden／VisibleはCanonical ContentとPresentation Contentを分けて検証する。
- Unclosed Thinkingの安全処理は正常系Acceptanceとは分離してUnit Testで維持する。

前回Medium Findingは解消した。

### 2.4 Lightning Environment Mode

`auto`、`studio-active`、`project-venv`の3 Modeが追加され、Lightning StudioのPersistent Active EnvironmentとProject-local Venvのどちらにも対応可能な構造になった。

大容量Upload前に単独実行可能なRead-only Preflightも追加された。Target実行結果はまだないが、Repository上の環境前提固定は解消した。

### 2.5 `nvcc`判定順

Native CUDA Rebuildが必要な場合だけ`nvcc`を要求する順序へ修正された。既存CUDA Build再利用とCPU Candidate確認を、不必要な`nvcc`必須判定で停止させない構造になった。

前回Low Observationは解消した。

## 3. 新規Finding

### 3.1 Medium: Full Project MypyがTestコードで失敗する

対象：

```text
tests/unit/inference/test_deployment_platform.py:698
```

独立実行結果：

```text
tests/unit/inference/test_deployment_platform.py:698: error:
Module "margpa_runtime_llm.adapters.model_backends.llama_cpp.runtime_detection"
does not explicitly export attribute "subprocess"  [attr-defined]
Found 1 error in 1 file
```

Testは、`runtime_detection_module.subprocess.run`をMonkeypatchしている。Runtime Moduleの非公開Import DetailへTestから到達する形になり、MypyのExplicit Package Base／Export規則に反する。

Required Follow-up：

- Testから非公開Module Memberへ到達しない形へ変更する。
- `subprocess.run`自体を適切にPatchするか、GPU Memory QueryのCommand Runner境界を注入可能にする。
- 修正後は限定対象ではなく、Project設定どおりのFull `mypy`を実行する。
- `ruff format --check`、`ruff check`、`pytest -q`も再確認する。

これはProduct Runtime FailureではなくTestのStatic Typing Failureであり、修正範囲も局所的である。ただしProjectの正式品質Gateが未合格であるため、Lightning搬入前に解消する。

## 4. Independent Verification

### 4.1 Static／Default Gate

```text
ruff format --check src scripts tests       : Pass／70 files
ruff check src scripts tests                : Pass
python -m compileall -q src scripts tests   : Pass
bash -n Lightning Setup／Preflight           : Pass
uv lock --check --offline                   : Pass／117 packages
pytest -q                                   : Pass／183 passed、3 deselected
Full Project mypy                           : Fail／1 error
```

### 4.2 Mac Native Gate

```text
pytest -q -m model_smoke tests/integration
Result: 2 passed、1 skipped、1 deselected
```

Mac実機ContextのStrict Phase 1-F Acceptance：

```text
success                         : true
all_required_checks_passed      : true
required_checks                 : 22／22 true
GPU Evidence                    : supported／requested／observed = true
GPU Observation Source          : metal_model_load
Japanese／English Evidence      : Pass
Stream／Cancel／Post-cancel      : Pass
Thinking Parse                  : complete
Thinking Finish                 : stop
Hidden／Visible Separation      : Pass
Unload                          : Pass
Load including SHA-512          : 約2.51秒
```

Sandbox内ではMetal Deviceを利用できないため、Native TestはSandbox外のMac実機Contextで実行した。結果は合格している。

## 5. User Accepted Setting Decisions

ユーザーは、次の変更機会からDefault Generation上限を次へ変更することを決定した。

```toml
[generation]
max_new_tokens = 2048
```

Current Repositoryはまだ`512`であり、本Follow-upではConfigが実装担当の変更Scope外だったため未反映である。現在のFindingに起因する不具合ではないが、忘失防止のため、Lightning搬入前の小規模Follow-upへ含める。

変更時は、Config既定値を前提とするTestも同時に更新する。Context上限、会話履歴、Guardrail導入後の負荷を見ながら、将来は再調整可能とする。

Thinking表示Labelの`高度推論`から`推論過程`等への変更は、Phase 1-GのUI／注記設計と合わせる後続事項とし、本Follow-upへ混在させない。

## 6. Acceptance Status

| Area | Result | Notes |
|---|---|---|
| 前回High Findings | Pass | 2件とも解消 |
| 前回Medium Findings | Pass | 2件とも解消 |
| 前回Low Observation | Pass | 1件解消 |
| Default Runtime Tests | Pass | 183 passed、3 deselected |
| Full Project Mypy | Fail | Test 1箇所のExport境界 |
| Mac 3.13／Metal Native | Pass | Model Smoke／Strict Acceptance |
| Python 3.12 Native | Pending | Lightningで実行予定 |
| Lightning Preflight | Pending | External Target未実行 |
| Lightning CUDA Mandatory Gate | Pending | External Target未実行 |
| Lightning CPU Candidate | Pending | Best Effort／未実行 |

## 7. Next Gate

大容量Uploadをなるべく一度にまとめる方針を維持し、次の順序とする。

```text
実装担当の小規模Repository Follow-up
  ├─ Full Mypy Failure修正
  ├─ generation.max_new_tokens既定値を2048へ変更
  ├─ 関連Test更新
  └─ Full Static／Default Gate再実行
        ↓
設計者役の短縮Follow-up Review
        ↓
Lightningへ小型Preflightだけ配置して実行
        ↓
Preflight合格後にSource／Modelを一度に搬入
        ↓
Lightning Python 3.12.11／CUDA Mandatory／CPU Candidate Gate
        ↓
後継Implementer Status
        ↓
Phase 1-F Final Review
```

Phase 1-G実装、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開はまだ開始しない。

## 8. Authorization Boundary

本ReviewとIndex作成は、Source／Config／Tests／Scriptsの修正、Lightning操作、Upload、Model Download、Backup、Git、GitHub公開を許可しない。

実装担当は、ユーザーが本Reviewを渡してFollow-up開始を指示した後に、Section 3.1とSection 5の限定範囲を変更する。

## 9. Append-Only

既存文書を変更せず、新TimestampのReviewとして追加した。
