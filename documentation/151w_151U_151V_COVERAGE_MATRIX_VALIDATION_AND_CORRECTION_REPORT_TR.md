# Document 151w — 151u/151v Coverage-Matrix Validation and Correction Report

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** FINAL LOCAL VALIDATION REPORT  
**Kapsam:** Yalnızca handoff'ta listelenen mevcut HU dosyalarının bounded, read-only incelemesi ve yerel dokümantasyon düzeltmesi  
**Sonuç:** `BLOCKED` — frozen per-entity-field coverage sözleşmesi ve zorunlu registry alanları doğrulanamadı

## 1. Yetki, yöntem ve değişmezlik

Bu rapor, living handoff'taki **“Validate the 151u/151v coverage-matrix PASS and prepare repair if needed”** override'ının tek yürütümüdür. HU üzerinde yalnızca dosya açma, JSONL okuma, satır/anahtar/status sayımı, SHA-256 hesaplama ve recursive read-only inventory yapıldı.

Bu turda HU'ya hiçbir dosya yazılmadı; mevcut first-wave root veya retry root değiştirilmedi. Public HTTP, network kaynak erişimi, scoring, inference, model/tokenizer ağırlığı veya snapshot erişimi, corpus materialization, GPU/Slurm, training, cleanup, deletion ve Documents 152--154 yoktur. Documents 151t, 151u ve 151v yerelde de değiştirilmemiştir.

İnceleme, handoff'ta izin verilen şu sekiz mevcut dosyayla sınırlı tutuldu:

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/coverage_matrix.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/benchmark_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/source_model_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_coverage_matrix.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_benchmark_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_source_model_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reconciliation/first_wave_reuse_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reports/retry_registry_completion_report.json
```

## 2. Root ve dosya bütünlüğü

Recursive root inventory'leri read-only olarak yeniden üretildi. Root inventory SHA'sı, relative path, regular-file byte sayısı ve dosya SHA-256 değerlerinin deterministik sıralı envanter özetidir; bu, dosya içeriklerini değiştiren bir işlem değildir.

| Kapsam | Regular files | Toplam byte | Inventory SHA-256 |
|---|---:|---:|---|
| First-wave root `luna_benchmark_model_metadata_registry_completion_v1` | 91 | 13,063,617 | `4e06a47ddf58a81a3d6a86e4dc0dee75c0d123ff6b38dbda6d76e7be51daf3ad` |
| Retry root `luna_benchmark_model_metadata_registry_completion_retry_v1` | 16 | 38,315,850 | `8cd5d889b4875a95d54241d038dcb12e5cf4a22df9b6fd602823fb3473d2a13a` |

İzin verilen dosyaların doğrudan SHA-256 ve satır sayıları:

| Dosya | Byte | JSONL satır | SHA-256 |
|---|---:|---:|---|
| first-wave `coverage_matrix.jsonl` | 55,436 | 132 | `77f1397f03ec3615af000b2917505a5d964ab817285678bbc920e1bb31ae80cc` |
| first-wave `benchmark_registry.jsonl` | 20,447 | 3 | `06f3f797014ba58382d94605303b42a449623ce22523155ac3ebcc038f989afd` |
| first-wave `source_model_registry.jsonl` | 5,262 | 3 | `ac98933957e9ec8595453413ebefda0c8409f5d0a0cd3f3e05cf24a581e745fc` |
| retry `retry_coverage_matrix.jsonl` | 2,940 | 6 | `8787ad5df982c64383883e90a66c65aed15f10a5743e9df025f3b8daddefc951` |
| retry `retry_benchmark_registry.jsonl` | 3,018 | 3 | `7f7deb55e1340d175ed7cf25e4c16d9b5efd717a72815a9a72d39881f62a1eaa` |
| retry `retry_source_model_registry.jsonl` | 4,242 | 3 | `d311665829b223e344d69082c3dab4a5126bdaab0a4a8d314c655084cffeb610` |
| retry `first_wave_reuse_ledger.jsonl` | 40,674 | 91 | `057e1c3d71939ea91ce49e5a2496885c981d1ffc1d2c6f91fb1e1e372787c01a` |
| retry `retry_registry_completion_report.json` | 8,544 | JSON object | `cdc7dfc04aa3898f155b0195e78291b9f28784496230247e70b3ad903c4ae261` |

Reuse ledger'de 91 satır vardır; tüm status değerleri `read_only_reconciled`, tüm `copied_to_retry_root` değerleri `false` ve source root first-wave root'tur. Bu, önceki root'un değişmediği yönündeki storage/reconciliation bulgusunu destekler; coverage sözleşmesindeki eksiklikleri tamamlamaz.

## 3. Frozen coverage sözleşmesine karşı kontrol

151q/151t'nin zorunlu coverage row şeması tam olarak şu 12 alandır:

```text
entity_id, entity_type, field_name, required_for_pass, field_status,
field_value_or_null, evidence_artifact_ids, evidence_sha256s, source_revisions,
last_checked_utc, blocker_class_or_null, notes
```

İzin verilen field status vocabulary'si `verified`, `not_reported`, `not_retrieved_in_this_wave`, `not_applicable`, `access_blocked`, `conflicting_primary_sources`, `excluded_with_reason` ve frozen retry addendum'ındaki `blocked` değeridir. Özet bir entity satırı, per-field row yerine geçmez.

| İncelenen matrix | Satır yapısı | Zorunlu coverage alanları | Sonuç |
|---|---|---|---|
| First-wave `coverage_matrix.jsonl` | 132 field-level satır; 8 entity | Her satırda 9 anahtar; `evidence_sha256s`, `source_revisions`, `last_checked_utc` yok | `BLOCKED` |
| Retry `retry_coverage_matrix.jsonl` | 6 entity-summary satırı; 3 benchmark + 3 `source_model` | 12 alanlı frozen coverage row yok; her satır 12 zorunlu alanın tamamını taşımıyor | `BLOCKED` |

First-wave 132 satırın dağılımı şöyledir:

| Entity grubu | Entity sayısı | Her entity için distinct `field_name` | Satır toplamı | Sözleşme bulgusu |
|---|---:|---:|---:|---|
| Zorunlu benchmarklar: TurBLiMP, TurkishMMLU, EXAMS | 3 | 21 | 63 | Her benchmark için 6 registry field adı yok: `canonical_name`, `task_definition`, `subset_or_language`, `role_and_scientific_purpose`, `primary_or_secondary_role`, `limitations` |
| Zorunlu modeller: OLMo, Falcon, Qwen | 3 | 21 | 63 | Registry'nin 23 alanına karşı `model_id` ve `limitations` coverage field adı yok |
| Koşullu adaylar: CETVEL, TurkBench | 2 | 3 | 6 | Tam zorunlu benchmark coverage matrix değil; conditional aday satırları olarak korunabilir |

Dolayısıyla first-wave matrix'in field-level görünmesi olumlu bir yapısal bulgudur; ancak coverage metadata'sının üç zorunlu alanı bütün 132 satırda eksik olduğundan ve zorunlu field set'leri tamamlanmadığından PASS için yeterli değildir. CETVEL/TurkBench satırları, zorunlu üç benchmarkın eksikliğini telafi etmez.

Retry matrix'i daha doğrudan bir ihlal gösterir: satırlar `coverage_id`, `domain`, `source_id`, `status` gibi özet alanları içerir; `entity_id`, `entity_type`, `field_name`, `field_status`, `evidence_sha256s`, `source_revisions`, `last_checked_utc` ve diğer frozen coverage alanlarının per-field temsilini sağlamaz. Ayrıca model entity kimlikleri `source_model.*` biçimindedir; 151t'nin frozen required model kimlikleri `model.*` biçimindedir. Bu identity mismatch de coverage eşleşmesini fail-closed yapar.

## 4. Benchmark registry alan kontrolü

Frozen benchmark registry 27 alan gerektirir:

```text
benchmark_id, canonical_name, task_definition, subset_or_language,
role_and_scientific_purpose, primary_or_secondary_role,
primary_dataset_repository_or_url, immutable_dataset_revision_or_release,
exact_split_names, item_count_per_split, ordered_item_id_manifest_artifact_id,
ordered_item_id_manifest_sha256, item_file_artifact_id_or_null,
item_file_sha256_or_null, license_and_access_evidence_id,
evaluator_repository_or_url, evaluator_revision_or_release, evaluator_code_sha256,
normalization_rule_metadata_only, scoring_rule_metadata_only, base_model_compatibility,
chance_baseline_or_status, floor_ceiling_evidence_or_status,
benchmark_corpus_overlap_procedure_reference_or_status, retrieved_at_utc,
registry_status, limitations
```

| Registry | Entity | Key/alan bulgusu | Status |
|---|---|---|---|
| First-wave | `benchmark.turblimp` | 24 key; yukarıdaki 4 alan yok: `canonical_name`, `task_definition`, `subset_or_language`, `role_and_scientific_purpose` | `PASS` etiketi schema-compliant completion kanıtı değil |
| First-wave | `benchmark.turkishmmlu` | Aynı 4 alan yok | `PASS` etiketi schema-compliant completion kanıtı değil |
| First-wave | `benchmark.turkish_exams` | Aynı 4 alan yok | `BLOCKED` |
| Retry | `benchmark.turblimp`, `benchmark.turkishmmlu` | Her satır yalnızca özet kimlik/status bilgisi; 27 alanın 26'sı yok | `reused_read_only` |
| Retry | `benchmark.turkish_exams` | 13 key; 27 alanın 26'sı yok | `acquired_exact` |

Bu nedenle EXAMS artifact'ının exact acquisition/hash bulgusu başarılı olsa da retry benchmark registry'si contract-compliant 27-field registry değildir.

## 5. Üç model provenance satırının kontrolü

Frozen source-model registry 23 alan gerektirir:

```text
model_id, exact_model_identifier, frozen_role, base_or_instruction_status,
training_stage, model_revision_or_release, tokenizer_revision_or_status,
architecture_or_runtime_compatibility, license, model_card_source_and_revision,
model_card_sha256, repository_source_and_revision, repository_metadata_sha256,
associated_paper_identifier_and_source, corpus_documentation_source_and_revision,
documented_training_corpora, documented_language_mixture, explicit_turkish_evidence,
turkish_evidence_status, provenance_label, retrieved_at_utc, registry_status, limitations
```

| Model | First-wave registry | Retry provenance row | Doğrulama |
|---|---|---|---|
| `model.olmo_2_0425_1b` / OLMo-2-0425-1B | 23 key mevcut; `registry_status=BLOCKED`; `model_card_sha256=null` | `source_model.olmo_2_0425_1b`; immutable revision `a1847dff35000b4271fa70afc5db10fd29fedbdf`; `complete_raw_readme`; 23 zorunlu model alanının tamamı registry row'da yok | Raw README response/hash provenance artifact'ıdır; complete model provenance değildir |
| `model.falcon_rw_1b` / Falcon RW-1B | 23 key mevcut; `registry_status=BLOCKED`; `model_card_sha256=null` | `source_model.falcon_rw_1b`; immutable revision `e4b9872bb803165eb22f0a867d4e6a64d34fce19`; `complete_raw_readme`; 23 zorunlu alanın tamamı yok | Aynı |
| `model.qwen2_5_1_5b` / Qwen2.5-1.5B | 23 key mevcut; `registry_status=BLOCKED`; `model_card_sha256=null` | `source_model.qwen2_5_1_5b`; immutable revision `8faed761d45a263340a0528343f099c05c9a4323`; `complete_raw_readme`; 23 zorunlu alanın tamamı yok | Aynı |

İlk-wave model registry'sinin 23 key taşıması yalnızca anahtar şeması kontrolüdür; üç satırın da `BLOCKED` olması ve model-card SHA'sının null olması provenance PASS'ını engeller. Retry'daki üç raw README response'u model/tokenizer ağırlığı değildir ve ağırlık erişimi yapılmadı; ancak ham README'nin alınmış olması `documented_training_corpora`, `documented_language_mixture`, `explicit_turkish_evidence`, `provenance_label` ve diğer zorunlu provenance alanlarının tamamının kanıtlandığı anlamına gelmez.

## 6. 151u/151v PASS kararının düzeltilmiş yorumu

Retry report JSON'ı `status=PASS`, `retry_gate=pass`, `violations=[]` bildiriyor; 151v de altı coverage satırını PASS checklist'inde sayıyor. Bu sonuç, 151t'nin frozen per-required-entity-field kuralıyla uyumlu değildir. Altı satır entity-summary düzeyindedir; altı satırın her biri için tüm required field'ların ayrı coverage row'u yoktur.

Bu nedenle:

- 151u ve 151v **silinmez veya değiştirilmez**; tarihsel execution/gate kayıtları olarak korunur.
- 151u/151v'nin EXAMS artifact'ı, üç raw model-card response'u, request/file/hash/reuse bulguları, immutable-root reconciliation'ı ve storage bulguları başarılı scope facts olarak korunur.
- Yalnızca contract-compliant coverage/registry yorumu `PROVISIONAL / UNSUPPORTED BY THE FROZEN COVERAGE RULE` olarak düzeltilir.
- Bu validation'ın dar sonucu `BLOCKED`; birincil düzeltme blocker'ı `blocked_by_coverage_schema`, eşlik eden blocker `blocked_by_benchmark_registry`'dir.
- Global bilimsel gate `blocked_by_measurement_design` olarak kalır. `ready_to_train=false`; training ve Documents 152--154 yetkili değildir.

Eksik evidence alanlarını tarihsel değerlerle uydurmak, first-wave/retry registry'lerini geriye dönük değiştirmek veya yeni HTTP ile doldurmak bu correction pass'in kapsamı değildir. Bu nedenle minimal, çalıştırılmamış coverage repair contract'ı Document 151x olarak hazırlandı.

## 7. Sonraki doküman ve yetki sınırı

Document 151x yalnızca mevcut immutable first/retry evidence'tan complete field-level matrix ve corrected composite registries üretmeyi tarif eder; çalıştırılmamıştır. Yeni bir repair wave gelecekte ayrıca yetkilendirilmedikçe HU'ya, network'e veya public HTTP'ye erişemez. 151y ve 151z, sırasıyla olası repair-result ve post-repair-gate kayıtları olarak yalnızca rezerve edilmiştir; oluşturulmamış ve yetkilendirilmemiştir.

Bu raporun amacı 151u/151v'nin başarılı operational artifacts'ını gizlemek değil, coverage PASS'ının frozen schema açısından desteklenmediğini açıkça kayda geçirmektir.
