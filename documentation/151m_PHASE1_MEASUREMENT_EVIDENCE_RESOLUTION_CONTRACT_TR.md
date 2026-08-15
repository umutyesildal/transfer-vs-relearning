# 151m — Phase-1 Measurement Evidence-Resolution Contract

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Durum:** **UNEXECUTED — bu turda yalnızca sözleşme oluşturuldu**  
**Tür:** Bounded, source-read-only, non-destructive Phase-1 evidence-resolution contract  
**Önceki belge:** Document 151j, `SUPERSEDED_UNEXECUTED_REQUIREMENTS_DRAFT`  
**Current gate:** `blocked_by_measurement_design`  
**Training gate:** `BLOCKED`

## 1. Amaç ve Phase-1 sınırı

Bu sözleşme, geniş ve içsel olarak dairesel hale gelen 151j gereksinimlerini daha küçük bir
evidence-resolution fazına ayırır. Phase 1 yalnızca daha sonra bir baseline-measurement contract'ı
hazırlamak için gerekli metadata, immutable set membership ve tanım kanıtını çözer. Model inference,
GPU, benchmark scoring, BPC/PPL, training veya gelecekteki M2-A/M2-B modelleri bu fazın konusu
değildir.

Phase 1'in daha sonraki yetkili execution'ı şu beş sınırlı work package'ı kapsayabilir:

1. benchmark registry metadata ve base-model uyumluluğu;
2. `713/829` exact-set reconciliation;
3. pattern/alias/template inventory provenance;
4. contamination tier tanımlarının ve ölçüm şemasının freeze edilmesi;
5. OLMo, Falcon ve Qwen source-model provenance metadata'sı.

Her sonuç `positive`, `negative`, `conditional`, `inconclusive` veya `blocked` olarak dürüstçe
raporlanabilir. Hiçbir work package olumlu bir sonuç üretmeye zorlanamaz; başarısız veya
çözülemeyen kanıt da aynı ayrıntıyla kaydedilir.

Bu belge oluşturulduğu turda çalıştırılmayacaktır. Bu turda HU, SSH, web, API, benchmark, model,
dataset, synthetic inventory veya evaluation erişimi yapılmayacak; yalnızca yerel dosyalar ve
dokümantasyon değiştirilecektir.

## 2. Açık olmayan kapsam ve yasaklar

Phase-1 execution'ı için ayrıca açık kullanıcı yetkisi olmadan aşağıdakiler yasaktır:

- HU/SSH veya herhangi bir remote command;
- web/network/API isteği veya public terms kabulü;
- model weight, tokenizer weight, checkpoint, corpus veya full benchmark dataset indirme;
- model inference, tokenizer inference, BPC/bits-per-byte, PPL veya fertility computation;
- TurBLiMP, TurkishMMLU, EXAMS, CETVEL/TurkBench scoring veya factual evaluation;
- synthetic inventory'nin full materialization'ı veya full-corpus contamination scan;
- GPU/Slurm, training, fine-tuning, checkpoint seçimi veya M2-A/M2-B construction;
- mevcut audit/repair root, manifest, report, cache veya evidence dosyalarının overwrite edilmesi;
- cleanup, deletion, migration veya artifact mutation;
- Documents 151k/151l, 152–154 veya başka bir execution/result document'ının oluşturulması.

Phase 1 metadata/item-file erişimi için bir sonraki kullanıcı yetkisi verilse bile bu liste, yalnız
bu sözleşmede açıkça izin verilen bounded public metadata ve küçük item files ile sınırlıdır.

## 3. Immutable roots ve future scratch root

Mevcut bounded-audit evidence root immutable/read-only'dur:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
```

Mevcut vngrs repair root ve bütün 151a–151i evidence'ı da overwrite edilemez:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1
```

Phase-1 için önerilen yeni scratch root şudur; bu sözleşme hazırlanırken root oluşturulmayacak:

```text
/vol/tmp2/yesildau/luna_phase1_measurement_evidence_resolution_v1
```

Gelecekteki execution yalnız bu yeni root altında yeni dosyalar yazabilir. Önerilen alt dizinler:

```text
contracts/
registries/
inventories/
manifests/
overlap/
reports/
logs/
tmp/
```

Bu task'ta hiçbir future root veya alt dizin oluşturulmadı. Repository-local path'ler scratch'e
çözülmedikçe output destination olarak kullanılamaz. HU home'a büyük veya yüksek hacimli çıktı
yazılamaz.

## 4. Önceden dondurulmuş source set

Execution başlamadan önce aşağıdaki source sınıfları ve sabit sıra kullanılacaktır. Exact revision
ve hash bulunamıyorsa tahmin yapılmaz; ilgili kayıt `NR` ve gate `blocked` olur.

| Sıra | Source class | Allowed use | Explicit exclusion |
|---:|---|---|---|
| 1 | TurBLiMP public primary metadata/release | registry, license, split/item metadata, optional small item file | scoring, inference, guessed revision |
| 2 | TurkishMMLU public primary metadata/release | registry, license, split/item metadata, optional small item file | scoring, model evaluation |
| 3 | Turkish EXAMS public primary metadata/release | Turkish subset metadata, license, item metadata | scoring, broad benchmark download |
| 4 | CETVEL/TurkBench only demonstrably relevant task metadata | exact task/revision/scoring/relevance check | full benchmark or irrelevant task acquisition |
| 5 | Frozen Relation V2 local/HU source files and release metadata | deterministic 713/829 extraction and provenance check | new corpus or synthetic population generation |
| 6 | Existing local/HU pattern/alias/template source files | provenance/reproducibility check | full fuzzy contamination scan |
| 7 | Primary metadata for `allenai/OLMo-2-0425-1B`, `tiiuae/falcon-rw-1b`, `Qwen/Qwen2.5-1.5B` | model card/revision/license/corpus-language metadata | weights, tokenizer files, inference |

The source URL, repository, release identifier and expected access type must be placed in the
preflight manifest before the first future request. Canonical public metadata source and any
predeclared official mirror are allowed; response-dependent source substitution is not allowed.
An inaccessible or changed source is recorded as blocked rather than replaced opportunistically.

## 5. Exact operational bounds

The following limits are frozen before any future network or source-read-only execution:

```text
max_total_http_requests = 96
max_total_retries = 16
max_total_response_bytes = 268435456          # 256 MiB
max_single_saved_metadata_or_item_file = 33554432  # 32 MiB
max_total_new_saved_bytes = 134217728         # 128 MiB
max_wall_clock_seconds = 1800                 # 30 minutes
max_new_regular_files = 256
max_new_storage_bytes_in_phase1_root = 536870912  # 512 MiB, including logs/tmp
```

`max_total_response_bytes` counts every HTTP response body, including failed/retry responses; it
is not inferred from saved file size. Redirects and retry responses consume request and byte
bounds. Metadata or item files larger than 32 MiB are not saved. No archive may be unpacked into
the Phase-1 root. Reaching any bound before all mandatory evidence is resolved fails closed as
`blocked_by_operational_access`.

The contract does not permit a failed page/file replacement, response-dependent benchmark
selection, silent retry loop, or continuation in a new root after a bound is hit. A future
execution may stop earlier and report `inconclusive` or a work-package-specific blocker.

## 6. Deterministic execution protocol

Before the first request or source-file read, future execution must write a preflight manifest to
the new Phase-1 root containing:

```text
contract_id = 151m
contract_sha256
allowed_source_order
allowed_source_urls_or_local_paths
known_revision_or_NR
sampling_seed = 42
ordering_rule = lexicographic(canonical_source_id, split, path, item_id)
runtime_and_code_revision
planned_request_count
all_bound_values
existing_root_inventory_and_sha
```

The deterministic procedure is:

1. validate all source paths, resolved destinations and immutable existing-root inventories;
2. enumerate the fixed source list in the order in §4;
3. process each source's predeclared canonical metadata/release URL or local path once;
4. use stable lexicographic ordering for registry rows, item IDs, file paths and set membership;
5. use seed `42` only where a deterministic ordering or bounded sample is unavoidable;
6. never choose a source, item, page, split or fallback based on a favorable response;
7. preserve every failed request/error/timeout and do not silently replace it;
8. stop and fail closed on any contract bound, path mismatch, duplicate mandatory ID or schema
   violation;
9. write only new evidence and reports under the new Phase-1 root.

No model or benchmark scoring process may be invoked. This protocol resolves evidence identity and
definitions only.

## 7. Common evidence schema and integrity ledger

Every registry row, inventory artifact and report must include or reference:

```text
evidence_id
work_package
source_id
source_url_or_local_path
immutable_revision_or_release
retrieved_at_utc
local_relative_path
byte_count
sha256
status = pass | conditional | blocked | NR
runtime_and_code_revision
code_sha256
notes_and_limitations
```

The execution root must contain a machine-readable input/output hash ledger with:

```text
artifact_id
artifact_type
source_revision
relative_path
byte_count
sha256
created_at_utc
status
```

Hashes are computed after writing and again during post-run audit. A missing hash, duplicate
artifact ID, non-deterministic ordering or mismatch between manifest and file fails closed. `NR`
means not reported or not resolvable; it must not be replaced by an estimate.

Raw benchmark PII, raw personal contact information and full source documents are not copied into
documentation. If a bounded source excerpt is indispensable for a later adjudication, it remains
under the future scratch root, is minimized, and is referenced by ID/hash in reports.

## 8. WP-A — Benchmark registry metadata

### 8.1 Registry scope

Phase 1 may resolve metadata for TurBLiMP, TurkishMMLU, Turkish EXAMS and only demonstrably relevant
CETVEL/TurkBench tasks. It may save a small public item file only when the license/access evidence
allows it and the file is within the frozen 32 MiB per-file bound. It must not run scoring,
tokenization inference or model evaluation.

Every candidate can end as `included`, `excluded_not_base_compatible`, `conditional`, `unresolved`
or `blocked`. “Turkish benchmark” naming alone is not suitability evidence.

### 8.2 Required fields

The benchmark registry must contain:

```text
benchmark_id
canonical_name
task_definition
subset_or_language
role_and_scientific_purpose
source_repository_or_url
immutable_release_or_revision
split_names
item_count_per_split
ordered_item_id_manifest_if_obtained
item_file_path_or_source_url
item_file_sha256_if_obtained
license_and_access_evidence
evaluator_source_revision_if_available
evaluator_code_sha256_if_available
normalization_and_scoring_rule
base_model_compatibility
chance_baseline_if_applicable
floor_ceiling_evidence_or_NR
benchmark_corpus_overlap_procedure
retrieved_at_utc
status
limitations
```

TurBLiMP is the preferred independent linguistic diagnostic candidate only after exact release,
evaluator, overlap and floor/ceiling evidence. TurkishMMLU and EXAMS are broad knowledge,
school/reasoning or cultural diagnostics, not pure language-adaptation proof. CETVEL/TurkBench
are included only for a demonstrably relevant, exact task; irrelevant or instruction-only tasks
are excluded without being called scientific failures.

No item set is called clean, frozen or evaluation-ready without an exact item manifest, hash,
license/access evidence and a separate overlap procedure. No scoring result is produced in Phase
1.

## 9. WP-B — Exact `713/829` reconciliation

### 9.1 Counting units

The following units are frozen and must not be mixed:

```text
subject_count = 5,000 unique subject_id
semantic_fact_id = subject_id | relation
semantic_fact_count = 25,000 unique semantic fact IDs
bilingual_resolved_row = semantic_fact_id | language
bilingual_resolved_row_count = 50,000 when en/tr rows are both present
relations = profession, birthplace, residence, university, employer
```

Semantic facts, canonical EN/TR surfaces, union surfaces, aliases, templates, patterns and
training sentences are separate sets. `50,000` is language-expanded resolved-row grain, not a
semantic-fact count.

### 9.2 Procedure and outputs

The future execution must use only the frozen Relation V2 release commit/manifest and existing
local/HU source files. It must record:

```text
relation_v2_release_commit
input_paths
input_sha256
schema_revision
normalization_version
declared_713_definition_and_source
deterministic_sorted_713_membership_sha256
deterministic_sorted_829_membership_sha256
```

It must produce, when reproducible, exact membership files and hashes for 713 and 829, their
intersection, `713-only`, `829-only`, exact counts, and normalization differences. The report
must distinguish language expansion, normalization, alias inclusion and genuine canonical-object
changes. It may not alter the fact population or generate replacement facts to recover 713.

If the declared 713 set, its source or its exact definition cannot be reconstructed from frozen
code/data, the result is `blocked_by_synthetic_inventory_provenance`; 829 cannot silently replace
713. If the two sets differ, the difference remains a reported evidence question rather than a
forced narrative reconciliation.

## 10. WP-C — Pattern, alias and template provenance

The future execution may inspect existing frozen provenance only for these categories:

```text
subjects
semantic_facts
canonical_en_surfaces
canonical_tr_surfaces
aliases_by_language
exact_training_sentences
patterns_or_templates
normalized_matching_surfaces
```

Each available record must preserve, as applicable:

```text
fact_id
subject_id
relation
language
category
original_surface
normalized_surface
source_file
source_row_or_template_id
release_commit
deterministic_record_id
```

Each category receives its own normalization version, ordered membership manifest and SHA-256.
Exact sentence, subject/object, alias and fuzzy normalization are not interchangeable. The
declared `65,717` pattern inventory is a reproduction target: it is either reproduced with exact
evidence, shown to differ with set/hash evidence, or classified as unreproducible.

Fuzzy rules may be specified as a future deterministic procedure, but Phase 1 does not treat fuzzy
matches as contamination and does not use them to optimize an inventory count. Missing aliases,
templates or pattern evidence yields `blocked_by_contamination_definition`.

## 11. WP-D — Contamination definition freeze

Phase 1 freezes definitions and schemas; it does not scan a full corpus. A later authorized,
bounded execution may apply these definitions only to explicitly authorized existing samples.

### 11.1 Required tiers

```text
Tier 0 = exact normalized declared training-sentence match
Tier 1 = exact subject + canonical object in one document
Tier 2 = exact subject + alias/object surface in one document
Tier 3 = template/full-fact-pattern match
Tier 4 = fuzzy candidate requiring deterministic adjudication
Object-only = diagnostic only
Subject-only = diagnostic only
```

For each tier, freeze Unicode/case/diacritic normalization, contamination unit, boundary rule,
language/mixed-language policy, alias/template policy, false-positive handling, common-object
handling, output aggregation, adjudication rule and pass/conditional/blocked rule.

The required future hit/candidate schema is:

```text
contamination_record_id
tier
source_id
source_revision
source_row_or_document_id
inventory_record_id
inventory_membership_sha256
language
normalization_version
match_type
matched_span_or_bounded_hash
fuzzy_parameters_if_any
adjudication_status
rule_revision
retrieved_at_utc
```

Benchmark overlap remains a separate WP-A registry result. Common object collisions are not
factual contamination without subject/fact context. No zero-contamination claim is permitted
when the required inventory or benchmark registry is absent. Raw PII is never written to the
documentation; bounded adjudication snippets, if later needed, remain scratch-only and hashed.

## 12. WP-E — Source-model provenance metadata

Phase 1 may resolve metadata only for these fixed roles and model IDs:

| Model ID | Frozen role |
|---|---|
| `allenai/OLMo-2-0425-1B` | a priori English-dominant candidate |
| `tiiuae/falcon-rw-1b` | secondary comparator candidate |
| `Qwen/Qwen2.5-1.5B` | multilingual/Turkish positive control |

The registry must record:

```text
model_id
immutable_revision
base_or_instruct
training_stage
architecture_and_parameter_count
tokenizer_id_and_revision_if_metadata_only
model_card_language_claims
training_corpus_names_and_revisions
known_language_mixture
explicit_turkish_evidence_or_NR
license_and_access_terms
primary_source_url
retrieved_at_utc
runtime_compatibility_metadata_if_reported
planned_role
provenance_label
limitations
```

Allowed conservative labels are:

```text
documented_multilingual_with_Turkish
documented_English_dominant_Turkish_fraction_unreported
Turkish_exposure_not_resolvable
not_suitable_training_stage
```

No weight or tokenizer package is downloaded. No model is called `Turkish unseen` without primary
source evidence. Missing Turkish documentation is not proof of zero exposure. Unresolved revision,
stage, license or Turkish evidence yields `blocked_by_source_model_provenance` for dependent claims.

## 13. Explicitly outside Phase 1

The following are not deliverables, diagnostics or pass criteria for this contract:

- BPC/bits-per-byte execution or any PPL calculation;
- Turkish or English language-model inference;
- TurBLiMP, TurkishMMLU, EXAMS, CETVEL or TurkBench scoring;
- model/tokenizer inference requiring weight access;
- M0/M1 capability comparison;
- M2-A/M2-B construction, training, evaluation or checkpoint selection;
- final model/corpus choice or dose selection;
- full benchmark, corpus or synthetic-inventory materialization;
- contamination scanning beyond a later separately bounded authorized sample;
- any claim of training readiness.

Phase 1 can only prepare evidence needed for a later baseline-measurement contract.

## 14. Failure-closed rules and decision vocabulary

### 14.1 Fail-closed triggers

The future execution must stop and record a failure rather than continue if any of the following
occurs:

- any request, retry, response-byte, single-file, total-storage, file-count or wall-clock bound
  is reached;
- a path resolves outside the declared new Phase-1 root or an immutable root changes;
- a mandatory manifest field, input hash, output hash or retrieval timestamp is missing;
- duplicate benchmark item ID, duplicate inventory membership ID or ambiguous source identity appears;
- an access/license term is not accepted or a source requires an unapproved credential;
- a model weight, tokenizer weight, full corpus, full benchmark archive or inference process is
  requested;
- a source revision cannot be made immutable or a required set cannot be reproduced;
- raw PII is emitted into a report or documentation.

Operational bound/path/storage violations map to `blocked_by_operational_access`. Missing
benchmark identity maps to `blocked_by_benchmark_registry`; unreproducible 713 maps to
`blocked_by_synthetic_inventory_provenance`; missing pattern/alias/template or unresolved tier
definition maps to `blocked_by_contamination_definition`; unresolved model metadata maps to
`blocked_by_source_model_provenance`.

### 14.2 Frozen decision vocabulary

At minimum the Phase-1 result must use:

```text
ready_to_freeze_baseline_measurement_contract
blocked_by_benchmark_registry
blocked_by_synthetic_inventory_provenance
blocked_by_contamination_definition
blocked_by_source_model_provenance
blocked_by_operational_access
```

`ready_to_freeze_baseline_measurement_contract` means only that a later BPC/benchmark/capability
contract may be drafted. It never means `ready_to_train`. If multiple blockers exist, all are
reported and the primary blocker is identified without hiding secondary unresolved evidence.

Positive, negative and inconclusive sub-results remain reportable even when the overall decision is
blocked. No post-outcome threshold or source is selected to obtain a favorable decision.

## 15. Preflight, post-run audit and deliverables

Before a future execution, the operator must record a read-only preflight for source paths,
existing-root inventory/hash, capacity/inodes, resolved new root, exact bounds, expected output
files and cache/log/tmp destinations. The preflight must confirm that the two existing roots are
unchanged and that the new root did not previously contain outputs from this contract.

After a future execution, the operator must record:

- final status and all sub-work-package decisions;
- request/retry/byte/time/file/storage ledger;
- every input/output path, byte count and SHA-256;
- benchmark registry and optional item-file manifest;
- 713/829 membership/count/hash reconciliation;
- pattern/alias/template provenance report;
- contamination-definition and schema report, without full-corpus claims;
- source-model provenance registry;
- failures, missing fields, blocked sources and inconclusive results;
- post-run capacity/inode/path audit and proof that immutable roots were unchanged.

The result must be written as a new report only. No existing 151a–151i file is modified.

## 16. Reserved result and gate documents

Reserve but do not create:

```text
Document 151n — Phase-1 measurement evidence-resolution execution result
Document 151o — Phase-1 post-execution decision gate
```

Any future authorization for 151m must explicitly authorize creation of 151n and 151o so the
execution and its gate are documented atomically. That authorization does not authorize 151k,
151l, 152–154, training or model inference.

## 17. Authorization boundary and current status

This is an unexecuted contract. Its creation does not create the Phase-1 root, access any source,
or open any gate.

The only next authorization request is:

```text
User explicitly authorizes one bounded, source-read-only, non-destructive execution of the frozen
Document 151m Phase-1 measurement evidence-resolution contract, including creation of Documents
151n and 151o, but excluding model inference, GPU/Slurm, training, full-corpus operations,
cleanup, and Documents 151k/151l or 152–154.
```

**Current status:** `UNEXECUTED`  
**Current measurement-design gate:** `blocked_by_measurement_design`  
**Current training authorization:** `BLOCKED`
