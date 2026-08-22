# Current project status

**As of:** 2026-08-22

**Current branch:** `agent/m1-pipeline-repair`

**Execution state:** local repair only; M1 has not started

## The short answer

M0 is finished. The project is now preparing the matched three-model M1 wave, but training and
evaluation remain disabled until the user reviews and explicitly authorizes the final hash-bound
M1 contract.

The recent stall was a control-plane error, not a scientific-design failure: the prospective M1
evaluator required checkpoint and training manifests before training, even though training is the
stage that creates those manifests. The repair makes them dependency outputs and keeps standalone
post-training evaluation fail-closed unless the real files and hashes exist.

## Closed M0 boundary

- active protocol: frozen `eval-v2`;
- Pile-10k: retired prospectively and absent from every active lane, gate and denominator;
- OLMo, Qwen and SmolLM: 21/21 active non-Pile M0 lanes available;
- exact-prefix: complete for all three models, 500 probes per model;
- source projection: 24/24 hash-verified references in v1b;
- canonical normalization: complete in v1f with 42 metric observations;
- rescoring or another M0 recovery: not required.

The v1b projection itself contains references rather than metric rows. The canonical observations
were written later by the separately authorized v1f normalizer. Both statements are true and no
longer treated as contradictory.

## Fixed M1 scientific design

M1 is a fresh matched comparison across exactly OLMo-2-0425-1B, Qwen2.5-1.5B and SmolLM2-1.7B at
their frozen M0 revisions.

All three use the same tracked Relation V2 release: 100 subjects, 500 facts, 3,500 training rows,
seed 42, 36 epochs, 252 updates and effective batch 500. Model-specific microbatch/accumulation
decompositions are allowed only where the effective recipe remains identical.

Every run must save the parent plus every epoch-end model state, producing 37 states per model and
111 states in total. The trace records loss, learning rate, gradient norm, token counts, fact
exposures, optimizer/update counts, storage checks, hyperparameters and immutable snapshot hashes.
This is the source for Max's fact-access/retention-over-epochs table.

## Fixed M1 evaluation policy

M1 inherits the active M0 `eval-v2` protocol. Exact-prefix is mandatory rather than optional.
Dense evaluation at parent and every epoch includes factual access, 500-probe exact-prefix,
WikiText English retention, Turkish retention control and cheap generation-integrity signals.
Full evaluation at entry, midpoint and endpoint adds the full factual suite, BLiMP, HellaSwag,
WinoGender, TurBLiMP and the full integrity panel.

```text
three identity/storage preflights
  → three independent M1 trainings with epoch traces
  → hash-close training/checkpoint manifests
  → checkpoint evaluations
  → canonical normalization
  → trajectory and presentation bundle
```

## Readiness is stage-specific

| Gate | Current state |
|---|---|
| M0 | complete |
| M1 scientific inputs/recipe | ready locally |
| M1 training adapter/contract | frozen locally; awaiting exact user authorization |
| M1 checkpoint evaluation adapter/contract | next implementation boundary |
| M1 execution authorization | absent; user must explicitly provide it later |
| M2 corpus and sibling contract | not frozen; does not block M1 preparation |

`vngrs-ai/vngrs-web-corpus` is reserved for the later M2-A/M2-B Turkish adaptation arms. It is not
an M1 training input. `trwiki-20260601` remains the Turkish cross-domain control.

## Current safety boundary

This branch may change local code, configs, documentation and offline tests because the user asked
for the repair. It may not connect to HU, submit Slurm, load/train models, score evaluations,
materialize corpora, push, merge, delete artifacts or reuse an old authorization.

The next legitimate handoff is a locally tested M1 adapter plus a reviewable, execution-disabled
contract/config pair. Only after the user says to start will a separate exact authorization be
consumed.

## Read next

- agent entry: [`START_HERE.md`](START_HERE.md)
- small machine projection: [`AGENT_BRIEF.yaml`](AGENT_BRIEF.yaml)
- ordered work: [`ROADMAP.md`](ROADMAP.md)
- measurement contract: [`../contracts/evaluation/eval-v2.md`](../contracts/evaluation/eval-v2.md)
- pipeline interface: [`../pipeline/README.md`](../pipeline/README.md)

Historical numbered documents and the earlier M0 failure/recovery records remain preserved. They
are evidence, not the default source of current status.
