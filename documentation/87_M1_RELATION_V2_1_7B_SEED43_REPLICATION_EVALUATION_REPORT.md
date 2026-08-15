# M1 Relation V2 1.7B Seed-43 Replication Evaluation Report

## Purpose

This run tests whether the near-perfect 1.7B Relation V2 result persists under an independent
training path. The train/validation files and split seed remain fixed; training seed and data-order
seed change from 42 to 43. All other data, optimization, exposure, and evaluation controls are
unchanged.

The corrected replication job was `399078`. It completed 36 epochs and 252 optimizer updates in
2,690 seconds. Final validation loss was 0.005654, compared with 0.007413 for seed 42. The loss
trajectory differed from seed 42, confirming that the data-order change produced an independent
training path.

## Checkpoint Results

| Checkpoint | Exact | Direct | QA | Overlap | Triple | Gate |
|---:|---:|---:|---:|---:|---:|:---:|
| 25 | 208 | 205 | 213 | 177 | 140 | Fail |
| 50 | 500 | 496 | 496 | 494 | 494 | Pass |
| 75 | 500 | 500 | 499 | 499 | 499 | **Pass, best** |
| 100 | 500 | 500 | 499 | 499 | 499 | Pass |
| 125 | 500 | 500 | 499 | 499 | 499 | Pass |
| 150 | 500 | 500 | 499 | 499 | 499 | Pass |
| 175 | 500 | 500 | 499 | 499 | 499 | Pass |
| 200 | 500 | 500 | 499 | 499 | 499 | Pass |
| 225 | 500 | 500 | 499 | 499 | 499 | Pass |
| 250 | 500 | 500 | 499 | 499 | 499 | Pass |
| 252 | 500 | 500 | 499 | 499 | 499 | Pass |

The first passing checkpoint is 50, matching the original seed's first gate pass. Checkpoint 75 is
selected by overlap, triple, direct, QA, and earlier-checkpoint tie-breaking. Performance remains
identical from checkpoint 75 through checkpoint 252.

## Cross-Seed Comparison

| Run | Selected checkpoint | Exact | Direct | QA | Overlap | Triple |
|---|---:|---:|---:|---:|---:|---:|
| Seed 42 | 200 | 500 | 499 | 498 | 497 | 497 |
| Seed 43/data seed 43 | 75 | 500 | 500 | 499 | 499 | 499 |
| Two-seed mean | - | 500.0 | 499.5 | 498.5 | 498.0 | 498.0 |

Both independent training paths pass the unchanged gate by large margins. Robust overlap is 99.4%
for seed 42 and 99.8% for seed 43, compared with 65.8% for the 360M reference. The conclusion that
capacity resolves nearly all of the 500-fact retrieval plateau is therefore replicated rather than
dependent on one training order.

## Remaining Error

The selected seed-43 checkpoint has one non-triple fact:

| Fact | Relation | Expected | Exact | Direct | QA-matched |
|---|---|---|---|---|---|
| `S00971_lives_in` | `lives_in` | Omaha | rank 1: Omaha | rank 1: Omaha | rank 2: predicted Gaziantep |

The same fact was one of the three failures at the selected seed-42 checkpoint. This repeatability
suggests a narrow hard prompt-binding case rather than broad stochastic instability. It does not
justify changing or removing `lives_in`.

## M1 Freeze Decision

The precommitted replication condition is satisfied.

- Canonical primary M1: seed-42 checkpoint 200.
- Independent replication M1: seed-43/data-seed-43 checkpoint 75.
- Both runs preserve exact storage and near-perfect held-out retrieval.
- The 1.7B Relation V2 500-fact M1 family is approved for freezing.
- No further M1 exposure increase is required for this 500-fact condition.

The next stage is to create immutable model manifests for both selected checkpoints and define the
M2/M3 adaptation matrix. The canonical seed-42 model should remain the primary thesis trajectory;
the seed-43 model provides the replication/control trajectory. Any decision to scale beyond 500
facts is a separate experiment and must not delay the M2/M3 transition for this validated family.

## Operational Note

All 33 evaluator outputs completed successfully. Stderr contained only non-fatal Transformers
deprecation messages. Training checkpoints and evaluation outputs remain on `/vol/tmp` and
`/vol/tmp2`; no large artifact was written back to the shared student home fileserver.

Model-only freeze job `399090` was launched on the `std` partition. It copies seed-42 checkpoint
200 and seed-43 checkpoint 75 into
`/vol/tmp/yesildau/transfer-vs-relearning/artifacts/models/m1_relation_v2_1_7b_500_frozen`, creates
local model manifests for both, and computes SHA-256 hashes for their `model.safetensors` files.
The job completed with `FREEZE_COMPLETE` and empty stderr. Both frozen directories contain
`model.safetensors` (3,422,777,952 bytes), config files, a local model manifest, and a SHA-256 file.
The selected M1 artifacts are therefore frozen and independently identifiable. No continuing sleep
process is active.
