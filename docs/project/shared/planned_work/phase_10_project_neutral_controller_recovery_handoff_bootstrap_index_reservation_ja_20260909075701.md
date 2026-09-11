# Phase 10 Project-neutral Controller Recovery Handoff Bootstrap Index予約

```yaml
document_id: phase_10_project_neutral_controller_recovery_handoff_bootstrap_index_reservation_20260909075701
document_type: planned_work_reservation
document_state: reserved
target_phase: phase_10
recorded_at: 2026-09-09 07:57:01 JST
language: ja
decision_authority: user
append_only: true
```

## 1. 決定

任意のProjectまたは新規Taskで、必要な前提を最小限の読取量から復元し、`プロジェクト責任者兼設計統括者役`を即時に立ち上げられるProject-neutralなRecovery／Handoff入口を作る。

仮版は次の構造を候補とする。

```text
docs/shared/
├─ recovery_handoff/
│  └─ project_controller_design_governor_bootstrap_index_ja.md
└─ history/
   └─ recovery_handoff/
      └─ project_controller_design_governor_bootstrap_index_ja_<timestamp>.md
```

Directory名は英語の`recovery_handoff`とする。Stable側だけで履歴を失わず、作成・改訂ごとに`docs/shared/history/recovery_handoff/`へAppend-onlyのHistoryを残す。

## 2. 仮版Bootstrap Indexの責務

Phase 10の本格的なDocs統合より前に作る仮版は、大量の規則本文を複製する新正本ではなく、既存の正本へ読む順番付きで案内する厳選Indexとする。対象Sourceは現在の`docs/project/shared/`にある文書のうち、Project固有要素を除いて他Projectでも有効な運用ルール、制度、Constitution、Authority、RecoveryおよびHandoff契約である。

最低限、次の順序で復旧できるリンクを選ぶ。

1. 人間の最終決定権、最上位規則および改訂Authority。
2. `プロジェクト責任者兼設計統括者役`のRole、責任、AuthorityおよびScope境界。
3. Docs正本、Write Authority、Stable／HistoryおよびAppend-only規則。
4. Automation、委任、Task間通信、完全待機およびResource節約規則。
5. Stop、Resume、Recovery、Handoff、FailureおよびEvidence契約。
6. Constitution／GovernanceのProject横断原則。
7. Provider差分とProject固有設定をPortable Coreへ混入させない原則。

Indexは「何を、どの順序で、何のために読むか」を示し、無関係な文書を機械的に全列挙しない。新規Taskが全Docsを読み直さなくても、役割の前提と禁止境界を再構築できる粒度にする。

## 3. Authority境界

Bootstrap Indexの読了だけでRole、Write、Git、External、DestructiveまたはProject ScopeのAuthorityが自動発生する設計にはしない。Roleの割当、対象Project、Authorized Rootおよび実作業Envelopeは、人間の指定または当該Projectで受理された契約によって確定する。

```text
Bootstrap／Recovery Readiness
  != Automatic Role Grant
  != Automatic Project Authority
  != Automatic Mutation Permission
```

## 4. Phase 10での正式化

Phase 10のDocs統合および移植Package作成では、この仮版Indexを入口として次を行う。

- `docs/project/shared/`からProject横断部分を抽出し、Project固有名、Path、Task ID、Phase固有状態およびProvider固有値を分離する。
- Project-neutral Core、Project Manifest、Role／Task ViewおよびProvider Adapterの境界を明示する。
- Source文書、抽出先、除外理由およびProvenanceを追跡可能にする。
- Bootstrap IndexのLink、読取順、Coverageおよび不足を再検証する。
- 新規Projectと既存Projectの両方で、Role復旧、Conflict検出およびAuthority非拡張をDry-runする。
- Phase 10の移植Packageへ`docs/shared/recovery_handoff/`と対応Historyを含める。

正式版の粒度、Schema、Manifestおよび検証方法はPhase 10の要件定義時に確定する。今回は予約のみであり、`docs/shared/`の新設、既存Docsの移動・複製・統合、移植Package作成、Git操作を許可しない。

## 5. `設計者兼実装者役`用Bootstrap Indexの追加（2026-09-09 User追記）

`プロジェクト責任者兼設計統括者役`だけでなく、現在の二Task運用で実装を担当している`設計者兼実装者役`も、任意のProjectまたは新規Taskで即時復旧できる専用Bootstrap Indexを同時に作る。

仮版の候補構造を次へ拡張する。

```text
docs/shared/
├─ recovery_handoff/
│  ├─ project_controller_design_governor_bootstrap_index_ja.md
│  └─ designer_implementer_bootstrap_index_ja.md
└─ history/
   └─ recovery_handoff/
      ├─ project_controller_design_governor_bootstrap_index_ja_<timestamp>.md
      └─ designer_implementer_bootstrap_index_ja_<timestamp>.md
```

`設計者兼実装者役`用Indexは、少なくとも次を読む順序付きで厳選する。

1. User Decision、Controller Handoff、Accepted Designおよび担当Work Unit。
2. `設計者兼実装者役`のRole、許可Scope、Write Authorityおよび禁止境界。
3. 対象ProjectのArchitecture、現行Contract、既知Baselineおよび変更禁止領域。
4. 実装、Test、Sabotage-regression、EvidenceおよびMaximum Claimの規則。
5. Stable／History、Append-only、Exact ReturnおよびRecoveryの規則。
6. Git、External、Destructive、Root外MutationおよびResource上限。
7. 中間報告、最終報告、停止、再開およびController Reviewへの返却契約。

Controller用Indexと`設計者兼実装者役`用Indexは相互参照可能にするが、Role、Decision Authority、Review AuthorityおよびMutation Authorityを混合しない。`設計者兼実装者役`用Indexの読了も、HandoffにないScope拡張、Phase Closure、Git Writeまたは自己承認を生成しない。

## 6. 実行優先順位（2026-09-09 User Decision）

現在の5時間利用制限がResetされた後、進行中のReworkに対するController側のReview、追加Rework指示またはClosure関連作業より先に、上記2種類の仮版Bootstrap Indexと対応Historyを作成する。その作成が完了するまで、Rework関連処理を先行させない。

## 7. Project現在地／Roadmapの条件付きDiscovery導線（2026-09-09 User追記）

`project_controller_design_governor_bootstrap_index_ja.md`には、共通のRole／Authority復旧後、対象Projectの「現在位置」「現在進行中の作業」「今後のRoadmap」を把握する条件付き導線を含める。

現MARGPA Runtime LLMでは、主な対応文書は次の2件である。

- `docs/public/roadmap_ja.md`: Projectの全体像、Phase構成、到達点および今後のRoadmap。
- `docs/project/current/documentation_index_ja.md`: Current Canonical、Active PhaseおよびProject現在位置。ただし更新が停止または遅延している場合があるため、単独で最新状態の正本とはみなさない。

これらのPathとFile名は現Projectにおける例であり、Project-neutralなBootstrap Coreへ固定しない。他の既存Projectでは名称、配置、形式が異なり、完全新規Projectでは該当文書が存在しない可能性を前提とする。

Bootstrap時は、Authorized Root内に限定して、次の意味を持つCurrent／Stable候補を有界に探索する。

1. Project Roadmap、Plan、MilestoneまたはPhase全体像を示す文書。
2. Current Documentation Index、Current State、Project StatusまたはCurrent Positionを示す文書。
3. Active Phase Index、現在有効なHandoff、Work Packageまたは進行中作業を示す文書。

File名だけで決めず、Document Metadata、見出し、更新日時、`current／stable／active`状態、Historyではない配置、参照関係およびAccepted Handoffとの整合から候補を判定する。`history／archive／backup／lossless`はCurrent候補より優先せず、古いIndexと新しいRoadmapまたはHandoffが矛盾する場合は、古いIndexだけを根拠に現在位置を確定しない。

```text
Candidate exists and is readable
  → read and record source／revision／freshness

No corresponding document
  → skip without error
  → mark project-position source as not_found／new_project_candidate

Multiple conflicting candidates
  → do not guess
  → preserve the conflict and request or derive an explicit Current authority
```

Discoveryは現在位置を理解するためのRead導線であり、無制限なFilesystem探索、Authorized Root外Read、全Historyの機械的読込、文書の自動生成またはAuthority拡張を許可しない。完全新規Projectで該当文書が存在しない場合、存在を捏造せずSkipし、Project初期化時にRoadmap／Current Indexを新設するかは別のUser Decision／Accepted Work Unitで決める。

## 8. Codex／Claude／Copilot／その他Providerでの共用（2026-09-09 User追記）

`project_controller_design_governor_bootstrap_index_ja.md`と`designer_implementer_bootstrap_index_ja.md`は、Codex専用のMemory、Task API、Tool名、UIまたは暗黙Contextを前提にしない。Claudeでは現時点で`プロジェクト責任者兼設計統括者役`を正式運用していないが、将来のRole構成変更、障害時代替、Cross-provider比較および移植先Projectに備え、両Indexを全Providerで利用可能にする。

共通IndexはProvider-neutralなRole Archetype、Authority、Reading Order、Current Position Discovery、Handoff、Recovery、StopおよびEvidence Contractだけを保持する。Codex、Claude、Copilotその他ProviderのTask作成、Memory、Compaction、Message送信、Tool Permission、Filesystem MappingおよびStatus取得の差は、Index本文のCoreを書き換えずProvider AdapterまたはProvider別補助Viewで解決する。

```text
Provider-neutral Bootstrap Index
  → Project Manifest／Current Position Discovery
  → Role View
  → Provider Adapter
  → Exact Task Instance
```

Providerが異なっても、同じRole名だけでAuthorityを継承させない。各TaskはUser Decision、対象Project、Authorized Root、Active HandoffおよびProvider Capabilityとの交差からEffective Authorityを再構築する。一つのProviderでしか実行できないCapabilityがあっても、共通Index全体をそのProvider専用へ変えない。

両Indexは、Development Agent間の指示／Handoffで採用する`Natural-language Intent／Rationale + XML Section Boundary + JSON Execution Contract`の共通運用RuleをMandatory Reading候補へ含める。
