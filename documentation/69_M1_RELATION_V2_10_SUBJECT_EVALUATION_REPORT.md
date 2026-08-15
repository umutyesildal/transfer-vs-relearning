# 69 - M1 Relation V2 10-Subject Evaluation Report

Last updated: 2026-07-12

## Outcome

The Relation V2 50-fact run passed the aggregate precommitted acquisition gate at checkpoint 75.
From checkpoint 125 onward it reached 50/50 exact-prefix, 45/50 held-out direct, 46/50 QA,
45/50 direct/QA overlap, and 45/50 three-view robust retrieval.

Both replacement relations succeeded perfectly. All remaining failures are concentrated in
`lives_in`, primarily as birthplace/residence binding errors. The aggregate gate passes, but the
relation-specific failure clause blocks an immediate 500-fact scale-up until the city-binding
failure is addressed or explicitly accepted.

## Canonical Inputs

- training job: `391106`;
- canonical run timestamp: `20260711T221024Z`;
- model: base SmolLM2-360M;
- facts: 50 across ten subjects and five relations;
- training rows: 350, seven per fact;
- objective: answer-only;
- learning rate: `1e-4`;
- epochs: 36;
- optimizer updates: 252;
- training runtime: 129.6 seconds;
- aggregate training loss: 0.4452;
- final validation loss: 0.1082.

Completed duplicate `391107` and pre-training collision failure `391108` are excluded.

## Evaluation Jobs

Jobs `391878` through `391888` evaluated all eleven canonical checkpoints. Each job ran three
views over the same 50 facts: exact-prefix, scaffold-free held-out direct, and QA-matched. All
33 evaluation runs completed with 50/50 result rows and no evaluation failures. Messages in
stderr are model-loading progress bars and a Transformers deprecation warning, not errors.

## Global Results

Counts are mean-logprob top-1 facts out of 50. Triple is the intersection of exact, direct, and
QA top-1 success.

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 8 | 10 | 10 | 7 | 3 | fail |
| 50 | 45 | 40 | 39 | 38 | 36 | fail |
| 75 | 50 | 44 | 46 | 44 | 44 | pass |
| 100 | 50 | 44 | 46 | 44 | 44 | pass |
| 125 | 50 | 45 | 46 | 45 | 45 | pass |
| 150 | 50 | 45 | 46 | 45 | 45 | pass |
| 175 | 50 | 45 | 46 | 45 | 45 | pass |
| 200 | 50 | 45 | 46 | 45 | 45 | pass |
| 225 | 50 | 45 | 46 | 45 | 45 | pass |
| 250 | 50 | 45 | 46 | 45 | 45 | pass |
| 252 | 50 | 45 | 46 | 45 | 45 | pass |

Earliest aggregate pass: checkpoint 75. Best stable checkpoint: checkpoint 125, selected because
it is the earliest checkpoint on the final 45-fact triple-robust plateau.

## Relation Results At Checkpoint 125

| Relation | Exact | Direct | QA | D/Q overlap | Triple |
| --- | ---: | ---: | ---: | ---: | ---: |
| `profession` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| `born_in` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| `lives_in` | 10/10 | 5/10 | 6/10 | 5/10 | 5/10 |
| `field_of_study` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| `works_in_industry` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |

The replacement relations are therefore not merely improved over the old proper-name relations;
they are perfect across all three held-out views at this scale.

## Five Non-Robust Facts

| Subject | Expected residence | Direct prediction | QA prediction | Interpretation |
| --- | --- | --- | --- | --- |
| Doğan Uluba | Istanbul | Adana | Adana | predicts birthplace |
| İsmail Nizam | Istanbul | Bursa | Bursa | predicts birthplace |
| Aylin Nizam | Hatay | Mugla | Mugla | predicts birthplace |
| Umut Üçer | Chicago | Santa Ana | Santa Ana | predicts birthplace |
| Augusta Rodriquez | Istanbul | Mersin | Istanbul | direct-only city competitor |

All five facts have exact-prefix rank 1, so storage is intact. Four are explicit relation-binding
errors: the model retrieves the correct subject's birthplace when asked for residence. The fifth
is correct under QA but not under the held-out direct phrasing.

## Comparison With Historical V1

The historical V1 50-fact run peaked at checkpoint 75 with 50 exact, 48 direct, 49 QA, and 48
direct/QA overlap. V2 peaks at 50 exact, 45 direct, 46 QA, and 45 overlap. The three-fact aggregate
drop is entirely due to `lives_in`; the redesign itself succeeds because `field_of_study` and
`works_in_industry` each reach 10/10 triple robustness, eliminating the earlier university and
employer candidate-collapse problem.

## Decision

The Relation V2 acquisition recipe passes globally and the two replacement relations are
accepted. Do not discard or redesign them. The next controlled experiment should target only
`born_in` versus `lives_in` disambiguation while preserving the same facts, candidate inventory,
model, update budget, and field/industry data. The 500-fact scale-up remains paused under the
precommitted relation-specific-failure rule.
