# Document 151bd — Post-Execution Gate for Prewarmed HU-Only Retry (TR)

**Tarih:** 2026-08-10  
**Gate:** `BLOCKED`  
**Related result:** Document 151bc

## Decision

The retry stopped before internal 151ax preflight because the bounded HU read-only connection
did not return a remote result. Consequently, the live `92460a0` HEAD, 42-entry dirty-state,
frozen-root absence, large-file manifest and exact-byte home usage were not freshly evidenced.
The previous accepted values were retained as historical context only and were not substituted
for live prewarm evidence.

## Gate ledger

| Gate | Result | Evidence |
|---|---|---|
| HU target commit | NOT OBTAINED | expected/last record `92460a00...`; no fresh remote response |
| dirty-state identity | NOT OBTAINED | expected/last record 42 / 39 `.D` / 3 untracked / SHA `71a2e3...c59e9` |
| frozen root absence | NOT OBTAINED | no fresh remote response |
| large-file priming | NOT OBTAINED | remote command result absent; 120-second bound not evidenced as completed |
| exact-byte priming | NOT OBTAINED | remote command result absent; `<30 GiB` unproven |
| internal 151ax preflight | NOT RUN | priming/connection gate failed |
| PyArrow self-check | NOT RUN | internal preflight not reached |
| executor | NOT RUN | invocation count `0` |
| post-run audit | INCOMPLETE | bounded audit connection timed out before remote result |

The bounded connectivity probe timed out after `30.004 s` with return code `null`, 226 stdout
bytes containing only the SSH spawn line and 0 stderr bytes. The post-run audit probe timed out
after `30.005 s` with return code `null`, 680 stdout bytes containing only the spawn/command
line and 0 stderr bytes.

## Current gate

The operational gate remains `blocked_by_operational_access`; the global gate remains
`blocked_by_measurement_design`. `ready_to_measure` and `ready_to_train` are false. This result
does not establish source unavailability, route failure or corpus quality. It only records that
the authorized retry could not obtain the mandatory live HU prewarm evidence.

Documents 151ba and 151bb remain unchanged. No automatic retry, source/footer HTTP, corpus,
calibration, materialization, scoring, evaluation, model/tokenizer access, GPU/Slurm, training,
cleanup or Documents 153–154 action is authorized by this gate.
