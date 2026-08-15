# 36 - M1 Ranking Objective Run Report

Date: 2026-07-08

## Purpose

This report records the first executable pilot of the ranking-objective M1 branch.

This branch keeps:

- `HuggingFaceTB/SmolLM2-360M`,
- English-only synthetic supervision,
- the same synthetic candidate world,

but replaces plain CLM training with direct candidate discrimination.

## Source State

Training repo:

- branch: `corpus-update`
- launch commit: `2e95506`
- pushed to GitHub: yes

## First Pilot Config

```text
configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1.yaml
```

Key settings:

- prompt sources: English direct probes + English QA prompts
- negatives per example: `7`
- candidates per prompt: `8`
- learning rate: `2e-5`
- epochs: `1`
- train batch size: `4`
- grad accumulation: `2`
- objective: cross-entropy over candidate scores
- score mode: mean answer-token logprob

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
389222
```

Verified startup log:

- selected config is the ranking `ep1` config,
- dataset version resolves to `synthetic_v1_bio_qa`,
- both direct probes and English QA prompts are enabled,
- candidate count per prompt is controlled by `negatives_per_example: 7`,
- the ranking slurm wrapper starts cleanly with no early stderr failure.

## Final Training Outcome

Training status:

```text
complete
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_fact_ranking/20260708T203650Z_m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1_e5698316
```

Final training metrics:

- train loss: `5.3664`
- train runtime: `4014.45s`
- train steps/sec: `1.716`
- optimizer steps: `6889`

Internal ranking holdout metrics:

- eval loss: `2.5550`
- eval top1: `0.1733`

Retained checkpoints:

- `checkpoint-1722`
- `checkpoint-3444`
- `checkpoint-5166`
- `checkpoint-6888`
- `checkpoint-6889`

## Immediate Interpretation

This is the first real test of the updated diagnosis:

```text
the missing ingredient may be answer discrimination rather than more CLM exposure
```

No scientific conclusion should be drawn until:

1. checkpoint evaluation runs under English direct and QA-matched prompts.
