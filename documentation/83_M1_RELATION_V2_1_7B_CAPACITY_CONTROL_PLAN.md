# 83 - M1 Relation V2 1.7B Capacity Control Plan

Last updated: 2026-07-13
Status: precommitted, implementation validation

## Decision

Run the clean Relation V2 100-subject / 500-fact acquisition experiment with
`HuggingFaceTB/SmolLM2-1.7B`. This is the first large-model test of the corrected direct-aware V2
recipe. The historical 1.7B R4 run used the obsolete QA-mix V1 recipe and cannot answer the current
capacity question.

## Scientific Question

Does increasing model capacity from 360M to 1.7B reduce prompt-robust retrieval interference when
data, objective, exposure, optimizer updates, and evaluation remain fixed?

## Frozen Contract

Identical to the clean 360M V2 run:

- 100 subjects and 500 facts;
- five Relation V2 relations;
- seven rows per fact, 3,500 rows total;
- answer-only loss;
- learning rate `1e-4`;
- 36 epochs;
- effective batch 500;
- 252 optimizer updates;
- constant-with-warmup scheduler and 2% warmup;
- no weight decay;
- exact, held-out direct, and held-out QA evaluator;
- gate `450/400/400/350` for exact/direct/QA/overlap.

The only scientific change is base-model capacity:

```text
SmolLM2-360M -> SmolLM2-1.7B
```

For A100 memory safety, the operational batch decomposition changes from micro-batch 50 with
gradient accumulation 10 to micro-batch 10 with accumulation 50. Both have effective batch 500.
Gradient checkpointing is enabled for the 1.7B run. These are memory controls, not changes to the
data or optimizer-step budget.

## Comparison

Primary reference is clean 360M Relation V2 checkpoint 250:

- exact 500/500;
- direct 378/500;
- QA 377/500;
- overlap/triple 329/500.

The 1.7B run passes only under the unchanged full gate. Directional improvements below the gate
are reported but do not retroactively change it. All checkpoints are evaluated because the final
checkpoint need not be best.

## Decision Rule

- Pass: repeat the selected 1.7B checkpoint with a second seed before M1 freezing.
- Strong directional improvement but gate fail: discuss a precommitted 1.7B replication or M1
  subset freeze; do not scale fact count immediately.
- Neutral/regression: conclude that capacity alone does not resolve the V2 retrieval plateau and
  freeze the strongest audited 360M subset for M2/M3.

## Implementation And Launch

- transfer commit: `c85f39b`;
- branch: `corpus-update`;
- local focused tests: 27/27 passed;
- HU focused tests: 27/27 passed;
- verified model: pinned SmolLM2-1.7B snapshot `effd688a12921b4cc83e3312b6feb579f70f9c71`;
- verified data: 3,500 rows, 500 facts, seven rows per fact;
- verified budget: effective batch 500, 252 optimizer updates;
- Slurm job: `393052`;
- first observed state: `RUNNING` on `gruenau9`;
- expected runtime: approximately 35-45 minutes;
- safe runtime range: 30-70 minutes;
- monitoring: no sleep process is active.

## First Launch Failure And Memory-Safe Relaunch

Job `393052` did not complete. It wrote a valid checkpoint 25, then disappeared from Slurm with
an empty stderr and left the run manifest in `started` state. The event occurred exactly at the
first save/evaluation boundary. The checkpoint was written successfully, making the ten-example
training micro-batch less likely to be the failing operation; the first 1.7B validation pass with
evaluation batch ten was initially treated as the strongest OOM candidate. However, the failure
also coincided with the institute's Monday maintenance window described below. OOM therefore
remains a hypothesis rather than a confirmed diagnosis. This is an operational failure and
checkpoint 25 is not interpreted as a scientific result.

The clean relaunch changes only `per_device_eval_batch_size: 10 -> 1`. Evaluation batch size does
not change gradients, effective training batch, optimizer updates, LR, epoch count, or examples.
Training still starts from the pinned base 1.7B model rather than the partial checkpoint.

The memory-safe config was pushed at commit `1559149`. Local and HU focused suites passed 27/27;
the 3,500-row, 500-fact, effective-batch-500, 252-update preflight passed again. Clean relaunch job
`393053` started on `gruenau9`. Because validation now uses batch one, expected runtime outside a
maintenance window is approximately 45-60 minutes with a safe 40-90 minute range.

## 13 July 2026 Maintenance Hold

The HU Informatik service-status page states that regular Monday maintenance runs from 07:00 to
09:00 and can cause short service interruptions or forced user logouts on institute servers. It
also announces central-service updates for 13 July 2026 from 06:00, with possible short DNS and
LDAP interruptions expected to finish after about 20 minutes.

Source: `https://www.informatik.hu-berlin.de/de/org/rechnerbetriebsgruppe/stoerungen`

To avoid mixing infrastructure instability with model behavior, job `393053` was cancelled during
this window. Immediately before cancellation it was `RUNNING` on `gruenau9` with elapsed time
`00:04:36`; after `scancel` it no longer appeared in `squeue`. The run produces no scientific
result and any partial checkpoint must not be resumed or evaluated as part of the capacity control.

At this point the experiment was paused until the user confirmed a restart after the maintenance
window. The next launch was required to start cleanly from the pinned SmolLM2-1.7B base model with
the unchanged memory-safe config at commit `1559149`.

## Post-Maintenance Relaunch

At 08:59:45 CEST on 13 July 2026, the GPU queue contained one unrelated running job and the
cancelled job `393053` was absent. The first post-maintenance submission attempt did not create a
Slurm job because the shared `/vol/fob-vol6` filesystem was at 100% capacity and 100% inode usage;
Git could not update `.git/FETCH_HEAD`. This is an infrastructure/storage condition, not an
experiment failure.

The remote repository was already at the required commit `1559149`. To preserve the scientific
recipe while avoiding writes to the full filesystem, the launch reads the repository, dataset,
environment, and pinned model from their existing locations but writes the runtime config, logs,
caches, checkpoints, and final run artifacts under:

```text
/vol/tmp2/yesildau/m1_relation_v2_1_7b_500
```

The copied runtime config changes only `training.output_root` to the absolute scratch path. The
model, data, answer-only objective, LR, epoch count, batch decomposition, effective exposure,
optimizer-step budget, seed, and evaluator contract remain unchanged. A `.condarc` timestamp
warning was emitted because the home directory remains on the full filesystem, but the job
continued and created its training manifest successfully under `/vol/tmp2`.

- clean Slurm job: `393054`;
- requested and assigned node: `gruenau10`;
- confirmed state: `RUNNING`;
- run manifest: `/vol/tmp2/yesildau/m1_relation_v2_1_7b_500/runs/20260713T070240Z_m1_smollm2_1_7b_relation_v2_100_subjects_500_facts_direct_lr1e-4_ep36_1a413394/training_manifest.json`;
- expected runtime: approximately 45-60 minutes;
- safe observation window: 40-90 minutes;
- monitoring: no sleep process is active.

## Gruenau10 Orphan-Process Failure And Clean Gruenau9 Relaunch

Job `393054` did not reach its first optimizer step. It failed during the first backward pass with
a CUDA OOM. The allocator report showed that the experiment process occupied only approximately
6.68 GiB while another process occupied 72.43 GiB on the assigned A100. Live inspection identified
that process as PID `54819`, user `pahldenn`, command `VLLM::EngineCore`, started on 11 July 2026.
No Slurm job was listed on `gruenau10` at inspection time, so the process was stale/orphaned from
the scheduler's perspective. A second unrelated Firefox process used 87 MiB.

This is not evidence that the 1.7B recipe requires more than an A100 80 GB. Slurm assigned physical
GPU 0 even though that GPU already held approximately 74.2 GiB outside the visible job queue;
physical GPUs 1 and 2 were effectively empty. Job `393054` is therefore an infrastructure-invalid
run and produces no scientific result.

Before relaunch, a short Slurm GPU probe was allocated on `gruenau9`. It received
`CUDA_VISIBLE_DEVICES=0` and reported 14 MiB used, 81,139 MiB free, zero utilization, and no compute
processes. The unchanged experiment was then submitted to that verified node:

- clean relaunch job: `393056`;
- node: `gruenau9`;
- config and output arrangement: unchanged from the `/vol/tmp2` post-maintenance launch;
- first confirmation: `RUNNING` for 1 minute 24 seconds with an empty stderr;
- comparison with failure: job `393054` had already failed after approximately 28 seconds;
- expected runtime remains approximately 45-60 minutes, with a safe 40-90 minute range;
- monitoring: no continuing sleep process is active.

Separately, `/vol/fob-vol6` recovered from 100% capacity/inode usage to 79% during this inspection
(approximately 269 GiB and 70.5 million inodes free). The experiment remains on `/vol/tmp2` so that
the output location does not change again within this run family.

## Completed 1.7B Training And Retrieval Evaluation Launch

Job `393056` completed successfully on `gruenau9`. It executed all 36 epochs and 252 optimizer
updates in 2,827 seconds (approximately 47 minutes 7 seconds). All planned checkpoints were
written: 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, and 252. The final reported training loss
was 0.2784 across the full run; validation loss fell from 0.8397 at the first checkpoint boundary
to 0.006978 near the end and was 0.007413 in the final epoch evaluation. These loss values confirm
successful acquisition optimization but are not the thesis retrieval metrics.

The exact/direct/QA checkpoint sweep was launched with the same 500 facts, probe files, candidate
ranking contract, and full gate used for the 360M reference. Each checkpoint has one evaluation
job that executes all three views. Evaluation configs, model manifests, logs, and results are under
`/vol/tmp2/yesildau/m1_relation_v2_1_7b_500`; jobs are constrained to the previously probed clean
`gruenau9` node.

```text
checkpoint-100 -> 394058
checkpoint-125 -> 394059
checkpoint-150 -> 394060
checkpoint-175 -> 394061
checkpoint-200 -> 394062
checkpoint-225 -> 394063
checkpoint-250 -> 394064
checkpoint-252 -> 394065
checkpoint-25  -> 394066
checkpoint-50  -> 394067
checkpoint-75  -> 394068
```

At first observation, jobs `394058-394060` were running concurrently on the three gruenau9 A100s;
the remaining jobs were pending for those resources. Evaluation stderr logs were empty and no
completed `per_fact_results.csv` files existed yet. No continuing sleep process is active.

All 33 evaluation views later completed successfully. The selected checkpoint 200 achieved
500 exact, 499 direct, 498 QA, 497 direct/QA overlap, and 497 triple successes, decisively passing
the full gate. See `85_M1_RELATION_V2_1_7B_CAPACITY_CONTROL_EVALUATION_REPORT.md` for the complete
checkpoint table, 360M comparison, remaining-error audit, and decision.
