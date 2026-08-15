# 141 - Qwen M2/M3 Exploratory Mechanism Analysis Plan

**Date:** 2026-08-03  
**Status:** Analysis plan; exploratory only; no new training authorized  
**Inputs:** Frozen M1/M2/M3 endpoint outputs and aggregate metrics only

## 1. Purpose and interpretation boundary

This plan investigates why seed 42 and seed 43 differ and where the large M1-to-M2/M3 Turkish
retrieval decline is concentrated. It does not modify the frozen primary gate, select a checkpoint,
exclude a seed, redefine the estimand, or authorize a new experiment.

The frozen primary decision remains:

```text
primary_success_criterion_not_met
```

Every output from this plan must be labeled `exploratory` or `post-hoc` and must not be presented as
confirmatory evidence for the original Branch-B causal hypothesis.

## 2. Frozen inputs

Use only these existing outputs:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/assembled_20260802T2315Z/
/vol/tmp2/yesildau/qwen_m2_m3_v1/analysis_v1/metrics_20260802T2315Z/
/vol/tmp2/yesildau/qwen_m2_m3_v1/evaluation_v1/results/
/vol/tmp2/yesildau/qwen_pre_m2_baseline_rtx3090_v1/
```

Create a new versioned exploratory output directory. Never overwrite the frozen assembly,
analysis, or gate directories.

## 3. Required analyses

### 3.1 Seed comparison

- Compare seed-42 and seed-43 state accuracy, M2→M3 changes, and Branch A/B interactions.
- Identify whether seed differences are already present in the M1 bilingual baseline.
- Report effect sizes and confidence intervals descriptively, without treating subgroup intervals
  as new gates.

### 3.2 Relation contribution

- Produce M1/M2/M3 state and paired-change tables by relation.
- Produce Branch A/B interaction tables by relation and direction.
- Identify relations contributing most to the seed-42 versus seed-43 interaction difference.

### 3.3 Prompt form and scaffold

- Compare Forms A/B/C/D.
- Compare direct and QA scaffolds.
- Report direction × form and direction × scaffold patterns for M1, M2-clean, and M3-fact.

### 3.4 Branch and robustness behavior

- Compare Branch A and Branch B arm changes for every direction.
- Compare average top-1 with robust all-cell intersections.
- Check whether a small subset of cells, subjects, or relations drives the aggregate contrast.

### 3.5 M1-to-M2/M3 Turkish decline

- Localize the decline by direction, relation, form, scaffold, frequency, name type, rarity, and
  popularity.
- Compare M2-clean and M3-fact against the corresponding M1 seed baseline.
- Distinguish absolute access loss from descriptive M3 recovery relative to M2-clean.

## 4. Required outputs

Produce a compact reproducible package containing:

- exploratory state tables;
- relation/form/scaffold tables;
- Branch A/B interaction tables;
- robust-intersection comparisons;
- seed-comparison summary;
- decline-localization summary;
- plots only where they clarify a multi-cell pattern;
- a JSON manifest with input hashes, source commit, parameters, and output hashes;
- a Markdown report with explicit `exploratory` labels and unsupported-claim boundaries.

## 5. Stop conditions

Stop and report instead of continuing if:

- any input hash differs from the frozen manifest;
- a result directory would be overwritten;
- a finding would require changing the primary gate or endpoint;
- a new GPU allocation or training job appears necessary;
- an artifact would need to be deleted or moved without approval.

## 6. Completion criterion

The exploratory phase is complete when the new package is reproducible from frozen inputs, its
primary decision is unchanged, all claims are labeled correctly, and Document 00 plus the next
chronological result report point to the package.
