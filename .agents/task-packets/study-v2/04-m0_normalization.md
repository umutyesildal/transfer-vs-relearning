# Luna task packet — m0_normalization

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m0_normalization`
Study plan: `df22a4ae934b7b5e`
Stage state: `M0`
Authority class: `local_write`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m0_normalization`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Normalize M0 evaluation and probing into canonical long tables without rescoring.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/evaluation/RESULT_SCHEMA_V1.md`
- `documentation/pipeline/README.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/normalize_state.py`
- `tests/study/test_state_normalizer.py`

## Acceptance criteria

- Canonical tables contain one explicit row for every required observation.
- Missing or failed inputs are never converted to zero.

## Expected handoff outputs

- `stages/m0_normalization/checkpoint_registry.parquet`
- `stages/m0_normalization/metric_observations.parquet`
- `stages/m0_normalization/factual_probe_results.parquet`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
