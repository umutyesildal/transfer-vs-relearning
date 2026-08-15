# 80 - M1 Relation V2 Relation-Conditioned Evaluation Report

Last updated: 2026-07-12
Status: complete, partial improvement, gate failed

## Outcome

The relation-conditioned continuation preserves perfect exact storage and produces a small robust
improvement, but it does not pass the precommitted gate. Checkpoint 120 is selected with 500 exact,
382 direct, 376 QA, 331 overlap, and 331 triple-robust facts.

Compared with the clean Relation V2 checkpoint 250 baseline (`500/378/377/329/329`), the selected
checkpoint changes exact/direct/QA/overlap/triple by `0/+4/-1/+2/+2`. This is a partial
improvement, not a promoted M1 checkpoint.

## Canonical Run

- transfer commit: `def71ad`;
- training job: `393017`;
- starting model: clean Relation V2 job `391918`, checkpoint 250;
- examples: 1,500 over 500 facts;
- candidates per example: 16;
- optimizer updates: 150/150;
- learning rate: `5e-6`;
- runtime errors: none;
- evaluation jobs: `393018` through `393027`;
- completed views: 30/30.

## Checkpoint Curve

| Checkpoint | Exact | Direct | QA | Overlap | Triple |
|---:|---:|---:|---:|---:|---:|
| 15 | 500 | 382 | 372 | 328 | 328 |
| 30 | 500 | 378 | 377 | 329 | 329 |
| 45 | 500 | 379 | 376 | 328 | 328 |
| 60 | 500 | 376 | 378 | 329 | 329 |
| 75 | 500 | 376 | 377 | 327 | 327 |
| 90 | 500 | 380 | 376 | 331 | 331 |
| 105 | 500 | 379 | 375 | 327 | 327 |
| 120 | 500 | 382 | 376 | 331 | 331 |
| 135 | 500 | 376 | 376 | 327 | 327 |
| 150 | 500 | 374 | 374 | 326 | 326 |

Checkpoint 120 wins the frozen overlap-first selection rule. Checkpoint 90 ties its overlap/triple
count but has two fewer direct facts. Later training regresses, so the final checkpoint is not
selected.

## Relation Breakdown At Checkpoint 120

| Relation | Triple robust | Change vs clean checkpoint 250 |
|---|---:|---:|
| `profession` | 97/100 | 0 |
| `born_in` | 70/100 | 0 |
| `lives_in` | 42/100 | -1 |
| `field_of_study` | 80/100 | +1 |
| `works_in_industry` | 42/100 | +2 |

The intervention modestly helps the replacement relations, especially industry, but does not
repair city binding. Across direct and QA views, 48 subjects show a residence-to-birthplace swap
and 17 show a birthplace-to-residence swap at least once.

## Gate Decision

The frozen gate was exact/direct/QA/overlap of at least `495/400/400/350`. Checkpoint 120 passes
exact but misses direct by 18, QA by 24, and overlap by 19. It is not promoted and does not open
25,000-fact scaling.

## Interpretation

Explicit relation wording and unseen ranking paraphrases can move a few held-out decisions while
preserving storage, so the objective is not entirely neutral. However, the gains are small,
unstable across checkpoints, and partly trade direct against QA. The intervention therefore does
not solve the scale-dependent retrieval/binding problem.

The curve also argues against simply extending this run: direct and QA peak at different early
checkpoints and both decline by checkpoint 150. More updates at the same learning rate are not the
next control.

## Decision

Apply the one precommitted learning-rate control from the plan without changing prompts,
candidates, starting checkpoint, seed, epoch count, or evaluation. Lower the learning rate to
`2e-6` to test whether the small direct gain can be retained without the QA trade-off. If that
control does not pass the unchanged gate, close this continuation family and return to objective
redesign at the canonical 500-fact scale.

## Learning-Rate Control Launch

- transfer commit: `5d4aab0`;
- only controlled change: learning rate `5e-6 -> 2e-6`;
- local focused tests: 34/34 passed;
- HU focused tests: 34/34 passed;
- real-data preflight: 1,500 examples over 500 facts;
- Slurm job: `393028`;
- first observed state: `RUNNING` on `gruenau9`;
- expected runtime: approximately 5-6 minutes, safe range 4-10 minutes;
- monitoring: no sleep process is active.

Training job `393028` subsequently completed 150/150 updates without runtime errors and wrote all
ten expected checkpoints. Evaluation jobs `393029` through `393038` now cover checkpoint 15
through 150 under a separate `lr2e6` namespace. At launch, six jobs were running across
`gruenau9` and `gruenau10`, with four pending. Expected complete-wave time is approximately 12-18
minutes, with a safe 12-25 minute range. No sleep monitor is active.

## Learning-Rate Control Result

All thirty evaluation views completed. Checkpoint 150 is selected for the `2e-6` control:

| Checkpoint | Exact | Direct | QA | Overlap | Triple |
|---:|---:|---:|---:|---:|---:|
| 15 | 500 | 377 | 379 | 328 | 328 |
| 30 | 500 | 379 | 377 | 330 | 330 |
| 45 | 500 | 378 | 374 | 329 | 329 |
| 60 | 500 | 379 | 377 | 328 | 328 |
| 75 | 500 | 376 | 375 | 327 | 327 |
| 90 | 500 | 377 | 374 | 327 | 327 |
| 105 | 500 | 376 | 377 | 328 | 328 |
| 120 | 500 | 376 | 374 | 327 | 327 |
| 135 | 500 | 376 | 375 | 327 | 327 |
| 150 | 500 | 381 | 377 | 331 | 331 |

Checkpoint 150 relation-level triple counts are 97 profession, 70 born-in, 43 lives-in, 78
field-of-study, and 43 works-in-industry. Across the two held-out views, 46 subjects have at least
one residence-to-birthplace swap and 17 have at least one reverse swap.

Comparison of selected checkpoints:

| Run | Exact | Direct | QA | Overlap / triple |
|---|---:|---:|---:|---:|
| Clean V2 baseline | 500 | 378 | 377 | 329 |
| Relation-conditioned `5e-6` | 500 | 382 | 376 | 331 |
| Relation-conditioned `2e-6` | 500 | 381 | 377 | 331 |

The lower learning rate recovers the one lost QA fact but does not raise the robust ceiling. It
misses the unchanged direct/QA/overlap gate by 19/23/19 facts. The continuation family is closed:
no additional learning-rate, epoch, or seed sweep is launched. Both controlled runs are retained
as evidence that prompt augmentation plus candidate ranking can move a few decisions but does not
solve relation-conditioned retrieval. The next branch must redesign the objective at 500 facts;
full 25,000-fact scaling remains blocked.
