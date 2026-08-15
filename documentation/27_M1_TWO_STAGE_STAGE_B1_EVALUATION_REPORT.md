# 27 - M1 Two-Stage Stage B1 Evaluation Report

Date: 2026-07-07

## Purpose

This report records the English direct and QA-matched checkpoint evaluation for the first
Stage B1 run of the two-stage M1 branch.

The key question is whether QA-only continuation from the Stage A final model can recover
the extraction weakness seen after Stage A.

## Training Run Under Evaluation

Training job:

```text
382777
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_qa_stage_b1/20260707T173927Z_m1_smollm2_360m_english_qa_stage_b1_lr5e-5_ep1_0c420e40
```

Retained checkpoints:

- `checkpoint-17`
- `checkpoint-34`
- `checkpoint-51`
- `checkpoint-68`
- `checkpoint-69`

## Submitted Evaluation Jobs

| Job | Checkpoint | Prompt |
|---:|---|---|
| `383458` | `checkpoint-17` | direct |
| `383463` | `checkpoint-17` | QA-matched |
| `383468` | `checkpoint-34` | direct |
| `383470` | `checkpoint-34` | QA-matched |
| `383471` | `checkpoint-51` | direct |
| `383472` | `checkpoint-51` | QA-matched |
| `383473` | `checkpoint-68` | direct |
| `383474` | `checkpoint-68` | QA-matched |
| `383475` | `checkpoint-69` | direct |
| `383476` | `checkpoint-69` | QA-matched |

All ten evaluation jobs completed.

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-17` | `0.012` | `0.044` | `0.0481` | `77.150` | `-4.596` | `0.020` | `0.058` | `0.0592` | `73.180` | `-2.095` | `3/500` |
| `checkpoint-34` | `0.012` | `0.046` | `0.0481` | `77.136` | `-4.880` | `0.016` | `0.052` | `0.0576` | `72.292` | `-2.027` | `2/500` |
| `checkpoint-51` | `0.012` | `0.044` | `0.0488` | `77.060` | `-4.943` | `0.014` | `0.056` | `0.0571` | `72.052` | `-2.019` | `2/500` |
| `checkpoint-68` | `0.012` | `0.048` | `0.0489` | `77.114` | `-4.974` | `0.016` | `0.058` | `0.0579` | `72.032` | `-2.016` | `2/500` |
| `checkpoint-69` | `0.012` | `0.048` | `0.0488` | `77.100` | `-4.974` | `0.016` | `0.054` | `0.0576` | `72.048` | `-2.017` | `2/500` |

Best checkpoints under each view:

- best direct top1: `0.012` at all checkpoints
- best QA top1: `0.020` at `checkpoint-17`
- best robust overlap: `3/500` at `checkpoint-17`

## Comparison Against Earlier Branches

Relative to Stage A:

- best direct top1 dropped from `0.014` to `0.012`
- best QA top1 improved from `0.014` to `0.020`
- best robust overlap stayed at `3/500`

Relative to BIO-QA single-stage:

- best direct top1 dropped from `0.016` to `0.012`
- best QA top1 dropped from `0.022` to `0.020`
- best robust overlap stayed at `3/500`

Relative to R2:

- best direct top1 dropped from `0.022` to `0.012`
- best QA top1 dropped from `0.024` to `0.020`
- best robust overlap dropped from `5/500` to `3/500`

## Interpretation

Stage B1 partially recovered QA-side extraction, but not enough.

What changed:

- QA top1 improved meaningfully over Stage A,
- direct top1 got slightly worse,
- robust overlap did not improve beyond the Stage A ceiling.

This means:

- the two-stage decomposition did separate some behavior,
- QA-only continuation can move the extraction side,
- but the current plain CLM Stage B1 objective still does not create a valid M1.

## Decision

```text
Do not promote any Stage B1 checkpoint as M1.
```

## Recommended Next Step

If the two-stage branch continues, the next escalation should be:

```text
Stage B2 = answer-focused loss on the English QA continuation stage
```

That is now the cleanest remaining test inside the two-stage family.
