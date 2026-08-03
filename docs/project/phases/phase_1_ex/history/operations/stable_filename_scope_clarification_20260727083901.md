# Stable Filename Scope Clarification Record

```yaml
document_id: stable_filename_scope_clarification
phase: phase_1_ex
status: corrected
language: ja
created_at: 2026-07-27 08:39:01 JST
owner: 設計統括者役
user_authorized: true
git_operation: none
deletion: none
```

## Correction

直前の説明で`roadmap_ja.md`だけを例示したため、TimestampなしStable Filename規則がRoadmapだけに適用されるように読める曖昧さがあった。

正しい規則は次である。

```text
TimestampなしStable Filename:
  Current Canonical全部
  Shared Stable全部
  Public Current全部
  Phase Stable全部
  Phase Index
  Phase Lossless Compilation
  既存DocsのLossless再整理後正本
  Project Continuity Master
  Design Governance Handoff

Timestamp付きFilename:
  History Snapshot
  Handoff
  Status
  Review
  Evidence
  Change Record
  Append-only Documentation Index Snapshot
```

`roadmap_ja.md`は例に過ぎず、特別扱いではない。

## Deferred Documentation Production

本訂正では、README、LICENSE、Canonical Docs、Public Docsまたは英語派生版を作成していない。

ユーザー指定の着手順に従い、Canonical／Public Docs、既存DocsのLossless再整理、README、Overview、Concept、Roadmap、設計書およびLICENSE等は後続作業として扱う。英語版はPhase 1-ex後半の全体Refreshまで延期する。

Lightning関連作業が完了した時点では、まず`roadmap_ja.md`の現在進捗を更新する予定である。

READMEには、現在の実行環境制約により高性能Model等を使用できていないこと、および将来変更予定であることを記載する予約がある。

本Recordは予約内容を保持するだけであり、ユーザーの着手指示前に対象文書を生成しない。

## Snapshot／SHA-512

```text
Documentation Rules Before:
6eb978db4035b0f27cafe64fab5a1f43426d63988a844e58988f34eea48fabefd56b33f1c19faa5e09371e1454a99ecdfe3182d5f6f7d0384125f560044420de

Documentation Rules After:
8c5900129d8835e1d1924938a4c31a4f4714cc3c8279ead634c2b6ee89f62244854b2a0fa010e1c1304cfb388b184f2e4865e190bb4a4c81f45f22280409d070

Documentation Operations Before:
1d6ccc365ed398aabc3ab17ec5a10337f4f7964a3b16389e09b10a238b408d98034c358069c71bbf415ce8f81cea01f92ae19e6e4b4c33bee6e1c326b09cd506

Documentation Operations After:
4704fc292c0488cde083326dfe18163f3e9ff6fce2b2c80175258f728220dc305cf2488c9367d415fdeb40f0c1feb234fe6062400eb17b3dc975967382403eb6

Phase Index Before:
80d1ffc951d12b72234d6fc6f8650c4696998663588feffb2522702bf0b726a2eec62af9d6278c19a4a882f605d17c39767827c6144544a658e48ba1207d01dd

Phase Index After:
b08f986e7d6145a79f48851fea911ee0e80acf3c4a5f5d8f6867abf52cd36beb5a0b1be3199b9c795344445680488a2f034b33e83c9526091f50aed7d790d190
```

各Before／After Snapshotは対応Stable原文との完全一致を確認した。

