# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 18:43:29 JST`
- 更新日時: `2026-07-21 18:43:29 JST`
- Snapshot: `20260721184329`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721184140.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Phase 1-H Mandatory Findings           : 4／4 Resolved
Phase 1-H Default Regression           : 246 passed、3 deselected
Phase 1-H Mac Metal Model Smoke        : 2 passed、1 skipped
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1-ex                              : Accepted Reservation／Not Started
Initial GitHub Publication              : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

文書集合とAccepted Evidenceは[documentation_index_20260721184140.md](documentation_index_20260721184140.md)から継承する。

本SnapshotはPhase 1-H Accepted状態を変更せず、解消項目と4 Mandatory Findingの対応を明確化する。

Accepted Review：

[designer_review_phase_1h_review_follow_up_20260721184140.md](handoffs/designer_review_phase_1h_review_follow_up_20260721184140.md)

## 3. Four Resolved Findings

### Finding 1：Successful Summary SSE Data Minimization

- Summary成功SSEからOriginal全文を除去した。
- 重複Summary全文Fieldを除去した。
- Non-content Transformation Metadataへ整理した。
- Original不在をRaw SSE Testで固定した。

### Finding 2：Long Silent SSE Keepalive

- 15秒IntervalのSSE Comment Keepaliveを追加した。
- Hidden Normal／Buffered Summaryの両方をTestした。
- Disconnect／Cancel／Cleanup／Terminal Countを回帰確認した。

### Finding 3：Summary Risk Notice

- 情報欠落／変形可能性を日本語とEnglishの両方へ追加した。
- Initial HTMLとTranslation Dictionaryを一致させた。

### Finding 4：Runtime Error Relocalization

- Runtime StatusをStable Stateへ変更した。
- Known ErrorをUI Language切替後に再描画できるようにした。
- Response Languageとの独立性を維持した。

## 4. Verification Evidence

```text
Format／Lint／Type／Compile            : Pass
Node Syntax                            : Pass
Default Test                           : 246 passed、3 deselected
Conversation／Summary／Web Targeted    : 51 passed
uv Lock                                : Pass／122 packages
Setup Shell Syntax                     : Pass
Mac Metal Model Smoke                  : 2 passed、1 skipped
Successful Summary Original Presence  : False
```

## 5. Current Accepted Phase 1-H Contract

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

## 6. Non-blocking Observations

- Summary Stage Broad ExceptionのSafe Operator Logは将来Observabilityで扱う。
- Legacy `force_cancel()`はRuntime Caller 0件のまま残る。
- Lightning Native／Reverse ProxyでのKeepaliveはBatch Gateで確認する。

## 7. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → User Manual Finalization
  → Phase 1 Completion Gate
```

## 8. Deferred State

- User Mac Acceptanceは未実施。
- Lightning Full Upload／Model Transferは未実行。
- Phase 1全体の完了宣言／Backupは未実施。
- Phase 1-exは未着手。
- Git／GitHub公開は未実施。

## 9. Authorization Boundary

本IndexはPhase 1-H Accepted状態を継承する。Lightning操作、Upload、Model Transfer、Phase 1完了宣言、Backup、Phase 1-ex、Git、GitHub公開を自動許可しない。

## 10. Append-Only

前Indexを変更せず、4 Findingとの対応を明確化した新TimestampのIndexを追加した。新しいTimestampの本Indexを最新とする。
