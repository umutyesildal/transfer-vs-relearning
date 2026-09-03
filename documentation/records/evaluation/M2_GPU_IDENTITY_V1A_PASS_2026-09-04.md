# M2 GPU identity V1A qualification PASS

Date: 2026-09-04. Status: single authorized qualification consumed, PASS.

User authorization bound contract SHA-256
`c58e62d87d418a7654d87d03c622150e2160890475c428300ebf8bd0f2eaba4d`
and commit `5430055a76b9ade7c755db24ce1bea4bf3f3752e`.
Ordinary non-force push and clean HU preservation-check/fast-forward from bde924c completed.
All 49 CPU-only targeted tests passed locally and on HU. Contract, gate and runtime-lock hashes
matched. Fresh root absence/non-symlink/path checks and duplicate-job guard passed. Scratch
available bytes were 121,546,723,033,088; available inodes 2,283,843,918.

Exactly one scheduler test-only passed (hypothetical ID 484042); exactly one real job 484043
was submitted. `scontrol` reports COMPLETED, ExitCode=0:0, Requeue=0, Restarts=0, gruenau10,
00:55:25–00:55:42 cluster time, duration 17 seconds. Resources were one A10080GB, eight CPUs,
64G host RAM, ten-minute maximum. Stderr was empty.

## Audited result

Root: `/vol/tmp2/yesildau/vnd_m2_oscar_gpu_identity_qualification_v1a`.
Audit: `gpu_identity_audit.json`, SHA-256
`ee2c7f395569c8b37f94e6c4fbc0a82eb5e475f32df695008f0e88591563059f`.

- Status: pass; Torch 2.6.0+cu124; NVIDIA A100 80GB PCIe.
- CUDA_VISIBLE_DEVICES=0, SLURM_JOB_GPUS=0, logical_device=0.
- Raw native `_CUuuid`: `4fc987af-7ab7-e2c3-e2bb-eec01fb1ba9d`.
- CUDA-derived/SMI-matched UUID: `GPU-4fc987af-7ab7-e2c3-e2bb-eec01fb1ba9d`.
- CUDA free/total bytes: 66,787,147,776 / 85,093,777,408.
- SMI free/total bytes: 66,787,999,744 / 85,899,345,920.
- Both free samples exceed the unchanged 21,474,836,480-byte gate; total difference is <1 GiB.

The real runtime confirms the bare-UUID representation and successful normalization. This
qualifies one allocation; it does not reconstruct the historical V1B cause or guarantee future
free memory. No model/tokenizer/checkpoint loading, inference, evaluation, training, cleanup,
source mutation, fallback or retry occurred. Prior roots and all 21 complete evaluations remain
preserved. The 42 missing/failed scientific tasks have NOT been recovered.

## Next boundary

Prepare a separately bound 42-task recovery with immutable input/completed-output hash inventory,
canary-first failure containment and combined 63-state finalization. Qualification PASS alone
does not authorize that inventory's external access, publication or scientific execution.
