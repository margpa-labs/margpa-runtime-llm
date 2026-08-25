# Phase 6 Ninth Rework — Designer/Implementer Complete Candidate Handoff

```yaml
document_id: phase_6_codex_designer_implementer_ninth_rework_complete_candidate_handoff_20260824163433
status: complete_candidate
phase: phase_6
from: 設計者兼実装者役
to: プロジェクト責任者兼設計統括者役
created_at: 2026-08-24 16:34:33 JST
scope: ninth_rework_judge_evidence_publish_ownership_and_lifecycle
phase_closure_authority: false
```

## 1. Return Status

```text
Status             : COMPLETE_CANDIDATE
P6-RW8-CODEX-001   : CORRECTED
Publish Lifecycle  : CORRECTED
Open Critical      : 0 known
Open Major         : 0 known
Phase 6 Closure    : NOT CLAIMED
```

Ninth ReworkのCaller-owned Evidence Publish Arbitrationと追加Publish Lifecycle照合を完了した。Controller Independent Re-reviewへ返す。

## 2. Result Summary

- 同期ENFORCE Judge／Repair Workerから外部Recorder Commit Authorityを除去した。
- WorkerはTyped ResultとMemory-only Pending Evidenceを返した直後にModel leaseを解放する。
- Conversation Terminal OwnerだけがPending Evidenceをpublish/discardできる。判断はidempotentで、0.25秒等の時間切れによる正常Evidence消失はない。
- Deadline、Cancel、Replacement Final Rejection、Caller FailureはEvidence 0。Late Worker解放後も0を維持する。
- Authorized Evidence I/OはModel lease外のtracked Auxiliary Publisherで実行する。
- Recorder Block中でも次Main lease取得はPASS。ShutdownはPublisherをjoin対象として認識し、Block中`False`、解放後`True`へ収束する。
- OBSERVE exactly once、正常ENFORCE exactly once、Recording OFF Recorder Call 0を維持する。
- Publisher start/run failureはPresented Final／Last-resultを上書きせず、Compositionへ明示Failureを残す。

Detailed Recovery / Evidence:

`docs/project/phases/phase_6/history/index/phase_6_ninth_rework_complete_candidate_ja_20260824163433.md`

## 3. Final Validation

```text
Focused Backend : 65 passed
Mypy            : 443 source files / 0 errors
Ruff Format     : 443 files already formatted
Ruff Check      : PASS
Backend Full    : 1602 passed / 7 deselected
Frontend        : no change; Eighth 221-test PASS Evidence reused
```

全pytestにProject内Exact `--basetemp`を指定した。Real Model／Metal、User Browserは再活性化していない。

## 4. Changed Files / SHA-512

```text
05b322d2ced91b77d2cb472e0ceca7bd94589ddc07ab096d8dc55dfa5da6173359292b209ef0d3dd30a9110359502e8b24a17838781f39e2a3238533e2c9f6e1  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
6a49a6bb29f1825cec0e1b64434f932cfdeb68a1e5ff87d4601f0f99e2c638ee2f2a21cf64cb5fe3495845f9085cba54422faec92c5dd6806e088f08f0decc83  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
703c8503fe89839c442f00c710adcd04b34f8b090ed55e3cff0aef56fa4012c990f638981dca92df953a065c3fee60b2be56110b26f11d5e42ff6c2fa66d3482  src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py
d0ac190b0342e24048cd3fa55bb94f81321f5f4e33fbda6d766e2501e533fd7f9bca2d4e4d126fded8f17b89546d1e1ef808b88e6d4dc5d243541654cc44b2ab  tests/unit/bootstrap/test_judge_live_integration.py
0cc1cf9ff92f65e590dc13586b0a4ee30b8bcdefd4a91c350a0fb6bd13331bd5a65a4a323e230d7cb1b1ff32785e114966bcc1f7d82d58911cb7268acb23889b  tests/unit/conversation/test_conversation_generation_judge_hook.py
239446d592ebbb39590b975e2889b72f60b3a9a80f9d994f8cc213275b1775656abdfae49634f9a60bb649e1b6185013e7773613d902cf1eb7e9c1531e61e45f  tests/unit/inference/test_model_access_coordinator.py
```

## 5. Incident Accounting / Boundary

```text
Process Incident cumulative   : 3
Root-outside Incident cumulative: 2
P6-RW9-INC-001 Git Read       : 1 / retained / non-blocking
Git Mutation                  : 0
Post-resume Git Action        : 0
Root-outside Action           : 0
Provider Memory               : 0
User runtime_data             : 0
Network                       : 0
Model Artifact                : 0
Phase 6 Closure/Phase 7       : 0
```

## 6. Controller Review Request

次を独立照合してほしい。

1. WorkerがRecorderへ直接Commitせず、Pending Evidenceだけを返すこと。
2. 0.25秒超Terminal判断、Deadline、Cancel、Final RejectのEvidence件数。
3. Blocked PublisherがModel leaseを保持せず、Main取得を阻害しないこと。
4. Shutdownがblocked Publisherをfalse-cleanとしないこと。
5. Normal ENFORCE／OBSERVE exactly once、Recording OFF 0。
6. Exact Digests、Validation、Incident Accounting。

Controller判定までPhase 6 Closure、Phase 7、Roadmap、Git、Network、追加実装へ進まない。
