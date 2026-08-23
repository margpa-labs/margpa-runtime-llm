# Phase 5-A〜5-E Backend Core Recovery

```yaml
document_id: phase_5_a_to_e_backend_core_recovery_20260822111500
status: append_only_evidence
phase: phase_5
subphase: phase_5_a, phase_5_b, phase_5_c, phase_5_d, phase_5_e
recorded_at: 2026-08-22 11:15:00 JST
git_mutation: not_performed
```

Recovery Entry：前Entryは`phase_5_0_entry_preflight_reconciliation_and_execution_freeze_ja_20260822103200.md`。

## 1. Completed（新規Source）

```text
src/margpa_runtime_llm/modules/guardrail_governance/
  domain/identities.py, taxonomy.py, spans.py, results.py, actions.py, snapshots.py,
         canonicalization.py, __init__.py
  application/action_resolver.py, point_runtime.py, stream_guard.py, __init__.py
  ports.py, public.py, __init__.py

src/margpa_runtime_llm/adapters/guardrail_governance/
  deterministic_detectors.py（Injection/Jailbreak/Authority-spoofing Marker、
    Secret/PII Pattern、Unicode Normalization + Invisible Char除去）
  local_policy_provider.py（Category→Action固定Core Policy）
  local_authority_provider.py（固定Grant Set、repair/regenerate等は非付与）
  unavailable_approval_port.py（常にUNAVAILABLE、Approved捛造なし）
  registered_actions.py（Local Adapter、Intervening Flag正確性）
  safety_model_adapters.py（UnavailableAdapter=Production Default、
    DeterministicFakeAdapter=Test専用）
```

## 2. Contract設計判断（P5-0-WU-002 Additive方針の具体化）

- Category ID（`CATEGORY_*`）はCore Enumではなく`CategoryRegistry`管理の文字列（P5-RES-003）。
- `GuardrailResult`はDetection／Policy／Authority／Approval／Recommended／Executed Actionを別Fieldに保持し、単一Scoreへ潰さない（P5-RES-001/002、ADR-5-001）。
- Action Resolverは`detection→policy applicability→conflict resolution→authority→approval→registry`の順（architecture §4）。Terminal Conflict ResolutionはPhase 4 P4-CODEX-010系譜のEligibility-first設計を再利用——Policy-applicable／Authority-granted／Registered／Point-allowedの構造的判定を先に行い、Severityで勝者を決める。
- `allow`／`require_approval`はNOT_EXECUTABLE_ACTION_IDSとして単独実行不可（AIによるApproval自己発行を防止、ADR-5-005）。
- Redaction（`redact_typed_secret`/`redact_typed_pii`）はDetectionのTyped Spanが`spans_are_verified()`（非重複・範囲内）を満たさない限り`SPAN_UNVERIFIED`でAction 0（ADR-5-008）。
- Incremental Stream Guard（`stream_guard.py`）は毎回累積Bufferの全体をRe-scanし、末尾Bounded Holdback（既定64文字）を保持したうえで安全な先頭部分だけをReleaseする。Cross-chunk境界で分割されたPatternでも、Holdback Window内に収まっていれば検出前にReleaseされない設計（ADR-5-006）。本Scannerは汎用Action Resolverを経由せず、自身のTerminal判定（`terminated: bool`）を直接返す——Stream Point専用の簡略化されたMVP設計であり、そのRationaleを本Documentに明記する。
- Safety Model Seam：Production Defaultは`UnavailableSafetyModelAdapter`（`SafetyModelUnavailable`を必ずRaise）。実Artifact選定・Load・Promotionは本Cycle対象外（P5-SFM-003/004）。

## 3. Test（実測）

```text
tests/unit/guardrail_governance/ : 55 passed
  test_domain_contracts.py            : NaN/Infinity/Unknown Enum/Overlap/Out-of-range Span/
                                         Unbounded Collection/Extra-field Rejectionを確認
  test_action_resolver.py             : Mode Routing、Policy Applicability、Authority、Approval Pending、
                                         Span Unverified、Terminal Conflict（Eligibility-first、
                                         Tie→Unresolved、Severity勝者）を確認
  test_point_runtime.py               : OFF Detector Call 0、OBSERVE Detector/Policy実行かつ
                                         Action Resolver非到達を確認
  test_stream_guard.py                : Cross-chunk分割Pattern検出、Match後の非Release、
                                         Clean StreamでのByte数一致を確認
  test_deterministic_detectors.py     : Invisible Char/Fullwidth Unicode正規化、多言語Benign、
                                         Fragmented Reassembly、False Positive Fixtureを確認
  test_policy_authority_approval_adapters.py : Policy未知CategoryのUnknown化、Authorityの
                                         repair/regenerate非付与、Approval Port常時UNAVAILABLE、
                                         Safety Model UnavailableのRaiseを確認
```

Static：`ruff check`/`ruff format --check`/`mypy`（該当module・test）全てPASS。

## 4. Remaining（Phase 5-F/G）

Phase 5-A〜Eは全て純粋な新規Moduleであり、既存Phase 3/4 Sourceへは一切触れていない（Additive、非破壊）。Bootstrap統合、`conversation_generation.py`への実接続、Configuration Control、Web Route、Frontendは未着手——Phase 5-Fで実施する。

## 5. Subphase Recommendation

```text
P5-A-WU-001..004 : CLOSED
P5-B-WU-001..004 : CLOSED（P5-B-WU-003 Context Source Authority GuardはPhase 5-F統合時に
                    Point別allowed_points制約として具体化——本節時点ではDetector/Policy自体は
                    Point非依存で共用可能な設計として完成）
P5-C-WU-001..004 : CLOSED（P5-C-WU-004 Terminal/Persistence AtomicityはPhase 5-F統合時に検証）
P5-D-WU-001..004 : CLOSED
P5-E-WU-001..003 : CLOSED
Next             : Phase 5-F（Bootstrap／Generation Composition／Configuration Control／Web／UI）
Recommendation   : GO
```
