# Phase 4 Codex Third Independent Review — Final Exact Rework Handoff

```yaml
document_id: phase_4_codex_third_independent_review_rework_handoff_20260822080242
status: one_major_rework_required
phase: phase_4
subphase: phase_4_h
work_unit: p4_h_wu_003_codex_third_independent_major_review
from: プロジェクト責任者兼設計統括者役（Codex）
to: Claude側設計統括者役
language: ja
recorded_at: 2026-08-22 08:02:42 JST
recorded_at_source: `TZ=Asia/Tokyo date '+%Y%m%d%H%M%S %Y-%m-%d %H:%M:%S %Z'`
predecessor: docs/project/phases/phase_4/handoffs/phase_4_claude_second_rework_complete_candidate_handoff_ja.md
completion_line: phase_4_claude_third_rework_complete_candidate
source_rework_authorized: true
test_rework_authorized: true
new_append_only_handoff_authorized: true
stable_doc_mutation_authorized: false
runtime_data_access_authorized: false
definitions_mutation_authorized: false
git_mutation_authorized: false
phase_4_closure_authorized: false
phase_5_authorized: false
```

## 0. Controller Decision

`ADJUST — ONE MAJOR FINDING REMAINS`。

第二回Reworkのうち、次はSource上もClosure可能と判断する。

```text
P4-CODEX-007 Evidence Typed Identity本体        : CLOSED except §1残件
P4-CODEX-008 Phase 3 Source Plan実Identity      : CLOSED except §1 OBSERVE接続
P4-CODEX-009 Mixed External Apply Atomicity     : CLOSED
P4-CODEX-010 Authority／Terminal Conflict       : CLOSED
P4-GOV-002 Test Temp Boundary Correction        : CORRECTED
```

新たな広範囲Reworkは不要である。残るのは、OBSERVE Binding／EvidenceとActual Mode Failure Evidenceの1群だけである。

```text
P4-CODEX-011 : OBSERVE Binding／Actual Degraded Evidence Gap

Phase 4 Technical Closure : BLOCKED
Phase 5                   : NOT AUTHORIZED
```

## 1. P4-CODEX-011 — OBSERVE Binding／Actual Degraded Evidence Gap

### 1.1 OBSERVEがBindingを作らない

Actual Hookはpre／postとも、次の条件でしかBindingを作らない。

```python
binding = composition.bind_point(...) if mode == "enforce" else None
```

そのため、Valid Bundle＋OBSERVEでも次になる。

```text
StandardGovernanceResult.binding_digest_sha512 : None
Evidence.binding_digest_sha512                 : None
Evidence.source_plan_id                        : None
Evidence.source_plan_digest_sha512             : None
```

第二回Reworkで実Source Plan ID／DigestとTyped Evidence Fieldは作られたが、比較実験の中心であるOBSERVE経路へ接続されていない。

Frozen Acceptance Matrixは次を別Rowとして定義する。

```text
valid definitions + valid binding + observe
  -> Result／Evidence only
  -> Output unchanged

valid definitions + stale binding + observe
  -> rebind or explicit unavailable
  -> stale reuse 0
```

現在はOBSERVEがBinding自体を省略するため、この2 Rowを実装／検証できない。さらにInvalid Bundle／Plan Compilation FailureでもOBSERVEはBinding Stateを見ず、Descriptorsが残れば評価を続け得る。

### 1.2 Mode Provider FailureのEvidence TestがActual Wiringを再現しない

`test_mode_unavailable_records_a_degraded_last_result_and_evidence`は、Hook側Mode ProviderだけをRaiseさせ、Observerは独立した`is_active() -> True`のFakeを使用する。

Actual CompositionではHookと`EvidenceGovernanceObserver`が同じ`mode_controller.current_mode_value`を参照する。したがってそのProviderがRaiseした場合、Actual Observerの`is_active()`は例外を内部でCatchして`False`を返し、Terminal Evidenceは書かれない。

Process-local Last ResultはDEGRADEDになったが、Completion Handoffが主張する「Actual Mode Provider UnavailableをEvidence Terminalへ記録」は実配線で成立していない。

### Required Correction

#### A. OBSERVEにもBindingを接続

- OFFだけは今までどおりBinder／Evaluator／Action／Evidence Call 0。
- OBSERVEとENFORCEは、同じCurrent Source Plan／Capability／Authority／Policy／Budget／RegistryからPoint Bindingを作る。
- OBSERVEはValid BindingをResult／Evidenceへ渡すが、Action Resolverを絶対に呼ばず、Model Input／Output／Stop／Persistence Mutation 0を維持する。
- OBSERVEの`StandardGovernanceResult.binding_digest_sha512`とEvidenceのBinding／Source Plan ID／Digestを非Nullにする。
- OBSERVEでBindingがUnavailable／Staleなら、再BindするかTyped `unavailable／degraded`へ収束し、Evaluator／Actionを実行しない。
- Definition 0件のOBSERVEは`inactive_no_definitions`を維持するが、Safe ReasonはBindingの`no_provider／provider_failure／invalid_bundle／no_definitions`を保持する。すべてを`no_definitions`へ潰さない。
- ENFORCEの既存Fail-closed、OFF Call 0は変更しない。

#### B. Actual Mode Failure Evidence

- Mode ProviderがUnreadableな経路は、Observerの同じMode Providerによる`is_active()`判定へ再依存させない。
- Readable OFFではEvidence Call 0を維持する。
- Readable Modeでは従来どおり通常Gateを使う。
- ModeがUnreadableになった異常経路では、Typed Degraded Terminalを一度だけSafeに記録する。Observer Write FailureはModel決定を変えず、Process-local Degraded Statusへ反映する。
- Actual `EvidenceGovernanceObserver`と同一のRaiseするMode Providerを使うIntegration Testを追加する。`is_active=True`だけを返す独立FakeでClosureしない。

## 2. Required Tests

最低限、次を追加／修正する。

1. Valid Bundle＋OBSERVEのpre／postが非Null Binding／Source Plan ID／DigestをResult／Restart Evidenceへ残す。
2. Valid Bundle＋OBSERVEでAction Resolver Call 0、Executed Action 0、Model Input／Output Mutation 0。
3. Stale／Unavailable Binding＋OBSERVEでEvaluator／Action 0、Typed unavailable／degraded。
4. Empty／Invalid／Provider Failure＋OBSERVEで各Safe Reasonを区別し、Output Mutation 0。
5. Actual `EvidenceGovernanceObserver`と同一Raise ProviderでMode Failure Terminal EvidenceまたはObserver Degraded Evidenceが残る。
6. Readable OFFでBinder／Evaluator／Observer／Evidence Call 0を維持する。
7. Existing ENFORCE、Public／Basic、v1／v2、Persistent／RAG Regressionを維持する。

## 3. Validation Boundary

前Cycleで成立したRoot-local Test Boundaryをそのまま使用する。

```text
Base Root     : <PROJECT_ROOT>/.p4t
pytest        : TMPDIR="$PWD/.p4t/t" ./.venv/bin/python -m pytest ... --basetemp="$PWD/.p4t/p-*"
Frontend      : TMPDIR="$PWD/.p4t/t" npm run ...
System Temp   : FORBIDDEN
uv run        : FORBIDDEN
Network       : FORBIDDEN
```

`.p4t`は本Cycleが新規作成したExact PathだけCleanup可。使用後のPostflightを新Handoffへ記録する。

## 4. Exact Allowed Scope

### Read

- Project Root内の本Findingに必要なSource／Test／Phase 4 Docs。
- `definitions/`はRead-only Test Source。

### Write／Modify

必要な最小Pathだけを選ぶ。

```text
src/margpa_runtime_llm/bootstrap/runtime_governance.py
src/margpa_runtime_llm/modules/runtime_governance/application/point_runtime.py
src/margpa_runtime_llm/modules/runtime_governance/domain/results.py

src/margpa_runtime_llm/modules/audit_evidence/**
src/margpa_runtime_llm/adapters/audit_evidence/**
src/margpa_runtime_llm/web/runtime_governance_routes.py

tests/unit/runtime_governance/**
tests/unit/audit_evidence/**
tests/integration/audit_evidence/**
tests/integration/web/test_runtime_governance_*.py

.p4t/**
```

Docs Writeは次の新規Append-only Handoffだけを許可する。

`docs/project/phases/phase_4/handoffs/phase_4_claude_third_rework_complete_candidate_handoff_ja.md`

## 5. Forbidden

- Project Root外Action、System Temp、Provider Memory、Claude／Codex Memory。
- `runtime_data/`、`models/`、`other/`、別Project。
- `definitions/`のWrite／Rename／Delete。
- Stable／Roadmap／Phase Index／Requirements／Architecture／ADR／Execution Plan／Acceptance Matrixの編集。
- Existing History／Existing Handoffの編集・置換・削除。
- Git／GitHub Mutation、Commit／Push／Branch／Tag／Release。
- Phase 4 Closure、User Acceptance、Phase 5／6、DeepSeek、AWS。
- OBSERVEをAction Resolverへ接続すること。
- Actual Observerと異なる独立FakeだけでMode Failure EvidenceをCloseすること。

## 6. Completion Contract

Routineな実装／Test調整はClaude側で完了させる。新規Human Decisionは不要である。

新Completion Handoffには次を記録する。

```text
P4-CODEX-011                    : CLOSED / OPEN
Observe Binding                : PASS / FAIL
Observe Source Plan Evidence   : PASS / FAIL
Observe Mutation／Action Call  : 0 / N
Observe Invalid/Stale Matrix   : PASS / FAIL
Actual Mode Failure Evidence   : PASS / FAIL
OFF Call 0                     : PASS / FAIL
ENFORCE Regression             : PASS / FAIL
Focused／Full／Static           : Exact Output
Root-local Temp                : Exact Path／Cleanup／Postflight
Stable Edit                    : 0 / N
Git Mutation                   : Evidence Class付き
Root-outside Action            : Evidence Class付き
runtime_data Access            : Evidence Class付き
Remaining Technical Major      : Exact List
Recommendation                 : GO / ADJUST / STOP
```

Handoff作成後に停止する。Phase 4 Closure／Git／Phase 5へ進まない。
