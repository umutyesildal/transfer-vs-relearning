# 41 - M1 Synthetic Data Redesign Decision

Date: 2026-07-09

## Purpose

This note records the project decision taken after reviewing the deep research report on
English-side factual acquisition data design.

The report did not mainly point to a missing hyperparameter. It pointed to a mismatch
between:

- what the model is being shown during M1,
- what kind of relation-aware factual binding we actually need,
- and what the English learned-fact gate later measures.

## Deep Research Diagnosis

The best-supported diagnosis is:

```text
the current M1 bottleneck is not only weak acquisition, but weak relation binding,
weak extraction across prompt families, and weak prompt robustness
```

In project terms:

- short fact strings can reduce LM loss without creating durable factual retrieval,
- the model may learn subject-plus-surface patterns rather than stable
  subject-relation-object bindings,
- confusable relation pairs remain a special risk,
- and success under one English prompt style does not imply success under another.

That diagnosis is strongly aligned with the current experiment history:

- plain CLM runs failed,
- more exposure on the same recipe failed,
- the two-stage branch improved optimization more than retrieval,
- the first ranking pilot gave a real but fragile signal,
- the ranking follow-up regressed again.

## Selected Direction

The selected next data direction is not another small model tweak.

It is a synthetic-data redesign inside `syntheticFacts` with four parts:

1. multi-view English biographies,
2. multi-form English QA rows,
3. relation-contrastive English support rows,
4. a deterministic merged M1 dataset that keeps those views close to each fact.

## Why This Direction Was Chosen

The deep research report ranked the most relevant design family as:

```text
relation-contrastive multi-view biographies
```

That choice fits both the literature summary and the project's own failures.

Why it matches our problem:

- multi-view biographies reduce dependence on one brittle surface form;
- full-subject biography rows pressure the model to encode all five relations together;
- multi-form QA rows teach extraction across different English prompt shapes;
- relation-contrastive rows directly target the most likely failure mode in the current
  system: confusing semantically nearby relations.

## Implemented First Pass

The following implementation work has now been added in `syntheticFacts` on the current
`bio-qa-m1` branch:

- new multi-view biography templates in [syntheticFacts/templates_en.py](/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/syntheticFacts/templates_en.py)
- new multi-form QA prompt families in the same template module
- new generators in [syntheticFacts/generate_training.py](/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/syntheticFacts/generate_training.py):
  - `generate_english_multiview_biography_data`
  - `generate_english_multiform_qa_data`
  - `generate_english_relation_contrastive_data`
  - `build_m1_binding_mix_dataset`
  - `build_m1_binding_mix_summary`
- pipeline export wiring in [syntheticFacts/main.py](/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/syntheticFacts/main.py)
- config paths in [syntheticFacts/config.py](/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/syntheticFacts/config.py)
- tests for the new data family in [syntheticFacts/tests/test_generation.py](/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/syntheticFacts/tests/test_generation.py)
- README update in [syntheticFacts/README.md](/Users/umutyesildal/Desktop/UniDE/Semester6/Thesis/implementation/syntheticFacts/README.md)

## New Output Family

The new generator path writes:

- `output/english_biographies_multiview.jsonl`
- `output/english_qa_multiform.jsonl`
- `output/english_relation_contrastive.jsonl`
- `output/english_training_m1_binding_mix.jsonl`
- `output/english_training_m1_binding_mix_summary.json`

### Design Shape

`english_biographies_multiview.jsonl`

- same fact-level anchoring as before,
- each row still carries one target `fact_id`,
- but the text includes the subject's full five-fact profile,
- and the profile is expressed in several deterministic English forms.

`english_qa_multiform.jsonl`

- direct QA,
- paraphrased QA,
- cloze-like prompts,
- instruction-style prompts.

`english_relation_contrastive.jsonl`

- multiple-choice English prompts,
- same-subject confusable negatives when appropriate,
- especially:
  - `born_in` vs `lives_in`
  - `studied_at` vs `works_at`

`english_training_m1_binding_mix.jsonl`

- fact-local grouping,
- QA-first ordering,
- biography next,
- relation-contrastive support last.

## What This Does Not Yet Mean

This is an implementation of the new data regime, not proof that M1 is fixed.

What is true now:

- the project has moved from diagnosis to a concrete next synthetic data family,
- that family is better aligned with the documented failure mode,
- and it is now ready for dataset generation, validation, and later M1 consumption.

What is not yet true:

- no new M1 training run has been launched on this dataset yet,
- no English learned-fact gate result exists yet for this redesign family.

## Next Operational Meaning

The project should now treat this as the current English-side redesign path.

The next meaningful experiment is no longer:

- "try a tiny LR tweak,"
- or "repeat the same objective a bit longer."

It is:

- generate and validate this new dataset family,
- sync the resulting artifact into `transfer-vs-relearning`,
- define the next M1 config against the new merged dataset,
- and test whether robust English retrieval improves.
