# 207 — M2 OSCAR fact-translation repair v1 test-only sonucu ve v1a hazırlığı

**Tarih:** 2026-08-31
**Durum:** `V1 CONSUMED / NO REAL JOB / V1A FROZEN UNEXECUTED`

## Yetkili v1 işlemleri

Kullanıcı, SHA-256 değeri
`b02a1970b540cd3e0fdd0202cd174bd66a4f90baf5c1204f2b8fbeaf15a94992` olan v1 sözleşmesini ve
commit `9ca46d6fd8febc9325d038c0dbdd6c58c560d163` için ordinary non-force push, preservation-checked
HU fast-forward ve tek CPU wave'i açıkça yetkilendirdi.

Push `b56306b..9ca46d6` olarak geçti. Aktif HU monorepo checkout'u temiz eski HEAD
`b56306bf265b10a15aa7bbe76cd7fffa7b700024` ve doğru branch üzerinde doğrulandı; fetched commit
exact eşleşti ve eski HEAD'in descendant'ıydı. Checkout yalnız `git merge --ff-only` ile exact
commite ilerledi. HU suite `18/18` PASS verdi.

## Fail-closed sonuç

Launcher tüm contract/commit/root/storage/predecessor kapılarını geçti, ilk root altında yalnız
submission hazırlık kaydını yazdı ve gerçek submission öncesi zorunlu `sbatch --test-only`
aşamasında durdu:

```text
sbatch: error: invalid partition specified: cpu
allocation failure: Invalid partition name specified
```

Read-only kapanış kontrolü:

- matching Slurm job: `0`;
- gerçek job ID: yok;
- tokenizer/model ağırlığı/GPU/optimizer smoke/training/evaluation erişimi: yok;
- ilk root: `/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_v1`;
- dosya sayısı: `1`;
- tek dosya: `control/submission_state.json`, 110 byte;
- tek dosya SHA-256: `c65c87e404e287c7925752e7ddd250f7795517c2d2f2d5aa22fdf7ee27d29556`;
- durum: `SUBMISSION_PREPARED`, `automatic_retry_authorized=false`, `ready_to_train=false`.

HU `sinfo` çıktısı geçerli partition'ları `std`, `interactive`, `longrun`, `gpu` ve `longgpu`
olarak gösterdi. Dolayısıyla hata bilimsel recipe veya veri hatası değil, HU'da bulunmayan `cpu`
partition adıdır. V1 yetkisi tüketildi; otomatik retry yapılmadı. İlk root korunur ve yeniden
kullanılmaz.

## V1a dar düzeltme

V1a yalnız şunları değiştirir:

1. CPU partition `cpu -> longrun`;
2. job adı `m2-fact-tr-repair-v1a`;
3. fresh output root
   `/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v1`;
4. submitter'a ilk root'un exact tek-dosya SHA ve dosya-sayısı preservation kapısı.

4 CPU, 32G, 2 saat, corrected registry, predecessor, tokenizerlar, block sayıları, 976 replacement
schedule ve repair operatorü değişmemiştir. Local compatible suite `19/19` PASS'tir.

Yeni frozen sözleşme:

```text
contract: vngrs-m2-oscar-fact-translation-repair-v1a
SHA-256: 067a370fa046df01a0fef9ac52556bc79c04f7c2d1add58ce40e735015d44ca1
```

V1a yalnız local hazırlanmıştır. Push, HU fast-forward veya yeni Slurm submission için exact
contract SHA ve hazırlanacak exact commit'e bağlı yeni kullanıcı yetkisi gerekir. GPU, model
ağırlığı erişimi, optimizer smoke, M2-A/M2-B training, evaluation, cleanup, deletion ve automatic
retry kapalı kalır.
