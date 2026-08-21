# Current roadmap

This roadmap orders work; it does not authorize external execution.

## R0 — Documentation control plane

Status: completed, validated, and published on `main`.

- keep root README and AGENTS compact;
- preserve previous guidance byte-for-byte;
- establish machine-readable project state;
- separate contracts, decisions, and records;
- update the Luna/Sol orchestrator for one monorepo and micro-context prompts;
- validate links, state invariants, preservation hashes, and tests.

Exit condition: a fresh agent can identify the current gate and one next task without reading the
full chronological archive. This condition is covered by control-plane tests and the accepted
documentation decision.

## R0.5 — Publication policy

Status: completed and verified on remote `main`.

- preserved the exact pre-filter branch in a verified private Git bundle;
- removed generated `output/` and `tools/synthetic-data/output/` paths from reachable history;
- retained the original source repositories and local scientific/user artifacts;
- verified zero reachable blobs at or above 10 MiB.

Exit condition: passed. A fresh secret and reachable-blob audit is still required immediately
before any later separately authorized publication.

## R1 — Evaluation inventory

Status: completed locally on `agent/eval-harness`.

Working branch: `agent/eval-harness`.

- inventory every current evaluation script, config, task, metric, denominator, output schema, and
  historical artifact shape;
- map each item to M0/M1/M2-A/M2-B and to factual access, retention, capability, or integrity;
- classify each item as reuse, repair, replace, or retire-with-history;
- identify exact parity and schema gaps.

Exit condition: a reviewed inventory with no unowned metric or evaluator.

Exit evidence: [`../evaluation/EVALUATOR_INVENTORY_V1.md`](../evaluation/EVALUATOR_INVENTORY_V1.md)
classifies the existing implementation as reuse, repair, replace, or historical-only. The hybrid
architecture and normalized schema own the previously missing integration surface.

## R2 — Evaluation qualification and freeze

Status: completed. eval-v1 is frozen; execution is not authorized.

- pin LM Evaluation Harness and exact task/dataset revisions;
- validate task IDs, prompts, few-shot settings, metrics, and availability;
- reconcile official WikiText word/byte PPL and BPB with custom retention evaluation;
- qualify the factual hard suite and generic degeneration panel;
- freeze normalized checkpoint rows, confidence intervals, missingness, cheap/full cadence, and
  gates;
- create `eval-v1` contract and acceptance tests.

Exit condition: semantic changes require `eval-v2`; all states use `eval-v1` unchanged.

Freeze evidence:

- [`../evaluation/LM_EVAL_TASK_QUALIFICATION_V1.md`](../evaluation/LM_EVAL_TASK_QUALIFICATION_V1.md);
- [`../evaluation/RESULT_SCHEMA_V1.md`](../evaluation/RESULT_SCHEMA_V1.md);
- [`../contracts/evaluation/eval-v1.md`](../contracts/evaluation/eval-v1.md);
- [`../../configs/evaluation/eval_v1_registry.yaml`](../../configs/evaluation/eval_v1_registry.yaml).

Document 180 binds the exact scientific dataset/environment identities, Pile cadence,
TurkishMMLU/XCOPA exclusions, full/cheap factual registries, numeric margins and the
per-training-contract checkpoint-binding rule. Any semantic change requires eval-v2.

## R3 — Pipeline productionization

Status: active. The local checkpoint planner, full 19-stage study controller, 39-node OLMo/Qwen/SmolLM matrix,
training trace, typed artifact scaffold, presentation contract, Luna micro-packets and seven-lane
M0 parallel adapters prepared; frozen bindings and all later-state execution adapters remain
blocked on R2 freeze.

- expose one validated pipeline interface for state/checkpoint evaluation;
- make manifests, resume, failure states, and output namespaces deterministic;
- normalize historical compatible evidence without rewriting raw outputs;
- generate trajectory tables and figures from normalized rows;
- add local smoke fixtures and bounded runtime estimates.

Exit condition: the same command/config family can evaluate M0, M1, M2-A, and M2-B.

Current local evidence: [`../pipeline/README.md`](../pipeline/README.md), the pipeline config under
`configs/pipelines/`, the full-study config under `configs/studies/`, the M0 entrypoint under
`scripts/study/`, the
[`three-model planning contract`](../contracts/three-model-study-matrix-v1.md), and fail-closed
planner/trace/artifact/study tests. The three scientific M0 bindings and one 24-lane family
operator are frozen. The exact standalone wave was submitted once after HU read-only identity and
30 GiB home gates passed; its authorization is consumed. Remaining work is read-only monitoring,
raw completion, complete-result normalization and figure rendering. Later-state training adapters
remain blocked without changing eval-v1 semantics.

## R4 — Corpus contract

- freeze the vngrs revision/shards, minimal quality checks, licence/provenance, held-out split,
  contamination policy, tokenizer/token budget, and `trwiki` control role;
- materialize only after a separately authorized bounded wave.

Exit condition: corpus inputs and splits are immutable and compatible with the M2 estimands.

## R5 — Training contracts

- freeze M1 model/recipe selection rules and checkpoint grid;
- freeze matched M2-A/M2-B objectives, total tokens, data order, seeds, sequence policy, and factual
  replacement mechanism;
- bind `eval-v1` without modifying it.

Exit condition: exact contracts are reviewable before any new training.

## R6 — Execution and analysis

- run separately authorized M0/M1/M2-A/M2-B waves;
- preserve raw artifacts and manifests;
- compute precommitted transfer/relearning contrasts and uncertainty;
- freeze results, figures, retention decisions, and thesis-ready evidence.

No R4–R6 step is authorized by this roadmap.
