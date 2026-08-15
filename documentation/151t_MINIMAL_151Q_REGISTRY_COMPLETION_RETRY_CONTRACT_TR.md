# Document 151t — Minimal 151q Registry-Completion Retry Contract

**Tarih:** 2026-08-07 (Europe/Berlin)  
**Durum:** **UNEXECUTED — FROZEN — RETRY_EXECUTION_NOT_AUTHORIZED**  
**Öncül contract:** Document 151q  
**Öncül result/gate:** Documents 151r/151s  

## 1. Amaç ve kanıt bütünlüğü

Bu belge, Documents 151r/151s'de fail-closed kalan tek dar registry-completion eksikliğini
gidermek için hazırlanmış minimal, yerel olarak freeze edilmiş ve henüz çalıştırılmamış bir retry
contract'ıdır. Bu belge hazırlanırken HU/SSH, network, public HTTP, retry execution, scoring,
inference, model/tokenizer artifact erişimi, corpus işlemi, GPU/Slurm, training, cleanup veya
deletion yapılmamıştır.

İlk execution'ın kararı geçerlidir: immutable EXAMS yolu
`data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz` için response 32 MiB sınırına
takılmıştır. Yerel hazırlık kanıtında beklenen resmi artifact boyutu `38,208,781` byte olarak
korunur; bu değer önceki 32 MiB sınırını `4,654,349` byte aşar. Bu, route'un kullanılamadığını
veya bilimsel bir model sonucu oluştuğunu göstermez.

Bu retry yalnızca:

1. eksik EXAMS `test_with_para` artifact'ını;
2. fail-closed duruştan sonra alınmamış üç exact source-model public model-card metadata
   response'unu

alabilir. İlk wave'de doğrulanmış TurBLiMP, TurkishMMLU ve beş retained EXAMS artifact'ı yeniden
indirilemez; yalnızca read-only integrity reconciliation başarısız olursa execution doğrudan
`BLOCKED` olur ve yeni bir kaynak seçimi veya replacement yapılamaz.

Bu belge benchmark scoring veya capability measurement sözleşmesi değildir. Başarılı bir retry
sadece registry-completion evidence'ını tamamlayabilir; `blocked_by_measurement_design`,
`ready_to_train` veya training authorization durumlarını kapatamaz.

## 2. Korunacak önceki kayıtlar ve path sınırı

151q, 151r ve 151s değiştirilmeden ve mevcut SHA-256 değerleri korunarak tarihsel kayıt olarak
kalır:

| Belge | SHA-256 | Durum |
|---|---|---|
| 151q final third-correction | `f1cdfe082a78fce612d7bc53766e88dae3182ffcf52a225f2aa81e24c2491561` | executed once; immutable contract record |
| 151r | `09ffb44bea8711e7c9e37dd7a4c5cea93d9c277f552bdc50bc556fdf55facfe8` | historical preliminary/provisional result |
| 151s | `cec364cf21716a186311d243094f669b998bd2cf558a02bd21fcb3438be61950` | historical blocked gate |

İlk execution root'u mevcut haliyle read-only ve immutable'dır:

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_v1
```

Retry için freeze edilen yeni root şudur; bu local preparation'da root oluşturulamaz:

```text
/vol/tmp2/yesildau/luna_benchmark_model_metadata_registry_completion_retry_v1
```

Retry root'u yalnızca gelecekteki ayrı ve açık execution authorization kapsamında yeni dosyalar
için kullanılabilir. Hiçbir mevcut sample, report, manifest, ledger, cache veya evidence dosyası
overwrite edilemez. HU home'a, 151q/151r/151s'nin bulunduğu root'a, önceki audit/repair/Phase-1
root'larına veya repository çalışma ağacına execution çıktısı yazılamaz.

## 3. Dondurulmuş source set ve exact request planı

Bu retry source set'i genişletmez. Response-dependent source, revision, task, failed-source
replacement, mirror veya fallback seçimi yasaktır.

### 3.1 Missing EXAMS request

```text
source_id = benchmark.turkish_exams
repository = https://github.com/mhardalov/exams-qa
immutable_commit = f859e665de6c370f6214ca5f36a34ace36ada6cb
path = data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz
request_url = https://raw.githubusercontent.com/mhardalov/exams-qa/f859e665de6c370f6214ca5f36a34ace36ada6cb/data/exams/cross-lingual/with_paragraphs/test_with_para.jsonl.tar.gz
expected_transferred_bytes = 38208781
expected_size_status = frozen_from_prior_local_evidence
```

Bu retry'da `data/exams/cross-lingual/test_tr.jsonl.tar.gz` veya başka bir EXAMS yolu
istenemez. Artifact tam response olarak, archive extraction veya expanded corpus yazılmadan
retained edilebilir. Exact SHA-256 execution sırasında tam response üzerinden hesaplanmalı ve
manifest/hash ledger'a yazılmalıdır; önceden bilinmeyen hash uydurulamaz. Transferred byte,
serialized file byte ve storage byte ayrı alanlardır.

### 3.2 Skipped source-model metadata requests

Yalnızca aşağıdaki üç immutable model-card response'u alınabilir. Model ağırlığı, tokenizer,
snapshot veya config tree indirme isteği yapılamaz.

| request order | source_id | exact repository @ revision | exact metadata URL |
|---:|---|---|---|
| 2 | `model.olmo_2_0425_1b` | `allenai/OLMo-2-0425-1B @ a1847dff35000b4271fa70afc5db10fd29fedbdf` | `https://huggingface.co/allenai/OLMo-2-0425-1B/blob/a1847dff35000b4271fa70afc5db10fd29fedbdf/README.md` |
| 3 | `model.falcon_rw_1b` | `tiiuae/falcon-rw-1b @ e4b9872bb803165eb22f0a867d4e6a64d34fce19` | `https://huggingface.co/tiiuae/falcon-rw-1b/blob/e4b9872bb803165eb22f0a867d4e6a64d34fce19/README.md` |
| 4 | `model.qwen2_5_1_5b` | `Qwen/Qwen2.5-1.5B @ 8faed761d45a263340a0528343f099c05c9a4323` | `https://huggingface.co/Qwen/Qwen2.5-1.5B/blob/8faed761d45a263340a0528343f099c05c9a4323/README.md` |

Bu üç card dışında 151q'da tanımlı repository, paper veya corpus-documentation kimlikleri
yalnızca first-wave frozen route metadata olarak read-only reference edilebilir; bu minimal retry
yeni URL seçemez. Üç model row'unun zorunlu provenance alanları bu üç card ve önceden frozen
route metadata ile eksiksiz kurulamazsa sonuç `BLOCKED` olur; eksik alan `zero_turkish_exposure`
olarak doldurulamaz.

### 3.3 Deterministic order and no replacement

Execution başlamadan önce aşağıdaki dört logical request'in tamamı sabitlenmeli ve ordered plan
olarak yeni root'a yazılmalıdır:

```text
retry-0001 = benchmark.turkish_exams / test_with_para.jsonl.tar.gz
retry-0002 = model.olmo_2_0425_1b / frozen README.md
retry-0003 = model.falcon_rw_1b / frozen README.md
retry-0004 = model.qwen2_5_1_5b / frozen README.md
```

Exact plan, runtime/code version ve plan SHA-256 ilk HTTP request'ten önce kaydedilmelidir.
Response-dependent request selection, başarısız request yerine başka sayfa/path koyma ve
duplicate source ID kabulü yasaktır. Her logical request aynı exact URL/revision ile en fazla
frozen retry sayısı kadar tekrarlanabilir; yeni source veya path eklenemez.

## 4. Frozen operational bounds

Bir HTTP retry veya redirect dahil her gerçek HTTP attempt request ledger'a bir row olarak yazılır.
Response body streaming sırasında aşağıdaki bound aşılırsa body retained edilmeden wave fail-closed
olur. Bound'ların hiçbiri preparation sırasında uygulanmadı; bunlar yalnızca gelecekte ayrı yetki
verilen execution için dondurulmuştur.

```text
max_total_http_requests = 8
max_total_retries = 4
max_redirects_per_logical_request = 2
max_single_response_bytes = 50331648          # 48 MiB
max_single_retained_file_bytes = 50331648     # 48 MiB
max_total_response_bytes = 67108864           # 64 MiB
max_total_retained_bytes = 67108864           # 64 MiB
max_new_regular_files = 64
max_new_storage_bytes = 134217728             # 128 MiB, all retry-root files
max_wall_clock_seconds = 900
```

48 MiB single-file/response bound, doğrulanmış `38,208,781` byte EXAMS artifact'ı için sınırlı
safety headroom'dur; genel download veya archive allowance değildir. `max_total_response_bytes`
ve `max_total_retained_bytes` model-card metadata ve küçük ledger/report dosyalarıyla birlikte
64 MiB'de tutulur. Herhangi bir request, retry, redirect, response, retained-byte, file, storage
veya wall-clock bound ihlalinde execution `BLOCKED` olur; bound artırmak için aynı contract içinde
karar verilemez.

Retry yalnızca aynı frozen URL için transient transport/HTTP failure durumunda ve toplam retry
sınırı içinde yapılabilir. 4 retry hakkı dolduğunda, HTTP 429/5xx sürdüğünde, redirect frozen URL
dışına çıktığında veya response status/encoding/byte hesabı doğrulanamadığında wave fail-closed
olur. Başarısız EXAMS request'i başka bir dosyayla, başarısız model-card request'i başka bir
repository ile değiştirilemez.

## 5. Zorunlu preflight ve immutable-root reconciliation

Gelecekte execution yetkisi verilirse, HU'ya erişmeden önce `ssh-client/README.md` ve AGENTS.md'de
tanımlı storage/path/inode preflight eksiksiz uygulanmalı; home, `/vol/tmp`, `/vol/tmp2`, ilk root,
retry root path ve inode durumu kaydedilmelidir. Retry root'un önceden var olması, path mismatch,
symlink ile HU home'a çözülme veya immutable root inventory değişikliği fail-closed koşuludur.

First-wave evidence read-only olarak yeniden doğrulanır ve kopyalanmaz. Yeni root'ta aşağıdaki
reconciliation ledger'ı, reused artifact'ın önceki root'taki absolute/relative path'ini,
first-wave manifestteki byte/SHA değerini, read-only gözlem sonucunu ve hangi yeni registry row'una
provenance verdiğini göstermelidir:

```text
reconciliation/first_wave_reuse_ledger.jsonl
```

Bu ledger, TurBLiMP, TurkishMMLU ve beş retained EXAMS artifact'ı için first-wave kayıtlarını;
ilk root'un path/size/SHA inventory eşitliğini ve 151r'de raporlanan
`4e06a47ddf58a81a3d6a86e4dc0dee75c0d123ff6b38dbda6d76e7be51daf3ad` root listing hash'ini
reference etmelidir. Read-only reconciliation başarısızsa hiçbir reused evidence yeniden
oluşturulamaz ve wave `BLOCKED` olur.

## 6. Zorunlu execution deliverables and schemas

Retry root yalnızca aşağıdaki yeni bounded evidence'ı yazabilir:

```text
contracts/retry_preflight_manifest.json
requests/retry_request_plan.json
requests/retry_request_ledger.jsonl
manifests/retry_file_manifest.jsonl
manifests/retry_hash_ledger.jsonl
reconciliation/first_wave_reuse_ledger.jsonl
registries/retry_benchmark_registry.jsonl
registries/retry_source_model_registry.jsonl
registries/retry_coverage_matrix.jsonl
reports/retry_registry_completion_report.json
reports/retry_registry_completion_report.md
reports/retry_post_run_storage_audit.json
```

### 6.1 Request ledger

Her logical request, redirect ve retry dahil her actual HTTP attempt için zorunlu alanlar:

```text
request_id
request_sequence
logical_request_id
source_id
source_url
immutable_revision
request_method
request_start_utc
response_end_utc
http_status
retry_count
response_transferred_bytes
content_encoding
response_sha256
local_retained_path_or_null
outcome
code_runtime_version
```

`response_transferred_bytes` request-level'dir. Aynı response byte count'u birden fazla artifact
row'una kopyalanamaz ve record/file byte toplamı gibi tekrar toplanamaz. Failed veya unretained
response'lar da ledger'a yazılmalıdır.

### 6.2 File and hash manifest

Her retained EXAMS archive veya model-card response için:

```text
artifact_id
source_id
artifact_kind
source_url
immutable_revision
source_path
local_relative_path
exact_serialized_file_bytes
retrieved_at_utc
http_status
content_encoding
sha256
first_wave_reuse_status
```

`retry_hash_ledger.jsonl` aynı artifact ID'nin tekilleştirilmiş SHA/byte kaydını ve hash hesaplama
runtime'ını içerir. Partial response, truncated file, missing timestamp, missing hash, path
substitution veya byte mismatch retained artifact olarak kabul edilemez.

### 6.3 Registry and coverage

`retry_benchmark_registry.jsonl` üç zorunlu benchmark row'unu; `retry_source_model_registry.jsonl`
üç exact model row'unu üretmelidir. First-wave verified rows read-only provenance linkiyle
referanslanır; EXAMS missing artifact ve üç model-card hash'i yeni evidence olarak işaretlenir.

Her row için minimum identity, revision, exact path/URL, split/task, item/evaluator identity,
license/access, byte/SHA, retrieval timestamp, status ve provenance reference alanları gerekir.
Model rows ayrıca base/instruction status, training stage, tokenizer status, documented corpus /
language mixture, explicit Turkish evidence ve conservative Turkish-evidence status alanlarını
taşımalıdır. Turkish exposure dokümante edilmemişse `not_reported` veya
`Turkish_exposure_not_resolvable` yazılır; sıfır varsayımı yapılamaz.

`retry_coverage_matrix.jsonl` her required entity-field için row üretmelidir; yalnızca başarılı
alanları raporlamak yasaktır. Status vocabulary 151q ile aynı kalır:
`verified`, `not_reported`, `not_retrieved_in_this_wave`, `not_applicable`, `access_blocked`,
`conflicting_primary_sources`, `excluded_with_reason` ve `blocked`. Duplicate entity/source
ID, missing mandatory field veya status/coverage mismatch doğrudan `BLOCKED`'dır.

## 7. Fail-closed decision rules

Retry result'ı ancak bütün aşağıdaki koşullar sağlanırsa `PASS` olabilir:

- EXAMS artifact exact frozen path/revision ile tam alınmış, `38,208,781` byte beklentisiyle
  tutarlı, tam response SHA-256 ve manifest timestamp'i mevcut;
- üç model-card response'u exact frozen model ID/revision/URL ile alınmış ve üç source-model
  row'unun mandatory provenance alanları tamamlanmış;
- first-wave TurBLiMP/TurkishMMLU/beş EXAMS artifact'ı read-only reconciliation ile korunmuş;
- request/file/hash/reuse/registry/coverage manifestleri complete ve internally consistent;
- duplicate ID, route/revision/path substitution, byte/hash/timestamp mismatch veya herhangi bir
  frozen operational bound ihlali yoktur;
- post-run storage audit yeni root ile sınırlı yazımı ve immutable roots'ın değişmediğini gösterir.

`CONDITIONAL` yalnızca exact identity/revision/item/evaluator evidence complete olup
non-gating contextual fields `not_reported` veya `not_applicable` kaldığında kullanılabilir;
zorunlu artifact, source-model provenance veya coverage alanı eksikse `CONDITIONAL` kullanılamaz.

`BLOCKED` koşulları: missing/partial EXAMS artifact, üç model row'undan birinin eksikliği,
first-wave reuse mismatch, duplicate ID, response-dependent selection, failed-source replacement,
manifest/coverage eksikliği, byte/hash/timestamp/path/revision mismatch, herhangi bir request/retry/
response/file/storage/time bound ihlali veya unauthorized write. Bu koşullarda retry gate'i
`blocked_by_operational_access` olarak raporlanır; önceki 151s kaydı değiştirilmez.

Bu contract başarılı olsa dahi `blocked_by_measurement_design` secondary/global gate'i açık kalır.
Benchmark overlap/contamination definitions, 713/829 reconciliation'ın ölçüm tasarımındaki
kalan kapsamı, missing pattern/alias inventory, benchmark scoring/evaluator execution ve Turkish
capability measurement bu retry'nin dışındadır. `ready_to_train = false` kalır; training,
capability measurement veya Documents 152--154 için yeni ve ayrı authorization gerekir.

## 8. Reserved result/gate documents and authorization boundary

Gelecekteki retry execution sonucu için, index'te boşsa şu belgeler rezerve edilir; bu preparation
turn'unda oluşturulmaz:

```text
Document 151u — minimal registry-completion retry execution result
Document 151v — post-retry registry-completion decision gate
```

Bu contract Document 151q, 151r veya 151s'nin yerine geçmez ve onları yeniden çalıştırmaz. 151u/v
ancak yeni retry root'ta tamamlanan execution evidence'ı ile ve kullanıcının ayrı, açık bir
execution authorization'ı kapsamında oluşturulabilir. Bu turdaki tek yetki yerel contract
hazırlığı, freeze ve hash hesaplamasıdır; retry execution yetkisi verilmemiştir.

**Freeze status:** `151t_execution_authorized = false`; `retry_root_created = false`;
`151u_status = RESERVED_UNCREATED`; `151v_status = RESERVED_UNCREATED`.

---

## APPEND-ONLY ROUTE CORRECTION — 2026-08-07

### Correction identity and preserved pre-correction hash

Bu addendum, Document 151t'nin önceki gövdesini yeniden yazmaz. Önceki gövdede bulunan üç
Hugging Face `/blob/<revision>/README.md` route'u tarihsel olarak korunur; execution için effective
route overlay aşağıda append-only olarak tanımlanır.

```text
correction_type = immutable_huggingface_model_card_resolve_route
pre_correction_151t_sha256 = eef968538b2022250803504ba1f206860c053663bb9ce74f761c3ae25c4c11cc
151t_execution_status = UNEXECUTED
151u_status = RESERVED_UNCREATED
151v_status = RESERVED_UNCREATED
```

### Effective model-card URL override

Önceki 3.2 tablosundaki yalnızca `exact metadata URL` alanı aşağıdaki immutable `/resolve/`
route'larıyla override edilir. Model ID, repository, immutable revision, request order ve diğer
151t alanları değişmez:

| request order | source_id | effective immutable model-card URL |
|---:|---|---|
| 2 | `model.olmo_2_0425_1b` | `https://huggingface.co/allenai/OLMo-2-0425-1B/resolve/a1847dff35000b4271fa70afc5db10fd29fedbdf/README.md` |
| 3 | `model.falcon_rw_1b` | `https://huggingface.co/tiiuae/falcon-rw-1b/resolve/e4b9872bb803165eb22f0a867d4e6a64d34fce19/README.md` |
| 4 | `model.qwen2_5_1_5b` | `https://huggingface.co/Qwen/Qwen2.5-1.5B/resolve/8faed761d45a263340a0528343f099c05c9a4323/README.md` |

Bu üç `/resolve/` URL'si dışında model-card fallback URL'si, `/blob/` URL'si, mirror, yeni
repository, yeni scientific source, model ağırlığı, tokenizer file, snapshot veya repository
checkout eklenemez. Önceki `/blob/` URL'leri yalnızca tarihsel pre-correction evidence'tır ve
gelecekteki retry request planında effective source URL olarak kullanılamaz.

### Required raw-artifact integrity checks for the later retry

Gelecekte ayrı yetkiyle çalıştırılacak retry, üç model-card response'u için şunları zorunlu
kılmalıdır:

1. `/resolve/` response'unun raw `README.md` bytes'ı retained edilmeli ve tam byte dizisi için
   SHA-256 hesaplanmalıdır; browser presentation HTML hash'lenemez.
2. Request ledger, `final_response_url`, ordered `redirect_chain`, HTTP status, `content_type`,
   `content_encoding`, transferred byte count ve response SHA-256 alanlarını kaydetmelidir.
3. Final response body HTML presentation page, login/error page, partial/truncated body veya
   raw README olmayan bir Hub page ise response retained edilmeden wave fail-closed olmalıdır.
4. Redirect chain veya final response, frozen repository/revision/path ile eşleşmiyorsa; immutable
   revision/path doğrulanamıyorsa; response byte/hash/manifest alanlarından biri eksik veya
   tutarsızsa model row `BLOCKED` olmalı ve retry gate'i `blocked_by_operational_access` olarak
   raporlanmalıdır.

Bu correction yalnızca Hugging Face artifact route ve buna bağlı raw-response integrity alanlarını
düzeltir. EXAMS request'i, request order, 151t'nin tüm request/retry/byte/file/storage/wall-clock
bound'ları, yeni retry root'u, first-wave reconciliation, prohibitions ve reserved 151u/151v
outputs aynen kalır. Bu addendum 151t'yi çalıştırmaz, retry root'u oluşturmaz ve 151u/151v'yi
oluşturmaz.
