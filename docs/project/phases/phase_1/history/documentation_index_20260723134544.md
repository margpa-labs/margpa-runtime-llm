# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-23 13:45:44 JST`
- 更新日時: `2026-07-23 13:45:44 JST`
- Snapshot: `20260723134544`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260723133644.md`

## 1. Current Position

```text
Public Author／Research Name             : Nazuna Research
Phase 1-G                                : Accepted
Phase 1-H                                : Accepted
User Mac Acceptance                      : Waiting
Phase 1-F／1-G／1-H Lightning Native     : Deferred／Batch Gate
Phase 1 Overall Completion               : Not Declared
Phase 1-ex                               : Accepted Reservation／Not Started
Public Roadmap                           : Updated／Current
Future ML Extension                      : Added／Future Reservation
Quantitative Calculation Mode            : Added／Future Reservation
Qualitative Calculation Mode             : Added／Future Reservation
Research／Developer Mode                 : Added／Future Reservation
Docs Writer until Phase 1-ex Complete    : Current Designer Task Only
Initial GitHub Publication               : Deferred until Phase 1-ex completion
Git                                      : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Current User Manual、Documentation単一Writer、README Roadmap最優先要件、Future ML Extensionおよび定量／定性計算モードは、[documentation_index_20260723133644.md](documentation_index_20260723133644.md)から継承する。

本Snapshotは、将来の一般向けProduct化を考慮した「研究・開発者モード」の予約を記録する。

## 3. Current Public Roadmap

[roadmap_ja.md](public/roadmap_ja.md)

変更前の初期Roadmap Snapshot：

[roadmap_ja_20260722023908.md](public/history/roadmap_ja_20260722023908.md)

## 4. Research／Developer Mode

Phase 2のConfiguration Control Surfaceへ、次のGlobal UI Optionを追加した。

```text
研究・開発者モード : OFF／ON

OFF:
  一般利用者向けの基本設定だけを表示する

ON:
  研究・開発者向けの設定群を表示し、許可された範囲で編集可能にする
```

Conceptual Config：

```toml
[ui.research_developer_mode]
enabled = false
```

一般公開ProfileではDefaultを`OFF`とする。Local環境または許可された利用者は`ON`へ切替可能とし、Public Deploymentでは切替権限をAccess Control Policyで決定する。

## 5. Candidate Advanced Setting Groups

- Model／Backend／Artifact
- 詳細Generation Parameter
- Context／Token／Performance
- Component別ON／OFF
- Governance Point別`off／observe／enforce`
- Guard／Judge／Repair／RAG／Agent
- 定量計算モード／定性計算モード
- Experiment Profile／Seed／Baseline
- Audit／Evidence／Status
- ML／Training／Adaptation

## 6. Separation Boundary

研究・開発者モードは、高度設定群の表示と編集入口をまとめて切り替える。

次を意味しない。

- 権限の新規付与
- Policyの解除
- Guardrail／Governance／Auditの解除
- Tool実行許可
- Componentの一括有効化
- 不正な設定組合せの受理

個々のComponent、Governance Point、定量計算モード、定性計算モードのON／OFFは独立設定として保持する。

## 7. Validation／Security Boundary

- `ON`でもAccess Control、Tool Permission、Approval、Dependency、Conflict、Capability、Schema Validationを迂回できない。
- `OFF`でもServer側の検証、安全機構およびAuditを自動的に無効化しない。
- UIで非表示にするだけでSecurity Boundaryが成立したとみなさない。
- Clientから直接送信された未許可設定はServer側で拒否する。
- 設定変更前後のDiff、Source、Apply Resultを表示し、Audit Eventとして記録可能にする。

## 8. Scoped Authorization

本更新はPublic RoadmapへのFuture Reservation追加と最新Index作成だけを対象とする。

次を自動許可しない。

- UI／Config／Access Control実装
- ML／Training実装
- Model Download／Weight更新
- Phase 1-ex開始
- Git／GitHub操作
- Lightning外部操作

## 9. Next Gate

```text
Research／Developer Mode Reserved
  → Phase 1 Current Gate継続
  → Lightning Native／Public URL Validation
  → Cross-environment Final Review
  → Phase 1 Completion／Backup
  → Phase 1-ex
```

## 10. Append-Only

旧Indexは変更せず保持する。新Timestampの本Indexを最新とする。
