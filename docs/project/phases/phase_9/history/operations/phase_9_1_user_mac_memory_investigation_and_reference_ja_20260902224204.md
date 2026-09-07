# Phase 9-1 User Mac メモリ調査まとめ・参照用

```yaml
document_id: phase_9_1_user_mac_memory_investigation_and_reference_20260902224204
document_type: investigation_note_and_reference
language: ja
recorded_at: 2026-09-02 22:42:04 JST
phase: phase_9
program: phase_9_1
package: P9-1-JUDGE-PACKAGE-2
recorder_role: Claude（設計者兼実装者役）
source_mutation: none
git_action: none
```

## 0. 位置づけ

[Judge／Guard不可用の原因](phase_9_1_user_mac_recheck_judge_and_guard_unavailable_root_cause_ja_20260902214201.md)を受けて発生した、実機メモリ調査の過程・道具・結果を、後日参照用にまとめる。原因自体(Resource Gate、OF-P2-003/006/007)は上記Docが正本。本Docは「実際にこのMacで何が起きていたか」「Memory確認Toolの違い」「調査中にClaudeが誤解した点とその訂正」を扱う。

## 1. macOSのMemory確認Tool、3種類の違い

同じ瞬間でも、Toolによって表示される数字が異なる。いずれも「間違い」ではなく、計算方法(何を"使用中"に含めるか)が違うだけ。

```text
top -l 1 -s 0 | grep PhysMem
  "used"に、即座に開放可能なDisk Cache／Compressed分まで含める。
  一番保守的(悲観的)な数字が出る。

vm_stat(free+inactive pagesの手計算)
  Inactive Pagesを"概ねAvailable"とみなす、中間的な近似。

psutil.virtual_memory().available（本Projectの SystemMemoryRoleResourceGate
  が実際に判定へ使う値）
  Free＋Inactive＋一部Purgeable相当を、実際に新規Processへ割り当て可能な
  見込み量として計算。3つの中では一番楽観的(実態に近い)。

アクティビティモニタ「使用済みメモリ」
  アプリメモリ＋確保されているメモリ(Wired)＋圧縮。キャッシュされたファイルは
  意図的に別枠(いつでも開放可能)として除外されている、最も分かりやすい集計。
  「物理メモリ - 使用済みメモリ」がpsutilのavailableに近い値になる。
```

**一番信頼できる「困ってるかどうか」の指標は、いずれの数字でもなく「スワップ使用領域」。** これがゼロである限り、Diskへの退避は一度も発生しておらず、Macは実際には破綻していない。

## 2. 実際の調査経過(時系列、実測値)

```text
1回目の再起動後: psutil available = 3.54GB(Server稼働中、Judge/Guard実際に拒否)
2回目の再起動後: psutil available = 7.16GB
  → 計算上、Guard(Qwen3Guard)は通る見込み、Judge(Gemma/Selene)はまだ厳しい

「なぜ再起動直後なのに9GBも使ってるのか」という疑問が発生。
アクティビティモニタで実際に確認:
  使用済みメモリ 10.37GB(アプリメモリ8.39GB＋確保済み1.20GB)
  スワップ使用領域は0バイト(=実際には破綻していない)

内訳(目視できた主要App、合計約2.5GB):
  Claude系(Helper Renderer＋本体＋CLI＋その他Helper) 約1.17GB
  VS Code系(Code Helper諸々)                       約0.64GB
  DeepL(Web＋本体＋Graphics)                        約0.27GB
  Finder／Terminal／ControlCenter等の常駐UI          約0.3GB
残り約5.5GBは、Siri関連(siriinferenced)、位置情報(routined)、HomeKit(homed)、
Spotlight Knowledge Graph(spotlightknowledged)、各種Widget等、個々は
10〜20MBの小さいmacOS標準常駐Daemonが多数積み重なったもの(異常ではない)。

その後、User自身が一部Appを終了した結果:
  使用済みメモリ 6.25GB(アプリメモリ4.14GB＋確保済み1.39GB)まで低下
  → 計算上のavailable ≈ 9.5〜9.75GB
```

## 3. 調査中にClaudeが誤った点(訂正記録、正直に残す)

Claudeは当初、「Userがこの会話でClaudeへメッセージを送っている以上、そのTerminal Commandを実行した瞬間にもClaude Desktopは必ず起動していたはずだ」と推論し、9GB使用の原因説明にClaude Desktopの分を含めて説明した。

実際には、Userは「先にTerminalでtop／vm_statを実行して結果を控え、その後でClaude Desktopを開いてChatへ貼り付けた」という順序であり、**測定の瞬間にはClaude Desktopはまだ起動していなかった**。「今この会話をしているならClaude Desktopは動いている」という事実自体は正しいが、それを「過去の測定時点でも動いていたはず」に拡張したのがClaudeの推論ミスであり、User本人から直接訂正を受けた。VS Code自体は「ログイン時に自動再起動する設定」とUser自身が意図的に行っていたものであり、これは正しく推測できていた。

## 4. 参照用 — Resource Gate判定早見表(実測Test出力の値そのまま、手計算での丸めなし)

`tests/integration/test_real_local_main_selene_concurrent_load_resource_gate_smoke.py`実行時の実測`required`値(margin=3,221,225,472 bytes=約3.22GiBを含む、手計算による概算ではなく実際のTest出力)。

```text
Main = Qwen3-4B の場合:
  必要available(required)   組み合わせ
  6.52GB以上               Guard(Qwen3Guard)が通る
  9.07GB以上               Gemmaが通る
  11.45GB以上              Seleneが通る

Main = DeepSeek8B の場合:
  9.05GB以上               Guardが通る
  11.60GB以上              Gemmaが通る
  13.98GB以上              Seleneが通る
```

このMac(物理16GB)の実運用上、Claude Desktop・VS Code等の常駐Appを開いたままだと、Main=Qwen3-4B構成でもSeleneが安定して通るだけのavailableを確保するのは難しい可能性が高い(§2参照)。Main=DeepSeek8Bを選ぶ場合はさらに厳しくなる。

## 5. 実務上の参考

```text
- Memory確認は`top`より「アクティビティモニタ」の「メモリ」Tab推奨(§1参照)。
- 「使用済みメモリ」の数字だけで一喜一憂せず、「スワップ使用領域」がゼロか
  どうかを実際の逼迫度の指標にする。
- Judge/Guardが通らない時は、まずアクティビティモニタで「メモリ」順にSort
  して、閉じられるAppがないか確認するのが手っ取り早い。
- 恒久的な対応(margin再設計等)は、[3-Gate終了判定Index §6.1](phase_9_1_package_2_residual_work_three_gate_closure_index_ja_20260902201032.md)
  記載のとおりPhase 11以降に保留中。
```

## 6. Status

```text
Current Point            : Memory確認Tool間の数字の違い、実際の調査経過、
                            Claudeの推論ミスとその訂正、Gate判定早見表を
                            後日参照用にまとめた。
Files Created／Modified   : 本Fileのみ(新規作成)。
Validation                : N/A(調査・参照記録)
Open Current Blocker      : NONE
Controller-owned Next Work: なし。
Exact Next Route          : User自身の実機Testの結果を待つ。
```
