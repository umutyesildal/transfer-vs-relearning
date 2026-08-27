# vngrs M2 D0 source-registry and storage discovery retry v1

**Status:** `FROZEN / UNEXECUTED`  
**Execution authorized:** no  
**Created:** 2026-08-27

## Preserved first-pass evidence

The exact authorized `vngrs-m2-d0-source-registry-storage-discovery-v1` pass executed once and is
not retried under its consumed authority. It verified the exact ledger as a 732,929-byte regular
file with the frozen SHA-256, confirmed the proposed D0 root was absent and recorded
122,943,170,412,544 available bytes on `/vol/tmp2`. It then stopped before inode output and ledger
payload return because HU `df` rejects `-i` together with `--output`. HU writes, downloads, corpus
rows and model/tokenizer/GPU actions were zero. The result remains preserved at
`artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_v1.json`.

## Sole correction

This contract preserves every input, bound, prohibition and derivation rule from the first
contract. The only operational change is the inode command:

- rejected first-pass form: `df -i --output=source,itotal,iused,iavail,ipcent,target <parent>`;
- retry form: `df -Pi <parent>`, parsed as the fixed POSIX columns
  `filesystem, 1024-blocks, used, available, capacity, mounted-on`.

The byte-capacity observation remains `df -B1 --output=source,size,used,avail,pcent,target`.
No scientific or corpus rule changes.

## Exact retry scope

Exactly one existing remote file may be opened:

`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1/shard_metadata_ledger.jsonl`

It must be a regular file no larger than 4 MiB and match SHA-256
`6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3` before one bounded payload
read. The proposed root `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1` must remain absent, and its
resolved parent must remain under `/vol/tmp2`.

The committed extractor must independently require the frozen 32-path order, immutable revision,
`lfs_oid` identities, positive sizes and exact total `9,468,474,036` bytes. It derives full-object
SHA-256 identities from the authoritative Git-LFS OIDs with zero corpus-row reads and zero full
object downloads.

HU writes are exactly zero. On success, the retry may replace no evidence; it may create only the
compact local result
`artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_retry_v1.json`.

## Prohibitions and authority

- no HU write, root creation, cache, temporary file or log;
- no corpus object/footer read, HTTP, download or materialization;
- no model/tokenizer access, inference, scoring, Slurm/GPU, training or evaluation;
- no Git push/pull/fetch, publication, cleanup, deletion or alternate inventory;
- no automatic retry and no D0/materialization/training readiness claim.

Preparation does not authorize HU/SSH. A new user instruction must quote this retry contract's
exact final SHA-256 and authorize its single read-only pass.
