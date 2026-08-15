# Document 151bh — vngrs License HTTP-307 Resolve-Cache Repair and Single Retry Contract (TR)

**Tarih:** 2026-08-12, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — EXACT SHA-BOUND AUTHORIZATION REQUIRED`

## 1. Gerekçe ve dar amaç

Documents 151bf/151bg, exact authorized 151be wave'inin connectivity, preservation, storage
preflight, PyArrow self-check ve 32 shard için 96 HEAD/trailer/footer request'ini geçtiğini; son
immutable README/license request'inde HTTP 307 gördüğü için frozen 302-only vocabulary'de
fail-closed durduğunu kaydeder. Tek 151be invocation tüketilmiştir ve output root absent kalmıştır.

Bu kontrat yalnız şu operational sorunu düzeltir:

> Exact immutable vngrs README route'unun Hugging Face same-origin `api/resolve-cache` HTTP
> 307 hop'u secret-safe ve identity-preserving biçimde kabul edilebilir mi?

Corpus quality, row sampling, sample calibration veya materialization sorusu açılmaz.

## 2. Frozen source identity

Değişmeyen source request:

```text
role       = license_attribution
method     = GET
repository = vngrs-ai/vngrs-web-corpus
revision   = ee5c6201ee84457a18182bfc483a7d8a7f3655ba
path       = README.md
source URL = https://huggingface.co/datasets/vngrs-ai/vngrs-web-corpus/resolve/
             ee5c6201ee84457a18182bfc483a7d8a7f3655ba/README.md?download=true
```

32 selected shard, revision, selection order, HEAD/trailer/footer range semantics, footer parser,
response/file/inode/wall-clock bounds ve seven-output package Documents 151an/151at/151ax'tan
değişmeden korunur.

## 3. Yeni ve tek redirect vocabulary

Shard route'ları için mevcut kural değişmez:

- yalnız HTTP 302;
- yalnız exact/suffix `xethub.hf.co` veya `cdn.hf.co`;
- en fazla bir hop;
- method ve Range preservation;
- cross-host Authorization/Cookie stripping.

Yeni kural yalnız `license_attribution` role'üne uygulanır:

1. terminal source response exact HTTP 307 olmalıdır;
2. Location absolute HTTPS veya root-relative olabilir;
3. resolution sonrası scheme `https`, host exact `huggingface.co` olmalıdır;
4. username/password, explicit port ve fragment yasaktır;
5. resolved path exact olarak aşağıdaki değerdir:

```text
/api/resolve-cache/datasets/vngrs-ai/vngrs-web-corpus/
ee5c6201ee84457a18182bfc483a7d8a7f3655ba/README.md
```

6. query key set'i yalnız `etag` veya `download,etag` olabilir; `etag` non-empty, varsa
   `download=true` olmalıdır;
7. query values veya raw Location artifact/ledger/documentation içine yazılmaz;
8. retained redirect evidence yalnız status, route class, Location/path SHA-256, scheme, host,
   URL length ve sorted query-key adlarını içerir;
9. hop aynı logical attempt içindedir, retry değildir ve HTTP-hop ledger'ına ayrı sayılır;
10. ikinci redirect, 301/303/308, 302-on-license, 307-on-shard, foreign host/repo/revision/path,
    duplicate/unknown query key veya method mutation fail-closed'dur.

Final 200 response exact README raw bytes olmalı; empty payload, HTML presentation route,
single/cumulative byte violation veya content read failure BLOCKED sonucudur.

## 4. Implementation binding

Append-only local repair yalnız şu yüzeyleri değiştirebilir:

```text
src/transfer_vs_relearning/corpora/vngrs/metadata_executor.py
src/transfer_vs_relearning/corpora/vngrs/metadata.py
tests/test_vngrs_preparation.py
```

Redirect evidence schema'sına `http_status` ve `route_class` eklenir. Final audit hem historical
151an contract SHA'sına hem bu Document 151bh'nin final SHA-256'sına bağlanmalıdır. Unit tests en
az şunları kanıtlar:

- absolute ve root-relative exact 307→200 PASS;
- GET method preservation ve one-hop/zero-retry accounting;
- raw query-value secret'in retained ledger'da bulunmaması;
- 307 shard, foreign source, wrong path/host, unknown query key ve license 302 rejection;
- existing safe shard 302 semantics ve 121 logical-attempt/242 HTTP-hop bounds preservation;
- validator'ın yanlış status/route-class/path-hash/query-key kanıtını reddetmesi.

## 5. Tek future execution wave

Yeni exact SHA-bound kullanıcı yetkisi verilirse tek wave şu sırayı izler:

1. local focused ve compatible tests;
2. dar commit ve ordinary non-force push;
3. HU live HEAD/status/path-overlap/root preservation checks;
4. preservation-checked fast-forward only; merge/reset/force yasak;
5. bounded connectivity ve exact-byte home/cache prewarm;
6. internal storage/path/inode/no-home-write ve PyArrow self-check;
7. exactly one existing metadata/footer executor invocation;
8. output/final-audit SHA ledger veya honest fail-closed result;
9. post-run Git/home/storage/root reconciliation;
10. reserved Documents 151bi/151bj result/gate.

151be'nin eski invocation'ı yeniden sınıflandırılmaz. Yeni invocation yalnız bu new contract'ın tek
attempt'idir; başarısız olursa automatic retry yoktur.

## 6. Scratch ve bounds

151be sonrası root absent olduğu için frozen root korunur:

```text
/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

Execution başında absent olmalıdır. Limits değişmez:

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

HU home write, prior-root mutation ve cleanup/deletion yasaktır.

## 7. Scope dışı

- corpus row veya full-shard retrieval;
- 151ak sample calibration;
- 151ah acquisition/materialization;
- corpus selection/quality PASS;
- model/tokenizer, scoring, inference, GPU/Slurm veya training;
- source revision/path/shard set change;
- ikinci executor invocation veya outcome-aware retry;
- cleanup/deletion.

Global gate `blocked_by_measurement_design`, contributing gate
`blocked_by_corpus_selection_or_materialization`; `ready_to_measure=false` ve
`ready_to_train=false` kalır. Bu belge tek başına push, HU/SSH, source request veya execution
yetkisi vermez.
