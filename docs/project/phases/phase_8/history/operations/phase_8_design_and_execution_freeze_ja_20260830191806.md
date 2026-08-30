# Phase 8 Design／Execution Freeze

```yaml
document_id: phase_8_design_and_execution_freeze_20260830191806
document_state: frozen_ready
phase: phase_8
language: ja
created_at: 2026-08-30 19:18:06 JST
authority_owner: Nazuna Research
implementation_started: false
```

## 1. Freeze Decision

Phase 8の現時点設計を次でFreezeする。

```text
Milestone      : Governed Agentic Execution Research Foundation
Packages       : P8-0〜P8-F
Work Units     : 35
Acceptance     : 40
Maximum Claim  : COMPLETE_CANDIDATE_FOR_USER_MANUAL
Current State  : READY／NOT STARTED／NOT ARMED
```

## 2. Frozen Scope

1. Manual pasted URL Fetch／Display／Untrusted Evidence／Citation。
2. Branch UI既定非表示、Archive一覧／開く／解除。
3. `constitution/` Provisional Runtime Constitution。
4. 通常Chat／Dev Agent Preview切替。
5. Run／Step／Tool Registry／Tool Port／MCP Client Adapter Port。
6. Fake／Deterministic Toolによる複数Step Execution。
7. Plan-only／Manual／Risk-based／Important-gate-only Harness。
8. Stop／Cancel／Budget／Persistence／Evidence／Failure Presentation。

## 3. Frozen Deferral

```text
Phase 9:
  Selene／Qwen3Guard／Semantic 109／Judge／Repair／Stale Fact Governance／Progressive ENFORCE

Phase 10:
  All Docs 2 Pass／Shared Constitution 2 Pass／PADG／Full Runtime Constitution／Large UI Consolidation

Phase 11+:
  General／Automatic Web Search／Formal Agent Level 1〜3／Generic MCP／Remote Side Effect／Hardening
```

## 4. Design Sources

- Phase 7 Final Closure／Manual Acceptance／未解決Registry。
- Manual URL EvidenceとGeneral Web分離のPlanned Work。
- Branch UI／Archive管理Planned Work。
- Dev Agent Level／Important-gate-only Harness Planned Work。
- Provisional／Full Runtime Constitution分離とLoose Coupling Planned Work。
- Public Roadmap 2種。

## 5. Quality Boundary

個人PoC／MVPとして、中心経路が動く、データ破損・虚偽成功がない、次Phaseの土台になる、User Manualへ渡せる、の4条件で止める。実画面前に理論上の一発完全合格を追わず、軽微FindingはStable未解決Registryへ送る。

## 6. Activation Boundary

本FreezeはPhase 8実装開始Authorityではない。Commit／Push後にUser Backup、Preflight、Start Authorizationを別々に成立させる。
