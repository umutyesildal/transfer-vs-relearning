# Document 151bb — Post-Execution Gate for Revised-Base 151an/151at Wave (TR)

**Tarih:** 2026-08-10  
**Gate:** `BLOCKED`  
**Related result:** Document 151ba

## Decision

The revised-base publication and preservation-checked HU synchronization passed, but the
corrected 151ax mandatory preflight did not complete. The primary exact-byte home check
`du -x -B1 -s /vol/fob-vol6/mi25/yesildau` timed out at its frozen 120-second bound before
the source stage. The human-readable `du -xsh` diagnostic also timed out at its 30-second
bound in that preflight. Because live `<30 GiB` usage was not established before execution,
the wave is fail-closed `BLOCKED`.

The later mandatory post-run audit completed successfully after no output root had been
created. That audit PASS confirms preservation and post-run storage state; it does not turn
the failed preflight into a PASS and does not authorize a retry.

## Gate ledger

| Gate | Result | Evidence |
|---|---|---|
| remote base / ancestry | PASS | live base `2ff1cac...`; merge-base same; local ahead 2, remote ahead 0 |
| ordinary publication | PASS | only `2ff1cac...92460a0` was pushed, non-force |
| HU dirty-state preservation | PASS | 42 entries, 39 `.D`, 3 untracked, 6,989 bytes, SHA `71a2e3...c59e9` |
| incoming path overlap | PASS | 2 incoming paths, overlap `0` |
| one HU fast-forward | PASS | final HU HEAD `92460a00ec136dd885b4940184bee9d954da9106` |
| corrected exact-byte preflight | BLOCKED | 120-second timeout, no parseable value |
| PyArrow self-check | NOT RUN | preflight blocked |
| 151an/151at executor | NOT RUN | preflight blocked; invocations `0` |
| post-run storage audit | PASS | root absent, 0 files/0 bytes, reconciliation PASS |

## Current authority

The narrow operational gate remains `blocked_by_operational_access`; the global scientific
gate remains `blocked_by_measurement_design`. `ready_to_measure` and `ready_to_train` are
false. PASS on the publication/synchronization or post-run audit subchecks does not close
the route-feasibility gate, does not select vngrs, and does not authorize corpus acquisition,
sample calibration, materialization, scoring, evaluation or training.

Documents 151ay and 151az remain preserved historical fail-closed records. No automatic
retry is authorized. A future wave requires a new explicit authorization, a successful
bounded corrected preflight, and the same single-execution/fail-closed protections.

## Append-only post-wave remote observation

After the authorized wave, a local read-only check observed both local `corpus-update` and
`origin/corpus-update` at `210e47256a499d098da9879d7ade990527cdbe35`. This was not part of the
authorized `2ff1cac...92460a0` push and no additional push, fetch, merge, HU access or executor
invocation was performed in response. The gate remains the result of the already completed wave:
`BLOCKED` at corrected preflight. The pre-observation SHA-256 of 151bb was
`0038ff7e6dbe169207a3c1849a69df229000864c3e9c6dc98f7966c27b4723c4`.
