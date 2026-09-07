# Phase 9-1 IR-R3-04 — GemmaのJSON欠陥Log絶対Path化と因果Scope訂正 未解決Snapshot

```yaml
document_id: phase_9_1_gemma_evidence_refs_json_defect_absolute_log_paths_and_causal_scope_correction_snapshot_20260905001646
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-05 00:16:46 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
supersedes_snapshot: phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_ja_20260904233724.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

Codex Controller独立Review(`../../../phases/phase_9/history/operations/phase_9_1_controller_p1_p2_p3_return_review_and_delta_rework_ja_20260904235434.md`)IR-R3-04の指摘: 前回Snapshot(`phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_ja_20260904233724.md`)が生Logを相対Scratchpad名(`wu03_gemma_repro/run1.log`等)でしか示しておらず、Controllerが実際に読めなかった。また同Snapshotの因果記述(「Gemma自身の限界」「本Projectのコード欠陥ではない」「意図して出力を終えている」)が、`finish_reason=stop`と反復した不正JSON形状という観測事実だけでは支持できない、過大な断定だった。本Snapshotはこの2点を訂正する。旧Snapshotは上書きせず、本Fileが正本として参照を引き継ぐ。

## 2. Log絶対Path(訂正)

Task所有隔離Process(このSession)のScratchpad配下、実Machine上の絶対Path:

```text
/private/tmp/claude-501/-Users-yukitakagi-Documents-pseudo-root-99-ps-Main-Creating-Objects---20260219-MARGPA-RUNTIME-LLM-margpa-runtime-llm/bccb7444-2530-4d4f-bbda-033f06c5df80/scratchpad/wu03_gemma_repro/
```

同ディレクトリ配下の各File:

| File | 対応Script | 内容 |
|---|---|---|
| `repro1_main_gemma_concurrent_bounded.py` | (Script本体) | Main+Gemma同時Load、有界1 Criterion、`evaluate()`の結果を出力するだけの最小Script |
| `run1.log` | `repro1_main_gemma_concurrent_bounded.py`実行1回目 | 誤答Candidate("Tenon")。`evaluate()`は1.8秒で復帰、`provider_state=failed`、`failure_reason=malformed_output:...` |
| `run2.log` | `repro1_main_gemma_concurrent_bounded.py`実行2回目(同一Script再実行) | run1.logと同一Candidate・同一結果(再現性確認) |
| `repro2_raw_content_diagnostic.py` | (Script本体) | run1/2で観測された`malformed_output`の生Model出力Textを直接確認するための最小Script(誤答Candidate) |
| `run_diagnostic.log` | `repro2_raw_content_diagnostic.py`実行 | 誤答Candidateに対する生JSON Textを出力。`evidence_refs`配列の閉じ`]`欠落を直接確認 |
| `repro3_raw_content_accept_case.py` | (Script本体、`repro2`の`candidate_answer`を正答へ変更した派生版) | 正答Candidateでの生Model出力Textを直接確認するための最小Script |
| `run_accept_case.log` | `repro3_raw_content_accept_case.py`実行 | 正答Candidateでも同一の閉じ`]`欠落Patternを確認 |

**注記**: このディレクトリはClaude Codeの Session専用Scratchpadであり、Session終了後の永続性は保証されない。Controllerが本Reviewサイクル内に読む場合は上記絶対Pathで到達可能である想定だが、時間が経過した場合は失われている可能性がある(Session性質上の制約であり、本Task側で回避策はない)。

## 3. 追加の第5試行(本Rework中に実施)

IR-R3-04対応でTest Fileを書き換えた際、実機Testを1回再実行した(`uv run pytest tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py -m model_smoke`)。結果は同一の`malformed_output`欠陥(`provider_state=failed`)であり、Nativeクラッシュは今回も再現しなかった。これで合計5回の実機試行(有界1 Criterion)のうち、5回とも同一のJSON欠陥形状、0回のNativeクラッシュという結果になった。

## 4. 因果Scopeの訂正(重要)

前回Snapshotの以下の記述を訂正する:

```text
[訂正前] 「Gemma自身のJSON整形欠陥」「本ProjectのCode欠陥ではない」
[訂正前] 「Gemma自身が意図してこの形で出力を終えている」

[訂正後] 観測できた事実のみを述べる:
  - `finish_reason=stop`であり、`completion_tokens`は`max_new_tokens=1000`の
    上限に対し88〜92のみ消費している(Token上限によるTruncationではない)。
  - `evidence_refs`配列に非空の引用文字列を含めると、5/5の実機試行で
    閉じ`]`が欠落する。
  - `reasoning`Fieldの内容は誤答・正答の両Caseとも意味的に正確である。

これらの観測事実は、Gemma自身のModelとしての出力品質限界を示唆する
一つの仮説とは整合するが、それを確定させるものではない。本Project側の
Prompt Template(`config/judge_templates/gemma_4_e2b/project_derived_
multi_criterion_prompt_v1.txt`)の構造、Response Schemaの指示文言、または
llama.cpp/llama-cpp-pythonのGemma固有のChat Template・Tokenizer処理
(Backend側)が寄与している可能性は、今回のEvidenceでは排除できていない。
「Modelの限界」と断定するには、少なくとも(a)Prompt Templateを変えた場合の
挙動比較、(b)他のGemma系実装／Backendでの再現有無、のいずれかの追加調査が
必要であり、今回はいずれも実施していない。
```

## 5. 結論(変更なし、根拠のみ訂正)

「Gemmaが正常に使える」という延期条件は今回も未成立、という結論(前回Snapshot §5〜7の内容)自体は変更しない。変更するのは、その根拠の言明方法(断定的な因果Claimを避け、観測事実と未確定事項を分離する)のみである。

## 6. Test Oracleの修正(関連、実装済み)

`tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py`の`is_the_tracked_gemma_evidence_refs_json_defect()`を、`provider_state=FAILED`かつ`failure_reason`が`malformed_output:`で始まる場合のみ真となるよう厳密化した(以前は`provider_state != ACTIVE`という広すぎる条件で、Nativeクラッシュ由来の`UNAVAILABLE`も誤って同じSkip扱いにしていた)。Fixture負例(Controllerの`-3`注入Probeを実Dispatch Engine経由で再現)を含む6件のOracle単体Testを追加し、これらは`model_smoke`Markerなしで通常実行される。詳細は同TestFileのDocstringを参照。

## 7. Status

```text
Current Point            : 生Log絶対Pathを本Fileへ記録、因果記述を観測
                            事実のみへ訂正。実機試行は合計5回(5/5同一
                            malformed_output欠陥、Nativeクラッシュ0回)。
                            Test Oracleを厳密化しFixture負例で検証済み。
Files Created／Modified   : 本File(新規作成、旧Snapshotは上書きせず)、
                            tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py
                            (Oracle厳密化、Fixture負例Test追加、実機Test
                            は6件Deselected＋1件Skip=意図どおり)。
Validation                : Unit相当のOracle Test 6件PASS、実機Test 1件
                            SKIP(意図どおり)。
Open Current Blocker      : Gemma`evidence_refs`JSON欠陥の真因は依然
                            未確定(Model／Prompt／Backendいずれの寄与も
                            排除できていない)。
Exact Next Route          : Codex Controller Independent Reviewを待つ。
```
