# Transfer vs. Relearning

This monorepo contains the code, controlled synthetic data generator, experiment configurations,
scientific record, paper sources, study notes, and operational tooling for the Master's thesis
**Transfer vs. Relearning in Cross-Lingual Factual Adaptation**.

The central comparison is whether Turkish access to facts learned in English comes from transfer
or from Turkish factual re-exposure:

```text
M0   frozen pretrained base model
M1   M0 + controlled English factual adaptation
M2-A M1 + fact-free Turkish adaptation
M2-B the same M1 + matched Turkish adaptation with controlled factual re-exposure
```

M2-A and M2-B are parallel sibling arms. M2-B is not a continuation of M2-A.

## Current status

M0 is closed under the active Pile-free `eval-v2` contract: all 21 non-Pile lanes, the three-model
exact-prefix panel and 42 normalized metric observations are complete. Work is now local M1
pipeline/contract repair for the fixed OLMo/Qwen/SmolLM cohort. M1 has not started and remains
execution-disabled until the user later authorizes the final hash-bound contract.

A local planner/tracing foundation now renders the future
preflight→train→epoch-eval→normalize→presentation sequence without executing it. See
[`documentation/pipeline/README.md`](documentation/pipeline/README.md).

The current local branch is `agent/m1-pipeline-repair`. vngrs is reserved for M2-A/M2-B and does
not block M1 preparation. No remote, HU, Slurm, model training/evaluation, corpus materialization,
push, merge, cleanup or deletion follows from this README.

Read the concise live state in
[`documentation/current/STATUS.md`](documentation/current/STATUS.md). The machine-readable state
is [`documentation/current/PROJECT_STATE.yaml`](documentation/current/PROJECT_STATE.yaml).

## Start here

For a human:

1. Read this README for the project map.
2. Read [`documentation/current/STATUS.md`](documentation/current/STATUS.md).
3. Read [`documentation/current/ROADMAP.md`](documentation/current/ROADMAP.md).
4. Open the relevant contract or historical record only when the task needs it.

For an agent:

1. Read [`AGENTS.md`](AGENTS.md).
2. Read [`documentation/current/START_HERE.md`](documentation/current/START_HERE.md).
3. Read [`documentation/current/AGENT_BRIEF.yaml`](documentation/current/AGENT_BRIEF.yaml).
4. Read the current task packet or explicit user instruction.
5. Read only the relevant frozen contract and evidence named by that task.

`AGENTS.md` alone is intentionally not enough for scientific or operational work: it contains
stable rules, while `AGENT_BRIEF.yaml` contains the small current projection. Scientific or
external execution additionally requires the full `PROJECT_STATE.yaml` and exact contract.

## Repository map

| Path | Role |
|---|---|
| `src/transfer_vs_relearning/` | Core Python package |
| `scripts/` | Grouped study, state-specific, corpus, training and evaluation entry points |
| `configs/` | Versioned experiment, model, corpus, training, and evaluation settings |
| `slurm/` | Launchers grouped under `m0/`, `m1/`, and `m2/`; presence is not authorization |
| `tests/` | Main offline test suite |
| `tools/synthetic-data/` | Synthetic data generator with imported, publication-sanitized history |
| `documentation/current/` | Small live control plane: state, authority, and roadmap |
| `documentation/contracts/` | Prospective frozen execution and measurement contracts |
| `documentation/decisions/` | Short durable architecture/scientific decisions |
| `documentation/pipeline/` | Train/trace/evaluate/normalize/presentation interface |
| `documentation/records/` | Immutable or superseded records and preserved guidance |
| `documentation/*.md` | Existing chronological scientific record, Documents 00–178 |
| `artifacts/evaluations/m0_three_model_v1/dump/` | Git-sized M0 metric dump with source hashes |
| `tools/m0-dashboard/` | Dependency-free local M0–M2 bilingual evaluation explorer |
| `artifacts/` and `runs/` | Local/generated scientific artifacts; generally not Git data |
| `paper/`, `papers/`, `study-notes/` | Thesis sources, reference notes, and learning material |
| `presentations/`, `reports/` | Authored and legacy presentation/report material |
| `.agents/` | Optional bounded Sol/Luna orchestration layer |
| `ssh-client/` | HU connection helpers and operational instructions |

## Local setup and verification

Python 3.11 or later is required.

```bash
uv sync --extra dev
uv run pytest
uv run pytest .agents/tests
(cd tools/synthetic-data && ../../.venv/bin/python -m pytest)
```

The lockfile is versioned. GPU, network, model, and corpus operations are not part of the standard
offline test suite.

To inspect the compact three-model M0 result dump locally (with prepared M1/M2 state slots):

```bash
python3 tools/m0-dashboard/serve.py
# open http://127.0.0.1:8765/tools/m0-dashboard/
```

The app reads `artifacts/evaluations/m0_three_model_v1/dump/m0_metrics.json`. It is read-only and
does not contact HU or rerun an evaluation; M1/M2 states remain explicitly empty until their
canonical snapshots exist.

## Documentation model

Markdown has one job per layer:

- `README.md` answers “where is everything?”
- `AGENTS.md` defines stable operating rules.
- `documentation/current/` answers “what is true now?”
- `documentation/contracts/` defines what a future bounded wave would do.
- `documentation/decisions/` records why a durable choice was made.
- `documentation/records/` and numbered documents preserve what happened.
- machine manifests and result tables carry exact run identity and metrics.

Do not create another ever-growing master narrative. Update the smallest owning document and link
to evidence instead of copying the same status into several files.

## Data, secrets, and artifacts

Large generated data, checkpoints, model weights, caches, local run outputs, `.env` files, and
reference PDFs are excluded by `.gitignore` unless a separate reviewed policy says otherwise.
Commit code, configs, schemas, manifests, hashes, compact summaries, and authored sources.

The imported history was publication-sanitized after explicit user approval: generated `output/`
and `tools/synthetic-data/output/` paths were removed from the reachable monorepo history. The
reachable ≥10 MiB blob count is now zero. The exact pre-filter branch remains recoverable from a
verified private Git bundle and the original source repositories remain untouched. This cleanup
does not itself authorize pushing or changing the default branch.

Never interpret “ignored by Git” as “safe to delete.” Local artifacts remain scientific or user
data until an explicit retention decision classifies them.

## Historical record

The chronological documents are preserved scientific evidence. Earlier failures and superseded
decisions are not rewritten to make the project history look cleaner. The new control plane points
to them without replacing them.

The lossless repository migration and verification result is documented in
[`documentation/migration/REPOSITORY_MIGRATION_V1.md`](documentation/migration/REPOSITORY_MIGRATION_V1.md).
