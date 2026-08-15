# 75 - M1 Relation V2 500-Fact Evaluation Report

Last updated: 2026-07-12

## Outcome

The clean Relation V2 500-fact run achieves perfect exact-prefix storage but narrowly misses the
precommitted prompt-robust progression gate. Checkpoint 250 is the best checkpoint at 500 exact,
378 held-out direct, 377 QA, 329 direct/QA overlap, and 329 three-view robust facts.

The gate required 450/400/400/350. Exact passes by a large margin; direct, QA, and overlap miss by
22, 23, and 21 facts respectively. The 2,500-fact scale is therefore blocked under the frozen
gate, but Relation V2 is a substantial improvement over the historical V1 500-fact run.

## Canonical Run

- synthetic-data-generation commit: `b33aa8b`;
- transfer-vs-relearning commit: `062a90a`;
- training job: `391918`;
- subjects: 100;
- facts: 500;
- train rows: 3,500;
- model: base SmolLM2-360M;
- objective: answer-only CLM;
- learning rate: `1e-4`;
- epochs: 36;
- effective batch: 500;
- optimizer updates: 252/252;
- runtime: 575.4 seconds;
- aggregate training loss: 0.6418;
- final validation loss: 0.3910;
- runtime/OOM failures: none.

## Full Checkpoint Curve

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 21 | 21 | 20 | 11 | 6 | fail |
| 50 | 79 | 62 | 66 | 42 | 25 | fail |
| 75 | 307 | 224 | 234 | 176 | 148 | fail |
| 100 | 475 | 333 | 340 | 283 | 277 | fail |
| 125 | 500 | 375 | 367 | 324 | 324 | fail |
| 150 | 500 | 371 | 369 | 320 | 320 | fail |
| 175 | 500 | 377 | 373 | 326 | 326 | fail |
| 200 | 500 | 374 | 374 | 325 | 325 | fail |
| 225 | 500 | 377 | 375 | 328 | 328 | fail |
| 250 | 500 | 378 | 377 | 329 | 329 | fail |
| 252 | 500 | 377 | 373 | 328 | 328 | fail |

Storage saturates by checkpoint 125. Prompt robustness then plateaus with a small late gain;
checkpoint 250 is selected by highest overlap, direct, and QA counts.

## Relation Results At Checkpoint 250

| Relation | Exact | Direct | QA | D/Q overlap | Triple |
| --- | ---: | ---: | ---: | ---: | ---: |
| `profession` | 100 | 97 | 100 | 97 | 97 |
| `born_in` | 100 | 81 | 78 | 70 | 70 |
| `lives_in` | 100 | 52 | 63 | 43 | 43 |
| `field_of_study` | 100 | 85 | 91 | 79 | 79 |
| `works_in_industry` | 100 | 63 | 45 | 40 | 40 |

All five relations have 100/100 exact storage. The remaining prompt-transfer difficulty is
largest for `lives_in` and `works_in_industry`. The city pair remains intentionally unchanged.

## City Binding

At checkpoint 250, 46 `lives_in` facts select the same subject's birthplace in at least one
held-out view. Seventeen `born_in` facts select the same subject's residence in at least one view.
These counts are reported as relation-binding diagnostics and do not justify removing or changing
either relation.

## Nested Ten-Subject Retention

The original nested ten subjects reach 50 exact, 37 direct, 39 QA, 32 overlap, and 32 triple at
checkpoint 250. Scaling therefore preserves all exact facts but reduces prompt robustness versus
the isolated 10-subject run, demonstrating binding interference under higher fact density.

## Historical V1 Comparison

The historical V1 500-fact checkpoint 250 reached 451 exact, 317 direct, 349 QA, and 277 overlap.
Relation V2 checkpoint 250 reaches 500, 378, 377, and 329 respectively:

```text
exact +49, direct +61, QA +28, overlap +52
```

The redesign is therefore a major controlled improvement even though the strict progression gate
remains unmet.

## Decision

- accept checkpoint 250 as the Relation V2 500-fact analysis checkpoint;
- keep all five relations unchanged, including the hard city pair;
- do not launch 2,500 facts under the current recipe because the frozen gate failed;
- preserve the perfect-storage result as evidence that acquisition capacity is not the current
  bottleneck;
- target prompt-robust extraction across `lives_in` and `works_in_industry` without modifying
  facts, candidate inventories, or relation definitions.
