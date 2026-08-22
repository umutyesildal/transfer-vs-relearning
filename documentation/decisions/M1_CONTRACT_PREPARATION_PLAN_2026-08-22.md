# M1 contract preparation plan — post-M0 normalization boundary

**Date:** 2026-08-22  
**Status:** planning only; no executable M1 contract  
**Training/evaluation authorized:** no  
**Current gate:** `blocked_by_measurement_design`

## Why this is a preparation plan, not a training contract

M0 is now operationally closed: eval-v2 source evidence is hash-closed, the v1c source audit
passed 24/24 bindings and 42/42 observations, and v1f wrote the canonical normalized table.
However, the current scientific gate still records `ready_to_train=false` with unresolved
`blocked_by_benchmark_registry` and `blocked_by_source_model_provenance` contributors. The
project instructions prohibit creating a later execution contract or claiming training readiness
until those evidence gaps and the measurement-design gate are closed. This document therefore
freezes the preparation order and the intended M1 data/evaluation shape without opening HU, Slurm,
training, scoring, corpus materialization or model downloads.

## Intended M1 estimand and model roles

M1 is the English factual-acquisition state:

```text
M0 base model → M1 + English synthetic factual acquisition
```

The current evidence supports roles, not a selected primary model:

- OLMo-2-0425-1B, Pythia-1.4B and Falcon-RW-1B are the provenance-first English-centric
  candidates identified by Documents 145, 147 and 151.
- Qwen2.5-1.5B remains a multilingual positive control with retained two-seed M1 evidence.
- SmolLM2 remains a preserved negative/control family; it is not silently promoted to a new main
  optimization branch.

No candidate is selected until the frozen provenance, tokenizer, capability and M1-usability
decision table is complete. “English-only” and “Turkish unseen” remain distinct evidence labels;
the latter is not inferred from absence of a model-card statement.

## Measurement package to carry into M1

The frozen eval-v2 contract remains the only M1 evaluation protocol:

- WikiText raw BPB is primary English retention; word/byte PPL and PPL ratio are companions.
- BLiMP and HellaSwag are capability/retention gates; WinoGender is diagnostic.
- Turkish capability and held-out Turkish PPL are the adaptation manipulation check.
- Project-native factual access includes robust Forms A–D, top-1 and relation controls.
- Historical exact-prefix is mandatory at M1 and is candidate-ranking evidence, not free generation.
- Generation integrity remains part of the cheap/full evaluation bundle.
- Pile-10k is retired and cannot re-enter M1.

## Epoch-by-epoch fact-access/retention table

The generated review view must use the existing schema in
`documentation/evaluation/M1_TRAJECTORY_TABLE_V1.md`, with one row per
`model × seed × checkpoint` and explicit missingness. For a prospective matched M1 run:

- checkpoint zero is the frozen M0 parent;
- a model-only snapshot is retained at every epoch end;
- cheap factual access, WikiText BPB/PPL and cheap integrity run at every epoch end;
- exact-prefix is required at every frozen M1 checkpoint;
- the full bundle runs at entry, the precommitted midpoint and endpoint;
- the trace records actual cumulative examples, supervised/total tokens, fact exposures, global
  update, epoch, effective batch, sequence length, learning rate, gradient accumulation and
  checkpoint hash;
- missing historical checkpoints are `not_observed_historically`, never interpolated or zero-filled.

The primary plot is raw BPB and `delta_bpb` against cumulative fact exposure. The visual
`retention_score = 100 / byte_perplexity_ratio` remains presentation-only and cannot replace raw
retention values.

## Required blocker-closure order

1. **Benchmark registry:** complete field-level TurBLiMP/Turkish capability registry, task
   definition, chance/floor-ceiling, overlap procedure, and base-model compatibility.
2. **Source-model provenance:** complete exact model/revision/tokenizer/license/training-stage
   rows for every candidate and assign truthful Turkish-evidence labels.
3. **Measurement design:** freeze capability definitions, contamination/overlap rules, thresholds,
   held-out Turkish split identity and the M1 decision table without looking at new M1 outcomes.
4. **Corpus decision:** compare paper-backed Turkish candidates, retain `trwiki-20260601` as the
   cross-domain control, and select/materialize only one primary corpus after license, revision,
   dedup, PII and synthetic-fact overlap evidence is complete.
5. **Recipe freeze:** bind exact per-model M1 recipes, effective batch, sequence length, optimizer,
   LR/schedule, seed, total tokens/updates, checkpoint cadence and storage budget. No historical
   recipe is substituted silently.
6. **Executable contract:** only after 1–5 pass, create a new SHA-bound M1 contract/config with
   `execution_authorized: false`, run local/HU preflight, and request separate user authorization.

## Explicit non-actions in this phase

- no model or corpus download/materialization;
- no HU/SSH, Slurm, GPU, training or scoring;
- no M1/M2 execution contract;
- no primary-model promotion;
- no cleanup or deletion;
- no changes to the completed M0 roots.

The next safe implementation task is a read-only blocker-resolution packet for items 1–3. Once
that packet is complete, this plan can be converted into a fully bound M1 execution contract
without changing the M0 evaluation protocol or losing historical evidence.

## User-confirmed design update (2026-08-22)

The user has now fixed the following design inputs for the future contract:

- M1 inherits the exact M0/eval-v2 TurBLiMP route (`juletxra/turblimp`, revision
  `cce94ca73ac04a0fabd9fbd7a56068261e6348ad`);
- every active M0 eval-v2 metric/task family is mandatory in M1;
- Pile-10k remains retired and is not reintroduced by the phrase “all M0 evals”;
- `vngrs-ai/vngrs-web-corpus` is the primary Turkish adaptation-corpus design choice;
- `trwiki-20260601` remains cross-domain control only.

These choices narrow the future contract but do not close the remaining manifest, split, license,
overlap, model-provenance or measurement-review gates. Corpus materialization and M1 training
remain separately unauthorized until those inputs are hash-bound.

## Append-only corpus correction (2026-08-22)

The later user clarification supersedes the final vngrs bullet above for the current execution
order. M1 is the English synthetic-fact acquisition state and therefore binds the tracked
synthetic-fact release, not vngrs. `vngrs-ai/vngrs-web-corpus` is reserved for the shared Turkish
adaptation input of the later matched M2-A/M2-B sibling arms. The original preparation record is
preserved; the current boundary is recorded in
`documentation/decisions/M1_DESIGN_REALIGNMENT_VNGRS_TO_M2_2026-08-22.md`.
