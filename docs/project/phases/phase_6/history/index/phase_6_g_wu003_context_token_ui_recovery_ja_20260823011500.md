# Phase 6-G-WU-003 Context／Token Control UI Recovery Entry（Real Browser Apply検証済み）

```yaml
document_id: phase_6_g_wu003_context_token_ui_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_g
work_unit: p6_g_wu003_complete
role: Claude側設計統括者役
long_running_mode_active: true
created_at: 2026-08-23 01:15:00 JST
```

## Exact Mutation

```text
Modified:
  src/margpa_runtime_llm/web/runtime_model_control_routes.py
    （RuntimeModelStatusResponseへdigest_sha512追加——CASにはSnapshot全体の
      digest_sha512を使う必要があり、main_model.artifact_digestとは別物と判明、
      Route自体に欠落していたBugをこのWUで検出・修正）
    （POST /context、POST /max-new-tokens 追加。RuntimeModelController.
      request_context_change()／set_max_new_tokens()をasyncio.to_threadで実行）
  src/margpa_runtime_llm/web/app.py
    （RuntimeModelControlWebError、6種Domain Error（RevisionConflict／
      ContextLimitExceeded／MaxNewTokensExceeded／Busy／LoadFailure／
      RollbackFailure）のException Handler追加。409／422／502/404に正確Map）
  tests/integration/web/test_runtime_model_control_public_basic_call0.py
    （digest_sha512フィールド追加に伴うExpected Dict更新）
  frontend/src/types.ts（RuntimeModelStatus.digest_sha512追加）
  frontend/src/api/client.ts（applyRuntimeModelContext／applyRuntimeModelMaxNewTokens追加）
  frontend/src/i18n/translations.ts（runtimeModelApply／ApplySuccess／ApplyFailed、JA／EN）
  frontend/src/components/RuntimeModelStatusPanel.tsx
    （Context Size／Max New Tokens各々に number input + Apply Button追加、
      syncedDigestパターンでApply成功後の値を再同期）
Created:
  tests/integration/web/test_runtime_model_control_mutation_routes.py（6 Test）
  （Backend側Fakeで発見：RuntimeModelController.request_context_change()は
    Definition Resolverを実際に呼ぶため、Status専用のFakeDefinitionResolver
    （NotImplementedError）では動かない。Mutation用に実装済みFakeを新規に用意）
```

## Real Browser検証（実施済み、model_smoke非該当）

```text
検証方法: tests/integration/web/test_runtime_model_control_mutation_routes.py の
          bound_runtime()（実装済みFake Backend）でServer起動、実Browserで
          Settings→Advanced ModeからContext Size 4096→8192、Max New Tokens
          2048→1024を実際に投入・Apply。
確認結果: Network Request実測でPOST /context・/max-new-tokens 両方200 OK、
          UI側もRevision 0→1→2、値の表示更新、「Applied.」表示を実際に確認。
          先にFake Backend未実装Loadで意図的に500になるCaseも確認済み
          （「Failed to apply.」を正しく表示、Console Error以外のCrash 0）。
Server後処理: Preview ServerとBrowser Tabを終了・破棄。
```

## Validation

```text
Backend New Test    : 6 passed（mutation routes：成功／Stale CAS 409／Limit 422×2／Unbound 404）
Frontend New Test   : 2 passed（Apply成功／Apply失敗）
Full Backend        : 1388 passed／3 deselected（回帰0）
Full Frontend       : 181 passed／21 files（回帰0）
Ruff／Mypy／ESLint／Typecheck: 全てClean
Frontend Build      : Success
```

## Next Exact Route

Phase 6-G-WU-004（Judge／Repair／Recording UI）、WU-005（UI Naming／Legacy Cleanup、
既存Phase Suffix除去）、WU-006（Browser Sync／Accessibility）へ進む。
