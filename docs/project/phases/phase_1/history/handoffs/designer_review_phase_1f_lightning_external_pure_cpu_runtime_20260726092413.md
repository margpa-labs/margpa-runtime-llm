# Phase 1-F Lightning External Pure CPU Runtime 設計Review

- 文書ID: `designer_review_phase_1f_lightning_external_pure_cpu_runtime`
- 状態: `external_runtime_accepted_full_suite_follow_up_required`
- 作成日時: `2026-07-26 09:24:13 JST`
- 更新日時: `2026-07-26 09:24:13 JST`
- Snapshot: `20260726092413`
- 作成担当: 設計者役担当Task
- 対象: ユーザー実行Lightning Pure CPU Environment Reconstruction／Native Acceptance
- Current Manual: [lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md](../user_manual/lightning_pure_cpu_actual_environment_reconstruction_manual_20260726092413.md)
- Test-only Handoff: [designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md](designer_handoff_phase_1f_lightning_test_isolation_follow_up_20260726092413.md)
- Previous Repository Review: [designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md](designer_review_phase_1f_pure_cpu_acceptance_correction_20260725214428.md)
- 正本言語: 日本語
- supersedes: なし

## 1. Conclusion

Lightning Linux x86_64 Pure CPU External RuntimeをAcceptedとする。

Full Repository Testは264件Pass、2件Test Isolation Failureであり、Full Suite GreenはPendingとする。

```text
External Pure CPU Runtime : ACCEPTED
Environment Verification : PASS
Native Acceptance        : PASS
Required Checks          : ALL TRUE
Static Verification      : PASS
Full Repository Suite    : FOLLOW-UP REQUIRED
Top-level Phase 1        : NOT DECLARED
```

## 2. Evidence Source

本Reviewはユーザー実行によるLightning Terminal出力と、Accepted Repository Contractを照合した。

外部Environmentへ本Taskから接続、変更または再実行していない。

## 3. Environment Evidence

```text
OS                    : Ubuntu Linux
Architecture          : x86_64
Execution Environment : container
Python                : 3.12.11
uv                    : 0.11.29／Project-isolated
Project Environment   : margpa-runtime-llm/.venv
Backend               : llama-cpp-python 0.3.34／Pure CPU
Model Root            : /teamspace/studios/this_studio/models
```

`uv` Binary SHA-512はAccepted値と一致した。

## 4. Runtime Evidence

Environment Verificationは成功した。

Bounded Native Acceptance：

```text
all_required_checks_passed : true
profile_key                : external.lightning-linux-x86_64.cpu-native
```

Pure CPU Profile Contract：

```text
Compute          : cpu
Acceleration API : none
GPU Offload      : false
Build Variant    : cpu
Fallback         : deny
```

実Model ArtifactはRegistry Relative Layoutで解決され、存在確認が成功した。

## 5. Static Verification

```text
Ruff Check  : PASS
Ruff Format : PASS／95 files
Mypy        : PASS／95 source files
```

## 6. Repository Test Progression

初回：

```text
258 passed
8 failed
1 skipped
3 deselected
```

内訳：

- UploadでShell実行権限喪失：5
- `.python-version`除外：1
- Platform Test Isolation：2

File Mode、MetadataおよびModel Root Environment漏出を解消後：

```text
264 passed
2 failed
1 skipped
3 deselected
```

## 7. Remaining Findings

### Finding A：Platform Execution Environment Isolation

2件のUnit Testが、OS／ArchitectureをMockしながら、Execution Environmentだけを実Lightning Containerから検出する。

Severity：

```text
Production Runtime : none
External Acceptance: non-blocking
Full Suite Green   : blocking
```

Required Action：

```text
Testへraw_execution_environment="native"を明示する。
```

### Finding B：Model Root Environment Isolation

`MARGPA_MODEL_ROOT`がTemporary Model Path Testへ漏出すると、Setupが設計どおりMismatchを拒否する。

Current user-run workaround：

```text
pytest ProcessからMARGPA_MODEL_ROOTとMARGPA_PROFILEを除外する。
```

恒久対応：

```text
Test Subprocess EnvironmentをTest内で明示的にSanitizeする。
```

## 8. Accepted Boundary

Acceptedとするもの：

- Lightning Pure CPU Environment再構築
- Pure CPU Backend
- Model Root解決
- Artifact Load
- Runtime／Profile一致
- Bounded Native Acceptance
- Static Verification

未Accepted：

- Cross-platform Full Suite Green
- Lightning Web Preview手動受入
- Top-level Phase 1完了
- Backup
- Phase 1-ex開始

## 9. Re-execution Scope

Follow-upはTest-only変更である。

次を再実行する。

- Mac Full Suite
- Lightning Full Suite
- Ruff
- Mypy

Production Runtime、Profile、SetupまたはAcceptance Scriptを変更しない限り、高コストなBounded Native Acceptanceの再実行は不要である。

## 10. Final Decision

```text
Phase 1-F Repository Pure CPU Follow-up : ACCEPTED
Lightning External Pure CPU Runtime     : ACCEPTED
Cross-platform Full Suite               : CHANGES REQUESTED／TEST ONLY
```

