# vngrs M2 OSCAR exact block recovery 4-CPU relocation contract v1

**Date:** 2026-08-30  
**Lifecycle:** `FROZEN / UNEXECUTED / CONDITIONAL PENDING-ONLY RELOCATION`  
**Contract ID:** `vngrs-m2-oscar-exact-block-materialization-recovery-4cpu-relocation-v1`

## Purpose

This contract permits one conditional operational relocation of CPU recovery job `482007` only
if it remains `PENDING` at or after 03:00 Europe/Berlin on 2026-08-31. It changes only
`cpus-per-task` from 8 to 4. Memory remains 128G, time limit remains six hours, and every corpus,
split, tokenizer, token-budget, replacement-dose, ordering, output and scientific invariant from
the fail-persistent recovery contract remains unchanged.

The currently queued job was submitted at commit
`6c8c7fa039b7c352e7c9be9236b2a6b9db71fd79`. Its root
`/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_v1` currently contains exactly two
submission records and no progress, log, manifest, fact or block artifact:

```text
control/submission_state.json  242 bytes  sha256 2eb731f41f3fcce810b6c7153ed50ea6823e2cc1a311eb180f794a35756e792c
control/submission_result.json 166 bytes  sha256 2c099abba7d6da631228dee8721bb06bf8a0c7a30aee57ba5f8bf260deccf66b
```

That root becomes immutable/read-only evidence if relocation executes.

## Conditional decision

At the scheduled decision check:

- if job `482007` is `RUNNING`, `COMPLETED`, terminal, absent, or has any progress/log/scientific
  artifact, relocation is forbidden and no queue mutation occurs;
- if job `482007` is still exactly `PENDING`, the two hashes above still match, no progress/log or
  manifest exists, the HU checkout is clean at the old commit, the new commit is fetched and
  proven fast-forward compatible, and test-only/capacity/duplicate gates remain satisfiable, the
  relocation transaction may proceed once;
- failure of any predicate is fail-closed and cannot trigger a second attempt.

## Frozen transaction order

To prevent the pending job from starting between checkout synchronization and cancellation:

1. ordinary non-force push of the amendment commit may occur after exact authorization;
2. at or after 03:00, fetch the amendment commit without changing HU HEAD and prove clean
   fast-forward compatibility;
3. revalidate exact `PENDING` state and the two-file queued-root evidence;
4. apply a user hold only to job `482007` and verify `PENDING / JobHeldUser`;
5. fast-forward the clean HU checkout to the exact amendment commit;
6. run the frozen submitter, which repeats the time, held-pending state, evidence, predecessor,
   source, split, commit, dirty, capacity, duplicate and Slurm test-only gates;
7. cancel only the held/not-started job `482007`, verify it leaves `squeue`, create the new fresh
   root and submit exactly one 4-CPU recovery job;
8. persist the cancelled job/root binding in the new submission state and begin read-only
   monitoring of the new job.

If an unexpected failure occurs after the hold but before cancellation/new submission, job
`482007` remains held and no automatic release, retry or alternative submission is authorized.
This is safer than releasing an old job against a checkout whose commit may have changed.

## Fresh output and resources

```text
new root:    /vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_recovery_4cpu_v1
job name:   vngrs-m2-oscar-blocks-recovery-4cpu-v1
CPUs:       4
RAM:        128G
time limit: 06:00:00
GPU:        none
```

The new root retains the same persistent submission, progress, exception, Slurm stdout/stderr,
`/usr/bin/time -v`, shell-exit and terminal audit rules. Success still leaves
`ready_to_train=false`; it does not open M2 training.

## Frozen implementation

```text
config       3b295a23bb1051adf66e45d3a2151941c972b2ce50c16161274632ec57122ac2
runner       5820113e09e45d5bfb2d2cabb4f9c110fc6c3b5cf123f18f541055b9d2f6f196
streaming    874b4af79966cb7ea142938e729a8f515a0ce5632fe4c8039ecb8a141e77cc36
Slurm        9af50e70ff0c458e7e068538f1e8c5007c7c7a46929b2e41a461b1d32f19851c
submitter    6ffb098d2efafdf61bdfaed8139b03961dbe77e524335fbc829d9348fd351b3e
tests        8d45c08bc0620ab918ba9ed2d6c459355a795e03a9823336245399cd5f5005b5
```

Compatible focused suite: `23 passed`.

## Authority boundary

This document authorizes nothing by itself. Exact SHA-bound user authorization may permit:

- ordinary non-force push of the exact amendment commit;
- the one conditional pending-only hold/cancel transaction above;
- preservation-checked HU fast-forward in the frozen order;
- exactly one new 4-CPU recovery submission and its read-only monitoring.

It does not authorize cancellation of a running/terminal job, a second relocation, automatic
retry/release, GPU, model-weight access, optimizer smoke, M2-A/M2-B training, evaluation, cleanup,
deletion or predecessor mutation.
