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

## R3 — Freeze the M2 corpus and sibling contract

Status: active corpus qualification; training execution disabled.

- preserve the running mixed-source D0 v3 wave as characterization evidence and verify its
  terminal artifacts;
- use only cleaned OSCAR-2201-derived vngrs rows as the prospective main M2 training source;
- keep mC4-derived rows training-excluded and preserved; do not substitute them automatically;
- freeze the exact OSCAR source label/predicate, quality/provenance, held-out split, 64-document
  review packet and per-model token budget in a new contract;
- preserve `trwiki-20260601` as cross-domain control;
- bind M2-A and M2-B to the same selected M1 parent and matched budgets;
- define controlled Turkish factual re-exposure only for M2-B.

## R4 — Execute and compare M2-A/M2-B

Status: not authorized.

Run the sibling arms, apply the unchanged eval-v2 bundle, compute the precommitted transfer versus
relearning contrasts, and generate thesis-ready tables and figures.
