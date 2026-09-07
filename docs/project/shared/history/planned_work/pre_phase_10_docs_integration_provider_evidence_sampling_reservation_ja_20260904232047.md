# Phase 10 Docs統合前予約 — Provider保存情報から研究Evidenceを限定採取

```yaml
document_id: pre_phase_10_docs_integration_provider_evidence_sampling_reservation_20260904232047
document_type: planned_work_reservation
document_state: reserved_not_started
language: ja
recorded_at: 2026-09-04 23:20:47 JST
decision_authority: user
authority_owner: Nazuna Research
scheduled_before: phase_10_docs_integration
collection_authorized_now: false
append_only: true
```

## 1. 目的と順序

Phase 10のDocs統合に入る前に、Codex／Claude／Copilotの保存情報から、本ProjectのConstitution研究に必要なEvidenceだけを採取・整理する。アプリ保存領域を丸ごとProjectへ移したり、丸ごと研究資料として保存したりしない。

順序は「対象を限定 → Evidence採取・確認 → Phase 10 Docs統合」。今回は予約のみで、保存領域の追加調査・読取・コピー・移転は実施しない。

## 2. 採取する範囲

- 本Projectの既知の事例を優先し、既存Evidenceで足りるものは再採取しない。不足する指示・応答・実行結果・訂正の前後関係を補う。
- 候補は、運用ルールの遵守／逸脱、Memory参照と更新、圧縮後の復帰、自己評価と実結果の差、Controller介入後の変化。失敗だけでなく改善・成功も、裏付けがある範囲で扱う。
- Provider、Model／推論設定（判明分のみ）、対象Task、発生日時と採取日時、出典・該当範囲を記録する。原文抜粋・ユーザー申告・採取者の解釈・未確認事項を分ける。
- 更新されるMemoryは採取時点を明示する。後日の内容を当時読んでいた証拠にせず、読取成功・自動読込・遵守改善も別々に扱う。少数事例からProvider全体の性質を断定しない。

## 3. 安全境界と成果物

- 着手時に対象Path・期間・Task・取得方法を絞り、その作業の許可範囲で採取する。本予約はHome全体、他Project、他者の会話へのアクセス許可ではない。
- 認証情報・Token・秘密鍵等は採取しない。必要な記録にも機密情報が混在し得るため、保存前に除外・伏せ字処理し、その処理を明記する。
- アプリの元データは移動・直接編集しない。稼働中DBの本体だけをコピーして完全な記録と扱わず、利用可能なら公式Export等を使う。取得不能は取得不能として残す。
- 成果物は、重複のない限定Evidenceと、事例から得たConstitution改善候補の短い対応表。新規のappend-only文書として既存Evidenceへ連結し、膨大な全ログ集や新たな監視基盤は作らない。
- Runtime Constitution／Shared Constitution／Portable Packageの3系統へは、各役割に適合する材料だけを渡す。Modelの自己説明やMemoryを、そのまま規範・要件に昇格させない。

MVP優先を維持する。Phase 11以降の外部・中立評価や構造／意味評価レイヤー分離を、今回の採取へ前倒ししない。
