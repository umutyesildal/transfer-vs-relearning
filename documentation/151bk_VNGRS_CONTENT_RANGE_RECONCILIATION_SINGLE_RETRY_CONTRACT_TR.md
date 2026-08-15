# Document 151bk — vngrs Content-Range Reconciliation and Single Retry Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — EXACT SHA-BOUND AUTHORIZATION REQUIRED`

## 1. Gerekçe ve tek amaç

Documents 151bi/151bj, exact authorized 151bh invocation'ının immutable README/license HTTP-307
repair'ını geçtiğini, fakat completed-package validator'ın bütün trailer/footer request rows için
`Content-Range is not reconciled` hatası verdiğini kaydeder. Tek 151bh invocation tüketildi ve
output root absent kaldı.

Local root-cause inspection exact protocol mismatch'ini bulmuştur:

```text
request Range syntax       = Range: bytes=START-END
response Content-Range     = Content-Range: bytes START-END/TOTAL
historical validator       = incorrectly expected bytes=START-END/TOTAL
```

Bu kontrat yalnız response `Content-Range` grammar'ındaki yanlış eşittir işaretini düzeltir.
Source, shard, footer parser, quality, sampling veya materialization kararı değişmez.

## 2. Frozen source ve wave identity

Documents 151an/151at/151bh'den aşağıdaki alanlar aynen korunur:

```text
repository        = vngrs-ai/vngrs-web-corpus
revision          = ee5c6201ee84457a18182bfc483a7d8a7f3655ba
split             = train
selected shards   = exact frozen 32-path midpoint set
license route     = exact immutable README + one same-origin 307 resolve-cache hop
corpus rows       = 0
scratch root      = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

151bh sonrası root absent olduğu için aynı root bir kez daha kullanılabilir; execution başında
absent olması zorunludur. Önceki evidence roots ve HU home read-only kalır.

## 3. Exact protocol correction

Validator trailer ve complete-footer success rows için exact canonical response değerlerini
hesaplar:

```text
trailer Content-Range = bytes (object_size-8)-(object_size-1)/object_size
footer Content-Range  = bytes (object_size-footer_length)-(object_size-1)/object_size
```

Buradaki `bytes` sonrasında tek ASCII space vardır; `=` yoktur. Request `range_header` kuralları
değişmez:

```text
trailer Range = bytes=-8
footer Range  = bytes=START-
```

Missing/malformed unit, wrong start/end/total, `bytes=...` response formu, wildcard total,
multi-range, whitespace/case drift, payload-length mismatch veya object-size mismatch fail-closed
kalır. Header değeri exact response ledger'a yazılır; secret içermez.

## 4. Implementation ve tests

Append-only local repair yalnız şu yüzeyleri değiştirebilir:

```text
src/transfer_vs_relearning/corpora/vngrs/metadata.py
src/transfer_vs_relearning/corpora/vngrs/metadata_executor.py
tests/test_vngrs_preparation.py
```

Tests en az şunları kanıtlar:

- real HTTP `Content-Range: bytes START-END/TOTAL` positive package PASS;
- request `Range: bytes=...` ile response `Content-Range: bytes ...` ayrımı;
- historical yanlış `Content-Range: bytes=...` rejection;
- wrong start/end/total ve payload mismatch rejection;
- 151bh HTTP-307 semantics, zero-row policy ve bütün mevcut integrity attacks korunur;
- final audit bu Document 151bk'nin exact SHA-256'sına bağlanır.

## 5. Tek future execution wave

Yeni exact SHA-bound kullanıcı yetkisi verilirse yalnız şu sıra çalışır:

1. local focused ve compatible tests;
2. narrow commit, ordinary non-force push;
3. HU live HEAD/status/path-overlap/root preservation;
4. preservation-checked fast-forward only;
5. connectivity ve exact-byte home/cache prewarm;
6. internal storage/path/inode/no-home-write ve PyArrow self-check;
7. exactly one metadata/footer executor invocation;
8. accepted output/final-audit SHA ledger veya honest fail-closed result;
9. post-run Git/home/storage/root reconciliation;
10. reserved Documents 151bl/151bm result/gate.

151bh invocation'ı yeniden sınıflandırılmaz. Bu yeni invocation başarısız olursa automatic retry
yoktur.

## 6. Bounds ve kapsam dışı

Bounds değişmez:

```text
logical attempts <= 121
HTTP hops        <= 242
retries          <= 24
single response  <= 4 MiB
total responses  <= 64 MiB
outputs/inodes   <= 128 / 128
wall clock       <= 7,200 seconds
corpus rows      = 0
```

Corpus row/full-shard retrieval, 151ak, 151ah materialization, corpus selection/quality PASS,
model/tokenizer, scoring, inference, GPU/Slurm, training, cleanup/deletion, source revision/path
change ve ikinci invocation kapsam dışıdır.

Global gate `blocked_by_measurement_design`, contributing gate
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure=false` ve
`ready_to_train=false` kalır. Bu belge tek başına publication, HU/SSH veya execution yetkisi
vermez.
