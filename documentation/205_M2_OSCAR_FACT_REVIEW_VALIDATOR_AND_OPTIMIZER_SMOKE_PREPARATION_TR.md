# 205 — M2 OSCAR fact-review validator ve optimizer-smoke hazırlığı

**Tarih:** 2026-08-31  
**Durum:** `LOCAL IMPLEMENTATION PASS / WAITING FOR 250 HUMAN VERDICTS / NON-EXECUTABLE`

## Kısa sonuç

Document 204'te training-readiness evidence PASS oldu; M2-A veya M2-B training başlamadı. Bir
sonraki teknik kapı için eski combined smoke→training launcher'ı kullanılmayacaktır: o launcher
smoke job'undan sonra otomatik olarak training ve finalizer job'ları bağladığı için mevcut dar
yetki modeline uygun değildir.

Bu hazırlık iki ayrı fail-closed katman ekler:

1. 250 fact'i exact packet ve registry hash'ine bağlayan human-decision validator;
2. hiçbir training job'u göndermeyen üç-model optimizer-smoke-only runner/Slurm/submitter yolu.

## Human review kapısı

Validator şu invariants olmadan PASS vermez:

- packet tam 250 unique fact ID ve exact `0..249` sıra taşır;
- decisions tam aynı 250 fact'i birer kez kapsar;
- her satır schema v1, non-empty reviewer ve exact fact-registry SHA-256 taşır;
- verdict yalnız `usable` veya `issue` olabilir;
- optimizer-smoke kapısı yalnız verdict dağılımı exact `usable=250` ise
  `M2_FACT_REVIEW_PASS` olur.

Herhangi bir `issue` sonucu `M2_FACT_REVIEW_BLOCKED` üretir; karar agent tarafından otomatik
olarak `usable`'a çevrilmez.

## Ayrılmış optimizer smoke

Her model yalnız kendi M2-A config'inden, exact M1 epoch-036 parent'ından ve ilk 128 frozen OSCAR
block'undan başlar. Smoke bir scientific training run değildir; fakat gerçek training recipe'sinin
bir tam effective batch'ini temsil etmek için:

```text
microbatch 4 × accumulation 32 = 128 block = 65,536 token
```

ile bir gerçek AdamW optimizer step'i çalıştırır. BF16 parameter, gradient ve AdamW
`exp_avg`/`exp_avg_sq` state dtype'ları; finite loss/gradient/parameter; peak allocated/reserved
VRAM; GPU identity; config/model/data SHA-256 değerleri ayrı role report'larında tutulur. Model veya
optimizer checkpoint'i yazılmaz. Üç rol `0-2%1` ile seri çalışır; bir modelin sonucu diğerinin
recipe'sini değiştirmez.

Proposed fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_optimizer_smoke_v1
```

Route A100-80GB, başlangıç free-VRAM gate'i en az 61,440 MiB'dir. Fallback veya retry yoktur.
Submitter review PASS, readiness final audit, config validation, exact clean commit, fresh root,
duplicate-job ve test-only kapılarını doğrular; yalnız smoke array gönderir. Training/finalizer
submission kodu bu submitter'da bulunmaz.

## Yerel doğrulama

Yeni focused suite ile mevcut training-preparation/readiness/exact-block/output testleri birlikte
`16/16` PASS verdi.
Python compile, iki shell dosyası için Bash syntax ve `git diff --check` ayrıca çalıştırılır.

## Mevcut blocker ve yetki sınırı

Şu anda 250 human verdict dosyası yoktur; config'teki decision/validation SHA alanları bilinçli
olarak `pending_human_review` kalır. Bu nedenle exact execution contract henüz dondurulamaz ve
optimizer smoke gönderilemez.

Bu hazırlık HU/SSH, Slurm/GPU, model ağırlığı erişimi, optimizer smoke execution, M2-A/M2-B
training, evaluation, cleanup, deletion veya automatic retry yetkisi vermez. Human decisions
geldikten sonra validator local çalıştırılacak, exact decision/validation hashleri bağlanacak ve
ayrı SHA-bound smoke execution contract'ı hazırlanacaktır.
