# 将来Scope提案 — margpa-runtime-llmのAWS配置

```yaml
document_id: future_scope_proposal_aws_deployment_20260818171240
status: reservation_not_started
phase: cross_phase
subphase: null
from: ユーザー（原案）／Claude側設計統括者役（まとめ直し）
to: プロジェクト責任者兼設計統括者役（Codex）
role: design_governor
created_at: 2026-08-18 17:12:40 JST
language: ja
purpose: |
  ユーザーが2026-08-18に提示した将来構想（margpa-runtime-llmを、
  なるべく早めにAWS上にも配置する）を、Trigger成立時の着手判断
  Inputとして記録する。ユーザー明示指示：「予約枠のところに...って、
  書いておいて」——本Docは実装（実際のAWS配置作業）着手を意味しない。
authorization: |
  ユーザー指示（2026-08-18）。history/planned_work/以下への新規
  Append-only File作成であり、Claude側設計統括者役の無許可書込み
  範囲内（運用メモ第3.11節）。
created: Claude Code
```

## 0. 位置づけ（重要）

**本Docは提案・記録のみであり、実装（実際のAWS環境構築・配置作業）は一切未着手・未着手予定。** 着手Timing自体も「なるべく早めに」という以上には確定していない。本Docの役割は、着手判断時に参照できるInput資料を残すことに限定される。

## 1. 背景・要旨

margpa-runtime-llmは、当初Lightsail（Lightning）無料枠での運用を想定していたが、Phase 2-Eを通じて機能・画面周り（React/Vite移行、Sidebar・Settings Modal化、会話の名前変更・削除、CSS微調整等）の実装が当初想定より大きくなった。ユーザーの評価では、この規模の実装を無料枠のまま運用するのは難しい可能性が高い。

また、ユーザーは「どのみち遅かれ早かれいずれ移行しようと思っていた」と述べており、今回の提案は、規模拡大を直接の契機としつつも、元々予定していた移行を前倒しする、という位置づけである。

## 2. 目的・公開時期の扱い

**目的は一般公開用の準備である。** ただし、**公開時期自体は未定**であり、今回の提案はAWS配置という**開発・Infrastructure整備の先行着手のみ**を対象とする。「AWSに配置する」ことと「一般公開する」ことは、別の判断・別のTimingとして扱う。

## 3. 必須要件

**会話の永続化Mode（Persistent）ではなく、一時的Chat（Non-persistent／Ephemeral）Modeを使用すること。**

理由：AWS上でPersistent Modeを使用した場合、外部からのAccessに伴うStorage・DB運用コストが利用量に応じて増大し、**課金が過大になるRiskがある**（ユーザー原文：「persistentモード使ってたら、課金でしぬ」）。この要件は、今回のAWS配置提案において、技術選定・Architecture設計のいずれよりも優先される制約条件として扱う。

## 4. 未確定事項（将来の着手判断時に検討する）

```text
- 具体的なAWS Service構成（EC2／ECS／Lightsail以外のManaged Service等、
  未検討）。
- 移行の具体的な手順・Timeline。
- Cost試算（Non-persistent Modeであっても、Compute・Network等の
  Costは発生するため、無料枠内で収まるか、収まらない場合の許容予算）。
- 一般公開時のSecurity・Access制御（今回の提案Scopeには含まれない、
  公開判断時に別途検討）。
- 既存のMac Local運用（llama.cpp／Metal Offload）との関係——AWS配置後も
  Local運用を継続するか、並行運用の位置づけをどうするか。
```

## 5. Status

```text
Current Point            : ユーザー構想を記録・まとめ直し。実装（実際の
                            AWS環境構築）着手・設計確定、いずれも未着手。
Files Created／Modified   : 本Fileのみ（新規作成）。
Validation                : N/A（提案記録）
Open Current Blocker      : NONE（Blockerではなく、着手判断時の
                            検討候補という位置づけ）
Controller-owned Next Work: 着手Timingの判断（ユーザーの「なるべく
                            早めに」という指示の具体化）、および
                            第4節未確定事項の検討。
Exact Next Route          : 本DocはRead-only参照材料として保持。
                            Claude側設計統括者役から能動的に着手・
                            提案することはない。
```
