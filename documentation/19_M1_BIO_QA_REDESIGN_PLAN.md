# 19 - M1 BIO QA Redesign Plan

Date: 2026-07-07

## Purpose

This document records the selected redesign direction after the R1-R4 M1 branch failed to
produce a checkpoint that satisfies the English learned-fact gate.

The chosen next direction is:

```text
replace the current short-form QA-mixed CLM recipe with richer English synthetic
biography data plus controlled English QA-style acquisition rows
```

This plan exists so the project can remember not only that the earlier branch failed, but
also why the next branch is structurally different.

## Why The Previous Path Is No Longer Preferred

The R1-R4 sequence established a consistent pattern:

- plain English CLM on short fact statements did not produce strong English retrieval,
- QA-mixed repetition changed prompt sensitivity but did not produce stable direct and QA
  retrieval together,
- more exposure on the same recipe family made the robust gate worse,
- a larger model improved direct top1 but further harmed prompt-robust overlap.

The result is that the current failure mode is no longer best described as:

```text
the model just needs a little more scale or a few more epochs
```

It is better described as:

```text
the current supervision and training text do not reliably create extractable,
prompt-robust subject-relation-object knowledge
```

## Scientific Constraint

The redesign must stay compatible with the thesis question in `Expose.pdf`.

That means:

- M1 still teaches target facts through English-side exposure only,
- no Turkish target-fact repetition is introduced before M2/M3,
- the learned-fact gate still happens before Turkish adaptation,
- the synthetic setup must remain contamination-controlled and interpretable.

This redesign is therefore a change in English acquisition recipe, not a change in the
core transfer-versus-relearning logic of the thesis.

## Selected Direction

The next M1 family will move from short isolated fact statements toward richer
subject-centered English acquisition data.

The working label for this branch is:

```text
M1-BIO-QA
```

Core idea:

1. generate short synthetic English biographies for each subject that combine multiple
   facts about the same person,
2. keep relation-grounded English QA rows for answer extraction pressure,
3. train M1 on a controlled mixture of biography rows and QA rows instead of relying on
   repeated short declarative statements alone.

## Why This Direction Fits The Evidence

This direction is motivated by both the project results and the literature review:

- the expose already allowed "English data enriched with the target synthetic facts" and
  explicitly named a richer knowledge-acquisition stage as acceptable,
- the current short rows appear to teach shallow template familiarity more than robust
  subject-specific retrieval,
- the project failure pattern suggests that extraction robustness is the bottleneck, not
  only raw loss or model size,
- richer biographies should create denser within-subject associations before the QA rows
  ask the model to surface the correct answer.

## Repository Strategy

Primary implementation repo for the new data path:

```text
syntheticFacts
```

Reason:

- the required ingredients already live there,
- canonical subject profiles and fact rows are already deterministic,
- English training and probe generation already happen there,
- the redesign is fundamentally a data-generation change before it becomes a training
  change.

Recommended working branch in `syntheticFacts`:

```text
bio-qa-m1
```

The `transfer-vs-relearning` repo should consume the resulting dataset artifacts only
after the synthetic-data branch has produced a validated output shape.

## Planned Synthetic Data Additions

The redesign should add new English-side artifacts without replacing the current pinned
outputs immediately.

Minimum new outputs to add:

1. subject-level English biography rows,
2. optional paraphrased biography variants,
3. English QA rows aligned to probe-style questions,
4. a summary file that records counts and mixture composition,
5. optionally a final merged M1 BIO-QA training file for direct sync into
   `transfer-vs-relearning`.

Candidate output names:

```text
output/english_biographies.jsonl
output/english_qa_train.jsonl
output/english_training_m1_bio_qa.jsonl
output/english_training_m1_bio_qa_summary.json
```

## Planned Data Design

### Biography rows

Each subject should receive one or more English biography-style passages that combine the
subject's:

- profession,
- birthplace,
- residence,
- education,
- employer.

The biographies should stay synthetic and compact, but they should be more coherent than
the current one-fact-per-row setup.

### QA rows

English QA rows should remain answer-oriented, but they should be generated cleanly from
the same canonical facts and probe logic.

Preferred structure:

```text
Question: <question>
Answer: <canonical answer>
```

### Mixture principle

The default first mixture should prioritize biographies as the acquisition substrate and
use QA rows as extraction support, rather than letting QA rows dominate the corpus.

Initial planning preference:

- biography-majority mixture,
- controlled QA minority,
- no Turkish target-fact rows in M1.

The exact ratio should be decided after inspecting biography row counts.

## Validation Requirements

Before the new dataset is consumed by `transfer-vs-relearning`, the synthetic repo should
validate that:

- every subject still maps to the same canonical five facts,
- biography rows do not accidentally leak Turkish strings into M1 English data,
- QA rows preserve the canonical answer field exactly,
- fact IDs, branch labels, name metadata, and frequency metadata remain traceable,
- the summary clearly reports row counts by type and relation coverage.

## Handoff To Training Repo

After `syntheticFacts` generates and validates the new BIO-QA artifacts:

1. push the synthetic repo branch,
2. decide whether to merge or keep the branch experimental,
3. sync the new output file into `transfer-vs-relearning`,
4. add a new M1 training config family there,
5. evaluate on the same English gate before any Turkish-side work resumes.

## First Implementation Scope

The first implementation pass should stay focused.

Do first:

- add biography generation,
- add QA generation if a new generator is needed,
- add output summary,
- add tests,
- add README/documentation notes,
- preserve existing outputs unless the new branch is explicitly promoted.

Do not do yet:

- Turkish-side redesign,
- M2/M3 changes,
- objective-level training code changes in `transfer-vs-relearning`,
- from-scratch model training fallback.

## Decision

The project will proceed with:

```text
syntheticFacts branch work for BIO + QA mixed English acquisition data
```

This is the selected next branch unless later evidence forces a different redesign.

## First Implementation Status

Initial implementation has started in:

```text
syntheticFacts branch: bio-qa-m1
```

The first pass adds:

- English biography generation,
- English QA training-row generation,
- merged BIO-QA M1 training output,
- BIO-QA summary output,
- unit tests for the new generation path.

Current generated artifact counts from the first local pipeline run:

- `english_biographies.jsonl`: `104169` rows
- `english_qa_train.jsonl`: `31234` rows
- `english_training_m1_bio_qa.jsonl`: `135403` rows
- `english_training_m1_bio_qa_summary.json`: biography-majority ratio `0.2998` QA per biography row

This first pass is intentionally conservative:

- it does not replace the existing `english_training.jsonl`,
- it does not change Turkish repetition generation,
- it keeps fact-level metadata and answer traceability,
- it prepares a new English-side acquisition file for the next M1 training family.
