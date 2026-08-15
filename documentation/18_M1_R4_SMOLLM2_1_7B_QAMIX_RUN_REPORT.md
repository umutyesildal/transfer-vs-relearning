# 18 - M1 R4 SmolLM2 1.7B QA-Mix Run Report

Date: 2026-07-07

## Purpose

This report records the first larger-model follow-up after the failed R3 continuation.

R4 keeps the same:

- dataset: `english_training_m1_r1_qamix_d2_q2.jsonl`
- learning rate: `5e-5`
- QA-mixed acquisition recipe

and changes:

- base model from `HuggingFaceTB/SmolLM2-360M` to `HuggingFaceTB/SmolLM2-1.7B`
- training length back to `1` epoch for a controlled first pilot

## Why R4 Was Chosen

R3 made the core diagnosis sharper:

- more exposure on the same SmolLM2-360M + QA-mix branch reduced retrieval quality,
- the next step should not be another same-family exposure increase,
- the most defensible next branch is a meaningfully larger model under the same stronger
  recipe.

R4 therefore tests whether capacity, rather than just exposure, is the missing ingredient
for English fact acquisition in M1.

## Training Config

Training config:

```text
configs/training/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1.yaml
```

Key settings:

- base model: `HuggingFaceTB/SmolLM2-1.7B`
- epochs: `1`
- learning rate: `5e-5`
- per-device train batch size: `2`
- gradient accumulation steps: `8`
- bf16: `true`
- gradient checkpointing: `true`

The batch settings were reduced conservatively to keep the 1.7B pilot memory-safe on the
HU A100 80GB node.

## Launch Verification

Training job:

```text
380489
```

Initial queue state after submission:

```text
RUNNING on gruenau9
```

Verified startup log:

- selected config matches the R4 file above,
- dataset path resolves to `english_training_m1_r1_qamix_d2_q2.jsonl`,
- model manifest resolves to `artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json`,
- runtime shows `NVIDIA A100 80GB PCIe`,
- no early stderr error was emitted at launch.

## Training Result

Training completed successfully.

Run directory:

```text
runs/training/m1_smollm2_1_7b_english_facts_r1_qamix/20260707T101345Z_m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1_2f6d82df
```

Completion time:

```text
2026-07-07T10:50:36Z
```

Final training metrics:

- train loss: `1.5105`
- eval loss: `1.3128`
- train runtime: `1975.92` seconds
- train steps per second: `0.413`
- estimated optimizer steps: `816`

Retained checkpoints:

- `checkpoint-204`
- `checkpoint-408`
- `checkpoint-612`
- `checkpoint-816`

## Checkpoint Evaluation Preparation

Prepared artifacts:

```text
runs/local_model_manifests/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1/
runs/local_configs/m1_checkpoint_eval_smollm2_1_7b_r1_qamix_lr5e-5_ep1/
```

The checkpoint evaluation protocol for R4 follows the same structure as R2 and R3:

- 4 checkpoints,
- 2 prompt styles per checkpoint,
- English direct and QA-matched results read from `per_fact_results.csv`.

## Evaluation Retry Notes

The first two evaluation submission attempts were not valid for interpretation.

First invalid attempt:

- jobs: `380490` through `380497`
- issue: shell variable expansion corrupted the checkpoint-specific file names, so the
  resolved config pointed to a malformed `checkpoint-` path
- action taken: all eight jobs were cancelled

Second invalid attempt:

- jobs: `380498` through `380505`, plus `380506` through `380516`
- issue: the submission path fell back to the default evaluator config
  `configs/evaluation/m0_gpt2_pilot_direct.yaml`, so logs showed base GPT-2 evaluation
  instead of R4 local-checkpoint evaluation
- action taken: those jobs were cancelled, checkpoint manifests/configs were regenerated
  with a Python-based writer, and the jobs were resubmitted with literal config paths

These retries are part of the run history and should not be hidden.

## Valid Evaluation Submission

The first valid R4 evaluation submission is:

- `380517`
- `380518`
- `380519`
- `380520`
- `380521`
- `380522`
- `380523`
- `380524`

Startup log was verified for `380517`:

- selected config:
  `runs/local_configs/m1_checkpoint_eval_smollm2_1_7b_r1_qamix_lr5e-5_ep1/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1_checkpoint-204_direct.yaml`
- selected model manifest:
  `runs/local_model_manifests/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1/checkpoint-204_model_manifest.json`
- output run root:
  `runs/evaluation/m1_smollm2_1_7b_english_facts_r1_qamix_lr5e-5_ep1_checkpoint-204_direct`

All eight valid evaluation jobs completed and produced checkpoint-specific evaluation CSVs.

## Current Status

```text
training complete; checkpoint evaluation complete
```

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-204` | `0.022` | `0.050` | `0.0542` | `75.800` | `-6.198` | `0.004` | `0.056` | `0.0545` | `64.902` | `-1.746` | `1/500` |
| `checkpoint-408` | `0.022` | `0.050` | `0.0543` | `75.808` | `-6.374` | `0.006` | `0.060` | `0.0584` | `64.272` | `-1.789` | `1/500` |
| `checkpoint-612` | `0.024` | `0.050` | `0.0555` | `75.912` | `-6.485` | `0.006` | `0.062` | `0.0590` | `63.884` | `-1.793` | `1/500` |
| `checkpoint-816` | `0.024` | `0.050` | `0.0553` | `75.898` | `-6.478` | `0.006` | `0.060` | `0.0587` | `64.034` | `-1.794` | `1/500` |

Best checkpoints under each view:

- best direct top1: `0.024` at `checkpoint-612` and `checkpoint-816`
- best QA top1: `0.006` at `checkpoint-408`, `checkpoint-612`, and `checkpoint-816`
- best robust overlap: `1/500`

## Interpretation

R4 is mixed and should be treated as a negative M1 result overall.

What improved:

- direct top1 recovered to `0.024`, which matches the best project-wide direct mark seen in
  the earliest GPT-2 pilot,
- training loss and eval loss are the strongest in the current M1 family,
- the bigger model clearly did not collapse on the direct prompt side.

What got worse:

- QA top1 fell to `0.006`, far below R1 (`0.030`) and R2 (`0.024`),
- robust direct-and-QA overlap fell to `1/500`, which is worse than R3 (`2/500`) and much
  worse than R1/R2 (`5/500`),
- all mean margins remained negative in both prompt styles.

Relative to the strongest earlier branches:

- versus R2:
  - direct top1 improved from `0.022` to `0.024`
  - QA top1 dropped from `0.024` to `0.006`
  - robust overlap dropped from `5/500` to `1/500`
- versus R3:
  - direct top1 improved from `0.018` to `0.024`
  - QA top1 stayed weak (`0.008` to `0.006`)
  - robust overlap dropped from `2/500` to `1/500`

This means the larger model helped direct retrieval somewhat, but it did not create stable,
prompt-robust English fact acquisition under the project gate.

## Decision

```text
Do not promote any checkpoint from M1-R4 as M1.
```

## What We Learned

R4 sharpens the diagnosis again:

- capacity alone is not enough,
- the current QA-mixed CLM recipe can raise direct retrieval without producing prompt-robust
  fact access,
- the remaining bottleneck now looks more like objective or supervision mismatch than raw
  model size.

## Next Action

Default next branch:

```text
do not spend another run on the same CLM + QA-mix family without changing the objective
```

Most plausible next directions:

1. answer-targeted supervision rather than plain CLM continuation,
2. a cleaner separation between fact acquisition and prompt-format adaptation,
3. a different model family only if paired with an objective change.
