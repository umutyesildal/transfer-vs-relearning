# Document 151bq — vngrs Clustered-Window Sample Design and Execution Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — SINGLE BOUNDED SAMPLE WAVE`

## 1. Gerekçe ve değişen estimand

Document 151bo, Document 151ak'nın 10.000 shard-wide systematic midpoint kaydının 5.696 row
group'ın 5.664'üne ve seçilmiş compressed byte'ların `%99.8622`'sine dokunduğunu gösterdi. Bu
kontrat o estimand'ı sessizce sürdürmez. Bounded transport'u önceliklendiren yeni bir
**stratified clustered-window calibration estimand** dondurur.

Bu değişiklik sample-quality sonucundan önce yapılır. Eski systematic sonuçla karşılaştırılabilir
veya aynı estimand olduğu iddia edilemez.

## 2. Frozen population ve allocation

Source identity, immutable revision, 32 selected shard, exact footer/root/hash bağları Documents
151bk/151bl/151bn/151bo ile aynıdır. Target tam 10.000 raw record kalır. Shard sample counts exact
row-count ağırlıklı integer largest-remainder allocation ile hesaplanır; current accepted rows'ta
her shard `312` veya `313` record alır ve toplam exact 10.000 olur.

Her shard dört disjoint integer row stratum'a bölünür:

```text
stratum_start(k) = floor(k * N / 4)
stratum_end(k)   = floor((k + 1) * N / 4), k = 0..3
```

Shard sample count dört cluster'a integer largest-remainder ile eşit dağıtılır; her cluster
`78` veya `79` contiguous row içerir. Tam 32 × 4 = 128 window/request üretilir.

## 3. Precommitted randomized start ve inclusion weights

Tek randomization seed `42`, schedule version
`vngrs_stratified_clustered_windows_32x4_v1`'dir. Her `(path, stratum)` için SHA-256 digest:

```text
sha256("vngrs_stratified_clustered_windows_32x4_v1|42|<path>|<stratum>")
```

unsigned big-endian integer'a çevrilir ve valid start count'a modulo uygulanır. Start, kendi
stratum'u içinde cluster'ın bütünü sığacak biçimde seçilir. Windows shard içinde disjoint'tir.
Response veya quality sonucuna göre start, length, shard veya seed değiştirilemez.

Her sampled row için conditional inclusion probability tam hesaplanır:

```text
valid_starts = stratum_size - cluster_length + 1
covering_starts(row) = valid starts whose window contains row
pi(row | selected shard/stratum) = covering_starts(row) / valid_starts
weight = 1 / pi
```

Primary descriptive rate, 32-shard selected population için Horvitz–Thompson total'ın bilinen
population row count'a bölünmesidir. Bu ağırlık selected 32 shards dışındaki release'i temsil
ettiği iddia edilmez. Uncertainty, 128 windows'u cluster olarak tutan seed-42, 2.000-replicate
cluster bootstrap ile ayrıca raporlanır ve design-unbiased CI olarak adlandırılmaz.

## 4. Transport ve bounds

Exact schedule herhangi bir row response öncesinde canonical JSON olarak yazılır. İzin verilen
tek row transport route'u, exact immutable source/shard/window binding'i kanıtlayabilen route'dur.
Dataset Viewer `/rows` yalnız response exact selected shard path ve immutable revision'a
bağlanabiliyorsa kullanılabilir; global split offset'i shard identity yerine geçirilemez.
Parquet range route kullanılırsa yalnız 128 scheduled cluster'ı kapsayan exact row-group/column
ranges açılabilir; full shard GET yasaktır.

```text
successful windows/row requests = exactly 128
maximum total attempts           = 160
maximum retries                  = 32
maximum rows per response        = 79
maximum one response             = 4 MiB
maximum total response bytes     = 256 MiB
exact raw records                = 10,000
selected shards                  = exactly 32
network concurrency              = 1
wall clock                       = 3,600 seconds
```

Transport route bu sınırlar ve exact shard binding ile execution öncesi çözülemezse source request
başlamadan `BLOCKED` olur. Bound sonucu görülerek büyütülemez.

## 5. Evaluation ve output

Document 151ak'nın frozen normalization, exact composite source identity, LID, deterministic
quality/PII diagnostics, contamination, exact/near-dedup, overlap, split ve text-free compact
manifest kuralları korunur. Heuristic quality/PII evaluator scope'u kapsamlı sınıflandırıcı olarak
sunulamaz. Missing frozen LID/evaluator identity veya benchmark overlap evidence final PASS'i
bloklar.

Fresh root:

```text
/vol/tmp2/yesildau/luna_vngrs_clustered_sample_calibration_v1
```

Schedule, request ledger, 10.000-row text-free record manifest, weighted/unweighted metrics,
cluster-bootstrap ledger, artifact manifest ve final audit yazılır. Raw text kalıcı output'a
yazılmaz. Root mevcutsa invocation başlamaz.

## 6. Decision ve yasaklar

PASS yalnız bu yeni clustered-window calibration estimand'ı için geçerlidir. PASS vngrs'i
otomatik selected/materialized/training-ready yapmaz; 151ah download/materialization ayrı exact
contract gerektirir.

Bu belgenin hazırlanması publication, HU/SSH, network, corpus row/range request, 151ak/151ah
execution, model/tokenizer, GPU/Slurm, training, cleanup veya deletion yetkisi değildir. Tek wave
ancak Document 151bq exact SHA-256'sına bağlı yeni kullanıcı izniyle çalıştırılabilir. Documents
151br/151bs result/gate için ayrılmıştır.

## 7. Effective preparation gate

Local schedule/allocation/inclusion-weight implementation ve structural tests tamamlanmış olsa da
exact immutable shard-window response üretecek transport adapter henüz frozen değildir. Dataset
Viewer global offsets selected shard identity'nin yerine kullanılamaz; Parquet range extraction
ise exact column-chunk/range ledger ve bounded reconstruction/decoder gerektirir.

```text
design status           = FROZEN
schedule implementation = READY LOCALLY
transport adapter       = UNRESOLVED
execution status        = PREPARATION_BLOCKED
source requests         = NOT AUTHORIZED
```

Bu nedenle Document 151bq için henüz execution authorization istenmemelidir. Önce aynı 128 window
schedule'ını değiştirmeden exact transport route, response-byte projection ve decoder integrity
kanıtı ayrı append-only correction ile dondurulmalıdır.

## 8. Official API route audit

Hugging Face'in current official Dataset Viewer documentation'ı `/rows` için yalnız `dataset`,
`config`, `split`, `offset` ve `length` parametrelerini (length maksimum 100) tanımlar. Immutable
revision veya original Parquet shard path parametresi yoktur. Response split-global `row_idx`
verir; original selected shard identity sunmaz. Bu nedenle official `/rows` route'u bu contract'ın
exact immutable 32-shard binding'ini tek başına karşılamaz.

Official `/parquet` endpoint ise dataset'in auto-converted `refs/convert/parquet` dosya URL'lerini
listeler. Bu conversion files, frozen original revision/path/object setiyle aynı source identity
olarak varsayılamaz. Ayrı conversion provenance/reconciliation olmadan original selected shards
yerine kullanılamaz.

Primary references:

- `https://huggingface.co/docs/dataset-viewer/rows`
- `https://huggingface.co/docs/dataset-viewer/parquet`

Bu official API audit mevcut `PREPARATION_BLOCKED` kararını güçlendirir; network execution
yapılmamıştır.
