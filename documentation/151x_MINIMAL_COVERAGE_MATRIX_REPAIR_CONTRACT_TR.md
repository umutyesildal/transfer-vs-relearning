# Document 151x — Minimal Coverage-Matrix Repair Contract

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** FROZEN — UNEXECUTED  
**Amaç:** 151u/151v'de raporlanan ancak 151t'nin frozen per-entity-field sözleşmesini karşılamayan coverage ve composite registry kayıtlarını, yalnızca mevcut immutable evidence üzerinden düzeltmek  
**Execution yetkisi:** Bu doküman tek başına execution yetkisi vermez; ayrıca açık kullanıcı yetkisi gerekir.

## 1. Dar kapsam ve değişmezlik

Bu contract, yeni public metadata erişimi yapmadan mevcut evidence'ın şematik yeniden kurulmasını tarif eder. Source evidence ve historical reports read-only'dir. 151t, 151u, 151v, first-wave root ve retry root hiçbir şekilde overwrite, rename, delete veya in-place modify edilemez.

```text
immutable_first_wave_root = /vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1
immutable_retry_root      = /vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1
new_repair_root           = /vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1
```

`new_repair_root` bu hazırlık turunda oluşturulmamıştır. Gelecekteki tek bounded execution, yeni dosyaları yalnızca bu root altında yazabilir. HU home, repository çalışma ağacı ve her iki immutable root write hedefi değildir.

Bu contract şunları kesin olarak yasaklar: public HTTP/network, yeni download, scoring, inference, model/tokenizer weight veya snapshot erişimi, corpus materialization, GPU/Slurm, training, cleanup/deletion, artifact migration ve Documents 152--154 işlemleri.

## 2. İzin verilen immutable input seti

Gelecekteki execution yalnızca aşağıdaki mevcut input'ları okuyabilir; input hash'leri execution başında 151w'deki değerlerle karşılaştırılır. Herhangi bir path, hash veya byte uyuşmazlığı fail-closed `BLOCKED`'dır:

```text
first-wave/registries/coverage_matrix.jsonl
first-wave/registries/benchmark_registry.jsonl
first-wave/registries/source_model_registry.jsonl
retry/registries/retry_coverage_matrix.jsonl
retry/registries/retry_benchmark_registry.jsonl
retry/registries/retry_source_model_registry.jsonl
retry/reconciliation/first_wave_reuse_ledger.jsonl
retry/reports/retry_registry_completion_report.json
```

Execution, 151w'de kaydedilen first-wave ve retry root inventory/hash bulgularını da immutable reconciliation baseline'ı olarak kullanır. Yeni input keşfi, root dışına okuma veya unlisted source ekleme yoktur.

## 3. Frozen repair outputs

Yalnızca `new_repair_root` altında yeni dosyalar yazılabilir. Minimum output seti:

```text
input_manifest.json
input_hash_ledger.jsonl
coverage_repair_field_matrix.jsonl
coverage_repair_benchmark_registry.jsonl
coverage_repair_source_model_registry.jsonl
coverage_repair_reconciliation.jsonl
coverage_repair_report.json
post_repair_storage_audit.json
```

Her output için relative path, byte count, SHA-256 ve UTC creation timestamp tutulur. Output manifest'i kendisi dahil tüm yeni regular files'i listeler. Maksimum 32 yeni regular file, 16 MiB toplam yeni byte ve 300 saniye wall-clock sınırı vardır. Bu sınırlar local repair'ın bounded ve non-destructive olmasını sağlar; sınırdan biri aşılırsa sonuç `BLOCKED`'dır.

## 4. Zorunlu coverage field matrix

`coverage_repair_field_matrix.jsonl`, summary row değil, frozen required entity-field başına tam bir row üretir. Her row tam olarak şu 12 alanı taşır:

```text
entity_id
entity_type
field_name
required_for_pass
field_status
field_value_or_null
evidence_artifact_ids
evidence_sha256s
source_revisions
last_checked_utc
blocker_class_or_null
notes
```

Required entity seti:

```text
benchmark.turblimp
benchmark.turkishmmlu
benchmark.turkish_exams
model.olmo_2_0425_1b
model.falcon_rw_1b
model.qwen2_5_1_5b
```

CETVEL ve TurkBench first-wave'de görülen conditional adaylardır; required six entity setinin yerine geçmezler. İstenirse ayrıca `excluded_with_reason` ile kaydedilebilirler; fakat bu contract'ın PASS'ı için zorunlu değildirler.

Field status yalnızca şu değerlerden biri olabilir:

```text
verified
not_reported
not_retrieved_in_this_wave
not_applicable
access_blocked
conflicting_primary_sources
excluded_with_reason
blocked
```

`field_value_or_null` boş bırakılırsa `notes` içinde neden, `blocker_class_or_null` içinde uygun blocker bulunur. Tarihsel evidence'ta olmayan timestamp, byte, revision veya SHA-256 backfill edilemez. Aynı `entity_id + field_name` ikilisi iki kez yazılırsa fail-closed'tur.

## 5. Corrected benchmark registry

`coverage_repair_benchmark_registry.jsonl` tam olarak üç required benchmark row'u üretir ve 151q/151t'nin 27 alanını eksiksiz taşır:

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

Değerler yalnızca immutable input'tan kopyalanabilir veya input'lar arasında açıkça reconcile edilebilir. Evidence yoksa alan uydurulmaz; ilgili coverage row'u `not_retrieved_in_this_wave`, `not_reported`, `access_blocked` veya `blocked` olur. Registry row'undaki `registry_status`, coverage matrix ile tutarlı olmalıdır.

## 6. Corrected source-model registry

`coverage_repair_source_model_registry.jsonl` tam olarak üç frozen model row'u üretir ve şu 23 alanı eksiksiz taşır:

```text
model_id, exact_model_identifier, frozen_role, base_or_instruction_status,
training_stage, model_revision_or_release, tokenizer_revision_or_status,
architecture_or_runtime_compatibility, license, model_card_source_and_revision,
model_card_sha256, repository_source_and_revision, repository_metadata_sha256,
associated_paper_identifier_and_source, corpus_documentation_source_and_revision,
documented_training_corpora, documented_language_mixture, explicit_turkish_evidence,
turkish_evidence_status, provenance_label, retrieved_at_utc, registry_status, limitations
```

Required model identity'leri `model.olmo_2_0425_1b`, `model.falcon_rw_1b` ve `model.qwen2_5_1_5b` olarak korunur. Retry'daki `source_model.*` identifiers ayrı source artifact ID'si olabilir; required `model_id` yerine geçirilemez. Raw README/hash input'ı, model-card source/revision için evidence olabilir, fakat repository metadata, paper, corpus, language mixture veya Turkish evidence alanları input'ta yoksa doldurulmuş gibi gösterilemez.

## 7. Reconciliation and fail-closed rules

Execution başlamadan önce input manifest ve 151w baseline hash'leri doğrulanır. Aşağıdakilerden biri olursa hiç PASS üretilmez:

- immutable input hash/path/byte mismatch;
- bir required entity veya field row'unun eksikliği;
- duplicate entity-field row veya duplicate required registry identity;
- 12 coverage field'ından biri yokluğu;
- registry row key count veya coverage/registry field-set mismatch;
- evidence SHA, source revision veya `last_checked_utc` olmaması;
- status ile `field_value_or_null`/blocker/notes arasında tutarsızlık;
- first-wave/retry reuse hash mismatch;
- new repair root dışına herhangi bir yazım;
- file/byte/wall-clock limitinin aşılması.

Mevcut immutable evidence gerekli alanları desteklemiyorsa repair çıktısı complete-shaped olabilir, ancak field status'ları gerçeğe uygun biçimde `not_retrieved_in_this_wave`, `not_reported` veya `blocked` kalır ve karar `BLOCKED` olur. Bu contract, eksik public metadata'yı network kullanmadan kapatabileceğini varsaymaz.

## 8. PASS / CONDITIONAL / BLOCKED

`PASS` yalnızca şu koşulların tümüyle mümkündür: altı required entity için her required field row'u vardır; üç benchmark registry row'u 27 alanlıdır; üç model registry row'u 23 alanlıdır; zorunlu alanlar evidence artifact ID, evidence SHA, source revision ve timestamp ile `verified`/izin verilen `not_applicable` durumundadır; input/reuse/hash/path kontrolleri ve storage audit PASS'tır.

`CONDITIONAL` yalnızca required identity, immutable revision, artifact/evaluator identity, model provenance ve coverage schema tamamken non-gating contextual alanlar `not_reported`/`not_applicable` kaldığında kullanılabilir. Mevcut zorunlu alan eksiklikleri CONDITIONAL'a indirgenemez.

`BLOCKED`, yukarıdaki şartlardan herhangi biri sağlanmadığında zorunludur. Bu durumda repair wave yalnızca evidence-integrity/coverage-scheme sonucunu verir; global `blocked_by_measurement_design` gate'ini kapatmaz ve `ready_to_train` üretmez.

## 9. Reserved documents and explicit non-authorization

Document 151y olası repair-wave execution result, Document 151z olası post-repair decision gate olarak rezerve edilir; bu contract onları oluşturmaz ve herhangi bir execution başlatmaz.

151x'in freeze edilmesi 151t, 151u veya 151v'yi yeniden açmaz. Gelecekteki execution için gereken tek yetki, bu contract'ın hash'i ve yeni repair root'u açıkça belirten ayrı bir kullanıcı yetkisidir. Başarılı bir coverage repair dahi benchmark scoring, capability measurement, training veya Documents 152--154 için yetki sayılmaz.

## 10. Append-only protocol correction — effective overlay (2026-08-08)

**Pre-correction SHA-256:**
`a19ed3b7e15540fa2810d5f483b2015cc5badd2bd41949d8678f945d3a6fb32e`

Bu bölüm, 151x'in önceki metnine append-only olarak eklenmiştir ve yalnızca aşağıdaki
execution-protocol ayrıntılarını düzeltir. Önceki input seti, immutable-root kuralları, repair
mapping kuralları, byte/file/wall-clock bound'ları, yasaklar ve PASS/CONDITIONAL/BLOCKED
kararları aksi açıkça belirtilmedikçe aynı kalır.

### 10.1 Named artifact-manifest ve self-reference'sız final-audit zinciri

Section 3'teki minimum output seti aşağıdaki named file ile tamamlanır:

```text
output_artifact_manifest.jsonl
```

Execution output sırası ve kapsamı dondurulmuştur:

1. `input_manifest.json`
2. `input_hash_ledger.jsonl`
3. `coverage_repair_field_matrix.jsonl`
4. `coverage_repair_benchmark_registry.jsonl`
5. `coverage_repair_source_model_registry.jsonl`
6. `coverage_repair_reconciliation.jsonl`
7. `coverage_repair_report.json`
8. `output_artifact_manifest.jsonl`
9. `post_repair_storage_audit.json`

İlk yedi artifact tamamlandıktan ve her birinin relative path, byte count, SHA-256 ve UTC
timestamp değeri hesaplandıktan sonra `output_artifact_manifest.jsonl` yazılır. Manifest, ilk
yedi artifact'ın her biri için tam olarak şu alanları içeren bir JSONL row taşır:

```text
relative_path
byte_count
sha256
created_at_utc
```

Manifest kendi row'unu ve henüz yazılmamış `post_repair_storage_audit.json` dosyasını içermez.
Manifest'in kendi byte/SHA değerleri manifest içine yazılmaz; böylece manifest self-reference
oluşturmaz. Manifest'in path'i, byte count'u ve SHA-256'sı final audit tarafından dış referans
olarak kaydedilir.

`post_repair_storage_audit.json` dokuzuncu ve son repair-root output'udur. Final audit:

- tamamlanmış `output_artifact_manifest.jsonl` path'ini, byte count'unu ve SHA-256'sını;
- repair root'taki final regular-file count ve toplam byte değerlerini;
- output path'in `/vol/tmp2` altında kaldığını ve HU home'a yazılmadığını;
- immutable first-wave/retry input-root inventory ve path/hash sonuçlarını;
- preflight ve post-run storage/path/inode sonuçlarını

kaydetmelidir. Final audit kendi SHA-256'sını kendisi veya `output_artifact_manifest.jsonl`
içine yazmaz. Final audit'in byte count/SHA-256 değeri, gelecekte oluşturulabilecek Document
151y'de sonradan raporlanır; 151y hiçbir HU dosyasını yeniden yazmaz. Böylece zincir:

```text
seven prior artifacts -> output_artifact_manifest.jsonl -> post_repair_storage_audit.json
```

şeklinde tek yönlüdür ve hiçbir dosya kendisini hash'leyen bir kayıt içermez.

`output_artifact_manifest.jsonl` ve `post_repair_storage_audit.json` dahil toplam yeni regular
file sayısı yine `max_new_regular_files = 32` bound'u içindedir; named manifest bu bound'u veya
16 MiB toplam byte bound'unu genişletmez.

### 10.2 Exact required coverage cardinality

`coverage_repair_field_matrix.jsonl` required matrix'i **tam olarak 150 satır** içermelidir:

```text
3 required benchmark entities × 27 benchmark registry fields = 81 rows
3 required model entities     × 23 model registry fields     = 69 rows
                                                         total = 150 rows
```

Required benchmark entities yalnızca şunlardır:

```text
benchmark.turblimp
benchmark.turkishmmlu
benchmark.turkish_exams
```

Required model entities yalnızca şunlardır:

```text
model.olmo_2_0425_1b
model.falcon_rw_1b
model.qwen2_5_1_5b
```

Benchmark ve model registry field listeleri Sections 5 ve 6'da verilen exact listelerdir.
Required matrix'te her `(entity_id, field_name)` tuple'ı bir kez ve yalnızca bir kez bulunur;
her row `required_for_pass=true` ve Section 4'teki 12 coverage key'inin tamamını taşır.
Duplicate tuple, missing tuple, 150 dışı required-row sayısı veya CETVEL/TurkBench row'unun
required matrix'e dahil edilmesi doğrudan `BLOCKED`'dır. CETVEL ve TurkBench yalnızca ayrı,
optional/excluded evidence olarak tutulabilir; 150 satırlık required matrix'e eklenemez.

### 10.3 Mandatory HU preflight before any repair write

151x execution başlamadan ve `new_repair_root` altında ilk dosya oluşturulmadan önce documented
HU route üzerinden şu preflight tamamlanmalıdır:

```bash
HOME_ROOT=/vol/fob-vol6/mi25/yesildau
REPAIR_ROOT=/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1
du -xsh "$HOME_ROOT"
df -h "$HOME_ROOT" /vol/tmp /vol/tmp2
df -i "$HOME_ROOT" /vol/tmp /vol/tmp2
test ! -e "$REPAIR_ROOT"
readlink -f "$REPAIR_ROOT"
```

Preflight manifest'i home usage, `/vol/tmp` ve `/vol/tmp2` capacity/inode sonuçlarını, repair
root'un execution öncesi absent olduğunu ve resolved repair path'in `/vol/tmp2/yesildau/`
altında kaldığını kaydeder. Existing first-wave ve retry root'ları ayrıca read-only olarak
resolve edilir; bunlardan herhangi birinin write target olması veya repair root'un mevcut olması
fail-closed `BLOCKED`'dır. Preflight başarısızsa repair output'larından hiçbiri yazılamaz.

Bu effective overlay sonrasında 151x hâlâ **FROZEN — UNEXECUTED** durumundadır; repair root,
151y ve 151z bu correction pass'te oluşturulmamıştır.
