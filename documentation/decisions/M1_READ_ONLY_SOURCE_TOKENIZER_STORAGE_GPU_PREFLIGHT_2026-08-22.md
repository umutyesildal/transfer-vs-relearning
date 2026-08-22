# M1 read-only source, tokenizer, storage and GPU preflight

**Date:** 2026-08-22  
**Status:** `PARTIAL_PASS_SCHEDULER_ACCESS_BLOCKED`  
**Scope:** one user-authorized read-only HU preflight  
**Training/evaluation:** not run  
**HU writes:** none

## Result summary

| Check | Result | Evidence |
|---|---|---|
| OLMo model manifest | PASS | File exists; 11,047 bytes; recorded SHA-256 matches |
| Qwen model manifest | PASS | File exists; 3,531 bytes; recorded SHA-256 matches |
| SmolLM model manifest | PASS | File exists; 3,407 bytes; recorded SHA-256 matches |
| Tokenizer identity in manifests | PASS | Native tokenizer class/revision fields were present and readable |
| `/vol/tmp2` capacity/inodes | PASS | 113T available; 2,284,305,772 free inodes |
| `/vol/fob-vol6` capacity/inodes | PASS | 605G available; 158,447,093 free inodes |
| RTX3090 scheduler inventory | CONDITIONAL PASS | `guppi5–8` visible as `idle`; queue was empty |
| RTX3090 allocation/process-level VRAM | BLOCKED | User group is not permitted to use `wbimlgpu` or `viscomgpu`; no allocation was made |

## Exact manifest evidence

| Model | Manifest path | Bytes | SHA-256 | Resolved revision | Tokenizer |
|---|---|---:|---|---|---|
| OLMo-2-0425-1B | `/vol/tmp2/yesildau/m1_provenance_screen_v3/models/allenai__OLMo-2-0425-1B/model_manifest.json` | 11,047 | `8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | `TokenizersBackend`, length 100,278 |
| Qwen2.5-1.5B | `/vol/tmp2/yesildau/m1_cross_family_screen_v1/models/Qwen__Qwen2.5-1.5B/model_manifest.json` | 3,531 | `c9d3562b717784251fe14c2b7972660fe4a20fe4687e15f69746bc1713d2d4fb` | `8faed761d45a263340a0528343f099c05c9a4323` | `Qwen2Tokenizer` |
| SmolLM2-1.7B | `/vol/fob-vol6/mi25/yesildau/transfer-vs-relearning/artifacts/models/HuggingFaceTB__SmolLM2-1.7B/model_manifest.json` | 3,407 | `e5d04302087b8b41828f734c1d88c4620a74bb80d6919de62df37b9d57dadbfc` | `effd688a12921b4cc83e3312b6feb579f70f9c71` | `GPT2Tokenizer` |

All three manifest bytes were read and hashed remotely. Every hash matched the value already
bound in the local M1 draft configs. No model weights or tokenizer files were copied or mutated.

## Storage evidence

The read-only filesystem checks reported:

- `/vol/tmp2`: 140T total, 27T used, 113T available, 20% used; 3% inode use.
- `/vol/fob-vol6`: 1.3T total, 672G used, 605G available, 53% used; 53% inode use.

Both roots have ample capacity for the planned scratch-only M1 wave. This is a capacity result,
not permission to create the M1 output root.

## GPU/access evidence

`sinfo` showed the following scheduler-level inventory, with an empty queue:

```text
guppi5–7 | gpu:rtx3090:3 | idle | none
guppi8  | gpu:rtx3090:4 | idle | none
```

However, both `srun --test-only --partition=wbimlgpu --gres=gpu:rtx3090:1 ...` and the same
test-only request against `viscomgpu` failed with:

```text
User's group not permitted to use this partition
```

Therefore this wave did **not** allocate a GPU, run `nvidia-smi`, or inspect process-level free
VRAM. The scheduler's `idle` state cannot prove that a node is free of foreign processes. The
read-only `sacctmgr` association query was also unavailable because the HU Munge/SlurmDBD
authentication socket failed. The 3090 suitability verdict is consequently
`blocked_by_partition_access`, not a hardware failure.

## Gate and next action

The source/tokenizer and storage portions of the preflight pass. The M1 execution gate remains
closed because process-level GPU cleanliness/access and the project-level measurement-design
blockers are unresolved. No training contract, HU output root, Slurm job, model load, evaluation,
download, cleanup or deletion was performed.

The next safe operational step is to obtain the correct HU account/partition association (or a
permitted RTX3090 route) and repeat only the test-only GPU preflight. Once that operational check
and the existing benchmark/measurement evidence gates are closed, a separate SHA-bound M1
execution contract can be prepared and explicitly authorized.
