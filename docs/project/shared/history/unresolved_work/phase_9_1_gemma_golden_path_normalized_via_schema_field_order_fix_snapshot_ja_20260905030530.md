# Phase 9-1 IR-R4 §4/§5 — Gemma Golden Path正常化(Schema Field順序局所修復)とSelene延期成立 Snapshot

```yaml
document_id: phase_9_1_gemma_golden_path_normalized_via_schema_field_order_fix_snapshot_20260905030530
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-05 03:05:30 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
supersedes_negative_result: phase_9_1_gemma_local_prompt_repair_attempt_bounded_negative_result_snapshot_ja_20260905002008.md
```

## 1. Trigger

Codex Controller独立Review(`../../../phases/phase_9/history/operations/phase_9_1_controller_ir_r3_return_review_and_delta_rework_ja_20260905003507.md`)§4/§5の指示: 「Gemmaは別仮説を明示して、記載の上限内で局所修復する」「最初の別仮説は最大2試行で判定。正常化した場合のみ既承認のOBSERVE／ENFORCE・同条件Repair→Rejudge→採用・Main Governance経路の確認へ進む」。前回(20260905002008 Snapshot)の第1仮説(閉じ括弧確認Rule追加)は否定的結果だった。本Snapshotは第2の異なる仮説とその結果を記録する。

## 2. 第2仮説(前回と異なる、試行前に確定)

```text
[観測事実の再検討] 5/5の全実機試行で、応答末尾の「連続4個の閉じ構造Token」
       (evidence_refs配列の`]`→Criterion Entry Objectの`}`→
       criterion_results配列の`]`→外側Objectの`}`)のうち、常に最初の`]`
       (evidence_refs自身の配列閉じ)だけが欠落していた。

[仮説2] 2B・量子化という小型ModelであるGemma 4 E2Bは、新規Contentを挟まず
       連続する複数の閉じ構造Tokenを続けて生成することに構造的な弱さが
       あり、閉じ括弧そのものへの一般的な注意喚起(第1仮説)では改善しない
       可能性がある。evidence_refs(配列)をCriterion Entry内の最後の
       Fieldにしない(直後に他のFieldが続く形にする)ことで、連続する
       閉じTokenの並びを4個から3個へ減らせば、欠落が解消する可能性がある。

[成功条件] 誤答Candidate・正答Candidateそれぞれについて、変更後Schemaで
       生成されたJSON全体が構文的に有効(json.loadsが例外を出さない)で
       あること。

[試行上限] Source変更前の検証Scriptで誤答1回・正答1回、計2回。
```

## 3. 検証結果(有界2回、Source変更前、肯定的)

Task所有隔離Process、Main+Gemma同時Load(既存許可済み構成)、`SelenePromptAdapter.build()`と同一のSchema構築ロジックを複製し、`evidence_refs`を`reason_code`より前へ並べ替えただけのScriptで実行:

```text
[FACT] 誤答Candidate: finish_reason=stop, completion_tokens=88、
       生JSON全体が構文的に有効(json.loadsが成功)。
[FACT] 正答Candidate: finish_reason=stop, completion_tokens=103、
       生JSON全体が構文的に有効(json.loadsが成功)。
```

Log(Task所有隔離Process、絶対Path):
`/private/tmp/claude-501/-Users-yukitakagi-Documents-pseudo-root-99-ps-Main-Creating-Objects---20260219-MARGPA-RUNTIME-LLM-margpa-runtime-llm/bccb7444-2530-4d4f-bbda-033f06c5df80/scratchpad/wu03_gemma_repro/run_alt_hypothesis_evidence_refs_reordered.log`

## 4. 正式実装(Source変更、Decoder無変更)

以下2箇所のSchema構築コードで、Criterion Entry内の`evidence_refs`Fieldを最後から`reason_code`の前へ移動した(Field順序のみ、`JudgeCriterionResult`の必須Field・型は無変更、Decoderの厳密性は変更していない):

- `src/margpa_runtime_llm/adapters/evaluation/selene.py`の`SelenePromptAdapter.build()`(Selene／Gemma共有のSchema構築Dict)。
- `src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py`の`_semantic_response_instruction()`(Main-shared用、Repair Rejudgeの現行Prompt含む)。

Gemma固有ではなくSelene／Main-sharedとも共有される箇所であるため、両方に同一の修正を適用した(SeleneやMain-selfは元々この欠陥を示していなかったが、Field順序変更自体はDecoderから見て無害であり、一貫性のため両方へ適用した)。Selene用Template File(`config/judge_templates/selene/`)自体は変更していない(Schema自体はPython側で生成されるため、Template File変更・Digest再計算は不要)。

## 5. Golden Path実機検証(修正後、5/5全PASS)

`tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py`にGolden Path実機Test 4件を新規追加し、既存のCrux Test(Native Crash非再現)と合わせて計5件、Main+Gemma同時Load下で実行した:

```text
[FACT] test_main_and_gemma_concurrent_load_never_reproduces_selenes_native_crash: PASSED
       (provider_state=ACTIVE、修正前はSkip扱いだった箇所が今回はPASS)。
[FACT] test_a_real_gemma_observe_run_never_withholds_but_genuinely_judges: PASSED
       (OBSERVE、実Gemma Dispatch、execution_state=completed)。
[FACT] test_a_real_gemma_enforce_run_accepts_a_genuinely_correct_candidate: PASSED
       (ENFORCE、正答Candidateを実Gemmaが正しくaccept)。
[FACT] test_a_real_gemma_enforce_repair_run_uses_the_same_condition_rejudge_and_adopts_the_improved_answer: PASSED
       (ENFORCE+Repair、実GemmaがDeviationを検出、Main(Qwen)がRepair候補生成、
       同一GemmaによるRejudgeで改善回答を採用。Hard Assertion、Skipなし)。
[FACT] test_a_real_gemma_main_governance_enforce_run_authorizes_and_persists_the_repair: PASSED
       (Judge側Repair Mode=OFF、Main Governance自身のENFORCE判断のみで
       実GemmaによるRepair認可・改善回答採用が成立)。
```

Backend全体Regression: 2316 passed(既存Baseline維持、Schema Field順序変更による回帰なし)。Mypy(`src tests`): 43 errors/4 files(既存Baseline維持)。

## 6. Selene延期の成立(User事前承認済み条件、今回初めて両方充足)

Userは以前(このRework Chainの前々Round)、「Gemmaが正常に使え、後工程に支障がなければSeleneだけ延期する」ことを承認済みである。今回:

```text
[条件1: Gemmaが正常に使える] 成立。OBSERVE／ENFORCE／Repair→同条件Rejudge
       →採用／Main Governance ENFORCEの4シナリオ全てが実機Gemmaで実証
       された(本Snapshot§5)。

[条件2: 後工程がSelene固有機能に依存しない] 成立。`SeleneRoleAdapter`は
       Docstringで明示的に「Gemmaへprovider_labelのみ変えて無変更で
       再利用」と規定されており、`_run_selene_dispatch`はDuck Typing
       (`.semantic_evaluator`属性の有無)でDispatchするためProvider
       非依存(前々Round確認済み、Source Read)。かつ今回、実Gemmaによる
       Main Governance ENFORCE経路(本Snapshot§5の4件目)が実機で成立した
       ことにより、この非依存性が実装Level・実機Level双方で確認された。
```

両条件が今回初めて同時に成立したため、User事前承認に基づき、**Seleneを延期候補として登録する**。「Seleneも完成」への言い換えは行わない——延期はUser自身の判断による完了条件の変更であり、Selene自体の未解決状態(Main同時Load時のNative Crash、原因未確定)は変更しない。

### 6.1 Selene再調査入口(登録)

- 未解決状態: `config/profiles/local_macos_arm64.toml`の`[dedicated_role_load_overrides]`コメント、および本Task内の複数Snapshot(`wu01_selene_repro/`配下Log含む)に、Main+Selene同時Load時の`RuntimeError: llama_decode returned -3`(Native Fatal Error)が2/2再現、Selene単独Loadでは0/1という実機Evidenceが保存済み。
- 再調査の入口: 上記config内Comment、および`docs/project/phases/phase_9/history/operations/`配下のWU-01関連Recovery Docが、再調査時の起点となる。
- 再調査条件(未実施、提示のみ): Gemmaで有効だった「Main+Dedicated Role同時Load」自体は問題なく、Seleneの32-Criteria BatchというLarge Request Shape、またはSelene固有のModel Architecture／gpu_layers設定が真因である可能性が高い(Gemmaの有界1 Criterion Dispatchでは同一構成でCrashしなかったため)。次の再調査があるとすれば、Seleneに対しても有界(1〜数Criteria)のBatch Sizeで同一実験を行うことが、最小の次Stepとして考えられる。

## 7. Status

```text
Current Point            : Gemma不正JSON欠陥の第2仮説(Schema Field順序
                            変更)が有界2回の検証で肯定的結果、正式Source
                            実装、Golden Path実機5/5全PASS。User事前承認
                            条件が今回両方充足したため、Seleneを延期候補
                            として登録(未解決状態自体は変更なし)。
Files Created／Modified  : 本File(新規作成)、
                            src/margpa_runtime_llm/adapters/evaluation/selene.py
                            (Schema Field順序修正)、
                            src/margpa_runtime_llm/modules/evaluation/application/judge_prompt_builder.py
                            (同上、Main-shared用)、
                            tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py
                            (Golden Path実機Test4件新規追加、Docstring更新)。
                            Scratchpad診断Script・Log1組追加。
Validation                : Backend全体2316 passed、Mypy 43 errors/4 files
                            (Baseline維持)、実機Test5/5 PASS(Main+Gemma
                            同時Load)。
Open Current Blocker     : Selene自体は未解決のまま(延期は完成への
                            言い換えではない)。Gemma不正JSON欠陥の真因
                            (小型Model構造的限界か、他の要因か)は依然
                            確定していない(効果があった修正の理由は
                            仮説どおりと推測されるが、確定的な検証は
                            行っていない)。
Exact Next Route          : Codex Controller Independent Reviewを待つ。
```
