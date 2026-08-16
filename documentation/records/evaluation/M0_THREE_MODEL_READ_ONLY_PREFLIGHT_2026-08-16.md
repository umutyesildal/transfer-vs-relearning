# Three-model scientific M0 read-only preflight record

**Date:** 2026-08-16 | **Classification:** operational preflight; no scientific result |
**Scientific work started:** no

## Bound identity

- branch: `agent/m0-evaluation`;
- HU commit: `5966678924329219d6daffa5e9bafdeae0114540`;
- family manifest: `configs/evaluation/m0_scientific_three_model_v1.yaml`;
- family-manifest SHA-256:
  `264525095a3f67b5899771069ad227a41ed431de14fd98c38168690787d2bf5d`;
- family root: `/vol/tmp2/yesildau/eval_v1_m0_scientific_three_model_v1`;
- models: OLMo, Qwen and SmolLM;
- topology: three parallel model DAGs, eight GPU lanes per model, 24 lanes total.

## Verification performed

The clean HU monorepo checkout was fast-forwarded to the bound commit. The focused HU suite passed
39/39. The non-executing family `plan` reproduced the three expected plan IDs and 24-lane topology.
The read-only family `preflight` then checked every model before any output namespace or Slurm job
was created.

All three models passed:

- frozen contract and execution-ready state;
- resolved eight-lane bindings;
- project eval-v1 readiness;
- fresh scratch output namespace and no-HU-home-write policy;
- frozen offline dataset cache identity: 404 files / 413,883,554 bytes;
- exact Python and environment-lock presence;
- historical model-manifest and frozen model revision binding;
- project evaluator-config identities;
- implementation commit ancestry, clean worktree and runtime-file hashes;
- Harness task overlays and lm-eval identity.

## Fail-closed result

The preflight exited `blocked_pre_scoring`, as required. The only per-model blocker was the frozen
false execution flag, reported under the inherited legacy check name
`qualification_execution_authorized`. The only family blocker was
`family_execution_not_authorized`.

No CPU data job, Slurm job, GPU allocation, model load, inference, scoring, result namespace,
network retrieval, training, cleanup or deletion occurred. The next permissible action is a
separate exact authorization bound to the frozen family contract and manifest; authorization must
be published fail-closed before submission.
