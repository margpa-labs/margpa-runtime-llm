# Model and Documentation RAG Setup

```yaml
document_type: model_and_rag_setup
document_state: current
language: ja_en
created_at: 2026-07-31
updated_at: 2026-07-31
public_author: Nazuna Research
project: MARGPA Runtime LLM
```

## 日本語

Model Weightは本Repositoryに含まれない。

想定する配置構成は次のとおりである。

```text
models/main/qwen3-4b/gguf/
models/guard/qwen3guard-gen-0.6b/gguf/
models/judge/selene-1-mini-llama-3.1-8b/gguf/
```

llama.cppを使用する推論環境は、`inference-llama` Extraを含めて構築する。

`llama-cpp-python`が導入されていない環境では、一部のTestを含むFull Testは実行できない。

Model Fileの取得、配置および各ModelのLicense確認は、利用者が自身の責任で行う。

### Documentation RAGの参照配置

Repository上の公開Documentは、次の形式で配置する。

```text
docs/*.md
```

Documentation RAGの実行時は、参照対象とする公開Documentを次の形式で配置する。

```text
docs/public/*.md
```

そのため、Repository上のDocument配置と、Documentation RAGが実行時に参照するDocument配置は異なる。

---

## English

Model weights are not included in this repository.

The expected directory structure is as follows.

```text
models/main/qwen3-4b/gguf/
models/guard/qwen3guard-gen-0.6b/gguf/
models/judge/selene-1-mini-llama-3.1-8b/gguf/
```

The inference environment for llama.cpp should be built with the
`inference-llama` extra.

Full tests, including some tests that depend on llama.cpp, cannot be run in an
environment where `llama-cpp-python` is not installed.

Users are responsible for obtaining and placing model files and for confirming
the license terms of each model.

### Documentation RAG Reference Placement

Public Documents in the repository are placed in the following form.

```text
docs/*.md
```

When running Documentation RAG, the public Documents to be used as reference
targets are placed in the following form.

```text
docs/public/*.md
```

Therefore, the Document placement in the repository differs from the Document
placement referenced by Documentation RAG at runtime.
