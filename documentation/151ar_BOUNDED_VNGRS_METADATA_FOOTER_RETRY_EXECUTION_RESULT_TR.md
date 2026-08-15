# Document 151ar — Bounded vngrs Metadata/Footer Retry Execution Result (TR)

**Date:** 2026-08-09 (Europe/Berlin)  
**Worker:** LUNA-Worker 2  
**Status:** `BLOCKED — ONE EXECUTION, FAIL-CLOSED`  
**Contract:** Document 151an, unchanged SHA-256
`937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`

## 1. Authorization and preservation boundary

This is the single explicitly authorized preservation-checked fast-forward and 151an retry wave.
Documents 151an, 151ao, 151ap and 151aq were verified before the wave and remain unchanged.
Their final hashes are:

```text
151an  937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79
151ao  5b8cb4be094e78f9e37a927348efab4491e5f00355496f2996d1170494dfae46
151ap  aef81d9b72dd856b802310daaa4c64c7e37089ef22e2527cb6c88bbba8923468
151aq  5a48d297ef5475550df41fd7e2baace4278acf54bbfb32bbfe455909dde7dbea
```

The owner state was preserved in place. No dirty artifact/run path was deleted, restored,
relocated or overwritten. No reset, checkout, stash, clean, force operation or deletion occurred.

## 2. HU Git reconciliation evidence

Before HU mutation, the local and live `corpus-update` publication resolved to
`c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23`. HU was at:

```text
HEAD before fetch/merge = 9f1755219ba003d4aaf962558b3c0512fc74f99a
porcelain-v2 status bytes = 6989
porcelain-v2 status SHA-256 = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
status entries = 42
tracked .D entries = 39
untracked entries = 3
incoming path overlap = 0 of 13
```

The exact three untracked entries were `.codex_pre_pull_backup_20260707T142553Z/`, `artifacts`
and `runs`; the 39 tracked `.D` paths are the unchanged artifact/run paths enumerated in 151aq.

Exactly one allowed fetch was performed:

```text
git -C /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning fetch origin corpus-update
fetch result = origin/corpus-update -> c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
```

After the fetch, the old HEAD was verified as an ancestor and the complete status blob remained
byte-for-byte unchanged (6,989 bytes, SHA-256 `71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9`,
42 entries, zero overlap). Exactly one ordinary fast-forward was then performed:

```text
git -C /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning merge --ff-only c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
result = Fast-forward 9f17552..c1a3127
```

The merge introduced only the 13 reviewed vngrs source/test paths. Immediately afterward:

```text
HU HEAD = c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
status bytes = 6989
status SHA-256 = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
status entries = 42
status unchanged = true
```

## 3. Preflight and independent writer/parser self-check

The synchronized executor ran the mandatory preflight before any public source request. It passed:

| Check | Result |
|---|---|
| `du -xsh /vol/fob-vol6/mi25/yesildau` | exit 0, 30-second bound, stderr 0, `14G`; parsed `home_usage_bytes=15032385536` |
| `du -x -B1 -s /vol/fob-vol6/mi25/yesildau` | exit 0, 30-second bound, stdout 40 B, stderr 0, `14688624640` B |
| home stop threshold | `32212254720` B; not reached |
| `df -h`, `df -i` | all exit 0 |
| resolved root | `/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1` |
| root before execution | absent |

The independent self-check also passed before source access:

```text
writer          = pyarrow 24.0.0
parser          = vngrs_parquet_footer_compact_thrift_parser_v1
status          = PASS
payload_bytes   = 531
payload_sha256  = 9cd10e081f3b5b613267543d78828fe589fc75656035184cf5be3661c9616634
rows            = 2
row_groups      = 1
```

## 4. Single 151an execution and fail-closed result

The frozen executor was invoked exactly once after the successful preconditions. The local shell
mistake described during execution preparation did not invoke HU, did not invoke the executor and
was terminated locally; the only remote executor invocation is the one recorded here.

The first and only source attempt was:

```text
request_id = head_metadata_route-00000
attempt_count = 1
retry_count = 0
total_response_bytes = 0
```

The frozen direct immutable route for shard `train-00004-of-00284.parquet` at revision
`ee5c6201ee84457a18182bfc483a7d8a7f3655ba` returned HTTP `302` with a `Location` on the Hugging
Face CDN. The executor deliberately did not follow that redirect. The contract requires a direct
immutable route with a valid non-redirect response, so it failed closed:

```text
status = BLOCKED
phase = source_request
reason = head_metadata_route-00000: non-retryable HTTP status 302 or invalid response
executor exit code = 3
HTTP attempts = 1
retries = 0
response bytes = 0
retained evidence artifacts = 0
```

No corpus row, row group, full shard, model, tokenizer or benchmark artifact was retrieved. This
is evidence of a frozen-route redirect mismatch, not evidence that vngrs or the route is
unavailable. No retry was attempted because 302 is non-retryable under 151an.

The complete package validator was not reached because the first source request failed before any
contract artifact package existed. The executor did run its fail-closed post-run storage audit.

## 5. Post-run storage audit

The frozen root remained absent after the blocked attempt:

```text
root_exists = false
file_count = 0
total_bytes = 0
resolved_root = /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

The final read-only audit confirmed HU HEAD `c1a3127…`, status SHA-256
`71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9`, 6,989 status bytes and 42
entries. Final capacity/inode checks completed successfully. No output was written to HU home.
The executor’s large-home-file audit listed five existing large files under the approved Conda,
Torch and selected frozen-model locations; this wave created none of them.

## 6. Gate result

```text
151an execution result          = BLOCKED
operational blocker             = frozen direct route returned HTTP 302
current operational gate        = blocked_by_operational_access
global gate                     = blocked_by_measurement_design
ready_to_measure                = false
ready_to_train                  = false
```

The successful HU reconciliation, preflight and independent writer check do not authorize a
second 151an execution. Documents 151ah/151ak, corpus materialization, scoring, evaluation,
GPU/Slurm, training and Documents 152–154 remain outside scope.
