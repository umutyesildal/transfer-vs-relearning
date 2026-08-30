# 192 — M2 OSCAR exact block materialization hazırlığı ve kapısı

**Tarih:** 2026-08-30  
**Durum:** `IMPLEMENTED LOCALLY / TESTED / EXECUTION NOT AUTHORIZED`

## Sonuç

Document 191'deki exact block materialization artık local olarak implement edilmiştir. Operator,
aynı frozen OSCAR split'inden OLMo, Qwen ve SmolLM tokenizer'ları için ayrı ayrı:

- 97,536 adet 512-token M2-A train block;
- aynı toplam bütçeli M2-B train block;
- 2,048 adet ortak held-out validation block;
- exact 100-subject M1 popülasyonundan yalnız 50 Branch-B subject / 250 Turkish fact;
- 976 evenly spaced factual replacement block;
- consumed-document, discarded-tail, fact/relation exposure ve artifact SHA-256 audit'i

üretecek biçimde fail-closed hazırlanmıştır.

M2-B ekstra token eklemez. Her factual prefix, aynı indeksteki M2-A generic prefix'inin yerini
alır; kalan generic tail aynıdır. Her model içinde M2-A ve M2-B block, token ve optimizer-update
bütçesi birebir eşittir. Tokenizer farkı nedeniyle modellerin token ID'leri ve hedef bütçeye kadar
tükettikleri OSCAR document sayısı farklı olabilir; bu beklenen ve raporlanan heterogeneity'dir.

## Local doğrulama

Focused suite sonucu: `15 passed`.

Doğrulanan başlıca invariant'lar:

- exact 100 subject = 50 Branch A + 50 Branch B;
- exact Branch-B fact registry = 250 unique fact / 5 relation;
- Branch-A factual exposure = 0;
- input row sırası değişse bile seed-42 document order ve block çıktısı deterministik;
- M2-A/M2-B block ve token bütçeleri eşit;
- exact 976 replacement kuralı config'te frozen;
- per-fact ve per-relation exposure farkı en fazla bir;
- runner explicit flag olmadan execution-disabled;
- launcher CPU-only, offline ve fresh-root/duplicate-job/capacity gated;
- Bash syntax ve `git diff --check` PASS.

## Neden henüz HU job başlamadı?

Bu hazırlık bilimsel state mutation yaratacak yaklaşık çok-GB token-ID dosyaları üretir. Mevcut
yetkiler yalnız daha önceki Phase-2 evidence wave'ine aitti; yeni materialization contract'ını
otomatik olarak açmaz. Bu nedenle kod ve tek-wave contract hazırlanmış, fakat HU/SSH, push ve
Slurm yapılmamıştır.

Frozen contract:

```text
documentation/contracts/corpora/vngrs-m2-oscar-exact-block-materialization-v1.md
```

Execution başarılı olsa bile `ready_to_train=false` kalır. Sonrasında 250 satırlık Türkçe fact
registry için bounded insan verdict'i, parent hash capture, optimizer smoke ve ayrı M2 training
contract gerekir.
