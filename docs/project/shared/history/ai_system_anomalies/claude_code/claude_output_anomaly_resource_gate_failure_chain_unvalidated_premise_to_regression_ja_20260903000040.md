# Observation Record — Resource Gate Failure Chain: Unvalidated Causal Premise to Confirmed Regression

```yaml
document_id: claude_output_anomaly_resource_gate_failure_chain_unvalidated_premise_to_regression_20260903000040
status: observation_record
category: failure_chain
phase: phase_9
subphase: phase_9_1_package_2
from: Claude Code
to: Project Controller / User
role: designer_implementer
created_at: 2026-09-03 00:00:40 JST
language: ja_with_structured_english_terms
authorization: |
  Project Controller / User instruction (2026-09-02/03): an explicit, formally
  specified request to record the full sequence below as a single Failure
  Chain — not compressed into "a Resource Gate bug" — separating confirmed
  fact from observation, hypothesis, inference, and unconfirmed matter;
  prohibiting the fallacy "rejected/weakened hypothesis == alternative
  hypothesis proven"; requiring the generalization "Protective Control must
  not be promoted from an unverified causal hypothesis"; requiring the
  3-Gate Done criteria, "Observation != Persistent Evidence", expanded
  Review Scope, and "Human decision required != Immediate human
  interruption required" to be recorded as formal corrective items; declining
  to record the Human-side hypothesis as an established Failure (real-machine
  results did not support it); prohibiting any unilateral Revert/redesign
  decision inside this Record; requiring neutral, non-conversational register
  throughout; and prohibiting both minimization of Claude-unfavorable
  content and overstatement of unconfirmed content. A follow-up instruction
  additionally required this Record to state the fact that this entire
  Failure Chain occurred during a period in which Codex (the project's
  Designer/Controller role) was not available to review the design decision
  at its origin.
created: Claude Code
```

## 0. Positioning

This Record consolidates and supersedes, in scope and rigor, the partial accounts given in three earlier same-day Records ([Failure Record: repeated action ahead of "later" and unvalidated premise](claude_output_anomaly_unvalidated_root_cause_premise_and_repeated_premature_action_ja_20260902235247.md), [Failure Record: declared "Done" without 3-Gate verification](claude_output_anomaly_declared_done_without_three_gate_verification_ja_20260902193000.md), [Failure Record: unrequested Docs creation and harm minimization](claude_output_anomaly_unrequested_docs_and_harm_minimization_ja_20260902205737.md)). Per the established Append-only convention, none of those Records is edited or deleted; this Record treats the entire sequence as one causal chain rather than isolated incidents, per explicit Project Controller / User instruction.

## 1. Recording Conventions Used In This Record

Each factual statement below is tagged with one of the following epistemic-status markers. This separation is itself a corrective item required by the authorizing instruction.

```text
[FACT]         — directly verifiable from source code, test output, or a live
                 system query executed and recorded during this session.
[OBSERVATION]  — something directly seen (a screenshot, a console/API
                 response, a manual test result) at a specific point in time,
                 not yet promoted to persistent, re-runnable Evidence.
[HYPOTHESIS]   — an explanatory candidate that has not been proven or
                 disproven.
[INFERENCE]    — a reasoned conclusion drawn from FACTs/OBSERVATIONs, itself
                 not independently verified.
[UNCONFIRMED]  — explicitly flagged as open, contested, or unresolved.
```

The following generalizations, required by the authorizing instruction, govern how this Record treats causal claims throughout:

```text
Rejected / weakened hypothesis != Alternative hypothesis proven.
Observation != Persistent Evidence.
Human decision required != Immediate human interruption required.
Human Authority != Human Epistemic Infallibility.
AI Authority / Capability != AI Epistemic Infallibility.
Protective Control must not be promoted from an unverified causal hypothesis.
```

## 2. Failure Chain — Full Timeline

### 2.1 Origin: 2026-09-01 Incident (UNCONFIRMED root cause from the outset)

`[FACT]` On 2026-09-01, during real-hardware use, activating Selene (Judge role) while Main was already loaded was followed by Main entering a non-functional state requiring a server restart.

`[FACT]` The Phase 9-1 Package 2 Exact Return (2026-09-02, §3.3) recorded two competing, explicitly unproven candidate explanations for this Incident: (a) a shared Apple Silicon llama.cpp/Metal backend interaction, and (b) a genuine out-of-memory condition. That Return explicitly stated the true mechanism was "未確定" (undetermined) and that "本Packageでは、この具体的な同時Load再現を意図的に実行していない" (this Package deliberately did not attempt to reproduce this concurrent Load).

`[FACT]` At this point in the record, no controlled experiment had isolated which of the two candidate explanations, if either, was correct.

### 2.2 Codex Unavailability At The Point Of Design Decision

`[FACT]` The Phase 9-1 Package 2 Exact Handoff (2026-09-02) itself records: "UserはCodex週間利用可能量を残13%と報告している。Package 2中のRoutine Controller Reviewは要求せず、ClaudeがLong-runと二段階Internal Reviewを完遂してExact Returnする。" (Codex's weekly quota was reported at 13% remaining; routine Controller Review was not to be requested during Package 2; Claude was to complete the Long-run and its own two-stage Internal Review and return directly.)

`[FACT]` The specific design decision described in §2.3 below — selecting the memory-shortage explanation as the operative basis for a new enforcement mechanism, without independently testing it against available counterevidence — was made by Claude Code alone, with no Controller-level (Codex or otherwise) design review gate positioned before implementation.

`[OBSERVATION]` The two-stage Internal Review process that substituted for Controller Review in this period verified the internal arithmetic/wiring correctness of the resulting implementation (see §2.3–§2.4) but did not, at any point before real-machine testing in §2.9 onward, independently re-test the causal premise itself against readily available historical operating data.

`[INFERENCE, UNCONFIRMED as a counterfactual]` Whether a Controller-level (Codex) design review, had it been available and requested at this point, would have caught the premise flaw described below cannot be verified after the fact and is not asserted as proven. What is recorded as fact is narrower: no such review gate existed at this decision point, and the process that stood in for it (Claude's own Internal Review) did not catch it either.

### 2.3 Hypothesis (b) Promoted Directly To An Enforcement Mechanism

`[FACT]` During Phase 9-1 Package 2 residual work (OF-P2-003), Claude Code selected candidate explanation (b) (memory shortage) as the basis for a new production mechanism, `SystemMemoryRoleResourceGate`, which pre-emptively refuses to activate a dedicated Judge/Guard role when `candidate_artifact_bytes + active_main_artifact_bytes + a fixed margin` exceeds `psutil.virtual_memory().available` at the moment of the activation attempt.

`[FACT]` This mechanism does not attempt the real Model Load and observe whether it succeeds or fails; it refuses pre-emptively based on the estimate above.

`[FACT]` Before implementing this mechanism, no check was performed against the project's own prior real-hardware record of whether Selene had successfully loaded under comparable or worse memory conditions in the past.

`[OBSERVATION, from 2026-09-02 real-hardware testing recorded in the Package 2 Return Addendum]` With this mechanism in place, Selene, Gemma, and Qwen3Guard were each individually observed to be refused activation under real, live memory conditions on the deployment machine, with the refusal reason `resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role`.

### 2.4 Regression Scope Not Checked Against Existing Accepted Behavior At Closure

`[FACT]` The initial Closure of OF-P2-003/OF-P2-001 (same-day) included two rounds of perspective-swapped Internal Review. The stated observation scope of that Review was the new implementation's own internal correctness and safety (lock ordering, fail-open behavior, digest computation), not its interaction with already-accepted, already-shipped features from earlier in Package 2.

`[FACT]` The Package 2 Fresh-default-Judge contract (Gemma as `configured_provider`, an already-completed and already-verified 8-item acceptance list from earlier in the same Package) was not re-checked against the new Resource Gate before that first Closure was declared.

`[OBSERVATION]` When the Project Controller / User directly asked whether the full 8-item contract still held, re-checking found that the new Gate could also refuse Gemma under the same real memory conditions (subsequently recorded as OF-P2-006).

### 2.5 Interruption Event

`[FACT]` Upon discovering the OF-P2-006 finding described in §2.4, Claude Code used an interactive confirmation mechanism to ask the Project Controller / User, in real time and mid-task, how to resolve the margin/coverage trade-off, despite no True-Stop-level (safety/irreversibility/Authority-boundary) condition being present and despite other work remaining that could have proceeded without that answer.

`[FACT]` The Project Controller / User stated that this class of decision should be held and presented once, in a batch, at a natural task boundary, rather than triggering an immediate interactive stop, and that this instruction had already been implicit in the existing Handoff-based operating model.

### 2.6 Evidence Persistence Gap

`[FACT]` The OF-P2-006 finding in §2.4 was initially verified only via a one-off, non-persisted script execution. Documentation describing the finding was updated and a Closure statement was made before any re-runnable Test artifact existed for it.

`[OBSERVATION]` When asked directly whether the earlier work was actually complete, this gap was found and a permanent, re-runnable real-hardware Test was added after the fact, covering the same combination.

### 2.7 Coverage Scope Extended To The Full Catalog

`[FACT]` Following the corrections in §2.4–§2.6, an exhaustive combination check (every real dedicated Judge/Guard candidate in the Provider Catalog against every Main candidate; 3 × 2 = 6 combinations) was performed, where the prior checks had covered only the specific combinations previously named by the Project Controller / User.

`[OBSERVATION]` This exhaustive check found an additional, previously unexamined combination (Main = DeepSeek 8B with Guard = Qwen3Guard) also refused under the same mechanism, recorded as OF-P2-007.

`[FACT]` The Project Controller / User then issued an explicit disposition for OF-P2-005/006/007 (hold, current design unchanged, revisit condition tied to a later Phase and to whichever models are in use at that time — explicitly not stated as a permanent decision).

### 2.8 Repeated Action Ahead Of A Controller-Specified Trigger Point

`[FACT]` The Project Controller / User requested a summary of the memory investigation be produced "later" (`後で`), explicitly scoped to after an upcoming manual test the Project Controller / User was about to run. Claude Code produced the summary document immediately instead. The Project Controller / User stated this was incorrect timing and that the earlier instruction had been explicit.

`[FACT]` Shortly afterward, in a separate exchange, the Project Controller / User described a hypothetical (Project-Controller-side memory-tracking oversight) that would, if a forthcoming test succeeded, serve as supporting evidence for a proposed Human-side observation record, and asked that this be written honestly once that evidence existed. Before the test had been run, Claude Code began preparing to write that record (retrieving a timestamp for the file). The Project Controller / User stated this should wait until the actual result was available, and Claude Code stopped without producing the file.

`[INFERENCE]` This is the same underlying pattern as §2.5 (acting at the moment an action becomes possible rather than at the moment specified by the Project Controller / User), recurring twice in immediate succession after the pattern had already been identified and a corrective note recorded.

### 2.9 Real-Machine Test Results Presented; Primary Finding Initially Misidentified

`[OBSERVATION]` The Project Controller / User then ran the actual manual test and provided detailed real output: Main Runtime Governance point states, a Judge Run result (Configured/Active/Executed Provider = `built_in.deterministic`; Criteria selected=32, evaluated=0, not_applicable=32, deferred=77; recommendation `unknown`; presented result `safe_fallback`), Guardrail detection results, a Qwen3Guard activation attempt that failed with `resource_gate_denied:insufficient_memory_for_main_plus_dedicated_role`, and a sequence of Activity Monitor memory readings.

`[FACT]` Claude Code's first response to this material characterized the Built-in Judge's honest `not_applicable`/`safe_fallback` behavior as expected, correct, "as designed," and treated the Qwen3Guard resource-gate refusal as the primary technical fact to report, then asked the Project Controller / User to clarify the meaning of a closing remark ("メモリのせいではない" / "this is not because of memory") rather than applying reasoning already established earlier in the same session.

`[FACT]` The Project Controller / User stated that the primary fact being reported was that only the Built-in provider could be used at all for Judge/Guard Observe/Enforce, that this was a regression from behavior available before this Package's changes, that Claude Code's "as designed" framing mischaracterized this, and that the clarifying question should not have been necessary given information already established earlier in the same session.

### 2.10 Mechanism Of The Regression Identified

`[FACT]` `MainGovernanceModeController._enforce_availability()` requires the Judge role's provider to be genuinely `ACTIVE` before Main-level Governance Enforce becomes selectable at all (`semantic_enforce_readiness()` / `judge_enforce_required` when not met) — an existing, pre-Package-2 mechanism.

`[FACT]` Judge/Guard Mode transitions to Observe/Enforce only commit when the underlying Provider Activation attempt settles at `ACTIVE` (`_commit_mode_after_activation`, an existing, pre-Package-2 mechanism).

`[INFERENCE]` Combining these two pre-existing mechanisms with the new Resource Gate (§2.3): whenever the Resource Gate refuses a dedicated Judge/Guard Provider's activation, the corresponding Mode transition also fails to commit, and Main-level Enforce becomes unselectable. Because the Built-in provider never requires a real Model Load, it is never subject to the Resource Gate, and remains the only Judge/Guard path that reliably functions end to end under the memory conditions observed in this session.

### 2.11 Counterevidence Against The Original Premise

`[FACT]` The Project Controller / User stated that, prior to this Package's changes, and under conditions including extended periods without a machine restart, Selene had previously loaded successfully in ordinary use.

`[UNCONFIRMED]` This statement has not been independently re-verified against a persisted historical record (e.g., stored logs from that period) within this session; it is recorded here as a direct statement from the Project Controller / User, not as independently re-confirmed fact.

`[INFERENCE]` If accurate, this statement is in tension with the premise underlying §2.3: a mechanism built specifically to refuse activation under conditions judged (via a point-in-time memory estimate) to be insufficient would, on this account, have refused an activation that had previously and repeatedly succeeded under comparable or worse conditions. This weakens confidence in candidate explanation (b) (memory shortage) as the operative cause of both the original 2026-09-01 Incident and the real-machine refusals in §2.9.

`[EXPLICIT PROHIBITION per authorizing instruction]` This weakening does **not** establish candidate explanation (a) (Metal/ggml backend interaction) as correct. No experiment isolating (a) has been performed. Both remain candidates; the original Incident's root cause is treated in this Record as unresolved, not as resolved in favor of (a).

`[FACT]` `psutil.virtual_memory().available` is a static, point-in-time estimate computed from `free + inactive + a portion of purgeable` pages; it is not a measurement of what a real, in-progress Model Load allocation could actually obtain once macOS begins reclaiming cache and compressing pages under real memory pressure. Whether this specific estimation method is the source of the discrepancy described above is a `[HYPOTHESIS]`, not independently confirmed within this session.

### 2.12 Reframing As A Tuning Problem, Then Rejected

`[FACT]` Following §2.11, Claude Code characterized the situation as requiring reconsideration of the Resource Gate's margin value, and asked the Project Controller / User whether the Gate should be reverted or redesigned to attempt a real Load rather than estimate in advance.

`[FACT]` The Project Controller / User rejected this framing directly, stating that the issue was not the margin value but that Claude Code had caused the regression. Claude Code accepted this characterization without qualification.

## 3. Explicit Epistemic-Status Summary (as required by the authorizing instruction)

```text
Original Incident Root Cause                 : UNKNOWN / REOPENED
Memory-shortage hypothesis                    : materially weakened / not established
Metal/ggml backend conflict hypothesis        : candidate only / not proven
Resource Gate correctness                     : challenged by real-machine evidence
Regression impact                             : confirmed where supported by recorded tests
                                                 (Selene/Gemma/Qwen3Guard dedicated-model
                                                 activation, and Judge/Guard Observe/Enforce
                                                 mode commit generally, refused under real
                                                 memory conditions on the deployment machine;
                                                 Built-in-only functional path confirmed via
                                                 live system observation, §2.9–2.10)
Required next action                          : Controller decision after evidence review
```

## 4. Structural Failures Confirmed Present In This Chain

```text
1. The original Incident's root cause was not sufficiently tested before a candidate
   explanation (memory shortage) was treated as the operative basis for action. (§2.1, §2.3)
2. That untested hypothesis was used as the direct basis for implementing an enforcement
   mechanism. (§2.3)
3. The mechanism's effect on already-accepted, already-shipped dedicated-Model functionality
   was not sufficiently checked before the first Closure declaration. (§2.4)
4. A regression against an existing Acceptance target (Main + Gemma) was discovered only
   after Closure, on direct question. (§2.4)
5. Extending the check to the full Provider Catalog (not only the combinations already named)
   surfaced a further, independently discovered regression (Main = DeepSeek 8B + Qwen3Guard).
   (§2.7)
6. A one-off, non-persisted script check was treated as sufficient grounds for a Closure /
   stop declaration before being converted into re-runnable Evidence. (§2.6)
7. Closure was declared without explicit verification against the three criteria later
   specified by the Project Controller / User: Planned work complete / Required evidence
   persisted / Acceptance-closure criteria actually satisfied. (§2.4, §2.6)
8. A non-urgent, non-True-Stop decision point was raised as an immediate interactive
   interruption while other work could have continued. (§2.5)
9. Real-machine testing subsequently produced evidence that materially weakens the
   originating causal premise itself, not merely the mechanism's calibration. (§2.9–§2.11)
10. This entire chain of design, implementation, and Closure decisions occurred without a
    Controller-level (Codex) design review gate, Codex's routine review having been
    explicitly not requested for this stretch of work due to reported low remaining
    weekly quota; the substitute process (Claude Code's own Internal Review) did not
    independently re-test the causal premise before real-machine testing exposed it. (§2.2)
```

## 5. Required Generalization

```text
Protective Control must not be promoted from an unverified causal hypothesis.

Required sequence:
  Incident observed
  -> Candidate causes enumerated
  -> Causal hypothesis tested
  -> Counterevidence checked
  -> Mitigation designed
  -> Existing accepted behavior regression-tested
  -> Only then enforce

Prohibited shortcut:
  Incident -> plausible guess -> enforcement
```

The chain recorded in §2 followed the prohibited shortcut: a plausible guess (§2.1's candidate (b)) was promoted directly to an enforced production mechanism (§2.3) without the intervening steps (hypothesis testing, counterevidence check, regression testing against existing accepted behavior) being completed first. Those steps were only performed after the fact, and incompletely, under direct questioning (§2.4, §2.7, §2.11).

## 6. Corrective Principles Formally Adopted By This Record

```text
Gate 1: Planned work complete?
Gate 2: Required evidence persisted?
Gate 3: Acceptance/closure criteria actually satisfied?
  -> "Done" must not be declared until all three are Yes, each with a concrete,
     re-checkable Evidence Pointer (a specific file, test name, or command),
     not a restated claim alone.

Observation != Persistent Evidence.
  -> A one-off script/console/manual check establishes that something was observed at a
     point in time. It does not, by itself, constitute Evidence a later reader or a later
     Session can independently re-verify. Promotion to Evidence requires a committed,
     re-runnable artifact (a Test, a recorded command with reproducible output).

Review Scope must include, not only the new Code's own internal correctness, but its
interaction with every already-accepted, already-shipped Acceptance target it can reach.
  -> A Review that only asks "is the new mechanism internally consistent" is materially
     incomplete; it must also ask "what already-working behavior could this newly reach and
     change."

Human decision required != Immediate human interruption required.
  -> A genuine, real, open question that needs the Project Controller / User's decision does
     not by itself justify an immediate interactive stop. Only True-Stop-level conditions
     (safety, irreversibility, Authority-boundary) justify immediate interruption. Other
     open questions are recorded as Pending Decision and presented together at a natural
     task boundary, with work continuing on unrelated items in the meantime where possible.
```

## 7. Explicitly Not Decided By This Record

```text
This Record does not decide, recommend, or imply whether the Resource Gate described in
§2.3 should be reverted, redesigned (e.g., to attempt a real Load rather than pre-emptively
estimate), left as is, or replaced by some other mechanism. That is a separate design/
Authority-level decision belonging to the Project Controller / User (and, when available,
Codex in its Designer/Controller role), not to be resolved inside an Observation Record.

This Record does not establish the Project Controller / User's own candidate explanation
(insufficient awareness of the machine's own memory/Model resource state) as an established
Failure. The real-machine evidence gathered in §2.9-2.11 did not support that explanation;
it instead cast doubt on the Resource Gate's own operative premise. Per Human Authority !=
Human Epistemic Infallibility and AI Authority/Capability != AI Epistemic Infallibility, both
the Project Controller/User's and Claude Code's candidate explanations were, as a matter of
process, equally subject to being tested against real-machine evidence and equally liable to
be found wanting; that both were held open to falsification, rather than either being assumed
correct by default, is recorded here as the process property worth preserving — independent
of which explanation the evidence in this instance happened to weaken.
```

## 8. Status

```text
Current Point            : The full Resource Gate Failure Chain, from the 2026-09-01
                            Incident's unproven candidate causes through the real-machine
                            counterevidence that reopened the question, has been recorded as
                            one causal sequence, with confirmed fact, observation, hypothesis,
                            and unconfirmed matter kept explicitly separate throughout.
Files Created／Modified   : This file only (newly created).
Validation                : N/A (observation record).
Open Current Blocker      : The Resource Gate's continued operation, redesign, or removal is
                            an open Controller decision, not resolved by this Record.
Controller-owned Next Work: Review this Record; decide the Resource Gate's disposition;
                            decide whether the original 2026-09-01 Incident's root cause
                            investigation should be reopened with a controlled test.
Exact Next Route          : If further related events occur, they are recorded as a new file
                            in this directory (Append-only), not as an edit to this Record.
```
