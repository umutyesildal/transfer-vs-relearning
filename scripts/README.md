# Script entrypoints

Use the smallest relevant directory; do not scan every historical workflow by default.

| Directory | Purpose |
|---|---|
| `study/` | Current manifest-driven pipeline and full M0→M2 study control |
| `training/` | Generic reusable training entrypoints |
| `evaluation/` | Generic reusable evaluation entrypoints |
| `data/` | Generic dataset validation/selection/synchronization |
| `corpora/` | Corpus preparation, sampling and transport |
| `operations/` | Model manifests, downloads, checks, storage retention audits and bounded operational helpers |
| `m1/` | M1-specific historical workflows; see its local family index |
| `m2/` | pre-M2, Qwen pilot and Turkish-bridge workflows; see its local family index |

The machine catalog at [`../configs/entrypoints/catalog.json`](../configs/entrypoints/catalog.json)
maps every previous flat path to its current path. All 129 pre-existing scripts remain present.
Moving a file does not make its historical contract executable or current.

Start new end-to-end work with `study/run_study.py`, not an old `submit_*.sh` file. Generic code
belongs in the Python package; scripts should remain thin entrypoints.
