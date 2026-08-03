# Phase 1-ex Lightning Basic Preview Manual Lifecycle Acceptance Review

```yaml
document_id: designer_review_phase_1_ex_lightning_basic_preview_manual_lifecycle_acceptance
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-27 00:24:40 JST
owner: 設計統括者役
review_target:
  - Lightning Linux x86_64 Pure CPU Basic Preview
  - Managed Secrets Basic Authentication
  - start / status / health / restart / stop Lifecycle
```

## 1. Review結論

Lightning AI Studio上のLinux x86_64 Pure CPU環境において、Basic Previewの手動Lifecycle Acceptanceは合格した。

Repository側の実装Review、Lightning上のLifecycle Unit Test、Managed Secrets、Preflight、起動、内部Health Check、Basic認証境界、外部Browser、RestartおよびStopまで、一連の必須確認が成立した。

判定：

```text
Lightning Basic Preview Manual Lifecycle Acceptance:
  ACCEPTED
```

## 2. 前提確認

以下が確認済みである。

```text
Lifecycle Unit Test:
  30 passed

Basic Preview Preflight:
  check.credentials=pass source=environment values=redacted

MARGPA_RUNTIME_STATE_ROOT:
  unset

Runtime State Override Check:
  RUNTIME_STATE_OVERRIDE_UNSET=0
```

通常のLightning運用では`MARGPA_RUNTIME_STATE_ROOT`を明示設定しない。

組み込みDefaultと同じPathであってもEnvironment Variableとして明示するとOverride扱いになり、親Directoryが未作成の場合は安全側に失敗する。Default運用ではScript自身に安全なState Directory作成を委ねる。

## 3. Start／Status／Health

ユーザー確認結果：

```text
Start:
  status=running pid=466377 health=healthy
  START_EXIT=0

Status:
  status=running pid=466377 health=healthy

Health:
  HTTP/1.1 200 OK
  {"status":"ok"}

Web Root without Credential:
  HTTP/1.1 401 Unauthorized
```

これにより、Process起動、PID Evidence、Health ContractおよびBasic認証境界が成立している。

## 4. External Browser／Managed Secrets

Lightningの外部公開URLについて、次をユーザーが確認した。

- Credentialなしでは開けない。
- 誤ったCredentialでは開けない。
- Lightning Managed Secretsに設定した正しいCredentialで開ける。
- 認証後にMARGPA Web画面を表示できる。
- MARGPA画面からModel生成を実行できる。

Secret値そのものはDocs、Log、Screenshot、ConfigおよびReviewへ保存しない。

## 5. Restart

ユーザー確認結果：

```text
Restart:
  state_cleanup=stale_pid_file_removed
  status=stopped
  status=running pid=488529 health=healthy
  RESTART_EXIT=0

Status after Restart:
  status=running pid=488529 health=healthy

Health after Restart:
  HTTP/1.1 200 OK
  {"status":"ok"}

Web Root without Credential:
  HTTP/1.1 401 Unauthorized
```

旧Processから新ProcessへPIDが変わり、Restart後もHealthとBasic認証境界が維持された。

## 6. Stop

ユーザー確認結果：

```text
Stop:
  state_cleanup=stale_pid_file_removed
  status=stopped
  STOP_EXIT=0

Status after Stop:
  status=stopped
  STATUS_EXIT=3

Health after Stop:
  curl: (7) Failed to connect to 127.0.0.1 port 8000
```

`STATUS_EXIT=3`は本Scriptにおける正常な停止状態のContractである。停止後にPort 8000へ接続できないことも確認できた。

## 7. `stale_pid_file_removed`表示のReview

実装確認の結果、`state_cleanup=stale_pid_file_removed`は異常なPID Evidenceを検出した場合だけでなく、正常なStop完了後にPID Fileを削除する場合にも共通のCleanup関数から出力される。

したがって、今回のRestart／Stop結果における同表示は機能異常を意味しない。

一方、正常終了時にも`stale`と表示されるため、Observability上は誤解を招き得る。将来、次のような中立的表示へ分離する候補とする。

```text
state_cleanup=pid_file_removed
```

本件は低優先度の表示改善候補であり、Phase 1-ex Basic Preview Acceptanceを妨げない。

## 8. Scope境界

今回Acceptedとする範囲：

- Lightning Linux x86_64 Pure CPU Basic Preview
- Environment-only Credential取得
- Managed SecretsによるBasic認証
- Start
- Status
- Local Health Check
- External Browser Authentication
- Model Generation
- Restart
- Stop
- 停止後のPort Close

今回のAcceptedに含めない範囲：

- Lightning PlatformによるTraffic-aware Auto-start
- Sleeping Studioの自動Wake-up
- Public URLの恒久性保証
- 匿名Public Demo
- Rate Limit／Cost Guard
- Public Demo用Tool／RAG／外部操作
- 常時稼働保証

## 9. 次の状態

Lightning Basic Preview LifecycleはRepository Reviewと実環境手動Acceptanceの両方が完了した。

次は、Phase 1-ex全体計画に従い、Auto-start Go／No-Go判定または次の承認済みScopeへ進める。匿名Public Demoや実変更は、別途設計とユーザーの明示承認を必要とする。
