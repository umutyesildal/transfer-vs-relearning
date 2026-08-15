# 20 - M1 BIO QA First Run Plan

Date: 2026-07-07

## Purpose

This document defines the first executable training run for the BIO-QA redesign branch.

The immediate goal is not to solve the entire thesis at once. The goal is to isolate the
effect of the new English-side acquisition data while keeping the base model family close
to the strongest earlier comparison point.

## Branch And Commit State

Synthetic data repo:

- branch: `bio-qa-m1`
- commit: `ae0e457`

Transfer/training repo:

- branch: `corpus-update`
- commit: `a0bbbaf`

## Dataset Sync Target

New dataset version in `transfer-vs-relearning`:

```text
synthetic_v1_bio_qa
```

Source:

```text
repo: git@github.com:umutyesildal/synthetic-data-generation.git
ref: bio-qa-m1
```

Key BIO-QA artifact:

```text
artifacts/datasets/synthetic_v1_bio_qa/output/english_training_m1_bio_qa.jsonl
```

## Why This First Run Uses SmolLM2-360M

The first BIO-QA run should compare against the clearest prior baseline, not jump to the
largest possible model immediately.

Chosen comparison anchor:

```text
R2 = SmolLM2-360M + QA-mixed R1 dataset + 1 epoch
```

Reason:

- same model class,
- same optimizer family,
- same one-epoch first pass,
- cleaner comparison of data recipe change.

## First Training Config

```text
configs/training/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_bio_qa`
- train file: `english_training_m1_bio_qa.jsonl`
- base model: `HuggingFaceTB/SmolLM2-360M`
- learning rate: `5e-5`
- epochs: `1`
- block size: `512`
- effective batch size: `16`

## Comparison Target

Primary direct comparison:

```text
R2 = SmolLM2-360M + english_training_m1_r1_qamix_d2_q2.jsonl + 1 epoch
```

Key marks to compare after checkpoint evaluation:

- direct top1,
- QA top1,
- robust direct-and-QA overlap,
- mean margin.

Interpretation rule:

- if BIO-QA improves direct only but collapses robust overlap, it is not enough,
- if BIO-QA improves robust overlap while staying competitive on direct, it becomes the
  strongest M1 branch so far,
- if BIO-QA fails similarly to R2-R4, the next step should move from data redesign to
  objective redesign.

## Execution Steps

1. Pull `corpus-update` on HU.
2. Sync dataset version `synthetic_v1_bio_qa` from synthetic repo branch `bio-qa-m1`.
3. Run focused local/remote training-config validation if needed.
4. Submit the SmolLM2-360M BIO-QA training job.
5. Check queue and startup log.
6. After training completes, run the same checkpoint-evaluation protocol used for R2-R4.

## Decision Goal

The first BIO-QA run is successful only if it gives a better overall English learned-fact
profile than the strongest earlier branch, not merely a better isolated direct score.
