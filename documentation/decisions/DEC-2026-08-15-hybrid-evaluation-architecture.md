# Hybrid evaluation architecture

**Status:** accepted | **Date:** 2026-08-15

## Context

Documents 177 and 178 require standard LM Evaluation Harness tasks, project-specific bilingual
factual access, longitudinal checkpoints and stable M0/M1/M2-A/M2-B comparisons. The repository
already has scientifically useful factual, robustness, bootstrap and degeneration evaluators, but
its custom block PPL is not equivalent to canonical rolling WikiText evaluation.

## Decision

Use three independent execution lanes and one normalization layer:

1. pinned LM Evaluation Harness for public retention and capability tasks;
2. project-native evaluators for factual causal estimands and generation integrity;
3. an immutable manifest lane for checkpoint/training identity;
4. a typed long-form normalizer that joins results without rescoring them.

Official WikiText BPB is primary English retention; word and byte PPL are always reported.
Project factual ranking keeps mean answer-token log probability as primary and total log
probability as sensitivity. No cross-family universal score is created.

Dense evaluation covers every precommitted checkpoint. Full factual and capability evaluation uses
state entry, midpoint and endpoint. Exact task and numerical gates remain in the eval-v1 contract
and must be frozen before execution.

## Rationale

- Standard tasks stay comparable to upstream implementations.
- Existing factual semantics, candidate inventories and robust controls are preserved.
- Long-form output prevents schema growth from turning into another large ad hoc table.
- A generated one-row-per-checkpoint view remains easy for Max and thesis figures.
- Task updates or semantic changes are visible and versioned rather than silently absorbed.

## Consequences

The harness is installed in a dedicated locked environment, not as an unpinned project dependency.
Raw harness and project outputs stay immutable outside Git; Git stores configs, schemas, small
manifests and tests. Historical token-PPL thresholds do not automatically become BPB thresholds.

The accepted architecture does not mean eval-v1 is frozen or authorize any evaluation.
