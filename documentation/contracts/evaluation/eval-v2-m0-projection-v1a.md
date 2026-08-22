# eval-v2 M0 Hash-Closed Projection v1a

**Lifecycle:** source-binding discovery passed; projection prepared and unexecuted

**Execution authorized:** no

## Objective

Freeze the source identities discovered by the authorized 2026-08-22 read-only pass without
rescoring or changing any historical evidence. This contract is the preparation boundary for a
later local projection registry. It does not normalize metrics and does not close the scientific
M0 gate by itself.

## Frozen source closure

The discovery pass verified exactly four top manifests and 24 lane-result bindings: 21 required
non-Pile eval-v2 lanes (seven for each of OLMo, Qwen and SmolLM) and three historical exact-prefix
supplement rows. Model repositories and immutable revisions matched the eval-v2 registry. The
source paths and hashes are recorded in the append-only discovery record:

`documentation/evaluation/M0_EVAL_V2_SOURCE_BINDING_DISCOVERY_2026-08-22.md`

The four observed top-manifest hashes are:

| source | SHA-256 |
| --- | --- |
| OLMo `evaluation_results.json` | `2adcbea6caeec9a3731b9f3fec4f9c3f3abf1b8c65caff750907e4b0d98c78a1` |
| Qwen `evaluation_results.json` | `18053c89efcafa7bc01f2b90988afbcf036786d3617f85ab8538e4a82c400f21` |
| SmolLM `evaluation_results.json` | `2ecc937cedd3860b84e999dbbd311b85c28db1b586d36b08a747419a64675ec4` |
| exact-prefix family result | `1bb5e066767d775b104965122490b873bd147b3f80292bb211175508b3aa03f8` |

The complete 24-row lane binding, including each lane-result hash and byte count, is preserved in
the discovery record and is the sole source for the subsequent projection.

## Projection boundary

A separately authorized projection may write only to the fresh root declared in the v1a config:

- `source_registry.jsonl` — exactly 24 immutable source references;
- `projection_manifest.json` — config and protocol identities plus explicit no-rescore status;
- `final_inventory.json` — one-way inventory that excludes itself.

The projection writes zero metric rows and performs no metric extraction, normalization, delta,
gate, model-selection, inference or model loading. Pile-10k remains excluded. Existing source
roots and all prior evidence remain read-only.

## Failure semantics and prohibitions

The operation fails closed on any missing source, lane drift, hash mismatch, model identity drift,
semantic-classification drift, duplicate lane or non-fresh output root. No inferred or zero-filled
metric is permitted. HU writes, network retrieval, GPU/Slurm, training, evaluation/scoring,
normalization, cleanup, deletion, publication and M1/M2 execution are outside this contract.
