# Evaluation result schema v1

**Status:** draft schema | **Canonical form:** long tables plus immutable raw artifacts

## Why long form

A single wide row gains a new column whenever a task or subgroup changes and becomes hard for
agents to validate. eval-v1 therefore stores stable long-form observations. A one-row-per-checkpoint
trajectory is a generated view, never the source of truth.

## Artifact set

| File | Grain | Purpose |
|---|---|---|
| `checkpoint_registry.parquet` | one row per state/seed/checkpoint | identity, dose, optimization and sequence trace |
| `metric_observations.parquet` | one row per metric/filter/checkpoint | normalized harness and project metrics |
| `factual_probe_results.parquet` | one row per factual probe/checkpoint | paired causal and robustness analysis |
| `evaluation_manifest.json` | one per evaluation namespace | hashes, environment, inputs, status and artifact inventory |
| `trajectory_wide.csv` | generated one row per checkpoint | human review and plotting only |

CSV mirrors may accompany Parquet for inspection. JSONL is used only where append-safe progress is
required. Raw harness/project outputs remain immutable and are referenced by SHA-256.

## Checkpoint registry required fields

```text
eval_contract, experiment_id, state, parent_state, arm, model_id, model_revision,
tokenizer_id, tokenizer_revision, run_id, seed, checkpoint_id, checkpoint_sha256,
update, epoch, normalized_progress, cumulative_examples, cumulative_fact_exposures,
cumulative_supervised_tokens, cumulative_total_tokens, learning_rate, train_loss,
microbatch, gradient_accumulation, effective_row_batch, max_sequence_length,
mean_nonpad_tokens, p50_nonpad_tokens, p95_nonpad_tokens, padding_fraction,
truncation_count, truncation_rate, precision, hardware_class,
record_status, manifest_path, manifest_sha256
```

Future runs source these fields from the training-trace manifest and epoch-end events. Historical
rows may contain explicit `not_observed_historically` missingness but must not infer missing epoch
weights or token statistics.

## Metric observation required fields

```text
eval_contract, experiment_id, state, parent_state, arm, seed, checkpoint_id,
lane, family, task_id, task_version, dataset_id, dataset_revision, split,
prompt_id, fewshot, metric, filter, role, value, unit, higher_is_better,
denominator_name, denominator_value, sample_count, stderr, ci_low, ci_high,
uncertainty_method, comparison_reference, absolute_delta, ratio_to_reference,
result_status, missing_reason, raw_artifact_path, raw_artifact_sha256
```

`role` is one of `primary`, `guardrail`, `secondary`, `sensitivity`, or `diagnostic`.
`result_status` is one of `complete`, `not_run`, `failed_pre_scoring`, `partial_invalid`, or
`not_in_contract`.

## Factual probe required fields

The existing evaluator fields are retained, including subject/fact/probe IDs, direction, relation,
form, scaffold, rendered prompt, candidate inventory identity, correct/predicted object, mean and
total scores, rank, margin, token count, relation-swap fields and failure type. eval-v1 adds state,
parent, arm, seed, checkpoint identity, probe-registry hash and contract version.

## Comparison rules

- Compare rows only when task version, dataset revision, split, prompt, few-shot and scoring
  semantics match.
- M1 acquisition is M1 minus M0 on identical probes.
- M2-A transfer is M2-A minus M1 for TR→EN.
- M2-B relearning is M2-B minus M2-A for TR→EN.
- English retention compares each state with its immediate parent; M2 arms use the same M1 row.
- Retention's primary comparison is raw BPB plus `absolute_delta = checkpoint − parent`. PPL ratio
  is companion evidence; BPB ratio is optional diagnostic only.
- No missing value is converted to zero, dropped from a denominator, or forward-filled.
- Aggregate views fail closed unless every required component row is `complete`.

## Uncertainty

Primary factual contrasts use 10,000-draw paired subject bootstrap with seed 42. Harness-native
stderr is stored for benchmark metrics but is not substituted for the paired causal interval.
Across seeds, every seed is shown; a replicated claim requires the precommitted sign/confidence
rule for every required seed. Derived `retention_score = 100 / PPL_ratio` may appear only in plot
data and is never a gate.
