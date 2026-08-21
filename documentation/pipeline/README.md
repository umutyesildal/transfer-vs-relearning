# Experiment pipeline v1

**Status:** scientific M0 operator frozen; later stages planner-only | **Execution authorization:** one M0 wave only

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

The human-oriented Turkish deep dive covering the full design, metric formulas, thresholds,
artifacts and current scientific M0 wave is
[`EVAL_V1_AND_END_TO_END_PIPELINE_DEEP_DIVE_TR.md`](../evaluation/EVAL_V1_AND_END_TO_END_PIPELINE_DEEP_DIVE_TR.md).
It is explanatory reference material, not an execution contract.

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

## Historical M0 qualification evidence

[`../../scripts/study/run_m0_olmo_evaluation.py`](../../scripts/study/run_m0_olmo_evaluation.py)
was the OLMo qualification entrypoint. It partitioned the qualification bundle into seven
independent GPU lanes:

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

TurkishMMLU is excluded from eval-v1 because the exact data is author-contact access only. Adding it
later requires a separately frozen eval-v2; it is not merged into the current Turkish lane.

The current draft can be inspected without evaluation:

```bash
.venv/bin/python scripts/study/run_m0_olmo_evaluation.py plan
.venv/bin/python scripts/study/run_m0_olmo_evaluation.py preflight
```

The qualification config is frozen with exact implementation/environment hashes and bounded cache
limits. V8 completed six lanes; its `english_capability` lane encountered a foreign-process OOM
before scoring. The separately frozen recovery reused the six hash-validated results, ran only that
lane on a V100 after a 16 GiB free-memory gate, and produced a complete 7/7 composite bundle. The
bundle remains `test_only_non_scientific`. WikiText and TurBLiMP parity subsequently passed and
eval-v1 was frozen by Documents 179 and 180. See the
[`v8 recovery contract`](../contracts/evaluation/m0-olmo-v8-english-capability-recovery-v1.md).

## Scientific three-model M0 entrypoint

[`../../scripts/study/run_three_model_m0_evaluation.py`](../../scripts/study/run_three_model_m0_evaluation.py)
is the current operator-facing scientific M0 entrypoint. It binds the exact OLMo, Qwen2.5-1.5B and
SmolLM2-1.7B assets to the same frozen eval-v1 inputs. Every model receives eight independent lanes:

| Lane | Work |
|---|---|
| `english_retention_wikitext` | full WikiText token loss and BPB |
| `english_retention_pile_10k` | full Pile-10k token loss and BPB |
| `english_grammar_blimp` | full 67-subtask BLiMP group |
| `english_capability` | HellaSwag and three WinoGender slices |
| `turkish_capability` | full 16-subtask TurBLiMP group |
| `turkish_retention_trwiki` | frozen trwiki validation token loss and UTF-8 BPB |
| `factual_access` | full 12,000-row bilingual factual suite |
| `generation_integrity` | degeneration and frozen generic completions |

That is 24 GPU lanes. Before submitting anything, the family controller runs every model's
read-only identity preflight. A blocker in any model submits zero jobs. Once separately authorized,
the three per-model DAGs are submitted independently and in parallel; a family finalizer records
their raw states. V100-32GB and A100-80GB are preferred, with RTX3090, RTX6000 and RTXA6000 frozen
as fallbacks inside a 900-second start window. The operator returns after submission and never
waits for the evaluations.

Inspect the exact plan and preflight without inference or scoring:

```bash
.venv/bin/python scripts/study/run_three_model_m0_evaluation.py plan
.venv/bin/python scripts/study/run_three_model_m0_evaluation.py preflight
```

The frozen contract is
[`m0-three-model-scientific-v1.md`](../contracts/evaluation/m0-three-model-scientific-v1.md).
The user subsequently authorized exactly one wave through the
[`single-wave authorization overlay`](../contracts/evaluation/m0-three-model-scientific-v1-authorization-2026-08-16.md).
The authorized operator repeats an exact 30 GiB HU-home measurement before submission, keeps
HU-home writes forbidden and cannot reuse the authorization because the fixed family root must be
fresh.

That single wave was submitted on 2026-08-16. Its 24 GPU lane IDs are `461861`–`461868`,
`461875`–`461882` and `461889`–`461896`; family finalizer `461898` joins the three model finalizers.
The authorization is consumed. Status inspection is read-only and no second submit or automatic
reroute is allowed.

## Remaining production boundary

The planner, trace/artifact contracts and fail-closed M0 Harness/project/parallel adapters are
implemented. The scientific three-model M0 raw-result layer is frozen and authorized for one
standalone wave. Its canonical scientific normalizer and every M1/M2 training adapter remain
separate work. The full-study plan therefore remains `execution_authorized: false`.

## Full M0→M2 study control

[`../../scripts/study/run_study.py`](../../scripts/study/run_study.py) owns the complete lifecycle:

```text
contract preflight
→ M0 evaluation + M0 probing + M0 exact-prefix → normalization
→ M1 training → evaluation + probing + exact-prefix → checkpoint selection
→ matched M2 sibling preflight
→ M2-A training + M2-B training
→ identical branch evaluation + probing + exact-prefix
→ paired branch analysis → presentation bundle
```

Render the complete 19-stage graph without scientific execution:

```bash
.venv/bin/python scripts/study/run_study.py run \
  --config configs/studies/m0_to_m2_eval_v1_template.yaml \
  --dry-run
```

The tested full-study runner accepts only registered Python adapters; it never executes arbitrary
shell text from YAML. The dedicated M0 controller likewise maps only four fixed adapter types and
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
single-model workflow across the exact OLMo, Qwen2.5-1.5B and SmolLM2-1.7B assets. It produces thirteen
three-job waves and keeps a barrier between waves:

```text
3× M0 evaluation
→ 3× M0 exact-prefix
→ 3× M1 training → 3× M1 evaluation → 3× M1 exact-prefix
→ 3× M2 sibling preflight
→ 3× M2-A training → 3× M2-B training
→ 3× M2-A evaluation → 3× M2-A exact-prefix
→ 3× M2-B evaluation → 3× M2-B exact-prefix
→ 3× paired branch analysis
```

That is 39 nodes: 24 state-evaluation nodes, 9 training nodes and 6 local preflight/analysis
nodes. M2-A and M2-B remain siblings from the same exact M1 parent with matched budgets. Inspect the
whole graph without execution:

```bash
.venv/bin/python scripts/study/run_model_matrix.py run --dry-run
```

Generate 39 one-model/one-stage Luna packets with:

```bash
.venv/bin/python scripts/study/run_model_matrix.py packets \
  --output-dir /tmp/three-model-luna-packets
```

The current matrix is `planned_not_authorized`. Its three scientific M0 bindings are frozen; the
missing M1/M2 recipes remain explicit null bindings with named blockers, so `run` still refuses the
full external workflow. See the
[`three-model planning contract`](../contracts/three-model-study-matrix-v1.md).

Historical exact-prefix is a mandatory candidate-ranking supplement, not a free-generation exact
match metric. Every M0/M1/M2-A/M2-B checkpoint set must provide a complete, hash-bound 500-probe
manifest. Missing probes, checkpoints, or identity drift fail closed before normalization,
checkpoint selection, or branch analysis.
