# 105 - M1 Cross-Family Model Screening Plan

**Date:** 2026-07-19  
**Status:** Frozen plan and local implementation complete; HU model acquisition, compatibility
smoke tests, training, and evaluation have not yet been submitted.  
**Scope:** Compare three new base-model families against the already completed SmolLM2-1.7B
Document 104 reference at 100 subjects / 500 facts. Add Llama only if its access, license, and
compatibility gates pass. M2, M3, seed-43 replication, and scale-up remain **HOLD**.

## 1. Decision And Scientific Question

Documents 101--104 established that SmolLM2-1.7B can store the canonical 500 English facts but
has not reached the frozen prompt-robust retrieval gates. Document 104's hybrid treatment reached
100% exact-prefix and trained A/B accuracy, but only 75.05% on held-out C/D cells and 39.6% on the
eight-cell robust intersection. The next controlled question is therefore:

> Is the remaining prompt-robustness failure specific to the SmolLM2 model-family stack, or does
> it persist across comparably sized base language-model families under the same acquisition
> curriculum, optimization budget, endpoint, and evaluation suite?

This is a legitimate model-family screen, not an unrecorded change to Document 103. Document 103
is complete and its immutable result is Document 104. The screen may select a different model for
later replication and scale-up, but it does not itself authorize M2 or final M1.

## 2. Frozen Candidate Panel

| Role | Frozen model ID | Participation |
|---|---|---|
| Existing reference | `HuggingFaceTB/SmolLM2-1.7B` | Reuse Document 104 result; do not retrain |
| New candidate Q | `Qwen/Qwen2.5-1.5B` | Required |
| New candidate S | `stabilityai/stablelm-2-1_6b` | Required |
| New candidate G | `google/gemma-2-2b` | Required, subject to authenticated model access |
| New candidate L | `meta-llama/Llama-3.2-1B` | Conditional on authenticated access, accepted license, and compatibility smoke |

Only pretrained/base checkpoints are permitted. Instruct/chat variants, quantized derivatives,
community conversions, coder/math variants, and post-trained checkpoints are excluded.

Before download or training, record the exact Hugging Face revision/commit for every participating
model. A gated model that cannot be accessed without exposing credentials is recorded as
`NOT RUN - ACCESS GATE`; it is not silently replaced and is not counted as a scientific failure.
Do not print or document Hugging Face tokens or other credentials.

## 3. Comparison Estimand And Fairness Boundary

The primary comparison is a **model-family stack comparison**: pretrained weights, architecture,
native tokenizer, and native embedding vocabulary vary together. It is not an architecture-only
causal ablation.

Every model must use its own official native tokenizer. Forcing one tokenizer across unrelated
models is prohibited. To make the remaining budget comparable, the implementation must report,
for each tokenizer:

- prompt, answer, and total token-count distributions;
- maximum sequence length and truncation count;
- number and percentage of answers split into multiple tokens;
- BOS, EOS, PAD, and unknown-token behavior;
- total supervised answer tokens seen over training.

No example may be removed or replaced because one tokenizer segments it differently. Any
truncation or unsupported special-token behavior blocks that model until corrected and audited.
Because native tokenization differs, equal rows and updates do not imply an identical token budget;
that limitation must be retained in the result report.

## 4. Frozen Training Contract

The new models use the byte-identical Document 103 Treatment T population and JSONL content:

- 100 subjects and 500 Relation V2 facts;
- three historical canonical declarative rows per fact;
- Form A under direct and QA scaffolds;
- Form B under direct and QA scaffolds;
- no Form C or Form D training row;
- 3,500 training rows, 500 validation rows, and seven rows per fact;
- seed and data seed 42;
- 36 epochs, effective batch 500, and exactly 252 optimizer updates;
- answer-only loss;
- `supervise_eos: false`;
- learning rate `5e-5` and the unchanged Document 103 optimizer/scheduler settings;
- BF16 training where the model implementation supports it;
- block size 128 with zero truncation;
- selection and evaluation at update 252 only; no checkpoint sweep.

Micro-batch size and gradient accumulation may differ only when required to fit a model on one
A100 80GB. Their product must preserve the effective batch of 500, example order, 252 updates,
and optimization semantics. Gradient checkpointing or an architecture-specific attention backend
may be enabled solely as an operational compatibility measure and must be recorded. No candidate
receives a post-result learning-rate search under this plan. Any later model-specific tuning is a
new exploratory plan and cannot overwrite this fixed-recipe screen.

## 5. Pre-Submission Compatibility Gates

Each new family must pass the following before its full training job is submitted:

1. pinned revision downloads entirely into an approved scratch cache;
2. `AutoConfig`, native tokenizer, and base `AutoModelForCausalLM` load in the pinned environment;
3. model type, parameter count, dtype, vocabulary size, special tokens, and license/access state
   are recorded without secrets;
4. the frozen dataset and per-model tokenization audit pass with zero truncation and zero leakage;
5. answer-only masking is unit-tested on at least one example from every relation and row type;
6. forward, backward, optimizer-step, checkpoint-write, and checkpoint-reload smoke tests pass;
7. measured peak GPU memory supports a safe one-A100-80GB full run;
8. the frozen evaluator loads the smoke checkpoint without a model-specific scoring change.

A candidate that fails compatibility is marked `NOT RUN - TECHNICAL GATE` with the exact reason.
Do not alter the scientific data or metric definitions merely to make one model run.

## 6. Frozen Evaluation Suite

Every successfully trained candidate receives the same suites used for Document 104:

- 500 canonical exact-prefix probes;
- 4,000 open-ended Forms A/B/C/D under direct and QA scaffolds;
- eight-cell robust intersection over all forms and scaffolds;
- per-relation and per-cell accuracy;
- relation-swapped/binding evaluation;
- frozen WikiText-2 generic perplexity;
- frozen 30 generic prompt/completion controls;
- empty-output, EOS-ending, and synthetic-subject-intrusion counts.

Generic perplexity must be computed for both the pinned untrained base and update-252 model of
each family. Compare the trained/base PPL ratio within a family; do not rank different tokenizers
by raw PPL alone. Evaluator prompts, normalization, top-1 scoring, relation membership, and gate
thresholds are immutable across models.

## 7. Frozen Gates And Selection Rule

The Document 103 treatment gates remain unchanged:

| Gate | Requirement |
|---|---:|
| Canonical exact-prefix | >=90% |
| Every trained A/B form/scaffold cell, globally and per relation | >=80% |
| Every held-out C/D form/scaffold cell, globally and per relation | >=80% |
| Eight-cell robust intersection, globally and per relation | >=70% |
| Generic PPL ratio | <=1.25; preferred <1.10 |
| Integrity and generic behavior | No leakage, relation collapse, empty-generation collapse, or synthetic intrusion |

If exactly one new candidate passes every gate, it becomes the proposed seed-43 candidate. If
multiple candidates pass, select by: (1) highest global eight-cell robust intersection, (2) highest
minimum per-relation robust intersection, (3) highest global held-out C/D accuracy, (4) lower
trained/base PPL ratio, then (5) lower measured training/storage cost. Apply these tie-breakers in
order.

If no new model passes every gate, no model is promoted. Rank-ordering failed models is diagnostic
only; it cannot authorize seed 43, scale-up, M2, or M3. A materially better but failing family may
motivate a separately frozen representation/objective or model-specific optimization plan.

The existing SmolLM Document 104 reference remains in every comparison table but cannot be
retroactively reselected under altered criteria.

## 8. Parallel HU Execution Plan

The required Qwen, StableLM, and Gemma training jobs may be submitted in one parallel Slurm wave.
Llama joins the same wave only if its gates are already complete. Each job requests one A100 80GB
and has a unique scratch output namespace. Simultaneous submission does not guarantee simultaneous
execution; Slurm may leave some jobs pending until GPUs are available.

Use a family root such as:

```text
/vol/tmp2/yesildau/m1_cross_family_screen_v1
```

with separate `models/`, `training/<candidate>/`, `evaluation/<candidate>/`, `cache/`, `logs/`, and
`tmp/` namespaces. All downloads, weights, optimizer state, caches, corpora, raw evaluation output,
and Slurm logs remain on scratch. No high-volume path may resolve to HU home.

One complete family-level storage/inode/path preflight immediately before the coordinated
submission wave is sufficient. It must enumerate every participating job and resolved path, and
estimate the combined checkpoint, cache, log, temporary, and evaluation demand. Do not repeat
`du`/`df` separately for each sibling job in that unchanged wave. Repeat preflight only if the
candidate set, paths, expected family size, filesystem state, or submission wave materially
changes. Scratch may be used heavily; concurrent jobs are allowed whenever their combined demand
fits the capacity and inodes actually available.

Inspect the queue once before the wave, submit each qualifying job once, capture every job ID, and
inspect the queue immediately afterward. Verify the initial state, allocated node/GPU, scratch
output, and stderr for every running job. Do not submit duplicates because one model remains
pending or temporarily quiet.

Training jobs are the first parallel wave. After successful endpoints and stderr are verified,
launch their evaluations as a second parallel wave. Failed or incomplete training must not feed an
evaluation job. Based on the Document 104 SmolLM runtime, report 40--55 minutes as the SmolLM
reference only; provide per-family runtime estimates from compatibility smoke measurements rather
than assuming identical speed.

## 9. Storage, Retention, And Post-Run Audit

The preflight must record:

- current HU home usage;
- scratch capacity and inode availability;
- each resolved model/cache/output/log path;
- expected checkpoints per candidate and combined estimated family size;
- which files will be retained after evaluation.

One family-level post-run audit may be performed after all sibling training/evaluation jobs in the
wave reach terminal state. It must verify that HU home did not grow unexpectedly and that no new
large regular artifact landed there. Preserve for every completed candidate:

- the update-252 model-only endpoint;
- config, tokenizer, pinned source revision, and run metadata;
- compact evaluation summaries and comparison table;
- manifest and SHA-256 checksums.

Duplicate checkpoints, optimizer/scheduler/RNG state, reproducible caches, and verbose logs remain
scratch cleanup candidates only after the selected evidence is verified. Do not delete or
overwrite a frozen model, unique dataset, canonical manifest, or non-reproducible result without
explicit user approval.

## 10. Required Deliverables And Next Decision

Before HU submission:

1. per-model pinned revision and access/license record;
2. versioned configs and a narrowly named parallel-family launcher;
3. dataset identity, tokenizer, leakage, masking, and compatibility-smoke reports;
4. resolved scratch layout, combined storage estimate, and retention plan;
5. a machine-readable comparison manifest containing the frozen gates and selection rule.

After completion, create:

```text
documentation/106_M1_CROSS_FAMILY_MODEL_SCREENING_RESULT.md
```

Document 106 must record every submitted job ID, node/GPU, state, runtime, pinned revision, output
path, selected checkpoint, storage audit, stderr status, all frozen metrics, candidate exclusions,
and the precommitted selection decision. Update Document 100 only after those results exist.

Until one candidate passes every gate and then passes an independently planned seed-43
replication, the 500-subject control, final M1, M2, and M3 remain **HOLD**.

## 11. Implementation Record Before HU Submission

The Document 105 implementation was prepared locally on 2026-07-19 and committed in the
`transfer-vs-relearning` repository as `20c40d5` (`Implement cross-family M1 screening`). No HU
job was submitted as part of this implementation step.

The versioned implementation adds:

- `configs/experiments/m1_cross_family_screen_v1.yaml`, freezing candidate order, required versus
  conditional participation, scratch paths, storage estimates, retention, and metric gates;
- `configs/training/m1_cross_family_seed42_template.yaml`, preserving the Document 103 fixed
  recipe and update-252 endpoint;
- scratch-only model resolution/download records that resolve and write the exact Hugging Face
  revision before snapshot download;
- per-family native-tokenizer audits covering length, truncation, answer segmentation, special
  tokens, and supervised-token exposure;
- a 35-cell masking audit over five relations by seven training representations;
- one-A100 forward/backward smoke plus scratch checkpoint write/reload/cleanup verification;
- one combined family-level preflight for each acquisition, training, and evaluation wave;
- parallel Slurm acquisition, training, and evaluation arrays;
- trained/base generic-capability evaluation per family and the unchanged hard/exact suites;
- reusable SSH submission and read-only inspection launchers documented by their narrow names.

The registry's conservative four-candidate estimate is 1,101 GiB including eleven possible
checkpoint slots per participating candidate and 100 GiB shared overhead. This is a fit check
against live scratch capacity, not a project quota. Training uses the already frozen, byte-identical
Document 103 dataset under `/vol/tmp2/yesildau/m1_canonical_form_diversity_v1/datasets`; it does not
generate a competing copy inside the new family.

Local verification completed with Python compile checks, Bash syntax checks for every new Slurm
and SSH launcher, `git diff --check`, YAML structure validation, and 39 passing relevant tests
covering the new family contract, canonical dataset, training core, and answer-only masking. The
local host lacks the project's PyYAML package, so the local test invocation used a temporary,
non-repository YAML parser adapter. The authoritative HU conda environment must rerun the same
tests before acquisition submission.

Execution order is frozen as:

1. user pushes the implementation commit;
2. HU pulls it with `--ff-only` and reruns the relevant tests;
3. one acquisition preflight job gates the four-way model acquisition array;
4. inspect access records and exact resolved revisions; Gemma must pass, while inaccessible Llama
   is recorded and omitted;
5. one combined training preflight gates the qualifying parallel GPU array;
6. after all required endpoints complete, one combined evaluation preflight gates the parallel
   evaluation array;
7. inspect, summarize, freeze hashes, run the family post-run audit, and write Document 106.

The new SSH entrypoints are:

```text
ssh-client/scripts/submit_m1_cross_family_acquisition.sh
ssh-client/scripts/submit_m1_cross_family_training.sh
ssh-client/scripts/submit_m1_cross_family_evaluation.sh
ssh-client/scripts/inspect_m1_cross_family.sh
```

## 12. Acquisition Wave Submission Record

The user pushed commit `20c40d5`, and HU fast-forwarded from `350ae24` to `20c40d5` on
2026-07-19. The authoritative HU conda environment then passed all 39 frozen relevant tests.

The Hugging Face read token was transferred without printing it and installed with mode `0600`
under the family scratch `HF_HOME`; it was not placed in Git, documentation, a command argument,
or HU home. Qwen, StableLM, and Gemma access passed first. The user subsequently received Llama
access, and its read-only check resolved revision
`4e20de362430cd3b72f300e6b0f18e50e7166e08`.

Read-only model access checks passed and resolved:

| Candidate | Resolved Hugging Face revision |
|---|---|
| Qwen2.5-1.5B | `8faed761d45a263340a0528343f099c05c9a4323` |
| StableLM2-1.6B | `f499ead74c53749bd93cebc6ce8bc0d7bdf1eaef` |
| Gemma-2-2B | `c5ebcd40d208330abc697524c919956e692655cf` |
| Llama-3.2-1B | `4e20de362430cd3b72f300e6b0f18e50e7166e08` |

Submitted Slurm work:

| Job | Purpose | Initial state |
|---|---|---|
| `409082` | Initial Qwen/StableLM/Gemma acquisition preflight | **FAILED**: incorrectly classified its own dependent target array as a duplicate |
| `409083_[0-2]` | Initial dependent acquisition array | Never ran (`DependencyNeverSatisfied`); canceled after preserving the failed preflight manifest |
| manual four-model preflight | Qwen/StableLM/Gemma/Llama combined storage/path/inode/source check | **PASS**; 1,101 GiB combined conservative estimate |
| `409084_[0-3]` | Four-task parallel acquisition array | **COMPLETED** on `gruenau3`; all four access/model manifests passed |

Job `409082` is retained as operational failure evidence; its manifest was copied to
`acquisition_failed_409082.json`. No model acquisition occurred under `409083`. The corrected
four-model array `409084` was submitted once and completed successfully. Its stderr contained only
Hugging Face deprecation and download-progress messages, with no scientific or storage failure.

The completed manifests record the following native model sizes:

| Candidate | Parameter count | Tokenizer implementation |
|---|---:|---|
| Qwen2.5-1.5B | 1,777,088,000 | `Qwen2Tokenizer` |
| StableLM2-1.6B | 1,644,515,328 | `TokenizersBackend` |
| Gemma-2-2B | 3,204,165,888 | `GemmaTokenizer` |
| Llama-3.2-1B | 1,498,482,688 | `TokenizersBackend` |

Gemma's instantiated parameter count is approximately 3.20B, materially larger than the other
screening candidates despite its repository name. It remains in the precommitted family screen,
but runtime, memory, and final scientific comparisons must explicitly retain this size caveat; it
must not be described as a strictly parameter-matched comparison.

## 13. Training Wave Submission Record

The dependent-array preflight correction was committed as `fe49175` and pushed by the user. HU
fast-forwarded to exact commit `fe4917555d6a3cead97ce58b968c49b0fb6ad312` on 2026-07-19. An
initial verification attempt used HU system Python and stopped because that interpreter does not
contain `pytest`; this was an environment-selection error, not a test failure. Re-running in the
project conda environment passed the complete suite (163 tests).

The post-acquisition audit immediately before training recorded:

- HU home usage: `8.0G`;
- `/vol/tmp2`: `116T` available and 3% inode use;
- no new home-resident model artifact over 500 MB; the three reported large files were existing
  CUDA/PyTorch libraries inside the project conda environment;
- all four pinned model manifests present under the scratch family root.

The coordinated training wave was then submitted once:

| Job | Purpose | Initial verified state |
|---|---|---|
| `409088` | Combined four-candidate training preflight | **PASS** on `gruenau`; manifest and stderr clean |
| `409089_0` | Qwen parallel-training task | `RUNNING` on `gruenau9` |
| `409089_1` | StableLM parallel-training task | `RUNNING` on `gruenau9` |
| `409089_2` | Gemma parallel-training task | `RUNNING` on `gruenau9` |
| `409089_3` | Llama parallel-training task | `RUNNING` on `gruenau10` |

Each array task requests one A100 80GB, uses its isolated scratch namespace, and retains the
precommitted update-252 endpoint. The smoke, tokenizer/masking, checkpoint write/reload, and path
gates run before full training inside each task. All four tasks were released by the successful
preflight and entered `RUNNING`; the first inspection found no immediate stderr failure. The
current practical completion estimate is
approximately 60--135 minutes after dependency release: Qwen, StableLM, and Llama are expected near
the lower part of that interval, while the larger 3.20B Gemma task may determine the family wall
time. This is an estimate, not a completion claim. Evaluation remains unsubmitted until every
required training endpoint and stderr is inspected.

An immediate `sacct` query returned a HU SlurmDBD/Munge authentication error. This does not reflect
a training failure: `squeue` remained available and showed the preflight running with the array
correctly dependency-blocked. Later status checks should therefore use `squeue` plus scratch logs
and manifests, and use `sacct` again only if the HU accounting service has recovered.

## 14. Invalid First Training Wave And Required Correction

The first training array `409089_[0-3]` reached terminal state without producing four valid family
endpoints. This wave is **operationally failed and scientifically inadmissible**; no evaluation was
submitted. Inspection found a launcher-level array race rather than a model-learning result.

`conda run` emitted a trailing blank line after the candidate resolver output. The launcher used
`tail -n 1`, therefore every task resolved `label` as the empty string and wrote to the same shared
config path:

```text
/vol/tmp2/yesildau/m1_cross_family_screen_v1/configs/training/.yaml
```

The four tasks concurrently overwrote that file. The last observed payload was Llama, so the array
did not train Qwen, StableLM, Gemma, and Llama as intended:

| Array task | Observed outcome | Scientific status |
|---|---|---|
| `409089_0` | Trained the overwritten Llama config to update 252 and wrote a Llama endpoint | Invalid cross-family artifact; do not evaluate or select |
| `409089_1` | `FileExistsError` on the same Llama run directory | Failed |
| `409089_2` | `FileExistsError` on the same Llama run directory | Failed |
| `409089_3` | Began the same Llama config and failed with CUDA OOM amid the collision | Failed |

The task-0 loss curve demonstrates that one accidental Llama training process could optimize the
dataset, but it is not admissible evidence because task identity and isolation were violated. The
run directories and logs are retained under scratch as failure evidence until the corrected wave
is verified; they are not frozen/selected models.

The local correction removes blank resolver lines before selecting the label, validates the result
against the four frozen candidate labels, and includes `SLURM_ARRAY_TASK_ID` in each training
config filename. The same fail-closed label validation is applied to acquisition and evaluation
launchers to prevent recurrence. A regression test freezes these properties. Bash syntax checks
and `git diff --check` passed locally; the normal local Python lacks PyYAML, so the authoritative HU
conda suite must validate the patch after it is pushed.

Before resubmission, preserve the `409089` logs, relocate the invalid Llama run tree into an
explicit failed-wave namespace on scratch, rerun the combined training preflight against clean
candidate output roots, and submit the corrected four-task array once. Do not reuse or evaluate
the accidental Llama endpoint. The corrected training wave is expected to require approximately
60--135 minutes after release; check the first smoke/config evidence after 10--15 minutes.

### Corrected training-wave submission

The user pushed correction commit `90c5fca`. HU fast-forwarded to exact commit
`90c5fca95a3a5bb97c82ba3fbaa306f9cbabbd27`, and the authoritative project conda environment
passed the complete 164-test suite. The invalid Llama tree was preserved, not deleted, at:

```text
/vol/tmp2/yesildau/m1_cross_family_screen_v1/failed_runs/training_409089/llama
```

All four active candidate training roots were then verified absent. The corrected coordinated wave
was submitted once:

| Job | Purpose | Initial state |
|---|---|---|
| `409428` | Corrected four-candidate combined training preflight | `RUNNING` on `gruenau`; stderr empty |
| `409429_[0-3]` | Corrected Qwen/StableLM/Gemma/Llama array | `PENDING (Dependency)` on `409428` |

At the immediate 29-second inspection the preflight was still running normally, so no corrected
task config existed yet. The lone legacy `.yaml` file under the config directory belongs to failed
wave `409089` and is not referenced by the corrected launcher. The next inspection must verify that
the preflight passed and that the four isolated configs are named `0_qwen.yaml`,
`1_stablelm.yaml`, `2_gemma.yaml`, and `3_llama.yaml` before interpreting any training progress.

### Corrected-wave early inspection

The next inspection verified all four isolated config names and their intended run/output labels.
The tokenizer/masking and full checkpoint write/reload/cleanup smoke gates passed independently for
all four intended model families:

| Task | Model verified by smoke | Peak allocated bytes | Early state |
|---|---|---:|---|
| `409429_0` | Qwen/Qwen2.5-1.5B | 7,207,909,376 | `RUNNING` on `gruenau9` |
| `409429_1` | stabilityai/stablelm-2-1_6b | 7,312,812,032 | `RUNNING` on `gruenau9` |
| `409429_2` | google/gemma-2-2b | 23,552,043,520 | `RUNNING` on `gruenau9` |
| `409429_3` | meta-llama/Llama-3.2-1B | 6,080,839,680 | **FAILED** on `gruenau10` after smoke |

Thus the config-isolation correction worked and the first-wave race did not recur. Llama task 3
failed at the first real training step with CUDA OOM. The error reported only approximately 0.50
GiB free, approximately 72.43 GiB held by another process (`54819`), and approximately 6.31 GiB
total use attributable to the current process. Because the same Llama model had just passed its
6.08-GiB smoke allocation and the A100 has 79.25 GiB total capacity, this is interpreted as a
contaminated/shared-orphan GPU allocation on `gruenau10`, not evidence that Llama intrinsically
cannot fit the requested device. Task 3 ran for 62 seconds and exited nonzero.

Qwen, StableLM, and Gemma remain active and must not be duplicated or interrupted. Their smoke
manifests verify the correct pinned revisions, native tokenizers, 35 masking cells, and isolated
config/output roots. Llama retry is deferred until those sibling jobs reach terminal state so the
duplicate-job preflight is not bypassed. Then preserve the failed corrected-wave Llama tree under
a `failed_runs/training_409429` namespace and submit a clean Llama-only preflight/retry, preferably
on an uncontaminated allocation. No evaluation may start until the required endpoints are checked;
Llama remains conditional but will be retried because access and smoke compatibility passed.

A follow-up Slurm allocation audit confirmed that the three surviving tasks are isolated on the
three physical A100 80GB devices of `gruenau9`: Qwen received GRES `IDX:0`, StableLM `IDX:1`, and
Gemma `IDX:2`. The node reports exactly three configured and three allocated A100 devices; each job
requests and receives `gres/gpu:a10080gb=1`. After more than ten minutes, all three tasks remained
`RUNNING` with `Reason=None`, `ExitCode=0:0`, and no traceback/OOM/NCCL marker. Therefore there is
no evidence that the active jobs share one physical GPU or contaminate one another.

The failed Llama allocation on `gruenau10` had also requested and received one A100 GRES, but the
terminal OOM snapshot reported a separate process consuming 72.43 GiB. The allocation is now gone,
so that historical process cannot be live-inspected through the completed job. This is treated as
a node/allocation anomaly requiring a clean retry, not as a threat to the isolated `gruenau9`
tasks and not as proof of a persistent user-owned orphan process.

### Corrected-wave late training status

At approximately 69 minutes after release, Qwen had completed successfully, StableLM had reached
the nominal endpoint but failed numerical-validity requirements, and Gemma remained active:

| Candidate | Runtime/progress | Observed result | Scientific disposition |
|---|---|---|---|
| Qwen | `01:06:42`, update 252 | `train_loss=0.2728061`, `eval_loss=0.000153679`; manifest `complete`, clean stderr | Valid training endpoint; evaluation still deferred |
| StableLM | approximately 57 minutes, update 252 | `train_loss=1.877163e22`, `eval_loss=NaN`; manifest mechanically says `complete` | Numerically invalid; must not be evaluated or selected |
| Gemma | `RUNNING`, at least checkpoint 175/252 | no traceback/OOM/NCCL marker | Continue without intervention |
| Llama | failed after 62 seconds | contaminated-allocation OOM after successful smoke | Clean retry pending after active sibling completion |

StableLM diverged at the first logged training window (`epoch 0.7143`) with loss `9.461e23` and
`grad_norm=NaN`; every subsequent logged evaluation loss was `NaN`. The generic trainer's
`status=complete` records process completion only and does not override the scientific finite-loss
gate. Repeating the unchanged deterministic recipe is not justified. Any StableLM-specific lower
learning rate, precision change, clipping change, or optimizer remediation would alter the frozen
comparison and must be labeled as a separately planned exploratory compatibility remediation, not
silently substituted into the primary screen.

No evaluation wave is submitted at this point. Preserve the Qwen endpoint and StableLM failure
evidence, allow Gemma to finish, then conduct the already justified Llama clean-allocation retry.

### Gemma completion and StableLM dtype remediation decision

Gemma subsequently completed successfully with `train_runtime=5452.0234` seconds,
`train_loss=0.29106365`, and `eval_loss=1.4856024e-05`. Its manifest reports `complete`, and stderr
contains no traceback, OOM, NCCL, or non-finite marker. Qwen and Gemma therefore provide two valid
training endpoints; neither is evaluated yet.

The StableLM numerical failure has a concrete precision-path explanation. The pinned native model
configs declare:

| Candidate | Native snapshot `torch_dtype` |
|---|---|
| Qwen | `bfloat16` |
| StableLM | `float16` |
| Gemma | `float32` |
| Llama | `bfloat16` |

The shared trainer requested BF16 autocast but loaded each model without an explicit dtype, leaving
StableLM parameters in native FP16. The original smoke performed one BF16-autocast forward/backward
at batch size 2 but did not execute an optimizer step. It therefore could not detect the FP16
parameter/optimizer overflow that appeared at the first real update with batch size 10 and 50-way
gradient accumulation.

A single-variable StableLM compatibility remediation is now frozen locally:

- explicitly load StableLM parameters as `bfloat16`;
- retain LR `5e-5`, batch size 10, accumulation 50, effective batch 500, 252 updates, seed 42,
  dataset bytes, answer-only loss, EOS-false policy, scheduler, and checkpoint schedule;
- strengthen the smoke gate to use the configured batch size, complete 50 accumulated
  microbatches, execute one AdamW step, and require finite loss, clipped gradient norm, and
  post-update parameters before full training;
- label the resulting endpoint as dtype remediation, not as an unchanged primary-screen rerun.

This change tests the diagnosed precision-path defect without tuning LR or choosing a checkpoint
after seeing evaluation metrics. If the optimizer-step smoke or full endpoint is still non-finite,
StableLM is excluded from the primary family comparison; any LR/optimizer experiment requires a
separate exploratory plan.

### Retry preflight correction required

The first Llama-only retry attempt submitted preflight `410100` and dependent array `410101_[3]`.
Preflight failed because the original family contract required candidate indices 0, 1, and 2 in
every training wave, including retries. The dependent job never ran or consumed a GPU and was
canceled. The failed Llama tree from `409429_3` remains preserved at
`failed_runs/training_409429/llama`.

The local correction adds an explicit `allow-subset-retry` preflight mode. It is permitted only for
the training stage, requires explicit candidate indices, and preserves all commit, source-hash,
model-manifest, dataset, output-absence, home/scratch, capacity/inode, and duplicate-job gates.
Normal acquisition/training/evaluation family waves retain the required-candidate rule. After the
correction is pushed and the HU suite passes, StableLM remediation and Llama retry may be submitted
as a coordinated two-task retry wave with clean, distinct output roots. Their strengthened smoke
gates must pass before either full training proceeds.

The remediation implementation was committed as `1c8fa35`. Its first authoritative HU test run
found one test-fixture path outside the mocked scratch root; the production safety check correctly
rejected that path. No retry job was submitted under that failing test state. The fixture was
corrected in commit `553e441`, pushed by the agent at the user's request, and HU then passed the
complete 166-test suite at exact commit `553e441aa3453a3863f9cc08dc30472271683696`.

The invalid StableLM endpoint was preserved, not deleted, under:

```text
/vol/tmp2/yesildau/m1_cross_family_screen_v1/failed_runs/training_409429/stablelm
```

With StableLM and Llama active output roots absent, the coordinated subset-retry wave was submitted:

| Job | Purpose | Initial state |
|---|---|---|
| `410102` | StableLM/Llama subset training preflight with all normal storage/source/duplicate gates | `RUNNING` on `gruenau`; stderr empty |
| `410103_[1,3]` | StableLM BF16 remediation and Llama clean retry | `PENDING (Dependency)` on `410102` |

The next inspection must first verify preflight PASS, distinct physical GPU allocations, and a
finite strengthened smoke report for each task. In particular, StableLM may proceed to full
training only if its configured batch-10, accumulation-50 AdamW smoke update reports finite loss,
gradient norm, and post-update parameters. The expected smoke window is approximately 10--15
minutes; successful full training is expected to take approximately 60--100 minutes depending on
allocation and checkpoint throughput.

### Subset-retry early validation

Preflight `410102` passed and released both retry tasks onto distinct physical A100 80GB devices on
`gruenau9`: StableLM task `410103_1` received GRES `IDX:0`, and Llama task `410103_3` received
`IDX:1`. At approximately seven minutes both jobs remained `RUNNING` with `Reason=None`,
`ExitCode=0:0`, and clean stderr.

The strengthened smoke gates passed before full training:

| Candidate | Load dtype | Batch / accumulation | Optimizer steps | Finite loss | Finite clipped grad norm | Peak allocated |
|---|---|---|---:|---:|---:|---:|
| StableLM remediation | BF16 | 10 / 50 | 1 | 7.2780113 | 308.0 | 16,720,175,616 bytes |
| Llama retry | native BF16 | 10 / 50 | 1 | 7.2805891 | 266.0 | 12,708,794,880 bytes |

Both smoke checkpoints were successfully saved, reloaded, and removed. Each full Trainer run then
reached and wrote `checkpoint-25` with no traceback, OOM, NCCL, or non-finite marker. Stdout metric
records remained buffered at this early check, so endpoint validity is not yet claimed. However,
StableLM's prior FP16 run had already produced non-finite gradients in its first logging window;
reaching checkpoint 25 after a finite accumulated optimizer-step smoke is strong early evidence
that the diagnosed dtype remediation corrected that immediate failure mode. Do not evaluate or
select either retry until update 252, final finite metrics, and endpoint manifests are verified.

### Overlapped completed-subset evaluation wave

To reduce idle wall time without evaluating incomplete models, commit `eaee347` added an explicit
completed-subset evaluation mode. It permits only the evaluation stage, requires explicit candidate
indices, and still requires a unique completed endpoint for every selected candidate plus all
normal source-hash, output-absence, storage, inode, capacity, and duplicate-job gates. It does not
permit partial scientific selection; comparison and selection remain deferred until all admissible
candidate results are available.

The agent pushed `eaee347`, HU fast-forwarded to exact commit
`eaee347c67dc3ecd9c895f3da50976af8dbcaa9a`, and the complete 167-test suite passed. Qwen and Gemma
evaluation roots were verified absent. Their completed endpoints were then submitted as a parallel
evaluation subset while StableLM and Llama training continued:

| Job | Purpose | Initial state |
|---|---|---|
| `410105` | Qwen/Gemma completed-subset evaluation preflight | `RUNNING` on `gruenau`; stderr empty |
| `410106_[0,2]` | Qwen and Gemma parallel evaluation tasks | `PENDING (Dependency)` on `410105` |

StableLM and Llama remained `RUNNING` as tasks `410103_1` and `410103_3` at the submission check.
No evaluation is permitted to consume those retry endpoints until their training manifests and
finite final metrics are verified. The Qwen/Gemma subset results may be computed and frozen now,
but must not be used to alter gates, StableLM/Llama training, or the precommitted final selection
rule.

### First evaluation results, Gemma retry, and Llama completion

Qwen evaluation task `410106_0` completed successfully in `00:21:49`. Its frozen results are:

- exact-prefix top-1: 500/500 (`1.000`);
- hard-suite top-1: 3,997/4,000 (`0.99925`);
- relation-swapped forced choice: 1,598/1,600 (`0.99875`);
- all-required-cell intersection by relation: 99--100%;
- failure taxonomy: one prompt-form failure and two same-subject relation swaps;
- base PPL `14.6988390`, trained PPL `21.4717611`, ratio approximately `1.46078`;
- generic completion top-1 changed from 27/30 to 29/30, but repetition metrics worsened.

Qwen therefore passes the frozen factual-storage, held-out-form, robust-intersection, and relation
binding gates but **fails** the frozen generic-capability PPL-ratio gate (`1.46078 > 1.25`). Its
endpoint and evaluations remain valid evidence, but Qwen cannot be declared a passing candidate or
selected under Document 105.

Gemma evaluation task `410106_2` failed after `00:02:11` on `gruenau10`. It encountered the same
separate PID `54819` consuming 72.43 GiB that had previously broken Llama training on that node.
This second independent recurrence is treated as a persistent node/allocation anomaly, not a Gemma
model failure. The partial Gemma evaluation tree was preserved at
`failed_runs/evaluation_410106/gemma`. Preflight `410108` then passed, and Gemma retry
`410109_2` was submitted with `gruenau10` explicitly excluded; it entered `RUNNING` on `gruenau9`
with clean initial stderr. Do not kill or otherwise interact with PID `54819`; preserve the two job
IDs, node, PID, and OOM messages for a possible HU administrator report.

Llama retry task `410103_3` completed successfully after `2355.1984` seconds with
`train_loss=0.24202736`, `eval_loss=0.0001387198`, manifest `complete`, and clean stderr. StableLM
remediation task `410103_1` remained `RUNNING` at least through checkpoint 175 with no non-finite
or runtime error. Llama evaluation is deferred until the current Gemma evaluation leaves the queue,
so the duplicate-evaluation preflight is not bypassed. StableLM evaluation remains prohibited until
its update-252 endpoint and finite final metrics are verified.

### StableLM remediation completion and Gemma retry progress

StableLM BF16 remediation task `410103_1` completed successfully on `gruenau9` with
`ExitCode=0:0` after `00:53:48`. The final manifest reports `complete`, with
`train_runtime=3116.3099` seconds, `train_loss=0.26217887`, and
`eval_loss=0.0001764308`. Late-epoch losses and gradient norms remained finite, and stderr contains
no traceback, OOM, NCCL, or non-finite marker. This confirms that the explicit BF16 load plus
optimizer-step smoke corrected the immediate FP16 numerical-divergence failure. The result remains
formally labeled a single-variable dtype remediation and awaits the frozen evaluation gates.

Gemma evaluation retry `410109_2` remained `RUNNING` on `gruenau9` with `Reason=None`,
`ExitCode=0:0`, and clean stderr. Its hard-suite progress reached 3,300/4,000 probes (82.5%). Exact
prefix and base/trained general-capability stages remain after the hard suite. Llama and StableLM
evaluation submission is deferred until this active evaluation leaves the queue, preserving the
duplicate-evaluation preflight rule.

### Concurrent disjoint StableLM/Llama evaluation wave

At the user's request, completed StableLM and Llama endpoints were scheduled for evaluation while
the disjoint Gemma retry continued. Commit `ae42a2e` extended duplicate-job detection to understand
Slurm array task indices: an active evaluation for another candidate may overlap, but an active or
pending task for the same selected candidate remains a hard duplicate. Compressed/unparseable array
identities fail closed. Endpoint uniqueness, output-absence, storage, source-hash, and capacity
checks remain unchanged.

The agent pushed `ae42a2e`; HU fast-forwarded to exact commit
`ae42a2ef1557532eebccabaa664826d40cfe5615` and passed the complete 168-test suite. StableLM and
Llama evaluation roots were absent. Preflight `410110` passed, then evaluation array
`410111_[1,3]` was submitted with `gruenau10` excluded. StableLM task `410111_1` and Llama task
`410111_3` both entered `RUNNING` on `gruenau9` with empty initial stderr while Gemma retry
`410109_2` continued on the same three-A100 node. Final scientific comparison remains deferred
until all three tasks finish and their compact metrics are verified.
