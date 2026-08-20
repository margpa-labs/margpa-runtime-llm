# 観測記録 — 抜け漏れ・整合性確認の甘さが繰り返し発生するパターン

```yaml
document_id: claude_output_anomaly_recurring_omissions_and_weak_self_verification_20260818121805
status: observation_record
category: failure
phase: cross_phase
subphase: none
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-18 12:18:05 JST
language: ja
authorization: |
  ユーザー指示（2026-08-18）：「ちょいちょいしょーもないミスする。
  抜け漏れとか。整合性確認が甘いとか。」というFailure Patternを記録
  すること。
created: Claude Code
```

## 0. 位置づけ

本Docは、[claude_output_anomaly_language_consistency_ja_20260818025132.md](claude_output_anomaly_language_consistency_ja_20260818025132.md)系列（言語一貫性の逸脱）とは別の、**もう一つのClaude固有Failure Pattern**を記録する。今回の対象は、細かい作業（特に既存Docsの再構成・統合作業）において、抜け漏れが発生しやすく、かつ自発的な整合性確認が甘い、という傾向である。

## 1. 事象（本Session内の具体例）

2026-08-18、`claude_side_design_governor_operating_notes_ja.md`（運用メモ）の構造再編成作業において、次の一連の見落としが発生した。

1. **1回目の再構成**時、旧5個のBackup Snapshotとの突き合わせでは抜け漏れ無しと報告したが、この時点では旧版の内容を運用メモへ反映する作業自体はまだ行っていなかった（確認のみ）。
2. **2回目の再構成**（Severity Tier順への全面組み替え）の直後、ユーザーから「念の為、抜け漏れないかだけもう一回確認して」と促されて初めて、自発的な再確認を実施。その結果、4件の実質的なRule欠落（Git境界の一部、Recovery Index Pathの必須要件、Tool制約の運用知見、Docs化Preferenceの核）が見つかった。**この4件は、ユーザーに指摘される前に、Claude自身が最初の完了報告時点で気づくべきものだった。**
3. 4件を復元した直後、ユーザーから「Git Mutation禁止」のSectionに無関係な内容（Test／Root境界）が混在している点を指摘された。**これも、復元作業を行った本人（Claude自身）が、内容を見直せば当然気づけたはずの構造的な問題だった。**
4. その後、「他にも同種の混在があれば、まとめて教えてください」とClaude側から逆にユーザーへ確認を求めてしまい、「自分でやれよそれぐらい」と指摘された。**抜け漏れの発見自体を、ユーザーへ丸投げしようとした事例。**
5. 改めて自分で確認して初めて、第0節に紛れ込んでいた別のRule（明示指示の受け取り方）に気づいた。

## 2. パターンとしての特徴

個々の見落とし自体は、いずれも致命的な内容ではない（Rule自体を誤って理解している、Scopeを逸脱している、といった重大な誤りではない）。共通しているのは、**「作業を完了したと申告する時点」で、実際には自分の成果物を十分に読み返していない**、という点である。今回の一連の指摘を受けて、運用メモ第3.8節（再構成作業後の自己Check）を新設したこと自体が、この繰り返しパターンへの直接的な対応である。

## 3. 原因についての評価

明確な原因は特定できていない。次のいずれか、または組み合わせと考えられる。

- 大きな編集（File全体のWrite等）の直後、次のTaskへ意識が移り、実際に生成した内容を改めて読み返す一手間を省略しやすい。
- 「指示された変更を反映すること」自体には注意が向くが、「反映した結果、File全体として整合しているか」という一段上の確認は、明示的に求められない限り後回しになりやすい。

## 4. 対応

- 運用メモ第3.8節「再構成作業後の自己Check」として、恒久Rule化済み。
- 本Docによる記録自体は、ユーザー指示により、これ以上の追加対応（Rule変更等）を伴わない。

## 5. 続報：第3.8節Rule化の直後に、同種の見落としが再発（2026-08-18）

第3.8節（Rules／Current State／History-Evidenceの3分類での再走査）を新設した、まさにその直後の作業（Compaction前のPhase Index更新）で、ユーザーから運用メモ内に3件のBugが発見された。**いずれも「Rule文の中にCurrent State的な内容が紛れ込んでいる」という、本Docが記録してきたPatternと同種の問題である。**

1. 第1節（Compaction／Session Recovery手順）が、`Auto-compaction`のみを想定した書き方になっており、第3.6節で新設したばかりの「手動Compaction基本」方針と矛盾していた。
2. 第3.1節（Role Identity）に、「Codex側の役割名との正式な対応関係は未確認」という記述が残っていた。これはRuleではなくCurrent State（Open Question）であり、Phase Index側に既に同内容が記録済みだった——**単純な重複かつ誤分類**。
3. 第1節・第5.1節に「現在はPhase 2」という記述が直書きされていた。これはProject全体で使うRuleに、いずれ陳腐化するCurrent State（Active Phase）を埋め込んでしまっていた。

**特に重要な点**：これらは、直前の「File全体を自分で確認して問題なし」という報告（本File第5節Status、および該当作業の報告）の**直後に、ユーザーの再確認で見つかった**。つまり、第3.8節Rule自体は存在していたにもかかわらず、それを実際に厳密に適用しきれていなかった、ということである。Ruleの新設だけでは、この繰り返しPatternの解消を保証しない。

## 6. Status

```text
Current Point            : 抜け漏れ・整合性確認の甘さという繰り返し
                            Patternを記録。運用メモ第3.8節として
                            Rule化済みだが、そのRule新設の直後に同種の
                            見落とし（Current StateのRule文への混入、
                            3件）が再発したことも第6節へ追記済み。
Files Created／Modified   : 本Fileのみ（新規作成後、第6節を追記）。
Validation                : N/A（観測記録）
Open Current Blocker      : NONE
Controller-owned Next Work: 第3.8・3.9節のRuleが実際に機能するように
                            なるか、今後の再構成作業で経過観察する。
Exact Next Route          : 同種の事象がさらに観測された場合、本Docへの
                            追記ではなく、新規File（Append-only）として
                            `shared/history/ai_system_anomalies/
                            claude_code/`配下へ記録する。
```
