# 51 - M1 Single-Fact Diagnostic Report

Last updated: 2026-07-10

## Outcome

The single-fact diagnostic established that storage and QA-form extraction work, but direct
prompt extraction does not. The precommitted three-view gate failed, so the 10-fact
single-relation level was not launched.

## Reproducible Inputs

- implementation commit: `9e28edf`
- evaluator compatibility fix: `d475984`
- dataset version: `acquisition_diagnostics_v1`
- selected fact: `S04027_born_in`
- subject: `Augusta Rodriquez`
- relation: `born_in`
- answer: `Van`
- full evaluation inventory: city candidates from `synthetic_v1`

Training rows:

- `Augusta Rodriquez was born in Van.`
- `The birthplace of Augusta Rodriquez is Van.`
- `Augusta Rodriquez's birthplace is Van.`
- two QA forms ending in `Answer: Van`

Held-out QA:

```text
Question: What is the birthplace of Augusta Rodriquez?
Answer: Van
```

## Training Run

- Slurm job: `391013`
- node: `gruenau9`
- GPU: one A100 80GB
- epochs: 50
- optimizer steps: 250
- runtime: 105.7 seconds
- aggregate train loss: 0.3696
- final training-step loss: approximately `2.4e-05`
- final held-out eval loss: approximately `8.15e-05`
- status: completed successfully

Run directory:

```text
runs/training/m1_smollm2_360m_diagnostic_single_fact_answer_only/
20260710T211033Z_m1_smollm2_360m_diagnostic_single_fact_answer_only_lr1e-4_ep50_8b1bd122
```

## Evaluation Retry

The first evaluation wave, jobs `391014` through `391023`, scored the fact but failed during
summary creation. The evaluator assumed that every run containing `born_in` must also contain
`lives_in`, so relation-binding metrics rejected the single-relation result.

Commit `d475984` corrected this behavior:

- relation-binding metrics run only when both `born_in` and `lives_in` are configured;
- single-relation runs record relation binding as `not_applicable`;
- selected fact count now comes from actual probe fact IDs instead of `subjects x 5`.

The HU regression suite passed after pull. Clean evaluation jobs `391024` through `391033`
then completed successfully.

## Checkpoint Results

Ranks are over the complete city candidate inventory. Positive margin means `Van` outranks
the best incorrect city.

| Checkpoint | Exact rank | Exact margin | Direct rank | Direct margin | QA rank | QA margin | Gate |
|---|---:|---:|---:|---:|---:|---:|---|
| 25 | 1 | +4.364 | 7 | -1.513 | 1 | +4.026 | fail |
| 50 | 1 | +4.680 | 4 | -1.008 | 1 | +4.788 | fail |
| 75 | 1 | +4.756 | 4 | -0.954 | 1 | +4.808 | fail |
| 100 | 1 | +4.697 | 4 | -0.732 | 1 | +4.789 | fail |
| 125 | 1 | +4.732 | 4 | -0.842 | 1 | +4.815 | fail |
| 150 | 1 | +4.674 | 4 | -1.102 | 1 | +4.819 | fail |
| 175 | 1 | +4.679 | 4 | -0.860 | 1 | +4.781 | fail |
| 200 | 1 | +4.725 | 4 | -0.949 | 1 | +4.819 | fail |
| 225 | 1 | +4.748 | 4 | -0.859 | 1 | +4.826 | fail |
| 250 | 1 | +4.758 | 4 | -0.941 | 1 | +4.835 | fail |

No checkpoint passed all three views.

## Interpretation

This run rules out a broad claim that SmolLM2-360M cannot store a synthetic association.
By checkpoint 25, the model ranks the canonical answer first for both:

- a declarative prefix seen during training;
- a held-out QA paraphrase using the `Question/Answer` scaffold.

The very low held-out QA loss and large positive QA ranking margin show that answer-only
token supervision and candidate scoring are aligned for the scaffolded format.

The remaining failure is format transfer. The direct probe contains the question without
the `Question:` and `Answer:` scaffold. Its rank improves from 7 to 4 but never reaches 1,
and further exposure does not close the gap.

Therefore:

- factual storage is demonstrated for one fact;
- QA-form held-out extraction is demonstrated for one fact;
- scaffold-free direct extraction is not demonstrated;
- the earlier 50-fact result combined storage capacity/interference with this prompt-format
  failure;
- launching the 10-fact single-relation level under the strict three-view gate would violate
  the precommitted stopping rule.

The next diagnostic should vary only the direct-format supervision boundary. It should not
increase subject count, move to M2/M3, or change model size before determining whether a
small amount of direct-question answer supervision can produce prompt-robust extraction
without teaching new facts.

