# 156c — Pythia RTX3090 BF16 Parametre/Optimizer-State Smoke Düzeltmesi

**Tarih:** 2026-08-11 (Europe/Berlin)  
**Durum:** `FROZEN — READY_FOR_EXACT_USER_AUTHORIZATION — UNEXECUTED`

## 1. 156b relocation sonucu

Document 156b'nin yetkili relocation wave'inde:

- V100 downstream jobları `452898/452899/452900` training başlamadan iptal edildi;
- dar registry/routing commitleri preservation-checked biçimde HU'ya fast-forward edildi;
- RTX3090 training preflight `453126` PASS oldu;
- job `453127` saniyeler içinde `guppi5` üzerindeki RTX3090'a yerleşti;
- exact runtime identity ve full tokenization audit PASS oldu;
- optimizer smoke, gerçek training başlamadan şu hata ile fail-closed oldu:

```text
ValueError: Attempting to unscale FP16 gradients.
```

`453128/453129` dependency-dead durumda iptal edildi. Training/evaluation namespace'leri absent;
checkpoint, optimizer update veya bilimsel sonuç yoktur. Existing tokenizer/composite manifest,
runtime ve tokenization kanıtları korunur; cleanup/deletion yoktur.

## 2. Kök neden

Pythia'nın native config'i parametreleri FP16 yükledi. PyTorch AMP `GradScaler`, doğrudan FP16
parameter gradientlerini FP32 master weight olmadan unscale etmeyi güvenli saymaz ve bilinçli olarak
reddeder. Bu model, dataset, tokenizer, GPU veya fact-learning sonucu değildir.

RTX3090'ın 24 GiB belleğinde 1.4B parametreyi FP32 parameters + FP32 gradients + AdamW states
ile çalıştırmak güvenilir bir bounded çözüm değildir. Ampere RTX3090 native BF16 destekler; BF16'ın
exponent aralığı loss scaling gerektirmez. Aynı v3 ailesinin frozen A100/RTX3090 yolu zaten BF16
template kullanmaktadır.

## 3. Dar düzeltme

Yalnız precision/runtime binding değişir:

```text
model_load_dtype: bfloat16
bf16: true
fp16: false
GradScaler: disabled
GPU: NVIDIA GeForce RTX 3090
compute capability: 8.6
compiled arch: sm_86
```

Runtime validator registry'deki frozen precision değerini okuyup exact Python/Torch/GPU/capability/
compiled-arch ile finite BF16 forward/backward kontrolü yapar. Dedicated launcher, frozen template
ve yeni preflight manifest yolunu sabit ve hash-bound seçer.

Dedicated RTX3090-BF16 launcherlar GRES, retry-root log yolları, registry, template ve preflight
manifestini sabitler; shared V100 launcher kullanılmaz. Preflight registry'nin declared template
yolunun ve SHA'sının submitted template ile aynı olduğunu doğrular. Smoke, optimizer step sonrası
parameter, gradient ve AdamW `exp_avg`/`exp_avg_sq` dtype inventory'sini kaydeder ve BF16 dışında
fail-closed olur. Bu tasarım FP32 master-weight iddiası yapmaz: parameters, gradients ve AdamW
moments BF16; optimizer `step` sayacı framework'ün FP32 scalar state'i olabilir.

Model revision, tokenizer, dataset, seed, LR, epoch, effective batch, update sayısı, loss masking,
EOS politikası, gradient checkpointing, checkpoint seçimi, evaluator ve bütün bilimsel eşikler
değişmez. Bu precision compatibility repair'dır; outcome-aware scientific remediation değildir.

## 4. Tek yeni zincir

Exact authorization sonrasında, aynı retry root'ta ve yalnız training/evaluation namespace'leri
absent ise:

```text
training_rtx3090_bf16 preflight
  → exact RTX3090/BF16 runtime gate
  → tokenization audit
  → BF16 optimizer/checkpoint-reload smoke
  → 252-update 500-fact training
  → evaluation_rtx3090_bf16 preflight
  → base/endpoint hard + exact + general-capability evaluation
  → Documents 157/158
```

Her stage `afterok` ile bağlıdır. Exactly one training ve one evaluation job submit edilir. OOM,
non-finite, runtime mismatch veya başka smoke failure bilimsel sonuç sayılmaz ve otomatik yeni
precision/optimizer/recipe retry açmaz.

## 5. Kapsam dışı

Silme/cleanup, first/retry root mutation, tokenizer/model revision değişimi, seed-43, LR/epoch/dose
remediation, OLMo/Falcon retraining, corpus, M2-A/M2-B ve başka GPU fallback kapsam dışıdır.

## 6. Exact authorization request

> Document 156c'nin exact SHA-256'sı kapsamındaki dar BF16 parameter/optimizer-state registry/runtime/
> launcher/test düzeltmesini, ordinary non-force push'u, preservation-checked HU fast-forward'u
> ve mevcut verified tokenizer/composite-manifest kanıtını yeniden kullanarak exactly one RTX3090
> BF16 training preflight → runtime/tokenization/optimizer smoke → 500-fact training → evaluation
> preflight → base/endpoint evaluation zincirini; ayrıca Documents 157/158 result/gate
> dokümantasyonunu yürütmeni yetkilendiriyorum.
