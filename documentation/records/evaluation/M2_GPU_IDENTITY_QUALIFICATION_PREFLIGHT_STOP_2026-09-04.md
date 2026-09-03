# GPU identity qualification: preflight path stop

Date: 2026-09-04. Status: BLOCKED before scheduler test-only or submission.

The user authorized contract `vngrs-m2-oscar-gpu-identity-qualification-v1`,
SHA-256 `4221b25cdd61a55751be85e9636b944a490cea441466d142d6a25e3535bbc34e`,
and commit `bde924c4abf44b3878d22e8a860bce10c1ebb047`.
Ordinary non-force publication and clean HU preservation-check/fast-forward completed.
All 34 targeted tests passed locally and on HU. HU contract and module hashes match.

The contract describes the runtime lock as being in the Python's "same directory".
The preflight consequently checked
`/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/environment.lock.txt`.
That path does not exist, so the fail-closed preflight stopped. Capacity and inode checks
were not reached. This is a contract/path issue, not GPU or scientific evidence.

A bounded read-only diagnostic located the 2,247-byte lock at
`/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/environment.lock.txt`.
Its SHA-256 is exactly the frozen expected value
`f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`.
No environment repair, installation or replacement was performed.

The fresh root remains absent, including as a broken symlink. The matching active job-name
query returned no jobs. No scheduler test-only, real submission, GPU initialization, model
load, inference, evaluation, training, cleanup or retry occurred.

The frozen contract is unchanged. A user-approved clarification of the absolute runtime-lock
path and permission to resume the stopped preflight are required before proceeding. All other
identities, resource limits, single-job limit and prohibitions remain unchanged. Existing
21 complete evaluations and 42 failed task records remain untouched.

## Explicit user clarification and continuation

The assistant asked permission to use the absolute environment-root lock path above and
resume the stopped preflight and the same single qualification job. The user answered
"ya hadi güncelle reis!!!1". This authorizes that narrow path clarification and continuation,
not another GPU job or any scientific recovery. The original contract bytes and exact
implementation commit remain unchanged. This append-only clarification supersedes only
the ambiguous "same directory" lock location; the lock SHA-256, Python executable, gate,
fresh root, resource bounds and all prohibitions remain identical.

## Authorized continuation and single submission

The first diagnostic command used system Python 3.6, which rejected subprocess `text=True`
before Git/hash/storage checks; no scheduler call or output creation occurred. The read-only
command was corrected to the documented xfer-relearn Python and compatible subprocess keyword.
The actual gates passed: exact commit, clean HU checkout, all three hashes, absent/non-symlink
fresh root, scratch path resolution and zero matching active jobs. Available scratch bytes were
121,546,723,033,088 and free inodes 2,283,843,948, above the 1 GiB/1,024 bounds.

Exactly one scheduler test-only passed (hypothetical ID 484039). The same resources and wrapped
command were submitted once after rechecking gates and creating only the new root/logs/tmp/cache.
Real job ID: **484040**. At 2026-09-04 00:45:49 cluster time, it was RUNNING on gruenau10,
started 00:45:37, with one A10080GB, eight CPUs, 64G host RAM and ten-minute limit.
Requeue=0 and Restarts=0. Both initial log files were empty.

The wrapped command binds caches/tmp to the fresh root, enables offline/no-bytecode settings,
rechecks exact commit/cleanliness/contract/module/runtime-lock hashes, then invokes the pinned
Python's allocation-local gate exactly once. No CUDA visibility override or model access occurs.
The job limit is consumed; no second submission is authorized.

## Terminal qualification result

Job 484040 FAILED with ExitCode=1:0 after 41 seconds (00:45:37–00:46:18 cluster time).
The persisted audit reports `CUDA device UUID unavailable or unsupported; no index fallback`.
CUDA_VISIBLE_DEVICES and SLURM_JOB_GPUS were both `0`, host gruenau10. The gate reached its
UUID-format/availability check and stopped before CUDA free-memory sampling and SMI probing.
The existing audit does not retain the raw UUID property; therefore absence versus unsupported
representation is unresolved. This result is not evidence of insufficient free VRAM and does
not establish the historical V1B incident cause.

Audit: `/vol/tmp2/yesildau/vnd_m2_oscar_gpu_identity_qualification_v1/gpu_identity_audit.json`.
SHA-256: `727168aa0acddf24c869c6e9b483508c4051a744133ae027289a9f5eb6747917`.
Traceback is preserved in `logs/484040.err` in the same root.
No model load, inference, scoring, training, cleanup or automatic retry occurred.
Qualification is BLOCKED. Next work is a local pinned-runtime UUID representation audit and
a separately authorized qualification repair; the 42-task scientific recovery remains unopened.
