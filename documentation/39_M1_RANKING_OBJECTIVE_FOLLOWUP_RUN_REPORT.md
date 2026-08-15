# 39 - M1 Ranking Objective Follow-Up Run Report

Date: 2026-07-09

## Purpose

This report records the second executable run inside the ranking-objective M1 branch.

The goal of this follow-up is narrow:

- keep the same ranking supervision,
- keep the same English BIO-QA candidate world,
- reduce the step size,
- and give the model more room than the first `ep1` pilot.

## Source State

Training repo:

- branch: `corpus-update`
- launch commit: `7d2b9ab`
- pushed to GitHub: yes

## Selected Config

```text
configs/training/m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2.yaml
```

Key settings relative to the first ranking pilot:

- learning rate: `1e-5` instead of `2e-5`
- epochs: `2` instead of `1`
- model: unchanged `HuggingFaceTB/SmolLM2-360M`
- prompt sources: unchanged English direct probes + English QA prompts
- negatives per example: unchanged `7`

## Validation Before Launch

Local focused tests:

```text
tests/test_training_core.py
tests/test_training_ranking.py
```

Result:

```text
passed
```

HU focused tests:

```text
tests/test_training_core.py
tests/test_training_ranking.py
```

Result:

```text
passed
```

## Slurm Launch

Training job:

```text
389480
```

Immediate Slurm state:

- state: `RUNNING`
- node: `gruenau10`
- start time: `2026-07-09 08:06:51`
- scheduled end time: `2026-07-09 12:06:51`
- time limit: `04:00:00`

Log paths:

- stdout: `logs/m1-ranking-389480.out`
- stderr: `logs/m1-ranking-389480.err`

## Final Training Outcome

Training status:

```text
complete
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_fact_ranking/20260709T060700Z_m1_smollm2_360m_english_fact_ranking_lr1e-5_ep2_0b3462e1
```

Final training metrics:

- train loss: `6.4562`
- train runtime: `3905.52s`
- train steps/sec: `3.5278`
- optimizer steps: `13778`

Internal ranking holdout metrics:

- eval loss: `3.2171`
- eval top1: `0.1422`

Retained checkpoints:

- `checkpoint-3444`
- `checkpoint-6888`
- `checkpoint-10332`
- `checkpoint-13776`
- `checkpoint-13778`

## Immediate Interpretation

This follow-up finished a little faster than the first `ep1` pilot despite using two
epochs, because the trainer sustained a much higher measured step rate on this run.

However, the trainer-side holdout metric moved in the wrong direction relative to the first
ranking pilot:

- first ranking pilot internal eval top1: `0.1733`
- follow-up internal eval top1: `0.1422`

That is not yet the thesis decision signal, but it is an early warning that the lower-LR,
longer ranking run may not improve the English learned-fact gate.

## Submitted Evaluation Jobs

English direct plus QA-matched checkpoint evaluation wave:

- `389515`
- `389516`
- `389517`
- `389518`
- `389519`
- `389520`
- `389521`
- `389522`
- `389523`
- `389524`

Immediate queue snapshot after submission:

- running: `389515`, `389516`, `389517`
- pending: `389518` to `389524`

## Pending Next Step

Wait for all ten English checkpoint evaluations to complete, then compare:

1. direct top1 against the first ranking pilot and the strongest plain SmolLM2 baseline,
2. QA-matched top1 against the first ranking pilot,
3. robust direct-and-QA overlap against the current `5/500` ranking benchmark.
