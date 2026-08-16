# Luna task packet — m1_evaluation

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v1::m1_evaluation`
Study plan: `74edcc978b9011e6`
Stage state: `M1`
Authority class: `evaluation`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m1_evaluation`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Apply the unchanged eval-v1 standard bundle to every required M1 trajectory point.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v1.md`
- `configs/evaluation/eval_v1_registry.yaml`
- `documentation/pipeline/README.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m1_evaluation.py`
- `tests/study/test_m1_evaluation_adapter.py`

## Acceptance criteria

- Parent and every required epoch have explicit complete or failed status.
- BPB, ΔBPB and companion PPL quantities use the same frozen parent.

## Expected handoff outputs

- `stages/m1_evaluation/evaluation_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
