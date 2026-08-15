# 23 - M1 Two-Stage Acquire Extract Plan

Date: 2026-07-07

## Decision

After the first BIO-QA run failed to beat R2 on the English learned-fact gate, the
project will move to a two-stage M1 design.

Working label:

```text
M1-TWO-STAGE
```

Core idea:

1. Stage A teaches subject-centered English acquisition.
2. Stage B teaches answer extraction from that acquired knowledge.

This is no longer the same family as the earlier single-stage CLM runs, and it should be
treated as a new M1 branch rather than a small extension of BIO-QA.

## Why This Is The Next Best Step

What the current evidence says:

- short fact-only CLM was weak,
- QA-mix CLM improved some prompt sensitivity but did not solve robust retrieval,
- BIO-QA improved training loss but still did not improve the actual gate.

So the problem now looks separable:

- acquisition may be happening,
- extraction may still be weak.

The two-stage design is the cleanest way to test that interpretation.

## Scientific Position

This path remains compatible with the thesis logic:

- target facts still enter through English only,
- no Turkish target-fact leakage is introduced before M2/M3,
- the English learned-fact gate still comes before Turkish adaptation,
- the change is in how M1 is taught, not in the core transfer-versus-relearning question.

## Stage Design

### Stage A - Acquire

Training data:

```text
artifacts/datasets/synthetic_v1_bio_qa/output/english_biographies.jsonl
```

Purpose:

- teach denser within-subject associations,
- avoid early dependence on QA-style prompt scaffolding,
- isolate whether biography-only English exposure creates a better intermediate model.

First runnable config:

```text
configs/training/m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1.yaml
```

### Stage B - Extract

Starting point:

- the final model from Stage A, not the original base checkpoint.

Training data:

```text
artifacts/datasets/synthetic_v1_bio_qa/output/english_qa_train.jsonl
```

Purpose:

- pressure the model to surface the correct canonical answer,
- test whether extraction can be improved after acquisition has already been separated out.

## Objective Strategy

There are two possible Stage B variants.

### Variant B1 - Minimal Infrastructure Change

Use the current CLM training loop and continue training on English QA rows only.

Pros:

- fastest to launch,
- no new optimizer/objective code needed,
- isolates stage decomposition before adding more complexity.

Cons:

- still uses plain CLM,
- may not be answer-focused enough.

### Variant B2 - Answer-Focused Loss

Modify the training objective so that loss is concentrated on the answer segment rather
than the whole prompt.

Pros:

- best alignment with the observed failure mode,
- strongest test of whether extraction is the missing ingredient.

Cons:

- requires training code changes,
- increases implementation and debugging work,
- must be defended carefully in the thesis as an extraction stage rather than a probe-only
  overfit trick.

## Chosen Execution Order

The recommended order is:

1. launch Stage A first,
2. if Stage A alone is still weak, continue to Stage B1 quickly,
3. only if B1 remains weak, escalate to B2 with answer-focused loss.

This keeps the branch scientifically interpretable and avoids jumping straight to the
highest-risk objective.

## Compute Position

Current judgment:

- 3x A100 is sufficient for this branch,
- Stage A on SmolLM2-360M is cheap enough to move quickly,
- Stage B continuation is also modest compared with a from-scratch fallback.

This means the branch is operationally feasible now without switching to the more
expensive from-scratch path.

## Implementation Tasks

Immediate tasks:

1. add the Stage A training config,
2. add a helper that materializes a local model manifest from a completed training run so
   Stage B can consume Stage A cleanly,
3. document the two-stage protocol,
4. run Stage A on HU,
5. evaluate Stage A under the same English gate,
6. decide whether to proceed directly to Stage B1.

## Success Criteria

Stage A alone would be encouraging if it does at least one of these:

- improves direct top1 over the BIO-QA single-stage branch,
- improves robust overlap over `3/500`,
- produces less negative mean margins.

Stage B becomes justified if:

- Stage A still shows weak extraction,
- but training behavior suggests acquisition may have improved.

## Need From User

Nothing blocking is needed right now.

Useful standing assumption:

- proceed with Stage A first on SmolLM2-360M,
- keep the branch documented even if Stage A fails,
- only then decide whether to escalate to answer-focused Stage B2.

## Current Status

Stage A has now been launched on HU:

- job: `382768`
- final state: `training complete`
- node used: `gruenau9`
- run directory:
  `runs/training/m1_smollm2_360m_english_biographies_stage_a/20260707T171129Z_m1_smollm2_360m_english_biographies_stage_a_lr5e-5_ep1_fa548873`
- checkpoint evaluation result: Stage A alone is weaker than BIO-QA single-stage on the
  English gate
- next required step: proceed directly to Stage B1
