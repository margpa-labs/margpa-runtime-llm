# Pre-initial Commit Documentation Refresh Plan

```yaml
document_id: pre_initial_commit_documentation_refresh_plan
status: accepted_not_executed
language: ja
created_at: 2026-07-26 17:53:18 JST
updated_at: 2026-07-27 22:57:35 JST
owner: 設計統括者役
phase: phase_1_ex
```

## 1. Timing

本Planは、2026年7月27日に変更されたPhase 1-ex実行順のStage 6として実施する。

実施時点では、Git未使用のGitHub一時掲載、Public Demo、Mac簡易Documentation RAG、Git運用設計およびGit初期化／公開Sanitationのうち、先行Stageとして承認・実施された結果を入力にする。Stage 1の一時掲載は本Planの合格を前提としない別境界である。

本Plan合格前に初回Commitを作成しない。匿名Public AccessはStage 2の専用Gateとユーザー判断に従い、本Planだけを根拠に有効化しない。

[Phase 1-ex 実行順変更／Git未使用掲載境界 Record](../history/operations/phase_1_ex_revised_execution_order_and_pre_git_publication_boundary_20260727225735.md)を順序の正本として参照する。

## 2. Inputs

- Final Source Tree
- Final Config
- Test Result
- Lightning Auto-start Preflight Result
- Public Demo Result
- Documentation RAG Result
- Current Docs
- Phase／Shared Docs
- Public Docs
- License／Terms素材
- Model／Dependency Provenance

## 3. Refresh Scope

### 3.1 Current

```text
docs/project/current/*_ja.md
docs/project/current/*_en.md
```

日本語版を先に更新し、Review後に英語派生版を生成・確認する。

### 3.2 Public

```text
README.md
LICENSE
NOTICE.md
CITATION.cff
docs/public/*_ja.md
docs/public/*_en.md
```

### 3.3 Phase／Shared

日本語版だけを更新する。英語版は作らない。

### 3.4 User／Setup

- Mac Setup
- Lightning Setup
- Basic Preview
- Public Demo
- Auto-start
- RAG
- Model配置
- `.venv`再構築
- Known Limitations

## 4. Lossless Rule

既存Phase History、Status、Review、HandoffおよびSource Evidenceを勝手に要約・再解釈・削除しない。

Current／Publicへ統合する場合も、Source、決定、例外、未解決事項および将来予約を追跡可能にする。

## 5. JA／EN Rule

- `_ja`が正本。
- `_en`は派生版。
- 日本語版確定前に英語版だけ先行確定しない。
- 英語版だけに新しい要件を追加しない。
- Conflict時は日本語版へ戻す。
- Translation Date／SourceをMetadataへ記録する。

## 6. Public Demo Gate

Docsへ次を正確に反映する。

- Auto-start合否
- Public Demoが実装済みか
- 匿名Public Accessが有効か
- Basic認証Previewとの違い
- Rate／Token／Budget
- RAG／Tool／外部操作が無効であること
- Cold Start
- CPU速度
- 動作保証なし
- 将来Public Demo方式

未実装または未確認を実装済みとして書かない。

## 7. RAG Gate

- Mac限定実装範囲
- External Hook
- Source範囲
- History除外
- docs不在時の動作
- Citation／Traceability限界
- Public Demoでは無効

## 8. Sanitation

- 個人情報
- Credential／Secret
- 実Absolute Path
- Model本体
- `.venv`
- Cache／Bytecode
- 実会話Log
- RAG私有資料
- Local Override
- `.DS_Store`
- Backup／Zip

## 9. Validation

- File Inventory
- Include／Exclude Allowlist
- SHA-512
- Local Link
- JA／EN Pair
- Source／Translation Metadata
- Current／Phase／Public到達性
- READMEからRoadmap到達
- Identity
- License／Terms／Notice
- Model License／Provenance
- Restore／Setup手順
- Target Manifest

## 10. Result

本Plan実行時に、Timestamp付きReview／Evidenceを新規作成する。

合格後、Stage 7の全体Review／Test／Privacy Scanへ進む。Stage 7が合格し、ユーザーが明示的に許可した後にStage 8の初回Commitへ進む。

本Plan自体はGit操作を許可しない。

Stage 1のGit未使用掲載、Stage 5のGitHub公開との対応およびStage 8の初回Commitの履歴関係は、Stage 4のGit運用設計で確定する。未確定の関係を本Planで推測しない。
