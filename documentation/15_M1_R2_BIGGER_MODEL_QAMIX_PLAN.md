# 15 - M1 R2 Bigger Model QA-Mix Plan

Date: 2026-07-06

## Goal

This document defines the second escalation step after M1-R1 failed.

R2 keeps the stronger QA-mixed recipe from R1 and changes the base model to
SmolLM2-360M.

## Why R2 Exists

The sequence so far has isolated two different failure sources:

1. plain GPT-2 recipe variants failed,
2. a simple switch to SmolLM2-360M without recipe change also failed,
3. GPT-2 with stronger QA-mixed repetition still failed.

R2 is the first run that combines the two promising directions at once:

- bigger base model than GPT-2,
- stronger answer-oriented English acquisition recipe.

## Fixed Choices

R2 keeps:

- the same derived R1 dataset,
- the same causal LM training script,
- the same checkpoint-evaluation protocol,
- learning rate `5e-5`,
- `1` epoch for the first R2 pass.

R2 changes:

- base model from GPT-2 to `HuggingFaceTB/SmolLM2-360M`.

## Training Dataset

Train file:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl
```

Summary:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2_summary.json
```

## Launch Config

```text
configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1.yaml
```

## Launch Command

```bash
sbatch --export=ALL,TRAIN_CONFIG=configs/training/m1_smollm2_360m_english_facts_r1_qamix_lr5e-5_ep1.yaml slurm/train_m1_gpt2_english_facts.slurm
```

## Success Criterion

R2 should beat the best overall result seen so far, not just one prompt style.

Current mark to beat:

- best direct top1: `0.024`
- best QA top1: `0.030`
- best robust overlap: `5/500`

Minimum interpretation rule:

- do not promote a checkpoint that improves QA only while leaving direct retrieval collapsed,
- prioritize robust direct-and-QA overlap over one isolated top1 spike.

## If R2 Fails

Move to step `3` in the agreed sequence:

```text
bigger model + stronger recipe + more exposure
```

The default R3 continuation should be one of:

1. SmolLM2-360M + R1 dataset + `3` epochs, or
2. a larger next model class if SmolLM2-360M still remains far below gate.
