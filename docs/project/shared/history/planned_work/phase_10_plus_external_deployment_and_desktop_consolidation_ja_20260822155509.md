# Phase 10以降 External Deployment／Desktop統合予約

```yaml
document_id: phase_10_plus_external_deployment_and_desktop_consolidation_20260822155509
status: accepted_planned_work_supersession
recorded_at: 2026-08-22 15:55:09 JST
authority: user_explicit_direction
mutation_authority: not_granted
external_action_authority: not_granted
```

## 1. Decision

Phase 6～9をLocal Runtime、Judge／Repair、Full RAG、Constitution／Agent／ToolおよびExperiment／Multi-Governance Research Platformへ集中させるため、次をPhase 10以降へ統合する。

1. AWS Infrastructure／Cloud Backend／Public-ready Surface。
2. Lightning AI StudioへのCurrent Runtime再反映とCross-environment Acceptance。
3. macOS Desktop Application Preview。
4. Windows Desktop Previewおよび後続Multi-OS展開。

`Phase 5-EX AWS Deployment Foundation`および`Phase 9-EX Desktop Application Preview`の前倒し予約は撤回する。Current Public Roadmapから両EX節を削除し、Phase 10 Platform／Backend ExpansionとDesktop Application化予約へ統合する。

## 2. Phase 6～9 Boundary

Phase 6～9では、AWS、Lightning更新、Desktop Packaging、一般公開、Cloud Secret、課金、URL共有、Code SigningまたはNotarizationを実装／Acceptance／Completion Dependencyにしない。

次は独立して継続可能である。

- Qwen3-4B Local Baseline。
- DeepSeek Local Feasibility／Adapter／Artifact／Model切替検証。
- Guard／Judge／Repair／RAG／Agent／Tool／ExperimentのLocal Runtime実装。
- Web／CLI／Runtime CoreのPlatform-neutral境界維持。

Local Model Artifactが既に存在しても、Cloud Resource作成、Current昇格、Model Loadまたは外部配置のAuthorityを生成しない。

## 3. Phase 10以降の分離Gate

Phase 10以降も、次を一つの許可へ結合しない。

- AWS Account／Quota／Cost確認。
- Network／Region／Secret／Storage。
- Model Hosting／Backend／Container。
- Public／Private／Auth／Rate／Token／Cost Limit。
- Ephemeral／Persistent Data Binding。
- Health／Shutdown／Rollback／Backup／Retention。
- Lightning Upload／Runtime Rebuild／External Browser Acceptance。
- Desktop Framework／Packaging／Signing／Notarization／Update。
- macOS／Windows／Linux対応。
- URL公開または第三者への共有。

各実操作は、その時点のユーザー明示許可とHuman Gateを必要とする。

## 4. Historical Reservation Handling

`docs/project/shared/history/planned_work/`および各Phase Historyに残るPhase 5-EX、Phase 9-EX、Phase 3 Closure後のAWS準備、Phase 4-H／別Deployment GateへのLightning延期記述は、当時の計画Evidenceとして変更しない。Current計画としては本Documentと更新後の`docs/public/roadmap_ja.md`が後順位の決定としてSupersedeする。

## 5. Current Objective

```text
Phase 6 : Judge／Evaluation／Repair／Observability — 重点Closure
Phase 7 : Full RAG／Data Governance — 最小Closure
Phase 8 : Constitution／Agent／Tool Prototype — 最小Closure
Phase 9 : Experiment／Multi-Governance Research Platform — 重点Closure
Phase 10以降 : AWS／Lightning／Desktop／Cloud Scale／Multi-OS
```

本予約はPhase 10の開始、Source実装、External操作、Git操作または公開許可ではない。
