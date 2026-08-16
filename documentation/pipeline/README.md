# Experiment pipeline v1

**Status:** local foundation, planner-only | **Execution authorization:** none

This layer turns one reviewed experiment manifest into a deterministic sequence:

```text
identity/storage preflight
  → train + optimizer/epoch trace + model-only epoch snapshots
  → dense evaluation at parent and every epoch
  → full evaluation at entry/midpoint/endpoint
  → canonical long-table normalization
  → presentation bundle
```

It reuses the existing trainer and evaluators. It does not replace them, choose scientific gates,
download inputs, submit Slurm jobs or grant execution authority.

## Current entry point

The prospective OLMo planning example is
[`../../configs/pipelines/eval_v1_olmo_epoch_trajectory_template.yaml`](../../configs/pipelines/eval_v1_olmo_epoch_trajectory_template.yaml).
Render and validate its non-executable plan with:

```bash
.venv/bin/python scripts/study/plan_experiment_pipeline.py \
  --config configs/pipelines/eval_v1_olmo_epoch_trajectory_template.yaml \
  --output /tmp/eval-v1-pipeline-plan.json
```

The command performs no training or evaluation. `--initialize-artifact-scaffold` may create a fresh
typed namespace with status `planned_not_run`; it refuses to overwrite an existing namespace and
contains zero result rows.

## What future training records

The opt-in `tracking` block in a training config activates:

- a static manifest containing model/data/config identities and every relevant hyperparameter;
- exact effective row batch and epoch/update mapping;
- tokenizer length, padding, truncation and supervised-token statistics;
- immutable optimizer-log and epoch-end event files with an atomic index;
- cumulative examples, fact exposures, supervised tokens and total non-padding tokens;
- loss, learning rate, gradient norm and progress at each epoch;
- one model-only epoch snapshot, file inventory and checkpoint SHA-256;
- initial and per-snapshot live storage guards.

Model-only epoch snapshots support retrospective dense evaluation. Separately saved milestone
checkpoints retain optimizer/scheduler/RNG state for recovery. These roles must not be conflated.

## Evaluation and presentation artifacts

The canonical sources are `checkpoint_registry.parquet`, `metric_observations.parquet` and
`factual_probe_results.parquet`. `trajectory_wide.csv` and the presentation directory are generated
views. The required figure identities are:

- fact access versus epoch;
- retention versus epoch using raw BPB and ΔBPB;
- fact-access/retention Pareto view;
- M2-A/M2-B sibling comparison.

Captions must carry model/data revisions, seed, microbatch, gradient accumulation, effective batch,
sequence length and precision. A missing result remains explicit and keeps its figure status
incomplete.

## Historical evidence

The historical OLMo family has weights only at parent and updates
`42/84/126/168/210/252`, mapping to epochs `0/6/12/18/24/30/36`. The historical-backfill planner
accepts only those points. It never interpolates or invents the missing epoch weights.

## M0 parallel evaluation entrypoint

[`../../scripts/study/run_m0_olmo_evaluation.py`](../../scripts/study/run_m0_olmo_evaluation.py)
is the single operator-facing M0 entrypoint. It partitions the bundle into seven independent GPU
lanes:

| Lane | Work |
|---|---|
| `english_retention_wikitext` | canonical WikiText rolling retention |
| `english_retention_pile_10k` | broad-domain Pile-10k retention control |
| `english_grammar_blimp` | BLiMP group |
| `english_capability` | HellaSwag and WinoGender slices |
| `turkish_capability` | TurBLiMP |
| `factual_access` | project-native factual ranking and paired uncertainty inputs |
| `generation_integrity` | project-native degeneration/integrity panel |

One online CPU/data preflight resolves and caches every included Harness task. Only after that job
passes do seven independent, scheduler-routed Slurm jobs run the lanes. Each active lane owns one
GPU/model process; the controller does not multiplex model instances on one GPU. An `afterany`
finalizer inventories every outcome, while complete normalization opens only after all required
lanes finish with identical plan and classification identities.

TurkishMMLU is excluded from qualification v1 because access is unresolved. This does not settle its
eval-v1 role. A later inclusion would use a separate five-shot lane and new contract version; it is
not merged into the zero-shot Turkish lane.

The current draft can be inspected without evaluation:

```bash
.venv/bin/python scripts/study/run_m0_olmo_evaluation.py plan
.venv/bin/python scripts/study/run_m0_olmo_evaluation.py preflight
```

The qualification config is frozen with exact implementation/environment hashes and bounded cache
limits. V8 completed six lanes; its `english_capability` lane encountered a foreign-process OOM
before scoring. The separately frozen recovery reused the six hash-validated results, ran only that
lane on a V100 after a 16 GiB free-memory gate, and produced a complete 7/7 composite bundle. The
bundle remains `test_only_non_scientific`; WikiText and TurBLiMP parity still block eval-v1 freeze.
See the
[`v8 recovery contract`](../contracts/evaluation/m0-olmo-v8-english-capability-recovery-v1.md).

## Remaining production boundary

The planner, trace/artifact contracts and fail-closed M0 Harness/project/parallel adapters are
implemented locally. The M0 qualification adapter is the only executable slice; its scientific
normalizer and all later-state evaluator/training adapters remain blocked on eval-v1 qualification
and separate contracts. The full-study plan therefore remains `execution_authorized: false` even
though the isolated M0 qualification config is test-only authorized.

## Full M0→M2 study control

[`../../scripts/study/run_study.py`](../../scripts/study/run_study.py) owns the complete lifecycle:

```text
contract preflight
→ M0 evaluation + M0 probing in parallel → normalization
→ M1 training → evaluation + probing → checkpoint selection
→ matched M2 sibling preflight
→ M2-A training + M2-B training
→ identical branch evaluation + probing
→ paired branch analysis → presentation bundle
```

Render the complete 15-stage graph without scientific execution:

```bash
.venv/bin/python scripts/study/run_study.py run \
  --config configs/studies/m0_to_m2_eval_v1_template.yaml \
  --dry-run
```

The tested full-study runner accepts only registered Python adapters; it never executes arbitrary
shell text from YAML. The dedicated M0 controller likewise maps only three fixed adapter types and
rejects submission until eval-v1 identities and exact authorization are frozen. Later training and
branch adapters remain unregistered.

Before implementing or starting the first M0 lane, inspect every machine-readable gate with:

```bash
.venv/bin/python scripts/study/run_study.py preflight-m0 \
  --config configs/studies/m0_to_m2_eval_v1_template.yaml
```

The command performs no inference or scoring and exits nonzero while any contract, binding,
environment or adapter prerequisite is unresolved.

## Three-model cohort control

[`../../scripts/study/run_model_matrix.py`](../../scripts/study/run_model_matrix.py) expands the
single-model workflow across the exact OLMo, Qwen2.5-1.5B and SmolLM2-1.7B assets. It produces nine
three-job waves and keeps a barrier between waves:

```text
3× M0 evaluation
→ 3× M1 training → 3× M1 evaluation
→ 3× M2 sibling preflight
→ 3× M2-A training → 3× M2-B training
→ 3× M2-A evaluation → 3× M2-B evaluation
→ 3× paired branch analysis
```

That is 27 nodes: 12 state-evaluation nodes, 9 training nodes and 6 local preflight/analysis
nodes. M2-A and M2-B remain siblings from the same exact M1 parent with matched budgets. Inspect the
whole graph without execution:

```bash
.venv/bin/python scripts/study/run_model_matrix.py run --dry-run
```

Generate 27 one-model/one-stage Luna packets with:

```bash
.venv/bin/python scripts/study/run_model_matrix.py packets \
  --output-dir /tmp/three-model-luna-packets
```

The current matrix is `planned_not_authorized`. Missing scientific M0 configs and M1/M2 recipes are
explicit null bindings with named blockers; `run` refuses external work. See the
[`three-model planning contract`](../contracts/three-model-study-matrix-v1.md).
