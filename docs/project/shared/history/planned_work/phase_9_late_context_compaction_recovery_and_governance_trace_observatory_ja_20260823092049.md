# Phase 9後半——Context圧縮・復旧とGovernance Trace Observatory予約

```yaml
document_id: phase_9_late_context_compaction_recovery_and_governance_trace_observatory_20260823092049
status: planned_work_priority_reservation
target_phase: phase_9_late
from: ユーザー／プロジェクト責任者兼設計統括者役
to: 将来のPhase 9設計・実装・Review担当
created_at: 2026-08-23 09:20:49 JST
language: ja
implementation_started: false
exact_subphase_frozen: false
default_modes: off
```

## 1. Decision

Phase 9のExperiment／Multi-Governance Research Platformが成立した後、累積Full Closure前の
後半候補として、次の3機能群を優先予約する。

1. Context Pressureに応じた自動Context圧縮・Snapshot・選択的復旧。
2. Context Observatoryの「重要Context復旧・Handoff作成」および「任意手動圧縮」操作。
3. Raw Model CandidateからGovernance／Judge／Repairを経たFinal Responseまでを表示する
   Governance Trace Observatory。

実装可否と完成範囲は、Phase 9時点の利用可能量、As-built Runtime、Provider Capability、
Phase 6〜8のAcceptanceおよびPhase 9前半のExperiment Schemaによって決定する。
本書はPhase 9の即時開始、Source Mutation、Public有効化または固定Subphase数を意味しない。

## 2. Existing Reservationとの関係

既存の[Context Observatory提案](future_scope_proposal_context_observatory_ja_20260817234734.md)は、
Context Capacity、Usage、Threshold、Compaction Event、Recovery State、圧縮前後比較および
Recovery Snapshotを予約している。その後、Context Gauge／Popover／基本内訳は実装済みとなった。

本書は既存提案を削除または置換しない。次を新しい優先決定として追加する。

- 実用的なNative Compaction／Recovery候補をPhase 9後半へ前倒しする。
- Handoff生成とManual Compactionの2操作をUIから実行可能にする。
- Governance介入のRaw／Final比較を独立した右側Observability Surfaceとして追加する。
- 実用候補を一律にPhase 10以降へ送らず、未実装分とLossless Algorithm研究だけを
  Phase 10以降に残す。

## 3. Feature A——Automatic Context Compaction and Recovery

### 3.1 Objective

Context Windowが限界に達してから失敗するのではなく、有効な残Budgetが小さくなった時点で
Recovery Snapshotを作成し、構造化された圧縮ContextへAtomicに切り替え、必要な原Turn、
EvidenceまたはArtifactを選択的に再読込する。

### 3.2 Threshold Design

固定の「95%」をそのまま実行線にしない。判定は将来のPhase 9設計統括者が、
実ModelとRuntimeの次を用いて動的に設計する。

```text
Effective Input Budget =
  Model Context Capacity
  - System／Governance Reserve
  - RAG／Tool Reserve
  - Max New Tokens
  - Compaction Working Reserve
  - Safety Margin
```

圧力Stateは少なくとも、通常、観測、Snapshot準備、圧縮実行および緊急停止を区別する。
Exact ThresholdはProvider固有値としてHard-codeせず、実測、Provider Report、Runtime Calculation、
EstimateまたはUnknownのMeasurement Classを付す。

### 3.3 Mode

自動動作の初期値は`off`とする。

```text
OFF:
  圧力観測と自動Snapshot／Compactionを実行しない。

OBSERVE:
  圧力、推奨タイミング、予想削減量、保持／脱落候補を表示する。
  Contextは切り替えない。

ENFORCE:
  定義されたPressure GateでSnapshot／Compaction／Recoveryを実行する。
```

### 3.4 Snapshot／Atomicity／Rollback

- 自動または手動圧縮前に、復元可能なPre-compaction Snapshotを必ず作る。
- SnapshotはTurn Identity、順序、目的、決定、未解決事項、Authority、Evidence Reference、
  Next Route、Schema VersionおよびDigestを持つ。
- 圧縮Contextの生成、Validationおよび保存が成功した場合だけActive Contextを切り替える。
- Failure、Cancel、Timeout、Digest MismatchまたはSchema Unknown時は旧Contextを維持する。
- 圧縮前の原Chat履歴を自動削除しない。

### 3.5 Recoveryの正確な意味

要約から失われた原文を生成的に「復号」するのではない。

```text
原Chat／Artifact／Evidence : 保持
圧縮Context                : Modelへ送る構造化版
Recovery Index              : 原Turn／Artifactへの参照
Rehydration                 : 必要範囲の選択的再読込
```

圧縮だけを唯一の解とせず、Phase 10以降のLossless Context／Ledger／Graph／Index研究と
差し替え可能なPortを保持する。

## 4. Feature B——Context Observatory Action Buttons

### 4.1 Placement／Interaction

Current Context Usageを確認するGauge／Popover／Panelの右側に、2つのIcon Buttonを配置する。
Exact IconとVisual Designは実装時のUI Systemに合わせる。

```text
Button A Hover Label:
  重要コンテキスト復旧・引き継ぎ書作成ボタン

Button B Hover Label:
  任意手動圧縮ボタン
```

Wide LayoutではContext Surfaceの右側へ表示し、Narrow／Mobile Layoutでは固定pxに依存せず
Popover、DrawerまたはBottom SheetへReflowする。Keyboard、Focus、Tooltip、Touchおよび日英Labelを
Acceptance対象にする。

### 4.2 Important Context Recovery／Handoff Generation

専用のStructured Instructionを使い、次を抽出する。

- Current Objective／Current Position。
- Fixed Decisions／Constraints／Authority。
- Completed／Unfinished／Deferred／Blocked。
- Important Evidence／Source／Identity／Digest。
- Known Failure／Risk／Recovery Point。
- Exact Next Route。

初期実装は生成結果をChat内または専用Log Surfaceへ表示し、Copyと任意の`.md` Downloadを
提供する。Handoff生成だけでActive Contextを変更しない。

### 4.3 Manual Compaction Confirmation

任意手動圧縮は即実行せず、必ず次の性質を持つ確認Dialogを表示する。

> モデルへ送信される過去文脈が要約版へ置き換えられます。元のChat履歴は保持されますが、
> 一部の細部が今後の回答へ反映されにくくなる可能性があります。実行前の復元Snapshotを作成した上で
> 圧縮しますか？

Dialogには推定Token削減、保持項目、脱落Risk、Snapshot ID、Cancelおよび実行を表示する。

## 5. Feature C——Governance Trace Observatory

### 5.1 Objective

Main Chatの右端に、左上Sidebar Toggleと同系統の表示／非表示Buttonを追加する。
Wide LayoutではMain Chatと右Observability Panelに画面を分割し、Narrow LayoutではOverlay／Drawerへ
Reflowする。

Panelは、次の因果ChainをRequest／Turn／Attempt単位で表示する。

```text
User Input
→ Constitution／Authority Result
→ RAG／Data Evidence
→ Main Governance PRE
→ Raw Model Candidate
→ Main Governance POST
→ Guardrail／Policy
→ Semantic Evaluator／Judge
→ Conflict Resolution
→ Action Resolver
→ Repair Attempt 1..N
→ Final Presented Response
→ Audit／Evidence
```

未実装、無効、未実行またはUnsupportedのLayerは、実行済みと捗造せず状態をそのまま表示する。

### 5.2 Research Full Raw Principle

本機能の主対象はAI Governance研究者である。Raw Failureを隠すと、どのGovernance、Judge、
ActionまたはRepairがどのように作用したかを比較できず、研究Platformとしての価値を失う。

そのため、研究者が明示的に有効化した場合は、Runtimeが実際に観測できたRaw Model Output、
拒否前Candidate、Hidden Original、Prompt／Tool関連情報および各Layer Evidenceを、選択した
Visibility／Persistence／Redaction契約に従って表示・保存可能にする。

Model BackendまたはProviderが露出しないInternal Hidden Reasoningを推測または捗造しない。

```text
RAW MODEL OUTPUT          : AVAILABLE／UNAVAILABLE
INTERNAL HIDDEN REASONING : NOT EXPOSED BY BACKEND
```

### 5.3 Visibility／Persistence／Redactionの分離

「見る」と「永続保存する」を同一Toggleにしない。

```text
Trace Visibility:
  off
  metadata
  full_raw

Trace Persistence:
  none
  session
  persistent

Redaction:
  none
  secrets_only
  standard
```

全ての初期値は不意なCaptureを避ける側に設定する。一方、研究者は明示的に
`full_raw／persistent／none`を選択できる。

### 5.4 Researcher-controlled Warning／Responsibility

Full Rawの初回有効化時は、拒否前の危険出力、誤情報、不適切な内容、個人情報、
機密情報候補、System／Tool関連情報が表示または保存され得ることを明示する。

本機能は一般利用者向けの無条件表示ではなく、研究者が内容、保存、共有、処置および
利用を自ら判断するResearcher-controlled Modeとする。ProjectのNo Warranty／No Liability方針と整合させるが、
警告は偶発的な外部公開、Git混入または外部送信への許可を生成しない。

### 5.5 Protectionの意味

`Protected Research Capture`のProtectionは、研究者からRawを隠すことを意味しない。
次の偶発事象を防ぐ境界である。

- Public／Basic Surfaceへの意図しない表示。
- 意図しないGit管理。
- 無許可の外部送信。
- Capture有効状態、Retention、Ownerおよび保存先の不明化。

Public／Basic／Cloudでの有効化は、将来の別Human Gateとし、Phase 9 Local Research Modeの実装から自動導出しない。

### 5.6 OBSERVE／ENFORCEの研究意味

```text
OBSERVE:
  Raw Model Candidateを通常Chatへ提示。
  Governance評価、Deviation、推奨Actionを右Panelへ表示。
  Executed Action = 0。

ENFORCE:
  Raw Model Candidateを右Panelで保持・表示。
  実際のGovernance／Action／Repair履歴を表示。
  Final Presented Responseを通常Chatへ提示。
```

OBSERVEは「何もしない」のではなく、無介入BaselineとCounterfactual Recommendationを記録するModeとする。

## 6. Trace／Evidence Identity候補

Phase 9の`experiment_id／run_id／request_id`を起点に、少なくとも次を関連付ける。

- Conversation／Session／Turn／Generation Attempt／Repair Attempt。
- Model Role／Model／Artifact／Backend／Context／Generation Config／Seed。
- Definition／Rule／Point／Plan／Mode／Digest。
- Input／Raw Candidate／Observation／Judge／Conflict／Recommended Action／Executed Action／Final。
- Token／Latency／Call／Repair Count／Warning／Error／Degraded。
- Persistence／Redaction／Retention／Export State。

Latest Process-global StateをCurrent Requestと混同せず、各表示はIdentityとTerminal Stateを持つ。

## 7. Dependency／Suggested Sequence

```text
Phase 6:
  Judge／Repair／Request-correlated Status／Recording

Phase 7:
  Full RAG／Data Governance／Citation／Evidence

Phase 8:
  Constitution／Agent／Tool／Memory／Handoff Governance

Phase 9 Early:
  Experiment Runtime／Evaluation／Multi-Governance／Conflict／Action Comparison

Phase 9 Late Candidate A:
  Context Pressure／Snapshot／Compaction／Recovery

Phase 9 Late Candidate B:
  Handoff Generation／Manual Compaction／Context UI

Phase 9 Late Candidate C:
  Governance Execution Trace／Research Full Raw／Right-side Observatory

Phase 9 Final:
  Phase 3〜9 Cumulative Full Closure
```

Exact Subphase Letter、Work Unit数、Artifact PackageおよびThresholdはPhase 9設計時に動的に決定し、
本書の例示をHard-codeしない。

## 8. Acceptance Candidate

- Context Capacity／Usage／Effective Budget／Measurement Classが分離される。
- 自動圧縮はDefault OFFで、OBSERVEはContextを変更しない。
- ENFORCE／Manualは実行前Snapshotを作成し、失敗時に旧Contextを維持する。
- 原Chat履歴を自動削除しない。
- Handoff生成はActive Contextを変更せず、Log／Copy／`.md` Exportが可能である。
- Manual Compactionは正確なWarning、Snapshot ID、CancelおよびRollbackを持つ。
- Trace PanelはRaw／Evaluation／Action／Repair／Finalを同一Identity Chainで追跡できる。
- OBSERVEはRawとAction 0、ENFORCEはRawと実Action／Finalを比較できる。
- Full Rawは研究者が明示有効化でき、利用可能なRawを不要に隠さない。
- Runtimeが観測できないHidden Reasoningを捗造しない。
- Visibility／Persistence／Redaction／Retentionが分離される。
- Public／Basic／Git／Externalへの偶発的なRaw露出がない。
- Wide／Narrow／Mobile／Keyboard／Focus／Touch／JA／ENで操作可能である。
- Phase 9 Experiment RunでRaw／Final／Governance構成差／Cost／Latencyを比較できる。

## 9. Non-scope at Reservation Time

- Exact Threshold、Subphase Letter、Work Unit数またはUI Pixelの固定。
- Providerが露出しないInternal Reasoningの抽出。
- Raw Dataの無条件Public／Basic／Cloud公開。
- 外部Serviceへの無許可Upload。
- 単純要約がLosslessであるという主張。
- Phase 10以降のLedger／Graph／OCILNS等のResearch Algorithm実装。

## 10. Completion Line

本書のStatusは`PLANNED WORK PRIORITY RESERVATION`である。Phase 9設計時にAs-builtと
利用可能量を再評価し、全て実装、一部実装またはPhase 10以降継続を判定する。
本予約をPhase 6・7・8のClosure Blockerへ変更しない。
