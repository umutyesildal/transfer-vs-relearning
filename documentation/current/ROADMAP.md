# Current roadmap

This roadmap orders work; it does not authorize external execution.

## R0 — Documentation control plane

Status: completed and validated on the local migration branch.

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

Status: unresolved; required before push/cutover, but not before local evaluation inventory.

- decide how to handle eight imported historical blobs at or above 10 MiB;
- compare full-history preservation, Git LFS migration, and rewritten-history-plus-archive routes;
- verify that local ignored outputs and scientific evidence remain preserved;
- repeat secret and reachable-blob audits before any publication.

Exit condition: the user approves one lossless-enough publication policy and its verification
evidence. This roadmap does not authorize rewriting history or removing blobs.

## R1 — Evaluation inventory

Status: next; not started by this documentation wave.

- inventory every current evaluation script, config, task, metric, denominator, output schema, and
  historical artifact shape;
- map each item to M0/M1/M2-A/M2-B and to factual access, retention, capability, or integrity;
- classify each item as reuse, repair, replace, or retire-with-history;
- identify exact parity and schema gaps.

Exit condition: a reviewed inventory with no unowned metric or evaluator.

## R2 — Evaluation qualification and freeze

- pin LM Evaluation Harness and exact task/dataset revisions;
- validate task IDs, prompts, few-shot settings, metrics, and availability;
- reconcile official WikiText word/byte PPL and BPB with custom retention evaluation;
- qualify the factual hard suite and generic degeneration panel;
- freeze normalized checkpoint rows, confidence intervals, missingness, cheap/full cadence, and
  gates;
- create `eval-v1` contract and acceptance tests.

Exit condition: semantic changes require `eval-v2`; all states use `eval-v1` unchanged.

## R3 — Pipeline productionization

- expose one validated pipeline interface for state/checkpoint evaluation;
- make manifests, resume, failure states, and output namespaces deterministic;
- normalize historical compatible evidence without rewriting raw outputs;
- generate trajectory tables and figures from normalized rows;
- add local smoke fixtures and bounded runtime estimates.

Exit condition: the same command/config family can evaluate M0, M1, M2-A, and M2-B.

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
