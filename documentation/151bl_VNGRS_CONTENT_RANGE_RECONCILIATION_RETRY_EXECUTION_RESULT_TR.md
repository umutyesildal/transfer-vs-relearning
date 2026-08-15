# Document 151bl — vngrs Content-Range Reconciliation Retry Execution Result (TR)

**Tarih:** 2026-08-13, Europe/Berlin  
**Contract:** Document 151bk SHA-256
`18f9a3c65d7e006a29645bfcef2a26a3d48eb1224291bfe2ca122fafbfc6e4f8`  
**Sonuç:** `PASS — ACCEPTED 32-SHARD METADATA/FOOTER PACKAGE — SINGLE INVOCATION CONSUMED`

## 1. Yetki ve publication

Kullanıcı Document 151bk'nin exact SHA-256'sına bağlı tek bounded vngrs Content-Range
reconciliation retry wave'ini açıkça yetkilendirdi. Shared recovery implementation commit'i:

```text
commit = 68e5be9b1c15a86c8dc8071d55c5de2789600c75
branch = corpus-update
push   = ordinary non-force
```

HU checkout `2c1e49c... -> 68e5be9...` preservation-checked fast-forward edildi. Incoming on path
ile canlı dirty state overlap'i sıfırdı. Existing HU status tam olarak korundu:

```text
status entries = 42
status bytes   = 6,989
status SHA-256 = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
```

Local complete compatible suite `382/382`; HU focused suite `102/102` geçti.

## 2. Prewarm ve execution gates

Execution öncesi root absent'ti:

```text
/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

External read-only prewarm:

```text
home logical bytes (`du -sb`) = 14,545,329,193
home threshold                = 32,212,254,720
large home files              = 5
canonical large-file SHA-256  = 1813b437fdc24610d7102129e0d83911a8f669e9b7cf20ecb467e441ffc7ce95
/vol/tmp2 available bytes     = 123,657,910,222,848
/vol/tmp2 inode use           = 3%
```

Executor internal preflight kendi frozen allocated-byte ölçümünü kullandı ve geçti:

```text
home usage (`du -x -B1 -s`) = 14,691,426,304
PyArrow                     = 24.0.0
independent payload bytes   = 531
independent payload SHA-256 = 9cd10e081f3b5b613267543d78828fe589fc75656035184cf5be3661c9616634
```

İki home değeri farklı `du` semantiğidir; ikisi de 30 GiB stop threshold altında ve kendi gate'i
içinde PASS'tir.

## 3. Exactly-one executor sonucu

Document 151bk repair'ı request `Range: bytes=...` ile response
`Content-Range: bytes START-END/TOTAL` grammar'ını doğru ayırdı. Tek invocation terminal sonucu:

```text
status                  = PASS
phase                   = completed
selected shards         = 32/32
route rows              = 32
logical requests        = 97
HTTP hops               = 194
redirect hops           = 97
retries                 = 0
evidence artifacts      = 97
total response bytes    = 17,047,078
maximum response bytes  = 589,995
corpus rows retrieved   = 0
validator complete      = true
validator errors        = []
```

97 logical request, 32 shard için `HEAD + trailer + complete footer` ve tek README/license
request'idir. Her logical request exact one-hop redirect kullandığı için 194 HTTP hop oluşmuştur.

Final audit exact bağları:

```text
historical metadata/footer contract = 937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79
license HTTP-307 repair              = 57d8dbd0b84f5914e9b249b12d888cb1aa7c2ea6b6733197aaf117dbcb801853
Content-Range repair                 = 18f9a3c65d7e006a29645bfcef2a26a3d48eb1224291bfe2ca122fafbfc6e4f8
selection payload                    = dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686
```

## 4. Accepted output ledger

Root toplam `104` regular file içerir. Regular-file byte toplamı internal audit'te
`18,025,945`; directory entries dahil `du -sb` değeri `18,050,521`'dir. Canonical
`relative_path + size` inventory SHA-256:

```text
120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3
```

Seven top-level output SHA-256 ledger:

| Output | SHA-256 |
|---|---|
| `evidence_artifact_manifest.jsonl` | `046a7c6be52633d60a291d15f791e8054725f289a727e592de66902bc556ca1b` |
| `feasibility_projection.json` | `7680d83fa3662c66aa668c8f641ab726003ce7d29c7082b85a564af55cf91d9c` |
| `metadata_footer_audit.json` | `769cda6c1e57170b6a39818b8fdf79dd65f091e3400131a3a964fd215e2015bb` |
| `request_ledger.jsonl` | `e511df8e3c30501f68e4d868d211c792c0b97d9c40673bd03baf7a0d063d88c1` |
| `route_ledger.jsonl` | `75097ab0187b66e77d9939794b9ed0a23c9df9e1030a88fcfa4d70d48507fc15` |
| `selection_plan.json` | `dbb9714347970634386ff62366384fcae12cf5f12f1df1df676cb9af3ae25686` |
| `shard_metadata_ledger.jsonl` | `6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` |

## 5. Post-run preservation

Internal post-run audit PASS verdi:

```text
files / regular bytes       = 104 / 18,025,945
large-home-file before/after SHA = 02ecc5c4c95191e91e531b3bba22e195a57c7783b1036b9a657b1b32dc2f2e59
added/changed/removed large home files = 0 / 0 / 0
HU HEAD                     = 68e5be9b1c15a86c8dc8071d55c5de2789600c75
HU status before/after      = exact same 42 / 6,989 / SHA-256
cleanup/deletion            = none
```

## 6. Honest result

```text
151bk execution                 = PASS
single invocation consumed      = true
metadata/footer feasibility     = PASS FOR EXACT 32-SHARD SET
accepted evidence package       = true
corpus quality/sample gate       = NOT RUN
151ak sample calibration         = NOT AUTHORIZED
151ah materialization            = NOT AUTHORIZED
global gate                      = blocked_by_measurement_design
contributing corpus gate         = blocked_by_corpus_selection_or_materialization
ready_to_measure                 = false
ready_to_train                   = false
```

PASS yalnız exact metadata/footer/license feasibility bileşenini kapatır. Corpus row/full shard,
sample quality, contamination, yield, selection veya materialization PASS'i değildir.
