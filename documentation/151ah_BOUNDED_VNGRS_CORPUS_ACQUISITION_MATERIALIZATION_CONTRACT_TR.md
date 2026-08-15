# Document 151ah — BOUNDED VNGRS CORPUS ACQUISITION AND MATERIALIZATION CONTRACT (TR)

**Tarih:** 2026-08-08  
**Authority:** Document 151ag corpus selection decision; Documents 145, 148, 149, 150, 151,
151h, 151i, 151p, 151aa, corrected 151ab, 151ae ve 151af  
**Durum:** `FROZEN — PREPARATION_BLOCKED — UNEXECUTED`  
**Reserved result/gate:** Documents 151ai/151aj (uncreated; reserved only)

## 1. Contract boundary

Bu contract yalnız conditional primary candidate olan
`vngrs-ai/vngrs-web-corpus` için bir sonraki acquisition/materialization wave'inin sınırlarını
dondurur. Bu belge bu turda çalıştırılmamıştır. HU, SSH, network, public HTTP, download, scratch
root creation, corpus materialization, scoring, inference, evaluation, model/tokenizer download,
GPU/Slurm, training, cleanup veya deletion yapılmamıştır.

Contract execution şu anda `PREPARATION_BLOCKED`'dır. Sebep, izin verilen read-only evidence'ta
immutable release file/shard route listesi ve execution-time license capture'ın bulunmamasıdır.
Bu boşluk wildcard route veya varsayılan shard adı uydurularak kapatılmayacaktır. Küçük bir
metadata-only route-resolution pass'i exact değerleri sağladıktan ve bu contract append-only
olarak yeniden freeze edildikten sonra ayrıca açıkça authorize edilmelidir.

## 2. Exact source identity and allowlist

| Alan | Frozen contract değeri | Evidence/condition |
|---|---|---|
| `source_repo` | `vngrs-ai/vngrs-web-corpus` | 151h/151i ve dataset-card literature record |
| `immutable_revision` | `ee5c6201ee84457a18182bfc483a7d8a7f3655ba` | 151h/151i exact revision |
| `source_split` | `train` | 151h/151i |
| `source_universe_rows` | `50,336,214` | Önceki bounded API universe; resolved release ile tekrar eşleşmeli |
| `license` | `CC BY-NC-SA 4.0` | Local literature/card record; route response ve attribution text execution öncesi capture edilmelidir |
| `source_file_shard_allowlist` | **UNRESOLVED CLOSED SET — no route allowed yet** | Exact file path/shard ordinal, immutable resolve URL, compressed bytes, raw bytes, row count ve SHA-256 metadata-only pass ile doldurulmadan execution BLOCKED |
| `dataset-card approximate size` | `84.9 GB` olarak yalnız planning metadata'sı | Full release byte evidence'i değildir; 25.33B sayı VBART-token bağlamındadır |

Bu contract'ın source allowlist'i bir wildcard değildir. Resolved allowlist şu kapalı kayıtları
her source file/shard için zorunlu taşımalıdır:

```text
source_repo
immutable_revision
split
shard_ordinal
exact_source_file_path
immutable_resolve_url
license_and_attribution_evidence_id
compressed_bytes
uncompressed_bytes
document_row_count
source_file_sha256
retrieved_at_utc
```

Herhangi bir path, shard ordinal, byte veya hash eksikse execution başlamaz; tüm release
materialization'ı `PREPARATION_BLOCKED` olarak kapanır. Dataset card'daki yaklaşık değerler bu
ledger'ın yerine geçemez.

## 3. Roots, write policy and hard bounds

Existing evidence ve source roots immutable/read-only'dir. Yeni root bu contract execution'ında
kullanılacak tek yazılabilir yerdir; bu hazırlık turunda oluşturulmamıştır:

```text
existing evidence root(s): read-only; no overwrite
new root: /vol/tmp2/yesildau/luna_vngrs_corpus_acquisition_materialization_v1
```

HU home `/vol/fob-vol6/mi25/yesildau`, prior audit roots ve prior repair roots'a yazım yasaktır.
Cache, temporary files, logs, downloaded archives, extracted data ve outputs yalnız new root
altında olmalıdır. Mandatory preflight ve post-run audit `AGENTS.md`/`ssh-client/README.md`
kurallarına göre execution result'a yazılır.

Contract bounds, execution başlamadan önce değiştirilemez:

| Bound | Exact maximum/target | Fail-closed kuralı |
|---|---:|---|
| Target unique documents | exactly `50,336,214` | Daha azı incomplete/blocked; daha fazlası duplicate/contract violation |
| Total HTTP requests | `2,048` | Bound'a ulaşmadan target tamamlanmazsa `blocked_by_operational_access` |
| Total retries | `4,096` | Retry bound hit edilirse wave kapanır |
| Compressed/download bytes | `100,000,000,000` bytes | Response veya archive byte toplamı aşarsa fail closed |
| Extracted/raw canonical bytes | `250,000,000,000` bytes | Aşımda hiçbir filtered artifact PASS sayılmaz |
| Wall clock | `43,200` seconds | Süre dolarsa target tamamlanmadıysa blocked |
| Output regular files | `128` | Yeni output file bound'u aşılmaz; old root değiştirilemez |
| Request/response ledger rows | one per request, max `2,048` | Retry ayrı request row; response byte tekrar record row'larına kopyalanmaz |

Bu sayılar source release'in gerçekleşmiş boyut iddiası değildir; contract safety bounds'udur.
Scratch capacity/inode preflight bu bound'ları karşılamıyorsa execution başlamaz. Metadata-only
route resolution, bu bound'ların resolved shard count/bytes ile uyumunu göstermelidir.

## 4. Deterministic acquisition protocol

1. İlk request'ten önce exact source file/shard allowlist, ordered shard listesi, code/runtime
   version, allowlist SHA-256 ve request plan SHA-256 yazılır.
2. File/shard ordering `shard_ordinal`, sonra exact source file path, sonra stable source row ID
   ile lexicographic ve immutable'dır. HTTP response, retry, status veya content-dependent
   seçim page/shard listesine etki edemez.
3. Failed page/shard replacement yoktur. Duplicate stable source row/document ID wave'i fail
   closed yapar; duplicate record silently drop edilmez.
4. Her source file için response chain, content type, content encoding, compressed bytes,
   uncompressed bytes, final URL, response SHA-256 ve archive/file SHA-256 ayrı ledger'a yazılır.
5. `source_row_id` exact release manifestinde yoksa acquisition başlatılmaz; local ordinal ile
   immutable source identity icat edilemez.
6. Target count ancak allowlisted release filesin tümü integrity PASS olduktan sonra kabul
   edilir. Network response'a göre erken durma veya sonradan sample büyütme yasaktır.

## 5. Staged fail-closed execution

### Stage 0 — metadata and storage precondition

- Mandatory HU home/scratch capacity and inode preflight.
- `readlink -f` ile all output/cache/tmp/log roots.
- Exact route/license/shard registry ve its SHA-256.
- Expected document, request, response-byte, extracted-byte ve file-count totals.
- Route, license, evaluator veya numeric bound unresolved ise `PREPARATION_BLOCKED`; Stage 1'e
  geçilmez.

### Stage 1 — acquisition and integrity

- Yalnız allowlisted vngrs release files/shards.
- Per-file archive SHA-256, compressed/uncompressed byte ve row-count equality.
- Per-record stable source ID, serialized payload SHA-256 ve normalized-text SHA-256.
- Request ledger response bytes ile record manifest record bytes ayrı tutulur; full response byte
  count her record'a kopyalanmaz ve tekrar tekrar toplanmaz.
- Any missing row, extra row, duplicate ID, bad hash, byte-bound veya timeout = blocked.

### Stage 2 — canonical raw/filtered artifact and deterministic diagnostics

Stage 1 PASS olmadan filtered corpus veya diagnostics sonucu scientific evidence değildir. Stage 2
tek model-neutral canonical artifact üretir; tokenizer-specific 50M/250M/1B dose slices üretmez.

#### LID

- Frozen implementation/model revision ve SHA-256 manifestte bulunur; unresolved ise blocked.
- Per-document top-1 language ve confidence kaydedilir.
- Inclusion threshold: `document_top1=tr` ve confidence `>=0.80`.
- Aggregate gate: retained input üzerinde document top-1 Turkish `>=98.00%`.
- `strict_mixed_line` aggregate `<=5.00%` diagnostic bound'udur; mixed line yalnız line-level
  diagnostic'tir ve tek başına document'ı non-Turkish yapmaz.
- Document-level ve line-level göstergeler tek bir “Turkish percentage” altında birleştirilmez.

#### Encoding and length

- UTF-8 decode başarısızlığı, replacement character, NUL/control-character violation veya boş
  normalized text reject reason code ile manifestte tutulur; raw sensitive text documentation'a
  yazılmaz.
- Normalized character length `[200, 100,000]` dışındaysa deterministic reject.
- Unicode normalization formu, whitespace rule ve normalization code SHA-256 freeze edilir.

#### Quality/boilerplate/spam/code/adult

Heuristic ve semantic filters ayrı field/status olarak tutulur; tek opaque quality score yoktur.
Contract threshold'ları:

```text
url_or_navigation_line_ratio > 0.20       => exclude
code_or_markup_line_ratio > 0.20          => exclude
boilerplate_duplicate_line_ratio > 0.50   => exclude
spam_flag=true                             => exclude
adult_or_harmful_flag=true                => exclude
```

Evaluator implementation, lexicon/model revision ve SHA-256 route-resolution/contract manifestte
freeze edilmeden bu eşikler çalıştırılamaz. Aggregate raw text değil yalnız counts, rates ve
reason codes taşır.

#### PII

- Email, phone, credential/token, full postal/contact identifier ve predeclared personal-ID
  recognizer hit'leri `pii_flag` olarak tutulur.
- PII hit'i olan document canonical training artifact'a alınmaz; yalnız salted identifier,
  count ve reason code yazılır.
- Raw PII örnekleri report, manifest veya documentation'a kopyalanmaz.
- PII recognizer version/lexicon SHA-256 eksikse gate `PREPARATION_BLOCKED` olur.

#### Exact and near dedup

- Exact dedup: Unicode-normalized full-document text SHA-256; duplicate group ID deterministic.
- Sentence/paragraph duplicate hashes ayrı diagnostic'tir.
- Near dedup: normalized character 5-gram set **feature cap olmadan**.
- MinHash: 128 permutations, seed `42`.
- LSH: 32 bands × 4 rows.
- Pair flag: estimated Jaccard `>=0.80`.
- Dedup is global across source files/shards; train/held-out leakage check splitten önce ve sonra
  yapılır. Equal IDs are not silently resolved.

### Stage 3 — contamination and overlap

Stage 2 quality, LID, PII, exact-dedup ve near-dedup PASS olmadan Stage 3 başlatılamaz.

Frozen local synthetic inventory units:

```text
5,000 subjects
25,000 unique semantic fact_id
50,000 bilingual resolved rows (language-expanded, not new semantic facts)
713 canonical Relation-V2 object surfaces
20,000 exact training sentences
4 × 5,000 subject/name channels
4 dataset-artifact identifiers
total declared contamination patterns = 65,717 unique pattern entries
```

Counting unit `fact_id`'dir. Alias, template, canonical object surface, language-specific answer
string ve training sentence ayrı ledgersdir; biri diğerinin semantic-fact sayısına eklenmez.
Source/derived Relation-V2 evidence hashes:

```text
source/legacy profile = 020c4daef91a25e6cc553a67241c448d2a0bb7fb23b8184d5296b55e524f455b
Relation-V2 profile    = 60dd741f8ef2815755beafa8bb5799f4112af3d94b1b8c4c171bfef28b07e6c1
release manifest       = 94df56dba548c81d39b03b7b7fe4f9a59d9555997e984fd7aed5cabd0a113425
```

Exact, Unicode-normalized, predeclared alias/template/fuzzy tiers ve benchmark-overlap ledger
ayrı field-level manifestte bulunmalıdır. Bunlar yoksa contamination stage BLOCKED; object-only
collision decisive full-name/fact collision ile karıştırılmaz. Benchmark train/dev/test ve
Turkish capability item overlap'ı yalnız metadata/ID/hash düzeyinde raporlanır; scoring yapılmaz.

### Stage 4 — document-disjoint primary split and training pool

Stage 3 PASS olmadan split oluşturulmaz. Frozen split protocol:

```text
split namespace = vngrs_primary_in_domain_heldout_v1
seed = 42
held-out target = exactly 1,006,724 documents
training-pool target = exactly 49,329,490 documents
selection key = SHA-256(seed || namespace || stable source row/document ID)
```

Selection stable source ID üzerinde yapılır; document, paragraph veya normalized-text duplicate
crossing split'e izin verilmez. Shard/source/domain/length strata için ordered counts manifestte
taşınır. Held-out ve training pool document-disjoint olmak zorundadır; duplicate/ambiguous ID'de
fail closed. `trwiki-20260601` bu split'e karıştırılmaz; ayrı cross-domain control artifact'ı
olarak kalır.

Canonical output model-neutral raw/filtered artifact'tır. Model veya tokenizer seçilmeden final
50M/250M/1B tokenizer-specific dose slice yazılmaz. Sonraki token projection yalnız frozen
canonical artifact, selected model/tokenizer revision, fertility code SHA-256 ve predeclared
byte/token budget üzerinden üretilebilir; bu contract onu çalıştırmaz.

## 6. Required evidence schemas and final audit chain

### Request ledger (one row per HTTP request)

```text
request_id
source_file_or_shard
request_start_utc
response_end_utc
HTTP_status
retry_count
response_transferred_bytes
content_encoding
response_SHA256
final_response_url
```

### Source-file/shard manifest

```text
source_repo
immutable_revision
split
shard_ordinal
exact_source_file_path
immutable_resolve_url
compressed_bytes
uncompressed_bytes
document_row_count
source_file_SHA256
license_evidence_id
retrieved_at_utc
```

### Record manifest (one row per unique source record)

```text
request_id
source_file_or_shard
record_index_within_response_or_file
stable_source_row_document_ID
sample_index_or_full_release_index
source_repo
immutable_revision
split/shard
exact_serialized_record_payload_bytes
serialized_record_payload_SHA256
normalized_text_SHA256
retrieved_at_utc
lid_status_and_confidence
quality_reason_codes
pii_flag
exact_duplicate_group_id
near_duplicate_group_id
contamination_status
heldout_or_training_pool
```

`response_transferred_bytes` request ledger'da bir kez bulunur; record manifestte
`exact_serialized_record_payload_bytes` bulunur. Response-level byte değeri her record'a
kopyalanmaz ve record bytes olarak toplanmaz.

### Output manifest and final audit

Ordered `output_artifact_manifest.jsonl` şu alanları taşımalıdır:

```text
artifact_order
relative_path
artifact_kind
bytes
sha256
row_count_or_null
source_contract_sha256
created_utc
retention_status
```

Final `final_materialization_audit.json` en son yazılır ve kendi hash'ini veya kendisini
manifestte listelemez. Audit; contract SHA, route/list hash, file/row/document totals, every
gate status, split disjointness, request/retry/byte/time bounds, source-root unchanged claim,
post-run storage/inode values, no-cleanup claim ve `ready_to_measure`/`ready_to_train` flags'ini
taşır. Self-reference veya missing mandatory field execution failure'dır.

## 7. Decision rules and retention

```text
PREPARATION_BLOCKED:
  exact route/shard/license evidence, evaluator hashes, alias/template ledgers veya required
  numeric metadata unresolved; no Stage 1 request is allowed.

BLOCKED:
  any contract violation, incomplete target, duplicate ID, bound hit, integrity/quality/PII/
  contamination/split failure or audit-chain failure.

CONDITIONAL:
  source artifact and declared gates complete, but external measurement-design blockers remain;
  this is not ready_to_measure or ready_to_train.

PASS:
  all contract gates and final audit PASS, with no forbidden operation; still no training
  authorization and no automatic closure of global measurement-design blockers.
```

Selected/frozen canonical artifacts, manifests, ledgers and reports retain edilir. Bu wave'de
cleanup, deletion, migration veya overwrite yoktur. Any later cleanup needs a separate explicit
authorization and retention manifest.

Bu contract model acquisition, benchmark scoring, inference, evaluation, GPU/Slurm, training,
M1/M2-A/M2-B execution veya Documents 152–154 işlemi değildir. Successful vngrs materialization
tek başına `blocked_by_measurement_design` gate'ini kapatmaz ve `ready_to_train` üretmez.

## 8. Freeze and next authorization

151ah `FROZEN — PREPARATION_BLOCKED — UNEXECUTED` olarak kaydedilmiştir. Exact file/shard route
ve execution license evidence için önce küçük metadata-only resolution pass'i gereklidir. Bu
belge çözülmemiş alanları doldurmak için sessizce değiştirilemez; resolution sonrası append-only
correction ve yeni SHA-256 gerekir.

Documents 151ai ve 151aj bu contract'ın gelecekteki execution result/gate kayıtları için reserve
edilmiştir ve bu turda oluşturulmamıştır. Hiçbir execution, training veya ready-to-train kararı
bu belgeyle verilmemiştir.

## 9. Append-only correction — bounded release metadata resolution and structural repair

**Correction date:** 2026-08-08  
**Pre-correction SHA-256:** `a8c1d1d2082ec3ae5b31ace5dc0a9506ace90f82d0f7bd1a2c1a528069ef2269`  
**Effective status after this addendum:** `FROZEN — PREPARATION_BLOCKED — UNEXECUTED`

This addendum is append-only. Where the earlier body conflicts with this section, this section is
the effective contract authority; the earlier text and its SHA remain historical evidence.
Nothing in this correction authorizes HU/SSH, a full-shard or corpus-row download, materialization,
151ah execution, scoring, inference, evaluation, GPU/Slurm, training, cleanup, deletion or
Documents 151ai/151aj/152--154.

### 9.1 Official public metadata actually verified

The bounded public review used only the official Hugging Face dataset card, immutable repository
tree and immutable README route for:

```text
source_repo       = vngrs-ai/vngrs-web-corpus
immutable_revision = ee5c6201ee84457a18182bfc483a7d8a7f3655ba
source_split      = train
dataset_tree      = https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/tree/ee5c6201ee84457a18182bfc483a7d8a7f3655ba/data
readme_route      = https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/blob/ee5c6201ee84457a18182bfc483a7d8a7f3655ba/README.md
```

The official immutable README metadata records:

| Field | Verified value | Evidence status |
|---|---|---|
| train examples | `50,336,214` | verified in the immutable README metadata |
| train dataset size | `141,807,806,497` bytes | verified metadata value; not a per-shard ledger |
| Hub download size | `84,893,303,434` bytes | verified metadata value; not a retry-aware execution bound |
| schema | `text: string`, `corpus: string`, `original_id: int64` | verified |
| license | `cc-by-nc-sa-4.0` / CC BY-NC-SA 4.0 | verified metadata label |
| attribution | attribution to the VBART paper is required by the card | verified card text |
| shard layout | `data/train-00000-of-00284.parquet` through `data/train-00283-of-00284.parquet` | tree exposes 284 Parquet paths; complete per-file ledger not captured |
| source description | cleaned Turkish sections of OSCAR-2201 and mC4 | verified card text |

The tree page shows the Parquet files as LFS objects and exposes rounded sizes for the visible
prefix (for example 447--452 MB for the first files and 285--316 MB for the later visible
prefix). The upload labels such as “part 00000-of-00006” are upload batches, not a six-shard
dataset; the actual release tree has 284 Parquet shards. This distinction supersedes any
six-part interpretation in preparation notes.

The following required fields were **not** verified in the bounded public pass and remain
preparation blockers:

```text
per-shard immutable LFS/Xet object identifiers at ee5c6201...55ba
per-shard exact SHA-256 and explicit hash semantics
per-shard exact compressed and uncompressed byte counts
Parquet footer row-group counts and footer schema for the selected files
execution-time README/license byte capture and SHA-256
sample-based tokenizer token-yield/fertility lower-bound evidence
```

The native `original_id: int64` field is therefore frozen as the candidate stable source-ID
field, with a fail-closed uniqueness check. It is not evidence that IDs are unique across the
whole release or within every selected shard; that property must be checked from the actual
selected-shard metadata/records during a separately authorized execution. No release-coordinate
ID is substituted while the native-field check remains unresolved.

The card's statement of approximately 25.33B VBART-tokenized tokens implies only a release-level
planning ratio of approximately `503.22` VBART tokens per row (`25.33B / 50,336,214`). It is not
sample-based evidence, not a lower confidence bound, and not a tokenizer-fertility measurement
for the project's candidate models. It must not be used to claim that a bounded shard subset is
adequate.

### 9.2 Corrected bounded-shard decision

The prior full-release target is overridden. The contract may never silently target all
`50,336,214` rows. The only permissible acquisition shape is a deterministic whole-shard subset
chosen before the first data request.

The bounded candidate domain is fixed to the first 32 release coordinates, in ordinal order:

```text
candidate_domain = {
  data/train-00000-of-00284.parquet,
  data/train-00001-of-00284.parquet,
  ...,
  data/train-00031-of-00284.parquet
}
```

The ellipsis above is a notation for the explicitly generated ordered coordinate set
`00000, 00001, ..., 00031`; it is not an executable wildcard and it is not yet the selected
allowlist. At most 32 whole shards may be selected. The exact selected list remains
`UNFROZEN / PREPARATION_BLOCKED` until every candidate file has exact immutable object/hash,
byte and footer metadata and the following pre-download calculation has real inputs:

```text
planned_max_token_pool                 = 1,000,000,000 tokens
predeclared_safety_factor              = 1.50
required_projected_retained_token_yield = 1,500,000,000 tokens
selection_order                        = shard_ordinal ascending
selection_unit                         = whole Parquet shard, never a response-dependent prefix
selection_stop                         = smallest prefix whose lower-bound retained yield reaches
                                         the required projected yield
```

The lower-bound retained yield must be computed from exact selected-shard footer row counts,
the existing sample-based retention estimate and sample-based tokenizer-yield/fertility evidence.
Those sample values are not present in the reviewed local evidence, so no shard is currently
frozen as an execution allowlist. The 32-shard domain is a hard upper bound and a bounded repair
decision, not permission to download it. If the lower-bound calculation cannot reach the target
within the domain, the contract fails closed and requires a new correction; no extra shard may be
added after the first request.

### 9.3 Corrected populations, split and LID ordering

The following populations are separate and must never be equated:

```text
raw_acquired_population          = all rows in the selected whole shards after integrity checks
filtered_retained_population     = raw_acquired_population minus deterministic rejects
heldout_population               = document-disjoint subset of retained canonical documents
training_pool                    = filtered_retained_population minus heldout_population
```

The old fixed values `1,006,724` and `49,329,490` are revoked. The corrected bounded split
rule is:

```text
heldout_target = min(100,000, max(10,000, ceil(0.02 * retained_canonical_document_count)))
training_pool_count = retained_canonical_document_count - heldout_target
split_namespace = vngrs_primary_in_domain_heldout_v2
seed = 42
selection_key = SHA-256(seed || split_namespace || stable_source_row_document_ID)
```

The 2% fraction follows the repository's existing deterministic split convention, while the
10,000 minimum and 100,000 ceiling bound the later measurement cost independently of the raw
release size. This is a bounded measurement-design target, not a claim that the split is already
materialized or hashed. The exact count is computed only after the retained population is known;
it may not be filled with raw-release arithmetic. The split remains document-disjoint and
`trwiki-20260601` remains a separate cross-domain control.

LID ordering is corrected as follows:

1. report aggregate Turkish LID on the raw acquired population before document retention;
2. apply the frozen per-document LID rule and all other retention gates;
3. report retained-pool language composition separately;
4. apply any retained-pool gate only to the separately reported retained population.

The aggregate gate may not be defined as a consequence of the per-document retention rule. The
exact LID implementation/model revision, confidence calibration and SHA-256 remain unresolved;
therefore no LID PASS is authorized.

### 9.4 Corrected bounded resource and request ledger

The old `4,096` retry maximum under `2,048` total requests is revoked. For the bounded candidate
domain, the hard ceilings are:

| Bound | Corrected maximum/target | Fail-closed rule |
|---|---:|---|
| candidate/selected whole shards | `32` | no shard outside the frozen candidate domain; no response-dependent addition |
| unique acquired rows | `6,000,000` | footer/record totals above the bound fail closed |
| total HTTP requests including retries | `256` | any request row above the bound fails closed |
| total retry attempts | `128` | retries are request rows and may not exceed total requests |
| transferred response bytes including retries | `25,000,000,000` | exceeded byte total fails closed |
| raw/canonical serialized bytes | `40,000,000,000` | exceeded output/input byte total fails closed |
| wall-clock duration | `43,200` seconds | unfinished bounded target at deadline is `BLOCKED` |
| output regular files | `256` | creation above the bound fails closed |
| peak process RSS | `68,719,476,736` bytes (64 GiB) | observed peak above bound fails closed |
| newly allocated inodes | `4,096` | preflight must show capacity; exceedance fails closed |

Each retry is one request-ledger row. `response_transferred_bytes` is counted once per request
attempt and never copied into every record row. Record-level bytes remain exact serialized-record
payload bytes. The selected-shard manifest, request plan, code/runtime identity and all computed
bound calculations must be written before the first data request.

### 9.5 Local implementation audit and remaining blockers

The local repository audit was read-only. The repository contains a generic Wikimedia/XML corpus
pipeline, not a vngrs Parquet acquisition/materialization implementation. Specifically:

| Required component | Local finding | Status |
|---|---|---|
| vngrs shard/Parquet reader and footer verifier | no vngrs-specific implementation found; existing dump helper is Wikimedia/XML | blocker |
| Turkish LID model/evaluator | no frozen vngrs LID tool/model identity or SHA | blocker |
| normalization | generic NFC/control/whitespace/markup routine; no vngrs contract identity/hash | blocker |
| quality/spam/code/adult filters | only generic configurable character/URL/markup heuristics; required evaluators absent | blocker |
| PII recognizer | no contract-compliant recognizer/version/lexicon hash found | blocker |
| exact dedup | normalized full-text SHA-256 exists | partial; vngrs integration/order not frozen |
| near dedup | no MinHash/LSH implementation found | blocker |
| synthetic contamination | local synthetic pattern inventory exists, but vngrs ingestion/benchmark-overlap integration is absent | blocker |
| benchmark overlap | no benchmark-overlap ledger/evaluator identity found | blocker |
| document split | generic SHA-256 split with default 2% exists; old 151ah split arithmetic is revoked | partial |

The environment declaration lists Python 3.11, `pyarrow`, `datasets`, `huggingface_hub`,
`mwxml==0.3.8` and `mwparserfromhell==0.7.2`, but this is not proof of the execution runtime,
vngrs evaluator versions or artifact hashes. No tool identity or threshold is invented by this
correction.

### 9.6 Effective decision and next gate

```text
151ah status                  = FROZEN — PREPARATION_BLOCKED — UNEXECUTED
bounded subset decision       = candidate domain bounded to 32 whole shards;
                                exact selected allowlist not frozen
operational gate              = blocked_by_corpus_selection_or_materialization
global gate                   = blocked_by_measurement_design
ready_to_measure              = false
ready_to_train                = false
151ai/151aj                   = reserved and uncreated
```

Residual blockers are exact per-shard object/LFS IDs and hashes, exact bytes, Parquet footer
metadata, execution-time license/attribution byte hashes, sample-based token/fertility lower
bounds, and all missing local vngrs filter/LID/PII/near-dedup/overlap tool identities. A future
execution request is not valid until these blockers are resolved and the exact selected shard
allowlist, plan hash and all gates are frozen. Successful vngrs materialization would not close
`blocked_by_measurement_design` or authorize training.

This correction creates no result/gate document. Documents 151ai and 151aj remain reserved and
uncreated.

## 10. Append-only systematic shard-selection correction (2026-08-08)

This addendum preserves the immediately preceding frozen SHA-256 as the pre-correction record:

```text
pre_correction_sha256 = 9151da7112b6d1ab9bbb3b483b202dec23449624beeddb53c23682569a0f598b
```

The prior first-32 ordinal candidate domain is no longer the preferred selection rule. It is
retained in the chronological record above, but it must not be used for a future bounded sample
or acquisition wave. The exact path set below is now the deterministic, source-spread systematic
selection for the maximum 32 whole-shard pool. It is generated before any request and is not
response-dependent:

```text
selection_version = vngrs_systematic_midpoint_32_of_284_v1
selection_formula = floor((rank + 0.5) * total_shards / selected_shards)
total_shards = 284
selected_shards = 32
selected_ordinals =
  00004, 00013, 00022, 00031, 00039, 00048, 00057, 00066,
  00075, 00084, 00093, 00102, 00110, 00119, 00128, 00137,
  00146, 00155, 00164, 00173, 00181, 00190, 00199, 00208,
  00217, 00226, 00235, 00244, 00252, 00261, 00270, 00279
selection_evidence_payload_sha256 = dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686
```

The corresponding immutable paths are:

```text
data/train-00004-of-00284.parquet
data/train-00013-of-00284.parquet
data/train-00022-of-00284.parquet
data/train-00031-of-00284.parquet
data/train-00039-of-00284.parquet
data/train-00048-of-00284.parquet
data/train-00057-of-00284.parquet
data/train-00066-of-00284.parquet
data/train-00075-of-00284.parquet
data/train-00084-of-00284.parquet
data/train-00093-of-00284.parquet
data/train-00102-of-00284.parquet
data/train-00110-of-00284.parquet
data/train-00119-of-00284.parquet
data/train-00128-of-00284.parquet
data/train-00137-of-00284.parquet
data/train-00146-of-00284.parquet
data/train-00155-of-00284.parquet
data/train-00164-of-00284.parquet
data/train-00173-of-00284.parquet
data/train-00181-of-00284.parquet
data/train-00190-of-00284.parquet
data/train-00199-of-00284.parquet
data/train-00208-of-00284.parquet
data/train-00217-of-00284.parquet
data/train-00226-of-00284.parquet
data/train-00235-of-00284.parquet
data/train-00244-of-00284.parquet
data/train-00252-of-00284.parquet
data/train-00261-of-00284.parquet
data/train-00270-of-00284.parquet
data/train-00279-of-00284.parquet
```

This is an exact path-selection decision, not evidence that these files have known exact
compressed bytes, LFS/Xet object IDs, Parquet footer rows, license-byte hashes or source-corpus
composition. The official immutable tree establishes the 284-file path family and rounded UI
sizes only; the unresolved per-shard fields remain `NULL`/`UNRESOLVED` and must be populated from
bounded official metadata before any execution. The systematic spread is chosen to avoid the
known first-prefix/source-domain risk; it is not a claim that the resulting `corpus` composition
is already balanced. Any footer or sample-calibration result that fails the frozen source-balance,
identity, integrity or dose-cap checks fails closed and cannot trigger replacement-shard
selection.

The release-level approximately 503.22 VBART-token-per-row ratio remains a planning check only.
It cannot establish tokenizer yield or justify materialization. The 32-shard pool remains a hard
maximum and an overprovisioned calibration/acquisition domain, not an authorization to download
or materialize it.

### 10.1 Effective status after the selection correction

```text
151ah status                  = FROZEN — PREPARATION_BLOCKED — UNEXECUTED
exact path set                = FROZEN, systematic and source-spread
exact per-shard registry      = INCOMPLETE / PREPARATION_BLOCKED
operational gate              = blocked_by_corpus_selection_or_materialization
global gate                   = blocked_by_measurement_design
ready_to_measure              = false
ready_to_train                = false
151ai/151aj                   = reserved and uncreated
```

No shard, row or model artifact was downloaded; no corpus was materialized; and no result/gate
document was created by this correction. A later bounded calibration contract is required to
resolve sample-based retention, LID/PII/quality/dedup/overlap behavior and conservative capacity
before any 151ah execution can be considered. Successful calibration or vngrs acquisition alone
does not close `blocked_by_measurement_design` or authorize training.
