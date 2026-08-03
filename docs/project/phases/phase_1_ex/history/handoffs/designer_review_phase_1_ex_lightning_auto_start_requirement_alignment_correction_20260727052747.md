# Phase 1-ex Lightning Auto-start Requirement Alignment Correction Review

```yaml
document_id: designer_review_phase_1_ex_lightning_auto_start_requirement_alignment_correction
phase: phase_1_ex
status: correction_accepted
language: ja
created_at: 2026-07-27 05:27:47 JST
owner: 設計統括者役
supersedes: designer_review_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727051659.md
corrected_by: explicit_user_requirement_reconfirmation
```

## 1. 訂正結論

[前Review](designer_review_phase_1_ex_lightning_auto_start_go_no_go_assessment_20260727051659.md)で、`DEFER`の最終決定とStage A Read-only Availability Checkを同列の選択肢として提示した判断を訂正する。

ユーザーが繰り返し明示した必須要件は次である。

> Studioが勝手にSleepしても、所有者のBrowser Tab、Studio画面およびTerminalが開かれていない状態で、第三者が公開URLへアクセスするだけでStudioとWeb Appが起動し、利用可能になること。

この条件を満たせないAuto-start工程は、本Projectにとって実用上の意味を持たない。

したがって正しい状態は次である。

```text
Assessment Evidence Package:
  ACCEPTED

Implementer DEFER Recommendation:
  REJECTED_AS_FINAL_PATH

Reason:
  manual Basic Preview satisfies current purpose という前提がUser Requirementと矛盾

Stage A Read-only Availability Check:
  REQUIRED

Stage B Unattended External Wake Trial:
  REQUIRED_IF_STAGE_A_AVAILABLE

Traffic-aware Auto-start Decision:
  IN_PROGRESS
```

## 2. 前Reviewの誤り

前Reviewは、実装担当Statusの次の根拠を妥当としてAcceptedした。

```text
Basic Previewを手動起動すれば現時点のPreview目的を満たせる。
```

これはユーザー要件と一致しない。

手動Basic Previewは、Model、認証、Lifecycleおよび外部到達性を確認する前提試験としては有効である。しかし、所有者がStudioを手動起動し続ける必要がある状態は、今回の公開Preview目的を満たさない。

設計統括者役はこのRequirement ConflictをReview時に検出すべきだった。前Reviewで`DEFER`を同列の選択肢として提示したのは設計判断の誤りである。

## 3. Official Platform Evidence

Lightning公式Docsでは、Web App向けAuto-start／Serverlessについて次が示されている。

- StudioはApp未使用時にSleepできる。
- Public URLへのUser RequestでStudioがWake-upする。
- OwnerがBrowserを開き続けることを前提としない。
- Wake-up時にはCold Start遅延が発生し得る。

公式参照：

- [Lightning Expose web apps](https://lightning.ai/docs/overview/host-web-apps/expose-web-apps)
- [Lightning Host web apps](https://lightning.ai/docs/overview/host-web-apps)
- [Lightning On-start actions](https://lightning.ai/docs/overview/ai-studio/on-start-actions)
- [Lightning Auto sleep](https://lightning.ai/docs/overview/ai-studio/auto-sleep)

したがって、ユーザー要件はLightningが案内するAuto-start用途と方向上整合している。

ただし、現Account、Organization、Studio、PluginおよびFree／Credit条件で実際に利用可能かは、Stage A／Stage Bで確認する。

## 4. 必須Acceptance Condition

Traffic-aware Auto-startを`GO`とするための中核条件：

```text
Precondition:
  Studio = sleeping
  Basic Preview Process = not running
  Owner Browser = closed
  Owner Studio Tab = closed
  Owner Terminal／SSH Session = not required

Trigger:
  Third-party viewer opens the public URL

Required Result:
  Lightning wakes the Studio
  Startup Command invokes the repository lifecycle entry point
  Model loads
  /healthz becomes HTTP 200
  Basic Authentication boundary remains effective
  Viewer can use MARGPA
```

Ownerが別操作でStudioを起動する、Terminalを開く、Browser Tabを維持する、または閲覧者へ事前連絡して手動対応する構成は、このAcceptance Conditionを満たさない。

## 5. Correct Decision Flow

```text
Stage A：Read-only Availability Check
  ├─ unavailable
  │    → Current Lightning Account／StudioではNO_GO
  │       または一時的外部制約ならBLOCKED_WITH_RECHECK_CONDITION
  │
  └─ available
       → User Review／Explicit Authorization
       → Stage B：Unattended External Wake Trial
            ├─ fail
            │    → NO_GOまたはFix設計
            └─ pass
                 → GO／CONDITIONAL_GO
```

`DEFER`は、単に面倒、未確認、または手動起動で代替できるという理由では選ばない。

外部Quota、Account制約、Platform障害などにより現在検証不能である場合だけ、再開条件と期限を明示した一時的な延期候補となる。

## 6. Stage Aの位置づけ

Stage Aは任意ではない。

Platform Mutationを行わず、現Account／Studioで次を確認する必須Gateである。

- API Builder／Public App／Auto-start機能の有無
- 現Accountでの利用可否
- CPU Studioへの適用可否
- Public URLとAuto-start設定の関係
- Startup Command設定可否
- Free／Credit条件
- URL Access Wake-upが公式UI上で提供されるか

Stage Aで機能が利用可能なら、Stage Bを行わずに工程を終了しない。

## 7. Stage Bの位置づけ

Stage Bは実際の必須要件を確認するAcceptance Testである。

最低限：

1. Basic Previewを停止する。
2. Auto-start用Platform設定とStartup Commandをユーザー操作で設定する。
3. StudioをSleepさせる。
4. Owner Browser／Studio Tab／Terminalを閉じる。
5. 別Accountまたは第三者相当のBrowser SessionからPublic URLを開く。
6. URL AccessだけでWake-upすることを確認する。
7. Model Load、Health、Basic認証および生成を確認する。
8. 再Sleep後に同じURLで再度Wake-upする。
9. URL維持、Cold Start、Creditおよび情報非露出を記録する。

Stage BはPlatform Mutationを含み得るため、Stage A結果のReviewとユーザーの明示許可後に行う。

## 8. Basic Previewの扱い

Basic Preview Lifecycle Acceptanceは無効化しない。

次の前提技術としてAcceptedを維持する。

- Repository Lifecycle Script
- Managed Secrets
- Basic Authentication
- Model Load
- Health Contract
- External Browser
- Restart／Stop
- Single Process Safety

ただし、Basic Previewの手動起動成功をTraffic-aware Auto-startの代替Acceptanceにはしない。

## 9. Scope／Authority

本Correction ReviewはDocs上のRequirement Alignmentを訂正する。

許可すること：

- Stage A Read-only Availability Checkの準備・実施
- Official Platform Evidenceの参照
- 未確認事項の明示

まだ許可しないこと：

- Stage B Platform Mutation
- Auto-start設定変更
- Startup Hook実装
- Public URL変更
- 匿名Public Demo
- RAG
- Git操作

## 10. 次の状態

次はStage A Read-only Availability Checkである。

Stage Aは`DEFER`と並ぶ任意選択肢ではなく、Traffic-aware Auto-start要件を継続するための必須工程として扱う。
