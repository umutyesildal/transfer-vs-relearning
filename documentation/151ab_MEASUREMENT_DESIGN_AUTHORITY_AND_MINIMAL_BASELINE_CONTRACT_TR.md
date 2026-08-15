# Document 151ab — MEASUREMENT-DESIGN AUTHORITY AND MINIMAL BASELINE CONTRACT (TR)

**Tarih:** 2026-08-08 (Europe/Berlin)  
**Durum:** `FROZEN — UNEXECUTED — EXECUTION-BLOCKED_PENDING_REVIEW_FIELDS`  
**Authority:** Documents 144, 145, 148, 150, 151 ve 151aa sonrası measurement-design authority  
**Global gate:** `blocked_by_measurement_design`  
**`ready_to_train`:** `false`

## 1. Kapsam ve non-execution

Bu belge, mevcut model/corpus evidence’ını yeni bir measurement-design contract altında toplar.
151ab bu turda çalıştırılmamıştır. HU’ya yazım, network, weights/tokenizer download, scoring,
inference, corpus materialization, GPU/Slurm, training, cleanup ve Documents 152–154 işlemleri
yapılmamıştır. Document 151aa’nın altı dosyalık read-only audit’i ve yedi satırlık manifest
düzeltmesi bu authority’nin input’udur.

Korunan upstream kimlikleri:

| Belge | SHA-256 / statü |
|---|---|
| 151x | `9c66cb95ee264d8411750d8e79aff258eaaeb4d1789ffc77bc8e162ffc93555b` |
| 151y | `1309af278901009c22d2ee5b2438fdec886abe27cdaa60c4555dcd3af42ae6ba` |
| 151z | `51e3cdda3db8a636f1308a42910c2dd76bfdca5ef0906a3a316dc639c4b984db` |
| 151aa | Bu belgenin oluşturulmasından sonra documentation index’e kaydedilecek |

Bu contract mevcut `blocked_by_benchmark_registry` ve `blocked_by_source_model_provenance`
blocker’larını kapatmaz. Review alanları Section 8.2’deki gibi tamamlanmadan execution başlatılamaz.

## 2. Model stage, roller ve estimand

Ana çalışma yalnızca **base/pretrained causal LM** stage’indedir. Instruction-tuned model, chat
template, SFT, DPO, synthetic dialogue veya delta-merge M2-A/M2-B ana koluna giremez.

| Model | Frozen role | Immutable revision | Sınır |
|---|---|---|---|
| `allenai/OLMo-2-0425-1B` | a-priori English-dominant primary candidate | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | Final winner değildir; Türkçe exposure/headroom kanıtı gerekir |
| `tiiuae/falcon-rw-1b` | secondary English comparator | `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | English-only card, zero-Turkish proofu değildir |
| `Qwen/Qwen2.5-1.5B` | multilingual/Turkish positive control | `8faed761d45a263340a0528343f099c05c9a4323` | Temiz unseen aday değildir |

OLMo veya Falcon `Turkish unseen` olarak adlandırılamaz; Qwen multilingual positive control olarak
raporlanır. Pythia ve diğer adaylar bu frozen execution setine response-dependent eklenemez.

State zinciri:

```text
M0 = frozen base/pretrained model
M1 = aynı modelin frozen English factual-acquisition checkpoint'i
M2-A = aynı M1 + general Turkish CPT, target facts yok
M2-B = aynı M1 + aynı Turkish CPT + matched Turkish target-fact re-exposure
```

Primary causal estimand `TR→EN(M2-B) − TR→EN(M2-A)`’dır. M2-B ekstra token/update alamaz; factual
rows matched neutral Turkish rows’un yerine geçer. `TR→TR` secondary, `EN→TR` exploratory,
`EN→EN` retention guardrail’dır.

## 3. Frozen benchmark roles ve exact registry kimlikleri

151q registry chain’de çözülmüş revision/path/evaluator kimlikleri kullanılır; execution sırasında
task, release, split veya evaluator seçilemez. Item-byte ve ordered-ID hash evidence’i 151aa’da
doğrulanan immutable registry ile eşleşmelidir.

### 3.1 TurBLiMP — primary independent linguistic diagnostic

```text
repository = https://github.com/ezgibasar/TurBLiMP
revision = 297de13fb7a0ce524fe32e8b175c6b5255d66960
primary_item_root = data/base/
evaluator = evaluation.py
evaluator_code_sha256 = c386def30cfdcbab4cd4366ef5805ab6ce4ae26a
```

Primary set `data/base/` altındaki 16 CSV’dir:

```text
augmented_anaphor_agreement.csv
augmented_argument_structure_ditransitive.csv
augmented_argument_structure_transitive.csv
augmented_binding.csv
augmented_determiners.csv
augmented_ellipsis.csv
augmented_irregular_forms.csv
augmented_island_effects.csv
augmented_nominalization.csv
augmented_npi_licensing.csv
augmented_passives.csv
augmented_quantifiers.csv
augmented_relative_clauses.csv
augmented_scrambling.csv
augmented_subject_verb_agreement.csv
augmented_suspended_affixation.csv
```

`experimental/` ve `human_judgments/` primary item setine dahil değildir. TurBLiMP exact item
hash, contamination ve floor/ceiling evidence’i tamamlanmadan primary linguistic gate açılmaz.

### 3.2 TurkishMMLU — secondary broad knowledge/reasoning

```text
repository = https://github.com/ArdaYueksel/TurkishMMLU
revision = 0686a674064a151567ae05757e1f2414ca9d83d5
items = dev/*.json and test/*.json
subjects = Biology, Chemistry, Geography, History, Mathematics, Philosophy, Physics,
           Religion and Ethics, Turkish Language and Literature
excluded = turkishmmlu_sub.json
evaluator_repository = https://github.com/EleutherAI/lm-evaluation-harness
evaluator_revision = f4d4b3de3ee6741a7151a9fe74945ee515262f4c
evaluator_path = lm_eval/tasks/turkishmmlu/config/
evaluator_subtree_sha256 = 35814d4b510da85f1bbd9f3d7293ab42bac200c8
```

Bu evaluator maintainer repository evaluator’ı gibi adlandırılamaz; author-contributed upstream
harness route’udur. TurkishMMLU broad knowledge/reasoning/cultural secondary outcome’dur, pure
language acquisition değildir. Base-model likelihood, fixed choice order ve no-CoT formatı kullanılır.

### 3.3 Turkish EXAMS — secondary school/knowledge/reasoning

```text
repository = https://github.com/mhardalov/exams-qa
revision = f859e665de6c370f6214ca5f36a34ace36ada6cb
evaluator = scripts/evaluation/evaluate_exams.py
evaluator_code_sha256 = ef242a76cd076d7144f7ed36eadc3d9da6ca7a69
```

Frozen path allowlist:

```text
data/exams/multilingual/train.jsonl.tar.gz
data/exams/multilingual/dev.jsonl.tar.gz
data/exams/multilingual/test.jsonl.tar.gz
data/exams/cross-lingual/train_tr.jsonl.tar.gz
data/exams/cross-lingual/dev_tr.jsonl.tar.gz
data/exams/cross-lingual/test.jsonl.tar.gz
data/exams/cross-lingual/with_paragraphs/train_tr_with_para.jsonl.tar.gz
data/exams/cross-lingual/with_paragraphs/dev_tr_with_para.jsonl.tar.gz
data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz
```

Turkish selection frozen path ve documented language/split rule ile yapılır; response-dependent
row selection yoktur. EXAMS school/knowledge/reasoning secondary outcome’dur.

### 3.4 CETVEL/TurkBench

Bu contract’ta zorunlu değildir. Exact task relevance, immutable item set, evaluator revision/code
hash ve base compatibility çözülmedikçe `excluded_with_reason` olarak kalır. Zorunlu üç benchmark’ın
yerine geçmez.

## 4. Held-out split sözleşmesi

```text
turkish_heldout_split_id = turkish_heldout_v1
turkish_heldout_source_control = trwiki-20260601
turkish_heldout_sha256 = REVIEW_REQUIRED_BEFORE_EXECUTION
english_retention_split_id = english_retention_v1
english_retention_sha256 = REVIEW_REQUIRED_BEFORE_EXECUTION
```

Exact split path, row/document manifest, byte count ve SHA-256 uydurulmayacaktır. Review öncesi
bu contract execution-blocked’dır. Her iki split training corpus, synthetic facts, subject/object/
alias inventory ve benchmark items ile document-level disjoint olmalı; source/domain/length
strata’sı, deterministic order seed’i ve item/document IDs manifestte korunmalıdır. Raw text
yalnız bounded scratch’ta, raporlar yalnız aggregate/hash/ID taşır.

`trwiki-20260601` frozen control’dur. CulturaX `excluded_access_blocked`; vngrs repair sonucu
operational/sample gate’i kapatsa da ana corpus selection kanıtını otomatik kapatmaz.

## 5. Contamination ve overlap policy

```text
Tier 0 = exact normalized declared training-sentence match
Tier 1 = exact subject + canonical object in one document
Tier 2 = exact subject + alias/object surface in one document
Tier 3 = template/full-fact-pattern match
Tier 4 = fuzzy candidate requiring deterministic adjudication
object-only = diagnostic only
subject-only = diagnostic only
```

Benchmark overlap synthetic-fact contamination’dan ayrı ledger’dır. Common object-only veya
subject-only eşleşme otomatik contamination değildir; Tier 4 candidate otomatik karar değildir.
Held-out veya benchmark item’ında Tier 0–3 overlap varsa item önceden tanımlı
`excluded_contaminated` kaydıyla çıkarılır; split identity/overlap-free evidence yoksa gate
`BLOCKED` kalır. 713/829 veya 65,717 inventory evidence yoksa contamination gate açılmaz. Raw
PII/snippet documentation’a alınmaz.

## 6. Measurement package

### 6.1 Primary BPC / bits-per-byte

```text
BPC = total_negative_log_likelihood_bits / total_UTF8_bytes
```

UTF-8 encoding, byte denominator, BOS/EOS, truncation, sliding-window/stride, document boundary,
masking ve aggregation frozen’dır. `ΔBPC = after − before`; negative improvement’dır.

### 6.2 Secondary within-model PPL

PPL yalnız aynı model/tokenizer chain içinde pre/post kıyaslanır. Farklı tokenizer’lar arasında raw
PPL rank’i yasaktır. Document-level distribution ve paired 95% bootstrap CI raporlanır.

### 6.3 Separate tokenizer fertility

Fertility capability score değildir ve BPC/PPL ile composite score yapılmaz. En az
`tokens_per_word`, `tokens_per_character`, `UTF8_bytes_per_token`, Turkish/English fertility
ratio, byte-fallback/unknown/special behavior ve projected tokens per dose/update/sequence
raporlanır. Tokenizer extension ana M2-A/M2-B factor’ı değildir.

### 6.4 Capability roles

| Ölçüm | Rol |
|---|---|
| TurBLiMP | Primary independent linguistic diagnostic; exact release/overlap/floor-ceiling şart |
| TurkishMMLU | Secondary broad knowledge/reasoning/cultural capability |
| EXAMS | Secondary school/knowledge/reasoning capability |
| English held-out PPL / EN→EN | Retention guardrail |
| TR→EN | Later primary factual causal outcome |
| TR→TR | Secondary Turkish lexicalization/access |
| EN→TR | Exploratory lexicalization/control |

## 7. Baseline ve dose ladder

Baseline states `M0`, `M1` ve Qwen M0/M1 positive-control chain’idir. OLMo/Falcon yalnız exact
model artifact/provenance manifesti hazırsa candidate baseline’a girebilir; missing artifact
download ile telafi edilemez ve `blocked_by_source_model_provenance` olarak raporlanır.

Factsiz M2-A-benzeri adaptation için literature-backed nominal dose ladder:

```text
50M Turkish tokens → 250M Turkish tokens → 1B Turkish tokens
```

Gerçek token exposure selected corpus manifesti ve tokenizer projected count ile doğrulanır;
factual result’a göre dose değiştirilemez. İlk geçen basamakta durulur; 1B’de geçiş yoksa M2-B
açılmaz. M2-A/M2-B’de same M1, tokenizer, optimizer, sequence, total tokens, updates, replay
ratio ve checkpoint endpoint kullanılır; B’de matched neutral row replacement vardır ve extra
token yoktur.

## 8. Thresholds, seeds ve stop rules

### 8.1 Formül ve karar threshold’ları

- BPC primary improvement: paired document bootstrap 95% CI üst sınırı `ΔBPC < 0`.
- Within-model PPL improvement: paired 95% CI üst sınırı `ΔPPL < 0`.
- TurBLiMP improvement: 95% CI alt sınırı `Δscore > 0`; zero’ı kapsayan sonuç ancak önceden
  review edilmiş equivalence/no-harm margin ile `CONDITIONAL` olabilir.
- English retention: delta alt CI sınırı review edilmiş `-δ_EN` altına inemez.
- TurkishMMLU/EXAMS chance, floor/ceiling ve CI ile descriptive secondary’dir; tek başına
  language-adaptation PASS vermez.

### 8.2 Execution öncesi review alanları

Şu değerler sonucu görmeden kullanıcı incelemesiyle doldurulmadan 151ab çalıştırılamaz:

```text
turkish_heldout_v1.sha256
english_retention_v1.sha256
delta_TurBLiMP_equivalence_margin
delta_EN_retention_margin
benchmark_floor_ceiling_saturation_rule
```

Formül, CI yönü ve PASS/CONDITIONAL/BLOCKED mantığı frozen’dır; eksik numeric margin veya hash
uydurulmayacaktır.

### 8.3 Seeds and aggregation

```text
evaluation/order seed = 42
bootstrap seeds = {42, 43}
future adaptation seeds = {42, 43}
paired unit = same document/item/fact across states
CI = predeclared paired 95% bootstrap
checkpoint = fixed endpoint; no outcome-based selection
```

### 8.4 Stop rules

Split/hash/evaluator/revision/manifest eksikliği, duplicate item ID, route mismatch, unapproved
artifact access veya byte-rule sapması wave’i `BLOCKED` yapar. English retention guardrail ihlalinde
dose ladder durur ve M2-B açılmaz. İlk passing facts-free dose bulunduğunda ladder durur. Hiçbir
basamak geçmezse `blocked_by_capability_measurement`; benchmark floor/ceiling secondary limitation
olarak raporlanır ve primary BPC/TurBLiMP yerine geçirilemez.

## 9. Status vocabulary ve future outputs

```text
ready_to_freeze_baseline_measurement_contract
ready_to_freeze_fact_free_turkish_dose_contract
blocked_by_benchmark_registry
blocked_by_source_model_provenance
blocked_by_capability_measurement
blocked_by_contamination_definition
blocked_by_measurement_design
```

Future root ve records yalnız rezerve edilmiştir; oluşturulmamıştır:

```text
future_measurement_root = /vol/tmp2/yesildau/luna_measurement_design_baseline_v1
reserved_result = Document 151ac (uncreated)
reserved_gate = Document 151ad (uncreated)
```

151ab’ın mevcut statüsü `blocked_by_measurement_design` ve `ready_to_train=false`’dır.

## 10. Tek sonraki yetkilendirme isteği

Review alanları tamamlanıp bu contract’ın final SHA’sı ayrıca doğrulandıktan sonra yalnızca şu
minimal execution değerlendirilebilir:

> Kullanıcı, Document 151ab’ın review-complete SHA’sı ile bir bounded baseline-measurement
> execution’ını açıkça yetkilendirir: mevcut immutable model artifacts ve frozen registry/evaluator
> manifests kullanılarak M0/M1 (Qwen positive control; OLMo/Falcon yalnız artifacts hazırsa)
> için UTF-8 BPC, within-model PPL, tokenizer fertility, TurBLiMP primary diagnostic ve
> TurkishMMLU/EXAMS secondary baseline/floor-ceiling calibrationı; yazımlar yalnız yeni
> `/vol/tmp2/yesildau/luna_measurement_design_baseline_v1` root’una; Documents 151ac/151ad
> oluşturulabilir. Model/corpus download, full corpus materialization, M2-A/M2-B veya dose-ladder
> training, GPU/Slurm, cleanup/deletion, previous-root writes ve Documents 152–154 bu yetkinin
> dışındadır.

Bu request 151ab’ı çalıştırmaz, training’i açmaz ve başarılı baseline sonucunu `ready_to_train`
olarak yorumlamaz. Factsiz dose execution için ayrıca ayrı frozen contract gerekir.

---

## Append-only Correction — Execution-readiness re-freeze (2026-08-08)

Bu addendum, Document 151ab’nin mevcut gövdesini silmez veya sessizce yeniden yazmaz. Mevcut
gövdenin bu correction öncesi SHA-256 değeri:

```text
pre_correction_sha256 = 500b24f6945272cbf7ddb0f26e95449434857bcac89ed5fb5d593e3fd189b4dd
```

Aşağıdaki hükümler, önceki gövdedeki aynı konudaki daha genel veya çelişkili ifadeleri append-only
olarak override eder. 151ab bu correction sonrasında da **FROZEN — UNEXECUTED** kalır. Bu addendum
ölçüm, scoring, inference, evaluation, model/tokenizer download, corpus/split materialization,
HU/SSH, GPU/Slurm, training, cleanup/deletion veya Documents 151ac/151ad ve 152–154 işlemi
yetkilendirmez.

### A. Metric nomenclature: BPB, BPC and PPL

Byte-denominator primary metric bundan sonra yalnızca **UTF-8 bits per byte (`BPB`)** olarak
adlandırılır:

```text
BPB = total_negative_log_likelihood_bits / total_UTF8_bytes
ΔBPB = after - before
```

`BPC` yalnızca karakter-denominator bir metrik için rezerve edilir:

```text
BPC = total_negative_log_likelihood_bits / total_unicode_characters
```

Önceki gövdede byte-denominator için kullanılan `BPC / bits-per-byte` adlandırması bu addendum ile
etkisizdir; byte-denominator sonuçlar BPB olarak raporlanacaktır. PPL, aynı model/tokenizer zinciri
içindeki ikincil, exponentiated özet olarak kalır ve farklı tokenizer’lar arasında model sıralamak
için kullanılmaz.

### B. Held-out split roles and immutable evidence

Önceki tek `trwiki` held-out tasarımı aşağıdaki iki ayrı role ayrılır:

| Role | Frozen definition | Current evidence state |
|---|---|---|
| Primary in-domain Turkish held-out | Finally selected Turkish adaptation corpus’undan çekilen, adaptation documents ile document-disjoint split | Corpus henüz seçilmedi/materialize edilmedi; path, manifest ve SHA uydurulmayacak; execution preparation `BLOCKED` |
| Cross-domain/control Turkish held-out | `trwiki-20260601` frozen control split | Cross-domain/control rolü; primary in-domain split’in yerine geçmez |

Primary split için deterministic document IDs, source/domain/length strata, ordered manifest,
file-byte SHA-256 ve scoring-chain identity daha sonra ayrı input-preparation aşamasında
freeze edilmelidir. `trwiki-20260601` control olarak korunur; bu isim primary in-domain split
olarak yorumlanamaz.

Bilinen WikiText-2 evidence’i korunur:

```text
known_WikiText2_token_stream_sha256 = be2effefc9f0655b0fc5bc3052ecfd18b51bdfa48bffa1ab2d4f0c217b81c78f
```

Bu yalnızca token-stream hash’idir. Required file-byte SHA-256, exact file/path manifest identity,
prompt/scoring chain ve evaluator identity yerine geçmez; bunlar ayrı review fields olarak kalır.

### C. Exact baseline-state matrix

Candidate comparison aşağıdaki state matrix olmadan yürütülemez:

| Model | M0 state | M1 state | Effective baseline rule |
|---|---|---|---|
| OLMo `allenai/OLMo-2-0425-1B` | frozen base/pretrained candidate | `M1_NOT_ACQUIRED_OR_NOT_FROZEN` | M0-only candidate; M1 acquisition/inventory ayrı authorization ister |
| Falcon `tiiuae/falcon-rw-1b` | frozen base/pretrained candidate | `M1_NOT_ACQUIRED_OR_NOT_FROZEN` | M0-only candidate; M1 acquisition/inventory ayrı authorization ister |
| Qwen `Qwen/Qwen2.5-1.5B` | frozen base/pretrained positive-control M0 | frozen M1 seed-42 step-75 chain **and** frozen M1 seed-43 step-50 chain, each exact artifact manifest/hash reviewine tabi | Qwen baseline includes M0 plus both M1 seed chains only when their immutable manifests/hashes verify |

OLMo/Falcon, weights already cached değil diye sessizce comparison’dan çıkarılamaz. Onların exact
model/tokenizer artifact inventory veya acquisition’ı ayrı, açıkça yetkilendirilmiş preparation
contract’ı ister. Aynı şekilde Qwen M1 seed-42 step-75 ve seed-43 step-50 zincirleri exact
artifact/tokenizer/config manifestleri ve SHA-256’ları doğrulanmadan tek bir “Qwen M1” satırına
indirgenemez. M1 yokluğu veya eksik manifest, `M1_NOT_FROZEN`/selection blocker olarak raporlanır;
sonradan aday seçimiyle giderilemez.

### D. Both thesis estimands

İki ayrı causal estimand zorunludur:

```text
transfer_estimand = TR→EN(M2-A) - TR→EN(M1)       [same model and sibling seed]
relearning_estimand = TR→EN(M2-B) - TR→EN(M2-A)    [same sibling seed]
```

Transfer estimand, Turkish adaptation’ın M1’e göre cross-lingual factual access katkısını ölçer.
Relearning estimand, matched Turkish factual re-exposure’ın aynı Turkish-adaptation background
üzerindeki ek katkısını ölçer. M2-A ve M2-B aynı M1 state, tokenizer, adaptation seed, document
order, total token/update budget, optimizer ve fixed endpoint kullanır; M2-B extra token/update
alamaz.

Roller ayrıca korunur:

```text
EN→EN = English retention guardrail
TR→TR = secondary access + Turkish answer lexicalization
EN→TR = exploratory lexicalization/control
```

Bu dört response direction tek bir bilingual score’a birleştirilemez. Primary factual direction
`TR→EN`’dir.

### E. Expanded pre-execution review-field ledger

Aşağıdaki alanlar beş eski placeholder ile sınırlı değildir. Her biri execution başlamadan önce
exact value, source/reference, immutable revision, manifest link ve gerektiğinde SHA-256 ile
doldurulmalıdır. Eksik değer `REVIEW_REQUIRED_BEFORE_EXECUTION` olarak kalır; tahmin edilemez:

```text
benchmark.item_set_sha256_by_benchmark
benchmark.ordered_item_id_sha256_by_benchmark
benchmark.exact_item_path_and_split_by_benchmark
benchmark.prompt_template_sha256_and_render_rule
benchmark.choice_template_sha256_and_choice_order_rule
TurBLiMP.pair_scoring_rule_and_pair_id_schema
TurkishMMLU.subject_selection_rule_and_dev_test_manifest
TurkishEXAMS.language_subset_selection_rule_and_split_manifest
base_model_compatibility_by_benchmark_and_model
model_artifact_manifest_sha256_by_model_and_state
tokenizer_artifact_manifest_sha256_by_model_and_state
BOS_EOS_inclusion_and_masking_rule
context_length_and_truncation_rule
sliding_window_stride_rule
document_boundary_and_reset_rule
NLL_aggregation_unit_and_byte_or_character_denominator
bootstrap_resample_count
bootstrap_seed_set_and_CI_method
paired_unit_and_missing_item_policy
turkish_in_domain_heldout_manifest_and_file_byte_sha256
trwiki_control_manifest_and_file_byte_sha256
english_retention_manifest_and_file_byte_sha256
evaluator_code_revision_and_code_sha256_by_benchmark
checkpoint_endpoint_and_artifact_identity_by_state
```

`known_WikiText2_token_stream_sha256` yalnız ilgili token stream evidence’ini doğrular; yukarıdaki
file-byte, manifest, evaluator, rendering ve artifact identities’lerinden herhangi birini
ikame etmez. Review ledger tamamlanmadan herhangi bir benchmark veya baseline measurement PASS’ı
üretilemez.

### F. Correct threshold semantics and repeated-dose looks

1. Uncertainty primary olarak paired document-level NLL/BPB deltasından hesaplanır. PPL, aynı
   model/tokenizer chain içinde `exp(mean loss)` veya önceden tanımlı aggregate üzerinden
   secondary summary’dir; unstable raw document-PPL means bootstrap edilerek primary karar
   verilemez.
2. TurBLiMP için tek taraflı marj **non-inferiority/no-harm** terminolojisiyle tanımlanır.
   Gerçek two-sided equivalence procedure, margin ve alpha önceden freeze edilmedikçe sonuç
   `equivalence` diye adlandırılamaz.
3. English retention için iki ayrı directional guardrail gerekir:

   ```text
   english_LM_loss_BPB_PPL_deterioration_upper_margin
   english_EN_to_EN_accuracy_deterioration_lower_margin
   ```

   Bunlar tek bir belirsiz `delta_EN_retention_margin` alanında birleştirilemez.
4. `50M → 250M → 1B` dose ladder üç predeclared sequential look olarak ele alınır. Repeated-look
   policy execution öncesi **fixed Bonferroni allocation**’dır: primary family için önceden
   seçilen total alpha üç doza eşit bölünür; her dose yalnız kendi predeclared alpha payıyla
   test edilir. İlk geçen dose fixed rule’a göre durdurur; sonradan alpha veya threshold
   değiştirilemez. Total alpha, non-inferiority margin, English guardrail margins ve exact
   multiple-comparison ledger execution öncesi review fields’tir; hiçbir değer outcome gördükten
   sonra seçilemez.

### G. Candidate-role and provenance wording correction

OLMo, a-priori **provenance-first candidate** olarak korunur; English-dominant olduğu kanıtlanmış
model değildir. Falcon secondary English comparator’dır; Qwen multilingual/Turkish positive
control’dur. Hiçbiri `Turkish unseen` olarak etiketlenemez. C2 `not_reported` training-corpus,
language-mixture veya Turkish-exposure fields uncertainty/caveat olarak kalır; C1 identity,
license, runtime ve stage provenance ile empirical Turkish headroom sağlandıktan sonra C2 alanları
tek başına sonsuz metadata blocker’ı yapılamaz. OLMo/Falcon’ın M1 state’i ayrıca acquisition ve
artifact-inventory authority gerektirir.

### H. Corrected next stage and single authorization request

151ab’ın mevcut next request’i baseline scoring/measurement istemez. Sıradaki en küçük bounded
stage yalnızca aşağıdakileri hazırlayabilir:

```text
future_input_preparation_root = /vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1
```

Bu root oluşturulmamıştır. Ayrı bir explicit authorization ile, yalnızca mevcut immutable/local
model-tokenizer artifact inventory ve evaluation-input metadata’sı read-only inventory/reconcile
edilebilir; C1 registry fields yeniden eşleştirilebilir; primary in-domain Turkish split ile
English retention split manifestleri hazırlanıp freeze edilebilir. Bu preparation stage:

- baseline scoring, inference, benchmark execution veya capability measurement yapamaz;
- model/tokenizer download, corpus/split materialization veya weights acquisition yapamaz;
- missing artifact varsa bunu `blocked_by_source_model_provenance`/`blocked_by_input_manifest` olarak
  raporlar ve ayrı contract ister;
- 151aa’yı, 151x–151z’yi veya başka frozen evidence root’larını değiştiremez;
- Documents 151ac/151ad ve 152–154 oluşturamaz.

Bu correction sonrasında tek sonraki authorization request şudur:

> Kullanıcı, corrected 151ab’ın final SHA-256’sı ile bir bounded, local/source-read-only evidence
> input-preparation pass’ini açıkça yetkilendirir: mevcut exact model/tokenizer artifact ve
> evaluation-input inventory’sini reconcile etme, C1 registry fields’i tamamlama ve primary
> in-domain Turkish ile English retention split manifestlerini yeni
> `/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1` root’una yazma. Bu yetki
> HU/SSH, network/public HTTP, download, corpus/split materialization, scoring, inference,
> evaluation, GPU/Slurm, training, cleanup/deletion, 151ac/151ad veya Documents 152–154 işlemi
> içermez. Missing artifact veya unresolved review field fail-closed blocker’dır; sonraki scoring
> veya measurement execution için ayrıca yeni contract ve açık authorization gerekir.

### I. Corrected status and freeze record

```text
status = FROZEN — UNEXECUTED — BLOCKED_BY_MEASUREMENT_DESIGN_PENDING_EVIDENCE_INPUT_PREPARATION
execution_authorized = false
measurement_executed = false
ready_to_measure = false
ready_to_train = false
151ac_151ad = uncreated_and_unauthorized
Documents_152_154 = uncreated_and_unauthorized
```

Final post-correction SHA-256, this append-only addendum’ın ardından hesaplanacak ve AGENTS.md,
`ssh-client/README.md`, documentation index ve living handoff’ta pre-correction SHA ile birlikte
aynı authority kaydı altında tutulacaktır. 151aa ve önceki chronological evidence belgeleri
değiştirilmemiştir.

### Append-only final hash freeze note

Bu correction’ın final local SHA-256 değeri, self-reference yaratmadan AGENTS.md, `ssh-client/README.md`,
documentation index ve living handoff’ta pre-correction SHA ile birlikte kaydedilmiştir. Bu hash
freeze note yeni bir execution veya measurement sonucu değildir. 151ab hâlâ unexecuted,
`blocked_by_measurement_design` ve `ready_to_train=false` durumundadır.

---

## Append-only Operational Correction 2 — HU inventory location, source allowlist and corpus gate (2026-08-08)

Bu ikinci operational correction, önceki correction’ın bilimsel hükümlerini değiştirmez; yalnızca
gelecekteki evidence/input inventory yetkisinin çalışma konumu, source mutability’si, allowlist’i,
çıktıları ve corpus gate’ini düzeltir. Mevcut corrected 151ab’nin bu operational correction
öncesi hash’i korunur:

```text
pre_operational_correction_sha256 = 3320516e674c12288d70396e31b33c059550c15365caabe9453e932e3858e2dc
```

Bu addendum da çalıştırılmamıştır. Bu turda HU/SSH, network/public HTTP, scratch-root oluşturma,
download, model/tokenizer veya corpus materialization, scoring, inference, evaluation, GPU/Slurm,
training, cleanup/deletion, result/gate document veya Documents 152–154 işlemi yapılmamıştır.

### 1. Operational location correction

Önceki `local/source-read-only` ifadesi, `/vol/tmp2` yazımı ile birlikte kullanıldığında
operasyonel olarak çelişkilidir. Effective rule bundan sonra şöyledir:

```text
source_read_only = true
execution_location = HU via documented ssh-client route, only if separately authorized
mandatory_preflight = storage + path + inode preflight before any remote read/write
existing_sources = immutable/read-only
new_writable_root = /vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1
new_writable_root_status = not created by this correction
```

Gelecekteki bounded inventory wave’i HU/SSH kullanabilir; bu, yalnızca bu correction sonrasında
ayrıca açıkça yetkilendirilen bir execution için geçerlidir. HU home
`/vol/fob-vol6/mi25/yesildau`, bütün önceki evidence/repair roots ve source artifact files read-only
kalır. Yeni yazım yalnızca yeni scratch root altında compact inventory manifests, ledgers,
reports ve storage-audit kayıtları olabilir. Source content, selected weights ve existing
manifests overwrite edilemez.

### 2. Closed source allowlist

Gelecekteki inventory wave’i yalnız aşağıdaki mevcut, belgelenmiş kaynaklara erişebilir. Allowlist
kapalıdır; parent-directory traversal, broad glob, response-dependent source addition veya yeni
public source seçimi yoktur. Aşağıdaki source paths read-only’dir:

#### 2.1 Qwen selected M1 artifacts and source identity

```text
/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75
/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50
/vol/tmp2/yesildau/qwen_scale_selected_v1/seed42_step75/selected_artifact_manifest.json
/vol/tmp2/yesildau/qwen_scale_selected_v1/seed43_step50/selected_artifact_manifest.json
/vol/fob-vol6/mi25/yesildau/frozen-models/qwen_m1_selected_v1
/vol/fob-vol6/mi25/yesildau/frozen-models/qwen_m1_selected_v1/archive_manifest.json
```

Document 127’deki selected-manifest SHA’ları `seed42_step75 =
aed52ff8baeb01b89efef443caa560b707871dfe52fde6bcec1d8ae3e46fb032` ve `seed43_step50 =
af3569aae2bd8066f51bb0ff1fecd4eec13eb74b5ba794915eae565f13f8bd53` olarak korunur. HU-home
archive yalnız read-only fallback’tir; archive manifest SHA’sı
`29098e221dd1be47a68fecc35a430c6784acc807e4ff5a04b1eda7c95a2980d8`’dir.

Qwen base/source-model identity, tokenizer identity ve M1 chain provenance yalnız bu exact
selected manifests ile onların manifest içinde açıkça bağlanan existing source-manifest entries
üzerinden reconcile edilebilir. Manifestte bağlanmayan hiçbir checkpoint, cache, optimizer state,
snapshot veya parent-directory file’i source allowlist’e dahil değildir. Büyük weight files için
yalnız path/stat/size ve mevcut manifest hash okunabilir; full weight re-hash bu contract’ın parçası
değildir.

#### 2.2 Existing frozen language-input evidence

```text
/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl
/vol/tmp2/yesildau/turkish_bridge_v1
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1/samples/trwiki_20260601_seed42_max10000_20260807.jsonl
```

WikiText-2 için yalnız mevcut input/evidence identity ve statik metadata okunur; corpus yeniden
edinilmez. `trwiki-20260601` için yalnız mevcut frozen control sample/manifest evidence’i okunur;
new dump, sample veya split materialization yapılamaz. `turkish_bridge_v1` altında yalnız
Document 149/151’de açıkça referanslanan control manifest metadata’sı erişilebilir; raw document
content recursive olarak okunamaz.

#### 2.3 Existing vngrs/provenance and registry evidence

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1/ledgers/vngrs_request_ledger.jsonl
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1/manifests/vngrs_record_manifest_corrected.jsonl
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1/reports/repair_evidence_hashes.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/contracts/preflight_manifest.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/requests/request_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/manifests/file_manifest.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/manifests/hash_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/benchmark_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/source_model_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/coverage_matrix.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/reports/registry_completion_report.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/reports/post_run_storage_audit_correction.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/contracts/retry_preflight_manifest.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/requests/retry_request_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/manifests/retry_file_manifest.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/manifests/retry_hash_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reconciliation/first_wave_reuse_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_benchmark_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_source_model_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/registries/retry_coverage_matrix.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reports/retry_registry_completion_report.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1/reports/retry_post_run_storage_audit.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/input_manifest.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/input_hash_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/coverage_repair_field_matrix.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/coverage_repair_benchmark_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/coverage_repair_source_model_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/coverage_repair_reconciliation.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/output_artifact_manifest.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/coverage_repair_report.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_coverage_repair_v1/post_repair_storage_audit.json
```

Bu listede belirtilmeyen raw sample, benchmark item payload, model weight, tokenizer snapshot,
cache veya corpus file’i future inventory wave’inde okunamaz. Existing root’ların path/stat
preflight’i gerekli olsa bile dosya içeriği yalnız yukarıdaki exact compact evidence paths için
okunabilir.

### 3. Bounded inventory limits and fail-closed rules

Future wave’in operasyonel limitleri önceden şöyledir:

```text
max_public_http_requests = 0
max_download_bytes = 0
max_recursive_corpus_reads = 0
max_large_weight_rehash_bytes = 0
max_source_path_stat_entries = 256
max_source_metadata_files = 256
max_source_metadata_bytes = 16777216
max_new_output_files = 64
max_new_output_bytes = 16777216
max_wall_clock_seconds = 900
max_writable_roots = 1
```

`max_source_path_stat_entries` large weight roots için yalnız path, type, size, mtime/inode ve
existing-manifest linkage anlamına gelir; weight bytes okunup hash’lenmez. Metadata byte bound,
allowlisted JSON/JSONL/YAML/config/tokenizer identity ve compact report bytes’larının toplamıdır.
Her bound, duplicate path, source-root mismatch, unapproved file, home write veya prior-root
mutation wave’i fail-closed `BLOCKED` yapar. Mandatory HU storage/path/inode preflight ve
post-run storage audit olmadan wave tamamlanmış sayılamaz.

### 4. Corpus-selection and split gate correction

Future inventory wave’i primary in-domain Turkish split seçemez, oluşturamaz veya freeze edemez.
Ana adaptation corpus henüz seçilmedi/materialize edilmediği için:

```text
selected_corpus_exists = verify_only
candidate_corpus_evidence = inventory_existing_only
missing_selected_corpus = blocked_by_corpus_selection_or_materialization
primary_in_domain_split = not_created_and_not_authorized
trwiki_20260601 = cross_domain_control_only
```

Wave yalnız mevcut selected-corpus artifact’ın varlığını doğrulayabilir, candidate-corpus/sample/
provenance evidence’ini inventory edebilir, mevcut WikiText/trwiki identities ve model/tokenizer
manifestlerini reconcile edebilir ve desteklenen C1 alanlarını raporlayabilir. Corpus seçimi,
materialization, primary in-domain split construction ve split hash’i için daha sonra ayrı bir
corpus decision/execution contract gerekir. `blocked_by_corpus_selection_or_materialization`
global `blocked_by_measurement_design` gate’ine katkı verir; metadata inventory bunu kapatmış
sayılmaz.

### 5. Future outputs and reserved result/gate documents

Future new scratch root altında yalnız compact outputs üretilebilir:

```text
inventory_preflight_manifest.json
source_allowlist_ledger.jsonl
model_tokenizer_inventory.jsonl
evaluation_input_inventory.jsonl
c1_reconciliation.jsonl
inventory_report.json
post_inventory_storage_audit.json
final_inventory_audit.json
```

Bu outputs copied weights, raw corpus documents, benchmark scoring data, raw PII/sensitive text
veya model snapshots içeremez. `151ac/151ad`, önceki baseline-measurement result/gate rezervasyonu
olarak korunur ve kullanılmaz. Bu operational inventory için index-safe yeni rezervasyon:

```text
reserved_result = Document 151ae (uncreated)
reserved_gate = Document 151af (uncreated)
```

151ae/151af bu correction’da oluşturulmaz; yalnız ayrı future execution authorization ile
oluşturulabilir. Başarılı inventory wave’i corpus selection, scoring, measurement, training veya
`ready_to_train` statüsü doğurmaz.

### 6. Corrected single next authorization request

Bu correction sonrasında 151ab’ın tek sonraki isteği artık local-only veya split-producing değildir:

> Kullanıcı, corrected 151ab’ın final SHA-256’sı ile **bir bounded HU/SSH evidence/input inventory
> execution**’ını açıkça yetkilendirir. Execution; mandatory storage/path/inode preflight’ı,
> yalnız yukarıdaki closed source allowlist’in read-only kullanımını, yalnız yeni
> `/vol/tmp2/yesildau/luna_measurement_design_input_preparation_v1` scratch root’una yazımı ve
> post-run storage audit’ini kapsar. Public HTTP/network, download, model/tokenizer/corpus veya
> benchmark materialization, primary in-domain split construction, scoring, inference, evaluation,
> GPU/Slurm, training, cleanup/deletion, HU-home writes, prior-root writes, Documents 151ac/151ad
> ve Documents 152–154 bu authorization’ın dışındadır. Yalnız compact manifests, ledgers ve
> inventory reports üretilebilir; selected corpus yoksa result `BLOCKED` ve
> `blocked_by_corpus_selection_or_materialization` olarak fail-closed raporlanır. Ayrı bir corpus
> decision contract’ı olmadan primary in-domain split hash’i veya `ready_to_measure`/`ready_to_train`
> iddiası yapılamaz. Bu execution ancak kullanıcı ayrıca bu tek isteği açıkça yetkilendirirse
> başlayabilir.

### 7. Corrected operational status and final-hash record

```text
status = FROZEN — UNEXECUTED — BLOCKED_BY_MEASUREMENT_DESIGN
operational_inventory_authorized = false
source_roots = immutable/read-only
new_scratch_root = not_created
primary_in_domain_split = blocked_by_corpus_selection_or_materialization
reserved_result_gate = 151ae/151af, uncreated
ready_to_measure = false
ready_to_train = false
```

Final post-operational-correction SHA-256 self-reference oluşturulmadan AGENTS.md,
`ssh-client/README.md`, documentation index ve living handoff’a pre-operational-correction hash
ile birlikte kaydedilecektir. 151aa ve önceki chronological evidence belgeleri değiştirilemez.
