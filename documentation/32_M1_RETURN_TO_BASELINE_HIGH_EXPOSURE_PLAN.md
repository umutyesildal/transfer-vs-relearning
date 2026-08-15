# 32 - M1 Return-To-Baseline High-Exposure Plan

Date: 2026-07-08

## Purpose

This plan records a deliberate return to the original plain M1 recipe:

- same small base model,
- same original English fact-training file,
- same full-sequence CLM objective,
- but longer exposure with a lower learning rate.

The motivation is not that the current evidence proves undertraining. It does not.
The motivation is that the user explicitly wants one controlled retry of the original
recipe family before abandoning it.

## Chosen Branch

Recipe label:

```text
M1-RETURN-BASELINE-HIGH-EXPOSURE
```

Base model:

```text
HuggingFaceTB/SmolLM2-360M
```

Dataset:

```text
artifacts/datasets/synthetic_v1/output/english_training.jsonl
```

Objective:

```text
plain causal language modeling
```

## Why This Exact Variant

We are not repeating the earlier run unchanged.

We are changing two things together:

1. lower learning rate from `5e-5` to `2e-5`,
2. longer training from `1` epoch to `5` epochs.

This is meant to test:

- whether the original plain-fact recipe was being updated too aggressively,
- whether a slower optimization path over more passes helps retention/retrieval,
- whether the earlier negative result was partly an optimization-shape problem rather
  than only a recipe problem.

## Config

Training config:

```text
configs/training/m1_smollm2_360m_english_facts_lr2e-5_ep5.yaml
```

Key settings:

- model: `HuggingFaceTB/SmolLM2-360M`
- dataset: `synthetic_v1`
- train file: `english_training.jsonl`
- loss mode: default full-sequence CLM
- learning rate: `2e-5`
- epochs: `5`
- per-device train batch: `8`
- gradient accumulation: `2`
- effective batch size: `16`
- scheduler: `cosine`
- warmup ratio: `0.05`

## Scientific Expectation

This is a high-risk retry, not the default scientifically preferred path.

Current evidence already suggests that:

- lower loss does not guarantee better retrieval,
- more exposure on some nearby recipe families made results worse.

So success here is possible, but not currently the most likely outcome.

## Success Criterion

The run is only worth keeping if it improves the English learned-fact gate relative to the
best plain small-model baseline.

Minimum practical target:

- direct top1 better than `0.014`,
- QA-matched top1 better than `0.016`,
- robust direct-and-QA overlap better than `3/500`.

## Next Step

1. launch the run on HU,
2. estimate runtime from early logs,
3. wait for completion,
4. run checkpoint evaluation under English direct and QA-matched prompts,
5. compare against the original plain SmolLM2 pilot and the stronger recipe branches.
