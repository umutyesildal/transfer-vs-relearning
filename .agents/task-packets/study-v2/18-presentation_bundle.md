# Luna task packet — presentation_bundle

Packet ID: `transfer-vs-relearning-m0-to-m2-eval-v2::presentation_bundle`
Study plan: `df22a4ae934b7b5e`
Stage state: `STUDY`
Authority class: `local_write`
Packet mode: `adapter_implementation_or_validation`

## Objective

Prepare or validate the local registered adapter for stage `presentation_bundle`. Do not execute the
scientific stage from this packet.

Scientific stage objective: Generate thesis-ready tables, plot data, figures and metadata-complete captions from canonical rows.

## Context budget

Read only the standard agent control files, this packet, and these task-specific files:

- `documentation/pipeline/README.md`
- `documentation/evaluation/RESULT_SCHEMA_V1.md`

## Allowed paths

- `src/transfer_vs_relearning/study/adapters/presentation.py`
- `tests/study/test_presentation_adapter.py`

## Acceptance criteria

- Every figure is generated only from canonical complete rows.
- Captions include model/data revisions, seeds, batch, sequence and precision identity.

## Expected handoff outputs

- `stages/presentation_bundle/presentation/figure_manifest.json`
- `stages/presentation_bundle/presentation/captions.json`

## Stop conditions

- Do not broaden the task or read the chronological archive unless this packet names a file.
- Do not commit, push, delete, clean, download, use HU/SSH, or submit Slurm.
- Stop if completion requires evaluation, training, network, HU/SSH, Slurm, or new scientific judgment.

## Handoff

Return the structured worker report with exact changed paths, tests, unmet criteria, and the single
next blocker. Project state lives in `documentation/current/PROJECT_STATE.yaml`, not chat memory.
