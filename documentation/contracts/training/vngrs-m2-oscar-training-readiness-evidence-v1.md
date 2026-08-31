# vngrs M2 OSCAR training-readiness evidence contract v1

**Date:** 2026-08-31  
**Lifecycle:** `FROZEN / UNEXECUTED / SINGLE CPU EVIDENCE WAVE`  
**Contract ID:** `vngrs-m2-oscar-training-readiness-evidence-v1`

## Purpose

Document 200 closed exact three-model M2 block materialization, but training remains unopened.
This contract freezes the next narrow evidence step. It does not train or evaluate a model. It
read-only validates the exact M1 epoch-036 parent assets, creates six execution-disabled sibling
configs, computes a conservative storage gate and prepares an all-250-fact human-review handoff.

## Frozen inputs

- exact block root, immutable/read-only:
  `/vol/tmp2/yesildau/vngrs_m2_oscar_exact_blocks_adapter_repair_v1`;
- block manifest SHA-256:
  `68dd7ca18d794c09ce3e1b1aa8b2b4b9f6ddb175195959b24b0103c7ea65dd63`;
- block final-audit SHA-256:
  `7475686c16d8aff55acfa18154cd5b6e686ee7aa1083547e28b6657f1c1b70a6`;
- 250-row fact registry SHA-256:
  `784f78a5a182c329b4b995ee1a97c580da994059a18b1f9702ec657569ccbfec`;
- OLMo epoch-036 snapshot/model manifests:
  `0226c6b0c70415c3f31049e275fa78bfe9b155af60819664bdfe4ae730ae0a57` /
  `e005a926daf95a051832438988df4c6416afe1276de2b9ba4c6574d3f92356b9`;
- Qwen epoch-036 snapshot/model manifests:
  `f4d839f49672c999dc3c0cf9cbdac0caf139c9a385cbf85366a161d6d998d831` /
  `e9d5bd7245ae3c22397fca30edd1489d218983f20998f986dd434efd99810dee`;
- SmolLM epoch-036 snapshot/model manifests:
  `9ba7cdec401f5c5f9e334a3fc75e5ea5c5899f78f78219e24bdf5c6f0712da7c` /
  `235bfb12a85d3c1196126349c6b11892ca5d2b4e2aac1cfcac251695bdf9c3ad`.

All prior M1, corpus, split and block roots remain read-only. This wave may read model-only parent
files solely to verify the existing per-file SHA-256 registry. It may not load parameters into a
model, allocate optimizer/gradient state or perform forward/backward/inference.

## Exact outputs

Fresh root:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_training_readiness_evidence_v1
```

The one CPU wave must produce:

1. `parent_registry.json`, covering all exact epoch-036 config/tokenizer/weight assets;
2. `storage_estimate.json`, conservatively accounting for 60 model-only checkpoints, three
   preserved future smoke states, three concurrently active training states, existing blocks,
   fixed 20 GiB headroom and a 1.25 safety multiplier;
3. six execution-disabled OLMo/Qwen/SmolLM × M2-A/M2-B configs and a validated config manifest;
4. an exact all-250-row fact review packet and standalone HTML interface;
5. a hash-closed evidence manifest and terminal final audit.

The HTML exports decisions bound to the exact fact-registry SHA-256. Human verdict entry is not
performed by this wave. After terminal PASS, the HTML and packet may be copied read-only to the
local workspace only if each is at most 1 MiB and their combined size is at most 2 MiB; the HU
source files remain unchanged.

Terminal PASS is
`EVIDENCE_PREPARED_AWAITING_FACT_REVIEW_AND_GPU_SMOKE`. It explicitly keeps
`ready_to_train=false`.

## Scientific recipe preserved

The six configs retain Document 191 unchanged: same M1 epoch-036 parent per sibling pair, exact
model-native blocks, sequence 512, 49,938,432 tokens/arm, 762 updates, effective batch 128,
LR 1e-5, BF16, seed 42 and exact checkpoint updates
`76,152,229,305,381,457,533,610,686,762`. No outcome-aware choice or primary-model promotion is
permitted.

## Frozen implementation

```text
wave config       f00828aa3562f2b09b0c5074604506541e2b089c80798b886a9f2d294467a153
preparation v2    bd14add33d812c2afd0145bb9f136b33fe9596d2a8dd1e726ba22637108917d7
readiness runner  81cffac8931892699103e67f73269b3a0287849133588356a1412121a9597dc2
family preparer   fb00ca7ff7a498b930db7d91034c7d1dc3e4506b110c84c60c84e4ba14d22f98
family validator  9190bfb25220cd8c951efdcb30d68219e67acbf68a5e65c032a05e7cc4b1d36c
Slurm             efa8ee3c18e96e42475a624021cd74ede5b3b773c7af99fa867fe7957fc485f4
submitter         d00bbd2ba05caca36b3b510ac95355f33c8bd4697a1b37dc208c30b44962b993
focused tests     dc1dc769cd3dd84e12b345f13f89b2922514e7ade98254b7bc45259f1ee6fae6
scientific plan   2c8d3aae2a631dc8e1eb7c8bcaccb4dcb300ad3a84d62875520fd62facc94494
```

Compatible block/training/output/eval/control suite: `67 passed`. Python/Bash syntax, YAML parse
and `git diff --check`: PASS.

## Authority boundary

This document authorizes nothing by itself. A later exact SHA-bound user authorization may permit
ordinary non-force push, preservation-checked HU fast-forward, one 4-CPU/64G CPU evidence job and
the bounded read-only review-handoff copy described above.

It does not authorize human verdict fabrication/entry, GPU, optimizer smoke, model inference,
scientific M2-A/M2-B training, evaluation/scoring, retry, cleanup, deletion or prior-root mutation.
A terminal result must be documented before the GPU-smoke or training contract can open.
