# M1 workflow archive

These are preserved M1-specific tools, not the default entrypoint for a new study. Start current
work at `scripts/study/run_study.py` and open one file here only when a stage adapter names it.

Filename families provide the local index:

- `*_cross_family*`, `*_provenance_screen*`, `*pythia*`: candidate acquisition and screening;
- `*_retention*`, `*_dose_pareto*`, `*_checkpoint_pareto*`: trajectory and Pareto work;
- `*_form_generalization*`, `*_canonical_form*`, `*relation_v2*`: form and binding controls;
- `prepare_*`, `build_*`, `freeze_*`: materialization and contract preparation;
- `preflight_*`, `smoke_*`, `validate_*`: fail-closed validation;
- `summarize_*`, `resolve_*`, `adjudicate_*`, `gate_*`: analysis and decisions;
- `submit_*.sh`: historical bounded launch wrappers.

The path catalog in `configs/entrypoints/catalog.json` resolves every former flat name.
