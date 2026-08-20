# M0 Five-Lane Retargeted Recovery Submission — 2026-08-20

Status: `SUBMITTED / CONTROLLER RUNNING`

The exact wave authorized against contract SHA-256
`1b030869455d68aa0ecf933f881c1661e1fbf504997376fdba08a626e1bc0a55` and
pre-authorization config SHA-256
`705661dd5e32d836ee58f64101bc887c7a85059bae3ca2b25505ad967bde9a7d` was submitted once.

- authorized config SHA-256:
  `08cbe81574b63aa3f488e7f17cc1f6f41b339e85c5d5814b7cbd6fbf76f27c41`;
- HU checkout: clean `agent/m0-evaluation` at
  `2c2cd04e895d99861847dc7e97a874430b179a42`;
- final preflight: 17/17 checks PASS, blockers empty;
- HU-home exact usage: `14,545,990,549` bytes against `32,212,254,720` bytes;
- retained/target split: 19 + 5;
- fresh root:
  `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_retargeted_v1`;
- topology: one exclusive three-A100 sequential controller plus four finalizers;
- controller: `471536`;
- model finalizers: OLMo `471537`, Qwen `471538`, SmolLM `471539`;
- family finalizer: `471540`;
- submission manifest SHA-256:
  `4551a5c9266d354e06a0438f286b9d4063c0a2c4b5ff5bc8e3b699daaa3da6ad`;
- recovery manifest SHA-256:
  `9a2011a89a31a48e2a3f9b68a137c0e25d606a4d3da95b940abb098e3386ff8f`.

The route test estimated immediate start at `2026-08-20T16:17:36+02:00`. The first post-submit
snapshot showed controller `471536` running on `gruenau10`; all four finalizers were dependency
pending. The single-wave authorization is consumed. No retry, normalization, M1/M2, cleanup or
deletion is authorized.
