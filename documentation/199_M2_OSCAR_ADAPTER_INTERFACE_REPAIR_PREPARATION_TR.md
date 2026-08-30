# 199 — M2 OSCAR tokenizer-adapter arayüz düzeltmesi hazırlığı

**Tarih:** 2026-08-31  
**Durum:** `LOCALLY IMPLEMENTED / TESTED / FROZEN / EXECUTION NOT AUTHORIZED`

## Sonuç

Job `482007` bellek yüzünden değil, `FrozenTokenizerAdapter` üzerinde doğrudan `eos_token_id`
aranması yüzünden terminal oldu. Kalıcı hata kaydı, traceback, Slurm exit ve stderr hashleri
Document 198'de donduruldu. Pending-only Document 197 relocation'ı koşul gerçekleşmediği için hiç
çalıştırılmadı ve artık uygulanamaz.

Yerelde yalnız adapter arayüz uyumluluğu düzeltildi: EOS kimliği hem doğrudan tokenizer'dan hem de
üretimdeki adapter'ın nested tokenizer nesnesinden güvenli biçimde çözülebiliyor. Üretim adapter
şeklini kullanan regresyon testi eklendi. Corpus, split, tokenizer snapshot, factual dose, token
bütçesi, sıralama ve streaming algoritması değişmedi.

Yeni fail-closed rota fresh root altında 4 CPU / 64G / 6 saat CPU wave'idir. 64G seçimi, başarısız
işin ölçülen yaklaşık 31.29 GiB peak RSS değerinin iki katından fazla headroom bırakır. Submitter,
önceki terminal root'u exact hashlerle doğrular; hiçbir eski job'u hold/cancel/release etmez ve
hiçbir eski root'u değiştirmez.

## Doğrulama

- adapter regression ve compatible exact-block suite: `12 passed`;
- Bash syntax: PASS;
- YAML parse: PASS;
- `git diff --check`: PASS;
- 4 CPU / 64G / 6h / CPU-only: PASS;
- fresh root, tek submission, no cancellation ve automatic-retry=false: PASS.

## Frozen contract

```text
documentation/contracts/corpora/vngrs-m2-oscar-exact-block-materialization-adapter-repair-v1.md
```

Final SHA-256:

```text
711deae9853287f9eeea62f35cc397a27a9c3ae3c3f8bbf2f65a8637d647508f
```

## Kapı

Bu hazırlık push, HU fast-forward veya Slurm submission yetkisi vermez. Exact contract SHA ve exact
implementation commit'e bağlı yeni kullanıcı yetkisi gerekir. GPU, weights, optimizer smoke,
M2-A/M2-B training, evaluation, cleanup, deletion ve otomatik retry kapalıdır.
