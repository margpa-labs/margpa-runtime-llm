# Phase 9-1 §7④ — Gemma不正JSON局所修復の有界試行と否定的結果 未解決Snapshot

```yaml
document_id: phase_9_1_gemma_local_prompt_repair_attempt_bounded_negative_result_snapshot_20260905002008
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-05 00:20:08 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

Controller Review §7④の指示: 「通常Main＋Gemmaの不正JSON診断・局所修復と実機正経路」を、Prompt／Output契約の既存範囲・許可済みArtifactに限定して試みる。仮説・成功条件・既存Logを先に確認し、有界化する。「Gemmaの能力限界・Project側に欠陥なしと先に断定しない」ことが明示的に求められている。

## 2. 仮説と成功条件(試行前に確定)

```text
[仮説] Gemma 4 E2Bが`evidence_refs`配列の閉じ`]`を一貫して落とす
       (`phase_9_1_gemma_evidence_refs_json_defect_absolute_log_paths_
       and_causal_scope_correction_snapshot_ja_20260905001646.md`で
       5/5再現確認済み)のは、Prompt内のRuleに配列を閉じることへの
       明示的な注意喚起がないためである可能性がある。

[修正] Prompt Template(`config/judge_templates/gemma_4_e2b/
       project_derived_multi_criterion_prompt_v1.txt`)のRules末尾へ、
       「配列を閉じてからObjectを閉じること。閉じ括弧の対応を数えて
       確認すること」という第5項を追加する(Decoderの厳密性緩和・
       Response Schema自体の変更は行わない。Prompt文言の追加のみ)。

[成功条件] 修正後Promptで、誤答Candidate・正答Candidateそれぞれについて
       実機Dispatchが`provider_state=ACTIVE`(有効なJSON、Decode成功)
       に到達すること。

[試行上限] 誤答1回・正答1回、計2回。この上限で成立しなければ、
       追加のPrompt変更は行わず未成立として維持する。
```

## 3. 実施内容(実装済み)

Prompt Templateへ第5項を追加した。実際の変更差分:

```diff
 4. If evidence is insufficient, use disposition=unknown for that criterion.
+5. Every array you open with [ must be closed with ] before its containing object is closed with }. Before you finish, count your opening and closing brackets and braces and make sure they match.
```

Template本文のSHA512変更に伴い、`config/judge_templates/gemma_4_e2b/manifest.json`の`derived_template_sha512`と`project_contract_digest_sha512`を、`SelenePromptAdapter`と同一のDigest計算手順で再計算し更新した。`SelenePromptAdapter.preflight_contract()`が正しく検証を通過することを確認済み(Digest不整合なし)。関連する既存Test(Gemma／Selene関連45件)も全PASSを確認した——本変更はProject管理下のPrompt Templateへの局所的な文言追加であり、Native Library更新・Download・新Resource Gate・Decoder変更のいずれにも該当しない。

## 4. 実機結果(有界2回、否定的)

```text
[FACT] 誤答Candidate(pytest経由、Main+Gemma同時Load): 修正後も
       provider_state=failed、failure_reason=malformed_output:...
       (前回と同一形状)。
[FACT] 誤答Candidate(生Content直接確認、repro2診断Script経由): 生JSON
       Textが修正前と完全に同一(`"evidence_refs":["...Paris."}]}"`、
       閉じ`]`欠落)。completion_tokens=88(修正前も88)。
[FACT] 正答Candidate(生Content直接確認、repro3診断Script経由): 同じく
       修正前と完全に同一の欠落Pattern。completion_tokens=92(修正前も92)。
```

Log(Task所有隔離Process、絶対Path):

```text
/private/tmp/claude-501/-Users-yukitakagi-Documents-pseudo-root-99-ps-Main-Creating-Objects---20260219-MARGPA-RUNTIME-LLM-margpa-runtime-llm/bccb7444-2530-4d4f-bbda-033f06c5df80/scratchpad/wu03_gemma_repro/run_post_prompt_fix_wrong_answer.log
/private/tmp/claude-501/-Users-yukitakagi-Documents-pseudo-root-99-ps-Main-Creating-Objects---20260219-MARGPA-RUNTIME-LLM-margpa-runtime-llm/bccb7444-2530-4d4f-bbda-033f06c5df80/scratchpad/wu03_gemma_repro/run_post_prompt_fix_correct_answer.log
```

## 5. 結論(否定的結果、成功条件は不成立)

有界2回の試行いずれも成功条件(`provider_state=ACTIVE`到達)を満たさなかった。生出力Textが修正前と1文字も変わらないことから、この特定のPrompt変更(閉じ括弧への注意喚起Rule追加)はGemma 4 E2Bの出力に測定可能な影響を与えなかったと判断する。

この結果は「Gemmaの能力限界」を確定させるものではない——今回試したのは1つの狭い仮説(Rule文言追加)のみであり、他のPrompt構造変更(例: Schema自体の簡略化、`evidence_refs`の指示文言の書き換え、Few-shot例の追加)は未検証のまま残る。ただし、今回の有界試行budgetは使い切ったため、追加のPrompt変更試行はこのTaskでは行わない。

## 6. 対応方針(未実装、提示のみ)

- Prompt Rule第5項の追加自体は、副作用がなく(既存Test全PASS、Digest整合)、一般論として有用な指示であるため、今回のChangeは**維持**する(Revertしない)。ただし、これが実際にGemmaの不正JSON問題を解決したという主張はしない。
- 今回検証していない別のPrompt改善仮説(Schema簡略化、Few-shot例追加等)は、User／Codexが優先順位を判断した上で、別Taskとして有界試行することを提案する。
- OBSERVE／ENFORCE、Repair→同条件Rejudge→改善回答の採用、Main Governance ENFORCEの一連の実機成立は、Judge Dispatch自体がACTIVE状態へ到達しない限り検証不能であり、今回も未達のまま維持する。

## 7. Status

```text
Current Point            : 局所修復(Prompt Rule追加)を有界2回試行し、
                            否定的結果(効果なし)を確認。Prompt変更
                            自体は副作用なく維持。OBSERVE／ENFORCE等の
                            下流検証は、Judge Dispatch非成立のため
                            今回も実施不能。
Files Created／Modified  : 本File(新規作成)、
                            config/judge_templates/gemma_4_e2b/
                            project_derived_multi_criterion_prompt_v1.txt
                            (Rule追加)、同manifest.json(Digest更新)。
                            Scratchpad実行Log2件追加。
Validation                : Digest整合確認済み、関連既存Test45件PASS、
                            実機有界試行2回(いずれも否定的結果)。
Open Current Blocker     : Gemma不正JSON欠陥は未解決のまま。今回の
                            有界試行Budgetは使い切った。
Exact Next Route          : Codex Controller Independent Reviewを待つ。
```
