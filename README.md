# transfer-vs-relearning

This repository implements the first software stage of a Master's thesis experiment on multilingual factual knowledge transfer versus relearning.

The scientific question is whether factual knowledge that becomes retrievable in Turkish after Turkish adaptation can be attributed to cross-lingual transfer from English parametric knowledge, rather than relearning from Turkish factual repetitions.

## Experiment States

- `M0`: original pretrained base model.
- `M1`: `M0` continued-pretrained on synthetic facts expressed only in English.
- `M2`: `M1` adapted with generic Turkish text containing none of the synthetic facts.
- `M3`: `M1` adapted with the same generic Turkish text plus Turkish repetitions of Branch B facts.

Branch A facts are transfer-only facts. Branch B facts are Turkish repetition/relearning facts. This repository does not implement training yet; the current milestone is dataset pinning plus `M0` factual candidate-ranking evaluation.

## Dataset Dependency

Dataset generation is maintained externally in `https://github.com/umutyesildal/synthetic-data-generation`. This repository consumes generated artifacts as a pinned dataset dependency and does not copy generator logic or modify that source repository.

Required source artifacts are:

- `data/canonical_subject_profiles_5000.csv`
- `output/english_training.jsonl`
- `output/turkish_repetition.jsonl`
- `output/probes_en.csv`
- `output/probes_tr.csv`
- `output/canonical_generation_summary.json`
- `output/source_validation_report.json`

Synchronize and freeze a dataset version:

```bash
python scripts/sync_synthetic_dataset.py \
  --source-repo https://github.com/umutyesildal/synthetic-data-generation \
  --ref main \
  --version synthetic_v1
```

The sync script resolves the exact source commit, copies required artifacts into `artifacts/datasets/synthetic_v1/`, computes SHA-256 hashes, validates scientific constraints, and writes `manifest.json` plus `validation_summary.json`. Existing dataset versions are immutable; use a new version name if artifacts change.

## Canonical Facts

The canonical CSV has 5,000 unique subjects. Each row expands deterministically into five facts:

- `profession`
- `born_in`
- `lives_in`
- `studied_at`
- `works_at`

The normalized fact ID format is `{subject_id}_{relation}`, for example `S01958_profession`.

Validate a synchronized dataset:

```bash
python scripts/validate_dataset.py \
  --dataset-dir artifacts/datasets/synthetic_v1
```

## Model Pinning

The first base model is exactly `openai-community/gpt2`. It is the `M0` model and is not instruction-tuned.

Download and pin the model snapshot when ready:

```bash
python scripts/download_model.py \
  --model-id openai-community/gpt2
```

The script uses `huggingface_hub.snapshot_download`, resolves the exact model revision, saves under `artifacts/models/openai-community__gpt2/<commit_sha>/`, and writes a model manifest. GPU evaluation loads the local pinned snapshot with `local_files_only=True`; it must not download during Slurm jobs.

## Pilot Selection

The first evaluation uses 100 subjects, all five facts per subject, and both English and Turkish probes. Selection is deterministic with seed `42` and round-robins across branch, name type, name rarity, and popularity strata where feasible.

```bash
python scripts/select_pilot.py \
  --dataset-version synthetic_v1 \
  --subjects 100 \
  --seed 42
```

This writes `artifacts/datasets/synthetic_v1/pilot_100_subjects.json`, which is reused for `M0`, `M1`, `M2`, and `M3`.

## Evaluation

The evaluator performs candidate ranking for causal language models. For each probe, it renders a configurable prompt, appends each candidate answer, scores only answer continuation tokens, and ranks candidates by mean answer-token log probability.

Default prompt:

```text
Question: {question}
Answer:
```

followed by one separating space and the candidate answer.

Primary score: mean answer-token log probability. Secondary score: total answer-token log probability. Ties are deterministic: descending score, then stable canonical object ID.

GPT-2 byte-level BPE boundaries are handled by tokenizing the full prompt-plus-candidate string with offset mappings and mapping the answer character span to token positions. The tokenizer pad token is set to EOS for batching/evaluation without resizing or training weights.

Run after dataset sync, pilot selection, and model download:

```bash
python scripts/evaluate_facts.py \
  --config configs/evaluation/m0_gpt2_pilot.yaml
```

Summarize an evaluation run:

```bash
python scripts/summarize_evaluation.py \
  --run-dir runs/evaluation/m0_gpt2_pilot/<run_id>
```

## Candidate Inventories

Candidates are built from canonical object pairs:

- profession: unique `(profession_en, profession_tr)`
- city: union of birthplace and residence pairs; shared by `born_in` and `lives_in`
- university: unique `(university_en, university_tr)`
- employer: unique `(employer_en, employer_tr)`

Object IDs are stable SHA-based IDs derived from relation family and normalized English/Turkish forms. English probes score English surfaces; Turkish probes score Turkish surfaces.

## Outputs

Each evaluation run writes to `runs/evaluation/m0_gpt2_pilot/<run_id>/`:

- `run_manifest.json`
- `resolved_config.yaml`
- `summary_metrics.json`
- `subgroup_metrics.csv`
- `relation_binding_metrics.json`
- `per_fact_results.parquet`
- `per_fact_results.csv`
- `errors.jsonl`
- `progress.json`
- `selected_subjects_reference.json`

Progress is saved atomically. Completed fact-language probes are skipped on resume.

## Relation Binding

Because `born_in` and `lives_in` share a city inventory, the evaluator reports whether the model distinguishes a subject's birthplace from current residence using canonical city IDs. Metrics include swapped-answer rates, other-city ranks, and pairwise relation-binding accuracy.

## Conda and Slurm

The HU server environment is expected to use Conda environment `xfer-relearn` with Python 3.11, PyTorch 2.7.0+cu128, CUDA runtime 12.8, and A100 80GB GPUs.

Create/update the environment:

```bash
conda env update --name xfer-relearn --file environment.yml
```

Submit the pilot evaluation only after the local model snapshot exists:

```bash
sbatch slurm/eval_m0_gpt2_pilot.slurm
```

The Slurm script uses partition `gpu`, GRES `gpu:a10080gb:1`, `module load anaconda/3-2024.06`, and `conda run --name xfer-relearn`. It sets Hugging Face offline flags and does not submit itself automatically.

## Tests

Standard tests are offline: no internet, no GPT-2 download, no GPU, no Slurm, and no changes to the external source repository.

```bash
python -m pytest
```

## Current Scope

Implemented in this stage:

- repository scaffold
- dataset synchronization and manifesting
- dataset validation
- model snapshot pinning command
- deterministic pilot selection
- causal LM candidate-ranking evaluator
- relation-binding and subgroup metrics
- Slurm pilot evaluation script
- offline unit tests

Not implemented in this stage:

- `M1`, `M2`, or `M3` training
- model fine-tuning
- Slurm job submission
