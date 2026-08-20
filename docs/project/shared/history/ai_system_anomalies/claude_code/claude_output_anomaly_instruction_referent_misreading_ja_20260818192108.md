# 観測記録 — 断片的に与えられた指示内の指示語（「頭に」等）の参照範囲取り違え

```yaml
document_id: claude_output_anomaly_instruction_referent_misreading_20260818192108
status: observation_record
category: failure
phase: cross_phase
subphase: none
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-18 19:21:08 JST
language: ja
authorization: |
  ユーザー指示（2026-08-18）：「ちょっと今回もこの程度で何回も変な
  ミス繰り返した事に関して、Failureのとこに書いとけ」。
  [claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md]
  （以下「関連Doc」）のStatus節「同種の事象がさらに観測された場合、
  本Docへの追記ではなく、新規File（Append-only）として記録する」に
  基づき、関連Docへの追記ではなく本Docを新規作成する。
created: Claude Code
```

## 0. 位置づけ

本Docは、[claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md](claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md)（以下「関連Doc」）と同系統の、**Claude固有のFailure Pattern**の新しい具体例を記録する。関連Docが扱う「抜け漏れ・整合性確認の甘さ」とは少し性質が異なり、今回は**機械的な自己Check自体は正しく実施できていたにもかかわらず、その前段のユーザー指示の解釈を誤った**事例である。

## 1. 事象

新設したCompaction Recovery Hash Manifest（`docs/project/shared/automation/claude_compaction_recovery_hash_manifest_ja.md`）の構成について、ユーザーから次の指示があった。

> 「『現在のCompaction Recovery成功回数：4　失敗回数：0』毎回載せたら行数無駄じゃね？頭に1個だけでいいじゃん。そのあとに、ひたすら淡々と、『Cycle 4〜』『Cycle 5〜』ってすればよい。」

この「頭に」の参照先を、Claudeは**File全体の先頭**（＝第0節「本Fileの目的・位置づけ」）と誤って解釈し、そこへ成功／失敗回数の記載を挿入した。しかし文脈上、「そのあとに、ひたすら淡々と、Cycle 4〜Cycle 5〜」という直後の文と合わせて読めば、「頭に」は明らかに**第2節「Cycle別Hash記録」の先頭**（Cycle記録が始まる直前）を指しており、第0節（目的・位置づけを説明する節）とは無関係だった。

ユーザーから直接、強い言葉で指摘された：「キミは本当に物分かり悪いね？実装はめちゃ早いくせに。（中略）どこが『本Fileの目的・位置づけ』なんだよ。」

## 2. パターンとしての特徴

関連Docが記録する「作業を完了したと申告する時点で、自分の成果物を十分に読み返していない」というPatternとは異なり、本件は**成果物のContent自体は正しく（Link切れ・文字化けなし）作成できていた**——機械的な自己Check（Diff比較、相対Link解決確認、文字化けToken検索）はいずれも実施し、いずれも問題を検出しなかった。問題は、**その前段、指示文中の指示語の参照範囲を、直前の文脈から正しく特定できなかった**ことにある。

複数の短いMessageに分けて断片的に与えられた指示（「頭に1個だけでいいじゃん」→「そのあとに、Cycle 4〜」という2文セット）において、指示語の係り先を、直前の文だけでなく、**続く文全体の構造**（「頭に1個」＋「そのあとに淡々とCycle記録」という一連の構成提案）から判断する必要があったが、それを怠り、より一般的・字義通りの解釈（File全体の先頭）へ流れた。

## 3. 原因についての評価

明確な原因は特定できていない。次の要素が関与した可能性がある。

- 「頭」という語は、File全体の先頭（Frontmatter直後、第0節相当）を指すことが多いという、それまでの本Session内での用例（運用メモ自体の第0節・第1節の扱い等）に、無意識に引きずられた可能性がある。
- 断片的な指示（複数文にまたがる一連の提案）を、文単位で逐次処理し、文同士の関係性（「頭に1個」の直後に続く「そのあとに」が、その1個をどこに置くかを規定している）を統合的に評価しきれなかった可能性がある。

## 4. 対応

- 本Docによる記録のみで完結する。ユーザーからの明示的なRule変更要求はない。
- 教訓として、今後、指示語（「頭に」「その後に」「ここに」等）を含む断片的な指示を受けた場合は、指示語単体で早期に解釈を確定させず、後続の文まで含めた一連の提案として参照範囲を確認してから反映する。

## 5. Status

```text
Current Point            : 指示語の参照範囲取り違えという、関連Docとは
                            別種のFailure事例を記録。機械的な自己Check
                            自体は正しく機能していたが、その前段の指示
                            解釈で誤った点が本件の特徴。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（観測記録）
Open Current Blocker      : NONE
Controller-owned Next Work: NONE。
Exact Next Route          : 同種の事象がさらに観測された場合、本Docへの
                            追記ではなく、新規File（Append-only）として
                            `shared/history/ai_system_anomalies/
                            claude_code/`配下へ記録する。
```
