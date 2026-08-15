# 157 — Pythia Resmî Tokenizer Repair Execution Result

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `COMPLETE — VALID SCIENTIFIC RESULT — GATES EVALUATED IN DOCUMENT 158`

## 1. Sonuç

Pythia-1.4B için resmî tokenizer repair zinciri tamamlandı. Exact frozen model revision, resmî
GPT-NeoX-20B tokenizer, 500-fact dataset, seed 42 ve 252-update recipe korunarak RTX3090 üzerinde
BF16 training ve base/endpoint evaluation baştan sona tamamlandı.

Bu zincir altyapı başarısızlığı değildir. Training ve bütün evaluation çıktıları eksiksizdir.
Endpoint fact'leri çok güçlü öğrendi, fakat prompt robustness ve generic retention gate'lerini
geçmedi.

## 2. Frozen identity

```text
model: EleutherAI/pythia-1.4b
revision: 0da31d8fb309463877ed8c40e54a8f911dced3ec
tokenizer repository: EleutherAI/pythia
tokenizer commit: 1e2365516a3284f18a68c13dbd4ca19fcae59a4b
tokenizer source: utils/20B_tokenizer.json
tokenizer bytes: 2,467,981
tokenizer SHA-256: 56ac4821e129d2c520fdaba60abd920fa852ada51b45c0dd52bbb6bd8c985ade
tokenizer vocabulary: 50,277
dataset: 3,500 train + 500 validation rows / 500 facts
seed: 42
updates: 252
precision: BF16 parameters/gradients/AdamW moments; GradScaler disabled
GPU: NVIDIA GeForce RTX 3090 / guppi5
```

Training sırasında LR `5e-5`, 36 epoch, effective batch 500, answer-only loss,
`supervise_eos:false`, block size 128, gradient checkpointing ve endpoint-only selection aynen
korundu. Evaluation model scoring yolu frozen evaluator kontratına uygun FP32 idi.

## 3. Repair tarihçesi

Bilimsel kaydı korumak için pre-training fail-closed aşamalar gizlenmez:

1. Document 156 wave: acquisition preflight `452542` PASS; tokenizer job `452543`, Transformers
   5.13 PAD class-default assertion'ında durdu. GPU/training yoktu.
2. Document 156a wave: `452895` acquisition preflight, `452896` official tokenizer ve `452897`
   training preflight PASS. V100 jobları `452898/452899/452900` kaynak beklerken, training
   başlamadan iptal edildi.
3. Document 156b relocation: `453126` RTX3090 preflight PASS; `453127` exact runtime ve
   tokenization PASS sonrası FP16 GradScaler unscale guard'ında durdu. Optimizer update/training
   yoktu; dependency-dead `453128/453129` iptal edildi.
4. Document 156c: dedicated RTX3090-BF16 launcher, registry-template-root binding, `guppi6`
   exclusion, minimum 20 GiB free-VRAM gate ve dtype-inventory smoke ile başarıyla tamamlandı.

## 4. Başarılı job zinciri

| Stage | Job | Sonuç |
|---|---:|---|
| BF16 training preflight | `453163` | PASS |
| BF16 smoke + 500-fact training | `453164` | COMPLETE, `guppi5` |
| Evaluation preflight | `453165` | PASS |
| Base/endpoint evaluation | `453166` | COMPLETE, `guppi5` |

Training runtime `3,572.36` saniye; 252/252 update ve 36 epoch tamamlandı. Final train loss
`0.239781`; validation loss `0.000325063` oldu. Runtime gate training öncesi
`25,003,687,936` free byte gözledi; frozen minimum `21,474,836,480` byte idi. Smoke peak allocated
memory `14,292,328,960` byte oldu.

Smoke doğrulaması:

- parameters: `torch.bfloat16`;
- gradients: `torch.bfloat16`;
- AdamW `exp_avg` / `exp_avg_sq`: `torch.bfloat16`;
- AdamW scalar `step`: `torch.float32`;
- smoke checkpoint reload: PASS;
- smoke checkpoint: `preserved_after_successful_reload`.

## 5. Evaluation sonuçları

| Metric | Base | Trained | Gate yorumu |
|---|---:|---:|---|
| Exact-prefix top-1 | 1.4% | 100.0% | exact acquisition PASS |
| Hard-suite top-1 | 42/4,000 = 1.05% | 3,927/4,000 = 98.175% | aggregate güçlü |
| Relation-swap forced choice | 797/1,600 | 1,598/1,600 = 99.875% | relation binding güçlü |
| WikiText-2 PPL | 22.5740 | 364.5404 | ratio 16.1487x, retention FAIL |
| Generic completion top-1 | 86.67% | 83.33% | düşüş |
| Max repeated-token run | 2 | 60 | degeneration uyarısı |
| Synthetic subject intrusion | 0 | 0 | PASS |

Trained hard-suite relation/form minimumleri:

| Relation | Top-1 | En düşük 100-probe cell |
|---|---:|---:|
| `born_in` | 800/800 | 100% |
| `field_of_study` | 800/800 | 100% |
| `lives_in` | 799/800 | 99% |
| `profession` | 728/800 | **65%** (`form_c/direct` ve `form_c/qa`) |
| `works_in_industry` | 800/800 | 100% |

Hard-suite failure taxonomy: 3,927 `none`, 72 `prompt_form_failure`, 1
`same_subject_relation_swap`. Frozen robust intersection minimumi 70% olduğu için profession
form-C sonucu FAIL'dir.

## 6. Artifact ve storage closure

```text
root: /vol/tmp2/yesildau/m1_provenance_screen_v3_pythia_repair_retry_v1
retained bytes: 14,209,955,948
human-readable: 14G
final model SHA-256: 4997eb2366096ff631d1210c84b063b994af2beb86baab490ba66c8ffc8e54b0
training manifest SHA-256: 8c24bcbe7bff0f561a5452bb7166de6cf4a1fd8b7c5348a194ccf4640173aedc
```

Compact evidence hashes:

| Artifact | SHA-256 |
|---|---|
| hard base summary | `233a0de3acc82f2c556da61b41ead8c77d6ce61f9967a9e4d0fd1e1d81a3840c` |
| hard trained summary | `740e298e82b8db3a0e6a470e8f679e123c5a0053970c8c5d4c00fa4bc289f343` |
| exact base summary | `faa8230a54213ba6cfc43813c585f12387881af5faeda499332dc51d475fbe51` |
| exact trained summary | `c77a8cfdac1079a4859ac782e9f7cefd8e64679a6217de5b80ae12b04b02efab` |
| general base summary | `e161ce9815d4df826e654986738fe753f623123bd1ac504bf1b00b917176113c` |
| general trained summary | `3f3ea5b15cce412d0d03d6478aeafd411808cb6b77d235ecb81b7034fa1a6405` |
| BF16 runtime manifest | `0bdd58a048f5acd8b222225271cb4c8a6a93a7d5ca5e25d9a71518fcd02a0d57` |
| BF16 smoke manifest | `1623cc80fd40fa64c931fd701e1df818e13fa88a850ae91522b69d89a1c91523` |

HU checkout remained at `f27e10bdb3d05c899910bd829f0fe394158f23ee`; the existing 42 paths'
newline-delimited `git status --porcelain=v1` path-list serialization SHA remained
`5cc7df20d5b559a6f8b7eb050ccec24700b469848c1dea0aa7b7069e42eeaf23`. This is not the
historical full porcelain-v2 status-blob digest `71a2e3...`; the serializations are deliberately
different.
No cleanup/deletion was performed. `/vol/tmp2` had 113T free and 3% inode use; HU home filesystem
had 607G free and 53% inode use. The frozen no-home-write route remained in force; repeated
recursive HU-home `du` was not run.
