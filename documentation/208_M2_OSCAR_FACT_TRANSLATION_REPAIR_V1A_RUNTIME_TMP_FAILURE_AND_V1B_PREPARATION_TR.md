# 208 — M2 OSCAR fact-translation repair v1a runtime-tmp sonucu ve v1b hazırlığı

**Tarih:** 2026-08-31
**Durum:** `V1A CONSUMED / OPERATIONAL NOT-RUN / V1B FROZEN UNEXECUTED`

## V1a execution

Exact v1a contract SHA
`067a370fa046df01a0fef9ac52556bc79c04f7c2d1add58ce40e735015d44ca1` ve commit
`db7d77b8c69adfd674388d478400797d1985c0dc` kullanıcı tarafından yetkilendirildi. Ordinary
non-force push ve HU checkout `9ca46d6 -> db7d77b` preservation-checked fast-forward geçti. HU
suite `19/19` PASS verdi.

`482056` yalnız test-only tahmin kimliğiydi. Tek gerçek iş `482057` olarak `longrun`, 4 CPU, 32G
ve iki saat recipe'siyle gönderildi. İş başladı fakat Python operatorü source validation,
tokenizer load veya block yazımına geçmeden durdu:

```text
ValueError: Unexpected pre-run fact-translation repair artifact: tmp/tmpiltx1wfc
```

Slurm script `TMPDIR`yi fresh root'taki `tmp/` dizinine bağlıyordu. `conda run`, Python processini
başlatmadan bu dizinde geçici dosya oluşturdu; operatorün precreated-root validatorü ise yalnız
`logs/` ve iki control dosyasını kabul ediyordu. Bu bilimsel veri veya recipe hatası değildir.

Terminal root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v1
files: 4
bytes: 17674
block files: 0
manifest: absent
```

Dosya SHA-256 değerleri v1b sözleşmesinde exact dondurulmuştur. `sacct`, bilinen Munge/SlurmDBD
authentication hatası nedeniyle okunamadı. Aktif queue kaydı yoktu; terminal stderr exact traceback
taşır. Model ağırlığı, GPU, optimizer smoke, training veya evaluation açılmadı. V1a yetkisi
tüketildi; otomatik retry yapılmadı ve root korunur.

## V1b dar düzeltme

V1b yalnız precreated-root validatorüne runtime-owned `tmp/` dosyalarını ekler. `logs/`, iki
submission-control dosyası ve `tmp/` dışında her pre-run artifact yine fail-closed reddedilir.
Regression testi bir `tmp/` dosyasını kabul eder ve beklenmeyen `blocks/` dosyasını reddeder.

Yeni root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v2
```

V1a'nın dört exact evidence hash'i submitter kapısıdır. Diğer tüm operational/scientific alanlar
değişmemiştir. Local suite `20/20` PASS'tir.

Frozen v1b sözleşmesi:

```text
contract: vngrs-m2-oscar-fact-translation-repair-v1b
SHA-256: b3229b2a7dee7a5345edc2086443a622f5908ae4bb2fcaab53bd1412fe5f2156
```

V1b push, HU fast-forward veya Slurm submission yetkisi vermez. Yeni exact SHA/commit-bound
kullanıcı yetkisi gerekir. GPU, model ağırlığı, optimizer smoke, M2-A/M2-B training, evaluation,
cleanup, deletion, further retry ve automatic retry kapalıdır.
