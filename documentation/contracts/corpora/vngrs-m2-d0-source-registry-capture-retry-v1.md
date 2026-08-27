# vngrs M2 D0 source-registry local-capture retry v1

**Status:** `FROZEN / UNEXECUTED`  
**Execution authorized:** no  
**Created:** 2026-08-27

## Preserved evidence

The original discovery pass and its first corrected retry are consumed and preserved. The first
stopped at incompatible inode-command syntax. The corrected retry completed every HU-side check:
the ledger remained a 732,929-byte regular file with its frozen SHA-256, the D0 root remained
absent, `/vol/tmp2` had 122,943,170,412,544 available bytes and 2,284,282,885 available inodes.
It emitted the complete compressed ledger, but the generic Codex command-output display truncated
the middle before the local extractor could receive it. HU writes, corpus reads, full-object
downloads and model/GPU actions remained zero. Neither pass derived a registry.

## Sole correction

This contract changes only local transport handling. The exact SSH stdout stream is piped directly
to the committed fail-closed parser
`scripts/corpora/parse_vngrs_registry_discovery_transport.py`; it is not routed through the
bounded human-visible command-output display. The parser:

1. requires exactly one closed marker block and the exact scalar/filesystem schemas;
2. base64-decodes and gzip-decompresses the in-memory ledger;
3. rechecks raw length and SHA-256;
4. invokes `build_source_registry_from_metadata_ledger` for the frozen path/order/revision/LFS/size
   gates; and
5. emits only compact derived JSON while persisting no raw ledger or SSH transcript.

No HU command, scientific rule, ledger, path, byte bound or filesystem observation changes.

## Exact pass

Exactly one existing file may be opened:
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1/shard_metadata_ledger.jsonl`.
It must be at most 4 MiB and match SHA-256
`6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` before its single bounded
read. The resolved parent must be `/vol/tmp2/yesildau`; the proposed D0 root must be absent. Byte
capacity uses `df -B1 --output=source,size,used,avail,pcent,target`; inode capacity uses `df -Pi`.

The source registry must close exactly 32 objects totaling `9,468,474,036` bytes. Git-LFS OIDs are
the authoritative full-object SHA-256 identities. Missing/truncated transport, marker drift,
decode/hash/schema/path/order/revision/LFS/size/total drift, root presence or filesystem mismatch
is `BLOCKED`.

HU writes are exactly zero. A successful pass may create only the compact local result
`artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_capture_retry_v1.json` through
`apply_patch` after reviewing the parser's compact stdout. Raw ledger and SSH transcript are never
persisted.

## Prohibitions and authority

- no HU write, root creation, cache, temporary file or log;
- no corpus object/footer read, HTTP, download or materialization;
- no model/tokenizer access, inference, scoring, Slurm/GPU, training or evaluation;
- no Git push/pull/fetch, publication, cleanup, deletion or alternate inventory;
- no automatic retry and no D0/materialization/training readiness claim.

Preparation does not authorize HU/SSH. One new user instruction must quote this contract's exact
final SHA-256 and authorize its single read-only pass.
