# 73 - M1 Relation V2 City Hard-Negative Evaluation Report

Last updated: 2026-07-12

## Outcome

Failed neutrally. The city-only hard-negative continuation changed none of the measured retrieval
counts at any saved checkpoint. All nine checkpoints reproduced the unmodified Relation V2
checkpoint-125 result exactly: 50 exact, 45 direct, 46 QA, 45 direct/QA overlap, and 45 triple.

`born_in` remains 10/10 triple robust, `lives_in` remains 5/10, and the same four residence facts
select the subject's birthplace. The continuation neither repaired nor damaged binding and is
not carried into scale-up.

## Canonical Run

- implementation commit: `b402719`;
- starting model: unmodified Relation V2 checkpoint 125 from job `391106`;
- training job: `391903`;
- examples: 140 over twenty city facts;
- relation balance: 70 `born_in`, 70 `lives_in`;
- candidate pair: correct city versus same-subject other-relation city;
- learning rate: `5e-6`;
- epochs: 1;
- optimizer updates: 35;
- runtime errors: none;
- evaluation jobs: `391906` through `391914`;
- completed evaluation views: 27/27.

## Results

Every checkpoint from 4 through 35 produced the same table:

| Metric | Result |
| --- | ---: |
| global exact | 50/50 |
| global direct | 45/50 |
| global QA | 46/50 |
| global direct/QA overlap | 45/50 |
| global triple | 45/50 |
| `born_in` triple | 10/10 |
| `lives_in` exact/direct/QA/overlap/triple | 10/5/6/5/5 |
| unique residence-to-birthplace swaps | 4 |
| reverse birthplace-to-residence swaps | 0 |

No checkpoint passed the precommitted 8/10 `lives_in` gate.

## Interpretation

The ranking loss was already very small, approximately 0.011-0.022, indicating that on the
training prompts the correct city generally outranked the paired city before continuation. The
held-out failures therefore concern prompt transfer, not an unlearned pairwise distinction on
seen prompts. A gentle 35-step continuation does not move that boundary.

## Decision

Keep `born_in` and `lives_in` permanently and keep their shared city candidate inventory. Reject
this continuation checkpoint as unnecessary. Proceed to 100 subjects / 500 facts using the clean
unmodified Relation V2 direct-aware CLM recipe. Continue reporting city-swap metrics as a hard
binding diagnostic rather than redesigning or removing either relation.
