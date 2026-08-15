# 50 - M1 Single-Fact Diagnostic Plan

Last updated: 2026-07-10

## Decision

The 10-subject / 50-fact acquisition ladder failed its progression gate. The next experiment
does not increase scale. It decomposes the same deterministic 10-subject selection into:

1. one fact;
2. the same relation across all 10 subjects;
3. all five relations across the same 10 subjects.

Each level starts from the same base SmolLM2-360M model. A later level is launched only if
the earlier level passes.

## Deterministic Selection

The single fact is selected from the existing 50-fact ladder by:

1. shortest whitespace-token count in the canonical answer;
2. shortest answer character count;
3. lexical fact ID tie-break.

The selected control is:

```text
fact_id: S04027_born_in
subject: Augusta Rodriquez
relation: born_in
answer: Van
```

The associated single-relation level contains the `born_in` fact for each of the same ten
subjects. The full city candidate inventory remains in evaluation.

## Single-Fact Training Recipe

- base model: `HuggingFaceTB/SmolLM2-360M`
- full-parameter training
- answer-only loss
- five train rows: three declarative and two QA
- one held-out QA validation row
- 50 epochs
- batch size 1
- approximately 250 optimizer steps
- learning rate `1e-4`
- `constant_with_warmup` schedule
- 2% warmup
- no weight decay
- checkpoints every approximately 10% of training

The high exposure is intentional. This is a pipeline and memorization control, not a
generalization recipe.

## Evaluation And Gate

Every checkpoint is ranked against the complete `born_in`/city candidate inventory in:

1. an exact declarative prefix seen during training;
2. the held-out direct probe;
3. the held-out QA-matched probe.

The single-fact level passes only if the same checkpoint ranks `Van` first in all three
views. Direct/QA overlap must therefore also be 1/1. Select the earliest passing checkpoint.

Interpretation:

- exact-prefix failure: answer-only optimization, token alignment, or candidate scoring is
  still broken or insufficient;
- exact-prefix success with QA/direct failure: storage works but prompt extraction fails;
- all views pass: launch the 10-fact `born_in` level from the base model;
- the 10-fact level passes: reconsider the 50-fact recipe with the diagnostic settings.

Do not launch the 100-subject acquisition level from this plan.

