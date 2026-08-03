# 任意英語派生版 Scope／延期予約 Record

```yaml
document_id: optional_english_derivative_scope_and_deferral_reservation
status: accepted_reservation
language: ja
created_at: 2026-07-27 23:06:12 JST
owner: 設計統括者役
phase: phase_1_ex
english_documents_created: false
```

## 1. 決定

Phase 1-ex Stage 6「Docs群、必要Doc・箇所の再整理または新規作成」において、作業余力がある場合は英語派生版も作成する。

英語版作成は必須Gateではない。余力がない場合は、未完了扱いでPhase 1-ex全体を停止せず、後日またはPhase 2前半へ明示的に延期する。

## 2. 対象

英語派生版の対象は、次のDirectory以下にある日本語Stable文書`*_ja`の全対象とする。

```text
docs/project/current/
docs/project/shared/
docs/public/
```

各Rootの下位Categoryも対象に含む。

## 3. 除外

上記三つのRoot内であっても、Path中に`history/`を含む全文書・全Artifactは英語派生版作成対象から除外する。

```text
docs/project/current/history/**
docs/project/shared/history/**
docs/public/history/**
```

History Snapshot、Append-only Index、Event、旧版、Before／After原文を翻訳、Rename、複製または`_en`化しない。

Phase文書、Handoff、Status、ReviewおよびRaw Historyも従来どおり英語版一括作成の対象外とする。

## 4. 翻訳規則

- 日本語版を正本とする。
- 英語版は`_en`を付ける。
- 概要版、短縮版または抄訳にしない。
- 日本語正本と同じ粒度、情報量および構造を維持する。
- 要件、根拠、設計判断、制約、例外、留意事項、既知の制限、未決事項および参照先を省略しない。
- 英語版だけに要件、権限、例外、状態または主張を追加しない。
- 意味の削除、弱化、強化、再解釈を行わない。
- Conflict時は日本語正本を優先する。
- 作成対象に含めた文書はJA／EN同等性を確認する。

## 5. 実施時期

優先順位：

1. Phase 1-ex Stage 6で、時間・Token・作業余力がある場合。
2. Stage 6で実施できない場合は後日。
3. それでも未実施の場合はPhase 2前半の予約作業。

延期時は、対象範囲、未作成理由および再開位置をCurrent Index、RoadmapまたはActive Phase Indexへ明示する。

## 6. Boundary

本Recordは英語派生版のScopeと延期先を予約するものであり、英語版を作成済み、翻訳済み、検証済みまたは公開済みへ変更しない。

英語版未作成だけを理由にPhase 1-ex、初回Commit、BackupまたはPhase 2移行を自動的に拒否しない。

