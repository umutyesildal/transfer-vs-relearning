# M0 SmolLM exact-prefix recovery result — 2026-08-21

## Terminal outcome

The single authorized SmolLM recovery wave completed. SmolLM evaluated all 500 frozen historical
exact-prefix candidate-ranking probes, and finalizer `473845` hash-verified and combined that lane
with the retained OLMo and Qwen lanes. The terminal family status is `complete` for all three
models. No retained lane was rerun.

## Model results

| Model | Source | Probes | Mean-logprob top-1 accuracy | Status |
|---|---|---:|---:|---|
| OLMo-2-0425-1B | retained, hash-verified | 500 | 0.022 | complete |
| Qwen2.5-1.5B | retained, hash-verified | 500 | 0.030 | complete |
| SmolLM2-1.7B | recovery job `473844_2` | 500 | 0.032 | complete |

These scores describe the frozen candidate-ranking probe. They are not free-generation exact-match
accuracy and do not by themselves select a primary model.

## Runtime and integrity evidence

- GPU: NVIDIA A100 80GB PCIe on `gruenau9`;
- observed free GPU memory: `60,165,259,264` bytes;
- frozen minimum: `21,474,836,480` bytes;
- SmolLM lane-result SHA-256:
  `c52447dd603691b5c135801633907abe7e8bf0ddacb38ec89120ce65b76e3771`;
- combined family-result SHA-256:
  `1bb5e066767d775b104965122490b873bd147b3f80292bb211175508b3aa03f8`;
- family-inventory SHA-256:
  `7095e5f0542ab6c7e1d776d00bb3e0ffae84940f7216cf95350171a34b4c3b69`;
- inventory: 21 listed files / 618,428 bytes;
- finalizer stderr: zero bytes;
- finalization timestamp: `2026-08-21T17:27:30.934035+00:00`.

The finalizer validated every referenced result artifact by path, byte count and SHA-256. `squeue`
became empty for both submitted jobs and complete final artifacts exist. `sacct` was unavailable
because the cluster's Munge/SlurmDBD authentication failed; this is missing accounting metadata,
not run failure.

## Current boundary

The exact-prefix M0 panel is complete for OLMo, Qwen and SmolLM. The authorization is consumed and
no retry, second submission, normalization, primary-model promotion, M1/M2 work, cleanup or
deletion is authorized by this result. The independent Qwen Pile-10k recovery remains separate.
