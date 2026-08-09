# Development Governance Constitution Research Index

```yaml
document_id: development_governance_constitution_research_index
status: reserved_active_research
normative: false
language: ja
created_at: 2026-08-09 18:41:34 JST
updated_at: 2026-08-09 19:19:56 JST
owner_role: プロジェクト責任者兼設計統括者役
decision_authority: user
provider_neutral: true
project_neutral_core: true
constitution_compiled: false
```

## 1. Purpose

本Directoryは、将来作成する開発統治憲法のための専用Stable入口である。Automation専用領域と分離し、憲法へ昇格させるSource、規則候補、Conflict、制度設計、Lossless Compilation、章別Normative Document、改憲およびProvider／Project移植性を一箇所から追跡する。

本IndexとSource Evidence Registerは憲法そのものではない。配置、読込または参照だけでRole、Task、Agent、Tool、Provider Adapterその他主体のAuthority、実行許可またはExceptionを生成しない。

## 2. Dedicated Structure

```text
docs/project/shared/constitution/
├─ constitution_research_index_ja.md
├─ constitution_source_evidence_register_ja.md
└─ future compiled constitution artifacts

docs/project/shared/history/constitution/
└─ <stable_name>_<phase>_<language>_YYYYMMDDHHMMSS.md
```

Stable変更前後はHistoryへ完全Snapshotを保存する。HistoryはAppend-onlyとし、旧Source、旧Rule候補、Conflict、非採用案または旧Revisionを削除・上書き・再解釈しない。

## 3. Future Artifact Classes

将来の正式編纂時は、少なくとも次を分離する。

```text
Lossless Source Compilation
  現行／旧運用Rule、Evidence、Incident、Near Miss、例外、Conflictを原意のまま統合するSource正本

Normative Constitution
  運用ルール完全定義書、統治書、制度書として、優先順位、Rule ID、適用対象、検知、違反時動作、復旧、Evidenceおよび改憲を章別に定義する正本

Project Manifest
  Project固有Root、Docs Source、Role Mapping、Git、BackupおよびPhase State

Provider Adapter
  Provider固有Capability、Task Lifecycle、Command／Tool MappingおよびFailure Contract

Constitution View
  Role／Phase／Task／Agent／Toolごとの適用条文を同一Revisionから生成する派生Artifact
```

Lossless Source CompilationとNormative Constitutionを一つの巨大Markdownへ混ぜない。情報ロスを防ぐSource正本と、実行・参照可能な制度正本の責務を分離する。

## 4. Open Supremacy Rule Set

「最上位規則群」は、ユーザーまたはユーザーが明示指定した人間が将来追加を指示できる意味で現時点の列挙に固定しない。この将来可能性は、AI側が追加候補を作成・登録・編集できることを意味しない。

```text
現在の最上位規則候補
  ≠ 永久に固定された完全列挙
  ≠ 新規規則候補の自動採用
```

最上位規則の追加、文言変更、削除、並替え、例外化およびそれらの指示権は人間専有である。AI、Role、Task、Agent、Tool、AutomationおよびProviderは、事実・Incident・Conflict・不明点を報告して停止する以外に、最上位規則へ1mmも自発的に触れない。Docs反映は、人間が明示した対象とActionの範囲に限って代行できる。

## 5. Compilation Timing

正式なLossless CompilationとNormative Constitutionは、原則としてAgent／Tool本格実装前の独立Gateで作成する。ただし、次の場合は時期を前倒しできる。

- Rule Conflictまたは重複がPilot安全性を阻害する。
- Provider間で規則解釈が分岐する。
- Source量が増え、後からのLossless再構築Riskが高まる。
- Userが明示的に前倒しを決定する。

前倒しはSource Inventory、Before／After History、Lossless検証、ReviewおよびUser Acceptanceの省略を意味しない。

## 6. Portability／Hard-code Prohibition

ConstitutionのNormative Coreへ特定Project、Repository、Absolute Path、Phase番号、Task名、Provider、Vendor、Tool、Command、UIまたはCloudをHard-codeしてはならない。

CoreはCapability、Authority、Evidence、State、Scope、Stop、Recovery、Human Gate、Rule PriorityおよびAmendmentで定義する。Project固有値はManifest、Provider固有操作はAdapter、適用主体固有値はView／Envelopeへ分離する。

## 7. Evidence Intake

Automation／Pilot固有の事実Evidenceは[Automation／Governance Evidence Log](../automation/automation_governance_evidence_log_ja.md)へ累積する。憲法へのSource採用、Chapter候補、Conflict、Rule昇格状態および未解決制度課題は[Constitution Source Evidence Register](constitution_source_evidence_register_ja.md)へ登録する。

同一Evidenceを別の意味へ要約して重複正本化しない。Automation Evidence Logを事実Source、Constitution RegisterをSource Trace付き制度候補台帳として分離する。

## 8. Current State

```text
Dedicated Folder              : created
Dedicated History             : created
Source Evidence Collection    : active
Lossless Source Compilation   : not started
Normative Constitution        : not compiled
Constitution Research Preview : not started
Agent／Tool Application       : future
Early Compilation             : conditional／user decision required
```

## 9. Related Documents

- [Constitution Source Evidence Register](constitution_source_evidence_register_ja.md)
- [Cross-project Development Governance Constitution Plan](../operations/cross_project_development_governance_constitution_plan_ja.md)
- [Automation Governance Index](../automation/automation_governance_index_ja.md)
- [Automation Control Profile](../automation/automation_control_profile_ja.md)
- [Research Asset Mutation Control](../operations/research_asset_mutation_control_ja.md)
- [Task Role／Write Authority Policy](../task_roles/task_role_write_authority_policy_ja.md)
