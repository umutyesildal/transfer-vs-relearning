# Luna task packet — m1_checkpoint_selection

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m1_checkpoint_selection`
Study plan: `df22a4ae934b7b5e`
Stage state: `M1`
Authority class: `local_write`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m1_checkpoint_selection`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Apply only the precommitted M1 checkpoint rule to normalized M1 evaluation and probing evidence.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v2.md`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`
- `documentation/current/PROJECT_STATE.yaml`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m1_selection.py`
- `tests/study/test_m1_selection_adapter.py`

## Acceptance criteria

- Selection is deterministic and uses no outcome-aware threshold changes.
- The selected checkpoint manifest and rejection reasons are preserved.

## Expected handoff outputs

- `stages/m1_checkpoint_selection/selection_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
