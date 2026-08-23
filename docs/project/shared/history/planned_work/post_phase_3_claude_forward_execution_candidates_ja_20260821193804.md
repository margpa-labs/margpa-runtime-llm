# Phase 3以降 Claude前倒し実行候補

```yaml
document_id: post_phase_3_claude_forward_execution_candidates
status: accepted_reservation
created_at: 2026-08-21 19:38:04 JST
from: プロジェクト責任者兼設計統括者役（Codex）
to: future_controller_and_claude_side_design_governor
execution_authorized: false
git_mutation_authorized: false
external_mutation_authorized: false
```

## 1. 目的

Codex利用可能量がClaude Codeより先に枯渇する可能性へ備え、後続PhaseでClaude側へ前倒し委任できる作業を、依存関係とHuman Gateで分類する。本書は候補一覧であり、Phase開始、実装、Download、AWS、Gitまたは公開を許可しない。

## 2. Codex残量がある間に優先して準備するもの

1. Phase 4のSubphase分割、Frozen Requirements／Architecture／ADR／Execution Plan／Acceptance Matrix／Claude Handoff。
2. Phase 5の大枠依存順、Phase 5-EX AWS境界、停止線および最終Closure境界。
3. 各PhaseでClaudeが停止する`COMPLETE_CANDIDATE`線と、Codex／User専用最終Closure線。
4. Stable Docs、Roadmap、Git、External、Secret、Cost、User実DataおよびRoot外操作のAuthority境界。
5. Auto-Compaction後に復元するCurrent WU、Exact Mutation、Open FindingおよびNext Routeの正本Entry。

## 3. Phase 3 Closure前でも前倒し可能なRead-only／Design作業

- DeepSeek V4 Flash／8B FallbackのArtifact Inventory、Exact Revision、License／Security確認項目整理。
- SGLang／vLLM／現行Adapter間のCompatibility MatrixとBenchmark設計。
- AWSのAccount／Quota／Cost／Network／Secret／Storage／Shutdown／Rollback設計。Resource作成はしない。
- Phase 4 Main Governance Point、Binding、Observe／Enforce、Repair境界の設計候補整理。
- Phase 5 Threat Model、Rule-based Guard、Policy／Authority／Human Approval Contractの設計候補整理。
- Phase 9-EX macOS Desktop Shellの技術候補、Packaging／Signing／Update／Sandbox比較。実装はしない。
- Responsive UI既知DebtのRead-only InventoryとAcceptance候補整理。

これらはCurrent PhaseのFrozen Sourceへ書き込まず、`shared/history/planned_work/`の新規Append-only Candidateとしてのみ作成する。

## 4. Phase 3 Closure後にClaudeへ大きく委任可能な作業

- Frozen Phase 4 Packageに基づくSubphase実装、Focused Test、Self-review、局所Reworkおよび`COMPLETE_CANDIDATE`作成。
- Phase 4内のModel Adapter／Backend Adapter／Main Governance Point／Mode Matrix／Evidence Integration。
- Frozen Phase 5 Package完成後のGuardrail／Policy／Authority実装。
- Phase内のAppend-only Recovery Entry、Compaction EvidenceおよびExact Mutation集約。
- Technical Test／Static Check／Frontend Build等の機械的検証。

ClaudeはStable Roadmap、Git、GitHub、User Backup、Phase完了宣言および次Phase開始Gateを扱わず、指定されたCompletion Lineで停止する。

## 5. Human／Codex Gateが必要で前倒し禁止のもの

- ModelのCurrent Promotion、実運用Default変更および大容量Artifact削除。
- AWS Account／Quota／Cost承認、Resource作成、Secret設定、Network公開、URL共有。
- User実Data Migration、Persistent Data Binding、Backup／Restoreの実操作。
- Stable Current Docs／Public Roadmapの最終更新。
- Git Commit／Push／Tag／Release。
- Phase最終Acceptance、Risk受容、正式Deferral、次Phase開始宣言。
- Project Root外または別Projectへの操作。

## 6. 推奨Route

```text
CodexがPhase設計とAuthority EnvelopeをFreeze
  → ClaudeがPhase実装をCOMPLETE_CANDIDATEまで自走
    → Codexが重大Findingだけ独立Review
      → ClaudeがExact Rework
        → Userが最小Manual Acceptance
          → Codexが最小Closure／Backup／Git／次Phase READY
```

Phase 3・4のClosureは利用可能量保全のため最小化し、重大Finding、実装／Test Evidence、必要最小限のManual Acceptance、Status／Index／Roadmap、Backup、Git一致および次Phase READYだけを必須とする。Phase 5終了時に余力があれば通常の完全Closureへ戻す。

## 7. 今回のRoadmap予約

- Phase 5-EX：AWS Deployment Foundation／Public-ready Surface。準備は前倒し可能、実Resource／課金／公開は別Gate。
- Phase 9-EX：macOS Desktop Application Preview。Windowsは可能なら同時、難しい場合は後続へ正式延期。
