# 08 - M1 Pilot LR5e-5 Epoch1 Run Report

Last updated: 2026-07-05

This report tracks the first M1 English fact acquisition pilot.

## Run Identity

Purpose:

```text
M1 pilot: GPT-2 continued CLM on English synthetic facts only.
```

Local implementation commit:

```text
be230625897a3f941842ef95f19bbdc4a20743b3 - Add M1 English fact acquisition training
```

HU repository after pull:

```text
be230625897a3f941842ef95f19bbdc4a20743b3
```

Training config:

```text
configs/training/m1_gpt2_english_facts_lr5e-5_ep1.yaml
```

Slurm job:

```text
378783 - first attempt, failed before optimizer training due TrainingArguments mismatch
378784 - retry after compatibility fix, completed
```

Training run directory:

```text
runs/training/m1_gpt2_english_facts/20260705T194836Z_m1_gpt2_english_facts_lr5e-5_ep1_1a968945 - failed first attempt
runs/training/m1_gpt2_english_facts/20260705T195512Z_m1_gpt2_english_facts_lr5e-5_ep1_1a968945 - completed retry
```

## Preflight

HU pull completed as a fast-forward from `638b697` to `be23062`.

HU smoke test:

```text
PYTHONPATH=src conda run --name xfer-relearn python -m pytest tests/test_training_core.py -q -ra
```

Result:

```text
4 passed
```

## Initial Queue And Logs

Immediately after submit:

```text
JOBID 378783
STATE R
NODE gruenau9
TIME_LIMIT 4:00:00
GPU NVIDIA A100 80GB PCIe
```

Startup log confirmed:

- `CUDA_VISIBLE_DEVICES=0`
- Python `3.11.15`
- config `m1_gpt2_english_facts_lr5e-5_ep1.yaml`
- learning rate `5.0e-5`
- epoch count `1.0`
- BF16 enabled
- training input `artifacts/datasets/synthetic_v1/output/english_training.jsonl`

Initial run manifest status:

```text
status: started
train_rows: 104169
git_commit: be230625897a3f941842ef95f19bbdc4a20743b3
dataset_manifest_sha256: c3ab6f53855c837359e26d22d9db40fd57b3ecce7939e6af747af015754c1763
train_file_sha256: 81d72d8a29ce197141baf0bc3938d729b5bfe5f2904d142779d4115e0d7b42f2
```

## First Attempt Result

The first Slurm attempt ended before optimizer training began.

Observed progress before failure:

- model weights loaded successfully,
- JSONL dataset loaded successfully,
- train split generated with 104,169 examples,
- tokenization completed,
- 512-token grouping completed.

Failure:

```text
TypeError: TrainingArguments.__init__() got an unexpected keyword argument 'overwrite_output_dir'
```

Root cause:

```text
HU environment uses transformers 5.13.0. Its TrainingArguments signature does not accept
some older/common Trainer kwargs such as overwrite_output_dir, do_train, do_eval, or
warmup_ratio.
```

Fix:

```text
e2890f7 - Fix TrainingArguments compatibility for M1
```

The fix filters `TrainingArguments` kwargs by the runtime signature and converts
`warmup_ratio` into explicit `warmup_steps`.

Local validation after fix:

```text
PYTHONPATH=src python3 -m pytest tests/test_training_core.py tests/test_data_core.py tests/test_evaluation_core.py -q -ra
```

Result:

```text
36 outcomes; 2 expected local skips because torch is not installed locally.
```

## Completed Retry

Retry job:

```text
378784
```

Completed run directory:

```text
runs/training/m1_gpt2_english_facts/20260705T195512Z_m1_gpt2_english_facts_lr5e-5_ep1_1a968945
```

Final manifest status:

```text
complete
```

Final model:

```text
runs/training/m1_gpt2_english_facts/20260705T195512Z_m1_gpt2_english_facts_lr5e-5_ep1_1a968945/final_model
```

Saved checkpoints:

```text
checkpoint-42
checkpoint-84
checkpoint-126
checkpoint-166
```

Training shape:

```text
train_blocks: 2644
eval_blocks: 54
estimated_optimizer_steps: 166
save_steps: 42
eval_steps: 42
warmup_steps: 8
```

Software/runtime:

```text
GPU: NVIDIA A100 80GB PCIe
torch: 2.7.0+cu128
cuda: 12.8
transformers: 5.13.0
datasets: 5.0.0
```

Training metrics:

```text
train_loss: 2.815246306270002
train_runtime: 78.5878 seconds
train_samples_per_second: 33.644
train_steps_per_second: 2.112
epoch: 1.0
```

Evaluation metrics:

```text
eval_loss: 2.2544260025024414
eval_runtime: 0.3526 seconds
eval_samples_per_second: 153.133
eval_steps_per_second: 19.851
epoch: 1.0
```

Logged loss curve:

```text
step ~10: train loss 4.852
step ~20: train loss 3.791
step ~40: train loss 3.050
checkpoint-42 eval_loss: 2.773
checkpoint-84 eval_loss: 2.376
checkpoint-126 eval_loss: 2.269
checkpoint-166/final eval_loss: 2.254
```

## Interpretation

The first M1 pilot completed successfully after the compatibility fix. The CLM loss dropped
substantially over one epoch, and the validation loss improved at every checkpoint. This is
a training-health signal only; it does not yet prove factual acquisition.

The next scientific step is to evaluate the saved checkpoints with the existing factual
candidate-ranking evaluator on English direct and English QA-matched probes.

Do not start the remaining LR/epoch pilot jobs until the user approves the next action.
