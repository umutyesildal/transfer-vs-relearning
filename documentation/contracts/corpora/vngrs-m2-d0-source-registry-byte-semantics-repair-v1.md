# vngrs M2 D0 source-registry byte-semantics repair v1

**Status:** `FROZEN / UNEXECUTED`  
**Execution authorized:** no  
**Created:** 2026-08-27

## Preserved finding

The authorized direct-pipe pass delivered the complete 732,929-byte ledger in memory, verified its
frozen SHA-256 and passed all 32 path/order/revision/LFS/positive-size checks. It then failed closed
at the aggregate gate: the ledger's `object_size_bytes` sum is `9,502,315,428`, while
`9,468,474,036` is the distinct sum of Parquet row-group `compressed_bytes`. The difference is
`33,841,392` bytes of object-format/header/page/metadata overhead. Historical Document 151bo
already defines `9,468,474,036` as a row-group compressed-byte projection rather than exact HTTP
object bytes. No registry was accepted and no raw ledger/transcript was persisted.

## Sole semantic repair

This repair separates the two immutable aggregates without changing any source row:

| Field | Required value | Role |
|---|---:|---|
| full-object bytes | `9,502,315,428` | materialization/HTTP/size gate |
| Parquet compressed bytes | `9,468,474,036` | footer/row-group reconciliation gate |

The updated committed extractor requires both totals independently. Every object row must contain
a positive `object_size_bytes` and positive `compressed_bytes`; the LFS OID remains the
authoritative full-object SHA-256. The 10 GiB response ceiling is unchanged and still exceeds the
correct full-object aggregate.

## Exact pass and transport

The HU command and direct in-memory stdout-to-parser route are identical to the consumed capture
pass. Exactly one existing file may be opened:
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1/shard_metadata_ledger.jsonl`.
It must be at most 4 MiB and match SHA-256
`6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` before one bounded read.

The proposed D0 root must remain absent. Byte capacity uses the existing `df -B1` form and inode
capacity uses `df -Pi`. SSH stdout is piped directly to the committed parser. Raw ledger bytes and
the SSH transcript are never persisted. A PASS requires exactly 32 canonical registry rows, both
aggregates above and a canonical registry SHA-256.

HU writes are exactly zero. A successful pass may create only the compact local result
`artifacts/corpora/vngrs_m2_d0/source_registry_byte_semantics_repair_v1.json` through `apply_patch`
after review of compact parser stdout.

## Prohibitions and authority

- no HU write, root creation, cache, temporary file or log;
- no corpus object/footer read, HTTP, download or materialization;
- no model/tokenizer access, inference, scoring, Slurm/GPU, training or evaluation;
- no Git push/pull/fetch, publication, cleanup, deletion or alternate inventory;
- no automatic retry and no D0/materialization/training readiness claim.

Preparation does not authorize HU/SSH. One new user instruction must quote this contract's exact
final SHA-256 and authorize its single read-only pass.
