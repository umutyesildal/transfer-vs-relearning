# 209 — M2 OSCAR fact-translation repair v1b PASS ve sonraki kapı

**Tarih:** 2026-08-31
**Durum:** `EXECUTED ONCE / PASS / CORRECTED THREE-MODEL M2-B BLOCKS MATERIALIZED`

## Yetki ve execution

Kullanıcı, SHA-256 değeri
`b3229b2a7dee7a5345edc2086443a622f5908ae4bb2fcaab53bd1412fe5f2156` olan
`vngrs-m2-oscar-fact-translation-repair-v1b` sözleşmesini ve commit
`29fa4faee8157c58de94617038a339b5cadc6040` için ordinary non-force push, HU
preservation-check sonrası fast-forward ve tek 4-CPU/32G `longrun` wave'ini açıkça yetkilendirdi.

Commit origin'e push edildi. Aktif HU checkout temiz `db7d77b` tabanından yalnız fast-forward ile
exact commite ilerledi. HU compatible suite `20/20` PASS verdi. `482065` yalnız test-only tahmin
kimliğiydi; tek gerçek job `482066` idi. İş `gruenau3` üzerinde başladı ve terminal manifest ile
final audit üretti. İkinci job veya otomatik retry yoktur.

## Terminal sonuç

Fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v2
```

- terminal manifest status: `EXACT_THREE_MODEL_M2_BLOCKS_MATERIALIZED`;
- repair status: `M2_FACT_TRANSLATION_REPAIR_PASS`;
- corrected fact rows: `250`;
- Branch-A exposure: `0`;
- root: `12` dosya / `1,359,520,243` byte;
- stderr: `0` byte;
- runtime tmp dosyası terminalde: `0`;
- GPU: `false`;
- model weights accessed: `false`;
- training opened: `false`;
- ready to train: `false`.

Slurm `sacct` bilinen Munge/SlurmDBD authentication hatası nedeniyle okunamadı. Bu missing
accounting metadata'dır; terminal manifest, final audit, boş stderr ve kapanmış queue kaydı PASS
sonucunu birlikte doğrular.

## Exact hash zinciri

```text
manifest                 96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486
final audit              fc2075cbce7f4d51c8013b7977ec64630d2181c8c9ebf30a64f5cab61514e54d
predecessor manifest     68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63
OLMo corrected M2-B      654c4bc253acfc72452404414dadedd36ed2794009651d7e4be2d5b2c5b9b367
OLMo audit               80c828c09b46878ad75b0979acb03a1ec9edf902d5aa7333dbd285e82728107f
Qwen corrected M2-B      6f2d7ceea4e64cdeff4392a83954b7a41aa9e49520aa25b4e37cf8951a76e5f3
Qwen audit               17ffa941886eb7f4ca961350cf90478cfaf1373b0f9a4269a60f402a07fcb8b7
SmolLM corrected M2-B    53615eed0a00c8ae8c0f1787fce58dde61e4b25e52ffdd330db42f36175a66a3
SmolLM audit             376f0bbce6d02ae64fd4087e38990a0c5ac6ca2fba0a43a65aa126536a075ea1
```

Her corrected M2-B dosyası exact `97,536` JSONL blok taşır. Her modelde replacement schedule
`976` bloktur ve scheduled olmayan `96,560` blok immutable M2-A kaynağından aynen korunur.

| Model | Eski M2-B'ye göre değişen blok | Değişen token pozisyonu |
|---|---:|---:|
| OLMo | 970 | 482,392 |
| Qwen | 971 | 480,240 |
| SmolLM | 963 | 473,838 |

Dört çevirideki token uzunluğu değişimleri concatenated factual replacement akışındaki sonraki
blok sınırlarını kaydırabildiğinden, değişim yalnız dört fiziksel blokla sınırlı değildir. Buna
rağmen değişen her blok frozen 976-blok schedule içindedir; scheduled olmayan generic bloklar
değişmemiştir. Bu davranış frozen whole-fact packing tasarımıyla uyumludur.

## Sonraki kapı

Corrected üç-model M2-B block family artık materialized ve hash-closed'dur. Eski M2-B dosyaları
gelecek training için superseded kalır; M2-A ve shared validation predecessor root'tan read-only
referans edilir.

Bu PASS optimizer smoke veya training yetkisi değildir. Mevcut smoke hazırlığının eski block
manifest bağı artık superseded'dır. Bir sonraki adım, corrected manifest
`96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486` üzerine yeniden bağlanan,
yalnız üç modelin memory/optimizer uyumluluğunu ölçen ayrı frozen GPU-smoke contract'ıdır. Smoke
PASS sonrasında dahi M2-A/M2-B training ve evaluation için ayrıca frozen contract ve exact
kullanıcı yetkisi gerekir. Cleanup ve deletion yetkili değildir.
