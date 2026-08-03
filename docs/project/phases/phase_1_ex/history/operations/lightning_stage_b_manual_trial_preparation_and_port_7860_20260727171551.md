# Lightning Stage B Manual Trial Preparation／Port 7860

```yaml
document_id: lightning_stage_b_manual_trial_preparation_and_port_7860
status: pre_wake_trial_complete
phase: phase_1_ex
created_at: 2026-07-27 17:15:51 JST
owner: 設計統括者役
platform_operator: user
trial_state:
  repository_preparation: accepted
  lightning_manual_preparation: passed
  running_studio_public_url_smoke: passed
  first_unattended_wake: not_run
  second_unattended_wake: not_run
public_url_recorded: false
credential_values_recorded: false
```

## 1. Purpose

設計統括者役によるDocs再構築作業を一旦終了した後、途中状態だったLightning Stage B手動試験を再開した。

本Recordは、実装担当によるStage B Repository Preparation Accepted後にユーザーがLightning上で実施した、File同期、Hash、Permission、Environment、Test、Preflight、Runtime State修復、Manual Preview停止、API Builder起動確認およびPort確定を記録する。

Stage Bの中核であるSleeping Studioへの第三者相当Public URL Accessによる無人Wakeは、まだ実施していない。

## 2. Authoritative References

- [Stage B Preparation Handoff](../handoffs/implementer_handoff_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727055625.md)
- [Stage B Preparation Status](../handoffs/implementer_status_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727063323.md)
- [Stage B Preparation Accepted Review](../handoffs/designer_review_phase_1_ex_lightning_auto_start_stage_b_preparation_20260727064044.md)
- [Public Demo／Auto-start Requirements](../../requirements/public_demo_auto_start_and_pre_release_requirements_ja.md)
- [Public Demo／Auto-start Architecture](../../architecture/public_demo_auto_start_and_rag_extension_architecture_ja.md)
- [ADR-0025](../../adr/adr_0025_public_demo_auto_start_and_pre_release_gate_ja.md)
- [ADR-0026](../../adr/adr_0026_lightning_basic_preview_lifecycle_and_managed_secrets_ja.md)
- [Lightning公式：Expose web apps](https://lightning.ai/docs/overview/host-web-apps/expose-web-apps)

## 3. File Synchronization

Stage B Repository Preparationによる実装変更は、次のTest File一件だけである。

```text
tests/unit/runtime/test_lightning_basic_preview_service.py
```

Runtime Script三件は既存のAccepted Artifactから変更されていない。Lightning上で四件すべてのSHA-512一致をユーザーが確認した。

```text
scripts/runtime/lightning/basic_preview_common.sh
1300cdb141ed135aa0ce8794919d30adbe7519174b886eaaf2f5420efa68882d6cbda55f28c29dbc4762d84111f4492ff9e33922bdfb0bbdefaff0d341df7a58

scripts/runtime/lightning/basic_preview_service.sh
7d5296a942c6fb1d5a9d8a74427317a834f2acd18385516fea1e14505075dc8b121cf921718b080e400c3ab17c990d24850c13f2045f55a91c618c4df75292ac

scripts/runtime/lightning/auto_start_preflight.sh
bd0bf4e242822a4474e9dd65c64c194fa620b1d92aba6d1b49c8a1187f38ce03acc501c4bc99dd1e168f50f336dbc2c5a5f150b7f2283f44cdd8eec3289c438d

tests/unit/runtime/test_lightning_basic_preview_service.py
2413cd6ca9a953d2829e676aac209e6b4781b0fe6ce3befaa0d7d934ca9cdff82cb8556ac8399c0a166c650084c9ff3443d4f64efbe76dbca080f3b6389eb88e
```

ScriptおよびTest FileのPermission設定もユーザーが実施した。

## 4. Environment／Credential Availability

新しいLightning Terminalで、Workspace、Project、Model、Project-local `uv`、`.venv`、Web Host、Web Port、Pure CPU ProfileおよびBasic Authentication ModeのEnvironmentを設定した。

Managed Secrets由来のCredentialは、値を表示せず、存在だけを確認した。

```text
USERNAME_AVAILABLE=1
PASSWORD_AVAILABLE=1
```

Credential実値は本Record、Docs、Command、ScreenshotまたはStatusへ記録していない。

## 5. Repository Test

Stage B追加TestをLightning Pure CPU環境で実行した。

```text
32 passed in 18.68s
```

## 6. Initial Preflight Failure

最初のRead-only Preflightでは、二つのPreflight Entryから同じFailが報告された。

```text
check.runtime_state_root=fail reason=owned_directory_mode_must_be_700
```

これはCredential、Model、PortまたはStage B Entrypointの失敗ではない。前回のManual Lifecycleで作成済みだった既定Runtime State DirectoryのModeが、Fail-closed Contractで要求する`700`と一致していなかった。

対象：

```text
/teamspace/studios/this_studio/.runtime-state/
  margpa-runtime-llm/basic-preview/
```

Safety Check：

```text
STATE_DIRECTORY_SAFETY_EXIT=0
```

対象がDirectoryであり、Symbolic Linkではないことを確認した。

修復後：

```text
700 basic-preview
600 basic-preview/basic-preview.log
600 basic-preview/.margpa-basic-preview-state
```

`basic-preview.pid`は存在しなかった。これは異常ではない。PID FileはManual Terminal向けBackground `start`で使用し、Foreground `run`では作成しない。

DirectoryやRuntime State Artifactは削除せず、対象を限定して必要なPermissionだけ修正した。

## 7. Preflight Revalidation

Permission修復後のPreflightは合格した。

```text
check.runtime_state_root=pass
check.credentials=pass source=environment values=redacted
check.web_bind=pass
check.access_boundary=pass mode=basic_preview public_demo=false
check.launch_contract=pass credentials=environment_only
```

Preflight上のPortは、その時点の設定値を検査する。最終的なStage B API Builder PortはSection 10の`7860`である。

`manual_required`項目はRepository側で偽Passにせず、Lightning Platform上のStage B手動試験へ残している。

## 8. Existing Manual Preview Stop

既存Manual Previewを停止した。

```text
status=stopped
STATUS_EXIT=3
```

`status`のExit `3`は、このLifecycle Scriptにおける正常なStopped状態である。

次のPort Listener確認では表示がなかった。

```bash
ss -ltnp | grep ':8000 ' || true
```

## 9. Foreground Entrypoint Confirmation

API Builder用として採用済みのForeground Entrypointを確認した。

```bash
bash scripts/runtime/lightning/basic_preview_service.sh run
```

起動Evidence：

```text
check.health_contract=pass expected_http=200 expected_body_status=ok
check.web_bind=pass
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
INFO: Uvicorn running
```

Studio稼働中の事前確認では、MARGPA Runtime LLM画面を通常利用できた。

API Builderで使用するのはForeground `run`である。Manual Background Lifecycle用の`start`は使用しない。

## 10. API Builder Port Decision

当初はPort `8000`を候補としていたが、API Builder上で予約済みPortとして扱われた。

その後、Lightningの解説例との整合および今後の運用上の分かりやすさを優先し、Stage B API Builderの確定Portを`7860`へ変更した。

確定値：

```text
API Builder Application Port : 7860
MARGPA_WEB_PORT               : 7860
MARGPA_WEB_HOST               : 0.0.0.0
Health Path                   : /healthz
Authentication               : basic
Runtime Profile               : lightning_linux_x86_64_cpu_native.toml
Startup Command:
  bash scripts/runtime/lightning/basic_preview_service.sh run
```

API Builder側PortとMARGPAのListen Portは同じ`7860`へ統一する。API Builderだけを`7860`、`MARGPA_WEB_PORT`を`8000`とする不一致構成は使用しない。

Source Code、Runtime Script、Deployment ProfileおよびModel Artifactの変更は不要である。

## 11. Running-Studio Public URL Smoke

Port `7860`を使用し、API Builderが発行したPublic URLを別Browserから開いて、MARGPA Runtime LLMの起動と利用を確認した。

```text
API Builder Public URL issuance : pass
Different Browser access        : pass
Application startup             : pass
Basic Preview availability      : pass
MARGPA interaction              : pass
```

Public URL実値は本Recordへ保存していない。

この結果は、Studio稼働中のPublic URL Smokeが合格したことを示す。Sleeping Studioが第三者相当AccessだけでWakeすることは、まだ証明していない。

## 12. Current Stage B State

```text
Repository Preparation:
  ACCEPTED

Lightning File／Hash／Permission:
  PASS

Managed Secrets Availability:
  PASS

Repository Target Test:
  32 PASSED

Runtime State Permission:
  REPAIRED／PASS

Preflight:
  PASS

Manual Preview Stop:
  PASS

Foreground run:
  PASS

API Builder Port:
  7860／CONFIRMED

Running-Studio Public URL Smoke:
  PASS

First Unattended Wake:
  NOT RUN

Second Unattended Wake:
  NOT RUN

Traffic-aware Auto-start:
  UNCONFIRMED
```

## 13. Next Action

次はStage B First Unattended Wake Trialを行う。

1. API BuilderのAuto-start／Serverlessが有効であることを確認する。
2. StudioをSleep状態にする。
3. Owner Browser、Studio Tab、TerminalおよびSSHをすべて閉じる。
4. 別Accountまたは第三者相当Private Browserから、同じPublic URLを開く。
5. Owner操作なしでStudioがWakeするか確認する。
6. Cold Start時間を記録する。
7. Credentialなし／誤Credentialが拒否されることを確認する。
8. 正しいCredentialでApplicationを開く。
9. `/healthz`、Basic認証および短いModel Generationを確認する。

一回目が合格した後、再Sleepさせ、同じPublic URLによる二回目のUnattended Wakeを確認する。

## 14. Acceptance Boundary

Stage B合格には、次をすべて満たす必要がある。

```text
Studio:
  SLEEPING

Owner Browser／Studio Tab／Terminal／SSH:
  CLOSED／NOT REQUIRED

Trigger:
  THIRD-PARTY EQUIVALENT VIEWER OPENS PUBLIC URL

Required Result:
  URL Access alone wakes Studio
  Foreground run starts
  Model loads
  /healthz returns HTTP 200
  Basic Authentication remains active
  Viewer can generate
  Second Sleep／Wake succeeds
  Same Public URL remains usable
```

Running StudioでPublic URLが動いたことだけでは、Traffic-aware Auto-start合格としない。

## 15. Stop Conditions

次の場合は推測で続行しない。

- Public URL AccessだけではStudioがWakeしない。
- Owner SessionまたはManual Wakeが必要になる。
- API Builder Portと`MARGPA_WEB_PORT`が一致しない。
- Basic認証が外れる。
- Credential、内部PathまたはStack Traceが外部へ露出する。
- 複数のWeb／Model Processが残る。
- Public URLが二回目のWakeで維持されない。
- 予期しないMachine変更またはCredit消費が発生する。
- Rollback対象または停止方法が不明になる。

## 16. Scope Boundary

本RecordはStage B無人Wake試験直前までの手動準備Evidenceである。

次は変更していない。

- Model Artifact
- Source Code
- Runtime Script
- Deployment Profile
- Managed Secretsの実値
- Git／GitHub
- Public Demo Mode
- RAG
- Phase 1-ex Completion State

First／Second Unattended Wakeの結果は、実施後の新しいAppend-only Evidenceへ記録する。

## 17. Documentation Lifecycle

Current／Phase Indexは変更前後の完全Snapshotを保存した。

### Current Documentation Index

```text
Before:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_before_lightning_stage_b_manual_trial_preparation_ja_20260727171551.md

After:
  docs/project/current/history/index/
  documentation_index_phase_1_ex_after_lightning_stage_b_manual_trial_preparation_ja_20260727171737.md

Before SHA-512:
5f24a297f834b792e773303ea242efb18c33756a55ca576853dcd93962940a161c01d72b7aff8055e196745e073f7ecc580e7437b69df28beeb25265538d8242

After SHA-512:
404fd5b14f044609f1fb2a61e3f48e8120d4dd6120f20c483ee63993c706fef02d87a70c22816c510d3020850e942e42d34404959deef356de802b4fb815a2de
```

### Phase 1-ex Index

```text
Before:
  docs/project/phases/phase_1_ex/history/operations/
  phase_index_before_lightning_stage_b_manual_trial_preparation_20260727171551.md

After:
  docs/project/phases/phase_1_ex/history/operations/
  phase_index_after_lightning_stage_b_manual_trial_preparation_20260727171737.md

Before SHA-512:
be73918927f765bd9eece8e9e7246f5dd1b3a06243de49242cc7181307267dab834f2ca055418fe6468414e545516edc11ac681898e98f8b5a94a444359cbec0

After SHA-512:
7b09c8cf4562437d8cfa05e61e837a0884d41bdd96f00cc66dc231a51937bf1ed4b48bd39bfd8000ed865d5c4767aafc26f38fb8084bcae8fc9ff6c5ec56c1f2
```

## 18. Validation

```text
Relative Links Checked    : 252
Missing Links             : 0
Old Identity／Private Path : 0
Public URL Value          : absent
Credential Value          : absent
Stable／After Match        : pass
.DS_Store                 : 0 after five-file cleanup
```
