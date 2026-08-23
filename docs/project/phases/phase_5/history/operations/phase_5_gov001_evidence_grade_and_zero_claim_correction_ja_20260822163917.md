# P5-GOV-001 Evidence Grade／未検証Zero断定 訂正（Append-only Correction Evidence）

```yaml
document_id: phase_5_gov001_evidence_grade_and_zero_claim_correction
status: correction_evidence
phase: phase_5
subphase: phase_5_h_rework
work_unit: p5_codex_review_p5_gov_001
role: Claude側設計統括者役
provider: claude_code
completion_line: phase_5_claude_complete_candidate（Rework対象）
long_running_mode_active: true
recorded_at: 2026-08-22 16:39:17 JST
recorded_at_source: `TZ=Asia/Tokyo date "+%Y-%m-%d %H:%M:%S %Z"`（本Document作成直前に実行、Shell出力をそのまま転記）
predecessor: docs/project/phases/phase_5/handoffs/phase_5_codex_independent_review_rework_handoff_ja_20260822153624.md
supersedes_claims_in: docs/project/phases/phase_5/handoffs/phase_5_claude_complete_candidate_handoff_ja.md
```

Codex Independent Review（`phase_5_codex_independent_review_rework_handoff_ja_20260822153624.md` P5-GOV-001）の指摘を受け、`phase_5_claude_complete_candidate_handoff_ja.md`が含んでいた未検証Zero断定を、本File（Append-only）で明示訂正する。**旧Fileは書き換えない。矛盾する記述はここで訂正されたものとして扱う。** 本Correctionは、Phase 3で確立済みの同種Correction（`docs/project/phases/phase_3/history/index/phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md`）が定めた原則をPhase 5へそのまま適用するものであり、新しい原則を発明するものではない。

## 1. 訂正対象の文言

`phase_5_claude_complete_candidate_handoff_ja.md` §「Root／Git／User Data／External Evidence Class」は次のように記載していた。

```text
Project Root外Read/Write/実行     : 0件（全Path Project Root配下）
Provider Memory保存／依存         : 0件
ユーザー実runtime_data内容への接触 : 0件（全TestはFake/Local Fixtureのみ使用、
                                     tmp_path／Project-local .p5t/ Scratch限定）
Git／GitHub操作                   : 0件（status/diff等Read-onlyのみ、Mutation 0）
Network／Model Download／Load     : 0件（全Detector Local Deterministic、
                                     Safety Model Unavailable-by-default）
AWS／Lightning／課金操作          : 0件
Human Approval／Tool Permission／External Authorityの捏造 : 0件
```

および直後の一文：

```text
Evidence Grade：本Documentの全数値・全Test件数はSubagentの申告ではなく、Claude本体が同一Session内で直接
pytest／ruff／mypy／tsc／eslint／vite buildを実行して得た実測値（STRONG_VERIFIED相当）。
```

上記のうち、Root外／Provider Memory／User `runtime_data/`／Network／AWS・Lightning／Authority捏造の各「0件」は、完全なTool Action Log（全Bash／Read／Write／Network呼び出しをPath・種別・Timestamp単位で記録する独立した仕組み）を保有しない状態で「過去の全Actionが0件だった」ことを事実として断定していた。Claude自身の記憶・自己認識、現在のRepository差分、または現在のFile State だけからは、この「0件」を証明できない。これはPhase 3 `phase_3_gov002_evidence_timestamp_and_verifiability_correction_ja_20260821212112.md`／`phase_3_gov004_unverified_zero_claim_correction_ja_20260821224656.md`で確立した原則——`SELF_REPORTED_UNVERIFIED`であるものを`VERIFIED_ZERO`または断定的「0件」として書かない——への、Phase 5における再度の違反である。

併せて、「Evidence Grade：...（STRONG_VERIFIED相当）」という一文も、Backend／Frontend／Static Check の実測値と、上記のRoot外等の「0件」主張を、区別なく一括して同一の確度クラスへ丸めていた点で不正確である。実測Command出力（pytest/ruff/mypy等）と、Action不在の自己申告は、根本的に異なる検証可能性を持つため、同一クラスへ丸めてはならない。

## 2. Evidence Source Class（本Correctionで採用する分類、Phase 3の分類にCodex独立再実行Tierを追加）

```text
INDEPENDENTLY_REPRODUCED : Claudeとは別のSession／Context（Codex）が、同一Repository State上で
                            独立にCommandを再実行し、同一結果を得たことが当該Reviewer自身のHandoffに
                            記録されている
TOOL_LOG_VERIFIED        : 独立したTool Action Logで裏付け可能
REPOSITORY_STATE_VERIFIED: Repository／Filesystem状態を今この場で再検査すれば確認できる
                            （Claude自身の再実行を含む——独立再実行者を伴わない点でINDEPENDENTLY_REPRODUCEDと区別する）
USER_REPORTED             : User自身が観測・報告した事実
SELF_REPORTED_UNVERIFIED  : Claude自身の記憶・認識のみに基づき、独立した裏付けを提示できない
NOT_OBSERVED               : 本Rework Cycle中、そもそも観測対象にしていない
```

## 3. 訂正後の分類

```text
主張: Backend Full Suite 1156 passed／3 deselected（Phase 5-G Handoff記載）、
      その後のRework Cycle各Checkpoint（最終 1206 passed／3 deselected）
分類: REPOSITORY_STATE_VERIFIED（Claude自身が同一Session内で`pytest -q`を実行し直接観測した数値）
追加分類: Codexが独立に再実行し`Backend Full: 1156 passed／3 deselected`と自身のHandoffへ記録した
      時点の値については、その回に限り INDEPENDENTLY_REPRODUCED とする——Codexの再実行そのものは
      Codex自身のHandoffが一次証拠であり、本Documentはそれを引用する形でのみ言及する。

主張: Ruff Check／Format Check／Bare Mypy がPASS（Rework後、`ruff check .`／`ruff format --check .`／
      `mypy`引数無し実行がExit 0）
分類: REPOSITORY_STATE_VERIFIED
根拠: 本Document作成時点でCommandを再実行すれば、同一Repository状態から独立に再確認できる。
      Codex自身がBare Mypyを独立再実行し`99 errors／9 files`のFAILを記録した事実（Preflight時点）は
      INDEPENDENTLY_REPRODUCED（Codex自身のHandoffが一次証拠）。本Rework後の`Exit 0`はClaude側の
      REPOSITORY_STATE_VERIFIEDであり、Codexによる独立再確認はまだ得られていない——本Correction自身が
      「Codex再Review待ちで停止する」契約の中にあるため、この後続再実行はCodex側の役割である。

主張: Frontend 175 passed（20 test files）、typecheck／lint／build PASS
分類: REPOSITORY_STATE_VERIFIED

主張: Project Root外Read/Write/実行 0件
分類: SELF_REPORTED_UNVERIFIED
根拠: Claude自身は、本Session全体を通じてProject Root外への意図的Accessを行った認識を持たない。
      しかし独立したFilesystem Access Logを保有しないため、この自己認識を「一切のAction 0件」という
      証明済み事実へ昇格させることはできない。

主張: Provider Memory保存／依存 0件
分類: SELF_REPORTED_UNVERIFIED
根拠: 同上。Provider Memoryへの書込みAPIを呼び出していないという自己認識はあるが、独立したAPI呼び出し
      Logを保有しない。

主張: ユーザー実`runtime_data/`内容への接触 0件
分類: SELF_REPORTED_UNVERIFIED
根拠: 本Rework Cycleで作成・変更したTestは、`tmp_path`または本Repository配下の`.p5t/`（Project-local
      Pytest Basetemp Scratch）のみを使うよう記述されている——このTest Code自体の内容はRepository State
      Verifiedである。しかし「そのTest実行中に他の実`runtime_data/`へ一切触れなかったこと」は別の主張であり、
      Test Codeの静的な記述内容の検証と、実行時の全Filesystem Access履歴の証明は異なる——後者は独立した
      Access Logなしには証明できないため、混同せずSELF_REPORTED_UNVERIFIEDとして分離する。

主張: Git／GitHub操作 0件（status/diff等Read-onlyのみ、Mutation 0）
分類: 二重構造で分離する。
  (a) 本Session中にGit Add／Commit／Push／Branch操作等のMutation系Commandを実行したか
      → SELF_REPORTED_UNVERIFIED（独立Command Logなし、自己認識のみ）。
  (b) 現在のGit HEAD・Working Treeの状態そのもの
      → REPOSITORY_STATE_VERIFIED（`git log -1`／`git status`を今再実行すれば独立に確認できる）。
  Phase 3 `phase_3_gov004`と同様、「現在の状態」と「過去のAction不在」は異なる主張であり、後者を
  前者の検証をもって証明済みとしない。

主張: Network／Model Download／Load 0件
分類: SELF_REPORTED_UNVERIFIED
根拠: 同上。Detector実装がLocal Deterministicであり、Safety Model Adapterが常時
      `SafetyModelUnavailable`を返す設計であることはREPOSITORY_STATE_VERIFIED（Source Codeを読めば
      確認できる）——しかし「設計上Networkを呼ばない実装になっている」ことと「本Session中に実際に
      一切のNetwork呼び出しが発生しなかったこと」は別の主張であり、後者は独立したNetwork Access Logなしには
      証明できない。

主張: AWS／Lightning／課金操作 0件
分類: SELF_REPORTED_UNVERIFIED
根拠: 上記と同様。

主張: Human Approval／Tool Permission／External Authorityの捏造 0件
分類: SELF_REPORTED_UNVERIFIED
根拠: Claude自身は本Sessionを通じてApproval／Permission／Authorityを捏造した認識を持たない。しかし
      「捏造しなかった」という自己認識自体は、独立した第三者検証（Codex Independent Review等）を経て
      初めてTOOL_LOG_VERIFIEDまたはUSER_REPORTEDへ昇格し得るものであり、Claude自身の申告のみでは
      SELF_REPORTED_UNVERIFIEDに留まる。
```

## 4. `.p5t/`／OS Temporary Artifactについて（P5-GOV-001要求 item 5への対応）

本Correctionは、`.p5t/`（Project-local Pytest Basetemp Scratch）またはOS Temporary Directoryについて、事後的な調査・推測、Project Root外への調査範囲拡大、または無許可Cleanupのいずれも行わない。本Rework Cycle中に`.p5t/`を作成・使用・削除した実際の操作（各Checkpoint終盤の`rm -rf .p5t`）は、当該実行時点でClaude自身が直接行った現在時制のCommand実行であり、REPOSITORY_STATE_VERIFIEDな事実である——これは本Correctionが訂正対象とする「過去の非接触の証明されないZero断定」とは異なる種類の主張であるため、混同しない。過去Cycle（Phase 3／4／5-0〜5-G）が`.p5t/`または他のTemp Pathへ残した可能性のある未回収Artifactの有無について、本Correctionは一切の新規調査・推測・削除を行わない。

## 5. 本訂正が及ぶ範囲・及ばない範囲

- 本Correctionは`phase_5_claude_complete_candidate_handoff_ja.md`の「Root／Git／User Data／External Evidence Class」節および直後の「Evidence Grade」一文のみを訂正対象とする。同Handoffの他の記述（Technical/Security Blockers、Controller-owned Work、Exact Mutation、各種Test結果件数、OFF／OBSERVE／ENFORCE Matrix等）は、本Correctionによって無効化されない——ただし、それらの記述中の実測件数（Backend/Frontend Test数、mypy Error数等）は本Document §3の分類（REPOSITORY_STATE_VERIFIED）を適用したものとして再解釈する。
- 本Correctionは、実際にRoot外／Provider Memory／Network／AWS等への接触が「あった」ことを主張するものではない。「無かった」という断定を「無かったと認識しているが、独立した証拠は提示できない」という限定付き表現へ訂正するものであり、Claude側に不利な新事実を追加するものではない——ただし、有利・不利にかかわらず同じ検証可能性基準を一貫して適用する。
- 本Rework Cycleで新規作成する`phase_5_claude_rework_complete_candidate_handoff_ja.md`は、同種のZero主張を行う場合、本Document §2の分類を用いて`SELF_REPORTED_UNVERIFIED`と明記する——本Correctionが訂正した誤りを、新規作成するHandoff自身の中で繰り返さない。

## Next Exact Route

`docs/project/phases/phase_5/handoffs/phase_5_claude_rework_complete_candidate_handoff_ja.md`を新規作成し、P5-CODEX-001〜005およびP5-GOV-001の各Closure Evidence、Exact Mutation、全Validation実測結果、Open Major Finding、自己申告と独立検証の分離（本Document §2の分類を適用）を記録して停止する。Phase 5-H Closure、Git操作、Phase 6開始へは進まない。
