# 14 - M1 R1 Run Report

Date: 2026-07-06

## Purpose

This report records the first explicit recipe-change run for M1.

R1 keeps GPT-2 but replaces the plain English fact-acquisition corpus with a stronger
QA-mixed and repetition-boosted dataset. The goal is to test whether weak answer-oriented
supervision was the main reason earlier M1 pilots failed the English learned-fact gate.

## Recipe Summary

Plan document:

```text
documentation/13_M1_R1_STRONGER_REPETITION_PLAN.md
```

Training config:

```text
configs/training/m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1.yaml
```

Derived train file:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2.jsonl
```

Derived summary:

```text
artifacts/datasets/synthetic_v1/output/english_training_m1_r1_qamix_d2_q2_summary.json
```

## Training Run

Slurm job:

```text
379169
```

Run directory:

```text
runs/training/m1_gpt2_english_facts_r1_qamix/20260706T073332Z_m1_gpt2_english_facts_r1_qamix_lr5e-5_ep1_5fa91c43
```

Final training metrics:

- train loss: `1.799191196259083`
- eval loss: `1.418290376663208`
- train runtime: `184.2519` seconds
- train steps per second: `4.309`

Recorded checkpoints:

- `checkpoint-198`
- `checkpoint-396`
- `checkpoint-594`
- `checkpoint-792`
- `checkpoint-794`

## Evaluation Retry Note

The first checkpoint-evaluation submission attempt was not valid for R1 interpretation.

What went wrong:

- the Slurm wrapper defaulted to `configs/evaluation/m0_gpt2_pilot_direct.yaml`,
- the intended per-checkpoint `EVAL_CONFIG` was not actually reaching the job environment,
- logs therefore showed base GPT-2 evaluation instead of local R1 checkpoint evaluation.

How it was fixed:

- each job was resubmitted with explicit config export:

```bash
sbatch --export=ALL,EVAL_CONFIG=<checkpoint-config> slurm/eval_m0_gpt2_pilot.slurm
```

- logs were spot-checked to confirm:
  - the selected config path was the intended local checkpoint config,
  - the model manifest pointed to the intended local checkpoint manifest,
  - the output run root matched the R1 checkpoint-specific evaluation directory.

Valid evaluation jobs after correction:

- `379279`
- `379290`
- `379291`
- `379292`
- `379295`
- `379296`
- `379300`
- `379305`
- `379306`
- `379307`

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-198` | `0.002` | `0.050` | `0.0443` | `73.264` | `-5.678` | `0.030` | `0.054` | `0.0668` | `66.622` | `-1.845` | `1/500` |
| `checkpoint-396` | `0.004` | `0.052` | `0.0452` | `73.116` | `-5.995` | `0.028` | `0.070` | `0.0685` | `65.766` | `-1.787` | `2/500` |
| `checkpoint-594` | `0.010` | `0.048` | `0.0490` | `73.126` | `-6.223` | `0.016` | `0.066` | `0.0621` | `65.710` | `-1.839` | `5/500` |
| `checkpoint-792` | `0.010` | `0.050` | `0.0491` | `73.094` | `-6.192` | `0.016` | `0.060` | `0.0611` | `65.198` | `-1.792` | `5/500` |
| `checkpoint-794` | `0.010` | `0.050` | `0.0490` | `73.070` | `-6.187` | `0.016` | `0.058` | `0.0619` | `65.638` | `-1.805` | `4/500` |

Best checkpoints under each view:

- best direct top1: `0.010` at `checkpoint-594`, `checkpoint-792`, and `checkpoint-794`
- best QA top1: `0.030` at `checkpoint-198`
- best robust overlap: `5/500` at `checkpoint-594` and `checkpoint-792`

## Interpretation

R1 changed the shape of the failure but did not solve it.

What improved:

- QA-matched retrieval improved early in training relative to most earlier GPT-2 pilots,
- the best QA top1 rose to `0.030`,
- the run confirmed that the QA-mixed recipe can shift prompt sensitivity.

What did not improve:

- direct retrieval remained extremely weak,
- robust direct-and-QA overlap did not exceed the earlier GPT-2 best of `5/500`,
- all mean margins stayed negative.

Relative to the strongest earlier GPT-2 pilot:

- previous best direct top1: `0.024`
- previous best QA top1: `0.024`
- previous best robust overlap: `5/500`

R1 therefore did not produce a better overall M1 candidate.

## Decision

```text
Do not promote any checkpoint from M1-R1 as M1.
```

## What We Learned

R1 narrows the diagnosis further:

- stronger repetition alone is not enough,
- explicit QA-style exposure helps QA prompting more than direct retrieval,
- the remaining bottleneck is still likely the model-and-objective combination rather than
  a missing checkpoint-evaluation path or a trivial hyperparameter issue.

## Next Action

Move to the next agreed escalation:

```text
Step 2 = bigger model + stronger recipe
```

The immediate candidate is:

- base model: `HuggingFaceTB/SmolLM2-360M`
- training recipe: same R1 QA-mixed dataset
- first launch: `lr=5e-5`, `1` epoch
