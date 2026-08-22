# Luna task packet — m2a_exact_prefix

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m2a_exact_prefix`
Study plan: `df22a4ae934b7b5e`
Stage state: `M2-A`
Authority class: `evaluation`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m2a_exact_prefix`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Run the unchanged historical exact-prefix supplement on every required M2-A checkpoint.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v2.md`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`
- `configs/studies/m0_to_m2_eval_v1_template.yaml`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/exact_prefix_gate.py`
- `tests/study/test_exact_prefix_gate.py`

## Acceptance criteria

- Every required M2-A checkpoint contains exactly 500 complete probes.
- Missing results or identity drift block branch analysis.

## Expected handoff outputs

- `stages/m2a_exact_prefix/exact_prefix_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
