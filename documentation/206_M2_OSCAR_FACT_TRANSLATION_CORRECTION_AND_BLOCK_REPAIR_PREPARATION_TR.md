# 206 — M2 OSCAR fact çeviri düzeltmesi ve block-repair hazırlığı

**Tarih:** 2026-08-31  
**Durum:** `LOCAL CORRECTION PASS / BLOCK REPAIR FROZEN / UNEXECUTED`

Kullanıcının 250-fact review ledger'ı tam `243 usable + 7 issue` içerdi. İngilizce source-value
karşılaştırması sonucunda dört çeviri exact düzeltildi; `bilişim` ve iki `ekoloji` satırı doğru
Türkçe karşılık olarak değişmeden kabul edildi. Kullanıcının devam/düzeltme talebi bu yedi satırın
resolution authority'sidir.

Canonical CSV veya eski registry değiştirilmedi. Local pipeline eski 250-fact registry'yi exact
`784f78...bfec` SHA ile yeniden üretti, dört satırlık overlay'i uyguladı ve yeni registry'yi
`46a107...c4a2` SHA ile dondurdu. Corrected packet, registry ve 250 kararın tamamı metin/relation/
fact-ID/hash düzeyinde cross-validate edildi; sonuç `M2_FACT_REVIEW_PASS`, `usable=250` oldu.

Mevcut M2-B token block'ları eski Türkçe cümleleri taşıdığı için doğrudan training'e geçilemez.
Hazırlanan CPU operator 9.5 GB OSCAR objelerini yeniden okumaz: immutable M2-A bloklarını generic
kaynak olarak kullanır, üç tokenizer altında corrected factual schedule'ı kurar ve fresh root'a
yalnız üç corrected M2-B dosyasıyla audit/manifest yazar. Eski M2-A ve validation dosyaları hash
doğrulaması sonrası read-only referans olarak korunur.

Frozen contract:

```text
documentation/contracts/corpora/vngrs-m2-oscar-fact-translation-repair-v1.md
```

Final contract SHA-256:

```text
b02a1970b540cd3e0fdd0202cd174bd66a4f90baf5c1204f2b8fbeaf15a94992
```

Local relevant suite `18/18` PASS'tir. Bu hazırlık push, HU/SSH, CPU Slurm, tokenizer erişimi,
GPU, optimizer smoke, training, evaluation, cleanup, deletion veya retry yetkisi vermez. Exact
contract SHA ve commit kullanıcıya ayrı authorization için sunulmalıdır.
