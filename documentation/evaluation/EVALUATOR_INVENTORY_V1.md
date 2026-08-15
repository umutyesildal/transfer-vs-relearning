# Evaluator inventory v1

**Status:** reviewed local inventory | **As of:** 2026-08-15

## Outcome

The existing evaluation code is reusable. The project needs an integration and parity layer, not a
rewrite. Standard public tasks belong to LM Evaluation Harness; project-specific factual causal
estimands remain in the project evaluator; a normalizer joins both without altering raw artifacts.

## Current implementation map

| Surface | Current evidence | Classification | eval-v1 role |
|---|---|---|---|
| `CausalCandidateEvaluator` | mean/total answer-token log probability, deterministic tie-break, top-1/top-5/MRR, subgroup and relation-binding outputs, manifests and fail-closed resume | reuse with schema adapter | general factual ranking foundation |
| `PreM2FrozenEvaluator` | Forms A–D, direct/QA scaffolds, token NLL, robust intersections, same-subject confusable controls, failure taxonomy | reuse as full factual suite | canonical full factual lane after probe registry freeze |
| `TurkishBridgeEvaluator` and analysis | EN→EN, TR→EN, TR→TR directions and paired subject bootstrap | reuse; rename historical state labels in normalizer only | transfer/relearning contrasts |
| `qwen_m2_m3` metrics | subject bootstrap, paired states, branch interactions, robust intersections | reuse compatible functions | state/arm contrasts without rewriting old results |
| general-capability evaluator | custom token PPL, generic candidate completions, empty/EOS/repetition/diversity/intrusion metrics | split | retain generation integrity; custom PPL becomes parity/sensitivity only |
| corpus PPL script | block-token NLL, token PPL and block bootstrap | repair/retire as primary | historical compatibility and parity diagnostics only |
| preparation/Slurm scripts | frozen historical namespaces, gates and recovery logic | retain with history | not the new canonical pipeline |
| `summarize_evaluation.py` | copies selected JSON summaries | replace for new work | superseded by typed long-form normalizer |

## Why custom PPL is not the new primary

The current custom scorer concatenates documents with EOS, splits non-overlapping token blocks and
does not score the first token of each block. It reports tokenizer-dependent token PPL and does not
produce canonical word PPL, byte PPL or bits per byte. Those results remain valid for their frozen
historical contracts, but new retention uses official rolling likelihood and byte-normalized
metrics. A bounded parity study will quantify the difference instead of rewriting old numbers.

## Metrics already scientifically usable

- mean answer-token log probability as the primary candidate rank;
- total answer-token log probability as a length-sensitive sensitivity analysis;
- deterministic top-1 accuracy and ranking margins;
- relation/form/scaffold breakdowns and worst-cell reporting;
- robust fact-level intersections;
- same-subject relation-swap controls;
- paired subject bootstrap for matched state contrasts;
- lexical-empty, early-EOS, repetition, distinct-n and synthetic-subject intrusion diagnostics;
- model, tokenizer, dataset, runtime and progress manifests.

Exact-prefix generation remains secondary and is used only where its prompt, normalization and
success rule are explicitly frozen.

## Repairs required before freeze

1. Bind every raw result to `eval-v1`, state, parent, seed and checkpoint identity.
2. Add a harness runner in a dedicated locked environment and preserve its native result JSON.
3. Normalize both lanes into the schema in [`RESULT_SCHEMA_V1.md`](RESULT_SCHEMA_V1.md).
4. Reconcile official WikiText rolling counts with the historical block scorer.
5. Freeze cheap factual probe IDs and a full-suite registry hash.
6. Make partial, failed and `NOT_RUN` rows explicit; never impute missing scores.
7. Add identity, parity, resume and duplicate-output tests.

## Historical handling

Old task names, thresholds and outputs stay attached to the contract that produced them. In
particular, the historical token-PPL ratio limit of `1.25` is not silently transferred to official
WikiText BPB. Compatible old evidence may be normalized with a `historical_contract` label, but raw
files and original interpretation remain unchanged.
