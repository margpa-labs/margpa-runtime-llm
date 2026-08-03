# Phase 1-F Lightning Full Suite Revalidation 設計Review

- 文書ID: `designer_review_phase_1f_lightning_full_suite_revalidation`
- 状態: `accepted_full_suite_green_web_acceptance_pending`
- 作成日時: `2026-07-26 09:42:41 JST`
- 更新日時: `2026-07-26 09:42:41 JST`
- Snapshot: `20260726094241`
- 作成担当: 設計者役担当Task
- 対象Review: [designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md](designer_review_phase_1f_lightning_test_isolation_follow_up_20260726093437.md)
- External Runtime Review: [designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md](designer_review_phase_1f_lightning_external_pure_cpu_runtime_20260726092413.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Lightning Linux x86_64 ContainerでのTest Isolation RevalidationをAcceptedとする。

```text
Targeted Test       : 41 passed
Full Suite          : 266 passed
Expected Skip       : 1
Expected Deselect   : 3
Failure             : 0
Full Suite          : GREEN
```

## 2. User-run Evidence

Targeted：

```text
41 passed in 0.70s
```

Full Suite：

```text
266 passed, 1 skipped, 3 deselected in 1.77s
```

Skip対象：

```text
tests/integration/test_llama_cpp_metal.py
```

Lightning Linux x86_64はApple Siliconではないため、このSkipは正常である。

## 3. Cross-platform Result

```text
Mac Full Suite       : 267 passed／3 deselected
Lightning Full Suite : 266 passed／1 skipped／3 deselected
```

Platform Testは実Container Markerから分離され、Temporary Model Path TestはShellの`MARGPA_MODEL_ROOT`から分離された。

## 4. Runtime Result

前回のEvidenceを維持する。

```text
Environment Verification       : PASS
External Pure CPU Runtime      : ACCEPTED
all_required_checks_passed     : true
Static Verification            : PASS
Cross-platform Full Suite      : GREEN
```

Test-only変更であり、Native Acceptanceの再実行は不要である。

## 5. Remaining Required Gate

Phase 1-F／Phase 1 Web Previewに関して、次の必須GateはLightning Web実起動と手動確認である。

- Pure CPU ProfileでWeb起動
- Basic認証
- `/healthz`
- CredentialなしRoot拒否
- Lightning Port公開
- Browser表示
- 短い日本語生成
- 停止
- 新規Chat
- Shutdown

## 6. Current Decision

```text
External Pure CPU Runtime  : ACCEPTED
Mac Full Suite             : GREEN
Lightning Full Suite       : GREEN
Lightning Web Acceptance   : PENDING
Top-level Phase 1          : NOT DECLARED
```

