# Phase 9 Closure時 Roadmap要約版作成予約

```yaml
document_id: phase_9_closure_roadmap_summary_reservation_20260823154121
status: planned_not_started
document_type: append_only_planned_work
target_gate: phase_9_closure_before_finalization
recorded_at: 2026-08-23 15:41:21 JST
decision_authority: user
source_mutation_authorized: false
git_mutation_authorized: false
```

## 1. Decision

Phase 9 Closureへ入る前に、現行`roadmap_ja.md`を正本として、人間が短時間で全体像と現在地を把握できる「要約版Roadmap」を新規作成する。

Exact File名、配置先、言語、要約粒度、公開範囲および必須項目は、Phase 9 Closure開始前にUserが追加要件を提示し、その時点のAs-builtとRoadmap正本を照合してFreezeする。

## 2. Purpose

Phase 1〜9の長期履歴、Subphase、完了済み機能、延期事項およびPhase 10以降の計画が累積した後も、次を一読で確認できる入口を用意する。

- Projectの目的と研究Platformとしての中核価値。
- Phase 1〜9の主要成果とCurrent State。
- OFF／OBSERVE／ENFORCEを含む主要機能の成立範囲。
- 完了、部分成立、延期、未着手およびPhase 10以降の境界。
- 次に何を行うかと、詳細正本へ辿るLink。

## 3. Source-of-truth Boundary

要約版は新しいRoadmap正本を増やさない。

```text
Detailed Canonical Roadmap : roadmap_ja.md
Summary Roadmap            : derived navigation／overview document
History／Evidence           : existing Phase and Shared documents
```

- 要約版から詳細を削っても、元RoadmapまたはEvidenceを削除しない。
- 要約版と詳細版が衝突する場合は、Acceptedな詳細正本とAs-built Evidenceを優先する。
- 要約版には参照元Revision、生成時点、Source Pathおよび必要なDigest／Manifestを持たせる。
- Phase番号、完了状態、延期状態または機能の成立範囲を、読みやすさのために捏造・過剰単純化しない。

## 4. Phase 9 Closure時の作業候補

1. Userから要約版のExact要件を受領する。
2. Current Roadmap、Phase Index、Closure EvidenceおよびAs-builtを照合する。
3. 要約対象と詳細正本へ残す情報を分類する。
4. 要約版を新規作成し、正本へのLinkを付与する。
5. Phase／機能／状態のCoverage Matrixで抜けを確認する。
6. Link、Privacy、Secret、Project固有情報の公開範囲を検証する。
7. Phase 9 ClosureおよびPhase 10 READYのIndexから入口を接続する。

## 5. Non-authorization

本書は将来作業の予約である。現時点では`roadmap_ja.md`、関連Stable Docs、Source、GitまたはGitHubを変更しない。要約版作成開始、既存Roadmapの編集およびCommit／Pushは別Gateで扱う。

