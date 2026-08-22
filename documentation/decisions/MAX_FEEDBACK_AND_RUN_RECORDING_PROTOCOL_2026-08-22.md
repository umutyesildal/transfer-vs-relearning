# Max feedback and run-recording protocol — M1 onward

**Date:** 2026-08-22  
**Status:** design/traceability protocol; no execution  
**Purpose:** make every future M1/M2 run presentation-ready without reconstructing evidence later

## Max feedback mapped to project artifacts

| Feedback / requirement | Required record | Existing implementation boundary |
|---|---|---|
| Track fact access and retention from the beginning, every epoch | one row per `model × seed × checkpoint`, including parent M0 and every epoch end | `M1_TRAJECTORY_TABLE_V1.md`, planner dense points and `TrainingTraceRecorder` epoch events |
| Show how much factual access and retention changes over training | factual top-1, robust intersection, relation control, exact-prefix, BPB/PPL/ratio and deltas against M0 | `metric_observations.parquet`, `factual_probe_results.parquet`, `trajectory_wide.csv` |
| Record batch size, gradient accumulation and sequence length | microbatch, accumulation, effective batch, block size, world size, tokenization statistics | static trace manifest, planner-derived schedule, `hyperparameters.csv` |
| Preserve all training facts for later slides | immutable config/model/dataset/runtime hashes, optimizer logs, epoch snapshots and checkpoint hashes | `training_trace_manifest.json`, `events/`, `snapshots/`, checkpoint registry |
| Capture failures rather than hiding them | typed status and missing reason; raw artifact path/hash; trace event ordering | result schema, trace index and `evaluation_manifest.json` |
| Make results presentation-ready | generated plots, captions and figure manifest derived from canonical long tables | `presentation/plot_data/`, `presentation/captions.json`, `presentation/figure_manifest.json` |

## Canonical per-run layout

Every authorized run must use one fresh scratch root with this logical structure:

```text
run_root/
├── run_manifest.json                 # contract/config/model/data/runtime identities
├── training_trace_manifest.json      # immutable run identity + hyperparameters
├── trace_index.json                  # ordered event hashes
├── events/                            # train begin, optimizer logs, epoch ends, eval, failures
├── snapshots/epoch-000..              # model-only snapshots; each has snapshot_manifest.json
├── checkpoint_registry.parquet       # one canonical row per state/checkpoint
├── metric_observations.parquet       # long-form LM-eval/project metrics
├── factual_probe_results.parquet     # fact/probe/form/scaffold rows
├── trajectory_wide.csv               # generated review view, never source of truth
├── hyperparameters.csv               # presentation-friendly resolved values
├── evaluation_manifest.json          # status, counts, missingness and raw references
├── raw/                               # immutable Harness/project outputs and hash ledger
└── presentation/
    ├── plot_data/
    ├── figure_manifest.json
    └── captions.json
```

Raw artifacts are never overwritten. A rerun gets a new root and a new identity; historical
failures remain linked by contract/config/model/data hashes.

## Required checkpoint row

The source row is long-form and must carry:

```text
model/state/arm/seed/run/checkpoint identity
checkpoint SHA-256, update, epoch, normalized progress
cumulative examples and cumulative fact exposures
cumulative supervised and total non-pad tokens
learning rate, train loss, microbatch, accumulation and effective batch
sequence length, padding/truncation statistics, precision and hardware class
record status, manifest path and manifest SHA-256
```

The parent M0 row is explicit. Missing historical checkpoints use typed missingness and are never
zero-filled, interpolated or silently copied from a neighboring checkpoint.

## Required evaluation row

Every active M0/eval-v2 family inherited by M1 writes raw and normalized rows with:

```text
eval contract, task/revision/split, checkpoint and state
metric/filter/role, raw value/unit, denominator and sample count
uncertainty method and CI when applicable
parent comparison, absolute delta and ratio
result status, missing reason, raw artifact path and SHA-256
```

The factual table additionally records subject/fact/probe/direction/relation/form/scaffold,
predicted object, answer-token likelihoods, rank, margin and probe-registry hash. This preserves
the A–D robust system and exact-prefix evidence instead of reducing it to one aggregate score.

## Epoch cadence for M1

```text
checkpoint 0: frozen M0 parent
each epoch end: cheap factual + exact-prefix + WikiText retention + cheap integrity
entry/midpoint/endpoint: complete active eval-v2 bundle
every checkpoint: immutable snapshot and trace row
```

The same M0 metric/task identities apply to M1. Pile-10k remains retired and produces no M1 row.
The chosen M1 TurBLiMP route is the M0 `juletxara/turblimp` identity.

## Presentation outputs generated after completion

The canonical tables generate at least these views:

1. factual access versus epoch and cumulative fact exposure;
2. WikiText BPB and BPB delta versus epoch/exposure;
3. PPL ratio as companion retention evidence;
4. fact-access/retention Pareto view;
5. M2-A versus M2-B branch comparison using the matched parent and budget.

The visual `retention_score = 100 / PPL ratio` is presentation-only. Raw BPB, PPL, ratio, factual
accuracy and confidence intervals remain the scientific evidence.

## Auditability rule

The presentation bundle is generated from hashed long-form tables, never from manually copied
numbers. Each figure has a manifest entry naming its source table, filters, checkpoint IDs,
contract/config hashes and caption metadata. A future slide can therefore be regenerated from the
run root without searching terminal history.

This protocol records Max’s feedback as a mandatory pipeline invariant. It does not authorize
M1/M2 training, evaluation, corpus materialization or HU/Slurm execution.
