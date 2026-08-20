# 将来Scope提案 — Context Observatory（Context Window観測・圧縮復旧機構）

```yaml
document_id: future_scope_proposal_context_observatory_20260817234734
status: reservation_not_started
phase: phase_3_candidate
subphase: null
from: ユーザー（原案）／Claude側設計統括者役（まとめ直し）
to: プロジェクト責任者兼設計統括者役（Codex）
role: design_governor
created_at: 2026-08-17 23:47:34 JST
language: ja
purpose: |
  ユーザーが2026-08-17に提示した将来Feature構想（LLMとの対話における
  Context Window使用状況の可視化、圧縮発生前の状態外部化、圧縮前後の
  比較記録を伴うRecovery機構）を、Phase 3着手判断のInputとして記録
  する。ユーザー明示指示：「Phase 3の頭でやりたい事として、docs/に
  まとめ直して書いておいて」——本Docは実装着手を意味しない。
authorization: |
  ユーザー指示（2026-08-17）。history/以下への新規Append-only File
  作成であり、Claude側設計統括者役の無許可書込み範囲内
  （運用メモ第3節）。
related:
  - future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001
    （本提案の第7節で言及するScheduler接続の相手側）
created: Claude Code
```

## 0. 位置づけ（重要）

**本Docは提案・記録のみであり、実装は一切未着手・未着手予定。** ユーザーは「Phase 3の頭で作れそうなら作ってしまいたい。今、使えるTokenが少ないからこそ」「後のほうが良ければ後でもよい」と明言しており、実装時期の判断自体もCodex側・ユーザー側の今後の判断に委ねられている。本Docの役割は、そのPhase 3着手判断時に参照できるInput資料を残すことに限定される。

## 1. 背景・要旨

ユーザーは、本Session内で実際に体験した「Context Window使用率が96%へ達した直後に、意図的にContext使用を限界まで続けたところ、実際にAuto-compaction（Context圧縮）が発生し、使用率が9%まで回復した。その過程で、直前に読んでいた複数のFileのうち一部は自動的に全文再挿入されたが、比較的大きいFile（Claude側設計統括者役自身の運用メモ）は『内容省略、必要なら再読込』という注記のみが残り、明示的な再読込が必要だった」という一連の実地観察（[claude_side_design_governor_operating_notes_ja.md](../task_roles/claude_side_design_governor_operating_notes_ja.md)第9節、および[automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md](automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md)に記録済み）を踏まえ、次の着想に至った。

**Context Windowの残量だけでなく、「記憶が失われる瞬間（圧縮）」そのものと、「そこからの復職過程」までを観測可能にすべきである。** これは、MARGPA Runtime LLM自身が、対話者向けの製品機能として持つべき、独立したScopeの提案である。

## 2. 核心的な設計原則——単なる「残り○%表示」ではなく、観測機構として設計する

ユーザーが提示した最重要の設計方針は、次の一言に集約される。

> 単なる残量Percentage表示に留めず、**Context Budget／Compaction観測機構**として、独立した研究機能に位置づけるべきである。

この考え方の核心は、次の6つの概念を、意図的に分離して扱うことにある。

```text
Context Capacity（Modelが扱える総容量）
  ≠ Current Usage（現在の使用量）
  ≠ Remaining Budget（残りの予算）
  ≠ Compaction Threshold（圧縮が発生する閾値）
  ≠ Compaction Event（圧縮が実際に発生したという事象）
  ≠ Recovery State（そこからの復旧状態）
```

これらを一つの「残量バー」に単純化してしまうと、失われる情報が多い。特に**Compaction Threshold（圧縮閾値）は、Provider・実装によって内部仕様が公開されていない可能性がある**ため、閾値の値そのものに、根拠のLabelを付すことが提案されている。

```text
measurement:
  observed           # 実測値
  provider_reported  # Provider側が公式に報告した値
  runtime_calculated # 自Runtime側で計算した値
  estimated          # 推定値
  unknown            # 不明
```

推定に過ぎない値を、実測値であるかのように見せない、という誠実さが、この設計の前提になっている。

## 3. 画面表示のUI概観——2つの独立した仕組みとして分ける

当初の整理では、「常時参照可能な詳細表示」と「閾値到達時の段階的な通知」を、一つの仕組みとして混同していた。ユーザーによる訂正を経て、これらは**目的の異なる2つの独立した仕組み**として設計すべきであることが明確になった。

### 3.1 常時参照可能なInspector Panel（Pull型、利用者が任意のタイミングで見るもの）

一つ目は、Claude Codeの開発Client自体が備えている、Context Window詳細Panelと同種のものを、**通常のChat／Thread画面にも実装する**、という要望である。将来的に、Claude CodeやCodexのような開発Agent的Productを別途作ることは想定しているが、この機能自体は、それとは独立して、**通常のChat／Threadにも欲しい**という点が重要である。

配置は、Message入力欄の近くに、Buttonのような形で置く。利用者がそのButtonを押した時にだけ開く、Pull型（利用者の意思で見に行く）のPanelであり、自動的にPopupしたり、会話へ割り込んだりはしない。

表示内容は、実際にユーザーが確認したClaude Codeの Panel例を踏まえ、次のような構成が想定される（項目・数値は例）。

```text
コンテキストウィンドウ                          83.8k / 967.0k (9%)
────────────────────────────────────────────
Messages                                    42.8k    4.4%
System tools                                17.1k    1.8%
System prompt                               11.5k    1.2%
MCP tools                                    8.5k    0.9%
Skills                                       3.6k    0.4%
Memory files                                  159    0.0%
Autocompact buffer                          33.0k    3.4%
Free space                                 850.2k   87.9%
System tools (deferred)                     20.2k      —
MCP tools (deferred)                        16.1k      —
（各行は展開可能：個別のMCP Tool名・Memory File名等の内訳を表示）

Plan使用制限
────────────────────────────────────────────
5時間制限     ： 残り時間とリセット時刻、使用率
週間・全Model ： リセット日、使用率
```

利用側から見た内訳（Messages・System prompt等）と、Provider側の内部運用に関わる内訳（System tools・MCP tools・Autocompact buffer等）を並べて表示する点、および、細目を展開して個別の内容を確認できる点が、単純な「残量○%」表示との違いである。

**なお、上記の表示内容・Layoutは、あくまで参考例であり、確定した画面設計ではない。** 実際にどのような画面にするかは、実装に着手する時点で改めて検討する。検討材料としては、上記のClaude Code Panel例に加えて、第2節で述べた設計原則の元になった、より詳細な構造提案（Context Capacity／Current Usage／Remaining／Warning threshold／Recovery threshold／Compaction／Last recovery snapshot／Measurementを個別項目として持つUI Mockup、および第5節のContext Observatory構成要素）も、あわせて入力として用いる。

### 3.2 LLM自身による段階的な自己申告（Push型、モデル側から能動的に伝えるもの）

二つ目は、第2部（当初の整理）で「段階表示」として記載していたものの実体であり、UI側の自動Popupではなく、**LLM自身が、会話の中で能動的に自らのContext使用状況を申告する**、という仕組みである。

```text
使用率 78%相当              → 特に何もしない（平常時）
使用率 85%相当              → LLMが「現在Contextが85%程度です」等、
                              会話の中で申告する
使用率 90%相当              → LLMが「そろそろRecovery文書を作成した
                              方がよいかもしれません」等、能動的に
                              提案する
使用率 95%相当              → LLMが「まもなく圧縮される可能性が
                              あります」等、明確に予告する
```

この仕組みは、3.1のInspector Panelとは独立している——Panelは「利用者が見に行けば、いつでも正確な状態がわかる」という受動的な仕組みであるのに対し、こちらは「LLM自身が、利用者から聞かれなくても、状況に応じて申告する」という能動的な仕組みである。両者は補完関係にあり、どちらか一方だけでは、今回ユーザーが求めている体験（第1節で述べた、圧縮前に現在状態を外部化できる体験）を十分には実現できない。

**申告の見せ方についても、まだ確定していない。** 候補として、(a) 会話を中断するPopup形式、(b) 会話Logの中に、通常のBlockの一つとして出力する形式（例：Log最下部への追記）、の少なくとも2種類が考えられる。Popup形式は、確実に気づけるという利点がある一方、会話の流れを断ち切る煩わしさが懸念される。会話Log内への出力形式は、その煩わしさを避けられる一方、見落とされる可能性がある。どちらが適切かは、実際の動作・体感次第であるため、両方を候補として残し、実装検討時に判断する。現時点で候補に挙げるとすれば、会話Log出力内の、最下部Blockとしての表示である。

この設計がもたらす価値は、次の一言で要約できる。**「壊れてから復旧する」のではなく、「壊れる前に、現在状態を外部化できる」ようになる、という点である。** 通常のThreadでは、現状「なんとなく長くなってきた」という体感だけを根拠に、引き継ぎ文書を作成するかどうかを判断するしかない。Context Windowの状態が観測可能になれば（3.1）、かつLLM自身がその状態を踏まえて能動的に申告できれば（3.2）、この「いつRecovery文書を作るべきか」という判断（Recovery Gate）を、体感ではなく定量的な基準として扱えるようになる。

### 3.3 補足：圧力表示・Recovery Button

Researcher向けの用途としては、さらに次のような表示・操作も提案されている。これらは3.1のInspector Panelを開いた際に、あわせて確認・操作できるものとして位置づけられる。

- 使用率が80%を超えている場合、"Context pressure: HIGH" という圧力表示。
- 使用率が90%を超えている場合、"Create Recovery Snapshot" という、Recovery文書生成Button。

## 4. Recovery Snapshot機構

Context使用率が一定の閾値（Configuration可能）を超えた場合の、Snapshot生成Flowが次のように提案されている。

```text
context_usage >= configured_threshold
        ↓
Recovery Preflight（事前確認）
        ↓
Current State抽出
FIXD（確定事項）抽出
Open Tasks（未完了事項）抽出
Authority／Scope抽出
Next Route（次に取るべき行動）抽出
        ↓
recovery_YYYYMMDD_HHMMSS.md 作成
        ↓
（必要であれば）新規Thread作成
        ↓
生成されたRecovery文書を読ませて復職
```

ユーザー自身の実際の運用に照らすと、次のような形で機能することが想定されている。

```text
残Budget 20%
  ↓
重要FIXD／現在地／未完了／次Route抽出
  ↓
recovery_YYYYMMDD.md 作成
  ↓
（必要であれば）新Thread作成
  ↓
.mdを読ませて復職
```

**ここで重要なのは、この機構が既存のStable文書へ勝手に書き込むものではない、という点である。** 生成されたSnapshotは、あくまで生成された事実があるだけであり、Canonical化（正本として採用されること）や、承認されたことを意味しない。

```text
Snapshot generated（生成された） ≠ Canonicalized（正本化された） ≠ Approved（承認された）
```

この区別は、本プロジェクトが一貫して採用してきた、「AI側が生成したものを、AI自身の判断で正本へ昇格させない」という既存のGovernance原則（[claude_side_design_governor_operating_notes_ja.md](../task_roles/claude_side_design_governor_operating_notes_ja.md)第3節のDocument Authority境界等）と、そのまま整合する設計である。

## 5. Context Observatoryという全体構成

ユーザーは、この機能群全体に対して、**「Context Observatory」**という名称を提案している。想定される内部構成は次の通りである。

```text
Context Observatory
├─ Budget Monitor（予算監視：容量・使用量・残量の追跡）
├─ Pressure／Threshold（圧力・閾値：警告・Recovery閾値の管理）
├─ Compaction Detection（圧縮検知：圧縮の発生をどう検知するか）
├─ Retention Comparison（保持比較：圧縮前後で何が保持され、何が失われたか）
├─ Recovery Snapshot（復旧Snapshot：第4節の生成機構）
└─ Recovery Evaluation（復旧評価：復旧がどれだけうまくいったかの評価）
```

## 6. 研究用途としてのInstrumentation（計測機構）

Researcher向けの用途として、次の項目を記録できることが望ましい、という提案がなされている。

- 圧縮前後のToken使用量
- 圧縮によって何が保持されたか
- 圧縮によって何が脱落したか
- System側によって自動的に再注入されたArtifact（File等）
- 明示的な再読込（Read）が必要だったArtifact
- Recovery完了までに要した時間
- Recovery後のTask継続性（作業が正しく引き継がれたか）
- 認識のDrift（復旧後に、認識のズレが生じていないか）
- Context圧縮率

**この提案の直接の動機は、本Session内で実際に観測された、次の事例そのものを、MARGPA自身の中で再現可能な形で計測できるようにすることにある。**

```text
Context使用率 96%付近
  → 重要な理解をDocsへ書き出す
  → Auto-compaction発生
  → 使用率 9%まで回復
  → Docsから復旧（一部Fileは自動再注入、運用メモ自体は明示的な
    再読込が必要だった）
```

すなわち、今回Claude側で実地に発生した圧縮・復旧の経験を、一度きりの実験結果として終わらせるのではなく、MARGPA自身が対話者へ提供する機能として組み込み、繰り返し計測・改善できる仕組みへ発展させる、という提案である。

## 7. Schedulerとの接続（将来構想）

本Docと同日別途記録した、[Time Provider／Scheduler構想](future_scope_proposal_temporal_authority_agentic_runtime_ja_20260817184001.md)が将来実現した場合、Context Observatoryは、時刻によるTriggerとは異なる、**状態によるTrigger**の一種として、Scheduler機構へ接続できる可能性がある。

```text
時刻Trigger（Time Providerによるもの）：
  Friday 18:00 JST → Jobが起動する

状態Trigger（Context Observatoryによるもの）：
  Context使用率 ≥ 90% → Recovery Preflightが起動する
```

両者は、トリガーの種類が異なるだけで、「一定の条件が満たされたら、あらかじめ定義された処理を起動する」という構造は共通している。この接続可能性は、あくまで将来の拡張候補として記録するに留め、本Docの提案範囲には含めない。

## 8. 実装時期についてのユーザーの位置づけ

ユーザーは、本構想を「Phase 3の頭で、もし作れてしまいそうなら作ってしまいたい」と位置づけている。その理由として、「今まさに使えるTokenが少ない状況だからこそ、この機能の必要性を強く感じる」という、逆説的だが説得力のある動機が示されている。一方で、「後回しにしたほうが良いのであれば、後でもよい」という柔軟な留保も、同時に示されている。

すなわち、本Docは「Phase 3着手時に、最初に検討すべき候補の一つ」として記録されるものであり、Phase 3の内容そのものを拘束するものではない。

## 9. 追加提案（2026-08-20追記：既存Context使用率Gauge実装後のFollow-up）

第1〜8節は、本Docの原案（2026-08-17時点、実装着手前）である。その後、Message入力欄近くのContext使用率Gauge（Click式Popover、内訳表示付き）自体は既に実装済みとなった。本節は、その実装済みGaugeを土台とした、追加の改善提案をまとめる。**本節も、他節と同様、提案記録に留まり、実装着手を意味しない。**

### 9.1 しきい値ベースの軽い警告

現状のGaugeは、使用率の数値・内訳を表示するのみである。次のように、使用率の段階に応じて表示を変化させる案が提示されている。

```text
50%超え： 通常表示
70%超え： 少し強調（色・太さ等）
80%超え： 色変化
85%超え： 引き継ぎ書作成をLLMから提案
95%超え： 保存／要約／引き継ぎを優先提案
```

あわせて、次の要素も候補として挙げられている。

- Gauge部分へのHoverで、詳細内訳を表示する。
- Compaction（圧縮）が推奨される目安のLineを、Gauge上に視覚的に表示する。
- 危険域（例：95%超え）では、「このまま続けると（Compactionにより文脈が）失われる可能性がある」という趣旨の、軽い示唆を行う。

これらは、第3.2節で述べた「LLM自身による段階的な自己申告」構想と関連するが、あくまでUI側の表示強化として独立に着手できる、より軽量な改善候補である。

### 9.2 ワンクリック引き継ぎ

Gauge Clickで開くPopover内に、次のようなButtonを追加する案。

- 現在の会話を要約する。
- 引き継ぎ書（Handoff Document）を作成する。
- 次の作業用のHandoffを生成する。

第4節のRecovery Snapshot機構と目的は重なるが、こちらはPopoverから即座に呼び出せる、より手軽な入口としての位置づけである。

### 9.3 内訳表示の充実

既存Gaugeの内訳表示（会話履歴／System Prompt／RAG Context／残り）は、「何がContextを消費しているか」を可視化できている点で、現状のままでも十分に有用と評価されている。将来的な拡張候補として、次の内訳項目を追加すると、研究用途としての価値がさらに高まるとされている。

- Attachments（添付File）
- Citations（引用・参照文書）
- Hidden runtime additions（利用者から見えないRuntime側の追加分）
- Tool outputs（Tool実行結果）

### 9.4（話題別）通常Chat画面の余白活用（将来の補助Pane候補）

第9.1〜9.3節とは別の話題として、通常Chat画面のLayoutに関する所感も、あわせてここへ記録する。

1920px幅の画面で見ると、中央のMessage表示領域の左右に、相当広い空白が生じている。将来的に、この空白（画面右側）へ、Citation／Trace／Eval／Governance Evidenceといった補助情報を表示するPaneを追加すれば、Space効率よく活用できる可能性がある。**現状のResearch Preview段階では、この空白は空けたままで問題ない**という位置づけであり、これも実装着手を意味しない、将来のUI拡張候補の記録である。

## 10. Status

```text
Current Point            : ユーザー構想を記録・まとめ直し（原案、第1〜8節）。
                            2026-08-20、既存Context使用率Gauge実装後の
                            追加提案（第9節）をユーザー指示により本File
                            へ直接追記。実装着手・設計確定は一切なし。
Files Created／Modified   : 本Fileのみ（新規作成、2026-08-20に第9節を
                            追記——ユーザー明示指示による例外的な既存
                            History File直接編集）。
Validation                : N/A（提案記録）
Open Current Blocker      : NONE（Blockerではなく、Phase 3着手判断時の
                            検討候補という位置づけ）
Controller-owned Next Work: Phase 3の内容・優先順位をCodex側・ユーザー
                            側で判断する際、本Docを候補の一つとして
                            参照する。
Exact Next Route          : 本DocはRead-only参照材料として保持。
                            Claude側設計統括者役から能動的に着手・
                            提案することはない（Phase 3自体がまだ
                            開始していないため）。
```
