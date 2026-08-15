# 16 - M1 R2 SmolLM2 QA-Mix Run Report

Date: 2026-07-07

## Purpose

This report records the first run that combines:

- a bigger base model than GPT-2,
- the stronger R1 QA-mixed English acquisition recipe.

R2 is the first direct test of whether the earlier failures came from needing both a
stronger model and a stronger answer-oriented acquisition signal at the same time.

## Configuration

Plan document:

```text
documentation/15_M1_R2_BIGGER_MODEL_QAMIX_PLAN.md
```

Training config:

```text
configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1.yaml
```

Base model:

```text
HuggingFaceTB/SmolLM2-360M
```

Train file:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl
```

## Training Run

Slurm job:

```text
379336
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts_r1_qamix/20260706T082339Z_m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1_62ab81e7
```

Final training metrics:

- train loss: `1.956`
- eval loss: `1.751`
- train runtime: `300.8` seconds
- train steps per second: `2.713`

Retained checkpoints:

- `checkpoint-204`
- `checkpoint-408`
- `checkpoint-612`
- `checkpoint-816`

## Checkpoint Evaluation

Prepared artifacts:

```text
runs/local_model_manifests/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1/
runs/local_configs/m1_checkpoint_eval_smollm2_360m_r1_qamix_lr5e-5_ep1/
```

Submitted jobs:

- `380472`
- `380473`
- `380474`
- `380475`
- `380476`
- `380477`
- `380478`
- `380479`

All eight evaluation jobs completed.

Evaluation command pattern:

```bash
sbatch --export=ALL,EVAL_CONFIG=<checkpoint-config> slurm/eval_m0_gpt2_pilot.slurm
```

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-204` | `0.020` | `0.054` | `0.0573` | `76.740` | `-5.525` | `0.024` | `0.068` | `0.0666` | `69.392` | `-1.985` | `5/500` |
| `checkpoint-408` | `0.022` | `0.058` | `0.0561` | `76.726` | `-5.832` | `0.016` | `0.066` | `0.0607` | `68.196` | `-1.908` | `3/500` |
| `checkpoint-612` | `0.020` | `0.054` | `0.0547` | `76.666` | `-5.868` | `0.016` | `0.064` | `0.0602` | `68.094` | `-1.901` | `3/500` |
| `checkpoint-816` | `0.020` | `0.056` | `0.0545` | `76.686` | `-5.874` | `0.016` | `0.062` | `0.0603` | `68.068` | `-1.900` | `3/500` |

Best checkpoints under each view:

- best direct top1: `0.022` at `checkpoint-408`
- best QA top1: `0.024` at `checkpoint-204`
- best robust overlap: `5/500` at `checkpoint-204`

## Interpretation

R2 is better than the earlier SmolLM2-only pilot on the direct side.

Relative to the earlier SmolLM2 baseline pilot:

- direct top1 improved from `0.014` to `0.022`,
- robust overlap improved from `3/500` to `5/500`,
- QA top1 did not beat the best R1 GPT-2 QA spike of `0.030`.

Relative to the strongest project-wide marks to beat:

- target direct top1: `0.024`
- target QA top1: `0.030`
- target robust overlap: `5/500`

R2 matched the best robust overlap but did not beat it, and it still fell short on both
best direct and best QA top1.

All mean margins remained negative in both prompt styles.

## Decision

```text
Do not promote any checkpoint from M1-R2 as M1.
```

## What We Learned

R2 adds a useful new piece to the diagnosis:

- combining stronger recipe plus larger small model is better than either change alone,
- the failure is no longer as severe as the early GPT-2 and SmolLM2 pilots,
- but the learned-fact gate is still not crossed,
- so the next step should increase exposure further or change the supervision objective.

## Next Action

Default next branch:

```text
M1-R3 = SmolLM2-360M + R1 QA-mixed dataset + more exposure
```

Most conservative first continuation:

- keep the same dataset,
- keep the same learning rate,
- increase training from `1` epoch to `3` epochs,
- re-run the same checkpoint-evaluation protocol.
