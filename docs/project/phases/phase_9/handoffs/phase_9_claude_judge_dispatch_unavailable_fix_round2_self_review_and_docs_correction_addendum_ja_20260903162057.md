# Phase 9-1 Judge Dispatch "unavailable" Fix — Round 2 Self-Review Exact Return兼Docs訂正Addendum

```yaml
document_id: phase_9_claude_judge_dispatch_unavailable_fix_round2_self_review_and_docs_correction_addendum_20260903162057
document_type: exact_bounded_implementation_return
document_state: candidate_for_controller_review
phase: phase_9
program: phase_9_1
created_at: 2026-09-03 16:20:57 JST
provider: Claude(Bounded Implementation Worker)
authorized_by: User直接指示「一周終わったら、3観点自己レビューして。でfindingあったら
  そのまま直して、でまた3観点自己レビューして。って繰り返しといて。」(自走Loop継続)
in_response_to: handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round1_self_review_exact_return_ja_20260903135915.md
supersedes: none(Append-only。前Round Docの内容は改変しない、本Docは訂正情報を追記
  するAddendumである)
git_action: none
```

## 0. 位置づけ

Round 1のFix(Diagnostic Detail追加)自体に対する3観点Self-Review(Round 2)の
結果と、そこで見つかったDocs側Findingへの対処を記録する。**Round 2ではCode側
Finding は0件だった** — これは2 Round連続でCode Fix自体が独立ReviewをPass
したことを意味する(収束の兆候、§4参照)。

## 1. Round 2 3観点Self-Review結果

### 1.1 Correctness再監査(Round 1のDiagnostic Detail追加を対象) — Finding無し

```text
Round 1で自分自身が行った2つの事前Check(InferenceErrorCode全値に
"cancelled"/"deadline_exceeded"/"malformed"部分文字列が含まれないこと、
他File/Testが正確なfailure_reason文字列に依存していないこと)を、独立した
Agentが再導出し、両方ともCONFIRMED(裏付け成立)。

追加でFrontend(frontend/src/)まで遡り、失敗Reasonの実際の型境界
(LlmJudgeResponse.failure_reason: JudgeFailureReason Enum、判定済み
Categoryのみ)を実際に追跡し、生のDiagnostic文字列がUIへ漏れないことを
実証的に確認(推測でなく型境界を実際にTraceした)。

_diagnostic_exception_detail()自体のEdge Case(.codeがNone/欠落/非文字列
Object)も再点検し、到達不能な理論上のRiskを1件言及したのみ(.code自身の
__str__が例外を投げる場合 — 現Codebase中に該当するException型は存在せず、
対処不要と判断)。

新規Test 2件についても、Fakeの形だけでなく実Code Path(_plan_batches、
run_tracked_stage経由のThread Propagation)を実際に辿って検証済み、
Tautologyではないことを確認。
```

### 1.2 Fresh Full回帰Sweep — Finding無し(既存の無関係Issue2件のみ言及)

```text
独立Agentが全Backend Suite(2253 passed/22 deselected)、Ruff/Mypy全Tree、
Frontend Suite(318 passed)、npm typecheck、git diff --checkを再実行。
今回のFix対象File(adapter.py, selene.py)はいずれもRuff/Mypy完全Clean。

言及された2件はいずれも今回のSessionとは無関係な既存Issue:
  - mypy 1件(judge_live_integration.py:604) — Commit 1f0e70e由来の
    既存Issue、git blame/Isolation Testで確認済み。
  - frontend/src/App.tsx の未Commit差分 — 別途進行中のPackage 3作業
    (maxNewTokens 2048->4096)由来、今回のJudge Dispatch Fixとは無関係。
どちらも本Task Scope外、対処不要と判断。
```

### 1.3 Docs完全性監査 — Finding3件、本Addendumで対処

```text
Finding 1(中): Round 1 Doc §4の行番号引用(L349-354/L386-396/L464-468)が、
  Doc作成後にFile自体が(別途進行中のPackage 2 WIP内容を含んでいたため)
  実際の行番号とズレていることが判明。正確な現在位置は本Addendum§2.1で
  訂正する。

Finding 2(中): Round 1 Doc §5 Open Finding 6と、Root Cause Doc §7
  「残る未確定点」点1(Pathological Repetition Latch)が、相互参照
  されないまま別々に記録されていた。さらに、Docs Auditが独自に
  発見した重要な事実 — 今回のDiagnostic Detail追加は、実は両者を
  区別可能にしている(Pathological Repetition Latch経路は`_state=
  FAILED`Latch後に`InferenceErrorCode.MODEL_NOT_LOADED`、Open Finding 6の
  正当なBusy衝突は`InferenceErrorCode.MODEL_BUSY`と、異なるCodeを
  持つため) — をどちらのDocsも明記していなかった。本Addendum§2.2で
  この事実を追記する。

Finding 3(小〜中): Open Finding 6のEvidence Script
  (lock_contention_repro_post_fix_verification.py)がScratchpad配下
  (Project外、Git管理外)のみに存在し、将来のSessionが再実行できない
  ことへの明示的な注記がなかった。本Addendum§2.3で注記する。
```

## 2. Docs訂正(Append-only、既存Doc本文は改変しない)

### 2.1 Round 1 Doc §4の行番号訂正

```text
Round 1 Doc(handoffs/phase_9_claude_judge_dispatch_unavailable_fix_round1_
self_review_exact_return_ja_20260903135915.md)§4記載の行番号は、Doc作成
時点でFileが並行して別Package作業内容を含んでいたため現在とズレている。
2026-09-03 16:20時点でのgrep -n実測による正確な位置は次のとおり
(selene.py):

  _diagnostic_exception_detail() 定義          : L233
  1箇所目(_plan_batches except)               : L377-383(呼出しL381)
  2箇所目(run_tracked_stage except)            : L415-427(呼出しL425)
  3箇所目(decode except)                       : L495-501(呼出しL499)

将来行番号が再びズレる可能性を考慮し、Source Truthは常に
`grep -n _diagnostic_exception_detail src/margpa_runtime_llm/adapters/
evaluation/selene.py`で再取得することを推奨する。
```

### 2.2 Open Finding 6とRoot Cause Doc §7点1の関係整理

```text
両者は別の、独立したAdapter汚染Mechanismである:

  Root Cause Doc §7点1(Pathological Repetition Latch):
    adapter.py _mark_generation_unavailable()が_state=FAILEDへ永続Latch
    -> 以降のcount_*_tokens/generate()はInferenceError(code=
       MODEL_NOT_LOADED)
    -> 実Incidentで実際に発生したかは今なお未確認(既存Open、変更なし)

  Round 1 Doc §5 Open Finding 6(正当なBusy衝突):
    取り残しThreadが実際にまだGenerate中 -> 後続Turnの実generate()試行が
    _begin_generation()のInferenceError(code=MODEL_BUSY)に衝突
    -> Round 1で実機確認済み(発生を確認済み、Behavior未対処のままOpen)

**新規確認事実(Docs Audit発見、Source変更なし)**: 本Round 1で追加した
_diagnostic_exception_detail()により、この2つは既に永続Evidence上の生
failure_reason文字列で区別可能になっている
  (例: "..._unavailable:InferenceError:model_not_loaded" vs
       "..._unavailable:InferenceError:model_busy")。
これはRoot Cause Doc §8 Option C(InferenceError.codeを収束Stringへ含める
観測性改善)を実質的に満たしている。ただし表示Category
(JudgeFailureReason.UNAVAILABLE)自体は両者とも変わらず区別されないため、
UI表示レベルでの区別にはならない(永続Evidence/Log直接参照時のみ有効)。

今後、実運用でこの生文字列から実際にどちらが発生しているか観察できる
ようになったため、Root Cause Doc §7点1の「実際に発生したか未確認」問題は、
今後の実Evidence蓄積で解消しうる状態になった。
```

### 2.3 Evidence Scriptの所在に関する注記

```text
Round 1 Doc §3.3が参照する実機再検証Script
(lock_contention_repro_post_fix_verification.py)は、本Projectの既存
慣行(調査用ScriptはScratchpad配下のみに置きGit管理しない)に従い、
Project外のSession-local Scratchpad Directoryにのみ存在する。したがって
将来のSessionがこのEvidenceを"再実行"することはできず、Round 1 Doc §3.3
の記述(結果の要約)のみが再利用可能な記録である。将来同種の実機再検証が
必要になった場合は、本Doc§2.1の正確なCode位置と、Root Cause Doc§3の
Script構成方針(実Main同時Load、実Registry、実109->32/77 Snapshot)を
参照して新規に構築する必要がある。
```

## 3. Focused Verification(本Addendum作成時点の再確認)

```text
.venv/bin/python -m pytest tests/unit/evaluation/test_selene_adapter.py \
  tests/unit/inference/test_llama_cpp_boundary.py -q
  -> 30 passed
.venv/bin/python -m pytest -q -m "not model_smoke"
  -> 2253 passed, 22 deselected
Ruff/Mypy(adapter.py, selene.py): Clean
Source変更: 本Addendum作成時点でなし(Round 1のCode Fixから不変)。
```

## 4. Loop収束についての判断

```text
Round 1: Code Fix実装 + 3観点Review(Concurrency-Safety Finding無し、
  Test Coverage Finding5件中主要1件対処、実機再検証でOpen Finding 6
  発見・Diagnostic Detail追加で対処)。
Round 2: Round 1差分(Diagnostic Detail追加)への3観点Review — Code側
  Finding 0件(2 Round連続)、Docs側Finding 3件(本Addendumで対処)。

2 Round連続でCode側のFinding がゼロに収束したことから、これ以上の
Code Fix自体への3観点Reviewは限界効用が低いと判断する。本Addendumの
Docs訂正はSource変更を伴わないため、これに対する更なるReview Round
(Round 3)は実施しない。Open Finding 6自体の挙動的解消(Bounded Wait/
Retry等)は、Round 1で記録したとおりController/User Authority判断待ち
のまま、本Loopの対象としない。
```

## 5. Exact Next Action

```text
1. 本Loop(Round 1-2)の結果をUserへ報告し、継続するか収束と見なすかの
   判断を仰ぐ。
2. Open Finding 6の対処方針(§2.2参照、既存3候補)は別途User/Controller
   Authority判断を要する。
```
