# Luna task packet — m0_probing

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::m0_probing`
Study plan: `df22a4ae934b7b5e`
Stage state: `M0`
Authority class: `evaluation`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `m0_probing`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Run the frozen factual access and generation-integrity probes on the identical M0 checkpoint.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/contracts/evaluation/eval-v2.md`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`
- `documentation/evaluation/EVALUATOR_INVENTORY_V1.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/m0_probing.py`
- `tests/study/test_m0_probing_adapter.py`

## Acceptance criteria

- Probe registry hash and complete per-probe rows are preserved.
- EN→EN, TR→EN and TR→TR denominators remain explicit.

## Expected handoff outputs

- `stages/m0_probing/evaluation_manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- This packet prepares or validates an external stage; it does not authorize the evaluation/training itself.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
