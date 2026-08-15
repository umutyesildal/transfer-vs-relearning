# 11 - M1 Pilot LR 5e-5 / 3 Epoch Run Report

Date: 2026-07-05

## Purpose

This run tests whether the conservative M1 learning rate from the first pilot needs more
English synthetic-fact exposure before factual retrieval becomes strong enough for the
M1 learned-fact gate.

Earlier M1 pilots showed healthy CLM loss reduction but weak factual retrieval:

- LR `5e-5`, 1 epoch: best direct top1 `0.024`, best QA-matched top1 `0.024`,
  robust direct-and-QA top1 overlap `5/500`.
- LR `1e-4`, 1 epoch: lower CLM loss, but no retrieval improvement; best direct top1
  `0.018`, best QA-matched top1 `0.024`, robust overlap `5/500`.

This third pilot keeps LR `5e-5` and increases training to 3 epochs.

## Training Configuration

Config:

```text
configs/training/m1_gpt2_english_facts_lr5e-5_ep3.yaml
```

Remote repository state:

```text
branch: corpus-update
commit: e2890f7 Fix TrainingArguments compatibility for M1
```

Training command:

```bash
sbatch --export=ALL,TRAIN_CONFIG=configs/training/m1_gpt2_english_facts_lr5e-5_ep3.yaml slurm/train_m1_gpt2_english_facts.slurm
```

Slurm job:

```text
378802
```

Run directory:

```text
runs/training/m1_gpt2_english_facts/20260705T201752Z_m1_gpt2_english_facts_lr5e-5_ep3_d83f491c
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

Important counts:

- training rows: `104169`
- train blocks: `2644`
- eval blocks: `54`
- estimated optimizer steps: `498`
- save/eval steps: `124`
- warmup steps: `25`

Final training metrics:

- train loss: `2.267362948881096`
- eval loss: `1.8304280042648315`
- train runtime: `113.8083` seconds
- train steps per second: `4.376`

Checkpoint directories recorded by the manifest:

- `checkpoints/checkpoint-124`
- `checkpoints/checkpoint-248`
- `checkpoints/checkpoint-372`
- `checkpoints/checkpoint-496`
- `checkpoints/checkpoint-498`

Final model directory:

```text
runs/training/m1_gpt2_english_facts/20260705T201752Z_m1_gpt2_english_facts_lr5e-5_ep3_d83f491c/final_model
```

## Checkpoint Evaluation Jobs

Evaluation manifests/configs were generated under:

```text
runs/local_model_manifests/m1_gpt2_english_facts_lr5e-5_ep3/
runs/local_configs/m1_checkpoint_eval_lr5e-5_ep3/
```

Submitted checkpoint evaluation jobs:

| Job | Checkpoint | Prompt |
|---:|---|---|
| `378803` | `checkpoint-124` | direct |
| `378804` | `checkpoint-124` | QA-matched |
| `378805` | `checkpoint-248` | direct |
| `378806` | `checkpoint-248` | QA-matched |
| `378807` | `checkpoint-372` | direct |
| `378808` | `checkpoint-372` | QA-matched |
| `378809` | `checkpoint-496` | direct |
| `378810` | `checkpoint-496` | QA-matched |
| `378811` | `checkpoint-498` | direct |
| `378812` | `checkpoint-498` | QA-matched |

First queue check after submission:

- `378803` through `378808` were running on `gruenau9` / `gruenau10`.
- `378809` through `378812` were pending for resources/priority.

## Checkpoint Evaluation Results

All ten checkpoint evaluation jobs completed successfully.

English direct and QA-matched metrics:

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | QA top1 | QA top5 | QA MRR | QA mean rank | Robust top1 overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-124` | `0.016` | `0.066` | `0.0578` | `68.782` | `0.016` | `0.054` | `0.0570` | `70.360` | `3/500` |
| `checkpoint-248` | `0.008` | `0.048` | `0.0482` | `69.758` | `0.002` | `0.046` | `0.0448` | `70.228` | `1/500` |
| `checkpoint-372` | `0.010` | `0.052` | `0.0508` | `69.218` | `0.004` | `0.052` | `0.0456` | `70.104` | `1/500` |
| `checkpoint-496` | `0.010` | `0.044` | `0.0497` | `68.858` | `0.000` | `0.044` | `0.0423` | `70.626` | `0/500` |
| `checkpoint-498` | `0.008` | `0.044` | `0.0495` | `68.970` | `0.006` | `0.044` | `0.0462` | `69.864` | `1/500` |

Top1 counts before overlap:

- `checkpoint-124`: direct `8/500`, QA `8/500`, overlap `3`, union `13`
- `checkpoint-248`: direct `4/500`, QA `1/500`, overlap `1`, union `4`
- `checkpoint-372`: direct `5/500`, QA `2/500`, overlap `1`, union `6`
- `checkpoint-496`: direct `5/500`, QA `0/500`, overlap `0`, union `5`
- `checkpoint-498`: direct `4/500`, QA `3/500`, overlap `1`, union `6`

All mean score margins remained negative in both prompt styles.

## Final Interpretation

The 3-epoch run continued to reduce CLM validation loss:

- LR `5e-5`, 1 epoch eval loss: `2.2544260025024414`
- LR `1e-4`, 1 epoch eval loss: `2.0019617080688477`
- LR `5e-5`, 3 epochs eval loss: `1.8304280042648315`

This is a healthy language-model training signal, but the probe results show that more
English exposure at the conservative learning rate did not improve factual extractability.

The best direct top1 under the English gate was only `0.016` at `checkpoint-124`.
The best QA-matched top1 was also only `0.016` at `checkpoint-124`.
The strongest robust direct-and-QA overlap was `3/500`, also at `checkpoint-124`.

This is weaker than the first pilot and clearly insufficient for M1 promotion.

Conclusion:

```text
Do not promote any checkpoint from the LR 5e-5 / 3 epoch pilot as M1.
```

## Next Action

The current M1 recipe has now failed in three tested variants:

1. `5e-5`, 1 epoch
2. `1e-4`, 1 epoch
3. `5e-5`, 3 epochs

The next step should be a recipe change rather than another small extension of the same
setup. Candidate directions include:

1. change model scale,
2. change objective or data formatting,
3. increase per-fact repetition strength more aggressively,
4. revisit whether raw CLM over `english_training.jsonl` is too weak for the learned-fact gate.
