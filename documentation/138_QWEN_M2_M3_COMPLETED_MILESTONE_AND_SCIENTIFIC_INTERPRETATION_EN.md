# 138 - Qwen M2/M3 Completed Milestone and Scientific Interpretation

**Date:** 2026-08-03  
**Language:** English master version  
**Status:** Completed milestone synthesis; no new experiment authorized  
**Scope:** The completed 2,500-fact Qwen M2-clean/M3-fact family and its frozen primary result

## 1. Purpose

This document records the scientific milestone reached after the complete Qwen M2/M3 endpoint
evaluation. It consolidates the current conclusion without replacing the chronological execution
record, failed-attempt ledger, manifests, or aggregate result package.

The detailed evidence remains in:

- Document 127 for the replicated English M1 selection and frozen starting artifacts;
- Documents 132--133 for the pre-M2 readiness and frozen execution plan;
- Document 134 for the completed bilingual M1 baseline and generic-PPL package;
- Document 135 for the frozen M2/M3 contract, materialization, smoke, and principal training;
- Document 136 for the complete endpoint evaluation, aggregation, hashes, and frozen gate;
- Document 137 for the independent external-review handoff.

This milestone is deliberately independent of any future supervisor feedback. Feedback-dependent
extensions, amendments, or new experiment families must be documented separately after they are
explicitly approved.

## 2. Milestone reached

The project has completed its first controlled intermediate-scale test of transfer versus factual
re-exposure using the newly selected Qwen M1 artifacts. The completed sibling chains are:

```text
Qwen M1 seed 42, selected step 75 -> M2-clean seed 42 and M3-fact seed 42
Qwen M1 seed 43, selected step 50 -> M2-clean seed 43 and M3-fact seed 43
```

Both downstream arms in a seed chain were initialized independently from the same frozen M1
artifact. M3-fact was not initialized from M2-clean. The experiment therefore preserves the
required sibling-arm causal structure.

There are no remaining pre-M2/M3 readiness tasks. Registry preparation, bilingual baselines,
generic PPL, contract freeze, matched-input materialization, smoke and resume checks, principal
training, fixed-endpoint evaluation, strict assembly, bootstrap analysis, and frozen gate
application are complete.

## 3. Frozen experimental contract

The completed family used:

- 500 subjects and 2,500 synthetic facts;
- 250 Branch A and 250 Branch B subjects;
- five relations per subject;
- no target synthetic factual binding in M2-clean;
- correct Turkish factual exposure only for the 1,250 Branch B facts in M3-fact;
- four complete cycles over those 1,250 facts, giving 5,000 factual exposures;
- zero Turkish factual exposure for Branch A;
- 512-token pretokenized blocks;
- 2,048 training blocks and 1,048,576 training tokens per arm;
- 128 optimizer updates per arm;
- matched optimizer, scheduler, batch decomposition, data seed, and endpoint rules;
- fixed endpoint `checkpoint-128`;
- 24 bilingual evaluation slices and 60,000 probes per state;
- 2,000 subject-bootstrap samples with seed `20260717`.

The primary outcome was TR-to-EN candidate-ranking top-1 accuracy. The primary causal estimand was
the Branch difference-in-differences:

```text
(M3-fact - M2-clean) for Branch B
minus
(M3-fact - M2-clean) for Branch A
```

The precommitted primary success criterion required a positive observed interaction and a 95%
bootstrap confidence-interval lower bound above zero in both independent seeds. The EN-to-EN
retention guardrail allowed no seed/arm decline worse than five percentage points relative to its
corresponding frozen M1 state.

## 4. Execution completeness and integrity

All four principal training runs completed 128 updates and produced their required endpoint.
Endpoint evaluation ultimately produced all 96 required M2/M3 slices, each with 2,500 probes.
Together with the two frozen M1 anchors, the final analysis contains six states with 60,000 probes
per state.

The original M3 seed-43 tasks 83--95 failed before evaluator execution because the HU checkout
changed while pending tasks still enforced the previous expected-commit guard. These failures were
correctly retained as infrastructure evidence and were not counted as scientific results. A
bounded retry evaluated only the 13 missing registry slices under a synchronized commit and did
not overwrite the existing 83 valid results.

Strict assembly verified registry membership, completion markers, row counts, metadata, probe
uniqueness, and slice hashes. The final analysis manifest reports `completed`, and the integrity
summary reports `passed`.

## 5. Headline state results

Top-1 accuracies at the frozen endpoint were:

| State | EN-to-EN | TR-to-EN | TR-to-TR |
|---|---:|---:|---:|
| M1 seed 42 | 99.29% | 52.03% | 29.05% |
| M2-clean seed 42 | 98.05% | 33.29% | 22.46% |
| M3-fact seed 42 | 98.22% | 35.14% | 24.04% |
| M1 seed 43 | 99.24% | 52.52% | 30.12% |
| M2-clean seed 43 | 96.24% | 33.70% | 23.25% |
| M3-fact seed 43 | 96.95% | 35.59% | 24.97% |

Relative to M1, clean Turkish adaptation caused a large decline in Turkish-prompt factual access
under the current intervention. M3-fact remained below M1 but consistently outperformed its
matched M2-clean sibling:

| Seed | M3-fact minus M2-clean, global | EN-to-EN | TR-to-EN | TR-to-TR |
|---|---:|---:|---:|---:|
| 42 | +1.20 pp | +0.17 pp | +1.86 pp | +1.58 pp |
| 43 | +1.44 pp | +0.70 pp | +1.89 pp | +1.72 pp |

These paired arm differences show a small and consistent descriptive benefit from the M3-fact
condition. They do not alone establish that the benefit was caused specifically by the controlled
Branch B factual exposure, because generic arm differences may also affect Branch A.

## 6. Frozen primary gate result

The primary TR-to-EN Branch interaction was:

| Seed | Observed interaction | 95% bootstrap CI | Frozen seed result |
|---|---:|---:|---|
| 42 | `0.0025` (+0.25 pp) | `[-0.0051, 0.0101]` | fail; interval crosses zero |
| 43 | `0.0135` (+1.35 pp) | `[0.0051, 0.0218]` | pass |

Operational validity passed. The EN-to-EN retention guardrail passed; the worst seed/arm decline
was seed-43 M2-clean versus M1 at -3.00 percentage points, inside the frozen -5-point limit.

The overall frozen decision is therefore:

```text
primary_success_criterion_not_met
```

This is a valid negative or inconclusive primary result, not a failed run. The family was complete,
the frozen evaluation and retention gates were applied correctly according to the recorded
contract, and one seed produced a positive interaction. The required two-seed replication of that
interaction was not obtained.

## 7. Scientific interpretation

The most defensible current interpretation is:

> Under the frozen 2,500-fact Qwen contract, clean Turkish adaptation did not improve access to the
> English-acquired synthetic facts and instead produced substantial Turkish-prompt retrieval loss.
> Matched Turkish factual re-exposure produced a small descriptive recovery relative to clean
> adaptation in both seeds, but the Branch-B-specific primary causal interaction was not replicated
> under the precommitted two-seed confidence criterion.

The result supports several narrower conclusions:

1. The replicated English M1 state was sufficient to run an operationally valid causal family.
2. Generic Turkish adaptation and factual-access preservation were not equivalent in this setup.
3. Correct factual re-exposure was associated with modestly higher endpoint performance than the
   matched clean condition.
4. The evidence is insufficient to claim a replicated Branch-B-specific factual-relearning effect.
5. A positive M3-minus-M2 point estimate must not be described as a passed primary causal result.

## 8. Claims that are not authorized

The completed evidence does not authorize claiming that:

- the primary transfer-versus-relearning hypothesis passed;
- Turkish adaptation opened factual access relative to M1;
- the seed-43 interaction alone is a replicated treatment effect;
- another checkpoint would have passed the frozen family;
- a third seed, larger factual dose, or relaxed confidence rule would rescue the original gate;
- the optional M3-lexical arm was part of this completed family;
- the separate 25,000-fact M1 scale branch is required to validate this completed result.

Any analysis beyond the frozen primary package must be explicitly labeled secondary or
post-hoc/exploratory. Any new training family must be treated as a separately approved amendment,
with its own frozen rationale, contract, endpoints, and decision rules.

## 9. Current project state

The completed family is ready for independent read-only review, deeper exploratory interpretation,
final documentation, and artifact-lifecycle closure. It is not waiting for another prerequisite
training or evaluation job. No automatic retraining, third seed, checkpoint search, dose change,
M3-lexical run, or 25,000-fact execution follows from this result.

The actions that can proceed independently of future supervisor feedback are frozen separately in
Document 139.
