# 09 - M1 Checkpoint Evaluation Report

Last updated: 2026-07-05

This report evaluates the first M1 pilot checkpoints from:

```text
runs/training/m1_gpt2_english_facts/20260705T195512Z_m1_gpt2_english_facts_lr5e-5_ep1_1a968945
```

Training config:

```text
configs/training/m1_gpt2_english_facts_lr5e-5_ep1.yaml
```

Evaluated checkpoints:

```text
checkpoint-42
checkpoint-84
checkpoint-126
checkpoint-166
```

Each checkpoint was evaluated on English-only pilot probes:

- direct prompt,
- QA-matched prompt.

Each run completed 500/500 probes with 0 failures.

## Slurm Jobs

```text
378785 checkpoint-126 direct
378786 checkpoint-126 QA-matched
378787 checkpoint-166 direct
378788 checkpoint-166 QA-matched
378789 checkpoint-42 direct
378790 checkpoint-42 QA-matched
378791 checkpoint-84 direct
378792 checkpoint-84 QA-matched
```

## Primary Metrics

Primary scoring is mean answer-token log probability.

| checkpoint | prompt | top1 | top5 | MRR | mean rank | mean margin |
|---|---:|---:|---:|---:|---:|---:|
| checkpoint-42 | direct | 0.024 | 0.090 | 0.0702 | 69.68 | -3.042 |
| checkpoint-42 | QA-matched | 0.024 | 0.074 | 0.0678 | 70.26 | -2.638 |
| checkpoint-84 | direct | 0.020 | 0.070 | 0.0620 | 67.82 | -2.656 |
| checkpoint-84 | QA-matched | 0.018 | 0.056 | 0.0585 | 69.11 | -2.265 |
| checkpoint-126 | direct | 0.018 | 0.066 | 0.0596 | 68.30 | -2.623 |
| checkpoint-126 | QA-matched | 0.012 | 0.056 | 0.0544 | 69.30 | -2.252 |
| checkpoint-166 | direct | 0.018 | 0.068 | 0.0600 | 68.23 | -2.597 |
| checkpoint-166 | QA-matched | 0.012 | 0.058 | 0.0553 | 69.80 | -2.247 |

## Robust Learned-Fact Counts

Top-1 overlap between direct and QA-matched prompts:

```text
checkpoint-42: direct=12/500, QA=12/500, overlap=5, union=19
checkpoint-84: direct=10/500, QA=9/500, overlap=4, union=15
checkpoint-126: direct=9/500, QA=6/500, overlap=3, union=12
checkpoint-166: direct=9/500, QA=6/500, overlap=3, union=12
```

## Interpretation

The first M1 pilot is a healthy training run but not a successful factual acquisition run.
The language-modeling loss improved during training, but factual candidate ranking did not
open a large learned-fact set. Checkpoint-42 is the best among the four evaluated
checkpoints, but even there the robust direct-and-QA top-1 set contains only 5 facts out of
500 pilot probes.

This supports the earlier concern from the literature notes: lower CLM loss on short
templated statements does not automatically imply extractable factual knowledge.

## Recommendation

Do not promote this checkpoint as M1.

Next recommended pilot:

```text
configs/training/m1_gpt2_english_facts_lr1e-4_ep1.yaml
```

Rationale:

- the one-epoch `5e-5` run under-learned the target facts;
- `1e-4` is still within the GPT-2 fine-tuning range recorded in the research notes;
- one epoch keeps the next test cheap and comparable.

After that pilot completes, evaluate its checkpoints with the same direct and QA-matched
English protocol before running the three-epoch `5e-5` pilot.
