# 135 - Qwen M2/M3 Contract And Materialization Status

**Date:** 2026-08-01

**Status:** Phase E contract frozen locally and pushed; Phase F materialization ready for HU CPU
submission

## 1. Decision and scope

The complete two-seed pre-M2 factual/PPL baseline is now available. Before inspecting any M2/M3
outcome, the core first family is frozen as four independently initialized runs:

```text
Qwen M1 seed 42, step 75 -> M2-clean-42 and M3-fact-42
Qwen M1 seed 43, step 50 -> M2-clean-43 and M3-fact-43
```

M2-clean contains generic Turkish material without target synthetic bindings. M3-fact uses the
same block and optimizer budget, replacing deterministic neutral generic-token positions with
complete correct Branch-B Turkish factual sentences. M3-lexical remains optional and is not part
of this first family.

The only previously unresolved scientific dose parameter is now precommitted to **four complete
exposures of all 1,250 Branch-B facts** (`fact_cycles=4`, exactly 5,000 scheduled fact exposures).
This dose was frozen after baseline package completion but before materialization and is not
adapted to any M2/M3 result.

## 2. Frozen execution contract

| Parameter | Frozen value |
|---|---:|
| Block size | 512 tokens |
| Generic training blocks per arm | 2,048 |
| Generic validation blocks | 256 shared blocks |
| Total training-token budget per arm | 1,048,576 |
| Optimizer updates | 128 |
| Learning rate | 1e-5 |
| Train/eval batch | 2 / 2 |
| Gradient accumulation | 8 |
| Warmup | 4 updates |
| Scheduler | constant with warmup |
| Checkpoint/eval schedule | 32, 64, 96, 128 |
| Precision | BF16, gradient checkpointing |
| Seed/data seed | 42/42 and 43/43 |

M2 and M3 share the same M1 artifact, seed, data order, tokenizer, block count, token budget,
optimizer budget, schedule, checkpoint rule, and shared validation set. Only Branch-B factual
exposure differs.

## 3. Frozen outcomes and interpretation rules

The primary metric is TR→EN candidate-ranking top-1. The primary causal contrast is:

```text
(M3-fact - M2-clean)_Branch-B - (M3-fact - M2-clean)_Branch-A
```

Subject-level bootstrap uses 2,000 samples with seed 20260717. TR→TR, EN→EN retention, PPL,
relation/form/scaffold, robust intersections, and the M1-to-arm contrasts are secondary outcomes.
Checkpoint 128 is the fixed endpoint for all arms; no treatment-specific checkpoint selection is
allowed. A positive primary interaction with a 95% CI lower bound above zero is the precommitted
factual-reexposure success criterion. An EN→EN top-1 drop above five percentage points relative to
M1 is the retention guardrail. These are interpretation rules, not early-stopping rules.

## 4. Materialization package

The versioned contract is:

```text
configs/experiments/qwen_m2_m3_contract_v1.json
```

The reusable HU launcher is `slurm/materialize_qwen_m2_m3_blocks.slurm`, submitted through
`scripts/submit_qwen_m2_m3_materialization.sh`. The scratch family root is:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1
```

The materialization must pass before any smoke or training submission:

- equal M2/M3 block count and exact 1,048,576-token budget;
- exactly 5,000 Branch-B factual exposures and zero Branch-A factual exposure;
- deterministic spread replacement positions;
- no target synthetic contamination in M2-clean;
- complete factual sentences only;
- source, output, config, order, and audit SHA-256 records.

The implementation and launcher were tested locally (`tests/test_qwen_m2_m3_training_family.py`,
2 passed), committed as `35ddeaa`, and pushed to `origin/corpus-update`.

## 5. HU materialization launch

The submit launcher initially hit a file-mode issue (`Permission denied`) before Slurm submission;
no output was created. The executable bit was corrected and pushed as commit `894f6f9`. After a
fresh storage/path preflight, HU was fast-forwarded to that commit and materialization job `439961`
was submitted. It entered `RUNNING` on `gruenau3` in `std` with a one-hour limit; initial stdout and
stderr were empty and the scratch block output was still empty at the first check. The job later
completed successfully; final stderr remained empty and the queue no longer listed the job.

## 6. Materialization result and post-run audit

Job `439961` produced the following validated scratch package:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/manifest.json
/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/matching_audit.json
/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/m2_clean_train_blocks.jsonl
/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/m3_fact_train_blocks.jsonl
/vol/tmp2/yesildau/qwen_m2_m3_v1/blocks/shared_validation_blocks.jsonl
```

The manifest reports `status=matched_m2_m3_blocks_ready`, `fact_cycles=4`,
`scheduled_fact_exposures=5000`, `unique_branch_b_facts=1250`,
`branch_a_fact_exposures=0`, `m2_m3_block_count_equal=true`,
`m2_m3_token_budget_equal=true`, and `total_tokens_per_arm=1048576`. The factual token share is
0.0693588 and the materialized block directory is approximately 20 MB. The package records
replacement positions and SHA-256 metadata for the relevant inputs and outputs.

The coordinated post-run storage audit reported home usage at 14G, `/vol/tmp2` with 114T
available and 3% inode use, and no new unexplained large regular file in home. The only large home
files observed were the two explicitly authorized frozen Qwen M1 model copies and existing Conda
libraries. Materialization is complete; no M2/M3 training job has been submitted yet.

## 7. Launch-readiness smoke submission

The short technical smoke launcher was added in commit `b1c8cde` and pushed to
`origin/corpus-update`. It selects the seed-42 M2-clean and M3-fact configs, runs one optimizer
update on an A100, checks finite train/eval losses and all pretokenized block shapes through the
real trainer, then rehearses the optimizer-checkpoint resume path. The smoke is technical only;
it is not scientific evidence and does not alter the frozen principal contract.

Local shell checks and `tests/test_qwen_m2_m3_training_family.py` passed (`2 passed`). HU was
fast-forwarded to the same commit. The common CPU/storage preflight is job `439968`; it entered
`RUNNING` on `gruenau` with a 20-minute limit. The two-task smoke array is job `439969` and is
waiting on `afterok:439968`. No principal M2/M3 training array has been submitted.

## 8. Smoke retry correction

The first smoke array `439969` reached the GPU guard but did not constitute a valid smoke result.
The M2-clean task exposed an operator-side launcher defect: `conda run ... python -` did not pass
the heredoc script through in this batch context, so the disposable smoke config was not written
before `train_clm.py` was called. The M3-fact task was independently and correctly stopped because
the allocated A100 had an unexpected Python compute process using approximately 8.7 GB. No
principal output was created.

The launcher was corrected in commit `4860dba` to use the pinned environment Python directly for
heredoc validation/config-generation snippets and to fail closed if the smoke config is absent.
The empty failed-smoke directory was removed; the logs and failure evidence were retained. Local
syntax/tests remained green (`2 passed`). HU was fast-forwarded to `4860dba` and the corrected
chain was resubmitted: preflight `439971`, smoke array `439972_[0-1]`. At the time of this update,
`439971` was pending for priority and `439972` was pending on its dependency. No principal M2/M3
training array has been submitted.

## 9. Frozen-M1 manifest correction and current retry

The second smoke attempt exposed a second schema mismatch before any scientific training: the
selected-artifact manifest intentionally records a frozen checkpoint and file hashes but does not
provide the `local_path_absolute` field required by `train_clm.py`. Treating that artifact-only
manifest as a training manifest was corrected without changing the scientific start point.

Commit `4073456` adds a fail-closed preparation step that verifies the selected M1 checkpoint and
hashes, derives a standard scratch training manifest with the pinned tokenizer, and points all
four configs to those derived manifests. The regenerated family and validation passed with commit
`4073456`; M2/M3 configs now reference:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/family/model_manifests/qwen_m1_seed42_step75.json
/vol/tmp2/yesildau/qwen_m2_m3_v1/family/model_manifests/qwen_m1_seed43_step50.json
```

The known-contaminated `gruenau10` smoke allocation was preserved as failure evidence under
`smoke_failed_439972`; no selected artifact was deleted. The current clean retry is sequential on
`gruenau9`: preflight `439977`, smoke array `439978_[0-1]`. At submission, `439977` was pending
for priority and `439978` was pending on its dependency. No principal M2/M3 training array has
been submitted.

## 10. Smoke completion after A100 node correction

The retry described in Section 9 was initially blocked because the fixed `gruenau9` node was
reported by Slurm as mixed/unavailable (`ReqNodeNotAvail`). The pending smoke array `439978` was
the only affected job and was canceled before it could start; no output was created by that
attempt. `slurm/smoke_qwen_m2_m3.slurm` was then updated in commit `260d32f` to use the currently
idle A100 node `gruenau10`. The commit was pushed to `origin/corpus-update`, HU was fast-forwarded,
and the smoke chain was resubmitted.

The replacement preflight `439982` passed with the exact expected and observed commit
`260d32fce0d906d783e4881271642873d488833a`. The sequential smoke array `439983_[0-1]` ran both
tasks on `gruenau10`, using the same allocated A100 80 GB GPU UUID. The launcher-level GPU guard
reported 18 MiB usage and `gpu_preflight=clean` before each task. Both technical reports passed:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/smoke/m2_clean_seed42/smoke_report.json
/vol/tmp2/yesildau/qwen_m2_m3_v1/smoke/m3_fact_seed42/smoke_report.json
```

Each task completed one optimizer update, finite train/evaluation checks, checkpoint creation,
and the real optimizer-checkpoint resume path. The reports are explicitly marked
`scientific_result=false`; no principal M2/M3 training array has been submitted. The two smoke
stderr logs contained progress/deprecation output but no traceback, CUDA OOM, exception, failed,
NaN, or segmentation-error signatures.

The coordinated post-run storage audit found home usage at 14G, `/vol/tmp2` with 114T available
and 3% inode use, and no new unexplained large home file. The only large home files remain the two
authorized frozen Qwen M1 model copies and existing Conda libraries. The M2/M3 launch-readiness
smoke gate is therefore passed; the next authorized step is the principal training-family
preflight and submission.

## 11. Principal M2/M3 training completion and contaminated-node retry

The principal-family preflight `439988` passed on the exact `260d32f` repository commit. The
initial array `439989_[0-3%2]` was submitted to the GPU partition. Task `439989_0` ran
`m2_clean_seed42` successfully on `gruenau10` and completed the full 128-update contract. Tasks
`439989_1`, `439989_2`, and `439989_3` were stopped before training by the existing clean-GPU
guard: Slurm mapped them to the A100 UUID
`GPU-5d089b0f-2824-0adc-2d93-1be85aa4ad86`, where unrelated PID `22926` (`python`) was using
8,708 MiB. Each failed with the intentional launcher exit code `3:0`; no scientific output was
created for those three tasks. The successful task 0 output was retained.

Commit `0e09f62` added a reusable targeted-array setting and an initial exclusion for the
contaminated node. Retry array `439994_[1-3%2]` was held with `ReqNodeNotAvail` because `gruenau9`
was fully allocated by another user's A100 job; it was canceled without starting. Commit
`e673a57` made node selection and exclusion explicit and portable in the submit launcher. The
replacement preflight `439995` passed, and sequential retry array `439996_[1-3%1]` ran on
`gruenau10` with `TRAIN_NODELIST=gruenau10`. All three tasks used the clean GPU UUID
`GPU-4fc987af-7ab7-e2c3-e2bb-eec01fb1ba9d`, reported 18 MiB at the guard, and completed:

| Task | Label | Final eval loss | Training runtime | Scratch output |
| --- | --- | ---: | ---: | ---: |
| `439989_0` | `m2_clean_seed42` | 2.387 | 268.9 s | 38G |
| `439996_1` | `m3_fact_seed42` | 2.389 | 265.9 s | 38G |
| `439996_2` | `m2_clean_seed43` | 2.379 | 268.5 s | 38G |
| `439996_3` | `m3_fact_seed43` | 2.382 | 271.3 s | 38G |

All four training manifests report `status=complete` and contain checkpoint-32/64/96/128 plus
the final model directory. The four principal run trees total approximately 152G on scratch.
The post-run storage audit reported home usage at 14G, `/vol/tmp2` with 113T available and 3%
inode use, and no new unexplained large home files. Training is complete; no cleanup or selected
artifact migration has been performed before the fixed-endpoint evaluation and artifact-selection
step.
