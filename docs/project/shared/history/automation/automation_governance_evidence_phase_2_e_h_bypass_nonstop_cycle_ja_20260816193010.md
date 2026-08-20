# Automation Governance Evidence — Phase 2-E-H Bypass・Nonstop実装Cycle

```yaml
document_id: automation_governance_evidence_phase_2_e_h_bypass_nonstop_cycle_20260816193010
status: evidence_record
phase: phase_2
subphase: phase_2_e_h
from: Claude側設計統括者役
to: プロジェクト責任者兼設計統括者役（Codex）／ユーザー
role: design_governor
created_at: 2026-08-16 19:30:10 JST
language: ja
related:
  - claude_phase_2_e_h_completion_handoff_ja_20260816193010
  - claude_phase_2_e_h_process_breakdown_design_ja_20260816173714
  - claude_side_design_governor_operating_notes_ja（第8節Permission Mode運用、第9節Context圧縮実験）
```

## 1. 背景

ユーザーはBackup（`margpa-runtime-llm_2-E-H実装直前_20260816.zip`、実装着手7分前取得）確認後、「作業開始で、可能であればノンストップH実装完了狙いでよろしく」と明示指示。設計は事前に[claude_phase_2_e_h_process_breakdown_design_ja_20260816173714.md](../../../phases/phase_2/history/architecture/claude_phase_2_e_h_process_breakdown_design_ja_20260816173714.md)で確定済み（Open Question全4問＋追加確認事項2件）。ユーザーからは事前に「"Bypass実験的にはNon-stopを狙って良い"、ただし"完全に無風で終わる保証はE/F/Gより低い"」という温度感を共有した上での実行許可。「想定外とか発生したら止まっていい」という条件付き。

## 2. 実測結果

2-E-B〜Gまでの一連のBypass実験（[運用メモ第8節](../../task_roles/claude_side_design_governor_operating_notes_ja.md)）に続き、2-E-Hの全工程——Backend設計確定→Domain/Adapter/Migration/Service/Contracts/Routes実装→Test新規作成→pytest全件→ruff／mypy→Frontend型/API/Component/i18n/CSS実装→npm lint/typecheck/test/build→実Browser確認（Server起動・実Chat UI操作・White/Dark両Theme・Server停止）→本Evidence作成に至るまで、**Tool実行確認Dialogは1回も発生しなかった**。

```text
対象Cycle          : 2-E-H全工程（Backend実装〜実Browser確認〜Docs化）
Dialog発生件数      : 0件
新たに実行した種類の
Action              : ALTER TABLE（SQL Schema変更）、既存Testの
                      Downgrade Helper修正、`nohup`によるReal LLM
                      Server起動→`kill -INT`による明示Stop、
                      `.claude/launch.json`新規作成
```

事前にユーザーへ共有した「完全に無風で終わる保証はE/F/Gより低い」という見立てのうち、**Permission Dialog面では結果的にE/F/Gと同じく0件で完走**した。一方、事前見立てどおり「品質判断上の細かい遭遇」は複数発生した（第3節）——ただしこれらはPermission Dialogとは無関係な、実装・検証手順上の技術的な発見であり、いずれも自己解決した。

## 3. 遭遇した技術的事象（Permission Dialogとは別種、いずれも自己解決）

```text
1. 既存Migration Step（TURN_CITATIONS_MIGRATION_STEP）のtarget_version
   が`STORAGE_SCHEMA_VERSION`モジュール定数を動的参照していたため、
   今回STORAGE_SCHEMA_VERSIONをsqlite-2→sqlite-3へ上げたことで、
   既存Testが「sqlite-1から直接sqlite-3へ」を誤って主張する形で壊れた
   （`duplicate column name: title`）。固定Literal参照への訂正で解消
   （[Completion Handoff第3.2節](claude_phase_2_e_h_completion_handoff_ja_20260816193010.md)
   に詳細）。

2. Browser Preview Toolの`preview_start`（Named Config経由）が、本
   Project Directory（日本語文字を含むPath）に対しSandbox制約で
   起動失敗（Code 126）。Bash側`nohup`起動＋`url`経由Attachへ切替えて
   解消。

3. `window.confirm()`のNative Dialogは本Browser Tool環境で自動Cancel
   される。検証目的でのみ`window.confirm`をMonkey-patchして実装コード
   自体は変更せず検証を完遂。

4. `computer`Toolの`key`Action、`"Return"`Label指定時にReact側
   `event.key === "Enter"`条件と一致せずRename確定が発火しなかった。
   `"Enter"`Labelへ変更して解消（Tool固有のKey Label挙動、実装Bugでは
   ない）。
```

いずれも「実装した時点では正しいはずだったが実際には動作していなかった」種類ではなく、（1）は既存Testの前提が新しい変更と噛み合わなくなった規模の小さいRegression、（2）〜（4）はTool側の制約・挙動に起因する検証手順上の発見であり、[claude_phase_2_e_f_g_css_refinement_completion_handoff群](../../../phases/phase_2/history/handoffs/)で記録してきた「実装Bug」と「Tool制約」の分類でいえば、今回は全件が後者（Tool制約）＋軽微な前提崩れ（1）であり、[自己評価Evidence](automation_governance_evidence_claude_frontend_design_capability_self_assessment_ja_20260816161000.md)で言うところの「Aesthetic Taste判断のズレ」系統の指摘は今回のCycleでは一件も発生しなかった（Backend中心の実装だったため、CSS微調整のようなIterationは不要だった）。

## 4. Status

```text
現在の運用   : Bypass Permissionsで引き続き運用中。2-E-D（単一
              Sub-phase）、2-E-E〜G（3 Sub-phase連続）に続き、2-E-H
              （新規Backend機能実装を含む、より複雑度の高いSub-phase）
              でも「Dialog 0件でのNon-stop完走」を実測。
累計実測      : 2-E-D、2-E-E、2-E-F、2-E-G、2-E-Hの5 Sub-phase
              すべてでDialog 0件。
正式化       : 未定（provisional、運用メモ第8.8節のStatusを参照）。
Rollback条件 : ユーザー判断（変更なし）。
```
