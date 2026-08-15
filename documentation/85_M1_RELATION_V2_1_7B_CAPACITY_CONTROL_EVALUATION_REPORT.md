# M1 Relation V2 1.7B Capacity-Control Evaluation Report

## Question

Does increasing only model capacity from SmolLM2-360M to SmolLM2-1.7B resolve the Relation V2
500-fact retrieval plateau when data, objective, exposure, optimization, and evaluators remain
unchanged?

## Controlled Setup

- 100 subjects, 500 independently assigned facts, five relations;
- seven acquisition rows per fact, 3,500 rows total;
- answer-only causal language-model objective;
- learning rate `1e-4`, 36 epochs, effective batch 500, 252 optimizer updates;
- identical exact-prefix, held-out direct, and QA-matched candidate-ranking probes;
- unchanged gate: exact >= 450, direct >= 400, QA >= 400, overlap >= 350;
- only scientific change: SmolLM2-360M -> SmolLM2-1.7B.

The successful training job was `393056` on `gruenau9`. It completed in 2,827 seconds. The prior
jobs interrupted by maintenance, storage saturation, or an orphan GPU process are infrastructure
failures and are not scientific observations.

## Checkpoint Results

`overlap` is the intersection of direct and QA rank-1 successes. `triple` additionally requires
exact-prefix rank 1.

| Checkpoint | Exact | Direct | QA | Overlap | Triple | Gate |
|---:|---:|---:|---:|---:|---:|:---:|
| 25 | 212 | 192 | 204 | 159 | 128 | Fail |
| 50 | 499 | 495 | 494 | 490 | 489 | Pass |
| 75 | 500 | 498 | 497 | 496 | 496 | Pass |
| 100 | 500 | 498 | 497 | 496 | 496 | Pass |
| 125 | 500 | 498 | 497 | 496 | 496 | Pass |
| 150 | 500 | 499 | 497 | 496 | 496 | Pass |
| 175 | 500 | 498 | 497 | 496 | 496 | Pass |
| 200 | 500 | 499 | 498 | 497 | 497 | **Pass, best** |
| 225 | 500 | 498 | 498 | 497 | 497 | Pass |
| 250 | 500 | 499 | 498 | 497 | 497 | Pass |
| 252 | 500 | 499 | 498 | 497 | 497 | Pass |

The first passing checkpoint is 50. Performance is already near saturation at checkpoint 75 and
remains stable through the end. Checkpoint 200 is selected by the predeclared ordering of overlap,
triple, direct, QA, and earlier checkpoint.

## Capacity Comparison

The clean 360M Relation V2 checkpoint-250 reference was:

| Model | Exact | Direct | QA | Overlap |
|---|---:|---:|---:|---:|
| SmolLM2-360M | 500 | 378 | 377 | 329 |
| SmolLM2-1.7B, checkpoint 200 | 500 | 499 | 498 | 497 |
| Absolute change | 0 | +121 | +121 | +168 |

Exact storage was already saturated in the 360M model. The 1.7B model therefore does not improve
the conclusion that the facts can be stored; it almost completely closes the gap between exact
storage and retrieval under held-out direct and QA prompts. Robust overlap rises from 65.8% to
99.4%.

This is strong evidence that the 360M plateau was primarily capacity-limited binding and access,
not a fundamental failure of the Relation V2 data format or answer-only acquisition objective.
The result does not prove that every future scale or M2/M3 condition will remain solved.

## Remaining Errors At Checkpoint 200

All three non-triple facts belong to `lives_in`; exact-prefix retrieval is correct for all three.

| Fact | Expected | Direct | QA-matched |
|---|---|---|---|
| `S00971_lives_in` | Omaha | rank 1: Omaha | rank 2: predicted Gaziantep |
| `S01052_lives_in` | Van | rank 1: Van | rank 2: predicted Indianapolis |
| `S02139_lives_in` | Tekirdag | rank 2: predicted Istanbul | rank 1: Tekirdag |

These are prompt-view-specific city-relation access errors rather than storage failures. They do
not justify removing `lives_in`; the relation is scientifically important and reaches 97/100 robust
success at minimum under the aggregate result implied by the three failures.

## Decision

The full precommitted gate passes decisively. Per the capacity-control plan, the next required
scientific action is a second-seed replication of the selected 1.7B recipe before freezing M1 for
M2/M3. Scaling the number of facts should not precede that replication.

The storage incident does not alter this scientific result. All successful training checkpoints
and the 33 evaluator outputs reside on approved scratch storage rather than the shared student home
fileserver.
