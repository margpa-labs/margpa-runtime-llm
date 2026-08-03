# Lightning Stage B Traffic-aware Auto-start Acceptance

```yaml
document_id: lightning_stage_b_traffic_aware_auto_start_acceptance
status: accepted_with_known_operational_characteristics
phase: phase_1_ex
created_at: 2026-07-27 22:46:09 JST
owner: 設計統括者役
platform_operator: user
continues_from:
  - lightning_stage_b_manual_trial_preparation_and_port_7860_20260727171551.md
  - lightning_stage_b_unattended_wake_failure_and_private_bootstrap_preparation_20260727182736.md
auto_start_go_no_go: go
traffic_aware_external_wake: passed
public_url_persistence: passed
credential_rotation: passed
old_credential_rejection: passed
idle_sleep_transition: passed
production_sla: not_claimed
private_bootstrap_source_recorded: false
exact_start_command_recorded: false
public_url_recorded: false
credential_values_recorded: false
```

## 1. Purpose

本Recordは、Lightning Stage BにおけるRepository外Private Bootstrapの実機検証、Sleep後Permission変化、Preflight、限定Unit Test、Manual Foreground起動、Traffic-aware External Wake、固定URL、Managed Secrets変更、旧Credential拒否、Idle Sleepおよび既知のCold Start特性を記録し、Auto-start Go／No-Goを確定する。

Private BootstrapのSource Code、正確な起動Command、Public URLおよびCredential実値は記録しない。

## 2. Sleep後Permission Observation

Private BootstrapのPermissionを、Sleep前後で確認した。

```text
Initial Upload:
  644

User-applied Private Mode:
  600

After Studio Sleep／Restart:
  744

Owner:
  unchanged
```

Lightning StudioのSleep／Restartを挟むと、Private Bootstrapを含むArtifactのFile Modeが復元時に変化することを確認した。少なくとも今回の対象では、`600`が保持されず`744`となった。

このため、「Permissionが永続する」ことを前提にしない。Private Bootstrapは起動時に自分自身と必要Artifactを再検査し、次の境界で処理する。

- 正規Fileである。
- Expected Ownerである。
- Symbolic Linkではない。
- Group／World Writableではない。
- `744`等のRead／Execute拡張だけであれば、Private Modeへ限定修復する。
- Group／World Writable、Owner不一致またはSymlink等の危険状態ではFail Closedする。

`stat`が出力するMode、Owner、Pathの行は状態表示であり、起動Commandではない。外側から無条件に`chmod`してから実行するとBootstrap内部の安全判定より先に対象へ作用するため、API Builderの定常起動では採用しない。

## 3. Python No-bytecode-cache Mode

Private Bootstrapの起動には、PythonのBytecode Cacheを生成しないModeを採用した。

これは`.pyc`または`__pycache__`をPrivate Bootstrap周辺へ増やさず、Sleep／復元時の不要ArtifactとPermission差分を減らすための運用上の選択である。

BootstrapおよびMARGPA Runtimeの機能成立に必須のAlgorithmではなく、起動時のFile生成を抑えるための軽量な実行条件である。

正確なPrivate Startup Commandは公開候補Docsへ保存しない。

## 4. Preflight／Test／Manual Run

Repository外Private Bootstrapを介したLightning上の事前検証は合格した。

Preflightの主要結果：

```text
Health Contract:
  PASS

Web Bind:
  0.0.0.0／7860／PASS

Access Boundary:
  basic_preview／public_demo=false／PASS

Launch Contract:
  credentials=environment_only／PASS

Runtime State Root:
  PASS

Health Client:
  PASS

Credentials:
  source=environment／values=redacted／PASS
```

限定Unit Test：

```text
32 passed in 18.05s
```

Manual Foreground起動：

```text
Application Startup:
  PASS

Listen:
  0.0.0.0:7860／PASS

Graceful Interrupt:
  PASS

Application Shutdown:
  PASS
```

Manual起動ではApplication StartupからShutdownまで正常に完了した。

## 5. Traffic-aware External Wake Trial 1

公開用API URLだけを別Browserから開き、Authentication画面、Model Load、LLM利用までを確認した。

```text
Start:
  19:04

Usable:
  19:14

Observed Cold Start:
  approximately 10 minutes

Authentication:
  PASS

Model Startup:
  PASS

LLM Interaction:
  PASS

Owner-side Manual Startup:
  NONE
```

Public URL実値は記録していない。

## 6. Long Idle／Sleep Confirmation

対象TabとBrowserを閉じ、StudioがSleepへ移行したことを確認するため、長時間放置した。

```text
Browser Closed:
  19:33

Sleep State Confirmed:
  21:43

Observation Window:
  approximately 2 hours 10 minutes

Studio Sleep:
  PASS
```

このObservationは、Sleep移行に2時間必要だったことを意味しない。確実にSleep状態となった後のWake試験を行うため、確認まで長く待ったものである。

## 7. Managed Secrets Rotation

Public URLを変更せず、Managed Secrets上のCredentialを変更した。

Studio稼働中の別Browser確認：

```text
Public URL:
  unchanged

Old Username／Password:
  rejected

New Username／Password:
  accepted

LLM Interaction after New Login:
  PASS
```

Credential値は記録していない。

この結果により、CredentialがSource、Config、Bootstrapまたは固定URLへ埋め込まれておらず、Managed Secretsの変更が新しいAuthenticationへ反映されることを確認した。

## 8. Traffic-aware External Wake Trial 2

Secret変更後のCredentialを使用し、Sleep状態から再度Public URLだけで起動した。

```text
Start:
  22:07

Usable:
  22:11

Observed Cold Start:
  approximately 3 to 4 minutes

Old Credential:
  rejected

New Credential:
  accepted

LLM Interaction:
  PASS
```

再利用後、Idle状態へ移行させた。

```text
Idle Start:
  22:11

Sleep Confirmed:
  22:22

Observed Idle-to-sleep:
  approximately 10 to 11 minutes
```

## 9. Traffic-aware External Wake Trial 3

別BrowserでPublic URLへAccessした後、そのBrowserを監視し続けず、別の作業を行った状態でもApplicationが起動することを確認した。

```text
Start:
  22:23

Usable:
  22:27

Observed Cold Start:
  approximately 3 to 4 minutes

Continuous Active Waiting:
  not required

Authentication:
  PASS

LLM Interaction:
  PASS
```

再度Idle状態へ移行させた。

```text
Idle Start:
  22:28

Sleep Confirmed:
  22:40

Observed Idle-to-sleep:
  approximately 12 minutes
```

## 10. Transient Response Observation

別BrowserからAccessした一回の試行で、Authentication画面の前にJSONらしき一時応答が表示された。

内容は記録されておらず、原因を断定できない。再度同じURLへAccessすると直ちにAuthentication画面が表示され、その後のLoginとLLM利用は正常だった。

```text
Transient JSON-like Response:
  observed once

Exact Content:
  not recorded

Reproduction:
  not confirmed

Recovery:
  reload／re-access succeeded

Severity:
  low-priority non-blocking observation
```

起動途中のProxy、Health、PlatformまたはApplication Responseであった可能性はあるが、EvidenceがないためFactとして断定しない。再現した場合は、表示内容、時刻、HTTP Status、Response HeaderおよびStartup Logを秘密情報を除外して記録する。

## 11. Observed Timing

今回観測したCold Startは、約3分から10分の範囲だった。

```text
Observed Cold Start Range:
  approximately 3 to 10 minutes

Observed Idle-to-sleep Range:
  approximately 10 to 12 minutes

Long Sleep Confirmation Window:
  approximately 2 hours 10 minutes
```

Cold Startが後続試行で短くなった理由は確定していない。Browser Cache、Platform Cache、Image／Environment復元状態、Model Artifact CacheまたはResource割当等の可能性はあるが、現時点ではInferenceとしても固定しない。

この値は今回のFree CPU Studioにおける観測値であり、SLA、上限保証または将来環境の性能保証ではない。

## 12. User-facing Notice

現在のBasic Previewを案内する場合は、次の説明を使用できる。

> 初回アクセス時または休止状態からの再起動時は、画面が表示されるまで数分から10分程度かかる場合があります。読み込み中の状態が続きますが、Lightning環境とモデルの起動が完了すると自動的に画面が表示されます。一時的な応答が表示された場合は、しばらく待ってから再読み込みしてください。

これは既知のCold Start特性を説明するものであり、起動時間を保証する記述ではない。

## 13. Acceptance Decision

```text
Lightning Auto-start Read-only Preflight:
  ACCEPTED

Auto-start Go／No-Go:
  GO

Traffic-aware External Wake:
  PASS

Repeated Wake／Sleep Cycle:
  PASS

Stable Public URL:
  PASS

Managed Secrets Rotation:
  PASS

Old Credential Rejection:
  PASS

New Credential Authentication:
  PASS

LLM Interaction:
  PASS

Idle Sleep:
  PASS

Cold Start:
  KNOWN OPERATIONAL CHARACTERISTIC

Transient JSON-like Response:
  NON-BLOCKING OBSERVATION
```

Stage Bは、現在のLightning Basic Preview用途について`ACCEPTED WITH KNOWN OPERATIONAL CHARACTERISTICS`とする。

これはProduction Availability、SLA、匿名Public Demo、Rate Limit、Token／Cost保護、Tool／RAG遮断または無制限公開を承認するものではない。

## 14. Remaining Boundary

Stage B Acceptance後も、次は未完了である。

- 匿名Public Demo Profile
- Rate Limit
- Token／Cost保護
- Tool／RAG／外部操作のPublic Demo遮断
- Public Demo用利用条件と表示
- Transient JSON-like Responseの再現調査
- Git運用設計
- Git初期化／Initial Commit
- Phase 1-ex Final Lossless
- Final Review／Backup／GitHub公開

Basic認証付きPreviewと、将来の匿名Public Demoを混同しない。
