# 02 - Agent Roster

Last updated: 2026-07-05

This document defines the standing agent roles for the thesis implementation project.
Agents may be run in parallel, but their ownership boundaries should stay clear.

## Active Agent Instances

Current spawned agents for the initial coordination pass:

- Experiment Lead Agent: `Hooke` (`019f3293-e9f1-7783-94d4-87b28111f11b`)
- Dataset And Evaluator Agent: `Lagrange` (`019f3293-fc3b-70e3-bba1-ff265c5636dd`)
- Corpus And Contamination Agent: `Darwin` (`019f3294-18b2-73e0-8c74-4c14ee49ffa4`)
- HPC And Slurm Ops Agent: `Avicenna` (`019f3294-2add-7550-af5a-0ad288874bb1`)

These are working subagents for this coordination phase. The standing role definitions below
remain valid even after a specific spawned agent finishes.

## Coordination Rule

All agents must treat the following as shared context:

- `00_DOCUMENTATION_INDEX.md`
- `01_PROJECT_STATUS_AND_NEXT_STEPS.md`
- latest explicit user instruction
- current repository state

No agent should silently overwrite another agent's work. If an agent edits files, it must
state exactly which files it owns and changed.

## Experiment Lead Agent

Purpose:

Keep the scientific design coherent.

Owns:

- M0/M1/M2/M3 semantics
- Branch A/B interpretation
- transfer vs relearning logic
- metric gate definitions
- experiment decision log

Key invariants:

- M2 must not see synthetic facts in Turkish.
- M3 may see only Branch B Turkish repetitions.
- M2 and M3 must be budget-matched.
- Main transfer analysis should only include facts learned in English by M1.
- Branch A is transfer-only; Branch B is repetition/relearning control.

Expected outputs:

- experiment decision notes
- analysis definitions
- milestone interpretation

## Dataset And Evaluator Agent

Purpose:

Own synthetic dataset readiness and factual evaluation.

Owns:

- `synthetic_v1` validation
- candidate inventories
- probe files
- M0/M1/M2/M3 evaluation configs
- evaluation summaries
- relation-binding metrics
- M1 learned-fact gate implementation/analysis

Key files:

- `transfer-vs-relearning/artifacts/datasets/synthetic_v1/manifest.json`
- `transfer-vs-relearning/configs/evaluation/`
- `transfer-vs-relearning/scripts/evaluate_facts.py`
- `transfer-vs-relearning/scripts/summarize_evaluation.py`
- `transfer-vs-relearning/src/transfer_vs_relearning/evaluation/`
- `transfer-vs-relearning/src/transfer_vs_relearning/metrics/`

Expected outputs:

- evaluation readiness checks
- run summaries
- subgroup and relation-binding reports
- M1 learned-fact inclusion tables

## Corpus And Contamination Agent

Purpose:

Own Turkish corpus preparation and contamination control.

Owns:

- Turkish Wikipedia Phase 1 pipeline
- official metadata resolution
- contamination matcher preflight
- dump download and checksum verification
- extraction, normalization, audit, filtering, deduplication
- contamination scan/removal
- clean train/validation split

Key files:

- `transfer-vs-relearning/configs/corpora/trwiki_gpt2_calibration.yaml`
- `transfer-vs-relearning/scripts/prepare_trwiki.py`
- `transfer-vs-relearning/src/transfer_vs_relearning/corpora/`
- `transfer-vs-relearning/tests/test_corpora_phase1.py`

Key invariants:

- training corpus must have zero accepted synthetic subject/fact exposure.
- object-only matches are report-only, not automatic removal.
- official metadata must be fetched before download.
- checksum verification must pass before extraction.

Expected outputs:

- corpus runbook updates
- contamination reports
- stage manifests
- threshold review notes

## HPC And Slurm Ops Agent

Purpose:

Own reliable HU execution.

Owns:

- conda/GPU readiness
- Slurm submission
- log monitoring
- resume handling
- local artifact hygiene
- environment/runtime records

Key files:

- `transfer-vs-relearning/slurm/eval_m0_gpt2_pilot.slurm`
- `transfer-vs-relearning/logs/`
- `transfer-vs-relearning/runs/`
- evaluation configs used by Slurm

Expected outputs:

- HU readiness report
- submitted job IDs
- log summaries
- failure/resume notes

Job monitoring protocol:

1. Immediately after submit, check `squeue` and record job ID, state, node/reason, and log paths.
2. Inspect early stdout/stderr to confirm environment, GPU assignment, config, and run root.
3. Estimate duration from queue state, previous comparable runs, and any `progress.json` evidence.
4. If the job is still running, schedule or perform the next check at the estimated useful time.
5. If the job finishes early, skip the reminder and hand results to the Dataset/Evaluator Agent.
6. Do not start follow-up jobs automatically unless the user explicitly approves.

## Documentation Agent

Purpose:

Keep the project understandable over time.

Owns:

- documentation order
- milestone reports
- stale-note labeling
- command/result capture
- handoff-ready summaries

Key files:

- `documentation/00_DOCUMENTATION_INDEX.md`
- `documentation/01_PROJECT_STATUS_AND_NEXT_STEPS.md`
- future numbered documentation files

Documentation rules:

- Keep the numeric reading order.
- Mark old Notion notes as historical unless confirmed current.
- Record exact commands and outputs for milestones.
- Do not bury blockers.
- Prefer adding a new dated report over rewriting history.

Expected outputs:

- updated index
- run reports
- current project status
- next-step checklists
