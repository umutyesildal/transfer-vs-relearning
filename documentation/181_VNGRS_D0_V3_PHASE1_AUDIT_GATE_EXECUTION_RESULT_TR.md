# VNGRS D0 V3 Phase-1 audit kapısı yürütme sonucu

**Tarih:** 2026-08-28

**Durum:** `BLOCKED / FAIL-CLOSED`

**Job:** `481844`

**Sözleşme:** `vngrs-m2-three-model-d0-v3`

**Sözleşme SHA-256:** `c583b434535475692b0682be27434d0d9d4319b4faebe984d3181e8aea9146aa`
**Yürütülen commit:** `b7af152139e4a50c323830474a8e862d91291a2b`

## Sonuç

Tek yetkili D0 V3 Phase-1 dalgası bütün 32 Parquet nesnesini başarıyla materyalize edip tam byte
kimliklerini doğruladı. Ardından karışık OSCAR/mC4 doküman nüfusundaki zorunlu lightweight audit
`BLOCKED` döndürdü. Orkestratör fail-closed durdu; split, 64-doküman review paketi, Phase 2,
tokenizer/model erişimi ve eğitim açılmadı.

Korunan terminal hata kaydı:

```json
{
  "error_type": "ValueError",
  "message": "mandatory lightweight audit blocked D0",
  "phase": "phase1_review_handoff",
  "ready_to_train": false,
  "schema_version": 1,
  "status": "BLOCKED"
}
```

## Doğrulanmış kanıt

| Kanıt | Değer |
|---|---:|
| V3 kökü | `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3` |
| Doğrulanmış nesne | 32/32 |
| Doğrulanmış full-object byte | 9,502,315,428 |
| Materyalizasyon manifesti | `control/materialization_v3.json` |
| Manifest SHA-256 | `bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10` |
| Terminal hata | `control/d0_failure.json` |
| Terminal hata SHA-256 | `a341e4787e38720f27beeaf5815331ef0163084cb2974d91799ee5ffe426c52f` |
| Gözlenen kök disk kullanımı | yaklaşık 8.9 GiB (`du -sh`) |
| Materyalizasyon manifest zamanı | `2026-08-28T10:30:12` |
| Hata kaydı zamanı | `2026-08-28T15:11:09` |

`sacct`, Munge/SlurmDBD kimlik doğrulama hatası nedeniyle terminal muhasebe satırını vermedi.
Bu eksik muhasebe metadatasıdır; korunmuş uygulama hata kaydını geçersiz kılmaz.

## Kanıt bütünlüğü eksikliği

V3 uygulaması audit nesnesini yalnızca audit PASS olduktan sonraki aşamalarda kullanıyordu. Audit
`BLOCKED` olduğunda yalnızca genel exception yazıldı; aşağıdaki belirleyici ayrıntılar kalıcılaşmadı:

- exact synthetic-surface hit sayısı ve örnekleri;
- Unicode-normalized hit sayısı ve örnekleri;
- `U+FFFD` invalid-encoding doküman sayısı;
- OSCAR/mC4 exact label, doküman ve UTF-8 byte bileşimi;
- normalized duplicate sayıları.

Kod semantiğine göre `BLOCKED`, exact hit, normalized hit veya en az bir `U+FFFD` dokümanından
en az birinin bulunduğunu kanıtlar; hangisinin tetiklediği mevcut V3 artefaktlarından çıkarılamaz.
Bu yüzden V3 sonucu corpus-quality PASS değildir ve tahminle yeniden yorumlanamaz.

## Bilimsel ve operasyonel sınıflandırma

- Materyalizasyon: `PASS`.
- Karışık kaynak lightweight audit: `BLOCKED`, ayrıntılı neden korunmadı.
- OSCAR-only qualification: `NOT_RUN`.
- Human review: `NOT_RUN`.
- Tokenizer accounting: `NOT_RUN`.
- M2-A/M2-B training: `NOT_RUN` ve yetkisiz.
- Otomatik retry: yetkisiz.
- Cleanup/deletion: yapılmadı ve yetkisiz.

V3 kökü bundan sonra immutable/read-only bilimsel ve operasyonel kanıttır.

## Düzeltme yönü

Sonraki pass aynı 9.5 GB'ı tekrar indirmemelidir. Korunmuş V3 materyalizasyonunu salt okunur
doğrulamalı, exact `corpus == "OSCAR"` adayını fail-closed sınamalı ve gate uygulanmadan önce exact
label inventory ile boyutu sınırlı audit nedenlerini yeni bir köke atomik yazmalıdır. Bu pass split,
review, tokenizer accounting veya training açmamalıdır. Ayrı dondurulmuş sözleşme:
`documentation/contracts/corpora/vngrs-m2-oscar-audit-recovery-v1.md`.
