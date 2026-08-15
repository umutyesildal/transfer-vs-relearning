# 151h — Bounded Audit Repair Wave Execution Result

**Tarih:** 2026-08-07 (Europe/Berlin)  
**İşçi:** LUNA-Worker 2  
**Tür:** Document 151g execution result; source-read-only ve non-destructive repair  
**Girdi contract:** Document 151g, SHA-256 `eb9992af3bb4bb4fca18e0198ce772051d67e861b8b41d8298071434c5bf3b92`

## 1. Yetki ve kapsam

Kullanıcının tek-seferlik açık execution yetkisi üzerine Document 151g'nin yalnızca frozen
repair-wave kısmı çalıştırıldı. Çalışma şu kaynak setiyle sınırlıydı:

```text
required_web_sources = {vngrs-ai/vngrs-web-corpus}
excluded_access_blocked_sources = {uonlp/CulturaX}
control_sources = {trwiki-20260601}
```

Training, fine-tuning, GPU/Slurm, model-weight download, full corpus download veya
materialization, CulturaX access-term kabulü, cleanup, deletion, migration ve Documents
152--154 oluşturma yapılmadı. `ready_to_train` üretilmedi.

Mevcut evidence root immutable/read-only tutuldu:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
```

Yeni dosyalar yalnızca şu repair root altına yazıldı:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1
```

151d ve 151e değiştirilmedi. 151g de değiştirilmedi; bu belge onun çalıştırma sonucudur.

## 2. Hash gate ve preflight

HU erişiminden önce lokal Document 151g SHA-256 yeniden hesaplandı ve kullanıcı tarafından
verilen değerle birebir eşleşti:

```text
eb9992af3bb4bb4fca18e0198ce772051d67e861b8b41d8298071434c5bf3b92
```

HU storage/path/inode preflight'i read-only yapıldı:

| Kontrol | Sonuç |
|---|---|
| HU home kullanımı | `14G` |
| `/vol/tmp` | `140T` toplam, `122T` kullanılan, `%88`; inode `%3` |
| `/vol/tmp2` | `140T` toplam, `27T` kullanılan, `%19`; inode `%3` |
| `/vol/fob-vol6` | `1.3T` toplam, `667G` kullanılan, `%53`; inode `%53` |
| Existing root resolve | tam olarak frozen existing root |
| New repair root başlangıç durumu | yoktu; yeni oluşturuldu |
| Existing root preflight inventory | 1.564 file, 162.513.315 byte |

Post-run inventory aynı kaldı. Existing root inventory digest'i:
`c0e5a59001cdb88c1ef3f9f26c0f8b3058c3e7df943aa6370380404fe0497b1c`.

## 3. Deterministic vngrs reacquisition

Frozen source `vngrs-ai/vngrs-web-corpus`, revision
`ee5c6201ee84457a18182bfc483a7d8a7f3655ba`, `train` split ve seed 42 kullanıldı. Dataset'in
50.336.214 satırlık universe'i ve 100-row API page size üzerinden tam 100 unique page ID,
ilk HTTP request'ten önce üretildi. Ordered page list ve offset listesi:

```text
ordered_page_ids_sha256 = 361561f8db310228ecc13d8b9c32d8954500e71eaff1c3a693c7a7c119bcefd8
sampling_code_sha256 = 8955a21b15de250deb7dd1047da89db572cda357bf19c2dc4bcea0b0ff8f2b9f
sampling_runtime_sha256 = ccd6fa34a08933c02634f97ac43659d9534cc4783b10ffa9a454f027a2d6ad0a
generated_at_utc_before_first_request = 2026-08-07T13:48:24.877527Z
```

Response-dependent page selection, failed-page replacement ve duplicate source ID düşürme
yapılmadı. Page list, runtime, code hash ve bütün frozen bound'lar
`reports/sampling_plan.json` içinde korunuyor.

Sonuç:

| Ölçüm | Sonuç |
|---|---:|
| Hedef unique record | 10.000 |
| Toplanan record | 10.000 |
| Tamamlanan page | 100/100 |
| HTTP request | 102 |
| HTTP 200 | 100 |
| HTTP 429 | 2 |
| Retry | 2 |
| Aggregate response-transferred bytes | 28.949.291 |
| Duplicate stable source ID | 0 |
| Request/retry/wall-clock/byte bound hit | Hayır |

Her 429 aynı frozen page üzerinde retry edildi; page replacement yapılmadı. 10.000 unique
record tamamlanınca başka request yapılmadı. Request-level byte değerleri
`ledgers/vngrs_request_ledger.jsonl` içinde tutuldu; record byte olarak tekrarlanmadı.

## 4. Manifest ve byte-accounting doğrulaması

Request ledger'da 102 unique request kaydı ve Document 151g'nin tüm zorunlu alanları var.
Contract-manifest olarak `manifests/vngrs_record_manifest_corrected.jsonl` kullanıldı ve
10.000 record içeriyor. `manifests/vngrs_record_manifest.jsonl` korunmuş ilk üretimdir; aynı
root içinde sessizce silinmedi veya overwrite edilmedi.

Corrected manifest'te:

- `source_repo`, immutable revision, `request_id`, response içi record index, stable source
  row/document ID ve `sample_index` var;
- `split/shard`, rows API source shard bilgisini expose etmediği için gerekçeli
  `NR` olarak kaydedildi; API page ID yalnız request provenance'tır;
- `exact serialized record payload bytes` her record için ayrı ölçüldü;
- `source_compressed_bytes`, rows API record-level compressed byte expose etmediği için
  gerekçeli `NR` olarak kaydedildi;
- normalized-text SHA-256 ve response sırasında üretilmiş `retrieved_at_utc` var.

Validation sonucu: required manifest field eksikliği yok, manifest/sample ID alignment doğru,
sample index `0..9999` sıralı ve normalized-text SHA mismatch yok. Historical 151d/151e
sample'larına timestamp veya byte backfill yapılmadı.

## 5. Contract-authorized diagnostics

### 5.1 LID

HU'daki immutable fastText modelin SHA-256 değeri
`8f3472cfe8738a7b6099e8e999c3cbfae0dcd15696aac7d7738a8039db603e83` olarak doğrulandı.
10.000 vngrs record işlendi:

```text
document top-1 Turkish = 9,988/10,000 = 99.88%
strict mixed-line flag = 201/10,000 = 2.01%
```

`mixed` yalnız line-level diagnostic'tir; document'ın non-Turkish olduğu anlamına gelmez.
LID record ve aggregate raporları yalnız yeni repair root altındadır.

### 5.2 Quality

Quality implementation Document 151g'deki ayrı 2.048 evenly-spaced normalized character
5-gram cap'i kullandı. Bu cap near-dedup'a uygulanmadı. 10.000/10.000 record işlendi;
aggregate quality report ham PII içermiyor, yalnız pattern-hit counts veriyor. Model-token
length bu repair wave'de model/tokenizer indirilmediği için `NR` bırakıldı.

### 5.3 Near-dedup

Near-dedup, 10.000 vngrs ve read-only 10.000 trwiki control record'ı üzerinde tamamlandı:

```text
all unique normalized character 5-grams; feature cap = none
MinHash = 128 permutations, seed = 42
LSH = 32 bands × 4 rows
near threshold = estimated Jaccard >= 0.80
```

Sonuç raporunda 586.666 bucket, 1.095.071 LSH candidate pair ve MinHash estimated
Jaccard >= 0.80 için 3.357 pair (vngrs internal 156, trwiki internal 3.201) yer alıyor.
Exact normalized-text duplicate pair sayısı 577'dir (vngrs 14, trwiki 563). CulturaX
erişimi olmadığı için CulturaX comparative pair sonucu üretilmedi.

İlk near-dedup denemesi HU helper'ın 600 saniyelik silence timeout'una 17.000/20.000
kayıtta takıldı; sonuç olarak kabul edilmedi. Cap eklenmeden vektörleştirilmiş retry
tamamlandı ve ilk deneme kaydı `reports/diagnostic_attempts.json` içinde korundu.

LID/quality'nin ilk uyumluluk denemesi de fastText-wheel/NumPy 2.x çağrı uyumsuzluğu
nedeniyle fail-closed oldu. Retry yalnız in-memory `np.array(copy=False)` uyarlaması kullandı;
immutable dependency cache değiştirilmedi. Boş ilk output dosyaları kronolojik iz olarak
korundu, sonuç yerine kullanılmadı.

## 6. Post-run storage audit ve evidence hashes

Post-run storage/inode audit `reports/postrun_storage_audit.json` altında yazıldı. HU home
`14G` olarak kaldı. Yeni repair output'ları scratch'te kaldı; cleanup, deletion veya
migration yapılmadı. Existing root post-run inventory preflight ile birebir aynı:

```text
file_count = 1,564
total_bytes = 162,513,315
inventory_digest = c0e5a59001cdb88c1ef3f9f26c0f8b3058c3e7df943aa6370380404fe0497b1c
```

Repair root'taki dosyaların SHA-256 değerleri `reports/repair_evidence_hashes.json` içinde
yer alıyor. Önemli evidence hash'leri:

| Dosya | SHA-256 |
|---|---|
| `samples/vngrs_seed42_repair_20260807.jsonl` | `642434f27a8bf8ddfee7d4eb4b528963e23515ba5518afcdabf35fb2483a6e55` |
| `ledgers/vngrs_request_ledger.jsonl` | `d27f3b45e1dab02eff68e05fdf8297be2fdb4d22fcdc5eaf3809ca85b910750e` |
| `manifests/vngrs_record_manifest_corrected.jsonl` | `8eec5079718c4a1b3a91a35000be733b982bb972df76ae2eeb396a64f3cb0418` |
| `reports/vngrs_lid_diagnostics_retry1.json` | `fde0be1a0d50d1e77e5cf924dfc2f6ad143ff9159c0a96b052f6551d011e1be9` |
| `reports/vngrs_quality_diagnostics_retry1.json` | `4a1bf3522715dcef4596b64fae2039a0ac43d97dc44590a1a7f151827860a44b` |
| `reports/vngrs_near_dedup_diagnostics_retry1.json` | `a4554160773016de8f4defc488d7d622b6c3a7a1ba42379a186ff4c8414a534d` |
| `reports/repair_validation_summary.json` | `f860a3a567e3d56a6289e6bf8d602b6337d8f541863cbf44f4fac1e23d9177d1` |

## 7. Execution verdict ve sonraki karar

`repair_validation_summary.json` status'u `passed`'dır. Required vngrs operational/sample
repair koşulları sağlandı: exact 10.000 unique record, complete request ledger, complete
corrected record manifest, immutable revision, no bound hit ve unchanged existing root.

Bu sonuç yalnız vngrs operational/sample-manifest ve açıkça frozen near-dedup repair
scope'unu kapatır. Global `quality_pass`, frozen corpus selection veya training readiness
iddiası değildir. CulturaX `excluded_access_blocked` olarak kalır; vngrs repair'inin
tamamlanmasını otomatik olarak engellemedi, fakat CulturaX--vngrs comparative selection
hala yapılamaz.

Primary gate'in vngrs repair açısından durumu ve secondary measurement gate, Document 151i'de
karar kuralına göre verilecektir. Training ve Documents 152--154 hâlâ yetkisizdir.

## 8. Append-only clarification — manifest semantics and near-dedup scope

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Statü:** 151h'nin önceki bölümlerine ek açıklama; önceki sayısal sonuçları değiştirmez

Bu bölüm, sonradan fark edilen evidence-integrity ayrımlarını açıklar. 151h'nin önceki
bölümleri, sayısal sonuçları ve 151i'deki karar dayanağı geriye dönük olarak yeniden
yazılmamıştır.

### 8.1 Manifest alanlarının kaynak anlamı

İlk vngrs manifestinde `source_compressed_bytes` alanı açıkça `NR` olarak değil, `null`
olarak yazılmıştı. Aynı ilk manifestte API page identifier'ı gerçek bir source shard gibi
temsil edilmişti. İncelenen rows API gerçek bir source shard alanı sunmadığı için bu iki
anlam eşdeğer değildir.

Bu nedenle düzeltilmiş ve yetkili manifestte:

```text
source_compressed_bytes = "NR"
shard = "NR"
reason = "rows API does not expose a genuine source shard or per-record compressed-byte field"
```

İlk manifest kronolojik kanıt olarak korunur ve **non-authoritative** kabul edilir. Düzeltilmiş
manifest bu alanların ölçülmediğini veya API tarafından sağlanmadığını açıkça gösterir; tarihsel
olarak kaydedilmemiş bir transferred/compressed-byte değeri veya gerçek shard bilgisi backfill
etmez.

### 8.2 Near-dedup kapsamı

151h'deki near-dedup sayıları aşağıdaki ayrıştırılmış scope'a aittir:

```text
vngrs internal MinHash-estimated J>=0.80 pairs: 156
trwiki internal MinHash-estimated J>=0.80 pairs: 3,201
vngrs–trwiki cross-source MinHash-estimated J>=0.80 pairs: 0

vngrs internal exact normalized-text duplicate pairs: 14
trwiki internal exact normalized-text duplicate pairs: 563
vngrs–trwiki cross-source exact normalized-text duplicate pairs: 0
```

Cross-source sıfır sonucu yalnızca bu bounded 10.000 + 10.000 kayıt karşılaştırması için
geçerlidir. Tam corpusların sıfır overlap'a sahip olduğunun kanıtı değildir. Near-dedup
implementation'ı 151g'de açıkça dondurulan cap'siz feature scope'una göre çalıştırılmıştır;
başka bir corpus veya full-corpus sonucu ima edilmez.

### 8.3 Scope ve verdict değişikliği yoktur

Full corpus indirilmemiş veya materialize edilmemiştir. Yalnızca açıkça yetkilendirilen bounded
10.000-kayıt vngrs sample'ı edinilmiştir. Bu append-only açıklama 151h'nin vngrs operational /
sample-manifest ve açıkça dondurulmuş near-dedup repair verdict'ini değiştirmez; global
`quality_pass`, frozen corpus selection, `ready_to_train` veya Documents 152--154 yetkisi vermez.
