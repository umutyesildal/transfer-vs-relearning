# 10 - M1 Pilot LR1e-4 Epoch1 Run Report

Last updated: 2026-07-05

This report tracks the second M1 English fact acquisition pilot.

## Run Identity

Purpose:

```text
M1 pilot: GPT-2 continued CLM on English synthetic facts only.
```

Training config:

```text
configs/training/m1_gpt2_english_facts_lr1e-4_ep1.yaml
```

Slurm job:

```text
378793
```

Training run directory:

```text
runs/training/m1_gpt2_english_facts/20260705T200848Z_m1_gpt2_english_facts_lr1e-4_ep1_20c47712
```

Final model:

```text
runs/training/m1_gpt2_english_facts/20260705T200848Z_m1_gpt2_english_facts_lr1e-4_ep1_20c47712/final_model
```

Saved checkpoints:

```text
checkpoint-42
checkpoint-84
checkpoint-126
checkpoint-166
```

## Training Metrics

```text
status: complete
train_blocks: 2644
eval_blocks: 54
estimated_optimizer_steps: 166
save_steps: 42
eval_steps: 42
warmup_steps: 8
```

```text
train_loss: 2.5172426901667952
eval_loss: 2.0019617080688477
train_runtime: 51.8517 seconds
train_steps_per_second: 3.201
```

Compared with the `5e-5 / 1 epoch` pilot, this run has lower CLM train/eval loss.

## Checkpoint Evaluation Jobs

Each checkpoint was evaluated on 500 English pilot probes under direct and QA-matched
prompting.

```text
378794 checkpoint-126 direct
378795 checkpoint-126 QA-matched
378796 checkpoint-166 direct
378797 checkpoint-166 QA-matched
378798 checkpoint-42 direct
378799 checkpoint-42 QA-matched
378800 checkpoint-84 direct
378801 checkpoint-84 QA-matched
```

All eight evaluation jobs completed 500/500 probes with 0 failures.

## Primary Metrics

Primary scoring is mean answer-token log probability.

| checkpoint | prompt | top1 | top5 | MRR | mean rank | mean margin |
|---|---:|---:|---:|---:|---:|---:|
| checkpoint-42 | direct | 0.018 | 0.070 | 0.0633 | 67.14 | -2.606 |
| checkpoint-42 | QA-matched | 0.024 | 0.076 | 0.0696 | 67.54 | -2.338 |
| checkpoint-84 | direct | 0.014 | 0.062 | 0.0571 | 68.40 | -2.355 |
| checkpoint-84 | QA-matched | 0.012 | 0.052 | 0.0528 | 68.85 | -2.085 |
| checkpoint-126 | direct | 0.012 | 0.068 | 0.0564 | 68.52 | -2.348 |
| checkpoint-126 | QA-matched | 0.012 | 0.050 | 0.0516 | 69.29 | -2.086 |
| checkpoint-166 | direct | 0.012 | 0.056 | 0.0539 | 68.42 | -2.350 |
| checkpoint-166 | QA-matched | 0.010 | 0.050 | 0.0504 | 69.61 | -2.091 |

## Robust Learned-Fact Counts

Top-1 overlap between direct and QA-matched prompts:

```text
checkpoint-42: direct=9/500, QA=12/500, overlap=5, union=16
checkpoint-84: direct=7/500, QA=6/500, overlap=4, union=9
checkpoint-126: direct=6/500, QA=6/500, overlap=3, union=9
checkpoint-166: direct=6/500, QA=5/500, overlap=3, union=8
```

## Interpretation

This run improves the CLM objective but does not improve extractable factual recall.
Checkpoint-42 remains the best checkpoint by robust overlap, but it still only gives 5
facts out of 500 that are top-1 in both direct and QA-matched English prompts.

This reinforces that the current one-epoch training recipes are not sufficient for the M1
learned-fact gate.

## Recommendation

Do not promote this checkpoint as M1.

Next recommended pilot:

```text
configs/training/m1_gpt2_english_facts_lr5e-5_ep3.yaml
```

Rationale:

- `1e-4 / 1 epoch` lowered CLM loss but did not improve retrieval.
- The remaining planned pilot tests whether more exposure at the conservative learning
  rate improves extractability rather than only short-form LM loss.
- The same checkpoint evaluation protocol should be used before any M1 promotion decision.
