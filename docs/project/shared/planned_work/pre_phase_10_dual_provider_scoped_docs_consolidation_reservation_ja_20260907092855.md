# Phase 10直前 Claude／Codex 独立Docs統合 予約

```yaml
document_id: pre_phase_10_dual_provider_scoped_docs_consolidation_reservation_ja_20260907092855
document_type: planned_work_reservation
document_state: reserved
phase: phase_10
recorded_at: 2026-09-07 09:28:55 JST
language: ja
authority_owner: Nazuna Research
append_only: true
```

## 1. 目的

Constitution関連資料の質を高めるため、Codexによる全範囲Docs統合の直前に、ClaudeとCodexが互いの成果へ影響されない形で、指定範囲のDocs統合をそれぞれ行う。

ClaudeとCodexは異なる観点の統合結果を作る可能性が高く、その差分を後続の全範囲Docs統合における有効な材料として利用する。

## 2. Stable作成対象

Stableを新規作成する範囲は、次に限定する。

- `docs/project/current/automation_cross_provider_compaction/`
- `docs/project/current/history/automation_cross_provider_compaction/`
- `docs/project/shared/`配下にある、Constitution関連で有効な資料の対象フォルダ

各Stableは完全新規ファイルとして、`shared/`直下の対応する各対象フォルダ内に作成する。

上記以外の範囲にはStable関連ファイルを作成しない。

## 3. 探索・読み取り範囲

Stableの作成対象は前節の指定範囲に限定するが、統合品質を高めるための探索・読み取り範囲は`docs/`配下の全ファイルとする。

## 4. Claude側の統合

1回目は`docs/`配下の全ファイルを読み込んだ後、指定範囲の各Stableファイルを新規作成する。

2回目は、作成したStableに抜け漏れがなく、Losslessにまとめ直されているかを、再度`docs/`配下の全ファイルを読みながら確認する。

補正が必要な場合も既存Stableを上書きせず、Append Onlyまたは新規ファイルの作成によって対応する。

## 5. Codex側の独立統合

可能であればCodexも、Claudeが作成した統合Docsを一切見ない状態で、同じ対象範囲・読み取り範囲・2回の確認手順により独立したStableを作成する。

Codex側の独立作業が完了するまで、Claude側の統合DocsをCodexの入力・探索対象へ混入させない。

作成者を明確に区別できるよう、ファイル名には次のような識別子を付ける。

- `claude_side_...`
- `codex_side_...`

## 6. 後続工程

Claude側とCodex側の独立した指定範囲統合が完了した後、改めて全範囲のDocs統合を行う。

## 7. 現時点の境界

本書は将来作業の予約記録であり、具体的な設計、対象ファイルの最終選定、Stableの命名詳細、実施用Handoffは実行時に決定する。

## 8. Append-only追記 — Blind隔離方式の採用（2026-09-11 17:46:29 JST）

後続User Decisionにより、Claudeを先行させた場合にCodexがClaude側統合Stableを読まないための方式を、File名による注意喚起だけでなく、次の複合Contractとして設計した。

- 工程開始時に`docs/`全体からSource候補を確定し、両Providerへ同一のFreeze Manifest／Digestを渡す。
- Claude側成果物を`blind_preintegration/<run_id>/claude_side_sealed_until_codex_complete/`へ隔離する。
- Claude側File名へ`codex_do_not_read_until_blind_complete`を含める。
- CodexはDirectory全探索ではなくFreeze ManifestのSource PathをAllowlistとして読む。
- Codex側Handoff、Recovery、検索、RAGおよびUser RelayからClaude側内容を除外する。
- 両側成果物をDigest付きでFreezeした後だけUnseal／比較する。
- 誤読が生じた場合はBlind成立を主張せず、`BLIND_CONTAMINATED`として保存する。

現行の詳細運用設計は次を正本とする。

- [Phase 10直前 Claude／Codex 独立Docs統合 Blind運用設計](../automation/pre_phase_10_dual_provider_blind_scoped_docs_consolidation_operating_design_ja.md)

本追記はStable作成対象範囲を広げない。指定範囲外へのStable作成禁止、各Provider二回の全Source照合、Append-only補正、Claude側／Codex側の作成者識別および後続の全範囲Docs統合という元予約を全て維持する。
