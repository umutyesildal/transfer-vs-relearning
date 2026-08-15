# 82 - M1 Relation V2 Prompt-Consistency Evaluation Report

Last updated: 2026-07-13
Status: complete, gate failed, objective closed

## Outcome

The prompt-consistency objective preserves perfect exact storage and reaches the strongest robust
count observed in the continuation family, but the gain is too small to pass the precommitted
gate. Checkpoint 90 is selected with 500 exact, 383 direct, 376 QA, 332 overlap, and 332 triple
facts.

Compared with clean Relation V2 checkpoint 250 (`500/378/377/329/329`), the change is
`0/+5/-1/+3/+3`. Compared with the previous best continuation result of 331 robust facts, the
improvement is one fact.

## Canonical Run

- transfer commit: `b1ffaed`;
- training job: `393039`;
- base: clean job `391918`, checkpoint 250;
- objective: candidate CE plus prompt-distribution consistency;
- data: 500 six-prompt fact groups, 3,000 prompt instances;
- candidates: sixteen per group in identical order;
- updates: 150/150;
- evaluation jobs: `393041` through `393050`;
- completed views: 30/30;
- runtime errors: none.

## Checkpoint Curve

| Checkpoint | Exact | Direct | QA | Overlap | Triple |
|---:|---:|---:|---:|---:|---:|
| 15 | 500 | 371 | 376 | 324 | 324 |
| 30 | 500 | 379 | 378 | 329 | 329 |
| 45 | 500 | 375 | 377 | 325 | 325 |
| 60 | 500 | 380 | 376 | 330 | 330 |
| 75 | 500 | 380 | 376 | 329 | 329 |
| 90 | 500 | 383 | 376 | 332 | 332 |
| 105 | 500 | 378 | 376 | 328 | 328 |
| 120 | 500 | 376 | 375 | 326 | 326 |
| 135 | 500 | 383 | 373 | 327 | 327 |
| 150 | 500 | 381 | 378 | 331 | 331 |

The curve is non-monotonic. Later optimization does not reliably increase overlap, and direct
improvements continue to trade against QA.

## Relation Breakdown At Checkpoint 90

| Relation | Triple robust | Change vs clean checkpoint 250 |
|---|---:|---:|
| `profession` | 97/100 | 0 |
| `born_in` | 71/100 | +1 |
| `lives_in` | 44/100 | +1 |
| `field_of_study` | 80/100 | +1 |
| `works_in_industry` | 40/100 | 0 |

Across direct and QA views, 46 subjects have at least one residence-to-birthplace swap and 16
have at least one reverse swap. City binding improves slightly but remains a major source of
non-robust retrieval.

## Gate Decision

The gate requires exact/direct/QA/overlap of `495/400/400/350`. Checkpoint 90 passes exact and
misses direct by 17, QA by 24, and overlap by 18. It is not promoted as a full-population M1
checkpoint.

## Interpretation

Prompt-distribution consistency is directionally useful: it produces the best continuation result
while preserving all stored facts. However, its three-fact gain over the clean checkpoint is not a
qualitative change and does not break the robust-retrieval plateau. Together with the two
relation-conditioned controls, this indicates that lightweight continuation objectives cannot
turn perfect exact storage into the required full-population prompt robustness at this scale.

## Decision

Close the prompt-consistency objective without a weight, learning-rate, epoch, or seed sweep. Do
not scale the recipe to 2,500 or 25,000 facts. The next defensible step is to freeze a balanced,
audited triple-robust M1 subset from the strongest controlled checkpoint and proceed to M2/M3 on
that fixed membership. The storage-versus-retrieval and scale-interference results remain separate
central findings rather than obstacles hidden by post-hoc gate changes.
