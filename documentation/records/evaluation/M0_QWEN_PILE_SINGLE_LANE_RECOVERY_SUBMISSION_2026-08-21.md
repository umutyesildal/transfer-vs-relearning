# M0 Qwen Pile-10k Single-Lane Recovery Submission — 2026-08-21

Status: `SUBMITTED / CONTROLLER PENDING RESOURCES`

The exact wave authorized against contract SHA-256
`88f135f74c8e1932660128e4e36f99cdb13923be15fb7ba82c6c3a2a98c40332` and
pre-authorization config SHA-256
`f394ca3ecf0e056f825545675b41f7fc7b970da240b41156fff030019a36cf36` was submitted once.

- authorized config SHA-256:
  `381fce7c26769da86fb3f41f3caa94febf89b659a484f5f7c3af2fe8bf675fae`;
- HU checkout: clean `agent/m0-evaluation` at
  `a06edbb41410abe30665b45f7d3d7c39528722e3`;
- final preflight: 15/15 checks PASS, blockers empty;
- HU-home exact usage: `14,545,990,549` bytes against `32,212,254,720` bytes;
- retained/target split: 23 + 1;
- fresh root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_qwen_pile_single_lane_v1`;
- topology: one exclusive three-A100 single-lane controller plus four finalizers;
- controller: `472809`;
- model finalizers: OLMo `472810`, Qwen `472811`, SmolLM `472812`;
- family finalizer: `472813`;
- submission manifest SHA-256:
  `af6ed4e5f87426d9120d2b31c0e20d8b5c122db6dc092161e4909b44a74a502f`;
- recovery manifest SHA-256:
  `11922e408b53f46d9616d2069ee04d9890f0d59431b2a6f116abbabcf649a480`;
- exclusive route-probe SHA-256:
  `0d63ff5bb3f2915e482287aaf45b3bbdf5effb4387a6e4332f52b278194f29d4`.

The `sbatch --test-only` route probe reported eligibility and estimated controller start at
`2026-08-22T23:05:06`. This estimate is not a guarantee. The first post-submit snapshot showed
controller `472809` pending for resources and all four finalizers dependency-pending. The
single-wave authorization is consumed. No retry, normalization, M1/M2, cleanup or deletion is
authorized.
