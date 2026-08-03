# Phase 1 Lightning最終化／Phase 1-ex開始前 統合記録

- 文書ID: `phase_1_lightning_finalization_and_phase_1_ex_pre_backup_record`
- 状態: `current_pre_backup_record`
- 作成日時: `2026-07-26 12:02:29 JST`
- 更新日時: `2026-07-26 12:02:29 JST`
- Snapshot: `20260726120229`
- 作成担当: 設計者役担当Task
- 対象期間: Lightning Pure CPU実環境構築の再整理依頼からPhase 1確定Backup直前まで
- Phase 1 Final Review: [designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md](../handoffs/designer_review_top_level_phase_1_completion_and_lightning_web_acceptance_20260726111632.md)
- Current User Manual: [phase_1_web_and_lightning_user_manual_20260726111632.md](../user_manual/phase_1_web_and_lightning_user_manual_20260726111632.md)
- Phase 1-ex Pre-start Requirements: [phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md](../requirements/phase_1_ex_pre_start_execution_order_and_public_demo_requirements_20260726120229.md)
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
