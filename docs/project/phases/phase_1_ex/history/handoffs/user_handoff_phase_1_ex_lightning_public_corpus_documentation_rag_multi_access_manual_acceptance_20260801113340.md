# ユーザー向けHandoff：Phase 1-ex Lightning Public Corpus Documentation RAG Multi-access Manual Acceptance

```yaml
document_id: user_handoff_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_manual_acceptance
phase: phase_1_ex
status: ready_after_public_corpus_completion
language: ja
created_at: 2026-08-01 11:33:40 JST
owner: 設計統括者役
operator: ユーザー
source_review: designer_review_phase_1_ex_lightning_public_corpus_documentation_rag_multi_access_20260801113340.md
lightning_operation_authority: user_only
```

## 1. Purpose

Repository実装Accepted後、Lightning実機で次を確認する。

```text
Basic Preview:
  Basic認証を維持
  公開8文書RAGを利用可能

Public Demo:
  認証なしを維持
  同じ公開8文書RAGを利用可能

Both:
  RAG Default OFF
  Internal Project Docs非参照
  Allowlist外Citationなし
  Sleep／Wake後も同じ境界
```

Lightning、API Builder、Port、Managed Secrets、Private Bootstrapおよび外部URLの操作はユーザーだけが行う。実装者役または設計統括者役へ外部操作権限を拡張しない。

## 2. Required Public Corpus

Lightning Project Rootの次の8 Pathへ、公開用として別途確定した文書を全件配置する。

```text
docs/public/overview_ja.md
docs/public/overview_en.md
docs/public/concept_ja.md
docs/public/concept_en.md
docs/public/roadmap_ja.md
docs/public/roadmap_en.md
docs/public/technology_selection_ja.md
docs/public/technology_selection_en.md
```

Manual Acceptance開始条件：

```text
expected=8
present=8
missing=0
all regular files
all non-symlink
all UTF-8 Markdown
```

現在のローカルProjectには3件だけが存在するため、別途用意した5件を含む完成版8文書をLightningへ配置してから判定する。Partial CorpusのままでもServerは起動できるが、今回の8文書Acceptanceとはしない。

## 3. Repository Artifact Set

Lightningへ反映するRepository側の変更対象は、Implementer StatusのChanged／Added Files and SHA-512を正とする。主なRuntime対象は次である。

```text
config/web_profiles/public_demo.toml
config/feature_profiles/lightning_public_documentation_rag.toml

src/margpa_runtime_llm/web/access_profiles.py
src/margpa_runtime_llm/modules/documentation_rag/contracts.py
src/margpa_runtime_llm/adapters/documentation_rag/local_filesystem_source.py
src/margpa_runtime_llm/adapters/documentation_rag/__init__.py
src/margpa_runtime_llm/bootstrap/documentation_rag.py
src/margpa_runtime_llm/entrypoints/web/main.py

scripts/runtime/lightning/basic_preview_common.sh
scripts/runtime/lightning/basic_preview_service.sh
scripts/runtime/lightning/public_demo_service.sh
```

Manual Test用に、Implementer Status記載の追加・変更Testも同期する。Dependency、`uv.lock`、Model Artifact、Private Bootstrap SourceまたはManaged Secret値の変更は不要である。

## 4. Preflight Acceptance

Basic PreviewとPublic Demoを別々にPreflightする。

必須Evidence：

```text
check.host_platform=pass value=linux_x86_64_container
check.documentation_rag_profile=pass mode=basic_preview
check.documentation_corpus_readiness=pass expected=8 present=8 missing=0
check.credentials=pass source=environment values=redacted
```

Public Demo：

```text
check.host_platform=pass value=linux_x86_64_container
check.documentation_rag_profile=pass mode=public_demo
check.documentation_corpus_readiness=pass expected=8 present=8 missing=0
Basic Credential value is not required or forwarded
```

Absolute Private Path、Credential値またはPrivate Bootstrap SourceをEvidenceへ転記しない。

## 5. Functional Matrix

### 5.1 Basic Preview

1. Credentialなし／誤Credentialで拒否される。
2. 正しいManaged Secretsで画面が開く。
3. 初期状態でDocumentation RAGがOFFである。
4. OFFの通常質問でProject Docs Citationが出ない。
5. ONにして日本語公開文書の質問へ日本語文書Citationが出る。
6. ONにして英語公開文書の質問へ英語文書Citationが出る。
7. Citation Pathが公開8 PathのSubsetである。
8. `docs/project/**`固有情報を根拠として回答またはCitationしない。
9. Stop、New Chat、ReloadおよびModel Busyが回帰しない。

### 5.2 Public Demo

1. Basic認証画面なしで開く。
2. Public Child ProcessへBasic Credentialを渡さない。
3. 初期状態でDocumentation RAGがOFFである。
4. OFFの通常質問でProject Docs Citationが出ない。
5. ONにして日本語公開文書の質問へ日本語文書Citationが出る。
6. ONにして英語公開文書の質問へ英語文書Citationが出る。
7. Citation Pathが公開8 PathのSubsetである。
8. `docs/project/**`固有情報を根拠として回答またはCitationしない。
9. Stop、New Chat、ReloadおよびModel Busyが回帰しない。

### 5.3 Missing／No-hit Safety

必要に応じて、公開8文書に根拠がないProject固有質問を使い、RAGが根拠を捏造せずSafe WarningまたはNo-hitになることを確認する。Lexical Retrievalの回答品質そのものをSemantic保証と解釈しない。

## 6. Lifecycle Matrix

Basic PreviewとPublic Demoの双方で次を確認する。

```text
Studio active:
  startup pass
  RAG ON pass

Browser／Owner Session closed:
  idle sleep transition

External URL access only:
  traffic-aware wake
  same access boundary
  same RAG profile
  same exact public corpus
```

Basic PreviewとPublic Demoは別Processで起動した場合に別々のIn-memory Indexを持つ。片方のIndex Buildまたは停止を、もう片方のPersistent State共有として扱わない。

## 7. Acceptance Decision

```text
PASS:
  8／8 corpus
  Basic Auth preserved
  Public auth none preserved
  RAG default off
  JA／EN retrieval and citation
  citation subset exact 8
  internal docs not cited
  sleep／wake preserved

SAFETY PASS／QUALITY TUNING PENDING:
  no-hit or bounded-context denial without guessed project facts

FAIL／BLOCKER:
  internal docs citation
  allowlist外citation
  Public Demo credential leakage
  Basic Preview authentication bypass
  RAG OFF file scan or citation
  partial evidence followed by guessed definitions or relations
```

## 8. Rollback Boundary

問題発生時は、まずUI上のDocumentation RAGをOFFにして通常Chatを維持する。Basic PreviewとPublic Demoを混同せず、問題があるSurfaceだけを停止する。

Repository Fileの削除、旧Artifactへの勝手な置換、Managed Secrets削除、Private Bootstrap変更、Git操作またはProject外Cleanupは本Handoffで許可しない。切戻しが必要な場合は、実測Evidenceを設計統括者役へ返し、対象を確定してから別指示とする。
