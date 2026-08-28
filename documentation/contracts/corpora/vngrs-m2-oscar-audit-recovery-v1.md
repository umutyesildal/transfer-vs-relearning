# vngrs M2 OSCAR-only audit evidence recovery contract v1

**Status:** `FROZEN / UNEXECUTED — DIAGNOSTIC CPU PASS ONLY`

**Owner:** thesis project

**Created:** 2026-08-28

**Predecessor result:** `documentation/181_VNGRS_D0_V3_PHASE1_AUDIT_GATE_EXECUTION_RESULT_TR.md`

## Purpose

Resolve exactly the evidence-persistence gap exposed by D0 V3 job `481844` and qualify the user's
prospective OSCAR-only direction far enough to design the later selection contract. This is not a
D0 Phase-1 retry and cannot produce a training-ready corpus.

The pass reads the preserved V3 bytes, freezes the exact observed `corpus` labels, audits only the
predeclared candidate predicate `corpus == "OSCAR"`, persists bounded reason evidence before
applying the gate, then stops. It creates no held-out split, human-review packet or tokenizer
accounting report.

## Preserved V3 source

The source is read-only:

```text
/vol/tmp2/yesildau/vngrs_m2_three_model_d0_v3
```

Mandatory bindings:

```text
control/materialization_v3.json
  SHA-256 bb413e9acafd0d891ea9c4461abc77acea1c737489560650db56dacf781dbd10

control/d0_failure.json
  SHA-256 a341e4787e38720f27beeaf5815331ef0163084cb2974d91799ee5ffe426c52f

materialized objects: 32
materialized bytes:   9,502,315,428
```

Every raw Parquet file is size- and SHA-revalidated against the V3 manifest before any row is
accepted. The pass performs no HTTP request, download, copy, hard-link, move, rewrite, resume,
cleanup or deletion. The V1/V2/V3 roots and HU home remain read-only.

## Exact candidate and fail-closed behavior

The candidate predicate is exactly:

```text
field: corpus
operator: exact_string_equality
value: OSCAR
```

`OSCAR` is a predeclared candidate to verify, not a claim that V3 already preserved that exact
observed label. The pass first records every exact label with document and UTF-8 byte counts. It
fails closed if exact `OSCAR` is absent or contains at most 10,000 documents.

The existing Relation V2 exact and Unicode-normalized contamination surfaces and existing regex
and duplicate semantics remain unchanged. The persisted audit evidence records exact counts and
at most 256 deterministic examples per hit kind so output size cannot grow with the corpus.
It records `ready_to_train=false` regardless of PASS/BLOCKED.

If the candidate audit blocks, the terminal recovery state says `BLOCKED` and identifies whether
the observed reasons were exact contamination, normalized contamination, invalid encoding or a
combination. No exclusion threshold or automatic repair is invented by this contract.

## Fresh output

Only this new root may be written:

```text
/vol/tmp2/yesildau/vngrs_m2_oscar_audit_recovery_v1
```

It must be absent. Exact outputs are:

```text
reports/corpus_label_inventory.json
reports/lightweight_audit.json
control/recovery_state.json
```

On a preflight/runtime exception, `control/d0_failure.json` is written instead or alongside
already committed diagnostic evidence without overwriting an existing artifact.

`recovery_state.json` is terminal diagnostic evidence only. Even `OSCAR_AUDIT_COMPLETE` does not
authorize or imply split creation, review, tokenization, Phase 2 or training readiness.

## Resource and execution bounds

- one standard CPU allocation;
- 8 requested CPUs, 128 GiB RAM, 12-hour walltime;
- at least 2 GiB free scratch and 1,024 free inodes;
- offline Hugging Face/Transformers mode;
- Python bytecode writes disabled;
- one `sbatch --test-only`, then exactly one real job;
- zero duplicate matching jobs;
- no automatic retry.

## Exact implementation route

```text
config:    configs/corpora/vngrs_m2_oscar_audit_recovery_v1.yaml
operator:  transfer_vs_relearning.corpora.vngrs.d0_oscar_recovery
runner:    scripts/corpora/run_vngrs_m2_oscar_audit_recovery_v1.py
submitter: scripts/corpora/submit_vngrs_m2_oscar_audit_recovery_v1.sh
Slurm:     slurm/m2/audit_vngrs_m2_oscar_d0_v1.slurm
job name:  vngrs-m2-oscar-audit-v1
```

## Authority boundary

This preparation does not authorize publication/push, HU synchronization or SSH, Slurm, corpus
read, model/tokenizer access, split/review creation, evaluation, training, cleanup or deletion.

One later exact SHA-bound user authorization may permit only ordinary non-force push of the
reviewed commit, preservation-checked HU fast-forward, focused tests/preflight, and this single
diagnostic CPU pass. It does not authorize a second attempt, Phase 2, M2-A/M2-B training, cleanup
or automatic retry.
