# VNGRS lowercase OSCAR audit recovery V1A yürütme sonucu ve kapı düzeltmesi

**Tarih:** 2026-08-29

**Durum:** `EXECUTED / ATOM-LEVEL GATE BLOCKED / INTERPRETATION REQUIRES REPAIR`

**Job:** `481886`

**Sözleşme:** `vngrs-m2-oscar-audit-recovery-v1a`

**Sözleşme SHA-256:** `cc28d822fb157b1783d6ec19042c890ffe7a33f3e3a02b7f8c6ad0bb144c2796`

## Korunan sonuç

Yetkili tek lowercase OSCAR pass'i tamamlandı. Exact `corpus == "oscar"` seçimi 354,482 belge ve
1,553,923,133 UTF-8 byte üretti. Split, 64-belgelik human review, tokenizer/model erişimi, Phase 2
ve eğitim açılmadı.

| Kanıt | Değer |
|---|---:|
| seçilen belge | 354,482 |
| source object | 32 |
| selected-ID SHA-256 | `c252d6b54d488e898f534564ef6c16196e22ae78f4fe0e61f83d4ad0bf83a056` |
| exact atom document-pattern hit | 439,906 |
| NFC/casefold atom document-pattern hit | 935,276 |
| invalid encoding belge | 0 |
| empty/very-short belge | 0 |
| boilerplate belge | 14,944 |
| SEO/betting belge | 17,304 |
| legal/jurisdiction belge | 5,181 |
| normalized duplicate group | 6,491 |
| duplicate gruplardaki belge | 36,091 |

Korunan output kökü:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_retry_v1
```

| Artifact | Byte | SHA-256 |
|---|---:|---|
| `reports/corpus_label_inventory.json` | 244 | `178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b` |
| `reports/lightweight_audit.json` | 66,616 | `2cac1f53dd924bfcf9866297ab4e2c447d26e67ef232cae589e1ade27668e939` |
| `control/recovery_state.json` | 505 | `49120b615a4516826c92fbc1693ca198ddd5cabbaabf5fb3242683de01f93f95` |

## Neden bu sayı doğrudan “sızıntı” değildir?

Eski audit 100 subject yüzeyi ile 500 answer/object yüzeyini bağımsız 600 substring olarak taradı.
Her şehir, meslek, çalışma alanı veya endüstri kelimesi kendi başına blocking hit oldu. Sayaçlar
unique belge değil, `document × pattern` çiftleridir; aynı belge birden fazla pattern'e katkıda
bulunabilir.

Persist edilmiş 256 exact ve 256 normalized bounded örneğin tamamı `object:*` sınıfındadır;
bunlarda sırasıyla 92 ve 90 farklı object pattern görülür. Bu, tüm 935,276 hit'in nesne-only
olduğunu kanıtlamaz; fakat mevcut bounded evidence gate'in sıradan cevap kelimeleri nedeniyle
bloklanabildiğini doğrudan gösterir. Dolayısıyla V1A'nın ham sayaçları korunur, ancak tek başına
sentetik fact contamination kararı olarak yorumlanmaz.

## Düzeltilecek karar kuralı

Bilimsel bir contamination adayı için aynı dokümanda:

```text
sentetik subject + o subject'e aynı fact_id ile bağlı answer
```

birlikte bulunmalıdır. `relation` bağı raporda korunur. Answer-only ve subject-only eşleşmeler
tanısal kalır, blocking olmaz. Exact veya NFC/casefold paired co-occurrence ile `U+FFFD` ise
fail-closed blocking koşuludur.

Bu değişiklik sonucu görüp threshold ayarlamak değildir; Relation V2'nin gerçek fact bağını eski
flattening işleminin kaybettiğini düzeltir. Önceki root ve BLOCKED state immutable/read-only kalır.

## Mevcut gate

```text
OSCAR label/volume                 PASS
atom-level surface audit          BLOCKED (historical, preserved)
fact-pair contamination audit     NOT_RUN / NEW AUTHORIZATION REQUIRED
split                             NOT_RUN
human review                      NOT_RUN
tokenizer accounting              NOT_RUN
M2 training                       NOT_RUN / UNAUTHORIZED
ready_to_train                    false
```

Yeni frozen sözleşme:
`documentation/contracts/corpora/vngrs-m2-oscar-fact-pair-contamination-audit-v1.md`.
