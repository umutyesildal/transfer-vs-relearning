# 214 — M2 OSCAR scientific training GPU-isolation recovery hazırlığı

Tarih: 2026-09-01
Durum: `LOCAL PREPARATION COMPLETE / FROZEN / UNEXECUTED`

## Sonuç

V1'in altı task'i model load öncesinde shared-node zero-process guard'ında durduğu için dar bir
operasyonel recovery hazırlanmıştır. Scientific recipe, exact inputs, smoke evidence, altı sibling
koşu, token/update bütçeleri, checkpoint'ler ve measurement matrix değişmemiştir.

Recovery her task için üç A100'ü tek allocation'a alır, üçünü de atomik ledger'a kaydeder ve yalnız
frozen free/used VRAM sınırlarını geçen en güvenli bir GPU'da training yapar. Task'ler `%1` throttle
ile seridir. Selector veya training hangi noktada durursa dursun task audit'i terminal nedenini
persist eder.

## Koruma ve cancellation sınırı

V1 root'u `/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_v1` immutable/read-only kalır.
Yalnız never-started dependency-dead finalizer `482208`, exact state/reason/runtime/dependency
kontrolleri PASS verdikten ve üç yeni job'un test-only kontrolü geçtikten sonra iptal edilebilir.
Başka job, artifact veya foreign process'e müdahale yoktur.

Yeni root:

```text
/vol/tmp2/yesildau/vnd_m2_oscar_scientific_training_recovery_v1
```

## Yerel doğrulama

- compatible M2 suite: `60 passed`;
- recovery config ile v1 scientific training/measurement/input/smoke/storage eşdeğerliği: PASS;
- selector bounded/deterministic unit test: PASS;
- recovery submitter ve üç Slurm entrypoint Bash syntax: PASS;
- yeni iki Python operator compilation: PASS.

Execution yapılmadı. Push, HU/SSH, job cancellation, Slurm/GPU, model load, training, checkpoint,
evaluation, cleanup ve deletion sıfırdır. Exact frozen contract:

```text
documentation/contracts/training/vngrs-m2-oscar-scientific-training-recovery-v1.md
```

Contract SHA ve publication commit, local commit kapandıktan sonra current-state dosyalarına
işlenecek ve kullanıcıdan exact SHA-bound authorization istenecektir.

Frozen contract SHA-256:

```text
c6f07cdc69003406d2ea44d8bb2c71b9c89ffd4694e224fd708460fb7374da13
```
