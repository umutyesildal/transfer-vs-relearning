# Luna task packet — m2a_evaluation_probing

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v1::m2a_evaluation_probing`
Study plan: `74edcc978b9011e6`
Stage state: `M2-A`
Authority class: `evaluation`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m2a_evaluation_probing`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Apply unchanged eval-v1 standard and factual probe bundles to M2-A.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v1.md`
- `configs/evaluation/eval_v1_registry.yaml`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m2a_evaluation.py`
- `tests/study/test_m2a_evaluation_adapter.py`

## Acceptance criteria

- Transfer contrasts remain paired to the same M1 observations.
- Turkish and English retention/manipulation metrics are complete.

## Expected handoff outputs

- `stages/m2a_evaluation_probing/evaluation_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
