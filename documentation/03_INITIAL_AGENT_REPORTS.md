# RETIRED DEFAULT REPORT — preserved initial coordination evidence

> Stop: this is historical evidence, not a current handoff. Read it only when a current task cites
> the initial coordination pass. Start ordinary work from `current/START_HERE.md`.

# 03 - Initial Agent Reports

Last updated: 2026-07-05

This document records the first coordination pass from the spawned project agents.
The agents did not edit files; they read the current documentation and repository state,
then reported their ownership boundaries, readiness findings, and risks.

## Spawned Agents

- Experiment Lead Agent: `Hooke`
- Dataset And Evaluator Agent: `Lagrange`
- Corpus And Contamination Agent: `Darwin`
- HPC And Slurm Ops Agent: `Avicenna`

## Experiment Lead Agent - Hooke

Main finding:

The scientific design is coherent and should be guarded against scope drift. The project
must remain focused on separating cross-lingual transfer from Turkish-side relearning,
not on becoming a generic Turkish factual benchmark.

Non-negotiable invariants:

- Target facts remain synthetic and controlled.
- `synthetic_v1` remains the current final dataset unless explicitly superseded.
- Branch A is transfer-only.
- Branch B is Turkish repetition/relearning control.
- Branch assignment stays subject-level.
- M2 sees no synthetic facts in Turkish.
- M3 sees only Branch B Turkish repetitions.
- M2 and M3 are budget-matched.
- Main transfer analysis includes only facts learned in English by M1.
- Candidate ranking remains the primary evaluation method.
- `born_in` and `lives_in` keep the shared city inventory for relation-binding analysis.

Current milestone:

The project has passed dataset/evaluator/corpus-pipeline preparation. The next major
milestone is the HU 100-subject M0 direct baseline evaluation.

Owner decisions needed soon:

- Final M1 learned-fact gate: direct top-1 + positive margin vs stricter dual-prompt gate.
- Turkish adaptation token budgets: for example 10M, 25M, 50M.
- M3 repetition replacement ratio: for example 24M generic + 1M Branch B repetition.
- Criteria for moving from M0 pilot to M1 training.
- Corpus contamination threshold review rules.

Documentation ownership:

The Experiment Lead Agent owns scientific design decisions, model-state semantics,
Branch A/B interpretation, analysis subsets, metric gates, and owner-approved experiment
decisions.

## Dataset And Evaluator Agent - Lagrange

Main finding:

Dataset and evaluator are ready for the M0 pilot, assuming HU has the pinned GPT-2 model
snapshot and runtime environment.

Dataset readiness:

- `synthetic_v1` validation: passed.
- 5,000 subjects.
- 25,000 facts.
- Branch A/B facts: 12,500 / 12,500.
- English/Turkish probes: 25,000 / 25,000.
- Candidate inventory: profession 200, city 130, university 91, employer 241.
- 100-subject pilot exists and is balanced.

Evaluator readiness:

- direct config exists.
- QA-matched config exists.
- primary scoring is mean answer-token log probability.
- total log probability is retained as sensitivity scoring.
- resume/fingerprint checks exist.
- strict completion status exists.
- relation-binding and subgroup outputs exist.

Exact M0 direct command on HU:

```bash
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
sbatch slurm/eval_m0_gpt2_pilot.slurm
```

Exact M0 QA-matched command after direct run:

```bash
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning
sbatch --export=ALL,EVAL_CONFIG=configs/evaluation/m0_gpt2_pilot_qa_matched.yaml \
  slurm/eval_m0_gpt2_pilot.slurm
```

Completion checks:

- `completion_status=completed`
- `expected_probe_count=1000`
- `successful_probe_count=1000`
- `failed_probe_count=0`

Risks:

- Local machine does not have `artifacts/models/openai-community__gpt2/model_manifest.json`.
- Local evaluation outputs are absent.
- 100-subject pilot is diagnostic, not population-weighted.
- M0 low accuracy is expected and should not be overinterpreted.
- M1 learned-fact gate is documented but not yet implemented as an analysis artifact.

Documentation ownership:

The Dataset And Evaluator Agent owns dataset validation snapshots, pilot selection
invariants, M0 direct and QA-matched run IDs, summary metrics interpretation,
relation-binding results, and M1 learned-fact gate tables.

## Corpus And Contamination Agent - Darwin

Main finding:

The Turkish Wikipedia Phase 1 corpus pipeline is architecturally ready, but full real-data
execution has not happened yet.

Current corpus state:

- branch/commit: `corpus-update`, `638b697fe67a4fa1ede76241caf4fa4215bde72f`
- configured source: `trwiki-20260601-pages-articles.xml.bz2`
- config: `transfer-vs-relearning/configs/corpora/trwiki_gpt2_calibration.yaml`
- corpus artifact directories currently contain only `.gitkeep` files locally.

Safe next corpus steps:

```bash
python scripts/prepare_trwiki.py resolve \
  --config configs/corpora/trwiki_gpt2_calibration.yaml

python scripts/prepare_trwiki.py resolve \
  --config configs/corpora/trwiki_gpt2_calibration.yaml \
  --fetch-metadata

python scripts/prepare_trwiki.py contamination-preflight \
  --config configs/corpora/trwiki_gpt2_calibration.yaml

python scripts/prepare_trwiki.py download \
  --config configs/corpora/trwiki_gpt2_calibration.yaml

python scripts/prepare_trwiki.py verify \
  --config configs/corpora/trwiki_gpt2_calibration.yaml

python3 -m pytest -ra \
  tests/test_corpora_phase1.py::test_production_parser_smoke_with_pinned_dependencies
```

Do not start extraction until the production parser smoke test passes on HU without skip
using pinned `mwxml==0.3.8` and `mwparserfromhell==0.7.2`.

Contamination invariants:

- M2 generic Turkish corpus must contain no synthetic subject/fact exposure.
- Removal signals include full synthetic subject names, generated fact sentences,
  subject IDs, fact IDs, dataset artifact names, and subject plus own canonical object
  co-occurrence.
- Object-only matches are flag-only.
- Split may only read `contamination/clean_documents.jsonl`.
- Final retained verified synthetic full-name matches should be zero.

Risks:

- Full Wikimedia dump has not been downloaded or verified.
- Real extraction/scan/split outputs do not exist yet.
- Filtering is still `audit_only`; threshold review is required before final removal.
- Phase 2 tokenization is not implemented.
- Deduplication is exact SHA-256 only; near-dedup is out of scope for now.

Documentation ownership:

The Corpus And Contamination Agent owns Turkish corpus pipeline notes, safe order,
metadata trust levels, parser smoke, audit/filter policy, contamination semantics,
split/report finalization, and future corpus runbooks.

## HPC And Slurm Ops Agent - Avicenna

Main finding:

HU is the correct execution target for GPU evaluation. Local machine is useful for
documentation and lightweight validation, but not for the real M0 GPU run.

HU readiness checklist:

- expected path: `/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning`
- expected branch: `corpus-update`
- expected commit: `638b697fe67a4fa1ede76241caf4fa4215bde72f`
- conda env: `xfer-relearn`
- Slurm script: `slurm/eval_m0_gpt2_pilot.slurm`
- requested GPU: A100 80GB
- expected model manifest: `artifacts/models/openai-community__gpt2/model_manifest.json`
- expected pilot count: 100 subjects x 5 relations x 2 languages = 1,000 probe-language rows

Pre-run verification:

```bash
cd /vol/fob-vol6/mi25/yesildau/transfer-vs-relearning

git branch --show-current
git rev-parse HEAD
git status --short

mkdir -p logs

module load anaconda/3-2024.06

conda run --name xfer-relearn python --version
conda run --name xfer-relearn python -m compileall -q src tests scripts
conda run --name xfer-relearn python -m pytest -ra

conda run --name xfer-relearn python scripts/validate_dataset.py \
  --dataset-dir artifacts/datasets/synthetic_v1

conda run --name xfer-relearn python -m json.tool \
  artifacts/models/openai-community__gpt2/model_manifest.json

sbatch --test-only slurm/eval_m0_gpt2_pilot.slurm
```

Run and monitor:

```bash
sbatch slurm/eval_m0_gpt2_pilot.slurm
squeue -j <job_id>
tail -f logs/m0-gpt2-pilot-<job_id>.out logs/m0-gpt2-pilot-<job_id>.err
```

Expected artifacts:

- `logs/m0-gpt2-pilot-<job_id>.out`
- `logs/m0-gpt2-pilot-<job_id>.err`
- `runs/evaluation/m0_gpt2_pilot/<run_id>/run_manifest.json`
- `runs/evaluation/m0_gpt2_pilot/<run_id>/summary_metrics.json`
- `runs/evaluation/m0_gpt2_pilot/<run_id>/subgroup_metrics.csv`
- `runs/evaluation/m0_gpt2_pilot/<run_id>/relation_binding_metrics.json`
- `runs/evaluation/m0_gpt2_pilot/<run_id>/per_fact_results.csv`
- optional `per_fact_results.parquet`
- `progress.json`
- `selected_subjects_reference.json`

Operational risks:

- If the model manifest is missing, offline evaluation should fail rather than download.
- Do not blindly update the conda env.
- `partial_failed` is not a scientific result.
- Resume only with matching config/dataset/model fingerprints.
- `logs/`, `runs/evaluation/`, and model artifacts should stay out of commits.
- Use `_direct.yaml` explicitly to avoid ambiguity with similarly named configs.

Documentation ownership:

The HPC And Slurm Ops Agent owns HU execution notes, immediate runbook steps, job IDs,
run IDs, log paths, completion status, and operational risk notes.

## Coordination Outcome

The project now has a clear agent structure:

- Experiment Lead guards scientific semantics.
- Dataset/Evaluator handles factual evaluation and metrics.
- Corpus/Contamination handles Turkish data cleanliness.
- HPC/Slurm Ops handles reliable HU execution.
- Documentation Agent keeps the ordered project memory current.

The next operational milestone remains the HU 100-subject M0 direct baseline evaluation.
