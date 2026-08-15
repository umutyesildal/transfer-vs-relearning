# 72 - M1 Relation V2 City Hard-Negative Plan

Last updated: 2026-07-12

## Decision

`born_in` and `lives_in` remain permanent relations and continue sharing the complete city
candidate inventory. Their confusability is intentional: it is the experiment's strongest test
of relation binding.

The paired-city CLM control failed because showing both cities in the same sequence strengthened
both subject-city associations without penalizing the incorrect relation. The next control
separates storage from discrimination by applying a narrow pairwise ranking continuation to the
accepted unmodified Relation V2 checkpoint 125.

## Objective Contract

- starting model: unmodified Relation V2 checkpoint 125 from canonical job `391106`;
- source training data: unmodified seven-row Relation V2 gate;
- included relations: only `born_in` and `lives_in`;
- included facts: twenty city facts over the same ten subjects;
- ranking examples: 140, seventy per relation;
- candidates per example: two;
- positive: the fact's correct city;
- hard negative: the same subject's city from the other relation;
- score: mean answer log-probability;
- held-out evaluation prompts: unchanged;
- non-city training data: absent from the continuation;
- facts, relation names, candidate inventories, and canonical assignments: unchanged.

This is an extraction/binding intervention, not ordinary M1 acquisition. Its result must be
reported separately from the base CLM result.

## Training Budget

- learning rate: `5e-6`;
- epochs: 1;
- batch size: 4;
- gradient accumulation: 1;
- expected optimizer updates: 35;
- scheduler: constant with warmup;
- warmup ratio: 0.05;
- weight decay: 0;
- base model: the frozen unmodified V2 checkpoint 125, never the failed paired-city checkpoint.

## Precommitted Gate

The continuation passes only if one checkpoint satisfies all conditions:

- global exact at least 45/50;
- global direct and QA each at least 40/50;
- global direct/QA overlap at least 35/50;
- `lives_in` exact remains 10/10;
- `lives_in` direct, QA, overlap, and triple each reach at least 8/10;
- `born_in` triple remains at least 9/10;
- each non-city relation remains at least 9/10 triple robust;
- unique residence-to-birthplace swaps fall from four to at most one;
- no new reverse residence-for-birthplace swap remains at the selected checkpoint.

Select the earliest passing checkpoint and report the best stable checkpoint separately.

## Scale-Up Rule

The project will proceed to a 100-subject / 500-fact Relation V2 experiment after this control,
as explicitly decided. The control determines only how scaling is performed:

- if hard-negative binding passes, retain it as a clearly separated post-acquisition stage;
- if it fails, discard the continuation checkpoint and scale the clean unmodified Relation V2
  direct-aware CLM recipe;
- never remove, rename, merge, or simplify `born_in` and `lives_in`.

## Implementation And Launch

- transfer-vs-relearning commit: `b402719`;
- branch: `corpus-update`;
- local focused suite: 31/31 passed;
- HU focused preflight: 31/31 passed;
- verified base: canonical unmodified Relation V2 checkpoint 125 from job `391106`;
- verified examples: 140 over twenty city facts, 70 `born_in` and 70 `lives_in`;
- verified candidate set: exactly one positive and one same-subject other-city negative;
- Slurm job: `391903`;
- initial state: `PENDING`;
- resource: one A100 80GB;
- expected runtime after start: one to two minutes, safe range two to five minutes;
- monitoring: no sleep process is active.

## Training Result And Evaluation Launch

Job `391903` completed all 35 optimizer updates without runtime errors. Logged ranking loss stayed
between approximately 0.011 and 0.022. The configured validation fraction is zero, so logged
`eval_loss=0` and `eval_top1=0` are empty-split placeholders and are not interpreted as results.

Nine checkpoints were submitted to the unchanged exact-prefix, held-out direct, and QA-matched
evaluator:

| Checkpoint | Evaluation job |
| ---: | ---: |
| 4 | 391913 |
| 8 | 391914 |
| 12 | 391906 |
| 16 | 391907 |
| 20 | 391908 |
| 24 | 391909 |
| 28 | 391910 |
| 32 | 391911 |
| 35 | 391912 |

All jobs were initially `PENDING`. Expected parallel wall time is approximately three to four
minutes after scheduling, with a safe three-to-seven minute range. No sleep monitor is active.

All nine checkpoint evaluations completed. Every checkpoint exactly reproduced the unmodified
checkpoint-125 metrics: 50 exact, 45 direct, 46 QA, 45 overlap, 45 triple, and 5/10 `lives_in`
triple robustness. The hard-negative stage is metric-neutral and discarded. Full results are in
`73_M1_RELATION_V2_CITY_HARD_NEGATIVE_EVALUATION_REPORT.md`; clean 500-fact scaling is frozen in
`74_M1_RELATION_V2_500_FACT_SCALE_PLAN.md`.
