# vngrs M2 OSCAR fact-translation block repair v1a

**Date:** 2026-08-31
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU PARTITION REPAIR WAVE`
**Contract ID:** `vngrs-m2-oscar-fact-translation-repair-v1a`

## Predecessor result

The exact v1 authorization was consumed once. Publication, preservation-checked HU fast-forward
and the frozen 18-test suite passed. The launcher then failed closed at `sbatch --test-only`
because HU has no partition named `cpu`:

```text
sbatch: error: invalid partition specified: cpu
allocation failure: Invalid partition name specified
```

No real Slurm job was submitted. Read-only verification found zero matching jobs. The first root
contains exactly one 110-byte file, `control/submission_state.json`, with SHA-256
`c65c87e404e287c7925752e7ddd250f7795517c2d2f2d5aa22fdf7ee27d29556` and status
`SUBMISSION_PREPARED`. That root is immutable evidence and must not be reused, changed or cleaned.

## Exact correction

This amendment changes only the operational route:

- partition `cpu` becomes HU's observed valid CPU partition `longrun`;
- the job name becomes `m2-fact-tr-repair-v1a`;
- every output path moves to the fresh root
  `/vol/tmp2/yesildau/vngrs_m2_oscar_fact_translation_repair_retry_v1`;
- the submitter requires the preserved first-root file count and SHA-256 before submission.

The resources remain exactly 4 CPUs, 32G memory and two hours. The corrected fact registry,
tokenizer identities, predecessor manifest, 97,536 blocks per arm, 976 replacement blocks,
scientific operator and every PASS requirement remain unchanged.

## Frozen implementation

```text
config                 d1a1c777cfe66f37a6d02d30c59872890f26b1c206ea04808bb790f9ceec1d16
block repair runner    8d31edee3cd6cbf231292fb7d16bdb9da03191a81dfe4617d4bc7f3af36543e1
Slurm                  385a8f3f841058eda81bc30db1ae1c05ee4de7480516b32d05c5b18f028849fc
submitter              d9c0315214ec32e0ff2247f018cdefc4eea1e9908b42dbca25f1357605b705bc
focused test file      3dd4a5429293b8d53ea3ee20273b58c2558adaeb1f3aa05ef23b1f717f42e86b
```

The compatible local suite passes `19/19`; Python and shell syntax checks pass.

## One separately authorized wave

A later exact SHA-bound instruction may authorize:

1. ordinary non-force push of the exact implementation commit;
2. preservation-checked HU active-checkout fast-forward to that commit;
3. targeted HU tests;
4. exactly one `sbatch --test-only` check and, only if it passes, one real 4-CPU/32G/2h
   `longrun` CPU job;
5. read-only access to the completed predecessor block family and tokenizer snapshots;
6. writes only under the fresh retry root.

PASS requirements remain those of v1: three roles, 250 corrected facts, exact predecessor hashes,
97,536 blocks per arm, 976 scheduled replacements, new corrected M2-B files, terminal
`M2_FACT_TRANSLATION_REPAIR_PASS` and `ready_to_train=false`.

## Authority boundary

This document authorizes nothing by itself. It does not authorize push, HU mutation, Slurm or
tokenizer access until the user quotes its exact final SHA-256 and exact implementation commit.
It never authorizes GPU, model-weight access, optimizer smoke, M2-A/M2-B training, evaluation,
cleanup, deletion, fallback, a second retry or automatic retry. The first root and all predecessor
roots remain preserved read-only.
