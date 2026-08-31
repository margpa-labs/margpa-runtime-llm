# Phase 8 Copilot残7% Resource Exhaustion／部分実装Evidence

```yaml
document_id: phase_8_copilot_seven_percent_resource_exhaustion_and_partial_implementation_evidence_20260830230710
document_type: cross_provider_resource_and_automation_evidence
document_state: final
language: ja
created_at: 2026-08-30 23:07:10 JST
provider: GitHub Copilot app
phase: phase_8
observed_resource_entry: 7_percent_remaining
terminal_state: resource_exhausted_partial
claim_scope: this_phase_8_short_pilot_only
```

## 1. 目的

本書は、Copilotの利用可能量がUser観測で残7%の状態からPhase 8先頭へ投入され、Resource Exhaustionまでに何を成立・未成立として残したかを記録する。Copilot一般またはGPT-5.6 Terra一般の永続特性へは一般化しない。

## 2. Entryと運用意図

User報告値：

```text
Codex Weekly Remaining   : 64%
Claude Weekly Remaining  : 42%
Copilot Weekly Remaining : 7%
```

Claude分の保全とCopilotの追加観測を兼ね、CopilotにはPhase 8全体ではなく`P8-0／P8-A`のResource-bounded Scopeを付与した。残7%での中断を想定し、今回に限ってWork UnitごとのRecovery Indexを求めた。

## 3. 成立したRecovery Boundary

Copilotは次の3件を、利用可能量が尽きる前に個別Recoveryとして残した。

1. `P8-0-WU-001`：Phase 7 Web KnowledgeのAs-built Map。
2. `P8-0-WU-002`：Citation永続化とMain Model Context注入点のAdjacent Boundary。
3. `P8-0-WU-003`：実Network・Git・User Dataを禁止したAuthority／Test Freeze。

これにより、後続ClaudeはMandatory ReadingとBaselineを最初からやり直さず、`CP8-04`から差分回復できた。残量に比例した細粒度Recoveryは、今回は実際に有効だった。

## 4. Current Partialと実装Failure

CopilotはDirect URL FetchのAPI契約とTestを開始し、次を部分追加した。

- `URL_FETCH_DISABLED`／`URL_REJECTED`。
- `WebCitation.content_sha512`。
- `DirectUrlFetchRequest`。
- `/api/v2/web-search/direct` Route。
- `WebKnowledgeService.fetch_direct_url()`。
- Disabled／Explicit URL／Rejected URLのTest。

一方、`fetch_direct_url()`を既存`search_and_fetch()`の途中に挿入し、元Methodの本体を分断した。そのためFocused Test Collectionは次で失敗した。

```text
IndentationError: unindent does not match any outer indentation level
src/margpa_runtime_llm/modules/web_knowledge/application/web_knowledge_service.py:223
```

Copilot自身はTestでIndentation Failureを検出し、Method Boundaryを修正する方針を表明したが、その直後にUserから利用可能量が尽きたと報告された。Copilot自身のStopped-safe Returnは作成されていない。

## 5. Automation観測

- 今回の短時間Pilotでは、CopilotがRoutine Confirmationや進捗報告を理由に勝手に終了した事実は観測していない。
- 終了原因はUserが報告したResource Exhaustionであり、実装難度を理由にした自己Gateではない。
- 一方、実装差分にはImport不能になるIndentation欠陥が含まれ、完成Claimを与えられる品質ではなかった。
- Manual Compaction／Auto-compactionの発動有無、Context Loss、残7%内の正確なToken・Command別消費量は未観測である。

## 6. Disposition

```text
Resource Boundary Design       : EFFECTIVE FOR THIS RUN
Granular Recovery              : EFFECTIVE FOR CROSS-PROVIDER RESUME
Implementation Completion      : PARTIAL
Focused Test                   : FAILED AT COLLECTION
Unnecessary Stop Observed      : NO IN THIS SHORT RUN
Compaction Behavior            : UNKNOWN
Independent Review Requirement : RETAINED
```

今回の結果は「残量が少ないProviderを、小さいScopeと細粒度Recoveryで実装補佐に使う」方式の有効性を支持する。ただし、Source品質とCross-component完結性は別Providerの回復・Reviewを必要とした。

## 7. Canonical Evidence

- [Phase 8 Copilot Entry Baseline](phase_8_copilot_seven_percent_resource_bounded_entry_baseline_ja_20260830195125.md)
- [Controller Resource Recovery](../../../phases/phase_8/history/index/phase_8_copilot_resource_exhausted_controller_recovery_ja_20260830200227.md)
- [WU-001 Recovery](../../../phases/phase_8/history/index/phase_8_copilot_p8_0_wu_001_recovery_index_ja_20260830.md)
- [WU-002 Recovery](../../../phases/phase_8/history/index/phase_8_copilot_p8_0_wu_002_recovery_index_ja_20260830.md)
- [WU-003 Recovery](../../../phases/phase_8/history/index/phase_8_copilot_p8_0_wu_003_recovery_index_ja_20260830.md)
