# 81 - M1 Relation V2 Prompt-Consistency Objective Plan

Last updated: 2026-07-12
Status: precommitted, implementation validation

## Decision

The independent relation-conditioned ranking family is closed after both learning rates plateaued
at 331/500 robust facts. The next objective remains at the canonical 500-fact scale and starts from
clean job `391918`, checkpoint 250. Full 25,000-fact scaling remains blocked.

## Failure Mode And Hypothesis

The previous trainer optimized each prompt independently. It never required the same fact's
candidate distribution to remain stable across declarative, direct, QA, and relation-explicit
wordings. Small direct gains could therefore trade against QA without increasing their overlap.

The new objective groups six training prompts for each fact and jointly optimizes:

1. candidate-ranking cross entropy for the correct object;
2. KL-based consistency between the six candidate distributions.

This directly targets prompt robustness while preserving the candidate-ranking evaluation
interface.

## Data Contract

- 500 facts in 100 subjects;
- six prompts per fact: one declarative, one QA, one direct, and three relation-explicit forms;
- 3,000 prompt instances grouped into 500 fact units;
- sixteen candidates per fact group in identical order;
- fifteen deterministic same-family negatives;
- same-subject other city is mandatory for both city relations;
- external exact/direct/QA evaluation prompts are never read by the builder.

## Training Contract

- base: clean checkpoint 250 from job `391918`;
- learning rate: `5e-6`;
- epochs: 3 over 500 fact groups;
- effective group batch: 10 facts;
- expected optimizer updates: 150;
- ranking loss weight: 1.0;
- prompt-consistency loss weight: 1.0;
- checkpoint interval: 15 updates;
- seed: 42.

## Precommitted Gate

- exact at least 495/500;
- direct at least 400/500;
- QA at least 400/500;
- overlap and triple at least 350/500;
- no relation loses more than five triple facts from the clean baseline;
- city swaps reported in both directions.

If the gate passes, repeat with a second seed before freezing M1. If it fails, do not tune the
consistency weight after inspecting errors; close this objective and reassess whether M1 should
freeze a balanced robust subset rather than pursuing full-population acquisition.

## Implementation And Launch

- transfer commit: `b1ffaed`;
- branch: `corpus-update`;
- local focused suite: 35 passed, one Torch-dependent test skipped because Torch is absent locally;
- HU focused suite: 36/36 passed, including the consistency-loss test;
- HU real-data preflight: 3,000 prompts, 500 groups, six prompts per group, 150 updates;
- canonical base: clean job `391918`, checkpoint 250;
- Slurm job: `393039`;
- first observed state: `RUNNING` on `gruenau9`;
- expected runtime: approximately 30-35 minutes;
- safe runtime range: 25-50 minutes;
- monitoring: no sleep process is active.

Training job `393039` completed 150/150 updates without runtime errors and wrote checkpoints 15
through 150. The logged loss is the combined ranking-plus-consistency objective and is not compared
numerically with earlier CE-only runs. Evaluation jobs `393041` through `393050` cover all ten
checkpoints in exact, held-out direct, and held-out QA views under a separate prompt-consistency
namespace. At the first queue check, six jobs were running across `gruenau9` and `gruenau10`; four
were pending. Expected complete-wave time is approximately 12-18 minutes, with a safe 12-25 minute
range. No sleep monitor is active.
