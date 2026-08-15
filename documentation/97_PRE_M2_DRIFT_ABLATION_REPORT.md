# 97 - Pre-M2 Drift Ablation Report

**Date:** 2026-07-18  
**Status:** WP5 complete; `5e-5`, EOS false, step 252 replicated and selected  
**Parent plan:** `93_PRE_M2_SUPERVISOR_FOLLOWUP_EXPERIMENT_PLAN.md`  
**Previous wave:** `96_PRE_M2_JOINT_RELATION_CONTROL_REPORT.md`

## 1. Scope

WP5 tests whether the previously measured 17--19% WikiText-2 perplexity increase is driven mainly
by learning-rate magnitude, supervised answer-final EOS, or their interaction. Stage 1 freezes the
canonical 100-subject/500-fact Relation V2 seed-42 recipe and varies only learning rate:

```text
2e-5, 5e-5, 1e-4, 2e-4
```

The existing frozen seed-42 `1e-4` run is the historical reference. New Stage 1 training is needed
for `2e-5`, `5e-5`, and `2e-4`. Each condition retains 3,500 training rows, 500 validation rows,
36 epochs, effective batch 500, 252 optimizer updates, answer-only loss, supervised EOS, seed/data
seed 42, and checkpoints at approximately updates 25, 50, 75, 100, 150, 200, and 252.

## 2. EOS Integrity Correction

Pre-launch code inspection found that `supervise_eos` was present in configs but the answer-only
trainer always appended EOS to the supervised labels. This did not change earlier `true` runs, but
would have invalidated Stage 2's `false` condition. Commit `134ffbd` makes the switch operational:

- `true` supervises answer tokens plus final EOS;
- `false` preserves identical inputs, prompts, answer-token labels, row order, and batching while
  replacing only the final EOS label with `-100`.

A unit test freezes this exact label-level contract. The complete local suite passed with four
expected skips; all 31 targeted HU training-core tests passed.

## 3. HU Preflight And Active Smoke

Before submission:

- HU home usage was `8.0G`;
- `/vol/tmp2` had approximately `118T` free with 3% inode use;
- `runs`, `artifacts`, and the base SmolLM2-1.7B weight resolved to approved scratch;
- each new condition has an upper-bound estimate of 225 GB, or 675 GB for the three-run family;
- retained scientific artifacts will be selected using both factual and generic-retention metrics.

GPU smoke job `406927` used the `2e-5` config because learning rate does not change tensor shapes
or memory demand. It passed with loss `6.0371`, 218 gradient tensors, and 7.29 GB peak GPU
allocation. The manifest explicitly recorded `supervise_eos: true`. HU home remained `8.0G`.

The three new Stage 1 conditions were submitted in parallel:

| Job | Learning rate | EOS | Initial state | Expected duration |
|---:|---:|---|---|---:|
| `406928` | `2e-5` | supervised | pending | 45-60 minutes |
| `406929` | `5e-5` | supervised | pending | 45-60 minutes |
| `406930` | `2e-4` | supervised | pending | 45-60 minutes |

The frozen historical `1e-4` seed-42 run remains the reference rather than consuming a fourth
training job.

All three jobs completed without runtime exceptions; stderr contained only normal model-loading
and evaluation progress. Training-only outcomes are:

| Job | LR | Runtime | Final monitoring eval loss | Run-level train loss |
|---:|---:|---:|---:|---:|
| `406928` | `2e-5` | 51m 42s | `0.8972` | `1.669` |
| `406929` | `5e-5` | 52m 36s | `0.05843` | `0.5442` |
| `406930` | `2e-4` | 52m 40s | `0.0002502` | `0.1804` |

These losses are not the LR selection metric. Each run produced the complete expected checkpoint
family, including predeclared updates 25, 50, 75, 100, 150, 200, and 252. HU home remained `8.0G`.
The next wave evaluates those seven checkpoints for all four LRs on the frozen hard factual,
exact-prefix, WikiText-2, generation, and generic-completion controls.

The checkpoint wave was frozen as 28 live-hashed model-only manifests. Optimizer, scheduler, RNG,
trainer-state, and training-argument files are deliberately excluded from evaluation manifests;
they remain resumable scratch state rather than frozen model evidence. The registry SHA-256 is
`08787a73d4d07a5f042d143aecc2c9751a56309ab6496ec68b6ad0fc019dbec6`.

Slurm array `406933` contains tasks 0--27 with at most eight concurrent GPUs. Every task runs, for
one LR/checkpoint pair:

1. the frozen 3,000-probe paraphrase hard suite;
2. the 500-fact exact-prefix backward-compatibility evaluation; and
3. the frozen WikiText-2 loss, generation, and generic-completion suite.

The array was submitted after a fresh storage audit: HU home `8.0G`, `/vol/tmp2` approximately
`118T` available, and scratch inode use 3%. Expected task runtime is approximately 20--35 minutes;
overall wall time depends on scheduler throughput.

### Evaluator compatibility correction

Array `406933` stopped before producing completed scientific results. The WP3 extension had made
`field_of_study` and `works_in_industry` request same-subject `studied_at` and `works_at` objects,
but the immutable Relation V2 canonical profile intentionally lacks university and employer
columns. Every task therefore stopped with `KeyError: university_en` before exact-prefix or
general-capability evaluation. This is an evaluator compatibility failure, not a model result.

Commit `501bc7f` now adds relation-swapped candidates only when the corresponding canonical columns
exist. WP3's merged four-relation profile retains the bidirectional hard pairs; Relation V2 runs
skip only the unavailable cross-family pairs. Thirteen targeted local and HU tests passed. The
launcher now resumes the valid partial hard-suite rows rather than recomputing them.

Corrected array `407687` was submitted for tasks 0--27 with the same frozen registry, model hashes,
thresholds, and maximum eight concurrent GPUs. No scientific selection was made from the failed
attempt.

The relation-column correction allowed hard-suite evaluation to complete. The first six tasks
then exposed a second legacy-schema incompatibility: the exact-prefix CSV predates the evaluator's
explicit `language` column, so exact evaluation stopped with `KeyError: language` and general
evaluation did not begin. Commit `b57038c` now supplies the configured source language only when
that field is absent; existing explicit language values are preserved. All 30 evaluator-core tests
passed locally and on HU. The shared code was updated for running/pending tasks, and failed indices
0--5 were resubmitted as array `407774` with hard-suite resume enabled. Again, no model metric was
used to alter the frozen design.

The language correction exposed the final missing legacy field group: exact-prefix probes omit
branch, relation-frequency, popularity, name-type, and name-rarity metadata because those values
already live in the canonical subject profile. Exact tasks therefore recorded 500 row failures and
stopped as `partial_failed`; hard-suite outputs remained valid. Commit `4782481` now preserves any
explicit probe metadata and otherwise derives these subgroup fields from the frozen canonical row
and relation-frequency column. All 31 evaluator-core tests passed locally and on HU. Pending retry
array `407774` will use the corrected code for indices 0--5; failed indices 6--20 were resubmitted
as array `407943`. The still-running original indices 21--27 received the shared code update before
their downstream exact/general stages where scheduler timing allowed. Any remaining failed index
will be resumed without recomputing its completed hard-suite output.

After exact-prefix evaluation began succeeding, completed retry tasks exposed an independent
general-capability input-path failure. Their generated configs referenced the repository-local
`artifacts/evaluation/general_capability_v1/wikitext2_raw_test.jsonl` symlink, whose stale target
resolved to a missing `/vol/tmp` file. The frozen corpus itself remained intact at
`/vol/tmp2/yesildau/general_capability_v1/wikitext2_raw_test.jsonl` (1,443,228 bytes). Thus the
hard and exact outputs produced before this point remain valid; no general-capability metric was
available and no scientific decision was made.

Commit `3d48c20` makes `--general-corpus` a required preparation argument, rejects paths outside
approved scratch, and verifies that the corpus exists before generating the wave. All 28 live
general configs were updated to the verified `/vol/tmp2` corpus. Failed indices 0--15 and 21--27
were resubmitted as array `408010` with hard/exact resume behavior. Indices 16--20 under array
`407943` reached the missing input before the live config correction and also failed; they were
therefore resubmitted as array `408017`. At the immediate post-submit check, tasks 0--5 of
`408010` were running, all other retry tasks were pending for resources, and no early traceback
was present. HU home remained `8.0G`; the correction changes only input location, not data,
models, probes, or metrics.

Arrays `408010` and the unaffected retry paths subsequently produced 23 of 28 complete
general-capability summaries. The first retry submission for indices 16--20 (`408017`) was issued
from the HU home directory rather than the repository, so Slurm set `SLURM_SUBMIT_DIR` to home and
the launcher could not find `scripts/evaluate_pre_m2_frozen_suite.py`. This was a submission
working-directory error before evaluator execution, not a scientific failure. After verifying the
repository script, corpus, scratch root, capacity, and inodes, the five indices were resubmitted
from the repository as array `408038`. Their existing hard/exact outputs remain resumable; no
threshold, checkpoint, input data, or evaluation setting changed.

## 4. Stage 1 Results And Pareto Decision

All 28 LR/checkpoint conditions completed the frozen 3,000-probe hard suite, 500-fact exact-prefix
evaluation, and general-capability suite. The queue was empty and all general summaries reported
`completion_status: completed`. A reusable aggregator was added in commit `914cce6`; its compact
outputs are:

| Artifact | SHA-256 |
|---|---|
| `wp5_checkpoint_summary.csv` | `a0b36434ae7742ebfe98bfcf81a62f1fe3d1da4a5b30ce5dacdf07b02955fd11` |
| `wp5_checkpoint_summary.json` | `99f261770b7d64cbf76460a6825e0618c6f38c3d4ddae1bf28b9cf00aaccc0f0` |

The decisive checkpoints are summarized below. Hard accuracy is across 3,000 prompt probes;
robust is the 1,000 fact/scaffold all-three-form intersection; forced choice contains 1,200
available relation-confusable comparisons. PPL ratios use the frozen base value `15.9240`.

| LR / step | Hard | Robust | Forced choice | Exact | PPL | Ratio | EOS endings |
|---|---:|---:|---:|---:|---:|---:|---:|
| `2e-5 / 252` | 29.4% | 8.1% | 52.2% | 72.0% | 16.632 | 1.044 | 7/30 |
| `5e-5 / 100` | 72.8% | 43.8% | 66.8% | 100% | 17.026 | 1.069 | 28/30 |
| `5e-5 / 252` | 74.1% | 46.9% | 67.4% | 100% | 17.143 | 1.077 | 27/30 |
| `1e-4 / 50` | 93.2% | 85.1% | 89.7% | 99.8% | 18.757 | 1.178 | 30/30 |
| `1e-4 / 200` | 96.1% | 90.2% | 93.3% | 100% | 19.018 | 1.194 | 30/30 |
| `2e-4 / 25` | 96.0% | 90.6% | 98.4% | 99.4% | 33.070 | 2.077 | 30/30 |
| `2e-4 / 252` | 97.7% | 93.3% | 99.4% | 100% | 36.341 | 2.282 | 30/30 |

The controlled sweep establishes a strong update-magnitude trade-off. `2e-5` stays inside the
no-material-drift band but does not learn the robust factual task sufficiently. `2e-4` reaches the
highest factual scores but causes material generic-loss degradation even by update 25. `1e-4`
reproduces the historical measurable-drift regime. `5e-5` reaches exact-prefix saturation by
update 100, remains below the precommitted 1.10 PPL-ratio boundary through update 252, and avoids
the generic-loss damage of the higher LRs, although prompt robustness remains materially below the
`1e-4` condition.

The Stage 1 Pareto LR is therefore **`5e-5`**, with checkpoint 252 as its maximum-factual endpoint
and checkpoint 100 as an earlier near-Pareto point. This selection is based on the precommitted
joint factual/retention criteria, not validation loss. The historical `1e-4` LR remains the
required Stage 2 reference because it is different from the selected LR. The persistent 27--28/30
EOS-ending rate at `5e-5`, despite a PPL ratio below 1.10, also shows why the controlled EOS-label
ablation remains necessary; Stage 1 alone cannot attribute that stopping bias causally.

Generic-completion top-1 remained 30/30 for every condition, so the LR effect is generic token
loss and stopping behavior rather than collapse of the frozen common-knowledge ranking control.

## 5. Post-Run Storage Audit And Next Step

The final audit recorded HU home at `8.0G`, `/vol/tmp2` with approximately `118T` available and 3%
inode use, and no experiment checkpoint or evaluation tree written into home. Home files above
500 MB were limited to known Conda environment libraries. Scientific outputs and model artifacts
remain on `/vol/tmp2`; compact hashes and conclusions are recorded here.

WP5 Stage 2 must now train the otherwise identical `supervise_eos: false` conditions at `5e-5`
and historical-reference `1e-4`. Their existing `true` runs are the frozen controls. The Stage 2
wave must preserve the same rows, order, update budget, checkpoints, and evaluator suite, changing
only the final EOS label mask.

## 6. Stage 2 EOS-Ablation Launch

Commit `cdcd68a` added the `5e-5` and `1e-4` EOS-false configs and generalized the existing WP5
launcher to accept an explicit `EOS_LABEL=true|false`. A controlled-pair test verifies identical
dataset, model, runtime, LR-specific hyperparameters, row order, epochs, batching, update budget,
and checkpoint schedule; only `supervise_eos`, run identity, and scratch output root differ. All 32
training-core tests passed locally and on HU.

The launch preflight recorded HU home at `8.0G`, `/vol/tmp2` with approximately `118T` free and 3%
inode use, and `runs`, `artifacts`, and base weights resolving to approved scratch. Both new output
roots were absent before launch. The two-condition upper-bound estimate is 450 GB on scratch.

GPU smoke job `408043` passed on `gruenau9` with `supervise_eos: false`, loss `6.8431`, 218 gradient
tensors, and 7.29 GB peak allocation. The two Stage 2 training jobs were then submitted in parallel:

| Job | LR | EOS supervision | Initial node/state | Expected duration |
|---:|---:|---|---|---:|
| `408044` | `5e-5` | false | `gruenau9`, running | 50--60 minutes |
| `408045` | `1e-4` | false | `gruenau9`, running | 50--60 minutes |

Both jobs entered `RUNNING`, reported the expected 3,500 train rows, 500 validation rows, 252
optimizer updates, scratch output roots, and clean initial stderr. Existing EOS-true runs are reused
as frozen controls and were not retrained.

Both EOS-false jobs completed successfully with clean stderr and all 11 saved checkpoints:

| Job | LR | Runtime | Final monitoring eval loss | Run-level train loss | Final-model SHA-256 |
|---:|---:|---:|---:|---:|---|
| `408044` | `5e-5` | 50m 45s | `0.10140` | `0.74825` | `96c5a7e2118aa1dbdf09de73771a220cdc2b016fe9bd15e5d1665ae0bc3db906` |
| `408045` | `1e-4` | 51m 43s | `0.003161` | `0.36553` | recorded in the frozen checkpoint manifests |

These training losses are monitoring evidence, not the EOS-ablation decision metric. The same
predeclared steps 25, 50, 75, 100, 150, 200, and 252 were frozen for evaluation for both LRs.
Their 14-task registry is at
`/vol/tmp2/yesildau/pre_m2_followup_v1/wp5_eos_ablation_checkpoint_wave/checkpoint_registry.csv`
with SHA-256 `cda8120191ba656e1b0f55cb2b89d5130b36b316d76a0cc791441edb71fd5f67`.

Evaluation array `408046` was submitted with at most eight concurrent GPUs. Each task runs the
same frozen 3,000-probe hard suite, 500-fact exact-prefix evaluation, and general-capability suite
used in Stage 1. HU home remained `8.0G`; `/vol/tmp2` had approximately `117T` free with 3% inode
use.

The manifest preparation hashes multiple multi-gigabyte checkpoints while `conda run` normally
buffers stdout. The initiating SSH calls therefore appeared to end before their delayed `sbatch`
commands became visible, and two redundant arrays (`408053` and `408054`) were subsequently
submitted. A provenance check against Slurm log paths established that `408046` was the original
array producing the canonical output tree. Arrays `408053` and `408054` were immediately canceled;
`408054` had not started, while only task 0 of `408053` had briefly run against the identical frozen
registry and shared resume-safe output. No metric, model, or input differed, and no output was
deleted. The canonical active array remains `408046`. At that audit it had produced 12/14 hard,
13 completed exact run summaries (including the harmless duplicate task-0 attempt), and 9/14
general summaries with no traceback in its stderr logs.

## 7. Stage 2 Results And Mechanism Decision

Canonical array `408046` completed all 14 unique hard, exact, and general-capability conditions
without evaluator traceback. The EOS-false compact evidence is frozen as:

| Artifact | SHA-256 |
|---|---|
| `wp5_checkpoint_summary.csv` | `2213993a08b5d1ee39957579b67a64c9dcbee98b3f0648018d326cc94de2323b` |
| `wp5_checkpoint_summary.json` | `d78c9bb78d7c083c29f0257579c3f6534adff9243b0fc09ffd3184678072b263` |

Matched true/false checkpoints show the decisive comparisons below. Hard accuracy is across 3,000
probes; robust is the 1,000 fact/scaffold all-three-form intersection.

| LR / step | EOS | Hard | Robust | Forced choice | Exact | PPL ratio | EOS endings |
|---|---|---:|---:|---:|---:|---:|---:|
| `5e-5 / 100` | true | 72.8% | 43.8% | 66.8% | 100% | 1.069 | 28/30 |
| `5e-5 / 100` | false | 75.0% | 48.1% | 69.1% | 100% | 1.074 | 0/30 |
| `5e-5 / 252` | true | 74.1% | 46.9% | 67.4% | 100% | 1.077 | 27/30 |
| `5e-5 / 252` | false | 77.9% | 52.4% | 71.2% | 100% | 1.082 | 0/30 |
| `1e-4 / 50` | true | 93.2% | 85.1% | 89.7% | 99.8% | 1.178 | 30/30 |
| `1e-4 / 50` | false | 94.1% | 86.2% | 93.8% | 100% | 1.114 | 0/30 |
| `1e-4 / 252` | true | 96.3% | 91.0% | 93.7% | 100% | 1.196 | 30/30 |
| `1e-4 / 252` | false | 95.7% | 89.1% | 94.8% | 100% | 1.117 | 0/30 |

Removing final-answer EOS supervision eliminates the stopping-behavior signal at every evaluated
checkpoint: all 14 EOS-false conditions ended 0/30 frozen open generations with EOS, versus
27--30/30 at learned EOS-true checkpoints. Empty/near-empty generations also fell to zero. This is
strong controlled evidence that supervised answer-final EOS caused the observed short-answer
stopping bias in seed 42.

The generic-loss effect interacts with LR. At `1e-4`, EOS removal reduces step-252 PPL from
`19.037` to `17.792` and its ratio from `1.196` to `1.117`, recovering about 6.5% relative PPL but
leaving measurable drift above the 1.10 boundary. At `5e-5`, EOS removal does not improve generic
loss: step-252 PPL changes only from `17.143` to `17.234` and the ratio from `1.077` to `1.082`.
Thus EOS supervision explains the stopping bias and a substantial LR-dependent share of the
`1e-4` generic drift, but it does not explain all generic drift.

At `5e-5`, EOS removal improves the step-252 hard score by 3.7 points, robust all-form intersection
by 5.5 points, and relation-confusable forced choice by 3.8 points while preserving 100% exact
retrieval and the no-material-drift PPL band. The discovery-stage Pareto recipe is therefore
**`5e-5`, `supervise_eos: false`, checkpoint 252**. Generic-completion ranking remains 30/30 for
every EOS-false condition.

This is a seed-42 controlled mechanism result. Per the precommitted plan, causal wording remains
provisional until the selected Pareto recipe and its relevant control are replicated with
independent training/data seed 43. No broader factorial grid or generic rehearsal is activated.

The post-run audit recorded HU home at `8.0G`, `/vol/tmp2` with approximately `117T` free and 3%
inode use, and no experiment artifact newly placed in home. Files above 500 MB in home remained
known Conda environment libraries.

## 8. Seed-43 Paired Replication Launch

Commit `56226d7` added the independent seed/data-order 43 replication pair for the selected
`5e-5` LR. Dataset rows, model revision, objective, epochs, effective batch, scheduler, clipping,
precision, 252-update budget, and checkpoint schedule remain frozen; only `supervise_eos` differs
within the pair. Relative to discovery, only training seed and data-order seed change from 42 to
43. All 33 training-core tests passed locally and on HU.

The replication preflight recorded HU home at `8.0G`, `/vol/tmp2` with approximately `117T` free
and 3% inode use, all large paths resolving to scratch, and both output roots absent. GPU smoke job
`408063` passed with `supervise_eos: false`, 218 gradient tensors, and 7.29 GB peak allocation.

| Job | LR | EOS supervision | Seed/data seed | Initial node/state | Expected duration |
|---:|---:|---|---:|---|---:|
| `408064` | `5e-5` | true | 43/43 | `gruenau9`, running | 50--60 minutes |
| `408065` | `5e-5` | false | 43/43 | `gruenau9`, running | 50--60 minutes |

Both jobs entered `RUNNING` with the expected dataset hashes, 3,500/500 rows, 252 updates, scratch
output roots, and clean initial stderr. This paired replication is the final precommitted check
before promoting the seed-42 EOS mechanism result from provisional to replicated evidence.

Both seed-43 jobs completed successfully with clean stderr and all 11 expected checkpoints:

| Job | EOS | Runtime | Final monitoring eval loss | Run-level train loss |
|---:|---|---:|---:|---:|
| `408064` | true | 50m 31s | `0.07114` | `0.54350` |
| `408065` | false | 50m 31s | `0.11433` | `0.74537` |

Commit `8cfac0e` added explicit selected-checkpoint support to the wave preparer so replication does
not repeat the seven-checkpoint discovery sweep. Only the precommitted Pareto endpoint, step 252,
was frozen for each EOS condition. The two-task registry SHA-256 is
`50801b0ffa8d99853949cd194ad71d17dbee8fa2ac89876e9d5081c31287075e`.

Final replication evaluation array `408066` entered `RUNNING` on `gruenau9` with both tasks active,
the expected model-manifest hashes, 3,000 hard probes, 500 exact probes, the frozen general suite,
scratch output roots, and clean initial stderr. Expected wall time is approximately 5--10 minutes.

## 9. Replication Result And Final WP5 Decision

Array `408066` completed both selected-checkpoint tasks with 2/2 hard, 2/2 exact, and 2/2 general
summaries and no traceback. The compact replication evidence is frozen as:

| Artifact | SHA-256 |
|---|---|
| `wp5_checkpoint_summary.csv` | `c8105d09e70518c1b6d621d673fe20de7148d41e57f0a153cd00149c81423df5` |
| `wp5_checkpoint_summary.json` | `82ed96561b61217cc0d80c27ae4675c6ec19f3659c2b3e51f86af9296fa498fb` |

| Seed | EOS | Hard | Robust | Forced choice | Exact | PPL | PPL ratio | EOS endings |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 42 | true | 74.1% | 46.9% | 67.4% | 100% | 17.143 | 1.077 | 27/30 |
| 42 | false | 77.9% | 52.4% | 71.2% | 100% | 17.234 | 1.082 | 0/30 |
| 43 | true | 73.1% | 44.5% | 66.3% | 100% | 17.133 | 1.076 | 27/30 |
| 43 | false | 76.2% | 50.1% | 69.8% | 100% | 17.259 | 1.084 | 0/30 |

The paired effect replicated closely. EOS removal improved hard accuracy by 3.7 points in seed 42
and 3.1 points in seed 43; robust intersection by 5.5 and 5.6 points; and forced choice by 3.8 and
3.4 points. Exact retrieval remained 100% in all four conditions. Most decisively, EOS endings fell
from 27/30 to 0/30 in both independent seeds, while empty/near-empty outputs fell from 1 to 0.

EOS-false PPL was slightly higher than EOS-true at `5e-5` in both seeds, but all four ratios stayed
inside the precommitted no-material-drift band below 1.10. Therefore supervised answer-final EOS is
a replicated cause of the stopping bias and, at this LR, its removal improves prompt-robust factual
behavior without material generic-loss degradation. The earlier `1e-4` control additionally showed
that EOS supervision contributes substantially to generic drift at higher update magnitude, while
LR-dependent drift remains after EOS removal.

WP5 is complete. The final pre-M2 Pareto recipe is **SmolLM2-1.7B, LR `5e-5`, answer-only loss,
`supervise_eos: false`, checkpoint 252**. Seed 42 is the discovery artifact and seed 43 supplies the
independent replication. This selection follows the frozen factual/retention gates rather than
validation loss or post-hoc checkpoint search.

The final post-run audit recorded HU home at `8.0G`, `/vol/tmp2` with approximately `117T` free and
3% inode use, and no new large experiment artifact in home. Files above 500 MB in home remained the
known Conda environment libraries.
