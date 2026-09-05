# M2 results website and thesis package — implementation result

**Date:** 2026-09-05  
**Status:** complete; verified; ordinary non-force push confirmed
**Execution boundary:** local derived reporting only; no HU/GPU/model/evaluation/training

## Delivered

Three GPT-5.6 Luna workers implemented the frozen reporting plan with disjoint file ownership.

### Validated web-data layer

- builder: `scripts/evaluation/build_results_explorer_data.py`;
- artifact: `tools/m0-dashboard/data/results_explorer_data.json`;
- schema: `results-explorer-data-v1`;
- artifact SHA-256: `3b2249298d01f8a601afa3a66f6bca29cb9469dbeb43c065dd2f45375deba7e9`;
- deterministic nine-source input identity:
  `647aa45c4f1fb170c40a62d5ebee81ca3cd404738851d3dcab99f4374522be22`.

The builder exact-hash-checks all nine compact sources and validates 111 M1 trajectory rows, 60 M2
checkpoint rows, 27 state endpoints, 66 endpoint breakdown rows, 39 corrected-bootstrap rows and
15 gate rows. It rejects duplicates, missing required values and inconsistent gate summaries.

### Existing website extended

The dependency-free bilingual application under `tools/m0-dashboard/` now has five views:

1. M0 → M1 → parallel M2-A/M2-B overview;
2. corrected transfer/relearning intervals, +0.05 threshold and gate ledger;
3. checkpoint trajectories with model/arm/metric filters;
4. relation, prompt-form and scaffold diagnostics;
5. source hashes, glossary and historical-bootstrap warning.

The browser does no scientific joining or winner selection. It explicitly states that M2-A and
M2-B are sibling arms from the same M1 parent, checkpoint factual top-1 has `n=1,500`, endpoint
full-suite top-1 has `n=12,000`, and Qwen's descriptive +4.35 pp relearning estimate does not pass
the frozen +5 pp point-gain gate.

### Thesis exports

- builder: `scripts/evaluation/build_m2_thesis_exports.py`;
- outputs: `paper/transfer_or_relearning_wip/derived_m2_exports/`;
- export manifest SHA-256:
  `d75af6f246c3cd396cb3d765718ebaccc45b9b89de74b18e5c9eefdbdd9f161d`.

The derived package contains canonical CSV/Markdown/SVG versions of the primary forest plot,
endpoint state comparison, dose trajectories, relation breakdown, form breakdown and primary gate
table, plus a scientific summary and per-output hash manifest. Every export carries the same input
manifest identity and uses the corrected `probe_id` bootstrap only.

## Verification

- focused data/export tests: 5/5 PASS;
- both Python builders compile;
- JavaScript syntax check PASS;
- all exported SVG files parse as XML;
- YAML/diff checks PASS;
- real localhost browser render verified for Overview, Primary Result, Trajectories and Provenance;
- Turkish/English toggle verified;
- corrected values and confidence intervals verified in the rendered UI;
- status strip shows the deterministic manifest identity rather than a pending placeholder;
- no HU request, model load, inference, evaluation, training, cleanup or deletion occurred.

The broader documentation control-plane run produced 12 passes and three pre-existing failures:
its frozen test expectations still name an older HU dependency commit, require `AGENTS.md` to be at
most 250 lines although HEAD already has 265, and require two readiness mappings that were already
different at HEAD. Neither the test nor those unrelated historical fields were changed as part of
this reporting task.

The website and thesis artifacts are derived reporting products. They do not alter the terminal
scientific conclusion: no model passes all primary gates and no automatic primary model is selected.

## Publication closure

The user performed the ordinary non-force push and the remote branch was subsequently verified:

- remote: `https://github.com/umutyesildal/transfer-vs-relearning`;
- branch: `agent/m2-three-model-vngrs-d0`;
- published commit: `677259972bec2b4857800d53b6e8253b3cec68f2`;
- remote HEAD verification: exact match.
