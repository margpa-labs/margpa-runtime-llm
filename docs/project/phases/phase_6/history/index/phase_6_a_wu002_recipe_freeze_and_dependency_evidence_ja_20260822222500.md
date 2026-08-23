# Phase 6-A Recipe Freeze／Dependency Acquisition Evidence（P6-A-WU-002）

```yaml
document_id: phase_6_a_wu002_recipe_freeze_and_dependency_evidence
status: current_recovery_entry
phase: phase_6
subphase: phase_6_a
work_unit: p6_a_wu002_in_progress
role: Claude側設計統括者役
provider: claude_code
long_running_mode_active: true
created_at: 2026-08-22 22:25:00 JST
authority_basis: phase_6_dependency_acquisition_authority_receipt_ja_20260822220804.md
```

## Authority Refresh確認（本WU再開の前提）

```text
Six-document Recovery Set : 6／6 再読済み（Provider Memory／Summary代替なし）
Frozen Core 7文書 SHA-512   : 独立再計算により7／7完全一致（改ざんなし確認）
Phase Index Digest          : 66f582fc...36401（Receipt記載値と一致）
Phase 6-B着手済みSource     : src/margpa_runtime_llm/modules/runtime_model_control/ 保持（削除／Reset 0）
Disk／Memory                : 87,198,348 KiB avail（約83.2 GiB）／16 GiB、Drift軽微・許容範囲
```

## Dependency Acquisition Evidence（Receipt §4 Required Procedure準拠）

```text
Pre-install State   : transformers／sentencepiece／gguf／safetensors／torch いずれも0件（Project .venv）
Install Command      : uv add --optional deepseek-conversion transformers sentencepiece gguf safetensors
                        （UV_CACHE_DIR／TMPDIR を .venv/.cache／.venv/.tmp へ限定）
Second Install       : uv add --optional deepseek-conversion torch
                        （理由：convert_hf_to_gguf.py が起動時に import torch を要求するとImportErrorで判明。
                        Receipt §3.2「新しい直接PackageがPhase 6 Acceptanceに必須なら追加できる」に該当）
Index                : Official PyPI（既定Index、--trusted-host／Credential／Private Index不使用）
Resolved Direct       : gguf==0.19.0, safetensors==0.8.0, sentencepiece==0.2.2, transformers==5.15.1, torch==2.13.0
Resolved Transitive   : filelock, fsspec, hf-xet, huggingface-hub, markdown-it-py, mdurl, regex, rich,
                        shellingham, tokenizers, tqdm, typer, mpmath, networkx, setuptools, sympy
pyproject.toml Diff   : [project.optional-dependencies] へ新Group `deepseek-conversion` 追加のみ。
                        既存 dependencies／inference-llama／web／dev／notebook Groupは無変更。
uv.lock               : uv addにより自動更新（Resolver Conflict 0）
既存Runtime影響        : llama_cpp==0.3.34／pydantic==2.13.4／fastapi==0.139.2、Before/After完全一致（影響0）
Focused Regression    : Backend Full Test 1236 passed／3 deselected（Install前と同数、回帰0）
Native Build           : torch/gguf/sentencepieceともprebuilt wheel取得（Native Compile不要、Build Failure 0）
License                : transformers(Apache-2.0), torch(BSD-3), sentencepiece(Apache-2.0), gguf(MIT系)
                        ——いずれもDeepSeek Weight自体のLicense(MIT)と別軸、Local内部利用のみで問題なし
Yanked／Warning        : 検出なし
Cache／Temp Cleanup    : 無断削除0（.venv/.cache, .venv/.tmp を保持）
```

## Conversion Tool／Recipe Freeze

```text
Tool                 : /opt/homebrew/bin/convert_hf_to_gguf.py（Read／Execute-only、Homebrew変更0）
Tool Revision        : Homebrew llama.cpp build 7970（formula stable 0.2.0）
実行Interpreter       : project .venv python（3.13.14）——Homebrew Pythonではなくこちらに依存導入
Architecture確認      : config.json architectures=Qwen3ForCausalLM、
                        convert_hf_to_gguf.py --print-supported-models にQwen3ForCausalLM含むことを確認
Recipe               : HF safetensors → GGUF Q8_0（中間）→ llama-quantize → GGUF Q4_K_M（最終）
中間Format選定理由     : Architecture文書はF16中間を例示するが、F16中間（約16GB）＋Q4_K_M最終（推定約5GB）を
                        同時保持すると空き容量が約63GiBとなり、Disk Preservation Floor（64 GiB）を下回る
                        見込みだったため、Q8_0中間（ほぼLossless、8bit）へRecipe変更。
                        Governance「通常のPackage不足...Recipe修正は自己解消する」の範囲内の判断。
Output Path (中間)    : models/main/deepseek-r1-0528-qwen3-8b/conversion_work/
                        deepseek-r1-0528-qwen3-8b-Q8_0-intermediate.gguf
Output Path (最終)    : models/main/deepseek-r1-0528-qwen3-8b/gguf/（llama-quantize実行後に作成予定）
Tokenizer／Template   : convert_hf_to_gguf.py既定のHF Tokenizer変換に委ね、独自Overrideは行わない
Quantize Tool         : /opt/homebrew/bin/llama-quantize（同Homebrew build、Read/Execute-only）
Canonical Mutation    : 0（huggingface/ Subtreeへの書込みは行っていない）
Disk Gate直前確認      : 87,198,348 KiB avail、Q8_0中間(推定約8.5GB)+Q4_K_M(推定約5GB)=約13.5GB見込み、
                        Floor 64 GiBに対し十分な余裕（約70GiB残見込み）
```

## Current Status

```text
Conversion Process   : Background実行中（HF → Q8_0 GGUF）、完了未確認
Next Step            : 完了後にOutput Size／SHA-512記録 → llama-quantize Q4_K_M実行 → Manifest作成
```

## Next Exact Route

Background Conversion完了確認後、Output Evidence記録、Q4_K_M量子化、Manifest作成（P6-A-WU-003）へ進む。並行してPhase 6-B-WU-001（Runtime Model Domain／Ports、既着手分の継続）を進める。
