# Luna task packet — branch_analysis

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v1::branch_analysis`
Study plan: `74edcc978b9011e6`
Stage state: `STUDY`
Authority class: `local_write`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `branch_analysis`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Normalize both M2 branches and compute only precommitted transfer/relearning contrasts.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v1.md`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`
- `documentation/178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/branch_analysis.py`
- `tests/study/test_branch_analysis_adapter.py`

## Acceptance criteria

- M2-A minus M1 and M2-B minus M2-A paired contrasts are explicit.
- Incomplete required rows block aggregate conclusions.

## Expected handoff outputs

- `stages/branch_analysis/branch_contrasts.parquet`
- `stages/branch_analysis/analysis_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
