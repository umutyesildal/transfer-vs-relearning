# vngrs M2 D0 source-registry and storage discovery v1

**Status:** `FROZEN / UNEXECUTED`  
**Execution authorized:** no  
**Created:** 2026-08-27

## Purpose

Close two remaining inputs needed to qualify the three-model vngrs D0 contract without reading a
corpus row or writing on HU:

1. derive the exact 32-object full-byte SHA-256 registry from the already accepted immutable
   Git-LFS identities in one compact metadata ledger; and
2. record current scratch filesystem byte/inode capacity plus exact proposed-root absence.

This is discovery evidence only. It does not materialize vngrs, qualify D0, or authorize M2.

## Exact remote input

Exactly one existing file may be opened:

`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1/shard_metadata_ledger.jsonl`

Its required SHA-256 is
`6c6f27651945043ec2dfbf1b26575f416b5d38a8783d0a22320f0ffbf83d3fa3`.
The file must be a regular file no larger than 4 MiB. The only allowed file operations are exact
`stat`, `sha256sum`, and one bounded byte read after both checks pass. Directory traversal, glob,
`find`, recursive inventory and reads of referenced footer/object artifacts are forbidden.

The returned ledger is accepted only if the committed extractor independently verifies its raw
SHA-256, exact 32-path order, immutable revision, `lfs_oid` identity kind, positive object sizes,
valid SHA-256 identities and exact total object bytes `9,468,474,036`. Git-LFS OIDs are the
authoritative full-object SHA-256 identities; no object hash may be guessed from an ETag, URL or
footer. The derivation reads zero corpus rows and downloads zero full objects.

## Exact filesystem observations

The same single read-only HU pass may perform only these path/filesystem observations:

- resolve `/vol/tmp2/yesildau` and require it to remain under `/vol/tmp2`;
- test that `/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1` is absent, without creating it;
- run byte-capacity `df` and inode-capacity `df` for the resolved parent filesystem;
- record sanitized filesystem, total, used, available and capacity values.

No `du` is run. The existing accepted exact HU-home measurement of `14,689,423,360` bytes and the
30 GiB policy limit are carried as reference evidence only; HU home remains read-only. A later
materialization contract must still freeze a numerical peak-storage requirement derived from this
ledger and pass a fresh scratch capacity/root/job preflight before any download.

## Output

HU writes are exactly zero. If separately authorized and successful, one compact local JSON result
may be created at:

`artifacts/corpora/vngrs_m2_d0/source_registry_storage_discovery_v1.json`

It may contain the 32 path/size/LFS-SHA rows, canonical registry hash, aggregate row/byte metadata,
sanitized `df`/inode values, root-absence result and contract/config/code bindings. It must not
contain raw corpus text, footer bytes, credentials, environment values, signed URLs or unbounded
command output. The raw remote ledger payload is not persisted locally.

## Prohibitions

- no HU write, directory creation, cache, temporary file or log;
- no corpus object/footer read, range request, public HTTP or download;
- no model/tokenizer access, inference, scoring, GPU, Slurm, training or evaluation;
- no Git push/pull/fetch, HU repository synchronization or branch publication;
- no cleanup, deletion, move, chmod, retry, alternate path or expanded inventory;
- no claim that D0 is qualified, materialization-ready or training-ready.

## Execution boundary

Preparation and local testing do not authorize HU/SSH. One later user instruction must quote the
exact final SHA-256 of this contract and authorize exactly this single read-only one-file plus
filesystem-metadata pass. There is no automatic retry.
