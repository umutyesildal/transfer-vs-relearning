# 12 - M1 SmolLM2 360M Pilot Run Report

Date: 2026-07-06

## Purpose

This run tests whether the existing M1 English fact-acquisition pipeline works better with a
different base model before changing the training objective or synthetic-fact recipe.

The core experimental question for this pilot is:

```text
If the exact same M1 pipeline is run on SmolLM2-360M instead of GPT-2, does English factual
retrieval improve enough to justify a model-scale/model-family change before rewriting the
M1 recipe?
```

## Why This Pilot

The GPT-2 M1 recipe already failed in three tested variants:

1. `5e-5`, 1 epoch
2. `1e-4`, 1 epoch
3. `5e-5`, 3 epochs

Those runs showed that:

- CLM loss can improve without reliable factual retrieval,
- small hyperparameter changes did not solve the learned-fact gate,
- it became unclear whether the main bottleneck was GPT-2 itself or the recipe.

SmolLM2-360M is the first direct test of that distinction.

## Model Download

Downloaded model:

```text
HuggingFaceTB/SmolLM2-360M
```

Resolved revision:

```text
f8027fd0eaeea54caa13c31d31b9fdc459c38b49
```

Manifest path:

```text
artifacts/models/HuggingFaceTB__SmolLM2-360M/model_manifest.json
```

## Training Configuration

Config:

```text
configs/training/m1_smollm2_360m_english_facts_lr5e-5_ep1.yaml
```

Training command:

```bash
sbatch --export=ALL,TRAIN_CONFIG=configs/training/m1_smollm2_360m_english_facts_lr5e-5_ep1.yaml slurm/train_m1_gpt2_english_facts.slurm
```

Slurm job:

```text
379044
```

Run directory:

```text
runs/training/m1_smollm2_360m_english_facts/20260706T064952Z_m1_smollm2_360m_english_facts_lr5e-5_ep1_8f852a51
```

Hardware/software:

- GPU: NVIDIA A100 80GB PCIe
- CUDA: `12.8`
- Torch: `2.7.0+cu128`
- Transformers: `5.13.0`
- Datasets: `5.0.0`

## Training Result

Status:

```text
complete
```

Final training metrics:

- train loss: `3.069818079118898`
- eval loss: `2.74118971824646`
- train runtime: `100.6961` seconds
- train steps per second: `1.678`

Checkpoint directories:

- `checkpoint-42`
- `checkpoint-84`
- `checkpoint-126`
- `checkpoint-168`
- `checkpoint-169`

## Checkpoint Evaluation Jobs

Checkpoint eval manifests/configs were generated under:

```text
runs/local_model_manifests/m1_smollm2_360m_english_facts_lr5e-5_ep1/
runs/local_configs/m1_checkpoint_eval_smollm2_360m_lr5e-5_ep1/
```

Submitted jobs:

| Job | Checkpoint | Prompt |
|---:|---|---|
| `379060` | `checkpoint-126` | direct |
| `379061` | `checkpoint-126` | QA-matched |
| `379062` | `checkpoint-168` | direct |
| `379063` | `checkpoint-168` | QA-matched |
| `379064` | `checkpoint-169` | direct |
| `379065` | `checkpoint-169` | QA-matched |
| `379066` | `checkpoint-42` | direct |
| `379067` | `checkpoint-42` | QA-matched |
| `379068` | `checkpoint-84` | direct |
| `379069` | `checkpoint-84` | QA-matched |

All ten evaluation jobs completed.

## English Gate Results

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | QA top1 | QA top5 | QA MRR | QA mean rank | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-42` | `0.008` | `0.054` | `0.0460` | `79.874` | `0.010` | `0.054` | `0.0493` | `78.740` | `2/500` |
| `checkpoint-84` | `0.012` | `0.054` | `0.0510` | `78.572` | `0.014` | `0.058` | `0.0536` | `76.864` | `3/500` |
| `checkpoint-126` | `0.014` | `0.056` | `0.0516` | `78.364` | `0.016` | `0.058` | `0.0551` | `76.672` | `3/500` |
| `checkpoint-168` | `0.014` | `0.056` | `0.0516` | `78.360` | `0.016` | `0.062` | `0.0554` | `76.636` | `3/500` |
| `checkpoint-169` | `0.014` | `0.056` | `0.0516` | `78.360` | `0.016` | `0.062` | `0.0554` | `76.634` | `3/500` |

Top1 counts before overlap:

- `checkpoint-42`: direct `4/500`, QA `5/500`, overlap `2`, union `7`
- `checkpoint-84`: direct `6/500`, QA `7/500`, overlap `3`, union `10`
- `checkpoint-126`: direct `7/500`, QA `8/500`, overlap `3`, union `12`
- `checkpoint-168`: direct `7/500`, QA `8/500`, overlap `3`, union `12`
- `checkpoint-169`: direct `7/500`, QA `8/500`, overlap `3`, union `12`

All mean score margins remained negative:

- direct margins around `-4.30`
- QA-matched margins around `-2.93`

## Interpretation

This pilot shows that the existing M1 pipeline transfers cleanly to a different
decoder-only base model. That is a useful engineering result by itself.

Scientifically, however, the learned-fact gate still fails.

The best SmolLM2 checkpoint reached:

- best direct top1: `0.014`
- best QA-matched top1: `0.016`
- best robust overlap: `3/500`

This is not better than the strongest GPT-2 pilot, which reached:

- best direct top1: `0.024`
- best QA-matched top1: `0.024`
- best robust overlap: `5/500`

Conclusion:

```text
Do not promote any checkpoint from the SmolLM2-360M 1-epoch pilot as M1.
```

## What We Learned

This pilot narrows the diagnosis:

- the M1 pipeline is not blocked by GPT-2-specific code,
- simply switching to a somewhat larger/different small decoder model is not enough,
- the main bottleneck now looks more like objective/data recipe strength than tooling.

## Next Action

The most reasonable next step is no longer another near-identical CLM pilot.

The next experiment should change at least one of:

1. model scale more substantially,
2. synthetic fact formatting or repetition structure,
3. training objective,
4. explicit answer-oriented supervision.
