# Document 151n — Phase-1 Measurement Evidence-Resolution Execution Result (TR)

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Contract:** Document 151m  
**Contract SHA-256:** `371c9c4fd2838626a731f802eec5e23666d265e4918d14a5cdf51e2c9ea881c0`  
**Durum:** `COMPLETED_WITH_EVIDENCE_BLOCKERS`  
**Phase-1 root:** `/vol/tmp2/yesildau/luna_phase1_measurement_evidence_resolution_v1`

## 1. Kapsam ve dürüst sonuç

Document 151m bir kez, bounded, source-read-only ve non-destructive olarak çalıştırıldı. Bu
sonuç yalnızca metadata/provenance resolution kaydıdır. Model inference, tokenizer/weight
erişimi, BPC/PPL, benchmark scoring, full benchmark/corpus materialization, contamination scan,
GPU/Slurm, training, cleanup, deletion veya migration yapılmadı. Mevcut bounded-audit root ve
repair root değiştirilmedi.

Operasyonel bounds ve immutable-root kontrolü PASS oldu; bilimsel evidence gate'leri kapanmadı.
İlk otomatik synthetic alan seçiminin contract grain'e uymadığı fark edilince mevcut dosyalar
overwrite edilmeden append-only correction evidence yazıldı. İlk hatalı sayımlar tarihsel kayıt
olarak korunuyor ve contract evidence sayılmıyor.

## 2. Zaman ve request muhasebesi

| Ölçüm | Değer |
|---|---:|
| Phase-1 execution start | `2026-08-07T15:40:42.712432+00:00` |
| Phase-1 execution end | `2026-08-07T15:40:47.776842+00:00` |
| Execution wall time | yaklaşık `5.064 s` |
| Public HTTP requests | `11 / 96` |
| Retries | `0 / 16` |
| Response bytes | `254,456 / 268,435,456` |
| Phase-1 root post-run storage | `3,229,528 bytes` before append-only correction |
| Post-correction root inventory | `35 files`, `3,745,674 bytes` |

Execution duration, HTTP response intervals ve response-generation duration aynı kavram değildir.
Bu dalgada LLM/model response generation hiç çalıştırılmadı; dolayısıyla model response-generation
duration yoktur. HTTP request başlangıç/bitiş zamanları `manifests/request_ledger.json` içindedir.
`15:43:24.959745+00:00` zamanındaki ek işlem yalnızca HU read-only synthetic schema kontrolü ve
new-root append-only correction evidence yazımıdır; yeni network request yapılmadı.

## 3. Synthetic inventory düzeltmesi

Frozen profil kaynağı:

`/vol/fob-vol6/mi25/yesildau/synthetic-data-generation/output/relation_v2/data/canonical_subject_profiles_5000.csv`

Profil SHA-256: `60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1`.

Doğru grain ile append-only correction evidence şu değerleri doğruladı:

| Birim | Sonuç |
|---|---:|
| Unique subjects | `5,000` |
| Semantic facts (`subject_id|source_relation`) | `25,000` |
| Bilingual resolved rows (semantic fact × language) | `50,000` türetilmiş grain |
| EN+TR normalize canonical surface candidate | `713` |
| Canonical surface candidate SHA-256 | `01203090614dea66b2cb8c882953d044d3afbc15aad4c9bfef7769298f214d22` |
| Source-relation semantic-fact manifest SHA-256 | `65f7a7b802d902a144b7df2aafe9937efb447cf0410347cd026167816a912320` |

Bu `713`, profile EN/TR normalized-surface candidate'ıdır; frozen historical `713` declaration,
exact membership definition ve historical set SHA'sı yeniden kurulamadı. `829` için exact set
definition/source/hash bulunamadı. Bu nedenle 713 ve 829 reconciliation gate'i
`blocked_by_synthetic_inventory_provenance` olarak kalır.

Release manifestindeki source relations:
`profession`, `born_in`, `lives_in`, `field_of_study`, `works_in_industry`.
151m'nin frozen relation listesi `profession`, `birthplace`, `residence`, `university`,
`employer` ile birebir uyuşmaz. `field_of_study`/`works_in_industry` değerleri sessizce
`university`/`employer` olarak yeniden adlandırılmadı.

İlk yürütmede kullanılan fazla geniş selector metadata/bucket alanlarını ve language-expanded
alanları relation kabul etti; bu nedenle `95,000` semantic fact ve `10,718` surface çıktıları
geçersiz candidate olarak üretildi. Bu dosyalar silinmedi veya overwrite edilmedi; correction
appendix bu hatayı açıkça kaydeder.

## 4. Benchmark registry

TurBLiMP, TurkishMMLU, Turkish EXAMS, CETVEL ve TurkBench için sabit sırada public primary
metadata sayfaları alındı. Her registry satırı `blocked` durumundadır: exact item manifest,
split/item ID listesi ve hash'i, evaluator revision/code hash'i, scoring/normalization rule'u ve
benchmark overlap procedure'ı Phase-1 içinde tam olarak çözülemedi. Publication identifier'ları
item-release revision olarak varsayılmadı. Bu nedenle primary decision:
`blocked_by_benchmark_registry`.

## 5. Source-model metadata

OLMo-2-0425-1B, Falcon-RW-1B ve Qwen2.5-1.5B için yalnızca public API/model-card metadata'sı
alındı; weight veya tokenizer indirilmedi. API revision ve lisans alanları kaydedildi, fakat
training-corpus revision'ları, tokenizer revision'ları ve gerekli Türkçe provenance kanıtı
complete değildir. Bağımlı karar `blocked_by_source_model_provenance` olarak kaldı.

## 6. Pattern/alias/contamination kapsamı

Pattern/alias/template provenance dosyaları yalnızca read-only incelendi. `65,717` exact
inventory set/hash'i, complete alias inventory ve exact training-sentence inventory yeniden
üretilemedi. Contamination tiers ve required hit schema kaydedildi; full-corpus veya bounded
sample contamination scan yapılmadı. Gate `blocked_by_contamination_definition` olarak kaldı.

## 7. Integrity ve storage audit

- Existing root `/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1` unchanged;
  pre/post inventory SHA: `22c23c2b72f499f991283f7b56201b868108a3c5b92a4d6460253388e0d24319`.
- Repair root `/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1` unchanged;
  pre/post inventory SHA: `15e2eab0454b8c8aa33da8e26fd667db9575ceb6b6d2c34785233ca5f9e691ea`.
- Initial post-run audit SHA-256:
  `411ac40f377fb82d6b80e44c680b971ab6075810fd6d2d5b7e21d24d59af9cf9`.
- Initial final file hash ledger SHA-256:
  `62653cccdb9a7b9fc77b10ce53792e4bac5177af68a5583a7fb746e8b7876b8c`.
- Append-only correction audit SHA-256:
  `b00673be07e6574ccd8fef08468d32a959f3464e269158878140e37d60c4087c`.
- Append-only correction hash ledger SHA-256:
  `87daa6e20cd40a72f741214c5350609487f57f394ed521d060f31f5bce9171fa`.
- HU home was `14G`; no new large regular file was created by this Phase-1 wave. Existing
  frozen model/environment files listed by the mandatory audit predated this wave.

## 8. Authorization boundary

Document 151j çalıştırılmadı; Documents 151k/151l oluşturulmadı. Documents 152–154, training,
M2-A/M2-B construction and `ready_to_train` yetkili değildir. Bu execution yalnız 151n ve 151o
sonuç kayıtlarının hazırlanmasına hizmet eder.

