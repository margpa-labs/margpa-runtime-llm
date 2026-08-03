# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:50:31 JST`
- 更新日時: `2026-07-21 18:50:31 JST`
- Snapshot: `20260721185031`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721184329.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Phase 1-H Mandatory Findings           : 4／4 Resolved
Phase 1-H Default Regression           : 246 passed、3 deselected
Phase 1-H Mac Metal Model Smoke        : 2 passed、1 skipped
Web／Lightning User Manual             : Updated／Current Candidate
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Lightning Account外Access              : Procedure Defined／Validation Waiting
Phase 1-ex                             : Accepted Reservation／Not Started
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidenceと文書集合は[documentation_index_20260721184329.md](documentation_index_20260721184329.md)から継承する。

本SnapshotはSource、Config、TestまたはPhase Acceptanceを変更しない。Phase 1 Web PreviewのMac起動、Lightning CUDA／CPU設定、Basic認証、Port公開、Account外Access、Current UI機能を新しいUser Manualへ統合した。

## 3. Current User Manual

[phase_1_web_and_lightning_user_manual_20260721185031.md](user_manual/phase_1_web_and_lightning_user_manual_20260721185031.md)

対象：

- Local Mac Web起動
- Lightning Project用uv 0.11.29
- Model Root設定
- Preview Basic認証
- CUDA Profile起動
- CPU Profile起動
- Lightning Port 8000公開
- Account外Browser Access
- Current Web UI設定
- Security Boundary
- Troubleshooting
- Lightning公開前Checklist

前Manual`phase_1_macos_user_manual_20260719171836.md`は履歴として保持し、新Manualがこれをsupersedeする。

## 4. Current Accepted Phase 1-H Contract

```text
Summary Mode           : off／post_generation
Default                : off
Normal max             : Request／Default 2048
Summary max            : 1024
Summary Thinking       : disabled
Execution              : Same Main Model Sequential
Success Presentation   : Summary only
Fallback Presentation  : Original only＋Warning
Cancel                 : Cancelled／No Fallback
Keepalive              : 15-second SSE Comment
UI Language            : ja／en Browser-only
Response Language      : ja／en／auto Independent
```

## 5. Lightning Public Preview Contract

```text
Bind Host              : 0.0.0.0
Bind Port              : 8000
Authentication         : Environment-only Basic／Mandatory for non-loopback
CUDA Profile           : config/profiles/lightning_linux_x86_64_cuda.toml
CPU Profile            : config/profiles/lightning_linux_x86_64_cpu.toml
Public Surface         : Lightning Port 8000 Public HTTPS URL
Studio Editor Sharing  : Not Required／Must not be substituted for App URL
External Validation    : Incognito／Logged-out Browser
```

## 6. Security Boundary

- Basic認証はPreview限定であり、本番Account機能ではない。
- CredentialをTracked FileまたはDocsへ保存しない。
- Public Portを有効にする前にBasic認証を設定する。
- Studio編集用URLとWeb App公開URLを区別する。
- External AccessはLightning Native／Reverse Proxy Gateで実測する。

## 7. Verification State

```text
Manual／Implementation Contract Match : Checked
Official Lightning Port Guidance      : Checked
Mac Web Manual Execution              : Waiting User Acceptance
Lightning CUDA／CPU Setup             : Waiting Full Upload／Native Gate
Lightning Public URL                  : Waiting User Operation
Account外Access                        : Waiting Incognito Acceptance
```

## 8. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Environment Rebuild
  → Lightning CUDA／CPU Native Validation
  → Lightning Web／Public URL／Reverse Proxy Validation
  → Account外Browser Acceptance
  → Cross-environment Final Review
  → Phase 1 Completion Gate
```

## 9. Deferred State

- Lightning Project／ModelのUploadはユーザー実施予定である。
- Lightning `.venv`再構築とNative Buildは未実施である。
- Lightning Full Native Gateは未完了である。
- Phase 1全体の完了宣言／Backupは未実施である。
- Phase 1-exは未着手である。
- Git／GitHub公開は未実施である。

## 10. Authorization Boundary

本IndexとUser Manualの作成は、Lightning操作、Upload、Model Transfer、Dependency Install、GPU利用、Port公開、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 11. Append-Only

前Indexと既存Manualを変更せず、新しいUser Manualを参照する新TimestampのIndexを追加した。新しいTimestampの本Indexを最新とする。
