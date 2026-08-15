# 63 - M1 Checkpoint-250 Ranking Continuation Run Report

Last updated: 2026-07-11

## Status

The initial job `391085` failed before its first training update because the ranking trainer
tried to load tokenizer files from the checkpoint directory. The checkpoint contains model
weights but relies on the manifest's base-tokenizer fallback. Commit `53ccc10` fixed the
trainer to honor that manifest contract. Canonical retry job `391086` is running on
`gruenau9`.

## Reproducibility

- implementation commit: `fb2697e`
- tokenizer fallback fix: `53ccc10`
- branch: `corpus-update`
- base model: acquisition checkpoint 250
- training config:
  `configs/training/m1_smollm2_360m_acquisition_500_facts_ranking_continuation_lr5e-6_ep1.yaml`
- failed Slurm job: `391085`, no optimizer updates;
- active canonical retry: `391086`;
- duplicate retry: `391087`, cancelled while running after duplicate detection;
- node: `gruenau9`
- GPU: one A100 80GB PCIe
- Python: 3.11.15

## Preflight

- HU pull fast-forwarded to `fb2697e`;
- focused tests: 7 passed;
- checkpoint-250 model manifest exists;
- checkpoint-250 model directory exists;
- training JSONL contains exactly 3,500 rows;
- held-out direct and QA probes are disabled as training sources;
- retry tokenizer path resolves to the pinned SmolLM2-360M base artifact;
- active retry stderr was empty at startup.

## Failure And Retry Record

Job `391085` produced only a `started` manifest. The error was:

```text
ValueError: Couldn't instantiate the backend tokenizer
```

This did not consume training updates or alter a checkpoint. The trainer now loads model
weights from checkpoint 250 and tokenizer files from `tokenizer_source_path_absolute` in the
local model manifest. Unit and full-suite tests passed after the fix.

The first fixed retry was submitted as `391086`. Because its helper output did not expose the
job ID promptly, an identical `391087` retry was accidentally submitted. Once both jobs were
visible in Slurm, `391087` was cancelled and `391086` was retained. Only `391086` is eligible
for analysis.

## Training Contract

- ranking examples: 3,500;
- candidates per example: 16;
- negatives: 15 deterministic balanced same-relation candidates;
- epochs: 1;
- learning rate: `5e-6`;
- micro-batch: 2;
- gradient accumulation: 5;
- effective example batch: 10;
- optimizer updates: 350;
- checkpoint interval: 35 updates.

## Timing

The estimate scales the measured throughput of the previous ranking runs by the larger
candidate group and accumulation workload:

- expected average: approximately 12 minutes;
- safe range: 10-20 minutes.

No local sleep monitor is active. The job remains under Slurm control and will be inspected
when the user next requests status.

## Live Progress Check

At 11 minutes elapsed, canonical retry `391086` remained healthy with empty stderr. Because
`conda run` buffers the trainer's stdout, progress was verified from checkpoint directories:

```text
35, 70, 105, 140, 175, 210, 245, 280, 315
```

Checkpoint 315 means 90% of the planned 350 optimizer updates are complete. Checkpoints were
arriving approximately every 70-73 seconds. Estimated remaining time at this check was 1-3
minutes including the final checkpoint and model save. No sleep monitor was started.

## Final Training Result

Canonical retry `391086` completed without runtime errors:

- optimizer updates: 350/350;
- runtime: 716.26 seconds, or 11.94 minutes;
- aggregate logged train loss: 1.5508;
- train examples: 3,500;
- retained checkpoints: 35 through 350 at intervals of 35;
- final manifest status: `complete`;
- final stderr: model-loading and checkpoint-writing progress only.

The internal eval metrics are zero because `validation_fraction` was deliberately set to
zero to keep all 500 facts in training and avoid using held-out probes inside the trainer.
They are placeholders, not evidence of model failure. External exact/direct/QA evaluation is
the decision source.

## Next Step

The preselected checkpoint 35/70/105 evaluation wave was launched. Evaluate exact-prefix,
held-out direct, and QA-matched views before choosing any checkpoint for promotion. Job and
timing details are in `64_M1_CHECKPOINT_250_RANKING_CONTINUATION_EVALUATION_REPORT.md`.
