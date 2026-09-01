# 217 — M2 OSCAR tek-A100 relocation submission ve ilk RUNNING durumu

Tarih: 2026-09-01
Durum: `AUTHORIZED / SUBMITTED ONCE / PREFLIGHT PASS / TASK 0 RUNNING`

Kullanıcı exact contract SHA
`ffea82ac9f9d0bbd9228c13cff7eec9d87c16fd381b92ab35021345413c83792` ve commit
`c15c1232e7dfd2317455abadbd635f136a320b92` için tek relocation wave'ini yetkilendirdi.

Eski `482225/482226` chain'i exact pending, runtime `00:00:00`, zero task audit ve zero training
artifact kontrollerinden sonra iptal edildi. HU checkout clean `a8978b1` predecessor'ından yalnız
fast-forward ile `c15c123` commitine ilerledi. İlk verification komutunun son contract-path
assertion'ında yalnız `vnd`/`vngrs` typo'su nedeniyle PASS etiketi basılmadı; cancellation ve
fast-forward tamamlanmıştı, submission yapılmamıştı. Düzeltilmiş exact path kontrolü ve HU M2
suite `62/62 PASS` verdi.

Yeni job'lar:

- test-only: `482228`, `482229`, `482230`;
- CPU preflight: `482231`;
- scientific serial array: `482232_[0-5%1]`;
- afterok finalizer: `482233`.

Submission manifest SHA `705df3203aee1c499c7398846e2f2523db860ccd5e7f1b1155ff3f25fad0d536`.
Preflight `M2_SCIENTIFIC_TRAINING_PREFLIGHT_PASS` tamamlandı:

- preflight SHA `f8b9db1447d0835913bf723af2069742f8e60c84995f191ad30cac1ea49cea3a`;
- config-validation SHA `0bf6c802896a77045ea41b0d02ee09095a944e5d678751a3a65b5792e11508a1`;
- six-config manifest SHA `dabcf252230fa847408ca1dcfa009dba7732e3f61796b7e80f8a6f5044c2fde7`.

Task `482232_0` / step job `482234` OLMo/M2-A olarak gruenau10 üzerinde RUNNING'e geçti.
Selector exact Slurm-allocated device'i UUID
`GPU-6be517a6-e5dc-ada7-1137-7a9fbe19a5d4` olarak bağladı; seçim anında
`78,628 MiB free / 2,525 MiB used` idi ve `M2_GPU_SELECTION_PASS` üretti. Selector audit SHA
`54f91ecdafb011994a6176694148ced05a0f7d7b870948bc60d805bfa3d2e732`.

Task audit `TRAINING_TASK_LAUNCH`; training manifest `status=started`. İlk gözlemde Slurm job
RUNNING, exit `0:0`, MaxRSS yaklaşık 884 MiB ve initialization aktifti. Henüz checkpoint veya
kanıtlanmış optimizer update yoktu; bu kayıt scientific completion iddiası değildir. Kalan beş
task array `%1` sınırında, finalizer dependency-pending'dir. Retry/fallback/evaluation/cleanup yoktur.
