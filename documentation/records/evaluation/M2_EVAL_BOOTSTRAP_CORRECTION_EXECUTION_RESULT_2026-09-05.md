# M2 eval-v2 bootstrap correction — execution result

**Date:** 2026-09-05  
**Status:** complete / PASS  
**Job:** `484357` (`std`, 4 CPU, 8 GiB; no GPU)

## Outcome

The single SHA-bound CPU publication wave completed successfully under the fresh append-only root
`/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_analysis_correction_v1`. It recomputed only the paired
subject bootstrap from the already completed 63-state evaluation family. It did not load a model,
run inference/evaluation, train, update a checkpoint, clean an artifact or retry.

The final audit records:

- `status = M2_EVAL_V2_ANALYSIS_CORRECTION_COMPLETE`;
- `source_inputs_unchanged = true`;
- `gpu_used = false`;
- `model_load_or_inference = false`;
- `automatic_retry = false`.

The job stderr is empty. The HU focused evaluation/recovery/correction suite passed 38/38 before
submission.

## Corrected scientific result

The correction pairs every unique `probe_id` and retains all eight prompt variants for each of the
100 subjects. With 10,000 paired-subject bootstrap draws at seed 42:

| Model | Transfer: M2-A − M1, `tr_to_en` | 95% CI | Relearning: M2-B − M2-A, `tr_to_en` | 95% CI | All primary gates |
|---|---:|---:|---:|---:|---:|
| OLMo | -0.14100 | [-0.16075, -0.12050] | +0.02000 | [+0.01500, +0.02550] | false |
| Qwen | -0.30700 | [-0.33675, -0.27750] | +0.04350 | [+0.02950, +0.05775] | false |
| SmolLM | -0.16175 | [-0.18525, -0.13850] | +0.00350 | [+0.00050, +0.00650] | false |

All three relearning confidence intervals remain above zero, but no point estimate reaches the
frozen +0.05 minimum. SmolLM also fails the M2-A English factual-retention gate. The terminal family
conclusion is therefore unchanged: no model passes every primary gate. Qwen remains the strongest
descriptive relearning result, not an automatic primary-model selection.

## Immutable bindings

- execution commit: `a4c2e609e494342f043c7b6859d77d9a9483c5e5`;
- contract SHA-256: `da2f3cb0251ae0bf9abc95e5663cb924988e77c1188dbdba4bc9c46066196b3f`;
- source root: `/vol/tmp2/yesildau/vnd_m2_oscar_eval_v2_recovery_v1a` (read-only);
- input manifest SHA-256: `967063ea706791d2061227bd95bccba34cdd574c33487630a26c00ed51f38319`;
- corrected analysis SHA-256: `7427b11f2f4fd2f5c191b23f6836d97a151a00fdbce755cd545a6aa4982b5043`;
- final audit SHA-256: `6173b4a9a7d46107bc95c169fa9d78133f70899b09a4169c221150148f6e039a`;
- submission result SHA-256: `29355083ee22ce0f299f0e15d3acafc07f790681ad133efaecfd18760ee8fd17`.

The older `fact_id`-paired bootstrap rows remain preserved as historical executed evidence and are
superseded for interpretation by this canonical HU-published correction. No further correction,
evaluation rerun or automatic retry is authorized or needed.
