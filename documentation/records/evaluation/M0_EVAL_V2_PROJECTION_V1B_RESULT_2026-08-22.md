# M0 eval-v2 projection v1b result — 2026-08-22

Status: `PASS / projection complete / metric normalization pending`

Authorized contract SHA-256: `4ee1d08f06f789c01f563cccd7ef80772fa403f51a7fe2bb440c577418f42500`

Authorized config SHA-256: `debc12012e77b323ac1ad73331a5ab4a7d66a7900e5b16efeaa3c274ad1d3f82`

Implementation/HU checkout commit: `323e695d87476fc31f07360f969763b6fcc461c7`

## Execution result

The single execution-enabled v1b wave passed the HU preflight and wrote only the fresh root:

`/vol/tmp2/yesildau/eval_v2_m0_three_model_projection_v1b`

The root contains exactly three files:

| file | bytes | SHA-256 |
| --- | ---: | --- |
| `source_registry.jsonl` | 17,058 | `a0dca252afe7c1d03e458a60a8b48d7e8d8858e0ad95e6e8be696311a0b34265` |
| `projection_manifest.json` | 853 | `9081b8eabef1ddfe1139754176cdcb1a26757fa3367d511cf81183536c8a9e0c` |
| `final_inventory.json` | 573 | `3d589db784fb0263e3ef9cc2506de3a8a920feaa00389379415d4d35e7537414` |

The source registry has exactly 24 rows: 21 canonical non-Pile rows plus three exact-prefix rows,
with eight rows per model and three rows per lane. The projection wrote zero metric rows;
`normalization_status` is `not_run_separate_boundary`, rescoring and scientific interpretation are
false, and historical sources are unchanged.

This is a source-reference closure, not the final M0 metric result. Metric extraction,
canonical normalization, comparison and scientific gate interpretation require a new separate
contract and exact authorization. M1 inventory/training and all M2 work remain closed.
