# Document 143 — Qwen M2/M3 Artifact Retention Freeze and Storage Audit

**Date:** 3 August 2026  
**Status:** Completed — model-only retention freeze; cleanup not performed  
**Precondition:** Document 140a independent review — `PASS WITH CONCERNS`, no blocker or major
issue  
**Scientific boundary:** No training, evaluation, checkpoint selection, gate change, or deletion
was performed.

## 1. Closure decision

The four completed `checkpoint-128` Qwen M2/M3 endpoints were frozen as model-only retention
copies on approved HU scratch. The original run trees remain untouched, including optimizer,
scheduler, RNG, trainer, and training-argument state. No cleanup was performed.

The retention copy is not a backup with durability guarantees; it is a compact, hash-verified
scratch artifact for reproducible continuation and controlled later lifecycle decisions.

## 2. Retention artifact

Retention root:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/retained_model_only_20260803T073244Z
```

Manifest:

```text
/vol/tmp2/yesildau/qwen_m2_m3_v1/retained_model_only_20260803T073244Z/model_only_retention_manifest.json
```

Manifest SHA-256:

```text
195aae05d65a580da2d98d8beb192244ac3a2a7046107ba1740208988f1082fa
```

The retention procedure was executed from repository commit
`9f1755219ba003d4aaf962558b3c0512fc74f99a`, using
`transfer-vs-relearning/scripts/freeze_qwen_m2_m3_model_only.py`.

| Endpoint | Source checkpoint | Source size | Retention contents |
|---|---|---:|---|
| `m2_clean_seed42` | `/vol/tmp2/yesildau/qwen_m2_m3_v1/runs/m2_clean_seed42/20260801T114914Z_m2_clean_seed42_0128283b/checkpoints/checkpoint-128` | 8.7 GiB | model-only |
| `m2_clean_seed43` | `/vol/tmp2/yesildau/qwen_m2_m3_v1/runs/m2_clean_seed43/20260801T120303Z_m2_clean_seed43_60dbf6d3/checkpoints/checkpoint-128` | 8.7 GiB | model-only |
| `m3_fact_seed42` | `/vol/tmp2/yesildau/qwen_m2_m3_v1/runs/m3_fact_seed42/20260801T115809Z_m3_fact_seed42_2687a927/checkpoints/checkpoint-128` | 8.7 GiB | model-only |
| `m3_fact_seed43` | `/vol/tmp2/yesildau/qwen_m2_m3_v1/runs/m3_fact_seed43/20260801T120759Z_m3_fact_seed43_907468f1/checkpoints/checkpoint-128` | 8.7 GiB | model-only |

Total retained size is approximately **12 GiB**. The manifest records each source path, source
training-manifest hash, retained path, size, and source/retained SHA-256 pair.

### Included files per endpoint

- `model.safetensors`
- `config.json`
- `generation_config.json`
- `tokenizer.json`
- `tokenizer_config.json`
- `chat_template.jinja`

### Explicitly excluded files

- `optimizer.pt`
- `scheduler.pt`
- `rng_state.pth`
- `trainer_state.json`
- `training_args.bin`

All **24/24** retained files passed `sha256sum -c SHA256SUMS.txt`. The original source files were
not overwritten or removed.

## 3. Storage and path audit

The required capacity and inode checks were repeated before and after the retention copy.

| Filesystem | Capacity observation | Inode observation |
|---|---|---|
| HU home filesystem `/vol/fob-vol6` | 1.3 T total, 609 G available, 53% used | 53% used |
| `/vol/tmp` | 19 T available | 3% used |
| `/vol/tmp2` | 113 T available | 3% used |

Resolved project paths remain on scratch:

```text
/vol/tmp/yesildau/transfer-vs-relearning/runs
/vol/tmp/yesildau/transfer-vs-relearning/artifacts
```

The retained model-only root is also under `/vol/tmp2/yesildau`. No M2/M3 retention copy was
placed in HU home. The post-freeze large-home-file scan found only the previously authorized
Qwen M1 model copies and expected Conda/CUDA library files; it found no new M2/M3 model artifact
in home.

The home `du -xsh` observation again reached the 90-second NFS timeout. This reproduces the
Document 140a procedural concern rather than indicating a storage-placement failure. Capacity,
inode, resolved-path, retention-size, and large-home-file observations were still recorded. No
cleanup decision is based on the incomplete home `du` value.

## 4. Scientific and lifecycle interpretation

This freeze preserves the exact evaluated endpoint models needed for the completed scientific
record. It does not promote the primary gate: the frozen decision remains
`primary_success_criterion_not_met`. It also does not convert the exploratory M3 recovery into a
confirmatory result.

The original scratch run trees and all optimizer/trainer state remain available. Any future
cleanup of duplicate checkpoints, optimizer state, caches, or verbose logs requires a separate
retention review; deletion or overwriting of selected models, unique datasets, canonical
manifests, or non-reproducible results requires explicit approval.

## 5. Current stop boundary

The authorized M2/M3 evidence and artifact closure work is complete up to this retention freeze.
Do not launch a new seed, training family, changed factual dose, checkpoint search, M3-lexical arm,
gate change, threshold relaxation, or 25,000-fact run without a separately approved scientific
amendment.

The current package is now ready for the next independent inspection, using Documents 136, 138,
140a, 142, and this Document 143 as the current evidence chain.
