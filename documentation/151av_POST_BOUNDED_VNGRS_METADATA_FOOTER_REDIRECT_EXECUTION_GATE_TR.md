# Document 151av — Post-Bounded vngrs Metadata/Footer Redirect Execution Gate (TR)

**Date:** 2026-08-09 (Europe/Berlin)  
**Status:** `BLOCKED — HU OPERATIONAL ACCESS`  
**Execution result:** Document 151au

## 1. Decision

```text
decision                    = BLOCKED
operational gate            = blocked_by_operational_access
global scientific gate      = blocked_by_measurement_design
corpus-selection contribution = blocked_by_corpus_selection_or_materialization
ready_to_measure            = false
ready_to_train              = false
```

The wave stopped before HU checkout verification because both the documented SSH route and the
bounded explicit-connect-timeout fallback timed out connecting to `gruenau10.informatik.hu-
berlin.de:22`. The user-prescribed preservation checks therefore could not pass. The wave did
not merge `de4a14e...` into HU, run preflight, run PyArrow, invoke 151an or access any vngrs route.

## 2. Reconciliation table

| Component | Result | Evidence |
|---|---|---|
| local HEAD | PASS | `de4a14e3370326173bdf04ce33356aae7826ddda` |
| remote base | PASS | live `origin/corpus-update = c1a3127a4e4c6d9afd3bb0fd06741ce4114ecf23` before push |
| ordinary publication | PASS | only `c1a3127..de4a14e` pushed, non-force |
| HU HEAD | NOT OBSERVED | SSH transport timeout |
| 42-entry status identity | NOT OBSERVED | current HU status could not be retrieved |
| status SHA / zero overlap | NOT VERIFIED | prior `71a2e3...` / zero overlap retained only as historical baseline |
| HU fast-forward | NOT PERFORMED | preservation gate failed closed |
| storage/path/inode preflight | NOT EXECUTED | HU unreachable |
| independent PyArrow self-check | NOT EXECUTED | HU unreachable |
| 151an executor | NOT INVOKED | pre-source fail-closed stop |
| HTTP/hop/retry/byte/file counts | 0 | no executor invocation or source request |
| post-run HU storage audit | NOT EXECUTED | no HU connectivity |

## 3. Preserved authorities

Documents 151an–151at remain unchanged. Their relevant frozen hashes are:

```text
151an = 937ec22c4b0f32d6c15a43ef872e497a0c62266383d46d2e74fca9069f952b79
151ar = e531443254133a3ade95fcdf004420cc8726d28f337c7171c730937de3019967
151as = 03c603265836320b173489a6659f91916c97db7ec78ebdd7b8faf0c1122a0ceb
151at = d846b3636aa4d55b4fdf95eebf00241ed6c85e6243b3c6a54dbd99bc546576fa
```

No automatic retry, route execution or second wave is authorized by this gate. A future request
must first establish bounded HU SSH reachability and re-run the complete preservation checks; it
must separately authorize any new 151an execution. This blocked result does not authorize corpus
materialization, 151ah/151ak, scoring, inference, evaluation, GPU/Slurm, training or Documents
152–154.

## 4. Append-only recovery gate after HU connectivity restoration

The first transport-timeout decision remains preserved in Document 151au. The subsequent
recovery continuation passed publication, dirty-state preservation, fetch and fast-forward:

```text
published commit              = de4a14e3370326173bdf04ce33356aae7826ddda
HU HEAD after merge            = de4a14e3370326173bdf04ce33356aae7826ddda
status                         = 42 entries (39 tracked .D + 3 untracked)
status SHA-256 before/after   = 71a2e3b1d03a5c73ab3fb16c02e59910b7ec35f553956b079edcf71f3a3c59e9
incoming overlap               = 0
```

The mandatory preflight did not pass because the 30-second `du -xsh` command returned
`returncode=null`, `timed_out=true`, `stdout=0` bytes and `stderr=0` bytes. Although `df -h`,
`df -i`, path resolution and root absence passed, home usage could not be established below
30 GiB. The independent PyArrow self-check was not run, and 151an was not invoked.

The post-run audit was executed and recorded root absence (`0` files / `0` bytes); its `du` and
large-home-file checks also timed out, while capacity/inode/path checks completed. Thus the
recovery gate remains:

```text
decision                 = BLOCKED
primary blocker          = blocked_by_operational_access / mandatory_du_timeout
HTTP attempts/hops       = 0 / 0
retries                  = 0
response bytes           = 0
artifacts/files/inodes   = 0 / 0 / 0
```

No automatic retry is authorized. A future authorization must first provide a bounded, successful
home-usage preflight (or a separately reviewed correction to the preflight route), then rerun all
preservation checks before any new 151an execution. This gate does not claim route unavailability,
corpus selection, quality PASS, `ready_to_measure` or `ready_to_train`.
