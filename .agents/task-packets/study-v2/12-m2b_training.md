# Luna task packet — m2b_training

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m2b_training`
Study plan: `df22a4ae934b7b5e`
Stage state: `M2-B`
Authority class: `training`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m2b_training`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Train the matched Turkish factual re-exposure arm from the same frozen M1 parent.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md`
- `documentation/pipeline/README.md`
- `documentation/contracts/evaluation/eval-v2.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m2b_training.py`
- `tests/study/test_m2b_training_adapter.py`

## Acceptance criteria

- Re-exposure rows and matched non-factual budget have frozen identities.
- Full epoch trace and model-only snapshots are preserved.

## Expected handoff outputs

- `stages/m2b_training/training_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
