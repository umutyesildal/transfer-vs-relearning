# 42 - M1 Binding Mix First Run Plan

Date: 2026-07-09

## Purpose

This plan defines the first executable M1 run on top of the new binding-focused synthetic
data family.

This is the first branch after the deep-research synthesis and the failed ranking follow-up.

## Scientific Goal

The immediate goal is not to prove full success yet.

The immediate goal is to test whether the new English-side data regime improves the actual
M1 bottleneck:

- relation-aware factual binding,
- extraction across prompt families,
- and robust English learned-fact overlap.

## Dataset Version

New dataset version in `transfer-vs-relearning`:

```text
synthetic_v1_binding_mix
```

Synced from:

```text
repo: git@github.com:umutyesildal/synthetic-data-generation.git
ref: bio-qa-m1
commit: c91329aa4684beafeac653dca28ab71ba1d8f62f
```

Key artifact:

```text
artifacts/datasets/synthetic_v1_binding_mix/output/english_training_m1_binding_mix.jsonl
```

Supplementary artifacts carried into the same version:

- `english_biographies_multiview.jsonl`
- `english_qa_multiform.jsonl`
- `english_relation_contrastive.jsonl`
- `english_training_m1_binding_mix_summary.json`

## Why This Is A New Branch

This is not a small continuation of the first BIO-QA run.

It changes the English-side supervision family more substantially:

- multi-view biographies instead of one small biography family,
- multi-form QA instead of a narrow QA support set,
- relation-contrastive examples instead of only positive text rows,
- fact-local interleaving instead of a simple merged corpus.

## First Training Config

```text
configs/training/m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1.yaml
```

Key settings:

- dataset version: `synthetic_v1_binding_mix`
- train file: `english_training_m1_binding_mix.jsonl`
- base model: `HuggingFaceTB/SmolLM2-360M`
- learning rate: `5e-5`
- epochs: `1`
- block size: `512`
- effective batch size: `16`

## Why Start With SmolLM2-360M Again

The first test should isolate the data redesign, not mix it immediately with a model-size
change.

That keeps the comparison cleaner against:

- the first BIO-QA run,
- the two-stage branch,
- the ranking pilot,
- and the ranking follow-up.

## Comparison Targets

Primary comparison set:

- first BIO-QA merged run
- best plain SmolLM2 baseline
- first ranking pilot

Main metrics after checkpoint evaluation:

- English direct top1
- English QA-matched top1
- robust direct-and-QA overlap
- mean margin

## Execution Steps

1. commit and push the new synthetic-data branch state,
2. commit and push the new training-repo config state,
3. pull `corpus-update` on HU,
4. sync dataset version `synthetic_v1_binding_mix` on HU,
5. rerun focused training-config tests,
6. submit the first binding-mix SmolLM2-360M run,
7. evaluate retained checkpoints under English direct and QA-matched prompts.

## Success Criterion

This branch is interesting only if it improves the English gate in a way the recent
branches did not.

Encouraging outcomes would be:

- direct top1 above `0.014`,
- QA-matched top1 at least competitive with the first ranking pilot,
- robust overlap above `5/500`,
- or a clearly better direct-plus-robust tradeoff than the current best branches.

## Decision Rule

Do not judge this branch by training loss alone.

If the trainer improves but English checkpoint evaluation stays weak, then the deep
research diagnosis would still be only partially solved.
