# M0 SmolLM exact-prefix recovery v1

**Status:** `frozen / unexecuted`  
**Date:** 2026-08-21  
**Execution:** not authorized

## Purpose

Complete only the missing SmolLM M0 historical exact-prefix lane. The already valid OLMo and Qwen
lanes are immutable inputs: the finalizer imports them only after exact lane-result and artifact
hash verification. This contract does not rerun either completed model.

## Frozen identities

- implementation commit: `f95d7418e901755cca4380d276f0395856fa975c`;
- config: `configs/evaluation/m0_exact_prefix_smollm_recovery_v1.yaml`;
- config SHA-256: `e8a5a2a6e97d90f83f9446ea88868e0a98cbdff0013096eae34259300d2205ea`;
- new root: `/vol/tmp2/yesildau/eval_v1_m0_exact_prefix_smollm_recovery_v1`;
- preserved source root:
  `/vol/tmp2/yesildau/eval_v1_m0_three_model_exact_prefix_supplement_a100_recovery_v1`;
- source family-result SHA-256:
  `7e48400f742cbc6c8bf06f832de695bd9c272fbf6240b2c445190747186e4f1c`;
- source family-inventory SHA-256:
  `5d14362f8d64546064eeb46b93fcc658f6dea076dcf48a35a40fcadee4a0ddc5`;
- retained OLMo lane SHA-256:
  `ec359ab7229aa898e39bc48af867794054ef9228a3e327870f31e6a907380712`;
- retained Qwen lane SHA-256:
  `934c51f34fb35742b3424564ee3987cd0d7b883c202d864a72ff62762f590d6c`.

## One-wave DAG

The only scientific task is array index `2`, SmolLM2-1.7B at revision
`effd688a12921b4cc83e3312b6feb579f70f9c71`. It requests one exclusive A10080GB allocation on
`gruenau9`, requires at least 20 GiB free VRAM before model load, and writes only to the fresh
scratch root. One CPU finalizer runs with `afterany` and produces `complete` only when OLMo, Qwen
and SmolLM lanes all pass exact artifact validation. Thus the bounded DAG contains two jobs.

## Scientific invariants

- exactly the frozen 500 English probes and 100 subjects;
- unchanged direct prompt, candidate set, mean-logprob primary score and canonical-ID tie-breaker;
- semantic class remains `historical_exact_prefix_candidate_ranking_not_free_generation`;
- no free-generation exact-match claim;
- no normalization or scientific comparison unless the combined family is complete.

## Authorization boundary

Preparation of this contract authorizes no push, HU synchronization, SSH, Slurm submission, model
load or scoring. One exact SHA-bound user authorization is required. It may authorize only:

1. ordinary non-force push and preservation-checked HU fast-forward;
2. final fail-closed preflight;
3. one two-job SmolLM-only DAG submission.

It may not authorize an automatic retry, OLMo/Qwen rerun, prior-root mutation, cleanup, deletion,
normalization, M1/M2 training, or any HU-home write.
