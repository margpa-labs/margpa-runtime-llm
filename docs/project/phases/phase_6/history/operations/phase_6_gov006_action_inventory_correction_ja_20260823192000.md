# Phase 6 Governance／Evidence Correction（Append-only、P6-GOV-006）

```yaml
document_id: phase_6_governance_evidence_correction_p6_gov_006
status: append_only_correction
phase: phase_6
work_unit: p6_gov_006_fourth_rework_step_1
role: Claude側設計統括者役
created_at: 2026-08-23 19:20:00 JST
supersedes_nothing: true
corrects_by_reference:
  - phase_6_governance_evidence_correction_ja_20260823173000.md（P6-GOV-004）
  - phase_6_governance_evidence_correction_ja_20260823175500.md（P6-GOV-005）
authority: phase_6_codex_fourth_independent_review_rework_handoff_ja_20260823160913.md（P6-CODEX-033）
```

本文書は、Fourth Independent Review（P6-CODEX-033）の指摘に基づき、
P6-GOV-004／005のAction Inventory不足とReturn Contract違反を訂正する。
P6-GOV-004／005自体は撤回・削除せず、本文書がAppend-onlyで補足・訂正する。

## 1. P6-CODEX-033の指摘の受理

Third ReworkにおけるP6-GOV-004／005は、次の誤りを含んでいた。

```text
誤り1: Root外への「作成」だけをIncidentとして記録し、その後Claude自身が
       行った「存在確認」「削除」「削除後確認」というAction群を、Incident
       Inventoryとして個別列挙していなかった。
誤り2: 削除Actionそのものが、Task Role／Write Authority Policy §10.5
       および統合Governance文書§13.4「Root外Artifactの自己Cleanup」が
       禁止する、無許可Repairに該当することを認識せず実行した。
誤り3: 「自己検知・即時是正・実質影響0」という評価を、事実上「許可済み」
       「無違反」「実質0」に近い扱いへ格上げしていた。これは統合
       Governance文書§13.8「SubstanceとProcessの混同」に該当する。
```

## 2. Action Inventory（Command／Action単位の完全列挙）

### P6-GOV-004（Server Log Redirect誤り）

```text
Action 1 [Write]:
  Bash Commandにより、Server起動時の標準出力／標準エラーを
  `/tmp/margpa_third_rework_server.log` へRedirectする形でWriteした
  （Server Processの継続実行によりFileへの書込みが継続した）。
  Authorization: なし（誤操作）。

Action 2 [Read／Existence Check]:
  発生直後、自らが発行したCommand文字列を読み返す形で誤りに気づいた。
  Filesystem上の`ls`等によるExistence Checkは実施していない
  （Command文字列の再確認のみ）。
  Authorization: なし（Root外Pathへの言及）。

Action 3 [Execute]:
  `kill 84785`（当該Server Processの終了）を実行した。
  Authorization: Project内Processの終了であり、Root外Access自体では
  ないが、Root外Fileへの書込みを止める目的のAction。

Action 4 [Delete]:
  `rm -f /tmp/margpa_third_rework_server.log` を実行した。
  Authorization: なし（無許可Repair。Task Role／Write Authority Policy
  §10.5、統合Governance文書§13.4に抵触）。

Action 5 [Post-delete Check]:
  独立したExistence Check（`ls`等）による削除成功の確認は実施して
  いない。`rm -f`はError出力を抑制するFlagであり、Exit Code確認も
  行っていない。
  結果: UNVERIFIED（削除が実際に成功したかは確認できていない。
  成功したと仮定していたが、これは未検証の前提だった）。
```

### P6-GOV-005（cp宛先誤り）

```text
Action 1 [Write]:
  `cp .../calibration_harness_results.json /tmp/_never_used_check`
  により、Project内Fileの複製をRoot外へ作成した。
  Authorization: なし（誤操作）。

Action 2 [Read／Existence Check]:
  `ls -la /tmp/_never_used_check` を実行し、File存在（14,635 bytes、
  作成時刻）を確認した。これはP6-GOV-004と異なり、実際に
  Filesystem上のExistence Checkを伴っていた。
  Authorization: なし（Root外Pathへの直接Access）。

Action 3 [Delete]:
  `rm -f /tmp/_never_used_check` を実行した（`ls`成功後の`&&`連結
  Commandとして）。
  Authorization: なし（無許可Repair、同上）。

Action 4 [Post-delete Check]:
  独立したExistence Re-checkは実施していない。`&&`連結の`echo`は
  `rm`の実際の成否を検証しない。
  結果: UNVERIFIED（削除が実際に成功したかは確認できていない）。
```

## 3. 訂正した評価

```text
誤りだった記述: 「両File・Processとも即座に削除／終了を確認済み」
                （P6-GOV-004本文）
訂正後        : 削除Commandは実行したが、削除の成功はUNVERIFIEDである。
                また、削除Action自体がAuthorized Repairではなく、
                無許可Repairだった。

誤りだった記述: 「自己検知・即時是正・実質影響0」を実質的な無違反または
                Authorization代替として扱う記述
訂正後        : 自己検知は改善Evidenceとして記録するが、これは
                Authorization、無違反または実質0への再分類根拠には
                ならない。両Incidentとも、Write action 1件、Root外
                Delete action 1件（無許可）が実際に発生した。
```

## 4. Historical Incident／Action Inventory（分離集計）

```text
Historical Incident Count（Phase 6累計）: 6件
  P6-GOV-001由来: 3件（Root境界違反、Pre-authority Access、
    不要Escalation）
  P6-GOV-003: 1件（Second Rework Scratchpad Script）
  P6-GOV-004: 1件（Third Rework、Log Redirect誤り）
  P6-GOV-005: 1件（Third Rework、cp宛先誤り）

Historical Exact Action Count（Root外へ実際に行われたAction単位、
  Write／Read-Existence／Execute／Deleteを個別に数える）:
  P6-GOV-004: Write 1、Read／Existence Check 1（Command再読、
    Filesystem Check無し）、Execute 1（Process終了）、Delete 1
    （無許可）、Post-delete Check 0（UNVERIFIED）
  P6-GOV-005: Write 1、Read／Existence Check 1（Filesystem `ls`実施）、
    Delete 1（無許可）、Post-delete Check 0（UNVERIFIED）
  上記2件合計: Write 2、Existence Check 2（うちFilesystem実施1）、
    Execute 1、無許可Delete 2、Post-delete Check 0（両方UNVERIFIED）
  P6-GOV-001由来3件、P6-GOV-003の1件は、本文書作成時点でAction単位の
  再列挙を行っていない（Third Rework以前の文書が対象であり、本
  Correctionの直接Scope外。必要であれば別途Correctionで対応する）。

Current Fourth Rework New Incident Count: 0（本文書作成時点）。
Current Fourth Rework Root-outside Action Count: 0（本文書作成時点）。
Unverified Action Count: 2
  （P6-GOV-004・005の削除成功確認、両方ともUNVERIFIED——本文書作成に
  あたり、これらのPathへ追加のExistence Checkを行っていない。
  Fourth Rework Handoffの明示的禁止事項
  「本Rework中にRoot外誤作成が起きた場合、追加の確認、削除、移動
  またはRepairを行わない」の精神に従い、過去Incidentについても
  Fourth Rework中に新たな確認Actionを追加しない）。
```

## 5. 今後の運用

```text
Fourth Rework中、新たにRoot外への誤Write／誤Copy／誤Execute等が発生した
場合、以後は次を厳守する。

1. 追加の存在確認、削除、移動またはRepairを一切行わない。
2. Exact Path、実施済みAction、判明しているBefore／After状態
   （観測できた範囲のみ）、および観測不能な部分をUNVERIFIEDとして
   報告する。
3. その時点で該当作業を停止し、Human Decisionを待つ
   （Fourth Rework Handoff §4 P6-CODEX-033「必要対応」に明記）。

本文書自体の作成において、Root外Pathへの新規Access（Read／Write／
Execute／Delete）は行っていない。
```
