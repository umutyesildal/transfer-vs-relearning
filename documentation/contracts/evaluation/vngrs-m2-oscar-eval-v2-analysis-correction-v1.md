# Frozen execution contract — `vngrs-m2-oscar-eval-v2-analysis-correction-v1`

**Status:** frozen, unexecuted; exact SHA-bound user authorization required

**Purpose:** publish one canonical, append-only CPU correction of the completed M2 endpoint
paired-subject bootstrap without evaluation, inference or source mutation

## Scientific correction

The executed analysis grouped `tr_to_en` rows by `subject_id/fact_id`. Each fact has eight prompt
variants, so dictionary assignment retained only the last CSV row. This contract changes only the
pairing identity from `fact_id` to unique `probe_id`. It preserves all matched prompts, calculates
each subject's mean change across its 40 `tr_to_en` probes and applies the unchanged 10,000-draw,
seed-42 paired-subject bootstrap.

Every other endpoint metric, direction, denominator, BPB value, gate threshold and gate direction
is unchanged. The original `scientific_analysis.json` remains immutable historical evidence.

## Exact source and output

- Immutable source root:
  `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a`.
- Fresh output root:
  `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_analysis_correction_v1`.
- Source finalizer: 63/63 complete; SHA-256
  `c04eff5ba1301f5fcd4a318cc3a88d281e389cd05f542e6f6d569826809bcebf`.
- Superseded analysis SHA-256:
  `732c9c23ab795bf3212196d582f8300ca6c02dbf6902c489a1d4ecd6eae6e0ca`.
- Task matrix SHA-256:
  `6d3b8b97f048e1531d2146e2d47626a7cf8475122bb2abf32c124a60536d990d`.
- M1 registry target SHA-256:
  `624374bd928016854e03e620c9fab9e012a17a7d1b658b5502f26a8a7a0574cf`.
- The exact three M1 and six M2 endpoint CSV byte sizes and SHA-256 values are frozen in the
  config. Their aggregate size is below 72 MiB. All 63 task-result hashes are independently
  rechecked from the terminal family manifest.

The job writes only:

1. `control/input_manifest.json`;
2. `control/corrected_scientific_analysis.json`;
3. `control/final_audit.json`;
4. the submitter's `control/submission_result.json` and Slurm stdout/stderr.

No output file may exceed 1 MiB. Inputs are hashed before and after computation; any change fails
closed. The source root, prior V1/V1A/V1B roots, M1 root, model files and corpus files are read-only.

## Frozen implementation

| Component | SHA-256 |
|---|---|
| pairing implementation `src/transfer_vs_relearning/evaluation/turkish_bridge_analysis.py` | `4ae4abdd0fea8847f35ad1d40b0bb435cc4f00362cc2d5930a172b69b963cf46` |
| correction operator `src/transfer_vs_relearning/study/m2_analysis_correction.py` | `44f5958358d3c06d045cedd0cf13bea3a99c9c1d82fec79a97131fb48a83ba3c` |
| unchanged M2 analysis/finalizer `src/transfer_vs_relearning/study/m2_eval_executor.py` | `c7c8f38f70b811cce9440d9f6b75ea505d38d2f61d31a691df95ef2da45d0a2b` |
| entrypoint `scripts/study/execute_m2_analysis_correction.py` | `8e927aafd5e472007339007ada92143cc2ed98002310bb6ca074e4585be8d992` |
| config `configs/evaluation/m2_oscar_eval_v2_analysis_correction_v1.yaml` | `093a74f0b561a69df11132377f7642663c8971e285fc7a0b60f8d73346f4cc84` |
| Slurm wrapper `slurm/m2/finalize_m2_oscar_eval_analysis_correction_v1.slurm` | `7642c300494db0f98acec6b0027052f4fcf67fa7990d4dc1c3de95e2eb3db63f` |
| submitter `scripts/m2/submit_m2_oscar_eval_analysis_correction_v1.sh` | `2e3dfd1a8c1366b79c13b00bfd35ee1c1ab9c331b0b078761e9ace99e1a52a5f` |

Runtime Python is
`/vol/tmp2/yesildau/eval_v1_envs/lm_eval_v0_4_12_torch260_cu124_v3/bin/python`; runtime lock SHA-256
is `f9238f731fe3286aa0f5e5934f2b559a4202794d43cea4b9b00b2960b37ee942`.

## Frozen expected correction

These values are deterministic acceptance checks, not newly selected thresholds:

| Model | Transfer estimate [95% CI] | Relearning estimate [95% CI] |
|---|---|---|
| OLMo | −0.141000 [−0.160750, −0.120500] | +0.020000 [+0.015000, +0.025500] |
| Qwen | −0.307000 [−0.336750, −0.277500] | +0.043500 [+0.029500, +0.057750] |
| SmolLM | −0.161750 [−0.185250, −0.138500] | +0.003500 [+0.000500, +0.006500] |

All three retain `all_primary_gates_pass=false` because no relearning point estimate reaches the
unchanged +0.05 minimum; SmolLM also retains its English factual-retention failure.

## Resources and execution

One `std` job only: 4 CPU, 8 GiB RAM, 2 hours, `--no-requeue` by policy of the submitter/contract.
The submitter must pass `sbatch --test-only`, prove the output root absent, prove no same-name job,
verify the exact commit/clean checkout/contract SHA and create only the fresh skeleton before the
single submission. Minimum free storage is 1 GiB and 256 inodes.

## Explicit prohibitions

No GPU; no model/tokenizer load; no inference or evaluation; no training or optimizer operation;
no checkpoint or corpus read; no network; no source/prior-root mutation; no cleanup, deletion,
fallback, second correction wave or automatic retry. A failure remains preserved and requires a
new diagnosis and separately frozen authority.

Preparation, commit and ordinary push are authorized by the user's current instruction. HU
fast-forward and this one CPU job require a new user authorization quoting this contract's final
SHA-256 and the publication commit.
