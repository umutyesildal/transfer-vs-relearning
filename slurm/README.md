# Slurm entrypoints

Slurm files are grouped by scientific state/family:

| Directory | Purpose |
|---|---|
| `m0/` | Historical M0 baseline launcher |
| `m1/` | M1 acquisition, screening, retention and recovery launchers; indexed locally |
| `m2/` | pre-M2, Qwen pilot and Turkish-bridge launchers; indexed locally |
| `study/` | Reserved for future eval-v1 full-study adapters after contract freeze |

The machine catalog at [`../configs/entrypoints/catalog.json`](../configs/entrypoints/catalog.json)
preserves every old→new path. All 135 pre-existing Slurm files remain present.

A `.slurm` file is an implementation artifact, never authorization. New work must enter through
the study manifest and a separately authorized stage adapter; do not infer the next job from these
directories.
