# M1 one-command evaluation orchestration

**Date:** 2026-08-22
**Status:** local implementation/preparation only; execution not authorized
**Scope:** M1 eval-v2 after a frozen M1 training/checkpoint input

## Answer

Yes. M1 can be operated as one command, but it must be a controller rather than a single opaque
model-evaluation process. The controller fans out one checkpoint lane for the M0 parent and every
M1 epoch-end snapshot, keeps the complete inherited eval-v2 bundle plus the mandatory 500-probe
exact-prefix supplement in each lane, waits at a normalization barrier, and then builds the
presentation bundle. The checkpoint lanes are independent after the training manifest is closed and
can therefore run in parallel, subject to a bounded concurrency limit.

The local entrypoint is:

```bash
PYTHONPATH=src python3 scripts/study/run_m1_eval.py \
  --config <frozen-m1-eval-config.yaml> \
  --project-state documentation/current/PROJECT_STATE.yaml \
  --execute
```

The current draft must be inspected without `--execute`:

```bash
PYTHONPATH=src python3 scripts/study/run_m1_eval.py \
  --config configs/pipelines/eval_v1_olmo_epoch_trajectory_template.yaml
```

That invocation is a plan/preflight only and is expected to exit non-zero while the M1 contract is
unfrozen. It does not call LM Eval, load weights, use HU/SSH, submit Slurm, or create an output root.

## Fixed scientific contents

- eval-v2 remains the single M0/M1/M2 contract.
- TurBLiMP is inherited from the M0 `juletxara/turblimp` route and its pinned revision.
- All active M0 eval-v2 families remain mandatory for M1.
- Pile-10k is retired and cannot re-enter the M1 bundle.
- Project-native factual Forms A–D, robust intersections, relation controls, generation integrity,
  and exact-prefix are retained.
- Turkish held-out retention and the frozen `trwiki-20260601` cross-domain control are explicit
  lanes; they are not silently replaced by English PPL.
- Exact-prefix is explicit: 500 frozen probes at the parent and every required M1 checkpoint.
- M1 trains on the hash-closed synthetic English fact dataset. vngrs is reserved for the later
  matched M2-A/M2-B Turkish sibling arms; `trwiki-20260601` remains cross-domain control.

## Runtime barriers

1. Hash-closed synthetic-fact dataset, M1 training and M1 checkpoint manifests.
2. Per-checkpoint eval lanes in parallel, with bounded GPU concurrency.
3. Canonical normalization only after every required lane has an explicit complete/failed row.
4. Presentation builder after normalization; raw namespaces remain immutable.

Max’s request is covered by the mandatory checkpoint registry and training trace: each row carries
fact exposures, retention, token and batch statistics, hyperparameters, checkpoint identity and
raw-artifact hashes. The presentation builder then derives the fact-access/retention trajectory
tables and plots without copying numbers by hand.

## Why it cannot start now

The project currently has `ready_to_measure=true` but `ready_to_train=false`; no hash-bound
synthetic-fact dataset, M1 checkpoint/training manifest or M1 execution adapter/contract is
available. Starting now would either score the wrong model state or silently turn missing dataset
provenance into a scientific result. The controller therefore reports the blockers and exits
before any external work. vngrs is intentionally not one of the M1 blockers; it is opened only by
the later M2 sibling contract.
