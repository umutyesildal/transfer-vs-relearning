# Three-model M0→M2 study matrix v1

**Status:** `frozen planning contract` | **Execution:** `not authorized` | **Date:** 2026-08-16

## Purpose

Operate OLMo, Qwen and SmolLM as one comparable cohort without letting chat history, partial
results, or one model's failure silently change the other models' protocol. This contract freezes
the control graph and asset identities only. eval-v1 has since been frozen and its binding updated
below; corpus, training recipes and scientific execution remain outside this contract.

The matrix reuses the existing 15-stage single-model workflow. It adds a model dimension, explicit
three-job barriers, machine-readable blockers, a durable state ledger and one micro-context Luna
packet per model/stage node.

## Exact implementation

- implementation commit: `329afaa91b4b403b86eca82f60bb3649a6f38800`;
- matrix config: `configs/studies/three_model_m0_to_m2_matrix_v1.yaml`;
- matrix config SHA-256:
  `2d1af87a99d50d2695c6f09f8947c64b0c68bc7bc17ce296a3adb74ca107a3ce`;
- operator entrypoint: `scripts/study/run_model_matrix.py`;
- operator entrypoint SHA-256:
  `ad4d64050c237630bb2b8a91e930f124fb7ac6284ca820d829c4de1b948c631e`;
- controller module: `src/transfer_vs_relearning/study/model_matrix.py`;
- controller SHA-256:
  `68970821c389125f47e04effa6c74251a9efe1c58419bf49368922f4295c8074`;
- tests: `tests/test_three_model_matrix.py`;
- test SHA-256:
  `96e06435fd70269a464c684ecdf6a5c56d9e33e2dbcb5fe3a2d2bfe83c08c321`;
- reused workflow-template SHA-256:
  `2fe1851eedd24061ad09f8d6db56ef82cd877c396d97dee38db2c1b6a1a4443c`.

The compatible local and HU target suite passed 29/29. HU dry-run reproduced 3 models, 27 nodes,
9 training nodes, 12 state-evaluation nodes and 9 three-job waves.

## Frozen model assets

| ID | Repository | Revision | Manifest SHA-256 |
|---|---|---|---|
| `olmo` | `allenai/OLMo-2-0425-1B` | `a1847dff35000b4271fa70afc5db10fd29fedbdf` | `8702b80d5b7e4c996c8ce2ff5fe771ada08ab0080bde1926c0b1f53c607303dc` |
| `qwen` | `Qwen/Qwen2.5-1.5B` | `8faed761d45a263340a0528343f099c05c9a4323` | `c9d3562b717784251fe14c2b7972660fe4a20fe4687e15f69746bc1713d2d4fb` |
| `smollm` | `HuggingFaceTB/SmolLM2-1.7B` | `effd688a12921b4cc83e3312b6feb579f70f9c71` | `e5d04302087b8b41828f734c1d88c4620a74bb80d6919de62df37b9d57dadbfc` |

These are asset identities, not selected-primary-model claims. Qwen's manifest is in the preserved
v1 screen root; SmolLM's manifest remains read-only in the preserved legacy checkout. The matrix
does not pull, relocate, rewrite, or clean either source.

## Wave graph

Every wave has exactly one node per model and a maximum of three concurrent jobs. A barrier keeps
the cohort aligned before the next wave opens.

| Wave | Nodes | State/role |
|---|---:|---|
| `m0_evaluation` | 3 | unchanged scientific eval-v1 + probes on each base model |
| `m1_training` | 3 | one frozen M1 recipe per base model |
| `m1_evaluation` | 3 | unchanged eval-v1 + probes on M1 |
| `m2_sibling_preflight` | 3 | same-M1-parent and matched-budget gate |
| `m2a_training` | 3 | fact-free Turkish sibling arm |
| `m2b_training` | 3 | controlled factual re-exposure sibling arm |
| `m2a_evaluation` | 3 | unchanged eval-v1 + probes on M2-A |
| `m2b_evaluation` | 3 | unchanged eval-v1 + probes on M2-B |
| `branch_analysis` | 3 | paired M2-A/M1 and M2-B/M2-A contrasts |

M2-A and M2-B both depend causally on the same per-model `m2_sibling_preflight`, which itself binds
the exact selected M1 checkpoint. The wave barrier may control scheduling order; it does not change
the sibling parent or permit outcome-aware recipe changes.

## Current fail-closed state

The prepared matrix intentionally uses explicit `null` config paths and named blockers where a
scientific binding does not yet exist. It never substitutes placeholders or historical recipes.

- eval-v1 is frozen but not execution-authorized;
- OLMo has a completed non-scientific qualification bundle, not a scientific M0 config;
- Qwen and SmolLM scientific M0 configs are not frozen;
- the M1 corpus and per-model recipes are not frozen;
- matched M2-A/M2-B corpus and per-model recipes are not frozen;
- matrix-level execution is false.

`run` therefore refuses external work. `run --dry-run`, `plan`, `init`, `status`, `next`, and
`packets` are local planning/inspection commands only.

## Operator and Luna usage

```bash
.venv/bin/python scripts/study/run_model_matrix.py run --dry-run

.venv/bin/python scripts/study/run_model_matrix.py init \
  --namespace /tmp/three-model-matrix-planned

.venv/bin/python scripts/study/run_model_matrix.py packets \
  --output-dir /tmp/three-model-luna-packets
```

Packet generation produces 27 independent files. Each packet contains one model, one phase, its
exact revision/manifest, dependencies and blockers; it tells Luna not to rely on chat history and
does not authorize evaluation, HU, Slurm, training, Git publication or cleanup.

## Required order to open execution

1. Close OLMo qualification parity and freeze eval-v1 semantics, dataset revisions and margins — complete in Documents 179/180.
2. Freeze scientific M0 configs for all three exact model assets.
3. Freeze one shared corpus contract and explicit per-model M1 recipes/hyperparameters.
4. Freeze matched M2-A/M2-B construction and per-model recipes from each exact M1 parent.
5. Replace the relevant `null` bindings with exact config paths and hashes.
6. Review a new execution contract and obtain separate explicit user authorization.

No step is automatically authorized by completion of the previous step.

## Prohibitions

- no scientific M0, M1 or M2 execution from this planning contract;
- no historical config substitution;
- no outcome-aware thresholds, recipes or per-model corpus changes;
- no automatic primary-model selection;
- no bypass of a wave dependency or M2 sibling-parent gate;
- no write to preserved model/run/evaluation roots;
- no cleanup, deletion, download, HU/SSH or Slurm action from Luna packets.
