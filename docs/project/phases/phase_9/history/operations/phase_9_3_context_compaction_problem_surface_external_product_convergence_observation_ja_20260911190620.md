# Phase 9-3 Context Compaction — 外部Product Problem Surface収束 Observation

```yaml
document_id: phase_9_3_context_compaction_problem_surface_external_product_convergence_observation_20260911190620
document_type: external_product_convergence_observation_evidence
document_state: append_only_history
recorded_at: 2026-09-11 19:06:20 JST
language: ja
project: MARGPA-RUNTIME-LLM
phase: phase_9_3
evidence_owner: Nazuna Research
decision_authority: user
observation_source: user_supplied_local_screenshot
external_product: claude_code
priority_or_copying_claimed: false
append_only: true
```

## 1. 記録目的

Phase 9-3でContext Compaction／Recoveryの改訂設計と実装を開始した当日、Claude CodeのUIにContext使用量表示、Auto Compaction閾値表示およびManual Compaction Actionが表示されたことを、ユーザー提供ScreenshotとRepository内Artifactの時刻関係とともに保存する。

本記録の目的は、「どちらが先に発明したか」「外部Productが本Projectを参照したか」を主張することではない。MARGPA-RUNTIME-LLMが独立に設計対象化していたFailure Surfaceが、Frontier Agent Product側でも利用者向け機能として表面化したという外部収束Observationを、後付け記述と混同しないProvenance付きで残すことである。

## 2. Direct Evidence

Screenshot:

```text
Path:
docs/project/phases/phase_9/images/claude_code_manual_compaction_ui.png

SHA-512:
ce7389df606c6702e6fe7d1783696a9cac019c72f2d978eae657af87250f3141ada442dd55ad9d762766f91074074d2f3fb9a301c33f0b8d63ff49f040459863

Dimensions:
441 x 277 px

Filesystem modified time observed during recording:
2026-09-11 18:42:51 JST
```

Screenshot上で直接確認できる表示は次の通り。

- `コンテキストウィンドウ`
- `591.5k / 1M (59%)`
- `97%で自動的に圧縮します`
- `セッションを圧縮`
- 5時間制限および週間・全モデル制限の表示

このうちPhase 9-3との比較対象は、Context使用状況、Auto Compaction閾値およびManual Compaction Actionの3点である。

## 3. Repository側の先行Artifact

Filesystem時刻はGit Commit時刻や外部公開時刻を証明するものではないが、同一Local Working Tree内の作業順序を確認する補助Evidenceになる。

| Artifact | 観測時刻 | 内容 |
|---|---|---|
| `phase_9_3_context_compaction_recovery_revised_execution_design_and_work_breakdown_ja.md` | 2026-09-11 17:49:54 JST | Manual常時可用、Auto独立Boolean Default ON、Hard Reserve、Recovery、最小2 Icon UIを規定 |
| `phase_9_controller_to_claude_phase_9_3_context_compaction_recovery_revised_long_run_exact_handoff_ja_20260911175040.md` | 2026-09-11 17:53:53 JST | 上記設計を実装Work Unitへ分解し、Claude Codeへ送るExact Handoff |
| Claude Code UI Screenshot | 2026-09-11 18:42:51 JST | Context量、97% Auto Compaction、Manual Session Compactionを表示 |

したがって、少なくとも本Local Artifact系列では、Claude Code UIの当該表示をScreenshotとして保存する前に、Phase 9-3の改訂設計と実装Handoffが既に作成されていた。

## 4. User Observation

ユーザーはScreenshot取得時、Claude Code上で当該機能を「数分前には確認していなかった」と報告した。これはユーザーの直接体験に基づくObservationであるが、Product Release時刻、Feature Flag反映時刻、Account別Rollout、Client Cacheまたは以前から存在したUIの見落としを外部から区別できない。

よって本書は次を分離する。

- **Directly Observed**: Screenshotに上記3機能面が表示されている。
- **Repository Provenance**: Phase 9-3改訂設計とHandoffのLocal Artifact時刻がScreenshot保存時刻より前である。
- **User-reported Observation**: 数分前には同じ表示を確認していなかった。
- **Unknown**: Anthropic側の設計開始日、実装開始日、Release／Rollout時刻、対象Account、他社内部設計。
- **Not Claimed**: 模倣、因果関係、発明の先後、特許上の先使用・新規性。

## 5. 設計比較

外部UIとPhase 9-3は、表面上、次のProblem Surfaceで一致する。

```text
Context使用量を可視化する
Auto Compactionの発動点を扱う
Manual Compaction Actionを利用者へ提供する
```

Phase 9-3はこれに加え、現時点の設計上、次をSystem Problemとして扱う。

```text
ManualとAutoの独立
Compaction Working ReserveとHard Reserve
Canonical Conversation原本とActive Projectionの分離
Pre-action Snapshot
Artifact Identity／Schema／Digest
CAS Activation
Failure時の旧Projection維持
Rollback
Recovery Index
Selective Rehydration
Handoff Artifact
Provider-neutral Port
Evidence／Restart Read
```

ただし、これら追加項目の一部は本Observation時点で実装途中であり、Controller Independent ReviewによりBlocker／Majorが確認されている。設計対象であることと、実装・Verification・Acceptanceが完了したことを混同しない。

## 6. Evidenceとしての意味

Evidence-Firstで許容される最大Claimは次である。

```text
Phase 9-3が選択したContext使用状況の観測、Auto Compaction、Manual Compactionという
Problem Surfaceは、個別Projectだけの特殊事情ではなく、同時期のFrontier Agent Productでも
利用者向け機能として対処されている問題面と一致した。
```

この一致はMARGPA-RUNTIME-LLM実装の正しさを証明しない。一方、Context Compaction／RecoveryをPhase 9の研究・実装対象へ置いたProblem Selectionの妥当性を補強する外部Observationとして利用できる。

## 7. Git Provenance方針

本Screenshot、Phase 9-3改訂設計、Partial実装／Return／Recovery、Claude Code Provider Self-assessmentおよびCodex Controller Independent Reviewを同一Git Checkpointへ含める。これにより、外部Screenshotを確認した後に設計全体を後付けしたという誤認を避けられるよう、少なくともRepository上の一貫した時点を保存する。

GitのAuthor／Commit Timestampは書換え可能であり、単独で法的な優先日や発明日を証明するものではない。GitHub Push時刻を含むRemote記録は補助Provenanceである。特許、新規性または先使用の判断は、本書では行わない。

## 8. Maximum Claim

```text
P9_3_CONTEXT_COMPACTION_EXTERNAL_PRODUCT_PROBLEM_SURFACE_CONVERGENCE_OBSERVATION_RECORDED
```

本書はObservationの保存だけをClaimし、Phase 9-3 Complete、外部Productとの優劣、模倣、発明の先後または特許可能性をClaimしない。
