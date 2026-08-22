# eval-v2 M0 Hash-Closed Projection v1

**Lifecycle:** read-only source discovery frozen; projection prepared and unexecuted

**Execution authorized:** no

## Objective

Close the M0 source-evidence boundary without model load, inference or rescoring. The operation
selects exactly seven completed non-Pile scientific lanes for each of OLMo, Qwen and SmolLM, then
attaches the completed three-model historical exact-prefix candidate-ranking supplement.

The projection is a reference artifact, not metric normalization. It records immutable source
paths and SHA-256 values so a later separately frozen normalizer can consume exactly the same raw
evidence.

## Frozen semantic rules

- protocol: `eval-v2`;
- model order: `olmo`, `qwen`, `smollm`;
- required scientific rows: `3 models × 7 non-Pile lanes = 21`;
- exact-prefix supplement: one complete 500-probe lane per model;
- total source-registry rows: 24;
- Pile-10k: forbidden;
- rescoring, inference and model loading: forbidden;
- missing/incomplete/hash-drifted evidence: fail closed, never zero or imputed;
- historical source paths: read-only;
- output root: fresh and reference-only.

## Source manifests

The read-only discovery scope and exact paths are frozen in
`configs/evaluation/eval_v2_m0_projection_v1.yaml`. The three retargeted
`evaluation_results.json` SHA-256 values remain unresolved. A bounded HU source-discovery pass may
only read those three exact files, the exact-prefix family result, and the lane-result/artifact
paths explicitly referenced by them. It may emit evidence to the caller but must write no HU file.

The discovery pass requires a separate exact user authorization bound to this document and the
prepared config SHA-256. Until its observed hashes are inserted and the implementation commit/file
hashes are frozen, the projection phase remains prepared rather than frozen.

## Projection outputs

After a separate exact authorization, the projector may create the one fresh output root and write:

- `source_registry.jsonl`: exactly 24 hash-verified source references;
- `projection_manifest.json`: plan/config identities and explicit no-rescore status;
- `final_inventory.json`: one-way inventory excluding itself.

It writes zero normalized metric rows. Metric extraction, deltas, gates, model comparison and M0
scientific closure require a later normalization contract and authorization.

## Failure semantics

The operation stops before writing when any required manifest, lane, artifact, model revision,
semantic classification, byte count or SHA-256 differs. An existing output root is never resumed
or overwritten. Failure does not invalidate historical raw evidence and does not open M1.

## Prohibitions

- no HU-home write, network, GPU, Slurm, model load, inference or scoring;
- no historical mutation, relocation, deletion or cleanup;
- no Pile row or fallback;
- no normalization, primary-model selection, M1/M2 execution or publication;
- no reuse of an old M0 execution authorization.
