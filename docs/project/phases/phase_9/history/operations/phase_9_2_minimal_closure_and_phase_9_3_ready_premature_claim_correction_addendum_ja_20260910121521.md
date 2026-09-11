# Phase 9-2最小Closure／Phase 9-3 READY 早期Claim訂正Addendum

```yaml
document_id: phase_9_2_minimal_closure_and_phase_9_3_ready_premature_claim_correction_addendum_20260910121521
document_state: accepted_append_only_correction
phase: phase_9
recorded_at: 2026-09-10 12:15:21 JST
language: ja
authority_owner: Nazuna Research
decision_authority: user
corrects: phase_9_2_minimal_closure_and_phase_9_3_ready_receipt_20260910120644
phase_9_2_status: incomplete_bounded_experimental_gate_rework_required
phase_9_3_status: design_draft_complete_not_ready
git_write_performed: false
```

## 1. 訂正結論

2026-09-10 12:06:44 JSTのReceiptで記録したPhase 9-2の`COMPLETE／USER ACCEPTED／MINIMAL CLOSURE`およびPhase 9-3の`READY`は早期Claimであり、本Addendumで撤回する。

成立しているのは、通常UIからExperiment Workspaceへ入るButton／State／Mountの削除、配信Static Bundleへの反映、およびユーザーによる実Browser上の入口非表示確認である。

一方、Experiment Backend API、Run Worker、Production Turn Adapter、Live Configuration ReaderおよびExperiment Configuration Leaseを、明示的なDefault-OFF Experimental Gate配下へ置く変更は実施されていない。したがって「通常UIから見えない」ことと「機能全体が通常Runtimeから無効化されている」ことを同一視してはならない。

## 2. Source確認で判明した残存境界

- `src/margpa_runtime_llm/web/app.py`はExperiment Routerを登録したままである。
- `src/margpa_runtime_llm/web/experiment_routes.py`の`/api/v7/experiment`系Endpointは残っている。
- `src/margpa_runtime_llm/bootstrap/web_application.py`は通常のConversation Persistence構成でExperiment Service／Run Workerを構築し得る。
- 同BootstrapはLive Production Turn Adapter、Live Configuration ReaderおよびExperiment Configuration Leaseを構築する。
- Settings変更RouteはLease保持中に`experiment_configuration_lease_held`として409を返す境界を持つ。
- Experiment専用の明示的なEnable／Disable Gateは確認できなかった。Conversation Persistenceの有無はExperiment機能の明示的Opt-inと同義ではない。

このため、UIを隠した状態でもAPI経由の見えないRunが成立し、実行中のLeaseによってSettings変更が一時拒否される可能性が設計上残る。

## 3. 直前Reworkで意図的に触れなかった範囲

直前のExperiment UI延期Handoffは、Headless Coreを保持する方針に基づき、次を明示的な変更禁止範囲としていた。

- Experiment Domain／Application Core。
- Experiment Adapter／Store／Run Worker。
- Experiment API Route。
- Bootstrap上のExperiment Service／Worker／Lease。

Claude Exact ReturnもBackend Experiment Coreを未変更と報告している。したがって、今回の不足は実装漏れを隠したものではなく、Controller側が「UI入口非表示だけでClosure可能」と早く判定したScope設計不足である。

## 4. 必要な限定Rework

Phase 9-2の残件は、Headless Coreの削除ではなく、機能全体を明示的なExperimental Gate配下に置く限定Reworkである。

最低限のContractは次とする。

1. Experiment RuntimeはDefault OFFとする。
2. 明示的Opt-in時だけExperiment API Run、Service、Worker、Production Adapter、Live Configuration ReaderおよびConfiguration Leaseを有効化する。
3. Default OFF時はExperiment起因のActor Call、Background Worker、Mutation、Evidence、Lease保持を0にする。
4. Default OFF時はExperimentを原因としてSettings変更を409拒否しない。
5. Gate ON時は既存Headless CoreとTop-level Experiment経路を保持する。
6. UI入口はPhase 11以降まで非表示のままとする。
7. Gateの名称、CLI／Configuration Surface、Disabled APIのHTTP Contractは実装前に既存Configuration方式と整合させる。

## 5. 必須の機械検証

- Default起動でExperiment Runtimeが構築・開始されない。
- Default起動でExperiment APIからRunを開始できない。
- Default起動でSettings変更がExperiment Leaseを理由に拒否されない。
- 明示的Enable時だけ既存API／Worker／Leaseが動作する。
- Enable時の既存Headless Core、Persistence、ComparisonおよびRestart Readが退行しない。
- ShutdownはEnable時に構築したWorkerだけを安全に停止する。

## 6. User Manual／Phase 9-3 Disposition

通常UI入口の非表示確認は既にPASSしており、同じ確認を反復する必要はない。限定Rework後のGateは原則として機械検証で成立させる。User実画面確認を追加する場合も、通常起動でExperiment入口がないこととSettings変更が正常であること以上へ無目的に拡大しない。

Phase 9-3の設計内容は破棄せずDraftとして保持する。ただしPhase 9-2のGate解決・Controller受理前に`READY`、Backup Gate開始またはSource実装開始を主張しない。

## 7. Exact Next Action

```text
Phase 9-2の明示的Default-OFF Experimental Gateについて限定Reworkを設計・実装・検証する。
Controller受理後にだけPhase 9-2最小ClosureとPhase 9-3 READYを再判定する。
```

本AddendumはSource Mutation、Git操作、Phase 9-2 ClosureまたはPhase 9-3開始Authorityを生成しない。
