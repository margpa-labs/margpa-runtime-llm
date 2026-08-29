# Phase 6 Copilot R9〜R12 Exact Return Handoff

```yaml
provider: GitHub Copilot app
role: 設計者兼実装者役
task_identity: Copilot Phase 6 Post-Review Rework Task
active_contract: P6-GOV-020 / R9-R12 Exact Rework Handoff
claim: Complete Candidate
next_owner: Codex プロジェクト責任者兼設計統括者役
next_exact_action: Independent Review
```

## Disposition

| Finding | Disposition |
|---|---|
| P6-CODEX-069 | Fixed: Judge/Guard provider Mode ON切替をtransactional candidate activationとrollback preservationへ変更。 |
| P6-CODEX-070 | Fixed: ENFORCE deadline及びcancel graceはfrozen provider `StageBudgetProfile`からrun単位で導出。 |
| P6-CODEX-071 | Fixed: hook failure/empty terminal fallbackをfrozen JA/EN languageへ収束。 |
| P6-CODEX-072 | Fixed: Judge Evidenceをbase request_idで記録し、API/UIのsame-id correlationを追加。 |
| P6-CODEX-073 | Fixed: unmatched/historical recordをCurrentへ混入させないresponse/UI projectionとregressionを追加。 |

## Verification and Review

| Surface | Result |
|---|---|
| Focused backend | 78 passed |
| Canonical backend | Ruff pass; Mypy pass; pytest 1700 passed, 7 deselected |
| Focused frontend | 16 passed; typecheck/lint pass |
| Canonical frontend | 230 passed; typecheck/lint/build pass |
| Internal Review 1 | P6-R12-IR-001〜003を検出、rework済み |
| Internal Review 2 | canonical verification後、open findingなし |
| Real Selene/Qwen3Guard・official provenance・browser | NOT RUN / AUTHORITY REQUIRED |

## S1〜S17 Execution Matrix

| S | Surface | Result |
|---|---|---|
| S1 | R9 candidate preflight failure | preserved tuple |
| S2 | R9 candidate load failure | preserved tuple |
| S3 | R9 old unload failure | preserved tuple |
| S4 | R9 successful activation | atomic projection |
| S5 | R10 frozen ENFORCE deadline | provider budget owned |
| S6 | R10 cancellation grace | provider budget owned |
| S7 | R10 timeout/late publication | safe fallback |
| S8 | R10 hook exception | frozen JA failure |
| S9 | R10 none/empty hook result | frozen language fallback |
| S10 | R10 built-in path | regression pass |
| S11 | R10 repair/rejudge inheritance | regression pass |
| S12 | R11 recording OFF | no-call regression pass |
| S13 | R11 base request identity | same-id projection |
| S14 | R11 cross-id recording | Historical/Unmatched |
| S15 | R11 polling/unmount | frontend regression pass |
| S16 | static contracts | ruff/mypy/typecheck/lint pass |
| S17 | full regression/build | backend/frontend canonical pass |

## Acceptance Inventory

Original Acceptance 40: `P6-ACC-001`〜`P6-ACC-040` are covered by the canonical backend/frontend regression result above. Delta Acceptance 26: `P6-RR-ACC-001`〜`P6-RR-ACC-026` cover S1〜S17, provider identity, frozen budget, 109 criterion accounting, failure language, recording correlation, negative path, UI polling, and canonical static/full verification; all passed. The 109 criterion invariant remains `selected = evaluated + deferred` and `evaluated = passed + deviated + unknown + not_applicable`; existing canonical coverage passed.

## Identity / Budget / Failure / Recording Correlation Matrix

| Matrix | Invariant |
|---|---|
| Identity | Configured/Active/Executed provider are independently projected; transition failure preserves the prior tuple. |
| Budget | Run freezes active provider stage budget before work; pipeline deadline and cancellation grace use that freeze. |
| Failure language | typed evaluation failure uses the run's frozen language; no user-facing fixed-English terminal escape remains. |
| Recording correlation | Turn, Judge Result, and Judge Evidence share base request_id; only same-id records become Current. |

## Incident and Pilot Evidence

`phase_6_copilot_r9_path_boundary_incident_ja_20260828212032.md` records the non-mutating initial pytest path-resolution exit 127 and the correction to explicit canonical-root commands. Previous automation stop behavior is recorded in `phase_6_copilot_post_review_r9_r12_pilot_entry_evidence_ja_20260828212032.md`; this execution continued through focused failure, review findings, rework, and canonical verification without a discretionary stop.

## Changed Source/Test SHA-512

```text
5ce772a0a595a780cea6b45b3d0e7aff13a5a698a54b34fd0c0a709d63abcfe610d8c4607347ac5e34ceb09f1e7f65abf14bdd9fc3e9a2e5dc2b33b65e2f72b3 provider_selection_controller.py
edefb5ea4a769886c666945c87e405e2a6f1189e275a7dd8119348616ec36a9f53fe10e24f18b37c849ed405e7925622cd1e53c7934f036c9799e01c08ee45d7 role_lifecycle_manager.py
8a5d629d9f87accbc53203d23882db9343b5408e6e206c249932940320913e66677eaa09be1b4e5cf41e94e6fd2f1446b1741c26196a6e5415cbeedccd9d8aef provider_selection_routes.py
994a2140d69a6f7d9abe504de12e89e4941d9fd4c9c1928b8e69d323729d8aed1015f6fd9d9e78c05873185f25b85478faac5518d8b6d3b492c5f0a2b038ab59 judge_live_integration.py
697fc52544bdcaae4f17f9c7109723773ff4d2e78236adc22690b12f5c37dca2acc13d8d534320ccdd93c81e8afe0af310b56befa4cbf759b3d5c6a803392579 recording_live_integration.py
11752f7eeed6c3e3f60ad3e4a7657d3515305d72544feaca8790e34678d072778bdf712c07f3934b2adb52fbddc3078c385650624d2af57ff5e5f62bf575f88e conversation_generation.py
3a8b7edb8f4865812599fe9420635c0e22822328131f50fbf1700623938d13306f12b29c0be4cbe8f2e96a731d3a35c91c9a82f5c5b9246b9dc5dbdecdc62d9d feature_modes_routes.py
4d04b83461885009a54f4667f66f64b73a249e8d111e075f3c972c742bc1a740bf20aa1fb584470ec5fb1f40cfe2eb639e20c1970a3b85255db562c9b8ef5e66 frontend/src/types.ts
d92c17090ab3549f9d4a913bb228c085548493754c3911fa28919f3bc6cda3b6d6ab87ae86d28212025217ca389396dba90e6dc20fe365e91ed43d2abc31ba03 FeatureModesPanel.tsx
f086816cf1864f096bb162efe30060be1ea94f1a49e57e1fb0b0d30e8827ce63b2a8d9d567a5e22c42cd4e4ad8782cdb075a9e60771af78757c97ba44289e586 test_provider_selection_role_atomicity.py
1d5370d98b1bb1b4276d6a0ee2f54ce54156880024f2831df198e010f23b1abf99b7b58799f063cfb68d02b498d7684cc10e1a0a90db351c9bbbb19d6b2a7a3e test_feature_modes_routes.py
ea395638803b4d4263f513601a07eb7380ae5905e58bab2b0c5deabc56fb819e032645f7de3def149dd6603a2f4d65f99635fc336e2bbcbf69f7ccea9ae48831 test_judge_live_integration.py
d17032c22cb598b4e44c1b3be21ac0ad8769ac312e14cff8aec4210a7d16bbbc960bf8e99782212e94075053923e018f41bd4028ba1a114b627490000a079490 test_recording_live_integration.py
1b9a3a0af31c8f616d60c1b39233b87b5ab8323e558c75c82fe1f3430da21f393ee4598ef424f62fd27b27bb517526ec6d5a6425a343bc1e06a13358ebde5fa2 test_conversation_generation_judge_hook.py
bfd9aeb3a51519715b157f7fdc3bcf622b49fd48c56ab105d993ab8b3a0376e7b89c5c220f5d2120ea5dfad828a4ccc9a4e669fd375234ca416401dbd9ce5702 FeatureModesPanel.test.tsx
740327325923bf1c8449a5e8d0c2e97facb0303fc17bd9057f47736827a382401f942a76b112013eadccaa4ab186432e7d1a8148ae308ecb6aab09ce3ebf0a9e web/static/app.js
1487a8f4b8ae9f24b7de3ff1b7ef6e0b3db0974b20ff538f23522e70709e913944dcf675a6173fcbb273f34e6f191dfb6767a26881efc899f6edabca8eb0e597 web/static/app.css
0164475a2143041d53cebf2d43b61f9ccf9ab1bdf9c1b49a9efe5cee8176caaa2b5b9bee34116d7a782ddc71df451f825059dabb44bfeeef744aaf8a43b759bb web/static/index.html
```

Exact next action: Codex Independent Review. No Phase 6 Closure or Phase 7 action has been taken.
