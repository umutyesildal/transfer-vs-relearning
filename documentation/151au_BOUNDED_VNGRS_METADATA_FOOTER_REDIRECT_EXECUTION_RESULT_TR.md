# Document 151au — Bounded vngrs Metadata/Footer Redirect Execution Result (TR)

**Date:** 2026-08-09 (Europe/Berlin)  
**Worker:** LUNA-Worker 2  
**Status:** `BLOCKED — ONE AUTHORIZED WAVE, FAIL-CLOSED`  
**Contract:** Document 151an, unchanged SHA-256  
`937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79`  
**Redirect semantics:** Document 151at, unchanged SHA-256  
`d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa`

## 1. Scope and publication result

This was the single user-authorized wave. The reviewed local follow-up commit was published by
ordinary non-force push:

```text
local HEAD before push       = de4a14e3370326173bdf04ce33356aae7826ddda
origin/corpus-update before  = c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
push result                  = c1a3127..de4a14e corpus-update -> corpus-update
HU merge target              = de4a14e3370326173bdf04ce33356aae7826ddda
```

Only the reviewed `de4a14e...` follow-up was published. No force push, amend, rebase, cleanup,
artifact-directory staging or other commit publication occurred.

## 2. HU transport and preservation gate

The documented helper was invoked for a read-only status/HEAD check. It produced no remote output
and the SSH transport timed out before a HU command was evidenced. A second bounded read-only
fallback used `ConnectTimeout=20`, one connection attempt, `ServerAliveInterval=10` and
`ServerAliveCountMax=2`; it also reported:

```text
ssh: connect to host gruenau10.informatik.hu-berlin.de port 22: Operation timed out
```

Consequently, the current HU checkout could not be re-read. The following values are historical
baselines from Documents 151aq/151ar, not current-wave observations:

```text
last recorded HU HEAD          = c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
last recorded status entries   = 42 (39 tracked .D + 3 untracked)
last recorded status bytes     = 6989
last recorded status SHA-256   = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
last recorded incoming overlap = 0
```

For this wave, HU HEAD, the 42-entry status identity/classification, the status digest and the
overlap are `NOT OBSERVED — SSH TRANSPORT TIMEOUT`. No merge was attempted. No restore, reset,
checkout, switch, stash, clean, deletion or overwrite occurred.

The local incoming path set for `c1a3127..de4a14e` was:

```text
src/transfer_vs_relearning/corpora/vngrs/manifest.py
src/transfer_vs_relearning/corpora/vngrs/metadata.py
src/transfer_vs_relearning/corpora/vngrs/metadata_executor.py
tests/test_vngrs_preparation.py
```

Its overlap with the current HU status cannot be claimed because the current status was not
retrieved. This failed closed before any HU mutation or source request.

## 3. Preflight and executor accounting

The mandatory HU storage/path/inode preflight and the independent PyArrow writer/parser self-check
were not run: HU transport failed before the checkout could be inspected. Therefore home usage,
resolved scratch paths, frozen-root absence and PyArrow availability are all `NOT OBSERVED` for
this wave. The executor was not invoked.

```text
logical request attempts       = 0 (executor not invoked)
physical HTTP hops             = 0
HTTP retries                   = 0
response bytes                 = 0
retained evidence artifacts    = 0
new output files/inodes        = 0
corpus rows/full shards        = 0
```

The frozen root
`/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1` was not accessed or written in
this wave. Its prior absence recorded by 151ar is historical evidence only; a current inventory
could not be performed.

## 4. Post-run audit and decision

The required HU post-run storage/path/inode audit could not be executed because the wave never
passed the HU transport gate. No source/footer route was contacted, no redirect was followed and
no artifact or audit payload was generated. The local result is therefore:

```text
result                 = BLOCKED
primary blocker        = blocked_by_operational_access
blocker detail         = HU SSH transport timeout before status/preflight
final audit            = NOT GENERATED — pre-source fail-closed stop
post-run HU audit      = NOT EXECUTED — HU unreachable
ready_to_measure       = false
ready_to_train         = false
```

This result does not establish vngrs route availability or unavailability and does not change the
global `blocked_by_measurement_design` gate. No corpus was selected or materialized, and no
training, scoring, inference, evaluation, GPU/Slurm, model/tokenizer access or Documents 152–154
action occurred.

## 5. Append-only recovery attempt after HU connectivity restoration

The first transport-timeout record above is preserved unchanged. After the user reported that HU
connectivity had been repaired, one recovery continuation was attempted before any source request.
Its pre-merge preservation checks passed:

```text
HU HEAD before merge             = c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23
status entries                   = 42
tracked .D                      = 39
untracked                       = 3
status bytes                    = 6989
status SHA-256                  = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
incoming path overlap           = 0
origin/corpus-update after fetch = de4a14e3370326173bdf04ce33356aae7826ddda
```

Only `origin corpus-update` was fetched and exactly one ordinary `git merge --ff-only
de4a14e3370326173bdf04ce33356aae7826ddda` was performed. After the merge, the dirty-state digest
remained byte-for-byte unchanged:

```text
HU HEAD after merge              = de4a14e3370326173bdf04ce33356aae7826ddda
status SHA-256 after merge      = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
status entries after merge      = 42 (39 tracked .D + 3 untracked)
```

The mandatory storage preflight then failed closed. The executor's frozen 30-second command bound
returned the following exact evidence for `du -xsh /vol/fob-vol6/mi25/yesildau`:

```text
returncode = null
timed_out  = true
stdout     = 0 bytes
stderr     = 0 bytes
```

`df -h`, `df -i` and `readlink -f /vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1`
completed with exit 0; the frozen root was absent. `home_usage_bytes` remained null, so the
home `<30 GiB` gate was not proven. The independent PyArrow writer/parser check was
`SKIPPED_PRE_FLIGHT`, and the executor was not invoked. The required post-run audit was still
run: the root remained absent with `file_count=0` and `total_bytes=0`; its `du` and large-home-file
checks also timed out at the 30-second bound, while `df -h`, `df -i` and path resolution completed.

The recovery result is therefore also `BLOCKED` before source access. No HTTP request, redirect,
retry, response byte, evidence artifact, corpus row or full shard was retrieved. The HU checkout
and dirty-state remained preserved; no cleanup, restore, reset, deletion or overwrite occurred.
