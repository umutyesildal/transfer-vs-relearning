# 197 — M2 OSCAR recovery 4-CPU koşullu relocation hazırlığı

**Tarih:** 2026-08-30  
**Durum:** `LOCALLY IMPLEMENTED / TESTED / FROZEN / EXECUTION NOT AUTHORIZED`

## Sonuç

Kullanıcının gece queue takibi ve 03:00 sonrası 4-CPU alternatifi isteği üzerine job `482007` için
pending-only relocation paketi hazırlandı. Paket yalnız `cpus-per-task: 8 → 4` değiştirir. RAM
128G, altı saat time limit, OSCAR source/split, üç tokenizer, 49,938,432 token/arm, 976 factual
replacement, seed/order, streaming writer ve persistent failure evidence aynıdır.

Mevcut job'un root'u iki exact submission dosyasıyla donduruldu; progress/log/manifest/block yoktur.
Relocation ancak 2026-08-31 Europe/Berlin 03:00 veya sonrasında job hâlâ `PENDING` ise uygulanabilir.
Race'i kapatmak için önce pending job hold edilir, sonra HU fast-forward yapılır, frozen submitter
yalnız `PENDING / JobHeldUser` durumunu kabul eder ve eski job'u iptal ettikten sonra fresh root'a
tek 4-CPU job gönderir. Job başlamışsa hiçbir cancellation veya relocation yapılmaz.

## Doğrulama

- compatible focused suite: `23 passed`;
- Bash syntax ve `git diff --check`: PASS;
- exact scientific recipe preservation assertions: PASS;
- 4 CPU / 128G / 6h / zero-GPU binding: PASS;
- 03:00 lower bound ve pending-only state gate: PASS;
- test-only → held-job cancellation → single submission ordering: PASS;
- fresh-root ve persistent-log assertions: PASS.

## Frozen contract

```text
documentation/contracts/corpora/vngrs-m2-oscar-exact-block-materialization-recovery-4cpu-relocation-v1.md
```

Final SHA-256:

```text
29b95dedc826c43e833d4332fe2a8756907436fe1f2a3981d5daf602ddf35413
```

## Kapı

Bu hazırlık tek başına push, hold, cancellation, HU fast-forward veya yeni Slurm submission yetkisi
vermez. Exact SHA-bound kullanıcı yetkisi gerekir. Yetki verilse bile koşul job `482007`nin hâlâ
pending ve scientific execution başlamamış olmasıdır. GPU, model weights, optimizer smoke,
training, evaluation, cleanup, deletion, automatic retry ve ikinci relocation kapalıdır.
