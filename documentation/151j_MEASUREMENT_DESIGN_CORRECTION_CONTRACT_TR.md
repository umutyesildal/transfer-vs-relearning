# 151j — Measurement-Design Correction Contract

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Durum:** **UNEXECUTED — yalnızca yerel sözleşme; bu belge çalıştırılmadı**  
**Tür:** Bounded measurement-design correction contract  
**Üst authority:** Documents 151f, 151g, 151h ve 151i; mevcut proje talimatı `AGENTS.md`

## 1. Sözleşmenin amacı ve değişmez sınırlar

Bu belge, `blocked_by_measurement_design` gate'ini denetimli ve sonuçtan bağımsız biçimde
incelemek için gerekli minimum düzeltme paketini dondurur. Bu bir execution result, benchmark
sonucu, capability sonucu, corpus seçimi veya training contract değildir. Bu belge oluşturulduğu
turda çalıştırılmayacaktır; ağ, HU, SSH, benchmark, evaluator, model veya veri erişimi yapılmadan
yalnızca dokümantasyon olarak saklanır.

Bu sözleşme yürürlüğe girmeden ve kullanıcı tek seferlik açık yetki vermeden aşağıdakiler
yapılamaz:

- HU/SSH, API veya başka network erişimi;
- benchmark veya capability evaluator çalıştırma;
- model/model-weight, corpus veya benchmark indirme;
- full corpus materialization, synthetic inventory üretimi veya contamination taraması;
- Slurm/GPU, training, fine-tuning veya evaluation sweep;
- mevcut artifact, manifest, cache, report veya evidence dosyasını değiştirme, silme veya taşıma;
- Documents 151k/151l veya 152–154 oluşturma;
- `ready_to_train` veya eşdeğeri bir karar verme.

Sözleşme sonucu pozitif, negatif veya inconclusive olabilir. Üç sonuç da aynı raporlama ağırlığına
sahiptir; eşik, benchmark, inventory tanımı, source model veya ölçüm yolu sonuç görüldükten sonra
değiştirilemez. “Başarı” yalnız bu sözleşmede belirtilen alt evidence gate'ini kapatabilir; tek
başına training yetkisi vermez.

## 2. Mevcut gate ve storage durumu

Execution başlamadan önce bu state değişmeden doğrulanır:

| Alan | Frozen mevcut durum |
|---|---|
| vngrs operational/sample-manifest gate | `PASS / closed` — Document 151h/151i kapsamıyla sınırlı |
| CulturaX | `excluded_access_blocked`; CulturaX–vngrs comparative selection unavailable |
| measurement-design gate | `blocked_by_measurement_design` |
| global training gate | `BLOCKED` |
| Documents 151d/151e | historical preliminary/provisional evidence, append-only |
| Documents 151f/151i | correction/repair evidence and current gate records |
| Documents 152–154 | unauthorized and uncreated |

Mevcut evidence root immutable/read-only kabul edilir:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
```

Bu sözleşmenin ileride yetkilendirilecek execution'ı için yeni, açık measurement root:

```text
/vol/tmp2/yesildau/luna_measurement_design_correction_v1
```

Bu root bu sözleşme hazırlanırken oluşturulmayacak; oluşturulması ve kullanılması ayrı execution
yetkisinin parçasıdır. Mevcut evidence root, 151a–151i dosyaları ve yerel kronolojik raporlar
üzerine yazılamaz. Yeni root altında yalnız yeni contract'a ait registries, inventories,
manifests, overlap ledgers, capability reports, logs ve tmp çıktıları yazılabilir.

## 3. Ortak kanıt ve kayıt şeması

Her yeni kanıt dosyası ve her alt-work-package raporu en az şu ortak alanları taşır:

```text
evidence_id
work_package
source_id_or_benchmark_id
immutable_revision_or_release
retrieved_at_utc
local_relative_path
byte_count
sha256
status = pass | conditional | blocked | NR
method_or_evaluator_revision
code_sha256
notes_and_limitations
```

`NR` ölçülmemiş veya kaynakta raporlanmamış alan için kullanılır; bilinmeyen değeri tahminle
doldurmaz. `blocked` ile `NR` ayrılır: NR alanı açıkça raporlanabilir bir eksikliktir, zorunlu
bir gate alanının eksik olması ise ilgili gate'i blocked yapar.

Her sonuç için ayrıca şunlar kaydedilir:

- kullanılan input dosyalarının immutable revision/path/byte/SHA kayıtları;
- execution code ve runtime/version bilgisi;
- UTC başlangıç/bitiş zamanları;
- kullanılan seed, item/record ID listeleri ve deterministic ordering;
- missing/error/timeout kayıtları;
- olumlu, olumsuz ve inconclusive sonuçların ayrı sayıları;
- kararın hangi pre-outcome kuralına dayandığı.

Raw benchmark PII, raw kişisel iletişim veya gereksiz tam metin dokümanları dokümantasyona
kopyalanmaz. Gerekli bounded scratch örnekleri yalnız yeni root'ta tutulur ve hash/ID ile
referanslanır.

## 4. WP-A — Benchmark registry correction

### 4.1 Adaylar ve önceden dondurulmuş roller

Aşağıdaki adaylar uygun kabul edilmez; yalnız audit listesinde tutulur:

- **TurBLiMP:** exact provenance/evaluator koşulları geçerse bağımsız linguistic diagnostic için
  preferred candidate;
- **TurkishMMLU:** broad Turkish knowledge/reasoning/cultural capability; saf language-adaptation
  ölçüsü değildir;
- **Turkish EXAMS:** Turkish school knowledge/reasoning capability; saf language-adaptation ölçüsü
  değildir;
- **CETVEL** ve/veya ilgili **TurkBench** alt kümeleri: yalnız exact task/revision/scoring ve
  base-compatible relevance çözülürse auxiliary veya grammar/MCQ diagnostic.

Generation-only, instruction/chat-template, judge-based ve task-alignment bölümleri base causal
LM manipulation-check ana gate'i olamaz. Adayın “Turkish benchmark” olarak adlandırılması tek
başına kabul gerekçesi değildir.

### 4.2 Zorunlu benchmark registry alanları

Her candidate/released benchmark için tek satırda veya immutable registry record'ında şu alanlar
zorunludur:

```text
benchmark_id
canonical_name
task_definition
subset_or_language
role_and_purpose
immutable_release_or_revision
split_names
item_count_per_split
ordered_item_id_manifest
item_file_path_or_source_url
item_file_sha256
license_and_access_terms
evaluator_revision
evaluator_code_sha256
prompt_template_or_cloze_context
answer_choice_order_rule
normalization_and_scoring_rule
chance_baseline
floor_and_ceiling_evidence
training-corpus-overlap_result_and_method
factual-inventory-overlap_result_and_method
retrieved_at_utc
limitations
status
```

Revision, item count, hash, license veya evaluator ayrıntısı birincil kaynakta/immutable release'te
yoksa uydurulmaz; alan `NR` olarak yazılır ve gerekli registry gate'i `blocked` kalır. Item listesi,
prompt/choice ordering, diacritics, whitespace ve answer boundary sonuçtan önce dondurulur.

### 4.3 Benchmark kararları

Registry tamamlanmadan benchmark skorları temiz veya capability proof olarak raporlanamaz.
Overlap'in bilinmemesi, license'ın bilinmemesi, evaluator'ın yeniden üretilememesi veya floor /
ceiling'in ölçülmemesi `blocked_by_benchmark_registry` üretir. Benchmark uygun değilse “başarısız
benchmark” değil, `excluded_not_base_compatible` olarak ayrı raporlanır.

## 5. WP-B — 713/829 synthetic inventory reconciliation

### 5.1 Dondurulmuş counting units

İki dilde genişleyen satırlar tek semantic fact'i iki kez saymayacak şekilde grain ayrımı korunur:

| Unit | Exact definition | Expected/reference count |
|---|---|---:|
| subject | unique `subject_id` | 5,000 |
| semantic fact | unique `fact_id = subject_id\|relation` | 25,000 |
| bilingual resolved row | unique `semantic_fact_id\|language` | 50,000 |
| canonical object surface | unique canonical object surface under frozen normalization | 713 and/or 829 claim to reconcile |
| language-specific answer string | one language-specific answer surface per resolved row | not semantic fact count |
| alias/template/training sentence | auxiliary surface/realization | not semantic fact count |

Relations are exactly `profession`, `birthplace`, `residence`, `university`, `employer`. Canonical
profile identity is valid only if it contains 5,000 subjects and 25,000 unique semantic facts.
50,000, when reproduced, is language-expanded resolved rows, not 50,000 semantic facts.

### 5.2 Exact reconciliation procedure

Execution, if authorized, must use a frozen Relation V2 release commit/manifest and must record:

```text
source_file
release_commit
input_file_sha256
record_schema_revision
normalization_version
deterministic_sorted_membership_sha256
record_count_by_unit
```

The procedure must identify the exact declared source and set definition for `713`, reconstruct
that set only from frozen code/data, deterministically sort membership, and hash it. It must then
reproduce the `829` profile-derived union and hash it. The report must include:

- exact set sizes and hashes for 713 and 829;
- intersection, 713-only and 829-only membership IDs;
- normalization differences;
- language expansion effects;
- aliases/templates and genuine canonical-object changes;
- whether either set is derived from a different release or counting grain.

No narrative explanation is allowed without exact set membership/hash evidence. If the 713 set
cannot be reconstructed from immutable source/code, status is
`blocked_by_synthetic_inventory_provenance`; 829 cannot silently replace 713 and the discrepancy
remains unresolved.

## 6. WP-C — Pattern, alias and fuzzy inventory correction

Required immutable inputs/outputs are separately recorded for:

```text
subjects
semantic facts
canonical English surfaces
canonical Turkish surfaces
aliases
exact training sentences
patterns/templates
normalized surfaces
fuzzy candidate pairs
```

Every inventory record must contain:

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

Each category receives its own normalization version and membership SHA-256. Exact sentence,
subject/object, alias and fuzzy normalization must not be conflated. Fuzzy records are candidates
only and require deterministic adjudication; a fuzzy candidate is not automatically contamination.

The historical `65,717` pattern inventory is a reproduction target, not a tuning target. The
report must say whether it is reproduced exactly, differs with exact set/hash evidence, or cannot
be reproduced. Missing aliases, templates or fuzzy candidates cause
`blocked_by_contamination_definition`; a favorable count cannot close that blocker.

## 7. WP-D — Contamination definition and measurement

### 7.1 Frozen contamination tiers

The following tiers are mutually labelled and cannot be merged into one “hit” count:

| Tier | Exact definition | Interpretation |
|---:|---|---|
| 0 | exact normalized declared training sentence | strongest declared sentence overlap |
| 1 | exact normalized subject + canonical object | canonical fact surface overlap |
| 2 | exact normalized subject + alias/object surface | declared alias/object realization overlap |
| 3 | predeclared template/full-fact pattern | structural or template overlap |
| 4 | fuzzy candidate requiring deterministic adjudication | candidate only until adjudicated |

Subject-only and object-only collisions are diagnostic counts, not factual contamination proof.
Common objects are not factual contamination without the required subject/fact context. Benchmark
overlap is a separate registry result and cannot be hidden inside corpus contamination.

### 7.2 Required definitions and per-record schema

The contract execution must freeze and report, for every tier:

- Unicode/text normalization and case/diacritic policy;
- contamination unit (document, sentence, paragraph, benchmark item or synthetic fact);
- boundary/tokenization rule;
- language and mixed-language handling;
- alias/template inclusion rule;
- false-positive and common-object handling;
- output status and aggregation unit;
- fuzzy candidate threshold, deterministic seed/parameters and adjudication rule;
- pass, conditional and blocked rule.

Each hit/candidate record must include:

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
reviewer_or_rule_revision
retrieved_at_utc
```

Raw PII is excluded from reports; bounded raw snippets, if indispensable for adjudication, remain
in the new scratch root and are referenced by hash. No zero-contamination claim is allowed when
the relevant inventory or benchmark registry is missing.

## 8. WP-E — Source-model Turkish provenance

### 8.1 Frozen roles

The provenance registry must retain the role distinction:

- **OLMo:** a priori English-dominant candidate;
- **Falcon:** comparator candidate;
- **Qwen:** multilingual positive control and retained pilot reference.

These are roles, not a claim that any model has zero Turkish exposure.

### 8.2 Required model provenance schema

For each source model and exact candidate checkpoint, record:

```text
model_id
immutable_revision
base_or_instruct
pretraining_stage
architecture_and_parameter_count
tokenizer_id_and_revision
model_card_language_statement
training_corpus_names_and_revisions
known_language_mixture
reported_turkish_evidence
turkish_fraction_or_NR
primary_source_urls_and_retrieved_at_utc
license_and_access_terms
provenance_manifest_sha256
planned_role
provenance_label
limitations
```

Allowed labels are exactly:

```text
documented_multilingual_with_Turkish
documented_English_dominant_Turkish_fraction_unreported
Turkish_exposure_not_resolvable
not_suitable_training_stage
```

No model is labelled “Turkish unseen” without primary-source evidence. Absence of a Turkish
fraction is not evidence of zero exposure. If immutable revision, stage, license or Turkish
exposure evidence cannot be resolved, status is `blocked_by_source_model_provenance` for a
claim that depends on it.

## 9. WP-F — Turkish capability and adaptation manipulation checks

### 9.1 Frozen state matrix and causal comparison

The same measurement package is required for:

```text
M0 = frozen pretrained base
M1 = selected English factual checkpoint
M2-A = general Turkish CPT, target facts excluded
M2-B = same adaptation with matched Turkish target-fact rows replacing neutral rows
```

M2-A and M2-B must use the same M1, tokenizer, adaptation seed, total token/update budget,
document ordering, optimizer, sequence length, replay, checkpoint schedule and evaluator package.
The only intended treatment difference is matched factual-row replacement. The primary factual
estimand is:

```text
TR→EN(M2-B) − TR→EN(M2-A)
```

No checkpoint, threshold, item subset or endpoint may be selected after seeing this contrast.

### 9.2 Capability dimensions kept separate

The report must not collapse the following into a single Turkish score:

1. Turkish LM fluency;
2. independent linguistic competence;
3. broad Turkish knowledge/reasoning/cultural capability;
4. tokenizer efficiency;
5. English retention;
6. synthetic factual retrieval and cross-lingual access.

### 9.3 Primary and secondary metrics

Primary normalized Turkish LM metric is frozen as UTF-8 byte-normalized BPC/bits-per-byte:

```text
primary = total negative log-likelihood bits / total UTF-8 bytes
```

The execution manifest must specify BOS/EOS inclusion, truncation/windowing, byte normalization,
document boundaries, treatment of invalid UTF-8, aggregation, and document-level bootstrap/CI.
Within one tokenizer chain, token-level PPL and its delta may be reported as secondary. Raw PPL
across tokenizer/model families may not rank models. Fertility remains a separate diagnostic:
tokens/word, tokens/character, bytes/token, unknown/special/byte-fallback behavior and Turkish /
English ratio.

TurBLiMP is preferred independent linguistic diagnostic only if WP-A registry, overlap, license
and floor/ceiling checks pass. TurkishMMLU and EXAMS are broad knowledge/school/reasoning
secondary measures, not pure language-adaptation proof. CETVEL/TurkBench subsets are allowed only
when exact task/revision/scoring/relevance are frozen. Generation-only or judge-based sections
cannot open the base causal manipulation gate.

### 9.4 Factual directions and retention

All states use the same frozen factual forms, aliases, scaffolds and item IDs:

| Direction | Frozen role |
|---|---|
| EN→EN | English/source retention guardrail |
| TR→EN | primary cross-lingual factual access outcome |
| TR→TR | secondary Turkish lexicalization + access outcome |
| EN→TR | exploratory lexicalization/control outcome |

Each direction reports answer correctness, no-answer/empty/repetition/short-output diagnostics,
relation/scaffold balance, paired uncertainty and contamination status. English retention is
reported separately and may not be traded away silently for TR→EN gains.

## 10. Thresholds, statistics and missing-data rules

Before any result is observed, the execution registry must classify each threshold as exactly one
of:

```text
literature_derived
inherited_from_frozen_project_baseline
pre_outcome_calibration
descriptive_only
```

For every endpoint it must freeze unit of analysis, pairing, seed policy, confidence interval,
bootstrap/resampling rule, multiple-comparison policy, missing/error/timeout handling, aggregation,
minimum evidence count and pass/conditional/blocked direction. A threshold may not be chosen,
relaxed or replaced after treatment results are visible. `descriptive_only` metrics never open a
gate.

The minimum paired state set is M0/M1/M2-A/M2-B, with the same item/document IDs wherever the
metric permits. Missing benchmark items, failed evaluator rows or unavailable source states are
not silently dropped: the denominator, reason, status and affected comparison are reported. A
missing mandatory input produces the corresponding blocked gate.

## 11. Exact failure and decision rules

### 11.1 Contract readiness

Before execution, all required input revisions, hashes, schemas, source access terms, benchmark
roles, inventory definitions, contamination tiers, capability endpoints and pre-outcome threshold
classes must be frozen. If any is missing, the contract remains unexecuted and the only status is
`blocked_by_measurement_design`.

When all fields are frozen and the user provides a separate one-time execution authorization, the
decision may be `ready_to_execute_bounded_measurement_audit`. That label authorizes only the
bounded measurement-design correction execution, not training.

### 11.2 Sub-gate decisions

| Condition | Exact decision |
|---|---|
| benchmark registry/revision/hash/license/evaluator/overlap/floor-ceiling incomplete | `blocked_by_benchmark_registry` |
| 713 set/hash/source definition unreconstructable | `blocked_by_synthetic_inventory_provenance` |
| pattern/alias/fuzzy inventory or contamination tiers unresolved | `blocked_by_contamination_definition` |
| BPC/capability/retention/factual endpoint design or thresholds incomplete | `blocked_by_capability_measurement_design` |
| model revision/stage/Turkish provenance claim unresolved | `blocked_by_source_model_provenance` |
| access, time, storage, input or operational bound fails | `blocked_by_operational_access` |
| all mandatory evidence passes but a substantive endpoint is unfavorable | `conditional` or `negative`, with the endpoint named |
| all mandatory evidence passes and pre-outcome gates pass | `measurement_audit_pass`, never `ready_to_train` |

One failed mandatory field fails closed; it is not substituted by a later source, an approximate
count or a favorable result. If multiple blockers exist, list all and designate the primary blocker
by the earliest frozen dependency; never hide secondary unresolved blockers.

### 11.3 Global gate

The global gate stays `blocked_by_measurement_design` until the required benchmark registry,
synthetic inventory reconciliation, contamination definitions/inventory, source-model provenance
and capability manipulation-check contract are complete and their evidence is accepted. A
successful vngrs reacquisition or a successful bounded measurement sub-work-package alone cannot
close the global gate. No result of this contract authorizes training, a new corpus choice, or
Documents 152–154.

## 12. Contract deliverables and reserved future records

The following are reserved but **must not be created by this contract-preparation task**:

- **Document 151k:** measurement-design correction execution result;
- **Document 151l:** post-measurement-design decision gate.

The future execution may write only new, hashed outputs under the new measurement root, in these
subdirectories:

```text
contracts/
registries/
inventories/
manifests/
overlap/
capability/
reports/
logs/
tmp/
```

The future execution must provide a machine-readable run manifest, benchmark registry, 713/829
set/hash reconciliation, pattern/alias/fuzzy inventory report, contamination tier ledgers,
source-model provenance registry, capability measurement registry, raw aggregate outputs,
failure log, input/output hash ledger and post-run storage/path audit. It may address only
operational/sample-manifest follow-up and these explicitly frozen measurement-design repairs.

The following remain outside its scope and must stay explicitly open:

- any full benchmark campaign or broad evaluation sweep;
- full-corpus acquisition/materialization or CulturaX access acceptance;
- model training, fine-tuning, Slurm/GPU work or model-weight download;
- resolution of any source claim not supported by immutable evidence;
- a new corpus selection or readiness-to-train decision.

In particular, this contract does not silently close the 713-surface reconciliation, missing
pattern/alias inventory or Turkish capability measurement before those outputs exist. It also
does not close any measurement blocker merely because vngrs reacquisition succeeded.

## 13. Authorization boundary and final contract status

This document is a frozen **proposal/contract**, not execution. The single next authorization that
may be requested is:

```text
User explicitly authorizes one bounded, source-read-only, non-destructive execution of the frozen
Document 151j measurement-design correction contract.
```

That authorization must continue to exclude training, fine-tuning, Slurm/GPU, model-weight or full
corpus downloads, CulturaX access-term acceptance, cleanup/deletion/migration, and creation of
Documents 151k/151l or 152–154 unless separately authorized later. Any contract violation fails
closed and produces a report rather than a partial scientific pass.

**Current status:** `UNEXECUTED`  
**Current global gate:** `blocked_by_measurement_design`  
**Current training authorization:** `BLOCKED`

## Append-only supersession note — 2026-08-07

**This note is an addendum only. The original 151j body is preserved verbatim above.**

Original pre-addendum SHA-256:

```text
15d43a2bd2c87802c0d1f9c20d20ac59c370af5135751ff02709b938be5e1259
```

The status of this document is corrected to:

```text
status = SUPERSEDED_UNEXECUTED_REQUIREMENTS_DRAFT
execution_authorized = false
scientific_results_produced = false
```

The original 151j was not executed. Its schemas, counting units, contamination tiers,
provenance labels and conceptual distinctions remain useful requirements. However, its proposed
single-wave execution request is withdrawn and must not be treated as an executable frozen
contract. The correction is required because:

1. it requires revisions, hashes, inventories, thresholds and measurement definitions to be
   frozen before execution even though the proposed execution is supposed to resolve them;
2. it combines benchmark metadata research, synthetic-inventory reconstruction, contamination
   analysis, source-model provenance, BPC, benchmark measurement and future evaluation in one
   wave;
3. the future-design M2-A/M2-B models do not yet exist;
4. exact BPC corpus/split/evaluator/windowing rules and thresholds are not frozen; and
5. the requested authorization excludes the result and gate documents needed to close the work.

The narrower, genuinely executable first phase is defined separately in Document 151m. Documents
151k and 151l remain uncreated and are not authorized from this superseded 151j draft. This note
does not create 151n/151o, does not authorize any remote or measurement work, and does not change
the global `blocked_by_measurement_design` or training `BLOCKED` gates.
