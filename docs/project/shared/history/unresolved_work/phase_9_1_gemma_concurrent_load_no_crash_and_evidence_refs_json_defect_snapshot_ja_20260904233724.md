# Phase 9-1 Controller再Review P3 — Main+Gemma同時Load実機結果 未解決Snapshot

```yaml
document_id: phase_9_1_gemma_concurrent_load_no_crash_and_evidence_refs_json_defect_snapshot_20260904233724
document_type: append_only_unresolved_reclassification_snapshot
document_state: historical_snapshot
language: ja
recorded_at: 2026-09-04 23:37:24 JST
source_current_registry: ../../unresolved_work/current_unresolved_findings_registry_ja.md
decision_authority: user
authority_owner: Nazuna Research
phase: phase_9
program: phase_9_1
phase_9_1_closure: false
```

## 1. Trigger

Controller再Review(`../../phases/phase_9/history/operations/phase_9_1_judge_governance_controller_re_review_ja_20260904224150.md`)§4の指示により、「共通基盤の残件解消後、通常構成のMain＋Gemmaによる実機正経路(OBSERVE／ENFORCE、Repair→同条件Rejudge→改善回答の採用、Main Governance ENFORCE)を確認する」作業を実施した。Userは「Gemmaが正常に使え、後工程に支障がなければSeleneだけ延期する」ことを承認済み。

## 2. 実機Evidence(Task所有隔離Process、4回の有界実行)

対象：`config/profiles/local_macos_arm64.toml`の`[dedicated_role_load_overrides]`に記録されたMain+Selene同時Load Native Crash(`RuntimeError: llama_decode returned -3`、32-Criteria Batch)と同一構成(Main context=16384, Gemma context=8192, ともにgpu_layers=-1)を、Gemmaへ置き換え・Criterion数を1件(有界)に絞って実機確認した。

Log保存先(Scratchpad、Task所有隔離Process):
- `wu03_gemma_repro/run1.log`、`run2.log`(同一有界Criterion、2回連続実行)
- `wu03_gemma_repro/run_diagnostic.log`(誤答Candidate、生Model出力Text直接確認)
- `wu03_gemma_repro/run_accept_case.log`(正答Candidate、生Model出力Text直接確認)
- Pytest実行: `tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py`(1 skipped、下記2.2の理由で意図どおり)

### 2.1 [FACT] Main+Gemma同時Load — Native Crash非再現

4回とも、Main(Qwen3-4B, context=16384, gpu_layers=-1)とGemma(context=8192, gpu_layers=-1)を同一Process内で同時Loadした状態から、Gemmaへ実Dispatch(`SeleneSemanticEvaluator.evaluate()`、有界1 Criterion)を行った。いずれも`RuntimeError: llama_decode returned -3`および他の未捕捉例外は発生せず、`evaluate()`は毎回1.8〜1.9秒で正常にTyped Responseを返した。Seleneの同型構成(ただし32-Criteria Batch)で確定しているNative Crashは、この有界(1 Criterion)条件では非再現である。

**重要な限定**: Criterion数がSeleneのCrash確認時(32件)と異なる(1件)ため、「GemmaはSeleneと違ってCrashしない」という一般的な結論ではなく、「有界(1 Criterion)条件では非再現」という範囲に限定する。32件相当のBatch Sizeでの同時Load再現は今回実施していない(無目的な再試行を避けるため、既存Selene Crash Evidenceで確立済みの条件を追試する動機がない)。

### 2.2 [FACT] Gemma自身の出力 — `evidence_refs` JSON閉じ括弧欠落(再現性あり、3/3)

4回中3回(run1/run2/run_diagnostic相当の誤答Candidateケース、およびrun_accept_case相当の正答Candidateケース)で、Gemmaの生出力Textを直接確認した。いずれも以下の共通する欠陥が確認された:

```text
"evidence_refs":["official-source | reference.txt: The capital of France is Paris."}]}
```

`evidence_refs`配列の閉じ`]`が欠落しており(`"...Paris."]}]}`となるべきところが`"...Paris."}]}`)、構文的に不完全なJSONとなっている。`finish_reason=stop`(Token Budget超過によるTruncationではない、`completion_tokens`は`max_new_tokens=1000`に対し88〜92のみ消費)であり、Gemma自身が意図してこの形で出力を終えている。誤答・正答いずれのCandidateでも同一の欠落パターンが再現し、`reasoning`Fieldの内容自体は両ケースとも意味的に正確(誤答を正しく`needs_repair`/`deviation`、正答を正しく`accept`/`pass`と判定)である。

IR-01修正(`../../phases/phase_9/history/operations/phase_9_1_judge_governance_rework_controller_review_ja_20260904191646.md`由来)により、この不完全なJSONは`JudgeDecodeError`としてTyped Failure(`malformed_output`)へ正しくFail-closedされ、ENFORCE下ではSafe Fallbackへ収束する(誤った回答が表示されることはない)。Fail-closed Contract自体は意図どおり機能している。

## 3. 解釈と結論

```text
[結論1] Main+Gemma同時Load自体は、有界(1 Criterion)条件でNative Crashを
        起こさない。Selene固有(または少なくともBatch Size依存)の問題で
        ある可能性が高まったが、Gemmaの32件相当Batchでの同時Load挙動は
        未確認であり、断定はしない。

[結論2] Gemma 4 E2B自身に、`evidence_refs`配列へ実際の引用文字列(空でない
        Evidence参照)を含める際、閉じ`]`を一貫して欠落させる出力品質上の
        欠陥がある(3/3再現、誤答・正答の両ケースで同一パターン)。これは
        Gemma自身のJSON Schema追従能力の限界であり、本ProjectのDecoder／
        Dispatch層のBugではない(Fail-closed Contractは正しく機能した)。

[結論3] 上記2により、「Gemmaが正常に使える」というUser承認済み延期条件は
        今回未成立。Judge Dispatch自体は安全側(Fail-closed)に倒れている
        が、ENFORCE ACCEPT／Repair→Rejudge→改善回答採用というGolden Path
        の実機成立は、この`evidence_refs`欠陥がある限り実証できない
        (Evidence Contextを伴う実運用のCriterion評価では、ほぼ必ず
        `evidence_refs`に非空文字列が含まれるため)。

[結論4] Seleneの延期(先送り)条件は今回も不成立のまま。Selene固有の問題
        (Main同時LoadでのNative Crash)とGemma固有の問題(evidence_refs
        JSON欠陥)は別種であり、後者の解消をもって前者を代替できない。
```

## 4. Registry反映(提案、正本編集はしない)

- **新規UF-P9-010**（提案）— Gemma 4 E2B、`evidence_refs`配列JSON閉じ括弧欠落。severity: P2(Fail-closedにより安全側、Golden Path実機成立をBlockする非Blocking Finding)。再現: 3/3(本Snapshot§2.2)。原因: Gemma自身の小型Model出力品質(本ProjectのCode欠陥ではない)。
- 既存UF-P9-003(Local Mac向け軽量LLM-as-a-Judge候補)の現況注記に、「GemmaはMain同時Load Native Crashを起こさない(有界条件)が、`evidence_refs`JSON欠陥(UF-P9-010)によりGolden Path実機成立は今回も未達」を追記候補とする。
- Selene関連のOpen Finding(WU-01)は、本Snapshotの結果によって変更しない(結論4のとおり)。

Registry本体(`current_unresolved_findings_registry_ja.md`)への反映はStable文書のため直接編集しない。次回Registry更新作業時にこの提案を反映するかはUser／Codex判断とする。

## 5. Status

```text
Current Point            : Main+Gemma同時Load(有界1 Criterion)はNative Crash
                            非再現。Gemma自身のevidence_refs JSON欠陥
                            (3/3再現)によりGolden Path実機成立は未達。
                            Selene延期条件は今回も不成立のまま。
Files Created／Modified   : 本File(新規作成)、
                            tests/integration/test_real_local_main_gemma_concurrent_dispatch_smoke.py
                            (新規実機Test、1件Skip=意図どおりの安全側挙動)、
                            Scratchpad配下の実行Log 4件。Source本体の変更なし。
Validation                : 実機4回実行、Log保存済み(上記2節)。
Open Current Blocker     : Gemma自身のevidence_refs JSON欠陥(UF-P9-010提案)。
                            Fix Attempt(Prompt再設計等)は本Task範囲外、
                            別Taskとして扱う。
Exact Next Route          : Codex Controller Independent Reviewを待つ。
                            Selene/Gemmaいずれの延期条件も今回は不成立の
                            ため、Selene登録・再調査入口は現状維持のまま
                            継続する。
```
