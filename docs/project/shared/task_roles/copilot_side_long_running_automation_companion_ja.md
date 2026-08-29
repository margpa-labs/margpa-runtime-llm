# GitHub Copilot側設計者兼実装者役 — Long-running Automation Companion

```yaml
document_id: copilot_side_long_running_automation_companion
document_type: shared_stable_task_role_operating_contract
document_state: current
empirical_state: pre_pilot_unverified
language: ja
created_at: 2026-08-28 19:19:37 JST
last_updated_at: 2026-08-28 19:19:37 JST
decision_authority: user
provider: GitHub Copilot app
target_role: 設計者兼実装者役
default_long_running_mode: inactive_until_exact_start
pilot_evidence_cadence: work_unit_and_package_boundary
```

## 0. 目的

本書は、GitHub Copilot appを長時間の実装へ投入する際の継続、Recovery、Evidenceおよび利用可能量管理を定義する。`copilot_side_designer_implementer_operating_notes_ja.md`を軽量化または置換しない。

## 1. Activation

Long-running Modeは、UserのExact StartとActive Handoffが両方成立した場合だけ有効になる。Copilot appの`Autopilot`選択だけでは有効にならない。

```text
Installed／Repository Added／Autopilot Selected
≠ Long-running Authority

Role Receipt + Handoff Receipt + Exact User Start
= Active Bounded Long-run
```

本書作成時点のModeは`inactive_until_exact_start`である。

## 2. Continuous Execution

Active Scope内では、Routineな確認を挟まず次のBoundaryまで自走する。

```text
Work Unit Entry
→ Implementation
→ Focused Verification
→ Work Unit Recovery
→ Package Integration
→ Package Recovery
→ 次Work Unit／Package
```

Progress Reportは停止理由にしない。True Stop、Resource Hard StopまたはExact Returnまで継続する。

## 3. Pilot Evidence Cadence

初回PilotからProvider特性が安定するまで、少なくとも次の境界ごとに新規Append-only EvidenceまたはRecovery Indexを残す。

1. Role／Authority Bootstrap完了時。
2. Exact Handoff／Digest Receipt完了時。
3. 最初のCommand／Mutation前のEntry Boundary。
4. 各Work Unit完了時。
5. 各Package完了時。
6. 長時間Command、Test、Build、Model、Browserまたは外部Tool実行の前後。
7. Manual／Auto Compactionを認識した前後。
8. 5時間／週間／Credit／Context等のResource停止と復帰時。
9. Incident、Near Miss、Unexpected Prompt、Unexpected Tool ActionまたはHarness挙動の発生時。
10. Implementation Freeze、Internal Review各Cycle、Rework各Cycle、Final VerificationおよびReturn時。

Provider共通の意味ある作業Cycleは`docs/project/shared/history/automation/`へ記録する。Phase固有の実装状態はPhase `history/index/`へRecovery Indexとして記録し、両者の責務を混同しない。

## 4. Evidence Minimum Fields

各Pilot Evidenceは、取得可能な範囲で次を持つ。取得不能値を推測しない。

```text
Provider／App
Task Identity
User-observed Model Label／Reasoning／Context／Mode
Active Role／Authority／Handoff／Digest
Current Phase／Package／Work Unit
開始／完了時刻
成立したAction／Mutation／Command
Test／Static／Build結果
Root／Git／Network／Provider Memory／User Data／Model Action Inventory
Compaction／Session／Resource Signal
Recoveryに再読したCanonical Docs
Incident／Near Miss／Failure／Open Finding
PASS／PARTIAL／NOT RUN／UNAVAILABLE／USER GATE／FAIL
作成したRecovery／Return Path
Claimしなかった事項
```

UI上のLabelしかない場合は`USER_OBSERVED_UI_LABEL`と明記し、内部状態へ一般化しない。

## 5. Recovery Index Contract

Recovery Indexは、別Taskが会話Contextなしで再開できる粒度を持つ。

- 最後に完全成立したWork Unit／Package。
- 途中のFile／Mutation／Test状態。
- やり直してはいけない範囲。
- Exact Next Work Unit。
- Open Finding／Incident。
- Active Process／Model Load／Temporary Artifact。
- Authority／Action Inventory。
- 再開時Mandatory Reading。

「作業中」「ほぼ完了」だけで停止しない。未確定部分は明示的に`PARTIAL`とする。

## 6. Compaction／Session Recovery

CopilotのAuto-compaction有無、発動閾値、圧縮品質および自動再開は実証前`UNKNOWN`である。Context表示が`400K`または`1.1M`でも、Compaction不要とは判断しない。

各Work Unit／Package BoundaryでRolling Recovery Baselineを作る。Compactionを認識した場合は、運用規則が定める七文書を明示再読し、次をEvidence化する。

- 認識方法。
- 圧縮前後で保持／欠落した事項。
- Canonical Docsから復旧した事項。
- Digest比較の有無。
- Exact Resume Boundary。
- Authority非継承を維持したこと。

Before Digestがない場合、After Digestだけで「前後一致」をClaimしない。

## 7. Resource Management

Context、5時間、週間、CreditまたはProvider独自のResource表示を混同しない。Userが伝えたSignalは、そのResource種別をExactに記録する。

Active HandoffがReserve Floorを定める場合、その値をHard Stopとして扱う。表示値の訂正があった場合、誤ったDraft Completion ClaimをSupersedeし、既に成立したEvidenceだけを保持する。

Resource Hard Stopでは、新規実装や再検証を開始せず、現在のCommand／Processを安全に収束し、RecoveryとStopped-safe Returnを作る。Provider側の自動再開を前提にしない。

## 8. Harness／Tool Safety

Harness緩和またはAutopilot中でも、Command前に次を確認する。

- Working DirectoryがAuthorized Rootか。
- Cache／Temp／Log／BasetempがProject内Task-owned PathへBoundされるか。
- Shell Redirection、Environment Variable、Command substitutionがRoot外を指さないか。
- Git、Network、Package ManagerまたはOS既定Pathへ暗黙接触しないか。
- Command ScopeがActive Work Unitに必要か。

不明なToolは、いきなり長時間／Mutation Actionへ使わず、Exact Handoffが許す最小Read-only Probeから特性をEvidence化する。

## 9. Evidence量の制御

初回Pilotでは高頻度Evidenceを優先するが、同じ内容を無意味に複製しない。

```text
Provider特性を新しく示す
Incident／Recoveryを再現可能にする
Work Unit／PackageのResumeに必要
Acceptance／Review／Claimを支える
```

のいずれにも該当しないChat経過は、Evidence Fileを増やさずPackage Recoveryへ要約する。Pilot後に十分な反復Evidenceが得られた項目は、Controller ReviewとUser DecisionによりCadenceを軽量化できる。

## 10. Return

Complete／Incomplete／Stopped-safeのいずれでも、Exact Return Handoffと最新Recoveryを作り、Controller Independent Review待ちで停止する。自動的にPhase Closure、Git、Backup、Roadmapまたは次Phaseへ進まない。
