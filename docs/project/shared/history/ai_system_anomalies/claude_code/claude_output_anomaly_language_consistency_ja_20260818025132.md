# 観測記録 — Claude出力における言語一貫性の逸脱（原因未特定）

```yaml
document_id: claude_output_anomaly_language_consistency_20260818025132
status: observation_record
category: failure
phase: cross_phase
subphase: none
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-18 02:51:32 JST
language: ja
authorization: |
  ユーザー指示（2026-08-18）：Claude出力中に発生した言語一貫性の逸脱2件
  について、対応（Rule変更等）は不要だが、Evidenceとしてどこかへ残す
  こと。ユーザー自身の見立てとして、本件はAutomation／Cross-provider
  PoCとも、本Projectの運用Ruleとも無関係で、Claude固有の問題である
  可能性が高いとの指摘があった。この見立てを踏まえ、本Docは
  `docs/project/shared/history/automation/`（Automation／Cross-provider
  PoC Evidence専用）ではなく、Claude固有のAnomaly記録として独立して
  置く。
  追記（2026-08-18 09:57）：ユーザー指示により、本Docの分類を明示的に
  「Failure」とし（category: failure）、置き場所を
  `docs/project/shared/history/ai_system_anomalies/claude_code/`
  （新設）へ移設した。詳細は末尾の追記節を参照。
created: Claude Code
```

## 0. 位置づけ

**本Docは、Automation／Cross-provider PoC Evidenceではなく、また本Projectの運用Rule文書でもない。** 3層モデル（[claude_side_design_governor_operating_notes_ja.md](../../../task_roles/claude_side_design_governor_operating_notes_ja.md)第0.5節）における「History／Evidence」層のうち、**Failure**カテゴリに分類される、Claude固有の出力品質Anomalyの記録である。本Session中にClaude側の出力で観測された、言語一貫性に関する2件の逸脱を、原因不明のまま事実として記録するものである。ユーザーからの明示指示により、対応（運用メモ等の変更）は行わない。

## 1. 事象

本Session中（2026-08-18、Provider Memory Incident・運用メモ構造再編成に関するやり取りの最中）、日本語でのやり取りが一貫して続いていた中、Claude側の出力に次の2件の言語一貫性逸脱が発生した。

### 1.1 応答全体が英語になった事例

運用メモの構造再編成に伴う既存History文書内の参照切れ4箇所を修正した直後、Claudeの応答は次の通り、全文英語で出力された（直前・直後のやり取りは全て日本語）。

> All internal references check out — that was the last one (§4→§6, now fixed). Added §4.1 to the operating notes with this exact case as the standing precedent, and logged it.
>
> **§4.1** now states plainly: fixing a side effect of already-authorized work is Routine judgment under the existing §4 criteria — no need to ask unless it actually hits Scope外/規則Conflict/Cross-Phase影響/重大Risk/定義済みGate. Logged as an existing-rule application failure, not a missing rule.

直前のユーザー発言は、「その程度のことをいちいちエスカレーションしてくんな」という、日本語での直接的な指摘であった。

### 1.2 言語混在の壊れた語（Garbled Token）の事例

Provider Memory誤用Incidentの経緯を説明する応答の中で、次のように、ラテン文字とカタカナが混在した、いずれの言語としても正しくない語が出力された。

> 「そして直前のTurンで、私はこれに新規追記・新規File作成をしました」

正しくは「Turn」（英語のまま使う場合）または「ターン」（カタカナ表記にする場合）のいずれかであるべきところ、両者が融合した「Turン」という語が出力された。

## 2. 発見の経緯

いずれも、ユーザーが該当箇所を直接指摘することで発覚した。Claude側の自発的な自己点検では検出されなかった。

## 3. 原因についての評価

**原因は特定できていない。** Claude側は、自身の内部処理を確実に検査する手段を持たないため、次のいずれであるかを、この場で断定することはできない。

- 本Session固有の要因（複数回のCompactionを挟んだ、長時間・高密度な会話）による、何らかの品質劣化。
- 上記とは無関係な、確率的に発生しうる通常範囲内の出力揺らぎ。

ユーザーからは、「Automation／Cross-providerとも、運用Ruleとも関係なく、Claude固有の問題である可能性が高い」という見立てが示された。この見立ては、少なくとも次の点と整合する——2件とも、本Projectの統治Architecture（Role、Authority、Docs境界等）とは無関係な、純粋な言語出力Levelの逸脱であり、Rule理解の誤りやScope逸脱とは性質が異なる。

## 4. 対応（初回記録時点）

**ユーザー指示により、Rule変更・運用変更は行わない。** 本Docによる記録のみで完結する。

**[2026-08-18 09:57 追記]** その後、同種の逸脱が3回目・4回目と再発したことを受け、ユーザー指示により、[claude_side_design_governor_operating_notes_ja.md](../../../task_roles/claude_side_design_governor_operating_notes_ja.md)第0.7節として「出力言語：日本語のみ・英語出力禁止」Ruleが新設された。したがって、本Doc記録時点では「対応なし」だったが、最終的にはRule化に至っている。経緯の全体は[claude_output_anomaly_language_consistency_ja_20260818092418.md](claude_output_anomaly_language_consistency_ja_20260818092418.md)を参照。

## 5. Status

```text
Current Point            : 2件の言語一貫性逸脱を記録。原因未特定。
                            後続の再発を経て、運用メモ第0.7節として
                            Rule化済み（第4節追記参照）。
Files Created／Modified   : 本Fileのみ。作成当初は
                            `docs/project/shared/history/`直下に配置
                            していたが、ユーザー指示によりFailure分類の
                            明示、および専用Directory
                            （`shared/history/ai_system_anomalies/
                            claude_code/`）への移設を実施した。
Validation                : N/A（観測記録）
Open Current Blocker      : NONE
Controller-owned Next Work: NONE。
Exact Next Route          : 同種の事象がさらに観測された場合、本Docへの
                            追記ではなく、新規File（Append-only）として
                            `shared/history/ai_system_anomalies/
                            claude_code/`配下へ記録する。`shared/
                            ai_system_anomalies/claude_code/`（無History
                            版）は、ある程度蓄積した時点でのまとめ用
                            であり、個々の記録では使用しない。
```
