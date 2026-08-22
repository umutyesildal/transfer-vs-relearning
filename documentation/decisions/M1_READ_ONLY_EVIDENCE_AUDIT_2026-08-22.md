# M1 read-only evidence audit — local control-plane pass

**Date:** 2026-08-22  
**Scope:** local repository/control-plane files only  
**Result:** `BLOCKED — no scientific gate closed`  
**HU/SSH, network, download, scoring, inference, Slurm/GPU, training:** not used

## Purpose

This is the next bounded step after the M1 preparation and blocker-resolution packet. It checks
whether the existing local eval-v2 registry, scientific-input config, historical trajectory plan
and preserved provenance configs are sufficient to close any M1 pre-execution gate. It does not
retrieve missing benchmark/model artifacts and does not reinterpret old execution configs as a new
authorization.

## Inputs checked

| Path | Local SHA-256 | Finding |
|---|---|---|
| `configs/evaluation/eval_v2_registry.yaml` | `0721412c651f5b112f531e69b53c98ccdb3633bee4888571bd7039d3f693229d` | frozen eval-v2 protocol; execution not authorized |
| `configs/evaluation/eval_v2_scientific_inputs_v1.yaml` | `e6afb5ed3cd210d9c429622995ccbf8a0da5fee4cf444e6fc979d8377d68b879` | exact non-Pile dataset/revision and control hashes present |
| `documentation/contracts/evaluation/eval-v2.md` | `95eec6fc5a9dd7ce6da3185dfe20e2a183ad3850194c15f88a1299f09a43c6a3` | frozen metric/missingness contract |
| `configs/evaluation/m1_historical_trajectory_inventory_v1.yaml` | `1a027df534fa06636f95bb6d1507e18fef8613c39c64d8aa4cd002043513285c` | prepared, unexecuted, read-only historical inventory |
| `configs/experiments/m1_provenance_screen_v3.yaml` | `4345042d8a2a02255f1b4553cd089cedbd5f792a5e2a35fdf48c9306ba37b5f4` | historical/unauthorized candidate config; not reused |
| `documentation/151ab_MEASUREMENT_DESIGN_AUTHORITY_AND_MINIMAL_BASELINE_CONTRACT_TR.md` | `3ff0823f8a4aa5f806ab451abfffa989e0d70f1b1ca6b240229306cfac99c06c` | frozen measurement authority; review fields unresolved |

## Findings

### A. Eval-v2 identity closure: `PASS` for protocol identity only

The local control plane has exact identities for WikiText, BLiMP, HellaSwag, WinoGender and the
cross-domain `trwiki-20260601` control, plus the factual registry hashes. Pile-10k is explicitly
retired. The active Harness task list contains seven canonical lanes and the exact-prefix
supplement remains mandatory.

This closes only protocol identity. It does **not** create the missing primary Turkish in-domain
held-out manifest required by 151ab, and it does not authorize scoring.

### B. Benchmark registry: `BLOCKED`

The frozen 151ab primary/secondary Turkish design and the active eval-v2 registry are not yet one
complete evidence object:

| Item | Local state | Decision |
|---|---|---|
| TurBLiMP in eval-v2 scientific inputs | `juletxara/turblimp` revision `cce94ca...` | protocol identity exists |
| TurBLiMP in 151ab measurement authority | GitHub `ezgibasar/TurBLiMP`, revision `297de13...`, 16 `data/base/` CSVs | separate frozen design identity; reconciliation required |
| TurkishMMLU | not in active eval-v2 Harness task list | secondary design is not execution-bound |
| Turkish EXAMS | not in active eval-v2 Harness task list | secondary design is not execution-bound |
| Item/ordered-ID/prompt/choice/evaluator hashes | not present as complete local evidence package | `blocked_by_benchmark_registry` |

The two TurBLiMP identities cannot be silently merged. A future read-only reconciliation must
choose one exact source/evaluator identity and record why it matches the frozen measurement role.
No benchmark score was produced in this pass.

### C. Source-model provenance: `BLOCKED`

The repository contains candidate IDs and requested revisions in historical configs, but not a
new complete immutable artifact/provenance package for M1:

| Model | Local identity | Current scientific role |
|---|---|---|
| OLMo-2-0425-1B | revision `a1847d...` in historical config | provenance-first candidate |
| Falcon-RW-1B | revision `e4b987...` in historical config | English comparator |
| Qwen2.5-1.5B | revision `8faed7...` in historical trajectory plan | multilingual positive control |
| Pythia-1.4B | revision `0da31d...` in old v3 screen config | preserved historical screen; not added to 151ab set |

Missing or not yet reconciled locally are the complete model/tokenizer artifact manifests,
repository metadata hashes, runtime compatibility evidence, license/stage rows and truthful
Turkish-exposure labels required by 151ab. Historical configs remain `execution_unauthorized` or
`prepared_unexecuted`; they cannot be promoted into a new M1 run.

### D. Measurement design: `BLOCKED`

The local eval-v2 config freezes the general retention/factual protocol, but 151ab still requires
user-reviewed values for:

```text
turkish_heldout_v1.sha256
english_retention_v1.sha256
delta_TurBLiMP_equivalence_margin
delta_EN_retention_margin
benchmark_floor_ceiling_saturation_rule
```

The primary Turkish in-domain split is still absent. `trwiki-20260601` is only the cross-domain
control and cannot be substituted for the primary adaptation-corpus split. The expanded 151ab
ledger (item hashes, rendering, tokenizer/masking, NLL/BPB denominator, bootstrap and evaluator
identities) is not complete either.

## Gate decision

```text
eval_v2_protocol_identity = PASS
benchmark_registry_evidence = BLOCKED
source_model_provenance = BLOCKED
measurement_design = BLOCKED
primary_corpus_and_in_domain_split = BLOCKED
ready_to_train = false
```

This audit therefore closes no gate and creates no executable M1 contract. It does establish the
next concrete work order:

1. reconcile the two TurBLiMP identities and bind TurkishMMLU/EXAMS roles, if retained;
2. reconcile model/tokenizer/artifact provenance from existing immutable evidence only;
3. review and freeze the five 151ab measurement fields plus the expanded ledger;
4. separately resolve the primary Turkish corpus/split decision;
5. only after all four pass, draft a new SHA-bound M1 execution contract.

## Local validation

- Exact hashes above were computed locally.
- Current YAML control files parse with Ruby/Psych.
- Python syntax checks for the study and trajectory tooling pass.
- No external state, HU root or prior artifact was read or changed.
