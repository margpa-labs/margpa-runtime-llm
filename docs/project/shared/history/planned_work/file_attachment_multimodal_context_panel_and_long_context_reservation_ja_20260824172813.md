# File Attachment／Multimodal／Context Panel／Long Context予約

```yaml
document_id: file_attachment_multimodal_context_panel_and_long_context_reservation_20260824172813
status: reserved
classification: planned_work
created_at: 2026-08-24 17:28:13 JST
implementation_authority: false
phase_6_closure_priority: highest
```

## 1. 決定

次の4件を将来作業として予約する。現在はPhase 6 User Mac Manual AcceptanceとPhase 6 Closureを最優先とし、本書だけで実装、Phase開始、依存追加、Model Download、Network、GitまたはRoadmap更新を許可しない。

| 予約項目 | 実施時期 |
|---|---|
| 汎用File Attachment | Manual PASS時はPhase 6 Closure後のPhase 7冒頭で規模判定。Manual ADJUST時は利用可能量回復後に規模判定。小規模なら早期実装、Phase級ならPhase 10以降 |
| 動画Multimodal Data Analysis | Phase 10以降 |
| Context Window状態Panel更新 | Phase 9終盤 |
| 最大Context Window拡張 | Phase 10以降 |

## 2. 汎用File Attachment

Chat UIへ、主要LLM Productと同等の次の入口を追加する。

- Composer付近のFile Attachment Icon Button。
- Drag & Drop。
- 画像、音声（WAV等）、Markdown、JSON、一般Document、ZIPその他の対応可能なFile。
- 添付済みFileの名称、Type、Size、処理状態、削除操作。
- Unsupported Type、Size超過、壊れたArchive等の明示的Safe Failure。

単なるUpload／Attachment、内容抽出、RAG Corpus取込、Model-native Multimodal推論、永続保存は同一機能として黙って結合しない。実装前Sizingで、Transport／Storage／Parser／Security／Model Capabilityへの影響を分ける。

Phase 7へ前倒しできる条件は、既存Conversation、Citation、Recording、Public／Basic境界を壊さず、局所的なVersioned Attachment Boundaryとして完結できることである。Phase級のSchema、Storage、Sandbox、ParserまたはMultimodal基盤が必要ならPhase 10以降へ送る。Manual AcceptanceがADJUSTの場合はPhase 6修正を優先し、利用可能量回復前にSizingを開始しない。

## 3. 動画Multimodal Data Analysis

Phase 10以降に、MP4等の動画をUploadし、映像、音声、Frame、Metadataおよび時間軸を用いたMultimodal Data Analysisを追加する。

- SettingsにOFF／ONを設け、初期値はOFF。
- File Attachmentの存在だけで解析を自動開始しない。
- 対応Model／Backend、Frame Sampling、音声抽出、Token／Compute Budget、Evidence／CitationおよびPrivacyを明示する。
- OFF時はMultimodal解析Call 0。

## 4. Context Window状態Panel更新

Phase 9終盤で、Settings内のContext Window状態Panelを、その時点の実装へ合わせて更新する。少なくとも次を区別して表示する。

- Current Usageと残量。
- Native Model Context上限。
- RoPE Scaling／YaRN等のScaled上限。
- Hardware／Backend／ProfileによるEffective上限。
- Model別上限とCurrent Main Model。
- Compaction、Summary、Recovery、Rehydration状態。
- RAG／External Memory等を含むEffective Working Context。
- Warning、切詰め、品質劣化候補、直近の圧縮結果。

存在しない状態や未計測値を推測表示せず、`unknown`／`unsupported`／`not measured`を区別する。

## 5. 最大Context Window拡張

Phase 10以降に、性能と安定性へ許容できない悪影響を与えない範囲で最大Context Windowを拡張する。

```text
Model Native Context
!= Scaled Context
!= Runtime Effective Context
!= Compaction／RAG込みEffective Working Context
```

候補にはNative Long-context Model、RoPE Scaling、YaRN、KV Cache最適化、Chunked Prefill、Compaction／Recovery、Selective RehydrationおよびRAGを含む。上限値は宣伝値やModel Cardだけで決めず、Exact Model Revision、Backend、Hardwareおよび実測で固定する。

評価軸：Recall、Instruction Retention、Governance Retention、Lost-in-the-middle、Latency、Memory、短文性能、品質劣化、Failure時のSafe Fallback。Defaultは保守的な値を維持し、拡張機能は明示的に有効化する。

## 6. 次Action

1. Phase 6 User Mac Manual Acceptanceを完了する。
2. PASSなら直ちにPhase 6 Closureへ進む。
3. PASS経路では、汎用File AttachmentをPhase 7冒頭でSizingする。
4. ADJUSTならPhase 6を未完了のまま保持し、利用可能量回復後にReworkと汎用File Attachment Sizingを再開する。
5. 他3件は予約Phaseまで再活性化しない。
