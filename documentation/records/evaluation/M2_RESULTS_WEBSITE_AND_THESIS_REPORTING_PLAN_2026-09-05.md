# M2 results website and thesis-reporting plan

**Date:** 2026-09-05  
**Status:** implemented locally and verified; no HU/GPU work used
**Target:** extend the existing dependency-free `tools/m0-dashboard/` application

## 1. Goal and boundary

Turn the completed M0, M1 and OSCAR M2 result layers into one bilingual, thesis-ready explorer and
an exportable figure/table package. The website must communicate the two precommitted M2
estimands without promoting a descriptive winner:

- **transfer:** M2-A minus M1 on `tr_to_en` factual access;
- **relearning:** M2-B minus M2-A on `tr_to_en` factual access.

This is a local derived-reporting task. It does not need or authorize HU access, Slurm, GPU, model
loading, inference, evaluation, training, corpus access, cleanup or deletion. Missing values must
remain missing and the historical `fact_id` bootstrap must remain preserved but visibly
superseded.

M2-A and M2-B must always be drawn as parallel sibling arms initialized from the same M1 parent.
M2-B was not trained from M2-A. No artificial overall score may combine factual accuracy, BPB,
exact-prefix and capability metrics.

## 2. Existing application to retain

The current site already provides the correct foundation:

- `tools/m0-dashboard/index.html`: three-page shell and M0/M1/M2 state selector;
- `tools/m0-dashboard/app.js`: bilingual labels, metric semantics and dependency-free rendering;
- `tools/m0-dashboard/styles.css`: responsive visual system;
- `tools/m0-dashboard/serve.py`: repository-root static server;
- `tools/m0-dashboard/README.md`: local launch instructions.

The present limitation is architectural rather than visual: `app.js` loads only
`m0_metrics.json`, and `hasCurrentData()` hard-codes M0 as the sole available state. The extension
will preserve the static/no-build character while replacing that special case with a versioned
multi-stage web-data manifest.

## 3. Frozen source inputs

The builder will read only the compact, Git-retained artifacts below and record their SHA-256
values in the generated web-data manifest.

| Stage | Input | SHA-256 |
|---|---|---|
| M0 | `artifacts/evaluations/m0_three_model_v1/dump/m0_metrics.json` | `859b598fdd3509d6e11e5cbf3f9662bc66accd58291bc635aad028185e1bdbbd` |
| M1 | `artifacts/evaluations/m1_three_model_v1/dump/m1_metrics.json` | `41c2f2c6b722fc25ac48af278f1b318acc5e743b3c48d649fe26259848080462` |
| M1 | `artifacts/evaluations/m1_three_model_v1/dump/m1_trajectory.csv` | `0cf33dca248d35c8c6f49bd8856d2ef801d3cfef522f59bde099a9aef72e269b` |
| M1 | `artifacts/evaluations/m1_three_model_v1/dump/m0_m1_comparison.csv` | `ee0a9f0bc21e8c360c8fc0b9971cd3be3ff76120bc89c55dee60c356a670e68a` |
| M2 | `artifacts/evaluations/m2_three_model_oscar_v1/dump/evaluation_family_result.json` | `c04eff5ba1301f5fcd4a318cc3a88d281e389cd05f542e6f6d569826809bcebf` |
| M2 historical | `artifacts/evaluations/m2_three_model_oscar_v1/dump/scientific_analysis.json` | `732c9c23ab795bf3212196d582f8300ca6c02dbf6902c489a1d4ecd6eae6e0ca` |
| M2 | `artifacts/evaluations/m2_three_model_oscar_v1/dump/m2_checkpoint_trajectory.csv` | `2e687bb24befc947ec21fa1e0c9040b27e6be2a3dff6da8ea6ab3e30b9e9a18a` |
| M2 | `artifacts/evaluations/m2_three_model_oscar_v1/dump/endpoint_relation_form_summary.csv` | `4502af97b0878b75b472ada774a6a73c0fe5c9d21b4856702148df09d41d7e9d` |
| M2 canonical correction | `artifacts/evaluations/m2_three_model_oscar_v1/dump/corrected_paired_subject_bootstrap.csv` | `e16610d1af87fea1f42a13ae1fcc2bc1e80ee78fe7343f91576858505563750d` |

The HU-published corrected analysis remains bound by SHA-256
`7427b11f2f4fd2f5c191b23f6836d97a151a00fdbce755cd545a6aa4982b5043` and is documented in
`M2_EVAL_BOOTSTRAP_CORRECTION_EXECUTION_RESULT_2026-09-05.md`.

## 4. Proposed information architecture

### Page 1 — Study overview

- four-state timeline: M0 → M1 → parallel M2-A / M2-B;
- exact model cohort: OLMo, Qwen and SmolLM;
- completion cards: M1 `111/111`, M2 `63/63`, M2 training checkpoints `60/60`;
- plain-language explanation of transfer versus relearning;
- prominent terminal conclusion: no model passes all primary gates.

### Page 2 — M2 primary result

- gate table for every model and every frozen criterion;
- forest/interval chart for transfer and relearning, including zero and the +0.05 relearning
  threshold;
- endpoint state comparison for M1, M2-A and M2-B across `en_to_en`, `tr_to_en` and `tr_to_tr`;
- explicit visual distinction between “CI above zero” and “point gain at least +0.05”;
- Qwen labelled strongest descriptive relearning effect, never “selected primary model”.

### Page 3 — Training trajectories

- model and arm filters;
- ten-checkpoint curves over dose/update for cheap factual top-1, OSCAR BPB, trwiki BPB,
  WikiText BPB and exact top-1;
- fixed denominator note: checkpoint factual top-1 uses 1,500 probes and must not be compared as
  if it were the endpoint 12,000-probe full suite;
- optional M1 epoch trajectory toggle using the existing M1 compact trajectory.

### Page 4 — Diagnostic breakdown

- endpoint relation breakdown for the five relations;
- prompt-form breakdown for forms A–D;
- scaffold/language-direction breakdown;
- M2-B minus M2-A view beside absolute M2-A/M2-B accuracy;
- table download using the exact compact CSV, not rounded screen values.

### Page 5 — Provenance and reading guide

- source path, SHA-256, row count and semantic role for every input;
- warning that the executed `fact_id` bootstrap is historical and superseded;
- canonical correction identity: `probe_id`, 100 subjects, eight prompt variants, 10,000 draws,
  seed 42;
- metric glossary for BPB, exact top-1, full-suite top-1, transfer and relearning;
- limitations: one seed, one frozen OSCAR subset, threshold-bound primary gate and no automatic
  primary-model selection.

## 5. Derived data layer

Add a deterministic Python builder, for example
`scripts/evaluation/build_results_explorer_data.py`, that:

1. verifies every expected source SHA before parsing;
2. validates model/arm/state vocabularies, denominators, 60 M2 trajectory rows, 66 endpoint
   breakdown rows and 39 corrected bootstrap rows;
3. refuses duplicate model/state/metric and duplicate bootstrap subset keys;
4. emits one compact versioned file under `tools/m0-dashboard/data/` containing overview, gates,
   state endpoints, trajectories, breakdowns, provenance and bilingual semantic metadata;
5. derives displayed deltas from source values and checks them against the frozen correction;
6. writes deterministically so a second build is byte-identical.

The browser must not perform scientific joins or select a winner. It may filter, sort and format
already validated rows. CSV parsing and metric semantics remain in the builder/tests, not scattered
through UI event handlers.

## 6. Implementation sequence

### Phase A — data contract and tests

- freeze the web-data schema and allowed metric vocabulary;
- implement the builder and fixture-level validation tests;
- add golden assertions for the six corrected all-subject estimands and all model gate booleans;
- assert deterministic rebuild and source-hash closure.

### Phase B — extend the existing UI

- replace the M0-only loader and hard-coded availability check;
- keep Turkish/English switching, responsive layout and zero-dependency serving;
- add the five pages above with accessible SVG/CSS charts, tooltips and table fallbacks;
- encode colour by model and line/shape by state or arm so meaning is not colour-only.

### Phase C — thesis export

- create a deterministic export command for thesis figures/tables under a derived output folder;
- use identical titles, units, rounding and captions in the website and thesis assets;
- export at minimum: primary forest plot, endpoint state comparison, dose trajectories, relation
  breakdown, form breakdown and gate table;
- record each export's input-manifest hash.

### Phase D — verification and documentation

- unit-test the builder and DOM/data helpers;
- run a local HTTP smoke test for every page and both languages;
- verify narrow/mobile and desktop layouts, keyboard navigation and no-JavaScript table fallback;
- compare every headline number manually against the compact artifacts and the terminal result
  record;
- update `tools/m0-dashboard/README.md`, `documentation/current/START_HERE.md`, `STATUS.md`,
  `PROJECT_STATE.yaml` and `AGENT_BRIEF.yaml` only after verification.

## 7. Acceptance criteria

The package is complete only if:

- M0, M1, M2-A and M2-B all show observed data where a compact source exists;
- the M2 completion count is 63/63 and no missing value renders as zero;
- the headline corrected values exactly equal OLMo `-0.141/+0.020`, Qwen
  `-0.307/+0.0435`, SmolLM `-0.16175/+0.0035`, with their exact CIs;
- all three `all_primary_gates_pass` values render false;
- the +0.05 threshold and zero line are visible and semantically distinct;
- the historical bootstrap cannot be mistaken for the canonical correction;
- source hashes are visible and the generated manifest is reproducible;
- browser console/network checks show no HU or external request;
- the same validated dataset feeds both website and thesis exports.

## 8. Recommended next action

Implement Phase A and Phase B together as one local, reviewable website change, then validate the
rendered result before producing thesis exports. This avoids freezing figures before the common
data contract and UI semantics are proven. No scientific rerun should be scheduled from this plan.

This sequence was completed on 2026-09-05. The implementation and verification evidence is in
`M2_RESULTS_WEBSITE_AND_THESIS_PACKAGE_IMPLEMENTATION_RESULT_2026-09-05.md`.
