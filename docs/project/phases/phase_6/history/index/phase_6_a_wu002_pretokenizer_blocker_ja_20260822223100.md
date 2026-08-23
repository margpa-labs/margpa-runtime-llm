# Phase 6-A Pre-tokenizer Blocker（P6-A-WU-002実行結果）

```yaml
document_id: phase_6_a_wu002_pretokenizer_blocker
status: current_recovery_entry
phase: phase_6
subphase: phase_6_a
work_unit: p6_a_wu002_blocked_toolchain_vintage
role: Claude側設計統括者役
provider: claude_code
created_at: 2026-08-22 22:31:00 JST
```

## 実行結果

```text
Command   : .venv/bin/python /opt/homebrew/bin/convert_hf_to_gguf.py
            models/main/deepseek-r1-0528-qwen3-8b/huggingface --outtype q8_0 ...
Exit Code : 1
Log       : .venv/.tmp/convert_q8_0.log（Project-local Temporary、無断削除せず保持）
Output    : conversion_work/ へのFile書込み0（例外発生時点で未書込み、Canonical/Derived Mutation 0）
```

## 根本原因

```text
config.json architectures        : Qwen3ForCausalLM
tokenizer_config.json tokenizer_class: LlamaTokenizerFast（不一致）
tokenizer.model (SentencePiece)  : 不在（FileNotFoundError）
実際のVocab形式                   : BPE（GPT2系Fallbackパスへ到達）
chkhsh (実測)                    : 0d75215efe33c49084836cb245f2fa78de4b3858f5a3e54d5e1fd27f4ce33b05
判定                              : convert_hf_to_gguf.py内蔵の既知Pre-tokenizer Hashテーブルに
                                    一致なし。誤Vocab生成を避けるためNotImplementedErrorで意図的停止
                                    （Tool自体のFail-safe設計、Bugではない）。
```

DeepSeek-R1 Distillシリーズは`tokenizer_class`表記とArchitecture/実Vocab形式が一致しないことがある既知の傾向であり、今回もその一種と推定される（Provider Opinion、未External確認）。

## 解消経路の評価

```text
経路1: brew upgrade llama.cpp（より新しいBuildならHash登録済みの可能性）
       → Dependency Acquisition Authority Receipt §3.4で明示的に禁止
         「Homebrew Prefixの探索、Formula変更、brew install／update／upgrade／uninstall
           またはTool本体の変更は許可しない」
経路2: convert_hf_to_gguf_update.py 実行（HF Hub照会でPre-tokenizer Hashテーブルを更新）
       → 同Receipt §3.3で明示的に禁止
         「PyPI以外のGit Repository、Release Asset、Model Hub、Cloud Storageまたは
           External APIへ拡張しない」
判定   : 両経路とも現行Authority外。Claude側での自己解消は不可（Recipe修正の範囲を超える）。
```

## Governance適用

Phase 6 Claude長期実行Governance §6「Model Artifact Governance」および両Receiptの明文により、
「ConversionやLoad失敗をSupportedへ捏造しない。Safe Unsupportedは正当な結果である。」を適用する。

本Blockerは、Dependency Acquisition Authority Receipt §6 Stop／Escalation Conditions
項目1（PyPI以外の取得元が必要）および項目2（Homebrew Mutationが必要）に該当する、
本Receipt上も正しく定義されたStop Triggerである。

## Current State

```text
Phase 6-A DeepSeek Conversion : BLOCKED（Toolchain Vintage／Model Tokenizer不一致）
Canonical Snapshot             : 無変更（huggingface/への書込み0）
Derived Subtree                : 空のまま（gguf/, manifests/, conversion_work/ログのみ）
Qwen Route                     : 無影響
Next Owner                     : User／Controller（Homebrew Upgrade許可、または
                                  HF Hub限定Read許可、またはDeepSeek-A自体をDeferredのまま
                                  Phase 6-B以降を優先継続、のいずれかを選択可能）
Claude側対応                    : 本Blockerを理由にPhase 6全体を停止せず、
                                  Phase 6-B（Runtime Model Domain、既着手分）を継続する。
```

## Next Exact Route

Phase 6-A-WU-002はBlocked状態でDeferred。User／Controllerの追加判断（Homebrew／Network拡張の可否）を待つ間、Phase 6-B-WU-001（Runtime Model Domain／Ports）を継続する。
