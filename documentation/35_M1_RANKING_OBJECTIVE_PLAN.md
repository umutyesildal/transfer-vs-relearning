# 35 - M1 Ranking Objective Plan

Date: 2026-07-08

## Purpose

This plan opens the next post-CLM M1 branch.

The core change is simple:

- keep the small model,
- keep English-only synthetic supervision,
- but stop training only for generic CLM loss,
- and instead train directly for answer discrimination among same-family candidates.

## Why This Branch Exists

The current evidence is now strong:

- plain English CLM on synthetic facts failed,
- more exposure on the same plain branch also failed,
- two-stage acquire/extract CLM also failed,
- lower training loss repeatedly failed to convert into better retrieval.

So the main diagnosis is no longer "the model just needs more exposure."

The stronger diagnosis is:

```text
the current objective is optimizing something easier than the actual retrieval behavior we
care about
```

## Branch Label

```text
M1-RANKING
```

## Training Idea

For each English prompt:

- score the correct answer,
- score several incorrect candidates from the same relation family,
- optimize cross-entropy so the correct answer outranks the negatives.

This aligns the training signal much more closely with the evaluation protocol.

## Data Sources

Dataset version:

```text
synthetic_v1_bio_qa
```

Prompt sources:

1. English direct probes from `probes_en.csv`
2. English QA prompts from `english_qa_train.jsonl`

This keeps the branch English-only while exposing the model to both prompt families we care
about at evaluation time.

## First Pilot Config

The original branch scaffold includes a longer `ep3` config, but the first HU pilot should
start with the cheaper `ep1` version to get signal quickly before committing more compute.

Training config:

```text
configs/training/m1_smollm2_360m_english_fact_ranking_lr2e-5_ep1.yaml
```

Key settings:

- model: `HuggingFaceTB/SmolLM2-360M`
- negatives per example: `7`
- candidates per prompt: `8` total
- learning rate: `2e-5`
- epochs: `1`
- train batch size: `4`
- grad accumulation: `2`
- scheduler: `cosine`
- score mode: `mean_logprob`

## Implementation Scope

New components:

- `src/transfer_vs_relearning/training/ranking.py`
- `scripts/train_ranking.py`
- `slurm/train_m1_ranking.slurm`

The existing CLM pipeline remains unchanged.

## Scientific Risks

This branch is more evaluation-aligned than plain CLM, so it carries a real overfitting
risk.

That risk is acceptable for now because:

- it directly tests our updated diagnosis,
- it is cheap relative to from-scratch alternatives,
- and it can quickly tell us whether answer discrimination is the missing ingredient.

## Success Criterion

This branch is only worth keeping if it improves the English learned-fact gate relative to
the strongest small-model CLM baselines.

Immediate target:

- direct top1 better than `0.014`,
- QA-matched top1 better than `0.016`,
- robust direct-and-QA overlap better than `3/500`.

## Next Step

1. validate the new trainer locally,
2. push and pull on HU,
3. run the first ranking-objective pilot,
4. if the first pilot is promising, scale to the `ep3` continuation,
5. evaluate all retained checkpoints under English direct and QA-matched prompts,
6. compare against the previous plain and two-stage SmolLM2 branches.
