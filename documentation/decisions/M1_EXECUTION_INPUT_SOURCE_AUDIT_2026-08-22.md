# M1 execution-input source audit

**Date:** 2026-08-22
**Status:** local read-only audit; no HU/SSH, network, model loading or scoring

## Findings

The M1 synthetic-fact input is available locally and hash-verified by
`M1_SYNTHETIC_FACT_DATASET_INPUT_AUDIT_2026-08-22.md`. The repository does not contain a new
hash-closed M1 model/checkpoint or training manifest: `artifacts/models/` contains only its
`.gitkeep`, and the tracked M1 configuration files point to historical or external scratch roots.
Those paths are evidence references, not automatically usable M1 inputs.

The M1 model set is fixed and inherited from M0: OLMo-2-0425-1B, Qwen2.5-1.5B and SmolLM2-1.7B,
with their already frozen M0 revisions. There is no model-choice gate here. The retained historical
Qwen/OLMo/SmolLM artifacts are heterogeneous pilot/screening evidence; they do not constitute the
new matched M1 cohort until each model has the same synthetic-fact identity binding, its frozen
recipe, epoch trace and checkpoint registry. The controller therefore must not silently promote
historical artifacts to the prospective wave.

## Required closure before execution

1. Bind all three fixed M0 model/tokenizer manifests and revisions.
2. Freeze each model's M1 training recipe against the synthetic-fact manifest.
3. Produce a fresh M1 training manifest plus model-only epoch checkpoint manifests per model.
4. Bind the exact-prefix registry and eval-v2 registry hashes.
5. Create a separately authorized execution contract and register the adapters.

Until these are present, `scripts/study/run_m1_eval.py` can only emit a plan and must exit before
LM Evaluation Harness, model loading, HU/SSH, Slurm or output-root creation. vngrs is not part of
this closure; it opens only after M1 checkpoint selection under the M2-A/M2-B sibling contract.
