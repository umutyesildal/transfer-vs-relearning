# 30 - M1 Two-Stage Stage B2 Eval Retry Note

Date: 2026-07-07

## Why This Note Exists

Stage B2 training completed successfully, but the first checkpoint-evaluation attempt did
not produce usable metrics. This note records exactly why, what was fixed, and what still
remains to be rerun.

## Training Run Being Evaluated

Run directory:

```text
runs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only/20260707T181202Z_m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1_0d974577
```

Real retained checkpoints:

- `checkpoint-478`
- `checkpoint-956`
- `checkpoint-1434`
- `checkpoint-1912`
- `checkpoint-1914`

## First Eval Failure

The first eval wave failed for two separate reasons:

1. the initial checkpoint guesses included nonexistent paths such as `checkpoint-479`,
   `checkpoint-958`, and `checkpoint-1437`;
2. even after switching to the real checkpoint directories, the evaluator tried to load
   the tokenizer directly from the checkpoint snapshot, but those checkpoint folders did
   not contain a usable fast-tokenizer backend.

Observed failure class:

```text
AutoTokenizer fast-backend instantiation failure from checkpoint-only directory
```

This means the model weights were present, but the evaluation manifest/evaluator path
resolution was not robust enough for checkpoint-only snapshots.

## Fix Applied

Training repo fix commit:

```text
4db0688
```

What this patch changed:

- evaluator now resolves the model-weight path and tokenizer path separately;
- checkpoint manifests can now carry explicit tokenizer-source fields;
- if those fields are absent, evaluator falls back to the training run's
  `training_manifest.json` and reads the base-model manifest payload from there;
- run manifests now record `local_tokenizer_snapshot` for traceability.

Validation after the fix:

- local focused tests: passed
- HU focused tests after pull: passed

## Current Status

Scientific status at the time of this note:

- Stage B2 training was complete.
- The evaluator bug had been fixed.
- A clean B2 checkpoint-eval resubmission was still pending.

## Planned Retry

This retry was later submitted successfully. See the dedicated evaluation report for the
final job IDs and metric outcome.

When submission is available again, rerun English direct and QA-matched evaluation only
for these five checkpoints:

- `checkpoint-478`
- `checkpoint-956`
- `checkpoint-1434`
- `checkpoint-1912`
- `checkpoint-1914`

Use the corrected Stage B2 eval helper/config path that isolates the retry wave from the
older invalid YAMLs.
