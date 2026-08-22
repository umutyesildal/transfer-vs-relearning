# M0 eval-v2 metric-source audit v1b result — 2026-08-22

**Scope:** one authorized read-only v1b source-adapter correction wave

**Contract SHA-256:** `5f3009709c729cf9af8c37ccfe8f945895539f3b591a4ac7ea10068698a40764`

**Config SHA-256:** `974d10defb5fa2660a92c1a83eefa005294bb702804ef5f374a116c7ff17e700`

**Implementation commit on HU:** `9048d57`

**Operator module SHA-256:** `3de614b9ffe3b4a8a91a2091c5387c0992a409233dc09d3eb7b5cb9792dbaf0d`

## Result

The v1b source adapter correctly accepted the three historical exact-prefix lanes and traversed all
24 hash-verified source rows. It then stopped with a fail-closed metric-schema report:

```text
status: audit_blocked
source_row_count: 24
metric_observation_candidate_count: 3
expected_metric_observation_count: 42
```

Only the three exact-prefix primary ranking observations were uniquely available under the v1b
rules. No normalization root was created, no source artifact was mutated, and no model, inference,
rescoring or training action occurred.

## Read-only schema findings

The declared artifacts expose structured fields that are more specific than the generic v1b leaf
aliases:

- WikiText: lm-eval `results.wikitext` with `word_perplexity,none`, `byte_perplexity,none` and
  `bits_per_byte,none`.
- BLiMP: lm-eval aggregate `results.blimp.acc,none`.
- English capability: `results.hellaswag.acc_norm,none`.
- Turkish capability: `results.turblimp_core.acc_norm,none`.
- Turkish perplexity: the summary whose top-level
  `primary_cross_tokenizer_metric` is `bits_per_byte`, with `bits_per_byte`, `byte_perplexity`
  and source `perplexity` fields. The current M0 lane is the documented `trwiki-20260601`
  cross-domain control; no primary in-domain Turkish held-out corpus is present in this lane.
- Factual access: JSON summary `top1` and `probes`, plus `summary_by_relation_form.csv` and
  `all_cell_intersections.csv`. The robust eight-cell intersection is tabular evidence and is
  not a JSON leaf.
- Generation integrity: `summary_metrics.json.generation.empty_generation_count`,
  `prompt_count` and `mean_repeated_3gram_fraction`.
- Exact-prefix: unique top-level `primary_mean_logprob_top1_accuracy` (already handled by v1b).

The v1b global leaf matcher intentionally did not infer these path-specific metrics. The resulting
classification is:

```text
blocked_by_path_specific_metric_schema_and_tabular_factual_evidence
```

## Required next correction

A v1c adapter must bind exact file/JSON paths and explicit CSV aggregations, preserve denominator
metadata, and keep the missing primary Turkish held-out corpus explicit rather than converting it to
zero. It must pass a 24-row / 42-observation synthetic fixture before any new HU audit. A new exact
SHA-bound authorization is required for publication and execution of that correction.
