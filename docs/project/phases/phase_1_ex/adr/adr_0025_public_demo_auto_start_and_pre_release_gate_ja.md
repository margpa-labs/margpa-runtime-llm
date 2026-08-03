# ADR-0025: Public Demo／Auto-start／Pre-release Gate

```yaml
document_id: adr_0025_public_demo_auto_start_and_pre_release_gate
status: accepted
language: ja
created_at: 2026-07-26 17:53:18 JST
updated_at: 2026-07-26 17:53:18 JST
owner: 設計統括者役
phase: phase_1_ex
```

## 1. Context

Phase 1では、MacとLightning Linux Pure CPU上で、Basic認証付きWeb Previewを動作確認した。

今後は、Lightning StudioがSleep中でもPublic URLへのAccessを契機に起動するTraffic-aware Auto-startを検証し、匿名で触れるPublic Demoを追加する可能性がある。

ただし、Public Demoは既存Basic認証Previewと同じAccess境界にしない。匿名Access、Rate Limit、Token上限、Cost保護および外部副作用禁止を独立Policyとして扱う。

## 2. Decision

Phase 1-exの実行順を次とする。

```text
Lightning Auto-start Read-only Preflight
  → Auto-start Go／No-Go
  → Public Demo基盤実装
  → Lossless Docs再整理
  → Canonical／Public Docs作成
  → Mac限定簡易Documentation RAG
  → Git運用設計
  → Initial Commit前Docs Refresh
  → Git初期化／Sanitation／Initial Commit
  → Public Demo最終確認
  → 匿名Public Access有効化
```

Public Demo基盤は前半で実装できるが、匿名Public Accessの有効化は、公開Docs、License／Terms、Git運用、SanitationおよびInitial Commit準備の完了後とする。

## 3. Auto-start

Auto-startはLightningのAPI Builder／Public App機能を第一候補とする。

`on_start.sh`はStudio起動後のServer開始Hookとして使用できるが、それ単独をTraffic-aware Auto-startとみなさない。

PreflightでAccount／Studio上の機能可用性、Public URL、Cold Start、Health Check、Sleep復帰およびURL維持を確認する。

Preflightが小規模で成立する場合はPhase 1-ex前半で実施する。Platform制約、Plugin制約、Credit制約または大規模工事が必要な場合は延期し、既存Basic認証Previewを維持する。

## 4. Access Mode Separation

```text
basic_preview:
  Basic認証
  少人数検証
  現行機能を維持

public_demo:
  匿名Access
  Side-effect-free
  Server-side Limitを強制
  Tool／RAG／外部操作なし
```

単一のBooleanでBasic認証を外してPublic化しない。Access Mode、Policy、起動Command、EnvironmentおよびTestを分離する。

## 5. Public Demo Boundary

Public Demoは「Read-only」ではなく、より正確には「外部副作用を持たないSide-effect-free Demo」と定義する。

必須境界：

- Rate Limit
- 最大生成TokenのServer-side Hard Cap
- 入力文字数、Message数、会話全体量のPublic用上限
- 同時生成1件
- Queueを作らずBusyを明示
- Generation Timeout／Cancel
- 一定期間ごとのGlobal Generation Budget
- Summary／Thinkingの既定無効化
- Tool／RAG／Agent／外部I/O／File Writeの禁止
- 会話、Prompt、IPまたはRaw Thinkingの永続保存なし
- Security Header／No-index
- Public Demo注意書き
- 設定不足時のFail Closed

In-memory Rate Limitは単一Process／単一Workerの試作品では許容する。ただし再起動でResetされることを既知制限として明示する。

## 6. Documentation Language

次を日本語正本と英語派生版の対象とする。

```text
docs/project/current/*_ja.md
docs/public/*_ja.md
```

対応する`*_en.md`を作成するが、判断、更新およびConflict解決は`*_ja.md`を正本とする。

Phase、Shared、Raw History、Handoff、Status、Reviewおよび内部Operationsは日本語のみとする。

## 7. Documentation RAG

Phase 1-exではMac限定簡易Documentation RAGを実装対象とする。

ただしCoreへmacOS固有PathまたはLocal Filesystem前提を埋め込まず、将来Lightning、Home Server、CloudまたはHybridへAdapter追加で展開できるPortを予約する。

Public DemoではRAGを強制無効とする。

## 8. Git Timing

Git運用設計はPhase 1-ex後半でよい。

ただし匿名Public Access、GitHub公開またはInitial Commitの前に、Docs、Identity、License、Terms、Public Allowlist、Secret、Model除外およびManifestを再確認する。

本ADRはGit操作またはPublic Access変更を単独で許可しない。

## 9. Consequences

### Positive

- Auto-start可否を先に判断できる。
- Basic PreviewとPublic Demoの安全境界が混ざらない。
- Public Demoを先に実装し、公開だけ後段Gateで止められる。
- Mac RAGを将来外部環境へ展開しやすい。
- 日本語正本と英語公開性を両立できる。

### Cost／Risk

- Public Demo用Middleware、Config、UI、Testが増える。
- App内LimitだけではPublic URL AccessによるStudio Wake-up自体を防げない。
- Cold StartとModel Loadが長い可能性がある。
- 日本語正本更新時に英語派生版の同期確認が必要になる。
