# Luna task packet — m1_probing

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m1_probing`
Study plan: `df22a4ae934b7b5e`
Stage state: `M1`
Authority class: `evaluation`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m1_probing`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Apply the unchanged factual and integrity probe bundle to required M1 trajectory points.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v2.md`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m1_probing.py`
- `tests/study/test_m1_probing_adapter.py`

## Acceptance criteria

- Fact access, robust intersection and failure taxonomy rows are complete.
- Probe identities match M0 exactly where comparisons require pairing.

## Expected handoff outputs

- `stages/m1_probing/evaluation_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
