# 210 — M2 OSCAR corrected-family optimizer smoke sözleşme hazırlığı

**Tarih:** 2026-08-31
**Durum:** `LOCAL IMPLEMENTATION PASS / CONTRACT FROZEN / UNEXECUTED`

## Sonuç

Job `482066` ile tamamlanan corrected block-family manifesti üzerine bağlanan, yalnız üç modelin
memory/optimizer uyumluluğunu ölçen yeni smoke-only yol hazırlanmıştır. Bu yol training veya
evaluation job'u gönderemez.

Frozen contract:

```text
contract: vngrs-m2-oscar-corrected-optimizer-smoke-v1
SHA-256: 2f43dc86836bb9d030988fe7567c19245b1c7246c335f34353184e8b3c4103f1
```

## Corrected-family bağı

Runner, her role için GPU model load'dan önce:

1. corrected family manifest SHA-256 değerini
   `96f9867c857b08bfd784660331d1a354be7d7c6bc39250091f427fdfaa3c6486` olarak doğrular;
2. terminal status ve `M2_FACT_TRANSLATION_REPAIR_PASS` bağını doğrular;
3. smoke configindeki M2-A dosyasının manifestteki exact path/byte/SHA ile aynı olduğunu doğrular;
4. aynı role ait corrected M2-B dosyasının exact path/byte/SHA değerini doğrular;
5. yalnız bundan sonra model ağırlığını read-only yükler.

Bu nedenle smoke eski/superseded M2-B ailesine yanlışlıkla bağlanamaz. M2-A kullanımı yalnız
memory equivalence içindir: iki sibling arm da 512-token bloklar ve aynı optimizer recipe'si
taşır; arm başına ayrı smoke çalıştırmak belleğe ilişkin yeni bilgi sağlamaz ve gereksiz GPU
tüketir.

## Smoke şekli

Tek array `0-2%1` OLMo, Qwen ve SmolLM rollerini seri çalıştırır. Her task:

- bir A100-80GB;
- 8 CPU / 64G RAM / 90 dakika;
- en az 61,440 MiB initial free VRAM ve sıfır foreign compute process;
- BF16 model/gradient/AdamW state;
- microbatch `4`, accumulation `32`, effective `128` blok / `65,536` token;
- tam bir optimizer update;
- finite loss/gradient/parameter ve peak VRAM kaydı;
- sıfır checkpoint ve sıfır scientific training

kapılarını taşır.

Fresh proposed root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_optimizer_smoke_corrected_v1
```

Üç taskın her biri bağımsız report/failure audit üretir. Bir taskın eksik veya BLOCKED olması tüm
family'yi BLOCKED bırakır; fallback veya retry yoktur.

## Yerel doğrulama

```text
config                 f66924c5c6fefdf18bfc83cd7c321a073c666b2086e65b64ccd12cbe33e32fef
runner                 0647f9aa457f700804f23f884e336802c4e53b5861eb0c2163cbfa16015633d8
Slurm                  2d9abb8120ebfee1c95e2258db801b4ec432bb7b9baf5f6c26803586a9120ff3
submitter              bcff46ce8a540029e78bdbdff39f773f8c918e23b0ecff341f50d7e704e3682e
focused test file      54bd06572d17fb742fcdd567048af6ab07b4b99fafb5cb258be54f41b39c8de5
```

Compatible suite `21/21` PASS verdi. Python compile, YAML parse, Bash syntax ve diff check geçti.

## Yetki sınırı

Hazırlık push, HU/SSH, Slurm, GPU, model-weight access veya smoke execution yetkisi vermez. Exact
contract SHA ve exact implementation commit'e bağlı yeni kullanıcı yetkisi gerekir.

Gelecekte smoke PASS olsa bile M2-A/M2-B training açılmaz. Önce corrected M2-B dosyalarını kullanan
altı training configi yeniden üretmek/doğrulamak, checkpoint/evaluation ölçüm zincirini final hale
getirmek ve ayrı training contract + exact kullanıcı yetkisi almak gerekir. Evaluation, cleanup,
deletion ve automatic retry kapalıdır.
