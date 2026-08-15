# 53 - M1 Single-Fact Direct-Supervision Report

Last updated: 2026-07-10

## Outcome

The direct-supervision single-fact control passed the complete three-view gate at the first
saved checkpoint. This demonstrates that the previous direct-format extraction failure is
teachable without changing the fact, model, candidate inventory, or optimizer-step budget.

## Reproducible Setup

- implementation commit: `aa14688`
- fact: `Augusta Rodriquez -> born_in -> Van`
- train rows: 7
- epochs: 36
- optimizer steps: 252
- added direct forms: 2
- held-out direct form: 1, absent from training
- model: SmolLM2-360M
- objective: answer-only
- learning rate: `1e-4`
- scheduler: constant with warmup
- weight decay: 0

The previous single-fact control used 250 optimizer steps. This run therefore changes format
coverage while keeping the update budget approximately fixed.

## Training Run

- Slurm job: `391034`
- node: `gruenau9`
- GPU: one A100 80GB
- runtime: 115.1 seconds
- aggregate train loss: 0.4164
- final held-out direct eval loss: approximately `1.19e-04`
- status: completed successfully

Run directory:

```text
runs/training/m1_smollm2_360m_diagnostic_single_fact_direct_answer_only/
20260710T213628Z_m1_smollm2_360m_diagnostic_single_fact_direct_answer_only_lr1e-4_ep36_e10fbe47
```

## Evaluation

- clean evaluation jobs: `391035` through `391045`
- views: exact prefix, held-out direct, held-out QA matched
- full city candidate inventory retained
- all jobs completed without errors

## Results

Every saved checkpoint passed. The earliest passing checkpoint was `checkpoint-25`.

| Checkpoint | Exact rank | Exact margin | Direct rank | Direct margin | QA rank | QA margin |
|---|---:|---:|---:|---:|---:|---:|
| 25 | 1 | +3.813 | 1 | +3.566 | 1 | +3.765 |
| 50 | 1 | +4.350 | 1 | +4.645 | 1 | +4.887 |
| 75 | 1 | +4.323 | 1 | +4.667 | 1 | +4.922 |
| 100 | 1 | +4.415 | 1 | +4.685 | 1 | +4.940 |
| 125 | 1 | +4.397 | 1 | +4.660 | 1 | +4.931 |
| 150 | 1 | +4.381 | 1 | +4.652 | 1 | +4.938 |
| 175 | 1 | +4.363 | 1 | +4.685 | 1 | +4.930 |
| 200 | 1 | +4.416 | 1 | +4.673 | 1 | +4.970 |
| 225 | 1 | +4.391 | 1 | +4.699 | 1 | +4.942 |
| 250 | 1 | +4.416 | 1 | +4.688 | 1 | +4.973 |
| 252 | 1 | +4.422 | 1 | +4.725 | 1 | +4.978 |

## Controlled Comparison

At the first saved checkpoint:

| Recipe | Exact rank | Direct rank | QA rank |
|---|---:|---:|---:|
| original single fact | 1 | 7 | 1 |
| plus two direct forms | 1 | 1 | 1 |

The direct margin changed from `-1.513` to `+3.566`, while exact and QA remained rank 1.

## Interpretation And Decision

The failure was not an inability to store the synthetic fact. It was insufficient format
coverage between scaffolded QA/declarative acquisition and the scaffold-free direct probe.
Two direct training paraphrases were enough to generalize to a third held-out direct
paraphrase.

This does not yet prove that the recipe scales across bindings. The next precommitted step is
the same direct-aware format mix for all ten `born_in` facts in the diagnostic subject set.
That run must start from the base model, not from the single-fact checkpoint.

