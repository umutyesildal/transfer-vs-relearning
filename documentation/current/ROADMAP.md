# Current roadmap

This file orders work; it never authorizes external execution.

## Completed

- repository migration, history sanitation and documentation control plane;
- evaluator inventory and LM Evaluation Harness qualification;
- frozen Pile-free `eval-v2` protocol;
- three-model M0 evidence closure: 21/21 active lanes, 3/3 exact-prefix and 42 normalized rows;
- Relation V2 M1 dataset identity and fixed OLMo/Qwen/SmolLM cohort;
- epoch-level training trace, model-only snapshots and presentation schema.

## R1 — Finish local M1 productionization

Status: active; execution disabled.

- remove the circular dependency on training-produced manifests;
- produce stable training and checkpoint binding manifests after each training run;
- validate the matched three-model DAG and immutable output roots;
- complete the registered Slurm adapter without submitting it;
- freeze one reviewable execution-disabled M1 contract/config pair;
- run offline unit, control-plane and dry-run tests.

Exit condition: one command can validate the future preflight → three parallel trainings →
checkpoint eval fan-out → normalization → presentation DAG, while refusing to execute without the
new exact user authorization.

## R2 — Execute M1 only after the user says start

Status: not authorized.

- synchronize the reviewed commit to HU;
- run final read-only identity/storage/scheduler preflight;
- submit exactly the contract-bound M1 DAG once;
- record every job, manifest, checkpoint, metric, failure and missing value;
- produce Max's epoch-level fact-access/retention tables and figures.

## R3 — M2 corpus, sibling contract and scientific training

Status: complete. OSCAR selection/audit/review, three-model token accounting, exact matched blocks,
fact corrections, optimizer smoke and all six OLMo/Qwen/SmolLM × M2-A/M2-B training runs are
complete. Sixty precommitted checkpoints exist.

- preserve every historical failure/recovery root and the successful training root read-only;
- preserve cleaned OSCAR as the sole main training source and mC4 as excluded evidence;
- preserve the matched per-arm token/update/checkpoint recipe and corrected M2-B facts;
- do not rerun, duplicate, clean or delete training artifacts.

## R4 — Finalize bindings, then evaluate and compare M2-A/M2-B

Status: CPU finalizer repair PASS; 6-run/60-checkpoint family and 63-state matrix hash-closed;
evaluation/scoring not authorized.

Prepare and offline-test a new evaluation execution adapter/contract against the frozen matrix.
Only after a new exact user authorization may eval-v2 run, compute the precommitted transfer versus
relearning contrasts, and generate thesis-ready tables and figures.
