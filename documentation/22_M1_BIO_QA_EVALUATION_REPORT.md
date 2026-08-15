# 22 - M1 BIO-QA Evaluation Report

Date: 2026-07-07

## Purpose

This report records the English direct and QA-matched checkpoint evaluation for the first
BIO-QA redesign run.

The key question is whether the BIO-QA acquisition recipe improves the actual M1
learned-fact gate, not only the training loss.

## Training Run Under Evaluation

Training job:

```text
380525
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts_bio_qa/20260707T122837Z_m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1_ed208753
```

Retained checkpoints:

- `checkpoint-163`
- `checkpoint-326`
- `checkpoint-489`
- `checkpoint-652`

## Evaluation Preparation

Prepared artifacts on HU:

```text
runs/local_model_manifests/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1/
runs/local_configs/m1_checkpoint_eval_smollm2_360m_bio_qa_lr5e-5_ep1/
```

The evaluation follows the corrected R1/R2 protocol:

- explicit checkpoint-specific model manifests,
- explicit per-job `EVAL_CONFIG` export,
- separate direct and QA-matched runs for each checkpoint.

## Submitted Jobs

| Job | Checkpoint | Prompt |
|---:|---|---|
| `381760` | `checkpoint-163` | direct |
| `381761` | `checkpoint-163` | QA-matched |
| `381762` | `checkpoint-326` | direct |
| `381763` | `checkpoint-326` | QA-matched |
| `381764` | `checkpoint-489` | direct |
| `381765` | `checkpoint-489` | QA-matched |
| `381766` | `checkpoint-652` | direct |
| `381767` | `checkpoint-652` | QA-matched |

Startup log was spot-checked for `381760` and confirmed:

- selected config:
  `runs/local_configs/m1_checkpoint_eval_smollm2_360m_bio_qa_lr5e-5_ep1/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1_checkpoint-163_direct.yaml`
- selected model manifest:
  `runs/local_model_manifests/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1/checkpoint-163_model_manifest.json`
- output run root:
  `runs/evaluation/m1_smollm2_360m_english_facts_bio_qa_lr5e-5_ep1_checkpoint-163_direct`

All eight evaluation jobs completed.

## English Gate Results

The table below uses only `language == "en"` rows from `per_fact_results.csv`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct mean margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA mean margin | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-163` | `0.016` | `0.050` | `0.0524` | `77.488` | `-4.994` | `0.022` | `0.066` | `0.0625` | `72.786` | `-2.076` | `3/500` |
| `checkpoint-326` | `0.014` | `0.050` | `0.0506` | `77.328` | `-5.321` | `0.022` | `0.060` | `0.0609` | `71.300` | `-1.947` | `3/500` |
| `checkpoint-489` | `0.014` | `0.044` | `0.0503` | `77.228` | `-5.375` | `0.022` | `0.062` | `0.0611` | `71.158` | `-1.931` | `3/500` |
| `checkpoint-652` | `0.014` | `0.048` | `0.0506` | `77.164` | `-5.387` | `0.022` | `0.064` | `0.0611` | `71.024` | `-1.931` | `2/500` |

Best checkpoints under each view:

- best direct top1: `0.016` at `checkpoint-163`
- best QA top1: `0.022` at all four checkpoints
- best robust overlap: `3/500` at `checkpoint-163`, `checkpoint-326`, and `checkpoint-489`

Top1 counts before overlap:

- `checkpoint-163`: direct `8/500`, QA `11/500`, overlap `3`, union `16`
- `checkpoint-326`: direct `7/500`, QA `11/500`, overlap `3`, union `15`
- `checkpoint-489`: direct `7/500`, QA `11/500`, overlap `3`, union `15`
- `checkpoint-652`: direct `7/500`, QA `11/500`, overlap `2`, union `16`

## Comparison Against R2

R2 reference:

- best direct top1: `0.022`
- best QA top1: `0.024`
- best robust overlap: `5/500`

BIO-QA first-run comparison:

- best direct top1 dropped from `0.022` to `0.016`
- best QA top1 dropped from `0.024` to `0.022`
- best robust overlap dropped from `5/500` to `3/500`

Training-vs-evaluation tension:

- BIO-QA improved training loss strongly,
- BIO-QA improved eval loss strongly,
- but BIO-QA did not improve retrieval under the actual English gate.

## Interpretation

This is an important negative result.

What the run suggests:

- richer biography-majority acquisition data is easier for the model to fit,
- the model becomes better under the CLM training objective,
- but that improvement does not translate into stronger candidate-ranking retrieval of
  the target facts under either direct or QA-matched English probes.

Most likely reading:

- BIO-QA improved general local next-token fit,
- but it still did not create sufficiently sharp answer discrimination for the target
  candidate sets,
- so the bottleneck remains retrieval-oriented factual acquisition, not only training
  stability or optimization loss.

All mean margins stayed negative in both prompt styles.

## Decision

```text
Do not promote any checkpoint from the first BIO-QA run as M1.
```

## What We Learned

BIO-QA is not a useless branch, but it did not solve the gate.

It gave us two strong signals:

1. The problem is not simply that the model could not fit the new data.
2. Better CLM loss on denser synthetic biographies is not enough by itself.

So the next step should change the acquisition objective or retrieval pressure more
directly rather than only increasing biography richness.

## Next Action

Most conservative next continuation:

- keep the BIO-QA branch as documented evidence,
- do not continue with the same recipe unchanged,
- design the next M1 attempt around stronger answer discrimination or a more explicitly
  retrieval-oriented English acquisition format.
