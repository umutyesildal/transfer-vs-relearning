# 151g — Bounded Audit Repair Contract

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Tür:** Minimal repair contract; **uygulanmadı**  
**Girdiler:** 151a frozen contract, 151f evidence-integrity correction and externally prompted validation  
**Current gate before repair:** `blocked_by_operational_access`  
**Secondary unresolved gate:** `blocked_by_measurement_design`

## 1. Yetki sınırı

Bu belge yalnızca sonraki **bounded, source-read-only, non-destructive repair wave that may write
only new samples, ledgers, manifests and reports to a new explicit scratch repair root**'un
değişmez koşullarını tanımlar. 151g'nin oluşturulması execution authorization değildir ve bu
belge uygulanmayacaktır.

Bu contract training, fine-tuning, GPU/Slurm, model-weight download, full corpus download/materialization, artifact mutation, cleanup, deletion, migration veya HU home output yetkisi vermez. Sonraki tek gerekli yetki, kullanıcıdan yukarıda tanımlanan **bounded, source-read-only, non-destructive repair wave that may write only new samples, ledgers, manifests and reports to a new explicit scratch repair root**'u açıkça çalıştırma onayıdır. Onay gelmeden hiçbir helper, API sample veya CPU analysis tekrar çalıştırılmaz.

151d ve 151e değiştirilmez. 151g onların provisional/non-contract-compliant statüsünü onarmak için yeni evidence üretme koşullarını dondurur; historical sample'ları geriye dönük manifestlemez.

### 1.1 Frozen evidence roots ve overwrite yasağı

```text
existing_evidence_root: /vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
existing_evidence_root_status: immutable/read-only
new_repair_root: /vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1
new_repair_root_write_policy: only new samples, ledgers, manifests and reports
```

Mevcut evidence root altındaki hiçbir sample, report, manifest, cache veya evidence file
overwrite edilemez. Yeni repair root açıkça oluşturulmadan ve output path'i doğrulanmadan
network veya sample işlemi başlatılamaz. 151d/151e historical files'larına backfill veya
in-place correction yapılmaz.

## 2. Frozen disposition ve kaynaklar

### 2.1 Required, excluded ve control source set

```text
required_web_sources = {vngrs-ai/vngrs-web-corpus}
excluded_access_blocked_sources = {uonlp/CulturaX}
control_sources = {trwiki-20260601}
```

`CulturaX` access-blocked statüsü vngrs repair audit'inin tamamlanmasını otomatik olarak
engellemez. Ancak CulturaX--vngrs comparative source selection, CulturaX erişimi ve
contract-compliant evidence'i sağlanana kadar kullanılamaz.

### 2.2 vngrs disposition

vngrs için repair disposition:

```text
reacquire_to_exactly_10000
```

Bu karar 151d'deki 3.400 kayıtlı partial sample'ı tamamlanmış saymaz. Bir sonraki yetkili wave, exact 10.000 unique record ve tam per-record manifest üretemezse otomatik fallback:

```text
abandoned_as_access_blocked
```

Fallback'te 3.400'lük mevcut sonuçlar yalnız exploratory partial diagnostics olarak kalır; `quality_pass` veya corpus selection üretmez.

Frozen vngrs source:

```text
repo: vngrs-ai/vngrs-web-corpus
immutable revision: ee5c6201ee84457a18182bfc483a7d8a7f3655ba
split: train
seed: 42
target: exactly 10,000 unique records
hard transfer stop: 1 GiB
```

CulturaX için kullanıcı adına access/contact agreement kabul edilmez. Hesapta erişim önceden açık değilse `excluded_access_blocked_sources` içinde kalır ve ayrı `blocked_by_access_condition` olarak raporlanır. `trwiki-20260601` yalnız frozen control'dür; mevcut partial JSONL contract-compliant manifest yerine geçirilmez.

## 3. API-rate-limit-safe deterministic vngrs sampling

Bu prosedür 151g execution wave'i için ilk network request'ten önce frozen'dır:

1. Dataset metadata'sındaki `50,336,214` train row universe ve `page_size=100` kullanılır.
2. `random.Random(42)` ile **tam 100 unique vngrs page ID** ilk request'ten önce üretilir. İlk request'ten önce `new_repair_root` altında `ordered_page_ids`, `ordered_page_ids_sha256`, `sampling_code_version`, `sampling_runtime_version`, `sampling_code_sha256` ve `sampling_runtime_sha256` kaydedilir; ordered page list'in kendisi de aynı pre-request ledger'a immutable input olarak yazılır.
3. Page list response'a göre değiştirilemez: response-dependent page selection, failed-page replacement ve farklı seed/sample-size seçimi yasaktır. Page order ve row order `sample_index` sırasını belirler; response arrival order kullanılmaz.
4. Aynı anda yalnız bir request yapılır. Request'ler arasında en az 2 saniye beklenir; API'nin `Retry-After` header'ı varsa ona uyulur.
5. HTTP 429 için aynı önceden seçilmiş page yeniden denenir ve backoff süreleri sırasıyla `30, 60, 120, 240, 480` saniyedir. Page alınamazsa failed page başka page ile değiştirilemez; wave fail-closed olur.
6. `max_total_http_requests = 600`, `max_total_retries = 500` ve `max_wall_clock_duration = 12h` execution başlamadan önce frozen ve ledger'da kaydedilmiş olmalıdır. Bu bound'lardan herhangi biri 10.000 unique record tamamlanmadan dolarsa verdict `blocked_by_operational_access` olur.
7. Duplicate stable source row/document ID tespit edilirse wave fail-closed olur; duplicate kayıt düşürülerek sessizce 10.000'e tamamlanamaz. Exact target **10.000 unique records**'tır.
8. Aggregate response-transferred byte hard stop `1 GiB` olarak kalır; bu stop 10.000 unique record'dan önce dolarsa `blocked_by_operational_access` olur. Full shard/full corpus indirilmez.
9. 10.000 unique record tamamlanırsa kalan request yapılmaz. 3.400'lük historical sample yeni completed evidence olarak adlandırılmaz.

Rate-limit durumu, ordered page list, request/retry/wall-clock bounds, byte budget ve unique-row
count değiştirilemez. Başarısız page için replacement yapılamaz.

## 4. Ayrı request ledger ve record manifest şemaları

Request-level byte accounting ile record-level byte accounting birbirine karıştırılamaz.
Response-level byte değeri her record'a kopyalanamaz ve aynı response byte değeri record sayısı
ile çarpılarak veya tekrar tekrar toplanarak record bytes olarak raporlanamaz.

### 4.1 Request ledger schema

Her HTTP request için, sample JSONL'den ayrı ve yeni repair root altında:

| Field | Zorunlu içerik |
|---|---|
| `request_id` | Wave içinde unique, monotonic ID |
| `page/offset` | Önceden frozen page ID ve/veya API offset/length |
| `request_start_utc` | Request gönderilmeden hemen önce ISO-8601 UTC timestamp |
| `response_end_utc` | Response body okuması tamamlandığında ISO-8601 UTC timestamp |
| `HTTP status` | Exact HTTP status code veya transport failure code |
| `retry_count` | Aynı page/request için 0-based retry count |
| `response_transferred_bytes` | Bu HTTP response'un ölçülen toplam transferred bytes değeri; request-level only |
| `content encoding` | Response'un gerçek content-encoding bilgisi |
| `response SHA-256` | Alınan response bytes'ın SHA-256 değeri |

### 4.2 Record manifest schema

Her response içindeki her record için, request ledger'den ayrı manifest JSONL'de:

| Field | Zorunlu içerik |
|---|---|
| `source_repo` | Frozen canonical repository ID |
| `request_id` | Record'ı taşıyan request ledger kaydı |
| `record index within response` | Response içindeki 0-based record index |
| `stable source row/document ID` | Kaynağın stable row/document ID'si; local line index ikame edilemez |
| `sample_index` | `0..9999`, frozen deterministic order |
| `immutable revision` | Exact commit/snapshot SHA; `main` tek başına kabul edilmez |
| `split/shard` | Kaynak split ve shard/file ID; yoksa gerekçeli `NR` |
| `exact serialized record payload bytes` | Yalnız bu record'ın exact serialized payload byte sayısı |
| `source_compressed_bytes` | Kaynak record-level compressed byte bilgisi gerçekten varsa; yoksa gerekçeli `NR` |
| `normalized-text SHA-256` | 151a NFC + whitespace-normalized UTF-8 SHA-256 |
| `retrieved_at_utc` | Response sırasında üretilmiş ISO-8601 UTC timestamp |

`response_transferred_bytes` yalnız request ledger'de tutulur. Her record'a aynı response byte
count yazılmaz; record payload bytes response-level byte count'tan türetilmiş varsayımsal bir
paylaştırma olamaz. Missing timestamp, measured byte veya required identity değeri historical
sample'a backfill edilemez; yeni wave'de zorunlu alan eksikse ilgili record/wave fail-closed olur.

Manifest directory repair wave başında oluşturulacak olsa bile, bu contract yazılırken mevcut scratch'e manifest dosyası eklenmez. 151d/151e sample'larına timestamp/byte backfill yapılmaz.

## 5. trwiki repair record policy

Mevcut trwiki JSONL'de `document_id`, `source_line_index` ve `normalized_text_sha256` bulunması yeterli değildir; `immutable_revision`, source split/shard, measured bytes ve retrieved UTC timestamp eksiktir. Yeni contract-compliant manifest ancak record source'tan okunurken canlı oluşturulabilir. Mevcut historical record'lara sonradan tahmini timestamp/byte yazılamaz.

Trwiki repair sample'ı aynı seed-42 control population'dan üretilecekse sample order, source line/document ID, normalized text hash ve measured source read bytes precommitted ledger ile kaydedilir. Bu wave çalıştırılmadıkça trwiki verdict `quality_conditional` üstüne çıkarılamaz.

## 6. Near-dedup ve quality implementation

### 6.1 Near-dedup

Repair contract'te undeclared per-document feature cap yoktur:

```text
feature: all normalized character 5-grams per document
MinHash: num_perm=128
seed: 42
LSH: 32 bands × 4 rows
near threshold: estimated Jaccard >= 0.80
```

512-feature cap 151a'da frozen olmadığı için repair wave'de uygulanmaz. Bellek yetmezliği olursa sessiz cap eklenmez; near-dedup sonucu `blocked_by_measurement_design` olur ve partial pair count frozen result olarak raporlanmaz.

### 6.2 Quality/repetition

Quality diagnostic olarak document başına 2.048 evenly-spaced normalized character 5-gram feature cap açıkça frozen'dır. Bu cap near-dedup sonucu değildir ve quality diagnostic ile near-dedup contract'i birbirine karıştırılamaz.

## 7. Synthetic inventory counting units

Repair wave şu exact grain'leri kullanır:

```text
semantic_fact_id = subject_id | relation
relations = profession, birthplace, residence, university, employer
semantic_fact_count = 25,000
bilingual_resolved_row = semantic_fact_id | language
bilingual_resolved_row_count = 50,000
```

Ayrı tutulacak alanlar:

- 5.000 unique subject;
- 25.000 language-independent semantic fact;
- 50.000 `en`/`tr` language-expanded resolved row;
- language-specific answer-string sets;
- canonical object-surface set;
- alias inventory;
- template/pattern inventory;
- declared/generated training sentences.

Canonical surface pass için exact membership set ve SHA zorunludur. Mevcut profile-derived union 829 yüzeydir ve SHA'sı:

```text
18e43a35961a75cf18919ff940555eb31aac96bde5a75adc15e96936262650df
```

151a declared `713` setinin exact definition/membership/hash'i sağlanmadan 713 veya 829 sayılarına canonical pass anlamı verilmez. 65.717 pattern ve alias/fuzzy listesi materialize değilse contamination gate `blocked_by_measurement_design` kalır. Object-only hit'ler semantic target-fact hit'i sayılmaz.

## 8. Benchmark revision/item/hash registry

Her benchmark için registry kaydı zorunludur:

| Field | Zorunlu |
|---|---|
| benchmark name ve task/subset | Evet |
| immutable dataset/repository revision | Exact SHA |
| item-set file ve SHA-256 | Evet |
| split ve item count | Evet |
| license/access evidence | Evet |
| scoring/evaluator code revision ve SHA | Evet |
| overlap normalization rule ve result | Evet |
| retrieval timestamp UTC | Evet |

TurkishMMLU, Turkish EXAMS, TurBLiMP ve CETVEL/TurkBench bu registry tamamlanmadan clean veya non-contaminated sayılmaz. Registry eksikliği `blocked_by_measurement_design` üretir; item sayısı uydurulmaz.

## 9. Exact decision rules

### 9.1 Source verdicts

- `quality_pass`: required sample size reached; all mandatory manifest fields present; source revision immutable; transfer hard stop respected; no undeclared dedup cap; required LID/quality/dedup/overlap/contamination diagnostics have contract-compliant outputs.
- `quality_conditional`: sample/manifest is usable for explicitly labelled exploratory diagnostics, but one or more non-fatal coverage, access, or measurement conditions remain; it cannot be used as a frozen corpus selection.
- `quality_blocked`: required sample or manifest is unavailable, incomplete because of access/rate limit, or required evidence cannot be verified.

### 9.2 Operational and measurement gates

- Primary combined gate is `blocked_by_operational_access` if any required web source remains incomplete because of HTTP 429, gated access, missing row access, or missing required manifest fields.
- Secondary gate is `blocked_by_measurement_design` if operational access is available but benchmark registry, synthetic set definition/hash, near-dedup implementation, contamination definition, or capability measurement freeze is incomplete.
- `ready_to_*` and `ready_to_train` are forbidden until both gates close in a later explicitly authorized contract.
- A partial vngrs sample, even with strong LID, cannot produce `quality_pass`.
- CulturaX access terms are never accepted on behalf of the user; absent prior account access remains `blocked_by_access_condition`.

## 10. Repair-wave scope ve reserved deliverables

Repair wave yalnız şu iki düzeltme sınıfını kapsar: (i) operational access/sample completeness
ve complete request/record manifest evidence'i, (ii) 151a'ya uygun ve açıkça frozen near-dedup
implementation. Aşağıdakiler bu wave'in kapsamı dışındadır ve ayrı measurement blockers olarak
kalır: benchmark revision/item/hash registry, `713` surface reconciliation, missing
pattern/alias inventory, contamination-definition closure ve Turkish capability measurement.

```text
reserved: Document 151h — repair-wave execution result
reserved: Document 151i — post-repair decision gate
status: not created; not authorized
```

151h veya 151i bu reservation ile oluşturulmuş sayılmaz. Successful vngrs reacquisition tek
başına `blocked_by_measurement_design` gate'ini kapatmaz ve training veya Documents 152--154
yetkisi vermez.

## 11. Non-execution and next authorization

151g uygulanmadı. No API sample, manifest generation, dedup rerun, benchmark download, synthetic materialization, model download, Slurm job, training, cleanup or deletion was performed for this contract.

The single next authorization required is:

```text
User explicitly authorizes one bounded, source-read-only, non-destructive repair wave that may
write only new samples, ledgers, manifests and reports to a new explicit scratch repair root,
using the frozen vngrs 10,000-record reacquisition procedure and complete request/record manifest
schema above.
```

Bu onay verilmeden Documents 152–154 oluşturulmaz ve hiçbir training/execution stage açılmaz.
