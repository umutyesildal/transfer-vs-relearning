# 46 - M1 Binding Mix Clean-Node Relaunch Report

Date: 2026-07-10
Last checked: 2026-07-10 09:13 CEST

## Purpose

This report records why pending job `389721` showed an implausible 41-hour start estimate,
its cancellation, and the immediate relaunch after verifying that `gruenau10` was clean.

## Cancelled Job

```text
job: 389721
state before cancellation: PENDING (Resources)
excluded node: gruenau10
scheduler-projected start: 2026-07-12 01:43:30 CEST
```

Job `389721` was cancelled on 2026-07-10 at the user's request.

## Root Cause Of The Long Estimate

The GPU partition had only two nodes with the requested A100 80 GB GPU type:

- `gruenau9`: three A100 80 GB GPUs, all three allocated; only about 9.2 GB node RAM free
- `gruenau10`: three A100 80 GB GPUs, Slurm state `IDLE`

There were no active Slurm reservations and no other jobs visible in the GPU partition
queue at the inspection time. The long estimate was not caused by the training recipe.
It was caused by excluding `gruenau10` while `gruenau9` had no available A100.

## Cleanliness Verification

Before relaunch, `gruenau10` reported:

```text
GPU 0: 14 MiB used, 0% utilization
GPU 1: 14 MiB used, 0% utilization
GPU 2: 14 MiB used, 0% utilization
compute processes: none
Slurm state: IDLE
```

The unrelated VLLM workers observed during the earlier failures were no longer present.

## Relaunch

The same memory-safe scientific recipe was resubmitted without excluding `gruenau10`:

```text
config: configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc.yaml
job: 389939
submitted: 2026-07-10 08:40:54 CEST
started: 2026-07-10 08:40:55 CEST
node: gruenau10
state at last check: RUNNING
time limit: 4:00:00
```

The job began one second after submission, confirming the scheduler diagnosis.

## Early Runtime Check

At approximately 2.5 minutes:

- the Slurm job was still running
- the Python training process was alive
- stderr was empty
- the job was loading/tokenizing the 191,637-row, 124 MB binding-mix JSONL dataset
- the GPU had not yet been loaded, which is expected during CPU-side dataset preparation

No training loss or checkpoint result was available at this early check.

At approximately 4.4 minutes, the model had loaded onto GPU 0:

```text
job process: python, PID 2386
GPU 0 memory: approximately 4.25 GB
GPU 0 utilization: 32%
GPU 1 and GPU 2: idle
stderr: empty
```

This confirms that the active GPU process belongs to job `389939` and that the previous
external 78 GB VLLM contamination is absent. The run is healthy through model loading and
early data preparation; the first logged optimizer step is still pending.

## Next Check

Wait until dataset preprocessing completes, then verify:

- GPU memory utilization belongs only to job `389939`
- the first logged training steps and loss are present
- no CUDA OOM occurs
- the projected completion time based on observed step throughput

## Final Training Outcome

Job `389939` completed successfully without CUDA OOM.

```text
status: complete
training runtime: 1313.8635 seconds (21 minutes 54 seconds)
optimizer steps: 879
train blocks: 14,056
eval blocks: 287
final train loss: 1.2978754163
final eval loss: 1.1413165331
```

Retained checkpoints:

- `checkpoint-220`
- `checkpoint-440`
- `checkpoint-660`
- `checkpoint-879`

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts_binding_mix/20260710T064112Z_m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc_8ca27779
```

Training loss decreased strongly and remained stable, but this is not sufficient to pass
the M1 learned-fact gate. Checkpoint-level English direct and QA-matched evaluation is
recorded in report `47_M1_BINDING_MIX_EVALUATION_REPORT.md`.
