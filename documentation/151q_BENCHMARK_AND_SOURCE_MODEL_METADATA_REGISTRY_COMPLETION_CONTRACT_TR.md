# Document 151q — Benchmark and Source-Model Metadata Registry Completion Contract (TR)

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Contract ID:** `151q`  
**Durum:** **UNEXECUTED — bu turda yalnızca sözleşme oluşturuldu**  
**Upstream correction authority:** Document 151p  
**Upstream SHA-256:** `9dfe3ce759aa6d257d39f5f1dc6b1b8a2ff3e5ad8d70c0667aa1c70344b6eb5c`  
**Tür:** bounded, source-read-only, non-destructive metadata-registry completion contract  
**Current global gate:** `blocked_by_measurement_design`  
**Training gate:** `BLOCKED`

## 1. Status, amaç ve execution sınırı

Bu belge, Document 151p'nin `incomplete_collection_or_extraction_from_the_executed_bounded_wave`
olarak bıraktığı benchmark ve source-model metadata registry kanıtını tamamlamak için frozen bir
gelecek execution contract'tır. Bu turda contract çalıştırılmadı; HU, SSH, network, API, public
terms kabulü, download, benchmark scoring, model/tokenizer inference, corpus işi, GPU, Slurm,
training, cleanup veya deletion yapılmadı.

Amaç yalnızca şunları immutable kimlik, revision, manifest, hash, lisans/erişim ve evaluator
metadata'sı ile kayıt altına almaktır:

1. TurBLiMP, TurkishMMLU ve Turkish EXAMS benchmark registry'leri;
2. Exact task relevance ve resmi item/evaluator kaynağı gösterilebilirse CETVEL veya TurkBench'ten
   seçilecek task registry'si;
3. `allenai/OLMo-2-0425-1B`, `tiiuae/falcon-rw-1b` ve `Qwen/Qwen2.5-1.5B` source-model
   provenance registry'si.

Bu contract benchmark scoring, model inference, Turkish capability measurement, BPC/PPL,
contamination/overlap adjudication, corpus download, full benchmark materialization, model veya
tokenizer ağırlığı erişimi ve training authorization vermez. Başarılı execution yalnızca iki
metadata-registry component'ini güncelleyebilir; global `blocked_by_measurement_design` gate'ini
ve training gate'ini kapatamaz.

## 2. Korunan kayıtlar ve rezerve execution belgeleri

Önceki chronological kayıtlar değiştirilmez:

- Documents 151d ve 151e: historical preliminary/provisional evidence;
- Document 151p: current local validation and blocker-correction authority;
- Documents 151k ve 151l: superseded 151j path'inden rezerve, oluşturulmayacak ve yetkisiz.

Bu contract'ın gelecekteki tek execution wave'i için, bu turda oluşturulmadan şu belgeler rezerve
edilir:

```text
Document 151r — benchmark/source-model metadata registry execution result
Document 151s — post-registry-completion decision gate
```

151r ve 151s bu contract'ın parçası olarak gelecekteki açık execution authorization içinde
oluşturulabilir; bu turda oluşturulmaz ve 151k/151l yerine kullanılamaz.

## 3. Immutable root'lar ve yeni future scratch root

Aşağıdaki mevcut evidence root'ları immutable/read-only kabul edilir; hiçbir dosya, manifest,
report, cache veya ledger overwrite edilemez:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1
/vol/tmp2/yesildau/luna_phase1_measurement_evidence_resolution_v1
```

151q execution'ı için yeni ve açık scratch root:

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1
```

Bu contract hazırlanırken yeni root veya alt dizinleri oluşturulmaz. Gelecekte yalnızca bu root
altına yeni dosyalar yazılabilir:

```text
contracts/
registries/
manifests/
requests/
reports/
logs/
tmp/
```

Repository-local path'ler resolved path açıkça scratch'e işaret etmiyorsa output destination
olamaz. HU home'a output yazılamaz. Source repository, model cache, benchmark cache ve mevcut
evidence root'ları write destination değildir.

## 4. Frozen source set ve resmi primary-source route

Execution başlamadan önce preflight manifest, aşağıdaki immutable source order'ı ve her source
route'unu yazmak zorundadır. Paper landing page yalnızca bağlam sağlayabilir; tek başına hiçbir
registry alanını doğrulayamaz.

### 4.1 Zorunlu benchmark adayları

| Sıra | `source_id` | Zorunluluk | Frozen resmi primary route | Bilimsel rol |
|---:|---|---|---|---|
| 1 | `benchmark.turblimp` | zorunlu | Benchmark maintainer'ın resmi dataset/release repository'si veya dataset card'ı; aynı release için resmi evaluator/scoring repository'si | tercih edilen bağımsız linguistic diagnostic |
| 2 | `benchmark.turkishmmlu` | zorunlu | Benchmark maintainer'ın resmi dataset/release repository'si; exact task/subset için resmi evaluator/scoring kaynağı | broad Turkish knowledge/reasoning diagnostic |
| 3 | `benchmark.turkish_exams` | zorunlu | Turkish EXAMS maintainer'ın resmi dataset/release repository'si; exact Turkish subset ve evaluator kaynağı | broad school/knowledge diagnostic |

Her route için canonical URL/repository, immutable commit/tag/release ve erişim türü preflight'ta
tek tek yazılır. Resmi source route bulunamaz, yalnızca paper route kalır veya route immutable
revision vermiyorsa source `blocked` olur; tahmini URL, commit, split, item count veya hash
kullanılamaz.

### 4.2 Koşullu benchmark adayları

| `source_id` | Koşullu route | Inclusion şartı | Aksi durumda |
|---|---|---|---|
| `benchmark.cetvel.<task_id>` | CETVEL maintainer'ın resmi task/release repository'si ve resmi evaluator'ı | exact task relevance, immutable item revision, item manifest/hash ve evaluator revision/code hash birlikte kanıtlanır | `excluded_with_reason` |
| `benchmark.turkbench.<task_id>` | TurkBench maintainer'ın resmi task/release repository'si ve resmi evaluator'ı | exact task relevance, immutable item revision, item manifest/hash ve evaluator revision/code hash birlikte kanıtlanır | `excluded_with_reason` |

CETVEL/TurkBench için genel benchmark adı, paper veya toplu leaderboard tek başına relevance
kanıtı değildir. Birden fazla task varsa her task ayrı `source_id` ve ayrı coverage row alır.
İlgisiz, yalnızca instruction-only veya evaluator/item kaynağı çözülemeyen task scientific
failure olarak değil, gerekçeli exclusion veya blocker olarak raporlanır.

### 4.3 Zorunlu source-model adayları ve roller

| Sıra | `source_id` | Exact model ID | Frozen role | Resmi primary route seti |
|---:|---|---|---|---|
| 1 | `model.olmo_2_0425_1b` | `allenai/OLMo-2-0425-1B` | a priori English-dominant candidate | resmi model card, resmi repository revision, associated paper, resmi training-corpus/language documentation |
| 2 | `model.falcon_rw_1b` | `tiiuae/falcon-rw-1b` | secondary comparator candidate | resmi model card, resmi repository revision, associated paper, resmi training-corpus/language documentation |
| 3 | `model.qwen2_5_1_5b` | `Qwen/Qwen2.5-1.5B` | multilingual/Turkish positive control | resmi model card, resmi repository revision, associated paper, resmi training-corpus/language documentation |

Model card, repository, paper ve corpus documentation farklı primary evidence source'larıdır;
birinin eksikliği diğerinden sessizce tamamlanamaz. Qwen'in positive-control rolü Türkçe maruziyet
kanıtı yerine geçmez. OLMo veya Falcon için Turkish documentation yokluğu, sıfır Turkish exposure
iddiasına dönüştürülemez.

### 4.4 Source selection kuralları

1. Preflight, her source için canonical URL/repository, beklenen access type, source owner,
   candidate revision/release alanını yazmadan ilk request yapılamaz.
2. Default branch, floating `latest` veya değişken dataset card immutable revision sayılmaz.
3. Resmi source birden fazla eligible release veriyorsa execution, source'un açıkça
   `recommended/default` olarak işaretlediği release'i seçer; böyle bir tekil işaret yoksa
   seçim yapılmaz ve `conflicting_primary_sources`/`blocked` yazılır.
4. Resmi primary route erişilemiyorsa response'a göre mirror, başka repository veya yeni task
   seçilemez. Yalnızca preflight'ta önceden belirtilmiş resmi mirror kullanılabilir.
5. Response-dependent benchmark/task selection, failed-source replacement, opportunistic
   fallback ve paper-only completion yasaktır.

## 5. Field-level status vocabulary

Her registry alanı coverage matrix'te bulunur ve aşağıdaki status'lardan tam biriyle raporlanır:

```text
verified
not_reported
not_retrieved_in_this_wave
not_applicable
access_blocked
conflicting_primary_sources
excluded_with_reason
```

Kurallar:

- `verified`: değer, immutable source/revision ve evidence artifact/hash ile desteklenmiştir.
- `not_reported`: source gerçekten kontrol edilmiş, fakat alan source'ta raporlanmamıştır.
- `not_retrieved_in_this_wave`: gerekli source veya artifact bu bounded wave'de alınmamıştır;
  public absence iddiası değildir.
- `not_applicable`: alanın bu entity/task için neden uygulanmadığı açıklanmıştır.
- `access_blocked`: permission, HTTP/access restriction, terms veya operational limit nedeniyle
  source alınamamıştır; gözlenen hata kanıtı saklanır.
- `conflicting_primary_sources`: iki veya daha fazla primary source farklı değer/revision
  bildirir; değer seçilmez, tüm conflict evidence korunur.
- `excluded_with_reason`: yalnızca koşullu CETVEL/TurkBench task'leri veya bilimsel kapsam dışı
  candidate'ler için, açık inclusion/relevance gerekçesiyle kullanılır.

Generic `NR`, boş string veya yalnızca `blocked` field status olarak kullanılamaz. `not_reported`,
`not_retrieved_in_this_wave` ve `access_blocked` birbirinin yerine geçirilemez.

## 6. Required evidence schemas

### 6.1 Preflight manifest

İlk request'ten önce yeni root'a yazılacak `preflight_manifest.json` en az şu alanları içerir:

```text
contract_id = 151q
contract_sha256
execution_run_id
source_order
source_id
canonical_primary_url_or_repository
declared_official_mirror_or_null
expected_access_type
candidate_revision_or_release_or_null
sampling_seed = 42
ordering_rule = source_order_then_lexicographic_path_then_item_id
runtime_version
code_revision_and_sha256
planned_request_count
all_frozen_bounds
existing_root_inventories_and_sha256
```

Bir execution run'ında aynı source_id için response'a göre yeni route eklenemez.

### 6.2 Request ledger

Her request, başarısız veya retry dahil, `request_ledger.jsonl` içine bir kez yazılır:

```text
request_id
request_sequence
work_package
source_id
source_url
request_method
request_start_utc
response_end_utc
http_status
retry_count
redirect_count
response_transferred_bytes
content_encoding
response_sha256
saved_artifact_id_or_null
failure_class_or_null
runtime_version
code_revision_and_sha256
```

`response_transferred_bytes` request-level bir değerdir. Aynı response byte count'u her item/file
row'una kopyalanamaz ve record byte toplamı olarak tekrar tekrar toplanamaz.

### 6.3 Retained response/file manifest

Her retained metadata, item manifest veya evaluator file için `file_manifest.jsonl` gerekir:

```text
artifact_id
source_id
artifact_kind = metadata | item_manifest | item_file | evaluator_source | model_card | repository_metadata | paper | corpus_documentation
source_url_or_repository
immutable_revision_or_release
task_or_subset_or_null
split_or_null
local_relative_path
exact_serialized_file_bytes
retrieved_at_utc
http_status_or_local_source_status
sha256
license_or_access_evidence_id
status
```

Her retained file için exact serialized file byte count ve SHA-256, request-level response byte
count'tan ayrı tutulur. Büyük archive, full benchmark dataset, model weights, tokenizer files ve
full repository checkout retained artifact olamaz.

### 6.4 Benchmark registry row

Her zorunlu ve koşullu candidate için, exclusion dahil, şu alanlar bulunur:

```text
benchmark_id
canonical_name
task_definition
subset_or_language
role_and_scientific_purpose
primary_or_secondary_role
primary_dataset_repository_or_url
immutable_dataset_revision_or_release
exact_split_names
item_count_per_split
ordered_item_id_manifest_artifact_id
ordered_item_id_manifest_sha256
item_file_artifact_id_or_null
item_file_sha256_or_null
license_and_access_evidence_id
evaluator_repository_or_url
evaluator_revision_or_release
evaluator_code_sha256
normalization_rule_metadata_only
scoring_rule_metadata_only
base_model_compatibility
chance_baseline_or_status
floor_ceiling_evidence_or_status
benchmark_corpus_overlap_procedure_reference_or_status
retrieved_at_utc
registry_status
limitations
```

`item_count_per_split` item manifest/hash olmadan verified sayılamaz. Scoring rule kaydı
scoring çalıştırmak anlamına gelmez; bu contract'ta evaluator yalnızca metadata/code identity
olarak tutulur.

### 6.5 Source-model registry row

Her model için şu alanlar coverage matrix ile birlikte tutulur:

```text
model_id
exact_model_identifier
frozen_role
base_or_instruction_status
training_stage
model_revision_or_release
tokenizer_revision_or_status
architecture_or_runtime_compatibility
license
model_card_source_and_revision
model_card_sha256
repository_source_and_revision
repository_metadata_sha256
associated_paper_identifier_and_source
corpus_documentation_source_and_revision
documented_training_corpora
documented_language_mixture
explicit_turkish_evidence
turkish_evidence_status
provenance_label
retrieved_at_utc
registry_status
limitations
```

`provenance_label` yalnızca evidence ile seçilebilir. Kullanılabilecek conservative labels:

```text
documented_multilingual_with_Turkish
documented_English_dominant_Turkish_fraction_unreported
Turkish_exposure_not_resolvable
not_suitable_training_stage
```

`Turkish_exposure_not_resolvable`, zero exposure değildir. Model/tokenizer weight veya snapshot
indirilmeden yalnızca küçük public metadata/config/README/API response dosyaları tutulabilir.

### 6.6 Mandatory coverage matrix

`coverage_matrix.jsonl` her benchmark/model row ve her required field için row üretir; yalnızca
başarılı değerler yazılamaz:

```text
entity_id
entity_type = benchmark | model
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

Coverage matrix'te row eksikliği contract violation'dır. Her `not_reported`,
`not_retrieved_in_this_wave`, `access_blocked` veya `conflicting_primary_sources` row'u neden ve
blocker class ile açıklanır.

## 7. Frozen operational bounds

Gelecekteki tek execution wave'i için, ilk request'ten önce şu bounds değiştirilemez:

```text
max_total_http_requests = 96
max_total_retries = 16
max_total_response_bytes = 268435456          # 256 MiB; failed/retry bodies dahil
max_single_retained_file_bytes = 33554432     # 32 MiB
max_total_new_retained_bytes = 134217728      # 128 MiB
max_wall_clock_seconds = 1800                 # 30 dakika
max_new_regular_files = 256
max_new_storage_bytes = 536870912             # 512 MiB; logs/tmp dahil
max_redirects_per_request = 5
```

Yanıt body'si, redirect, failed request ve retry response byte'ları total response bound'a
sayılır. 32 MiB üzerindeki metadata/item/evaluator dosyası kaydedilemez. Archive extraction,
full benchmark/corpus download, full repository clone, model weight/tokenizer snapshot ve broad
crawl yasaktır.

Her bound'a zorunlu registry completion gerçekleşmeden ulaşılırsa execution fail-closed olarak
`blocked_by_operational_access` biter. Bound aşıldığında yeni source, yeni root veya sessiz retry
ile devam edilemez.

Gelecek HU execution'ından hemen önce AGENTS.md preflight'ı ayrıca uygulanır: home/scratch
capacity ve inode, resolved destination, existing-root inventory, projected file/byte count ve
retention policy kaydedilir. Bu contract hazırlanırken hiçbir HU preflight'ı çalıştırılmaz.

## 8. Deterministic execution protocol

1. Contract SHA, source order, candidate source routes, code/runtime revision ve bounds yeni root
   altındaki preflight manifest'e yazılır.
2. Mevcut üç immutable root'un path/inode/file inventory ve SHA'sı doğrulanır; herhangi bir
   mismatch execution'ı fail-closed yapar.
3. Source'lar sabit sırada işlenir: TurBLiMP, TurkishMMLU, Turkish EXAMS, koşullu CETVEL/TurkBench
   task'leri ve sonra OLMo, Falcon, Qwen model source setleri. Her source içindeki path, split ve
   item ID ordering lexicographic'tir.
4. İlk resmi metadata/release response'ları alınır; exact immutable revision, split, item set ve
   evaluator identity response'tan uydurulmaz, source'ta açıkça bulunmalıdır.
5. Aynı source'un paper landing page'i, mirror'i veya başka release'i favorable response için
   seçilemez. İlk source başarısızsa failed-page replacement yapılamaz.
6. Her request ve retained artifact ledger'a yazılır; hash yazılmadan registry row `verified`
   olamaz.
7. Duplicate `source_id`, duplicate benchmark item ID, duplicate model ID veya duplicate artifact
   ID; manifest/coverage mismatch; missing mandatory field; unbounded response; route/path mismatch
   execution'ı fail-closed yapar.
8. Hiçbir benchmark item evaluator ile çalıştırılmaz, hiçbir model/tokenizer çağrılmaz ve hiçbir
   overlap/capability score üretilmez.

## 9. WP-A — Benchmark registry completion

### 9.1 Zorunlu pass alanları

TurBLiMP, TurkishMMLU ve Turkish EXAMS için her row aşağıdaki alanlarda `verified` veya meşru
`not_applicable` evidence taşımalıdır: canonical task/subset, official dataset/repository,
immutable release/commit, exact splits, item counts, ordered item-ID manifest ve SHA-256, license/
access evidence, official evaluator source revision ve code SHA-256. `normalization_rule_metadata`
ve `scoring_rule_metadata` ayrıca coverage row alır; scoring yürütülmez.

`base_model_compatibility`, chance/floor/ceiling evidence ve benchmark-corpus overlap procedure
metadata olarak kaydedilir. Bu alanların source'ta raporlanmaması `not_reported` olabilir, ancak
baseline measurement contract'ı freeze etmek için yeterli değildir.

### 9.2 CETVEL/TurkBench kararı

Koşullu task, exact relevance ve resmi item/evaluator evidence tamamlanırsa `included` registry
row'u alır. Aksi durumda `excluded_with_reason` veya gerekli primary evidence eksikse `blocked`
row'u alınır. Genel isim, citation veya leaderboard ile task dahil edilemez.

### 9.3 Benchmark overlap sınırı

151q overlap procedure'ı icat etmez, full corpus scan yapmaz ve contamination tier'larını
çalıştırmaz. Mevcut frozen overlap procedure reference kaydedilir; yoksa `not_reported` olarak
coverage matrix'e yazılır ve future measurement-design blocker olarak kalır.

## 10. WP-B — Source-model metadata completion

Üç exact model ID için base/instruction status, training stage, model revision, tokenizer
revision/status, license, model card/repository/paper/corpus documentation evidence, documented
language mixture, explicit Turkish evidence, runtime compatibility ve experimental role ayrı ayrı
parse edilir.

Official source'lar farklı revision veya language claim verirse conflict rows korunur; ajan
seçimiyle tek bir değer üretilmez. Missing Turkish field `not_reported` veya
`not_retrieved_in_this_wave` olarak kalır; hiçbir durumda `zero_turkish_exposure` yazılamaz.

## 11. Exact decision rules

### 11.1 Per-field ve per-entity rules

- Required field `verified` veya gerekçeli `not_applicable` değilse entity `PASS` olamaz.
- `not_reported`, `not_retrieved_in_this_wave`, `access_blocked` veya
  `conflicting_primary_sources` required field'de ise entity `BLOCKED` olur.
- Optional contextual field `not_reported` olabilir; exact identity, revision, item/evaluator
  manifest ve hash alanları optional değildir.
- `excluded_with_reason` yalnızca koşullu candidate'i registry kapsamı dışında bırakır; zorunlu
  TurBLiMP/TurkishMMLU/EXAMS veya üç frozen model ID için kullanılamaz.
- Duplicate, missing hash, response/file byte mismatch, missing timestamp veya source route
  substitution entity'yi doğrudan `BLOCKED` yapar.

### 11.2 Contract result

```text
PASS:
  - üç zorunlu benchmark registry row'u exact source/revision/split/item/evaluator/hash alanlarıyla
    complete;
  - üç source-model row'u mandatory provenance fields ile complete;
  - koşullu CETVEL/TurkBench task'leri ya verified included ya da gerekçeli excluded;
  - request/file/coverage manifests bütünlük kontrollerinden geçer;
  - hiçbir contract bound veya fail-closed kuralı tetiklenmez.

CONDITIONAL:
  - zorunlu identity/revision/item/evaluator artifacts complete ve hash'li;
  - yalnızca non-gating contextual fields not_reported/not_applicable veya koşullu candidate
    exclusion vardır;
  - coverage ve ledger bütünlüğü PASS'tir;
  - global measurement-design gate yine açık kalır.

BLOCKED:
  - herhangi bir zorunlu field missing/not_retrieved/access_blocked/conflicting;
  - exact immutable revision, item manifest/hash, evaluator revision/code hash veya model
    provenance chain kurulamıyor;
  - duplicate ID, missing manifest field, hash/byte/timestamp mismatch, path mismatch veya
    response/retry/time/file/storage bound ihlali var;
  - source paper-only kalıyor ya da resmi route response'a göre değiştiriliyor.
```

`PASS` veya `CONDITIONAL` yalnızca registry completion result'ıdır. Hiçbir durumda
`ready_to_train`, `ready_to_execute_bounded_measurement_audit` veya global measurement-design
gate closed anlamına gelmez. Post-gate report, benchmark overlap definitions, Turkish capability
measurement, BPC/PPL, inference/scoring ve training için ayrı unresolved/blocked durumları
korumak zorundadır.

## 12. Future execution deliverables

Gelecekteki execution wave'i yalnızca yeni 151q root'unda şunları üretebilir:

```text
preflight_manifest.json
requests/request_ledger.jsonl
manifests/file_manifest.jsonl
registries/benchmark_registry.jsonl
registries/source_model_registry.jsonl
registries/coverage_matrix.jsonl
manifests/hash_ledger.jsonl
reports/registry_completion_report.json
reports/registry_completion_report.md
```

Execution sonucunda Document 151r ve post-execution gate Document 151s oluşturulabilir. Bu
contract'ın başarılı olması 151p'nin synthetic inventory kararını yeniden açmaz, 65,717
inventory'yi değiştirmez ve herhangi bir later measurement/training document'ı oluşturmaz.

## 13. Single authorization boundary

Bu belge hazırlanırken 151q **UNEXECUTED** kalır. Bundan sonraki tek yetki isteği şudur:

> User explicitly authorizes one bounded, source-read-only, non-destructive execution of frozen
> Document 151q, including creation of Documents 151r and 151s, with the frozen source set,
> bounds, manifests and fail-closed rules above. This does not authorize 151k/151l, benchmark
> scoring, model/tokenizer access, corpus or model downloads, capability measurement, GPU/Slurm,
> training, cleanup, deletion, migration or Documents 152–154.

Bu turda bu authorization uygulanmadı; contract çalıştırılmadı ve hiçbir remote/network erişimi
yapılmadı.

---

## APPEND-ONLY CORRECTION ADDENDUM — 2026-08-07

### A. Correction identity, preservation and current status

Bu addendum, Document 151q'nın önceki 525 satırlık gövdesini yeniden yazmaz ve önceki SHA-256
değerini geçersiz kılmaz. Önceki gövdenin SHA-256 değeri aşağıdaki gibi korunur:

```text
pre_correction_151q_sha256 = b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c
```

Bu addendum, `main`/latest gibi hareketli branch isimlerini daha sonra kullanılacak immutable
revision yerine geçirmez. Addendum'ın effective overlay'ı şudur:

```text
correction_type = append_only_public_metadata_route_resolution
repair_pass_status = COMPLETED_WITH_PREPARATION_BLOCKER
151q_execution_status = UNEXECUTED
151r_status = RESERVED_UNCREATED
151s_status = RESERVED_UNCREATED
current_global_gate = blocked_by_measurement_design
training_gate = BLOCKED
```

Route-resolution pass yalnızca 2026-08-07 tarihinde kamuya açık GitHub, Hugging Face ve paper/
model-card metadata sayfalarının read-only incelenmesiyle yapıldı. Benchmark item gövdeleri,
response archives, model/tokenizer snapshot'ları, weights, inference, scoring, corpus ve HU/SSH
erişimi bu pass'in parçası değildi. Aşağıdaki repair-pass sınırları değişmez:

```text
max_public_http_requests = 32
max_total_retries = 8
max_total_response_bytes = 16777216
max_single_response_bytes = 4194304
max_wall_clock_seconds = 1200
```

Bu pass için 151q execution ledger'ı veya registry artifact'ı oluşturulmadı. Public metadata
route-resolution request'leri daha sonraki 151q request ledger'ına eklenemez ve onun request
bound'ını tüketmiş sayılmaz.

### B. Resolved canonical public routes

Aşağıdaki URL'ler allowlist'e alınabilecek canonical public route kimlikleridir. Route'un
görülebilir olması, benchmark item hash'lerinin veya source repository'nin immutable revision
kararının tamamlandığı anlamına gelmez.

#### B.1 TurBLiMP

```text
canonical_repository = https://github.com/ezgibasar/TurBLiMP
official_branch_observed = main
observed_dataset_roots =
  data/base/
  data/experimental/
  data/human_judgments/
observed_supplementary_root = supplementary_materials/
official_evaluator_path = evaluation.py
```

Public tree metadata `data/base/` altında `augmented_anaphor_agreement.csv`,
`augmented_argument_structure_ditransitive.csv`, `augmented_argument_structure_transitive.csv`,
`augmented_binding.csv`, `augmented_determiners.csv`, `augmented_ellipsis.csv`,
`augmented_irregular_forms.csv`, `augmented_island_effects.csv`, `augmented_nominalization.csv`,
`augmented_npi_licensing.csv`, `augmented_passives.csv`, `augmented_quantifiers.csv`,
`augmented_relative_clauses.csv`, `augmented_scrambling.csv`, `augmented_subject_verb_agreement.csv`
ve `augmented_suspended_affixation.csv` yollarını gösterdi. `data/experimental/` ve
`data/human_judgments/` altındaki exact file allowlist ise bu bounded metadata pass'inde
deterministik olarak listelenemedi. Ayrıca resmi repository'nin current `main` tipinin full
immutable commit SHA'sı public page extraction'ında görünmedi. `297de13fb7a0ce524fe32e8b175c6b5255d66960`
değeri, canonical `evaluation.py` yoluna işaret eden üçüncü taraf bir public metadata kaydında
geçen historical commit'tir; current official release/evaluator tipinin yerine otomatik olarak
terfi ettirilmemiştir.

Sonuç: canonical repository ve evaluator path **RESOLVED**, fakat full immutable source revision,
complete item-file allowlist ve corresponding evaluator revision/code hash **UNRESOLVED**.
TurBLiMP zorunlu registry row'u execution için `BLOCKED` kalır.

#### B.2 TurkishMMLU

```text
canonical_maintainer_repository = https://github.com/ArdaYueksel/TurkishMMLU
official_branch_observed = main
observed_repository_roots = dev/ ; test/ ; turkishmmlu_sub.json
observed_test_paths =
  test/TurkishMMLU_Biology.json
  test/TurkishMMLU_Chemistry.json
  test/TurkishMMLU_Geography.json
  test/TurkishMMLU_History.json
  test/TurkishMMLU_Mathematics.json
  test/TurkishMMLU_Philosophy.json
  test/TurkishMMLU_Physics.json
  test/TurkishMMLU_Religion and Ethics.json
  test/TurkishMMLU_Turkish Language and Literature.json
official_dataset_route_candidate = https://huggingface.co/datasets/AYueksel/TurkishMMLU
```

Maintainer README's public access instruction email-based access'i belirtir; bu pass'te email,
terms kabulü veya dataset item retrieval yapılmadı. Hugging Face metadata'sında `main` README
history için görülen `fcbe5bb` kısa revision, exact full immutable dataset revision olarak
doğrulanmadı. Maintainer repository içinde benchmark scoring/evaluator için deterministically
freeze edilebilir bir official evaluator path ve corresponding code revision bu pass'te
belirlenemedi. EleutherAI lm-evaluation-harness içindeki TurkishMMLU task route'u bağımsız bir
harness route'udur; maintainer'ın official evaluator'ı olarak varsayılmaz.

Sonuç: canonical maintainer repo, observed test paths ve dataset route candidate **RESOLVED**;
immutable dataset revision, `dev/` exact file allowlist, official evaluator path/revision ve
code hash **UNRESOLVED**. TurkishMMLU zorunlu registry row'u `BLOCKED` kalır.

#### B.3 Turkish EXAMS

```text
canonical_repository = https://github.com/mhardalov/exams-qa
official_branch_observed = main
turkish_multilingual_paths =
  data/exams/multilingual/train.jsonl.tar.gz
  data/exams/multilingual/dev.jsonl.tar.gz
  data/exams/multilingual/test.jsonl.tar.gz
turkish_crosslingual_paths =
  data/exams/cross-lingual/train_tr.jsonl.tar.gz
  data/exams/cross-lingual/dev_tr.jsonl.tar.gz
  data/exams/cross-lingual/test.jsonl.tar.gz
  data/exams/cross-lingual/with_paragraphs/train_tr_with_para.jsonl.tar.gz
  data/exams/cross-lingual/with_paragraphs/dev_tr_with_para.jsonl.tar.gz
  data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz
official_evaluator_path = scripts/evaluation/evaluate_exams.py
```

Repository README, Turkish multilingual split counts (Train 747 / Dev 240 / Test 977),
cross-lingual `*_tr` naming rule and evaluator pathı public metadata olarak doğrulandı. Exact
Turkish rows later execution'da yalnızca frozen path ve documented language/split rule ile
seçilebilir; response-dependent selection yapılamaz. `data/exams/multilingual/` ve
`data/exams/cross-lingual/` tree'leri görüldü, fakat official GitHub `main` tipinin full
immutable commit SHA'sı ve evaluator file code hash bu metadata pass'inde elde edilemedi.
Hugging Face `mhardalov/exams` conversion history'si canonical maintainer GitHub revision'ının
yerine kullanılmaz.

Sonuç: canonical repository, Turkish path allowlist ve evaluator path **RESOLVED**; full
immutable official repository/evaluator revision ve exact item-file hashes **UNRESOLVED**.
Turkish EXAMS zorunlu registry row'u `BLOCKED` kalır.

#### B.4 CETVEL/TurkBench

```text
decision = excluded_with_reason
reason = bounded pass exact task relevance + official immutable item route + official evaluator
         revision/code hash üçlüsünü deterministically freeze edemedi; response-dependent task
         selection yasaktır.
```

Bu, zorunlu üç benchmark için bir `PASS` replacement değildir. CETVEL/TurkBench comparative
selection bu contract'ta yoktur ve bu exclusion later measurement-design blocker'ını kapatmaz.

#### B.5 Source-model routes

Model weights veya tokenizer snapshot'ları açılmadan, public Hugging Face metadata'dan aşağıdaki
exact repository IDs ve full immutable revisions çözüldü. `README.md` model-card route'ları yalnızca
metadata doğrulama içindir:

| role | repository ID | immutable HF revision | model-card/paper/corpus metadata route | status |
|---|---|---|---|---|
| a priori English-dominant | `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | `https://huggingface.co/allenai/OLMo-2-0425-1B/blob/a1847dff35000b4271fa70afc5db10fd29fedbdf/README.md`; `https://github.com/allenai/OLMo`; `https://github.com/allenai/OLMo-Eval`; `https://arxiv.org/abs/2501.00656` | RESOLVED_METADATA_ONLY |
| secondary English comparator | `tiiuae/falcon-rw-1b` | `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | `https://huggingface.co/tiiuae/falcon-rw-1b/blob/e4b9872bb803165eb22f0a867d4e6a64d34fce19/README.md`; `https://huggingface.co/datasets/tiiuae/falcon-refinedweb`; `https://arxiv.org/abs/2306.01116` | RESOLVED_METADATA_ONLY |
| multilingual/Turkish positive control | `Qwen/Qwen2.5-1.5B` | `8faed761d45a263340a0528343f099c05c9a4323` | `https://huggingface.co/Qwen/Qwen2.5-1.5B/blob/8faed761d45a263340a0528343f099c05c9a4323/README.md`; `https://github.com/QwenLM/Qwen2.5`; `https://qwen.readthedocs.io/`; `https://arxiv.org/abs/2407.10671` | RESOLVED_METADATA_ONLY |

OLMo card metadata explicitly identifies English, OLMo-mix-1124/Dolmino-mix-1124 and the official
OLMo/OLMo-Eval repositories; Falcon card metadata identifies English, RefinedWeb and its paper;
Qwen card metadata identifies the base pretraining stage and multilingual support. None of these
claims is a capability measurement, a Turkish exposure proof, or an authorization to access model
files. Source-model registry rows may use these frozen IDs/revisions during later execution, but
model files, tokenizer files and inference remain forbidden.

### C. Effective route overlay and fail-closed preparation decision

For any later 151q execution, only the following are legal:

1. the canonical URLs and repository IDs recorded above;
2. a full immutable revision/commit or tag whose exact object identity is recorded before the first
   request;
3. the exact benchmark file/path allowlist and evaluator path/revision recorded before retrieval;
4. a hash ledger generated from the retrieved allowlisted files, within the original 151q 32 MiB
   single-file and 128 MiB total-retained-file bounds.

No later execution may resolve a missing revision from `main`, substitute a mirror or third-party
dataset, select a task after seeing a response, or silently broaden a directory allowlist.

The required benchmark item manifests and hashes were intentionally **not** collected in this
repair pass because the current override forbade benchmark item-content collection. The unresolved
official GitHub revision/evaluator identity and incomplete TurBLiMP/TurkishMMLU exact file
allowlists therefore remain preparation blockers. Under the original Section 11 rules, the
mandatory benchmark entities are `BLOCKED`; this addendum does not manufacture `PASS` rows.

The primary current gate remains `blocked_by_measurement_design`. The operational/path bounds gate
remains PASS from prior records, but no 151q execution authorization is requested by this
addendum. Successful future metadata-registry completion alone cannot close benchmark overlap,
713-surface reconciliation, missing pattern/alias inventory or Turkish capability measurement,
and cannot authorize training.

### D. Explicit non-execution record

```text
151q_executed = false
151r_created = false
151s_created = false
HU_accessed = false
SSH_used = false
benchmark_item_content_collected_in_repair_pass = false
benchmark_scoring_or_inference = false
model_or_tokenizer_artifact_access = false
training_or_Slurm = false
```

Bu append-only correction tamamlandıktan sonra 151q hâlâ yürütülmemiş, 151r/151s hâlâ
oluşturulmamış ve global training gate `BLOCKED` durumundadır. Final corrected SHA-256 bu dosyanın
dışındaki documentation index ve living handoff kayıtlarında tutulur; self-referential hash
alanı eklenmemiştir.

---

## APPEND-ONLY SECOND CORRECTION ADDENDUM — FINAL IMMUTABLE BENCHMARK OVERLAY — 2026-08-07

### 1. Preservation, scope and verification identity

Bu ikinci addendum, 151q'nın özgün gövdesini veya ilk addendum'ı yeniden yazmaz. Önceki
kimlikler tarihsel olarak korunur:

```text
original_151q_sha256 = b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c
first_addendum_151q_sha256 = 0acf5251bea811e07b6442681ec02c7bc4fa2ea584a55e8b48cbcb704d4209e3
second_addendum_type = append_only_final_immutable_benchmark_overlay
verification_mode = bounded_public_read_only_metadata_second_pass
verification_date = 2026-08-07 Europe/Berlin
max_public_metadata_requests = 16
max_total_response_bytes = 8388608
benchmark_item_content_downloaded = false
151q_executed = false
151r_created = false
151s_created = false
```

Bu pass'te item dosyalarının gövdeleri, benchmark arşivleri, response payload'ları, model veya
tokenizer artefaktları alınmadı; scoring, inference, HU/SSH, corpus, GPU, Slurm, training,
cleanup veya deletion yapılmadı. Doğrulama resmi GitHub commit/tree/blob metadata ve resmi
repository README route açıklamalarıyla sınırlı tutuldu. Exact item-byte/SHA ledger'ları sonraki
151q execution deliverable'ıdır; bu addendum onları üretmez.

### 2. Effective immutable benchmark overlay

Bu bölüm önceki addendum'daki daha genel veya unresolved benchmark route ifadelerini effective
olarak düzeltir. Aşağıdaki source identity, path ve evaluator değerleri 151q execution başlamadan
önce değiştirilemez.

#### 2.1 TurBLiMP

```text
repository = https://github.com/ezgibasar/TurBLiMP
immutable_commit = 297de13fb7a0ce524fe32e8b175c6b5255d66960
primary_item_root = data/base/
excluded_item_roots = data/experimental/ ; data/human_judgments/
evaluator_path = evaluation.py
evaluator_git_blob_sha1 = c386def30cfdcbab4cd4366ef5805ab6ce4ae26a
overlay_status = VERIFIED_FROZEN
```

Primary item allowlist is exactly the following 16 files under `data/base/`; no directory
expansion, experimental paradigm, or human-judgment file is implicit:

```text
data/base/augmented_anaphor_agreement.csv
data/base/augmented_argument_structure_ditransitive.csv
data/base/augmented_argument_structure_transitive.csv
data/base/augmented_binding.csv
data/base/augmented_determiners.csv
data/base/augmented_ellipsis.csv
data/base/augmented_irregular_forms.csv
data/base/augmented_island_effects.csv
data/base/augmented_nominalization.csv
data/base/augmented_npi_licensing.csv
data/base/augmented_passives.csv
data/base/augmented_quantifiers.csv
data/base/augmented_relative_clauses.csv
data/base/augmented_scrambling.csv
data/base/augmented_subject_verb_agreement.csv
data/base/augmented_suspended_affixation.csv
```

#### 2.2 TurkishMMLU

```text
repository = https://github.com/ArdaYueksel/TurkishMMLU
immutable_commit = 0686a674064a151567ae05757e1f2414ca9d83d5
primary_item_roots = dev/ ; test/
excluded_item_file = turkishmmlu_sub.json
overlay_status = VERIFIED_FROZEN
```

The primary item allowlist is the nine subject files in each of `dev/` and `test/`:

```text
dev/TurkishMMLU_Biology.json
dev/TurkishMMLU_Chemistry.json
dev/TurkishMMLU_Geography.json
dev/TurkishMMLU_History.json
dev/TurkishMMLU_Mathematics.json
dev/TurkishMMLU_Philosophy.json
dev/TurkishMMLU_Physics.json
dev/TurkishMMLU_Religion and Ethics.json
dev/TurkishMMLU_Turkish Language and Literature.json
test/TurkishMMLU_Biology.json
test/TurkishMMLU_Chemistry.json
test/TurkishMMLU_Geography.json
test/TurkishMMLU_History.json
test/TurkishMMLU_Mathematics.json
test/TurkishMMLU_Philosophy.json
test/TurkishMMLU_Physics.json
test/TurkishMMLU_Religion and Ethics.json
test/TurkishMMLU_Turkish Language and Literature.json
```

The standard non-CoT evaluator overlay is the author-contributed upstream lm-evaluation-harness
task, not a maintainer-repository evaluator:

```text
evaluator_repository = https://github.com/EleutherAI/lm-evaluation-harness
evaluator_immutable_revision = f4d4b3de3ee6741a7151a9fe74945ee515262f4c
evaluator_path = lm_eval/tasks/turkishmmlu/config/
evaluator_subtree_git_object_sha1 = 35814d4b510da85f1bbd9f3d7293ab42bac200c8
evaluator_provenance = TurkishMMLU author ArdaYueksel contribution/maintenance
included_evaluator_variant = config/ (standard non-CoT)
excluded_evaluator_variant = config_cot/
```

The provenance caveat remains mandatory: this is an upstream harness task contributed by the
TurkishMMLU author, not an evaluator file maintained in the `TurkishMMLU` repository itself.

#### 2.3 Turkish EXAMS

```text
repository = https://github.com/mhardalov/exams-qa
immutable_commit = f859e665de6c370f6214ca5f36a34ace36ada6cb
evaluator_path = scripts/evaluation/evaluate_exams.py
evaluator_git_blob_sha1 = ef242a76cd076d7144f7ed36eadc3d9da6ca7a69
overlay_status = VERIFIED_FROZEN
```

The effective Turkish source-path allowlist is:

```text
data/exams/cross-lingual/train_tr.jsonl.tar.gz
data/exams/cross-lingual/dev_tr.jsonl.tar.gz
data/exams/cross-lingual/test.jsonl.tar.gz
data/exams/cross-lingual/with_paragraphs/train_tr_with_para.jsonl.tar.gz
data/exams/cross-lingual/with_paragraphs/dev_tr_with_para.jsonl.tar.gz
data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz
```

`data/exams/cross-lingual/test_tr.jsonl.tar.gz` is not a valid source path. Any such path in an
earlier draft/addendum is explicitly overridden and must never be requested. The cross-lingual
test artifact is the shared `test.jsonl.tar.gz`; Turkish test membership is selected later only
by the repository's documented language/item rule, never by inventing a Turkish-specific test
filename. The `with_paragraphs` test artifact is likewise the shared
`test_with_para.jsonl.tar.gz` path above.

The multilingual train/dev/test archives remain contextual repository artifacts and are not
silently substituted for the frozen Turkish cross-lingual allowlist. Exact item IDs, serialized
bytes and hashes remain execution outputs.

### 3. Preserved source-model and conditional-benchmark decisions

The first addendum's metadata-only source-model revisions remain effective and are not reopened:

```text
OLMo = allenai/OLMo-2-0425-1B @ a1847dff35000b4271fa70afc5db10fd29fedbdf
Falcon = tiiuae/falcon-rw-1b @ e4b9872bb803165eb22f0a867d4e6a64d34fce19
Qwen = Qwen/Qwen2.5-1.5B @ 8faed761d45a263340a0528343f099c05c9a4323
```

CETVEL and TurkBench remain `excluded_with_reason`; no exact task relevance, immutable item
route, item manifest/hash and evaluator revision/code hash tuple was frozen for either. This does
not replace or weaken the mandatory TurBLiMP/TurkishMMLU/EXAMS overlay.

### 4. Re-freezed status and execution boundary

The second correction closes the prior *preparation* blocker for immutable benchmark revisions,
file allowlists and evaluator identities. It does not collect item hashes and does not execute
the contract:

```text
second_correction_status = VERIFIED_FROZEN
151q_status = UNEXECUTED — EXECUTION_READY
151r_status = RESERVED_UNCREATED
151s_status = RESERVED_UNCREATED
benchmark_item_manifest_and_sha_status = RESERVED_FOR_151q_EXECUTION
primary_global_gate = blocked_by_measurement_design
training_gate = BLOCKED
```

A later 151q execution may read only the three frozen benchmark source routes, the frozen model
metadata routes, and the exact allowlists above, then write new bounded manifests, ledgers and
reports only under the already specified new scratch root. It must fail closed on any revision,
path, evaluator blob, item ordering, hash, bound or manifest mismatch. It may not infer or score
models, download weights/tokenizers, materialize a corpus, access HU, run GPU/Slurm/training,
rewrite any prior record, create Documents 151k/151l, or create Documents 152--154.

Successful metadata-registry execution still cannot close `blocked_by_measurement_design` as a
whole: benchmark overlap/contamination definitions, the 713/829 scope already identified by
151p, missing pattern/alias inventory and Turkish capability measurement remain outside this
contract. It cannot authorize training. The next and only authorization requested after this
freeze is one separately explicit bounded execution of corrected 151q, including creation of
151r and 151s; that execution is not authorized or performed in this turn.

---

## APPEND-ONLY THIRD CORRECTION ADDENDUM — EXECUTION-LOCATION AUTHORIZATION CLARIFICATION — 2026-08-07

This short operational addendum resolves an authorization contradiction only. It does not execute
151q, collect benchmark/model files, or create 151r/151s. All earlier document text remains
preserved, with this section the effective clarification for a later separately authorized wave.

```text
original_151q_sha256 = b55499242100263e0d9adbe946679b6175268012d1c3e897298413a2af1ef60c
first_addendum_151q_sha256 = 0acf5251bea811e07b6442681ec02c7bc4fa2ea584a55e8b48cbcb704d4209e3
second_addendum_151q_sha256 = c217f4d8395a8e3b657f96fd46f3e6443a11fcde6bbfbd6f7a8414933ccf89ee
151q_status = UNEXECUTED — EXECUTION_READY
151r_status = RESERVED_UNCREATED
151s_status = RESERVED_UNCREATED
```

The earlier blanket `no HU/SSH` statements apply to the preparation and public-metadata
correction passes only. They do not prohibit a later execution that receives one new explicit
authorization. That future authorization may use the documented `ssh-client` route to HU and
perform the mandatory storage/path/inode preflight. It may create and write only new files under:

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1
```

That future wave may retrieve only the already frozen public benchmark/model metadata and the
allowlisted benchmark item files, within 151q's existing request/byte/file/time limits, and must
perform the mandatory post-run storage audit. HU home remains read-only for this work. The existing
audit, repair and Phase-1 evidence roots remain immutable/read-only; no existing sample, report,
manifest, cache, ledger or evidence file may be overwritten.

The following remain unconditionally forbidden, including any future 151q execution: model or
tokenizer weights/snapshots, model inference, **all benchmark scoring** (there is no scoring
exception inside the registry contract), corpus materialization, Slurm/GPU work, training,
cleanup/deletion, writes to HU home or prior roots, Documents 151k/151l and Documents 152--154.

Only a separate explicit authorization containing bounded HU/SSH access, the frozen scratch root,
the mandatory preflight/post-run audit, and public HTTP retrieval within the existing 151q limits
may start the registry wave. Such authorization must also authorize creation of 151r/151s. This
clarification does not authorize or perform that wave and does not change the
`blocked_by_measurement_design` or `BLOCKED` training gate.
