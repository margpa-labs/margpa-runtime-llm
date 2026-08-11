# Phase 2-0 Dynamic Documentation Resolution／General Hard-code Rule Evidence

```yaml
document_id: phase_2_0_dynamic_documentation_resolution_and_general_hardcode_rule_evidence
status: recorded
phase: phase_2
subphase: phase_2_0
created_at: 2026-08-11 11:34:01 JST
from_role: プロジェクト責任者兼設計統括者役
to_role: ユーザー／Phase 2設計担当者役
trigger: explicit_user_direction
history_policy: append_only
pilot_restarted: false
new_task_created: false
git_mutation: false
external_mutation: false
```

## 1. Purpose

本Evidenceは、Mode-invariant Role／Docs Authority CorrectionのReviewで判明した三つの修正事項と、ユーザーが明示した一般Hard-code禁止の最上位規則を、既存Historyを変更せずLosslessに記録する。

対象：

1. 固定されたWork Unit Documentation PackageをDynamic Documentation Requirement Resolverへ置換する。
2. 前回のDocument Transactionで記録対象から漏れたPhase 2現行Draft 6文書を、完全なSource／Snapshot／Index対象へ復帰させる。
3. Phase Indexの「Role View再投影待ち」という古い現在地を補正する。
4. 「可能な限りHard-codeを禁止し、どうしても必要な場合だけ管理された例外として許可する」を、人間の明示指示に基づく最上位規則として反映する。

## 2. Finding 1 — Fixed Packageは不適切なHard-codeである

全Work UnitへIndex、Inbound Handoff、Outbound StatusおよびReview／Acceptance Eventを一律要求する設計は、Artifact名と件数を固定し、必要性のないDocs、Storage、Review、ContextおよびAI利用可能量を増やす。Work Unit種別、Role境界、State Transition、Mutation RiskおよびRecovery要件が異なるため、一つのPackageは不足と過剰の両方を生む。

現行契約：

```text
Required Documentation
  = resolve(
      work_unit_type,
      role_or_task_boundary,
      state_transition,
      mutation_risk,
      review_or_human_gate,
      audit_or_recovery_need,
      provider_capability
    )
```

- IndexはNavigation／Recovery入口が必要な場合だけ作る。
- HandoffはRole／Task間で責任、Authority、入力または次Actionを移転する場合だけ作る。
- Statusは進捗、停止、失敗、完了またはRecovery Stateの永続化が必要な場合だけ作る。
- Review／Acceptanceは独立Review、Gateまたは受領判定がある場合だけ作る。
- Evidenceは監査、復元、Authority証明または再現性に必要な場合だけ作る。
- 一つのArtifactが複数責務をLosslessに満たせる場合は統合する。
- 必要性を示せないArtifactは作らない。
- From／ToはRole／Task間の移転Artifactにだけ要求する。

CoreはArtifactのExact Name、件数または固定Packageを持たない。Project Bindingが許可Document Root／Classを与え、Work Unit開始前にResolver結果をExact Class／PathへFreezeする。Resolverは既存Stableへの直書き、既存History Mutation、許可外Document Class、Authorized Root外またはExternal ActionのAuthorityを生成しない。

## 3. Finding 2 — 6文書のDocument Transaction記録漏れ

前回のMode-invariant Correctionでは、次のPhase 2現行Draft 6文書も変更対象だったが、Correction EvidenceとDocumentation IndexがShared中心の記録となり、6文書の変更対象列挙と新しいAfter Snapshotが欠落した。これは実内容の欠落ではなく、Document Transaction Evidenceの欠落である。

対象6文書：

1. `docs/project/phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md`
2. `docs/project/phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md`
3. `docs/project/phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md`
4. `docs/project/phases/phase_2/governance/phase_2_0_phase_designer_role_view_draft_ja.md`
5. `docs/project/phases/phase_2/handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md`
6. `docs/project/phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md`

復元性：

- `20260811013723`の`after_document_authority_matrix` Snapshotが修正前の直近完全状態を保持する。
- 本Transactionの`before_dynamic_documentation_and_general_hardcode_rule` Snapshotが、前回Correction後かつ今回修正前の完全状態を保持する。
- 本Transactionの`after_dynamic_documentation_and_general_hardcode_rule` Snapshotが今回修正後の完全状態を保持する。
- したがって、旧状態、前回Correction差分および今回差分を再構築できる。

## 4. Finding 3 — Phase 2現在地の補正

Role View draft-2へのMode-invariant Authority再投影は既に完了していたため、「再投影待ち」は古い状態だった。現行Stateを次へ補正した。

```text
Control State       : PAUSED／ROLE_AUTHORITY_DESIGN
Role View           : draft-2／reprojected／not accepted
Documentation       : dynamic resolver projected／review pending
Envelope            : draft-4／not accepted
New Task            : not created
Pilot Restart       : not started
Next Gate           : resolver review → exact class／path freeze → acceptance → READY／ARMED → user start
```

## 5. Human-directed Supreme Rule — General Hard-code Prohibition

ユーザーの明示指示により、次を最上位規則群へ追加した。

```text
可能な限りHard-codeを禁止する。
技術的または論理的にどうしても必要な場合だけ、管理された例外として許可候補とする。
```

適用対象は通常運転、Automation、全設計、全Role、全Task、全Agent、全Toolおよび全Providerである。まず抽象化、Configuration、Manifest、Registry、Adapter、Profile、Schema、Runtime BindingまたはDynamic Resolutionを用いる。

不可避なHard-codeには次を要求する。

- 理由。
- 検討した代替案。
- 代替不能性。
- Exact ScopeとOwner。
- 変更・Review方法。
- 除去／Migration条件。
- TestとEvidence。

便宜、速度、現行Project／Providerへの最適化または「一時的」であることだけを理由にしない。Project Manifest、Authorization Envelope、Role View、ConfigまたはFreeze EventによるExact Runtime Bindingは、再利用されるCoreへの固定埋込みと区別する。

本規則の追加はHuman-only Supreme Rule Authorityに従う。AI側は本規則を自発的に拡張、縮小、例外化または削除できない。

## 6. Modified Current／Stable Documents

| Document | SHA-512 after |
|---|---|
| `docs/project/shared/task_roles/role_authority_matrix_ja.md` | `0123812788c8f37d3ef656d23f122c48932bb0d2a23403323621a71c9245c405f415f92a9231ef103f0c3cefc310d00b00ff637de4ce81a625444f3dbd2cf744` |
| `docs/project/shared/task_roles/task_role_write_authority_policy_ja.md` | `cf846f97b6ed72cfea45351f21af6fa2e1e61bd4d6e5c0e8f568160154ed37d0173944f99d9c977942a4917b51d90a88415611e89139838c6fddb9c463c4a043` |
| `docs/project/shared/operations/documentation_structure_and_task_operations_ja.md` | `6d6d80818597ec7f3e9285bd62a2ada6fe64b3cbfb5ee4a257c5c8a8fe085ec52fa940dbddd1e34c2879f697c5291ce29aefd8731245185314822dc33de61e18` |
| `docs/project/shared/automation/automation_control_profile_ja.md` | `a3df8b871ad7217ba7138c598ba2d53acdcf1c3c112735c9941cf358b98c71c512608122778821077512b6ba43d612f2fafaa12d759f413d5660de913e54dfb6` |
| `docs/project/shared/automation/automation_governance_index_ja.md` | `9347d7f46ec715ed0686dc1727e56e9adbae0dc8ca9ea19e4812ca6210ccfcc9b0eaa172a2ef383c35e9999a8131c1cf2cf30778aff542083050393d56abd149` |
| `docs/project/shared/automation/automation_governance_evidence_log_ja.md` | `e438b6806bd1762d8a3a07d652cdba534a8ae0bc425306451582c4e2f7cd6f98f49b0fd513f2c70be1941a465da17c8b6558a38a4cf52d06e96999d11e239344` |
| `docs/project/shared/automation/pre_pilot_governance_baseline_ja.md` | `9bc608a4b90d1af14ca268086ec9019aeb22759fec511bcc36c92f534864075ff705dfb63d23f87b3a19611d461e4c52b78f14e59163b9b9bb0bc48f635b0671` |
| `docs/project/shared/constitution/constitution_research_index_ja.md` | `c001b9723093e55c93226dc1385b9f0b6b450ac0500abdb7f29f9085b3cd56710346bbebd17417e96ed9c04316a7b5fb1458f580626909a6dee946a08a9f251d` |
| `docs/project/shared/constitution/constitution_source_evidence_register_ja.md` | `e254f991a77973a87bcfb5b888078e2ae12d820d585af2c59f9c1cd9b9984cf6cc77be55bb46016d2b9cd5ccecfd4d4192c6deaa0a0ac80aea1769ff7a04e5c3` |
| `docs/project/phases/phase_2/phase_index_ja.md` | `e67043d1812f492c4ed53ba9ca86b1a985ad6333e8d6cac115f6c254e757ecf10b487cf30a4a11a2f0801c86f3ee154e85427a4c09afc2a15c30b78b38c72ec6` |
| `docs/project/phases/phase_2/requirements/phase_2_0_automation_pilot_requirements_ja.md` | `961fc17bd251103a5b6fc44ec89456485f1aba247c497407b1cc4a303291d8d7dae38dc6ebdf1e29f8151d087488d551956f798d2ad52d15589f5d78009a8886` |
| `docs/project/phases/phase_2/architecture/phase_2_0_automation_pilot_architecture_ja.md` | `a7f3da0a2207fe23f9e2f84c2ac587739f546f3c737292ce7a8726ae24d5a727c68555ea7c77c8a09d0bd2bcc115069d99c3a061f71adeb7b24f7652827e1726` |
| `docs/project/phases/phase_2/governance/phase_2_0_authorization_envelope_draft_ja.md` | `3dbba1333a44f369e707439bb098e8e4194acd71366565c545cd8478a5302da5110c2b84b367f615f2dd23d38f0abc176da9835cd297483416d6f97272c16928` |
| `docs/project/phases/phase_2/governance/phase_2_0_phase_designer_role_view_draft_ja.md` | `ef6fa03db63d05b9779baf370e900998ec63fecc3e22df65b811965346b91f8606865a779f785f722686832f7bea6dd75928a5467abf9724069b7dc7e7f476db` |
| `docs/project/phases/phase_2/handoffs/phase_2_0_phase_designer_bootstrap_handoff_draft_ja.md` | `8da86a4e382ae666afa942081e5da0551c11a897bf85508209b9aabdeecd56cfb7070fcdb3c966574339dcd8cc804efe45a7eb230c1665f37f772381c6701815` |
| `docs/project/phases/phase_2/operations/phase_2_0_automation_pilot_execution_plan_ja.md` | `cca012dc4c783c5313af847492faa8441890968905347ddb2a2300e6d65079006988bd6714072216568b5258629e09c43472bafd46ba10b3b033ca8ca070ccd3` |

## 7. Snapshot Contract

各Modified Current／Stable Documentについて、`20260811113401`の同一Transaction IDで`before_dynamic_documentation_and_general_hardcode_rule`と`after_dynamic_documentation_and_general_hardcode_rule`の完全Snapshotを対応するHistory Classへ保存した。

既存History Fileは変更、削除、移動、Renameまたは統合していない。

## 8. Boundary／Result

```text
Automation Control State : PAUSED／ROLE_AUTHORITY_DESIGN
Envelope                  : draft-4／accepted false
Role View                 : draft-2／accepted false
New Task                  : not created
Pilot Restart             : not started
Git Mutation              : none
External Mutation         : none
Project Root外Access      : none
```

本変更は設計修正とEvidence Closureだけであり、Pilot Acceptance、Task作成、READY／ARMED、Start EventまたはPhase 2-A開始を意味しない。
