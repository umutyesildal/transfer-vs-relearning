# Three-model scientific M0 submission record

**Date:** 2026-08-16 | **Status:** submitted; results pending | **Automatic retry:** forbidden

## Bound execution

- HU implementation commit: `dc5a94c56c676e69edbd06378a1ba410bd0a8ec9`;
- frozen scientific contract SHA-256:
  `013f6f638176cbfd15fbe65c7d07a9dbb8d0029879e217f65e4e69bbeef765d9`;
- pre-authorization manifest SHA-256:
  `264525095a3f67b5899771069ad227a41ed431de14fd98c38168690787d2bf5d`;
- authorized manifest SHA-256:
  `7ae29ce2e8086cf7d00df22050158537869b98460572af1308db7d864c113867`;
- family root: `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`;
- family submission-manifest SHA-256:
  `3a12962501607643827571ca20e3860fa612e81617b614c5aa62d8395b896c04`.

The HU focused suite passed 40/40. The immediately preceding authorized preflight returned
`status=ready`, `blockers=[]`; all 30 per-model identity checks passed. The submit-time exact HU-home
measurement was `14,545,990,549` bytes against the `32,212,254,720`-byte limit, leaving
`17,666,264,171` bytes. HU-home writes remained forbidden.

## Job ledger

| Model | CPU/data preflight | Eight GPU lanes | Model finalizer |
|---|---:|---|---:|
| OLMo | `461860` | `461861`–`461868` | `461869` |
| Qwen | `461874` | `461875`–`461882` | `461883` |
| SmolLM | `461888` | `461889`–`461896` | `461897` |

Family finalizer `461898` has dependency `afterany:461869:461883:461897`. Each model's GPU lanes
have an `afterok` dependency on its CPU/data preflight; each model finalizer has `afterany` over its
eight lanes. The first scheduler snapshot showed all three CPU/data preflights running concurrently
on `gruenau4`, all GPU lanes dependency-pending and every finalizer dependency-pending.

Submission-manifest SHA-256 values:

- OLMo: `b60b9e300f3993a5ba9bc1a47960654e13eeec4346efc04c8d9575f48f755ca9`;
- Qwen: `e1cda12fb717f19879193598d237f2d2c95dc592053c981939a46166afb6910b`;
- SmolLM: `9d3db937a161a28e7951ecb395f81aee8fba4bc8727bc41f550b680b0b24c45e`.

## GPU route audit

Each model received five Slurm `--test-only` route probes. V100-32GB and RTX6000 were eligible and
supplied the 24 assignments. A100-80GB and RTXA6000 were eligible but outside the frozen 900-second
window. RTX3090 was tested for every model but rejected by Slurm with
`User's group not permitted to use this partition`; therefore it could not be used as a fallback.

Route-manifest SHA-256 values:

- OLMo: `221da3fcd432479c9cd55a67b942d54a882592d2a0d12020f89d57e094c67ffd`;
- Qwen: `eeadd8538bc9dd32c733479f7416b796bb8523c941e0bf85a8f3f525ccad52ac`;
- SmolLM: `1835c3b64b8875546898e8f055bf7766eedf11974707c58091da2f991e98cdab`.

Slurm's non-binding route estimates at submission were approximately 2026-08-16 19:15 for OLMo,
2026-08-18 03:05 for Qwen and 2026-08-19 10:56 for SmolLM. Actual starts may change with scheduler
state. No cancellation, reroute, second submission or automatic retry is authorized.

This record is operational submission evidence, not an evaluation result. Scientific conclusions
remain forbidden until all raw lanes and finalizers complete, identities are revalidated and the
separate deterministic normalization/gate step is frozen and run.

## Initial post-submission observation

All three CPU/data preflights completed with 8/8 tasks resolved and the exact 404-file /
413,883,554-byte cache identity. GPU dependencies opened.

OLMo `english_capability` job `461864` and SmolLM `english_capability` job `461892` then stopped as
`failed_pre_scoring` during model load on `gruenau2` RTX6000 allocations. Each observed a foreign
process using approximately 20.41 GiB, leaving only 1.39 GiB free; OLMo's warm-up allocation needed
2.77 GiB and SmolLM's needed 3.19 GiB. Neither lane produced a scientific metric. Other submitted
lanes remain running or queued and their finalizers remain active.

These are preserved operational failures, not zero scores or model-quality evidence. The submitted
wave continues under its original dependencies. No cancellation, retry, reroute or foreign-process
intervention was performed or authorized.
