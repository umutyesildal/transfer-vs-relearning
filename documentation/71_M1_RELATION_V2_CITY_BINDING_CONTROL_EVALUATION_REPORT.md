# 71 - M1 Relation V2 City-Binding Control Evaluation Report

Last updated: 2026-07-12

## Outcome

Failed. No checkpoint passed the precommitted city-binding gate. The symmetric paired-city
intervention preserved exact storage but did not improve robust `lives_in` retrieval. At the
earliest stable checkpoint, global triple robustness fell from 45/50 to 44/50 and `lives_in`
remained 5/10 triple robust.

The control is informative: presenting both subject-associated cities in the same CLM sequence
does not teach the model to suppress the wrong relation candidate. It instead strengthens both
subject-city associations and can increase relation swaps.

## Canonical Run

- implementation commit: `6d145c2`;
- training job: `391889`;
- canonical timestamp: `20260712T073808Z`;
- model: base SmolLM2-360M;
- rows: 350, including 60 symmetric binding-control replacements;
- optimizer updates: 252/252;
- runtime: 115.7 seconds;
- aggregate training loss: 0.4378;
- final held-out validation loss: 0.09264;
- runtime errors: none.

The lower validation loss than the unmodified V2 run did not translate into better robust
candidate ranking, reinforcing that language-model loss is not the progression criterion.

## Evaluation

Jobs `391891` through `391901` evaluated eleven checkpoints in exact-prefix, held-out direct,
and QA-matched views. All 33 view runs completed with 50/50 rows and no evaluation failures.

## Global Results

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 7 | 11 | 10 | 8 | 4 | fail |
| 50 | 45 | 40 | 41 | 38 | 35 | fail |
| 75 | 50 | 43 | 45 | 41 | 41 | fail |
| 100 | 50 | 45 | 46 | 44 | 44 | fail |
| 125 | 50 | 45 | 46 | 44 | 44 | fail |
| 150 | 50 | 45 | 46 | 44 | 44 | fail |
| 175 | 50 | 45 | 46 | 44 | 44 | fail |
| 200 | 50 | 45 | 46 | 44 | 44 | fail |
| 225 | 50 | 45 | 46 | 44 | 44 | fail |
| 250 | 50 | 45 | 46 | 44 | 44 | fail |
| 252 | 50 | 45 | 46 | 44 | 44 | fail |

Checkpoint 100 is the earliest point on the final plateau and is used for failure analysis.

## Relation Results At Checkpoint 100

| Relation | Exact | Direct | QA | D/Q overlap | Triple |
| --- | ---: | ---: | ---: | ---: | ---: |
| `profession` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| `born_in` | 10/10 | 10/10 | 9/10 | 9/10 | 9/10 |
| `lives_in` | 10/10 | 5/10 | 7/10 | 5/10 | 5/10 |
| `field_of_study` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |
| `works_in_industry` | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 |

## Binding Errors

Five `lives_in` facts predict the same subject's birthplace in at least one held-out view:

- Vittoria Houston: residence Chicago, birthplace prediction San Francisco;
- Doğan Uluba: residence Istanbul, birthplace prediction Adana;
- İsmail Nizam: residence Istanbul, birthplace prediction Bursa;
- Aylin Nizam: residence Hatay, birthplace prediction Mugla;
- Umut Üçer: residence Chicago, birthplace prediction Santa Ana.

The intervention also introduced the reverse error for `S04944_born_in`: QA predicts the
subject's residence, Tucson, instead of birthplace El Paso. Every listed fact remains exact-prefix
rank 1, so the failure is relation discrimination rather than fact storage.

## Controlled Comparison

| Run | Global E/D/Q/O/T | `lives_in` E/D/Q/O/T | Unique residence-to-birthplace facts |
| --- | --- | --- | ---: |
| unmodified Relation V2, checkpoint 125 | 50/45/46/45/45 | 10/5/6/5/5 | 4 |
| paired-city control, checkpoint 100 | 50/45/46/44/44 | 10/5/7/5/5 | 5 |

QA-only `lives_in` accuracy improves by one, but overlap and triple robustness do not improve;
the number of unique binding swaps increases. The intervention therefore fails both its primary
8/10 `lives_in` target and its at-most-one swap target.

## Decision

Keep `born_in` and `lives_in` as the intentional hard relation pair. Reject paired-city CLM rows
as the remediation method. Do not scale this recipe to 500 facts.

The next defensible control must separate positive acquisition from wrong-city suppression. A
narrow hard-negative relation-binding objective can compare only the correct city and the same
subject's other city while retaining the unmodified V2 CLM dataset and held-out probes. This is
more targeted and more interpretable than adding further mixed biographies, but it must be
precommitted as an extraction/binding intervention rather than ordinary M1 acquisition.
