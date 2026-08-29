# VNGRS OSCAR review-coverage repair yürütme sonucu

**Tarih:** 2026-08-29

**Durum:** `COVERAGE_VALIDATED / AWAITING_HUMAN_REVIEW`

**Job:** `481908` (`481907` yalnız `sbatch --test-only` tahmin numarasıdır)

**Sözleşme SHA-256:** `f05b43faaee6f2561af85a693cfff35194c7b7aaa467911de68684d4b5163f06`

**Yürütülen commit:** `09e1627afde68879d06567731ddd301793c3b4ff`

## Sonuç

Tek yetkili CPU pass tamamlandı. Korunmuş 354,482-doküman OSCAR nüfusu ve frozen
344,482/10,000 split yeniden doğrulandı; split yazılmadı veya değiştirilmedi. Gerçek quartile
envanteri yalnız q0'ın dolu olduğunu gösterdi:

| Stratum | Doküman | UTF-8 byte |
|---|---:|---:|
| q0 | 354,482 | 1,553,923,133 |
| q1 | 0 | 0 |
| q2 | 0 | 0 |
| q3 | 0 | 0 |

Dolayısıyla önceki paketin 64/64 q0 dağılımı bir örnekleme hatası değildir. Coverage-floor kuralı
yalnız dolu stratum q0'ı kapsayan yeni authoritative 64-paketi üretti. Packet semantic SHA-256
`73329e45fd8ff2c6b24c36fa6f9b5bac767b9d25726b691d527c71f9fdf90af8` değeridir.

## Artifact zinciri

Kök: `/vol/tmp2/yesildau/vngrs_m2_oscar_review_coverage_repair_v1` (205,216 byte).

- state: `3c0305d89f1496ea397694e18e7888e9d1dc58724ac588f3aa797240f73f24f6`
- final audit: `6ce5f1f7b13fa61ae3f9c021b237b0464e4989ae179dc73fe32030049772c177`
- manifest: `324eddfe5eee4e5cc9354c8f859fcc725ecd223684f7b95062e75ec68e765149`
- inventory: `8ff29ad8d72ad81616d4af3dee5951e55bde2752254988dad76c9cbbb03dd51f`
- review packet file: `621d8416f120803cc37f75453f0068a5fecaa60562698f11936b22caa3b75c61`
- sample: `008d6d14f5b5c5e0293291316981113f381ff41ecc0d10b9b2adad9d5cee4fcf`
- null-verdict template: `9bacc785ad3945c6acda1b593a6524c96ae09c651ac988de030e5c96a6785e65`

Terminal durum `AWAITING_HUMAN_REVIEW`; verdict girişi, tokenizer/model erişimi, Phase 2, eğitim,
cleanup ve retry yapılmadı. Authoritative packet yalnız yerel inceleme için indirildi ve corpus
excerpt'leri Git dışında tutuldu. Yerel self-contained HTML, seçimleri packet hash'ine bağlı
browser storage'da tutar ve ancak 64/64 karar tamamlanınca JSONL dışa aktarır.
