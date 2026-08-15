# Document 151r — Benchmark ve Source-Model Metadata Registry Execution Result

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Contract:** Document 151q  
**Contract SHA-256:** `f1cdfe082a78fce612d7bc53766e88dae3182ffcf52a225f2aa81e24c2491561`  
**Execution run:** `151q-20260807T174246Z`  
**Durum:** **BLOCKED — `blocked_by_operational_access`**  
**Primary global gate:** **`blocked_by_measurement_design`**  
**Training gate:** **BLOCKED**  
**`ready_to_train`: `false`**

## 1. Yetki ve kapsam

Bu belge, kullanıcının Single Next Authorization Request kapsamında açıkça yetkilendirdiği tek
bounded 151q execution wave'inin sonucudur. HU/SSH, zorunlu storage/path/inode preflight, yalnızca
151q'da frozen public HTTP route'ları, yeni scratch root'a yazım ve post-run storage audit
yapılmıştır.

Şunlar yapılmamıştır ve bu execution tarafından yetkilendirilmemiştir: benchmark scoring,
model inference, model veya tokenizer ağırlığı/snapshot erişimi, corpus materialization,
GPU/Slurm, training, cleanup/deletion, HU home yazımı, eski evidence root'larına yazım,
Documents 151k/151l veya 152--154.

`/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1` execution'ın tek yazma
root'udur. Aşağıdaki önceki root'lar immutable/read-only kalmıştır:

```text
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_v1
/vol/tmp2/yesildau/luna_bounded_provenance_sample_audit_repair_v1
/vol/tmp2/yesildau/luna_phase1_measurement_evidence_resolution_v1
```

## 2. Zaman ve preflight

UTC execution başlangıcı `2026-08-07T17:42:46.900326Z`, bitişi
`2026-08-07T17:43:18.026939Z` olmuştur; bu yaklaşık 31.13 saniyelik execution süresidir.
İlk HTTP request `17:42:48.244205Z`, son response `17:43:02.522413Z` içinde tamamlanmıştır.
Bu ayrım, HTTP response süresini bütün execution/report-generation/storage-audit süresiyle
karıştırmamak içindir.

HU preflight sonuçları:

| Kontrol | Sonuç |
|---|---|
| HU home `du -xsh` | `14G` |
| `/vol/tmp2/yesildau` `du -xsh` | `3.5T` |
| `/vol/fob-vol6` capacity | `1.3T / 667G used / 610G available / 53%` |
| `/vol/tmp` capacity | `140T / 122T used / 18T available / 88%` |
| `/vol/tmp2` capacity | `140T / 27T used / 113T available / 19%` |
| `/vol/fob-vol6` inode | `53%` |
| `/vol/tmp` inode | `3%` |
| `/vol/tmp2` inode | `3%` |
| New root before execution | absent; exact path check PASS |
| Existing roots | present; before/after inventory SHA equal |

Post-run correction audit `reports/post_run_storage_audit_correction.json` aynı `du` değerlerini
doğrulamış, eski root'ların değişmediğini göstermiş ve home üzerinde 5 adet `+500MiB` regular
file gözlemlemiştir. Execution yazma planı home'a yazmadığı için bu dosyalar execution output'u
olarak sınıflandırılmamıştır; ayrıca başlangıçta ayrı bir large-home-file baseline listesi
alınmadığından bu tarama yeni dosya yokluğuna dair bağımsız bir baseline iddiası değildir.

## 3. Execution bound ve fail-closed sonucu

Frozen bounds:

```text
max_total_http_requests = 96
max_total_retries = 16
max_total_response_bytes = 268435456
max_single_retained_file_bytes = 33554432
max_total_new_retained_bytes = 134217728
max_wall_clock_seconds = 1800
max_new_regular_files = 256
max_new_storage_bytes = 536870912
max_redirects_per_request = 5
```

Gerçekleşen değerler:

| Ölçüm | Değer | Durum |
|---|---:|---|
| Planned HTTP requests | 83 | fixed plan; response-dependent seçim yok |
| Actual request-ledger rows | 80 | request bound içinde |
| Retries | 0 | retry bound içinde |
| Response bytes observed | 43,265,866 | total bound içinde |
| Retained bytes | 12,805,516 | retained bound içinde |
| Final root storage | 13,063,617 | 512 MiB bound içinde |
| Final root regular files | 91 | 256-file bound içinde |
| Wall clock | yaklaşık 31.13 s | 1800 s bound içinde |

Wave, fixed EXAMS route'larından biri 32 MiB single-response bound'ını aştığında fail-closed
olmuştur:

```text
source_id = benchmark.turkish_exams
path = data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz
request_id = req-0080
HTTP = 200
observed response bytes = 33,554,432
failure = single_response_bound_exceeded
artifact saved = false
```

Bu nedenle effective operational gate `blocked_by_operational_access`'tir. İlk yürütme raporunun
`operational_gate = PASS` alanı, aynı rapordaki `response_bound_failure` ile çelişmektedir; ilk
rapor değiştirilmemiş, bu çelişki yeni ve append-only
`reports/post_run_storage_audit_correction.json` artifact'ında düzeltilmiştir. Effective gate
kararı bu correction artifact'ını izler.

## 4. Manifest, registry ve coverage sonucu

Ledger ve manifest bütünlüğü:

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `contracts/preflight_manifest.json` | 8,066 | `38c056362cfc8c63180fe3c6ebdf1f25c5c1ae99efd7d70884e5e40d305978f6` |
| `requests/request_plan.json` | 23,595 | `b2a1fac6ba5a9f02cf5f43fbe15afd2fb09cd426f5c0b3097d094c618d11a78a` |
| `requests/request_ledger.jsonl` | 65,781 | `1789ec1fae2474039018786ea714468fb4809511ad15d9a60d20888c4fae68c3` |
| `manifests/file_manifest.jsonl` | 57,094 | `e8e8ff112c07956d035951bae09a6af4642e76416372394390c00ee5c7ed5d88` |
| `manifests/hash_ledger.jsonl` | 13,416 | `7ff233c13cc65c888bce5c1bef55e035571dfad1d68e9d012ac4ee38bd30dee5` |
| `registries/benchmark_registry.jsonl` | 20,447 | `06f3f797014ba58382d94605303b42a449623ce22523155ac3ebcc038f989afd` |
| `registries/source_model_registry.jsonl` | 5,262 | `ac98933957e9ec8595453413ebefda0c8409f5d0a0cd3f3e05cf24a581e745fc` |
| `registries/coverage_matrix.jsonl` | 55,436 | `77f1397f03ec3615af000b2917505a5d964ab817285678bbc920e1bb31ae80cc` |
| `reports/post_run_storage_audit_correction.json` | 4,326 | `4054941581cf9b0c949f8d723bd9dca1027f827406cd8f17715a5b5bf3fd1271` |

Root inventory: 91 regular files, 13,063,617 bytes; deterministic path/size/SHA listing hash
`4e06a47ddf58a81a3d6a86e4dc0dee75c0d123ff6b38dbda6d76e7be51daf3ad`. `file_manifest` ve
`hash_ledger` each have 78 rows: 39 retained item files and 39 generated item-ID manifests.
Model card artifact'ları fail-closed sonrasında alınmadığı için bu wave'de model card SHA'sı
yoktur.

### Benchmark rows

| Entity | Registry status | Retrieved item coverage |
|---|---|---|
| `benchmark.turblimp` | `PASS` component | 16 base CSV; her biri 1,000 item, toplam 16,000 |
| `benchmark.turkishmmlu` | `PASS` component | 9 dev dosyası x 5 = 45; 9 test dosyası x 100 = 900; toplam 945 |
| `benchmark.turkish_exams` | `BLOCKED` | 6 frozen archive route'unun 5'i retained; `test_with_para` bound nedeniyle alınamadı |

EXAMS için retained archive içi in-memory parsing ile beş route'tan 23,664 item ID manifest'e
alınmıştır. Archive extraction veya expanded corpus yazımı yapılmamıştır. `test_with_para`
manifest/hash'i yoktur; bu nedenle Turkish EXAMS entity'si PASS değildir.

CETVEL ve TurkBench, exact task relevance + immutable item route + evaluator revision/code
üçlüsü frozen olmadığı için `excluded_with_reason` olarak korunmuştur; bunlar zorunlu benchmark
yerine geçmez.

### Model rows

`allenai/OLMo-2-0425-1B`, `tiiuae/falcon-rw-1b` ve `Qwen/Qwen2.5-1.5B` için üç registry row'u
`BLOCKED` kalmıştır. Fail-closed EXAMS response'undan sonra model-card request'leri yapılmamış,
model/tokenizer artifact'ı veya inference alınmamıştır. Frozen model ID/revision bilgileri
contract overlay'ından korunmuş olsa da bu wave'in complete source-model provenance chain'i
oluşmamıştır.

Coverage matrix 132 row içerir:

```text
verified = 61
access_blocked = 59
not_retrieved_in_this_wave = 6
not_reported = 0
excluded_with_reason = 6
```

## 5. Gate yorumu ve kalan blocker'lar

Bu execution'ın registry sonucu `BLOCKED`'dır. Başarılı TurBLiMP/TurkishMMLU component row'ları
overall 151q PASS anlamına gelmez. Operational bound failure ve eksik EXAMS/model metadata
nedeniyle 151q completion gate kapanmamıştır.

Primary global gate `blocked_by_measurement_design` olarak korunur. Özellikle aşağıdakiler bu
wave tarafından çözülmemiştir:

- benchmark overlap/contamination definitions;
- 713 versus 829 surface reconciliation'in ölçüm tasarımı bağlamındaki kullanımı;
- missing pattern/alias inventory;
- Turkish capability measurement, benchmark scoring ve model inference.

Bu belge `ready_to_train` değildir ve training, Documents 152--154 veya başka bir measurement
wave'i otomatik olarak açmaz.

## 6. Canonical evidence paths

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/contracts/preflight_manifest.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/requests/request_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/manifests/file_manifest.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/manifests/hash_ledger.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/benchmark_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/source_model_registry.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/registries/coverage_matrix.jsonl
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/reports/registry_completion_report.json
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1/reports/post_run_storage_audit_correction.json
```

151q contract metni değiştirilmeyecek; bu execution sonucu ve gate Document 151s'de korunur.
