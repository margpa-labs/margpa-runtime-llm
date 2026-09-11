# Phase 9-2 Explicit Default-OFF Experiment Runtime Gate — Controller独立Review受理／最小Closure Receipt

```yaml
document_id: phase_9_2_explicit_default_off_experiment_runtime_gate_controller_independent_review_acceptance_and_minimal_closure_receipt_20260911163201
document_state: accepted_append_only_event
phase: phase_9
program: phase_9_2
recorded_at: 2026-09-11 16:32:01 JST
language: ja
authority_owner: Nazuna Research
decision_authority: user
controller_provider: codex
controller_task_id: 019f739b-8a21-7592-95cc-c83c9c08e5f6
executor_provider: claude_code
executor_session_id: local_d7f17853-1ab4-45aa-bacd-b9d6db898b65
phase_9_2_status: complete_user_accepted_minimal_closure
phase_9_3_status: design_frozen_ready_user_backup_pending
additional_user_real_hardware_check_required_for_phase_9_2: false
git_write_performed: false
```

## 1. 結論

Phase 9-2 Explicit Default-OFF Experiment Runtime Gateの実装とClaude差分継続ReturnをCodex Controllerが独立再検証した。Confirmed Blocker／Majorはなく、早期Closure訂正で残した唯一の限定Reworkは解決した。

Phase 9-2はHeadless Experiment／Evaluation／Multi-Governance Coreを成立範囲として`COMPLETE／USER ACCEPTED／MINIMAL CLOSURE`とする。通常UIのExperiment WorkspaceはPhase 11以降へ延期したまま、現在の通常UI入口は非表示である。

Phase 9-3の設計Draftは依存解決により`FROZEN／READY／USER BACKUP PENDING`へ昇格する。Backup完了とユーザーの明示開始まではSource実装へ進まない。

## 2. 受理したRuntime Contract

- `--phase-9-experiment-runtime`は明示Opt-inで、既定値はOFF。
- Conversation PersistenceはStorage Prerequisiteであり、Experiment Authorityではない。
- Flag省略時はExperiment Service、Run Worker、Production Turn Adapter、Live Configuration ReaderおよびConfiguration Leaseを構築しない。
- Default OFF時はExperiment Actor Call、Background Worker、Mutation、EvidenceおよびLease保持が0。
- Default OFF時はExperimentを理由としてSettings変更を409拒否しない。
- Experiment Plan／Run等はDisabled Contractへ収束し、見えない実行を開始できない。
- Explicit ON時はLocal／Loopback／Authentication Disabled／Conversation Persistenceを要求する。
- Direct Runtime FactoryでExperiment構成物がBoundされた場合も、Non-local Access PolicyではRequest受付前にFail-closedする。
- Explicit ONでは既存のPlan→Run→Evidence→Comparison→Restart Readを維持する。
- 通常UI入口は再表示しない。

## 3. Claude Return

Final Exact Return:

`docs/project/phases/phase_9/handoffs/phase_9_claude_phase_9_2_explicit_default_off_experiment_runtime_gate_final_exact_return_ja_20260911162216.md`

SHA-512:

```text
7a7f4ede207b15b04743ba3317624553e1946e9ed8b610a3b4ef90c02b6237e89388bde29710ee872eb7098384c710f895abada190f748517b95a947b89f9ce4
```

Final Recovery:

`docs/project/phases/phase_9/history/index/phase_9_2_explicit_default_off_experiment_runtime_gate_final_recovery_ja_20260911162216.md`

SHA-512:

```text
0fd21ba049bc5110d5b9864d3aebb9b213f06f0247ff3649b2111af5e48f016a0c7e1f4cd491f7fa5dc7122e737bcdfdba83daec4419b8991ffa6438bba7534b
```

ClaudeはCL-GATE-01〜06を完了し、Relevant 72件、Sabotage、Ruff、Mypy新規Error 0、Review A／Bを成立させた。Mypy実行中に見つけたChanged Test内の型変数衝突1件は局所修正済みで、残件へ持ち越していない。

## 4. Controller Independent Review

### Review C1 — Identity／Claim／Scope

- Return／RecoveryのIdentity、Task／Session ID、Maximum Claim、Changed 8 Pathおよび禁止事項を照合した。
- ReturnはPhase 9-2 ClosureやPhase 9-3開始を自己承認していない。
- Gate実装以外の既存Dirty Diffを今回の成果として再分類していない。

結果: PASS。

### Review C2 — Default-OFF／Enabled Top-level再実行

Controller環境では`uv` CacheがSandbox外にあり初回CommandがProduct Code実行前に失敗した。この事象をProduct Failureに分類せず、Projectの既存`.venv`から同一Testを実行した。

```text
./.venv/bin/python -m pytest -q \
  tests/unit/web/test_web_cli.py \
  tests/integration/web/test_experiment_routes.py

72 passed in 3.56s
```

さらに、Real Modelを除外したTop-level Smokeを再実行した。

```text
./.venv/bin/python -m pytest -q -m 'not model_smoke' \
  tests/integration/test_real_top_level_experiment_production_gate_smoke.py

6 passed, 3 deselected in 0.57s
```

結果: PASS。

### Review C3 — API Surface／Static Validation

`experiment_routes.py`の全公開Endpointを列挙し、Preset Discovery以外はService／Worker不在でDisabled Contractへ収束することを確認した。Default OFFで実Workへ到達する迂回Endpointは確認されなかった。

Changed 8 PathへControllerからRuffとFocused Mypyを実行した。

```text
Ruff: All checks passed!
Mypy: Success: no issues found in 8 source files
git diff --check: PASS
```

結果: PASS。

## 5. User Manual Disposition

ユーザーは2026-09-10に、通常UIからExperiment入口が非表示であることを実Browserで確認済みである。今回の残件はBackendのDefault-OFF Runtime Gateであり、機械検証で確認可能な範囲である。

Real Model、Browser、ExperimentPanel強制表示または同じUI非表示確認の反復はPhase 9-2 Closureへ追加しない。追加User Manualは不要である。

## 6. 早期Closure訂正との関係

2026-09-10の早期Claim訂正は正当だった。UI入口非表示だけではBackend Runtime Gateがなく、見えないAPI RunとSettings Lease拒否の可能性が残っていた。

今回、その不足をDefault-OFF Gate、Disabled API Contract、Settings非409、Explicit ON RegressionおよびDirect Factory Fail-closedとして実装・検証したため、訂正前Receiptを復活させるのではなく、本Receiptを新しい受理EventとしてAppend-onlyで追加する。

## 7. 残件

- Phase 9-2 Blocker／Major: なし。
- Phase 9-2追加User Manual: なし。
- Repository全体の既存Mypy 43件: 今回Changed Path外の既存Baselineとして別Scopeを維持。
- Experiment Workspace UI: Phase 11以降の再設計対象として延期を維持。

## 8. Exact Next Action

```text
1. UserがPhase 9-3 READY時点のCurrent Working Tree Backupを取得する。
2. UserがPhase 9-3 Source実装開始を明示する。
3. それまではPhase 9-3 Source Mutation、Git操作または追加実機試験へ進まない。
```

本ReceiptはPhase 9-2の限定最小ClosureとPhase 9-3 READYへの昇格を記録する。Phase 9-3 Source実装、Git、Networkまたは外部ActionのAuthorityは生成しない。
