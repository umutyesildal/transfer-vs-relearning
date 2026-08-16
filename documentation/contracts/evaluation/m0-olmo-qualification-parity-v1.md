# M0 OLMo qualification parity v1

**Status:** `prepared / not executable` | **Owner:** project | **Created:** 2026-08-16  
**Parent:** `m0-olmo-qualification-v1`

## Purpose

This bounded test-only wave resolves exactly two open qualification checks from the completed OLMo
seven-lane bundle:

1. `wikitext_count_result_and_heading_parity`; and
2. `turblimp_16_subtask_macro_parity`.

It cannot produce a scientific M0 score and cannot freeze eval-v1 by itself. A PASS only removes
these two named verification blockers. Dataset revisions, Pile-10k cadence, TurkishMMLU disposition,
scientific factual registries, numerical margins and exact checkpoint bindings remain separate
eval-v1 freeze requirements.

## Frozen semantics at preparation time

The source bundle is the immutable qualification-v8 namespace. The completed targeted recovery is
used only as evidence that the full seven-lane bundle is available; the parity computation reads
the original WikiText and TurBLiMP lane artifacts bound by their lane-result SHA-256 values.

WikiText canonical parity recomputes, from every logged sample:

- the upstream detokenized target;
- the upstream word denominator from the original `page` string;
- the UTF-8 byte denominator from the original `page` string;
- word perplexity, byte perplexity and bits-per-byte from the summed rolling
  log-likelihood; and
- result/sample counts and exact document IDs.

The absolute floating-point parity tolerance is `1e-12`. The predefined heading sensitivity maps
each `= heading =` line to a same-depth Markdown heading such as `# heading`, evaluates the same two
documents and recomputes its own transformed denominators. Its numeric deltas are descriptive only:
there is no outcome-aware magnitude threshold.

TurBLiMP parity binds all 16 upstream subtasks in their emitted order and exactly two logged samples
per subtask. Per-example `acc` is recomputed from the two raw choice log-likelihoods. Decision metric
`acc_norm` is recomputed after dividing each choice log-likelihood by its candidate sentence's UTF-8
byte length. Per-subtask means and the unweighted 16-subtask macro are then compared with the Harness
result. The duplicated upstream `aggregate_metric_list` key and its effective last-value-wins
`acc_norm` meaning must both be recorded; no silent YAML repair is permitted.

## Execution boundary

The user authorized continuing this sequence on 2026-08-16. Execution nevertheless remains
fail-closed until a first implementation commit, exact implementation-file hashes and a frozen
companion config are committed and published. The executable wave will use:

- one fresh root: `/vol/tmp2/yesildau/eval_v1_m0_olmo_qualification_parity_v1`;
- the pinned lm-eval v0.4.12 environment and exact OLMo manifest;
- a CPU structural recomputation before any GPU submission;
- one V100-32GB heading-sensitivity job after a Slurm `--test-only` gate and a 16 GiB runtime
  free-memory gate; and
- one `afterany` CPU finalizer that preserves PASS or blocked evidence.

HU home and every prior evidence root remain read-only. No training, scientific M0 evaluation,
corpus work, cleanup, deletion, threshold change or eval-v1 freeze is authorized by this contract.

## Required outputs

- `parity_plan.json`;
- `structural_parity.json`;
- `gpu_route_selection.json`;
- `heading/gpu_memory_preflight.json`;
- raw heading Harness result and logged samples;
- `heading_sensitivity.json`;
- `parity_results.jsonl`;
- `parity_manifest.json`;
- `parity_result.json`; and
- `final_inventory.json`.

## Freeze blockers

- implementation commit not bound;
- exact implementation-file hashes not bound;
- companion config not frozen and execution-authorized.
