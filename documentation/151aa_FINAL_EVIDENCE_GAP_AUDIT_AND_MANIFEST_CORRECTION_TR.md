# Document 151aa — FINAL EVIDENCE-GAP AUDIT AND MANIFEST CORRECTION (TR)

**Tarih:** 2026-08-08 (Europe/Berlin)  
**Durum:** `READ_ONLY_AUDIT_COMPLETED`  
**Kapsam:** Document 151x repair root’unun altı mevcut dosyasının HU üzerinde source-read-only doğrulaması  
**HU yazımı:** `false`  
**Network/public HTTP:** `false`

## 1. Amaç ve korunmuş kayıtlar

Bu belge, kullanıcı tarafından yetkilendirilen bounded read-only audit sonucudur. Yalnızca Document
151x’in mevcut repair root’undaki altı dosya okundu; hiçbir HU dosyası, root’u veya önceki evidence
root’u değiştirilmedi. Scoring, inference, model/tokenizer erişimi, corpus materialization,
GPU/Slurm, training, cleanup ve Documents 152–154 işlemleri yapılmadı.

151x, 151y ve 151z değiştirilmemiştir:

| Belge | SHA-256 |
|---|---|
| 151x | `9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b` |
| 151y | `1309af278901009c22d2ee5b2438fdec886abe27cdaa60c4555dcd3af42ae6ba` |
| 151z | `51e3cdda3db8a636f1308a42910c2dd76bfdca5ef0906a3a316dc639c4b984db` |

## 2. HU repair-root file doğrulaması

İncelenen root:

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1
```

Altı dosyanın path, byte, SHA-256 ve satır/JSON biçimi doğrudan HU üzerinde yeniden doğrulandı:

| Dosya | Byte | Satır/biçim | SHA-256 |
|---|---:|---:|---|
| `coverage_repair_field_matrix.jsonl` | 114,649 | 150 | `19c45daa9454d3c13bd55bc3cb3f0b00865b7ddd37b04ea16e9c87393168d29b` |
| `coverage_repair_benchmark_registry.jsonl` | 20,091 | 3 | `22ca0fbd1581637a5d9b5590f5ec3763d5603bbb1923d128e245cc640929b04c` |
| `coverage_repair_source_model_registry.jsonl` | 5,307 | 3 | `4711d12d2e54d3b795b9e006d16d14a49d4d769f637ef5ec44949167f908d638` |
| `coverage_repair_report.json` | 3,382 | JSON object | `c70fbbfc6afc1639025a6ec7bbe4fd620cd606af87e5714e805df06385704f1b` |
| `output_artifact_manifest.jsonl` | 1,311 | 7 | `dee64588a922cd9be35e5710c00c837616e12aafea11f29bfaa4b9f8b131cdc2` |
| `post_repair_storage_audit.json` | 3,633 | JSON object | `a61520578cafb290618d521c04d8d211d06afdc559ca250e433e5b7636ec8812` |

## 3. Manifest-count correction

`output_artifact_manifest.jsonl` gerçek olarak **7 satır** içerir. Satırlar şunlardır:

```text
input_manifest.json
input_hash_ledger.jsonl
coverage_repair_field_matrix.jsonl
coverage_repair_benchmark_registry.jsonl
coverage_repair_source_model_registry.jsonl
coverage_repair_reconciliation.jsonl
coverage_repair_report.json
```

Bu, 151x Section 10’daki doğru zincirle uyumludur:

```text
seven prior artifacts → output_artifact_manifest.jsonl → post_repair_storage_audit.json
```

Document 151y Section 3’teki “previous eight outputs” ifadesi bu belgeyle append-only olarak
düzeltilmiştir. 151y’nin hash’i ve HU’daki başarılı dokuz-output execution kaydı korunur; 151y
yeniden yazılmamıştır. Manifest kendisini ve final audit’i içermemektedir.

## 4. Coverage ve registry reconciliation

Field matrix’in gerçek anahtarı `field_status`’tır. Sonuç:

| `field_status` | Satır |
|---|---:|
| `verified` | 96 |
| `not_reported` | 30 |
| `not_retrieved_in_this_wave` | 18 |
| `blocked` | 6 |
| **Toplam** | **150** |

Dolayısıyla `96 verified + 54 non-verified = 150` tam olarak sağlanır. Registry satırları da
field matrix ile uyumludur:

| Registry | Entity ID’leri | Satır başına alan | Registry status |
|---|---|---:|---|
| Benchmark | `benchmark.turblimp`, `benchmark.turkishmmlu`, `benchmark.turkish_exams` | 27 | `BLOCKED` (3/3) |
| Source model | `model.olmo_2_0425_1b`, `model.falcon_rw_1b`, `model.qwen2_5_1_5b` | 23 | `BLOCKED` (3/3) |

### Sınıflandırma kodları

- **C1 — provenance-required / derived gate:** Model veya benchmark seçimi için gerekli kimlik,
  compatibility, licence, tokenizer/repository veya evidence-complete registry alanı. `R1`:
  bounded 151x wave alanı toplamamıştır; bu public absence iddiası değildir. `R3`: registry
  status, required evidence-complete alanlar bulunmadığı için türetilmiş `BLOCKED` gate’idir.
- **C2 — admissible-not-reported:** Primary evidence’in açıkça raporlamadığı model/corpus/Türkçe
  exposure alanı. Bu alanlar `zero Turkish exposure` kanıtı değildir ve metadata’yı sonsuza kadar
  talep eden blocker’a dönüştürülmemelidir. `R2`: immutable registry `not_reported` taşıyor.
- **C3 — future-measurement-produced:** Chance, floor/ceiling ve benchmark-overlap prosedürü gibi
  sonuçtan bağımsız fakat ölçüm/kalibrasyon execution’ında üretilmesi gereken alanlar. `R4`:
  mevcut metadata registry bu alanı çözmez; measurement contract’a aktarılır.

### 54 non-verified alanın tam tablosu

| Entity | Field | Status | Blocker | Evidence reference | Class | Reason |
|---|---|---|---|---|---|---|
| `benchmark.turblimp` | `canonical_name` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turblimp` | `task_definition` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turblimp` | `subset_or_language` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turblimp` | `role_and_scientific_purpose` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turblimp` | `base_model_compatibility` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turblimp` | C1 | R2 |
| `benchmark.turblimp` | `chance_baseline_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turblimp` | C3 | R4 |
| `benchmark.turblimp` | `floor_ceiling_evidence_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turblimp` | C3 | R4 |
| `benchmark.turblimp` | `benchmark_corpus_overlap_procedure_reference_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turblimp` | C3 | R4 |
| `benchmark.turblimp` | `registry_status` | `blocked` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turblimp` | C1 | R3 |
| `benchmark.turkishmmlu` | `canonical_name` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkishmmlu` | `task_definition` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkishmmlu` | `subset_or_language` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkishmmlu` | `role_and_scientific_purpose` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkishmmlu` | `base_model_compatibility` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkishmmlu` | C1 | R2 |
| `benchmark.turkishmmlu` | `chance_baseline_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkishmmlu` | C3 | R4 |
| `benchmark.turkishmmlu` | `floor_ceiling_evidence_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkishmmlu` | C3 | R4 |
| `benchmark.turkishmmlu` | `benchmark_corpus_overlap_procedure_reference_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkishmmlu` | C3 | R4 |
| `benchmark.turkishmmlu` | `registry_status` | `blocked` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkishmmlu` | C1 | R3 |
| `benchmark.turkish_exams` | `canonical_name` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkish_exams` | `task_definition` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkish_exams` | `subset_or_language` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkish_exams` | `role_and_scientific_purpose` | `not_retrieved_in_this_wave` | `blocked_by_benchmark_registry` | `—` | C1 | R1 |
| `benchmark.turkish_exams` | `base_model_compatibility` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkish_exams` | C1 | R2 |
| `benchmark.turkish_exams` | `chance_baseline_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkish_exams` | C3 | R4 |
| `benchmark.turkish_exams` | `floor_ceiling_evidence_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkish_exams` | C3 | R4 |
| `benchmark.turkish_exams` | `benchmark_corpus_overlap_procedure_reference_or_status` | `not_reported` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkish_exams` | C3 | R4 |
| `benchmark.turkish_exams` | `registry_status` | `blocked` | `blocked_by_benchmark_registry` | `first_wave_benchmark_registry.jsonl#benchmark.turkish_exams` | C1 | R3 |
| `model.olmo_2_0425_1b` | `tokenizer_revision_or_status` | `not_retrieved_in_this_wave` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C1 | R1 |
| `model.olmo_2_0425_1b` | `architecture_or_runtime_compatibility` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C1 | R2 |
| `model.olmo_2_0425_1b` | `license` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C1 | R2 |
| `model.olmo_2_0425_1b` | `repository_metadata_sha256` | `not_retrieved_in_this_wave` | `blocked_by_source_model_provenance` | `—` | C1 | R1 |
| `model.olmo_2_0425_1b` | `documented_training_corpora` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C2 | R2 |
| `model.olmo_2_0425_1b` | `documented_language_mixture` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C2 | R2 |
| `model.olmo_2_0425_1b` | `explicit_turkish_evidence` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C2 | R2 |
| `model.olmo_2_0425_1b` | `turkish_evidence_status` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C2 | R2 |
| `model.olmo_2_0425_1b` | `registry_status` | `blocked` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.olmo_2_0425_1b` | C1 | R3 |
| `model.falcon_rw_1b` | `tokenizer_revision_or_status` | `not_retrieved_in_this_wave` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C1 | R1 |
| `model.falcon_rw_1b` | `architecture_or_runtime_compatibility` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C1 | R2 |
| `model.falcon_rw_1b` | `license` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C1 | R2 |
| `model.falcon_rw_1b` | `repository_metadata_sha256` | `not_retrieved_in_this_wave` | `blocked_by_source_model_provenance` | `—` | C1 | R1 |
| `model.falcon_rw_1b` | `documented_training_corpora` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C2 | R2 |
| `model.falcon_rw_1b` | `documented_language_mixture` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C2 | R2 |
| `model.falcon_rw_1b` | `explicit_turkish_evidence` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C2 | R2 |
| `model.falcon_rw_1b` | `turkish_evidence_status` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C2 | R2 |
| `model.falcon_rw_1b` | `registry_status` | `blocked` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.falcon_rw_1b` | C1 | R3 |
| `model.qwen2_5_1_5b` | `tokenizer_revision_or_status` | `not_retrieved_in_this_wave` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C1 | R1 |
| `model.qwen2_5_1_5b` | `architecture_or_runtime_compatibility` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C1 | R2 |
| `model.qwen2_5_1_5b` | `license` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C1 | R2 |
| `model.qwen2_5_1_5b` | `repository_metadata_sha256` | `not_retrieved_in_this_wave` | `blocked_by_source_model_provenance` | `—` | C1 | R1 |
| `model.qwen2_5_1_5b` | `documented_training_corpora` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C2 | R2 |
| `model.qwen2_5_1_5b` | `documented_language_mixture` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C2 | R2 |
| `model.qwen2_5_1_5b` | `explicit_turkish_evidence` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C2 | R2 |
| `model.qwen2_5_1_5b` | `turkish_evidence_status` | `not_reported` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C2 | R2 |
| `model.qwen2_5_1_5b` | `registry_status` | `blocked` | `blocked_by_source_model_provenance` | `first_wave_source_model_registry.jsonl#model.qwen2_5_1_5b` | C1 | R3 |

## 5. Gap interpretation and decision consequences

`blocked_by_benchmark_registry` gerçek bir current gate’tir: zorunlu benchmark identity/evaluator
evidence’i tamamlanmadan benchmark capability result üretilemez. Ancak chance baseline,
floor/ceiling ve overlap-procedure alanları metadata’nın eksikliği değil, 151ab’de dondurulacak
measurement deliverable’larıdır.

`blocked_by_source_model_provenance` de gerçek bir selection gate’idir: base/instruction stage,
runtime, licence ve tokenizer/repository kimliği çözülmeden bir model final winner olarak seçilemez.
Primary source’ların training corpus, language mixture veya explicit Turkish evidence bildirmemesi
ise `C2 admissible-not-reported` olarak korunur. Bu, OLMo/Falcon’ı “Turkish unseen” ilan etmeyi
yasaklar; Qwen’i multilingual positive control olarak kullanmayı da tek başına engellemez. Eksik
metadata, olmayan bir public claim’i sonsuza kadar istemek için kullanılmayacaktır.

Mevcut bilimsel durum:

```text
measurement_design_gate = blocked_by_measurement_design
training_gate = BLOCKED
ready_to_train = false
Documents 152–154 = unauthorized and uncreated
```

Bu belge 151y’yi veya 151z’yi yeniden yazmaz; yalnızca manifest-count narrative correction ve
gap authority sağlar. Measurement design için sonraki frozen authority Document 151ab’dir.
