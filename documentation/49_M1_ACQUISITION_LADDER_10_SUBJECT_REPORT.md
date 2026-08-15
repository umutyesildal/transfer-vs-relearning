# 49 - M1 Acquisition Ladder 10-Subject Report

Last updated: 2026-07-10

## Outcome

The first acquisition-ladder level failed its precommitted progression gate. Do not launch
the 100-subject / 500-fact level with this recipe.

## Implementation And Deployment

- branch: `corpus-update`
- implementation commit: `8ee4f17`
- GitHub push: successful on 2026-07-10
- HU pull: fast-forward from `59a63e3` to `8ee4f17`
- remote dataset build: passed
- focused remote test suite: passed

Generated ladder counts:

- 10 subjects: 50 facts, 250 train rows, 50 held-out validation rows
- 100 subjects: 500 facts, 2,500 train rows, 500 held-out validation rows
- 500 subjects: 2,500 facts, 12,500 train rows, 2,500 held-out validation rows

Only the 10-subject level was trained.

## Training Run

- Slurm job: `390992`
- assigned compute node: `gruenau9`
- GPU request: one A100 80GB
- run directory:

```text
runs/training/m1_smollm2_360m_acquisition_ladder_10_answer_only/
20260710T203516Z_m1_smollm2_360m_acquisition_ladder_10_answer_only_lr5e-5_ep10_db089691
```

Training completed successfully:

- optimizer steps: 320
- epochs: 10
- runtime: 116.6 seconds
- train loss: 1.864
- final held-out eval loss: 1.254
- lowest held-out eval loss: approximately 1.254 at epochs 9-10

The run used full-parameter SmolLM2-360M training with answer-only loss. It did not use
LoRA or MCQ negative strings.

## Evaluation Operations

The first evaluation submission attempt created jobs `390993` through `391002`, but all ten
failed before model evaluation. The local helper captured stdout from
`create_local_model_manifest.py` inside the `EVAL_CONFIG_DIR` shell variable, producing an
invalid multi-line directory path. These jobs produced no scientific metrics.

The helper was corrected by discarding the manifest subprocess stdout. Clean evaluation
jobs were then submitted:

- `391003` through `391012`
- one job per checkpoint
- three views per job: exact-prefix, direct, and QA-matched
- all jobs completed without evaluation errors

Slurm distributed the jobs across both A100 nodes:

- `gruenau9`: 3 x A100 80GB, 32 CPUs
- `gruenau10`: 3 x A100 80GB, 72 CPUs

Both nodes provide the same GPU type and count. The training job requested only eight CPUs,
so forcing it onto `gruenau10` would not increase GPU throughput. Allowing Slurm to use both
nodes enabled six evaluations to run concurrently. Node pinning should be reserved for a
verified hardware or contamination issue, not used as the default policy.

## Checkpoint Results

All values are English top-1 fractions over 50 facts. `Overlap` is the direct/QA top-1
intersection.

| Checkpoint | Exact prefix | Direct | QA matched | Overlap | Gate |
|---|---:|---:|---:|---:|---|
| 32 | 0.02 | 0.00 | 0.02 | 0.00 | fail |
| 64 | 0.08 | 0.00 | 0.06 | 0.00 | fail |
| 96 | 0.10 | 0.02 | 0.08 | 0.02 | fail |
| 128 | 0.14 | 0.02 | 0.12 | 0.02 | fail |
| 160 | 0.22 | 0.02 | 0.14 | 0.02 | fail |
| 192 | 0.22 | 0.02 | 0.16 | 0.02 | fail |
| 224 | 0.24 | 0.02 | 0.20 | 0.02 | fail |
| 256 | 0.24 | 0.02 | 0.20 | 0.02 | fail |
| 288 | 0.24 | 0.02 | 0.22 | 0.02 | fail |
| 320 | 0.24 | 0.02 | 0.20 | 0.02 | fail |

Best observed counts:

- exact-prefix: 12/50
- direct: 1/50
- QA-matched: 11/50
- robust direct/QA overlap: 1/50

Precommitted thresholds were:

- exact-prefix at least 90%
- direct at least 50%
- QA-matched at least 50%
- robust overlap at least 40%

No checkpoint passed.

## Interpretation

The increasing exact-prefix and QA curves show a real acquisition signal, but the model did
not reliably memorize even 50 controlled bindings under this recipe. Direct retrieval stayed
near chance and did not follow the QA improvement. The held-out loss plateaued while factual
ranking remained far below the gate, again confirming that loss alone is not a promotion
criterion.

This result localizes the current problem below the scale of the previous 25,000-fact runs.
It is therefore not justified to launch the 100-subject level, add more large-scale epochs,
or move directly to M2/M3.

The next action must diagnose the 50-fact rung itself, including answer-token supervision,
candidate scoring alignment, effective per-fact exposure, and whether an even smaller
single-relation or single-fact control can reach deterministic retrieval.

