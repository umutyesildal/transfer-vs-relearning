# Luna task packet — m1_training

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v1::m1_training`
Study plan: `74edcc978b9011e6`
Stage state: `M1`
Authority class: `training`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m1_training`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Train the frozen M1 recipe from the exact M0 parent with epoch trace and snapshots enabled.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/pipeline/README.md`
- `configs/training/eval_v1_olmo_epoch_tracked_template.yaml`
- `documentation/contracts/evaluation/eval-v1.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m1_training.py`
- `tests/study/test_m1_training_adapter.py`

## Acceptance criteria

- Training identity, hyperparameters, epoch trace and snapshot hashes are complete.
- No M1 evaluation result is used to mutate the frozen recipe.

## Expected handoff outputs

- `stages/m1_training/training_manifest.json`
- `stages/m1_training/training_trace_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
