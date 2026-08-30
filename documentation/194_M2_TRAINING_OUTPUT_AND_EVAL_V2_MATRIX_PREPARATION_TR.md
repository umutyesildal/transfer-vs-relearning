# 194 — M2 training-output ve eval-v2 matrix hazırlığı

**Tarih:** 2026-08-30  
**Durum:** `LOCAL PREPARATION PASS / EXECUTION ADAPTER NOT REGISTERED / NOT AUTHORIZED`

## Sonuç

M2 training çıktıları ile eval-v2 arasında eksik olan iki yerel bağ hazırlandı:

1. her tamamlanmış M2 run'ı exact update kimliklerinde hash-kapatan training-output finalizer;
2. altı sibling run'dan execution-disabled eval-v2 task matrix üreten hazırlık operatorü.

## Training-output finalizer

Her OLMo/Qwen/SmolLM × M2-A/M2-B koşusu için finalizer şunları zorunlu tutar:

- `training_manifest.status=complete`;
- exact role/arm identity;
- endpoint `762`;
- yalnız exact checkpoint listesi
  `76,152,229,305,381,457,533,610,686,762`;
- aynı exact parent model-manifest SHA-256;
- disk üzerinde tam on checkpoint directory;
- checkpoint model/config dosyalarının SHA-256 kapanışı;
- optimizer/scheduler/RNG state'lerinin model-only eval manifestine girmemesi.

Altı training task'i PASS olduktan sonra CPU finalizer toplam 60 model-only checkpoint binding'i
üretir. Bir run eksikse veya fazla run directory varsa aile PASS olamaz.

## Eval-v2 matrix

Matrix exact olarak:

```text
3 model × 2 arm × 10 checkpoint = 60 GPU checkpoint state
3 model × 2 arm × 2 full update = 12 full checkpoint state
3 mevcut M1 endpoint = hash-closed projection, yeniden scoring yok
toplam unique scientific state = 63
```

Her 60 checkpoint'te dense paket; yalnız update 381 ve 762'de full paket açılır. Dense paket
exact-prefix, factual cheap, WikiText BPB, OSCAR held-out BPB, trwiki control ve generation
integrity içerir. Full paket 12,000-probe factual panel ve eval-v2 English/Turkish capability
paketlerini ekler. Pile-10k emekli ve yasaktır.

## Fail-closed sınır

Bu hazırlık eski M1 executor'ını M2'ye sessizce yeniden kullanmaz. M2'nin OSCAR held-out BPB,
sibling-arm identities ve causal comparison çıktıları için özel runtime adapter henüz kayıtlı
değildir. Hazırlanan matrix şu değerlerle durur:

```text
execution_adapter_registered = false
evaluation_authorized = false
ready_to_evaluate = false
```

Dolayısıyla bu çalışma inference/scoring job'u gönderemez. Exact runtime adapter, task-level
artifact schema, final paired M2-A−M1 / M2-B−M2-A analyzer ve SHA-bound evaluation contract daha
sonra ayrıca dondurulmalıdır.

## Yerel kanıt

Training finalizer, six-run family finalizer, 60/12/63 matrix cardinality, exact full-update
kimlikleri, parent projection ve Pile exclusion fixture testleri PASS. Önceki block, training ve
control-plane testleri korunur.

Bu belge HU/SSH, GPU, training, inference, evaluation, cleanup, deletion veya automatic retry
yetkisi vermez.
