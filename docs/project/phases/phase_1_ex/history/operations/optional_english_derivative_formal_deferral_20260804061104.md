# Optional English Derivative Formal Deferral

```yaml
document_type: phase_deferral_record
phase: phase_1_ex
status: accepted_non_blocking_deferral
created_at: 2026-08-04 06:11:04 JST
decision_authority: user
reviewer_role: 設計統括者役
owner_role: プロジェクト責任者役
```

## 1. Deferred Scope

Phase 1-exでは、次の非History Stable文書に対する英語派生版の一括作成を必須Blockerにしない。

```text
docs/project/current/**
docs/project/shared/**
docs/public/**
```

`history/**`は英語派生対象外である。Existing Public Documentation RAGの日本語／英語8文書は実装済みCorpusとして別途維持する。

## 2. Reason

- 日本語正本、Final Lossless、Recovery、Test、BackupおよびGitの完了に必要な情報は既に日本語正本で保持される。
- 英語派生版は同じ粒度と意味を維持する必要があり、Phase Closureを止めて急ぐより後続の専用Taskで検証する方が安全である。
- 本Deferralは情報削除、正本粒度の縮小または日本語正本の弱体化を許可しない。

## 3. Impact

Phase 1-exのRuntime、Safety Boundary、Docs Reconstruction、Recovery、Backup、Git、Public Demo、Documentation RAGおよびPhase 2開始可能性への未解決影響はない。

## 4. Re-entry Trigger／Target

- ユーザーが作業余力を確保した時点
- Phase 2前半または対外文書の英語対応が必要になった時点
- Public Corpus、READMEまたは対外説明の英語整合性が次Gateの前提になった時点

## 5. Verification

- 各英語版は対応する日本語正本と同じ粒度を持つ。
- 概要化、意味変更、名義変更、Authority変更または実装済み範囲の過大表現を行わない。
- 日本語正本Path、SnapshotまたはDigestへ追跡できる。
- Link、Terminology、Privacy／SecretおよびPublic Boundaryを独立検証する。

## 6. Acceptance

ユーザーは2026-08-04に「英語版はまだいい」と明示し、Formal Deferralを承認した。本ItemはPhase 1-ex完了のBlockerではない。
