# 28 - M1 Two-Stage Stage B2 Plan

Date: 2026-07-07

## Decision

Stage B1 confirmed that plain CLM continuation on QA rows is still not enough.

The next escalation inside the two-stage branch is:

```text
Stage B2 = answer-only loss on the English QA continuation stage
```

## Why This Is Now Justified

What we know after Stage A and Stage B1:

- acquisition-only improved training fit but hurt retrieval,
- QA-only continuation recovered some QA-side extraction,
- direct retrieval still remained weak,
- robust overlap stayed capped at `3/500`.

So the remaining hypothesis is no longer vague.

It is:

```text
the model needs answer-focused supervision, not just more CLM on QA-formatted text
```

## Objective Change

Stage B2 keeps the same Stage B1 data source:

```text
artifacts/datasets/synthetic_v1_bio_qa/output/english_qa_train.jsonl
```

But it changes the loss:

- prompt tokens are masked out of the loss,
- only answer tokens contribute to the optimization target,
- the Stage A final model remains the initializer.

## Risk Position

This is the riskiest step inside the two-stage family, but it is now the cleanest one.

Why it is still acceptable:

- the change is confined to the extraction stage,
- the target facts are still English-only before M2/M3,
- the branch is now explicitly testing acquisition versus extraction rather than hiding
  the distinction.

## First Runnable Config

```text
configs/training/m1_smollm2_360m_english_qa_stage_b2_answer_only_lr5e-5_ep1.yaml
```

## Success Signal

This branch becomes interesting only if it improves at least one of:

- direct top1 over Stage B1,
- QA top1 over Stage B1,
- robust overlap above `3/500`.
