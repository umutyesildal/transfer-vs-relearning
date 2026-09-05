# M2 OSCAR three-model terminal result dump

This directory contains the compact, repository-safe result layer for the completed M2 OSCAR
evaluation family. The canonical raw result root remains immutable on HU at
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a`.

- `evaluation_family_result.json`: byte-identical copy of the terminal 63-state finalizer output.
- `scientific_analysis.json`: byte-identical copy of the precommitted endpoint/gate analysis.
- `m2_checkpoint_trajectory.csv`: compact values derived read-only from the 60 checkpoint summary
  files. `factual_top1` is the 1,500-probe cheap panel and is not interchangeable with the
  12,000-probe endpoint full suite.
- `endpoint_relation_form_summary.csv`: update-762 full-suite aggregation over all three language
  directions. Relation rows have `n=2,400`, form rows `n=3,000`, and scaffold rows `n=6,000` per
  model/arm.
- `corrected_paired_subject_bootstrap.csv`: prompt-identity-preserving correction of the endpoint
  `tr_to_en` bootstrap. The terminal `scientific_analysis.json` is retained byte-identically but
  its bootstrap rows are superseded because the executed implementation collapsed eight prompt
  variants to the last row for each `fact_id`.

The exact source hashes and interpretation are recorded in
`documentation/records/evaluation/M2_EVAL_RECOVERY_V1A_TERMINAL_RESULT_2026-09-05.md`.
