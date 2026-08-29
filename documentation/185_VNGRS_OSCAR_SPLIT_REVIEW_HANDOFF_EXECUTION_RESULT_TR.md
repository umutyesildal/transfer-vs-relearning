# VNGRS OSCAR split ve review handoff yürütme sonucu

**Tarih:** 2026-08-29

**Job:** `481906`

**Sözleşme:** `vngrs-m2-oscar-split-review-handoff-v1`

**Sözleşme SHA-256:** `8d5784518afd5291a0e0302f17d5fba8dc38acd910e8414961f2336aa42a632e`

**Commit:** `fd0ca0b207ae2b9dc91ef7b77ae6957f3fff297b`

## Sonuç

Tek yetkili CPU pass tamamlandı. Exact 354,482 OSCAR dokümanı seed-42 kuralıyla 344,482 train ve
10,000 held-out dokümana ayrıldı; kümeler ayrık ve birleşimleri tam nüfusa eşit. Split SHA-256
`21f43359570ea66a73e969c1d0e8b4f08408f8ebbb71f50fc40dbd0d7e16f38f` olarak donduruldu.
64 satırlık paket ve boş karar şablonu üretildi; verdict veya reviewer alanı doldurulmadı. Phase 2,
tokenizer/model erişimi ve eğitim çalışmadı.

## Post-run integrity bulgusu

Fiziksel LF satırlarıyla yapılan bağımsız kontrolde manifest hash'leri, cardinality, uniqueness,
train/held-out ayrıklığı ve 64 ID'nin sample/packet/template eşitliği PASS verdi. Ancak 64 satırın
tamamı `oscar|q0` idi ve q1--q3 nüfus sayıları artifact'te bulunmadığından paket henüz insan verdict'i
için yeterince kanıtlanmış değildir.

Ayrıca bir excerpt içinde literal U+0085 bulundu. JSONL bozuk değildir; sorun `splitlines()`
çağrısının bu Unicode karakterini yanlışlıkla satır ayırıcı saymasıdır. Okuyucu fiziksel LF
semantiğine geçirildi ve regresyon testi eklendi.

Bu bulgular frozen split'i geçersiz kılmaz. Eski 64-paket yalnız verdict girişi bakımından
`PROVISIONAL / SUPERSEDED PENDING COVERAGE VALIDATION` kabul edilir. Yeni frozen sözleşme
`vngrs-m2-oscar-review-coverage-repair-v1` yalnız quartile nüfusunu ölçer ve gerekirse yeni 64-paketi
üretir. İnsan incelemesi, Phase 2 ve eğitim hâlâ açılmamıştır.
