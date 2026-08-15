# Document 151bn — vngrs Sample Transport Feasibility Projection Contract (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Durum:** `FROZEN — UNEXECUTED — READ-ONLY SOURCE / ZERO CORPUS ROW`

## 1. Amaç

Document 151bl/151bm exact 32-shard metadata/footer paketini kabul etti. Document 151ak'nın
10.000 systematic midpoint kaydı için dondurduğu 100 `/rows` request sınırı ise structural
control'de en az 373 pencere gerektirdiği için doğrudan çalıştırılamaz. Bu kontrat request veya
byte limitini sonuç görerek büyütmez ve sampling estimand'ını değiştirmez. Yalnız accepted footer
ledger'dan, aynı 10.000 pozisyonun hangi Parquet row group'larına temas edeceğini ve konservatif
compressed-byte taşıma büyüklüğünü hesaplayan tek bounded projection wave'ini tanımlar.

Bu projection corpus sample değildir; hiçbir corpus row veya text byte okumaz.

## 2. Frozen input identity

Tek izin verilen read-only input root:

```text
/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

Zorunlu input bağları:

| Artifact | SHA-256 |
|---|---|
| `evidence_artifact_manifest.jsonl` | `046a7c6be52633d60a291d15f791e8054725f289a727e592de66902bc556ca1b` |
| `feasibility_projection.json` | `7680d83fa3662c66aa668c8f641ab726003ce7d29c7082b85a564af55cf91d9c` |
| `metadata_footer_audit.json` | `769cda6c1e57170b6a39818b8fdf79dd65f091e3400131a3a964fd215e2015bb` |
| `request_ledger.jsonl` | `e511df8e3c30501f68e4d868d211c792c0b97d9c40673bd03baf7a0d063d88c1` |
| `route_ledger.jsonl` | `75097ab0187b66e77d9939794b9ed0a23c9df9e1030a88fcfa4d70d48507fc15` |
| `selection_plan.json` | `dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686` |
| `shard_metadata_ledger.jsonl` | `6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` |

Input root tam olarak 104 regular file / 18,025,945 regular-file byte olmalıdır. Önceki canonical
relative-path-plus-size inventory SHA-256
`120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3` provenance kaydı olarak
çıktıya taşınır; bu kontrat algoritması freeze edilmemiş bir inventory string'ini yeniden üretip
gate olarak kullanmaz. İçerik bütünlüğü exact yedi top-level hash, onların accepted artifact
manifest/audit zinciri ve file/byte cardinality ile doğrulanır. Document 151bk SHA-256
`18f9a3c65d7e006a29645bfcef2a26a3d48eb1224291bfe2ca122fafbfc6e4f8` final audit içinde exact
bağlı kalmalıdır.

## 3. Deterministic projection

Executor şu sırayı izler:

1. Input root ve yedi top-level artifact hash'ini doğrular.
2. Accepted audit'in `PASS/completed`, 32 shard, 0 corpus row ve exact 151bk binding'ini doğrular.
3. Shard ledger'ın frozen 32 path sırasını, positive row counts'u, row-group cardinality'yi ve
   row-group toplamlarının shard row count'a eşitliğini doğrular.
4. Document 151ak'nın exact largest-remainder allocation ve
   `floor((2*rank+1)*row_count/(2*sample_count))` pozisyonlarını yeniden hesaplar.
5. Her pozisyonu cumulative row bounds ile tam bir row group'a bağlar.
6. Her shard ve toplam için touched row-group count, contiguous row-group run count, touched
   compressed bytes, total compressed bytes ve coverage ratio üretir.

`touched_compressed_bytes`, footer'daki full row-group compressed-size toplamıdır. Exact HTTP byte
range veya download maliyeti olduğu iddia edilmez; page/header/index overhead ve column-level
offset eksikliği açıkça korunur. Projection hiçbir ağ isteği üretmez.

## 4. Bounds ve output

Yeni output root:

```text
/vol/tmp2/yesildau/luna_vngrs_sample_transport_projection_v1
```

Kurallar:

```text
exact invocation count     = 1
network requests           = 0
corpus rows/text bytes     = 0
input-root writes          = 0
output regular files       = exactly 1
output file                = sample_transport_projection.json
maximum output bytes       = 1 MiB
maximum wall clock         = 300 seconds
HU home writes             = forbidden
cleanup/deletion           = forbidden
```

Output; contract SHA, implementation commit, input hashes, schedule SHA, exact 32 per-shard rows,
aggregate counts/bytes/ratios, assumptions, limitations ve terminal `PASS` veya `BLOCKED` status
içerir. Atomic fresh-root publication zorunludur; root mevcutsa executor başlamaz.

## 5. Fail-closed karar

Her input/hash/root/schema/cardinality/schedule/byte/output sapması `BLOCKED` olur. `PASS` yalnız
projection'ın reproducible ve evidence-bound olduğunu söyler. `PASS`, `/rows` veya Parquet
transport route'u seçmez; 151ak execution, sample quality, LID, PII, dedup, contamination,
materialization veya training readiness sağlamaz.

## 6. Execution sınırı

Bu belgenin hazırlanması publication, HU/SSH, executor invocation veya yeni output root yazımını
yetkilendirmez. Gelecekte tek wave için kullanıcının bu belgenin exact SHA-256'sını açıkça
yetkilendirmesi gerekir. 151ak/151ah, public HTTP, corpus row/full shard, model/tokenizer,
GPU/Slurm, training, cleanup, deletion ve eski evidence-root mutation kesinlikle kapsam dışıdır.

Documents 151bo/151bp olası execution result/gate için ayrılmıştır.
