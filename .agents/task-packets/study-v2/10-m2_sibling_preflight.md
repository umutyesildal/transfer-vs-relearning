# Luna task packet — m2_sibling_preflight

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m2_sibling_preflight`
Study plan: `df22a4ae934b7b5e`
Stage state: `STUDY`
Authority class: `local_read_only`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m2_sibling_preflight`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Bind M2-A and M2-B to the same selected M1 parent and matched training/evaluation budgets.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v2.md`
- `documentation/178_END_TO_END_EXPERIMENTAL_PLAN_AND_EVALUATION_PROTOCOL_EN.md`
- `configs/studies/m0_to_m2_eval_v1_template.yaml`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m2_preflight.py`
- `tests/study/test_m2_sibling_preflight.py`

## Acceptance criteria

- Both arms resolve the identical M1 checkpoint hash.
- Total tokens, sequence policy, seeds and evaluation bundles are matched.

## Expected handoff outputs

- `stages/m2_sibling_preflight/manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
