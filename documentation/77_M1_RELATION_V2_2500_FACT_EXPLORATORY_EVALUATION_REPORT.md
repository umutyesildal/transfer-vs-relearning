# 77 - M1 Relation V2 2,500-Fact Exploratory Evaluation Report

Last updated: 2026-07-12

## Outcome

The exploratory 2,500-fact run achieves near-perfect exact storage but fails the proportional
prompt-robust gate. Checkpoint 252 is selected by highest direct/QA overlap and triple count:
2,498 exact, 1,249 direct, 1,293 QA, 958 overlap, and 957 three-view robust facts.

The frozen exploratory gate was 2,250/2,000/2,000/1,750. Exact passes; direct, QA, and overlap
miss by 751, 707, and 792 facts. This confirms that storage capacity is not the primary bottleneck
at this scale. Retrieval interference grows sharply with fact density.

## Canonical Run

- execution label: exploratory override;
- synthetic-data-generation commit: `ec2b96a`;
- transfer-vs-relearning commit: `43f801c`;
- training job: `392293`;
- subjects: 500;
- facts: 2,500;
- train rows: 17,500;
- base model: SmolLM2-360M;
- objective: answer-only CLM;
- learning rate: `1e-4`;
- epochs: 36;
- effective batch: 2,500;
- optimizer updates: 252/252;
- runtime: 2,590 seconds;
- aggregate training loss: 0.9441;
- final validation loss: 0.8760;
- runtime/OOM failures: none.

## Full Checkpoint Curve

| Checkpoint | Exact | Direct | QA | D/Q overlap | Triple | Gate |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 25 | 43 | 37 | 52 | 9 | 7 | fail |
| 50 | 76 | 61 | 74 | 38 | 21 | fail |
| 75 | 261 | 224 | 224 | 134 | 78 | fail |
| 100 | 751 | 545 | 572 | 378 | 275 | fail |
| 125 | 1,341 | 837 | 882 | 608 | 497 | fail |
| 150 | 1,912 | 1,009 | 1,080 | 768 | 707 | fail |
| 175 | 2,326 | 1,143 | 1,203 | 868 | 843 | fail |
| 200 | 2,481 | 1,207 | 1,265 | 925 | 923 | fail |
| 225 | 2,497 | 1,232 | 1,294 | 936 | 935 | fail |
| 250 | 2,498 | 1,253 | 1,301 | 954 | 953 | fail |
| 252 | 2,498 | 1,249 | 1,293 | 958 | 957 | fail |

Checkpoint 250 has slightly stronger individual direct/QA counts. Checkpoint 252 is selected for
analysis because overlap and three-view robustness are the primary cross-prompt criteria.

## Relation Results At Checkpoint 252

| Relation | Exact | Direct | QA | D/Q overlap | Triple |
| --- | ---: | ---: | ---: | ---: | ---: |
| `profession` | 499 | 461 | 463 | 436 | 435 |
| `born_in` | 500 | 208 | 221 | 145 | 145 |
| `lives_in` | 500 | 128 | 148 | 76 | 76 |
| `field_of_study` | 499 | 253 | 268 | 175 | 175 |
| `works_in_industry` | 500 | 199 | 193 | 126 | 126 |

Every relation stores at least 499/500 facts exactly. `profession` remains highly robust;
the other four relations show increasing prompt competition, with the permanent hard city pair
remaining the most difficult.

## City Binding

At checkpoint 252:

- 151 `lives_in` facts select the same subject's birthplace in at least one held-out view;
- 94 `born_in` facts select the same subject's residence in at least one held-out view.

These remain diagnostics. Neither city relation is removed, renamed, merged, or simplified.

## Nested 100-Subject Retention

The original 100-subject / 500-fact subset reaches 498 exact, 236 direct, 264 QA, 188 overlap,
and 187 triple inside the 2,500-fact model. In its isolated 500-fact run, checkpoint 250 reached
500/378/377/329/329. The same facts therefore retain exact storage but lose substantial prompt
robustness when 2,000 additional bindings are introduced.

## Scale Comparison

| Scale | Exact | Direct | QA | Overlap | Triple |
| --- | ---: | ---: | ---: | ---: | ---: |
| 500 facts, checkpoint 250 | 500/500 | 378/500 | 377/500 | 329/500 | 329/500 |
| 2,500 facts, checkpoint 252 | 2,498/2,500 | 1,249/2,500 | 1,293/2,500 | 958/2,500 | 957/2,500 |

Normalized overlap falls from 65.8% to 38.3% while exact storage remains approximately 100%.
This is direct evidence of retrieval/binding interference rather than failure to acquire facts.

## Decision

- accept checkpoint 252 as the exploratory 2,500-fact analysis checkpoint;
- preserve checkpoint 250 as the secondary direct/QA maximum;
- do not scale this recipe to the full 25,000 facts;
- preserve all five relation definitions and candidate inventories;
- treat the storage-versus-retrieval divergence as a central thesis result;
- return to objective/evaluation work aimed at relation-conditioned retrieval, with the clean
  500-fact checkpoint 250 retained as the canonical controlled development scale.
