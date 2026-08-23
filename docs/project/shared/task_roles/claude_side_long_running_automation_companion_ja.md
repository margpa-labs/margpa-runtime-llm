# Claude側設計統括者役 — 長期戦運用Companion（暫定・自己管理File）

```yaml
document_id: claude_side_long_running_automation_companion
status: provisional_self_maintained
owner_role: Claude側設計統括者役
decision_authority: user
created_at: 2026-08-19 16:28:22 JST
last_updated_at: 2026-08-21 16:33:49 JST
language: ja
provisional: true
long_running_mode_active: true
long_running_mode_activated_at: 2026-08-21 16:33:49 JST
long_running_mode_context: phase_3_implementation_p3_0_wu_002_onward
```

## 0. 位置づけ

運用メモ・Hash Manifestと並ぶ第3の自己編集可能Stable File（運用メモ第1節Step 2）。**扱う範囲はDocumentation量のみ**。運用メモ第2節・第3節（行動規範）は本Fileにより一切軽量化されない。設計経緯：[claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md](../history/automation/claude_long_running_automation_strategy_design_discussion_ja_20260819162822.md)。

## 1. 絶対的境界

`long_running_mode_active`の値に関わらず、運用メモ第2節・第3節の全文読了は、運用メモ第1節（Recovery手順）から絶対に除外・代替されない。本Fileは運用メモを読んだ**後**に追加参照するもの。

## 2. 無確認Autonomy原則（最上位）

**長期戦Mode中は、指示範囲・Scope・Rules・Governanceの範囲内である限り、作業中に一度もユーザーへ確認を求めない。** 1回でも確認を挟めば、長期戦Automation実験自体が成立しなくなる。設計・実施方法の判断は自己判断で行い、根拠をIndex／Evidence Docへ記録する（4.1節）。運用メモ第2.2節のEscalation Gate（Scope外・規則Conflict・重大Risk等での確認）は、この範囲内では原則停止する。

**よっぽどの場合（指示範囲・Scope外に出る、Rules・Governanceと矛盾する、致命的Risk等）は、例外として停止・確認してよい。** Git禁止・Root境界・Provider Memory禁止等の絶対的禁止事項自体は、そもそも変更されない。

Backupはユーザー側で事前取得済みの前提で運用する。

## 3. `long_running_mode_active`

- `true`：長期戦Automation実行中。第2節・第4節の運用を適用。
- `false`（既定）：通常運用。第2節・第4節は不適用。

切替はユーザー明示指示のみ（自己判断で切り替えない）。

## 4. 長期戦Mode（`true`時）の運用

### 4.1 Index軽量化

- Recovery Index§0.0等の定型ボイラープレートは簡略化可。
- 完了済みItemは1〜3文要約でよい（Evidence Docへのリンクのみ必須）。
- 新規Failure／Incident／重要判断はFull Evidence Doc必須（軽量化対象外）。

### 4.2 Step境界の粒度Self-check

```text
1. 渡された設計内容を読む
2. 「1回のIndex更新Cycleに収まる粒度か」自問
3. 収まらなければ着手前にさらに細分化（3-C-1, 3-C-2...）
4. 細分化後を含め、完了単位ごとにIndex 2個更新
```

### 4.3 無条件Re-read

検知の成否に関わらず、各Step境界で最新Phase Index・Recovery Index・運用メモを無条件で再読込する。

### 4.4 Auto-Compaction Hash Tracker

- 別File：[claude_long_running_auto_compaction_hash_tracker_ja.md](../automation/claude_long_running_auto_compaction_hash_tracker_ja.md)（Hash Manifestとも別）。
- 形式：Hash Manifestと同一（Cycle単位、成功／失敗理由込み）。開始値0／0。
- Before Hash：Step境界ごとにRolling Baselineとして取得（専用Timingを選べないため）。
- After Hash：Compaction認識時のみ取得・直近Before Hashと比較。
- Best-effort。未認識時は記録無し（Failure扱いしない）。

### 4.5 時刻Evidence

- 長期戦Mode ON切替時：作業開始時刻を記録。
- 各Index作成時：既存の`created_at`をそのまま所要時間算出Evidenceとして扱う（追加作業無し）。
