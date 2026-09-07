# Phase 9-1 — 実Gemma 32 Criterion Rejudge Evidence分離 Exact Return Handoff

```yaml
document_type: exact_return_handoff
document_state: candidate_for_controller_review
from: claude
to: codex_controller
in_response_to: ../handoffs/phase_9_controller_real_32_criterion_rejudge_evidence_disambiguation_exact_handoff_ja_20260905082539.md
git_action: none
network_action: none
external_artifact_mutation: none
closure_authority: none_requested
language: ja
recorded_at: 2026-09-05 08:39:24 JST
```

## 1. Maximum Claim

`P9_1_REAL_32_CRITERION_REJUDGE_EVIDENCE_REWORK_PARTIAL_SELF_LIMITED_CAPTURE`

**主張すること**:
- Test-only Observability(§2.A、7項目)をProduction Decoder/Contractを一切変更せずに実装し、Ruff/Mypy/非実機Full Suiteで無害であることを確認した。
- Unit境界補正(§2.C)を実装した: Candidate使用量400を維持し、局所`RepairBudget(max_additional_tokens=2799)`(Production `LIVE_REPAIR_BUDGET`は無変更・2800のまま)で1 Token不足を証明する形へ訂正した。
- Claim訂正(§2.D)を実装した: 前回Returnおよび該当Source Commentの「Decode-scale limitationと整合的」という断定的表現を、「Decoder FAILEDとDecoder COMPLETED+Criterion UNKNOWNは区別できておらず、真因未確定」という正確な表現へ訂正した。
- 同一条件の追加実機試験(§2.B)を**指示どおり正確に1回のみ**実行した。結果は前回と同じ不成立形状(`outcome=unknown`, `accepted=False`, `rejected_reason=None`, Plan/Identity層は正常)であり、再現性そのものは確認された。

**主張しないこと(明示的除外、および今回新たに生じた制約)**:
- **Decoder FAILEDかDecoder COMPLETED+Criterion UNKNOWNかの区別は、今回も確定できなかった。** 理由はSourceの欠陥ではなく、後述§5.3のとおり、この2回目実機試験の診断出力(Test-only Observabilityが実際に計算・出力した詳細値)を、Claude自身のLog取得コマンド(`tail -100`)が切り詰めたため、確認できなかった(Claude自身の検証手順上のミスであり、実機やCodeの欠陥ではない)。
- 上記の理由により、指示(§2.B「不成立時: Decoder FAILEDとCOMPLETED+UNKNOWNを区別し、実測値と理由を返す」)を**完全には満たせていない**ことを明示する。実測値のうち、`RepairExecutionResult`由来の粗いFieldは確認できたが、診断Decodeの詳細(execution_state／failure_reason／Criterion内訳／missing・extra ID／Raw Content Digest)はこの回では確認できていない。
- 指示(§3「実機失敗を見て追加試行や即時修復へ進まない」)に従い、**3回目の実機試験は実行していない**。取得ミスの修復のためであっても反復しないことを優先した。
- Selene解決、Phase 9-1 Closure、Decoder変更、Criterion削減、予算再変更は主張しない。

## 2. 対象

[Codex Controller Exact Handoff(2026-09-05 08:25:39 JST)](../handoffs/phase_9_controller_real_32_criterion_rejudge_evidence_disambiguation_exact_handoff_ja_20260905082539.md)、§2(A/B/C/D全項目)。

## 3. Files Changed

| File | 対応項目 | 変更内容 |
|---|---|---|
| `src/margpa_runtime_llm/bootstrap/repair_live_integration.py` | §2.D(Claim訂正) | `LIVE_REPAIR_BUDGET`直前Commentの「consistent with a genuine Decode-scale limitation」という断定的表現を削除し、Decoder FAILED(`JudgeDecodeError`)とDecoder COMPLETED+Criterion UNKNOWN(`_recommendation_from_criterion_results()`がCriterion単位のunknownをRecommendation UNKNOWNへ写像する経路)という2つの異なる原因を`outcome=unknown`だけでは区別できないことを明記し、「真因は未確定」へ訂正。Production Decoder/Contract自体(`judge_output_decoder.py`)は無変更。 |
| `tests/unit/bootstrap/test_repair_live_integration.py` | §2.C(Unit境界補正) | `test_the_2800_token_budget_is_exceeded_by_exactly_one_token_and_rejected`を全面書換。Candidate使用量を現実的な400(`_REPAIR_MAX_NEW_TOKENS`)へ変更、Production `LIVE_REPAIR_BUDGET`(2800)は変更せず、局所`RepairBudget(max_additional_tokens=2799)`で32×75=2400が1 Token不足になることを証明。Production Budgetが変異していないことをTest自身でAssertする行を追加。 |
| `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` | §2.A(Observability)、§2.B(追加実機試験)、§2.D(Docstring訂正) | `test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget`へ、失敗Assertより前に実行するTest-only Observability Blockを追加(実`max_new_tokens`、`finish_reason`、Prompt/Completion Token、生成時間、Raw Content長とSHA-512、同一Raw Contentを実`decode_judge_output()`(生の、Fail-closedでない版)へ1回通した診断結果——`execution_state`、`JudgeDecodeError.reason`、Recommendation、Criterion内訳(pass/deviation/unknown数)、期待32 IDとのmissing/extra差分)。Module DocstringのGolden Path更新部にあった同様の断定的表現を訂正し、本Handoffによる訂正の経緯を追記。 |

## 4. Files Deliberately Not Changed

- `src/margpa_runtime_llm/modules/evaluation/application/judge_output_decoder.py`(Production Decoder/Contract) — 無変更。診断は同一Raw ContentをTest側で再Decodeするだけ。
- Selene関連一式、不正JSON限定リトライ機構、Schema変更、Criterion削減、予算再変更(`LIVE_REPAIR_BUDGET`は2800のまま)、Batching — 無変更。
- IR-R5-01 Planner Failure分類、IR-R5-02 Gemma Golden Path、Gemma Schema Field順序修正 — 受理済みのため再設計・再実装なし。
- Frontend一式 — 今回未編集。
- `docs/project/shared/unresolved_work/current_unresolved_findings_registry_ja.md`、`docs/project/phases/phase_9/phase_index_ja.md` — 直接編集していない。
- 旧Return(`phase_9_claude_normal_32_criterion_rejudge_budget_2800_exact_return_ja_20260905081933.md`)・旧Recovery — 上書きしていない(append-only)。誤った断定は本Returnと該当Source Commentで訂正した。

## 5. Real Evidence

### 5.1 §2.A — Test-only Observabilityの実装確認

対象File Ruff・Canonical Mypy・非実機Full Suiteで、Observability追加自体がProduction Codeへ悪影響を与えていないことを確認した(§6)。診断Decode呼出しは`decode_judge_output()`(生、Fail-closedでない版)を直接使用し、`JudgeDecodeError`を捕捉して`.reason`を取得する構造になっている(Source確認済み、後述§5.3のとおり今回の実行では出力値そのものの確認に至らなかった)。

### 5.2 §2.C — Unit境界補正

`test_the_2800_token_budget_is_exceeded_by_exactly_one_token_and_rejected`を実行し、**PASS**を確認(Unit Suite単体38 passed、§6)。局所`RepairBudget(max_additional_tokens=2799)`使用時のみ1 Token不足で拒否され、Production `LIVE_REPAIR_BUDGET.max_additional_tokens`が2800のまま変異していないことをTest自身のAssertで確認した。

### 5.3 §2.B — 追加実機試験(正確に1回)、および今回判明したEvidence取得上の制約

`test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget`を、Observability追加後、前回と同一条件(Main Qwen context=16384でRepair Candidate生成、Gemma context=8192で実109 Corpusから通常選択した同一32 Criterionを同一Frozen集合のままRejudge)で**追加で正確に1回**実行した。

```text
[FACT] 実行コマンド: `./.venv/bin/python -m pytest
       "tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py::
       test_a_real_normal_32_criterion_selection_repair_on_main_rejudge_on_gemma_within_the_2800_budget"
       -q -m model_smoke -s` を実行し、出力を `tail -100` へPipeした(Claude自身の
       手順上の誤り——後述)。
[FACT] 結果: 前回(20260905081933 Return記載)と同一形状で不成立。
       request_id='real-32-criterion-rejudge-2'(前回とは異なるRequest ID、
       同一Modelを再Loadした別Runであることを明示)。
       outcome='unknown'、accepted=False、new_turn_id=None、
       presented_content=None、rejudge_model_identity=
       'judge.gemma-4-e2b-it-q4-0'、rejudge_role='independent_artifact'。
       rejected_reason はPytestの通常のRepr省略により直接読み取れなかったが、
       表示された省略Patternは前回と同じ形("r...False")であり、
       `attempt_live_repair()`のSource上、accepted=Falseかつこの経路に
       至る場合は`rejected_reason=None`(事前Typed拒否ではなく、事後の
       Rejudge評価Decode後の未Accept経路)であることがCode上確定している。
[FACT] 上記2つのHard Assert(`rejected_reason not in {budget_insufficient,
       budget_exceeded}`、Gemma Identity一致)は、失敗Assertより前に
       PASSしている(Assertion Traceback上、失敗箇所は
       `assert result.accepted is True`であり、それより前の2つのAssertは
       通過済み)——Plan/Budget層は今回も正常に機能し、正しいGemma
       Identityも今回も確認された。
```

**今回判明したEvidence取得上の制約(正直な報告)**: 本Testの新設Observability Blockは、`assert result is not None`より前に無条件で実行されるPrint文で、`finish_reason`・実Token数・生成時間・Raw Content長とSHA-512・診断Decodeの`execution_state`/`failure_reason`/Recommendation/Criterion内訳/missing・extra IDを全て出力する構造になっている(Source上確認済み)。しかし、Claude自身が実行結果を`tail -100`へPipeして確認したため、この診断Print行(pytestの"Captured stdout call"Sectionに出力されたはずの実測値)が、Traceback以前に出力された分だけ切り詰められ、**確認できなかった**。これはCode・実機の欠陥ではなく、Claude自身のLog取得手順のミスである。

Handoffの明示的禁止事項「実機失敗を見て追加試行や即時修復へ進まない」に従い、このミスを修復する目的であっても**3回目の実機試験は実行していない**。Observability自体はCodeとして正しく実装され、次に実機試験が承認される際には(出力を`tee`等でFile保存する等、切り詰めない方法で)実測値を確実に取得できる状態のまま保持している。

## 6. Focused／Static Verification

- 対象File Ruff: `./.venv/bin/ruff check src/margpa_runtime_llm/bootstrap/repair_live_integration.py tests/unit/bootstrap/test_repair_live_integration.py tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py` → **All checks passed**。
- Canonical Mypy: `./.venv/bin/mypy src tests` → **43 errors, 4 files**(既存Baseline維持、新規Errorなし)。
- Unit Suite単体: `tests/unit/bootstrap/test_repair_live_integration.py` → **38 passed**。
- Backend非実機Full Suite: `./.venv/bin/python -m pytest -q -m "not model_smoke"` → **2316 passed, 30 deselected**(前回と同数、Test構成の純増減なし)。
- 実機Model Smoke(対象Testのみ、追加で1回): **1 failed**(§5.3のとおり、粗いResult形状は確認、詳細診断値は取得ミスにより未確認)。他の既存実機Testは指示により再実行していない。
- Frontend: 今回未変更のため再実行していない。

## 7. Internal Review(2回、観点の異なる完全別Pass)

### Review A — Handoff §2 A/B/C/Dへの適合性

- [OK] §2.A: Observabilityを7項目全て実装し、Production Decoder/Contractを変更していないことをGrep・Diffで確認した。
- [PARTIAL] §2.B: 追加実機試験を指示どおり正確に1回実行し、不成立時に反復・即時修復・Criterion削減・予算変更へ進んでいない。ただし「Decoder FAILEDとCOMPLETED+UNKNOWNを区別し、実測値と理由を返す」という要求は、Claude自身のLog取得ミスにより**完全には満たせていない**(§5.3)。
- [OK] §2.C: Candidate 400維持、局所Budget 2799、Production Budget無変更をTest自身で確認する形に訂正した。
- [OK] §2.D: 前回Returnと該当Source Commentの断定的表現を、新規Return(本File)と該当Source Comment自体の訂正で正した(旧Return/Recoveryは上書きしていない)。

### Review B — 手続き・Regression・Evidence整合(自己批判的Pass)

- [OK] Git: Read-onlyのみ、`git status`で意図しない変更がないことを確認した。
- [OK] Append-only: 新規Docs2件(本Return・Recovery)は新規Path、既存Handoff/History上書きなし。
- [OK] 禁止事項: JSON Retry、Decoder変更、Schema変更、Criterion削減、予算再変更、Batching、Selene、Frontend、Phase 9-2/9-3、Closure、Git変更のいずれも行っていない。
- [自己指摘] 実機試験の出力取得手順(`tail -100`)が、新設Observabilityの実測値そのものを確認できない形で実行結果を切り詰めてしまった。これは今回のRework自体の実装ミスではなく、Claudeの検証コマンドの選択ミスである。3回目の実機試験でこれを「修復」することはHandoffの明示的禁止(反復禁止)に反するため行っていない——結果として、本Round全体としては§2.Bの目的(原因分離)を実機Evidenceとして完成させられなかったことを、Maximum Claimと本SectionでHonestに報告する。
- [OK] 2回目実機試験は前回と異なるRequest IDで実行され、同一Model再Loadによる独立したRunであることを確認した(Modelの状態が前回のまま持ち越されたものではない)。
- [OK] 実機Trial完了後、`finally`Blockで両Model Unload済み、残存Load・稼働Processなし(2回とも同一の`finally`構造)。

## 8. Open Findings／True Stop

Open Findingのまま(True Stopではない、Codex Controller判断待ち):

1. **Decoder FAILED vs COMPLETED+Criterion UNKNOWNの区別**: 今回も未確定。原因はSourceではなく、Claude自身のLog取得ミス(§5.3、§7 Review B)。Observability自体はCode上正しく実装され、次回実機試験(いつ承認されるとしても)で確実に取得できる状態。
2. **実機32 Criterion Rejudge**: 2回連続で同一形状の不成立(`outcome=unknown`, `accepted=False`)——Plan/Budget層・Gemma Identityは2回とも正常。再現性は確認されたが、根本原因(Decode失敗か、Criterion単位のUnknownか)は未確定のまま。
3. **Selene**: 未解決のまま(前回Returnと同じ、今回変更なし)。
4. **Mypy 43 errors/4 files**: 既存Baseline、今回のScope外。
5. **Frontend再検証**: 今回変更なしのため未実施。

## 9. Action Inventory

**実行した**: Test-only Observability(§2.A、7項目)の実装、Unit境界補正(§2.C)、Claim訂正(§2.D、Source Comment・Test Module Docstring双方)、追加実機試験(§2.B)を指示どおり正確に1回実行、対象File Ruff・Canonical Mypy・非実機Full Suite・Unit Suite単体の実行、本Return・Recovery新規File作成。

**実行しなかった**: 実機試験の3回目実行(Log取得ミスの修復目的であっても)。Decoder・Schema・予算・Criterion数への変更。Selene・JSON Retry・Batching・Frontend・Phase 9-2/9-3・Closureへの着手。Git Add/Commit/Push等の変更操作。既存Mypy 43件の無断修復。旧Return/Recoveryの上書き。

**Temporary Artifact／Active Process／Model Load**: 2回目実機Trial完了後、既存の`finally`BlockによりMain/Gemma両Model Unload済み、残存Load・稼働Processなし。

## 10. Exact Next Action for Codex Controller

1. §2.A Test-only Observabilityの実装(Production Decoder/Contract無変更であること含む)を確認する。
2. §2.C Unit境界補正(Candidate 400維持、局所Budget 2799、Production Budget無変更)を確認する。
3. §2.D Claim訂正(旧断定的表現の訂正内容)を確認する。
4. §2.B追加実機試験について、Claude自身のLog取得ミスにより「Decoder FAILED vs COMPLETED+UNKNOWN」の区別が今回も実機Evidenceとして得られなかったことを踏まえ、次のStep(Observabilityの実装自体は完了しているため、Log取得手順を改めた上での3回目試行をUser判断で改めて許可するか、Fixture水準の成立とPlan/Budget層の実機再現性確認をもって本項目を一旦区切りとするか)をUserとともに判断する。

本Returnの提出をもって停止する。Phase Closure、次Phaseへの着手、追加のGit操作は行わない。Codex Controller Independent Reviewを待つ。
