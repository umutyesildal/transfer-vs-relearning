# VNGRS OSCAR audit recovery V1 yürütme sonucu

**Tarih:** 2026-08-29

**Durum:** `BLOCKED / EXACT-LABEL MISMATCH`

**Job:** `481863`

**Sözleşme:** `vngrs-m2-oscar-audit-recovery-v1`

**Sözleşme SHA-256:** `ab3ad95cc6126682d8206715a0d3e01d80784f81e01944a655750e839d06b442`

## Sonuç

Tek yetkili recovery pass korunmuş V3 materyalizasyonunun 5,671,686 dokümanını okudu ve exact
source-label inventory'yi başarıyla kalıcılaştırdı. Önceden aday olarak dondurulan uppercase
`corpus == "OSCAR"` etiketi gözlenmediği için pass fail-closed durdu. Audit başlamadı; split,
human review, tokenizer/model erişimi ve eğitim açılmadı.

## Exact label inventory

| Exact label | Doküman | UTF-8 byte | Doküman payı | Byte payı |
|---|---:|---:|---:|---:|
| `oscar` | 354,482 | 1,553,923,133 | 6.25% | 9.8663% |
| `mc4` | 5,317,204 | 14,195,860,459 | 93.75% | 90.1337% |
| toplam | 5,671,686 | 15,749,783,592 | 100% | 100% |

Korunan kanıtlar:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_v1/reports/corpus_label_inventory.json
SHA-256 178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b

/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_v1/control/d0_failure.json
SHA-256 6ce9a5dfc302498e4713ed03293962ca53f40f97daef28ffeea49d8fbc2e813b
```

## Sınıflandırma

Bu corpus-volume başarısızlığı değildir. Exact lowercase `oscar` nüfusu minimum 10,001-document
kapısını yaklaşık 35.4 kat geçmektedir. Bu yalnız predeclared candidate-label case mismatch'idir.
İlk recovery kökü immutable/read-only kanıt olarak korunmalıdır.

Audit, contamination/encoding kararı, split, review ve tokenizer accounting `NOT_RUN` kalır.
Otomatik retry yoktur. Sonraki tek düzeltme exact predicate'i `corpus == "oscar"` olarak bağlamalı,
ilk recovery kökünü doğrulamalı ve yeni bir kök kullanmalıdır.
