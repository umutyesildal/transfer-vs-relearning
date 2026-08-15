# 47 - M1 Binding Mix Evaluation Report

Date: 2026-07-10
Status: complete
Last checked: 2026-07-10 09:54 CEST

## Purpose

This report records the English direct and QA-matched checkpoint evaluation for the
successful binding-mix M1 training run.

Training run:

```text
runs/training/m1_smollm2_360m_english_facts_binding_mix/20260710T064112Z_m1_smollm2_360m_english_facts_binding_mix_lr5e-5_ep1_bs2_ga8_gc_8ca27779
```

## Evaluation Protocol

The evaluation preserves the protocol used by earlier M1 branches:

- 100-subject pilot
- 500 English facts across five relations
- candidate ranking with mean answer-token log probability
- separate direct and QA-matched prompt runs
- robust overlap defined as top-1 under both prompt formats

## Submitted Jobs

| Job | Checkpoint | Prompt | Final state |
|---:|---|---|---|
| `389946` | `checkpoint-220` | direct | completed |
| `389947` | `checkpoint-220` | QA-matched | completed |
| `389948` | `checkpoint-440` | direct | completed |
| `389949` | `checkpoint-440` | QA-matched | completed |
| `389950` | `checkpoint-660` | direct | completed |
| `389951` | `checkpoint-660` | QA-matched | completed |
| `389952` | `checkpoint-879` | direct | completed |
| `389953` | `checkpoint-879` | QA-matched | completed |

All eight jobs completed `1000/1000` English-plus-Turkish probes without evaluator errors.

## English Gate Results

The table below uses only the 500 rows with `language == "en"`.

| Checkpoint | Direct top1 | Direct top5 | Direct MRR | Direct mean rank | Direct margin | QA top1 | QA top5 | QA MRR | QA mean rank | QA margin | Robust overlap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `checkpoint-220` | `0.012` | `0.054` | `0.0508` | `76.910` | `-4.712` | `0.022` | `0.060` | `0.0607` | `72.150` | `-1.921` | `3/500` |
| `checkpoint-440` | `0.014` | `0.056` | `0.0511` | `76.624` | `-5.035` | `0.014` | `0.048` | `0.0557` | `71.186` | `-1.857` | `3/500` |
| `checkpoint-660` | `0.012` | `0.052` | `0.0496` | `76.516` | `-5.125` | `0.016` | `0.048` | `0.0570` | `70.890` | `-1.852` | `3/500` |
| `checkpoint-879` | `0.012` | `0.052` | `0.0497` | `76.520` | `-5.128` | `0.016` | `0.048` | `0.0569` | `70.912` | `-1.849` | `3/500` |

Best checkpoint views:

- best direct top1: `0.014` (`7/500`) at `checkpoint-440`
- best QA-matched top1: `0.022` (`11/500`) at `checkpoint-220`
- best robust direct-and-QA overlap: `3/500` at every checkpoint
- best direct-plus-QA top1 union: `14/500` at `checkpoint-220`

## Relation Breakdown

At `checkpoint-220`, which has the strongest QA and union result:

| Relation | Direct top1 | QA top1 | Robust overlap |
|---|---:|---:|---:|
| `born_in` | `1/100` | `3/100` | `1/100` |
| `lives_in` | `0/100` | `2/100` | `0/100` |
| `profession` | `0/100` | `2/100` | `0/100` |
| `studied_at` | `3/100` | `2/100` | `1/100` |
| `works_at` | `2/100` | `2/100` | `1/100` |

The robust results are sparse and distributed across only three relations. No robust
`lives_in` or `profession` fact was recovered.

## Comparison Against Prior Branches

| Branch | Best direct top1 | Best QA top1 | Best robust overlap |
|---|---:|---:|---:|
| Original plain SmolLM2 | `0.014` | `0.016` | `3/500` |
| R2 SmolLM2 QA-mix | `0.022` | `0.024` | `5/500` |
| First BIO-QA | `0.016` | `0.022` | `3/500` |
| First ranking objective | `0.014` | `0.018` | `5/500` |
| Binding mix | `0.014` | `0.022` | `3/500` |

Binding mix:

- matches the original plain baseline on direct top1 and robust overlap
- matches first BIO-QA on best QA top1 but has lower best direct top1
- remains below R2 on direct top1, QA top1, and robust overlap
- remains below the first ranking pilot on robust overlap

## Interpretation

This is a negative learned-fact-gate result despite successful optimization.

The training run reduced full-sequence CLM loss to `1.2979` and eval loss to `1.1413`, but
that improvement did not create reliable candidate discrimination. Every mean margin is
still negative. The best QA result occurs at the first checkpoint, direct top1 peaks only
slightly at the second checkpoint, and later training does not improve robust overlap.

The evidence therefore does not support undertraining as the remaining explanation. The
second-generation multi-view biography, multi-form QA, and relation-contrastive data mix
is learnable under CLM loss, but the small model still does not bind and retrieve the target
facts robustly under the thesis gate.

## Decision

```text
Do not promote any binding-mix checkpoint as M1.
```

This branch should remain documented as evidence that richer binding-focused data plus
plain full-sequence CLM is not sufficient for SmolLM2-360M under the current probe gate.
