# M0 Seven-Lane Recovery Execution Result — 2026-08-20

Status: `TERMINAL_NOT_RUN_GPU_MEMORY_GUARD`  
Scientific scores produced: `0`  
Authorization consumed: `yes`

## Bound identities

- Contract SHA-256: `1ee7c8d9d1da092cd1e4a64dbffa4594e041ebf2b4d56eb62f345a6aaa8c25c4`
- Pre-authorization config SHA-256: `4a603719dd43a65dd9b36a36786407993afe84cf8d1d48f6245656d235c6bfeb`
- Execution config SHA-256: `d934b782fe307d1d54b7fdce47be8ebc2409a6b6c2acf3f2aa435aa4577ac6d7`
- HU execution commit: `28b123ce984e35c835a2cf7a5e154aa6f6b3212a`
- Recovery root: `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_recovery_v1`
- Source family bundle SHA-256: `75fcd7cf1e388eb5a4e883264c6aa14db83797b2e7832a4bbc8e40bb38865db1`

HU focused tests passed 10/10. The final preflight passed every gate. Exact HU-home usage was
`14,545,990,549` bytes against the `32,212,254,720`-byte limit. The source root remained read-only,
the fresh recovery root was absent before submission and no duplicate recovery jobs existed.

## Submitted DAG

| Model | Lane | Job | Route | Terminal class |
|---|---|---:|---|---|
| OLMo | English capability | 470523 | V10032 | memory guard blocked |
| OLMo | Turkish capability | 470524 | V10032 | memory guard blocked |
| OLMo | Turkish perplexity | 470525 | V10032 | memory guard blocked |
| OLMo | model finalizer | 470526 | CPU | partial invalid |
| Qwen | Pile-10k retention | 470527 | A10080 | memory guard blocked |
| Qwen | Turkish capability | 470528 | V10032 | memory guard blocked |
| Qwen | Turkish perplexity | 470529 | V10032 | memory guard blocked |
| Qwen | model finalizer | 470530 | CPU | partial invalid |
| SmolLM | English capability | 470531 | V10032 | memory guard blocked |
| SmolLM | model finalizer | 470532 | CPU | partial invalid |
| family | composite finalizer | 470533 | CPU | partial invalid; normalization closed |

## Exact GPU guard evidence

All seven jobs stopped before model load or scoring.

| Job | Node | Lane | Free bytes | Visible total bytes | Required bytes |
|---:|---|---|---:|---:|---:|
| 470523 | gruenau1 | OLMo English capability | 21,226,782,720 | 34,072,559,616 | 30,064,771,072 |
| 470524 | gruenau1 | OLMo Turkish capability | 23,413,063,680 | 23,593,091,072 | 30,064,771,072 |
| 470525 | gruenau1 | OLMo Turkish perplexity | 21,226,782,720 | 34,072,559,616 | 30,064,771,072 |
| 470527 | gruenau10 | Qwen Pile-10k | 39,630,471,168 | 85,093,777,408 | 68,719,476,736 |
| 470528 | gruenau1 | Qwen Turkish capability | 23,413,063,680 | 23,593,091,072 | 30,064,771,072 |
| 470529 | gruenau1 | Qwen Turkish perplexity | 23,413,063,680 | 23,593,091,072 | 30,064,771,072 |
| 470531 | gruenau1 | SmolLM English capability | 21,226,782,720 | 34,072,559,616 | 30,064,771,072 |

These are operational NOT-RUN outcomes, not model scores. No lane produced a `lane_result.json`.
The retained 17 source lanes were not rescored or modified.

## Frozen output hashes

- `submission_manifest.json`: `90598763f9639e44b6d078dd4399d48f121f7313435d10c1461fe228beb5b989`
- `gpu_route_selection.json`: `3d451f3eca40a18499ae56005125fe042b53e89c73b46721fe958cc857430ce2`
- `recovery_manifest.json`: `1d69e0ed66eca488c52ebb55a8ea56f00aeffe5a9e65ec8d3c22fba12874cdf4`
- `three_model_m0_composite_bundle.json`:
  `a714ce0dc891641ab0c6f99a3366d941ba2b3f8f3e2b0d4db8b28f4e90125f06`

The composite status is `partial_invalid_no_cross_model_summary`, retained count is 17,
recovered count is absent, and `normalization_allowed` is false.

## Gate

The single authorized wave is consumed. Automatic retry, a second recovery wave, threshold/route
changes, normalization and M1/M2 remain unauthorized. A later attempt requires a separately frozen
contract that explains and resolves the observed shared-GPU/visible-memory condition without
weakening the scientific evaluation semantics or modifying the preserved first recovery root.
