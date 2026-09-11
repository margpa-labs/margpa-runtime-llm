# Phase 11以降 Cross-industry Multimodal Video Data Analysis予約

```yaml
document_id: phase_11_plus_cross_industry_multimodal_video_data_analysis_reservation_20260909122852
document_type: planned_work_architecture_reservation
document_state: reserved_not_started
earliest_target: phase_11_plus
recorded_at: 2026-09-09 12:28:52 JST
decision_authority: user
mandatory_initial_domains: [singing, dance]
implementation_authorized: false
append_only: true
```

## 1. User Decision

既存の「動画Multimodal Data Analysis」予約を、歌と踊りだけに限定せず、**マルチモーダルデータを含めたあらゆる動画データの分析機能**へ拡張する。

歌と踊りの分析は必須とする。そのうえで、医療、自動車その他、動画・音声・時間軸・補助Sensorを組み合わせる価値が高い複数業界へ展開可能な設計を目指す。

全領域の実装工数が大きい場合は、Phase 11以降の初期実装を代表的な用途へ絞る。ただし未実装領域も、現時点で想定可能かつ有効性が高い範囲では、全体設計と詳細設計候補まで残す。機能規模がMARGPA Runtime本体へ収まらない場合、別Projectとして構築し、完成後にVersioned Port／Adapterで疎結合する。

## 2. 対象Dataの考え方

「動画」を単一の映像Fileとして扱わず、時間軸で同期し得る複数SignalのContainerとして扱う。

- 映像Frame、Scene、Object、Pose、Motion、Optical Flow。
- 音声、発話、歌声、音楽、環境音、話者、Timing。
- Subtitle、OCR、Caption、譜面、Annotation、Document Context。
- Timestamp、Camera／Codec／Frame Rate等のMetadata。
- 利用可能な場合のSensor、車両Telemetry、医療計測、Wearable、位置・姿勢Data。
- 人間Annotation、専門家判定、Ground Truth、Source Provenance。

全Data種を常に必須にせず、存在するModalityだけをCapability Manifestで宣言する。欠落Modalityを推測値で補完して観測済みと表示しない。

## 3. 必須初期Domain

### 3.1 歌唱分析

少なくとも次を設計対象とする。

- Pitch、音程推移、Rhythm、Tempo、Timing、Dynamics、音域。
- 発声区間、息継ぎ、安定性、Timbre候補、歌詞／発音Alignment。
- 伴奏とVocalの分離可能性、原曲／譜面／Referenceとの比較。
- 映像がある場合の表情、姿勢、口形、演奏・Performanceとの時間同期。
- 評価値、観測値、推定、主観Reviewを混同しないEvidence表示。

### 3.2 踊り・身体動作分析

- Pose／Skeleton、関節軌跡、重心、速度、加速度、可動域。
- Beat／Rhythm同期、振付一致、左右差、Timingずれ。
- 複数人のFormation、同期、距離、Occlusion。
- Reference動画または振付Annotationとの比較。
- Camera角度、衣装、遮蔽、Frame欠落による不確実性。
- 歌唱と踊りを同時に扱うPerformance分析。

## 4. Cross-industry候補

実装優先順位は、有効性、実現可能性、必要Model／Data、Privacy／Safety、検証可能性および工数で決める。

| Domain | 主な用途候補 | 重要な追加境界 |
|---|---|---|
| 医療・介護・Rehabilitation | 歩行・姿勢・運動評価、処置動画、患者状態推移、Training支援 | 診断代替禁止、個人情報、同意、専門家Review、High-stakes誤判定 |
| 自動車・Mobility | 運転者状態、車内行動、交通Scene、危険Event、試験走行・整備動画 | Safety Critical、Sensor同期、責任分界、低Latency |
| 製造・品質・保全 | 作業手順、欠陥、設備異常、安全動作、予知保全用Event | Camera差、False Alarm、現場秘匿情報 |
| Sports | Form、戦術、選手Tracking、怪我Risk候補、試合分析 | 公平性、身体差、Reference選択 |
| 教育・Training | 手技、実演、Presentation、技能習熟、講義理解補助 | 評価の説明可能性、未成年・教室Privacy |
| 建設・Infrastructure | 安全装備、危険動作、進捗、点検、Drone動画 | 現場条件、規制、位置情報 |
| 物流・Retail | 荷扱い、動線、棚・在庫、混雑、作業改善 | 監視化Risk、従業員Privacy |
| Agriculture・Food | 生育、家畜行動、収穫、選別、衛生・調理工程 | 季節差、環境差、Data偏り |
| Media・Entertainment | 編集支援、Scene理解、Performance比較、Highlight、Accessibility素材生成 | 著作権、肖像、生成物の出典 |
| Security・Incident Analysis | Event時系列、異常候補、複数Camera相関 | 常時監視化、誤検知、権限、監査 |
| Accessibility | 字幕、音声説明、手話・Gesture補助、重要Event通知 | 誤案内、Language／文化差 |
| Science・Research | 実験動画、行動観察、時間系列Event抽出 | Reproducibility、Ground Truth、Data Governance |

これは実装確約一覧ではない。Phase 11以降のSizingで代表Domainを選び、残りは設計・Adapter候補またはDeferred Workへ送る。

## 5. 共通Architecture候補

```text
Ingestion／Validation
→ Media Demux・Timebase normalization
→ Modality Adapters
   ├─ Vision／Frame／Object／Pose
   ├─ Audio／Speech／Music
   ├─ OCR／Text／Metadata
   └─ Optional Sensor／Domain Data
→ Temporal Alignment／Segment Graph
→ Domain Analyzer Plugins
→ Governance／Privacy／Budget／Human Gate
→ Evidence Ledger／Comparison／Report
```

- Coreは特定業界、Model、CodecまたはProviderをHard-codeしない。
- Domain固有LogicはPlugin／Adapterへ分離する。
- Analysis Plan、Model Identity、Segment、Timestamp、Source Digest、Confidence、FailureをEvidenceへ残す。
- OFF時は解析Call 0。File添付だけで自動分析を開始しない。
- 重い処理はBudget、Cancel、Resume、Partial ResultおよびResource Gateを持つ。
- Model出力、Deterministic解析、人間評価、専門家判断を別Identityで保持する。

## 6. 初期実装の縮小条件

工数が大きい場合でも歌唱・踊り分析は外さない。初期実装は次のように縮小可能とする。

1. 共通Ingestion／Timebase／Evidence Contract。
2. 歌唱の代表的なPitch／Rhythm／Alignment。
3. 踊りの代表的なPose／Timing／Reference比較。
4. 汎用動画のScene／Event／OCR／音声要約のうち実現可能な一組。
5. 医療または自動車の一方を、実診断・実制御ではないResearch Fixtureとして設計検証。

残りは設計済みExtension Pointとして保持し、未実装を実装済みと表示しない。

## 7. 別Project化Gate

次のいずれかが顕著なら、独立Project化を検討する。

- Model、Media Pipeline、Storage、GPU／Hardware依存がRuntime本体を大幅に上回る。
- 医療・自動車等のCompliance／Safety Caseが独立したLifecycleを必要とする。
- Dataset管理、Annotation、Training／Fine-tuningが主要機能になる。
- Video Processing Serviceとして独立Scaling／Deploymentが必要。
- MARGPA RuntimeのRelease、DependencyまたはSecurity Boundaryを不必要に肥大化させる。

別Project化しても、MARGPA RuntimeとはVersioned Request／Result Contract、Capability Discovery、Evidence Pointer、Cancel／Budget、Authentication／Authorityを通じて疎結合する。独立Serviceが停止しても通常Chat、Governance、Judge、Repairその他Coreを停止させない。

## 8. Privacy／Safety／Rights

- 顔、声、生体、位置、医療、未成年、従業員、車内Dataを高感度として分類する。
- Consent、Retention、Deletion、Access、Encryption、Local／Remote Processingを明示する。
- 著作権、肖像権、Performance権、Dataset Licenseを追跡する。
- 医療診断、自動運転判断、治安判断等のHigh-stakes用途は、人間専門家と制度上のAuthorityを代替しない。
- Emotion、Intent、健康状態等の推定を観測事実として断定しない。

## 9. Phase 11以降の進め方

1. 既存File Attachment／Multimodal予約と重複整理。
2. Use Case Inventory、Risk、Resource、DependencyのSizing。
3. 共通ArchitectureとDomain Plugin Contractの全体設計。
4. 必須2 Domainと優先代表Domainの詳細設計。
5. 本体内実装か別Project化かをUser Decisionで確定。
6. Fixture、実Data、Human／Expert Reviewを分けたAcceptance設計。

本予約は現時点の実装、Model取得、Data収集、外部送信、医療／車両利用、別Project作成またはGit操作を許可しない。
