# Document 151at — Bounded Hugging Face CDN Redirect Semantics Correction Contract (TR)

**Durum:** `FROZEN — UNEXECUTED — LOCAL IMPLEMENTATION/PUBLIC-METADATA-ONLY CORRECTION`

**Tarih:** 2026-08-09, Europe/Berlin

## 1. Kapsam ve yetki sınırı

Bu belge, Document 151an’ın ilk doğrudan immutable `/resolve/` isteğinin HTTP 302 ile
Hugging Face CDN/Xet konumuna yönlenmesi üzerine hazırlanmış, yalnızca yerel kod ve test
düzeltmesini tanımlar. 151at çalıştırılmamıştır ve çalıştırma yetkisi vermez. 151an’ın
başlangıç metni, 32 shard seçimi, source revision’i, byte/file/inode/wall-clock sınırları
ve önceki sonuç kayıtları değiştirilmemiştir.

Bu hazırlıkta HU/SSH, vngrs route’ları, source/footer/corpus byte’ları, scratch root,
network üzerinden vngrs erişimi, corpus materialization, scoring, inference, model veya
tokenizer erişimi, GPU/Slurm, training, cleanup/deletion ve Documents 151au/151av veya
152–154 kullanılmaz. Bu belge yalnızca sonraki, ayrıca yetkilendirilmesi gereken bir
route-feasibility wave için correction contract’tır.

Korunan kronolojik kayıtların hazırlık öncesi SHA-256 değerleri:

| Belge | SHA-256 |
|---|---|
| 151an | `937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79` |
| 151ao | `5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46` |
| 151ap | `aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468` |
| 151aq | `5a48d297ef5475550df41fd7e2baace4278acf54bbfb32bbfe455909dde7dbea` |
| 151ar | `e531443254133a3ade95fcdf004420cc8726d28f337c7171c730937de3019967` |
| 151as | `03c603265836320b173489a6659f91916c97db7ec78ebdd7b8faf0c1122a0ceb` |

Bu SHA değerleri, 151at hazırlığı sırasında yerel olarak yeniden doğrulanmış ve belgeler
değiştirilmemiştir.

## 2. Resmî Hugging Face dayanağı

Yalnızca resmî Hugging Face dokümantasyonu ve resmî `huggingface_hub` repository source
metadata kullanılmıştır:

1. `huggingface_hub` file-download dokümantasyonu, `/<repo>/resolve/<revision>/<path>`
   download route’unu ve büyük dosyalarda çözümlenen adresin CDN olabileceğini belirtir;
   content-addressed dosya adları nedeniyle immutable revision ile CDN cache’in stale
   olmaması beklenir:  
   <https://huggingface.co/docs/huggingface_hub/en/package_reference/file_download>
2. Resmî `huggingface_hub` test metadata’sı LFS location için `xethub.hf.co` veya
   `cdn.hf.co` beklentisini açıkça kullanır:  
   <https://github.com/huggingface/huggingface_hub/blob/main/tests/test_file_download.py>
3. Resmî `_http.py` source, metadata HEAD çağrılarında `follow_redirects=False` kullanır
   ve yalnız relative redirect’i takip eder; external CDN redirect’ini otomatik takip
   etmez. 151at bu güvenli varsayılanı koruyup, kaynak kimliği ve host suffix’i doğrulanmış
   tek explicit CDN hop ekler:  
   <https://github.com/huggingface/huggingface_hub/blob/main/src/huggingface_hub/utils/_http.py>
4. Hub download dokümantasyonu, `huggingface.co` ile ayrı storage/CDN host’larına HTTP
   redirect olduğunu ve `hf.co`/`huggingface.co` suffix allowlisting seçeneğini açıklar:
   <https://huggingface.co/docs/hub/models-downloading>

Bu web/source metadata incelemesi 2026-08-09’da yapılmıştır. Açık bir immutable upstream
commit SHA’sı bu public HTML/source metadata sayfalarında sunulmadığı için burada `main`
branch’i immutable source revision gibi gösterilmemiştir. Bu kaynaklar vngrs route’una
istek atıldığına veya source bytes alındığına dair kanıt değildir.

## 3. Değişmeyen vngrs source identity

Sonraki wave, yalnızca 151an’da zaten dondurulmuş kimliği kullanabilir:

- repository: `vngrs-ai/vngrs-web-corpus`
- immutable revision: `ee5c6201ee84457a18182bfc483a7d8a7f3655ba`
- split: `train`
- shard count: `284`
- route kind: `parquet_footer_range`
- initial route: `https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/resolve/ee5c6201ee84457a18182bfc483a7d8a7f3655ba/<path>`
- selected paths: exactly the 151an 32-path set, with ordinals
  `00004,00013,00022,00031,00039,00048,00057,00066,00075,00084,00093,00102,00110,00119,00128,00137,00146,00155,00164,00173,00181,00190,00199,00208,00217,00226,00235,00244,00252,00261,00270,00279`
- frozen selection payload SHA-256:
  `dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686`

No path, revision, split, route kind or selection ordinal may be substituted. Dataset Viewer
`/rows` routes remain forbidden.

## 4. Controlled redirect protocol

For each logical HEAD/GET request:

1. Send the exact direct immutable `/resolve/` URL first with the frozen method and Range
   header. Automatic `urllib` redirects remain disabled.
2. Accept a terminal 200/206 response with zero redirects, or exactly one response with
   status **302** and an explicit absolute `Location` followed by one terminal 200/206
   response.
3. The one-hop target must satisfy every condition:
   - absolute URL with `https` scheme;
   - no relative target, userinfo, fragment or explicit port;
   - URL length `1..8192` bytes/characters as represented by the raw header value;
   - normalized host is exactly `xethub.hf.co`/`cdn.hf.co` or a subdomain ending in
     `.xethub.hf.co`/`.cdn.hf.co`;
   - the second response is terminal: a second 302 or any further redirect fails closed;
   - method and Range are preserved exactly.
4. Any 301/303/307/308, missing Location, downgrade, malformed URL, near-match host,
   explicit port, second hop, terminal status mismatch or route identity mismatch is
   `BLOCKED`.  429/503 and no-response transport failures retain their existing logical
   retry rules; a redirect hop is never counted as a retry.

The initial direct URL remains the canonical `request_url` and safe `final_url` in ledgers.
The raw signed CDN URL is used only in memory for the second request and is never written to
logs, reports, JSON artifacts, request rows or exception context.

## 5. Secret-safe redirect evidence

Each accepted redirect is represented inside the existing `redirect_chain` field by exactly
one mapping with exactly these fields:

```text
location_sha256
scheme
host
path_sha256
url_length
query_keys
```

`location_sha256` hashes the exact raw Location header in memory; `path_sha256` hashes the
parsed target path; `scheme` is `https`; `host` is normalized lowercase; `url_length` is the
raw Location length; and `query_keys` is a sorted list of query-key names. Query values,
signatures, credentials and cookies are never persisted. Cross-host requests explicitly strip
`Authorization` and `Cookie` headers. The redirect chain has cardinality zero or one and
all fields are validated again before a successful result can enter the ledger.

The raw terminal URL is not part of the persisted `AttemptResult` evidence graph. `final_url`
continues to mean the canonical direct route, while terminal response headers, Content-Length,
ETag/LFS OID, Content-Range, Parquet trailer/footer bytes and parsed footer metadata bind the
returned object to the original immutable identity. A signed CDN URL alone is never sufficient
evidence.

## 6. Bounded accounting and output surface

151at separates the following quantities:

- logical request/attempt rows: at most `121` (`97` base logical requests plus at most `24`
  logical retries);
- physical HTTP hops: at most `242` (`121` terminal/retry request attempts × two possible
  hops);
- redirect hops: at most one per logical attempt and never a retry;
- retries: at most `24`, retaining 429/503/no-response semantics;
- total response bytes: at most `64 MiB`;
- single non-redirect response: at most `4 MiB`;
- wall clock: at most `7,200` seconds;
- output files and new inodes: at most `128`.

The existing seven top-level outputs and existing evidence/retry artifacts are retained. No
new redirect file is introduced. The final audit must reconcile:

```text
logical_request_attempt_count = request_ledger row count
redirect_hop_count            = sum(len(row.redirect_chain))
http_hop_count                = logical_request_attempt_count + redirect_hop_count
retry_count                   = number of retry rows / retry ordinal transitions
```

The audit must state `max_logical_request_attempts=121`, `max_http_hops=242`, and
`redirect_hop_retry_separation=true`. Any mismatch or bound overflow is `BLOCKED` before
the package is accepted.

## 7. HTTPError response-read correction

The local executor’s nested `HTTPError` response-read handler is corrected so the outer
`http_error` object is not shadowed by the inner read exception. A bounded body-read failure
now fails closed with:

- `phase=response_read_failure`;
- original `http_status` preserved (for example 503);
- compact `response_read_exception` type context;
- no retry artifact or fabricated successful response.

It must not fall through to `unexpected_executor_error`, lose the original status, or persist
the error body beyond the existing response-byte rules.

## 8. Verification performed locally

The focused command was:

```bash
PYTHONPATH=src python3 -m pytest -o addopts='' -q tests/test_vngrs_preparation.py
```

It passed with `66 passed, 2 skipped in 12.12s` after adding one-hop success, method/Range
preservation, secret-redaction, two-hop/unsafe-target negative controls and HTTPError read-failure
regression coverage; the only skips are the existing PyArrow-dependent local checks.

The compatible repository command was:

```bash
PYTHONPATH=src python3 -m pytest -o addopts='' -q tests --ignore=tests/test_m1_cross_family.py
```

It passed locally with `305 passed, 9 skipped in 28.43s`. The sole exclusion is an
environment-only collection failure because the local Python environment lacks `yaml`; no source
or public vngrs route was contacted.

The implementation was committed locally in one narrow follow-up commit after verification:
`de4a14e3370326173bdf04ce33356aae7826ddda`. The published three-commit chain was not amended,
force-pushed or published.

## 9. Decision and next authorization

151at is a **preparation PASS / execution BLOCKED** contract: the local protocol and tests are
ready, but no source-route feasibility claim follows from them. The prior 151an operational gate
remains `blocked_by_operational_access` until a separately authorized wave can perform the
mandatory HU preflight and source access. The global gate remains
`blocked_by_measurement_design`; redirect acceptance alone does not close it, authorize 151an,
authorize 151au/151av, authorize corpus materialization, or authorize training.

Only a future explicit authorization may execute a corrected bounded wave. That future wave
must preserve 151an–151as, use the existing new-root rule from 151an, perform mandatory
storage/path/inode and independent-writer preflight, and create any result/gate documents only
if separately authorized. Documents 151au/151av remain reserved and uncreated.
