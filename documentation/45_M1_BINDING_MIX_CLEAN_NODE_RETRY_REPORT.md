# 45 - M1 Binding Mix Clean-Node Retry Report

Date: 2026-07-09
Last checked: 2026-07-10 08:36 CEST

Status: superseded; job `389721` was cancelled at user request on 2026-07-10.

## Purpose

This report records the retry that keeps the memory-safe relaunch config but excludes the
contaminated HU node discovered during the first recovery attempt.

## Why Another Retry Was Needed

The memory-safe relaunch job (`389719`) still failed with CUDA OOM, but the failure
signature showed that the node itself was polluted by unrelated GPU workers.

Observed node-level evidence on `gruenau10`:

```text
42818, VLLM::Worker_TP0, 78064 MiB
42819, VLLM::Worker_TP1, 78064 MiB
```

Owner of the reported PID:

```text
UID=serbetco PID=42818 CMD=VLLM::Worker_TP0
```

Interpretation:

- the second OOM is not strong evidence against the memory-safe recipe
- the allocated A100 was effectively unusable because most of its memory was already
  occupied by non-project processes on `gruenau10`

## Retry Strategy

Keep the same training config:

```text
configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc.yaml
```

Change only the scheduler placement:

- exclude node: `gruenau10`

## Slurm Retry

Training job:

```text
389721
```

Current Slurm state:

- state: `PENDING`
- reason: `Resources`
- excluded node: `gruenau10`
- scheduler-projected start: `2026-07-12 01:43:30`
- projected end if started on time: `2026-07-12 05:43:30`
- requested resources: `1 x A100 80 GB`, `8 CPUs`, `64 GB RAM`
- runtime limit: `4:00:00`
- current priority: `11106`

## Monitoring Update - 2026-07-10 08:36 CEST

Live checks with `squeue`, `squeue --start`, `scontrol`, and `sprio` confirmed that job
`389721` has not started and has not produced training results yet. At the time of this
check, the projected start was approximately 41 hours away. This is a scheduler backfill
estimate and may move as cluster availability changes.

No scientific comparison can be made until the job starts, finishes, and the English
direct plus QA-matched evaluations are run on its checkpoint.

## Current Decision

Given the external GPU contamination on the default A100 node, leaving this retry pending
for a later clean slot is acceptable and scientifically cleaner than forcing another run on
the polluted node.

## Superseding Update - 2026-07-10

Later inspection showed that `gruenau10` had become clean and idle, while all three A100s
on `gruenau9` were allocated. Excluding `gruenau10` therefore removed the only immediately
eligible node and caused the misleading 41-hour backfill estimate. Job `389721` was
cancelled and replaced by job `389939`; see report `46_M1_BINDING_MIX_CLEAN_NODE_RELAUNCH_REPORT.md`.
