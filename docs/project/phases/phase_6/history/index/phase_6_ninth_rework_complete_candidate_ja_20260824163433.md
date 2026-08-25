# Phase 6 Ninth Rework — Complete Candidate Recovery Entry

```yaml
document_id: phase_6_ninth_rework_complete_candidate_20260824163433
status: complete_candidate
phase: phase_6
work: judge_evidence_publish_ownership_and_lifecycle
created_at: 2026-08-24 16:34:33 JST
controller_review_required: true
phase_closure_claimed: false
```

## 1. Authority

```text
Initial Exact Handoff:
  docs/project/phases/phase_6/handoffs/
  phase_6_codex_controller_ninth_rework_exact_handoff_ja_20260824160222.md
  SHA-512: 07bc124193f88af7e5227038484028086998339dd492040f38cbb60c3d68fe6b004a05e7532c75cb9c9e9c9d323fd0e5cae2d54e1cadbf50b95feb8f618e09fc

Publish Lifecycle Resume Authority:
  docs/project/phases/phase_6/handoffs/
  phase_6_codex_controller_ninth_rework_publish_lifecycle_resume_authority_ja_20260824162427.md
  SHA-512: 2def544e8b76492f32ac463fbb80db8e351ac1c25e29d9e2e6cc297bd28cd47ecf0c89bdd3bce3b16714e4a01d0b67c7de3e8ef5ce4d5685a6e2f358954a7072
```

## 2. Completion State

`P6-RW8-CODEX-001`のCheck-then-Act TOCTOUを除去した。同期ENFORCEのJudge／Repair Model Workerは、Typed ResultとMemory-only Pending Evidenceだけを返し、外部Recorderを呼ばない。Conversation Terminal OwnerがCompletedを採用した場合だけ、idempotent Arbitrationを通じてEvidence Publicationを承認する。Deadline、Cancel、Replacement Final Rejection、Caller FailureはPendingを永久破棄する。

Evidence I/Oは`ModelAccessCoordinator.start_auxiliary()`で開始するtracked Auxiliary Taskへ分離した。Auxiliary TaskはCoordinatorのShutdown Lifecycleに属するが、`_current_kind` Model leaseには参加しない。このため、RecorderがBlockしても次Main Turnは即時にModel leaseを取得できる。ShutdownはBlock中のPublisherをcleanと誤報せず`False`へ収束し、Recorder解放後の再Shutdownでjoin済み`True`へ収束する。

旧0.25秒Arbitration Timeoutは延長ではなく除去した。Pending EvidenceはTerminal Ownerの判断までMemory上で保持され、Judge Model Workerは判断を待たずModel leaseを解放する。Terminal判断が0.25秒を超えても正常ENFORCE Evidenceはexactly onceである。

OBSERVEも外部RecorderをModel Workerから分離し、tracked Auxiliary Publisher登録後にJudge terminalをprojectionする。Recording OFFはPending自体を生成せずRecorder Call 0を維持する。Publisher start/run failureはPresented FinalやJudge Resultを改変せず、`JudgeGovernanceComposition.evidence_publication_failure()`へ明示的に記録する。

## 3. Adversarial Regression

```text
Worker before Terminal authorization       : Recorder entry 0
Terminal decision delayed > 0.25 seconds   : ENFORCE Evidence exactly once
Duplicate Terminal authorization           : Evidence exactly once
User Cancel before authorization            : Evidence 0
Judge Deadline + Late Worker release        : Evidence 0 / deadline_exceeded unchanged
Replacement Final rejection                 : Evidence 0
Normal ENFORCE                              : Evidence exactly once
OBSERVE                                     : Evidence exactly once
Recording OFF                               : Recorder Call 0
Recorder blocked after authorization        : Main lease acquisition PASS
Recorder blocked during Shutdown            : false-clean rejected / False
Recorder released then Shutdown retry       : tracked join / True
Unexpected caller-side exit                 : events() finally discards Pending
```

Controllerの旧Adversarial Reproductionで成立していた「同期Judge WorkerがRecorder入口へ先に入り、その後DeadlineがTerminalを奪う」前提は構造的に成立しない。RecorderはTerminal authorization前に呼ばれず、authorization後もModel Workerではなくtracked Auxiliary Publisherだけが呼ぶ。

## 4. Validation

全pytestは次のProject内Exact Basetempを使用した。

```text
<Root>/.venv/.t/phase_6_ninth_rework_20260824160541/pytest
```

Final Result:

```text
Focused Judge/Conversation/Coordinator : 65 passed in 2.02s
Canonical Mypy                         : 443 source files / 0 errors
Ruff Format Check                      : 443 files already formatted
Ruff Check                             : PASS
Backend Full                           : 1602 passed / 7 deselected in 65.55s
Frontend                               : no change; Eighth PASS Evidence reused
  Typecheck                            : PASS
  Lint                                 : PASS
  Test                                 : 24 files / 221 passed
  Production Build                     : PASS / 48 modules transformed
```

Intermediate Finding:

```text
Backend Full attempt 1 : 1 failed / 1601 passed / 7 deselected
Cause                  : OBSERVE terminal projection was visible immediately
                         before Auxiliary Publisher registration.
Correction             : register tracked Publisher before terminal projection;
                         Recorder I/O remains asynchronous and lease-free.
Final revalidation     : all PASS as above.
```

## 5. Exact Changed Files / SHA-512

```text
05b322d2ced91b77d2cb472e0ceca7bd94589ddc07ab096d8dc55dfa5da6173359292b209ef0d3dd30a9110359502e8b24a17838781f39e2a3238533e2c9f6e1  src/margpa_runtime_llm/bootstrap/judge_live_integration.py
6a49a6bb29f1825cec0e1b64434f932cfdeb68a1e5ff87d4601f0f99e2c638ee2f2a21cf64cb5fe3495845f9085cba54422faec92c5dd6806e088f08f0decc83  src/margpa_runtime_llm/modules/conversation/application/conversation_generation.py
703c8503fe89839c442f00c710adcd04b34f8b090ed55e3cff0aef56fa4012c990f638981dca92df953a065c3fee60b2be56110b26f11d5e42ff6c2fa66d3482  src/margpa_runtime_llm/modules/inference/application/model_access_coordinator.py
d0ac190b0342e24048cd3fa55bb94f81321f5f4e33fbda6d766e2501e533fd7f9bca2d4e4d126fded8f17b89546d1e1ef808b88e6d4dc5d243541654cc44b2ab  tests/unit/bootstrap/test_judge_live_integration.py
0cc1cf9ff92f65e590dc13586b0a4ee30b8bcdefd4a91c350a0fb6bd13331bd5a65a4a323e230d7cb1b1ff32785e114966bcc1f7d82d58911cb7268acb23889b  tests/unit/conversation/test_conversation_generation_judge_hook.py
239446d592ebbb39590b975e2889b72f60b3a9a80f9d994f8cc213275b1775656abdfae49634f9a60bb649e1b6185013e7773613d902cf1eb7e9c1531e61e45f  tests/unit/inference/test_model_access_coordinator.py
```

## 6. Incident / Mutation Boundary

```text
P6-RW7-INC-001                                  : Historical / retained
P6-RW8-INC-001                                  : Historical / retained
P6-RW9-INC-001 Unauthorized Git Read            : RECORDED / NON-BLOCKING
Phase 6 cumulative known Process Incidents      : 3
Phase 6 cumulative known Root-outside Incidents : 2
Ninth cumulative Unauthorized Git Read          : 1
Ninth Git Mutation                              : 0
Resume Cycle Git Action after Authority          : 0
Ninth Root-outside Action                        : 0
Provider Memory Action                           : 0
User runtime_data Action                         : 0
Network Action                                   : 0
Model Artifact Action                            : 0
Frontend Mutation                                : 0
Phase 6 Closure / Phase 7 / Roadmap Action       : 0
```

## 7. Review Boundary

```text
Open Critical                     : 0 known
Open Major                        : 0 known
Real Model / Metal Validation     : NOT EXECUTED / User Gate retained
User Browser Acceptance           : NOT EXECUTED / Gate retained
Phase 6 Closure                   : NOT CLAIMED
Next Action                       : Controller Independent Re-review
```
