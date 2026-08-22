# M1 model provenance reconciliation — historical evidence versus new baseline

**Date:** 2026-08-22  
**Status:** read-only memo; no model acquisition  
**Gate:** `blocked_by_source_model_provenance`  
**Training/evaluation:** not run

## Scope

This memo reconciles identities already present in the repository. It does not download weights,
read HU roots, hash large artifacts or promote a primary model. Historical negative results remain
valid evidence, but they are not silently converted into a new matched M1 training contract.

## Current role and evidence table

| Model | Frozen identity | Existing local evidence | 151ab status | Safe interpretation |
|---|---|---|---|---|
| OLMo-2-0425-1B | `allenai/OLMo-2-0425-1B`, revision `a1847dff35000b4271fa70afc5db10fd29fedbdf` | M0 candidate and historical M1/dose-Pareto negative results with compact manifest hashes in Document 158/160 | `M1_NOT_ACQUIRED_OR_NOT_FROZEN` for the new baseline | provenance-first candidate; not “zero Turkish exposure” |
| Falcon-RW-1B | `tiiuae/falcon-rw-1b`, revision `e4b9872bb803165eb22f0a867d4e6a64d34fce19` | M0 candidate and historical M1 results; Falcon dose family remains incomplete at three cheap checkpoints | `M1_NOT_ACQUIRED_OR_NOT_FROZEN` for the new baseline | English comparator; model-card language is not mathematical zero exposure |
| Qwen2.5-1.5B | `Qwen/Qwen2.5-1.5B`, revision `8faed761d45a263340a0528343f099c05c9a4323` | two frozen historical M1 selected manifests: seed-42 step-75 and seed-43 step-50 | frozen positive-control chain, subject to manifest review | multilingual/Turkish positive control; never “Turkish unseen” |
| Pythia-1.4B | `EleutherAI/pythia-1.4b`, revision `0da31d8fb309463877ed8c40e54a8f911dced3ec` | official tokenizer repair and valid negative result preserved in Documents 156–158/old v3 configs | not in 151ab frozen execution set | historical provenance evidence; no response-dependent re-insertion |

## What is actually frozen locally

- Candidate model IDs and requested revisions are present in historical configs.
- Qwen’s two selected historical manifest hashes are explicit in the trajectory inventory config.
- OLMo/Falcon/Pythia historical training/evaluation results and their negative classifications are
  preserved in numbered documents; no result is deleted or rewritten.
- The trajectory table records model revision and checkpoint hash as required future fields.

## What is not yet closed for a new M1 contract

The new 151ab baseline still requires, per model and state:

```text
model artifact manifest SHA-256
tokenizer artifact manifest SHA-256
repository metadata identity/hash
architecture and runtime compatibility
license and training-stage identity
exact checkpoint identity for M0/M1
truthful Turkish-exposure label
```

The historical OLMo/Falcon runs cannot fill those fields automatically because they belong to an
older screen/recipe boundary. The existence of a Qwen M1 checkpoint does not make OLMo/Falcon
matched or make Qwen a clean unseen-Turkish candidate.

## Reconciliation rules

1. Preserve historical runs as historical evidence; do not rerun or relabel them in this memo.
2. Treat Qwen’s existing M1 manifests as a positive-control input candidate only after exact
   artifact/tokenizer manifest review.
3. Treat OLMo and Falcon as candidates that need a separate immutable input inventory; missing
   artifacts remain `blocked_by_source_model_provenance`, not an invitation to download silently.
4. Keep Pythia outside the 151ab execution set unless a new measurement decision explicitly adds it.
5. Do not choose a primary model from historical outcomes. Selection must be predeclared before a
   new matched M1 run.

## Decision

The provenance blocker remains open, but its remaining work is now explicit: perform a bounded
local artifact/metadata inventory for the 151ab role set, reconcile each manifest and tokenizer
identity, and record missing fields without acquisition. No training contract can be issued until
that inventory and the measurement-design review pass.
