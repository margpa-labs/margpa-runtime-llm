# Public Demo／Auto-start／Pre-release 要件

```yaml
document_id: public_demo_auto_start_and_pre_release_requirements
status: accepted
language: ja
created_at: 2026-07-26 17:53:18 JST
updated_at: 2026-07-26 19:49:49 JST
owner: 設計統括者役
phase: phase_1_ex
```

## 1. Goal

既存のBasic認証Previewを維持したまま、Lightning Traffic-aware Auto-startの可用性を安全に検証し、匿名Public Demoを外部副作用なし・Resource制限付きで追加できる状態を作る。

## 2. Auto-start Read-only Preflight

PreflightはPlatform設定を無断変更しない。

確認項目：

- API Builder／Public App／Auto-start機能の可用性
- 使用可能MachineとCredit条件
- Public URLの発行可否
- Sleeping StudioへのURL AccessによるWake-up
- Startup Command実行
- Model Load／Artifact Hash確認
- `/healthz`到達
- Cold Start時間
- Idle後のSleep復帰
- Restart後のURL維持
- Log、CredentialおよびSecret露出の有無

Platform上の設定変更またはPublic Access有効化が必要な確認は、ユーザー操作または個別許可後に行う。

## 3. Web Access Profiles

最低限次を分離する。

```text
basic_preview
public_demo
```

Access Modeが不明、Public Policyが不足または非対応Profileである場合は起動を拒否する。

## 4. Public Demo Security／Cost

Public Demoは次をServer側で強制する。

- Anonymous Access
- Same-origin
- Single Worker
- Max Concurrent Generation = 1
- Queue Disabled
- Configurable Global Rate Limit
- Configurable Global Generation Budget
- Configurable Cooldown
- Generation Timeout
- Request Body Cap
- User Message Cap
- Conversation Message Count Cap
- Conversation Total Character Cap
- Max New Tokens Hard Cap
- `429`と`Retry-After`
- `Cache-Control: no-store`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: no-referrer`
- Content Security Policy
- `X-Robots-Tag: noindex, nofollow`

Public Demoの最大生成Token初期候補は512以下とし、CPU速度、Cold StartおよびCredit条件によりさらに下げられるようにする。Client指定でHard Capを超えられないこと。

## 5. Feature Allowlist

Public Demoで許可する候補：

- Text Chat
- New Chat
- Stop
- Copy
- UI日本語／English
- 回答言語`ja／en／auto`

Public Demoで強制無効：

- RAG
- Tool
- Agent
- External I/O
- File／DB Write
- Summary Mode
- Raw Thinking表示
- Persistent Conversation
- Audit原本への実Prompt保存
- User Account／Long-term Memory

機能追加はDeny-by-defaultとする。

## 6. Privacy

- Prompt、回答、IP、Browser識別子およびRaw Thinkingを永続保存しない。
- Operational LogへPrompt本文を出さない。
- Error Responseへ内部Path、Stack TraceまたはCredentialを出さない。
- Rate Limit用状態はProcess Memory内に限定し、既定で永続化しない。

## 7. Basic Preview

既存Basic認証PreviewはPublic Demo追加後も独立して使用できる。

Public Demo設定がBasic Previewへ上書きされず、Basic Preview CredentialがPublic Demoへ不要に渡らないこと。

### 7.1 Credential／Lifecycle

- Basic PreviewのUsername／PasswordはLightning Managed Secretsから環境変数として受け取る。
- Username／Passwordはどちらも後から変更可能とし、Web Process再起動で反映する。
- Credential値をRepository、Config、Script、Log、Docs、ScreenshotまたはCommand Argumentへ保存しない。
- Repository側はPreflight、Run、Start、Stop、StatusおよびRestartを一つの主入口から扱えるLifecycle Scriptを提供する。
- Lightning側のSecret登録、Hook設置、Port設定、Public URLおよび実行操作はユーザーが行う。

## 8. Documentation RAG Hook

Mac限定簡易Documentation RAGは、次の交換可能境界を持つ。

- Document Source
- Document Catalog
- Chunker
- Embedding
- Index Store
- Retriever
- Context Assembler
- Citation／Source Trace

Phase 1-exの実装AdapterはLocal Mac／Local Filesystemに限定できる。ただしPort ContractとConfigはLightning、Home Server、Object Storage、Remote EmbeddingまたはExternal Vector Storeを追加可能にする。

`docs/`が存在しない場合はError扱いとせず、機能無効または「docsが設置されていないため参照できません」と明示する。

Public DemoではRAG AdapterをLoadしない。

## 9. Bilingual Documentation

対象：

```text
docs/project/current/*_ja.md
docs/public/*_ja.md
```

対応する`*_en.md`を同じDocumentation Refresh単位で作る。

規則：

- 日本語版が正本
- 英語版は派生版
- 英語版だけで新しい要件・判断を追加しない
- Conflict時は日本語版へ戻す
- Phase／Shared／Historyは日本語のみ

## 10. Initial Commit Documentation Gate

Initial Commit前に、実装完了後の状態へDocsを再編集する。

最低対象：

- Current Canonical日本語版
- Current Canonical英語版
- Public日本語版
- Public英語版
- README
- LICENSE
- NOTICE
- CITATION
- Roadmap
- Public Demo状態
- RAG状態
- Git運用
- Setup／User Manual
- Identity／Privacy／Secret
- Model／`.venv`／Cache除外
- Manifest／Hash／Link

Phase／Sharedの英訳はInitial Commit条件にしない。

## 11. Activation Gate

匿名Public Accessは次の全条件合格後だけ有効化する。

- Auto-start Preflight合格
- Public Demo Test合格
- Public Safety／Cost Policy合格
- Public Docs完成
- License／Terms／Notice完成
- Git運用Accepted
- Sanitation合格
- Initial Commit準備完了
- ユーザーの明示許可

## 12. Out of Scope

- Production Account
- Persistent User Quota
- Distributed Rate Limit
- Multi-replica同期
- Payment
- Production SLA
- Tool／RAG付きPublic Demo
- Guardrail／Judgeによる完全な公開安全性保証
