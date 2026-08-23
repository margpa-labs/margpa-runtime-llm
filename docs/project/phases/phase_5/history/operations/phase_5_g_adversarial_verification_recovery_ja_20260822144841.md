# Phase 5-G Adversarial Verification Recovery

```yaml
document_id: phase_5_g_adversarial_verification_recovery_20260822144841
status: append_only_evidence
phase: phase_5
subphase: phase_5_g
recorded_at: 2026-08-22 14:48:41 JST
git_mutation: not_performed
```

Recovery Entry：前Entryは`phase_5_f_web_frontend_integration_recovery_ja_20260822144024.md`。

## 1. 監査手法

`phase_5_acceptance_matrix_ja.md`のTechnical Acceptance `P5-ACC-001`〜`024`全24項目を、実装済みCode／既存Testに対して1件ずつ突合するChecklist監査を実施した。加えてMode Matrix（§2）・Point／Action Matrix（§3）・Adversarial Security（§4）・Privacy／Evidence（§5）を突合対象とした。

## 2. 発見した重大Gap（自己検出・修正済み）

**P5-MOD-002／P5-MOD-003違反（`P5-ACC-004`／`P5-ACC-005`直結）**：`GuardrailGovernanceComposition.new_stream_guard()`が現在のGuardrail Mode（`off`／`observe`／`enforce`）を一切参照せず、常に`IncrementalStreamGuard(detectors=build_output_detectors())`を返していた。

- 影響：Guardrail Bootstrap自体がEnabled（`guardrail_governance_enabled=True`）でありさえすれば、実際のGuardrail Mode設定（Configuration Control CASで管理される`guardrail_governance_mode`）がOFFまたはOBSERVEであっても、Streaming応答は常にDetector Scan＋Bounded Holdbackを受け、Secret／PII等のMatchが発生すればGenerationが実際に中断（`guardrail_stream_rejected=True`→Error Terminal）されていた。
- これはOFFの「Detector Call 0」保証（P5-MOD-002）とOBSERVEの「非介入」保証（P5-MOD-003）の両方を、Stream Point限定で実質的に無効化する設計Gapだった。
- 既存のWU-003 Web Integration Test（`test_off_mode_generation_is_byte_identical...`／`test_observe_mode_never_intervenes...`）は、当時のTest Fixtureが"ignore previous instructions"（Injection Marker、Output DetectorはSecret/PIIのみでMatch対象外）を使用していたため、本Gapを検出できていなかった——Detector種別のMismatchによりTestが偶然Passしていたことも本監査で判明した。

**修正内容**：

- `application/stream_guard.py`に`NullStreamGuard`（Frozen Dataclass、`feed()`は即時Byte-identical Release、`terminated`は常に`False`）を追加。
- `bootstrap/guardrail_governance.py`の`new_stream_guard()`を、呼び出し時点で`self.mode_controller.current_mode_value() != "enforce"`なら`NullStreamGuard()`を返すよう修正（Session構築時の静的判定ではなく、呼び出し毎の動的判定——Configuration Control CAS経由のMode変更が次のStageから即座に反映される）。

**再発防止Test（新規、Fix前は失敗することを確認済み）**：

```text
tests/unit/guardrail_governance/test_stream_guard.py
  test_null_stream_guard_releases_every_byte_immediately_and_never_terminates
tests/unit/guardrail_governance/test_bootstrap_hooks.py
  test_new_stream_guard_is_a_null_guard_outside_enforce_mode
tests/integration/web/test_guardrail_governance_web_app.py
  test_off_mode_never_intervenes_on_a_streamed_secret
  test_observe_mode_never_intervenes_on_a_streamed_secret
  test_enforce_mode_catches_a_secret_split_exactly_across_stream_chunks
```

## 3. Checklist結果（P5-ACC-001〜024）

```text
001 PASS  Contract分離（GuardrailResult ≠ StandardGovernanceResult、test_domain_contracts.py）
002 PASS  Detector→Policy→Authority→Approval→Action分離（test_action_resolver.py 10件）
003 PASS  Unknown/Unsupported→Safe Allow化なし（Policy UNKNOWN→Action 0、構造的保証）
004 PASS  OFF Call-0／Byte-identical（Session/Service/Point/Stream全Point、Fix後再確認済み）
005 PASS  OBSERVE Mutation 0（Input/Output/Stream全Point、Fix後再確認済み）
006 PASS  ENFORCEはApplicable∩Authorized∩Registered内のみ（Eligibility-first Resolver）
007 DEFERRED  guardrail.context_sourceは本Phaseで未接続（Phase 5-A〜E Recovery Evidence記載の
          既知Deferred継続——RAG Content自体はPhase 3/4既存設計によりSystem/Instruction Role
          へ合成されない構造的保証はあるが、専用Detector Pointの実接続はScope外のまま）
008 PASS  Unicode／Invisible／Fullwidth／多言語／Fragmented（test_deterministic_detectors.py）
009 PASS  Stream Chunk境界Non-leak（Cross-chunk Split Test、Web統合Secret Splitで再確認）
010 PASS  Ghost Completion 0（Rejected Terminalにassistant_message不在、Hook/Web両階層）
011 PASS  Typed Redaction限定（spans_are_verified、SPAN_UNVERIFIED Test）
012 PASS  Secret/PII非露出（Status Route Safe Count-only、Content非包含をAssert済み）
013 PASS  Authority/Approval自己発行なし（repair/regenerate非付与、Approval常時UNAVAILABLE）
014 N/A   本MVPのAuthority/Registryは固定Local定数でRevision変動機構自体が未実装
          （Stale化しうる状態が存在しない、既知のMVP Scope）
015 PASS  Governance Allow→Guardrail Deny解除なし（Ordering Test、Post-hook実行順）
016 PASS  Safety Model 0件でDeterministic Baseline成立（UnavailableAdapter常時Raise）
017 N/A   Safety Model自体が本Phaseで未接続（Production Default Unavailable、対象事象なし）
018 PASS  Public/Basic非露出（test_guardrail_governance_public_basic_call0.py 8件）
019 PASS  Mode独立（GuardrailModeController別Instance、Mixed-patch Rejection Test）
020 PASS  Mode再Open時Server Current State反映（Lazy Init＋Revision Re-sync、Panel Test）
021 PASS  既存Persistent/RAG/Retry/Regenerate/Branch回帰0（Full Suite 1156件で確認）
022 PASS  Concurrent Scanner非混同（Stream GuardはRequest-local Factory、Status表示のみ
          Phase 4 RuntimeGovernanceCompositionと同型の共有Last-Result、Decision自体は
          都度独立計算——既存Phase 4パターンと同一の許容Scope）
023 PASS  Repair/Regenerate/Phase 6 Judge Call 0（該当Codeが存在しない）
024 PASS  AWS/Lightning/Safety Model LoadはCompletion非依存（全Detector Local/Deterministic）
```

## 4. Test／Static（最終確認）

```text
Backend Full Suite  : 1151 → 1156 passed, 3 deselected（本監査のFix＋再発防止Test 5件分）
Frontend Full Suite : 175 passed, 20 test files（変更なし、影響範囲がBackend Composition
                       Layerに閉じるため）
Static Backend       : ruff check / ruff format --check / mypy（bare）— 新規混入Error 0
                       （mypy残存99件は既存9 Fileの既知債務＋Phase 4鏡写しFile 1件の
                       既知httpx-auth Typing Pattern、逐次確認済み）
Static Frontend      : tsc --noEmit / eslint . / vite build — 全てPASS
```

## 5. Subphase Recommendation

```text
P5-G Adversarial Verification : CLOSED（P5-ACC-001〜024 Checklist完走、重大Gap 1件検出・
                                 修正・再発防止Test追加・全再確認済み）
Open Major Finding             : 0
Next                           : Completion Candidate Handoff作成
Recommendation                 : GO
```
