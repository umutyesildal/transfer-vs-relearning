# vngrs three-model M2 D0 corpus closure contract v2

**Status:** `FROZEN / UNEXECUTED — PHASE 1 ONLY`  
**Owner:** thesis project  
**Created:** 2026-08-28  
**Base scientific contract:** `vngrs-m2-three-model-d0-v1`

## Purpose

Retry the still-unexecuted scientific D0 Phase 1 on one fresh root after V1C durably proved that
the accepted metadata/footer package was rejected only because the preflight used the wrong
inventory serialization. V2 changes no corpus, model, audit, split, review, tokenizer, storage or
HTTP field from V1. It corrects the inventory hash semantics and preserves the occupied V1 root as
terminal operational evidence.

## Preserved V1 terminal evidence

The authorized V1C job `481836` ran from commit
`aad286d479a237096053b95ad5d91ea10d077bd3`. It stopped before network or materialization and
wrote exactly one compact terminal record:

```text
/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v1/control/preflight_failure.json
```

That record binds:

- status `BLOCKED_OPERATIONAL_PREFLIGHT`;
- exception `ValueError: accepted read-only evidence closure drift`;
- `network_requests=0`;
- `source_objects_written=0`;
- `ready_to_train=false`;
- `automatic_retry_authorized=false`.

The preserved file is exactly 351 bytes with SHA-256
`54e3f59abd2df14cc00acb260dbe13c0f90dd5a18a22e8d0eb9089f31382a1ce`. Both the submitter and
in-job preflight must reproduce that exact identity; mere path existence is insufficient.

The V1 root is immutable evidence. V2 does not delete, move, overwrite, resume or reuse it.

## Evidence-integrity correction

The accepted read-only metadata/footer root remains:

```text
/vol/tmp2/yesildau/luna_vngrs_metadata_footer_feasibility_v1
```

The post-V1C read-only audit reproduced the frozen file count and bytes exactly:

```text
regular files = 104
regular bytes = 18,025,945
```

It also proved that the historical inventory SHA-256 is the SHA-256 of lexically sorted UTF-8
records serialized exactly as:

```text
<relative_path><ASCII SPACE><decimal_size><LF>
```

That exact payload reproduces:

```text
120cdd7b21e161bf981cf8191fa278a11829d3fc5c155b71ed4bc8836e27f1d3
```

V1 preflight instead hashed canonical JSON objects and obtained
`268ebe818021efcbd7a96658e4371fc28a4594a8c6259d473369166bdda550dc`. This was a validator
semantic mismatch, not source-root drift. V2 freezes the historical line serialization explicitly
and rejects the canonical-JSON inventory hash.

The 18,025,945-byte figure is the compact read-only metadata/footer evidence package. It is not the
future corpus download. The exact 32 selected Parquet objects still total `9,502,315,428` bytes
and may be retrieved only by an exactly authorized V2 Phase-1 wave beneath the new root.

## Fresh V2 root

V2 uses exactly:

```text
/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v2
```

It must be absent before execution. Preflight also requires the V1C failure artifact to remain
present, the reviewed Git checkout to be clean and exact, no duplicate `vngrs-m2-d0-v2` job, HU
home below 30 GiB, at least 40 GiB and 1,024 inodes available on the resolved scratch parent, and
the same closed 32-object registry.

If a pre-network V2 exception occurs, the sole V2 root is created only to atomically persist
`control/preflight_failure.json`. The record refuses overwrite and binds the error, job, commit,
zero network requests, zero written source objects and no retry authority.

## Inherited scientific protocol

Every V1 scientific field is inherited unchanged, including:

- repository `vngrs-ai/vngrs-web-corpus` at revision
  `ee5c6201ee84457a18182bfc483a7d8a7f3655ba`;
- the exact systematic 32-of-284 selected paths and their immutable LFS-derived identities;
- `9,502,315,428` full-object bytes and `9,468,474,036` Parquet compressed bytes;
- the 10 GiB cumulative HTTP-response bound;
- schema and stable-document identity rules;
- the Max-aligned lightweight audit and frozen Relation V2 contamination surfaces;
- the deterministic 10,000-document held-out split;
- the 64-document review packet and stop at `AWAITING_HUMAN_REVIEW`;
- future OLMo, Qwen and SmolLM tokenizer accounting;
- `trwiki-20260601` as control-only with zero training rows;
- `ready_to_train=false` throughout Phase 1.

Phase 1 performs no model-weight load, inference, scoring, GPU work or training. A successful
Phase 1 stops before tokenizer accounting and D0 PASS.

## Exact implementation route

```text
config:    configs/corpora/vngrs_m2_three_model_d0_v2.yaml
preflight: transfer_vs_relearning.corpora.vngrs.d0_preflight_v2
runner:    scripts/corpora/run_vngrs_m2_d0_v2.py
submitter: scripts/corpora/submit_vngrs_m2_d0_v2_phase1.sh
Slurm:     slurm/m2/materialize_vngrs_m2_d0_v2_phase1.slurm
job name:  vngrs-m2-d0-v2
```

The submitter performs one `sbatch --test-only` followed by exactly one real CPU submission. Slurm
stdout/stderr remain `/dev/null`; terminal pre-root evidence is persisted beneath the sole V2
root. No other V1 launcher is eligible for V2.

## Authority boundary

Preparation and freeze do not authorize push, HU fast-forward, SSH, Slurm, public HTTP retrieval,
corpus materialization, Phase 2, tokenizer access, model weights, inference, evaluation, training,
cleanup, deletion or automatic retry.

One separately supplied exact SHA-bound authorization may permit only:

1. ordinary non-force push of the exact implementation commit;
2. preservation-checked HU fast-forward to that commit;
3. HU tests and fresh preflight;
4. exactly one V2 Phase-1 test-only plus real CPU wave.

Phase 2, training, cleanup and automatic retry remain separately forbidden.
