# Phase 6-0 Entry／As-built Reconciliation／Exact Freeze Recovery Entry

```yaml
document_id: phase_6_0_entry_reconciliation_and_freeze_recovery
status: current_recovery_entry
phase: phase_6
subphase: phase_6_0
work_unit: p6_0_wu_004_complete
role: Claude側設計統括者役
provider: claude_code
completion_line: phase_6_i_complete_candidate
long_running_mode_active: true
created_at: 2026-08-22 21:45:50 JST
user_start_declared_at: 2026-08-22（本チャットにて明示宣言「Phase 6を開始する。」）
```

Long期戦Mode下のLightweight Recovery Entry（Companion第4.1節適用）。定型§0.0 Boilerplateは省略。Frozen Core 8文書（phase_index／requirements／architecture／adr／governance／execution_plan／acceptance_matrix／claude_execution_handoff）は本Entryで一切変更していない。Automation Control State（`ARMED_NOT_ON`→`ON`）とUser Startの事実は、本History Entryにのみ記録し、Frozen Core／Phase Index本体へは直書きしない。

## Current State

```text
Accepted Predecessor  : Activation Preflight／ARMED Receipt（20260822212732）PASS
User Start            : 宣言済み（本チャット、2026-08-22）
Automation Control    : ARMED_NOT_ON → ON（本Entry時点でOperational Factとして記録）
Current WU            : P6-0-WU-001〜004 完了 → 次はP6-A-WU-001
Governance Runtime Mode: 未変更（Phase 5 Acceptance時点の設定を維持）
```

## P6-0-WU-001：Authority／Recovery Preflight（PASS）

Mandatory Reading Order 20項目（うちItem 20はResolved Target先読み禁止のため意図的に本WU-003まで留保）、Authorized Root（`git rev-parse --show-toplevel`一致、branch=`main`）、Read-only Git Current Diff、Phase 5 Technical／Mac Acceptance（`COMPLETE／ACCEPTED／CLOSED`）、Automation State（ARMED確認）、Compaction Recovery（Hash Tracker 0 success／2 failure、技術継続性はCycle 2でSUCCESS）、禁止Scope（Git Index／Ref／Worktree Mutation不可）を確認済み。本WU中もGit Mutationは0。

## P6-0-WU-002：Phase 4／5 As-built Reconciliation（PASS、Baseline確定）

```text
Backend Full Test   : 1236 passed／3 deselected（62.34s）
                      直近Phase 5 Fourth Rework確定値1234 passed＋新設2件（Malformed Provider Return
                      Decoder Fail-closed Test）= 1236で一致、Drift 0。
Frontend Test        : 175 passed（20 files、3.31s）
Ruff (src tests)     : All checks passed
Mypy (src)           : Success — 205 source files
```

Main Runtime Governance、Guardrail Governance、Policy、Authority、Configuration Control、Streaming、Persistence、RAGおよびUIのSource／Testは現行Repositoryと完全整合。回帰0。

## P6-0-WU-003：Model／Runtime／Resource Reconciliation（PASS）

```text
Qwen Current Route      : main.qwen3-4b-q4-k-m（config/application.toml selected_model一致）
models Symlink Logical  : margpa-runtime-llm/models
models Symlink Resolved : /Users/Nazuna Research/models/margpa-runtime-llm/models
                          （`readlink -f models`実測、Exact Model Authority Receipt §2と完全一致）
DeepSeek Canonical Snapshot : Presence未再確認（Full Digest Revalidationは
                          Receipt §4.2の通りP6-A-WU-001 Canonical Snapshot Revalidationへ委譲。
                          本WUではResolved Target内Deepseek Subtreeへの新規Readは実施していない）
llama.cpp Toolchain     : llama-cpp-python==0.3.34（project .venv、pyproject.toml記載と一致）
                          convert_hf_to_gguf.py 確認（/opt/homebrew/bin、Homebrew提供）
Config Registry         : config/models/qwen3_4b_q4_k_m.toml（単一登録、DeepSeek未登録＝As-built通り）
Disk Available          : 84Gi（`df -h /`実測。Preflight Receipt記載値「約84.0 GiB」と一致、Drift 0）
Physical Memory         : 17,179,869,184 bytes（16 GiB、Receipt値と一致）
```

Symlink・Disk・Memoryのいずれも前回Receipt記録値からのDriftは検出されなかった。DeepSeek Canonical Snapshotの内容そのもの（Exact Commit／Manifest／Digest）はP6-A-WU-001で初めて読む。

## P6-0-WU-004：Exact Mutation／Test／Rollback Freeze

### 本Freeze自体のExact Mutation

```text
Created:
  docs/project/phases/phase_6/history/index/phase_6_0_entry_reconciliation_and_freeze_recovery_ja_20260822214550.md
Modified: なし
Git Mutation        : 0
Root外Action         : 0（Resolved Target内容Readは`readlink`によるTarget文字列確認のみ、
                        Subtree内Fileはunopened）
```

### Path Class Freeze（Phase 6-A以降で使用予定のCandidate Write Class）

```text
models/main/deepseek-r1-0528-qwen3-8b/gguf/**（Derived、新規作成のみ）
models/main/deepseek-r1-0528-qwen3-8b/manifests/**（新規作成のみ）
models/main/deepseek-r1-0528-qwen3-8b/conversion_work/**（新規作成のみ、Intermediate無断削除禁止）
config/models/**（DeepSeek Candidate定義追加時）
src/margpa_runtime_llm/modules/runtime_model／（後続Phase 6-B、6-Aでは通常未使用）
docs/project/phases/phase_6/history/**（Append-only）
```

Qwen Artifact、DeepSeek huggingface Canonical Snapshot本体、Frozen Core 8文書はWrite対象に含めない。

## Test Command Freeze

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check .
.venv/bin/python -m mypy src
npm --prefix frontend test -- --run
npm --prefix frontend run build
```

## Forbidden Actions（変更なし）

Handoff第9節Stop Conditions、Governance許可範囲、Exact Model Authority Receipt §6 Explicit Non-authorityのまま。Qwen／DeepSeek Canonical Artifactの変更・削除、Sibling Model／親Directory／V4接触、Network Download、Git Mutationは引き続き0。

## Next Exact Route

P6-A-WU-001（Canonical Snapshot Revalidation）へ進む。Exact Commit、Manifest、Missing File、Size、Source Digest EvidenceおよびLicenseを再検証し、全巨大Weight Digest再計算のCostと必要性を区別する。
