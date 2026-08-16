# Luna task packet — contract_preflight

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v1::contract_preflight`
Study plan: `74edcc978b9011e6`
Stage state: `STUDY`
Authority class: `local_read_only`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `contract_preflight`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Validate exact study, model, corpus, evaluation and output identities before any scientific work.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/current/PROJECT_STATE.yaml`
- `documentation/contracts/evaluation/eval-v1.md`
- `configs/evaluation/eval_v1_registry.yaml`
- `configs/studies/m0_to_m2_eval_v1_template.yaml`

## Allowed paths

- `src/transfer_vs_relearning/study/**`
- `tests/test_full_study_workflow.py`

## Acceptance criteria

- Every frozen identity is present and placeholder-free.
- M2-A and M2-B share the same M1 parent, budget policy and eval contract.

## Expected handoff outputs

- `stages/contract_preflight/manifest.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
