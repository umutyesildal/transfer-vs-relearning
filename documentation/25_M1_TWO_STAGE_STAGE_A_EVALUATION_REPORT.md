# 25 - M1 Two-Stage Stage A Evaluation Report

Date: 2026-07-07

## Purpose

This report records the English direct and QA-matched checkpoint evaluation for the first
Stage A run of the two-stage M1 branch.

The key question is whether biography-only acquisition already improves the English
learned-fact gate before any extraction-focused continuation.

## Training Run Under Evaluation

Training job:

```text
382768
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_biographies_stage_a/20260707T171129Z_m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_fa548873
```

Retained checkpoints:

- `checkpoint-146`
- `checkpoint-292`
- `checkpoint-438`
- `checkpoint-583`

## Submitted Evaluation Jobs

| Job | Checkpoint | Prompt |
|---:|---|---|
| `382769` | `checkpoint-146` | direct |
| `382770` | `checkpoint-146` | QA-matched |
| `382771` | `checkpoint-292` | direct |
| `382772` | `checkpoint-292` | QA-matched |
| `382773` | `checkpoint-438` | direct |
| `382774` | `checkpoint-438` | QA-matched |
| `382775` | `checkpoint-583` | direct |
| `382776` | `checkpoint-583` | QA-matched |

All eight evaluation jobs completed.

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-146` | `0.014` | `0.050` | `0.0501` | `77.932` | `-4.755` | `0.014` | `0.050` | `0.0529` | `75.480` | `-2.767` | `3/500` |
| `checkpoint-292` | `0.008` | `0.042` | `0.0454` | `77.858` | `-4.966` | `0.012` | `0.050` | `0.0516` | `75.076` | `-2.680` | `2/500` |
| `checkpoint-438` | `0.008` | `0.044` | `0.0453` | `77.662` | `-4.941` | `0.010` | `0.048` | `0.0501` | `74.876` | `-2.658` | `1/500` |
| `checkpoint-583` | `0.008` | `0.042` | `0.0450` | `77.674` | `-4.953` | `0.012` | `0.052` | `0.0519` | `74.866` | `-2.664` | `2/500` |

Best checkpoints under each view:

- best direct top1: `0.014` at `checkpoint-146`
- best QA top1: `0.014` at `checkpoint-146`
- best robust overlap: `3/500` at `checkpoint-146`

## Comparison Against Earlier Branches

Relative to BIO-QA single-stage:

- best direct top1 dropped from `0.016` to `0.014`
- best QA top1 dropped from `0.022` to `0.014`
- best robust overlap stayed at `3/500`

Relative to R2:

- best direct top1 dropped from `0.022` to `0.014`
- best QA top1 dropped from `0.024` to `0.014`
- best robust overlap dropped from `5/500` to `3/500`

## Interpretation

Stage A alone is not enough.

What this means:

- biography-only acquisition may improve CLM fit,
- but it weakens extraction even more than the BIO-QA single-stage mixture,
- so the two-stage branch should not stop after Stage A.

This is exactly the reason the two-stage path exists:

- Stage A is acquisition-heavy,
- Stage B now has to test whether extraction can be recovered by QA-only continuation.

## Decision

```text
Do not promote any Stage A checkpoint as M1.
Proceed directly to Stage B1.
```
