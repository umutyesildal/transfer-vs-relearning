# M1 fixed three-model set

**Date:** 2026-08-22
**Status:** user-confirmed design clarification; no execution authorization

M1 uses exactly the same model families and immutable revisions as the M0 matrix:

| model | revision |
|---|---|
| `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` |
| `Qwen/Qwen2.5-1.5B` | `8faed761d45a263340a0528343f099c05c9a4323` |
| `HuggingFaceTB/SmolLM2-1.7B` | `effd688a12921b4cc83e3312b6feb579f70f9c71` |

M1 does not perform candidate selection or substitute a new model. Each member receives the
same eval-v2 identity, synthetic-fact data identity and matched logical M1 schedule; memory-safe
precision/microbatch decompositions may differ only when explicitly documented without changing
the effective scientific budget. A null `selected_primary_model` records that no single winner
has been promoted; it is not a blocker for the fixed three-model wave.
