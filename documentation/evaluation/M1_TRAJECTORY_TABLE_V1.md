# M1 factual-access and retention trajectory table v1

**Status:** prepared schema; no new measurement executed

This table implements the supervisor request to show how factual access and language retention
change from the frozen M0 parent through M1 training.

## Canonical grain

One row represents one exact `model × seed × checkpoint`. The source of truth remains long-form
checkpoint, metric and factual-probe tables; the trajectory table is a generated review view.

Required columns:

```text
model_id, model_revision, seed, run_id, state, checkpoint_id, checkpoint_sha256,
update, epoch, normalized_progress, cumulative_examples, cumulative_fact_exposures,
cumulative_supervised_tokens, cumulative_total_tokens,
factual_exact_prefix_accuracy, factual_top1_accuracy, robust_fact_intersection,
minimum_relation_robust_accuracy, relation_forced_choice_accuracy,
wikitext_bpb, parent_wikitext_bpb, delta_bpb,
byte_perplexity, parent_byte_perplexity, byte_perplexity_ratio,
retention_score_visualization_only,
blimp_accuracy, hellaswag_acc_norm, generation_integrity_status,
cadence_class, record_status, missing_reason
```

## Cadence

- prospective matched M1: M0 parent plus every epoch-end checkpoint for cheap factual access,
  WikiText retention and cheap integrity;
- full suite: entry, precommitted midpoint and endpoint;
- exact-prefix: every checkpoint required by the frozen M1 contract;
- historical backfill: only weights that actually exist; never interpolate missing epochs.

## Metric roles

- primary retention: raw WikiText BPB and `delta_bpb = checkpoint − M0`;
- companion: byte-perplexity ratio;
- visualization only: `retention_score = 100 / byte_perplexity_ratio`;
- fact access: top-1 plus robust intersection; exact-prefix alone is insufficient;
- factual exposure: actual cumulative training-row exposure from the trace, not an inferred epoch
  label when the historical manifest cannot prove the schedule.

## Missingness vocabulary

- `complete`: measured on the exact checkpoint;
- `not_observed_historically`: checkpoint/trace field was never retained;
- `not_run`: eligible artifact exists but evaluation was not executed;
- `failed_pre_scoring`: attempted operation produced no scientific metric;
- `not_in_contract`: metric/cadence does not apply.

No missing value is converted to zero, forward-filled or estimated from a later checkpoint.

## Decision use

The historical table answers “what can be reused without retraining?” It cannot by itself answer a
matched OLMo–Qwen–SmolLM model-family comparison when recipes, fact counts or objectives differ.
That comparison requires a prospective frozen M1 contract with every-epoch snapshots enabled.

## Traceability to supervisor feedback

The epoch-by-epoch fact-access/retention requirement and presentation handoff are operationalized
in [`MAX_FEEDBACK_AND_RUN_RECORDING_PROTOCOL_2026-08-22.md`](../decisions/MAX_FEEDBACK_AND_RUN_RECORDING_PROTOCOL_2026-08-22.md).
That protocol binds each trajectory row to immutable training/evaluation artifacts, resolved
hyperparameters, checkpoint hashes and generated figure metadata.
