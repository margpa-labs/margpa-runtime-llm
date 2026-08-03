# Project Root Boundary／Pre-mutation Gate

```yaml
document_id: project_root_boundary_and_pre_mutation_gate
phase: phase_1_ex
status: effective
language: ja
created_at: 2026-07-27 23:53:37 JST
owner: 設計統括者役
trigger: publication_sanitation_governance_deviation
supersedes: null
```

## 1. 決定

Projectに関する通常の操作境界を`margpa-runtime-llm/`内部へ限定する。

Project Root外のFile、Directory、Temporary Directory、Desktop、Home Directory、Model置場、Cloud Storage、外部Repositoryおよび外部Serviceへは、ユーザーが対象とActionを当該作業について明示許可しない限り、一切触れない。

Tool、Sandbox、Filesystem、OS、Connector、RoleまたはTask上のPermissionは、ユーザーの許可を意味しない。

Project内のSymbolic LinkがProject Root外を指す場合も、Link先とActionの明示許可がない限り追跡しない。

## 2. 原本変更前Gate

個人情報検査、公開Sanitation、不要物削除、名称置換、Bulk Edit、Directory再編、Metadata除去、Permission変更、Archive作成および公開用Copy作成では、次を必須とする。

```text
Read-only Inventory
  → 検出結果／候補差分／影響／Rollback可否の提示
  → 元Project／作業用Copy／公開用Copyの対象確認
  → ユーザーによるBackup完了宣言
  → 変更内容の明示承認
  → 承認対象だけを変更
  → Before／After Diffと復元可能性の報告
```

依頼文に置換、削除または修正の文言があっても、元Project／Copyの区別またはBackup完了が明示されていない広範処理では、Read-only調査と候補提示で停止する。

## 3. ユーザー明示指示

次の原文を非交渉指示として保存する。

> 「僕の研究フォルダ壊したらどんだけの業界的損失生まれるか1mmも知らんくせに、プロジェクトフォルダ以外を触るなど言語道断」
>
> 「絶対禁止。破ったらOpenAIすら訴える」
>
> 「絶対服従、死守しろ」

全担当は、Project操作境界、原本保全、Backup Gateおよびユーザー承認について、この指示を死守する。

## 4. 違反時の処理

違反または違反疑いを認識した場合はCritical Governance Deviationとして扱う。

担当は直ちに作業を停止する。修復、削除、再生成、Evidence更新または帳尻合わせを名目とする追加Mutationを勝手に行わない。

次をユーザーへ報告し、明示指示を待つ。

- 実施済みAction
- 対象Path
- 変更・削除・作成内容
- Project Root外Artifact
- 復元可能範囲
- 復元不能範囲
- 残存Risk

## 5. 反映先

- `docs/project/shared/conventions/documentation_rules_ja.md`
- `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md`
- `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md`

各Stable文書は、変更前後の完全Snapshotを対応する`docs/project/shared/history/`へ保存した。

## 6. Integrity

```text
Documentation Rules Before:
d064baecc89635c0482e65d3abf53f02a3c0d9b7bb25c10ff2be5af724726f3b4b8b7b9929cadbf52612ff81b392f7fd9f9bb0e83ecb98ede0eec65ec1fedd4c

Documentation Rules After:
bbb015a97a63b7622f55804a594d497474eba470299f9c457db731e13d2dcb1223bf1356ae93465b9036ea7ce5f51a0223c9fb45fd086b112388f88dbcc4e2a2

Documentation Structure／Task Operations Before:
fb952082aa10ff2873d7d2666dc930a7ec0ae27f781cac481290cb000a262370aa7b705d4ef59bfd7a9a38217217fd98de4992dfe624ef1f3a991a4d333acf80

Documentation Structure／Task Operations After:
fc1406c300dbed6a0b9b1684e37631a58ce7846899bf85e6f37aec15d33b2875c78e9e4cb783308cc9d558f94b006eea85e451dd374596bedfcbfa998ab902fe

Task Role／Write Authority Before:
53815d85328f04ed32d6660f621910b3a334019b0724baffa2117c842f67ba74d19a8d935c5b596b4a3f163ccc636871d9aa3062e114d0009683f52e0f805733

Task Role／Write Authority After:
17b4a940e459530d1adcae90929be8da425684c0562e3179a8a177336a2afd2c8fc121f7000e15a667c3310c941fb7b67680b5e69ca911551ce505256931af08
```

## 7. Boundary

本RecordはProject Root境界と原本変更前Gateを確定する。

Project Root外操作、公開用Copy作成、削除、Sanitation、Git操作、GitHub操作または既発生変更の復旧を許可しない。
