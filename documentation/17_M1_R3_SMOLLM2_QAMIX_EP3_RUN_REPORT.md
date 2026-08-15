# 17 - M1 R3 SmolLM2 QA-Mix EP3 Run Report

Date: 2026-07-07

## Purpose

This report records the first higher-exposure continuation of the SmolLM2 QA-mixed branch.

R3 keeps the same:

- base model: `HuggingFaceTB/SmolLM2-360M`
- dataset: `english_training_m1_r1_qamix_d2_q2.jsonl`
- learning rate: `5e-5`

and changes only:

- training length from `1` epoch to `3` epochs.

## Why R3 Was Worth Testing

R2 was the strongest SmolLM2 branch so far, but it still failed the project-wide M1 gate:

- best direct top1: `0.022`
- best QA top1: `0.024`
- best robust overlap: `5/500`

R3 tests whether that branch was simply underexposed rather than fundamentally misaligned.

## Training Run

Training config:

```text
configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep3.yaml
```

Slurm job:

```text
380480
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts_r1_qamix/20260707T084629Z_m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep3_edc280af
```

Final training metrics:

- train loss: `1.7061`
- eval loss: `1.5707`
- train runtime: `1454.68` seconds
- train steps per second: `1.683`

Retained checkpoints:

- `checkpoint-612`
- `checkpoint-1224`
- `checkpoint-1836`
- `checkpoint-2448`

## Checkpoint Evaluation

Prepared artifacts:

```text
runs/local_model_manifests/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep3/
runs/local_configs/m1_checkpoint_eval_smollm2_360m_r1_qamix_lr5e-5_ep3/
```

Submitted jobs:

- `380481`
- `380482`
- `380483`
- `380484`
- `380485`
- `380486`
- `380487`
- `380488`

The evaluation CSV outputs were produced for all four checkpoints in both prompt styles.

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-612` | `0.018` | `0.050` | `0.0502` | `76.606` | `-6.088` | `0.006` | `0.054` | `0.0536` | `67.466` | `-1.865` | `2/500` |
| `checkpoint-1224` | `0.016` | `0.044` | `0.0490` | `76.432` | `-6.127` | `0.008` | `0.058` | `0.0546` | `66.870` | `-1.846` | `2/500` |
| `checkpoint-1836` | `0.014` | `0.046` | `0.0482` | `76.410` | `-6.105` | `0.008` | `0.060` | `0.0548` | `66.784` | `-1.841` | `2/500` |
| `checkpoint-2448` | `0.014` | `0.046` | `0.0483` | `76.432` | `-6.117` | `0.008` | `0.060` | `0.0542` | `66.804` | `-1.843` | `1/500` |

Best checkpoints under each view:

- best direct top1: `0.018` at `checkpoint-612`
- best QA top1: `0.008` at `checkpoint-1224`, `checkpoint-1836`, and `checkpoint-2448`
- best robust overlap: `2/500`

## Interpretation

R3 is a negative result.

Training loss improved further relative to R2, but retrieval did not.

Relative to R2:

- direct top1 dropped from `0.022` to `0.018`
- QA top1 dropped from `0.024` to `0.008`
- robust overlap dropped from `5/500` to `2/500`

This means more exposure on the same SmolLM2 + QA-mixed branch did not help. It made the
learned-fact gate weaker.

All mean margins remained negative in both prompt styles.

## Decision

```text
Do not promote any checkpoint from M1-R3 as M1.
```

## What We Learned

R3 sharpens the diagnosis:

- this is not just an undertraining problem,
- stronger repetition plus more epochs on the same small-model branch is not enough,
- future progress likely requires either a larger model class or a changed supervision
  objective rather than more of the same exposure.

## Next Action

Default next branch:

```text
move beyond the current SmolLM2 + QA-mix recipe family
```

Most plausible next directions:

1. a meaningfully larger model,
2. an objective that scores or generates answers more directly than plain CLM,
3. a recipe that separates acquisition from answer-format adaptation more explicitly.
