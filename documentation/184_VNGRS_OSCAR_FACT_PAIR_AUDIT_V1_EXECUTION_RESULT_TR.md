# VNGRS OSCAR fact-pair contamination audit V1 yürütme sonucu

**Tarih:** 2026-08-29

**Durum:** `AUDIT_COMPLETE / PASS`

**Job:** `481904`

**Sözleşme:** `vngrs-m2-oscar-fact-pair-contamination-audit-v1`

**Sözleşme SHA-256:** `eee2da1d2ea166f05443e8ebba591d4b1c519475e6b029f9e73293cee870075d`

**Yürütülen commit:** `cfa8b46f5e045207e6e32cee27af3529774e3535`

## Sonuç

Tek yetkili CPU pass korunmuş V3 materyalizasyonunu ve V1A atom-audit kanıtını read-only kullandı.
Exact lowercase `corpus == "oscar"` nüfusunda 354,482 dokümanı yeniden doğruladı. Relation V2'nin
500 `subject_id -> fact_id -> relation -> answer` bağıyla yapılan taramada exact veya NFC/casefold
subject-answer co-occurrence bulunmadı; `U+FFFD` invalid-encoding belgesi de yoktu.

```text
exact subject-only document-surface pairs       0
normalized subject-only document-surface pairs  0
exact paired document-fact pairs                0
normalized paired document-fact pairs           0
invalid-encoding documents                      0
```

Bu sonuç, aynı nüfustaki predecessor 439,906 exact ve 935,276 normalized atom hit'in sentetik
subject kaynaklı olmadığını gösterir: tüm atom hit'ler answer/object yüzeyleridir. Önceki V1A
BLOCKED kaydı değiştirilmez; onun flatten edilmiş gate'inin bilimsel yorumu bu yeni fact-bound
evidence ile düzeltilir.

## Korunan artifact'ler

Kök: `/vol/tmp2/yesildau/vngrs_m2_oscar_fact_pair_audit_v1`

| Artifact | Byte | SHA-256 |
|---|---:|---|
| `reports/corpus_label_inventory.json` | 244 | `178991f311336a4acead1bb00fe8043d60a18c590e809b11629ca64f4920ee2b` |
| `reports/fact_pair_contamination_audit.json` | 1,501 | `bf076ab36fc31b16ab6f47d4a02ff04877177c1562e8bda2f8bb11f1a14091d3` |
| `control/recovery_state.json` | 608 | `381772af2ce8ebca68aa30ee6862e0933689abb88dabafcf499d96603c5dba57` |

Root toplamı yaklaşık 24 KiB'dir. `control/d0_failure.json` yoktur. Aynı isimli aktif veya pending
job yoktur. `sacct`, Munge/SlurmDBD authentication arızası nedeniyle accounting satırı vermedi;
bu eksik scheduler metadatasıdır, tamamlanmış hash-bound terminal artifact'leri geçersiz kılmaz.

## Kapı

```text
exact OSCAR identity/volume          PASS
fact-pair contamination             PASS
invalid encoding                    PASS
deterministic split                 NOT_RUN
64-document human-review packet     NOT_RUN
human verdicts                      NOT_RUN
tokenizer/model access              NOT_RUN
Phase 2 / M2 training               NOT_RUN / UNAUTHORIZED
ready_to_train                      false
```

Bu PASS corpus'un tüm kalite boyutlarında otomatik kabulü değildir. V1A'daki boilerplate,
SEO/betting, legal/jurisdiction ve duplicate sayaçları tanısal kalır; precommitted 64-document
human review bunların kullanılabilirlik etkisini değerlendirmeden eğitim açılmaz.

Bir sonraki frozen sınır yalnız deterministic OSCAR split ve review handoff üretimidir:
`documentation/contracts/corpora/vngrs-m2-oscar-split-review-handoff-v1.md`.
