# Phase 6 Fifth Rework — Recovery Entry（Package C: Recording Path／Regression Repair 完了）

```yaml
document_id: phase_6_fifth_rework_package_c_recording_path_and_regression_repair
status: recovery_entry
phase: phase_6
package: package_c
role: Claude側設計統括者役
created_at: 2026-08-23 21:09:44 JST
governing_handoff: phase_6_codex_fifth_independent_review_rework_handoff_ja_20260823183203.md
previous_entry: phase_6_fifth_rework_package_b_deepseek_multiturn_ja_20260823205724.md
```

## Current Package／Work Unit

Package C（Recording Atomic Path／Regression Repair、対象P6-CODEX-038＋
P6-CODEX-039の実Qwen Test Failure部分）完了。Package Dへ進む直前。

## Last Completed Action

`tests/integration/llama_cpp/test_phase1b_runtime.py::
test_phase1b_production_runtime_load_generate_stream_cancel_and_unload`を
実測値に基づいて修正し、実Qwenで`1 passed`を確認。直後にFull Backend Test
（`tests/`全体、real-hardware Marker除く）1559 passed, 1 deselected
（Package B完了時点1556から、Recording Writer向け新規Fault Injection Test
3件分の増分）、`mypy src/ scripts/`エラー0を確認。

## Completed Findings

```text
P6-CODEX-038 CLOSED — LocalFilesystemRecordingWriter
  （src/margpa_runtime_llm/adapters/runtime_observability/
  local_filesystem_recording_writer.py）のTOCTOU残存を解消。

  従来の実装は、Symlink／Hardlink／Owner等の各Checkを`lstat()`等で
  LEXICAL PATHに対して行った後、Lock／Temp／Target／Rename／
  Directory-fsyncの各操作を別のSyscallで同じLEXICAL PATHを再解決して
  実行していた——Check完了からその後の実際の使用までの間に、別Process
  またはConcurrentなWriteがDirectory EntryをSymlink等へ差し替える
  Race Windowが構造的に残っていた。

  Fix: `_open_verified_base_dir_fd()`を新設し、Authorized
  `containment_root`から`base_dir`までを、`dir_fd`相対の
  `open(..., O_NOFOLLOW, dir_fd=parent)`を連鎖させる単一のWalkとして
  実装した——各Componentは「親の既に検証済みのfdに対して」作成
  （`os.mkdir(name, dir_fd=parent_fd)`、EEXIST許容）された直後に、
  同じ親fdに対して`O_NOFOLLOW`でOpenされる。LEXICAL PATHの再解決が
  一切発生しないため、CheckとUseの間に差し替えを行うRace自体が
  構造的に成立しない。取得した`base_dir`のfd（`base_fd`）は、この
  Writeの残り全て（`.write.lock`のOpen、一時File作成、既存Target
  Entryの`lstat`相当Check、Quota Scan用の`os.scandir(base_fd)`、
  Orphan一時File Prune、`os.rename(..., src_dir_fd=base_fd,
  dst_dir_fd=base_fd)`によるAtomic Replace、`os.fsync(base_fd)`に
  よるDirectory Durability）に一貫して束縛される。

  `os.replace()`は本Platform（macOS/Darwin）で`dir_fd`を受け付けない
  ため、`os.rename()`（`dir_fd`対応、かつPOSIX上は`rename()`と同じ
  Syscallで常にDestinationをAtomicに置換する——`os.replace`との
  意味的差はWindows限定）を直接使用した。

  containment_rootを指定しない呼び出し形（既存の限定的Semantics、
  base_dir自身のSymlink Checkのみで中間Componentは対象外）は、既存の
  documented Behaviorをそのまま維持しつつ、base_dir自身についても
  `O_NOFOLLOW` Openで同じCheck-and-Use一体化の恩恵を得るよう修正した。

  Deterministic Fault Injection Testを3件追加
  （tests/unit/runtime_observability/test_local_filesystem_recording_
  writer.py）:
    1. test_intermediate_component_swapped_to_symlink_between_create_
       and_open_is_rejected — `os.mkdir`をMonkeypatchし、中間Component
       作成直後にSymlinkへ差し替えるRaceを直接再現し、`O_NOFOLLOW`
       Openが依然としてFail-closedすることを確認（P6-CODEX-038が
       名指しした"Intermediate-swap-after-check"そのもの）。
    2. test_rename_failure_cleans_up_the_temp_file_and_raises_write_
       failure — Replace段階の失敗（`os.rename`）で一時Fileが残らず
       `RecordingWriteFailure`が発生することを確認。
    3. test_directory_fsync_failure_after_rename_raises_write_failure
       — Rename成功後のDirectory-fsync失敗が`RecordingWriteFailure`
       として表面化することを確認（Silent Successを許さない）。

  既存32 Testは全てPass（1件、Cross-process Lock Testの
  `_prune_orphan_temp_files`直接Monkeypatchが新Signature
  （`base_fd`引数を取るStaticmethod）に合わせて要修正だったため、
  Testのみ更新——Production Code側の意図的な仕様変更に伴う、機械的な
  Signature追従）。Total 35 Tests Pass。

P6-CODEX-039（実Qwen Test Failure部分）CLOSED —
  tests/integration/llama_cpp/test_phase1b_runtime.pyの
  STATUS Event Count Assertion（`== 1`）が、現在のSTATUS Vocabulary
  （`_events_with_summary()`が"preparing"／"guarding"／
  "summarizing_answer"の3件を発行する）に対して陳腐化していたことを
  Source Code読解で特定した。Exclude/Markではなく、実測されたStatus
  Sequence自体をAssertする形（`["preparing", "guarding",
  "summarizing_answer"]`）へ修正し、実Qwenで`1 passed`を確認した。
```

## Exact changed files（Package C、本Package全体での変更分）

```text
Modified:
  src/margpa_runtime_llm/adapters/runtime_observability/
    local_filesystem_recording_writer.py
  tests/unit/runtime_observability/test_local_filesystem_recording_writer.py
    （既存Test 1件のSignature追従修正＋新規Fault Injection Test 3件追加）
  tests/integration/llama_cpp/test_phase1b_runtime.py
    （STATUS Event Assertionを実測Vocabularyへ修正）

New: なし
Deleted: なし
```

## Executed Commands／Exit Codes／Test Counts

```text
python3 -m mypy src/margpa_runtime_llm/adapters/runtime_observability/
  local_filesystem_recording_writer.py
  → Success: no issues found（Exit 0）

python3 -m mypy src/ scripts/ tests/unit/runtime_observability/ \
  tests/integration/llama_cpp/test_deepseek_multiturn.py
  → 1 error（tests/unit/runtime_observability/test_local_filesystem_
  recording_writer.py:36、_envelope()ヘルパーのmetadata_fields型注釈に
  関する既存・無関係のPre-existing issue——`python3 -m mypy`（config
  files=["src","scripts","tests"]による全tests/対象実行）でも同種の
  Pre-existing issueが他4 File・計22件存在することを確認済み。いずれも
  本Rework／本Packageの変更に起因しない、以前のPhaseからの既存事項
  ——Package DのAcceptance再導出で正直に記録する）

python3 -m mypy src/ scripts/（Package A／B同様の既定Scope）
  → Success: no issues found in 279 source files（Exit 0）

python3 -m ruff format --diff <touched files>; ruff check <touched files>
  → All checks passed（Exit 0、複数回）

python3 -m pytest tests/unit/runtime_observability/
  test_local_filesystem_recording_writer.py -q
  → 35 passed（Exit 0、既存32＋新規3）

python3 -m pytest tests/integration/llama_cpp/test_phase1b_runtime.py \
  -q -m model_smoke（実Qwen）
  → 1 passed（9.73s、Exit 0——Package B時点の既知Failureを実際に解消）

python3 -m pytest tests/ -q --ignore=tests/integration/llama_cpp \
  --ignore=tests/integration/test_real_local_judge_smoke.py \
  --ignore=tests/integration/test_runtime_model_control_smoke.py
  → 1559 passed, 1 deselected（Exit 0、Package B完了時点1556から
  Fault Injection Test 3件分の増分、回帰なし）
```

## Active Process／Model Load／Scratch State

```text
Active Process: margpa_runtime_llm.entrypoints系のProcessは0件。
Model Load State: 実Qwen（test_phase1b_runtime.py）がTest Fixture管理下で
  Load／Unloadしたのみ。本Entry作成時点で永続Load Stateは無い。
Scratch State: 新規作成なし（本Packageの作業は既存Test Suite内で完結）。
```

## User runtime_data Contact Count

0。

## Root-outside／Git／Network／Provider Memory Action Count

0（Package C自身での新規発生なし。`git status`/`git log`/`git show`の
Read-only参照のみ実施——Working Tree・Index・Historyへの変更なし）。

## Artifact／Snapshot／DigestのCurrent State

```text
Qwen Artifact: main.qwen3-4b-q4-k-m、sha512=f182f1d4...（未変更、
  実Load/Unloadのみ発生）
DeepSeek Artifact: 本Package内での接触なし（未変更）
config/models/*.tomlは未変更。
```

## 未解決の既知Pre-existing Issue（本Packageのスコープ外、Package Dで正直に記録）

```text
`python3 -m mypy`（tests/を含む全Scope）で、本Rework・本Package以外の
以下4 Fileに計22件のPre-existing mypy Errorが存在することを確認した
（本Package Cの変更に起因しない、以前のPhaseからの既存事項）:
  tests/unit/runtime_observability/test_local_filesystem_recording_
    writer.py（1件、_envelope()ヘルパーの型注釈）
  tests/unit/bootstrap/test_repair_live_integration.py（5件）
  tests/unit/inference/test_model_access_coordinator.py（11件）
  tests/unit/bootstrap/test_judge_live_integration.py（3件）
Package A／B／Cはいずれも`mypy src/ scripts/`（Test除外）を自身の
Verification Scopeとして一貫して用いてきており、これはHandoff自体が
再定義していない既存Conventionである。Package DのAcceptance再導出・
最終Verificationで、このGapの存在と範囲を隠さず記録する
（Silent Carry-forwardではなく、明示的な既知事項として）。
```

## Open Findings（Severity／Current Impact）

```text
P6-CODEX-039 CRITICAL EVIDENCE／REQUIRED — 残る作業はAcceptance Matrix
  全ID再導出のみ（Package Dで対応）
P6-CODEX-040/P6-GOV-007 CRITICAL GOVERNANCE EVIDENCE／REQUIRED
  （Package Dで対応）
```

## Exact Next Action

Package D（Acceptance／Governance／Final Verification）を開始する:

```text
1. P6-CODEX-039残部: Phase 6 Acceptance Matrixの全ID（7件に限らず全件）
   をPASS／PARTIAL／NOT_EXECUTED／UNVERIFIED／DEFERRED／NOT_APPLICABLE
   ＋Evidence Source／Evidence Grade／Current Impactで個別に再導出する。
   本Reworkのsrc変更（chat_template.py、local_filesystem_recording_
   writer.py、model_access_coordinator.py、runtime_model_controller.py、
   runtime_governance.py、web_application.py、runtime_model_control.py）
   の影響を受ける既存PASSは再評価する。
2. 実Model／実BrowserでのSame-model Context Reloadを実施する。
3. P6-CODEX-040/P6-GOV-007: Fourth Rework HandoffのGovernance記録から
   「User Override」という Framing を訂正するAppend-only Correctionを
   history/operations/phase_6_gov007_*として作成する。Root-outside
   Incident自体はUnauthorizedのまま維持し、`/tmp/margpa_fourth_rework_
   preview_server.log`自体には一切接触しない（存在Checkも含めて）。
   自身のMemory File（feedback_dont_halt_on_minor_root_boundary_
   incidents.md）は削除せず、「今後の作業行動に関する指示としては有効」
   「特定のRoot-outside Incidentを遡って正当化するものではない」という
   区別を明示する形で扱う。
4. 最終Verification一式を実行する: Backend Full（`tests/`全体）、
   Focused Concurrency/Path（Runtime Switch、Recording Path Fault
   Injection）、Ruff、Mypy（`src/ scripts/`、および上記Pre-existing
   Test Gapの正直な記録）、Frontend（Typecheck/Lint/Test/Build）、
   実Qwen、実DeepSeek（Multi-turn Matrixの再実行を含めるか、Package B
   のEvidenceをそのまま引用するかは、当時からのSource変更有無で判断
   ——chat_template.pyはPackage B以降未変更のため、Package Bの実施済み
   Evidenceを引用可能）、実Browser（Runtime Switch、DeepSeek Multi-turn、
   Judge/Repair/Recording/Runtime State）。
5. Exact changed／new filesとCommands／Exit Codes／Evidence Grade／
   残存事項を記録する。
6. Package D完了Recovery Entryと、新しい
   handoffs/phase_6_claude_fifth_rework_complete_candidate_handoff_ja_
   <timestamp>.mdを作成する。Handoff §10 Return Contractが真に満たされて
   いる場合のみComplete Candidateとして提出し、満たされていない場合は
   STOPPED_SAFEで正確に報告する。
```

## Exact Resume Command／Resume手順

```text
1. 本Entry、phase_6_fifth_rework_package_b_deepseek_multiturn_ja_
   20260823205724.md、phase_6_fifth_rework_package_b_pre_model_run_ja_
   20260823204226.md、phase_6_fifth_rework_package_a_runtime_switch_
   integrity_ja_20260823202658.mdを読む。
2. `git status --porcelain`で本Entry作成時点からの増分Diffを確認する
   （local_filesystem_recording_writer.py修正、対応Test修正・追加、
   test_phase1b_runtime.py修正以外に予期しない変更が無いことを確認）。
3. 上記「Exact Next Action」からPackage Dを開始する。
```
