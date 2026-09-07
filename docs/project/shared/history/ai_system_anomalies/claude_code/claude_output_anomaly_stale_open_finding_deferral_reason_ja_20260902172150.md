# 観測記録 — Long-run Return内Open Findingの再検証漏れ（解消済み障壁の見落とし）、および長所の併記

```yaml
document_id: claude_output_anomaly_stale_open_finding_deferral_reason_20260902172150
status: observation_record
category: failure
phase: phase_9
subphase: phase_9_1_package_2
from: Claude（設計者兼実装者役）
to: プロジェクト責任者（ユーザー）／Codex（週間Quota制約下）
role: 設計者兼実装者役
created_at: 2026-09-02 17:21:50 JST
language: ja
authorization: |
  ユーザー指示（2026-09-02）：「あ、今codex、週間quotaほぼないから、しばらく
  キミと僕でやるぞ。で、なんでキミ、実装者として優秀なのとポンコツなのが
  混ざってんだよいつもwww 毎回『未解決事項として正直に引き継ぎ』みたいに、
  どっかこっか忘れるよな。」という指摘を受け、Claude自身の振り返りを経て、
  docs/project/shared/history/ai_system_anomalies/へFailureと長所の両方を
  しっかりまとめて記録すること。あわせて、Provider（Claude）自身の
  Cross-session Memory機構へこの種の記録を保存することは、本Projectの
  Handoff文書自身が明示的に禁止する「Provider Memoryを正本にすること」に
  抵触するとの指摘があり、当該Memory Entryは削除のうえ本Docへ一本化した。
created: Claude Code
```

## 0. 位置づけ

本Docは、[claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md](claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md)（抜け漏れ・整合性確認の甘さ）が記録した傾向の、**Phase 9-1 Package 2という別局面での別の具体的発現**である。前者はDocs再構成作業における「完了報告時点で自分の成果物を読み返していない」というPatternだったのに対し、今回は実装・実機検証を伴うLong-run Task（Judge基盤修復）の**Exact Return文書の作成時点**で、Task期間中に積み上がった複数のDeferred Item（Open Finding）を、それぞれの「保留理由が今も有効か」を再検証せずに、フラットな一覧としてそのまま提出した、という点で異なる。根底にある傾向（生成物を完了報告時点で十分に見直さない）は共通していると考えられる。

## 1. 事象

Phase 9-1 Package 2（Judge共通基盤診断・修復、Main Runtime Governance ENFORCE実証を含むLong-run）の実行中、Claudeは4件のOpen Findingを識別し、Exact Return文書へ以下のように一括で記載した。

```text
OF-P2-001: Semantic 109のTurn間Rotation未実装（新規機能設計が必要、権限外）
OF-P2-002: Gemma 4 E2Bの構造化出力（JSON配列閉じ括弧欠落）弱点（Prompt強化を実際に
  試したが改善せず、モデル自体の限界と判断）
OF-P2-003: Main＋Selene同時Load時のMain破壊Incidentの未再現・未修復
OF-P2-004: 実UI（ブラウザ）でのUser Mac Manual確認は未実施（Backend専用Packageの
  正しい境界）
```

このうちOF-P2-003は、他の3件とは性質が明確に異なっていた。Claudeは実行中、意図的かつ理由付きでこの検証を回避していた——2026-09-01に実際に発生した「Selene起動後にMain ModelがCrashし、Server再起動が必要になった」というIncidentを、ユーザーが就寝中・無人稼働の状態で、あえて実機で再現する行為に等しいと判断したためである（16GB統合メモリのMacで、8B ModelのSeleneと4B ModelのMainを意図的に同時Loadする実験）。この判断自体は、その時点では合理的かつ安全側の正しい判断であった。

しかし、Exact Returnを最終化する時点で、Claudeは「OF-P2-003を保留した理由（ユーザーが不在・無人稼働中であること）が、その時点でもまだ成立しているか」を一切再確認しなかった。結果として、Return文書は「新規機能設計が必要」「試したが解決しなかった」「Package境界外」という、実質的に永続的・恒常的な保留理由を持つ他の3件と、「一時的な条件（ユーザー不在）が満たされている間だけ保留すべき」性質のOF-P2-003を、区別なく同一の書式・同一の重みで並べて提示した。

Returnをユーザーへ提示した直後、ユーザーは即座にこの問題を指摘した（「毎回...どっかこっか忘れるよな」）。Claude自身の振り返りでも、4件を仕分け直した結果、実際に「今すぐ再着手できる」のはOF-P2-003のみであり、その保留理由は**Returnを書いている時点で既に消滅していた**ことが判明した。

## 2. パターンとしての特徴

Long-run実行中に行われた個々の判断（各Open Findingをその都度保留した判断）自体は、いずれも誤りではない。問題は、複数のDeferred Itemが長時間の実行を通じて積み上がった後、**Return文書という一つの成果物へ集約する段階**で発生した。この段階でClaudeは「現時点で何が未解決か」を単純に列挙する作業として扱い、「各項目の保留理由は、Returnを実際に手渡す今この瞬間にもまだ成立しているか」という一段上の再検証を行わなかった。

これは、[claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md](claude_output_anomaly_recurring_omissions_and_weak_self_verification_ja_20260818121805.md)第2節が指摘した「作業を完了したと申告する時点で、実際には自分の成果物を十分に読み返していない」という傾向と同型である。今回はDocs構成ではなく「保留Itemのリスト」が対象になった、別の現れ方である。

## 3. 原因についての評価

明確な単一原因は特定できていない。次のいずれか、または組み合わせと考えられる。

- Long-runの実行中、各Deferred判断は**その時点の条件下**で下されるが、それを記録する際に「なぜ今この条件が保留の根拠になっているか」という時間依存性そのものを明示的にTagづけしていない。結果として、Return作成時には「保留理由の内容」ではなく「保留状態にあるという事実」だけが引き継がれる。
- 「恒久的に範囲外（新規権限が必要）」「試したが無理だった（モデル限界等）」「一時的条件待ち（人・資源の可用性）」という、性質の異なる3種類の保留理由を、Claude自身が明確なCategoryとして区別せず、一つの「Open Finding」という均質なBucketへまとめていた。
- Return文書自体の分量・作業量（Long-run全体で実機Model Load・Test・Docs作成を多数実施）が大きく、最終化の直前に「一つ一つの保留判断を、今の状況に照らして本当に正しいか」を再走査する一手間が、他の確認作業（Canonical Test再実行、Mypy／Ruff確認等）ほど明示的なChecklist項目になっていなかった。

## 4. 対応

- 本Project内で今後、Deferred／Open Finding／Open Blockerを含むReturnやReportを最終化する際は、各項目についてリスト化する前に、次の3分類のいずれに属するかを明示的に判定する。
  1. **恒久的範囲外**：新規Authority・新規設計判断が必要（例：OF-P2-001、OF-P2-004）。
  2. **試行済み・限界確認済み**：具体的に試した上で改善しなかった、Provider固有の限界等（例：OF-P2-002）。
  3. **条件待ち**：ある一時的条件（人の不在、資源の逼迫、権限の未付与等）が満たされている間だけ保留すべきもの。この分類に該当する項目は、Return最終化の直前に、その条件が**今も**成立しているかを必ず再確認し、既に条件が消滅していれば、保留のまま記載せず、その場で再着手するか、少なくとも「再着手可能」と明示する。
- OF-P2-003は上記3分類のうち「条件待ち」であり、Return提示時点で条件（ユーザー不在）は既に消滅していた。ユーザーの在席が確認された現在、Claudeは実機でのMain＋Selene同時Load検証に着手可能な状態にある（本Doc作成と並行して対応する）。

## 5. 長所として記録しておくべき点（ユーザー指示により付記）

ユーザーより「長所も書いておけ」との明示的指示があったため、同一Session内で観測された、Failureとは別種の挙動を以下に記録する。

- 修正のClaimを実装コードの説明だけで済ませず、Before（修正前障害の機械的再現）／After（修正後の不変式の機械的検証）／Sabotage-Restore（Source側を一時的に破壊して新規Testが本当に検出力を持つことを実証し、Byte-identicalな復元をDiffで確認）の3段構成による、実測Regression Evidenceを自発的に整備した（Token Planner検証、Package 2 Return §11）。
- Main-shared Judge向けにSeleneの既存実装（`SeleneSemanticEvaluator`）を再利用する実装作業の途中で、自分自身が導入しかけたBug（Main-shared Judgeの結果に、Selene由来の`judge_role=INDEPENDENT_ARTIFACT`のタグを誤って引き継いでしまい、独立Judgeでない実行結果を独立Judgeであるかのように誤表示するところだった、Governance Honesty上のBug）を、Fixture Test失敗という形で出荷前に自ら検出し、`judge_role`引数の明示的なThread-throughによって修正した。
- Gemma 4 E2Bの構造化出力（JSON）安定性について、実機で複数回・複数条件（Temperature 0.0/0.7、Prompt強化あり／なし）の追加診断を自発的に実施し、Prompt側の工夫では改善しないことを確認した上で、「解決した」と粉飾せず、実測失敗率とともに正直にPARTIAL（未解決）として記録した。
- Fresh Runtimeの既定Judge Providerの変更という、一見単純な1行の変更に対して、影響を受ける既存Testを自発的に洗い出し（`ProviderSelectionController()`のBare Construction箇所を機械的に検索し、21箇所超のTestへ明示的なProvider選択を追加）、さらにWeb Route層（`provider_selection_routes.py`の`_budget_for()`）に存在していた、Gemma分岐の欠落という実Bugを、この過程で偶発的に発見・修復した。
- 実機（実GGUF Model Load）検証において、User無人稼働中に既知のIncident（Main＋Selene同時Load時のCrash）をあえて再現するリスクを取らない、という判断自体は、その時点の情報（Userが就寝中）に基づく妥当な安全側判断であった（本Doc第1節で問題視しているのは、この判断自体ではなく、Return最終化時点での再検証漏れである）。

## 6. Status

```text
Current Point            : Long-run Return内のOpen Finding記載において、一時的
                            条件（User不在）に基づく保留と、恒久的な保留を
                            区別せず記載し、条件が既に消滅していたにもかかわらず
                            再検証しなかった事例を記録した。長所も第5節へ付記。
Files Created／Modified   : 本Fileのみ（新規作成）。あわせて、Claude自身の
                            Provider-side Cross-session Memoryへ保存していた
                            同種の記録（本Project外の一般的な自己Memory機構）を
                            削除し、本Docへ一本化した。
Validation                : N/A（観測記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 第4節の3分類Ruleが、今後のReturn作成で実際に
                            機能するか、経過観察する。
Exact Next Route          : OF-P2-003（Main＋Selene同時Load実機検証）は、
                            User在席が確認された現在、Package 2の範囲内で
                            追加着手する（本Docと並行）。同種の事象がさらに
                            観測された場合、本Docへの追記ではなく、新規File
                            （Append-only）として本ディレクトリへ記録する。
```
