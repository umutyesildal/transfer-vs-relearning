# 128 — SmolLM 500-Fact Prompt-Consistency Remediation Plan

**Date:** 29 July 2026  
**Status:** Completed seed-42; failed the frozen robust-retrieval gate; branch closed  
**Authority:** User-authorized follow-up; Documents 100, 122, 125, 127, and `AGENTS.md`

## 1. Decision and scope

SmolLM2-1.7B remains a useful second-model scientific comparison, but it is not eligible for the
M2/M3 causal arms under the completed contrastive results. The completed `lambda=0`, `0.10`, and
exploratory `0.25` candidate-ranking conditions respectively reached 39.6%, 52.2%, and 50.4%
eight-cell robustness, below the frozen 70% requirement.

The user has authorized one new, bounded **500-fact** remediation family. It is not a replication
of a failed coefficient and it is not a 2,500-fact scale-up. Its question is whether explicitly
making answer-candidate distributions agree across *seen but distinct* Form-A/Form-B prompts can
improve unseen C/D access while preserving canonical English LM acquisition.

This document opens only seed-42 discovery. M2, M3, SmolLM seed-43, and SmolLM 2,500-fact scale-up
remain closed unless the gates below are passed and documented.

## 2. Frozen comparison and one changed mechanism

The reference is the completed `lambda=0.10` run in Document 127:

```text
L_reference = L_answer_only_LM + 0.10 * L_relation_matched_ranking
```

The new treatment keeps the identical model, 100-subject/500-fact Relation V2 population, seven
rows per fact, answer-only LM, no EOS supervision, optimizer budget, candidate construction,
ranking coefficient, seed, and held-out evaluator. It adds exactly one loss term:

```text
L_V2 = L_answer_only_LM
     + 0.10 * L_relation_matched_ranking
     + 0.10 * L_prompt_distribution_consistency
```

For each fact, the consistency term is the mean KL divergence from each of the four candidate
distributions produced by the training-only A/B direct/QA prompts to their detached mean
distribution. The same deterministic relation-matched 16-candidate set (gold at index zero plus
15 negatives, including the paired-city negative where applicable) is used in all four prompts.

The term does **not** expose Form C, Form D, C/D wording, C/D examples, or an external paraphrase
corpus during training. It therefore tests generalization beyond seen A/B forms rather than
teaching to the held-out probes.

## 3. Fixed training contract

| Item | Frozen value |
|---|---|
| Model | `HuggingFaceTB/SmolLM2-1.7B` pinned base manifest |
| Population | 100 subjects × 5 relations = 500 facts |
| Curriculum | Existing byte-identical canonical-plus-A/B dataset: 3 declaratives + A direct/QA + B direct/QA |
| Objective | Canonical answer-only LM + relation-matched ranking + A/B prompt-distribution consistency |
| Coefficients | ranking `0.10`; consistency `0.10` |
| Candidate set | 16 candidates per prompt: gold + 15 deterministic relation-matched negatives |
| Held-out data | Form C/D are excluded from all training tensors, candidate groups, and loss terms |
| Optimizer | AdamW, LR `5e-5`, constant-with-warmup, warmup `0.02`, WD `0`, max grad norm `1.0` |
| Exposure/budget | 36 epochs; batch 10; accumulation 50; effective batch 500; 252 optimizer updates |
| Seed | model/data seed `42/42` |
| Checkpoints | 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 252, plus final model |
| Scratch root | `/vol/tmp2/yesildau/smollm_prompt_consistency_v2` |
| Retention | Selected model-only artifact + manifests/hashes after evaluation; other checkpoint states stay scratch cleanup candidates |

The implementation must log factual LM loss, ranking loss, and consistency loss separately, plus
their coefficients and number of complete fact groups. A grouped batch must never split its four
A/B prompts across facts; the preflight/test gate verifies complete groups and identical candidate
ordering before GPU allocation.

## 4. Frozen outcome measures and gate

Evaluate the final model and every checkpoint with the existing exact-prefix, A/B/C/D direct/QA,
eight-cell intersection, per-relation robust count, relation-swapped forced-choice, generic
completion/intrusion, and matched WikiText-2 PPL suite. The existing evaluator and definitions are
not changed.

Seed-42 can open a seed-43 replication only when the earliest checkpoint satisfying all of the
following is identified before seed-43 starts:

- exact-prefix >= 90%;
- every relation/form/scaffold cell >= 80%;
- global eight-cell robust >= 70% and every relation >= 70%;
- WikiText-2 PPL/base ratio <= 1.25;
- zero synthetic intrusion and corrected lexical integrity pass.

If no checkpoint passes, record the result and close this V2 remediation family. Do not tune a
coefficient, form set, checkpoint, threshold, or candidate count after seeing its result.

## 5. Implementation and launch gates

Before submission, the implementation must pass:

1. Unit tests for zero consistency loss on identical distributions, finite gradient on divergent
   distributions, correct loss composition, and rejection of incomplete/misordered A/B groups.
2. Dataset audit that proves exactly four A/B training prompts per fact and zero C/D references in
   the consistency tensors.
3. Local syntax/targeted test run and narrow commit/push.
4. HU fast-forward to the exact commit and remote targeted tests.
5. One combined storage/inode/path/queue preflight covering the training, 12 checkpoint outputs,
   cache, logs, data materialization, held-out evaluation, and post-run audit. All high-volume
   paths must resolve to approved scratch and HU home must remain below the protected threshold.
6. One A100-80GB single-group smoke: finite three losses, nonzero gradients, expected tensor
   shapes, and no allocation/path error.

The nearest comparable `lambda=0.10` treatment took 6 h 52 m. The new treatment adds one
four-prompt candidate group for one designated row per fact, so the conservative training estimate
is **10--14 hours** after A100 allocation; the Slurm limit is 20 hours. The final held-out
evaluation is expected to take about 60--90 minutes after GPU allocation. These are estimates,
not results.

## 6. Interpretation boundary

A passing SmolLM seed-42 would make it a candidate for an independent seed-43 replication; it
would not make it a final M1 or authorize Turkish M2/M3. Only two passing 500-fact seeds would
authorize a separately frozen 2,500-fact SmolLM scale plan. Qwen remains the sole replicated
2,500-fact English M1 result while this bounded remediation is evaluated.

## 7. Implementation, preflight, and launch record — 29 July 2026

The implementation was committed and pushed in two narrow commits:

- `0d5c831` — canonical-LM + ranking + A/B-only prompt-distribution-consistency trainer,
  seed-42 config, launcher, and loss/config tests;
- `567b872` — dedicated scratch-only preflight launcher and its contract test.

Local targeted tests passed; the HU checkout fast-forwarded to `567b872bd7c98d366f24352394a00f94c9145b5d`.
The direct HU targeted suite passed **45 tests**. Existing remote tracked-data deletions and
scratch-backed `artifacts`/`runs` links were observed before the fast-forward and were preserved;
no reset, cleanup, or home artifact write was performed.

Preflight job **439171** completed successfully. Its compact manifest records:

| Gate | Result |
|---|---|
| HU home usage | PASS: 8,299,872 KiB, below 10,485,760 KiB limit |
| `runs` / `artifacts` / base-model resolution | PASS: all resolve to approved `/vol/tmp` scratch |
| Training output absence | PASS: `/vol/tmp2/yesildau/smollm_prompt_consistency_v2/training/seed42` was absent |
| Config and launcher | PASS: exact committed files hashed in manifest |
| Capacity/inodes | Recorded in the manifest; no home-placement failure |

One training job was submitted after that PASS, with no duplicate:

| Job | Role | First verified state | Node | Initial stderr |
|---:|---|---|---|---|
| 439185 | SmolLM prompt-consistency seed-42 training | RUNNING | `gruenau9` A100-80GB | 0 bytes |

The job repeats the narrow preflight after allocation before model training. The conservative
post-allocation training estimate is 10--14 hours, followed by a separately submitted 60--90
minute held-out evaluation only after training reaches a healthy terminal state. No M2/M3,
SmolLM seed-43, or SmolLM scale-up job has been submitted.

### Live training checkpoint — 29 July 2026

At the user's 10-hour follow-up, job 439185 remained healthy and active at **10 h 56 m**. It had
written checkpoints 25, 50, 75, 100, 125, 150, 175, and **200** of the frozen 252-update budget.
The allocated A100-80GB was actively computing (100% utilization; approximately 30.8 GiB used),
and the Slurm stderr log remained 0 bytes. The training manifest remained correctly `started`, as
expected before final model saving. At the observed approximately 3.3 minutes/update rate, the
remaining 52 updates imply an estimated **about 3 hours** to training completion, plus the
separately planned 60--90 minute held-out evaluation.

## 8. Seed-42 training completion and evaluation-wave preparation — 30 July 2026

Training job **439185** reached terminal completion after **46,489.42 seconds (12 h 54 m 49 s)**.
Its final model, all frozen checkpoint directories, training manifest, train/validation metrics,
and separated objective diagnostics are present under the intended scratch-only run root. The
training manifest has status `complete`; the final trainer validation loss is `0.00018034`. Its
stderr contains normal evaluation-progress rendering but no traceback, OOM, NaN, or Inf event.

The separated training diagnostics are:

| Diagnostic | Value |
|---|---:|
| Mean factual LM loss | 0.772060 |
| Mean relation-matched ranking loss | 0.653131 |
| Mean A/B prompt-consistency loss | 0.045811 |
| Ranking coefficient | 0.10 |
| Consistency coefficient | 0.10 |
| Consistency groups processed | 18,000 |
| Training batches | 12,600 |

The scalar Trainer loss (42.10) combines differently shaped per-step quantities and must not be
used as a factual-quality or cross-treatment selection metric. The run currently occupies 109 GiB
on `/vol/tmp2`, with no selected artifact deleted or moved.

To apply the frozen earliest-all-gates rule, commit `d5c6dd5` adds a checkpoint-aware evaluator:
it can locate the completed training manifest for either `final_model` or a nested checkpoint and
records the actual checkpoint label in the derived model manifest. It also adds a scratch-only
preflight and a parallel **12-task array** for checkpoints 25, 50, 75, 100, 125, 150, 175, 200,
225, 250, 252, and the final model. All tasks use the unchanged exact, A/B/C/D hard suite,
relation-binding, and WikiText-2/general-integrity evaluator. Local and HU targeted tests passed
45 tests.

Evaluation preflight job **439290** is running at the time of this record. It checks all 12 output
namespaces before GPU submission. If it passes, one array submission will run the checkpoints in
parallel; each task has a 3-hour Slurm cap and an estimated 60--90 minute runtime. No result is
interpreted before all required evaluator outputs are complete.

### Evaluation submission correction — 30 July 2026

Preflight 439290 later passed. An initial array submission (439353) was made after its
30-minute freshness window had elapsed. Its first three tasks correctly rejected the stale
manifest before model loading or result-directory creation; their stderr records only
`Preflight manifest is stale`. The array was immediately cancelled, no `results/` namespace was
created, and no factual metric or partial result exists to interpret. This is an operational
submission-timing correction, not an experimental result.

Fresh preflight **439365** was then submitted. The next evaluation array may be submitted only
after that job records a new PASS manifest and its timestamp is checked immediately before
submission.

### Queue-delay remediation and final evaluation submission — 30 July 2026

Fresh preflight 439365 passed, but it too had waited in the scheduler long enough that its manifest
was more than 30 minutes old when array tasks first obtained GPUs. Array 439367 therefore correctly
rejected the stale manifest before output creation and was cancelled. This reproduced the same
operational, no-result condition rather than a model or evaluator failure.

Commit `09e584e` corrects the launcher: the family preflight remains a coordinated input/output
audit, while each array task now creates a **new, task-local preflight after GPU allocation** for
its own output namespace. This preserves the original home/scratch/hash checks and makes queue
delay harmless. Local and HU targeted tests again passed 45 tests.

The corrected final wave was submitted as a dependency chain:

| Job | Role | Submission state |
|---:|---|---|
| 439379 | coordinated 12-output family preflight | PENDING at submission |
| 439380_[0-11] | checkpoint 25--252 plus final-model frozen evaluation array | PENDING on `afterok:439379` |

No evaluation metric is available yet. Once a task starts, its own fresh preflight must pass before
model load; after all 12 results complete, the earliest-all-gates checkpoint decision and storage
post-audit will be documented.

### Parallelism status — 30 July 2026

Family preflight 439379 passed and released array 439380. All twelve tasks were submitted in one
parallel array. At the first post-release check, tasks 0--2 were RUNNING on `gruenau10` with empty
stderr logs; tasks 3--11 were correctly PENDING only for Slurm GPU resources. This is the maximum
currently offered by the cluster, not a serial launcher restriction. No duplicate array was
submitted because that would compete for the same scarce GPUs and slow completion.

### First evaluation outputs — 30 July 2026

At the one-hour follow-up, the array had completed the hard suite for checkpoints 25, 50, 75,
100, 125, and 150; exact-prefix output was complete through checkpoint 125. Tasks for checkpoint
150, 175, and 200 were still running and 225, 250, 252, and final-model tasks were waiting for
GPU resources. Completed stderr logs contain only expected model-load progress and the Transformers
dtype deprecation warning.

| Checkpoint | Exact primary top-1 | Hard top-1 | Relation-swapped forced choice |
|---:|---:|---:|---:|
| 25 | 5.6% | 188/4,000 (4.70%) | 812/1,600 (50.75%) |
| 50 | 35.4% | 1,379/4,000 (34.48%) | 889/1,600 (55.56%) |
| 75 | 85.2% | 2,980/4,000 (74.50%) | 1,205/1,600 (75.31%) |
| 100 | 100.0% | 3,458/4,000 (86.45%) | 1,435/1,600 (89.69%) |
| 125 | 100.0% | 3,571/4,000 (89.28%) | 1,485/1,600 (92.81%) |
| 150 | pending | 3,626/4,000 (90.65%) | 1,494/1,600 (93.38%) |

These are **interim, incomplete** factual observations. Eight-cell robust intersection,
per-relation cell floors, PPL, generic integrity, and the final-model result are required before
the frozen earliest-all-gates selection rule can be applied.

## 9. Complete held-out evaluation, post-run audit, and decision — 30 July 2026

The corrected array `439380_[0-11]` completed all eleven checkpoints and the final model. Every
task passed its task-local post-allocation preflight. Stderr contains only normal model-load
progress and the Transformers dtype deprecation warning; no traceback, OOM, NaN, or Inf occurred.
The compact evaluation tree is 214 MiB on approved `/vol/tmp2` scratch.

Base SmolLM2-1.7B PPL is 15.9242 under this frozen WikiText-2 protocol. `Robust` is the eight-cell
intersection over 500 facts and `min relation` is the weakest relation's eight-cell percentage.

| Checkpoint | Exact | Hard | Robust | Min relation | Forced | PPL | PPL/base |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 25 | 5.6% | 4.70% | 1.0% | 0.0% | 50.75% | 16.100 | 1.011 |
| 50 | 35.4% | 34.48% | 7.4% | 3.0% | 55.56% | 16.424 | 1.031 |
| 75 | 85.2% | 74.50% | 23.6% | 14.0% | 75.31% | 16.801 | 1.055 |
| 100 | 100.0% | 86.45% | 38.4% | 23.0% | 89.69% | 17.051 | 1.071 |
| 125 | 100.0% | 89.28% | 46.6% | 28.0% | 92.81% | 17.222 | 1.082 |
| 150 | 100.0% | 90.65% | 51.0% | 30.0% | 93.38% | 17.336 | 1.089 |
| 175 | 100.0% | 90.88% | 51.4% | 32.0% | 93.75% | 17.372 | 1.091 |
| 200 | 100.0% | 91.15% | 53.4% | 36.0% | 94.00% | 17.453 | 1.096 |
| 225 | 100.0% | 91.62% | 55.0% | 38.0% | 94.06% | 17.490 | 1.098 |
| **250** | **100.0%** | **91.67%** | **55.8%** | **38.0%** | 94.00% | 17.505 | 1.099 |
| 252 / final | 100.0% | 91.60% | 55.2% | 38.0% | **94.12%** | 17.510 | 1.100 |

All generic-integrity outputs pass: generic top-1 is 30/30, and lexical-empty/synthetic-subject
intrusion counts are zero. Retention/integrity is not the failure mechanism.

Checkpoint 250 is the best observed robust point but is **not** an eligible selected checkpoint:
it misses the precommitted 70% global robust threshold by 14.2 points and the per-relation floor
by 32 points. Relation robust counts are born-in 74, field-of-study 68, lives-in 53, profession
38, and works-in-industry 46 out of 100. The weakest required cell is
`profession / Form-C / QA = 44/100`; `profession / Form-C / direct = 51/100` and
`works_in_industry / Form-D / direct = 49/100` also miss the 80% cell floor.

**Decision:** no checkpoint passes every frozen gate. V2 improves the preceding `lambda=0.10`
robust result from 52.2% to 55.8%, but does not establish SmolLM as a second M1 candidate. Close
this SmolLM branch without seed-43 or 2,500-fact scale-up; Qwen remains the sole replicated
2,500-fact English M1 result.

### Post-run storage audit

After all tasks terminated, HU home was 8.0 GiB. `/vol/tmp2` had 113 TiB free at 3% inode use;
the only home files over 500 MiB are pre-existing Conda/Torch CUDA libraries. No experiment model,
checkpoint, dataset, raw evaluation, cache, or verbose log was written to home. The 109 GiB
training run and all retained evidence remain scratch-only and untouched.
