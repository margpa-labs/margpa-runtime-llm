# MARGPA Runtime LLM Documentation Index

- 文書ID: `documentation_index`
- 状態: `current`
- 作成日時: `2026-07-21 19:19:15 JST`
- 更新日時: `2026-07-21 19:19:15 JST`
- Snapshot: `20260721191915`
- 作成担当: 設計者役担当Task
- 正本言語: 日本語
- supersedes: `documentation_index_20260721185031.md`

## 1. Current Position

```text
Public Author／Research Name           : Nazuna Research
Phase 1-G                              : Accepted
Phase 1-H                              : Accepted
Web／Lightning User Manual             : Updated／Current Candidate
User Mac Acceptance                    : Waiting
Phase 1-F／1-G／1-H Lightning Native   : Deferred／Batch Gate
Phase 1-ex                             : Accepted Reservation／Not Started
Docs Writer until Phase 1-ex Complete  : Current Designer Task Only
Phase Compilation Owner                : Current Designer Task
README Roadmap Priority                : Accepted Requirement
Initial GitHub Publication             : Deferred until Phase 1-ex completion
Git                                     : Not Initialized
```

## 2. Snapshot Resolution

Phase 1-H Accepted Evidence、Lightning User Manual、Current Phase状態は[documentation_index_20260721185031.md](documentation_index_20260721185031.md)から継承する。

本Snapshotは、Phase 1-ex完了までのDocumentation Writerを現在の設計者役担当Taskへ一時統一し、README内でRoadmapを最優先導線にする要件を追加する。

## 3. New Accepted Requirements

[phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md](requirements/phase_1_ex_interim_documentation_single_writer_and_roadmap_priority_requirements_20260721191915.md)

主要決定：

- Phase 1-ex完了まで`docs/`の全Fileを現在の設計者役が作成する。
- Implementer Status、External Docs Statusを含め、他担当はDocsへ直接書き込まない。
- Phase単位Lossless Compilationも現在の設計者役が担当する。
- README、LICENSE、CITATION、NOTICE等のPhase 1-ex Documentation成果物も現在の設計者役が作成する。
- License条件はユーザーが決定する。
- README上部で`docs/public/roadmap_ja.md`を中核公開文書として強調する。
- Phase 1-ex完了後のWriter分担は、新しいRole／Authority Policyで決める。

## 4. Common Handoff

[common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md](handoffs/common_documentation_single_writer_until_phase_1_ex_completion_20260721191915.md)

このHandoffを、Phase 1-ex完了までの設計者役、実装者役、対外Docs役、将来のPhase別設計者役へ共通適用する。

## 5. Temporary Ownership Matrix

| Artifact | Writer until Phase 1-ex Completion | Input Provider |
|---|---|---|
| Requirements／Architecture／ADR | 現在の設計者役 | ユーザー／各担当 |
| Implementer Handoff | 現在の設計者役 | 設計者役 |
| Implementer Status Document | 現在の設計者役 | 実装者役の報告Payload |
| Review／Index | 現在の設計者役 | 実装Evidence |
| README／Public Docs | 現在の設計者役 | ユーザー／対外Docs役の提案Payload |
| Lossless Phase Compilation | 現在の設計者役 | Frozen Source Set |
| Project Continuity Master | 現在の設計者役 | 全Canonical Source |
| LICENSE文面 | 現在の設計者役がFile化 | ユーザーが権利条件決定 |

## 6. README Roadmap Contract

```text
README Position     : Project概要直後または同等に目立つ上部
Roadmap Link        : docs/public/roadmap_ja.md
Roadmap Role        : Current Position／All Phases／Future Integrationの中核公開文書
README Tone         : 日本語敬語
README End          : English Abstract
Broken Roadmap Link : Publication Gate Fail
```

READMEへRoadmap全文を複製せず、Roadmapを最初に参照するよう強く案内する。

## 7. Unchanged Boundaries

- Phase 1全体の完了宣言は未実施である。
- Lightning Native／Public URL Gateは未完了である。
- Phase 1-exは未開始である。
- Docs Migration、Lossless Compilation実行、README生成はまだ許可されていない。
- Git／GitHub公開は未実施である。
- Public License条件はまだ最終確定していない。

## 8. Next Gate

```text
User Mac Acceptance
  → Batch Lightning Upload／Native／Web Validation
  → Cross-environment Final Review
  → Phase 1 Completion Gate
  → Backup
  → Phase 1-ex Start Authorization
  → Single WriterによるDocs／Git／Public再整備
  → Phase 1-ex Completion Gate
```

## 9. Authorization Boundary

本Indexと新Requirements／Handoffの作成は、Source変更、Phase 1-ex開始、Docs Migration、Lossless Compilation実行、README／LICENSE生成、Git初期化、Commit、Push、GitHub公開またはLightning操作を自動許可しない。

## 10. Append-Only

前Indexと既存Role Policyを変更せず、Documentation単一WriterとRoadmap最優先導線を記録した新TimestampのIndexを追加した。新しいTimestampの本Indexを最新とする。
