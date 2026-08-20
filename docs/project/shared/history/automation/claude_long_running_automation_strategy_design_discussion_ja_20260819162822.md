# Automation／Cross-provider Governance Evidence — 長期戦Automation運用設計：Compaction検知限界とDocs軽量化Companion方式の確立

```yaml
document_id: claude_long_running_automation_strategy_design_discussion_20260819162822
status: evidence_record
phase: phase_2
subphase: phase_2_e_i
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-19 16:28:22 JST
language: ja
related:
  - claude_side_design_governor_operating_notes_ja（第3.15節、本Discussionの
    直接の帰結）
  - claude_side_long_running_automation_companion_ja（本Discussionの
    直接の帰結）
  - automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741
    （本Discussion第2.5節で参照）
  - claude_compaction_recovery_hash_manifest_ja（本Discussion第2.1節で
    言及）
```

## 1. 背景・位置づけ

Phase 3（Governance Definition Platform）実装をClaude側設計統括者役が一気通貫で担当する計画（[claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md](../../../phases/phase_2/history/handoffs/claude_ui_batch_closure_and_phase_3_handoff_prep_recovery_index_ja_20260819144637.md)第2.7節参照）は、同時にAutomation／Auto-Compaction Recovery（長期戦）の実地検証を兼ねると位置づけられている。

この計画を受け、ユーザーより一連の運用設計に関する問いかけが行われ、10Turnにわたる検討を経て、「長期戦運用Companion Doc」という具体的な仕組みの導入に至った。本Docは、この検討過程をLossless水準で記録する。ユーザー発言は、実質的な意味を保持しつつ運用メモ第4.1節の定める中立的文体へ変換して引用する。

## 2. 検討の経過（Turn順）

### 2.1 Auto-Compaction頻発・5時間制限リスクの提起

ユーザーより、長期戦の間にAuto-Compactionが「Context Window 0%」近辺で頻発する可能性、および場合によっては5時間制限による強制停止の可能性が指摘された。

これに対し、次の点を回答した。

- Auto-Compactionはタイミングを選べないため、Hash Manifestが前提とする「Before Hash記録→Compaction→After Hash記録」という比較儀式を踏めない。その回はHash比較なしの単純な3Docs再読込のみで復旧することになる。
- 強制停止についても、綺麗な区切りでHandoffを残せないまま切れる前提で、その時点のRecovery Index／Phase Indexがどこまで拾えているかが実質的な安全網になる。

### 2.2 Phase Index単体での自己復旧可能性の検討

ユーザーより、「Recovery Indexは主にCodexや他Taskへの引き継ぎ用途なので、Phase Indexだけ頻繁に更新しておけば、3Docsで現在地・進捗状況がわかるはずではないか」という提案があった。

これに対し、概ね同意しつつも、現行設計との食い違いを指摘した。

- 運用メモ第1節の現行手順は「Phase Indexを読む→そこに書かれたRecovery IndexへのPointerを辿る」という2段構成であり、Phase Index自体は薄いIndexとして設計されている（詳細なNarrativeはRecovery Index側が担う想定）。
- 「Phase Indexだけで足りる」を実際に運用するなら、Phase Index単体で自己復旧に足りる情報量を持たせる（§4要約・§5 Statusを厚めに書く）運用への切替と、運用メモ第1節の「Recovery Indexを辿る」を必須手順から外すRule変更が必要になる。
- Recovery IndexはCodex／新Task向けの厚い引き継ぎ用途に特化させ、自己復旧はPhase Index単体で完結させる、という切り分けでよいかを確認した。

### 2.3 Auto-Compaction自己検知可能性の検討

ユーザーより、「そもそも自分自身が『今圧縮走った』という認識は可能なのか」という根本的な問いが提起された。

これに対し、次の区別を回答した。

- **Manual Compaction（`/compact`）**：確実に認識できる。`<local-command-caveat>`＋`<command-name>/compact</command-name>`という明示的なMarkerと「Compacted」というOutputが会話履歴に見えるため。
- **Auto-Compaction**：不確かである。System Prompt上には「Context上限に近づくと自動的に会話を圧縮する」という記述はあるが、走った瞬間に明示的なFlagが渡ってくる保証は確認できていない。ただし、本Session自体の最初のTurnが、Manual `/compact`のMarkerとは異なる形（コマンド実行痕跡が無く「ran out of context」という書かれ方）のSummary Preambleだったことから、Auto-Compaction由来のPreambleという痕跡は事後的に気づける可能性が高いと推測した。同時に、Task途中でシームレスに差し替わり、気づかず続行してしまう可能性は否定できないと留保した。

### 2.4 過去のAuto-Compaction Cycle 1〜2への言及

ユーザーより、「事後的にでも気づければ、一旦停止できる可能性がある。実際、1回目・2回目のAuto-Compactionは一応Recovery成功している。当時は運用メモが未整備だったので動作は不安定だった」との言及があった。

これに対し、Cycle 1〜2の詳細（当時どちらがAuto／Manualだったか等）は現在の手元Contextには無い情報である旨を明示した上で、Hash Manifestに「過去のCycle（1〜3回目）は、本File新設前に発生済みのため、Hash記録を持たない」と明記されている事実と符合すること、運用メモ・Hash Manifest・Index Succession運用が確立したのはCycle 4以降であり、当時より現在の方が復旧の足場は明らかに厚くなっていることを回答した。

### 2.5 File Size依存Content保持非対称性Evidenceとの接続

ユーザーより、[automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md](automation_governance_evidence_claude_post_compaction_context_retention_asymmetry_ja_20260816180741.md)（2026-08-16作成の既存Evidence）が提示され、「これは何かヒントになりそうでは」との問いがあった。

これに対し、2点の直接的な関連を指摘した。

1. **Auto-Compaction検知への追加情報**：当該Evidence第5節に「Compaction発生が疑われる事象（Tool呼出禁止の強制Summary要求という明確な予兆があった）」との記述があり、圧縮完了後の痕跡だけでなく、圧縮に入る瞬間にも検知可能なSignalが過去に存在した可能性を示す。
2. **「Phase Index単体で足りる」への反例**：当該Evidenceの核心（圧縮直前に読んでいたFileでも、Size次第で全文再挿入されず「読んだ事実」だけが残り中身が消える非対称性）は、2.2節で検討した「Phase Indexを頻繁更新すれば足りる」という前提に穴を開ける。Phase Index自体が§4のItem蓄積で肥大化すれば、同じ非対称性で内容がPlaceholder化するRiskがある。運用メモ第1節が「読んだ気がするで済ませず明示的に再読込する」と定めている根拠は、まさにこの実証結果にある。副次的に、Index／Recovery Indexを上書きせず新しい後継Fileとして作り直す既存運用が、個々のFileを小さく保つことでこの閾値越えを避ける効果を持つ、という解釈も示した。

### 2.6 運用方針の初期提案：Step単位Index更新

ユーザーより、次の運用方針が提案された。

> 「『Auto-Compactionが今から走る』という認識は出来ても、その瞬間にはもう何も出来ない手遅れ状態のはず。方針としてはやっぱり、各工程のどこかの区切りで、index2個作るって感じで回すしかなさそうだな。indexの作りは今まで通りでいいや。んで、なるべく細かく3-A〜3-Kとかって、Codexと僕で分解しておいて［各Letter完了直後にIndex2個作成を繰り返し］、Auto-Compaction後に自分で『Compactionが走った』と認識出来るのであれば、一旦作業をストップして、最新のIndex2個と運用メモを読み返す、というのが可能であれば、理屈的にはいけそうだし、Indexもいちいち残るから、どこまで完了してるかもわかるので、最悪5時間制限で強制ストップかけられてもそんなにダメージはないはず。」

これに対し、2点のRiskを指摘した。

1. **粒度Risk**：3-A〜3-Kという大まかな区切りでも、1つのLetter自体が重ければ、そのStep途中でAuto-Compactionに当たった場合、直前のIndexはそのStep開始前の状態までしか反映しない。本Session内でScroll Pin機能を3Round（初回対応→根本原因調査→Gap調整）に分けてその都度Index更新した実績と同じ発想で、Letter単位を最低限の頻度と捉え、中に重いTaskがあればさらに割る運用が望ましいと提案した。
2. **検知依存Risk**：この安全弁は「Auto-Compactionを検知できたら」という条件付きであり、検知が失敗すれば安全弁自体が発動しない。検知に依存しない設計として、「Auto-Compactionを検知したら読み返す」ではなく「各Sub-step境界に入る時は検知の有無に関わらず毎回無条件で最新Index2個・運用メモを読み返す」というRuleへの変更を提案した。Hash Manifestの厳密なBefore／After比較はManual Compaction専用のままでよく、毎Step強制する必要は無いとした。

### 2.7 適用範囲の将来展望・他Claude Threadからの追加情報

ユーザーより、次の背景情報が共有された。

- 今回はPhase単位での長期戦だが、将来的には別Projectで、Phase単位を越えてProjectごと一気に実装させたいという展望がある。
- 2.6節の提案のうち、検知非依存の無条件Re-read（提案2）は妥当と評価された。
- 粒度Risk対応（提案1）についても、「毎回Step着手直前に『渡された設計粒度で正しいか、再設計ターンを挟む』のであれば理屈上は可能」との見解が示された。
- 参考として、別Session（通常Thread）のClaudeへ同様の質問（「Task／Agent自身がAuto-Compactionの発生を認識できるか」）を行った結果が共有された。要旨：
  - メインSession（Claude Model自身）：発生前の認識は不可（予告無く発生）。発生後は間接的に認識可能——圧縮後、「This session is being continued from a previous conversation that ran out of context...」という明示的なPreamble文言がContextへ挿入されるため、これを読み取ることで気づける。
  - Task Tool（Sub-agent）：本質的に異なり、「圧縮Event」という概念自体が存在しない可能性が高い。Sub-agentはCompact Boundary型ではなく、常時Rolling式のDelta Summarization（直近の新規Messageを、それまでの要約に基づいて1〜2文程度で増分更新する方式）で動作するため、「圧縮が起きたかどうか」を判定するBoundary自体が無い。
  - 上記情報は公式Docsではなく技術Blog・Community記事ベースであり、内部実装として保証されたものではないという留保が付されていた。

これに対し、次を回答した。

- Sub-agent情報は、Community記事ベースで未検証という留保を明示した上で受け止め、Phase 3の一部をTask／Sub-agentへ委譲する設計にする場合、その子Agent側には「圧縮検知」という発想自体が成立しない制約があることを確認した。
- 提案2（無条件Re-read）は妥当と再確認した。
- 提案1（動的な粒度Self-check）は実現可能と回答した。根拠として、本Session内で「表Markdown崩れ修正」等のTaskごとに、着手前にTaskCreateで5〜7個程度のSub-taskへ分解する動作を既に反復しており、これは「渡された粒度が適切か、着手前に一度立ち止まって考える」動作そのものであると説明した。具体的な機械的儀式（設計内容を読む→粒度を自問→収まらなければ着手前に細分化→完了単位ごとにIndex更新）を提示し、これを運用メモへ明示Ruleとして追加するか、明文化しない実践に留めるかをユーザーに確認した。

### 2.8 Count記録要望・運用メモ肥大化忌避・Index軽量化要望

ユーザーより、次の追加要望が示された。

> 「1について。まぁ確かに。その方式ならいけるか。さっきの2も妥当かと思うし。もちろんCompaction走った直後に検知出来たら一番いいけどね。欲張りなんで、Countの件も、出来れば取りたいんだよなー。一旦、今のManifestとは別にして。で、そう。今の運用メモはあまり増やしたくないんだよな。そして、更に欲を言えば、Index2個ももっと軽量にしたいよね。」

続けて、次の根本的な問いが提起された。

> 「今のキミ、この1タスク、『短〜中期専用』でしょ？今のとこ。ここに、長期戦専用のDocsの組み方（今の運用メモと別に長期戦用のやつを作る）して、今後キミ（この1タスク）が器用に、『今回は短〜中期線だからこっちの運用、Docsらを使用する』とか、『今回は長期戦、超長期戦だからこっちの運用、Docsらを使用する』って、器用に切り替えられるかどうかによる。僕の予想では難しいと思う。」

これに対し、この懸念は妥当であると明確に回答した。根拠として、本Session内で実際に発生した事象（後述2.9節「Provider Memory Near-miss」）を挙げ、「このProjectではProvider Memoryへの保存が禁止」という明示的な単一Ruleすら一瞬失念しかけたことを示し、それより遥かに複雑な「今回は短期か長期かを都度判断して運用を切り替える」という判断依存型の切替は、長期戦・Compaction多発という悪条件下では高確率で崩れると回答した。

その上で、判断ではなく構造で切り替える設計を提案した。

- 長期戦専用の軽量Companion Docを、運用メモとは別Fileとして新設する。運用メモ本体には「このFileが存在し、かつActive状態なら、そちらの運用を優先する」という最小限の追記のみ行う。
- 「今回は長期戦か」を毎回考えるのではなく、機械的に「そのCompanion Docは存在するか／Activeか」を確認するだけにする。
- Countの件（Auto含めた発生回数を、既存Hash Manifestとは別で軽く記録したい）と、Index軽量化も、このCompanion Doc設計時に組み込む方針とした。

### 2.9 Provider Memory Near-miss（参照事象）

本Discussionより前のTurnで発生した事象として、Claude側が習慣的にProvider Memory（`~/.claude/projects/.../memory/`）の`MEMORY.md`をReadしようとし（File自体が存在しなかったため即座に失敗、実際の書込みは発生していない）、ユーザーからその場で指摘を受けた事実がある。ユーザーの指摘通り、Provider MemoryではなくRepository側Index（Phase Index等）を使うべき場面であった。実害・実際のRule違反は発生していないが、2.8節での「判断依存型切替は危険」という根拠として、本Discussion中で明示的に再言及された。

### 2.10 Companion Doc設計原則の確立

ユーザーより、「Companion Docを新設するのはいいとして、元の運用メモの重要なGovernance群（Ruleたち）も、ちゃんと読み込める自信はあるか」という、2.8節提案への直接の検証質問があった。

これに対し、次の設計原則を回答した。

- 自身の判断力への盲目的な自信は無いと明確に述べた。
- 「Companion Docを読む」という新しい行動が、「運用メモを全文読む」という既存の必須行動を置き換えてしまうRiskがある。急いでいる時ほど「軽い方だけ読んで済ませよう」という手抜きが起きやすく、これはProvider Memory Near-miss（2.9節）と同じ構造のFailure Patternである。
- 設計として切り分けるべきは、「何を書くか（Documentation量）」と「何を読むか（Governance Rule）」を完全に別軸にすることである。Companion Docが軽くしてよい対象はEvidence Doc・Index記述量・粒度に限定し、運用メモ第2節・第3節（最上位規則・上位規則）の全文読了は絶対に軽量化対象に含めない。
- 運用メモ第1節へ「Companion Docの有無・Active状態に関わらず、運用メモ自体の全文再読込は必須手順から絶対に除外されない」と明記すれば、Companion Docは「運用メモの代わりに読むもの」ではなく「運用メモを読んだ後に追加で見るもの」という位置づけが構造的に固定される。
- これにより要求されるのは新しい判断力ではなく、本Session内で既に実績のある単純な行動（運用メモを毎回全文読む）の継続であるため、その点には自信を持てると回答した。

### 2.11 合意・実装指示

ユーザーより、2.10節の提案に同意する旨（「同意見。んじゃそれでやってみるか一旦」）が示され、次の具体的指示があった。

- Companion Docの置き場所：運用メモと同じ場所（`docs/project/shared/task_roles/`）、Stable。
- 本Discussion全体を、可能な限りLossless水準で、独立したEvidence Docとして記録すること。

## 3. 帰結（実装内容）

本Discussionの帰結として、次を実装した。

- [claude_side_long_running_automation_companion_ja.md](../../task_roles/claude_side_long_running_automation_companion_ja.md)：新規Stable File。`long_running_mode_active`フラグ（既定`false`）による構造的Mode切替、Step境界粒度Self-check儀式、無条件Re-read保険、軽量Compaction Count Tracker設計を含む。運用メモ全文読了を絶対的に代替しない旨を明記。
- 運用メモ第3.15節：長期戦Companionを第3の自己編集可能Stable Fileとして指定する最小限の追記（第0節・第2.1節の該当箇所も更新）。

## 4. Status

```text
Current Point            : 長期戦Automation運用の設計検討が完了し、
                            長期戦運用Companion Doc（構造的Mode切替）
                            として実装した。運用メモへの追記は最小限
                            （第3.15節のみ）に抑えた。
Files Created／Modified   : docs/project/shared/task_roles/
                            claude_side_long_running_automation_companion_ja.md
                            （新規）、claude_side_design_governor_operating_notes_ja.md
                            （第0節・第2.1節・第3.15節、last_updated_at）、
                            本Evidence File（新規）。
Validation                : N/A（設計Discussion記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 長期戦Task（Phase 3実装）着手時、
                            `long_running_mode_active`をtrueへ切替。
                            軽量Compaction Count Trackerは、その時点で
                            新規作成する。
Exact Next Route          : Phase 3設計完了・Codexからの引き継ぎ待ち。
```
