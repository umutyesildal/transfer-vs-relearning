# M2 OSCAR eval-v2 recovery V1A — terminal result and bootstrap correction

**Date:** 2026-09-05

**Execution status:** `M2_EVAL_V2_COMPLETE`

**Scientific-analysis status:** complete, with the original bootstrap rows superseded by the
prompt-identity correction documented below

**Canonical HU root:** `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a`

## Outcome

The authorized V1A recovery closed the three-model M2 evaluation family at **63/63 complete
scientific states**. There are no missing or failed task results and no active jobs from the wave.
The family consists of 60 M2 checkpoint states, three M1-parent OSCAR completion states and the
existing hash-bound M1 endpoint projection. No training, checkpoint writing, cleanup, deletion or
automatic retry occurred.

| Component | Complete | Expected |
|---|---:|---:|
| M2 checkpoint evaluations | 60 | 60 |
| M1-parent OSCAR completion tasks | 3 | 3 |
| Total scientific states | 63 | 63 |

Jobs were preflight `484057`, canary `484058`, recovery array `484059` and finalizer `484060`.
The finalizer reports `M2_EVAL_V2_COMPLETE`; its generated analysis reports
`M2_EVAL_V2_SCIENTIFIC_ANALYSIS_COMPLETE`.

## Identity and integrity

| Artifact | SHA-256 |
|---|---|
| `control/evaluation_family_result.json` | `c04eff5ba1301f5fcd4a318cc3a88d281e389cd05f542e6f6d569826809bcebf` |
| `control/scientific_analysis.json` | `732c9c23ab795bf3212196d582f8300ca6c02dbf6902c489a1d4ecd6eae6e0ca` |
| `control/submission_manifest.json` | `6c24e6aa806117460de01a1b17b41dd33048b2f434a432f342aba4d5d924cdbc` |
| `control/source_inventory.json` | `90c63f65f54d370dda91eae32d150bea8402704ffb844321ab4046d263bc7c4a` |
| `control/task_matrix.json` | `6d3b8b97f048e1531d2146e2d47626a7cf8475122bb2abf32c124a60536d990d` |
| M1 endpoint projection | `41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462` |

Byte-identical copies of the first two terminal JSON files and compact derived tables are under
`artifacts/evaluations/m2_three_model_oscar_v1/dump/`. Raw per-probe results and model artifacts
remain on HU and were not copied or mutated.

## Endpoint language-modeling and factual-access results

Lower BPB is better. `tr→en` is full-suite top-1 accuracy with `n=4,000` prompts per state.

| Model | M1 OSCAR BPB | M2-A OSCAR BPB | M1 WikiText BPB | M2-A WikiText BPB | M1 tr→en | M2-A tr→en | M2-B tr→en |
|---|---:|---:|---:|---:|---:|---:|---:|
| OLMo | 2.081719 | 1.498948 | 0.687969 | 0.927336 | 23.375% | 9.275% | 11.275% |
| Qwen | 1.456695 | 1.193852 | 0.736614 | 0.944411 | 76.350% | 45.650% | 50.000% |
| SmolLM | 1.546141 | 1.432482 | 0.651458 | 0.946396 | 29.500% | 13.325% | 13.675% |

General Turkish OSCAR adaptation therefore improved the in-domain Turkish BPB gate for all three
models, but M2-A reduced Turkish-prompt/English-answer factual access relative to M1 for every
model. This is the main transfer result: improved Turkish language modeling did not by itself
preserve cross-lingual access to the M1 facts.

## Prompt-identity bootstrap correction

The executed analysis function grouped each subject by `fact_id` in a dictionary. The full suite
contains eight prompt variants for each fact (four forms × direct/QA), so seven variants were
silently overwritten and the retained row depended on CSV order. The terminal JSON is preserved
as historical execution evidence, but its bootstrap point estimates, confidence intervals and the
two bootstrap-derived gate booleans are not the current scientific authority.

The corrected implementation pairs on unique `probe_id`, rejects duplicate probe identities and
averages all 40 `tr_to_en` probes per subject before the unchanged 10,000-draw seed-42 subject
bootstrap. No inference or evaluation was repeated. The correction used the already completed,
hash-bound M1, M2-A and M2-B endpoint per-probe CSVs read-only.

| Model | Transfer M2-A−M1 | 95% CI | Relearning M2-B−M2-A | 95% CI | ≥5 pp gate |
|---|---:|---:|---:|---:|---|
| OLMo | −14.100 pp | [−16.075, −12.050] | +2.000 pp | [+1.500, +2.550] | FAIL |
| Qwen | −30.700 pp | [−33.675, −27.750] | +4.350 pp | [+2.950, +5.775] | FAIL |
| SmolLM | −16.175 pp | [−18.525, −13.850] | +0.350 pp | [+0.050, +0.650] | FAIL |

All three corrected relearning intervals are strictly above zero, but none reaches the frozen
minimum point gain of five percentage points. Consequently the correction changes some individual
bootstrap gate booleans but **does not change the family-level conclusion: no model passes every
primary gate**.

## Qwen relation and prompt robustness

Qwen is the strongest relearning signal. Corrected `tr_to_en` M2-B−M2-A differences are:

| Slice | Gain | 95% CI |
|---|---:|---:|
| `born_in` | +8.625 pp | [+4.750, +12.625] |
| `field_of_study` | +2.375 pp | [+0.500, +4.250] |
| `lives_in` | +0.375 pp | [−5.250, +6.125] |
| `profession` | +5.750 pp | [+2.750, +9.125] |
| `works_in_industry` | +4.625 pp | [+2.625, +6.750] |
| direct scaffold | +5.000 pp | [+3.300, +6.650] |
| QA scaffold | +3.700 pp | [+2.100, +5.350] |

All four prompt forms have positive corrected intervals and gains from +4.1 to +4.5 pp. The
effect is therefore not confined to one wording, although relation breadth is uneven and
`lives_in` is inconclusive.

## Checkpoint trajectory

M2 used ten precommitted update checkpoints (`76, 152, 229, 305, 381, 457, 533, 610, 686, 762`),
approximately every 10% of the fixed 762-update dose. These are dose checkpoints, not 36 M1-style
epochs.

- OSCAR BPB decreases monotonically or near-monotonically for every model and arm.
- Cheap factual top-1 falls from the first to last checkpoint in every arm.
- Qwen M2-B exceeds Qwen M2-A at all ten checkpoints; at the endpoint the cheap-panel difference
  is +3.467 pp.
- OLMo M2-B develops a smaller positive separation; SmolLM has no durable M2-B advantage.
- Exact-prefix remains strongest for Qwen (M2-A 99.2%, M2-B 100.0% at update 762), while OLMo and
  SmolLM decline to roughly 91–93%.

The full 60-row trajectory is `m2_checkpoint_trajectory.csv`. Endpoint relation/form/scaffold
aggregates over all 12,000 full-suite prompts are in `endpoint_relation_form_summary.csv`; the
corrected `tr_to_en` bootstrap and slice intervals are in
`corrected_paired_subject_bootstrap.csv`.

## Primary gate

After the prompt-identity correction:

| Gate | OLMo | Qwen | SmolLM |
|---|---|---|---|
| M2-A OSCAR BPB improvement | PASS | PASS | PASS |
| M2-A WikiText retention | PASS | PASS | PASS |
| M2-A English factual drop ≤5 pp | PASS | PASS | FAIL |
| Relearning point gain ≥5 pp | FAIL | FAIL | FAIL |
| Relearning 95% CI lower bound >0 | PASS | PASS | PASS |
| **All primary gates** | **FAIL** | **FAIL** | **FAIL** |

Qwen is the leading descriptive result, not an automatically selected primary model. Its positive
relearning estimate is statistically separated from zero but remains below the precommitted
minimum effect size. OLMo and SmolLM show smaller positive endpoint differences that are also below
the minimum; SmolLM additionally fails English factual retention.

## Verification and boundary

Focused regression tests covering the shared analysis function and M2 executor pass `20/20` after
the prompt-identity repair. The original terminal JSON is not rewritten. A future canonical HU
corrected-analysis artifact would require a separately bounded CPU-only publication/finalization
step; it would reuse existing result CSVs and require no GPU, model load or inference.

This record authorizes no new evaluation, training, model promotion, cleanup, deletion, retry or
artifact mutation. The immediate local next step is review/commit/publication of this corrected
result layer; any optional figures or thesis prose can be generated from the committed compact
tables without another scientific job.
