# Document 151bo — vngrs Sample Transport Feasibility Projection Execution Result (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Contract:** Document 151bn SHA-256
`7716fcaf63a30feded65e617107ac3c088ce01a43ca08ac696aeec9936f42110`  
**Sonuç:** `PASS — SYSTEMATIC MIDPOINT TRANSPORT IS EFFECTIVELY FULL-SHARD-LIKE`

## 1. Publication ve preservation

Implementation commit'i `6589f6abae514f9220e1420419f1b4eec914d995` ordinary non-force push
ile yayımlandı ve HU checkout `68e5be9... -> 6589f6a...` preservation-checked fast-forward
edildi. Incoming 10 path ile existing dirty path seti overlap etmedi. HU `-uall` status
fingerprint pre/post tam olarak korundu:

```text
entries = 49
SHA-256 = 8d6c5d44b4a387b29e3803e8bbc122f0dbbabf4ecd9fbe46a82c65c32c6d3297
```

Local focused suite `105/105`, compatible suite `355/355`; HU focused suite exit 0 verdi.

## 2. Exactly-one projection

Source root 104 regular file / 18,025,945 regular-file byte olarak doğrulandı. Yedi accepted
top-level artifact exact SHA bağları, final audit, 32-shard order, row-count ve row-group
reconciliation gate'leri geçti. Output root execution öncesinde absent'ti.

Tek invocation şu artifact'i üretti:

```text
root   = /vol/tmp2/yesildau/luna_vngrs_sample_transport_projection_v1
file   = sample_transport_projection.json
bytes  = 31,554
SHA-256 = c5f4d7a392870528bdd1f2f52da1bb83f6ec8381cb4bf5d095cf142219106ca2
du -sb root = 35,650
```

Execution boyunca network request ve corpus-row/text retrieval tam olarak sıfırdı.

## 3. Projection sonucu

```text
status                         = PASS
target records                 = 10,000
selected shards                = 32
schedule SHA-256               = 5dac087272e5a7dfd5d6797313a936778d166897094b0929720aa0c5dcb6f130
total row groups               = 5,696
touched row groups             = 5,664
contiguous row-group runs      = 32
total compressed bytes         = 9,468,474,036
touched compressed bytes       = 9,455,428,874
touched compressed ratio       = 0.9986222529680706
network requests               = 0
corpus rows retrieved          = 0
exact transport route selected = false
```

Document 151ak'nın exact row-count-weighted systematic midpoint pozisyonları 32 shard'ın her
birinde neredeyse bütün row-group'lara dağılmaktadır. Full touched-row-group compressed-size
projection'ı toplam seçilmiş compressed verinin yaklaşık `%99.8622`'sidir. Bu değer exact HTTP
byte range değildir; column/page/header overhead'i içermez. Buna rağmen mevcut estimand için
row-group-granular Parquet transport'un küçük bounded sample olmadığı açıkça gösterilmiştir.

## 4. Honest interpretation

```text
151bn projection                         = PASS
current 100-request /rows plan           = infeasible (historical minimum 373)
row-group-granular Parquet alternative   = effectively full-shard-like
sample calibration                       = NOT RUN
corpus quality/LID/PII/dedup/overlap     = NOT MEASURED
vngrs selected/materialized              = false
ready_to_measure                         = false
ready_to_train                           = false
```

Bu sonuç sample-quality PASS değildir. Mevcut systematic midpoint estimand'ı korunarak bounded
transport açılamaz; sonraki adım yeni, önceden dondurulmuş sampling/transport design kararıdır.
151ak/151ah, public HTTP, corpus download, materialization veya cleanup yapılmadı.
