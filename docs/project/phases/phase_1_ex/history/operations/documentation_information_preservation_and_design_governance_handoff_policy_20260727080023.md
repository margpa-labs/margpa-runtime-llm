# Documentation Information Preservation／Design Governance Handoff Policy Record

```yaml
document_id: documentation_information_preservation_and_design_governance_handoff_policy
phase: phase_1_ex
status: accepted
language: ja
created_at: 2026-07-27 08:00:23 JST
owner: 設計統括者役
user_authorized: true
git_operation: none
deletion: none
```

## 1. 目的

ユーザー指示に基づき、Current Index History、Shared Category、Public History、設計統括者役専用Handoffおよび情報保存最優先運用を共通ルール・運用ルール・Role Authority・Project Continuityへ正式反映した。

本作業は、情報ロスによる再説明必要化、復元不能状態、判断根拠の断絶および機会損失を防ぐために行った。

## 2. 確認・採用したDirectory

```text
docs/project/current/history/index/

docs/project/shared/
├─ conventions/
├─ operations/
├─ task_roles/
├─ schemas/
├─ templates/
├─ user_manual/
└─ design_governance_handoff/

docs/project/shared/history/
├─ conventions/
├─ operations/
├─ task_roles/
├─ schemas/
├─ templates/
├─ user_manual/
└─ design_governance_handoff/

docs/public/history/
├─ overview/
├─ concept/
└─ roadmap/
```

既存の`operations/`、`user_manual/`および各Historyも正式構造として保持した。新Directoryの採用を理由に既存Categoryを削除していない。

## 3. Current Index History確認

ユーザーが`docs/project/current/history/index/`へ配置した次の2件を確認した。

```text
documentation_index_phase_1_ex_ja_20260727072019.md
documentation_index_phase_1_ex_ja_20260727072057.md
```

SHA-512：

```text
20260727072019:
9434b1569a9f53d6cf063609bb689e8fa2302519adc46e8d912dbcbeb65e162bfda0977bed24e702ff347bde581ecdb38e8500c79cc4e659e444f567e56f6e1b

20260727072057:
401d177338bfa01bc55c3a0b848d1774c261ed42a823319b80cd29ae43b5d06020811f4bfab077f7ae7b9fe499fe864457577dfb68dc7f7710b08241354790d6
```

`20260727072057`版は本作業開始前のCurrent Stable Indexと完全一致していた。

本作業ではさらに、Current Indexの更新前後原文を次へ保存した。

```text
Before:
docs/project/current/history/index/
documentation_index_phase_1_ex_ja_20260727075236.md

After:
docs/project/current/history/index/
documentation_index_phase_1_ex_ja_20260727075953.md
```

## 4. 確定した情報保存規則

次は情報ロスを一切許さない水準で、累積・自己完結の完全版として作成・更新する。

- 既存DocsのLossless再整理
- Current Canonical
- Project Continuity Master
- Shared Rules／Operations／Role／Schema／Template
- Phase Lossless Compilation
- Design Governance Handoff／Recovery Manifest

最新版をDiff-onlyにしない。Accepted情報を、簡潔化、重複除去、読みやすさ、File SizeまたはGit差分を理由に黙って削らない。後続版はProjectの進展に応じ、原則として粒度と情報量を増やす。

訂正時は更新前原文をHistoryへ保持し、旧状態、訂正理由および現在有効な内容を追跡可能にする。

## 5. Public文書規則

Public文書も基本的に追加式とし、変更前後完全SnapshotをCategory別Historyへ保存する。

- `overview_ja.md`：Project概要。300〜500程度を基準とし、必要に応じて追加する。
- `concept_ja.md`：OverviewとRoadmapを踏まえ、コンセプトが伝わる粒度とする。
- `roadmap_ja.md`：現在のRoadmap並みの詳細粒度を維持し、必要に応じて追加する。

Legacy Historyである`docs/public/history/roadmap/roadmap_phase_1_ja.md`は変更していない。

```text
SHA-512:
5585a1e5f11633306f645fe16fcf6a1311349d4bd359c3242491d9be88ad184dce722b5f6a57b5ff7e58543fbc661ec4de9fb293f7e7c7be1a1c079af948e344
```

## 6. 設計統括者役専用Handoff

Stable入口を新設した。

```text
docs/project/shared/design_governance_handoff/
design_governance_handoff_ja.md
```

History／Recovery Evidence：

```text
docs/project/shared/history/design_governance_handoff/
```

原則各Phase完了後、Phase Backup直前にStable Handoffを累積更新し、次を作成する。

```text
design_governance_recovery_manifest_YYYYMMDDHHMMSS.md
```

TaskがPhase途中で限界へ近づいた場合は臨時Refreshを許容する。新しい設計統括者役Taskが旧Taskの会話記憶なしで完全復元でき、さらにPhase別設計者役、実装者役および対外Docs役を正本とHandoffから再作成できることを完了条件とした。

Phase 1-exは未完了であるため、本作業ではPhase完了用Recovery Manifestを作成していない。完了を装うEvidenceを作らない。

## 7. Stable Snapshot／SHA-512

| Stable Document | Before Snapshot SHA-512 | After Snapshot SHA-512 |
|---|---|---|
| Documentation Rules | `7170c59e5296d62316ee0eaa10b70a6f38f6369d3047b7993527f3e44393fad87b097e92ef32452c866ee7ac766443d2436db57a49aa568cc9fcec1f2f0cb4fa` | `a4ae20e9e7b225c4e0df8ce34cadc34b668e5c18c0620d10738f9c55edffa59e31f980a4e0e4a6bc9716ab7460a4194ab721e88b89846a6953df3cda54f87337` |
| Documentation Structure／Task Operations | `464d5ff3ccab11743ade650b797f1e06476ac6db0e3991af0a9bb3cc6b72ee4c53c1cf27a8d6452c5415ed643f1158de1c94a9c4475ae005a6ed7ff63745810f` | `303c077a97ae671a1b08a4b51944b633e46cdb99f448811ae32a1c9e115a668d2e47752ea53fc349c8ab9a82e0822962e68947b854fc63d149a72a2d6c4fd10d` |
| Task Role／Write Authority | `2cc941383bf9dacc09958a53a25ef926c8a6757dccd09847d0807f3680ce866a7627daa60916b03bac642dfcc6fc08a1b909a12b7b8cbfbcd84198776827d0bc` | `39e6fe0fceaf650a7367199621022c6ce4af5b299ea876a6cca239aeef6c91aec70115b09f8fb483e36fc360cb700bd2a29e459c9963fdeb45d5d05bdb069813` |
| Project Continuity Master | `62377162a4afc06ad2a16a4a02c0437b98834af7c4559427cf5384cc8da4b0f0005e3b95cf5f5c9e77b15d3074d15fd61980c5e96067db19544d8b4b91b4507d` | `dc8cf20b1bd165dbcdc95549ecb0abc805a26d2eec8042234d5940924bacf24869146f76755bb5bc9a8106c3a4f22832718eec251706115b1101282c3de28c30` |
| Current Documentation Index | `401d177338bfa01bc55c3a0b848d1774c261ed42a823319b80cd29ae43b5d06020811f4bfab077f7ae7b9fe499fe864457577dfb68dc7f7710b08241354790d6` | `8d23c1d76f6dfab76d79facb4198e42906ac7d35b0bf6af29e9c9010808ec4cf0df9b49e41e322f67ea6000a7b509eeaaa3c18d9cda7bc3603f3786cc25fbcf6` |
| Design Governance Handoff | 初版のためBeforeなし | `b1f211f67ac53a46c149caccce3368e12fd89840795867262426fa3554dd60579c419f799717f6125e8cfaa10ee34855e84b359cd0ed5d8f76dc1f78bc810f18` |

各Before／After Snapshotは、対応Stable原文と`cmp`一致を確認した。

## 8. Phase Index Snapshot

```text
Before:
docs/project/phases/phase_1_ex/history/operations/
phase_index_before_documentation_information_preservation_and_design_governance_handoff_policy_20260727080023.md

After:
docs/project/phases/phase_1_ex/history/operations/
phase_index_after_documentation_information_preservation_and_design_governance_handoff_policy_20260727080023.md
```

SHA-512：

```text
Before:
cf478bebf1a97eee8d0d149215581085611e966fedb2c488c00aaba0f6ab94936ddbcee087d2efbccb248705bd9b6f9cb1eaee12b2499ba3e3d24f64bc51bafa

After:
ac115a250bdd534f792c544d90eb33d26606077047320ad120fe5fd3518a193a149fb37e8d1b48fe4ea671ac92aa7a2cf18f0e35f936aa12537955cd336b70a5
```

## 9. 非実施事項

- Historyの削除、上書き、圧縮または退役
- Git初期化、Commit、Tag、Remote、Pushまたは履歴加工
- Phase 1-ex完了宣言
- Phase 1-ex Backup
- Phase完了用Recovery Manifest
- Public Overview／Concept本文の先行作成
- External Service変更

