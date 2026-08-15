# 13 - M1 R1 Stronger Repetition Plan

Date: 2026-07-06

## Goal

This document defines the first explicit recipe change after the GPT-2 and SmolLM2 pilots.

The purpose of M1-R1 is to test whether the main bottleneck is weak acquisition signal
rather than model-loading infrastructure or small hyperparameter differences.

## Core Change

M1-R1 does not switch the base model first.

It keeps:

- base model: GPT-2,
- optimizer/scheduler family,
- learning rate: `5e-5`,
- training epochs: `1`,
- existing checkpoint-evaluation protocol.

It changes the English-side training data recipe.

## New Training Dataset

Input file:

```text
artifacts/datasets/synthetic_v1/output/english_training.jsonl
```

Derived file:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl
```

Summary file:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2_summary.json
```

## R1 Dataset Recipe

The derived dataset is built from the pinned English synthetic training rows.

For every fact:

1. keep declarative English training rows,
2. duplicate declarative rows with multiplier `2`,
3. add QA-style rows with multiplier `2`,
4. format QA rows as:

```text
Question: <english probe-style question>
Answer: <canonical answer>
```

This creates a stronger answer-oriented signal while staying inside a causal LM training
setup.

## Why This Recipe

The current dataset already uses multiple declarative templates, but it does not directly
teach the prompt-to-answer form used by the stricter QA-matched probe.

R1 is intended to test two hypotheses together:

1. the model may need much denser English-side exposure,
2. the model may need explicit prompt-answer surface forms during M1 acquisition.

## Generated Dataset Size

Derived summary:

- input row count: `104169`
- output row count: `416676`
- declarative row count: `208338`
- QA row count: `208338`
- unique fact count: `25000`

Frequency-bucket scaling:

- low: `60300` -> `241200`
- medium: `33864` -> `135456`
- high: `10005` -> `40020`

This is exactly a `4x` expansion over the original English training rows.

## Implementation Artifacts

New builder module:

```text
src/transfer_vs_relearning/training/recipe_data.py
```

CLI script:

```text
scripts/build_m1_recipe_dataset.py
```

New training config:

```text
configs/training/m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1.yaml
```

Local validation:

```text
PYTHONPATH=src python3 -m pytest tests/test_recipe_data.py tests/test_training_core.py -q -ra
```

Result:

```text
7 passed
```

## Launch Plan

Build the derived dataset if it is missing:

```bash
PYTHONPATH=src python scripts/build_m1_recipe_dataset.py \
  --input artifacts/datasets/synthetic_v1/output/english_training.jsonl \
  --output artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl \
  --summary-output artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2_summary.json
```

Then submit:

```bash
sbatch --export=ALL,TRAIN_CONFIG=configs/training/m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1.yaml slurm/train_m1_gpt2_english_facts.slurm
```

## Success Criterion

R1 is successful only if checkpoint evaluation improves the English learned-fact gate
relative to the strongest previous GPT-2 pilot.

Current GPT-2 best to beat:

- direct top1: `0.024`
- QA-matched top1: `0.024`
- robust direct-and-QA overlap: `5/500`

If R1 does not beat that level meaningfully, move to step `2` in the agreed sequence:

```text
bigger model + stronger recipe
```
